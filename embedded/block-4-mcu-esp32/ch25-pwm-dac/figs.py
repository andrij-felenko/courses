# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 25 — «PWM і ЦАП» (Модуль 4).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи нумеруються посекційно
(Рис. C.S.N) у тексті розділу.

Скрипт нарощується по ітераціях: кожна тема додає свої функції-фігури.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра ─────────────────────────────────────────────────────────────────
RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LAMB  = "#fff6e0"
METAL = "#9a9aa0"
GOLD  = "#caa24a"
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


def poly(points, color=INK, w=2, fill="none", dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return (f'<polyline points="{pts}" fill="{fill}" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round" stroke-linecap="round"/>\n')


def pwm(x, y0, y1, w, duty, n, col=BLUE):
    """Прямокутна хвиля: n періодів ширини w, частка duty висока."""
    pts = [(x, y1)]
    cx = x
    for i in range(n):
        hi = w * duty
        pts += [(cx, y0), (cx + hi, y0), (cx + hi, y1), (cx + w, y1)]
        cx += w
    return poly(pts, col, 2.4)


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ═════════════════════════════════════════════════════════════════════════════
# §25.1 ШІМ: «вдавати» аналог — fig-25-1-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 25.1.1 — ніжка вміє лише 0 або максимум ─────────────────────────────
def fig11_only_on_off():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 32, "Цифрова ніжка вміє лише 0 або максимум — а треба «між»", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "digitalWrite дає тільки HIGH чи LOW; як же дістати половину яскравості чи пів-швидкості?", 10.5, GREY, "middle", style="italic")
    # dial 0..max with desired 50%
    cx, cy, r = 250, 200, 80
    s += f'<path d="M {cx-r} {cy} A {r} {r} 0 0 1 {cx+r} {cy}" fill="none" stroke="{GREY}" stroke-width="3"/>\n'
    s += text(cx - r, cy + 22, "0", 12, BLUE, "middle", "bold")
    s += text(cx + r, cy + 22, "макс", 12, RED, "middle", "bold")
    s += line(cx, cy, cx, cy - r, GREEN, 2.4)
    s += text(cx, cy - r - 8, "хочемо 50%", 10, GREEN, "middle", "bold")
    s += circle(cx, cy, 5, INK, INK, 0)
    s += text(cx, cy + 50, "цифрова ніжка тут стрибає", 9.5, INK, "middle")
    s += text(cx, cy + 66, "лише між КРАЯМИ", 9.5, RED, "middle", "bold")
    s += rect(520, 130, 360, 140, "none", FAINT, 1.6, 12)
    s += text(700, 158, "Потрібне «середнє»:", 11.5, INK, "middle", "bold")
    s += text(540, 186, "• світлодіод — на пів-яскравості", 10.5, INK, "start")
    s += text(540, 210, "• мотор — на пів-швидкості", 10.5, INK, "start")
    s += text(540, 234, "• нагрівач — на пів-потужності", 10.5, INK, "start")
    s += text(700, 262, "а ніжка дає лише 0 або повне!", 9.5, RED, "middle", "bold")
    s += text(W / 2, 330, "Розв'язок хитрий: швидко вмикати й вимикати — і керувати ЧАСТКОЮ часу «увімкнено».", 10.3, INK, "middle", "bold")
    save("fig-25-1-1-only-on-off.svg", s)


# ── Рис. 25.1.2 — ідея ШІМ ───────────────────────────────────────────────────
def fig12_pwm_idea():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Ідея ШІМ: перемикай швидко — середнє і є «аналог»", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "сигнал стрибає 0↔макс дуже часто; яку частку часу він «увімкнено», таке й середнє", 10.5, GREY, "middle", style="italic")
    ox = 90
    y0, y1 = 110, 230
    s += line(ox - 6, y0, 880, y0, FAINT, 1.4)
    s += text(64, y0 + 4, "макс", 9, RED, "end", "bold")
    s += line(ox - 6, y1, 880, y1, FAINT, 1.4)
    s += text(64, y1 + 4, "0", 9, BLUE, "end", "bold")
    s += pwm(ox, y0, y1, 110, 0.5, 7, BLUE)
    # average line
    yavg = (y0 + y1) / 2
    s += line(ox, yavg, 860, yavg, GREEN, 2.4, dash="7,4")
    s += text(866, yavg + 4, "середнє = 50%", 10, GREEN, "start", "bold")
    s += arrow(300, 280, 300, 234, GREEN, 1.8)
    s += text(300, 298, "половину часу — увімк.", 9, INK, "middle")
    s += rect(150, 320, 660, 50, LAMB, GOLD, 1.4, 10)
    s += text(480, 346, "Навантаження (око, мотор, нагрівач) не встигає за швидкими стрибками — воно «бачить» СЕРЕДНЄ.", 10, INK, "middle", "bold")
    s += text(480, 364, "Тож 50% часу «увімк.» = пів-яскравості, пів-швидкості. Це й є ШІМ (PWM).", 9.5, GREY, "middle")
    save("fig-25-1-2-pwm-idea.svg", s)


# ── Рис. 25.1.3 — шпаруватість (duty cycle) ──────────────────────────────────
def fig13_duty_cycle():
    W, H = 960, 410
    s = header(W, H)
    s += text(W / 2, 32, "Шпаруватість (duty cycle): яку частку періоду сигнал «увімкнено»", 16.5, INK, "middle", "bold")
    s += text(W / 2, 54, "0% — завжди вимк., 100% — завжди увімк., між ними — будь-яке середнє", 11, GREY, "middle", style="italic")
    duties = [("0%", 0.0), ("25%", 0.25), ("50%", 0.5), ("75%", 0.75), ("100%", 1.0)]
    bw = 175
    for i, (lab, d) in enumerate(duties):
        ox = 40 + i * 182
        y0, y1 = 110, 175
        s += text(ox + bw / 2, 96, lab, 12, INK, "middle", "bold")
        s += rect(ox, y0 - 4, bw, y1 - y0 + 8, "none", FAINT, 1.2, 4)
        s += pwm(ox, y0, y1, bw / 2, d, 2, BLUE)
        # average bar
        yavg = y1 - (y1 - y0) * d
        s += line(ox, yavg, ox + bw, yavg, GREEN, 2, dash="5,3")
        s += rect(ox + bw / 2 - 30, 210, 60, 110 * d + 0.5 if d > 0 else 2, LGRN, GREEN, 1.2)
        s += text(ox + bw / 2, 336, "середнє", 8.5, GREEN, "middle")
    s += text(W / 2, 372, "Шпаруватість — головна «ручка» ШІМ: міняєш її — плавно міняється середній рівень.", 10.3, INK, "middle", "bold")
    s += text(W / 2, 392, "(період той самий, рухається лише частка «увімкнено»)", 9.3, GREY, "middle")
    save("fig-25-1-3-duty-cycle.svg", s)


# ── Рис. 25.1.4 — формула середнього ─────────────────────────────────────────
def fig14_average_formula():
    W, H = 940, 340
    s = header(W, H)
    s += text(W / 2, 32, "Середнє = шпаруватість × напруга живлення", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "проста пряма залежність: подвоїв частку «увімк.» — подвоїв середню напругу", 11, GREY, "middle", style="italic")
    s += rect(120, 90, 700, 56, "#0f1115", INK, 1.6, 10)
    s += '<text x="470" y="126" font-family="Consolas, monospace" font-size="18" fill="#e8e8e8" text-anchor="middle" font-weight="bold">U_серед = шпаруватість × U_живлення</text>\n'
    s += text(470, 184, "Приклад: 50% на 3.3 В", 13, INK, "middle", "bold")
    s += rect(120, 202, 700, 70, "none", FAINT, 1.6, 10)
    s += text(140, 230, "шпаруватість = 0.5,  живлення = 3.3 В", 11, INK, "start")
    s += text(140, 256, "U_серед = 0.5 × 3.3 = 1.65 В", 12, GREEN, "start", "bold")
    s += text(640, 244, "75% → 2.48 В", 10, GREY, "middle")
    s += text(640, 262, "25% → 0.83 В", 10, GREY, "middle")
    s += text(W / 2, 312, "Хочеш конкретний середній рівень — поділи його на живлення, дістанеш потрібну шпаруватість.", 10.3, INK, "middle", "bold")
    save("fig-25-1-4-average-formula.svg", s)


# ── Рис. 25.1.5 — навантаження усереднює ─────────────────────────────────────
def fig15_load_averages():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Чому це працює: навантаження саме «згладжує» імпульси", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "перемикання швидше, ніж устигає реагувати око чи мотор — тож вони бачать середнє", 10.5, GREY, "middle", style="italic")
    # pulses in
    ox = 80
    s += text(64, 110, "ШІМ →", 10, BLUE, "start", "bold")
    s += pwm(140, 110, 160, 50, 0.4, 5, BLUE)
    s += arrow(400, 135, 470, 135, INK, 2.2)
    items = [("око", "інерція зору", "бачить рівну яскравість"),
             ("мотор", "інерція маси", "крутиться рівно"),
             ("нагрівач", "теплова інерція", "гріє рівно")]
    for i, (t, why, res) in enumerate(items):
        y = 110 + i * 80
        s += rect(490, y - 18, 160, 56, "#fbfcff", GREEN, 1.6, 8)
        s += text(570, y + 2, t, 11, GREEN, "middle", "bold")
        s += text(570, y + 22, why, 8.7, GREY, "middle")
        s += text(680, y + 6, "→ " + res, 9.5, INK, "start")
    s += rect(140, 300, 680, 64, LAMB, GOLD, 1.4, 10)
    s += text(480, 326, "Якби перемикання було повільним, ми б бачили блимання. Швидке ж — зливається в рівне.", 10, INK, "middle", "bold")
    s += text(480, 348, "Тому в ШІМ важлива не лише шпаруватість, а й достатньо ВИСОКА частота (про це далі).", 9.5, GREY, "middle")
    save("fig-25-1-5-load-averages.svg", s)


