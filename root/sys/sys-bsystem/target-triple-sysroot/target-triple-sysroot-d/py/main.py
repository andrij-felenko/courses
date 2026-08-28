#!/usr/bin/env python3
import os, sys

def sanitize_sysroot_links(sysroot_dir):
    sysroot_dir = os.path.abspath(sysroot_dir)
    fixed_count = 0
    
    for root, dirs, files in os.walk(sysroot_dir):
        for name in files + dirs:
            full_path = os.path.join(root, name)
            if os.path.islink(full_path):
                target = os.readlink(full_path)
                # Якщо посилання починається з '/', воно абсолютне
                if target.startswith('/'):
                    # Обчислюємо новий абсолютний шлях усередині sysroot
                    new_target_abs = os.path.join(sysroot_dir, target.lstrip('/'))
                    # Обчислюємо відносний шлях від поточного каталогу
                    rel_target = os.path.relpath(new_target_abs, start=root)
                    os.unlink(full_path)
                    os.symlink(rel_target, full_path)
                    fixed_count += 1
                    
    print(f"Санація завершена: виправлено {fixed_count} абсолютних symlink.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Використання: python3 sanitize_sysroot.py <каталог_sysroot>")
        sys.exit(1)
    sanitize_sysroot_links(sys.argv[1])
