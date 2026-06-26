# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. delay блокує все, tick — ні ────────────────────────────────────────────
# Ідея: delay() зупиняє ВЕСЬ цикл — і анімацію, і кнопки, і зв'язок. Неблокувальний
# tick лише дивиться на годинник і за потреби робить один крок, лишаючи цикл вільним.
def fig_blocking_vs_tick():
    W, H = 760, 340
    p = []

    # ── ліворуч: delay ── один потік, у якому все стоїть
    lx = 40
    p.append(text(lx + 150, 50, "delay(20) у циклі", size=14, color=POS, bold=True))
    bar_y, bar_h = 80, 30
    # суцільна смуга «зайнято/спимо»
    segs = [("крок", FIELD), ("СПИМО", "#f0c0c0"), ("крок", FIELD),
            ("СПИМО", "#f0c0c0"), ("крок", FIELD), ("СПИМО", "#f0c0c0")]
    sw = 300 / len(segs)
    for i, (lab, col) in enumerate(segs):
        x = lx + i * sw
        p.append(rect(x, bar_y, sw, bar_h, fill=col, stroke="#cfd8e3", sw=1.0, rx=0))
        p.append(text(x + sw / 2, bar_y + bar_h / 2 + 4, lab, size=9, color=INK))
    p.append(text(lx + 150, bar_y + bar_h + 24, "час →", size=10, color=MUTED))
    # внизу — те, що поховано
    p.append(fitbox(lx, 175, 300, 110,
                    "поки delay спить —\nкнопка не читається,\nзв'язок не відповідає,\nінші ефекти стоять",
                    size=12, fill="#fdecea", stroke=POS, sw=1.6))

    # ── праворуч: tick ── цикл біжить вільно, крок робиться лише коли «час настав»
    rx = 420
    p.append(text(rx + 150, 50, "tick(): дивимось на годинник", size=14, color=FIELD, bold=True))
    # тонка лінія часу з мітками «настав час»
    ty = bar_y + bar_h / 2
    p.append(line(rx, ty, rx + 300, ty, color=MUTED, sw=1.5))
    for i in range(6):
        x = rx + 20 + i * 52
        p.append(circle(x, ty, 7, fill="#eafaf0", stroke=FIELD, sw=2))
        p.append(text(x, ty - 16, "крок", size=8, color=FIELD))
    p.append(text(rx + 150, bar_y + bar_h + 24, "між мітками цикл вільний", size=10, color=MUTED))
    p.append(fitbox(rx, 175, 300, 110,
                    "між кроками цикл крутиться —\nчитає кнопки, веде зв'язок,\nрухає ВСІ ефекти разом;\nкрок — лише коли настав час",
                    size=12, fill="#eafaf0", stroke=FIELD, sw=1.6))

    render(os.path.join(OUT, "blocking-vs-tick.svg"), W, H, *p)


# ── 2. анімація як автомат над фазою 0→1 ──────────────────────────────────────
# Ідея: ефект — це функція phase∈[0,1] → яскравість. Лічильник фази повзе в часі,
# на кінці — або стоп, або розворот, або стрибок на 0 (цикл).
def fig_phase_machine():
    W, H = 740, 330
    p = []

    p.append(text(W / 2, 34, "ефект = функція фази → яскравість", size=15, bold=True))

    # вісь фази 0..1
    ax, ay, aw = 70, 120, 420
    p.append(line(ax, ay, ax + aw, ay, color=INK, sw=2))
    for frac, lab in [(0, "0.0"), (0.5, "0.5"), (1.0, "1.0")]:
        x = ax + frac * aw
        p.append(line(x, ay - 5, x, ay + 5, color=INK, sw=1.5))
        p.append(text(x, ay + 20, lab, size=11, color=MUTED))
    p.append(text(ax + aw / 2, ay - 50, "фаза повзе в часі: phase += dt / тривалість", size=12, color=INK))
    # бігунець
    bx = ax + 0.62 * aw
    p.append(circle(bx, ay, 9, fill="#fff3d6", stroke="#d99a00", sw=2.2))
    p.append(text(bx, ay - 16, "зараз", size=10, color="#a06b00", bold=True))

    # три виходи на кінці фази
    cy = 250
    b1 = fitbox(60, cy, 195, 56, "СТОП на 1.0\n(одноразовий ефект)", size=11,
                fill=FILL, stroke=LINE, sw=1.4)
    b2 = fitbox(275, cy, 195, 56, "РОЗВОРОТ 1→0\n(дихання туди-сюди)", size=11,
                fill="#eafaf0", stroke=FIELD, sw=1.4)
    b3 = fitbox(490, cy, 195, 56, "СТРИБОК на 0.0\n(нескінченний цикл)", size=11,
                fill="#eaf0fd", stroke=NEG, sw=1.4)
    p += [b1, b2, b3]
    p.append(text(W / 2, cy - 14, "що робити, коли фаза дійшла 1.0:", size=11, color=MUTED))

    render(os.path.join(OUT, "phase-machine.svg"), W, H, *p)


