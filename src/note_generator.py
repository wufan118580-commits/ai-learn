from llm_service import DeepSeekService

class NoteGenerator:
    """学习笔记生成器（集成知识图谱）"""

    def __init__(self, api_key: str):
        self.deepseek_client = DeepSeekService(api_key)

    def generate_document_notes(self, content: str, filename: str="", ) -> Dict:
        """为单个文档生成学习笔记（包含知识图谱）"""
        print(f"为文档 '{filename}' 生成学习笔记...")

        # 一次API调用生成完整笔记
        notes = self.deepseek_client.generate_comprehensive_notes(
            content=content,
            filename=filename,
        )
        # 后处理结果
        result = {}
        # 1. 格式化单个文档笔记为Markdown
        result['md'] = self._format_document_notes_md(notes)   
        # 2. 获取知识图谱的html格式内容
        mermaid_code = self.extract_mermaid_code(notes.get('knowledge_graph', ''))
        result['html'] = ''
        if mermaid_code:
            # 生成HTML预览
            html_path = os.path.join(output_dir, f"{filename}_graph.html")
            result['html'] = self._generate_mermaid_html(mermaid_code, html_path, f"{notes.get('filename')} 知识图谱")
            
        return result
    def extract_mermaid_code(self, text: str) -> str:
        """从文本中提取Mermaid代码"""
        import re
        # 查找```mermaid```之间的代码
        pattern = r'```mermaid\s*(.*?)\s*```'
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            return matches[0].strip()

        # 如果没有找到标记，查找可能的Mermaid代码
        pattern2 = r'graph\s+[A-Z]{2}\s*(.*?)(?=\n```|\n\n\n|\Z)'
        matches2 = re.findall(pattern2, text, re.DOTALL)

        if matches2:
            return matches2[0].strip()

        return ""

    
    def _format_document_notes_md(self, notes: Dict) -> str:
        """格式化单个文档笔记为Markdown"""
        filename = notes.get('filename', '未知文档')

        md = f"""# 📝 学习笔记: {filename}

## 📋 文档概述
{notes.get('document_overview', '无概述')}

## 🎯 核心概念
"""
        core_concepts = notes.get('core_concepts', [])
        if isinstance(core_concepts, list):
            for concept in core_concepts:
                md += f"- {concept}\n"
        else:
            md += f"{core_concepts}\n"

        md += f"\n## 📚 知识要点\n"
        key_points = notes.get('key_points', [])
        if isinstance(key_points, list):
            for point in key_points:
                md += f"- {point}\n"
        else:
            md += f"{key_points}\n"

        md += f"""
## 🔗 逻辑关系
{notes.get('logical_relationships', '无逻辑关系分析')}

## 💡 学习建议
{notes.get('learning_suggestions', '无学习建议')}

## 🗺️ 知识图谱
{notes.get('knowledge_graph', '```mermaid graph TD  A[知识图谱生成失败]```')}

---
*所属单元: {notes.get('unit', '未知单元')}*  
*生成时间: {notes.get('generated_time', datetime.now().isoformat())}*
"""
        return md

    def _generate_mermaid_html(self, mermaid_code: str, title: str = "知识图谱"):
        """生成Mermaid图表的HTML预览"""
        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .mermaid {{
            background-color: white;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .info {{
            background-color: #e8f4fd;
            padding: 15px;
            border-left: 4px solid #2196F3;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .download-btn {{
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            display: inline-block;
            margin-top: 10px;
        }}
        .download-btn:hover {{
            background-color: #45a049;
        }}
    </style>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }}
        }});
    </script>
</head>
<body>
    <div class="container">
        <h1>📊 {title}</h1>

        <div class="info">
            <strong>💡 使用说明：</strong>
            <ul>
                <li>此图表基于Mermaid生成，展示了知识点的结构和关系</li>
                <li>您可以右键点击图表保存为图片</li>
                <li>图表是交互式的，可以拖动和缩放</li>
            </ul>
        </div>

        <div class="mermaid">
{mermaid_code}
        </div>

        <div>
            <strong>📥 下载选项：</strong><br>
            <a href="#" onclick="downloadAsSVG()" class="download-btn">下载为SVG</a>
            <a href="#" onclick="downloadAsPNG()" class="download-btn">下载为PNG</a>
        </div>
    </div>

    <script>
        function downloadAsSVG() {{
            const svg = document.querySelector('.mermaid svg');
            if (!svg) {{
                alert('请等待图表加载完成');
                return;
            }}

            const serializer = new XMLSerializer();
            const source = serializer.serializeToString(svg);
            const blob = new Blob([source], {{type: 'image/svg+xml'}});
            const url = URL.createObjectURL(blob);

            const a = document.createElement('a');
            a.href = url;
            a.download = 'knowledge_graph.svg';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }}

        function downloadAsPNG() {{
            alert('PNG下载功能需要额外配置，请使用SVG下载或截图保存。');
        }}
    </script>
</body>
</html>'''

        return html_content