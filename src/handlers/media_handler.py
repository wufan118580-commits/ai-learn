"""
媒材建议分析处理逻辑
"""
from llm_service import DeepSeekService


class MediaHandler:
    """媒材建议处理器"""

    def analyze_media_suggestions(self, text: str, api_key: str):
        """
        分析媒材建议

        Args:
            text: 文档原文（支持中英文）
            api_key: API密钥

        Returns:
            媒材建议列表
        """
        llm_service = DeepSeekService(api_key)
        return llm_service.analyze_media_suggestions(text)
