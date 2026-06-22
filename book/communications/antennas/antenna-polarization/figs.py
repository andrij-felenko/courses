# -*- coding: utf-8 -*-
"""Фігури до теми «Поляризація антени».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math

# Локальні відтінки понад палітру svgkit
WAVE = "#c0392b"     # хвиля / поле E — гаряча лінія
WAVE2 = "#2457d6"    # друга (схрещена) хвиля
GOOD = FIELD         # «проходить», згода — зелене
BAD = POS            # «мертво», провал — червоне


def _sine(x0, y0, length, amp, cycles, phase=0.0, color=WAVE, sw=2.4, n=120):
    """Полілінія-синусоїда вздовж осі X від (x0,y0) на довжину length."""
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + t * length
        y = y0 - amp * math.sin(2 * math.pi * cycles * t + phase)
        pts.append("%.1f,%.1f" % (x, y))
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (" ".join(pts), color, sw))


# ── 1. Орієнтація антени задає поляризацію ───────────────────────────────────
def fig_orientation():
    W, H = 720, 340
    f = [text(W / 2, 26, "Куди дріт — туди й поле E", size=16, bold=True)]

    # ліва панель: вертикальна антена → вертикальне E
    cxL = 200
    base = 250
    f.append(line(cxL, base, cxL, base - 120, color=INK, sw=4))          # дріт
    f.append(circle(cxL, base, 5, fill=INK, stroke=INK, sw=1))            # основа
    f.append(text(cxL, base + 26, "вертикальна антена", size=12, bold=True))
    # стрілки поля E вздовж дроту (вертикальні)
    for dy in (-100, -70, -40):
        f.append(arrow(cxL, base + dy + 16, cxL, base + dy - 16, color=WAVE, sw=2.2))
        f.append(arrow(cxL, base + dy - 16, cxL, base + dy + 16, color=WAVE, sw=2.2))
    f.append(text(cxL + 60, base - 70, "E ↕", size=14, color=WAVE, bold=True))
    f.append(text(cxL, base + 46, "→ вертикальна поляризація", size=11, color=MUTED))

    # права панель: горизонтальна антена → горизонтальне E
    cxR = 520
    f.append(line(cxR - 60, base - 60, cxR + 60, base - 60, color=INK, sw=4))   # дріт
    f.append(circle(cxR, base - 60, 5, fill=INK, stroke=INK, sw=1))
    f.append(text(cxR, base + 26, "горизонтальна антена", size=12, bold=True))
    for dx in (-40, 0, 40):
        f.append(arrow(cxR + dx - 16, base - 110, cxR + dx + 16, base - 110, color=WAVE, sw=2.2))
        f.append(arrow(cxR + dx + 16, base - 110, cxR + dx - 16, base - 110, color=WAVE, sw=2.2))
    f.append(text(cxR, base - 132, "E ↔", size=14, color=WAVE, bold=True))
    f.append(text(cxR, base + 46, "→ горизонтальна поляризація", size=11, color=MUTED))

    render(os.path.join(IMG, "orientation.svg"), W, H, *f)


# ── 2. Передавач і приймач мусять збігатися ──────────────────────────────────
def fig_matching():
    W, H = 720, 360
    f = [text(W / 2, 26, "Поляризації мусять збігатися", size=16, bold=True)]

    rows = [
        (95,  "vert", "vert", GOOD, "повний сигнал"),
        (185, "horz", "horz", GOOD, "повний сигнал"),
        (285, "vert", "horz", BAD,  "майже нічого"),
    ]
    txC, rxC = 150, 470
    for y, tx, rx, col, verdict in rows:
        # передавач
        if tx == "vert":
            f.append(line(txC, y + 28, txC, y - 28, color=INK, sw=4))
        else:
            f.append(line(txC - 28, y, txC + 28, y, color=INK, sw=4))
        # приймач
        if rx == "vert":
            f.append(line(rxC, y + 28, rxC, y - 28, color=INK, sw=4))
        else:
            f.append(line(rxC - 28, y, rxC + 28, y, color=INK, sw=4))
        # хвиля між ними
        f.append(_sine(txC + 36, y, rxC - txC - 72, 14, 4,
                       color=(GOOD if col == GOOD else MUTED), sw=2.2))
        # вердикт
        bx = rxC + 60
        f.append(circle(bx, y, 12, fill=("#eafaf0" if col == GOOD else "#fdecea"),
                        stroke=col, sw=2))
        f.append(text(bx, y + 5, "✓" if col == GOOD else "✕", size=15, color=col, bold=True))
        f.append(text(bx + 24, y + 5, verdict, size=12, color=col, anchor="start", bold=True))

    f.append(text(txC, 332, "передавач", size=11, color=MUTED))
    f.append(text(rxC, 332, "приймач", size=11, color=MUTED))
    render(os.path.join(IMG, "matching.svg"), W, H, *f)


# ── 3. Втрати від кута: закон cos²θ ──────────────────────────────────────────
def fig_angle_loss():
    W, H = 760, 360
    ox, oy = 90, 300
    aw, ah = 470, 210
    f = [text(W / 2, 26, "Втрати від кута: закон cos²θ", size=16, bold=True)]

    # осі
    f.append(arrow(ox, oy, ox + aw + 8, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.8))
    f.append(text(ox + aw, oy + 22, "кут θ", size=12, color=INK, bold=True, anchor="end"))
    f.append(text(ox - 12, oy - ah, "проходить", size=11, color=INK, anchor="start", bold=True))

    # крива cos²θ від 0 до 90
    pts = []
    for i in range(91):
        th = i
        v = math.cos(math.radians(th)) ** 2
        x = ox + (th / 90.0) * aw
        y = oy - v * ah
        pts.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" '
             'stroke-linejoin="round"/>' % (" ".join(pts), GOOD))

    # позначки на кривій
    marks = [(0, "0° → 0 дБ"), (45, "45° → −3 дБ"), (60, "60° → −6 дБ"), (90, "90° → ≈0")]
    for th, lbl in marks:
        v = math.cos(math.radians(th)) ** 2
        x = ox + (th / 90.0) * aw
        y = oy - v * ah
        f.append(circle(x, y, 4, fill=WAVE, stroke=WAVE, sw=0))
        anc = "end" if th == 90 else "start"
        dx = -8 if th == 90 else 8
        f.append(text(x + dx, y - 8, lbl, size=10.5, color=WAVE, bold=True, anchor=anc))

    # ось абсцис: підписи кутів
    for th in (0, 45, 90):
        x = ox + (th / 90.0) * aw
        f.append(line(x, oy - 5, x, oy + 5, color=INK, sw=1))
        f.append(text(x, oy + 22, "%d°" % th, size=10, color=MUTED))

    # рамка-висновок праворуч (через fitbox — текст не вилазить)
    f.append(fitbox(600, 100, 150, 170,
                    "На практиці\n90° дає не нуль,\nа −20…−30 дБ —\nзв'язку фактично\nнема.\n\nДо 30°\nвтрати дрібні.",
                    size=11, fill="#fbf3f3", stroke=BAD, color=INK))

    render(os.path.join(IMG, "angle-loss.svg"), W, H, *f)


# ── 4. Чому телефон працює під будь-яким нахилом (деполяризація) ──────────────
def fig_depolarization():
    W, H = 720, 360
    f = [text(W / 2, 26, "Відбиття «розмазують» поляризацію", size=16, bold=True)]

    # передавач ліворуч
    tx = (90, 180)
    f.append(line(tx[0], tx[1] + 26, tx[0], tx[1] - 26, color=INK, sw=4))
    f.append(text(tx[0], tx[1] + 46, "джерело", size=11, color=MUTED))

    # стіни-відбивачі (прямокутники)
    walls = [(360, 70, 120, 16), (520, 250, 16, 90), (250, 300, 140, 16)]
    for x, y, w, h in walls:
        f.append(rect(x, y, w, h, fill="#e9edf2", stroke=MUTED, sw=1.2, rx=2))

    # приймач (нахилений телефон) праворуч
    rx = (630, 200)
    f.append('<g transform="rotate(35 %d %d)">%s</g>' % (
        rx[0], rx[1], rect(rx[0] - 16, rx[1] - 34, 32, 68, fill="#f4f6f8", stroke=INK, sw=2, rx=6)))
    f.append(text(rx[0], rx[1] + 60, "нахилений\nтелефон" if False else "телефон (під кутом)",
                  size=11, color=MUTED))

    # промені: один прямий + кілька через відбиття, кольори = різні орієнтації
    cols = [WAVE, WAVE2, FIELD, "#8e44ad"]
    paths = [
        [(120, 180), (610, 195)],                       # майже прямий
        [(120, 175), (400, 90), (614, 185)],            # від верхньої стіни
        [(120, 190), (528, 280), (618, 210)],           # від правої стіни
        [(120, 195), (320, 310), (612, 205)],           # від нижньої стіни
    ]
    for col, pth in zip(cols, paths):
        d = "M %.0f,%.0f " % pth[0] + " ".join("L %.0f,%.0f" % p for p in pth[1:])
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8" '
                 'stroke-dasharray="2,3" opacity="0.85"/>' % (d, col))

    # підпис-висновок
    f.append(fitbox(250, 100, 200, 56,
                    "кожне відбиття трохи повертає\nполяризацію → до приймача\nдолітає суміш орієнтацій",
                    size=10.5, fill="#eafaf0", stroke=FIELD, color=INK))
    render(os.path.join(IMG, "depolarization.svg"), W, H, *f)


# ── 5. Колова поляризація: поле, що обертається ──────────────────────────────
def fig_circular():
    W, H = 720, 340
    f = [text(W / 2, 26, "Колова: вектор E обертається гвинтом", size=16, bold=True)]

    ox, oy = 90, 190
    length, amp = 520, 70
    # вісь руху
    f.append(arrow(ox, oy, ox + length + 8, oy, color=INK, sw=1.6))
    f.append(text(ox + length, oy + 24, "напрям руху", size=11, color=MUTED, anchor="end"))

    # дві схрещені складові: вертикальна (синус) і «горизонтальна» (косинус, як глибина)
    f.append(_sine(ox, oy, length, amp, 1.0, phase=0.0, color=WAVE, sw=2.0))            # верт. складова
    f.append(_sine(ox, oy, length, amp * 0.45, 1.0, phase=math.pi / 2, color=WAVE2, sw=2.0))  # «гор.» (зсув 90°)

    # вектори E у кількох точках → видно обертання (гвинт)
    n = 9
    for i in range(n + 1):
        t = i / n
        x = ox + t * length
        vy = amp * math.sin(2 * math.pi * t)
        f.append(line(x, oy, x, oy - vy, color=INK, sw=1.4))
        f.append(circle(x, oy - vy, 2.6, fill=WAVE, stroke=WAVE, sw=0))

    f.append(text(ox + 40, oy - amp - 6, "повний оберт за одну довжину хвилі", size=11, color=INK, anchor="start"))
    f.append(text(ox + 4, oy - amp - 28, "RHCP / LHCP — за напрямом обертання", size=11, color=MUTED, anchor="start"))
    render(os.path.join(IMG, "circular.svg"), W, H, *f)


# ── 6. Навіщо колова: байдужа до орієнтації, відсікає відбиття ───────────────
def fig_circular_benefit():
    W, H = 760, 360
    f = [text(W / 2, 26, "Три переваги колової поляризації", size=16, bold=True)]

    cards = [
        (130, "Байдужа до\nорієнтації", "лінійну ловить\nпід будь-яким кутом\n≈ −3 дБ, без нулів", FIELD),
        (385, "Відкидає\nвідбиття", "відбиття перевертає\n«руку» (RHCP↔LHCP)\n→ копії відсіюються", WAVE2),
        (640, "Подвоєння\nканалу", "RHCP і LHCP взаємно\n«глухі» → дві лінії\nна одній частоті", "#8e44ad"),
    ]
    for cx, head, body, col in cards:
        f.append(rect(cx - 105, 60, 210, 230, fill="#fbfdff", stroke=col, sw=1.8, rx=10))
        f.append(mtext(cx, 92, head, size=14, color=col, bold=True, lh=1.25))
        f.append(line(cx - 80, 142, cx + 80, 142, color=col, sw=1))
        f.append(mtext(cx, 172, body, size=11, color=INK, lh=1.4))

    f.append(text(W / 2, 326, "тому колову беруть для GPS і супутників — орієнтація постійно «гуляє»",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "circular-benefit.svg"), W, H, *f)


# ── 7. Поляризація на практиці: що коли брати ────────────────────────────────
def fig_practical():
    W, H = 720, 360
    f = [text(W / 2, 26, "Що коли брати", size=16, bold=True)]

    rows = [
        ("Нерухомий лінк точка-точка", "лінійна, узгоджена (обидві вертикальні)", FIELD),
        ("Місто / приміщення", "лінійна — відбиття все одно перемішають", FIELD),
        ("GPS і супутники", "колова RHCP — орієнтація не має значення", WAVE2),
        ("Дрон, що маневрує (FPV)", "колова — щоб не «провалюватись» у віражі", WAVE2),
    ]
    y = 70
    for left, right, col in rows:
        f.append(rect(40, y, 300, 52, fill="#f4f6f8", stroke=INK, sw=1.4, rx=8))
        f.append(fitbox(40, y, 300, 52, left, size=12.5, fill="#f4f6f8", stroke=INK, bold=True))
        f.append(arrow(345, y + 26, 378, y + 26, color=col, sw=2))
        f.append(fitbox(385, y, 295, 52, right, size=11.5, fill="#fbfdff", stroke=col))
        y += 68

    render(os.path.join(IMG, "practical.svg"), W, H, *f)


if __name__ == "__main__":
    fig_orientation()
    fig_matching()
    fig_angle_loss()
    fig_depolarization()
    fig_circular()
    fig_circular_benefit()
    fig_practical()
    print("OK: 7 figures ->", IMG)
