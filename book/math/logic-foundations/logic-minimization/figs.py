# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREEN_FILL = "#eafaf0"
RED_FILL   = "#fdecea"
GREY_FILL  = "#eef1f5"
HL_FILL    = "#fdf6e3"   # підсвітка «єдиного» стовпця


def cell(x, y, s, w, h, fill=BG, stroke=INK, sw=1.4, size=15, color=INK, bold=True):
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=0)
    if s != "":
        out += text(x + w / 2, y + h / 2 + size * 0.35, s, size=size, color=color, bold=bold)
    return out


# ── Фіг. 1: карта з трьома простими імплікантами (простий · істотний · зайвий) ──
# Функція F(A,B,C,D)=Σm(0,1,4,5,6,7,8,9). Три прості імпліканти:
#   Ā·B  — увесь рядок AB=01 (істотний: лише він накриває 6,7)
#   B̄·C̄ — {0,1,8,9}, обгортка верх↔низ (істотний: лише він накриває 8,9)
#   Ā·C̄ — 2×2 зліва вгорі {0,1,4,5}: простий, але лежить під двома іншими → зайвий
def fig_implicants():
    W, H = 520, 470
    cw = 62
    ox, oy = 150, 70
    colsCD = ["00", "01", "11", "10"]
    rowsAB = ["00", "01", "11", "10"]
    ones = {0, 1, 4, 5, 6, 7, 8, 9}
    p = []

    # заголовки осей
    p.append(text(ox + cw * 2, oy - 34, "CD", size=13, color=MUTED, bold=True))
    for j, c in enumerate(colsCD):
        p.append(text(ox + cw * (j + 0.5), oy - 14, c, size=12, color=NEG, bold=True))
    p.append(text(ox - 30, oy + cw * 2 - 6, "AB", size=13, color=MUTED, bold=True))
    for i, r in enumerate(rowsAB):
        p.append(text(ox - 22, oy + cw * (i + 0.5) + 5, r, size=12, color=NEG, bold=True))

    # клітини: 1-клітина показує свій номер мінтерма, 0-клітина — світла й порожня
    for i in range(4):
        for j in range(4):
            A = int(rowsAB[i][0]); B = int(rowsAB[i][1])
            C = int(colsCD[j][0]); D = int(colsCD[j][1])
            idx = A * 8 + B * 4 + C * 2 + D
            if idx in ones:
                p.append(cell(ox + cw * j, oy + cw * i, str(idx), cw, cw,
                              fill=BG, size=15, color=INK))
            else:
                p.append(cell(ox + cw * j, oy + cw * i, "", cw, cw,
                              fill=GREY_FILL, size=13, color=MUTED))

    # зелена група — увесь рядок AB=01 (i=1)
    p.append(rect(ox - 5, oy + cw * 1 - 5, cw * 4 + 10, cw + 10,
                  fill="none", stroke=FIELD, sw=3, rx=14))
    # червона група — {0,1,8,9}: два боки (рядок 0 і рядок 3), стовпці 0..1
    p.append(rect(ox - 7, oy + cw * 0 - 7, cw * 2 + 14, cw + 14,
                  fill="none", stroke=POS, sw=3, rx=14))
    p.append(rect(ox - 7, oy + cw * 3 - 7, cw * 2 + 14, cw + 14,
                  fill="none", stroke=POS, sw=3, rx=14))
    # сіра група — 2×2 зліва вгорі {0,1,4,5}, всередині (inset), пунктиром
    p.append(rect(ox + 7, oy + 7, cw * 2 - 14, cw * 2 - 14,
                  fill="none", stroke=MUTED, sw=1.8, rx=12, ))
    # окремим фрагментом додамо пунктир поверх (rect не має dash-параметра тут — лінії)
    gx, gy, gw2 = ox + 7, oy + 7, cw * 2 - 14
    for seg in [ (gx, gy, gx + gw2, gy), (gx + gw2, gy, gx + gw2, gy + gw2),
                 (gx + gw2, gy + gw2, gx, gy + gw2), (gx, gy + gw2, gx, gy) ]:
        p.append(line(seg[0], seg[1], seg[2], seg[3], color=MUTED, sw=1.6, dash="6 4"))

    # зірки на «єдиних» клітинах: 6,7 (лише зелена) та 8,9 (лише червона)
    def star(i, j, col):
        return text(ox + cw * (j + 1) - 12, oy + cw * i + 17, "★", size=13, color=col)
    p.append(star(1, 3, FIELD)); p.append(star(1, 2, FIELD))   # 6, 7
    p.append(star(3, 0, POS));   p.append(star(3, 1, POS))     # 8, 9

    # легенда під картою
    lx, ly = 58, oy + cw * 4 + 34
    def swatch(y, col, fill):
        return rect(lx, y - 11, 20, 15, fill=fill, stroke=col, sw=2, rx=3)
    p.append(swatch(ly, FIELD, GREEN_FILL))
    p.append(text(lx + 30, ly, "Ā·B — простий, істотний", size=12, color=INK, anchor="start"))
    p.append(swatch(ly + 27, POS, RED_FILL))
    p.append(text(lx + 30, ly + 27, "B̄·C̄ — простий, істотний (обгортка верх↔низ)", size=12, color=INK, anchor="start"))
    p.append(swatch(ly + 54, MUTED, GREY_FILL))
    p.append(text(lx + 30, ly + 54, "Ā·C̄ — простий, але ЗАЙВИЙ (лежить під двома іншими)", size=12, color=INK, anchor="start"))
    p.append(text(lx, ly + 84, "★  клітину накриває лише один простий імплікант — його не уникнути",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "implicants.svg"), W, H, *p,
           title="Прості імпліканти: істотні — неминучі, зайві — викидаємо")


