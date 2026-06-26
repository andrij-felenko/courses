# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CODE = FIELD   # зелений — пам'ять/шина коду
DATA = NEG     # синій  — пам'ять/шина даних
CPU  = POS     # червоний — ALU/процесор
WARM = "#caa24a"  # бурштин — акцент


# ── 1. accumulator: одно-операндна машина навколо регістра W ──────────────────
# Ідея: майже кожна дія тече через W — він і вхід, і вихід АЛП.
def fig_accumulator():
    W, H = 720, 360
    p = []
    p.append(text(W/2, 30, "Уся арифметика тече через єдиний регістр W", size=15, bold=True))

    # АЛП по центру
    ax, ay = 330, 165
    p.append(rect(ax, ay, 120, 90, fill="#fdecea", stroke=CPU, sw=2))
    p.append(text(ax+60, ay+38, "АЛП", size=15, color=CPU, bold=True))
    p.append(text(ax+60, ay+60, "(+ − & | …)", size=11, color=MUTED))

    # W ліворуч від АЛП
    wx, wy = 120, 185
    b, w, h = textbox(wx, wy, "W\nакумулятор", size=13, color=CPU, stroke=CPU,
                      fill="#fdecea", bold=True, min_w=120)
    p.append(b)

    # файловий регістр (пам'ять даних) праворуч
    fx, fy = 600, 185
    b, w, h = textbox(fx, fy, "файловий\nрегістр f\n(комірка RAM)", size=12, color=DATA,
                      stroke=DATA, fill="#eef2fb", bold=True, min_w=140)
    p.append(b)

    # W -> АЛП (перший операнд)
    p.append(arrow(wx+62, wy-8, ax+8, ay+30, color=CPU, sw=2.2))
    p.append(text(232, 150, "операнд 1", size=10.5, color=CPU, bold=True))
    # f -> АЛП (другий операнд)
    p.append(arrow(fx-72, fy-8, ax+112, ay+30, color=DATA, sw=2.2))
    p.append(text(520, 150, "операнд 2", size=10.5, color=DATA, bold=True))

    # АЛП -> результат: або назад у W, або у f (вибирає біт d)
    p.append(arrow(ax+8, ay+70, wx+62, wy+34, color=INK, sw=2.0))
    p.append(arrow(ax+112, ay+70, fx-72, fy+34, color=INK, sw=2.0))
    p.append(text(360, 300, "результат → W  (d=0)   або   → f  (d=1)", size=12, color=INK, bold=True))

    p.append(text(W/2, 340, "один біт у команді вирішує, куди лягає відповідь — у W чи назад у комірку",
                  size=11, color=MUTED, italic=True))
    return render(os.path.join(OUT, "accumulator.svg"), W, H, *p)


