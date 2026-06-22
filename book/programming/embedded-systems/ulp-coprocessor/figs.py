# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «ULP-співпроцесор».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: ULP як сторож порога ───────────────────────────────────────────
# Ідея: ULP сам крутить цикл «таймер → вимір → поріг?» у RTC-домені; гілка «норма»
# веде назад у сон (велике ядро так і спить), гілка «поріг» будить велике ядро.
# Важко передати словами саме РОЗГАЛУЖЕННЯ: одна подія з тисячі йде праворуч.
def fig_guard():
    W, H = 680, 500
    P = [text(W / 2, 28, "ULP як сторож порога: велике ядро будиться лише на подію",
              size=16, bold=True)]

    cx = W / 2
    # вертикальний стовпчик ULP-циклу
    fr, w, h = textbox(cx, 70, "RTC-таймер будить ULP\n(кожні X мс)", size=13,
                       bold=True, color=FIELD, fill="#e9f7ef", stroke=FIELD, min_w=260)
    P.append(fr)
    P.append(arrow(cx, 70 + h / 2, cx, 120, color=FIELD))

    fr, w, h = textbox(cx, 142, "читає RTC-АЦП / RTC-GPIO\n(вимір — мікросекунди)", size=13,
                       color=INK, fill=FILL, stroke=LINE, min_w=260)
    P.append(fr)
    P.append(arrow(cx, 142 + h / 2, cx, 192, color=INK))

    fr, w, h = textbox(cx, 214, "поза порогом?", size=13, bold=True,
                       color=POS, fill="#fdf3e6", stroke="#b8860b", min_w=190)
    P.append(fr)
    decision_w = w

    # ── гілка «ні, норма» — ліворуч і назад у сон ──
    lx = 120
    P.append(arrow(cx - decision_w / 2, 214, lx + 60, 214, color=FIELD))
    P.append(text((cx - decision_w / 2 + lx + 60) / 2, 205, "ні · норма",
                  size=11, color=FIELD, bold=True))
    fr, w, h = textbox(lx, 270, "записати вимір\nу RTC-пам'ять", size=12,
                       color=FIELD, fill="#e9f7ef", stroke=FIELD, min_w=150)
    P.append(fr)
    P.append(arrow(lx, 270 + h / 2, lx, 322, color=FIELD))
    fr, w, h = textbox(lx, 344, "велике ядро\nСПИТЬ", size=13, bold=True,
                       color=NEG, fill="#eaf0fd", stroke=NEG, min_w=150)
    P.append(fr)
    P.append(text(lx, 390, "I ≈ одиниці мкА", size=11, color=NEG, bold=True))
    # повернення в цикл: від «спить» нагору до таймера
    P.append(line(lx, 344 + h / 2 + 6, lx, 440, color=MUTED, sw=1.5))
    P.append(line(lx, 440, 36, 440, color=MUTED, sw=1.5))
    P.append(line(36, 440, 36, 70, color=MUTED, sw=1.5))
    P.append(arrow(36, 70, cx - 132, 70, color=MUTED, sw=1.5))
    P.append(text(195, 458, "наступний тік — знову вимір", size=10.5, color=MUTED))

    # ── гілка «так, поріг» — праворуч, будимо ядро ──
    rx = W - 110
    P.append(arrow(cx + decision_w / 2, 214, rx - 60, 214, color=POS))
    P.append(text((cx + decision_w / 2 + rx - 60) / 2, 205, "так · поріг!",
                  size=11, color=POS, bold=True))
    fr, w, h = textbox(rx, 270, "ULP будить\nвелике ядро", size=12, bold=True,
                       color=POS, fill="#fdecea", stroke=POS, min_w=150)
    P.append(fr)
    P.append(arrow(rx, 270 + h / 2, rx, 322, color=POS))
    fr, w, h = textbox(rx, 344, "ядро активне:\nпередає тривогу", size=13, bold=True,
                       color=POS, fill="#fdecea", stroke=POS, min_w=150)
    P.append(fr)
    P.append(text(rx, 390, "I ≈ міліампери (коротко)", size=11, color=POS, bold=True))

    # підсумкова смужка
    P.append(fitbox(W / 2 - 235, 470, 470, 24,
                    "майже всі виміри ULP відсіює сам — велике ядро не прокидається",
                    size=11.5, fill="#e9f7ef", stroke=FIELD))

    render("img/ulp-guard.svg", W, H, *P)


