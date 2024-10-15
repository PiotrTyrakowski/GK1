from PyQt5.QtCore import Qt, QPoint



class Constraint:
    def __init__(self, type, value=None):
        self.type = type  # 'horizontal', 'vertical', 'length'
        self.value = value  # Length value if type is 'length'

class Vertex:
    def __init__(self, x, y):
        self.point = QPoint(x, y)

class BezierSegment:
    def __init__(self, start_vertex, end_vertex, control1, control2, continuity='G0'):
        self.start_vertex = start_vertex
        self.end_vertex = end_vertex
        self.control1 = control1  # QPoint
        self.control2 = control2  # QPoint
        self.continuity = continuity  # 'G0', 'G1', 'C1'

class Polygon:
    def __init__(self):
        self.vertices = []  # List of Vertex
        self.constraints = {}  # key: edge index, value: Constraint
        self.bezier_segments = {}  # key: edge index, value: BezierSegment

    def add_vertex(self, x, y):
        self.vertices.append(Vertex(x, y))

    def remove_vertex(self, index):
        print(f"Removing vertex at index {index}")
        if 0 <= index < len(self.vertices):
            print(f"Removing vertex at index {index}")
            del self.vertices[index]
            # Remove associated constraints and bezier segments
            if index in self.constraints:
                del self.constraints[index]
            if index in self.bezier_segments:
                del self.bezier_segments[index]

    def insert_vertex(self, edge_index, x, y):
        """Insert a vertex at the specified edge."""
        # Insert the new vertex after the start vertex of the edge
        self.insert_vertex_at_position(edge_index + 1, x, y)

        # Shift constraints and bezier segments for subsequent edges
        if edge_index in self.constraints:
            # Constraints on the original edge are removed in MainWindow
            pass  # Already handled
        if edge_index in self.bezier_segments:
            # Transfer the bezier segment to the new edge
            bezier = self.bezier_segments.pop(edge_index)
            new_edge_index = edge_index + 1
            self.bezier_segments[new_edge_index] = bezier

    def insert_vertex_at_position(self, index, x, y):
        """Insert a vertex at the specified list index."""
        if 0 <= index <= len(self.vertices):
            self.vertices.insert(index, Vertex(x, y))

    def get_edges(self):
        edges = []
        n = len(self.vertices)
        for i in range(n):
            start = self.vertices[i].point
            end = self.vertices[(i + 1) % n].point
            edges.append((start, end))
        return edges


