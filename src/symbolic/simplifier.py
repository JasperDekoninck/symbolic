from .base import *
from copy import deepcopy


def equality(expression1, expression2, not_use_algorithms=None):
    """
    Checks whether or not two expressions are the same
    :param expression1: Expression of type Base
    :param expression2: Expression of type Base
    :param not_use_algorithms: Algorithms you shouldn't use for simplification
    :return: Boolean
    """
    # for now it is a rather easy statement
    if expression1 is None and expression2 is None:
        return True
    elif expression1 is None:
        return False
    elif expression2 is None:
        return False
    elif str(expression2) == str(expression1):
        return True

    simplified = simplify(expression1 - expression2, not_use_algorithms=not_use_algorithms)
    return simplified.calculate() == 0


def simplify(expression, not_use_algorithms=None):
    """
    Simplifies the given expression by using all algorithms below
    :param expression: Base,expression
    :param not_use_algorithms: Algorithms you shouldn't use for simplification
    :return: simplified expression
    """
    expression = deepcopy(expression)
    algorithms = [remove_redundant_operations, add_subtract_simplification, multiply_divide_simplification,
                  separate_division_multiplication_constant, factorize]

    if not_use_algorithms is not None:
        for algorithm in not_use_algorithms:
            if algorithm in algorithms:
                algorithms.remove(algorithm)

    while True:
        old_express_string = expression.latexify(use_value=False)
        for algorithm in algorithms:
            expression = algorithm(expression)
        if old_express_string == expression.latexify(use_value=False):
            break

    return expression

def get_terms_add_subtract_operation(expression):
    """
    Gets terms within an add an subtract operation in list
    :param expression: expression from which to extraxt the terms
    :return: list of terms
    example: expression = x + y + z + 2 * x - 3, returns: [x, y, z, 2 * x, -3]
    """
    if not isinstance(expression, (Add, Subtract)):
        return [expression]
    if isinstance(expression, Add):
        terms = get_terms_add_subtract_operation(expression.x)
        terms_extra = get_terms_add_subtract_operation(expression.y)
        return terms + terms_extra
    if isinstance(expression, Subtract):
        terms = get_terms_add_subtract_operation(expression.x)
        terms_extra = get_terms_add_subtract_operation(expression.y)
        terms_extra = [- term for term in list(terms_extra)]
        return terms + terms_extra


def get_factors_multiply_divide_operation(expression):
    """
    Gets factors within an multiply an divide operation in list
    :param expression: expression from which to extraxt the factors
    :return: list of factors
    example: expression = x * z * (2 + y) / x, returns: [x, z, (2 + y), x ** (-1)]
    """
    if not isinstance(expression, (Multiply, Divide)):
        return [expression]
    if isinstance(expression, Multiply):
        factors = get_factors_multiply_divide_operation(expression.x)
        factors_extra = get_factors_multiply_divide_operation(expression.y)
        return factors + factors_extra
    if isinstance(expression, Divide):
        factors = get_terms_add_subtract_operation(expression.x)
        factors_extra = get_terms_add_subtract_operation(expression.y)
        factors_extra = [term ** (-1) for term in list(factors_extra)]
        return factors + factors_extra


def get_factors_other_operation(expression, commutative_class):
    """
   Gets factors within a certain commutative operation operation in list
   :param expression: expression from which to extraxt the factors
   :param commutative_class: the commutative operation form wich to extract the terms
   :return: list of factors
   example: expression = Class(x, Class(2 + y, Class(z))), returns: [x, (2 + y), z]
   """
    if not isinstance(expression, commutative_class):
        return [expression]
    if isinstance(expression, commutative_class):
        factors = get_factors_other_operation(expression.x, commutative_class)
        factors_extra = get_factors_other_operation(expression.y, commutative_class)
        return factors + factors_extra


def commutative_equality_check_part(factors1, factors2):
    """
    Checks if the given factors are the same in different order
    :param factors1: list of factors or terms
    :param factors2: list of factors or terms
    :return: Boolean indicating whether or not they are equal
    """
    for factor in factors1:
        index = None
        for i, factor2 in enumerate(factors2):
            if commutative_equality_check(factor, factor2):
                index = i
                break
        if index is not None:
            factors2 = factors2[:index] + factors2[index + 1:]

    return len(factors2) == 0


