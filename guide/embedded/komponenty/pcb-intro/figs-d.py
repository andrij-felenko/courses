# -*- coding: utf-8 -*-
# Фігури для ДЕТАЛЬНОЇ статті pcb-intro-d.md.
# Ідуть ГЛИБШЕ за базові (anatomy / copper-pattern / via-types):
#   1) trace-xsection  — трапеція доріжки (etch factor, підтрав) + геометрія міді
#   2) trace-current   — крива IPC-2221 «струм проти ширини» для 1 oz зовні/всередині
#   3) via-barrel      — стінка отвору як циліндр: опір, індуктивність, aspect ratio
#   4) return-path     — сигнал і його ЗВОРОТНИЙ струм під ним; що робить розрив землі
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

COPPER = "#b87333"
COPDK  = "#8a561f"
CORE   = "#d8c98a"
CORE_E = "#b8a55f"
MASK   = "#1f7a4d"
MASKDK = "#155c3a"
SILK   = "#f4f6f8"
BG_    = "#ffffff"
CURR   = "#c0392b"   # струм (гарячий)
RET    = "#2457d6"   # зворотний струм (холодний)
HEAT   = "#e67e22"   # тепло


# ── 1. trace-xsection: реальний профіль доріжки — трапеція від підтраву ──────
# Ідея: доріжка НЕ прямокутник. Травник гризе мідь і вбік під маскою-резистом,
# тож переріз — трапеція: вужча зверху, ширша знизу. Показуємо «ідеал проти
# реальності», підтрав, кут стінки й де рахується ширина.
def fig_trace_xsection():
    W, H = 780, 430
    p = []
    p.append(text(W/2, 30, "Переріз доріжки: травлення робить не прямокутник, а трапецію", size=15, bold=True))

    # спільна база (ізолятор) під обома варіантами
    base_y = 300
    p.append(rect(60, base_y, 660, 70, fill=CORE, stroke=CORE_E, sw=1.4, rx=3))
    p.append(text(390, base_y + 44, "ізолятор (ламінат)", size=11, color="#8a7a2f"))

    # ---- ЛІВОРУЧ: ідеал (прямокутник) ----
    lx = 150
    p.append(text(lx, 78, "ідеал у програмі", size=12, bold=True, color=MUTED))
    tw = 120
    th = 46
    p.append(rect(lx - tw/2, base_y - th, tw, th, fill=COPPER, stroke=COPDK, sw=1.4, rx=1))
    # розмірна ширина зверху = знизу
    p.append(line(lx - tw/2, base_y - th - 14, lx + tw/2, base_y - th - 14, color=MUTED, sw=1.0))
    p.append(text(lx, base_y - th - 20, "w", size=12, color=MUTED, italic=True))
    b, _, _ = textbox(lx, 130, "переріз = w × t\nрівні стінки", size=10.5, color=INK,
                      fill="#ffffff", stroke=MUTED, sw=1.0, pad=6)
    p.append(b)

    # ---- ПРАВОРУЧ: реальність (трапеція) ----
    rx = 560
    p.append(text(rx, 78, "реально після травлення", size=12, bold=True, color=COPDK))
    wb = 130            # ширина знизу (біля основи)
    wt = 84             # ширина зверху (підтравлена)
    th2 = 46
    # трапеція: широка внизу, вужча вгорі
    x_bl, x_br = rx - wb/2, rx + wb/2
    x_tl, x_tr = rx - wt/2, rx + wt/2
    p.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.6"/>'
             % (x_bl, base_y, x_br, base_y, x_tr, base_y - th2, x_tl, base_y - th2, COPPER, COPDK))
    # маска-резист поверх (визначала ширину ЗВЕРХУ)
    p.append(rect(x_tl - 2, base_y - th2 - 8, wt + 4, 8, fill=MASK, stroke=MASKDK, sw=1.0, rx=1))
    # ширина зверху
    p.append(line(x_tl, base_y - th2 - 22, x_tr, base_y - th2 - 22, color=COPDK, sw=1.0))
    p.append(text(rx, base_y - th2 - 28, "w_top (менша)", size=10, color=COPDK, italic=True))
    # ширина знизу
    p.append(line(x_bl, base_y + 16, x_br, base_y + 16, color=COPDK, sw=1.0))
    p.append(text(rx, base_y + 30, "w_bot (як у файлі)", size=10, color=COPDK, italic=True))
    # підтрав — маленькі стрілки, що показують «з'їдено вбік» під резистом
    p.append(line(x_tl - 20, base_y - th2 + 8, x_tl - 2, base_y - th2 + 8, color=CURR, sw=1.4))
    p.append(text(x_tl - 40, base_y - th2 + 12, "підтрав", size=9.5, color=CURR))
    # кут стінки d — по горизонталі від низу до верху
    p.append(line(x_br, base_y, x_tr, base_y - th2, color="#333", sw=0.8, dash="3 3"))
    p.append(text(x_br + 26, base_y - th2/2, "стінка", size=9.5, color=MUTED))

    # підпис про etch factor унизу праворуч
    b, _, _ = textbox(rx, 150, "етч-фактор = t / підтрав\nтипово ≈ 3…4", size=10.5, color=INK,
                      fill="#ffffff", stroke=COPPER, sw=1.1, pad=6)
    p.append(b)

    # спільний виновід унизу
    p.append(text(W/2, H - 14,
                  "справжня мідь трохи вужча, ніж намальовано — це закладають у правила ширини для точних місць",
                  size=10.5, color=MUTED))
    render(os.path.join(OUT, "trace-xsection.svg"), W, H, *p)


