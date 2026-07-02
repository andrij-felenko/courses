# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Один великий проти чотирьох скромних: та сама площа, різний зиск ────────
# Ідея (правило Поллака): подвоєння площі одного ядра дає лише ~√2 швидкодії,
# а розбиття тієї самої площі на чотири ядра дає до 4× сумарної роботи —
# якщо тільки задачу є на що ділити.
def fig_tradeoff():
    W, H = 720, 340
    p = []
    p.append(text(W / 2, 26, "Той самий кремній, той самий бюджет тепла — два способи витратити", size=13, bold=True))

    # ліворуч: одне велике ядро
    lx, ly, lw, lh = 60, 70, 240, 200
    p.append(rect(lx, ly, lw, lh, fill="#fdf2f0", stroke=POS, sw=2))
    p.append(rect(lx + 30, ly + 40, lw - 60, lh - 90, fill="#fadbd6", stroke=POS, sw=1.6))
    p.append(text(lx + lw / 2, ly + lh / 2 + 4, "ОДНЕ", size=22, color=POS, bold=True))
    p.append(text(lx + lw / 2, ly + lh / 2 + 30, "велике ядро", size=13, color=INK))
    p.append(text(lx + lw / 2, ly - 10, "усе на одну потужну машину", size=11, color=MUTED))
    p.append(text(lx + lw / 2, ly + lh + 26, "вдвічі більше транзисторів →", size=11, color=INK))
    p.append(text(lx + lw / 2, ly + lh + 44, "лише ~1.4× швидше (√площі)", size=11, color=POS, bold=True))

    # праворуч: чотири малі ядра тієї самої сумарної площі
    rx, ry, rw, rh = 420, 70, 240, 200
    p.append(rect(rx, ry, rw, rh, fill="#eef6ff", stroke=NEG, sw=2))
    cw, ch = (rw - 36) / 2, (rh - 36) / 2
    for i in range(4):
        col, row = i % 2, i // 2
        ccx = rx + 12 + col * (cw + 12)
        ccy = ry + 12 + row * (ch + 12)
        p.append(rect(ccx, ccy, cw, ch, fill="#d6e6fb", stroke=NEG, sw=1.6))
        p.append(text(ccx + cw / 2, ccy + ch / 2 + 5, "ядро", size=12, color=NEG, bold=True))
    p.append(text(rx + rw / 2, ry - 10, "поділити на кілька скромних", size=11, color=MUTED))
    p.append(text(rx + rw / 2, ry + rh + 26, "чотири простіші ядра →", size=11, color=INK))
    p.append(text(rx + rw / 2, ry + rh + 44, "до 4× роботи, якщо є що ділити", size=11, color=NEG, bold=True))

    # знак «=» між площами
    p.append(text(W / 2, ly + lh / 2 - 8, "=", size=30, color=MUTED, bold=True))
    p.append(text(W / 2, ly + lh / 2 + 18, "та сама", size=10, color=MUTED))
    p.append(text(W / 2, ly + lh / 2 + 32, "площа", size=10, color=MUTED))

    render(os.path.join(OUT, "tradeoff.svg"), W, H, *p)


