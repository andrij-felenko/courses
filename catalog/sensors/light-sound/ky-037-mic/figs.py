# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «KY-037 — давач звуку (великий мікрофон)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Тракт сигналу: мікрофон → зсув → компаратор; відгалуження на AO ─────────
def fig_signal_path():
    W, H = 940, 400
    f = [text(W / 2, 28, "Тракт KY-037: мікрофон дає плавний AO, компаратор — цифровий DO",
              size=15, bold=True)]

    # ── горизонтальний ланцюг блоків ──
    by = 140          # верх блоків
    bh = 90
    def block(x, w, lines, col=INK, fill=FILL):
        f.append(rect(x, by, w, bh, fill=fill, stroke=col, sw=2, rx=10))
        f.append(mtext(x + w / 2, by + bh / 2 - (len(lines) - 1) * 8 + 4, lines,
                       size=11.5, bold=True, color=col))

    # мікрофон
    mx, mw = 40, 150
    block(mx, mw, ["електретний", "мікрофон", "(CMA-6542PF)"], col=NEG, fill="#eaf1fb")
    # підсилювач/зсув
    ax, aw = 250, 160
    block(ax, aw, ["підсилення +", "зсув до ½·+V", "(робоча точка)"], col=INK)
    # компаратор
    cx, cw = 470, 170
    block(cx, cw, ["компаратор LM393", "порівнює з порогом", "(гвинтик)"], col=INK)

    # стрілки між блоками
    f.append(arrow(mx + mw, by + bh / 2, ax, by + bh / 2, color=INK))
    f.append(arrow(ax + aw, by + bh / 2, cx, by + bh / 2, color=INK))

    # ── відгалуження на AO (аналог) — з виходу зсуву, ДО компаратора ──
    tapx = ax + aw + (cx - ax - aw) / 2   # точка відгалуження на стрілці
    aoy = by + bh + 70
    f.append(circle(tapx, by + bh / 2, 4, fill=INK, stroke=INK))
    f.append(line(tapx, by + bh / 2, tapx, aoy, color=FIELD, sw=2.2))
    f.append(arrow(tapx, aoy, W - 120, aoy, color=FIELD, sw=2.2))
    f.append(text(W - 116, aoy + 4, "AO", size=14, bold=True, color=FIELD, anchor="start"))
    f.append(text(W - 116, aoy + 22, "(аналог)", size=10, color=MUTED, anchor="start"))
    f.append(text(tapx + 8, aoy - 10, "плавна напруга мікрофона: коливається навколо ½·+V",
                  size=10.5, color=FIELD, anchor="start"))

    # ── вихід компаратора → DO (цифра) ──
    doy = by + bh / 2
    f.append(arrow(cx + cw, doy, W - 120, doy, color=POS, sw=2.4))
    f.append(text(W - 116, doy + 4, "DO", size=14, bold=True, color=POS, anchor="start"))
    f.append(text(W - 116, doy + 22, "(0 / 1)", size=10, color=MUTED, anchor="start"))
    f.append(text(cx + cw + 8, doy - 12, "перескок за поріг → цифровий рівень",
                  size=10.5, color=POS, anchor="start"))

    # підпис-висновок унизу
    note, nw, nh = textbox(W / 2, 340,
        "AO — миттєвий голос мікрофона (треба обробити самому);  DO — уже готове «гучно / тихо» щодо порога",
        size=11.5, fill="#f4f8f4", stroke=FIELD, pad=10)
    f.append(note)
    return render(os.path.join(IMG, 'signal-path.svg'), W, H, *f)


