# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для вставки 4.12.2c — «USB-C: CC-резистори і кабель лише для заряджання».
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Фігури:
  fig-r12-s2c-1-pins.svg       — функціональна карта 24-контактного гнізда Type-C
  fig-r12-s2c-2-chargeonly.svg — порівняння повноцінного та charge-only кабелю
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: функціональна карта 24 контактів Type-C ───────────────────────

def fig1_pins():
    W, H = 920, 520
    frags = []

    # Заголовок
    tb, _, _ = textbox(W // 2, 28,
                       "Type-C очима прошивача: де тут дані, де виявлення, де живлення",
                       size=14, bold=True, fill=FILL, stroke=MUTED, pad=8)
    frags.append(tb)

    # Чотири групи контактів: колонки зліва (номінал/група) та права (роль)
    groups = [
        # (label, members, fill, stroke, role_text, role_fill, role_stroke)
        (
            "VBUS / GND",
            "×4 кожен\n(обидва боки)",
            "#fdecea", POS,
            "ЖИВЛЕННЯ\nсиметричне — поворот\nне має значення",
            "#fdecea", POS,
        ),
        (
            "CC1 / CC2",
            "по 1",
            "#edf7ed", FIELD,
            "ВИЯВЛЕННЯ + ОРІЄНТАЦІЯ\nRd 5.1 кОм → хост бачить\nпристрій і вмикає VBUS",
            "#edf7ed", FIELD,
        ),
        (
            "D+ / D−",
            "×2 (дубльовані\nобома боками!)",
            "#eaf0fd", NEG,
            "ДАНІ USB 2.0\nнаші дані і прошивка;\nдубльовані → FS не\nзалежить від повороту",
            "#eaf0fd", NEG,
        ),
        (
            "TX1/RX1\nTX2/RX2",
            "4 пари (USB 3.x)",
            "#f4f6f8", MUTED,
            "ШВИДКІ ПАРИ\nUSB 3.x / alt-mode;\nNOT our lane (ESP32\nне використовує)",
            "#f4f6f8", MUTED,
        ),
    ]

    col_label_x = 170
    col_cnt_x   = 310
    col_role_x  = 660
    row_y_start = 95
    row_h       = 105

    # Заголовки стовпців
    frags.append(text(col_label_x, 72, "Група контактів", size=12, color=MUTED, bold=True))
    frags.append(text(col_cnt_x,   72, "Кількість", size=12, color=MUTED, bold=True))
    frags.append(text(col_role_x,  72, "Роль у пристрої-приймачу (sink)", size=12, color=MUTED, bold=True))

    # Роздільна лінія
    frags.append(line(30, 80, W - 30, 80, color=MUTED, sw=0.8))

    for i, (label, members, lfill, lstroke, role, rfill, rstroke) in enumerate(groups):
        cy = row_y_start + i * row_h + row_h // 2

        # рамка «група»
        tb_l, _, _ = textbox(col_label_x, cy, label,
                             size=13, bold=True, fill=lfill, stroke=lstroke, pad=8, min_w=110)
        frags.append(tb_l)

        # рамка «кількість»
        tb_c, _, _ = textbox(col_cnt_x, cy, members,
                             size=12, fill=lfill, stroke=lstroke, pad=8, min_w=110)
        frags.append(tb_c)

        # стрілка → роль
        frags.append(arrow(col_cnt_x + 70, cy, col_role_x - 145, cy,
                           color=lstroke, sw=1.5))

        # рамка «роль»
        tb_r, _, _ = textbox(col_role_x, cy, role,
                             size=12, fill=rfill, stroke=rstroke, pad=10, min_w=260)
        frags.append(tb_r)

        # горизонтальний роздільник
        if i < len(groups) - 1:
            div_y = row_y_start + (i + 1) * row_h
            frags.append(line(30, div_y, W - 30, div_y, color=MUTED, sw=0.5, dash="4,4"))

    # Висновок-рамка внизу
    summary = ("Для USB-device на ESP32 реально потрібні:  "
               "VBUS · GND · D+ · D−  плюс Rd 5.1 кОм на CC1 і CC2")
    tb_sum, _, _ = textbox(W // 2, H - 28, summary,
                           size=12, bold=True, fill="#fffbe6", stroke="#e67e22", pad=10)
    frags.append(tb_sum)

    render(os.path.join(OUT, "fig-r12-s2c-1-pins.svg"), W, H, *frags,
           title=None)
    return os.path.join(OUT, "fig-r12-s2c-1-pins.svg")


# ── Фігура 2: повноцінний vs charge-only кабель ──────────────────────────────

