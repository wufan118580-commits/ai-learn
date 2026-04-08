"""
公式识别页面 - 识别图片中的数学公式并转换为LaTeX格式
"""
import streamlit as st
import os
import time


def render_formula_tab():
    """渲染公式识别页面"""
    st.title("📐 公式识别")
    st.markdown("上传包含数学公式的截图,自动转换为LaTeX格式")

    # 添加使用说明
    with st.expander("💡 使用说明", expanded=False):
        st.markdown("""
        **功能说明:**
        - 上传包含数学公式的图片(PNG、JPG、JPEG、BMP格式)
        - 自动识别并转换为LaTeX和MathML格式
        - 支持预览渲染效果和复制代码

        **导出格式说明:**
        - **LaTeX代码**: 用于LaTeX文档、Markdown、Jupyter Notebook等
        - **MathML代码**: 可直接复制到Word中使用,支持粘贴后自动转换为可编辑公式

        **注意事项:**
        - 首次使用时需要下载识别模型(约500MB),请耐心等待
        - 图片质量越高,识别准确度越好
        - 建议使用清晰的手写公式或印刷体公式
        - 复杂公式可能需要较长的识别时间

        **优化建议:**
        - 图片中的公式尽量居中且清晰
        - 避免背景过于复杂
        - 建议使用白底黑字的公式图片

        **Word中使用MathML:**
        1. 点击"复制MathML代码"或下载MathML文件
        2. 在Word中按 Ctrl+V 粘贴
        3. 公式会自动转换为Word可编辑的公式格式
        """)

    st.markdown("---")

    # 初始化 API 客户端
    if 'formula_api_client' not in st.session_state:
        from api_client import FormulaAPIClient
        st.session_state.formula_api_client = FormulaAPIClient()
    
    # 检查 API 服务状态
    api_status = st.session_state.formula_api_client.health_check()
    if api_status.get("status") != "healthy":
        st.warning(f"⚠️ 公式识别 API 服务不可用: {api_status.get('error', '未知错误')}")
        st.info("请确保 API 服务已启动，或切换到本地模式")
        
        # 备用：本地处理器（如果 API 不可用）
        if 'formula_handler' not in st.session_state:
            from handlers.formula_handler import FormulaHandler
            st.session_state.formula_handler = FormulaHandler()
        use_api = False
    else:
        use_api = True

    # 初始化状态
    if 'formula_result' not in st.session_state:
        st.session_state.formula_result = None

    # 文件上传
    uploaded_file = st.file_uploader(
        "📤 选择图片",
        type=['png', 'jpg', 'jpeg', 'bmp'],
        help="支持PNG、JPG、JPEG、BMP格式",
        key="formula_upload"
    )

    if uploaded_file:
        # 显示图片预览
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📷 原始图片")
            st.image(uploaded_file)

            # 显示文件信息
            file_size = len(uploaded_file.getvalue()) / 1024
            st.caption(f"文件名: {uploaded_file.name} | 大小: {file_size:.1f} KB")

        # 识别按钮
        with col2:
            st.subheader("🔍 识别结果")
            if st.button("🚀 识别公式", type="primary", key="recognize_formula_button"):
                with st.spinner("正在识别公式..."):
                    start_time = time.time()

                    # 读取图片数据
                    image_data = uploaded_file.read()
                    
                    # 根据 API 状态选择处理方式
                    if use_api:
                        # 调用 API 服务
                        result = st.session_state.formula_api_client.recognize_formula(
                            image_data, 
                            uploaded_file.name
                        )
                    else:
                        # 本地处理（备用）
                        result = st.session_state.formula_handler.process_formula_image(uploaded_file)

                    elapsed_time = time.time() - start_time

                    st.session_state.formula_result = result

                    if result.get('success'):
                        st.success(f"✅ 识别成功! (耗时: {elapsed_time:.1f}秒)")
                        # 同步更新可编辑的LaTeX代码
                        st.session_state.editable_latex = result['data']['latex']
                        # 清除文本框的旧值，强制使用新值
                        if 'editable_latex_text' in st.session_state:
                            del st.session_state.editable_latex_text
                    else:
                        st.error(f"❌ {result.get('error', '识别失败')}")

        # 显示识别结果
        if st.session_state.formula_result:
            result = st.session_state.formula_result

            if result['success']:
                st.markdown("---")
                st.subheader("🔍 识别结果验证")

                # 初始化可编辑的LaTeX代码
                if 'editable_latex' not in st.session_state:
                    # 兼容两种结果格式：API格式和本地格式
                    latex = result['data']['latex'] if 'data' in result else result['latex']
                    st.session_state.editable_latex = latex

                # 分两栏显示：左侧LaTeX代码，右侧可视化预览
                col_left, col_right = st.columns([1, 1])

                with col_left:
                    st.markdown("### 📝 LaTeX代码 (可编辑)")

                    # 可编辑的LaTeX文本框
                    edited_latex = st.text_area(
                        "编辑LaTeX代码",
                        value=st.session_state.editable_latex,
                        height=200,
                        key="editable_latex_text",
                        help="可以直接修改LaTeX代码，右侧预览会实时更新"
                    )

                    # 更新session state
                    st.session_state.editable_latex = edited_latex

                    # 重置按钮
                    if st.button("🔄 重置为原始识别结果", key="reset_latex"):
                        # 兼容两种结果格式：API格式和本地格式
                        latex = result['data']['latex'] if 'data' in result else result['latex']
                        st.session_state.editable_latex = latex
                        st.rerun()

                    st.info("💡 提示：可以直接修改上方的LaTeX代码，右侧预览会自动更新")

                with col_right:
                    st.markdown("### 👀 公式预览")

                    # 实时预览
                    try:
                        preview_latex = f"$${st.session_state.editable_latex}$$"
                        st.markdown(preview_latex, unsafe_allow_html=True)

                        # 显示当前使用的代码
                        st.caption("当前预览的LaTeX代码:")
                        st.code(st.session_state.editable_latex, language="latex")
                    except Exception as e:
                        st.error(f"❌ 预览失败: {str(e)}")
                        st.warning("请检查LaTeX语法是否正确")

                st.markdown("---")

                # 显示MathML代码（基于编辑后的LaTeX）
                # 获取原始 LaTeX（兼容两种格式）
                original_latex = result['data']['latex'] if 'data' in result else result['latex']
                
                if st.session_state.editable_latex != original_latex:
                    st.info("⚠️ 注意：您已修改了LaTeX代码，MathML将基于修改后的代码生成")
                    # 重新生成MathML
                    updated_mathml = st.session_state.formula_handler.convert_latex_to_mathml(
                        st.session_state.editable_latex
                    )
                    current_mathml = updated_mathml if updated_mathml else result.get('mathml', '')
                else:
                    # 获取原始 MathML（兼容两种格式）
                    original_mathml = result['data']['mathml'] if 'data' in result else result.get('mathml', '')
                    current_mathml = original_mathml

                # MathML代码显示（折叠）
                with st.expander("🧮 查看MathML代码 (用于Word)", expanded=False):
                    if current_mathml:
                        st.text_area(
                            "MathML代码",
                            current_mathml,
                            height=150,
                            key="formula_mathml_display"
                        )
                        if st.button("📋 复制MathML代码", key="copy_mathml"):
                            st.code(current_mathml)
                            st.toast("✅ 已显示MathML代码,请复制!", icon="✅")
                    else:
                        st.warning("MathML生成失败")

                st.markdown("---")
                st.subheader("📥 导出文件")

                # 操作按钮
                col_export1, col_export2, col_export3 = st.columns(3)

                with col_export1:
                    # 下载LaTeX文件
                    st.download_button(
                        label="📥 下载LaTeX文件",
                        data=st.session_state.editable_latex,
                        file_name=f"{os.path.splitext(result['filename'])[0]}.tex",
                        mime="text/plain",
                        key="download_latex"
                    )

                with col_export2:
                    if current_mathml:
                        # 下载MathML文件
                        st.download_button(
                            label="📥 下载MathML文件",
                            data=current_mathml,
                            file_name=f"{os.path.splitext(result['filename'])[0]}.mathml",
                            mime="application/mathml+xml",
                            key="download_mathml"
                        )

                with col_export3:
                    if current_mathml:
                        # 下载Word兼容的MathML文件
                        word_mathml_content = f"""<html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word'>
<head>
<meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
<title>公式</title>
</head>
<body>
{current_mathml}
</body>
</html>"""
                        st.download_button(
                            label="📥 下载Word文件",
                            data=word_mathml_content,
                            file_name=f"{os.path.splitext(result['filename'])[0]}.html",
                            mime="text/html",
                            key="download_word_html"
                        )

                # 下载Markdown文件
                st.download_button(
                    label="📥 下载Markdown文件",
                    data=f"# 公式识别结果\n\n原始文件: {result['filename']}\n\n识别时间: {result['timestamp']}\n\n## LaTeX代码\n\n```\n{st.session_state.editable_latex}\n```\n\n## MathML代码\n\n```xml\n{current_mathml}\n```\n\n## 预览\n\n$${st.session_state.editable_latex}$$\n",
                    file_name=f"{os.path.splitext(result['filename'])[0]}_公式.md",
                    mime="text/markdown",
                    key="download_formula_md"
                )

                # 使用说明
                st.markdown("---")
                st.subheader("💡 使用说明")
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.markdown("""
                    **LaTeX代码用途:**
                    - LaTeX文档编辑器
                    - Markdown编辑器
                    - Jupyter Notebook
                    - Markdown格式笔记应用

                    **如何使用:**
                    1. 左侧编辑LaTeX代码
                    2. 右侧实时预览效果
                    3. 确认无误后导出
                    """)
                with col_info2:
                    st.markdown("""
                    **MathML代码用途:**
                    - Microsoft Word (直接粘贴)
                    - 网页开发
                    - 支持MathML的文档编辑器
                    - 电子书制作

                    **📝 Word使用方法:**
                    1. 点击"复制MathML代码"或下载Word文件
                    2. 在Word文档中按 Ctrl+V 粘贴
                    3. 公式会自动转换为Word可编辑的公式
                    4. 可以像普通公式一样编辑
                    """)

            else:
                st.error(f"识别失败: {result['error']}")

    st.markdown("---")

    # 历史记录
    render_formula_history()


