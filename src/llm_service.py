
from openai import OpenAI
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://api.deepseek.com").rstrip('/')
DEEPSEEK_MODEL = os.getenv("MODEL_NAME", "deepseek-chat")


class DeepSeekService:
    """DeepSeek API服务封装"""

    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API Key 不能为空")

        self.client = OpenAI(
            api_key=api_key,
            base_url=BASE_URL
        )

    def generate_comprehensive_notes(self, prompt: str, max_tokens: int = 8000, filename: str = "") -> dict:
        try:
            response = self.client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system",
                     "content": "你是一位专业的学习导师和知识可视化专家，擅长生成结构化的学习内容和可视化的知识图谱。请始终以JSON格式返回结果。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )

            result = response.choices[0].message.content
            notes_data = json.loads(result)

            # 添加元数据
            notes_data["filename"] = filename
            notes_data["generated_time"] = datetime.now().isoformat()

            # 确保knowledge_graph字段存在
            if "knowledge_graph" not in notes_data:
                notes_data["knowledge_graph"] = self._generate_default_mermaid(notes_data.get("core_concepts", []))

            return notes_data

        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return self._create_fallback_notes(filename)
        except Exception as e:
            print(f"生成学习笔记失败: {e}")
            return None
    def _generate_default_mermaid(self, concepts: list[str]) -> str:
        """生成默认的Mermaid图谱"""
        # 提取概念名称
        concept_names = []
        for concept in concepts[:8]:  # 最多8个概念
            if ':' in concept:
                concept_names.append(concept.split(':')[0].strip())
            else:
                concept_names.append(concept.strip())

        # 生成简单的Mermaid代码
        mermaid_code = "```mermaid\ngraph TD\n"
        if concept_names:
            # 第一个节点作为中心
            mermaid_code += f"  A[{concept_names[0]}]\n"

            # 其他节点连接到中心
            for i, concept in enumerate(concept_names[1:], start=2):
                mermaid_code += f"  {chr(64 + i)}[{concept}]\n"
                mermaid_code += f"  A --> {chr(64 + i)}\n"

        mermaid_code += "```"
        return mermaid_code 
    
    def _create_fallback_notes(self, filename: str,) -> dict:
        """创建备用的学习笔记"""
        return {
            "filename": filename,
            "document_overview": f"【文档概述】{filename} 的学习内容",
            "core_concepts": ["主要概念"],
            "key_points": ["请查看原始文档获取详细信息"],
            "logical_relationships": "逻辑关系待分析",
            "learning_suggestions": "建议直接阅读原文并做笔记",
            "knowledge_graph": self._generate_default_mermaid(["核心概念"]),
            "generated_time": datetime.now().isoformat()
        }

    def translate_to_chinese(self, text: str, source_language: str = "auto") -> str:
        """将文本翻译成中文"""
        prompt = f"""请将以下文本翻译成中文：

    原文语言: {source_language}
    原文内容:
    {text[:20000]}  # 限制输入长度

    要求：
    1. 保持原文的含义和语气
    2. 翻译要自然流畅，符合中文表达习惯
    3. 专业术语请保留或提供合适的中文对应词
    4. 不要添加额外的解释或注释，只返回翻译结果

    翻译结果:"""

        try:
            response = self.client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system",
                     "content": "你是一位专业的翻译助手，擅长将各种语言准确、自然地翻译成中文。请只返回翻译结果，不要添加其他内容。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=6000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"翻译失败: {e}")
            return None

    def translate_document(
        self,
        text: str,
        source_language: str = "auto",
        chunk_size: int = 8000,
        progress_callback=None
    ) -> str:
        """
        将文档翻译成中文（支持长文档分块翻译）

        Args:
            text: 要翻译的文本
            source_language: 源语言，默认为 auto 自动检测
            chunk_size: 每块的最大字符数
            progress_callback: 进度回调函数，参数为 (当前块, 总块数)

        Returns:
            翻译后的中文文本
        """
        # 如果文本较短，直接翻译
        if len(text) <= chunk_size:
            return self.translate_to_chinese(text, source_language)

        # 分块翻译
        chunks = []
        current_pos = 0
        total_chunks = (len(text) + chunk_size - 1) // chunk_size

        while current_pos < len(text):
            chunk = text[current_pos:current_pos + chunk_size]

            # 尝试在句子边界分割
            if current_pos + chunk_size < len(text):
                # 查找最近的句号、问号、感叹号
                for separator in ['。', '！', '？', '.', '!', '?', '\n']:
                    last_sep = chunk.rfind(separator)
                    if last_sep > len(chunk) * 0.7:  # 确保不会切得太短
                        chunk = chunk[:last_sep + 1]
                        current_pos += last_sep + 1
                        break
                else:
                    current_pos += chunk_size
            else:
                current_pos += chunk_size

            # 翻译当前块
            translated_chunk = self.translate_to_chinese(chunk, source_language)
            if translated_chunk:
                chunks.append(translated_chunk)
            else:
                # 如果翻译失败，保留原文
                chunks.append(chunk)

            # 调用进度回调
            if progress_callback:
                progress_callback(len(chunks), total_chunks)

        # 合并所有翻译结果
        return ''.join(chunks)