# ── 2. trace-current: крива IPC-2221 — струм проти ширини для 1 oz ───────────
# Ідея: показати НЕЛІНІЙНІСТЬ. Струм росте не пропорційно ширині, а як ширина
# у степені ~0.725; внутрішні доріжки тримають удвічі менше за зовнішні.
# Малюємо дві криві (зовні / всередині) для ΔT=10°C, 1 oz.
def fig_trace_current():
    import math
    W, H = 760, 440
    p = []
    p.append(text(W/2, 30, "Скільки струму тримає доріжка 1 oz (ΔT = 10 °C): ширина проти струму", size=14.5, bold=True))

    # осі
    ox, oy = 90, 360          # початок осей (лівий низ)
    ax_w, ax_h = 600, 280
    p.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.6))          # X
    p.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.6))          # Y
    p.append(text(ox + ax_w/2, oy + 42, "ширина доріжки, мм", size=11.5, color=INK))
    p.append('<text x="%d" y="%d" font-family="%s" font-size="11.5" fill="%s" text-anchor="middle" transform="rotate(-90 %d %d)">струм, А</text>'
             % (30, oy - ax_h/2, FONT, INK, 30, oy - ax_h/2))

    # діапазони: ширина 0..3 мм, струм 0..6 А
    wmax, imax = 3.0, 6.0
    def X(wmm): return ox + wmm / wmax * ax_w
    def Y(i):   return oy - i / imax * ax_h

    # сітка: лише короткі поділки на осях (без наскрізних ліній, щоб не різати написи)
    for wv in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
        p.append(line(X(wv), oy, X(wv), oy - 6, color=MUTED, sw=1.0))     # тик на осі X
        p.append(text(X(wv), oy + 18, ("%g" % wv), size=10, color=MUTED))
    for iv in [1, 2, 3, 4, 5, 6]:
        p.append(line(ox, Y(iv), ox + 6, Y(iv), color=MUTED, sw=1.0))     # тик на осі Y
        p.append(text(ox - 14, Y(iv) + 4, str(iv), size=10, color=MUTED))

    # IPC-2221: I = k · dT^0.44 · A^0.725 ; A[mil^2], 1 oz = 1.378 mil товщина
    # ширина[мм] → ширина[mil] = w/0.0254 ; A = w_mil · 1.378
    dT = 10.0
    t_mil = 1.378
    def current(wmm, k):
        w_mil = wmm / 0.0254
        A = w_mil * t_mil
        return k * (dT ** 0.44) * (A ** 0.725)

    def curve(k, col):
        pts = []
        wv = 0.05
        while wv <= wmax + 1e-9:
            pts.append((X(wv), Y(min(current(wv, k), imax))))
            wv += 0.05
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % pt for pt in pts[1:])
        return '<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, col)

    p.append(curve(0.048, CURR))    # зовнішня
    p.append(curve(0.024, RET))     # внутрішня

    # позначки кривих — у чистих проміжках між лініями сітки (щоб лінія не різала напис)
    b, _, _ = textbox(X(2.05), 104, "зовнішня (k=0.048)", size=10.5,
                      color=CURR, fill="#ffffff", stroke=CURR, sw=1.1, pad=5)
    p.append(b)
    b, _, _ = textbox(X(2.5), 292, "внутрішня (k=0.024)", size=10.5,
                      color=RET, fill="#ffffff", stroke=RET, sw=1.1, pad=5)
    p.append(b)

    # маркер: подвоїли ширину 0.5→1.0 — струм зріс лише в ~1.65 раза (не 2×)
    i05 = current(0.5, 0.048); i10 = current(1.0, 0.048)
    p.append(circle(X(0.5), Y(i05), 4, fill=CURR, stroke="#fff", sw=1.2))
    p.append(circle(X(1.0), Y(i10), 4, fill=CURR, stroke="#fff", sw=1.2))
    # виновід від пари точок до пояснення (у чистому проміжку сітки, праворуч-вгору)
    b, _, _ = textbox(X(1.62), 196, "×2 ширини → лише ×1.65 струму\n(крива, не пряма)",
                      size=10, color=INK, fill="#fffef8", stroke=HEAT, sw=1.1, pad=5)
    p.append(b)

    p.append(text(W/2, H - 12,
                  "внутрішня доріжка тримає ≈ удвічі менший струм за ту саму ширину — немає обдування повітрям",
                  size=10.5, color=MUTED))
    render(os.path.join(OUT, "trace-current.svg"), W, H, *p)


