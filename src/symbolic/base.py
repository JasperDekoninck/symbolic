from math import log, e


class Base:
    """
    Base class for the Symbols and operations such that every operation can be easily defined for both of them.
    """
    # When the operation should be done, important for latexify because of brackets
    order_of_operation = 99999  # should be high, because no brackets around symbol or Constant

    def __init__(self, name=None, value=None, error=None):
        """
            Initialize for the symbol
            :param name: the name of the symbol, the way in which it should appear in expressions.
            :param value: the value of the variable, can be anything from None to a number to a numpy matrix/array
            :param error: error of the variable
            """
        self.name = name
        self.value = value
        self.error = error

    def calculate(self, parameters=None):
        """
        Calculates the value of the symbol in a calculation
        :param parameters: dict, if the name of the symbol is in the dict, it will take the value of the key in the
                            dict
        :return: the value of the symbol in a calculation
        """
        if parameters is not None and self.name in parameters:
            return parameters[self.name]
        else:
            return self.value

    def calculate_error(self, parameters=None, error_parameters=None):
        """
        Calculates the value of the symbol and the error on the symbol in a calculation
        :param parameters: dict, if the name of the symbol is in the dict, it will take the value of the key in the
                            dict
        :param error_parameters: dict, if the name of the symbol is in the dict, it will take the value of the key in
                                        the dict
        :return: the error of the symbol in a calculation
        """
        if error_parameters is not None and self.name in error_parameters:
            return error_parameters[self.name]
        else:
            return self.error

    def calculate_all(self, parameters, error_parameters):
        """
        Calculates the error of the symbol and the error on the symbol in a calculation
        :param parameters: dict, if the name of the symbol is in the dict, it will take the value of the key in the
                            dict
        :param error_parameters: dict, if the name of the symbol is in the dict, it will take the value of the key in
                                        the dict
        :return: the value of the symbol in a calculation
        """
        return self.calculate(parameters), self.calculate_error(error_parameters)

    def latexify(self, use_value=True):
        """
        Turns the symbol into latex code
        :param use_value: If True, the symbol will be displayed as its value if the value is a number
        :return: the latex code for the symbol
        """
        if is_numerical(self.value) and use_value:
            return str(self.value)
        else:
            return str(self.name)

    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __sub__(self, other):
        return Subtract(self, other)

    def __rsub__(self, other):
        return Subtract(other, self)

    def __mul__(self, other):
        return Multiply(self, other)

    def __rmul__(self, other):
        return Multiply(other, self)

    def __truediv__(self, other):
        return Divide(self, other)

    def __rtruediv__(self, other):
        return Divide(other, self)

    def __pow__(self, power, modulo=None):
        return Power(self, power)

    def __rpow__(self, other):
        return Power(other, self)

    def __neg__(self):
        return Multiply(-1, self)
    
    def __equal__(self, other):
        if not isinstance(other, Symbol):
            return False
        return self.name == other.name


def is_numerical(variable):
    """
    Checks whether or not the given variable is a number or not.
    :param variable: A random variable that needs to be checked.
    :return: True if variable is a number otherwise False
    """
    try:
        float(variable)
        return True
    except Exception:
        return False


class Symbol(Base):
    """
    Class for defining Symbolic variables for expressions
    """
    def get_dependent_symbols(self):
        """
        Returns the symbols on which the expression depends
        :return: set(self)
        """
        return {self}

    def derivative(self, x):
        """
        derivatives the Symbol with respect to the given Symbol
        :param x: Symbol
        :return: derivative
        """
        assert isinstance(x, Symbol)
        if self.__equal__(x):
            return Constant(1)
        return Constant(0)
    
    def __equal__(self, other):
        if not isinstance(other, Symbol):
            return False
        return self.name == other.name

    def __str__(self):
        """
        String of the symbol
        :return: the latexified code without value.
        """
        return self.latexify()


class Constant(Base):
    """
    Class for defining values for expressions
    """

    def __init__(self, value=None, error=None, name=None):
        super(Constant, self).__init__(name=name, value=value, error=error)

    def get_dependent_symbols(self):
        """
        Returns the symbols on which the expression depends
        :return: None
        """
        return None

    def derivative(self, x):
        """
        derivatives the Constant with respect to the given Symbol
        :param x: Symbol
        :return: derivative
        """
        assert isinstance(x, Symbol)
        return Constant(0)

    def __str__(self):
        """
        String of the symbol
        :return: the latexified code without value.
        """
        return self.latexify()

    def __lt__(self, other):
        if self.value is not None and other.value is not None:
            return self.value < other.value
        return False

    def __le__(self, other):
        if self.value is not None and other.value is not None:
            return self.value <= other.value
        return False

    def __ge__(self, other):
        if self.value is not None and other.value is not None:
            return self.value >= other.value
        return False

    def __gt__(self, other):
        if self.value is not None and other.value is not None:
            return self.value > other.value
        return False


