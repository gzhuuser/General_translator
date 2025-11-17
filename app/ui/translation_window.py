import os
import sys
import json
import tempfile
import shutil
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTextEdit, QFrame, QDesktopWidget, QApplication, QMessageBox)
from PyQt5.QtCore import Qt, QPoint

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.managers import ConfigManager, NotesManager, rag_manager
from app.threads import ProcessingThread, TextCorrectionThread
from app.ui.notes_window import NotesWindow
from app.ui.screenshot_widget import ScreenshotWidget
from app.ui.region_input_dialog import RegionInputDialog
from app.ui.draggable_button import DraggableButton

class TranslationWindow(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window  # 主窗口引用
        self.notes_window = None  # 初始化笔记窗口
        self.processing_thread = None  # 添加线程管理
        self.correction_thread = None  # OCR文本修正线程
        self.is_processing = False  # 添加处理状态标志
        self.user_level = ConfigManager.load_user_level()  # 加载用户水平设置
        self.font_size = ConfigManager.load_font_size()  # 加载字体大小设置
        self.zoom_scale = ConfigManager.load_zoom_scale()  # 加载缩放比例设置
        self.is_details_visible = True  # 翻译详情区域是否可见
        
        # 模型已在run.py中预加载，这里无需重复初始化
        print("[UI] 启动翻译窗口界面...")
        print(f"[UI] 用户英语水平: {self.user_level}")
        print(f"[UI] 字体大小: {self.font_size}")
        print(f"[UI] 缩放比例: {self.zoom_scale}%")
        
        self.init_ui()
        
    
    def auto_screenshot(self):
        """自动截取用户设置的区域并处理"""
        if self.is_processing:
            print("OCR处理正在进行中，忽略此次调用")
            self.status_label.setText("OCR处理正在进行中，请等待...")
            return
            
        try:
            # 获取保存的截图区域
            x, y, width, height = ConfigManager.load_region()
            
            screen = QApplication.primaryScreen()
            screenshot = screen.grabWindow(0, x, y, width, height)
            
            # 确保img目录存在
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            img_dir = os.path.join(current_dir, "img")
            if not os.path.exists(img_dir):
                os.makedirs(img_dir)
            
            # 保存为1.png
            img_path = os.path.join(img_dir, "1.png")
            screenshot.save(img_path, 'PNG')
            
            print(f"截图已保存到: {img_path}")
            self.status_label.setText(f"自动截图完成 (区域: {x},{y},{width}x{height})，正在处理...")
            
            # 创建临时文件副本用于处理（避免删除原始文件）
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            shutil.copy2(img_path, temp_file.name)
            temp_file.close()
            
            # 调用统一的处理方法
            self.start_ocr_processing(temp_file.name)
            
        except Exception as e:
            print(f"自动截图失败: {str(e)}")
            self.status_label.setText(f"自动截图失败: {str(e)}")
        
    def closeEvent(self, event):
        """窗口关闭时停止热键监听"""
        # 停止OCR处理线程
        if hasattr(self, 'processing_thread') and self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.quit()
            self.processing_thread.wait(3000)  # 等待3秒
        
        event.accept()
        
    def start_ocr_processing(self, image_path):
        """统一的OCR处理方法"""
        if self.is_processing:
            print("已有OCR处理正在进行，忽略新请求")
            return
        
        # 停止之前的线程（如果存在）
        if hasattr(self, 'processing_thread') and self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.quit()
            self.processing_thread.wait(1000)
        
        print(f"开始OCR处理: {image_path}")
        self.is_processing = True
        
        # 禁用按钮
        self.clear_btn.setEnabled(False)
        self.screenshot_btn.setEnabled(False)
        self.setup_region_btn.setEnabled(False)
        
        # 创建并启动处理线程
        self.processing_thread = ProcessingThread(image_path, self.user_level)
        self.processing_thread.text_processed.connect(self.on_text_processed)
        self.processing_thread.error_occurred.connect(self.on_error)
        self.processing_thread.finished.connect(self.on_processing_finished)
        self.processing_thread.start()
    
    def on_processing_finished(self):
        """OCR处理完成后的清理工作"""
        print("OCR处理完成")
        self.is_processing = False
        
        # 重新启用按钮
        self.clear_btn.setEnabled(True)
        self.screenshot_btn.setEnabled(True)
        self.setup_region_btn.setEnabled(True)
        
        # 清理线程引用
        if hasattr(self, 'processing_thread'):
            self.processing_thread = None
        
    def init_ui(self):
        self.setWindowTitle("二游翻译助手")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.is_topmost = True  # 记录置顶状态
        
        # 根据缩放比例计算窗口尺寸
        self.base_width = 680
        self.base_height = 800
        self.base_collapsed_width = 180
        self.base_collapsed_height = 80
        scale_factor = self.zoom_scale / 100.0
        self.scaled_width = int(self.base_width * scale_factor)
        self.scaled_height = int(self.base_height * scale_factor)
        self.scaled_collapsed_width = int(self.base_collapsed_width * scale_factor)
        self.scaled_collapsed_height = int(self.base_collapsed_height * scale_factor)
        
        # 设置窗口位置（屏幕左侧）
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(20, 150, self.scaled_width, self.scaled_height)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 背景框架
        self.main_frame = QFrame()
        self.main_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 0);
                border-radius: 0px;
                border: none;
            }
        """)
        
        frame_layout = QVBoxLayout(self.main_frame)
        
        # 标题
        self.title_label = QLabel("二游翻译助手")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #FF0000;
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                background-color: rgba(0, 0, 0, 0);
                border: none;
                margin-bottom: 10px;
            }
        """)
        frame_layout.addWidget(self.title_label)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        # 设置按钮
        self.setup_region_btn = QPushButton("设置")
        self.setup_region_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 165, 0, 200);
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 165, 0, 255);
            }
            QPushButton:pressed {
                background-color: rgba(220, 140, 0, 255);
            }
        """)
        self.setup_region_btn.clicked.connect(self.back_to_settings)
        
        self.screenshot_btn = QPushButton("快速截图")
        self.screenshot_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(74, 144, 226, 200);
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(74, 144, 226, 255);
            }
            QPushButton:pressed {
                background-color: rgba(55, 120, 200, 255);
            }
        """)
        self.screenshot_btn.clicked.connect(self.start_screenshot)
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(231, 76, 60, 200);
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(231, 76, 60, 255);
            }
            QPushButton:pressed {
                background-color: rgba(200, 60, 50, 255);
            }
        """)
        self.close_btn.clicked.connect(self.close)
        
        # 清除按钮
        self.clear_btn = QPushButton("清除翻译")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(46, 204, 113, 200);
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(46, 204, 113, 255);
            }
            QPushButton:pressed {
                background-color: rgba(39, 174, 96, 255);
            }
        """)
        self.clear_btn.clicked.connect(self.clear_translation)
        
        # 生成笔记按钮
        self.notes_btn = QPushButton("📚 笔记")
        self.notes_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(156, 39, 176, 200);
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(156, 39, 176, 255);
            }
            QPushButton:pressed {
                background-color: rgba(123, 31, 162, 255);
            }
        """)
        self.notes_btn.clicked.connect(self.open_notes_window)
        
        # 收起/展开按钮（可拖拽）
        self.toggle_btn = DraggableButton("收起", self)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 193, 7, 200);
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 193, 7, 255);
            }
            QPushButton:pressed {
                background-color: rgba(255, 160, 0, 255);
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_details)
        
        button_layout.addWidget(self.setup_region_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.notes_btn)
        button_layout.addWidget(self.toggle_btn)
        button_layout.addWidget(self.screenshot_btn)
        button_layout.addWidget(self.close_btn)
        frame_layout.addLayout(button_layout)
        
        # 翻译结果显示
        self.translation_label = QLabel("翻译:")
        self.translation_label.setStyleSheet(f"color: #0066CC; font-size: {self.font_size}px; font-weight: bold; margin-top: 15px;")
        frame_layout.addWidget(self.translation_label)
        
        self.translation_text = QTextEdit()
        self.translation_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: rgba(0, 0, 0, 0);
                color: #0066CC;
                border: none;
                border-radius: 0px;
                padding: 10px;
                font-size: {self.font_size}px;
                font-weight: bold;
            }}
        """)
        self.translation_text.setReadOnly(True)
        self.translation_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.translation_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        frame_layout.addWidget(self.translation_text)
        
        # 重要单词显示
        self.words_label = QLabel("重要单词:")
        self.words_label.setStyleSheet(f"color: #FF0000; font-size: {self.font_size}px; font-weight: bold; margin-top: 15px;")
        frame_layout.addWidget(self.words_label)
        
        self.words_text = QTextEdit()
        words_font_size = max(12, int(self.font_size * 0.82))
        self.words_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: rgba(0, 0, 0, 0);
                color: #FF0000;
                border: none;
                border-radius: 0px;
                padding: 10px;
                font-size: {words_font_size}px;
                font-weight: bold;
            }}
        """)
        self.words_text.setReadOnly(True)
        self.words_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.words_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        frame_layout.addWidget(self.words_text)
        
        # 语法解释显示
        self.grammar_label = QLabel("语法解释:")
        self.grammar_label.setStyleSheet(f"color: #FF00FF; font-size: {self.font_size}px; font-weight: bold; margin-top: 15px;")
        frame_layout.addWidget(self.grammar_label)
        
        self.grammar_text = QTextEdit()
        grammar_font_size = max(12, int(self.font_size * 0.82))
        self.grammar_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: rgba(0, 0, 0, 0);
                color: #FF00FF;
                border: none;
                border-radius: 0px;
                padding: 10px;
                font-size: {grammar_font_size}px;
                font-weight: bold;
            }}
        """)
        self.grammar_text.setReadOnly(True)
        self.grammar_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.grammar_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        frame_layout.addWidget(self.grammar_text)
        
        # 状态显示
        x, y, width, height = ConfigManager.load_region()
        self.status_label = QLabel(f"当前区域: ({x},{y}) {width}x{height}")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #00FF00;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
                background-color: rgba(0, 0, 0, 0);
                border: none;
            }
        """)
        frame_layout.addWidget(self.status_label)
        
        main_layout.addWidget(self.main_frame)
        self.setLayout(main_layout)
        
        # 截图工具
        self.screenshot_widget = ScreenshotWidget()
        self.screenshot_widget.screenshot_taken.connect(self.process_screenshot)
        
        # 区域选择器
        self.region_input_dialog = RegionInputDialog(self)
        
        # 使窗口可拖拽
        self.drag_position = QPoint()
        
    def back_to_settings(self):
        """返回设置页面"""
        if self.main_window:
            # 显示主窗口
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
        
        # 关闭翻译窗口
        self.close()
    
    def setup_region(self):
        """设置截图区域"""
        if self.region_input_dialog.exec_() == QDialog.Accepted:
            x, y, width, height = self.region_input_dialog.get_region()
            self.on_region_selected(x, y, width, height)
        
    def on_region_selected(self, x, y, width, height):
        """处理区域选择完成"""
        if ConfigManager.save_region(x, y, width, height):
            self.status_label.setText(f"区域已更新: ({x},{y}) {width}x{height} | 按2键或点击'快速截图' | F9切换置顶")
        else:
            self.status_label.setText("区域设置失败，请重试")
        
    def keyPressEvent(self, event):
        """处理键盘事件"""
        # F9键切换置顶状态
        if event.key() == Qt.Key_F9:
            self.toggle_topmost()
        super().keyPressEvent(event)
    
    def toggle_topmost(self):
        """切换窗口置顶状态"""
        self.is_topmost = not self.is_topmost
        
        if self.is_topmost:
            self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
            self.status_label.setText("窗口已置顶 (按F9切换)")
        else:
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.status_label.setText("窗口取消置顶 (按F9切换)")
        
        # 重新显示窗口以应用新的窗口标志
        self.show()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            
    def start_screenshot(self):
        """直接截取用户设置的区域"""
        if self.is_processing:
            print("OCR处理正在进行中，忽略此次调用")
            self.status_label.setText("OCR处理正在进行中，请等待...")
            return
        
        # 自动清除之前的翻译内容
        self.clear_translation()
        print("已自动清除之前的翻译内容")
            
        try:
            print("开始快速截图...")
            
            # 获取保存的截图区域
            x, y, width, height = ConfigManager.load_region()
            
            screen = QApplication.primaryScreen()
            screenshot = screen.grabWindow(0, x, y, width, height)
            
            # 确保img目录存在
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            img_dir = os.path.join(current_dir, "img")
            if not os.path.exists(img_dir):
                os.makedirs(img_dir)
            
            # 保存为1.png
            img_path = os.path.join(img_dir, "1.png")
            screenshot.save(img_path, 'PNG')
            
            print(f"快速截图完成: {img_path}")
            self.status_label.setText(f"快速截图完成 (区域: {x},{y},{width}x{height})，正在处理...")
            
            # 创建临时文件副本用于处理
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            shutil.copy2(img_path, temp_file.name)
            temp_file.close()
            
            # 调用统一的处理方法
            self.start_ocr_processing(temp_file.name)
            
        except Exception as e:
            print(f"快速截图失败: {str(e)}")
            self.status_label.setText(f"快速截图失败: {str(e)}")
    
    def clear_translation(self):
        """清除所有翻译文本内容"""
        self.translation_text.clear()
        self.words_text.clear()
        self.grammar_text.clear()
        self.status_label.setText("翻译内容已清除")
        
        # 重置文本框高度
        self.translation_text.setFixedHeight(100)
        self.words_text.setFixedHeight(80)
        self.grammar_text.setFixedHeight(80)
    
    def toggle_details(self):
        """切换翻译详情区域的显示/隐藏"""
        self.is_details_visible = not self.is_details_visible
        
        if self.is_details_visible:
            # 展开状态：显示所有控件
            self.title_label.setVisible(True)
            self.setup_region_btn.setVisible(True)
            self.clear_btn.setVisible(True)
            self.notes_btn.setVisible(True)
            self.screenshot_btn.setVisible(True)
            self.close_btn.setVisible(True)
            self.translation_label.setVisible(True)
            self.translation_text.setVisible(True)
            self.words_label.setVisible(True)
            self.words_text.setVisible(True)
            self.grammar_label.setVisible(True)
            self.grammar_text.setVisible(True)
            self.status_label.setVisible(True)
            
            # 恢复窗口大小
            self.setFixedSize(self.scaled_width, self.scaled_height)
            
            # 更新按钮文本和样式
            self.toggle_btn.setText("收起")
            self.toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 193, 7, 200);
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 5px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(255, 193, 7, 255);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 160, 0, 255);
                }
            """)
            
            print("翻译详情已展开")
        else:
            # 收起状态：只显示展开按钮
            self.title_label.setVisible(False)
            self.setup_region_btn.setVisible(False)
            self.clear_btn.setVisible(False)
            self.notes_btn.setVisible(False)
            self.screenshot_btn.setVisible(False)
            self.close_btn.setVisible(False)
            self.translation_label.setVisible(False)
            self.translation_text.setVisible(False)
            self.words_label.setVisible(False)
            self.words_text.setVisible(False)
            self.grammar_label.setVisible(False)
            self.grammar_text.setVisible(False)
            self.status_label.setVisible(False)
            
            # 调整窗口大小为小按钮
            self.setFixedSize(self.scaled_collapsed_width, self.scaled_collapsed_height)
            
            # 确保展开按钮可见并填满整个窗口
            self.toggle_btn.setVisible(True)
            self.toggle_btn.setGeometry(0, 0, self.scaled_collapsed_width, self.scaled_collapsed_height)
            self.toggle_btn.raise_()  # 确保按钮在最上层
            
            # 更新按钮文本和样式
            self.toggle_btn.setText("📖 展开")
            self.toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 193, 7, 240);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: 18px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(255, 200, 50, 255);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 160, 0, 255);
                }
            """)
            
            print("翻译详情已收起")
        
    def process_screenshot(self, image_path):
        """处理截图（用于拖拽选择等情况）"""
        print("process_screenshot被调用，使用统一处理方法")
        self.status_label.setText("处理中，请稍候...")
        self.start_ocr_processing(image_path)
        
    def adjust_text_height(self, text_edit):
        """根据内容动态调整文本框高度"""
        doc = text_edit.document()
        doc.setTextWidth(text_edit.viewport().width())
        height = doc.size().height() + 30  # 添加一些边距
        text_edit.setFixedHeight(int(height))
    
    def open_notes_window(self):
        """打开笔记窗口"""
        try:
            if not hasattr(self, 'notes_window') or not self.notes_window:
                self.notes_window = NotesWindow()
                # 连接笔记窗口的返回信号
                self.notes_window.return_to_main.connect(self.on_return_from_notes)
            
            self.notes_window.show()
            self.notes_window.raise_()
            self.notes_window.activateWindow()
            
            # 隐藏主窗口
            self.hide()
            
        except Exception as e:
            QMessageBox.warning(self, "打开笔记失败", f"打开笔记窗口时发生错误:\n{str(e)}")
    
    def on_return_from_notes(self):
        """从笔记窗口返回主程序"""
        try:
            # 关闭笔记窗口
            if hasattr(self, 'notes_window') and self.notes_window:
                self.notes_window.close()
                self.notes_window = None
            
            # 重新显示主窗口
            self.show()
            self.raise_()
            self.activateWindow()
            
        except Exception as e:
            print(f"返回主程序时出错: {e}")
            # 确保主窗口显示
            self.show()
    
    def on_text_processed(self, original_text, translated_text):
        # 不再显示原文，直接处理翻译结果
        
        
        # 尝试解析JSON格式的翻译结果
        try:
            json_str = translated_text.strip()
            
            # 移除可能的Markdown格式
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.startswith("```"):
                json_str = json_str[3:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            json_str = json_str.strip()
            
            
            result_dict = json.loads(json_str)
            
            # 显示翻译
            translation = result_dict.get('translation', '未找到翻译')
            self.translation_text.setPlainText(translation)
            self.adjust_text_height(self.translation_text)
            
            # 显示重要单词
            important_words = result_dict.get('important_words', {})
            words_text = ""
            for word, meaning in important_words.items():
                words_text += f"• {word}: {meaning}\n"
            self.words_text.setPlainText(words_text.strip() if words_text else "未找到重要单词")
            self.adjust_text_height(self.words_text)
            
            # 显示语法解释
            grammar = result_dict.get('important_grammar', {})
            grammar_text = ""
            for sentence, explanation in grammar.items():
                grammar_text += f"【{sentence}】\n{explanation}\n\n"
            self.grammar_text.setPlainText(grammar_text.strip() if grammar_text else "未找到语法解释")
            self.adjust_text_height(self.grammar_text)
            
            # 检查是否来自RAG并显示相应状态
            if result_dict.get('from_rag', False):
                similarity = result_dict.get('similarity', 0)
                special_terms = result_dict.get('special_terms', {})
                if special_terms:
                    terms_info = f" | 检测到专有名词: {len(special_terms)}个"
                else:
                    terms_info = ""
                self.status_label.setText(f"RAG匹配成功！相似度: {similarity:.1%} (来自历史学习记录){terms_info}")
            else:
                # 显示专有名词检测信息
                special_terms_info = ""
                try:
                    # 从翻译结果中提取专有名词信息（如果有的话）
                    if 'special_terms' in result_dict:
                        special_terms = result_dict['special_terms']
                        if special_terms:
                            special_terms_info = f" | 检测到专有名词: {len(special_terms)}个"
                except:
                    pass
                
                self.status_label.setText(f"API翻译完成{special_terms_info}")
            
            # 保存翻译记录到笔记（只有API翻译的才保存，避免重复）
            if not result_dict.get('from_rag', False):
                # 启动独立线程修正OCR文本，然后保存
                self.correction_thread = TextCorrectionThread(
                    original_text,
                    translation,
                    important_words,
                    grammar
                )
                self.correction_thread.correction_completed.connect(self.on_correction_completed)
                self.correction_thread.correction_failed.connect(self.on_correction_failed)
                self.correction_thread.start()
                print("已启动OCR文本修正线程（后台运行）")
            
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            # 如果不是JSON格式，直接显示翻译结果
            self.translation_text.setPlainText(translated_text)
            self.adjust_text_height(self.translation_text)
            self.words_text.setPlainText("JSON解析失败，请检查LLM返回格式")
            self.adjust_text_height(self.words_text)
            self.grammar_text.setPlainText("JSON解析失败，请检查LLM返回格式")
            self.adjust_text_height(self.grammar_text)
            self.status_label.setText("JSON解析失败，但显示了原始翻译")
        except Exception as e:
            print(f"其他错误: {e}")
            self.translation_text.setPlainText(translated_text)
            self.adjust_text_height(self.translation_text)
            self.words_text.setPlainText(f"处理错误: {str(e)}")
            self.adjust_text_height(self.words_text)
            self.grammar_text.setPlainText(f"处理错误: {str(e)}")
            self.adjust_text_height(self.grammar_text)
            self.status_label.setText("处理过程中出现错误")
    
    def on_correction_completed(self, corrected_text, translation, important_words, grammar_points):
        """OCR文本修正完成后保存笔记"""
        try:
            saved = NotesManager.save_translation_record(
                original_text=corrected_text,
                translation=translation,
                important_words=important_words,
                grammar_points=grammar_points
            )
            if saved:
                print("翻译记录已保存到笔记（使用修正后的文本）")
                # 同时添加到RAG索引
                rag_manager.add_new_record_to_index(corrected_text, translation, important_words, grammar_points)
        except Exception as save_error:
            print(f"保存翻译记录失败: {save_error}")
    
    def on_correction_failed(self):
        """OCR文本修正失败时的处理（静默失败，不影响用户体验）"""
        print("OCR文本修正失败，但不影响翻译功能")
        
    def on_error(self, error_message):
        """处理OCR错误"""
        print(f"OCR处理出错: {error_message}")
        self.status_label.setText(f"错误: {error_message}")
        # 清空所有文本框
        self.translation_text.clear()
        self.words_text.clear()
        self.grammar_text.clear()


