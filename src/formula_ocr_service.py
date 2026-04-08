"""
公式OCR服务 - 用于识别图片中的数学公式并转换为LaTeX格式
"""
import os
import warnings

# 在导入OpenCV相关模块之前设置环境变量，禁用GUI功能
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '1'

# 抑制PyCryptodome的弃用警告
warnings.filterwarnings('ignore', category=DeprecationWarning, module='cryptography')

from PIL import Image
import io


class FormulaOCRService:
    """Pix2Tex公式识别服务"""

    def __init__(self):
        self.model = None

    def get_model(self):
        """懒加载模型,节省内存"""
        if self.model is None:
            try:
                from pix2tex.cli import LatexOCR
                self.model = LatexOCR()
            except Exception as e:
                print(f"加载Pix2Tex模型失败: {e}")
                raise RuntimeError(
                    "无法加载Pix2Tex模型。请确保已安装pix2tex包。\n"
                    "安装命令: pip install pix2tex"
                ) from e
        return self.model

    def recognize_formula(self, image_data: bytes) -> str:
        """
        识别图片中的公式

        Args:
            image_data: 图片的二进制数据

        Returns:
            LaTeX格式的公式字符串
        """
        try:
            model = self.get_model()
            image = Image.open(io.BytesIO(image_data))
            latex_code = model(image)
            return latex_code
        except Exception as e:
            print(f"公式识别失败: {e}")
            return None

    def recognize_formula_from_file(self, file_path: str) -> str:
        """
        从文件路径识别公式

        Args:
            file_path: 图片文件路径

        Returns:
            LaTeX格式的公式字符串
        """
        try:
            model = self.get_model()
            latex_code = model(file_path)
            return latex_code
        except Exception as e:
            print(f"公式识别失败: {e}")
            return None