def render_formula_history():
    """渲染公式识别历史记录"""
    st.subheader("📜 识别历史")

    # 获取历史记录
    history = st.session_state.formula_handler.get_history(limit=10)

    if not history:
        st.info("📭 暂无识别历史")
        return

    # 显示历史记录
    for i, record in enumerate(history):
        with st.expander(
            f"📅 {record['timestamp'][:19]} - {record.get('filename', 'unknown')}",
            expanded=False
        ):
            col_h1, col_h2, col_h3 = st.columns([3, 1, 1])

            with col_h1:
                st.text_area(
                    "LaTeX代码",
                    record['latex'],
                    height=100,
                    key=f"history_latex_{i}",
                    disabled=True
                )

            with col_h2:
                # 显示图片(如果存在)
                image_path = record.get('image_path')
                if image_path and os.path.exists(image_path):
                    st.image(image_path, width=150)
                else:
                    st.caption("图片已丢失")

            with col_h3:
                st.markdown("**操作**")
                # 复制按钮
                if st.button("📋 复制", key=f"copy_history_{i}"):
                    st.code(record['latex'])
                    st.toast("✅ 已复制!", icon="✅")

                # 删除按钮
                if st.button("🗑️ 删除", key=f"delete_history_{i}"):
                    if st.session_state.formula_handler.delete_history(record['id']):
                        st.toast("✅ 已删除!", icon="✅")
                        st.rerun()
                    else:
                        st.error("删除失败")

    # 清空历史按钮
    st.markdown("---")
    _, col_clear2 = st.columns([10, 1])
    with col_clear2:
        if st.button("🗑️ 清空历史", type="secondary", key="clear_all_history"):
            if st.session_state.get('confirm_clear', False):
                if st.session_state.formula_handler.clear_all_history():
                    st.session_state.formula_result = None
                    st.success("✅ 已清空历史记录")
                    st.rerun()
                else:
                    st.error("清空失败")
