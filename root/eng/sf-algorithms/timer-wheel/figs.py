# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

FILLED = "#eafaf0"   # слот із таймерами (світло-зелений)
EMPTY  = "#f4f6f8"   # вільний слот
ACTIVE = "#fff3cd"   # поточний активний слот (жовтуватий)

def cell_positions(cx, cy, R, n=8, start_deg=-90):
    """Центри n слотів по колу за годинниковою стрілкою."""
    pts = []
    for i in range(n):
        a = math.radians(start_deg + i * (360.0 / n))
        pts.append((cx + R * math.cos(a), cy + R * math.sin(a)))
    return pts

# ── Fig 1: Однорівневе колесо таймерів ──────────────────────────────────────────
def fig_single_level():
    W, H = 850, 480
    p = []

    p.append(text(W / 2, 35, "Однорівневе колесо таймерів (Single-Level Timer Wheel)", size=16, color=INK, bold=True))

    cx, cy, R = 320, 260, 130
    n = 8
    cs = 44
    pts = cell_positions(cx, cy, R, n)
    occupied = {1, 3, 6}
    current_tick = 3

    # Малювання зовнішнього та внутрішнього кола
    p.append(circle(cx, cy, R + cs / 2 + 10, fill="none", stroke="#d8dde3", sw=1.2))
    p.append(circle(cx, cy, R - cs / 2 - 10, fill="none", stroke="#d8dde3", sw=1.2))

    for i, (x, y) in enumerate(pts):
        if i == current_tick:
            fill = ACTIVE
            stk = POS
            sw = 2.0
        elif i in occupied:
            fill = FILLED
            stk = FIELD
            sw = 1.6
        else:
            fill = EMPTY
            stk = LINE
            sw = 1.2
        p.append(rect(x - cs / 2, y - cs / 2, cs, cs, fill=fill, stroke=stk, sw=sw, rx=6))
        p.append(text(x, y + 4, f"[{i}]", size=12, color=INK, bold=True))

    # Покажчик поточного тіку
    curr_x, curr_y = pts[current_tick]
    ux = cx + (R - 55) * (curr_x - cx) / R
    uy = cy + (R - 55) * (curr_y - cy) / R
    ex_ = cx + (R - cs / 2 - 6) * (curr_x - cx) / R
    ey_ = cy + (R - cs / 2 - 6) * (curr_y - cy) / R
    p.append(arrow(ux, uy, ex_, ey_, color=POS, sw=2.5))
    p.append(text(cx, cy - 8, "current_tick = 3", size=13, color=POS, bold=True))
    p.append(text(cx, cy + 12, "Квант: δ = 10 ms", size=11, color=MUTED))

    # Список таймерів, приєднаний до слота 3 та слота 6
    # Для слота 3
    s3_x, s3_y = pts[3]
    lx1 = s3_x + cs / 2 + 8
    ly1 = s3_y
    p.append(arrow(s3_x + cs / 2, s3_y, lx1 + 20, ly1, color=FIELD, sw=1.8))

    box1, w1, h1 = textbox(lx1 + 80, ly1, "Timer ID: 42\ndelta: +0 (зараз)\nrounds: 0", size=10, fill="#e8f8f5", stroke=FIELD)
    p.append(box1)

    p.append(arrow(lx1 + 80 + w1 / 2, ly1, lx1 + 80 + w1 / 2 + 30, ly1, color=FIELD, sw=1.8))
    box2, w2, h2 = textbox(lx1 + 80 + w1 + 50, ly1, "Timer ID: 89\ndelta: +80 ms\nrounds: 1", size=10, fill="#fef9e7", stroke="#f39c12")
    p.append(box2)

    # Пояснення справа зверху
    p.append(rect(560, 60, 260, 120, fill="#f8f9fa", stroke="#bdc3c7", sw=1.0, rx=6))
    p.append(text(690, 82, "Правило вставки:", size=12, color=INK, bold=True))
    p.append(mtext(690, 102, "slot = (current + Δ / δ) mod N\nrounds = Δ / (N · δ)", size=11, color=INK))

    p.append(rect(560, 200, 260, 120, fill="#f8f9fa", stroke="#bdc3c7", sw=1.0, rx=6))
    p.append(text(690, 222, "Проблема rounds:", size=12, color=POS, bold=True))
    p.append(mtext(690, 242, "При переході на слот доводиться\nсканувати весь список і зменшувати\nrounds, навіть якщо таймер ще не дозрів!", size=10.5, color=INK))

    render(os.path.join(OUT, "single-level-wheel.svg"), W, H, *p,
           title="Однорівневе колесо таймерів зі слотами та списком обертів rounds")

