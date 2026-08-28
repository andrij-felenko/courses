#!/usr/bin/env python3
"""validate_relink.py — Автоматизована перевірка можливості перелінкування."""
import os
import subprocess
import sys
import tempfile
import shutil

def run_cmd(cmd, cwd):
    res = subprocess.run(cmd, cwd=cwd, shell=True, 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"ПОМИЛКА при виконанні: {cmd}\n{res.stderr}")
        sys.exit(1)
    return res.stdout

def test_relink_kit(bundle_path):
    temp_dir = tempfile.mkdtemp(prefix="relink_test_")
    print(f"[+] Розгортання комплекту перелінкування у: {temp_dir}")
    
    # 1. Розпакування комплекту
    shutil.unpack_archive(bundle_path, temp_dir)
    kit_root = os.path.join(temp_dir, "dist_relink_kit")
    
    # 2. Первинне збирання
    print("[+] Збирання базової прошивки клієнтським Makefile...")
    run_cmd("make firmware.bin", cwd=kit_root)
    
    base_size = os.path.getsize(os.path.join(kit_root, "firmware.bin"))
    print(f"[+] Базовий розмір бінарника: {base_size} байтів")
    
    # 3. Емуляція модифікації LGPL-коду клієнтом
    print("[+] Внесення модифікації у вихідний код LGPL-бібліотеки...")
    codec_c = os.path.join(kit_root, "lgpl_src", "codec.c")
    with open(codec_c, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Додавання клієнтського хука
    modified_content = content.replace(
        "/* COMPRESSION_LOGIC */",
        "/* USER_MODIFIED */ volatile int user_hook = 0xABCD1234;\n/* COMPRESSION_LOGIC */"
    )
    with open(codec_c, "w", encoding="utf-8") as f:
        f.write(modified_content)
        
    # 4. Повторне перелінкування
    print("[+] Повторне збирання модифікованої прошивки...")
    run_cmd("make clean && make firmware.bin", cwd=kit_root)
    
    # 5. Перевірка наявності зміненого маркера у скомпільованому бінарнику
    with open(os.path.join(kit_root, "firmware.bin"), "rb") as f:
        bin_data = f.read()
        
    if b"\x34\x12\xcd\xab" in bin_data:
        print(" УСПІХ: Модифікацію виявлено у прошивці. Комплект ліцензійно валідний.")
    else:
        print("❌ ВАДА: Модифікація не потрапила в образ після перелінкування!")
        sys.exit(1)
        
    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    test_relink_kit("customer_relink_bundle.tar.gz")
