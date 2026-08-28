# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOLD = "#a9791f"
PURPLE = "#7d3c98"

def poly_lines(pts, color=LINE, sw=1.5):
    res = []
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i+1]
        res.append(line(x1, y1, x2, y2, color=color, sw=sw))
    return "".join(res)

# ── 1. avr-fuse-memory-map: Карта енергонезалежної пам'яті та бітів конфігурації AVR ──
def fig_avr_fuse_memory_map():
    W, H = 840, 520
    p = []

    # Загальний заголовок схеми
    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.5))
    p.append(text(W / 2, 36, "Карта енергонезалежної пам'яті: Flash, EEPROM, Fuses та Lock Bits", size=15, bold=True, color=INK))

    # Секція Flash пам'яті
    fx, fy, fw, fh = 30, 60, 240, 420
    p.append(rect(fx, fy, fw, fh, fill="#ffffff", stroke="#8c959f", sw=1.8))
    p.append(text(fx + fw / 2, fy + 24, "Flash пам'ять програм", size=13, bold=True, color=NEG))
    
    # Application Section
    app_h = 240
    p.append(rect(fx + 10, fy + 38, fw - 20, app_h, fill="#eef3ff", stroke=NEG, sw=1.4))
    p.append(text(fx + fw / 2, fy + 65, "Секція застосунку (Application)", size=11, bold=True, color=NEG))
    p.append(text(fx + fw / 2, fy + 88, "Адреса 0x0000 ... BOOTRST", size=10, color=MUTED))
    p.append(fitbox(fx + 20, fy + 110, fw - 40, 70, "Код користувача\nЗахист від запису через BLB01/02\nДоступ до SPM обмежено", size=10, color=INK, fill="#ffffff", stroke="#c8d6f5", sw=1))
    p.append(text(fx + fw / 2, fy + 230, "Вектори переривань", size=10, bold=True, color=MUTED))

    # Bootloader Section
    boot_y = fy + 38 + app_h + 10
    boot_h = fh - app_h - 60
    p.append(rect(fx + 10, boot_y, fw - 20, boot_h, fill="#fbf3df", stroke=GOLD, sw=1.4))
    p.append(text(fx + fw / 2, boot_y + 25, "Секція завантажувача (Bootloader)", size=11, bold=True, color=GOLD))
    p.append(text(fx + fw / 2, boot_y + 46, "Розмір задається BOOTSZ[1:0]", size=10, color=MUTED))
    p.append(fitbox(fx + 20, boot_y + 60, fw - 40, 56, "Має право виконувати SPM\nЗахист через BLB11/12", size=10, color=INK, fill="#ffffff", stroke="#ebd8a7", sw=1))

    # Секція EEPROM
    ex, ey, ew, eh = 290, 60, 230, 160
    p.append(rect(ex, ey, ew, eh, fill="#ffffff", stroke="#8c959f", sw=1.8))
    p.append(text(ex + ew / 2, ey + 24, "EEPROM (Енергонезалежні дані)", size=12, bold=True, color=FIELD))
    p.append(fitbox(ex + 10, ey + 38, ew - 20, 110, "Збереження налаштувань\nі калібрувальних таблиць.\n\nФьюз EESAVE=0 запобігає\nстиранню при Chip Erase!", size=10, color=INK, fill="#eafaf0", stroke=FIELD, sw=1.2))

    # Секція Lock Bits
    lx, ly, lw, lh = 290, 240, 230, 240
    p.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke="#8c959f", sw=1.8))
    p.append(text(lx + lw / 2, ly + 24, "Lock Bits (Байт блокування)", size=12, bold=True, color=POS))
    
    lock_items = [
        ("LB[2:1]", "Режими захисту чіпа 1, 2, 3 (заборона ISP читання/запису)"),
        ("BLB0[2:1]", "Блокування запису/читання Application з Bootloader"),
        ("BLB1[2:1]", "Блокування запису/читання Bootloader з Application"),
    ]
    for i, (tag, desc) in enumerate(lock_items):
        item_y = ly + 40 + i * 62
        p.append(rect(lx + 10, item_y, lw - 20, 54, fill="#fdf0ef", stroke=POS, sw=1.1))
        p.append(text(lx + 20, item_y + 18, tag, size=11, bold=True, color=POS, anchor="start"))
        p.append(text(lx + 20, item_y + 36, desc, size=9, color=INK, anchor="start"))

    # Секція Fuses
    fux, fuy, fuw, fuh = 540, 60, 270, 420
    p.append(rect(fux, fuy, fuw, fuh, fill="#ffffff", stroke="#8c959f", sw=1.8))
    p.append(text(fux + fuw / 2, fuy + 24, "Конфігураційні байти (Fuses)", size=13, bold=True, color=PURPLE))

    # Low Fuse Byte
    p.append(rect(fux + 10, fuy + 38, fuw - 20, 114, fill="#f8f4fb", stroke=PURPLE, sw=1.2))
    p.append(text(fux + 20, fuy + 56, "Low Fuse (lfuse)", size=11, bold=True, color=PURPLE, anchor="start"))
    p.append(text(fux + 20, fuy + 74, "• CKSEL[3:0]: Джерело тактування", size=10, color=INK, anchor="start"))
    p.append(text(fux + 20, fuy + 92, "• SUT[1:0]: Час старту та стабілізації", size=10, color=INK, anchor="start"))
    p.append(text(fux + 20, fuy + 110, "• CKOUT: Вивід тактового сигналу", size=10, color=INK, anchor="start"))
    p.append(text(fux + 20, fuy + 128, "• CKDIV8: Ділення частоти на 8", size=10, color=INK, anchor="start"))

    # High Fuse Byte
    p.append(rect(fux + 10, fuy + 160, fuw - 20, 140, fill="#f8f4fb", stroke=PURPLE, sw=1.2))
    p.append(text(fux + 20, fuy + 178, "High Fuse (hfuse)", size=11, bold=True, color=PURPLE, anchor="start"))
    p.append(text(fux + 20, fuy + 196, "• RSTDISBL: Вимкнення Reset (GPIO)", size=10, color=POS, anchor="start"))
    p.append(text(fux + 20, fuy + 214, "• DWEN: Вмикання debugWIRE", size=10, color=INK, anchor="start"))
    p.append(text(fux + 20, fuy + 232, "• SPIEN: Дозвіл ISP програмування", size=10, color=INK, anchor="start"))
    p.append(text(fux + 20, fuy + 250, "• WDTON: Сторожовий таймер завжди увімкнений", size=10, color=INK, anchor="start"))
    p.append(text(fux + 20, fuy + 268, "• EESAVE: Збереження EEPROM при Chip Erase", size=10, color=INK, anchor="start"))
    p.append(text(fux + 20, fuy + 286, "• BOOTSZ/BOOTRST: Налаштування завантажувача", size=10, color=INK, anchor="start"))

    # Extended Fuse Byte
    p.append(rect(fux + 10, fuy + 308, fuw - 20, 94, fill="#f8f4fb", stroke=PURPLE, sw=1.2))
    p.append(text(fux + 20, fuy + 326, "Extended Fuse (efuse)", size=11, bold=True, color=PURPLE, anchor="start"))
    p.append(text(fux + 20, fuy + 346, "• BODLEVEL[2:0]: Поріг спрацьовування", size=10, color=INK, anchor="start"))
    p.append(text(fux + 32, fuy + 364, "детектора просідання напруги (Brown-out)", size=9, color=MUTED, anchor="start"))
    p.append(text(fux + 32, fuy + 382, "(запобігає пошкодженню пам'яті при спаді VCC)", size=9, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "avr-fuse-memory-map.svg"), W, H, *p,
           title="Карта енергонезалежної пам'яті та бітів конфігурації AVR")


