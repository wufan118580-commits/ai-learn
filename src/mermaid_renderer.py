import streamlit as st
import streamlit.components.v1 as components

def render_mermaid(mermaid_code: str, height: int = 400):
    """
    使用HTML组件渲染Mermaid图表
    """
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <title>知识图谱</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({{startOnLoad: true}});</script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .mermaid {{ background-color: white; padding: 20px; }}
    </style>
</head>
<body>
    <h1>知识图谱</h1>
    <div class="mermaid">
{mermaid_code}
    </div>
</body>
</html>"""
    
    # 使用components.html渲染HTML
    components.html(html_template, height=height)

# 可选：提供一个备用渲染方法（使用纯markdown）
def render_mermaid_markdown(mermaid_code: str):
    """
    使用markdown渲染Mermaid（Streamlit原生支持）
    """
    st.markdown(f"```mermaid\n{mermaid_code}\n```")