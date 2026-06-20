# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..','..','..','..','scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Локальні кольори за змістом
RF   = "#8e44ad"   # прийнятий ВЧ-сигнал (фіолетовий)
LO   = FIELD       # гетеродин (зелений)
IF   = POS         # проміжна частота (червоний — те, що лишаємо й підсилюємо)
IMG  = MUTED       # дзеркальний канал (сірий — небажаний)


def tri(cx, base_y, half_w, h, color, sw=2.4, fill=None):
    """Трикутний «горбик» спектра з центром cx, основою на base_y."""
    pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (cx - half_w, base_y, cx, base_y - h, cx + half_w, base_y)
    f = fill if fill else "none"
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (pts, f, color, sw))


def tick(x, base_y, lbl, color=MUTED, up=False):
    dy = -6 if up else 18
    return (line(x, base_y - 4, x, base_y + 4, color=MUTED, sw=1.2) +
            text(x, base_y + dy, lbl, size=12, color=color))


# ── Фігура 1: перенесення спектра на сталу IF (серце ідеї) ───────────────────

def fig_translate():
    W, H = 720, 360
    ax, ay = 60, 250            # початок осі частоти
    axw = 600                   # довжина осі
    p = []
    p.append(line(ax, ay, ax + axw, ay, color=INK, sw=1.6))
    p.append(arrow(ax + axw - 22, ay, ax + axw, ay, color=INK, sw=1.6))
    p.append(text(ax + axw + 8, ay + 5, "f", size=15, color=INK, italic=True, anchor="start"))

    # координати трьох частот на осі (умовні px)
    f_lo  = ax + 250
    f_rf  = ax + 330
    f_if  = ax + 110

    # прийнятий сигнал на ВЧ (фіолетовий горбик, високо по частоті)
    p.append(tri(f_rf, ay, 26, 70, RF, fill="#f3e8fb"))
    p.append(tick(f_rf, ay, "f_RF", color=RF))
    p.append(text(f_rf, ay - 86, "прийнятий", size=12, color=RF, bold=True))
    p.append(text(f_rf, ay - 70, "сигнал", size=12, color=RF, bold=True))

    # гетеродин — гострий пік (зелена «паличка»)
    p.append(line(f_lo, ay, f_lo, ay - 96, color=LO, sw=3.0))
    p.append(arrow(f_lo, ay - 80, f_lo, ay - 98, color=LO, sw=3.0))
    p.append(tick(f_lo, ay, "f_LO", color=LO))
    p.append(text(f_lo, ay - 106, "гетеродин", size=12, color=LO, bold=True))

    # результат — на IF (червоний горбик, низько по частоті)
    p.append(tri(f_if, ay, 26, 70, IF, fill="#fdecea"))
    p.append(tick(f_if, ay, "f_IF", color=IF))
    p.append(text(f_if, ay - 86, "та сама", size=12, color=IF, bold=True))
    p.append(text(f_if, ay - 70, "інформація", size=12, color=IF, bold=True))

    # дуга-перенесення RF → IF
    midx = (f_rf + f_if) / 2
    p.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="2.2" stroke-dasharray="6 4" marker-end="url(#arrow)"/>'
             % (f_rf - 26, ay - 60, midx, ay - 150, f_if + 26, ay - 60, INK))
    p.append(text(midx, ay - 158, "перенесення", size=13, color=INK, bold=True))

    # формула IF = |RF − LO|
    b, bw, bh = textbox(ax + axw - 150, ay + 56, "f_IF = | f_RF − f_LO |",
                        size=14, color=INK, bold=True, min_w=240)
    p.append(b)

    render(os.path.join(OUT, "translate.svg"), W, H, *p,
           title="Змішування переносить сигнал на сталу проміжну частоту")


# ── Фігура 2: чому фіксована IF — це легко (станції їдуть, фільтр стоїть) ─────

