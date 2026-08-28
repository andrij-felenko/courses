# Варіант 2: вибірковий імпорт атрибута
from math import sqrt

# Байткод CPython:
# 0 LOAD_CONST     0 (0)         [level = 0]
# 2 LOAD_CONST     1 (('sqrt',)) [fromlist = ('sqrt',)]
# 4 IMPORT_NAME    0 (math)      [завантажує модуль math на вершину стека]
# 6 IMPORT_FROM    1 (sqrt)      [видобуває функцію sqrt на стек]
# 8 STORE_NAME     1 (sqrt)      [зберігає sqrt у локальний простір]
# 10 POP_TOP                     [скидає об'єкт модуля math зі стека]
