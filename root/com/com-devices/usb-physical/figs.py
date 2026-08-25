# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── four-wires: чотири провідники кабелю й що кожен робить ────────────────────
# Ідея: уся машинерія USB їде по двох сигнальних дротах; ще два — живлення.
# Видно поділ: VBUS/GND — енергія, D+/D− — вита пара даних (один логічний сигнал).
def fig_four_wires():
    W, H = 700, 320
    p = []
    cx = W / 2
    # оболонка кабелю
    p.append(rect(70, 70, W - 140, 180, fill="#f4f6f8", stroke=LINE, sw=1.6, rx=24))
    p.append(text(cx, 56, "Розріз стандартного USB-кабелю", size=13, color=MUTED, italic=True))
    # чотири жили
    wires = [
        (160, "VBUS", "+5 В", POS, "#fdecea", "живлення"),
        (300, "D−", "дані", NEG, "#eaf0fd", "вита пара"),
        (400, "D+", "дані", POS, "#fdecea", "вита пара"),
        (540, "GND", "0 В", INK, "#eef0f2", "спільна земля"),
    ]
    for x, name, val, col, fill, note in wires:
        p.append(circle(x, 150, 34, fill=fill, stroke=col, sw=2.4))
        p.append(text(x, 148, name, size=15, color=col, bold=True))
        p.append(text(x, 166, val, size=10, color=MUTED))
        p.append(text(x, 214, note, size=10, color=MUTED))
    # дужка над D+/D− — вони працюють як одна пара
    p.append(line(300, 104, 400, 104, color=FIELD, sw=2.0))
    p.append(line(300, 104, 300, 116, color=FIELD, sw=2.0))
    p.append(line(400, 104, 400, 116, color=FIELD, sw=2.0))
    p.append(text(350, 98, "одна диференційна пара", size=11, color=FIELD, bold=True))
    # підсумок
    p.append(fitbox(120, 268, W - 240, 34,
                    "Дані їдуть лише парою D+/D− · VBUS і GND несуть енергію",
                    size=12, fill="#eafaf1", stroke=FIELD, sw=1.5, bold=True))
    return render(os.path.join(OUT, "four-wires.svg"), W, H, *p,
                  title="Чотири дроти USB: дані та живлення")


