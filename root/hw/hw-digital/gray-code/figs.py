# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: чому звичайний двійковий код збоїть на межі, а Грей — ні ───────
def fig_straddle():
    W, H = 720, 380
    f = []
    f.append(text(W/2, 26, "Перехід через одну межу: двійковий vs Грей", size=17, bold=True))

    # дві колонки: ліворуч звичайний, праворуч Грей
    colx = [W*0.27, W*0.73]
    titles = ["Звичайний двійковий", "Код Грея"]
    # перехід 3 → 4
    pairs = [("011", "100"), ("010", "110")]
    notes = ["3 біти міняються РАЗОМ", "міняється РІВНО 1 біт"]
    note_col = [POS, FIELD]

    for c in range(2):
        cx = colx[c]
        f.append(text(cx, 62, titles[c], size=14, bold=True,
                      color=(POS if c == 0 else FIELD)))
        a, b = pairs[c]
        # три біти у клітинках, від старшого до молодшого
        cw, ch = 46, 46
        gap = 8
        total = 3*cw + 2*gap
        x0 = cx - total/2
        ytop, ybot = 92, 92 + ch + 70
        for row, val in enumerate((a, b)):
            y = ytop if row == 0 else ybot
            for i, ch_ in enumerate(val):
                x = x0 + i*(cw+gap)
                changed = (a[i] != b[i])
                fill = "#fdecea" if (changed and c == 0) else (
                       "#eafaf1" if (changed and c == 1) else FILL)
                stk = (POS if (changed and c == 0) else
                       (FIELD if (changed and c == 1) else LINE))
                f.append(rect(x, y, cw, ch, fill=fill, stroke=stk, sw=2.2 if changed else 1.4))
                f.append(text(x+cw/2, y+ch/2+7, ch_, size=22, bold=True,
                              color=(stk if changed else INK)))
        # підписи значень
        f.append(text(x0-14, ytop+ch/2+6, "3", size=15, bold=True, color=MUTED, anchor="end"))
        f.append(text(x0-14, ybot+ch/2+6, "4", size=15, bold=True, color=MUTED, anchor="end"))
        # стрілка переходу
        f.append(arrow(cx, ytop+ch+6, cx, ybot-6, color=LINE, sw=2))
        # нотатка
        f.append(fitbox(cx-total/2, ybot+ch+16, total, 34, notes[c], size=12,
                        fill="#fff", stroke=note_col[c], sw=1.6))

    # нижній підсумок-стрічка по центру
    f.append(line(W/2, 70, W/2, H-66, color="#dddddd", sw=1, dash="4 5"))
    msg = ("Перемкнулися біти не точно разом — проміжне читання двійкового дасть 7 чи 0,\n"
           "будь-яке хибне число. У Грея проміжку немає: на виході або старе, або нове.")
    f.append(fitbox(40, H-52, W-80, 40, msg, size=12, fill="#f7f7f9", stroke=MUTED, sw=1))
    render(os.path.join(IMG, 'straddle.svg'), W, H, *f)


# ── Фігура 2: відбиття — як з n-бітного коду будують (n+1)-бітний ─────────────
def fig_reflect():
    W, H = 720, 430
    f = []
    f.append(text(W/2, 26, "Побудова відбиттям: 2 біти → 3 біти", size=17, bold=True))

    g2 = ["00", "01", "11", "10"]
    # колонка 1: 2-бітний
    cw = 70
    x1 = 70
    ytop = 70
    rh = 40
    for i, v in enumerate(g2):
        y = ytop + i*rh
        f.append(rect(x1, y, cw, rh-6, fill=FILL, stroke=LINE, sw=1.4))
        f.append(text(x1+cw/2, y+rh/2, v, size=18, bold=True))
    f.append(text(x1+cw/2, ytop-12, "2 біти", size=13, bold=True, color=MUTED))

    # дзеркало: ось відбиття
    mirx = x1 + cw + 60
    ymir_top = ytop
    ymir_bot = ytop + 8*rh - 6
    f.append(line(mirx, ymir_top, mirx, ymir_bot, color=FIELD, sw=2, dash="6 5"))
    f.append(text(mirx, ymir_bot+22, "вісь відбиття", size=12, color=FIELD, bold=True))

    # колонка 2: 3-бітний = (0 + список) ⌢ (1 + список навспак)
    x2 = mirx + 60
    half = g2[:]               # верх — як є
    halfR = list(reversed(g2)) # низ — навспак
    full = [("0", v) for v in half] + [("1", v) for v in halfR]
    cw3 = 96
    for i, (pre, v) in enumerate(full):
        y = ytop + i*rh
        topblock = (i < 4)
        fill = "#eef4ff" if topblock else "#fff5ec"
        stk = NEG if topblock else POS
        f.append(rect(x2, y, cw3, rh-6, fill=fill, stroke=stk, sw=1.5))
        # префікс окремим кольором
        f.append(text(x2+18, y+rh/2, pre, size=18, bold=True, color=stk))
        f.append(text(x2+18+30, y+rh/2, v, size=18, bold=True, color=INK))
    f.append(text(x2+cw3/2, ytop-12, "3 біти", size=13, bold=True, color=MUTED))

    # дужки-пояснення праворуч
    rx = x2 + cw3 + 18
    f.append(fitbox(rx, ytop, 150, 4*rh-6, "верхня половина:\nпопереду 0,\nстарий порядок",
                    size=11.5, fill="#eef4ff", stroke=NEG, sw=1.3))
    f.append(fitbox(rx, ytop+4*rh, 150, 4*rh-6, "нижня половина:\nпопереду 1,\nпорядок НАВСПАК",
                    size=11.5, fill="#fff5ec", stroke=POS, sw=1.3))

    # підсумок
    f.append(fitbox(40, H-52, W-80, 40,
                    "Дзеркало робить шов на стику половин безпечним: сусіди 011 і 111\n"
                    "різняться лише префіксом. Воно ж склеює кінець із початком у кільце.",
                    size=12, fill="#f7f7f9", stroke=MUTED, sw=1))
    render(os.path.join(IMG, 'reflect.svg'), W, H, *f)


