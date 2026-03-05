import os
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/")
def hello():
    """根路径处理函数"""
    return "Hello World from Python Flask!"


@app.route("/health")
def health_check():
    """健康检查接口"""
    return jsonify(
        {
            "status": "healthy",
            "message": "Python Flask app is running",
            "python_version": os.sys.version,
        }
    )


@app.route("/api/info")
def get_info():
    """获取请求信息"""
    return jsonify(
        {
            "method": request.method,
            "path": request.path,
            "headers": dict(request.headers),
            "args": dict(request.args),
        }
    )


@app.errorhandler(404)
def not_found():
    """404 错误处理"""
    return (
        jsonify(
            {"error": "Not Found", "message": "The requested resource was not found"}
        ),
        404,
    )


@app.errorhandler(500)
def internal_error():
    """500 错误处理"""
    return (
        jsonify({"error": "Internal Server Error", "message": "Something went wrong"}),
        500,
    )


if __name__ == "__main__":
    # 监听所有网络接口的 9000 端口
    app.run(host="0.0.0.0", port=9000, debug=True)
