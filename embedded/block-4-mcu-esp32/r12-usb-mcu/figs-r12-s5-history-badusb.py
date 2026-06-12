# -*- coding: utf-8 -*-
"""
figs-r12-s5-history-badusb.py — фігури до історії «BadUSB і Rubber Ducky»
(вставка r12-s5-history-badusb.md, тема §4.12.5 «Класи пристроїв: CDC, HID, MSC»).

Рис. 4.12.5i.1  fig-12-5i-1-ducky-chain.svg
    Горизонтальний ланцюг атаки Rubber Ducky:
    «виглядає як флешка» → HID-енумерація → потік натискань → виконана команда.

Рис. 4.12.5i.2  fig-12-5i-2-badusb-layers.svg
    Двошаровий розріз флешки: видимий MSC-диск (вгорі) vs
    прихований HID-контролер з перепрошитою прошивкою (знизу).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.5i.1 — Ланцюг атаки Rubber Ducky
# ══════════════════════════════════════════════════════════════════════════════
def fig1_ducky_chain():
    W, H = 880, 340
    frags = []

    # ── Заголовок ──
    frags.append(text(W / 2, 28, "Рис. 4.12.5i.1. Анатомія атаки Rubber Ducky",
                      size=15, bold=True, color=INK))

    # ── Чотири блоки ланцюга ──
    boxes = [
        {
            "cx": 100, "cy": 155,
            "label": "Виглядає\nяк флешка",
            "sublabel": "корпус USB,\nніяких підозр",
            "fill": FILL,
            "stroke": INK,
        },
        {
            "cx": 300, "cy": 155,
            "label": "Енумерація\nHID-keyboard",
            "sublabel": "VID/PID + дескриптор;\nОС ставить класовий\nдрайвер без дозволу",
            "fill": "#fdecea",
            "stroke": POS,
        },
        {
            "cx": 530, "cy": 155,
            "label": "Потік HID-звітів",
            "sublabel": "payload/DuckyScript;\n~1000+ символів/с;\nDELAY між кроками",
            "fill": "#fff3e0",
            "stroke": "#c8700a",
        },
        {
            "cx": 760, "cy": 155,
            "label": "Команда\nвиконана",
            "sublabel": "консоль відкрита,\nсторонній код\nзапущено",
            "fill": "#fdecea",
            "stroke": POS,
        },
    ]

    box_w = 155
    for b in boxes:
        tb, bw, bh = textbox(b["cx"], b["cy"] - 12, b["label"],
                             size=13, bold=True, fill=b["fill"],
                             stroke=b["stroke"], sw=2, pad=10, min_w=box_w)
        frags.append(tb)
        frags.append(mtext(b["cx"], b["cy"] + bh / 2 + 10 + 5,
                           b["sublabel"], size=10, color=MUTED))

    # ── Стрілки між блоками ──
    arrow_y = 155 - 12
    gaps = [(183, 218), (387, 440), (622, 680)]
    for x1, x2 in gaps:
        frags.append(arrow(x1, arrow_y, x2, arrow_y, color=POS, sw=2.2))

    # ── Виноска «довіра без питання» над другим блоком ──
    trust_x = 300
    frags.append(line(trust_x, 155 - 12 - 22, trust_x, 68, color=FIELD, sw=1.4, dash="4,3"))
    tb_trust, _, _ = textbox(trust_x, 54,
                             "Довіра без питання:\nдрайвер HID уже є в ОС",
                             size=11, fill="#e8f8ee", stroke=FIELD, sw=1.6, pad=7)
    frags.append(tb_trust)

    # ── Підпис-висновок внизу ──
    frags.append(text(W / 2, H - 22,
                      "Хост не може відрізнити цей потік від живих пальців — уся атака в тому, що клавіатурі довіряють за замовчуванням.",
                      size=10, color=MUTED))

    render(os.path.join(OUT, 'fig-12-5i-1-ducky-chain.svg'), W, H, *frags)
    print("fig-12-5i-1-ducky-chain.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.5i.2 — Двошаровий розріз флешки (BadUSB)
# ══════════════════════════════════════════════════════════════════════════════
def fig2_badusb_layers():
    W, H = 880, 420
    frags = []

    # ── Заголовок ──
    frags.append(text(W / 2, 28, "Рис. 4.12.5i.2. Чому BadUSB страшніший за вірус-файл",
                      size=15, bold=True, color=INK))

    # ── Тіло флешки (обрис) ──
    body_x, body_y = 240, 55
    body_w, body_h = 300, 300
    frags.append(rect(body_x, body_y, body_w, body_h,
                      fill="#f0f0f0", stroke="#888", sw=2, rx=14))

    # ── Верхній шар: MSC-диск ──
    top_x, top_y = body_x + 12, body_y + 12
    top_w, top_h = body_w - 24, 125
    frags.append(rect(top_x, top_y, top_w, top_h,
                      fill="#eaf0fd", stroke=NEG, sw=2.0, rx=8))
    frags.append(text(top_x + top_w / 2, top_y + 22,
                      "MSC-диск (видимий ОС і антивірусу)", size=12, bold=True, color=NEG))
    frags.append(text(top_x + top_w / 2, top_y + 44,
                      "файлова система · дані · програми", size=11, color=MUTED))
    frags.append(mtext(top_x + top_w / 2, top_y + 72,
                       "сканується антивірусом\nформатується — дані зникають",
                       size=10, color=NEG))

    # ── Роздільник між шарами ──
    sep_y = top_y + top_h + 10
    frags.append(line(body_x + 14, sep_y, body_x + body_w - 14, sep_y,
                      color="#888", sw=1.4, dash="6,4"))

    # ── Нижній шар: контролер із прошивкою ──
    bot_x, bot_y = body_x + 12, sep_y + 10
    bot_w, bot_h = body_w - 24, body_y + body_h - sep_y - 22
    frags.append(rect(bot_x, bot_y, bot_w, bot_h,
                      fill="#fdecea", stroke=POS, sw=2.0, rx=8))
    frags.append(text(bot_x + bot_w / 2, bot_y + 20,
                      "Мікроконтролер-контролер", size=12, bold=True, color=POS))

    # Блок «ПРОШИВКА» всередині нижнього шару
    fw_w, fw_h = 130, 44
    fw_x = bot_x + (bot_w - fw_w) / 2
    fw_y = bot_y + 34
    frags.append(rect(fw_x, fw_y, fw_w, fw_h,
                      fill="#c0392b", stroke=POS, sw=1.5, rx=6))
    frags.append(text(fw_x + fw_w / 2, fw_y + 16, "ПРОШИВКА",
                      size=12, bold=True, color="#fff"))
    frags.append(text(fw_x + fw_w / 2, fw_y + 32, "перепрошита",
                      size=10, color="#fdecea"))

    # Підпис під блоком прошивки
    frags.append(mtext(bot_x + bot_w / 2, fw_y + fw_h + 18,
                       "оголошує MSC + HID-keyboard\n(композитний пристрій)",
                       size=10, color=POS))

    # ── Три виноски праворуч ──
    note_x_start = body_x + body_w + 20
    notes = [
        (top_y + top_h / 2,
         "форматування\nстирає диск,\nне прошивку",
         NEG),
        (fw_y + fw_h / 2,
         "антивірус\nбачить файли,\nне контролер",
         POS),
        (fw_y + fw_h + 55,
         "заражений ПК\nперепрошує\nнаступну флешку\n→ поширення",
         POS),
    ]
    for ny, nlabel, nc in notes:
        tb_n, tnw, tnh = textbox(note_x_start + 95, ny, nlabel,
                                 size=10, fill=FILL, stroke=nc, sw=1.4, pad=7)
        frags.append(tb_n)
        frags.append(line(body_x + body_w, ny, note_x_start + 2, ny,
                          color=nc, sw=1.2, dash="4,3"))
        frags.append(arrow(note_x_start + 2, ny, note_x_start + 95 - tnw / 2 - 2, ny,
                           color=nc, sw=1.2))

    # ── Роз'єм USB зліва (символічно) ──
    conn_x, conn_y = body_x - 54, body_y + body_h / 2
    frags.append(rect(conn_x, conn_y - 18, 40, 36,
                      fill="#ddd", stroke="#666", sw=2, rx=4))
    frags.append(text(conn_x + 20, conn_y + 5, "USB", size=10, color=INK))

    # Стрілка від роз'єму до тіла
    frags.append(arrow(conn_x + 42, conn_y, body_x - 2, conn_y, color=INK, sw=1.8))

    # ── Підпис-висновок внизу ──
    frags.append(mtext(W / 2, H - 26,
                       "Вада не у файлі й не в одній фірмі, а в архітектурі USB: пристрій сам каже, хто він, — і це нічим не перевіряється.",
                       size=10, color=MUTED))

    render(os.path.join(OUT, 'fig-12-5i-2-badusb-layers.svg'), W, H, *frags)
    print("fig-12-5i-2-badusb-layers.svg — OK")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    fig1_ducky_chain()
    fig2_badusb_layers()
    print("Усі фігури згенеровано.")
