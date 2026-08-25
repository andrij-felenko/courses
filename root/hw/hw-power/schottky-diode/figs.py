# -*- coding: utf-8 -*-
"""Фігури для статті «Діод Шотткі».
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── barrier-compare: два бар'єри поруч — PN-дифузійний vs контакт метал—напівпров. ──
# Серце теми: у кремнієвого PN висота бар'єра ~0.7 В — це вбудований дифузійний
# потенціал двох легованих областей; у Шотткі контакт метал—напівпровідник дає
# лише різницю робіт виходу ~0.3 В. Нижчий бар'єр → нижче Vf.

def fig_barrier_compare():
    W, H = 720, 380
    p = []

    # дві колонки-схеми
    def stack(cx, top_lbl, mid_lbl, bot_lbl, mid_col, mid_fill, barrier_v, note):
        col = []
        bw, x0 = 150, cx - 75
        # верхній шар
        col.append(rect(x0, 80, bw, 48, fill="#e8eefc", stroke=NEG, sw=1.8))
        col.append(text(cx, 109, top_lbl, size=13, color=NEG, bold=True))
        # межа-перехід (виділена смуга) з підписом висоти бар'єра
        col.append(rect(x0, 128, bw, 34, fill=mid_fill, stroke=mid_col, sw=2.2))
        col.append(text(cx, 150, mid_lbl, size=12, color=mid_col, bold=True))
        # нижній шар
        col.append(rect(x0, 162, bw, 48, fill="#fdece9", stroke=POS, sw=1.8))
        col.append(text(cx, 191, bot_lbl, size=13, color=POS, bold=True))
        # підпис висоти бар'єра збоку
        col.append(text(cx, 245, barrier_v, size=16, color=INK, bold=True))
        col.append(text(cx, 266, note, size=11, color=MUTED))
        return col

    p += stack(200, "n-кремній", "дифузійний бар'єр", "p-кремній",
               INK, "#efece2", "≈ 0.7 В", "звичайний PN-діод")
    p += stack(520, "n-кремній", "контакт метал—напівпр.", "метал (аноду)",
               FIELD, "#eaf7ef", "≈ 0.3 В", "діод Шотткі")

    # стрілка «нижчий бар'єр» між колонками
    p.append(text(360, 150, "→", size=30, color=INK, bold=True))
    p.append(text(360, 300, "нижчий бар'єр → менше прямого падіння Vf → менше тепла",
                  size=12, color=INK, italic=True))

    render(os.path.join(OUT, "barrier-compare.svg"), W, H, *p,
           title="Чому Шотткі падає менше: PN-бар'єр ~0.7 В проти контакту ~0.3 В")


# ── reverse-recovery: PN «висмоктує» накопичений заряд, Шотткі гасне чисто ──────
# Ідея: при різкому закриванні PN-діод іще мить проводить у ЗВОРОТНИЙ бік — струм
# провалюється нижче нуля, поки виметається накопичений дірковий заряд (Qrr).
# Шотткі неосновного заряду не має → закривається майже миттєво, без провалу.

def fig_reverse_recovery():
    W, H = 720, 360
    L, R = 90, 660
    T, B = 70, 250
    zero = 175                 # рівень I = 0
    p = []

    # осі
    p.append(line(L, T, L, B, color=INK, sw=2))
    p.append(line(L, zero, R, zero, color=INK, sw=2))      # вісь часу на рівні нуля
    p.append(text(L - 12, T - 6, "струм", size=12, color=INK, anchor="start", italic=True))
    p.append(text(R, zero + 20, "час →", size=12, color=MUTED, anchor="end", italic=True))
    p.append(text(L - 14, zero + 4, "0", size=11, color=MUTED, anchor="end"))

    # момент перемикання
    xsw = L + 0.42 * (R - L)
    p.append(line(xsw, T, xsw, B, color=MUTED, sw=1.0, dash="4,4"))
    p.append(text(xsw, B + 22, "команда «закрийся»", size=11, color=MUTED))

    # PN-діод (червоний): вів уперед, потім провал нижче нуля (recovery), тоді 0
    Ifwd = zero - 60
    Irr = zero + 46            # провал зворотного струму
    pn = []
    pn.append((L, Ifwd))
    pn.append((xsw, Ifwd))
    # різкий провал у мінус
    pn.append((xsw + 8, Irr))
    # відновлення до нуля по хвості
    for k in range(1, 13):
        t = k / 12.0
        x = xsw + 8 + t * 90
        y = Irr - (Irr - zero) * (1 - math.exp(-3.2 * t))
        pn.append((x, y))
    for i in range(len(pn) - 1):
        p.append(line(pn[i][0], pn[i][1], pn[i + 1][0], pn[i + 1][1], color=POS, sw=2.6))
    p.append(text(L + 6, Ifwd - 10, "PN-діод", size=12, color=POS, anchor="start", bold=True))
    # підпис провалу
    p.append(text(xsw + 60, Irr + 20, "зворотний «висмок» Qrr", size=11, color=POS))

    # Шотткі (зелений): вів уперед, гасне майже вертикально до нуля, без провалу
    sy = zero - 30
    sk = []
    sk.append((L, sy))
    sk.append((xsw, sy))
    sk.append((xsw + 6, zero))          # чистий зріз до нуля
    sk.append((R - 20, zero))
    for i in range(len(sk) - 1):
        p.append(line(sk[i][0], sk[i][1], sk[i + 1][0], sk[i + 1][1], color=FIELD, sw=2.6))
    p.append(text(L + 6, sy - 10, "Шотткі", size=12, color=FIELD, anchor="start", bold=True))
    p.append(text(xsw + 70, zero - 12, "гасне чисто, без провалу", size=11, color=FIELD))

    p.append(text(W / 2, H - 20,
                  "PN-діод іще мить жене струм назад, поки виметається накопичений заряд; Шотткі його не має",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "reverse-recovery.svg"), W, H, *p,
           title="Зворотне відновлення: PN «висмоктує» заряд, Шотткі гасне миттєво")


# ── leakage-vs-temp: ціна за низький бар'єр — зворотний витік, що росте з нагрівом ─
# Ідея: нижчий бар'єр легше «перестрибнути» тепловим електронам, тож зворотний
# витік Шотткі на порядки більший за PN і круто росте з температурою — аж до
# теплового розгону, якщо діод грітиме сам себе.

def fig_leakage_vs_temp():
    W, H = 700, 380
    L, R = 90, 620
    T, B = 70, 300
    Tmin, Tmax = 25.0, 125.0
    p = []

    def px(tc): return L + (tc - Tmin) / (Tmax - Tmin) * (R - L)
    # лог-вісь витоку: 1 мкА .. 100 мА → 5 декад
    dec_min, dec_max = -6.0, -1.0   # log10(A): 1e-6 .. 1e-1
    def py(logi): return B - (logi - dec_min) / (dec_max - dec_min) * (B - T)

    # осі
    p.append(line(L, T, L, B, color=INK, sw=2))
    p.append(line(L, B, R, B, color=INK, sw=2))
    for tc in (25, 50, 75, 100, 125):
        x = px(tc)
        p.append(line(x, B, x, B + 5, color=INK, sw=1.2))
        p.append(text(x, B + 22, "%d" % tc, size=12, color=MUTED))
    p.append(text((L + R) / 2, B + 44, "температура кристала, °C", size=12, color=INK, italic=True))
    labels = {-6: "1 мкА", -5: "10 мкА", -4: "100 мкА", -3: "1 мА", -2: "10 мА", -1: "100 мА"}
    for d in range(-6, 0):
        y = py(d)
        p.append(line(L - 5, y, L, y, color=INK, sw=1.0))
        p.append(text(L - 10, y + 4, labels[d], size=10, color=MUTED, anchor="end"))
    p.append(text(L - 6, T - 16, "зворотний витік (лог)", size=12, color=INK, italic=True, anchor="start"))

    # Шотткі: круто росте (кожні ~10 °C приблизно × ~1.8) — від ~30 мкА до ~10 мА
    sch = []
    for tc in range(25, 126, 5):
        i25 = 3e-5
        i = i25 * (1.8 ** ((tc - 25) / 10.0))
        sch.append((px(tc), py(math.log10(min(i, 1e-1)))))
    for i in range(len(sch) - 1):
        p.append(line(sch[i][0], sch[i][1], sch[i + 1][0], sch[i + 1][1], color=POS, sw=2.6))
    p.append(text(px(96), py(math.log10(3e-5 * 1.8 ** ((96 - 25) / 10.0))) - 12,
                  "Шотткі", size=13, color=POS, bold=True, anchor="end"))

    # PN-діод: майже пласко внизу, ~кілька мкА
    pn = []
    for tc in range(25, 126, 5):
        i = 1e-6 * (2.0 ** ((tc - 25) / 25.0))
        pn.append((px(tc), py(math.log10(i))))
    for i in range(len(pn) - 1):
        p.append(line(pn[i][0], pn[i][1], pn[i + 1][0], pn[i + 1][1], color=NEG, sw=2.6))
    p.append(text(px(70), py(math.log10(1e-6 * 2.0 ** ((70 - 25) / 25.0))) + 20,
                  "звичайний PN-діод", size=12, color=NEG, bold=True))

    p.append(text(W / 2, H - 14,
                  "гарячий Шотткі тече назад дедалі більше, гріється ще дужче — і може піти в тепловий розгін",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "leakage-vs-temp.svg"), W, H, *p,
           title="Ціна низького бар'єра: зворотний витік Шотткі росте з нагрівом")


if __name__ == "__main__":
    fig_barrier_compare()
    fig_reverse_recovery()
    fig_leakage_vs_temp()
    print("OK: figures written to", OUT)
