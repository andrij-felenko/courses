# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Той самий середній рівень: ШІМ (один довгий імпульс) vs sigma-delta ──
def fig_pwm_vs_pdm():
    """Однакова середня частка увімкненого (3/8), але ШІМ збиває її в один
    широкий імпульс на кадр, а sigma-delta розкидає короткими, часто й рівно."""
    W, H = 760, 380
    frags = []
    x0, aw = 80, 600
    n = 16                      # елементарних тактів на смузі
    cell = aw / n
    high = 26                   # висота рівня «увімкнено»

    def waverow(y, pattern, col, fillc, title):
        frags.append(text(x0, y - high - 14, title, size=14, color=col, bold=True, anchor="start"))
        base = y
        # базова лінія
        frags.append(line(x0, base, x0 + aw, base, color="#cfcfcf", sw=1.2))
        prev = 0
        path = []
        for k in range(n):
            lvl = base - high if pattern[k] else base
            xa = x0 + k * cell
            xb = x0 + (k + 1) * cell
            # заливка увімкнених тактів
            if pattern[k]:
                frags.append(rect(xa, base - high, cell, high, fill=fillc, stroke="none", rx=0))
            # горизонтальний відрізок
            path.append((xa, lvl, xb, lvl))
            # вертикальний фронт
            if k > 0:
                prevlvl = base - high if pattern[k - 1] else base
                if prevlvl != lvl:
                    frags.append(line(xa, prevlvl, xa, lvl, color=col, sw=2.4))
        for (xa, la, xb, lb) in path:
            frags.append(line(xa, la, xb, lb, color=col, sw=2.4))
        # підпис рівнів
        frags.append(text(x0 - 8, base + 4, "0", size=11, color=MUTED, anchor="end"))
        frags.append(text(x0 - 8, base - high + 4, "1", size=11, color=MUTED, anchor="end"))

    # 6 із 16 увімкнено = 3/8 у обох рядах
    pwm = [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]            # один блок
    pdm = [1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0]            # розкидано рівно

    waverow(120, pwm, NEG, "#dfe7fb", "Класична ШІМ:  один широкий імпульс на кадр")
    waverow(250, pdm, FIELD, "#dcf3e6", "Sigma-delta (густина):  короткі, часто, рівномірно")

    frags.append(text(x0 + aw / 2, 300,
                      "однакове середнє (6 із 16 = 3/8) — але розкидані імпульси дають "
                      "пульсацію втричі вищу частотою й набагато меншу амплітудою",
                      size=12.5, color=MUTED, italic=True))
    # дужка-кадр під ШІМ
    frags.append(line(x0, 138, x0 + 6 * cell, 138, color=NEG, sw=1.4))
    frags.append(text(x0 + 3 * cell, 154, "одна довга «яма» для фільтра", size=11, color=NEG))

    render(os.path.join(IMG, "pwm-vs-pdm.svg"), W, H, *frags,
           title="Та сама середня величина, два способи її розкласти в часі")


