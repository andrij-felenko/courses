# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 2.4 — «АЧХ, децибели й фільтри» (Модуль 2).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи посекційно (Рис. 2.4.Т.k);
для історії до розділу — секція 0 (Рис. 2.4.0.k). Допоміжні функції
скопійовано з попередніх розділів (єдиний вигляд).
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
COPP  = "#b5732e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey"}


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


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _poly(pts, col, wv=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" '
            f'fill="none" stroke="{col}" stroke-width="{wv}"{d}/>\n')


def _axes(ox, oy, w, h, xlab, ylab):
    s = arrow(ox, oy, ox, oy - h - 14, INK, 2)
    s += arrow(ox, oy, ox + w + 14, oy, INK, 2)
    s += text(ox + w + 18, oy + 4, xlab, 13, INK, "start", "bold")
    s += text(ox - 4, oy - h - 22, ylab, 13, INK, "middle", "bold")
    return s


def _frame(x, y, w, h, title=""):
    s = rect(x, y, w, h, "#ffffff", "#c9d3dc", 1.4, 6)
    if title:
        s += text(x + w / 2, y - 6, title, 12, INK, "middle", "bold")
    return s


# ─────────────────────────────────────────────────────────────────────────────
#  Історія до Розділу 2.4 — Гендрік Боде
# ─────────────────────────────────────────────────────────────────────────────
def fig0_trio():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 34, "Тріо Bell Labs, що приручило зворотний зв'язок", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "винахід — критерій — інженерний інструмент: три кроки за тринадцять років",
              12.5, GREY, "middle", style="italic")
    panels = ((70, "1927 · Гарольд Блек", "ВИНАХІД", LGRN, GREEN,
               ("віддати велике «сире»", "підсилення в обмін", "на точність і стабільність:", "від'ємний зворотний зв'язок")),
              (320, "1932 · Гаррі Найквіст", "КРИТЕРІЙ", LBLUE, BLUE,
               ("коли петля зв'язку", "перетворює підсилювач", "на генератор виття:", "математична умова стійкості")),
              (570, "1938–40 · Гендрік Боде", "ІНСТРУМЕНТ", LRED, "#c98a8a",
               ("графіки на лог-осях,", "де все малюється лінійкою,", "і ЗАПАСИ стійкості, які", "видно простим оком")))
    for x, who, role, fill, stroke, lines_ in panels:
        s += rect(x, 90, 200, 250, fill, stroke, 2, 10)
        s += text(x + 100, 122, who, 13, INK, "middle", "bold")
        s += text(x + 100, 148, role, 12.5, GREY, "middle", "bold")
        for i, ln in enumerate(lines_):
            s += text(x + 100, 186 + i * 20, ln, 11.5, INK, "middle")
        s += text(x + 100, 320, "Bell Labs", 10.5, GREY, "middle", style="italic")
    s += arrow(272, 215, 318, 215, GREY, 2)
    s += arrow(522, 215, 568, 215, GREY, 2)
    s += text(W / 2, 384, "усі троє розв'язували одну задачу: тисячі підсилювачів трансконтинентальної телефонної лінії",
              12, GREY, "middle", style="italic")
    save("fig-r04-0-1-trio.svg", s)


