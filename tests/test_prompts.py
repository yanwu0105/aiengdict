"""
Tests for prompts.py module
"""

from prompts import (
    CHINESE_PROMPT,
    ENGLISH_PROMPT,
    CHINESE_PROMPT_DETAILED,
    ENGLISH_PROMPT_DETAILED,
    get_prompt,
)


class TestPromptConstants:
    """Test prompt constant definitions"""

    def test_chinese_prompt_exists(self):
        """Test that Chinese prompt is defined and not empty"""
        assert CHINESE_PROMPT is not None
        assert len(CHINESE_PROMPT.strip()) > 0
        assert "{word}" in CHINESE_PROMPT

    def test_english_prompt_exists(self):
        """Test that English prompt is defined and not empty"""
        assert ENGLISH_PROMPT is not None
        assert len(ENGLISH_PROMPT.strip()) > 0
        assert "{word}" in ENGLISH_PROMPT

    def test_chinese_detailed_prompt_exists(self):
        """Test that detailed Chinese prompt is defined and not empty"""
        assert CHINESE_PROMPT_DETAILED is not None
        assert len(CHINESE_PROMPT_DETAILED.strip()) > 0
        assert "{word}" in CHINESE_PROMPT_DETAILED

    def test_english_detailed_prompt_exists(self):
        """Test that detailed English prompt is defined and not empty"""
        assert ENGLISH_PROMPT_DETAILED is not None
        assert len(ENGLISH_PROMPT_DETAILED.strip()) > 0
        assert "{word}" in ENGLISH_PROMPT_DETAILED


class TestGetPromptFunction:
    """Test get_prompt function"""

    def test_get_chinese_standard_prompt(self):
        """Test getting Chinese standard prompt"""
        result = get_prompt("chinese", "standard")
        assert result == CHINESE_PROMPT

    def test_get_chinese_detailed_prompt(self):
        """Test getting Chinese detailed prompt"""
        result = get_prompt("chinese", "detailed")
        assert result == CHINESE_PROMPT_DETAILED

    def test_get_english_standard_prompt(self):
        """Test getting English standard prompt"""
        result = get_prompt("english", "standard")
        assert result == ENGLISH_PROMPT

    def test_get_english_detailed_prompt(self):
        """Test getting English detailed prompt"""
        result = get_prompt("english", "detailed")
        assert result == ENGLISH_PROMPT_DETAILED

    def test_get_prompt_invalid_language(self):
        """Test getting prompt with invalid language returns fallback"""
        result = get_prompt("invalid", "standard")
        assert result == CHINESE_PROMPT

    def test_get_prompt_invalid_style(self):
        """Test getting prompt with invalid style returns fallback"""
        result = get_prompt("chinese", "invalid")
        assert result == CHINESE_PROMPT

    def test_get_prompt_both_invalid(self):
        """Test getting prompt with both invalid parameters"""
        result = get_prompt("invalid", "invalid")
        assert result == CHINESE_PROMPT


class TestPromptFormatting:
    """Test prompt formatting with word substitution"""

    def test_chinese_prompt_formatting(self):
        """Test Chinese prompt can be formatted with word"""
        prompt = get_prompt("chinese", "standard")
        formatted = prompt.format(word="測試")
        assert "測試" in formatted
        assert "{word}" not in formatted

    def test_english_prompt_formatting(self):
        """Test English prompt can be formatted with word"""
        prompt = get_prompt("english", "standard")
        formatted = prompt.format(word="test")
        assert "test" in formatted
        assert "{word}" not in formatted

    def test_detailed_prompts_formatting(self):
        """Test detailed prompts can be formatted with word"""
        chinese_detailed = get_prompt("chinese", "detailed")
        english_detailed = get_prompt("english", "detailed")

        chinese_formatted = chinese_detailed.format(word="學習")
        english_formatted = english_detailed.format(word="learning")

        assert "學習" in chinese_formatted
        assert "learning" in english_formatted
        assert "{word}" not in chinese_formatted
        assert "{word}" not in english_formatted


class TestPromptContent:
    """Test prompt content quality"""

    def test_chinese_prompt_contains_key_elements(self):
        """Test Chinese prompt contains expected elements"""
        prompt = CHINESE_PROMPT
        expected_elements = ["英文翻譯", "詞性", "定義", "例句"]

        for element in expected_elements:
            assert element in prompt, f"Missing element: {element}"

    def test_english_prompt_contains_key_elements(self):
        """Test English prompt contains expected elements"""
        prompt = ENGLISH_PROMPT
        expected_elements = [
            "Chinese translation",
            "Part of speech",
            "definition",
            "Example sentences",
        ]

        for element in expected_elements:
            assert element in prompt, f"Missing element: {element}"

    def test_detailed_prompts_more_comprehensive(self):
        """Test that detailed prompts are more comprehensive than standard ones"""
        chinese_standard = get_prompt("chinese", "standard")
        chinese_detailed = get_prompt("chinese", "detailed")
        english_standard = get_prompt("english", "standard")
        english_detailed = get_prompt("english", "detailed")

        # Detailed prompts should be longer
        assert len(chinese_detailed) > len(chinese_standard)
        assert len(english_detailed) > len(english_standard)
