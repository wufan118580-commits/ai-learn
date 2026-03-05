import pytest
import tempfile
import os
from src.document_processor import DocumentProcessor


def test_extract_text_from_txt():
    """测试TXT文本提取"""
    processor = DocumentProcessor()

    # 创建测试文件
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("测试文本内容")
        tmp_path = f.name

    try:
        text = processor.extract_text_from_txt(tmp_path)
        assert text == "测试文本内容"
    finally:
        os.unlink(tmp_path)


def test_process_unsupported_file():
    """测试不支持的文件格式"""
    processor = DocumentProcessor()

    # 模拟上传文件对象
    class MockUploadedFile:
        name = "test.unsupported"

        def getvalue(self):
            return b"test"

    with pytest.raises(ValueError):
        processor.process_uploaded_file(MockUploadedFile())
