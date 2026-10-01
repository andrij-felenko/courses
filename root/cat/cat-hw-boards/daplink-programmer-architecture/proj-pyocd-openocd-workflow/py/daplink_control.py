#!/usr/bin/env python3
"""
daplink_control.py

Скрипт автоматизації зневадження та прошивання мікроконтролерів ARM Cortex-M
через програматор DAPLink (CMSIS-DAP) за допомогою бібліотеки pyOCD.

Програма демонструє:
1. Ініціалізацію сесії підключення до DAPLink та цільового мікроконтролера.
2. Керування станом ядра ARM Cortex-M (halt, reset, resume).
3. Стирання Flash-пам'яті, запис бінарного образу (.bin/.hex) та верифікацію.
4. Зчитування й відображення вмісту загальних регістрів ядра (R0-R15/SP/LR/PC) та xPSR.
5. Дамп ділянок оперативної пам'яті (RAM).
6. Детальну діагностику системного стану ядра та HardFault через регістри SCB.
"""

import sys
import os
import argparse
import logging
from typing import List, Optional, Dict, Any

try:
    from pyocd.core.helpers import ConnectHelper
    from pyocd.flash.file_programmer import FileProgrammer
    from pyocd.core.target import Target
    from pyocd.core.exceptions import Error as PyOCDError
except ImportError:
    print("Помилка: Бібліотеку 'pyocd' не встановлено.")
    print("Встановіть її за допомогою команди: pip install pyocd")
    sys.exit(1)

# Адреси системних регістрів SCB (System Control Block) в ARM Cortex-M
SCB_ICSR = 0xE000ED04   # Interrupt Control and State Register
SCB_CFSR = 0xE000ED28   # Configurable Fault Status Register
SCB_HFSR = 0xE000ED2C   # HardFault Status Register
SCB_MMFAR = 0xE000ED34  # MemManage Fault Address Register
SCB_BFAR = 0xE000ED38   # BusFault Address Register

# Перелік назв основних регістрів ядра ARM Cortex-M
CORE_REGISTERS = [
    'r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7',
    'r8', 'r9', 'r10', 'r11', 'r12', 'sp', 'lr', 'pc', 'xpsr'
]


