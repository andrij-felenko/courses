# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── trilemma: трикутник якість ↔ бітрейт ↔ затримка ──────────────────────────
# Ідея: три кути тягнуть одна одну; задаси два — третій визначиться. Праворуч —
# що чим платиш, і чому канал зазвичай забирає бітрейт.

def fig_trilemma():
    W, H = 720, 360
    p = []
    # трикутник
    ax, ay = 230, 80        # вершина — якість
    bx, by = 90, 300        # лівий низ — бітрейт
    cx, cy = 370, 300       # правий низ — затримка
    p.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="#eef4ff" '
             'stroke="%s" stroke-width="2.2" stroke-linejoin="round"/>'
             % (ax, ay, bx, by, cx, cy, INK))
    p.append(circle(ax, ay, 6, fill=FIELD, stroke=INK, sw=1.3))
    p.append(circle(bx, by, 6, fill=NEG, stroke=INK, sw=1.3))
    p.append(circle(cx, cy, 6, fill=POS, stroke=INK, sw=1.3))
    p.append(text(ax, ay - 12, "ЯКІСТЬ", size=13, color=FIELD, bold=True))
    p.append(text(bx - 4, by + 22, "БІТРЕЙТ", size=13, color=NEG, bold=True))
    p.append(text(cx + 4, cy + 22, "ЗАТРИМКА", size=13, color=POS, bold=True))
    p.append(mtext((ax + bx + cx) / 3, (ay + by + cy) / 3 - 4,
                   ["обери 2 —", "третя слідом"], size=11, color=INK, bold=True))

    # права панель — правило трьох ручок
    px = 430
    p.append(rect(px, 70, 250, 250, fill=FILL, stroke=INK, sw=1.4, rx=10))
    p.append(text(px + 125, 96, "правило трьох ручок", size=12, color=INK, bold=True))
    rows = [
        (FIELD, "Хочеш ЯКІСТЬ?", "плати бітрейтом або затримкою"),
        (NEG,   "Канал тисне БІТРЕЙТ?", "ріж якість або копи буфер (лаг)"),
        (POS,   "Мала ЗАТРИМКА?", "стиск гірший → якість чи біти"),
    ]
    ry = 124
    for col, head, sub in rows:
        p.append(circle(px + 16, ry - 4, 5, fill=col, stroke=INK, sw=1))
        p.append(text(px + 28, ry, head, size=10, color=col, anchor="start", bold=True))
        p.append(text(px + 28, ry + 15, sub, size=9, color=INK, anchor="start"))
        ry += 50
    p.append(rect(px + 14, 270, 222, 42, fill="#eef4ff", stroke=NEG, sw=1.3, rx=8))
    p.append(mtext(px + 125, 286,
                   ["Найчастіше канал ЗАДАЄ бітрейт —",
                    "лишається торг якість ↔ затримка"],
                   size=9, color=INK, bold=True))

    render(os.path.join(OUT, "trilemma.svg"), W, H, *p,
           title="Трикутник компромісу: задай дві ручки — третя визначиться")


# ── rate-distortion: крива «біти за якість» з насиченням і коліном ────────────
# Ідея: перша половина біт дає майже всю якість, далі крива вирівнюється; коліно
# — найвигідніша точка. Праворуч — дві стратегії: CBR проти VBR.

def fig_rate_distortion():
    W, H = 720, 360
    p = []
    ox, oy = 70, 300
    aw, ah = 300, 230
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "бітрейт →", size=10, color=MUTED, anchor="end", bold=True))
    p.append(text(ox + 4, oy - ah + 2, "↑ якість", size=10, color=MUTED, anchor="start", bold=True))

    # крива з насиченням
    pts = [(0, 0), (0.10, 0.42), (0.22, 0.62), (0.38, 0.76), (0.58, 0.86),
           (0.78, 0.92), (1.0, 0.96)]
    poly = " ".join("%.1f,%.1f" % (ox + x * aw, oy - y * ah) for x, y in pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" '
             'stroke-linejoin="round"/>' % (poly, NEG))

    # ліва точка — мало біт
    p.append(circle(ox + 0.10 * aw, oy - 0.42 * ah, 5, fill=POS, stroke=INK, sw=1))
    p.append(text(ox + 0.10 * aw + 12, oy - 0.42 * ah + 4,
                  "мало біт: блочно", size=9, color=POS, anchor="start"))
    # коліно
    kx, ky = ox + 0.30 * aw, oy - 0.70 * ah
    p.append(circle(kx, ky, 6.5, fill=FIELD, stroke=INK, sw=1.3))
    p.append(text(kx + 12, ky - 4, "«коліно»", size=10, color=FIELD, anchor="start", bold=True))
    p.append(text(kx + 12, ky + 10, "максимум якості за біт", size=9, color=FIELD, anchor="start"))
    # права — насичення
    p.append(circle(ox + 0.78 * aw, oy - 0.92 * ah, 5, fill=MUTED, stroke=INK, sw=1))
    p.append(text(ox + 0.78 * aw, oy - 0.92 * ah - 10,
                  "зиск дрібніє", size=9, color=MUTED))

    # права панель — CBR проти VBR
    px = 430
    p.append(rect(px, 96, 250, 196, fill=FILL, stroke=INK, sw=1.3, rx=10))
    p.append(text(px + 125, 120, "дві стратегії бітрейту", size=11, color=INK, bold=True))
    p.append(text(px + 16, 148, "CBR — сталий потік", size=10, color=NEG, anchor="start", bold=True))
    p.append(mtext(px + 16, 164, ["біти фіксовані, якість гуляє;", "рівно лягає у вузький канал"],
                   size=9, color=INK, anchor="start"))
    p.append(text(px + 16, 212, "VBR — змінний потік", size=10, color=POS, anchor="start", bold=True))
    p.append(mtext(px + 16, 228, ["якість стала, біти стрибають;", "для запису, та на каналі",
                                   "просить буфер → затримку"],
                   size=9, color=INK, anchor="start"))

    render(os.path.join(OUT, "rate-distortion.svg"), W, H, *p,
           title="Біти за якість: крута крива з насиченням")


