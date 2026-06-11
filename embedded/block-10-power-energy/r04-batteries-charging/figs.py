# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 10.4 — «Батареї і заряд» (Модуль 10).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи: «Рис. 10.4.T.k»;
для історії до розділу — тема 0 (Рис. 10.4.0.k). Хелпери — копія з §10.3.

Скрипт нарощується по ітераціях: кожна тема додає свої функції-фігури.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
COPP  = "#b5763a"
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
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", GREEN: "aGreen"}


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


def poly(points, color=INK, w=2.4, dash=None):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{pts}" fill="none" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round" stroke-linecap="round"/>\n')


def plus(cx, cy, r=12, color=RED, w=2.5):
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w)
            + line(cx, cy - r * 0.55, cx, cy + r * 0.55, color, w))


def _res(x, y, w, h, label, c=INK):
    out = rect(x, y, w, h, "#ffffff", c, 1.8, 4)
    out += text(x + w / 2, y + h / 2 + 4, label, 10.5, c, "middle", "bold")
    return out


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── Рис. 10.4.0.1 — таймлайн доледієвих акумуляторів ─────────────────────────
def fig_timeline():
    W, H = 940, 760
    s = header(W, H)
    s += text(W / 2, 40, "До літію: два століття перезаряджуваних батарей", 20, INK, "middle", "bold")
    s += text(W / 2, 62, "колективна історія — і одна гучна несправедливість з іменами",
              12.5, GREY, "middle", style="italic")
    spine = 250
    top, bot = 96, H - 70
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("1800", "Алессандро Вольта (IT)", "«вольтів стовп» — джерело сталого струму, але ПЕРВИННЕ: розрядилось — викинь", INK, False),
        ("1859", "Гастон Планте (FR)", "свинцево-кислотний елемент — перший, що ОЖИВАВ після розряду (акумулятор)", BLUE, True),
        ("1881", "Каміль Фор (FR)", "намащені пластини — лід-кислота стає практичною й придатною до серії", BLUE, False),
        ("1899", "Вальдемар Юнгнер (SE)", "лужні NiCd і NiFe — міцна альтернатива свинцю; патент від 11.03.1899", GREEN, True),
        ("лют. 1901", "Томас Едісон (US)", "патентує свій NiFe — на ДВА роки пізніше Юнгнера → судова тяганина", RED, True),
        ("1901–10", "суд і гроші", "Едісон виграв позов не пріоритетом, а грошима; у світі осіла «батарея Едісона»", RED, False),
        ("XX ст.", "спадок", "свинець — авто й UPS; NiCd → Saft (фірма Юнгнера); NiFe — нішевий «вічний»", INK, False),
    ]
    n = len(nodes)
    for i, (yr, who, what, c, hot) in enumerate(nodes):
        y = top + 24 + (bot - top - 48) * i / (n - 1)
        if hot:
            s += circle(spine, y, 10, "#fff", c, 3.2)
            s += circle(spine, y, 4.5, c, c, 0)
        else:
            s += circle(spine, y, 7, "#fff", c, 2.4)
        s += text(spine - 22, y + 5, yr, 12.5, GREY, "end", "bold")
        s += text(spine + 24, y - 4, who, 14.5, c, "start", "bold")
        s += text(spine + 24, y + 15, what, 11.5, INK, "start")
    s += text(W / 2, H - 30, "Жодна з цих хімій — не витвір однієї руки: за кожною стоять попередники, суперники й удосконалювачі.",
              12, INK, "middle")
    s += text(W / 2, H - 12, "А «батарея Едісона» — приклад, як гучне ім'я й капітал переписують авторство справжнього винахідника (Юнгнера).",
              12, RED, "middle", style="italic")
    save("fig-10-0-1-timeline.svg", s)


# ── Рис. 10.4.0.2 — патентна боротьба Юнгнер vs Едісон ───────────────────────
def fig_priority():
    W, H = 940, 440
    s = header(W, H)
    s += text(W / 2, 32, "Хто винайшов нікель-залізний акумулятор?", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "пріоритет і авторство — це різні речі, коли в гру входять гроші", 12.5, GREY, "middle", style="italic")
    # Юнгнер
    s += rect(60, 80, 360, 150, "#eef8ef", GREEN, 2, 12)
    s += text(240, 106, "Вальдемар Юнгнер (Швеція)", 13, GREEN, "middle", "bold")
    for i, t in enumerate(["патент від 11 березня 1899 р.", "винайшов NiFe, NiCd і Ag-Cd", "був ПЕРШИМ — за кілька років до Едісона"]):
        s += text(80, 134 + i * 24, "• " + t, 11, INK, "start")
    s += text(240, 214, "малий капітал, мала фірма", 10.5, GREY, "middle", style="italic")
    # Едісон
    s += rect(520, 80, 360, 150, "#fbe9e7", RED, 2, 12)
    s += text(700, 106, "Томас Едісон (США)", 13, RED, "middle", "bold")
    for i, t in enumerate(["патент від 5 лютого 1901 р.", "свій NiFe — на ~2 роки ПІЗНІШЕ", "потужна компанія й великий капітал"]):
        s += text(540, 134 + i * 24, "• " + t, 11, INK, "start")
    s += text(700, 214, "ім'я, що гриміло на весь світ", 10.5, GREY, "middle", style="italic")
    # суд
    s += arrow(420, 155, 470, 155, INK, 2)
    s += arrow(520, 175, 470, 175, INK, 2)
    s += rect(390, 270, 160, 50, "#fff7e6", AMBER, 2, 10)
    s += text(470, 292, "СУДОВА ТЯГАНИНА", 11, AMBER, "middle", "bold")
    s += text(470, 310, "(1901–1910-ті)", 9.5, INK, "middle")
    s += arrow(240, 230, 440, 270, GREEN, 1.8)
    s += arrow(700, 230, 500, 270, RED, 1.8)
    s += arrow(470, 320, 470, 350, INK, 2)
    s += rect(150, 350, 640, 70, "#fbe9e7", RED, 1.8, 12)
    s += text(470, 375, "Едісон виграв — НЕ пріоритетом, а фінансовими ресурсами.", 12.5, RED, "middle", "bold")
    s += text(470, 397, "У світ пішла назва «батарея Едісона»; ім'я справжнього першовинахідника Юнгнера — стерлося.", 11, INK, "middle")
    s += text(470, 413, "Едісон реально вдосконалив і впровадив NiFe — та «винайшов першим» тут міф.", 10, GREY, "middle", style="italic")
    save("fig-10-0-2-priority.svg", s)


