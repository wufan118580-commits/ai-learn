"""
公式识别处理器 - 处理公式识别业务逻辑
"""
import os
import json
from datetime import datetime
from latex2mathml.converter import convert as latex_to_mathml
from formula_ocr_service import FormulaOCRService


class FormulaHandler:
    """公式识别处理器"""

    def __init__(self, storage_dir: str = "formula_history"):
        self.storage_dir = storage_dir
        self.metadata_file = os.path.join(storage_dir, "metadata.json")
        self.ocr_service = FormulaOCRService()

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

    def process_formula_image(self, image_file, save_image: bool = True) -> dict:
        """
        处理上传的公式图片

        Args:
            image_file: Streamlit上传的文件对象
            save_image: 是否保存图片到历史记录

        Returns:
            包含识别结果的字典
        """
        try:
            # 读取图片数据
            image_data = image_file.read()

            # 调用公式识别服务
            latex_code = self.ocr_service.recognize_formula(image_data)

            if not latex_code:
                return {
                    "success": False,
                    "error": "公式识别失败，请检查图片质量",
                    "latex": ""
                }

            # 转换为MathML
            mathml_code = self.convert_latex_to_mathml(latex_code)

            result = {
                "success": True,
                "latex": latex_code,
                "mathml": mathml_code,
                "preview": f"${latex_code}$",
                "filename": image_file.name,
                "file_size": len(image_data),
                "timestamp": datetime.now().isoformat()
            }

            # 保存到历史记录
            if save_image:
                self._save_to_history(image_file, image_data, result)

            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"处理失败: {str(e)}",
                "latex": ""
            }

    def _save_to_history(self, image_file, image_data: bytes, result: dict):
        """保存识别结果到历史记录"""
        try:
            import time
            record_id = f"formula_{int(time.time())}"

            # 保存图片
            image_path = os.path.join(self.storage_dir, f"{record_id}.png")
            with open(image_path, 'wb') as f:
                f.write(image_data)

            # 更新元数据
            metadata = self._load_metadata()
            metadata.append({
                "id": record_id,
                "filename": image_file.name,
                "latex": result.get("latex", ""),
                "timestamp": result.get("timestamp", ""),
                "image_path": image_path
            })

            # 按时间倒序排序(最新的在前)
            metadata.sort(key=lambda x: x["timestamp"], reverse=True)

            # 限制历史记录数量(最多保留50条)
            if len(metadata) > 50:
                # 删除旧记录的图片文件
                old_records = metadata[50:]
                for record in old_records:
                    old_image_path = record.get("image_path")
                    if old_image_path and os.path.exists(old_image_path):
                        os.remove(old_image_path)
                metadata = metadata[:50]

            self._save_metadata(metadata)
        except Exception as e:
            print(f"保存历史记录失败: {e}")

    def get_history(self, limit: int = 10) -> list:
        """
        获取历史记录

        Args:
            limit: 返回记录数量

        Returns:
            历史记录列表
        """
        try:
            metadata = self._load_metadata()
            return metadata[:limit]
        except Exception as e:
            print(f"获取历史记录失败: {e}")
            return []

    def delete_history(self, record_id: str) -> bool:
        """
        删除历史记录

        Args:
            record_id: 记录ID

        Returns:
            是否删除成功
        """
        try:
            metadata = self._load_metadata()

            # 找到并删除记录
            for i, record in enumerate(metadata):
                if record["id"] == record_id:
                    # 删除图片文件
                    image_path = record.get("image_path")
                    if image_path and os.path.exists(image_path):
                        os.remove(image_path)

                    # 从元数据中删除
                    metadata.pop(i)
                    self._save_metadata(metadata)
                    return True

            return False
        except Exception as e:
            print(f"删除历史记录失败: {e}")
            return False

    def clear_all_history(self) -> bool:
        """清空所有历史记录"""
        try:
            metadata = self._load_metadata()

            # 删除所有图片文件
            for record in metadata:
                image_path = record.get("image_path")
                if image_path and os.path.exists(image_path):
                    os.remove(image_path)

            # 清空元数据
            self._save_metadata([])

            return True
        except Exception as e:
            print(f"清空历史记录失败: {e}")
            return False