# ── 2. harvard-widths: дві пам'яті, СЛОВО КОДУ ШИРШЕ за байт даних ─────────────
# Ідея: Гарвард із різною шириною слова — команда несе й опкод, і константу.
def fig_harvard_widths():
    W, H = 740, 330
    p = []
    p.append(text(W/2, 30, "Гарвард: окремі пам'яті, і слово коду ширше за байт даних", size=14.5, bold=True))

    cx, cy = 360, 175
    b, w, h = textbox(cx, cy, "ядро PIC\n(W + АЛП)", size=13, color=CPU, stroke=CPU,
                      fill="#fdecea", bold=True, min_w=130)
    p.append(b)

    # пам'ять коду — широке слово (14 біт у мід-рейндж)
    p.append(rect(70, 120, 150, 56, fill="#eaf6ee", stroke=CODE, sw=2))
    p.append(text(145, 142, "пам'ять коду", size=12, color=CODE, bold=True))
    p.append(text(145, 162, "Flash, слово 14 біт", size=11, color=CODE))
    p.append(arrow(222, 148, cx-68, 165, color=CODE, sw=2.4))
    p.append(text(280, 138, "команди", size=10.5, color=CODE, bold=True))

    # пам'ять даних — байт
    p.append(rect(520, 120, 150, 56, fill="#eef2fb", stroke=DATA, sw=2))
    p.append(text(595, 142, "пам'ять даних", size=12, color=DATA, bold=True))
    p.append(text(595, 162, "RAM, комірка 8 біт", size=11, color=DATA))
    p.append(line(cx+68, 165, 520, 148, color=DATA, sw=2.4))
    p.append(arrow(520, 148, cx+70, 162, color=DATA, sw=2.4))
    p.append(text(450, 138, "дані ⇄", size=10.5, color=DATA, bold=True))

    # розклад одного 14-бітного слова: опкод + дані вмонтовані
    sx, sy, cellw = 165, 250, 28
    p.append(text(W/2, 232, "одне 14-бітне слово команди несе все одразу:", size=11.5, color=INK, bold=True))
    labels = ["опкод", "опкод", "опкод", "опкод", "опкод", "опкод",
              "f/d", "f", "f", "f", "f", "f", "f", "f"]
    cols = [CODE]*6 + [WARM] + [DATA]*7
    for i in range(14):
        x = sx + i*cellw
        p.append(rect(x, sy, cellw-2, 30, fill="#ffffff", stroke=cols[i], sw=1.4, rx=3))
        p.append(text(x+(cellw-2)/2, sy+20, str((14-1-i)%10), size=11, color=cols[i], bold=True))
    p.append(text(sx+3*cellw, sy+52, "опкод дії", size=10.5, color=CODE, bold=True, anchor="middle"))
    p.append(text(sx+10*cellw, sy+52, "адреса комірки в банку (вмонтована в команду)", size=10.5, color=DATA, bold=True, anchor="middle"))
    return render(os.path.join(OUT, "harvard-widths.svg"), W, H, *p)


# ── 3. banks: банкована пам'ять даних + непряма адресація через FSR/INDF ───────
# Ідея: адреса в команді коротка → пам'ять порізана на банки; FSR/INDF — обхід.
def fig_banks():
    W, H = 720, 430
    p = []
    p.append(text(W/2, 30, "Пряма адреса коротка → RAM порізана на банки", size=15, bold=True))

    # чотири банки стовпчиками
    bx0, by, bw, bh = 60, 64, 140, 230
    names = ["Банк 0", "Банк 1", "Банк 2", "Банк 3"]
    for i in range(4):
        x = bx0 + i*(bw+12)
        p.append(rect(x, by, bw, bh, fill="#eef2fb", stroke=DATA, sw=1.6))
        p.append(text(x+bw/2, by+22, names[i], size=12.5, color=DATA, bold=True))
        # верх — SFR, низ — GPR
        p.append(rect(x+8, by+34, bw-16, 52, fill="#fdecea", stroke=CPU, sw=1.2, rx=4))
        p.append(text(x+bw/2, by+57, "SFR", size=11, color=CPU, bold=True))
        p.append(text(x+bw/2, by+73, "керування", size=9.5, color=MUTED))
        p.append(rect(x+8, by+92, bw-16, bh-104, fill="#eaf6ee", stroke=CODE, sw=1.2, rx=4))
        p.append(text(x+bw/2, by+140, "GPR", size=11, color=CODE, bold=True))
        p.append(text(x+bw/2, by+158, "ваші змінні", size=9.5, color=MUTED))

    p.append(text(W/2, by+bh+28,
                  "пряма команда бачить лише ОДИН банк нараз — активний обирають біти RP1:RP0",
                  size=11.5, color=INK, bold=True, anchor="middle"))

    # FSR/INDF — наскрізний покажчик, рядком унизу
    fy = by + bh + 66
    b, w, h = textbox(150, fy, "FSR — покажчик\n(повна адреса)", size=12, color=WARM, stroke=WARM,
                      fill="#fbf6e8", bold=True, min_w=180)
    p.append(b)
    p.append(arrow(245, fy, 360, fy, color=WARM, sw=2.2))
    b, w, h = textbox(470, fy, "читаєш/пишеш INDF →\nлізе в будь-який банк", size=12, color=WARM,
                      stroke=WARM, fill="#fbf6e8", bold=True, min_w=210)
    p.append(b)
    p.append(text(W/2, fy+44, "обхід банків: адреса лежить у FSR, а не вмонтована в команду",
                  size=10.5, color=MUTED, italic=True, anchor="middle"))
    return render(os.path.join(OUT, "banks.svg"), W, H, *p)


