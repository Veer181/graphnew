from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QApplication, QPushButton, QFileDialog, QInputDialog
from graph_renderer import GraphRenderer
import json


class GraphUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("2D Graph Drawer")

        # Creating the main OpenGL widget
        self.gl_widget = GraphRenderer(self)

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.gl_widget)

        # Creating buttons
        add_vertex_button = QPushButton("Add Vertex")
        add_vertex_button.clicked.connect(self.add_vertex)

        add_edge_button = QPushButton("Select Vertex for Edge")
        add_edge_button.clicked.connect(self.select_vertex)

        layout_button = QPushButton("Run Layout Algorithm")
        layout_button.clicked.connect(self.run_layout_algorithm)

        reset_button = QPushButton("Reset Graph")
        reset_button.clicked.connect(self.reset_graph)

        load_file_button = QPushButton("Load Graph from File")
        load_file_button.clicked.connect(self.load_graph_from_file)

        save_file_button = QPushButton("Save Graph to File")
        save_file_button.clicked.connect(self.save_graph_to_file)
        undo_button = QPushButton("Undo")  # Undo button
        undo_button.clicked.connect(self.undo)

        redo_button = QPushButton("Redo")  # Redo button
        redo_button.clicked.connect(self.redo)

        layout.addWidget(add_vertex_button)
        layout.addWidget(add_edge_button)
        layout.addWidget(layout_button)
        layout.addWidget(reset_button)
        layout.addWidget(load_file_button)
        layout.addWidget(save_file_button)
        layout.addWidget(undo_button) 
        layout.addWidget(redo_button)  

        # Set the layout for the central widget
        self.setCentralWidget(central_widget)

    def add_vertex(self):
        """Add a vertex interactively."""
        self.gl_widget.add_vertex()

    def select_vertex(self):
        """Select a vertex interactively for edge creation."""
        vertex_id, ok = QInputDialog.getInt(self, "Select Vertex", "Enter vertex ID:")
        if ok:  
            self.gl_widget.select_vertex_by_id(vertex_id)

    def run_layout_algorithm(self):
        """Run the force-directed layout algorithm."""
        self.gl_widget.run_force_directed_algorithm()

    def reset_graph(self):
        """Reset the graph to its initial state."""
        self.gl_widget.reset_graph()

    def load_graph_from_file(self):
        """Load a graph from a JSON file."""
        options = QFileDialog.Options()
         # Open a dialog to get the file path for loading
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Graph File",
            "",
            "JSON Files (*.json);;All Files (*)",
            options=options
        )
        if file_path:   # Proceed if a file path was selected
            try:
                with open(file_path, 'r') as file:
                    graph_data = json.load(file)

                # Pass the loaded JSON data to the renderer
                self.gl_widget.load_graph(graph_data)
                print(f"Graph loaded successfully from {file_path}")

            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON file format. {e}")
            except FileNotFoundError:
                print("Error: File not found.")
            except Exception as e:
                print(f"Unexpected error: {e}")

    def save_graph_to_file(self):
        """Save the current graph to a JSON file."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Graph File",
            "",
            "JSON Files (*.json);;All Files (*)",
            options=options
        )
        if file_path:
            try:
                graph_data = self.gl_widget.save_graph()
                with open(file_path, 'w') as file:
                    json.dump(graph_data, file, indent=4) # Save JSON data to the file with indentation
                print(f"Graph saved successfully to {file_path}")
            except Exception as e:
                print(f"Error saving graph: {e}")

    def undo(self):
        """Undo the last action."""
        self.gl_widget.undo()

    def redo(self):
        """Redo the last undone action."""
        self.gl_widget.redo()

# Main execution block
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    main_window = GraphUI()
    main_window.resize(800, 600)
    main_window.show()
    sys.exit(app.exec_())