# ── 2. Що НАСПРАВДІ на AO: звук їздить навколо зсуву, а не «рівень гучності» ───
def fig_ao_waveform():
    W, H = 920, 430
    f = [text(W / 2, 28, "Головна пастка AO: це коливання навколо ½·+V, а не готове число гучності",
              size=14.5, bold=True)]

    import math
    x0, x1 = 90, 850
    span = 100.0                     # умовний час, поділки
    def X(t): return x0 + (x1 - x0) * t / span

    # осі напруги
    v_top = 70                       # +V
    v_mid = 200                      # ½·+V (робоча точка / зсув)
    v_bot = 330                      # GND
    f.append(line(x0, v_top, x1, v_top, color=MUTED, sw=1, dash="4,4"))
    f.append(line(x0, v_bot, x1, v_bot, color=MUTED, sw=1, dash="4,4"))
    f.append(line(x0, v_mid, x1, v_mid, color=NEG, sw=1.6, dash="6,4"))
    f.append(text(x0 - 10, v_top + 4, "+V", size=11, bold=True, color=POS, anchor="end"))
    f.append(text(x0 - 10, v_bot + 4, "GND", size=11, bold=True, anchor="end"))
    f.append(text(x0 - 10, v_mid + 4, "½·+V", size=11, bold=True, color=NEG, anchor="end"))
    f.append(text(x1 + 6, v_mid + 4, "зсув (спокій)", size=10, color=NEG, anchor="start"))

    # хвиля: тиша (мала амплітуда) → гучно (велика) → тиша
    def amp(t):
        if t < 30:   return 6
        if t < 70:   return 60 * (0.5 - 0.5 * math.cos(2 * math.pi * (t - 30) / 40)) + 6
        return 6
    pts = []
    for i in range(0, 601):
        t = span * i / 600
        y = v_mid - amp(t) * math.sin(2 * math.pi * t * 0.9)
        pts.append((X(t), y))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (d, FIELD))

    # позначки: тиша / гучно
    f.append(text(X(15), v_bot + 30, "тиша: тонка смужка навколо зсуву", size=10.5, color=MUTED))
    f.append(text(X(50), v_bot + 30, "гучно: розмах більший", size=10.5, bold=True, color=FIELD))
    f.append(text(X(85), v_bot + 30, "знову тиша", size=10.5, color=MUTED))

    # права частина: як із цього дістати «гучність»
    ry = v_mid
    bx = x1 + 8
    # текстовий блок під віссю
    tip, tw, th = textbox(W / 2, 400,
        "«Гучність» = РОЗМАХ навколо зсуву за коротке вікно: max−min багатьох відліків.\n"
        "Один analogRead() дасть випадкову точку синусоїди — і тиша, і крик виглядатимуть однаково.",
        size=11, fill="#fff8e6", stroke="#e0b400", pad=10)
    f.append(tip)
    return render(os.path.join(IMG, 'ao-waveform.svg'), W, H, *f)


