from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QComboBox, QMessageBox, QDialog)
from PyQt5.QtCore import Qt
from app.managers import ConfigManager
from app.ui.region_input_dialog import RegionInputDialog
from app.ui.translation_window import TranslationWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_region = None  # 存储当前设置的区域
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("二游英语翻译助手")
        self.setGeometry(100, 100, 500, 400)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("二游英语翻译助手")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title_label)
        
        # 用户英语水平选择
        level_layout = QHBoxLayout()
        level_label = QLabel("英语水平:")
        level_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.level_combo = QComboBox()
        self.level_combo.addItems(["初级", "中级", "高级"])
        self.level_combo.setCurrentText(ConfigManager.load_user_level())
        self.level_combo.setStyleSheet("""
            QComboBox {
                font-size: 14px;
                padding: 5px;
                border: 2px solid #2196F3;
                border-radius: 5px;
                min-width: 100px;
            }
        """)
        self.level_combo.currentTextChanged.connect(self.on_level_changed)
        level_layout.addStretch()
        level_layout.addWidget(level_label)
        level_layout.addWidget(self.level_combo)
        level_layout.addStretch()
        layout.addLayout(level_layout)
        
        # 字体大小选择
        font_layout = QHBoxLayout()
        font_label = QLabel("翻译字体大小:")
        font_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["12", "14", "16", "18", "20", "22", "24", "26", "28", "30"])
        current_font_size = ConfigManager.load_font_size()
        self.font_size_combo.setCurrentText(str(current_font_size))
        self.font_size_combo.setStyleSheet("""
            QComboBox {
                font-size: 14px;
                padding: 5px;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                min-width: 100px;
            }
        """)
        self.font_size_combo.currentTextChanged.connect(self.on_font_size_changed)
        font_layout.addStretch()
        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_size_combo)
        font_layout.addStretch()
        layout.addLayout(font_layout)
        
        # 缩放比例选择
        zoom_layout = QHBoxLayout()
        zoom_label = QLabel("翻译窗口缩放:")
        zoom_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.zoom_scale_combo = QComboBox()
        self.zoom_scale_combo.addItems(["66%", "75%", "90%", "100%", "125%", "150%", "175%", "200%"])
        current_zoom_scale = ConfigManager.load_zoom_scale()
        self.zoom_scale_combo.setCurrentText(f"{current_zoom_scale}%")
        self.zoom_scale_combo.setStyleSheet("""
            QComboBox {
                font-size: 14px;
                padding: 5px;
                border: 2px solid #FF9800;
                border-radius: 5px;
                min-width: 100px;
            }
        """)
        self.zoom_scale_combo.currentTextChanged.connect(self.on_zoom_scale_changed)
        zoom_layout.addStretch()
        zoom_layout.addWidget(zoom_label)
        zoom_layout.addWidget(self.zoom_scale_combo)
        zoom_layout.addStretch()
        layout.addLayout(zoom_layout)
        
        # 当前截图区域显示
        x, y, width, height = ConfigManager.load_region()
        self.current_region = (x, y, width, height)
        self.region_label = QLabel(f"当前截图区域: ({x}, {y}) - 大小: {width}x{height}")
        self.region_label.setAlignment(Qt.AlignCenter)
        self.region_label.setStyleSheet("font-size: 14px; color: #666; margin: 10px;")
        layout.addWidget(self.region_label)
        
        # 说明
        info_label = QLabel("使用说明：\n• 点击「设置截图区域」输入要翻译的屏幕区域坐标\n• 建议先用系统截图工具（Win+Shift+S）查看坐标\n• 然后点击「启动翻译窗口」开始使用\n• 在翻译窗口中可以按数字键2或点击快速截图按钮翻译\n• 支持游戏内实时截图翻译")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 14px; margin: 20px; background-color: #f9f9f9; padding: 15px; border-radius: 8px;")
        layout.addWidget(info_label)
        
        # 按钮布局
        button_layout = QVBoxLayout()
        
        # 设置截图区域按钮
        setup_btn = QPushButton("设置截图区域")
        setup_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 15px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        setup_btn.clicked.connect(self.setup_screenshot_region)
        button_layout.addWidget(setup_btn)
        
        # 启动翻译窗口按钮
        start_btn = QPushButton("启动翻译窗口")
        start_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        start_btn.clicked.connect(self.start_translation_window)
        button_layout.addWidget(start_btn)
        
        layout.addLayout(button_layout)
        central_widget.setLayout(layout)
        
        # 创建区域选择器
        self.region_input_dialog = RegionInputDialog(self)
        
    def setup_screenshot_region(self):
        """设置截图区域"""
        if self.region_input_dialog.exec_() == QDialog.Accepted:
            x, y, width, height = self.region_input_dialog.get_region()
            self.on_region_selected(x, y, width, height)
    
    def on_level_changed(self, level):
        if ConfigManager.save_user_level(level):
            print(f"用户英语水平已设置为: {level}")
        else:
            QMessageBox.warning(self, "设置失败", "保存用户水平设置失败，请重试")
    
    def on_font_size_changed(self, font_size_text):
        font_size = int(font_size_text)
        if ConfigManager.save_font_size(font_size):
            print(f"翻译字体大小已设置为: {font_size}")
        else:
            QMessageBox.warning(self, "设置失败", "保存字体大小设置失败，请重试")
    
    def on_zoom_scale_changed(self, zoom_scale_text):
        zoom_scale = int(zoom_scale_text.replace("%", ""))
        if ConfigManager.save_zoom_scale(zoom_scale):
            print(f"翻译窗口缩放已设置为: {zoom_scale}%")
        else:
            QMessageBox.warning(self, "设置失败", "保存缩放比例设置失败，请重试")
        
    def on_region_selected(self, x, y, width, height):
        """处理区域选择完成"""
        if ConfigManager.save_region(x, y, width, height):
            self.current_region = (x, y, width, height)
            self.region_label.setText(f"当前截图区域: ({x}, {y}) - 大小: {width}x{height}")
            QMessageBox.information(self, "设置成功", f"截图区域已设置为:\n位置: ({x}, {y})\n大小: {width} x {height}")
        else:
            QMessageBox.warning(self, "设置失败", "保存截图区域设置失败，请重试")
        
    def start_translation_window(self):
        self.translation_window = TranslationWindow(self)
        self.translation_window.show()
        self.hide()

