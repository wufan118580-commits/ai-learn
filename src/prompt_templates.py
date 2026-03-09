from typing import List, Optional

class PromptManager:
    """管理提示词模板"""
    
    DEFAULT_TEMPLATES = {
        "学习笔记": """请基于以下学习材料，生成一份完整的学习笔记，包含详细的知识梳理和Mermaid格式的知识图谱：
内容长度: {content_length} 字符

学习材料内容:
{document_text}

请按照以下结构生成学习笔记：

## 第一部分：知识梳理
1. 【文档概述】用一段话简要说明本文档的核心内容
2. 【核心概念】列出重要的概念或术语，每个概念简要解释
3. 【知识要点】详细说明关键知识点，分点阐述
4. 【逻辑关系】描述知识点之间的关联和逻辑结构
5. 【学习建议】针对本文档的学习方法和注意事项

## 第二部分：知识图谱（Mermaid格式）
基于上面的知识梳理，生成一个Mermaid流程图来可视化知识结构。

要求：
1. 图谱要体现主要概念和它们之间的关系
2. 使用适当的节点形状和连接线
3. 包含清晰的层次结构
4. Mermaid代码要放在单独的代码块中

## 输出格式
请以JSON格式返回，包含以下字段：
{{
    "document_overview": "文档概述",
    "core_concepts": ["概念1: 解释", "概念2: 解释", ...],
    "key_points": ["要点1", "要点2", ...],
    "logical_relationships": "逻辑关系描述",
    "learning_suggestions": "学习建议",
    "knowledge_graph": "```mermaid\\ngraph TD\\n  A[概念1] --> B[概念2]\\n  ...\\n```"
}}

请确保knowledge_graph字段包含完整的Mermaid代码块（包括```mermaid```标记）。"""
    }
    
    def __init__(self):
        self.templates = self.DEFAULT_TEMPLATES.copy()
    
    def get_template_names(self) -> List[str]:
        """获取所有模板名称"""
        return list(self.templates.keys())
    
    def get_template(self, name: str) -> str:
        """获取指定模板"""
        return self.templates.get(name, "")
    
    def add_template(self, name: str, template: str) -> None:
        """添加自定义模板"""
        self.templates[name] = template
    
    def format_prompt(self, template_name: str, document_text: str, custom_prompt: Optional[str] = None) -> str:
        """格式化提示词"""
        if custom_prompt:
            # 使用自定义提示词
            return custom_prompt.replace("{document_text}", document_text)
        # 使用内置模板
        template = self.get_template(template_name)
        return template.format(document_text=document_text, content_length=len(document_text))