def commutative_equality_check(expression1, expression2):
    """
    Checks whether or not the given expressions are equal using a simplified version of the equality check algorithm:
    the algorithm checks for commutative operations if the factors of the operations are the same but in a different
    order
    :param expression1: expression
    :param expression2: expression
    :return: Boolean indicating whether or not they are equal
    """
    if str(expression1) == str(expression2):
        return True
    elif isinstance(expression1, Constant):
        return expression1.value == expression2.value
    elif isinstance(expression1, BaseOperator2):

        if not isinstance(expression2, BaseOperator2):
            return False
        elif isinstance(expression1, (Add, Subtract)):
            if not isinstance(expression2, (Add, Subtract)):
                return False
            terms1 = get_terms_add_subtract_operation(expression1)
            terms2 = get_terms_add_subtract_operation(expression2)
            return commutative_equality_check_part(terms1, terms2)
        elif isinstance(expression1, (Multiply, Divide)):
            if not isinstance(expression2, (Multiply, Divide)):
                return False
            factors1 = get_factors_multiply_divide_operation(expression1)
            factors2 = get_factors_multiply_divide_operation(expression2)
            return commutative_equality_check_part(factors1, factors2)
        elif expression1.commutative:
            if not isinstance(expression2, expression1.__class__):
                return False
            factors1 = get_factors_other_operation(expression1, expression1.__class__)
            factors2 = get_factors_other_operation(expression2,  expression1.__class__)
            return commutative_equality_check_part(factors1, factors2)
        return False

    elif isinstance(expression1, BaseOperator1) and isinstance(expression2, expression1.__class__):
        return commutative_equality_check(expression1.x, expression2.x)

    return False


def remove_redundant_operations_recursive(expression):
    """
    removes operations of the type a + 0, 1 * a, a / 1, ... in recursive manner
    :param expression: Expression of type Base
    :return: Simplified expression
    """
    expression = deepcopy(expression)
    if expression.calculate() is not None:
        return Constant(expression.calculate())
    if isinstance(expression, Add):
        if expression.x.value is not None and expression.x.value == 0:
            return remove_redundant_operations_recursive(expression.y)
        elif expression.y.value is not None and expression.y.value == 0:
            return remove_redundant_operations_recursive(expression.x)
        else:
            expression.x = remove_redundant_operations_recursive(expression.x)
            expression.y = remove_redundant_operations_recursive(expression.y)
            return expression
    elif isinstance(expression, Subtract):
        if expression.x.value is not None and expression.x.value == 0:
            return remove_redundant_operations_recursive(- expression.y)
        elif expression.y.value is not None and expression.y.value == 0:
            return remove_redundant_operations_recursive(expression.x)
        else:
            expression.x = remove_redundant_operations_recursive(expression.x)
            expression.y = remove_redundant_operations_recursive(expression.y)
            return expression
    elif isinstance(expression, Multiply):
        if expression.x.value is not None and expression.x.value == 1:
            return remove_redundant_operations_recursive(expression.y)
        elif expression.x.value is not None and expression.x.value == 0:
            return Constant(0)
        elif expression.y.value is not None and expression.y.value == 1:
            return remove_redundant_operations_recursive(expression.x)
        elif expression.y.value is not None and expression.y.value == 0:
            return Constant(0)
        else:
            expression.x = remove_redundant_operations_recursive(expression.x)
            expression.y = remove_redundant_operations_recursive(expression.y)
            return expression
    elif isinstance(expression, Divide):
        if expression.y.value is not None and expression.y.value == 1:
            return remove_redundant_operations_recursive(expression.x)
        elif expression.x.value is not None and expression.x.value == 0:
            return Constant(0)
        else:
            expression.x = remove_redundant_operations_recursive(expression.x)
            expression.y = remove_redundant_operations_recursive(expression.y)
            return expression
    elif isinstance(expression, Power):
        if expression.y.value is not None and expression.y.value == 1:
            return remove_redundant_operations_recursive(expression.x)
        if expression.y.value is not None and expression.y.value == 0:
            return Constant(1)
        elif expression.x.value is not None and expression.x.value == 0:
            return Constant(0)
        elif expression.x.value is not None and expression.x.value == 1:
            return Constant(1)
        else:
            expression.x = remove_redundant_operations_recursive(expression.x)
            expression.y = remove_redundant_operations_recursive(expression.y)
            return expression
    elif isinstance(expression, (Symbol, Constant)):
        return expression
    else:
        expression.x = remove_redundant_operations_recursive(expression.x)
        expression.y = remove_redundant_operations_recursive(expression.y)
        return expression