# ── 2. Цифрова петля: акумулятор накопичує помилку, переповнення = біт виходу ──
def fig_loop():
    W, H = 793, 330
    frags = []
    cy = 168
    # блоки зліва направо
    bx = [96, 268, 438, 612]
    s1, w1, h1 = textbox(bx[0], cy, "вхід\n(ціль 96/256)", size=12.5, pad=11,
                         stroke=INK, sw=1.8)
    frags.append(s1)
    # суматор (коло з +/−)
    frags.append(circle(bx[1], cy, 22, fill="#f4f6f8", stroke=INK, sw=2))
    frags.append(text(bx[1] - 7, cy - 3, "+", size=16, color=POS, bold=True))
    frags.append(text(bx[1] - 7, cy + 14, "−", size=16, color=NEG, bold=True))
    s3, w3, h3 = textbox(bx[2], cy, "акумулятор\n(додає різницю\nщотакту)", size=12.5, pad=11,
                         fill="#dcf3e6", stroke=FIELD, sw=2)
    frags.append(s3)
    s4, w4, h4 = textbox(bx[3], cy, "переповнення?\n1 → вихід ON\n0 → вихід OFF", size=12.5, pad=11,
                         fill="#fdecea", stroke=POS, sw=2)
    frags.append(s4)

    # стрілки вперед
    frags.append(arrow(bx[0] + w1 / 2 + 4, cy, bx[1] - 24, cy, color=INK, sw=2))
    frags.append(arrow(bx[1] + 24, cy, bx[2] - w3 / 2 - 4, cy, color=INK, sw=2))
    frags.append(arrow(bx[2] + w3 / 2 + 4, cy, bx[3] - w4 / 2 - 4, cy, color=INK, sw=2))

    # зворотний зв'язок: вихідний біт віднімається (повна шкала)
    fb_y = cy + 96
    frags.append(line(bx[3], cy + h4 / 2 + 4, bx[3], fb_y, color=POS, sw=2))
    frags.append(line(bx[3], fb_y, bx[1], fb_y, color=POS, sw=2))
    frags.append(arrow(bx[1], fb_y, bx[1], cy + 24, color=POS, sw=2))
    frags.append(text((bx[1] + bx[3]) / 2, fb_y + 18,
                      "якщо вихід був ON — відняти повну шкалу (256); якщо OFF — нічого",
                      size=12, color=POS))

    # підпис виходу
    frags.append(arrow(bx[3] + w4 / 2 + 4, cy, bx[3] + w4 / 2 + 60, cy, color=FIELD, sw=2.2))
    frags.append(text(bx[3] + w4 / 2 + 66, cy - 8, "потік", size=12, color=FIELD, anchor="start"))
    frags.append(text(bx[3] + w4 / 2 + 66, cy + 9, "бітів →", size=12, color=FIELD, anchor="start"))

    render(os.path.join(IMG, "loop.svg"), W, H, *frags,
           title="Sigma-delta першого порядку у прошивці: один акумулятор і перенесення")


# ── 3. Куди лягає шум квантування: рівний шар (ШІМ-усереднення) vs витиснутий ──
def fig_noise_shape():
    W, H = 760, 380
    ox, oy = 80, H - 64
    aw, ah = 600, 250
    frags = []
    frags.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))
    frags.append(line(ox, oy, ox, oy - ah, color=INK, sw=2))
    frags.append(text(ox + aw, oy + 26, "частота →", size=13, color=INK, anchor="end"))
    frags.append(text(ox - 10, oy - ah + 4, "шум", size=13, color=INK, anchor="end", bold=True))

    # робоча смуга (низ) — де живе корисний сигнал
    bw = 0.16 * aw
    frags.append(rect(ox, oy - ah, bw, ah, fill="#eef6ff", stroke="none", rx=0))
    frags.append(text(ox + bw / 2, oy - ah - 8, "робоча\nсмуга", size=11, color=NEG))
    frags.append(line(ox + bw, oy, ox + bw, oy - ah, color=NEG, sw=1.2, dash="4,4"))

    # рівний шар (білий шум звичайного квантування / ШІМ-усереднення)
    flat = oy - 70
    frags.append(line(ox, flat, ox + aw, flat, color=NEG, sw=2.4, dash="7,5"))
    frags.append(text(ox + aw - 6, flat - 8, "рівний шар: квантування без формування",
                      size=12, color=NEG, anchor="end"))

    # формований шум: росте з частотою (нахил, нуль на 0)
    pts = []
    for k in range(0, 101):
        f = k / 100.0
        y = oy - 6 - (ah - 12) * (f * f)        # ~ f² форма (наочно «крутіше вгору»)
        pts.append("%.1f,%.1f" % (ox + f * aw, y))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
                 % (" ".join(pts), FIELD))
    frags.append(text(ox + 0.74 * aw, oy - 0.62 * ah, "sigma-delta:\nшум витиснуто вгору",
                      size=12.5, color=FIELD))

    # стрілка «у смузі тихо»
    frags.append(arrow(ox + bw * 0.5, flat - 4, ox + bw * 0.5, oy - 18, color=FIELD, sw=2))
    frags.append(text(ox + bw + 8, oy - 22, "у смузі сигналу — тихо", size=12, color=FIELD, anchor="start"))

    render(os.path.join(IMG, "noise-shape.svg"), W, H, *frags,
           title="Шум той самий — питання, де він лежить")


