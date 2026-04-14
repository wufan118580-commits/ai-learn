"""
公式识别 API 客户端
UI 服务通过此客户端调用 API 服务
"""
import os
import requests
import json
from typing import Optional, Dict, Any
from io import BytesIO

class FormulaAPIClient:
    """公式识别 API 客户端"""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        初始化 API 客户端
        
        Args:
            base_url: API 服务地址，默认从环境变量 FORMULA_API_URL 获取
        """
        self.base_url = base_url or os.getenv("FORMULA_API_URL", "http://localhost:8000")
        self.base_url = self.base_url.rstrip("/")
        # 读取 API Key（用于认证）
        self.api_key = os.getenv("API_KEY", "")
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头，包含 API Key 认证信息"""
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers
        
    def health_check(self) -> Dict[str, Any]:
        """检查 API 服务状态"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.json()
        except requests.exceptions.ConnectionError:
            return {"status": "unreachable", "error": "无法连接到 API 服务"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def recognize_formula(self, image_data: bytes, filename: str = "formula.png") -> Dict[str, Any]:
        """
        识别图片中的公式
        
        Args:
            image_data: 图片二进制数据
            filename: 文件名（用于 Content-Disposition）
            
        Returns:
            识别结果字典
        """
        try:
            files = {"image": (filename, image_data, "image/png")}
            response = requests.post(
                f"{self.base_url}/api/v1/formula/recognize",
                files=files,
                headers=self._get_headers(),
                timeout=30  # 模型加载可能需要时间
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"API 错误: {response.status_code} - {response.text}"
                }
                
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "无法连接到公式识别 API 服务"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def convert_latex(self, latex_code: str) -> Dict[str, Any]:
        """
        转换 LaTeX 为 MathML
        
        Args:
            latex_code: LaTeX 公式字符串
            
        Returns:
            转换结果字典
        """
        try:
            data = {"latex": latex_code}
            response = requests.post(
                f"{self.base_url}/api/v1/formula/convert",
                json=data,
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"API 错误: {response.status_code} - {response.text}"
                }
                
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "无法连接到公式识别 API 服务"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def batch_recognize(self, image_data_list: list, filenames: list = None) -> list:
        """
        批量识别公式
        
        Args:
            image_data_list: 图片二进制数据列表
            filenames: 文件名列表（可选）
            
        Returns:
            识别结果列表
        """
        results = []
        for i, image_data in enumerate(image_data_list):
            filename = filenames[i] if filenames else f"formula_{i}.png"
            result = self.recognize_formula(image_data, filename)
            results.append(result)
        
        return results
    
    def is_available(self) -> bool:
        """检查 API 服务是否可用"""
        health = self.health_check()
        return health.get("status") == "healthy"


# 全局客户端实例
_formula_api_client = None

def get_formula_api_client() -> FormulaAPIClient:
    """获取全局 API 客户端实例"""
    global _formula_api_client
    if _formula_api_client is None:
        _formula_api_client = FormulaAPIClient()
    return _formula_api_client


if __name__ == "__main__":
    # 测试客户端
    client = FormulaAPIClient()
    
    print("🔍 检查 API 服务状态...")
    health = client.health_check()
    print(f"服务状态: {health}")
    
    print("\n测试 LaTeX 转换:")
    result = client.convert_latex("E = mc^2")
    print(f"转换结果: {result}")