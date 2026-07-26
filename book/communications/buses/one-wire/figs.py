# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

MASTER = POS     # ведучий тягне лінію — гарячий, червоний
SLAVE  = NEG     # ведений тягне лінію — холодний, синій
IDLE   = "#8a93a0"  # спокій: лінію тримає підтяжка


# ── топологія: один сигнальний дріт, підтяжка, ведучий + ведені ───────────────
def fig_topology():
    W, H = 720, 360
    p = []
    vdd_y, data_y, gnd_y = 74, 150, 300
    x0, x1 = 60, W - 60

    # шини живлення й землі
    p.append(line(x0, vdd_y, x1, vdd_y, color=MASTER, sw=2.2))
    p.append(text(x0 - 6, vdd_y + 4, "Vdd", size=12, color=MASTER, anchor="end", bold=True))
    p.append(line(x0, gnd_y, x1, gnd_y, color=INK, sw=2.2))
    p.append(text(x0 - 6, gnd_y + 4, "GND", size=12, color=INK, anchor="end", bold=True))

    # єдина лінія даних
    p.append(line(x0, data_y, x1, data_y, color=FIELD, sw=3.2))
    p.append(text(x1 + 4, data_y + 4, "DQ", size=12, color=FIELD, anchor="start", bold=True))
    p.append(text(W / 2, data_y - 12, "одна сигнальна жила (спільна для всіх)",
                  size=11, color=FIELD, italic=True))

    # підтяжка Vdd → лінія
    rpx = x0 + 66
    p.append(line(rpx, vdd_y, rpx, vdd_y + 18, color=MASTER, sw=2))
    p.append(rect(rpx - 8, vdd_y + 18, 16, 34, fill=BG, stroke=MASTER, sw=1.8, rx=3))
    p.append(line(rpx, vdd_y + 52, rpx, data_y, color=MASTER, sw=2))
    p.append(text(rpx + 14, vdd_y + 40, "Rp ≈ 4.7 кОм", size=10, color=MASTER, anchor="start"))
    p.append(text(rpx + 14, vdd_y + 54, "тримає лінію високою", size=9, color=MUTED, anchor="start", italic=True))

    # ведучий і ведені висять на лінії, ногами в землю
    def node(cx, top_label, bot_label, col, active_note):
        out = []
        bw, bh = 118, 66
        by = data_y + 30
        out.append(line(cx, data_y, cx, by, color=FIELD, sw=2))       # до лінії даних
        out.append(rect(cx - bw / 2, by, bw, bh, fill=FILL, stroke=col, sw=1.9))
        out.append(text(cx, by + 24, top_label, size=11.5, color=col, bold=True))
        out.append(text(cx, by + 42, bot_label, size=9.5, color=MUTED, italic=True))
        out.append(line(cx, by + bh, cx, gnd_y, color=INK, sw=2))     # до землі
        # маленький «ключ вниз» — символ відкритого стоку
        out.append(text(cx, by + 58, active_note, size=8.5, color=MUTED))
        return out

    p += node(x0 + 190, "ВЕДУЧИЙ", "мікроконтролер", MASTER, "тягне ↓ / відпускає")
    p += node(x0 + 340, "ведений", "давач температури", SLAVE, "лише тягне ↓")
    p += node(x0 + 480, "ведений", "ключ-таблетка", SLAVE, "лише тягне ↓")

    p.append(text(W / 2, H - 16,
                  "кожен пристрій уміє лише притягувати жилу до нуля (відкритий стік); "
                  "спокій = високий рівень",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "topology.svg"), W, H, *p,
           title="Шина 1-Wire: одна жила, підтяжка, ведучий і ведені")


# ── чотири мікрооперації: запис-1, запис-0, читання-1, читання-0 ───────────────
def _bit_panel(px, py, pw, title, tcol, segs, sample_frac, sample_val, note):
    """segs: список (frac, level 0/1, color). Малює цифрову хвилю в панелі."""
    out = []
    out.append(text(px + pw / 2, py + 15, title, size=12, color=tcol, bold=True))
    ax0, ax1 = px + 30, px + pw - 14
    yhi, ylo = py + 40, py + 84
    out.append(line(ax0, yhi, ax1, yhi, color="#e2e5ea", sw=1.0, dash="3 4"))
    out.append(line(ax0, ylo, ax1, ylo, color="#e2e5ea", sw=1.0))
    out.append(text(px + 22, yhi + 4, "1", size=9, color=MUTED, anchor="end"))
    out.append(text(px + 22, ylo + 4, "0", size=9, color=MUTED, anchor="end"))
    total = sum(f for f, _, _ in segs)
    x = ax0
    prev = None
    for frac, lvl, col in segs:
        w = (ax1 - ax0) * frac / total
        y = yhi if lvl else ylo
        if prev is not None and prev[0] != y:
            out.append(line(x, prev[0], x, y, color=col, sw=2.8))
        out.append(line(x, y, x + w, y, color=col, sw=2.8))
        prev = (y, col)
        x += w
    # мить вибірки
    sx = ax0 + (ax1 - ax0) * sample_frac
    out.append(line(sx, py + 32, sx, py + 92, color=FIELD, sw=1.5, dash="2 3"))
    out.append(text(sx, py + 106, "вибірка = %s" % sample_val, size=9.5, color=FIELD, bold=True))
    out.append(text(px + pw / 2, py + 124, note, size=9, color=MUTED, italic=True))
    return "".join(out)


