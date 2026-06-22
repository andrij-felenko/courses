# -*- coding: utf-8 -*-
# Фігури теми «Гістерезис і тригер Шмітта» (analog/schmitt-trigger).
# svgkit імпортуємо зі scripts/, не переписуємо (§5). Вивід — у ./img/.
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── two-thresholds: два пороги й «нечутлива смуга» між ними ───────────────────
# Ідея: один поріг → брязкіт; два пороги (VH угору, VL униз) лишають між собою
# смугу, де вихід глухий до шуму — це й є гістерезис.
def fig_two_thresholds():
    W, H = 700, 300
    ox, oy = 70, 250
    aw, ah = 560, 196
    p = []
    vh = oy - ah * 0.66          # верхній поріг
    vl = oy - ah * 0.34          # нижній поріг

    # «нечутлива смуга» між порогами
    p.append(rect(ox, vh, aw, vl - vh, fill="#fbf3e0", stroke="#e0c98a", sw=0.8, rx=0))

    # осі
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "час", size=12, color=INK, italic=True))
    p.append(text(ox - 16, oy - ah - 2, "сигнал", size=12, color=INK, anchor="end", italic=True))

    # сигнал, що піднімається й опускається (трикутник), перетинає обидва пороги
    p.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f" fill="none" stroke="%s" '
             'stroke-width="2.4" stroke-linejoin="round"/>'
             % (ox, oy - ah * 0.10, ox + aw * 0.5, oy - ah * 0.92,
                ox + aw, oy - ah * 0.10, NEG))

    # пороги
    p.append(line(ox, vh, ox + aw, vh, color=POS, sw=1.6, dash="6 4"))
    p.append(text(ox + aw + 6, vh + 4, "VH", size=12, color=POS, anchor="start", bold=True))
    p.append(line(ox, vl, ox + aw, vl, color=FIELD, sw=1.6, dash="6 4"))
    p.append(text(ox + aw + 6, vl + 4, "VL", size=12, color=FIELD, anchor="start", bold=True))

    p.append(text(ox + aw * 0.5, (vh + vl) / 2 + 4, "вихід тримає стан (пам'ять)",
                  size=12, color="#9a7b2e", bold=True))
    p.append(text(ox + aw * 0.23, oy - ah * 0.97, "угору: на VH",
                  size=11, color=POS, bold=True))
    p.append(text(ox + aw * 0.77, oy - ah * 0.97, "униз: на VL",
                  size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "two-thresholds.svg"), W, H, *p,
           title="Два пороги замість одного: смуга між ними — гістерезис")


# ── positive-feedback: частину виходу повертають на «+», поріг тікає за виходом ─
# Ідея: компаратор, дільник вертає частку виходу на неінвертуючий вхід; вихід
# угорі піднімає поріг (VH), унизу опускає (VL).
def fig_positive_feedback():
    W, H = 700, 320
    p = []
    cx, cy = 300, 160            # центр трикутника-компаратора
    tw, th = 120, 120

    # трикутник компаратора
    p.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="%s" stroke="%s" '
             'stroke-width="1.8"/>' % (cx - tw / 2, cy - th / 2, cx - tw / 2, cy + th / 2,
                                       cx + tw / 2, cy, FILL, LINE))
    # входи
    p.append(plus(cx - tw / 2 + 16, cy - th * 0.25, r=10))
    p.append(minus(cx - tw / 2 + 16, cy + th * 0.25, r=10))

    # сигнал на «−»
    p.append(arrow(cx - tw / 2 - 110, cy + th * 0.25, cx - tw / 2 - 2, cy + th * 0.25,
                   color=INK, sw=1.7))
    p.append(text(cx - tw / 2 - 112, cy + th * 0.25 - 8, "сигнал", size=12, color=INK, anchor="start"))

    # вихід
    outx = cx + tw / 2
    p.append(arrow(outx, cy, outx + 150, cy, color=INK, sw=2.0))
    p.append(text(outx + 150, cy - 10, "вихід", size=12, color=INK, anchor="end"))

    # дільник зворотного зв'язку на «+»
    nodex = outx + 90
    fbx = cx - tw / 2 + 16
    fby = cy - th * 0.25
    p.append(line(nodex, cy, nodex, cy + 110, color=POS, sw=1.7))
    p.append(line(nodex, cy + 110, fbx, cy + 110, color=POS, sw=1.7))
    p.append(arrow(fbx, cy + 110, fbx, fby + 12, color=POS, sw=1.7))
    rb, rbw, rbh = textbox(nodex, cy + 60, "частка\nвиходу", size=11, color=POS,
                           stroke=POS, fill="#fdecea")
    p.append(rb)
    p.append(text(fbx + 6, cy + 104, "на «+»", size=11, color=POS, anchor="start", bold=True))

    # підписи логіки порога
    b1, _, _ = textbox(cx + tw / 2 + 70, cy - 92, "вихід угорі → поріг ↑ = VH",
                       size=11, color=POS, stroke=POS, fill="#fdecea")
    b2, _, _ = textbox(cx + tw / 2 + 70, cy - 62, "вихід унизу → поріг ↓ = VL",
                       size=11, color=FIELD, stroke=FIELD, fill="#eafaf0")
    p.append(b1)
    p.append(b2)

    render(os.path.join(OUT, "positive-feedback.svg"), W, H, *p,
           title="Додатний зв'язок на «+»: поріг рухається слідом за виходом")


