from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt


class DraggableButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.parent_window = parent
        self.drag_start_position = None
        self.mouse_press_pos = None
        self.is_dragging = False
        self.drag_threshold = 5
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_press_pos = event.globalPos()
            self.drag_start_position = event.globalPos() - self.parent_window.pos()
            event.accept()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.mouse_press_pos is not None:
            move_distance = (event.globalPos() - self.mouse_press_pos).manhattanLength()
            
            if move_distance > self.drag_threshold:
                self.is_dragging = True
                self.parent_window.move(event.globalPos() - self.drag_start_position)
                event.accept()
            else:
                super().mouseMoveEvent(event)
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.is_dragging:
                self.is_dragging = False
                event.accept()
                return
            
            self.mouse_press_pos = None
            self.is_dragging = False
        super().mouseReleaseEvent(event)
