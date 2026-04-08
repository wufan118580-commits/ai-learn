"""
文档学习助手 - Streamlit 应用主入口
"""
import os
import warnings
import streamlit as st
from dotenv import load_dotenv

# 抑制非关键警告
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning, module='albumentations')
warnings.filterwarnings('ignore', category=UserWarning, module='pydantic')

# 禁用OpenCV的GUI功能（在无GUI环境中）
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '1'
os.environ['XDG_RUNTIME_DIR'] = '/tmp/runtime-root'

# 确保工作目录存在
os.makedirs('/tmp/runtime-root', exist_ok=True)

# 加载环境变量
load_dotenv()

# 导入业务处理模块
from document_processor import DocumentProcessor
from prompt_templates import PromptManager
from handlers.notes_handler import NotesHandler
from handlers.translation_handler import TranslationHandler
from handlers.media_handler import MediaHandler

# 导入UI模块
from ui.components import show_error, show_success, show_warning, show_spinner
from ui.notes_tab import render_notes_results
from ui.media_tab import render_media_results
from ui.html_tab import render_html_tab
from ui.formula_tab import render_formula_tab
from ui.home_page import render_home_page


# 初始化组件
doc_processor = DocumentProcessor()
prompt_manager = PromptManager()

# 页面配置
st.set_page_config(
    page_title="文档学习助手",
    page_icon="📚",
    layout="wide"
)


# 初始化 session state
def init_session_state():
    """初始化 session state"""
    state_vars = {
        'generated_result': None,
        'last_uploaded_file': None,
        'translated_text': None,
        'polished_text': None,
        'tts_audio_path': None,
        'media_suggestions': None,
        'edit_mode': False,
        'edited_notes': None,
        'api_key': None,
        'uploaded_file': None,
        'show_polish_options': False,
        'preview_id': None,
        'confirm_clear': False
    }
    for key, default_value in state_vars.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


init_session_state()


# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 配置")

    # API密钥配置
    api_key_option = st.radio(
        "API密钥来源",
        ["使用内置密钥", "自定义密钥"]
    )

    if api_key_option == "使用内置密钥":
        st.session_state.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not st.session_state.api_key:
            st.error("❌ 未找到内置API密钥，请在.env文件中配置")
    else:
        st.session_state.api_key = st.text_input("请输入DeepSeek API密钥", type="password")

    # 提示词选择
    st.header("📝 提示词设置")
    prompt_option = st.radio(
        "提示词来源",
        ["内置模板", "自定义提示词"]
    )

    selected_template = None
    custom_prompt = None

    if prompt_option == "内置模板":
        template_names = prompt_manager.get_template_names()
        selected_template = st.selectbox("选择模板", template_names)
    else:
        custom_prompt = st.text_area(
            "输入自定义提示词",
            height=200,
            help="使用 {document_text} 作为文档内容的占位符"
        )

    st.markdown("---")
    st.markdown("### 📖 使用说明")
    st.markdown("""
    1. 在首页选择要使用的功能
    2. 配置API密钥
    3. 选择或自定义提示词
    4. 根据功能提示操作
    """)


# 页面选择器 - 简化为三个选项
if 'page' not in st.session_state:
    st.session_state.page = "🏠 首页"

page = st.sidebar.radio(
    "📌 页面导航",
    ["🏠 首页", "📚 文档学习", "📐 公式识别", "📄 HTML 管理"],
    index=["🏠 首页", "📚 文档学习", "📐 公式识别", "📄 HTML 管理"].index(st.session_state.page) if st.session_state.page in ["🏠 首页", "📚 文档学习", "📐 公式识别", "📄 HTML 管理"] else 0
)

# 更新 session state 中的页面
st.session_state.page = page


# 首页
if page == "🏠 首页":
    render_home_page()