# ── Фіг. 2: таблиця «імплікант × мінтерм» (задача покриття) ────────────────────
def fig_pi_chart():
    W, H = 740, 360
    x0 = 56                     # ліва межа стовпця назв
    namew = 104
    cx = x0 + namew             # початок клітин
    cw, ch = 54, 46
    y0 = 74                     # верх заголовка
    mints = [0, 1, 4, 5, 6, 7, 8, 9]
    rows = [
        ("Ā·B",  {4, 5, 6, 7}, "істотний", FIELD),
        ("B̄·C̄", {0, 1, 8, 9}, "істотний", POS),
        ("Ā·C̄",  {0, 1, 4, 5}, "зайвий",    MUTED),
    ]
    # унікальні (накриті лише раз) мінтерми
    cover_cnt = {m: sum(1 for _, s, _, _ in rows if m in s) for m in mints}
    unique = {m for m in mints if cover_cnt[m] == 1}

    p = []
    p.append(text(cx + cw * len(mints) / 2, y0 - 20, "мінтерми (стовпці таблиці істинності, де F = 1)",
                  size=12, color=MUTED))
    p.append(text(x0 + namew / 2, y0 + ch / 2 + 5, "прості", size=12, color=INK, bold=True))
    # підсвітити «єдині» стовпці на всю висоту
    for k, m in enumerate(mints):
        if m in unique:
            p.append(rect(cx + cw * k, y0, cw, ch * (len(rows) + 1), fill=HL_FILL, stroke="none", rx=0))
    # заголовок: номери мінтермів
    for k, m in enumerate(mints):
        p.append(cell(cx + cw * k, y0, str(m), cw, ch, fill="none",
                      stroke=INK, size=14, color=INK))
    # рядки-імпліканти
    for r, (name, s, tag, col) in enumerate(rows):
        yy = y0 + ch * (r + 1)
        p.append(cell(x0, yy, name, namew, ch, fill=BG, stroke=INK, size=15, color=col))
        for k, m in enumerate(mints):
            mark = "✓" if m in s else ""
            mc = FIELD if m in s else MUTED
            p.append(cell(cx + cw * k, yy, mark, cw, ch, fill="none",
                          stroke=INK, size=17, color=mc))
        # позначка істотності/зайвості праворуч
        tagcol = col if tag == "зайвий" else col
        p.append(text(cx + cw * len(mints) + 14, yy + ch / 2 + 5, tag,
                      size=12, color=tagcol, bold=True, anchor="start"))

    # підпис під «єдиними» стовпцями
    for k, m in enumerate(mints):
        if m in unique:
            p.append(text(cx + cw * (k + 0.5), y0 + ch * (len(rows) + 1) + 16,
                          "єдиний", size=10, color=POS))

    # висновок (два рядки, щоб не вилазив за межі)
    box, _, _ = textbox(W / 2, y0 + ch * (len(rows) + 1) + 56,
                        "Стовпці 6,7 і 8,9 накриті лише раз → Ā·B і B̄·C̄ неминучі й разом покрили все.\nОтже Ā·C̄ зайвий.   Мінімум:  F = Ā·B + B̄·C̄",
                        size=12, color=INK, fill="#f6f4ec", stroke=INK, sw=1.6, bold=True)
    p.append(box)

    render(os.path.join(OUT, "pi-chart.svg"), W, H, *p,
           title="Таблиця покриття: істотні імпліканти беруть перше слово")


