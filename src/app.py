import streamlit as st
import os
from dotenv import load_dotenv
from document_processor import DocumentProcessor
from llm_service import DeepSeekService
from prompt_templates import PromptManager
from note_generator import NoteGenerator
import re

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

# 尝试导入 streamlit-mermaid

from streamlit_mermaid import st_mermaid


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
    
    api_key = None
    if api_key_option == "使用内置密钥":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            st.error("❌ 未找到内置API密钥，请在.env文件中配置")
    else:
        api_key = st.text_input("请输入DeepSeek API密钥", type="password")
    
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
    4. 点击生成按钮
    """)

# 主界面 - 改为上下布局
st.header("📤 1. 上传文档")

# 上传区域
uploaded_file = st.file_uploader(
    "选择文件",
    type=['txt', 'pdf', 'docx'],
    help="支持txt、pdf、docx格式"
)

# 显示文档预览
if uploaded_file:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.success(f"✅ 已上传: {uploaded_file.name}")
    with col2:
        st.info(f"文件大小: {len(uploaded_file.getvalue()) / 1024:.1f} KB")
    
    # 文档预览（可折叠）
    with st.expander("📄 预览文档内容", expanded=False):
        try:
            text_content = doc_processor.process_uploaded_file(uploaded_file)
            if text_content:
                st.text(text_content[:2000] + ("..." if len(text_content) > 2000 else ""))
        except Exception as e:
            st.error(f"❌ 文档处理失败: {str(e)}")

# 生成区域
st.header("🎯 2. 生成内容")
st.markdown("---")

# 生成按钮
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_button = st.button(
        "🚀 生成学习笔记和思维导图",
        type="primary",
        use_container_width=True,
        disabled=not (uploaded_file and api_key)
    )

# 结果显示区域
if generate_button and api_key:
    with st.spinner("🔄 正在处理文档并生成内容..."):
        try:
            # 提取文档内容
            document_text = doc_processor.process_uploaded_file(uploaded_file)
            
            if not document_text:
                st.error("❌ 无法提取文档内容")
            else:
                # 构建提示词
                if prompt_option == "内置模板":
                    prompt = prompt_manager.format_prompt(
                        selected_template,
                        document_text[:12000]  # 限制长度
                    )
                else:
                    prompt = custom_prompt.replace("{document_text}", document_text[:12000])
                
                # 调用API
                note_generator = NoteGenerator(api_key)
                result = note_generator.generate_document_notes(prompt, uploaded_file.name)
                
                # 显示结果
                st.success("✅ 生成完成！")
                
                # 创建结果显示区域
                result_tabs = st.tabs(["📖 学习笔记", "🧠 思维导图", "📝 完整输出"])
                
                # 解析Mermaid代码
                mermaid_pattern = r'```mermaid\n(.*?)\n```'
                mermaid_matches = re.findall(mermaid_pattern, result, re.DOTALL)

                if mermaid_matches:
                    # 分离笔记和思维导图
                    # 移除所有Mermaid代码块，剩下的就是笔记
                    notes = re.sub(mermaid_pattern, '', result, flags=re.DOTALL)

                    with result_tabs[0]:
                        st.markdown("### 📖 学习笔记")
                        st.markdown(notes)

                    with result_tabs[1]:
                        st.markdown("### 🧠 思维导图")

                        # 显示Mermaid图表（如果有多个，全部显示）
                        for i, mermaid_code in enumerate(mermaid_matches, 1):
                            if len(mermaid_matches) > 1:
                                st.markdown(f"**思维导图 {i}**")

                            # 清理Mermaid代码 - 移除非法字符
                            cleaned_code = mermaid_code.strip()
                            # 移除HTML转义字符
                            import html
                            cleaned_code = html.unescape(cleaned_code)
                            # 移除所有HTML标签
                            cleaned_code = re.sub(r'<[^>]+>', '', cleaned_code)
                            # 移除中文标点（逗号、分号、顿号、书名号、波浪号等）
                            cleaned_code = re.sub(r'[，；、。；：、。；：？【】《》""''（）()]', ' ', cleaned_code)
                            cleaned_code = re.sub(r'[～~]', '-', cleaned_code)
                            cleaned_code = re.sub(r'[《》]', '|', cleaned_code)
                            # 移除其他非法符号
                            cleaned_code = re.sub(r'[★●▪►▼▲]', '', cleaned_code)
                            # 移除前后空白行
                            lines = [line for line in cleaned_code.split('\n') if line.strip()]
                            cleaned_code = '\n'.join(lines)

                            # 分为两个区域：代码编辑区和渲染结果区
                            col_code, col_render = st.columns([2, 1])

                            with col_code:
                                st.markdown("### 📝 Mermaid 代码")
                                editable_code = st.text_area(
                                    "编辑 Mermaid 代码",
                                    value=cleaned_code,
                                    height=500,
                                    # key=f"mermaid_code_{i}",
                                    # help="可以手动修改 Mermaid 代码，右侧会实时渲染"
                                )

                            with col_render:
                                st.markdown("### 🖼️ 渲染结果")
                                try:
                                    st_mermaid(editable_code, height="500px")
                                except Exception as e:
                                    st.error(f"❌ Mermaid渲染失败: {e}")
                                    st.markdown("### 错误提示:")
                                    st.markdown("请检查 Mermaid 代码语法是否正确，常见问题：")
                                    st.markdown("- 缺少 `graph TD` 或 `flowchart` 开头")
                                    st.markdown("- 包含非法字符（如中文标点）")
                                    st.markdown("- 节点名称格式不正确")
                            

                            # 下载按钮
                            st.download_button(
                                label=f"📥 下载思维导图{i}.mmd",
                                data=mermaid_code,
                                file_name=f"mindmap_{i}.mmd",
                                mime="text/plain",
                                key=f"download_{i}"
                            )
                    
                    with result_tabs[2]:
                        st.markdown("### 📝 完整输出")
                        st.markdown(result)
                
                else:
                    # 如果没有检测到Mermaid代码，统一显示在完整输出中
                    with result_tabs[0]:
                        st.info("未检测到思维导图，显示完整内容")
                        st.markdown(result)
                    
                    with result_tabs[1]:
                        st.info("未检测到思维导图")
                    
                    with result_tabs[2]:
                        st.markdown("### 📝 完整输出")
                        st.markdown(result)
                
        except Exception as e:
            st.error(f"❌ 生成失败: {str(e)}")
            
            # 显示错误详情（开发调试用）
            with st.expander("查看错误详情"):
                st.exception(e)

# 底部信息
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and DeepSeek")

# 添加一些CSS美化
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