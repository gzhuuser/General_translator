import re


class FuzzySearchEngine:
    
    @staticmethod
    def levenshtein_distance(s1, s2):
        if len(s1) < len(s2):
            return FuzzySearchEngine.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    @staticmethod
    def calculate_similarity(query, text):
        if not query or not text:
            return 0.0
        
        query_lower = query.lower().strip()
        text_lower = text.lower().strip()
        
        if query_lower == text_lower:
            return 1.0
        
        if query_lower in text_lower:
            return 0.9
        
        if text_lower.startswith(query_lower):
            return 0.8
        
        words = text_lower.split()
        for word in words:
            if word.startswith(query_lower):
                return 0.75
            if query_lower in word:
                return 0.7
        
        max_len = max(len(query_lower), len(text_lower))
        if max_len == 0:
            return 0.0
        
        distance = FuzzySearchEngine.levenshtein_distance(query_lower, text_lower)
        similarity = 1.0 - (distance / max_len)
        
        if len(query_lower) <= 3 and similarity >= 0.5:
            return similarity * 0.6
        elif len(query_lower) <= 6 and similarity >= 0.7:
            return similarity * 0.65
        elif similarity >= 0.8:
            return similarity * 0.6
        
        return 0.0
    
    @staticmethod
    def search_in_record(query, record):
        if not query or not query.strip():
            return 0.0
        
        query_terms = query.lower().split()
        max_score = 0.0
        
        search_fields = [
            (record.get("important_words", {}), 1.0),
            (record.get("original_text", ""), 0.9),
            (record.get("translation", ""), 0.8),
            (record.get("grammar_points", {}), 0.7),
        ]
        
        for field_data, weight in search_fields:
            field_score = 0.0
            
            if isinstance(field_data, dict):
                for key, value in field_data.items():
                    for term in query_terms:
                        key_score = FuzzySearchEngine.calculate_similarity(term, key)
                        value_score = FuzzySearchEngine.calculate_similarity(term, str(value))
                        field_score = max(field_score, key_score, value_score)
            else:
                for term in query_terms:
                    term_score = FuzzySearchEngine.calculate_similarity(term, str(field_data))
                    field_score = max(field_score, term_score)
            
            max_score = max(max_score, field_score * weight)
        
        return max_score
    
    @staticmethod
    def highlight_matches(text, query):
        if not query or not text:
            return text
        
        highlighted_text = text
        query_terms = query.lower().split()
        
        for term in query_terms:
            if len(term) < 2:
                continue
            
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            highlighted_text = pattern.sub(f'<span style="background-color: #ffeb3b; font-weight: bold;">{term}</span>', highlighted_text)
        
        return highlighted_text
