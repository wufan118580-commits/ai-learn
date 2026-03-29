"""公式识别处理器 - 处理公式识别业务逻辑"""
import os
import json
from datetime import datetime
from pathlib import Path
from latex2mathml.converter import convert as latex_to_mathml


class FormulaHandler:
    """公式识别处理器"""

    def __init__(self, storage_dir: str = "formula_history"):
        self.storage_dir = storage_dir
        self.metadata_file = os.path.join(storage_dir, "metadata.json")

        # 确保存储目录存在
        os.makedirs(storage_dir, exist_ok=True)

        # 初始化元数据文件
        self._init_metadata()

    def _init_metadata(self):
        """初始化元数据文件"""
        if not os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def _load_metadata(self) -> list:
        """加载元数据"""
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载元数据失败: {e}")
            return []

    def _save_metadata(self, metadata: list):
        """保存元数据"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存元数据失败: {e}")

    def convert_latex_to_mathml(self, latex_code: str) -> str:
        """
        将LaTeX代码转换为MathML格式

        Args:
            latex_code: LaTeX代码

        Returns:
            MathML代码字符串
        """
        try:
            # 转换为MathML (latex2mathml已经包含math标签)
            mathml_code = latex_to_mathml(latex_code)

            # 检查是否已经包含math标签，如果有则直接返回
            if '<math' in mathml_code:
                return mathml_code

            # 如果没有math标签，则包装
            return f'<math xmlns="http://www.w3.org/1998/Math/MathML">{mathml_code}</math>'

        except Exception as e:
            print(f"LaTeX转MathML失败: {e}")
            return None