# ── Фігура 3: 3-бітний кодувальний диск (кільце з одиничними переходами) ──────
def fig_disk():
    import math
    W, H = 560, 460
    f = []
    f.append(text(W/2, 26, "Кодувальний диск: 3 доріжки, на межі — 1 біт", size=16, bold=True))

    cx, cy = W/2, 250
    rings = [(118, 150), (86, 118), (54, 86)]  # (r_in, r_out) для бітів b2,b1,b0
    seq = ["000", "001", "011", "010", "110", "111", "101", "100"]
    n = len(seq)
    # колір сектора за бітом: 1 = темний, 0 = світлий
    dark = "#2c3e50"
    lite = "#e8edf2"

    def sector(r_in, r_out, a0, a1, fill):
        a0r, a1r = math.radians(a0), math.radians(a1)
        x0o, y0o = cx + r_out*math.cos(a0r), cy + r_out*math.sin(a0r)
        x1o, y1o = cx + r_out*math.cos(a1r), cy + r_out*math.sin(a1r)
        x1i, y1i = cx + r_in*math.cos(a1r), cy + r_in*math.sin(a1r)
        x0i, y0i = cx + r_in*math.cos(a0r), cy + r_in*math.sin(a0r)
        large = 1 if (a1-a0) % 360 > 180 else 0
        d = ("M%.2f %.2f A%.2f %.2f 0 %d 1 %.2f %.2f L%.2f %.2f A%.2f %.2f 0 %d 0 %.2f %.2f Z"
             % (x0o, y0o, r_out, r_out, large, x1o, y1o, x1i, y1i, r_in, r_in, large, x0i, y0i))
        return ('<path d="%s" fill="%s" stroke="#ffffff" stroke-width="1.2"/>' % (d, fill))

    step = 360.0/n
    for k, code in enumerate(seq):
        a0 = -90 + k*step
        a1 = a0 + step
        for bit_idx in range(3):  # b2,b1,b0 → кільця зовні-всередину
            r_in, r_out = rings[bit_idx]
            f.append(sector(r_in, r_out, a0, a1, dark if code[bit_idx] == '1' else lite))
        # підпис коду назовні
        amid = math.radians(a0 + step/2)
        lr = 168
        tx, ty = cx + lr*math.cos(amid), cy + lr*math.sin(amid)
        f.append(text(tx, ty+5, code, size=13, bold=True, color=INK))

    # маркер зчитування (нерухомий промінь угорі)
    f.append(line(cx, cy-156, cx, cy-46, color=POS, sw=2.4))
    f.append(text(cx, cy-166, "зчитувачі", size=12, bold=True, color=POS))

    # центр
    f.append(circle(cx, cy, 54, fill=BG, stroke=LINE, sw=1.4))
    f.append(text(cx, cy-4, "обертання", size=12, color=MUTED))
    f.append(text(cx, cy+14, "→", size=18, color=MUTED, bold=True))

    f.append(fitbox(28, H-50, W-56, 40,
                    "Темне кільце = 1, світле = 0. На кожній межі секторів темнішає\n"
                    "чи світлішає рівно одне кільце — один біт. Межі не збігаються.",
                    size=12, fill="#f7f7f9", stroke=MUTED, sw=1))
    render(os.path.join(IMG, 'disk.svg'), W, H, *f)


if __name__ == '__main__':
    fig_straddle()
    fig_reflect()
    fig_disk()
    print("ok")
