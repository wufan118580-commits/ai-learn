"""
HTML 文件管理处理逻辑
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Optional


class HTMLHandler:
    """HTML 文件处理器"""

    def __init__(self, storage_dir: str = "html_storage"):
        """
        初始化 HTML 处理器

        Args:
            storage_dir: HTML 文件存储目录
        """
        self.storage_dir = storage_dir
        self.metadata_file = os.path.join(storage_dir, "metadata.json")
        self._ensure_storage_dir()

    def _ensure_storage_dir(self):
        """确保存储目录存在"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
            # 初始化空的元数据文件
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _load_metadata(self) -> List[Dict]:
        """加载元数据"""
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def _save_metadata(self, metadata: List[Dict]):
        """保存元数据"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def upload_html(self, filename: str, html_content: str) -> Dict:
        """
        上传 HTML 文件

        Args:
            filename: 文件名
            html_content: HTML 内容

        Returns:
            文件信息字典
        """
        # 生成唯一文件名（添加时间戳避免重名）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(self.storage_dir, safe_filename)

        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # 生成文件 ID
        metadata = self._load_metadata()
        file_id = len(metadata) + 1

        # 创建文件信息
        file_info = {
            'id': file_id,
            'filename': filename,
            'safe_filename': safe_filename,
            'file_path': file_path,
            'upload_time': datetime.now().isoformat(),
            'file_size': len(html_content)
        }

        # 更新元数据
        metadata.append(file_info)
        self._save_metadata(metadata)

        return file_info

    def get_html_list(self) -> List[Dict]:
        """
        获取所有 HTML 文件列表

        Returns:
            文件信息列表
        """
        metadata = self._load_metadata()

        # 检查文件是否实际存在，清理不存在的文件
        valid_metadata = []
        for item in metadata:
            if os.path.exists(item['file_path']):
                valid_metadata.append(item)
            else:
                print(f"警告：文件 {item['filename']} 不存在，已从列表中移除")

        # 如果有文件被移除，更新元数据
        if len(valid_metadata) != len(metadata):
            self._save_metadata(valid_metadata)

        return valid_metadata

    def get_html_content(self, file_id: int) -> Optional[str]:
        """
        获取 HTML 文件内容

        Args:
            file_id: 文件 ID

        Returns:
            HTML 内容，如果文件不存在返回 None
        """
        metadata = self._load_metadata()
        for item in metadata:
            if item['id'] == file_id and os.path.exists(item['file_path']):
                with open(item['file_path'], 'r', encoding='utf-8') as f:
                    return f.read()
        return None

    def delete_html(self, file_id: int) -> bool:
        """
        删除 HTML 文件

        Args:
            file_id: 文件 ID

        Returns:
            是否删除成功
        """
        metadata = self._load_metadata()
        updated_metadata = []
        deleted = False

        for item in metadata:
            if item['id'] == file_id:
                # 删除文件
                try:
                    if os.path.exists(item['file_path']):
                        os.remove(item['file_path'])
                        deleted = True
                except Exception as e:
                    print(f"删除文件 {item['filename']} 失败: {e}")
            else:
                updated_metadata.append(item)

        if deleted:
            self._save_metadata(updated_metadata)

        return deleted

    def get_html_info(self, file_id: int) -> Optional[Dict]:
        """
        获取文件详细信息

        Args:
            file_id: 文件 ID

        Returns:
            文件信息字典，如果不存在返回 None
        """
        metadata = self._load_metadata()
        for item in metadata:
            if item['id'] == file_id:
                return item
        return None

    def clear_all(self):
        """清空所有 HTML 文件"""
        metadata = self._load_metadata()
        for item in metadata:
            if os.path.exists(item['file_path']):
                try:
                    os.remove(item['file_path'])
                except Exception as e:
                    print(f"删除文件 {item['filename']} 失败: {e}")

        # 清空元数据
        self._save_metadata([])