# ── Рис. 25.1.6 — ШІМ родом із таймера ───────────────────────────────────────
def fig16_pwm_from_timer():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "ШІМ родом із таймера: порівняння з §24.3 у дії", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "лічильник рахує до ВЕРХУ (період); поки він менший за поріг — ніжка увімк., далі — вимк.", 10, GREY, "middle", style="italic")
    ox, oy = 90, 220
    s += arrow(ox, oy, 880, oy, INK, 2)
    # sawtooth counter
    saw = [(ox, oy), (250, 90), (250, oy), (470, 90), (470, oy), (690, 90), (690, oy)]
    s += poly(saw, GREEN, 2)
    s += text(64, 100, "лічильник", 9.5, GREEN, "start", "bold")
    s += line(ox, 160, 760, 160, GOLD, 1.6, dash="5,3")
    s += text(764, 164, "поріг = шпаруватість", 9.5, "#8a6a14", "start", "bold")
    # output below
    yo = 300
    s += text(64, 290, "ніжка", 9.5, BLUE, "start", "bold")
    # high while counter<threshold within each ramp
    # threshold crossing at fraction (oy-160)/(oy-90)
    frac = (oy - 160) / (oy - 90)
    seg = []
    for base in (ox, 250, 470, 690):
        hi = (250 - ox) * frac if base != 690 else 0
        seg += [(base, yo), (base + hi, yo), (base + hi, yo + 34), (min(base + (250 - ox), 760), yo + 34)] if base != 690 else []
    sq = [(ox, yo)]
    period = 220
    for base in (ox, 250, 470):
        hi = period * frac
        sq += [(base, yo), (base + hi, yo), (base + hi, yo + 34), (base + period, yo + 34)]
    s += poly(sq, BLUE, 2.6)
    for x in (ox, 250, 470, 690):
        s += line(x, 160, x, yo + 34, FAINT, 1, "3,3")
    s += text(W / 2, 362, "Підняв поріг — ширший імпульс (більша шпаруватість); опустив — вужчий. Усе апаратно.", 10.3, INK, "middle", "bold")
    s += text(W / 2, 384, "ШІМ — це режим порівняння таймера (§24.3): процесор не бере участі, лише задає поріг.", 9.5, GREY, "middle")
    save("fig-25-1-6-pwm-from-timer.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §25.2 Як таймер генерує PWM апаратно — fig-25-2-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 25.2.1 — механізм ШІМ із лічильника ─────────────────────────────────
def fig21_pwm_mechanism():
    W, H = 960, 420
    s = header(W, H)
    s += text(W / 2, 32, "Механізм ШІМ: лічильник, ВЕРХ і поріг порівняння", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "на початку періоду ніжка — увімк.; на збігу з порогом — вимк.; на ВЕРХУ — знову увімк.", 10.5, GREY, "middle", style="italic")
    ox, oy = 90, 230
    s += arrow(ox, oy, 900, oy, INK, 2)
    period = 220
    top = 90
    saw = []
    for k in range(3):
        bx = ox + k * period
        saw += [(bx, oy), (bx + period, top)]
    s += poly(saw, GREEN, 2.2)
    s += text(64, 100, "лічильник", 9.5, GREEN, "start", "bold")
    s += line(ox, top, 760, top, GREY, 1, "3,3")
    s += text(ox - 6, top - 4, "ВЕРХ", 9, GREY, "end", "bold")
    # compare line
    cmp_y = 165
    s += line(ox, cmp_y, 760, cmp_y, GOLD, 1.6, dash="5,3")
    s += text(764, cmp_y + 4, "поріг (compare)", 9.5, "#8a6a14", "start", "bold")
    # output
    yo = 320
    s += text(64, 310, "ніжка", 9.5, BLUE, "start", "bold")
    frac = (oy - cmp_y) / (oy - top)
    sq = [(ox, yo - 34)]
    for k in range(3):
        bx = ox + k * period
        hi = period * frac
        sq += [(bx, yo - 34), (bx + hi, yo - 34), (bx + hi, yo), (bx + period, yo)]
    s += poly(sq, BLUE, 2.6)
    for k in range(4):
        x = ox + k * period
        s += line(x, top, x, yo, FAINT, 1, "3,3")
        if k < 3:
            s += text(x + 4, yo - 38, "увімк", 8, BLUE, "start", "bold")
    for k in range(3):
        x = ox + k * period + period * frac
        s += line(x, cmp_y, x, yo, "#e6c88a", 1, "3,3")
    s += text(W / 2, 388, "ВЕРХ задає період (частоту), поріг — шпаруватість. Усе формує лічильник, без коду.", 10.3, INK, "middle", "bold")
    save("fig-25-2-1-pwm-mechanism.svg", s)


# ── Рис. 25.2.2 — дві ручки: ВЕРХ і поріг ────────────────────────────────────
def fig22_two_knobs():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Дві ручки: ВЕРХ керує частотою, поріг — шпаруватістю", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "це два окремі регістри; міняєш один — міняється одне, не зачіпаючи інше", 11, GREY, "middle", style="italic")
    s += rect(60, 90, 400, 230, "none", BLUE, 1.8, 12)
    s += text(260, 116, "Регістр ВЕРХУ (період)", 12, BLUE, "middle", "bold")
    s += text(82, 146, "скільки лічити до скиду", 10, INK, "start")
    s += text(82, 168, "→ задає ПЕРІОД, а отже ЧАСТОТУ", 10, INK, "start", "bold")
    s += text(82, 200, "більший ВЕРХ → довший період", 9.5, GREY, "start")
    s += text(82, 220, "→ нижча частота", 9.5, GREY, "start")
    s += pwm(82, 250, 290, 110, 0.5, 3, BLUE)
    s += text(260, 308, "частота = такт / (передільник × (ВЕРХ+1))", 8.7, INK, "middle")
    s += rect(500, 90, 400, 230, "none", GOLD, 1.8, 12)
    s += text(700, 116, "Регістр порога (compare)", 12, "#8a6a14", "middle", "bold")
    s += text(522, 146, "до якого числа ніжка увімк.", 10, INK, "start")
    s += text(522, 168, "→ задає ШПАРУВАТІСТЬ", 10, INK, "start", "bold")
    s += text(522, 200, "вищий поріг → ширший імпульс", 9.5, GREY, "start")
    s += text(522, 220, "→ більше середнє", 9.5, GREY, "start")
    s += pwm(522, 250, 290, 110, 0.75, 3, GOLD)
    s += text(700, 308, "шпаруватість = поріг / (ВЕРХ+1)", 8.7, INK, "middle")
    s += text(W / 2, 360, "Частота й шпаруватість керуються НЕЗАЛЕЖНО — у цьому вся зручність апаратної ШІМ.", 10.3, INK, "middle", "bold")
    save("fig-25-2-2-two-knobs.svg", s)


# ── Рис. 25.2.3 — зміна шпаруватості на льоту ────────────────────────────────
def fig23_change_duty():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Зміна шпаруватості: просто рухаємо поріг", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "період незмінний; піднімаєш поріг — ширший імпульс, опускаєш — вужчий", 11, GREY, "middle", style="italic")
    rows = [("низький поріг", 0.2, GREEN), ("середній", 0.5, GOLD), ("високий поріг", 0.8, RED)]
    for i, (lab, d, col) in enumerate(rows):
        y0 = 100 + i * 80
        s += text(80, y0 + 22, lab, 10.5, col, "start", "bold")
        s += pwm(230, y0, y0 + 40, 130, d, 4, BLUE)
        s += line(230, y0, 230, y0 + 40, col, 1.4, dash="3,2")
        yavg = (y0 + 40) - 40 * d
        s += line(230, yavg, 770, yavg, col, 1.6, dash="6,3")
        s += text(800, yavg + 4, "%d%% сер." % int(d * 100), 9.5, col, "start", "bold")
    s += rect(150, 330, 660, 42, LAMB, GOLD, 1.4, 8)
    s += text(480, 356, "Один регістр, плавна зміна: так ledcWrite(значення) і керує яскравістю чи швидкістю.", 10.3, INK, "middle", "bold")
    save("fig-25-2-3-change-duty.svg", s)


# ── Рис. 25.2.4 — один лічильник, багато каналів ─────────────────────────────
def fig24_multi_channel():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Один лічильник — багато каналів: спільна частота, свої шпаруватості", 16.5, INK, "middle", "bold")
    s += text(W / 2, 54, "усі канали ділять один період (ВЕРХ), та кожен має власний поріг (свою шпаруватість)", 10.5, GREY, "middle", style="italic")
    s += rect(60, 100, 170, 80, LGRN, GREEN, 1.8, 10)
    s += text(145, 130, "лічильник", 11, GREEN, "middle", "bold")
    s += text(145, 150, "(один період)", 9, INK, "middle")
    s += text(145, 168, "= спільна частота", 8.5, GREY, "middle")
    chans = [("канал R", 0.8, RED), ("канал G", 0.4, GREEN), ("канал B", 0.15, BLUE)]
    for i, (lab, d, col) in enumerate(chans):
        y = 110 + i * 90
        s += arrow(230, 140, 290, y + 20, INK, 1.6)
        s += text(310, y, lab, 10.5, col, "start", "bold")
        s += text(310, y + 16, "поріг %d%%" % int(d * 100), 8.7, GREY, "start")
        s += pwm(430, y - 6, y + 30, 100, d, 4, col)
    s += text(W / 2, 360, "Так одним блоком ШІМ керують RGB-світлодіодом (3 канали) чи кількома моторами заразом —", 10.3, INK, "middle", "bold")
    s += text(W / 2, 380, "усі з однаковою частотою, але кожен зі своєю яскравістю/швидкістю.", 9.7, GREY, "middle")
    save("fig-25-2-4-multi-channel.svg", s)


# ── Рис. 25.2.5 — крайове проти центрованого ─────────────────────────────────
def fig25_edge_vs_center():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Два різновиди: крайове й центроване вирівнювання", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "крайове — лічба лише вгору; центроване — вгору-вниз, імпульс посередині періоду", 10.5, GREY, "middle", style="italic")
    # edge
    s += rect(50, 80, 410, 250, "none", FAINT, 1.6, 12)
    s += text(255, 106, "Крайове (edge-aligned)", 12, INK, "middle", "bold")
    ox, oy = 80, 200
    s += poly([(ox, oy), (200, 130), (200, oy), (320, 130), (320, oy), (440, 130)], GREEN, 1.8)
    s += pwm(80, 240, 270, 120, 0.4, 3, BLUE)
    s += text(255, 300, "лічить угору й скидається; імпульс на початку", 9, INK, "middle")
    s += text(255, 318, "проста, найпоширеніша", 9, GREEN, "middle", "bold")
    # center
    s += rect(500, 80, 410, 250, "none", FAINT, 1.6, 12)
    s += text(705, 106, "Центроване (center-aligned)", 11.5, INK, "middle", "bold")
    bx, by = 530, 200
    s += poly([(bx, by), (590, 130), (650, by), (710, 130), (770, by), (830, 130), (890, by)], GREEN, 1.8)
    # symmetric pulses centered
    cpulse = [(530, 240), (560, 240), (560, 270), (620, 270), (620, 240), (650, 240),
              (650, 270), (710, 270), (710, 240), (740, 240), (740, 270), (800, 270), (800, 240), (890, 240)]
    s += poly([(530, 270), (560, 270), (560, 240), (620, 240), (620, 270), (650, 270), (650, 240),
               (710, 240), (710, 270), (740, 270), (740, 240), (800, 240), (800, 270), (890, 270)], BLUE, 2.2)
    s += text(705, 300, "лічить угору-вниз; імпульс по центру", 9, INK, "middle")
    s += text(705, 318, "рівніша для моторів (менше гармонік)", 9, GREEN, "middle", "bold")
    s += text(W / 2, 360, "Для світлодіодів байдуже; центроване беруть у точному керуванні моторами.", 10.3, INK, "middle", "bold")
    save("fig-25-2-5-edge-vs-center.svg", s)


# ── Рис. 25.2.6 — LEDC в ESP32 ───────────────────────────────────────────────
def fig26_esp32_ledc():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "ШІМ в ESP32: блок LEDC (таймер + канали)", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "задаєш частоту й роздільність (біти) — це ВЕРХ; ledcWrite задає поріг (шпаруватість)", 10.5, GREY, "middle", style="italic")
    s += rect(70, 100, 250, 120, LGRN, GREEN, 1.8, 12)
    s += text(195, 128, "таймер LEDC", 12, GREEN, "middle", "bold")
    s += text(90, 154, "частота (Гц)  +", 10.5, INK, "start")
    s += text(90, 176, "роздільність (біт)", 10.5, INK, "start")
    s += text(195, 200, "→ задають ВЕРХ = 2^біт − 1", 9, GREY, "middle")
    for i, (lab, d, col) in enumerate([("канал 0", 0.6, BLUE), ("канал 1", 0.3, GOLD)]):
        y = 120 + i * 90
        s += arrow(320, 150, 400, y + 18, INK, 1.6)
        s += rect(400, y, 200, 56, "#fbfcff", col, 1.6, 10)
        s += text(500, y + 24, lab + " → ніжка", 10.5, col, "middle", "bold")
        s += text(500, y + 44, "ledcWrite(%d, поріг)" % i, 9.5, INK, "middle")
    s += rect(660, 110, 250, 130, "#0f1115", INK, 1.4, 8)
    s += '<text x="678" y="140" font-family="Consolas, monospace" font-size="11.5" fill="#7ee0a0">// налаштувати:</text>\n'
    s += '<text x="678" y="162" font-family="Consolas, monospace" font-size="11.5" fill="#e8e8e8">ledcAttach(pin,</text>\n'
    s += '<text x="678" y="182" font-family="Consolas, monospace" font-size="11.5" fill="#e8e8e8">  5000, 8); // 5кГц, 8біт</text>\n'
    s += '<text x="678" y="208" font-family="Consolas, monospace" font-size="11.5" fill="#7ee0a0">// яскравість:</text>\n'
    s += '<text x="678" y="228" font-family="Consolas, monospace" font-size="11.5" fill="#e8e8e8">ledcWrite(pin, 128);</text>\n'
    s += rect(150, 300, 660, 76, LAMB, GOLD, 1.4, 10)
    s += text(480, 326, "8 біт → шкала 0…255; ledcWrite(pin, 128) ≈ 50% шпаруватості.", 10.3, INK, "middle", "bold")
    s += text(480, 348, "Частота й роздільність пов'язані (вища частота — менше доступних біт): про це §25.3.", 9.7, GREY, "middle")
    s += text(480, 368, "Усе інше — апаратно: задав раз, далі таймер формує імпульси сам.", 9.5, GREY, "middle")
    save("fig-25-2-6-esp32-ledc.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §25.3 Шпаруватість, роздільність, частота — fig-25-3-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 25.3.1 — три параметри ШІМ ──────────────────────────────────────────
def fig31_three_params():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Три параметри ШІМ: шпаруватість, роздільність, частота", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "шпаруватість — ЯКИЙ рівень; роздільність — на СКІЛЬКИ кроків; частота — як ШВИДКО повторюється", 9.7, GREY, "middle", style="italic")
    cards = [
        (50, "Шпаруватість", "який середній рівень зараз", "(значення, яке пишемо)", BLUE, "0…макс"),
        (340, "Роздільність", "на скільки кроків ділиться шкала", "(число біт)", GREEN, "8 біт = 256 кроків"),
        (630, "Частота", "скільки періодів за секунду", "(Гц)", GOLD, "напр., 5 кГц"),
    ]
    for ox, t, l1, l2, col, ex in cards:
        s += rect(ox, 90, 280, 200, "#fbfcff", col, 1.8, 12)
        s += text(ox + 140, 120, t, 13.5, col, "middle", "bold")
        s += line(ox + 20, 134, ox + 260, 134, col, 1.2)
        s += text(ox + 140, 168, l1, 10.5, INK, "middle")
        s += text(ox + 140, 192, l2, 9.3, GREY, "middle")
        s += rect(ox + 60, 220, 160, 36, "#f7f7f7", col, 1.2, 6)
        s += text(ox + 140, 243, ex, 10.5, col, "middle", "bold")
    s += text(W / 2, 330, "Шпаруватість крутиш постійно; роздільність і частоту обираєш один раз — і вони ПОВ'ЯЗАНІ.", 10.3, INK, "middle", "bold")
    s += text(W / 2, 352, "Саме цей зв'язок частоти й роздільності — головний компроміс теми.", 9.7, GREY, "middle")
    save("fig-25-3-1-three-params.svg", s)


# ── Рис. 25.3.2 — роздільність = кількість кроків ────────────────────────────
def fig32_resolution_steps():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Роздільність — на скільки кроків ділиться шпаруватість", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "більше біт — дрібніші кроки — плавніше керування; менше біт — грубо, «сходинками»", 10.5, GREY, "middle", style="italic")
    # 2-bit coarse
    s += rect(50, 84, 410, 250, "none", RED, 1.8, 12)
    s += text(255, 110, "2 біти — лише 4 кроки", 12, RED, "middle", "bold")
    ox, oy = 90, 290
    for i in range(5):
        x = ox + i * 80
        s += line(x, oy, x, oy - i * 50, GREY, 1.2, "3,3")
    g = [(90, 290), (170, 290), (170, 240), (250, 240), (250, 190), (330, 190), (330, 140), (410, 140)]
    s += poly(g, RED, 2.6)
    s += text(255, 318, "грубо: «вимк / 33% / 66% / повна»", 9, INK, "middle")
    # 8-bit smooth
    s += rect(500, 84, 410, 250, "none", GREEN, 1.8, 12)
    s += text(705, 110, "8 біт — 256 кроків", 12, GREEN, "middle", "bold")
    bx = 540
    f = [(bx, 290)]
    for i in range(36):
        f.append((bx + i * 9, 290 - i * 4))
    s += poly(f, GREEN, 2.4)
    s += text(705, 318, "плавно: майже неперервна шкала", 9, INK, "middle")
    s += text(W / 2, 360, "Для світлодіода 8 біт зазвичай досить; для звуку чи точності беруть більше (10–12 біт).", 10.3, INK, "middle", "bold")
    save("fig-25-3-2-resolution-steps.svg", s)


# ── Рис. 25.3.3 — компроміс частота↔роздільність ─────────────────────────────
def fig33_freq_res_tradeoff():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Головний компроміс: частота × кроки ≤ такт", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "за один період має вміститися 2^біт тіків; що вища частота, то менше тіків — і менше біт", 10, GREY, "middle", style="italic")
    s += rect(120, 90, 720, 50, "#0f1115", INK, 1.6, 10)
    s += '<text x="480" y="122" font-family="Consolas, monospace" font-size="16" fill="#e8e8e8" text-anchor="middle" font-weight="bold">частота × 2^роздільність ≤ частота_такту</text>\n'
    # see-saw idea: table
    cols = [(150, "частота", 200), (370, "тіків у періоді (80 МГц)", 280), (670, "макс. біт", 160)]
    for x, t, w in cols:
        s += rect(x, 160, w, 32, "#eef1f8", BLUE, 1.4, 6)
        s += text(x + w / 2, 182, t, 10.5, BLUE, "middle", "bold")
    rows = [("1 кГц", "80 000", "16 біт", GREEN), ("5 кГц", "16 000", "13 біт", GREEN),
            ("100 кГц", "800", "9 біт", GOLD), ("1 МГц", "80", "6 біт", RED)]
    y = 196
    for f, ticks, bits, col in rows:
        s += rect(150, y, 200, 38, "#fff", GREY, 1.2, 5)
        s += text(250, y + 24, f, 11, INK, "middle", "bold")
        s += rect(370, y, 280, 38, "#fff", GREY, 1.2, 5)
        s += text(510, y + 24, ticks, 11, INK, "middle")
        s += rect(670, y, 160, 38, ("#eef6ef" if col == GREEN else ("#fff8e8" if col == GOLD else "#fdf2f2")), col, 1.2, 5)
        s += text(750, y + 24, bits, 11, col, "middle", "bold")
        y += 44
    s += text(W / 2, 388, "Вища частота «з'їдає» роздільність. Тому беруть якнайнижчу частоту, що ще годиться навантаженню.", 10, INK, "middle", "bold")
    save("fig-25-3-3-freq-res-tradeoff.svg", s)


# ── Рис. 25.3.4 — формула максимальної роздільності ──────────────────────────
def fig34_max_res_formula():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 32, "Скільки біт можна: max біт = log2(такт / частота)", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "ділимо такт на частоту — це число тіків у періоді; його двійковий логарифм і є межа біт", 9.7, GREY, "middle", style="italic")
    s += rect(120, 86, 700, 50, "#0f1115", INK, 1.6, 10)
    s += '<text x="470" y="118" font-family="Consolas, monospace" font-size="16" fill="#e8e8e8" text-anchor="middle" font-weight="bold">max_біт = log2( такт / частота )</text>\n'
    s += text(470, 172, "Приклади на 80 МГц", 12.5, INK, "middle", "bold")
    s += rect(120, 190, 700, 96, "none", FAINT, 1.6, 10)
    s += text(140, 218, "5 кГц:  80 000 000 / 5 000 = 16 000  →  log2 ≈ 13.9  →  13 біт", 11, GREEN, "start", "bold")
    s += text(140, 244, "100 кГц: 80 000 000 / 100 000 = 800  →  log2 ≈ 9.6  →  9 біт", 11, "#8a6a14", "start", "bold")
    s += text(140, 270, "1 МГц:  80 000 000 / 1 000 000 = 80  →  log2 ≈ 6.3  →  6 біт", 11, RED, "start", "bold")
    s += text(W / 2, 322, "Беремо ціле число біт, що не перевищує цю межу. Хочеш і високу частоту, і багато біт — не вийде.", 10, INK, "middle", "bold")
    save("fig-25-3-4-max-res-formula.svg", s)