def fig_bit_slots():
    W, H = 720, 430
    p = []
    pw = 320
    lx, rx = 30, 370
    ry1, ry2 = 56, 220

    # запис-1: ведучий коротко тягне ↓, тоді відпускає — лінія висока
    p.append(_bit_panel(lx, ry1, pw, "Запис «1»", MASTER,
                        [(0.10, 0, MASTER), (0.90, 1, IDLE)], 0.24, "1",
                        "тягне ↓ на 1–15 мкс, тоді відпускає"))
    # запис-0: ведучий тримає ↓ весь слот
    p.append(_bit_panel(rx, ry1, pw, "Запис «0»", MASTER,
                        [(0.86, 0, MASTER), (0.14, 1, IDLE)], 0.24, "0",
                        "тримає ↓ увесь слот (≥ 60 мкс)"))
    # читання-1: ведучий стартує слот, ведений відпускає
    p.append(_bit_panel(lx, ry2, pw, "Читання «1»", SLAVE,
                        [(0.10, 0, MASTER), (0.90, 1, IDLE)], 0.24, "1",
                        "ведучий стартує, ведений відпускає → росте"))
    # читання-0: ведучий стартує, ведений тримає ↓
    p.append(_bit_panel(rx, ry2, pw, "Читання «0»", SLAVE,
                        [(0.10, 0, MASTER), (0.76, 0, SLAVE), (0.14, 1, IDLE)], 0.24, "0",
                        "ведучий стартує, ведений тримає ↓"))

    # легенда
    ly = H - 24
    seg = [("ведучий тягне ↓", MASTER), ("ведений тягне ↓", SLAVE), ("підтяжка тримає ↑", IDLE)]
    lxx = 120
    for lab, col in seg:
        p.append(line(lxx, ly, lxx + 26, ly, color=col, sw=3))
        p.append(text(lxx + 32, ly + 4, lab, size=10, color=INK, anchor="start"))
        lxx += 200
    render(os.path.join(OUT, "bit-slots.svg"), W, H, *p,
           title="Один біт = один часовий слот на спільній жилі")


# ── скидання й імпульс присутності ────────────────────────────────────────────
def fig_reset_presence():
    W, H = 720, 280
    p = []
    ax0, ax1 = 70, W - 40
    yhi, ylo = 120, 186

    p.append(line(ax0, yhi, ax1, yhi, color="#e2e5ea", sw=1.0, dash="3 4"))
    p.append(line(ax0, ylo, ax1, ylo, color="#e2e5ea", sw=1.0))
    p.append(text(ax0 - 10, yhi + 4, "1", size=10, color=MUTED, anchor="end"))
    p.append(text(ax0 - 10, ylo + 4, "0", size=10, color=MUTED, anchor="end"))

    segs = [(0.06, 1, IDLE), (0.42, 0, MASTER), (0.09, 1, IDLE), (0.30, 0, SLAVE), (0.13, 1, IDLE)]
    total = sum(f for f, _, _ in segs)
    x = ax0
    prev = None
    marks = []
    for frac, lvl, col in segs:
        w = (ax1 - ax0) * frac / total
        y = yhi if lvl else ylo
        if prev is not None and prev[0] != y:
            p.append(line(x, prev[0], x, y, color=col, sw=3))
        p.append(line(x, y, x + w, y, color=col, sw=3))
        marks.append((x, x + w, lvl, col))
        prev = (y, col)
        x += w

    # підписи інтервалів
    def span(i, label, col, up=True):
        a, b, lvl, _ = marks[i]
        yy = ylo + 26
        p.append(line(a, yy, b, yy, color=col, sw=1.4))
        p.append(line(a, yy - 4, a, yy + 4, color=col, sw=1.4))
        p.append(line(b, yy - 4, b, yy + 4, color=col, sw=1.4))
        p.append(text((a + b) / 2, yy + 15, label, size=10, color=col, bold=True))

    span(1, "скидання: ведучий тягне ↓  ≥ 480 мкс", MASTER)
    p.append(text((marks[2][0] + marks[2][1]) / 2, ylo - 12, "пауза\n15–60 мкс", size=8.5, color=MUTED))
    span(3, "присутність: ведений тягне ↓  60–240 мкс", SLAVE)

    p.append(text(W / 2, H - 14,
                  "довгий низький рівень = «усім скинутись»; у відповідь пристрій сам "
                  "притискає жилу — «я тут»",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "reset-presence.svg"), W, H, *p,
           title="Скидання і присутність: перевірка «чи є хтось на шині»")


# ── паразитне живлення: чіп бере струм із тієї самої жили ──────────────────────
def _diode(x, y, col=INK, r=11):
    # трикутник вістрям униз + смужка (провідність згори вниз)
    out = ['<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s" opacity="0.85"/>'
           % (x - r, y - r, x + r, y - r, x, y + r * 0.6, col)]
    out.append(line(x - r, y + r * 0.6, x + r, y + r * 0.6, color=col, sw=2.4))
    return "".join(out)


