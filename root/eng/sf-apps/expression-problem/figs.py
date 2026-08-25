# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Одна матриця, два розрізи: транспонована дуальність рядків і стовпців ──────
def fig_expression_duality():
    W, H = 1180, 600
    frags = []
    frags.append(text(W / 2, 40, "Проблема вираження: одна матриця, два розрізи",
                      size=17, bold=True, color=INK))
    frags.append(text(W / 2, 62,
                      "типи — рядки, операції — стовпці; одиниця коду — або рядок, або стовпець",
                      size=12.5, color=MUTED))
    frags.append(line(W / 2, 92, W / 2, H - 92, color="#d0d5db", sw=1.2, dash="6,6"))

    ops = ["eval", "show", "simp"]
    types = ["Lit", "Add", "Mul"]
    hdrW, hdrH, cw, ch = 78, 34, 68, 44
    oy = 120

    def panel(ox, unit, title, cap_cheap, cap_dear):
        cx = ox + (hdrW + 3 * cw) / 2          # центр «ядра» сітки
        p = [text(cx, 106, title, size=14, bold=True, color=INK)]
        # кут
        p.append(rect(ox, oy, hdrW, hdrH, fill="#eef2f7", stroke=LINE, sw=1.1))
        p.append(text(ox + hdrW / 2, oy + hdrH / 2 + 4, "тип·опер", size=10, color=MUTED))
        # шапка-операції (стовпці); у ФП саме вони — одиниця коду, тож зелені
        colunit = (unit == "col")
        for j, op in enumerate(ops):
            cxj = ox + hdrW + j * cw
            p.append(rect(cxj, oy, cw, hdrH, fill=("#e8f6ee" if colunit else "#eef2f7"),
                          stroke=(FIELD if colunit else LINE), sw=(1.5 if colunit else 1.1)))
            p.append(text(cxj + cw / 2, oy + hdrH / 2 + 4, op, size=12, bold=colunit, color=INK))
        # шапка-типи (рядки) + тіло; в ООП рядки — одиниця коду, тож зелені
        rowunit = (unit == "row")
        for i, tp in enumerate(types):
            ry = oy + hdrH + i * ch
            p.append(rect(ox, ry, hdrW, ch, fill=("#e8f6ee" if rowunit else "#eef2f7"),
                          stroke=(FIELD if rowunit else LINE), sw=(1.5 if rowunit else 1.1)))
            p.append(text(ox + hdrW / 2, ry + ch / 2 + 4, tp, size=12, bold=rowunit, color=INK))
            for j in range(3):
                cxj = ox + hdrW + j * cw
                p.append(rect(cxj, ry, cw, ch, fill=BG, stroke="#c9ced6", sw=1.0))
        # привид: новий РЯДОК унизу
        cheap_row = (unit == "row")
        rc = FIELD if cheap_row else POS
        rt = "#eef8f2" if cheap_row else "#fdecea"
        ry = oy + hdrH + 3 * ch
        p.append(rect(ox, ry, hdrW, ch, fill=rt, stroke=rc, sw=1.6, rx=4))
        p.append(text(ox + hdrW / 2, ry + ch / 2 + 4, "+тип", size=11.5, bold=True, color=rc))
        for j in range(3):
            cxj = ox + hdrW + j * cw
            p.append(rect(cxj, ry, cw, ch, fill=rt, stroke=rc, sw=1.3, rx=4))
        # привид: новий СТОВПЕЦЬ праворуч
        cc = POS if cheap_row else FIELD
        ct = "#fdecea" if cheap_row else "#eef8f2"
        cxg = ox + hdrW + 3 * cw
        p.append(rect(cxg, oy, cw, hdrH, fill=ct, stroke=cc, sw=1.6, rx=4))
        p.append(text(cxg + cw / 2, oy + hdrH / 2 + 4, "+опер", size=11, bold=True, color=cc))
        for i in range(3):
            ry2 = oy + hdrH + i * ch
            p.append(rect(cxg, ry2, cw, ch, fill=ct, stroke=cc, sw=1.3, rx=4))
        # підписи: зелене — дешева вісь, червоне — дорога
        p.append(text(cx, 372, cap_cheap, size=12, bold=True, color=FIELD))
        p.append(text(cx, 394, cap_dear, size=12, bold=True, color=POS))
        return p

    frags += panel(145, "row", "Об'єктний розклад (ООП): код = РЯДОК",
                   "+тип — 1 клас, старе ціле", "+опер — метод у КОЖЕН клас")
    frags += panel(744, "col", "Функційний розклад (ФП): код = СТОВПЕЦЬ",
                   "+опер — 1 функція, старе ціле", "+тип — гілка в КОЖНУ функцію")
    frags.append(text(W / 2, 556,
                      "Що одна сторона дарує (зелене), друга бере за те саме плату (червоне): осі протилежні.",
                      size=12.5, color=INK))
    render(os.path.join(IMG, 'expression-duality.svg'), W, H, *frags)


