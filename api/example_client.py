#!/usr/bin/env python3
"""
公式识别 API 客户端示例
"""
import requests
import json
import time
import os

class FormulaAPIClient:
    """公式识别 API 客户端"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
    
    def health_check(self):
        """检查服务状态"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.json()
        except requests.exceptions.ConnectionError:
            return {"status": "unreachable", "error": "无法连接到服务"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def recognize_formula(self, image_path):
        """
        识别图片中的公式
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            识别结果字典
        """
        if not os.path.exists(image_path):
            return {"success": False, "error": f"文件不存在: {image_path}"}
        
        try:
            with open(image_path, "rb") as f:
                files = {"image": (os.path.basename(image_path), f, "image/png")}
                response = requests.post(
                    f"{self.base_url}/api/v1/formula/recognize",
                    files=files,
                    timeout=30  # 模型加载可能需要时间
                )
            
            return response.json()
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def convert_latex(self, latex_code):
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
                timeout=10
            )
            
            return response.json()
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def batch_recognize(self, image_paths):
        """
        批量识别公式（顺序处理）
        
        Args:
            image_paths: 图片文件路径列表
            
        Returns:
            识别结果列表
        """
        results = []
        for i, image_path in enumerate(image_paths):
            print(f"处理图片 {i+1}/{len(image_paths)}: {image_path}")
            result = self.recognize_formula(image_path)
            results.append(result)
            time.sleep(0.5)  # 避免请求过快
        
        return results


def main():
    """客户端示例"""
    client = FormulaAPIClient()
    
    print("🔍 检查服务状态...")
    health = client.health_check()
    print(f"服务状态: {health}")
    
    if health.get("status") != "healthy":
        print("❌ 服务不可用，请先启动 API 服务")
        return
    
    print("\n" + "="*50)
    print("示例 1: LaTeX 转 MathML")
    print("="*50)
    
    latex_examples = [
        "E = mc^2",
        "x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}",
        "\\int_{a}^{b} f(x) dx",
        "\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}"
    ]
    
    for latex in latex_examples:
        print(f"\nLaTeX: {latex}")
        result = client.convert_latex(latex)
        
        if result.get("success"):
            data = result["data"]
            print(f"✅ MathML 长度: {len(data['mathml'])} 字符")
            print(f"预览: {data['preview']}")
        else:
            print(f"❌ 失败: {result.get('error', '未知错误')}")
    
    print("\n" + "="*50)
    print("示例 2: 图片识别（需要图片文件）")
    print("="*50)
    
    # 检查是否有测试图片
    test_images = [
        "test_formula.png",
        "formula.png",
        "example.png",
        "math.png"
    ]
    
    for image_name in test_images:
        if os.path.exists(image_name):
            print(f"\n识别图片: {image_name}")
            result = client.recognize_formula(image_name)
            
            if result.get("success"):
                data = result["data"]
                print(f"✅ 识别成功 (耗时: {data.get('processing_time', 0):.2f}秒)")
                print(f"LaTeX: {data['latex']}")
                print(f"预览: {data['preview']}")
            else:
                print(f"❌ 识别失败: {result.get('error', '未知错误')}")
        else:
            print(f"⚠️  测试图片不存在: {image_name}")
    
    print("\n" + "="*50)
    print("API 使用说明")
    print("="*50)
    print("1. 启动 API 服务: python run.py")
    print("2. 使用 cURL 测试:")
    print("   curl -X POST -F 'image=@formula.png' http://localhost:8000/api/v1/formula/recognize")
    print("3. 访问文档: http://localhost:8000/docs")


if __name__ == "__main__":
    main()