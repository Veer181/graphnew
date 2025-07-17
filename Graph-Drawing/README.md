# 2D Graph Drawer

A Python-based graphical application to create, visualize, and edit 2D graphs using OpenGL. The application supports features such as adding vertices, creating edges, running a force-directed layout algorithm, saving/loading graphs, and resetting the graph to its initial state.

---

## Features

### 1. **Add Vertex**
- Add new vertices to the graph.
- Vertices are assigned random positions within the bounds `[-10, 10]` for both `x` and `y` coordinates.

### 2. **Add Edge**
- Create edges between existing vertices by selecting their IDs.

### 3. **Run Force-Directed Layout Algorithm**
- Dynamically reposition vertices based on attractive and repulsive forces.
- Adjusts positions to create a visually appealing layout.
- The implemented algorithm is a type of force-directed layout, sharing core principles with algorithms like Fruchterman-Reingold. It uses attractive forces between connected vertices (simulating springs) and repulsive forces between all pairs of vertices. However, the specific mathematical formulas used to calculate the magnitudes of these attractive and repulsive forces differ from those in the classical Fruchterman-Reingold algorithm, making this a custom implementation of the force-directed paradigm.

### 4. **Reset Graph**
- Restore the graph to its initial state, including vertices, edges, and positions.

### 5. **Save Graph**
- Save the graph as a `.json` file containing:
  - Vertices
  - Edges
  - Vertex positions

### 6. **Load Graph**
- Load a graph from a `.json` file.
- Restores vertices, edges, and positions.

### 7. **Undo/Redo**
- Undo or redo the last action performed on the graph.
- **Supported actions**:
  - Adding a vertex.
  - Adding an edge.

---

## Installation

### **Virtual Environment (Required)**
Set up a virtual environment for dependency management:

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - Windows:
     ```bash
     venv\Scripts\activate
     ```

3. Install dependencies (see below).

4. Deactivate the virtual environment when done:
   ```bash
   deactivate
   ```

### **Steps to Install and run**
1. Install the required libraries inside the virtual environment:
   ```bash
   python3 -m pip install PyQt5 PyOpenGL PyOpenGL-accelerate numpy
   ```

3. Start the application:
   ```bash
   python3 graph_ui.py
   ```

4. Use the GUI to:
   - Add vertices and edges.
   - Load and save graphs.
   - Run the force-directed layout algorithm.
   - Reset the graph.

---

## Graph Bounds

- **X-axis**: `-10 <= x <= 10`
- **Y-axis**: `-10 <= y <= 10`

**Note**: Ensure all vertices in the JSON file have coordinates within this range. If coordinates exceed these limits, parts of the graph may go out of view.

---

## Example JSON Files

### Small Graph Example
```json
{
    "vertices": [
        {"id": 0},
        {"id": 1},
        {"id": 2},
        {"id": 3}
    ],
    "edges": [
        [0, 1],
        [1, 2],
        [2, 3],
        [3, 0]
    ],
    "positions": {
        "0": [0.0, 0.0],
        "1": [5.0, 0.0],
        "2": [5.0, 5.0],
        "3": [0.0, 5.0]
    }
}
```

### Larger Graph Example
```json
{
    "vertices": [
        {"id": 0},
        {"id": 1},
        {"id": 2},
        {"id": 3},
        {"id": 4},
        {"id": 5},
        {"id": 6},
        {"id": 7},
        {"id": 8},
        {"id": 9},
        {"id": 10},
        {"id": 11}
    ],
    "edges": [
        [0, 1],
        [0, 2],
        [1, 3],
        [1, 4],
        [2, 5],
        [2, 6],
        [3, 7],
        [4, 7],
        [5, 8],
        [6, 9],
        [7, 10],
        [8, 10],
        [9, 11],
        [10, 11]
    ],
    "positions": {
        "0": [0.0, 0.0],
        "1": [2.0, 2.0],
        "2": [2.0, -2.0],
        "3": [4.0, 3.0],
        "4": [4.0, 1.0],
        "5": [4.0, -1.0],
        "6": [4.0, -3.0],
        "7": [6.0, 2.0],
        "8": [6.0, -1.0],
        "9": [6.0, -4.0],
        "10": [8.0, 0.0],
        "11": [10.0, 0.0]
    }
}
```

---