def _cap(x, y, col=INK, w=22):
    out = [line(x - w / 2, y - 5, x + w / 2, y - 5, color=col, sw=2.6)]
    out.append(line(x - w / 2, y + 5, x + w / 2, y + 5, color=col, sw=2.6))
    return "".join(out)


def fig_parasite():
    W, H = 720, 340
    p = []
    line_y = 70
    x0, x1 = 60, W - 60
    p.append(line(x0, line_y, x1, line_y, color=FIELD, sw=3.2))
    p.append(text(x1 + 4, line_y + 4, "DQ", size=12, color=FIELD, anchor="start", bold=True))
    p.append(text(x0, line_y - 12, "лінія 1-Wire (той самий дріт, що несе дані)",
                  size=11, color=FIELD, anchor="start", italic=True))

    # ланцюг збору енергії всередині веденого
    cx = 250
    dy = line_y
    p.append(line(cx, line_y, cx, 120, color=INK, sw=2))
    p.append(_diode(cx, 132, col=MASTER))
    p.append(text(cx + 20, 134, "діод", size=10, color=MASTER, anchor="start"))
    p.append(line(cx, 143, cx, 176, color=INK, sw=2))
    p.append(_cap(cx, 182, col=NEG))
    p.append(text(cx + 22, 185, "Cpp — внутрішній", size=10, color=NEG, anchor="start"))
    p.append(text(cx + 22, 198, "конденсатор", size=10, color=NEG, anchor="start"))
    p.append(line(cx, 187, cx, 214, color=INK, sw=2))
    p.append(line(cx - 26, 214, cx + 26, 214, color=INK, sw=2.4))  # земля
    p.append(text(cx, 230, "GND", size=9.5, color=MUTED))

    # відгалуження на ядро
    p.append(line(cx, 160, cx + 120, 160, color=INK, sw=2))
    b, bw, bh = cx + 120, 150, 44
    p.append(rect(b, 160 - bh / 2, bw, bh, fill=FILL, stroke=INK, sw=1.8))
    p.append(text(b + bw / 2, 156, "ядро чіпа", size=11, color=INK, bold=True))
    p.append(text(b + bw / 2, 172, "живлення звідси", size=9, color=MUTED, italic=True))

    # дві фази
    p.append(text(x0, 268, "лінія ВИСОКА  →  діод відкритий  →  Cpp заряджається",
                  size=11, color=MASTER, anchor="start", bold=True))
    p.append(text(x0, 288, "лінія НИЗЬКА  →  діод закритий  →  чіп живиться із Cpp",
                  size=11, color=NEG, anchor="start", bold=True))
    p.append(text(x0, 314, "для «голодних» операцій (конверсія, запис EEPROM) ведучий "
                  "на час вмикає сильну підтяжку — ключ Vdd→лінія",
                  size=10, color=MUTED, anchor="start", italic=True))
    render(os.path.join(OUT, "parasite-power.svg"), W, H, *p,
           title="Паразитне живлення: струм із сигнальної жили")


# ── 64-бітний ROM: код родини + серійний номер + CRC ──────────────────────────
def fig_rom64():
    W, H = 720, 250
    p = []
    x0, x1 = 60, W - 60
    y, h = 90, 60
    total = 64.0
    parts = [
        ("код родини", "8 біт", 8, FIELD, "що це за пристрій"),
        ("серійний номер", "48 біт", 48, FILL, "який саме екземпляр"),
        ("CRC-8", "8 біт", 8, "#f6d9d4", "перевірка читання"),
    ]
    x = x0
    for name, bits, w, fill, note in parts:
        ww = (x1 - x0) * w / total
        stroke = MASTER if name == "CRC-8" else (FIELD if "родини" in name else INK)
        p.append(rect(x, y, ww, h, fill=fill, stroke=stroke, sw=1.9, rx=4))
        p.append(text(x + ww / 2, y + 26, name, size=11.5, color=INK, bold=True))
        p.append(text(x + ww / 2, y + 44, bits, size=10, color=MUTED))
        p.append(text(x + ww / 2, y + h + 18, note, size=9.5, color=stroke, italic=True))
        x += ww

    # напрямок передавання
    p.append(text(x0, y - 18, "молодший байт — перший на дроті", size=10, color=MUTED, anchor="start", italic=True))
    p.append(arrow(x0, y - 6, x0 + 120, y - 6, color=MUTED, sw=1.6))

    p.append(text(W / 2, H - 40,
                  "48 біт серійного → 2⁴⁸ ≈ 2.8·10¹⁴ унікальних номерів на кожну родину",
                  size=11, color=INK, italic=True))
    p.append(text(W / 2, H - 20,
                  "адресу не налаштовують — вона випалена лазером на заводі, "
                  "глобально унікальна",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "rom64.svg"), W, H, *p,
           title="64-бітний ROM: заводська адреса кожного пристрою")


