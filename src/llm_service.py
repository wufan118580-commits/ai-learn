import requests
from typing import Optional, Dict, Any

class DeepSeekService:
    """DeepSeek API服务封装"""
    
    BASE_URL = "https://api.deepseek.com/v1/chat/completions"
    # BASE_URL = "https://api.deepseek.com"
    DEFAULT_TIMEOUT = 30  # 30秒超时
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # print('sdfsfs:', self.api_key)
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
    
    def generate(self, prompt: str, max_tokens: int = 8000) -> Optional[str]:
        """调用DeepSeek生成内容"""
        payload: Dict[str, Any] = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一个专业的知识提取助手，擅长从文档中提取关键信息并生成结构化的学习笔记和思维导图。"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            response = self.session.post(
                self.BASE_URL,
                json=payload,
                timeout=self.DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.Timeout as e:
            raise TimeoutError(f"API请求超时: {str(e)}") from e
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"API请求失败: {str(e)}") from e
        except KeyError as e:
            raise ValueError(f"API响应格式错误: {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"生成内容时发生未知错误: {str(e)}") from e
    
    def __del__(self):
        """清理session连接"""
        if hasattr(self, 'session'):
            self.session.close()