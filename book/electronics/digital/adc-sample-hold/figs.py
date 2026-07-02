# -*- coding: utf-8 -*-
"""Фігури для теми adc-sample-hold. Запуск: python figs.py → ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Схема ядра S/H: ключ + конденсатор + буфер ───────────────────────────
def fig_circuit():
    W, H = 720, 340
    p = []
    p.append(text(W/2, 26, "Ядро вибірки-зберігання: ключ, конденсатор пам'яті, буфер", size=16, bold=True))

    y = 150               # рівень сигнальної шини
    x_in = 70
    x_sw1, x_sw2 = 190, 300   # межі ключа
    x_node = 300          # вузол пам'яті (після ключа)
    x_buf = 470           # вхід буфера
    x_out = 660

    # вхідна лінія
    p.append(text(x_in-6, y-16, "vвх", size=14, italic=True, anchor="end"))
    p.append(line(x_in, y, x_sw1, y, color=INK, sw=2))
    p.append(circle(x_in, y, 4, fill=INK, stroke=INK))

    # ключ (розмикач) із керуванням «такт»
    p.append(circle(x_sw1, y, 4, fill=INK, stroke=INK))
    p.append(line(x_sw1, y, x_sw2-6, y-22, color=POS, sw=2.4))   # розімкнений контакт
    p.append(circle(x_sw2, y, 4, fill=INK, stroke=INK))
    box = fitbox(x_sw1-24, y-92, 92, 34, "ключ", size=13, fill="#fdecea", stroke=POS)
    p.append(box)
    p.append(line((x_sw1+x_sw2)/2-6, y-58, (x_sw1+x_sw2)/2-6, y-24, color=POS, sw=1.4, dash="4 3"))
    p.append(text((x_sw1+x_sw2)/2+70, y-70, "керує такт", size=12, color=MUTED, anchor="start"))

    # вузол пам'яті → конденсатор на землю
    p.append(line(x_node, y, x_buf-6, y, color=INK, sw=2))
    p.append(circle(x_node, y, 4, fill=INK, stroke=INK))
    # конденсатор вниз
    cy = y+58
    p.append(line(x_node, y, x_node, cy-10, color=INK, sw=2))
    p.append(line(x_node-20, cy-10, x_node+20, cy-10, color=INK, sw=2.4))   # верхня пластина
    p.append(line(x_node-20, cy,    x_node+20, cy,    color=INK, sw=2.4))   # нижня пластина
    p.append(text(x_node+30, cy-4, "Cз", size=14, italic=True, anchor="start"))
    # земля
    gy = cy+30
    p.append(line(x_node, cy, x_node, gy, color=INK, sw=2))
    for i, wdt in enumerate((22, 14, 6)):
        p.append(line(x_node-wdt, gy+i*5, x_node+wdt, gy+i*5, color=INK, sw=2))

    # буфер — трикутник (одиничний підсилювач)
    tb = 34
    p.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f Z" fill="#eaf0fd" stroke="%s" stroke-width="1.8"/>'
             % (x_buf, y-tb, x_buf, y+tb, x_buf+70, y, NEG))
    p.append(text(x_buf+22, y+5, "×1", size=14, color=NEG, bold=True))
    p.append(text(x_buf+30, y+tb+18, "буфер", size=12, color=MUTED))

    # вихід до АЦП
    p.append(line(x_buf+70, y, x_out, y, color=INK, sw=2))
    p.append(circle(x_out, y, 4, fill=INK, stroke=INK))
    p.append(text(x_out-4, y-16, "до АЦП", size=13, anchor="end"))

    # дві фази — підписи-рамки внизу
    b1 = fitbox(60, 250, 300, 60,
                "СТЕЖЕННЯ: ключ замкнений\nCз повторює vвх", size=13,
                fill="#eafaf0", stroke=FIELD)
    p.append(b1)
    b2 = fitbox(390, 250, 300, 60,
                "ЗБЕРІГАННЯ: ключ розімкнений\nCз тримає останнє vвх", size=13,
                fill=FILL, stroke=LINE)
    p.append(b2)

    render(os.path.join(IMG, "sh-circuit.svg"), W, H, *p)


# ── 2. Осцилограма: вхід, слідування, заморожування ─────────────────────────
def fig_waveform():
    W, H = 720, 360
    p = []
    p.append(text(W/2, 26, "Слідкувати — заморозити — слідкувати знову", size=16, bold=True))

    ox, oy = 60, 285          # початок осей
    ax_w, ax_h = 620, 220
    p.append(line(ox, oy, ox+ax_w, oy, color=INK, sw=1.6))          # X
    p.append(line(ox, oy, ox, oy-ax_h, color=INK, sw=1.6))          # Y
    p.append(text(ox+ax_w-4, oy+22, "час", size=12, color=MUTED, anchor="end"))
    p.append(text(ox-10, oy-ax_h+6, "V", size=12, color=MUTED, anchor="end"))

    def X(t):  return ox + t*ax_w
    def Y(v):  return oy - (v*0.5+0.5)*ax_h*0.9    # v у [-1..1] → в межах осі

    # вхідна синусоїда (тонка, сіра)
    N = 260
    pts = []
    for i in range(N+1):
        t = i/N
        v = math.sin(2*math.pi*1.4*t)
        pts.append("%.1f,%.1f" % (X(t), Y(v)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="3 3"/>'
             % (" ".join(pts), MUTED))
    p.append(text(X(0.02), Y(math.sin(2*math.pi*1.4*0.02))-10, "вхід", size=12, color=MUTED, anchor="start"))

    # фази: track [0..0.22], hold [0.22..0.42], track [0.42..0.64], hold [0.64..0.84], track...
    edges = [0.0, 0.24, 0.44, 0.68, 0.88, 1.0]
    hold_spans = [(0.24, 0.44), (0.68, 0.88)]
    # смуги «зберігання»
    for a, b in hold_spans:
        p.append(rect(X(a), oy-ax_h, X(b)-X(a), ax_h, fill="#fbeee9", stroke="none", rx=0))

    # вихід S/H: під час track = сигнал; під час hold = плоско (з легким провисанням)
    out = []
    step = 1/N
    held = None
    for i in range(N+1):
        t = i/N
        in_hold = any(a <= t < b for a, b in hold_spans)
        if in_hold:
            if held is None:
                held = math.sin(2*math.pi*1.4*t)
                hold_start = t
            # легкий спад (провисання) під час зберігання
            v = held - 0.10*(t-hold_start)/0.20
        else:
            held = None
            v = math.sin(2*math.pi*1.4*t)
        out.append("%.1f,%.1f" % (X(t), Y(v)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(out), POS))
    p.append(text(X(0.55), Y(math.sin(2*math.pi*1.4*0.55))+18, "вихід S/H", size=12, color=POS, anchor="middle"))

    # підписи фаз під віссю
    for a, b, lbl, col in [(0.0,0.24,"стеження",FIELD),(0.24,0.44,"зберігання",POS),
                           (0.44,0.68,"стеження",FIELD),(0.68,0.88,"зберігання",POS)]:
        p.append(text((X(a)+X(b))/2, oy+22, lbl, size=11.5, color=col))

    # момент вибірки — вертикальна риска на кожному переході track→hold
    for a, _ in hold_spans:
        p.append(line(X(a), oy-ax_h, X(a), oy, color=NEG, sw=1.4, dash="4 3"))
    p.append(text(X(0.24)+6, oy-ax_h+14, "мить вибірки", size=11.5, color=NEG, anchor="start"))

    render(os.path.join(IMG, "track-hold-waveform.svg"), W, H, *p)


# ── 3. Три похибки плато зберігання: п'єдестал, провисання, шум ──────────────
def fig_hold_errors():
    W, H = 720, 340
    p = []
    p.append(text(W/2, 26, "Що псує заморожену напругу під час зберігання", size=16, bold=True))

    ox, oy = 70, 250
    ax_w, ax_h = 600, 190
    p.append(line(ox, oy, ox+ax_w, oy, color=INK, sw=1.6))
    p.append(line(ox, oy, ox, oy-ax_h, color=INK, sw=1.6))
    p.append(text(ox+ax_w-4, oy+22, "час", size=12, color=MUTED, anchor="end"))
    p.append(text(ox-12, oy-ax_h+4, "V", size=12, color=MUTED, anchor="end"))

    def X(t): return ox + t*ax_w
    Vt = oy-130     # рівень «істинної» замороженої напруги
    ped = 22        # висота п'єдесталу (крок)
    t_s = 0.30      # мить розмикання ключа

    # фаза стеження — сигнал слідує (пряма похила до миті вибірки)
    p.append(line(X(0.02), oy-70, X(t_s), Vt, color=FIELD, sw=2.4))
    p.append(text(X(0.10), oy-64, "стеження", size=12, color=FIELD, anchor="start"))

    # істинний рівень (пунктир) — те, що мало б заморозитися
    p.append(line(X(t_s), Vt, X(0.98), Vt, color=MUTED, sw=1.4, dash="5 4"))
    p.append(text(X(0.96), Vt-8, "мало бути", size=11.5, color=MUTED, anchor="end"))

    # реальний рівень: стрибок п'єдесталу вниз, тоді повільне провисання
    yr0 = Vt+ped
    seg = []
    Npt = 120
    for i in range(Npt+1):
        t = t_s + (0.98-t_s)*i/Npt
        droop = 40*(t-t_s)/(0.98-t_s)          # лінійне провисання
        v = yr0 + droop
        # дрібний шум
        v += 2.2*math.sin(40*t)
        seg.append("%.1f,%.1f" % (X(t), v))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(seg), POS))

    # 1) п'єдестал — вертикальна стрілка кроку
    p.append(line(X(t_s), Vt, X(t_s), yr0, color=NEG, sw=1.4, dash="3 3"))
    ab = fitbox(X(t_s)+8, Vt-6, 150, 34, "1. п'єдестал\n(вкидання заряду)", size=11.5,
                fill="#eaf0fd", stroke=NEG)
    p.append(ab)

    # 2) провисання — стрілка нахилу
    p.append(arrow(X(0.72), yr0+8, X(0.92), yr0+38, color=INK, sw=1.6))
    bb = fitbox(X(0.60), oy-46, 190, 32, "2. провисання (витік Cз)", size=11.5,
                fill=FILL, stroke=LINE)
    p.append(bb)

    # 3) шум — підпис на брижах
    cb = fitbox(X(0.30), oy-176, 200, 30, "3. шум вибірки (kT/C, дрож)", size=11.5,
                fill="#eafaf0", stroke=FIELD)
    p.append(cb)

    # мить вибірки
    p.append(line(X(t_s), oy, X(t_s), oy-ax_h, color=MUTED, sw=1.0, dash="2 4"))
    p.append(text(X(t_s), oy+22, "мить вибірки", size=11.5, color=MUTED))

    render(os.path.join(IMG, "hold-errors.svg"), W, H, *p)


# ── 4. Історична лінія: від аналогових машин до масиву в SAR (для hist-вставки) ─
def fig_history():
    W, H = 760, 320
    p = []
    p.append(text(W/2, 26, "Родовід вузла: від аналогових машин до масиву в мікросхемі", size=16, bold=True))

    ox, oxe = 60, 700
    y = 96                      # рівень стрічки часу
    p.append(line(ox, y, oxe, y, color=INK, sw=2.2))
    p.append(arrow(oxe-2, y, oxe+2, y, color=INK, sw=2.2))

    # вузли часу: (частка вздовж, рік, назва, підпис-суть, колір, зверху/знизу)
    nodes = [
        (0.00, "1930-40-і", "аналогові машини",
         "інтегратор із режимом\n«тримати» (HOLD)", FIELD, "up"),
        (0.24, "1950-і",    "дискретні дані",
         "«track-and-hold»,\n«boxcar» у теорії", NEG, "down"),
        (0.50, "1969",      "перші модулі S/H",
         "SHA1/SHA2 на платах\n(Pastoriza / ADI)", POS, "up"),
        (0.72, "1975",      "монолітні S/H",
         "одна мікросхема\n(BI-FET, LF198/398)", NEG, "down"),
        (0.94, "1975+",     "масив у SAR",
         "вибірка = самі\nконденсатори АЦП", FIELD, "up"),
    ]
    for frac, yr, name, note, col, side in nodes:
        x = ox + frac*(oxe-ox-30)
        p.append(circle(x, y, 6, fill=col, stroke=col))
        p.append(text(x, y-14 if side == "up" else y+24, yr, size=12.5, color=col, bold=True))
        bw, bh = 168, 52
        by = (y-14-18-bh) if side == "up" else (y+24+8)
        bx = min(max(x-bw/2, 4), W-bw-4)
        p.append(fitbox(bx, by, bw, bh, name+"\n"+note, size=11.5,
                        fill=(FILL if side == "down" else "#eafaf0"),
                        stroke=col))
        # поводок від вузла до рамки
        p.append(line(x, y-8 if side == "up" else y+8,
                      x, by+bh if side == "up" else by, color=col, sw=1.0, dash="3 3"))

    # наскрізна думка внизу
    p.append(fitbox(60, 268, 640, 40,
             "Незмінна суть крізь усі втілення: замкни ключ — заряди конденсатор — розімкни й тримай мить нерухомою.",
             size=12.5, fill="#fffef2", stroke=MUTED))
    render(os.path.join(IMG, "sh-history.svg"), W, H, *p)


# ── 5. Крива набору: недобір падає, пороги розрядності перетинають її ────────
def fig_acq_settling():
    W, H = 720, 360
    p = []
    p.append(text(W/2, 26, "Скільки сталих часу треба на N розрядів", size=16, bold=True))

    ox, oy = 70, 290
    ax_w, ax_h = 590, 240
    p.append(line(ox, oy, ox+ax_w, oy, color=INK, sw=1.6))          # X
    p.append(line(ox, oy, ox, oy-ax_h, color=INK, sw=1.6))          # Y
    p.append(text(ox+ax_w-4, oy+22, "сталі часу k = t/τ", size=12, color=MUTED, anchor="end"))
    p.append(text(ox-12, oy-ax_h+2, "недобір", size=11.5, color=MUTED, anchor="end"))
    p.append(text(ox-12, oy-ax_h+16, "(лог)", size=11.5, color=MUTED, anchor="end"))

    kmax = 14.0
    def X(k):  return ox + (k/kmax)*ax_w
    def Y(k):  return (oy-ax_h) + (k/kmax)*ax_h   # лог-шкала: недобір e^-k

    # сітка по цілих k
    for k in range(0, int(kmax)+1, 2):
        p.append(line(X(k), oy, X(k), oy-ax_h, color="#eeeeee", sw=1.0))
        p.append(text(X(k), oy+16, str(k), size=11, color=MUTED))

    # крива недобору = пряма на лог-шкалі
    pts = []
    NN = 120
    for i in range(NN+1):
        k = kmax*i/NN
        pts.append("%.1f,%.1f" % (X(k), Y(k)))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), POS))
    p.append(text(X(2.4), Y(2.4)-8, "e⁻ᵏ", size=13, color=POS, anchor="start", italic=True))

    # горизонтальні пороги 1/2^(N+1) для N=8,12,16 → рівень k=(N+1)ln2
    for n, col, lbl in [(8, FIELD, "8 біт"), (12, NEG, "12 біт"), (16, INK, "16 біт")]:
        kth = (n+1)*math.log(2)
        yy = Y(kth)
        p.append(line(ox, yy, X(kth), yy, color=col, sw=1.4, dash="5 4"))
        p.append(line(X(kth), yy, X(kth), oy, color=col, sw=1.2, dash="2 3"))
        p.append(circle(X(kth), yy, 4, fill=col, stroke=col))
        p.append(text(ox+6, yy-5, "½ мл. розряду, %s → k≈%.1f" % (lbl, kth),
                      size=11, color=col, anchor="start"))

    render(os.path.join(IMG, "acq-settling.svg"), W, H, *p)


# ── 6. Дві топології входу: високоомний давач напряму vs через буфер ─────────
def fig_buffer_vs_direct():
    W, H = 720, 340
    p = []
    p.append(text(W/2, 26, "Високоомний давач: напряму vs через буфер", size=16, bold=True))

    def adc_input(x0, y):
        s = []
        s.append(line(x0, y, x0+26, y, color=INK, sw=2))
        s.append(circle(x0+26, y, 3.5, fill=INK, stroke=INK))
        s.append(line(x0+26, y, x0+50, y-16, color=POS, sw=2.2))   # розімкнений ключ
        s.append(circle(x0+50, y, 3.5, fill=INK, stroke=INK))
        s.append(text(x0+38, y-24, "ключ", size=10.5, color=POS, anchor="middle"))
        s.append(line(x0+50, y, x0+50, y+22, color=INK, sw=2))
        s.append(line(x0+36, y+22, x0+64, y+22, color=INK, sw=2.2))
        s.append(line(x0+36, y+30, x0+64, y+30, color=INK, sw=2.2))
        s.append(text(x0+70, y+28, "Cз", size=11.5, italic=True, anchor="start"))
        gy = y+48
        s.append(line(x0+50, y+30, x0+50, gy, color=INK, sw=2))
        for i, wdt in enumerate((16, 10, 4)):
            s.append(line(x0+50-wdt, gy+i*4, x0+50+wdt, gy+i*4, color=INK, sw=1.8))
        return s

    y = 152
    # ── ліва половина: напряму ──
    p.append(fitbox(40, 250, 300, 66,
                    "НАПРЯМУ: Cз повзе через величезний Rдж —\nнабір десятки мкс або не встигає",
                    size=12, fill="#fbeee9", stroke=POS))
    xs = 70
    p.append(circle(xs, y, 16, fill=FILL, stroke=INK, sw=1.8))
    p.append(text(xs, y+5, "~", size=18, color=INK))
    p.append(text(xs, y-26, "давач", size=11, color=MUTED))
    p.append(line(xs+16, y, xs+40, y, color=INK, sw=2))
    p.append(rect(xs+40, y-9, 46, 18, fill="#fdecea", stroke=POS, sw=1.6, rx=3))
    p.append(text(xs+63, y+4, "Rдж", size=11.5, color=POS, italic=True))
    p.append(text(xs+63, y-16, "сотні кОм", size=10, color=POS))
    p.append(line(xs+86, y, xs+120, y, color=INK, sw=2))
    p.extend(adc_input(xs+120, y))
    p.append(text(xs+196, y-40, "АЦП", size=11, color=MUTED, anchor="start"))

    # роздільник
    p.append(line(W/2, 60, W/2, 226, color="#dddddd", sw=1.2, dash="4 4"))

    # ── права половина: через буфер ──
    p.append(fitbox(380, 250, 300, 66,
                    "ЧЕРЕЗ БУФЕР: давач майже не навантажений,\nCз набирає з низькоомного виходу — швидко",
                    size=12, fill="#eafaf0", stroke=FIELD))
    xd = 390
    p.append(circle(xd, y, 16, fill=FILL, stroke=INK, sw=1.8))
    p.append(text(xd, y+5, "~", size=18, color=INK))
    p.append(text(xd, y-26, "давач", size=11, color=MUTED))
    p.append(line(xd+16, y, xd+44, y, color=INK, sw=2))
    tb = 22
    p.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f Z" fill="#eaf0fd" stroke="%s" stroke-width="1.8"/>'
             % (xd+44, y-tb, xd+44, y+tb, xd+44+42, y, NEG))
    p.append(text(xd+58, y+4, "×1", size=12, color=NEG, bold=True))
    p.append(text(xd+62, y+tb+16, "буфер", size=10.5, color=NEG))
    p.append(text(xd+66, y-tb-6, "польовий вхід", size=9.5, color=MUTED))
    p.append(line(xd+86, y, xd+120, y, color=INK, sw=2))
    p.append(text(xd+103, y-10, "низький Rвих", size=9.5, color=FIELD, anchor="middle"))
    p.extend(adc_input(xd+120, y))
    p.append(text(xd+196, y-40, "АЦП", size=11, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "buffer-vs-direct.svg"), W, H, *p)


if __name__ == "__main__":
    fig_circuit()
    fig_waveform()
    fig_hold_errors()
    fig_history()
    fig_acq_settling()
    fig_buffer_vs_direct()
    print("OK: sh-circuit, track-hold-waveform, hold-errors, sh-history, acq-settling, buffer-vs-direct")
