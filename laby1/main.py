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
        self.canvas.vertex_clicked.connect(self.on_vertex_clicked)
        self.adding_vertex_mode = False
        self.removing_vertex_mode = False
        self.adding_constraint_mode = False
        self.removing_constraint_mode = False
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

    def on_vertex_clicked(self, vertex_index, pos):
        print(f"Vertex index: {vertex_index}, Click position: {pos}")
        print(f"Removing vertex mode: {self.removing_vertex_mode}")
        if self.removing_vertex_mode:
            self.remove_vertex(vertex_index)
            self.removing_vertex_mode = False
            # Uncheck the remove vertex button
            remove_vertex_btn = self.findChild(QPushButton, "remove_vertex_btn")
            if remove_vertex_btn:
                remove_vertex_btn.setChecked(False)

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

    def remove_vertex(self, vertex_index):
        print(f"Removing vertex at index {vertex_index}")
        
        self.remove_constraint_without_information(vertex_index)
        self.remove_constraint_without_information(vertex_index - 1 % len(self.canvas.polygon.vertices))
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

    def set_bresenham(self, edge_index):
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