# ── Рис. 25.3.5 — як обирати ─────────────────────────────────────────────────
def fig35_choosing():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Як обирати: спершу частота під навантаження, тоді роздільність", 17, INK, "middle", "bold")
    s += text(W / 2, 54, "частоту диктує фізика навантаження; роздільність береш найбільшу, що ще вміщається", 10, GREY, "middle", style="italic")
    steps = [
        ("1. Частоту — від навантаження", ["світлодіод: > 200 Гц (не блимає)", "мотор: часто 1–20 кГц (тихо)", "звук: за межею чутності"], BLUE),
        ("2. Роздільність — що влізе", ["порахуй max біт за формулою", "візьми стільки, скільки треба", "для LED 8 біт майже завжди"], GREEN),
    ]
    for i, (t, lines, col) in enumerate(steps):
        ox = 50 + i * 460
        s += rect(ox, 90, 410, 220, "#fbfcff", col, 1.8, 12)
        s += text(ox + 205, 120, t, 12, col, "middle", "bold")
        s += line(ox + 20, 134, ox + 390, 134, col, 1.2)
        for j, c in enumerate(lines):
            s += text(ox + 30, 166 + j * 32, "• " + c, 10.5, INK, "start")
    s += rect(150, 326, 660, 44, LAMB, GOLD, 1.4, 8)
    s += text(480, 352, "Правило: НАЙНИЖЧА частота, що годиться навантаженню → лишається найбільше біт на плавність.", 9.8, INK, "middle", "bold")
    save("fig-25-3-5-choosing.svg", s)


