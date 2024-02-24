# Symbolic
This is a very simple project where I just made a symbolic calculation engine. I wrote this because in my bachelor physics we had to do so many error calculations that I wanted something that did this automatically for me. Therefore, this simple engine can define symbols, perform basic operations with them (+,*,/,-,log,pow), simplify the equation, use derivatives, print it in LaTeX notation, compute the result and the standard deviation of the result given the standard deviation on the input symbols.

## Install
First, install [Conda](https://docs.conda.io/projects/miniconda/en/latest/) and then run:

```bash
conda create -n symbolic python=3.11
conda activate symbolic
pip install -e .
python test/test.py
```

The last command performs several tests.


## Use
The following example shows the things that can be done with this simple symbolic engine.

```python
from symbolic import Symbol, simplify, Log

x = Symbol('x')
y = Symbol('y')

formula = x + y # possible operations: +, *, **, /, -, and Log
print(str(formula)) # str(formula) gives a latex representation of the equation
simplified_formula = simplify(x + y + y) # returns a simplified version of the formula given
print(simplified_formula.calculate({'x': 2, 'y': 3})) # returns 8
print(simplified_formula.calculate_error({'x': 2, 'y': 3}, {'x': 0.1, 'y': 0.1})) # computes the error on the computation given the standard deviations
print(formula.derivative(x)) # returns 1
```