# ── 4. family-ladder: три покоління ядра — ширшає слово, глибшає стек ──────────
def fig_family_ladder():
    W, H = 740, 365
    p = []
    p.append(text(W/2, 30, "Три покоління одного ядра: ширшає слово, глибшає стек", size=14.5, bold=True))

    cols = [
        ("Baseline", "PIC10/12", "слово 12 біт", "стек 2 рівні", "≈33 команди", CODE, 230),
        ("Mid-range", "PIC16", "слово 14 біт", "стек 8 рівнів", "≈35 команд", DATA, 180),
        ("PIC18",    "PIC18",  "слово 16 біт", "стек 31 рівень", "≈75 команд", CPU, 130),
    ]
    x0, bw, gap, baseY = 90, 170, 30, 275
    centers = []
    for i,(name, fam, word, stk, ins, col, top) in enumerate(cols):
        x = x0 + i*(bw+gap)
        centers.append(x+bw/2)
        h = baseY - top
        p.append(rect(x, top, bw, h, fill="#ffffff", stroke=col, sw=2))
        p.append(rect(x, top, bw, 30, fill=col, stroke=col, sw=2))
        p.append(text(x+bw/2, top+20, name, size=13, color="#ffffff", bold=True))
        yy = top+52
        for lineit in (fam, word, stk, ins):
            p.append(text(x+bw/2, yy, lineit, size=11.5, color=INK))
            yy += 22
        p.append(text(x+bw/2, baseY+22, "↑ глибше / ширше" if i>0 else "простіше / менше", size=10.5,
                      color=MUTED, italic=True))
    # стрілки прогресу між колонками
    p.append(arrow(x0+bw+4, baseY-10, x0+bw+gap-4, baseY-10, color=INK, sw=2))
    p.append(arrow(x0+2*bw+gap+4, baseY-10, x0+2*bw+2*gap-4, baseY-10, color=INK, sw=2))
    p.append(text(W/2, H-14, "та сама родина команд — старший код майже без змін піднімається вгору",
                  size=11, color=MUTED, italic=True))
    return render(os.path.join(OUT, "family-ladder.svg"), W, H, *p)


# ── 5. name-timeline: як розшифровка PIC мінялася і обросла варіантами ─────────
# Ідея (📜 hist): три усталені віхи на стрілці часу + окремий ярус «спірні
# варіанти», щоб читач БАЧИВ межу між усталеним і переказом.
def fig_name_timeline():
    W, H = 760, 360
    p = []
    p.append(text(W/2, 30, "«PIC»: назва, що міняла зміст і обросла варіантами", size=15, bold=True))

    # стрілка часу
    ax, ay, aw = 70, 150, 620
    p.append(arrow(ax, ay, ax+aw, ay, color=INK, sw=2))

    stops = [
        (0.10, "1976", "Peripheral\nInterface\nController", "контролер\nперифер. інтерфейсу", CODE, "#eaf6ee"),
        (0.45, "1977", "Programmable\nIntelligent\nComputer", "самостійний\nкомп'ютер", DATA, "#eef2fb"),
        (0.82, "нині", "PIC\n(торгова марка)", "вже не\nабревіатура", CPU, "#fdecea"),
    ]
    for frac, yr, full, note, col, fill in stops:
        x = ax + aw*frac
        p.append(circle(x, ay, 6, fill=col, stroke=col, sw=2))
        p.append(text(x, ay-58, yr, size=13, color=col, bold=True))
        b,_,_ = textbox(x, ay+44, full, size=11, color=col, stroke=col, fill=fill, bold=True, min_w=150)
        p.append(b)
        p.append(text(x, ay-30, note.replace("\n"," "), size=9.5, color=MUTED, italic=True))

    # ярус спірних варіантів
    sy = 290
    p.append(line(ax, sy-22, ax+aw, sy-22, color=MUTED, sw=1, dash="4,4"))
    p.append(text(ax, sy-6, "спірне (ходить у переказах, без твердого першоджерела):",
                  size=10.5, color=MUTED, italic=True, anchor="start"))
    p.append(text(ax+12, sy+16, "• Programmable Interface Controller        • Peripheral Interface Chip",
                  size=11, color=MUTED, anchor="start"))
    p.append(text(W/2, H-14, "кілька розшифровок = маркетингова назва, а не строгий термін",
                  size=11, color=MUTED, italic=True))
    return render(os.path.join(OUT, "name-timeline.svg"), W, H, *p)


