# -*- coding: utf-8 -*-
"""Фігури до теми «pymavlink».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

CODE_BG = "#1b1f24"      # темна заливка код-панелі
CODE_FG = "#cfe8cf"      # світло-зелений код
AMBER   = "#b08900"      # тепле виділення (MAVLink-міст)


# ── 1. pymavlink: бібліотека кількома рядками ─────────────────────────────────
# Ідея: ліворуч — мінімальний код, що вже читає потік апарата; праворуч — що
# саме бібліотека бере на себе. Показуємо: розмова з апаратом коротка.
def fig_library():
    W, H = 760, 290
    f = [text(W / 2, 26, "pymavlink: MAVLink у Python кількома рядками", size=15, bold=True)]

    # код-панель
    cx, cy, cw, ch = 30, 56, 470, 150
    f.append(rect(cx, cy, cw, ch, fill=CODE_BG, stroke=INK, sw=1.5, rx=8))
    code = [
        "from pymavlink import mavutil",
        "m = mavutil.mavlink_connection(",
        "        'udpin:localhost:14550')",
        "m.wait_heartbeat()        # апарат на лінії",
        "while True:",
        "    msg = m.recv_match(blocking=True)",
        "    # …реагуй, шли команди, веди логіку…",
    ]
    ly = cy + 24
    for ln in code:
        f.append(text(cx + 16, ly, ln, size=10.5, color=CODE_FG, anchor="start"))
        ly += 18

    # права панель — що дає бібліотека
    px, py, pw, ph = 520, 56, 210, 150
    f.append(rect(px, py, pw, ph, fill="#fbfbfb", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(px + pw / 2, py + 24, "бібліотека бере на себе:", size=10.5, color=FIELD, bold=True))
    items = ["• з'єднання serial/udp/tcp", "• розбір і пакування кадрів",
             "• усі діалекти з тих XML", "• основа MAVProxy"]
    iy = py + 50
    for it in items:
        f.append(text(px + 12, iy, it, size=9.5, color=INK, anchor="start"))
        iy += 22

    f.append(text(W / 2, H - 14,
                  "кілька рядків — і ти вже читаєш потік апарата",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "library.svg"), W, H, *f)


# ── 2. Бортовий комп'ютер: розум на самому апараті ────────────────────────────
# Ідея: маленький Linux-комп'ютер поряд із контролером, з'єднаний КОРОТКИМ UART
# (а не радіо). Підкреслено: дріт замість ефіру.
def fig_companion():
    W, H = 760, 280
    f = [text(W / 2, 26, "Бортовий комп'ютер: розум прямо на апараті", size=15, bold=True)]

    # апарат-пропелер (схематично) угорі по центру
    cx, cy, r = W / 2, 92, 13
    for dx in (-32, 32):
        f.append(circle(cx + dx, cy - 20, r, fill="none", stroke=NEG, sw=2))
        f.append(circle(cx + dx, cy + 20, r, fill="none", stroke=NEG, sw=2))
    f.append(line(cx - 32, cy - 20, cx + 32, cy + 20, color=NEG, sw=3))
    f.append(line(cx - 32, cy + 20, cx + 32, cy - 20, color=NEG, sw=3))
    f.append(rect(cx - 14, cy - 10, 28, 20, fill="#e9eefb", stroke=NEG, sw=1.6, rx=3))
    f.append(text(cx, cy + 44, "апарат", size=10, color=NEG, italic=True))

    # дві коробки: контролер ←UART→ комп'ютер
    by = 180
    fc = fitbox(170, by, 150, 64, "політний\nконтролер", size=11.5, color=POS,
                fill="#fbfbfb", stroke=POS, sw=1.8, bold=True)
    cc = fitbox(440, by, 160, 64, "бортовий комп'ютер\n(Raspberry Pi / Jetson)",
                size=9.5, color=FIELD, fill="#fbfbfb", stroke=FIELD, sw=1.6, bold=True)
    f.append(fc); f.append(cc)
    f.append(line(320, by + 32, 440, by + 32, color=INK, sw=3))
    f.append(text(380, by + 22, "UART", size=9, color=INK, bold=True))

    f.append(text(W / 2, H - 14,
                  "MAVLink по короткому дроту — швидко, надійно, без ефіру",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "companion.svg"), W, H, *f)


# ── 3. Поділ праці: політ окремо, розум окремо ───────────────────────────────
# Ідея: дві ролі поряд — контролер (реальний час, надійність) та комп'ютер
# (важке думання); між ними MAVLink обома напрямками.
def fig_architecture():
    W, H = 760, 300
    f = [text(W / 2, 26, "Поділ праці: політ окремо, розум окремо", size=15, bold=True)]

    # ліва панель — контролер
    lx, ly, pw, ph = 40, 70, 290, 180
    f.append(rect(lx, ly, pw, ph, fill="#fbfbfb", stroke=POS, sw=1.8, rx=10))
    f.append(text(lx + pw / 2, ly + 26, "Політний контролер", size=12.5, color=POS, bold=True))
    for i, s in enumerate(["• стабілізація, реальний час", "• читання давачів, мотори",
                           "• надійність понад усе", "• проста, перевірена логіка"]):
        f.append(text(lx + 18, ly + 56 + i * 28, s, size=10.5, color=INK, anchor="start"))

    # права панель — комп'ютер
    rx = 430
    f.append(rect(rx, ly, pw, ph, fill="#fbfbfb", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(rx + pw / 2, ly + 26, "Бортовий комп'ютер", size=12.5, color=FIELD, bold=True))
    for i, s in enumerate(["• комп'ютерний зір, ШІ", "• складні рішення, маршрути",
                           "• зв'язок (LTE, мережа)", "• важкі обчислення"]):
        f.append(text(rx + 18, ly + 56 + i * 28, s, size=10.5, color=INK, anchor="start"))

    # MAVLink між ними, обидва напрямки
    midy = ly + ph / 2
    f.append(arrow(lx + pw, midy - 14, rx, midy - 14, color=AMBER, sw=2.4))
    f.append(arrow(rx, midy + 14, lx + pw, midy + 14, color=AMBER, sw=2.4))
    f.append(text((lx + pw + rx) / 2, midy - 22, "MAVLink", size=9.5, color=AMBER, bold=True))

    f.append(text(W / 2, H - 12,
                  "контролер — «спинний мозок» (рефлекси); комп'ютер — «головний мозок» (плани)",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "architecture.svg"), W, H, *f)


# ── 4. Повне коло: початкова мета й сьогодення ────────────────────────────────
# Ідея: ліворуч — мета 2008-го (дрон, що сам бачить), MAVLink лише побічний;
# праворуч — сьогодні той самий зір живе на борту через pymavlink.
def fig_full_circle():
    W, H = 760, 280
    f = [text(W / 2, 26, "Повне коло: початкова мета здійснюється", size=15, bold=True)]

    # ліва — мета 2008
    lx, ly, pw, ph = 40, 64, 250, 150
    f.append(rect(lx, ly, pw, ph, fill="#fbfbfb", stroke=NEG, sw=1.8, rx=10))
    f.append(text(lx + pw / 2, ly + 26, "2008: мета", size=11.5, color=NEG, bold=True))
    f.append(mtext(lx + pw / 2, ly + 56, ["дрон, що сам бачить", "і літає (зір)"], size=10, color=INK))
    f.append(mtext(lx + pw / 2, ly + 104, ["MAVLink —", "лише побічний інструмент"],
                   size=9.5, color=MUTED))

    # стрілка «роки»
    f.append(arrow(lx + pw + 6, ly + ph / 2, lx + pw + 70, ly + ph / 2, color=INK, sw=2.4))
    f.append(text(lx + pw + 38, ly + ph / 2 - 10, "роки", size=9, color=MUTED))

    # права — сьогодні
    rx = lx + pw + 80
    f.append(rect(rx, ly, pw, ph, fill="#fbfbfb", stroke=FIELD, sw=1.8, rx=10))
    f.append(text(rx + pw / 2, ly + 26, "сьогодні", size=11.5, color=FIELD, bold=True))
    f.append(mtext(rx + pw / 2, ly + 56, ["бортовий комп'ютер +", "pymavlink + зір/ШІ"],
                   size=10, color=INK))
    f.append(mtext(rx + pw / 2, ly + 104, ["= та сама автономність,", "якої прагнули"],
                   size=9.5, color=FIELD, bold=True))

    f.append(text(W / 2, H - 12,
                  "інструмент, зроблений «між іншим», тепер несе той самий зір",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "full-circle.svg"), W, H, *f)


# ── 5. Що можна автоматизувати на борту ───────────────────────────────────────
# Ідея: чотири типові сценарії «читай → вирішуй → командуй», тепер без людини.
def fig_scenarios():
    W, H = 760, 280
    f = [text(W / 2, 26, "Що можна автоматизувати на борту", size=15, bold=True)]

    cards = [
        ("🔋", "Розумний failsafe", "сів заряд →\nсам шле RTL", AMBER),
        ("🎯", "Слідкування за ціллю", "зір бачить об'єкт →\nкоригує курс", FIELD),
        ("🧱", "Геозона", "наблизився до межі →\nне пускає далі", POS),
        ("🗺", "Авто-картографування", "облітає площу\nй знімає за планом", NEG),
    ]
    cw, gap = 170, 14
    x = (W - (cw * 4 + gap * 3)) / 2
    for emo, title_, note, col in cards:
        f.append(rect(x, 56, cw, 178, fill="#fbfbfb", stroke=col, sw=2, rx=12))
        f.append(text(x + cw / 2, 96, emo, size=22))
        f.append(fitbox(x + 8, 110, cw - 16, 30, title_, size=11.5, color=col, bold=True,
                        fill="#fbfbfb", stroke="none", sw=0))
        f.append(mtext(x + cw / 2, 168, note.split("\n"), size=9.8, color=INK))
        x += cw + gap

    f.append(text(W / 2, H - 12,
                  "той самий цикл «читай → вирішуй → командуй», але без людини",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "scenarios.svg"), W, H, *f)


# ── 6. Екосистема над pymavlink ───────────────────────────────────────────────
# Ідея: pymavlink — фундамент; над ним рівні (MAVProxy, MAVSDK, MAVROS→ROS).
def fig_ecosystem():
    W, H = 760, 320
    f = [text(W / 2, 26, "Від pymavlink до великої робототехніки", size=15, bold=True)]

    rows = [
        ("MAVProxy", "командний GCS і проксі на pymavlink", NEG),
        ("MAVSDK / DroneKit", "вищі рівні API для зручнішої автоматизації", FIELD),
        ("MAVROS", "міст MAVLink ↔ ROS — велика робототехніка", AMBER),
    ]
    nx, nw = 70, 220
    dx, dw = nx + nw + 34, 360
    y = 60
    for name, note, col in rows:
        f.append(rect(nx, y, nw, 50, fill="#fbfbfb", stroke=col, sw=1.6, rx=9))
        f.append(text(nx + nw / 2, y + 30, name, size=12.5, color=col, bold=True))
        f.append(arrow(nx + nw + 4, y + 25, dx - 4, y + 25, color=INK, sw=1.6))
        f.append(rect(dx, y, dw, 50, fill="#f7f7f7", stroke=col, sw=1.3, rx=9))
        f.append(text(dx + 16, y + 30, note, size=11, color=INK, anchor="start"))
        y += 66

    # фундамент
    f.append(rect(70, y + 4, dx + dw - 70, 38, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=9))
    f.append(text(70 + (dx + dw - 70) / 2, y + 28,
                  "усе стоїть на тому самому MAVLink, що задає кадр до байта",
                  size=10.5, color=INK, bold=True))
    render(os.path.join(IMG, "ecosystem.svg"), W, H, *f)


if __name__ == "__main__":
    fig_library()
    fig_companion()
    fig_architecture()
    fig_full_circle()
    fig_scenarios()
    fig_ecosystem()
    print("OK: 6 figures ->", IMG)
