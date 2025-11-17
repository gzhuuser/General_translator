from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QLabel, QSpinBox, QDialogButtonBox
from app.managers import ConfigManager


class RegionInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("设置截图区域坐标")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout()
        
        info_label = QLabel("""请输入截图区域的坐标信息：

推荐方法：使用系统截图工具
• 按Win+Shift+S（或使用QQ截图、微信截图等）
• 在截图工具中框选目标区域，查看显示的坐标信息
• 将坐标填入下方输入框

手动测量方法：
• 打开游戏或目标窗口
• 使用屏幕测量工具记录要翻译区域的坐标和大小""")
        info_label.setStyleSheet("font-size: 12px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        form_layout = QGridLayout()
        
        x, y, width, height = ConfigManager.load_region()
        
        form_layout.addWidget(QLabel("X坐标 (左上角):"), 0, 0)
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 9999)
        self.x_spin.setValue(x)
        form_layout.addWidget(self.x_spin, 0, 1)
        
        form_layout.addWidget(QLabel("Y坐标 (左上角):"), 1, 0)
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 9999)
        self.y_spin.setValue(y)
        form_layout.addWidget(self.y_spin, 1, 1)
        
        form_layout.addWidget(QLabel("宽度:"), 2, 0)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 9999)
        self.width_spin.setValue(width)
        form_layout.addWidget(self.width_spin, 2, 1)
        
        form_layout.addWidget(QLabel("高度:"), 3, 0)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 9999)
        self.height_spin.setValue(height)
        form_layout.addWidget(self.height_spin, 3, 1)
        
        layout.addLayout(form_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def get_region(self):
        return self.x_spin.value(), self.y_spin.value(), self.width_spin.value(), self.height_spin.value()