# ── Фіг. 3: який метод — за числом змінних ────────────────────────────────────
def fig_landscape():
    W, H = 760, 360
    axx0, axx1, axy = 96, 700, 300
    notex = 694                               # спільний правий стовпець приміток
    p = []

    # (коротка назва в смузі; докладна примітка — окремим правим стовпцем)
    bands = [
        ("Алгебра",             250, FIELD, GREEN_FILL, "2–4 · вручну, ненадійно"),
        ("Карта Карно",         336, NEG,   "#eaf0fd",  "до ~6 · очима, швидко"),
        ("Квайн–Мак-Класкі",    478, POS,   RED_FILL,   "десятки · точно, та експонента"),
        ("Евристики, синтезатори", 700, INK, GREY_FILL, "сотні–тисячі · майже мінімум"),
    ]
    y = 66
    bh, gap = 48, 10
    for name, xend, col, fill, note in bands:
        p.append(rect(axx0, y, xend - axx0, bh, fill=fill, stroke=col, sw=2, rx=10))
        p.append(text(axx0 + 14, y + bh / 2 + 5, name, size=14, color=INK, bold=True, anchor="start"))
        p.append(text(notex, y + bh / 2 + 5, note, size=11, color=MUTED, anchor="end"))
        y += bh + gap

    # вісь «кількість змінних»
    p.append(line(axx0, axy, axx1 + 6, axy, color=INK, sw=1.6))
    p.append(text(axx1 + 6, axy, "▶", size=12, color=INK, anchor="start"))
    p.append(text(axx0, axy + 26, "кількість змінних  →", size=12, color=MUTED, anchor="start"))
    for xt, lab in [(250, "≈4"), (336, "≈6"), (478, "десятки"), (660, "тисячі")]:
        p.append(line(xt, axy - 4, xt, axy + 4, color=MUTED, sw=1.4))
        p.append(text(xt, axy + 18, lab, size=11, color=MUTED))

    render(os.path.join(OUT, "landscape.svg"), W, H, *p,
           title="Який метод мінімізації — залежить від числа змінних")


# ══ Фігури вставки math-prime-implicants ══════════════════════════════════════

BLUE_FILL = "#eaf0fd"


def _node(x, y, w, h, label, pts, fill=BG, stroke=INK, sw=1.4,
          lsize=11, psize=10, lcolor=INK):
    """Вузол-імплікант: рамка + назва добутку + множина накритих точок під нею."""
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=6)
    out += text(x + w / 2, y + h * 0.40 + lsize * 0.35, label,
                size=lsize, color=lcolor, bold=True)
    out += text(x + w / 2, y + h * 0.78, pts, size=psize, color=MUTED)
    return out


