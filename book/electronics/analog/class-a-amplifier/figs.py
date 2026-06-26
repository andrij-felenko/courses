# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def sine_path(x0, y0, w, amp, n=120, frac=1.0, base_clip=None):
    """Точки синуса зліва направо. frac — частка періоду, де веде струм (решта — нуль/відсічка)."""
    pts = []
    for i in range(n + 1):
        t = i / n               # 0..1 період
        ph = 2 * math.pi * t
        s = math.sin(ph)
        # для класу B/C: відкритий лише коли поточний кут у межах вікна протікання
        if base_clip is not None:
            # вікно протікання frac центроване на піку (ph=pi/2) для верхньої півхвилі
            on = (s > base_clip)
            y = y0 - amp * (s - base_clip) / (1 - base_clip) if on else y0
        else:
            y = y0 - amp * s
        pts.append((x0 + w * t, y))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    return d


def fig_conduction_angle():
    W, H = 760, 330
    frags = []
    panels = [
        ("Клас A — 360°", None, "веде ВЕСЬ період", FIELD),
        ("Клас B — 180°", 0.0, "лише верхні півхвилі", NEG),
        ("Клас C — <180°", 0.5, "вузький пік періоду", POS),
    ]
    pw = 230
    gap = 20
    x0 = 30
    top = 70
    ph = 180
    base_y = top + ph * 0.62
    amp = 58
    for i, (name, clip, sub, col) in enumerate(panels):
        px = x0 + i * (pw + gap)
        frags.append(rect(px, top, pw, ph, fill="#ffffff", stroke=MUTED, sw=1.2))
        # вісь часу
        frags.append(line(px + 12, base_y, px + pw - 12, base_y, color=MUTED, sw=1.2))
        frags.append(text(px + pw - 14, base_y - 5, "t", size=12, color=MUTED, anchor="end", italic=True))
        # сигнал
        d = sine_path(px + 14, base_y, pw - 28, amp, frac=1.0, base_clip=clip)
        frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, col))
        # підпис панелі
        frags.append(text(px + pw / 2, top - 14, name, size=15, color=INK, bold=True))
        frags.append(text(px + pw / 2, top + ph + 22, sub, size=12, color=MUTED))
    # нижня примітка про струм спокою для A
    frags.append(line(x0 + 14, base_y, x0 + pw - 14, base_y, color=FIELD, sw=0, dash="3,3"))
    render(os.path.join(OUT, 'conduction-angle.svg'), W, H, *frags,
           title="Кут протікання: скільки періоду прилад веде струм")


def fig_power_flow():
    W, H = 720, 360
    frags = []
    # дві колонки: тиша / повний сигнал. Кожна — стовпчик повної потужності,
    # поділений на «корисне» (зелене) і «тепло» (червоне).
    def column(cx, title, useful_frac, note):
        col_w = 130
        col_h = 200
        top = 80
        x = cx - col_w / 2
        # повна потужність — рамка-контур
        frags.append(rect(x, top, col_w, col_h, fill="#ffffff", stroke=INK, sw=1.6))
        heat_h = col_h * (1 - useful_frac)
        use_h = col_h * useful_frac
        # тепло (зверху вниз) червоне
        frags.append(rect(x, top, col_w, heat_h, fill="#fbe3df", stroke=POS, sw=1.2))
        # корисне знизу зелене
        if use_h > 1:
            frags.append(rect(x, top + heat_h, col_w, use_h, fill="#e3f4e9", stroke=FIELD, sw=1.2))
        # підписи всередині
        frags.append(text(cx, top + heat_h / 2 + 4, "тепло", size=13, color=POS, bold=True))
        if use_h > 22:
            frags.append(text(cx, top + heat_h + use_h / 2 + 4, "у динамік", size=12, color=FIELD, bold=True))
        # заголовок колонки
        frags.append(text(cx, top - 30, title, size=15, color=INK, bold=True))
        # «однакова повна потужність» — стрілка зверху
        frags.append(text(cx, top + col_h + 26, note, size=12, color=MUTED))

    column(195, "У тиші (нема сигналу)", 0.0, "уся витрата → тепло")
    column(525, "На повному сигналі", 0.30, "частина → корисний вихід")

    # спільна шкала зліва: повна потужність від живлення
    bx = 50
    frags.append(line(bx, 80, bx, 280, color=MUTED, sw=1.4))
    frags.append(text(bx - 6, 80, "Pжив", size=12, color=MUTED, anchor="end", bold=True))
    frags.append(text(bx + 8, 300, "однакова в обох випадках (струм спокою тече завжди)",
                      size=11, color=MUTED, anchor="start"))
    render(os.path.join(OUT, 'power-flow.svg'), W, H, *frags,
           title="Куди йде енергія в класі A")


def fig_class_tradeoff():
    W, H = 740, 340
    frags = []
    # горизонтальні смуги: для кожного класу — ефективність (довжина) + мітка вірності
    rows = [
        ("Клас A", 0.35, "вірність найкраща", FIELD, "≈25–50 %"),
        ("Клас AB", 0.55, "вірність добра", "#2aa198", "≈50–65 %"),
        ("Клас B", 0.785, "перехідне спотворення", NEG, "≈78 %"),
        ("Клас C", 0.80, "сильне спотворення*", "#b07a1e", "висока*"),
        ("Клас D", 0.92, "ключ, не плавний", POS, ">90 %"),
    ]
    x0 = 150
    bar_max = 430
    top = 64
    rh = 46
    # осьовий підпис
    frags.append(text(x0 + bar_max / 2, top - 18, "ефективність (ККД) →", size=13, color=MUTED, bold=True))
    for i, (name, eff, fid, col, lab) in enumerate(rows):
        y = top + i * rh
        frags.append(text(x0 - 12, y + 17, name, size=14, color=INK, anchor="end", bold=True))
        bw = bar_max * eff
        frags.append(rect(x0, y, bw, 26, fill=col, stroke=INK, sw=1.0, rx=4))
        frags.append(text(x0 + bw + 8, y + 18, lab, size=12, color=INK, anchor="start", bold=True))
        frags.append(text(x0 + 8, y + 40, fid, size=11, color=MUTED, anchor="start"))
    # шкала 0..100
    frags.append(line(x0, top - 6, x0, top + len(rows) * rh - 8, color=MUTED, sw=1.0))
    frags.append(text(x0, H - 14, "* клас C спотворює форму — годиться лише з резонансним контуром (радіо)",
                      size=11, color=MUTED, anchor="start"))
    render(os.path.join(OUT, 'class-tradeoff.svg'), W, H, *frags,
           title="Обмін: вірність проти ефективності за класами")


if __name__ == '__main__':
    fig_conduction_angle()
    fig_power_flow()
    fig_class_tradeoff()
    print("OK figures written to", OUT)
