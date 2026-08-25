# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

HOT  = "#c0392b"
WARM = "#e67e22"
COOL = "#2457d6"
GREY = "#d8dee5"


# ── 1. Паяння гріє всю комірку — зварювання лише точку ──────────────────────
def fig_solder_vs_weld():
    W, H = 720, 360
    frags = []
    cy, ch = 105, 175

    frags.append('<defs><linearGradient id="hotcell" x1="0" y1="0" x2="0" y2="1">'
                 '<stop offset="0%%" stop-color="%s"/>'
                 '<stop offset="55%%" stop-color="%s"/>'
                 '<stop offset="100%%" stop-color="#f7ccbc"/></linearGradient></defs>' % (HOT, WARM))

    # ── ліворуч: паяння ──
    lx = 178
    frags.append(text(lx, 50, "Паяння", size=17, bold=True))
    frags.append(text(lx, 72, "секунди тепла в усій комірці", size=12, color=MUTED))
    cx, cw = lx - 45, 90
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="10" '
                 'fill="url(#hotcell)" stroke="%s" stroke-width="1.5"/>' % (cx, cy, cw, ch, LINE))
    frags.append(rect(cx + 28, cy - 12, 34, 12, fill=GREY, stroke=LINE, sw=1.2, rx=3))
    frags.append(circle(cx + 45, cy - 6, 9, fill="#bcbec2", stroke=LINE, sw=1.2))
    frags.append(text(lx, cy + ch + 26, "жар «пливе» всередину —", size=12, color=HOT))
    frags.append(text(lx, cy + ch + 44, "до сепаратора й електроліту", size=12, color=HOT))

    # ── роздільник ──
    frags.append(line(360, 40, 360, 320, color="#d0d4da", sw=1.2, dash="4 4"))

    # ── праворуч: зварювання ──
    rx = 545
    frags.append(text(rx, 50, "Контактне зварювання", size=17, bold=True))
    frags.append(text(rx, 72, "мілісекунда тепла — лише в точці", size=12, color=MUTED))
    cx2 = rx - 45
    frags.append(rect(cx2, cy, cw, ch, fill="#eef1f4", stroke=LINE, sw=1.5, rx=10))
    frags.append(rect(cx2 + 10, cy - 10, cw - 20, 10, fill=GREY, stroke=LINE, sw=1.2, rx=2))
    for dx in (28, 62):
        frags.append(circle(cx2 + dx, cy - 5, 5, fill=HOT, stroke=HOT, sw=1))
    frags.append(text(rx, cy + ch + 26, "решта комірки", size=12, color=COOL))
    frags.append(text(rx, cy + ch + 44, "лишається холодною", size=12, color=COOL))

    render(os.path.join(OUT, 'solder-vs-weld.svg'), W, H, *frags)