# ── (hist) сталева «таблетка» iButton: дві провідні поверхні ───────────────────
def fig_ibutton_can():
    W, H = 720, 380
    p = []
    p.append(text(360, 52, "iButton — сталева капсула MicroCan, ≈ 16 мм, як батарейка-таблетка",
                  size=11, color=MUTED, italic=True))

    # капсула збоку: кришка (дані) — кільце (ізолятор) — корпус (земля)
    LID  = "#fdecea"; GROM = "#eafaf0"; STEEL = "#eef1f4"
    p.append(rect(110, 86, 190, 32, fill=LID,   stroke=MASTER, sw=2.2, rx=9))   # кришка
    p.append(rect(116, 118, 178, 9, fill=GROM,  stroke=FIELD,  sw=1.6, rx=2))   # ізокільце
    p.append(rect(110, 127, 190, 96, fill=STEEL, stroke=INK,   sw=2.2, rx=9))   # корпус+дно
    p.append(text(205, 107, "кришка = DQ", size=11, color=MASTER, bold=True))
    p.append(mtext(205, 168, ["корпус і дно", "= земля (GND)"], size=10.5, color=INK, bold=True))

    # виноски праворуч
    def lead(y, s, col):
        p.append(line(300, y, 330, y, color=col, sw=1.3))
        p.append(text(336, y + 4, s, size=10, color=col, anchor="start"))
    lead(102, "кришка — єдиний контакт даних (DQ)", MASTER)
    lead(122, "поліпропіленове кільце — ізолятор", FIELD)
    lead(175, "сталевий корпус і дно — спільна земля (GND)", INK)

    # підсумок
    p.append(text(360, 300, "Дві металеві поверхні — і все.", size=13, color=INK, bold=True))
    p.append(text(360, 322,
                  "Один сигнальний контакт + земля: ні штирів, ні роз'єму, ні полярності — "
                  "торкнувся й прочитав.",
                  size=11, color=MUTED, italic=True))
    p.append(text(360, 348, "Мінімум контактів — найдешевший і найнадійніший дотик.",
                  size=10.5, color=FIELD, italic=True))
    render(os.path.join(OUT, "ibutton-can.svg"), W, H, *p,
           title="iButton: носій даних на двох поверхнях")


# ── (hist) родовід: Dallas → Maxim → Analog Devices ───────────────────────────
def fig_onewire_timeline():
    W, H = 820, 300
    p = []
    axy, x0, x1 = 158, 95, 725
    p.append(line(60, axy, 760, axy, color=INK, sw=2.2))
    p.append(text(410, 50,
                  "Одна ідея пережила дві зміни власника: марка «1-Wire» тепер належить "
                  "Maxim / Analog Devices",
                  size=11, color=MUTED, italic=True))

    DAL, MAX, ADI = NEG, MASTER, FIELD
    miles = [
        (["1984", "Dallas Semiconductor", "засновано · Даллас, Техас"], DAL, +1),
        (["1989", "перші сталеві 1-Wire-", "«таблетки»: Touch Memory"], DAL, -1),
        (["1994", "«1-Wire» —", "торгова марка"], DAL, +1),
        (["1996", "«iButton» —", "торгова марка"], DAL, -1),
        (["1998", "Java Ring", "на JavaOne"], DAL, +1),
        (["2001", "Maxim Integrated", "купує Dallas ($2.5 млрд)"], MAX, -1),
        (["2021", "Analog Devices", "купує Maxim ($28 млрд)"], ADI, +1),
    ]
    n = len(miles)
    for i, (lines, col, side) in enumerate(miles):
        x = x0 + (x1 - x0) * i / (n - 1)
        p.append(circle(x, axy, 6, fill=col, stroke=col, sw=1.5))
        cy = axy - 70 if side > 0 else axy + 70
        frag, w, h = textbox(x, cy, "\n".join(lines), size=10, pad=7,
                             fill=BG, stroke=col, sw=1.6, color=INK)
        if side > 0:
            p.append(line(x, axy - 6, x, cy + h / 2, color=col, sw=1.4))
        else:
            p.append(line(x, axy + 6, x, cy - h / 2, color=col, sw=1.4))
        p.append(frag)

    render(os.path.join(OUT, "onewire-timeline.svg"), W, H, *p,
           title="Родовід 1-Wire: від сталевої «таблетки» Dallas до Analog Devices")