# ── Чому базова диспетчеризація закриває РІВНО одну вісь ──────────────────────
def fig_single_dispatch_axis():
    W, H = 980, 480
    p = []
    p.append(text(W / 2, 30, "Спільний контракт перелічує одну вісь — саме її й закриває",
                  size=16, bold=True))
    p.append(line(W / 2, 56, W / 2, H - 52, color=MUTED, sw=1, dash="6,6"))

    def panel(cx, header, sub, contract, clabel, members, mlab):
        pp = []
        pp.append(text(cx, 80, header, size=14, bold=True, color=INK))
        pp.append(text(cx, 99, sub, size=11, italic=True, color=MUTED))
        # контракт — перелічена вісь = закрита (POS)
        pp.append(fitbox(cx - 180, 118, 360, 46, contract, size=12.5,
                         fill="#fdecea", stroke=POS, sw=1.9))
        pp.append(text(cx, 182, clabel, size=11.5, color=POS, bold=True))
        # відкрита вісь — члени (FIELD), останній новий
        bw, gap, by, bh = 118, 16, 252, 44
        total = 3 * bw + 2 * gap
        x0 = cx - total / 2
        for i, lab in enumerate(members):
            x = x0 + i * (bw + gap)
            new = (i == 2)
            pp.append(fitbox(x, by, bw, bh, lab, size=12.5,
                             fill="#eaf7ee" if new else FILL,
                             stroke=FIELD if new else LINE,
                             sw=1.8 if new else 1.4, bold=new))
        pp.append(plus(x0 + 2 * (bw + gap) + bw - 6, by, r=10))
        pp.append(text(cx, by + bh + 24, mlab[0], size=11.5, color=FIELD, bold=True))
        pp.append(text(cx, by + bh + 42, mlab[1], size=11, color=MUTED))
        return pp

    p += panel(245, "Об'єктний стиль — x.op()", "інтерфейс фіксує операції",
               "interface Shape\n{ area(); perimeter(); }",
               "перелічує ОПЕРАЦІЇ → вісь закрита",
               ["Circle", "Rect", "+ новий тип"],
               ["новий тип = новий клас,", "контракт недоторканий → відкрито"])
    p += panel(735, "Процедурний стиль — op(x)", "сума типів фіксує випадки",
               "enum Kind\n{ Circle, Rect }",
               "перелічує ТИПИ → вісь закрита",
               ["area()", "perimeter()", "+ нова оп."],
               ["нова операція = нова функція,", "контракт недоторканий → відкрито"])

    p.append(text(W / 2, H - 30,
                  "Одна вісь мусить лягти у спільний контракт — саме вона й закрита.",
                  size=12.5, color=INK))
    p.append(text(W / 2, H - 12,
                  "Базова (одинарна) диспетчеризація тримає відкритою рівно одну вісь.",
                  size=12.5, italic=True, color=MUTED))
    render(os.path.join(IMG, "single-dispatch-axis.svg"), W, H, *p)


# ── Чотири виходи з вилки на площині «дешево додати тип / операцію» ───────────
def fig_escape_quadrants():
    W, H = 1000, 600
    frags = []
    frags.append(text(W / 2, 38, "Чотири виходи з вилки — і хибний вихід",
                      size=17, bold=True, color=INK))
    frags.append(text(W / 2, 60,
                      "осі: чи дешево додати ОПЕРАЦІЮ (праворуч) і чи дешево додати ТИП (вгору)",
                      size=12.5, color=MUTED))

    L, R, T, B = 150, 858, 100, 470
    midx, midy = (L + R) / 2, (T + B) / 2
    frags.append(rect(L, T, R - L, B - T, fill=BG, stroke="#c9ced6", sw=1.2))
    frags.append(line(midx, T, midx, B, color="#d0d5db", sw=1.1, dash="5,5"))
    frags.append(line(L, midy, R, midy, color="#d0d5db", sw=1.1, dash="5,5"))

    def qbox(cx, cy, lines, hl=False, faint=False):
        fill = "#eafaf1" if hl else (BG if faint else FILL)
        stroke = FIELD if hl else ("#d0d5db" if faint else LINE)
        color = MUTED if faint else INK
        b, _, _ = textbox(cx, cy, lines, size=12, fill=fill, stroke=stroke,
                          sw=(2 if hl else 1.3), color=color, bold=hl)
        return b

    frags.append(qbox(327, 192, ["ООП · Абстрактна фабрика",
                                 "рядки — даром,", "стовпці — за плату"]))
    frags.append(qbox(681, 192, ["Мультиметоди · Класи типів",
                                 "Tagless-final · Object algebras",
                                 "обидві осі — відкрито"], hl=True))
    frags.append(qbox(327, 377, ["(обидві дорого —", "свідомо не тут)"], faint=True))
    frags.append(qbox(681, 377, ["ФП · взірці · Відвідувач",
                                 "стовпці — даром,", "рядки — за плату"]))

    # відвідувач — двобічна діагональ (поворот між рогами, не вихід)
    frags.append(arrow(430, 225, 575, 352, color=NEG, sw=1.6))
    frags.append(arrow(575, 352, 430, 225, color=NEG, sw=1.6))
    frags.append(text(300, 320, "Відвідувач — поворот, не вихід", size=12, color=NEG))

    # осьові мітки
    frags.append(text(300, 492, "операцію: ДОРОГО", size=12, bold=True, color=POS))
    frags.append(text(700, 492, "операцію: ДЕШЕВО", size=12, bold=True, color=FIELD))
    frags.append(text(midx, 510, "→ додати операцію (стовпець)", size=11.5, color=MUTED))
    frags.append(mtext(78, 150, ["тип:", "ДЕШЕВО"], size=11.5, color=FIELD, bold=True))
    frags.append(mtext(78, 452, ["тип:", "ДОРОГО"], size=11.5, color=POS, bold=True))

    frags.append(text(W / 2, 540,
                      "ООП-ріг (класи) і ФП-ріг стоять навпроти по діагоналі; Відвідувач лише возить між ними.",
                      size=12, color=INK))
    frags.append(text(W / 2, 562,
                      "Правий-верхній кут — справжній вихід: додати і тип, і операцію, не чіпаючи старого.",
                      size=12, color=INK))
    render(os.path.join(IMG, 'escape-quadrants.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_expression_duality()
    fig_single_dispatch_axis()
    fig_escape_quadrants()
    print("figs done")
