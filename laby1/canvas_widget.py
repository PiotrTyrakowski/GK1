import sys
import math
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout,
    QHBoxLayout, QLabel, QMessageBox, QRadioButton, QButtonGroup,
    QInputDialog
)
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QMouseEvent
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
import numpy as np

from helper_classes import Polygon, Constraint, BezierSegment, Vertex

class Canvas(QWidget):
    edge_clicked = pyqtSignal(int, QPoint)  # New signal
    vertex_clicked = pyqtSignal(int, QPoint)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.polygon = Polygon()
        self.init_predefined_scene()
        self.selected_vertex = None
        self.selected_control = None
        self.dragging = False
        self.dragging_control = False
        self.bresenham = False  # If True, use Bresenham's algorithm
        self.adding_bezier = False
        self.current_bezier = None
        self.edge_threshold = 10  # Distance threshold for edge selection
        self.selected_edge_index = None

    def init_predefined_scene(self):
        # Initialize with a predefined polygon and constraints
        self.polygon.add_vertex(100, 100)
        self.polygon.add_vertex(300, 100)
        self.polygon.add_vertex(300, 300)
        self.polygon.add_vertex(100, 300)
        
        # Add a Bezier segment on the first edge
        start = self.polygon.vertices[0].point
        end = self.polygon.vertices[1].point
        control1 = QPoint(150, 50)
        control2 = QPoint(250, 150)
        bezier = BezierSegment(
            start_vertex=0,
            end_vertex=1,
            control1=control1,
            control2=control2
        )
        self.polygon.bezier_segments[0] = bezier
        
        # Add some constraints
        self.polygon.constraints[1] = Constraint('horizontal')
        self.polygon.constraints[2] = Constraint('length', 200)
        
        # Set some example continuity
        self.polygon.vertices[1].continuity = 'G1'  # Example continuity at vertex 1

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw polygon edges
        edges = self.polygon.get_edges()
        for i, (start, end) in enumerate(edges):
            pen = QPen(Qt.black, 2)
            if i in self.polygon.constraints:
                pen.setColor(Qt.red)
            if i == self.selected_edge_index:
                pen.setColor(Qt.blue)
                pen.setWidth(3)
            painter.setPen(pen)

            # Draw the edge (either as Bezier or straight line)
            if i in self.polygon.bezier_segments:
                bezier = self.polygon.bezier_segments[i]
                self.draw_bezier(painter, bezier)
            else:
                if self.bresenham:
                    self.draw_bresenham(painter, start, end)
                else:
                    painter.drawLine(start, end)

            # Draw constraint labels
            if i in self.polygon.constraints:
                constraint = self.polygon.constraints[i]
                mid_x = (start.x() + end.x()) // 2
                mid_y = (start.y() + end.y()) // 2
                
                # Draw constraint icon
                painter.setBrush(QBrush(Qt.blue))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(QPoint(mid_x, mid_y), 5, 5)
                
                # Draw constraint text
                painter.setPen(QPen(Qt.blue))
                constraint_text = f"{constraint.type}"
                if constraint.type == 'length':
                    constraint_text += f"={constraint.value}"
                painter.drawText(mid_x + 10, mid_y, constraint_text)

        # Draw vertices with enhanced continuity information
        for i, vertex in enumerate(self.polygon.vertices):
            # Draw vertex circle
            painter.setBrush(QBrush(Qt.green))
            painter.setPen(QPen(Qt.black, 1))
            painter.drawEllipse(vertex.point, 5, 5)
            
            # Draw vertex index and continuity information
            if vertex.continuity != 'G0':
                # Draw background for better readability
                text = f"V{i}({vertex.continuity})"
                painter.setPen(QPen(Qt.white))
                painter.setBrush(QBrush(Qt.darkGreen))
                text_rect = painter.boundingRect(
                    vertex.point.x() - 15,
                    vertex.point.y() - 25,
                    50, 20,
                    Qt.AlignLeft,
                    text
                )
                text_rect.adjust(-2, -2, 2, 2)
                painter.drawRect(text_rect)
                
                # Draw text
                painter.setPen(QPen(Qt.white))
                painter.drawText(
                    vertex.point.x() - 15,
                    vertex.point.y() - 25,
                    50, 20,
                    Qt.AlignLeft,
                    text
                )
            else:
                # Just draw vertex index for G0 vertices
                painter.setPen(QPen(Qt.black))
                painter.drawText(
                    vertex.point.x() - 15,
                    vertex.point.y() - 10,
                    f"V{i}"
                )

        # Draw control points for Bezier curves
        for edge_idx, bezier in self.polygon.bezier_segments.items():
            painter.setBrush(QBrush(Qt.blue))
            painter.setPen(QPen(Qt.black, 1))
            
            # Draw control points
            painter.drawEllipse(bezier.control1, 3, 3)
            painter.drawEllipse(bezier.control2, 3, 3)
            
            # Draw control lines
            start_vertex = self.polygon.vertices[bezier.start_vertex].point
            end_vertex = self.polygon.vertices[bezier.end_vertex].point
            painter.setPen(QPen(Qt.gray, 1, Qt.DashLine))
            painter.drawLine(start_vertex, bezier.control1)
            painter.drawLine(end_vertex, bezier.control2)
            
            # Draw Bezier curve index
            mid_point = self.calculate_bezier_point(bezier, 0.5)
            painter.setPen(QPen(Qt.darkMagenta))
            painter.drawText(mid_point[0], mid_point[1], f"B{edge_idx}")

    def draw_bresenham(self, painter, start, end):
        # Implement Bresenham's line algorithm
        x0, y0 = start.x(), start.y()
        x1, y1 = end.x(), end.y()
        points = self.bresenham_line(x0, y0, x1, y1)
        pen = QPen(Qt.black, 1)
        painter.setPen(pen)
        for point in points:
            painter.drawPoint(point[0], point[1])

    def bresenham_line(self, x0, y0, x1, y1):
        """Generate points on a line using Bresenham's algorithm."""
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = -1 if x0 > x1 else 1
        sy = -1 if y0 > y1 else 1
        if dy <= dx:
            err = dx / 2.0
            while x != x1:
                points.append((x, y))
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                points.append((x, y))
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        points.append((x1, y1))
        return points

    def draw_bezier(self, painter, bezier):
        # Draw the Bezier curve incrementally
        pen = QPen(Qt.darkMagenta, 2, Qt.DashLine)
        painter.setPen(pen)
        points = self.calculate_bezier_points(bezier, steps=100)
        for i in range(len(points) - 1):
            painter.drawLine(QPoint(*points[i]), QPoint(*points[i+1]))

    def calculate_bezier_points(self, bezier, steps=100):
        # Retrieve the actual QPoint objects from the polygon's vertices using indices
        start_vertex = self.polygon.vertices[bezier.start_vertex].point
        end_vertex = self.polygon.vertices[bezier.end_vertex].point

        P0 = np.array([start_vertex.x(), start_vertex.y()])
        P1 = np.array([bezier.control1.x(), bezier.control1.y()])
        P2 = np.array([bezier.control2.x(), bezier.control2.y()])
        P3 = np.array([end_vertex.x(), end_vertex.y()])
        
        points = []
        for t in np.linspace(0, 1, steps):
            point = (1-t)**3 * P0 + 3*(1-t)**2 * t * P1 + 3*(1-t)*t**2 * P2 + t**3 * P3
            points.append(tuple(point.astype(int)))
        return points

    def calculate_bezier_point(self, bezier, t):
        """Calculate a single point on the Bezier curve at parameter t."""
        start_vertex = self.polygon.vertices[bezier.start_vertex].point
        end_vertex = self.polygon.vertices[bezier.end_vertex].point
        
        P0 = np.array([start_vertex.x(), start_vertex.y()])
        P1 = np.array([bezier.control1.x(), bezier.control1.y()])
        P2 = np.array([bezier.control2.x(), bezier.control2.y()])
        P3 = np.array([end_vertex.x(), end_vertex.y()])
        
        point = (1-t)**3 * P0 + 3*(1-t)**2 * t * P1 + 3*(1-t)*t**2 * P2 + t**3 * P3
        return tuple(point.astype(int))

    def mousePressEvent(self, event: QMouseEvent):

        pos = event.pos()
        if event.button() == Qt.LeftButton:
            flag = False
            clicked_edge = self.get_clicked_edge(pos)
            clicked_vertex = self.get_clicked_vertex(pos)

            print(f"Clicked edge: {clicked_edge}")
            print(f"Clicked vertex: {clicked_vertex}")

            if clicked_vertex is not None:
                print(f"Clicked vertex: {clicked_vertex}")
                self.vertex_clicked.emit(clicked_vertex, pos)
                self.selected_vertex = clicked_vertex
                self.dragging = True
                flag = True
            if clicked_edge is not None:
                print(f"Clicked edge: {clicked_edge}")
                # Emit signal with edge index and click position
                self.edge_clicked.emit(clicked_edge, pos)
                flag = True
            
            # Check if a control point is clicked
            for bezier in self.polygon.bezier_segments.values():
                if self.distance(pos, bezier.control1) < 5:
                    self.selected_control = ('control1', bezier)
                    self.dragging_control = True
                    flag = True
                elif self.distance(pos, bezier.control2) < 5:
                    self.selected_control = ('control2', bezier)
                    self.dragging_control = True
                    flag = True
            # Else, start dragging the whole polygon

            if flag:
                return 
            self.selected_vertex = 'polygon'
            self.dragging = True
            self.last_mouse_pos = pos

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.pos()
        if self.dragging and self.selected_vertex != 'polygon':
            index = self.selected_vertex
            # Apply constraints if any
            if index in self.polygon.constraints:
                constraint = self.polygon.constraints[index]
                if constraint.type == 'horizontal':
                    self.polygon.vertices[index].point.setY(pos.y())
                elif constraint.type == 'vertical':
                    self.polygon.vertices[index].point.setX(pos.x())
                elif constraint.type == 'length':
                    # For simplicity, skip implementing length constraint during drag
                    self.polygon.vertices[index].point = pos
                else:
                    self.polygon.vertices[index].point = pos
            else:
                self.polygon.vertices[index].point = pos
            self.update()
        elif self.dragging and self.selected_vertex == 'polygon':
            delta = pos - self.last_mouse_pos
            for vertex in self.polygon.vertices:
                vertex.point += delta
            for bezier in self.polygon.bezier_segments.values():
                bezier.control1 += delta
                bezier.control2 += delta
            self.last_mouse_pos = pos
            self.update()

        # we find bezier segment and manipuate it via control
        if self.dragging_control and self.selected_control:
            control_name, bezier = self.selected_control
            start_vertex = bezier.start_vertex
            end_vertex = bezier.end_vertex
            before_start_vertex = (bezier.start_vertex - 1) % self.polygon.length
            after_end_vertex = (bezier.end_vertex + 1) % self.polygon.length
            before_bezier = None
            after_bezier = None

            for bez in self.polygon.bezier_segments.values():
                if bez.start_vertex == before_start_vertex and bez.end_vertex == start_vertex:
                    before_bezier = bez
                elif bez.start_vertex == end_vertex and bez.end_vertex == after_end_vertex:
                    after_bezier = bez


            if control_name == 'control1':
                if before_bezier is None:
                    start_vertex
                    print(12345)
                else:
                    print(678)

                

                bezier.control1 = pos
            elif control_name == 'control2':
                if after_bezier is None:

                    bezier.control2 = pos
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.dragging = False
        self.dragging_control = False
        self.selected_vertex = None
        self.selected_control = None

    def distance(self, p1: QPoint, p2: QPoint):
        return math.hypot(p1.x() - p2.x(), p1.y() - p2.y())

    def get_clicked_edge(self, pos):
        edges = self.polygon.get_edges()
        for i, (start, end) in enumerate(edges):
            if self.is_near_edge(pos, start, end):
                return i
        return None
    
    def get_clicked_vertex(self, pos):
        for i, vertex in enumerate(self.polygon.vertices):
            if self.distance(pos, vertex.point) < 10:
                print("something")
                return i
        return None

    def is_near_edge(self, point, start, end):
        """Check if a point is within a threshold distance from an edge."""
        x0, y0 = point.x(), point.y()
        x1, y1 = start.x(), start.y()
        x2, y2 = end.x(), end.y()

        # Compute the distance from point to the line segment
        numerator = abs((y2 - y1)*x0 - (x2 - x1)*y0 + x2*y1 - y2*x1)
        denominator = math.hypot(y2 - y1, x2 - x1)
        if denominator == 0:
            return False
        distance = numerator / denominator
        return distance <= self.edge_threshold