# ── 3. via-barrel: отвір як циліндр — опір, індуктивність, aspect ratio ──────
# Ідея: заглибитися у via. Струм тече ТОНКОЮ стінкою (циліндром), не суцільним
# металом; що глибша й вужча дірка, то важче її рівно покрити (aspect ratio).
def fig_via_barrel():
    W, H = 780, 430
    p = []
    p.append(text(W/2, 30, "Перехідний отвір зблизька: тонка стінка, опір, глибина проти діаметра", size=14.5, bold=True))

    # ---------- ЛІВОРУЧ: розріз стінки з розмірами ----------
    lx0, lx1 = 60, 340
    lcx = (lx0 + lx1) / 2
    ytop, ybot = 96, 300
    p.append(text(lcx, 72, "стінка = мідний циліндр", size=12, bold=True, color=INK))
    # тіло плати
    p.append(rect(lx0, ytop, lx1 - lx0, ybot - ytop, fill=CORE, stroke=CORE_E, sw=1.4, rx=3))
    # мідь верх/низ
    p.append(rect(lx0, ytop - 10, lx1 - lx0, 10, fill=COPPER, stroke=COPDK, sw=1.0, rx=1))
    p.append(rect(lx0, ybot, lx1 - lx0, 10, fill=COPPER, stroke=COPDK, sw=1.0, rx=1))
    # отвір
    hw = 46
    holeL, holeR = lcx - hw/2, lcx + hw/2
    wall = 7
    p.append(rect(holeL, ytop - 10, wall, (ybot + 10) - (ytop - 10), fill=COPPER, stroke=COPDK, sw=1.0))
    p.append(rect(holeR - wall, ytop - 10, wall, (ybot + 10) - (ytop - 10), fill=COPPER, stroke=COPDK, sw=1.0))
    p.append(rect(holeL + wall, ytop - 10, hw - 2*wall, (ybot + 10) - (ytop - 10), fill=BG_, stroke="none", sw=0))
    # майданчики
    p.append(rect(lcx - hw/2 - 16, ytop - 10, hw + 32, 10, fill=COPPER, stroke=COPDK, sw=1.0))
    p.append(rect(lcx - hw/2 - 16, ybot, hw + 32, 10, fill=COPPER, stroke=COPDK, sw=1.0))

    # розмір: діаметр d
    p.append(line(holeL, ytop - 26, holeR, ytop - 26, color=INK, sw=1.0))
    p.append(text(lcx, ytop - 32, "d — діаметр отвору", size=10, color=INK, italic=True))
    # розмір: глибина h (= товщина плати)
    p.append(line(lx1 + 14, ytop - 10, lx1 + 14, ybot + 10, color=INK, sw=1.0))
    p.append('<text x="%d" y="%d" font-family="%s" font-size="10" fill="%s" text-anchor="middle" font-style="italic" transform="rotate(-90 %d %d)">h — глибина (товщина плати)</text>'
             % (lx1 + 30, (ytop+ybot)/2, FONT, INK, lx1 + 30, (ytop+ybot)/2))
    # стінка t — виновід на лівий стовпчик
    p.append(line(holeL + wall/2, ytop + 60, lx0 + 30, ytop + 60, color=CURR, sw=1.2))
    b, _, _ = textbox(lx0 - 2, ytop + 60, "стінка t\n≈ 20…25 мкм", size=9.5, color=CURR,
                      fill="#ffffff", stroke=COPPER, sw=1.0, pad=5)
    p.append(b)
    # струм тече стінкою
    p.append(text(lcx, ybot + 44, "струм тече лише стінкою —", size=10, color=CURR))
    p.append(text(lcx, ybot + 60, "не суцільним металом", size=10, color=CURR, bold=True))

    # роздільник
    p.append(line(W/2, 60, W/2, H - 20, color="#d0d4d8", sw=1.4, dash="6 5"))

    # ---------- ПРАВОРУЧ: aspect ratio — легко проти важко ----------
    rx0 = 420
    p.append(text(600, 72, "співвідношення h : d (aspect ratio)", size=12, bold=True, color=INK))

    def barrel_demo(cx, plate_h, d, label, ok):
        frag = []
        yt = 110
        yb = yt + plate_h
        w_plate = 150
        frag.append(rect(cx - w_plate/2, yt, w_plate, plate_h, fill=CORE, stroke=CORE_E, sw=1.3, rx=3))
        # отвір по центру
        frag.append(rect(cx - d/2, yt, d, plate_h, fill=BG_, stroke=COPDK, sw=1.0))
        # покриття стінки: рівне (ok) чи тонше в центрі (not ok)
        wallc = 6 if ok else 6
        # верх стінки завжди товстий; для not-ok у центрі тонший
        n = 14
        for i in range(n):
            yy = yt + (i + 0.5) * plate_h / n
            if ok:
                tw = wallc
            else:
                # тонше посередині
                mid = abs((i + 0.5)/n - 0.5) * 2   # 0 у центрі, 1 скраю
                tw = 2.2 + (wallc - 2.2) * mid
            frag.append(rect(cx - d/2, yy - plate_h/n/2, tw, plate_h/n, fill=COPPER, stroke="none", sw=0))
            frag.append(rect(cx + d/2 - tw, yy - plate_h/n/2, tw, plate_h/n, fill=COPPER, stroke="none", sw=0))
        col = FIELD if ok else CURR
        frag.append(text(cx, yb + 22, label, size=10.5, color=col, bold=True))
        return frag

    # низький aspect (легко, рівна стінка)
    for f in barrel_demo(500, 90, 40, "низьке h:d — рівно", True): p.append(f)
    # високий aspect (важко, тонко в центрі)
    for f in barrel_demo(690, 170, 20, "високе h:d — тонко в центрі", False): p.append(f)

    b, _, _ = textbox(600, 340, "правило цеху: h : d не більше ≈ 8…10 : 1\nглибше — стінку рівно не покрити",
                      size=10, color=INK, fill="#fffef8", stroke=HEAT, sw=1.1, pad=6)
    p.append(b)

    render(os.path.join(OUT, "via-barrel.svg"), W, H, *p)


