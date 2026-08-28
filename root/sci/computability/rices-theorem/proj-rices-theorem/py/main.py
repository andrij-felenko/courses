import ast
import types

def build_rice_gadget(target_fn_code: str, target_arg: int, oracle_fn_code: str) -> types.CodeType:
    """
    Синтезує функцію Q(x) за принципом s-m-n теореми Кліні:
      1. Запустити target_fn(target_arg)
      2. Якщо завершилось — виконати oracle_fn(x)
    """
    gadget_source = f"""
def generated_gadget(x):
    # Крок 1: Емуляція цільової машини M на вході w
    def _target():
{target_fn_code}
    _target()({target_arg})

    # Крок 2: Корисне обчислення g(x), якщо M(w) зупинилася
    def _oracle(n):
{oracle_fn_code}
    return _oracle(x)
"""
    parsed_ast = ast.parse(gadget_source)
    compiled_code = compile(parsed_ast, filename="<rice_gadget>", mode="exec")
    
    namespace = {}
    exec(compiled_code, namespace)
    return namespace["generated_gadget"]

# Приклад 1: Програма, що гарантовано зупиняється
halting_program = """        return lambda arg: arg + 1"""

# Приклад 2: Програма з нескінченним циклом
looping_program = """        def loop(arg):
            while True:
                pass
        return loop"""

# Цільова семантична функція g(x) = x * 2 (елемент класу P)
oracle_program = """        return n * 2"""

# Синтезуємо ґаджет для програми, що спиняється:
gadget_halts = build_rice_gadget(halting_program, 10, oracle_program)
print("Результат ґаджета для програми, що спиняється:", gadget_halts(5)) # Надрукує 10 (g(5))

# Синтезуємо ґаджет для програми, що зависає:
gadget_loops = build_rice_gadget(looping_program, 0, oracle_program)
# Виклик gadget_loops(5) ніколи не поверне управління, обчислюючи скрізь невизначену функцію f_empty