def remove_redundant_operations(expression):
    """
    removes operations of the type a + 0, 1 * a, a / 1, ...
    :param expression: Expression of type Base
    :return: Simplified expression
    """
    new_expression = deepcopy(expression)
    while True:
        old_express_string = new_expression.latexify(use_value=False)
        new_expression = remove_redundant_operations_recursive(new_expression)
        if new_expression.latexify(use_value=False) == old_express_string:
            break

    return new_expression


def get_terms(expression):
    """
    Groups two things if they add to the same symbol/expression. Recursive function to actually do the calculations
    :param expression: Expression of type base
    :return: simplified expression
    example: a dictionary grouping all the different elements with their factors
    """
    expression = deepcopy(expression)
    if isinstance(expression, Add):
        extra_symbols = get_terms(expression.x)
        extra_symbols_y = get_terms(expression.y)
        for symb in extra_symbols_y:
            for extra_symb in extra_symbols:
                # If you want, you could use the better algorithm "equality" without the algorithm add_subtract, but
                # this takes much longer and the difference between the two is negligable
                if commutative_equality_check(symb, extra_symb):
                    extra_symbols[extra_symb] += extra_symbols_y[symb]
                    break
            else:
                extra_symbols[symb] = extra_symbols_y[symb]
        return extra_symbols

    elif isinstance(expression, Subtract):
        extra_symbols = get_terms(expression.x)
        extra_symbols_y = get_terms(expression.y)
        for symb in extra_symbols_y:
            for extra_symb in extra_symbols:
                # If you want, you could use the better algorithm "equality" without the algorithm add_subtract, but
                # this takes much longer and the difference between the two is negligable
                if commutative_equality_check(symb, extra_symb):
                    extra_symbols[extra_symb] -= extra_symbols_y[symb]
                    break
            else:
                extra_symbols[symb] = - extra_symbols_y[symb]
        return extra_symbols

    elif isinstance(expression, Multiply):
        if expression.x.value is not None:
            extra_symbols = get_terms(expression.y)
            for el in extra_symbols:
                extra_symbols[el] *= expression.x.value
            return extra_symbols

        if expression.y.value is not None:
            extra_symbols = get_terms(expression.x)
            for el in extra_symbols:
                extra_symbols[el] *= expression.y.value
            return extra_symbols

    elif isinstance(expression, Divide):
        if expression.y.value is not None:
            extra_symbols = get_terms(expression.x)
            for el in extra_symbols:
                extra_symbols[el] /= expression.y.value
            return extra_symbols

    elif expression.value is not None:
        return {None: expression.value}

    return {expression: 1}


def add_subtract_simplification(expression):
    """
    Groups two things if they add to the same symbol/expression
    :param expression: Expression of type base
    :return: simplified expression
    example: 1 + 2 * x + 3 * x - z + y * 3 + x / 2 - x + y + x ** 2 + x ** 2 + z + 3 -> 4 + 4.5 * x + 4 * y + 2 * x^{2}
    """
    expression = deepcopy(expression)
    elements = get_terms(expression)
    output_expression = None
    for element in elements:
        if element is None:
            to_add = Constant(elements[element])
        else:
            to_add = elements[element] * element

        if output_expression is None:
            output_expression = to_add
        else:
            output_expression = output_expression + to_add

    output_expression = remove_redundant_operations(output_expression)

    if isinstance(output_expression, BaseOperator1):
        output_expression.x = add_subtract_simplification(output_expression.x)
        if isinstance(output_expression, BaseOperator2):
            output_expression.y = add_subtract_simplification(output_expression.y)

    return output_expression


