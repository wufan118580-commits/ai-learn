"""
MathML转换功能测试
用于验证LaTeX到MathML的转换功能
"""
import pytest


class TestMathMLDependencies:
    """测试MathML转换依赖包"""

    def test_latex2mathml_installed(self):
        """测试latex2mathml是否已安装"""
        try:
            from latex2mathml.converter import convert as latex_to_mathml
            assert latex_to_mathml is not None
        except ImportError:
            pytest.fail("latex2mathml未安装，请运行: pip install latex2mathml>=3.76.0")


class TestMathMLConversion:
    """测试MathML转换功能"""

    def test_mass_energy_equation(self):
        """测试质能方程转换"""
        from latex2mathml.converter import convert as latex_to_mathml

        latex = r"E = mc^2"
        mathml_code = latex_to_mathml(latex)

        assert mathml_code is not None, "MathML转换失败"
        assert isinstance(mathml_code, str), "MathML应为字符串类型"
        # 检查是否包含基本的MathML标签
        assert '<mi>' in mathml_code or '<msup>' in mathml_code, "MathML格式不正确"

    def test_fraction_addition(self):
        """测试分数加法转换"""
        from latex2mathml.converter import convert as latex_to_mathml

        latex = r"\frac{a}{b} + \frac{c}{d}"
        mathml_code = latex_to_mathml(latex)

        assert mathml_code is not None, "MathML转换失败"
        assert '<mfrac>' in mathml_code, "缺少分数标签"

    def test_integral(self):
        """测试积分转换"""
        from latex2mathml.converter import convert as latex_to_mathml

        latex = r"\int_{0}^{\infty} e^{-x^2} dx = \frac{\sqrt{\pi}}{2}"
        mathml_code = latex_to_mathml(latex)

        assert mathml_code is not None, "MathML转换失败"
        assert '<mrow>' in mathml_code, "MathML格式不正确"

    def test_summation(self):
        """测试求和公式转换"""
        from latex2mathml.converter import convert as latex_to_mathml

        latex = r"\sum_{i=1}^{n} i = \frac{n(n+1)}{2}"
        mathml_code = latex_to_mathml(latex)

        assert mathml_code is not None, "MathML转换失败"

    def test_quadratic_formula(self):
        """测试二次方程求根公式转换"""
        from latex2mathml.converter import convert as latex_to_mathml

        latex = r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}"
        mathml_code = latex_to_mathml(latex)

        assert mathml_code is not None, "MathML转换失败"
        assert '<mroot>' in mathml_code or '<msqrt>' in mathml_code, "缺少平方根标签"

    def test_mathml_wrapper(self):
        """测试MathML包装格式"""
        from latex2mathml.converter import convert as latex_to_mathml

        latex = r"E = mc^2"
        mathml_code = latex_to_mathml(latex)

        # 检查latex2mathml已经包含了math标签
        assert mathml_code.startswith('<math'), "MathML应以<math>标签开头"
        assert 'xmlns="http://www.w3.org/1998/Math/MathML"' in mathml_code, "缺少MathML命名空间"
        assert mathml_code.endswith('</math>'), "MathML应以</math>标签结尾"

        # 检查没有双层嵌套
        math_count = mathml_code.count('<math')
        assert math_count == 1, f"应该只有一层math标签，但检测到{math_count}层"

    def test_multiple_formulas(self):
        """测试批量转换多个公式"""
        from latex2mathml.converter import convert as latex_to_mathml

        formulas = [
            r"E = mc^2",
            r"\frac{a}{b}",
            r"x^2 + y^2 = z^2"
        ]

        results = []
        for latex in formulas:
            try:
                mathml_code = latex_to_mathml(latex)
                results.append(mathml_code is not None)
            except Exception:
                results.append(False)

        assert all(results), "所有公式转换应成功"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

