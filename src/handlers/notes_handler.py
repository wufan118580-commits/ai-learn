"""
学习笔记生成处理逻辑
"""
from note_generator import NoteGenerator


class NotesHandler:
    """学习笔记处理器"""

    def generate_notes(self, prompt: str, filename: str, api_key: str):
        """
        生成学习笔记

        Args:
            prompt: 提示词
            filename: 文件名
            api_key: API密钥

        Returns:
            生成的学习笔记结果
        """
        note_generator = NoteGenerator(api_key)
        return note_generator.generate_document_notes(prompt, filename)
