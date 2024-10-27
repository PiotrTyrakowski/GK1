from PyQt5.QtCore import Qt, QPoint



class Constraint:
    def __init__(self, type, value=None):
        self.type = type  # 'horizontal', 'vertical', 'length'
        self.value = value  # Length value if type is 'length'

class Vertex:
    def __init__(self, x, y):
        self.point = QPoint(x, y)
        self.continuity = 'G0' # New Attribute: 'G0', 'G1', 'C1'

class BezierSegment:
    def __init__(self, start_vertex, end_vertex, control1, control2):
        self.start_vertex = start_vertex
        self.end_vertex = end_vertex
        self.control1 = control1  # QPoint
        self.control2 = control2  # QPoint

class Polygon:
    def __init__(self):
        self.vertices = []  # List of Vertex
        self.constraints = {}  # key: edge index, value: Constraint
        self.bezier_segments = {}  # key: edge index, value: BezierSegment
        self.length = 0

    def add_vertex(self, x, y):
        self.vertices.append(Vertex(x, y))
        self.length += 1


        





    def remove_vertex(self, index):
        print(f"Removing vertex at index {index}")
        if 0 <= index < len(self.vertices):
            # Remove associated constraints and bezier segments
            before_index = (index - 1) % self.length
            after_index = (index + 1) % self.length
            if index in self.constraints:
                del self.constraints[index]
            if before_index in self.constraints:
                del self.constraints[before_index]
            # if after_index in self.constraints:
            #     del self.constraints[after_index]
            if index in self.bezier_segments:
                del self.bezier_segments[index]
            if before_index in self.bezier_segments:
                del self.bezier_segments[before_index]
            # if after_index in self.bezier_segments:
            #     del self.bezier_segments[after_index]


            self.vertices[before_index].continuity = "G0"
            self.vertices[index].continuity = "G0"
            self.vertices[after_index].continuity = "G0"


            print(f"Removing vertex at index {index}")
            del self.vertices[index]
            self.length -= 1
            # Remove associated constraints and bezier segments

            local_constraints = {}
            local_beziers = {}
            
            for i in range(index + 1):
                if self.constraints.get(i):
                    local_constraints[i] = self.constraints.get(i)
                if self.bezier_segments.get(i):
                    local_beziers[i] = self.bezier_segments.get(i)
                
            for i in range(index + 1, len(self.get_edges())):
                item = self.constraints.get(i)
                if item:
                    local_constraints[i-1] = item
                item = self.bezier_segments.get(i)
                if item:
                    item.start_vertex = (item.start_vertex - 1) % self.length
                    item.end_vertex = (item.end_vertex - 1) % self.length
                    local_beziers[i-1] = item

            self.constraints = local_constraints
            self.bezier_segments = local_beziers
                    #TODO ADD CONTINUTEITE BETTER.

            

    def add_vertex_continuity(self, vertex_index, selected_continuity="G0"):
        self.vertices[vertex_index].continuity = selected_continuity

    def insert_vertex(self, edge_index, x, y):
        """Insert a vertex at the specified edge."""
        # Insert the new vertex after the start vertex of the edge
        self.insert_vertex_at_position(edge_index + 1, x, y)

       
        if edge_index in self.constraints:
            del self.constraints[edge_index]
        
        if edge_index in self.bezier_segments:
            del self.bezier_segments[edge_index]
       

        # Shift constraints and bezier segments for subsequent edges
        local_constraints = {}
        local_beziers = {}

        for i in range(edge_index + 1):
            if self.constraints.get(i):
                local_constraints[i] = self.constraints.get(i)
            if self.bezier_segments.get(i):
                local_beziers[i] = self.bezier_segments.get(i)
            
        for i in reversed(range(edge_index + 1, len(self.get_edges()))):
            item = self.constraints.get(i - 1)
            if item:
                local_constraints[i] = item
            item = self.bezier_segments.get(i - 1)
            if item:
                item.start_vertex = (item.start_vertex + 1) % self.length
                item.end_vertex = (item.end_vertex + 1) % self.length
                local_beziers[i] = item

        self.constraints = local_constraints
        self.bezier_segments = local_beziers
                #TODO ADD CONTINUTEITE BETTER.


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
    
    def get_beziers(self):
        return self.bezier_segments



