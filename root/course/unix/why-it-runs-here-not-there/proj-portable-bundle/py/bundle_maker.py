#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bundle_maker.py: Автоматизований збирач герметичних переносних бандлів для Linux."""

import os
import sys
import shutil
import subprocess
import re

# Бібліотеки, які не слід бандлити (мають надаватися хостом/драйверами)
SYSTEM_EXCLUDE = {
    "linux-vdso.so.1",
    "libGL.so.1",
    "libEGL.so.1",
    "libcuda.so.1",
    "libnvidia-ml.so.1",
    "libvulkan.so.1",
    "libX11.so.6",
    "libasound.so.2",
    "libdrm.so.2",
    "libwayland-client.so.0"
}

def resolve_dependencies(binary_path):
    """Рекурсивно збирає всі залежності .so за допомогою ldd."""
    deps = {}
    ldd_output = subprocess.check_output(["ldd", binary_path], universal_newlines=True)
    
    for line in ldd_output.splitlines():
        line = line.strip()
        if not line:
            continue
        
        # Формат: libname.so => /path/to/libname.so (0x...)
        match = re.match(r"^(.*?)\s*=>\s*(.*?)\s*\(0x[0-9a-fA-F]+\)$", line)
        if match:
            soname, target_path = match.group(1).strip(), match.group(2).strip()
            if target_path and target_path != "not found" and soname not in SYSTEM_EXCLUDE:
                deps[soname] = target_path
        else:
            # Формат: /lib64/ld-linux-x86-64.so.2 (0x...)
            match_interp = re.match(r"^(/.*?)\s*\(0x[0-9a-fA-F]+\)$", line)
            if match_interp:
                interp_path = match_interp.group(1).strip()
                soname = os.path.basename(interp_path)
                if soname not in SYSTEM_EXCLUDE:
                    deps[soname] = interp_path
                    
    return deps

def create_bundle(binary_path, output_dir):
    """Створює структуру бандла, копіює файли та налаштовує DT_RUNPATH."""
    abs_binary = os.path.abspath(binary_path)
    binary_name = os.path.basename(abs_binary)
    
    bin_dir = os.path.join(output_dir, "bin")
    lib_dir = os.path.join(output_dir, "lib")
    
    os.makedirs(bin_dir, exist_ok=True)
    os.makedirs(lib_dir, exist_ok=True)
    
    print(f"[*] Аналіз залежностей для {abs_binary}...")
    deps = resolve_dependencies(abs_binary)
    
    # 1. Копіювання головного бінарника
    dest_binary = os.path.join(bin_dir, binary_name)
    shutil.copy2(abs_binary, dest_binary)
    os.chmod(dest_binary, 0o755)
    print(f"[+] Скопійовано бінарник -> {dest_binary}")
    
    # 2. Копіювання бібліотек
    for soname, src_path in deps.items():
        if os.path.isfile(src_path):
            dest_lib = os.path.join(lib_dir, soname)
            # Якщо це symlink — копіюємо реальний файл та розгортаємо посилання
            real_src = os.path.realpath(src_path)
            shutil.copy2(real_src, dest_lib)
            os.chmod(dest_lib, 0o755)
            print(f"  -> Бібліотека {soname} ({src_path})")
            
    # 3. Модифікація DT_RUNPATH для бінарника та бібліотек
    print("[*] Модифікація заголовків DT_RUNPATH ($ORIGIN/../lib)...")
    subprocess.run(["patchelf", "--set-rpath", "$ORIGIN/../lib:$ORIGIN", dest_binary], check=True)
    
    for lib_file in os.listdir(lib_dir):
        lib_full_path = os.path.join(lib_dir, lib_file)
        if os.path.isfile(lib_full_path):
            try:
                subprocess.run(["patchelf", "--set-rpath", "$ORIGIN", lib_full_path], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                pass
                
    # 4. Генерація стартового скрипта app.sh
    launcher_path = os.path.join(output_dir, "app.sh")
    launcher_content = f"""#!/usr/bin/env sh
# Автогенерований герметичний лаунчер для {binary_name}
set -e

# Визначення абсолютного каталогу бандла
SELF_DIR="\$(cd "\$(dirname "\$0")" && pwd)"

# Санітизація оточення
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# Запуск бінарника з передачею всіх аргументів
exec "\$SELF_DIR/bin/{binary_name}" "\$@"
"""
    with open(launcher_path, "w", encoding="utf-8") as f:
        f.write(launcher_content)
    os.chmod(launcher_path, 0o755)
    print(f"[+] Лаунчер згенеровано -> {launcher_path}")
    print("[✓] Герметичний бандл успішно створено!")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Використання: {sys.argv[0]} <шлях_до_бінарника> <вихідний_каталог>")
        sys.exit(1)
    create_bundle(sys.argv[1], sys.argv[2])
