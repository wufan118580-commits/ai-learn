"""
首页 - 功能导航
"""
import streamlit as st


def render_home_page():
    """渲染首页"""
    st.markdown("""
    <style>
        .feature-card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin: 10px 0;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.2);
            border-color: #6667AB;
        }
        .feature-icon {
            font-size: 48px;
            margin-bottom: 15px;
        }
        .feature-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }
        .feature-desc {
            font-size: 16px;
            color: #666;
            line-height: 1.6;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("📚 文档学习助手")
    st.markdown("---")

    st.markdown("### 选择功能")

    # 功能卡片布局
    col1, col2 = st.columns(2)

    with col1:
        # 文档学习卡片
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📖</div>
            <div class="feature-title">文档学习</div>
            <div class="feature-desc">
                上传文档，AI 自动生成学习笔记、翻译语音和媒材建议
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 开始使用", key="goto_notes", use_container_width=True):
            st.session_state.page = "📚 文档学习"
            st.rerun()

    with col2:
        # HTML 管理卡片
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <div class="feature-title">HTML 管理</div>
            <div class="feature-desc">
                管理 HTML 静态页面，支持上传、查看、预览和删除操作
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 开始使用", key="goto_html", use_container_width=True):
            st.session_state.page = "📄 HTML 管理"
            st.rerun()

    st.markdown("---")
    st.markdown("### 💡 使用提示")
    st.markdown("""
    - 点击任意功能的「开始使用」按钮即可进入对应页面
    - 使用左侧侧边栏进行页面导航
    - 文档学习包含生成笔记、翻译语音、媒材建议三个功能
    """)
