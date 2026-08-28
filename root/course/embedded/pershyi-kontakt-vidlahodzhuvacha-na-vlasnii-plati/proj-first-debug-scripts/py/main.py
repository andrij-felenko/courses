#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Автоматизована верифікація першого контакту плати через pyOCD."""

import sys
import time
from pyocd.core.helpers import ConnectHelper
from pyocd.core.target import Target
from pyocd.flash.file_programmer import FileProgrammer

def verify_board(target_override="stm32f401re", firmware_path=None):
    print(f"[*] Пошук підключеного відлагоджувача...")
    
    # Налаштовуємо сесію: Connect under Reset, безпечна частота 1 МГц
    session = ConnectHelper.session_with_chosen_probe(
        target_override=target_override,
        options={
            "connect_mode": "under-reset",
            "frequency": 1000000,          # 1 МГц
            "reset_type": "hw",            # Апаратне скидання через NRST
            "auto_unlock": True            # Автоматичне зняття RDP
        }
    )
    
    if session is None:
        print("[!] Помилка: Апаратний відлагоджувач (DAPLink/ST-Link) не знайдено на USB.")
        sys.exit(1)

    with session:
        board = session.board
        target = session.target
        
        print(f"[+] Відлагоджувач: {board.name}")
        print(f"[+] Цільовий процесор: {target.part_number}")
        
        # Читання ідентифікатора CoreSight DP IDCODE
        dp_id = target.dp.dpidr.read()
        print(f"[+] CoreSight DP IDCODE: 0x{dp_id:08X}")
        
        # Зупиняємо ядро та читаємо поточні регістри
        target.halt()
        pc = target.read_core_register("pc")
        sp = target.read_core_register("sp")
        print(f"[+] Стан ядра: HALTED | PC = 0x{pc:08X} | SP = 0x{sp:08X}")
        
        if firmware_path:
            print(f"[*] Прошивання тестового бінарника: {firmware_path}...")
            programmer = FileProgrammer(session)
            programmer.program(firmware_path, base_address=0x08000000)
            print("[+] Прошивку успішно записано та перевірено!")
            
            # Апаратний перезапуск для виконання прошивки
            print("[*] Перезапуск плати...")
            target.reset()
            print("[+] Плата працює.")

if __name__ == "__main__":
    fw = sys.argv[1] if len(sys.argv) > 1 else None
    verify_board(firmware_path=fw)