# ── Рис. 10.4.0.3 — три доледієві хімії ──────────────────────────────────────
def fig_chemistries():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 32, "Три доледієві хімії та що з них вийшло", 19, INK, "middle", "bold")
    cards = [
        ("Свинцево-кислотний", "Планте, 1859", "~2.0 В/елемент",
         ["важкий, дешевий", "терпить великий струм", "не любить глибокий розряд"],
         "досі: авто, UPS, ДБЖ", BLUE, 50),
        ("Нікель-кадмій (NiCd)", "Юнгнер, 1899", "~1.2 В/елемент",
         ["міцний, морозостійкий", "«ефект пам'яті»", "кадмій — токсичний"],
         "досі: фірма Saft; ховається в NiMH", GREEN, 360),
        ("Нікель-залізо (NiFe)", "Юнгнер; впровадив Едісон", "~1.2 В/елемент",
         ["майже «вічний», грубий", "низький ККД, саморозряд", "терпить знущання"],
         "ніша: резерв, відновлювана енергетика", AMBER, 670),
    ]
    for title, who, volt, props, legacy, c, x in cards:
        s += rect(x, 64, 220, 300, "#ffffff", c, 2, 12)
        s += text(x + 110, 90, title, 12, c, "middle", "bold")
        s += text(x + 110, 108, who, 9.5, GREY, "middle", style="italic")
        s += text(x + 110, 134, volt, 13, INK, "middle", "bold")
        s += line(x + 20, 146, x + 200, 146, FAINT, 1)
        for j, p in enumerate(props):
            s += text(x + 22, 170 + j * 24, "• " + p, 10, INK, "start")
        s += line(x + 20, 250, x + 200, 250, FAINT, 1)
        s += text(x + 110, 272, "спадок:", 9.5, GREY, "middle", "bold")
        # legacy може бути довгим — розіб'ємо на ~22 символи
        words = legacy.split()
        lines, cur = [], ""
        for wd in words:
            if len(cur) + len(wd) + 1 > 24:
                lines.append(cur); cur = wd
            else:
                cur = (cur + " " + wd).strip()
        if cur:
            lines.append(cur)
        for j, ln in enumerate(lines[:3]):
            s += text(x + 110, 292 + j * 16, ln, 9.5, c, "middle", "bold")
    s += rect(60, 378, W - 120, 32, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, 398, "Кожна хімія — компроміс напруги, міцності, ціни й безпеки. Саме ці осі ми порівнюватимемо й для літію в темі 10.4.1.",
              10.5, INK, "middle")
    save("fig-10-0-3-chemistries.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 10.4.1 — Хімії порівняно
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 10.4.1.1 — напруга елемента ─────────────────────────────────────────
def fig_voltage_ladder():
    W, H = 900, 410
    s = header(W, H)
    s += text(W / 2, 32, "Напруга елемента: скільки комірок на потрібні вольти", 18, INK, "middle", "bold")
    x0, y0 = 110, 330
    vmax, ph = 4.5, 250
    s += line(x0, y0, x0, y0 - ph, INK, 1.6)
    s += arrow(x0, y0 - ph, x0, y0 - ph - 10, INK, 1.6)
    for v in [0, 1, 2, 3, 4]:
        yy = y0 - v / vmax * ph
        s += line(x0 - 5, yy, x0, yy, INK, 1.2)
        s += text(x0 - 10, yy + 4, str(v), 9.5, GREY, "end")
    s += text(x0 - 10, y0 - ph - 6, "В", 9.5, INK, "end", "bold")
    chems = [
        ("Свинець", 1.75, 2.0, 2.4, BLUE, 230),
        ("NiMH", 1.0, 1.2, 1.4, GREEN, 400),
        ("Li-ion", 3.0, 3.7, 4.2, RED, 570),
        ("LiFePO4", 2.5, 3.2, 3.65, AMBER, 740),
    ]
    for name, vmin, vnom, vmaxc, c, x in chems:
        ymin = y0 - vmin / vmax * ph
        ymax = y0 - vmaxc / vmax * ph
        ynom = y0 - vnom / vmax * ph
        s += rect(x - 22, ymax, 44, ymin - ymax, "#fff", c, 1.6, 5)
        s += f'<rect x="{x-22:.0f}" y="{ymax:.0f}" width="44" height="{ymin-ymax:.0f}" rx="5" fill="{c}" fill-opacity="0.15"/>\n'
        s += line(x - 22, ynom, x + 22, ynom, c, 2.6)
        s += text(x + 30, ynom + 4, f"{vnom} В", 10, c, "start", "bold")
        s += text(x, y0 + 18, name, 10.5, c, "middle", "bold")
        s += text(x, y0 + 34, f"{vmin}–{vmaxc} В", 8.5, GREY, "middle")
    s += rect(70, H - 34, W - 140, 24, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 18, "Номінал визначає, скільки елементів послідовно треба на цільову напругу: 12 В — це 6 свинцевих, 3–4 літієвих чи 10 NiMH.", 10, INK, "middle")
    save("fig-10-1-1-voltage.svg", s)


# ── Рис. 10.4.1.2 — питома енергія ───────────────────────────────────────────
def fig_specific_energy():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Питома енергія: скільки ват-годин на кілограм", 18, INK, "middle", "bold")
    bars = [("Свинець", 40, BLUE), ("NiMH", 90, GREEN), ("LiFePO4", 120, AMBER), ("Li-ion / LiPo", 200, RED)]
    x0, y0 = 130, 320
    bw, gap, maxv, ph = 120, 70, 220, 230
    s += line(x0, y0, W - 60, y0, INK, 1.6)
    s += line(x0, y0, x0, y0 - ph, INK, 1.6)
    for v in [0, 50, 100, 150, 200]:
        yy = y0 - v / maxv * ph
        s += line(x0 - 5, yy, x0, yy, INK, 1)
        s += text(x0 - 10, yy + 4, str(v), 9, GREY, "end")
    s += text(x0 - 6, y0 - ph - 4, "Вт·год/кг", 9, INK, "end", "bold")
    for i, (name, v, c) in enumerate(bars):
        x = x0 + 50 + i * (bw + gap)
        h = v / maxv * ph
        s += rect(x, y0 - h, bw, h, "#fff", c, 2, 5)
        s += f'<rect x="{x:.0f}" y="{y0-h:.0f}" width="{bw}" height="{h:.0f}" rx="5" fill="{c}" fill-opacity="0.16"/>\n'
        s += text(x + bw / 2, y0 - h - 8, f"~{v}", 12, c, "middle", "bold")
        s += text(x + bw / 2, y0 + 18, name, 10, c, "middle", "bold")
    s += rect(70, H - 34, W - 140, 24, "#fbf7ec", AMBER, 1.4, 8)
    s += text(W / 2, H - 18, "Та сама енергія: на літії — найлегша, на свинці — у ~5 разів важча. Звідси літій у дронах і носимому; свинець — де вага байдужа.", 9.5, INK, "middle")
    save("fig-10-1-2-energy.svg", s)


# ── Рис. 10.4.1.3 — криві розряду ────────────────────────────────────────────
def fig_discharge_curves():
    W, H = 960, 430
    s = header(W, H)
    s += text(W / 2, 32, "Криві розряду: чи видно заряд по напрузі", 18, INK, "middle", "bold")
    x0, y0 = 90, 350
    pw, ph, vmax = 720, 270, 4.5
    s += line(x0, y0, x0 + pw, y0, INK, 1.6)
    s += line(x0, y0, x0, y0 - ph, INK, 1.6)
    for v in [0, 1, 2, 3, 4]:
        yy = y0 - v / vmax * ph
        s += line(x0 - 5, yy, x0, yy, INK, 1)
        s += text(x0 - 9, yy + 4, str(v), 9, GREY, "end")
    s += text(x0 - 9, y0 - ph - 4, "В", 9, INK, "end", "bold")
    for p in [0, 25, 50, 75, 100]:
        xx = x0 + p / 100 * pw
        s += line(xx, y0, xx, y0 + 5, INK, 1)
        s += text(xx, y0 + 18, f"{p}%", 9, GREY, "middle")
    s += text(x0 + pw / 2, y0 + 34, "розряджено", 10, INK, "middle")

    def curve(pts, c, label, ly):
        path = [(x0 + p / 100 * pw, y0 - v / vmax * ph) for p, v in pts]
        out = poly(path, c, 2.6)
        out += text(x0 + pw + 6, ly, label, 9, c, "start", "bold")
        return out

    s += curve([(0, 4.2), (10, 4.0), (30, 3.8), (60, 3.6), (85, 3.3), (100, 3.0)], RED, "Li-ion", y0 - 3.6 / vmax * ph)
    s += curve([(0, 3.45), (8, 3.3), (20, 3.25), (80, 3.2), (92, 3.1), (100, 2.5)], AMBER, "LiFePO4", y0 - 3.2 / vmax * ph)
    s += curve([(0, 1.4), (10, 1.3), (25, 1.25), (80, 1.2), (92, 1.15), (100, 1.0)], GREEN, "NiMH", y0 - 1.2 / vmax * ph + 4)
    s += curve([(0, 2.1), (15, 2.0), (50, 1.95), (80, 1.9), (100, 1.75)], BLUE, "Свинець", y0 - 1.9 / vmax * ph)
    s += rect(70, H - 30, W - 140, 20, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "Похила крива (літій, свинець) дає оцінити заряд по напрузі; ПЛАСКА (LiFePO4, NiMH) — майже ні: напруга «бреше» на плато.", 9.5, INK, "middle")
    save("fig-10-1-3-discharge.svg", s)


# ── Рис. 10.4.1.4 — ресурс циклів ────────────────────────────────────────────
def fig_cycle_life():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Скільки циклів: і чому LiFePO4 виграє «на дистанції»", 18, INK, "middle", "bold")
    bars = [("Свинець", 300, BLUE), ("NiMH", 500, GREEN), ("Li-ion", 800, RED), ("LiFePO4", 3000, AMBER)]
    x0, y0 = 130, 320
    bw, gap, maxv, ph = 120, 70, 3200, 230
    s += line(x0, y0, W - 60, y0, INK, 1.6)
    s += line(x0, y0, x0, y0 - ph, INK, 1.6)
    for v in [0, 1000, 2000, 3000]:
        yy = y0 - v / maxv * ph
        s += line(x0 - 5, yy, x0, yy, INK, 1)
        s += text(x0 - 10, yy + 4, str(v), 8.5, GREY, "end")
    s += text(x0 - 8, y0 - ph - 4, "циклів", 9, INK, "end", "bold")
    for i, (name, v, c) in enumerate(bars):
        x = x0 + 50 + i * (bw + gap)
        h = v / maxv * ph
        s += rect(x, y0 - h, bw, h, "#fff", c, 2, 5)
        s += f'<rect x="{x:.0f}" y="{y0-h:.0f}" width="{bw}" height="{h:.0f}" rx="5" fill="{c}" fill-opacity="0.16"/>\n'
        s += text(x + bw / 2, y0 - h - 8, f"~{v}", 11.5, c, "middle", "bold")
        s += text(x + bw / 2, y0 + 18, name, 10, c, "middle", "bold")
    s += rect(70, H - 34, W - 140, 24, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 18, "LiFePO4 живе у 3–10 разів довше — тож, дорожчий за штуку, на ціну ОДНОГО циклу він часто найдешевший. Рахуй за весь термін, не за чек.", 9.5, INK, "middle")
    save("fig-10-1-4-cycles.svg", s)


# ── Рис. 10.4.1.5 — температурні вікна ───────────────────────────────────────
def fig_temp_windows():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Температурні вікна: заряд вужчий за розряд", 18, INK, "middle", "bold")
    x0, xr, tmin, tmax = 180, 660, -30, 60

    def tx(t):
        return x0 + (t - tmin) / (tmax - tmin) * xr

    s += line(x0, 320, x0 + xr, 320, INK, 1.4)
    for t in [-20, 0, 20, 40, 60]:
        s += line(tx(t), 320, tx(t), 326, INK, 1)
        s += text(tx(t), 340, f"{t}°C", 9, GREY, "middle")
    rows = [
        ("Li-ion / LiPo", 0, 45, -20, 60, RED, 90),
        ("LiFePO4", 0, 55, -20, 60, AMBER, 145),
        ("NiMH", 0, 45, -20, 55, GREEN, 200),
        ("Свинець", -20, 50, -30, 55, BLUE, 255),
    ]
    for name, cmin, cmax, dmin, dmax, c, y in rows:
        s += text(x0 - 12, y + 4, name, 10, c, "end", "bold")
        s += rect(tx(dmin), y - 9, tx(dmax) - tx(dmin), 18, "#f0f0f0", GREY, 1, 4)
        s += f'<rect x="{tx(cmin):.0f}" y="{y-9:.0f}" width="{tx(cmax)-tx(cmin):.0f}" height="18" rx="4" fill="{c}" fill-opacity="0.32" stroke="{c}" stroke-width="1.5"/>\n'
    s += rect(x0 + xr - 40, 78, 14, 12, "#cccccc", GREY, 1, 2)
    s += text(x0 + xr - 22, 88, "розряд", 8.5, GREY, "start")
    s += rect(x0 + xr - 40, 96, 14, 12, "#f7c9c4", RED, 1.2, 2)
    s += text(x0 + xr - 22, 106, "заряд", 8.5, RED, "start", "bold")
    s += line(tx(0), 78, tx(0), 300, RED, 1.4, dash="5,4")
    s += text(tx(0), 72, "0°C", 9, RED, "middle", "bold")
    s += rect(70, H - 34, W - 140, 24, "#fbe9e7", RED, 1.4, 8)
    s += text(W / 2, H - 18, "Залізне правило літію: НЕ заряджати нижче 0°C — інакше осідає металевий літій і комірка деградує (а то й коротить). Розряджати на морозі — можна.", 9.5, INK, "middle")
    save("fig-10-1-5-temp.svg", s)


# ── Рис. 10.4.1.6 — карта вибору ─────────────────────────────────────────────
def fig_decision_map():
    W, H = 940, 410
    s = header(W, H)
    s += text(W / 2, 32, "Яку хімію обрати: задача → батарея", 18, INK, "middle", "bold")
    cards = [
        ("Максимум енергії,|мінімум ваги", "Li-ion / LiPo", "дрон, носиме, мобільне|(ціна — захист, обережність)", RED, 50),
        ("Довге життя|й безпека", "LiFePO4", "стаціонар, сонце, робот|(пласка крива — SoC важче)", AMBER, 285),
        ("Дешево, безпечно,|готові «пальчики»", "NiMH", "прості пристрої, іграшки|(мала енергія, 1.2 В)", GREEN, 520),
        ("Дешева енергія|+ пусковий струм", "Свинець", "авто, ДБЖ, стаціонар|(важко; боїться розряду)", BLUE, 755),
    ]
    for q, chem, note, c, x in cards:
        s += rect(x, 70, 150, 250, "#ffffff", c, 2, 12)
        for j, ln in enumerate(q.split("|")):
            s += text(x + 75, 96 + j * 17, ln, 10, INK, "middle", "bold")
        s += line(x + 18, 138, x + 132, 138, FAINT, 1)
        s += text(x + 75, 168, chem, 12.5, c, "middle", "bold")
        s += text(x + 75, 188, "↓", 14, c, "middle", "bold")
        for j, ln in enumerate(note.split("|")):
            s += text(x + 75, 214 + j * 16, ln, 8.6, GREY, "middle")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 26, "Немає «найкращої» хімії — є найкраща під задачу. Зважують чотири осі: енергія на вагу, цикли (ціна за весь термін), безпека й температура.", 10, INK, "middle")
    s += text(W / 2, H - 12, "А далі в розділі — як саме заряджати обрану хімію, чесно оцінювати її залишок і захищати від відмов.", 9.5, GREY, "middle")
    save("fig-10-1-6-decision.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 10.4.2 — Внутрішній опір і просадка
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 10.4.2.1 — модель Rвн ───────────────────────────────────────────────
def fig_rint_model():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 32, "Реальна батарея = ідеальне джерело + внутрішній опір", 17, INK, "middle", "bold")
    s += rect(110, 88, 320, 200, "#fbfbf8", GREY, 1.5, 12)
    s += text(270, 110, "реальна комірка", 10.5, GREY, "middle", "bold")
    bx = 175
    s += line(bx - 20, 162, bx + 20, 162, INK, 3)
    s += line(bx - 11, 174, bx + 11, 174, INK, 6)
    s += line(bx - 20, 188, bx + 20, 188, INK, 3)
    s += line(bx - 11, 200, bx + 11, 200, INK, 6)
    s += text(bx - 30, 178, "OCV", 10.5, INK, "end", "bold")
    s += text(bx - 30, 194, "3.7 В", 8.5, GREY, "end")
    s += line(bx, 145, bx, 162, INK, 2)
    s += line(bx, 200, bx, 240, INK, 2)
    s += line(bx, 145, 250, 145, INK, 2)
    s += _res(250, 129, 70, 32, "Rвн", RED)
    s += line(320, 145, 405, 145, INK, 2)
    s += arrow(345, 145, 385, 145, RED, 1.8)
    s += text(365, 138, "I", 9.5, RED, "middle", "bold")
    s += circle(405, 145, 4, RED, RED, 0)
    s += text(414, 141, "+", 13, RED, "start", "bold")
    s += line(bx, 240, 405, 240, INK, 2)
    s += circle(405, 240, 4, BLUE, BLUE, 0)
    s += text(414, 246, "−", 13, BLUE, "start", "bold")
    s += text(270, 268, "клеми — те, що бачить пристрій", 9.5, INK, "middle")
    s += line(405, 145, 470, 145, INK, 2)
    s += line(405, 240, 470, 240, INK, 2)
    s += rect(470, 150, 90, 85, "#eef3fb", BLUE, 1.8, 8)
    s += text(515, 188, "наван-", 10, BLUE, "middle", "bold")
    s += text(515, 203, "таження", 10, BLUE, "middle", "bold")
    s += line(560, 150, 560, 235, INK, 2)
    s += line(470, 150, 470, 145, INK, 2)
    s += line(470, 235, 470, 240, INK, 2)
    s += rect(630, 108, 250, 160, "#f6f6f6", GREY, 1.4, 10)
    s += text(755, 134, "Що на клемах", 11.5, INK, "middle", "bold")
    s += text(755, 163, "V = OCV − I·Rвн", 14, RED, "middle", "bold")
    s += text(755, 190, "спокій (I=0): V = OCV", 10, INK, "middle")
    s += text(755, 210, "під струмом просідає на", 10, INK, "middle")
    s += text(755, 228, "I·Rвн — це й є ПРОСАДКА", 10.5, RED, "middle", "bold")
    s += text(755, 250, "більший I чи Rвн → глибше", 9.5, GREY, "middle")
    s += rect(70, H - 32, W - 140, 22, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 17, "Заряд може бути повний, та якщо Rвн великий, сильний струм «з'їдає» напругу на клемах — пристрій бачить менше, ніж є в комірці.", 9.5, INK, "middle")
    save("fig-10-2-1-model.svg", s)


# ── Рис. 10.4.2.2 — просадка під імпульсом ───────────────────────────────────
def fig_pulse_sag():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Просадка під імпульсом струму", 18, INK, "middle", "bold")
    x0, y0 = 90, 300
    pw, ph = 770, 230
    s += line(x0, y0, x0 + pw, y0, INK, 1.5)
    s += line(x0, y0, x0, y0 - ph, INK, 1.5)
    s += text(x0 - 9, y0 - ph - 2, "V клем", 9, INK, "end", "bold")
    s += text(x0 + pw, y0 + 18, "час →", 9.5, INK, "end")
    ocv = y0 - 200
    s += line(x0, ocv, x0 + pw, ocv, GREY, 1.2, dash="4,3")
    s += text(x0 + pw + 4, ocv + 4, "OCV", 9, GREY, "start", "bold")
    bo = y0 - 95
    s += line(x0, bo, x0 + pw, bo, RED, 1.3, dash="6,4")
    s += text(x0 + pw + 4, bo + 4, "поріг", 8.5, RED, "start", "bold")
    pa, pb = x0 + 300, x0 + 520
    s += f'<rect x="{pa:.0f}" y="{y0-ph:.0f}" width="{pb-pa:.0f}" height="{ph:.0f}" fill="#f4f4f4"/>\n'
    s += text((pa + pb) / 2, y0 - ph + 12, "імпульс струму (напр. радіо TX)", 8.5, GREY, "middle")
    sagL = y0 - 150
    s += poly([(x0, ocv), (pa, ocv), (pa, sagL), (pb, sagL), (pb, ocv), (x0 + pw, ocv)], GREEN, 2.6)
    s += text(pa + 10, sagL - 6, "малий Rвн — мілка просадка", 8.5, GREEN, "start", "bold")
    sagH = y0 - 55
    s += poly([(x0, ocv - 3), (pa, ocv - 3), (pa, sagH), (pb, sagH), (pb, ocv - 3), (x0 + pw, ocv - 3)], RED, 2.6)
    s += text(pa + 10, sagH + 14, "великий Rвн — провал ПІД поріг → ресет", 8.5, RED, "start", "bold")
    s += arrow(pa - 16, ocv, pa - 16, sagH, INK, 1.5)
    s += text(pa - 22, (ocv + sagH) / 2, "ΔV = I·Rвн", 8.5, INK, "end")
    s += rect(70, H - 30, W - 140, 20, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "Важлива не середня напруга, а ГЛИБИНА просадки під час піку: провалилася під поріг brownout — пристрій ресетиться.", 9.5, INK, "middle")
    save("fig-10-2-2-pulse.svg", s)


# ── Рис. 10.4.2.3 — двоточковий вимір ────────────────────────────────────────
def fig_measure_rint():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Виміряти Rвн: дві точки під різним струмом", 18, INK, "middle", "bold")
    x0, y0 = 110, 310
    pw, ph = 620, 240
    s += line(x0, y0, x0 + pw, y0, INK, 1.5)
    s += line(x0, y0, x0, y0 - ph, INK, 1.5)
    s += text(x0 + pw, y0 + 18, "струм I →", 9.5, INK, "end")
    s += text(x0 - 9, y0 - ph - 2, "V клем", 9, INK, "end", "bold")
    ocvY = y0 - 210
    p1 = (x0 + 120, y0 - 180)
    p2 = (x0 + 500, y0 - 70)
    s += line(x0, ocvY, p2[0] + 40, p2[1] - 12, GREY, 1.6, dash="5,4")
    s += circle(x0, ocvY, 4, INK, INK, 0)
    s += text(x0 - 8, ocvY - 6, "OCV (I=0)", 9, GREY, "end", "bold")
    s += circle(p1[0], p1[1], 5, RED, RED, 0)
    s += text(p1[0], p1[1] - 10, "(I1, V1)", 9.5, RED, "middle", "bold")
    s += circle(p2[0], p2[1], 5, RED, RED, 0)
    s += text(p2[0], p2[1] - 10, "(I2, V2)", 9.5, RED, "middle", "bold")
    s += line(p1[0], p1[1], p2[0], p1[1], INK, 1.2, dash="3,3")
    s += line(p2[0], p1[1], p2[0], p2[1], INK, 1.2, dash="3,3")
    s += text((p1[0] + p2[0]) / 2, p1[1] - 6, "ΔI", 9, INK, "middle", "bold")
    s += text(p2[0] + 8, (p1[1] + p2[1]) / 2, "ΔV", 9, INK, "start", "bold")
    s += rect(x0 + 40, 78, 300, 84, "#f6f6f6", GREY, 1.4, 10)
    s += text(x0 + 190, 104, "Rвн = ΔV / ΔI =", 12.5, INK, "middle", "bold")
    s += text(x0 + 190, 128, "(V1 − V2) / (I2 − I1)", 12.5, RED, "middle", "bold")
    s += text(x0 + 190, 150, "нахил лінії V(I) — це −Rвн", 9.5, GREY, "middle")
    s += rect(70, H - 34, W - 140, 24, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 18, "Два заміри напруги під легким і важким струмом — і Rвн з нахилу. AC-метод на 1 кГц дасть менше (ESR); для просадки важливіший саме DC.", 9.5, INK, "middle")
    save("fig-10-2-3-measure.svg", s)