# ── 3. Схема модуля KY-037: мікрофон, зсув, LM393, поріг, два виходи, LED ──────
def fig_schematic():
    W, H = 960, 600
    f = [text(W / 2, 28, "Схема KY-037: електретний мікрофон зі зсувом, LM393-компаратор, поріг-гвинтик",
              size=14.5, bold=True)]

    # рейки живлення: +V угорі, GND унизу
    vcc_y = 66
    gnd_y = 470
    xL, xR = 90, 880
    f.append(line(xL, vcc_y, xR, vcc_y, color=POS, sw=2.2))
    f.append(text(xL - 8, vcc_y + 4, "+V", size=12, bold=True, color=POS, anchor="end"))
    f.append(line(xL, gnd_y, xR, gnd_y, color=INK, sw=2.2))
    f.append(text(xL - 8, gnd_y + 4, "GND", size=12, bold=True, anchor="end"))

    sig_y = 250            # горизонталь сигнального тракту

    # ── мікрофон ліворуч: резистор навантаження до +V, капсуль до GND ──
    mic_x = 150
    # резистор навантаження R від +V до сигнального вузла
    f.append(rect(mic_x - 15, 120, 30, 14, fill=FILL, stroke=INK, sw=1.6, rx=3))
    f.append(line(mic_x, vcc_y, mic_x, 120, color=INK, sw=2))
    f.append(line(mic_x, 134, mic_x, sig_y, color=INK, sw=2))
    f.append(text(mic_x - 22, 132, "R", size=11, bold=True, anchor="end"))
    # символ електретного мікрофона нижче сигнального вузла
    mic_cy = 340
    f.append(line(mic_x, sig_y, mic_x, mic_cy - 26, color=INK, sw=2))
    f.append(circle(mic_x, mic_cy, 26, fill="#eaf1fb", stroke=NEG, sw=2))
    f.append(line(mic_x - 18, mic_cy + 18, mic_x + 18, mic_cy - 18, color=NEG, sw=2))
    f.append(line(mic_x, mic_cy + 26, mic_x, gnd_y, color=INK, sw=2))
    f.append(text(mic_x - 34, mic_cy + 4, "мікрофон", size=11, bold=True, color=NEG, anchor="end"))

    # ── розділовий конденсатор → вузол «+» входу компаратора ──
    capx = 270
    f.append(line(mic_x, sig_y, capx - 12, sig_y, color=INK, sw=2))
    f.append(line(capx - 12, sig_y - 12, capx - 12, sig_y + 12, color=INK, sw=2.4))
    f.append(line(capx, sig_y - 12, capx, sig_y + 12, color=INK, sw=2.4))
    f.append(text(capx - 6, sig_y - 20, "C", size=11, bold=True))

    plusnode_x = 360
    f.append(line(capx, sig_y, plusnode_x, sig_y, color=INK, sw=2))
    f.append(circle(plusnode_x, sig_y, 3.5, fill=INK, stroke=INK))

    # подільник зсуву ½·+V: два рівні резистори від +V і до GND, середина — вузол
    div_x = plusnode_x
    f.append(rect(div_x - 15, 120, 30, 14, fill=FILL, stroke=MUTED, sw=1.4, rx=3))
    f.append(line(div_x, vcc_y, div_x, 120, color=MUTED, sw=1.6))
    f.append(line(div_x, 134, div_x, sig_y, color=MUTED, sw=1.6))
    f.append(rect(div_x - 15, 400, 30, 14, fill=FILL, stroke=MUTED, sw=1.4, rx=3))
    f.append(line(div_x, sig_y, div_x, 400, color=MUTED, sw=1.6))
    f.append(line(div_x, 414, div_x, gnd_y, color=MUTED, sw=1.6))
    f.append(text(div_x + 20, 175, "зсув", size=10, color=MUTED, anchor="start"))
    f.append(text(div_x + 20, 189, "½·+V", size=10, color=MUTED, anchor="start"))

    # ── компаратор LM393 (трикутник) ──
    cmp_x = 520
    cmp_cy = sig_y
    cw, ch = 120, 130
    tri = "M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" % (
        cmp_x, cmp_cy - ch / 2, cmp_x, cmp_cy + ch / 2, cmp_x + cw, cmp_cy)
    f.append('<path d="%s" fill="%s" stroke="%s" stroke-width="2"/>' % (tri, FILL, INK))
    f.append(text(cmp_x + cw * 0.40, cmp_cy - 6, "LM393", size=12, bold=True))
    # входи «+» (сигнал) і «−» (поріг)
    inp = cmp_cy - 28
    inm = cmp_cy + 28
    f.append(line(plusnode_x, sig_y, plusnode_x, inp, color=INK, sw=2))
    f.append(line(plusnode_x, inp, cmp_x, inp, color=INK, sw=2))
    f.append(text(cmp_x + 10, inp - 4, "+", size=14, bold=True, color=POS, anchor="start"))
    f.append(text(cmp_x + 10, inm + 10, "−", size=14, bold=True, color=NEG, anchor="start"))

    # ── поріг: підстроювальний резистор (гвинтик) знизу, відвід на «−» вхід ──
    potx = 430
    poty = 448
    f.append(rect(potx - 40, poty - 15, 80, 30, fill="#fdf4f4", stroke=POS, sw=1.6, rx=6))
    f.append(text(potx, poty + 4, "поріг ⟳", size=10.5, bold=True, color=POS))
    f.append(line(potx - 24, poty - 15, potx - 24, vcc_y, color=POS, sw=1.3, dash="3,3"))
    f.append(line(potx - 24, poty + 15, potx - 24, gnd_y, color=POS, sw=1.3, dash="3,3"))
    # рухомий відвід: вгору й на «−» вхід
    f.append(line(potx + 40, poty, 490, poty, color=POS, sw=2))
    f.append(line(490, poty, 490, inm, color=POS, sw=2))
    f.append(line(490, inm, cmp_x, inm, color=POS, sw=2))

    # ── вихід компаратора → DO; світлодіод спрацювання окремою колонкою ──
    outy = cmp_cy
    donode_x = 720
    f.append(line(cmp_x + cw, outy, donode_x, outy, color=INK, sw=2))
    f.append(circle(donode_x, outy, 3.5, fill=INK, stroke=INK))
    f.append(line(donode_x, outy, xR - 40, outy, color=POS, sw=2.2))
    f.append(circle(xR - 40, outy, 5, fill=POS, stroke=POS))
    f.append(text(xR - 30, outy + 4, "DO", size=13, bold=True, color=POS, anchor="start"))
    # LED2 (спрацювання) від DO-вузла вниз до GND
    led2y = 400
    f.append(line(donode_x, outy, donode_x, led2y, color=INK, sw=1.6))
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.4"/>'
             % (donode_x - 9, led2y, donode_x + 9, led2y, donode_x, led2y + 18, "#fdecea", POS))
    f.append(line(donode_x - 9, led2y + 18, donode_x + 9, led2y + 18, color=POS, sw=2))
    f.append(line(donode_x, led2y + 18, donode_x, gnd_y, color=INK, sw=1.6))
    f.append(text(donode_x + 16, led2y + 12, "LED2", size=10, bold=True, color=POS, anchor="start"))
    f.append(text(donode_x + 16, led2y + 26, "«спрацювало»", size=9, color=POS, anchor="start"))

    # ── AO: плавний сигнал мікрофона (вузол «+») — трасою в нижньому полі, під GND ──
    ao_y = 545                       # нижнє поле, нижче за GND: жодних перетинів із трактом
    ao_tap_x = 300
    f.append(line(ao_tap_x, sig_y, ao_tap_x, ao_y, color=FIELD, sw=2))
    f.append(circle(ao_tap_x, sig_y, 3.5, fill=FIELD, stroke=FIELD))
    f.append(line(ao_tap_x, ao_y, xR - 40, ao_y, color=FIELD, sw=2))
    f.append(circle(xR - 40, ao_y, 5, fill=FIELD, stroke=FIELD))
    f.append(text(xR - 30, ao_y + 4, "AO", size=13, bold=True, color=FIELD, anchor="start"))
    f.append(text(ao_tap_x + 14, ao_y - 8, "плавний сигнал мікрофона (навколо ½·+V) — відгалуження до компаратора",
                  size=9.5, color=FIELD, anchor="start"))

    # LED1 (живлення) — окрема колонка вгорі праворуч, суто індикатор
    led1x = 810
    f.append(line(led1x, vcc_y, led1x, 96, color=INK, sw=1.4))
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.4"/>'
             % (led1x - 9, 96, led1x + 9, 96, led1x, 114, "#eafaef", FIELD))
    f.append(line(led1x - 9, 114, led1x + 9, 114, color=FIELD, sw=2))
    f.append(line(led1x, 114, led1x, gnd_y, color=INK, sw=1.4))
    f.append(text(led1x + 14, 100, "LED1", size=10, bold=True, color=FIELD, anchor="start"))
    f.append(text(led1x + 14, 114, "«живлення»", size=9, color=FIELD, anchor="start"))

    return render(os.path.join(IMG, 'schematic.svg'), W, H, *f)


