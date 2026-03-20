"""
文档学习助手 - Streamlit 应用主入口
"""
import streamlit as st
import os
from dotenv import load_dotenv

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
from ui.notes_tab import render_notes_tab, render_notes_results
from ui.translation_tab import render_translation_tab, render_translation_results
from ui.media_tab import render_media_tab, render_media_results


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
        'show_polish_options': False
    }
    for key, default_value in state_vars.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

init_session_state()


# 标题
st.title("📚 文档学习助手")
st.markdown("上传文档，自动生成学习笔记和思维导图")


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
    1. 上传文档（支持txt、pdf、docx）
    2. 配置API密钥
    3. 选择或自定义提示词
    4. 选择功能并执行
    """)


# 主界面 - 上传文档
st.header("📤 1. 上传文档")

uploaded_file = st.file_uploader(
    "选择文件",
    type=['txt', 'pdf', 'docx'],
    help="支持txt、pdf、docx格式"
)

if uploaded_file:
    st.session_state.uploaded_file = uploaded_file
    col1, col2 = st.columns([3, 1])
    with col1:
        st.success(f"✅ 已上传: {uploaded_file.name}")
    with col2:
        st.info(f"文件大小: {len(uploaded_file.getvalue()) / 1024:.1f} KB")

    # 文档预览
    with st.expander("📄 预览文档内容", expanded=False):
        try:
            text_content = doc_processor.process_uploaded_file(uploaded_file)
            if text_content:
                st.text(text_content[:2000] + ("..." if len(text_content) > 2000 else ""))
        except Exception as e:
            show_error("文档处理失败", show_details=True, exception=e)


# 功能选择区域
st.header("🎯 2. 选择功能")
st.markdown("---")

# 创建三个功能选项卡
function_tabs = st.tabs(["📚 生成学习笔记", "🔊 翻译语音", "🎨 媒材建议"])


# 学习笔记 Tab
with function_tabs[0]:
    generate_button = render_notes_tab()


# 翻译语音 Tab
with function_tabs[1]:
    translate_button, voice, rate, pitch, polish_button, polish_style = render_translation_tab(
        st.session_state.last_uploaded_file or (uploaded_file.name if uploaded_file else "")
    )


# 媒材建议 Tab
with function_tabs[2]:
    analyze_button = render_media_tab()


# 处理学习笔记生成
if generate_button and st.session_state.api_key:
    with show_spinner("正在处理文档并生成内容..."):
        try:
            document_text = doc_processor.process_uploaded_file(uploaded_file)

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
                result = notes_handler.generate_notes(prompt, uploaded_file.name, st.session_state.api_key)

                st.session_state.generated_result = result
                st.session_state.last_uploaded_file = uploaded_file.name

                show_success("学习笔记生成完成！")

        except Exception as e:
            show_error(f"生成失败: {str(e)}", show_details=True, exception=e)


# 处理翻译语音生成
if translate_button and st.session_state.api_key:
    with show_spinner("正在翻译文档..."):
        try:
            document_text = doc_processor.process_uploaded_file(uploaded_file)

            if not document_text:
                show_error("无法提取文档内容")
            else:
                translation_handler = TranslationHandler()
                translated_text = translation_handler.translate_document(document_text, st.session_state.api_key)

                if translated_text:
                    st.session_state.translated_text = translated_text
                    st.session_state.tts_audio_path = None
                    show_success("翻译完成！请在下方配置语音参数")
                    st.rerun()
                else:
                    show_error("翻译失败")
        except Exception as e:
            show_error(f"翻译失败: {str(e)}", show_details=True, exception=e)


# 处理文本润色
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


# 处理语音生成
if 'generate_tts_button' in st.session_state and st.session_state.generate_tts_button:
    with show_spinner("正在生成语音，请稍候..."):
        try:
            translation_handler = TranslationHandler()
            tts_text = st.session_state.translated_text[:5000]
            audio_path = translation_handler.generate_speech(
                tts_text,
                voice,
                rate,
                pitch
            )

            if audio_path and os.path.exists(audio_path):
                st.session_state.tts_audio_path = audio_path
                show_success("语音生成成功！")
                st.rerun()
            else:
                show_error("语音生成失败")
        except Exception as e:
            show_error(f"语音生成失败: {str(e)}", show_details=True, exception=e)


# 处理媒材分析
if analyze_button and st.session_state.api_key:
    with show_spinner("正在分析文本..."):
        try:
            # 优先使用翻译后的文本，如果没有翻译则使用原文
            text_to_analyze = st.session_state.translated_text
            text_source = "翻译文本"

            if not text_to_analyze:
                text_to_analyze = doc_processor.process_uploaded_file(uploaded_file)
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


# 显示结果区域
if st.session_state.generated_result:
    render_notes_results(st.session_state.generated_result, st.session_state.last_uploaded_file)


if st.session_state.translated_text:
    render_translation_results()


if st.session_state.media_suggestions:
    render_media_results()


# 底部信息
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and DeepSeek")


# CSS 美化
st.markdown("""
<style>
    .stButton > button {
        font-size: 18px;
        font-weight: bold;
        padding: 10px 20px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)
