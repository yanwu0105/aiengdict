"""
AI Dictionary Prompts Configuration
"""

# Chinese word lookup prompt
CHINESE_PROMPT = """請提供中文詞彙「{word}」的詳細解釋，包括：
1. 英文翻譯
2. 詞性
3. 詳細定義
4. 使用例句（中英對照）

請以清晰易懂的格式回答。"""

# English word lookup prompt
ENGLISH_PROMPT = """Please provide a detailed explanation for the English word "{word}", including:
1. Chinese translation
2. Part of speech
3. Detailed definition
4. Example sentences (with Chinese translation)

Please format the response clearly."""

# Alternative prompts for testing
CHINESE_PROMPT_DETAILED = """
 將該單詞翻譯成英文。
• 提供其英文翻譯的詞性 (例如: [noun], [verb], [adjective], [adverb] 等)。
• 用簡單、基礎的英文單詞提供英文解釋，讓初學者能看懂。
• 如果其英文翻譯是動詞，請提供常見的時態變化：原形 (base form)、過去式 (past tense)、過去分詞 (past participle)、現在分詞 (present participle) 和第三人稱單數 (third person singular)。
• 列出3到5個常見的英文同義詞，詞性需與翻譯的英文單詞相同。
• 提供三個使用該英文單詞的簡單例句 (選填，但有助於理解)。
-
輸出格式:
【單詞】: [中文單詞]
【英文翻譯】: [English Translation]
【詞性】: [Part of Speech]
【英文解釋】: [Simple English Definition]
【時態變化】: [base form], [past tense], [past participle], [present participle], [third person singular] (僅在單詞為動詞時提供)
【同義詞】: [Synonyms]
【例句】: [Example Sentences] [Chinese Translation]
-
請提供中文詞彙「{word}」的詳細解釋
"""

ENGLISH_PROMPT_DETAILED = """
You are an expert English-Traditional Chinese translation assistant. Follow the specific rules based on the input type:

English Word Translation and Explanation
(When the input is a single English word)
    • Translate the word into Traditional Chinese.
    • Provide an English definition using only simple, common words that a basic English learner can understand.
    • Identify the part of speech (e.g., [noun], [verb], [adjective], [adverb], etc.).
    • If the word is a verb, provide common tense forms: base form, past tense, past participle, present participle, and third person singular.
    • List 3 to 5 common English synonyms, matching the same part of speech.
    • Provide three simple example sentence using the word in context (optional but encouraged for clarity).
-
Output format:
【Word】: [English Word]
【詞性】: [Part of Speech]
【中文翻譯】: [Traditional Chinese Translation]
【英文解釋】: [Simple English Definition]
【時態變化】: [base form], [past tense], [past participle], [present participle], [third person singular] （Only include if the word is a verb)
【同義詞】: [Synonyms]
【例句】: [Example Sentence] [Chinese Translation]
-
Please provide a detailed explanation for the English word "{word}"
"""


# Prompt selection function
def get_prompt(language: str, style: str = "standard") -> str:
    """
    Get prompt based on language and style

    Args:
        language: 'chinese' or 'english'
        style: 'standard' or 'detailed'

    Returns:
        Formatted prompt string
    """
    prompts = {
        "chinese": {"standard": CHINESE_PROMPT, "detailed": CHINESE_PROMPT_DETAILED},
        "english": {"standard": ENGLISH_PROMPT, "detailed": ENGLISH_PROMPT_DETAILED},
    }

    return prompts.get(language, {}).get(style, CHINESE_PROMPT)
