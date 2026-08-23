# -*- coding: utf-8 -*-
"""Фігури до теми «Активне балансування: топології і вибір».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

C_FULL = POS      # повна комірка — гаряча, червона
C_LOW  = NEG      # порожня комірка — холодна, синя
C_OK   = FIELD    # зрівняне / корисне — зелене


def cell(x, y, w, h, frac, col, label=None):
    """Комірка-батарея: рамка + заповнення знизу на частку frac (0..1)."""
    out = [rect(x, y, w, h, fill="#fff", stroke=INK, sw=1.6)]
    fh = (h - 6) * max(0.0, min(1.0, frac))
    out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" fill="%s" fill-opacity="0.35"/>'
               % (x + 3, y + h - 3 - fh, w - 6, fh, col))
    # клема зверху
    out.append(rect(x + w / 2 - 6, y - 5, 12, 6, fill=INK, stroke=INK, sw=1, rx=1))
    if label:
        out.append(text(x + w / 2, y + h + 16, label, size=10, color=col, bold=True))
    return out


# ── 1. Пасивне гасить у тепло — активне переносить заряд ──────────────────────
def fig_principle():
    """Дві відповіді на ту саму перекошену пару: спалити надлишок чи перелити його.
    Головна думка теми в одній картинці."""
    W, H = 780, 380
    f = [text(W / 2, 30, "Два способи зрівняти пару комірок", size=16, bold=True)]
    cw, ch = 54, 120
    # ── ліворуч: пасивне ──
    f.append(text(195, 64, "Пасивне: спалити надлишок", size=13, color=MUTED, bold=True))
    f += cell(120, 90, cw, ch, 0.92, C_FULL, "повна")
    f += cell(250, 90, cw, ch, 0.55, C_LOW, "слабша")
    # резистор-«грілка» на повній
    rx0 = 120 + cw + 8
    f.append(rect(rx0, 110, 26, 60, fill="#fff", stroke=POS, sw=1.6))
    f.append(mtext(rx0 + 13, 134, "R\n🔥", size=11, color=POS, bold=True))
    f.append(text(rx0 + 13, 188, "у тепло", size=9, color=POS, anchor="middle"))
    f.append(text(195, 250, "надлишок повної згорів —", size=10, color=INK))
    f.append(text(195, 266, "слабша лишилась як була", size=10, color=INK))
    f.append(fitbox(70, 286, 250, 46,
                    "Пакет тепер обмежує слабша комірка.\nЕнергія повної просто втрачена.",
                    size=9.5, fill="#fdf3f2", stroke=POS, sw=1.3))
    # розділювач
    f.append(line(W / 2, 56, W / 2, 332, color=MUTED, sw=1, dash="4 4"))
    # ── праворуч: активне ──
    f.append(text(585, 64, "Активне: перелити заряд", size=13, color=FIELD, bold=True))
    f += cell(510, 90, cw, ch, 0.78, C_OK, "вирівняна")
    f += cell(640, 90, cw, ch, 0.72, C_OK, "вирівняна")
    # стрілка переносу між ними
    f.append(arrow(510 + cw + 6, 150, 640 - 6, 150, color=FIELD, sw=2.4))
    f.append(text(585, 140, "заряд →", size=10, color=FIELD, bold=True))
    f.append(text(585, 250, "надлишок повної перейшов", size=10, color=INK))
    f.append(text(585, 266, "у слабшу — нічого не згоріло", size=10, color=INK))
    f.append(fitbox(460, 286, 250, 46,
                    "Обидві піднялись до спільного рівня.\nЗбережено майже всю енергію.",
                    size=9.5, fill="#eafaf0", stroke=FIELD, sw=1.3))
    render(os.path.join(IMG, "principle.svg"), W, H, *f)


# ── 2. Три топології переносу заряду ─────────────────────────────────────────
def fig_topologies():
    """Чим саме переносять заряд: конденсатор, котушка, трансформатор —
    і куди кожен дотягується (сусід / будь-хто / весь пакет)."""
    W, H = 820, 430
    f = [text(W / 2, 30, "Три родини переносу: чим і куди", size=16, bold=True)]
    cw, ch = 220, 320
    gx = 20
    x0 = (W - 3 * cw - 2 * gx) / 2
    cy = 56

    def stack(cx, cyc, cols):
        """Колонка з трьох комірок одна над одною."""
        out = []
        bw, bh = 30, 26
        for i, col in enumerate(cols):
            yy = cyc + i * (bh + 6)
            out.append(rect(cx, yy, bw, bh, fill="#fff", stroke=col, sw=1.6))
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s" fill-opacity="0.3"/>'
                       % (cx + 2, yy + 2, bw - 4, bh - 4, col))
        return out, bw, bh

    cards = [
        (C_FULL, "Конденсатор", "«літаючий» кон-р",
         "перемикається між сусідніми\nкомірками й переносить\nпорцію заряду туди-сюди",
         "сусід ↔ сусід", "дешево, просто;\nближче до рівня — повільніше"),
        (C_LOW, "Котушка", "buck-boost між парою",
         "запасає заряд у магнітному\nполі й віддає сусідці;\nструм можна задати й тримати",
         "сусід ↔ сусід", "швидше, керований струм;\nдросель і ключі на пару"),
        (FIELD, "Трансформатор", "flyback, спільна обмотка",
         "тягне з усього пакета\nй адресно віддає будь-якій\nкомірці (чи навпаки)",
         "пакет ↔ будь-яка", "дотягнеться будь-куди, ізоляція;\nдорого, складне керування"),
    ]
    for i, (col, title, sub, how, reach, cost) in enumerate(cards):
        cx = x0 + i * (cw + gx)
        f.append(rect(cx, cy, cw, ch, fill="#fff", stroke=col, sw=2))
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="44" rx="6" fill="%s" fill-opacity="0.15"/>'
                 % (cx, cy, cw, col))
        f.append(text(cx + cw / 2, cy + 20, title, size=14, color=col, bold=True))
        f.append(text(cx + cw / 2, cy + 37, sub, size=9.5, color=MUTED, italic=True))
        # схемка: стек комірок ліворуч + елемент переносу
        sx = cx + 26
        sy = cy + 60
        st, bw, bh = stack(sx, sy, [C_FULL, MUTED, C_LOW])
        f += st
        ex = sx + bw + 40
        ey = sy + bh + 3
        if i == 0:   # конденсатор
            f.append(line(ex, ey - 14, ex, ey + 14, color=col, sw=2.4))
            f.append(line(ex + 12, ey - 14, ex + 12, ey + 14, color=col, sw=2.4))
            f.append(line(sx + bw, ey - bh + 4, ex, ey - 14, color=col, sw=1.4, dash="4 3"))
            f.append(line(sx + bw, ey + bh + 4, ex + 12, ey + 14, color=col, sw=1.4, dash="4 3"))
        elif i == 1:  # котушка
            for k in range(4):
                f.append('<path d="M %.1f %.1f q 7 -10 14 0" fill="none" stroke="%s" stroke-width="2.2"/>'
                         % (ex - 6, ey - 12 + k * 8, col))
            f.append(line(sx + bw, ey - 6, ex - 6, ey - 12, color=col, sw=1.4, dash="4 3"))
            f.append(line(sx + bw, ey + 10, ex - 6, ey + 20, color=col, sw=1.4, dash="4 3"))
        else:        # трансформатор
            f.append(line(ex, ey - 16, ex, ey + 16, color=col, sw=2))
            for k in range(4):
                f.append('<path d="M %.1f %.1f q -7 -10 0 -10 q 7 0 0 10" fill="none" stroke="%s" stroke-width="2"/>'
                         % (ex - 2, ey - 14 + k * 8, col))
                f.append('<path d="M %.1f %.1f q 7 -10 0 -10 q -7 0 0 10" fill="none" stroke="%s" stroke-width="2"/>'
                         % (ex + 2, ey - 14 + k * 8, col))
            f.append(line(sx + bw, ey, ex - 10, ey, color=col, sw=1.4, dash="4 3"))
        # текст «як»
        f.append(mtext(cx + cw / 2, cy + 184, how, size=9.5, color=INK, lh=1.25))
        # досяжність
        f.append(rect(cx + 20, cy + 232, cw - 40, 24, fill="#fff", stroke=col, sw=1.2))
        f.append(text(cx + cw / 2, cy + 248, reach, size=10.5, color=col, bold=True))
        # ціна
        f.append(line(cx + 16, cy + ch - 44, cx + cw - 16, cy + ch - 44, color=col, sw=0.8, dash="3 3"))
        f.append(mtext(cx + cw / 2, cy + ch - 26, cost, size=9, color=MUTED, lh=1.2))
    render(os.path.join(IMG, "topologies.svg"), W, H, *f)


# ── 3. Чому конденсатор гальмує під кінець ────────────────────────────────────
def fig_diminishing():
    """Рушій конденсаторного переносу — сама різниця напруг ΔU.
    Що ближче до рівня, то менший струм — «довгий хвіст» вирівнювання."""
    W, H = 760, 400
    f = [text(W / 2, 30, "Конденсаторний перенос: рушій згасає сам", size=16, bold=True)]
    ox, oy = 90, 300
    pw, ph = W - ox - 150, oy - 70
    f.append(line(ox, oy, ox + pw, oy, color=INK, sw=1.5))   # X
    f.append(line(ox, oy, ox, oy - ph, color=INK, sw=1.5))   # Y
    f.append(text(ox + pw / 2, oy + 34, "час →", size=10, color=MUTED))
    f.append(text(ox - 16, oy - ph - 4, "ΔU між", size=9.5, color=MUTED, anchor="end"))
    f.append(text(ox - 16, oy - ph + 9, "комірками", size=9.5, color=MUTED, anchor="end"))

    import math
    # експонента ΔU(t) = ΔU0 · e^(−t/τ): струм ~ ΔU, тож і він згасає
    pts = []
    N = 60
    for k in range(N + 1):
        t = k / N
        y = math.exp(-3.0 * t)
        pts.append((ox + t * pw, oy - y * ph))
    p = " ".join("%.1f,%.1f" % xy for xy in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" '
             'stroke-linecap="round"/>' % (p, C_FULL))
    # «корисна» зона vs «довгий хвіст»
    xk = ox + 0.33 * pw
    f.append(line(xk, oy, xk, oy - ph, color=MUTED, sw=1, dash="4 4"))
    f.append(text((ox + xk) / 2, oy - ph + 18, "швидко", size=10, color=FIELD, bold=True))
    f.append(text((ox + xk) / 2, oy - ph + 33, "(велике ΔU)", size=9, color=MUTED))
    f.append(text((xk + ox + pw) / 2, oy - 28, "довгий хвіст: ΔU мале → струм мізерний",
                  size=9.5, color=POS, bold=True))
    # точки-«порції»
    for t in (0.05, 0.18, 0.34, 0.55, 0.8):
        y = math.exp(-3.0 * t)
        f.append(circle(ox + t * pw, oy - y * ph, 3.5, fill=C_FULL, stroke=C_FULL, sw=1))
    f.append(fitbox(ox, oy + 48, pw, 26,
                    "Струм переносу пропорційний ΔU — і сам гасне, коли комірки сходяться.",
                    size=10, fill="#fdf3f2", stroke=POS, sw=1.3))
    render(os.path.join(IMG, "diminishing.svg"), W, H, *f)


# ── 4. Карта вибору: пасив чи актив, і яка топологія ─────────────────────────
def fig_choice():
    """Спершу рішення пасив/актив за масштабом пакета; тоді — яка з топологій."""
    W, H = 800, 410
    f = [text(W / 2, 30, "Вибір: спершу пасив чи актив, тоді — чим", size=16, bold=True)]
    # верх: дві колонки пасив/актив
    cw, ch = 360, 150
    gx = 20
    x0 = (W - 2 * cw - gx) / 2
    cy = 54
    cols = [
        (MUTED, "Пасив вистачає",
         "малий пакет, рідко циклює,\nкомірки з одної партії,\nдрейф невеликий",
         "дешево, тихо; надлишок —\nу тепло, лічені десятки мА"),
        (FIELD, "Актив виправданий",
         "великий/довгий пакет,\nдорогі комірки, жорсткий\nбюджет енергії та часу",
         "переносить 1–5 А при >90%;\nдорожче й складніше"),
    ]
    for i, (col, title, when, cost) in enumerate(cols):
        cx = x0 + i * (cw + gx)
        f.append(rect(cx, cy, cw, ch, fill="#fff", stroke=col, sw=2))
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="34" rx="6" fill="%s" fill-opacity="0.15"/>'
                 % (cx, cy, cw, col))
        f.append(text(cx + cw / 2, cy + 23, title, size=13.5, color=col, bold=True))
        f.append(mtext(cx + cw / 2, cy + 64, when, size=10.5, color=INK))
        f.append(line(cx + 16, cy + ch - 36, cx + cw - 16, cy + ch - 36, color=col, sw=0.8, dash="3 3"))
        f.append(mtext(cx + cw / 2, cy + ch - 20, cost, size=9.5, color=MUTED))
    # стрілка вниз: «обрав актив → яка топологія»
    f.append(arrow(W / 2, cy + ch + 4, W / 2, cy + ch + 30, color=FIELD, sw=2))
    f.append(text(W / 2 + 12, cy + ch + 22, "якщо актив:", size=10, color=FIELD, bold=True, anchor="start"))
    # низ: три топології-плитки
    ty = cy + ch + 40
    tw, th = 240, 92
    tgx = 18
    tx0 = (W - 3 * tw - 2 * tgx) / 2
    tiles = [
        (C_FULL, "Конденсатор", "дрейф малий, сусідній;\nекономія й простота"),
        (C_LOW, "Котушка", "треба швидше, керований\nструм між сусідами"),
        (FIELD, "Трансформатор", "слабка комірка десь у пакеті;\nтреба ізоляція"),
    ]
    for i, (col, title, body) in enumerate(tiles):
        cx = tx0 + i * (tw + tgx)
        f.append(rect(cx, ty, tw, th, fill="#fff", stroke=col, sw=1.8))
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="26" rx="6" fill="%s" fill-opacity="0.15"/>'
                 % (cx, ty, tw, col))
        f.append(text(cx + tw / 2, ty + 18, title, size=12, color=col, bold=True))
        f.append(mtext(cx + tw / 2, ty + 50, body, size=9.5, color=INK))
    render(os.path.join(IMG, "choice.svg"), W, H, *f)


if __name__ == "__main__":
    fig_principle()
    fig_topologies()
    fig_diminishing()
    fig_choice()
    print("OK: 4 figures ->", IMG)