def fig_fixed_if():
    W, H = 720, 340
    p = []
    # ВЕРХ: різні станції на ВЧ — фільтр мусив би «бігати»
    ax, ay = 60, 140
    axw = 600
    p.append(line(ax, ay, ax + axw, ay, color=INK, sw=1.5))
    p.append(arrow(ax + axw - 22, ay, ax + axw, ay, color=INK, sw=1.5))
    p.append(text(ax + axw + 8, ay + 5, "f", size=14, color=INK, italic=True, anchor="start"))
    p.append(text(ax, ay - 70, "Без переносу: станції на різних f —", size=13, color=INK, bold=True, anchor="start"))
    p.append(text(ax, ay - 52, "вузький фільтр мусив би перестроюватись під кожну", size=12, color=MUTED, anchor="start"))
    for i, dx in enumerate([130, 250, 370, 490]):
        col = RF
        p.append(tri(ax + dx, ay, 18, 40, col, fill="#f3e8fb"))
    # «біжучий» фільтр — пунктирна рамка зі стрілкою туди-сюди
    p.append(rect(ax + 232, ay - 50, 36, 56, fill="none", stroke=NEG, sw=1.8, rx=4))
    p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6" '
             'marker-end="url(#arrow)" marker-start="url(#arrow)" stroke-dasharray="4 3"/>'
             % (ax + 120, ay - 22, ax + 380, ay - 22, NEG))
    p.append(text(ax + 250, ay - 60, "?", size=18, color=NEG, bold=True))

    # НИЗ: усі станції переносяться на ОДНУ IF — фільтр стоїть нерухомо
    bx, by = 60, 290
    bxw = 600
    p.append(line(bx, by, bx + bxw, by, color=INK, sw=1.5))
    p.append(arrow(bx + bxw - 22, by, bx + bxw, by, color=INK, sw=1.5))
    p.append(text(bx + bxw + 8, by + 5, "f", size=14, color=INK, italic=True, anchor="start"))
    p.append(text(bx, by - 72, "З переносом на IF: яку станцію не візьми —", size=13, color=INK, bold=True, anchor="start"))
    p.append(text(bx, by - 54, "вона лягає на ту саму f_IF; фільтр один, нерухомий, гострий", size=12, color=MUTED, anchor="start"))
    f_if = bx + 250
    p.append(tri(f_if, by, 20, 46, IF, fill="#fdecea"))
    p.append(tick(f_if, by, "f_IF", color=IF))
    # нерухомий фільтр
    p.append(rect(f_if - 26, by - 56, 52, 60, fill="none", stroke=FIELD, sw=2.2, rx=4))
    p.append(text(f_if, by - 64, "сталий фільтр", size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, "fixed-if.svg"), W, H, *p,
           title="Чому стала IF легша: фільтр і підсилювач налаштовані раз")


# ── Фігура 3: дзеркальний канал ──────────────────────────────────────────────

def fig_image():
    W, H = 720, 340
    ax, ay = 60, 250
    axw = 600
    p = []
    p.append(line(ax, ay, ax + axw, ay, color=INK, sw=1.6))
    p.append(arrow(ax + axw - 22, ay, ax + axw, ay, color=INK, sw=1.6))
    p.append(text(ax + axw + 8, ay + 5, "f", size=15, color=INK, italic=True, anchor="start"))

    f_img = ax + 150
    f_lo  = ax + 300
    f_rf  = ax + 450

    # корисний сигнал
    p.append(tri(f_rf, ay, 24, 64, RF, fill="#f3e8fb"))
    p.append(tick(f_rf, ay, "f_RF", color=RF))
    p.append(text(f_rf, ay - 80, "корисний", size=12, color=RF, bold=True))

    # гетеродин
    p.append(line(f_lo, ay, f_lo, ay - 96, color=LO, sw=3.0))
    p.append(arrow(f_lo, ay - 80, f_lo, ay - 98, color=LO, sw=3.0))
    p.append(tick(f_lo, ay, "f_LO", color=LO))

    # дзеркало — на стільки ж нижче LO, на скільки RF вище
    p.append(tri(f_img, ay, 24, 64, IMG, fill="#eef0f2"))
    p.append(tick(f_img, ay, "f_дзерк", color=IMG))
    p.append(text(f_img, ay - 80, "дзеркало", size=12, color=IMG, bold=True))

    # симетрія навколо LO: дві дужки по IF
    for fx, lbl in [((f_lo + f_rf) / 2, "IF"), ((f_img + f_lo) / 2, "IF")]:
        p.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
                 'stroke-width="1.8"/>' % (min(fx*2-f_lo, f_lo), ay + 26,
                                           fx, ay + 52,
                                           max(fx*2-f_lo, f_lo), ay + 26, INK))
        p.append(text(fx, ay + 66, lbl, size=12, color=INK, bold=True))

    # підпис-висновок
    b, bw, bh = textbox(ax + 300, 64,
                        "Обидві частоти віддалені від f_LO на IF →\nобидві лягають на ту саму f_IF",
                        size=12.5, color=INK, fill=BG, stroke=MUTED, min_w=380)
    p.append(b)

    render(os.path.join(OUT, "image.svg"), W, H, *p,
           title="Дзеркальний канал: друга частота, що дає ту саму IF")


