from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QListWidget, QListWidgetItem,
                             QSplitter, QLineEdit, QScrollArea, QTabWidget, QComboBox,
                             QTextEdit, QMessageBox, QDesktopWidget)
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal
from app.managers import NotesManager, rag_manager
from app.utils import FuzzySearchEngine

class NotesWindow(QMainWindow):
    # 添加返回主程序的信号
    return_to_main = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.records = []
        self.filtered_records = []
        self.search_scores = {}  # 存储搜索分数
        self.search_timer = QTimer()  # 防抖动计时器
        self.search_timer.timeout.connect(self.perform_search)
        self.search_timer.setSingleShot(True)
        self.init_ui()
        self.load_records()
        
    def init_ui(self):
        self.setWindowTitle("英语学习笔记本 📚")
        
        # 自适应窗口大小 - 根据屏幕尺寸调整
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        screen_width = screen.width()
        screen_height = screen.height()
        
        # 计算适合的窗口尺寸（占屏帇95%）
        window_width = min(1600, int(screen_width * 0.95))
        window_height = min(1100, int(screen_height * 0.95))
        
        # 居中显示
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.setGeometry(x, y, window_width, window_height)
        
        # 设置整体样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
        """)
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局 - 使用更大的自适应间距
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)  # 增大边距
        main_layout.setSpacing(20)  # 增大间距
        
        # 标题区域 - 自适应高度
        self.create_header(main_layout)
        
        # 搜索和筛选区域 - 自适应高度
        self.create_search_area(main_layout)
        
        # 主要内容区域 - 分割器 (占用最大空间)
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #dee2e6;
                width: 4px;
            }
            QSplitter::handle:hover {
                background-color: #007bff;
            }
        """)
        
        # 左侧：句子列表
        self.create_sentences_list(content_splitter)
        
        # 右侧：详细信息
        self.create_detail_area(content_splitter)
        
        # 使用比例分割而非固定大小，更加自适应
        content_splitter.setSizes([600, 900])  # 调整比例：左侧40%，右侧60%
        content_splitter.setStretchFactor(0, 2)  # 左侧权重2
        content_splitter.setStretchFactor(1, 3)  # 右侧权重3，更多空间给详情区
        main_layout.addWidget(content_splitter, 1)  # 设置stretch为1，占用最大空间
        
        # 底部统计信息 - 自适应高度
        self.create_statistics(main_layout)
        
    def create_header(self, layout):
        """创建标题区域 - 自适应高度"""
        header_frame = QFrame()
        # 移除最大高度限制，让内容自适应
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 12px;
                padding: 20px 25px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setSpacing(25)  # 增大间距
        header_layout.setContentsMargins(15, 15, 15, 15)  # 增大内边距
        
        title_label = QLabel("📚 英语学习笔记本")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 22px;
                font-weight: bold;
                background: transparent;
                padding: 5px;
            }
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # 返回主程序按钮
        back_btn = QPushButton("⬅️ 返回翻译助手")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(52, 152, 219, 0.9);
                color: white;
                border: 2px solid rgba(52, 152, 219, 0.7);
                padding: 15px 25px;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                min-width: 140px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: rgba(52, 152, 219, 1.0);
                border: 2px solid rgba(52, 152, 219, 0.9);
            }
        """)
        back_btn.clicked.connect(self.return_to_main_program)
        header_layout.addWidget(back_btn)
        
        # 题库练习按钮
        quiz_btn = QPushButton("🎯 题库练习")
        quiz_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 193, 7, 0.9);
                color: white;
                border: 2px solid rgba(255, 193, 7, 0.7);
                padding: 15px 25px;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                min-width: 120px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: rgba(255, 193, 7, 1.0);
                border: 2px solid rgba(255, 193, 7, 0.9);
            }
        """)
        quiz_btn.clicked.connect(self.open_quiz_window)
        header_layout.addWidget(quiz_btn)
        
        # 导出按钮 - 增大尺寸
        export_btn = QPushButton("📤 导出笔记")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.3);
                padding: 15px 25px;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                min-width: 120px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
        """)
        export_btn.clicked.connect(self.export_notes)
        header_layout.addWidget(export_btn)
        
        layout.addWidget(header_frame)
    
    def create_search_area(self, layout):
        """创建搜索和筛选区域 - 自适应高度"""
        search_frame = QFrame()
        # 移除最大高度限制，让内容自适应
        search_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px 20px;
                border: 1px solid #e9ecef;
            }
        """)
        
        search_layout = QHBoxLayout(search_frame)
        search_layout.setSpacing(25)  # 增加间距
        search_layout.setContentsMargins(10, 10, 10, 10)
        
        # 搜索框
        search_label = QLabel("🔍 搜索:")
        search_label.setStyleSheet("font-weight: bold; color: #495057; font-size: 16px; padding: 8px; min-width: 60px;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🤖 智能搜索：句子、单词、翻译、语法解释（支持模糊匹配）...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 15px 18px;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                font-size: 16px;
                min-height: 30px;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
        """)
        self.search_input.textChanged.connect(self.on_search_text_changed)  # 使用防抖动搜索
        
        # 日期筛选
        date_label = QLabel("📅 日期:")
        date_label.setStyleSheet("font-weight: bold; color: #495057; font-size: 16px; padding: 8px; min-width: 60px;")
        
        self.date_filter = QComboBox()
        self.date_filter.setStyleSheet("""
            QComboBox {
                padding: 15px 18px;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                font-size: 16px;
                min-width: 160px;
                min-height: 30px;
            }
            QComboBox:focus {
                border-color: #007bff;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
        """)
        self.date_filter.currentTextChanged.connect(self.on_search_text_changed)  # 使用防抖动搜索
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 2)  # 给搜索框更多空间
        search_layout.addWidget(date_label)
        search_layout.addWidget(self.date_filter, 1)
        
        layout.addWidget(search_frame)
    
    def create_sentences_list(self, splitter):
        """创建学习内容列表（包含句子和单词两个标签页）"""
        list_frame = QFrame()
        list_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e9ecef;
            }
        """)
        
        list_layout = QVBoxLayout(list_frame)
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: white;
                top: -1px;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                color: #495057;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
                min-height: 25px;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #007bff;
                border-bottom: 2px solid #007bff;
            }
            QTabBar::tab:hover {
                background-color: #e9ecef;
            }
        """)
        
        # 句子标签页
        sentences_widget = QWidget()
        sentences_layout = QVBoxLayout(sentences_widget)
        sentences_layout.setContentsMargins(0, 8, 0, 0)  # 适当的上边距
        
        # 句子列表
        self.sentences_list = QListWidget()
        self.sentences_list.setStyleSheet("""
            QListWidget {
                border: none;
                outline: none;
                background-color: white;
            }
            QListWidget::item {
                padding: 18px;
                border-bottom: 1px solid #f1f3f4;
                background-color: white;
                min-height: 70px;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                border-left: 4px solid #2196f3;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        self.sentences_list.itemClicked.connect(self.show_record_detail)
        sentences_layout.addWidget(self.sentences_list)
        
        # 单词标签页
        words_widget = QWidget()
        words_layout = QVBoxLayout(words_widget)
        words_layout.setContentsMargins(0, 8, 0, 0)  # 适当的上边距
        
        # 单词列表
        self.words_list = QListWidget()
        self.words_list.setStyleSheet("""
            QListWidget {
                border: none;
                outline: none;
                background-color: white;
            }
            QListWidget::item {
                padding: 15px 18px;
                border-bottom: 1px solid #f1f3f4;
                background-color: white;
                min-height: 60px;
            }
            QListWidget::item:selected {
                background-color: #f3e5f5;
                border-left: 4px solid #9c27b0;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
        """)
        self.words_list.itemClicked.connect(self.show_word_detail)
        words_layout.addWidget(self.words_list)
        
        # 添加标签页
        self.tab_widget.addTab(sentences_widget, "📝 句子")
        self.tab_widget.addTab(words_widget, "💎 单词")
        
        list_layout.addWidget(self.tab_widget)
        splitter.addWidget(list_frame)
    
    def create_detail_area(self, splitter):
        """创建详细信息区域"""
        detail_frame = QFrame()
        detail_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e9ecef;
            }
        """)
        
        detail_layout = QVBoxLayout(detail_frame)
        detail_layout.setContentsMargins(0, 0, 0, 0)
        
        # 详情标题 - 优化样式
        detail_title = QLabel("📖 详细信息")
        detail_title.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                padding: 15px 20px;
                font-size: 16px;
                font-weight: bold;
                color: #495057;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border-bottom: 2px solid #e9ecef;
            }
        """)
        detail_layout.addWidget(detail_title)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
            QScrollBar:vertical {
                background-color: #f1f3f4;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #c1c1c1;
                border-radius: 6px;
                min-height: 25px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a8a8a8;
            }
        """)
        
        # 详情内容
        self.detail_content = QWidget()
        self.detail_layout = QVBoxLayout(self.detail_content)
        self.detail_layout.setContentsMargins(20, 20, 20, 20)  # 增大内边距
        self.detail_layout.setSpacing(20)  # 增大间距，给内容更多呼吸空间
        
        # 初始提示
        self.show_empty_detail()
        
        scroll_area.setWidget(self.detail_content)
        detail_layout.addWidget(scroll_area)
        
        splitter.addWidget(detail_frame)
    
    def create_statistics(self, layout):
        """创建统计信息"""
        stats_frame = QFrame()
        # 移除最大高度限制，让内容自适应
        stats_frame.setMinimumHeight(40)  # 只设置最小高度
        stats_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #4facfe, stop:1 #00f2fe);
                border-radius: 8px;
                padding: 12px 20px;
            }
        """)
        
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(10, 8, 10, 8)  # 增加内边距
        
        self.stats_label = QLabel("📊 学习统计: 加载中...")
        self.stats_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 15px;
                font-weight: bold;
                background: transparent;
                padding: 2px 0;
            }
        """)
        
        stats_layout.addWidget(self.stats_label)
        
        layout.addWidget(stats_frame)
    
    def resizeEvent(self, event):
        """窗口大小改变时重新计算列表项高度"""
        super().resizeEvent(event)
        # 延迟更新以确保窗口完全调整大小后再重新计算
        QTimer.singleShot(100, self.refresh_list_heights)
    
    def refresh_list_heights(self):
        """刷新列表项高度（只刷新单词列表，句子列表使用固定高度）"""
        try:
            # 只刷新单词列表，因为句子列表现在使用固定高度
            for i in range(self.words_list.count()):
                item = self.words_list.item(i)
                if item:
                    widget = self.words_list.itemWidget(item)
                    if widget:
                        calculated_height = self.calculate_item_height(widget, self.words_list)
                        item.setSizeHint(QSize(-1, calculated_height))
        except Exception as e:
            print(f"刷新列表高度时出错: {e}")
    
    def refresh_sentences_heights(self):
        """句子列表使用固定高度，不需要刷新"""
        pass  # 句子列表现在使用固定高度120px
    
    def refresh_words_heights(self):
        """专门刷新单词列表的高度"""
        try:
            for i in range(self.words_list.count()):
                item = self.words_list.item(i)
                if item:
                    widget = self.words_list.itemWidget(item)
                    if widget:
                        calculated_height = self.calculate_item_height(widget, self.words_list)
                        item.setSizeHint(QSize(-1, calculated_height))
        except Exception as e:
            print(f"刷新单词列表高度时出错: {e}")
    
    def show_empty_detail(self):
        """显示空详情提示"""
        # 清空之前的内容
        for i in reversed(range(self.detail_layout.count())):
            layout_item = self.detail_layout.itemAt(i)
            if layout_item:
                widget = layout_item.widget()
                if widget:
                    widget.setParent(None)
                else:
                    self.detail_layout.removeItem(layout_item)
        
        empty_label = QLabel("👈 请从左侧选择一条学习记录来查看详细信息")
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 18px;
                padding: 60px;
                background-color: #f8f9fa;
                border-radius: 12px;
                border: 3px dashed #dee2e6;
                margin: 20px;
            }
        """)
        
        self.detail_layout.addWidget(empty_label)
        self.detail_layout.addStretch()
    
    def load_records(self):
        """加载所有记录"""
        self.records = NotesManager.load_all_records()
        self.filtered_records = self.records.copy()
        
        # 更新日期筛选选项
        dates = ["全部日期"] + list(set(record.get("date", "") for record in self.records))
        dates.sort(reverse=True)
        self.date_filter.clear()
        self.date_filter.addItems(dates)
        
        # 更新列表
        self.update_sentences_list()
        self.update_words_list()
        self.update_statistics()
    
    def calculate_text_height(self, label, width):
        """计算文本标签的准确高度（支持中英文混合和长文本）"""
        try:
            font_metrics = label.fontMetrics()
            text = label.text()
            
            if not text.strip():
                return font_metrics.height()
            
            # 为文本预留更多宽度以避免不必要的换行
            text_width = max(width - 50, 200)
            
            # 计算文本在给定宽度下需要的高度
            text_rect = font_metrics.boundingRect(0, 0, text_width, 10000, 
                                                Qt.TextWordWrap | Qt.AlignLeft, text)
            
            # 为多行文本加上额外的行间距
            line_count = max(text_rect.height() // font_metrics.height(), 1)
            line_spacing = 4 if line_count > 1 else 0
            
            return text_rect.height() + line_spacing + 15  # 加上内边距
            
        except Exception as e:
            print(f"计算文本高度时出错: {e}")
            return 30  # 返回默认高度
    
    def calculate_item_height(self, item_widget, list_widget):
        """计算列表项的准确高度"""
        try:
            # 获取列表宽度，如果列表还未显示则使用默认值
            if list_widget.isVisible() and list_widget.viewport().width() > 0:
                list_width = list_widget.viewport().width()
            else:
                list_width = 400  # 默认宽度
            
            # 为item预留一些宽度（滚动条、边距等）
            available_width = max(list_width - 60, 280)
            
            total_height = 0
            layout = item_widget.layout()
            
            if layout:
                # 计算所有子widget的高度
                for i in range(layout.count()):
                    child = layout.itemAt(i)
                    if child and child.widget():
                        widget = child.widget()
                        if isinstance(widget, QLabel):
                            # 确保label有文本再计算
                            if widget.text().strip():
                                text_height = self.calculate_text_height(widget, available_width)
                                total_height += text_height
                            else:
                                total_height += 20  # 空文本的默认高度
                        else:
                            hint_height = widget.sizeHint().height()
                            total_height += hint_height if hint_height > 0 else 20
                
                # 加上layout的间距和边距
                if layout.count() > 1:
                    total_height += layout.spacing() * (layout.count() - 1)
                
                margins = layout.contentsMargins()
                total_height += margins.top() + margins.bottom()
            
            # 确保最小高度和合理的最大高度
            return max(min(total_height + 30, 300), 80)
            
        except Exception as e:
            print(f"计算item高度时出错: {e}")
            return 100  # 返回默认高度
    
    def update_words_list(self):
        """更新单词列表（考虑句子的学习次数来统计单词频次，支持搜索高亮）"""
        self.words_list.clear()
        
        search_query = self.search_input.text().strip()
        
        # 收集所有单词及其出现次数和含义
        word_stats = {}
        for record in self.filtered_records:
            words = record.get("important_words", {})
            learn_count = record.get("learn_count", 1)  # 获取该句子的学习次数
            
            for word, meaning in words.items():
                word_lower = word.lower()
                if word_lower not in word_stats:
                    word_stats[word_lower] = {
                        "word": word,
                        "meaning": meaning,
                        "count": 0,
                        "sentences": []
                    }
                # 根据句子的学习次数来累计单词出现次数
                word_stats[word_lower]["count"] += learn_count
                word_stats[word_lower]["sentences"].append(record)
        
        # 按出现频率排序
        sorted_words = sorted(word_stats.values(), key=lambda x: x["count"], reverse=True)
        
        for word_data in sorted_words:
            item = QListWidgetItem()
            
            # 创建自定义widget
            item_widget = QWidget()
            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(3)
            
            # 单词和频次（现在显示累计学习次数，带高亮）
            word_text = f"{word_data['word']} ({word_data['count']}次)"
            if search_query:
                word_text = FuzzySearchEngine.highlight_matches(word_text, search_query)
            
            word_label = QLabel(word_text)
            word_label.setStyleSheet("""
                QLabel {
                    font-size: 15px;
                    font-weight: bold;
                    color: #4a148c;
                }
            """)
            word_label.setTextFormat(Qt.RichText)  # 支持HTML高亮
            
            # 为单词标签添加点击事件
            word_label.mousePressEvent = lambda event, item=item: self.on_word_label_clicked(item, event)
            
            # 含义（设置合理的高度限制，带高亮）
            meaning_text = word_data['meaning']
            if search_query:
                meaning_text = FuzzySearchEngine.highlight_matches(meaning_text, search_query)
            
            meaning_label = QLabel(meaning_text)
            meaning_label.setStyleSheet("""
                QLabel {
                    font-size: 13px;
                    color: #666;
                    margin-top: 2px;
                }
            """)
            meaning_label.setWordWrap(True)
            meaning_label.setMaximumHeight(60)  # 限制含义标签的最大高度
            meaning_label.setTextFormat(Qt.RichText)  # 支持HTML高亮
            
            # 为含义标签添加点击事件
            meaning_label.mousePressEvent = lambda event, item=item: self.on_word_label_clicked(item, event)
            
            item_layout.addWidget(word_label)
            item_layout.addWidget(meaning_label)
            
            # 为整个单词item widget添加点击事件，以便点击空白区域也能显示详情
            item_widget.mousePressEvent = lambda event, item=item: self.on_word_label_clicked(item, event)
            
            # 为单词列表设置合理的最大高度，但允许适当调整
            calculated_height = min(self.calculate_item_height(item_widget, self.words_list), 100)
            item.setSizeHint(QSize(-1, calculated_height))
            
            self.words_list.addItem(item)
            self.words_list.setItemWidget(item, item_widget)
            
            # 存储单词数据
            item.setData(Qt.UserRole, word_data)
        
        # 延迟刷新高度以确保所有item都已正确创建
        QTimer.singleShot(50, self.refresh_words_heights)
    
    def on_search_text_changed(self):
        """搜索文本变化时的处理（防抖动）"""
        # 停止之前的计时器
        self.search_timer.stop()
        # 设置300毫秒的延迟，减少频繁搜索
        self.search_timer.start(300)
    
    def perform_search(self):
        """执行实际的搜索操作"""
        self.filter_records_with_fuzzy_search()
    
    def filter_records_with_fuzzy_search(self):
        """使用模糊搜索算法进行智能筛选"""
        search_text = self.search_input.text().strip()
        date_filter = self.date_filter.currentText()
        
        self.filtered_records = []
        self.search_scores = {}
        
        # 如果没有搜索内容，则只进行日期筛选
        if not search_text:
            for record in self.records:
                if date_filter == "全部日期" or record.get("date", "") == date_filter:
                    self.filtered_records.append(record)
                    self.search_scores[record.get("id", 0)] = 1.0
        else:
            # 使用模糊搜索算法
            scored_records = []
            
            for record in self.records:
                # 日期筛选
                if date_filter != "全部日期" and record.get("date", "") != date_filter:
                    continue
                
                # 计算搜索分数
                score = FuzzySearchEngine.search_in_record(search_text, record)
                
                # 只保留有一定匹配度的结果
                if score > 0.1:  # 设置一个最低阈值
                    scored_records.append((record, score))
                    self.search_scores[record.get("id", 0)] = score
            
            # 按照分数排序（由高到低）
            scored_records.sort(key=lambda x: x[1], reverse=True)
            self.filtered_records = [record for record, score in scored_records]
        
        # 更新显示
        self.update_sentences_list()
        self.update_words_list()
        self.update_statistics()
    
    def show_word_detail(self, item):
        """显示单词详情"""
        word_data = item.data(Qt.UserRole)
        if not word_data:
            return
        
        # 清空之前的内容
        for i in reversed(range(self.detail_layout.count())):
            layout_item = self.detail_layout.itemAt(i)
            if layout_item:
                widget = layout_item.widget()
                if widget:
                    widget.setParent(None)
                else:
                    self.detail_layout.removeItem(layout_item)
        
        # 单词信息标题
        word_header_frame = QFrame()
        word_header_frame.setStyleSheet("""
            QFrame {
                background-color: #f3e5f5;
                border-left: 4px solid #9c27b0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        word_header_layout = QVBoxLayout(word_header_frame)
        
        word_title = QLabel(f"💎 单词: {word_data['word']}")
        word_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #4a148c; margin-bottom: 5px;")
        
        word_meaning = QLabel(f"📖 含义: {word_data['meaning']}")
        word_meaning.setStyleSheet("font-size: 16px; color: #666; margin-bottom: 5px;")
        word_meaning.setWordWrap(True)
        
        word_count = QLabel(f"📊 出现次数: {word_data['count']} 次")
        word_count.setStyleSheet("font-size: 14px; color: #888;")
        
        word_header_layout.addWidget(word_title)
        word_header_layout.addWidget(word_meaning)
        word_header_layout.addWidget(word_count)
        self.detail_layout.addWidget(word_header_frame)
        
        # 包含该单词的句子列表
        sentences_frame = QFrame()
        sentences_frame.setStyleSheet("""
            QFrame {
                background-color: #fff3e0;
                border-left: 4px solid #ff9800;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        sentences_layout = QVBoxLayout(sentences_frame)
        
        sentences_title = QLabel(f"📝 包含该单词的句子 ({len(word_data['sentences'])} 条)")
        sentences_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ef6c00; margin-bottom: 10px;")
        sentences_layout.addWidget(sentences_title)
        
        # 句子容器
        sentences_container = QFrame()
        sentences_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #ffcc02;
                padding: 10px;
            }
        """)
        sentences_container_layout = QVBoxLayout(sentences_container)
        
        for i, record in enumerate(word_data['sentences'][:10], 1):  # 最多显示10条
            sentence_item = QFrame()
            sentence_item.setStyleSheet("""
                QFrame {
                    background-color: #fafafa;
                    border-radius: 8px;
                    padding: 12px;
                    margin-bottom: 8px;
                    border-left: 3px solid #ffb300;
                }
            """)
            sentence_item_layout = QVBoxLayout(sentence_item)
            sentence_item_layout.setSpacing(8)
            
            # 句子编号、时间和学习次数
            learn_count = record.get('learn_count', 1)
            header_info = f"📅 记录 {i} - {record.get('timestamp', '')}"
            if learn_count > 1:
                header_info += f" (学习{learn_count}次)"
            
            header_label = QLabel(header_info)
            header_label.setStyleSheet("font-size: 12px; color: #888; font-weight: bold;")
            
            # 原文
            original_label = QLabel(f"原文: {record.get('original_text', '')}")
            original_label.setStyleSheet("font-size: 14px; color: #333; font-weight: bold;")
            original_label.setWordWrap(True)
            
            # 翻译
            translation_label = QLabel(f"翻译: {record.get('translation', '')}")
            translation_label.setStyleSheet("font-size: 13px; color: #666;")
            translation_label.setWordWrap(True)
            
            sentence_item_layout.addWidget(header_label)
            sentence_item_layout.addWidget(original_label)
            sentence_item_layout.addWidget(translation_label)
            
            sentences_container_layout.addWidget(sentence_item)
        
        if len(word_data['sentences']) > 10:
            more_label = QLabel(f"... 还有 {len(word_data['sentences']) - 10} 条记录")
            more_label.setStyleSheet("font-size: 12px; color: #888; text-align: center; padding: 10px;")
            more_label.setAlignment(Qt.AlignCenter)
            sentences_container_layout.addWidget(more_label)
        
        sentences_layout.addWidget(sentences_container)
        self.detail_layout.addWidget(sentences_frame)
        
        self.detail_layout.addStretch()
    
    def update_sentences_list(self):
        """更新句子列表（显示学习次数信息和搜索匹配度，长句子使用滚动条）"""
        self.sentences_list.clear()
        
        search_query = self.search_input.text().strip()
        
        for record in self.filtered_records:
            item = QListWidgetItem()
            
            # 创建主容器widget
            item_widget = QWidget()
            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(0)
            
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
                    background-color: #f0f0f0;
                    width: 8px;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical {
                    background-color: #c0c0c0;
                    border-radius: 4px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #a0a0a0;
                }
            """)
            
            # 创建内容widget
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setContentsMargins(12, 12, 12, 12)  # 增加内边距
            content_layout.setSpacing(8)  # 增加组件间距
            
            # 获取搜索匹配度（如果有）
            record_id = record.get("id", 0)
            match_score = self.search_scores.get(record_id, 0.0)
            
            # 原文（带高亮）
            original_text = record.get("original_text", "")
            if search_query:
                original_text = FuzzySearchEngine.highlight_matches(original_text, search_query)
            
            original_label = QLabel(original_text)
            original_label.setStyleSheet("""
                QLabel {
                    font-size: 15px;
                    font-weight: bold;
                    color: #212529;
                    background-color: transparent;
                    line-height: 1.4;
                    padding: 5px 0;
                }
            """)
            original_label.setWordWrap(True)
            # 允许HTML显示用于高亮
            original_label.setTextFormat(Qt.RichText)
            
            # 为原文标签添加点击事件
            original_label.mousePressEvent = lambda event, item=item: self.on_label_clicked(item, event)
            
            # 翻译（带高亮）
            translation_text = record.get("translation", "")
            if search_query:
                translation_text = FuzzySearchEngine.highlight_matches(translation_text, search_query)
            
            translation_label = QLabel(translation_text)
            translation_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #6c757d;
                    margin-top: 3px;
                    background-color: transparent;
                    line-height: 1.4;
                    padding: 5px 0;
                }
            """)
            translation_label.setWordWrap(True)
            translation_label.setTextFormat(Qt.RichText)
            
            # 为翻译标签添加点击事件
            translation_label.mousePressEvent = lambda event, item=item: self.on_label_clicked(item, event)
            
            # 时间和学习次数信息
            learn_count = record.get("learn_count", 1)
            time_info = f"🕐 {record.get('timestamp', '')}"
            if learn_count > 1:
                time_info += f" • 📚 已学习 {learn_count} 次"
            
            # 如果有搜索匹配度，显示它
            if match_score > 0 and search_query:
                match_percentage = int(match_score * 100)
                time_info += f" • 🎯 匹配度: {match_percentage}%"
            
            # 创建底部信息区域的水平布局
            bottom_info_layout = QHBoxLayout()
            
            time_label = QLabel(time_info)
            time_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #868e96;
                    margin-top: 5px;
                    background-color: transparent;
                    padding: 3px 0;
                }
            """)
            
            # 为时间标签添加点击事件
            time_label.mousePressEvent = lambda event, item=item: self.on_label_clicked(item, event)
            
            # 创建删除按钮
            delete_btn = QPushButton("🗑️ 删除")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: bold;
                    min-width: 50px;
                    max-height: 24px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
                QPushButton:pressed {
                    background-color: #a71e2a;
                }
            """)
            delete_btn.clicked.connect(lambda: self.delete_record_with_confirmation(record.get("id")))
            
            # 添加到水平布局
            bottom_info_layout.addWidget(time_label)
            bottom_info_layout.addStretch()  # 添加弹性空间，把删除按钮推到右边
            bottom_info_layout.addWidget(delete_btn)
            
            content_layout.addWidget(original_label)
            content_layout.addWidget(translation_label)
            content_layout.addLayout(bottom_info_layout)
            
            # 为整个内容widget添加点击事件，以便点击空白区域也能显示详情
            content_widget.mousePressEvent = lambda event, item=item: self.on_label_clicked(item, event)
            
            # 设置滚动区域的内容
            scroll_area.setWidget(content_widget)
            item_layout.addWidget(scroll_area)
            
            # 增加列表项高度，让一般句子能完整显示，减少滚动条需求
            item_height = 180  # 从120增加到180，约50%的提升
            item.setSizeHint(QSize(-1, item_height))
            
            self.sentences_list.addItem(item)
            self.sentences_list.setItemWidget(item, item_widget)
            
            # 存储记录数据
            item.setData(Qt.UserRole, record)
    
    def filter_records(self):
        """筛选记录（兼容旧版本，调用新的模糊搜索）"""
        self.filter_records_with_fuzzy_search()
    
    def on_label_clicked(self, item, event):
        """处理标签点击事件，显示记录详情"""
        if event.button() == Qt.LeftButton:  # 只处理左键点击
            self.show_record_detail(item)
    
    def on_word_label_clicked(self, item, event):
        """处理单词标签点击事件，显示单词详情"""
        if event.button() == Qt.LeftButton:  # 只处理左键点击
            self.show_word_detail(item)
    
    def show_record_detail(self, item):
        """显示记录详情"""
        record = item.data(Qt.UserRole)
        if not record:
            return
        
        # 清空之前的内容
        for i in reversed(range(self.detail_layout.count())):
            layout_item = self.detail_layout.itemAt(i)
            if layout_item:
                widget = layout_item.widget()
                if widget:
                    widget.setParent(None)
                else:
                    self.detail_layout.removeItem(layout_item)
        
        # 时间和学习次数标签
        time_frame = QFrame()
        time_frame.setStyleSheet("""
            QFrame {
                background-color: #e3f2fd;
                border-left: 4px solid #2196f3;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        learn_count = record.get('learn_count', 1)
        time_info = f"🕐 学习时间: {record.get('timestamp', '')}"
        if learn_count > 1:
            time_info += f"  📚 累计学习: {learn_count} 次"
        
        time_label = QLabel(time_info)
        time_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #1976d2;")
        time_layout = QVBoxLayout(time_frame)
        time_layout.addWidget(time_label)
        self.detail_layout.addWidget(time_frame)
        
        # 原文区域
        original_frame = QFrame()
        original_frame.setStyleSheet("""
            QFrame {
                background-color: #fff3e0;
                border-left: 4px solid #ff9800;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        original_layout = QVBoxLayout(original_frame)
        
        original_title = QLabel("📝 原文")
        original_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ef6c00; margin-bottom: 10px;")
        
        original_text = QLabel(record.get("original_text", ""))
        original_text.setStyleSheet("""
            QLabel {
                font-size: 15px;
                line-height: 1.6;
                color: #212529;
                background-color: white;
                padding: 15px;
                border-radius: 8px;
                border: 1px solid #ffcc02;
            }
        """)
        original_text.setWordWrap(True)
        
        original_layout.addWidget(original_title)
        original_layout.addWidget(original_text)
        self.detail_layout.addWidget(original_frame)
        
        # 翻译区域
        translation_frame = QFrame()
        translation_frame.setStyleSheet("""
            QFrame {
                background-color: #e8f5e8;
                border-left: 4px solid #4caf50;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        translation_layout = QVBoxLayout(translation_frame)
        
        translation_title = QLabel("🌐 翻译")
        translation_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2e7d32; margin-bottom: 10px;")
        
        translation_text = QLabel(record.get("translation", ""))
        translation_text.setStyleSheet("""
            QLabel {
                font-size: 15px;
                line-height: 1.6;
                color: #212529;
                background-color: white;
                padding: 15px;
                border-radius: 8px;
                border: 1px solid #81c784;
            }
        """)
        translation_text.setWordWrap(True)
        
        translation_layout.addWidget(translation_title)
        translation_layout.addWidget(translation_text)
        self.detail_layout.addWidget(translation_frame)
        
        # 重要单词区域
        words = record.get("important_words", {})
        if words:
            words_frame = QFrame()
            words_frame.setStyleSheet("""
                QFrame {
                    background-color: #f3e5f5;
                    border-left: 4px solid #9c27b0;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            words_layout = QVBoxLayout(words_frame)
            
            words_title = QLabel("💎 重要单词")
            words_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7b1fa2; margin-bottom: 10px;")
            words_layout.addWidget(words_title)
            
            words_container = QFrame()
            words_container.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 8px;
                    border: 1px solid #ce93d8;
                    padding: 15px;
                }
            """)
            words_container_layout = QVBoxLayout(words_container)
            
            for word, meaning in words.items():
                word_item = QFrame()
                word_item.setStyleSheet("""
                    QFrame {
                        background-color: #fafafa;
                        border-radius: 5px;
                        padding: 10px;
                        margin-bottom: 5px;
                        border-left: 3px solid #ab47bc;
                    }
                """)
                word_layout = QHBoxLayout(word_item)
                word_layout.setContentsMargins(10, 5, 10, 5)
                
                word_label = QLabel(word)
                word_label.setStyleSheet("font-weight: bold; color: #4a148c; font-size: 14px;")
                
                meaning_label = QLabel(meaning)
                meaning_label.setStyleSheet("color: #212529; font-size: 14px;")
                meaning_label.setWordWrap(True)
                
                word_layout.addWidget(word_label, 0)
                word_layout.addWidget(QLabel("→"), 0)
                word_layout.addWidget(meaning_label, 1)
                
                words_container_layout.addWidget(word_item)
            
            words_layout.addWidget(words_container)
            self.detail_layout.addWidget(words_frame)
        
        # 语法解释区域
        grammar = record.get("grammar_points", {})
        if grammar:
            grammar_frame = QFrame()
            grammar_frame.setStyleSheet("""
                QFrame {
                    background-color: #fff8e1;
                    border-left: 4px solid #ffc107;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            grammar_layout = QVBoxLayout(grammar_frame)
            
            grammar_title = QLabel("📚 语法解释")
            grammar_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #f57f17; margin-bottom: 10px;")
            grammar_layout.addWidget(grammar_title)
            
            grammar_container = QFrame()
            grammar_container.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 8px;
                    border: 1px solid #ffcc02;
                    padding: 15px;
                }
            """)
            grammar_container_layout = QVBoxLayout(grammar_container)
            
            for sentence, explanation in grammar.items():
                grammar_item = QFrame()
                grammar_item.setStyleSheet("""
                    QFrame {
                        background-color: #fafafa;
                        border-radius: 8px;
                        padding: 15px;
                        margin-bottom: 10px;
                        border-left: 3px solid #ffb300;
                    }
                """)
                grammar_item_layout = QVBoxLayout(grammar_item)
                
                sentence_label = QLabel(f"📖 {sentence}")
                sentence_label.setStyleSheet("""
                    QLabel {
                        font-weight: bold;
                        color: #e65100;
                        font-size: 14px;
                        margin-bottom: 8px;
                        background-color: #fff3e0;
                        padding: 8px;
                        border-radius: 5px;
                    }
                """)
                sentence_label.setWordWrap(True)
                
                explanation_label = QLabel(explanation)
                explanation_label.setStyleSheet("""
                    QLabel {
                        color: #424242;
                        font-size: 14px;
                        line-height: 1.5;
                        padding: 10px;
                        background-color: #f5f5f5;
                        border-radius: 5px;
                    }
                """)
                explanation_label.setWordWrap(True)
                
                grammar_item_layout.addWidget(sentence_label)
                grammar_item_layout.addWidget(explanation_label)
                
                grammar_container_layout.addWidget(grammar_item)
            
            grammar_layout.addWidget(grammar_container)
            self.detail_layout.addWidget(grammar_frame)
        
        self.detail_layout.addStretch()
    
    def update_statistics(self):
        """更新统计信息（包括搜索结果统计）"""
        total_records = len(self.records)
        filtered_records = len(self.filtered_records)
        
        # 统计独特单词数
        all_words = set()
        filtered_words = set()
        for record in self.records:
            words = record.get("important_words", {}).keys()
            all_words.update(w.lower() for w in words)
        
        for record in self.filtered_records:
            words = record.get("important_words", {}).keys()
            filtered_words.update(w.lower() for w in words)
        
        today = datetime.now().strftime("%Y-%m-%d")
        today_records = len([r for r in self.records if r.get("date", "") == today])
        
        # 添加搜索状态信息
        search_query = self.search_input.text().strip()
        search_info = ""
        if search_query:
            search_info = f" | 🔍 搜索: '{search_query}'"
        
        stats_text = f"📊 总计: {total_records} 句子, {len(all_words)} 单词 | 📝 显示: {filtered_records} 句子, {len(filtered_words)} 单词 | 🗓️ 今日: {today_records} 条{search_info}"
        self.stats_label.setText(stats_text)
    
    def export_notes(self):
        """导出笔记"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 这里可以实现导出功能，比如导出为文本文件
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            export_path = os.path.join(current_dir, f"learning_notes_export_{timestamp}.txt")
            
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write("=== 英语学习笔记导出 ===\n")
                f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"总记录数: {len(self.records)}\n\n")
                
                for i, record in enumerate(self.records, 1):
                    f.write(f"--- 记录 {i} ---\n")
                    f.write(f"时间: {record.get('timestamp', '')}\n")
                    f.write(f"原文: {record.get('original_text', '')}\n")
                    f.write(f"翻译: {record.get('translation', '')}\n")
                    
                    if record.get("important_words"):
                        f.write("重要单词:\n")
                        for word, meaning in record.get("important_words", {}).items():
                            f.write(f"  • {word}: {meaning}\n")
                    
                    if record.get("grammar_points"):
                        f.write("语法解释:\n")
                        for sentence, explanation in record.get("grammar_points", {}).items():
                            f.write(f"  【{sentence}】\n  {explanation}\n")
                    
                    f.write("\n" + "="*50 + "\n\n")
            
            QMessageBox.information(self, "导出成功", f"笔记已导出至:\n{export_path}")
        except Exception as e:
            QMessageBox.warning(self, "导出失败", f"导出笔记时发生错误:\n{str(e)}")
    
    def open_quiz_window(self):
        """打开题库练习窗口"""
        try:
            if not self.records:
                QMessageBox.warning(self, "提示", "没有可用的学习记录！\n请先进行一些翻译学习，积累学习记录后再开始测试。")
                return
            
            # 导入题库窗口
            from quiz.quiz_window import QuizWindow
            
            # 检查是否已有题库窗口打开
            if not hasattr(self, 'quiz_window') or not self.quiz_window:
                self.quiz_window = QuizWindow(self.records)
            
            # 更新记录数据（防止记录更新后题库窗口数据过期）
            self.quiz_window.records = self.records
            
            self.quiz_window.show()
            self.quiz_window.raise_()
            self.quiz_window.activateWindow()
            
        except ImportError as e:
            QMessageBox.critical(self, "错误", f"题库功能模块未找到:\n{str(e)}\n\n请确保quiz目录中的文件完整。")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开题库练习时发生错误:\n{str(e)}")
    
    def delete_record_with_confirmation(self, record_id):
        """显示确认对话框并删除记录"""
        if record_id is None:
            return
            
        try:
            # 找到对应的记录以获取显示信息
            record_to_delete = None
            for record in self.records:
                if record.get("id") == record_id:
                    record_to_delete = record
                    break
            
            if not record_to_delete:
                QMessageBox.warning(self, "错误", "未找到要删除的记录！")
                return
            
            # 获取记录的简短预览信息
            original_text = record_to_delete.get("original_text", "")
            preview_text = original_text[:50] + "..." if len(original_text) > 50 else original_text
            
            # 显示确认对话框
            reply = QMessageBox.question(
                self,
                "确认删除",
                f"确定要删除这条学习记录吗？\n\n原文: {preview_text}\n\n此操作不可撤销！",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No  # 默认选择"否"
            )
            
            if reply == QMessageBox.Yes:
                # 执行删除
                success = NotesManager.delete_record(record_id)
                if success:
                    # 删除成功，重新加载数据并更新界面
                    self.load_records()
                    QMessageBox.information(self, "删除成功", "记录已成功删除！")
                    
                    # 如果有RAG管理器，需要重新构建索引
                    try:
                        if rag_manager.is_loaded:
                            rag_manager.build_index_from_notes()
                            print("RAG索引已更新")
                    except Exception as rag_error:
                        print(f"更新RAG索引时出错: {rag_error}")
                        
                else:
                    QMessageBox.critical(self, "删除失败", "删除记录时发生错误，请重试！")
                    
        except Exception as e:
            print(f"删除记录时出错: {e}")
            QMessageBox.critical(self, "错误", f"删除记录时发生错误:\n{str(e)}")
    
    def return_to_main_program(self):
        """返回主程序"""
        try:
            # 确认对话框
            reply = QMessageBox.question(
                self, 
                "返回翻译助手", 
                "确定要关闭学习笔记并返回二游翻译助手吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 发送返回信号
                self.return_to_main.emit()
                
        except Exception as e:
            print(f"返回主程序时出错: {e}")
            # 即使出错也发送信号
            self.return_to_main.emit()