# ── differential: чому різниця, а не рівень — завада гасне у відніманні ───────
# Ідея: біт несе РІЗНИЦЯ D+−D−. Синфазна завада зсуває обидва дроти однаково,
# тож у відніманні вона зникає — звідси завадостійкість і довгий кабель.
def fig_differential():
    W, H = 720, 420
    p = []
    x0, x1 = 90, W - 40
    mid = 150          # вісь верхньої пари
    amp = 34
    # ── верх: D+ і D− із накладеною синфазною завадою ──
    p.append(text(x0, mid - 96, "На дротах: корисний сигнал + спільна завада",
                  size=12, color=INK, anchor="start", bold=True))
    p.append(line(x0, mid, x1, mid, color=MUTED, sw=1.0, dash="3 3"))
    n = 9
    step = (x1 - x0) / n
    # завада — повільна хвиля, ОДНАКОВА на обох дротах
    import math
    def noise(i):
        return 26 * math.sin(i * 0.9)
    # D+ : високий там, де біт = J; D− дзеркальний; обидва зсунуті завадою разом
    pat = [1, 1, 0, 1, 0, 0, 1, 0, 1, 1]   # 1 → D+ вгорі
    dp = []; dm = []
    for i in range(n + 1):
        x = x0 + i * step
        b = pat[i]
        base_p = -amp if b else amp
        base_m = amp if b else -amp
        dp.append((x, mid + base_p + noise(i)))
        dm.append((x, mid + base_m + noise(i)))
    def poly(pts, col, sw):
        d = " ".join(("%.1f,%.1f" % (x, y)) for x, y in pts)
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, col, sw)
    p.append(poly(dp, POS, 2.4))
    p.append(poly(dm, NEG, 2.4))
    p.append(text(x1 + 4, dp[-1][1] + 4, "D+", size=12, color=POS, anchor="start", bold=True))
    p.append(text(x1 + 4, dm[-1][1] + 4, "D−", size=12, color=NEG, anchor="start", bold=True))
    # стрілка-завада
    p.append(text(x0, mid + 86, "завада зсуває D+ і D− РАЗОМ (синфазно)",
                  size=11, color=MUTED, anchor="start", italic=True))
    # ── низ: різниця D+−D− — завада зникла ──
    base = 330
    p.append(text(x0, base - 58, "Приймач бачить РІЗНИЦЮ D+ − D−: завада скоротилась",
                  size=12, color=INK, anchor="start", bold=True))
    p.append(line(x0, base, x1, base, color=MUTED, sw=1.0, dash="3 3"))
    diff = []
    for i in range(n + 1):
        x = x0 + i * step
        b = pat[i]
        diff.append((x, base + (-2 * amp if b else 2 * amp) * 0.7))
    # чистий прямокутний хід різниці
    d2 = []
    for i in range(n + 1):
        x = x0 + i * step
        y = diff[i][1]
        if i > 0:
            d2.append((x, diff[i - 1][1]))
        d2.append((x, y))
    p.append(poly(d2, INK, 2.6))
    p.append(text(x1 + 4, d2[-1][1] + 4, "D+−D−", size=11, color=INK, anchor="start", bold=True))
    p.append(fitbox(x0, base + 44, x1 - x0, 30,
                    "Однакова на обох дротах завада гине у відніманні → біт цілий",
                    size=11, fill="#eafaf1", stroke=FIELD, sw=1.4, bold=True))
    return render(os.path.join(OUT, "differential.svg"), W, H, *p,
                  title="Диференційна пара: чому різниця, а не рівень")


# ── speeds: три швидкості USB 2.0 на логарифмічній шкалі ──────────────────────
# Ідея: LS/FS/HS різняться на порядки (1.5 → 12 → 480 Мбіт/с); тому й фронтенд
# від найпростішого до складного. Лог-шкала чесно показує розрив у 320 разів.
def fig_speeds():
    W, H = 720, 330
    p = []
    import math
    x0, x1 = 120, W - 60
    base = 250
    speeds = [
        ("Low-Speed", "LS", 1.5, "1,5 Мбіт/с", "миша, клавіатура", NEG),
        ("Full-Speed", "FS", 12, "12 Мбіт/с", "більшість МК, аудіо, HID", FIELD),
        ("High-Speed", "HS", 480, "480 Мбіт/с", "диски, камери", POS),
    ]
    lo, hi = math.log10(1.0), math.log10(600.0)
    def sx(v):
        return x0 + (math.log10(v) - lo) / (hi - lo) * (x1 - x0)
    # вісь
    p.append(line(x0, base, x1, base, color=LINE, sw=1.6))
    for tick in (1, 10, 100):
        tx = sx(tick)
        p.append(line(tx, base - 4, tx, base + 4, color=MUTED, sw=1.0))
        p.append(text(tx, base + 20, str(tick), size=10, color=MUTED))
    p.append(text((x0 + x1) / 2, base + 40, "Мбіт/с (логарифмічна шкала)",
                  size=11, color=MUTED, italic=True))
    # стовпчики
    for name, ab, v, lab, use, col in speeds:
        bx = sx(v)
        bh = 30 + (math.log10(v) - lo) / (hi - lo) * 120
        p.append(rect(bx - 30, base - bh, 60, bh, fill=BG, stroke=col, sw=2.2, rx=5))
        p.append(text(bx, base - bh - 22, name, size=12, color=col, bold=True))
        p.append(text(bx, base - bh - 8, lab, size=10, color=INK))
        p.append(text(bx, base - bh / 2 + 4, ab, size=15, color=col, bold=True))
    p.append(text((x0 + x1) / 2, 300, "FS швидший за LS у 8 разів, HS за FS — у 40",
                  size=11, color=MUTED, italic=True))
    return render(os.path.join(OUT, "speeds.svg"), W, H, *p,
                  title="Три швидкості USB 2.0")


