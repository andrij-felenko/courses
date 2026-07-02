# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: дротяний запобіжник vs eFuse — що всередині ─────────────────────
def fig_anatomy():
    W, H = 760, 340
    p = []

    # ── ліворуч: звичайний плавкий запобіжник ──
    p.append(text(190, 46, "Плавкий запобіжник", size=16, bold=True))
    # вхід
    p.append(line(60, 150, 120, 150, color=POS, sw=3))
    p.append(text(60, 138, "+Vin", size=12, color=POS, anchor="start", bold=True))
    # корпус із тонким дротиком
    p.append(rect(120, 130, 140, 40, fill="#fdf0e6"))
    # звивистий дротик
    wire = "M124 150 L140 150 L146 138 L158 162 L170 138 L182 162 L194 138 L206 162 L218 138 L230 150 L256 150"
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (wire, POS))
    p.append(text(190, 190, "тонкий дріт", size=11, color=MUTED))
    # вихід
    p.append(line(260, 150, 320, 150, color=INK, sw=3))
    box1 = fitbox(250, 210, 140, 46, "згоряє — розрив\nназавжди", size=12, fill="#fdecea", stroke=POS)
    p.append(box1)
    p.append(text(190, 300, "гріється → плавиться → міняй", size=12, color=MUTED))

    # роздільник
    p.append(line(380, 40, 380, 300, color="#d0d0d0", sw=1.5, dash="4,4"))

    # ── праворуч: eFuse ──
    p.append(text(575, 46, "eFuse (мікросхема-запобіжник)", size=16, bold=True))
    p.append(line(410, 150, 460, 150, color=POS, sw=3))
    p.append(text(410, 138, "+Vin", size=12, color=POS, anchor="start", bold=True))
    # корпус чипа
    p.append(rect(460, 92, 230, 150, fill="#eef4ff", stroke=NEG, sw=1.8))
    # силовий MOSFET-ключ у розрив
    b1 = fitbox(478, 130, 90, 40, "силовий\nMOSFET", size=11, fill=BG, stroke=INK)
    p.append(b1)
    # шунт-давач струму
    b2 = fitbox(585, 130, 92, 40, "давач\nструму", size=11, fill=BG, stroke=INK)
    p.append(b2)
    p.append(line(568, 150, 585, 150, color=INK, sw=2.5))
    # логіка знизу
    b3 = fitbox(478, 186, 199, 40, "логіка: межа струму · поріг напруги · термозахист", size=11, fill="#eafaf0", stroke=FIELD)
    p.append(b3)
    p.append(arrow(577, 170, 577, 186, color=FIELD))
    # вихід
    p.append(line(690, 150, 740, 150, color=INK, sw=3))
    box2 = fitbox(470, 258, 220, 44, "обмежує / вимикає й сам вертається — без заміни", size=12, fill="#eafaf0", stroke=FIELD)
    p.append(box2)

    render(os.path.join(IMG, 'anatomy.svg'), W, H, *[f if isinstance(f, str) else f[0] for f in p])


