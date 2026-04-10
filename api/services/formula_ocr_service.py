"""
公式OCR服务 - 用于识别图片中的数学公式并转换为LaTeX格式
"""
import os
import warnings
import time
import torch

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
        self.model_loaded = False
        self.device = None
        self._setup_optimizations()

    def _setup_optimizations(self):
        """设置推理优化参数"""
        if torch.cuda.is_available():
            self.device = torch.device('cuda')
            print("🎯 检测到GPU，使用CUDA加速")
        else:
            self.device = torch.device('cpu')
            # CPU优化：使用物理核心数，避免超线程带来的性能下降
            # logical_cores = os.cpu_count() or 4
            logical_cores = 8
            physical_cores = max(1, logical_cores // 2)  # 估算物理核心数
            torch.set_num_threads(physical_cores)
            torch.set_float32_matmul_precision('medium')  # 平衡精度和速度
            print(f"💻 使用CPU模式，设置线程数: {physical_cores}")

    def get_model(self):
        """懒加载模型，仅加载一次"""
        if not self.model_loaded:
            try:
                from pix2tex.cli import LatexOCR
                print(f"🔧 正在加载Pix2Tex模型...")
                self.model = LatexOCR()
                
                # 设为评估模式
                if hasattr(self.model, 'eval'):
                    self.model.eval()
                
                self.model_loaded = True
                print("✅ 模型加载完成")
                
            except Exception as e:
                print(f"❌ 加载Pix2Tex模型失败: {e}")
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
            start_time = time.time()
            
            # 获取模型（仅第一次调用时加载）
            model = self.get_model()
            
            # 图片预处理
            image = Image.open(io.BytesIO(image_data))
            
            # 模型推理（禁用梯度计算提升性能）
            with torch.no_grad():
                latex_code = model(image)
            
            # 性能统计
            elapsed = time.time() - start_time
            print(f"📊 识别耗时: {elapsed:.3f}秒")
            
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
