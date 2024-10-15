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
        self.canvas = Canvas(self)
        self.init_ui()
        self.canvas.edge_clicked.connect(self.on_edge_clicked)  # Connect the signal
        self.adding_vertex_mode = False
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
        add_vertex_btn.setCheckable(True)
        add_vertex_btn.clicked.connect(self.toggle_add_vertex_mode)
        controls.addWidget(add_vertex_btn)

        # Remove Vertex Button
        remove_vertex_btn = QPushButton("Usuń Wierzchołek")
        remove_vertex_btn.clicked.connect(self.remove_vertex)
        controls.addWidget(remove_vertex_btn)

        # Add Constraint Button
        add_constraint_btn = QPushButton("Dodaj Ograniczenie")
        add_constraint_btn.clicked.connect(self.add_constraint)
        controls.addWidget(add_constraint_btn)

        # Remove Constraint Button
        remove_constraint_btn = QPushButton("Usuń Ograniczenie")
        remove_constraint_btn.clicked.connect(self.remove_constraint)
        controls.addWidget(remove_constraint_btn)

        # Radio Buttons for Line Drawing
        controls.addWidget(QLabel("Algorytm rysowania linii:"))
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

    def on_edge_clicked(self, edge_index, click_pos):
        if self.adding_vertex_mode:
            # Optionally, ask user to confirm or adjust position
            # For simplicity, we'll add the vertex at the click position
            print(f"Edge index: {edge_index}, Click position: {click_pos}")
            self.add_vertex_on_edge(edge_index, click_pos)
            self.adding_vertex_mode = False
            # Uncheck the add vertex button
            add_vertex_btn = self.findChild(QPushButton, "Dodaj Wierzchołek")
            if add_vertex_btn:
                add_vertex_btn.setChecked(False)

    def add_vertex_on_edge(self, edge_index, pos):
        # Calculate the midpoint or use click position
        # Here, we'll use the click position
        x, y = pos.x(), pos.y()

        # Insert the new vertex into the polygon
        self.canvas.polygon.insert_vertex(edge_index, x, y)
        
        # Remove constraints from the original edge
        if edge_index in self.canvas.polygon.constraints:
            del self.canvas.polygon.constraints[edge_index]

        # Update the canvas
        self.canvas.update()

    def remove_vertex(self):
        # For simplicity, remove last vertex
        if self.canvas.polygon.vertices:
            self.canvas.polygon.remove_vertex(-1)
            self.canvas.update()
        else:
            QMessageBox.information(self, "Info", "Brak wierzchołków do usunięcia.")

    def add_constraint(self):
        # Simple implementation: add horizontal constraint to first edge without constraint
        for i in range(len(self.canvas.polygon.vertices)):
            if i not in self.canvas.polygon.constraints:
                self.canvas.polygon.constraints[i] = Constraint('horizontal')
                self.canvas.update()
                return
        QMessageBox.information(self, "Info", "Brak krawędzi do dodania ograniczenia.")

    def remove_constraint(self):
        # Remove constraint from first constrained edge
        for i in list(self.canvas.polygon.constraints.keys()):
            del self.canvas.polygon.constraints[i]
            self.canvas.update()
            return
        QMessageBox.information(self, "Info", "Brak ograniczeń do usunięcia.")

    def set_bresenham(self):
        self.canvas.bresenham = self.radio_bresenham.isChecked()
        self.canvas.update()

    def show_documentation(self):
        doc = """
        **Instrukcja Obsługi**

        **Dodawanie Wierzchołka:**
        - Kliknij przycisk "Dodaj Wierzchołek", aby dodać nowy wierzchołek na domyślnej pozycji.

        **Usuwanie Wierzchołka:**
        - Kliknij przycisk "Usuń Wierzchołek", aby usunąć ostatni wierzchołek.

        **Dodawanie Ograniczenia:**
        - Kliknij przycisk "Dodaj Ograniczenie", aby dodać ograniczenie poziome do pierwszej dostępnej krawędzi bez ograniczeń.

        **Usuwanie Ograniczenia:**
        - Kliknij przycisk "Usuń Ograniczenie", aby usunąć ograniczenie z pierwszej dostępnej krawędzi z ograniczeniem.

        **Przełączanie Algorytmu Rysowania Linii:**
        - Wybierz między algorytmem Bresenhama a bibliotecznym za pomocą przycisków radiowych.

        **Edycja Wielokąta:**
        - Kliknij i przeciągnij wierzchołki (zielone kółka), aby je przesuwać.
        - Kliknij i przeciągnij kontrolne punkty krzywych Beziera (niebieskie kółka), aby edytować krzywe.

        **Kontynuacja Krzywych Beziera:**
        - Aktualna implementacja wspiera ciągłość G0. Dalsze implementacje mogą dodać G1 i C1.

        **Przesuwanie Całego Wielokąta:**
        - Kliknij i przeciągnij dowolny obszar wielokąta, aby przesunąć cały wielokąt.

        **Dodawanie/Wyłączanie Krzywych Beziera:**
        - Aktualna implementacja automatycznie rysuje segmenty krzywych Beziera na predefiniowanych krawędziach.

        """
        QMessageBox.information(self, "Instrukcja Obsługi", doc)

# ----- Main Execution -----

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()