import random
import json
import uuid
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
from datetime import datetime

# 添加父目录到路径以导入LLM模块
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm.call_api import chat


class QuizGenerator:
    """测试题目生成器"""
    
    def __init__(self):
        self.question_types = [
            "word_spelling",     # 单词默写
            "grammar_choice",    # 语法选择题  
            "word_choice",       # 单词释义选择题
            "translation_choice" # 翻译选择题
        ]
        self.difficulty_levels = ["easy", "medium", "hard"]
        
    def generate_quiz_from_records(self, records: List[Dict], 
                                 question_count: int = 10,
                                 question_types: Optional[List[str]] = None) -> List[Dict]:
        """
        从学习记录中生成测试题目
        
        Args:
            records: 学习记录列表
            question_count: 要生成的题目数量
            question_types: 指定题目类型，None表示随机
        
        Returns:
            生成的题目列表
        """
        if not records:
            return []
        
        if question_types is None:
            question_types = self.question_types
        
        questions = []
        used_records = set()
        
        for _ in range(question_count):
            # 随机选择题目类型
            q_type = random.choice(question_types)
            
            # 根据题目类型选择合适的记录
            suitable_records = self._filter_records_for_type(records, q_type)
            if not suitable_records:
                continue
                
            # 选择一个未使用的记录（避免重复）
            available_records = [r for r in suitable_records if r.get('id') not in used_records]
            if not available_records:
                available_records = suitable_records  # 如果都用过了，重新开始
                
            record = random.choice(available_records)
            used_records.add(record.get('id'))
            
            # 根据类型生成对应的题目
            question = self._generate_question_by_type(record, q_type)
            if question:
                questions.append(question)
        
        return questions
    
    def _filter_records_for_type(self, records: List[Dict], q_type: str) -> List[Dict]:
        """根据题目类型筛选合适的记录"""
        filtered = []
        
        for record in records:
            if q_type == "word_spelling" and record.get("important_words"):
                filtered.append(record)
            elif q_type == "grammar_choice" and record.get("grammar_points"):
                filtered.append(record)
            elif q_type in ["word_choice", "translation_choice"]:
                if record.get("important_words") or record.get("original_text"):
                    filtered.append(record)
        
        return filtered
    
    def _generate_question_by_type(self, record: Dict, q_type: str) -> Optional[Dict]:
        """根据类型生成具体题目"""
        try:
            if q_type == "word_spelling":
                return self._generate_word_spelling_question(record)
            elif q_type == "grammar_choice":
                return self._generate_grammar_choice_question(record)
            elif q_type == "word_choice":
                return self._generate_word_choice_question(record)
            elif q_type == "translation_choice":
                return self._generate_translation_choice_question(record)
        except Exception as e:
            print(f"生成题目时出错: {e}")
            return None
        
        return None
    
    def _generate_word_spelling_question(self, record: Dict) -> Optional[Dict]:
        """生成单词默写题"""
        important_words = record.get("important_words", {})
        if not important_words:
            return None
        
        # 随机选择一个单词
        word, meaning = random.choice(list(important_words.items()))
        
        question = {
            "question_id": str(uuid.uuid4()),
            "question_type": "word_spelling",
            "question": f"根据释义写出单词：\n\n【释义】{meaning}",
            "correct_answer": word.lower(),
            "explanation": f"正确答案是: {word}\n释义: {meaning}",
            "source_record_id": record.get("id"),
            "difficulty": self._determine_difficulty(word),
            "tags": ["单词", "默写"],
            "context_sentence": record.get("original_text", ""),
            "hint": f"单词长度: {len(word)} 个字母，首字母: {word[0].upper()}"
        }
        
        return question
    
    def _generate_grammar_choice_question(self, record: Dict) -> Optional[Dict]:
        """生成语法选择题（需要LLM生成干扰选项）"""
        grammar_points = record.get("grammar_points", {})
        if not grammar_points:
            return None
        
        # 随机选择一个语法点
        sentence, explanation = random.choice(list(grammar_points.items()))
        
        # 不立即调用LLM，先返回题目框架
        question = {
            "question_id": str(uuid.uuid4()),
            "question_type": "grammar_choice",
            "question": f"下面句子的语法解释哪个是正确的？\n\n【句子】{sentence}",
            "sentence": sentence,
            "explanation": explanation,
            "source_record_id": record.get("id"),
            "difficulty": self._determine_grammar_difficulty(sentence),
            "tags": ["语法", "选择题"],
            "context_sentence": record.get("original_text", ""),
            "needs_llm_options": True
        }
        
        return question
    
    def _generate_word_choice_question(self, record: Dict) -> Optional[Dict]:
        """生成单词释义选择题"""
        important_words = record.get("important_words", {})
        if not important_words:
            return None
        
        # 随机选择一个单词
        word, correct_meaning = random.choice(list(important_words.items()))
        
        # 不立即调用LLM，先返回题目框架
        question = {
            "question_id": str(uuid.uuid4()),
            "question_type": "word_choice",
            "question": f"单词 \"{word}\" 在下面语境中的正确释义是？\n\n【语境】{record.get('original_text', '')}",
            "word": word,
            "correct_meaning": correct_meaning,
            "explanation": f"正确答案: {correct_meaning}",
            "source_record_id": record.get("id"),
            "difficulty": self._determine_difficulty(word),
            "tags": ["单词", "释义", "选择题"],
            "context_text": record.get('original_text', ''),
            "needs_llm_options": True
        }
        
        return question
    
    def _generate_translation_choice_question(self, record: Dict) -> Optional[Dict]:
        """生成翻译选择题"""
        original_text = record.get("original_text", "")
        correct_translation = record.get("translation", "")
        
        if not original_text or not correct_translation:
            return None
        
        # 不立即调用LLM，先返回题目框架
        question = {
            "question_id": str(uuid.uuid4()),
            "question_type": "translation_choice",
            "question": f"下面英文句子的正确翻译是？\n\n【英文】{original_text}",
            "original_text": original_text,
            "correct_translation": correct_translation,
            "explanation": f"正确翻译: {correct_translation}",
            "source_record_id": record.get("id"),
            "difficulty": self._determine_translation_difficulty(original_text),
            "tags": ["翻译", "选择题"],
            "needs_llm_options": True
        }
        
        return question
    
    def _generate_grammar_options_with_llm(self, sentence: str, correct_explanation: str) -> List[Dict]:
        """使用LLM生成语法选择题的干扰选项"""
        prompt = f"""
请为以下语法题目生成3个错误的干扰选项和1个正确选项（总共4个选项）。

【句子】{sentence}
【正确解释】{correct_explanation}

要求：
1. 干扰选项要看起来合理但实际错误
2. 难度适中，不要太明显的错误
3. 每个选项50字以内

请按照以下JSON格式返回：
{{
    "options": [
        {{"text": "选项内容", "is_correct": false}},
        {{"text": "选项内容", "is_correct": false}},
        {{"text": "选项内容", "is_correct": false}},
        {{"text": "{correct_explanation}", "is_correct": true}}
    ]
}}
只返回JSON，不要其他内容。
"""
        
        try:
            response = chat(prompt)
            # 清理响应格式
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            result = json.loads(response)
            return result.get("options", [])
        except Exception as e:
            print(f"LLM生成语法选项失败: {e}")
            return []
    
    def _generate_word_meaning_options_with_llm(self, word: str, correct_meaning: str) -> List[Dict]:
        """使用LLM生成单词释义选择题的干扰选项"""
        prompt = f"""
请为单词释义题目生成3个错误的干扰选项和1个正确选项（总共4个选项）。

【单词】{word}
【正确释义】{correct_meaning}

要求：
1. 干扰选项要是相似或相关的释义但不正确
2. 每个选项30字以内
3. 保持中文释义风格

请按照以下JSON格式返回：
{{
    "options": [
        {{"text": "干扰释义1", "is_correct": false}},
        {{"text": "干扰释义2", "is_correct": false}},
        {{"text": "干扰释义3", "is_correct": false}},
        {{"text": "{correct_meaning}", "is_correct": true}}
    ]
}}
只返回JSON，不要其他内容。
"""
        
        try:
            response = chat(prompt)
            # 清理响应格式
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            result = json.loads(response)
            return result.get("options", [])
        except Exception as e:
            print(f"LLM生成单词选项失败: {e}")
            return []
    
    def _generate_translation_options_with_llm(self, original_text: str, correct_translation: str) -> List[Dict]:
        """使用LLM生成翻译选择题的干扰选项"""
        prompt = f"""
请为翻译题目生成3个错误的干扰选项和1个正确选项（总共4个选项）。

【英文原文】{original_text}
【正确翻译】{correct_translation}

要求：
1. 干扰选项要看起来合理但存在翻译错误
2. 可以是语义偏差、语法错误或表达不当
3. 保持中文表达的自然性

请按照以下JSON格式返回：
{{
    "options": [
        {{"text": "错误翻译1", "is_correct": false}},
        {{"text": "错误翻译2", "is_correct": false}},
        {{"text": "错误翻译3", "is_correct": false}},
        {{"text": "{correct_translation}", "is_correct": true}}
    ]
}}
只返回JSON，不要其他内容。
"""
        
        try:
            response = chat(prompt)
            # 清理响应格式
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            result = json.loads(response)
            return result.get("options", [])
        except Exception as e:
            print(f"LLM生成翻译选项失败: {e}")
            return []
    
    def generate_options_batch_threaded(self, questions: List[Dict], max_workers: int = 8) -> List[Dict]:
        """
        多线程批量生成选择题选项
        
        Args:
            questions: 需要生成选项的题目列表
            max_workers: 最大线程数
        
        Returns:
            完善后的题目列表
        """
        # 筛选出需要生成选项的题目
        questions_need_options = [q for q in questions if q.get("question_type") in ["grammar_choice", "word_choice", "translation_choice"]]
        
        if not questions_need_options:
            return questions
        
        completed_questions = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交任务
            future_to_question = {}
            for question in questions_need_options:
                if question.get("question_type") == "grammar_choice":
                    future = executor.submit(self._enhance_grammar_question_with_llm, question)
                elif question.get("question_type") == "word_choice":
                    future = executor.submit(self._enhance_word_question_with_llm, question)
                elif question.get("question_type") == "translation_choice":
                    future = executor.submit(self._enhance_translation_question_with_llm, question)
                
                future_to_question[future] = question
            
            # 收集结果
            for future in as_completed(future_to_question):
                original_question = future_to_question[future]
                try:
                    enhanced_question = future.result(timeout=30)  # 30秒超时
                    if enhanced_question:
                        completed_questions.append(enhanced_question)
                    else:
                        # 如果增强失败，使用原始题目
                        completed_questions.append(original_question)
                except Exception as e:
                    print(f"线程处理题目失败: {e}")
                    completed_questions.append(original_question)
        
        # 合并结果，保持原有顺序
        result_questions = []
        for q in questions:
            if q.get("question_type") in ["grammar_choice", "word_choice", "translation_choice"]:
                # 找到对应的增强题目
                enhanced = next((cq for cq in completed_questions if cq.get("question_id") == q.get("question_id")), q)
                result_questions.append(enhanced)
            else:
                result_questions.append(q)
        
        return result_questions
    
    def _enhance_grammar_question_with_llm(self, question: Dict) -> Dict:
        """增强语法题目（添加LLM生成的选项）"""
        sentence = question.get("sentence", question.get("context_sentence", ""))
        explanation = question.get("explanation", "")
        
        options = self._generate_grammar_options_with_llm(sentence, explanation)
        if not options:
            options = self._generate_fallback_grammar_options(explanation)
        
        random.shuffle(options)
        correct_index = -1
        for i, option in enumerate(options):
            if option.get("is_correct", False):
                correct_index = i
                break
        
        question.update({
            "options": [option["text"] for option in options],
            "correct_answer": correct_index,
            "needs_llm_options": False
        })
        
        return question
    
    def _enhance_word_question_with_llm(self, question: Dict) -> Dict:
        """增强单词题目"""
        word = question.get("word", "")
        correct_meaning = question.get("correct_meaning", "")
        
        if not word or not correct_meaning:
            return question
        
        options = self._generate_word_meaning_options_with_llm(word, correct_meaning)
        if not options:
            options = self._generate_fallback_word_options(correct_meaning)
        
        random.shuffle(options)
        correct_index = -1
        for i, option in enumerate(options):
            if option.get("is_correct", False):
                correct_index = i
                break
        
        question.update({
            "options": [option["text"] for option in options],
            "correct_answer": correct_index,
            "needs_llm_options": False
        })
        
        return question
    
    def _enhance_translation_question_with_llm(self, question: Dict) -> Dict:
        """增强翻译题目"""
        original_text = question.get("original_text", "")
        correct_translation = question.get("correct_translation", "")
        
        if not original_text or not correct_translation:
            return question
        
        options = self._generate_translation_options_with_llm(original_text, correct_translation)
        if not options:
            options = self._generate_fallback_translation_options(correct_translation)
        
        random.shuffle(options)
        correct_index = -1
        for i, option in enumerate(options):
            if option.get("is_correct", False):
                correct_index = i
                break
        
        question.update({
            "options": [option["text"] for option in options],
            "correct_answer": correct_index,
            "needs_llm_options": False
        })
        
        return question
    
    def _generate_fallback_grammar_options(self, explanation: str) -> List[Dict]:
        """生成语法题的预设干扰选项"""
        return [
            {"text": explanation, "is_correct": True},
            {"text": "这是一个简单句结构，主语+谓语+宾语", "is_correct": False},
            {"text": "这句话使用了被动语态来强调动作的接受者", "is_correct": False},
            {"text": "句中包含定语从句，用来修饰前面的名词", "is_correct": False}
        ]
    
    def _generate_fallback_word_options(self, correct_meaning: str) -> List[Dict]:
        """生成单词题的预设干扰选项"""
        fallback_meanings = [
            "表示时间的副词",
            "表示地点的名词",
            "表示动作的动词",
            "表示状态的形容词"
        ]
        
        options = [{"text": correct_meaning, "is_correct": True}]
        for meaning in fallback_meanings[:3]:
            options.append({"text": meaning, "is_correct": False})
        
        return options
    
    def _generate_fallback_translation_options(self, correct_translation: str) -> List[Dict]:
        """生成翻译题的预设干扰选项"""
        return [
            {"text": correct_translation, "is_correct": True},
            {"text": "这是一个关于游戏剧情的句子。", "is_correct": False},
            {"text": "角色在讨论某个重要事件。", "is_correct": False},
            {"text": "句子表达了某种情感或态度。", "is_correct": False}
        ]
    
    def _determine_difficulty(self, word: str) -> str:
        """根据单词长度和复杂度判断难度"""
        length = len(word)
        if length <= 4:
            return "easy"
        elif length <= 8:
            return "medium"
        else:
            return "hard"
    
    def _determine_grammar_difficulty(self, sentence: str) -> str:
        """根据句子复杂度判断语法难度"""
        # 简单的难度判断逻辑
        if len(sentence.split()) <= 6:
            return "easy"
        elif len(sentence.split()) <= 12:
            return "medium"
        else:
            return "hard"
    
    def _determine_translation_difficulty(self, text: str) -> str:
        """根据文本长度和复杂度判断翻译难度"""
        words = text.split()
        if len(words) <= 5:
            return "easy"
        elif len(words) <= 10:
            return "medium"
        else:
            return "hard"


