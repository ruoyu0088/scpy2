import math
import re
from sympy import cse, numbered_symbols, S, lambdify
from sympy.printing import StrPrinter


FUNC_ALIAS = {
    "asin": ["arcsin"],
    "acos": ["arccos"],
    "atan": ["arctan"],
    "atan2": ["arctan2"],
    "asinh": ["arcsinh"],
    "acosh": ["arccosh"],
    "atanh": ["arctanh"]
}


def strip_zeros(num):
    m = re.match(r"^(\d+)\.(\d+)$", num)
    if m is not None:
        p1 = m.group(1)
        p2 = m.group(2).rstrip("0")
        if not p2:
            p2 = "0"
        return "{}.{}".format(p1, p2)
    else:
        return num


class CseExprPrinter(StrPrinter):

    _default_settings = {
        "calc_number": False,
        "func_module": math,
        "order": "none"}

    def __init__(self, settings=None):
        super(CseExprPrinter, self).__init__(settings)
        self.functions = set()

    def _print(self, expr, *args, **kwargs):
        if self._settings["calc_number"] and expr.is_number:
            return strip_zeros(str(expr.evalf()))
        else:
            return super(CseExprPrinter, self)._print(expr, *args, **kwargs)

    @property
    def func_module(self):
        import math
        return self._settings.get('func_module', math)

    def _print_Integer(self, expr):
        return strip_zeros(str(expr.evalf()))

    def _print_Rational(self, expr):
        return '%s.0/%s' % (expr.p, expr.q)

    def _print_Function(self, expr):
        name = expr.func.__name__
        if not hasattr(self.func_module, name):
            for alias_name in FUNC_ALIAS[name]:
                if hasattr(self.func_module, alias_name):
                    name = alias_name
                    break
            else:
                raise ValueError("function {} not found in module {}".format(name, self.func_module))

        self.functions.add(name)
        return name + "(%s)" % self.stringify(expr.args, ", ")

    def _print_Pow(self, expr):
        exp = expr.exp
        eval_exp = exp.evalf()
        if eval_exp == 0.5:
            self.functions.add("sqrt")
            return 'sqrt(%s)' % (self._print(expr.base))
        else:
            return '(%s)**(%s)' % (self._print(expr.base), self._print(exp))


def cse2func(funcname, exprs, module=math, auto_import=True, calc_number=True, symbols="_tmp"):
    import textwrap
    printer = CseExprPrinter(settings={"func_module": module, "calc_number": calc_number})
    seq, results = cse(exprs, symbols=numbered_symbols(symbols))
    codes = ["def %s:" % funcname]
    for variable, value in seq:
        if calc_number:
            value = value.evalf()
        codes.append("%s = %s" % (variable, printer._print(value)))
    returns = "return (%s)" % ", ".join([printer._print(value) for value in results])
    codes.append('\n'.join(textwrap.wrap(returns, 80)))
    if auto_import and printer.functions:
        codes.insert(1, "from {} import {}".format(module.__name__, ", ".join(printer.functions)))
    code = '\n    '.join(codes)
    return code

if __name__ == '__main__':
    import numpy as np
    from sympy import symbols, solve, sin, atan
    a, b, c, d, x = symbols("a, b, c, d, x", real=True)
    solutions = solve(sin(1)*x**2 + atan(b)*x + c, x)
    print cse2func("test(a, b, c)", solutions, module=np, calc_number=True)
