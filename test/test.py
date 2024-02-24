from symbolic.base import *
from symbolic.simplifier import *
import unittest
import numpy as np


class TestOperations(unittest.TestCase):
    def assertArrayAlmostEqual(self, first, second, decimals=7):
        result = np.sum(np.round(first - second, decimals))
        self.assertEqual(result, 0)

    def setUp(self):
        self.x = Symbol("x")
        self.y = Symbol("y")
        self.z = Symbol("z")

    def test_add(self):
        computation = self.x + self.y
        self.assertEqual(str(computation), "x + y")
        calculation = computation.calculate({"x": 2.2, "y": 3.3})
        self.assertAlmostEqual(calculation, 5.5)
        calculation = computation.calculate({"x": np.arange(0, 100), "y": np.arange(1, 101)})
        self.assertArrayAlmostEqual(calculation, np.arange(1, 201, 2))

    def test_subtract(self):
        computation = self.x - self.y
        self.assertEqual(str(computation), "x - y")
        calculation = computation.calculate({"x": 2.2, "y": 3.3})
        self.assertAlmostEqual(calculation, -1.1)
        calculation = computation.calculate({"x": np.arange(0, 100), "y": np.arange(1, 201, 2)})
        self.assertArrayAlmostEqual(calculation, np.arange(-1, -101, -1))

    def test_add_subtract(self):
        computation = self.x - self.y + self.y
        self.assertEqual(str(computation), "x - y + y")
        calculation = computation.calculate({"x": np.arange(0, 100), "y": np.arange(1, 201, 2)})
        self.assertArrayAlmostEqual(calculation, np.arange(0, 100))

    def test_multiply(self):
        computation = self.x * self.y
        self.assertEqual(str(computation), r"x \cdot y")
        calculation = computation.calculate({"x": 2, "y": 3})
        self.assertAlmostEqual(calculation, 6)
        calculation = computation.calculate({"x": np.arange(0, 100), "y": np.arange(1, 101)})
        self.assertArrayAlmostEqual(calculation, np.array([n * (n + 1) for n in range(100)]))

    def test_divide(self):
        computation = self.x / self.y
        self.assertEqual(str(computation), r"\frac{x}{y}")
        calculation = computation.calculate({"x": 9, "y": 3})
        self.assertAlmostEqual(calculation, 3)
        calculation = computation.calculate({"x": np.arange(0, 100), "y": np.arange(1, 101, 1)})
        self.assertArrayAlmostEqual(calculation, np.array([n / (n + 1) for n in range(100)]))

    def test_divide_multiply(self):
        computation = self.x / self.y * self.y
        self.assertEqual(str(computation), r"\frac{x}{y} \cdot y")
        calculation = computation.calculate({"x": np.arange(0, 100), "y": np.arange(1, 201, 2)})
        self.assertArrayAlmostEqual(calculation, np.arange(0, 100))

    def test_power(self):
        computation = self.x ** self.y
        self.assertEqual(str(computation), r"x^{y}")
        calculation = computation.calculate({"x": np.arange(2, 4), "y": np.arange(1, 3)})
        self.assertArrayAlmostEqual(calculation, np.array([2, 9]))

    def test_complicated_function1(self):
        computation = (self.x + self.y) / (self.x * self.y) - self.y
        self.assertEqual(str(computation), r"\frac{x + y}{x \cdot y} - y")
        calculation = computation.calculate({"x": 9, "y": 3})
        self.assertAlmostEqual(calculation, 12 / 27 - 3)

    def test_complicated_function2(self):
        computation = (self.x + self.y) * (self.x - self.y) ** self.z
        self.assertEqual(str(computation), r"\left( x + y \right) \cdot \left( x - y \right)^{z}")
        calculation = computation.calculate({"x": 9, "y": 3, "z": 2})
        self.assertAlmostEqual(calculation, (9 + 3) * (9 - 3) ** 2)
        self.x.value = 6
        self.y.value = 3
        latex = computation.latexify(use_value=True)
        self.assertEqual(latex, r"9 \cdot 3^{z}")

    def test_constant_function(self):
        computation = 3 * self.x + self.x * 3 ** self.y + self.z ** 2
        self.assertEqual(str(computation), r"3 \cdot x + x \cdot 3^{y} + z^{2}")
        calculation = computation.calculate({"x": 9, "y": 3, "z": 2})
        self.assertAlmostEqual(calculation, (9 * 3) + (9 * 3 ** 3) + 2 ** 2)

    def test_remove_redundant_simplifier(self):
        computation = self.x * 0 + 0 / self.y + 1 * self.z + 0 + self.z / 1 + self.x ** 2 / (3 * self.x + 5)
        new_expression = remove_redundant_operations(computation)
        self.assertEqual(str(new_expression), r"z + z + \frac{x^{2}}{3 \cdot x + 5}")

    def test_add_subtract_simplifier(self):
        computation = 1 + 2 * self.x + 3 * self.x - self.z + self.y * 3 + self.x / 2 - self.x + self.y + self.x ** 2 + \
                      self.x ** 2 + self.z + 3
        new_expression = add_subtract_simplification(computation)
        self.assertEqual(str(new_expression), r"4 + 4.5 \cdot x + 4 \cdot y + 2 \cdot x^{2}")

    def test_multiply_divide_simplifier(self):
        computation = self.x * self.x ** 2 * (self.x + self.y) ** (self.z + 3) * (self.x * self.y ** 2) ** 2
        new_expression = multiply_divide_simplification(computation)
        self.assertEqual(str(new_expression), r"x^{5} \cdot \left( x + y \right)^{z + 3} \cdot y^{4}")
        computation2 = 2 ** (self.x + 3) * 2 ** (3 + self.y) + self.x * self.x ** 2
        new_expression2 = multiply_divide_simplification(computation2)
        self.assertEqual(str(new_expression2), r"2^{x + 3 + 3 + y} + x^{3}")
        computation3 = self.x ** 2 / self.y * self.z ** (2 + self.y) / (self.x / self.y)
        new_expression3 = multiply_divide_simplification(computation3)
        self.assertEqual(str(new_expression3), r"x \cdot z^{2 + y}")

    def test_separate_multiplication_division_constant(self):
        computation = (self.x + self.y) / 2 + (self.x - self.y) / 2 + 2 * (self.x + self.z)
        expression = separate_division_multiplication_constant(computation)
        self.assertEqual(str(expression),
                         r"\frac{x}{2} + \frac{y}{2} + \frac{x}{2} - \frac{y}{2} + 2 \cdot x + 2 \cdot z")

    def test_simplifier(self):
        computation = (self.x * 4 + self.y * self.x - self.x ** 2 * self.x + self.x ** self.z - 2 * self.x +
                       self.x ** 3) / (self.y * self.x + self.x - 1 / 2 * self.x ** self.z + self.x +
                                       3 / 2 * self.x ** self.z)
        expression = simplify(computation)
        self.assertEqual(str(expression), r"1.0")

    def test_factorize(self):
        computation = self.x + self.x * self.y
        expression = factorize(computation)
        self.assertEqual(str(expression), r"x \cdot \left( 1 + y \right)")
        computation = self.x * self.y * (self.z + 2) + self.x ** 2 * (self.z + 2)
        expression = factorize(computation)
        self.assertEqual(str(expression), r"x \cdot \left( z + 2 \right) \cdot \left( y + x \right)")

    def test_derivative(self):
        computation = self.x + self.y
        new_expression = computation.derivative(self.x)
        self.assertEqual(str(new_expression), r"1")
        new_expression = computation.derivative(self.z)
        self.assertEqual(str(new_expression), r"0")

        computation = self.x - self.y
        new_expression = computation.derivative(self.y)
        self.assertEqual(str(new_expression), r"-1")

        computation = self.x / self.y
        new_expression = simplify(computation.derivative(self.y))
        self.assertEqual(str(new_expression), r"-1 \cdot x \cdot y^{-2}")

        computation = self.x ** 3
        new_expression = simplify(computation.derivative(self.x))
        self.assertEqual(str(new_expression), r"3 \cdot x^{2}")

        computation = Log(self.x)
        new_expression = simplify(computation.derivative(self.x))
        self.assertEqual(str(new_expression), r"x^{-1}")

    def test_error(self):
        computation = self.x + self.y
        calculation = computation.calculate_error({"x": 1, "y": 2}, {"x": 0.5, "y": 0.5})
        self.assertAlmostEqual(calculation, (0.5 ** 2 + 0.5 ** 2) ** 0.5)

        computation = self.x - self.y
        calculation = computation.calculate_error({"x": 1, "y": 2}, {"x": 0.5, "y": 0.5})
        self.assertAlmostEqual(calculation, (0.5 ** 2 + 0.5 ** 2) ** 0.5)

        computation = self.x * self.y
        calculation = computation.calculate_error({"x": 1, "y": 2}, {"x": 0.5, "y": 0.5})
        self.assertAlmostEqual(calculation, (2 ** 2 * 0.5 ** 2 + 0.5 ** 2) ** 0.5)

        computation = self.x / self.y
        calculation = computation.calculate_error({"x": 1, "y": 2}, {"x": 0.5, "y": 0.5})
        self.assertAlmostEqual(calculation, (1 / 4 * 0.5 ** 2 + 1 / 16 * 0.5 ** 2) ** 0.5)


if __name__ == '__main__':
    unittest.main()