# ── 4. Пульсація після того самого RC: велика й повільна (ШІМ) vs мала й швидка ──
def fig_ripple():
    W, H = 760, 360
    frags = []
    midx = W / 2
    frags.append(line(midx, 58, midx, H - 26, color="#d8d8d8", sw=1.4, dash="3,5"))

    def panel(cx, big, col, fillc, title, sub):
        ax0 = cx - 150
        aw = 300
        base = 200
        amp = 52 if big else 16
        period = 150 if big else 40      # ШІМ — довгий період; sd — короткий
        frags.append(text(cx, 70, title, size=14, color=col, bold=True))
        frags.append(line(ax0, base, ax0 + aw, base, color="#cfcfcf", sw=1.2))
        # середній рівень (ціль)
        frags.append(line(ax0, base - 30, ax0 + aw, base - 30, color=MUTED, sw=1.4, dash="5,4"))
        frags.append(text(ax0 + aw + 4, base - 30, "ціль", size=11, color=MUTED, anchor="start"))
        # трикутна пульсація навколо середнього
        pts = []
        x = ax0
        up = True
        y = base - 30
        step = 6
        while x <= ax0 + aw:
            pts.append("%.1f,%.1f" % (x, y))
            # пилкоподібний хід навколо середнього
            phase = ((x - ax0) % period) / period
            yy = base - 30 + amp * (2 * abs(phase - 0.5) - 0.5)
            y = yy
            x += step
        frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                     % (" ".join(pts), col))
        # розмах пульсації
        frags.append(line(ax0 + aw - 24, base - 30 - amp / 2, ax0 + aw - 24, base - 30 + amp / 2,
                          color=col, sw=1.4))
        frags.append(text(ax0 + aw - 18, base - 30, ("великий" if big else "малий") + "\nрозмах",
                          size=11, color=col, anchor="start"))
        frags.append(text(cx, base + 56, sub, size=12, color=col, italic=True))

    panel(midx / 2 + 30, True, NEG, "#dfe7fb",
          "ШІМ через той самий RC",
          "повільна, велика пульсація:\nфільтрові важко")
    panel(midx + midx / 2 - 30, False, FIELD, "#dcf3e6",
          "Sigma-delta через той самий RC",
          "швидка, дрібна пульсація:\nфільтр давить її легко")

    render(os.path.join(IMG, "ripple.svg"), W, H, *frags,
           title="Однаковий RC-фільтр — а на виході пульсація різна")


# ════════════════════════════════════════════════════════════════════════════
#  Фігури для вставки proj-firmware-modulator.md (прошивка модулятора)
# ════════════════════════════════════════════════════════════════════════════

