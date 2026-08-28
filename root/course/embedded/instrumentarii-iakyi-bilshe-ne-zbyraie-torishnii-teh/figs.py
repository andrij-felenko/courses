# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_build_drift():
    W, H = 820, 360
    parts = []

    # Title / Header
    parts.append(text(W / 2, 28, "Старіння оточення: чому незмінний тег перестає збиратися", size=16, bold=True))

    # Top flow: Year 2023 (Success)
    y1 = 100
    parts.append(rect(20, y1 - 35, 780, 100, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(40, y1 - 15, "2023: Момент випуску тегу v1.4.2", size=13, bold=True, color="#0f172a", anchor="start"))
    
    b1, w1, h1 = textbox(130, y1 + 25, ["Git Tag v1.4.2", "(Вихідний код C)"], size=12, fill="#eaf0fd", stroke=NEG)
    parts.append(b1)
    
    b2, w2, h2 = textbox(360, y1 + 25, ["Хост: Ubuntu 20.04", "GCC 9.4 · Python 3.8"], size=12, fill="#f0fdf4", stroke=FIELD)
    parts.append(b2)
    
    b3, w3, h3 = textbox(660, y1 + 25, ["firmware-v1.4.2.bin", "504 KB · Реліз успішний"], size=12, fill="#f0fdf4", stroke=FIELD, bold=True)
    parts.append(b3)
    
    parts.append(arrow(130 + w1 / 2 + 5, y1 + 25, 360 - w2 / 2 - 5, y1 + 25, color=FIELD, sw=2))
    parts.append(arrow(360 + w2 / 2 + 5, y1 + 25, 660 - w3 / 2 - 5, y1 + 25, color=FIELD, sw=2))

    # Bottom flow: Year 2026 (Failure)
    y2 = 250
    parts.append(rect(20, y2 - 35, 780, 120, fill="#fef2f2", stroke="#fecaca", sw=1.5, rx=8))
    parts.append(text(40, y2 - 15, "2026: Спроба зібрати той самий тег для термінового виправлення", size=13, bold=True, color=POS, anchor="start"))
    
    b4, w4, h4 = textbox(130, y2 + 28, ["Git Tag v1.4.2", "(Незмінний код)"], size=12, fill="#eaf0fd", stroke=NEG)
    parts.append(b4)
    
    b5, w5, h5 = textbox(360, y2 + 28, ["Хост: Ubuntu 24.04", "GCC 13.2 · Python 3.12", "glibc 2.39 (без 32-bit lib)"], size=11, fill="#fff1f2", stroke=POS)
    parts.append(b5)
    
    b6, w6, h6 = textbox(660, y2 + 28, ["Помилка збірки (BUILD FAIL)", "ModuleNotFoundError: imp", "-Werror=implicit-function"], size=11, fill="#fff1f2", stroke=POS, bold=True)
    parts.append(b6)
    
    parts.append(arrow(130 + w4 / 2 + 5, y2 + 28, 360 - w5 / 2 - 5, y2 + 28, color=POS, sw=2))
    parts.append(arrow(360 + w5 / 2 + 5, y2 + 28, 660 - w6 / 2 - 5, y2 + 28, color=POS, sw=2))

    render(os.path.join(OUT, "build-drift.svg"), W, H, *parts)


def fig_toolchain_decay_layers():
    W, H = 800, 370
    parts = []

    parts.append(text(W / 2, 28, "Чотири анатомічні шари руйнування інструментарію", size=16, bold=True))

    layers = [
        ("Шар 4: Зовнішні ресурси та мережа", "CDN вендора, HTTP-посилання на тарболи, сторонні репозиторії", "HTTP 404, протухлі SSL-сертифікати, оновлені гілки submodules", POS),
        ("Шар 3: Крос-компілятор та компонувальник", "arm-none-eabi-gcc, LLVM/Clang, binutils, newlib/libc", "Зміна оптимізацій, переповнення Flash (+4KB), нові діалекти C/C++", "#d97706"),
        ("Шар 2: Інтерпретатор та скрипти збірки", "Python 2/3, CMake, Meson, Kconfiglib, генератори коду", "Видалення distutils/imp, синтаксичні розриви, зміна поведінки CMake", "#2563eb"),
        ("Шар 1: Хостова операційна система", "Системний glibc, libncurses5, динамічний лінкер, архітектура 64-bit", "Несумісність версій символів libc, відсутність 32-bit рантайму", "#7c3aed")
    ]

    box_w = 740
    box_h = 62
    start_x = 30
    start_y = 55
    spacing = 74

    for i, (title, desc, symptom, col) in enumerate(layers):
        cur_y = start_y + i * spacing
        parts.append(rect(start_x, cur_y, box_w, box_h, fill="#ffffff", stroke=col, sw=1.8, rx=6))
        
        # Left color bar
        parts.append(rect(start_x, cur_y, 8, box_h, fill=col, stroke=col, rx=2))
        
        # Text details
        parts.append(text(start_x + 22, cur_y + 20, title, size=13, bold=True, color=col, anchor="start"))
        parts.append(text(start_x + 22, cur_y + 40, desc, size=11, color=INK, anchor="start"))
        parts.append(text(start_x + 22, cur_y + 54, "→ Наслідок: " + symptom, size=10, italic=True, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "toolchain-decay-layers.svg"), W, H, *parts)


def fig_hermetic_pipeline():
    W, H = 820, 340
    parts = []

    parts.append(text(W / 2, 28, "Архітектура герметичного конвеєра збірки (Hermetic Build)", size=16, bold=True))

    # Left input boxes
    y_mid = 175
    b_src, w_src, h_src = textbox(130, 100, ["Фіксований вихідний код", "(Git commit hash SHA-1)"], size=12, fill="#eaf0fd", stroke=NEG)
    parts.append(b_src)

    b_img, w_img, h_img = textbox(130, 180, ["Герметичний OCI-образ", "image@sha256:7f9a..."], size=12, fill="#f0fdf4", stroke=FIELD, bold=True)
    parts.append(b_img)

    b_dep, w_dep, h_dep = textbox(130, 260, ["Кеш залежностей (Vendor)", "(sha256 lockfile, offline)"], size=12, fill="#fff7ed", stroke="#ea580c")
    parts.append(b_dep)

    # Center Container execution box
    cx, cy, cw, ch = 430, 180, 250, 190
    parts.append(rect(cx - cw / 2, cy - ch / 2, cw, ch, fill="#f8fafc", stroke=LINE, sw=2, rx=8))
    parts.append(text(cx, cy - 65, "Ізольоване середовище збірки", size=13, bold=True, color="#0f172a"))
    parts.append(text(cx, cy - 45, "(Docker / Podman / Nix)", size=11, color=MUTED))
    
    parts.append(rect(cx - 105, cy - 25, 210, 30, fill="#ffffff", stroke="#cbd5e1", rx=4))
    parts.append(text(cx, cy - 6, "Фіксований GCC + Libc + Python", size=11, bold=True, color=INK))
    
    parts.append(rect(cx - 105, cy + 15, 210, 30, fill="#ffffff", stroke="#cbd5e1", rx=4))
    parts.append(text(cx, cy + 34, "SOURCE_DATE_EPOCH + Flags", size=11, bold=True, color=INK))
    
    parts.append(rect(cx - 105, cy + 55, 210, 25, fill="#fee2e2", stroke=POS, rx=4))
    parts.append(text(cx, cy + 71, "Мережа ВИМКНЕНА (--net=none)", size=10, bold=True, color=POS))

    # Right output box
    b_out, w_out, h_out = textbox(720, y_mid, ["Бінарно ідентична", "прошивка (Deterministic)", "firmware.bin", "ELF + DWARF + Map"], size=12, fill="#f0fdf4", stroke=FIELD, bold=True)
    parts.append(b_out)

    # Arrows
    parts.append(arrow(130 + w_src / 2 + 5, 100, cx - cw / 2 - 5, cy - 40, color=NEG, sw=1.8))
    parts.append(arrow(130 + w_img / 2 + 5, 180, cx - cw / 2 - 5, cy, color=FIELD, sw=2))
    parts.append(arrow(130 + w_dep / 2 + 5, 260, cx - cw / 2 - 5, cy + 40, color="#ea580c", sw=1.8))
    
    parts.append(arrow(cx + cw / 2 + 5, cy, 720 - w_out / 2 - 5, cy, color=FIELD, sw=2.5))

    render(os.path.join(OUT, "hermetic-pipeline.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_build_drift()
    fig_toolchain_decay_layers()
    fig_hermetic_pipeline()
    print("Figures generated successfully.")
