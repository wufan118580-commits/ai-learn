"""
文本转语音服务模块
使用 edge-tts 将中文文本转换为语音
"""
import asyncio
import edge_tts
import os
import tempfile
from typing import Optional


class TTSService:
    """文本转语音服务"""

    # 可用语音列表（中文）
    CHINESE_VOICES = {
        'female': {
            'zh-CN-XiaoxiaoNeural': '晓晓（女声，温柔）',
            'zh-CN-XiaoyiNeural': '晓伊（女声，可爱）',
            'zh-CN-XiaohanNeural': '晓涵（女声，知性）',
            'zh-CN-XiaoxuanNeural': '晓萱（女声，活泼）',
            'zh-CN-XiaomengNeural': '晓梦（女声，甜美）',
        },
        'male': {
            'zh-CN-YunyangNeural': '云扬（男声，沉稳）',
            'zh-CN-YunxiNeural': '云希（男声，磁性）',
            'zh-CN-YunjianNeural': '云健（男声，有力）',
        }
    }

    # 默认语音
    DEFAULT_VOICE = 'zh-CN-XiaoxiaoNeural'

    def __init__(self, output_dir: str = None):
        """
        初始化 TTS 服务

        Args:
            output_dir: 音频输出目录，默认使用临时目录
        """
        self.output_dir = output_dir or tempfile.gettempdir()
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def get_voices(self) -> dict:
        """获取可用的语音列表"""
        return self.CHINESE_VOICES

    async def text_to_speech_async(
        self,
        text: str,
        voice: str = DEFAULT_VOICE,
        output_filename: str = None,
        rate: str = '+0%',
        pitch: str = '+0Hz',
        volume: str = '+0%'
    ) -> Optional[str]:
        """
        异步将文本转换为语音

        Args:
            text: 要转换的文本内容
            voice: 语音ID，默认为 'zh-CN-XiaoxiaoNeural'
            output_filename: 输出文件名（不含扩展名），如果为None则自动生成
            rate: 语速调整，例如 '+10%', '-10%'
            pitch: 音调调整，例如 '+10Hz', '-10Hz'
            volume: 音量调整，例如 '+10%', '-10%'

        Returns:
            生成的音频文件路径，失败返回None
        """
        try:
            # 如果没有指定文件名，生成一个唯一的文件名
            if not output_filename:
                import uuid
                output_filename = f"tts_{uuid.uuid4().hex[:8]}"

            output_path = os.path.join(self.output_dir, f"{output_filename}.mp3")

            # 创建 TTS 对象
            communicate = edge_tts.Communicate(
                text,
                voice,
                rate=rate,
                pitch=pitch,
                volume=volume
            )

            # 生成音频文件
            await communicate.save(output_path)

            return output_path

        except Exception as e:
            print(f"文本转语音失败: {e}")
            return None

    def text_to_speech(
        self,
        text: str,
        voice: str = DEFAULT_VOICE,
        output_filename: str = None,
        rate: str = '+0%',
        pitch: str = '+0Hz',
        volume: str = '+0%'
    ) -> Optional[str]:
        """
        将文本转换为语音（同步接口）

        Args:
            text: 要转换的文本内容
            voice: 语音ID
            output_filename: 输出文件名
            rate: 语速调整
            pitch: 音调调整
            volume: 音量调整

        Returns:
            生成的音频文件路径，失败返回None
        """
        try:
            # 在新的事件循环中运行异步函数
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.text_to_speech_async(
                    text, voice, output_filename, rate, pitch, volume
                )
            )
            loop.close()
            return result
        except Exception as e:
            print(f"文本转语音失败: {e}")
            return None

    def clean_old_files(self, max_age_hours: int = 24):
        """
        清理旧的音频文件

        Args:
            max_age_hours: 文件最大保存时间（小时）
        """
        import time
        current_time = time.time()

        try:
            for filename in os.listdir(self.output_dir):
                if filename.startswith('tts_') and filename.endswith('.mp3'):
                    filepath = os.path.join(self.output_dir, filename)
                    file_age = current_time - os.path.getmtime(filepath)

                    # 如果文件超过指定时间，删除它
                    if file_age > max_age_hours * 3600:
                        os.remove(filepath)
                        print(f"已删除旧文件: {filename}")
        except Exception as e:
            print(f"清理旧文件失败: {e}")
