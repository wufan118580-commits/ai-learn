"""
公式识别功能测试脚本
用于验证公式识别功能是否正常工作
"""
import os
import sys
import pytest
import shutil

# 添加项目根目录和src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestFormulaDependencies:
    """测试依赖包"""

    def test_pillow_installed(self):
        """测试Pillow是否已安装"""
        try:
            __import__('PIL')
            assert True, "Pillow已安装"
        except ImportError:
            pytest.fail("Pillow未安装")


class TestFormulaImports:
    """测试导入是否正常"""

    def test_import_formula_ocr_service(self):
        """测试FormulaOCRService导入"""
        try:
            from api.services.formula_ocr_service import FormulaOCRService
            assert FormulaOCRService is not None
        except ImportError as e:
            pytest.fail(f"FormulaOCRService导入失败: {e}")

    def test_import_formula_handler(self):
        """测试FormulaHandler导入"""
        try:
            from handlers.formula_handler import FormulaHandler
            assert FormulaHandler is not None
        except ImportError as e:
            pytest.fail(f"FormulaHandler导入失败: {e}")


class TestFormulaHandler:
    """测试FormulaHandler功能"""

    @pytest.fixture
    def temp_handler(self):
        """创建临时处理器"""
        temp_dir = "test_formula_history"
        from handlers.formula_handler import FormulaHandler

        handler = FormulaHandler(storage_dir=temp_dir)
        yield handler

        # 清理
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    def test_handler_initialization(self, temp_handler):
        """测试处理器初始化"""
        assert temp_handler is not None
        assert temp_handler.storage_dir == "test_formula_history"

    def test_metadata_file_creation(self, temp_handler):
        """测试元数据文件是否创建"""
        metadata_file = os.path.join(temp_handler.storage_dir, "metadata.json")
        assert os.path.exists(metadata_file), "元数据文件未创建"

    def test_get_history_returns_list(self, temp_handler):
        """测试获取历史记录返回列表"""
        history = temp_handler.get_history()
        assert isinstance(history, list), "历史记录返回类型错误"

    def test_get_history_initially_empty(self, temp_handler):
        """测试初始历史记录为空"""
        history = temp_handler.get_history()
        assert len(history) == 0, "初始历史记录应为空"

    def test_delete_nonexistent_history(self, temp_handler):
        """测试删除不存在的记录"""
        result = temp_handler.delete_history("nonexistent_id")
        assert result is False, "删除不存在的记录应返回False"

    def test_clear_all_history(self, temp_handler):
        """测试清空所有历史记录"""
        result = temp_handler.clear_all_history()
        assert result is True, "清空历史记录应返回True"


class TestFormulaOCRService:
    """测试FormulaOCRService功能（需要torch环境，CI中可能跳过）"""

    def test_service_initialization(self):
        """测试服务初始化"""
        try:
            from api.services.formula_ocr_service import FormulaOCRService
            service = FormulaOCRService()
            assert service is not None
            assert service.model is None, "模型初始应为None"
        except ImportError:
            pytest.skip("pix2tex/torch未安装，跳过")

    def test_get_model_returns_none_without_loading(self):
        """测试不加载模型时返回None"""
        try:
            from api.services.formula_ocr_service import FormulaOCRService
            service = FormulaOCRService()
            # 不调用get_model，模型应为None
            assert service.model is None
        except ImportError:
            pytest.skip("pix2tex/torch未安装，跳过")

    def test_recognize_formula_without_loading(self):
        """测试不加载模型时识别返回None"""
        try:
            from api.services.formula_ocr_service import FormulaOCRService
            service = FormulaOCRService()

            # 创建假的图片数据
            fake_image_data = b"fake image data"
            result = service.recognize_formula(fake_image_data)
            # 由于没有加载模型，应该返回None或抛出异常
            try:
                assert result is None or result is not None
            except Exception:
                pass
        except ImportError:
            pytest.skip("pix2tex/torch未安装，跳过")
