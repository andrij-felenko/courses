# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

C0 = "#c0392b"   # фрагмент 0 — червоний
C1 = "#2457d6"   # фрагмент 1 — синій
C2 = "#27ae60"   # фрагмент 2 — зелений
C3 = "#e08a1e"   # фрагмент 3 — оранж
GRY = "#d7dde5"  # чужі дані в RAM
LT0 = "#fbe9e7"; LT1 = "#e8eefb"; LT2 = "#e6f6ec"; LT3 = "#fcf0dd"


def cbox(x, y, w, h, col, lite, l1, l2=None, ts=11):
    """Кольорова рамка з лівою смужкою і 1–2 рядками тексту всередині."""
    out = rect(x, y, w, h, fill=lite, stroke=col, sw=1.8, rx=6)
    out += rect(x, y, 7, h, fill=col, stroke=col, sw=0, rx=0)
    cx = x + 7 + (w - 7) / 2
    if l2 is None:
        out += text(cx, y + h / 2 + 4, l1, size=ts, color=INK, bold=True)
    else:
        out += text(cx, y + h / 2 - 4, l1, size=ts, color=INK, bold=True)
        out += text(cx, y + h / 2 + 13, l2, size=ts - 1, color=MUTED)
    return out


# ── Фіг. 1: один список перетворює розкидане на логічно суцільне ───────────────
# Логічний буфер суцільний (як його бачить програма) ↔ фізично він лежить
# розкиданими сторінками в RAM ↔ scatter-gather список тримає (адреса, довжина)
# кожного фрагмента в ЛОГІЧНОМУ порядку. Стрілки список→RAM перетинаються — саме
# так список «збирає» шматки, розкидані фізично в іншому порядку.
def fig_mapping():
    W, H = 900, 480
    p = []
    p.append(text(112, 60, "Логічний буфер", size=13, color=INK, bold=True))
    p.append(text(112, 76, "(що бачить програма)", size=10.5, color=MUTED))
    p.append(text(455, 60, "Scatter-gather список", size=13, color=INK, bold=True))
    p.append(text(455, 76, "(адреса · довжина)", size=10.5, color=MUTED))
    p.append(text(792, 60, "Фізична RAM", size=13, color=INK, bold=True))
    p.append(text(792, 76, "(де насправді лежить)", size=10.5, color=MUTED))

    cols = [C0, C1, C2, C3]
    lts = [LT0, LT1, LT2, LT3]
    lens = ["20 КБ", "16 КБ", "20 КБ", "12 КБ"]

    # A — логічний буфер: суцільний стовпчик із 4 фрагментів
    ax, aw = 58, 108
    ah = 74
    ay0 = 100
    for i in range(4):
        y = ay0 + i * ah
        p.append(cbox(ax, y, aw, ah, cols[i], lts[i], "фрагмент %d" % i, lens[i], ts=11))
    p.append(text(ax + aw / 2, ay0 - 6, "0", size=10, color=MUTED))
    p.append(text(ax + aw / 2, ay0 + 4 * ah + 16, "кінець", size=10, color=MUTED))

    # C — SG список: 4 записи, вирівняні по фрагментах
    lx, lw = 322, 232
    lh = 60
    ly = [104, 178, 252, 326]
    for i in range(4):
        p.append(cbox(lx, ly[i], lw, lh, cols[i], "#fbfdff",
                      "сегмент %d" % i, "A%s · %s" % ("₀₁₂₃"[i], lens[i]), ts=12))

    # B — фізична RAM: адресний простір із розкиданими фрагментами (інший порядок)
    bx, bw = 712, 118
    p.append(rect(bx - 6, 92, bw + 12, 348, fill="#f7f9fc", stroke="#c8d0da", sw=1.4, rx=8))
    # (фрагмент_індекс, y0, висота); None = чужі дані
    ram = [(None, 100, 34), (2, 138, 48), (None, 190, 26), (0, 220, 48),
           (3, 272, 40), (None, 316, 24), (1, 344, 48), (None, 396, 38)]
    ram_mid = {}
    for frag, y0, hh in ram:
        if frag is None:
            p.append(rect(bx, y0, bw, hh, fill=GRY, stroke="#c2cad4", sw=1.0, rx=4))
            p.append(text(bx + bw / 2, y0 + hh / 2 + 4, "чуже", size=9.5, color=MUTED))
        else:
            p.append(cbox(bx, y0, bw, hh, cols[frag], lts[frag], "фрагм. %d" % frag, ts=10.5))
            ram_mid[frag] = y0 + hh / 2

    # стрілки A → список (логічний порядок зберігається)
    for i in range(4):
        p.append(arrow(ax + aw + 6, ay0 + i * ah + ah / 2, lx - 6, ly[i] + lh / 2,
                       color=MUTED, sw=1.5))
    # стрілки список → RAM (перетинаються — список збирає розкидане)
    for i in range(4):
        p.append(arrow(lx + lw + 6, ly[i] + lh / 2, bx - 8, ram_mid[i],
                       color=cols[i], sw=1.8))

    # висновок унизу
    p.append(text(455, 462, "фізичний порядок ≠ логічний — список несе саме логічний",
                  size=11.5, color=INK, bold=True))

    render(os.path.join(OUT, "mapping.svg"), W, H, *p,
           title="Один список перетворює розкидане на логічно суцільне")