# ── Рис. 25.3.6 — гамма: око бачить нелінійно ────────────────────────────────
def fig36_gamma():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Підступ сприйняття: око бачить яскравість НЕлінійно", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "рівні кроки шпаруватості не дають рівних кроків яскравості — потрібна гамма-корекція", 10, GREY, "middle", style="italic")
    ox, oy = 110, 300
    s += arrow(ox, oy, 470, oy, INK, 2)
    s += arrow(ox, oy, ox, 90, INK, 2)
    s += text(ox - 8, 86, "яскравість", 9.5, INK, "end", "bold")
    s += text(470, oy + 22, "шпаруватість", 9.5, INK, "middle")
    # linear duty
    s += line(ox, oy, 450, 110, GREY, 1.6, dash="4,3")
    s += text(420, 120, "лінійно (наївно)", 8.7, GREY, "start")
    # perceived curve (log-ish): rises fast then flat
    perc = [(ox, oy), (160, 180), (220, 140), (300, 120), (380, 112), (450, 110)]
    s += poly(perc, RED, 2.6)
    s += text(250, 230, "як БАЧИТЬ око:", 9.5, RED, "middle", "bold")
    s += text(250, 248, "знизу стрибає, згори майже не міняється", 8.5, INK, "middle")
    s += rect(510, 100, 400, 200, "none", FAINT, 1.6, 12)
    s += text(710, 128, "Що з цим робити", 11.5, INK, "middle", "bold")
    s += text(528, 156, "• застосувати гамма-криву:", 10, INK, "start")
    s += text(545, 176, "поріг = (рівень/макс)^гамма", 9.5, GREEN, "start", "bold")
    s += text(528, 202, "• або таблицю перерахунку", 10, INK, "start")
    s += text(528, 226, "• більша роздільність допомагає,", 10, INK, "start")
    s += text(545, 246, "бо дає тонші кроки внизу", 9.3, GREY, "start")
    s += text(710, 280, "тоді дімування виглядає РІВНИМ", 9.5, GREEN, "middle", "bold")
    s += text(W / 2, 376, "Тому «плавне затемнення» — це не лінійні кроки шпаруватості, а гамма-крива під око людини.", 10, INK, "middle", "bold")
    save("fig-25-3-6-gamma.svg", s)


def _capv(x, y0, y1, w, duty, n, col=RED):
    """Напруга на конденсаторі: зростає в HIGH, спадає в LOW, навколо середнього."""
    yavg = y1 - (y1 - y0) * duty
    amp = (y1 - y0) * 0.12
    pts = [(x, yavg + amp)]
    cx = x
    for i in range(n):
        hi = w * duty
        pts += [(cx + hi, yavg - amp), (cx + w, yavg + amp)]
        cx += w
    return poly(pts, col, 2.4)


# ═════════════════════════════════════════════════════════════════════════════
# §25.4 RC-фільтр — fig-25-4-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 25.4.1 — ШІМ → постійна напруга ─────────────────────────────────────
def fig41_pwm_to_dc():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "RC-фільтр перетворює ШІМ на рівну постійну напругу", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "для справжнього аналогу (а не «середнього в навантаженні») імпульси треба ЗГЛАДИТИ", 10, GREY, "middle", style="italic")
    s += text(120, 110, "ШІМ (стрибки)", 10, BLUE, "middle", "bold")
    s += pwm(60, 140, 220, 40, 0.5, 6, BLUE)
    s += arrow(320, 180, 420, 180, INK, 2.4)
    s += rect(420, 150, 130, 60, LAMB, GOLD, 1.8, 10)
    s += text(485, 178, "RC-фільтр", 11, INK, "middle", "bold")
    s += text(485, 196, "(згладжує)", 8.7, GREY, "middle")
    s += arrow(550, 180, 650, 180, INK, 2.4)
    s += text(800, 110, "рівна напруга (= середнє)", 10, GREEN, "middle", "bold")
    s += line(660, 180, 900, 180, GREEN, 2.6)
    s += line(660, 220, 900, 220, FAINT, 1, "3,3")
    s += text(908, 184, "U = шпар.×жив.", 9, GREEN, "start")
    s += rect(150, 300, 660, 56, LAMB, GOLD, 1.4, 10)
    s += text(480, 326, "Око й мотор усереднюють ШІМ самі; а для аналогового входу, ЦАП-подібного виходу чи звуку", 9.8, INK, "middle", "bold")
    s += text(480, 346, "потрібна СПРАВЖНЯ рівна напруга — її й дає RC-фільтр.", 9.5, GREY, "middle")
    save("fig-25-4-1-pwm-to-dc.svg", s)


# ── Рис. 25.4.2 — схема RC-фільтра ───────────────────────────────────────────
def fig42_rc_circuit():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Схема: резистор послідовно, конденсатор на землю", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "це фільтр низьких частот — пропускає повільне (середнє), глушить швидкі стрибки", 10.5, GREY, "middle", style="italic")
    # PWM source
    s += rect(80, 160, 120, 50, LBLUE, BLUE, 1.6, 8)
    s += text(140, 184, "ніжка ШІМ", 10.5, INK, "middle", "bold")
    s += text(140, 202, "(стрибки)", 8.5, GREY, "middle")
    # R in series
    s += line(200, 185, 280, 185, INK, 2)
    s += rect(280, 173, 90, 24, "#ffffff", GOLD, 1.6, 4)
    s += text(325, 165, "R", 12, "#8a6a14", "middle", "bold")
    s += line(370, 185, 470, 185, INK, 2)
    # node = output
    s += circle(470, 185, 4, INK, INK, 0)
    s += line(470, 185, 560, 185, INK, 2.4)
    s += circle(560, 185, 4, "none", GREEN, 2)
    s += text(566, 182, "вихід (рівна U)", 10, GREEN, "start", "bold")
    # C to ground
    s += line(470, 185, 470, 240, INK, 2)
    s += line(450, 240, 490, 240, INK, 2.4)
    s += line(450, 250, 490, 250, INK, 2.4)
    s += text(500, 250, "C", 12, BLUE, "start", "bold")
    s += line(470, 250, 470, 300, INK, 2)
    s += line(120, 300, 560, 300, BLUE, 2.2)
    s += text(120, 320, "GND", 10, BLUE, "start", "bold")
    s += line(140, 210, 140, 300, INK, 2)
    s += rect(640, 150, 260, 100, "none", FAINT, 1.6, 10)
    s += text(770, 176, "стала часу τ = R·C", 11, INK, "middle", "bold")
    s += text(656, 202, "R стримує струм у C,", 9.5, INK, "start")
    s += text(656, 220, "C повільно набирає/віддає —", 9.5, INK, "start")
    s += text(656, 238, "разом вони й усереднюють.", 9.5, INK, "start")
    s += text(W / 2, 356, "Той самий RC, що в §22.4 (підтяжка) і §22.5 (дребезг) — тут він згладжує ШІМ у напругу.", 10, INK, "middle", "bold")
    save("fig-25-4-2-rc-circuit.svg", s)


# ── Рис. 25.4.3 — як конденсатор усереднює ───────────────────────────────────
def fig43_capacitor_averages():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Як це працює: конденсатор не встигає за стрибками", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "у HIGH він повільно набирає заряд, у LOW повільно віддає — і завмирає біля середнього", 10.3, GREY, "middle", style="italic")
    ox = 90
    y0, y1 = 110, 230
    s += line(ox - 6, y0, 900, y0, FAINT, 1.2)
    s += text(64, y0 + 4, "жив.", 9, RED, "end")
    s += line(ox - 6, y1, 900, y1, FAINT, 1.2)
    s += text(64, y1 + 4, "0", 9, BLUE, "end")
    s += pwm(ox, y0, y1, 100, 0.5, 7, "#b9c6ee")
    yavg = (y0 + y1) / 2
    s += line(ox, yavg, 860, yavg, GREEN, 1.6, dash="6,3")
    s += text(866, yavg - 4, "середнє", 9.5, GREEN, "start", "bold")
    s += _capv(ox, y0, y1, 100, 0.5, 7, RED)
    s += text(250, 270, "напруга на C — дрібна «брижа» навколо середнього", 9.5, RED, "middle", "bold")
    s += arrow(420, 290, 420, 250, RED, 1.8)
    s += text(420, 308, "залишкове коливання = ПУЛЬСАЦІЯ (ripple)", 9, INK, "middle")
    s += rect(150, 330, 660, 42, LAMB, GOLD, 1.4, 8)
    s += text(480, 356, "Чим повільніший RC (більший) і вища частота ШІМ — тим дрібніша брижа, тим рівніша напруга.", 9.8, INK, "middle", "bold")
    save("fig-25-4-3-capacitor-averages.svg", s)


# ── Рис. 25.4.4 — компроміс пульсація↔швидкість ──────────────────────────────
def fig44_ripple_tradeoff():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Компроміс: рівність проти швидкості (знову RC)", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "більший RC — рівніше, але повільніше реагує на зміну шпаруватості; менший — навпаки", 10.3, GREY, "middle", style="italic")
    # small RC
    s += rect(50, 84, 410, 250, "none", GOLD, 1.8, 12)
    s += text(255, 110, "Малий RC", 12, "#8a6a14", "middle", "bold")
    s += pwm(80, 140, 200, 40, 0.5, 8, "#cdd8f2")
    s += _capv(80, 140, 200, 40, 0.5, 8, RED)
    s += text(255, 230, "✓ швидко наздоганяє зміни", 10, INK, "middle")
    s += text(255, 254, "✗ помітна пульсація", 10, RED, "middle", "bold")
    s += text(255, 300, "(швидко, але «брудно»)", 9, GREY, "middle")
    # big RC
    s += rect(500, 84, 410, 250, "none", GREEN, 1.8, 12)
    s += text(705, 110, "Великий RC", 12, GREEN, "middle", "bold")
    s += pwm(530, 140, 200, 40, 0.5, 8, "#cdd8f2")
    s += line(530, 170, 880, 170, RED, 2.4)
    s += text(705, 230, "✓ майже без пульсації — рівно", 10, INK, "middle")
    s += text(705, 254, "✗ мляво реагує на зміни", 10, RED, "middle", "bold")
    s += text(705, 300, "(рівно, але повільно)", 9, GREY, "middle")
    s += text(W / 2, 360, "Той самий компроміс «швидко проти чисто», що з підтяжкою (§22.4) — обирай під задачу.", 10, INK, "middle", "bold")
    save("fig-25-4-4-ripple-tradeoff.svg", s)


