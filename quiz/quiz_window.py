import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTextEdit, QFrame, 
                             QProgressBar, QMessageBox, QDialog, QListWidget,
                             QListWidgetItem, QLineEdit, QRadioButton, 
                             QButtonGroup, QScrollArea, QGridLayout, QTabWidget,
                             QSpinBox, QComboBox, QCheckBox, QSplitter, QGroupBox,
                             QProgressDialog, QApplication)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPen, QColor, QBrush, QMovie

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quiz.quiz_generator import QuizGenerator, QuizSession
from quiz.progress_manager import ProgressManager, WrongQuestionReview


class LoadingDialog(QDialog):
    """加载对话框，显示题目生成进度"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("正在生成题目...")
        self.setModal(True)
        self.setFixedSize(400, 200)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title_label = QLabel("🤖 AI正在为你生成个性化题目...")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                text-align: center;
                padding: 10px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3498db;
                border-radius: 10px;
                text-align: center;
                height: 25px;
                font-weight: bold;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:0.5 #5dade2, stop:1 #85c1e9);
                border-radius: 8px;
            }
        """)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("正在分析学习记录...")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                text-align: center;
                padding: 5px;
            }
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 取消按钮
        self.cancel_btn = QPushButton("取消生成")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def update_progress(self, value, status_text):
        """更新进度"""
        self.progress_bar.setValue(value)
        self.status_label.setText(status_text)
        QApplication.processEvents()  # 确保界面更新


