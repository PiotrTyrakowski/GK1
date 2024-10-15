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
        if 0 <= index < len(self.vertices):
            del self.vertices[index]
            # Remove associated constraints and bezier segments
            if index in self.constraints:
                del self.constraints[index]
            if index in self.bezier_segments:
                del self.bezier_segments[index]

    def insert_vertex(self, index, x, y):
        if 0 <= index < len(self.vertices):
            self.vertices.insert(index + 1, Vertex(x, y))

    def get_edges(self):
        edges = []
        n = len(self.vertices)
        for i in range(n):
            start = self.vertices[i].point
            end = self.vertices[(i + 1) % n].point
            edges.append((start, end))
        return edges