# ── Рис. 25.4.5 — зріз нижче частоти ШІМ ─────────────────────────────────────
def fig45_cutoff_vs_pwm():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 32, "Правило: зріз фільтра — добряче НИЖЧЕ за частоту ШІМ", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "тоді постійне (середнє) проходить, а швидкі імпульси гасяться — лишається мала брижа", 10, GREY, "middle", style="italic")
    ox, oy = 90, 250
    s += arrow(ox, oy, 880, oy, INK, 2)
    s += text(884, oy + 4, "частота", 9.5, INK, "start")
    # passband
    s += rect(ox, 110, 230, oy - 110, LGRN, GREEN, 1.2, 0)
    s += text(ox + 115, 130, "проходить", 10, GREEN, "middle", "bold")
    s += text(ox + 115, 146, "(середнє, пов.)", 8.3, INK, "middle")
    # cutoff
    s += line(320, 110, 320, oy, GOLD, 1.8, dash="5,3")
    s += text(320, 102, "зріз fc = 1/(2πRC)", 9.5, "#8a6a14", "middle", "bold")
    # rolloff
    s += poly([(320, oy), (560, oy)], RED, 1)
    s += line(320, 130, 620, oy, RED, 2, dash="2,2")
    # pwm freq
    s += line(700, 110, 700, oy, BLUE, 1.8, dash="5,3")
    s += text(700, 102, "частота ШІМ", 9.5, BLUE, "middle", "bold")
    s += text(700, 130, "(тут — глушиться)", 8.3, INK, "middle")
    s += rect(150, 290, 640, 56, LAMB, GOLD, 1.4, 10)
    s += text(470, 314, "Бери зріз разів у 10 нижче за частоту ШІМ — пульсація стане малою.", 10, INK, "middle", "bold")
    s += text(470, 334, "Вища частота ШІМ → можна менший (швидший) фільтр за тієї ж рівності.", 9.5, GREY, "middle")
    save("fig-25-4-5-cutoff-vs-pwm.svg", s)


# ── Рис. 25.4.6 — ШІМ + RC = дешевий ЦАП ─────────────────────────────────────
def fig46_poor_mans_dac():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "ШІМ + RC = «ЦАП для бідних»: дешево, та з межами", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "будь-яка ШІМ-ніжка + два копійчані компоненти дають керовану аналогову напругу", 10.3, GREY, "middle", style="italic")
    s += rect(60, 90, 400, 220, "#f3faf4", GREEN, 1.8, 12)
    s += text(260, 116, "Плюси", 12.5, GREEN, "middle", "bold")
    for i, c in enumerate(["працює на будь-якій ШІМ-ніжці", "лише резистор + конденсатор", "роздільність від ШІМ (багато біт)", "майже безкоштовно"]):
        s += text(82, 148 + i * 32, "✓ " + c, 10.3, INK, "start")
    s += rect(500, 90, 400, 220, "#fdf2f2", RED, 1.8, 12)
    s += text(700, 116, "Межі", 12.5, RED, "middle", "bold")
    for i, c in enumerate(["лишається пульсація (ripple)", "повільний (через фільтр)", "слабкий вихід (опір R) →", "часто треба буфер (ОП)"]):
        s += text(522, 148 + i * 32, "✗ " + c, 10.3, INK, "start")
    s += text(710, 286, "для точного/швидкого — справжній ЦАП (§25.6)", 9, RED, "middle", "bold")
    s += text(W / 2, 348, "Для повільних, невибагливих аналогових рівнів (опорна напруга, зміщення, проста генерація)", 9.8, INK, "middle", "bold")
    s += text(W / 2, 368, "ШІМ+RC — чудовий дешевий вибір; для аудіо чи точності беруть окремий ЦАП.", 9.5, GREY, "middle")
    save("fig-25-4-6-poor-mans-dac.svg", s)


def _ledtri(x, y, col=GOLD):
    """Маленький символ світлодіода (трикутник + риска)."""
    o = f'<polygon points="{x},{y} {x+22},{y} {x+11},{y+18}" fill="{LAMB}" stroke="{INK}" stroke-width="1.6"/>\n'
    o += line(x, y + 18, x + 22, y + 18, INK, 2.2)
    o += arrow(x + 24, y + 4, x + 34, y - 4, col, 1.4)
    return o


def _mosbox(x, y, w=70, h=56, lab="N-MOS"):
    o = rect(x, y, w, h, "#fbfcff", INK, 1.8, 8)
    o += text(x + w / 2, y + h / 2 + 4, lab, 10, INK, "middle", "bold")
    return o


# ═════════════════════════════════════════════════════════════════════════════
# §25.5 Застосування ШІМ — fig-25-5-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 25.5.1 — яскравість світлодіода ─────────────────────────────────────
def fig51_led_brightness():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Яскравість світлодіода: шпаруватість = яскравість", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "малий LED — прямо з ніжки (через резистор); потужний LED чи стрічку — через транзистор", 10, GREY, "middle", style="italic")
    # small led direct
    s += rect(50, 84, 410, 250, "none", FAINT, 1.6, 12)
    s += text(255, 110, "Малий світлодіод — прямо", 12, GREEN, "middle", "bold")
    s += rect(80, 150, 110, 44, LBLUE, BLUE, 1.6, 8)
    s += text(135, 177, "ніжка ШІМ", 10, INK, "middle", "bold")
    s += line(190, 172, 250, 172, INK, 2)
    s += rect(250, 162, 50, 20, "#fff", GOLD, 1.4, 3)
    s += text(275, 156, "R", 9, "#8a6a14", "middle", "bold")
    s += line(300, 172, 330, 172, INK, 2)
    s += _ledtri(330, 163)
    s += line(352, 181, 352, 220, INK, 2)
    s += line(120, 220, 352, 220, BLUE, 2)
    s += text(255, 250, "шпаруватість 20% → ~п'ята яскравості", 9.5, INK, "middle")
    s += text(255, 274, "(не забудь гамму, §25.3)", 9, GREY, "middle")
    # power led via transistor
    s += rect(500, 84, 410, 250, "none", FAINT, 1.6, 12)
    s += text(705, 110, "Потужний LED / стрічка — через ключ", 11, BLUE, "middle", "bold")
    s += rect(520, 150, 90, 40, LBLUE, BLUE, 1.6, 8)
    s += text(565, 175, "ніжка ШІМ", 9, INK, "middle", "bold")
    s += line(610, 170, 650, 170, INK, 2)
    s += _mosbox(650, 150, 70, 50, "ключ")
    s += line(685, 150, 685, 120, INK, 2)
    s += _ledtri(674, 95, RED)
    s += line(685, 95, 685, 80, INK, 2)
    s += line(620, 80, 760, 80, RED, 2)
    s += text(620, 72, "+V (потужне)", 9, RED, "start", "bold")
    s += line(685, 200, 685, 230, INK, 2)
    s += line(560, 230, 760, 230, BLUE, 2)
    s += text(705, 260, "ніжка керує затвором, струм тягне +V", 9.3, INK, "middle")
    s += text(705, 282, "(той самий ключ, що §22.6)", 9, GREY, "middle")
    save("fig-25-5-1-led-brightness.svg", s)


# ── Рис. 25.5.2 — швидкість мотора ───────────────────────────────────────────
def fig52_motor_speed():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Швидкість мотора: шпаруватість = середня напруга = оберти", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "через транзистор-ключ і ОБОВ'ЯЗКОВО флайбек-діод (мотор індуктивний, §22.6)", 10.3, GREY, "middle", style="italic")
    s += rect(70, 110, 100, 44, LBLUE, BLUE, 1.6, 8)
    s += text(120, 137, "ніжка ШІМ", 9.5, INK, "middle", "bold")
    s += line(170, 132, 230, 132, INK, 2)
    s += rect(230, 110, 20, 20, "#fff", GOLD, 1.4, 3)
    s += text(240, 104, "Rg", 8, "#8a6a14", "middle")
    s += line(250, 132, 300, 132, INK, 2)
    s += _mosbox(300, 110, 80, 60, "N-MOS")
    s += line(340, 110, 340, 80, INK, 2)
    s += circle(340, 55, 24, "none", INK, 2)
    s += text(340, 61, "M", 14, INK, "middle", "bold")
    s += line(340, 31, 340, 20, INK, 2)
    s += line(250, 20, 450, 20, RED, 2.2)
    s += text(250, 12, "+V", 9, RED, "start", "bold")
    # flyback diode across motor
    s += line(410, 55, 410, 20, INK, 2)
    s += f'<polygon points="{400},{50} {420},{50} {410},{34}" fill="{LBLUE}" stroke="{INK}" stroke-width="1.8"/>\n'
    s += line(400, 34, 420, 34, INK, 2.2)
    s += line(340, 55, 410, 55, INK, 2)
    s += text(430, 44, "флайбек-діод", 8.5, BLUE, "start", "bold")
    s += line(340, 170, 340, 200, INK, 2)
    s += line(120, 200, 450, 200, BLUE, 2.2)
    s += text(120, 220, "GND", 9, BLUE, "start", "bold")
    s += line(120, 154, 120, 200, INK, 2)
    s += rect(560, 110, 340, 150, "none", FAINT, 1.6, 12)
    s += text(730, 138, "Правила", 11.5, INK, "middle", "bold")
    s += text(578, 164, "• шпаруватість ↑ → швидше", 10, INK, "start")
    s += text(578, 186, "• ключ + флайбек-діод (§22.6)", 10, INK, "start")
    s += text(578, 208, "• частота > 20 кГц — щоб не пищав", 10, INK, "start")
    s += text(578, 230, "• спільна земля з силовим +V", 10, INK, "start")
    s += text(W / 2, 350, "Те саме — для вентилятора (а 4-пінові вентилятори мають окремий ШІМ-вхід на 25 кГц).", 9.8, INK, "middle", "bold")
    save("fig-25-5-2-motor-speed.svg", s)


# ── Рис. 25.5.3 — сервопривід ────────────────────────────────────────────────
def fig53_servo():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Сервопривід: особлива ШІМ — ширина імпульсу = кут", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "тут важить не «середнє», а ШИРИНА: 1 мс → 0°, 1.5 мс → 90°, 2 мс → 180°, період 20 мс", 9.7, GREY, "middle", style="italic")
    rows = [("1.0 мс", "0°", 0.05, GREEN), ("1.5 мс", "90° (центр)", 0.075, GOLD), ("2.0 мс", "180°", 0.10, RED)]
    for i, (w, ang, frac, col) in enumerate(rows):
        y0 = 100 + i * 80
        s += text(80, y0 + 22, w + " →", 11, col, "start", "bold")
        s += text(170, y0 + 22, ang, 10.5, INK, "start", "bold")
        # one period 20ms scaled, pulse small
        bx = 300
        per = 560
        hi = per * frac
        s += poly([(bx, y0 + 36), (bx, y0), (bx + hi, y0), (bx + hi, y0 + 36), (bx + per, y0 + 36)], BLUE, 2.4)
        s += text(bx + hi + 10, y0 + 14, "імпульс", 8, BLUE, "start")
        s += text(bx + per - 100, y0 + 30, "пауза до 20 мс", 8, GREY, "start")
    s += rect(150, 330, 660, 56, LAMB, GOLD, 1.4, 10)
    s += text(480, 356, "Серво саме декодує ширину імпульсу в кут — це НЕ усереднення, а кодування значення шириною.", 9.8, INK, "middle", "bold")
    s += text(480, 376, "Період 50 Гц (20 мс) фіксований; міняється лише ширина 1…2 мс.", 9.3, GREY, "middle")
    save("fig-25-5-3-servo.svg", s)


