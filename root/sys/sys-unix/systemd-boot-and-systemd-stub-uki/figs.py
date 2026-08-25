# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GREY_FILL = "#f4f6f8"


def tb(cx, cy, lines, **kw):
    frag, w, h = textbox(cx, cy, lines, **kw)
    return frag, cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2


# ── 1. Будова Unified Kernel Image (UKI) ──────────────────────────────────
def fig_uki_structure():
    W, H = 1480, 680
    p = []

    p.append(text(W / 2, 45, "Анатомія Unified Kernel Image (UKI): PE/COFF контейнер", size=18, bold=True))

    # Зовнішній контейнер PE/COFF
    p.append(rect(40, 75, 1400, 565, fill="#f8fafc", stroke=MUTED, sw=2, rx=10))
    p.append(text(75, 105, "Екологія PE/COFF (.efi виконуваний файл підписаний Secure Boot)", size=14, bold=True, color=MUTED, anchor="start"))

    # Заголовок та заглушка
    fr, x0, x1, y0, y1 = tb(240, 160, ["PE/COFF Header & DOS Stub", "Точка входу: systemd-stub"],
                            size=13, fill=WARM_FILL, stroke=LINE, min_w=340)
    p.append(fr)

    # Секції UKI
    sections = [
        (".linux", "Бинарний образ ядра Linux (vmlinuz / zImage)", GREEN_FILL),
        (".initrd", "Об'єднаний архів початкової файлової системи (initramfs)", GREEN_FILL),
        (".cmdline", "Параметри командного рядка ядра (статично зашиті)", GREEN_FILL),
        (".osrel", "Ідентифікатор ОС (/etc/os-release)", BLUE_FILL),
        (".uname", "Версія ядра (значення uname -r)", BLUE_FILL),
        (".pcrpkey", "Публічний ключ виміряного завантаження TPM2", BLUE_FILL),
        (".pcrsig", "Підпис політики TPM2 PCR від Центру довіри", BLUE_FILL),
        (".sbat", "Метадані Secure Boot Advanced Targeting (відкликання)", RED_FILL),
        (".splash", "Графічна заставка ранньої ініціалізації (BMP)", GREY_FILL),
    ]

    y_pos = 225
    for sec_name, desc, fill in sections:
        fr1 = fitbox(60, y_pos, 190, 36, sec_name, size=13, bold=True, fill=fill, stroke=LINE)
        fr2 = fitbox(265, y_pos, 1150, 36, desc, size=13, fill="#ffffff", stroke=MUTED, anchor="start", pad=12)
        p.append(fr1)
        p.append(fr2)
        y_pos += 42

    render(os.path.join(IMG, 'uki-structure.svg'), W, H, *p)


# ── 2. Порівняння завантаження: Класичне vs UKI ────────────────────────────
def fig_boot_sequence():
    W, H = 1480, 680
    p = []

    p.append(text(W / 2, 45, "Межа безпеки: Класичне завантаження проти UKI", size=18, bold=True))

    # Верхній блок: Класична схема
    p.append(rect(40, 75, 1400, 260, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    p.append(text(60, 105, "Класична схема (Роздільні файли на ESP): Вразлива до підміни initramfs та cmdline", size=14, bold=True, color=POS, anchor="start"))

    fr1, _, _, _, _ = tb(180, 180, ["UEFI Firmware", "Secure Boot"], size=13, fill="#ffffff", stroke=LINE, min_w=200)
    fr2, _, _, _, _ = tb(480, 180, ["systemd-boot / GRUB", "Завантажувач"], size=13, fill="#ffffff", stroke=LINE, min_w=220)
    fr3, _, _, _, _ = tb(800, 140, ["vmlinuz", "[Підписано]"], size=13, fill=GREEN_FILL, stroke=FIELD, min_w=200)
    fr4, _, _, _, _ = tb(800, 220, ["initramfs + cmdline", "[БЕЗ підпису!]"], size=13, fill=RED_FILL, stroke=POS, min_w=200)
    fr5, _, _, _, _ = tb(1200, 180, ["Запуск ядра", "Можлива підміна init"], size=13, fill=RED_FILL, stroke=POS, min_w=220)

    p.extend([fr1, fr2, fr3, fr4, fr5])
    p.append(arrow(285, 180, 365, 180))
    p.append(arrow(595, 160, 695, 140))
    p.append(arrow(595, 200, 695, 220))
    p.append(arrow(905, 140, 1085, 160))
    p.append(arrow(905, 220, 1085, 200))

    # Нижній блок: UKI схема
    p.append(rect(40, 365, 1400, 275, fill="#f0fff4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(60, 395, "Схема UKI (Атомарний виконуваний файл): Повний криптографічний контроль", size=14, bold=True, color=FIELD, anchor="start"))

    fr6, _, _, _, _ = tb(180, 485, ["UEFI Firmware", "Secure Boot"], size=13, fill="#ffffff", stroke=LINE, min_w=200)
    fr7, _, _, _, _ = tb(580, 485, ["UKI Executable (.efi)", "systemd-stub + vmlinuz +", "initramfs + cmdline + sbat", "[Єдиний підпис Authenticode]"], size=13, fill=GREEN_FILL, stroke=FIELD, min_w=380)
    fr8, _, _, _, _ = tb(1000, 485, ["TPM2 PCR 11", "Вимірювання секцій"], size=13, fill=BLUE_FILL, stroke=NEG, min_w=220)
    fr9, _, _, _, _ = tb(1300, 485, ["Запуск ядра", "Контроль довіри"], size=13, fill=GREEN_FILL, stroke=FIELD, min_w=180)

    p.extend([fr6, fr7, fr8, fr9])
    p.append(arrow(285, 485, 385, 485))
    p.append(arrow(775, 485, 885, 485))
    p.append(arrow(1115, 485, 1205, 485))

    render(os.path.join(IMG, 'boot-sequence.svg'), W, H, *p)


if __name__ == '__main__':
    fig_uki_structure()
    fig_boot_sequence()
    print("Figures generated successfully.")