# ── Фігура 2: економіка ULP (площа під кривою = заряд) ────────────────────────
# Ідея: однакова частота вимірів, але профіль струму різний. (а) кожен вимір =
# дорогий сплеск ядра; (б) ULP робить виміри за мікроамперним фоном, ядро
# спалахує зрідка. Площі (= заряд) відрізняються на порядки — це і є виграш.
def fig_economics():
    W, H = 740, 400
    P = [text(W / 2, 28, "Та сама частота вимірів — різний заряд (площа під кривою)",
              size=16, bold=True)]

    base = 250          # лінія нуля струму
    top = 70            # стеля сплеску
    spikes = [110, 185, 260, 335, 410]   # моменти вимірів (спільні для обох)

    # ── панель (а): ядро будиться на КОЖЕН вимір ──
    ax0 = 50
    P.append(text(225, 56, "(а) будити ядро на кожен вимір", size=12.5, bold=True))
    P.append(line(ax0, top - 6, ax0, base, color=INK, sw=1.5))      # вісь струму
    P.append(line(ax0, base, 460, base, color=INK, sw=1.5))         # вісь часу
    P.append(text(ax0 - 18, (top + base) / 2, "I", size=12, color=INK, bold=True))
    for sx in spikes:
        # дорогий прямокутний сплеск ядра
        P.append(rect(sx - 7, top, 14, base - top, fill="#fdecea", stroke="none", sw=0))
        P.append(line(sx, base, sx, top, color=POS, sw=2.0))
        P.append(line(sx, top, sx + 14, top, color=POS, sw=2.0))
        P.append(line(sx + 14, top, sx + 14, base, color=POS, sw=2.0))
    P.append(text(225, base + 26, "I_сер ≈ міліампери", size=12, color=POS, bold=True))
    P.append(text(225, base + 44, "← площа велика", size=10.5, color=MUTED))

    # ── панель (б): ULP міряє за мікроамперним фоном, ядро зрідка ──
    bx0 = 500
    floor = base - 6     # тонкий мікроамперний фон
    P.append(text(620, 56, "(б) ULP міряє, ядро спить", size=12.5, bold=True))
    P.append(line(bx0, top - 6, bx0, base, color=INK, sw=1.5))
    P.append(line(bx0, base, 715, base, color=INK, sw=1.5))
    P.append(text(bx0 - 18, (top + base) / 2, "I", size=12, color=INK, bold=True))
    # мікроамперний фон ULP — суцільна низька лінія з ледь помітними тіками вимірів
    P.append(line(bx0, floor, 715, floor, color=NEG, sw=2.0))
    for i, frac in enumerate((0.16, 0.34, 0.52, 0.70, 0.88)):
        tx = bx0 + frac * (715 - bx0)
        P.append(line(tx, floor, tx, floor - 7, color=FIELD, sw=1.5))   # тік виміру ULP
    # один рідкісний сплеск ядра
    spx = bx0 + 0.5 * (715 - bx0)
    P.append(rect(spx - 5, top + 8, 10, base - top - 8, fill="#fdecea", stroke="none", sw=0))
    P.append(line(spx, floor, spx, top + 8, color=POS, sw=2.0))
    P.append(line(spx, top + 8, spx + 10, top + 8, color=POS, sw=2.0))
    P.append(line(spx + 10, top + 8, spx + 10, floor, color=POS, sw=2.0))
    P.append(text(spx + 40, top + 16, "ядро — зрідка", size=10, color=POS, bold=True, anchor="start"))
    P.append(text(620, base + 26, "I_сер ≈ десятки мкА", size=12, color=FIELD, bold=True))
    P.append(text(620, base + 44, "← площа крихітна", size=10.5, color=MUTED))

    # підсумок
    P.append(fitbox(40, 358, W - 80, 28,
                    "виміри ті самі — ULP прибирає дорогі пробудження, заряд менший на порядки",
                    size=12, fill="#e9f7ef", stroke=FIELD))

    render("img/ulp-economics.svg", W, H, *P)


