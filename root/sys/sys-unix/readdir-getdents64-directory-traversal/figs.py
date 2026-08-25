# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT  = "#fbfcff"
WARM  = "#fdf3e7"
COOL  = "#eaf0fd"
GREEN = "#eafaf0"
GREY  = "#f1f2f4"
ALERT = "#fdecea"

def fig_traversal_flow():
    W, H = 1140, 640
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill=BG, stroke=LINE, sw=1, rx=8))
    p.append(text(W / 2, 45, "Багатошарова архітектура обходу каталогів у Linux", size=18, bold=True, color=INK))

    # Шар 1: Користувацький простір (Application & libc)
    y1 = 85
    p.append(rect(40, y1, 1060, 130, fill=COOL, stroke=NEG, sw=1.5, rx=8))
    p.append(text(60, y1 + 26, "Простір користувача (User Space)", size=14, bold=True, color=NEG, anchor="start"))
    
    # Блоки всередині шару 1
    p.append(textbox(220, y1 + 75, "Додаток\nreaddir() / opendir()", size=13, pad=12, fill=BG, stroke=NEG, bold=True)[0])
    p.append(arrow(340, y1 + 75, 430, y1 + 75, color=NEG, sw=1.8))
    p.append(textbox(600, y1 + 75, "C-бібліотека (glibc / musl)\nБуфер DIR* (у glibc 32 KB)\nЗсув у буфері ptr", size=13, pad=12, fill=BG, stroke=NEG, bold=True)[0])

    # Перехід до системного виклику
    y_sys = 245
    p.append(rect(40, y_sys, 1060, 50, fill=WARM, stroke=POS, sw=1.5, rx=6))
    p.append(text(W / 2, y_sys + 31, "Системний виклик: sys_getdents64(fd, dirp, count)", size=14, bold=True, color=POS))

    # Стрілка вниз
    p.append(arrow(600, y1 + 130, 600, y_sys, color=NEG, sw=2))
    p.append(arrow(600, y_sys + 50, 600, 325, color=POS, sw=2))

    # Шар 2: Ядро (VFS & FS)
    y2 = 325
    p.append(rect(40, y2, 1060, 175, fill=GREEN, stroke=FIELD, sw=1.5, rx=8))
    p.append(text(60, y2 + 26, "Простір ядра (Kernel VFS & Filesystem)", size=14, bold=True, color=FIELD, anchor="start"))

    p.append(textbox(260, y2 + 100, "VFS: ksys_getdents64()\niterate_shared()\nstruct dir_context", size=13, pad=12, fill=BG, stroke=FIELD, bold=True)[0])
    p.append(arrow(410, y2 + 100, 490, y2 + 100, color=FIELD, sw=1.8))
    p.append(textbox(670, y2 + 100, "Файлова система (ext4 / XFS / btrfs)\nОбхід HTree / B+tree / dentry\nЗаповнення filldir64()", size=13, pad=12, fill=BG, stroke=FIELD, bold=True)[0])

    # Шар 3: Дискова підсистема
    y3 = 530
    p.append(rect(40, y3, 1060, 75, fill=GREY, stroke=LINE, sw=1.5, rx=8))
    p.append(text(60, y3 + 28, "Блочний пристрій / Дисковий накопичувач (NVMe / SSD / HDD)", size=13, bold=True, color=INK, anchor="start"))
    p.append(textbox(720, y3 + 42, "Дискові блоки каталогів / Індекси HTree", size=12, pad=8, fill=BG, stroke=LINE)[0])

    p.append(arrow(670, y2 + 175, 670, y3, color=LINE, sw=1.8))

    render(os.path.join(OUT, "dir-traversal-flow.svg"), W, H, *p,
           title="Багатошарова архітектура обходу каталогів у Linux")


def fig_buffer_layout():
    W, H = 1140, 560
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill=BG, stroke=LINE, sw=1, rx=8))
    p.append(text(W / 2, 42, "Структура пакетованого буфера linux_dirent64 у getdents64()", size=17, bold=True, color=INK))

    y_start = 80
    p.append(text(60, y_start + 15, "Неперервний буфер пам'яті (char buf[32768]), повернутий getdents64()", size=13, color=MUTED, anchor="start"))

    # Запис 1
    y_rec1 = 120
    p.append(rect(50, y_rec1, 980, 110, fill=COOL, stroke=NEG, sw=1.5, rx=6))
    p.append(text(70, y_rec1 + 25, "Запис 1: d_name = \".\" (d_reclen = 24 байти)", size=13, bold=True, color=NEG, anchor="start"))

    # Поля Запису 1
    fields1 = [
        (70, "d_ino (8B)", "inode = 140291", 140),
        (220, "d_off (8B)", "cookie = 104", 140),
        (370, "d_reclen (2B)", "24", 110),
        (490, "d_type (1B)", "DT_DIR (4)", 110),
        (610, "d_name[]", "\".\\0\"", 110),
        (730, "вирівнювання", "3B pad", 120),
    ]
    for fx, ftitle, fval, fw in fields1:
        p.append(rect(fx, y_rec1 + 40, fw, 55, fill=BG, stroke=LINE, sw=1, rx=4))
        p.append(text(fx + fw / 2, y_rec1 + 60, ftitle, size=11, bold=True, color=INK))
        p.append(text(fx + fw / 2, y_rec1 + 80, fval, size=11, color=MUTED))

    # Стрілка покажчика
    p.append(arrow(540, y_rec1 + 110, 540, y_rec1 + 140, color=POS, sw=2))
    p.append(mtext(670, y_rec1 + 128, "ptr = (void*)ptr + d_reclen", size=12, color=POS, bold=True, anchor="start"))

    # Запис 2
    y_rec2 = 270
    p.append(rect(50, y_rec2, 980, 110, fill=WARM, stroke=POS, sw=1.5, rx=6))
    p.append(text(70, y_rec2 + 25, "Запис 2: d_name = \"access.log\" (d_reclen = 32 байти)", size=13, bold=True, color=POS, anchor="start"))

    fields2 = [
        (70, "d_ino (8B)", "inode = 991823", 140),
        (220, "d_off (8B)", "cookie = 320", 140),
        (370, "d_reclen (2B)", "32", 110),
        (490, "d_type (1B)", "DT_REG (8)", 110),
        (610, "d_name[]", "\"access.log\\0\"", 150),
        (770, "вирівнювання", "2B pad", 120),
    ]
    for fx, ftitle, fval, fw in fields2:
        p.append(rect(fx, y_rec2 + 40, fw, 55, fill=BG, stroke=LINE, sw=1, rx=4))
        p.append(text(fx + fw / 2, y_rec2 + 60, ftitle, size=11, bold=True, color=INK))
        p.append(text(fx + fw / 2, y_rec2 + 80, fval, size=11, color=MUTED))

    # Запис 3 (байтовий залишок)
    y_rec3 = 410
    p.append(rect(50, y_rec3, 980, 70, fill=GREY, stroke=LINE, sw=1, rx=6))
    p.append(text(W / 2, y_rec3 + 40, "... наступні записи linux_dirent64 до кінця повернутого блоку (nbytes) ...", size=13, color=MUTED))

    render(os.path.join(OUT, "getdents64-buffer-layout.svg"), W, H, *p,
           title="Структура пакетованого буфера linux_dirent64 у getdents64()")


if __name__ == "__main__":
    fig_traversal_flow()
    fig_buffer_layout()
    print("SVG generation completed.")