# ── 4. Підключення KY-037 до МК: 4 дроти, AO на АЦП, DO на цифровий вхід ───────
def fig_wiring():
    W, H = 880, 420
    f = [text(W / 2, 28, "Підключення KY-037: чотири дроти — AO на АЦП, DO на цифровий вхід",
              size=15, bold=True)]

    # модуль ліворуч
    mx, my, mw, mh = 80, 90, 210, 230
    f.append(rect(mx, my, mw, mh, fill="#eaf1fb", stroke=NEG, sw=2, rx=12))
    f.append(text(mx + mw / 2, my + 26, "KY-037", size=15, bold=True, color=NEG))
    f.append(text(mx + mw / 2, my + 46, "(мікрофон + LM393)", size=10, color=MUTED))
    # чотири штирі праворуч на модулі — порядок ГУЛЯЄ, читай написи
    pins = [("AO", my + 90, FIELD), ("GND", my + 130, INK),
            ("+ / VCC", my + 170, POS), ("DO", my + 210, POS)]
    for lbl, py, col in pins:
        f.append(circle(mx + mw, py, 6, fill=col, stroke=col))
        f.append(text(mx + mw - 14, py + 4, lbl, size=12, bold=True, color=col, anchor="end"))

    # МК праворуч
    kx, ky, kw, kh = 560, 90, 200, 240
    f.append(rect(kx, ky, kw, kh, fill="#f4f6f8", stroke=INK, sw=2, rx=12))
    f.append(text(kx + kw / 2, ky + 26, "мікроконтролер", size=12.5, bold=True))
    f.append(text(kx + kw / 2, ky + 44, "(Arduino / ESP32)", size=10, color=MUTED))
    targets = [("A0  (АЦП)", ky + 90, FIELD), ("GND", ky + 130, INK),
               ("5V / 3V3", ky + 170, POS), ("D3  вхід", ky + 210, POS)]
    for lbl, py, col in targets:
        f.append(circle(kx, py, 6, fill=col, stroke=col))
        f.append(text(kx + 16, py + 4, lbl, size=11.5, bold=True, color=col, anchor="start"))

    # чотири дроти
    for (l1, py1, c1), (l2, py2, c2) in zip(pins, targets):
        midx = (mx + mw + kx) / 2
        f.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" '
                 'fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (mx + mw + 6, py1, midx, py1, midx, py2, kx - 6, py2, c1))

    # примітка
    note, nw, nh = textbox(W / 2, 372,
        "Порядок штирів на різних платах різний — з'єднуй за ПІДПИСАМИ, не за позицією.\n"
        "Живлення бери під логіку плати (3.3 В на 3.3-вольтовій), щоб рівень AO/DO їй пасував.",
        size=11, fill="#fff8e6", stroke="#e0b400", pad=10)
    f.append(note)
    return render(os.path.join(IMG, 'wiring.svg'), W, H, *f)