# ── Рис. 10.4.2.4 — Rвн від SoC ──────────────────────────────────────────────
def fig_rint_soc():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Внутрішній опір залежить від заряду (SoC)", 18, INK, "middle", "bold")
    x0, y0 = 110, 310
    pw, ph = 660, 230
    s += line(x0, y0, x0 + pw, y0, INK, 1.5)
    s += line(x0, y0, x0, y0 - ph, INK, 1.5)
    s += text(x0 - 9, y0 - ph - 2, "Rвн", 9, INK, "end", "bold")
    for p in [0, 25, 50, 75, 100]:
        xx = x0 + p / 100 * pw
        s += line(xx, y0, xx, y0 + 5, INK, 1)
        s += text(xx, y0 + 18, f"{p}%", 9, GREY, "middle")
    s += text(x0 + pw / 2, y0 + 34, "заряд (SoC)", 10, INK, "middle")
    pts = [(0, 210), (8, 150), (20, 95), (50, 70), (80, 75), (92, 95), (100, 120)]
    path = [(x0 + p / 100 * pw, y0 - v) for p, v in pts]
    s += poly(path, RED, 2.8)
    s += text(x0 + 28, y0 - 188, "порожня →", 10, RED, "start", "bold")
    s += text(x0 + 28, y0 - 172, "Rвн великий", 10, INK, "start")
    s += text(x0 + pw * 0.5 - 30, y0 - 52, "середина — найменший Rвн", 9.5, GREEN, "middle", "bold")
    s += rect(70, H - 34, W - 140, 24, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 18, "Майже порожня комірка має найбільший Rвн — тому саме «на останніх відсотках» пристрій найлегше валиться під піком струму.", 9.5, INK, "middle")
    save("fig-10-2-4-soc.svg", s)


# ── Рис. 10.4.2.5 — Rвн від температури ──────────────────────────────────────
def fig_rint_temp():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Внутрішній опір залежить від температури", 18, INK, "middle", "bold")
    x0, y0 = 130, 310
    pw, ph = 620, 230
    s += line(x0, y0, x0 + pw, y0, INK, 1.5)
    s += line(x0, y0, x0, y0 - ph, INK, 1.5)
    s += text(x0 - 9, y0 - ph - 2, "Rвн", 9, INK, "end", "bold")
    for t in [-20, 0, 20, 40]:
        xx = x0 + (t + 20) / 60 * pw
        s += line(xx, y0, xx, y0 + 5, INK, 1)
        s += text(xx, y0 + 18, f"{t}°C", 9, GREY, "middle")
    s += text(x0 + pw / 2, y0 + 34, "температура", 10, INK, "middle")
    pts = [(-20, 205), (-10, 150), (0, 105), (10, 80), (20, 65), (30, 58), (40, 55)]
    path = [(x0 + (t + 20) / 60 * pw, y0 - v) for t, v in pts]
    s += poly(path, BLUE, 2.8)
    s += text(x0 + 40, y0 - 188, "мороз → Rвн", 10, BLUE, "start", "bold")
    s += text(x0 + 40, y0 - 172, "росте в рази", 10, INK, "start")
    s += text(x0 + pw - 30, y0 - 48, "тепло — низький", 9.5, GREEN, "end", "bold")
    s += rect(70, H - 34, W - 140, 24, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 18, "Ось чому телефон гасне на морозі, а авто не заводиться взимку: холод піднімає Rвн, і батарея не тягне піковий струм, хоч заряд є.", 9.5, INK, "middle")
    save("fig-10-2-5-temp.svg", s)


# ── Рис. 10.4.2.6 — проєктувати під просадку ─────────────────────────────────
def fig_rint_design():
    W, H = 940, 410
    s = header(W, H)
    s += text(W / 2, 32, "Що з цим робити: проєктувати під просадку", 18, INK, "middle", "bold")
    s += rect(60, 95, 110, 80, "#eef8ef", GREEN, 1.8, 10)
    s += text(115, 127, "батарея", 10.5, GREEN, "middle", "bold")
    s += text(115, 145, "OCV, Rвн", 8.5, INK, "middle")
    s += _res(190, 121, 56, 28, "Rвн", RED)
    s += line(170, 135, 190, 135, INK, 2)
    s += line(246, 135, 330, 135, INK, 2)
    s += circle(330, 135, 4, INK, INK, 0)
    s += line(330, 135, 330, 172, INK, 2)
    s += line(318, 172, 342, 172, INK, 3)
    s += line(318, 180, 342, 180, INK, 3)
    s += text(352, 180, "великий C", 9, AMBER, "start", "bold")
    s += line(330, 192, 330, 212, INK, 2)
    s += line(316, 212, 344, 212, INK, 2)
    s += line(430, 135, 430, 212, INK, 2)
    s += line(330, 212, 430, 212, INK, 2)
    s += line(330, 135, 360, 135, INK, 2)
    s += rect(360, 108, 100, 54, "#eef3fb", BLUE, 1.8, 8)
    s += text(410, 130, "навантаження", 8.5, BLUE, "middle", "bold")
    s += text(410, 147, "імпульсне", 8, INK, "middle")
    s += line(460, 135, 430, 135, INK, 2)
    s += text(255, 92, "C віддає ШВИДКИЙ пік, батарея — середнє", 9, AMBER, "middle", "bold")
    s += rect(600, 78, 310, 252, "#f6f6f6", GREY, 1.4, 10)
    s += text(755, 104, "Чотири ходи", 12, INK, "middle", "bold")
    items = [
        "• Бери комірку під ПІК струму",
        "   (низький Rвн, високий C-rate)",
        "• Не працюй біля «порожньо»,",
        "   якщо потрібні піки",
        "• Великий конденсатор —",
        "   для КОРОТКИХ піків (мс і менше)",
        "• Поріг brownout — із запасом",
        "   на найгіршу просадку",
    ]
    for i, t in enumerate(items):
        s += text(616, 132 + i * 23, t, 9.5, INK, "start")
    s += rect(70, H - 50, W - 140, 38, "#fbf7ec", AMBER, 1.4, 9)
    s += text(W / 2, H - 32, "Чесний нюанс: конденсатор рятує лише КОРОТКІ піки (мікро- й мілісекунди). Довгий пік (радіо TX на 100 мс) йому не під силу —", 9.5, INK, "middle")
    s += text(W / 2, H - 17, "тут потрібна сама комірка з малим Rвн або більша батарея. Деталі розрахунку — у 🧮-вставці про просадку.", 9.5, INK, "middle")
    save("fig-10-2-6-design.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 10.4.3 — Заряд правильно: CC/CV
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 10.4.3.1 — профіль CC/CV ────────────────────────────────────────────
def fig_ccv_curves():
    W, H = 960, 440
    s = header(W, H)
    s += text(W / 2, 32, "CC/CV: як заряджають літій", 18, INK, "middle", "bold")
    x0, y0 = 100, 330
    pw, ph = 720, 250
    s += line(x0, y0, x0 + pw, y0, INK, 1.5)
    s += line(x0, y0, x0, y0 - ph, INK, 1.5)
    s += line(x0 + pw, y0, x0 + pw, y0 - ph, GREY, 1.2)
    s += text(x0 - 9, y0 - ph - 2, "напруга", 9, BLUE, "end", "bold")
    s += text(x0 + pw + 9, y0 - ph - 2, "струм", 9, RED, "start", "bold")
    s += text(x0 + pw, y0 + 18, "час →", 9.5, INK, "end")
    xp = x0 + 0.08 * pw
    xcc = x0 + 0.55 * pw
    xend = x0 + 0.95 * pw
    for xb in [xp, xcc, xend]:
        s += line(xb, y0, xb, y0 - ph, FAINT, 1, dash="4,3")
    s += text((x0 + xp) / 2, y0 - ph - 4, "перед-", 8, GREY, "middle")
    s += text((x0 + xp) / 2, y0 - ph + 8, "заряд", 8, GREY, "middle")
    s += text((xp + xcc) / 2, y0 - ph - 2, "CC — сталий струм", 9.5, INK, "middle", "bold")
    s += text((xcc + xend) / 2, y0 - ph - 2, "CV — стала напруга", 9.5, INK, "middle", "bold")
    s += text((xend + x0 + pw) / 2, y0 - ph + 8, "стоп", 8.5, GREEN, "middle", "bold")
    vfull = y0 - 4.2 / 4.5 * ph
    vstart = y0 - 3.0 / 4.5 * ph
    vpre = y0 - 3.2 / 4.5 * ph
    s += poly([(x0, vstart), (xp, vpre), (xcc, vfull), (xend, vfull), (x0 + pw, vfull)], BLUE, 2.8)
    s += line(x0, vfull, x0 + pw, vfull, BLUE, 1, dash="2,3")
    s += text(x0 - 9, vfull + 4, "4.2 В", 9, BLUE, "end", "bold")
    imax = y0 - 0.85 * ph
    ipre = y0 - 0.15 * ph
    iterm = y0 - 0.10 * ph
    s += poly([(x0, ipre), (xp, ipre), (xp, imax), (xcc, imax)], RED, 2.8)
    taper = [(xcc, imax), (xcc + (xend - xcc) * 0.2, y0 - 0.55 * ph),
             (xcc + (xend - xcc) * 0.45, y0 - 0.32 * ph),
             (xcc + (xend - xcc) * 0.7, y0 - 0.18 * ph), (xend, iterm)]
    s += poly(taper, RED, 2.8)
    s += line(xend, iterm, x0 + pw, iterm, RED, 1.5, dash="3,3")
    s += text(x0 + pw + 8, iterm + 4, "C/10", 8.5, RED, "start", "bold")
    s += text(xcc + 8, imax - 6, "Imax", 8.5, RED, "start", "bold")
    s += rect(70, H - 50, W - 140, 38, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 32, "CC: ллємо сталий струм, напруга росте до 4.2 В (тут — більшість ємності). CV: тримаємо 4.2 В, струм сам спадає.", 9.5, INK, "middle")
    s += text(W / 2, H - 17, "Коли струм у CV впав нижче ~C/10 — заряд СТОП. Літій не «доливають» струмом без кінця, на відміну від старих хімій.", 9.5, INK, "middle")
    save("fig-10-3-1-ccv.svg", s)


# ── Рис. 10.4.3.2 — фази заряду ──────────────────────────────────────────────
def fig_charge_phases():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 32, "Фази заряду літію: від «мертвої» до повної", 18, INK, "middle", "bold")
    boxes = [
        ("низька дуже?", "якщо < ~3 В —", "обережний старт", AMBER, 40),
        ("ПЕРЕДЗАРЯД", "малий струм,", "поки V не підросте", GREY, 225),
        ("CC", "повний струм,", "напруга росте", BLUE, 410),
        ("CV", "тримаю 4.2 В,", "струм спадає", GREEN, 595),
        ("СТОП", "I < C/10 —", "заряд завершено", RED, 780),
    ]
    for title, l1, l2, c, x in boxes:
        s += rect(x, 86, 130, 96, "#ffffff", c, 2, 10)
        s += text(x + 65, 112, title, 11, c, "middle", "bold")
        s += text(x + 65, 142, l1, 9, INK, "middle")
        s += text(x + 65, 158, l2, 9, INK, "middle")
        if x < 780:
            s += arrow(x + 130, 134, x + 185, 134, INK, 2)
    s += text(W / 2, 224, "у нормі комірка стартує одразу з CC; передзаряд — лише для глибоко сівшої (пор. power path, 10.3.6)", 9.5, INK, "middle")
    s += rect(70, H - 50, W - 140, 38, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 32, "Більшість заряду входить у фазі CC; повільний «хвіст» CV доливає останні відсотки. Передзаряд рятує глибоко розряджену", 9.5, INK, "middle")
    s += text(W / 2, H - 17, "комірку: повний струм у майже мертвий літій небезпечний, тож спершу — крапельку, поки напруга не вийде в безпечну зону.", 9.5, INK, "middle")
    save("fig-10-3-2-phases.svg", s)


# ── Рис. 10.4.3.3 — точність 4.2 В ───────────────────────────────────────────
def fig_voltage_accuracy():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Чому 4.2 В треба точно: ємність проти життя", 18, INK, "middle", "bold")
    cx = 250
    y_top, y_bot = 84, 318
    s += line(cx, y_top, cx, y_bot, INK, 2)
    s += arrow(cx, y_top, cx, y_top - 10, RED, 1.6)
    marks = [
        (4.25, RED, "перезаряд: стрес, нагрів,", "ризик — НЕ можна"),
        (4.20, INK, "стандарт: повна ємність", "(точність ±1%!)"),
        (4.10, GREEN, "трохи менше ємності,", "та життя в РАЗИ довше"),
        (4.00, GREEN, "ще довговічніше", "(довге зберігання)"),
    ]
    for v, c, l1, l2 in marks:
        y = y_bot - (v - 3.95) / (4.30 - 3.95) * (y_bot - y_top)
        s += line(cx - 8, y, cx + 8, y, c, 2.5)
        s += circle(cx, y, 4, c, c, 0)
        s += text(cx - 16, y + 4, f"{v:.2f} В", 11, c, "end", "bold")
        s += text(cx + 22, y, l1, 10, INK, "start")
        s += text(cx + 22, y + 15, l2, 9, GREY, "start")
    s += text(cx + 4, y_top - 16, "вище → ємніше, та менше життя й безпеки", 8.5, RED, "start")
    s += text(cx, y_bot + 18, "↓ нижче → менше ємності, довше життя", 8.5, GREEN, "middle")
    s += rect(70, H - 50, W - 140, 38, "#fbe9e7", RED, 1.4, 9)
    s += text(W / 2, H - 32, "Заряд літію — балансування на вольтах: 4.25 В уже небезпечні, 4.20 дають повну ємність, 4.10 коштують кількох відсотків", 9.5, INK, "middle")
    s += text(W / 2, H - 17, "ємності, зате подовжують життя в рази. Тому точність опорної напруги критична, а навмисний недозаряд — легальний прийом.", 9.5, INK, "middle")
    save("fig-10-3-3-voltage.svg", s)