# ── Фіг. 4 (вставка): поверхи імплікантів; максимальних — рівно 3 ─────────────
# Три поверхи Imp(F) за числом літер. Ланцюг Ā·B·C·D̄ → Ā·B·C → Ā·B — «прогулянка
# вгору» з леми 1: кожен крок скидає одну літеру, тож більш ніж за n кроків не буває.
def fig_pi_poset():
    W, H = 1090, 430
    CX = 620

    tops = [                                   # 2 літери · 4 точки — МАКСИМАЛЬНІ
        ("B̄·C̄", "{0,1,8,9}", POS,   RED_FILL),
        ("Ā·B",  "{4,5,6,7}", FIELD, GREEN_FILL),   # index 1 — вершина ланцюга
        ("Ā·C̄", "{0,1,4,5}", MUTED, GREY_FILL),
    ]
    mids = [                                   # 3 літери · 2 точки
        ("Ā·B̄·C̄", "{0,1}"), ("Ā·C̄·D̄", "{0,4}"), ("B̄·C̄·D̄", "{0,8}"),
        ("Ā·C̄·D", "{1,5}"), ("B̄·C̄·D", "{1,9}"),
        ("Ā·B·C",  "{6,7}"),                        # index 5 — середина ланцюга
        ("Ā·B·C̄", "{4,5}"), ("Ā·B·D̄", "{4,6}"), ("Ā·B·D", "{5,7}"),
        ("A·B̄·C̄", "{8,9}"),
    ]
    bots = [                                   # 4 літери · 1 точка — мінтерми
        ("Ā·B̄·C̄·D̄", "{0}"), ("Ā·B̄·C̄·D", "{1}"),
        ("Ā·B·C̄·D̄", "{4}"), ("Ā·B·C̄·D", "{5}"),
        ("Ā·B·C·D̄", "{6}"),                         # index 4 — низ ланцюга
        ("Ā·B·C·D", "{7}"),
        ("A·B̄·C̄·D̄", "{8}"), ("A·B̄·C̄·D", "{9}"),
    ]

    TY, TH, TW, TG = 58, 44, 124, 44
    MY, MH, MW, MG = 196, 40, 78, 8
    BY, BH, BW, BG_ = 330, 40, 98, 8
    tx0 = CX - (len(tops) * TW + (len(tops) - 1) * TG) / 2
    mx0 = CX - (len(mids) * MW + (len(mids) - 1) * MG) / 2
    bx0 = CX - (len(bots) * BW + (len(bots) - 1) * BG_) / 2

    def tcx(i): return tx0 + i * (TW + TG) + TW / 2
    def mcx(i): return mx0 + i * (MW + MG) + MW / 2
    def bcx(i): return bx0 + i * (BW + BG_) + BW / 2

    p = []

    # ── ліві підписи поверхів (окремий стовпець, лінії й вузли туди не заходять)
    def band(y, l1, l2, l3, c3):
        return (text(18, y + 10, l1, size=11, color=INK, bold=True, anchor="start") +
                text(18, y + 26, l2, size=11, color=MUTED, anchor="start") +
                text(18, y + 42, l3, size=10, color=c3, bold=True, anchor="start"))

    p.append(band(TY, "2 літери", "грань = 4 точки", "МАКСИМАЛЬНІ → прості", INK))
    p.append(band(MY, "3 літери", "грань = 2 точки", "10 штук", MUTED))
    p.append(band(BY, "4 літери", "грань = 1 точка", "8 мінтермів", MUTED))

    # ── поверхи
    for i, (lab, pts, col, fill) in enumerate(tops):
        chain = (i == 1)
        p.append(_node(tcx(i) - TW / 2, TY, TW, TH, lab, pts, fill=fill,
                       stroke=NEG if chain else col, sw=3.2 if chain else 2.2,
                       lsize=13, psize=11, lcolor=col))
    for i, (lab, pts) in enumerate(mids):
        chain = (i == 5)
        p.append(_node(mcx(i) - MW / 2, MY, MW, MH, lab, pts, fill=BLUE_FILL if chain else BG,
                       stroke=NEG if chain else INK, sw=3.0 if chain else 1.2))
    for i, (lab, pts) in enumerate(bots):
        chain = (i == 4)
        p.append(_node(bcx(i) - BW / 2, BY, BW, BH, lab, pts, fill=BLUE_FILL if chain else BG,
                       stroke=NEG if chain else INK, sw=3.0 if chain else 1.2))

    # ── ланцюг «угору»: стрілки живуть у порожніх смугах МІЖ поверхами
    p.append(arrow(bcx(4), BY - 4, mcx(5), MY + MH + 4, color=NEG, sw=2.6))
    p.append(arrow(mcx(5), MY - 4, tcx(1), TY + TH + 4, color=NEG, sw=2.6))

    p.append(text(CX, 402,
                  "синім — прогулянка вгору: Ā·B·C·D̄ → Ā·B·C → Ā·B. "
                  "Кожен крок скидає одну літеру, тож кроків не більше за n = 4",
                  size=12, color=NEG))

    render(os.path.join(OUT, "pi-poset.svg"), W, H, *p,
           title="Усі 21 імпліканти F — і лише 3 максимальні серед них")


