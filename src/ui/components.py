"""
通用 UI 组件
"""
import streamlit as st


def show_error(message: str, show_details: bool = False, exception=None):
    """显示错误信息"""
    st.error(f"❌ {message}")
    if show_details and exception:
        with st.expander("查看错误详情"):
            st.exception(exception)


def show_success(message: str):
    """显示成功信息"""
    st.success(f"✅ {message}")


def show_warning(message: str):
    """显示警告信息"""
    st.warning(f"⚠️ {message}")


def show_info(message: str):
    """显示提示信息"""
    st.info(f"💡 {message}")


def show_spinner(message: str):
    """返回 spinner 上下文管理器"""
    return st.spinner(f"🔄 {message}")
