# -*- coding: utf-8 -*-
"""Фігури до теми «Багатокаскадний підсилювач».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def res_h(x, y, w=46, h=18, label=None, lbl_below=False):
    """Горизонтальний резистор-прямокутник із центром по вертикалі на y."""
    out = [rect(x, y - h / 2, w, h, fill="#eef1f5", stroke=INK, sw=1.6, rx=3)]
    if label:
        if lbl_below:
            out.append(text(x + w / 2, y + h / 2 + 16, label, size=12, bold=True))
        else:
            out.append(text(x + w / 2, y - h / 2 - 7, label, size=12, bold=True))
    return "".join(out)


def res_v(cx, y_top, h=46, w=18, label=None):
    """Вертикальний резистор-прямокутник."""
    out = [rect(cx - w / 2, y_top, w, h, fill="#eef1f5", stroke=INK, sw=1.6, rx=3)]
    if label:
        out.append(text(cx + w / 2 + 6, y_top + h / 2 + 4, label, size=12, bold=True, anchor="start"))
    return "".join(out)


def gnd(cx, cy):
    out = [line(cx, cy, cx, cy + 6, color=INK, sw=1.8),
           line(cx - 13, cy + 6, cx + 13, cy + 6, color=INK, sw=2.2),
           line(cx - 8, cy + 11, cx + 8, cy + 11, color=INK, sw=2.0),
           line(cx - 3, cy + 16, cx + 3, cy + 16, color=INK, sw=1.8)]
    return "".join(out)


def cap_h(cx, cy, label=None):
    """Горизонтальний конденсатор (дві пластини) з центром (cx,cy)."""
    g = 7
    out = [line(cx - g, cy - 13, cx - g, cy + 13, color=INK, sw=2.4),
           line(cx + g, cy - 13, cx + g, cy + 13, color=INK, sw=2.4)]
    if label:
        out.append(text(cx, cy - 22, label, size=12, bold=True))
    return "".join(out)


def stage_box(x, y, w, h, title, sub, fill=FILL, stroke=LINE):
    """Прямокутник-каскад із заголовком (жирним) і підписом ролі (нижче)."""
    out = [rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8, rx=8)]
    out.append(text(x + w / 2, y + 26, title, size=14, bold=True))
    # підпис ролі — у рамку-fitbox, щоб напевно влізло
    out.append(fitbox(x + 8, y + 38, w - 16, h - 48, sub, size=11,
                      fill="none", stroke="none", color=MUTED))
    return "".join(out)


# ─────────────────────────────────────────────────────────────────────────────
def fig_loading_divider():
    """Стик двох каскадів = дільник Rout/(Rout+Rin)."""
    W, H = 760, 360
    f = [text(W / 2, 28, "Стик каскадів — це дільник напруги", size=16, bold=True)]

    top_y = 120          # верхня (сигнальна) шина
    gnd_y = 270          # нижня (земля)

    # ── ЛІВОРУЧ: модель виходу першого каскаду (джерело + Rout) ──
    src_x = 90
    # рамка-підпис «перший каскад»
    f.append(rect(40, 70, 250, 230, fill="#fafbfc", stroke=MUTED, sw=1.3, rx=10))
    f.append(text(60, 90, "вихід 1-го каскаду", size=11, color=MUTED, anchor="start"))
    # джерело підсиленої напруги — кружок із позначкою
    f.append(circle(src_x, (top_y + gnd_y) / 2, 24, fill="#fff", stroke=INK, sw=1.8))
    f.append(text(src_x, (top_y + gnd_y) / 2 - 4, "A·u", size=13, bold=True))
    f.append(text(src_x, (top_y + gnd_y) / 2 + 14, "вн.", size=10, color=MUTED))
    # від + джерела вгору до top_y
    f.append(line(src_x, (top_y + gnd_y) / 2 - 24, src_x, top_y, color=INK, sw=1.8))
    # Rout послідовно у верхній шині
    rout_x = src_x + 60
    f.append(line(src_x, top_y, rout_x, top_y, color=INK, sw=1.8))
    f.append(res_h(rout_x, top_y, w=70, label="Rout"))
    f.append(line(rout_x + 70, top_y, 300, top_y, color=INK, sw=1.8))
    # від − джерела вниз і по землі праворуч
    f.append(line(src_x, (top_y + gnd_y) / 2 + 24, src_x, gnd_y, color=INK, sw=1.8))
    f.append(line(src_x, gnd_y, 660, gnd_y, color=INK, sw=1.8))

    # ── вузол стику (де поєднано) ──
    node_x = 380
    f.append(line(300, top_y, node_x, top_y, color=INK, sw=1.8))
    f.append('<circle cx="%.1f" cy="%.1f" r="3.5" fill="%s"/>' % (node_x, top_y, INK))
    f.append(text(node_x, top_y - 16, "стик", size=12, bold=True, color=POS))

    # ── ПРАВОРУЧ: вхід другого каскаду = Rin на землю ──
    f.append(rect(470, 70, 250, 230, fill="#fafbfc", stroke=MUTED, sw=1.3, rx=10))
    f.append(text(490, 90, "вхід 2-го каскаду", size=11, color=MUTED, anchor="start"))
    rin_x = 560
    f.append(line(node_x, top_y, rin_x, top_y, color=INK, sw=1.8))
    f.append(res_v(rin_x, top_y, h=80, label="Rin"))
    f.append(line(rin_x, top_y + 80, rin_x, gnd_y, color=INK, sw=1.8))
    f.append('<circle cx="%.1f" cy="%.1f" r="3.5" fill="%s"/>' % (rin_x, gnd_y, INK))
    f.append(gnd((src_x + 660) / 2, gnd_y))

    # ── формула дільника ──
    f.append(fitbox(250, 312, 260, 38,
                    "U(на 2-й) = A·u · Rin / (Rout + Rin)",
                    size=12, fill="#f0f7f1", stroke=FIELD, color=INK))
    render(os.path.join(IMG, "loading-divider.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
def fig_three_stage_roles():
    """Три ланки: буфер високого Zin → підсилення → буфер низького Zout."""
    W, H = 820, 320
    f = [text(W / 2, 28, "Розподіл ролей у триланковому тракті", size=16, bold=True)]

    y = 95
    bh = 120
    bw = 190
    xs = [40, 315, 590]

    # джерело ліворуч
    f.append(text(20, y - 8, "джерело", size=11, color=MUTED, anchor="start"))

    stages = [
        ("Вхідний буфер", "високий Rin\nне вантажить джерело\nпідсилення ×1", "#eef6ff", NEG),
        ("Каскад підсилення", "велике підсилення\nнапруги A\n(головна ланка)", "#fdecea", POS),
        ("Вихідний буфер", "низький Rout\nживить навантаження\nпідсилення ×1", "#eef7ef", FIELD),
    ]
    centers = []
    for x, (t, s, fill, stroke) in zip(xs, stages):
        f.append(stage_box(x, y, bw, bh, t, s, fill=fill, stroke=stroke))
        centers.append(x + bw / 2)

    # стрілки-сигнал між ланками
    for i in range(len(xs) - 1):
        f.append(arrow(xs[i] + bw, y + bh / 2, xs[i + 1], y + bh / 2, color=INK, sw=2.0))
    # вхід зліва і вихід справа
    f.append(arrow(8, y + bh / 2, xs[0], y + bh / 2, color=INK, sw=2.0))
    f.append(text(W - 14, y - 8, "навантаження", size=11, color=MUTED, anchor="end"))
    f.append(arrow(xs[-1] + bw, y + bh / 2, W - 8, y + bh / 2, color=INK, sw=2.0))

    # підсумковий рядок під ланками
    f.append(fitbox(40, y + bh + 30, 740, 40,
                    "Підсилення живе лише в середній ланці; крайні ланки узгоджують опори, щоб стики не з'їдали сигнал.",
                    size=12, fill="#fafbfc", stroke=MUTED, color=INK))
    render(os.path.join(IMG, "three-stage-roles.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
def fig_coupling_types():
    """Ємнісний стик (конденсатор) проти прямого (гальванічного)."""
    W, H = 820, 360
    f = [text(W / 2, 28, "Два способи стику: розв'язка постійних рівнів", size=16, bold=True)]

    def half(x0, title, mode):
        out = [rect(x0, 60, 360, 250, fill="#fafbfc", stroke=MUTED, sw=1.3, rx=10)]
        out.append(text(x0 + 180, 84, title, size=13, bold=True))
        sig_y = 150
        # ── каскад 1 (ліворуч): прямокутник із рівнем спокою ──
        b1x = x0 + 24
        out.append(rect(b1x, 110, 96, 80, fill="#eef1f5", stroke=INK, sw=1.6, rx=6))
        out.append(text(b1x + 48, 132, "каскад 1", size=12, bold=True))
        out.append(text(b1x + 48, 152, "спокій", size=10, color=MUTED))
        out.append(text(b1x + 48, 168, "6.0 В", size=12, bold=True, color=POS))
        # ── каскад 2 (праворуч) ──
        b2x = x0 + 240
        out.append(rect(b2x, 110, 96, 80, fill="#eef1f5", stroke=INK, sw=1.6, rx=6))
        out.append(text(b2x + 48, 132, "каскад 2", size=12, bold=True))
        out.append(text(b2x + 48, 152, "спокій", size=10, color=MUTED))
        if mode == "cap":
            out.append(text(b2x + 48, 168, "2.0 В", size=12, bold=True, color=NEG))
        else:
            out.append(text(b2x + 48, 168, "6.0 В", size=12, bold=True, color=POS))
        # ── провід між ними на рівні sig_y ──
        left_end = b1x + 96
        right_end = b2x
        mid = (left_end + right_end) / 2
        if mode == "cap":
            out.append(line(left_end, sig_y, mid - 7, sig_y, color=INK, sw=1.8))
            out.append(cap_h(mid, sig_y, "C"))
            out.append(line(mid + 7, sig_y, right_end, sig_y, color=INK, sw=1.8))
            note = "Конденсатор = розрив для постійки.\nРівні незалежні (6 В і 2 В).\nКрізь нього йде ТІЛЬКИ сигнал."
            nfill = "#eef6ff"; nstroke = NEG
        else:
            out.append(line(left_end, sig_y, right_end, sig_y, color=INK, sw=1.8))
            out.append('<circle cx="%.1f" cy="%.1f" r="3" fill="%s"/>' % (mid, sig_y, INK))
            out.append(text(mid, sig_y - 12, "прямо", size=11, bold=True))
            note = "Пряме з'єднання передає й рівень.\nРівні узгоджені (6 В = 6 В).\nПроходить і постійна складова."
            nfill = "#eef7ef"; nstroke = FIELD
        out.append(fitbox(x0 + 24, 218, 312, 76, note, size=11, fill=nfill, stroke=nstroke, color=INK))
        return "".join(out)

    f.append(half(30, "Ємнісний зв'язок (AC)", "cap"))
    f.append(half(430, "Пряма (гальванічна) зв'язка", "direct"))
    render(os.path.join(IMG, "coupling-types.svg"), W, H, *f)


if __name__ == "__main__":
    fig_loading_divider()
    fig_three_stage_roles()
    fig_coupling_types()
    print("OK: loading-divider, three-stage-roles, coupling-types")
