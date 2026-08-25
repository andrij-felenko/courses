# -*- coding: utf-8 -*-
"""Фігури до теми «Передача відео».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки понад палітру svgkit
AMBER = "#b9770e"     # цифрова дорога / бурштинова крива (тепле, читабельне)


# ── helper: ланка-блок із дворядковим написом ────────────────────────────────
def stage(f, cx, cy, w, h, top, bot, col):
    f.append(rect(cx - w / 2, cy - h / 2, w, h, fill=FILL, stroke=col, sw=1.7))
    if bot:
        f.append(text(cx, cy - 3, top, size=11.5, color=INK, bold=True))
        f.append(text(cx, cy + 13, bot, size=10, color=MUTED))
    else:
        f.append(text(cx, cy + 4, top, size=11.5, color=INK, bold=True))


# ── 1. Дві дороги з борту на землю ───────────────────────────────────────────
def fig_two_paths():
    W, H = 760, 360
    f = [text(W / 2, 26, "Дві дороги з борту на землю", size=15, bold=True)]

    # верхня доріжка: аналог
    f.append(text(40, 70, "Аналогове FPV", size=12.5, color=NEG, anchor="start", bold=True))
    ay = 104
    stage(f, 110, ay, 120, 50, "камера", "", NEG)
    stage(f, 270, ay, 130, 50, "відеосигнал", "яскр. + синхро", NEG)
    stage(f, 430, ay, 120, 50, "модулятор", "5.8 ГГц", NEG)
    stage(f, 660, ay, 120, 50, "демодул.", "+ окуляри", NEG)
    f.append(arrow(170, ay, 205, ay, color=INK, sw=1.6))
    f.append(arrow(335, ay, 365, ay, color=INK, sw=1.6))
    f.append(text(545, ay - 8, ")))", size=14, color=NEG, bold=True))
    f.append(text(545, ay + 8, "ефір", size=9, color=NEG))
    f.append(arrow(490, ay, 600, ay, color=NEG, sw=1.7))
    f.append(text(40, 148, "без стиску, без пакетів → майже нульова затримка; та грубо й односторонньо",
                  size=10, color=MUTED, anchor="start", italic=True))

    # нижня доріжка: цифра
    f.append(text(40, 210, "Цифрова мережа", size=12.5, color=AMBER, anchor="start", bold=True))
    dy = 244
    stage(f, 96, dy, 96, 50, "камера", "", AMBER)
    stage(f, 224, dy, 96, 50, "стиск", "H.264", AMBER)
    stage(f, 352, dy, 96, 50, "пакети", "", AMBER)
    stage(f, 488, dy, 110, 50, "радіо / IP", "", AMBER)
    stage(f, 668, dy, 104, 50, "збір + декод", "+ екран", AMBER)
    for x1, x2 in ((144, 176), (272, 304), (400, 433)):
        f.append(arrow(x1, dy, x2, dy, color=INK, sw=1.6))
    f.append(text(575, dy - 8, ")))", size=14, color=AMBER, bold=True))
    f.append(text(575, dy + 8, "ефір", size=9, color=AMBER))
    f.append(arrow(543, dy, 616, dy, color=AMBER, sw=1.7))
    f.append(text(40, 288, "HD, шифрування, маршрут в інтернет; та лаг (кодек + буфер) і складність",
                  size=10, color=MUTED, anchor="start", italic=True))

    f.append(text(W / 2, 332,
                  "аналог кладе відео просто на хвилю; цифра спершу стискає й пакетує — звідси й усі відмінності",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "two-paths.svg"), W, H, *f)


# ── 2. Аналогове FPV: відео просто на несучій ────────────────────────────────
def fig_analog_fpv():
    W, H = 760, 340
    f = [text(W / 2, 26, "Аналогове FPV: відео просто на несучій", size=15, bold=True)]

    y = 92
    stage(f, 110, y, 130, 54, "композитне", "відео", NEG)
    stage(f, 300, y, 130, 54, "модулятор", "~5.8 ГГц", NEG)
    stage(f, 560, y, 150, 54, "демодул. → окуляри", "", NEG)
    f.append(arrow(175, y, 235, y, color=INK, sw=1.7))
    f.append(text(430, y - 9, ")))", size=15, color=NEG, bold=True))
    f.append(text(430, y + 8, "ефір", size=9, color=NEG))
    f.append(arrow(365, y, 485, y, color=NEG, sw=1.8))

    # синусоїда композитного сигналу (синхро + яскравість)
    import math
    bx, by, bw = 50, 168, 200
    f.append(text(bx, by - 12, "один рядок: синхро + яскравість", size=10, color=MUTED, anchor="start"))
    pts = []
    for i in range(0, bw + 1, 4):
        t = i / bw
        if t < 0.12:                       # синхроімпульс — провал
            v = -0.9
        else:
            v = 0.5 * math.sin((t - 0.12) * 22) - 0.1
        pts.append((bx + i, by + 30 - v * 24))
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" '
             'stroke-linejoin="round"/>' % (poly, NEG))

    # ~40 каналів у діапазоні
    cbx, cby, cbw = 300, 168, 410
    f.append(text(cbx, cby - 12, "діапазон 5.8 ГГц: ~40 каналів", size=10, color=MUTED, anchor="start"))
    f.append(line(cbx, cby + 40, cbx + cbw, cby + 40, color=MUTED, sw=1.4))
    for k in range(40):
        x = cbx + 6 + k * (cbw - 12) / 39
        hh = 20 if k % 5 else 30
        col = FIELD if k % 5 == 0 else NEG
        f.append(line(x, cby + 40, x, cby + 40 - hh, color=col, sw=2))

    # за що люблять / чим платять
    yb = 250
    f.append(rect(40, yb, 330, 64, fill="#eef7f0", stroke=FIELD, sw=1.5))
    f.append(text(56, yb + 22, "За що люблять", size=11.5, color=FIELD, anchor="start", bold=True))
    f.append(text(56, yb + 42, "майже нульова затримка (нема кодека", size=10, color=INK, anchor="start"))
    f.append(text(56, yb + 56, "й буфера), плавне згасання, дешевизна", size=10, color=INK, anchor="start"))
    f.append(rect(390, yb, 330, 64, fill="#fdeeec", stroke=POS, sw=1.5))
    f.append(text(406, yb + 22, "Чим платять", size=11.5, color=POS, anchor="start", bold=True))
    f.append(text(406, yb + 42, "низька роздільність, шум і завади,", size=10, color=INK, anchor="start"))
    f.append(text(406, yb + 56, "односторонньо, без шифру, не HD", size=10, color=INK, anchor="start"))

    render(os.path.join(IMG, "analog-fpv.svg"), W, H, *f)


# ── 3. Цифра: відео як потік пакетів ─────────────────────────────────────────
def fig_packets_network():
    W, H = 760, 360
    f = [text(W / 2, 26, "Цифрова мережа: відео як потік пакетів", size=15, bold=True)]

    # бітпотік ріжуть на нумеровані пакети
    f.append(text(40, 62, "стиснений бітпотік → нумеровані пакети", size=11, color=MUTED, anchor="start"))
    px, py = 48, 76
    for i in range(6):
        x = px + i * 116
        col = POS if i == 3 else AMBER     # один загублений
        fill = "#fdeeec" if i == 3 else FILL
        f.append(rect(x, py, 104, 44, fill=fill, stroke=col, sw=1.6))
        if i == 3:
            f.append(text(x + 52, py + 20, "✗ втрата", size=10.5, color=POS, bold=True))
            f.append(text(x + 52, py + 36, "збій до I-кадру", size=9, color=MUTED))
        else:
            f.append(text(x + 52, py + 19, "№%d" % (i + 1), size=11, color=INK, bold=True))
            f.append(text(x + 52, py + 35, "заг. + відео", size=9, color=MUTED))

    # UDP+FEC рамка
    yb = 150
    f.append(rect(40, yb, 680, 70, fill="#fcfcfd", stroke="#e6e6ea", sw=1.4))
    f.append(text(56, yb + 24, "Наживо — по UDP, не TCP", size=12, color=INK, anchor="start", bold=True))
    f.append(text(56, yb + 44, "перепитувати марно: спізнілий кадр уже непотрібний;", size=10, color=MUTED, anchor="start"))
    f.append(text(56, yb + 58, "втрати латає FEC — надлишкові пакети, відновлення без зворотного запиту", size=10, color=MUTED, anchor="start"))

    # дві ніші
    yn = 244
    f.append(rect(40, yn, 330, 92, fill=FILL, stroke=NEG, sw=1.6))
    f.append(text(205, yn + 24, "локальний радіолінк", size=12, color=NEG, bold=True))
    f.append(text(205, yn + 44, "точка-точка: борт ↔ пульт", size=10, color=INK))
    f.append(text(205, yn + 62, "OcuSync · HDZero · Walksnail", size=9.5, color=MUTED, italic=True))
    f.append(text(205, yn + 80, "малий лаг, та обмежена дальність", size=9.5, color=MUTED, italic=True))

    f.append(rect(390, yn, 330, 92, fill=FILL, stroke=AMBER, sw=1.6))
    f.append(text(555, yn + 24, "IP-мережа", size=12, color=AMBER, bold=True))
    f.append(text(555, yn + 44, "LTE / 5G → інтернет", size=10, color=INK))
    f.append(text(555, yn + 62, "відео в хмару й за обрій (BVLOS)", size=9.5, color=MUTED, italic=True))
    f.append(text(555, yn + 80, "лаг мережі, залежність від покриття", size=9.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "packets-network.svg"), W, H, *f)


# ── 4. Плавно чи з обриву ─────────────────────────────────────────────────────
def fig_graceful_vs_cliff():
    W, H = 760, 380
    f = [text(W / 2, 26, "Плавно чи з обриву: як гасне картинка на краю дальності", size=15, bold=True)]

    ox, oy = 90, 300          # початок осей
    aw, ah = 600, 230         # розміри поля
    f.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.6))
    f.append(text(ox + aw, oy + 22, "слабшання сигналу / відстань →", size=10, color=MUTED, anchor="end", bold=True))
    f.append(text(ox + 6, oy - ah + 4, "↑ якість картинки", size=10, color=MUTED, anchor="start", bold=True))

    top = oy - ah + 16

    # аналог: плавне згасання (синій)
    apts = [(ox, top + 6), (ox + 110, top + 24), (ox + 220, top + 56),
            (ox + 330, top + 100), (ox + 440, top + 150), (ox + 540, top + 192),
            (ox + 600, oy - 8)]
    poly = " ".join("%.1f,%.1f" % p for p in apts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' % (poly, NEG))
    f.append(text(ox + 250, top + 70, "аналог — плавно", size=12, color=NEG, anchor="start", bold=True))
    f.append(text(ox + 470, oy - 60, "сніг росте, та видно", size=10, color=NEG, anchor="start"))
    f.append(text(ox + 470, oy - 46, "→ є запас і попередження", size=10, color=NEG, anchor="start"))

    # цифра: тримається й обривається (бурштин)
    cliff = ox + 360
    dpts = [(ox, top), (ox + 220, top), (cliff - 20, top + 8),
            (cliff, top + 16), (cliff + 8, oy - 6)]
    poly = " ".join("%.1f,%.1f" % p for p in dpts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' % (poly, AMBER))
    f.append(text(ox + 20, top - 4, "цифра — з обриву", size=12, color=AMBER, anchor="start", bold=True))
    f.append(circle(cliff, top + 16, 5, fill="#fdeeec", stroke=POS, sw=1.4))
    f.append(text(cliff + 14, top + 36, "«обрив»: ідеально… і раптом", size=10, color=POS, anchor="start", bold=True))
    f.append(text(cliff + 14, top + 50, "стоп-кадр / розсип квадратів", size=10, color=POS, anchor="start", bold=True))

    # підсумкова рамка
    yb = 332
    f.append(rect(ox, yb, aw, 40, fill="#fbf6ea", stroke=AMBER, sw=1.4))
    f.append(text(ox + aw / 2, yb + 17, "адаптивний бітрейт і FEC пом'якшують обрив — та зовсім його не прибрати:",
                  size=10, color="#7a5310"))
    f.append(text(ox + aw / 2, yb + 32, "за порогом декодер просто не збере кадр", size=10, color="#7a5310"))

    render(os.path.join(IMG, "graceful-vs-cliff.svg"), W, H, *f)


if __name__ == "__main__":
    fig_two_paths()
    fig_analog_fpv()
    fig_packets_network()
    fig_graceful_vs_cliff()
    print("OK: 4 figures ->", IMG)
