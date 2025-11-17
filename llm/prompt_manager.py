class PromptManager:
    
    TRANSLATION_PROMPTS = {
        "初级": """你是一个专业的原神游戏英文翻译助手。请将以下英文文本翻译成中文，并提供适合**初级水平**学习者的详细分析。

                    要求：
                    1. 翻译要准确自然，符合中文表达习惯
                    2. 初级词汇要求：选择3-5个基础且常用的词汇（如基本动词、名词、形容词），避免过于高级的词汇
                    3. 初级语法要求：重点讲解基础语法（如一般现在时、过去时、简单句结构、基本的介词用法等），避免复杂语法
                    4. 重要：如果提供了专有名词对照表，必须严格按照对照表进行翻译，不可使用其他译名

                    英文原文：{text}

                    {special_terms_section}

                    请按照以下JSON格式返回结果：
                    {{
                        "translation": "准确流畅的中文翻译",
                        "important_words": {{
                            "基础单词1": "中文释义、词性、简单例句",
                            "基础单词2": "中文释义、词性、简单例句"
                        }},
                        "important_grammar": {{
                            "基础语法点原句": "简单易懂的语法解释和例句"
                        }}
                    }}
                    必须只返回json的格式,不要有其他回复
                    """,
        
        "中级": """你是一个专业的原神游戏英文翻译助手。请将以下英文文本翻译成中文，并提供适合**中级水平**学习者的详细分析。

                要求：
                1. 翻译要准确自然，符合中文表达习惯
                2. 中级词汇要求：选择4-6个中等难度的词汇（如常用短语动词、中级形容词副词等）
                3. 中级语法要求：重点讲解中等复杂度语法（如完成时态、被动语态、定语从句、状语从句等）
                4. 重要：如果提供了专有名词对照表，必须严格按照对照表进行翻译，不可使用其他译名

                英文原文：{text}

                {special_terms_section}

                请按照以下JSON格式返回结果：
                {{
                    "translation": "准确流畅的中文翻译",
                    "important_words": {{
                        "中级单词1": "中文释义、用法说明、例句",
                        "中级单词2": "中文释义、用法说明、例句"
                    }},
                    "important_grammar": {{
                        "中级语法点原句": "详细的语法解释和例句"
                    }}
                }}
                必须只返回json的格式,不要有其他回复
                """,
        
        "高级": """你是一个专业的原神游戏英文翻译助手。请将以下英文文本翻译成中文，并提供适合高级水平学习者的详细分析。

                要求：
                1. 翻译要准确自然，符合中文表达习惯
                2. 高级词汇要求：选择3-5个高级或不常用的词汇（如高级词汇、习语、专业术语等）
                3. 高级语法要求：重点讲解高级语法（如倒装句、强调句、虚拟语气、复杂从句结构、修辞手法等）
                4. 重要：如果提供了专有名词对照表，必须严格按照对照表进行翻译，不可使用其他译名

                英文原文：{text}

                {special_terms_section}

                请按照以下JSON格式返回结果：
                {{
                    "translation": "准确流畅的中文翻译",
                    "important_words": {{
                        "高级单词1": "深入的中文释义、细微用法区别、高级例句",
                        "高级单词2": "深入的中文释义、细微用法区别、高级例句"
                    }},
                    "important_grammar": {{
                        "高级语法点原句": "深入的语法分析和高级例句"
                    }}
                }}
                必须只返回json的格式,不要有其他回复
                """
    }
    
    OCR_CORRECTION_PROMPT = """你是一个专业的OCR文本修正助手。请修正以下英文文本中可能存在的单词粘连问题（空格缺失）。

                            【原文】
                            {text}

                            **要求：**
                            1. 仔细检查文本中是否有单词粘连在一起的情况（例如 "isattacking" 应该是 "is attacking"）
                            2. 如果发现粘连，请在正确的位置添加空格
                            3. 不要改变文本的原意和其他标点符号
                            4. 如果文本没有任何问题，直接返回原文
                            5. **只返回修正后的英文文本，不要有任何其他说明或解释**

                            修正后的文本：
                            """
    
    DEFAULT_LEVEL = "中级"
    VALID_LEVELS = ["初级", "中级", "高级"]
    
    @classmethod
    def get_translation_prompt(cls, user_level: str = None) -> str:
        """
        获取指定用户水平的翻译提示词模板
        
        Args:
            user_level: 用户英语水平 ("初级", "中级", "高级")
            
        Returns:
            str: 对应水平的提示词模板
        """
        if user_level not in cls.VALID_LEVELS:
            user_level = cls.DEFAULT_LEVEL
        return cls.TRANSLATION_PROMPTS[user_level]
    
    @classmethod
    def format_translation_prompt(cls, text: str, special_terms: dict = None, user_level: str = None) -> str:
        """
        格式化翻译提示词
        
        Args:
            text: 要翻译的英文原文
            special_terms: 专有名词对照表 {英文: 中文}
            user_level: 用户英语水平
            
        Returns:
            str: 格式化后的完整提示词
        """
        special_terms_section = cls._build_special_terms_section(special_terms)
        
        prompt_template = cls.get_translation_prompt(user_level)
        
        return prompt_template.format(
            text=text,
            special_terms_section=special_terms_section
        )
    
    @classmethod
    def format_ocr_correction_prompt(cls, text: str) -> str:
        """
        格式化OCR修正提示词
        
        Args:
            text: 需要修正的OCR文本
            
        Returns:
            str: 格式化后的完整提示词
        """
        return cls.OCR_CORRECTION_PROMPT.format(text=text)
    
    @classmethod
    def _build_special_terms_section(cls, special_terms: dict = None) -> str:
        """
        构建专有名词部分的文本
        
        Args:
            special_terms: 专有名词对照表
            
        Returns:
            str: 格式化的专有名词说明文本
        """
        if not special_terms or len(special_terms) == 0:
            return ""
        
        section = "专有名词对照表（必须严格按照此表翻译）：\n"
        for en_term, zh_term in special_terms.items():
            section += f"- {en_term} → {zh_term}\n"
        section += "\n请务必在翻译中使用上述对照表中的中文译名，不要使用其他译名！"
        
        return section
    
    @classmethod
    def get_all_levels(cls) -> list:
        """返回所有支持的英语水平"""
        return cls.VALID_LEVELS.copy()
    
    @classmethod
    def is_valid_level(cls, level: str) -> bool:
        """检查指定的水平是否有效"""
        return level in cls.VALID_LEVELS
