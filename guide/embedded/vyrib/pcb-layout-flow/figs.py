# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

COPPER = "#b87333"
COPDK  = "#8a561f"
CORE   = "#d8c98a"
MASK   = "#1f7a4d"
SILK   = "#f4f6f8"
STEP   = "#eef3fb"   # блок-крок конвеєра
STEPB  = "#4a6fa5"   # обрис блока
FAB    = "#fff4e0"   # завод/виробник
FABB   = "#c9820f"


# ── flow: конвеєр «від схеми до плати в руках» ──────────────────────────────
# Ідея: показати всю нитку одним поглядом. Схема (що з'єднати) → нетліст
# (машинний список зв'язків) → розводка (де фізично лягла мідь) → пакет
# файлів для заводу (гербери + свердло + BOM + CPL) → завод → плата.
# Це спинний хребет статті: читач має відразу вхопити, ЩО за чим іде.
def fig_flow():
    W, H = 820, 300
    p = []
    p.append(text(W/2, 30, "Від схеми до плати в руках: що за чим іде", size=16, bold=True))

    y = 120          # центр ряду блоків
    bw, bh = 118, 66
    xs = [78, 232, 386, 540]   # центри перших чотирьох блоків
    def block(cx, title, sub, fill=STEP, stroke=STEPB):
        b, w, h = textbox(cx, y, title + "\n" + sub, size=11, bold=False,
                          fill=fill, stroke=stroke, sw=1.6, pad=8, min_w=bw)
        # заголовок жирним — окремим рядком поверх
        return b
    # блоки з двома рядками: перший жирний-назва, другий — суть
    def block2(cx, name, sub, fill=STEP, stroke=STEPB, minw=bw):
        lines = [name, sub]
        w = max(minw, max(text_width(name, 11.5, True), text_width(sub, 10, False)) + 16)
        h = bh
        x0 = cx - w/2
        frag = rect(x0, y - h/2, w, h, fill=fill, stroke=stroke, sw=1.6, rx=7)
        frag += text(cx, y - 6, name, size=11.5, bold=True, color=INK)
        frag += text(cx, y + 13, sub, size=9.5, color=MUTED)
        return frag, w

    b1, w1 = block2(xs[0], "Схема", "що з'єднати")
    b2, w2 = block2(xs[1], "Нетліст", "список зв'язків")
    b3, w3 = block2(xs[2], "Розводка", "де лягла мідь")
    b4, w4 = block2(xs[3], "Пакет файлів", "гербери + BOM")
    for b in (b1, b2, b3, b4):
        p.append(b)

    # завод — окремим кольором, ширший
    fx = 700
    fw = 150
    p.append(rect(fx - fw/2, y - bh/2, fw, bh, fill=FAB, stroke=FABB, sw=1.8, rx=7))
    p.append(text(fx, y - 6, "Виробник", size=11.5, bold=True, color=INK))
    p.append(text(fx, y + 13, "фотоплотер → друк", size=9.5, color=MUTED))

    # стрілки між блоками
    centers = xs + [fx]
    widths  = [w1, w2, w3, w4, fw]
    for i in range(len(centers) - 1):
        x_from = centers[i] + widths[i]/2 + 4
        x_to   = centers[i+1] - widths[i+1]/2 - 4
        p.append(arrow(x_from, y, x_to, y, color=STEPB, sw=2.0))

    # підписи над стрілками: що саме передається
    labels = ["EDA", "розводить", "експорт", "замовлення"]
    for i in range(len(centers) - 1):
        xm = (centers[i] + widths[i]/2 + centers[i+1] - widths[i+1]/2) / 2
        p.append(text(xm, y - bh/2 - 10, labels[i], size=9, color=STEPB, italic=True))

    # плата на виході (праворуч від заводу — вниз)
    px = fx
    py = y + 92
    p.append(arrow(fx, y + bh/2 + 4, px, py - 24, color=FABB, sw=2.0))
    p.append(rect(px - 40, py - 20, 80, 42, fill=MASK, stroke="#155c3a", sw=1.6, rx=5))
    # кілька майданчиків на «платі»
    for gx in (px - 24, px, px + 24):
        p.append(circle(gx, py + 1, 5, fill=COPPER, stroke=COPDK, sw=1.0))
    p.append(text(px, py + 40, "готова плата", size=10, color="#155c3a", bold=True))

    # знизу — де межа: ліворуч ти, праворуч завод
    p.append(line(626, 78, 626, 250, color="#c9820f", sw=1.4, dash="5 5"))
    p.append(text(360, 250, "усе це робиш ти в EDA-програмі", size=10.5, color=STEPB))
    p.append(text(722, 250, "це робить завод", size=10.5, color=FABB))

    render(os.path.join(OUT, "flow.svg"), W, H, *p)


