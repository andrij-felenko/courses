# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Місія = індексований список команд, який автопілот проходить ──────────
def fig_lifecycle():
    W, H = 940, 430
    p = []
    p.append(text(W / 2, 30, "місію автопілот проходить крок за кроком; активна — рівно одна NAV-команда",
                  size=13, color=MUTED))

    items = [
        ("0", "TAKEOFF", "набрати\nвисоту 30 м", FILL),
        ("1", "WAYPOINT", "летіти\nдо точки A", FILL),
        ("2", "WAYPOINT", "летіти\nдо точки B", "#eaf3ff"),   # активна
        ("3", "DO_SET_SERVO", "скинути\nвантаж", "#f0f0f0"),
        ("4", "WAYPOINT", "летіти\nдо точки C", FILL),
        ("5", "RTL", "додому\nй сісти", FILL),
    ]
    n = len(items)
    bw, bh = 128, 96
    gap = (W - 40 - n * bw) / (n - 1)
    x0 = 20
    y = 150
    cx_active = None
    for i, (seq, cmd, desc, fill) in enumerate(items):
        x = x0 + i * (bw + gap)
        st = NEG if seq == "2" else LINE
        sw = 2.6 if seq == "2" else 1.6
        p.append(rect(x, y, bw, bh, fill=fill, stroke=st, sw=sw, rx=9))
        p.append(text(x + 14, y + 22, "#" + seq, size=12, color=MUTED, anchor="start", bold=True))
        p.append(text(x + bw / 2, y + 44, cmd, size=13, color=INK, bold=True))
        p.append(mtext(x + bw / 2, y + 64, desc, size=11.5, color=MUTED))
        # стрілка до наступного
        if i < n - 1:
            ax1 = x + bw
            ax2 = x + bw + gap
            p.append(arrow(ax1, y + bh / 2, ax2 - 3, y + bh / 2, color=LINE, sw=1.8))
        if seq == "2":
            cx_active = x + bw / 2

    # покажчик активної команди
    p.append(text(cx_active, y - 16, "▲ зараз тут", size=12, color=NEG, bold=True))
    p.append(text(cx_active, y + bh + 26, "проходить пункт #2;\nяк дійде — індекс #3",
                  size=11.5, color=NEG))

    # DO-команда — не рухає, виконується миттєво «збоку»
    do_x = x0 + 3 * (bw + gap)
    p.append(line(do_x + bw / 2, y + bh, do_x + bw / 2, y + bh + 40, color=MUTED, sw=1.3, dash="4,3"))
    p.append(text(do_x + bw / 2, y + bh + 58, "DO-команда не веде —\nспрацьовує й пропускається",
                  size=11, color=MUTED))

    # нижня смуга — де живе цей список
    yb = 360
    b, bwd, bhd = textbox(W / 2, yb, "цей список лежить у пам'яті автопілота; GCS завантажив його заздалегідь\nпо MAVLink; у польоті борт лише крокує індексом — без зв'язку із землею",
                          size=12, pad=12, fill="#f7faf7", stroke=FIELD, color=INK)
    p.append(b)
    return render(os.path.join(OUT, "mission-lifecycle.svg"), W, H, *p)