# ── 3. криві: лінійна, плавний вхід-вихід, і де тут гамма ─────────────────────
# Ідея: дві різні криві працюють по черзі. Easing (плавний хід фази) — форма РУХУ;
# гамма — корекція ока. Лінійна фаза + гамма ще «механічна»; easing додає живість.
def fig_curves():
    W, H = 740, 360
    p = []
    p.append(text(W / 2, 32, "дві криві в одному конвеєрі", size=15, bold=True))

    # координатна рамка
    gx, gy, gw, gh = 90, 70, 300, 230
    p.append(rect(gx, gy, gw, gh, fill="#fbfcfe", stroke="#cfd8e3", sw=1.2))
    p.append(text(gx + gw / 2, gy + gh + 26, "фаза 0 → 1", size=11, color=MUTED))
    p.append(text(gx - 16, gy + gh / 2, "вихід", size=11, color=MUTED, anchor="middle"))

    def curve(fn, color, sw=2.4, dash=None):
        pts = []
        N = 48
        for i in range(N + 1):
            t = i / N
            v = fn(t)
            x = gx + t * gw
            y = gy + gh - v * gh
            pts.append("%.1f,%.1f" % (x, y))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" '
                'stroke-width="%.1f"%s/>' % (" ".join(pts), color, sw, d))

    # лінійна
    p.append(curve(lambda t: t, MUTED, sw=1.8, dash="5,4"))
    # плавний вхід-вихід (smoothstep)
    p.append(curve(lambda t: t * t * (3 - 2 * t), FIELD, sw=2.6))
    # «механічний» різкий старт для контрасту (ease-in квадрат)
    p.append(curve(lambda t: t * t, NEG, sw=2.0))

    # легенда
    lx, ly = 420, 95
    p.append(line(lx, ly, lx + 28, ly, color=MUTED, sw=1.8, dash="5,4"))
    p.append(text(lx + 36, ly + 4, "лінійна — рух механічний", size=11, color=INK, anchor="start"))
    p.append(line(lx, ly + 28, lx + 28, ly + 28, color=NEG, sw=2.0))
    p.append(text(lx + 36, ly + 32, "ease-in — рвучкий старт", size=11, color=INK, anchor="start"))
    p.append(line(lx, ly + 56, lx + 28, ly + 56, color=FIELD, sw=2.6))
    p.append(text(lx + 36, ly + 60, "плавний вхід-вихід — живий", size=11, color=INK, anchor="start"))

    # підказка про порядок
    box = fitbox(420, 200, 250, 110,
                 "порядок у коді:\nфаза → easing (форма руху)\n→ гамма (корекція ока)\n→ duty у ledcWrite",
                 size=11, fill="#fff8e8", stroke="#d99a00", sw=1.5)
    p.append(box)

    render(os.path.join(OUT, "curves.svg"), W, H, *p)


