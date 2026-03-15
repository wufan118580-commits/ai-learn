"""
媒材建议 Tab UI
"""
import streamlit as st


def render_media_tab():
    """渲染媒材建议 Tab"""
    st.markdown("### 🎨 分析媒材建议")

    # 显示当前使用的文本来源
    if st.session_state.translated_text:
        source_info = "✅ 将使用**翻译文本**进行分析"
        st.info(source_info)
    else:
        source_info = "ℹ️ 将使用**原文**进行分析（如需使用翻译文本，请先在「🔊 翻译语音」功能中翻译）"
        st.info(source_info)

    st.markdown("为需要配图的片段提供搜索或AI生成的建议")

    # 如果已上传文档，显示分析按钮
    if st.session_state.uploaded_file:
        analyze_button = st.button(
            "🔍 分析配图建议",
            type="primary",
            use_container_width=True,
            disabled=not st.session_state.get('api_key'),
            key="analyze_media_button"
        )

        # 显示已有的分析结果
        if st.session_state.media_suggestions:
            st.markdown("---")
            st.success(f"✅ 已分析完成，共找到 {len(st.session_state.media_suggestions)} 个配图建议")

            # 重新分析按钮
            col1, _ = st.columns([1, 4])
            with col1:
                if st.button("🔄 重新分析", key="reanalyze_media"):
                    st.session_state.media_suggestions = None
                    st.rerun()

            st.markdown("---")

            # 显示每个建议
            for idx, suggestion in enumerate(st.session_state.media_suggestions, 1):
                render_media_suggestion(idx, suggestion)

        return analyze_button

    else:
        st.warning("⚠️ 请先上传文档")
        return None


def render_media_suggestion(idx: int, suggestion: dict):
    """渲染单个媒材建议"""
    media_type = suggestion.get('media_type', 'search')
    icon = "🔍" if media_type == "search" else "✨"
    type_label = "搜索素材" if media_type == "search" else "AI生成"
    type_color = "#e7f3ff" if media_type == "search" else "#fff4e7"

    with st.container():
        # 标题栏
        st.markdown(f"""
        <div style="background-color: {type_color}; padding: 10px; border-radius: 8px; margin-bottom: 10px;">
            <strong>{icon} 建议 #{idx} - {type_label}</strong>
        </div>
        """, unsafe_allow_html=True)

        # 原文本
        st.markdown("**📝 原文片段：**")
        st.info(suggestion.get('text', ''))

        # 关键词/提示词
        keywords = suggestion.get('keywords', [])
        if media_type == "search":
            st.markdown("**🏷️ 搜索关键词：**")
            if isinstance(keywords, list):
                st.markdown(" - " + "\n - ".join(keywords))
            else:
                st.markdown(f" - {keywords}")

            # 搜索链接
            search_url = f"https://www.google.com/search?tbm=isch&q={keywords[0] if isinstance(keywords, list) else keywords}"
            st.markdown(f"🔗 [在 Google 图片搜索](<{search_url}>)")
        else:
            st.markdown("**🎨 AI生成提示词：**")
            st.code(keywords, language='text')

        # 理由
        st.markdown(f"**💡 理由：** {suggestion.get('reason', '')}")

        st.markdown("---")


def render_media_results():
    """渲染媒材建议结果"""
    st.header("🎨 3. 媒材建议结果")
    st.markdown("---")
    st.success(f"✅ 已分析完成，共找到 {len(st.session_state.media_suggestions)} 个配图建议")

    # 重新分析按钮
    col1, _ = st.columns([1, 4])
    with col1:
        if st.button("🔄 重新分析", key="reanalyze_media_result"):
            st.session_state.media_suggestions = None
            st.rerun()

    st.markdown("---")

    # 显示每个建议
    for idx, suggestion in enumerate(st.session_state.media_suggestions, 1):
        render_media_suggestion(idx, suggestion)

    st.markdown("---")