# ── gerber-layers: одна плата → пачка файлів (по файлу на шар) ───────────────
# Ідея: розвіяти головну плутанину новачка — гербер не «файл плати», а НАБІР
# файлів, по одному чорно-білому знімку на кожен фізичний шар. Ліворуч стос
# плати в розрізі; праворуч — окремі «знімки», що з нього виходять.
def fig_gerber_layers():
    W, H = 780, 430
    p = []
    p.append(text(W/2, 30, "Гербер — не один файл, а знімок кожного шару окремо", size=15, bold=True))

    # ---- ліворуч: двошарова плата стосом (спрощено) ----
    lx = 70
    lw = 150
    p.append(text(lx + lw/2, 66, "одна фізична плата", size=11.5, bold=True, color=INK))
    stack = [
        ("маска верх",  MASK,  "#155c3a"),
        ("мідь верх",   COPPER, COPDK),
        ("осердя FR-4", CORE,  "#b8a55f"),
        ("мідь низ",    COPPER, COPDK),
        ("маска низ",   MASK,  "#155c3a"),
    ]
    sy = 92
    for i, (nm, fl, st) in enumerate(stack):
        h = 34 if "осердя" in nm else 20
        p.append(rect(lx, sy, lw, h, fill=fl, stroke=st, sw=1.3, rx=2))
        p.append(text(lx + lw/2, sy + h/2 + 4, nm, size=9,
                      color="#ffffff" if fl in (MASK, COPPER) else "#7a6a2a", bold=True))
        sy += h + 4
    p.append(text(lx + lw/2, sy + 14, "плюс отвори наскрізь", size=9.5, color=MUTED))

    # велика стрілка «розкладається на»
    p.append(arrow(lx + lw + 12, 210, lx + lw + 66, 210, color=STEPB, sw=2.4))
    p.append(text(lx + lw + 40, 196, "дає", size=10, color=STEPB, italic=True))

    # ---- праворуч: колонка «знімків», кожен — окремий файл ----
    fx = 330
    fw = 380
    files = [
        (".GTL", "верхня мідь — доріжки згори", COPPER),
        (".GBL", "нижня мідь — доріжки знизу", COPPER),
        (".GTS", "верхня маска — де ЛишиТи лак", MASK),
        (".GBS", "нижня маска", MASK),
        (".GTO", "верхня шовкографія — написи", "#555b63"),
        (".DRL", "свердло — координати й діаметри отворів", INK),
    ]
    fy = 82
    rowh = 46
    for ext, desc, accent in files:
        # рамка-«знімок»: чорне на білому — так гербер і виглядає
        p.append(rect(fx, fy, fw, rowh - 8, fill="#ffffff", stroke="#cfd4da", sw=1.3, rx=5))
        # кольорова мітка-плашка з розширенням
        p.append(rect(fx + 6, fy + 5, 56, rowh - 18, fill=accent, stroke="none", sw=0, rx=4))
        p.append(text(fx + 6 + 28, fy + (rowh-8)/2 + 4, ext, size=11, color="#ffffff", bold=True))
        p.append(text(fx + 74, fy + (rowh-8)/2 + 4, desc, size=10.5, color=INK, anchor="start"))
        fy += rowh

    p.append(text(fx + fw/2, fy + 12,
                  "кожен файл — плаский чорно-білий малюнок одного шару; разом вони описують усю плату",
                  size=10, color=MUTED))

    render(os.path.join(OUT, "gerber-layers.svg"), W, H, *p)


