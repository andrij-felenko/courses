# -*- coding: utf-8 -*-
"""Фігури теми «Архітектура ExpressLRS». Запуск: python figs.py → ./img/*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: наскрізний ланцюг — пульт → передавач → ефір → приймач → політник ─
# Показує, ЩО таке ELRS: тонка ланка радіо між двома CRSF-дротами.
def fig_chain():
    W, H = 760, 300
    parts = []
    by = 90
    bh = 66
    bw = 128
    # чотири вузли з достатніми проміжками під дроти й ефір
    x_hand, x_tx, x_rx, x_fc = 24, 190, 470, 636
    parts.append(fitbox(x_hand, by, bw, bh, "Пульт\n(EdgeTX/OpenTX)", size=13, bold=True, fill=FILL))
    parts.append(fitbox(x_tx,   by, bw, bh, "Передавач ELRS\nMCU + радіочип", size=13, bold=True, fill="#eaf0fd"))
    parts.append(fitbox(x_rx,   by, bw, bh, "Приймач ELRS\nMCU + радіочип", size=13, bold=True, fill="#eaf0fd"))
    parts.append(fitbox(x_fc,   by, bw, bh, "Політник\n(FC)", size=13, bold=True, fill=FILL))

    cy = by + bh / 2
    # CRSF-дріт пульт→передавач
    ax1s, ax1e = x_hand + bw + 4, x_tx - 4
    parts.append(arrow(ax1s, cy, ax1e, cy, color=FIELD, sw=2.4))
    parts.append(text((ax1s+ax1e)/2, cy - 10, "CRSF", 11, FIELD, "middle", bold=True))
    parts.append(text((ax1s+ax1e)/2, by + bh + 16, "дріт у пульті", 10, MUTED, "middle"))

    # радіоланка передавач→приймач (ефір), двобічна
    rs, re = x_tx + bw + 6, x_rx - 6
    rmid = (rs + re) / 2
    parts.append(arrow(rs, cy - 8, re, cy - 8, color=POS, sw=2.6))
    parts.append(arrow(re, cy + 10, rs, cy + 10, color=NEG, sw=2.0))
    parts.append(text(rmid, cy - 18, "керування ↑", 11, POS, "middle", bold=True))
    parts.append(text(rmid, cy + 26, "телеметрія ↓", 11, NEG, "middle", bold=True))
    parts.append(text(rmid, by - 10, "радіоефір · FHSS", 12, INK, "middle", bold=True))
    parts.append(text(rmid, by + bh + 24, "2.4 ГГц або 900 МГц", 10, MUTED, "middle"))

    # CRSF-дріт приймач→політник
    ax2s, ax2e = x_rx + bw + 4, x_fc - 4
    parts.append(arrow(ax2s, cy, ax2e, cy, color=FIELD, sw=2.4))
    parts.append(text((ax2s+ax2e)/2, cy - 10, "CRSF", 11, FIELD, "middle", bold=True))
    parts.append(text((ax2s+ax2e)/2, by + bh + 16, "дріт у дроні", 10, MUTED, "middle"))

    parts.append(text(W/2, 252, "ELRS — це лише дві коробки й ефір між ними; з обох боків той самий серійний CRSF.",
                      12, INK, "middle"))
    return render(os.path.join(IMG, "chain.svg"), W, H, *parts, title="Наскрізний ланцюг керування")


# ── Фігура 2: обмін «частота пакетів ↔ чутливість/дальність» ─────────────────
# Стовпчики: що вище рейт, то менша чутливість (менша дальність), зате менша
# затримка. Точні числа з даташитів ELRS (2.4 ГГц).
def fig_rate_tradeoff():
    W, H = 700, 380
    parts = []
    # осі
    x0, y0 = 90, 300
    axw, axh = 540, 230
    parts.append(arrow(x0, y0, x0 + axw + 10, y0, color=MUTED, sw=1.3))     # вісь рейтів
    parts.append(arrow(x0, y0, x0, y0 - axh - 10, color=MUTED, sw=1.3))     # вісь чутливості
    parts.append(text(x0 + axw + 6, y0 + 18, "частота пакетів →", 11, MUTED, "end"))
    parts.append(text(x0 - 8, y0 - axh - 16, "чутливість (дальність)", 11, MUTED, "start"))

    # дані: (рейт, чутливість дБм, модуляція)
    # чутливість переводимо в висоту: -100 dBm → низько, -123 dBm → високо
    modes = [
        ("50 Гц",  -115, "LoRa"),
        ("150 Гц", -112, "LoRa"),
        ("250 Гц", -108, "LoRa"),
        ("500 Гц", -105, "LoRa"),
        ("1000 Гц", -104, "FLRC"),
    ]
    smin, smax = -104, -117   # діапазон для масштабу
    n = len(modes)
    slotw = axw / n
    bw = slotw * 0.5
    for i, (rate, sens, mod) in enumerate(modes):
        frac = (sens - smax) / (smin - smax)   # 0..1, більша чутливість — вище
        h = 30 + frac * (axh - 50)
        bx = x0 + i * slotw + (slotw - bw) / 2
        col = FIELD if mod == "LoRa" else POS
        fillc = "#e8f6ee" if mod == "LoRa" else "#fdecea"
        parts.append(rect(bx, y0 - h, bw, h, fill=fillc, stroke=col, sw=1.8))
        parts.append(text(bx + bw/2, y0 - h - 8, "%d дБм" % sens, 10, col, "middle", bold=True))
        parts.append(text(bx + bw/2, y0 + 16, rate, 11, INK, "middle", bold=True))
        parts.append(text(bx + bw/2, y0 + 30, mod, 9, MUTED, "middle"))

    # стрілка-напрямок унизу
    parts.append(text(x0 + axw/2, 355,
                      "ліворуч — далі й повільніше; праворуч — швидше й ближче",
                      12, INK, "middle"))
    return render(os.path.join(IMG, "rate-tradeoff.svg"), W, H, *parts,
                  title="Частота пакетів проти дальності (2.4 ГГц)")


# ── Фігура 3: FHSS — синхронний стрибок частотами за спільним UID ─────────────
def fig_fhss():
    W, H = 700, 360
    parts = []
    x0, y0 = 70, 300
    axw, axh = 560, 240
    parts.append(arrow(x0, y0, x0 + axw + 10, y0, color=MUTED, sw=1.3))     # час
    parts.append(arrow(x0, y0, x0, y0 - axh - 10, color=MUTED, sw=1.3))     # частота (канали)
    parts.append(text(x0 + axw + 6, y0 + 18, "час →", 11, MUTED, "end"))
    parts.append(text(x0 - 4, y0 - axh - 16, "канал", 11, MUTED, "start"))

    # сітка каналів
    nch = 6
    chh = axh / nch
    for c in range(nch):
        gy = y0 - c * chh - chh/2
        parts.append(line(x0, gy, x0 + axw, gy, color="#e5e7eb", sw=1.0, dash="2 5"))
        parts.append(text(x0 - 8, gy + 4, "f%d" % c, 9, MUTED, "end"))

    # псевдовипадкова послідовність каналів (задана UID)
    seq = [1, 4, 0, 3, 5, 2, 4, 1]
    nstep = len(seq)
    stepw = axw / nstep
    prev = None
    dots = []
    for i, ch in enumerate(seq):
        cx = x0 + i * stepw + stepw/2
        cy = y0 - ch * chh - chh/2
        dots.append((cx, cy))
        # маркер стрибка
        parts.append(circle(cx, cy, 7, fill="#eaf0fd", stroke=NEG, sw=2))
        parts.append(text(cx, y0 + 16, "%d" % (i+1), 9, MUTED, "middle"))
    # з'єднати стрибки лінією
    for i in range(1, len(dots)):
        parts.append(line(dots[i-1][0], dots[i-1][1], dots[i][0], dots[i][1],
                          color=NEG, sw=1.4, dash="4 3"))

    # рамка: обидва боки рахують ту саму послідовність із UID
    box, bwid, bhei = textbox(x0 + axw/2, 40,
        "TX і RX рахують ту саму послідовність із спільного UID —\nобидва знають, де слухати наступний пакет",
        size=12, fill=FILL, stroke=LINE)
    parts.append(box)
    return render(os.path.join(IMG, "fhss.svg"), W, H, *parts,
                  title="FHSS: синхронний стрибок каналами")


# ── Фігура 4: телеметричне співвідношення — рідкий зворотний слот у потоці ─────
def fig_tlm_ratio():
    W, H = 700, 260
    parts = []
    x0 = 40
    y = 120
    slot = 74
    gap = 6
    # співвідношення 1:4 — кожен 4-й слот віддано телеметрії (вниз)
    labels_up = ["кер.", "кер.", "кер.", "ТЛМ", "кер.", "кер.", "кер.", "ТЛМ"]
    n = len(labels_up)
    for i, lab in enumerate(labels_up):
        bx = x0 + i * (slot + gap)
        if lab == "ТЛМ":
            parts.append(rect(bx, y, slot, 46, fill="#eaf0fd", stroke=NEG, sw=1.8))
            parts.append(text(bx + slot/2, y + 28, "ТЛМ ↓", 12, NEG, "middle", bold=True))
        else:
            parts.append(rect(bx, y, slot, 46, fill="#fdecea", stroke=POS, sw=1.8))
            parts.append(text(bx + slot/2, y + 28, "кер. ↑", 12, POS, "middle", bold=True))
        parts.append(text(bx + slot/2, y - 8, "%d" % (i+1), 9, MUTED, "middle"))

    # шкала часу
    parts.append(arrow(x0, y + 70, x0 + n*(slot+gap) - gap, y + 70, color=MUTED, sw=1.3))
    parts.append(text(x0 + n*(slot+gap)/2, y + 88, "час (слоти пакетів однакової тривалості) →", 11, MUTED, "middle"))

    parts.append(text(W/2, 40,
        "Співвідношення 1:4 — кожен четвертий слот віддано зворотній телеметрії;", 12, INK, "middle"))
    parts.append(text(W/2, 58,
        "решта — керування. Один радіоканал працює в обидва боки почергово.", 12, INK, "middle"))
    return render(os.path.join(IMG, "tlm-ratio.svg"), W, H, *parts,
                  title="Телеметричне співвідношення (1:4)")


# ── Фігура 5 (для нарису про походження): хронологія народження ELRS ───────────
# Спина історії: від закритого стандарту 2015 до вибуху відкритої системи.
def fig_history():
    W, H = 760, 320
    parts = []
    bx = 60
    ex = W - 40
    ty = 150
    # головна вісь часу
    parts.append(arrow(bx, ty, ex, ty, color=MUTED, sw=1.6))
    parts.append(text(ex, ty + 20, "час →", 11, MUTED, "end"))

    # (частка_по_осі, рік, підпис угорі/внизу(+1/−1), колір, текст)
    events = [
        (0.02, "2015", -1, POS,   "TBS Crossfire:\nзакритий стандарт"),
        (0.30, "1.10.2018", +1, NEG, "Перший коміт\nAlessandroAU"),
        (0.50, "2019", -1, FIELD, "200 Гц на 900 МГц\nна залізі FrSky R9M"),
        (0.72, "~2020", +1, NEG, "2.4 ГГц (SX1280)\n+ дешеве залізо → вибух"),
        (0.95, "02.2021", -1, FIELD, "явний файл\nліцензії GPLv3"),
    ]
    for frac, year, side, col, label in events:
        px = bx + frac * (ex - bx)
        parts.append(circle(px, ty, 7, fill="#ffffff", stroke=col, sw=2.4))
        # рік — біля точки на осі
        yr_y = ty + 20 if side < 0 else ty - 12
        # виносна рамка з підписом
        box_cy = ty + side * 74
        box, bw, bh = textbox(px, box_cy, label, size=11, fill=("#fdecea" if col==POS else "#eaf0fd" if col==NEG else "#e8f6ee"),
                              stroke=col, color=INK)
        # тримати рамку в межах полотна по горизонталі
        shift = 0
        if px - bw/2 < 4:
            shift = 4 - (px - bw/2)
        elif px + bw/2 > W - 4:
            shift = (W - 4) - (px + bw/2)
        if shift:
            box, bw, bh = textbox(px + shift, box_cy, label, size=11,
                                  fill=("#fdecea" if col==POS else "#eaf0fd" if col==NEG else "#e8f6ee"),
                                  stroke=col, color=INK)
        # лінія-поводок від осі до рамки
        lead_y2 = box_cy - side * bh/2
        parts.append(line(px, ty, px + shift, lead_y2, color=col, sw=1.3, dash="3 3"))
        parts.append(box)
        parts.append(text(px, yr_y, year, 10, col, "middle", bold=True))

    parts.append(text(W/2, 40,
        "Від закритого стандарту до вибуху відкритої системи — за неповних п'ять років.",
        12, INK, "middle"))
    parts.append(text(W/2, 300,
        "Червоне — закрите; синє — ключові коміти; зелене — коли відкритість стала правилом.",
        10, MUTED, "middle"))
    return render(os.path.join(IMG, "history.svg"), W, H, *parts,
                  title="Хронологія народження ExpressLRS")


if __name__ == "__main__":
    fig_chain()
    fig_rate_tradeoff()
    fig_fhss()
    fig_tlm_ratio()
    fig_history()
    print("OK: figures written to", IMG)
