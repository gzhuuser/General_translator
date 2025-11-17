from PyQt5.QtCore import QThread, pyqtSignal


class TextCorrectionThread(QThread):
    correction_completed = pyqtSignal(str, str, dict, dict)
    correction_failed = pyqtSignal()
    
    def __init__(self, original_text, translation, important_words, grammar_points):
        super().__init__()
        self.original_text = original_text
        self.translation = translation
        self.important_words = important_words
        self.grammar_points = grammar_points
    
    def run(self):
        try:
            from llm.call_api import correct_ocr_text
            
            corrected_text = correct_ocr_text(self.original_text)
            
            self.correction_completed.emit(
                corrected_text,
                self.translation,
                self.important_words,
                self.grammar_points
            )
            
        except Exception as e:
            print(f"文本修正线程出错: {e}")
            self.correction_failed.emit()
