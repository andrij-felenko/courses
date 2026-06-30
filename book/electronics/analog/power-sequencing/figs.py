# -*- coding: utf-8 -*-
"""Фігури до теми «Черговість увімкнення шин живлення».
  latchup.svg    — паразитний тиристор p-n-p-n у КМОН (два BJT, регенерація)
  backpower.svg  — сигнал живить знеструмлений чип крізь захисний ESD-діод
  monotonic.svg  — монотонне наростання проти провалу в критичній зоні
  methods.svg    — три способи задати черговість (RC / Power-Good / розпорядник)
Вставка comp-isolation-switch:
  iso-block.svg  — блок-схема ключа/буфера-розв'язки з вивідами EN/OE/DIR
  iso-ioff.svg   — звичайний ESD-діод проти Ioff (блокувальний діод від Vcc)
  iso-place.svg  — куди ставити розв'язку: на межі знеструмлений↔живлений
Вставка comp-sequencer-ic:
  seq-block.svg  — блок-схема розпорядника (автомат + компаратори UV/OV → EN)
  seq-wiring.svg — типове підключення: EN назовні, вихід шини назад на нагляд
  seq-timing.svg — програма пуску по черзі й гасіння у зворотному порядку
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Паразитний тиристор у КМОН ───────────────────────────────────────────
def fig_latchup():
    W, H = 700, 380
    f = []
    f.append(text(W/2, 26, "Паразитний тиристор у КМОН: p-n-p-n замикає V+ на землю", size=16, bold=True))

    # шини
    f.append(line(70, 70, 630, 70, color=POS, sw=3))
    f.append(text(60, 75, "V+", size=15, color=POS, anchor="end", bold=True))
    f.append(line(70, 320, 630, 320, color=NEG, sw=3))
    f.append(text(60, 325, "GND", size=14, color=NEG, anchor="end", bold=True))

    # чотири шари p-n-p-n як стовпчик блоків
    cx = 250
    layers = [("p", "#f6d6d2", POS), ("n", "#d6e0f8", NEG), ("p", "#f6d6d2", POS), ("n", "#d6e0f8", NEG)]
    y0, bw, bh = 110, 130, 42
    for i, (lab, fill, col) in enumerate(layers):
        y = y0 + i*bh
        f.append(rect(cx-bw/2, y, bw, bh, fill=fill, stroke=col, sw=1.8, rx=4))
        f.append(text(cx, y+bh*0.66, lab, size=20, color=col, bold=True))
    f.append(line(cx, 70, cx, y0, color=POS, sw=2))
    f.append(line(cx, y0+4*bh, cx, 320, color=NEG, sw=2))
    f.append(text(cx, y0-8, "структура p-n-p-n", size=12, color=MUTED))

    # еквівалент: два BJT, регенеративна петля
    bx = 500
    b1, _, _ = textbox(bx, 150, "PNP", size=15, fill="#fdecea", stroke=POS, color=POS, bold=True, min_w=86)
    b2, _, _ = textbox(bx, 250, "NPN", size=15, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True, min_w=86)
    f.append(b1); f.append(b2)
    f.append(line(bx, 70, bx, 132, color=POS, sw=2))
    f.append(line(bx, 268, bx, 320, color=NEG, sw=2))
    # регенеративна петля: колектор PNP → база NPN і навпаки
    f.append(arrow(bx+44, 158, bx+44, 242, color=INK, sw=1.8))
    f.append(arrow(bx-44, 242, bx-44, 158, color=INK, sw=1.8))
    f.append(text(bx+96, 205, "сам себе", size=12, color=INK, anchor="middle"))
    f.append(text(bx+96, 221, "тримає", size=12, color=INK, anchor="middle"))

    # підпис-висновок про струм
    note = fitbox(150, 340, 400, 30, "відкрився раз → низькоомний канал V+→GND, струми в ампери",
                  size=12, fill="#fff6e5", stroke="#e0a800", color="#7a5b00")
    f.append(note)
    render(os.path.join(IMG, "latchup.svg"), W, H, *f)


# ── 2. Живлення з чорного ходу крізь ESD-діод ───────────────────────────────
def fig_backpower():
    W, H = 700, 360
    f = []
    f.append(text(W/2, 26, "Живлення «з чорного ходу» крізь захисний діод виводу", size=16, bold=True))

    # сусід (ввімкнений)
    nb = fitbox(60, 120, 150, 90, "Сусід\nввімкнено\nвидає сигнал",
                size=14, fill="#e9f7ee", stroke=FIELD, color="#1c6b3a", bold=True)
    f.append(nb)

    # знеструмлений чип
    ch_x, ch_y, ch_w, ch_h = 420, 95, 200, 175
    f.append(rect(ch_x, ch_y, ch_w, ch_h, fill="#f0f0f2", stroke=MUTED, sw=1.8, rx=8))
    f.append(text(ch_x+ch_w/2, ch_y+24, "Знеструмлений чип", size=14, color=INK, bold=True))
    f.append(text(ch_x+ch_w/2, ch_y+42, "(шина = 0 В)", size=12, color=MUTED))

    # внутрішня шина чипа + ESD-діоди на виводі
    vbus_y = ch_y+70
    f.append(line(ch_x+20, vbus_y, ch_x+ch_w-20, vbus_y, color=POS, sw=2.5))
    f.append(text(ch_x+ch_w-24, vbus_y-8, "шина чипа", size=11, color=POS, anchor="end"))
    pad_x = ch_x+40
    pad_y = ch_y+130
    f.append(circle(pad_x, pad_y, 7, fill=BG, stroke=INK, sw=2))
    f.append(text(pad_x, pad_y+26, "вивід", size=11, color=INK))
    # верхній діод вивід→шина (трикутник вказує вгору = відкритий цим сигналом)
    dx = pad_x
    f.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f z" fill="#fdecea" stroke="%s" stroke-width="1.6"/>'
             % (dx-9, vbus_y+34, dx+9, vbus_y+34, dx, vbus_y+14, POS))
    f.append(line(dx-11, vbus_y+14, dx+11, vbus_y+14, color=POS, sw=2))
    f.append(line(dx, vbus_y, dx, vbus_y+14, color=POS, sw=2))
    f.append(line(dx, vbus_y+34, dx, pad_y-7, color=INK, sw=2))
    f.append(text(dx+62, vbus_y+30, "ESD-діод", size=11, color=POS, anchor="middle"))
    f.append(text(dx+62, vbus_y+46, "відкрився", size=11, color=POS, anchor="middle"))

    # сигнал тече від сусіда у вивід і вгору в шину
    f.append(arrow(210, 165, pad_x-2, pad_y, color=INK, sw=2.2))
    f.append(text(310, 150, "сигнал > 0 В", size=12, color=INK))

    # висновок
    note = fitbox(40, 302, 620, 38, "сигнал живить мертву шину → напівмертвий стан, струм палить діод, ризик засувки",
                  size=13, fill="#fff6e5", stroke="#e0a800", color="#7a5b00")
    f.append(note)
    render(os.path.join(IMG, "backpower.svg"), W, H, *f)


# ── 3. Монотонність проти провалу ───────────────────────────────────────────
def fig_monotonic():
    W, H = 720, 340
    f = []
    f.append(text(W/2, 26, "Монотонне наростання проти провалу в критичній зоні", size=16, bold=True))

    def axes(ox, oy, w, h, title, ok):
        g = []
        col = FIELD if ok else POS
        g.append(text(ox+w/2, oy-h-12, title, size=13, color=col, bold=True))
        g.append(line(ox, oy, ox+w, oy, color=INK, sw=1.6))          # t
        g.append(line(ox, oy, ox, oy-h, color=INK, sw=1.6))          # V
        g.append(text(ox+w+4, oy+4, "t", size=12, color=INK))
        g.append(text(ox-6, oy-h-2, "V", size=12, color=INK, anchor="end"))
        # критична зона 0.5..0.9 (як смуга по висоті)
        zy1 = oy - h*0.30
        zy2 = oy - h*0.62
        g.append(rect(ox, zy2, w, zy1-zy2, fill="#fdecec", stroke="none", rx=0))
        g.append(text(ox+w-4, (zy1+zy2)/2+4, "крит. зона", size=10, color=MUTED, anchor="end"))
        return g, col, zy1, zy2

    # ліворуч: монотонне
    ox, oy, w, h = 70, 280, 250, 200
    g, col, zy1, zy2 = axes(ox, oy, w, h, "монотонно — старт ОК", True)
    f.extend(g)
    pts = []
    for i in range(0, 101):
        t = i/100.0
        v = 1 - math.exp(-3.2*t)               # рівне насичення
        pts.append((ox + t*w, oy - v*h*0.9))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join("%.1f,%.1f" % p for p in pts), FIELD))

    # праворуч: провал
    ox2 = 400
    g, col, zy1, zy2 = axes(ox2, oy, w, h, "провал — старт зривається", False)
    f.extend(g)
    pts = []
    for i in range(0, 101):
        t = i/100.0
        v = 1 - math.exp(-3.2*t)
        # провал у критичній зоні (t ~ 0.28..0.45)
        if 0.26 < t < 0.50:
            v -= 0.34*math.exp(-((t-0.38)/0.06)**2)
        pts.append((ox2 + t*w, oy - max(v,0)*h*0.9))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join("%.1f,%.1f" % p for p in pts), POS))
    # позначити провал
    f.append(text(ox2+w*0.40, oy - h*0.18, "провал", size=12, color=POS, bold=True))
    f.append(arrow(ox2+w*0.42, oy - h*0.22, ox2+w*0.40, oy - h*0.36, color=POS, sw=1.8))

    render(os.path.join(IMG, "monotonic.svg"), W, H, *f)


# ── 4. Три способи задати черговість ────────────────────────────────────────
def fig_methods():
    W, H = 720, 360
    f = []
    f.append(text(W/2, 26, "Три способи задати черговість шин", size=16, bold=True))

    col_w = 210
    xs = [30, 255, 480]
    titles = ["RC-затримка", "естафета Power-Good", "розпорядник"]
    subs = ["дешево, кілька шин", "за справжньою напругою", "багато шин, нагляд, гасіння"]
    cols = [MUTED, NEG, FIELD]

    for x, ti, su, cc in zip(xs, titles, subs, cols):
        f.append(rect(x, 50, col_w, 285, fill=BG, stroke=cc, sw=1.8, rx=8))
        f.append(text(x+col_w/2, 74, ti, size=14, color=cc, bold=True))
        f.append(line(x+14, 84, x+col_w-14, 84, color=cc, sw=1))

    # 1) RC
    x = xs[0]
    f.append(fitbox(x+20, 100, 170, 30, "шина 1 «є»", size=12, fill="#f4f6f8", stroke=POS, color=POS))
    f.append(line(x+col_w/2, 130, x+col_w/2, 150, color=INK, sw=2))
    f.append(rect(x+60, 150, 90, 30, fill="#f0f0f2", stroke=INK, sw=1.5, rx=4))
    f.append(text(x+col_w/2, 170, "R·C", size=13, color=INK, bold=True))
    f.append(arrow(x+col_w/2, 180, x+col_w/2, 205, color=INK, sw=2))
    f.append(fitbox(x+20, 205, 170, 34, "EN шини 2\nіз затримкою", size=12, fill="#eef5ff", stroke=NEG, color=NEG))
    f.append(text(x+col_w/2, 270, "таймер наосліп", size=11, color=MUTED))

    # 2) Power-Good
    x = xs[1]
    f.append(fitbox(x+20, 100, 170, 34, "перетворювач 1\nдоріс до номіналу", size=11.5, fill="#f4f6f8", stroke=POS, color=POS))
    f.append(arrow(x+col_w/2, 134, x+col_w/2, 158, color=FIELD, sw=2.2))
    f.append(text(x+col_w/2+6, 150, "PG↑", size=12, color=FIELD, anchor="start", bold=True))
    f.append(fitbox(x+20, 158, 170, 30, "EN шини 2", size=12, fill="#eef5ff", stroke=NEG, color=NEG))
    f.append(arrow(x+col_w/2, 188, x+col_w/2, 210, color=INK, sw=2))
    f.append(fitbox(x+20, 210, 170, 30, "шина 2 росте", size=12, fill="#f4f6f8", stroke=POS, color=POS))
    f.append(text(x+col_w/2, 270, "за фактом готовності", size=11, color=MUTED))

    # 3) розпорядник
    x = xs[2]
    f.append(rect(x+55, 100, 100, 60, fill="#e9f7ee", stroke=FIELD, sw=2, rx=6))
    f.append(text(x+col_w/2, 124, "чип-", size=12, color="#1c6b3a", bold=True))
    f.append(text(x+col_w/2, 142, "розпорядник", size=12, color="#1c6b3a", bold=True))
    for i, yy in enumerate([200, 235, 270]):
        f.append(arrow(x+col_w/2, 162, x+40, yy-8, color=FIELD, sw=1.6))
        f.append(arrow(x+col_w/2, 162, x+col_w-40, yy-8, color=FIELD, sw=1.6))
    f.append(fitbox(x+24, 195, 162, 26, "EN шини 1 … N", size=11.5, fill="#eef5ff", stroke=NEG, color=NEG))
    f.append(fitbox(x+24, 228, 162, 26, "нагляд за рівнями", size=11.5, fill="#f4f6f8", stroke=INK, color=INK))
    f.append(fitbox(x+24, 261, 162, 26, "гасіння в зворотному порядку", size=10.5, fill="#f4f6f8", stroke=INK, color=INK))

    render(os.path.join(IMG, "methods.svg"), W, H, *f)


# ── 5. Блок-схема ключа/буфера-розв'язки з вивідами керування ────────────────
def fig_iso_block():
    W, H = 720, 360
    f = []
    f.append(text(W/2, 26, "Розв'язка сигналу: ключ / буфер із вивідами керування", size=16, bold=True))

    # центральний пристрій
    dx, dy, dw, dh = 270, 90, 180, 180
    f.append(rect(dx, dy, dw, dh, fill="#eef5ff", stroke=NEG, sw=2, rx=10))
    f.append(text(dx+dw/2, dy+26, "розв'язувач", size=14, color=NEG, bold=True))
    f.append(text(dx+dw/2, dy+44, "ключ / буфер", size=12, color=MUTED))

    # сигнальний прохід A ↔ B крізь пристрій
    sy = dy+110
    f.append(line(120, sy, dx, sy, color=INK, sw=2.4))
    f.append(line(dx+dw, sy, 600, sy, color=INK, sw=2.4))
    f.append(circle(dx, sy, 6, fill=BG, stroke=INK, sw=2))
    f.append(circle(dx+dw, sy, 6, fill=BG, stroke=INK, sw=2))
    f.append(text(120, sy-12, "бік A", size=12, color=INK, anchor="start", bold=True))
    f.append(text(600, sy-12, "бік B", size=12, color=INK, anchor="end", bold=True))
    # розрив у проході: видимий «замок»
    f.append(rect(dx+dw/2-20, sy-13, 40, 26, fill="#fff6e5", stroke="#e0a800", sw=1.6, rx=4))
    f.append(text(dx+dw/2, sy+5, "⟂", size=15, color="#7a5b00", bold=True))

    # виводи керування знизу
    pins = [("EN", "увімкнути канал", FIELD),
            ("OE", "вихід → Hi-Z", NEG),
            ("DIR", "A→B чи B→A", POS)]
    for i, (nm, desc, cc) in enumerate(pins):
        px = dx + 30 + i*60
        f.append(line(px, dy+dh, px, dy+dh+22, color=cc, sw=2))
        f.append(circle(px, dy+dh+22, 5, fill=BG, stroke=cc, sw=2))
        f.append(text(px, dy+dh+40, nm, size=12, color=cc, bold=True))
    f.append(fitbox(180, 310, 360, 30,
                    "EN/OE — пускати чи рвати канал · DIR — куди дивиться буфер",
                    size=11.5, fill="#f4f6f8", stroke=MUTED, color=INK))

    # ярлик «живлення власне»
    f.append(line(dx+dw/2, dy, dx+dw/2, 60, color=POS, sw=2))
    f.append(text(dx+dw/2, 54, "Vcc розв'язувача", size=11, color=POS))
    render(os.path.join(IMG, "iso-block.svg"), W, H, *f)


# ── 6. Звичайний ESD-діод проти Ioff (блокувальний діод від Vcc) ─────────────
def fig_iso_ioff():
    W, H = 720, 360
    f = []
    f.append(text(W/2, 26, "Чому Ioff не пускає струм у мертвий Vcc", size=16, bold=True))

    def diode_up(x, ytop, ybot, col):
        # трикутник вершиною вгору (провідність знизу-вгору), катод-риска згори
        g = []
        g.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f z" fill="#fdecea" stroke="%s" stroke-width="1.6"/>'
                 % (x-9, ybot, x+9, ybot, x, ytop+8, col))
        g.append(line(x-11, ytop+8, x+11, ytop+8, color=col, sw=2))
        return g

    # ── ліва панель: звичайний вивід (back-power) ──
    f.append(text(180, 60, "звичайний вивід", size=13, color=POS, bold=True))
    vx = 180
    f.append(line(vx-70, 90, vx+70, 90, color=MUTED, sw=2.5))
    f.append(text(vx-74, 95, "Vcc=0", size=12, color=MUTED, anchor="end"))
    f.extend(diode_up(vx, 90, 150, POS))                  # вивід → Vcc
    f.append(line(vx, 150, vx, 210, color=INK, sw=2))
    f.append(circle(vx, 210, 6, fill=BG, stroke=INK, sw=2))
    f.append(text(vx, 234, "вивід (сигнал > 0)", size=11, color=INK))
    f.append(arrow(vx, 205, vx, 100, color=POS, sw=2.4))  # струм угору в Vcc
    f.append(text(vx+58, 150, "струм", size=11, color=POS))
    f.append(text(vx+58, 165, "у Vcc", size=11, color=POS))
    f.append(fitbox(70, 270, 220, 32, "діод відкрився → мертва шина оживає",
                    size=11.5, fill="#fdecea", stroke=POS, color=POS))

    # ── права панель: Ioff (блокувальний діод) ──
    f.append(text(540, 60, "вивід з Ioff", size=13, color=FIELD, bold=True))
    bx = 540
    f.append(line(bx-70, 90, bx+70, 90, color=MUTED, sw=2.5))
    f.append(text(bx+74, 95, "Vcc=0", size=12, color=MUTED, anchor="start"))
    # блокувальний діод між спільним катодом і Vcc (вершиною ВНИЗ — назад заперто)
    f.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f z" fill="#e9f7ee" stroke="%s" stroke-width="1.6"/>'
             % (bx-9, 104, bx+9, 104, bx, 124, FIELD))
    f.append(line(bx-11, 124, bx+11, 124, color=FIELD, sw=2))
    f.append(line(bx, 90, bx, 104, color=FIELD, sw=2))
    f.append(text(bx+58, 116, "блокує", size=11, color=FIELD))
    f.extend(diode_up(bx, 124, 168, POS))                 # ESD-діод вивід→спільний катод
    f.append(line(bx, 168, bx, 210, color=INK, sw=2))
    f.append(circle(bx, 210, 6, fill=BG, stroke=INK, sw=2))
    f.append(text(bx, 234, "вивід (сигнал > 0)", size=11, color=INK))
    # перекреслений шлях угору
    f.append(line(bx, 205, bx, 130, color=MUTED, sw=2, dash="5,5"))
    f.append(text(bx-58, 150, "немає", size=11, color=FIELD))
    f.append(text(bx-58, 165, "шляху", size=11, color=FIELD))
    f.append(fitbox(430, 270, 220, 32, "блокувальний діод заперто → Vcc не оживає",
                    size=11.5, fill="#e9f7ee", stroke=FIELD, color="#1c6b3a"))

    # роздільник
    f.append(line(360, 80, 360, 300, color="#dddddd", sw=1.4, dash="4,4"))
    render(os.path.join(IMG, "iso-ioff.svg"), W, H, *f)


# ── 7. Куди ставити розв'язку: на межі знеструмлений ↔ живлений ──────────────
def fig_iso_place():
    W, H = 720, 320
    f = []
    f.append(text(W/2, 26, "Розв'язку ставлять на межі двох доменів живлення", size=16, bold=True))

    # домен А — рано вмикається / завжди живий
    f.append(rect(40, 80, 200, 150, fill="#e9f7ee", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(140, 104, "завжди живий", size=13, color="#1c6b3a", bold=True))
    f.append(text(140, 122, "(або вмикається раніше)", size=10.5, color=MUTED))
    f.append(fitbox(70, 150, 140, 50, "процесор\nшина 3.3 В\nбалакучий", size=12,
                    fill=BG, stroke=FIELD, color="#1c6b3a"))

    # домен Б — пізно вмикається / може бути мертвий
    f.append(rect(480, 80, 200, 150, fill="#f0f0f2", stroke=MUTED, sw=1.8, rx=8))
    f.append(text(580, 104, "вмикається пізно", size=13, color=INK, bold=True))
    f.append(text(580, 122, "(буває знеструмлений)", size=10.5, color=MUTED))
    f.append(fitbox(510, 150, 140, 50, "давач / модуль\nшина може\nбути 0 В", size=12,
                    fill=BG, stroke=MUTED, color=INK))

    # розв'язувач посередині на межі
    f.append(rect(300, 110, 120, 90, fill="#eef5ff", stroke=NEG, sw=2, rx=8))
    f.append(text(360, 138, "розв'язка", size=13, color=NEG, bold=True))
    f.append(text(360, 156, "ключ /", size=11, color=NEG))
    f.append(text(360, 172, "буфер Ioff", size=11, color=NEG))

    # сигнальні лінії крізь розв'язувач
    f.append(line(240, 175, 300, 175, color=INK, sw=2.2))
    f.append(line(420, 175, 480, 175, color=INK, sw=2.2))

    # EN від «живого» домену
    f.append(arrow(190, 205, 330, 205, color=FIELD, sw=1.8))
    f.append(line(330, 205, 330, 200, color=FIELD, sw=1.8))
    f.append(text(255, 222, "EN/OE дозволяє канал, коли обидва домени живі",
                  size=10.5, color="#1c6b3a", anchor="middle"))

    f.append(fitbox(120, 258, 480, 34,
                    "доки правий домен мертвий — канал розірвано: ні back-power, ні засувки",
                    size=12, fill="#fff6e5", stroke="#e0a800", color="#7a5b00"))
    render(os.path.join(IMG, "iso-place.svg"), W, H, *f)


# ── 8. Блок-схема мікросхеми-розпорядника живлення ───────────────────────────
def fig_seq_block():
    W, H = 720, 420
    f = []
    f.append(text(W/2, 26, "Усередині розпорядника: автомат + компаратори на кожен канал", size=15, bold=True))

    # центральний автомат послідовності
    ax, ay, aw, ah = 280, 70, 160, 90
    f.append(rect(ax, ay, aw, ah, fill="#eef5ff", stroke=NEG, sw=2, rx=10))
    f.append(text(ax+aw/2, ay+30, "автомат", size=14, color=NEG, bold=True))
    f.append(text(ax+aw/2, ay+48, "послідовності", size=12, color=NEG))
    f.append(text(ax+aw/2, ay+68, "+ таймери", size=11, color=MUTED))
    # пам'ять програми збоку
    f.append(rect(490, ay+8, 120, 36, fill="#f4f6f8", stroke=INK, sw=1.4, rx=5))
    f.append(text(550, ay+30, "програма (NV)", size=11, color=INK))
    f.append(arrow(490, ay+26, ax+aw+2, ay+26, color=MUTED, sw=1.6))

    # три канали: компаратори UV/OV → вивід EN
    chy = [200, 280, 360]
    for i, cy in enumerate(chy):
        # компаратор-пара
        cmpx = 90
        f.append(rect(cmpx, cy-22, 120, 44, fill="#fdecea", stroke=POS, sw=1.6, rx=6))
        f.append(text(cmpx+60, cy-4, "UV / OV", size=12, color=POS, bold=True))
        f.append(text(cmpx+60, cy+12, "пороги", size=10.5, color=MUTED))
        # вхід «зворотний зв'язок з шини i»
        f.append(line(20, cy, cmpx, cy, color=POS, sw=2))
        f.append(text(20, cy-8, "шина %d" % (i+1), size=10.5, color=POS, anchor="start"))
        # компаратор → автомат (статус готовності)
        f.append(arrow(cmpx+120, cy, ax-2, ay+ah-10 if i == 0 else (ay+ah+10), color=POS, sw=1.5))
        # автомат → вивід EN каналу i
        ex = ax+aw+40
        f.append(arrow(ax+aw, ay+ah-6, ex, cy, color=FIELD, sw=1.6))
        f.append(circle(ex+40, cy, 6, fill=BG, stroke=FIELD, sw=2))
        f.append(line(ex, cy, ex+40, cy, color=FIELD, sw=2))
        f.append(text(ex+50, cy+4, "EN%d → перетв. %d" % (i+1, i+1), size=11, color=FIELD, anchor="start"))

    # глобальні виводи: спільний дозвіл, спільне «усе добре», скидання
    f.append(line(ax, ay, ax, 40, color=INK, sw=2))
    f.append(circle(ax, 40, 6, fill=BG, stroke=INK, sw=2))
    f.append(text(ax-10, 40, "EN (пуск усього)", size=11, color=INK, anchor="end"))
    f.append(line(ax+aw, ay, ax+aw, 40, color=INK, sw=2))
    f.append(circle(ax+aw, 40, 6, fill=BG, stroke=INK, sw=2))
    f.append(text(ax+aw+10, 40, "ALL_GOOD / RESET", size=11, color=INK, anchor="start"))

    f.append(fitbox(40, 392, 640, 24,
                    "автомат веде EN кожного каналу за програмою; компаратори UV/OV доповідають реальний рівень кожної шини",
                    size=11, fill="#f4f6f8", stroke=MUTED, color=INK))
    render(os.path.join(IMG, "seq-block.svg"), W, H, *f)


# ── 9. Типове підключення розпорядника до перетворювачів ─────────────────────
def fig_seq_wiring():
    W, H = 720, 400
    f = []
    f.append(text(W/2, 26, "Типове підключення: дві лінії на кожну шину", size=16, bold=True))

    # розпорядник зліва
    sx, sy, sw_, sh = 50, 90, 150, 250
    f.append(rect(sx, sy, sw_, sh, fill="#eef5ff", stroke=NEG, sw=2, rx=10))
    f.append(text(sx+sw_/2, sy+26, "розпорядник", size=14, color=NEG, bold=True))

    # три перетворювачі праворуч
    convs = [("перетв. ядра", "0.9 В", 80),
             ("перетв. виводів", "1.8 В", 175),
             ("перетв. I/O", "3.3 В", 270)]
    cvx, cvw, cvh = 470, 180, 70
    for nm, vv, cy in convs:
        f.append(rect(cvx, cy, cvw, cvh, fill="#f4f6f8", stroke=INK, sw=1.6, rx=8))
        f.append(text(cvx+cvw/2, cy+26, nm, size=12.5, color=INK, bold=True))
        f.append(text(cvx+cvw/2, cy+46, "вихід " + vv, size=11, color=POS))
        # EN: розпорядник → перетворювач (керування)
        eny = cy+18
        f.append(arrow(sx+sw_, sy+50, cvx, eny, color=FIELD, sw=1.7))
        f.append(text((sx+sw_+cvx)/2, eny-6, "EN", size=11, color=FIELD, anchor="middle", bold=True))
        # зворотний зв'язок виходу → у розпорядник (нагляд)
        fby = cy+52
        f.append(arrow(cvx, fby, sx+sw_+2, sy+200, color=POS, sw=1.4))
        f.append(text((sx+sw_+cvx)/2, fby+14, "вихід на нагляд (UV/OV)", size=10, color=POS, anchor="middle"))

    # підтяжка на спільному виході ALL_GOOD/RESET
    rx0 = sx+sw_/2
    f.append(line(rx0, sy+sh, rx0, 372, color=INK, sw=2))
    f.append(circle(rx0, 372, 6, fill=BG, stroke=INK, sw=2))
    f.append(text(rx0, 392, "RESET → процесору", size=11, color=INK))

    f.append(fitbox(250, 352, 200, 34, "EN — назовні; вихід шини —\nназад на нагляд", size=10.5,
                    fill="#f4f6f8", stroke=MUTED, color=INK))
    render(os.path.join(IMG, "seq-wiring.svg"), W, H, *f)


# ── 10. Часова діаграма: програмований пуск і гасіння у зворотному порядку ────
def fig_seq_timing():
    W, H = 720, 420
    f = []
    f.append(text(W/2, 26, "Програма розпорядника: пуск по черзі, гасіння — навспак", size=15, bold=True))

    ox, oy, w = 90, 40, 540          # спільна вісь часу
    rails = [("ядро 0.9 В", FIELD, 70),
             ("виводи 1.8 В", NEG, 150),
             ("I/O 3.3 В", POS, 230)]
    rh = 34
    # часові межі подій (частки ширини)
    t_on  = [0.10, 0.22, 0.34]       # моменти увімкнення
    t_off = [0.86, 0.74, 0.62]       # моменти гасіння (зворотні)

    f.append(line(ox, 300, ox+w, 300, color=INK, sw=1.6))  # вісь t
    f.append(text(ox+w+6, 304, "t", size=12, color=INK))
    # вертикальні маркери фаз
    f.append(line(ox+w*0.45, 50, ox+w*0.45, 300, color="#cccccc", sw=1.2, dash="4,4"))
    f.append(text(ox+w*0.45, 318, "усі шини в нормі → ALL_GOOD↑", size=10.5, color=MUTED))
    f.append(line(ox+w*0.55, 50, ox+w*0.55, 300, color="#cccccc", sw=1.2, dash="4,4"))

    for i, (nm, col, yy) in enumerate(rails):
        f.append(text(ox-8, yy+rh*0.7, nm, size=11.5, color=col, anchor="end", bold=True))
        x_on  = ox + w*t_on[i]
        x_off = ox + w*t_off[i]
        # рівень-«ванна»: фронт угору, плато, фронт униз
        f.append('<polyline points="%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" '
                 'fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (ox, yy+rh, x_on, yy+rh, x_on+14, yy, x_off-14, yy, x_off, yy+rh, col))
        f.append('<polyline points="%.0f,%.0f %.0f,%.0f" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (x_off, yy+rh, ox+w, yy+rh, col))
        # номери порядку
        f.append(text(x_on+18, yy-4, "↑%d" % (i+1), size=11, color=col, anchor="start", bold=True))
        f.append(text(x_off-18, yy-4, "↓%d" % (3-i), size=11, color=col, anchor="end", bold=True))

    f.append(fitbox(ox, 340, 250, 30, "пуск: ядро → виводи → I/O", size=11.5,
                    fill="#e9f7ee", stroke=FIELD, color="#1c6b3a"))
    f.append(fitbox(ox+290, 340, 250, 30, "гасіння: I/O → виводи → ядро", size=11.5,
                    fill="#fdecea", stroke=POS, color=POS))
    f.append(fitbox(ox, 380, 540, 28,
                    "ядро вмикається першим і гасне останнім — переходи весь час зміщені безпечно",
                    size=11, fill="#f4f6f8", stroke=MUTED, color=INK))
    render(os.path.join(IMG, "seq-timing.svg"), W, H, *f)


def fig_latchup_structure():
    # Фізичний зріз кармана КМОН: де саме в кремнії сидить паразитний тиристор,
    # + той самий прилад як два BJT у петлі. Для історичної вставки hist-latchup.
    W, H = 760, 430
    f = []
    f.append(text(W/2, 26, "Де в кремнії живе паразит: зріз кармана й та сама петля", size=15, bold=True))

    # ── зліва: зріз ────────────────────────────────────────────────────────
    ox, oy = 40, 70
    sw_, sh = 360, 250
    # пластина p-типу
    f.append(rect(ox, oy+70, sw_, sh-70, fill="#f6d6d2", stroke=POS, sw=1.6, rx=4))
    f.append(text(ox+sw_-10, oy+sh-10, "p-пластина", size=12, color=POS, anchor="end", italic=True))
    # n-карман (праворуч)
    wx, ww = ox+200, 150
    f.append(rect(wx, oy+70, ww, 120, fill="#d6e0f8", stroke=NEG, sw=1.6, rx=4))
    f.append(text(wx+ww/2, oy+150, "n-карман", size=12, color=NEG, italic=True))

    # дифузії: n⁺ (nMOS витік) у пластині зліва; p⁺ (pMOS витік) у кармані
    def diff(x, lab, col, fill):
        f.append(rect(x, oy+70, 52, 26, fill=fill, stroke=col, sw=1.6, rx=3))
        f.append(text(x+26, oy+88, lab, size=12.5, color=col, bold=True))
    diff(ox+40, "n⁺", NEG, "#bcd0f6")        # витік nMOS
    diff(wx+ww-92, "p⁺", POS, "#f6c4be")     # витік pMOS

    # шини зверху
    f.append(line(ox, oy+20, ox+sw_, oy+20, color=NEG, sw=2.6))
    f.append(text(ox-6, oy+25, "GND", size=12, color=NEG, anchor="end", bold=True))
    f.append(line(ox, oy+44, ox+sw_, oy+44, color=POS, sw=2.6))
    f.append(text(ox-6, oy+49, "V+", size=12, color=POS, anchor="end", bold=True))
    # n⁺ → GND, p⁺ → V+
    f.append(line(ox+66, oy+70, ox+66, oy+20, color=NEG, sw=1.6))
    f.append(line(wx+ww-66, oy+70, wx+ww-66, oy+44, color=POS, sw=1.6))

    # чотири шари позначка p-n-p-n уздовж шляху
    f.append(text(ox+sw_/2, oy+sh+22, "уздовж: p⁺ — n-карман — p-пластина — n⁺  =  тиристор",
                  size=11.5, color=INK))

    # шунтувальні опори Rк (карман→V+) і Rп (пластина→GND) — головна ручка
    f.append(text(wx+ww+6, oy+110, "Rₖ", size=12, color=NEG, anchor="start", bold=True))
    f.append(line(wx+ww, oy+96, wx+ww+30, oy+96, color=NEG, sw=1.4, dash="3,3"))
    f.append(text(ox+sw_*0.62, oy+sh-6, "Rₚ", size=12, color=POS, anchor="middle", bold=True))

    # ── справа: дві BJT у петлі ─────────────────────────────────────────────
    bx = 600
    b1, _, _ = textbox(bx, 150, "p-n-p", size=14, fill="#fdecea", stroke=POS, color=POS, bold=True, min_w=92)
    b2, _, _ = textbox(bx, 255, "n-p-n", size=14, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True, min_w=92)
    f.append(b1); f.append(b2)
    f.append(line(bx, 90, bx, 132, color=POS, sw=2)); f.append(text(bx, 84, "V+", size=11, color=POS, bold=True))
    f.append(line(bx, 273, bx, 320, color=NEG, sw=2)); f.append(text(bx, 334, "GND", size=11, color=NEG, bold=True))
    f.append(arrow(bx+50, 160, bx+50, 245, color=INK, sw=1.8))
    f.append(arrow(bx-50, 245, bx-50, 160, color=INK, sw=1.8))
    f.append(text(bx, 205, "колектор →", size=10.5, color=MUTED))
    f.append(text(bx, 219, "база іншого", size=10.5, color=MUTED))

    # умова замикання
    f.append(fitbox(ox+10, oy+sh+40, sw_-20, 30, "паразит замкнеться, коли βₙₚₙ·βₚₙₚ > 1",
                    size=12.5, fill="#fff6e5", stroke="#e0a800", color="#7a5b00", bold=True))
    f.append(fitbox(bx-95, oy+sh+40, 190, 30, "ліки: Rₖ, Rₚ ↓ і β ↓",
                    size=11.5, fill="#e9f7ee", stroke=FIELD, color="#1c6b3a"))
    render(os.path.join(IMG, "latchup-structure.svg"), W, H, *f)


if __name__ == "__main__":
    fig_latchup()
    fig_latchup_structure()
    fig_backpower()
    fig_monotonic()
    fig_methods()
    fig_iso_block()
    fig_iso_ioff()
    fig_iso_place()
    fig_seq_block()
    fig_seq_wiring()
    fig_seq_timing()
    print("done:", os.listdir(IMG))
