from PyQt5.QtOpenGL import QGLWidget
from PyQt5.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random
import copy
# this is just for cherry pick


class GraphRenderer(QGLWidget):
    def __init__(self, parent=None):
        super(GraphRenderer, self).__init__(parent)
        self.graph = {"vertices": [], "edges": []}  # Store graph data
        self.vertex_positions = {}  
        self.history = []  
        self.redo_stack = []  
        self.save_state()  # Save the initial state
        self.initial_graph_state = None 
        self.selected_vertices = [] 
        self.force_iterations = 50  # Number of iterations for force-directed layout
        self.vertex_radius = 0.5 
        self.viewport_size = 20  # OpenGL viewport dimension (-10 to 10)

     # Sets the graph data to be rendered
    def set_graph(self, graph):
        """Set the graph data to be rendered."""
        self.graph = graph
        self.vertex_positions = graph.get("positions", {})  # Load positions
        self.initialize_vertex_positions()
        self.save_initial_state()  
        self.update()

    # Saves the current state of the graph
    def save_state(self):
        """Save the current state of the graph for undo/redo."""
        self.history.append(copy.deepcopy((self.graph, self.vertex_positions)))
        self.redo_stack.clear()  # Clear redo stack on new action
    
    def undo(self):
        """Undo the last action."""
        if len(self.history) > 1:
            self.redo_stack.append(self.history.pop())
            self.graph, self.vertex_positions = copy.deepcopy(self.history[-1])
            print("Undo performed.")
            self.update()
        else:
            print("No more actions to undo.")
    
    def redo(self):
        """Redo the last undone action."""
        if self.redo_stack:
            self.history.append(self.redo_stack.pop())
            self.graph, self.vertex_positions = copy.deepcopy(self.history[-1])
            print("Redo performed.")
            self.update()
        else:
            print("No more actions to redo.")            
    
     # Assigns random positions to any vertices that don't have them
    def initialize_vertex_positions(self):
        """Randomly initialize vertex positions if not already set."""
        for vertex in self.graph["vertices"]:
            vertex_id = vertex["id"]
            if vertex_id not in self.vertex_positions:
                self.vertex_positions[vertex_id] = np.array([random.uniform(-5, 5), random.uniform(-5, 5)])
        print(f"Initialized vertex positions: {self.vertex_positions}")

    # Saves the current graph state
    def save_initial_state(self):
        """Save the initial state of the graph for resetting."""
        self.initial_graph_state = {
            "vertices": copy.deepcopy(self.graph["vertices"]),
            "edges": copy.deepcopy(self.graph["edges"]),
            "positions": copy.deepcopy(self.vertex_positions),
        }
        print("Initial graph state saved.")

    # Resets the graph to the state saved by save_initial_state
    def reset_graph(self):
        """Reset the graph to its initial state."""
        if not self.initial_graph_state:
            print("Graph has no initial state to reset to.")
            return
        self.graph = {
            "vertices": copy.deepcopy(self.initial_graph_state["vertices"]),
            "edges": copy.deepcopy(self.initial_graph_state["edges"]),
        }
        self.vertex_positions = copy.deepcopy(self.initial_graph_state["positions"])
        print("Graph reset to initial state.")
        self.update()
        

    def add_vertex(self, position=None):
        """Add a new vertex at the given position or a random position."""
        new_id = len(self.graph["vertices"])
        self.graph["vertices"].append({"id": new_id})
        if position is None:
            position = np.array([random.uniform(-10, 10), random.uniform(-10, 10)])
        self.vertex_positions[new_id] = position
        self.save_state()  # Save the updated state
        print(f"Added vertex: {new_id} at {position}")
        self.update()
       

    def add_edge(self, start_id, end_id):
        """Add a new edge between two vertices."""
        if start_id not in self.vertex_positions or end_id not in self.vertex_positions:
            print(f"Cannot add edge: Vertex {start_id} or {end_id} does not exist.")
            return
        self.graph["edges"].append([start_id, end_id])
        self.save_state()  # Save the updated state
        print(f"Added edge: {start_id} -> {end_id}")
        self.update()
        

     # Applies a force-directed layout algorithm
    def run_force_directed_algorithm(self):
        """Run a 2D force-directed layout algorithm."""
        if not self.graph["vertices"] or not self.graph["edges"]:
            print("Graph is empty or has no edges. Layout algorithm skipped.")
            return

        print("Running force-directed algorithm...")
        vertices = self.graph["vertices"]
        edges = self.graph["edges"]

        # Constants for forces
        k = np.sqrt(1 / len(vertices)) * 5  # Ideal distance between vertices
        c_attract = 0.1  
        c_repulse = 0.5  

        for iteration in range(self.force_iterations):
            forces = {v["id"]: np.array([0.0, 0.0]) for v in vertices}

            # Calculate repulsive forces
            for v1 in vertices:
                for v2 in vertices:
                    if v1["id"] != v2["id"]:
                        pos1 = self.vertex_positions[v1["id"]]
                        pos2 = self.vertex_positions[v2["id"]]
                        delta = pos1 - pos2
                        distance = np.linalg.norm(delta) + 0.01  # Avoid division by zero
                        repulsive_force = c_repulse * (delta / distance**2)
                        forces[v1["id"]] += repulsive_force

            # Calculate attractive forces
            for edge in edges:
                v1_id, v2_id = edge
                pos1 = self.vertex_positions[v1_id]
                pos2 = self.vertex_positions[v2_id]
                delta = pos2 - pos1
                distance = np.linalg.norm(delta) + 0.01  
                attractive_force = c_attract * (delta * (distance - k))
                forces[v1_id] += attractive_force
                forces[v2_id] -= attractive_force

            # Update positions based on forces
            for vertex in vertices:
                self.vertex_positions[vertex["id"]] += forces[vertex["id"]] * 0.1  # Damping factor

        print(f"Final vertex positions: {self.vertex_positions}")
        self.update()

    # Prepares and returns the current graph data (vertices, edges, positions) for saving to a file
    def save_graph(self):
        """Return the graph data including positions for saving."""
        return {
            "vertices": self.graph["vertices"],
            "edges": self.graph["edges"],
            "positions": {str(k): v.tolist() for k, v in self.vertex_positions.items()},
        }

     # Loads graph data from a dictionary 
    def load_graph(self, graph_data):
        """Load the graph data, including positions."""
        try:
            # Validate JSON structure
            if "vertices" not in graph_data or "edges" not in graph_data or "positions" not in graph_data:
                raise KeyError("The JSON file must contain 'vertices', 'edges', and 'positions' keys.")

            # Load vertices, edges, and positions
            self.graph = {
                "vertices": graph_data["vertices"],
                "edges": graph_data["edges"],
            }
            self.vertex_positions = {int(k): np.array(v) for k, v in graph_data["positions"].items()}

            # Save initial state for reset
            self.save_initial_state()
            self.update()
            print(f"Graph loaded successfully: {self.graph}")

        except KeyError as e:
            print(f"Error loading graph: Missing key {e}")
        except ValueError as e:
            print(f"Error loading graph: Invalid data format for positions. {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

     # Handles the logic for selecting a vertex by its ID for edge creation
    def select_vertex_by_id(self, vertex_id):
        """Select a vertex by its ID."""
        if vertex_id in self.vertex_positions:
            print(f"Vertex {vertex_id} selected.")
            self.selected_vertices.append(vertex_id)
            if len(self.selected_vertices) == 2:
                # If two vertices are selected, create an edge
                self.add_edge(self.selected_vertices[0], self.selected_vertices[1])
                self.selected_vertices = []  
            self.update()  
        else:
            print(f"Vertex ID {vertex_id} does not exist.")

     # Processes mouse press events
    def mousePressEvent(self, event):
        """Handle mouse press events to select vertices."""
        if event.button() == Qt.LeftButton:
            # Map mouse click to OpenGL coordinates
            x = (event.x() / self.width()) * self.viewport_size - self.viewport_size / 2
            y = -((event.y() / self.height()) * self.viewport_size - self.viewport_size / 2)
            print(f"Mouse clicked at OpenGL coordinates: ({x}, {y})") 
            self.select_vertex(x, y)

    # Selects the vertex nearest to the given cooridnates if within radius(given)
    def select_vertex(self, x, y):
        """Select a vertex based on a mouse click."""
        nearest_vertex = None
        min_distance = float('inf')

        # Find the nearest vertex to the mouse click
        for vertex_id, position in self.vertex_positions.items():
            distance = np.linalg.norm(position - np.array([x, y]))
            print(f"Checking vertex {vertex_id}: position={position}, distance={distance}")  
            if distance <= self.vertex_radius and distance < min_distance:
                nearest_vertex = vertex_id
                min_distance = distance

        if nearest_vertex is not None:
            print(f"Vertex {nearest_vertex} selected.")
            self.selected_vertices.append(nearest_vertex)
            if len(self.selected_vertices) == 2:
                # If two vertices are selected, create an edge
                self.add_edge(self.selected_vertices[0], self.selected_vertices[1])
                self.selected_vertices = []  # Reset selection after creating edge
            self.update() 
    def initializeGL(self):
        """Initialize OpenGL settings."""
        glEnable(GL_DEPTH_TEST) 
        glClearColor(0.1, 0.1, 0.1, 1.0)  

     # Called when the widget is resized, sets the OpenGL viewport and projection matrix
    def resizeGL(self, width, height):
        """Handle resizing of the OpenGL widget."""
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(-10, 10, -10, 10)  # Set 2D orthographic projection
        glMatrixMode(GL_MODELVIEW)

    # Contains all OpenGL drawing calls
    def paintGL(self):
        """Render the OpenGL scene."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Draw vertices
        glPointSize(10)
        for vertex_id, position in self.vertex_positions.items():
            if vertex_id in self.selected_vertices:
                glColor3f(1.0, 0.0, 0.0)  # Red for selected vertices
            else:
                glColor3f(1.0, 1.0, 1.0)  # White for normal vertices
            glBegin(GL_POINTS)
            glVertex2f(*position)
            glEnd()

        # Draw edges
        glLineWidth(2)
        glColor3f(0.5, 0.5, 1.0)  # Blue color for edges
        glBegin(GL_LINES)
        for edge in self.graph["edges"]:
            start_id, end_id = edge
            glVertex2f(*self.vertex_positions[start_id])
            glVertex2f(*self.vertex_positions[end_id])
        glEnd()