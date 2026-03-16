"""
学习笔记 Tab UI
"""
import streamlit as st
import os
from streamlit_mermaid import st_mermaid
import re


def render_notes_tab():
    """渲染学习笔记 Tab"""
    st.markdown("### 📚 生成学习笔记和思维导图")
    st.info("将文档转换为结构化的学习笔记和可视化思维导图")

    generate_button = st.button(
        "🚀 生成学习笔记和思维导图",
        type="primary",
        use_container_width=True,
        disabled=not (st.session_state.get('uploaded_file') and st.session_state.get('api_key')),
        key="generate_notes_button"
    )

    return generate_button


def render_notes_results(result, uploaded_file_name):
    """渲染学习笔记结果"""
    st.header("📊 3. 学习笔记结果")
    st.markdown("---")

    # 初始化编辑状态
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
    if 'edited_notes' not in st.session_state:
        st.session_state.edited_notes = None

    # 显示标题建议
    if 'suggested_titles' in result and result['suggested_titles']:
        st.markdown("### 📌 标题建议")
        st.info("💡 以下是基于文档内容生成的标题建议，您可以选择一个作为学习笔记的标题")
        for i, title in enumerate(result['suggested_titles'], 1):
            st.markdown(f"**{i}.** {title}")
        st.markdown("---")

    # 创建结果显示区域
    result_tabs = st.tabs(["📖 学习笔记", "🧠 思维导图", "📝 完整输出"])

    with result_tabs[0]:
        st.markdown("### 📖 学习笔记")

        # 添加下载和编辑按钮
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.download_button(
                label="📥 下载学习笔记 (MD)",
                data=st.session_state.edited_notes if st.session_state.edited_notes else result['md'],
                file_name=f"{os.path.splitext(uploaded_file_name)[0]}_学习笔记.md",
                mime="text/markdown",
                key=f"download_notes_{uploaded_file_name}"
            )
        with col2:
            if st.button("✏️ 编辑笔记" if not st.session_state.edit_mode else "👁️ 查看预览", key="toggle_edit"):
                st.session_state.edit_mode = not st.session_state.edit_mode
                if not st.session_state.edit_mode:
                    st.session_state.edited_notes = st.session_state.get('temp_edited_notes')
                    st.rerun()
        with col3:
            if st.session_state.edit_mode and st.button("💾 保存修改", key="save_notes"):
                st.session_state.edited_notes = st.session_state.get('temp_edited_notes')
                st.session_state.edit_mode = False
                st.success("✅ 已保存修改！")
                st.rerun()

        st.markdown("---")

        # 显示编辑或预览
        if st.session_state.edit_mode:
            st.info("📝 编辑模式：下方文本框中修改内容，点击\"💾 保存修改\"或\"👁️ 查看预览\"来保存")
            edited_content = st.text_area(
                "编辑学习笔记内容",
                value=st.session_state.edited_notes if st.session_state.edited_notes else result['md'],
                height=600,
                key="notes_editor"
            )
            st.session_state.temp_edited_notes = edited_content
        else:
            content_to_show = st.session_state.edited_notes if st.session_state.edited_notes else result['md']
            st.markdown(content_to_show)

    with result_tabs[1]:
        st.markdown("### 🧠 思维导图")
        if result.get('html'):
            st.markdown("### 📊 交互式思维导图")
            st.info("💡 点击下方按钮下载HTML文件，用浏览器打开查看交互式思维导图")

            if 'html_path' in result and os.path.exists(result['html_path']):
                with open(result['html_path'], 'r', encoding='utf-8') as f:
                    html_content = f.read()

                st.download_button(
                    label="📥 下载思维导图HTML文件",
                    data=html_content,
                    file_name=os.path.basename(result['html_path']),
                    mime="text/html",
                    key=f"download_html_{uploaded_file_name}"
                )

                st.markdown("""
                **使用说明：**
                1. 点击上方按钮下载HTML文件
                2. 用浏览器打开下载的HTML文件
                3. 可以在页面中查看、缩放、拖动思维导图
                4. 支持导出为SVG格式
                """)
            else:
                st.warning("⚠️ HTML文件未找到，尝试直接渲染...")
                mermaid_code = extract_mermaid_code(result.get('md', ''))
                if mermaid_code:
                    cleaned_code = clean_mermaid_code(mermaid_code)
                    st_mermaid(cleaned_code, height="600px")
                else:
                    st.error("❌ 未找到有效的Mermaid代码")
        else:
            st.info("📝 暂无思维导图内容")

    with result_tabs[2]:
        st.markdown("### 📝 完整输出")
        st.markdown(result.get('md', '无内容'))


def extract_mermaid_code(text: str) -> str:
    """从文本中提取Mermaid代码"""
    pattern = r'```mermaid\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    return matches[0] if matches else ""


def clean_mermaid_code(code: str) -> str:
    """清理Mermaid代码中的非法字符"""
    import html as html_module

    cleaned_code = code.strip()
    cleaned_code = html_module.unescape(cleaned_code)
    cleaned_code = re.sub(r'<[^>]+>', '', cleaned_code)

    # 清理中文标点和特殊符号
    illegal_chars = "，；、。；：、。；：？【】《》\"'（）()～~►▼▲★●▪"
    for char in illegal_chars:
        cleaned_code = cleaned_code.replace(char, '')

    lines = [line for line in cleaned_code.split('\n') if line.strip()]
    return '\n'.join(lines)