# ── Фігура 3: часова діаграма ULP + великих ядер (для вставки proj-) ──────────
# Ідея: чотири доріжки спільного часу. RTC-таймер тікає рівномірно; на кожен тік
# ULP коротко міряє (мікросекунди) і вирішує; великі ядра майже весь час у сні і
# спалахують лише на той тік, де вимір перейшов поріг. Видно, чому Iсер — мкА.
def fig_timeline():
    W, H = 900, 470
    P = [text(W / 2, 28, "ULP і великі ядра: хто коли активний", size=16, bold=True)]

    left = 150          # права межа підписів доріжок
    x0 = left           # початок осі часу
    x1 = 855
    ticks = [190, 320, 450, 580, 710]   # тіки RTC-таймера (спільна сітка)
    over = ticks[3]                       # на 4-му тіку вимір перейшов поріг

    lanes = [
        ("RTC-таймер", "тіки 20 мс", 80),
        ("ULP", "вимір АЦП", 150),
        ("рішення", "поза порогом?", 220),
        ("великі ядра", "струм", 300),
    ]
    for name, sub, y in lanes:
        P.append(text(left - 12, y - 4, name, size=12, color=INK, anchor="end", bold=True))
        P.append(text(left - 12, y + 12, sub, size=10.5, color=MUTED, anchor="end"))
        P.append(line(x0, y + 26, x1, y + 26, color="#e5e7eb", sw=1.0))

    # доріжка RTC-таймера: вузькі імпульси
    ty = 80
    for tx in ticks:
        P.append(line(tx, ty + 20, tx, ty - 14, color="#c0560b", sw=2.0))
        P.append(line(tx, ty - 14, tx + 8, ty - 14, color="#c0560b", sw=2.0))
        P.append(line(tx + 8, ty - 14, tx + 8, ty + 20, color="#c0560b", sw=2.0))
    P.append(line(ticks[0] + 8, ty - 26, ticks[1], ty - 26, color="#c0560b", sw=1.0))
    P.append(text((ticks[0] + ticks[1]) / 2, ty - 31, "≈20 мс", size=10, color="#c0560b"))

    # доріжка ULP: короткий вимір на кожен тік
    uy = 150
    for tx in ticks:
        P.append(rect(tx, uy - 14, 16, 30, fill=FILL, stroke=LINE, sw=1.3, rx=2))
    P.append(text(ticks[0] + 8, uy - 20, "≈мкс", size=10, color=INK))

    # доріжка рішення: «ні» на нормі, «так» на четвертому тіку
    dy = 220
    for tx in ticks:
        ok = (tx == over)
        col = FIELD if ok else MUTED
        fill = "#e9f7ef" if ok else "#f0f1f3"
        P.append(fitbox(tx - 30, dy - 14, 66, 30, "так!" if ok else "ні",
                        size=10.5, color=col, fill=fill, stroke=col, bold=ok))
    P.append(arrow(over + 3, dy + 16, over + 3, 286, color=POS, sw=1.8))
    P.append(text(over + 12, dy + 40, "wakeup", size=10, color=POS, anchor="start"))

    # доріжка великих ядер: смуга deep-sleep + один сплеск
    gy = 300
    P.append(rect(x0, gy, over - x0, 14, fill="#e2e6ea", stroke="#b9c0c7", sw=1.0, rx=0))
    P.append(text((x0 + over) / 2, gy - 6, "deep-sleep  (≈10 мкА)", size=10.5, color=MUTED))
    P.append(rect(over, gy - 22, 150, 36, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    P.append(text(over + 75, gy - 6, "пробудження (≈45 мА)", size=10.5, color=POS, bold=True))
    P.append(text(over + 75, gy + 9, "читає результат → знову спить", size=9.5, color=MUTED))

    # вісь часу
    P.append(arrow(x0, gy + 60, x1 + 8, gy + 60, color=INK, sw=1.4))
    P.append(text(x1 + 16, gy + 64, "t", size=13, color=INK, italic=True))
    for i, tx in enumerate(ticks):
        P.append(line(tx, gy + 56, tx, gy + 64, color=INK, sw=1.1))
        P.append(text(tx, gy + 78, "%d·Δt" % (i + 1), size=10, color=MUTED))

    # підсумок
    P.append(fitbox(W / 2 - 250, gy + 92, 500, 24,
                    "великі ядра спалахують лише на «так» — тому середній струм мікроамперний",
                    size=11.5, fill="#e9f7ef", stroke=FIELD))

    render("img/ulp-timeline.svg", W, H, *P)


if __name__ == "__main__":
    fig_guard()
    fig_economics()
    fig_timeline()
    print("OK: 3 figures -> img/")