# ── 6. two-fates: господар (CP1600) згасає, помічник (PIC) переростає його ─────
# Ідея (📜 hist): дві траєкторії в часі — спадна (CP1600) і висхідна (PIC),
# що перетинаються в середині 1980-х. Серце сюжету в одній картинці.
def fig_two_fates():
    W, H = 780, 380
    p = []
    p.append(text(W/2, 30, "Господар згасає, помічник переростає його", size=15, bold=True))

    # осі
    ox, oy, plotw, ploth = 90, 300, 600, 210
    p.append(arrow(ox, oy, ox, oy-ploth, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox+plotw, oy, color=INK, sw=1.6))
    p.append(text(ox-14, oy-ploth+6, "впливовість", size=10, color=INK, anchor="end"))
    # роки на осі
    for frac, yr in [(0.05,"1975"),(0.28,"1980"),(0.55,"1985"),(0.85,"1989")]:
        x = ox + plotw*frac
        p.append(line(x, oy, x, oy+5, color=INK, sw=1.4))
        p.append(text(x, oy+20, yr, size=10.5, color=MUTED))

    def pt(frac, h):  # h: частка висоти plot
        return ox + plotw*frac, oy - ploth*h

    # CP1600 — злет і спад (червоний)
    cp = [pt(0.05,0.20), pt(0.20,0.70), pt(0.33,0.85), pt(0.50,0.55), pt(0.60,0.18)]
    dpath = "M %.1f %.1f " % cp[0] + " ".join("L %.1f %.1f"%(x,y) for x,y in cp[1:])
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (dpath, CPU))
    p.append(circle(cp[-1][0], cp[-1][1], 5, fill=BG, stroke=CPU, sw=2.4))
    p.append(text(cp[2][0], cp[2][1]-14, "CP1600 — 16-біт «господар»", size=11.5, color=CPU, bold=True))
    p.append(text(cp[3][0]+6, cp[3][1]-6, "крах відеоігор 1983", size=9.5, color=MUTED, italic=True, anchor="start"))
    p.append(text(cp[-1][0]+8, cp[-1][1]+4, "≈1985: майже мертвий", size=9.5, color=CPU, anchor="start"))

    # PIC — народження й невпинне зростання (зелений)
    pi = [pt(0.10,0.06), pt(0.30,0.14), pt(0.50,0.30), pt(0.68,0.55), pt(0.85,0.88)]
    ppath = "M %.1f %.1f " % pi[0] + " ".join("L %.1f %.1f"%(x,y) for x,y in pi[1:])
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (ppath, CODE))
    p.append(circle(pi[0][0], pi[0][1], 5, fill=BG, stroke=CODE, sw=2.4))
    p.append(circle(pi[-1][0], pi[-1][1], 5, fill=CODE, stroke=CODE, sw=2.4))
    p.append(text(pi[0][0]+8, pi[0][1]-8, "1976: PIC народжується\nяк придаток", size=9.5, color=CODE, anchor="start"))
    p.append(text(pi[-1][0]-6, pi[-1][1]-12, "→ опора Microchip", size=11.5, color=CODE, bold=True, anchor="end"))

    p.append(text(W/2, H-12, "те, що задумали милицею для CP1600, пережило того, кому мало служити",
                  size=11, color=MUTED, italic=True))
    return render(os.path.join(OUT, "two-fates.svg"), W, H, *p)


