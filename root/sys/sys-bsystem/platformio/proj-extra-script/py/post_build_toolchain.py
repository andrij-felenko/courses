# scripts/post_build_toolchain.py
import struct
import zlib
import subprocess
import os

Import("env")

def compute_checksum_crc32(file_path):
    """Розрахунок стандартного 32-бітного полінома CRC32."""
    crc = 0
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            crc = zlib.crc32(chunk, crc)
    return crc & 0xFFFFFFFF

def analyze_memory_footprint(elf_path):
    """Запуск size для зчитування секцій .text, .data та .bss."""
    try:
        # Витягуємо точний шлях до утиліти size із середовища SCons
        size_tool = env.subst("$SIZE")
        if not size_tool:
            size_tool = "arm-none-eabi-size"
            
        output = subprocess.check_output([size_tool, elf_path]).decode("utf-8")
        lines = output.strip().split("\n")
        if len(lines) >= 2:
            print("[POST-BUILD] Карта пам'яті ELF:")
            print(f"  {lines[0]}")
            print(f"  {lines[1]}")
    except Exception as err:
        print(f"[POST-BUILD WARNING] Не вдалося викликати size: {err}")

def process_firmware_binary(source, target, env):
    """Пост-процесинг: ін'єкція CRC32 у кінець образу та вивід параметрів."""
    # target[0] є SCons Node об'єктом цільового бінарного файлу
    bin_path = str(target[0])
    elf_path = bin_path.replace(".bin", ".elf")
    
    if not os.path.exists(bin_path):
        print(f"[POST-BUILD ERROR] Бінарний файл не знайдено: {bin_path}")
        return

    if os.path.exists(elf_path):
        analyze_memory_footprint(elf_path)

    original_size = os.path.getsize(bin_path)
    crc_value = compute_checksum_crc32(bin_path)
    
    # Дописуємо 4 байти контрольної суми у форматі Little-Endian
    with open(bin_path, "ab") as f:
        f.write(struct.pack("<I", crc_value))
        
    final_size = os.path.getsize(bin_path)
    
    print("\n" + "=" * 64)
    print(f"[POST-BUILD] Успішна обробка образу: {os.path.basename(bin_path)}")
    print(f"  Початковий розмір Flash: {original_size} байтів")
    print(f"  Розрахована CRC32:       0x{crc_value:08X}")
    print(f"  Фінальний розмір (+4B):  {final_size} байтів")
    print("=" * 64 + "\n")

# Реєстрація пост-хука над генерацією фінального двійкового образу
env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", process_firmware_binary)