# 文档学习页面 - 合并三个功能
elif page == "📚 文档学习":
    st.header("📚 文档学习")
    st.info("上传文档后，可以使用生成笔记、翻译语音、媒材建议等功能")

    # 创建三个标签页
    tab_notes, tab_translation, tab_media = st.tabs(["📝 学习笔记", "🔊 翻译语音", "🎨 媒材建议"])

    # 文档上传（每个标签页都有，保持独立）
    def render_upload_section():
        """渲染上传区域"""
        uploaded_file = st.file_uploader(
            "📤 上传文档",
            type=['txt', 'pdf', 'docx'],
            help="支持txt、pdf、docx格式",
            key=f"upload_{st.session_state.get('current_tab', 'notes')}"
        )

        if uploaded_file:
            st.session_state.uploaded_file = uploaded_file
            upload_col1, upload_col2 = st.columns([3, 1])
            with upload_col1:
                st.success(f"✅ 已上传: {uploaded_file.name}")
            with upload_col2:
                st.info(f"文件大小: {len(uploaded_file.getvalue()) / 1024:.1f} KB")

            # 文档预览
            with st.expander("📄 预览文档内容", expanded=False):
                try:
                    text_content = doc_processor.process_uploaded_file(uploaded_file)
                    if text_content:
                        st.text(text_content[:2000] + ("..." if len(text_content) > 2000 else ""))
                except Exception as e:
                    show_error("文档处理失败", show_details=True, exception=e)

        return uploaded_file

    # 学习笔记标签页
    with tab_notes:
        st.session_state.current_tab = 'notes'
        st.markdown("---")

        notes_uploaded_file = render_upload_section()

        # 生成按钮
        generate_button = st.button(
            "🚀 生成学习笔记和思维导图",
            type="primary",
            use_container_width=True,
            disabled=not (st.session_state.get('uploaded_file') and st.session_state.get('api_key')),
            key="generate_notes_button"
        )

        # 处理学习笔记生成
        if generate_button and st.session_state.api_key:
            with show_spinner("正在处理文档并生成内容..."):
                try:
                    document_text = doc_processor.process_uploaded_file(notes_uploaded_file)

                    if not document_text:
                        show_error("无法提取文档内容")
                    else:
                        # 构建提示词
                        if prompt_option == "内置模板":
                            prompt = prompt_manager.format_prompt(
                                selected_template,
                                document_text[:12000]
                            )
                        else:
                            prompt = custom_prompt.replace("{document_text}", document_text[:12000])

                        # 调用处理
                        notes_handler = NotesHandler()
                        result = notes_handler.generate_notes(prompt, notes_uploaded_file.name, st.session_state.api_key)

                        st.session_state.generated_result = result
                        st.session_state.last_uploaded_file = notes_uploaded_file.name

                        show_success("学习笔记生成完成！")

                except Exception as e:
                    show_error(f"生成失败: {str(e)}", show_details=True, exception=e)

        # 显示结果
        if st.session_state.generated_result:
            st.markdown("---")
            render_notes_results(st.session_state.generated_result, st.session_state.last_uploaded_file)

    # 翻译语音标签页
    with tab_translation:
        st.session_state.current_tab = 'translation'
        st.markdown("---")

        trans_uploaded_file = render_upload_section()

        if trans_uploaded_file:
            st.session_state.uploaded_file = trans_uploaded_file

            # 翻译按钮
            translate_button = st.button(
                "🔄 翻译文档",
                type="primary",
                use_container_width=True,
                disabled=not st.session_state.get('api_key'),
                key="translate_button"
            )

            # 处理翻译
            if translate_button and st.session_state.api_key:
                with show_spinner("正在翻译文档..."):
                    try:
                        document_text = doc_processor.process_uploaded_file(trans_uploaded_file)

                        if not document_text:
                            show_error("无法提取文档内容")
                        else:
                            translation_handler = TranslationHandler()
                            translated_text = translation_handler.translate_document(
                                document_text,
                                st.session_state.api_key
                            )

                            if translated_text:
                                st.session_state.translated_text = translated_text
                                st.session_state.tts_audio_path = None
                                show_success("翻译完成！")
                                st.rerun()
                            else:
                                show_error("翻译失败")
                    except Exception as e:
                        show_error(f"翻译失败: {str(e)}", show_details=True, exception=e)

            # 润色和语音配置
            if st.session_state.translated_text:
                st.markdown("---")

                # 润色按钮
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✨ 润色文本", key="show_polish"):
                        st.session_state.show_polish_options = True
                        st.rerun()
                with col2:
                    if st.button("🎵 生成语音", key="show_tts"):
                        st.session_state.show_polish_options = False
                        st.rerun()

                # 润色选项
                if st.session_state.get('show_polish_options'):
                    st.markdown("### ✨ 文本润色")
                    st.info("将翻译后的文本润色成更适合社交媒体传播的风格")

                    polish_style = st.radio(
                        "选择润色风格",
                        ["social_media", "narrative"],
                        format_func=lambda x: "📱 社交媒体风格" if x == "social_media" else "📖 叙事风格"
                    )

                    polish_button = st.button(
                        "🚀 开始润色",
                        type="secondary",
                        use_container_width=True,
                        disabled=not st.session_state.get('api_key'),
                        key="execute_polish_button"
                    )

                    if polish_button and st.session_state.api_key:
                        with show_spinner("正在润色文本..."):
                            try:
                                translation_handler = TranslationHandler()
                                polished_text = translation_handler.polish_text(
                                    st.session_state.translated_text,
                                    st.session_state.api_key,
                                    polish_style
                                )

                                if polished_text:
                                    st.session_state.polished_text = polished_text
                                    st.session_state.show_polish_options = False
                                    show_success("润色完成！")
                                    st.rerun()
                                else:
                                    show_error("润色失败")
                            except Exception as e:
                                show_error(f"润色失败: {str(e)}", show_details=True, exception=e)

                # 语音配置
                else:
                    st.markdown("### 🎵 语音配置")
                    translation_handler = TranslationHandler()

                    col1, col2 = st.columns(2)
                    with col1:
                        voice_gender = st.radio(
                            "选择声音类型",
                            ["female", "male"],
                            format_func=lambda x: "女声" if x == "female" else "男声"
                        )
                    with col2:
                        available_voices = translation_handler.get_available_voices()
                        voice_options = available_voices.get(voice_gender, {})
                        selected_voice = st.selectbox(
                            "选择声音",
                            list(voice_options.keys()),
                            format_func=lambda x: voice_options[x]
                        )

                    col3, col4 = st.columns(2)
                    with col3:
                        rate = st.slider("语速调整", -50, 50, 0, 10, format="%d%%")
                    with col4:
                        pitch = st.slider("音调调整", -10, 10, 0, 1, format="%dHz")

                    # 生成语音按钮
                    generate_tts_button = st.button(
                        "🎵 生成语音",
                        type="secondary",
                        use_container_width=True,
                        key="generate_tts_button"
                    )

                    # 处理语音生成
                    if generate_tts_button:
                        with show_spinner("正在生成语音..."):
                            try:
                                tts_text = st.session_state.translated_text[:5000]
                                audio_path = translation_handler.generate_speech(
                                    tts_text,
                                    selected_voice,
                                    f"{rate:+d}%",
                                    f"{pitch:+d}Hz"
                                )

                                if audio_path and os.path.exists(audio_path):
                                    st.session_state.tts_audio_path = audio_path
                                    show_success("语音生成成功！")
                                    st.rerun()
                                else:
                                    show_error("语音生成失败")
                            except Exception as e:
                                show_error(f"语音生成失败: {str(e)}", show_details=True, exception=e)

                    # 播放音频
                    if st.session_state.tts_audio_path:
                        st.markdown("### 🎧 播放语音")
                        with open(st.session_state.tts_audio_path, 'rb') as audio_file:
                            audio_bytes = audio_file.read()
                        st.audio(audio_bytes, format='audio/mp3')

                        with open(st.session_state.tts_audio_path, 'rb') as f:
                            st.download_button(
                                label="📥 下载音频文件",
                                data=f,
                                file_name=os.path.basename(st.session_state.tts_audio_path),
                                mime="audio/mpeg",
                                key="download_audio"
                            )

            # 显示翻译结果
            if st.session_state.translated_text:
                st.markdown("---")
                st.header("🔊 翻译结果")
                tab1, tab2 = st.tabs(["📄 翻译文本", "✨ 润色文本"])

                with tab1:
                    with st.expander("📖 查看翻译文本", expanded=False):
                        st.markdown(
                            st.session_state.translated_text[:5000] +
                            ("..." if len(st.session_state.translated_text) > 5000 else "")
                        )

                with tab2:
                    if st.session_state.polished_text:
                        with st.expander("✨ 查看润色文本", expanded=False):
                            st.markdown(
                                st.session_state.polished_text[:5000] +
                                ("..." if len(st.session_state.polished_text) > 5000 else "")
                            )

                        st.download_button(
                            label="📥 下载润色文本",
                            data=st.session_state.polished_text,
                            file_name="润色文本.txt",
                            mime="text/plain",
                            key="download_polished_text"
                        )
                    else:
                        st.info("💡 点击「✨ 润色文本」按钮来生成更适合传播的版本")

    # 媒材建议标签页
    with tab_media:
        st.session_state.current_tab = 'media'
        st.markdown("---")

        media_uploaded_file = render_upload_section()

        if media_uploaded_file:
            st.session_state.uploaded_file = media_uploaded_file

            # 显示当前使用的文本来源
            if st.session_state.translated_text:
                st.info("✅ 将使用**翻译文本**进行分析")
            else:
                st.info("ℹ️ 将使用**原文**进行分析")

            # 分析按钮
            analyze_button = st.button(
                "🔍 分析配图建议",
                type="primary",
                use_container_width=True,
                disabled=not st.session_state.get('api_key'),
                key="analyze_media_button"
            )

            # 处理媒材分析
            if analyze_button and st.session_state.api_key:
                with show_spinner("正在分析文本..."):
                    try:
                        # 优先使用翻译后的文本，如果没有翻译则使用原文
                        text_to_analyze = st.session_state.translated_text
                        text_source = "翻译文本"

                        if not text_to_analyze:
                            text_to_analyze = doc_processor.process_uploaded_file(media_uploaded_file)
                            text_source = "原文"

                        if not text_to_analyze:
                            show_error("无法获取文档内容")
                        else:
                            media_handler = MediaHandler()
                            suggestions = media_handler.analyze_media_suggestions(
                                text_to_analyze,
                                st.session_state.api_key
                            )

                            if suggestions:
                                st.session_state.media_suggestions = suggestions
                                show_success(f"分析完成！找到 {len(suggestions)} 个配图建议（基于{text_source}）")
                                st.rerun()
                            else:
                                show_warning("未找到适合配图的片段")
                    except Exception as e:
                        show_error(f"分析失败: {str(e)}", show_details=True, exception=e)

        # 显示结果
        if st.session_state.media_suggestions:
            st.markdown("---")
            render_media_results()


# 公式识别页面
elif page == "📐 公式识别":
    render_formula_tab()


# HTML 管理页面
elif page == "📄 HTML 管理":
    render_html_tab()


# 底部信息
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and DeepSeek")