# ── 2. SMP проти AMP: як пов'язані ядра ───────────────────────────────────────
# SMP: однакові ядра, спільна памʼять, одна ОС бачить усіх — задачі мігрують.
# AMP: різні ядра, кожне зі своєю роллю (і часто памʼяттю), звʼязок повідомленнями.
def fig_smp_amp():
    W, H = 720, 380
    p = []

    # ── SMP ліворуч ──
    p.append(text(185, 30, "SMP — симетрична", size=14, bold=True, color=FIELD))
    p.append(text(185, 48, "однакові ядра, спільна памʼять, одна ОС", size=10, color=MUTED))
    for i in range(4):
        cx = 55 + i * 75
        p.append(rect(cx, 70, 62, 50, fill="#e7f7ee", stroke=FIELD, sw=1.8))
        p.append(text(cx + 31, 92, "ядро", size=11, color=FIELD, bold=True))
        p.append(text(cx + 31, 108, str(i), size=10, color=MUTED))
        p.append(line(cx + 31, 120, cx + 31, 150, color=INK, sw=1.5))
    # спільна шина
    p.append(line(70, 150, 355, 150, color=INK, sw=2.2))
    # спільна памʼять
    p.append(rect(120, 175, 180, 46, fill="#f4f6f8", stroke=INK, sw=1.8))
    p.append(text(210, 195, "спільна памʼять", size=12, bold=True))
    p.append(text(210, 211, "усі ядра — ті самі адреси", size=9, color=MUTED))
    # одна ОС
    p.append(rect(95, 245, 230, 44, fill="#e7f7ee", stroke=FIELD, sw=1.6))
    p.append(text(210, 264, "одна ОС на всіх", size=12, bold=True, color=FIELD))
    p.append(text(210, 280, "задача може піти на будь-яке вільне ядро", size=9, color=MUTED))

    # роздільник
    p.append(line(375, 60, 375, 300, color=MUTED, sw=1, dash="4,4"))

    # ── AMP праворуч ──
    p.append(text(545, 30, "AMP — асиметрична", size=14, bold=True, color=POS))
    p.append(text(545, 48, "різні ядра, кожне зі своєю роллю", size=10, color=MUTED))
    # велике ядро + свій світ
    p.append(rect(410, 70, 120, 50, fill="#fdf2f0", stroke=POS, sw=1.8))
    p.append(text(470, 90, "потужне ядро", size=11, color=POS, bold=True))
    p.append(text(470, 106, "застосунок, ОС", size=9, color=MUTED))
    p.append(rect(410, 135, 120, 36, fill="#f4f6f8", stroke=INK, sw=1.5))
    p.append(text(470, 157, "своя памʼять", size=10))
    p.append(line(470, 120, 470, 135, color=INK, sw=1.4))

    # мале ядро + свій світ
    p.append(rect(560, 70, 120, 50, fill="#eef6ff", stroke=NEG, sw=1.8))
    p.append(text(620, 90, "мале ядро", size=11, color=NEG, bold=True))
    p.append(text(620, 106, "радіо / реальний час", size=9, color=MUTED))
    p.append(rect(560, 135, 120, 36, fill="#f4f6f8", stroke=INK, sw=1.5))
    p.append(text(620, 157, "своя памʼять", size=10))
    p.append(line(620, 120, 620, 135, color=INK, sw=1.4))

    # звʼязок повідомленнями
    p.append(arrow(535, 95, 555, 95, color=INK, sw=1.8))
    p.append(arrow(555, 108, 535, 108, color=INK, sw=1.8))
    p.append(text(545, 200, "спілкуються", size=10, color=INK, bold=True))
    p.append(text(545, 216, "повідомленнями,", size=10, color=INK))
    p.append(text(545, 232, "не спільною памʼяттю", size=10, color=INK))

    render(os.path.join(OUT, "smp-amp.svg"), W, H, *p)


# ── 3. Закон Амдала: скільки не додавай ядер, послідовне тримає ──────────────
# Крива прискорення S = 1/((1-p) + p/N) для кількох часток p, що паралеляться.
def fig_amdahl():
    W, H = 720, 400
    p = []
    p.append(text(W / 2, 26, "Закон Амдала: стеля прискорення тримається послідовною часткою", size=13, bold=True))

    # осі
    ox, oy = 90, 330            # початок координат
    ax_w, ax_h = 560, 250
    p.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.6))          # X
    p.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.6))          # Y
    p.append(text(ox + ax_w / 2, oy + 40, "кількість ядер N", size=11, color=INK))
    p.append(text(ox - 60, oy - ax_h / 2, "прискорення", size=11, color=INK))
    p.append(text(ox - 60, oy - ax_h / 2 + 15, "(у скільки разів)", size=9, color=MUTED))

    # шкала X: 1..16 ядер (лог-подібно, але візьмемо рівномірно 1,2,4,8,16)
    xs_nodes = [1, 2, 4, 8, 16]
    def X(n):
        # рівномірно за індексом вузла
        idx = xs_nodes.index(n) if n in xs_nodes else 0
        return ox + idx * (ax_w / (len(xs_nodes) - 1))
    for n in xs_nodes:
        p.append(line(X(n), oy, X(n), oy + 5, color=INK, sw=1.2))
        p.append(text(X(n), oy + 20, str(n), size=10, color=MUTED))

    # шкала Y: 1..16
    ymax = 16
    def Y(s):
        return oy - (s - 1) / (ymax - 1) * ax_h
    for s in [1, 2, 4, 8, 16]:
        p.append(line(ox - 5, Y(s), ox, Y(s), color=INK, sw=1.2))
        p.append(text(ox - 16, Y(s) + 4, str(s), size=10, color=MUTED))
    # пунктир ідеалу (лінійне прискорення N=S)
    ideal = [(X(n), Y(min(n, ymax))) for n in xs_nodes]
    for a, b in zip(ideal, ideal[1:]):
        p.append(line(a[0], a[1], b[0], b[1], color=MUTED, sw=1.3, dash="5,4"))
    p.append(text(X(8) + 4, Y(9) - 6, "ідеал (S = N)", size=10, color=MUTED, italic=True))

    # криві Амдала для p = 0.95, 0.75, 0.50
    def amdahl(pp, n):
        return 1.0 / ((1 - pp) + pp / n)
    curves = [(0.95, NEG, "95% паралельно"),
              (0.75, FIELD, "75%"),
              (0.50, POS, "50%")]
    for pp, col, lbl in curves:
        pts = [(X(n), Y(min(amdahl(pp, n), ymax))) for n in xs_nodes]
        for a, b in zip(pts, pts[1:]):
            p.append(line(a[0], a[1], b[0], b[1], color=col, sw=2.4))
        for a in pts:
            p.append(circle(a[0], a[1], 3.2, fill=col, stroke=col, sw=1))
        last = pts[-1]
        p.append(text(last[0] - 6, last[1] - 10, lbl, size=10, color=col, bold=True, anchor="end"))

    # стеля 50%: горизонтальна риска на S=2
    p.append(line(ox, Y(2), ox + ax_w, Y(2), color=POS, sw=1, dash="2,4"))
    p.append(text(ox + ax_w, Y(2) - 6, "стеля ×2", size=9, color=POS, anchor="end"))

    render(os.path.join(OUT, "amdahl.svg"), W, H, *p)


