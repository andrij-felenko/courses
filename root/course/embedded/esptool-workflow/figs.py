# -*- coding: utf-8 -*-
"""Фігури до теми «esptool: прошивання й читання Flash»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_path():
    """Ланцюг даних: ПК → USB-UART → ROM-завантажувач → SPI-Flash."""
    W, H = 760, 250
    f = []
    boxes = [
        (60,  "Ваш ПК",        "esptool\n(Python)",     FILL),
        (250, "USB↔UART",      "міст\nна платі",        "#eaf0fd"),
        (440, "ROM у чипі",    "вшитий\nзавантажувач",  "#eafaf1"),
        (630, "SPI-Flash",     "сама\nпам'ять",         FILL),
    ]
    bw, bh = 120, 80
    cy = 130
    for x, title, sub, col in boxes:
        f.append(rect(x - bw/2, cy - bh/2, bw, bh, fill=col))
        f.append(text(x, cy - 12, title, size=14, bold=True))
        f.append(mtext(x, cy + 8, sub, size=11, color=MUTED))
    # стрілки між блоками (двобічні — і запис, і читання)
    for i in range(3):
        x1 = boxes[i][0] + bw/2 + 4
        x2 = boxes[i+1][0] - bw/2 - 4
        f.append(arrow(x1, cy - 8, x2, cy - 8))
        f.append(arrow(x2, cy + 12, x1, cy + 12))
    # підписи каналів
    f.append(text(155, cy - 24, "USB-кабель", size=10, color=MUTED))
    f.append(text(345, cy - 24, "UART (TX/RX)", size=10, color=MUTED))
    f.append(text(535, cy - 24, "шина SPI", size=10, color=MUTED))
    f.append(text(W/2, 210, "Униз — запис (write_flash), вгору — читання (read_flash). esptool сам не торкає Flash:",
                  size=11, color=INK))
    f.append(text(W/2, 228, "він лише шле байти завантажувачеві, а той уже пише в пам'ять по шині SPI.",
                  size=11, color=INK))
    render(os.path.join(IMG, 'data-path.svg'), W, H, *f,
           title="Хто з ким говорить, коли ви прошиваєте чип")


def fig_layout():
    """Типова мапа Flash: адреси й що там лежить."""
    W, H = 720, 420
    f = []
    x0, w = 210, 270
    rows = [
        (0x0,     "(порожньо / залежить від чипа)", MUTED, FILL, 28),
        (0x1000,  "Завантажувач (bootloader)",      INK,   "#eafaf1", 46),
        (0x8000,  "Таблиця розділів",               INK,   "#fdf3e7", 30),
        (0x9000,  "NVS / службові дані",             MUTED, FILL, 36),
        (0x10000, "Прошивка (app)",                  INK,   "#eaf0fd", 90),
        (0x310000,"OTA / файлова система",           MUTED, FILL, 44),
    ]
    y = 60
    for off, label, col, fill, h in rows:
        f.append(rect(x0, y, w, h, fill=fill))
        f.append(fitbox(x0, y, w, h, label, size=13, fill=fill, color=col))
        f.append(text(x0 - 14, y + h/2 + 5, "0x%05X" % off, size=12,
                      color=INK, anchor="end", bold=True))
        y += h + 4
    f.append(text(x0 + w/2, y + 18, "вгору — старші адреси", size=10, color=MUTED))
    f.append(text(x0 - 78, 50, "адреса", size=11, color=MUTED, anchor="middle"))
    # пояснення збоку
    note = ("Кожен шматок має\nсвою адресу-зсув.\nwrite_flash 0x10000\napp.bin кладе\nприкладну прошивку\nсаме на її місце —\nне на початок Flash.")
    f.append(fitbox(x0 + w + 24, 95, 196, 170, note, size=11, fill="#ffffff", stroke=MUTED))
    render(os.path.join(IMG, 'flash-map.svg'), W, H, *f,
           title="Типова мапа Flash на ESP32: що де лежить")


def fig_reset():
    """Авто-скидання: DTR/RTS → EN/IO0 через два транзистори."""
    W, H = 720, 320
    f = []
    # USB-UART зліва
    f.append(rect(40, 110, 130, 110, fill="#eaf0fd"))
    f.append(text(105, 150, "USB↔UART", size=13, bold=True))
    f.append(text(105, 172, "DTR", size=12, color=INK, anchor="middle"))
    f.append(text(105, 194, "RTS", size=12, color=INK, anchor="middle"))
    # два транзистори (як рамки-логіка)
    f.append(fitbox(290, 110, 110, 50, "транзистор\n(DTR→IO0)", size=10, fill=FILL))
    f.append(fitbox(290, 180, 110, 50, "транзистор\n(RTS→EN)", size=10, fill=FILL))
    # ESP32 справа
    f.append(rect(540, 110, 140, 110, fill="#eafaf1"))
    f.append(text(610, 150, "ESP32", size=13, bold=True))
    f.append(text(610, 174, "IO0 (boot)", size=12, anchor="middle"))
    f.append(text(610, 196, "EN (reset)", size=12, anchor="middle"))
    # лінії
    f.append(arrow(170, 165, 288, 135))   # DTR -> T1
    f.append(arrow(170, 188, 288, 205))   # RTS -> T2
    f.append(arrow(400, 135, 538, 168))   # T1 -> IO0
    f.append(arrow(400, 205, 538, 192))   # T2 -> EN
    f.append(text(W/2, 255,
                  "Хитрість схеми: транзистори увімкнено так, що коли DTR і RTS смикають разом —",
                  size=11))
    f.append(text(W/2, 273,
                  "чип НЕ скидається. Тому esptool може окремо «притиснути IO0», тоді «смикнути EN» —",
                  size=11))
    f.append(text(W/2, 291,
                  "і чип прокидається вже в режимі завантаження, без жодної кнопки.",
                  size=11))
    render(os.path.join(IMG, 'auto-reset.svg'), W, H, *f,
           title="Як esptool сам уводить чип у режим завантаження")


def fig_roundtrip():
    """Цикл довіри: стерти → записати → перевірити → (за потреби) вичитати назад."""
    W, H = 740, 220
    f = []
    steps = [
        (110, "erase_flash", "очистити", "#fdecea"),
        (300, "write_flash", "залити app", "#eaf0fd"),
        (490, "verify", "звірити хеш", "#eafaf1"),
        (660, "read_flash", "знати, що там", FILL),
    ]
    bw, bh = 130, 70
    cy = 110
    for x, t, sub, col in steps:
        f.append(rect(x - bw/2, cy - bh/2, bw, bh, fill=col))
        f.append(text(x, cy - 8, t, size=13, bold=True))
        f.append(mtext(x, cy + 12, sub, size=11, color=MUTED))
    for i in range(3):
        x1 = steps[i][0] + bw/2 + 4
        x2 = steps[i+1][0] - bw/2 - 4
        f.append(arrow(x1, cy, x2, cy))
    f.append(text(W/2, 185,
                  "Запис не доводить успіху сам собою — доводить його звірка. А read_flash дає бекап і правду про чип.",
                  size=11))
    render(os.path.join(IMG, 'roundtrip.svg'), W, H, *f,
           title="Повний цикл: від чистого чипа до перевіреної прошивки")


def fig_lineage():
    """Історія: дві гілки 2014 → офіційний інструмент Espressif → v5-перейменування."""
    W, H = 760, 360
    f = []
    # вісь часу
    f.append(line(60, 300, 700, 300, color=MUTED, sw=2))
    for x, yr in [(110, "2014"), (300, "2016"), (470, "2018+"), (650, "2025")]:
        f.append(line(x, 295, x, 305, color=MUTED, sw=2))
        f.append(text(x, 322, yr, size=11, color=MUTED))
    # дві гілки 2014
    f.append(fitbox(40, 60, 150, 56, "esptool-ck (C)\nКрістіан Кліппель",
                    size=10, fill=FILL))
    f.append(fitbox(40, 132, 150, 56, "esptool.py (Python)\nФредрік Альберг",
                    size=10, fill="#eaf0fd"))
    # злиття в офіційний
    f.append(fitbox(330, 96, 150, 60, "офіційний\ninструмент\nEspressif", size=11,
                    fill="#eafaf1"))
    # v5
    f.append(fitbox(560, 96, 160, 60, "esptool v5\n(назва без .py,\nClick)", size=10,
                    fill="#fdf3e7"))
    # стрілки
    f.append(arrow(190, 100, 328, 116))   # ck -> official (згасає)
    f.append(arrow(190, 158, 328, 130))   # py -> official (головна)
    f.append(arrow(480, 126, 558, 126))   # official -> v5
    f.append(text(255, 96, "C-гілка згасла", size=9, color=MUTED))
    f.append(text(255, 178, "Python переміг", size=9, color=FIELD))
    f.append(text(W/2, 348,
                  "Дві спільнотні гілки 2014-го; Python-варіант став офіційним, а 2025-го в v5 скоротив назву.",
                  size=11))
    render(os.path.join(IMG, 'lineage.svg'), W, H, *f,
           title="Звідки взявся esptool: від хобі-проєкту до офіційного")


def fig_offsets():
    """Чому 0x1000 на класичному ESP32, а 0x0 на S3/C3: зарезервований сектор."""
    W, H = 760, 380
    f = []
    colW = 280
    # ── класичний ESP32 (ліва колонка) ──
    lx = 70
    f.append(text(lx + colW/2, 56, "Класичний ESP32", size=14, bold=True))
    f.append(rect(lx, 80, colW, 44, fill="#fdecea"))
    f.append(fitbox(lx, 80, colW, 44, "0x0: сектор під Secure Boot v1\n(IV + дайджест) — зарезервовано",
                    size=10, fill="#fdecea", color=POS))
    f.append(rect(lx, 128, colW, 70, fill="#eafaf1"))
    f.append(fitbox(lx, 128, colW, 70, "0x1000:\nзавантажувач", size=13, fill="#eafaf1"))
    f.append(rect(lx, 202, colW, 36, fill="#fdf3e7"))
    f.append(fitbox(lx, 202, colW, 36, "0x8000: таблиця розділів", size=11, fill="#fdf3e7"))
    f.append(rect(lx, 242, colW, 56, fill="#eaf0fd"))
    f.append(fitbox(lx, 242, colW, 56, "0x10000: прошивка", size=12, fill="#eaf0fd"))
    f.append(text(lx + colW/2, 326, "перші 4 КБ зайняті → завантажувач зсунуто на 0x1000",
                  size=10, color=POS))
    # ── ESP32-S3 / C3 (права колонка) ──
    rx = 410
    f.append(text(rx + colW/2, 56, "ESP32-S3 / C3", size=14, bold=True))
    f.append(rect(rx, 80, colW, 70, fill="#eafaf1"))
    f.append(fitbox(rx, 80, colW, 70, "0x0:\nзавантажувач (одразу з початку)", size=12,
                    fill="#eafaf1"))
    f.append(rect(rx, 154, colW, 36, fill="#fdf3e7"))
    f.append(fitbox(rx, 154, colW, 36, "0x8000: таблиця розділів", size=11, fill="#fdf3e7"))
    f.append(rect(rx, 194, colW, 56, fill="#eaf0fd"))
    f.append(fitbox(rx, 194, colW, 56, "0x10000: прошивка", size=12, fill="#eaf0fd"))
    f.append(fitbox(rx, 258, colW, 40, "Secure Boot v2 не тримає окремого\nсектора попереду: підпис ДОПИСАНО",
                    size=9, fill="#ffffff", stroke=FIELD, color=FIELD))
    f.append(text(rx + colW/2, 326, "перед завантажувачем нічого не бронюють → 0x0",
                  size=10, color=FIELD))
    f.append(text(W/2, 360,
                  "Зсув не примха: на класичному ESP32 перший сектор заброньовано під дайджест Secure Boot v1.",
                  size=11))
    render(os.path.join(IMG, 'offsets.svg'), W, H, *f,
           title="Чому завантажувач на 0x1000, а не на 0x0")


if __name__ == '__main__':
    fig_path()
    fig_layout()
    fig_reset()
    fig_roundtrip()
    fig_lineage()
    fig_offsets()
    print("OK: 6 figs ->", IMG)