# ── Рис. 10.4.3.4 — заряд за температурою (JEITA) ────────────────────────────
def fig_jeita_temp():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Заряд за температурою (стиль JEITA)", 18, INK, "middle", "bold")
    x0, xr, tmin, tmax = 120, 720, -20, 60

    def tx(t):
        return x0 + (t - tmin) / (tmax - tmin) * xr

    yb = 250
    zones = [
        (-20, 0, "#e7ecf5", "НЕ заряджати", "(мороз губить літій)", RED),
        (0, 10, "#f3ecdf", "знижений струм", "(напр. половина)", AMBER),
        (10, 45, "#dff0e1", "повний заряд", "CC/CV 4.2 В", GREEN),
        (45, 60, "#fdeeea", "знижена V / стоп", "(спека старить)", RED),
    ]
    for t1, t2, fill, l1, l2, c in zones:
        s += f'<rect x="{tx(t1):.0f}" y="150" width="{tx(t2)-tx(t1):.0f}" height="86" fill="{fill}" stroke="{c}" stroke-width="1.4" rx="4"/>\n'
        s += text((tx(t1) + tx(t2)) / 2, 186, l1, 9.5, c, "middle", "bold")
        s += text((tx(t1) + tx(t2)) / 2, 206, l2, 8.5, INK, "middle")
    s += line(x0, yb, x0 + xr, yb, INK, 1.4)
    for t in [-20, 0, 10, 25, 45, 60]:
        s += line(tx(t), yb, tx(t), yb + 5, INK, 1)
        s += text(tx(t), yb + 18, f"{t}°", 9, GREY, "middle")
    s += text(x0 + xr / 2, yb + 36, "температура комірки (давач TS)", 10, INK, "middle")
    s += rect(70, H - 50, W - 140, 38, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 32, "Заряд безпечний лише у вузькому вікні. На холоді струм знижують (а нижче 0°C взагалі не заряджають), на спеці знижують", 9.5, INK, "middle")
    s += text(W / 2, H - 17, "напругу або зупиняються. Усе це чип робить за давачем температури TS — тим самим, що ми бачили в зарядних мікросхемах.", 9.5, INK, "middle")
    save("fig-10-3-4-jeita.svg", s)


# ── Рис. 10.4.3.5 — заряд за хімією ──────────────────────────────────────────
def fig_charge_targets():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Кожна хімія заряджається по-своєму", 18, INK, "middle", "bold")
    s += rect(50, 64, 840, 30, "#eef3fb", BLUE, 1.4, 6)
    cols = ["Хімія", "Цільова напруга", "Як", "Термінація"]
    cx = [70, 300, 540, 710]
    for i, t in enumerate(cols):
        s += text(cx[i], 84, t, 10.5, BLUE, "start", "bold")
    rows = [
        ("Li-ion", "4.20 В/елем", "CC/CV", "струм < C/10", RED),
        ("LiFePO4", "3.65 В/елем", "CC/CV", "струм < C/10", AMBER),
        ("Свинець", "2.40 → 2.30 (float)", "CC/CV + плавання", "перехід на float", BLUE),
        ("NiMH", "~1.45 В/елем", "сталий струм", "−ΔV або dT/dt", GREEN),
    ]
    for r, (chem, volt, how, term, c) in enumerate(rows):
        y = 100 + r * 52
        s += rect(50, y, 840, 48, "#ffffff" if r % 2 == 0 else "#f7f7f7", FAINT, 1, 0)
        s += text(cx[0], y + 30, chem, 11, c, "start", "bold")
        s += text(cx[1], y + 30, volt, 10.5, INK, "start")
        s += text(cx[2], y + 30, how, 10.5, INK, "start")
        s += text(cx[3], y + 30, term, 10.5, INK, "start")
    s += rect(70, H - 44, W - 140, 32, "#fbe9e7", RED, 1.4, 9)
    s += text(W / 2, H - 26, "Алгоритм заряду — частина ХІМІЇ, а не дрібниця: літій тримають по напрузі й зупиняють за струмом; NiMH — навпаки,", 9.5, INK, "middle")
    s += text(W / 2, H - 11, "заряджають струмом і ловлять кінець за −ΔV. Зарядити одну хімію «методом» іншої — псування, а то й небезпека.", 9.5, INK, "middle")
    save("fig-10-3-5-targets.svg", s)


# ── Рис. 10.4.3.6 — зарядний вузол ───────────────────────────────────────────
def fig_charge_node():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 32, "Зарядний вузол: що задаємо й що стережемо", 18, INK, "middle", "bold")
    s += rect(50, 150, 110, 64, "#fbe9e7", RED, 1.8, 10)
    s += text(105, 178, "вхід 5 В", 10, RED, "middle", "bold")
    s += text(105, 196, "(USB)", 8.5, INK, "middle")
    s += arrow(160, 182, 228, 182, RED, 2.4)
    s += rect(230, 118, 220, 152, "#eef8ef", GREEN, 2, 12)
    s += text(340, 144, "зарядний чип CC/CV", 11, GREEN, "middle", "bold")
    for i, t in enumerate(["• ISET — струм фази CC", "• VSET = 4.2 В (точно!)", "• термінація на C/10", "• TS — темп. вікно"]):
        s += text(248, 172 + i * 22, t, 9.5, INK, "start")
    s += arrow(450, 182, 518, 182, RED, 2.4)
    s += rect(520, 150, 110, 64, "#eef8ef", GREEN, 1.8, 10)
    s += text(575, 178, "комірка", 10, GREEN, "middle", "bold")
    s += text(575, 196, "Li 1S", 8.5, INK, "middle")
    s += line(575, 214, 575, 250, INK, 1.4, dash="3,3")
    s += _res(550, 250, 50, 26, "TS", AMBER)
    s += line(575, 276, 575, 290, AMBER, 1.4, dash="3,3")
    s += line(575, 290, 340, 290, AMBER, 1.4, dash="3,3")
    s += line(340, 290, 340, 270, AMBER, 1.4, dash="3,3")
    s += text(700, 268, "термістор на комірці", 8.5, AMBER, "middle")
    s += line(450, 138, 700, 138, BLUE, 1.4, dash="4,3")
    s += rect(700, 118, 160, 44, "#eef3fb", BLUE, 1.6, 8)
    s += text(780, 138, "STAT → МК / LED", 9.5, BLUE, "middle", "bold")
    s += text(780, 154, "заряд / готово", 8.5, INK, "middle")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 26, "Розробник задає лише струм (ISET) і покладається на точну опорну 4.2 В та термінацію чипа; давач TS блокує заряд поза вікном.", 9.5, INK, "middle")
    s += text(W / 2, H - 11, "Готовий чип робить усю CC/CV-логіку сам — конкретику обв'язки розберемо у 🔌-вставці про зарядник TP4056-класу.", 9.5, INK, "middle")
    save("fig-10-3-6-node.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 10.4.4 — Скільки лишилось: SoC
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 10.4.4.1 — проблема паливоміра ──────────────────────────────────────
def fig_soc_problem():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Скільки лишилось? — батарея не показує сама", 18, INK, "middle", "bold")
    s += rect(70, 110, 130, 180, "#eef8ef", GREEN, 2, 12)
    s += rect(110, 96, 50, 16, "#eef8ef", GREEN, 2, 4)
    s += text(135, 232, "?", 58, GREY, "middle", "bold")
    s += text(135, 262, "скільки %", 10, INK, "middle", "bold")
    s += text(135, 308, "видно лише V та I на клемах", 8.5, GREY, "middle")
    s += arrow(210, 200, 268, 200, INK, 2)
    cards = [
        ("1. Напруга", "глянь на V → SoC", "швидко, та БРЕШЕ", AMBER, 290),
        ("2. Кулонометрія", "лічи заряд (∫I·dt)", "точно, та ДРЕЙФУЄ", BLUE, 540),
        ("3. Фьюжн", "поєднай обидва", "найкраще на практиці", GREEN, 790),
    ]
    for t, l1, l2, c, x in cards:
        s += rect(x, 130, 130, 130, "#ffffff", c, 2, 10)
        s += text(x + 65, 158, t, 11, c, "middle", "bold")
        s += text(x + 65, 192, l1, 9, INK, "middle")
        s += text(x + 65, 224, l2, 9, GREY, "middle")
    s += rect(70, H - 34, W - 140, 24, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 18, "Усе, що видно ззовні, — напруга й струм на клемах. «Паливомір» батареї доводиться РАХУВАТИ з них, і кожен спосіб має свою ваду.", 9.5, INK, "middle")
    save("fig-10-4-1-problem.svg", s)


# ── Рис. 10.4.4.2 — метод напруги ────────────────────────────────────────────
def fig_voltage_method():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 32, "Напруга → SoC: працює на похилій, бреше на плато", 18, INK, "middle", "bold")
    x0, y0 = 110, 330
    pw, ph = 700, 250
    s += line(x0, y0, x0 + pw, y0, INK, 1.5)
    s += line(x0, y0, x0, y0 - ph, INK, 1.5)
    s += text(x0 - 9, y0 - ph - 2, "V", 9, INK, "end", "bold")
    for p in [0, 25, 50, 75, 100]:
        xx = x0 + p / 100 * pw
        s += line(xx, y0, xx, y0 + 5, INK, 1)
        s += text(xx, y0 + 18, f"{p}%", 9, GREY, "middle")
    s += text(x0 + pw / 2, y0 + 34, "SoC (заряд)", 10, INK, "middle")

    def vy(v):
        return y0 - (v - 2.8) / (4.4 - 2.8) * ph

    li = [(0, 3.0), (20, 3.5), (50, 3.7), (80, 4.0), (100, 4.2)]
    s += poly([(x0 + p / 100 * pw, vy(v)) for p, v in li], RED, 2.6)
    s += text(x0 + pw * 0.55, vy(3.72) - 8, "Li-ion (похила)", 9.5, RED, "start", "bold")
    lfp = [(0, 2.8), (12, 3.15), (25, 3.22), (75, 3.28), (88, 3.32), (100, 3.45)]
    s += poly([(x0 + p / 100 * pw, vy(v)) for p, v in lfp], AMBER, 2.6)
    s += text(x0 + pw * 0.28, vy(3.22) + 18, "LiFePO4 (плато)", 9.5, AMBER, "start", "bold")
    s += f'<rect x="{x0+0.2*pw:.0f}" y="{vy(3.33):.0f}" width="{0.55*pw:.0f}" height="{vy(3.18)-vy(3.33):.0f}" fill="#caa24a" fill-opacity="0.16"/>\n'
    s += text(x0 + 0.47 * pw, vy(3.25) - 2, "тут 10 мВ = десятки % SoC", 8.5, AMBER, "middle", "bold")
    s += rect(70, H - 30, W - 140, 20, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "На похилій Li-ion напрузі SoC читається пристойно. На пласкому плато LFP дрібна похибка напруги (чи просадка I·Rвн) дає велетенську похибку SoC.", 9, INK, "middle")
    save("fig-10-4-2-voltage.svg", s)


# ── Рис. 10.4.4.3 — кулонометрія ─────────────────────────────────────────────
def fig_coulomb():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Кулонометрія: лічимо заряд, але він дрейфує", 18, INK, "middle", "bold")
    s += rect(60, 66, 820, 38, "#f6f6f6", GREY, 1.4, 8)
    s += text(W / 2, 91, "SoC = SoC(старт) − (∫ I·dt) / Ємність     — як лічильник витрати на «паливній» трубі", 12, INK, "middle", "bold")
    x0, y0 = 110, 320
    pw, ph = 700, 170
    s += line(x0, y0, x0 + pw, y0, INK, 1.5)
    s += line(x0, y0, x0, y0 - ph, INK, 1.5)
    s += text(x0 - 9, y0 - ph - 2, "SoC", 9, INK, "end", "bold")
    s += text(x0 + pw, y0 + 18, "час →", 9, INK, "end")
    s += poly([(x0, y0 - ph * 0.9), (x0 + pw, y0 - ph * 0.2)], GREEN, 2.6)
    s += text(x0 + pw + 4, y0 - ph * 0.2 + 4, "істина", 8.5, GREEN, "start", "bold")
    s += poly([(x0, y0 - ph * 0.9), (x0 + pw, y0 - ph * 0.34)], RED, 2.6, dash="6,4")
    s += text(x0 + pw * 0.55, y0 - ph * 0.66, "оцінка дрейфує", 8.5, RED, "start", "bold")
    s += arrow(x0 + pw * 0.86, y0 - ph * 0.3, x0 + pw * 0.86, y0 - ph * 0.21, INK, 1.4)
    s += text(x0 + pw * 0.86 + 6, y0 - ph * 0.27, "помилка росте", 8, INK, "start")
    s += rect(70, H - 44, W - 140, 32, "#fbf7ec", AMBER, 1.4, 9)
    s += text(W / 2, H - 26, "Інтеграл струму точний КОРОТКО, та накопичує помилку: зсув давача струму потроху додається, а справжню ємність (що тане) лічильник", 9.2, INK, "middle")
    s += text(W / 2, H - 11, "не знає. Тому без періодичного «обнулення» оцінка з часом розходиться з істиною.", 9.2, INK, "middle")
    save("fig-10-4-3-coulomb.svg", s)


# ── Рис. 10.4.4.4 — фьюжн ────────────────────────────────────────────────────
def fig_fusion():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Фьюжн: кулонометрія + напруга = найкраще", 18, INK, "middle", "bold")
    s += rect(60, 90, 250, 80, "#eef3fb", BLUE, 1.8, 10)
    s += text(185, 116, "Кулонометрія", 11, BLUE, "middle", "bold")
    s += text(185, 138, "гладко, точно коротко,", 9, INK, "middle")
    s += text(185, 154, "та повільно дрейфує", 9, INK, "middle")
    s += rect(60, 220, 250, 80, "#f3ecdf", AMBER, 1.8, 10)
    s += text(185, 246, "Напруга (у спокої)", 11, AMBER, "middle", "bold")
    s += text(185, 268, "шумна, та АБСОЛЮТНА —", 9, INK, "middle")
    s += text(185, 284, "не дрейфує", 9, INK, "middle")
    s += arrow(310, 130, 418, 175, INK, 2)
    s += arrow(310, 260, 418, 215, INK, 2)
    s += rect(420, 150, 200, 90, "#eef8ef", GREEN, 2, 12)
    s += text(520, 180, "ПОЄДНАННЯ", 12, GREEN, "middle", "bold")
    s += text(520, 202, "коротко — лічимо заряд,", 9, INK, "middle")
    s += text(520, 218, "напруга підправляє дрейф", 9, INK, "middle")
    s += arrow(620, 195, 698, 195, GREEN, 2.4)
    s += rect(700, 160, 180, 70, "#ffffff", GREEN, 1.8, 10)
    s += text(790, 188, "точний SoC", 11, GREEN, "middle", "bold")
    s += text(790, 208, "стабільний, без дрейфу", 8.5, INK, "middle")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 26, "Кожен спосіб латає ваду іншого: лічильник заряду дає гладкість і коротку точність, напруга — абсолютну прив'язку, що не дає дрейфу", 9.2, INK, "middle")
    s += text(W / 2, H - 11, "накопичитись. Саме так працюють сучасні «паливоміри» (fuel gauge), нерідко ще й з моделлю конкретної комірки всередині.", 9.2, INK, "middle")
    save("fig-10-4-4-fusion.svg", s)