def get_factors(expression):
    """
    Gets the factors of a certain multiplication, power or division
    :param expression: Base, expression
    :return: a simplified expression
    Example: x ** 2 * 2 * x * y * z / (x ** 2 * z) -> {x: 1, z: 0, y: 1}
    """
    expression = deepcopy(expression)
    if isinstance(expression, Multiply):
        extra_symbols = get_factors(expression.x)
        extra_symbols_y = get_factors(expression.y)
        for symb in extra_symbols_y:
            for extra_symb in extra_symbols:
                # If you want, you could use the better algorithm "equality" without the algorithm multiply_divide, but
                # this takes much longer and the difference between the two is negligable
                if commutative_equality_check(symb, extra_symb):
                    extra_symbols[extra_symb] += extra_symbols_y[symb]
                    break
            else:
                extra_symbols[symb] = extra_symbols_y[symb]
        return extra_symbols

    elif isinstance(expression, Divide):
        extra_symbols = get_factors(expression.x)
        extra_symbols_y = get_factors(expression.y)
        for symb in extra_symbols_y:
            for extra_symb in extra_symbols:
                # If you want, you could use the better algorithm "equality" without the algorithm multiply_divide, but
                # this takes much longer and the difference between the two is negligable
                if commutative_equality_check(symb, extra_symb):
                    extra_symbols[extra_symb] -= extra_symbols_y[symb]
                    break
            else:
                extra_symbols[symb] = - extra_symbols_y[symb]
        return extra_symbols

    elif isinstance(expression, Power):
        extra_symbols = get_factors(expression.x)
        for el in extra_symbols:
            extra_symbols[el] = expression.y * extra_symbols[el]

        return extra_symbols

    return {expression: 1}


def multiply_divide_simplification(expression):
    """
    Simplifies the given expression by using some arithmetic with multiplication, division and powers
    :param expression: Base, expression
    :return: a simplified expression
    Example: x * x ** 2 * (x + y) ** (z + 3) * (.x * y ** 2) ** 2 -> x ** 5 * (x + y) ** (z + 3) * y ** 4
    Example 2: 2 ** (x + 3) * 2 ** (3 + y) + x * x ** 2 -> 2 ** (x + 3 + 3 + y) + x ** 3
    """
    expression = deepcopy(expression)
    elements = get_factors(expression)
    output_expression = None
    for element in elements:
        if output_expression is None:
            output_expression = element ** elements[element]
        else:
            output_expression = output_expression * element ** elements[element]

    output_expression = remove_redundant_operations(output_expression)
    if isinstance(output_expression, BaseOperator1):
        output_expression.x = multiply_divide_simplification(output_expression.x)
        if isinstance(output_expression, BaseOperator2):
            output_expression.y = multiply_divide_simplification(output_expression.y)

    return output_expression


def separate_division_multiplication_constant(expression):
    """
    If a sum is divided by one constant, seperate it. If a sum is multiplied by a constant, seperate it
    :param expression: Base, expression
    :return: simplified expression
    """
    expression = deepcopy(expression)
    if isinstance(expression, Multiply):
        if isinstance(expression.x, Constant) and isinstance(expression.y, Add):
            expression = expression.x * expression.y.x + expression.x * expression.y.y
        elif isinstance(expression.x, Constant) and isinstance(expression.y, Subtract):
            expression = expression.x * expression.y.x - expression.x * expression.y.y
        elif isinstance(expression.y, Constant) and isinstance(expression.x, Add):
            expression = expression.y * expression.x.x + expression.y * expression.x.y
        elif isinstance(expression.y, Constant) and isinstance(expression.x, Subtract):
            expression = expression.y * expression.x.x - expression.y * expression.x.y
    elif isinstance(expression, Divide):
        if isinstance(expression.y, Constant) and isinstance(expression.x, Add):
            expression = expression.x.x / expression.y + expression.x.y / expression.y
        elif isinstance(expression.y, Constant) and isinstance(expression.x, Subtract):
            expression = expression.x.x / expression.y - expression.x.y / expression.y

    if isinstance(expression, BaseOperator1):
        expression.x = separate_division_multiplication_constant(expression.x)
        if isinstance(expression, BaseOperator2):
            expression.y = separate_division_multiplication_constant(expression.y)
    expression = remove_redundant_operations(expression)
    return expression