class QuizSession:
    """测试会话管理器"""
    
    def __init__(self, questions: List[Dict]):
        self.questions = questions
        self.current_question_index = 0
        self.user_answers = {}
        self.score = 0
        self.start_time = datetime.now()
        self.end_time = None
        
    def get_current_question(self) -> Optional[Dict]:
        """获取当前题目"""
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None
    
    def submit_answer(self, answer) -> bool:
        """提交答案并返回是否正确"""
        current_question = self.get_current_question()
        if not current_question:
            return False
        
        question_id = current_question.get("question_id")
        correct_answer = current_question.get("correct_answer")
        
        # 记录用户答案
        self.user_answers[question_id] = {
            "user_answer": answer,
            "is_correct": self._check_answer(answer, correct_answer, current_question.get("question_type")),
            "question": current_question
        }
        
        is_correct = self.user_answers[question_id]["is_correct"]
        if is_correct:
            self.score += 1
        
        return is_correct
    
    def _check_answer(self, user_answer, correct_answer, question_type: str) -> bool:
        """检查答案是否正确"""
        if question_type == "word_spelling":
            # 单词默写题，不区分大小写
            return user_answer.lower().strip() == str(correct_answer).lower().strip()
        else:
            # 选择题，比较选项索引
            return user_answer == correct_answer
    
    def next_question(self) -> bool:
        """进入下一题，返回是否还有题目"""
        self.current_question_index += 1
        return self.current_question_index < len(self.questions)
    
    def is_completed(self) -> bool:
        """测试是否完成"""
        return self.current_question_index >= len(self.questions)
    
    def finish_session(self):
        """结束测试会话"""
        self.end_time = datetime.now()
    
    def get_results(self) -> Dict:
        """获取测试结果"""
        total_questions = len(self.questions)
        correct_answers = self.score
        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        duration = None
        if self.end_time and self.start_time:
            duration = (self.end_time - self.start_time).total_seconds()
        
        return {
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "wrong_answers": total_questions - correct_answers,
            "accuracy": round(accuracy, 1),
            "duration_seconds": duration,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "detailed_answers": self.user_answers
        }