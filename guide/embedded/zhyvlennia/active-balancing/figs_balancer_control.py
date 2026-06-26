# -*- coding: utf-8 -*-
"""Фігури до вставки «Керування балансиром у прошивці» (proj-balancer-control).
Окремий генератор у тій самій теці теми; вивід — у ./img/.
Запуск:  python figs_balancer_control.py
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

HOT  = POS     # гаряче / повна / небезпека
COLD = NEG     # холодне / слабша
OK   = FIELD   # зрівняне / дозволено


# ── 1. Кінцевий автомат балансира ────────────────────────────────────────────
def fig_fsm():
    """IDLE → MEASURE → BALANCE → COOLDOWN і спільний аварійний вихід у IDLE.
    Чому петля, а не пряма лінія: вимір треба повторювати, а перегрів/захист
    будь-коли скидають усе в безпечний спокій."""
    W, H = 820, 430
    f = [text(W / 2, 28, "Кінцевий автомат балансира: чотири стани в петлі", size=16, bold=True)]

    # координати чотирьох станів (ромб петлі)
    nodes = {
        "IDLE":     (150, 230, "IDLE", "спокій:\nреле/ключі вимкнено", OK),
        "MEASURE":  (410, 110, "MEASURE", "зняти напруги,\nоцінити SOC і розкид", MUTED),
        "BALANCE":  (670, 230, "BALANCE", "перенос/розряд\nз тримання струму", HOT),
        "COOLDOWN": (410, 350, "COOLDOWN", "силовий вузол\nохолоджується", COLD),
    }
    rw, rh = 150, 64

    def box(key):
        cx, cy, title, body, col = nodes[key]
        out = rect(cx - rw / 2, cy - rh / 2, rw, rh, fill="#fff", stroke=col, sw=2.2, rx=10)
        out += ('<rect x="%.1f" y="%.1f" width="%.1f" height="20" rx="10" fill="%s" fill-opacity="0.15"/>'
                % (cx - rw / 2, cy - rh / 2, rw, col))
        out += text(cx, cy - rh / 2 + 15, title, size=12.5, color=col, bold=True)
        out += mtext(cx, cy + 2, body, size=9, color=INK, lh=1.2)
        return out

    for k in nodes:
        f.append(box(k))

    def edge(a, b, label, col=INK, off=0.0):
        ax, ay = nodes[a][0], nodes[a][1]
        bx, by = nodes[b][0], nodes[b][1]
        dx, dy = bx - ax, by - ay
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        # відступ від країв рамок (приблизно)
        sa = rw * 0.42
        sb = rw * 0.42
        x1, y1 = ax + ux * sa, ay + uy * sa
        x2, y2 = bx - ux * sb, by - uy * sb
        f.append(arrow(x1, y1, x2, y2, color=col, sw=2.2))
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        tb, tw, th = textbox(mx, my + off, label, size=9, pad=4, fill="#fff",
                             stroke=col, sw=1.0, color=col)
        f.append(tb)

    edge("IDLE", "MEASURE", "період\nспрацював", col=OK)
    edge("MEASURE", "BALANCE", "розкид ≥ START\nі дозволено", col=HOT)
    edge("BALANCE", "COOLDOWN", "розкид ≤ STOP\nабо t_max / гаряче", col=COLD)
    edge("COOLDOWN", "IDLE", "охолов /\nвитримка минула", col=MUTED)
    # коротке замикання MEASURE→IDLE (балансувати не треба) — окремою дугою ліворуч,
    # щоб не накладатися на антипаралельну IDLE→MEASURE
    f.append('<path d="M %.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" '
             'stroke-width="2.0" marker-end="url(#arrow)"/>'
             % (348, 128, 210, 150, 158, 208, MUTED))
    tb, tw, th = textbox(214, 132, "розкид < START\n(нема за що)", size=9, pad=4,
                         fill="#fff", stroke=MUTED, sw=1.0, color=MUTED)
    f.append(tb)

    # спільний аварійний вихід: червона дуга з BALANCE назад в IDLE
    f.append('<path d="M %.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" '
             'stroke-width="2.4" stroke-dasharray="6 4" marker-end="url(#arrow)"/>'
             % (670, 200, 410, 40, 195, 205, HOT))
    f.append(text(410, 70, "захист сказав «стоп» → негайно в IDLE", size=10, color=HOT, bold=True))

    f.append(fitbox(60, 392, 700, 30,
                    "Вимір повторюється щоперіоду; балансуємо лише коли є за що і поки тепло дозволяє; "
                    "будь-яке вето монітора-захисту — миттєвий відкат у спокій.",
                    size=10, fill="#f4f6f8", stroke=MUTED, sw=1.2))
    render(os.path.join(IMG, "fsm.svg"), W, H, *f)


# ── 2. Критерій вирівнювання залежить від форми кривої хімії ──────────────────
def fig_criterion():
    """Похила Li-ion: напруга інформативна скрізь → балансуй за напругою.
    Пласка LiFePO4: на плато напруга «сліпа» → балансуй за SOC або в зламі."""
    W, H = 820, 410
    f = [text(W / 2, 28, "За чим вирівнювати: форма кривої вирішує", size=16, bold=True)]

    def axes(ox, oy, pw, ph, title, col):
        out = [line(ox, oy, ox + pw, oy, color=INK, sw=1.4),
               line(ox, oy, ox, oy - ph, color=INK, sw=1.4),
               text(ox + pw / 2, oy + 30, "заряд, що лишився →", size=9.5, color=MUTED),
               text(ox - 6, oy - ph - 6, "U комірки", size=9.5, color=MUTED, anchor="end"),
               text(ox + pw / 2, oy - ph - 8, title, size=12.5, color=col, bold=True)]
        return out

    # ── ліворуч: похила Li-ion ──
    ox, oy, pw, ph = 80, 300, 300, 190
    f += axes(ox, oy, pw, ph, "Li-ion: похила крива", HOT)
    pts = []
    N = 60
    for k in range(N + 1):
        s = k / N                     # від порожнього (0) до повного (1)
        # плавний нахил від 3.0 до 4.2 з легким S
        u = 3.0 + 1.2 * (0.5 - 0.5 * math.cos(math.pi * s))
        x = ox + s * pw
        y = oy - (u - 2.9) / (4.3 - 2.9) * ph
        pts.append((x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" '
             'stroke-linecap="round"/>' % (" ".join("%.1f,%.1f" % p for p in pts), HOT))
    # дві комірки з невеликою ΔU посередині — добре видно по U
    sx = 0.5
    ux = 3.0 + 1.2 * (0.5 - 0.5 * math.cos(math.pi * sx))
    yx = oy - (ux - 2.9) / (4.3 - 2.9) * ph
    f.append(circle(ox + sx * pw, yx, 4, fill=HOT, stroke=HOT))
    f.append(circle(ox + (sx + 0.10) * pw, oy - (3.0 + 1.2 * (0.5 - 0.5 * math.cos(math.pi * (sx + 0.10))) - 2.9) / (4.3 - 2.9) * ph, 4, fill=COLD, stroke=COLD))
    f.append(line(ox + sx * pw, yx, ox + sx * pw, yx - 28, color=OK, sw=1.2, dash="3 3"))
    f.append(text(ox + sx * pw + 4, yx - 32, "ΔU помітна", size=9, color=OK, anchor="start", bold=True))
    f.append(fitbox(ox - 10, oy + 44, pw + 20, 38,
                    "Напруга чесно стежить за зарядом скрізь —\nбалансуй за напругою (краще на крутому верху).",
                    size=9.5, fill="#fdf3f2", stroke=HOT, sw=1.2))

    # ── праворуч: пласка LiFePO4 ──
    ox2, oy2 = 460, 300
    f += axes(ox2, oy2, pw, ph, "LiFePO4: плато + злам", COLD)
    pts2 = []
    for k in range(N + 1):
        s = k / N
        # різкий старт, довге плато ~3.3, різкий злам угору в кінці
        if s < 0.08:
            u = 2.9 + (3.25 - 2.9) * (s / 0.08)
        elif s < 0.9:
            u = 3.25 + 0.10 * ((s - 0.08) / 0.82)
        else:
            u = 3.35 + (3.6 - 3.35) * ((s - 0.9) / 0.10)
        x = ox2 + s * pw
        y = oy2 - (u - 2.9) / (4.3 - 2.9) * ph
        pts2.append((x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" '
             'stroke-linecap="round"/>' % (" ".join("%.1f,%.1f" % p for p in pts2), COLD))
    # на плато дві комірки з тією ж ΔSOC дають майже однакову U → «сліпо»
    s1, s2 = 0.45, 0.62
    u_p = 3.25 + 0.10 * ((0.5 - 0.08) / 0.82)
    y_p = oy2 - (u_p - 2.9) / (4.3 - 2.9) * ph
    f.append(circle(ox2 + s1 * pw, y_p, 4, fill=HOT, stroke=HOT))
    f.append(circle(ox2 + s2 * pw, y_p - 1, 4, fill=COLD, stroke=COLD))
    f.append(line(ox2 + s1 * pw, y_p, ox2 + s2 * pw, y_p, color=MUTED, sw=1.0, dash="2 2"))
    f.append(text((ox2 + (s1 + s2) / 2 * pw), y_p - 8, "однакова U, різний заряд", size=8.5, color=MUTED, bold=True))
    # позначити злам у кінці
    f.append(circle(ox2 + 0.95 * pw, oy2 - (3.475 - 2.9) / (4.3 - 2.9) * ph, 4, fill=OK, stroke=OK))
    f.append(text(ox2 + 0.95 * pw, oy2 - (3.475 - 2.9) / (4.3 - 2.9) * ph - 10, "злам", size=9, color=OK, bold=True))
    f.append(fitbox(ox2 - 10, oy2 + 44, pw + 20, 38,
                    "На плато напруга «сліпа» (≈0.09 В на 20–80%) —\nбалансуй за SOC, а напругу довіряй лише в зламі.",
                    size=9.5, fill="#eaf0fd", stroke=COLD, sw=1.2))
    render(os.path.join(IMG, "criterion.svg"), W, H, *f)


# ── 3. Три шари керування + хто має право вето ────────────────────────────────
def fig_layers():
    """Рішення (мозок) → силовий вузол (м'язи) → монітор-захист (вето).
    Балансир ніколи не сперечається із захистом; перегрів силового вузла —
    окремий стоп-кран усередині балансира."""
    W, H = 820, 420
    f = [text(W / 2, 28, "Три шари: мозок, м'язи і право вето", size=16, bold=True)]

    # шар 1: рішення
    bx, by, bw, bh = 60, 56, 700, 78
    f.append(rect(bx, by, bw, bh, fill="#fff", stroke=MUTED, sw=2, rx=10))
    f.append(text(bx + 16, by + 22, "1 · Рішення (логіка балансира)", size=12.5, color=INK, bold=True, anchor="start"))
    f.append(mtext(bx + bw / 2, by + 46, "знайти найповнішу й найслабшу за ПРАВИЛЬНИМ критерієм (U чи SOC за хімією) ·\n"
                  "увімкнути перенос із гістерезисом · обрати напрям (заряд / розряд)",
                  size=9.5, color=INK, lh=1.25))

    # шар 2: силовий вузол
    by2 = 158
    f.append(rect(bx, by2, bw, bh, fill="#fff", stroke=HOT, sw=2, rx=10))
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="22" rx="10" fill="%s" fill-opacity="0.12"/>'
             % (bx, by2, bw, HOT))
    f.append(text(bx + 16, by2 + 16, "2 · Силовий вузол (ключі, котушка/трансформатор, балансувальні резистори)",
                  size=12, color=HOT, bold=True, anchor="start"))
    f.append(mtext(bx + bw / 2, by2 + 48, "тримає заданий струм переносу · має ВЛАСНИЙ датчик температури ·\n"
                  "перегрівся → сам просить COOLDOWN, не чекаючи зовнішнього дозволу",
                  size=9.5, color=INK, lh=1.25))

    # шар 3: монітор-захист з правом вето
    by3 = 260
    f.append(rect(bx, by3, bw, bh, fill="#fff", stroke=COLD, sw=2.4, rx=10))
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="22" rx="10" fill="%s" fill-opacity="0.12"/>'
             % (bx, by3, bw, COLD))
    f.append(text(bx + 16, by3 + 16, "3 · Монітор-захист комірок  (ПРАВО ВЕТО — стоїть над усіма)",
                  size=12, color=COLD, bold=True, anchor="start"))
    f.append(mtext(bx + bw / 2, by3 + 48, "стежить за межами U, I, T кожної комірки · будь-яке порушення →\n"
                  "балансир НЕГАЙНО в IDLE; захист завжди важить більше за вирівнювання",
                  size=9.5, color=INK, lh=1.25))

    # стрілки команд униз і вето вгору
    f.append(arrow(180, by + bh, 180, by2, color=INK, sw=2))
    f.append(text(150, (by + bh + by2) / 2 + 4, "команда", size=9, color=INK, anchor="end"))
    f.append(arrow(180, by2 + bh, 180, by3, color=INK, sw=2))
    # вето: червона стрілка знизу аж нагору
    f.append('<path d="M %.0f %.0f C %.0f %.0f %.0f %.0f %.0f %.0f" fill="none" stroke="%s" '
             'stroke-width="2.6" marker-end="url(#arrow)"/>'
             % (650, by3, 770, by3 - 30, 770, by + 20, 660, by + 8, COLD))
    f.append(text(700, (by + by3) / 2, "ВЕТО ↑", size=11, color=COLD, bold=True))

    f.append(fitbox(60, 350, 700, 50,
                    "Балансир — це лише шар 1, що командує шаром 2. Він НІКОЛИ не сперечається із шаром 3: "
                    "коли захист каже «стоп», балансування зупиняється першим. Перегрів власне силового вузла — "
                    "окремий внутрішній стоп-кран (шар 2), а не привід чекати команди ззовні.",
                    size=10, fill="#f4f6f8", stroke=MUTED, sw=1.2))
    render(os.path.join(IMG, "layers.svg"), W, H, *f)


if __name__ == "__main__":
    fig_fsm()
    fig_criterion()
    fig_layers()
    print("OK: 3 figures ->", IMG)