def fig0_bode_idea():
    W, H = 840, 470
    s = header(W, H)
    s += text(W / 2, 34, "Фокус Боде: на логарифмічних осях криві стають прямими", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "та сама частотна характеристика кола — у двох системах координат",
              12.5, GREY, "middle", style="italic")

    def resp(f):
        # підсилення ФНЧ другого порядку (умовно)
        return 1.0 / math.sqrt((1 + (f / 0.08) ** 2) * (1 + (f / 0.4) ** 2))

    # ліва панель: лінійні осі
    ox, oy, w, h = 80, 380, 320, 250
    s += _frame(60, 90, 360, 330, "лінійні осі: незручна крива")
    s += _axes(ox, oy, w, h, "f", "підсилення")
    pts = [(ox + f / 100 * w, oy - resp(f / 100) * 0.9 * h) for f in range(0, 101)]
    s += _poly(pts, RED, 2.6)
    s += text(ox + 0.55 * w, oy - 0.45 * h, "усе найцікавіше", 11.5, GREY, "middle", style="italic")
    s += text(ox + 0.55 * w, oy - 0.45 * h + 16, "стиснуте біля нуля", 11.5, GREY, "middle", style="italic")
    # права панель: лог-лог
    ox2 = 500
    s += _frame(480, 90, 340, 330, "лог-лог: ламана з прямих")
    s += _axes(ox2, oy, w, h, "f (лог)", "підсилення (лог)")

    def lg(f):
        return math.log10(f)

    fmin, fmax = 0.005, 2.0
    pts = []
    for j in range(0, 201):
        f = fmin * (fmax / fmin) ** (j / 200)
        x = ox2 + (lg(f) - lg(fmin)) / (lg(fmax) - lg(fmin)) * w
        g = resp(f)
        y = oy - (math.log10(g) + 2.6) / 2.6 * 0.9 * h
        pts.append((x, y))
    s += _poly(pts, RED, 2.6)
    # асимптоти
    def X(f):
        return ox2 + (lg(f) - lg(fmin)) / (lg(fmax) - lg(fmin)) * w

    def Y(g):
        return oy - (math.log10(g) + 2.6) / 2.6 * 0.9 * h

    s += line(X(fmin), Y(1), X(0.08), Y(1), GREEN, 1.8, dash="6,4")
    s += line(X(0.08), Y(1), X(0.4), Y(resp(0.4) * 1.41), GREEN, 1.8, dash="6,4")
    s += line(X(0.4), Y(resp(0.4) * 1.41), X(fmax), Y(resp(0.4) * 1.41 * (0.4 / fmax) ** 2), GREEN, 1.8, dash="6,4")
    s += circle(X(0.08), Y(1), 4, GREEN, GREEN, 0)
    s += circle(X(0.4), Y(resp(0.4) * 1.41), 4, GREEN, GREEN, 0)
    s += text(X(0.08), Y(1) - 12, "злам", 10.5, GREEN, "middle", "bold")
    s += text(X(0.4), Y(resp(0.4) * 1.41) - 12, "ще злам", 10.5, GREEN, "middle", "bold")
    s += text(ox2 + 0.52 * w, oy - 0.18 * h, "прямі-асимптоти:", 11.5, "#1f6e33", "middle", "bold")
    s += text(ox2 + 0.52 * w, oy - 0.18 * h + 16, "малюються лінійкою", 11.5, "#1f6e33", "middle", "bold")
    s += text(W / 2, 446, "а підсилення каскадів на лог-осях ДОДАЄТЬСЯ замість множитися — складні системи збираються з прямих",
              12, GREY, "middle", style="italic")
    save("fig-r04-0-2-bode-idea.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §2.4.1 — Коло як фільтр: що таке частотна характеристика
# ─────────────────────────────────────────────────────────────────────────────
def _square_partial(ox, oy, w, amp, nmax, col, wv=2.2):
    pts = []
    for j in range(0, 401):
        t = j / 400.0
        v = 0.0
        n = 1
        while n <= nmax:
            v += math.sin(2 * math.pi * n * t * 2) / n
            n += 2
        pts.append((ox + t * w, oy - amp * v * 4 / math.pi * 0.78))
    return _poly(pts, col, wv)


def fig11_square_sum():
    W, H = 820, 520
    s = header(W, H)
    s += text(W / 2, 34, "Будь-який сигнал — суміш синусоїд: меандр по частинах", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "додаємо непарні гармоніки — і з хвиль складається прямокутник",
              12.5, GREY, "middle", style="italic")
    rows = ((1, "лише 1-ша гармоніка (основна)", BLUE),
            (3, "1-ша + 3-тя", GREEN),
            (5, "1-ша + 3-тя + 5-та", COPP),
            (19, "…до 19-ї: уже майже меандр", RED))
    for i, (nmax, lab, col) in enumerate(rows):
        oy = 135 + i * 100
        # цільовий меандр блідо
        sq = []
        for j in range(0, 401):
            t = j / 400.0
            v = 0.78 if (t * 2) % 1 < 0.5 else -0.78
            sq.append((120 + t * 560, oy - 36 * v))
        s += _poly(sq, FAINT, 1.6)
        s += _square_partial(120, oy, 560, 36, nmax, col)
        s += text(110, oy + 4, lab, 11, INK, "end")
    s += text(W / 2, 500, "що крутіші деталі сигналу (фронти, кути) — то вищі частоти в них «зашиті»; це знадобиться постійно",
              12, GREY, "middle", style="italic")
    save("fig-r04-1-1-square-sum.svg", s)


def fig11_concept():
    W, H = 840, 470
    s = header(W, H)
    s += text(W / 2, 34, "Частотна характеристика: ручка гучності для кожної частоти", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "лінійне коло обробляє кожну синусоїду суміші незалежно — лише масштабує і зсуває",
              12.5, GREY, "middle", style="italic")
    freqs = (0.15, 0.3, 0.45, 0.6, 0.75)
    gains = (1.0, 0.95, 0.7, 0.35, 0.12)
    # вхідний спектр
    ox1, oy1, w1, h1 = 70, 330, 180, 200
    s += _axes(ox1, oy1, w1, h1, "f", "вхід")
    for f in freqs:
        s += line(ox1 + f * w1 / 0.9, oy1, ox1 + f * w1 / 0.9, oy1 - 0.75 * h1, BLUE, 5)
    # блок кола з K(f)
    bx, by, bw, bh = 320, 150, 200, 180
    s += rect(bx, by, bw, bh, "#f7f7f7", INK, 2, 10)
    s += text(bx + bw / 2, by - 12, "коло (фільтр)", 12.5, INK, "middle", "bold")
    pts = [(bx + 20 + t / 100 * (bw - 40), by + 40 + (1 - 1 / math.sqrt(1 + (t / 45.0) ** 4)) * (bh - 80)) for t in range(0, 101)]
    s += _poly(pts, RED, 2.4)
    s += text(bx + bw / 2, by + bh - 14, "K(f) — АЧХ", 11.5, RED, "middle", "bold")
    s += arrow(255, 230, 315, 230, GREY, 2.2)
    s += arrow(525, 230, 585, 230, GREY, 2.2)
    # вихідний спектр
    ox2, oy2 = 600, 330
    s += _axes(ox2, oy2, w1, h1, "f", "вихід")
    for f, g in zip(freqs, gains):
        s += line(ox2 + f * w1 / 0.9, oy2, ox2 + f * w1 / 0.9, oy2 - 0.75 * h1 * g, GREEN, 5)
    s += text(W / 2, 400, "кожен стовпчик спектра помножився на «свою» висоту кривої K(f) — і більше нічого не сталося:",
              12, INK, "middle", "bold")
    s += text(W / 2, 422, "у цьому вся сила опису — одна крива розповідає, що коло зробить із БУДЬ-ЯКИМ сигналом",
              12, INK, "middle", "bold")
    save("fig-r04-1-2-concept.svg", s)


def fig11_rc_three():
    W, H = 840, 500
    s = header(W, H)
    s += text(W / 2, 34, "Звідки береться форма K(f): RC-дільник на трьох частотах", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "реактивність конденсатора залежить від частоти — отже, і коефіцієнт дільника теж",
              12.5, GREY, "middle", style="italic")
    # схема
    sx, sy = 110, 150
    s += line(sx, sy, sx + 50, sy, INK, 2.2)
    s += rect(sx + 50, sy - 9, 60, 18, "#f3f3f3", INK, 1.6)
    s += text(sx + 80, sy - 16, "R", 12, INK, "middle", "bold")
    s += line(sx + 110, sy, sx + 170, sy, INK, 2.2)
    s += circle(sx + 170, sy, 3.5, INK, INK, 0)
    s += line(sx + 170, sy, sx + 230, sy, INK, 2.2)
    s += text(sx + 230 + 8, sy + 4, "вихід", 11.5, GREEN, "start", "bold")
    s += line(sx + 170, sy, sx + 170, sy + 40, INK, 2)
    cs_y = sy + 49
    s += line(sx + 156, cs_y - 4, sx + 184, cs_y - 4, INK, 2.6)
    s += line(sx + 156, cs_y + 5, sx + 184, cs_y + 5, INK, 2.6)
    s += line(sx + 170, cs_y + 5, sx + 170, sy + 95, INK, 2)
    s += text(sx + 196, cs_y + 4, "C", 12, INK, "start", "bold")
    s += text(sx - 8, sy + 4, "вхід", 11.5, BLUE, "end", "bold")
    # три режими
    rows = (("низька f:", "Xc величезна — дільник віддає все", "K ≈ 1", GREEN),
            ("f ≈ f_c:", "Xc ≈ R — ділить приблизно навпіл", "K ≈ 0.7", COPP),
            ("висока f:", "Xc мізерна — вихід майже замкнено", "K → 0", RED))
    for i, (a, b, c, col) in enumerate(rows):
        y = 300 + i * 28
        s += text(110, y, a, 12.5, INK, "start", "bold")
        s += text(200, y, b, 12.5, INK, "start")
        s += text(545, y, c, 12.5, col, "start", "bold")
    # ескіз K(f)
    ox, oy, w, h = 480, 250, 300, 160
    s += _axes(ox, oy, w, h, "f (лог)", "K")
    pts = [(ox + t / 100 * w, oy - 0.85 * h / math.sqrt(1 + (10 ** (3 * t / 100 - 1.5)) ** 2)) for t in range(0, 101)]
    s += _poly(pts, RED, 2.6)
    s += line(ox + 0.5 * w, oy, ox + 0.5 * w, oy - 0.6 * h, GREY, 1.2, dash="4,4")
    s += text(ox + 0.5 * w, oy + 18, "f_c", 12, INK, "middle", "bold")
    s += text(W / 2, 432, "та сама логіка «дільник із реактивністю», що в π-фільтрі (§2.3.3) — тепер як ціла крива для всіх частот;",
              12, GREY, "middle", style="italic")
    s += text(W / 2, 452, "докладний розбір цього кола — у наступній темі",
              12, GREY, "middle", style="italic")
    save("fig-r04-1-3-rc-three.svg", s)


def fig11_four_shapes():
    W, H = 820, 330
    s = header(W, H)
    s += text(W / 2, 34, "Чотири канонічні форми АЧХ", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "що пропускаємо: низ, верх, смугу — чи все, крім смуги",
              12.5, GREY, "middle", style="italic")

    def shape(kind, t):
        if kind == "lp":
            return 1 / math.sqrt(1 + (t / 0.45) ** 6)
        if kind == "hp":
            return 1 / math.sqrt(1 + (0.45 / max(t, 1e-3)) ** 6)
        if kind == "bp":
            return 1 / math.sqrt(1 + ((t - 0.5) / 0.12) ** 4)
        return 1 - 1 / math.sqrt(1 + ((t - 0.5) / 0.12) ** 4)

    cells = (("lp", "нижніх частот (ФНЧ)"), ("hp", "верхніх частот (ФВЧ)"),
             ("bp", "смуговий"), ("nf", "режекторний"))
    for i, (kind, lab) in enumerate(cells):
        ox, oy, w, h = 70 + i * 190, 240, 150, 130
        s += _axes(ox, oy, w, h, "f", "K" if i == 0 else "")
        pts = [(ox + t / 100 * w, oy - 0.85 * h * shape(kind, t / 100)) for t in range(0, 101)]
        s += _poly(pts, COPP, 2.4)
        s += text(ox + w / 2, oy + 40, lab, 11.5, INK, "middle", "bold")
    s += text(W / 2, 308, "будь-який складніший фільтр — комбінація цих чотирьох характерів (деталі — у темах розділу)",
              11.5, GREY, "middle", style="italic")
    save("fig-r04-1-4-four-shapes.svg", s)


def fig11_phase_matters():
    W, H = 820, 440
    s = header(W, H)
    s += text(W / 2, 34, "Фаза — друга половина портрета: амплітуди ті самі, форма інша", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "той самий набір гармонік меандра, але 3-тю і 5-ту зсунуто по фазі",
              12.5, GREY, "middle", style="italic")

    def sig(ox, oy, w, amp, phases, col):
        pts = []
        for j in range(0, 401):
            t = j / 400.0
            v = 0.0
            for n, ph in phases:
                v += math.sin(2 * math.pi * n * t * 2 + ph) / n
            pts.append((ox + t * w, oy - amp * v * 4 / math.pi * 0.8))
        return _poly(pts, col, 2.2)

    s += text(120, 110, "фази правильні (усі нуль):", 12.5, INK, "start", "bold")
    s += sig(120, 175, 560, 42, ((1, 0), (3, 0), (5, 0), (7, 0), (9, 0)), GREEN)
    s += text(120, 270, "ті САМІ амплітуди, але фази гармонік зсунуті:", 12.5, INK, "start", "bold")
    s += sig(120, 340, 560, 42, ((1, 0), (3, 1.2), (5, 2.4), (7, 0.7), (9, 1.9)), RED)
    s += text(W / 2, 410, "АЧХ обох сигналів однакова — а форма геть різна: ось чому в даташитах поруч із АЧХ малюють і ФЧХ",
              12, GREY, "middle", style="italic")
    save("fig-r04-1-5-phase-matters.svg", s)


def fig11_everything_filters():
    W, H = 820, 440
    s = header(W, H)
    s += text(W / 2, 34, "Фільтрує все — навіть те, що фільтром не назване", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "паразитні R і C є в кожному з'єднанні — отже, у кожного з'єднання є своя АЧХ",
              12.5, GREY, "middle", style="italic")
    items = ((80, "кабель чи довга доріжка", "опір жил + ємність між ними", "= прихований ФНЧ"),
             (340, "вхід приладу чи чипа", "опір джерела + вхідна ємність", "= прихований ФНЧ"),
             (600, "підсилювач", "обмежена швидкість каскадів", "= смуга в даташиті"))
    for x, t1, t2, t3 in items:
        s += rect(x, 100, 200, 150, "#fbfbfb", "#c9d3dc", 1.6, 8)
        s += text(x + 100, 130, t1, 12, INK, "middle", "bold")
        s += text(x + 100, 158, t2, 10.5, GREY, "middle")
        s += text(x + 100, 182, t3, 11.5, RED, "middle", "bold")
        ox, oy, w, h = x + 35, 235, 130, 55
        pts = [(ox + t / 100 * w, oy - 0.8 * h / math.sqrt(1 + (t / 55.0) ** 4)) for t in range(0, 101)]
        s += _poly(pts, COPP, 2)
    s += text(W / 2, 330, "наслідок для практики: у кожної системи є СМУГА — діапазон частот, який вона чесно передає;",
              12.5, INK, "middle", "bold")
    s += text(W / 2, 352, "сигнали зі швидшими деталями (крутішими фронтами) вона округлить, хочете ви того чи ні",
              12.5, INK, "middle", "bold")
    s += text(W / 2, 396, "тому «яка у вас смуга?» — перше питання і до осцилографа, і до підсилювача, і до кабелю",
              11.5, GREY, "middle", style="italic")
    save("fig-r04-1-6-everything-filters.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §2.4.2 — RC-фільтр низьких частот
# ─────────────────────────────────────────────────────────────────────────────
def fig21_circuit():
    W, H = 760, 360
    s = header(W, H)
    s += text(W / 2, 34, "RC-ФНЧ: сигнал іде через R, конденсатор зливає швидке в землю", 17.5, INK, "middle", "bold")
    y = 140
    s += circle(90, y, 5, INK, INK, 0)
    s += text(90, y - 18, "вхід", 12, BLUE, "middle", "bold")
    s += line(90, y, 160, y, INK, 2.4)
    s += rect(160, y - 10, 70, 20, "#f3f3f3", INK, 1.8)
    s += text(195, y - 18, "R", 13, INK, "middle", "bold")
    s += line(230, y, 330, y, INK, 2.4)
    s += circle(330, y, 4, INK, INK, 0)
    s += line(330, y, 430, y, INK, 2.4)
    s += circle(430, y, 5, INK, INK, 0)
    s += text(430, y - 18, "вихід", 12, GREEN, "middle", "bold")
    s += line(330, y, 330, y + 48, INK, 2)
    s += line(314, y + 52, 346, y + 52, INK, 2.8)
    s += line(314, y + 62, 346, y + 62, INK, 2.8)
    s += text(356, y + 60, "C", 13, INK, "start", "bold")
    s += line(330, y + 62, 330, y + 100, INK, 2)
    s += line(90, y + 100, 560, y + 100, INK, 2.2)
    s += arrow(480, y, 560, y, GREY, 1.8)
    s += text(520, y - 12, "до споживача", 10.5, GREY, "middle")
    # анотації
    s += arrow(265, y - 44, 265, y - 8, GREEN, 1.8)
    s += text(265, y - 52, "повільне: проходить (Xc велика)", 11, "#1f6e33", "middle", "bold")
    s += arrow(390, y + 36, 344, y + 52, RED, 1.8)
    s += text(440, y + 36, "швидке: зливається в землю", 11, "#9a2b22", "start", "bold")
    s += text(W / 2, 310, "це дільник напруги, у якого нижнє плече — реактивність: коефіцієнт ділення залежить від частоти",
              12, GREY, "middle", style="italic")
    save("fig-r04-2-1-circuit.svg", s)


def fig22_triangle():
    W, H = 760, 420
    s = header(W, H)
    s += text(W / 2, 34, "Звідки корінь у формулі: R та Xc складаються під прямим кутом", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "напруги на R і на C зсунуті на 90° (§2.3.4) — отже, додаються як катети",
              12.5, GREY, "middle", style="italic")
    ox, oy = 180, 330
    sc = 2.1
    rlen, xlen = 110 * sc / 2.1, 80 * sc / 2.1
    rl, xl = 220, 160
    s += arrow(ox, oy, ox + rl, oy, COPP, 3)
    s += text(ox + rl / 2, oy + 24, "R (у фазі зі струмом)", 12, COPP, "middle", "bold")
    s += arrow(ox + rl, oy, ox + rl, oy - xl, BLUE, 3)
    s += text(ox + rl + 12, oy - xl / 2, "Xc (на 90° позаду)", 12, BLUE, "start", "bold")
    s += arrow(ox, oy, ox + rl, oy - xl, RED, 3)
    s += text(ox + rl / 2 - 18, oy - xl / 2 - 14, "|Z| = √(R² + Xc²)", 13, RED, "middle", "bold")
    s += rect(ox + rl - 14, oy - 14, 14, 14, "none", GREY, 1.2)
    ax = 520
    s += text(ax, 150, "вихід знімаємо з C, тож:", 13, INK, "start", "bold")
    s += text(ax, 186, "K = Xc / |Z|", 15, INK, "start", "bold")
    s += text(ax, 222, "підставимо Xc = 1/(2πfC)", 12.5, INK, "start")
    s += text(ax, 240, "і поділимо чисельник", 12.5, INK, "start")
    s += text(ax, 258, "та знаменник на Xc:", 12.5, INK, "start")
    s += text(ax, 296, "K(f) = 1/√(1 + (f/f_c)²)", 15, GREEN, "start", "bold")
    s += text(ax, 330, "f_c = 1/(2π·R·C)", 14, GREEN, "start", "bold")
    save("fig-r04-2-2-triangle.svg", s)


def _lp_axes_log(ox, oy, w, h, s_add_label=True):
    out = ""
    for d in range(0, 4):
        x = ox + d / 3 * w
        out += line(x, oy, x, oy - h, FAINT, 1)
    return out


def fig23_curve():
    W, H = 800, 460
    s = header(W, H)
    s += text(W / 2, 34, "K(f) фільтра нижніх частот: полиця, плече, спад", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "частота — логарифмічно (декадами); три опорні точки варто пам'ятати",
              12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 100, 380, 600, 270
    for d, lab in ((0, "0.1·f_c"), (1, "f_c"), (2, "10·f_c"), (3, "100·f_c")):
        x = ox + d / 3 * w
        s += line(x, oy, x, oy - h, FAINT, 1)
        s += text(x, oy + 20, lab, 11.5, GREY, "middle", "bold")
    s += _axes(ox, oy, w, h, "f (лог)", "K")
    pts = []
    for j in range(0, 301):
        lg = -1 + 3 * j / 300.0
        fr = 10 ** lg
        k = 1 / math.sqrt(1 + fr * fr)
        pts.append((ox + (lg + 1) / 3 * w, oy - 0.88 * h * k))
    s += _poly(pts, RED, 2.8)
    marks = ((0.1, 0.995, "0.995 — майже все"), (1.0, 0.707, "0.707 — точка зрізу"), (10.0, 0.0995, "≈0.1 — удесятеро слабше"))
    for fr, k, lab in marks:
        x = ox + (math.log10(fr) + 1) / 3 * w
        y = oy - 0.88 * h * k
        s += circle(x, y, 4.5, RED, RED, 0)
        s += text(x + 10, y - 10, lab, 11.5, INK, "start", "bold")
    s += text(W / 2, 432, "нижче за f_c фільтр майже прозорий; вище — глушить дедалі сильніше: ×10 за частотою = ÷10 за амплітудою",
              12, GREY, "middle", style="italic")
    save("fig-r04-2-3-curve.svg", s)


def fig24_asymptotes():
    W, H = 780, 440
    s = header(W, H)
    s += text(W / 2, 34, "Дві прямі-асимптоти: ескіз Боде за десять секунд", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "на лог-лог осях крива притискається до полиці K=1 і до спаду «вдесятеро на декаду»",
              12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 100, 360, 580, 250

    def X(lg):
        return ox + (lg + 1.5) / 3.0 * w

    def Y(klog):
        return oy - (klog + 2.2) / 2.2 * 0.95 * h

    s += _axes(ox, oy, w, h, "f (лог)", "K (лог)")
    # асимптоти
    s += line(X(-1.5), Y(0), X(0), Y(0), GREEN, 2, dash="7,5")
    s += line(X(0), Y(0), X(1.5), Y(-1.5), GREEN, 2, dash="7,5")
    s += circle(X(0), Y(0), 4.5, GREEN, GREEN, 0)
    s += text(X(0), Y(0) - 14, "злам на f_c", 11.5, "#1f6e33", "middle", "bold")
    # реальна крива
    pts = []
    for j in range(0, 301):
        lg = -1.5 + 3 * j / 300.0
        k = 1 / math.sqrt(1 + (10 ** lg) ** 2)
        pts.append((X(lg), Y(math.log10(k))))
    s += _poly(pts, RED, 2.6)
    s += circle(X(0), Y(math.log10(0.707)), 4.5, RED, RED, 0)
    s += text(X(0) + 10, Y(math.log10(0.707)) + 16, "реальна крива: 0.707 у зламі", 11.5, RED, "start", "bold")
    s += text(X(0.8), Y(-0.45), "нахил: ÷10 на декаду", 11.5, "#1f6e33", "start", "bold")
    s += text(W / 2, 412, "далі в розділі цей нахил дістане звичне ім'я «−20 дБ/декаду» — а малюється він уже зараз, лінійкою",
              12, GREY, "middle", style="italic")
    save("fig-r04-2-4-asymptotes.svg", s)


def fig25_phase():
    W, H = 760, 400
    s = header(W, H)
    s += text(W / 2, 34, "Фаза ФНЧ: вихід відстає — від 0° до −90°", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "рівно −45° у точці зрізу: фаза «чує» наближення зрізу раніше за амплітуду",
              12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 100, 320, 560, 200
    for d, lab in ((0, "0.01·f_c"), (1, "0.1·f_c"), (2, "f_c"), (3, "10·f_c"), (4, "100·f_c")):
        x = ox + d / 4 * w
        s += line(x, oy, x, oy - h, FAINT, 1)
        s += text(x, oy + 20, lab, 10.5, GREY, "middle", "bold")
    s += _axes(ox, oy, w, h, "f (лог)", "φ")
    pts = []
    for j in range(0, 301):
        lg = -2 + 4 * j / 300.0
        ph = -math.atan(10 ** lg)
        pts.append((ox + (lg + 2) / 4 * w, oy - h * (1 + ph / (math.pi / 2)) * 0.88 - 0.0 * h))
    s += _poly(pts, BLUE, 2.8)
    s += line(ox, oy - 0.88 * h, ox + w, oy - 0.88 * h, GREY, 1, dash="4,4")
    s += text(ox - 8, oy - 0.88 * h + 4, "0°", 11.5, GREY, "end")
    s += line(ox, oy - 0.44 * h, ox + w, oy - 0.44 * h, GREY, 1, dash="4,4")
    s += text(ox - 8, oy - 0.44 * h + 4, "−45°", 11.5, GREY, "end")
    s += text(ox - 8, oy + 4, "−90°", 11.5, GREY, "end")
    s += circle(ox + 0.5 * w, oy - 0.44 * h, 4.5, BLUE, BLUE, 0)
    save("fig-r04-2-5-phase.svg", s)


def fig26_two_languages():
    W, H = 820, 430
    s = header(W, H)
    s += text(W / 2, 34, "Два портрети одного кола: відповідь на сходинку і АЧХ", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "τ = R·C і f_c = 1/(2π·R·C) — одне число в часовій і частотній мовах",
              12.5, GREY, "middle", style="italic")
    # step response
    ox1, oy1, w1, h1 = 80, 330, 300, 200
    s += _frame(60, 90, 340, 290, "час: сходинка на вході")
    s += _axes(ox1, oy1, w1, h1, "t", "")
    pts = [(ox1 + t / 100 * w1, oy1 - (1 - math.exp(-5 * t / 100)) * 0.8 * h1) for t in range(0, 101)]
    s += _poly(pts, RED, 2.6)
    s += _poly([(ox1, oy1 - 0.02 * h1), (ox1 + 2, oy1 - 0.8 * h1), (ox1 + w1, oy1 - 0.8 * h1)], GREY, 1.6, dash="5,4")
    s += text(ox1 + 0.5 * w1, oy1 - 0.32 * h1, "експонента, стала часу τ = RC", 11.5, RED, "middle", "bold")
    s += text(ox1 + 0.5 * w1, oy1 + 28, "«конденсатор не встигає» (§2.1.4)", 11, GREY, "middle", style="italic")
    # АЧХ
    ox2, oy2 = 480, 330
    s += _frame(460, 90, 340, 290, "частота: синуси на вході")
    s += _axes(ox2, oy2, w1, h1, "f (лог)", "")
    pts = []
    for j in range(0, 301):
        lg = -1.5 + 3 * j / 300.0
        k = 1 / math.sqrt(1 + (10 ** lg) ** 2)
        pts.append((ox2 + (lg + 1.5) / 3 * w1, oy2 - 0.8 * h1 * k))
    s += _poly(pts, RED, 2.6)
    s += line(ox2 + 0.5 * w1, oy2, ox2 + 0.5 * w1, oy2 - 0.8 * h1, GREY, 1.2, dash="4,4")
    s += text(ox2 + 0.5 * w1, oy2 + 18, "f_c = 1/(2πτ)", 11.5, INK, "middle", "bold")
    s += text(ox2 + 0.5 * w1, oy2 - 0.32 * h1, "«високі гармоніки зрізано»", 11.5, RED, "middle", "bold")
    s += text(W / 2, 408, "повільне коло (велика τ) = низька f_c; швидке = висока: дві мови, один компроміс",
              12.5, INK, "middle", "bold")
    save("fig-r04-2-6-two-languages.svg", s)


def fig27_loading():
    W, H = 780, 430
    s = header(W, H)
    s += text(W / 2, 34, "Навантаження псує фільтр: полиця сідає, зріз їде", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "опір споживача стає другим плечем дільника — і переписує характеристику",
              12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 100, 350, 560, 240
    s += _axes(ox, oy, w, h, "f (лог)", "K")
    for col, drop, fc_shift, lab, y_lab in ((RED, 1.0, 1.0, "без навантаження", 0.93),
                                            (BLUE, 0.5, 2.0, "R_L = R: полиця 0.5, зріз поїхав", 0.55)):
        pts = []
        for j in range(0, 301):
            lg = -1.5 + 3 * j / 300.0
            k = drop / math.sqrt(1 + (10 ** lg / fc_shift) ** 2)
            pts.append((ox + (lg + 1.5) / 3 * w, oy - 0.9 * h * k))
        s += _poly(pts, col, 2.6)
        s += text(ox + 0.05 * w, oy - 0.9 * h * drop - 10, lab, 11.5, col, "start", "bold")
    s += text(W / 2, 402, "правила: навантаження має бути значно більшим за R — або відгородіть фільтр буфером (§2.8.5)",
              12, GREY, "middle", style="italic")
    save("fig-r04-2-7-loading.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §2.4.3 — RC-фільтр високих частот
# ─────────────────────────────────────────────────────────────────────────────
def fig31_circuit():
    W, H = 760, 360
    s = header(W, H)
    s += text(W / 2, 34, "RC-ФВЧ: тепер конденсатор у шляху, резистор — униз", 17.5, INK, "middle", "bold")
    y = 140
    s += circle(90, y, 5, INK, INK, 0)
    s += text(90, y - 18, "вхід", 12, BLUE, "middle", "bold")
    s += line(90, y, 170, y, INK, 2.4)
    s += line(186, y - 14, 186, y + 14, INK, 2.8)
    s += line(196, y - 14, 196, y + 14, INK, 2.8)
    s += text(191, y - 24, "C", 13, INK, "middle", "bold")
    s += line(196, y, 330, y, INK, 2.4)
    s += circle(330, y, 4, INK, INK, 0)
    s += line(330, y, 430, y, INK, 2.4)
    s += circle(430, y, 5, INK, INK, 0)
    s += text(430, y - 18, "вихід", 12, GREEN, "middle", "bold")
    s += line(330, y, 330, y + 40, INK, 2)
    s += rect(320, y + 40, 20, 44, "#f3f3f3", INK, 1.8)
    s += text(352, y + 66, "R", 13, INK, "start", "bold")
    s += line(330, y + 84, 330, y + 110, INK, 2)
    s += line(90, y + 110, 560, y + 110, INK, 2.2)
    s += arrow(265, y - 44, 265, y - 8, GREEN, 1.8)
    s += text(265, y - 52, "швидке: проходить (Xc мала)", 11, "#1f6e33", "middle", "bold")
    s += text(120, y + 60, "повільне й постійне:", 11, "#9a2b22", "start", "bold")
    s += text(120, y + 76, "конденсатор не пускає", 11, "#9a2b22", "start", "bold")
    s += text(W / 2, 310, "той самий дільник, але вихід знято з резистора: коефіцієнт росте з частотою",
              12, GREY, "middle", style="italic")
    save("fig-r04-3-1-circuit.svg", s)


def fig32_formula():
    W, H = 760, 400
    s = header(W, H)
    s += text(W / 2, 34, "Той самий трикутник — інший катет", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "ФНЧ знімав вихід із Xc, ФВЧ знімає з R; гіпотенуза спільна",
              12.5, GREY, "middle", style="italic")
    ox, oy = 160, 320
    rl, xl = 220, 160
    s += arrow(ox, oy, ox + rl, oy, COPP, 3)
    s += text(ox + rl / 2, oy + 24, "R  ← звідси вихід ФВЧ", 12, COPP, "middle", "bold")
    s += arrow(ox + rl, oy, ox + rl, oy - xl, BLUE, 3)
    s += text(ox + rl + 12, oy - xl / 2, "Xc ← звідси був вихід ФНЧ", 12, BLUE, "start", "bold")
    s += arrow(ox, oy, ox + rl, oy - xl, RED, 3)
    s += text(ox + rl / 2 - 20, oy - xl / 2 - 16, "√(R² + Xc²)", 13, RED, "middle", "bold")
    ax = 500
    s += text(ax, 140, "K = R / √(R² + Xc²)", 14.5, INK, "start", "bold")
    s += text(ax, 176, "після підстановки Xc = 1/(2πfC):", 12, INK, "start")
    s += text(ax, 212, "K(f) = 1/√(1 + (f_c/f)²)", 15, GREEN, "start", "bold")
    s += text(ax, 248, "f_c = 1/(2π·R·C) — ТА САМА", 13.5, GREEN, "start", "bold")
    s += text(ax, 284, "формула ФНЧ, лише дріб f/f_c", 12, GREY, "start", style="italic")
    s += text(ax, 302, "перевернувся: тепер глушаться низькі", 12, GREY, "start", style="italic")
    save("fig-r04-3-2-formula.svg", s)


def fig33_curve():
    W, H = 800, 470
    s = header(W, H)
    s += text(W / 2, 34, "K(f) фільтра верхніх частот: підйом, злам, полиця", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "дзеркало ФНЧ: ×10 на декаду вгору, поки не вперлися в полицю K = 1",
              12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 100, 380, 600, 270

    def X(lg):
        return ox + (lg + 1.5) / 3.0 * w

    def Y(klog):
        return oy - (klog + 2.2) / 2.2 * 0.95 * h

    s += _axes(ox, oy, w, h, "f (лог)", "K (лог)")
    for d, lab in ((-1, "0.1·f_c"), (0, "f_c"), (1, "10·f_c")):
        s += line(X(d), oy, X(d), oy - h, FAINT, 1)
        s += text(X(d), oy + 20, lab, 11.5, GREY, "middle", "bold")
    # асимптоти
    s += line(X(-1.5), Y(-1.5), X(0), Y(0), GREEN, 2, dash="7,5")
    s += line(X(0), Y(0), X(1.5), Y(0), GREEN, 2, dash="7,5")
    pts = []
    for j in range(0, 301):
        lg = -1.5 + 3 * j / 300.0
        k = 1 / math.sqrt(1 + (10 ** (-lg)) ** 2)
        pts.append((X(lg), Y(math.log10(k))))
    s += _poly(pts, RED, 2.8)
    marks = ((-1, 0.0995, "0.1"), (0, 0.707, "0.707"), (1, 0.995, "0.995"))
    for lg, k, lab in marks:
        s += circle(X(lg), Y(math.log10(k)), 4.5, RED, RED, 0)
        s += text(X(lg) + 10, Y(math.log10(k)) + 16, lab, 11.5, INK, "start", "bold")
    s += text(X(-1.0), Y(-0.4), "підйом ×10 на декаду", 11.5, "#1f6e33", "start", "bold")
    s += text(W / 2, 438, "постійний струм (f = 0) не проходить узагалі — це строгий вигляд «блокує постійне» з §2.1.1",
              12, GREY, "middle", style="italic")
    save("fig-r04-3-3-curve.svg", s)


def fig34_phase():
    W, H = 760, 380
    s = header(W, H)
    s += text(W / 2, 34, "Фаза ФВЧ: вихід попереду — від +90° до 0°", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "+45° у зрізі; «випередження» стосується усталеної синусоїди, причинність ціла",
              12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 100, 310, 560, 200
    s += _axes(ox, oy, w, h, "f (лог)", "φ")
    pts = []
    for j in range(0, 301):
        lg = -2 + 4 * j / 300.0
        ph = math.pi / 2 - math.atan(10 ** lg)
        pts.append((ox + (lg + 2) / 4 * w, oy - h * (ph / (math.pi / 2)) * 0.88))
    s += _poly(pts, BLUE, 2.8)
    s += line(ox, oy - 0.88 * h, ox + w, oy - 0.88 * h, GREY, 1, dash="4,4")
    s += text(ox - 8, oy - 0.88 * h + 4, "+90°", 11.5, GREY, "end")
    s += line(ox, oy - 0.44 * h, ox + w, oy - 0.44 * h, GREY, 1, dash="4,4")
    s += text(ox - 8, oy - 0.44 * h + 4, "+45°", 11.5, GREY, "end")
    s += text(ox - 8, oy + 4, "0°", 11.5, GREY, "end")
    s += circle(ox + 0.5 * w, oy - 0.44 * h, 4.5, BLUE, BLUE, 0)
    s += text(ox + 0.5 * w, oy + 20, "f_c", 12, INK, "middle", "bold")
    save("fig-r04-3-4-phase.svg", s)


def fig35_square():
    W, H = 820, 460
    s = header(W, H)
    s += text(W / 2, 34, "Меандр крізь ФВЧ: «вуса» на фронтах і провисання полиць", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "фронти (високі гармоніки) проходять; полиці (низькі) фільтр стягує до нуля",
              12.5, GREY, "middle", style="italic")
    # вхід
    ox, w = 110, 600
    oy1 = 160
    s += text(96, oy1 - 40, "вхід:", 12, INK, "end", "bold")
    sq = []
    per = 0.5
    for j in range(0, 601):
        t = j / 600.0
        v = 0.7 if (t / per) % 1 < 0.5 else -0.7
        sq.append((ox + t * w, oy1 - 50 * v))
    s += _poly(sq, BLUE, 2.2)
    # вихід: експоненційні вуса
    oy2 = 330
    s += text(96, oy2 - 40, "вихід:", 12, GREEN, "end", "bold")
    pts = []
    tauf = 0.07
    v = 0.0
    prev = -0.7
    for j in range(0, 601):
        t = j / 600.0
        x = (t / per) % 1
        lvl = 0.7 if x < 0.5 else -0.7
        tin = (x if x < 0.5 else x - 0.5) * per
        start = 1.4 if lvl > 0 else -1.4
        vout = start * math.exp(-tin / tauf)
        pts.append((ox + t * w, oy2 - 50 * vout))
    s += _poly(pts, GREEN, 2.2)
    s += line(ox, oy2, ox + w, oy2, GREY, 1, dash="4,4")
    s += text(ox + w + 6, oy2 + 4, "0", 11, GREY, "start")
    s += text(ox + 0.30 * w, oy2 - 95, "стрибок проходить цілком", 11, "#1f6e33", "middle", "bold")
    s += text(ox + 0.62 * w, oy2 + 64, "полиця «провисає» до нуля зі сталою τ = RC", 11, "#9a2b22", "middle", "bold")
    s += text(W / 2, 428, "що нижча частота меандра відносно f_c, то сильніше провисання: ФВЧ чесно не вміє тримати «постійне»",
              12, GREY, "middle", style="italic")
    save("fig-r04-3-5-square.svg", s)


def fig36_coupling():
    W, H = 820, 470
    s = header(W, H)
    s += text(W / 2, 34, "Головна служба ФВЧ: розділовий конденсатор між каскадами", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "кожен каскад тримає свій постійний рівень; між ними мандрує лише змінний сигнал",
              12.5, GREY, "middle", style="italic")
    # каскади
    s += rect(70, 110, 170, 160, "#f3f3f3", INK, 1.8, 8)
    s += text(155, 138, "каскад 1", 12.5, INK, "middle", "bold")
    s += text(155, 160, "робоча точка 6 В", 11, GREY, "middle")
    s += rect(560, 110, 170, 160, "#f3f3f3", INK, 1.8, 8)
    s += text(645, 138, "каскад 2", 12.5, INK, "middle", "bold")
    s += text(645, 160, "робоча точка 1.5 В", 11, GREY, "middle")
    y = 200
    s += line(240, y, 360, y, INK, 2.4)
    s += line(378, y - 14, 378, y + 14, INK, 2.8)
    s += line(388, y - 14, 388, y + 14, INK, 2.8)
    s += text(383, y - 24, "C розділовий", 11.5, INK, "middle", "bold")
    s += line(388, y, 560, y, INK, 2.4)
    s += circle(470, y, 4, INK, INK, 0)
    s += line(470, y, 470, 250, INK, 2)
    s += rect(460, 250, 20, 40, "#f3f3f3", INK, 1.6)
    s += text(492, 274, "R (вхідний опір", 10.5, INK, "start")
    s += text(492, 288, "каскада 2)", 10.5, INK, "start")
    s += line(470, 290, 470, 318, INK, 2)
    s += line(70, 318, 730, 318, INK, 2.2)
    # сигнали
    for x0, dc, col, lab in ((150, 0.45, BLUE, "сигнал на 6 В"), (640, 0.0, GREEN, "той самий сигнал на 1.5 В")):
        pts = []
        for j in range(0, 101):
            t = j / 100.0
            pts.append((x0 - 55 + t * 110, 372 - 18 * math.sin(2 * math.pi * 3 * t) - 30 * dc))
        s += _poly(pts, col, 2)
        s += text(x0, 408, lab, 10.5, col, "middle", "bold")
    s += text(W / 2, 440, "пара «C розділовий + вхідний опір наступного каскада» — це і є ФВЧ: f_c = 1/(2πRC) ставлять нижче за корисні частоти",
              11.5, GREY, "middle", style="italic")
    save("fig-r04-3-6-coupling.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §2.4.4 — Децибели
# ─────────────────────────────────────────────────────────────────────────────
def fig41_why_log():
    W, H = 820, 430
    s = header(W, H)
    s += text(W / 2, 34, "Дев'ять порядків на одній осі: навіщо логарифм", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "сигнали електроніки живуть від нановольтів до вольтів — лінійна шкала безсила",
              12.5, GREY, "middle", style="italic")
    # лінійна шкала
    s += text(110, 110, "лінійна шкала:", 12.5, INK, "start", "bold")
    s += line(110, 150, 710, 150, INK, 2)
    s += circle(710, 150, 5, RED, RED, 0)
    s += text(710, 132, "1 В (вихід)", 11, RED, "middle", "bold")
    s += circle(110, 150, 5, BLUE, BLUE, 0)
    s += text(110, 174, "тут злиплися ВСІ інші: 1 нВ, 1 мкВ, 1 мВ…", 11, "#27447e", "start", "bold")
    # лог шкала
    s += text(110, 240, "логарифмічна шкала:", 12.5, INK, "start", "bold")
    s += line(110, 290, 710, 290, INK, 2)
    marks = (("1 нВ", "шум антени"), ("", ""), ("1 мкВ", "радіосигнал"), ("", ""),
             ("1 мВ", "мікрофон"), ("", ""), ("1 В", "лінійний вихід"), ("", ""), ("1 кВ", ""))
    for i in range(0, 9):
        x = 110 + i * 75
        s += line(x, 284, x, 296, INK, 1.6)
        lab, sub = marks[i] if i < len(marks) else ("", "")
        if lab:
            s += text(x, 314, lab, 11, INK, "middle", "bold")
            if sub:
                s += text(x, 330, sub, 9.5, GREY, "middle")
    s += text(W / 2, 380, "кожен крок шкали — ×10: рівні відстані означають рівні МНОЖНИКИ, і всі дев'ять порядків видно одночасно",
              12, GREY, "middle", style="italic")
    save("fig-r04-4-1-why-log.svg", s)


def fig42_ladder():
    W, H = 800, 500
    s = header(W, H)
    s += text(W / 2, 34, "Розмовник дБ ↔ разів: вивчіть ці рядки напам'ять", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "ліворуч — напруга (20·log), праворуч — потужність (10·log)",
              12.5, GREY, "middle", style="italic")
    rows = (("+40 дБ", "×100", "×10 000"),
            ("+20 дБ", "×10", "×100"),
            ("+6 дБ", "×2", "×4"),
            ("+3 дБ", "×1.41 (√2)", "×2"),
            ("0 дБ", "×1", "×1"),
            ("−3 дБ", "×0.707", "×0.5  ← половина потужності!"),
            ("−6 дБ", "×0.5", "×0.25"),
            ("−20 дБ", "×0.1", "×0.01"),
            ("−40 дБ", "×0.01", "×0.0001"))
    s += text(260, 96, "за напругою", 12, GREY, "middle", "bold")
    s += text(560, 96, "за потужністю", 12, GREY, "middle", "bold")
    y = 130
    for db, v, p in rows:
        hl = "−3" in db
        if hl:
            s += rect(80, y - 18, 660, 28, LGRN, GREEN, 1.4, 6)
        s += text(140, y, db, 13.5, INK, "middle", "bold")
        s += text(260, y, v, 13, (GREEN if hl else INK), "middle", "bold" if hl else "normal")
        s += text(560, y, p, 13, (GREEN if hl else INK), "middle", "bold" if hl else "normal")
        y += 36
    s += text(W / 2, y + 10, "решта збирається додаванням: 26 дБ = 20 + 6 → ×10·×2 = ×20", 12.5, INK, "middle", "bold")
    save("fig-r04-4-2-ladder.svg", s)


def fig43_20log():
    W, H = 780, 400
    s = header(W, H)
    s += text(W / 2, 34, "Чому для напруг 20·log: потужність — це квадрат", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "ті самі децибели мають описувати ту саму фізичну зміну",
              12.5, GREY, "middle", style="italic")
    # ілюстрація: V×2 → P×4
    s += rect(100, 110, 240, 120, LBLUE, BLUE, 1.8, 8)
    s += text(220, 145, "напруга ×2", 14, INK, "middle", "bold")
    s += text(220, 175, "на тому самому опорі", 11, GREY, "middle")
    s += text(220, 205, "P = V²/R  →  потужність ×4", 12.5, INK, "middle", "bold")
    s += arrow(350, 170, 430, 170, GREY, 2.2)
    s += rect(440, 110, 240, 120, LGRN, GREEN, 1.8, 8)
    s += text(560, 145, "мовою потужності:", 12, INK, "middle")
    s += text(560, 172, "10·log(4) ≈ +6 дБ", 13.5, INK, "middle", "bold")
    s += text(560, 200, "мовою напруги:", 12, INK, "middle")
    s += text(560, 225, "20·log(2) ≈ +6 дБ  ✓", 13.5, GREEN, "middle", "bold")
    s += text(W / 2, 290, "10·log(V₂²/V₁²) = 20·log(V₂/V₁): двійка перед логарифмом — це показник квадрата, що «вийшов» із нього",
              12.5, INK, "middle", "bold")
    s += text(W / 2, 330, "тож −3 дБ — це 0.5 за потужністю І 0.707 за напругою: одна й та сама точка зрізу двома мовами",
              12, GREY, "middle", style="italic")
    s += text(W / 2, 360, "(строго 20·log для напруг чесний на однакових опорах; на практиці так позначають будь-яке відношення напруг)",
              10.5, GREY, "middle", style="italic")
    save("fig-r04-4-3-20log.svg", s)


def fig44_cascade():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 34, "Головна зручність: каскади ДОДАЮТЬСЯ", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "логарифм перетворює множення коефіцієнтів на додавання децибелів",
              12.5, GREY, "middle", style="italic")
    blocks = (("підсилювач", "+40 дБ", "×100"), ("фільтр на краю смуги", "−3 дБ", "×0.707"), ("довгий кабель", "−1 дБ", "×0.89"))
    x = 80
    y = 150
    for name, db, k in blocks:
        s += rect(x, y - 40, 190, 80, "#f3f3f3", INK, 1.8, 8)
        s += text(x + 95, y - 12, name, 12, INK, "middle", "bold")
        s += text(x + 95, y + 14, db, 13.5, GREEN, "middle", "bold")
        s += text(x + 95, y + 32, k, 10.5, GREY, "middle")
        if x > 90:
            s += arrow(x - 40, y, x - 2, y, GREY, 2.2)
        x += 230
    s += arrow(x - 40, y, x - 2, y, GREY, 2.2)
    s += text(x + 8, y + 5, "разом", 11.5, INK, "start", "bold")
    s += rect(170, 260, 480, 90, LGRN, GREEN, 2, 10)
    s += text(410, 292, "у децибелах: 40 − 3 − 1 = +36 дБ (усно!)", 14, INK, "middle", "bold")
    s += text(410, 322, "у разах: 100 · 0.707 · 0.89 ≈ ×63 (уже з калькулятором)", 12.5, GREY, "middle")
    s += text(W / 2, 390, "саме заради цього додавання Боде й перевів усі графіки на логарифмічну мову",
              12, GREY, "middle", style="italic")
    save("fig-r04-4-4-cascade.svg", s)


def fig45_slopes():
    W, H = 800, 430
    s = header(W, H)
    s += text(W / 2, 34, "Нахили дістають імена: −20 дБ/декаду", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "наші «÷10 на декаду» з тем про ФНЧ і ФВЧ — ось як вони підписані в даташитах",
              12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 110, 350, 560, 240

    def X(lg):
        return ox + (lg + 1.5) / 3.0 * w

    def Y(db):
        return oy - (db + 45) / 45.0 * 0.95 * h

    s += _axes(ox, oy, w, h, "f (лог)", "K, дБ")
    for db in (0, -20, -40):
        s += line(ox, Y(db), ox + w, Y(db), FAINT, 1)
        s += text(ox - 8, Y(db) + 4, f"{db}", 11.5, GREY, "end")
    pts = []
    for j in range(0, 301):
        lg = -1.5 + 3 * j / 300.0
        k = 1 / math.sqrt(1 + (10 ** lg) ** 2)
        pts.append((X(lg), Y(20 * math.log10(k))))
    s += _poly(pts, RED, 2.8)
    s += line(X(0), Y(0), X(1.5), Y(-30), GREEN, 2, dash="7,5")
    s += circle(X(0), Y(-3), 4.5, RED, RED, 0)
    s += text(X(0) + 10, Y(-3) - 8, "−3 дБ на f_c — ось вона, «точка зрізу»", 11.5, INK, "start", "bold")
    s += text(X(0.75), Y(-9), "−20 дБ/декаду", 12.5, "#1f6e33", "start", "bold")
    s += text(X(0.75), Y(-14), "(= −6 дБ/октаву)", 10.5, GREY, "start")
    s += text(W / 2, 402, "у дБ навіть вісь K стала лінійною: рівні децибели — рівні кроки; фільтр вищого порядку дасть −40, −60… дБ/дек",
              11.5, GREY, "middle", style="italic")
    save("fig-r04-4-5-slopes.svg", s)


def fig46_dbm():
    W, H = 800, 460
    s = header(W, H)
    s += text(W / 2, 34, "дБм: децибели з прив'язкою — вже не відношення, а рівень", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "опора 1 мВт: 0 дБм = 1 мВт; далі звичайна драбина по 10 дБ = ×10 потужності",
              12.5, GREY, "middle", style="italic")
    lx = 230
    rows = (("+30 дБм", "1 Вт", "передавач рації"),
            ("+20 дБм", "100 мВт", "Wi-Fi роутер"),
            ("0 дБм", "1 мВт", "опорна точка"),
            ("−30 дБм", "1 мкВт", "сильний прийнятий сигнал"),
            ("−70 дБм", "100 пВт", "типовий рівень прийому Wi-Fi"),
            ("−100 дБм", "0.1 пВт", "межа чутливості приймачів"))
    s += line(lx, 100, lx, 420, GREY, 2)
    y = 120
    for db, p, note in rows:
        s += circle(lx, y, 4.5, INK, INK, 0)
        s += text(lx - 16, y + 4, db, 13, INK, "end", "bold")
        s += text(lx + 18, y - 2, p, 12.5, GREEN, "start", "bold")
        s += text(lx + 18, y + 15, note, 11, GREY, "start")
        y += 56
    s += text(560, 180, "навіщо: тракт рахується", 12.5, INK, "start", "bold")
    s += text(560, 202, "однією колонкою додавань:", 12.5, INK, "start", "bold")
    s += text(560, 232, "передавач      +20 дБм", 12, INK, "start")
    s += text(560, 252, "втрати тракту  −80 дБ", 12, INK, "start")
    s += text(560, 272, "приймач        −60 дБм", 12.5, GREEN, "start", "bold")
    s += text(560, 296, "(= 1 нВт — і це нормальна", 11, GREY, "start")
    s += text(560, 312, "робота радіозв'язку)", 11, GREY, "start")
    save("fig-r04-4-6-dbm.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §2.4.5 — АЧХ і діаграма Боде
# ─────────────────────────────────────────────────────────────────────────────
def fig51_full_bode():
    W, H = 800, 560
    s = header(W, H)
    s += text(W / 2, 34, "Діаграма Боде: офіційний портрет кола з двох панелей", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "зверху амплітуда в дБ, знизу фаза в градусах — спільна логарифмічна вісь частоти",
              12.5, GREY, "middle", style="italic")
    ox, w = 110, 560

    def X(lg):
        return ox + (lg + 2) / 4.0 * w

    # амплітудна панель
    oy1, h1 = 280, 180
    s += _axes(ox, oy1, w, h1, "", "К, дБ")
    for db in (0, -20, -40):
        y = oy1 - (db + 45) / 45.0 * 0.9 * h1
        s += line(ox, y, ox + w, y, FAINT, 1)
        s += text(ox - 8, y + 4, f"{db}", 11, GREY, "end")
    pts = []
    for j in range(0, 301):
        lg = -2 + 4 * j / 300.0
        k = 1 / math.sqrt(1 + (10 ** lg) ** 2)
        pts.append((X(lg), oy1 - (20 * math.log10(k) + 45) / 45.0 * 0.9 * h1))
    s += _poly(pts, RED, 2.8)
    s += circle(X(0), oy1 - (-3 + 45) / 45.0 * 0.9 * h1, 4.5, RED, RED, 0)
    s += text(X(0) + 10, oy1 - (-3 + 45) / 45.0 * 0.9 * h1 - 8, "−3 дБ", 11.5, INK, "start", "bold")
    # фазова панель
    oy2, h2 = 510, 160
    s += _axes(ox, oy2, w, h2, "f (лог)", "φ")
    for ph, lab in ((0, "0°"), (-45, "−45°"), (-90, "−90°")):
        y = oy2 - (ph + 90) / 90.0 * 0.9 * h2
        s += line(ox, y, ox + w, y, FAINT, 1)
        s += text(ox - 8, y + 4, lab, 11, GREY, "end")
    pts = []
    for j in range(0, 301):
        lg = -2 + 4 * j / 300.0
        ph = -math.degrees(math.atan(10 ** lg))
        pts.append((X(lg), oy2 - (ph + 90) / 90.0 * 0.9 * h2))
    s += _poly(pts, BLUE, 2.8)
    s += line(X(0), oy1 - 0.9 * h1, X(0), oy2, GREY, 1.2, dash="4,4")
    s += text(X(0), oy2 + 20, "f_c", 12, INK, "middle", "bold")
    save("fig-r04-5-1-full-bode.svg", s)


def fig52_alphabet():
    W, H = 840, 360
    s = header(W, H)
    s += text(W / 2, 34, "Алфавіт Боде: чотири цеглинки, з яких складаються діаграми", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "у мові інженерів злами звуться «полюс» (униз) і «нуль» (угору)",
              12.5, GREY, "middle", style="italic")
    cells = (("підсилення K₀", "горизонталь на 20·log K₀", lambda t: 0.55),
             ("полюс на f_p", "після зламу −20 дБ/дек", lambda t: 0.85 if t < 0.45 else 0.85 - (t - 0.45) * 1.5),
             ("нуль на f_z", "після зламу +20 дБ/дек", lambda t: 0.25 if t < 0.45 else 0.25 + (t - 0.45) * 1.5),
             ("інтегратор 1/f", "пряма −20 дБ/дек скрізь", lambda t: 0.95 - t * 0.8))
    for i, (name, note, fn) in enumerate(cells):
        ox, oy, w, h = 60 + i * 195, 260, 160, 140
        s += _axes(ox, oy, w, h, "f", "дБ" if i == 0 else "")
        pts = [(ox + t / 100 * w, oy - h * max(0.04, min(0.96, fn(t / 100)))) for t in range(0, 101)]
        s += _poly(pts, COPP, 2.6)
        s += text(ox + w / 2, oy + 26, name, 11.5, INK, "middle", "bold")
        s += text(ox + w / 2, oy + 44, note, 9.5, GREY, "middle")
    s += text(W / 2, 336, "сума цеглинок у дБ = добуток характеристик у разах (§2.4.4): складна діаграма — це додані прямі",
              11.5, GREY, "middle", style="italic")
    save("fig-r04-5-2-alphabet.svg", s)


def fig53_build():
    W, H = 820, 540
    s = header(W, H)
    s += text(W / 2, 34, "Рецепт: малюємо смуговий підсилювач трьома цеглинками", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "ФВЧ 20 Гц (розділовий C) + підсилення +40 дБ + ФНЧ 20 кГц (смуга каскадів)",
              12.5, GREY, "middle", style="italic")
    ox, w = 110, 600

    def X(lg):
        return ox + lg / 6.0 * w      # lg від 0 (=1 Гц) до 6 (=1 МГц)

    def Y(db):
        return 470 - (db + 20) / 70.0 * 350

    s += _axes(ox, 470, w, 360, "f", "К, дБ")
    for db in (0, 20, 40):
        s += line(ox, Y(db), ox + w, Y(db), FAINT, 1)
        s += text(ox - 8, Y(db) + 4, f"{db}", 11, GREY, "end")
    for lg, lab in ((0, "1 Гц"), (1.3, "20 Гц"), (3, "1 кГц"), (4.3, "20 кГц"), (6, "1 МГц")):
        s += line(X(lg), 470, X(lg), 476, INK, 1.4)
        s += text(X(lg), 492, lab, 10.5, GREY, "middle", "bold")
    # цеглинки пунктиром
    s += line(X(0), Y(40), X(6), Y(40), GREEN, 1.6, dash="6,5")
    s += text(X(5.0), Y(40) - 8, "+40 дБ", 10.5, "#1f6e33", "middle", "bold")
    s += _poly([(X(0), Y(-20 + 26)), (X(1.3), Y(0)), (X(6), Y(0))], BLUE, 1.6, dash="6,5")
    s += text(X(0.5), Y(10), "ФВЧ: +20 дБ/дек до 20 Гц", 10, "#27447e", "start")
    s += _poly([(X(0), Y(0)), (X(4.3), Y(0)), (X(6), Y(-34))], COPP, 1.6, dash="6,5")
    s += text(X(5.1), Y(-12), "ФНЧ: −20 дБ/дек", 10, COPP, "start")
    # сума
    pts = []
    for j in range(0, 301):
        lg = 6 * j / 300.0
        f = 10 ** lg
        k = 100.0
        k *= 1 / math.sqrt(1 + (20.0 / f) ** 2)
        k *= 1 / math.sqrt(1 + (f / 20000.0) ** 2)
        pts.append((X(lg), Y(20 * math.log10(k))))
    s += _poly(pts, RED, 3)
    s += text(X(2.7), Y(43) - 8, "СУМА: робоча смуга 20 Гц … 20 кГц на полиці +40 дБ", 11.5, RED, "middle", "bold")
    save("fig-r04-5-3-build.svg", s)


def fig54_phase_build():
    W, H = 800, 420
    s = header(W, H)
    s += text(W / 2, 34, "Фазова панель того самого підсилювача", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "кожен злам веде фазу до ±90°, розмазано на дві декади; −45°/+45° точно на зламі",
              12.5, GREY, "middle", style="italic")
    ox, w = 110, 600

    def X(lg):
        return ox + lg / 6.0 * w

    def Y(ph):
        return 340 - (ph + 100) / 200.0 * 250

    s += _axes(ox, 340, w, 260, "f", "φ")
    for ph, lab in ((90, "+90°"), (45, "+45°"), (0, "0°"), (-45, "−45°"), (-90, "−90°")):
        s += line(ox, Y(ph), ox + w, Y(ph), FAINT, 1)
        s += text(ox - 8, Y(ph) + 4, lab, 10.5, GREY, "end")
    pts = []
    for j in range(0, 301):
        lg = 6 * j / 300.0
        f = 10 ** lg
        ph = math.degrees(math.atan(20.0 / f)) - math.degrees(math.atan(f / 20000.0))
        pts.append((X(lg), Y(ph)))
    s += _poly(pts, BLUE, 2.8)
    for lg, lab in ((1.3, "20 Гц"), (4.3, "20 кГц")):
        s += line(X(lg), 340, X(lg), 80, GREY, 1.1, dash="4,4")
        s += text(X(lg), 360, lab, 10.5, GREY, "middle", "bold")
    s += text(X(2.8), Y(8), "посередині смуги фаза ≈ 0 — сигнал проходить «чесно»", 11, GREY, "middle", style="italic")
    save("fig-r04-5-4-phase-build.svg", s)


def fig55_read_opamp():
    W, H = 800, 470
    s = header(W, H)
    s += text(W / 2, 34, "Тренування: прочитати криву підсилення з даташита", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "типовий операційний підсилювач (§2.8.9): полиця + полюс + спад −20 дБ/дек",
              12.5, GREY, "middle", style="italic")
    ox, w = 110, 580

    def X(lg):
        return ox + lg / 7.0 * w

    def Y(db):
        return 380 - (db + 10) / 120.0 * 300

    s += _axes(ox, 380, w, 310, "f", "К, дБ")
    for db in (0, 40, 80, 100):
        s += line(ox, Y(db), ox + w, Y(db), FAINT, 1)
        s += text(ox - 8, Y(db) + 4, f"{db}", 11, GREY, "end")
    for lg, lab in ((0, "1 Гц"), (1, "10"), (3, "1 кГц"), (5, "100 кГц"), (6, "1 МГц"), (7, "10 МГц")):
        s += line(X(lg), 380, X(lg), 386, INK, 1.2)
        s += text(X(lg), 400, lab, 10, GREY, "middle")
    pts = []
    for j in range(0, 301):
        lg = 7 * j / 300.0
        f = 10 ** lg
        k_db = 100 - 10 * math.log10(1 + (f / 10.0) ** 2)
        pts.append((X(lg), Y(max(k_db, -8))))
    s += _poly(pts, RED, 2.8)
    qs = ((3, 60, "на 1 кГц: К = 60 дБ = ×1000"), (6, 0, "0 дБ на 1 МГц: далі чип уже не підсилює"))
    for lg, db, lab in qs:
        s += circle(X(lg), Y(db), 4.5, RED, RED, 0)
        s += text(X(lg) + 10, Y(db) - 8, lab, 11, INK, "start", "bold")
    s += text(X(1.0), Y(96), "полиця 100 дБ, полюс на ~10 Гц", 10.5, GREY, "start")
    s += text(W / 2, 440, "уся крива — наші цеглинки: полиця, один полюс, −20 дБ/дек; докладно про ці межі ОП — §2.8.9",
              11.5, GREY, "middle", style="italic")
    save("fig-r04-5-5-read-opamp.svg", s)


def fig56_second_order():
    W, H = 780, 440
    s = header(W, H)
    s += text(W / 2, 34, "Тизер другого порядку: −40 дБ/дек і пік, що залежить від Q", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "LC-фільтр — два «полюси» разом: крутіший спад, а біля f₀ може стирчати резонанс (§2.3.6)",
              12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 100, 360, 580, 260

    def X(lg):
        return ox + (lg + 1.5) / 3.0 * w

    def Y(db):
        return oy - (db + 60) / 80.0 * 0.95 * h

    s += _axes(ox, oy, w, h, "f (лог)", "К, дБ")
    for db in (0, -20, -40):
        s += line(ox, Y(db), ox + w, Y(db), FAINT, 1)
        s += text(ox - 8, Y(db) + 4, f"{db}", 10.5, GREY, "end")
    for qv, col, lab in ((0.7, GREEN, "Q ≈ 0.7: плоско"), (3.0, RED, "Q = 3: пік на f₀")):
        pts = []
        for j in range(0, 301):
            lg = -1.5 + 3 * j / 300.0
            x = 10 ** lg
            k = 1 / math.sqrt((1 - x * x) ** 2 + (x / qv) ** 2)
            pts.append((X(lg), Y(max(20 * math.log10(k), -58))))
        s += _poly(pts, col, 2.6)
        s += text(X(0.42), Y(8 if qv > 1 else -13), lab, 11.5, col, "start", "bold")
    s += text(X(0.9), Y(-44), "−40 дБ/дек", 11.5, INK, "start", "bold")
    s += text(W / 2, 412, "порядок фільтра = кількість полюсів = крутість спаду; докладніше — в останній темі розділу",
              11.5, GREY, "middle", style="italic")
    save("fig-r04-5-6-second-order.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §2.4.6 — Смуга пропускання й точка −3 дБ
# ─────────────────────────────────────────────────────────────────────────────
def fig61_bw_def():
    W, H = 840, 380
    s = header(W, H)
    s += text(W / 2, 34, "Смуга пропускання: де K не нижче за −3 дБ від полиці", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "одне означення — три застосування: ФНЧ, смуговий, ФВЧ",
              12.5, GREY, "middle", style="italic")

    def panel(ox, kind, lab, bw_lab):
        oy, w, h = 300, 200, 180
        out = _axes(ox, oy, w, h, "f", "К" if ox < 100 else "")
        pts = []
        for j in range(0, 121):
            t = j / 120.0
            if kind == "lp":
                k = 1 / math.sqrt(1 + (t / 0.45) ** 4)
            elif kind == "bp":
                k = 1 / math.sqrt(1 + ((t - 0.5) / 0.13) ** 4)
            else:
                k = 1 / math.sqrt(1 + (0.45 / max(t, 1e-3)) ** 4)
            pts.append((ox + t * w, oy - 0.85 * h * k))
        # заштрихована смуга
        if kind == "lp":
            x1, x2 = ox, ox + 0.45 * w
        elif kind == "bp":
            x1, x2 = ox + 0.37 * w, ox + 0.63 * w
        else:
            x1, x2 = ox + 0.45 * w, ox + w
        out += rect(x1, oy - 0.85 * h, x2 - x1, 0.85 * h, LGRN, "none", 0)
        out += _poly(pts, COPP, 2.4)
        out += line(ox, oy - 0.85 * h * 0.707, ox + w, oy - 0.85 * h * 0.707, GREY, 1.1, dash="5,4")
        out += text(ox + w / 2, oy + 24, lab, 11.5, INK, "middle", "bold")
        out += text(ox + w / 2, oy + 42, bw_lab, 10, GREY, "middle")
        return out

    s += panel(60, "lp", "ФНЧ: смуга 0 … f_c", "BW = f_c")
    s += panel(320, "bp", "смуговий: f₁ … f₂", "BW = f₂ − f₁ = f₀/Q")
    s += panel(580, "hp", "ФВЧ: від f_c угору", "межу зверху ставить схема")
    save("fig-r04-6-1-bw-def.svg", s)


def fig62_risetime():
    W, H = 820, 470
    s = header(W, H)
    s += text(W / 2, 34, "Смуга визначає найкрутіший фронт: t_r ≈ 0.35 / BW", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "та сама ідеальна сходинка крізь системи різної смуги",
              12.5, GREY, "middle", style="italic")
    rows = ((10.0, GREEN, "BW = 100 МГц:  t_r ≈ 3.5 нс"),
            (3.0, COPP, "BW = 30 МГц:  t_r ≈ 12 нс"),
            (1.0, RED, "BW = 10 МГц:  t_r ≈ 35 нс"))
    ox, w = 130, 560
    for i, (bw, col, lab) in enumerate(rows):
        oy = 160 + i * 95
        s += line(ox, oy, ox + w, oy, FAINT, 1)
        pts = []
        for j in range(0, 201):
            t = j / 200.0
            v = 1 - math.exp(-t * 14 * bw / 10.0) if t > 0.06 else 0
            v = 0 if t < 0.06 else 1 - math.exp(-(t - 0.06) * 14 * bw / 10.0)
            pts.append((ox + t * w, oy - 60 * v))
        s += _poly(pts, col, 2.4)
        s += text(ox - 10, oy - 25, lab.split(":")[0], 11, col, "end", "bold")
        s += text(ox + w + 10, oy - 25, lab.split(":  ")[1], 11, INK, "start", "bold")
    s += text(W / 2, 440, "звідки 0.35 — у математичній вставці до цієї теми; правило інженера: смуга приладу ≥ 5× смуги сигналу",
              12, GREY, "middle", style="italic")
    save("fig-r04-6-2-risetime.svg", s)


def fig63_cascade_shrink():
    W, H = 780, 440
    s = header(W, H)
    s += text(W / 2, 34, "Каскади звужують смугу: два по −3 дБ дають −6", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "сумарна точка −3 дБ переїжджає ліворуч: BW двох однакових каскадів ≈ 0.64 від одного",
              12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 100, 360, 580, 250

    def X(lg):
        return ox + (lg + 1.5) / 3.0 * w

    def Y(db):
        return oy - (db + 45) / 45.0 * 0.95 * h

    s += _axes(ox, oy, w, h, "f (лог)", "К, дБ")
    for db in (0, -3, -20, -40):
        s += line(ox, Y(db), ox + w, Y(db), FAINT, 1)
        s += text(ox - 8, Y(db) + 4, f"{db}", 10.5, GREY, "end")
    for n, col, lab in ((1, GREEN, "один каскад"), (2, RED, "два каскади поспіль")):
        pts = []
        for j in range(0, 301):
            lg = -1.5 + 3 * j / 300.0
            k = (1 / math.sqrt(1 + (10 ** lg) ** 2)) ** n
            pts.append((X(lg), Y(max(20 * math.log10(k), -43))))
        s += _poly(pts, col, 2.6)
        s += text(X(0.55), Y(-7 * n), lab, 11.5, col, "start", "bold")
    s += circle(X(0), Y(-3), 4.5, GREEN, GREEN, 0)
    s += circle(X(0), Y(-6), 4.5, RED, RED, 0)
    s += circle(X(math.log10(0.644)), Y(-3), 4.5, RED, RED, 0)
    s += arrow(X(-0.02), Y(-3) - 14, X(math.log10(0.644)) + 6, Y(-3) - 14, RED, 1.8)
    s += text(X(-0.45), Y(-3) - 22, "нова межа смуги: 0.64·f_c", 11, "#9a2b22", "middle", "bold")
    s += text(W / 2, 412, "правило: смуга тракту завжди вужча за смугу найвужчого каскада — і тим вужча, що більше каскадів",
              12, GREY, "middle", style="italic")
    save("fig-r04-6-3-cascade-shrink.svg", s)


def fig64_bp_q():
    W, H = 780, 440
    s = header(W, H)
    s += text(W / 2, 34, "Смуговий фільтр: BW = f₀/Q — дві мови зійшлися", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "«ширина на рівні −3 дБ» з цього розділу — це та сама Δf з розмови про добротність",
              12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 100, 360, 580, 250
    s += _axes(ox, oy, w, h, "f", "К, дБ")
    f0, q = 0.5, 6.0
    pts = []
    for j in range(0, 301):
        t = j / 300.0
        x = t / f0
        k = 1 / math.sqrt(1 + (q * (x - 1 / max(x, 1e-6))) ** 2)
        pts.append((ox + t * w, oy - 0.9 * h * k))
    s += _poly(pts, COPP, 2.6)
    lvl = 0.9 * 0.707
    s += line(ox, oy - lvl * h, ox + w, oy - lvl * h, GREY, 1.2, dash="6,5")
    s += text(ox + w + 6, oy - lvl * h + 4, "−3 дБ", 10.5, GREY, "start")
    f1 = f0 * (math.sqrt(1 + 1 / (4 * q * q)) - 1 / (2 * q))
    f2 = f0 * (math.sqrt(1 + 1 / (4 * q * q)) + 1 / (2 * q))
    for fx, lab in ((f1, "f₁"), (f2, "f₂"), (f0, "f₀")):
        s += line(ox + fx * w, oy, ox + fx * w, oy - lvl * h - (18 if lab == "f₀" else 0), GREY, 1.1, dash="4,4")
        s += text(ox + fx * w, oy + 20, lab, 12, INK, "middle", "bold")
    s += arrow(ox + f1 * w, oy - lvl * h - 12, ox + f2 * w, oy - lvl * h - 12, GREEN, 2)
    s += arrow(ox + f2 * w, oy - lvl * h - 12, ox + f1 * w, oy - lvl * h - 12, GREEN, 2)
    s += text(ox + f0 * w, oy - lvl * h - 24, "BW = f₂ − f₁ = f₀/Q", 12.5, "#1f6e33", "middle", "bold")
    s += text(W / 2, 412, "вузька смуга = висока Q = довгий дзвін: усі три твердження — одне (§2.3.6)",
              12, GREY, "middle", style="italic")
    save("fig-r04-6-4-bp-q.svg", s)


def fig65_margin():
    W, H = 800, 430
    s = header(W, H)
    s += text(W / 2, 34, "Правило 5×: куди мають влізти гармоніки сигналу", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "вимірюєш меандр — у смугу приладу мусять поміститися хоча б 5-та гармоніка фронтів",
              12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 100, 330, 600, 220
    s += _axes(ox, oy, w, h, "f", "")
    # спектр меандра
    for n in (1, 3, 5, 7, 9):
        x = ox + n * 0.09 * w
        amp = 0.8 / n
        s += line(x, oy, x, oy - amp * h, BLUE, 6)
        s += text(x, oy + 18, f"{n}f", 10.5, GREY, "middle")
    # смуга приладу
    s += rect(ox, oy - h, 0.52 * w, h, LGRN, "none", 0)
    pts = []
    for j in range(0, 201):
        t = j / 200.0
        k = 1 / math.sqrt(1 + (t / 0.52) ** 8)
        pts.append((ox + t * w, oy - 0.95 * h * k))
    s += _poly(pts, GREEN, 2.2, dash="6,4")
    s += text(ox + 0.26 * w, oy - h + 18, "смуга приладу (≥ 5f сигналу)", 11.5, "#1f6e33", "middle", "bold")
    s += text(ox + 0.75 * w, oy - 0.45 * h, "гармоніки поза смугою", 11, "#9a2b22", "middle", "bold")
    s += text(ox + 0.75 * w, oy - 0.45 * h + 16, "вже «зрізаються»", 11, "#9a2b22", "middle", "bold")
    s += text(W / 2, 400, "смуга «впритул» до основної частоти показала б замість меандра синусоїду — прилад має бачити і фронти",
              12, GREY, "middle", style="italic")
    save("fig-r04-6-5-margin.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  🧮 Вставка до §2.4.4 — Логарифми
# ─────────────────────────────────────────────────────────────────────────────
def fig4m1_counter():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Логарифм — лічильник порядків: «у якому степені десятка дає це число?»", 17.5, INK, "middle", "bold")
    ox, oy, w = 90, 200, 640
    s += line(ox, oy, ox + w, oy, INK, 2.2)
    marks = ((0, "1", "10⁰"), (1, "10", "10¹"), (2, "100", "10²"), (3, "1000", "10³"))
    for p, num, pw in marks:
        x = ox + p / 3.0 * w
        s += line(x, oy - 7, x, oy + 7, INK, 2)
        s += text(x, oy + 28, num, 14, INK, "middle", "bold")
        s += text(x, oy - 16, pw, 12.5, GREY, "middle")
        s += text(x, oy + 56, f"log = {p}", 12.5, BLUE, "middle", "bold")
    x2 = ox + 0.301 / 3.0 * w
    s += line(x2, oy - 7, x2, oy + 7, RED, 2.2)
    s += circle(x2, oy, 4.5, RED, RED, 0)
    s += arrow(x2, oy - 64, x2, oy - 12, RED, 1.8)
    s += text(x2 + 8, oy - 72, "2 = 10^0.301  →  log 2 ≈ 0.301", 12.5, RED, "start", "bold")
    s += text(x2, oy + 28, "2", 13, RED, "middle", "bold")
    s += text(W / 2, 300, "цілі відповіді — лише в круглих степенів; решта чисел живе між ними з дробовими логарифмами,",
              12, GREY, "middle", style="italic")
    s += text(W / 2, 320, "і «двійка — це 30% шляху від 1 до 10, якщо міряти множниками»",
              12, GREY, "middle", style="italic")
    save("fig-r04-4m-1-counter.svg", s)


def fig4m2_anchors():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 34, "Дві опорні точки — і вся таблиця збирається сама", 18, INK, "middle", "bold")
    s += _frame(60, 70, 200, 120, "запам'ятати")
    s += text(160, 110, "log 2 ≈ 0.301", 15, RED, "middle", "bold")
    s += text(160, 144, "log 3 ≈ 0.477", 15, BLUE, "middle", "bold")
    s += _frame(300, 70, 240, 250, "зібрати з них")
    rows = (("log 4 = 2·log 2", "≈ 0.602"),
            ("log 5 = 1 − log 2", "≈ 0.699"),
            ("log 6 = log 2 + log 3", "≈ 0.778"),
            ("log 8 = 3·log 2", "≈ 0.903"),
            ("log 9 = 2·log 3", "≈ 0.954"))
    for i, (f, v) in enumerate(rows):
        y = 105 + i * 42
        s += text(316, y, f, 12.5, INK, "start")
        s += text(524, y, v, 12.5, GREEN, "end", "bold")
    s += _frame(580, 70, 200, 250, "звідси драбина дБ")
    s += text(680, 106, "×2 потужності:", 12, INK, "middle")
    s += text(680, 126, "10·log 2 ≈ 3 дБ", 13, RED, "middle", "bold")
    s += text(680, 162, "×2 напруги:", 12, INK, "middle")
    s += text(680, 182, "20·log 2 ≈ 6 дБ", 13, RED, "middle", "bold")
    s += text(680, 218, "×10 напруги:", 12, INK, "middle")
    s += text(680, 238, "20·log 10 = 20 дБ", 13, RED, "middle", "bold")
    s += text(680, 274, "1 дБ = 10^0.05", 12, GREY, "middle")
    s += text(680, 292, "≈ ×1.12", 12, GREY, "middle")
    s += arrow(268, 130, 296, 130, INK, 2)
    s += arrow(548, 190, 576, 190, INK, 2)
    s += text(W / 2, 372, "«магічні числа» децибелів — це таблиця логарифмів, записана в інших одиницях:",
              12, GREY, "middle", style="italic")
    s += text(W / 2, 392, "хто тримає в голові 0.301 і 0.477, тому драбину дБ не треба зазубрювати",
              12, GREY, "middle", style="italic")
    save("fig-r04-4m-2-anchors.svg", s)


def fig4m3_log_axis():
    W, H = 820, 330
    s = header(W, H)
    s += text(W / 2, 34, "Лог-вісь: рівні відрізки — рівні множники", 18.5, INK, "middle", "bold")
    ox, oy, w = 90, 170, 640
    s += line(ox, oy, ox + w, oy, INK, 2.2)
    for n in range(1, 11):
        x = ox + math.log10(n) * w
        hgt = 10 if n in (1, 2, 3, 5, 10) else 6
        s += line(x, oy - hgt, x, oy + hgt, INK, 2 if hgt == 10 else 1.2)
        s += text(x, oy + 30, str(n), 12.5 if hgt == 10 else 10.5, INK if hgt == 10 else GREY, "middle",
                  "bold" if hgt == 10 else "normal")
    # дві дужки ×2: 2→4 і 5→10
    for a, b, lab in ((2, 4, "×2"), (5, 10, "×2")):
        xa, xb = ox + math.log10(a) * w, ox + math.log10(b) * w
        s += line(xa, oy - 38, xb, oy - 38, GREEN, 2.4)
        s += line(xa, oy - 38, xa, oy - 30, GREEN, 2)
        s += line(xb, oy - 38, xb, oy - 30, GREEN, 2)
        s += text((xa + xb) / 2, oy - 46, lab + " — однакова довжина", 11, "#1f6e33", "middle", "bold")
    xm = ox + 0.5 * w
    s += line(xm, oy - 14, xm, oy + 14, RED, 2, dash="4,3")
    s += text(xm, oy - 64, "середина декади = 10^0.5 ≈ 3.16,", 11.5, RED, "middle", "bold")
    s += text(xm, oy - 50, "а не 5.5!", 11.5, RED, "middle", "bold")
    s += text(W / 2, 250, "позиції для ока: 2 — на 30% декади (log 2), 3 — майже посередині (log 3 ≈ 0.48), 5 — на 70% (1 − log 2);",
              12, GREY, "middle", style="italic")
    s += text(W / 2, 270, "хто пам'ятає ці три точки — читає лог-осі діаграм Боде без сітки",
              12, GREY, "middle", style="italic")
    save("fig-r04-4m-3-log-axis.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  📜 Історія до §2.4.4 — Бел і «миля стандартного кабелю»
# ─────────────────────────────────────────────────────────────────────────────
def fig4i1_msc():
    W, H = 840, 420
    s = header(W, H)
    s += text(W / 2, 34, "«Миля стандартного кабелю»: еталон, який слухали вухом", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "якість будь-якої лінії виражали довжиною еталонного кабелю з таким самим загасанням",
              12.5, GREY, "middle", style="italic")
    # вимірювана лінія
    y1 = 150
    s += text(70, y1 - 26, "вимірювана лінія (місто A → місто B):", 12, INK, "start", "bold")
    s += line(70, y1, 430, y1, COPP, 3)
    s += circle(70, y1, 5, COPP, COPP, 0)
    s += circle(430, y1, 5, COPP, COPP, 0)
    s += text(250, y1 + 20, "загасання — ?", 11.5, GREY, "middle", style="italic")
    # еталон
    y2 = 260
    s += text(70, y2 - 30, "еталон у лабораторії: котушки «стандартного кабелю» по 1 милі:", 12, INK, "start", "bold")
    for i in range(0, 8):
        x = 80 + i * 46
        s += circle(x, y2, 16, "#fbfbfb", BLUE, 2)
        s += circle(x, y2, 7, LBLUE, BLUE, 1.4)
    s += text(80 + 8 * 46 + 10, y2 + 5, "… вмикаємо по одній,", 11, INK, "start")
    s += text(80 + 8 * 46 + 10, y2 + 22, "поки гучність не зрівняється", 11, INK, "start")
    # вухо-компаратор
    s += rect(560, y1 - 34, 220, 68, LGRN, GREEN, 1.8, 10)
    s += text(670, y1 - 8, "вимірювальний прилад:", 11, "#1f6e33", "middle", "bold")
    s += text(670, y1 + 14, "вухо телефоніста", 12.5, "#1f6e33", "middle", "bold")
    s += arrow(430, y1, 556, y1, GREY, 1.8)
    s += text(W / 2, 350, "«ця лінія звучить як 20 миль еталона» — і всі розуміли однаково; 1 миля ≈ найменша зміна гучності,",
              12, GREY, "middle", style="italic")
    s += text(W / 2, 370, "яку вухо взагалі помічає (~1 дБ сучасною мовою) — еталон ненавмисно влучив у поріг слуху",
              12, GREY, "middle", style="italic")
    save("fig-r04-4i-1-msc.svg", s)


def fig4i2_timeline():
    W, H = 860, 430
    s = header(W, H)
    s += text(W / 2, 34, "Триста років до децибела — і сто після", 18.5, INK, "middle", "bold")
    y = 200
    s += line(60, y, 800, y, INK, 2.4)
    events = (
        (95, "1614", "Непер публікує", "логарифми", BLUE, -1),
        (190, "1617", "Бріггс: таблиці", "за основою 10", GREY, 1),
        (300, "~1896", "«миля стандартного", "кабелю» в Bell", COPP, -1),
        (415, "1915", "лінія Нью-Йорк —", "Сан-Франциско", GREY, 1),
        (520, "1924", "TU: 10·log(P₁/P₂)", "(Мартін, BSTJ)", RED, -1),
        (625, "1928", "бел і непер:", "міжнародна угода", GREEN, 1),
        (700, "1929", "«децибел» — нове", "ім'я в BSTJ", RED, -1),
        (790, "нині", "dBm, дБ SPL,", "RSSI, аудіо…", INK, 1),
    )
    for x, yr, l1, l2, col, side in events:
        s += circle(x, y, 5.5, col, col, 0)
        yy = y - 64 if side < 0 else y + 38
        s += line(x, y + (8 if side > 0 else -8), x, yy - (0 if side > 0 else -26), GREY, 1.1, dash="3,3")
        s += text(x, yy - 30 if side < 0 else yy, yr, 13, col, "middle", "bold")
        s += text(x, (yy - 12 if side < 0 else yy + 18), l1, 10, INK, "middle")
        s += text(x, (yy + 2 if side < 0 else yy + 32), l2, 10, INK, "middle")
    s += text(W / 2, 350, "одиниця згадує одразу двох шотландців: непер — Джона Непера, що подарував світу логарифми,",
              12, GREY, "middle", style="italic")
    s += text(W / 2, 370, "а бел — Александра Грема Белла, який про одиницю свого імені так і не дізнався (він помер 1922-го)",
              12, GREY, "middle", style="italic")
    save("fig-r04-4i-2-timeline.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  🧮 Вставка до §2.4.2 — Передавальна функція RC
# ─────────────────────────────────────────────────────────────────────────────
def fig2m1_divider():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Той самий дільник — але плечі тепер комплексні опори", 18, INK, "middle", "bold")
    # компактна схема
    y = 150
    s += circle(70, y, 5, INK, INK, 0)
    s += text(70, y - 16, "V_вх", 11.5, BLUE, "middle", "bold")
    s += line(70, y, 120, y, INK, 2.2)
    s += rect(120, y - 10, 60, 20, "#f3f3f3", INK, 1.8)
    s += text(150, y - 18, "Z_R = R", 11.5, INK, "middle", "bold")
    s += line(180, y, 250, y, INK, 2.2)
    s += circle(250, y, 4, INK, INK, 0)
    s += line(250, y, 305, y, INK, 2.2)
    s += circle(305, y, 5, INK, INK, 0)
    s += text(305, y - 16, "V_вих", 11.5, GREEN, "middle", "bold")
    s += line(250, y, 250, y + 40, INK, 2)
    s += line(234, y + 44, 266, y + 44, INK, 2.6)
    s += line(234, y + 54, 266, y + 54, INK, 2.6)
    s += text(276, y + 53, "Z_C = 1/(jωC)", 11.5, INK, "start", "bold")
    s += line(250, y + 54, 250, y + 90, INK, 2)
    s += line(70, y + 90, 305, y + 90, INK, 2.2)
    # виведення
    x = 400
    s += text(x, 110, "формула дільника напруги — без змін:", 12.5, INK, "start")
    s += text(x, 140, "H(jω) = Z_C / (Z_R + Z_C)", 14.5, INK, "start", "bold")
    s += text(x, 178, "підставляємо опори:", 12.5, INK, "start")
    s += text(x, 208, "H = (1/(jωC)) / (R + 1/(jωC))", 14, INK, "start", "bold")
    s += text(x, 246, "множимо чисельник і знаменник на jωC:", 12.5, INK, "start")
    s += text(x, 280, "H(jω) = 1 / (1 + jωRC)", 16, RED, "start", "bold")
    s += text(W / 2, 330, "одна формула на все коло: у ній уже сидять і АЧХ (модуль), і ФЧХ (кут) — лишилося їх прочитати",
              12, GREY, "middle", style="italic")
    save("fig-r04-2m-1-divider.svg", s)


def fig2m2_vector():
    W, H = 840, 430
    s = header(W, H)
    s += text(W / 2, 34, "Знаменник 1 + jωRC на комплексній площині: три погоди", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "модуль H — одиниця, поділена на довжину стрілки; фаза H — мінус її кут",
              12.5, GREY, "middle", style="italic")

    def panel(ox, om, title, k_lab, ph_lab):
        oy, sc = 300, 150
        out = _frame(ox, 90, 230, 270, title)
        cx, cy = ox + 60, oy
        out += arrow(cx - 30, cy, cx + 175, cy, GREY, 1.4)
        out += arrow(cx, cy + 18, cx, cy - 165, GREY, 1.4)
        out += text(cx + 178, cy + 14, "Re", 10.5, GREY, "middle")
        out += text(cx - 14, cy - 158, "Im", 10.5, GREY, "middle")
        ex, ey = cx + sc * 0.85, cy - sc * 0.85 * om
        # компоненти
        out += line(cx, cy, cx + sc * 0.85, cy, COPP, 2.2)
        out += text(cx + sc * 0.42, cy + 16, "1", 11.5, COPP, "middle", "bold")
        if om > 0.05:
            out += line(cx + sc * 0.85, cy, ex, ey, BLUE, 2.2, dash="5,4")
            out += text(ex + 6, (cy + ey) / 2, "jωRC", 11, BLUE, "start", "bold")
        out += arrow(cx, cy, ex, ey, RED, 2.6)
        out += text(ex - 30, ey - 10, k_lab, 11, RED, "start", "bold")
        out += text(ox + 115, 348, ph_lab, 11, INK, "middle", "bold")
        return out

    s += panel(40, 0.12, "f << f_c", "|D| ≈ 1", "K ≈ 1,  φ ≈ 0°")
    s += panel(300, 1.0, "f = f_c", "|D| = √2", "K = 0.707,  φ = −45°")
    s += panel(560, 3.2, "f >> f_c", "|D| ≈ ωRC", "K ≈ f_c/f,  φ → −90°")
    s += text(W / 2, 398, "уся поведінка ФНЧ — полиця, точка 0.707/−45°, спад із запізненням 90° — це одна стрілка, що задирається з частотою",
              12, GREY, "middle", style="italic")
    save("fig-r04-2m-2-vector.svg", s)


def fig2m3_two_panels():
    W, H = 820, 430
    s = header(W, H)
    s += text(W / 2, 34, "Одна функція — обидві панелі діаграми Боде", 18.5, INK, "middle", "bold")
    s += text(W / 2, 70, "H(jω) = 1/(1 + jωRC)", 17, RED, "middle", "bold")
    s += arrow(330, 86, 220, 130, INK, 1.8)
    s += arrow(490, 86, 600, 130, INK, 1.8)
    s += text(255, 102, "модуль", 12, INK, "middle", "bold")
    s += text(565, 102, "кут", 12, INK, "middle", "bold")

    # ліва панель: |H|
    ox, oy, w, h = 80, 330, 290, 165
    s += _axes(ox, oy, w, h, "f (лог)", "|H|, дБ")
    pts = []
    for j in range(0, 201):
        lg = -1.5 + 3 * j / 200.0
        x = 10 ** lg
        k = 1 / math.sqrt(1 + x * x)
        pts.append((ox + (lg + 1.5) / 3.0 * w, oy - (20 * math.log10(k) + 45) / 45.0 * 0.9 * h))
    s += _poly(pts, GREEN, 2.5)
    s += text(ox + w / 2, oy + 24, "|H| = 1/√(1+(f/f_c)²)", 12.5, "#1f6e33", "middle", "bold")
    s += text(ox + w / 2, oy - h - 18, "АЧХ — Рис. 2.4.2.3", 11, GREY, "middle")

    # права панель: фаза
    ox2 = 460
    s += _axes(ox2, oy, w, h, "f (лог)", "φ")
    pts = []
    for j in range(0, 201):
        lg = -1.5 + 3 * j / 200.0
        ph = -math.degrees(math.atan(10 ** lg))
        pts.append((ox2 + (lg + 1.5) / 3.0 * w, oy - (ph + 95) / 95.0 * 0.9 * h))
    s += _poly(pts, BLUE, 2.5)
    for ph, lab in ((0, "0°"), (-45, "−45°"), (-90, "−90°")):
        yy = oy - (ph + 95) / 95.0 * 0.9 * h
        s += line(ox2, yy, ox2 + w, yy, FAINT, 1)
        s += text(ox2 - 6, yy + 4, lab, 10, GREY, "end")
    s += text(ox2 + w / 2, oy + 24, "φ = −arctan(f/f_c)", 12.5, BLUE, "middle", "bold")
    s += text(ox2 + w / 2, oy - h - 18, "ФЧХ — Рис. 2.4.2.5", 11, GREY, "middle")
    s += text(W / 2, 400, "тема діставала ці криві трикутником і таблицею — комплексний дріб видає обидві одним рухом",
              12, GREY, "middle", style="italic")
    save("fig-r04-2m-3-two-panels.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  🧮 Вставка до §2.4.6 — Чому −3 дБ = половина потужності
# ─────────────────────────────────────────────────────────────────────────────
def fig6m1_half_square():
    W, H = 800, 420
    s = header(W, H)
    s += text(W / 2, 34, "Потужність — це площа: половина площі ≠ половина сторони", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "P ∝ V², тож потужність зручно бачити квадратом зі стороною V",
              12.5, GREY, "middle", style="italic")
    # великий квадрат
    cx, cy, a = 230, 240, 180
    x0, y0 = cx - a / 2, cy - a / 2
    s += rect(x0, y0, a, a, LBLUE, BLUE, 2.2)
    # вписаний через середини сторін (половина площі)
    m = (
        (cx, y0), (x0 + a, cy), (cx, y0 + a), (x0, cy)
    )
    s += (f'<path d="M {m[0][0]},{m[0][1]} L {m[1][0]},{m[1][1]} L {m[2][0]},{m[2][1]} '
          f'L {m[3][0]},{m[3][1]} Z" fill="{LRED}" stroke="{RED}" stroke-width="2.2"/>\n')
    s += text(cx, y0 - 12, "сторона V — площа V² (уся потужність)", 12, BLUE, "middle", "bold")
    s += text(cx, cy + 6, "сторона V/√2 ≈ 0.707·V", 12, RED, "middle", "bold")
    s += text(cx, cy + 26, "площа рівно ПОЛОВИНА", 12, RED, "middle", "bold")
    # пояснення праворуч
    x = 480
    s += text(x, 150, "хочемо половину потужності:", 12.5, INK, "start")
    s += text(x, 184, "P/2 = (V_x)²/R   ⇒   V_x = V/√2", 14, INK, "start", "bold")
    s += text(x, 222, "1/√2 = 0.7071…", 14.5, RED, "start", "bold")
    s += text(x, 260, "перевірка квадратом:", 12.5, INK, "start")
    s += text(x, 290, "0.707² = 0.5  ✓", 13.5, GREEN, "start", "bold")
    s += text(x, 328, "а половина АМПЛІТУДИ (0.5·V)", 12.5, INK, "start")
    s += text(x, 348, "дала б лише чверть потужності!", 12.5, "#9a2b22", "start", "bold")
    s += text(W / 2, 394, "тому «впала на 30%» мовою напруг = «впала вдвічі» мовою потужностей — це та сама подія",
              12, GREY, "middle", style="italic")
    save("fig-r04-6m-1-half-square.svg", s)


def fig6m2_pythagoras():
    W, H = 820, 460
    s = header(W, H)
    s += text(W / 2, 34, "Чому фільтр на f_c віддає рівно половину: Піфагор", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "на частоті зрізу R = X_C — катети трикутника напруг рівні",
              12.5, GREY, "middle", style="italic")
    # трикутник напруг з квадратами на сторонах
    ox, oy = 250, 330
    leg = 150
    # катети: горизонтальний V_R, вертикальний V_C
    s += line(ox, oy, ox + leg, oy, COPP, 3)
    s += line(ox + leg, oy, ox + leg, oy - leg, BLUE, 3)
    s += line(ox, oy, ox + leg, oy - leg, RED, 3)
    s += rect(ox + leg - 16, oy - 16, 16, 16, "none", GREY, 1.2)
    # квадрати на катетах (половинки)
    s += rect(ox, oy + 6, leg, 44, LGRN, GREEN, 1.6)
    s += text(ox + leg / 2, oy + 33, "V_R² = 0.5", 12, "#1f6e33", "middle", "bold")
    s += rect(ox + leg + 6, oy - leg, 44, leg, LGRN, GREEN, 1.6)
    s += text(ox + leg + 28, oy - leg / 2, "0.5", 12, "#1f6e33", "middle", "bold")
    s += text(ox + leg / 2 - 14, oy - leg / 2 - 26, "V_вх = 1", 12.5, RED, "middle", "bold")
    s += text(ox + leg / 2, oy - 10, "V_R = 0.707", 11.5, COPP, "middle", "bold")
    s += text(ox + leg - 52, oy - leg + 18, "V_C = 0.707", 11.5, BLUE, "start", "bold")
    # арифметика праворуч
    x = 520
    s += text(x, 140, "Піфагор для напруг (§2.4.2):", 12.5, INK, "start")
    s += text(x, 170, "V_R² + V_C² = V_вх²", 14, INK, "start", "bold")
    s += text(x, 206, "на f_c катети рівні, тож", 12.5, INK, "start")
    s += text(x, 236, "V_C² = V_вх²/2", 14, RED, "start", "bold")
    s += text(x, 274, "квадрат напруги — це потужність:", 12.5, INK, "start")
    s += text(x, 304, "вихід несе половину", 13.5, GREEN, "start", "bold")
    s += text(x, 340, "у децибелах:", 12.5, INK, "start")
    s += text(x, 370, "10·log(0.5) = −3.01 дБ", 14, RED, "start", "bold")
    s += text(W / 2, 430, "одиниця квадрата вхідної амплітуди чесно розпадається на дві рівні половини — звідси і «точка половинної потужності»",
              12, GREY, "middle", style="italic")
    save("fig-r04-6m-2-pythagoras.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  🧮 Вставка до §2.4.6 — Фронт і смуга (0.35/t_rise)
# ─────────────────────────────────────────────────────────────────────────────
def fig6m3_step_rise():
    W, H = 820, 470
    s = header(W, H)
    s += text(W / 2, 34, "Сходинка крізь один полюс: звідки 2.2·τ", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "відповідь — експонента §2.1.4; лишається чесно зняти з неї точки 10% і 90%",
              12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 90, 360, 600, 250
    s += _axes(ox, oy, w, h, "t", "V")
    # експонента
    T = 5.2
    pts = []
    for j in range(0, 301):
        t = T * j / 300.0
        v = 1 - math.exp(-t)
        pts.append((ox + t / T * w, oy - v * 0.9 * h))
    s += _poly(pts, GREEN, 2.6)
    s += line(ox, oy - 0.9 * h, ox + w, oy - 0.9 * h, GREY, 1.1, dash="5,4")
    s += text(ox + w + 6, oy - 0.9 * h + 4, "100%", 10.5, GREY, "start")
    t10, t90 = math.log(10 / 9.0), math.log(10.0)
    for tv, frac, lab in ((t10, 0.1, "10%:  t₁₀ = τ·ln(10/9) ≈ 0.105·τ"),
                          (t90, 0.9, "90%:  t₉₀ = τ·ln(10) ≈ 2.303·τ")):
        x = ox + tv / T * w
        y = oy - frac * 0.9 * h
        s += line(x, oy, x, y, GREY, 1.2, dash="4,4")
        s += line(ox, y, x, y, GREY, 1.2, dash="4,4")
        s += circle(x, y, 4.5, RED, RED, 0)
        s += text(x + 10, y + (18 if frac < 0.5 else -10), lab, 11.5, INK, "start", "bold")
    xa, xb = ox + t10 / T * w, ox + t90 / T * w
    s += arrow(xa, oy + 28, xb, oy + 28, RED, 2)
    s += arrow(xb, oy + 28, xa, oy + 28, RED, 2)
    s += text((xa + xb) / 2, oy + 48, "t_r = τ·ln 9 ≈ 2.20·τ", 13, RED, "middle", "bold")
    s += text(W / 2, 442, "далі — заміна τ = 1/(2π·BW):  t_r = ln 9/(2π·BW) = 0.35/BW. Число 0.35 — це просто ln 9 поділити на 2π",
              12, GREY, "middle", style="italic")
    save("fig-r04-6m-3-step-rise.svg", s)


def fig6m4_rss():
    W, H = 820, 440
    s = header(W, H)
    s += text(W / 2, 34, "Фронти каскадів складаються, як катети: квадратично", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "t_r(тракту) = √(t_r₁² + t_r₂² + …) — Піфагор у часі",
              12.5, GREY, "middle", style="italic")
    # трикутник
    ox, oy = 140, 330
    l1, l2 = 240, 72   # 10 нс і 3 нс у масштабі
    s += line(ox, oy, ox + l1, oy, COPP, 3)
    s += line(ox + l1, oy, ox + l1, oy - l2, BLUE, 3)
    s += line(ox, oy, ox + l1, oy - l2, RED, 3)
    s += rect(ox + l1 - 14, oy - 14, 14, 14, "none", GREY, 1.2)
    s += text(ox + l1 / 2, oy + 22, "каскад 1:  t_r = 10 нс", 12, COPP, "middle", "bold")
    s += text(ox + l1 + 12, oy - l2 / 2, "каскад 2:  3 нс", 12, BLUE, "start", "bold")
    s += text(ox + l1 / 2 - 30, oy - l2 / 2 - 22, "разом: √(100 + 9) ≈ 10.4 нс", 12.5, RED, "middle", "bold")
    s += text(ox + l1 / 2, 130, "повільний катет майже все і вирішує:", 12.5, INK, "middle", "bold")
    s += text(ox + l1 / 2, 150, "швидкий каскад додав лише 4%", 12.5, INK, "middle")
    # віднімання приладу
    x = 540
    s += _frame(x, 110, 240, 250, "той самий Піфагор навспак")
    s += text(x + 120, 146, "осцилограф (BW 100 МГц):", 11.5, INK, "middle")
    s += text(x + 120, 166, "власний t_r ≈ 3.5 нс", 11.5, GREY, "middle")
    s += text(x + 120, 198, "на екрані фронт: 5.0 нс", 12, INK, "middle", "bold")
    s += text(x + 120, 234, "справжній фронт сигналу:", 11.5, INK, "middle")
    s += text(x + 120, 262, "√(5.0² − 3.5²) ≈ 3.6 нс", 13, RED, "middle", "bold")
    s += text(x + 120, 298, "прилад «додав» свій фронт —", 10.5, GREY, "middle")
    s += text(x + 120, 314, "квадратично його й віднімаємо", 10.5, GREY, "middle")
    s += text(W / 2, 408, "правило точне для «гладких» характеристик і чудова оцінка для звичайних однополюсних каскадів",
              12, GREY, "middle", style="italic")
    save("fig-r04-6m-4-rss.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §2.4.7 — LC- і RLC-фільтри; порядок фільтра
# ─────────────────────────────────────────────────────────────────────────────
def fig71_rc_stack():
    W, H = 800, 470
    s = header(W, H)
    s += text(W / 2, 34, "Чому не «просто ще один RC»: коліно м'якшає, а не гострішає", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "далекий спад справді крутіший, але перехід розмазується, а зріз тікає ліворуч",
              12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 100, 390, 580, 280

    def X(lg):
        return ox + (lg + 1.5) / 3.0 * w

    def Y(db):
        return oy - (db + 50) / 50.0 * 0.95 * h

    s += _axes(ox, oy, w, h, "f (лог)", "К, дБ")
    for db in (0, -3, -20, -40):
        s += line(ox, Y(db), ox + w, Y(db), FAINT, 1)
        s += text(ox - 8, Y(db) + 4, f"{db}", 10.5, GREY, "end")
    curves = (
        ("один RC", GREEN, lambda x: 1 / math.sqrt(1 + x * x)),
        ("два RC з буфером між ними", COPP, lambda x: 1 / (1 + x * x)),
        ("два RC впритул (навантажують один одного)", RED,
         lambda x: 1 / math.sqrt((1 - x * x) ** 2 + 9 * x * x)),
    )
    for lab, col, f in curves:
        pts = []
        for j in range(0, 301):
            lg = -1.5 + 3 * j / 300.0
            k = f(10 ** lg)
            pts.append((X(lg), Y(max(20 * math.log10(k), -48))))
        s += _poly(pts, col, 2.5)
    s += text(X(0.62), Y(-11), "−20 дБ/дек", 11, "#1f6e33", "start", "bold")
    s += text(X(0.30), Y(-26), "−40 дБ/дек", 11, "#7a4e1d", "start", "bold")
    s += text(X(-0.30), Y(-21), "ще м'якше коліно,", 10.5, "#9a2b22", "end", "bold")
    s += text(X(-0.30), Y(-25.5), "зріз поїхав ліворуч", 10.5, "#9a2b22", "end", "bold")
    s += circle(X(0), Y(-3), 4.5, GREEN, GREEN, 0)
    s += text(W / 2, 440, "перехідна зона лише ширшає: щоб коліно стало гострим, потрібен інакший елемент — не другий такий самий",
              12, GREY, "middle", style="italic")
    save("fig-r04-7-1-rc-stack.svg", s)


def _coil(x, y, n=4, r=10):
    p = f"M {x},{y} "
    for _ in range(n):
        p += f"a {r},{r} 0 0 1 {2 * r},0 "
    return f'<path d="{p}" fill="none" stroke="{INK}" stroke-width="2.2"/>\n'


def fig72_lc_circuit():
    W, H = 800, 420
    s = header(W, H)
    s += text(W / 2, 34, "LC-ФНЧ: завада дістає удар із двох боків", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "котушка в шляху закривається для високого, конденсатор додолу зливає те, що прорвалося",
              12.5, GREY, "middle", style="italic")
    y = 170
    s += circle(80, y, 5, INK, INK, 0)
    s += text(80, y - 18, "вхід", 12, BLUE, "middle", "bold")
    s += line(80, y, 180, y, INK, 2.4)
    s += _coil(180, y, 4, 11)
    s += text(224, y - 22, "L", 13, INK, "middle", "bold")
    s += line(268, y, 360, y, INK, 2.4)
    s += circle(360, y, 4, INK, INK, 0)
    s += line(360, y, 470, y, INK, 2.4)
    s += circle(470, y, 5, INK, INK, 0)
    s += text(470, y - 18, "вихід", 12, GREEN, "middle", "bold")
    s += line(360, y, 360, y + 48, INK, 2)
    s += line(344, y + 52, 376, y + 52, INK, 2.8)
    s += line(344, y + 62, 376, y + 62, INK, 2.8)
    s += text(386, y + 60, "C", 13, INK, "start", "bold")
    s += line(360, y + 62, 360, y + 100, INK, 2)
    s += line(80, y + 100, 560, y + 100, INK, 2.2)
    s += arrow(224, y - 58, 224, y - 34, RED, 1.8)
    s += text(224, y - 66, "X_L = 2πfL росте: шлях для швидкого ЗАКРИВАЄТЬСЯ", 11, "#9a2b22", "middle", "bold")
    s += arrow(430, y + 40, 380, y + 54, BLUE, 1.8)
    s += text(440, y + 42, "X_C падає: рештки швидкого — в землю", 11, BLUE, "start", "bold")
    s += rect(580, 120, 180, 130, "#fbfbfb", "#c9d3dc", 1.6, 8)
    s += text(670, 148, "два накопичувачі", 12, INK, "middle", "bold")
    s += text(670, 170, "енергії — два полюси:", 11.5, INK, "middle")
    s += text(670, 196, "−40 дБ/дек", 14, RED, "middle", "bold")
    s += text(670, 222, "замість −20 в RC", 11, GREY, "middle")
    s += text(W / 2, 370, "і жоден із двох не гріється: пара L–C не розсіює заваду, а відбиває її назад до джерела (§2.2.9)",
              12, GREY, "middle", style="italic")
    save("fig-r04-7-2-lc-circuit.svg", s)


def fig73_rc_vs_lc():
    W, H = 780, 450
    s = header(W, H)
    s += text(W / 2, 34, "Той самий зріз — удвічі крутіший схил", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "декада вище зрізу: RC лишив 10% сигналу, LC — лише 1%",
              12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 100, 370, 580, 260

    def X(lg):
        return ox + (lg + 1.5) / 3.0 * w

    def Y(db):
        return oy - (db + 80) / 80.0 * 0.95 * h

    s += _axes(ox, oy, w, h, "f (лог)", "К, дБ")
    for db in (0, -20, -40, -60, -80):
        s += line(ox, Y(db), ox + w, Y(db), FAINT, 1)
        s += text(ox - 8, Y(db) + 4, f"{db}", 10.5, GREY, "end")
    for col, lab, n in ((GREEN, "RC, 1-й порядок: −20 дБ/дек", 1),
                        (RED, "LC, 2-й порядок: −40 дБ/дек", 2)):
        pts = []
        for j in range(0, 301):
            lg = -1.5 + 3 * j / 300.0
            x = 10 ** lg
            k = 1 / math.sqrt(1 + x ** (2 * n))
            pts.append((X(lg), Y(max(20 * math.log10(k), -78))))
        s += _poly(pts, col, 2.6)
    s += text(X(0.70), Y(-16), "−20 дБ/дек", 11.5, "#1f6e33", "start", "bold")
    s += text(X(0.42), Y(-40), "−40 дБ/дек", 11.5, "#9a2b22", "start", "bold")
    s += line(X(1), oy, X(1), Y(-40), GREY, 1.1, dash="4,4")
    s += circle(X(1), Y(-20), 4.5, GREEN, GREEN, 0)
    s += circle(X(1), Y(-40), 4.5, RED, RED, 0)
    s += text(X(1) + 10, Y(-20) + 4, "−20 дБ (×0.1)", 11, "#1f6e33", "start", "bold")
    s += text(X(1) + 10, Y(-40) + 4, "−40 дБ (×0.01)", 11, "#9a2b22", "start", "bold")
    s += text(X(1), oy + 20, "10·f_c", 11.5, INK, "middle", "bold")
    s += text(W / 2, 422, "та сама частота зрізу, ті самі дві деталі в шляху сигналу — а тиша за зрізом у десять разів глибша",
              12, GREY, "middle", style="italic")
    save("fig-r04-7-3-rc-vs-lc.svg", s)


def fig74_order_family():
    W, H = 800, 470
    s = header(W, H)
    s += text(W / 2, 34, "Порядок фільтра: кожен накопичувач енергії додає −20 дБ/дек", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "порядок = кількість незалежних L і C = кількість полюсів = крутість далекого спаду",
              12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 100, 390, 580, 280

    def X(lg):
        return ox + (lg + 1.2) / 2.7 * w

    def Y(db):
        return oy - (db + 100) / 100.0 * 0.95 * h

    s += _axes(ox, oy, w, h, "f (лог)", "К, дБ")
    for db in (0, -20, -40, -60, -80, -100):
        s += line(ox, Y(db), ox + w, Y(db), FAINT, 1)
        s += text(ox - 8, Y(db) + 4, f"{db}", 10.5, GREY, "end")
    fam = ((1, GREEN, "1-й (RC): −20"),
           (2, COPP, "2-й (LC): −40"),
           (4, RED, "4-й (LC+LC): −80 дБ/дек"))
    for n, col, lab in fam:
        pts = []
        for j in range(0, 301):
            lg = -1.2 + 2.7 * j / 300.0
            x = 10 ** lg
            k = 1 / math.sqrt(1 + x ** (2 * n))
            pts.append((X(lg), Y(max(20 * math.log10(k), -98))))
        s += _poly(pts, col, 2.5)
    s += text(X(1.05), Y(-23), "1-й (RC)", 11, "#1f6e33", "start", "bold")
    s += text(X(0.82), Y(-42), "2-й (LC)", 11, "#7a4e1d", "start", "bold")
    s += text(X(0.52), Y(-62), "4-й (LC+LC)", 11, "#9a2b22", "start", "bold")
    s += text(W / 2, 440, "плата за порядок: більше деталей, допусків і дзвону біля зрізу — порядок беруть НЕ більший, ніж треба",
              12, GREY, "middle", style="italic")
    save("fig-r04-7-4-order-family.svg", s)


def fig75_q_character():
    W, H = 780, 460
    s = header(W, H)
    s += text(W / 2, 34, "Те саме LC — три характери коліна: все вирішує демпфування", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "опір у колі гасить резонанс пари L–C: мало опору — пік-дзвін, забагато — провисла полиця",
              12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 100, 380, 580, 270

    def X(lg):
        return ox + (lg + 1.3) / 2.6 * w

    def Y(db):
        return oy - (db + 50) / 62.0 * 0.95 * h

    s += _axes(ox, oy, w, h, "f (лог)", "К, дБ")
    for db in (10, 0, -20, -40):
        s += line(ox, Y(db), ox + w, Y(db), FAINT, 1)
        s += text(ox - 8, Y(db) + 4, f"{db:+d}" if db > 0 else f"{db}", 10.5, GREY, "end")
    fam = ((2.5, RED, "Q = 2.5: пік і дзвін на фронтах"),
           (0.707, GREEN, "Q ≈ 0.707: максимально плоска"),
           (0.3, COPP, "Q = 0.3: полиця провисає заздалегідь"))
    for qv, col, lab in fam:
        pts = []
        for j in range(0, 301):
            lg = -1.3 + 2.6 * j / 300.0
            x = 10 ** lg
            k = 1 / math.sqrt((1 - x * x) ** 2 + (x / qv) ** 2)
            pts.append((X(lg), Y(min(max(20 * math.log10(k), -48), 11))))
        s += _poly(pts, col, 2.5)
    s += text(X(-0.07), Y(9.5), "Q = 2.5: пік (дзвін на фронтах)", 11, "#9a2b22", "middle", "bold")
    s += text(X(-1.25), Y(-4.5), "Q ≈ 0.707: максимально плоска полиця", 11, "#1f6e33", "start", "bold")
    s += text(X(-1.25), Y(-12), "Q = 0.3: провисає задовго до зрізу", 11, "#7a4e1d", "start", "bold")
    s += text(W / 2, 430, "іменні форми з довідників — Баттерворт, Чебишов, Бессель — це і є різні домовленості про характер коліна",
              12, GREY, "middle", style="italic")
    save("fig-r04-7-5-q-character.svg", s)


def fig76_pi_t():
    W, H = 820, 430
    s = header(W, H)
    s += text(W / 2, 34, "π і Т: ті самі цеглинки, складені інакше", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "три накопичувачі — третій порядок, −60 дБ/дек; різниця — що фільтр «показує» джерелу й навантаженню",
              12.5, GREY, "middle", style="italic")

    def cap_down(x, y):
        out = line(x, y, x, y + 34, INK, 2)
        out += line(x - 15, y + 38, x + 15, y + 38, INK, 2.6)
        out += line(x - 15, y + 47, x + 15, y + 47, INK, 2.6)
        out += line(x, y + 47, x, y + 78, INK, 2)
        return out

    # π-фільтр (C–L–C)
    y = 170
    s += text(210, 110, "π-фільтр (C–L–C)", 13.5, INK, "middle", "bold")
    s += circle(70, y, 5, INK, INK, 0)
    s += line(70, y, 140, y, INK, 2.4)
    s += circle(140, y, 4, INK, INK, 0)
    s += cap_down(140, y)
    s += line(140, y, 175, y, INK, 2.4)
    s += _coil(175, y, 4, 9)
    s += text(211, y - 20, "L", 12.5, INK, "middle", "bold")
    s += line(247, y, 285, y, INK, 2.4)
    s += circle(285, y, 4, INK, INK, 0)
    s += cap_down(285, y)
    s += line(285, y, 350, y, INK, 2.4)
    s += circle(350, y, 5, INK, INK, 0)
    s += line(70, y + 78, 350, y + 78, INK, 2.2)
    s += text(210, y + 108, "улюбленець кіл живлення (§2.3.3):", 11, GREY, "middle")
    s += text(210, y + 124, "обом портам показує конденсатор", 11, GREY, "middle")

    # T-фільтр (L–C–L)
    s += text(610, 110, "Т-фільтр (L–C–L)", 13.5, INK, "middle", "bold")
    s += circle(470, y, 5, INK, INK, 0)
    s += line(470, y, 500, y, INK, 2.4)
    s += _coil(500, y, 4, 9)
    s += text(536, y - 20, "L", 12.5, INK, "middle", "bold")
    s += line(572, y, 610, y, INK, 2.4)
    s += circle(610, y, 4, INK, INK, 0)
    s += cap_down(610, y)
    s += line(610, y, 645, y, INK, 2.4)
    s += _coil(645, y, 4, 9)
    s += text(681, y - 20, "L", 12.5, INK, "middle", "bold")
    s += line(717, y, 750, y, INK, 2.4)
    s += circle(750, y, 5, INK, INK, 0)
    s += line(470, y + 78, 750, y + 78, INK, 2.2)
    s += text(610, y + 108, "обом портам показує котушку:", 11, GREY, "middle")
    s += text(610, y + 124, "м'якший до імпульсних джерел", 11, GREY, "middle")

    s += text(W / 2, 398, "пасивний LC розраховують під конкретні опори джерела й навантаження — з «чужими» опорами коліно дзвенить або провисає",
              12, GREY, "middle", style="italic")
    save("fig-r04-7-6-pi-t.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  🔌 Вставка до §2.4.1 — Щуп осцилографа 10:1
# ─────────────────────────────────────────────────────────────────────────────
def fig1c1_probe_inside():
    W, H = 860, 420
    s = header(W, H)
    s += text(W / 2, 34, "Щуп 10:1 зсередини: два дільники в одному корпусі", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "на постійному струмі ділять резистори, на високих частотах — конденсатори",
              12.5, GREY, "middle", style="italic")
    y = 190
    # наконечник
    s += circle(60, y, 6, RED, RED, 0)
    s += text(60, y - 18, "наконечник", 11, RED, "middle", "bold")
    s += line(60, y, 110, y, INK, 2.2)
    # R1 ∥ C1 (трим)
    s += rect(110, y - 26, 120, 52, "#fbfbfb", "#c9d3dc", 1.4, 6)
    s += rect(124, y - 19, 92, 14, "#f3f3f3", INK, 1.6)
    s += text(170, y - 24, "R1 = 9 МОм", 10.5, INK, "middle", "bold")
    s += line(124, y + 14, 162, y + 14, INK, 1.8)
    s += line(162, y + 8, 162, y + 20, INK, 2.2)
    s += line(170, y + 8, 170, y + 20, INK, 2.2)
    s += arrow(155, y + 30, 177, y + 2, GREY, 1.4)
    s += line(170, y + 14, 216, y + 14, INK, 1.8)
    s += text(170, y + 42, "C1 ≈ 12 пФ (трим — викрутка!)", 10, GREY, "middle")
    s += line(110, y, 124, y, INK, 1.6)
    s += line(216, y, 230, y, INK, 1.6)
    s += line(124, y, 124, y + 14, INK, 1.6)
    s += line(216, y, 216, y + 14, INK, 1.6)
    s += line(230, y, 300, y, INK, 2.2)
    # кабель
    s += rect(300, y - 16, 150, 32, LBLUE, BLUE, 1.4, 10)
    s += text(375, y - 24, "коаксіальний кабель", 10.5, BLUE, "middle", "bold")
    s += text(375, y + 4, "C_каб ≈ 90 пФ", 10.5, BLUE, "middle")
    s += line(450, y, 520, y, INK, 2.2)
    # вхід осцилографа
    s += rect(520, y - 56, 250, 112, "#fbfbfb", "#c9d3dc", 1.4, 8)
    s += text(645, y - 64, "вхід осцилографа", 11.5, INK, "middle", "bold")
    s += line(520, y, 600, y, INK, 1.8)
    s += circle(600, y, 3.5, INK, INK, 0)
    s += line(600, y, 670, y, INK, 1.8)
    s += rect(592, y + 8, 16, 36, "#f3f3f3", INK, 1.6)
    s += text(600, y + 58, "R2 = 1 МОм", 10, INK, "middle", "bold")
    s += line(600, y, 600, y + 8, INK, 1.6)
    s += line(670, y, 670, y + 14, INK, 1.6)
    s += line(652, y + 14, 688, y + 14, INK, 2.2)
    s += line(652, y + 23, 688, y + 23, INK, 2.2)
    s += text(694, y + 22, "C2 ≈ 20 пФ", 10, INK, "start", "bold")
    # земля
    s += line(60, y + 80, 770, y + 80, INK, 2.2)
    s += line(600, y + 44, 600, y + 80, INK, 1.6)
    s += line(670, y + 23, 670, y + 80, INK, 1.6)
    s += line(375, y + 16, 375, y + 80, BLUE, 1.4, dash="4,4")
    # умова компенсації
    s += text(W / 2, 330, "умова компенсації:  R1·C1 = R2·(C2 + C_каб)   →   9 МОм·12 пФ = 1 МОм·110 пФ  ✓",
              13, RED, "middle", "bold")
    s += text(W / 2, 358, "коло бачить лише 10 МОм і ~11 пФ замість 1 МОм і 110 пФ прямого шнура — ось головний виграш",
              12, GREY, "middle", style="italic")
    save("fig-r04-1c-1-probe-inside.svg", s)


def fig1c2_compensation():
    W, H = 840, 400
    s = header(W, H)
    s += text(W / 2, 34, "Підстроювання по меандру: три обличчя одного щупа", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "меандр містить усі частоти одразу (§2.4.1) — тому будь-який перекіс дільника видно з одного погляду",
              12.5, GREY, "middle", style="italic")

    def trace(ox, mode, col, t1, t2):
        oy, w, hh = 290, 220, 130
        out = _frame(ox, 90, 240, 250, "")
        per, amp = 70, 80
        pts = []
        x = ox + 12
        lvl_hi, lvl_lo = oy - hh, oy - hh + amp
        for k in range(0, 3):
            for half in (0, 1):
                y_t = lvl_hi if half == 0 else lvl_lo
                y_f = lvl_lo if half == 0 else lvl_hi
                sgn = 1 if half == 0 else -1
                for j in range(0, 36):
                    t = j / 35.0
                    if mode == "ok":
                        v = 0
                    elif mode == "under":
                        v = -sgn * 26 * math.exp(-t * 6) + 0
                    else:
                        v = sgn * 30 * math.exp(-t * 6)
                    pts.append((x + (k * 2 + half) * per / 2 + t * per / 2, y_t + v))
        out += _poly(pts, col, 2.3)
        out += text(ox + 120, 318, t1, 12, col, "middle", "bold")
        out += text(ox + 120, 334, t2, 10.5, GREY, "middle")
        return out

    s += trace(40, "under", BLUE, "недокомпенсований", "C1 замалий: верхи зрізані, плечі повзуть")
    s += trace(300, "ok", GREEN, "скомпенсований ✓", "рівний прямокутник: ділить 10:1 на всіх частотах")
    s += trace(560, "over", RED, "перекомпенсований", "C1 завеликий: «роги» — ВЧ проходить надміру")
    s += text(W / 2, 372, "крутіть трим-конденсатор щупа на клемі «PROBE COMP» (меандр ~1 кГц), доки роги чи завали не зникнуть",
              12, GREY, "middle", style="italic")
    save("fig-r04-1c-2-compensation.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  🔌 Вставка до §2.4.2 — RC на вході вимірювання
# ─────────────────────────────────────────────────────────────────────────────
def fig2c1_adc_rc():
    W, H = 840, 430
    s = header(W, H)
    s += text(W / 2, 34, "RC перед АЦП: пропустити давач, відсіяти ШІМ-сміття", 18, INK, "middle", "bold")
    # схема
    y = 130
    s += circle(80, y, 16, "#fbfbfb", INK, 2)
    s += text(80, y + 5, "~", 16, INK, "middle", "bold")
    s += text(80, y - 28, "давач (повільний)", 11, INK, "middle", "bold")
    s += line(96, y, 150, y, INK, 2.2)
    s += rect(150, y - 10, 80, 20, "#f3f3f3", INK, 1.8)
    s += text(190, y - 18, "R = 10 кОм", 11.5, INK, "middle", "bold")
    s += line(230, y, 320, y, INK, 2.2)
    s += circle(320, y, 4, INK, INK, 0)
    s += line(320, y, 400, y, INK, 2.2)
    s += rect(400, y - 26, 110, 52, "#fbfbfb", "#c9d3dc", 1.6, 8)
    s += text(455, y - 2, "АЦП", 13, INK, "middle", "bold")
    s += text(455, y + 16, "вхід MCU", 10, GREY, "middle")
    s += line(320, y, 320, y + 36, INK, 2)
    s += line(304, y + 40, 336, y + 40, INK, 2.6)
    s += line(304, y + 50, 336, y + 50, INK, 2.6)
    s += text(342, y + 50, "C = 160 нФ", 11, INK, "start", "bold")
    s += line(320, y + 50, 320, y + 80, INK, 2)
    s += line(80, y + 80, 510, y + 80, INK, 2.2)
    s += line(80, y + 16, 80, y + 80, INK, 2)
    s += text(620, y - 6, "f_c = 1/(2πRC) ≈ 100 Гц", 13, RED, "start", "bold")
    s += text(620, y + 18, "τ = RC = 1.6 мс", 11.5, GREY, "start")
    # вісь частот із зонами
    ox, oy, w = 110, 350, 620
    s += arrow(ox - 20, oy, ox + w + 24, oy, INK, 2)
    s += text(ox + w + 28, oy + 4, "f (лог)", 11.5, INK, "start", "bold")
    s += rect(ox, oy - 60, 130, 60, LGRN, "none", 0)
    s += text(ox + 65, oy - 70, "сигнал: 0…5 Гц", 11, "#1f6e33", "middle", "bold")
    xc = ox + (2.0 / 4.6) * w          # 100 Гц на осі 1 Гц…40 кГц
    s += line(xc, oy, xc, oy - 86, RED, 1.6, dash="5,4")
    s += text(xc, oy - 94, "зріз 100 Гц", 11, RED, "middle", "bold")
    pts = []
    for j in range(0, 201):
        t = j / 200.0
        lg = t * 4.6  # 1 Гц … 40 кГц приблизно
        k = 1 / math.sqrt(1 + (10 ** lg / 100.0) ** 2)
        pts.append((ox + t * w, oy - 8 - 52 * k))
    s += _poly(pts, COPP, 2.2)
    xp = ox + (math.log10(20000) / 4.6) * w
    s += line(xp, oy, xp, oy - 50, BLUE, 7)
    s += text(xp, oy + 18, "ШІМ 20 кГц", 11, BLUE, "middle", "bold")
    s += arrow(xp, oy - 50, xp, oy - 14, RED, 1.8)
    s += text(xp - 14, oy - 60, "−46 дБ (×0.005)", 11, RED, "end", "bold")
    s += text(ox + 65, oy + 18, "тут полиця: K ≈ 1", 10.5, GREY, "middle")
    save("fig-r04-2c-1-adc-rc.svg", s)


def fig2c2_tradeoff():
    W, H = 840, 400
    s = header(W, H)
    s += text(W / 2, 34, "Платня за гладкість — повільність: одна ручка RC", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "той самий сигнал зі сходинкою: без фільтра і з фільтром f_c = 100 Гц",
              12.5, GREY, "middle", style="italic")
    import random as _r
    _r.seed(7)

    def panel(ox, filt, col, lab1, lab2):
        oy, w, hh = 300, 340, 150
        out = _frame(ox, 90, 370, 250, "")
        base = oy - 40
        pts = []
        n = 240
        for j in range(0, n):
            t = j / (n - 1.0)
            step = 80 if t > 0.45 else 0
            if filt:
                v = step * (1 - math.exp(-(t - 0.45) * 28)) if t > 0.45 else 0
                noise = 2.0 * math.sin(t * 90) * 0.3
            else:
                v = step
                noise = _r.uniform(-11, 11)
            pts.append((ox + 15 + t * w, base - v + noise))
        out += _poly(pts, col, 1.8)
        out += text(ox + 185, 318, lab1, 12, col, "middle", "bold")
        out += text(ox + 185, 334, lab2, 10.5, GREY, "middle")
        return out

    s += panel(40, False, BLUE, "без фільтра", "АЦП ловить ±дрож: молодші біти скачуть")
    s += panel(430, True, GREEN, "з фільтром 100 Гц", "гладко, але сходинка доїжджає за ~5τ ≈ 8 мс")
    s += arrow(700, 218, 740, 218, RED, 1.8)
    s += text(700, 200, "5τ", 11.5, RED, "middle", "bold")
    s += text(W / 2, 372, "вибір f_c — компроміс: нижче зріз → чистіші покази, але повільніша реакція на справжню зміну",
              12, GREY, "middle", style="italic")
    save("fig-r04-2c-2-tradeoff.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  🔌 Вставка до §2.4.3 — Розділовий конденсатор в аудіотракті
# ─────────────────────────────────────────────────────────────────────────────
def fig3c1_audio_chain():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 34, "Аудіотракт: що нижчий опір за конденсатором — то він товщий", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "обидва розділові рахуються тією самою формулою f_c = 1/(2πRC) — лише R різний",
              12.5, GREY, "middle", style="italic")
    y = 170

    def cap_series(x, lab1, lab2, electro=False):
        out = line(x - 26, y, x - 5, y, INK, 2.2)
        out += line(x - 5, y - 14, x - 5, y + 14, INK, 2.8)
        if electro:
            out += (f'<path d="M {x + 7},{y - 14} a 18,18 0 0 0 0,28" fill="none" '
                    f'stroke="{INK}" stroke-width="2.8"/>\n')
            out += text(x - 14, y - 20, "+", 13, RED, "middle", "bold")
        else:
            out += line(x + 5, y - 14, x + 5, y + 14, INK, 2.8)
        out += line(x + 7, y, x + 28, y, INK, 2.2)
        out += text(x, y - 30, lab1, 11, INK, "middle", "bold")
        out += text(x, y + 34, lab2, 10, GREY, "middle")
        return out

    s += rect(50, y - 28, 110, 56, "#fbfbfb", "#c9d3dc", 1.6, 8)
    s += text(105, y - 3, "джерело", 11.5, INK, "middle", "bold")
    s += text(105, y + 14, "(DAC, 0 В DC)", 9.5, GREY, "middle")
    s += line(160, y, 204, y, INK, 2.2)
    s += cap_series(230, "C1 = 10 мкФ", "зріз 2 Гц на 10 кОм")
    s += line(258, y, 300, y, INK, 2.2)
    s += rect(300, y - 42, 150, 84, "#fbfbfb", "#c9d3dc", 1.6, 8)
    s += text(375, y - 18, "підсилювач", 12, INK, "middle", "bold")
    s += text(375, y + 2, "вхід 10 кОм", 10, GREY, "middle")
    s += text(375, y + 22, "вихід сидить на 2.5 В", 10, COPP, "middle", "bold")
    s += line(450, y, 494, y, INK, 2.2)
    s += cap_series(520, "C2 = 470 мкФ (електроліт)", "зріз 20 Гц на 32 Ом", electro=True)
    s += line(548, y, 600, y, INK, 2.2)
    s += circle(622, y, 20, "#fbfbfb", INK, 2)
    s += text(622, y + 5, "🎧", 16, INK, "middle")
    s += text(622, y + 40, "навушник 32 Ом, 0 В DC", 10, GREY, "middle")
    s += line(660, y - 26, 760, y - 26, INK, 0)
    s += text(740, y - 6, "", 10, GREY, "middle")
    # арифметика
    s += text(W / 2, 290, "C2 = 1/(2π·20 Гц·32 Ом) ≈ 250 мкФ  →  беруть 330–470 мкФ із запасом", 13, RED, "middle", "bold")
    s += text(W / 2, 318, "ті самі 20 Гц на вході 10 кОм коштували лише 1 мкФ: ємність росте обернено до опору навантаження —",
              11.5, GREY, "middle", style="italic")
    s += text(W / 2, 336, "ось чому в старих плеєрах біля гнізда навушників стояли «бочки», а міжкаскадні конденсатори дрібні",
              11.5, GREY, "middle", style="italic")
    save("fig-r04-3c-1-audio-chain.svg", s)


def fig3c2_thump():
    W, H = 840, 420
    s = header(W, H)
    s += text(W / 2, 34, "«Клац» при вмиканні: ФВЧ чесно диференціює стрибок робочої точки", 17.5, INK, "middle", "bold")
    ox, w = 130, 420
    # верхня панель: вихід підсилювача
    oy1 = 170
    s += text(70, 110, "вихід підсилювача (до C2):", 12, INK, "start", "bold")
    s += line(ox, oy1, ox + w, oy1, FAINT, 1)
    pts = [(ox, oy1)]
    for j in range(0, 200):
        t = j / 199.0
        v = 70 * (1 - math.exp(-max(t - 0.18, 0) * 18)) if t > 0.18 else 0
        ripple = 4 * math.sin(t * 110) if t > 0.55 else 0
        pts.append((ox + t * w, oy1 - v - ripple))
    s += _poly(pts, COPP, 2.4)
    s += text(ox + w + 12, oy1 - 66, "0 → 2.5 В: заряд", 11, COPP, "start", "bold")
    s += text(ox + w + 12, oy1 - 50, "робочої точки", 11, COPP, "start", "bold")
    s += text(ox + w + 12, oy1 - 28, "далі — музика", 10.5, GREY, "start")
    # нижня панель: навушник
    oy2 = 330
    s += text(70, 250, "навушник (після C2):", 12, INK, "start", "bold")
    s += line(ox, oy2, ox + w, oy2, FAINT, 1)
    pts = []
    for j in range(0, 240):
        t = j / 239.0
        if t <= 0.18:
            v = 0
        else:
            v = 55 * math.exp(-(t - 0.18) * 9) * (1 if t < 0.5 else 1)
        ripple = 4 * math.sin(t * 110) if t > 0.55 else 0
        pts.append((ox + t * w, oy2 - v - ripple))
    s += _poly(pts, RED, 2.4)
    s += text(ox + 0.26 * w, oy2 - 64, "«вус» ФВЧ = КЛАЦ у вухах", 11.5, RED, "middle", "bold")
    s += text(ox + w + 12, oy2 - 28, "потім DC заблоковано,", 10.5, GREY, "start")
    s += text(ox + w + 12, oy2 - 12, "лишається тільки звук", 10.5, GREY, "start")
    # ліки
    s += _frame(640, 110, 170, 250, "ліки")
    for i, t1 in enumerate(("повільний наростання", "живлення (soft-start)", "", "реле, що підключає", "навушники із затримкою", "", "вихід без C2 взагалі:", "двополярне живлення,", "вихід сидить на 0 В")):
        s += text(725, 140 + i * 24, t1, 10.5, INK, "middle")
    s += text(W / 2, 396, "той самий «вус» з Рис. 2.4.3.5 — лише тут він не на екрані осцилографа, а у вухах",
              12, GREY, "middle", style="italic")
    save("fig-r04-3c-2-thump.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  🔌 Вставка до §2.4.7 — Кросовер у колонці
# ─────────────────────────────────────────────────────────────────────────────
def fig7c1_crossover():
    W, H = 860, 460
    s = header(W, H)
    s += text(W / 2, 34, "Кросовер першого порядку: котушка басовику, конденсатор пищалці", 17.5, INK, "middle", "bold")
    # схема ліворуч
    y0 = 150
    s += rect(40, y0 - 30, 120, 60, "#fbfbfb", "#c9d3dc", 1.6, 8)
    s += text(100, y0 - 6, "підсилювач", 11.5, INK, "middle", "bold")
    s += text(100, y0 + 12, "(ампери!)", 9.5, GREY, "middle")
    s += line(160, y0, 210, y0, INK, 2.4)
    s += circle(210, y0, 4, INK, INK, 0)
    # гілка вуфера
    s += line(210, y0, 210, y0 - 55, INK, 2.2)
    s += line(210, y0 - 55, 240, y0 - 55, INK, 2.2)
    s += _coil(240, y0 - 55, 4, 9)
    s += text(276, y0 - 76, "L = 0.64 мГн", 10.5, INK, "middle", "bold")
    s += line(312, y0 - 55, 350, y0 - 55, INK, 2.2)
    s += circle(372, y0 - 55, 22, "#fbfbfb", INK, 2)
    s += circle(372, y0 - 55, 9, "#e8e8e8", INK, 1.4)
    s += text(372, y0 - 88, "вуфер 8 Ом", 10.5, INK, "middle", "bold")
    s += text(372, y0 - 22, "ФНЧ: бас проходить", 9.5, "#1f6e33", "middle")
    # гілка пищалки
    s += line(210, y0, 210, y0 + 55, INK, 2.2)
    s += line(210, y0 + 55, 250, y0 + 55, INK, 2.2)
    s += line(250, y0 + 47, 250, y0 + 63, INK, 2.6)
    s += line(258, y0 + 47, 258, y0 + 63, INK, 2.6)
    s += text(254, y0 + 78, "C = 10 мкФ", 10.5, INK, "middle", "bold")
    s += line(258, y0 + 55, 350, y0 + 55, INK, 2.2)
    s += circle(372, y0 + 55, 14, "#fbfbfb", INK, 2)
    s += circle(372, y0 + 55, 5, "#e8e8e8", INK, 1.4)
    s += text(372, y0 + 86, "пищалка 8 Ом", 10.5, INK, "middle", "bold")
    s += text(378, y0 + 30, "ФВЧ: захист від басів", 9.5, "#9a2b22", "middle")
    s += text(100, y0 + 96, "L = R/(2πf_c), C = 1/(2πf_c·R)", 10.5, GREY, "start")
    s += text(100, y0 + 114, "для f_c = 2 кГц і R = 8 Ом", 10.5, GREY, "start")
    # АЧХ праворуч
    ox, oy, w, h = 520, 300, 300, 190
    s += _axes(ox, oy, w, h, "f (лог)", "К, дБ")

    def X(lg):
        return ox + (lg - 1.8) / 2.6 * w

    def Y(db):
        return oy - (db + 24) / 24.0 * 0.9 * h

    for col, hp in ((GREEN, False), (RED, True)):
        pts = []
        for j in range(0, 201):
            lg = 1.8 + 2.6 * j / 200.0
            x = 10 ** lg / 2000.0
            k = 1 / math.sqrt(1 + (x if not hp else 1 / x) ** 2)
            pts.append((X(lg), Y(max(20 * math.log10(k), -23))))
        s += _poly(pts, col, 2.4)
    s += line(X(math.log10(2000)), oy, X(math.log10(2000)), Y(-3), GREY, 1.2, dash="4,4")
    s += circle(X(math.log10(2000)), Y(-3), 4, COPP, COPP, 0)
    s += text(X(math.log10(2000)), oy + 18, "2 кГц", 11, INK, "middle", "bold")
    s += text(X(2.05), Y(-6), "вуфер", 11, "#1f6e33", "start", "bold")
    s += text(X(3.85), Y(-6), "пищалка", 11, "#9a2b22", "end", "bold")
    s += text(X(math.log10(2000)) + 8, Y(-3) - 10, "−3 дБ обом", 10, COPP, "start", "bold")
    s += text(W / 2, 432, "перший порядок: м'які −6 дБ/октаву, смуги широко перекриваються; другий порядок ріже вдвічі крутіше —",
              11.5, GREY, "middle", style="italic")
    s += text(W / 2, 450, "але крутить фазу на 180°, тому пищалку тоді вмикають у протифазі (перевернуті клеми — не помилка монтажника!)",
              11.5, GREY, "middle", style="italic")
    save("fig-r04-7c-1-crossover.svg", s)


def fig7c2_impedance():
    W, H = 840, 440
    s = header(W, H)
    s += text(W / 2, 34, "Динамік — не резистор: «8 Ом» гуляють від 6 до 40", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "а пасивний LC-кросовер розраховано на сталий опір — тому поруч ставлять вирівнювальні ланки",
              12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 100, 350, 520, 240
    s += _axes(ox, oy, w, h, "f (лог)", "|Z|, Ом")

    def X(lg):
        return ox + (lg - 1.0) / 3.4 * w

    def Y(z):
        return oy - z / 45.0 * 0.95 * h

    for z in (8, 20, 40):
        s += line(ox, Y(z), ox + w, Y(z), FAINT, 1)
        s += text(ox - 8, Y(z) + 4, str(z), 10.5, GREY, "end")
    pts = []
    for j in range(0, 301):
        lg = 1.0 + 3.4 * j / 300.0
        f = 10 ** lg
        # резонанс підвіски ~55 Гц + ріст від індуктивності котушки
        zres = 30 / (1 + ((math.log10(f) - math.log10(55)) / 0.12) ** 2)
        zl = 0.004 * f ** 0.78
        z = 6.5 + zres + zl
        pts.append((X(lg), Y(min(z, 44))))
    s += _poly(pts, COPP, 2.6)
    s += text(X(math.log10(55)), Y(38) - 10, "резонанс підвіски ~55 Гц", 11, INK, "middle", "bold")
    s += text(X(3.9), Y(21), "ріст від індуктивності", 11, INK, "end", "bold")
    s += text(X(3.9), Y(17.5), "звукової котушки", 11, INK, "end", "bold")
    s += line(X(math.log10(300)), Y(7), X(math.log10(1200)), Y(7), GREEN, 2.4)
    s += text(X(math.log10(600)), Y(7) + 16, "тут майже чесні 8 Ом", 10.5, "#1f6e33", "middle", "bold")
    # Цобель
    s += _frame(660, 120, 150, 200, "ланка Цобеля")
    s += line(700, 150, 700, 175, INK, 2)
    s += rect(692, 175, 16, 40, "#f3f3f3", INK, 1.6)
    s += text(722, 198, "R ≈ 8 Ом", 10, INK, "start")
    s += line(700, 215, 700, 235, INK, 2)
    s += line(686, 239, 714, 239, INK, 2.4)
    s += line(686, 248, 714, 248, INK, 2.4)
    s += text(722, 246, "C ≈ 1 мкФ", 10, INK, "start")
    s += line(700, 248, 700, 268, INK, 2)
    s += text(735, 296, "паралельно динаміку:", 9.5, GREY, "middle")
    s += text(735, 310, "гасить ріст |Z| угорі", 9.5, GREY, "middle")
    s += text(W / 2, 408, "що ближче імпеданс до розрахункового, то чесніше працює кросовер — той самий закон узгодження з §2.4.7",
              12, GREY, "middle", style="italic")
    save("fig-r04-7c-2-impedance.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  ⚙️ Вставка до §2.4.5 — Зняти АЧХ власноруч
# ─────────────────────────────────────────────────────────────────────────────
def fig5a1_setup():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 34, "Установка: два канали, бо вхід теж пливе", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "ділимо ВИМІРЯНИЙ вихід на ВИМІРЯНИЙ вхід — і характеристика генератора випадає з результату",
              12.5, GREY, "middle", style="italic")
    y = 180
    s += rect(50, y - 35, 140, 70, "#fbfbfb", "#c9d3dc", 1.6, 8)
    s += text(120, y - 10, "генератор", 12, INK, "middle", "bold")
    s += text(120, y + 10, "синус, лог-кроки", 9.5, GREY, "middle")
    s += line(190, y, 280, y, INK, 2.4)
    s += circle(235, y, 4, INK, INK, 0)
    s += rect(280, y - 35, 150, 70, LGRN, GREEN, 1.8, 8)
    s += text(355, y - 8, "ваше коло", 12.5, "#1f6e33", "middle", "bold")
    s += text(355, y + 12, "(фільтр, підсилювач…)", 9.5, GREY, "middle")
    s += line(430, y, 520, y, INK, 2.4)
    s += circle(475, y, 4, INK, INK, 0)
    s += rect(520, y - 60, 180, 120, "#fbfbfb", "#c9d3dc", 1.6, 8)
    s += text(610, y - 36, "осцилограф", 12, INK, "middle", "bold")
    s += line(235, y, 235, y + 70, BLUE, 1.8, dash="5,4")
    s += line(235, y + 70, 545, y + 70, BLUE, 1.8, dash="5,4")
    s += line(545, y + 70, 545, y + 26, BLUE, 1.8, dash="5,4")
    s += text(556, y - 4, "CH1: A_вх", 11, BLUE, "start", "bold")
    s += line(475, y, 475, y + 48, RED, 1.8, dash="5,4")
    s += line(475, y + 48, 572, y + 48, RED, 1.8, dash="5,4")
    s += line(572, y + 48, 572, y + 26, RED, 1.8, dash="5,4")
    s += text(556, y + 18, "CH2: A_вих", 11, RED, "start", "bold")
    s += text(610, y + 44, "K = A_вих / A_вх", 11.5, INK, "middle", "bold")
    # табличка
    s += _frame(60, 280, 680, 84, "")
    s += text(80, 306, "f, Гц:", 11, GREY, "start", "bold")
    s += text(80, 332, "G, дБ:", 11, GREY, "start", "bold")
    for i, (fv, gv) in enumerate((("100", "0.0"), ("200", "−0.1"), ("500", "−0.9"), ("1к", "−3.1"),
                                  ("2к", "−7.0"), ("5к", "−14.2"), ("10к", "−20.1"), ("20к", "−26.0"))):
        x = 170 + i * 72
        s += text(x, 306, fv, 11, INK, "middle")
        s += text(x, 332, gv, 11, COPP, "middle", "bold")
    s += text(W / 2, 384, "кроки частоти — рівні МНОЖНИКИ (тут ×2…×2.5; для гладкої кривої — 10 точок на декаду, крок ×1.26)",
              11.5, GREY, "middle", style="italic")
    save("fig-r04-5a-1-setup.svg", s)


def fig5a2_read():
    W, H = 820, 460
    s = header(W, H)
    s += text(W / 2, 34, "Від точок до портрета: що шукати очима", 18.5, INK, "middle", "bold")
    ox, oy, w, h = 100, 380, 600, 280

    def X(lg):
        return ox + (lg - 1.7) / 2.8 * w

    def Y(db):
        return oy - (db + 30) / 30.0 * 0.95 * h

    s += _axes(ox, oy, w, h, "f (лог)", "G, дБ")
    for db in (0, -3, -10, -20):
        s += line(ox, Y(db), ox + w, Y(db), FAINT, 1)
        s += text(ox - 8, Y(db) + 4, f"{db}", 10.5, GREY, "end")
    # асимптоти
    s += line(X(1.7), Y(0), X(3.0), Y(0), GREY, 1.4, dash="7,5")
    s += line(X(3.0), Y(0), X(4.3), Y(-26), GREY, 1.4, dash="7,5")
    # крива
    pts = []
    for j in range(0, 201):
        lg = 1.7 + 2.8 * j / 200.0
        k = 1 / math.sqrt(1 + (10 ** lg / 1000.0) ** 2)
        pts.append((X(lg), Y(max(20 * math.log10(k), -29))))
    s += _poly(pts, COPP, 2.2)
    # виміряні точки: густіше біля коліна
    for fv in (60, 120, 250, 500, 700, 850, 1000, 1200, 1500, 2000, 3000, 6000, 12000):
        lg = math.log10(fv)
        k = 1 / math.sqrt(1 + (fv / 1000.0) ** 2)
        s += circle(X(lg), Y(max(20 * math.log10(k), -29)), 4.2, "#ffffff", RED, 2)
    s += text(X(2.2), Y(2.6), "полиця: 0 дБ", 11.5, "#1f6e33", "start", "bold")
    s += circle(X(3.0), Y(-3), 5, GREEN, GREEN, 0)
    s += text(X(3.0) + 10, Y(-3) + 16, "−3 дБ → це і є f_c", 11.5, "#1f6e33", "start", "bold")
    s += text(X(3.75), Y(-13), "нахил: −20 дБ", 11.5, INK, "start", "bold")
    s += text(X(3.75), Y(-16.6), "на декаду → 1 полюс", 11.5, INK, "start", "bold")
    s += text(X(2.95), Y(-22), "точки згущено там, де крива гнеться", 10.5, "#9a2b22", "middle", style="italic")
    s += text(W / 2, 430, "звірка з асимптотами (пунктир) — головна перевірка: якщо далекий нахил не кратний 20 дБ/дек, вимір бреше",
              12, GREY, "middle", style="italic")
    save("fig-r04-5a-2-read.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  🧮 Вставка до §2.4.7 — Каскадування фільтрів
# ─────────────────────────────────────────────────────────────────────────────
def fig7m1_ladder():
    W, H = 840, 430
    s = header(W, H)
    s += text(W / 2, 34, "Драбинка R–C–R–C: звідки в знаменнику «зайвий» доданок", 18, INK, "middle", "bold")
    # схема
    y = 150
    s += circle(60, y, 5, INK, INK, 0)
    s += text(60, y - 16, "вхід", 11, BLUE, "middle", "bold")
    s += line(60, y, 100, y, INK, 2.2)
    s += rect(100, y - 9, 54, 18, "#f3f3f3", INK, 1.7)
    s += text(127, y - 16, "R", 12, INK, "middle", "bold")
    s += line(154, y, 210, y, INK, 2.2)
    s += circle(210, y, 4, INK, INK, 0)
    s += text(210, y - 16, "A", 11.5, GREEN, "middle", "bold")
    s += line(210, y, 210, y + 34, INK, 2)
    s += line(196, y + 38, 224, y + 38, INK, 2.5)
    s += line(196, y + 47, 224, y + 47, INK, 2.5)
    s += text(230, y + 46, "C", 11.5, INK, "start", "bold")
    s += line(210, y + 47, 210, y + 76, INK, 2)
    s += line(210, y, 264, y, INK, 2.2)
    s += rect(264, y - 9, 54, 18, "#f3f3f3", INK, 1.7)
    s += text(291, y - 16, "R", 12, INK, "middle", "bold")
    s += line(318, y, 374, y, INK, 2.2)
    s += circle(374, y, 5, INK, INK, 0)
    s += text(374, y - 16, "вихід", 11, GREEN, "middle", "bold")
    s += line(374, y, 374, y + 34, INK, 2)
    s += line(360, y + 38, 388, y + 38, INK, 2.5)
    s += line(360, y + 47, 388, y + 47, INK, 2.5)
    s += text(394, y + 46, "C", 11.5, INK, "start", "bold")
    s += line(374, y + 47, 374, y + 76, INK, 2)
    s += line(60, y + 76, 420, y + 76, INK, 2.2)
    s += arrow(300, y + 110, 230, y + 56, RED, 1.8)
    s += text(308, y + 118, "друга ланка тягне струм із вузла A —", 11, "#9a2b22", "start", "bold")
    s += text(308, y + 134, "дільник першої ланки «просідає»", 11, "#9a2b22", "start", "bold")
    # формули праворуч
    x = 470
    s += text(x, 110, "з буфером між ланками (z = jf/f_c):", 12, INK, "start")
    s += text(x, 140, "H = 1/(z² + 2z + 1)", 14, GREEN, "start", "bold")
    s += text(x, 178, "драбинка впритул (рівні R і C):", 12, INK, "start")
    s += text(x, 208, "H = 1/(z² + 3z + 1)", 14, RED, "start", "bold")
    s += text(x, 246, "уся різниця — один доданок:", 12, INK, "start")
    s += text(x, 276, "2z  →  3z", 14.5, INK, "start", "bold")
    s += text(x, 306, "це і є взаємне навантаження,", 12, INK, "start")
    s += text(x, 324, "записане однією літерою", 12, INK, "start")
    s += text(W / 2, 392, "на f_c: буферизовані дають |2j| → −6 дБ, драбинка |3j| → −9.5 дБ — коліно не гострішає, а тоне",
              12, GREY, "middle", style="italic")
    save("fig-r04-7m-1-ladder.svg", s)


def fig7m2_three_denominators():
    W, H = 800, 470
    s = header(W, H)
    s += text(W / 2, 34, "Три знаменники біля коліна — і рятунок «драбинкою вгору»", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "другий каскад у 10 разів високоомніший (R×10, C÷10): та сама f_c, а навантаження майже зникло",
              12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 100, 390, 580, 280

    def X(lg):
        return ox + (lg + 1.5) / 2.5 * w

    def Y(db):
        return oy - (db + 40) / 40.0 * 0.95 * h

    s += _axes(ox, oy, w, h, "f (лог)", "К, дБ")
    for db in (0, -3, -6, -9.5, -20, -40):
        s += line(ox, Y(db), ox + w, Y(db), FAINT, 1)
        s += text(ox - 8, Y(db) + 4, f"{db:g}", 10, GREY, "end")
    curves = ((2.0, GREEN, None, "з буфером: z²+2z+1"),
              (2.1, COPP, "7,5", "драбинка ×10: z²+2.1z+1"),
              (3.0, RED, None, "впритул: z²+3z+1"))
    for b, col, dash, lab in curves:
        pts = []
        for j in range(0, 301):
            lg = -1.5 + 2.5 * j / 300.0
            x = 10 ** lg
            den = math.hypot(1 - x * x, b * x)
            pts.append((X(lg), Y(max(20 * math.log10(1 / den), -38))))
        s += _poly(pts, col, 2.5, dash=dash)
    s += text(X(0.30), Y(-13), "впритул", 11.5, "#9a2b22", "start", "bold")
    s += text(X(0.62), Y(-23), "буфер і ×10 — майже одне", 11.5, "#1f6e33", "start", "bold")
    s += circle(X(0), Y(-6), 4.5, GREEN, GREEN, 0)
    s += circle(X(0), Y(-9.5), 4.5, RED, RED, 0)
    s += text(X(0) + 10, Y(-6) - 8, "−6", 10.5, "#1f6e33", "start", "bold")
    s += text(X(0) + 10, Y(-9.5) + 14, "−9.5", 10.5, "#9a2b22", "start", "bold")
    s += text(W / 2, 440, "коефіцієнт при z — то «демпфування» пари: 2 = ідеал, 2.1 = драбинка ×10 (похибка ~5%), 3 = рівні ланки впритул",
              11.5, GREY, "middle", style="italic")
    save("fig-r04-7m-2-three-denominators.svg", s)


if __name__ == "__main__":
    # Історія до Розділу 2.4 — Боде
    fig0_trio()
    fig0_bode_idea()
    # §2.4.1 Коло як фільтр
    fig11_square_sum()
    fig11_concept()
    fig11_rc_three()
    fig11_four_shapes()
    fig11_phase_matters()
    fig11_everything_filters()
    # §2.4.2 RC-ФНЧ
    fig21_circuit()
    fig22_triangle()
    fig23_curve()
    fig24_asymptotes()
    fig25_phase()
    fig26_two_languages()
    fig27_loading()
    # §2.4.3 RC-ФВЧ
    fig31_circuit()
    fig32_formula()
    fig33_curve()
    fig34_phase()
    fig35_square()
    fig36_coupling()
    # §2.4.4 Децибели
    fig41_why_log()
    fig42_ladder()
    fig43_20log()
    fig44_cascade()
    fig45_slopes()
    fig46_dbm()
    # §2.4.5 Діаграма Боде
    fig51_full_bode()
    fig52_alphabet()
    fig53_build()
    fig54_phase_build()
    fig55_read_opamp()
    fig56_second_order()
    # §2.4.6 Смуга і −3 дБ
    fig61_bw_def()
    fig62_risetime()
    fig63_cascade_shrink()
    fig64_bp_q()
    fig65_margin()
    # 🧮 вставка до §2.4.2 — передавальна функція
    fig2m1_divider()
    fig2m2_vector()
    fig2m3_two_panels()
    # 🧮 вставка до §2.4.6 — половина потужності
    fig6m1_half_square()
    fig6m2_pythagoras()
    # 🧮 вставка до §2.4.6 — фронт і смуга
    fig6m3_step_rise()
    fig6m4_rss()
    # 📜 історія до §2.4.4 — бел і миля кабелю
    fig4i1_msc()
    fig4i2_timeline()
    # 🧮 вставка до §2.4.4 — логарифми
    fig4m1_counter()
    fig4m2_anchors()
    fig4m3_log_axis()
    # 🔌 вставка до §2.4.1 — щуп 10:1
    fig1c1_probe_inside()
    fig1c2_compensation()
    # 🔌 вставка до §2.4.2 — RC на вході вимірювання
    fig2c1_adc_rc()
    fig2c2_tradeoff()
    # 🔌 вставка до §2.4.3 — розділовий конденсатор
    fig3c1_audio_chain()
    fig3c2_thump()
    # 🔌 вставка до §2.4.7 — кросовер
    fig7c1_crossover()
    fig7c2_impedance()
    # ⚙️ вставка до §2.4.5 — зняти АЧХ власноруч
    fig5a1_setup()
    fig5a2_read()
    # 🧮 вставка до §2.4.7 — каскадування
    fig7m1_ladder()
    fig7m2_three_denominators()
    # §2.4.7 LC/RLC і порядок фільтра
    fig71_rc_stack()
    fig72_lc_circuit()
    fig73_rc_vs_lc()
    fig74_order_family()
    fig75_q_character()
    fig76_pi_t()
    print("OK — фігури Розділу 2.4 (історія + §2.4.1–2.4.7) згенеровано в", OUT)