# ── 2. Один кістяк місії — чотири платформи; що змінюється ───────────────────
def fig_platform_fork():
    W, H = 940, 470
    p = []
    p.append(text(W / 2, 30, "той самий кістяк «зліт → маршрут → дія → повернення» — під кожну платформу", size=13, color=MUTED))

    rows = [
        ("🏠 дім", "стаціонарний вузол",
         ["немає зльоту й руху", "«маршрут» = розклад станів", "«повернення» = безпечний режим"],
         "#f7faf7", FIELD),
        ("🚗 ровер", "наземний (UGV)",
         ["зльоту немає — одразу їде", "маршрут по землі, обхід перешкод", "RTL = повернутися й спинитися"],
         FILL, LINE),
        ("🚁 коптер", "мультиротор",
         ["TAKEOFF вертикально", "висить у точці, точна посадка", "RTL: набрати, долетіти, сісти"],
         "#eaf3ff", NEG),
        ("✈️ літак", "нерухоме крило",
         ["зліт з рук / кидком / смугою", "не висить — кружляє (loiter)", "RTL: коло над домом, потім захід"],
         "#fdecea", POS),
    ]
    y = 70
    rh = 88
    lw = 168      # ліва колонка
    dw = W - 40 - lw
    for name, kind, diffs, fill, stroke in rows:
        x = 20
        p.append(rect(x, y, lw, rh, fill=fill, stroke=stroke, sw=1.8, rx=9))
        p.append(text(x + lw / 2, y + 34, name, size=16, color=INK, bold=True))
        p.append(text(x + lw / 2, y + 58, kind, size=11.5, color=MUTED))
        # три відмінності — колонки праворуч
        xd = x + lw
        cw = dw / 3
        labels = ["зліт", "маршрут / дія", "повернення"]
        for j, d in enumerate(diffs):
            cx = xd + j * cw
            p.append(rect(cx, y, cw, rh, fill=BG, stroke="#dfe3e8", sw=1.1, rx=6))
            if y == 70:
                p.append(text(cx + cw / 2, y - 8, labels[j], size=11, color=MUTED, bold=True))
            p.append(fitbox(cx + 6, y + rh / 2 - 15, cw - 12, 30, d, size=11.5, pad=4,
                            fill=BG, stroke="none", color=INK))
        y += rh + 12
    return render(os.path.join(OUT, "platform-fork.svg"), W, H, *p)


# ── 3. Місія працює всередині захисної оболонки ─────────────────────────────
def fig_safety_envelope():
    W, H = 720, 560
    p = []
    p.append(text(W / 2, 30, "місія виконується ВСЕРЕДИНІ вкладених запобіжників", size=13, color=MUTED))

    cx = W / 2
    # концентричні рамки, зовнішня — найзагальніша
    shells = [
        (54, 60, "#fdecea", POS, "ARMING-перевірки: без «все зелено» місія взагалі не стартує"),
        (108, 120, "#fff6e6", "#e08a1e", "GEOFENCE: межа простору — за неї борт не випустять"),
        (162, 180, "#eef7ee", FIELD, "FAILSAFE: зник зв'язок / сіла батарея → перехопити"),
    ]
    y0 = 70
    for i, (inset, top, fill, stroke, label) in enumerate(shells):
        x = 20 + inset
        w = W - 2 * (20 + inset)
        y = y0 + top
        h = H - 40 - y - (top - 30 if i < 2 else 0)
        # спрощення: фіксовані висоти шарів
    # намалюємо вручну три вкладені прямокутники + ядро
    outer = (40, 60, W - 80, H - 110)
    mid = (95, 118, W - 190, H - 220)
    inner = (150, 176, W - 300, H - 330)
    core = (205, 236, W - 410, H - 430)

    p.append(rect(*outer, fill="#fdf1f0", stroke=POS, sw=1.8, rx=14))
    p.append(text(cx, outer[1] + 22, "ARMING-перевірки — без «зелено» місія не стартує", size=12.5, color=POS, bold=True))

    p.append(rect(*mid, fill="#fff8ee", stroke="#d98218", sw=1.8, rx=12))
    p.append(text(cx, mid[1] + 22, "GEOFENCE — межу простору борт не перетне", size=12.5, color="#b56c12", bold=True))

    p.append(rect(*inner, fill="#eef7ee", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(cx, inner[1] + 22, "FAILSAFE — зник лінк / сіла батарея → перехопити", size=12.5, color="#1e7d42", bold=True))

    p.append(rect(*core, fill="#eaf3ff", stroke=NEG, sw=2.4, rx=8))
    p.append(mtext(cx, core[1] + core[3] / 2 - 8, "МІСІЯ\nкроки #0…#N", size=15, color=NEG, bold=True))

    # підпис: напрям спрацювання
    p.append(text(cx, H - 22, "порушив будь-який шар → місію уриває RTL і веде додому",
                  size=12.5, color=INK, bold=True))
    return render(os.path.join(OUT, "safety-envelope.svg"), W, H, *p)


if __name__ == "__main__":
    fig_lifecycle()
    fig_platform_fork()
    fig_safety_envelope()
    print("ok")