# ── Рис. 10.4.4.5 — перекалібрування ─────────────────────────────────────────
def fig_recalibrate():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Перекалібрування: краї кривої — надійні якорі", 18, INK, "middle", "bold")
    x0, y0 = 110, 310
    pw, ph = 700, 220
    s += line(x0, y0, x0 + pw, y0, INK, 1.5)
    s += line(x0, y0, x0, y0 - ph, INK, 1.5)
    s += text(x0 - 9, y0 - ph - 2, "V", 9, INK, "end", "bold")
    for p in [0, 50, 100]:
        xx = x0 + p / 100 * pw
        s += line(xx, y0, xx, y0 + 5, INK, 1)
        s += text(xx, y0 + 18, f"{p}%", 9, GREY, "middle")
    s += text(x0 + pw / 2, y0 + 34, "SoC", 10, INK, "middle")

    def vy(v):
        return y0 - (v - 2.8) / (4.4 - 2.8) * ph

    curve = [(0, 2.9), (8, 3.4), (20, 3.62), (50, 3.72), (80, 3.95), (92, 4.1), (100, 4.2)]
    s += f'<rect x="{x0:.0f}" y="{y0-ph:.0f}" width="{0.18*pw:.0f}" height="{ph:.0f}" fill="#1f8a3b" fill-opacity="0.12"/>\n'
    s += f'<rect x="{x0+0.82*pw:.0f}" y="{y0-ph:.0f}" width="{0.18*pw:.0f}" height="{ph:.0f}" fill="#1f8a3b" fill-opacity="0.12"/>\n'
    s += poly([(x0 + p / 100 * pw, vy(v)) for p, v in curve], BLUE, 2.8)
    s += text(x0 + 0.09 * pw, y0 - ph + 14, "круто — добрий якір", 8.3, GREEN, "middle", "bold")
    s += text(x0 + 0.91 * pw, y0 - ph + 14, "круто — добрий якір", 8.3, GREEN, "middle", "bold")
    s += text(x0 + 0.5 * pw, vy(3.72) - 12, "пласко — поганий якір", 8.5, AMBER, "middle", "bold")
    s += circle(x0 + pw, vy(4.2), 6, "none", RED, 2.5)
    s += text(x0 + pw - 4, vy(4.2) - 12, "повний = 100%", 8.5, RED, "end", "bold")
    s += circle(x0, vy(2.9), 6, "none", RED, 2.5)
    s += text(x0 + 40, vy(2.9) + 4, "відсічка = 0%", 8.5, RED, "start", "bold")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 26, "Дрейф кулонометрії «обнуляють» на ВІДОМИХ точках: повний заряд (термінація, 10.4.3) = 100%, відсічка = 0%, де напруга крута й надійна.", 9.2, INK, "middle")
    s += text(W / 2, H - 11, "Тому кожен повний заряд заодно перекалібровує паливомір — а в пласкій середині покладаються на лічбу заряду, не на напругу.", 9.2, INK, "middle")
    save("fig-10-4-5-recal.svg", s)


# ── Рис. 10.4.4.6 — вибір методу ─────────────────────────────────────────────
def fig_soc_decision():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Який метод обрати — і три залізні правила", 18, INK, "middle", "bold")
    cards = [
        ("Похила Li-ion,|треба дешево", "напруга у спокої", "проста оцінка, без чипа", RED, 60),
        ("Пласка LFP /|потрібна точність", "кулонометрія + напруга", "паливомір (fuel gauge)", AMBER, 360),
        ("Складна система,|телеметрія", "паливомір з моделлю", "+ SoH, прогноз часу", GREEN, 660),
    ]
    for q, m, note, c, x in cards:
        s += rect(x, 70, 230, 130, "#ffffff", c, 2, 12)
        for j, ln in enumerate(q.split("|")):
            s += text(x + 115, 96 + j * 17, ln, 10.5, INK, "middle", "bold")
        s += line(x + 20, 134, x + 210, 134, FAINT, 1)
        s += text(x + 115, 158, m, 11, c, "middle", "bold")
        s += text(x + 115, 180, note, 8.8, GREY, "middle")
    s += rect(70, 220, W - 140, 110, "#eef8ef", GREEN, 1.5, 10)
    s += text(W / 2, 246, "Три залізні правила паливоміра", 12, GREEN, "middle", "bold")
    s += text(W / 2, 272, "1) перекалібровуй на повному заряді (і на відсічці) — там напруга надійна;", 10, INK, "middle")
    s += text(W / 2, 294, "2) не вір останнім ~10% — там найбільша невизначеність;", 10, INK, "middle")
    s += text(W / 2, 316, "3) врахуй, що ємність тане з віком — інакше «100%» старої батареї бреше (про старіння — далі).", 10, INK, "middle")
    save("fig-10-4-6-decision.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 10.4.5 — Старіння: цикли, календар, SoH
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 10.4.5.1 — два старіння ─────────────────────────────────────────────
def fig_two_agings():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Два старіння: від циклів і просто від часу", 18, INK, "middle", "bold")
    x0, y0 = 100, 320
    pw, ph = 720, 240
    s += line(x0, y0, x0 + pw, y0, INK, 1.5)
    s += line(x0, y0, x0, y0 - ph, INK, 1.5)
    s += text(x0 - 9, y0 - ph - 2, "ємність", 9, INK, "end", "bold")
    s += text(x0 + pw, y0 + 18, "час / використання →", 9, INK, "end")
    s += text(x0 - 12, y0 - ph + 4, "100%", 8.5, GREY, "end")
    s += line(x0, y0 - ph, x0 + pw, y0 - ph, FAINT, 1)
    s += poly([(x0, y0 - ph), (x0 + pw, y0 - ph * 0.78)], GREEN, 2.6, dash="6,4")
    s += text(x0 + pw * 0.46, y0 - ph * 0.86, "лише час (календарне)", 9, GREEN, "start", "bold")
    s += poly([(x0, y0 - ph), (x0 + pw * 0.5, y0 - ph * 0.72), (x0 + pw, y0 - ph * 0.5)], RED, 2.8)
    s += text(x0 + pw * 0.55, y0 - ph * 0.45, "час + цикли", 9.5, RED, "start", "bold")
    s += line(x0, y0 - ph * 0.8, x0 + pw, y0 - ph * 0.8, AMBER, 1.2, dash="3,3")
    s += text(x0 + 6, y0 - ph * 0.8 - 4, "кінець життя ~80%", 8.5, AMBER, "start", "bold")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 26, "Батарея старіє двома шляхами одразу: від кожного циклу заряд-розряд і просто від часу (навіть лежачи в шухляді).", 9.2, INK, "middle")
    s += text(W / 2, H - 11, "Обидва зменшують ємність і піднімають Rвн (теми 10.4.2/10.4.4). Тепло пришвидшує і те, і те.", 9.2, INK, "middle")
    save("fig-10-5-1-two-agings.svg", s)


# ── Рис. 10.4.5.2 — спад ємності, ріст опору ─────────────────────────────────
def fig_capacity_fade():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Спад ємності та зростання опору з циклами", 18, INK, "middle", "bold")
    x0, y0 = 100, 320
    pw, ph = 720, 240
    s += line(x0, y0, x0 + pw, y0, INK, 1.5)
    s += line(x0, y0, x0, y0 - ph, INK, 1.5)
    s += text(x0 - 9, y0 - ph - 2, "ємність %", 9, BLUE, "end", "bold")
    s += text(x0 + pw, y0 + 18, "цикли →", 9, INK, "end")
    for cy, lab in [(100, "100"), (80, "80"), (60, "60")]:
        yy = y0 - cy / 110 * ph
        s += line(x0 - 5, yy, x0, yy, INK, 1)
        s += text(x0 - 10, yy + 4, lab, 8.5, GREY, "end")
    fade = [(0, 100), (20, 97), (40, 93), (60, 88), (80, 82), (100, 76)]
    s += poly([(x0 + p / 100 * pw, y0 - c / 110 * ph) for p, c in fade], BLUE, 2.8)
    s += line(x0, y0 - 80 / 110 * ph, x0 + pw, y0 - 80 / 110 * ph, AMBER, 1.4, dash="6,4")
    s += text(x0 + pw - 4, y0 - 80 / 110 * ph - 6, "кінець життя ≈ 80%", 8.5, AMBER, "end", "bold")
    s += poly([(x0, y0 - 0.1 * ph), (x0 + pw * 0.6, y0 - 0.25 * ph), (x0 + pw, y0 - 0.55 * ph)], RED, 2.4, dash="4,3")
    s += text(x0 + pw * 0.5, y0 - 0.4 * ph, "Rвн росте", 9, RED, "start", "bold")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 26, "З циклами ємність повзе вниз, а внутрішній опір — угору. Умовний «кінець життя» зазвичай беруть за падіння ємності до 80%", 9.2, INK, "middle")
    s += text(W / 2, H - 11, "від початкової — але це не «смерть», а поріг, де батарею пора планувати на заміну. Швидкість спаду залежить від умов.", 9.2, INK, "middle")
    save("fig-10-5-2-fade.svg", s)


# ── Рис. 10.4.5.3 — прискорювачі старіння ────────────────────────────────────
def fig_killers():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Що пришвидшує старіння літію", 18, INK, "middle", "bold")
    cards = [
        ("Спека", "кожні +10°C ≈ вдвічі|швидше (Арреніус)", RED, 40, 215),
        ("Зберігання на 100%", "повний заряд старить|найшвидше, надто в теплі", AMBER, 270, 215),
        ("Глибокий розряд", "розряд «у нуль» і нижче|ушкоджує комірку", BLUE, 500, 180),
        ("Струм і холодний заряд", "великий C-rate, заряд <0°C —|стрес і осад літію", "#9b59b6", 695, 205),
    ]
    for title, body, c, x, w in cards:
        s += rect(x, 80, w, 150, "#ffffff", c, 2, 12)
        s += text(x + w / 2, 110, title, 10.8, c, "middle", "bold")
        s += line(x + 15, 122, x + w - 15, 122, FAINT, 1)
        for j, ln in enumerate(body.split("|")):
            s += text(x + w / 2, 150 + j * 18, ln, 8.6, INK, "middle")
    s += rect(70, H - 50, W - 140, 38, "#fbe9e7", RED, 1.4, 9)
    s += text(W / 2, H - 32, "Головний прискорювач — ТЕПЛО: воно множить швидкість усіх реакцій старіння. Найгірша пара — гаряче І повністю заряджене.", 9.5, INK, "middle")
    s += text(W / 2, H - 17, "За календарним старінням стоїть переважно ріст захисного шару SEI, що поволі з'їдає літій і піднімає опір.", 9.5, INK, "middle")
    save("fig-10-5-3-killers.svg", s)


# ── Рис. 10.4.5.4 — глибина розряду vs ресурс ────────────────────────────────
def fig_dod_cycles():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Глибина розряду вирішує: мілкі цикли живуть довше", 18, INK, "middle", "bold")
    bars = [("100% DoD", "~500", 500, RED), ("80% DoD", "~1000", 1000, AMBER),
            ("50% DoD", "~3000", 3000, GREEN), ("20% DoD", "~10000+", 10000, BLUE)]
    x0, y0 = 130, 320
    bw, gap, maxv, ph = 120, 70, 10000, 230
    s += line(x0, y0, W - 60, y0, INK, 1.6)
    s += line(x0, y0, x0, y0 - ph, INK, 1.6)
    s += text(x0 - 8, y0 - ph - 4, "циклів", 9, INK, "end", "bold")
    for i, (name, lab, v, c) in enumerate(bars):
        x = x0 + 50 + i * (bw + gap)
        h = min(v, maxv) / maxv * ph
        s += rect(x, y0 - h, bw, h, "#fff", c, 2, 5)
        s += f'<rect x="{x:.0f}" y="{y0-h:.0f}" width="{bw}" height="{h:.0f}" rx="5" fill="{c}" fill-opacity="0.16"/>\n'
        s += text(x + bw / 2, y0 - h - 8, lab, 11, c, "middle", "bold")
        s += text(x + bw / 2, y0 + 18, name, 9.5, c, "middle", "bold")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 26, "Розряджати на півглибини замість «у нуль» — і та сама батарея витримає в рази більше циклів. Звідси прийом:", 9.5, INK, "middle")
    s += text(W / 2, H - 11, "навмисне користуватися лише СЕРЕДИНОЮ заряду (напр. 20–80%), жертвуючи частиною ємності заради довшого життя.", 9.5, INK, "middle")
    save("fig-10-5-4-dod.svg", s)


# ── Рис. 10.4.5.5 — зберігання: заряд × температура ──────────────────────────
def fig_storage_grid():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Зберігання: заряд × температура → швидкість старіння", 17, INK, "middle", "bold")
    socs = ["100% (повна)", "~50% (краще)", "низька"]
    temps = ["прохолодно", "тепло", "спека"]
    rates = [[1, 2, 3], [0, 1, 2], [1, 1, 2]]
    cols = {0: "#dff0e1", 1: "#f3ecdf", 2: "#fbe2db", 3: "#f6c9c0"}
    labs = ["повільно", "помірно", "швидко", "найшвидше"]
    gx, gy, cw, chh = 330, 88, 175, 64
    for j, t in enumerate(temps):
        s += text(gx + cw / 2 + j * cw, gy - 8, t, 10, INK, "middle", "bold")
    for i, soc in enumerate(socs):
        s += text(gx - 10, gy + chh / 2 + i * chh + 4, soc, 9.5, INK, "end", "bold")
        for j in range(3):
            r = rates[i][j]
            s += rect(gx + j * cw, gy + i * chh, cw, chh, cols[r], GREY, 1, 6)
            s += text(gx + j * cw + cw / 2, gy + i * chh + chh / 2 + 4, labs[r], 9.5, INK, "middle", "bold")
    s += rect(70, H - 66, W - 140, 52, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 46, "Найкраще для довгого зберігання — НАПОЛОВИНУ заряджена й ПРОХОЛОДНА комірка. Найгірше — повна й гаряча.", 9.5, INK, "middle")
    s += text(W / 2, H - 30, "Тому пристрої «на полицю» лишають десь на 50% (3.7–3.8 В), а не повними, і не тримають у спеці.", 9.5, INK, "middle")
    s += text(W / 2, H - 14, "(Дуже низький заряд при зберіганні теж погано — комірка може впасти нижче безпечного й померти.)", 9, GREY, "middle")
    save("fig-10-5-5-storage.svg", s)


