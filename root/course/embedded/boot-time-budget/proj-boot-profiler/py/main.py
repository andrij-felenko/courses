import re, sys

# Рядок завантажувача: 'I (47) boot: Partition Table:'
# Беремо число в дужках — це мілісекунди від старту.
BOOT_LINE = re.compile(r'^[IWE] \((\d+)\) boot[_a-z]*:')

def last_bootloader_ms(lines):
    last = None
    for ln in lines:
        m = BOOT_LINE.search(ln)
        if m:
            last = int(m.group(1))     # перезаписуємо — лишиться остання мітка
    return last                        # мс від старту до кінця завантажувача

# приклад використання: згодувати накопичені рядки серійного виводу
ms = last_bootloader_ms(sys.stdin.readlines())
print(f"завантажувач закінчив на {ms} мс від старту" if ms is not None
      else "міток завантажувача нема — увімкніть CONFIG_BOOTLOADER_LOG_LEVEL=INFO")