def get_factors_addition(expression):
    """
    Gets all factors in every addition/subtraction
    :param expression: expression
    :return: lsit of dictionary, each dictionary containing all factors in a given
    """
    expression = deepcopy(expression)
    if isinstance(expression, Add):
        factors_x = get_factors_addition(expression.x)
        factors_y = get_factors_addition(expression.y)
        return factors_x + factors_y
    elif isinstance(expression, Subtract):
        factors_x = get_factors_addition(expression.x)
        factors_y = get_factors_addition(expression.y)
        factors_y = [- factor for factor in factors_y]
        return factors_x + factors_y
    else:
        return [get_factors(expression)]


def get_common_factors(factors):
    """
    removes all the factors that don't appear as keys in each dictionary of factors
    :param factors: list of dictionaries
    :return:
    """
    possible_factors = list(factors[0].keys())
    possible_factors2 = list(possible_factors)
    for factor in factors[1:]:
        for key in possible_factors:
            contains_key = False
            for fact in factor:
                if commutative_equality_check(key, fact):
                    contains_key = True
                    break

            if not contains_key and key in possible_factors2:
                possible_factors2.remove(key)

    output_factors = []
    for factor in factors:
        new_factor = dict()
        for element in factor:
            for other_element in possible_factors2:
                if commutative_equality_check(other_element, element):
                    new_factor[element] = factor[element]
                    break

        output_factors.append(new_factor)

    return output_factors


def get_highest_power_common_factors(factors):
    """
    Gets the highest power of each common factor appearing in every term. assumes that get_common_factors
    is already run on factors
    :param factors: list of dictionaries with expressions as keys (the base op the power) and dictionaries as values
     (the exponent of the power)
    :return:
    """
    possibilities = factors[0].keys()
    common_factors = dict()
    for possibility in possibilities:
        possible_powers = factors[0][possibility]
        for factor in factors[1:]:
            possible_powers2 = None
            for factor_possibility in factor.keys():
                if commutative_equality_check(factor_possibility, possibility):
                    possible_powers2 = factor[factor_possibility]
                    break

            deleted_keys = []
            for key in possible_powers:
                found_common_key = False
                for key2 in possible_powers2:
                    if commutative_equality_check(key, key2):
                        possible_powers[key] = min(possible_powers[key], possible_powers2[key2])
                        found_common_key = True
                if not found_common_key:
                    deleted_keys.append(key)

            for key in deleted_keys:
                del possible_powers[key]

        common_factors[possibility] = possible_powers

    for common_factor in common_factors:
        new_factor = None
        for power in common_factors[common_factor]:
            if new_factor is not None:
                if power is not None:
                    new_factor += power * common_factors[common_factor][power]
                else:
                    new_factor += common_factors[common_factor][power]
            else:
                if power is not None:
                    new_factor = common_factors[common_factor][power]
                else:
                    new_factor = common_factors[common_factor][power]
        common_factors[common_factor] = new_factor

    return common_factors


def factorize(expression):
    """
    Factorizes the given expression
    :param expression: Base, expression
    :return: factorized expression
    """
    expression = deepcopy(expression)
    factors = get_factors_addition(expression)
    common_factors = get_common_factors(factors)

    for dictionary in common_factors:
        for element in dictionary:
            if not isinstance(dictionary[element], Base):
                dictionary[element] = {None: dictionary[element]}
            else:
                dictionary[element] = get_terms(dictionary[element])

    common_factors = get_highest_power_common_factors(common_factors)

    output_expression = 1
    for common_factor in common_factors:
        output_expression *= common_factor ** common_factors[common_factor]

    output_expression_second_part = None

    terms = get_terms(expression)
    for term in terms:
        if output_expression_second_part is None:
            if term is not None:
                output_expression_second_part = multiply_divide_simplification(terms[term] * term / output_expression)
            else:
                output_expression_second_part = multiply_divide_simplification(terms[term] / output_expression)
        else:
            if term is not None:
                output_expression_second_part += multiply_divide_simplification(terms[term] * term / output_expression)
            else:
                output_expression_second_part += multiply_divide_simplification(terms[term] / output_expression)

    return remove_redundant_operations(output_expression * output_expression_second_part)