# ── 2. Де народжується тепло: шлях струму й контактний опір ─────────────────
def fig_where_heat():
    W, H = 720, 400
    frags = []
    frags.append(text(W / 2, 30, "Шлях струму: тепло — там, де опір найбільший", size=16, bold=True))

    # два електроди зверху
    ex1, ex2 = 300, 420
    ey = 70
    for ex in (ex1, ex2):
        frags.append(rect(ex - 14, ey, 28, 46, fill="#b5651d", stroke=LINE, sw=1.4, rx=4))
    frags.append(text((ex1 + ex2) / 2, ey - 8, "два електроди поруч", size=12, color=MUTED))

    # стрічка
    sy = 130
    frags.append(rect(230, sy, 260, 16, fill=GREY, stroke=LINE, sw=1.5, rx=3))
    frags.append(text(500, sy + 12, "нікелева стрічка", size=12, color=MUTED, anchor="start"))

    # верх комірки (банка)
    ty = 170
    frags.append(rect(210, ty, 300, 120, fill="#eef1f4", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(360, ty + 108, "корпус комірки", size=12, color=MUTED))

    # гарячі точки на межі стрічка↔банка
    for ex in (ex1, ex2):
        frags.append(circle(ex, sy + 16, 7, fill=HOT, stroke=HOT, sw=1))

    # шлях струму: вниз лівим електродом, уздовж межі, вгору правим
    frags.append(arrow(ex1, ey + 46, ex1, sy, color=COOL, sw=2.4))
    frags.append(arrow(ex1, sy + 20, ex1, ty + 4, color=COOL, sw=2.4))
    frags.append(line(ex1, ty + 8, ex2, ty + 8, color=COOL, sw=2.4))
    frags.append(arrow(ex2, ty + 4, ex2, sy + 20, color=COOL, sw=2.4))
    frags.append(arrow(ex2, sy, ex2, ey + 46, color=COOL, sw=2.4))

    # підпис до гарячих точок
    b, bw, bh = textbox(150, sy + 20, "тут опір\nнайбільший →\nтут і плавить",
                        size=12, color=HOT, stroke=HOT, fill="#fdecea", pad=8)
    frags.append(b)

    # чому два поруч (а не наскрізь)
    b2, _, _ = textbox(W / 2, 335,
                       "Обидва електроди — з ОДНОГО боку. Струм не йде наскрізь крізь комірку,\n"
                       "а «пірнає» у корпус під першим і виходить під другим. Комірка не в колі.",
                       size=12, pad=10, min_w=560)
    frags.append(b2)

    render(os.path.join(OUT, 'where-heat.svg'), W, H, *frags)


# ── 3. Профіль струму: кволий і робочий імпульс ─────────────────────────────
def fig_pulse_profile():
    W, H = 720, 340
    frags = []
    frags.append(text(W / 2, 30, "Два імпульси: спершу пробити, тоді зварити", size=16, bold=True))

    ox, oy = 90, 250          # початок осей
    axw, axh = 560, 180
    frags.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.6))       # час →
    frags.append(arrow(ox, oy, ox, oy - axh - 6, color=INK, sw=1.6))   # струм ↑
    frags.append(text(ox + axw, oy + 24, "час (мс)", size=12, color=MUTED))
    frags.append(text(ox - 10, oy - axh - 12, "струм", size=12, color=MUTED, anchor="middle"))

    def pulse(x0, w, h, color, label):
        out = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
               'fill="%s" fill-opacity="0.25" stroke="%s" stroke-width="2" rx="2"/>'
               % (x0, oy - h, w, h, color, color))
        out += text(x0 + w / 2, oy - h - 8, label, size=12, color=color, bold=True)
        return out

    # кволий перший імпульс (пробити оксид, зім'яти контакт)
    frags.append(pulse(ox + 30, 55, 55, WARM, "пробити"))
    # пауза
    frags.append(text(ox + 30 + 55 + 32, oy + 22, "пауза", size=11, color=MUTED))
    # робочий другий імпульс (сплавити ядро)
    frags.append(pulse(ox + 30 + 55 + 64, 90, 150, HOT, "зварити"))

    # рівень «сотні ампер»
    frags.append(line(ox, oy - 150, ox + axw - 20, oy - 150, color=MUTED, sw=1, dash="3 4"))
    frags.append(text(ox + axw - 18, oy - 150, "сотні А", size=11, color=MUTED, anchor="start"))

    # пояснення
    b, _, _ = textbox(W / 2, 305,
                      "Q = I² · R · t.  Струм у квадраті — тож короткий сильний імпульс кладе "
                      "тепло\nу точку швидше, ніж встигає розтектися вглиб комірки.",
                      size=12, pad=10, min_w=560)
    frags.append(b)

    render(os.path.join(OUT, 'pulse-profile.svg'), W, H, *frags)


# ── 4. Випадок Томсона: розряд банки сплавив стик котушки ────────────────────
def fig_thomson_accident():
    W, H = 720, 380
    frags = []
    frags.append(text(W / 2, 30, "Випадок, з якого народилося зварювання опором", size=16, bold=True))

    # лейденська банка (конденсатор)
    jx, jy = 95, 120
    frags.append(rect(jx, jy, 60, 120, fill="#eef1f4", stroke=LINE, sw=1.6, rx=8))
    frags.append(rect(jx + 22, jy - 22, 16, 24, fill=GREY, stroke=LINE, sw=1.4, rx=2))
    frags.append(text(jx + 30, jy + 70, "лейден-", size=12, color=MUTED))
    frags.append(text(jx + 30, jy + 88, "ська", size=12, color=MUTED))
    frags.append(text(jx + 30, jy + 106, "банка", size=12, color=MUTED))
    frags.append(text(jx + 30, jy + 148, "заряд →", size=11, color=COOL))

    # котушка: тонка обмотка (первинка від банки), груба (з розривом-стиком)
    coilx = 300
    coily = 130
    frags.append(rect(coilx, coily, 150, 90, fill="#f7f3ea", stroke=LINE, sw=1.6, rx=8))
    # витки тонкі
    for i in range(6):
        yy = coily + 14 + i * 12
        frags.append(line(coilx + 16, yy, coilx + 134, yy, color=WARM, sw=1.4))
    frags.append(text(coilx + 75, coily - 10, "тонка обмотка", size=12, color=WARM))
    frags.append(text(coilx + 75, coily + 108, "(струм від банки)", size=11, color=MUTED))

    # провід від банки до котушки
    frags.append(arrow(jx + 60, jy + 30, coilx, coily + 20, color=COOL, sw=2.2))

    # грубі кінці зі стиком праворуч
    gy = 175
    frags.append(line(coilx + 150, gy, 560, gy, color="#7a7f87", sw=5))
    frags.append(line(600, gy, 660, gy, color="#7a7f87", sw=5))
    # стик — гаряча точка
    frags.append(circle(580, gy, 12, fill=HOT, stroke=HOT, sw=1))
    frags.append(text(580, gy - 22, "стик:", size=12, color=HOT, bold=True))
    frags.append(text(580, gy + 34, "тут опір найбільший", size=12, color=HOT))
    frags.append(text(580, gy + 52, "→ увесь жар сюди → сплав", size=12, color=HOT))
    frags.append(text(505, gy - 40, "грубі кінці, що лише торкаються", size=11, color=MUTED, anchor="start"))

    # формула
    b, _, _ = textbox(W / 2, 350,
                      "Q = I² · R · t.  Струм скрізь однаковий, а опір R на нещільному стику — "
                      "найбільший.\nТому весь жар сідає туди й плавить метал. Томсон побачив у цьому спосіб.",
                      size=12, pad=10, min_w=580)
    frags.append(b)

    render(os.path.join(OUT, 'thomson-accident.svg'), W, H, *frags)