# ── Рис. 25.5.4 — керування потужністю нагрівача ─────────────────────────────
def fig54_heater_power():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Керування потужністю: шпаруватість = середня потужність", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "повна потужність частку часу → середня потужність = шпаруватість × повна (ЛІНІЙНО)", 10, GREY, "middle", style="italic")
    # bar: power vs duty linear
    ox, oy = 110, 260
    s += arrow(ox, oy, 470, oy, INK, 2)
    s += arrow(ox, oy, ox, 100, INK, 2)
    s += text(ox - 8, 96, "сер. потужн.", 9, INK, "end", "bold")
    s += text(470, oy + 22, "шпаруватість", 9.5, INK, "middle")
    s += line(ox, oy, 450, 110, GREEN, 2.6)
    s += text(360, 150, "лінійно!", 10, GREEN, "middle", "bold")
    s += text(250, 300, "0% → 0 потужн.;  50% → половина;  100% → повна", 9.3, INK, "middle")
    s += rect(520, 100, 390, 160, "none", FAINT, 1.6, 12)
    s += text(715, 128, "Чому це добре", 11.5, INK, "middle", "bold")
    s += text(538, 154, "• потужність лінійна зі шпаруватістю", 9.7, INK, "start")
    s += text(538, 176, "• майже без втрат (ключ, не резистор)", 9.7, INK, "start")
    s += text(538, 202, "• для НИЗЬКОВОЛЬТНОГО: транзистор + ШІМ", 9.7, INK, "start")
    s += text(538, 228, "• для МЕРЕЖІ ~220 В: твердотільне реле", 9.7, RED, "start", "bold")
    s += text(538, 248, "(повільна ШІМ цілими півперіодами)", 8.7, GREY, "start")
    s += text(W / 2, 350, "Нагрівач, лампа, ТЕН — усе плавно й ощадно, бо транзистор повністю відкритий чи закритий.", 9.8, INK, "middle", "bold")
    save("fig-25-5-4-heater-power.svg", s)


# ── Рис. 25.5.5 — універсальний патерн через транзистор ──────────────────────
def fig55_through_transistor():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Універсальний патерн: усе сильніше за LED — через ключ", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "ніжка ШІМ керує затвором, транзистор комутує великий струм навантаження (§22.6)", 10, GREY, "middle", style="italic")
    s += rect(70, 150, 120, 50, LBLUE, BLUE, 1.6, 8)
    s += text(130, 174, "ніжка ШІМ", 10, INK, "middle", "bold")
    s += text(130, 192, "(мА — крихта)", 8, GREY, "middle")
    s += arrow(190, 175, 270, 175, GOLD, 2.4)
    s += text(230, 165, "затвор", 8.5, "#8a6a14", "middle")
    s += _mosbox(270, 145, 110, 70, "транзистор-ключ")
    s += line(325, 145, 325, 110, INK, 2)
    s += rect(280, 70, 90, 40, "#fbfcff", INK, 1.6, 8)
    s += text(325, 95, "навантаження", 9, INK, "middle", "bold")
    s += line(325, 70, 325, 50, INK, 2)
    s += line(240, 50, 420, 50, RED, 2.2)
    s += text(240, 42, "+V (окреме, потужне)", 9, RED, "start", "bold")
    # flyback for inductive
    s += line(400, 90, 400, 50, INK, 1.8)
    s += f'<polygon points="{390},{86} {410},{86} {400},{70}" fill="{LBLUE}" stroke="{INK}" stroke-width="1.6"/>\n'
    s += line(390, 70, 410, 70, INK, 2)
    s += line(325, 90, 400, 90, INK, 1.8)
    s += text(420, 82, "флайбек (для індуктивних)", 8.3, BLUE, "start")
    s += line(325, 215, 325, 245, INK, 2)
    s += line(130, 245, 420, 245, BLUE, 2.2)
    s += text(130, 265, "GND (спільна!)", 9.5, BLUE, "start", "bold")
    s += line(130, 200, 130, 245, INK, 2)
    s += rect(560, 150, 350, 130, "none", FAINT, 1.6, 12)
    s += text(735, 176, "Один патерн на все:", 11, INK, "middle", "bold")
    s += text(578, 202, "• світлодіодна стрічка, мотор,", 10, INK, "start")
    s += text(590, 220, "нагрівач, помпа, соленоїд…", 10, INK, "start")
    s += text(578, 244, "• індуктивне → флайбек-діод", 10, RED, "start", "bold")
    s += text(578, 266, "• спільна земля обов'язкова", 10, INK, "start")
    s += text(W / 2, 360, "ШІМ лише «натискає кнопку» на затворі — усю силу тягне транзистор. Це й уся схема.", 9.8, INK, "middle", "bold")
    save("fig-25-5-5-through-transistor.svg", s)


# ── Рис. 25.5.6 — карта застосувань ──────────────────────────────────────────
def fig56_applications_map():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Карта застосувань ШІМ: що, як і з якою частотою", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "одна ідея — керувати часткою часу — і десятки застосувань", 11, GREY, "middle", style="italic")
    apps = [
        ("Яскравість LED", "шпаруватість = яскравість", "1–5 кГц, +гамма", GREEN),
        ("Швидкість мотора/вентилятора", "шпаруватість = оберти", "> 20 кГц (тихо), ключ+діод", BLUE),
        ("Сервопривід", "ширина імпульсу = кут", "50 Гц, 1–2 мс", GOLD),
        ("Потужність нагрівача/лампи", "шпаруватість = потужність", "низьк.: ключ; ~220 В: реле", RED),
        ("Аналоговий рівень / звук", "шпаруватість → напруга", "ШІМ + RC-фільтр (§25.4)", "#7a4fb0"),
    ]
    y = 96
    for t, how, freq, col in apps:
        s += rect(60, y, 840, 52, "#fbfcff", col, 1.6, 10)
        s += text(80, y + 31, t, 12, col, "start", "bold")
        s += text(420, y + 31, how, 10.5, INK, "start")
        s += text(700, y + 31, freq, 9.7, GREY, "start")
        y += 60
    save("fig-25-5-6-applications-map.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §25.6 Справжній ЦАП (DAC) — fig-25-6-k
# ═════════════════════════════════════════════════════════════════════════════

def _rbox(x, y, w, h, lab, col=INK):
    """Резистор IEC-стилю (прямокутник) із підписом по центру."""
    s = rect(x, y, w, h, "#ffffff", col, 2, 2)
    s += text(x + w / 2, y + h / 2 + 4, lab, 10.5, col, "middle", "bold")
    return s


def _gnd(x, y, col=INK):
    """Символ землі (три риски)."""
    s = line(x - 13, y, x + 13, y, col, 2)
    s += line(x - 8, y + 5, x + 8, y + 5, col, 2)
    s += line(x - 4, y + 10, x + 4, y + 10, col, 2)
    return s


# ── Рис. 25.6.1 — ЦАП проти ШІМ: пряма напруга vs усереднене миготіння ────────
def fig61_dac_vs_pwm():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 30, "Дві дороги до аналогу: ШІМ імітує, ЦАП видає напряму", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "ціль одна — напруга 2.0 В: ШІМ миготить і усереднює, ЦАП ставить рівно стільки одразу", 10.5, GREY, "middle", style="italic")
    y0, y1 = 120, 210
    yv = y1 - (y1 - y0) * 0.6
    # --- ліворуч: ШІМ ---
    s += text(255, 88, "ШІМ (PWM) + RC-фільтр", 13, BLUE, "middle", "bold")
    ox = 80
    s += line(ox - 6, y0, 445, y0, FAINT, 1.3)
    s += line(ox - 6, y1, 445, y1, FAINT, 1.3)
    s += text(ox - 12, y0 + 4, "макс", 8.5, RED, "end")
    s += text(ox - 12, y1 + 4, "0", 8.5, BLUE, "end")
    s += pwm(ox, y0, y1, 62, 0.6, 6, BLUE)
    rip = []
    xx = ox
    i = 0
    while xx <= 445:
        rip.append((xx, yv - 6 if i % 2 == 0 else yv + 6))
        xx += 28
        i += 1
    s += poly(rip, GREEN, 2.2)
    s += text(255, 250, "середнє ≈ 2.0 В, але з ПУЛЬСАЦІЄЮ", 10, GREEN, "middle", "bold")
    s += text(255, 268, "потрібен фільтр; швидко змінити заважає інерція RC", 9, GREY, "middle")
    # --- праворуч: ЦАП ---
    s += text(715, 88, "ЦАП (DAC)", 13, GREEN, "middle", "bold")
    ox2 = 545
    s += line(ox2 - 6, y0, 905, y0, FAINT, 1.3)
    s += line(ox2 - 6, y1, 905, y1, FAINT, 1.3)
    s += text(ox2 - 12, y0 + 4, "макс", 8.5, RED, "end")
    s += text(ox2 - 12, y1 + 4, "0", 8.5, BLUE, "end")
    s += line(ox2, yv, 900, yv, GREEN, 3)
    s += text(830, yv - 9, "рівно 2.0 В", 10, GREEN, "middle", "bold")
    s += text(715, 250, "рівна напруга ОДРАЗУ — без фільтра,", 10, GREEN, "middle", "bold")
    s += text(715, 268, "без пульсації, зміна миттєва", 9, GREY, "middle")
    s += rect(150, 300, 660, 56, LAMB, GOLD, 1.4, 10)
    s += text(480, 324, "ШІМ дає аналог СЕРЕДНІМ (миготіння + фільтр + пульсація).", 10.3, INK, "middle", "bold")
    s += text(480, 343, "ЦАП дає аналог НАПРЯМУ — справжню напругу просто на ніжці.", 10.3, INK, "middle", "bold")
    save("fig-25-6-1-dac-vs-pwm.svg", s)


# ── Рис. 25.6.2 — передавальна характеристика: код → напруга ──────────────────
def fig62_dac_transfer():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 30, "ЦАП: число перетворюється на напругу (8 біт → 256 рівнів)", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "кожному коду 0..255 відповідає своя напруга 0..Vref; разом виходять сходинки", 10.5, GREY, "middle", style="italic")
    ox, oy = 130, 360
    topx, topy = 810, 95
    s += arrow(ox, oy, ox, topy - 12, INK, 2)
    s += arrow(ox, oy, topx + 14, oy, INK, 2)
    s += text(ox - 12, topy - 2, "напруга", 11, INK, "end", "bold")
    s += text(ox - 12, topy + 14, "Vref ≈ 3.3 В", 9.5, GREEN, "end")
    s += text(topx + 6, oy + 26, "код (0 … 255)", 11, INK, "middle", "bold")
    steps = 16
    x_lo, x_hi = ox, topx
    y_lo, y_hi = oy, topy + 18
    pts = []
    for k in range(steps):
        xa = x_lo + (x_hi - x_lo) * k / steps
        xb = x_lo + (x_hi - x_lo) * (k + 1) / steps
        yk = y_lo + (y_hi - y_lo) * k / steps
        pts.append((xa, yk))
        pts.append((xb, yk))
    pts.append((x_hi, y_hi))
    s += poly(pts, BLUE, 2.6)
    # опорні точки
    xmid = (x_lo + x_hi) / 2
    ymid = (y_lo + y_hi) / 2
    s += line(ox, ymid, xmid, ymid, GREEN, 1.3, dash="5,4")
    s += line(xmid, oy, xmid, ymid, GREEN, 1.3, dash="5,4")
    s += circle(xmid, ymid, 4, GREEN, GREEN, 0)
    s += text(xmid + 8, ymid - 8, "код 128 → ≈ 1.65 В", 9.5, GREEN, "start", "bold")
    s += text(ox + 6, oy - 6, "код 0 → 0 В", 9.5, BLUE, "start", "bold")
    s += text(x_hi - 4, y_hi - 8, "код 255 → ≈ 3.3 В", 9.5, RED, "end", "bold")
    s += circle(x_hi, y_hi, 4, RED, RED, 0)
    s += rect(150, 372, 640, 44, LAMB, GOLD, 1.4, 8)
    s += text(470, 390, "Один крок (LSB) = Vref / 255 ≈ 3.3 / 255 ≈ 0.0129 В ≈ 12.9 мВ.", 10.3, INK, "middle", "bold")
    s += text(470, 408, "Більше біт — дрібніші сходинки; 8 біт дають 256 рівнів напруги.", 9.3, GREY, "middle")
    save("fig-25-6-2-dac-transfer.svg", s)


