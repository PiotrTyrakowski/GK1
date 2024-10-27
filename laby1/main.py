import sys
import math
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout,
    QHBoxLayout, QLabel, QMessageBox, QRadioButton, QButtonGroup,
    QInputDialog
)
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QMouseEvent
from PyQt5.QtCore import Qt, QPoint
import numpy as np

from canvas_widget import Canvas
from helper_classes import Constraint, Vertex, BezierSegment, Polygon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edytor Wielokątów/Krzywoliniowych")
        # Set initial window size
        self.setGeometry(100, 100, 1200, 800)  # x, y, width, height
        self.canvas = Canvas(self)  # This creates an instance of the Canvas class, passing the current MainWindow instance as the parent. This allows the Canvas to be displayed within the MainWindow and enables communication between the two components.
        self.init_ui()
        self.canvas.edge_clicked.connect(self.on_edge_clicked)  # Connect the signal
        self.canvas.vertex_clicked.connect(self.on_vertex_clicked)
        self.adding_vertex_mode = False
        self.removing_vertex_mode = False
        self.adding_constraint_mode = False
        self.removing_constraint_mode = False
        self.adding_bezier_mode = False  # New Mode
        self.removing_bezier_mode = False  # Optional: If you want to remove Bezier curves
        self.adding_vertex_continuity_mode = False  # Initialize continuity mode
        self.selected_edge = None

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout()
        main_widget.setLayout(layout)

        # Left side: Canvas
        layout.addWidget(self.canvas)

        # Right side: Controls
        controls = QVBoxLayout()

        # Add Vertex Button
        add_vertex_btn = QPushButton("Dodaj Wierzchołek")
        add_vertex_btn.setObjectName("add_vertex_btn")
        add_vertex_btn.setCheckable(True)
        add_vertex_btn.clicked.connect(self.toggle_add_vertex_mode)
        controls.addWidget(add_vertex_btn)

        # Remove Vertex Button
        remove_vertex_btn = QPushButton("Usuń Wierzchołek")
        remove_vertex_btn.setObjectName("remove_vertex_btn")
        remove_vertex_btn.setCheckable(True)
        remove_vertex_btn.clicked.connect(self.toggle_remove_vertex_mode)
        controls.addWidget(remove_vertex_btn)

        # Add Constraint Button
        add_constraint_btn = QPushButton("Dodaj Ograniczenie")
        add_constraint_btn.setObjectName("add_constraint_btn")
        add_constraint_btn.setCheckable(True)
        add_constraint_btn.clicked.connect(self.toggle_add_constraint_mode)
        controls.addWidget(add_constraint_btn)

        # Remove Constraint Button
        remove_constraint_btn = QPushButton("Usuń Ograniczenie")
        remove_constraint_btn.setObjectName("remove_constraint_btn")
        remove_constraint_btn.setCheckable(True)
        remove_constraint_btn.clicked.connect(self.toggle_remove_constraint_mode)
        controls.addWidget(remove_constraint_btn)

        # Add Bezier Curve Button
        add_bezier_btn = QPushButton("Dodaj Krzywą Béziera")
        add_bezier_btn.setObjectName("add_bezier_btn")
        add_bezier_btn.setCheckable(True)
        add_bezier_btn.clicked.connect(self.toggle_add_bezier_mode)
        controls.addWidget(add_bezier_btn)

        # Remove Bezier Curve Button
        remove_bezier_btn = QPushButton("Usuń Krzywą Béziera")
        remove_bezier_btn.setObjectName("remove_bezier_btn")
        remove_bezier_btn.setCheckable(True)
        remove_bezier_btn.clicked.connect(self.toggle_remove_bezier_mode)
        controls.addWidget(remove_bezier_btn)

        # Add Vertex Continuity Constraint Button
        add_vertex_continuity_btn = QPushButton("Dodaj Ciągłość Wierzchołka")
        add_vertex_continuity_btn.setObjectName("add_vertex_continuity_btn")
        add_vertex_continuity_btn.setCheckable(True)
        add_vertex_continuity_btn.clicked.connect(self.toggle_add_vertex_continuity_mode)
        controls.addWidget(add_vertex_continuity_btn)

        # Radio Buttons for Line Drawing
        controls.addWidget(QLabel("Algorytm ry/sowania linii:"))
        self.radio_bresenham = QRadioButton("Bresenham")
        self.radio_library = QRadioButton("Biblioteczny")
        self.radio_library.setChecked(True)
        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.radio_bresenham)
        self.radio_group.addButton(self.radio_library)
        self.radio_bresenham.toggled.connect(self.set_bresenham)
        controls.addWidget(self.radio_bresenham)
        controls.addWidget(self.radio_library)

        # Documentation Button
        doc_btn = QPushButton("Instrukcja")
        doc_btn.clicked.connect(self.show_documentation)
        controls.addWidget(doc_btn)

        controls.addStretch()
        layout.addLayout(controls)

    def toggle_add_vertex_mode(self, checked):
        self.adding_vertex_mode = checked
        if checked:
            QMessageBox.information(self, "Tryb Dodawania Wierzchołka", "Kliknij na krawędź, aby dodać wierzchołek.")
        else:
            self.selected_edge = None

    def toggle_remove_vertex_mode(self, checked):
        self.removing_vertex_mode = checked
        if checked:
            QMessageBox.information(self, "Tryb Usuwania Wierzchołka", "Kliknij na wierzchołek, aby usunąć.")
        else:
            self.selected_vertex = None

    def toggle_add_constraint_mode(self, checked):
        print(checked)
        self.adding_constraint_mode = checked
        if checked:
            QMessageBox.information(self, "Tryb Dodawania Ograniczenia", "Kliknij na krawędź, aby dodać ograniczenie.")
        else:
            self.selected_edge = None

    def toggle_remove_constraint_mode(self, checked):
        print(checked)
        self.removing_constraint_mode = checked
        if checked:
            QMessageBox.information(self, "Tryb Usuwania Ograniczenia", "Kliknij na krawędź, aby usunąć ograniczenie.")
        else:
            self.selected_edge = None

    def toggle_add_bezier_mode(self, checked):
        self.adding_bezier_mode = checked
        if checked:
            QMessageBox.information(self, "Tryb Dodawania Krzywej Béziera",
                                    "Kliknij na krawędź, aby dodać krzywą Béziera.")
        else:
            self.selected_edge = None
    
    def toggle_remove_bezier_mode(self, checked):
        self.removing_bezier_mode = checked
        if checked:
            QMessageBox.information(self, "Tryb Usuwania Krzywej Béziera",
                                    "Kliknij na krzywą Béziera, aby usunąć.")
        else:
            self.selected_bezier = None

    def toggle_add_vertex_continuity_mode(self, checked):
        self.adding_vertex_continuity_mode = checked
        if checked:
            QMessageBox.information(self, "Tryb Dodawania Ograniczenia Wierzchołka",
                                    "Kliknij na wierzchołek, aby dodać ograniczenie ciągłości.")
        else:
            self.selected_vertex = None

    def on_edge_clicked(self, edge_index, click_pos):
        if self.adding_vertex_mode:
            # Optionally, ask user to confirm or adjust position
            # For simplicity, we'll add the vertex at the click position
            print(f"Edge index: {edge_index}, Click position: {click_pos}")
            self.add_vertex_on_edge(edge_index, click_pos)
            self.adding_vertex_mode = False
            # Uncheck the add vertex button
            add_vertex_btn = self.findChild(QPushButton, "add_vertex_btn")
            if add_vertex_btn:
                add_vertex_btn.setChecked(False)
        elif self.adding_constraint_mode:
            self.add_constraint(edge_index, click_pos)
            self.adding_constraint_mode = False
            # Uncheck the add constraint button
            add_constraint_btn = self.findChild(QPushButton, "add_constraint_btn")
            if add_constraint_btn:
                add_constraint_btn.setChecked(False)
        elif self.removing_constraint_mode:
            self.remove_constraint(edge_index)
            self.removing_constraint_mode = False
            # Uncheck the remove constraint button
            remove_constraint_btn = self.findChild(QPushButton, "remove_constraint_btn")
            if remove_constraint_btn:
                remove_constraint_btn.setChecked(False)
        elif self.adding_bezier_mode:
            self.add_bezier_curve(edge_index)
            self.adding_bezier_mode = False
            # Uncheck the add bezier button
            add_bezier_btn = self.findChild(QPushButton, "add_bezier_btn")
            if add_bezier_btn:
                add_bezier_btn.setChecked(False)
        elif self.removing_bezier_mode:
            self.remove_bezier_curve(edge_index)
            self.removing_bezier_mode = False
            # Uncheck the remove bezier button
            remove_bezier_btn = self.findChild(QPushButton, "remove_bezier_btn")
            if remove_bezier_btn:
                remove_bezier_btn.setChecked(False)

    def on_vertex_clicked(self, vertex_index, pos):
        if self.adding_vertex_continuity_mode:
            
            flag = False
            for segments in self.canvas.polygon.bezier_segments.values():
                if segments.start_vertex == vertex_index or segments.end_vertex == vertex_index:
                    flag = True
                    break
            
            if flag is False:
                return
            
            
            self.add_vertex_continuity(vertex_index)
            self.adding_vertex_continuity_mode = False
            # Uncheck the add vertex continuity button
            add_vertex_continuity_btn = self.findChild(QPushButton, "add_vertex_continuity_btn")
            if add_vertex_continuity_btn:
                add_vertex_continuity_btn.setChecked(False)
        elif self.removing_vertex_mode:
            self.remove_vertex(vertex_index)
            self.removing_vertex_mode = False
            # Uncheck the remove vertex button
            remove_vertex_btn = self.findChild(QPushButton, "remove_vertex_btn")
            if remove_vertex_btn:
                remove_vertex_btn.setChecked(False)
        else:
            # Other vertex click handling, if any
            pass

    def add_vertex_on_edge(self, edge_index, pos):
        # Calculate the midpoint or use click position
        # Here, we'll use the click position
        x, y = pos.x(), pos.y()

        # Insert the new vertex into the polygon
        self.canvas.polygon.insert_vertex(edge_index, x, y)

        # Update the canvas
        self.canvas.update()

    def remove_vertex(self, vertex_index):
        print(f"Removing vertex at index {vertex_index}")

        # Remove constraints related to this vertex and adjacent edges
        self.remove_constraint_without_information(vertex_index)
        prev_edge_index = (vertex_index - 1) % len(self.canvas.polygon.vertices)
        self.remove_constraint_without_information(prev_edge_index)

        self.canvas.polygon.remove_vertex(vertex_index)

        self.canvas.update()

    def add_constraint(self, edge_index, pos):
        clicked_edge = edge_index
        print(f"Clicked edge: {clicked_edge}")
        if clicked_edge is not None and clicked_edge not in self.canvas.polygon.bezier_segments:
            # Show possible constraints
            options = ["horizontal", "vertical", "length"]
            selected_constraint, ok = QInputDialog.getItem(self, "Wybierz Ograniczenie",
                                                            "Typ ograniczenia:", options, 0, False)
            if ok and selected_constraint:
                # Check for existing constraints
                if clicked_edge in self.canvas.polygon.constraints:
                    QMessageBox.information(self, "Info", "Krawędź ma już ograniczenie.")
                    return
                # Add the selected constraint
                if selected_constraint == "length":
                    length, ok = QInputDialog.getInt(self, "Długość Ograniczenia",
                                                    "Podaj długość:", 100, 1, 1000)
                    if ok:
                        self.canvas.polygon.constraints[clicked_edge] = Constraint('length', length)
                else:
                    # Ensure that two adjacent edges cannot both be vertical or both horizontal
                    if selected_constraint in ["horizontal", "vertical"]:
                        # Check previous and next edges
                        n = len(self.canvas.polygon.vertices)
                        prev_edge = (clicked_edge - 1) % n
                        next_edge = (clicked_edge + 1) % n
                        constraints = [
                            self.canvas.polygon.constraints.get(prev_edge),
                            self.canvas.polygon.constraints.get(next_edge)
                        ]
                        for constraint in constraints:
                            if constraint and constraint.type == selected_constraint:
                                QMessageBox.warning(self, "Ostrzeżenie",
                                                    f"Dwoma sąsiednimi krawędziami nie mogą być oba {selected_constraint}.")
                                return
                    self.canvas.polygon.constraints[clicked_edge] = Constraint(selected_constraint)
                self.canvas.update()
        else:
            QMessageBox.information(self, "Info", "Nie można dodać ograniczenia do tej krawędzi.")

    def remove_constraint_without_information(self, edge_index):
        clicked_edge = edge_index
        if clicked_edge is not None and clicked_edge in self.canvas.polygon.constraints:
            del self.canvas.polygon.constraints[clicked_edge]
            self.canvas.update()

    def remove_constraint(self, edge_index):
        clicked_edge = edge_index
        if clicked_edge is not None and clicked_edge in self.canvas.polygon.constraints:
            self.remove_constraint_without_information(edge_index)
        else:
            QMessageBox.information(self, "Info", "Brak ograniczenia do usunięcia.")

    def set_bresenham(self, checked):
        self.canvas.bresenham = self.radio_bresenham.isChecked()
        self.canvas.update()

    def show_documentation(self):
        doc = """
        **Instrukcja Obsługi**

        **Dodawanie Wierzchołka:**
        - Kliknij przycisk "Dodaj Wierzchołek", aby dodać nowy wierzchołek na wybranej krawędzi.

        **Usuwanie Wierzchołka:**
        - Kliknij przycisk "Usuń Wierzchołek", a następnie kliknij na wierzchołek, który chcesz usunąć.

        **Dodawanie Ograniczenia:**
        - Kliknij przycisk "Dodaj Ograniczenie", a następnie kliknij na krawędź, do której chcesz dodać ograniczenie (poziome, pionowe, długości).

        **Usuwanie Ograniczenia:**
        - Kliknij przycisk "Usuń Ograniczenie", a następnie kliknij na krawędź, z której chcesz usunąć ograniczenie.

        **Dodawanie Krzywej Béziera:**
        - Kliknij przycisk "Dodaj Krzywą Béziera", a następnie kliknij na krawędź, do której chcesz dodać krzywą.

        **Dodawanie Ciągłości Wierzchołka:**
        - Kliknij przycisk "Dodaj Ciągłość Wierzchołka", a następnie kliknij na wierzchołek, aby dodać ciągłość (G0, G1, C1).

        **Przełączanie Algorytmu Rysowania Linii:**
        - Wybierz między algorytmem Bresenhama a bibliotecznym za pomocą przycisków radiowych.

        **Edycja Wielokąta:**
        - Kliknij i przeciągnij wierzchołki (zielone kółka), aby je przesuwać.
        - Kliknij i przeciągnij kontrolne punkty krzywych Béziera (niebieskie kółka), aby edytować krzywe.

        **Kontynuacja Krzywych Béziera:**
        - Aktualna implementacja wspiera ciągłość G0, G1 i C1. Ograniczenia wynikające z ciągłości są automatycznie zarządzane.

        **Przesuwanie Całego Wielokąta:**
        - Kliknij i przeciągnij dowolny obszar wielokąta, aby przesunąć cały wielokąt.

        **Dodawanie/Wyłączanie Krzywych Béziera:**
        - Dodawanie krzywych Béziera jest możliwe tylko dla krawędzi bez istniejących ograniczeń.

        """
        QMessageBox.information(self, "Instrukcja Obsługi", doc)

    def add_bezier_curve(self, edge_index):
        # Check if the edge has constraints
        if edge_index in self.canvas.polygon.constraints:
            QMessageBox.warning(self, "Błąd", "Nie można dodać krzywej Béziera do krawędzi z ograniczeniem.")
            return
        # Check if the edge already has a Bezier segment
        if edge_index in self.canvas.polygon.bezier_segments:
            QMessageBox.information(self, "Info", "Krawędź już ma krzywą Béziera.")
            return

        
        # Add a default Bezier segment
        start = self.canvas.polygon.vertices[edge_index].point
        end = self.canvas.polygon.vertices[(edge_index + 1) % len(self.canvas.polygon.vertices)].point
        print(f"Start: {start}, End: {end}")
        control1 = QPoint(start.x() + 50, start.y() - 50)
        control2 = QPoint(end.x() - 50, end.y() + 50)
        bezier = BezierSegment(
            start_vertex=edge_index,
            end_vertex=(edge_index + 1) % len(self.canvas.polygon.vertices),
            control1=control1,
            control2=control2,
            continuity='G0'  # Default continuity
        )
        self.canvas.polygon.bezier_segments[edge_index] = bezier
        self.canvas.update()

    def remove_bezier_curve(self, edge_index):
        if edge_index in self.canvas.polygon.bezier_segments:
            del self.canvas.polygon.bezier_segments[edge_index]
            self.canvas.update()
        else:
            QMessageBox.information(self, "Info", "Brak krzywej Béziera do usunięcia.")

    def add_vertex_continuity(self, vertex_index):
        # Prompt user to select continuity type
        options = ["G0", "G1", "C1"]
        selected_continuity, ok = QInputDialog.getItem(self, "Wybierz Ciągłość",
                                                       "Typ ciągłości:", options, 0, False)
        if ok and selected_continuity:
            # Assign continuity to the vertex
            self.canvas.polygon.add_vertex_continuity(vertex_index, selected_continuity)
            # self.canvas.polygon.vertices[vertex_index].continuity = selected_continuity
            self.canvas.update()



# ----- Main Execution -----

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