# ── 5. (proj) Як число гучності виходить із вікна: два виміри розмаху ──────────
def fig_loudness_window():
    W, H = 940, 470
    f = [text(W / 2, 26, "Гучність із вікна: розмах (max−min) і середньоквадратичне відхилення (RMS)",
              size=14.5, bold=True)]

    import math
    x0, x1 = 90, 660
    span = 100.0
    def X(t): return x0 + (x1 - x0) * t / span

    mid = 190          # ½·+V
    top, bot = 90, 290
    # рамка вікна
    f.append(rect(x0 - 6, top - 10, (x1 - x0) + 12, (bot - top) + 20,
                  fill="#f7fbff", stroke=NEG, sw=1.4, rx=8))
    f.append(text(x0 - 6, top - 18, "одне вікно ≈ 30–50 мс", size=10.5, color=NEG, anchor="start"))

    # лінія зсуву й межі, що їх знайшло вікно
    f.append(line(x0, mid, x1, mid, color=MUTED, sw=1.4, dash="6,4"))
    f.append(text(x1 + 6, mid + 4, "½·+V", size=10.5, color=MUTED, anchor="start"))

    # хвиля в вікні (кілька періодів середньої гучності)
    pts = []
    hi, lo = mid, mid
    for i in range(0, 481):
        t = span * i / 480
        env = 60 * (0.35 + 0.65 * math.sin(math.pi * t / span))   # горбок амплітуди
        y = mid - env * math.sin(2 * math.pi * t * 0.11)
        pts.append((X(t), y))
        hi = min(hi, y); lo = max(lo, y)      # y менше = вище на екрані
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.7"/>' % (d, FIELD))

    # позначки max і min (найвища й найнижча точки хвилі)
    f.append(line(x0, hi, x1, hi, color=POS, sw=1.2, dash="3,3"))
    f.append(line(x0, lo, x1, lo, color=POS, sw=1.2, dash="3,3"))
    f.append(text(x0 + 6, hi - 6, "max", size=10.5, bold=True, color=POS, anchor="start"))
    f.append(text(x0 + 6, lo + 14, "min", size=10.5, bold=True, color=POS, anchor="start"))
    # стрілка розмаху праворуч усередині вікна
    ax = x1 - 40
    f.append(arrow(ax, hi, ax, lo, color=POS, sw=1.8))
    f.append(arrow(ax, lo, ax, hi, color=POS, sw=1.8))
    f.append(text(ax + 8, (hi + lo) / 2, "розмах", size=10.5, bold=True, color=POS, anchor="start"))
    f.append(text(ax + 8, (hi + lo) / 2 + 15, "max−min", size=9.5, color=POS, anchor="start"))

    # два способи-картки праворуч
    b1 = fitbox(690, 80, 230, 120,
        "СПОСІБ 1 — розмах\nmax−min за вікно.\nШвидко, ловить піки,\nчутливий до одного\nвипадкового виплеску.",
        size=11, fill="#fdf3f2", stroke=POS, bold=False)
    f.append(b1)
    b2 = fitbox(690, 220, 230, 130,
        "СПОСІБ 2 — RMS\nσ = √(Σ(vᵢ−серед)² / N).\nСереднє відхилення від\nзсуву; стійкіший до\nодиничного викиду,\nближчий до відчуття гучності.",
        size=10.5, fill="#eafaef", stroke=FIELD, bold=False)
    f.append(b2)

    tip, tw, th = textbox(W / 2, 430,
        "Обидва беруть ПАЧКУ відліків за вікно, а не одну точку. Розмах — простіший; RMS — рівніший і менш смиканий.",
        size=11, fill="#fff8e6", stroke="#e0b400", pad=10)
    f.append(tip)
    return render(os.path.join(IMG, 'loudness-window.svg'), W, H, *f)