# ── transfer-loop: передатна крива «вихід від входу» з петлею ─────────────────
# Ідея: вгору вихід стрибає на VH, униз падає на VL; шляхи не збігаються — петля
# = «пам'ять». Стрілками показано напрям обходу.
def fig_transfer_loop():
    W, H = 700, 320
    ox, oy = 110, 250
    aw, ah = 480, 196
    p = []
    lo = oy - ah * 0.12          # рівень «низько»
    hi = oy - ah * 0.88          # рівень «високо»
    xvl = ox + aw * 0.36         # VL по осі входу
    xvh = ox + aw * 0.66         # VH по осі входу

    # осі
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "вхід", size=12, color=INK, italic=True))
    p.append(text(ox - 16, oy - ah - 2, "вихід", size=12, color=INK, anchor="end", italic=True))

    # нижня гілка (вхід росте): низько до VH, тоді стрибок угору
    p.append(line(ox, lo, xvh, lo, color=POS, sw=2.6))
    p.append(arrow((ox + xvh) / 2 - 8, lo, (ox + xvh) / 2 + 8, lo, color=POS, sw=2.6))
    p.append(line(xvh, lo, xvh, hi, color=POS, sw=2.6, dash="4 3"))

    # верхня гілка (вхід падає): високо до VL, тоді стрибок униз
    p.append(line(xvl, hi, ox + aw - 20, hi, color=NEG, sw=2.6))
    p.append(arrow((xvl + ox + aw - 20) / 2 + 8, hi, (xvl + ox + aw - 20) / 2 - 8, hi,
                   color=NEG, sw=2.6))
    p.append(line(xvl, hi, xvl, lo, color=NEG, sw=2.6, dash="4 3"))

    # пороги по осі входу
    p.append(line(xvl, oy, xvl, oy + 6, color=FIELD, sw=1.6))
    p.append(text(xvl, oy + 20, "VL", size=12, color=FIELD, bold=True))
    p.append(line(xvh, oy, xvh, oy + 6, color=POS, sw=1.6))
    p.append(text(xvh, oy + 20, "VH", size=12, color=POS, bold=True))

    p.append(text(ox + aw * 0.5, hi - 12, "вхід падає ←", size=11, color=NEG, bold=True))
    p.append(text(ox + aw * 0.30, lo + 18, "вхід росте →", size=11, color=POS, bold=True))
    p.append(text(ox + aw * 0.5, (hi + lo) / 2, "ширина петлі = гістерезис",
                  size=12, color="#9a7b2e", bold=True))

    render(os.path.join(OUT, "transfer-loop.svg"), W, H, *p,
           title="Передатна крива з петлею: шлях угору й униз різний")


