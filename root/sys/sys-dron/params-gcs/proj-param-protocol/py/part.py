import struct
from dataclasses import dataclass

# Поля PARAM_VALUE, які несе кожна відповідь борту:
@dataclass
class ParamValue:
    param_value: float    # значення, ЗАВЖДИ як IEEE-754 float
    param_count: int      # скільки всього параметрів на апараті
    param_index: int      # індекс ЦЬОГО параметра (0 .. count-1)
    param_id: bytes       # ім'я; якщо рівно 16 байтів — БЕЗ \0 у кінці
    param_type: int       # як трактувати float: int8/16/32, uint…, float