# ── latency: ланцюг від скла до скла; де ховається лаг ────────────────────────
# Ідея: кадр іде сенсор → кодек → буфер → канал → буфер → декодер → екран.
# Фіксовані ланки не вкоротиш; кодек і буфери — головні схованки лагу.

def fig_latency():
    W, H = 720, 320
    p = []
    stages = [
        ("Сенсор", "захоплення", NEG),
        ("Кодек", "рух, B-кадри", POS),
        ("Буфер", "згладити", POS),
        ("Канал", "радіо/мережа", NEG),
        ("Буфер", "згладити", POS),
        ("Декодер", "зібрати", POS),
        ("Екран", "показ", FIELD),
    ]
    n = len(stages)
    bw, bh = 78, 64
    gap = (W - 2 * 30 - n * bw) / (n - 1)
    y = 96
    x = 30
    centers = []
    for i, (name, sub, col) in enumerate(stages):
        bx = x + i * (bw + gap)
        centers.append(bx + bw / 2)
        p.append(rect(bx, y, bw, bh, fill="#0f172a", stroke=col, sw=1.9, rx=7))
        p.append(text(bx + bw / 2, y + 26, name, size=11, color=col, bold=True))
        p.append(text(bx + bw / 2, y + 46, sub, size=9, color="#cbd5e1"))
        if i > 0:
            px0 = x + (i - 1) * (bw + gap) + bw
            p.append(arrow(px0 + 2, y + bh / 2, bx - 2, y + bh / 2, color=MUTED, sw=1.5))

    # підписи знизу: де лаг
    p.append(text((centers[0] + centers[3]) / 2, y + bh + 24,
                  "↑ фіксовані ланки — майже не вкоротиш", size=9, color=NEG))
    p.append(text((centers[1] + centers[5]) / 2, y + bh + 42,
                  "↑ кодек і буфери — головні схованки лагу", size=10, color=POS, bold=True))

    # рамка з рецептом
    box, w_, h_ = textbox(W / 2, y + bh + 92,
                          "Зрізати затримку = жертвувати стиском:  B-кадри геть · малий GOP · малий буфер · проста обробка",
                          size=10, fill="#fef9c3", stroke="#d98a00", sw=1.5, color=INK, bold=True)
    p.append(box)

    render(os.path.join(OUT, "latency.svg"), W, H, *p,
           title="Затримка від скла до скла — сума всіх ланок")


# ── profiles: три апарати — три кути трикутника ───────────────────────────────
# Ідея: гонка тягне за затримку, далекобій — за бітрейт/дальність, кінозйомка —
# за якість; той самий кодек, різні налаштування.

def fig_profiles():
    W, H = 720, 320
    p = []
    cards = [
        (POS, "ГОНОЧНИЙ FPV", "цар — ЗАТРИМКА",
         ["миттєвість понад усе", "жертва: чіткість, дальність",
          "intra-важко, малий буфер", "low-latency (720p120, <28 мс)"]),
        (NEG, "ДАЛЕКОБІЙ / HD", "тиск — БІТРЕЙТ",
         ["канал вузький на відстані", "тисне сильно (H.265)",
          "терпить десятки мс лагу", "якість — під залишок смуги"]),
        (FIELD, "ЗАПИС / КІНО", "цар — ЯКІСТЬ",
         ["не наживо → лаг байдужий", "B-кадри, великий буфер",
          "VBR, високий бітрейт", "макс. деталь і колір"]),
    ]
    cw = 220
    gap = (W - 2 * 20 - 3 * cw) / 2
    y = 70
    ch = 224
    for i, (col, title_, king, rows) in enumerate(cards):
        cx = 20 + i * (cw + gap)
        p.append(rect(cx, y, cw, ch, fill=FILL, stroke=col, sw=2.0, rx=12))
        p.append('<rect x="%.0f" y="%.0f" width="%.0f" height="34" rx="10" '
                 'fill="%s" fill-opacity="0.15"/>' % (cx, y, cw, col))
        p.append(text(cx + cw / 2, y + 22, title_, size=12, color=col, bold=True))
        p.append(text(cx + cw / 2, y + 56, king, size=11, color=INK, bold=True))
        ry = y + 84
        for r in rows:
            p.append(text(cx + 14, ry, "• " + r, size=9.5, color=INK, anchor="start"))
            ry += 24

    p.append(text(W / 2, y + ch + 28,
                  "Той самий кодек — різні налаштування: «найкращого» нема, є налаштований під місію",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "profiles.svg"), W, H, *p,
           title="Три апарати — три кути трикутника")


if __name__ == "__main__":
    fig_trilemma()
    fig_rate_distortion()
    fig_latency()
    fig_profiles()
    print("OK: figures written to", OUT)