# ── dfm-rules: три геометричні обмеження заводу ─────────────────────────────
# Ідея: показати, ЧОМУ не будь-яка розводка виготовна. Завод має скінченну
# роздільність: мінімальний зазор між міддю, мінімальне свердло й кільце
# навколо нього. Порушив — плата або дорожча, або бракована.
def fig_dfm_rules():
    W, H = 780, 300
    p = []
    p.append(text(W/2, 30, "Завод має скінченну роздільність: три головні межі", size=15, bold=True))

    y0 = 70
    colw = 250
    cxs = [140, 390, 640]

    # ---- 1. доріжка/зазор ----
    cx = cxs[0]
    p.append(text(cx, y0, "доріжка / зазор", size=12, bold=True, color=INK))
    ty = y0 + 30
    # дві доріжки з проміжком
    p.append(rect(cx - 70, ty, 44, 90, fill=COPPER, stroke=COPDK, sw=1.3, rx=2))
    p.append(rect(cx + 6,  ty, 44, 90, fill=COPPER, stroke=COPDK, sw=1.3, rx=2))
    # розмір ширини
    p.append(line(cx - 70, ty - 8, cx - 26, ty - 8, color=STEPB, sw=1.4))
    p.append(text(cx - 48, ty - 12, "ширина", size=9, color=STEPB))
    # розмір зазору
    p.append(line(cx - 26, ty + 100, cx + 6, ty + 100, color=POS, sw=1.4))
    p.append(text(cx - 10, ty + 114, "зазор", size=9, color=POS))
    p.append(text(cx, ty + 132, "типово ≥ 0.15 мм (6 mil)", size=9.5, color=MUTED))

    # ---- 2. свердло ----
    cx = cxs[1]
    p.append(text(cx, y0, "мінімальне свердло", size=12, bold=True, color=INK))
    ty = y0 + 74
    p.append(circle(cx, ty, 34, fill=COPPER, stroke=COPDK, sw=1.4))   # майданчик
    p.append(circle(cx, ty, 14, fill="#ffffff", stroke=COPDK, sw=1.2)) # отвір
    p.append(line(cx - 14, ty, cx + 14, ty, color=NEG, sw=1.4))
    p.append(text(cx, ty - 44, "діаметр отвору", size=9, color=NEG))
    p.append(text(cx, ty + 58, "типово ≥ 0.3 мм", size=9.5, color=MUTED))
    p.append(text(cx, ty + 74, "тонше — дорожче/лазер", size=9, color=MUTED))

    # ---- 3. кільце (annular ring) ----
    cx = cxs[2]
    p.append(text(cx, y0, "кільце навколо отвору", size=12, bold=True, color=INK))
    ty = y0 + 74
    p.append(circle(cx, ty, 34, fill=COPPER, stroke=COPDK, sw=1.4))
    p.append(circle(cx, ty, 18, fill="#ffffff", stroke=COPDK, sw=1.2))
    # показати кільце-обід стрілкою
    p.append(line(cx + 18, ty, cx + 34, ty, color=FIELD, sw=2.2))
    p.append(text(cx, ty - 44, "annular ring — обід міді", size=9, color=FIELD))
    p.append(text(cx, ty + 58, "мідь мусить лишитися", size=9.5, color=MUTED))
    p.append(text(cx, ty + 74, "навколо просвердленого", size=9, color=MUTED))

    # роздільники
    p.append(line(265, y0 - 8, 265, H - 20, color="#dde1e6", sw=1.2, dash="5 5"))
    p.append(line(515, y0 - 8, 515, H - 20, color="#dde1e6", sw=1.2, dash="5 5"))

    render(os.path.join(OUT, "dfm-rules.svg"), W, H, *p)