# ── pullup-speed: підтяжка визначає присутність І швидкість ───────────────────
# Ідея: одна підтяжка 1,5 кОм на 3,3 В вирішує дві задачі — каже хосту «я тут»
# і одразу декларує швидкість: на D+ → Full-Speed, на D− → Low-Speed.
def fig_pullup_speed():
    W, H = 720, 360
    p = []
    cases = [
        (180, "D+", "Full-Speed", "12 Мбіт/с", POS, "#fdecea"),
        (520, "D−", "Low-Speed", "1,5 Мбіт/с", NEG, "#eaf0fd"),
    ]
    for cx, pin, speed, rate, col, fill in cases:
        # хост ліворуч (pull-down), пристрій праворуч (pull-up)
        p.append(rect(cx - 130, 70, 100, 60, fill="#eef0f2", stroke=LINE, sw=1.4, rx=8))
        p.append(text(cx - 80, 96, "Хост", size=12, color=INK, bold=True))
        p.append(text(cx - 80, 114, "pull-down", size=9, color=MUTED))
        p.append(rect(cx + 30, 70, 110, 60, fill=fill, stroke=col, sw=1.8, rx=8))
        p.append(text(cx + 85, 96, "Пристрій", size=12, color=col, bold=True))
        p.append(text(cx + 85, 114, "pull-up 1,5 кОм", size=9, color=MUTED))
        # лінія, що піднялась
        ly = 170
        p.append(line(cx - 80, 130, cx - 80, ly, color=MUTED, sw=1.2))
        p.append(line(cx + 85, 130, cx + 85, ly, color=col, sw=2.0))
        p.append(line(cx - 80, ly, cx + 85, ly, color=col, sw=2.0))
        p.append(text(cx + 2, ly - 8, pin + " ↑ 3,3 В", size=12, color=col, bold=True))
        # підтяжка тягне на 3,3 В
        p.append(text(cx + 85, 152, "↑ до 3,3 В", size=9, color=col))
        # висновок
        b, bw, bh = textbox(cx, 232, [speed, rate], size=13, bold=True,
                            color=col, fill=BG, stroke=col, sw=2.0, min_w=150)
        p.append(b)
    # спільний підсумок
    p.append(fitbox(110, 290, W - 220, 38,
                    "Одна підтяжка робить дві справи: каже «пристрій тут» і декларує швидкість",
                    size=12, fill="#eafaf1", stroke=FIELD, sw=1.5, bold=True))
    return render(os.path.join(OUT, "pullup-speed.svg"), W, H, *p,
                  title="Підтяжка 1,5 кОм: присутність і швидкість")


# ════════════════════════════════════════════════════════════════════════════
#  Фігури для математичної вставки math-nrzi.md
# ════════════════════════════════════════════════════════════════════════════

