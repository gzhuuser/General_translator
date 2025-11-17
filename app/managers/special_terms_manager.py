import os
import json
import re


class SpecialTermsManager:
    def __init__(self):
        self.terms_dict = {}
        self.is_loaded = False
        self.words_file_path = "./rag/data/words.json"
        
    def load_special_terms(self):
        try:
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            words_file_path = os.path.join(current_dir, "rag", "data", "words.json")
            
            if not os.path.exists(words_file_path):
                print(f"专有名词文件未找到: {words_file_path}")
                return False
            
            with open(words_file_path, 'r', encoding='utf-8') as f:
                words_data = json.load(f)
            
            for item in words_data:
                en_word = item.get("en", "")
                zh_cn = item.get("zhCN", "")
                if en_word and zh_cn:
                    self.terms_dict[en_word] = zh_cn
                    self.terms_dict[en_word.lower()] = zh_cn
                    self.terms_dict[en_word.capitalize()] = zh_cn
                    self.terms_dict[en_word.upper()] = zh_cn
            
            self.is_loaded = True
            print(f"专有名词库加载成功！共 {len(words_data)} 个条目")
            return True
            
        except Exception as e:
            print(f"加载专有名词库失败: {e}")
            return False
    
    def extract_proper_nouns(self, text):
        words = re.findall(r'\b[A-Z][a-z]*(?:[A-Z][a-z]*)*\b', text)
        
        proper_nouns = []
        text_words = text.split()
        
        for word in words:
            is_sentence_start = False
            for i, text_word in enumerate(text_words):
                if word in text_word:
                    if i == 0 or any(punct in text_words[i-1] for punct in '.!?'):
                        is_sentence_start = True
                        break
            
            common_words = {'The', 'This', 'That', 'These', 'Those', 'We', 'You', 'They', 
                          'He', 'She', 'It', 'I', 'My', 'Your', 'His', 'Her', 'Our', 'Their'}
            
            if not is_sentence_start and word not in common_words:
                proper_nouns.append(word)
        
        return list(set(proper_nouns))
    
    def find_matched_terms(self, text):
        if not self.is_loaded:
            return {}
        
        matched_terms = {}
        
        for en_term, zh_term in self.terms_dict.items():
            if en_term[0].isupper() and not any(c.islower() for c in en_term[1:]):
                continue
            if en_term.islower() or en_term.capitalize() != en_term:
                continue
                
            pattern = r'\b' + re.escape(en_term) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                matched_terms[en_term] = zh_term
        
        proper_nouns = self.extract_proper_nouns(text)
        for noun in proper_nouns:
            if noun in self.terms_dict:
                matched_terms[noun] = self.terms_dict[noun]
            elif noun.lower() in self.terms_dict:
                original_form = None
                for key in self.terms_dict.keys():
                    if key.lower() == noun.lower() and key[0].isupper():
                        original_form = key
                        break
                if original_form:
                    matched_terms[original_form] = self.terms_dict[noun.lower()]
        
        return matched_terms
    
    def format_terms_for_llm(self, matched_terms):
        if not matched_terms:
            return ""
        
        terms_text = "专有名词对照表：\n"
        for en_term, zh_term in matched_terms.items():
            terms_text += f"- {en_term} → {zh_term}\n"
        
        return terms_text


special_terms_manager = SpecialTermsManager()
