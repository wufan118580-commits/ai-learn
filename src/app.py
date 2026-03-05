import streamlit as st
import os
from typing import Optional
from dotenv import load_dotenv
from document_processor import DocumentProcessor
from llm_service import DeepSeekService
from prompt_templates import PromptManager

# 加载环境变量
load_dotenv()

# 初始化组件
doc_processor = DocumentProcessor()
prompt_manager = PromptManager()

# 页面配置
st.set_page_config(
    page_title="文档学习助手",
    page_icon="📚",
    layout="wide"
)

def init_session_state():
    """初始化session state"""
    if 'generated_content' not in st.session_state:
        st.session_state.generated_content = None
    if 'error_message' not in st.session_state:
        st.session_state.error_message = None

def display_error(message: str):
    """显示错误信息"""
    st.session_state.error_message = message
    st.error(message)

def clear_error():
    """清除错误信息"""
    st.session_state.error_message = None

def process_document(uploaded_file, api_key: str, prompt: str) -> Optional[str]:
    """处理文档并生成内容"""
    try:
        # 提取文档内容
        document_text = doc_processor.process_uploaded_file(uploaded_file)
        
        if not document_text:
            raise ValueError("无法提取文档内容")
        
        # 调用API
        llm_service = DeepSeekService(api_key)
        result = llm_service.generate(prompt)
        
        return result
        
    except (ValueError, TimeoutError, ConnectionError, RuntimeError) as e:
        display_error(str(e))
        return None
    except Exception as e:
        display_error(f"处理文档时发生未知错误: {str(e)}")
        return None

# 初始化session state
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
        ["使用内置密钥", "自定义密钥"],
        key="api_key_option"
    )
    
    api_key: Optional[str] = None
    if api_key_option == "使用内置密钥":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            st.error("未找到内置API密钥，请在.env文件中配置")
    else:
        api_key = st.text_input("请输入DeepSeek API密钥", type="password", key="custom_api_key")
    
    # 提示词选择
    st.header("📝 提示词设置")
    prompt_option = st.radio(
        "提示词来源",
        ["内置模板", "自定义提示词"],
        key="prompt_option"
    )
    
    selected_template = None
    custom_prompt = None
    
    if prompt_option == "内置模板":
        template_names = prompt_manager.get_template_names()
        selected_template = st.selectbox("选择模板", template_names, key="template_select")
    else:
        custom_prompt = st.text_area(
            "输入自定义提示词",
            height=200,
            help="使用 {document_text} 作为文档内容的占位符",
            key="custom_prompt_input"
        )
    
    st.markdown("---")
    st.markdown("### 使用说明")
    st.markdown("""
    1. 上传文档（支持txt、pdf、docx）
    2. 配置API密钥
    3. 选择或自定义提示词
    4. 点击生成按钮
    """)

# 主界面
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📤 上传文档")
    uploaded_file = st.file_uploader(
        "选择文件",
        type=['txt', 'pdf', 'docx'],
        help="支持txt、pdf、docx格式",
        key="file_uploader"
    )
    
    if uploaded_file:
        st.success(f"已上传: {uploaded_file.name}")
        
        # 显示文档预览
        with st.expander("预览文档内容"):
            try:
                text_content = doc_processor.process_uploaded_file(uploaded_file)
                if text_content:
                    preview_text = text_content[:1000]
                    if len(text_content) > 1000:
                        preview_text += "..."
                    st.text(preview_text)
            except Exception as e:
                st.error(f"文档预览失败: {str(e)}")

with col2:
    st.header("🎯 生成内容")
    
    generate_button = st.button(
        "🚀 生成学习笔记和思维导图",
        type="primary",
        disabled=not (uploaded_file and api_key),
        key="generate_button"
    )
    
    if generate_button and api_key and uploaded_file:
        clear_error()
        with st.spinner("正在处理文档并生成内容..."):
            # 构建提示词
            if prompt_option == "内置模板" and selected_template:
                prompt = prompt_manager.format_prompt(
                    selected_template,
                    text_content[:8000] if 'text_content' in locals() else ""  # 限制长度
                )
            elif custom_prompt:
                prompt = custom_prompt.replace("{document_text}", text_content[:8000] if 'text_content' in locals() else "")
            else:
                st.error("请选择或输入提示词")
                st.stop()
            
            # 处理文档
            result = process_document(uploaded_file, api_key, prompt)
            
            if result:
                st.session_state.generated_content = result
                st.success("生成完成！")
    
    # 显示生成的内容
    if st.session_state.generated_content:
        result = st.session_state.generated_content
        
        # 解析结果（根据模板类型）
        if "```mermaid" in result:
            # 分离笔记和思维导图
            parts = result.split("```mermaid")
            if len(parts) > 1:
                notes = parts[0]
                mermaid_code = "```mermaid" + parts[1]
                
                st.subheader("📖 学习笔记")
                st.markdown(notes)
                
                st.subheader("🧠 思维导图")
                st.code(mermaid_code, language="mermaid")
                
                # 提供下载
                st.download_button(
                    "下载思维导图代码",
                    mermaid_code,
                    file_name="mindmap.mmd",
                    key="download_button"
                )
        else:
            # 简单显示
            st.markdown(result)

# 底部信息
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and DeepSeek")