class QuizSetupDialog(QDialog):
    """测试设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📚 测试设置")
        self.setModal(True)
        self.resize(500, 600)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("🎯 自定义测试设置")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                text-align: center;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 题目数量设置
        count_group = QGroupBox("📊 题目数量")
        count_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #34495e;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        count_layout = QHBoxLayout(count_group)
        
        count_layout.addWidget(QLabel("题目数量:"))
        self.question_count_spin = QSpinBox()
        self.question_count_spin.setRange(5, 50)
        self.question_count_spin.setValue(10)
        self.question_count_spin.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QSpinBox:focus {
                border-color: #3498db;
            }
        """)
        count_layout.addWidget(self.question_count_spin)
        count_layout.addStretch()
        
        layout.addWidget(count_group)
        
        # 题目类型选择
        type_group = QGroupBox("📝 题目类型")
        type_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #34495e;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        type_layout = QVBoxLayout(type_group)
        
        checkbox_style = """
            QCheckBox {
                font-size: 14px;
                spacing: 10px;
                color: #2c3e50;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border: 2px solid #2980b9;
                border-radius: 3px;
            }
            QCheckBox::indicator:unchecked {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 3px;
            }
        """
        
        self.word_spelling_cb = QCheckBox("✏️ 单词默写题")
        self.word_spelling_cb.setChecked(True)
        self.word_spelling_cb.setStyleSheet(checkbox_style)
        
        self.grammar_choice_cb = QCheckBox("📚 语法选择题")
        self.grammar_choice_cb.setChecked(True)
        self.grammar_choice_cb.setStyleSheet(checkbox_style)
        
        self.word_choice_cb = QCheckBox("💎 单词释义选择题")
        self.word_choice_cb.setChecked(True)
        self.word_choice_cb.setStyleSheet(checkbox_style)
        
        self.translation_choice_cb = QCheckBox("🌐 翻译选择题")
        self.translation_choice_cb.setChecked(True)
        self.translation_choice_cb.setStyleSheet(checkbox_style)
        
        type_layout.addWidget(self.word_spelling_cb)
        type_layout.addWidget(self.grammar_choice_cb)
        type_layout.addWidget(self.word_choice_cb)
        type_layout.addWidget(self.translation_choice_cb)
        
        layout.addWidget(type_group)
        
        # 难度级别选择
        difficulty_group = QGroupBox("⚡ 难度级别")
        difficulty_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #34495e;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        difficulty_layout = QHBoxLayout(difficulty_group)
        
        difficulty_layout.addWidget(QLabel("选择难度:"))
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["全部", "简单", "中等", "困难"])
        self.difficulty_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
                background-color: white;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #bdc3c7;
                selection-background-color: #3498db;
            }
        """)
        difficulty_layout.addWidget(self.difficulty_combo)
        difficulty_layout.addStretch()
        
        layout.addWidget(difficulty_group)
        
        # 测试模式选择
        mode_group = QGroupBox("🎲 测试模式")
        mode_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #34495e;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        mode_layout = QVBoxLayout(mode_group)
        
        radio_style = """
            QRadioButton {
                font-size: 14px;
                spacing: 10px;
                color: #2c3e50;
                padding: 5px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator:checked {
                background-color: #3498db;
                border: 2px solid #2980b9;
                border-radius: 9px;
            }
            QRadioButton::indicator:unchecked {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 9px;
            }
        """
        
        self.mode_group = QButtonGroup()
        
        self.normal_mode_rb = QRadioButton("📚 标准模式（从学习记录随机生成）")
        self.normal_mode_rb.setChecked(True)
        self.normal_mode_rb.setStyleSheet(radio_style)
        
        self.review_mode_rb = QRadioButton("🔄 错题复习模式（专门练习之前做错的题目）")
        self.review_mode_rb.setStyleSheet(radio_style)
        
        self.mode_group.addButton(self.normal_mode_rb, 0)
        self.mode_group.addButton(self.review_mode_rb, 1)
        
        mode_layout.addWidget(self.normal_mode_rb)
        mode_layout.addWidget(self.review_mode_rb)
        
        layout.addWidget(mode_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        start_btn = QPushButton("🚀 开始测试")
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        start_btn.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(start_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def get_settings(self):
        """获取用户设置"""
        question_types = []
        if self.word_spelling_cb.isChecked():
            question_types.append("word_spelling")
        if self.grammar_choice_cb.isChecked():
            question_types.append("grammar_choice")
        if self.word_choice_cb.isChecked():
            question_types.append("word_choice")
        if self.translation_choice_cb.isChecked():
            question_types.append("translation_choice")
        
        difficulty_map = {"全部": None, "简单": "easy", "中等": "medium", "困难": "hard"}
        
        # 获取测试模式
        test_mode = "normal" if self.normal_mode_rb.isChecked() else "review"
        
        return {
            "question_count": self.question_count_spin.value(),
            "question_types": question_types if question_types else None,
            "difficulty": difficulty_map[self.difficulty_combo.currentText()],
            "test_mode": test_mode
        }


class QuizGeneratorThread(QThread):
    """题目生成线程"""
    questions_generated = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    progress_updated = pyqtSignal(int, str)  # 进度值, 状态文本
    
    def __init__(self, records, settings):
        super().__init__()
        self.records = records
        self.settings = settings
        self._is_cancelled = False
    
    def cancel(self):
        """取消生成"""
        self._is_cancelled = True
    
    def run(self):
        try:
            if self._is_cancelled:
                return
                
            self.progress_updated.emit(10, "正在分析学习记录...")
            generator = QuizGenerator()
            
            if self._is_cancelled:
                return
            
            self.progress_updated.emit(20, "正在筛选适合的记录...")
            
            questions = generator.generate_quiz_from_records(
                self.records,
                question_count=self.settings["question_count"],
                question_types=self.settings["question_types"]
            )
            
            if self._is_cancelled:
                return
                
            if not questions:
                self.error_occurred.emit("没有足够的学习记录来生成题目")
                return
            
            self.progress_updated.emit(40, f"已生成 {len(questions)} 道基础题目...")
            
            if self._is_cancelled:
                return
            
            # 计算需要LLM处理的题目数量
            llm_questions = [q for q in questions if q.get("question_type") in ["grammar_choice", "word_choice", "translation_choice"]]
            
            if llm_questions:
                self.progress_updated.emit(50, "正在调用AI生成高质量选项...")
                
                # 多线程生成选项，并提供进度回调
                enhanced_questions = self._generate_options_with_progress(generator, questions, llm_questions)
                
                if self._is_cancelled:
                    return
                    
                self.progress_updated.emit(90, "正在完善题目细节...")
                self.questions_generated.emit(enhanced_questions)
            else:
                self.progress_updated.emit(90, "正在完善题目...")
                self.questions_generated.emit(questions)
            
            self.progress_updated.emit(100, "题目生成完成！")
            
        except Exception as e:
            if not self._is_cancelled:
                self.error_occurred.emit(f"生成题目时出错: {str(e)}")
    
    def _generate_options_with_progress(self, generator, all_questions, llm_questions):
        """使用多线程生成选项，并提供进度更新"""
        try:
            total_llm = len(llm_questions)
            completed = 0
            
            # 一次性处理所有题目，利用多线程并发
            self.progress_updated.emit(50, f"AI正在并发生成 {total_llm} 道题目的选项...")
            
            # 直接使用多线程处理所有题目
            enhanced_questions = generator.generate_options_batch_threaded(llm_questions, max_workers=8)
            
            if self._is_cancelled:
                return all_questions
            
            # 更新all_questions中对应的题目
            result_questions = all_questions.copy()
            for enhanced_q in enhanced_questions:
                for j, orig_q in enumerate(result_questions):
                    if orig_q.get("question_id") == enhanced_q.get("question_id"):
                        result_questions[j] = enhanced_q
                        break
            
            self.progress_updated.emit(85, "AI生成选项完成！")
            
            return result_questions
            
        except Exception as e:
            print(f"生成选项时出错: {e}")
            return all_questions


class QuizWindow(QMainWindow):
    """题库练习主窗口"""
    
    def __init__(self, records):
        super().__init__()
        self.records = records
        self.quiz_session = None
        self.current_question = None
        self.user_answer = None
        
        # 初始化进度管理器
        self.progress_manager = ProgressManager()
        self.wrong_question_review = WrongQuestionReview(self.progress_manager)
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("🎯 英语题库练习")
        
        # 自适应窗口大小
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        screen_width = screen.width()
        screen_height = screen.height()
        
        window_width = min(1200, int(screen_width * 0.8))
        window_height = min(900, int(screen_height * 0.8))
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.setGeometry(x, y, window_width, window_height)
        
        # 主窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
        """)
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 创建不同的页面
        self.create_start_page(main_layout)
        self.create_quiz_page(main_layout)
        self.create_result_page(main_layout)
        
        # 默认显示开始页面
        self.show_start_page()
    
    def create_start_page(self, parent_layout):
        """创建开始页面"""
        self.start_page = QWidget()
        main_layout = QVBoxLayout(self.start_page)
        main_layout.setContentsMargins(0, 0, 0, 0)  # 主布局无边距
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #f1f3f4;
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background-color: #c1c1c1;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a8a8a8;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        # 创建内容容器
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(30)
        layout.setContentsMargins(20, 20, 20, 20)  # 给内容适当的边距
        
        # 标题区域
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 15px;
                padding: 30px;
            }
        """)
        title_layout = QVBoxLayout(title_frame)
        
        title_label = QLabel("🎯 英语题库练习系统")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
                text-align: center;
                background: transparent;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("基于你的学习记录智能生成个性化测试题目")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 16px;
                text-align: center;
                background: transparent;
                margin-top: 10px;
            }
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        layout.addWidget(title_frame)
        
        # 统计信息
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 2px solid #e9ecef;
                padding: 25px;
            }
        """)
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setSpacing(20)  # 增加卡片之间的间距
        stats_layout.setContentsMargins(15, 15, 15, 15)  # 增加边距
        
        # 统计卡片
        total_records = len(self.records)
        total_words = sum(len(record.get("important_words", {})) for record in self.records)
        total_grammar = sum(len(record.get("grammar_points", {})) for record in self.records)
        
        # 获取进度统计
        progress_stats = self.progress_manager.get_statistics_summary()
        wrong_questions_count = len(self.progress_manager.get_wrong_questions())
        
        stats_data = [
            ("📚", "学习记录", str(total_records), "#3498db"),
            ("💎", "重要单词", str(total_words), "#e74c3c"),
            ("🎯", "总测试次数", str(progress_stats.get("total_quizzes", 0)), "#2ecc71"),
            ("📊", "总体正确率", f"{progress_stats.get('overall_accuracy', 0)}%", "#f39c12"),
            ("❌", "错题待复习", str(wrong_questions_count), "#e67e22"),
            ("📈", "近期进步", f"{progress_stats.get('improvement_trend', 0):+.1f}%", "#9b59b6")
        ]
        
        # 使用3列布局，让卡片更紧凑
        for i, (icon, label, value, color) in enumerate(stats_data):
            card = self.create_stat_card(icon, label, value, color)
            row, col = divmod(i, 3)  # 改为3列布局
            stats_layout.addWidget(card, row, col)
        
        layout.addWidget(stats_frame)
        
        # 功能说明
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border: 2px solid #ffeaa7;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        info_title = QLabel("💡 测试类型说明")
        info_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #856404; margin-bottom: 10px;")
        
        info_text = QLabel("""
        ✏️ 单词默写题：根据释义写出正确的单词
        📚 语法选择题：选择正确的语法解释  
        💎 单词释义选择题：选择单词在语境中的正确含义
        🌐 翻译选择题：选择正确的中文翻译
        """)
        info_text.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #856404;
                line-height: 1.5;
                background: transparent;
            }
        """)
        
        info_layout.addWidget(info_title)
        info_layout.addWidget(info_text)
        layout.addWidget(info_frame)
        
        # 学习洞察和建议
        insights = self.progress_manager.get_learning_insights()
        if insights:
            insights_frame = QFrame()
            insights_frame.setStyleSheet("""
                QFrame {
                    background-color: #e8f5e8;
                    border: 2px solid #28a745;
                    border-radius: 10px;
                    padding: 20px;
                }
            """)
            insights_layout = QVBoxLayout(insights_frame)
            
            insights_title = QLabel("💡 个性化学习建议")
            insights_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #155724; margin-bottom: 10px;")
            
            insights_text = QLabel("\n".join(insights))
            insights_text.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #155724;
                    line-height: 1.5;
                    background: transparent;
                }
            """)
            insights_text.setWordWrap(True)
            
            insights_layout.addWidget(insights_title)
            insights_layout.addWidget(insights_text)
            layout.addWidget(insights_frame)
        
        # 开始按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        start_btn = QPushButton("🚀 开始新测试")
        start_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4facfe, stop:1 #00f2fe);
                color: white;
                border: none;
                padding: 15px 40px;
                border-radius: 25px;
                font-size: 18px;
                font-weight: bold;
                min-width: 200px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #43a3f5, stop:1 #00d4e6);
            }
        """)
        start_btn.clicked.connect(self.setup_new_quiz)
        
        button_layout.addWidget(start_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # 将内容widget设置到滚动区域
        scroll_area.setWidget(content_widget)
        
        # 将滚动区域添加到主布局
        main_layout.addWidget(scroll_area)
        
        parent_layout.addWidget(self.start_page)
    
    def create_stat_card(self, icon, label, value, color):
        """创建统计卡片"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 20px;
            }}
        """)
        card.setFixedHeight(130)  # 进一步增加高度到130px
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)  # 增加内边距
        layout.setSpacing(15)  # 增加组件间距
        
        # 图标标签 - 给更多空间
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 36px; 
                color: {color};
                min-width: 50px;
                text-align: center;
                padding: 5px;
            }}
        """)
        icon_label.setFixedWidth(60)  # 固定图标区域宽度
        icon_label.setAlignment(Qt.AlignCenter)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(8)  # 增加间距
        text_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标签文字 - 增大字体和高度
        label_widget = QLabel(label)
        label_widget.setStyleSheet("""
            QLabel {
                font-size: 15px; 
                color: #7f8c8d; 
                font-weight: bold;
                min-height: 25px;
                padding: 3px 0;
            }
        """)
        label_widget.setWordWrap(True)  # 支持换行
        label_widget.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        # 数值文字 - 增大字体
        value_widget = QLabel(value)
        value_widget.setStyleSheet(f"""
            QLabel {{
                font-size: 26px; 
                font-weight: bold; 
                color: {color};
                min-height: 35px;
                padding: 3px 0;
            }}
        """)
        value_widget.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        text_layout.addWidget(label_widget)
        text_layout.addWidget(value_widget)
        text_layout.addStretch()  # 添加弹性空间
        
        layout.addWidget(icon_label)
        layout.addLayout(text_layout, 1)  # 给文本布局更多空间
        
        return card
    
    def create_quiz_page(self, parent_layout):
        """创建答题页面"""
        self.quiz_page = QWidget()
        layout = QVBoxLayout(self.quiz_page)
        layout.setSpacing(20)
        
        # 顶部进度区域
        progress_frame = QFrame()
        progress_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 2px solid #e9ecef;
                padding: 15px;
            }
        """)
        progress_layout = QVBoxLayout(progress_frame)
        
        # 进度信息
        progress_info_layout = QHBoxLayout()
        
        self.question_counter_label = QLabel("题目 1 / 10")
        self.question_counter_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        
        self.score_label = QLabel("得分: 0")
        self.score_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #27ae60;
            }
        """)
        
        progress_info_layout.addWidget(self.question_counter_label)
        progress_info_layout.addStretch()
        progress_info_layout.addWidget(self.score_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                text-align: center;
                height: 25px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2ecc71);
                border-radius: 6px;
            }
        """)
        
        progress_layout.addLayout(progress_info_layout)
        progress_layout.addWidget(self.progress_bar)
        layout.addWidget(progress_frame)
        
        # 题目区域
        self.question_frame = QFrame()
        self.question_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 2px solid #e9ecef;
                padding: 25px;
            }
        """)
        
        self.question_layout = QVBoxLayout(self.question_frame)
        layout.addWidget(self.question_frame)
        
        # 答题区域
        self.answer_frame = QFrame()
        self.answer_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 2px solid #e9ecef;
                padding: 20px;
            }
        """)
        
        self.answer_layout = QVBoxLayout(self.answer_frame)
        layout.addWidget(self.answer_frame)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        
        # 退出按钮
        self.exit_btn = QPushButton("🚪 退出练习")
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.exit_btn.clicked.connect(self.exit_quiz)
        
        self.hint_btn = QPushButton("💡 提示")
        self.hint_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        self.hint_btn.clicked.connect(self.show_hint)
        
        self.submit_btn = QPushButton("提交答案")
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.submit_btn.clicked.connect(self.submit_answer)
        
        self.next_btn = QPushButton("下一题")
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.next_btn.clicked.connect(self.next_question)
        self.next_btn.setVisible(False)
        
        control_layout.addWidget(self.exit_btn)
        control_layout.addWidget(self.hint_btn)
        control_layout.addStretch()
        control_layout.addWidget(self.submit_btn)
        control_layout.addWidget(self.next_btn)
        
        layout.addLayout(control_layout)
        
        parent_layout.addWidget(self.quiz_page)
    
    def create_result_page(self, parent_layout):
        """创建结果页面"""
        self.result_page = QWidget()
        layout = QVBoxLayout(self.result_page)
        layout.setSpacing(30)
        
        # 结果标题
        self.result_title = QLabel("🎉 测试完成！")
        self.result_title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                text-align: center;
                margin: 20px;
            }
        """)
        self.result_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_title)
        
        # 结果统计
        self.result_stats = QFrame()
        self.result_stats.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 2px solid #e9ecef;
                padding: 25px;
            }
        """)
        
        self.result_layout = QVBoxLayout(self.result_stats)
        layout.addWidget(self.result_stats)
        
        # 按钮区域
        result_button_layout = QHBoxLayout()
        
        restart_btn = QPushButton("🔄 重新测试")
        restart_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        restart_btn.clicked.connect(self.setup_new_quiz)
        
        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        result_button_layout.addStretch()
        result_button_layout.addWidget(restart_btn)
        result_button_layout.addWidget(close_btn)
        result_button_layout.addStretch()
        
        layout.addLayout(result_button_layout)
        layout.addStretch()
        
        parent_layout.addWidget(self.result_page)
    
    def show_start_page(self):
        """显示开始页面"""
        self.start_page.setVisible(True)
        self.quiz_page.setVisible(False)
        self.result_page.setVisible(False)
    
    def show_quiz_page(self):
        """显示答题页面"""
        self.start_page.setVisible(False)
        self.quiz_page.setVisible(True)
        self.result_page.setVisible(False)
    
    def show_result_page(self):
        """显示结果页面"""
        self.start_page.setVisible(False)
        self.quiz_page.setVisible(False)
        self.result_page.setVisible(True)
    
    def setup_new_quiz(self):
        """设置新测试"""
        if not self.records:
            QMessageBox.warning(self, "提示", "没有可用的学习记录！")
            return
        
        # 显示设置对话框
        dialog = QuizSetupDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            settings = dialog.get_settings()
            if not settings["question_types"]:
                QMessageBox.warning(self, "提示", "请至少选择一种题目类型！")
                return
            
            self.generate_questions(settings)
    
    def generate_questions(self, settings):
        """生成题目"""
        # 检查是否是错题复习模式
        if settings.get("test_mode") == "review":
            # 错题复习模式 - 显示简单加载提示
            loading_dialog = LoadingDialog(self)
            loading_dialog.update_progress(50, "正在从错题库生成复习题目...")
            loading_dialog.show()
            
            try:
                review_questions = self.wrong_question_review.create_review_quiz(
                    question_type=None if not settings["question_types"] else None,  # 暂时不按类型筛选
                    count=settings["question_count"]
                )
                
                loading_dialog.update_progress(100, "错题复习题目生成完成！")
                QTimer.singleShot(500, loading_dialog.close)  # 延迟关闭以显示完成状态
                
                if not review_questions:
                    QMessageBox.information(self, "提示", 
                        "没有找到错题记录！\n请先完成一些标准测试，产生错题后再使用错题复习模式。")
                    return
                
                # 直接创建测试会话
                self.on_questions_generated(review_questions)
                return
                
            except Exception as e:
                loading_dialog.close()
                QMessageBox.critical(self, "错误", f"生成错题复习失败: {str(e)}")
                return
        
        # 标准模式 - 显示详细进度的加载对话框
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()
        
        # 启动生成线程
        self.generator_thread = QuizGeneratorThread(self.records, settings)
        self.generator_thread.questions_generated.connect(self.on_questions_generated)
        self.generator_thread.error_occurred.connect(self.on_generator_error)
        self.generator_thread.progress_updated.connect(self.on_progress_updated)
        
        # 连接取消按钮
        self.loading_dialog.cancel_btn.clicked.disconnect()  # 先断开默认连接
        self.loading_dialog.cancel_btn.clicked.connect(self.cancel_generation)
        
        self.generator_thread.start()
    
    def cancel_generation(self):
        """取消题目生成"""
        if hasattr(self, 'generator_thread') and self.generator_thread.isRunning():
            self.generator_thread.cancel()
            self.generator_thread.quit()
            self.generator_thread.wait(3000)  # 等待3秒
        
        if hasattr(self, 'loading_dialog'):
            self.loading_dialog.close()
        
        QMessageBox.information(self, "提示", "题目生成已取消")
    
    def on_questions_generated(self, questions):
        """题目生成完成"""
        # 关闭加载对话框
        if hasattr(self, 'loading_dialog'):
            self.loading_dialog.close()
        
        if not questions:
            QMessageBox.warning(self, "错误", "生成题目失败，请重试！")
            return
        
        # 创建测试会话
        self.quiz_session = QuizSession(questions)
        
        # 显示答题页面
        self.show_quiz_page()
        self.load_current_question()
        self.update_progress()
    
    def on_generator_error(self, error_message):
        """生成器错误"""
        # 关闭加载对话框
        if hasattr(self, 'loading_dialog'):
            self.loading_dialog.close()
            
        QMessageBox.critical(self, "错误", error_message)
    
    def on_progress_updated(self, progress, message):
        """进度更新"""
        if hasattr(self, 'loading_dialog') and self.loading_dialog.isVisible():
            self.loading_dialog.update_progress(progress, message)
    
    def load_current_question(self):
        """加载当前题目"""
        if not self.quiz_session:
            return
        
        self.current_question = self.quiz_session.get_current_question()
        if not self.current_question:
            self.finish_quiz()
            return
        
        # 清空题目区域
        for i in reversed(range(self.question_layout.count())):
            child = self.question_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 清空答案区域
        for i in reversed(range(self.answer_layout.count())):
            child = self.answer_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 显示题目
        question_type = self.current_question.get("question_type")
        question_text = self.current_question.get("question")
        
        # 题目标题
        type_icons = {
            "word_spelling": "✏️",
            "grammar_choice": "📚",
            "word_choice": "💎",
            "translation_choice": "🌐"
        }
        
        type_names = {
            "word_spelling": "单词默写题",
            "grammar_choice": "语法选择题",
            "word_choice": "单词释义选择题",
            "translation_choice": "翻译选择题"
        }
        
        question_type_label = QLabel(f"{type_icons.get(question_type, '❓')} {type_names.get(question_type, '未知题型')}")
        question_type_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #8e44ad;
                margin-bottom: 20px;
                padding: 12px 16px;
                background-color: #f8f9fa;
                border-radius: 8px;
                min-height: 50px;
            }
        """)
        
        self.question_layout.addWidget(question_type_label)
        
        # 题目内容区域 - 使用滚动区域处理长文本
        question_scroll_area = QScrollArea()
        question_scroll_area.setWidgetResizable(True)
        question_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        question_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        question_scroll_area.setFrameShape(QFrame.NoFrame)
        question_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid #3498db;
            }
            QScrollBar:vertical {
                background-color: #e9ecef;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #6c757d;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #495057;
            }
        """)
        question_scroll_area.setMaximumHeight(150)  # 限制最大高度
        
        # 题目内容widget
        question_content_widget = QWidget()
        question_content_layout = QVBoxLayout(question_content_widget)
        question_content_layout.setContentsMargins(15, 15, 15, 15)
        
        question_content_label = QLabel(question_text)
        question_content_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #2c3e50;
                line-height: 1.6;
                background-color: transparent;
            }
        """)
        question_content_label.setWordWrap(True)
        question_content_label.setTextFormat(Qt.RichText)
        
        question_content_layout.addWidget(question_content_label)
        question_content_layout.addStretch()
        
        question_scroll_area.setWidget(question_content_widget)
        self.question_layout.addWidget(question_scroll_area)
        
        # 根据题目类型创建答题界面
        if question_type == "word_spelling":
            self.create_spelling_answer_ui()
        else:
            self.create_choice_answer_ui()
        
        # 重置按钮状态
        self.submit_btn.setVisible(True)
        self.next_btn.setVisible(False)
        self.user_answer = None
    
    def create_spelling_answer_ui(self):
        """创建单词默写答题界面"""
        answer_label = QLabel("请输入单词:")
        answer_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #34495e;
                margin-bottom: 15px;
                padding: 10px;
                min-height: 30px;
            }
        """)
        
        self.spelling_input = QLineEdit()
        self.spelling_input.setStyleSheet("""
            QLineEdit {
                font-size: 18px;
                padding: 18px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
                min-height: 30px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.spelling_input.setPlaceholderText("在此输入单词...")
        
        # 提示信息
        hint = self.current_question.get("hint", "")
        if hint:
            hint_label = QLabel(f"💡 {hint}")
            hint_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #7f8c8d;
                    margin-top: 10px;
                    padding: 10px;
                    background-color: #ecf0f1;
                    border-radius: 5px;
                    min-height: 40px;
                }
            """)
            hint_label.setWordWrap(True)
            self.answer_layout.addWidget(hint_label)
        
        self.answer_layout.addWidget(answer_label)
        self.answer_layout.addWidget(self.spelling_input)
    
    def create_choice_answer_ui(self):
        """创建选择题答题界面"""
        options = self.current_question.get("options", [])
        if not options:
            return
        
        answer_label = QLabel("请选择正确答案:")
        answer_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #34495e;
                margin-bottom: 20px;
                padding: 10px;
                min-height: 20px;
            }
        """)
        self.answer_layout.addWidget(answer_label)
        
        # 创建选项滚动区域
        options_scroll_area = QScrollArea()
        options_scroll_area.setWidgetResizable(True)
        options_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        options_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        options_scroll_area.setFrameShape(QFrame.NoFrame)
        options_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #e9ecef;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #6c757d;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #495057;
            }
        """)
        options_scroll_area.setMaximumHeight(600)  # 限制选项区域最大高度，足以显示四个选项
        
        # 选项容器widget
        options_widget = QWidget()
        options_layout = QVBoxLayout(options_widget)
        options_layout.setContentsMargins(10, 10, 10, 10)
        options_layout.setSpacing(10)
        
        # 创建选项按钮组
        self.option_group = QButtonGroup()
        self.option_buttons = []
        
        for i, option in enumerate(options):
            # 选项容器框架
            option_frame = QFrame()
            option_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 2px solid #e9ecef;
                    border-radius: 8px;
                    padding: 8px;
                    min-height: 40px;
                }
                QFrame:hover {
                    border-color: #3498db;
                    background-color: #f8f9fa;
                }
            """)
            
            option_layout = QHBoxLayout(option_frame)
            option_layout.setContentsMargins(15, 15, 15, 15)
            
            option_btn = QRadioButton()
            option_btn.setStyleSheet("""
                QRadioButton {
                    font-size: 16px;
                    color: #2c3e50;
                    spacing: 15px;
                    padding: 5px;
                }
                QRadioButton::indicator {
                    width: 20px;
                    height: 20px;
                }
                QRadioButton::indicator:checked {
                    background-color: #3498db;
                    border: 3px solid #2980b9;
                    border-radius: 10px;
                }
                QRadioButton::indicator:unchecked {
                    background-color: white;
                    border: 2px solid #bdc3c7;
                    border-radius: 10px;
                }
            """)
            
            # 选项文本标签，支持长文本换行和滚动
            option_text_label = QLabel(f"{chr(65+i)}. {option}")
            option_text_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #2c3e50;
                    line-height: 1.5;
                    background-color: transparent;
                    padding: 8px;
                    min-height: 20px;
                }
            """)
            option_text_label.setWordWrap(True)
            option_text_label.setTextFormat(Qt.RichText)
            
            option_layout.addWidget(option_btn)
            option_layout.addWidget(option_text_label, 1)  # 给文本标签更多空间
            
            # 点击整个框架时也能选中选项
            def make_click_handler(btn):
                def handler(event):
                    btn.setChecked(True)
                return handler
            
            option_frame.mousePressEvent = make_click_handler(option_btn)
            
            self.option_group.addButton(option_btn, i)
            self.option_buttons.append(option_btn)
            options_layout.addWidget(option_frame)
        
        options_layout.addStretch()
        options_scroll_area.setWidget(options_widget)
        self.answer_layout.addWidget(options_scroll_area)
    
    def submit_answer(self):
        """提交答案"""
        if not self.quiz_session or not self.current_question:
            return
        
        # 获取用户答案
        question_type = self.current_question.get("question_type")
        
        if question_type == "word_spelling":
            user_answer = self.spelling_input.text().strip()
            if not user_answer:
                QMessageBox.warning(self, "提示", "请输入答案！")
                return
        else:
            checked_button = self.option_group.checkedButton()
            if not checked_button:
                QMessageBox.warning(self, "提示", "请选择一个答案！")
                return
            user_answer = self.option_group.id(checked_button)
        
        self.user_answer = user_answer
        
        # 提交答案
        is_correct = self.quiz_session.submit_answer(user_answer)
        
        # 显示答案反馈
        self.show_answer_feedback(is_correct)
        
        # 更新进度
        self.update_progress()
        
        # 切换按钮状态
        self.submit_btn.setVisible(False)
        self.next_btn.setVisible(True)
    
    def show_answer_feedback(self, is_correct):
        """显示答案反馈"""
        # 创建反馈滚动区域
        feedback_scroll_area = QScrollArea()
        feedback_scroll_area.setWidgetResizable(True)
        feedback_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        feedback_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        feedback_scroll_area.setFrameShape(QFrame.NoFrame)
        feedback_scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {'#d4edda' if is_correct else '#f8d7da'};
                border: 2px solid {'#28a745' if is_correct else '#dc3545'};
                border-radius: 8px;
                margin-top: 10px;
            }}
            QScrollBar:vertical {{
                background-color: #e9ecef;
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background-color: #6c757d;
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: #495057;
            }}
        """)
        feedback_scroll_area.setMaximumHeight(200)  # 限制反馈区域最大高度
        
        # 反馈内容widget
        feedback_widget = QWidget()
        feedback_layout = QVBoxLayout(feedback_widget)
        feedback_layout.setContentsMargins(15, 15, 15, 15)
        feedback_layout.setSpacing(10)
        
        # 结果图标和文字
        result_text = "✅ 回答正确！" if is_correct else "❌ 回答错误"
        result_label = QLabel(result_text)
        result_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {'#155724' if is_correct else '#721c24'};
                margin-bottom: 10px;
                background-color: transparent;
            }}
        """)
        
        # 正确答案
        correct_answer = self.current_question.get("correct_answer")
        question_type = self.current_question.get("question_type")
        
        if question_type == "word_spelling":
            correct_text = f"✓ 正确答案: {correct_answer}"
            user_text = f"✎ 您的答案: {self.user_answer}"
        else:
            options = self.current_question.get("options", [])
            correct_text = f"✓ 正确答案: {chr(65+correct_answer)}. {options[correct_answer] if correct_answer < len(options) else 'N/A'}"
            user_text = f"✎ 您的答案: {chr(65+self.user_answer)}. {options[self.user_answer] if self.user_answer < len(options) else 'N/A'}"
        
        correct_label = QLabel(correct_text)
        correct_label.setStyleSheet("font-size: 14px; margin: 5px 0; background-color: transparent;")
        correct_label.setWordWrap(True)
        correct_label.setTextFormat(Qt.RichText)
        
        if not is_correct:
            user_label = QLabel(user_text)
            user_label.setStyleSheet("font-size: 14px; margin: 5px 0; background-color: transparent;")
            user_label.setWordWrap(True)
            user_label.setTextFormat(Qt.RichText)
            feedback_layout.addWidget(user_label)
        
        feedback_layout.addWidget(result_label)
        feedback_layout.addWidget(correct_label)
        
        # 解释
        explanation = self.current_question.get("explanation", "")
        if explanation:
            explanation_label = QLabel(f"📝 解释: {explanation}")
            explanation_label.setStyleSheet("""
                QLabel {
                    font-size: 13px;
                    color: #6c757d;
                    margin-top: 10px;
                    background-color: rgba(255, 255, 255, 0.7);
                    padding: 10px;
                    border-radius: 5px;
                    line-height: 1.4;
                }
            """)
            explanation_label.setWordWrap(True)
            explanation_label.setTextFormat(Qt.RichText)
            feedback_layout.addWidget(explanation_label)
        
        # 复习提示（如果是复习题目）
        if self.current_question.get("is_review"):
            error_count = self.current_question.get("original_error_count", 1)
            review_hint = self.current_question.get("review_hint", f"这是你之前错过{error_count}次的题目")
            
            review_label = QLabel(f"🔄 {review_hint}")
            review_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #856404;
                    background-color: #fff3cd;
                    padding: 8px;
                    border-radius: 4px;
                    margin-top: 5px;
                }
            """)
            review_label.setWordWrap(True)
            feedback_layout.addWidget(review_label)
        
        feedback_layout.addStretch()
        feedback_scroll_area.setWidget(feedback_widget)
        
        # 添加到答案区域
        self.answer_layout.addWidget(feedback_scroll_area)
    
    def next_question(self):
        """下一题"""
        if not self.quiz_session:
            return
        
        if self.quiz_session.next_question():
            # 还有下一题
            self.load_current_question()
            self.update_progress()
        else:
            # 测试完成
            self.finish_quiz()
    
    def finish_quiz(self):
        """完成测试"""
        if self.quiz_session:
            self.quiz_session.finish_session()
            results = self.quiz_session.get_results()
            
            # 保存测试结果到进度管理器
            try:
                self.progress_manager.record_quiz_result(results)
                print("测试结果已保存到进度管理器")
            except Exception as e:
                print(f"保存测试结果失败: {e}")
            
            self.show_results(results)
        
        self.show_result_page()
    
    def show_results(self, results):
        """显示测试结果"""
        # 清空结果布局
        for i in reversed(range(self.result_layout.count())):
            child = self.result_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 总体结果
        accuracy = results["accuracy"]
        
        # 结果等级
        if accuracy >= 90:
            grade = "优秀"
            grade_color = "#27ae60"
            grade_icon = "🌟"
        elif accuracy >= 70:
            grade = "良好"
            grade_color = "#f39c12"
            grade_icon = "👍"
        elif accuracy >= 60:
            grade = "及格"
            grade_color = "#3498db"
            grade_icon = "👌"
        else:
            grade = "需要加强"
            grade_color = "#e74c3c"
            grade_icon = "💪"
        
        # 结果卡片
        result_cards_layout = QGridLayout()
        result_cards_layout.setSpacing(20)  # 增加卡片之间的间距
        result_cards_layout.setContentsMargins(10, 10, 10, 10)  # 增加边距
        
        cards_data = [
            ("📊", "总题数", str(results["total_questions"]), "#3498db"),
            ("✅", "答对", str(results["correct_answers"]), "#27ae60"),
            ("❌", "答错", str(results["wrong_answers"]), "#e74c3c"),
            ("🎯", "正确率", f"{accuracy}%", grade_color)
        ]
        
        # 使用2列布局，4个卡片正好2行2列
        for i, (icon, label, value, color) in enumerate(cards_data):
            card = self.create_stat_card(icon, label, value, color)
            row, col = divmod(i, 2)
            result_cards_layout.addWidget(card, row, col)
        
        # 等级显示
        grade_label = QLabel(f"{grade_icon} 测试等级: {grade}")
        grade_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {grade_color};
                text-align: center;
                padding: 25px;
                background-color: rgba({int(grade_color[1:3], 16)}, {int(grade_color[3:5], 16)}, {int(grade_color[5:7], 16)}, 0.1);
                border-radius: 12px;
                margin: 20px 0;
                min-height: 60px;
                border: 2px solid rgba({int(grade_color[1:3], 16)}, {int(grade_color[3:5], 16)}, {int(grade_color[5:7], 16)}, 0.3);
            }}
        """)
        grade_label.setAlignment(Qt.AlignCenter)
        
        self.result_layout.addLayout(result_cards_layout)
        self.result_layout.addWidget(grade_label)
        
        # 用时信息
        if results.get("duration_seconds"):
            duration = int(results["duration_seconds"])
            minutes = duration // 60
            seconds = duration % 60
            time_text = f"⏱️ 用时: {minutes}分{seconds}秒"
            
            time_label = QLabel(time_text)
            time_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #7f8c8d;
                    text-align: center;
                    margin: 15px;
                    padding: 10px;
                    min-height: 40px;
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    border: 1px solid #e9ecef;
                }
            """)
            time_label.setAlignment(Qt.AlignCenter)
            self.result_layout.addWidget(time_label)
    
    def update_progress(self):
        """更新进度显示"""
        if not self.quiz_session:
            return
        
        total = len(self.quiz_session.questions)
        current = self.quiz_session.current_question_index + 1
        score = self.quiz_session.score
        
        # 更新计数器
        self.question_counter_label.setText(f"题目 {current} / {total}")
        
        # 更新得分
        self.score_label.setText(f"得分: {score}")
        
        # 更新进度条
        progress = int((self.quiz_session.current_question_index / total) * 100)
        self.progress_bar.setValue(progress)
        self.progress_bar.setFormat(f"{progress}%")
    
    def show_hint(self):
        """显示提示"""
        if not self.current_question:
            return
        
        question_type = self.current_question.get("question_type")
        
        if question_type == "word_spelling":
            hint = self.current_question.get("hint", "暂无提示")
            QMessageBox.information(self, "💡 提示", hint)
        else:
            # 对于选择题，可以排除一个错误选项
            explanation = self.current_question.get("explanation", "")
            context = self.current_question.get("context_sentence", "")
            
            hint_text = ""
            if context:
                hint_text += f"上下文: {context}\n\n"
            if explanation:
                hint_text += f"提示: 想想相关的语法规则或词汇含义"
            
            if not hint_text:
                hint_text = "仔细分析题目，回忆相关的知识点"
            
            QMessageBox.information(self, "💡 提示", hint_text)
    
    def exit_quiz(self):
        """退出测试练习"""
        try:
            # 显示确认对话框
            reply = QMessageBox.question(
                self,
                "退出练习",
                "确定要退出当前的测试练习吗？\n当前进度将会丢失。",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 停止当前测试会话
                if self.quiz_session:
                    # 如果有未完成的测试，可以选择保存部分进度
                    if self.quiz_session.current_question_index > 0:
                        try:
                            # 保存部分完成的结果
                            partial_results = self.quiz_session.get_results()
                            if partial_results and partial_results.get("correct_answers", 0) > 0:
                                self.progress_manager.record_quiz_result(partial_results)
                                print(f"已保存部分测试进度: {partial_results.get('correct_answers', 0)}道正确答案")
                        except Exception as e:
                            print(f"保存部分进度时出错: {e}")
                    
                    # 清理测试会话
                    self.quiz_session = None
                
                # 清理当前状态
                self.current_question = None
                self.user_answer = None
                
                # 停止题目生成线程（如果正在运行）
                if hasattr(self, 'generator_thread') and self.generator_thread and self.generator_thread.isRunning():
                    self.generator_thread.cancel()
                    self.generator_thread.quit()
                    self.generator_thread.wait(3000)
                
                # 关闭加载对话框（如果存在）
                if hasattr(self, 'loading_dialog') and self.loading_dialog:
                    self.loading_dialog.close()
                
                # 返回到开始页面
                self.show_start_page()
                
                print("已退出测试练习")
                
        except Exception as e:
            print(f"退出测试时出错: {e}")
            # 即使出错也尝试返回开始页面
            self.show_start_page()