import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter


class ProgressManager:
    """学习进度管理器"""
    
    def __init__(self):
        self.progress_file = self._get_progress_file_path()
        self.progress_data = self._load_progress_data()
    
    def _get_progress_file_path(self) -> str:
        """获取进度数据文件路径"""
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(current_dir, "quiz_progress.json")
    
    def _load_progress_data(self) -> Dict:
        """加载进度数据"""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {
                "quiz_history": [],
                "wrong_questions": [],
                "word_statistics": {},
                "grammar_statistics": {},
                "difficulty_stats": {
                    "easy": {"total": 0, "correct": 0},
                    "medium": {"total": 0, "correct": 0},
                    "hard": {"total": 0, "correct": 0}
                },
                "question_type_stats": {
                    "word_spelling": {"total": 0, "correct": 0},
                    "grammar_choice": {"total": 0, "correct": 0},
                    "word_choice": {"total": 0, "correct": 0},
                    "translation_choice": {"total": 0, "correct": 0}
                }
            }
        except Exception as e:
            print(f"加载进度数据失败: {e}")
            return {}
    
    def _save_progress_data(self):
        """保存进度数据"""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存进度数据失败: {e}")
    
    def record_quiz_result(self, quiz_results: Dict):
        """记录测试结果"""
        try:
            # 添加到历史记录
            quiz_record = {
                "timestamp": datetime.now().isoformat(),
                "total_questions": quiz_results["total_questions"],
                "correct_answers": quiz_results["correct_answers"],
                "wrong_answers": quiz_results["wrong_answers"],
                "accuracy": quiz_results["accuracy"],
                "duration_seconds": quiz_results.get("duration_seconds", 0)
            }
            
            self.progress_data["quiz_history"].append(quiz_record)
            
            # 记录错题
            detailed_answers = quiz_results.get("detailed_answers", {})
            for question_id, answer_data in detailed_answers.items():
                question = answer_data.get("question", {})
                is_correct = answer_data.get("is_correct", False)
                
                # 更新难度统计
                difficulty = question.get("difficulty", "medium")
                if difficulty in self.progress_data["difficulty_stats"]:
                    self.progress_data["difficulty_stats"][difficulty]["total"] += 1
                    if is_correct:
                        self.progress_data["difficulty_stats"][difficulty]["correct"] += 1
                
                # 更新题型统计
                question_type = question.get("question_type", "")
                if question_type in self.progress_data["question_type_stats"]:
                    self.progress_data["question_type_stats"][question_type]["total"] += 1
                    if is_correct:
                        self.progress_data["question_type_stats"][question_type]["correct"] += 1
                
                # 记录错题
                if not is_correct:
                    wrong_question = {
                        "timestamp": datetime.now().isoformat(),
                        "question_id": question_id,
                        "question": question,
                        "user_answer": answer_data.get("user_answer"),
                        "error_count": 1
                    }
                    
                    # 检查是否已存在相同题目的错误记录
                    existing_wrong = None
                    for wq in self.progress_data["wrong_questions"]:
                        if self._is_similar_question(wq["question"], question):
                            existing_wrong = wq
                            break
                    
                    if existing_wrong:
                        existing_wrong["error_count"] += 1
                        existing_wrong["timestamp"] = datetime.now().isoformat()
                    else:
                        self.progress_data["wrong_questions"].append(wrong_question)
                
                # 更新单词统计（如果是单词相关题目）
                if question_type in ["word_spelling", "word_choice"]:
                    self._update_word_statistics(question, is_correct)
                
                # 更新语法统计（如果是语法题目）
                if question_type == "grammar_choice":
                    self._update_grammar_statistics(question, is_correct)
            
            # 保存数据
            self._save_progress_data()
            
        except Exception as e:
            print(f"记录测试结果失败: {e}")
    
    def _is_similar_question(self, q1: Dict, q2: Dict) -> bool:
        """判断两个题目是否相似（用于合并错题记录）"""
        # 简单的相似度判断，可以根据需要完善
        return (q1.get("question_type") == q2.get("question_type") and 
                q1.get("source_record_id") == q2.get("source_record_id"))
    
    def _update_word_statistics(self, question: Dict, is_correct: bool):
        """更新单词统计"""
        # 从题目中提取单词信息
        question_text = question.get("question", "")
        # 这里需要根据具体的题目结构来提取单词
        # 简化处理，后续可以完善
        pass
    
    def _update_grammar_statistics(self, question: Dict, is_correct: bool):
        """更新语法统计"""
        # 从题目中提取语法信息
        # 简化处理，后续可以完善
        pass
    
    def get_wrong_questions(self, limit: Optional[int] = None, 
                          question_type: Optional[str] = None) -> List[Dict]:
        """获取错题列表"""
        wrong_questions = self.progress_data.get("wrong_questions", [])
        
        # 按题型筛选
        if question_type:
            wrong_questions = [wq for wq in wrong_questions 
                             if wq["question"].get("question_type") == question_type]
        
        # 按错误次数排序（错误次数多的排前面）
        wrong_questions.sort(key=lambda x: x.get("error_count", 0), reverse=True)
        
        # 限制数量
        if limit:
            wrong_questions = wrong_questions[:limit]
        
        return wrong_questions
    
    def get_statistics_summary(self) -> Dict:
        """获取统计摘要"""
        history = self.progress_data.get("quiz_history", [])
        
        if not history:
            return {
                "total_quizzes": 0,
                "total_questions": 0,
                "overall_accuracy": 0,
                "improvement_trend": 0,
                "weak_areas": [],
                "strong_areas": []
            }
        
        total_quizzes = len(history)
        total_questions = sum(quiz["total_questions"] for quiz in history)
        total_correct = sum(quiz["correct_answers"] for quiz in history)
        overall_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        # 计算进步趋势（最近5次测试的平均分与之前的对比）
        improvement_trend = 0
        if len(history) >= 6:
            recent_avg = sum(quiz["accuracy"] for quiz in history[-5:]) / 5
            previous_avg = sum(quiz["accuracy"] for quiz in history[-10:-5]) / 5
            improvement_trend = recent_avg - previous_avg
        
        # 分析薄弱环节
        weak_areas = []
        strong_areas = []
        
        difficulty_stats = self.progress_data.get("difficulty_stats", {})
        for difficulty, stats in difficulty_stats.items():
            if stats["total"] > 0:
                accuracy = stats["correct"] / stats["total"] * 100
                if accuracy < 60:
                    weak_areas.append(f"{difficulty}难度题目")
                elif accuracy > 80:
                    strong_areas.append(f"{difficulty}难度题目")
        
        type_stats = self.progress_data.get("question_type_stats", {})
        type_names = {
            "word_spelling": "单词默写",
            "grammar_choice": "语法选择",
            "word_choice": "单词释义",
            "translation_choice": "翻译选择"
        }
        
        for q_type, stats in type_stats.items():
            if stats["total"] > 0:
                accuracy = stats["correct"] / stats["total"] * 100
                type_name = type_names.get(q_type, q_type)
                if accuracy < 60:
                    weak_areas.append(type_name)
                elif accuracy > 80:
                    strong_areas.append(type_name)
        
        return {
            "total_quizzes": total_quizzes,
            "total_questions": total_questions,
            "overall_accuracy": round(overall_accuracy, 1),
            "improvement_trend": round(improvement_trend, 1),
            "weak_areas": weak_areas,
            "strong_areas": strong_areas,
            "recent_performance": [quiz["accuracy"] for quiz in history[-10:]]  # 最近10次成绩
        }
    
    def generate_review_questions(self, count: int = 10) -> List[Dict]:
        """基于错题生成复习题目"""
        wrong_questions = self.get_wrong_questions()
        
        if not wrong_questions:
            return []
        
        # 按错误次数和时间排序，优先复习错误次数多且较新的题目
        review_questions = []
        
        for wq in wrong_questions[:count]:
            question = wq["question"].copy()
            question["is_review"] = True
            question["error_count"] = wq.get("error_count", 1)
            question["review_note"] = f"这是你之前错过 {wq.get('error_count', 1)} 次的题目，请仔细作答。"
            review_questions.append(question)
        
        return review_questions
    
    def get_learning_insights(self) -> List[str]:
        """获取学习洞察和建议"""
        insights = []
        stats = self.get_statistics_summary()
        
        # 基于总体表现给出建议
        if stats["overall_accuracy"] >= 90:
            insights.append("🌟 优秀！你的整体表现非常出色，继续保持！")
        elif stats["overall_accuracy"] >= 70:
            insights.append("👍 不错！你的学习进步很明显，继续努力！")
        elif stats["overall_accuracy"] >= 60:
            insights.append("📈 进步中！建议多做练习，特别关注薄弱环节。")
        else:
            insights.append("💪 需要加油！建议从基础题目开始，逐步提高。")
        
        # 基于进步趋势
        if stats["improvement_trend"] > 5:
            insights.append("📊 近期进步显著！学习方法很有效。")
        elif stats["improvement_trend"] < -5:
            insights.append("⚠️ 近期成绩有所下降，建议复习之前的错题。")
        
        # 薄弱环节建议
        if stats["weak_areas"]:
            weak_areas_str = "、".join(stats["weak_areas"])
            insights.append(f"🎯 建议重点练习：{weak_areas_str}")
        
        # 优势领域鼓励
        if stats["strong_areas"]:
            strong_areas_str = "、".join(stats["strong_areas"])
            insights.append(f"✨ 你在这些方面表现优秀：{strong_areas_str}")
        
        # 错题建议
        wrong_count = len(self.get_wrong_questions())
        if wrong_count > 10:
            insights.append(f"📝 你有 {wrong_count} 道错题待复习，建议定期进行错题练习。")
        elif wrong_count > 0:
            insights.append(f"📋 你有 {wrong_count} 道错题，建议抽时间复习一下。")
        
        return insights
    
    def clear_old_data(self, days: int = 30):
        """清理旧数据（可选功能）"""
        try:
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            
            # 清理旧的测试历史
            history = self.progress_data.get("quiz_history", [])
            self.progress_data["quiz_history"] = [
                quiz for quiz in history 
                if datetime.fromisoformat(quiz["timestamp"]).timestamp() > cutoff_date
            ]
            
            # 清理旧的错题记录
            wrong_questions = self.progress_data.get("wrong_questions", [])
            self.progress_data["wrong_questions"] = [
                wq for wq in wrong_questions
                if datetime.fromisoformat(wq["timestamp"]).timestamp() > cutoff_date
            ]
            
            self._save_progress_data()
            
        except Exception as e:
            print(f"清理旧数据失败: {e}")


