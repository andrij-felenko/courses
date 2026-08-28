# generate_errors.py (Детерміністичний скрипт генерації)
import sys

errors = {
    "ERR_NOT_FOUND": 404,
    "ERR_ACCESS_DENIED": 403,
    "ERR_TIMEOUT": 408,
    "ERR_INTERNAL": 500,
    "ERR_BAD_GATEWAY": 502
}

with open("src/error_table.c", "w", encoding="utf-8") as f:
    f.write('/* Згенеровано автоматично (детерміністично) */\n')
    f.write('#include "calc.h"\n\n')
    f.write('const char* error_names[] = {\n')
    # Сортування ключів за абеткою гарантує однаковий порядок рядків
    for name in sorted(errors.keys()):
        f.write(f'    "{name}",\n')
    f.write('};\n')
