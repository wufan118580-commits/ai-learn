
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

    def analyze_media_suggestions(self, text: str) -> list:
        """
        分析文本，为适合配图的片段提供素材建议

        Args:
            text: 要分析的中文文本

        Returns:
            媒体建议列表，每个元素包含：
            - text: 文本片段
            - media_type: 'search' (搜索) 或 'generate' (生成)
            - keywords: 搜索关键词或生成提示词
            - reason: 选择该类型的理由
        """
        prompt = f"""请分析以下中文文本，找出适合搭配图片或视频素材的文本片段，并为每个片段提供素材建议。

原文内容：
{text[:15000]}

分析要求：
1. 只选择那些需要视觉辅助才能更好理解的片段
2. 判断该片段适合：
   - "search": 搜索现成素材（名人、著名建筑、历史事件、已知事物、地理景观等）
   - "generate": AI生成图片（抽象概念、想象场景、未来科技、情感表达、创意插图等）
3. 为每个片段提供：
   - text: 原文本片段（保持原样）
   - media_type: "search" 或 "generate"
   - keywords:
     - 如果是search: 提供2-4个搜索关键词（中英文）
     - 如果是generate: 提供详细的AI生成提示词（中文，包含风格、细节、氛围等）
   - reason: 选择该类型的理由（简短说明）

输出格式（纯JSON，不要包含其他文字）：
{{
  "suggestions": [
    {{
      "text": "文本片段",
      "media_type": "search",
      "keywords": ["关键词1", "keyword2"],
      "reason": "适合搜索的理由"
    }},
    {{
      "text": "文本片段",
      "media_type": "generate",
      "keywords": "详细的英文提示词，描述画面内容、风格、细节等",
      "reason": "适合生成的理由"
    }}
  ]
}}

注意：
- 每个建议的text应该是一个完整的句子或段落，不要太短也不要太长
- 选择5-10个最需要配图的片段
- JSON格式必须正确，可以被直接解析"""

        try:
            response = self.client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system",
                     "content": "你是一位专业的多媒体内容策划师，擅长分析文本并找出需要视觉辅助的内容。请严格按照JSON格式返回结果，不要包含任何其他文字。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )

            result = response.choices[0].message.content
            data = json.loads(result)
            return data.get("suggestions", [])

        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return []
        except Exception as e:
            print(f"分析媒体建议失败: {e}")
            return []

    def polish_text(self, text: str, style: str = "social_media"):
        """
        润色文本，使其更适合传播

        Args:
            text: 要润色的文本
            style: 润色风格，可选 "social_media"（社交媒体）或 "narrative"（叙事）

        Returns:
            润色后的文本
        """
        if style == "social_media":
            prompt = f"""请将以下文本润色成更适合社交媒体传播的风格。

要求：
1. 保持原文的所有观点和科学知识，不得改变核心内容
2. 使用更生动、吸引人的语言
3. 适当加入一些情感表达和互动性语言
4. 优化句子结构，使其朗朗上口，适合朗读
5. 添加一些能引起共鸣的表达方式
6. 控制篇幅，保持简洁有力
7. 使用更贴近大众的语言，避免过于学术化的表达
8. 可以适当使用感叹号、问号等增强语气
9. 保持逻辑清晰，便于理解

原文内容：
{text}

请直接返回润色后的文本，不要包含任何解释或说明。"""

        else:  # narrative
            prompt = f"""请将以下文本润色成更适合叙事的风格。

要求：
1. 保持原文的所有观点和科学知识，不得改变核心内容
2. 使用更具故事性的表达方式
3. 优化句子结构，使文章流畅易读
4. 适当加入一些连接词和过渡语
5. 使用更生动的语言，增强可读性

原文内容：
{text}

请直接返回润色后的文本，不要包含任何解释或说明。"""

        try:
            response = self.client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system",
                     "content": "你是一位专业的文案编辑，擅长将各种文本改写成更适合传播的风格。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=6000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"润色失败: {e}")
            return None