def fig2_chargeonly():
    W, H = 900, 480
    frags = []

    # Заголовок
    tb, _, _ = textbox(W // 2, 28,
                       "Чому «кабель лише для заряджання» зриває прошивку",
                       size=14, bold=True, fill=FILL, stroke=MUTED, pad=8)
    frags.append(tb)

    # Вертикальна лінія-роздільник
    frags.append(line(W // 2, 50, W // 2, H - 90, color=MUTED, sw=1.2, dash="6,4"))

    # Підзаголовки двох кабелів
    tb_full, _, _ = textbox(220, 72, "Повноцінний кабель\n(data cable)", size=13,
                            bold=True, fill="#eaf0fd", stroke=NEG, pad=8)
    frags.append(tb_full)

    tb_co, _, _ = textbox(680, 72, "Charge-only кабель\n(зарядний)", size=13,
                          bold=True, fill="#fdecea", stroke=POS, pad=8)
    frags.append(tb_co)

    # Жили кабелів (ліворуч — повноцінний; праворуч — charge-only)
    wires_full = [
        ("VBUS", "#fdecea", POS, True),
        ("GND",  "#f4f6f8", MUTED, True),
        ("CC",   "#edf7ed", FIELD, True),
        ("D+",   "#eaf0fd", NEG, True),
        ("D−",   "#eaf0fd", NEG, True),
    ]
    wires_co = [
        ("VBUS", "#fdecea", POS, True),
        ("GND",  "#f4f6f8", MUTED, True),
        ("CC",   "#edf7ed", FIELD, True),
        ("D+",   "#fdecea", POS, False),   # відсутня — позначити червоним
        ("D−",   "#fdecea", POS, False),   # відсутня
    ]

    y_start = 115
    y_step  = 46

    for i, ((wname, wfill, wstroke, present), (_, _, _, _)) in enumerate(
            zip(wires_full, wires_co)):
        cy = y_start + i * y_step

        # Ліва — повноцінний
        tb_w, _, _ = textbox(220, cy, wname, size=13, bold=True,
                             fill=wfill, stroke=wstroke, pad=8, min_w=80)
        frags.append(tb_w)
        # Галочка
        frags.append(text(345, cy + 5, "✓", size=18, color=FIELD))

    for i, (wname, wfill, wstroke, present) in enumerate(wires_co):
        cy = y_start + i * y_step

        if present:
            tb_w, _, _ = textbox(680, cy, wname, size=13, bold=True,
                                 fill=wfill, stroke=wstroke, pad=8, min_w=80)
            frags.append(tb_w)
            frags.append(text(805, cy + 5, "✓", size=18, color=FIELD))
        else:
            # Жила ВІДСУТНЯ — перекреслений блок червоним
            tb_w, _, _ = textbox(680, cy, wname + " — ВІДСУТНЯ", size=12, bold=True,
                                 fill="#fdecea", stroke=POS, pad=8, min_w=140, color=POS)
            frags.append(tb_w)
            frags.append(text(805, cy + 5, "✗", size=18, color=POS))

    # Таблиця симптомів внизу обох стовпців
    sym_y = y_start + len(wires_full) * y_step + 20

    headers = ["Живиться / світиться?", "COM-порт видно?", "Прошивається / enum?"]
    full_ans = ["ТАК", "ТАК", "ТАК"]
    co_ans   = ["ТАК", "НІ", "НІ"]
    full_colors = [FIELD, FIELD, FIELD]
    co_colors   = [FIELD, POS, POS]

    row_h_sym = 36
    for j, (hdr, fa, ca, fcolor, ccolor) in enumerate(
            zip(headers, full_ans, co_ans, full_colors, co_colors)):
        ry = sym_y + j * row_h_sym

        # Рядок заголовка (по центру)
        tb_h, _, _ = textbox(W // 2, ry + row_h_sym // 2, hdr,
                             size=11, fill="#f8f8f8", stroke=MUTED, pad=6, min_w=260)
        frags.append(tb_h)

        # Відповідь для повноцінного
        tb_fa, _, _ = textbox(220, ry + row_h_sym // 2, fa,
                              size=12, bold=True, fill="#edf7ed", stroke=fcolor, pad=6, min_w=70,
                              color=fcolor)
        frags.append(tb_fa)

        # Відповідь для charge-only
        co_fill = "#fdecea" if ccolor == POS else "#edf7ed"
        tb_ca, _, _ = textbox(680, ry + row_h_sym // 2, ca,
                              size=12, bold=True, fill=co_fill, stroke=ccolor, pad=6, min_w=70,
                              color=ccolor)
        frags.append(tb_ca)

    # Правило-підказка
    rule = "Плата живиться, але не видно по USB → СПЕРШУ зміни кабель, потім чіпай плату"
    tb_rule, _, _ = textbox(W // 2, H - 28, rule,
                            size=12, bold=True, fill="#fffbe6", stroke="#e67e22", pad=10)
    frags.append(tb_rule)

    render(os.path.join(OUT, "fig-r12-s2c-2-chargeonly.svg"), W, H, *frags,
           title=None)
    return os.path.join(OUT, "fig-r12-s2c-2-chargeonly.svg")


# ── Запуск ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    p1 = fig1_pins()
    p2 = fig2_chargeonly()
    print("Готово:")
    print("  ", p1)
    print("  ", p2)
