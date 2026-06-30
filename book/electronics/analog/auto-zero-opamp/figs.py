# -*- coding: utf-8 -*-
"""Фігури до теми «Auto-zero і чоперна стабілізація ОП» (аналогова електроніка).
Три фігури:
  offset-noise-spectrum.svg — спектр похибок звичайного ОП: 1/f внизу, тепловий вище, зсув поверх
  autozero-phases.svg       — дві фази auto-zero: вимір власної похибки → віднімання
  chopper-frequency-shift.svg— чопер переносить сигнал нагору й назад, виносячи зсув/1-f геть
Запуск:  python figs.py   → пише SVG у ./img/  (швидко, без залежностей)
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def offset_noise_spectrum():
    """Логарифмічна вісь частоти: крива шуму = 1/f (спад) + плато (тепловий),
    поверх — пунктир постійного зсуву; ліворуч заштриховано зону, яку прибирає zero-drift."""
    W, H = 720, 410
    p = []
    ox, oy = 90, 300          # початок осей
    aw, ah = 540, 220         # довжина осей
    # осі
    p.append(arrow(ox, oy, ox + aw + 16, oy, color=INK, sw=2))      # частота →
    p.append(arrow(ox, oy, ox, oy - ah - 16, color=INK, sw=2))      # шум ↑
    p.append(text(ox + aw / 2, oy + 46, "частота (лог)  →", size=13, bold=True))
    p.append(text(ox - 58, oy - ah / 2, "рівень", size=13, bold=True))
    p.append(text(ox - 58, oy - ah / 2 + 17, "похибки", size=13, bold=True))

    # крива шуму: знизу-зліва високо (1/f), плавно спадає до плато (тепловий)
    # x у [0..1] як логарифм частоти; рівень = max(плато, 1/f-внесок)
    plateau = 0.30            # тепловий рівень (частка ah)
    pts = []
    N = 120
    for k in range(N + 1):
        u = k / N                                  # 0..1 уздовж осі
        f_dec = u                                  # «логарифм частоти»
        onef = 0.92 * math.exp(-3.6 * f_dec)       # спад 1/f
        lvl = plateau + onef                       # сумарний шум (огинаюча)
        x = ox + aw * u
        y = oy - ah * min(0.98, lvl)
        pts.append((x, y))
    d = "M" + " L".join("%.1f %.1f" % q for q in pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, POS))

    # частота зламу 1/f — там, де спад 1/f зрівнявся з плато
    fc_u = -math.log(plateau / 0.92) / 3.6
    fc_x = ox + aw * fc_u
    p.append(line(fc_x, oy, fc_x, oy - ah * (plateau + plateau) - 4, color=MUTED, sw=1.3, dash="4 3"))
    p.append(text(fc_x, oy - ah * (2 * plateau) - 10, "частота зламу 1/f", size=11, color=MUTED))

    # підписи ділянок кривої
    p.append(text(ox + aw * 0.16, oy - ah * 0.86, "шум 1/f", size=13, bold=True, color=POS))
    p.append(text(ox + aw * 0.16, oy - ah * 0.86 + 16, "(росте вниз по частоті)", size=10, color=MUTED))
    p.append(text(ox + aw * 0.80, oy - ah * plateau - 12, "тепловий шум (рівний)", size=12, color=POS))

    # постійний зсув — горизонтальний пунктир високо
    off_y = oy - ah * 0.93
    p.append(line(ox, off_y, ox + aw, off_y, color=NEG, sw=2, dash="7 4"))
    p.append(text(ox + aw - 4, off_y - 8, "постійний зсув (DC)", size=12, color=NEG, anchor="end"))

    # зона, яку прибирає zero-drift: ліва частина (низькі частоти)
    band_x2 = ox + aw * 0.40
    p.append(rect(ox, oy - ah, band_x2 - ox, ah, fill="#eafaf0", stroke="none", sw=0, rx=0))
    # повторно домалювати криву поверх заливки (заливку додали після — перемалюємо лінію)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, POS))
    p.append(line(ox, off_y, band_x2, off_y, color=NEG, sw=2, dash="7 4"))
    p.append(text(ox + (band_x2 - ox) / 2, oy - ah - 8, "тут живе повільний сигнал", size=11, bold=True, color=FIELD))

    b, _, _ = textbox(W / 2, 380,
                      "Похибки ОП густі ліворуч: шум 1/f здіймається на низьких частотах, поверх — постійний зсув.\n"
                      "Корисний повільний сигнал живе якраз тут. Zero-drift прибирає всю цю ліву зону разом.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'offset-noise-spectrum.svg'), W, H, *p,
           title="Спектр похибок звичайного ОП: зсув і шум 1/f панують унизу")


def autozero_phases():
    """Дві панелі: ліва — фаза обнулення (входи замкнуто, міряємо власну похибку на C),
    права — фаза підсилення (входи на сигналі, поправка з C віднімається)."""
    W, H = 720, 380
    p = []

    def amp_tri(x, y, lbl):
        out = ['<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
               % (x, y - 30, x, y + 30, x + 64, y, FILL, LINE)]
        out.append(text(x + 22, y + 5, lbl, size=15, bold=True))
        return out

    # ── ЛІВА: фаза обнулення ──
    lx = 36
    cyL = 150
    p.append(text(lx + 150, 64, "фаза обнулення", size=14, bold=True, color=NEG))
    p.append(text(lx + 150, 82, "(входи замкнуто — бачимо лише власну похибку)", size=10, color=MUTED))
    # входи замкнуто на спільну точку
    p.append(line(lx, cyL - 16, lx + 40, cyL - 16, color=INK, sw=2))
    p.append(line(lx, cyL + 16, lx + 40, cyL + 16, color=INK, sw=2))
    p.append(line(lx, cyL - 16, lx, cyL + 16, color=POS, sw=2.4))     # перемичка коротко
    p.append(text(lx - 6, cyL, "0", size=12, bold=True, color=POS, anchor="end"))
    p += amp_tri(lx + 40, cyL, "A")
    # вихід → у конденсатор
    p.append(arrow(lx + 104, cyL, lx + 150, cyL, color=INK, sw=2))
    # запам'ятовувальний конденсатор
    capx = lx + 158
    p.append(line(capx, cyL - 22, capx, cyL + 22, color=FIELD, sw=3))
    p.append(line(capx + 9, cyL - 22, capx + 9, cyL + 22, color=FIELD, sw=3))
    p.append(text(capx + 4, cyL + 44, "C", size=14, bold=True, color=FIELD))
    p.append(text(capx + 4, cyL + 60, "(пам'ять поправки)", size=10, color=MUTED))
    p.append(text(lx + 120, cyL - 40, "міряємо зсув", size=11, color=POS))

    # роздільник
    p.append(line(W / 2, 60, W / 2, 300, color=MUTED, sw=1, dash="5 5"))

    # ── ПРАВА: фаза підсилення ──
    rx = W / 2 + 30
    cyR = 150
    p.append(text(rx + 150, 64, "фаза підсилення", size=14, bold=True, color=FIELD))
    p.append(text(rx + 150, 82, "(входи на сигналі — поправка з C віднімається)", size=10, color=MUTED))
    # сигнал на входи
    p.append(arrow(rx - 6, cyR - 16, rx + 40, cyR - 16, color=INK, sw=2))
    p.append(arrow(rx - 6, cyR + 16, rx + 40, cyR + 16, color=INK, sw=2))
    p.append(text(rx - 10, cyR, "сигнал", size=11, color=INK, anchor="end"))
    p += amp_tri(rx + 40, cyR, "A")
    # поправка з C підмішується у вхід (стрілка знизу)
    capx2 = rx + 72
    p.append(line(capx2, cyR + 70, capx2, cyR + 70, color=FIELD))   # якір
    p.append(line(capx2 - 5, cyR + 58, capx2 - 5, cyR + 82, color=FIELD, sw=3))
    p.append(line(capx2 + 4, cyR + 58, capx2 + 4, cyR + 82, color=FIELD, sw=3))
    p.append(arrow(capx2, cyR + 56, capx2, cyR + 22, color=FIELD, sw=2))
    p.append(text(capx2 + 8, cyR + 74, "− поправка з C", size=11, bold=True, color=FIELD, anchor="start"))
    # чистий вихід
    p.append(arrow(rx + 104, cyR, rx + 150, cyR, color=INK, sw=2))
    p.append(text(rx + 158, cyR + 4, "вихід без зсуву", size=11, bold=True, color=FIELD, anchor="start"))

    # стрілка циклу між панелями
    p.append(text(W / 2, 286, "⟳  фази швидко чергуються", size=12, bold=True, color=MUTED))

    b, _, _ = textbox(W / 2, 350,
                      "Спершу підсилювач міряє власну похибку на замкнутих входах і запам'ятовує її на C.\n"
                      "Тоді на сигналі ця поправка віднімається. Часте чергування тримає нуль попри дрейф і 1/f.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'autozero-phases.svg'), W, H, *p,
           title="Auto-zero: виміряти власний зсув, тоді відняти його")


def chopper_frequency_shift():
    """Ланцюг: вхід → 1-й чопер ↑ → підсилювач (+похибка внизу) → 2-й чопер ↑ → фільтр → вихід.
    Під кожним вузлом — мінісмужка «де сидить сигнал / де похибка» по частоті."""
    W, H = 760, 430
    p = []
    cy = 120
    # вузли ланцюга як прямокутники
    nodes = [
        (60,  "вхід",      "сигнал\nунизу"),
        (190, "1-й чопер", "↑ нагору"),
        (330, "підсилювач","+похибка\nунизу"),
        (480, "2-й чопер", "↑ нагору"),
        (620, "фільтр НЧ", "відрізає\nверх"),
    ]
    bw, bh = 96, 56
    for x, lbl, _ in nodes:
        if "чопер" in lbl:
            p.append(rect(x, cy - bh / 2, bw, bh, fill="#fdecea", stroke=POS, sw=2))
        elif "фільтр" in lbl:
            p.append(rect(x, cy - bh / 2, bw, bh, fill="#eafaf0", stroke=FIELD, sw=2))
        else:
            p.append(rect(x, cy - bh / 2, bw, bh, fill=FILL, stroke=LINE, sw=1.8))
        p.append(text(x + bw / 2, cy + 4, lbl, size=13, bold=True))
    # стрілки між вузлами
    for i in range(len(nodes) - 1):
        x1 = nodes[i][0] + bw
        x2 = nodes[i + 1][0]
        p.append(arrow(x1, cy, x2, cy, color=INK, sw=2))
    # вихід
    p.append(arrow(nodes[-1][0] + bw, cy, nodes[-1][0] + bw + 40, cy, color=INK, sw=2))
    p.append(text(nodes[-1][0] + bw + 46, cy + 4, "чистий\nвихід".split("\n")[0], size=11, bold=True, color=FIELD, anchor="start"))
    p.append(text(nodes[-1][0] + bw + 46, cy + 18, "вихід", size=11, bold=True, color=FIELD, anchor="start"))

    # ── під кожним вузлом: смужка частоти з двома мітками (сигнал / похибка) ──
    sy = cy + 96            # рівень смужок
    sbw = bw                # ширина смужки = ширина вузла
    sbh = 70                # висота смужки (низ=DC, верх=fchop)
    # стани (сигнал_позиція, похибка_позиція) у частці висоти: 0=низько(DC), 1=високо(fchop); None=нема
    states = [
        (0.10, None),       # вхід: сигнал унизу, похибки ще «своєї» нема
        (0.85, None),       # 1-й чопер: сигнал угорі
        (0.85, 0.10),       # підсилювач: сигнал угорі, похибка додалась унизу
        (0.10, 0.85),       # 2-й чопер: сигнал назад униз, похибка викинута вгору
        (0.10, None),       # фільтр: похибку відрізано, лишився сигнал унизу
    ]
    for (x, _, _), (spos, npos) in zip(nodes, states):
        sx = x
        # рамка смужки + підписи DC/fchop
        p.append(rect(sx, sy, sbw, sbh, fill=BG, stroke=MUTED, sw=1))
        p.append(text(sx - 4, sy + sbh - 2, "DC", size=9, color=MUTED, anchor="end"))
        p.append(text(sx - 4, sy + 9, "fчоп", size=9, color=MUTED, anchor="end"))
        # сигнал — синя риска
        sy_sig = sy + sbh - sbh * spos
        p.append(line(sx + 8, sy_sig, sx + sbw - 8, sy_sig, color=NEG, sw=3))
        p.append(text(sx + sbw / 2, sy_sig - 4, "сигнал", size=9, bold=True, color=NEG))
        # похибка — червона риска (якщо є)
        if npos is not None:
            ny = sy + sbh - sbh * npos
            p.append(line(sx + 8, ny, sx + sbw - 8, ny, color=POS, sw=3, dash="4 2"))
            p.append(text(sx + sbw / 2, ny + 11, "похибка", size=9, bold=True, color=POS))

    p.append(text(W / 2, sy - 12, "де по частоті сидить сигнал (синій) і похибка нуля (червоний)",
                  size=11, bold=True, color=MUTED))

    b, _, _ = textbox(W / 2, 402,
                      "Сигнал їде нагору на частоту чопера, де підсилювач чистий, і повертається назад на місце.\n"
                      "Зсув та шум 1/f, навпаки, виносяться нагору — і фільтр НЧ їх прибирає. Нуль до виходу не доходить.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'chopper-frequency-shift.svg'), W, H, *p,
           title="Чопер: підняти сигнал угору, де нема похибок, тоді опустити назад")


def dropin_blackbox():
    """Те, що читач бачить ззовні (5-вивідний ОП), і те, що сховано всередині:
    стабілізувальна петля (чопер/auto-zero), яка безперервно прибирає зсув головного каскаду."""
    W, H = 760, 430
    p = []

    # ── зовнішній корпус: 5 виводів, як у звичайного ОП ──
    bx, by, bw, bh = 250, 110, 260, 200
    p.append(rect(bx, by, bw, bh, fill="#eef7f0", stroke=FIELD, sw=2.2))
    p.append(text(bx + bw / 2, by - 12, "ззовні — звичайний ОП на 5 виводів", size=13, bold=True, color=FIELD))

    # виводи: +IN, −IN зліва; OUT справа; V+ зверху, V− знизу
    p.append(text(bx - 8, by + 64, "+IN", size=12, bold=True, color=POS, anchor="end"))
    p.append(line(bx - 40, by + 60, bx, by + 60, color=INK, sw=2))
    p.append(text(bx - 8, by + 132, "−IN", size=12, bold=True, color=NEG, anchor="end"))
    p.append(line(bx - 40, by + 128, bx, by + 128, color=INK, sw=2))
    p.append(text(bx + bw + 8, by + 96, "OUT", size=12, bold=True, anchor="start"))
    p.append(arrow(bx + bw, by + 96, bx + bw + 40, by + 96, color=INK, sw=2))
    p.append(text(bx + bw / 2, by - 30, "V+", size=11, color=MUTED))
    p.append(line(bx + bw / 2, by - 26, bx + bw / 2, by, color=MUTED, sw=2))
    p.append(text(bx + bw / 2, by + bh + 24, "V−", size=11, color=MUTED))
    p.append(line(bx + bw / 2, by + bh, bx + bw / 2, by + bh + 18, color=MUTED, sw=2))

    # ── всередині: головний каскад (трикутник) ──
    ax, ay = bx + 70, by + 96
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
             % (ax, ay - 34, ax, ay + 34, ax + 70, ay, FILL, LINE))
    p.append(plus(ax - 0, ay - 18, 7))
    p.append(minus(ax - 0, ay + 18, 7))
    p.append(text(ax + 26, ay + 5, "головний", size=10, bold=True))
    p.append(text(ax + 26, ay + 18, "каскад", size=10, bold=True))
    # вхідні лінії до каскаду
    p.append(line(bx, by + 60, ax, ay - 18, color=POS, sw=1.6))
    p.append(line(bx, by + 128, ax, ay + 18, color=NEG, sw=1.6))
    # вихід каскаду
    p.append(line(ax + 70, ay, bx + bw, by + 96, color=INK, sw=1.8))

    # ── стабілізувальна петля (те, що приховано) ──
    loop_y = by + bh - 34
    p.append(rect(bx + 28, loop_y - 18, bw - 56, 34, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(bx + bw / 2, loop_y + 4, "чопер / auto-zero: міряє й гасить зсув", size=10.5, bold=True, color=POS))
    # стрілка: петля «дивиться» на головний каскад і підправляє його
    p.append(arrow(bx + bw / 2, loop_y - 18, bx + bw / 2, ay + 36, color=POS, sw=1.6))
    p.append(text(bx + bw / 2 + 6, ay + 52, "− корекція зсуву", size=9.5, color=POS, anchor="start"))

    # підпис «приховано»
    p.append(text(bx + bw / 2, by + bh + 44, "всередині — машинерія, якої на виводах не видно", size=12, bold=True, color=POS))

    # ── ліворуч: підпис «що це дає на виводах» ──
    b, _, _ = textbox(150, 150,
                      "На виводах\nповодиться як\nдрібний ОП:\n+IN, −IN, OUT,\nживлення.\n\nDrop-in заміна.",
                      size=12, fill="#eef7f0", stroke=FIELD, bold=False)
    p.append(b)
    # ── праворуч: чим відрізняється ──
    b2, _, _ = textbox(632, 150,
                       "Але всередині\nщось безперервно\nперемикається —\nзвідси й переваги,\nі граблі класу.",
                       size=12, fill="#fdecea", stroke=POS)
    p.append(b2)

    b3, _, _ = textbox(W / 2, 402,
                       "Зовні zero-drift ОП — звичайна 5-вивідна мікросхема, drop-in заміна будь-якого ОП.\n"
                       "Усередині схована петля, що безперервно вимірює власний зсув каскаду й віднімає його.",
                       size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b3)
    render(os.path.join(OUT, 'dropin-blackbox.svg'), W, H, *p,
           title="Zero-drift ОП ззовні і всередині: звичайні виводи, схована петля")


def ripple_and_filter():
    """Чому «перший байт» на виході не чистий: брязкіт на частоті чопера + голки charge injection,
    і як простий RC/фільтр НЧ після виходу прибирає їх, лишаючи чистий повільний рівень."""
    W, H = 760, 430
    p = []

    # ── ліва панель: сирий вихід (брязкіт + голки) ──
    lx, ly, lw, lh = 40, 90, 300, 150
    p.append(rect(lx, ly, lw, lh, fill=BG, stroke=MUTED, sw=1))
    p.append(text(lx + lw / 2, ly - 12, "сирий вихід zero-drift ОП", size=13, bold=True, color=POS))
    midL = ly + lh * 0.55
    # корисний рівень (рівна синя лінія)
    p.append(line(lx + 8, midL, lx + lw - 8, midL, color=NEG, sw=1.4, dash="6 4"))
    p.append(text(lx + lw - 10, midL + 16, "корисний рівень", size=10, color=NEG, anchor="end"))
    # брязкіт: пилкоподібний/прямокутний меандр навколо рівня
    saw = []
    n = 14
    for i in range(n + 1):
        u = i / n
        x = lx + 8 + (lw - 16) * u
        y = midL + (-1 if i % 2 == 0 else 1) * 14
        saw.append((x, y))
    d = "M" + " L".join("%.1f %.1f" % q for q in saw)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d, POS))
    p.append(text(lx + 70, ly + 22, "брязкіт fчоп", size=11, bold=True, color=POS))
    # голки charge injection — кілька тонких вертикальних піків
    for gx in (lx + 60, lx + 150, lx + 240):
        p.append(line(gx, midL, gx, midL - 30, color=INK, sw=1.4))
        p.append(line(gx, midL - 30, gx + 4, midL - 22, color=INK, sw=1.4))
        p.append(line(gx, midL - 30, gx - 4, midL - 22, color=INK, sw=1.4))
    p.append(text(lx + lw / 2, ly + lh + 18, "голки charge injection (перемикання ключів)", size=10, color=INK))

    # ── стрілка через фільтр ──
    fx = lx + lw + 20
    p.append(rect(fx, midL - 26, 70, 52, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(text(fx + 35, midL - 4, "фільтр", size=11, bold=True, color=FIELD))
    p.append(text(fx + 35, midL + 11, "НЧ (RC)", size=11, bold=True, color=FIELD))
    p.append(arrow(lx + lw, midL, fx, midL, color=INK, sw=2))
    p.append(arrow(fx + 70, midL, fx + 70 + 24, midL, color=INK, sw=2))

    # ── права панель: чистий вихід ──
    rx, ry, rw, rh = fx + 70 + 24 + 6, ly, 300 - 60, lh
    p.append(rect(rx, ry, rw, rh, fill=BG, stroke=MUTED, sw=1))
    p.append(text(rx + rw / 2, ry - 12, "після фільтра", size=13, bold=True, color=FIELD))
    midR = ry + rh * 0.55
    p.append(line(rx + 8, midR, rx + rw - 8, midR, color=NEG, sw=2.4))
    p.append(text(rx + rw / 2, midR - 10, "чистий повільний рівень", size=10, bold=True, color=FIELD))

    # підпис-застереження
    b, _, _ = textbox(W / 2, 330,
                      "Брязкіт сидить на частоті чопера (сотні кГц), голки — на перемиканнях ключів.\n"
                      "Простий фільтр НЧ після виходу їх прибирає — але ВЕСТИ сигнал у смузі біля fчоп не можна.",
                      size=12, fill="#fdecea", stroke=POS)
    p.append(b)
    b2, _, _ = textbox(W / 2, 402,
                       "Тому «перший байт» zero-drift ОП на осцилографі — не рівна лінія, а рівень із брязкотом і голками.\n"
                       "Це нормальна поведінка класу: фільтруй вихід і не клади корисну смугу впритул до частоти чопера.",
                       size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b2)
    render(os.path.join(OUT, 'ripple-and-filter.svg'), W, H, *p,
           title="«Перший байт»: брязкіт чопера й голки на виході — і фільтр, що їх знімає")


if __name__ == '__main__':
    offset_noise_spectrum()
    autozero_phases()
    chopper_frequency_shift()
    dropin_blackbox()
    ripple_and_filter()
    print("OK: 5 figures ->", OUT)
