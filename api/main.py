"""
公式识别 API 服务主入口
基于 FastAPI 的独立公式识别服务
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径，以便导入现有模块
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import io
import time

# 导入现有服务
from api.services.formula_ocr_service import FormulaOCRService
from src.handlers.formula_handler import FormulaHandler

# 创建 FastAPI 应用
app = FastAPI(
    title="Formula OCR API",
    description="数学公式识别服务 - 将图片中的公式转换为 LaTeX 和 MathML",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 全局变量
ocr_service = None
formula_handler = None

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化服务"""
    global ocr_service, formula_handler
    print("🚀 正在初始化公式识别 API 服务...")
    
    # 初始化 OCR 服务
    try:
        ocr_service = FormulaOCRService()
        # 提前加载模型，避免第一次请求时延迟
        ocr_service.get_model()
        print("✅ Pix2Tex 模型加载完成")
    except Exception as e:
        print(f"❌ 模型初始化失败: {e}")
        ocr_service = None
    
    # 初始化业务处理器
    formula_handler = FormulaHandler()
    print("✅ 公式识别服务初始化完成")

@app.get("/")
async def root():
    """API 根路径"""
    return {
        "service": "Formula OCR API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "识别公式": "POST /api/v1/formula/recognize",
            "LaTeX转MathML": "POST /api/v1/formula/convert",
            "健康检查": "GET /health"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    # 服务进程存活即返回 healthy，模型加载状态通过 model_loaded 字段体现
    return {
        "status": "healthy",
        "service": "formula-ocr-api",
        "model_loaded": ocr_service is not None,
        "timestamp": time.time()
    }

@app.post("/api/v1/formula/recognize")
async def recognize_formula(image: UploadFile = File(...)):
    """
    识别图片中的数学公式
    
    Args:
        image: 图片文件 (PNG, JPG, JPEG, BMP)
    
    Returns:
        包含 LaTeX 和 MathML 格式的识别结果
    """
    if ocr_service is None or formula_handler is None:
        raise HTTPException(503, "服务暂不可用")
    
    # 验证文件类型
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/bmp"]
    if image.content_type not in allowed_types:
        raise HTTPException(400, f"不支持的文件类型: {image.content_type}")
    
    # 验证文件大小 (限制 10MB)
    if hasattr(image.file, 'size'):
        file_size = image.file.size
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(400, "文件大小超过 10MB 限制")
    
    # 读取图片数据
    try:
        image_data = await image.read()
        if not image_data:
            raise HTTPException(400, "文件内容为空")
    except Exception as e:
        raise HTTPException(400, f"读取文件失败: {str(e)}")
    
    # 记录开始时间
    start_time = time.time()
    
    try:
        # 调用 OCR 识别
        latex_code = ocr_service.recognize_formula(image_data)
        
        if not latex_code:
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "error": "公式识别返回空结果，请确保图片包含清晰的数学公式"
                }
            )
        
        # 转换为 MathML
        mathml_code = formula_handler.convert_latex_to_mathml(latex_code)
        
        # 计算耗时
        elapsed_time = time.time() - start_time
        
        # 返回结果
        result = {
            "success": True,
            "data": {
                "latex": latex_code,
                "mathml": mathml_code,
                "preview": f"${latex_code}$" if latex_code else "",
                "processing_time": round(elapsed_time, 3)
            },
            "metadata": {
                "filename": image.filename,
                "content_type": image.content_type,
                "file_size": len(image_data)
            }
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(500, f"处理失败: {str(e)}")

@app.post("/api/v1/formula/convert")
async def convert_latex_to_mathml(data: dict):
    """
    将 LaTeX 代码转换为 MathML 格式
    
    Args:
        data: JSON 数据，包含 latex 字段
        
    Example:
        {"latex": "x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}"}
    """
    if formula_handler is None:
        raise HTTPException(503, "服务暂不可用")
    
    # 验证输入
    if "latex" not in data:
        raise HTTPException(400, "缺少 'latex' 字段")
    
    latex_code = data["latex"]
    
    if not isinstance(latex_code, str) or not latex_code.strip():
        raise HTTPException(400, "LaTeX 代码不能为空")
    
    try:
        # 转换为 MathML
        mathml_code = formula_handler.convert_latex_to_mathml(latex_code)
        
        return {
            "success": True,
            "data": {
                "latex": latex_code,
                "mathml": mathml_code,
                "preview": f"${latex_code}$"
            }
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": f"转换失败: {str(e)}"
            }
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 启动公式识别 API 服务，监听 {host}:{port}")
    print(f"📄 文档地址: http://{host}:{port}/docs")
    
    uvicorn.run(app, host=host, port=port)