# ── Фіг. 2: gather і scatter — два напрямки того самого списку ─────────────────
# Gather: багато розкиданих шматків памʼяті зливаються в ОДИН вихідний потік до
# пристрою (writev, надсилання). Scatter: один вхідний потік розкладається по
# розкиданих шматках памʼяті (readv, приймання). Список той самий — напрям різний.
def fig_gather_scatter():
    W, H = 900, 430
    p = []

    def mem(x, y, col, lite):
        return cbox(x, y, 96, 42, col, lite, "шматок", ts=10.5)

    # ── ліва панель: GATHER ──
    p.append(rect(24, 66, 410, 330, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(text(229, 92, "Gather — зібрати", size=14, color=INK, bold=True))
    p.append(text(229, 110, "памʼять → пристрій", size=11, color=MUTED))
    mys = [140, 200, 260]
    mcol = [(C0, LT0), (C1, LT1), (C2, LT2)]
    for i in range(3):
        p.append(mem(52, mys[i], mcol[i][0], mcol[i][1]))
    # вузол списку
    p.append(circle(250, 200, 22, fill="#eef2f8", stroke=INK, sw=1.6))
    p.append(text(250, 204, "SG", size=12, color=INK, bold=True))
    for i in range(3):
        p.append(arrow(150, mys[i] + 21, 230, 200, color=mcol[i][0], sw=1.7))
    # пристрій
    p.append(rect(330, 172, 84, 56, fill="#eef7f0", stroke=FIELD, sw=1.6, rx=7))
    p.append(text(372, 196, "пристрій", size=11, color=INK, bold=True))
    p.append(text(372, 212, "1 потік", size=10, color=MUTED))
    p.append(arrow(272, 200, 326, 200, color=INK, sw=2.0))
    p.append(text(229, 356, "розкидані шматки → один потік", size=11, color=INK))
    p.append(text(229, 374, "writev · надсилання пакета", size=10.5, color=MUTED))

    # ── права панель: SCATTER ──
    p.append(rect(466, 66, 410, 330, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(text(671, 92, "Scatter — розсіяти", size=14, color=INK, bold=True))
    p.append(text(671, 110, "пристрій → памʼять", size=11, color=MUTED))
    # пристрій
    p.append(rect(486, 172, 84, 56, fill="#eef7f0", stroke=FIELD, sw=1.6, rx=7))
    p.append(text(528, 196, "пристрій", size=11, color=INK, bold=True))
    p.append(text(528, 212, "1 потік", size=10, color=MUTED))
    # вузол
    p.append(circle(650, 200, 22, fill="#eef2f8", stroke=INK, sw=1.6))
    p.append(text(650, 204, "SG", size=12, color=INK, bold=True))
    p.append(arrow(572, 200, 626, 200, color=INK, sw=2.0))
    for i in range(3):
        p.append(mem(748, mys[i], mcol[i][0], mcol[i][1]))
        p.append(arrow(672, 200, 744, mys[i] + 21, color=mcol[i][0], sw=1.7))
    p.append(text(671, 356, "один потік → розкидані шматки", size=11, color=INK))
    p.append(text(671, 374, "readv · приймання пакета", size=10.5, color=MUTED))

    render(os.path.join(OUT, "gather-scatter.svg"), W, H, *p,
           title="Той самий список, два напрямки: gather і scatter")


# ── Фіг. 3: три форми того самого списку ──────────────────────────────────────
# Той самий набір (адреса, довжина) живе трьома способами: масив (ПЗ індексує),
# звʼязний ланцюг (залізо йде за next до прапорця LAST), кільце (безперервний
# потік). Це і є звʼязок scatter-gather зі структурами даних.
def fig_forms():
    W, H = 920, 400
    p = []

    def panel(px, title, sub):
        out = [rect(px, 66, 280, 300, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10)]
        out.append(text(px + 140, 92, title, size=13.5, color=INK, bold=True))
        out.append(text(px + 140, 348, sub, size=10.5, color=MUTED))
        return out

    # P1 — масив
    p.extend(panel(20, "Масив дескрипторів", "ПЗ проходить індексом · iovec[]"))
    for i in range(3):
        x = 52 + i * 72
        p.append(rect(x, 190, 68, 54, fill="#eef2f8", stroke=INK, sw=1.5, rx=5))
        p.append(text(x + 34, 214, "d%d" % i, size=13, color=INK, bold=True))
        p.append(text(x + 34, 232, "адр·дов", size=10, color=MUTED))
        p.append(text(x + 34, 176, "i=%d" % i, size=10, color=MUTED))
    p.append(text(160, 268, "суцільний блок у памʼяті", size=10, color=MUTED))

    # P2 — ланцюг
    p.extend(panel(320, "Ланцюг (звʼязний список)", "залізо йде за next · LAST — кінець"))
    for i in range(3):
        x = 352 + i * 78
        p.append(rect(x, 190, 60, 54, fill="#eef2f8", stroke=INK, sw=1.5, rx=5))
        p.append(text(x + 30, 212, "d%d" % i, size=13, color=INK, bold=True))
        p.append(text(x + 30, 230, "next→", size=10, color=MUTED))
        if i < 2:
            p.append(arrow(x + 60, 217, x + 78, 217, color=NEG, sw=1.8))
    p.append(text(586, 217, "⊥", size=18, color=POS, bold=True))
    p.append(text(586, 238, "LAST", size=9, color=POS, bold=True))

    # P3 — кільце
    p.extend(panel(620, "Кільце (ring)", "безперервний потік · rx/tx мережівки"))
    cx, cy, r = 760, 216, 62
    import math
    pos = []
    for k in range(4):
        a = -math.pi / 2 + k * math.pi / 2
        pos.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    for k in range(4):
        x, y = pos[k]
        p.append(rect(x - 26, y - 18, 52, 36, fill="#eef2f8", stroke=INK, sw=1.4, rx=5))
        p.append(text(x, y + 5, "d%d" % k, size=12, color=INK, bold=True))
    for k in range(4):
        x1, y1 = pos[k]
        x2, y2 = pos[(k + 1) % 4]
        vx, vy = x2 - x1, y2 - y1
        L = (vx * vx + vy * vy) ** 0.5
        ux, uy = vx / L, vy / L
        p.append(arrow(x1 + ux * 30, y1 + uy * 22, x2 - ux * 30, y2 - uy * 22,
                       color=FIELD, sw=1.7))
    p.append(text(cx, cy + 4, "HEAD/TAIL", size=9, color=MUTED))

    render(os.path.join(OUT, "forms.svg"), W, H, *p,
           title="Три форми того самого списку сегментів")


# ── Фіг. 4: advance(n) — обрізати список після часткового пересилання ─────────
# Пристрій переслав n байтів. Операція advance(n) прибирає повністю зʼїдені
# сегменти, а той, у який n влучив, ОБРІЗАЄ: зсуває базу вперед і зменшує довжину.
# Це серце потокового вжитку (частковий send/recv по сокету).
def fig_advance():
    W, H = 860, 400
    p = []
    total = 1200.0
    x0, span = 96, 420          # байтова вісь
    n = 650

    def BX(b):
        return x0 + span * b / total

    # ── рядок «До» ──
    p.append(text(x0 - 8, 118, "До:", size=12, color=INK, bold=True, anchor="end"))
    segs = [(0, 300, C0, LT0), (300, 500, C1, LT1), (800, 400, C2, LT2)]
    y1 = 128
    for i, (b0, ln, col, lite) in enumerate(segs):
        x = BX(b0)
        w = span * ln / total
        p.append(cbox(x, y1, w, 52, col, lite, "сегм %d" % i, "%d Б" % ln, ts=11))
    p.append(text(x0 + span, 108, "усього 1200 Б", size=11, color=MUTED, anchor="end"))

    # маркер n=650
    mx = BX(n)
    p.append(line(mx, y1 - 16, mx, y1 + 64, color=POS, sw=2.2, dash="5,4"))
    p.append(text(mx, y1 - 22, "n = 650 Б переслано", size=11, color=POS, bold=True))

    # стрілка-перехід
    p.append(arrow(x0 + span / 2, 210, x0 + span / 2, 244, color=MUTED, sw=1.8))
    p.append(text(x0 + span / 2 + 96, 232, "advance(650)", size=11.5, color=INK, bold=True))

    # ── рядок «Після» ──
    p.append(text(x0 - 8, 300, "Після:", size=12, color=INK, bold=True, anchor="end"))
    y2 = 268
    # сегм0 — повністю зʼїдено (блідий, перекреслений)
    x = BX(0); w = span * 300 / total
    p.append(rect(x, y2, w, 52, fill="#f0f0f2", stroke="#c9ccd2", sw=1.4, rx=6))
    p.append(line(x + 8, y2 + 26, x + w - 8, y2 + 26, color="#b0b3ba", sw=2.0))
    p.append(text(x + w / 2, y2 + 70, "зʼїдено повністю", size=9.5, color=MUTED))
    # сегм1 — обрізано: лишилось 150 Б, база зсунута на +350
    x = BX(300); wfull = span * 500 / total
    cut = span * 350 / total
    p.append(rect(x, y2, cut, 52, fill="#f0f0f2", stroke="#c9ccd2", sw=1.2, rx=4))
    xr = x + cut; wr = wfull - cut
    p.append(cbox(xr, y2, wr, 52, C1, LT1, "150 Б", "A₁+350", ts=10.5))
    # сегм2 — цілий
    x = BX(800); w = span * 400 / total
    p.append(cbox(x, y2, w, 52, C2, LT2, "сегм 2", "400 Б", ts=11))

    p.append(text(x0 + span / 2, 358, "залишок списку: [150 Б][400 Б] = 550 Б",
                  size=12, color=INK, bold=True))

    render(os.path.join(OUT, "advance.svg"), W, H, *p,
           title="advance(n): зʼїдені сегменти геть, влучений — обрізати")


# ── Фіг. 5: sg_build — прохід сторінками зі злиттям фізично суміжних ──────────
# Буфер 10000 Б від НЕвирівняної vaddr=0x7F001F40 накриває 4 віртуальні сторінки.
# Кожна віддає свій шматок (хвіст 192 Б · 4096 · 4096 · край 1616 Б). Дві середні
# сторінки випадково лягли поряд ФІЗИЧНО (0x885000 і 0x886000) — і зливаються в
# ОДИН сегмент 8192 Б. Підсумок: 4 сторінки → 3 сегменти, сума байтів збережена.
def fig_build_coalesce():
    W, H = 980, 600
    p = []
    colx = [66, 286, 506, 726]
    colw = 190
    cx = [x + colw / 2 for x in colx]

    p.append(text(W / 2, 54, "віртуальний буфер:  vaddr = 0x7F001F40 · len = 10000 Б",
                  size=12, color=MUTED))

    # ── Ряд 1: віртуальні сторінки й шматок від кожної ──
    p.append(text(66, 86, "① сторінки, які накриває буфер (та скільки байтів бере з кожної)",
                  size=11.5, color=INK, bold=True, anchor="start"))
    vpage = ["0x7F001", "0x7F002", "0x7F003", "0x7F004"]
    vtake = ["хвіст 192 Б", "4096 Б", "4096 Б", "край 1616 Б"]
    pcol = [(C0, LT0), (C1, LT1), (C1, LT1), (C2, LT2)]   # 1 і 2 — той самий колір: зіллються
    for i in range(4):
        p.append(cbox(colx[i], 96, colw, 62, pcol[i][0], pcol[i][1],
                      "стор. " + vpage[i], vtake[i], ts=11.5))

    for i in range(4):
        p.append(arrow(cx[i], 162, cx[i], 179, color=MUTED, sw=1.5))

    # ── Ряд 2: фізична адреса цього байта = кадр + зсув ──
    p.append(text(66, 192, "② фізична адреса шматка:  page_phys(сторінка) + зсув",
                  size=11.5, color=INK, bold=True, anchor="start"))
    phys = ["0x00312F40", "0x00885000", "0x00886000", "0x00419000"]
    frame = ["кадр 0x00312000 + 0xF40", "кадр 0x00885000", "кадр 0x00886000", "кадр 0x00419000"]
    for i in range(4):
        p.append(cbox(colx[i], 202, colw, 62, pcol[i][0], "#fbfdff",
                      phys[i], frame[i], ts=11.5))

    # ── Ряд 3: рішення — новий сегмент чи злити з попереднім ──
    p.append(text(66, 292, "③ чи продовжує цей шматок попередній сегмент фізично?",
                  size=11.5, color=INK, bold=True, anchor="start"))
    p.append(text(cx[0], 322, "перший —", size=11, color=MUTED))
    p.append(text(cx[0], 338, "новий сегмент", size=11, color=INK, bold=True))

    p.append(text(cx[1], 322, "0x312F40+192 = 0x313000", size=9.5, color=MUTED))
    p.append(text(cx[1], 338, "≠ 0x885000 → новий", size=11, color=INK, bold=True))

    p.append(text(cx[2], 322, "0x885000+4096 = 0x886000", size=9.5, color=MUTED))
    p.append(text(cx[2], 338, "= 0x886000 → ЗЛИТИ ✓", size=11, color=FIELD, bold=True))

    p.append(text(cx[3], 322, "0x885000+8192 = 0x887000", size=9.5, color=MUTED))
    p.append(text(cx[3], 338, "≠ 0x419000 → новий", size=11, color=INK, bold=True))

    for i in range(4):
        p.append(arrow(cx[i], 350, cx[i], 379, color=(FIELD if i == 2 else MUTED), sw=1.6))

    # ── Ряд 4: готові сегменти (середній — злитий, удвічі ширший) ──
    p.append(text(66, 394, "④ список сегментів на виході", size=11.5, color=INK,
                  bold=True, anchor="start"))
    p.append(cbox(colx[0], 404, colw, 66, C0, LT0, "сегм 0 · 192 Б", "0x00312F40", ts=11.5))
    p.append(cbox(colx[1], 404, colx[2] + colw - colx[1], 66, C1, LT1,
                  "сегм 1 · 8192 Б  (дві сторінки злито)", "0x00885000", ts=11.5))
    p.append(cbox(colx[3], 404, colw, 66, C2, LT2, "сегм 2 · 1616 Б", "0x00419000", ts=11.5))

    # ── Підсумок ──
    p.append(text(W / 2, 512, "192 + 8192 + 1616 = 10000 Б — жодного байта не загублено",
                  size=12.5, color=INK, bold=True))
    p.append(text(W / 2, 538, "4 сторінки → 3 сегменти: злиття зменшує список задарма, "
                              "бо перевіряється до виділення слота", size=11, color=MUTED))
    p.append(text(W / 2, 564, "стеля без злиття: ⌈10000/4096⌉ + 1 = 4 сегменти "
                              "(неповний хвіст + неповний край)", size=11, color=MUTED))

    render(os.path.join(OUT, "build-coalesce.svg"), W, H, *p,
           title="sg_build: сторінка за сторінкою, зі злиттям фізично суміжних")


# ── Фіг. 6: advance як зсув ВИДУ, а не перекладання масиву ────────────────────
# Стаття показала advance по БАЙТАХ; тут — що діється в ПАМʼЯТІ. Масив сегментів
# не рухається взагалі: зʼїдені комірки просто лишаються позаду вида, влучена
# комірка правиться на місці, а вид (seg, n) зсувається праворуч. Звідси ціна
# O(зʼїдених), а не O(K), — і головна пастка: sg.seg уже не початок масиву.
def fig_view_slide():
    W, H = 920, 500
    p = []
    cellx = [170, 380, 590]
    cellw = 200

    # ── ДО ──
    p.append(text(36, 84, "ДО", size=13, color=INK, bold=True, anchor="start"))
    p.append(text(36, 102, "sg.n = 3", size=11, color=MUTED, anchor="start"))
    for i, nm in enumerate(["store[0]", "store[1]", "store[2]"]):
        p.append(text(cellx[i] + cellw / 2, 80, nm, size=10, color=MUTED))
    p.append(cbox(cellx[0], 88, cellw, 62, C0, LT0, "A₀ · 300 Б", ts=12))
    p.append(cbox(cellx[1], 88, cellw, 62, C1, LT1, "A₁ · 500 Б", ts=12))
    p.append(cbox(cellx[2], 88, cellw, 62, C2, LT2, "A₂ · 400 Б", ts=12))
    p.append(text(cellx[0] + 30, 172, "▲", size=13, color=POS, bold=True))
    p.append(text(cellx[0] + 30, 190, "sg.seg", size=11, color=POS, bold=True))
    p.append(text(cellx[2] + cellw + 24, 124, "усього 1200 Б", size=11,
                  color=MUTED, anchor="start"))

    # перехід
    p.append(line(36, 220, W - 36, 220, color="#dfe4ea", sw=1.2, dash="6,5"))
    p.append(text(W / 2, 248, "sg_advance(&sg, 650)", size=12.5, color=INK, bold=True))

    # ── ПІСЛЯ ──
    p.append(text(36, 300, "ПІСЛЯ", size=13, color=INK, bold=True, anchor="start"))
    p.append(text(36, 318, "sg.n = 2", size=11, color=MUTED, anchor="start"))
    # комірка 0 — поза видом, але фізично на місці
    p.append(rect(cellx[0], 304, cellw, 62, fill="#f0f0f2", stroke="#c9ccd2", sw=1.4, rx=6))
    p.append(text(cellx[0] + cellw / 2, 330, "A₀ · 300 Б", size=11.5, color="#9aa0ab"))
    p.append(text(cellx[0] + cellw / 2, 350, "лишилась у масиві — поза видом",
                  size=9.5, color="#9aa0ab"))
    # комірка 1 — розрізана НА МІСЦІ
    p.append(cbox(cellx[1], 304, cellw, 62, C1, LT1, "A₁+350 · 150 Б", "правлена на місці", ts=12))
    p.append(cbox(cellx[2], 304, cellw, 62, C2, LT2, "A₂ · 400 Б", "не чіпали", ts=12))
    p.append(text(cellx[1] + 30, 388, "▲", size=13, color=POS, bold=True))
    p.append(text(cellx[1] + 30, 406, "sg.seg", size=11, color=POS, bold=True))
    p.append(text(cellx[2] + cellw + 24, 340, "лишилось 550 Б", size=11,
                  color=MUTED, anchor="start"))

    # ── Висновки ──
    p.append(text(W / 2, 448, "масив не зрушив з місця · жодного memmove · ціна = "
                              "O(зʼїдених сегментів), не O(K)", size=12, color=INK, bold=True))
    p.append(text(W / 2, 474, "⚠ звідси й пастка: sg.seg більше НЕ початок масиву — "
                              "free(sg.seg) зруйнує купу", size=11.5, color=POS, bold=True))

    render(os.path.join(OUT, "view-slide.svg"), W, H, *p,
           title="sg_advance: масив стоїть, зсувається лише вид")


# ══════════════════════════════════════════════════════════════════════════════
# Фігури до вставки hist-scatter-gather-lineage.md
# ══════════════════════════════════════════════════════════════════════════════

# Ролі полів — колір за РОЛЛЮ, не за епохою: саме так видно, що скелет один.
R_ADDR = C1      # адреса — синій
R_LEN  = C2      # довжина — зелений
R_MORE = C0      # ознака «є ще» — червоний
R_ETC  = "#7a8699"  # службове
LT_ETC = "#eef1f5"


def _slot(x, y, w, h, col, lite, s, dashed=False, ts=10.5):
    """Поле запису: суцільна рамка — окреме поле; штрихова — поля НЕМА."""
    if dashed:
        out = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" '
               'fill="#ffffff" stroke="%s" stroke-width="1.4" '
               'stroke-dasharray="5,3"/>' % (x, y, w, h, col))
        out += text(x + w / 2, y + h / 2 + 4, s, size=ts, color=MUTED)
        return out
    out = rect(x, y, w, h, fill=lite, stroke=col, sw=1.6, rx=4)
    out += rect(x, y, 5, h, fill=col, stroke=col, sw=0, rx=0)
    out += text(x + 5 + (w - 5) / 2, y + h / 2 + 4, s, size=ts, color=INK, bold=True)
    return out


# ── Фіг.: родовід — чотири покоління, той самий скелет запису ─────────────────
# Колір полів — за РОЛЛЮ (адреса синя, довжина зелена, «є ще» червона). Читаючи
# картки зліва направо, видно повтор тієї самої трійці. Штрихова рамка = поля в
# цьому поколінні НЕМА (роль виконує щось інше) — саме тут видно, що System/360
# не винайшов chaining, а ВИОКРЕМИВ його в окремий біт.
def fig_lineage():
    W, H = 1020, 570
    p = []

    eras = [
        (25, C0, LT0, "1957–58",
         ["IBM 709 · 766 Data", "Synchronizer"],
         [(R_ETC, LT_ETC, "код операції", False),
          (R_ADDR, LT1, "Y-адреса", False),
          (R_LEN, LT2, "лічильник слів", False),
          (R_MORE, LT0, "«є ще» вшито в код", True)],
         ["лічильник вичерпано —", "канал бере наступну", "команду: IOCP «Proceed»"]),
        (275, C1, LT1, "1964",
         ["IBM System/360", "CCW"],
         [(R_ETC, LT_ETC, "код команди · 8 б", False),
          (R_ADDR, LT1, "адреса даних · 24 б", False),
          (R_LEN, LT2, "лічильник · 16 б", False),
          (R_MORE, LT0, "прапорець CD · біт 32", False)],
         ["CD = наступне CCW дає", "нову ділянку пам'яті", "для ТІЄЇ САМОЇ операції"]),
        (525, C2, LT2, "1982–83",
         ["4.2BSD", "struct iovec"],
         [(R_ETC, LT_ETC, "коду немає — йде ЦП", True),
          (R_ADDR, LT1, "iov_base", False),
          (R_LEN, LT2, "iov_len", False),
          (R_MORE, LT0, "«є ще» = iovcnt", True)],
         ["наступний елемент", "масиву; скільки лишилось —", "тримає uio_resid"]),
        (775, C3, LT3, "2007–08",
         ["Linux 2.6.24", "struct scatterlist"],
         [(R_ETC, LT_ETC, "offset у сторінці", False),
          (R_ADDR, LT1, "page_link → сторінка", False),
          (R_LEN, LT2, "length", False),
          (R_MORE, LT0, "біт 0 = SG_CHAIN", False)],
         ["звичайно sg++, а якщо", "біт 0 — стрибок за", "покажчиком на нову пачку"]),
    ]

    CW, CY, CH = 220, 118, 348

    # вісь часу
    p.append(line(25, 92, 995, 92, color=MUTED, sw=2))
    p.append(text(1000, 96, "→", size=15, color=MUTED, anchor="start"))

    for (cx0, col, lite, year, name, slots, nxt) in eras:
        mid = cx0 + CW / 2
        p.append(circle(mid, 92, 7, fill=col, stroke=col, sw=2))
        p.append(line(mid, 99, mid, CY, color=col, sw=1.4, dash="4,3"))

        p.append(rect(cx0, CY, CW, CH, fill="#ffffff", stroke=col, sw=1.8, rx=8))
        p.append(rect(cx0, CY, CW, 30, fill=lite, stroke=col, sw=0, rx=0))
        p.append(text(mid, CY + 21, year, size=13.5, color=col, bold=True))
        p.append(text(mid, CY + 52, name[0], size=12.5, color=INK, bold=True))
        p.append(text(mid, CY + 70, name[1], size=11.5, color=MUTED))
        p.append(line(cx0 + 14, CY + 84, cx0 + CW - 14, CY + 84, color="#dde3ea", sw=1.2))
        p.append(text(mid, CY + 104, "один запис списку:", size=10.5, color=MUTED))

        sy = CY + 116
        for i, (sc, sl, stext, dsh) in enumerate(slots):
            p.append(_slot(cx0 + 14, sy + i * 34, CW - 28, 29, sc, sl, stext, dashed=dsh))

        p.append(line(cx0 + 14, CY + 264, cx0 + CW - 14, CY + 264, color="#dde3ea", sw=1.2))
        p.append(text(mid, CY + 284, "як знайти наступний:", size=10.5, color=MUTED))
        for i, ln in enumerate(nxt):
            p.append(text(mid, CY + 302 + i * 15, ln, size=10, color=INK))

    # легенда ролей
    lg = [(R_ADDR, "адреса"), (R_LEN, "довжина"), (R_MORE, "ознака «є ще»")]
    lx = 240
    for col, lab in lg:
        p.append(rect(lx, 494, 13, 13, fill=col, stroke=col, sw=0, rx=2))
        p.append(text(lx + 20, 505, lab, size=11, color=INK, anchor="start"))
        lx += 34 + text_width(lab, 11) + 26
    p.append(text(768, 505, "штрихова рамка = такого поля немає",
                  size=10.5, color=MUTED, anchor="start"))

    p.append(text(W / 2, 538, "адреса · довжина · ознака «є ще» — скелет не змінився "
                              "за пів століття", size=13, color=INK, bold=True))
    p.append(text(W / 2, 558, "змінювалося лише те, ЧИЙ автомат іде списком: "
                              "канал → процесор → знову залізо", size=11.5, color=MUTED))

    render(os.path.join(OUT, "lineage.svg"), W, H, *p,
           title="Родовід списку сегментів: чотири покоління, один запис")


# ── Фіг.: біт «читай далі» — CCW 1964 проти page_link 2007 ────────────────────
# Головна теза вставки в одній картинці: обидві епохи знаходять у слові-описі
# вільний біт і кажуть ним «це ще не кінець». Нумерація бітів різна (IBM рахує
# зліва, Linux справа) — тож збіг НЕ в номері, а в самому ході думки.
def fig_ccw_vs_sg():
    W, H = 1020, 580
    p = []
    X0, X1 = 60, 980
    span = X1 - X0
    bit = span / 64.0

    def bx(b):
        return X0 + b * bit

    # ── 1964: CCW ──
    p.append(text(X0, 62, "1964 · IBM System/360 · CCW — подвійне слово, 64 біти",
                  size=12.5, color=C1, anchor="start", bold=True))
    p.append(text(X1, 62, "IBM нумерує біти ЗЛІВА", size=10.5, color=MUTED, anchor="end"))

    BY, BH = 76, 44
    fields = [
        (0, 8, LT_ETC, R_ETC, "код"),
        (8, 32, LT1, R_ADDR, "адреса даних"),
        (32, 37, LT0, R_MORE, ""),
        (37, 48, "#ffffff", "#c3ccd7", "—"),
        (48, 64, LT2, R_LEN, "лічильник"),
    ]
    for (b0, b1, fl, st, lab) in fields:
        x, w = bx(b0), (b1 - b0) * bit
        p.append(rect(x, BY, w, BH, fill=fl, stroke=st, sw=1.6, rx=2))
        if lab:
            p.append(text(x + w / 2, BY + BH / 2 + 4,
                          lab, size=fit_font(lab, w - 8, 11.5), color=INK, bold=True))
    for b in (0, 8, 32, 37, 48):
        p.append(text(bx(b), BY + BH + 16, str(b), size=10, color=MUTED))
    p.append(text(X1, BY + BH + 16, "63", size=10, color=MUTED))

    # виноска на поле прапорців
    ZX0, ZX1, ZY = 372, 768, 178
    p.append(line(bx(32), BY + BH, ZX0, ZY, color=R_MORE, sw=1.2, dash="4,3"))
    p.append(line(bx(37), BY + BH, ZX1, ZY, color=R_MORE, sw=1.2, dash="4,3"))
    p.append(text(W / 2, ZY - 10, "п'ять прапорців зблизька", size=11, color=MUTED))

    flags = [("CD", 32, True), ("CC", 33, False), ("SLI", 34, False),
             ("SKIP", 35, False), ("PCI", 36, False)]
    fw = (ZX1 - ZX0) / 5.0
    for i, (nm, bnum, hot) in enumerate(flags):
        x = ZX0 + i * fw
        p.append(rect(x, ZY, fw, 42, fill=LT0 if hot else "#f2f4f7",
                      stroke=R_MORE if hot else "#c3ccd7", sw=2 if hot else 1.4, rx=3))
        p.append(text(x + fw / 2, ZY + 27, nm, size=13 if hot else 11.5,
                      color=R_MORE if hot else MUTED, bold=True))
        p.append(text(x + fw / 2, ZY + 58, "біт %d" % bnum, size=9.5, color=MUTED))

    p.append(text(W / 2, ZY + 88, "CD (Chain Data) = «наступне CCW описує нову ділянку "
                                  "пам'яті для ТІЄЇ САМОЇ операції»",
                  size=12, color=R_MORE, bold=True))

    # ── 2007: page_link ──
    p.append(line(X0, 316, X1, 316, color="#e3e8ee", sw=1.2))
    p.append(text(X0, 352, "2007–08 · Linux · struct scatterlist — поле page_link, "
                           "машинне слово", size=12.5, color=C3, anchor="start", bold=True))
    p.append(text(X1, 352, "Linux нумерує біти СПРАВА", size=10.5, color=MUTED, anchor="end"))

    PY, PH = 368, 44
    p.append(rect(X0, PY, 800 - X0, PH, fill=LT1, stroke=R_ADDR, sw=1.6, rx=2))
    p.append(text((X0 + 800) / 2, PY + PH / 2 + 4,
                  "адреса struct page — вирівняна, тож молодші біти завжди нульові",
                  size=11.5, color=INK, bold=True))
    p.append(rect(800, PY, 90, PH, fill=LT3, stroke=C3, sw=1.8, rx=2))
    p.append(text(845, PY + PH / 2 + 6, "1", size=17, color=C3, bold=True))
    p.append(rect(890, PY, 90, PH, fill=LT0, stroke=R_MORE, sw=2.2, rx=2))
    p.append(text(935, PY + PH / 2 + 6, "0", size=17, color=R_MORE, bold=True))
    p.append(text(X0, PY + PH + 16, "…", size=10, color=MUTED))
    p.append(text(845, PY + PH + 16, "біт 1", size=9.5, color=MUTED))
    p.append(text(935, PY + PH + 16, "біт 0", size=9.5, color=MUTED))

    p.append(text(X0, 458, "біт 0 = SG_CHAIN (0x01) — у слові не сторінка, а покажчик "
                           "на наступну пачку записів",
                  size=11.5, color=R_MORE, anchor="start", bold=True))
    p.append(text(X0, 478, "біт 1 = SG_END (0x02) — цей запис у списку останній",
                  size=11.5, color=C3, anchor="start", bold=True))

    # ── теза ──
    p.append(rect(X0, 500, span, 62, fill="#fbfcfd", stroke="#d7dde5", sw=1.4, rx=8))
    p.append(text(W / 2, 524, "Різні машини, різні епохи, навіть біти нумеровано "
                              "в різні боки — і той самий хід:", size=12.5, color=INK, bold=True))
    p.append(text(W / 2, 548, "знайти у слові-описі вільний біт і сказати ним "
                              "«це ще не кінець, бери наступний»", size=12.5,
                  color=R_MORE, bold=True))

    render(os.path.join(OUT, "ccw-vs-sg.svg"), W, H, *p,
           title="Біт «читай далі»: 1964 і 2007")


if __name__ == "__main__":
    fig_mapping()
    fig_gather_scatter()
    fig_forms()
    fig_advance()
    fig_build_coalesce()
    fig_view_slide()
    fig_lineage()
    fig_ccw_vs_sg()
    print("OK figs")
