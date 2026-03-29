# 测试文件组织说明

## 测试文件结构

```
tests/
├── __init__.py                    # 测试包初始化文件
├── test_document_processor.py    # 文档处理器测试
├── test_formula.py               # 公式识别功能测试
├── test_mathml_conversion.py     # MathML转换功能测试
├── test_mermaid.py               # Mermaid图表功能测试
└── README.md                     # 本文件
```

## 测试文件说明

### 1. test_document_processor.py
- **测试对象**: 文档处理器
- **测试内容**: 文档上传、解析、处理等基础功能
- **运行命令**: `make test` 或 `pytest tests/test_document_processor.py -v`

### 2. test_formula.py
- **测试对象**: 公式识别功能
- **测试内容**:
  - 依赖包安装检查
  - 服务初始化
  - 处理器功能
  - 历史记录管理
- **运行命令**: `make test-formula` 或 `pytest tests/test_formula.py -v`

### 3. test_mathml_conversion.py
- **测试对象**: MathML转换功能
- **测试内容**:
  - latex2mathml依赖检查
  - 基础公式转换(质能方程、分数等)
  - 复杂公式转换(积分、求和、根号等)
  - MathML格式验证
  - 批量转换测试
- **运行命令**: `make test-mathml` 或 `pytest tests/test_mathml_conversion.py -v`

### 4. test_mermaid.py
- **测试对象**: Mermaid图表功能
- **测试内容**: 图表渲染、格式转换等
- **运行命令**: `make test` 或 `pytest tests/test_mermaid.py -v`

## Makefile测试命令

```bash
# 运行所有测试
make test

# 运行公式识别测试
make test-formula

# 运行MathML转换测试
make test-mathml

# 运行集成测试
make test-integration

# 运行指定测试文件
pytest tests/test_mathml_conversion.py -v

# 运行指定测试函数
pytest tests/test_mathml_conversion.py::TestMathMLConversion::test_mass_energy_equation -v

# 显示测试覆盖率
pytest tests/ --cov=src --cov-report=term-missing
```

## 测试覆盖率目标

- **核心功能测试**: 100%
- **边界条件测试**: 80%+
- **错误处理测试**: 90%+
- **集成测试**: 70%+

## CI/CD集成

测试文件已经集成到CI/CD流程中:

1. **代码提交前**: 本地运行 `make test` 确保测试通过
2. **CI检查**: 自动运行所有测试,失败则阻止合并
3. **覆盖率报告**: 生成测试覆盖率报告,用于代码质量监控

## 添加新测试

添加新测试时,请遵循以下规范:

1. **文件命名**: 使用 `test_*.py` 格式
2. **测试类**: 使用 `Test*` 格式
3. **测试方法**: 使用 `test_*` 格式
4. **文档字符串**: 每个测试都要有清晰的说明
5. **断言**: 使用有意义的断言,包含错误信息

示例:

```python
class TestNewFeature:
    """新功能测试"""

    def test_basic_functionality(self):
        """测试基础功能"""
        result = some_function()
        assert result is not None, "函数应返回有效结果"

    def test_edge_case(self):
        """测试边界情况"""
        result = some_function(param=None)
        assert result == expected_value, "边界情况处理不正确"
```

## 常见问题

### Q1: 如何运行单个测试?
```bash
pytest tests/test_mathml_conversion.py::TestMathMLConversion::test_mass_energy_equation -v
```

### Q2: 如何查看详细的测试输出?
```bash
pytest tests/ -v -s
```

### Q3: 如何调试失败的测试?
```bash
pytest tests/ -v --pdb  # 进入调试模式
pytest tests/ -v --traceback=long  # 显示完整堆栈
```

### Q4: 如何跳过某些测试?
```bash
pytest tests/ -k "not test_slow"  # 跳过慢速测试
pytest tests/ -k "test_mathml"   # 只运行mathml相关测试
```

## 测试最佳实践

1. **独立性**: 每个测试应该独立运行,不依赖其他测试
2. **可重复性**: 测试结果应该可重复,不依赖外部状态
3. **快速执行**: 单个测试应该在秒级完成
4. **清晰命名**: 测试名称应该清楚描述测试内容
5. **合理断言**: 断言应该精确,避免过度复杂
6. **错误处理**: 测试应该包含正常和异常情况
7. **文档完善**: 复杂测试需要添加注释说明

## 测试数据管理

测试数据应该放在 `tests/fixtures/` 目录下(如需要):

```
tests/
├── fixtures/
│   ├── sample_formulas/
│   ├── test_documents/
│   └── test_images/
└── ...
```

## 性能测试

对于性能相关的测试,可以使用 `pytest-benchmark`:

```bash
pip install pytest-benchmark
pytest tests/ --benchmark-only
```

## 持续改进

- 定期审查测试覆盖率
- 优化慢速测试
- 添加边界情况测试
- 更新过时的测试用例
- 改进测试文档
