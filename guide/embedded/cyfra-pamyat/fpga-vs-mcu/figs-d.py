# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

MCU  = "#2457d6"   # мікроконтролер
FPGA = "#1f8a3b"   # FPGA
DSP  = "#8a5a1f"   # третій шлях (DSP/периферія)
WARM = "#c0392b"


# ── latency-budget: розклад НАЙГІРШОЇ затримки МК на доданки vs плаский бюджет FPGA ──
# Ідея (глибше за базову вісь-порядки): затримка МК — це СУМА кількох незалежних
# доданків, кожен зі своїм джерелом, і саме їх сума «плаває»; у FPGA бюджет —
# один короткий незмінний прохід. Показуємо стек доданків, а не одну смугу.

def fig_latency_budget():
    W = 760
    bx = 300                      # ліва межа стеків
    scale = 3.4                   # px на такт
    top = 92
    p = [text(W/2, 30, "З чого складається найгірша затримка", size=17, bold=True),
         text(W/2, 50, "МК: сума незалежних доданків, що «плаває» · FPGA: один сталий прохід",
              size=11.5, color=MUTED, italic=True)]

    # МК: стек доданків (у тактах ядра, зразок Cortex-M з нульовими wait-станами)
    mcu_parts = [
        ("вхід у обробник", 12, "#dfe6fb"),      # 12 тактів входу в ISR (ARM TRM)
        ("збереження контексту", 8, "#cdd8f8"),  # частина вже в 12, тут — додаткові дії
        ("витіснення вищим ISR", 40, "#b7c6f4"), # найбільший і найпримхливіший доданок
        ("позиція каналу в черзі", 24, "#a2b4f0"),
        ("сам обробник", 16, "#8ea3ec"),
    ]
    y = top
    p.append(text(bx-16, y-14, "МІКРОКОНТРОЛЕР (переривання)", size=11.5, color=MCU,
                  anchor="end", bold=True))
    xacc = bx
    total = 0
    for label, cyc, col in mcu_parts:
        w = cyc * scale
        p.append(rect(xacc, y, w, 34, fill=col, stroke=MCU, sw=1.3))
        if w > 46:
            p.append(text(xacc + w/2, y+21, str(cyc), size=10.5, color=MCU, bold=True))
        p.append(text(xacc + w/2, y+50, label, size=8.5, color=MUTED))
        xacc += w
        total += cyc
    p.append(text(xacc + 12, y+21, "= %d тактів" % total, size=11, color=WARM,
                  anchor="start", bold=True))
    # дужка «плаває»
    p.append(text(bx + 12*scale + 8*scale + 20*scale, y-6,
                  "три праві доданки залежать від того,", size=8.5, color=WARM, anchor="middle"))
    p.append(text(bx + 12*scale + 8*scale + 20*scale, y+66,
                  "чим ядро було зайняте -> джитер", size=8.5, color=WARM, anchor="middle"))

    # FPGA: один короткий блок
    y2 = top + 120
    p.append(text(bx-16, y2-14, "FPGA (пряма логіка)", size=11.5, color=FPGA,
                  anchor="end", bold=True))
    # ~2 такти: синхронізатор + логіка; у тому ж масштабі
    w = 2 * scale * 8  # трохи розтягнемо, щоб було видно (2 такти реально крихітні)
    p.append(rect(bx, y2, w, 34, fill="#e6f3ea", stroke=FPGA, sw=1.6))
    p.append(text(bx + w/2, y2+21, "1-2 такти", size=10, color=FPGA, bold=True))
    p.append(text(bx + w + 12, y2+21, "той самий для 1-го і 10-го каналу",
                  size=10, color=FPGA, anchor="start", bold=True))
    p.append(text(bx + w/2, y2+50, "синхронізатор + вентилі", size=8.5, color=MUTED))

    box = fitbox(40, y2+78, W-80, 56,
                 "Числа МК — у тактах ядра (зразок Cortex-M, нульові wait-стани). "
                 "Плаває не «трохи», а на десятки тактів — і саме це вбиває жорсткий таймінг.",
                 size=11, pad=10, fill="#f4f6f8", stroke=INK, sw=1.4, bold=False)
    p.append(box)
    render(os.path.join(OUT, "latency-budget.svg"), W, y2+150, *p)