# ── Рис. 10.4.5.6 — проєктувати під деградацію ───────────────────────────────
def fig_design_for_aging():
    W, H = 940, 410
    s = header(W, H)
    s += text(W / 2, 32, "Проєктувати «під деградацію»", 18, INK, "middle", "bold")
    s += text(200, 70, "Користуватися СЕРЕДИНОЮ", 11, INK, "middle", "bold")
    bx, by, bw2, bh = 140, 90, 120, 200
    s += rect(bx, by, bw2, bh, "#f6f6f6", GREY, 1.5, 8)
    s += f'<rect x="{bx}" y="{by}" width="{bw2}" height="40" fill="#fbe2db"/>\n'
    s += text(bx + bw2 / 2, by + 24, "не до 100%", 9, RED, "middle", "bold")
    s += f'<rect x="{bx}" y="{by+40}" width="{bw2}" height="110" fill="#dff0e1"/>\n'
    s += text(bx + bw2 / 2, by + 92, "робоче вікно", 9.5, GREEN, "middle", "bold")
    s += text(bx + bw2 / 2, by + 109, "(напр. 20–80%)", 8.5, INK, "middle")
    s += f'<rect x="{bx}" y="{by+150}" width="{bw2}" height="50" fill="#fbe2db"/>\n'
    s += text(bx + bw2 / 2, by + 178, "не в нуль", 9, RED, "middle", "bold")
    s += rect(330, 76, 560, 230, "#f6f6f6", GREY, 1.4, 10)
    s += text(610, 102, "Шість ходів довговічності", 12, INK, "middle", "bold")
    items = [
        "Бери батарею БІЛЬШУ: щоб і на 80% EoL вистачало",
        "Заряджай нижче (4.1 В) — життя в рази довше",
        "Циклюй серединою, не «0–100%»",
        "Тримай прохолодно; уникай «спека + повна»",
        "Зберігай на ~50%, не повною",
        "Передбач ЗАМІНУ батареї в конструкції",
    ]
    for i, t in enumerate(items):
        s += text(348, 130 + i * 27, "• " + t, 10, INK, "start")
    s += rect(70, H - 40, W - 140, 28, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 22, "Деградація неминуча — її ПЛАНУЮТЬ: запас ємності на кінець життя, лагідний режим і можливість замінити батарею.", 9.5, INK, "middle")
    s += text(W / 2, H - 8, "Здоров'я (SoH) тим часом стежать за двома знаками: спад ємності (паливомір) і зростання Rвн.", 9.5, INK, "middle")
    save("fig-10-5-6-design.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 10.4.6 — Захист і BMS
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 10.4.6.1 — навіщо захист ────────────────────────────────────────────
def fig_why_protect():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Захист батареї: останній рубіж проти чотирьох загроз", 17, INK, "middle", "bold")
    s += rect(390, 152, 160, 90, "#eef8ef", GREEN, 2, 12)
    s += text(470, 184, "комірка", 11, GREEN, "middle", "bold")
    s += text(470, 204, "+ ЗАХИСТ", 11, RED, "middle", "bold")
    s += text(470, 222, "(відрубує на межі)", 8.5, INK, "middle")
    threats = [
        ("Перезаряд", "OVP: V > ~4.3 В → пожежа", RED, 70, 92),
        ("Переразряд", "UVP: V < ~2.5 В → смерть", BLUE, 660, 92),
        ("Надструм", "OCP: забагато ампер", AMBER, 70, 288),
        ("Коротке замикання", "SCP: миттєвий обрив", "#9b59b6", 660, 288),
    ]
    for title, body, c, x, y in threats:
        s += rect(x, y, 210, 70, "#ffffff", c, 1.8, 10)
        s += text(x + 105, y + 27, title, 11, c, "middle", "bold")
        s += text(x + 105, y + 49, body, 9, INK, "middle")
    s += arrow(280, 127, 388, 176, GREY, 1.6)
    s += arrow(660, 127, 552, 176, GREY, 1.6)
    s += arrow(280, 323, 388, 218, GREY, 1.6)
    s += arrow(660, 323, 552, 218, GREY, 1.6)
    s += rect(70, H - 44, W - 140, 32, "#fbe9e7", RED, 1.4, 9)
    s += text(W / 2, H - 26, "Літій нещадний: перезаряд — пожежа, переразряд — смерть комірки, надструм і КЗ — перегрів. Захист стежить за межами", 9.5, INK, "middle")
    s += text(W / 2, H - 11, "й АВАРІЙНО відрубує комірку, коли щось пішло не так. Це не зарядник — це останній рубіж, що рятує, коли решта відмовила.", 9.5, INK, "middle")
    save("fig-10-6-1-why.svg", s)


# ── Рис. 10.4.6.2 — захисна плата ────────────────────────────────────────────
def fig_protection_board():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Захисна плата за долар: чип + два MOSFET", 18, INK, "middle", "bold")
    s += rect(60, 150, 110, 80, "#eef8ef", GREEN, 1.8, 10)
    s += text(115, 182, "комірка", 10.5, GREEN, "middle", "bold")
    s += text(115, 200, "Li 1S", 8.5, INK, "middle")
    s += line(170, 165, 800, 165, RED, 2.4)
    s += text(150, 159, "B+", 8.5, RED, "end")
    s += line(170, 215, 360, 215, INK, 2)
    s += rect(360, 198, 60, 34, "#fff7e6", AMBER, 1.8, 6)
    s += text(390, 219, "FET1", 8.5, AMBER, "middle", "bold")
    s += rect(440, 198, 60, 34, "#fff7e6", AMBER, 1.8, 6)
    s += text(470, 219, "FET2", 8.5, AMBER, "middle", "bold")
    s += line(420, 215, 440, 215, INK, 2)
    s += line(500, 215, 800, 215, INK, 2)
    s += text(390, 248, "заряд", 8, INK, "middle")
    s += text(470, 248, "розряд", 8, INK, "middle")
    s += text(150, 220, "B−", 8.5, INK, "end")
    s += rect(360, 282, 140, 70, "#eef3fb", BLUE, 1.8, 10)
    s += text(430, 308, "захисний чип", 9.5, BLUE, "middle", "bold")
    s += text(430, 326, "DW01-клас", 8.5, INK, "middle")
    s += text(430, 342, "стежить V та I", 8, GREY, "middle")
    s += line(115, 230, 115, 367, INK, 1.2, dash="3,3")
    s += line(115, 367, 360, 367, INK, 1.2, dash="3,3")
    s += text(235, 380, "міряє напругу комірки", 8, INK, "middle")
    s += line(390, 282, 390, 232, GREEN, 1.6)
    s += line(470, 282, 470, 232, GREEN, 1.6)
    s += text(430, 272, "керує затворами", 8, GREEN, "middle", "bold")
    s += circle(800, 165, 4, RED, RED, 0)
    s += text(810, 160, "P+", 9, RED, "start", "bold")
    s += circle(800, 215, 4, INK, INK, 0)
    s += text(810, 219, "P−", 9, INK, "start", "bold")
    s += text(800, 132, "до пристрою / зарядки", 8.5, GREY, "middle")
    s += rect(70, H - 30, W - 140, 20, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "Два послідовні MOSFET у мінусовій лінії — окремий для заряду й для розряду; чип міряє напругу й струм і РОЗМИКАЄ їх на аварії.", 9.2, INK, "middle")
    save("fig-10-6-2-board.svg", s)


# ── Рис. 10.4.6.3 — пороги захисту ───────────────────────────────────────────
def fig_thresholds():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Пороги захисту: вікно, поза яким відрубує", 18, INK, "middle", "bold")
    cx, ytop, ybot = 300, 80, 320

    def vy(v):
        return ybot - (v - 2.0) / (4.6 - 2.0) * (ybot - ytop)

    s += f'<rect x="{cx-60}" y="{ytop}" width="120" height="{vy(4.25)-ytop:.0f}" fill="#fbe2db"/>\n'
    s += text(cx, ytop + 18, "OVP: відрубити ЗАРЯД", 9, RED, "middle", "bold")
    s += f'<rect x="{cx-60}" y="{vy(4.25):.0f}" width="120" height="{vy(2.5)-vy(4.25):.0f}" fill="#dff0e1"/>\n'
    s += text(cx, vy(3.4), "робоче вікно", 10, GREEN, "middle", "bold")
    s += text(cx, vy(3.4) + 16, "2.5–4.2 В", 9, INK, "middle")
    s += f'<rect x="{cx-60}" y="{vy(2.5):.0f}" width="120" height="{ybot-vy(2.5):.0f}" fill="#e7ecf5"/>\n'
    s += text(cx, ybot - 14, "UVP: відрубити РОЗРЯД", 9, BLUE, "middle", "bold")
    s += rect(cx - 60, ytop, 120, ybot - ytop, "none", GREY, 1.2)
    s += text(cx - 70, vy(4.3) - 2, "OVP ≈ 4.3", 8, RED, "end", "bold")
    s += text(cx - 70, vy(2.5) + 12, "UVP ≈ 2.5", 8, BLUE, "end", "bold")
    s += rect(540, 110, 350, 180, "#f6f6f6", GREY, 1.4, 10)
    s += text(715, 136, "А ще — за струмом і теплом", 11, INK, "middle", "bold")
    rows = [("OCP — надструм", "забагато ампер довго → відрубити"),
            ("SCP — коротке", "миттєвий стрибок → відрубити вмить"),
            ("гістерезис", "вмикає назад лише після відновлення"),
            ("OTP — перегрів", "є у складніших платах")]
    for i, (t, d) in enumerate(rows):
        s += text(560, 166 + i * 30, "• " + t, 10, INK, "start", "bold")
        s += text(577, 180 + i * 30, d, 8.5, GREY, "start")
    s += rect(70, H - 30, W - 140, 20, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "Захист має вікно за напругою (OVP/UVP) і за струмом (OCP/SCP); вийшов за межі — комірку від'єднано. Вмикає назад із гістерезисом.", 9, INK, "middle")
    save("fig-10-6-3-thresholds.svg", s)


# ── Рис. 10.4.6.4 — балансування ─────────────────────────────────────────────
def fig_balancing():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Балансування: пасивне проти активного", 18, INK, "middle", "bold")
    cells = [("4.20", 1), ("4.15", 0), ("4.10", 0)]
    s += rect(50, 70, 400, 260, "#fbf7ec", AMBER, 1.6, 12)
    s += text(250, 94, "Пасивне: зливати надлишок", 12, AMBER, "middle", "bold")
    for i, (v, full) in enumerate(cells):
        y = 120 + i * 60
        s += rect(120, y, 90, 44, "#eef8ef", GREEN, 1.8, 8)
        s += text(165, y + 20, "комірка", 8.5, INK, "middle")
        s += text(165, y + 36, v + " В", 10, GREEN, "middle", "bold")
        if full:
            s += _res(240, y + 8, 50, 28, "R", RED)
            s += text(330, y + 26, "← зливає тепло", 9, RED, "start", "bold")
    s += text(250, 314, "просто, дешево — та енергію палимо в тепло", 9, INK, "middle")
    s += rect(490, 70, 400, 260, "#eef8ef", GREEN, 1.6, 12)
    s += text(690, 94, "Активне: переливати заряд", 12, GREEN, "middle", "bold")
    for i, (v, full) in enumerate(cells):
        y = 120 + i * 60
        s += rect(560, y, 90, 44, "#eef8ef", GREEN, 1.8, 8)
        s += text(605, y + 20, "комірка", 8.5, INK, "middle")
        s += text(605, y + 36, v + " В", 10, GREEN, "middle", "bold")
    s += arrow(660, 142, 660, 200, BLUE, 2)
    s += text(700, 172, "переливає заряд", 9, BLUE, "start", "bold")
    s += text(700, 188, "з повної в порожнішу", 8.5, INK, "start")
    s += text(690, 314, "ефективно — та складно й дорого", 9, INK, "middle")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 26, "У послідовній збірці комірки дрейфують; балансування їх вирівнює. Пасивне зливає зайве з повніших у тепло (просто).", 9.2, INK, "middle")
    s += text(W / 2, H - 11, "Активне переносить заряд із повних у порожніші (ефективно, та складніше). Без балансування пакет старіє швидше й недодає ємності.", 9.2, INK, "middle")
    save("fig-10-6-4-balancing.svg", s)


# ── Рис. 10.4.6.5 — найслабша комірка ────────────────────────────────────────
def fig_weakest_cell():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Найслабша комірка диктує обидва краї", 18, INK, "middle", "bold")
    caps = [(100, "повна"), (100, ""), (85, "слабша"), (100, "")]
    x0, cw, cy, chh = 130, 165, 108, 130
    s += text(W / 2, cy - 10, "послідовна збірка (наприклад 4S)", 10, INK, "middle")
    for i, (cap, lab) in enumerate(caps):
        x = x0 + i * cw
        s += rect(x, cy, 110, chh, "#f0f0f0", GREY, 1.4, 8)
        h = cap / 100 * (chh - 10)
        c = RED if cap < 100 else GREEN
        s += f'<rect x="{x+5}" y="{cy+chh-5-h:.0f}" width="100" height="{h:.0f}" rx="4" fill="{c}" fill-opacity="0.3" stroke="{c}" stroke-width="1.5"/>\n'
        s += text(x + 55, cy + chh + 16, f"{cap}%", 10, c, "middle", "bold")
        if lab:
            s += text(x + 55, cy + chh + 32, lab, 9, c, "middle", "bold")
        if i < 3:
            s += text(x + 137, cy + chh / 2, "+", 16, INK, "middle", "bold")
    s += rect(70, 286, W - 140, 96, "#fbe9e7", RED, 1.5, 10)
    s += text(W / 2, 308, "На ЗАРЯДІ слабша перша впирається в OVP → решта не добирають → пакет не дозаряджається.", 10, INK, "middle")
    s += text(W / 2, 330, "На РОЗРЯДІ вона ж перша впирається в UVP → пакет зупиняється, хоч у сильніших ще є заряд.", 10, INK, "middle")
    s += text(W / 2, 354, "Корисна ємність пакета = найслабша комірка. Балансування й добір однакових комірок це лікують.", 10, RED, "middle", "bold")
    save("fig-10-6-5-weakest.svg", s)


# ── Рис. 10.4.6.6 — спектр захисту ───────────────────────────────────────────
def fig_spectrum():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Спектр захисту: від плати за долар до повної BMS", 18, INK, "middle", "bold")
    steps = [
        ("Захисна плата", "1S, одна комірка", "OVP/UVP/OCP/SCP|чип + 2 FET ($1)", GREEN, 50),
        ("Захист + баланс", "кілька комірок (nS)", "+ балансування|+ моніторинг комірок", AMBER, 350),
        ("Повна BMS", "великі пакети", "+ SoC/SoH, зв'язок,|тепловий режим", RED, 650),
    ]
    for title, sub, body, c, x in steps:
        s += rect(x, 80, 240, 180, "#ffffff", c, 2, 12)
        s += text(x + 120, 108, title, 12.5, c, "middle", "bold")
        s += text(x + 120, 128, sub, 9, GREY, "middle", style="italic")
        s += line(x + 20, 140, x + 220, 140, FAINT, 1)
        for j, ln in enumerate(body.split("|")):
            s += text(x + 120, 166 + j * 20, ln, 9.5, INK, "middle")
    s += arrow(290, 170, 348, 170, INK, 2)
    s += arrow(590, 170, 648, 170, INK, 2)
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 26, "Мінімум для БУДЬ-ЯКОГО літію — захисна плата (часто вже в комірці). Кілька комірок послідовно — додається балансування.", 9.2, INK, "middle")
    s += text(W / 2, H - 11, "Великі пакети (транспорт, накопичувачі) — повноцінна BMS з моніторингом, зв'язком і тепловим керуванням. Чим більше — тим складніше.", 9.2, INK, "middle")
    save("fig-10-6-6-spectrum.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 10.4.7 — Механіка і безпека
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 10.4.7.1 — батарея як фізичний об'єкт ───────────────────────────────
def fig_battery_object():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Батарея — це ще й фізичний об'єкт", 18, INK, "middle", "bold")
    s += rect(410, 165, 120, 90, "#eef8ef", GREEN, 2, 10)
    s += rect(455, 152, 30, 14, "#eef8ef", GREEN, 2, 4)
    s += text(470, 215, "комірка", 10.5, GREEN, "middle", "bold")
    concerns = [
        ("Має вагу й об'єм", "тримати, не навантажувати виводи", BLUE, 70, 95),
        ("Надувається", "лишити місце на роздуття", RED, 660, 95),
        ("Проколюється / тисне", "захист від механіки → інакше пожежа", AMBER, 70, 285),
        ("Потребує конектора", "полярність, струм, не закоротити", "#9b59b6", 660, 285),
    ]
    for title, body, c, x, y in concerns:
        s += rect(x, y, 210, 66, "#ffffff", c, 1.8, 10)
        s += text(x + 105, y + 26, title, 10.8, c, "middle", "bold")
        s += text(x + 105, y + 47, body, 8.6, INK, "middle")
    s += arrow(280, 128, 408, 178, GREY, 1.5)
    s += arrow(660, 128, 532, 178, GREY, 1.5)
    s += arrow(280, 318, 408, 242, GREY, 1.5)
    s += arrow(660, 318, 532, 242, GREY, 1.5)
    s += rect(70, H - 30, W - 140, 20, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "Електрика — лише половина справи. Батарея масивна, здатна надутись, боїться проколу й тиску, і її треба надійно тримати та під'єднувати.", 9, INK, "middle")
    save("fig-10-7-1-object.svg", s)


# ── Рис. 10.4.7.2 — тримачі ──────────────────────────────────────────────────
def fig_holders():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Як тримати: три форм-фактори, три підходи", 18, INK, "middle", "bold")
    cards = [
        ("Циліндрична", "(18650-клас)",
         ["пружинний тримач: просто,", "  але контакт гірший (Rвн↑),", "  може розхитатись", "приварені вивідні: надійно,", "  та складніше в монтажі"], BLUE, 50),
        ("Пакетна (LiPo)", "м'яка, без корпусу",
         ["захистити від проколу й тиску", "не навантажувати виводи", "  й тонкі дроти", "лишити МІСЦЕ на роздуття", "  (не затискати намертво)"], AMBER, 350),
        ("Монетна", "(coin / button)",
         ["тримач із пружним контактом", "пильнувати полярність", "малі струми — менше турбот", "часто припаюють із", "  «пелюстками» (tabs)"], GREEN, 650),
    ]
    for title, sub, rows, c, x in cards:
        s += rect(x, 70, 240, 250, "#ffffff", c, 2, 12)
        s += text(x + 120, 96, title, 12.5, c, "middle", "bold")
        s += text(x + 120, 114, sub, 9, GREY, "middle", style="italic")
        s += line(x + 20, 124, x + 220, 124, FAINT, 1)
        for j, r in enumerate(rows):
            pre = "   " if r.startswith("  ") else "• "
            s += text(x + 22, 146 + j * 19, pre + r.strip(), 8.7, INK, "start")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 26, "Кожен форм-фактор має свій спосіб тримання — і свою головну небезпеку: циліндр розхитується, пакет проколюється", 9.2, INK, "middle")
    s += text(W / 2, H - 11, "й надувається, монета любить переплутану полярність. Спільне: контакт надійний, а виводи — без механічного навантаження.", 9.2, INK, "middle")
    save("fig-10-7-2-holders.svg", s)


