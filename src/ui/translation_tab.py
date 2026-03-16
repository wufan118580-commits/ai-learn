"""
翻译语音 Tab UI
"""
import streamlit as st
import os


def render_translation_tab(_uploaded_file_name):
    """渲染翻译语音 Tab"""
    st.markdown("### 🔊 翻译文档并生成语音")
    st.info("将文档翻译为中文，并转换为语音播放")

    # 如果已有翻译结果，显示重新翻译按钮
    if st.session_state.translated_text:
        if st.button("🔄 重新翻译", key="retranslate_button"):
            st.session_state.translated_text = None
            st.session_state.tts_audio_path = None
            st.rerun()

    # 翻译语音按钮
    translate_button = st.button(
        "🔄 翻译并生成语音",
        type="primary",
        use_container_width=True,
        disabled=not (st.session_state.get('uploaded_file') and st.session_state.get('api_key')),
        key="translate_tts_button"
    )

    # 如果已有翻译结果，显示语音配置
    if st.session_state.translated_text:
        st.markdown("---")
        st.success("✅ 已完成翻译，现在配置语音参数：")

        return render_tts_config()

    return translate_button, None, None, None


def render_tts_config():
    """渲染TTS配置界面"""
    from handlers.translation_handler import TranslationHandler
    translation_handler = TranslationHandler()

    # 语音选择
    col1, col2 = st.columns(2)
    with col1:
        voice_gender = st.radio("选择声音类型", ["female", "male"], format_func=lambda x: "女声" if x == "female" else "男声")
    with col2:
        available_voices = translation_handler.get_available_voices()
        voice_options = available_voices.get(voice_gender, {})
        selected_voice = st.selectbox("选择声音", list(voice_options.keys()),
                                    format_func=lambda x: voice_options[x])

    # 语速和音调
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

    return generate_tts_button, selected_voice, f"{rate:+d}%", f"{pitch:+d}Hz"


def render_translation_results():
    """渲染翻译结果"""
    st.header("🔊 3. 翻译语音结果")
    st.markdown("---")

    st.success("✅ 翻译完成")
    with st.expander("📄 查看翻译文本", expanded=False):
        st.markdown(st.session_state.translated_text[:5000] +
                   ("..." if len(st.session_state.translated_text) > 5000 else ""))

    st.markdown("---")