# ── photoplotter: чому гербер такий, який є ─────────────────────────────────
# Ідея (вставка hist): формат — закам'янілий протокол керування ВЕКТОРНИМ
# фотоплотером. Верстат мав набір діафрагм (отворів різної форми), обирав
# одну, переміщався в координату й «спалахував» майданчик або вів доріжку.
# Звідси в гербері досі «діафрагми» (D-коди) і «спалахи», хоч механіки давно
# нема. Показуємо: барабан діафрагм → промінь крізь обрану → плівка з малюнком.
def fig_photoplotter():
    W, H = 780, 340
    LAMP = "#f4b400"      # промінь світла
    FILM = "#20252b"      # фотоплівка (темна)
    p = []
    p.append(text(W/2, 30, "Векторний фотоплотер: звідки в гербері «діафрагми» й «спалахи»",
                  size=14.5, bold=True))

    # ---- ліворуч: джерело світла ----
    sx = 70
    sy = 150
    p.append(circle(sx, sy, 22, fill=LAMP, stroke="#b8860b", sw=1.6))
    p.append(text(sx, sy + 40, "джерело", size=10, color=INK, bold=True))
    p.append(text(sx, sy + 55, "світла", size=10, color=INK, bold=True))

    # ---- барабан діафрагм: набір отворів різної форми ----
    dx = 240
    dtop = 78
    p.append(text(dx, dtop - 12, "барабан діафрагм (apertures)", size=11, bold=True, color=INK))
    p.append(rect(dx - 46, dtop, 92, 150, fill="#cfd4da", stroke="#8a9099", sw=1.6, rx=8))
    # чотири діафрагми-отвори різної форми у барабані
    shapes_y = [dtop + 24, dtop + 60, dtop + 96, dtop + 132]
    # коло (обрана — підсвічена)
    p.append(circle(dx, shapes_y[0], 11, fill="#ffffff", stroke=POS, sw=2.2))
    p.append(text(dx + 34, shapes_y[0] + 4, "D10", size=9, color=POS, anchor="start", bold=True))
    # квадрат
    p.append(rect(dx - 9, shapes_y[1] - 9, 18, 18, fill="#ffffff", stroke="#4a4f57", sw=1.4, rx=1))
    p.append(text(dx + 34, shapes_y[1] + 4, "D11", size=9, color=MUTED, anchor="start"))
    # прямокутник
    p.append(rect(dx - 14, shapes_y[2] - 6, 28, 12, fill="#ffffff", stroke="#4a4f57", sw=1.4, rx=1))
    p.append(text(dx + 34, shapes_y[2] + 4, "D12", size=9, color=MUTED, anchor="start"))
    # смужка (доріжка)
    p.append(rect(dx - 16, shapes_y[3] - 3, 32, 6, fill="#ffffff", stroke="#4a4f57", sw=1.4, rx=3))
    p.append(text(dx + 34, shapes_y[3] + 4, "D13", size=9, color=MUTED, anchor="start"))
    p.append(text(dx, dtop + 150 + 16, "обрано D10 (коло)", size=9.5, color=POS))

    # промінь: джерело → крізь обрану діафрагму → плівка
    p.append(line(sx + 22, sy, dx - 46, dtop + 24, color=LAMP, sw=2.4))
    p.append(arrow(dx + 46, dtop + 24, 520, dtop + 24, color=LAMP, sw=2.4))
    p.append(text((dx + 46 + 520) / 2, dtop + 14, "промінь крізь діафрагму", size=9,
                  color="#b8860b", italic=True))

    # ---- праворуч: фотоплівка з уже «намальованим» шаром ----
    fx = 540
    fw = 170
    fy = 82
    fh = 160
    p.append(rect(fx, fy, fw, fh, fill=FILM, stroke="#0d0f12", sw=1.6, rx=6))
    p.append(text(fx + fw/2, fy - 12, "фотоплівка — негатив шару", size=11, bold=True, color=INK))
    # майданчики (спалахи) — світлі кола/прямокутники на темному
    p.append(circle(fx + 40, fy + 40, 9, fill="#eef3fb", stroke="none", sw=0))
    p.append(circle(fx + 40, fy + 120, 9, fill="#eef3fb", stroke="none", sw=0))
    p.append(rect(fx + 110, fy + 32, 20, 16, fill="#eef3fb", stroke="none", sw=0, rx=1))
    p.append(rect(fx + 112, fy + 112, 16, 16, fill="#eef3fb", stroke="none", sw=0, rx=1))
    # доріжка (веде лінію) — світла смужка між майданчиками
    p.append(line(fx + 40, fy + 40, fx + 120, fy + 40, color="#eef3fb", sw=5))
    p.append(line(fx + 40, fy + 120, fx + 120, fy + 120, color="#eef3fb", sw=5))
    p.append(text(fx + fw/2, fy + fh + 16, "«спалах» = майданчик · «лінія» = доріжка",
                  size=9, color=MUTED))

    render(os.path.join(OUT, "photoplotter.svg"), W, H, *p)


