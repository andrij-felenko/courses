# -*- coding: utf-8 -*-
"""Фігури до теми «Моделі розповсюдження ITU-R і 3GPP».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Чому моделі: рівна пряма вільного простору проти хмари вимірів ─────────
def fig_why():
    W, H = 760, 430
    x0, y0 = 80, 60          # лівий-верх осей
    pw, ph = 600, 290        # поле графіка
    xr = x0 + pw
    yb = y0 + ph
    parts = []
    # осі
    parts.append(line(x0, y0, x0, yb, color=INK, sw=2))
    parts.append(line(x0, yb, xr, yb, color=INK, sw=2))
    parts.append(text(x0 - 12, y0 + 6, "втрати", size=12, color=MUTED, anchor="end"))
    parts.append(text(x0 - 12, y0 + 22, "(дБ)", size=12, color=MUTED, anchor="end"))
    parts.append(text(xr, yb + 26, "відстань (лог)", size=13, color=MUTED, anchor="end"))
    parts.append(text(x0, yb + 26, "близько", size=12, color=MUTED, anchor="middle"))
    parts.append(text(xr - 40, yb + 26, "далеко", size=12, color=MUTED, anchor="middle"))

    # лог-осі: x у відносних "декадах" 0..3, втрати ростуть ліворуч-униз→праворуч-угору
    def px(d):   # d у декадах 0..3
        return x0 + pw * d / 3.0
    def py(loss):  # loss 0..1 (частка висоти зверху)
        return y0 + ph * loss

    # пряма вільного простору: нахил 20 дБ/декаду → n=2
    fs = [(0.0, 0.12), (3.0, 0.92)]
    parts.append(line(px(fs[0][0]), py(fs[0][1]), px(fs[1][0]), py(fs[1][1]),
                      color=NEG, sw=3))
    parts.append(text(px(2.55), py(0.70) - 10, "вільний простір", size=13, color=NEG, bold=True, anchor="middle"))
    parts.append(text(px(2.55), py(0.70) + 8, "n = 2  (20 дБ/декаду)", size=11, color=NEG, anchor="middle"))

    # реальна "крутіша" пряма міста: n≈3.5 → 35 дБ/декаду
    rl = [(0.0, 0.16), (3.0, 1.0 - 0.02)]
    # хмара точок навколо неї (тінь — shadowing)
    import random
    random.seed(7)
    pts = []
    for k in range(46):
        d = random.uniform(0.15, 2.95)
        base = 0.16 + (0.98 - 0.16) * (d / 3.0)
        jit = random.uniform(-0.075, 0.075)   # ±~8 дБ розкид
        pts.append((d, max(0.05, min(0.99, base + jit))))
    for (d, l) in pts:
        parts.append(circle(px(d), py(l), 3.2, fill="#fbe3df", stroke=POS, sw=1.0))
    # лінія регресії крізь хмару
    parts.append(line(px(rl[0][0]), py(rl[0][1]), px(rl[1][0]), py(rl[1][1]),
                      color=POS, sw=3, dash="7 4"))
    parts.append(text(px(0.95), py(0.34) - 8, "реальне місто (виміри)", size=13, color=POS, bold=True, anchor="middle"))
    parts.append(text(px(0.95), py(0.34) + 9, "n ≈ 3.5  + розкид «тіні»", size=11, color=POS, anchor="middle"))

    # вертикальна двостороння стрілка — різниця = «що додає середовище»
    dx = px(2.4)
    parts.append(line(dx, py(0.585), dx, py(0.88), color=FIELD, sw=2))
    parts.append(arrow(dx, py(0.70), dx, py(0.585), color=FIELD, sw=2))
    parts.append(arrow(dx, py(0.70), dx, py(0.88), color=FIELD, sw=2))
    box = fitbox(dx + 12, py(0.66), 150, 40,
                 "це й описує\nмодель середовища", size=11, fill="#eafaf0", stroke=FIELD, color=FIELD)
    parts.append(box)

    render(os.path.join(IMG, "why-models.svg"), W, H, *parts,
           title="Вільний простір — лише підлога; середовище додає згори")


# ── 2. Спектр моделей: детерміновані ↔ емпіричні ↔ статистичні ───────────────
def fig_spectrum():
    W, H = 780, 360
    cy = 150
    x0, x1 = 60, 720
    # вісь-шкала
    parts = [line(x0, cy, x1, cy, color=INK, sw=2)]
    parts.append(arrow(x1 - 2, cy, x1 + 2, cy, color=INK, sw=2))
    parts.append(text((x0 + x1) / 2, 40, "Чим платимо за точність — обчисленнями й даними", size=15, bold=True, anchor="middle"))

    cols = [
        (170, "ДЕТЕРМІНОВАНІ", "трасування променів,\nкарта будинків",
         "найточніше для\nконкретного місця", "дуже дорого:\n3D-модель + годинник", NEG, "#eaf0fd"),
        (390, "ЕМПІРИЧНІ", "Okumura–Hata,\nCOST 231",
         "формула з вимірів,\nрахується миттєво", "лише в межах,\nде міряли", FIELD, "#eafaf0"),
        (610, "СТАТИСТИЧНІ", "3GPP TR 38.901,\nITU-R сценарії",
         "середнє + розкид\nдля класу місць", "не про твою точку,\nа про «типову»", POS, "#fbe3df"),
    ]
    for (cx, name, ex, plus_t, minus_t, col, fillc) in cols:
        parts.append(circle(cx, cy, 11, fill=col, stroke=INK, sw=1.5))
        # заголовок над віссю
        b = fitbox(cx - 95, 64, 190, 40, name, size=14, bold=True, fill=fillc, stroke=col, color=col)
        parts.append(b)
        parts.append(line(cx, 104, cx, cy - 11, color=col, sw=1.5, dash="3 3"))
        parts.append(fitbox(cx - 95, cy - 4 + 22, 190, 34, ex, size=11, fill=BG, stroke=MUTED, color=INK))
        # «+» і «−» нижче
        parts.append(plus(cx - 78, cy + 86, r=8))
        parts.append(mtext(cx - 62, cy + 80, plus_t, size=10.5, color=INK, anchor="start"))
        parts.append(minus(cx - 78, cy + 128, r=8))
        parts.append(mtext(cx - 62, cy + 122, minus_t, size=10.5, color=INK, anchor="start"))

    render(os.path.join(IMG, "model-spectrum.svg"), W, H, *parts)


# ── 3. Будова Okumura–Hata: рецепт у децибелах ───────────────────────────────
def fig_hata():
    W, H = 760, 470
    parts = []
    cx = W / 2
    # рядок-рецепт
    y = 80
    parts.append(text(cx, 42, "Hata: одна формула = вільний простір + поправки", size=15, bold=True, anchor="middle"))
    # центральна "сума"
    eqs = [
        ("A", "база від\nчастоти f", NEG, "#eaf0fd"),
        ("B·lg(h_b)", "висота\nбазової", FIELD, "#eafaf0"),
        ("C·lg(d)", "відстань d\n(нахил n)", POS, "#fbe3df"),
        ("− a(h_m)", "висота\nмобільного", "#7c3aed", "#f1eafd"),
        ("− K", "тип\nмісцевості", MUTED, FILL),
    ]
    bx = 50
    bw = 128
    gap = 14
    total = len(eqs) * bw + (len(eqs) - 1) * gap
    bx = (W - total) / 2
    for i, (sym, lab, col, fillc) in enumerate(eqs):
        x = bx + i * (bw + gap)
        parts.append(fitbox(x, y, bw, 46, sym, size=15, bold=True, fill=fillc, stroke=col, color=col))
        parts.append(fitbox(x, y + 54, bw, 38, lab, size=10.5, fill=BG, stroke=MUTED, color=INK))
        if i < len(eqs) - 1:
            parts.append(text(x + bw + gap / 2, y + 30, "+", size=20, color=INK, bold=True, anchor="middle"))
    parts.append(text(cx, y + 118, "L (дБ)  =  усе це додати", size=13, color=INK, bold=True, anchor="middle"))

    # рамка чинності
    vy = 250
    parts.append(fitbox(60, vy, W - 120, 36,
                        "ЧИННА ЛИШЕ В СВОЇХ МЕЖАХ — поза ними формула бреше:",
                        size=13, bold=True, fill="#fff7e6", stroke="#b9770e", color="#7a4d00"))
    ranges = [
        ("частота", "150–1500 МГц"),
        ("базова h_b", "30–200 м"),
        ("мобільний h_m", "1–10 м"),
        ("відстань d", "1–20 км"),
    ]
    rw = (W - 120) / 4
    for i, (k, v) in enumerate(ranges):
        x = 60 + i * rw
        parts.append(rect(x + 4, vy + 44, rw - 8, 58, fill=BG, stroke="#b9770e", sw=1.3))
        parts.append(text(x + rw / 2, vy + 66, k, size=11, color=MUTED, anchor="middle"))
        parts.append(text(x + rw / 2, vy + 88, v, size=13, color=INK, bold=True, anchor="middle"))

    # підказка про COST 231
    parts.append(fitbox(60, vy + 120, W - 120, 36,
                        "COST 231-Hata — той самий рецепт, перерахований на 1500–2000 МГц (для PCS/GSM-1800)",
                        size=12, fill="#eafaf0", stroke=FIELD, color="#145a32"))
    render(os.path.join(IMG, "hata-recipe.svg"), W, H, *parts)


# ── 4. Сценарії 3GPP/ITU: LOS/NLOS і «тінь» σ ────────────────────────────────
def fig_scenarios():
    W, H = 780, 430
    parts = []
    parts.append(text(W / 2, 40, "Сучасний підхід: спершу сценарій, тоді LOS чи NLOS", size=15, bold=True, anchor="middle"))

    scen = [
        ("RMa", "село / поле", "веж видно далеко", "#2e7d32", "#e7f6e9"),
        ("UMa", "місто, висока вежа", "над дахами", "#1565c0", "#e6f0fb"),
        ("UMi", "вулиця-каньйон", "низька вежа", "#c0392b", "#fbe3df"),
        ("InH", "у приміщенні", "офіс / зал", "#7c3aed", "#f1eafd"),
    ]
    cw = 175
    gap = 18
    total = 4 * cw + 3 * gap
    x0 = (W - total) / 2
    y0 = 70
    for i, (code, env, note, col, fillc) in enumerate(scen):
        x = x0 + i * (cw + gap)
        parts.append(rect(x, y0, cw, 86, fill=fillc, stroke=col, sw=2))
        parts.append(text(x + cw / 2, y0 + 30, code, size=22, color=col, bold=True, anchor="middle"))
        parts.append(text(x + cw / 2, y0 + 54, env, size=12, color=INK, anchor="middle"))
        parts.append(text(x + cw / 2, y0 + 73, note, size=10.5, color=MUTED, anchor="middle"))

    # розгалуження LOS / NLOS під кожним — показано на одному (UMi), решта натяком
    by = 200
    parts.append(text(W / 2, by - 8, "кожен сценарій далі ділиться:", size=12, color=MUTED, anchor="middle"))
    # LOS гілка
    lx = W / 2 - 200
    parts.append(fitbox(lx - 90, by + 6, 180, 52,
                        "LOS — видимість пряма\nм'який нахил, мала тінь σ",
                        size=11.5, bold=True, fill="#eafaf0", stroke=FIELD, color="#145a32"))
    # NLOS гілка
    rx = W / 2 + 200
    parts.append(fitbox(rx - 90, by + 6, 180, 52,
                        "NLOS — крізь перепони\nкрутіший нахил, велика тінь σ",
                        size=11.5, bold=True, fill="#fbe3df", stroke=POS, color="#7a1f14"))

    # формула-кістяк
    fy = 300
    parts.append(fitbox(80, fy, W - 160, 46,
                        "L = A + B·lg(d) + C·lg(f)   +   X_σ   (випадкова «тінь», нормальна, σ дБ)",
                        size=14, bold=True, fill=FILL, stroke=INK, color=INK))
    parts.append(text(W / 2, fy + 72, "Та сама арифметика дБ — плюс чесно дописаний розкид місць",
                      size=12, color=MUTED, anchor="middle"))
    parts.append(text(W / 2, fy + 92, "Працює аж до 100 ГГц (mmWave) — туди, куди Hata не сягає",
                      size=12, color=MUTED, anchor="middle"))
    render(os.path.join(IMG, "scenarios-3gpp.svg"), W, H, *parts)


# ── 5. Дзеркало dB↔лінійне: симетричний дзвін у дБ → перекошений у разах ──────
def fig_lognormal():
    import math
    W, H = 780, 410
    parts = []
    parts.append(text(W / 2, 32, "Та сама тінь: симетрична в децибелах — перекошена в разах", size=15, bold=True, anchor="middle"))

    # ЛІВА панель: гаусіана по осі дБ (відхилення від середнього)
    lx0, lph, lpw = 70, 250, 300
    lyb = 110 + lph
    parts.append(line(lx0, 110, lx0, lyb, color=INK, sw=2))
    parts.append(line(lx0, lyb, lx0 + lpw, lyb, color=INK, sw=2))
    parts.append(text(lx0 + lpw / 2, 100, "у децибелах (X_σ)", size=12, bold=True, color=NEG, anchor="middle"))
    # симетрична крива
    sig = 7.0
    def gx(v):  # v у дБ, діапазон -22..22
        return lx0 + lpw * (v + 22) / 44.0
    def gy(p, pmax):  # p густина
        return lyb - (lph - 18) * p / pmax
    pts = []
    pmax = 1.0 / (sig * math.sqrt(2 * math.pi))
    for k in range(0, 101):
        v = -22 + 44 * k / 100.0
        p = math.exp(-(v * v) / (2 * sig * sig)) / (sig * math.sqrt(2 * math.pi))
        pts.append((gx(v), gy(p, pmax)))
    poly = " ".join("%.1f,%.1f" % q for q in pts)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (poly, NEG))
    # вісь нуля (середнє)
    parts.append(line(gx(0), 122, gx(0), lyb, color=MUTED, sw=1.3, dash="4 3"))
    parts.append(text(gx(0), lyb + 18, "0", size=11, color=MUTED, anchor="middle"))
    parts.append(text(gx(-15), lyb + 18, "−15", size=10.5, color=MUTED, anchor="middle"))
    parts.append(text(gx(15), lyb + 18, "+15", size=10.5, color=MUTED, anchor="middle"))
    parts.append(text(lx0 + lpw / 2, lyb + 34, "відхилення, дБ", size=11, color=MUTED, anchor="middle"))
    # позначка ±σ
    parts.append(line(gx(-sig), gy(pmax * 0.607, pmax), gx(-sig), lyb, color=NEG, sw=1, dash="2 2"))
    parts.append(line(gx(sig), gy(pmax * 0.607, pmax), gx(sig), lyb, color=NEG, sw=1, dash="2 2"))
    parts.append(mtext(gx(0), 150, "симетрична\n(нормальна)", size=11, color=NEG, anchor="middle"))

    # стрілка-перехід
    parts.append(text(W / 2 - 8, 235, "10^(x/10)", size=11, color=INK, anchor="middle", italic=True))
    parts.append(arrow(lx0 + lpw + 12, 245, lx0 + lpw + 58, 245, color=INK, sw=2))

    # ПРАВА панель: логнормальна по лінійній осі (множник до втрат, у разах)
    rx0 = 470
    rpw = 250
    parts.append(line(rx0, 110, rx0, lyb, color=INK, sw=2))
    parts.append(line(rx0, lyb, rx0 + rpw, lyb, color=INK, sw=2))
    parts.append(text(rx0 + rpw / 2, 100, "у разах (×)", size=12, bold=True, color=POS, anchor="middle"))
    # логнормальна: x = 10^(v/10), щільність перекошена
    def rxf(mult):  # mult 0..6 разів
        return rx0 + rpw * min(mult, 6.0) / 6.0
    pts2 = []
    # параметри: mediana=1 (0 дБ), у "разах" розмах праворуч більший
    s_ln = sig / (10.0 / math.log(10))   # σ у натуральному лозі
    rpmax = 0
    raw = []
    for k in range(1, 200):
        x = 6.0 * k / 200.0
        if x <= 0.02:
            continue
        p = math.exp(-((math.log(x)) ** 2) / (2 * s_ln * s_ln)) / (x * s_ln * math.sqrt(2 * math.pi))
        raw.append((x, p))
        rpmax = max(rpmax, p)
    for (x, p) in raw:
        pts2.append((rxf(x), lyb - (lph - 18) * p / rpmax))
    poly2 = " ".join("%.1f,%.1f" % q for q in pts2)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (poly2, POS))
    parts.append(line(rxf(1), 122, rxf(1), lyb, color=MUTED, sw=1.3, dash="4 3"))
    for m in (1, 2, 3, 4, 5):
        parts.append(text(rxf(m), lyb + 18, "×%d" % m, size=10.5, color=MUTED, anchor="middle"))
    parts.append(text(rx0 + rpw / 2, lyb + 34, "у скільки разів гірше", size=11, color=MUTED, anchor="middle"))
    parts.append(mtext(rxf(2.6), 165, "довгий хвіст\nправоруч", size=11, color=POS, anchor="middle"))

    render(os.path.join(IMG, "lognormal-mirror.svg"), W, H, *parts,
           title=None)


# ── 6. Запас на затінення: хвіст Q-функції під задане покриття ────────────────
def fig_margin():
    import math
    W, H = 780, 420
    parts = []
    parts.append(text(W / 2, 32, "Запас на затінення = скільки σ відрізати, щоб накрити p% місць", size=15, bold=True, anchor="middle"))

    x0, y0 = 70, 70
    pw, ph = 640, 250
    yb = y0 + ph
    parts.append(line(x0, y0, x0, yb, color=INK, sw=2))
    parts.append(line(x0, yb, x0 + pw, yb, color=INK, sw=2))
    parts.append(text(x0 + pw / 2, yb + 50, "втрати X_σ відносно середнього (в одиницях σ)", size=12, color=MUTED, anchor="middle"))

    sig_px = 1.0
    lo, hi = -3.2, 3.2
    def mx(z):
        return x0 + pw * (z - lo) / (hi - lo)
    pmax = 1.0 / math.sqrt(2 * math.pi)
    def my(p):
        return yb - (ph - 24) * p / pmax
    # крива
    curve = []
    for k in range(0, 161):
        z = lo + (hi - lo) * k / 160.0
        p = math.exp(-z * z / 2) / math.sqrt(2 * math.pi)
        curve.append((mx(z), my(p)))
    # заливка хвоста (z > 1.645) — «місця, де сигнал гірший за запас» = аварія
    zc = 1.645
    tail = [(mx(zc), yb)]
    for k in range(0, 161):
        z = lo + (hi - lo) * k / 160.0
        if z >= zc:
            p = math.exp(-z * z / 2) / math.sqrt(2 * math.pi)
            tail.append((mx(z), my(p)))
    tail.append((mx(hi), yb))
    polyt = " ".join("%.1f,%.1f" % q for q in tail)
    parts.append('<polygon points="%s" fill="#fbe3df" stroke="none" opacity="0.9"/>' % polyt)
    # тіло «накрито» (z < zc) злегка зелене
    body = [(mx(lo), yb)]
    for k in range(0, 161):
        z = lo + (hi - lo) * k / 160.0
        if z <= zc:
            p = math.exp(-z * z / 2) / math.sqrt(2 * math.pi)
            body.append((mx(z), my(p)))
    body.append((mx(zc), yb))
    polyb = " ".join("%.1f,%.1f" % q for q in body)
    parts.append('<polygon points="%s" fill="#eafaf0" stroke="none" opacity="0.8"/>' % polyb)
    poly = " ".join("%.1f,%.1f" % q for q in curve)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (poly, NEG))

    # лінія порогу-запасу
    parts.append(line(mx(zc), y0 + 6, mx(zc), yb, color=POS, sw=2.2))
    parts.append(text(mx(zc), y0 - 2, "запас = 1.645σ", size=12, bold=True, color=POS, anchor="middle"))
    # вісь нуля
    parts.append(line(mx(0), my(pmax) - 4, mx(0), yb, color=MUTED, sw=1.2, dash="4 3"))
    for z in (-3, -2, -1, 0, 1, 2, 3):
        parts.append(text(mx(z), yb + 18, ("%+d" % z if z else "0") + "σ", size=10.5, color=MUTED, anchor="middle"))

    # підписи площ
    parts.append(mtext(mx(-0.2), my(pmax) * 0.0 + 150, "накрито 95% місць\n(сигнал кращий за запас)",
                       size=11.5, bold=True, color="#145a32", anchor="middle"))
    parts.append(mtext(mx(2.35), my(0.02) - 60, "5% — тут сигнал\nслабший: аварія",
                       size=11, bold=True, color="#7a1f14", anchor="middle"))
    # підпис Q
    parts.append(fitbox(x0 + 8, yb + 60, pw - 16, 30,
                        "затемнена площа праворуч = Q(1.645) ≈ 0.05 — частка місць, де навіть запасу замало",
                        size=12, fill=FILL, stroke=MUTED, color=INK))
    render(os.path.join(IMG, "shadow-margin.svg"), W, H, *parts, title=None)


# ── 7. σ за середовищами: чим заплутаніший шлях, тим ширший дзвін ─────────────
def fig_sigma_env():
    import math
    W, H = 780, 410
    parts = []
    parts.append(text(W / 2, 32, "Більше перешкод на шляху — ширший дзвін затінення (більший σ)", size=15, bold=True, anchor="middle"))

    x0, y0 = 70, 80
    pw, ph = 640, 230
    yb = y0 + ph
    parts.append(line(x0, yb, x0 + pw, yb, color=INK, sw=2))
    parts.append(text(x0 + pw / 2, yb + 52, "відхилення рівня від середнього, дБ", size=12, color=MUTED, anchor="middle"))
    lo, hi = -26, 26
    def mx(v):
        return x0 + pw * (v - lo) / (hi - lo)
    for v in range(-24, 25, 6):
        parts.append(line(mx(v), yb, mx(v), yb + 5, color=MUTED, sw=1))
        parts.append(text(mx(v), yb + 20, ("%+d" % v if v else "0"), size=10, color=MUTED, anchor="middle"))
    # вісь середнього
    parts.append(line(mx(0), y0 - 4, mx(0), yb, color=MUTED, sw=1.2, dash="4 3"))

    # три гаусіани з різним σ; нормуємо ВИСОТУ на спільний пік, щоб усі читалися
    curves = [
        (3.0, NEG,   "LOS — пряма видимість", "σ ≈ 3–4 дБ", -1),
        (8.0, POS,   "NLOS — крізь перепони", "σ ≈ 8 дБ", +1),
    ]
    topp = ph - 26
    for sig, col, name, slab, side in curves:
        pts = []
        for k in range(0, 241):
            v = lo + (hi - lo) * k / 240.0
            p = math.exp(-(v * v) / (2 * sig * sig))   # нормований на пік=1
            pts.append((mx(v), yb - topp * p))
        poly = " ".join("%.1f,%.1f" % q for q in pts)
        parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (poly, col))
        # підпис біля піка, зсунутий убік
        lx = mx(side * (sig + 4))
        parts.append(mtext(lx, y0 + 14, name + "\n" + slab, size=11.5, bold=True, color=col,
                           anchor=("start" if side > 0 else "end")))
        # позначка ширини ±σ внизу
        yh = yb - topp * math.exp(-0.5)   # висота на ±σ
        parts.append(line(mx(-sig), yh, mx(sig), yh, color=col, sw=1.2, dash="3 3"))

    # «вільний простір» — гострий пік біля нуля (σ→мале): тонка стрілка
    parts.append(line(mx(0), yb - topp, mx(0), yb, color=FIELD, sw=3))
    # підпис ліворуч у вільному полі, зі стрілкою до піка
    parts.append(mtext(mx(-13.5), yb - topp + 10, "вільний простір:\nрозкиду майже нема",
                       size=11, bold=True, color=FIELD, anchor="middle"))
    parts.append(arrow(mx(-8.0), yb - topp + 6, mx(-1.4), yb - topp + 2, color=FIELD, sw=1.6))

    render(os.path.join(IMG, "sigma-by-env.svg"), W, H, *parts, title=None)


# ── 7. Поправка a(h_m): лінійна (середнє місто) проти параболи (велике) ───────
def fig_ahm():
    """a(h_m) vs h_m на 900 МГц: середнє місто — лінійна; велике — квадратична."""
    import math as _m
    W, H = 760, 440
    x0, y0 = 86, 70
    pw, ph = 580, 280
    xr, yb = x0 + pw, y0 + ph
    parts = []
    parts.append(text(W / 2, 40, "Поправка a(h_m) на 900 МГц: середнє місто vs велике", size=15, bold=True, anchor="middle"))

    hm_min, hm_max = 1.0, 10.0          # м
    a_min, a_max = -2.0, 24.0           # дБ (вміщає обидві криві до h_m=10)
    lgf = _m.log10(900.0)

    def a_medium(hm):
        return (1.1 * lgf - 0.7) * hm - (1.56 * lgf - 0.8)

    def a_large(hm):                    # гілка 200<f<=1500 МГц
        return 3.20 * (_m.log10(11.75 * hm)) ** 2 - 4.97

    def px(hm):
        return x0 + pw * (hm - hm_min) / (hm_max - hm_min)

    def py(a):
        return yb - ph * (a - a_min) / (a_max - a_min)

    parts.append(line(x0, y0, x0, yb, color=INK, sw=2))
    parts.append(line(x0, yb, xr, yb, color=INK, sw=2))
    parts.append(text(x0 - 12, y0 + 4, "a(h_m), дБ", size=12, color=MUTED, anchor="end"))
    parts.append(text(xr, yb + 30, "висота мобільної антени h_m, м", size=12, color=MUTED, anchor="end"))
    for hv in (1, 2, 4, 6, 8, 10):
        parts.append(line(px(hv), yb, px(hv), yb + 5, color=MUTED, sw=1))
        parts.append(text(px(hv), yb + 20, str(hv), size=11, color=MUTED, anchor="middle"))
    for av in (0, 8, 16, 24):
        parts.append(line(x0 - 5, py(av), x0, py(av), color=MUTED, sw=1))
        parts.append(text(x0 - 10, py(av) + 4, str(av), size=11, color=MUTED, anchor="end"))
        parts.append(line(x0, py(av), xr, py(av), color="#e5e7eb", sw=1))

    parts.append(line(px(1.5), y0, px(1.5), yb, color=MUTED, sw=1.2, dash="5 4"))
    parts.append(text(px(1.5) + 6, y0 + 14, "1.5 м (носимий)", size=10.5, color=MUTED, anchor="start"))

    def polyline(fn, color):
        pts = []
        n = 60
        for i in range(n + 1):
            hm = hm_min + (hm_max - hm_min) * i / n
            pts.append("%.1f,%.1f" % (px(hm), py(fn(hm))))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
                % (" ".join(pts), color))

    parts.append(polyline(a_medium, FIELD))
    parts.append(polyline(a_large, POS))

    parts.append(text(px(7.0) + 40, py(a_medium(7.0)) - 6, "середнє місто", size=12, color=FIELD, bold=True, anchor="start"))
    parts.append(text(px(7.0) + 40, py(a_medium(7.0)) + 9, "(лінійна за h_m)", size=10.5, color=FIELD, anchor="start"))
    parts.append(text(px(7.4), py(a_large(7.4)) + 26, "велике місто", size=12, color=POS, bold=True, anchor="middle"))
    parts.append(text(px(7.4), py(a_large(7.4)) + 41, "(парабола за lg h_m)", size=10.5, color=POS, anchor="middle"))

    render(os.path.join(IMG, "ahm-curves.svg"), W, H, *parts)


# ── 8. Драбина знижок за тип місцевості (900 МГц) ────────────────────────────
def fig_terrain():
    """Місто → передмістя → відкрите: децибельна драбина знижок (абс. втрати)."""
    W, H = 760, 400
    parts = []
    parts.append(text(W / 2, 40, "Знижка за відкритість місцевості (900 МГц, та сама траса)", size=15, bold=True, anchor="middle"))

    base_y = 330           # низ стовпців
    top_city = 92          # верх стовпця міста (повні втрати)
    full = base_y - top_city
    levels = [
        ("щільне\nмісто", 0.0, "L_U (повні втрати)", POS, "#fbe3df"),
        ("перед-\nмістя", 9.9, "−9.9 дБ", FIELD, "#eafaf0"),
        ("відкрите\nполе", 28.5, "−28.5 дБ", NEG, "#eaf0fd"),
    ]
    bw, gap = 150, 70
    total = 3 * bw + 2 * gap
    x0 = (W - total) / 2
    span = 34.0            # дБ, що відповідає повній висоті стовпця міста
    for i, (lab, drop, note, col, fillc) in enumerate(levels):
        x = x0 + i * (bw + gap)
        col_top = top_city + full * (drop / span)
        parts.append(rect(x, col_top, bw, base_y - col_top, fill=fillc, stroke=col, sw=2))
        parts.append(fitbox(x + 12, base_y - 48, bw - 24, 36, lab, size=12.5, bold=True, fill=BG, stroke=col, color=col))
        parts.append(text(x + bw / 2, col_top - 12, note, size=12, color=col, bold=True, anchor="middle"))
        if i > 0:
            ax = x - gap / 2
            parts.append(line(ax, top_city, ax, col_top, color=MUTED, sw=1.4, dash="4 3"))
            parts.append(arrow(ax, top_city + 4, ax, col_top, color=MUTED, sw=1.4))

    parts.append(line(x0 - 10, top_city, x0 + total + 10, top_city, color=POS, sw=1.2, dash="6 4"))
    parts.append(text(x0 + total + 8, top_city - 6, "рівень міста", size=10.5, color=POS, anchor="end"))
    parts.append(text(W / 2, base_y + 42, "Менше забудови — менше втрат; кожна сходинка — поправка-знижка Хати", size=11.5, color=MUTED, anchor="middle"))
    render(os.path.join(IMG, "terrain-ladder.svg"), W, H, *parts)


# ── 9. Чотири діапазони чинності й «зламані» краї ─────────────────────────────
def fig_validity():
    """Смуги чинності Hata; за краєм — заштрихована зона екстраполяції."""
    W, H = 880, 400
    parts = []
    parts.append(text(W / 2, 40, "Чотири діапазони чинності Hata — і що за краєм", size=15, bold=True, anchor="middle"))

    rows = [
        ("частота f", "150", "1500", "МГц", "Wi-Fi 2.4 ГГц → інша модель"),
        ("відстань d", "1", "20", "км", "<1 км → завищує (ще LOS)"),
        ("вежа h_b", "30", "200", "м", "нижче дахів → інший режим"),
        ("мобільний h_m", "1", "10", "м", "висока щогла → парабола бреше"),
    ]
    lx = 60
    bx0, bx1, bxe = 196, 506, 600
    y, dy = 88, 70
    for (lab, lo, hi, unit, broke) in rows:
        cy = y + 18
        parts.append(text(lx, cy + 4, lab, size=12.5, color=INK, bold=True, anchor="start"))
        parts.append(rect(bx0, y, bx1 - bx0, 36, fill="#eafaf0", stroke=FIELD, sw=2))
        parts.append(text((bx0 + bx1) / 2, cy + 5, "формула спирається на виміри", size=11, color="#145a32", anchor="middle"))
        parts.append(text(bx0, y - 6, lo + " " + unit, size=11, color=INK, anchor="middle"))
        parts.append(text(bx1, y - 6, hi + " " + unit, size=11, color=INK, anchor="middle"))
        parts.append(rect(bx1, y, bxe - bx1, 36, fill="#fdecea", stroke=POS, sw=1.5))
        sx = bx1 + 6
        while sx < bxe - 2:
            parts.append(line(sx, y + 34, min(sx + 16, bxe - 2), y + 2, color="#e8a99f", sw=1))
            sx += 12
        parts.append(text(bxe + 10, cy + 4, broke, size=10, color=POS, anchor="start"))
        y += dy

    parts.append(text(W / 2, y + 4, "Усередині — реальні дані; за краєм формула рахує, але підстав немає", size=11.5, color=MUTED, anchor="middle"))
    render(os.path.join(IMG, "validity-edges.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_why()
    fig_spectrum()
    fig_hata()
    fig_scenarios()
    fig_lognormal()
    fig_margin()
    fig_sigma_env()
    fig_ahm()
    fig_terrain()
    fig_validity()
    print("OK figs ->", IMG)
