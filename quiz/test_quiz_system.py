#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题库系统使用示例和测试脚本

运行此脚本可以测试题库系统的各项功能
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.main import NotesManager
from quiz import QuizGenerator, ProgressManager, WrongQuestionReview


def test_quiz_generator():
    """测试题目生成器"""
    print("=" * 50)
    print("测试题目生成器")
    print("=" * 50)
    
    # 加载学习记录
    records = NotesManager.load_all_records()
    if not records:
        print("❌ 没有找到学习记录，请先进行一些翻译学习")
        return False
    
    print(f"✅ 找到 {len(records)} 条学习记录")
    
    # 创建题目生成器
    generator = QuizGenerator()
    
    # 生成题目
    questions = generator.generate_quiz_from_records(
        records=records,
        question_count=5,
        question_types=["word_spelling", "grammar_choice"]
    )
    
    if questions:
        print(f"✅ 成功生成 {len(questions)} 道题目")
        
        # 显示题目信息
        for i, q in enumerate(questions, 1):
            print(f"\n题目 {i}:")
            print(f"  类型: {q.get('question_type')}")
            print(f"  难度: {q.get('difficulty')}")
            print(f"  题目: {q.get('question', '')[:100]}...")
        
        return True
    else:
        print("❌ 题目生成失败")
        return False


def test_progress_manager():
    """测试进度管理器"""
    print("=" * 50)
    print("测试进度管理器")
    print("=" * 50)
    
    # 创建进度管理器
    progress_manager = ProgressManager()
    
    # 获取统计摘要
    stats = progress_manager.get_statistics_summary()
    
    print("📊 学习统计:")
    print(f"  总测试次数: {stats['total_quizzes']}")
    print(f"  总题目数: {stats['total_questions']}")
    print(f"  总体正确率: {stats['overall_accuracy']}%")
    print(f"  进步趋势: {stats['improvement_trend']:+.1f}%")
    
    if stats['weak_areas']:
        print(f"  薄弱环节: {', '.join(stats['weak_areas'])}")
    
    if stats['strong_areas']:
        print(f"  优势领域: {', '.join(stats['strong_areas'])}")
    
    # 获取学习建议
    insights = progress_manager.get_learning_insights()
    if insights:
        print("\n💡 学习建议:")
        for insight in insights:
            print(f"  • {insight}")
    
    # 获取错题信息
    wrong_questions = progress_manager.get_wrong_questions()
    print(f"\n❌ 错题数量: {len(wrong_questions)}")
    
    return True


def test_wrong_question_review():
    """测试错题复习功能"""
    print("=" * 50)
    print("测试错题复习功能")
    print("=" * 50)
    
    progress_manager = ProgressManager()
    review = WrongQuestionReview(progress_manager)
    
    # 获取错题统计
    review_stats = review.get_review_statistics()
    
    print("📋 错题统计:")
    print(f"  总错题数: {review_stats['total_wrong_questions']}")
    print(f"  按类型分布: {review_stats['by_type']}")
    print(f"  按难度分布: {review_stats['by_difficulty']}")
    
    if review_stats['most_problematic']:
        print("\n🚨 最需要复习的题目:")
        for i, wq in enumerate(review_stats['most_problematic'][:3], 1):
            question = wq['question']
            print(f"  {i}. {question.get('question_type')} - 错误{wq.get('error_count', 1)}次")
    
    # 生成复习题目
    review_questions = review.create_review_quiz(count=3)
    
    if review_questions:
        print(f"\n✅ 生成 {len(review_questions)} 道复习题")
        for i, q in enumerate(review_questions, 1):
            print(f"  {i}. {q.get('question_type')} (原错误{q.get('original_error_count', 1)}次)")
    else:
        print("\n🎉 没有错题需要复习！")
    
    return True


def show_usage_instructions():
    """显示使用说明"""
    print("=" * 70)
    print("🎯 英语学习本题库系统使用指南")
    print("=" * 70)
    
    instructions = """
📚 功能特色:
  • 四种题型：单词默写、语法选择、单词释义选择、翻译选择
  • 智能难度分级：简单、中等、困难
  • 多线程LLM生成干扰选项，提高题目质量
  • 错题自动收集和复习系统
  • 学习进度统计和个性化建议
  • 美观的界面设计，提供舒适的练习体验

🚀 使用方法:
  1. 运行主程序：python app/main.py
  2. 先进行翻译学习，积累学习记录
  3. 在笔记窗口点击"🎯 题库练习"按钮
  4. 选择题目类型、数量和难度
  5. 开始答题，系统会自动记录错误和进度
  6. 使用错题复习模式针对性练习

📁 文件结构:
  quiz/
  ├── __init__.py              # 模块初始化
  ├── quiz_generator.py        # 题目生成器
  ├── quiz_window.py           # 题库练习界面
  └── progress_manager.py      # 进度管理器

📊 数据文件:
  • learning_notes.json        # 学习记录（已有）
  • quiz_progress.json         # 题库练习进度（自动生成）

💡 提示:
  • 建议先积累至少10条翻译记录再开始题库练习
  • 定期进行错题复习，巩固学习效果
  • 关注个性化学习建议，针对薄弱环节加强练习
    """
    
    print(instructions)


def main():
    """主函数"""
    print("🎯 英语学习本题库系统测试")
    print("正在测试各项功能...")
    
    try:
        # 测试题目生成器
        success1 = test_quiz_generator()
        
        # 测试进度管理器
        success2 = test_progress_manager()
        
        # 测试错题复习
        success3 = test_wrong_question_review()
        
        print("\n" + "=" * 50)
        print("测试结果总结:")
        print("=" * 50)
        print(f"题目生成器: {'✅ 成功' if success1 else '❌ 失败'}")
        print(f"进度管理器: {'✅ 成功' if success2 else '❌ 失败'}")
        print(f"错题复习功能: {'✅ 成功' if success3 else '❌ 失败'}")
        
        if all([success1, success2, success3]):
            print("\n🎉 所有功能测试通过！题库系统可以正常使用。")
        else:
            print("\n⚠️ 部分功能测试失败，请检查学习记录是否存在。")
        
        # 显示使用说明
        show_usage_instructions()
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        print("请确保所有依赖都已正确安装，并且有可用的学习记录。")


if __name__ == "__main__":
    main()