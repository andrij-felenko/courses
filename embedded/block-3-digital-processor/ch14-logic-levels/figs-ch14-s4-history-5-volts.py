# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для історичної вставки §3.1.4i — «Чому саме 5 вольтів:
спадщина TTL і довгий шлях униз до 3.3 і 1.8 В».

Самодостатній скрипт (НЕ чіпає головний figs.py розділу). Чистий Python без
залежностей. Вивід → ./img/ тієї ж папки розділу.

Стиль (AUTHORING §9): білий фон; HIGH/'1'/+ червоний, LOW/'0'/− синій;
«дійсне/безпечне/запас» — зелене; «небезпека/спотворення» — бурштин; стрілки
через marker; шрифт sans-serif. Підписи нумеруються «Рис. 3.1.4i.k» у тексті.

Три фігури:
  fig-14-4i-1-timeline.svg  — хронологія напруги: 5 В тримаються, тоді спуск
  fig-14-4i-2-why-five.svg  — бюджет переходів усередині TTL: чому ~5 В
  fig-14-4i-3-down.svg      — дві сили вниз: пробій ізолятора і енергія V²
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра (та сама, що в figs.py розділу) ─────────────────────────────────
RED    = "#c0271e"   # HIGH / '1' / +
BLUE   = "#1f47b5"   # LOW / '0' / −
GREEN  = "#1f8a3b"   # дійсне / запас / безпечно
INK    = "#1b1b1b"   # основний текст/лінії
GREY   = "#8a8a8a"   # допоміжне
FAINT  = "#e4e4e4"   # дуже бліде тло
AMBER  = "#caa24a"   # небезпека / спотворення / енергія
COPPER = "#b5742e"   # реле / мідь / BJT
FONT   = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", AMBER: "aAmber"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def polygon(points, fill="none", stroke=INK, w=2, opacity=None):
    op = f' fill-opacity="{opacity}"' if opacity is not None else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return (f'<polygon points="{pts}" fill="{fill}"{op} stroke="{stroke}" '
            f'stroke-width="{w}"/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ═════════════════════════════════════════════════════════════════════════════
# Рис. 3.1.4i.1 — хронологія: 5 В тримаються десятиліттями, далі спуск сходинками
# ═════════════════════════════════════════════════════════════════════════════
def fig_timeline():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 32, "Біографія однієї напруги: 5 В тримаються — тоді швидкий спуск",
              size=18, color=INK, anchor="middle", weight="bold")

    # осі
    x0, x1 = 95, 820          # вісь часу
    yb = 392                  # базова лінія (0 В)
    ytop = 70                 # верх поля графіка
    # роки 1960..2010 → x
    yr0, yr1 = 1960, 2012

    def X(year):
        return x0 + (year - yr0) / (yr1 - yr0) * (x1 - x0)

    # вольти 0..6 → y
    vmax = 6.0

    def Y(v):
        return yb - v / vmax * (yb - ytop)

    # горизонтальні рівні-напруги (бліді)
    for v, lab in [(5.0, "5.0 В"), (3.3, "3.3 В"), (2.5, "2.5 В"),
                   (1.8, "1.8 В"), (1.2, "1.2 В")]:
        s += line(x0, Y(v), x1, Y(v), FAINT, 1)
        s += text(x0 - 10, Y(v) + 4, lab, size=12, color=GREY, anchor="end")

    # вісь часу + позначки років
    s += arrow(x0, yb, x1 + 12, yb, INK, 2)
    s += text(x1 + 16, yb + 5, "рік", size=13, color=INK)
    for year in range(1960, 2011, 10):
        s += line(X(year), yb, X(year), yb + 5, INK, 1.5)
        s += text(X(year), yb + 22, str(year), size=12, color=INK, anchor="middle")

    # вісь напруги
    s += arrow(x0, yb, x0, ytop - 6, INK, 2)
    s += text(x0 - 8, ytop - 12, "В", size=13, color=INK, anchor="end")

    # ── крива напруги живлення логіки у часі (ступінчаста) ──
    pts = [
        (X(1962), Y(5.0)),
        (X(1992), Y(5.0)),   # 5 В панують ~30 років
        (X(1993), Y(3.3)),
        (X(1999), Y(3.3)),
        (X(2000), Y(2.5)),
        (X(2003), Y(2.5)),
        (X(2004), Y(1.8)),
        (X(2008), Y(1.8)),
        (X(2009), Y(1.2)),
        (X(2012), Y(1.2)),
    ]
    s += polyline(pts, RED, 3.2)
    # вузли
    for (xx, yy) in [pts[0], pts[1], pts[2], pts[4], pts[6], pts[8]]:
        s += circle(xx, yy, 4.5, RED, RED, 1)

    # ── підсвітити «плато 5 В» і «спуск» ──
    # плато
    s += line(X(1965), Y(5.0) - 30, X(1989), Y(5.0) - 30, GREEN, 2, dash="2,4")
    s += text((X(1965) + X(1989)) / 2, Y(5.0) - 38,
              "≈ 30 років незрушно — інерція стандарту",
              size=13, color=GREEN, anchor="middle", weight="bold")
    # спуск
    s += text(X(2004), Y(1.8) - 60, "спуск за роки:",
              size=13, color=BLUE, anchor="middle", weight="bold")
    s += text(X(2004), Y(1.8) - 44, "транзистори здрібніли,",
              size=12, color=BLUE, anchor="middle")
    s += text(X(2004), Y(1.8) - 28, "батареї зажадали економії",
              size=12, color=BLUE, anchor="middle")

    # ── підписи ключових подій уздовж лінії 5 В ──
    ev = [
        (1961, "1961: Дж. Б'юї — патент TTL\n(«B+», числа 5 В ще немає)"),
        (1963, "1963: Sylvania SUHL\n(Т. Лонго; ракета Phoenix)"),
        (1966, "сер. 1960-х: TI серія 7400\n— 5 В стають законом"),
    ]
    # розкладемо підписи на різних рівнях, щоб не злипались
    levels = [Y(5.0) + 55, Y(5.0) + 95, Y(5.0) + 135]
    for (yr, label), ylab in zip(ev, levels):
        xx = X(yr)
        s += line(xx, Y(5.0), xx, ylab - 14, GREY, 1, dash="2,3")
        s += circle(xx, Y(5.0), 3.5, INK, INK, 1)
        for i, ln in enumerate(label.split("\n")):
            s += text(xx + 8, ylab + i * 15, ln, size=11.5, color=INK)

    # подія для 3.3 В (JEDEC)
    xx = X(1994)
    s += line(xx, Y(3.3), xx, Y(3.3) + 40, GREY, 1, dash="2,3")
    s += text(xx + 8, Y(3.3) + 36, "1990-ті: JEDEC задає 3.3 / 2.5 / 1.8 В",
              size=11.5, color=INK)
    s += text(xx + 8, Y(3.3) + 51, "(LVTTL/LVCMOS; «5V-tolerant»)",
              size=11.5, color=GREY)

    save("fig-14-4i-1-timeline.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# Рис. 3.1.4i.2 — бюджет напруги всередині TTL: чому саме ~5 В
# три колонки: 3 В (мало) / 5 В (в самий раз) / 9 В (забагато)
# ═════════════════════════════════════════════════════════════════════════════
def fig_why_five():
    W, H = 880, 500
    s = header(W, H)
    s += text(W / 2, 30, "Чому ~5 В: над падіннями переходів TTL має лишитися «1» із запасом",
              size=17, color=INK, anchor="middle", weight="bold")
    s += text(W / 2, 50, "кожен p-n-перехід «з'їдає» ≈ 0.7 В (Vbe, §2.6); потрібен запас на чистий рівень",
              size=12.5, color=GREY, anchor="middle")

    # три панелі
    cols = [
        (70,  3.0, "Vcc ≈ 3 В", "ЗАМАЛО", AMBER,
         "над переходами не лишається\nмісця на «1» із запасом —\nсхема тендітна"),
        (335, 5.0, "Vcc = 5 В", "В САМИЙ РАЗ", GREEN,
         "над падіннями ще є запас\nна чистий рівень, а втрати\nще помірні"),
        (600, 9.0, "Vcc ≈ 9 В", "ЗАБАГАТО", AMBER,
         "переходи працюють, але чип\nдарма палить енергію\nй гріється"),
    ]
    pw = 215           # ширина панелі
    yb = 410           # низ шкали (0 В)
    yt = 95            # верх поля
    vmax = 9.5
    n_drops = 3        # умовно 3 послідовні переходи по 0.7 В
    vdrop = 0.7

    for (x, vcc, vlab, verdict, vcol, note) in cols:
        cx = x + pw / 2

        def Y(v, yb=yb, yt=yt, vmax=vmax):
            return yb - v / vmax * (yb - yt)

        # рамка панелі
        s += rect(x, yt - 20, pw, yb - yt + 95, "none", vcol, 2, rx=10)
        s += text(cx, yt - 30, vlab, size=15, color=INK, anchor="middle", weight="bold")

        # вертикальна шкала напруги (стовпчик)
        bar_x = x + 52
        bw = 46
        # рівень Vcc
        s += line(bar_x - 10, Y(vcc), bar_x + bw + 10, Y(vcc), INK, 2)
        s += text(bar_x + bw + 16, Y(vcc) + 4, f"Vcc={vcc:g}В", size=12, color=INK)

        # стовпчик: знизу вгору — n переходів (мідні), решта — «доступний запас на 1»
        # падіння переходів
        y_cur = yb
        for i in range(n_drops):
            y_next = Y(vdrop * (i + 1))
            s += rect(bar_x, y_next, bw, y_cur - y_next, COPPER, COPPER, 1)
            s += text(bar_x + bw / 2, (y_cur + y_next) / 2 + 4, "0.7", size=10.5,
                      color="#ffffff", anchor="middle")
            y_cur = y_next
        s += text(bar_x + bw / 2, yb + 16, f"{n_drops}×Vbe", size=11, color=COPPER,
                  anchor="middle")

        # «запас, що лишився» від вершини переходів до Vcc
        margin = vcc - n_drops * vdrop
        y_top_drops = Y(n_drops * vdrop)
        if margin > 0:
            mcol = GREEN if margin >= 2.0 else AMBER
            s += rect(bar_x, Y(vcc), bw, y_top_drops - Y(vcc), mcol, mcol, 1, rx=0)
            # додамо легку прозорість через окремий полігон-заливку
            s += text(bar_x + bw / 2, (Y(vcc) + y_top_drops) / 2 + 4,
                      f"{margin:.1f}В", size=11, color="#ffffff", anchor="middle",
                      weight="bold")
        else:
            # від'ємний запас — позначка
            s += text(bar_x + bw / 2, y_top_drops - 10, "немає!", size=11,
                      color=AMBER, anchor="middle", weight="bold")

        # підпис «запас на 1»
        s += text(bar_x + bw + 16, (Y(vcc) + y_top_drops) / 2 + 4,
                  "← запас на «1»", size=11,
                  color=(GREEN if margin >= 2.0 else AMBER))

        # вісь 0
        s += line(bar_x - 10, yb, bar_x + bw + 10, yb, INK, 1.5)
        s += text(bar_x - 14, yb + 4, "0", size=11, color=GREY, anchor="end")

        # вердикт
        s += text(cx, yb + 48, verdict, size=15, color=vcol, anchor="middle",
                  weight="bold")
        for i, ln in enumerate(note.split("\n")):
            s += text(cx, yb + 68 + i * 15, ln, size=11.5, color=INK, anchor="middle")

    save("fig-14-4i-2-why-five.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# Рис. 3.1.4i.3 — дві сили вниз: (ліво) пробій тонкого ізолятора; (право) енергія V²
# ═════════════════════════════════════════════════════════════════════════════
def fig_down():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 30, "Чому 5 В довелося покинути: дві сили тиснуть напругу вниз",
              size=18, color=INK, anchor="middle", weight="bold")

    # розділова лінія
    s += line(W / 2, 60, W / 2, H - 30, FAINT, 2)

    # ─────────── ЛІВО: пробій тонкого ізолятора (E = V/d) ───────────
    s += text(225, 84, "1. Пробій: транзистор здрібнів",
              size=15, color=INK, anchor="middle", weight="bold")
    s += text(225, 104, "та сама напруга на тоншому ізоляторі = більше поле",
              size=12, color=GREY, anchor="middle")

    # два «конденсатори-затвори»: товстий (старий) і тонкий (новий), однакові 5 В
    def gate(cx, top, d_gap, label, sub, danger):
        # дві обкладки (метал затвора зверху, канал знизу), ізолятор між ними
        plate_w = 120
        col = AMBER if danger else GREEN
        # верхня обкладка (затвор, +5 В)
        s_local = rect(cx - plate_w / 2, top, plate_w, 12, RED, RED, 1)
        # нижня обкладка (канал, 0)
        s_local += rect(cx - plate_w / 2, top + 12 + d_gap, plate_w, 12, BLUE, BLUE, 1)
        # ізолятор (рамка) між ними
        s_local += rect(cx - plate_w / 2, top + 12, plate_w, d_gap, FAINT, col, 1.5)
        s_local += text(cx + plate_w / 2 + 8, top + 8, "+5 В", size=11, color=RED)
        s_local += text(cx + plate_w / 2 + 8, top + 12 + d_gap + 10, "0 В",
                        size=11, color=BLUE)
        # стрілки поля E всередині ізолятора (густота = сила)
        n = 3 if not danger else 6
        for i in range(n):
            xx = cx - plate_w / 2 + plate_w * (i + 0.5) / n
            s2 = arrow(xx, top + 13, xx, top + 12 + d_gap - 1, col, 1.8)
            s_local_add = s2
            s_local += s_local_add
        # підпис d
        s_local += line(cx - plate_w / 2 - 14, top + 12, cx - plate_w / 2 - 14,
                        top + 12 + d_gap, INK, 1)
        s_local += text(cx - plate_w / 2 - 18, top + 12 + d_gap / 2 + 4, "d",
                        size=12, color=INK, anchor="end", style="italic")
        s_local += text(cx, top + 12 + d_gap + 42, label, size=13, color=INK,
                        anchor="middle", weight="bold")
        s_local += text(cx, top + 12 + d_gap + 60, sub, size=11.5,
                        color=col, anchor="middle")
        return s_local

    s += gate(150, 150, 56, "старий, великий", "поле помірне — ОК", danger=False)
    s += gate(330, 150, 20, "новий, дрібний", "поле велике — ПРОБІЙ", danger=True)

    # формула E = V/d
    s += text(225, 350, "E = V / d", size=16, color=INK, anchor="middle",
              weight="bold", style="italic")
    s += text(225, 372, "d ↓  при тому самому V  ⇒  E ↑  ⇒  ізолятор руйнується",
              size=12, color=INK, anchor="middle")
    s += text(225, 396, "менший транзистор фізично ВИМАГАЄ нижчої напруги",
              size=12.5, color=AMBER, anchor="middle", weight="bold")

    # ─────────── ПРАВО: енергія V² ───────────
    s += text(655, 84, "2. Енергія: витрати ростуть як V²",
              size=15, color=INK, anchor="middle", weight="bold")
    s += text(655, 104, "критично для всього, що живиться від батареї",
              size=12, color=GREY, anchor="middle")

    # стовпчики E ∝ V² для 5 / 3.3 / 1.8 В
    base_x = 520
    yb = 340
    htop = 130
    levels = [(5.0, "5 В", 1.00), (3.3, "3.3 В", (3.3 / 5.0) ** 2),
              (1.8, "1.8 В", (1.8 / 5.0) ** 2)]
    bw = 70
    gap = 40
    maxh = yb - htop
    for i, (v, lab, e) in enumerate(levels):
        x = base_x + i * (bw + gap)
        h = e * maxh
        col = AMBER if i == 0 else (GREEN if i == 2 else "#7bb36a")
        s += rect(x, yb - h, bw, h, col, col, 1, rx=4)
        s += text(x + bw / 2, yb - h - 8, f"×{e:.2f}", size=13, color=INK,
                  anchor="middle", weight="bold")
        s += text(x + bw / 2, yb + 18, lab, size=13, color=INK, anchor="middle")
    # базова лінія
    s += line(base_x - 12, yb, base_x + 3 * (bw + gap) - gap + 12, yb, INK, 1.5)
    s += text(base_x - 16, yb + 4, "0", size=11, color=GREY, anchor="end")
    s += text(655, yb + 44, "E ∝ C · V²   (строго — Модуль 4)",
              size=13, color=INK, anchor="middle", weight="bold")
    s += text(655, yb + 64, "половинна напруга → вчетверо менше тепла",
              size=12, color=GREEN, anchor="middle")

    # спільний підпис-висновок унизу
    s += text(W / 2, H - 8,
              "обидві сили тиснуть в один бік — тому спуск 5 → 3.3 → 1.8 В був неминучим",
              size=12.5, color=INK, anchor="middle", style="italic")

    save("fig-14-4i-3-down.svg", s)


if __name__ == "__main__":
    fig_timeline()
    fig_why_five()
    fig_down()
    print("done: 3 figures ->", OUT)
