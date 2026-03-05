from typing import List, Optional

class PromptManager:
    """管理提示词模板"""
    
    DEFAULT_TEMPLATES = {
        "学习笔记": """请基于以下文档内容，生成一份结构化的学习笔记。笔记应该包含：
1. 核心概念和定义
2. 主要观点和论点
3. 重要细节和例子
4. 总结和关键 takeaways

文档内容：
{document_text}

请用中文回复，使用markdown格式。""",

        "思维导图": """请基于以下文档内容，生成一个思维导图（Mermaid格式）。思维导图应该：
1. 以文档主题为中心节点
2. 包含主要分支（核心概念、重要观点等）
3. 适当的子分支展示细节

文档内容：
{document_text}

请只返回Mermaid格式的代码，不要有其他解释。使用中文。""",

        "学习笔记+思维导图": """请基于以下文档内容，生成：
1. 结构化的学习笔记
2. Mermaid格式的思维导图

文档内容：
{document_text}

学习笔记要求：
- 核心概念和定义
- 主要观点和论点
- 重要细节和例子

思维导图要求：
- 以主题为中心节点
- 包含主要分支
- 适当的子分支

请用中文回复，先给出学习笔记（使用markdown），然后给出思维导图（使用Mermaid代码块）。"""
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
        return template.format(document_text=document_text)