# ── (proj) два читання на кожен біт: пряме + інверсне → таблиця розв'язків ──────
def fig_search_reads():
    W, H = 760, 336
    p = []
    p.append(text(W / 2, 50,
                  "на кожен біт ведучий робить ДВА читання — прямий біт і його інверсію;",
                  size=11, color=MUTED, italic=True))
    p.append(text(W / 2, 66,
                  "відкритий стік дає монтажне І: лінія = 0, якщо хоч один ведений притиснув",
                  size=11, color=MUTED, italic=True))

    # координати колонок
    cx1, w1 = 40, 92
    cx2, w2 = 132, 96
    cx3, w3 = 228, 252
    cx4, w4 = 480, 240
    hy, hh = 84, 34
    ry0, rh = 122, 46

    def cell(x, w, y, h, s, fill=BG, stroke="#d6dae0", color=INK, bold=False, size=12):
        out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.3, rx=4)
        out += text(x + w / 2, y + h / 2 + size * 0.35, s, size=size, color=color, bold=bold)
        return out

    # шапка
    p.append(cell(cx1, w1, hy, hh, "пряме", fill="#eef1f4", bold=True, size=11.5))
    p.append(cell(cx2, w2, hy, hh, "інверсне", fill="#eef1f4", bold=True, size=11.5))
    p.append(cell(cx3, w3, hy, hh, "що на шині", fill="#eef1f4", bold=True, size=11.5))
    p.append(cell(cx4, w4, hy, hh, "дія ведучого", fill="#eef1f4", bold=True, size=11.5))

    rows = [
        ("0", "1", "усі ведені мають тут 0", "гілка 0 — визначено", BG, INK),
        ("1", "0", "усі ведені мають тут 1", "гілка 1 — визначено", BG, INK),
        ("0", "0", "є і 0, і 1 — РОЗВИЛКА", "обрати гілку, другу — на потім", "#eafaf0", FIELD),
        ("1", "1", "ніхто не відповів", "порожня шина або збій", "#fdecea", POS),
    ]
    for i, (a, b, c, d, fill, acc) in enumerate(rows):
        y = ry0 + i * rh
        p.append(cell(cx1, w1, y, rh, a, fill=fill, color=NEG if a == "0" else POS, bold=True, size=15))
        p.append(cell(cx2, w2, y, rh, b, fill=fill, color=NEG if b == "0" else POS, bold=True, size=15))
        p.append(cell(cx3, w3, y, rh, c, fill=fill, color=INK, bold=(i >= 2)))
        p.append(cell(cx4, w4, y, rh, d, fill=fill, color=acc, bold=(i >= 2)))

    p.append(text(W / 2, H - 16,
                  "розвилку (0,0) видно тому, що один ведений відпускає жилу, а інший притискає — "
                  "виходить 0 в обох читаннях",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "search-reads.svg"), W, H, *p,
           title="Search ROM: два читання на біт розрізняють згоду й розвилку")


# ── (proj) обхід дерева адрес: розвилки, вибір гілки, повернення за LastDiscrepancy ─
def _diamond(cx, cy, r, fill, stroke, sw=1.7):
    return ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f z" '
            'fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (cx, cy - r, cx + r, cy, cx, cy + r, cx - r, cy, fill, stroke, sw))


def _darrow(x1, y1, x2, y2, color=MUTED, sw=1.5):
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f" '
            'stroke-dasharray="4 4" marker-end="url(#arrow)"/>' % (x1, y1, x2, y2, color, sw))


def _badge(cx, cy, n, col):
    return (circle(cx, cy, 11, fill=col, stroke=col, sw=1) +
            text(cx, cy + 4.5, str(n), size=12, color="#ffffff", bold=True))


def fig_search_tree():
    W, H = 760, 486
    p = []
    P1, P2, P3 = NEG, POS, "#8e44ad"   # кольори трьох проходів

    R  = (300, 96)     # розвилка на біті 1
    F2 = (486, 208)    # розвилка на біті 2
    D3 = (138, 300)    # лист, знайдений проходом 1
    D1 = (398, 348)    # лист, знайдений проходом 2
    D2 = (612, 348)    # лист, знайдений проходом 3

    # ребра дерева (лише досяжні гілки)
    p.append(line(R[0], R[1] + 11, D3[0] + 4, D3[1] - 24, color=INK, sw=1.8))
    p.append(line(R[0], R[1] + 11, F2[0], F2[1] - 11, color=INK, sw=1.8))
    p.append(line(F2[0], F2[1] + 11, D1[0], D1[1] - 24, color=INK, sw=1.8))
    p.append(line(F2[0], F2[1] + 11, D2[0], D2[1] - 24, color=INK, sw=1.8))

    # мітки гілок 0/1 (з відступом від лінії)
    p.append(text(202, 196, "0", size=13, color=INK, bold=True))
    p.append(text(402, 150, "1", size=13, color=INK, bold=True))
    p.append(text(420, 292, "0", size=13, color=INK, bold=True))
    p.append(text(560, 292, "1", size=13, color=INK, bold=True))

    # пунктирні повернення до розвилок
    p.append(_darrow(D3[0] + 10, D3[1] - 26, R[0] - 14, R[1] + 6))
    p.append(_darrow(D1[0] + 8, D1[1] - 26, F2[0] - 12, F2[1] + 8))

    # вузли-розвилки: зелений ромб
    p.append(_diamond(R[0], R[1], 12, "#eafaf0", FIELD))
    p.append(_diamond(F2[0], F2[1], 12, "#eafaf0", FIELD))
    p.append(text(R[0], R[1] - 22, "розвилка (біт 1)", size=10, color=FIELD, bold=True))
    p.append(text(F2[0] + 78, F2[1] + 4, "розвилка (біт 2)", size=10, color=FIELD, bold=True))

    # листи-пристрої
    def leaf(center, label, col, n):
        cx, cy = center
        bw, bh = 116, 40
        p.append(rect(cx - bw / 2, cy - bh / 2, bw, bh, fill=BG, stroke=col, sw=2, rx=6))
        p.append(text(cx, cy + 5, label, size=13, color=INK, bold=True))
        p.append(_badge(cx - bw / 2, cy - bh / 2, n, col))

    leaf(D3, "D3 = …011", P1, 1)
    leaf(D1, "D1 = …100", P2, 2)
    leaf(D2, "D2 = …110", P3, 3)

    # примітки про три проходи
    ny = 396
    p.append(text(40, ny, "Прохід 1 → D3: на розвилці біта 1 обрано 0; гілка 1 лишилась → LastDiscrepancy = 1.",
                  size=10.5, color=P1, anchor="start"))
    p.append(text(40, ny + 20, "Прохід 2 → D1: вертаємось на гілку 1, там нова розвилка (біт 2), обрано 0 → LastDiscrepancy = 2.",
                  size=10.5, color=P2, anchor="start"))
    p.append(text(40, ny + 40, "Прохід 3 → D2: гілка 1 біта 2; розвилок більше нема → останній пристрій, кінець.",
                  size=10.5, color=P3, anchor="start"))
    p.append(text(40, ny + 62,
                  "① ② ③ — порядок відкриття · зелений ромб — розвилка (0,0) · пунктир — повернення до останньої розвилки",
                  size=9.5, color=MUTED, anchor="start", italic=True))

    render(os.path.join(OUT, "search-tree.svg"), W, H, *p,
           title="Пошук ROM = обхід дерева адрес із однією закладкою")


