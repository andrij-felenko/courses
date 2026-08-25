import sys
import os

# Додаємо шлях до scripts/ у корені репо (4 рівні вгору)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))

from svgkit import render, fitbox, textbox, line, arrow, text, rect, POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG

def make_arch_fig(img_dir):
    w, h = 840, 420
    frags = []

    # Title / Headers
    frags.append(text(w / 2, 30, "Розподіл оперативної пам'яті (RAM) та потік kexec/kdump", size=18, bold=True, color=INK))

    # Main Memory Container
    frags.append(rect(40, 60, 760, 210, fill="#f8fafc", stroke=LINE, sw=2, rx=8))
    frags.append(text(450, 85, "Фізична оперативна пам'ять (System RAM)", size=15, bold=True, color=INK))

    # Primary Kernel Memory Block
    frags.append(rect(60, 105, 460, 145, fill="#eef2ff", stroke="#4f46e5", sw=2, rx=6))
    frags.append(text(290, 130, "Основне ядро (Primary Kernel)", size=14, bold=True, color="#3730a3"))
    frags.append(fitbox(80, 145, 200, 40, "Код ядра, SLAB, Page Cache\n(Працююча система)", size=12, fill="#ffffff", stroke="#818cf8"))
    frags.append(fitbox(300, 145, 200, 40, "Пам'ять процесів (Userspace)\nі структури VFS", size=12, fill="#ffffff", stroke="#818cf8"))
    frags.append(fitbox(80, 195, 420, 40, "Дані для аварійного аналізу (PT_LOAD сторінки в /proc/vmcore)", size=12, fill="#e0e7ff", stroke="#6366f1", color="#312e81"))

    # Reserved Crashkernel Block
    frags.append(rect(540, 105, 240, 145, fill="#fef2f2", stroke=POS, sw=2, rx=6))
    frags.append(text(660, 130, "crashkernel=512M", size=14, bold=True, color=POS))
    frags.append(fitbox(555, 145, 210, 40, "Ізольоване аварійне ядро\n(Crash Kernel в RAM)", size=12, fill="#ffffff", stroke="#fca5a5", color="#991b1b"))
    frags.append(fitbox(555, 195, 210, 40, "Спеціальний initramfs\n(kdump-tools / makedumpfile)", size=12, fill="#ffffff", stroke="#fca5a5", color="#991b1b"))

    # Triggers and Flow Arrows
    # 1. Normal kexec flow
    frags.append(arrow(180, 270, 180, 315, color=NEG, sw=2))
    frags.append(textbox(180, 345, "Стандартний kexec:\nsys_kexec_load() → Purgatory\nЗаміна первинного ядра новим", size=12, fill="#eff6ff", stroke=NEG, color="#1e40af")[0])

    # 2. Kernel Panic -> kdump flow
    frags.append(arrow(660, 270, 660, 315, color=POS, sw=2))
    frags.append(textbox(660, 345, "Kernel Panic → crash_kexec():\nСтрибок у зарезервовану RAM\nбез скидання апаратури", size=12, fill="#fff1f2", stroke=POS, color="#991b1b")[0])

    # 3. Read vmcore arrow
    frags.append(line(540, 215, 510, 215, color=FIELD, sw=2, dash="4,4"))
    frags.append(arrow(510, 215, 538, 215, color=FIELD, sw=2))
    frags.append(text(525, 205, "Мапування /proc/vmcore", size=11, bold=True, color=FIELD, anchor="middle"))

    out_path = os.path.join(img_dir, "kexec-kdump-arch.svg")
    render(out_path, w, h, *frags)
    print(f"Generated: {out_path}")

def make_timeline_fig(img_dir):
    w, h = 820, 360
    frags = []

    frags.append(text(w / 2, 28, "Етапи виконання kexec та фази аварійного переходу kdump", size=18, bold=True, color=INK))

    # Steps in horizontal chain
    steps = [
        ("1. Підготовка", "Утиліта kexec готує\nсегменти ядра та initramfs;\nвиклики kexec_file_load()"),
        ("2. Сигнал паніки", "Kernel Panic / SysRq 'c';\nвикликається panic()\nта crash_kexec()"),
        ("3. Зупинка CPU", "NMI-переривання зупиняють\nінші CPU; збереження\nрегістрів у crash_notes"),
        ("4. Purgatory Stub", "Код релокації перевіряє\nSHA256 хеші сегментів;\nвимкнення VMX/IOMMU"),
        ("5. Запуск Crash Kernel", "Стрибок на startup_64;\nboot з elfcorehdr=;\nмонтування /proc/vmcore")
    ]

    box_w = 140
    gap = 20
    start_x = 35

    for i, (title, desc) in enumerate(steps):
        x = start_x + i * (box_w + gap)
        y = 70
        color = NEG if i == 0 else (POS if i in (1, 2) else FIELD)
        bg = "#eff6ff" if i == 0 else ("#fff1f2" if i in (1, 2) else "#f0fdf4")
        stroke = NEG if i == 0 else (POS if i in (1, 2) else FIELD)

        frags.append(rect(x, y, box_w, 220, fill=bg, stroke=stroke, sw=2, rx=6))
        frags.append(text(x + box_w / 2, y + 25, title, size=12, bold=True, color=color))
        frags.append(fitbox(x + 8, y + 45, box_w - 16, 160, desc, size=11, fill="#ffffff", stroke=stroke))

        if i < len(steps) - 1:
            arrow_x1 = x + box_w
            arrow_x2 = arrow_x1 + gap
            frags.append(arrow(arrow_x1, y + 110, arrow_x2, y + 110, color=LINE, sw=2))

    # Bottom summary box
    frags.append(fitbox(start_x, 305, w - 2 * start_x, 35,
                        "Загальний час переходу від фатального збою до збереження дампу в /proc/vmcore становить 1-3 секунди",
                        size=12, fill="#f4f6f8", stroke=MUTED, color=INK, bold=True))

    out_path = os.path.join(img_dir, "kexec-transition-timeline.svg")
    render(out_path, w, h, *frags)
    print(f"Generated: {out_path}")

if __name__ == "__main__":
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    make_arch_fig(img_dir)
    make_timeline_fig(img_dir)
