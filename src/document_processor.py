import os
import tempfile
from typing import Optional
from pypdf import PdfReader
from docx import Document
import chardet


class DocumentProcessor:
    """处理各种格式的文档，提取文本内容"""

    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """从TXT文件提取文本"""
        with open(file_path, "rb") as f:
            raw_data = f.read()
            encoding = chardet.detect(raw_data)["encoding"] or "utf-8"

        with open(file_path, "r", encoding=encoding) as f:
            return f.read()

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """从PDF文件提取文本"""
        text = []
        with open(file_path, "rb") as f:
            pdf_reader = PdfReader(f)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return "\n".join(text)

    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """从Word文档提取文本"""
        doc = Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    def process_uploaded_file(self, uploaded_file) -> Optional[str]:
        """处理上传的文件，返回提取的文本"""
        if uploaded_file is None:
            return None

        # 创建临时文件
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(uploaded_file.name)[1]
        ) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        try:
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()

            if file_ext == ".txt":
                return self.extract_text_from_txt(tmp_path)
            elif file_ext == ".pdf":
                return self.extract_text_from_pdf(tmp_path)
            elif file_ext == ".docx":
                return self.extract_text_from_docx(tmp_path)
            else:
                raise ValueError(f"不支持的文件格式: {file_ext}")
        finally:
            # 清理临时文件
            os.unlink(tmp_path)