# ── Фігура 2: відповідь на перевантаження — плато регулювання й швидкий зріз ──
def fig_response():
    W, H = 800, 360
    p = []
    ox, oy = 90, 300          # початок осей
    axw, axh = 620, 250
    p.append(text(W/2, 32, "Що робить eFuse зі струмом перевантаження", size=16, bold=True))

    # осі
    p.append(arrow(ox, oy, ox + axw, oy, color=INK))
    p.append(arrow(ox, oy, ox, oy - axh, color=INK))
    p.append(text(ox + axw, oy + 22, "час", size=12, anchor="end"))
    p.append(text(ox - 14, oy - axh + 4, "струм", size=12, anchor="end"))

    # рівні
    y_ilim = oy - 150         # межа струму
    y_ifast = oy - 210        # поріг швидкого зрізу
    p.append(line(ox, y_ilim, ox + axw, y_ilim, color=POS, sw=1.3, dash="5,4"))
    p.append(text(ox - 8, y_ilim + 4, "Iмежа", size=12, color=POS, anchor="end", bold=True))
    p.append(line(ox, y_ifast, ox + axw, y_ifast, color="#8e44ad", sw=1.3, dash="5,4"))
    p.append(text(ox - 8, y_ifast + 4, "Iзріз", size=12, color="#8e44ad", anchor="end", bold=True))

    # крива струму: спокій → повільне перевантаження (регулювання на плато) → відпустило
    # 1) нормальний рівень
    y_norm = oy - 60
    p.append(line(ox, y_norm, ox + 150, y_norm, color=NEG, sw=2.6))
    # 2) наростання до плато й тримання на Iмежа
    p.append('<path d="M%d %d L%d %d L%d %d" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (ox + 150, y_norm, ox + 210, y_ilim, ox + 360, y_ilim, NEG))
    # 3) повернення в норму (напруга просіла, навантаження знято)
    p.append('<path d="M%d %d L%d %d L%d %d" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (ox + 360, y_ilim, ox + 400, y_norm, ox + 470, y_norm, NEG))

    # підпис зони регулювання
    b1 = fitbox(ox + 200, y_ilim - 78, 172, 44, "тримає струм на межі, не рве коло", size=11, fill="#fdf0e6", stroke=POS)
    p.append(b1)
    p.append(arrow(ox + 286, y_ilim - 34, ox + 286, y_ilim - 4, color=POS))

    # окремо: коротке замикання — крутий стрибок вище Iзріз і миттєвий зріз
    xsc = ox + 490
    p.append(line(xsc, y_norm, xsc, oy, color=INK, sw=1, dash="3,3"))
    p.append(text(xsc + 4, oy + 22, "коротке", size=11, color=INK, anchor="start"))
    # стрибок вгору
    p.append('<path d="M%d %d L%d %d" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (xsc, y_norm, xsc + 8, y_ifast - 6, NEG))
    # миттєвий зріз до нуля
    p.append('<path d="M%d %d L%d %d L%d %d" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (xsc + 8, y_ifast - 6, xsc + 8, oy, xsc + 120, oy, NEG))
    b2 = fitbox(xsc + 20, y_ifast - 40, 150, 40, "зріз < 1 мкс:\nключ закрито", size=11, fill="#f3e9f7", stroke="#8e44ad")
    p.append(b2)

    render(os.path.join(IMG, 'response.svg'), W, H, *[f if isinstance(f, str) else f[0] for f in p])


# ── Фігура 3: три реакції на затяжну аварію ──────────────────────────────────
def fig_modes():
    W, H = 760, 300
    p = []
    p.append(text(W/2, 30, "Три способи повестися після зриву", size=16, bold=True))

    cols = [
        (130, "Засувка", "вимкнувся —\nі стоїть, доки\nне скинеш вручну", "#fdecea", POS),
        (380, "Автоповтор", "почекав —\nспробував знову,\nі так по колу", "#eafaf0", FIELD),
        (630, "Автомат", "тримає межу,\nаж поки не\nперегріється", "#eef4ff", NEG),
    ]
    for cx, name, desc, fill, col in cols:
        b = fitbox(cx - 110, 58, 220, 40, name, size=15, bold=True, fill=fill, stroke=col)
        p.append(b)
        ox, oy = cx - 95, 210
        axw, axh = 190, 88
        # міні-осі
        p.append(line(ox, oy, ox + axw, oy, color=INK, sw=1.4))
        p.append(line(ox, oy, ox, oy - axh, color=INK, sw=1.4))
        yhi = oy - 60
        if name == "Засувка":
            # один імпульс і в нуль назавжди
            p.append('<path d="M%d %d L%d %d L%d %d L%d %d L%d %d" fill="none" stroke="%s" stroke-width="2.4"/>'
                     % (ox, yhi, ox + 40, yhi, ox + 40, oy, ox + 40, oy, ox + axw, oy, col))
        elif name == "Автоповтор":
            # серія коротких спроб
            x = ox
            path = "M%d %d" % (x, yhi)
            for _ in range(3):
                path += " L%d %d L%d %d L%d %d" % (x + 22, yhi, x + 22, oy, x + 55, oy)
                x += 55
            p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (path, col))
        else:
            # тримає плато довго, тоді термозахист рубає
            p.append('<path d="M%d %d L%d %d L%d %d L%d %d" fill="none" stroke="%s" stroke-width="2.4"/>'
                     % (ox, yhi, ox + 130, yhi, ox + 130, oy, ox + axw, oy, col))
            p.append(text(ox + 130, oy - 66, "перегрів", size=10, color=MUTED, anchor="middle"))
        p.append(fitbox(cx - 110, 232, 220, 52, desc, size=11, fill=BG, stroke=col))

    render(os.path.join(IMG, 'modes.svg'), W, H, *[f if isinstance(f, str) else f[0] for f in p])


# ── Фігура 4 (для hist-вставки): два «eFuse» — спільний лише корінь ───────────
def fig_two_efuses():
    W, H = 780, 430
    p = []
    p.append(text(W / 2, 30, "Одне слово «eFuse» — дві різні речі", size=17, bold=True))

    # спільний корінь угорі
    root = fitbox(W / 2 - 150, 46, 300, 34, "спільне: лише корінь «fuse» (плавка ланка)",
                  size=12, fill="#f4f6f8", stroke=MUTED)
    p.append(root)
    p.append(line(W / 2 - 120, 80, 200, 108, color=MUTED, sw=1.4))
    p.append(line(W / 2 + 120, 80, 580, 108, color=MUTED, sw=1.4))

    # ── ЛІВОРУЧ: захисна мікросхема в проводі живлення ──
    p.append(rect(40, 112, 320, 288, fill="#eef4ff", stroke=NEG, sw=1.8))
    p.append(text(200, 136, "1 · eFuse у проводі живлення", size=14, bold=True, color=NEG))
    p.append(text(200, 156, "(onsemi, серії NIS)", size=11, color=MUTED))
    # мінісхема: вхід — ключ — вихід
    p.append(line(70, 210, 120, 210, color=POS, sw=3))
    p.append(text(70, 198, "+Vin", size=11, color=POS, anchor="start", bold=True))
    p.append(fitbox(120, 190, 90, 40, "MOSFET-\nключ", size=11, fill=BG, stroke=INK))
    p.append(line(210, 210, 260, 210, color=INK, sw=3))
    p.append(text(300, 206, "навантаження", size=10, color=MUTED, anchor="middle"))
    p.append(line(260, 210, 300, 210, color=INK, sw=3))
    p.append(fitbox(60, 250, 280, 44, "вимірює струм → обмежує або вимикає;\nпісля аварії вертається сама",
                    size=11, fill=BG, stroke=NEG))
    p.append(fitbox(60, 306, 280, 34, "багаторазова · зовні чипа · захист",
                    size=11, fill="#eafaf0", stroke=FIELD))
    p.append(fitbox(60, 350, 280, 34, "робить: рятує коло від струму й напруги",
                    size=11, fill="#fdf0e6", stroke=POS))

    # ── ПРАВОРУЧ: одноразовий кремнієвий запобіжник у чипі ──
    p.append(rect(420, 112, 320, 288, fill="#f3e9f7", stroke="#8e44ad", sw=1.8))
    p.append(text(580, 136, "2 · eFuse усередині чипа", size=14, bold=True, color="#8e44ad"))
    p.append(text(580, 156, "(IBM, 2002 · 2004)", size=11, color=MUTED))
    # мінісхема: полікремнієва доріжка з силіцидом, розрив електроміграцією
    p.append(line(450, 210, 500, 210, color=INK, sw=2))
    p.append(rect(500, 202, 80, 16, fill="#d9c7e8", stroke="#8e44ad", sw=1.4, rx=3))
    p.append(text(540, 232, "силіцид на", size=9, color=MUTED, anchor="middle"))
    p.append(text(540, 244, "полікремнії", size=9, color=MUTED, anchor="middle"))
    p.append(line(580, 210, 630, 210, color=INK, sw=2))
    # позначка розриву-міграції
    p.append(text(620, 196, "→ витік атомів", size=9, color="#8e44ad", anchor="middle"))
    p.append(fitbox(440, 250, 280, 44, "струм 10 мА · 200 мкс жене атоми силіциду —\nопір злітає раз і назавжди",
                    size=11, fill=BG, stroke="#8e44ad"))
    p.append(fitbox(440, 306, 280, 34, "одноразова · всередині чипа · пам'ять",
                    size=11, fill="#eafaf0", stroke=FIELD))
    p.append(fitbox(440, 350, 280, 34, "робить: серійний номер, ключ, обхід дефекту",
                    size=11, fill="#fdf0e6", stroke=POS))

    render(os.path.join(IMG, 'two-efuses.svg'), W, H,
           *[f if isinstance(f, str) else f[0] for f in p])


if __name__ == '__main__':
    fig_anatomy()
    fig_response()
    fig_modes()
    fig_two_efuses()
    print("ok")