# ── Fig 2: Ієрархічне таймерне колесо ──────────────────────────────────────────
def fig_hierarchical_wheel():
    W, H = 880, 460
    p = []

    p.append(text(W / 2, 30, "Ієрархічне колесо таймерів (Hierarchical Timer Wheel)", size=16, color=INK, bold=True))

    # Три рівні коліс: Wheel 0 (TV1), Wheel 1 (TV2), Wheel 2 (TV3)
    wheels = [
        {"name": "TV1 (Рівень 0)", "bits": "0..7 (256 слотів)", "range": "0..255 ms", "x": 160, "color": "#27ae60", "curr": 142},
        {"name": "TV2 (Рівень 1)", "bits": "8..13 (64 слоти)", "range": "256..16383 ms", "x": 440, "color": "#2980b9", "curr": 18},
        {"name": "TV3 (Рівень 2)", "bits": "14..19 (64 слоти)", "range": "16.4s..1048s", "x": 720, "color": "#8e44ad", "curr": 3}
    ]

    cy = 230
    R = 85
    n = 8
    cs = 32

    for w in wheels:
        cx = w["x"]
        p.append(text(cx, 75, w["name"], size=14, color=INK, bold=True))
        p.append(text(cx, 95, f"Біти: {w['bits']}", size=11, color=MUTED))
        p.append(text(cx, 112, f"Діапазон: {w['range']}", size=11, color=w["color"], bold=True))

        p.append(circle(cx, cy, R, fill=EMPTY, stroke=w["color"], sw=2.0))

        pts = cell_positions(cx, cy, R, n)
        curr_idx = w["curr"] % n

        for i, (x, y) in enumerate(pts):
            is_curr = (i == curr_idx)
            fill = ACTIVE if is_curr else BG
            stk = w["color"] if is_curr else "#cbd5e1"
            p.append(circle(x, y, 14, fill=fill, stroke=stk, sw=1.5 if is_curr else 1.0))
            p.append(text(x, y + 4, str(i), size=10, color=INK, bold=is_curr))

        # Покажчик поточного слота
        curr_x, curr_y = pts[curr_idx]
        p.append(arrow(cx, cy, curr_x, curr_y, color=w["color"], sw=2.0))

    # Стрілки каскадування між колесами
    p.append(arrow(370, cy, 270, cy, color=POS, sw=2.2))
    p.append(text(320, cy - 12, "Каскадування", size=11, color=POS, bold=True))
    p.append(text(320, cy + 16, "при TV1 wrap (255->0)", size=9.5, color=MUTED))

    p.append(arrow(650, cy, 550, cy, color=POS, sw=2.2))
    p.append(text(600, cy - 12, "Каскадування", size=11, color=POS, bold=True))
    p.append(text(600, cy + 16, "при TV2 wrap", size=9.5, color=MUTED))

    # Нижня інструкція про бітовий розподіл
    p.append(rect(100, 360, 680, 75, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=8))
    p.append(text(W / 2, 382, "Розподіл бітів таймауту в 32-бітному таймері:", size=12, color=INK, bold=True))
    p.append(mtext(W / 2, 404, "[ Біти 31..20: TV4 / TV5 ]  |  [ Біти 19..14: TV3 ]  |  [ Біти 13..8: TV2 ]  |  [ Біти 7..0: TV1 ]\nШвидке обчислення слота за один бітовий зсув та маскування:  slot = (expire >> shift) & mask", size=10.5, color=INK))

    render(os.path.join(OUT, "hierarchical-timer-wheel.svg"), W, H, *p,
           title="Ієрархічні колеса таймерів із каскадуванням між рівнями")

# ── Fig 3: Процес каскадування таймерів ──────────────────────────────────────────
def fig_timer_cascade():
    W, H = 840, 420
    p = []

    p.append(text(W / 2, 30, "Процес каскадування таймерів (Cascade Process)", size=16, color=INK, bold=True))

    # Крок 1: Тік TV1 обгортається на 0
    box1, w1, h1 = textbox(180, 110, "1. TV1 робить оберт (255 → 0)\nПоточний tick підходить до TV2[index]", size=11, fill="#e8f8f5", stroke=FIELD)
    p.append(box1)

    p.append(arrow(180, 150, 180, 200, color=FIELD, sw=2.0))

    # Крок 2: Витягування списку з TV2
    box2, w2, h2 = textbox(180, 240, "2. Витягування всього списку\nтаймерів із TV2[index]\n(слот TV2 очищається)", size=11, fill="#eaf2f8", stroke="#2980b9")
    p.append(box2)

    p.append(arrow(310, 240, 420, 240, color="#2980b9", sw=2.0))

    # Крок 3: Перехешування таймерів у TV1
    box3, w3, h3 = textbox(570, 240, "3. Для кожного таймера обчислюється\nзалишок часу Δ = expire - current_tick.\nТаймер переноситься у відповідний слот TV1!", size=11, fill="#fef9e7", stroke="#f39c12")
    p.append(box3)

    p.append(arrow(570, 180, 570, 140, color="#f39c12", sw=2.0))

    # Крок 4: Виконання O(1) у TV1
    box4, w4, h4 = textbox(570, 100, "4. Точне O(1) виконання:\nТаймер гарантовано спрацює\nпід час точного тіку в TV1!", size=11, fill="#fadbd8", stroke=POS)
    p.append(box4)

    # Нижня підсумкова картка
    p.append(rect(80, 310, 680, 80, fill="#f8f9fa", stroke="#bdc3c7", sw=1.2, rx=6))
    p.append(text(W / 2, 332, "Ключова перевага каскадування:", size=12, color=INK, bold=True))
    p.append(mtext(W / 2, 355, "Замість того щоб перевіряти кожен таймер на кожному тіку ($O(N)$),\nтаймер перебуває «в списку очікування» вищого колеса і переноситься в TV1\nлише тоді, коли до його спрацьовування лишається менше ніж 256 тіків!", size=11, color=INK))

    render(os.path.join(OUT, "timer-cascade-process.svg"), W, H, *p,
           title="Кроки алгоритму каскадування таймерів при зміщенні покажчика колеса")

if __name__ == "__main__":
    fig_single_level()
    fig_hierarchical_wheel()
    fig_timer_cascade()
    print("All figures generated successfully!")