# ── A. Повний тракт прошивки: чотири ланки одного переривання ────────────────
def fig_firmware_chain():
    """Ланцюг усередині ISR: фазовий акумулятор біжить по таблиці синуса → дає
    миттєвий рівень 0..255 → sigma-delta акумулятор перетворює рівень на потік
    бітів (переповнення вмикає ніжку) → RC-фільтр згладжує потік у синусоїду."""
    W, H = 900, 400
    frags = []
    cy = 176                      # центр ряду блоків
    # чотири блоки-ланки зліва направо + маленькі ескізи над кожним
    b1x, b2x, b3x, b4x = 128, 356, 566, 792

    # блок 1 — фазовий акумулятор + таблиця синуса
    s1, w1, h1 = textbox(b1x, cy, "фазовий акумулятор\n+ таблиця синуса\n(256 точок)",
                         size=13, pad=12, fill="#eef2ff", stroke=NEG, sw=2, color=INK)
    # блок 2 — миттєвий рівень
    s2, w2, h2 = textbox(b2x, cy, "миттєвий\nрівень\n0..255", size=13, pad=12,
                         fill=FILL, stroke=INK, sw=1.8)
    # блок 3 — sigma-delta акумулятор
    s3, w3, h3 = textbox(b3x, cy, "sigma-delta\nакумулятор\n(переповнення→біт)",
                         size=13, pad=12, fill="#dcf3e6", stroke=FIELD, sw=2)
    # блок 4 — RC-фільтр
    s4, w4, h4 = textbox(b4x, cy, "RC-фільтр\nза ніжкою", size=13, pad=12,
                         fill="#fff7ed", stroke=POS, sw=2)
    frags += [s1, s2, s3, s4]

    # стрілки між ланками з підписами того, що тече
    def flow(xa, xb, lab, col):
        frags.append(arrow(xa, cy, xb, cy, color=INK, sw=2.2))
        frags.append(text((xa + xb) / 2, cy - 12, lab, size=11, color=col, italic=True))

    flow(b1x + w1 / 2 + 4, b2x - w2 / 2 - 4, "фаза", NEG)
    flow(b2x + w2 / 2 + 4, b3x - w3 / 2 - 4, "рівень", INK)
    flow(b3x + w3 / 2 + 4, b4x - w4 / 2 - 4, "потік бітів", FIELD)

    # маленький ескіз під кожним блоком — що воно за сигнал
    ey = cy + h3 / 2 + 46         # рівень ескізів під блоками
    ehw = 46                      # піврозмах ескіза по x

    # 1) наростаюча «пилка» фази
    px = []
    for k in range(0, 41):
        t = k / 40.0
        yy = ey + 16 - 32 * ((t * 3) % 1.0)
        px.append("%.1f,%.1f" % (b1x - ehw + t * 2 * ehw, yy))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>'
                 % (" ".join(px), NEG))
    frags.append(text(b1x, ey + 40, "фаза росте по колу", size=10.5, color=MUTED))

    # 2) плавна синусоїда рівня
    sx = []
    for k in range(0, 49):
        t = k / 48.0
        yy = ey - 18 * math.sin(2 * math.pi * t)
        sx.append("%.1f,%.1f" % (b2x - ehw + t * 2 * ehw, yy))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
                 % (" ".join(sx), INK))
    frags.append(text(b2x, ey + 40, "плавне число", size=10.5, color=MUTED))

    # 3) потік бітів (щільність за синусоїдою)
    bits = [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0]
    bw = 2 * ehw / len(bits)
    prevy = ey + 16
    for k, bt in enumerate(bits):
        yy = ey - 16 if bt else ey + 16
        xa = b3x - ehw + k * bw
        if k > 0 and yy != prevy:
            frags.append(line(xa, prevy, xa, yy, color=FIELD, sw=1.6))
        frags.append(line(xa, yy, xa + bw, yy, color=FIELD, sw=1.8))
        prevy = yy
    frags.append(text(b3x, ey + 40, "хмарка бітів", size=10.5, color=MUTED))

    # 4) згладжена синусоїда на виході (та сама форма, чиста)
    ox = []
    for k in range(0, 49):
        t = k / 48.0
        yy = ey - 18 * math.sin(2 * math.pi * t)
        ox.append("%.1f,%.1f" % (b4x - ehw + t * 2 * ehw, yy))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(ox), POS))
    frags.append(text(b4x, ey + 40, "чистий тон", size=10.5, color=MUTED))

    # рамка «усе це — всередині одного переривання таймера»
    fx0, fy0 = b1x - w1 / 2 - 20, cy - h3 / 2 - 20
    fw = (b3x + w3 / 2 + 20) - fx0
    fh = (ey + 54) - fy0
    frags.append(rect(fx0, fy0, fw, fh, fill="none", stroke=MUTED, sw=1.4, rx=10))
    frags.append(text(fx0 + fw / 2, fy0 - 8,
                      "усе всередині ISR — лише цілочислові додавання й одне порівняння",
                      size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "firmware-chain.svg"), W, H, *frags,
           title="Чотири ланки одного переривання: від фази до плавної хвилі")


