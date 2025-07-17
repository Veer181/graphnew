from PyQt5.QtOpenGL import QGLWidget
from PyQt5.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random
import copy


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
        self.vertex_radius = 0.15 
        self.viewport_size = 20  # OpenGL viewport dimension (-10 to 10)

        # Camera attributes
        self.camera_rot_x = 0.0
        self.camera_rot_y = 0.0
        self.camera_distance = 20.0
        self.last_mouse_pos = None

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
                self.vertex_positions[vertex_id] = np.array([random.uniform(-5, 5), random.uniform(-5, 5), random.uniform(-5, 5)], dtype=float)
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
            pos_array = np.array([random.uniform(-7, 7), random.uniform(-7, 7), random.uniform(-7, 7)], dtype=float)
        else:
            # Ensure position is a numpy array with float dtype
            pos_array = np.array(position, dtype=float)  
        self.vertex_positions[new_id] = pos_array
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
        """Run a 3D force-directed layout algorithm."""
        if not self.graph["vertices"] or not self.graph["edges"]:
            print("Graph is empty or has no edges. Layout algorithm skipped.")
            return

        print("Running force-directed algorithm...")
        vertices = self.graph["vertices"]
        edges = self.graph["edges"]

        # Constants for forces
        k = np.sqrt(1 / len(vertices)) * 2.5  # Ideal distance between vertices (further reduced)
        c_attract = 0.1  
        c_repulse = 0.15  # Further reduced for 3D
        c_center = 0.01 # Centering force constant

        for iteration in range(self.force_iterations):
            forces = {v["id"]: np.array([0.0, 0.0, 0.0]) for v in vertices}

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
            
            # Apply centering force
            for v_id in forces.keys():
                pos = self.vertex_positions[v_id]
                forces[v_id] -= pos * c_center

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
            self.vertex_positions = {int(k): np.array(v, dtype=float) for k, v in graph_data["positions"].items()}

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
        """Handle mouse press events to select vertices or rotate camera."""
        if event.button() == Qt.LeftButton:
            mouse_x = event.x()
            mouse_y = self.height() - event.y() # Convert to OpenGL's bottom-left origin
            self.select_vertex_at_screen_pos(mouse_x, mouse_y)
        elif event.button() == Qt.RightButton:
            self.last_mouse_pos = event.pos()
            print(f"Right Mouse pressed at: {event.pos()}")
        # super().mousePressEvent(event) # Avoid calling super if we handle all relevant buttons

    def mouseMoveEvent(self, event):
        """Handle mouse move events for camera rotation."""
        if self.last_mouse_pos and event.buttons() & Qt.RightButton: # Check if right button is held
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()

            self.camera_rot_x += dy * 0.5
            self.camera_rot_y += dx * 0.5

            # Clamp camera_rot_x to avoid flipping
            self.camera_rot_x = max(-90.0, min(90.0, self.camera_rot_x))

            self.last_mouse_pos = event.pos()
            self.update()
            print(f"Camera rotated to: rot_x={self.camera_rot_x}, rot_y={self.camera_rot_y}")
        # super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if event.button() == Qt.RightButton:
            self.last_mouse_pos = None
            print("Right Mouse released.")
        # super().mouseReleaseEvent(event)
        
    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming."""
        delta = event.angleDelta().y()
        if delta > 0:
            self.camera_distance -= 1.0
        elif delta < 0:
            self.camera_distance += 1.0
        
        self.camera_distance = max(1.0, min(self.camera_distance, 100.0)) # Clamp zoom
        self.update()
        print(f"Camera distance: {self.camera_distance}")

    def select_vertex_at_screen_pos(self, mouse_x, mouse_y):
        # Get current OpenGL matrices and viewport
        # These calls need to be done when the context is current and matrices are set,
        # typically within a drawing or event handling scope where paintGL has recently run
        # or the GL context is otherwise assured.
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)

        nearest_vertex_id = None
        min_dist_sq = float('inf')
        
        # Define a screen-space selection radius (e.g., 10 pixels)
        screen_select_radius_sq = 10**2 

        for vertex_id, world_pos_np in self.vertex_positions.items():
            if not isinstance(world_pos_np, np.ndarray) or world_pos_np.size != 3:
                print(f"Skipping vertex {vertex_id} with invalid position: {world_pos_np}")
                continue

            world_pos = world_pos_np.tolist() # gluProject expects list or separate args

            # Project world coordinates to screen coordinates
            try:
                screen_x, screen_y, screen_z_depth = gluProject(
                    world_pos[0], world_pos[1], world_pos[2],
                    modelview, projection, viewport
                )
            except Exception as e:
                # This can happen if matrices are singular, though unlikely in normal operation
                print(f"Error projecting vertex {vertex_id}: {e}")
                continue

            # Check if the vertex is in front of the camera (screen_z_depth is between 0 and 1)
            if not (0 <= screen_z_depth <= 1):
                continue # Vertex is clipped (behind camera or too far)

            # Calculate squared Euclidean distance in screen space
            dx = screen_x - mouse_x
            dy = screen_y - mouse_y
            dist_sq = dx**2 + dy**2

            if dist_sq < screen_select_radius_sq and dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                nearest_vertex_id = vertex_id
        
        if nearest_vertex_id is not None:
            print(f"Vertex {nearest_vertex_id} selected via screen projection.")
            if nearest_vertex_id in self.selected_vertices: # Allow deselecting by clicking again
                 self.selected_vertices.remove(nearest_vertex_id)
                 print(f"Vertex {nearest_vertex_id} deselected.")
            else:
                self.selected_vertices.append(nearest_vertex_id)
            
            if len(self.selected_vertices) == 2:
                self.add_edge(self.selected_vertices[0], self.selected_vertices[1])
                self.selected_vertices = []  # Reset selection
            self.update()
        else:
            # If no vertex was clicked, potentially clear selection
            # self.selected_vertices = [] 
            # self.update()
            print("No vertex selected.")

    # Selects the vertex nearest to the given cooridnates if within radius(given)
    # def select_vertex(self, x, y):
    #     """
    #     Select a vertex based on a mouse click (approximate in 3D).
    #     Note: This selection is based on a 2D projection of the vertices 
    #     and may not be accurate in a 3D view. For precise selection, 
    #     please use the 'Select Vertex by ID' functionality.
    #     """
    #     print("Note: 3D vertex selection via mouse click is approximate.")
    #     print("For precise selection, please use the 'Select Vertex by ID' functionality via the GUI.")
        
    #     nearest_vertex = None
    #     min_distance = float('inf')

    #     # Find the nearest vertex to the mouse click (using only X and Y for approximation)
    #     for vertex_id, position in self.vertex_positions.items():
    #         # Ensure position is a numpy array and has at least 2 elements
    #         if not isinstance(position, np.ndarray):
    #             position_np = np.array(position)
    #         else:
    #             position_np = position
            
    #         if position_np.size < 2:
    #             print(f"Skipping vertex {vertex_id} due to insufficient coordinate data.")
    #             continue

    #         distance = np.linalg.norm(position_np[:2] - np.array([x, y]))
    #         # print(f"Checking vertex {vertex_id}: projected_position_xy={position_np[:2]}, click_xy={[x,y]}, distance={distance}")  
    #         if distance <= self.vertex_radius and distance < min_distance:
    #             nearest_vertex = vertex_id
    #             min_distance = distance

    #     if nearest_vertex is not None:
    #         print(f"Vertex {nearest_vertex} selected.")
    #         self.selected_vertices.append(nearest_vertex)
    #         if len(self.selected_vertices) == 2:
    #             # If two vertices are selected, create an edge
    #             self.add_edge(self.selected_vertices[0], self.selected_vertices[1])
    #             self.selected_vertices = []  # Reset selection after creating edge
    #         self.update() 
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
        gluPerspective(55, (width / height) if height > 0 else 1, 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW) # Standard practice to switch back to ModelView

    # Contains all OpenGL drawing calls
    def paintGL(self):
        """Render the OpenGL scene."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Apply camera transformations
        glTranslatef(0.0, 0.0, -self.camera_distance)
        glRotatef(self.camera_rot_x, 1, 0, 0)
        glRotatef(self.camera_rot_y, 0, 1, 0)

        # Draw vertices
        glPointSize(8)
        for vertex_id, position in self.vertex_positions.items():
            if vertex_id in self.selected_vertices:
                glColor3f(1.0, 0.0, 0.0)  # Red for selected vertices
            else:
                glColor3f(1.0, 1.0, 1.0)  # White for normal vertices
            glBegin(GL_POINTS)
            glVertex3f(*position)
            glEnd()

        # Draw edges
        glLineWidth(2)
        glColor3f(0.5, 0.5, 1.0)  # Blue color for edges
        glBegin(GL_LINES)
        for edge in self.graph["edges"]:
            start_id, end_id = edge
            # Ensure positions are valid before drawing
            if start_id in self.vertex_positions and end_id in self.vertex_positions:
                glVertex3f(*self.vertex_positions[start_id])
                glVertex3f(*self.vertex_positions[end_id])
        glEnd()