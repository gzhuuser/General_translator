import tempfile
from PyQt5.QtWidgets import QWidget, QApplication, QRubberBand, QDesktopWidget
from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSignal


class ScreenshotWidget(QWidget):
    screenshot_taken = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        desktop = QDesktopWidget()
        screen_rect = desktop.screenGeometry()
        self.setGeometry(screen_rect)
        
        self.setStyleSheet("background-color: rgba(0, 0, 0, 100);")
        
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        
    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()
        self.activateWindow()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.rubber_band.setGeometry(QRect(self.start_point, self.start_point))
            self.rubber_band.show()
            print(f"开始截图，起始点: {self.start_point}")
            
    def mouseMoveEvent(self, event):
        if self.rubber_band.isVisible():
            self.rubber_band.setGeometry(QRect(self.start_point, event.pos()).normalized())
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.end_point = event.pos()
            self.rubber_band.hide()
            print(f"结束截图，结束点: {self.end_point}")
            self.take_screenshot()
            self.hide()
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.rubber_band.hide()
            self.hide()
            
    def take_screenshot(self):
        rect = QRect(self.start_point, self.end_point).normalized()
        print(f"截图区域: {rect}")
        if rect.width() > 10 and rect.height() > 10:
            screen = QApplication.primaryScreen()
            screenshot = screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())
            
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            screenshot.save(temp_file.name, 'PNG')
            temp_file.close()
            
            print(f"截图已保存: {temp_file.name}")
            self.screenshot_taken.emit(temp_file.name)
        else:
            print("截图区域太小，取消截图")
