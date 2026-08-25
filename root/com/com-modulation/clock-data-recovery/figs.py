# -*- coding: utf-8 -*-
"""Фігури до теми «Відновлення такту з даних (CDR)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def edge(x0, x1, y0, y1, n=18):
    """Список точок згладженого переходу рівня від (x0,y0) до (x1,y1)."""
    pts = []
    for i in range(n + 1):
        t = i / n
        s = 0.5 * (1 - math.cos(math.pi * t))
        pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * s))
    return pts


def polyline(pts, color=INK, sw=1.8, opacity=1.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    o = ' stroke-opacity="%.2f"' % opacity if opacity < 1 else ''
    pd = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s%s/>'
            % (pd, color, sw, o, d))


def wave(x0, bits, ub, hi, lo, sw=2.0, color=INK, edgew=0.28):
    """Цифрова траса з бітів: список сегментів SVG."""
    pts = []
    prev = bits[0]
    for i, b in enumerate(bits):
        x = x0 + i * ub
        yb = hi if b else lo
        yp = hi if prev else lo
        if i == 0:
            pts.append((x, yb))
        else:
            pts += edge(x, x + ub * edgew, yp, yb)
        pts.append((x + ub, yb))
        prev = b
    return polyline(pts, color=color, sw=sw)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 1 — суть задачі: такту нема, його треба зчитати з переходів даних
# ════════════════════════════════════════════════════════════════════════════
def fig_problem():
    W, H = 720, 330
    els = [text(W / 2, 26, "Такту в лінії немає — момент відліку треба здобути з самих переходів", size=15, bold=True)]

    lx, lw = 60, 600
    bits = [1, 0, 1, 1, 0, 1, 0, 0, 1, 0]
    ub = lw / len(bits)
    hi, lo = 90, 170

    # рівні
    els.append(line(lx, hi, lx + lw, hi, color=MUTED, sw=1, dash="3,4"))
    els.append(line(lx, lo, lx + lw, lo, color=MUTED, sw=1, dash="3,4"))
    els.append(text(lx - 8, hi + 4, "1", size=12, color=MUTED, anchor="end"))
    els.append(text(lx - 8, lo + 4, "0", size=12, color=MUTED, anchor="end"))
    els.append(text(lx + lw / 2, 56, "єдина лінія даних (окремого дроту-такту немає)", size=12, color=INK))

    # сама траса
    els.append(wave(lx, bits, ub, hi, lo))

    # позначити переходи — «мітки часу»
    prev = bits[0]
    for i, b in enumerate(bits):
        if i > 0 and b != prev:
            x = lx + i * ub + ub * 0.14
            els.append(line(x, hi - 16, x, lo + 16, color=FIELD, sw=1.4, dash="2,3"))
        prev = b
    els.append(text(lx + lw * 0.30, hi - 24, "перехід = мітка часу", size=11.5, color=FIELD, bold=True))

    # точки відліку — в середині кожного біта
    sy = lo + 58
    els.append(line(lx, sy, lx + lw, sy, color=MUTED, sw=1))
    for i, b in enumerate(bits):
        xc = lx + i * ub + ub * 0.5
        els.append(circle(xc, sy, 4.5, fill="#eafaf0", stroke=FIELD, sw=1.8))
        els.append(line(xc, lo + 16, xc, sy - 6, color=FIELD, sw=1, dash="1,3"))
    els.append(text(lx + lw / 2, sy + 26, "мета CDR: клацнути рівно в СЕРЕДИНІ кожного біта — найдалі від переходів",
                    size=12, color=FIELD, bold=True))

    render(os.path.join(IMG, "cdr-problem.svg"), W, H, *els)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 2 — контур CDR: детектор фази → фільтр → генератор, назад на детектор
# ════════════════════════════════════════════════════════════════════════════
def fig_loop():
    W, H = 720, 340
    els = [text(W / 2, 26, "Контур відновлення такту: та сама петля, що й у PLL, але опора — самі дані", size=14.5, bold=True)]

    y = 150
    bw, bh = 132, 66

    # блок 1: фазовий детектор
    b1 = fitbox(70, y - bh / 2, bw, bh, "Детектор фази\n(дані ↔ такт: рано/пізно?)", size=12, fill=FILL, stroke=LINE)
    els.append(b1)
    # блок 2: фільтр контуру
    b2 = fitbox(294, y - bh / 2, bw, bh, "Фільтр контуру\n(згладжує похибку)", size=12, fill=FILL, stroke=LINE)
    els.append(b2)
    # блок 3: генератор
    b3 = fitbox(518, y - bh / 2, bw, bh, "Генератор такту\n(VCO / NCO)", size=12, fill="#eafaf0", stroke=FIELD)
    els.append(b3)

    # стрілки вперед
    els.append(arrow(202, y, 292, y, color=LINE, sw=2))
    els.append(text(247, y - 8, "похибка", size=11, color=MUTED))
    els.append(arrow(426, y, 516, y, color=LINE, sw=2))
    els.append(text(471, y - 8, "керування", size=11, color=MUTED))

    # вхід даних у детектор
    els.append(arrow(70, y - 46, 70, y - bh / 2, color=INK, sw=2))
    els.append(text(70, y - 54, "потік даних", size=12, color=INK, bold=True))

    # відновлений такт — вихід генератора
    els.append(arrow(650, y - bh / 2, 650, y - 46, color=FIELD, sw=2))
    els.append(text(650, y - 54, "відновлений такт", size=12, color=FIELD, bold=True))

    # зворотний зв'язок: вихід генератора назад на детектор
    els.append(line(584, y + bh / 2, 584, y + 78, color=LINE, sw=1.8))
    els.append(line(584, y + 78, 136, y + 78, color=LINE, sw=1.8))
    els.append(arrow(136, y + 78, 136, y + bh / 2, color=LINE, sw=1.8))
    els.append(text(360, y + 94, "відновлений такт повертається на детектор — петля сама гасить розбіжність фаз",
                    size=11.5, color=MUTED))

    # сэмплер збоку: такт клацає дані в середині біта
    els.append(fitbox(300, y + 108, 120, 40, "цим тактом клацаємо\nдані в середині біта", size=11, fill="#fff8e6", stroke=POS))

    render(os.path.join(IMG, "cdr-loop.svg"), W, H, *els)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 3 — bang-bang (Alexander): відлік на переході каже лише «рано / пізно»
# ════════════════════════════════════════════════════════════════════════════
def fig_bangbang():
    W, H = 720, 350
    els = [text(W / 2, 24, "Bang-bang детектор (Alexander): відлік на межі каже тільки «рано» чи «пізно»", size=14.5, bold=True)]

    def scene(px, title, early, verdict, vcol):
        # перехід 0→1 стоїть у ФІКСОВАНОМУ місці вікна; наш такт клацає на своїй "межі".
        # early=True: наша межа спрацьовує ДО переходу (даних ще не змінились) → такт зарано.
        top, bot = 74, 196
        w = 250
        x0 = px
        mid = (top + bot) / 2
        # справжній перехід даних — трохи правіше або лівіше центру
        tc = x0 + w * (0.50)                 # центр вікна = ідеальне місце межі
        tr0, tr1 = tc - w * 0.05, tc + w * 0.05
        out = [text(px + w / 2, 52, title, size=13, bold=True)]
        out.append(line(x0, top, x0 + w, top, color=MUTED, sw=1, dash="3,4"))
        out.append(line(x0, bot, x0 + w, bot, color=MUTED, sw=1, dash="3,4"))
        # три відліки нашого такту: центр біта зліва (D_pre), МЕЖА (E), центр біта справа (D_post)
        # їх ставимо симетрично навколо ІДЕАЛЬНОЇ межі, але сама межа-відлік E зсунута,
        # бо генератор зарано/запізно
        ui = w * 0.42
        shift = (-1 if early else +1) * w * 0.14
        ex = tc + shift                       # де насправді клацає наш "межовий" відлік
        dpre = ex - ui * 0.5
        dpost = ex + ui * 0.5

        # траса 0→1 (перехід у tc)
        pts = [(x0, bot)] + edge(tr0, tr1, bot, top) + [(x0 + w, top)]
        out.append(polyline(pts, color=INK, sw=2.2))

        def lvl(xx):
            if xx <= tr0:
                return bot
            if xx >= tr1:
                return top
            return mid
        for lab, xx, sub in (("D₋", dpre, "біт до"), ("E", ex, "МЕЖА"), ("D₊", dpost, "біт після")):
            out.append(line(xx, top - 8, xx, bot + 8, color=(POS if lab == "E" else MUTED),
                            sw=(1.6 if lab == "E" else 1.0), dash="2,3"))
            out.append(circle(xx, lvl(xx), 4.6, fill="#fdecea", stroke=POS, sw=1.8))
            out.append(text(xx, top - 14, lab, size=12, color=(POS if lab == "E" else MUTED), bold=(lab == "E")))
        # позначити ідеальну межу
        out.append(line(tc, top - 8, tc, bot + 8, color=FIELD, sw=1.2, dash="4,3"))
        out.append(text(tc, bot + 24, "справжній перехід", size=10.5, color=FIELD))
        out.append(text(px + w / 2, bot + 48, verdict, size=12.5, color=vcol, bold=True))
        return out

    # ліва: наша межа E спрацювала ДО переходу — на ній дані ще старі (=D₋) → такт зарано
    els += scene(50, "такт зарано", True,
                 "на межі E дані ще НЕ змінились → «рано»: пригальмувати", NEG)
    # права: наша межа E спрацювала ПІСЛЯ переходу — дані вже нові → такт запізно
    els += scene(400, "такт запізно", False,
                 "на межі E дані ВЖЕ змінились → «пізно»: підігнати", POS)

    els.append(text(W / 2, 314, "Детектор не міряє, НАСКІЛЬКИ схибив такт, лише В ЯКИЙ БІК — тому такт дрібно «клює» навколо цілі (звідси bang-bang).",
                    size=11.5, color=INK))
    render(os.path.join(IMG, "cdr-bangbang.svg"), W, H, *els)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 4 — передискретизація й вибір фази: N відліків на біт, беремо середній
# ════════════════════════════════════════════════════════════════════════════
def fig_oversample():
    W, H = 720, 330
    els = [text(W / 2, 24, "Передискретизація: беремо N відліків на біт і вибираємо той, що найдалі від переходів", size=13.5, bold=True)]

    lx, lw = 60, 600
    bits = [1, 1, 0, 1, 0, 0, 1]
    ub = lw / len(bits)
    hi, lo = 80, 150
    OS = 5  # відліків на UI

    els.append(line(lx, hi, lx + lw, hi, color=MUTED, sw=1, dash="3,4"))
    els.append(line(lx, lo, lx + lw, lo, color=MUTED, sw=1, dash="3,4"))
    els.append(text(lx - 8, hi + 4, "1", size=12, color=MUTED, anchor="end"))
    els.append(text(lx - 8, lo + 4, "0", size=12, color=MUTED, anchor="end"))

    els.append(wave(lx, bits, ub, hi, lo, edgew=0.22))

    # відліки OS на біт: точки зверху; де є перехід — сусідні відліки різні
    sy = lo + 40
    prev = bits[0]
    # позначимо, у яких біт-межах перехід
    for i, b in enumerate(bits):
        x0 = lx + i * ub
        for k in range(OS):
            xs = x0 + ub * (k + 0.5) / OS
            # рівень відліку: беремо значення біта (перехід у першій частці біта)
            in_edge = (i > 0 and b != prev and k == 0)
            col = POS if in_edge else INK
            els.append(circle(xs, sy, 3.2, fill=("#fdecea" if in_edge else FILL),
                              stroke=col, sw=1.4))
        # вибраний «середній» відлік біта — зелений (найдалі від країв)
        xm = x0 + ub * (OS // 2 + 0.5) / OS
        els.append(circle(xm, sy, 5.2, fill="#eafaf0", stroke=FIELD, sw=2.2))
        prev = b
    els.append(text(lx + lw / 2, sy + 26, "кожен біт «сфотографовано» %d рази; червоні відліки впіймали перехід" % OS,
                    size=11.5, color=MUTED))
    els.append(text(lx + lw / 2, sy + 44, "зелений — обраний відлік у СЕРЕДИНІ біта (між сусідніми переходами)",
                    size=11.5, color=FIELD, bold=True))

    render(os.path.join(IMG, "cdr-oversample.svg"), W, H, *els)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 5 — довга серія однакових бітів: такт «пливе», бо нема за що чіплятись
# ════════════════════════════════════════════════════════════════════════════
def fig_drift():
    W, H = 720, 320
    els = [text(W / 2, 24, "Довга серія без переходів — такт «пливе» й може прорахувати біт", size=14.5, bold=True)]

    lx, lw = 60, 600
    # багато нулів поспіль, потім перехід
    bits = [1, 0, 1] + [0] * 9 + [1, 0]
    ub = lw / len(bits)
    hi, lo = 78, 140

    els.append(line(lx, hi, lx + lw, hi, color=MUTED, sw=1, dash="3,4"))
    els.append(line(lx, lo, lx + lw, lo, color=MUTED, sw=1, dash="3,4"))
    els.append(text(lx - 8, hi + 4, "1", size=12, color=MUTED, anchor="end"))
    els.append(text(lx - 8, lo + 4, "0", size=12, color=MUTED, anchor="end"))
    els.append(wave(lx, bits, ub, hi, lo, edgew=0.22))

    # зона «мовчання» (нулі)
    z0 = lx + 3 * ub
    z1 = lx + 12 * ub
    els.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.10" stroke="none"/>'
               % (z0, hi - 14, z1 - z0, (lo - hi) + 28, POS))
    els.append(text((z0 + z1) / 2, hi - 22, "дев'ять нулів поспіль — жодного переходу", size=12, color=POS, bold=True))

    # ідеальний такт (зелений) vs той, що пливе (червоний), нижче
    ty = lo + 46
    els.append(text(lx - 8, ty + 4, "такт", size=11, color=MUTED, anchor="end"))
    # ідеальні мітки
    for i in range(len(bits)):
        xc = lx + i * ub + ub * 0.5
        els.append(line(xc, ty - 8, xc, ty + 8, color=FIELD, sw=1.4))
    els.append(text(lx + 1.5 * ub, ty - 16, "ідеал: мітки точно посередині", size=11, color=FIELD))
    # такт, що пливе — у зоні мовчання мітки поступово зсуваються вправо
    ty2 = ty + 44
    for i in range(len(bits)):
        drift = 0.0
        if 3 <= i <= 12:
            drift = (i - 3) * 0.045 * ub  # накопичений зсув
        xc = lx + i * ub + ub * 0.5 + drift
        col = POS if 3 <= i <= 12 else INK
        els.append(line(xc, ty2 - 8, xc, ty2 + 8, color=col, sw=1.4))
    els.append(text(lx + lw * 0.62, ty2 + 22, "реальний генератор «пливе» — мітки сповзають; на виході серії ризик зчитати зайвий/пропущений біт",
                    size=11, color=POS, bold=True))

    render(os.path.join(IMG, "cdr-drift.svg"), W, H, *els)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 6 (вставка hist) — родовід: від телеграфного розмивання до детекторів
# ════════════════════════════════════════════════════════════════════════════
def fig_lineage():
    W, H = 760, 470
    els = [text(W / 2, 28, "Родовід відновлення такту: спільна думка — добути ритм із самого сигналу", size=15, bold=True)]

    # вертикальна вісь часу
    ax = 150
    y0, y1 = 62, 430
    els.append(line(ax, y0, ax, y1, color=MUTED, sw=2.0))
    els.append(text(ax, y0 - 12, "час", size=11, color=MUTED))

    # віхи: (рік, підпис, суть)  розкладені зверху вниз
    nodes = [
        ("1858/66", "Трансатлантичний кабель", "крапки розмиваються;\nсуперечка Вайтгаус vs Томсон"),
        ("1874", "Розподільники Бодо", "два кінці йдуть у ногу\nгодинниковим механізмом"),
        ("1916", "Старт-стоп (Крам)", "відлік прив'язують\nдо події в сигналі"),
        ("1937", "PCM (Алек Рівз)", "зв'язок стає потоком бітів —\nCDR постає в чистому вигляді"),
        ("1962", "Магістраль T1 (Bell)", "репітер САМ добуває такт\nіз потоку — CDR у ділі"),
        ("1975", "Детектор Александера", "bang-bang: лише «рано / пізно»,\nгрубо, зате стійко"),
        ("1985", "Детектор Хоґґа", "лінійний: «наскільки» —\nтакт точно в центрі ока"),
    ]
    n = len(nodes)
    ys = [y0 + 26 + i * (y1 - y0 - 40) / (n - 1) for i in range(n)]

    for i, (yr, ttl, sub) in enumerate(nodes):
        yc = ys[i]
        # рік ліворуч від осі
        els.append(text(ax - 18, yc + 4, yr, size=12, color=INK, anchor="end", bold=True))
        # вузол на осі
        col = FIELD if i >= 5 else INK
        els.append(circle(ax, yc, 6, fill=BG, stroke=col, sw=2.4))
        # картка праворуч
        bx = ax + 26
        box, bw, bh = textbox(bx + 220, yc, ttl + "\n" + sub, size=11, pad=8,
                              fill=FILL, stroke=col, sw=1.6)
        els.append(box)
        # з'єднати вузол із карткою
        els.append(line(ax + 6, yc, bx + 220 - bw / 2, yc, color=MUTED, sw=1.2))

    render(os.path.join(IMG, "cdr-lineage.svg"), W, H, *els)


if __name__ == "__main__":
    fig_problem()
    fig_loop()
    fig_bangbang()
    fig_oversample()
    fig_drift()
    fig_lineage()
    print("OK: figures written to", IMG)