# ── B. Перший порядок проти другого: петлі поряд + спектри шуму ──────────────
def fig_order1_vs_order2():
    """Ліворуч дві структури: 1-й порядок — один акумулятор, переповнення дає біт;
    2-й порядок — два акумулятори каскадом, рішення бере знак другого, реально
    віддана порція повертається в обидва. Праворуч — спектри: нахил 2-го вдвічі
    крутіший, тож у робочій смузі шуму менше."""
    W, H = 900, 470
    frags = []

    # ─── ліва половина: дві структури петель ───
    # 1-й порядок (угорі зліва)
    ax = 96
    y1 = 96
    s_in1, wi1, hi1 = textbox(ax, y1, "рівень", size=12, pad=9, fill=FILL, stroke=INK, sw=1.6)
    s_a1, wa1, ha1 = textbox(ax + 168, y1, "акумулятор", size=12, pad=10,
                             fill="#dcf3e6", stroke=FIELD, sw=2)
    s_o1, wo1, ho1 = textbox(ax + 320, y1, "переповнення\n→ біт", size=12, pad=10,
                             fill="#fdecea", stroke=POS, sw=1.8)
    frags += [s_in1, s_a1, s_o1]
    frags.append(arrow(ax + wi1 / 2 + 4, y1, ax + 168 - wa1 / 2 - 4, y1, color=INK, sw=2))
    frags.append(arrow(ax + 168 + wa1 / 2 + 4, y1, ax + 320 - wo1 / 2 - 4, y1, color=INK, sw=2))
    # зворотний зв'язок 1-го порядку
    fby1 = y1 + 46
    frags.append(line(ax + 320, y1 + ho1 / 2 + 3, ax + 320, fby1, color=POS, sw=1.8))
    frags.append(line(ax + 320, fby1, ax + 168, fby1, color=POS, sw=1.8))
    frags.append(arrow(ax + 168, fby1, ax + 168, y1 + ha1 / 2 + 3, color=POS, sw=1.8))
    frags.append(text(ax + 150, y1 - hi1 / 2 - 14, "Перший порядок: один акумулятор",
                      size=13, color=FIELD, bold=True, anchor="start"))
    frags.append(text(ax + 244, fby1 + 15, "− повна порція, якщо ON", size=10.5, color=POS))

    # 2-й порядок (нижче зліва): два акумулятори каскадом
    y2 = 250
    s_in2, wi2, hi2 = textbox(ax, y2, "рівень", size=12, pad=9, fill=FILL, stroke=INK, sw=1.6)
    s_a2a, waa, haa = textbox(ax + 150, y2, "акум. 1", size=12, pad=10,
                              fill="#dcf3e6", stroke=FIELD, sw=2)
    s_a2b, wab, hab = textbox(ax + 286, y2, "акум. 2", size=12, pad=10,
                              fill="#cfeede", stroke=FIELD, sw=2.4)
    s_o2, wo2, ho2 = textbox(ax + 420, y2, "знак → біт", size=12, pad=10,
                             fill="#fdecea", stroke=POS, sw=1.8)
    frags += [s_in2, s_a2a, s_a2b, s_o2]
    frags.append(arrow(ax + wi2 / 2 + 4, y2, ax + 150 - waa / 2 - 4, y2, color=INK, sw=2))
    frags.append(arrow(ax + 150 + waa / 2 + 4, y2, ax + 286 - wab / 2 - 4, y2, color=INK, sw=2))
    frags.append(arrow(ax + 286 + wab / 2 + 4, y2, ax + 420 - wo2 / 2 - 4, y2, color=INK, sw=2))
    frags.append(text(ax, y2 - hi2 / 2 - 14, "Другий порядок: два акумулятори каскадом",
                      size=13, color=FIELD, bold=True, anchor="start"))

    # зворотний зв'язок 2-го: віддана порція заходить в ОБИДВА акумулятори
    fby2 = y2 + 66
    ox_fb = ax + 420
    frags.append(line(ox_fb, y2 + ho2 / 2 + 3, ox_fb, fby2, color=POS, sw=1.8))
    frags.append(line(ox_fb, fby2, ax + 150, fby2, color=POS, sw=1.8))
    frags.append(arrow(ax + 150, fby2, ax + 150, y2 + haa / 2 + 3, color=POS, sw=1.8))   # у 1-й
    frags.append(arrow(ax + 286, fby2, ax + 286, y2 + hab / 2 + 3, color=POS, sw=1.8))   # у 2-й
    frags.append(text(ax + 285, fby2 + 15,
                      "віддану порцію віднімають з ОБОХ", size=10.5, color=POS))

    # роздільна вертикаль між структурами й спектрами
    divx = 610
    frags.append(line(divx, 64, divx, H - 34, color="#dddddd", sw=1.4, dash="4,6"))

    # ─── права половина: спектри шуму 1-го vs 2-го порядку ───
    ox, oy = divx + 40, H - 78
    aw, ah = 210, 300
    frags.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))
    frags.append(line(ox, oy, ox, oy - ah - 4, color=INK, sw=2))
    frags.append(text(ox + aw, oy + 24, "частота →", size=12, color=INK, anchor="end"))
    frags.append(text(ox - 10, oy - ah + 2, "шум", size=12, color=INK, anchor="end", bold=True))

    # робоча смуга (вузька, зліва)
    bw = 0.20 * aw
    frags.append(rect(ox, oy - ah, bw, ah, fill="#eef6ff", stroke="none", rx=0))
    frags.append(line(ox + bw, oy, ox + bw, oy - ah, color=NEG, sw=1.2, dash="4,4"))
    frags.append(text(ox + bw + 4, oy - ah + 14, "робоча\nсмуга", size=10, color=NEG, anchor="start"))

    # крива 1-го порядку: пологий ріст ~ f
    p1 = []
    for k in range(0, 101):
        f = k / 100.0
        y = oy - 4 - (ah - 10) * f
        p1.append("%.1f,%.1f" % (ox + f * aw, y))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(p1), NEG))
    frags.append(text(ox + 0.72 * aw, oy - 0.52 * ah, "1-й\n(пологий)", size=11, color=NEG))

    # крива 2-го порядку: крутіший ріст ~ f²
    p2 = []
    for k in range(0, 101):
        f = k / 100.0
        y = oy - 4 - (ah - 10) * (f * f)
        p2.append("%.1f,%.1f" % (ox + f * aw, y))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
                 % (" ".join(p2), FIELD))
    frags.append(text(ox + 0.60 * aw, oy - 0.86 * ah, "2-й\n(крутіший)", size=11, color=FIELD))

    # акцент: у смузі 2-й нижче 1-го
    frags.append(text(ox + bw + 6, oy - 30,
                      "у смузі шуму\nу 2-го менше", size=10.5, color=FIELD, anchor="start"))
    frags.append(arrow(ox + bw * 0.5, oy - 0.30 * ah, ox + bw * 0.5, oy - 8, color=FIELD, sw=1.8))

    render(os.path.join(IMG, "order1-vs-order2.svg"), W, H, *frags,
           title="Один акумулятор проти двох — і що це дає спектру шуму")


