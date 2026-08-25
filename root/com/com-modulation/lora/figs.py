# -*- coding: utf-8 -*-
"""Фігури теми «LoRa (чирп-модуляція)». Запуск: python figs.py → ./img/*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: що таке чирп — тон проти лінійно «їдучої» частоти ───────────────
# Площина «частота × час». Зліва: звичайний тон — горизонтальна лінія (одна
# частота весь час). Справа: чирп — частота рівно «їде» знизу вгору, проходячи
# всю смугу BW за час символа. Та сама енергія розмазана по всій смузі.
def fig_what_is_chirp():
    W, H = 680, 360
    # дві однакові панелі
    panels = [(60, "тон: одна частота", False), (380, "чирп: частота лінійно «їде»", True)]
    pw, ph = 240, 220
    py0 = 70
    parts = []
    for px0, caption, is_chirp in panels:
        # осі панелі
        parts.append(arrow(px0 - 6, py0 + ph, px0 + pw + 14, py0 + ph, color=MUTED, sw=1.3))  # t
        parts.append(arrow(px0, py0 + ph + 6, px0, py0 - 14, color=MUTED, sw=1.3))            # f
        parts.append(text(px0 + pw + 12, py0 + ph + 16, "час", 11, MUTED, "middle"))
        parts.append(text(px0 - 2, py0 - 18, "частота", 11, MUTED, "middle"))
        # межі смуги BW (верх/низ діапазону)
        ftop, fbot = py0 + 20, py0 + ph - 20
        parts.append(line(px0, ftop, px0 + pw, ftop, color=MUTED, sw=1.0, dash="3 4"))
        parts.append(line(px0, fbot, px0 + pw, fbot, color=MUTED, sw=1.0, dash="3 4"))
        parts.append(text(px0 + pw - 4, ftop - 6, "верх смуги", 10, MUTED, "end"))
        parts.append(text(px0 + pw - 4, fbot + 14, "низ смуги", 10, MUTED, "end"))
        if not is_chirp:
            # горизонтальна лінія посередині смуги
            fy = (ftop + fbot) / 2
            parts.append(line(px0, fy, px0 + pw, fy, color=NEG, sw=3.0))
        else:
            # пилоподібний підйом: частота їде вгору, дійшовши верху — стрибок униз
            seg = pw  # один повний прохід за символ
            parts.append(line(px0, fbot, px0 + seg, ftop, color=POS, sw=3.0))
            # стрілка напрямку
            parts.append(text(px0 + pw * 0.5 + 18, (ftop + fbot) / 2 - 6, "↗", 18, POS, "middle"))
        parts.append(text(px0 + pw / 2, py0 + ph + 36, caption, 11, INK, "middle"))
    render(os.path.join(IMG, "what-is-chirp.svg"), W, H, *parts,
           title="Чирп: частота рівномірно «їде» через усю смугу")


# ── Фігура 2: як чирп несе дані — циклічний зсув старту ───────────────────────
# Базовий up-chirp їде від низу до верху. Дані кодуються СТАРТОВОЮ частотою:
# чирп стартує з іншого місця, дійшовши верху — «загортається» вниз і доїжджає.
# Три приклади символів з різним стартом = різні значення.
def fig_chirp_symbol():
    W, H = 680, 360
    px0, py0, pw, ph = 90, 70, 480, 210
    ftop, fbot = py0 + 14, py0 + ph - 14
    parts = []
    parts.append(arrow(px0 - 6, py0 + ph, px0 + pw + 14, py0 + ph, color=MUTED, sw=1.3))
    parts.append(arrow(px0, py0 + ph + 6, px0, py0 - 14, color=MUTED, sw=1.3))
    parts.append(text(px0 + pw + 12, py0 + ph + 16, "час (один символ)", 11, MUTED, "end"))
    parts.append(text(px0 - 2, py0 - 18, "частота", 11, MUTED, "middle"))
    parts.append(line(px0, ftop, px0 + pw, ftop, color=MUTED, sw=1.0, dash="3 4"))
    parts.append(line(px0, fbot, px0 + pw, fbot, color=MUTED, sw=1.0, dash="3 4"))

    def chirp(start_frac, color, sw, label):
        # частота лінійно росте; на верху загортається вниз і їде далі.
        # start_frac ∈ [0,1) — частка смуги, з якої стартуємо.
        segs = []
        N = 200
        for i in range(N + 1):
            t = i / N
            f = (start_frac + t) % 1.0  # 0..1 по смузі, із загортанням
            x = px0 + t * pw
            y = fbot - f * (fbot - ftop)
            segs.append((x, y))
        # розбиваємо на полілінії в місцях стрибка (загортання), щоб не було вертикалі
        out = []
        run = [segs[0]]
        for j in range(1, len(segs)):
            if abs(segs[j][1] - segs[j - 1][1]) > (fbot - ftop) * 0.6:
                out.append(run); run = [segs[j]]
            else:
                run.append(segs[j])
        out.append(run)
        frag = ""
        for run in out:
            pts = " ".join("%.1f,%.1f" % (x, y) for x, y in run)
            frag += ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                     % (pts, color, sw))
        # позначка стартової частоти зліва
        ys = fbot - start_frac * (fbot - ftop)
        frag += circle(px0, ys, 4, fill=color, stroke=INK, sw=1)
        frag += text(px0 - 10, ys + 4, label, 11, color, "end")
        return frag

    parts.append(chirp(0.0, MUTED, 2.0, "0"))     # базовий чирп — від низу
    parts.append(chirp(0.33, NEG, 2.6, "A"))      # символ A
    parts.append(chirp(0.66, POS, 2.6, "B"))      # символ B
    # підпис-висновок
    box = fitbox(px0 + pw - 196, py0 + 4, 188, 64,
                 "Значення = стартова\nчастота чирпа.\nДоїхав до верху —\nзагорнувся вниз.",
                 size=11, fill="#fff8e1", stroke="#f0b429", sw=1.2, color=INK)
    parts.append(box)
    parts.append(text(px0 + pw / 2, py0 + ph + 36,
                      "той самий нахил, різний старт → різні символи (тут 2 з 2^SF можливих)",
                      11, INK, "middle"))
    render(os.path.join(IMG, "chirp-symbol.svg"), W, H, *parts,
           title="Дані в чирпі: значення задає стартова частота")


# ── Фігура 3: компроміс SF — символ довшає вдвічі на кожен крок ───────────────
# Стовпчики тривалості символа Ts ∝ 2^SF для SF7..SF12 (одна смуга 125 кГц).
# Підписи: SF7 — швидко/близько, SF12 — повільно/далеко. Видно подвоєння.
def fig_sf_tradeoff():
    W, H = 680, 380
    base_x, base_y = 80, 300
    bw = 70           # ширина стовпчика
    gap = 26
    sfs = [7, 8, 9, 10, 11, 12]
    # Ts = 2^SF / BW. Для масштабу беремо відносно SF7 (=128) і малюємо в px.
    ref = 2 ** 7
    maxh = 230        # висота для SF12
    parts = []
    parts.append(arrow(base_x - 14, base_y, base_x - 14, base_y - maxh - 24, color=MUTED, sw=1.3))
    parts.append(text(base_x - 14, base_y - maxh - 30, "тривалість символа", 11, MUTED, "middle"))
    parts.append(line(base_x - 18, base_y, base_x + len(sfs) * (bw + gap), base_y, color=MUTED, sw=1.3))
    # реальні відносні значення часу (×) для підпису
    for i, sf in enumerate(sfs):
        rel = (2 ** sf) / ref
        h = maxh * rel / ((2 ** 12) / ref)  # нормуємо так, щоб SF12 = maxh
        x = base_x + i * (bw + gap)
        col = NEG if sf == 7 else (POS if sf == 12 else FIELD)
        parts.append(rect(x, base_y - h, bw, h, fill="#eef2f7", stroke=col, sw=2.0, rx=4))
        parts.append(text(x + bw / 2, base_y + 18, "SF%d" % sf, 12, INK, "middle", bold=True))
        parts.append(text(x + bw / 2, base_y - h - 8, "×%d" % int(rel), 10, MUTED, "middle"))
    # підписи-крайнощі
    parts.append(fitbox(base_x - 2, base_y - maxh - 8, 168, 48,
                        "SF7: коротко —\nшвидко, близько",
                        size=12, fill="#eaf0fd", stroke=NEG, sw=1.2, color=INK))
    lastx = base_x + (len(sfs) - 1) * (bw + gap)
    parts.append(fitbox(lastx - 132, base_y - maxh - 8, 206, 48,
                        "SF12: довго — повільно,\nдалеко, більше енергії",
                        size=12, fill="#fdecea", stroke=POS, sw=1.2, color=INK))
    parts.append(text(W / 2, H - 14,
                      "крок SF на +1 = вдвічі довший символ (Ts = 2^SF / BW), та сама смуга",
                      11, MUTED, "middle"))
    render(os.path.join(IMG, "sf-tradeoff.svg"), W, H, *parts,
           title="Коефіцієнт розширення SF: дальність купуємо часом")


# ── Фігура 4: як приймач витягує чирп з-під шуму — стиснення в пік ────────────
# Зліва: розмазаний по смузі чирп, ледь вищий за шум. Множення на дзеркальний
# (down-)чирп «розпрямляє» його в одну частоту → праворуч гострий пік над шумом.
# Це виграш обробки: чому LoRa чує сигнал, слабший за шум.
def fig_despread():
    W, H = 700, 340
    parts = []
    # ── ліва панель: f×t, чирп ледь над шумом
    lx, ly, lw, lh = 60, 70, 250, 190
    parts.append(arrow(lx - 6, ly + lh, lx + lw + 12, ly + lh, color=MUTED, sw=1.3))
    parts.append(arrow(lx, ly + lh + 6, lx, ly - 12, color=MUTED, sw=1.3))
    parts.append(text(lx + lw / 2, ly + lh + 34, "прийнято: чирп тоне в шумі", 11, INK, "middle"))
    # шумовий фон — короткі риски
    import random
    random.seed(7)
    for _ in range(70):
        rx = lx + random.random() * lw
        ry = ly + 12 + random.random() * (lh - 20)
        parts.append(line(rx, ry, rx + 4, ry, color="#c2c7cf", sw=1.2))
    # сам чирп — діагональ, не набагато вища за шум
    parts.append(line(lx + 4, ly + lh - 16, lx + lw - 4, ly + 16, color=POS, sw=2.4))
    # ── стрілка-операція
    cxm = lx + lw + 60
    parts.append(arrow(lx + lw + 14, ly + lh / 2, cxm + 26, ly + lh / 2, color=INK, sw=2.0))
    parts.append(fitbox(cxm - 24, ly + lh / 2 - 44, 96, 36,
                        "× дзеркальний\nчирп",
                        size=10, fill="#eafaf1", stroke=FIELD, sw=1.2, color=INK))
    # ── права панель: частота×амплітуда, гострий пік
    rx0, ry0, rw, rh = cxm + 44, 70, 250, 190
    parts.append(arrow(rx0 - 6, ry0 + rh, rx0 + rw + 12, ry0 + rh, color=MUTED, sw=1.3))
    parts.append(arrow(rx0, ry0 + rh + 6, rx0, ry0 - 12, color=MUTED, sw=1.3))
    parts.append(text(rx0 + rw / 2, ry0 + rh + 34, "після стиснення: гострий пік", 11, INK, "middle"))
    parts.append(text(rx0 + rw + 10, ry0 + rh + 16, "частота", 11, MUTED, "end"))
    parts.append(text(rx0 - 2, ry0 - 16, "рівень", 11, MUTED, "middle"))
    # шумова підлога — низькі риски
    random.seed(11)
    for _ in range(60):
        nx = rx0 + random.random() * rw
        nh = 4 + random.random() * 8
        parts.append(line(nx, ry0 + rh, nx, ry0 + rh - nh, color="#c2c7cf", sw=1.2))
    # рівень шуму
    noise_y = ry0 + rh - 14
    parts.append(line(rx0, noise_y, rx0 + rw, noise_y, color=MUTED, sw=1.0, dash="4 4"))
    parts.append(text(rx0 + rw - 2, noise_y - 4, "шум", 10, MUTED, "end"))
    # пік
    pk = rx0 + rw * 0.45
    parts.append(line(pk, ry0 + rh, pk, ry0 + 8, color=FIELD, sw=3.4))
    parts.append(text(pk, ry0 + 2, "сигнал", 11, FIELD, "middle", bold=True))
    render(os.path.join(IMG, "despread.svg"), W, H, *parts,
           title="Виграш обробки: дзеркальний чирп збирає сигнал у пік над шумом")


fig_what_is_chirp()
fig_chirp_symbol()
fig_sf_tradeoff()
fig_despread()
print("Done. SVG in", IMG)