# ── 4. [hist-easing] єдиний роз'єм f(t,b,c,d), багато форм ─────────────────────
# Ідея: винахід Пеннера — не окрема крива, а СПІЛЬНИЙ інтерфейс. Усі функції беруть
# ті самі 4 аргументи й повертають значення; різна лише начинка (t², t³, sin, …).
def fig_easing_api():
    W, H = 760, 360
    p = []
    p.append(text(W / 2, 32, "один роз'єм f(t, b, c, d), багато форм", size=15, bold=True))

    # центральний «роз'єм» — підпис аргументів
    cx = W / 2
    sock = fitbox(cx - 150, 70, 300, 64,
                  "f(t, b, c, d) → значення\nt — час · b — початок · c — приріст · d — тривалість",
                  size=12, fill="#fff8e8", stroke="#d99a00", sw=1.8)
    p.append(sock)
    p.append(text(cx, 154, "однаковий зовні — різний усередині", size=11, color=MUTED))

    # маленькі картки форм із мінікривими
    forms = [
        ("Quad", lambda t: t * t, FIELD),
        ("Cubic", lambda t: t ** 3, FIELD),
        ("Sine", lambda t: math.sin(t * math.pi / 2), NEG),
        ("Expo", lambda t: (2 ** (10 * (t - 1))) if t > 0 else 0.0, NEG),
        ("Back", lambda t: t * t * (2.70158 * t - 1.70158), POS),
        ("Bounce", lambda t: _bounce(t), POS),
    ]
    bw, bh, gap = 108, 92, 12
    total = len(forms) * bw + (len(forms) - 1) * gap
    x0 = (W - total) / 2
    ty = 200
    for i, (name, fn, col) in enumerate(forms):
        x = x0 + i * (bw + gap)
        p.append(rect(x, ty, bw, bh, fill="#fbfcfe", stroke="#cfd8e3", sw=1.2))
        p.append(text(x + bw / 2, ty + 16, name, size=11, color=col, bold=True))
        # мінікрива в нижній частині картки
        gx, gy, gw, gh = x + 12, ty + 26, bw - 24, bh - 38
        pts = []
        Nn = 24
        for k in range(Nn + 1):
            t = k / Nn
            v = fn(t)
            v = max(-0.35, min(1.25, v))           # клампимо для картки
            xx = gx + t * gw
            yy = gy + gh - (v + 0.35) / 1.60 * gh   # вмістити діапазон −0.35..1.25
            pts.append("%.1f,%.1f" % (xx, yy))
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
                 % (" ".join(pts), col))
        # стрілка-зв'язок від роз'єму до картки
        p.append(line(cx, 136, x + bw / 2, ty, color="#d9cfa6", sw=1.0, dash="3,4"))

    p.append(text(W / 2, ty + bh + 26,
                  "поміняти форму = поміняти лише начинку, не торкаючись коду довкола",
                  size=11, color=INK))
    render(os.path.join(OUT, "easing-api.svg"), W, H, *p)


def _bounce(t):
    # easeOut-«відскок» Пеннера (для мінікривої картки)
    if t < 1 / 2.75:
        return 7.5625 * t * t
    elif t < 2 / 2.75:
        t -= 1.5 / 2.75
        return 7.5625 * t * t + 0.75
    elif t < 2.5 / 2.75:
        t -= 2.25 / 2.75
        return 7.5625 * t * t + 0.9375
    else:
        t -= 2.625 / 2.75
        return 7.5625 * t * t + 0.984375


# ── 5. [hist-easing] дерево портів: Flash → JS → усюди → прошивка ──────────────
# Ідея: набір пережив технологію. Оригінал на ActionScript (2002) розійшовся
# мовами й каркасами; та сама форма f(t,b,c,d) доходить аж до коду в нашому циклі.
def fig_easing_ports():
    W, H = 760, 380
    p = []
    p.append(text(W / 2, 32, "форма пережила технологію", size=15, bold=True))

    # корінь
    root = fitbox(W / 2 - 150, 56, 300, 50,
                  "ActionScript / Flash · 2002\nрівняння Пеннера, BSD",
                  size=12, fill="#fff8e8", stroke="#d99a00", sw=1.8)
    p.append(root)

    # ланка jQuery (Сміт, 2007)
    jq = fitbox(W / 2 - 120, 138, 240, 48,
                "плагін jQuery · 2007\n(Дж. Сміт) → jQuery UI",
                size=12, fill="#eaf0fd", stroke=NEG, sw=1.6)
    p.append(jq)
    p.append(line(W / 2, 106, W / 2, 138, color=MUTED, sw=1.6))

    # розгалуження мовами/каркасами
    leaves = ["JavaScript", "C# / Unity", "Java", "Swift", "Qt (C++)", "Python"]
    lw, lh, gap = 112, 40, 10
    total = len(leaves) * lw + (len(leaves) - 1) * gap
    x0 = (W - total) / 2
    ly = 232
    for i, name in enumerate(leaves):
        x = x0 + i * (lw + gap)
        p.append(fitbox(x, ly, lw, lh, name, size=11, fill=FILL, stroke=LINE, sw=1.3))
        p.append(line(W / 2, 186, x + lw / 2, ly, color=MUTED, sw=1.0))

    # фінальна ланка — прошивка
    fw = fitbox(W / 2 - 165, 306, 330, 50,
                "прошивка: shape(phase) у нашому циклі\nта сама f(t, b, c, d) на ESP32",
                size=12, fill="#eafaf0", stroke=FIELD, sw=1.8)
    p.append(fw)
    p.append(line(W / 2, ly + lh, W / 2, 306, color=FIELD, sw=1.8, dash="5,4"))

    render(os.path.join(OUT, "easing-ports.svg"), W, H, *p)


if __name__ == "__main__":
    fig_blocking_vs_tick()
    fig_phase_machine()
    fig_curves()
    fig_easing_api()
    fig_easing_ports()
    print("ok")