# ── gerber-eras: три епохи формату, що лишався собою ────────────────────────
# Ідея (вставка hist): показати дорослішання гербера як стрічку часу.
# 1) Standard Gerber (RS-274-D, 1980): малюнок + ОКРЕМА таблиця діафрагм → баг.
# 2) RS-274X (1998): опис форм УСЕРЕДИНІ файла → один самодостатній файл.
# 3) Gerber X2 (2014): + атрибути (сенс шарів, нетліст), а не лише геометрія.
def fig_gerber_eras():
    W, H = 800, 300
    OK   = "#27ae60"
    BAD  = "#c0392b"
    p = []
    p.append(text(W/2, 30, "Три епохи гербера — той самий синтаксис, дедалі більше сенсу",
                  size=14.5, bold=True))

    # стрічка часу
    p.append(line(60, 78, 740, 78, color="#c9cfd6", sw=2.0))
    for x in (150, 400, 650):
        p.append(circle(x, 78, 5, fill=STEPB, stroke="none", sw=0))

    cols = [
        (150, "Standard Gerber", "RS-274-D · 1980",
         ["малюнок шару", "+ ОКРЕМА таблиця", "  діафрагм"],
         "форми в окремому файлі —\nлегко переплутати → брак", BAD),
        (400, "Extended Gerber", "RS-274X · 1998",
         ["малюнок шару", "+ опис форм", "  УСЕРЕДИНІ файла"],
         "один самодостатній файл —\nтаблиця не губиться", OK),
        (650, "Gerber X2", "2014",
         ["усе з RS-274X", "+ атрибути шарів", "+ дані нетлісту"],
         "не лише геометрія, а й СЕНС:\nщо за шар, що з чим з'єднати", OK),
    ]
    boxy = 100
    boxw = 210
    boxh = 96
    for cx, name, ver, lines, note, notecol in cols:
        p.append(text(cx, 66, ver, size=9.5, color=STEPB, italic=True))
        x0 = cx - boxw/2
        p.append(rect(x0, boxy, boxw, boxh, fill=STEP, stroke=STEPB, sw=1.6, rx=7))
        p.append(text(cx, boxy + 20, name, size=12, bold=True, color=INK))
        ly = boxy + 42
        for ln in lines:
            anch = "middle"
            p.append(text(cx, ly, ln, size=9.5, color=INK))
            ly += 15
        # примітка-висновок під блоком (двома рядками)
        ny = boxy + boxh + 18
        for j, seg in enumerate(note.split("\n")):
            p.append(text(cx, ny + j * 13, seg, size=9, color=notecol))

    render(os.path.join(OUT, "gerber-eras.svg"), W, H, *p)


# ── etch-undercut: чому доріжка виходить вужчою за малюнок ───────────────────
# Ідея (detailed): ізотропне травлення гризе мідь у всі боки. Поки доходить
# донизу (товщина t), устигає підгризти вбік під захист — це підтрав u. Готова
# доріжка звужується на 2u і має трапецієподібний переріз. Показуємо два стани:
# зверху малюнок на резисті (прямокутник), знизу — готову трапецію з підтравом.
def _poly(points, fill, stroke, sw=1.4):
    d = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (d, fill, stroke, sw))