# ── 6. (proj) Автомат «оплеск on/off»: фронт + гістерезис у часі ───────────────
def fig_clap_fsm():
    W, H = 980, 470
    f = [text(W / 2, 26, "Оплеск вмикає / вимикає: ловимо ФРОНТ гучності через поріг, а не сам рівень",
              size=14.5, bold=True)]

    import math
    x0, x1 = 80, 720
    span = 100.0
    def X(t): return x0 + (x1 - x0) * t / span

    # ── верхня панель: гучність, поріг, фронти, глухі вікна ──
    base = 175         # рівень гучності «0»
    thr = 88           # висота порога над base
    f.append(text(x0, 66, "гучність (розмах вікна)", size=10.5, color=FIELD, anchor="start"))
    f.append(line(x0, base - thr, x1, base - thr, color=POS, sw=1.4, dash="6,4"))
    f.append(text(x1 + 6, base - thr + 4, "поріг", size=10.5, bold=True, color=POS, anchor="start"))

    # два оплески — два горби; піки коротко над порогом
    def loud(t):
        g = 0.0
        for c in (22, 62):
            g += 118 * math.exp(-((t - c) ** 2) / 24)
        return g + 5 * (1 + math.sin(t))
    pts = [(X(span * i / 400), base - min(loud(span * i / 400), 132)) for i in range(0, 401)]
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (d, FIELD))

    # моменти перетину порога вгору = ФРОНТ (кружечки з короткою міткою)
    fronts = [("1-й оплеск", 18.6), ("2-й оплеск", 58.6)]
    for lbl, c in fronts:
        f.append(circle(X(c), base - thr, 5, fill=POS, stroke=POS))
        f.append(text(X(c), base - thr - 12, "▲ " + lbl, size=10, bold=True, color=POS, anchor="middle"))

    # смуги «глухого» гістерезису після кожного фронту (з короткою міткою над кожною)
    for _, c in fronts:
        gx0, gx1 = X(c), X(c + 13)
        f.append(rect(gx0, base + 14, gx1 - gx0, 20, fill="#eef0f2", stroke=MUTED, sw=1, rx=4))
        f.append(text((gx0 + gx1) / 2, base + 27, "глухо", size=9.5, color=MUTED, anchor="middle"))
    f.append(text(X(50), base + 52, "«глухо» ≈ 250 мс: хвіст того самого оплеску ігноруємо",
                  size=10, color=MUTED, anchor="middle"))

    # ── нижня панель: стан виходу (світло) — toggle на кожен фронт ──
    sy = base + 118
    f.append(text(x0, sy - 34, "стан виходу (світло) — перекидається на КОЖЕН фронт:",
                  size=10.5, bold=True, anchor="start"))
    seg = [(0, 18.6, 0), (18.6, 58.6, 1), (58.6, 100, 0)]
    for a, b, st in seg:
        yy = sy - (22 if st else 0)
        f.append(line(X(a), yy, X(b), yy, color=NEG, sw=2.8))
    for _, c in fronts:
        f.append(line(X(c), sy, X(c), sy - 22, color=NEG, sw=2.8))
    f.append(text(X(38.5), sy - 7, "УВІМКНЕНО", size=10.5, bold=True, color=NEG, anchor="middle"))
    f.append(text(X(9), sy + 15, "вимкнено", size=10, color=MUTED, anchor="middle"))
    f.append(text(X(80), sy + 15, "вимкнено", size=10, color=MUTED, anchor="middle"))

    tip, tw, th = textbox(W / 2, 438,
        "Подія — це ПЕРЕХІД гучності знизу вгору через поріг (фронт), а не сам факт «зараз голосно».\n"
        "Після фронту — глухе вікно, щоб решта піків того самого оплеску не смикнула toggle вдруге.",
        size=11, fill="#fff8e6", stroke="#e0b400", pad=10)
    f.append(tip)
    return render(os.path.join(IMG, 'clap-fsm.svg'), W, H, *f)


if __name__ == "__main__":
    for fn in (fig_signal_path, fig_ao_waveform, fig_schematic, fig_wiring,
               fig_loudness_window, fig_clap_fsm):
        p = fn()
        print("wrote", p)
