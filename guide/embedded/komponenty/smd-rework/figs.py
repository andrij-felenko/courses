# -*- coding: utf-8 -*-
"""Фігури до теми «Ручне паяння SMD».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

SOLDER = "#9aa3ad"   # припій (сірий метал)
PAD    = "#c98a2b"   # мідний майданчик
BODY   = "#3a4150"   # тіло компонента
HEAT   = POS         # тепло / гаряче


def solder_blob(cx, cy, w, h, concave=True):
    """Галтеля припою: ввігнута (добра) або опукла (холодна) крапля."""
    if concave:
        # увігнута: плавний трикутний клин від контакту до майданчика
        d = ('M %.1f %.1f Q %.1f %.1f %.1f %.1f L %.1f %.1f Z'
             % (cx - w/2, cy + h/2, cx, cy - h/2, cx + w/2, cy + h/2,
                cx - w/2, cy + h/2))
        return ('<path d="%s" fill="%s" stroke="%s" stroke-width="1.2"/>'
                % (d, SOLDER, LINE))
    else:
        # опукла кулька
        return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
                'stroke="%s" stroke-width="1.2"/>'
                % (cx, cy, w/2, h/2, "#b8bec6", LINE))


# ─────────────────────────────────────────────────────────────────────────────
# Фіг.1 — Тепловий місток: гостре сухе жало проти жала-копитця з краплею
# ─────────────────────────────────────────────────────────────────────────────
def fig_heat_bridge():
    W, H = 720, 360
    f = []
    f.append(text(W/2, 28, "Як жало передає тепло в з'єднання", size=17, bold=True))

    def board(x0, y0):
        # плата з мідним майданчиком і контактом компонента
        f.append(rect(x0, y0, 230, 26, fill="#e7eaee", stroke=LINE, sw=1.3, rx=3))
        f.append(rect(x0 + 40, y0 - 8, 150, 12, fill=PAD, stroke=LINE, sw=1.1, rx=2))  # майданчик
        f.append(rect(x0 + 120, y0 - 30, 80, 24, fill=BODY, stroke=LINE, sw=1.2, rx=3))  # тіло
        f.append(text(x0 + 160, y0 - 14, "контакт", size=10, color=BG))

    # ── Ліва панель: гостре сухе жало ──
    Lx = 40
    f.append(text(Lx + 115, 70, "гостре сухе жало", size=13, bold=True, color=NEG))
    board(Lx, 230)
    # жало гостре — клин, торкається точкою
    tipx = Lx + 75
    f.append('<path d="M %.0f %.0f L %.0f %.0f L %.0f %.0f Z" fill="#cfd5db" stroke="%s" stroke-width="1.4"/>'
             % (tipx - 24, 120, tipx + 24, 120, tipx, 214, LINE))
    f.append(text(tipx, 108, "жало", size=11, color=MUTED))
    # тонка цівка тепла — одна вузька стрілка
    f.append(arrow(tipx, 216, tipx, 226, color=HEAT, sw=2.0))
    f.append(text(Lx + 115, 300, "контакт точкою → тонка цівка тепла", size=11, color=INK))
    f.append(text(Lx + 115, 320, "дотик доводиться тримати довго", size=11, color=NEG))
    f.append(text(Lx + 115, 340, "→ плата перегрівається", size=11, bold=True, color=NEG))

    # ── Права панель: копитце + крапля ──
    Rx = 410
    f.append(text(Rx + 115, 70, "жало-копитце + крапля припою", size=13, bold=True, color=FIELD))
    board(Rx, 230)
    # жало зі зрізом — широкий контакт
    bx = Rx + 60
    f.append('<path d="M %.0f %.0f L %.0f %.0f L %.0f %.0f L %.0f %.0f Z" '
             'fill="#cfd5db" stroke="%s" stroke-width="1.4"/>'
             % (bx - 22, 120, bx + 22, 120, bx + 34, 206, bx - 4, 206, LINE))
    f.append(text(bx, 108, "жало", size=11, color=MUTED))
    # крапля припою — місток між жалом і майданчиком
    f.append('<ellipse cx="%.0f" cy="%.0f" rx="24" ry="12" fill="%s" stroke="%s" stroke-width="1.2"/>'
             % (bx + 15, 216, SOLDER, LINE))
    f.append(text(bx + 70, 200, "крапля = місток", size=10, color=FIELD))
    # широкий потік тепла — три стрілки
    for dx in (-12, 6, 24):
        f.append(arrow(bx + 15 + dx, 210, bx + 15 + dx, 226, color=HEAT, sw=2.0))
    f.append(text(Rx + 115, 300, "велика площа + рідкий місток", size=11, color=INK))
    f.append(text(Rx + 115, 320, "прогрів за частку секунди", size=11, color=FIELD))
    f.append(text(Rx + 115, 340, "→ прибрав жало, плата ціла", size=11, bold=True, color=FIELD))

    # роздільник
    f.append(line(W/2, 84, W/2, 348, color="#d0d4d9", sw=1.0, dash="4,4"))
    render(os.path.join(IMG, "heat-bridge.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# Фіг.2 — Паяння змахом: натяг розводить припій по майданчиках
# ─────────────────────────────────────────────────────────────────────────────
def fig_drag_solder():
    W, H = 720, 330
    f = []
    f.append(text(W/2, 28, "Паяння змахом: чому надлишок не замикає вивідки", size=17, bold=True))

    # тіло мікросхеми
    chip_y = 70
    f.append(rect(140, chip_y, 440, 40, fill=BODY, stroke=LINE, sw=1.4, rx=4))
    f.append(text(360, chip_y + 25, "корпус QFP / SOIC", size=12, color=BG))

    # ряд вивідків + майданчики під ними
    n = 8
    x0, step = 175, 50
    pad_y = chip_y + 40
    for i in range(n):
        px = x0 + i * step
        # вивідок (ніжка)
        f.append(rect(px - 5, pad_y, 10, 18, fill="#cfd5db", stroke=LINE, sw=1.0, rx=1))
        # майданчик
        f.append(rect(px - 18, pad_y + 18, 36, 12, fill=PAD, stroke=LINE, sw=1.1, rx=2))
        # припій стягнутий до КОЖНОГО майданчика окремо (увігнуті галтелі)
        f.append(solder_blob(px, pad_y + 30, 30, 16, concave=True))

    # чисті проміжки між майданчиками — підпис
    gapx = x0 + step // 2
    f.append(text(gapx + step, pad_y + 64, "чистий проміжок", size=10, color=FIELD))
    f.append(arrow(gapx + step, pad_y + 56, gapx + step - 6, pad_y + 40, color=FIELD, sw=1.6))

    # жало з надлишком припою веде вздовж ряду
    jy = pad_y + 44
    jx = x0 + (n - 1.4) * step
    f.append('<path d="M %.0f %.0f L %.0f %.0f L %.0f %.0f L %.0f %.0f Z" '
             'fill="#cfd5db" stroke="%s" stroke-width="1.4"/>'
             % (jx, jy + 70, jx + 36, jy + 70, jx + 24, jy + 6, jx + 12, jy + 6, LINE))
    f.append('<ellipse cx="%.0f" cy="%.0f" rx="26" ry="13" fill="%s" stroke="%s" stroke-width="1.2"/>'
             % (jx + 18, jy + 2, SOLDER, LINE))
    # стрілка напрямку змаху
    f.append(arrow(jx + 6, jy - 16, x0 + 6, jy - 16, color=HEAT, sw=2.2))
    f.append(text((jx + x0) / 2 + 10, jy - 24, "один рух жалом уздовж ряду", size=11, bold=True, color=HEAT))

    # підпис-висновок
    f.append(text(W/2, 312, "Під кожним вивідком — свій майданчик; поверхневий натяг стягує припій "
                  "до кожного окремо.", size=11, color=INK))
    render(os.path.join(IMG, "drag-solder.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# Фіг.3 — Якість пайки: чотири з'єднання поряд
# ─────────────────────────────────────────────────────────────────────────────
def fig_joint_quality():
    W, H = 740, 320
    f = []
    f.append(text(W/2, 28, "Чотири з'єднання: читаємо якість пайки очима", size=17, bold=True))

    panel_w = 175
    xs = [20 + i * (panel_w + 5) for i in range(4)]
    base_y = 210

    def cell(x, label, good, draw):
        col = FIELD if good else POS
        f.append(rect(x, 56, panel_w, 230, fill=BG, stroke="#d8dce0", sw=1.2, rx=8))
        f.append(text(x + panel_w / 2, 80, label, size=13, bold=True, color=col))
        # плата + майданчик
        f.append(rect(x + 20, base_y, panel_w - 40, 20, fill="#e7eaee", stroke=LINE, sw=1.2, rx=3))
        f.append(rect(x + 35, base_y - 6, panel_w - 70, 10, fill=PAD, stroke=LINE, sw=1.0, rx=2))
        draw(x + panel_w / 2)

    # 1) добра галтеля
    def d_good(cx):
        # контакт компонента
        f.append(rect(cx + 18, base_y - 40, 34, 40, fill=BODY, stroke=LINE, sw=1.2, rx=3))
        f.append(solder_blob(cx + 2, base_y - 6, 44, 30, concave=True))
        f.append(text(cx, base_y + 60, "увігнута,", size=11, color=FIELD))
        f.append(text(cx, base_y + 78, "блискуча", size=11, color=FIELD))
    cell(xs[0], "добра", True, d_good)

    # 2) холодна пайка
    def d_cold(cx):
        f.append(rect(cx + 18, base_y - 40, 34, 40, fill=BODY, stroke=LINE, sw=1.2, rx=3))
        f.append(solder_blob(cx, base_y - 8, 40, 28, concave=False))
        # «зернистість» — крапочки
        for dx, dy in [(-6, -10), (4, -6), (-2, -2), (8, -12)]:
            f.append(circle(cx + dx, base_y - 8 + dy, 1.4, fill=MUTED, stroke=MUTED, sw=0.5))
        f.append(text(cx, base_y + 60, "опукла,", size=11, color=POS))
        f.append(text(cx, base_y + 78, "зерниста", size=11, color=POS))
    cell(xs[1], "холодна", False, d_cold)

    # 3) перемичка
    def d_bridge(cx):
        # два контакти
        f.append(rect(cx - 40, base_y - 40, 24, 40, fill=BODY, stroke=LINE, sw=1.2, rx=3))
        f.append(rect(cx + 16, base_y - 40, 24, 40, fill=BODY, stroke=LINE, sw=1.2, rx=3))
        # припій залив проміжок
        f.append('<path d="M %.0f %.0f Q %.0f %.0f %.0f %.0f L %.0f %.0f Q %.0f %.0f %.0f %.0f Z" '
                 'fill="%s" stroke="%s" stroke-width="1.2"/>'
                 % (cx - 34, base_y, cx, base_y - 18, cx + 34, base_y,
                    cx + 34, base_y, cx, base_y + 2, cx - 34, base_y, SOLDER, LINE))
        f.append(text(cx, base_y + 60, "припій замкнув", size=11, color=POS))
        f.append(text(cx, base_y + 78, "два вивідки", size=11, color=POS))
    cell(xs[2], "перемичка", False, d_bridge)

    # 4) надгробок
    def d_tomb(cx):
        # деталь стоїть сторч
        f.append('<rect x="%.0f" y="%.0f" width="20" height="56" rx="3" fill="%s" stroke="%s" '
                 'stroke-width="1.2" transform="rotate(-12 %.0f %.0f)"/>'
                 % (cx - 6, base_y - 56, BODY, LINE, cx + 4, base_y - 28))
        # припій лише на одному майданчику (правому)
        f.append(solder_blob(cx + 6, base_y - 6, 30, 24, concave=True))
        # лівий контакт відірваний — порожній майданчик
        f.append(arrow(cx - 30, base_y - 30, cx - 16, base_y - 44, color=POS, sw=1.6))
        f.append(text(cx, base_y + 60, "піднявся сторч:", size=11, color=POS))
        f.append(text(cx, base_y + 78, "несиметр. прогрів", size=10, color=POS))
    cell(xs[3], "надгробок", False, d_tomb)

    render(os.path.join(IMG, "joint-quality.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# Фіг.4 — Дві нитки історії: свинець у припої та спосіб монтажу (вставка hist)
# ─────────────────────────────────────────────────────────────────────────────
def fig_leadfree_timeline():
    W, H = 760, 360
    f = []
    f.append(text(W / 2, 26, "Дві історії, що зустрічаються на столі ремонтника", size=17, bold=True))

    x0, x1 = 70, 700          # межі осей за часом
    y_top, y_bot = 110, 250   # дві паралельні лінії

    def xat(year):
        # 1945 → x0,  2010 → x1
        return x0 + (year - 1945) / (2010 - 1945) * (x1 - x0)

    # підписи ліній
    f.append(text(x0 - 8, y_top + 5, "свинець", size=12, bold=True, color=POS, anchor="end"))
    f.append(text(x0 - 8, y_bot + 5, "монтаж", size=12, bold=True, color=NEG, anchor="end"))

    # осі
    f.append(line(x0, y_top, x1, y_top, color=POS, sw=2.0))
    f.append(line(x0, y_bot, x1, y_bot, color=NEG, sw=2.0))

    # шкала років (спільна, унизу)
    for yr in (1950, 1960, 1970, 1980, 1990, 2000, 2010):
        x = xat(yr)
        f.append(line(x, y_bot, x, y_bot + 6, color=MUTED, sw=1.0))
        f.append(text(x, y_bot + 22, str(yr), size=10, color=MUTED))

    def node(x, y, color, up, head, sub):
        # точка-вузол + виноска (up=True — підпис над лінією)
        f.append(circle(x, y, 4.5, fill=BG, stroke=color, sw=2.0))
        if up:
            f.append(text(x, y - 24, head, size=11, bold=True, color=color))
            f.append(text(x, y - 10, sub, size=9, color=MUTED))
        else:
            f.append(text(x, y + 18, head, size=11, bold=True, color=color))
            f.append(text(x, y + 31, sub, size=9, color=MUTED))

    # ── верхня лінія: свинець ──
    node(xat(1948), y_top, POS, True, "вусики олова", "Bell Labs, ~1948")
    node(xat(1955), y_top, POS, False, "ліки: + свинець", "~0.5–1% Pb гасить вусики")
    node(xat(1980), y_top, POS, True, "пів століття спокою", "свинець тихо тримає надійність")
    node(xat(2006), y_top, POS, False, "RoHS забирає Pb", "вусики повертаються")

    # ── нижня лінія: спосіб монтажу ──
    node(xat(1960), y_bot, NEG, True, "планарний монтаж", "IBM, 1960")
    node(xat(1966), y_bot, NEG, False, "оплавлення в космосі", "комп'ютер Saturn (LVDC)")
    node(xat(1986), y_bot, NEG, True, "~10% збірок", "автомати pick-and-place")
    node(xat(2000), y_bot, NEG, False, "панування SMD", "кінець 1990-х")

    # точка зустрічі: 2006 на обох лініях підсвічуємо вертикаллю
    xm = xat(2006)
    f.append(line(xm, y_top, xm, y_bot, color=FIELD, sw=1.4, dash="4,4"))
    f.append(text(W / 2, 330, "Свинцевий чи безсвинцевий під жалом — вибір, у якому сходяться "
                  "обидві історії.", size=11, color=INK))
    render(os.path.join(IMG, "leadfree-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_heat_bridge()
    fig_drag_solder()
    fig_joint_quality()
    fig_leadfree_timeline()
    print("OK: 4 фігури у", IMG)
