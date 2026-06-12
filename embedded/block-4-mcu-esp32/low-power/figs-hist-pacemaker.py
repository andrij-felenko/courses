# -*- coding: utf-8 -*-
"""
Фігури для 📜 r13-history-pacemaker.md
  fig-r13-history-pm-1-two-lines  — Рис. 4.13.0.1 (таймлайн двох ліній)
  fig-r13-history-pm-2-battery    — Рис. 4.13.0.2 (два важелі: ємність × ощадність)

Запуск: python figs-r13-history-pacemaker.py
Вивід → ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 4.13.0.1 — Таймлайн двох незалежних ліній + злиття в батарейній арці
# ─────────────────────────────────────────────────────────────────────────────
def fig1_two_lines():
    W, H = 860, 420
    frags = []

    # ── Кольори доріжок ──
    C_EU   = "#2457d6"   # Європа / Швеція — синя
    C_USA  = "#c0392b"   # США / Буффало — червона
    C_BAT  = "#27ae60"   # злиття → батарея (зелена)
    C_AXIS = "#6b7280"   # лінія часу

    # ── Горизонтальна ось часу ──
    TIMELINE_Y_EU  = 130   # y верхньої (EU) доріжки
    TIMELINE_Y_USA = 280   # y нижньої (USA) доріжки
    MERGE_Y        = 205   # y вузла злиття

    TX_LEFT  = 60    # x початку осі
    TX_RIGHT = 810   # x кінця осі

    # Роки для x-позицій
    T_START = 1930
    T_END   = 1975

    def tx(year):
        return TX_LEFT + (year - T_START) / (T_END - T_START) * (TX_RIGHT - TX_LEFT)

    # Лінії доріжок
    frags.append(line(TX_LEFT, TIMELINE_Y_EU, TX_RIGHT - 30, TIMELINE_Y_EU,
                      color=C_EU, sw=2.5, dash="8,4"))
    frags.append(line(TX_LEFT, TIMELINE_Y_USA, TX_RIGHT - 30, TIMELINE_Y_USA,
                      color=C_USA, sw=2.5, dash="8,4"))

    # Вісь часу (нижня підпис)
    frags.append(arrow(TX_LEFT, H - 38, TX_RIGHT, H - 38, color=C_AXIS, sw=1.5))
    for yr in [1932, 1950, 1956, 1958, 1960, 1968, 1972]:
        x = tx(yr)
        frags.append(line(x, H - 43, x, H - 33, color=C_AXIS, sw=1))
        frags.append(text(x, H - 20, str(yr), size=10, color=C_AXIS))

    # ── Мітки заголовків доріжок ──
    tb, _, _ = textbox(TX_LEFT - 2, TIMELINE_Y_EU, "Європа\n(Швеція)",
                       size=11, fill="#dbeafe", stroke=C_EU, pad=6, color=C_EU, bold=True, min_w=60)
    frags.append(tb)
    tb, _, _ = textbox(TX_LEFT - 2, TIMELINE_Y_USA, "США\n(Буффало)",
                       size=11, fill="#fdecea", stroke=C_USA, pad=6, color=C_USA, bold=True, min_w=60)
    frags.append(tb)

    # ── Вузли EU-доріжки ──
    # 1932: Hyman — термін «pacemaker»
    x32 = tx(1932)
    frags.append(circle(x32, TIMELINE_Y_EU, 5, fill=C_EU, stroke=C_EU))
    tb, _, _ = textbox(x32, TIMELINE_Y_EU - 42, "Hyman 1932\n«pacemaker»\n(термін)",
                       size=9, fill="#dbeafe", stroke=C_EU, pad=5, color=C_EU, min_w=72)
    frags.append(tb)

    # 1957: Bakken носимий транзисторний
    x57 = tx(1957)
    frags.append(circle(x57, TIMELINE_Y_EU, 5, fill=C_EU, stroke=C_EU))
    tb, _, _ = textbox(x57, TIMELINE_Y_EU - 46, "Баккен 1957\nносимий\n(транзистор,\nбатарея)",
                       size=9, fill="#dbeafe", stroke=C_EU, pad=5, color=C_EU, min_w=78)
    frags.append(tb)

    # 1958: Elmqvist+Senning — перший імплант
    x58 = tx(1958)
    frags.append(circle(x58, TIMELINE_Y_EU, 8, fill="#fff", stroke=C_EU, sw=2.5))
    # іконка «чашки» (маленький прямокутник із напівколом)
    frags.append(rect(x58 - 7, TIMELINE_Y_EU + 12, 14, 10, fill="#dbeafe", stroke=C_EU, sw=1.5, rx=3))
    tb, _, _ = textbox(x58 + 2, TIMELINE_Y_EU + 52, "Елмквіст+Сеннінг\n8.10.1958\nперший ІМПЛАНТ\n(~3 год → заміни)",
                       size=9, fill="#dbeafe", stroke=C_EU, pad=5, color=C_EU, min_w=100)
    frags.append(tb)

    # ── Вузли USA-доріжки ──
    # 1956: «не той резистор»
    x56 = tx(1956)
    frags.append(circle(x56, TIMELINE_Y_USA, 5, fill=C_USA, stroke=C_USA))
    # іконка резистора (маленький прямокутник із зиґзаґом)
    frags.append(rect(x56 - 8, TIMELINE_Y_USA + 12, 16, 8, fill="#fdecea", stroke=C_USA, sw=1.5, rx=2))
    frags.append(text(x56, TIMELINE_Y_USA + 17, "⚡", size=8, color=C_USA))
    tb, _, _ = textbox(x56, TIMELINE_Y_USA + 52, "Ґрейтбатч 1956\n«не той резистор»\nгенератор\nімпульсів",
                       size=9, fill="#fdecea", stroke=C_USA, pad=5, color=C_USA, min_w=88)
    frags.append(tb)

    # 1958: собака (перший дослід)
    x58b = tx(1958) - 8
    frags.append(circle(x58b, TIMELINE_Y_USA, 4, fill=C_USA, stroke=C_USA))
    tb, _, _ = textbox(x58b - 28, TIMELINE_Y_USA - 38, "1958\nсобака",
                       size=9, fill="#fdecea", stroke=C_USA, pad=4, color=C_USA, min_w=52)
    frags.append(tb)

    # 1960: Chardack+Gage — перший довготривалий
    x60 = tx(1960)
    frags.append(circle(x60, TIMELINE_Y_USA, 8, fill="#fff", stroke=C_USA, sw=2.5))
    tb, _, _ = textbox(x60 + 4, TIMELINE_Y_USA - 52, "Чардак+Ґейдж 1960\nперший\nдовготривалий\n(Medtronic)",
                       size=9, fill="#fdecea", stroke=C_USA, pad=5, color=C_USA, min_w=96)
    frags.append(tb)

    # ── Вузол злиття (1968–1972): літій-йодна комірка ──
    X_MERGE = tx(1970)
    # Лінії-злиття від обох доріжок
    frags.append(line(tx(1958.5), TIMELINE_Y_EU, X_MERGE, MERGE_Y, color=C_BAT, sw=2))
    frags.append(line(tx(1961), TIMELINE_Y_USA, X_MERGE, MERGE_Y, color=C_BAT, sw=2))

    # Іконка батареї (два прямокутники)
    frags.append(rect(X_MERGE - 14, MERGE_Y - 20, 28, 40, fill="#d1fae5", stroke=C_BAT, sw=2.5, rx=4))
    frags.append(rect(X_MERGE - 6, MERGE_Y - 25, 12, 7, fill="#d1fae5", stroke=C_BAT, sw=1.5, rx=2))

    # Підпис вузла
    tb, _, _ = textbox(X_MERGE + 2, MERGE_Y + 62,
                       "1968–1972\nлітій-йодна комірка\nртуть ~2 роки → Li ~10 років\n(Catalyst Research Corp)",
                       size=9, fill="#d1fae5", stroke=C_BAT, pad=6, color=C_BAT, bold=True, min_w=130)
    frags.append(tb)

    # ── Заголовок ──
    frags.append(text(W / 2, 26, "Дві незалежні лінії — одна стіна: батарея", size=15, bold=True))

    # Підпис знизу
    note = "Два «перші»: Швеція 1958 — перший імплант; США 1960 — перший довготривалий. Переміг той, хто здолав батарею."
    tb, _, _ = textbox(W / 2, H - 12, note, size=10, fill="#f0fdf4", stroke=C_BAT, pad=7, min_w=500)
    frags.append(tb)

    render(os.path.join(OUT, "fig-r13-history-pm-1-two-lines.svg"), W, H, *frags,
           title=None)  # заголовок уже в frags


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 4.13.0.2 — Два важелі: ємність × ощадність → роки
# ─────────────────────────────────────────────────────────────────────────────
def fig2_battery_lever():
    W, H = 720, 400
    frags = []

    C_NUMER = "#27ae60"   # чисельник (зелений = добрий)
    C_DENOM = "#2457d6"   # знаменник (синій = зменшуємо)
    C_YEARS = "#1a1a1a"

    # ── Центральна формула ──
    CX = W // 2
    # Велика моноширинна формула у рамці
    FORMULA_Y = 165
    formula_box = ('  роки ≈ ємність (мА·год)  \n'
                   '  ───────────────────────  \n'
                   '  середній струм (мкА)     ')
    tb, fw, fh = textbox(CX, FORMULA_Y, formula_box,
                         size=14, fill="#f8f8f8", stroke=C_YEARS, pad=12,
                         color=C_YEARS, bold=True, min_w=280)
    frags.append(tb)

    FORM_TOP    = FORMULA_Y - fh / 2
    FORM_BOTTOM = FORMULA_Y + fh / 2
    FORM_LEFT   = CX - fw / 2
    FORM_RIGHT  = CX + fw / 2

    # ── Стрілка вгору (чисельник — краща хімія) ──
    ARR_TOP = FORM_TOP - 90
    frags.append(arrow(CX, FORM_TOP - 8, CX, ARR_TOP + 12, color=C_NUMER, sw=2.5))
    tb, _, _ = textbox(CX, ARR_TOP - 20,
                       "краща хімія:\nртуть → літій-йод\n(герметичність, малий саморозряд)",
                       size=11, fill="#d1fae5", stroke=C_NUMER, pad=7, color=C_NUMER, min_w=210)
    frags.append(tb)

    # ── Стрілка вниз (знаменник — ощадніша схема) ──
    ARR_BOT = FORM_BOTTOM + 90
    frags.append(arrow(CX, FORM_BOTTOM + 8, CX, ARR_BOT - 12, color=C_DENOM, sw=2.5))
    tb, _, _ = textbox(CX, ARR_BOT + 22,
                       "ощадніша схема:\nКМОН, майже завжди мовчить,\nзрідка б'є — → §4.13.3/§4.13.6",
                       size=11, fill="#dbeafe", stroke=C_DENOM, pad=7, color=C_DENOM, min_w=230)
    frags.append(tb)

    # ── Стовпчики ліворуч: порівняння ртуть vs літій ──
    BAR_CX_HG = 110   # x центру стовпчика ртуті
    BAR_CX_LI = 200   # x центру стовпчика літію
    BAR_W = 52
    BASE_Y = FORM_BOTTOM + 10

    HG_YEARS = 2
    LI_YEARS = 10
    MAX_YEARS = 12
    BAR_MAX_H = 120

    def bar_h(yrs):
        return yrs / MAX_YEARS * BAR_MAX_H

    h_hg = bar_h(HG_YEARS)
    h_li = bar_h(LI_YEARS)

    # Ртуть (темно-сіра)
    frags.append(rect(BAR_CX_HG - BAR_W / 2, BASE_Y - h_hg, BAR_W, h_hg,
                      fill="#e5e7eb", stroke="#6b7280", sw=2, rx=4))
    frags.append(text(BAR_CX_HG, BASE_Y - h_hg - 10, "~2 р.", size=11, bold=True, color="#6b7280"))
    frags.append(text(BAR_CX_HG, BASE_Y + 16, "ртуть", size=10, color="#6b7280"))

    # Літій (зелений)
    frags.append(rect(BAR_CX_LI - BAR_W / 2, BASE_Y - h_li, BAR_W, h_li,
                      fill="#d1fae5", stroke=C_NUMER, sw=2, rx=4))
    frags.append(text(BAR_CX_LI, BASE_Y - h_li - 10, "~10 р.", size=11, bold=True, color=C_NUMER))
    frags.append(text(BAR_CX_LI, BASE_Y + 16, "літій-йод", size=10, color=C_NUMER))

    # Підпис блоку стовпчиків
    frags.append(text((BAR_CX_HG + BAR_CX_LI) / 2, BASE_Y + 32,
                      "ресурс батареї", size=10, color=MUTED))

    # ── Висновок внизу ──
    note = "Перемогу 1970-х дала ПАРА: більший чисельник × менший знаменник"
    tb, _, _ = textbox(W / 2, H - 18, note, size=11, fill="#f0fdf4", stroke=C_NUMER, pad=8, min_w=440)
    frags.append(tb)

    # ── Заголовок ──
    frags.append(text(W / 2, 26, "Роки життя = ємність ÷ струм: два важелі кардіостимулятора 1970-х",
                      size=13, bold=True))

    render(os.path.join(OUT, "fig-r13-history-pm-2-battery.svg"), W, H, *frags, title=None)


if __name__ == "__main__":
    fig1_two_lines()
    fig2_battery_lever()
    print("OK: fig-r13-history-pm-1 і fig-r13-history-pm-2 записано в", OUT)