class BaseOperator1(Base):
    """
    The base class for operators with only 1 variable (i.e. cos(x))
    """

    def __init__(self, x, name=None):
        """
        Initializes the base operator
        :param x: A variable of the Base class, or a value (that is interpreted as Constant)
        :param name: the name of the operation.
        """
        super(BaseOperator1, self).__init__(name, None, None)
        if isinstance(x, Base):
            self.x = x
        else:
            self.x = Constant(x)

    def calculate(self, parameters=None):
        """
        Base class for the calculation of the operation
        :param parameters: dict, if the name of the symbol is in the dict, it will take the value of the key in the
                            dict
        :return: the value of x for the operator
        """
        if parameters is not None and self.name in parameters:
            return parameters[self.name]
        return self.x.calculate(parameters)

    def calculate_error(self, parameters=None, error_parameters=None):
        """
        Calculates the value of the symbol and the error on the symbol in a calculation
        :param parameters: dict, if the name of the symbol is in the dict, it will take the value of the key in the
                            dict
        :param error_parameters: dict, if the name of the symbol is in the dict, it will take the value of the key in
                                        the dict
        :return: the error of the symbol in a calculation
        """
        if error_parameters is not None and self.name in error_parameters:
            return error_parameters[self.name]
        else:
            dependent_symbols = self.get_dependent_symbols()

            if dependent_symbols is not None:
                error = (sum([self.derivative(symbol).calculate(parameters) ** 2 *
                              symbol.calculate_error(parameters, error_parameters) ** 2
                              for symbol in dependent_symbols])) ** 0.5
                return error
            else:
                return None

    def latexify(self, use_value=True):
        """
        Base class for turning the operation into latex code
        :return: the latex code for the operation
        """
        calculation = self.calculate()
        if is_numerical(calculation) and use_value:
            return str(calculation)

    def get_dependent_symbols(self):
        """
        Gets the symbols on which the operation depends
        :return: set of symbols on which the expression depends
        """
        symbols_x = self.x.get_dependent_symbols()
        return symbols_x

    def derivative(self, x):
        """
        derivatives the Operator with respect to the given Symbol
        :param x: Symbol
        :return: derivative
        """
        return Constant(0)

    def __str__(self):
        return self.latexify()


class BaseOperator2(BaseOperator1):
    """
    The base class for operators with 2 variables (i.e. x + y)
    """
    commutative = False

    def __init__(self, x, y, name=None):
        """
        Initializes the base operator
        :param x: A variable of the Base class, or a value (that is interpreted as Constant)
        :param name: the name of the operation.
        """
        super(BaseOperator2, self).__init__(x, name)

        if isinstance(y, Base):
            self.y = y
        else:
            self.y = Constant(y)

    def calculate(self, parameters=None):
        """
        Base class for the calculation of the operation
        :param parameters: dict, if the name of the symbol is in the dict, it will take the value of the key in the
                            dict
        :return: the value of x for the operator
        """
        x = super(BaseOperator2, self).calculate(parameters)
        return x, self.y.calculate(parameters)

    def bracketify(self, other, use_value=True):
        """
        Latexifies the other (most of the time, the x and y of the operation) and puts brackets around it if necessary
        :param other: Something of type Base that has a latexify option
        :param use_value: Whether or not to use the value in the latexify option
        :return: latexification
        """
        if other.order_of_operation < self.order_of_operation and not is_numerical(other.latexify(use_value)) \
                and not other.latexify(use_value).startswith(r"\left("):
            return r"\left( " + other.latexify(use_value) + r" \right)"
        else:
            return other.latexify(use_value)

    def get_dependent_symbols(self):
        """
        Gets the symbols on which the operation depends
        :return: set of symbols on which the expression depends
        """
        symbols_x = self.x.get_dependent_symbols()
        symbols_y = self.y.get_dependent_symbols()
        if symbols_x is None and symbols_y is None:
            return None
        elif symbols_x is None:
            return symbols_y
        elif symbols_y is None:
            return symbols_x
        else:

            return symbols_y.union(symbols_x)


class Add(BaseOperator2):
    """
    The addition operator for two elements from the Base class
    """
    order_of_operation = 0
    commutative = True

    def calculate(self, parameters=None):
        """
        Calculates the sum of the two elements
        :param parameters: dict, if the name of the symbol is in the dict, it will take the value of the key in the
                            dict
        :return: x + y
        """
        x, y = super(Add, self).calculate(parameters)
        if x is not None and y is not None:
            value = x + y
        else:
            value = None
        return value

    def latexify(self, use_value=True):
        result = super(Add, self).latexify(use_value)
        if result is not None:
            return result
        return self.bracketify(self.x, use_value) + r" + " + self.bracketify(self.y, use_value)

    def derivative(self, x):
        """
        derivatives the Operator with respect to the given Symbol
        :param x: Symbol
        :return: derivative
        """
        return self.x.derivative(x) + self.y.derivative(x)