# ════════════════════════════════════════════════════════════════════════════
#  Фігури для вставки math-noise-power.md (математика формування шуму)
# ════════════════════════════════════════════════════════════════════════════

# ── 5. NTF першого порядку: |2 sin(πf/fₛ)|, нуль на DC, лінійний ріст унизу ──
def fig_ntf():
    """Передавальна функція шуму |1 − z⁻¹| = |2 sin(πf/fₛ)|: дорівнює 0 на DC,
    унизу росте прямою ≈ 2πf/fₛ, нагорі сягає 2. Сигнал живе в лівій вузькій
    смузі — саме там, де крива притиснута до нуля."""
    W, H = 760, 400
    ox, oy = 86, H - 70
    aw, ah = 590, 268
    frags = []
    # осі
    frags.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))
    frags.append(line(ox, oy, ox, oy - ah - 6, color=INK, sw=2))
    frags.append(text(ox + aw, oy + 28, "частота  f / fₛ →", size=13, color=INK, anchor="end"))
    frags.append(text(ox - 12, oy - ah + 2, "|NTF|", size=13, color=INK, anchor="end", bold=True))
    # позначки на осі f: 0 .. 0.5 (Найквіст)
    for fr, lab in [(0.0, "0"), (0.25, "fₛ/4"), (0.5, "fₛ/2")]:
        xx = ox + fr / 0.5 * aw
        frags.append(line(xx, oy, xx, oy + 5, color=INK, sw=1.4))
        frags.append(text(xx, oy + 20, lab, size=11, color=MUTED))
    # рівень |NTF| = 2 (максимум на Найквісті)
    ytop = oy - ah
    frags.append(line(ox - 5, ytop, ox, ytop, color=INK, sw=1.4))
    frags.append(text(ox - 10, ytop + 4, "2", size=11, color=MUTED, anchor="end"))

    # робоча смуга (OSR великий → дуже вузька зліва)
    bw = 0.10 * aw
    frags.append(rect(ox, ytop, bw, ah, fill="#eef6ff", stroke="none", rx=0))
    frags.append(line(ox + bw, oy, ox + bw, ytop, color=NEG, sw=1.2, dash="4,4"))
    frags.append(text(ox + bw + 6, ytop + 16, "робоча\nсмуга (1/OSR)", size=11, color=NEG, anchor="start"))

    # повна крива |2 sin(πf/fₛ)|; нормуємо так, щоб значення 2 лягло на ytop
    def ntf(fr):                       # fr = f/fₛ у [0..0.5]
        return abs(2.0 * math.sin(math.pi * fr))
    pts = []
    for k in range(0, 121):
        fr = 0.5 * k / 120.0
        val = ntf(fr)
        y = oy - (val / 2.0) * ah
        pts.append("%.1f,%.1f" % (ox + fr / 0.5 * aw, y))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
                 % (" ".join(pts), FIELD))
    frags.append(text(ox + 0.66 * aw, oy - 0.40 * ah,
                      "|NTF| = |2 sin(πf/fₛ)|", size=13, color=FIELD, anchor="start"))

    # пряма-наближення внизу: 2πf/fₛ (дотична біля нуля), пунктир
    appts = []
    for k in range(0, 46):
        fr = 0.5 * k / 120.0 * (45.0 / 45.0)
        fr = 0.20 * k / 45.0           # до f/fₛ ≈ 0.20
        val = 2.0 * math.pi * fr
        if val > 2.05:
            break
        y = oy - (val / 2.0) * ah
        appts.append("%.1f,%.1f" % (ox + fr / 0.5 * aw, y))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="6,5"/>'
                 % (" ".join(appts), POS))
    frags.append(text(ox + 0.235 * aw, oy - 0.74 * ah,
                      "пряма ≈ 2πf/fₛ\n(низькі частоти)", size=11.5, color=POS, anchor="start"))

    # стрілка-акцент на нуль при DC
    frags.append(text(ox + 4, oy - 14, "нуль на DC", size=11.5, color=NEG, anchor="start"))
    frags.append(circle(ox, oy, 4.2, fill=NEG, stroke=NEG, sw=1))

    render(os.path.join(IMG, "ntf.svg"), W, H, *frags,
           title="Передавальна функція шуму першого порядку: нуль на DC, ріст угору")