# ── Фігура 4: структура супергетеродинного приймача ──────────────────────────

def fig_blocks():
    W, H = 760, 300
    cy = 150
    p = []

    def block(x, w, lbl, sub, col=INK, fill=FILL):
        h = 64
        y = cy - h / 2
        out = rect(x, y, w, h, fill=fill, stroke=col, sw=2.0, rx=6)
        out += text(x + w / 2, cy - 4, lbl, size=13.5, color=col, bold=True)
        out += text(x + w / 2, cy + 16, sub, size=11, color=MUTED)
        return out, x + w

    # антена
    p.append(line(40, cy, 70, cy, color=INK, sw=2))
    p.append('<polyline points="40,%.0f 34,%.0f 46,%.0f 40,%.0f" fill="none" stroke="%s" stroke-width="2"/>'
             % (cy, cy - 14, cy - 14, cy, INK))
    p.append(text(40, cy + 28, "антена", size=11, color=MUTED))

    x = 70
    b, x = block(x, 96, "ВЧ-фільтр", "+ підсил.", col=RF); p.append(b);
    p.append(line(x, cy, x + 26, cy, color=INK, sw=2)); x += 26
    # змішувач — коло з ×
    mx = x + 30
    p.append(circle(mx, cy, 26, fill="#fff", stroke=INK, sw=2.2))
    p.append(text(mx, cy + 7, "×", size=22, color=INK, bold=True))
    p.append(text(mx, cy - 36, "змішувач", size=11, color=INK, bold=True))
    x = mx + 26
    # гетеродин знизу у змішувач
    p.append(line(mx, cy + 50, mx, cy + 26, color=LO, sw=2))
    p.append(arrow(mx, cy + 30, mx, cy + 26, color=LO, sw=2))
    bl, _ = block(mx - 55, 110, "гетеродин", "f_LO, перестр.", col=LO, fill="#eafaf0")
    # перемістимо блок гетеродина нижче
    p.append(rect(mx - 55, cy + 50, 110, 50, fill="#eafaf0", stroke=LO, sw=2.0, rx=6))
    p.append(text(mx, cy + 70, "гетеродин", size=12, color=LO, bold=True))
    p.append(text(mx, cy + 88, "f_LO (перестр.)", size=10.5, color=MUTED))

    p.append(line(x, cy, x + 22, cy, color=INK, sw=2)); x += 22
    b, x = block(x, 122, "IF-фільтр", "вузький, сталий", col=IF, fill="#fdecea"); p.append(b)
    p.append(line(x, cy, x + 20, cy, color=INK, sw=2)); x += 20
    b, x = block(x, 96, "IF-підсил.", "велике G", col=IF); p.append(b)
    p.append(line(x, cy, x + 20, cy, color=INK, sw=2)); x += 20
    b, x = block(x, 96, "детектор", "→ звук/біти", col=INK); p.append(b)
    p.append(line(x, cy, x + 24, cy, color=INK, sw=2))
    p.append(arrow(x + 20, cy, x + 24, cy, color=INK, sw=2))

    render(os.path.join(OUT, "blocks.svg"), W, H, *p,
           title="Тракт супергетеродина: уся складна робота — на сталій IF")


if __name__ == "__main__":
    fig_translate()
    fig_fixed_if()
    fig_image()
    fig_blocks()
    print("OK: figures written to", OUT)
