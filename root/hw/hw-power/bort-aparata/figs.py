# -*- coding: utf-8 -*-
"""Фігури для теми «Борт апарата: 12/24 В, скидання навантаження, холодний пуск».
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *  # noqa: E402,F403

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def pline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ""
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (" ".join("%.1f,%.1f" % p for p in pts), color, sw, d))


def gnd(cx, cy):
    return (line(cx, cy, cx, cy + 6, color=INK, sw=2) +
            line(cx - 12, cy + 6, cx + 12, cy + 6, color=INK, sw=2) +
            line(cx - 7, cy + 11, cx + 7, cy + 11, color=INK, sw=2) +
            line(cx - 2, cy + 16, cx + 2, cy + 16, color=INK, sw=2))


# ── 1. Профіль холодного пуску (Cold Crank) ──────────────────────────────────
def fig_cold_crank():
    """Профіль напруги при холодному пуску двигуна (ISO 16750-2)."""
    W, H = 940, 500
    f = []

    ox, oy = 90, 410
    axW, axH = 780, 320

    # Осі
    f.append(arrow(ox, oy, ox, oy - axH - 20, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox + axW + 20, oy, color=INK, sw=1.8))
    f.append(text(ox - 10, oy - axH - 12, "Напруга на клемах (В)", size=13, color=INK, anchor="start", bold=True))
    f.append(text(ox + axW + 15, oy + 22, "Час (t)", size=13, color=INK, anchor="end", bold=True))

    def Y(v):
        return oy - axH * (v / 16.0)

    # Горизонтальні рівні напруги
    for v, lbl, col in ((14.4, "14.4 В (генератор)", MUTED),
                        (12.0, "12.0 В (номінал АКБ)", MUTED),
                        (6.0, "6.0 В (прокручування)", MUTED),
                        (3.2, "3.2 В (пусковий зрив)", POS)):
        y_pos = Y(v)
        f.append(line(ox, y_pos, ox + axW, y_pos, color=col, sw=1.1, dash="5 5"))
        f.append(text(ox - 12, y_pos + 4, lbl, size=11.5, color=col, anchor="end", bold=(v == 3.2)))

    # Небезпечна зона перезавантаження
    f.append(rect(ox + 1, Y(6.0), axW - 2, Y(0) - Y(6.0), fill="#fdecea", stroke="none"))
    f.append(text(ox + axW - 20, Y(2.0), "Зона перезавантаження мікроконтролерів (Brownout / UVLO)",
                  size=12, color=POS, anchor="end", bold=True))

    # Побудова профілю напруги
    pts = []
    # Фаза 0: до пуску (12.0 В)
    x0 = ox
    x1 = ox + 60
    for xx in range(int(x0), int(x1)):
        pts.append((xx, Y(12.0)))

    # Фаза 1: миттєвий зрив (з 12.0 до 3.2 В за кілька мс)
    x2 = x1 + 18
    pts.append((x2, Y(3.2)))

    # Фаза 2: утримання на дні зриву (5–15 мс)
    x3 = x2 + 30
    pts.append((x3, Y(3.2)))

    # Фаза 3: підйом до плато прокручування (6.0 В)
    x4 = x3 + 25
    pts.append((x4, Y(6.0)))

    # Фаза 4: прокручування колінвала стартером з компресійними пульсаціями (синусоїда 10–50 Гц)
    x5 = x4 + 380
    for xx in range(int(x4), int(x5)):
        t_rel = (xx - x4) / 25.0
        # наростання середнього рівня від 6.0 до 8.5 В під час пуску
        v_base = 6.0 + 2.5 * ((xx - x4) / 380.0)
        v_rip = 1.0 * math.sin(t_rel * 2.0 * math.pi)
        pts.append((xx, Y(v_base + v_rip)))

    # Фаза 5: двигун завівся, відновлення напруги генератором (до 14.4 В)
    x6 = x5 + 70
    for xx in range(int(x5), int(x6)):
        progress = (xx - x5) / 70.0
        v = 8.5 + (14.4 - 8.5) * (1.0 - math.exp(-progress * 4.0))
        pts.append((xx, Y(v)))

    # Фаза 6: робота від генератора (14.4 В)
    x7 = ox + axW
    for xx in range(int(x6), int(x7)):
        pts.append((xx, Y(14.4)))

    f.append(pline(pts, color=NEG, sw=3.0))

    # Позначення етапів
    f.append(line(x1, oy, x1, Y(14.0), color=MUTED, sw=1.1, dash="3 3"))
    f.append(line(x4, oy, x4, Y(14.0), color=MUTED, sw=1.1, dash="3 3"))
    f.append(line(x5, oy, x5, Y(14.0), color=MUTED, sw=1.1, dash="3 3"))

    f.append(text((x1 + x3) / 2, Y(14.8), "I. Пусковий зрив", size=11, color=POS, bold=True))
    f.append(text((x1 + x3) / 2, Y(14.8) + 16, "(3.0...4.5 В, t ≤ 20 мс)", size=10, color=POS))

    f.append(text((x4 + x5) / 2, Y(14.8), "II. Прокручування стартером з компресійними пульсаціями", size=11, color=INK, bold=True))
    f.append(text((x4 + x5) / 2, Y(14.8) + 16, "(6.0...8.5 В, пульсації ±1 В, t = 1...10 с)", size=10, color=MUTED))

    f.append(text((x5 + x7) / 2, Y(14.8), "III. Робота генератора", size=11, color=FIELD, bold=True))
    f.append(text((x5 + x7) / 2, Y(14.8) + 16, "(13.8...14.4 В)", size=10, color=FIELD))

    render(os.path.join(IMG, "cold-crank-profile.svg"), W, H, *f,
           title="Профіль напруги при холодному пуску (Cold Crank за ISO 16750-2)")
    return "cold-crank-profile"


# ── 2. Імпульс скидання навантаження (Load Dump) ──────────────────────────────
def fig_load_dump():
    """Імпульс скидання навантаження (Load Dump): некерований проти керованого."""
    W, H = 940, 500
    f = []

    ox, oy = 90, 420
    axW, axH = 780, 340

    # Осі
    f.append(arrow(ox, oy, ox, oy - axH - 20, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox + axW + 20, oy, color=INK, sw=1.8))
    f.append(text(ox - 10, oy - axH - 12, "Напруга шини V_BAT (В)", size=13, color=INK, anchor="start", bold=True))
    f.append(text(ox + axW + 15, oy + 22, "Час після розриву клеми (мс)", size=13, color=INK, anchor="end", bold=True))

    def Y(v):
        return oy - axH * (v / 120.0)

    def X(t_ms):
        return ox + (t_ms / 500.0) * axW

    # Горизонтальні рівні напруги
    for v, lbl, col in ((100.0, "100 В (пік некерованого сплеску)", POS),
                        (35.0, "35 В (лавинне обмеження генератора)", FIELD),
                        (14.4, "14.4 В (номінал генератора)", MUTED)):
        y_pos = Y(v)
        f.append(line(ox, y_pos, ox + axW, y_pos, color=col, sw=1.1, dash="5 5"))
        f.append(text(ox - 12, y_pos + 4, lbl, size=11.5, color=col, anchor="end", bold=(v > 15)))

    # Часові поділки
    for t in (0, 100, 200, 300, 400, 500):
        xx = X(t)
        f.append(line(xx, oy, xx, oy + 6, color=INK, sw=1.3))
        f.append(text(xx, oy + 20, str(t), size=11, color=MUTED))

    # Сплеск A: Некерований Load Dump (ISO 7637-2 / ISO 16750-2 Test A, пік до 100 В, спад tau = 150 мс)
    ptsA = [(X(0), Y(14.4)), (X(5), Y(100.0))]
    for t in range(5, 501, 5):
        # експоненційний спад
        v = 14.4 + (100.0 - 14.4) * math.exp(-(t - 5) / 120.0)
        ptsA.append((X(t), Y(v)))
    f.append(pline(ptsA, color=POS, sw=3.0))

    # Сплеск B: Централізовано обмежений Load Dump (ISO 16750-2 Test B, діоди генератора затискають на 35 В)
    ptsB = [(X(0), Y(14.4)), (X(2), Y(35.0))]
    for t in range(2, 501, 5):
        # утримується на рівні 35 В, поки не спаде нижче
        v_unclamped = 14.4 + (100.0 - 14.4) * math.exp(-(t - 2) / 120.0)
        v = min(35.0, v_unclamped)
        ptsB.append((X(t), Y(v)))
    f.append(pline(ptsB, color=FIELD, sw=3.0))

    # Текстові підписи кривих
    bxA, _, _ = textbox(X(120), Y(75), "Некерований Load Dump (Test A):\nU_max = 100 В, td = 40...400 мс\n(енергія вбиває класичні TVS)",
                        size=12, fill="#fdecea", stroke=POS, sw=1.8, color=POS, bold=True)
    f.append(bxA)

    bxB, _, _ = textbox(X(280), Y(42), "Керований Load Dump (Test B):\nОбмежений лавинними діодами на 35 В\n(сучасні автомобільні генератори)",
                        size=12, fill="#eafaf1", stroke=FIELD, sw=1.8, color=FIELD, bold=True)
    f.append(bxB)

    # Причина виникнення
    bx_cause, _, _ = textbox(X(370), Y(105), "Причина: раптовий розрив клеми АКБ при великому струмі заряджання.\nМагнітна енергія ротора генератора розряджається в бортову мережу.",
                             size=11.5, fill=FILL, stroke=LINE, sw=1.2, color=INK)
    f.append(bx_cause)

    render(os.path.join(IMG, "load-dump-profile.svg"), W, H, *f,
           title="Імпульс скидання навантаження (Load Dump за ISO 16750-2)")
    return "load-dump-profile"


# ── 3. Повний захисний ланцюг бортового входу ────────────────────────────────
def fig_protection_stages():
    """Архітектура вхідного захисного тракту бортової плати (5 каскадів)."""
    W, H = 960, 480
    f = []

    # Заголовок зверху
    f.append(text(W / 2, 45, "Багаторівневий захист входу 12 В / 24 В бортової плати", size=16, bold=True, color=INK))

    # 5 блоків каскадів
    stages = [
        ("I. Вхідний EMI-фільтр", "LC-ланка + синфазний дросель\nЗгладжує наносекундні\nвикиди 3a/3b та RF-завади", MUTED),
        ("II. Первинний супресор", "TVS-діод (лавинний)\nЗрізає короткі імпульси\nдо мікросекунд (Pulse 1, 2a)", POS),
        ("III. Ідеальний діод", "N-MOSFET + контролер\nЗахист від переполюсовки\nПадіння ≤ 20 мВ (замість 0.7 В)", NEG),
        ("IV. Активний Surge Stopper", "Прохідний N-MOSFET у лінійному\nрежимі: затискає вихід на 28 В\nпід час 100 В Load Dump", FIELD),
        ("V. Широкий DC-DC", "Buck-Boost перетворювач\nПрацює від 3.0 В (Crank)\nдо 36 В (Surge Stopper)", INK)
    ]

    bw = 160
    bh = 130
    gap = 26
    start_x = 35
    by = 120

    for i, (title, desc, col) in enumerate(stages):
        bx = start_x + i * (bw + gap)
        # Рамка блоку
        f.append(rect(bx, by, bw, bh, fill=FILL, stroke=col, sw=2.2, rx=8))
        f.append(text(bx + bw / 2, by + 24, title, size=12, bold=True, color=col))
        f.append(line(bx + 10, by + 34, bx + bw - 10, by + 34, color=MUTED, sw=1, dash="2 2"))
        f.append(mtext(bx + bw / 2, by + 56, desc, size=11, color=INK, lh=1.3))

        # Стрілка між блоками
        if i < len(stages) - 1:
            ax1 = bx + bw + 2
            ax2 = bx + bw + gap - 4
            ay = by + bh / 2
            f.append(arrow(ax1, ay, ax2, ay, color=LINE, sw=2.0))

    # Вхід та вихід шини
    in_x = start_x
    out_x = start_x + 4 * (bw + gap) + bw
    mid_y = by + bh / 2

    f.append(arrow(in_x - 30, mid_y, in_x - 4, mid_y, color=POS, sw=2.4))
    f.append(text(in_x - 32, mid_y - 12, "V_IN (Борт)", size=12, color=POS, bold=True, anchor="end"))
    f.append(text(in_x - 32, mid_y + 14, "-100 В ... +100 В", size=10, color=POS, anchor="end"))

    f.append(arrow(out_x + 4, mid_y, out_x + 35, mid_y, color=FIELD, sw=2.4))
    f.append(text(out_x + 40, mid_y - 12, "V_SYS (Система)", size=12, color=FIELD, bold=True, anchor="start"))
    f.append(text(out_x + 40, mid_y + 14, "Стабільні 3.3 В / 5 В", size=10, color=FIELD, anchor="start"))

    # Нижня пояснювальна таблиця реакції на загрози
    threats_y = 300
    f.append(rect(start_x, threats_y, W - 2 * start_x, 140, fill="#fafbfc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(start_x + 20, threats_y + 24, "Як захисний тракт відпрацьовує аварії борту:", size=13, bold=True, color=INK, anchor="start"))

    t_lines = [
        ("Холодний пуск (Cold Crank, 3.2 В):", "Каскади I–IV повністю відкриті (падіння < 50 мВ), каскад V (Buck-Boost) піднімає напругу до 5 В."),
        ("Скидання навантаження (Load Dump, 100 В):", "Каскад IV (Surge Stopper) тримає MOSFET у лінійному режимі, затискаючи вихід на рівні 28 В."),
        ("Переполюсовка (-12 В / -24 В):", "Каскад III (ідеальний діод) замикає затвор на витік за мікросекунди і повністю розриває коло."),
        ("Швидкі індуктивні викиди (Pulse 1, 2a, 3a/b):", "Каскад I фільтрує ВЧ-спектр, каскад II (TVS) зрізає піки, не перевантажуючи силові MOSFET.")
    ]

    for idx, (th_title, th_desc) in enumerate(t_lines):
        ty = threats_y + 50 + idx * 22
        f.append(text(start_x + 25, ty, th_title, size=11, bold=True, color=POS if idx != 0 else NEG, anchor="start"))
        f.append(text(start_x + 320, ty, th_desc, size=11, color=INK, anchor="start"))

    render(os.path.join(IMG, "protection-stages-chain.svg"), W, H, *f,
           title="Повний захисний ланцюг бортового входу")
    return "protection-stages-chain"


# ── 4. Робота активного обмежувача (Surge Stopper) ───────────────────────────
def fig_surge_stopper():
    """Принцип роботи Surge Stopper: лінійний режим MOSFET та таймер SOA."""
    W, H = 940, 520
    f = []

    # Дві осі поруч: зверху напруги V_IN та V_OUT, знизу потужність P_FET та таймер
    ox, oy1 = 90, 240
    oy2 = 450
    axW, axH = 780, 160

    # Верхній графік: Напруги
    f.append(arrow(ox, oy1, ox, oy1 - axH - 20, color=INK, sw=1.8))
    f.append(arrow(ox, oy1, ox + axW + 20, oy1, color=INK, sw=1.8))
    f.append(text(ox - 10, oy1 - axH - 8, "Напруга (В)", size=12, color=INK, anchor="start", bold=True))

    def Y1(v):
        return oy1 - axH * (v / 110.0)

    def X(t):
        return ox + (t / 300.0) * axW

    # Рівні
    f.append(line(ox, Y1(14.4), ox + axW, Y1(14.4), color=MUTED, sw=1, dash="4 4"))
    f.append(text(ox - 12, Y1(14.4) + 4, "14.4 В", size=11, color=MUTED, anchor="end"))

    f.append(line(ox, Y1(28.0), ox + axW, Y1(28.0), color=FIELD, sw=1.2, dash="5 5"))
    f.append(text(ox - 12, Y1(28.0) + 4, "28 В (V_CLAMP)", size=11, color=FIELD, anchor="end", bold=True))

    f.append(line(ox, Y1(100.0), ox + axW, Y1(100.0), color=POS, sw=1, dash="4 4"))
    f.append(text(ox - 12, Y1(100.0) + 4, "100 В (Пік)", size=11, color=POS, anchor="end"))

    # Крива V_IN (Сплеск Load Dump)
    pts_in = [(X(0), Y1(14.4)), (X(20), Y1(14.4)), (X(25), Y1(100.0))]
    for t in range(25, 301, 5):
        v = 14.4 + (100.0 - 14.4) * math.exp(-(t - 25) / 70.0)
        pts_in.append((X(t), Y1(v)))
    f.append(pline(pts_in, color=POS, sw=2.6))
    f.append(text(X(90), Y1(75), "V_IN (вхідний сплеск)", size=12, color=POS, bold=True, anchor="start"))

    # Крива V_OUT (Затиснута Surge Stopper-ом)
    pts_out = [(X(0), Y1(14.4)), (X(20), Y1(14.4)), (X(25), Y1(28.0)), (X(140), Y1(28.0))]
    for t in range(140, 301, 5):
        v_in = 14.4 + (100.0 - 14.4) * math.exp(-(t - 25) / 70.0)
        v = min(28.0, v_in)
        pts_out.append((X(t), Y1(v)))
    f.append(pline(pts_out, color=FIELD, sw=3.0))
    f.append(text(X(60), Y1(34), "V_OUT (безпечна шина для навантаження)", size=12, color=FIELD, bold=True, anchor="start"))

    # Нижній графік: Розсіювана потужність на MOSFET
    f.append(arrow(ox, oy2, ox, oy2 - axH - 20, color=INK, sw=1.8))
    f.append(arrow(ox, oy2, ox + axW + 20, oy2, color=INK, sw=1.8))
    f.append(text(ox - 10, oy2 - axH - 8, "Потужність P_FET (Вт) = (V_IN - V_OUT) · I_LOAD", size=12, color=INK, anchor="start", bold=True))
    f.append(text(ox + axW + 15, oy2 + 20, "Час (мс)", size=12, color=INK, anchor="end", bold=True))

    def Y2(p):
        return oy2 - axH * (p / 350.0)

    # Крива потужності на польовому транзисторі при струмі 4 А: P = (V_in - V_out) * 4
    pts_p = [(X(0), Y2(0)), (X(20), Y2(0)), (X(25), Y2((100.0 - 28.0) * 4.0))]
    for t in range(25, 301, 5):
        v_in = 14.4 + (100.0 - 14.4) * math.exp(-(t - 25) / 70.0)
        v_drop = max(0.0, v_in - 28.0)
        p = v_drop * 4.0
        pts_p.append((X(t), Y2(p)))
    f.append(pline(pts_p, color=NEG, sw=2.6))

    f.append(text(X(35), Y2(295), "Пікова потужність: P = (100 В - 28 В) · 4 А = 288 Вт", size=12, color=NEG, bold=True, anchor="start"))

    # Таймер витримки несправності (TMR capacitor ramp)
    bx_tmr, _, _ = textbox(X(190), Y2(150),
                           "Захист SOA: Контролер заряджає конденсатор таймера.\nЯкщо сплеск триває довше розрахункового часу (наприклад, > 50 мс),\nMOSFET повністю закривається для запобігання тепловому пробою.",
                           size=11.5, fill="#f4f6f8", stroke=LINE, sw=1.2, color=INK)
    f.append(bx_tmr)

    render(os.path.join(IMG, "surge-stopper-operation.svg"), W, H, *f,
           title="Робота Surge Stopper: лінійний режим MOSFET та розсіювання тепла")
    return "surge-stopper-operation"


if __name__ == "__main__":
    print(fig_cold_crank())
    print(fig_load_dump())
    print(fig_protection_stages())
    print(fig_surge_stopper())
    print("Всі фігури згенеровано успішно в:", IMG)