# ── (proj) дві дії над ніжкою: притиснути (вихід-0) vs відпустити (вхід-Z) ─────
def fig_bitbang_pin_states():
    W, H = 780, 384
    p = []
    p.append(text(W / 2, 52,
                  "Ніжку не «ставлять у 1» — перемикають лише її НАПРЯМ (DDR); "
                  "біт даних (PORT) завжди 0",
                  size=11, color=MUTED, italic=True))

    def panel(px, title, tcol, drive, reg, level_txt, level_col):
        out = []
        pw = 350
        out.append(rect(px, 74, pw, 244, fill=BG, stroke="#e2e5ea", sw=1.4, rx=8))
        out.append(text(px + pw / 2, 98, title, size=12.5, color=tcol, bold=True))

        vdd_x = px + pw - 62
        vdd_y = 118
        line_y = 170
        gnd_y = 268
        pin_x = px + 96
        c_top, c_bot = 200, 234

        # зовнішня підтяжка Rp (на шині, не в МК)
        out.append(text(vdd_x, vdd_y - 8, "Vdd", size=10, color=IDLE, bold=True))
        out.append(line(vdd_x, vdd_y, vdd_x, vdd_y + 14, color=IDLE, sw=1.8))
        out.append(rect(vdd_x - 7, vdd_y + 14, 14, 26, fill=BG, stroke=IDLE, sw=1.6, rx=2))
        out.append(text(vdd_x + 13, vdd_y + 31, "Rp", size=9, color=IDLE, anchor="start"))
        out.append(line(vdd_x, vdd_y + 40, vdd_x, line_y, color=IDLE, sw=1.8))

        # лінія DQ
        out.append(line(pin_x, line_y, vdd_x, line_y, color=level_col, sw=3))
        out.append(text(vdd_x + 5, line_y - 8, "DQ", size=10, color=FIELD, anchor="start", bold=True))
        out.append(text((pin_x + vdd_x) / 2, line_y - 11, level_txt, size=11, color=level_col, bold=True))

        # ніжка МК: дріт від DQ через ключ-драйвер до землі
        out.append(text(pin_x - 12, line_y - 10, "ніжка", size=9, color=MUTED, anchor="end"))
        out.append(line(pin_x, line_y, pin_x, c_top, color=INK, sw=2))
        out.append(circle(pin_x, c_top, 3, fill=BG, stroke=INK, sw=1.4))
        out.append(circle(pin_x, c_bot, 3, fill=BG, stroke=INK, sw=1.4))
        out.append(line(pin_x, c_bot, pin_x, gnd_y, color=INK, sw=2))
        # ключ (вихідний транзистор ніжки) між контактами
        if drive:
            out.append(line(pin_x, c_top, pin_x, c_bot, color=level_col, sw=3.4))
            out.append(text(pin_x + 22, 213, "ЗАМКНЕНО", size=9.5, color=level_col, anchor="start", bold=True))
            out.append(text(pin_x + 22, 229, "ніжка жене 0", size=9, color=MUTED, anchor="start"))
        else:
            out.append(line(pin_x, c_top, pin_x + 22, c_top - 12, color=MUTED, sw=3.4))
            out.append(text(pin_x + 22, 213, "РОЗІМКНЕНО", size=9.5, color=MUTED, anchor="start", bold=True))
            out.append(text(pin_x + 22, 229, "ніжка hi-Z", size=9, color=MUTED, anchor="start"))
        # символ землі
        out.append(line(pin_x - 12, gnd_y, pin_x + 12, gnd_y, color=INK, sw=2.4))
        out.append(line(pin_x - 7, gnd_y + 4, pin_x + 7, gnd_y + 4, color=INK, sw=2))
        out.append(line(pin_x - 3, gnd_y + 8, pin_x + 3, gnd_y + 8, color=INK, sw=2))
        out.append(text(pin_x, gnd_y + 22, "GND", size=9, color=MUTED))

        out.append(text(px + pw / 2, 306, reg, size=11, color=tcol, bold=True))
        return out

    p += panel(22, "притиснути   ow_drive_low()", MASTER, True,
               "DDRD |= OW_BIT   (вихід жене 0)", "лінія = 0 (LOW)", MASTER)
    p += panel(408, "відпустити   ow_release()", IDLE, False,
               "DDRD &= ~OW_BIT   (вхід, hi-Z)", "лінія = 1 (тягне Rp)", IDLE)

    p.append(text(W / 2, 352,
                  "PORTD-біт лишається 0 назавжди → внутрішню підтяжку вимкнено, «1» на лінію "
                  "не подаємо; високий рівень дає лише зовнішній Rp",
                  size=10.5, color=INK, italic=True))
    render(os.path.join(OUT, "bitbang-pin-states.svg"), W, H, *p,
           title="Відкритий стік на звичайній ніжці: вихід-0 або вхід-Z")