# ── kills-chatter: один шумний сигнал, два пороги — вихід чистий ──────────────
# Ідея: верхня панель — зашумлений сигнал між порогами; нижня — чистий вихід
# з одним перемиканням, бо шум менший за зазор.
def fig_kills_chatter():
    W, H = 720, 360
    ox = 70
    aw = 580
    p = []

    # ВЕРХ: сигнал і пороги
    oy1, ah1 = 170, 130
    vh = oy1 - ah1 * 0.62
    vl = oy1 - ah1 * 0.34
    p.append(rect(ox, vh, aw, vl - vh, fill="#fbf3e0", stroke="#e0c98a", sw=0.8, rx=0))
    p.append(arrow(ox, oy1, ox, oy1 - ah1 - 8, color=INK, sw=1.5))
    p.append(arrow(ox, oy1, ox + aw, oy1, color=INK, sw=1.5))
    p.append(text(ox - 16, oy1 - ah1, "сигнал", size=11, color=INK, anchor="end", italic=True))

    # зашумлена наростаюча крива (детермінований «шум»)
    pts = []
    n = 220
    for i in range(n + 1):
        t = i / n
        base = ah1 * (0.12 + 0.78 * t)
        noise = ah1 * 0.10 * math.sin(t * 47) * math.cos(t * 13)
        pts.append("%.1f,%.1f" % (ox + t * aw, oy1 - (base + noise)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" '
             'stroke-linejoin="round"/>' % (" ".join(pts), NEG))
    p.append(line(ox, vh, ox + aw, vh, color=POS, sw=1.4, dash="6 4"))
    p.append(text(ox + aw + 6, vh + 4, "VH", size=11, color=POS, anchor="start", bold=True))
    p.append(line(ox, vl, ox + aw, vl, color=FIELD, sw=1.4, dash="6 4"))
    p.append(text(ox + aw + 6, vl + 4, "VL", size=11, color=FIELD, anchor="start", bold=True))
    p.append(text(ox + aw * 0.5, (vh + vl) / 2 + 4, "шум менший за зазор",
                  size=11, color="#9a7b2e", bold=True))

    # точка перетину VH (де вихід перекидається)
    tx = ox + aw * 0.64
    p.append(line(tx, oy1, tx, 320, color=MUTED, sw=1.0, dash="3 4"))

    # НИЗ: чистий вихід — одна сходинка
    oy2, ah2 = 320, 70
    p.append(arrow(ox, oy2, ox, oy2 - ah2 - 8, color=INK, sw=1.5))
    p.append(arrow(ox, oy2, ox + aw, oy2, color=INK, sw=1.5))
    p.append(text(ox - 16, oy2 - ah2, "вихід", size=11, color=INK, anchor="end", italic=True))
    p.append(text(ox + aw, oy2 + 18, "час", size=11, color=INK, italic=True))
    p.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f L %.1f,%.1f" fill="none" '
             'stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>'
             % (ox, oy2 - 6, tx, oy2 - 6, tx, oy2 - ah2 + 6, ox + aw, oy2 - ah2 + 6, FIELD))
    p.append(text(ox + aw * 0.3, oy2 - 18, "один чистий перехід", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "kills-chatter.svg"), W, H, *p,
           title="Той самий шумний сигнал — але вихід без брязкоту")