# ── 4. Поворот індустрії: від першого дводкового до настільного столу ─────────
# Часова вісь: POWER4 (2001, сервер) → стіна потужності (2004, скасовані чипи) →
# два ядра приходять на десктоп (2005). Показує, що поворот стався ЧЕРЕЗ стіну.
def fig_turn_timeline():
    W, H = 760, 340
    p = []
    p.append(text(W / 2, 26, "Поворот до багатьох ядер: серверний первісток, стіна потужності, десктоп", size=13, bold=True))

    # горизонтальна вісь часу
    ax_y = 150
    x0, x1 = 60, 700
    p.append(line(x0, ax_y, x1, ax_y, color=INK, sw=2))
    p.append(arrow(x1 - 2, ax_y, x1 + 6, ax_y, color=INK, sw=2))
    p.append(text(x1 + 2, ax_y + 22, "час", size=10, color=MUTED, anchor="end"))

    # роки-вузли: (рік, x, колір, зверху?)
    def X(frac):
        return x0 + frac * (x1 - x0 - 20)

    nodes = [
        (X(0.02),  "жовт. 2001", "IBM POWER4", "перший неембедед-чип\nіз двома ядрами (сервер)", NEG, True),
        (X(0.46),  "трав.–жовт. 2004", "СТІНА ПОТУЖНОСТІ", "скасовано Tejas і 4-ГГц P4:\nтепло вперлося у стелю", POS, False),
        (X(0.80),  "трав. 2005", "два ядра на столі", "Pentium D · Athlon 64 X2 —\nдесктоп стає багатоядерним", FIELD, True),
    ]
    for x, yr, title, sub, col, above in nodes:
        p.append(circle(x, ax_y, 6, fill=col, stroke=col, sw=2))
        p.append(line(x, ax_y, x, ax_y - 34 if above else ax_y + 34, color=col, sw=1.4, dash="3,3"))
        ty = ax_y - 40 if above else ax_y + 46
        p.append(text(x, ty, yr, size=11, color=col, bold=True))
        p.append(text(x, ty + (-16 if above else 16), title, size=12, color=INK, bold=True))
        # підпис-пояснення у два рядки
        lines = sub.split("\n")
        base = ty + (-34 if above else 34)
        for i, ln in enumerate(lines):
            p.append(text(x, base + i * 14, ln, size=9.5, color=MUTED))

    # дуга-причинність: від стіни до десктопу («тому й повернули»)
    p.append(text(W / 2, H - 24, "Стіна 2004-го — причина: одиноке ядро вже не пришвидшити, тож ту саму площу пустили на кілька ядер",
                  size=10.5, color=INK, italic=True))

    render(os.path.join(OUT, "turn-timeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_tradeoff()
    fig_smp_amp()
    fig_amdahl()
    fig_turn_timeline()
    print("figs done")
