# -*- coding: utf-8 -*-
"""Фігури до теми «Динамічний діапазон».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Динамічний діапазон: смуга між шумом і насиченням ─────────────────────
def fig_dynamic_range():
    W, H = 760, 420
    f = [text(W / 2, 26, "Сцена ширша за вікно сенсора", size=16, bold=True),
         text(W / 2, 46, "ловиться лише смуга — від підлоги шуму до насичення",
              size=12, color=MUTED)]

    # СЦЕНА: вертикальний градієнт від неба (світле) до тіні (темне)
    sx, sy, sw, sh = 150, 80, 90, 300
    n = 14
    for i in range(n):
        g = int(245 - i * (245 / (n - 1)))
        ry = sy + i * (sh / n)
        f.append('<rect x="%d" y="%.1f" width="%d" height="%.1f" fill="rgb(%d,%d,%d)"/>'
                 % (sx, ry, sw, sh / n + 0.6, g, g, g))
    f.append(rect(sx, sy, sw, sh, fill="none", stroke=INK, sw=1.5))
    f.append(text(sx + sw / 2, sy - 10, "СЦЕНА", size=11, bold=True))
    f.append(text(sx - 8, sy + 16, "небо", size=10, color=MUTED, anchor="end"))
    f.append(text(sx - 8, sy + sh - 6, "тінь", size=10, color=MUTED, anchor="end"))

    # ВІКНО сенсора — зелена рамка на середній смузі
    wx, wy, ww, wh = 250, 168, 56, 150
    f.append(rect(wx, wy, ww, wh, fill="#eafaef", stroke=FIELD, sw=2))
    f.append(line(sx + sw, wy, wx, wy, color=FIELD, sw=1.3, dash="4,3"))
    f.append(line(sx + sw, wy + wh, wx, wy + wh, color=FIELD, sw=1.3, dash="4,3"))
    f.append(text(wx + ww + 14, wy + wh / 2 - 4, "ВІКНО", size=11, color="#15803d",
                  anchor="start", bold=True))
    f.append(text(wx + ww + 14, wy + wh / 2 + 12, "сенсора", size=11, color="#15803d",
                  anchor="start", bold=True))
    f.append(text(wx + ww + 14, wy - 6, "вище → пересвіт", size=9.5, color=POS, anchor="start"))
    f.append(text(wx + ww + 14, wy + wh + 16, "нижче → провал", size=9.5, color=NEG, anchor="start"))

    # СТОПИ: пояснення подвоєння світла
    bx, by = 500, 110
    f.append(text(bx + 120, by - 14, "ширину міряють у СТОПАХ", size=11, bold=True))
    for i in range(5):
        yy = by + i * 30
        fill = "#eef2ff" if i % 2 == 0 else "#dbeafe"
        f.append(rect(bx, yy, 240, 24, fill=fill, stroke="#c7d2fe", sw=1, rx=6))
        f.append(text(bx + 10, yy + 16, "+1 стоп  =  ×2 світла", size=10,
                      anchor="start"))
    f.append(text(bx + 120, by + 168, "у сенсора 8–12 стопів,", size=10, color=MUTED))
    f.append(text(bx + 120, by + 184, "сонячна сцена буває й 20", size=10, color=MUTED))

    cap = ("Усе вище вікна вибілюється, усе нижче провалюється в чорноту — "
           "там нема даних, деталі втрачено.")
    f.append(text(W / 2, H - 14, cap, size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "dynamic-range.svg"), W, H, *f)


# ── 2. Три джерела шуму ──────────────────────────────────────────────────────
def fig_noise_types():
    W, H = 820, 380
    f = [text(W / 2, 26, "Три джерела зерна в кадрі", size=16, bold=True)]

    cw, cx0, cy, ch = 248, 20, 64, 250
    gap = 16

    # картка 1 — дробовий (фотонний)
    x = cx0
    f.append(rect(x, cy, cw, ch, fill="white", stroke=NEG, sw=1.9, rx=12))
    f.append(text(x + cw / 2, cy + 26, "ДРОБОВИЙ (фотонний)", size=12.5, color=NEG, bold=True))
    f.append(mtext(x + 16, cy + 50,
                   ["світло прилітає випадковими", "порціями — мало фотонів,",
                    "більше відносного зерна"], size=10, anchor="start"))
    # темне поле з рідкими крупинками
    f.append(rect(x + 20, cy + 96, 96, 78, fill="#0f172a", stroke=INK, sw=1, rx=4))
    import random
    random.seed(1)
    for _ in range(7):
        f.append(circle(x + 30 + random.random() * 76, cy + 106 + random.random() * 58,
                        2.4, fill="#e5e7eb", stroke="none"))
    f.append(text(x + 68, cy + 190, "темно", size=9, color=MUTED))
    # світле поле з густими крупинками
    f.append(rect(x + 130, cy + 96, 96, 78, fill="#334155", stroke=INK, sw=1, rx=4))
    for gx in range(8):
        for gy in range(5):
            f.append(circle(x + 140 + gx * 11, cy + 106 + gy * 14, 1.7,
                            fill="#e5e7eb", stroke="none"))
    f.append(text(x + 178, cy + 190, "світло", size=9, color=MUTED))
    f.append(text(x + cw / 2, cy + ch - 12, "фундамент — не вимкнути", size=9.5,
                  color=NEG, bold=True))

    # картка 2 — читання
    x = cx0 + cw + gap
    f.append(rect(x, cy, cw, ch, fill="white", stroke="#d98a00", sw=1.9, rx=12))
    f.append(text(x + cw / 2, cy + 26, "ЧИТАННЯ", size=12.5, color="#b06b00", bold=True))
    f.append(mtext(x + 16, cy + 50,
                   ["електроніка домішує крихту", "випадковості щоразу,",
                    "коли перетворює заряд на число"], size=10, anchor="start"))
    pts = []
    random.seed(7)
    for i in range(46):
        pts.append("%d,%.1f" % (x + 18 + i * 4.6, cy + 138 + random.random() * 12 - 6))
    f.append('<polyline points="%s" fill="none" stroke="#d98a00" stroke-width="1.4"/>'
             % " ".join(pts))
    f.append(line(x + 18, cy + 162, x + 230, cy + 162, color=MUTED, sw=1, dash="3,3"))
    f.append(text(x + cw / 2, cy + 186, "стала «підлога шуму»", size=9.5, color=MUTED))
    f.append(text(x + cw / 2, cy + ch - 12, "не залежить від світла", size=9.5,
                  color="#b06b00", bold=True))

    # картка 3 — тепловий
    x = cx0 + 2 * (cw + gap)
    f.append(rect(x, cy, cw, ch, fill="white", stroke=POS, sw=1.9, rx=12))
    f.append(text(x + cw / 2, cy + 26, "ТЕПЛОВИЙ (темновий)", size=12.5, color=POS, bold=True))
    f.append(mtext(x + 16, cy + 50,
                   ["нагрів сам народжує зайві", "електрони навіть у темряві —",
                    "гірше на спеці й довгій витримці"], size=10, anchor="start"))
    # термометр
    tx = x + 28
    f.append(rect(tx, cy + 100, 12, 64, fill="#fde2e2", stroke=INK, sw=1.2, rx=6))
    f.append(rect(tx, cy + 138, 12, 26, fill=POS, stroke="none", rx=6))
    f.append(circle(tx + 6, cy + 170, 11, fill=POS, stroke=INK, sw=1.2))
    # темне поле з гарячими крупинками
    f.append(rect(x + 70, cy + 104, 150, 64, fill="#0f172a", stroke=INK, sw=1, rx=4))
    random.seed(3)
    for _ in range(9):
        f.append(circle(x + 82 + random.random() * 130, cy + 114 + random.random() * 44,
                        2.5, fill="#fca5a5", stroke="none"))
    f.append(text(x + cw / 2, cy + ch - 12, "росте з нагрівом і витримкою", size=9.5,
                  color=POS, bold=True))

    f.append(text(W / 2, H - 12,
                  "Дробовий слабшає на світлі, читання сталий, тепловий росте з теплом — зерно різне.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "noise-types.svg"), W, H, *f)


# ── 3. Сигнал-шум: рятує лише світло ─────────────────────────────────────────
def fig_snr():
    W, H = 780, 400
    f = [text(W / 2, 26, "Лік від зерна — більше світла, а не підсилення", size=16, bold=True)]

    # темно: короткий сигнал, помітний шум
    f.append(text(160, 74, "ТЕМНО (мало фотонів)", size=12, color=NEG, bold=True))
    f.append(text(60, 96, "сигнал", size=9, color=MUTED, anchor="start"))
    f.append(rect(60, 100, 200, 26, fill="#e5e7eb", stroke="none", rx=4))
    f.append(rect(60, 100, 60, 26, fill=NEG, stroke="none", rx=4))
    f.append(text(60, 146, "шум", size=9, color=MUTED, anchor="start"))
    f.append(rect(60, 150, 200, 14, fill="#e5e7eb", stroke="none", rx=4))
    f.append('<rect x="60" y="150" width="44" height="14" rx="4" fill="%s" fill-opacity="0.6"/>' % POS)
    f.append(text(160, 192, "низький SNR → зернисто", size=11, color=POS, bold=True))

    # світло: довгий сигнал, дрібний шум
    f.append(text(160, 232, "СВІТЛО (багато фотонів)", size=12, color="#15803d", bold=True))
    f.append(text(60, 254, "сигнал", size=9, color=MUTED, anchor="start"))
    f.append(rect(60, 258, 200, 26, fill="#e5e7eb", stroke="none", rx=4))
    f.append(rect(60, 258, 184, 26, fill=FIELD, stroke="none", rx=4))
    f.append(text(60, 304, "шум", size=9, color=MUTED, anchor="start"))
    f.append(rect(60, 308, 200, 14, fill="#e5e7eb", stroke="none", rx=4))
    f.append('<rect x="60" y="308" width="26" height="14" rx="4" fill="%s" fill-opacity="0.6"/>' % POS)
    f.append(text(160, 350, "високий SNR → чисто", size=11, color="#15803d", bold=True))

    # формула
    f.append(rect(440, 96, 300, 96, fill="#f4f4f5", stroke=INK, sw=1.5, rx=10))
    f.append(text(590, 132, "SNR ∝ √(фотони)", size=16, bold=True))
    f.append(text(590, 160, "учетверо світла → удвічі чистіше", size=10.5, color=MUTED))
    f.append(text(590, 178, "учетверо менше зерна", size=10.5, color=MUTED))

    # підсилення
    f.append(rect(440, 224, 300, 130, fill="#fff5e6", stroke="#d98a00", sw=1.6, rx=10))
    f.append(text(590, 250, "А підсилення?", size=12, bold=True))
    f.append(mtext(590, 274,
                   ["множить і сигнал, І шум", "на одне число — відношення",
                    "від фотонного шуму не росте.", "Кадр яскравіє, та не чистіє."],
                   size=10, color=MUTED, lh=1.45))

    f.append(text(W / 2, H - 12,
                  "Єдиний справжній лік — більше фотонів: більший піксель, ширша діафрагма, довша витримка.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "snr.svg"), W, H, *f)


# ── 4. HDR: кілька витримок в один кадр ──────────────────────────────────────
def fig_hdr():
    W, H = 800, 400
    f = [text(W / 2, 26, "HDR: коли сцена ширша за сенсор", size=16, bold=True),
         text(W / 2, 46, "короткий кадр ловить світле, довгий — темне; зливаємо обидва",
              size=12, color=MUTED)]

    fw, fh, fy = 150, 130, 86

    def frame(x, top, bot, label, note, lc):
        out = [text(x + fw / 2, fy - 8, label, size=11.5, color=lc, bold=True)]
        out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="8" fill="%s"/>'
                   % (x, fy, fw, fh / 2, top))
        out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="8" fill="%s"/>'
                   % (x, fy + fh / 2, fw, fh / 2, bot))
        out.append(rect(x, fy, fw, fh, fill="none", stroke=INK, sw=1.6))
        out.append(text(x + fw / 2, fy + fh + 18, note, size=9.5, color=MUTED))
        return out

    f += frame(40, "#a5b4d8", "#000000", "КОРОТКИЙ кадр", "небо добре, тінь чорна", NEG)
    f.append(text(225, fy + fh / 2 + 6, "+", size=20, bold=True))
    f += frame(250, "#ffffff", "#6b7280", "ДОВГИЙ кадр", "тінь добре, небо біле", "#d98a00")
    f.append(arrow(420, fy + fh / 2, 460, fy + fh / 2, sw=2.4))
    f += frame(475, "#7c93c4", "#5b6470", "ЗЛИТО (HDR)", "і небо, і тінь видно", "#15803d")

    # пояснення для машинного бачення
    f.append(rect(660, fy, 130, fh, fill="#eafaef", stroke=FIELD, sw=1.5, rx=11))
    f.append(mtext(725, fy + 24,
                   ["для машинного", "бачення:", "", "вузький DR →", "ціль гине",
                    "в блиску чи тіні"], size=9.5, color="#15803d", lh=1.4))

    f.append(text(W / 2, H - 26,
                  "Склавши з кожного кадру добру частину, дістаємо ширший діапазон, ніж сенсор уловив би за раз.",
                  size=11, color=MUTED, italic=True))
    f.append(text(W / 2, H - 10,
                  "Та на рухомому апараті об'єкти зсуваються між кадрами — радше беруть сенсор із ширшим власним діапазоном.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "hdr.svg"), W, H, *f)


if __name__ == "__main__":
    fig_dynamic_range()
    fig_noise_types()
    fig_snr()
    fig_hdr()
    print("OK: dynamic-range, noise-types, snr, hdr")
