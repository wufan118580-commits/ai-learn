"""
HTML 管理页面 UI
"""
import streamlit as st
import os
from handlers.html_handler import HTMLHandler


def render_html_tab():
    """渲染 HTML 管理页面"""
    st.markdown("### 📄 HTML 静态页面管理")
    st.info("上传、下载和删除 HTML 静态页面")

    # 初始化处理器
    if 'html_handler' not in st.session_state:
        st.session_state.html_handler = HTMLHandler()
        st.session_state.html_handler_initialized = True

    handler = st.session_state.html_handler

    # 创建两个标签：上传管理和已上传列表
    tab1, tab2 = st.tabs(["📤 上传 HTML", "📋 页面列表"])

    with tab2:
        # 显示已上传的页面列表
        html_list = handler.get_html_list()

        # 调试信息
        if st.checkbox("显示调试信息", key="debug_html"):
            st.write(f"存储目录: {handler.storage_dir}")
            st.write(f"元数据文件: {handler.metadata_file}")
            st.write(f"目录存在: {os.path.exists(handler.storage_dir)}")
            st.write(f"元数据文件存在: {os.path.exists(handler.metadata_file)}")
            if os.path.exists(handler.metadata_file):
                import json
                with open(handler.metadata_file, 'r', encoding='utf-8') as f:
                    st.write(f"元数据内容: {json.load(f)}")

    with tab1:
        st.markdown("#### 上传新的 HTML 页面")

        # 文件上传
        uploaded_file = st.file_uploader(
            "选择 HTML 文件",
            type=['html', 'htm'],
            help="支持 .html 和 .htm 格式的文件"
        )

        # 文本输入（直接粘贴 HTML 代码）
        st.markdown("---")
        st.markdown("#### 或者直接粘贴 HTML 代码")
        filename_input = st.text_input("文件名（例如：page.html）", value="index.html")
        html_content = st.text_area(
            "HTML 代码",
            height=400,
            help="粘贴完整的 HTML 代码"
        )

        # 上传按钮
        col1, col2 = st.columns([1, 4])
        with col1:
            upload_button = st.button(
                "📤 上传页面",
                type="primary",
                disabled=(not uploaded_file and not html_content),
                use_container_width=True,
                key="upload_html_button"
            )

        # 处理上传
        if upload_button:
            try:
                file_info = None
                if uploaded_file:
                    # 从文件上传
                    html_data = uploaded_file.getvalue().decode('utf-8')
                    file_info = handler.upload_html(uploaded_file.name, html_data)
                elif html_content and filename_input:
                    # 从文本上传
                    file_info = handler.upload_html(filename_input, html_content)
                else:
                    st.warning("⚠️ 请选择文件或输入 HTML 代码")

                if file_info:
                    st.success(f"✅ 上传成功！文件 ID: {file_info['id']}")
                    st.rerun()

            except Exception as e:
                st.error(f"❌ 上传失败: {str(e)}")

    with tab2:
        # 显示已上传的页面列表
        html_list = handler.get_html_list()

        if not html_list:
            st.info("📭 暂无上传的页面")
        else:
            st.markdown(f"#### 已上传 {len(html_list)} 个页面")

            # 批量操作
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🗑️ 清空所有页面", key="clear_all_html"):
                    if st.session_state.get('confirm_clear', False):
                        handler.clear_all()
                        st.session_state.confirm_clear = False
                        st.success("✅ 已清空所有页面")
                        st.rerun()
                    else:
                        st.session_state.confirm_clear = True
                        st.warning("⚠️ 再次点击确认删除所有页面")

            with col2:
                if st.session_state.get('confirm_clear', False):
                    if st.button("❌ 取消", key="cancel_clear"):
                        st.session_state.confirm_clear = False
                        st.rerun()

            st.markdown("---")

            # 显示每个页面
            for item in html_list:
                with st.expander(f"📄 {item['filename']} (ID: {item['id']})", expanded=False):
                    col1, col2 = st.columns([2, 1])

                    # 显示信息
                    with col1:
                        st.markdown(f"**文件名：** {item['filename']}")
                        st.markdown(f"**上传时间：** {item['upload_time']}")
                        st.markdown(f"**文件大小：** {item['file_size']} 字节")

                        # 下载按钮
                        html_content = handler.get_html_content(item['id'])
                        if html_content:
                            st.download_button(
                                label=f"📥 下载 {item['filename']}",
                                data=html_content,
                                file_name=item['filename'],
                                mime="text/html",
                                key=f"download_{item['id']}"
                            )

                    # 删除按钮
                    with col2:
                        if st.button("🗑️ 删除", key=f"delete_{item['id']}", use_container_width=True):
                            if handler.delete_html(item['id']):
                                st.success(f"✅ 已删除 {item['filename']}")
                                st.rerun()
                            else:
                                st.error("❌ 删除失败")

                    st.markdown("---")