# ── Рис. 25.6.3 — будова ЦАП: резисторна драбина R-2R ─────────────────────────
def fig63_r2r_ladder():
    W, H = 960, 430
    s = header(W, H)
    s += text(W / 2, 30, "Як ЦАП робить напругу: резисторна драбина R-2R", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "кожен біт через ключ під'єднує свою «вагу» до Vref або до землі; драбина їх підсумовує", 10.5, GREY, "middle", style="italic")
    rail_y = 175
    nx = [240, 400, 560, 720]          # b3 (MSB) … b0 (LSB)
    bits = [1, 0, 1, 1]                # приклад: код 1011₂ = 11
    labs = ["b3 (×8)", "b2 (×4)", "b1 (×2)", "b0 (×1)"]
    red_bus, blue_bus = 296, 322
    # лівий термінатор 2R до землі
    s += line(150, rail_y, nx[0], rail_y, INK, 2)
    s += line(150, rail_y, 150, rail_y + 26, INK, 2)
    s += _rbox(135, rail_y + 26, 30, 44, "2R")
    s += line(150, rail_y + 70, 150, rail_y + 96, INK, 2)
    s += _gnd(150, rail_y + 96)
    # вузли + горизонтальні R + вертикальні 2R + ключі
    for i, x in enumerate(nx):
        if i > 0:
            mid = (nx[i - 1] + x) / 2
            s += line(nx[i - 1], rail_y, mid - 22, rail_y, INK, 2)
            s += _rbox(mid - 22, rail_y - 15, 44, 30, "R")
            s += line(mid + 22, rail_y, x, rail_y, INK, 2)
        s += circle(x, rail_y, 3.2, INK, INK, 0)
        s += line(x, rail_y, x, rail_y + 26, INK, 2)
        s += _rbox(x - 15, rail_y + 26, 30, 44, "2R")
        cy = rail_y + 96
        s += line(x, rail_y + 70, x, cy, INK, 2)
        s += circle(x, cy, 3, INK, INK, 0)
        if bits[i]:
            s += line(x, cy, x, red_bus, RED, 2.6)
        else:
            s += line(x, cy, x, blue_bus, BLUE, 2.6)
        s += text(x, 392, labs[i], 9.5, INK, "middle", "bold")
        s += text(x, 408, ("1 → Vref" if bits[i] else "0 → земля"), 8.7, (RED if bits[i] else BLUE), "middle")
    # шини
    s += line(150, red_bus, 760, red_bus, RED, 2)
    s += text(140, red_bus + 4, "Vref", 10, RED, "end", "bold")
    s += line(150, blue_bus, 760, blue_bus, BLUE, 2)
    s += text(140, blue_bus + 4, "0 В", 10, BLUE, "end", "bold")
    # вихід → буфер
    s += line(nx[-1], rail_y, 800, rail_y, GREEN, 2.6)
    s += poly([(805, rail_y - 22), (805, rail_y + 22), (852, rail_y), (805, rail_y - 22)], INK, 2, fill=LGRN)
    s += text(820, rail_y + 4, "буфер", 8.5, INK, "middle")
    s += line(852, rail_y, 905, rail_y, GREEN, 2.6)
    s += text(905, rail_y - 8, "Vout", 11, GREEN, "start", "bold")
    s += text(905, rail_y + 10, "= Vref·код/2ᴺ", 8.6, GREY, "start")
    s += text(W / 2, 366, "приклад коду b3b2b1b0 = 1011₂ = 11  →  Vout = Vref · 11/16 ≈ 0.69·Vref", 10, INK, "middle", "bold")
    save("fig-25-6-3-r2r-ladder.svg", s)


# ── Рис. 25.6.4 — ЦАП в ESP32: два канали, GPIO25/26 ──────────────────────────
def fig64_esp32_dac():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 30, "ЦАП в ESP32: два 8-бітні канали на GPIO25 і GPIO26", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "пишеш число 0..255 — на ніжці з'являється напруга 0..~3.3 В (без жодного фільтра)", 10.5, GREY, "middle", style="italic")
    # чіп
    s += rect(70, 110, 250, 180, LBLUE, BLUE, 2, 12)
    s += text(195, 138, "ESP32", 15, BLUE, "middle", "bold")
    s += rect(100, 158, 190, 56, "#ffffff", INK, 1.6, 8)
    s += text(195, 182, "8-біт ЦАП × 2", 12, INK, "middle", "bold")
    s += text(195, 200, "(вбудований, апаратний)", 8.7, GREY, "middle")
    # дві ніжки
    s += arrow(320, 168, 470, 168, GREEN, 2.4)
    s += text(395, 160, "GPIO25 (DAC1)", 10, INK, "middle", "bold")
    s += arrow(320, 232, 470, 232, GREEN, 2.4)
    s += text(395, 252, "GPIO26 (DAC2)", 10, INK, "middle", "bold")
    s += text(486, 172, "0 .. ~3.3 В", 11, GREEN, "start", "bold")
    s += text(486, 236, "0 .. ~3.3 В", 11, GREEN, "start", "bold")
    # код
    s += rect(620, 120, 300, 96, "#fbfcff", GREY, 1.4, 10)
    s += text(640, 146, "dacWrite(25, v);", 12, INK, "start", "bold")
    s += text(640, 168, "v = 0   → 0 В", 10, BLUE, "start")
    s += text(640, 187, "v = 128 → ≈ 1.65 В", 10, INK, "start")
    s += text(640, 206, "v = 255 → ≈ 3.3 В", 10, RED, "start")
    # буфер-застереження
    s += rect(70, 312, 410, 70, LAMB, GOLD, 1.4, 10)
    s += text(275, 334, "Вихід СЛАБКИЙ (високий опір).", 10.3, INK, "middle", "bold")
    s += text(275, 353, "Пряму ніжку — лише на високоомний вхід;", 9.4, GREY, "middle")
    s += text(275, 369, "для реального навантаження — буфер (ОП-підсилювач).", 9.4, GREY, "middle")
    # сімейство
    s += rect(500, 312, 420, 70, LRED, RED, 1.4, 10)
    s += text(710, 334, "Є в ESP32 та ESP32-S2.", 10.3, RED, "middle", "bold")
    s += text(710, 353, "У ESP32-S3 / C3 / C6 ЦАП НЕМА —", 9.4, INK, "middle")
    s += text(710, 369, "там аналог дають лише через ШІМ (пор. §20.7).", 9.4, GREY, "middle")
    save("fig-25-6-4-esp32-dac.svg", s)


# ── Рис. 25.6.5 — ЦАП у часі: потік чисел → аналогова хвиля ───────────────────
def fig65_dac_waveform():
    import math
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 30, "ЦАП у часі: потік чисел стає аналоговою хвилею (звук, сигнал)", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "таймер задає темп, ЦАП видає відлік за відліком — на ніжці виростає форма сигналу", 10.5, GREY, "middle", style="italic")
    ox, mid, A = 80, 190, 92
    s += line(ox, mid, 905, mid, FAINT, 1.4)
    s += text(ox - 10, mid + 4, "0", 9, GREY, "end")
    # ідеальна синусоїда
    sine = []
    N = 240
    for i in range(N + 1):
        x = ox + 820 * i / N
        y = mid - A * math.sin(2 * math.pi * 2 * i / N)
        sine.append((x, y))
    s += poly(sine, GREY, 1.6)
    # 8-бітні відліки (сходинки sample-hold)
    M = 24
    stair = []
    for j in range(M):
        x0 = ox + 820 * j / M
        x1 = ox + 820 * (j + 1) / M
        q = round(math.sin(2 * math.pi * 2 * j / M) * 8) / 8
        y = mid - A * q
        stair.append((x0, y))
        stair.append((x1, y))
        s += circle(x0, y, 2.4, BLUE, BLUE, 0)
    s += poly(stair, BLUE, 2.2)
    s += text(150, 96, "сірим — ідеал;  синім — 8-бітні відліки ЦАП (сходинки)", 10, INK, "start")
    s += rect(120, 312, 720, 50, LGRN, GREEN, 1.4, 10)
    s += text(480, 334, "Послідовність чисел у часі → аналоговий сигнал. Темп відліків задає таймер, потік — DMA.", 9.8, INK, "middle", "bold")
    s += text(480, 352, "ШІМ так теж уміє, але через фільтр; ЦАП малює напряму. (ESP32 має й вбудований генератор косинуса.)", 9.2, GREY, "middle")
    save("fig-25-6-5-dac-waveform.svg", s)


# ── Рис. 25.6.6 — коли ЦАП, а коли ШІМ ───────────────────────────────────────
def fig66_dac_vs_pwm_map():
    W, H = 960, 470
    s = header(W, H)
    s += text(W / 2, 30, "Коли обирати ЦАП, а коли ШІМ", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "обидва дають «аналог», але по-різному — у кожного своя сильна сторона", 10.5, GREY, "middle", style="italic")
    cx_d, cx_p = 510, 760
    s += rect(330, 74, 250, 34, LGRN, GREEN, 1.6, 8)
    s += text(cx_d - 55, 96, "ЦАП (DAC)", 13, GREEN, "middle", "bold")
    s += rect(640, 74, 250, 34, LBLUE, BLUE, 1.6, 8)
    s += text(cx_p + 5, 96, "ШІМ (PWM)", 13, BLUE, "middle", "bold")
    rows = [
        ("Як працює", "справжня напруга одразу", "миготіння + усереднення"),
        ("Фільтр", "не потрібен", "треба RC для чистого аналогу"),
        ("Канали (ESP32)", "лише 2 (GPIO25/26)", "багато (LEDC ~16)"),
        ("Роздільність", "8 біт (256 рівнів)", "до ~20 біт (§25.3)"),
        ("Зміна значення", "миттєва", "сповільнює інерція фільтра"),
        ("Драйв", "слабкий, треба буфер", "повна напруга, тягне силу"),
        ("Наявність", "ESP32/S2 (S3/C3 — нема)", "усі чіпи, будь-яка ніжка"),
        ("Найкраще для", "звук, опорна напруга", "яскравість, мотор, потужність"),
    ]
    y = 120
    for i, (lab, d, p) in enumerate(rows):
        bg = "#ffffff" if i % 2 == 0 else "#f6f8fc"
        s += rect(40, y, 880, 40, bg, FAINT, 1, 4)
        s += text(56, y + 25, lab, 10.5, INK, "start", "bold")
        s += text(cx_d - 55, y + 25, d, 9.8, GREEN, "middle")
        s += text(cx_p + 5, y + 25, p, 9.8, BLUE, "middle")
        y += 42
    save("fig-25-6-6-dac-vs-pwm-map.svg", s)


