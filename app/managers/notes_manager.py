import os
import json
import time
import shutil
from datetime import datetime


class NotesManager:
    @staticmethod
    def get_notes_path():
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(current_dir, "learning_notes.json")
    
    @staticmethod
    def save_translation_record(original_text, translation, important_words, grammar_points):
        try:
            notes_path = NotesManager.get_notes_path()
            
            if os.path.exists(notes_path):
                with open(notes_path, 'r', encoding='utf-8') as f:
                    notes_data = json.load(f)
            else:
                notes_data = {"records": []}
            
            existing_record = None
            for record in notes_data["records"]:
                if record.get("original_text", "").strip() == original_text.strip():
                    existing_record = record
                    break
            
            if existing_record:
                print(f"发现重复句子，更新现有记录: {original_text[:50]}...")
                
                existing_record["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                existing_record["date"] = datetime.now().strftime("%Y-%m-%d")
                existing_record["learn_count"] = existing_record.get("learn_count", 1) + 1
                
                existing_words = existing_record.get("important_words", {})
                for word, meaning in important_words.items():
                    if word not in existing_words:
                        existing_words[word] = meaning
                    else:
                        if isinstance(meaning, dict) and isinstance(existing_words[word], dict):
                            if meaning != existing_words[word]:
                                existing_words[word] = meaning
                        elif isinstance(meaning, str) and isinstance(existing_words[word], str):
                            if meaning != existing_words[word] and meaning not in existing_words[word]:
                                existing_words[word] += f"; {meaning}"
                existing_record["important_words"] = existing_words
                
                existing_grammar = existing_record.get("grammar_points", {})
                for sentence, explanation in grammar_points.items():
                    if sentence not in existing_grammar:
                        existing_grammar[sentence] = explanation
                    else:
                        if isinstance(explanation, str) and isinstance(existing_grammar[sentence], str):
                            if explanation != existing_grammar[sentence] and explanation not in existing_grammar[sentence]:
                                existing_grammar[sentence] += f"\n\n补充：{explanation}"
                existing_record["grammar_points"] = existing_grammar
                
                print(f"已更新重复句子的单词和语法信息，学习次数：{existing_record['learn_count']}")
                
            else:
                new_record = {
                    "id": len(notes_data["records"]) + 1,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "original_text": original_text,
                    "translation": translation,
                    "important_words": important_words,
                    "grammar_points": grammar_points,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "learn_count": 1
                }
                
                notes_data["records"].append(new_record)
                print(f"添加新句子记录: {original_text[:50]}...")
            
            with open(notes_path, 'w', encoding='utf-8') as f:
                json.dump(notes_data, f, ensure_ascii=False, indent=2)
            
            print(f"翻译记录已保存到笔记文件")
            return True
            
        except Exception as e:
            print(f"保存翻译记录失败: {e}")
            return False
    
    @staticmethod
    def load_all_records():
        try:
            notes_path = NotesManager.get_notes_path()
            if os.path.exists(notes_path):
                if os.path.getsize(notes_path) == 0:
                    print(f"笔记文件为空，初始化默认结构: {notes_path}")
                    default_data = {"records": []}
                    with open(notes_path, 'w', encoding='utf-8') as f:
                        json.dump(default_data, f, ensure_ascii=False, indent=2)
                    return []
                
                with open(notes_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        print(f"笔记文件内容为空，初始化默认结构")
                        return []
                    
                    notes_data = json.loads(content)
                    return notes_data.get("records", [])
            else:
                print(f"笔记文件不存在，将在首次保存时创建: {notes_path}")
                return []
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            print("尝试备份损坏的文件并创建新文件...")
            try:
                notes_path = NotesManager.get_notes_path()
                backup_path = notes_path + f".backup_{int(time.time())}"
                if os.path.exists(notes_path):
                    shutil.copy2(notes_path, backup_path)
                    print(f"已备份损坏文件到: {backup_path}")
                
                default_data = {"records": []}
                with open(notes_path, 'w', encoding='utf-8') as f:
                    json.dump(default_data, f, ensure_ascii=False, indent=2)
                print("已创建新的笔记文件")
                return []
            except Exception as backup_error:
                print(f"备份和恢复过程失败: {backup_error}")
                return []
        except Exception as e:
            print(f"加载翻译记录失败: {e}")
            return []
    
    @staticmethod
    def delete_record(record_id):
        try:
            notes_path = NotesManager.get_notes_path()
            
            if not os.path.exists(notes_path):
                print(f"笔记文件不存在: {notes_path}")
                return False
            
            with open(notes_path, 'r', encoding='utf-8') as f:
                notes_data = json.load(f)
            
            records = notes_data.get("records", [])
            original_count = len(records)
            
            filtered_records = [record for record in records if record.get("id") != record_id]
            
            if len(filtered_records) == original_count:
                print(f"未找到ID为 {record_id} 的记录")
                return False
            
            notes_data["records"] = filtered_records
            
            with open(notes_path, 'w', encoding='utf-8') as f:
                json.dump(notes_data, f, ensure_ascii=False, indent=2)
            
            print(f"成功删除ID为 {record_id} 的记录")
            return True
            
        except Exception as e:
            print(f"删除记录失败: {e}")
            return False