# ── thermostat: гістерезис у термостаті — мертва зона 19…21° ──────────────────
# Ідея: котел гріє до 21°, вимикається; вмикається знов лише з 19°. Між ними —
# мертва зона, що не дає брязкати.
def fig_thermostat():
    W, H = 700, 300
    ox, oy = 70, 250
    aw, ah = 560, 196
    p = []
    t21 = oy - ah * 0.80
    t19 = oy - ah * 0.40

    p.append(rect(ox, t21, aw, t19 - t21, fill="#fbf3e0", stroke="#e0c98a", sw=0.8, rx=0))
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "час", size=12, color=INK, italic=True))
    p.append(text(ox - 16, oy - ah - 2, "T °C", size=12, color=INK, anchor="end", italic=True))

    # пилкоподібна температура: гріється до 21, падає до 19, знову гріється
    seg = [(0.00, 0.40), (0.22, 0.80), (0.44, 0.40), (0.66, 0.80), (0.88, 0.40), (1.00, 0.58)]
    pts = ["%.1f,%.1f" % (ox + tx * aw, oy - ah * h) for tx, h in seg]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round"/>' % (" ".join(pts), NEG))

    p.append(line(ox, t21, ox + aw, t21, color=POS, sw=1.6, dash="6 4"))
    p.append(text(ox + aw + 6, t21 + 4, "21° викл", size=11, color=POS, anchor="start", bold=True))
    p.append(line(ox, t19, ox + aw, t19, color=FIELD, sw=1.6, dash="6 4"))
    p.append(text(ox + aw + 6, t19 + 4, "19° вкл", size=11, color=FIELD, anchor="start", bold=True))
    p.append(text(ox + aw * 0.5, (t21 + t19) / 2 + 4, "мертва зона",
                  size=12, color="#9a7b2e", bold=True))

    render(os.path.join(OUT, "thermostat.svg"), W, H, *p,
           title="Термостат: гріє до 21°, вмикає знов лише з 19°")


# ── schmitt: символ тригера Шмітта + походження від нерва кальмара ────────────
# Ідея: трикутник-буфер зі значком петлі гістерезису всередині; коротка лінія
# історії — нерв «все-або-нічого» → електроніка (Отто Шмітт, 1934/1937).
def fig_schmitt():
    W, H = 700, 300
    p = []

    # символ: буфер-трикутник зі значком петлі
    cx, cy = 220, 150
    tw, th = 130, 120
    p.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="%s" stroke="%s" '
             'stroke-width="1.8"/>' % (cx - tw / 2, cy - th / 2, cx - tw / 2, cy + th / 2,
                                       cx + tw / 2, cy, FILL, LINE))
    # значок петлі гістерезису всередині трикутника
    gx, gy, gw, gh = cx - 30, cy, 44, 26
    p.append('<path d="M %.1f,%.1f h %.1f M %.1f,%.1f h %.1f M %.1f,%.1f v %.1f M %.1f,%.1f v %.1f" '
             'fill="none" stroke="%s" stroke-width="2.2"/>'
             % (gx, gy + gh / 2, gw * 0.6, gx + gw * 0.4, gy - gh / 2, gw * 0.6,
                gx + gw * 0.4, gy + gh / 2, -gh, gx + gw, gy - gh / 2, gh, INK))
    # вхід/вихід
    p.append(arrow(cx - tw / 2 - 80, cy, cx - tw / 2 - 2, cy, color=INK, sw=1.7))
    p.append(text(cx - tw / 2 - 82, cy - 8, "вхід", size=12, color=INK, anchor="start"))
    p.append(arrow(cx + tw / 2, cy, cx + tw / 2 + 80, cy, color=INK, sw=1.7))
    p.append(text(cx + tw / 2 + 80, cy - 8, "вихід", size=12, color=INK, anchor="end"))
    p.append(text(cx, cy + th / 2 + 24, "символ тригера Шмітта", size=12, color=MUTED))

    # ланцюжок історії праворуч
    bx = 470
    b1, w1, h1 = textbox(bx, 110, "нерв кальмара:\n«все-або-нічого»", size=11,
                         stroke=FIELD, fill="#eafaf0")
    p.append(b1)
    b2, w2, h2 = textbox(bx, 200, "електроніка:\nдва пороги + пам'ять", size=11,
                         stroke=NEG, fill="#eaf0fd")
    p.append(b2)
    p.append(arrow(bx, 110 + h1 / 2, bx, 200 - h2 / 2, color=INK, sw=1.7))
    p.append(text(bx, 262, "Отто Шмітт, 1934/1937", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "schmitt.svg"), W, H, *p,
           title="Тригер Шмітта: від нерва кальмара до електроніки")


if __name__ == "__main__":
    fig_two_thresholds()
    fig_positive_feedback()
    fig_transfer_loop()
    fig_kills_chatter()
    fig_thermostat()
    fig_schmitt()
    print("analog/schmitt-trigger: 6 фігур згенеровано у", OUT)