# ── 4. return-path: зворотний струм тече ПІД доріжкою; розрив землі шкодить ──
# Ідея — кульмінація «мідь теж деталь»: струм завжди тече ПЕТЛЕЮ. На швидкій
# цифрі зворотний струм по землі йде РІВНО під сигналом (найменша петля).
# Розрив у площині землі змушує його робити гак — петля роздувається.
def fig_return_path():
    W, H = 780, 430
    p = []
    p.append(text(W/2, 30, "Зворотний струм: він тече петлею, і на швидкій цифрі — рівно під сигналом", size=14.5, bold=True))

    # два «сендвічі» поруч: цілісна земля VS розрізана
    def board(cx, split):
        frag = []
        top_y = 96          # сигнальна доріжка (вид збоку)
        gnd_y = 200         # площина землі
        w = 300
        x0, x1 = cx - w/2, cx + w/2
        # ізолятор між шарами
        frag.append(rect(x0, top_y, w, gnd_y - top_y, fill=CORE, stroke=CORE_E, sw=1.1, rx=2))
        # сигнальна доріжка згори
        frag.append(rect(x0, top_y - 8, w, 8, fill=COPPER, stroke=COPDK, sw=1.0, rx=1))
        # площина землі знизу (суцільна або з розривом)
        if not split:
            frag.append(rect(x0, gnd_y, w, 10, fill=COPPER, stroke=COPDK, sw=1.0, rx=1))
        else:
            gap = 30
            frag.append(rect(x0, gnd_y, w/2 - gap/2, 10, fill=COPPER, stroke=COPDK, sw=1.0, rx=1))
            frag.append(rect(cx + gap/2, gnd_y, w/2 - gap/2, 10, fill=COPPER, stroke=COPDK, sw=1.0, rx=1))
            # позначка розриву
            frag.append(text(cx, gnd_y + 30, "розрив землі", size=10, color=CURR, bold=True))

        # прямий струм сигналу (зверху, зліва направо) — червона стрілка
        frag.append(arrow(x0 + 20, top_y - 4, x1 - 20, top_y - 4, color=CURR, sw=2.0))
        frag.append(text(cx, top_y - 16, "сигнал →", size=10, color=CURR, bold=True))

        # зворотний струм по землі (справа наліво)
        if not split:
            # тече РІВНО під доріжкою — маленька петля
            frag.append(arrow(x1 - 20, gnd_y + 5, x0 + 20, gnd_y + 5, color=RET, sw=2.0))
            frag.append(text(cx, gnd_y + 26, "зворотний струм — рівно під сигналом (мала петля)",
                             size=9.5, color=RET))
        else:
            # мусить обійти розрив — гак униз і вбік (велика петля)
            yb = gnd_y + 40
            frag.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" stroke-width="2.0" marker-end="url(#arrow)"/>'
                        % (x1 - 20, gnd_y + 5, cx + 40, yb, cx - 40, yb, x0 + 20, gnd_y + 5, RET))
            frag.append(text(cx, yb + 18, "мусить обійти → петля роздулася", size=9.5, color=RET, bold=True))
        return frag

    for f in board(215, False): p.append(f)
    for f in board(565, True):  p.append(f)
    p.append(text(215, 74, "суцільна земля", size=12, bold=True, color=FIELD))
    p.append(text(565, 74, "земля з розривом", size=12, bold=True, color=CURR))

    # роздільник
    p.append(line(W/2, 60, W/2, 330, color="#d0d4d8", sw=1.4, dash="6 5"))

    p.append(text(W/2, H - 30,
                  "мала петля — мало випромінює й ловить; роздута петля — джерело завад і антена.",
                  size=11, color=INK))
    p.append(text(W/2, H - 12,
                  "тому суцільний шар землі під сигналом — не розкіш, а керування зворотним струмом",
                  size=10.5, color=MUTED))
    render(os.path.join(OUT, "return-path.svg"), W, H, *p)


if __name__ == "__main__":
    fig_trace_xsection()
    fig_trace_current()
    fig_via_barrel()
    fig_return_path()
    print("figs-d done:", [f for f in os.listdir(OUT) if f.endswith('.svg')])