# ── (proj) чому cli(): переривання розтягує провал і перевертає біт ────────────
def fig_bitbang_irq_stretch():
    W, H = 780, 372
    p = []
    p.append(text(W / 2, 52,
                  "Запис «1» — це провал лише 6 мкс. Переривання посеред нього розтягує "
                  "провал, і ведений читає «0»",
                  size=11, color=MUTED, italic=True))

    def wave(y0, title, tcol, low_end, sample, isr, read_val, read_col):
        out = []
        ax0, ax1 = 172, W - 140
        yhi, ylo = y0, y0 + 44
        out.append(mtext(58, y0 + 14, title, size=11, color=tcol, bold=True, anchor="start"))
        out.append(line(ax0, yhi, ax1, yhi, color="#e2e5ea", sw=1.0, dash="3 4"))
        out.append(line(ax0, ylo, ax1, ylo, color="#e2e5ea", sw=1.0))
        out.append(text(ax0 - 10, yhi + 4, "1", size=9, color=MUTED, anchor="end"))
        out.append(text(ax0 - 10, ylo + 4, "0", size=9, color=MUTED, anchor="end"))
        xle = ax0 + (ax1 - ax0) * low_end
        out.append(line(ax0, yhi, ax0, ylo, color=MASTER, sw=2.8))
        out.append(line(ax0, ylo, xle, ylo, color=MASTER, sw=2.8))
        out.append(line(xle, ylo, xle, yhi, color=IDLE, sw=2.8))
        out.append(line(xle, yhi, ax1, yhi, color=IDLE, sw=2.8))
        # мить вибірки веденим
        sx = ax0 + (ax1 - ax0) * sample
        out.append(line(sx, yhi - 10, sx, ylo + 10, color=SLAVE, sw=1.6, dash="2 3"))
        out.append(text(sx, yhi - 15, "вибірка веденим", size=9, color=SLAVE, bold=True))
        # ISR-хатч
        if isr:
            ia = ax0 + (ax1 - ax0) * isr[0]
            ib = ax0 + (ax1 - ax0) * isr[1]
            out.append(rect(ia, yhi - 2, ib - ia, ylo - yhi + 4, fill="#fff3cd", stroke="#d39e00", sw=1.2, rx=3))
            out.append(text((ia + ib) / 2, ylo + 22, "ISR — CPU зайнятий, провал росте", size=9, color="#9a7400", bold=True))
        out.append(text(ax1 + 12, ylo - 8, "→ «%s»" % read_val, size=15, color=read_col, anchor="start", bold=True))
        return out

    p += wave(112, ["з cli():", "нас не спинити"], FIELD,
              low_end=0.10, sample=0.46, isr=None, read_val="1", read_col=FIELD)
    p += wave(250, ["без cli():", "ISR влітає"], MASTER,
              low_end=0.56, sample=0.46, isr=(0.10, 0.54), read_val="0", read_col=MASTER)

    render(os.path.join(OUT, "bitbang-irq-stretch.svg"), W, H, *p,
           title="Навіщо на слоті гасять переривання")


# ── (api) пінаут і два способи живлення: зовнішнє vs паразитне ─────────────────
def _res_v(x, y0, y1, col, label, lx_off=13):
    """Вертикальний резистор між y0 (згори) і y1 (знизу) з підписом праворуч."""
    out = [line(x, y0, x, y0 + 12, color=col, sw=1.9)]
    out.append(rect(x - 8, y0 + 12, 16, 30, fill=BG, stroke=col, sw=1.7, rx=3))
    out.append(line(x, y0 + 42, x, y1, color=col, sw=1.9))
    out.append(text(x + lx_off, y0 + 31, label, size=10, color=col, anchor="start"))
    return "".join(out)