class Subtract(BaseOperator2):
    """
    The subtract operator for two elements from the Base class
    """
    order_of_operation = 0

    def calculate(self, parameters=None):
        """
        Calculates the difference between the two elements
        :param parameters: dict, if the name of the symbol is in the dict, it will take the value of the key in the
                            dict
        :return: x - y
        """
        x, y = super(Subtract, self).calculate(parameters)
        if x is not None and y is not None:
            value = x - y
        else:
            value = None
        return value

    def latexify(self, use_value=True):
        result = super(Subtract, self).latexify(use_value)
        if result is not None:
            return result

        if isinstance(self.y, (Add, Subtract)):
            return self.bracketify(self.x, use_value) + r" - \left( " + self.y.latexify(use_value) + r"\right)"
        else:
            return self.bracketify(self.x, use_value) + r" - " + self.bracketify(self.y, use_value)

    def derivative(self, x):
        """
        derivatives the Operator with respect to the given Symbol
        :param x: Symbol
        :return: derivative
        """
        return self.x.derivative(x) - self.y.derivative(x)


class Multiply(BaseOperator2):
    """
    The multiplication operator for two elements from the Base class
    """
    order_of_operation = 1
    commutative = True

    def calculate(self, parameters=None):
        """
        Calculates the multiplication between the two elements
        :param parameters: dict, if the name of the symbol is in the dict, it will take the value of the key in the
                            dict
        :return: x * y
        """
        x, y = super(Multiply, self).calculate(parameters)
        if x is not None and y is not None:
            value = x * y
        else:
            value = None
        return value

    def latexify(self, use_value=True):
        result = super(Multiply, self).latexify(use_value)
        if result is not None:
            return result
        return self.bracketify(self.x, use_value) + r" \cdot " + self.bracketify(self.y, use_value)

    def derivative(self, x):
        """
        derivatives the Operator with respect to the given Symbol
        :param x: Symbol
        :return: derivative
        """
        return self.x.derivative(x) * self.y + self.x * self.y.derivative(x)


class Divide(BaseOperator2):
    """
    The division operator for two elements from the Base class
    """
    order_of_operation = 1

    def calculate(self, parameters=None):
        """
        Calculates the division between the two elements
        :param parameters: dict, if the name of the symbol is in the dict, it will take the value of the key in the
                            dict
        :return: x / y
        """
        x, y = super(Divide, self).calculate(parameters)
        if x is not None and y is not None:
            value = x / y
        else:
            value = None
        return value

    def latexify(self, use_value=True):
        result = super(Divide, self).latexify(use_value)
        if result is not None:
            return result
        # you don't want brackets for a division
        return r"\frac{" + self.x.latexify(use_value) + r"}{" + self.y.latexify(use_value) + r"}"

    def derivative(self, x):
        """
        derivatives the Operator with respect to the given Symbol
        :param x: Symbol
        :return: derivative
        """
        return (self.x.derivative(x) * self.y - self.x * self.y.derivative(x)) / self.y ** 2


class Power(BaseOperator2):
    """
    The power operator for two elements from the Base class
    """
    order_of_operation = 2

    def calculate(self, parameters=None):
        """
        Calculates the power of the two elements
        :param parameters: dict, if the name of the symbol is in the dict, it will take the value of the key in the
                            dict
        :return: x ** y
        """
        x, y = super(Power, self).calculate(parameters)
        if x is not None and y is not None:
            value = x ** y
        else:
            value = None
        return value

    def latexify(self, use_value=True):
        result = super(Power, self).latexify(use_value)
        if result is not None:
            return result
        # you don't want brackets in the exponent
        return self.bracketify(self.x, use_value) + r"^{" + self.y.latexify(use_value) + r"}"

    def derivative(self, x):
        """
        derivatives the Operator with respect to the given Symbol
        :param x: Symbol
        :return: derivative
        """
        return self.x ** self.y * (self.y.derivative(x) * Log(self.x) + self.y / self.x * self.x.derivative(x))


class Log(BaseOperator2):
    """
    The logarithm operator for two elements from the Base class
    """
    order_of_operation = 2

    def __init__(self, x, y=Constant(e, name="e"), name=None):
        super(Log, self).__init__(x, y, name)

    def calculate(self, parameters=None):
        """
        Calculates the power of the two elements
        :param parameters: dict, if the name of the symbol is in the dict, it will take the value of the key in the
                            dict
        :return: log_y(x)
        """
        x, y = super(Log, self).calculate(parameters)
        if x is not None and y is not None:
            value = log(x) / log(y)
        else:
            value = None
        return value

    def latexify(self, use_value=True):
        result = super(Log, self).latexify(use_value)
        if result is not None:
            return result
        # you don't want brackets in the exponent
        return r"\log_{" + self.y.latexify(use_value) + r"}" + self.bracketify(self.x, use_value)

    def derivative(self, x):
        """
        derivatives the Operator with respect to the given Symbol
        :param x: Symbol
        :return: derivative
        """
        return (1 / self.x * self.x.derivative(x) * Log(self.y) - Log(self.x) / self.y * self.y.derivative(x)) \
               / (Log(self.y) ** 2)
