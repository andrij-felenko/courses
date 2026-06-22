# -*- coding: utf-8 -*-
"""Фігури до теми «EEPROM і FRAM».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки понад палітру svgkit
GREEN = FIELD        # EEPROM/FRAM-перевага, «добре»
RED   = POS          # флеш-обмеження, «дорого»
BLUE  = NEG          # колонка EEPROM
AMBER = "#b9770e"    # тепле застереження (зайва робота)


# ── 1. Побайтовий запис: чому для дрібних налаштувань зручніша EEPROM/FRAM ────
def fig_byte_write():
    W, H = 1000, 470
    f = [text(W / 2, 32, "Побайтовий запис: чому дрібне оновлення любить EEPROM і FRAM",
              size=18, bold=True)]
    f.append(text(W / 2, 55, "Flash мусить СПЕРШУ стерти цілий блок, щоб змінити один байт; "
                  "EEPROM і FRAM міняють окремий байт напряму",
                  size=12.5, color=MUTED, italic=True))

    def cells(x0, y, hi, hi_fill, hi_stroke):
        out = []
        for i in range(16):
            cx = x0 + i * 34
            if i == hi:
                out.append(rect(cx, y, 30, 30, fill=hi_fill, stroke=hi_stroke, sw=1.6, rx=3))
            else:
                out.append(rect(cx, y, 30, 30, fill=BG, stroke="#cfcfcf", sw=1.0, rx=3))
        return out

    # --- Flash: рядок + процедура «стерти блок → переписати» ---
    f.append(text(90, 108, "Flash (NOR/NAND): один байт не змінити окремо",
                  size=13.5, color=RED, anchor="start", bold=True))
    f.append(text(295, 124, "хочу змінити цей", size=10, color=RED, bold=True))
    f += cells(110, 132, 5, "#fdecea", RED)

    f.append(text(382, 186, "крок 1: стерти ВЕСЬ блок (усі 16 → 0xFF)",
                  size=11, color=AMBER, bold=True))
    f.append(text(382, 206, "крок 2: записати блок наново", size=11, color=INK))
    f.append(rect(110, 220, 540, 26, fill="#fff7e6", stroke=AMBER, sw=1.4, rx=4))
    f.append(text(382, 237, "багато зайвої роботи заради одного байта",
                  size=10.5, color=AMBER, italic=True))

    # --- EEPROM / FRAM: один байт напряму ---
    f.append(text(90, 306, "EEPROM / FRAM: пишемо РІВНО потрібний байт",
                  size=13.5, color=GREEN, anchor="start", bold=True))
    f += cells(110, 322, 5, "#eaf7ee", GREEN)
    f.append(line(295, 300, 295, 320, color=GREEN, sw=2))   # стрілка вниз на потрібний байт
    f.append(text(295, 296, "записали — і все", size=10, color=GREEN, bold=True))
    f.append(text(484, 372, "решта байтів недоторкані; стирати нічого",
                  size=11, color=GREEN, bold=True))

    f.append(text(W / 2, 446, "Для лічильника напрацювання чи окремої уставки це безцінно: "
                  "оновив одне число — і не переписав увесь блок.", size=12, color=INK))
    render(os.path.join(IMG, "byte-write.svg"), W, H, *f)


# ── 2. EEPROM проти FRAM: ресурс, швидкість, енергія ─────────────────────────
def fig_eeprom_vs_fram():
    W, H = 1000, 470
    f = [text(W / 2, 32, "EEPROM проти FRAM: де межа ресурсу й чому FRAM швидша",
              size=19, bold=True)]
    f.append(text(W / 2, 55, "FRAM витримує практично необмежено перезаписів і пише миттєво; "
                  "EEPROM дешевша, але цикли її зношують",
                  size=12.5, color=MUTED, italic=True))

    # колонки
    cx_axis, cx_ee, cx_fr = 245, 545, 825
    x_axis, w_axis = 80, 330
    x_ee, w_ee = 410, 270
    x_fr, w_fr = 680, 290
    y0 = 92
    rh = 48

    # шапка
    def header(x, w, cx, label, color):
        out = [rect(x, y0, w, rh, fill="#eef0f4", stroke=MUTED, sw=1.6, rx=0)]
        out.append(text(cx, y0 + 30, label, size=14, color=color, bold=True))
        return out
    f += header(x_axis, w_axis, cx_axis, "Вісь порівняння", INK)
    f += header(x_ee, w_ee, cx_ee, "EEPROM", BLUE)
    f += header(x_fr, w_fr, cx_fr, "FRAM", GREEN)

    rows = [
        ("Ресурс перезапису комірки", "~10⁴–10⁶ циклів", "~10¹²–10¹⁴ (≈ безмежно)"),
        ("Час запису байта",          "мілісекунди",     "як читання, наносекунди"),
        ("Енергія на запис",          "помітна",         "дуже мала"),
        ("Нелеткість",                "так",             "так"),
        ("Ціна за біт",               "низька",          "вища"),
        ("Коли брати",                "рідкі уставки, дешево", "часті записи, лог по живленню"),
    ]
    for i, (axis, ee, fr) in enumerate(rows):
        y = y0 + rh * (i + 1)
        band = BG if i % 2 == 0 else "#fafafa"
        f.append(rect(x_axis, y, w_axis, rh, fill=band, stroke="#e4e4e4", sw=1, rx=0))
        f.append(rect(x_ee, y, w_ee, rh, fill=band, stroke="#e4e4e4", sw=1, rx=0))
        f.append(rect(x_fr, y, w_fr, rh, fill=band, stroke="#e4e4e4", sw=1, rx=0))
        f.append(text(x_axis + 16, y + 29, axis, size=12, color=INK, anchor="start"))
        f.append(text(cx_ee, y + 29, ee, size=12, color=BLUE, bold=True))
        f.append(text(cx_fr, y + 29, fr, size=12, color=GREEN, bold=True))

    # рамка довкола таблиці
    f.append(rect(x_axis, y0, (x_fr + w_fr) - x_axis, rh * (len(rows) + 1),
                  fill="none", stroke=MUTED, sw=1.6, rx=0))

    f.append(text(W / 2, 456, "FRAM сяє там, де треба часто й безпечно зберігати стан — "
                  "дописувати лічильник при кожному циклі чи рятувати дані при зникненні живлення.",
                  size=11.5, color=GREEN, bold=True))
    render(os.path.join(IMG, "eeprom-vs-fram.svg"), W, H, *f)


if __name__ == "__main__":
    fig_byte_write()
    fig_eeprom_vs_fram()
    print("OK: figs у", IMG)