# ── Рис. 10.4.7.3 — конектори ────────────────────────────────────────────────
def fig_connectors():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Конектори: полярність, струм, коротке", 18, INK, "middle", "bold")
    cards = [
        ("Полярність", "ключований роз'єм —|не вставиш навпаки", "переполюсування губить|пристрій (тема 10.4.6)", RED, 50),
        ("Струм за ПІКОМ", "тонкий роз'єм гріється|й просідає (10.4.2/10.3.7)", "добирати під пік,|не під середнє", AMBER, 350),
        ("Не закоротити", "голі виводи на викрутці —|класична пожежа LiPo", "ізолювати, під'єднувати|обережно", "#9b59b6", 650),
    ]
    for title, l1, l2, c, x in cards:
        s += rect(x, 76, 240, 180, "#ffffff", c, 2, 12)
        s += text(x + 120, 104, title, 12.5, c, "middle", "bold")
        s += line(x + 20, 116, x + 220, 116, FAINT, 1)
        for j, ln in enumerate(l1.split("|")):
            s += text(x + 120, 142 + j * 18, ln, 9.2, INK, "middle")
        for j, ln in enumerate(l2.split("|")):
            s += text(x + 120, 196 + j * 16, ln, 8.6, GREY, "middle")
    s += rect(70, H - 58, W - 140, 46, "#fbe9e7", RED, 1.4, 9)
    s += text(W / 2, H - 40, "Три правила конектора: ключований (щоб не переплутати +/−), на повний ПІКОВИЙ струм (інакше гарячий вузол і просадка),", 9.2, INK, "middle")
    s += text(W / 2, H - 25, "і ніколи не лишати голих виводів, що можуть закоротити об метал. Коротке на батареї — це миттєвий жар і ризик займання.", 9.2, INK, "middle")
    s += text(W / 2, H - 10, "Приклад: пристрій із піком 3 А на роз'ємі, розрахованому на 2 А, з часом перегріє й сам роз'єм, і контакти.", 8.6, GREY, "middle")
    save("fig-10-7-3-connectors.svg", s)


# ── Рис. 10.4.7.4 — надутий LiPo ─────────────────────────────────────────────
def fig_swelling():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 32, "Надутий LiPo: попередження, яке не можна ігнорувати", 17, INK, "middle", "bold")
    s += rect(90, 92, 150, 64, "#eef8ef", GREEN, 2, 8)
    s += text(165, 122, "нормальний", 10, GREEN, "middle", "bold")
    s += text(165, 140, "плаский", 9, INK, "middle")
    s += arrow(250, 124, 308, 124, RED, 2.4)
    s += text(280, 113, "газ", 8.5, RED, "middle", "bold")
    s += f'<ellipse cx="400" cy="124" rx="80" ry="46" fill="#fbe2db" stroke="{RED}" stroke-width="2"/>\n'
    s += text(400, 120, "НАДУТИЙ", 10.5, RED, "middle", "bold")
    s += text(400, 138, "(газ усередині)", 8, INK, "middle")
    s += text(400, 188, "= комірку пошкоджено", 9.5, RED, "middle", "bold")
    s += rect(530, 84, 360, 100, "#f6f6f6", GREY, 1.4, 10)
    s += text(710, 108, "Чому надувається", 11, INK, "middle", "bold")
    s += text(548, 130, "розклад електроліту → газ:", 9, INK, "start")
    s += text(562, 146, "перезаряд, перегрів, прокол,", 8.7, GREY, "start")
    s += text(562, 160, "глибокий розряд, старість (10.4.5)", 8.7, GREY, "start")
    s += text(548, 178, "це знак ушкодження, не «втоми»", 9, RED, "start", "bold")
    s += rect(70, 218, W - 140, 112, "#fbe9e7", RED, 1.6, 10)
    s += text(W / 2, 242, "Що робити з надутою коміркою", 12, RED, "middle", "bold")
    dos = [
        "1. НЕГАЙНО припинити заряд і використання",
        "2. Ізолювати: вогнетривка ємність / пісок / надвір, подалі від горючого",
        "3. НЕ проколювати, не тиснути, не «здувати» — газ горючий, прокол = займання",
        "4. Здати на утилізацію батарей; не в смітник",
    ]
    for i, t in enumerate(dos):
        s += text(110, 270 + i * 16, t, 9.5, INK, "start")
    s += rect(70, H - 30, W - 140, 20, "#fff7e6", AMBER, 1.4, 8)
    s += text(W / 2, H - 15, "І на майбутнє: у корпусі ЛИШАЮТЬ місце на роздуття — затиснутий намертво пакет, надуваючись, тисне на все довкола.", 9, INK, "middle")
    save("fig-10-7-4-swelling.svg", s)


# ── Рис. 10.4.7.5 — поведінка при відмові ────────────────────────────────────
def fig_fail_safe():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Поведінка при відмові: проєктувати на «безпечно згоріти»", 17, INK, "middle", "bold")
    seq = [("ушкодження /", "перегрів", AMBER, 80), ("вихід газу", "(venting)", RED, 290),
           ("тепловий", "розгін", RED, 500), ("займання", "/ каскад", "#9b59b6", 710)]
    for a, b, c, x in seq:
        s += rect(x, 80, 150, 56, "#ffffff", c, 1.8, 8)
        s += text(x + 75, 104, a, 9.5, c, "middle", "bold")
        s += text(x + 75, 120, b, 9.5, c, "middle", "bold")
        if x < 710:
            s += arrow(x + 150, 108, x + 205, 108, INK, 2)
    s += text(W / 2, 160, "Завдання конструкції — РОЗІРВАТИ цей ланцюг або хоча б локалізувати наслідки:", 10, INK, "middle", "bold")
    moves = [
        ("Шлях для газу", "вентиляція, а не герметичний короб під тиском", GREEN),
        ("Розділяти комірки", "щоб розгін однієї не підпалив сусідні", BLUE),
        ("Без горючого поруч", "жодного палива впритул до комірки", AMBER),
        ("Не затискати", "тиск на надуту комірку — прискорювач", RED),
    ]
    for i, (t, d, c) in enumerate(moves):
        y = 184 + i * 42
        s += rect(80, y, 22, 22, c, c, 0, 4)
        s += text(116, y + 11, t, 10.5, c, "start", "bold")
        s += text(116, y + 27, d, 9, INK, "start")
    s += rect(70, H - 30, W - 140, 20, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "Відмова однієї комірки не має ставати катастрофою: дати газу вийти, розвести комірки, прибрати горюче — щоб «згоріло безпечно».", 9, INK, "middle")
    save("fig-10-7-5-failsafe.svg", s)


# ── Рис. 10.4.7.6 — зберігання, транспорт, утилізація ────────────────────────
def fig_storage_transport():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Зберігання, перевезення, утилізація", 18, INK, "middle", "bold")
    cards = [
        ("Зберігати", ["~50% заряду, прохолодно (10.4.5)", "у вогнетривкій ємності", "ПОДАЛІ від металу (монети,", "  ключі = коротке!)"], GREEN, 50),
        ("Перевозити", ["низький заряд (часто ~30%)", "межі за ват-годинами", "авіа — суворі правила,", "  пошкоджені — заборонені"], AMBER, 350),
        ("Утилізувати", ["НІКОЛИ не в смітник", "  (пожежа у відходах)", "здавати в пункти прийому", "надуті/биті — тим паче"], RED, 650),
    ]
    for title, rows, c, x in cards:
        s += rect(x, 76, 240, 200, "#ffffff", c, 2, 12)
        s += text(x + 120, 104, title, 13, c, "middle", "bold")
        s += line(x + 20, 116, x + 220, 116, FAINT, 1)
        for j, r in enumerate(rows):
            pre = "   " if r.startswith("  ") else "• "
            s += text(x + 22, 142 + j * 24, pre + r.strip(), 9.2, INK, "start")
    s += rect(70, H - 58, W - 140, 46, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 40, "Літій небезпечний і поза пристроєм: зберігати напівзарядженим, прохолодним і подалі від металу, що може закоротити виводи;", 9.2, INK, "middle")
    s += text(W / 2, H - 25, "перевозити з низьким зарядом і в межах правил (надто авіа); а наприкінці — здавати на утилізацію, бо в смітнику літій горить.", 9.2, INK, "middle")
    s += text(W / 2, H - 10, "Це не бюрократія, а та сама фізика: заряджений літій — це запас енергії, що за коротким чи проколом виходить теплом.", 8.6, GREY, "middle")
    save("fig-10-7-6-storage.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Вставка 🧮 (до теми 10.4.2) — Просадка з Rвн і C-rate
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 10.4.2m.1 — ΔV від C-rate ───────────────────────────────────────────
def fig_sag_vs_crate():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "Просадка від C-rate: ΔV = (C·Q)·Rвн", 18, INK, "middle", "bold")
    x0, y0 = 100, 330
    pw, ph = 680, 250
    s += line(x0, y0, x0 + pw, y0, INK, 1.5)
    s += line(x0, y0, x0, y0 - ph, INK, 1.5)
    s += text(x0 - 9, y0 - ph - 2, "ΔV, В", 9, INK, "end", "bold")
    s += text(x0 + pw, y0 + 18, "C-rate →", 9, INK, "end")
    Q, cmax, vmax = 1.5, 5, 1.0
    for c in [1, 2, 3, 4, 5]:
        xx = x0 + c / cmax * pw
        s += line(xx, y0, xx, y0 + 5, INK, 1)
        s += text(xx, y0 + 18, f"{c}C", 9, GREY, "middle")
    for v in [0.2, 0.4, 0.6, 0.8, 1.0]:
        yy = y0 - v / vmax * ph
        s += line(x0 - 5, yy, x0, yy, INK, 1)
        s += text(x0 - 9, yy + 4, f"{v}", 8.5, GREY, "end")
    allowed = 0.6
    s += line(x0, y0 - allowed / vmax * ph, x0 + pw, y0 - allowed / vmax * ph, RED, 1.6, dash="6,4")
    s += text(x0 + pw - 4, y0 - allowed / vmax * ph - 6, "межа ΔV = OCV − brownout = 0.6 В", 8.5, RED, "end", "bold")
    for rin, c, lab in [(0.1, GREEN, "Rвн=0.1 Ом"), (0.2, BLUE, "Rвн=0.2 Ом"), (0.4, AMBER, "Rвн=0.4 Ом")]:
        cr_v = vmax / (Q * rin)
        cr_end = min(cmax, cr_v)
        dv_end = cr_end * Q * rin
        s += poly([(x0, y0), (x0 + cr_end / cmax * pw, y0 - dv_end / vmax * ph)], c, 2.6)
        s += text(x0 + cr_end / cmax * pw, y0 - dv_end / vmax * ph - 6, lab, 8.5, c, "middle", "bold")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 26, "Для комірки 1.5 А·год: 2C = 3 А. Чим більший Rвн, тим крутіша лінія — і тим меншу C-rate можна тягнути, не пробивши межу.", 9.2, INK, "middle")
    s += text(W / 2, H - 11, "Перетин лінії з межею ΔV дає максимальну допустиму C-rate: при Rвн=0.1 це ~4C, при 0.2 — ~2C, при 0.4 — лише ~1C.", 9.2, INK, "middle")
    save("fig-10-2m1-sag.svg", s)


