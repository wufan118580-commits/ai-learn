"""
翻译和语音生成处理逻辑
"""
from llm_service import DeepSeekService
from tts_service import TTSService


class TranslationHandler:
    """翻译和语音处理器"""

    def __init__(self):
        self.tts_service = TTSService()

    def translate_document(self, text: str, api_key: str):
        """
        翻译文档

        Args:
            text: 文档文本
            api_key: API密钥

        Returns:
            翻译后的中文文本
        """
        llm_service = DeepSeekService(api_key)
        return llm_service.translate_document(text)

    def polish_text(self, text: str, api_key: str, style: str = "social_media"):
        """
        润色文本

        Args:
            text: 要润色的文本
            api_key: API密钥
            style: 润色风格，"social_media" 或 "narrative"

        Returns:
            润色后的文本
        """
        llm_service = DeepSeekService(api_key)
        return llm_service.polish_text(text, style)

    def generate_speech(
        self,
        text: str,
        voice: str,
        rate: str = "+0%",
        pitch: str = "+0Hz"
    ):
        """
        生成语音

        Args:
            text: 要转换的文本
            voice: 语音ID
            rate: 语速调整
            pitch: 音调调整

        Returns:
            音频文件路径
        """
        return self.tts_service.text_to_speech(text, voice, rate=rate, pitch=pitch)

    def get_available_voices(self):
        """获取可用语音列表"""
        return self.tts_service.get_voices()
