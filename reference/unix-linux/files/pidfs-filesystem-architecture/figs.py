# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL  = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL   = "#fdecea"
WARM_FILL  = "#fff6e5"
GREY_FILL  = "#eef0f3"
WARM       = "#b8860b"

def box(x, y, w, h, lines, fill=FILL, stroke=LINE, size=14, bold=False, sw=1.6):
    out = [rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=8)]
    if isinstance(lines, str):
        lines = lines.split("\n")
    cy = y + h / 2 - (len(lines) - 1) * size * 1.35 / 2 + size * 0.35
    out.append(mtext(x + w / 2, cy, lines, size=size, bold=bold))
    return out

# ── 1. Порівняння ідентифікації через PID і через pidfs ────────────────────
def fig_pidfs_architecture():
    W, H = 1000, 440
    p = []

    # Заголовки двох частин
    p += box(40, 25, 430, 44, "Небезпека: гонка чисельного PID", size=16, bold=True, fill=RED_FILL, stroke=POS)
    p += box(530, 25, 430, 44, "Безпека: дескриптор процесу у pidfs", size=16, bold=True, fill=GREEN_FILL, stroke=FIELD)

    # Розділювальна лінія
    p.append(line(500, 20, 500, 390, color=MUTED, sw=1.5, dash="6,6"))

    # Ліва колонка — чисельний PID
    p += box(60, 90, 390, 60, ["Процес A відкриває /proc/1234", "або планує kill(1234, SIGTERM)"], size=13, fill=FILL)
    p.append(arrow(255, 150, 255, 185))
    
    p += box(60, 185, 390, 54, ["Гонка TOCTOU: процес 1234 помирає,", "а ядро виділяє PID 1234 процесу B"], size=13, fill=RED_FILL, stroke=POS)
    p.append(arrow(255, 239, 255, 274))

    p += box(60, 274, 390, 64, ["kill(1234) нищить невинний процес B!", "Синхронізація відсутня"], size=14, bold=True, fill=RED_FILL, stroke=POS)

    # Права колонка — pidfs
    p += box(550, 90, 390, 60, ["Процес A отримує pidfd", "(pidfd_open або clone3)"], size=13, fill=FILL)
    p.append(arrow(745, 150, 745, 185))

    p += box(550, 185, 390, 54, ["pidfd вказує на inode у pidfs", "з унікальним 64-бітним stx_ino"], size=13, fill=BLUE_FILL, stroke=NEG)
    p.append(arrow(745, 239, 745, 274))

    p += box(550, 274, 390, 64, ["Смерть процесу не переносить inode:", "ioctl віддає ESRCH, а stx_ino не змінюється"], size=13, bold=True, fill=GREEN_FILL, stroke=FIELD)

    p.append(text(500, 415, "pidfs гарантує незмінність посилання на struct pid на весь час життя inode", size=14, color=MUTED, italic=True))

    render(os.path.join(IMG, 'pidfs-architecture.svg'), W, H, *p)

# ── 2. Топологія зв'язку pidfd -> pidfs inode -> struct pid ────────────────
def fig_pidfs_inode_mapping():
    W, H = 960, 440
    p = []

    p += box(40, 25, 880, 40, "Зв'язок дескрипторів із внутрішньою файловою системою pidfs", size=16, bold=True, fill=GREY_FILL)

    # User space file descriptors
    p += box(50, 100, 260, 70, ["Процес-наглядач №1", "pidfd = 4"], size=14, fill=BLUE_FILL, stroke=NEG)
    p += box(50, 200, 260, 70, ["Процес-наглядач №2", "pidfd = 9 (через SCM_RIGHTS)"], size=13, fill=BLUE_FILL, stroke=NEG)

    # VFS struct file objects
    p += box(370, 100, 220, 70, ["struct file #1", "(f_op = pidfs_file_operations)"], size=12, fill=FILL)
    p += box(370, 200, 220, 70, ["struct file #2", "(f_op = pidfs_file_operations)"], size=12, fill=FILL)

    p.append(arrow(310, 135, 370, 135))
    p.append(arrow(310, 235, 370, 235))

    # Core inode in pidfs
    p += box(660, 130, 250, 110, [
        "Inode у pidfs_mnt",
        "stx_dev: pidfs (pseudo-dev)",
        "stx_ino: 0x8f4a2b01c3... (64-bit)",
        "Прив'язано до struct pid"
    ], size=13, bold=True, fill=GREEN_FILL, stroke=FIELD)

    p.append(arrow(590, 135, 660, 160))
    p.append(arrow(590, 235, 660, 210))

    # Target kernel object struct pid
    p += box(350, 315, 560, 70, [
        "Об'єкт ядра struct pid (процес-ціль)",
        "Порівняння statx(fd1) == statx(fd2) дає ідентичні (stx_dev, stx_ino)",
        "Навіть якщо процес завершено, inode у pidfs зберігає унікальність"
    ], size=13, fill=WARM_FILL, stroke=WARM)

    p.append(arrow(785, 240, 630, 315))

    p.append(text(480, 420, "Окремі файлові дескриптори посилаються на один стійкий inode у псевдо-ФС pidfs", size=14, color=MUTED, italic=True))

    render(os.path.join(IMG, 'pidfs-inode-mapping.svg'), W, H, *p)

if __name__ == '__main__':
    fig_pidfs_architecture()
    fig_pidfs_inode_mapping()
    print("ok")