# ── Рис. 10.4.2m.2 — бюджет до brownout ──────────────────────────────────────
def fig_sag_margin():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 32, "Бюджет напруги: просадка з'їдає запас до brownout", 17, INK, "middle", "bold")
    y0, ph, vmax = 330, 250, 4.0

    def vy(v):
        return y0 - v / vmax * ph

    def col(x, rin, label):
        ocv, bo, I = 3.6, 3.0, 2.0
        dv = I * rin
        term = ocv - dv
        o = f'<rect x="{x-40}" y="{vy(ocv):.0f}" width="80" height="{y0-vy(ocv):.0f}" fill="#eef8ef" stroke="{GREEN}" stroke-width="1.4"/>\n'
        o += f'<rect x="{x-40}" y="{vy(ocv):.0f}" width="80" height="{vy(term)-vy(ocv):.0f}" fill="#fbe2db" stroke="{RED}" stroke-width="1"/>\n'
        o += text(x, vy((ocv + term) / 2) + 3, f"ΔV={dv:.1f}", 8.5, RED, "middle", "bold")
        o += line(x - 40, vy(term), x + 40, vy(term), INK, 2)
        o += text(x, vy(term) - 4, f"{term:.1f} В", 9.5, INK, "middle", "bold")
        o += line(x - 46, vy(bo), x + 46, vy(bo), "#9b59b6", 1.6, dash="5,3")
        o += text(x, y0 + 18, label, 9.5, INK, "middle", "bold")
        ok = term > bo
        o += text(x, y0 + 34, "ЗАПАС OK" if ok else "НИЖЧЕ — ресет!", 9.5, GREEN if ok else RED, "middle", "bold")
        return o

    s += col(300, 0.1, "Rвн=0.1 Ом (свіжа, тепла)")
    s += col(640, 0.4, "Rвн=0.4 Ом (холод/старість)")
    s += text(120, vy(3.6) + 4, "OCV 3.6 В", 9, GREEN, "start", "bold")
    s += text(120, vy(3.0) + 4, "brownout 3.0 В", 9, "#9b59b6", "start", "bold")
    s += line(150, vy(3.6), 254, vy(3.6), FAINT, 1, dash="3,3")
    s += line(150, vy(3.0), 254, vy(3.0), FAINT, 1, dash="3,3")
    s += rect(70, H - 30, W - 140, 20, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "Той самий пік 2 А: при Rвн=0.1 Ом на клемах лишається 3.4 В (запас є), при 0.4 Ом — 2.8 В, нижче brownout 3.0 В → ресет.", 9, INK, "middle")
    save("fig-10-2m2-margin.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Вставка 🔌 (до теми 10.4.3) — Зарядник TP4056-класу
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 10.4.3c.1 — плата TP4056 ────────────────────────────────────────────
def fig_tp4056():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Зарядна плата TP4056-класу: один резистор задає струм", 17, INK, "middle", "bold")
    s += rect(50, 150, 100, 60, "#fbe9e7", RED, 1.8, 10)
    s += text(100, 175, "USB 5 В", 10, RED, "middle", "bold")
    s += text(100, 193, "(вхід)", 8.5, INK, "middle")
    s += arrow(150, 180, 228, 180, RED, 2.4)
    s += text(190, 172, "VCC", 8.5, RED, "middle", "bold")
    s += rect(230, 120, 200, 150, "#eef8ef", GREEN, 2, 12)
    s += text(330, 146, "TP4056-клас", 12, GREEN, "middle", "bold")
    s += text(330, 163, "лінійний CC/CV", 9, INK, "middle")
    s += text(330, 179, "до 4.2 В, автономно", 8.5, GREY, "middle")
    s += arrow(430, 180, 508, 180, RED, 2.4)
    s += text(470, 172, "BAT", 8.5, RED, "middle", "bold")
    s += rect(510, 150, 100, 60, "#eef8ef", GREEN, 1.8, 10)
    s += text(560, 175, "комірка", 10, GREEN, "middle", "bold")
    s += text(560, 193, "Li 1S", 8.5, INK, "middle")
    s += line(290, 270, 290, 318, INK, 1.6)
    s += _res(265, 318, 50, 28, "Rprog", BLUE)
    s += line(290, 346, 290, 360, INK, 1.6)
    s += line(278, 360, 302, 360, INK, 2)
    s += text(330, 332, "Rprog задає струм CC:", 8.8, BLUE, "start", "bold")
    s += text(330, 346, "Iзар ≈ 1200 / Rprog  (1.2к→1 А, 2к→0.6 А)", 8.8, INK, "start")
    s += line(370, 120, 370, 90, AMBER, 1.6)
    s += circle(370, 84, 6, "#fff", AMBER, 1.8)
    s += text(370, 72, "CHRG", 7.5, AMBER, "middle", "bold")
    s += line(400, 120, 400, 90, GREEN, 1.6)
    s += circle(400, 84, 6, "#fff", GREEN, 1.8)
    s += text(402, 72, "STDBY", 7.5, GREEN, "middle", "bold")
    s += text(385, 58, "світлодіоди: заряд / готово", 8, GREY, "middle")
    s += line(250, 270, 250, 300, AMBER, 1.4, dash="3,3")
    s += text(182, 302, "TEMP → термістор (опц.)", 8, AMBER, "end")
    s += line(560, 210, 560, 250, INK, 1.4)
    s += arrow(560, 250, 678, 250, BLUE, 2)
    s += rect(680, 230, 120, 44, "#eef3fb", BLUE, 1.6, 8)
    s += text(740, 250, "система", 9.5, BLUE, "middle", "bold")
    s += text(740, 266, "(тягне з BAT!)", 8, RED, "middle")
    s += text(615, 224, "класична плата: OUT ≈ BAT", 8, RED, "start", "bold")
    s += rect(470, 296, 250, 40, "none", GREY, 1.4, 8)
    s += text(595, 312, "DW01+8205 — окремий захист", 8.5, GREY, "middle", "bold")
    s += text(595, 328, "(на «захищених» платах, тема 10.4.6)", 7.6, GREY, "middle")
    s += rect(70, H - 30, W - 140, 20, "#fbf7ec", AMBER, 1.4, 8)
    s += text(W / 2, H - 15, "Плата заряджає сама: подай 5 В, постав Rprog під струм. Та лінійний чип ГРІЄТЬСЯ, а класична версія тягне систему прямо з BAT (нема power-path).", 8.6, INK, "middle")
    save("fig-10-3c1-tp4056.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Вставка 🔌 (до теми 10.4.4) — Паливомір MAX17048-класу
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 10.4.4c.1 — паливомір без шунта ─────────────────────────────────────
def fig_fuel_gauge():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Паливомір MAX17048-класу: SoC без шунта", 18, INK, "middle", "bold")
    s += rect(50, 150, 100, 70, "#eef8ef", GREEN, 1.8, 10)
    s += text(100, 180, "комірка", 10, GREEN, "middle", "bold")
    s += text(100, 198, "Li 1S", 8.5, INK, "middle")
    s += line(150, 165, 758, 165, RED, 2.4)
    s += text(762, 169, "у систему", 8.5, RED, "start")
    s += rect(380, 152, 50, 26, "#fff", GREY, 1.4, 4)
    s += text(405, 169, "шунт", 8, GREY, "middle")
    s += line(376, 148, 434, 182, RED, 2.2)
    s += line(434, 148, 376, 182, RED, 2.2)
    s += text(405, 196, "НЕ потрібен", 8.5, RED, "middle", "bold")
    s += rect(250, 230, 200, 120, "#eef3fb", BLUE, 2, 12)
    s += text(350, 256, "паливомір", 12, BLUE, "middle", "bold")
    s += text(350, 274, "модель комірки", 9, INK, "middle")
    s += text(350, 290, "міряє лише VCELL", 9, INK, "middle")
    s += text(350, 308, "→ рахує SOC %", 9.5, GREEN, "middle", "bold")
    s += text(350, 326, "(без інтеграла струму)", 8, GREY, "middle")
    s += line(100, 220, 100, 290, GREEN, 1.4, dash="3,3")
    s += line(100, 290, 250, 290, GREEN, 1.4, dash="3,3")
    s += text(168, 283, "VCELL (вимір + живлення)", 7.6, GREEN, "middle")
    s += rect(620, 230, 160, 120, "#ffffff", INK, 2, 12)
    s += text(700, 256, "МК", 12, INK, "middle", "bold")
    s += line(450, 280, 620, 280, BLUE, 2)
    s += text(535, 272, "I²C (SDA/SCL)", 8.5, BLUE, "middle", "bold")
    s += text(535, 292, "читає SOC, VCELL", 8, INK, "middle")
    s += line(450, 320, 620, 320, AMBER, 2)
    s += text(535, 334, "ALRT → переривання (низький заряд)", 8, AMBER, "middle", "bold")
    s += rect(70, H - 30, W - 140, 20, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "Паливомір сидить на напрузі комірки й моделлю оцінює SoC — без шунта в силовій лінії (отже, без втрат на ньому) і без дрейфу кулонометрії.", 8.8, INK, "middle")
    save("fig-10-4c1-fuelgauge.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Вставка ⚙️ (до теми 10.4.4) — Лічба заряду у прошивці
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 10.4.4a.1 — конвеєр кулонометрії ────────────────────────────────────
def fig_coulomb_loop():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Лічба заряду в прошивці: інтеграл струму з корекціями", 16.5, INK, "middle", "bold")
    boxes = [
        ("АЦП струму", "(шунт)", BLUE, 40),
        ("− зсув", "(калібр. нуля)", AMBER, 220),
        ("× Δt, ∫", "інтегрувати", GREEN, 400),
        ("Q += I·Δt", "накопичувач", INK, 580),
        ("SoC = SoC0", "− Q/Ємність", RED, 760),
    ]
    for t, sub, c, x in boxes:
        s += rect(x, 110, 140, 60, "#ffffff", c, 1.8, 10)
        s += text(x + 70, 134, t, 10, c, "middle", "bold")
        s += text(x + 70, 152, sub, 8.3, INK, "middle")
        if x < 760:
            s += arrow(x + 140, 140, x + 218, 140, INK, 2)
    s += rect(120, 230, 320, 56, "#eef8ef", GREEN, 1.6, 10)
    s += text(280, 252, "ЯКОРІ (скидають дрейф)", 10, GREEN, "middle", "bold")
    s += text(280, 270, "повний заряд → SoC=100, Q=0;  відсічка → SoC=0", 8.3, INK, "middle")
    s += arrow(280, 230, 650, 172, GREEN, 1.6, dash="5,4")
    s += rect(500, 230, 320, 56, "#fbf7ec", AMBER, 1.6, 10)
    s += text(660, 252, "НАПРУГА у спокої (фьюжн)", 10, AMBER, "middle", "bold")
    s += text(660, 270, "м'яко підправляє Q проти дрейфу (10.4.4)", 8.3, INK, "middle")
    s += arrow(660, 230, 810, 172, AMBER, 1.6, dash="5,4")
    s += rect(70, H - 58, W - 140, 46, "#fbf7ec", AMBER, 1.4, 9)
    s += text(W / 2, H - 40, "Серце — періодичне Q += I·Δt; та без двох підпорок воно бреше: ЯКОРІ на повному/порожньому скидають накопичений дрейф,", 9, INK, "middle")
    s += text(W / 2, H - 25, "а НАПРУГА у спокої м'яко тягне оцінку до істини. Окремо віднімають зсув АЦП — інакше навіть «нульовий» струм інтегрується в помилку.", 9, INK, "middle")
    s += text(W / 2, H - 10, "І ділять на ВИВЧЕНУ ємність (вона тане з віком, тема 10.4.5), а не на паспортну.", 8.5, GREY, "middle")
    save("fig-10-4a1-coulomb.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Вставка 🔌 (до теми 10.4.6) — Захист DW01+8205
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 10.4.6c.1 — плата DW01+8205 ─────────────────────────────────────────
def fig_dw01():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Плата DW01+8205: захист LiPo за долар, зблизька", 17, INK, "middle", "bold")
    s += rect(50, 150, 100, 80, "#eef8ef", GREEN, 1.8, 10)
    s += text(100, 184, "комірка", 10, GREEN, "middle", "bold")
    s += text(100, 202, "Li 1S", 8.5, INK, "middle")
    s += line(150, 165, 818, 165, RED, 2.4)
    s += text(160, 158, "B+", 8.5, RED, "start", "bold")
    s += circle(820, 165, 4, RED, RED, 0)
    s += text(828, 161, "P+", 9, RED, "start", "bold")
    s += line(150, 215, 380, 215, INK, 2)
    s += text(160, 230, "B−", 8.5, INK, "start", "bold")
    s += rect(380, 198, 60, 34, "#fff7e6", AMBER, 1.8, 6)
    s += text(410, 219, "FET", 8.5, AMBER, "middle", "bold")
    s += rect(460, 198, 60, 34, "#fff7e6", AMBER, 1.8, 6)
    s += text(490, 219, "FET", 8.5, AMBER, "middle", "bold")
    s += line(440, 215, 460, 215, INK, 2)
    s += line(520, 215, 818, 215, INK, 2)
    s += text(410, 246, "розряд", 7.5, INK, "middle")
    s += text(490, 246, "заряд", 7.5, INK, "middle")
    s += text(560, 188, "8205 — спарений N-MOSFET", 8, AMBER, "middle")
    s += circle(820, 215, 4, INK, INK, 0)
    s += text(828, 219, "P−", 9, INK, "start", "bold")
    s += text(820, 132, "до пристрою / зарядки", 8.5, GREY, "middle")
    s += rect(360, 290, 200, 80, "#eef3fb", BLUE, 1.8, 10)
    s += text(460, 314, "DW01 — захисний чип", 10, BLUE, "middle", "bold")
    s += text(460, 332, "стежить V комірки та струм", 8.3, INK, "middle")
    s += text(460, 348, "(падіння на FET = шунт)", 8, GREY, "middle")
    s += line(100, 230, 100, 330, INK, 1.2, dash="3,3")
    s += line(100, 330, 360, 330, INK, 1.2, dash="3,3")
    s += text(225, 343, "VCC: міряє напругу комірки", 7.8, INK, "middle")
    s += line(410, 290, 410, 232, GREEN, 1.4)
    s += text(396, 268, "OD", 7.5, GREEN, "end", "bold")
    s += line(490, 290, 490, 232, GREEN, 1.4)
    s += text(504, 268, "OC", 7.5, GREEN, "start", "bold")
    s += text(450, 282, "керує затворами", 7.6, GREEN, "middle")
    s += line(560, 320, 600, 320, AMBER, 1.4)
    s += line(600, 320, 600, 217, AMBER, 1.4, dash="3,3")
    s += text(612, 300, "CS: струм за падінням на FET", 7.6, AMBER, "start")
    s += rect(70, H - 30, W - 140, 20, "#fbe9e7", RED, 1.4, 8)
    s += text(W / 2, H - 15, "DW01 розмикає потрібний FET на OVP/UVP/OCP/SCP. Поріг струму залежить від Rds ключів (вони ж і шунт), тож він не точний. Це ЛИШЕ захист 1S.", 8.6, INK, "middle")
    save("fig-10-6c1-dw01.svg", s)


if __name__ == "__main__":
    fig_timeline()
    fig_priority()
    fig_chemistries()
    # тема 10.4.1
    fig_voltage_ladder()
    fig_specific_energy()
    fig_discharge_curves()
    fig_cycle_life()
    fig_temp_windows()
    fig_decision_map()
    # тема 10.4.2
    fig_rint_model()
    fig_pulse_sag()
    fig_measure_rint()
    fig_rint_soc()
    fig_rint_temp()
    fig_rint_design()
    # тема 10.4.3
    fig_ccv_curves()
    fig_charge_phases()
    fig_voltage_accuracy()
    fig_jeita_temp()
    fig_charge_targets()
    fig_charge_node()
    # тема 10.4.4
    fig_soc_problem()
    fig_voltage_method()
    fig_coulomb()
    fig_fusion()
    fig_recalibrate()
    fig_soc_decision()
    # тема 10.4.5
    fig_two_agings()
    fig_capacity_fade()
    fig_killers()
    fig_dod_cycles()
    fig_storage_grid()
    fig_design_for_aging()
    # тема 10.4.6
    fig_why_protect()
    fig_protection_board()
    fig_thresholds()
    fig_balancing()
    fig_weakest_cell()
    fig_spectrum()
    # тема 10.4.7
    fig_battery_object()
    fig_holders()
    fig_connectors()
    fig_swelling()
    fig_fail_safe()
    fig_storage_transport()
    # вставка 🧮 sag-calc
    fig_sag_vs_crate()
    fig_sag_margin()
    # вставка 🔌 TP4056
    fig_tp4056()
    # вставка 🔌 fuel gauge
    fig_fuel_gauge()
    # вставка ⚙️ coulomb counting
    fig_coulomb_loop()
    # вставка 🔌 DW01 захист
    fig_dw01()
    print("done r04 figures")