# ── 6. Площа під формованим шумом у смузі: вужча смуга → стрімко менша площа ──
def fig_band_area():
    """Густина шуму після формування ~ (2πf/fₛ)² (парабола від нуля). Корисна смуга
    лежить зліва, де крива майже нуль; інтеграл (площа) у смузі = в-смузі-шум.
    Звужуючи смугу вдвічі (вищий OSR), відрізаємо площу, яка спадає як куб."""
    W, H = 760, 400
    ox, oy = 86, H - 64
    aw, ah = 590, 270
    frags = []
    frags.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))
    frags.append(line(ox, oy, ox, oy - ah - 6, color=INK, sw=2))
    frags.append(text(ox + aw, oy + 26, "частота →", size=13, color=INK, anchor="end"))
    frags.append(text(ox - 12, oy - ah + 2, "густина\nшуму", size=12.5, color=INK, anchor="end", bold=True))

    # парабола густини ~ f² (формований шум), нормована
    def dens(fr):                      # fr у [0..1] (частина до Найквіста)
        return fr * fr
    curve = []
    for k in range(0, 121):
        fr = k / 120.0
        y = oy - dens(fr) * (ah - 8)
        curve.append((ox + fr * aw, y))
    poly = " ".join("%.1f,%.1f" % p for p in curve)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (poly, FIELD))
    frags.append(text(ox + 0.60 * aw, oy - 0.30 * ah,
                      "формований шум ~ (2πf/fₛ)²", size=12.5, color=FIELD, anchor="start"))

    # дві межі смуги: широка (низький OSR) і вдвічі вужча (вищий OSR)
    fb_wide = 0.46
    fb_nar = 0.23
    def shade(fb, fillc, lab, labcol, dyl):
        xs = []
        for k in range(0, 61):
            fr = fb * k / 60.0
            y = oy - dens(fr) * (ah - 8)
            xs.append((ox + fr * aw, y))
        # замкнути полігон по осі
        pts = ["%.1f,%.1f" % (ox, oy)]
        pts += ["%.1f,%.1f" % p for p in xs]
        pts.append("%.1f,%.1f" % (ox + fb * aw, oy))
        frags.append('<polygon points="%s" fill="%s" stroke="none" opacity="0.55"/>'
                     % (" ".join(pts), fillc))
        xx = ox + fb * aw
        frags.append(line(xx, oy, xx, oy - dens(fb) * (ah - 8), color=labcol, sw=1.6, dash="4,4"))
        frags.append(text(xx, oy + dyl, lab, size=11, color=labcol, anchor="middle"))

    shade(fb_wide, "#dfe7fb", "межа смуги при OSR", NEG, 20)
    shade(fb_nar, "#cfeede", "при 2·OSR", FIELD, 38)

    # підписи площ
    frags.append(text(ox + 0.13 * aw, oy - 0.05 * ah, "площа =\nв-смузі-шум", size=11, color=FIELD))
    frags.append(text(ox + 0.34 * aw, oy - 0.16 * ah,
                      "відрізаний\nшмат", size=10.5, color=NEG))

    # підказка про куб
    s, w, h = textbox(ox + aw - 150, oy - ah + 60,
                      "смугу ÷2  →  площа ÷8\n(=  −9 дБ за октаву)",
                      size=12, pad=10, fill="#fff7ed", stroke=POS, sw=1.8, color=POS, bold=True)
    frags.append(s)

    render(os.path.join(IMG, "band-area.svg"), W, H, *frags,
           title="В-смузі-шум — це площа під параболою у вузькій смузі зліва")