def print_header(title: str) -> None:
    """Виводить відформатований заголовок розділу."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def read_registers(target: Target) -> Dict[str, int]:
    """
    Зчитує значення загальних регістрів ядра ARM Cortex-M.

    :param target: Об'єкт цільового мікроконтролера pyOCD Target.
    :return: Словник з назвами регістрів та їхніми 32-бітними значеннями.
    """
    print_header("Зчитування регістрів ядра Cortex-M")
    
    if not target.is_halted():
        print("[!] Увага: Ядро працює. Для коректного читання регістрів виконується halt...")
        target.halt()

    reg_values = {}
    raw_values = target.read_core_register_list(CORE_REGISTERS)
    
    for name, val in zip(CORE_REGISTERS, raw_values):
        reg_values[name] = val
        print(f"  {name.upper():<6}: 0x{val:08X} ({val})")

    # Декодування xPSR
    xpsr = reg_values.get('xpsr', 0)
    isr_num = xpsr & 0x1FF
    thumb_bit = (xpsr >> 24) & 1
    print(f"\n  [xPSR Декодування]")
    print(f"    - Thumb mode (T-bit) : {'1 (Active)' if thumb_bit else '0 (FAULT - ARM state unsupported!)'}")
    print(f"    - ISR Number         : {isr_num} ({'Thread Mode' if isr_num == 0 else f'Exception Handler #{isr_num}'})")

    return reg_values


def dump_memory(target: Target, address: int, count_words: int = 16) -> List[int]:
    """
    Зчитує та відображає ділянку оперативної пам'яті (RAM) у 32-бітному форматі.

    :param target: Об'єкт target pyOCD.
    :param address: Початкова адреса пам'яті (мусить бути вирівняна по 4 байти).
    :param count_words: Кількість 32-бітних слів для зчитання.
    :return: Список зчитаних 32-бітних слів.
    """
    print_header(f"Дамп пам'яті з адреси 0x{address:08X} ({count_words} слів)")

    if address % 4 != 0:
        print("[!] Попередження: Адресу не вирівняно по 4-байтовій межі. Вирівнюємо...")
        address &= ~0x3

    try:
        words = target.read_memory_block32(address, count_words)
        
        for i in range(0, len(words), 4):
            curr_addr = address + (i * 4)
            chunk = words[i:i + 4]
            hex_str = " ".join(f"{w:08X}" for w in chunk)
            ascii_str = ""
            for w in chunk:
                for b in w.to_bytes(4, byteorder='little'):
                    ascii_str += chr(b) if 32 <= b <= 126 else "."
            print(f"  0x{curr_addr:08X}: {hex_str:<35} |{ascii_str}|")

        return words
    except PyOCDError as e:
        print(f"[-] Помилка під час зчитування пам'яті 0x{address:08X}: {e}")
        return []


def diagnose_hardfault(target: Target) -> None:
    """
    Аналізує системний стан ядра та регістри SCB для виявлення причин HardFault.

    :param target: Об'єкт target pyOCD.
    """
    print_header("Діагностика системного стану та апаратних помилок (HardFault)")

    if not target.is_halted():
        target.halt()

    try:
        icsr = target.read32(SCB_ICSR)
        cfsr = target.read32(SCB_CFSR)
        hfsr = target.read32(SCB_HFSR)
        
        vectactive = icsr & 0x1FF
        print(f"  SCB->ICSR : 0x{icsr:08X} (VECTACTIVE: {vectactive})")
        print(f"  SCB->HFSR : 0x{hfsr:08X}")
        print(f"  SCB->CFSR : 0x{cfsr:08X}")

        if vectactive == 3:
            print("  [!] ВИЯВЛЕНО АКТИВНИЙ ОБРОБНИК HardFault (Vector #3)!")
        elif vectactive != 0:
            print(f"  [*] Ядро перебуває в обробнику переривання №{vectactive}.")
        else:
            print("  [*] Ядро перебуває у звичайному режимі виконання (Thread Mode).")

        # Аналіз HFSR
        if hfsr & (1 << 30):
            print("    -> HardFault FORCED: Збій виник внаслідок ескалації звичайного Fault (Bus/Mem/Usage).")
        if hfsr & (1 << 1):
            print("    -> HardFault VECTTBL: Помилка читання таблиці векторів переривань.")

        # Аналіз CFSR (MemManage, BusFault, UsageFault)
        mmfsr = cfsr & 0xFF
        bfsr = (cfsr >> 8) & 0xFF
        ufsr = (cfsr >> 16) & 0xFFFF

        if mmfsr != 0:
            print(f"\n  [MemManage Fault (MMFSR: 0x{mmfsr:02X})]")
            if mmfsr & (1 << 0):
                print("    - IACCVIOL: Спроба виконання інструкції з непам'ятної ділянки.")
            if mmfsr & (1 << 1):
                print("    - DACCVIOL: Порушення прав доступу при читанні/запису даних.")
            if mmfsr & (1 << 3):
                print("    - MUNSTKERR: Помилка витягування контексту зі стеку при поверненні з винятку.")
            if mmfsr & (1 << 4):
                print("    - MSTKERR: Помилка збереження контексту в стек при вході у виняток.")
            if mmfsr & (1 << 7):
                mmfar = target.read32(SCB_MMFAR)
                print(f"    - MMARVALID: Адреса порушення MemManage = 0x{mmfar:08X}")

        if bfsr != 0:
            print(f"\n  [BusFault (BFSR: 0x{bfsr:02X})]")
            if bfsr & (1 << 0):
                print("    - IBUSERR: Помилка шини при вибірці інструкцій (Instruction Bus Error).")
            if bfsr & (1 << 1):
                print("    - PRECISERR: Точна помилка шини при доступі до даних (Precise Data Bus Error).")
            if bfsr & (1 << 2):
                print("    - IMPRECISERR: Неточна помилка шини при збереженні даних (Imprecise Data Bus Error).")
            if bfsr & (1 << 3):
                print("    - UNSTKERR: Помилка шини при розгортанні стеку.")
            if bfsr & (1 << 4):
                print("    - STKERR: Помилка шини при згортанні стеку.")
            if bfsr & (1 << 7):
                bfar = target.read32(SCB_BFAR)
                print(f"    - BFARVALID: Точна адреса помилки шини = 0x{bfar:08X}")

        if ufsr != 0:
            print(f"\n  [UsageFault (UFSR: 0x{ufsr:04X})]")
            if ufsr & (1 << 0):
                print("    - UNDEFINSTR: Спроба виконання невизначеної або непідтримуваної інструкції.")
            if ufsr & (1 << 1):
                print("    - INVSTATE: Спроба переходу в некоректний стан (наприклад, T-bit = 0).")
            if ufsr & (1 << 2):
                print("    - INVPC: Некоректне значення PC при поверненні з винятку (EXC_RETURN).")
            if ufsr & (1 << 3):
                print("    - NOCP: Спроба звернутися до відсутнього або вимкненого співпроцесора (наприклад, FPU).")
            if ufsr & (1 << 8):
                print("    - UNALIGNED: Спроба невирівняного доступу до пам'яті при увімкненому UNALIGN_TRP.")
            if ufsr & (1 << 9):
                print("    - DIVBYZERO: Спроба ділення на нуль при увімкненому DIV_0_TRP.")

        if cfsr == 0 and hfsr == 0:
            print("  [*] Прапори апаратних помилок у SCB відсутні.")

    except PyOCDError as e:
        print(f"[-] Не вдалося зчитати регістри SCB: {e}")


def flash_firmware(session: Any, file_path: str, base_address: Optional[int] = None) -> bool:
    """
    Прошиває бінарний або HEX-файл у Flash-пам'ять мікроконтролера з верифікацією.

    :param session: Активна сесія pyOCD ConnectHelper.
    :param file_path: Шлях до файлу прошивки (.bin, .hex, .elf).
    :param base_address: Початкова адреса у Flash (обов'язкова для .bin).
    :return: True якщо прошивання успішне, False інакше.
    """
    print_header(f"Прошивання мікроконтролера: {file_path}")

    if not os.path.isfile(file_path):
        print(f"[-] Помилка: Файл прошивки '{file_path}' не знайдено.")
        return False

    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext == '.bin' and base_address is None:
        base_address = 0x08000000
        print(f"[!] Базову адресу для BIN-файлу не вказано. Використовується за замовчуванням: 0x{base_address:08X}")

    try:
        programmer = FileProgrammer(session)
        print("[+] Запуск процедури прошивання (стирання, програмування, верифікація)...")
        programmer.program(
            file_or_path=file_path,
            base_address=base_address
        )
        print("[+] Прошивання та верифікацію успішно завершено!")
        return True
    except PyOCDError as e:
        print(f"[-] Помилка під час прошивання Flash: {e}")
        return False


def parse_args() -> argparse.ArgumentParser:
    """Налаштовує аргументи командного рядка."""
    parser = argparse.ArgumentParser(
        description="Автоматизація зневадження та прошивання ARM Cortex-M через DAPLink (pyOCD)."
    )
    parser.add_argument(
        "-t", "--target",
        default="cortex_m",
        help="Тип цільового мікроконтролера (наприклад, stm32f401xe, nrf52840, cortex_m)."
    )
    parser.add_argument(
        "-f", "--frequency",
        type=int,
        default=1000000,
        help="Тактова частота шини SWD/JTAG у Гц (за замовчуванням: 1000000 Гц = 1 МГц)."
    )
    parser.add_argument(
        "--flash",
        type=str,
        help="Шлях до файлу прошивки (.bin, .hex, .elf) для запису у Flash-пам'ять."
    )
    parser.add_argument(
        "--address",
        type=lambda x: int(x, 0),
        default=0x08000000,
        help="Адреса Flash або RAM для операцій (за замовчуванням: 0x08000000)."
    )
    parser.add_argument(
        "--ram-addr",
        type=lambda x: int(x, 0),
        default=0x20000000,
        help="Початкова адреса RAM для дампу (за замовчуванням: 0x20000000)."
    )
    parser.add_argument(
        "--ram-words",
        type=int,
        default=16,
        help="Кількість 32-бітних слів для дампу RAM (за замовчуванням: 16)."
    )
    parser.add_argument(
        "--skip-reset",
        action="store_true",
        help="Пропустити процедуру скидання (reset) після підключення."
    )
    return parser


def main() -> None:
    parser = parse_args()
    args = parser.parse_args()

    # Налаштування формату логування pyOCD
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    print_header(f"Ініціалізація підключення DAPLink (Target: {args.target})")

    # Конфігурація сесії pyOCD
    session_options = {
        'target_override': args.target,
        'frequency': args.frequency,
        'auto_unlock': True,
    }

    try:
        # Встановлення сесії зв'язку з DAPLink програматором
        with ConnectHelper.session_with_chosen_target(options=session_options) as session:
            board = session.board
            target = session.target

            print(f"[+] Програматор розпізнано: {board.name if board else 'CMSIS-DAP/DAPLink'}")
            print(f"[+] Успішне підключення до цілі: {target.part_number}")

            # Step 1: Зупинка ядра (halt) та скидання (reset)
            print_header("Керування станом ядра ARM Cortex-M")
            print("[+] Зупинка ядра (target.halt())...")
            target.halt()

            if not args.skip_reset:
                print("[+] Виконання процедури скидання із зупинкою (reset_and_halt)...")
                target.reset_and_halt()

            print(f"[+] Поточний стан ядра: {'HALTED (Зупинено)' if target.is_halted() else 'RUNNING (Працює)'}")

            # Step 2: Прошивання (якщо вказано файл)
            if args.flash:
                flash_firmware(session, args.flash, args.address)
                # Після прошивання виконати скидання ядра
                target.reset_and_halt()

            # Step 3: Зчитування регістрів ядра
            read_registers(target)

            # Step 4: Зчитування оперативної пам'яті (RAM)
            dump_memory(target, address=args.ram_addr, count_words=args.ram_words)

            # Step 5: Аналіз системного стану та HardFault
            diagnose_hardfault(target)

            # Step 6: Відновлення виконання
            print_header("Завершення сесії зневадження")
            print("[+] Відновлення виконання програми ядра (target.resume())...")
            target.resume()
            print("[+] Сесію DAPLink успішно завершено.")

    except PyOCDError as e:
        print(f"\n[-] Критична помилка pyOCD під час роботи з DAPLink: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[-] Несподівана помилка виконання: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
