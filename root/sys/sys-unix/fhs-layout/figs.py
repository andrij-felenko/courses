# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL  = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL   = "#fdecea"
WARM_FILL  = "#fff6e5"
GREY_FILL  = "#f4f6f8"

# ── 1. Ієрархія FHS та Матриця 2x2 ─────────────────────────────────────────
def fig_fhs_layout():
    W, H = 1040, 520
    frags = []

    # Загальна рамка
    frags.append(rect(20, 20, 1000, 480, fill=BG, stroke=LINE, sw=1.5, rx=10))
    frags.append(text(520, 50, "Класифікаційна матриця FHS 3.0 та основні каталоги", size=18, bold=True))

    # Стовпчики матриці (Shareable vs Unshareable)
    frags.append(text(280, 85, "Shareable (Спільні для мережі)", size=15, bold=True, color=NEG))
    frags.append(text(760, 85, "Unshareable (Унікальні для хоста)", size=15, bold=True, color=FIELD))

    # Рядки матриці (Static vs Variable)
    # Квадрант 1: Static + Shareable
    frags.append(rect(40, 110, 470, 180, fill=BLUE_FILL, stroke=NEG, sw=1.5, rx=8))
    frags.append(text(55, 135, "Static + Shareable", size=14, bold=True, color=NEG, anchor="start"))
    frags.append(text(55, 155, "Не змінюються під час роботи; спільні для NFS", size=11, color=MUTED, anchor="start"))
    q1_items = ["/usr/bin — Користувацькі утиліти", "/usr/lib — Бібліотеки програм", "/usr/share — Незалежні від арх. дані (doc, man)"]
    for i, item in enumerate(q1_items):
        frags.append(rect(55, 175 + i * 32, 440, 26, fill=BG, stroke=NEG, sw=1.0, rx=4))
        frags.append(text(65, 192 + i * 32, item, size=12, anchor="start", color=INK))

    # Квадрант 2: Static + Unshareable
    frags.append(rect(530, 110, 470, 180, fill=GREEN_FILL, stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(545, 135, "Static + Unshareable", size=14, bold=True, color=FIELD, anchor="start"))
    frags.append(text(545, 155, "Змінюються лише адміністратором; унікальні для хоста", size=11, color=MUTED, anchor="start"))
    q2_items = ["/etc — Конфігураційні файли системи", "/boot — Ядро vmlinuz, initramfs, GRUB", "/etc/fstab, /etc/hosts — Специфіка хоста"]
    for i, item in enumerate(q2_items):
        frags.append(rect(545, 175 + i * 32, 440, 26, fill=BG, stroke=FIELD, sw=1.0, rx=4))
        frags.append(text(555, 192 + i * 32, item, size=12, anchor="start", color=INK))

    # Квадрант 3: Variable + Shareable
    frags.append(rect(40, 305, 470, 180, fill=WARM_FILL, stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(55, 330, "Variable + Shareable", size=14, bold=True, color="#b45309", anchor="start"))
    frags.append(text(55, 350, "Динамічно змінюються; можуть ділитися у мережі", size=11, color=MUTED, anchor="start"))
    q3_items = ["/var/mail — Поштові скриньки користувачів", "/var/spool/news — Черги новин та друку", "/srv — Дані веб-серверів та FTP (FHS 3.0)"]
    for i, item in enumerate(q3_items):
        frags.append(rect(55, 370 + i * 32, 440, 26, fill=BG, stroke="#d97706", sw=1.0, rx=4))
        frags.append(text(65, 387 + i * 32, item, size=12, anchor="start", color=INK))

    # Квадрант 4: Variable + Unshareable
    frags.append(rect(530, 305, 470, 180, fill=RED_FILL, stroke=POS, sw=1.5, rx=8))
    frags.append(text(545, 330, "Variable + Unshareable", size=14, bold=True, color=POS, anchor="start"))
    frags.append(text(545, 350, "Змінюються під час роботи; строго локальні для хоста", size=11, color=MUTED, anchor="start"))
    q4_items = ["/var/log — Журнали системних подій", "/var/run (/run) — PID-файли та сокети в RAM", "/tmp, /var/tmp — Тимчасові файли"]
    for i, item in enumerate(q4_items):
        frags.append(rect(545, 370 + i * 32, 440, 26, fill=BG, stroke=POS, sw=1.0, rx=4))
        frags.append(text(555, 387 + i * 32, item, size=12, anchor="start", color=INK))

    render(os.path.join(IMG, 'fhs-layout.svg'), W, H, *frags)


# ── 2. Схема об'єднання usrmerge ──────────────────────────────────────────
def fig_fhs_usrmerge():
    W, H = 1000, 440
    frags = []

    frags.append(rect(20, 20, 960, 400, fill=BG, stroke=LINE, sw=1.5, rx=10))
    frags.append(text(500, 50, "Архітектура usrmerge: консолідація бінарників у /usr", size=18, bold=True))

    # Ліва частина: Історичний поділ
    frags.append(rect(40, 80, 420, 320, fill=WARM_FILL, stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(250, 110, "Традиційна схема (до usrmerge)", size=15, color="#b45309", bold=True))
    frags.append(line(55, 125, 445, 125, color="#d97706", sw=1.0))

    trad_boxes = [
        ("/bin & /sbin", "Критичні утиліти завантаження (bash, ip, mount)"),
        ("/lib & /lib64", "Критичні системні бібліотеки (libc.so, ld-linux)"),
        ("/usr/bin & /usr/sbin", "Основний софт користувача (gcc, python, nginx)"),
        ("/usr/lib & /usr/lib64", "Основні бібліотеки додатків"),
    ]
    for i, (path_str, desc_str) in enumerate(trad_boxes):
        y_b = 140 + i * 62
        frags.append(rect(55, y_b, 390, 52, fill=BG, stroke="#d97706", sw=1.0, rx=6))
        frags.append(text(65, y_b + 22, path_str, size=13, anchor="start", bold=True, color="#b45309"))
        frags.append(text(65, y_b + 40, desc_str, size=11, anchor="start", color=MUTED))

    # Стрілка переносу
    frags.append(arrow(470, 240, 530, 240, color=LINE, sw=2.0))
    frags.append(text(500, 225, "usrmerge", size=12, bold=True, color=POS))

    # Права частина: Сучасна схема з usrmerge
    frags.append(rect(540, 80, 420, 320, fill=GREEN_FILL, stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(750, 110, "Сучасна схема usrmerge (/usr-only)", size=15, color=FIELD, bold=True))
    frags.append(line(555, 125, 945, 125, color=FIELD, sw=1.0))

    modern_boxes = [
        ("/bin -> /usr/bin", "Символічне посилання на єдиний каталог утиліт"),
        ("/sbin -> /usr/sbin", "Символічне посилання (або далі на /usr/bin)"),
        ("/lib -> /usr/lib", "Символічне посилання на бібліотеки у /usr"),
        ("/usr (Канонічне сховище)", "Єдиний read-only розділ, атомарне оновлення"),
    ]
    for i, (path_str, desc_str) in enumerate(modern_boxes):
        y_b = 140 + i * 62
        frags.append(rect(555, y_b, 390, 52, fill=BG, stroke=FIELD, sw=1.0, rx=6))
        frags.append(text(565, y_b + 22, path_str, size=13, anchor="start", bold=True, color=FIELD))
        frags.append(text(565, y_b + 40, desc_str, size=11, anchor="start", color=INK))

    render(os.path.join(IMG, 'fhs-usrmerge.svg'), W, H, *frags)


# ── 3. Специфікація XDG Base Directory ────────────────────────────────────
def fig_fhs_xdg_structure():
    W, H = 1000, 420
    frags = []

    frags.append(rect(20, 20, 960, 380, fill=BG, stroke=LINE, sw=1.5, rx=10))
    frags.append(text(500, 50, "Організація користувацького простору XDG Base Directory", size=18, bold=True))

    # Коренева папка користувача
    frags.append(rect(40, 80, 920, 300, fill=BLUE_FILL, stroke=NEG, sw=1.5, rx=8))
    frags.append(text(60, 110, "Домашній каталог користувача (~/ або /home/user)", size=15, color=NEG, bold=True, anchor="start"))
    frags.append(line(55, 125, 945, 125, color=NEG, sw=1.0))

    xdg_items = [
        ("$XDG_CONFIG_HOME", "~/.config", "Конфігурації додатків користувача (ini, json, yaml)"),
        ("$XDG_DATA_HOME", "~/.local/share", "Персональні дані, файли баз даних, ярлики .desktop"),
        ("$XDG_CACHE_HOME", "~/.cache", "Непринципові тимчасові кеші (браузери, мініатюри)"),
        ("$XDG_STATE_HOME", "~/.local/state", "Стан сесій, історія команд, логи додатків"),
        ("$XDG_RUNTIME_DIR", "/run/user/$UID", "Тимчасові сокети Wayland/PipeWire, tmpfs у RAM"),
    ]

    for i, (var_name, path_name, desc_str) in enumerate(xdg_items):
        y_b = 140 + i * 46
        frags.append(rect(55, y_b, 890, 38, fill=BG, stroke=NEG, sw=1.0, rx=6))
        frags.append(text(70, y_b + 24, var_name, size=13, anchor="start", bold=True, color=NEG))
        frags.append(text(260, y_b + 24, path_name, size=13, anchor="start", bold=True, color=FIELD))
        frags.append(text(460, y_b + 24, desc_str, size=12, anchor="start", color=INK))

    render(os.path.join(IMG, 'fhs-xdg-structure.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_fhs_layout()
    fig_fhs_usrmerge()
    fig_fhs_xdg_structure()
