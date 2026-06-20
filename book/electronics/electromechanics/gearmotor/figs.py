# -*- coding: utf-8 -*-
"""Фігури до теми «Мотор-редуктор».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def gear(cx, cy, r, teeth, fill=FILL, stroke=INK, sw=1.6, tooth=0.16, hub=0.30):
    """Спрощена шестерня: коло + прямокутні зуби по колу + маточина."""
    out = []
    tl = r * tooth
    for i in range(teeth):
        a = math.radians(i * 360.0 / teeth)
        x0, y0 = cx + r * math.cos(a), cy + r * math.sin(a)
        x1, y1 = cx + (r + tl) * math.cos(a), cy + (r + tl) * math.sin(a)
        out.append(line(x0, y0, x1, y1, color=stroke, sw=sw * 2.4))
    out.append(circle(cx, cy, r, fill=fill, stroke=stroke, sw=sw))
    out.append(circle(cx, cy, r * hub, fill=BG, stroke=stroke, sw=sw))
    return "".join(out)


# ── 1. Чому мотор+редуктор зрослися: окремо vs готовий вузол ──────────────────
def fig_why_integrated():
    W, H = 760, 380
    f = [text(W / 2, 26, "Окремі мотор і редуктор vs готовий мотор-редуктор",
              size=16, bold=True)]

    # ─ ліва панель: те, що треба збирати самому ─
    f.append(rect(30, 60, 350, 290, fill="#fbfdff", stroke="#d6dde6", sw=1.4, rx=10))
    f.append(text(205, 84, "зібрати й узгодити самому", size=12.5, bold=True, color=MUTED))
    # мотор
    f.append(rect(60, 120, 78, 56, fill="#eef2f8", stroke=INK, sw=1.6, rx=6))
    f.append(mtext(99, 142, ["мотор", "швидкий,", "слабкий"], size=10, color=INK, lh=1.15))
    # шестерні (купка)
    f.append(gear(200, 150, 26, 12))
    f.append(gear(244, 168, 18, 10))
    f.append(text(222, 200, "набір шестерень", size=10, color=MUTED))
    # корпус
    f.append(rect(300, 122, 56, 52, fill=FILL, stroke=MUTED, sw=1.4, rx=5))
    f.append(text(328, 152, "корпус", size=10, color=MUTED))
    # перелік клопотів
    b, _, _ = textbox(205, 270, "порахувати i, дібрати вали,\nспіввісність, посадити в корпус",
                      size=10.5, fill="#fdecea", stroke=POS, min_w=300)
    f.append(b)
    f.append(text(205, 322, "— інженерне завдання щоразу", size=11, color=POS, italic=True))

    # стрілка-перехід
    f.append(arrow(392, 205, 432, 205, color=FIELD, sw=3))

    # ─ права панель: готовий вузол ─
    f.append(rect(445, 60, 290, 290, fill="#f3fbf5", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(590, 84, "мотор-редуктор (готовий)", size=12.5, bold=True, color=FIELD))
    # суцільний корпус
    f.append(rect(485, 140, 120, 70, fill="#eef2f8", stroke=INK, sw=1.8, rx=8))
    f.append(mtext(545, 168, ["мотор +", "редуктор", "в одному"], size=11, color=INK, lh=1.15, bold=True))
    # вихідний вал
    f.append(line(605, 175, 690, 175, color=INK, sw=7))
    f.append(circle(692, 175, 8, fill=MUTED, stroke=INK, sw=1.5))
    f.append(text(648, 160, "один вал", size=10.5, color=INK))
    b, _, _ = textbox(590, 270, "повільний, сильний,\nузгоджений на заводі",
                      size=11, fill="#eafaef", stroke=FIELD, min_w=240, bold=True)
    f.append(b)
    f.append(text(590, 322, "— готова деталь з паспортом", size=11, color=FIELD, italic=True))
    render(os.path.join(IMG, "why-integrated.svg"), W, H, *f)


# ── 2. Обмін обертів на момент усередині: швидко-слабко → повільно-сильно ─────
def fig_speed_torque_trade():
    W, H = 760, 340
    f = [text(W / 2, 26, "Редуктор міняє оберти на момент: потужність майже зберігається",
              size=16, bold=True)]

    # вхід (мотор)
    b1, _, _ = textbox(120, 110, "вал мотора\nвисокі оберти\nмалий момент",
                       size=12, fill="#eaf0fd", stroke=NEG, min_w=180, bold=True)
    f.append(b1)
    f.append(text(120, 175, "n_мотора · M_мотора = P", size=11, color=NEG))

    # блок редуктора
    f.append(arrow(215, 110, 300, 110, color=INK, sw=2.4))
    f.append(gear(345, 110, 30, 14))
    f.append(gear(345, 110, 30, 14))  # (підсилення видимості зубів)
    f.append(text(345, 165, "редуктор  ·i", size=12, bold=True, color=INK))
    f.append(arrow(395, 110, 480, 110, color=INK, sw=2.4))

    # вихід
    b2, _, _ = textbox(595, 110, "вихідний вал\nоберти / i\nмомент · i · η",
                       size=12, fill="#fdecea", stroke=POS, min_w=180, bold=True)
    f.append(b2)
    f.append(text(595, 175, "n_вих · M_вих ≈ P", size=11, color=POS))

    # втрата в тепло
    f.append(arrow(345, 145, 345, 205, color="#e08a3c", sw=2))
    f.append(text(345, 224, "частина P → тепло (тертя зубів)", size=11, color="#e08a3c"))

    # підпис унизу — суть
    b3, _, _ = textbox(W / 2, 285,
                       "оберти падають у i разів  →  момент росте майже в i разів (мінус ККД)",
                       size=12.5, fill="#eef2f8", stroke=INK, min_w=560, bold=True)
    f.append(b3)
    render(os.path.join(IMG, "speed-torque-trade.svg"), W, H, *f)


# ── 3. Шкала передавальних чисел: мале vs велике ─────────────────────────────
def fig_gear_ratio():
    W, H = 760, 360
    f = [text(W / 2, 26, "Передавальне число «1:i» — компроміс швидкість ↔ сила",
              size=16, bold=True)]

    # вісь-шкала
    ox, oy, w = 70, 150, 620
    f.append(line(ox, oy, ox + w, oy, color=INK, sw=2))
    for frac, lab in [(0.0, "1:5"), (0.25, "1:10"), (0.5, "1:50"),
                      (0.75, "1:100"), (1.0, "1:300")]:
        x = ox + frac * w
        f.append(line(x, oy - 6, x, oy + 6, color=INK, sw=1.6))
        f.append(text(x, oy - 14, lab, size=12, bold=True, color=INK))
    f.append(text(ox + w / 2, oy + 26, "передавальне число", size=11, color=MUTED))

    # ліворуч (мале число)
    b1, _, _ = textbox(ox + 95, 250,
                       "малі числа:\nшвидкий, але слабкий вихід\nмало ступенів, ККД вищий",
                       size=11, fill="#eaf0fd", stroke=NEG, min_w=250)
    f.append(b1)
    f.append(arrow(ox + 95, 205, ox + 30, oy + 12, color=NEG, sw=1.8))

    # праворуч (велике число)
    b2, _, _ = textbox(ox + w - 95, 250,
                       "великі числа:\nповільний і дуже сильний вихід\nбільше ступенів, ККД нижчий, гарячіше",
                       size=11, fill="#fdecea", stroke=POS, min_w=250)
    f.append(b2)
    f.append(arrow(ox + w - 95, 205, ox + w - 30, oy + 12, color=POS, sw=1.8))

    # нагадування про перемноження ККД
    b3, _, _ = textbox(W / 2, 322,
                       "ККД ступенів ПЕРЕМНОЖУЄТЬСЯ: 0.9 × 0.9 × 0.9 ≈ 0.73",
                       size=12, fill="#fff6ec", stroke="#e08a3c", min_w=430, bold=True)
    f.append(b3)
    render(os.path.join(IMG, "gear-ratio.svg"), W, H, *f)


# ── 4. Три типи редуктора всередині ──────────────────────────────────────────
def fig_types():
    W, H = 770, 360
    f = [text(W / 2, 26, "Три типи редуктора всередині мотор-редуктора",
              size=16, bold=True)]

    # ── прямозубий ──
    cx = 145
    f.append(text(cx, 70, "Прямозубий", size=13, bold=True, color=INK))
    f.append(gear(cx - 34, 150, 26, 12))
    f.append(gear(cx + 22, 150, 26, 12))
    f.append(line(cx + 48, 150, cx + 96, 150, color=INK, sw=6))   # вал збоку
    b, _, _ = textbox(cx, 268, "дешево, ремонтопридатно\nале шумно, довгий ряд",
                      size=10.5, fill=FILL, stroke=MUTED, min_w=215)
    f.append(b)

    # ── планетарний ──
    cx = 390
    f.append(text(cx, 70, "Планетарний", size=13, bold=True, color=INK))
    f.append(circle(cx, 150, 56, fill="#fbfdff", stroke=INK, sw=1.6))   # вінець
    f.append(gear(cx, 150, 18, 10, fill="#fdecea", stroke=POS))         # сонце
    for a in (90, 210, 330):
        px = cx + 36 * math.cos(math.radians(a))
        py = 150 + 36 * math.sin(math.radians(a))
        f.append(gear(px, py, 12, 8, fill="#eaf0fd", stroke=NEG))       # сателіти
    f.append(text(cx, 222, "сонце · сателіти · вінець", size=9.5, color=MUTED))
    b, _, _ = textbox(cx, 268, "великий момент у малому\nспіввісному корпусі, дорожчий",
                      size=10.5, fill="#f3fbf5", stroke=FIELD, min_w=235)
    f.append(b)

    # ── черв'ячний ──
    cx = 635
    f.append(text(cx, 70, "Черв'ячний", size=13, bold=True, color=INK))
    f.append(gear(cx + 6, 162, 30, 16))                                 # колесо
    # черв'як (гвинт) збоку зверху
    f.append(rect(cx - 40, 112, 70, 20, fill="#eef2f8", stroke=INK, sw=1.5, rx=4))
    for i in range(6):
        xx = cx - 36 + i * 11
        f.append(line(xx, 112, xx + 6, 132, color=MUTED, sw=1.4))
    f.append(text(cx - 5, 106, "черв'як", size=9.5, color=MUTED))
    b, _, _ = textbox(cx, 268, "велике сповільнення + само-\nгальмування, але низький ККД",
                      size=10.5, fill="#fff6ec", stroke="#e08a3c", min_w=235)
    f.append(b)
    render(os.path.join(IMG, "types.svg"), W, H, *f)


# ── 5. Люфт: зазор між зубами при зміні напряму ──────────────────────────────
def fig_backlash():
    W, H = 760, 360
    f = [text(W / 2, 26, "Люфт: при зміні напряму вихід стоїть, поки вибирається зазор",
              size=16, bold=True)]

    def panel(x0, title, gap, moved):
        cxa, cya = x0 + 95, 175      # колесо входу
        cxb, cyb = x0 + 235, 175     # колесо виходу
        f.append(text(x0 + 165, 70, title, size=13, bold=True, color=INK))
        f.append(gear(cxa, cya, 40, 12, fill="#eaf0fd", stroke=NEG))
        f.append(gear(cxb, cyb, 40, 12, fill="#fdecea", stroke=POS))
        f.append(text(cxa, cya + 70, "вхід (мотор)", size=10.5, color=NEG))
        f.append(text(cxb, cyb + 70, "вихід", size=10.5, color=POS))
        # зуб входу і зуб виходу в зоні зачеплення з зазором/без
        midy = cya
        zx = (cxa + cxb) / 2
        # зуб входу
        f.append(rect(zx - 18 - gap, midy - 9, 9, 18, fill=NEG, stroke=INK, sw=1.2, rx=2))
        # зуб виходу
        f.append(rect(zx + 9, midy - 9, 9, 18, fill=POS, stroke=INK, sw=1.2, rx=2))
        if gap > 0:
            f.append(line(zx - 9 - gap, midy + 28, zx + 9, midy + 28, color="#e08a3c", sw=1.6))
            f.append(text(zx, midy + 44, "зазор", size=10.5, color="#e08a3c"))
        else:
            f.append(text(zx, midy + 44, "зуби торкнулись", size=10, color=FIELD))
        b, _, _ = textbox(x0 + 165, 300, moved, size=11,
                          fill=FILL if gap > 0 else "#f3fbf5",
                          stroke="#e08a3c" if gap > 0 else FIELD, min_w=300)
        f.append(b)

    panel(20, "Щойно змінили напрям", 22, "вхід уже рухається,\nвихід ЩЕ СТОЇТЬ")
    f.append(line(W / 2, 70, W / 2, 330, color="#d6dde6", sw=1.2, dash="4,5"))
    panel(400, "Зазор вибрано", 0, "зуби зійшлися —\nтільки тепер вихід рушив")
    render(os.path.join(IMG, "backlash.svg"), W, H, *f)


if __name__ == "__main__":
    fig_why_integrated()
    fig_speed_torque_trade()
    fig_gear_ratio()
    fig_types()
    fig_backlash()
    print("OK: 5 figures ->", IMG)