# ── 7. Нахили SNR від передискретизації: 3 / 9 / 15 дБ за октаву ──────────────
def fig_slopes():
    """SNR(OSR) у напівлогарифмічних осях: горизонталь — log₂(OSR) (октави),
    вертикаль — SNR у дБ. Три прямі з нахилами 3, 9, 15 дБ/окт — усереднення,
    1-й, 2-й порядок. Видно, чому формування круте, а усереднення пологе."""
    W, H = 760, 420
    ox, oy = 86, H - 64
    aw, ah = 590, 300
    frags = []
    frags.append(line(ox, oy, ox + aw, oy, color=INK, sw=2))
    frags.append(line(ox, oy, ox, oy - ah - 6, color=INK, sw=2))
    frags.append(text(ox + aw, oy + 28, "октав передискретизації  log₂(OSR) →",
                      size=12.5, color=INK, anchor="end"))
    frags.append(text(ox - 12, oy - ah + 2, "SNR, дБ", size=12.5, color=INK, anchor="end", bold=True))

    octs = 8                # 0..8 октав по осі
    db_max = 130.0
    def X(o):
        return ox + (o / octs) * aw
    def Y(db):
        return oy - (db / db_max) * ah
    # сітка по октавах
    for o in range(0, octs + 1):
        frags.append(line(X(o), oy, X(o), oy + 5, color=INK, sw=1.2))
        frags.append(text(X(o), oy + 20, str(o), size=10.5, color=MUTED))
    # сітка по дБ
    for db in range(0, int(db_max) + 1, 30):
        frags.append(line(ox - 5, Y(db), ox, Y(db), color=INK, sw=1.2))
        frags.append(text(ox - 10, Y(db) + 4, str(db), size=10.5, color=MUTED, anchor="end"))
        frags.append(line(ox, Y(db), ox + aw, Y(db), color="#eeeeee", sw=1))

    base = 14.0            # умовна стартова «підлога» (1-біт, OSR=1)
    def linef(slope, col, lab, laby):
        pts = "%.1f,%.1f %.1f,%.1f" % (X(0), Y(base), X(octs), Y(base + slope * octs))
        frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (pts, col))
        frags.append(text(X(octs) - 4, Y(base + slope * octs) + laby, lab,
                          size=12, color=col, anchor="end", bold=True))

    linef(3.0, MUTED, "усереднення: 3 дБ/окт", 16)
    linef(9.0, FIELD, "1-й порядок: 9 дБ/окт", -6)
    linef(15.0, POS, "2-й порядок: 15 дБ/окт", -6)

    # позначка «½ біта / 1.5 біта / 2.5 біта за октаву»
    s, w, h = textbox(ox + 0.30 * aw, Y(108),
                      "за октаву:  ½ біт · 1.5 біт · 2.5 біт\nправило (6L+3) дБ/окт",
                      size=11.5, pad=9, fill="#f4f6f8", stroke=INK, sw=1.4)
    frags.append(s)

    render(os.path.join(IMG, "slopes.svg"), W, H, *frags,
           title="Нахил SNR від передискретизації: чому формування круте")


if __name__ == "__main__":
    fig_pwm_vs_pdm()
    fig_loop()
    fig_noise_shape()
    fig_ripple()
    fig_firmware_chain()
    fig_order1_vs_order2()
    fig_ntf()
    fig_band_area()
    fig_slopes()
    print("ok: figures written to", IMG)