# ── throughput-plane: пропускна = (операцій за такт) × (частота такту) ─────────
# Ідея: два незалежні важелі. Одне ядро жене частоту вгору, але лишається на
# «1 смузі»; FPGA бере паралелізм (багато смуг) на скромній частоті; жорстка
# периферія/DSP — вузька, але дуже швидка спеціалізована смуга. Показуємо як
# площину «смуги × частота» з ізолініями сталої пропускної.

def fig_throughput_plane():
    W, H = 760, 470
    ax, ay = 90, 380              # початок осей
    aw, ah = 600, 300
    p = [text(W/2, 30, "Пропускна = (операцій за такт) × (частота такту)", size=17, bold=True),
         text(W/2, 50, "два незалежні важелі — тому «швидший такт» і «більше смуг» не одне й те саме",
              size=11.5, color=MUTED, italic=True)]

    # осі
    p.append(arrow(ax, ay, ax, ay-ah, color=INK, sw=1.6))
    p.append(arrow(ax, ay, ax+aw, ay, color=INK, sw=1.6))
    p.append(text(ax-10, ay-ah+4, "паралельних", size=10.5, color=INK, anchor="end"))
    p.append(text(ax-10, ay-ah+18, "смуг", size=10.5, color=INK, anchor="end"))
    p.append(text(ax+aw, ay+20, "частота такту ->", size=10.5, color=INK, anchor="end"))

    # ізолінія сталої пропускної (смуги × частота = const): гіпербола
    import math
    for c, lbl in [(0.20, ""), (0.5, "стала пропускна")]:
        pts = []
        for i in range(1, 60):
            fx = 0.08 + i/60.0*0.9      # нормована частота
            fy = c/fx
            if fy > 1.0 or fy < 0.03: continue
            pts.append((ax + fx*aw, ay - fy*ah))
        if len(pts) > 1:
            d = "M " + " L ".join("%.1f %.1f" % pt for pt in pts)
            p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.2" '
                     'stroke-dasharray="4 3"/>' % (d, MUTED))
        if lbl and pts:
            mx, my = pts[len(pts)//2]
            p.append(text(mx+8, my-6, lbl, size=9.5, color=MUTED, italic=True, anchor="start"))

    # точки-представники (нормовані частота, смуги)
    def marker(fx, fy, col, name, sub):
        cxp, cyp = ax + fx*aw, ay - fy*ah
        out = circle(cxp, cyp, 7, fill=col, stroke="#ffffff", sw=1.5)
        out += text(cxp, cyp-14, name, size=11, color=col, bold=True)
        out += text(cxp, cyp+22, sub, size=8.5, color=MUTED)
        return out

    p.append(marker(0.86, 0.06, MCU, "МК: одне ядро",
                    "1 смуга, висока частота"))
    p.append(marker(0.34, 0.82, FPGA, "FPGA",
                    "багато смуг, скромна частота"))
    p.append(marker(0.72, 0.20, DSP, "DSP / жорстка периферія",
                    "кілька спец-смуг, швидко"))

    # підказка про Амдала внизу
    box = fitbox(40, ay+40, W-80, 56,
                 "Одне ядро тисне лише правий важіль (частоту) — і впирається в стелю Амдала: "
                 "послідовну частину роботи не розігнати додаванням смуг.",
                 size=11, pad=10, fill="#f4f6f8", stroke=INK, sw=1.4)
    p.append(box)
    render(os.path.join(OUT, "throughput-plane.svg"), W, ay+112, *p)


# ── breakeven: собівартість партії = NRE + одиниця×кількість -> точка перетину ─
# Ідея: рішення часто не технічне, а економічне. Дешевша одиниця (МК) виграє на
# великих тиражах; але висока NRE (розробка FPGA) розкладається й окуповується
# лише за певним обсягом. Малюємо дві прямі й точку беззбитковості.

def fig_breakeven():
    W, H = 760, 430
    ax, ay = 92, 350
    aw, ah = 590, 280
    p = [text(W/2, 30, "Коли вища ціна розробки окуповується", size=17, bold=True),
         text(W/2, 50, "собівартість партії = разова розробка (NRE) + ціна_за_шт × кількість",
              size=11.5, color=MUTED, italic=True)]

    p.append(arrow(ax, ay, ax, ay-ah, color=INK, sw=1.6))
    p.append(arrow(ax, ay, ax+aw, ay, color=INK, sw=1.6))
    p.append(text(ax-10, ay-ah+6, "сумарна", size=10.5, color=INK, anchor="end"))
    p.append(text(ax-10, ay-ah+20, "вартість", size=10.5, color=INK, anchor="end"))
    p.append(text(ax+aw, ay+20, "тираж, шт ->", size=10.5, color=INK, anchor="end"))

    # Модель (умовні числа для наочності):
    # Варіант A (МК): низька NRE, вища ціна за шт.
    # Варіант B (спец-рішення на дорожчому чипі): вища NRE, нижча ціна за шт великих обсягів.
    # Малюємо в нормованих координатах; точка перетину ~ посередині.
    A0, Aslope = 0.06, 0.72       # МК: старт низько, крутіше росте (дорожча одиниця)
    B0, Bslope = 0.42, 0.34       # інше рішення: старт високо (NRE), пологіше (дешевша одиниця)

    def linepts(y0, slope):
        x1, y1 = 0.0, y0
        x2, y2 = 1.0, min(1.0, y0 + slope)
        return (ax + x1*aw, ay - y1*ah, ax + x2*aw, ay - y2*ah)

    xa1,ya1,xa2,ya2 = linepts(A0, Aslope)
    xb1,yb1,xb2,yb2 = linepts(B0, Bslope)
    p.append(line(xa1,ya1,xa2,ya2, color=MCU, sw=2.4))
    p.append(line(xb1,yb1,xb2,yb2, color=FPGA, sw=2.4))
    p.append(text(xa2-6, ya2-8, "рішення A: дешева розробка,", size=10, color=MCU, anchor="end", bold=True))
    p.append(text(xa2-6, ya2+6, "дорожча одиниця (напр. МК+обв'язка)", size=9, color=MCU, anchor="end"))
    p.append(text(xb2-6, yb2-8, "рішення B: дорога розробка (NRE),", size=10, color=FPGA, anchor="end", bold=True))
    p.append(text(xb2-6, yb2+6, "дешевша одиниця на обсязі", size=9, color=FPGA, anchor="end"))

    # точка перетину: A0 + Aslope x = B0 + Bslope x
    xc = (B0 - A0) / (Aslope - Bslope)
    yc = A0 + Aslope*xc
    pxc, pyc = ax + xc*aw, ay - yc*ah
    p.append(line(pxc, ay, pxc, pyc, color=MUTED, sw=1.2, dash="3 3"))
    p.append(circle(pxc, pyc, 6, fill=WARM, stroke="#ffffff", sw=1.5))
    p.append(text(pxc, pyc-14, "точка беззбитковості", size=10.5, color=WARM, bold=True))
    p.append(text(pxc, ay+20, "цей тираж", size=9.5, color=WARM))
    # зони
    p.append(text(ax + xc*aw*0.5, ay-ah*0.12, "тут дешевше A", size=10, color=MCU, italic=True))
    p.append(text(ax + xc*aw + (aw-xc*aw)*0.5, ay-ah*0.12, "тут дешевше B", size=10, color=FPGA, italic=True))

    box = fitbox(40, ay+44, W-80, 52,
                 "Точка перетину = NRE_різниця / (ціна_за_шт_різниця). Малий тираж — розробку не "
                 "розкласти, виграє простіше рішення; великий — виграє дешевша одиниця.",
                 size=11, pad=10, fill="#f4f6f8", stroke=INK, sw=1.4)
    p.append(box)
    render(os.path.join(OUT, "breakeven.svg"), W, ay+116, *p)


# ── energy-op: енергія на пристрій, що «прокинувся-зробив-заснув» ──────────────
# Ідея (глибше за базову тезу про сон): повна енергія = активна×час + спокій×(1−час).
# У FPGA великий струм спокою тканини; у МК — мікроампери. За малого коефіцієнта
# активності (duty) МК різко ощадливіший; лінії перетинаються лише під важким
# постійним навантаженням. Малюємо дві криві повної потужності vs частка активності.

def fig_energy_op():
    W, H = 760, 430
    ax, ay = 96, 350
    aw, ah = 580, 280
    p = [text(W/2, 30, "Середня потужність = активна × частка + спокій × решта", size=16.5, bold=True),
         text(W/2, 50, "чому на батарейці зазвичай виграє МК, а FPGA — лише під постійним навантаженням",
              size=11.5, color=MUTED, italic=True)]

    p.append(arrow(ax, ay, ax, ay-ah, color=INK, sw=1.6))
    p.append(arrow(ax, ay, ax+aw, ay, color=INK, sw=1.6))
    p.append(text(ax-10, ay-ah+6, "середня", size=10.5, color=INK, anchor="end"))
    p.append(text(ax-10, ay-ah+20, "потужність", size=10.5, color=INK, anchor="end"))
    p.append(text(ax+aw, ay+20, "частка активного часу (duty) ->", size=10.5, color=INK, anchor="end"))

    # Нормовані моделі: P(d) = Pstatic + (Pactive - Pstatic) * d
    # МК: крихітний спокій, помірна активна.  FPGA: великий спокій, ефективна активна.
    def curve(Pstat, Pact, col, name, sub, ny):
        pts = []
        for i in range(0, 61):
            d = i/60.0
            P = Pstat + (Pact - Pstat)*d
            pts.append((ax + d*aw, ay - min(1.0, P)*ah))
        dpth = "M " + " L ".join("%.1f %.1f" % pt for pt in pts)
        out = '<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (dpth, col)
        out += text(ax+aw-6, ny, name, size=11, color=col, anchor="end", bold=True)
        out += text(ax+aw-6, ny+14, sub, size=9, color=MUTED, anchor="end")
        return out, pts

    mcu_c, mcu_pts   = curve(0.02, 0.55, MCU, "МК", "спокій ~мкА, активна помірна", ay-ah+40)
    fpga_c, fpga_pts = curve(0.40, 0.78, FPGA, "FPGA", "спокій на тканину великий", ay-ah+80)
    p.append(mcu_c); p.append(fpga_c)

    # точка перетину кривих (лінійні): розв'яжемо
    # 0.02 + 0.53 d = 0.40 + 0.38 d  -> 0.15 d = 0.38 -> d = 2.53 (поза [0,1]) =>
    # у цій моделі МК нижчий на всьому [0,1] окрім дуже високих d; познач це чесно.
    p.append(text(ax + aw*0.16, ay - (0.02+0.53*0.16)*ah - 16,
                  "малий duty:", size=9.5, color=MCU, italic=True))
    p.append(text(ax + aw*0.16, ay - (0.02+0.53*0.16)*ah - 4,
                  "МК різко нижче", size=9.5, color=MCU, italic=True))
    p.append(text(ax + aw*0.82, ay - (0.40+0.38*0.82)*ah - 30,
                  "постійне важке навантаження:", size=9.5, color=FPGA, italic=True, anchor="middle"))
    p.append(text(ax + aw*0.82, ay - (0.40+0.38*0.82)*ah - 18,
                  "на ват логіки FPGA ефективна", size=9.5, color=FPGA, italic=True, anchor="middle"))

    box = fitbox(40, ay+44, W-80, 52,
                 "Крива FPGA стартує високо через струм спокою тканини; крива МК майже від нуля. "
                 "Для «прокинувся-зробив-заснув» (малий duty) МК виграє з великим запасом.",
                 size=11, pad=10, fill="#f4f6f8", stroke=INK, sw=1.4)
    p.append(box)
    render(os.path.join(OUT, "energy-op.svg"), W, ay+116, *p)


if __name__ == "__main__":
    fig_latency_budget()
    fig_throughput_plane()
    fig_breakeven()
    fig_energy_op()
    print("figs-d done")