# ── Фіг. 5 (вставка): теорема залежить від того, ЩО міряють ───────────────────
# F(A,B,C)=Σm(0,1,2,3,4,5). Обидва записи — по 2 доданки, але правий містить
# НЕ простий Ā·B (він лежить усередині Ā) і коштує на літеру більше.
def fig_cost_caveat():
    W, H = 760, 322
    cw = 56
    oy = 112
    colsBC = ["00", "01", "11", "10"]
    ones = {0, 1, 2, 3, 4, 5}

    def kmap(ox, groups, cap1, cap2, capcol):
        q = []
        q.append(text(ox + cw * 2, oy - 34, "BC", size=13, color=MUTED, bold=True))
        for j, c in enumerate(colsBC):
            q.append(text(ox + cw * (j + 0.5), oy - 14, c, size=12, color=NEG, bold=True))
        q.append(text(ox - 34, oy + cw - 6, "A", size=13, color=MUTED, bold=True))
        for i in range(2):
            q.append(text(ox - 18, oy + cw * (i + 0.5) + 5, str(i), size=12, color=NEG, bold=True))
        for i in range(2):
            for j in range(4):
                B = int(colsBC[j][0]); C = int(colsBC[j][1])
                idx = i * 4 + B * 2 + C
                if idx in ones:
                    q.append(cell(ox + cw * j, oy + cw * i, str(idx), cw, cw,
                                  fill=BG, size=14, color=INK))
                else:
                    q.append(cell(ox + cw * j, oy + cw * i, "", cw, cw,
                                  fill=GREY_FILL, size=12, color=MUTED))
        for gx, gy, gw, gh, col in groups:
            q.append(rect(gx, gy, gw, gh, fill="none", stroke=col, sw=3, rx=13))
        q.append(text(ox + cw * 2, oy + cw * 2 + 40, cap1, size=15, color=INK, bold=True))
        q.append(text(ox + cw * 2, oy + cw * 2 + 62, cap2, size=12, color=capcol, bold=True))
        return q

    ox1, ox2 = 118, 478
    # ліва карта: Ā (увесь рядок A=0) + B̄ (два ліві стовпці, обидва рядки)
    p = kmap(ox1,
             [(ox1 - 5, oy - 5, cw * 4 + 10, cw + 10, FIELD),
              (ox1 - 11, oy - 11, cw * 2 + 22, cw * 2 + 22, POS)],
             "F = Ā + B̄",
             "2 доданки · 2 літери · обидва прості", FIELD)
    # права карта: B̄ + Ā·B (пів-грані: Ā·B лежить усередині Ā)
    p += kmap(ox2,
              [(ox2 - 11, oy - 11, cw * 2 + 22, cw * 2 + 22, POS),
               (ox2 + cw * 2 + 8, oy - 5, cw * 2 - 16, cw + 10, NEG)],
              "F = B̄ + Ā·B",
              "2 доданки · 3 літери · Ā·B НЕ простий", NEG)

    render(os.path.join(OUT, "pi-cost-caveat.svg"), W, H, *p,
           title="Та сама функція, два записи по два доданки")


if __name__ == "__main__":
    fig_implicants()
    fig_pi_chart()
    fig_landscape()
    fig_pi_poset()
    fig_cost_caveat()
    print("OK: figures written to", OUT)