def fig_etch_undercut():
    W, H = 780, 400
    RESIST = "#8e7cc3"   # фоторезист (захист)
    p = []
    p.append(text(W/2, 30, "Ізотропне травлення підгризає мідь — доріжка виходить вужчою",
                  size=14.5, bold=True))

    # ---- горішній стан: малюнок на резисті (ще не травлено) ----
    ty = 92
    p.append(text(180, ty - 16, "малюнок: мідь під захистом", size=11.5, bold=True, color=INK))
    # осердя
    p.append(rect(90, ty + 46, 300, 16, fill=CORE, stroke="#b8a55f", sw=1.2, rx=1))
    p.append(text(240, ty + 58, "ізолятор (FR-4)", size=8.5, color="#7a6a2a"))
    # мідь суцільним прямокутником
    cu_x0, cu_w = 190, 100
    p.append(rect(cu_x0, ty + 16, cu_w, 30, fill=COPPER, stroke=COPDK, sw=1.3, rx=1))
    p.append(text(cu_x0 + cu_w/2, ty + 35, "мідь", size=9, color="#ffffff", bold=True))
    # резист зверху
    p.append(rect(cu_x0, ty + 6, cu_w, 10, fill=RESIST, stroke="#5b4a8f", sw=1.1, rx=1))
    p.append(text(cu_x0 + cu_w/2, ty - 2, "захист (резист)", size=8.5, color="#5b4a8f"))
    # розмір ширини малюнка
    p.append(line(cu_x0, ty + 52, cu_x0 + cu_w, ty + 52, color=STEPB, sw=1.2))
    p.append(text(cu_x0 + cu_w/2, ty + 74, "ширина малюнка", size=9, color=STEPB))

    # стрілка «травимо»
    p.append(arrow(240, ty + 84, 240, ty + 116, color=NEG, sw=2.2))
    p.append(text(300, ty + 102, "травник гризе у всі боки", size=9.5, color=NEG, italic=True))

    # ---- нижній стан: готова доріжка (трапеція + підтрав) ----
    by = 250
    p.append(text(180, by - 8, "готово: трапеція, вужча зверху", size=11.5, bold=True, color=INK))
    # осердя
    p.append(rect(90, by + 60, 300, 16, fill=CORE, stroke="#b8a55f", sw=1.2, rx=1))
    # трапеція міді: широка внизу (біля осердя), вужча вгорі
    base_l, base_r = 190, 290           # низ (як був малюнок)
    top_l, top_r   = 202, 278           # верх (звужено на підтрав з боків)
    p.append(_poly([(base_l, by + 60), (base_r, by + 60),
                    (top_r, by + 30), (top_l, by + 30)],
                   fill=COPPER, stroke=COPDK, sw=1.4))
    # пунктир — де МАЛА б бути мідь (первісний контур), щоб видно підтрав
    p.append(line(base_l, by + 30, base_l, by + 60, color=POS, sw=1.2, dash="3 3"))
    p.append(line(base_r, by + 30, base_r, by + 60, color=POS, sw=1.2, dash="3 3"))
    # підтрав з боку (від пунктиру до реального верху)
    p.append(line(base_l, by + 22, top_l, by + 22, color=POS, sw=1.6))
    p.append(text(base_l - 4, by + 14, "підтрав u", size=9, color=POS, anchor="end"))
    p.append(line(base_r, by + 22, top_r, by + 22, color=POS, sw=1.6))
    p.append(text(base_r + 4, by + 14, "u", size=9, color=POS, anchor="start"))
    # ширина зверху (реальна готова)
    p.append(line(top_l, by + 84, top_r, by + 84, color=FIELD, sw=1.4))
    p.append(text((top_l+top_r)/2, by + 100, "готова ширина = малюнок − 2u", size=9, color=FIELD))

    # ---- формула праворуч ----
    fx = 470
    p.append(rect(fx, 90, 280, 210, fill=STEP, stroke=STEPB, sw=1.4, rx=8))
    p.append(text(fx + 140, 116, "коефіцієнт травлення", size=12, bold=True, color=INK))
    p.append(text(fx + 140, 146, "EF = t / u", size=13, color=INK, bold=True))
    p.append(text(fx + 140, 168, "u = t / EF   (підтрав з боку)", size=10.5, color=MUTED))
    p.append(line(fx + 20, 182, fx + 260, 182, color="#c9cfd6", sw=1.0))
    p.append(text(fx + 140, 204, "мідь 1oz: t ≈ 35 мкм, EF = 3", size=10.5, color=INK))
    p.append(text(fx + 140, 226, "u ≈ 11.7 мкм · 2u ≈ 23 мкм", size=10.5, color=POS))
    p.append(text(fx + 140, 252, "мідь 2oz (70 мкм): 2u ≈ 47 мкм", size=10.5, color=INK))
    p.append(text(fx + 140, 278, "товща мідь → більший підтрав", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "etch-undercut.svg"), W, H, *p)