# ── nrzi: 0 перемикає лінію, 1 лишає; інформація — у переходах ────────────────
def fig_nrzi():
    W, H = 720, 300
    p = []
    bits = [1, 0, 0, 1, 1, 1, 0, 1, 0]
    x0 = 80
    step = (W - 120) / len(bits)
    hi, lo = 120, 200          # рівні J / K
    # бітові підписи + сітка
    state = 0                  # 0 = J(hi), 1 = K(lo)
    levels = [hi]
    p.append(text(40, hi + 5, "J", size=13, color=POS, bold=True))
    p.append(text(40, lo + 5, "K", size=13, color=NEG, bold=True))
    prev_y = hi
    pts = [(x0, hi)]
    for i, b in enumerate(bits):
        x = x0 + i * step
        xn = x0 + (i + 1) * step
        p.append(line(x, 90, x, 230, color="#e3e6ea", sw=1.0))
        p.append(text(x + step / 2, 80, str(b), size=14,
                      color=(MUTED if b else INK), bold=True))
        if b == 0:
            state ^= 1          # перемкнути
        y = hi if state == 0 else lo
        if y != prev_y:
            pts.append((x, prev_y)); pts.append((x, y))
        pts.append((xn, y))
        prev_y = y
    p.append(line(x0 + len(bits) * step, 90, x0 + len(bits) * step, 230, color="#e3e6ea", sw=1.0))
    d = " ".join(("%.1f,%.1f" % (x, y)) for x, y in pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, INK))
    p.append(text(W / 2, 264, "0 → перехід (клацання) · 1 → лінія без змін",
                  size=12, color=MUTED, italic=True))
    p.append(text(W / 2, 282, "позиції 4–6: три одиниці підряд дають рівну ділянку без краю",
                  size=11, color=POS, italic=True))
    return render(os.path.join(OUT, "nrzi.svg"), W, H, *p,
                  title="NRZI: нуль перемикає, одиниця лишає")


# ── stuffing: вставлений 0 після 6 одиниць рятує синхронізацію ────────────────
def fig_stuffing():
    W, H = 740, 360
    p = []
    x0 = 70
    def draw_stream(bits, ytop, label, stuff_idx):
        step = (W - 110) / max(len(bits), 13)
        hi, lo = ytop, ytop + 70
        p.append(text(x0 - 30, ytop - 18, label, size=12, color=INK, anchor="start", bold=True))
        state = 0
        prev_y = hi
        pts = [(x0, hi)]
        for i, b in enumerate(bits):
            x = x0 + i * step
            xn = x0 + (i + 1) * step
            is_stuff = (stuff_idx is not None and i == stuff_idx)
            lab = "0*" if is_stuff else str(b)
            col = FIELD if is_stuff else (MUTED if b else INK)
            p.append(text(x + step / 2, ytop - 4, lab, size=12, color=col, bold=True))
            if b == 0:
                state ^= 1
            y = hi if state == 0 else lo
            if y != prev_y:
                pts.append((x, prev_y)); pts.append((x, y))
            pts.append((xn, y))
            prev_y = y
            if is_stuff:
                p.append(line(x, ytop - 16, x, lo + 14, color=FIELD, sw=1.2, dash="3 3"))
        d = " ".join(("%.1f,%.1f" % (x, y)) for x, y in pts)
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, INK))
        return step
    # без стафінгу: 6 одиниць → довга рівна ділянка
    draw_stream([0, 1, 1, 1, 1, 1, 1, 0], 90, "Без стафінгу: 6×1 — рівна лінія, такт «пливе»", None)
    p.append(text(W / 2, 188, "↑ довга тиша без переходу — приймач губить межі бітів",
                  size=11, color=POS, italic=True))
    # зі стафінгом: після 6 одиниць вставлено 0*
    draw_stream([0, 1, 1, 1, 1, 1, 1, 0, 0], 250, "Зі стафінгом: після 6×1 вставлено 0* → перехід", 7)
    p.append(fitbox(x0, 336, W - 110, 30,
                    "Гарантований край ≥ раз на 7 бітів ≈ 583 нс (Full-Speed); приймач знімає 0*",
                    size=11, fill="#eafaf1", stroke=FIELD, sw=1.4, bold=True))
    return render(os.path.join(OUT, "stuffing.svg"), W, H, *p,
                  title="Біт-стафінг: вставлений 0 після шести одиниць")


if __name__ == "__main__":
    fig_four_wires()
    fig_differential()
    fig_speeds()
    fig_pullup_speed()
    fig_nrzi()
    fig_stuffing()
    print("ok: four-wires, differential, speeds, pullup-speed, nrzi, stuffing")
