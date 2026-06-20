# -*- coding: utf-8 -*-
"""Фігури до теми «Кроковий мотор».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

import math


# ── 1. Принцип: котушки тягнуть зубчастий ротор по черзі ─────────────────────
def fig_principle():
    W, H = 720, 380
    f = [text(W / 2, 28, "Котушки живляться по черзі — ротор перестрибує між фіксаціями", size=16, bold=True)]

    def panel(x0, on_idx, caption, sub):
        cx, cy = x0 + 130, 200
        # корпус-статор
        f.append(circle(cx, cy, 96, fill="#f7f9fb", stroke=MUTED, sw=1.4))
        # чотири котушки-полюси хрестом
        poles = [(0, -1, "A"), (1, 0, "B"), (0, 1, "A′"), (-1, 0, "B′")]
        for i, (dx, dy, lab) in enumerate(poles):
            px, py = cx + dx * 96, cy + dy * 96
            live = (i == on_idx)
            col = POS if live else MUTED
            fl = "#fdecea" if live else "#eef1f5"
            f.append(rect(px - 17, py - 17, 34, 34, fill=fl, stroke=col,
                          sw=2.4 if live else 1.4, rx=4))
            f.append(text(px, py + 5, lab, size=13, bold=live, color=col))
            if live:
                f.append(text(px + (24 if dx >= 0 else -24), py - 22,
                              "під струмом", size=10, bold=True, color=POS,
                              anchor="start" if dx >= 0 else "end"))
        # ротор: зубчастий диск, що дивиться зубцем на ввімкнений полюс
        ang = {0: -90, 1: 0, 2: 90, 3: 180}[on_idx]
        for k in range(6):
            a = math.radians(ang + k * 60)
            tx, ty = cx + 52 * math.cos(a), cy + 52 * math.sin(a)
            f.append(circle(tx, ty, 7, fill="#dfe6ee", stroke=LINE, sw=1.3))
        f.append(circle(cx, cy, 40, fill="#cfd8e2", stroke=LINE, sw=1.6))
        f.append(circle(cx, cy, 6, fill=BG, stroke=LINE, sw=1.3))
        # зубець, який «спіймала» котушка — виділити
        a = math.radians(ang)
        hx, hy = cx + 52 * math.cos(a), cy + 52 * math.sin(a)
        f.append(circle(hx, hy, 7, fill="#fdecea", stroke=POS, sw=2.2))
        f.append(text(cx, cy + 130, caption, size=13, bold=True, color=INK))
        f.append(text(cx, cy + 150, sub, size=11, color=MUTED))

    panel(20, 0, "Крок 1: живимо A", "найближчий зуб стає навпроти A")
    f.append(arrow(310, 200, 360, 200, color=FIELD, sw=2.4))
    f.append(text(335, 184, "перемкнули", size=10, color=FIELD))
    panel(360, 1, "Крок 2: живимо B", "ротор довертається на один крок")
    render(os.path.join(IMG, "principle.svg"), W, H, *f)


# ── 2. Навіщо: розімкнений рахунок кроків проти замкненого зв'язку ───────────
def fig_open_loop():
    W, H = 720, 320
    f = [text(W / 2, 28, "Чому без давача: крок порахований — кут відомий", size=16, bold=True)]

    # верх: кроковий — розімкнена петля
    y1 = 92
    b0, w0, _ = textbox(120, y1, "лічильник\nкроків", size=12, fill="#eef6ef", stroke=FIELD)
    f.append(b0)
    f.append(arrow(120 + w0 / 2, y1, 300, y1, color=LINE))
    b1, w1, _ = textbox(360, y1, "драйвер\n(крок + напрям)", size=12, fill=FILL, stroke=LINE)
    f.append(b1)
    f.append(arrow(360 + w1 / 2, y1, 540, y1, color=LINE))
    b2, _, _ = textbox(600, y1, "мотор", size=12, fill="#eef2f8", stroke=NEG, bold=True)
    f.append(b2)
    f.append(text(W / 2, y1 - 44, "Кроковий: РОЗІМКНЕНА петля — зворотного дроту нема",
                  size=13, bold=True, color=FIELD))
    f.append(text(W / 2, y1 + 52, "кут = кроки × крок на оберт; нічого не міряємо",
                  size=11, color=MUTED))

    f.append(line(60, 168, W - 60, 168, color="#d6dde6", sw=1.2, dash="5,5"))

    # низ: серво — замкнена петля
    y2 = 246
    b3, w3, _ = textbox(120, y2, "ціль\n(кут)", size=12, fill=FILL, stroke=LINE)
    f.append(b3)
    f.append(arrow(120 + w3 / 2, y2, 300, y2, color=LINE))
    b4, w4, _ = textbox(360, y2, "регулятор\n+ підсилювач", size=12, fill=FILL, stroke=LINE)
    f.append(b4)
    f.append(arrow(360 + w4 / 2, y2, 540, y2, color=LINE))
    b5, w5, _ = textbox(600, y2, "мотор\n+ давач", size=12, fill="#fbeee6", stroke=POS, bold=True)
    f.append(b5)
    # дріг зворотного зв'язку
    f.append(line(600, y2 + 26, 600, y2 + 52, color=POS, sw=2))
    f.append(line(600, y2 + 52, 360, y2 + 52, color=POS, sw=2))
    f.append(arrow(360, y2 + 52, 360, y2 + 22, color=POS, sw=2))
    f.append(text(480, y2 + 66, "зворотний зв'язок: вимір реального кута", size=10.5, color=POS))
    f.append(text(W / 2, y2 - 40, "Серво: ЗАМКНЕНА петля — давач + регулятор",
                  size=13, bold=True, color=POS))
    render(os.path.join(IMG, "open-loop.svg"), W, H, *f)


# ── 3. Повний / напівкрок / мікрокрок ───────────────────────────────────────
def fig_microstep():
    W, H = 720, 360
    f = [text(W / 2, 28, "Та сама дуга — грубо сходинками або плавно мікрокроком", size=16, bold=True)]

    ox, oy = 80, 300
    ax_w, ax_h = 560, 230
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.7))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.7))
    f.append(text(ox + ax_w / 2, oy + 38, "час →", size=12, color=INK))
    f.append(text(ox - 52, oy - ax_h / 2, "кут", size=12, color=INK))
    f.append(text(ox - 52, oy - ax_h / 2 + 16, "ротора", size=11, color=MUTED))

    # плавна синусоїда-ідеал (мікрокрок)
    pts = []
    for i in range(0, 561, 6):
        t = i / 560.0
        y = oy - (0.5 + 0.5 * math.sin(t * 2 * math.pi - math.pi / 2)) * (ax_h - 30) - 10
        pts.append("%.1f,%.1f" % (ox + i, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join(pts), FIELD))
    f.append(text(ox + ax_w - 6, oy - ax_h + 30, "мікрокрок (плавно)",
                  size=12, color=FIELD, anchor="end", bold=True))

    # сходинки повного кроку (4 великі)
    def steps(divs, color, dash, label, ly):
        pts = []
        for s in range(divs + 1):
            t = s / float(divs)
            y = oy - (0.5 + 0.5 * math.sin(t * 2 * math.pi - math.pi / 2)) * (ax_h - 30) - 10
            x = ox + t * ax_w
            if pts:
                pts.append("%.1f,%.1f" % (x, prev_y))
            pts.append("%.1f,%.1f" % (x, y))
            prev_y = y
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"%s/>'
                 % (" ".join(pts), color,
                    ' stroke-dasharray="%s"' % dash if dash else ''))
        f.append(text(ox + 8, ly, label, size=12, color=color, anchor="start", bold=True))

    steps(4, POS, None, "повний крок (4 грубі сходинки)", oy - 14)
    steps(8, NEG, "5,4", "напівкрок (удвічі дрібніше)", oy - 14 - 18)
    render(os.path.join(IMG, "microstep.svg"), W, H, *f)


# ── 4. Момент і пропуск кроків: крива моменту від швидкості ──────────────────
def fig_torque():
    W, H = 720, 360
    f = [text(W / 2, 28, "Момент падає зі швидкістю — за межею ротор зриває крок", size=16, bold=True)]

    ox, oy = 90, 300
    ax_w, ax_h = 540, 235
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.7))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.7))
    f.append(text(ox + ax_w / 2, oy + 38, "швидкість (кроків за секунду) →", size=12, color=INK))
    f.append(text(ox - 58, oy - ax_h / 2, "момент", size=12, color=INK))

    # спадна крива моменту
    pts = []
    for i in range(0, 541, 6):
        t = i / 540.0
        y = oy - (1.0 / (1.0 + 3.2 * t)) * (ax_h - 24) - 12
        pts.append("%.1f,%.1f" % (ox + i, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), NEG))
    f.append(text(ox + 150, oy - (1.0 / (1.0 + 3.2 * 150 / 540.0)) * (ax_h - 24) - 30,
                  "доступний момент", size=12, color=NEG, bold=True, anchor="start"))

    # лінія потрібного моменту (навантаження)
    need_y = oy - 0.42 * (ax_h - 24) - 12
    f.append(line(ox, need_y, ox + ax_w, need_y, color=POS, sw=2, dash="6,5"))
    f.append(text(ox + ax_w - 6, need_y - 8, "момент, потрібний навантаженню",
                  size=12, color=POS, anchor="end", bold=True))

    # точка перетину — межа
    # знайти t, де крива = need
    cross_t = None
    for i in range(0, 541, 2):
        t = i / 540.0
        y = oy - (1.0 / (1.0 + 3.2 * t)) * (ax_h - 24) - 12
        if y >= need_y:
            cross_t = t
            cross_x = ox + i
            break
    if cross_t is not None:
        f.append(line(cross_x, oy, cross_x, need_y, color=MUTED, sw=1.3, dash="3,3"))
        f.append(circle(cross_x, need_y, 4.5, fill=BG, stroke=INK, sw=1.6))
        b, _, _ = textbox(cross_x + 96, need_y - 58,
                          "за цією швидкістю\nмомент менший за потрібний\n→ пропуск кроків",
                          size=11, fill="#fbeee6", stroke=POS)
        f.append(b)
        f.append(text(cross_x, oy + 18, "гранична швидкість", size=10.5, color=MUTED))
    render(os.path.join(IMG, "torque.svg"), W, H, *f)


# ── 5. Драйвер: стабілізація струму (chopper) ───────────────────────────────
def fig_driver():
    W, H = 720, 360
    f = [text(W / 2, 28, "Драйвер тримає ЗАДАНИЙ струм у котушці, а не напругу", size=16, bold=True)]

    # блок-схема: MCU → драйвер (H-міст + сенс) → котушка
    b0, w0, _ = textbox(95, 110, "MCU\nSTEP / DIR", size=12, fill="#eef6ef", stroke=FIELD)
    f.append(b0)
    f.append(arrow(95 + w0 / 2, 110, 210, 110, color=LINE))
    b1, w1, h1 = textbox(300, 110, "драйвер:\nH-міст + датчик струму\n+ компаратор", size=12,
                         fill=FILL, stroke=LINE)
    f.append(b1)
    f.append(arrow(300 + w1 / 2, 110, 470, 110, color=LINE))
    # котушка-спіраль (символ)
    cxL = 520
    f.append(text(cxL + 40, 86, "котушка", size=11, color=MUTED))
    loops = []
    for i in range(4):
        loops.append('<path d="M%.0f %.0f a10 14 0 1 1 0.1 0" fill="none" stroke="%s" stroke-width="2.2"/>'
                     % (cxL + i * 20, 110, NEG))
    f.extend(loops)
    f.append(line(cxL - 14, 110, cxL, 110, color=NEG, sw=2.2))
    f.append(line(cxL + 78, 110, cxL + 96, 110, color=NEG, sw=2.2))

    # нижче: «рубання» струму пилкою навколо уставки
    ox, oy = 110, 320
    ax_w, ax_h = 500, 120
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.5))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.5))
    f.append(text(ox + ax_w / 2, oy + 26, "час →", size=11, color=INK))
    f.append(text(ox - 52, oy - ax_h / 2, "струм", size=11, color=INK))
    # уставка
    set_y = oy - 0.7 * ax_h
    f.append(line(ox, set_y, ox + ax_w, set_y, color=POS, sw=1.8, dash="6,4"))
    f.append(text(ox + ax_w - 4, set_y - 8, "уставка струму", size=11, color=POS, anchor="end", bold=True))
    # наростання до уставки, потім пила (вмик/вимик ключів)
    pts = ["%.1f,%.1f" % (ox, oy)]
    x = ox
    # наростання
    while x < ox + 150:
        x += 8
        frac = min(0.7, (x - ox) / 150.0 * 0.7)
        pts.append("%.1f,%.1f" % (x, oy - frac * ax_h))
    # пила навколо уставки
    up = False
    while x < ox + ax_w - 6:
        x += 14
        y = set_y + (10 if up else -10)
        pts.append("%.1f,%.1f" % (x, y))
        up = not up
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (" ".join(pts), NEG))
    f.append(text(ox + 330, oy - ax_h + 4, "ключі рубають струм, тримаючи уставку",
                  size=10.5, color=MUTED, anchor="middle"))
    render(os.path.join(IMG, "driver.svg"), W, H, *f)


if __name__ == "__main__":
    fig_principle()
    fig_open_loop()
    fig_microstep()
    fig_torque()
    fig_driver()
    print("OK: 5 figures ->", IMG)