# ── annular-ring: чому майданчик мусить бути з запасом більший за отвір ──────
# Ідея (detailed): свердло приходить не в геометричний центр (похибка
# суміщення r). Ліворуч ідеал (кільце рівне), праворуч реальність (зсув з'їв
# кільце з одного боку — breakout). Праворуч — формула мінімального майданчика.
def fig_annular_ring():
    W, H = 780, 340
    p = []
    p.append(text(W/2, 30, "Кільце навколо отвору: майданчик мусить пережити зсув свердла",
                  size=14.5, bold=True))

    padR = 46
    holeR = 24
    cy = 150

    # ---- ліворуч: ідеал ----
    cx = 150
    p.append(text(cx, 74, "ідеал: отвір у центрі", size=11.5, bold=True, color=INK))
    p.append(circle(cx, cy, padR, fill=COPPER, stroke=COPDK, sw=1.5))    # майданчик
    p.append(circle(cx, cy, holeR, fill="#ffffff", stroke=COPDK, sw=1.3)) # отвір
    # рівне кільце — стрілка обода
    p.append(line(cx + holeR, cy, cx + padR, cy, color=FIELD, sw=2.4))
    p.append(text(cx, cy + padR + 22, "кільце рівне з усіх боків", size=9.5, color=FIELD))

    # ---- праворуч: реальність (зсув) ----
    cx = 400
    off = 20   # зсув отвору
    p.append(text(cx, 74, "реальність: свердло зсунулось", size=11.5, bold=True, color=INK))
    p.append(circle(cx, cy, padR, fill=COPPER, stroke=COPDK, sw=1.5))         # майданчик
    p.append(circle(cx + off, cy, holeR, fill="#ffffff", stroke=POS, sw=1.6))  # зсунутий отвір
    # показати зсув
    p.append(line(cx, cy, cx + off, cy, color=POS, sw=1.6))
    p.append(text(cx + off/2, cy - 8, "зсув r", size=9, color=POS))
    # з боку зсуву кільце з'їдено
    p.append(text(cx + padR + 6, cy + 4, "тут кільце", size=9, color=POS, anchor="start"))
    p.append(text(cx + padR + 6, cy + 18, "з'їдено → розрив", size=9, color=POS, anchor="start"))
    p.append(text(cx, cy + padR + 22, "breakout: контакт втрачено", size=9.5, color=POS))

    # ---- формула праворуч ----
    fx = 556
    p.append(rect(fx, 96, 210, 200, fill=STEP, stroke=STEPB, sw=1.4, rx=8))
    p.append(text(fx + 105, 120, "мінімальний майданчик", size=11.5, bold=True, color=INK))
    p.append(text(fx + 105, 148, "D_pad ≥ D_отв", size=11, color=INK, bold=True))
    p.append(text(fx + 105, 168, "+ 2·кільце + 2r + Δd", size=11, color=INK))
    p.append(line(fx + 16, 182, fx + 194, 182, color="#c9cfd6", sw=1.0))
    p.append(text(fx + 105, 204, "отвір 0.3 · кільце 0.15", size=10, color=MUTED))
    p.append(text(fx + 105, 222, "r 0.05 · Δd 0.05", size=10, color=MUTED))
    p.append(text(fx + 105, 250, "D_pad ≥ 0.75 мм", size=12, color=POS, bold=True))
    p.append(text(fx + 105, 276, "«удвічі більший» — замало", size=9.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "annular-ring.svg"), W, H, *p)


# ── rotation-convention: дві домовленості про «нуль» → деталь боком ──────────
# Ідея (detailed): кут 0° — домовленість, і їх дві. У бібліотеці деталь при 0°
# дивиться pin1 угору; автомат чекає pin1 ліворуч. Різниця стала (90°), тож усі
# деталі корпусу повертаються однаково не туди. Показуємо два корпуси поряд.
def fig_rotation_convention():
    W, H = 780, 330
    CHIP = "#3a3f47"
    PIN1 = "#f4b400"
    p = []
    p.append(text(W/2, 30, "Кут «0°» — домовленість, і їх дві: звідси деталь боком",
                  size=14.5, bold=True))

    def chip(cx, cy, pin1_at, label):
        # корпус-прямокутник із крапкою pin1 у заданому кутку
        w, h = 78, 54
        p.append(rect(cx - w/2, cy - h/2, w, h, fill=CHIP, stroke="#1a1d22", sw=1.4, rx=4))
        # ніжки з боків (декоративно)
        for i in range(3):
            yy = cy - 16 + i * 16
            p.append(line(cx - w/2 - 8, yy, cx - w/2, yy, color="#9aa0a8", sw=2.2))
            p.append(line(cx + w/2, yy, cx + w/2 + 8, yy, color="#9aa0a8", sw=2.2))
        # крапка pin1
        offs = {"tl": (-w/2 + 12, -h/2 + 12), "bl": (-w/2 + 12, h/2 - 12)}
        dx, dy = offs[pin1_at]
        p.append(circle(cx + dx, cy + dy, 6, fill=PIN1, stroke="#b8860b", sw=1.2))
        p.append(text(cx, cy + h/2 + 20, label, size=10, color=INK, bold=True))

    # ---- ліворуч: бібліотека (pin1 угорі-ліворуч) ----
    lx = 180
    p.append(text(lx, 84, "твоя бібліотека @ 0°", size=12, bold=True, color=STEPB))
    chip(lx, 160, "tl", "pin 1 — угорі")
    p.append(text(lx, 236, "так ти намалював посадкове місце", size=9.5, color=MUTED))

    # ---- посередині: різниця ----
    mx = 390
    p.append(text(mx, 150, "≠", size=30, bold=True, color=POS))
    p.append(text(mx, 182, "різниця", size=10, color=POS))
    p.append(text(mx, 196, "стала 90°", size=10, color=POS, bold=True))

    # ---- праворуч: автомат (pin1 унизу-ліворуч) ----
    rx = 600
    p.append(text(rx, 84, "автомат чекає @ 0°", size=12, bold=True, color=FABB))
    chip(rx, 160, "bl", "pin 1 — ліворуч")
    p.append(text(rx, 236, "його нульова орієнтація (IPC-7351)", size=9.5, color=MUTED))

    # висновок унизу
    p.append(line(60, 268, 720, 268, color="#dde1e6", sw=1.0))
    p.append(text(W/2, 290, "конвенції розійшлись на 90° → УСІ деталі цього корпусу стануть на 90° не туди",
                  size=10.5, color=INK))
    p.append(text(W/2, 310, "помилка систематична — ловиться на одному примірнику до масового пуску",
                  size=9.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "rotation-convention.svg"), W, H, *p)