# ── 7. grouping-payoff: розкидані змінні → BANKSEL перед кожним доступом;  ─────
#      угруповані в один банк → одне перемикання на всю функцію.
# Ідея (⚙️ proj): та сама логіка, інша розкладка пам'яті — інша довжина коду.
def fig_grouping_payoff():
    W, H = 760, 410
    p = []
    p.append(text(W/2, 28, "Та сама логіка, інша розкладка → інша довжина коду", size=15, bold=True))

    colW = 320
    lx = 40                 # ліва колонка — розкидано
    rx = W - 40 - colW      # права колонка — угруповано

    # заголовки колонок
    p.append(text(lx+colW/2, 58, "Розкидано по банках", size=13, color=CPU, bold=True))
    p.append(text(rx+colW/2, 58, "Угруповано в один банк", size=13, color=CODE, bold=True))

    # ── ліва колонка: три доступи, перед кожним BANKSEL ──
    rowh, y0 = 30, 78
    left_rows = [
        ("BANKSEL count_lo", CPU, True),
        ("incf  count_lo", INK, False),
        ("BANKSEL count_hi", CPU, True),
        ("incf  count_hi", INK, False),
        ("BANKSEL ovf_flag", CPU, True),
        ("movwf ovf_flag", INK, False),
    ]
    for i,(s,col,sw) in enumerate(left_rows):
        y = y0 + i*rowh
        fill = "#fdecea" if sw else "#ffffff"
        p.append(rect(lx, y, colW, rowh-6, fill=fill, stroke=col, sw=1.6 if sw else 1.1, rx=4))
        p.append(text(lx+12, y+rowh-15, s, size=12, color=col, bold=sw, anchor="start"))
    # підпис-лічильник перемикань
    p.append(text(lx+colW/2, y0+6*rowh+18, "3 перемикання банку", size=12.5, color=CPU, bold=True))

    # ── права колонка: одне BANKSEL, далі три доступи поспіль ──
    right_rows = [
        ("BANKSEL ctr", CODE, True),
        ("incf  ctr+0", INK, False),
        ("incf  ctr+1", INK, False),
        ("movwf ctr+2", INK, False),
    ]
    for i,(s,col,sw) in enumerate(right_rows):
        y = y0 + i*rowh
        fill = "#eaf6ee" if sw else "#ffffff"
        p.append(rect(rx, y, colW, rowh-6, fill=fill, stroke=col, sw=1.6 if sw else 1.1, rx=4))
        p.append(text(rx+12, y+rowh-15, s, size=12, color=col, bold=sw, anchor="start"))
    # дужка «той самий банк — без перемикань»
    by = y0 + rowh
    p.append(line(rx+colW+8, by+4, rx+colW+8, by+3*rowh-10, color=CODE, sw=2))
    p.append(text(rx+colW+14, by+1.5*rowh, "той самий банк:", size=10, color=CODE, anchor="start"))
    p.append(text(rx+colW+14, by+1.5*rowh+14, "BANKSEL зайвий →", size=10, color=CODE, anchor="start"))
    p.append(text(rx+colW+14, by+1.5*rowh+28, "компілятор прибрав", size=10, color=CODE, anchor="start"))
    p.append(text(rx+colW/2, y0+6*rowh+18, "1 перемикання банку", size=12.5, color=CODE, bold=True))

    p.append(text(W/2, H-16, "загорнув три змінні у struct — і два перемикання щезли самі",
                  size=11.5, color=MUTED, italic=True))
    return render(os.path.join(OUT, "grouping-payoff.svg"), W, H, *p)


if __name__ == "__main__":
    fig_accumulator()
    fig_harvard_widths()
    fig_banks()
    fig_family_ladder()
    fig_name_timeline()
    fig_two_fates()
    fig_grouping_payoff()
    print("ok")