# ── §4.7.7 Адресні світлодіоди ───────────────────────────────────────────────
def fig71_problem():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 32, "Адресні світлодіоди: кожен піксель — свого кольору", 18, INK, "middle", "bold")
    s += rect(60, 80, 370, 200, LRED, RED, 2, 12)
    s += text(245, 106, "«У лоб»", 12, RED, "middle", "bold")
    s += text(245, 136, "кожному RGB-світлодіоду —", 10, INK, "middle")
    s += text(245, 156, "3 канали ШІМ", 11, INK, "middle", "bold")
    s += text(245, 190, "100 пікселів → 300 каналів", 10.5, RED, "middle", "bold")
    s += text(245, 212, "✗ неможливо", 12, RED, "middle", "bold")
    s += rect(470, 80, 370, 200, LGRN, GREEN, 2, 12)
    s += text(655, 106, "Адресні (WS2812-клас)", 12, GREEN, "middle", "bold")
    s += text(655, 136, "кожен піксель має власний", 10, INK, "middle")
    s += text(655, 156, "контролер і сам ШІМить R/G/B", 10, INK, "middle")
    s += text(655, 190, "усі — на ОДНОМУ дроті даних", 10.5, GREEN, "middle", "bold")
    s += text(655, 212, "✓ хоч тисяча пікселів", 12, GREEN, "middle", "bold")
    s += text(W / 2, 308, "МК більше не ШІМить кожен колір — він лише шле дані, а ШІМ робить сам піксель.",
              10.5, INK, "middle", "bold")
    save("fig-25-7-1-problem.svg", s)


def fig72_pixel_pwm():
    W, H = 900, 320
    s = header(W, H)
    s += text(W / 2, 32, "ШІМ усередині кожного пікселя", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "піксель отримує 24 біти кольору й сам крутить ШІМ на трьох світлодіодах (§4.7.1)",
              9.8, GREY, "middle", style="italic")
    s += rect(60, 84, 220, 70, LBLUE, BLUE, 1.8, 10)
    s += text(170, 114, "24 біти кольору", 12, BLUE, "middle", "bold")
    s += text(170, 136, "R=200  G=50  B=255", 10, INK, "middle")
    s += arrow(280, 119, 330, 119, INK, 2.2)
    s += rect(330, 80, 510, 200, "#fbfbff", INK, 1.8, 12)
    s += text(585, 104, "піксель: контролер + 3 світлодіоди", 11, INK, "middle", "bold")
    chans = [("R", 0.78, RED, 130), ("G", 0.20, GREEN, 180), ("B", 1.0, BLUE, 230)]
    for lab, duty, col, yy in chans:
        s += text(360, yy + 4, lab, 11, col, "middle", "bold")
        s += pwm(385, yy - 12, yy + 8, 60, duty, 6, col)
        s += text(820, yy + 4, f"яскравість {int(duty*255)}", 9, GREY, "end")
    s += text(W / 2, 304, "Контролер пікселя ШІМить кожен субсвітлодіод до заданої яскравості — рівно як у §4.7.1, лише вбудовано.",
              9.8, INK, "middle", "bold")
    save("fig-25-7-2-pixel-pwm.svg", s)


def fig73_daisy_chain():
    W, H = 900, 290
    s = header(W, H)
    s += text(W / 2, 32, "Ланцюжок: дані течуть від пікселя до пікселя", 18, INK, "middle", "bold")
    s += rect(60, 110, 110, 60, LBLUE, BLUE, 1.8, 10)
    s += text(115, 145, "МК", 13, BLUE, "middle", "bold")
    x = 200
    for i in range(3):
        s += rect(x, 110, 150, 60, LGRN, GREEN, 1.8, 10)
        s += text(x + 75, 138, "піксель " + str(i + 1), 10.5, GREEN, "middle", "bold")
        s += text(x + 20, 162, "DIN", 8, GREY, "start")
        s += text(x + 130, 162, "DOUT", 8, GREY, "end")
        s += arrow(x - 30, 140, x, 140, INK, 2)
        x += 180
    s += arrow(x - 30, 140, x, 140, INK, 2)
    s += text(x + 6, 144, "…далі", 10, GREY, "start")
    s += rect(120, 196, 660, 78, "#fbfbfb", GREY, 1.4, 10)
    s += text(450, 220, "Перший піксель забирає СВОЇ перші 24 біти, а решту штовхає сусідові.", 10.3, INK, "middle", "bold")
    s += text(450, 242, "На N пікселів шлемо N×24 біти поспіль; наприкінці довгий LOW — «защіпка» —", 9.8, GREY, "middle")
    s += text(450, 260, "вмикає всі кольори одночасно.", 9.8, GREY, "middle")
    save("fig-25-7-3-daisy-chain.svg", s)


def fig74_bit_encoding():
    W, H = 900, 300
    s = header(W, H)
    s += text(W / 2, 32, "Біти — шириною імпульсу (один дріт, без такту)", 18, INK, "middle", "bold")
    bits = [1, 0, 1, 1, 0]
    x0, w, hi, lo = 120, 130, 110, 150
    pts = [(x0, lo)]
    cx = x0
    for b in bits:
        h = 0.7 if b else 0.32
        pts += [(cx, hi), (cx + w * h, hi), (cx + w * h, lo), (cx + w, lo)]
        s += text(cx + w / 2, hi - 8, str(b), 12, (GREEN if b else RED), "middle", "bold")
        cx += w
    s += poly(pts, BLUE, 2.6)
    s += text(80, (hi + lo) / 2, "DATA", 10, BLUE, "end", "bold")
    s += text(x0 + 65, lo + 22, "довгий HIGH = 1", 8.6, GREEN, "middle")
    s += text(x0 + 1.5 * w + 65, lo + 22, "короткий HIGH = 0", 8.6, RED, "middle")
    s += rect(120, 232, 660, 46, LAMB, GOLD, 1.4, 10)
    s += text(450, 254, "Такту нема — біт розрізняють за шириною імпульсу (сотні нс), тому таймінг критичний.", 9.8, INK, "middle", "bold")
    s += text(450, 272, "Точні часи, скидання й кадр — у ⚙️-вставці про протокол одного дроту.", 9, GREY, "middle")
    save("fig-25-7-4-bit-encoding.svg", s)


def fig75_why_hardware():
    W, H = 900, 290
    s = header(W, H)
    s += text(W / 2, 32, "Чому таймінг роблять залізом, а не «руками»", 18, INK, "middle", "bold")
    s += rect(60, 80, 370, 150, LRED, RED, 2, 12)
    s += text(245, 106, "Біт-бенгінг у коді ✗", 11.5, RED, "middle", "bold")
    s += text(245, 136, "смикаємо ніжку — а переривання", 9.8, INK, "middle")
    s += text(245, 154, "збиває точний таймінг", 9.8, INK, "middle")
    s += text(245, 188, "піксель прочитає не той біт →", 9.8, RED, "middle")
    s += text(245, 206, "глюки кольору", 11, RED, "middle", "bold")
    s += rect(470, 80, 370, 150, LGRN, GREEN, 2, 12)
    s += text(655, 106, "Спеціальний блок ✓", 11.5, GREEN, "middle", "bold")
    s += text(655, 136, "RMT (ESP32) чи DMA жене біти", 9.8, INK, "middle")
    s += text(655, 154, "з точним таймінгом сам,", 9.8, INK, "middle")
    s += text(655, 188, "не залежачи від коду й переривань", 9.8, GREEN, "middle")
    s += text(655, 206, "→ кольори чисті", 11, GREEN, "middle", "bold")
    s += text(W / 2, 262, "Жорсткий таймінг без такту — робота для заліза; біт-бенгінг (§4.4.7) тут хіба з вимкненими перериваннями.",
              9.6, INK, "middle", "bold")
    save("fig-25-7-5-why-hardware.svg", s)


def fig76_power():
    W, H = 900, 300
    s = header(W, H)
    s += text(W / 2, 32, "Живлення: стрічка — це не іграшка", 19, INK, "middle", "bold")
    s += rect(70, 84, 350, 96, LAMB, GOLD, 1.8, 12)
    s += text(245, 112, "Скільки їсть струму", 11.5, "#8a6d1a", "middle", "bold")
    s += text(245, 138, "піксель на повну білизну ≈ 60 мА", 10, INK, "middle")
    s += text(245, 160, "(3 × 20 мА)", 9, GREY, "middle")
    s += rect(470, 84, 370, 96, LRED, RED, 1.8, 12)
    s += text(655, 112, "100 пікселів ≈ 6 А !", 13, RED, "middle", "bold")
    s += text(655, 140, "із ніжки МК такого не взяти", 10, INK, "middle")
    s += text(655, 162, "(§4.4.6) — треба окреме живлення", 9.6, GREY, "middle")
    s += text(W / 2, 214, "Тому: окремий блок 5 В, спільна земля, зсув рівнів даних, конденсатор і резистор на даних.",
              10, INK, "middle", "bold")
    s += text(W / 2, 240, "Усі тонкощі підключення (інжекція живлення по довжині, номінали) — у 🔌-вставці про стрічку.",
              9.4, GREY, "middle")
    s += rect(150, 262, 600, 0, FAINT, FAINT, 0)
    save("fig-25-7-6-power.svg", s)


if __name__ == "__main__":
    # §25.1 ШІМ: «вдавати» аналог
    fig11_only_on_off()
    fig12_pwm_idea()
    fig13_duty_cycle()
    fig14_average_formula()
    fig15_load_averages()
    fig16_pwm_from_timer()
    # §25.2 Як таймер генерує PWM апаратно
    fig21_pwm_mechanism()
    fig22_two_knobs()
    fig23_change_duty()
    fig24_multi_channel()
    fig25_edge_vs_center()
    fig26_esp32_ledc()
    # §25.3 Шпаруватість, роздільність, частота
    fig31_three_params()
    fig32_resolution_steps()
    fig33_freq_res_tradeoff()
    fig34_max_res_formula()
    fig35_choosing()
    fig36_gamma()
    # §25.4 RC-фільтр
    fig41_pwm_to_dc()
    fig42_rc_circuit()
    fig43_capacitor_averages()
    fig44_ripple_tradeoff()
    fig45_cutoff_vs_pwm()
    fig46_poor_mans_dac()
    # §25.5 Застосування ШІМ
    fig51_led_brightness()
    fig52_motor_speed()
    fig53_servo()
    fig54_heater_power()
    fig55_through_transistor()
    fig56_applications_map()
    # §25.6 Справжній ЦАП (DAC)
    fig61_dac_vs_pwm()
    fig62_dac_transfer()
    fig63_r2r_ladder()
    fig64_esp32_dac()
    fig65_dac_waveform()
    fig66_dac_vs_pwm_map()
    # §4.7.7 Адресні світлодіоди
    fig71_problem()
    fig72_pixel_pwm()
    fig73_daisy_chain()
    fig74_bit_encoding()
    fig75_why_hardware()
    fig76_power()
    print("OK - figures for Section 25 (25.1..25.7) generated in", OUT)