class WrongQuestionReview:
    """错题复习专用类"""
    
    def __init__(self, progress_manager: ProgressManager):
        self.progress_manager = progress_manager
    
    def create_review_quiz(self, question_type: Optional[str] = None, 
                          count: int = 10) -> List[Dict]:
        """创建错题复习测试"""
        wrong_questions = self.progress_manager.get_wrong_questions(
            limit=count, question_type=question_type
        )
        
        review_questions = []
        for wq in wrong_questions:
            question = wq["question"].copy()
            question["is_review"] = True
            question["original_error_count"] = wq.get("error_count", 1)
            question["review_hint"] = self._generate_review_hint(question, wq)
            review_questions.append(question)
        
        return review_questions
    
    def _generate_review_hint(self, question: Dict, wrong_record: Dict) -> str:
        """为错题生成复习提示"""
        error_count = wrong_record.get("error_count", 1)
        question_type = question.get("question_type", "")
        
        hints = {
            "word_spelling": f"这个单词你已经错过{error_count}次了，注意拼写细节。",
            "grammar_choice": f"这个语法点你错过{error_count}次，仔细分析句子结构。",
            "word_choice": f"这个单词的释义你错过{error_count}次，注意语境含义。",
            "translation_choice": f"这个翻译你错过{error_count}次，注意语句的完整表达。"
        }
        
        return hints.get(question_type, f"这道题你已经错过{error_count}次，请仔细思考。")
    
    def get_review_statistics(self) -> Dict:
        """获取错题复习统计"""
        wrong_questions = self.progress_manager.get_wrong_questions()
        
        if not wrong_questions:
            return {
                "total_wrong_questions": 0,
                "by_type": {},
                "by_difficulty": {},
                "most_problematic": []
            }
        
        by_type = defaultdict(int)
        by_difficulty = defaultdict(int)
        
        for wq in wrong_questions:
            question = wq["question"]
            by_type[question.get("question_type", "unknown")] += 1
            by_difficulty[question.get("difficulty", "unknown")] += 1
        
        # 找出最常错的题目
        most_problematic = sorted(
            wrong_questions, 
            key=lambda x: x.get("error_count", 0), 
            reverse=True
        )[:5]
        
        return {
            "total_wrong_questions": len(wrong_questions),
            "by_type": dict(by_type),
            "by_difficulty": dict(by_difficulty),
            "most_problematic": most_problematic
        }