def _wiring_panel(px, py, pw, title, tcol, parasite):
    out = []
    ph = 288
    out.append(rect(px, py, pw, ph, fill=BG, stroke="#e2e5ea", sw=1.4, rx=8))
    out.append(text(px + pw / 2, py + 26, title, size=13, color=tcol, bold=True))

    vdd_y = py + 62
    gnd_y = py + 232
    dq_y  = py + 150
    railx0, railx1 = px + 30, px + pw - 26

    # шини Vdd і GND
    out.append(line(railx0, vdd_y, railx1, vdd_y, color=POS, sw=2.4))
    out.append(text(railx0 - 6, vdd_y + 4, "Vdd", size=11, color=POS, anchor="end", bold=True))
    out.append(text(railx1, vdd_y - 9, "3.0–5.5 В", size=9, color=MUTED, anchor="end", italic=True))
    out.append(line(railx0, gnd_y, railx1, gnd_y, color=INK, sw=2.4))
    out.append(text(railx0 - 6, gnd_y + 4, "GND", size=11, color=INK, anchor="end", bold=True))

    # ведучий
    mx, mw, mh = px + 36, 72, 62
    out.append(rect(mx, dq_y - mh / 2, mw, mh, fill=FILL, stroke=tcol, sw=1.8, rx=6))
    out.append(text(mx + mw / 2, dq_y - 2, "ведучий", size=10.5, color=tcol, bold=True))
    out.append(text(mx + mw / 2, dq_y + 14, "µC", size=10, color=MUTED))

    # пристрій із трьома ногами на лівому боці
    devw, devh = 96, 118
    devx = px + pw - devw - 26
    devy = dq_y - devh / 2
    out.append(rect(devx, devy, devw, devh, fill=FILL, stroke=SLAVE, sw=1.9, rx=6))
    out.append(text(devx + devw / 2, devy + devh / 2 - 5, "ведений", size=10.5, color=SLAVE, bold=True))
    p_vdd, p_dq, p_gnd = devy + 24, dq_y, devy + devh - 24
    for yy, lab in ((p_vdd, "VDD"), (p_dq, "DQ"), (p_gnd, "GND")):
        out.append(text(devx + 7, yy + 3, lab, size=9, color=MUTED, anchor="start"))

    # лінія DQ: ведучий ↔ нога DQ пристрою
    out.append(line(mx + mw, dq_y, devx, p_dq, color=FIELD, sw=3))
    out.append(text(mx + mw + 6, dq_y - 8, "DQ", size=9.5, color=FIELD, anchor="start", bold=True))

    # підтяжка Rp: Vdd → лінія DQ (підпис ліворуч від резистора)
    rpx = px + pw * 0.40
    out.append(line(rpx, vdd_y, rpx, vdd_y + 12, color=POS, sw=1.9))
    out.append(rect(rpx - 8, vdd_y + 12, 16, 30, fill=BG, stroke=POS, sw=1.7, rx=3))
    out.append(line(rpx, vdd_y + 42, rpx, dq_y, color=POS, sw=1.9))
    out.append(text(rpx - 13, vdd_y + 20, "Rp", size=9.5, color=POS, anchor="end", bold=True))
    out.append(text(rpx - 13, vdd_y + 33, "4.7к", size=9, color=POS, anchor="end"))

    # нога GND пристрою → шина GND (наліво від коробки, тоді вниз)
    out.append(line(devx, p_gnd, devx - 20, p_gnd, color=INK, sw=1.9))
    out.append(line(devx - 20, p_gnd, devx - 20, gnd_y, color=INK, sw=1.9))

    if parasite:
        # VDD замкнено на землю — струм краде з лінії DQ
        out.append(line(devx, p_vdd, devx - 40, p_vdd, color=NEG, sw=1.9))
        out.append(line(devx - 40, p_vdd, devx - 40, gnd_y, color=NEG, sw=1.9))
        out.append(text(devx - 44, p_vdd - 7, "VDD→GND", size=9, color=NEG, anchor="end", bold=True))
        note = "два дроти (DQ + GND): VDD замкнено на землю, струм — із жили"
    else:
        # VDD → шина Vdd (окреме живлення)
        out.append(line(devx, p_vdd, devx - 40, p_vdd, color=POS, sw=1.9))
        out.append(line(devx - 40, p_vdd, devx - 40, vdd_y, color=POS, sw=1.9))
        note = "три дроти (DQ + GND + VDD): живлення окремою жилою"
    out.append(text(px + pw / 2, py + ph - 14, note, size=9.5, color=MUTED, italic=True))
    return out


def fig_wiring():
    W, H = 780, 388
    p = []
    p.append(text(W / 2, 38,
                  "Той самий пристрій, два підключення: живити VDD окремо або красти струм із лінії",
                  size=11, color=MUTED, italic=True))
    p += _wiring_panel(20, 62, 360, "Зовнішнє живлення", FIELD, parasite=False)
    p += _wiring_panel(400, 62, 360, "Паразитне живлення", POS, parasite=True)
    render(os.path.join(OUT, "wiring.svg"), W, H, *p,
           title="Пінаут 1-Wire і два способи живлення пристрою")


if __name__ == "__main__":
    fig_wiring()
    fig_topology()
    fig_bit_slots()
    fig_reset_presence()
    fig_parasite()
    fig_rom64()
    fig_ibutton_can()
    fig_onewire_timeline()
    fig_search_reads()
    fig_search_tree()
    fig_bitbang_pin_states()
    fig_bitbang_irq_stretch()
    print("OK: figures written to", OUT)