# ── 5. Перший зварювальник Томсона: понижувальний трансформатор ──────────────
def fig_thomson_machine():
    W, H = 720, 360
    frags = []
    frags.append(text(W / 2, 30, "Перший зварювальник Томсона (1885): струм із трансформатора", size=15, bold=True))

    # осердя
    corex, corey, corew, coreh = 300, 90, 90, 170
    frags.append(rect(corex, corey, corew, coreh, fill="#e9e2d0", stroke=LINE, sw=1.6, rx=4))
    frags.append(text(corex + corew / 2, corey + coreh + 18, "осердя", size=11, color=MUTED))

    # первинка — багато витків тонкого дроту (ліворуч)
    for i in range(9):
        yy = corey + 12 + i * 18
        frags.append(line(corex - 40, yy, corex + 6, yy, color=COOL, sw=1.6))
    frags.append(text(corex - 60, corey - 12, "первинка:", size=12, color=COOL, anchor="start"))
    frags.append(text(corex - 95, corey + coreh + 4, "багато витків тонкого дроту", size=11, color=COOL, anchor="start"))
    frags.append(text(corex - 95, corey + coreh + 20, "від мережі (сотні В)", size=11, color=MUTED, anchor="start"))

    # вторинка — кілька витків грубої шини (праворуч)
    for i in range(3):
        yy = corey + 40 + i * 34
        frags.append(line(corex + corew - 6, yy, corex + corew + 55, yy, color=HOT, sw=5))
    frags.append(text(corex + corew + 60, corey + 30, "вторинка:", size=12, color=HOT, anchor="start"))
    frags.append(text(corex + corew + 60, corey + 46, "кілька витків", size=11, color=MUTED, anchor="start"))
    frags.append(text(corex + corew + 60, corey + 62, "грубої шини", size=11, color=MUTED, anchor="start"))

    # губки-електроди зі стиком деталей
    ey = corey + 74
    frags.append(rect(corex + corew + 150, ey - 14, 26, 28, fill="#b5651d", stroke=LINE, sw=1.4, rx=3))
    frags.append(rect(corex + corew + 150, ey + 46, 26, 28, fill="#b5651d", stroke=LINE, sw=1.4, rx=3))
    # деталі між губками
    frags.append(rect(corex + corew + 176, ey - 6, 40, 12, fill=GREY, stroke=LINE, sw=1.3, rx=2))
    frags.append(rect(corex + corew + 176, ey + 54, 40, 12, fill=GREY, stroke=LINE, sw=1.3, rx=2))
    frags.append(circle(corex + corew + 216, ey + 30, 8, fill=HOT, stroke=HOT, sw=1))
    # шина від вторинки до губок
    frags.append(line(corex + corew + 55, corey + 40, corex + corew + 163, ey - 8, color=HOT, sw=4))
    frags.append(line(corex + corew + 55, corey + 108, corex + corew + 163, ey + 60, color=HOT, sw=4))
    frags.append(text(corex + corew + 200, ey - 26, "стик деталей", size=11, color=HOT))

    b, _, _ = textbox(W / 2, 330,
                      "Напруга падає в багато разів — струм у стільки ж разів росте: кілька вольтів, "
                      "сотні ампер.\nЦей струм гріє стик деталей власним опором і сплавляє — без полум'я, без припою.",
                      size=12, pad=10, min_w=600)
    frags.append(b)

    render(os.path.join(OUT, 'thomson-machine.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_solder_vs_weld()
    fig_where_heat()
    fig_pulse_profile()
    fig_thomson_accident()
    fig_thomson_machine()
    print("figs done")