# ── cam-pipeline: що CAM-система заводу робить із пакетом ────────────────────
# Ідея (detailed): онлайн-завод не «друкує файл» — CAM осмислює пакет. Ланцюг
# кроків: зіставити шари → контур → зшити свердло → DFM → BOM/CPL. Кожен крок
# споживає свій файл із пакета й повертає ок/попередження. Показуємо конвеєр
# із підписом «який файл живить цей крок».
def fig_cam_pipeline():
    W, H = 800, 360
    WARN = "#e08600"
    p = []
    p.append(text(W/2, 30, "Перші хвилини на заводі: що CAM робить із твоїм пакетом",
                  size=15, bold=True))

    steps = [
        ("Зіставити шари", "який гербер\nякий шар", "гербери (.GTL…) / X2"),
        ("Знайти контур", "де межа\nплати", "файл контуру (.GML)"),
        ("Зшити свердло", "отвори в\nмайданчики", "Excellon (.DRL)"),
        ("Прогнати DFM", "проти можли-\nвостей заводу", "уся геометрія"),
        ("Готувати зборку", "що паяти,\nкуди й як", "BOM + CPL"),
    ]
    n = len(steps)
    bw = 130
    gap = 14
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    by = 120
    bh = 74

    cxs = []
    for i, (name, sub, feed) in enumerate(steps):
        x = x0 + i * (bw + gap)
        cx = x + bw/2
        cxs.append((cx, x, x + bw))
        p.append(rect(x, by, bw, bh, fill=STEP, stroke=STEPB, sw=1.6, rx=7))
        p.append(text(cx, by + 20, name, size=11, bold=True, color=INK))
        for j, seg in enumerate(sub.split("\n")):
            p.append(text(cx, by + 40 + j * 14, seg, size=9, color=MUTED))
        # який файл живить крок — під блоком
        p.append(text(cx, by + bh + 22, "живить:", size=8.5, color=FABB, italic=True))
        p.append(text(cx, by + bh + 36, feed, size=9, color=FABB))
        # результат — над блоком
        p.append(text(cx, by - 12, "→ ок / попередження", size=8.5, color=WARN))

    # стрілки між блоками
    for i in range(n - 1):
        p.append(arrow(cxs[i][2] + 2, by + bh/2, cxs[i+1][1] - 2, by + bh/2,
                       color=STEPB, sw=2.0))

    # вхід ліворуч і вихід праворуч
    p.append(text(x0 - 4, by + bh/2, "ZIP", size=12, color=INK, bold=True, anchor="end"))
    p.append(arrow(x0 - 40, by + bh/2, x0 - 6, by + bh/2, color=INK, sw=1.8))

    # висновок унизу
    p.append(line(60, 300, 740, 300, color="#dde1e6", sw=1.0))
    p.append(text(W/2, 324,
                  "кожен файл пакета = вхід одного кроку CAM; прибери файл — крок спіткнеться",
                  size=10.5, color=INK))
    p.append(text(W/2, 344,
                  "ціна й попередження на сайті — це і є результат прогону через CAM",
                  size=9.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "cam-pipeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_flow()
    fig_gerber_layers()
    fig_dfm_rules()
    fig_photoplotter()
    fig_gerber_eras()
    fig_etch_undercut()
    fig_annular_ring()
    fig_rotation_convention()
    fig_cam_pipeline()
    print("figs done:", os.listdir(OUT))