# ── 2. hvpp-recovery-timing: Часова діаграма відновлення чіпа через HVPP (+12V на Reset) ──
def fig_hvpp_recovery_timing():
    W, H = 840, 480
    p = []

    # Фон та заголовок
    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.5))
    p.append(text(W / 2, 34, "Послідовність сигналів високовольтного паралельного програмування (HVPP)", size=14, bold=True, color=INK))

    # Часова шкала та фази
    t_x = 160
    phases = [
        ("T0: Подача VCC", 110),
        ("T1: Подача +12V", 110),
        ("T2: Вхід у режим", 120),
        ("T3: Команда Chip Erase", 140),
        ("T4: Очищення і розблокування", 140),
    ]

    cur_x = t_x
    for name, dur in phases:
        p.append(line(cur_x, 56, cur_x, 420, color="#e1e4e8", sw=1.2, dash="4,4"))
        p.append(text(cur_x + dur / 2, 70, name, size=10, bold=True, color=MUTED))
        cur_x += dur
    p.append(line(cur_x, 56, cur_x, 420, color="#e1e4e8", sw=1.2, dash="4,4"))

    # Лінії сигналів
    signals = [
        ("VCC (5.0V)", 110, "vcc"),
        ("RESET (+12V)", 165, "reset"),
        ("XA1 / XA0", 220, "xa"),
        ("PAGEL / BS1", 275, "bs"),
        ("DATA[7:0]", 330, "data"),
        ("/WR (Запис)", 385, "wr"),
        ("RDY / /BSY", 435, "rdy"),
    ]

    for label, y_pos, stype in signals:
        p.append(text(t_x - 15, y_pos + 5, label, size=11, bold=True, color=INK, anchor="end"))

    # Траса VCC
    p.append(poly_lines([(t_x, 125), (t_x + 30, 125), (t_x + 45, 95), (t_x + 620, 95)], color=FIELD, sw=2.2))
    p.append(text(t_x + 70, 90, "5.0V", size=9, bold=True, color=FIELD))

    # Траса RESET (+12V)
    p.append(poly_lines([(t_x, 180), (t_x + 140, 180), (t_x + 155, 145), (t_x + 620, 145)], color=POS, sw=2.4))
    p.append(text(t_x + 180, 140, "+12.0V (High Voltage Trigger)", size=9, bold=True, color=POS))

    # Траса XA1 / XA0 (Command mode: XA1=1, XA0=0)
    p.append(poly_lines([(t_x, 235), (t_x + 230, 235), (t_x + 240, 205), (t_x + 460, 205), (t_x + 470, 235), (t_x + 620, 235)], color=PURPLE, sw=1.8))
    p.append(text(t_x + 310, 200, "XA1=1, XA0=0 (Command Mode)", size=9, bold=True, color=PURPLE))

    # Траса PAGEL / BS1
    p.append(poly_lines([(t_x, 290), (t_x + 230, 290), (t_x + 240, 265), (t_x + 460, 265), (t_x + 470, 290), (t_x + 620, 290)], color=PURPLE, sw=1.8))
    p.append(text(t_x + 310, 260, "BS1=0, PAGEL=0", size=9, color=MUTED))

    # Траса DATA[7:0]
    p.append(rect(t_x + 250, 315, 180, 26, fill="#eef3ff", stroke=NEG, sw=1.5))
    p.append(text(t_x + 340, 332, "0x80 (Chip Erase Command)", size=10, bold=True, color=NEG))
    p.append(line(t_x, 328, t_x + 250, 328, color="#8c959f", sw=1.5))
    p.append(line(t_x + 430, 328, t_x + 620, 328, color="#8c959f", sw=1.5))

    # Траса /WR (Write Strobe)
    p.append(poly_lines([(t_x, 375), (t_x + 360, 375), (t_x + 365, 395), (t_x + 410, 395), (t_x + 415, 375), (t_x + 620, 375)], color=INK, sw=2))
    p.append(text(t_x + 388, 410, "Строб запису (t_WLRH)", size=9, color=INK))

    # Траса RDY / /BSY
    p.append(poly_lines([(t_x, 425), (t_x + 380, 425), (t_x + 385, 445), (t_x + 540, 445), (t_x + 545, 425), (t_x + 620, 425)], color=GOLD, sw=2))
    p.append(text(t_x + 460, 440, "Зайнято (стирання матриці Flash/Lock)", size=9, bold=True, color=GOLD))
    p.append(text(t_x + 575, 420, "Готово (0xFF)", size=9, bold=True, color=FIELD))

    render(os.path.join(OUT, "hvpp-recovery-timing.svg"), W, H, *p,
           title="Послідовність сигналів високовольтного паралельного програмування (HVPP)")


if __name__ == "__main__":
    fig_avr_fuse_memory_map()
    fig_hvpp_recovery_timing()
    print("Figures generated successfully in img/")
