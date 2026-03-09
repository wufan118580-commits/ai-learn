import streamlit as st
from streamlit_mermaid import st_mermaid

st.set_page_config(
    page_title="Streamlit Mermaid Example",
    page_icon=":shark:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Streamlit Mermaid Example")

st.markdown(
    """
    ## Mermaid
    [Mermaid](https://mermaid-js.github.io/mermaid/#/) is a diagramming and charting tool that uses text-based descriptions to render diagrams.
    """
)

st.markdown(
    """
    ### Flowchart
    """
)

cleaned_code = """graph TD
    A[工业时序数据高效存储方案] --> B[电力行业数据存储场景]
    A --> C[工业高频数据存储场景]
    B --> B1[数据特征]
    B1 --> B1_1[频率: 每秒1条]
    B1 --> B1_2[列数: 10000-30000列]
    B --> B2[传统方法]
    B2 --> B2_1[存储方式: 每秒存1行]
    B2 --> B2_2[结构: 1列时间戳 + 10000列测点数值]
    B --> B3[新方法]
    B3 --> B3_1[存储方式: 每秒存1行]
    B3 --> B3_2[结构: 1列时间戳 + 1列Json全量数据]
    B3 --> B3_3[Json内容: 包含30000个KeyValue的Json串]
    B --> B4[技术优势]
    B4 --> B4_1[查询效率: Postgres Json操作符使查询效率等价于结构化字段]
    B4 --> B4_2[存储空间: 比传统方法节省50-100倍]
    B --> B5[案例效果]
    B5 --> B5_1[案例: 中电行唐生物质电厂]
    B5 --> B5_2[传统技术: 5T空间仅存22天]
    B5 --> B5_3[新方法: 5T空间可存1000天以上]
    B --> B6[对应专利]
    B6 --> B6_1[一种基于数字工业实时时序数据的存储计算的实现方法及装置]
    C --> C1[数据特征]
    C1 --> C1_1[频率: 每秒100-1000条]
    C1 --> C1_2[列数: 数十列]
    C --> C2[传统方法]
    C2 --> C2_1[存储方式: 每秒存1000行]
    C2 --> C2_2[结构: 1列时间戳 + 数十列测点数值]
    C --> C3[新方法]
    C3 --> C3_1[存储方式: 每秒存1行]
    C3 --> C3_2[结构: 1列时间戳 + 数十列Geometry类型数据]
    C3 --> C3_3[Geometry数据: 将1000个数值转化为GIS米制坐标]
    C3 --> C3_4[坐标映射: X轴每米代表1毫秒, Y轴代表测点数值]
    C --> C4[技术优势]
    C4 --> C4_1[数据处理: 利用PostGIS引擎高效转化并抽稀为linestring]
    C4 --> C4_2[数据用途: 抽稀后数据可作为AI训练样本]
    C4 --> C4_3[存储空间: 比传统方法最高节省约500倍]
    C --> C5[案例效果]
    C5 --> C5_1[案例: 中电行唐生物质电厂]
    C5 --> C5_2[传统技术: 5T空间仅存22天]
    C5 --> C5_3[新方法: 5T空间可存1000天以上]
    C --> C6[对应专利]
    C6 --> C6_1[一种结合时空大数据技术的工业时序数据存储分析方法及装置] 
    
"""
# 分为两个区域：代码编辑区和渲染结果区
col_code, col_render = st.columns([1, 2])

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
# mermaid_code = st.text_area("Mermaid Code", mermaid_code)

# st_mermaid(mermaid_code, height="2000px")
