# -*- coding: utf-8 -*-
# Фігури для вставки hist-flyby.md — історія переходу double-T → fly-by й
# народження вирівнювання. Окремий файл, щоб не чіпати figs.py теми.
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── timeline: лінія поколінь DDR і де JEDEC переламав топологію ────────────────
# Ідея: швидкість росте з кожним поколінням; на DDR3 (2007) double-T перестало
# тримати сигнал — JEDEC перейшов на fly-by й увів вирівнювання. Це точка, де
# проблема SI стала проблемою таймінгу й переїхала в контролер.

def fig_timeline():
    W, H = 860, 360
    p = []
    ax0, ax1, ay = 70, W - 40, 150
    p.append(line(ax0, ay, ax1, ay, color=INK, sw=2.2))
    p.append(text(ax1, ay - 12, "час →", size=11, color=INK, italic=True, anchor="end"))

    # покоління: (підпис, рік, типова швидкість МТ/с, топологія, колір)
    gens = [
        ("DDR",  "2000", "200–400",   "T",      MUTED),
        ("DDR2", "2003", "400–1066",  "double-T", NEG),
        ("DDR3", "2007", "800–2133",  "fly-by", POS),
        ("DDR4", "2012", "1600–3200", "fly-by", FIELD),
        ("DDR5", "2020", "3200–8400", "fly-by", INK),
    ]
    n = len(gens)
    step = (ax1 - ax0 - 60) / (n - 1)
    xs = [ax0 + 30 + i * step for i in range(n)]

    for i, (name, year, speed, topo, col) in enumerate(gens):
        x = xs[i]
        # вузол на осі
        p.append(circle(x, ay, 6, fill=col, stroke=col, sw=2))
        # рік під віссю
        p.append(text(x, ay + 22, year, size=11, color=MUTED, bold=True))
        # назва покоління над віссю
        p.append(text(x, ay - 60, name, size=14, color=col, bold=True))
        # швидкість
        p.append(text(x, ay - 44, speed + " МТ/с", size=9, color=MUTED))
        p.append(line(x, ay - 38, x, ay - 8, color=col, sw=1.4, dash="3 3"))

    # ── переламна позначка на DDR3 ──
    x3 = xs[2]
    p.append(text(x3, ay + 56, "перелам топології", size=12, color=POS, bold=True))
    box = fitbox(x3 - 150, ay + 70, 300, 70,
                 "double-T → fly-by\nстуби стали неприйнятні; з'явилися\nwrite/read leveling — проблема SI\nпереїхала в контролер",
                 size=9, fill="#fdecea", stroke=POS, sw=1.6, color=POS, bold=False)
    p.append(box)
    p.append(arrow(x3, ay + 50, x3, ay + 8, color=POS, sw=1.8))

    # підпис двох ер під віссю стрілками
    p.append(line(xs[0], ay + 130, xs[1] + step/2, ay + 130, color=NEG, sw=1.4))
    p.append(text((xs[0] + xs[1]) / 2 + step/4, ay + 124, "ера розгалужень (стуби)", size=9, color=NEG))
    p.append(line(xs[1] + step/2 + 2, ay + 130, xs[4], ay + 130, color=FIELD, sw=1.4))
    p.append(text((xs[2] + xs[4]) / 2 + step/4, ay + 124, "ера fly-by (вирівнювання в контролері)", size=9, color=FIELD))

    p.append(text(W / 2, H - 12, "зі зростанням швидкості JEDEC переламав топологію на DDR3 — і складність перейшла з плати в контролер",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "timeline.svg"), W, H, *p,
           title="Покоління DDR: де топологію змінили й народилося вирівнювання")


# ── leveling-handshake: як DRAM сам каже контролеру, чи DQS збігся з CK ────────
# Ідея write leveling: контролер не РАХУЄ затримку, а ПИТАЄ. Він шле повільні
# імпульси DQS; чип ловить ними свій такт CK як D-вхід тригера й віддає
# результат назад по лінії даних DQ. Контролер зсуває DQS, доки не побачить
# перехід 0→1 — це і є момент, коли DQS збігся з фронтом CK у цього чипа.

def fig_leveling_handshake():
    W, H = 860, 420
    p = []

    # ── контролер ліворуч ──
    cx, cy = 70, 120
    p.append(fitbox(cx, cy, 150, 150,
                    "КОНТРОЛЕР\n\nзсуває фазу DQS\nкроками лінії\nзатримки",
                    size=11, fill="#f6f4ec", stroke=INK, sw=1.8, bold=True))

    # ── чип DRAM праворуч ──
    dx, dy = W - 230, 120
    p.append(fitbox(dx, dy, 160, 150, "", size=10,
                    fill="#eef4ff", stroke=NEG, sw=1.8))
    p.append(text(dx + 80, dy + 22, "DRAM", size=13, color=NEG, bold=True))
    # тригер усередині: D = CK, такт = DQS, Q → DQ
    fbx, fby, fbw, fbh = dx + 36, dy + 44, 90, 70
    p.append(rect(fbx, fby, fbw, fbh, fill=BG, stroke=NEG, sw=1.6))
    p.append(text(fbx + fbw/2, fby + 20, "тригер", size=10, color=NEG, bold=True))
    p.append(text(fbx + 4, fby + 40, "D ← CK", size=9, color=INK, anchor="start"))
    p.append(text(fbx + 4, fby + 56, "такт ← DQS", size=9, color=INK, anchor="start"))

    # ── стрілка 1: DQS від контролера до чипа (запит) ──
    y1 = cy + 50
    p.append(arrow(cx + 150, y1, dx, y1, color=FIELD, sw=2.2))
    p.append(text((cx + 150 + dx) / 2, y1 - 8, "повільні імпульси DQS →", size=11, color=FIELD, bold=True))
    p.append(text((cx + 150 + dx) / 2, y1 + 16, "(чип ловить ними свій CK)", size=9, color=MUTED))

    # ── стрілка 2: відповідь по DQ назад ──
    y2 = cy + 110
    p.append(arrow(dx, y2, cx + 150, y2, color=POS, sw=2.2))
    p.append(text((cx + 150 + dx) / 2, y2 + 18, "← відповідь по лінії DQ", size=11, color=POS, bold=True))
    p.append(text((cx + 150 + dx) / 2, y2 + 34, "0 = DQS рано · 1 = DQS збігся з фронтом CK", size=9, color=MUTED))

    # ── правило зупину ──
    p.append(fitbox(cx, cy + 200, W - 110, 64,
                    "Контролер зсуває DQS, доки відповідь не перемкнеться 0 → 1: саме там фронт DQS лягає на фронт CK у ЦЬОГО чипа.\nДля кожного чипа — свій зсув; так керований перекіс fly-by вимірюється апаратно, а не рахується олівцем.",
                    size=10, fill="#eafaf0", stroke=FIELD, sw=1.6, bold=False))

    p.append(text(W / 2, H - 12, "write leveling: контролер не рахує затримку, а ПИТАЄ чип — і той відповідає одним бітом по DQ",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "leveling-handshake.svg"), W, H, *p,
           title="Народження вирівнювання: чип сам каже, коли DQS збігся з тактом")


if __name__ == "__main__":
    fig_timeline()
    fig_leveling_handshake()
    print("OK: figures written to", OUT)
