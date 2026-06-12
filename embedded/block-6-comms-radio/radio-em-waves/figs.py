# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 39 — «Радіо: фізика електромагнітних хвиль» (Модуль 6).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; E-поле червоне, B-поле синє; стрілки через marker;
шрифт sans-serif. Підписи посекційно (Рис. C.S.N); історія — секція 0 (Рис. 39.0.N).
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"   # електричне поле E
BLUE  = "#1f47b5"   # магнітне поле B
GREEN = "#1f8a3b"   # висновок
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
SPARK = "#e8b53a"   # іскра
METAL = "#9a9aa0"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LGREY = "#f3f3f3"
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


def sine(x0, y0, length, amp, periods, color, w=2.4, phase=0.0):
    pts = []
    n = max(40, int(length / 3))
    for i in range(n + 1):
        t = i / n
        x = x0 + t * length
        y = y0 - amp * math.sin(2 * math.pi * periods * t + phase)
        pts.append((x, y))
    return f'<path d="M ' + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f'" fill="none" stroke="{color}" stroke-width="{w}"/>\n'


def spark(cx, cy, r=14, col=SPARK, w=2.2):
    s = ""
    pts = []
    import math as _m
    for k in range(8):
        ang = k * _m.pi / 4
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rr * _m.cos(ang), cy + rr * _m.sin(ang)))
    path = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"
    s += f'<path d="{path}" fill="none" stroke="{col}" stroke-width="{w}"/>\n'
    return s


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── Рис. 39.0.1 — таймлайн ───────────────────────────────────────────────────
def fig_timeline():
    W, H = 900, 600
    s = header(W, H)
    s += text(W / 2, 38, "Від рівнянь Максвелла до спійманої хвилі", 21, INK, "middle", "bold")
    s += text(W / 2, 60, "спершу математика передбачила хвилю, і лише за 20+ років її впіймали в досліді",
              12.5, GREY, "middle", style="italic")
    spine = 250
    top, bot = 96, H - 28
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("1865", "Максвелл / Maxwell",
         "Рівняння поля передбачають хвилю, що біжить зі швидкістю світла. Чисто на папері", False, False),
        ("1879", "Максвелл помирає",
         "Так і не дочекавшись, чи існує його хвиля насправді", False, False),
        ("1886–88", "Герц / Hertz, Карлсруе",
         "Іскровий передавач і петля-приймач: невидима хвиля СПРАВДІ перетнула кімнату", False, True),
        ("1888", '"Жодної користі"',
         "«Це лише доказ, що маестро Максвелл мав рацію» — Герц не бачив застосувань", False, False),
        ("1890-ті+", "Марконі, Попов, Тесла…",
         "Інші зробили з хвилі РАДІО — окрема, колективна й спірна історія (Розділ 41)", False, False),
        ("Розділ 39", "Фізика радіо сьогодні",
         "Що ж насправді летить «по повітрю»: електромагнітна хвиля від першопричин", True, False),
    ]
    n = len(nodes)
    for i, (yr, who, q, dest, accent) in enumerate(nodes):
        y = top + 30 + (bot - top - 60) * i / (n - 1)
        col = GREY if dest else INK
        if accent:
            s += circle(spine, y, 10, "#fff", RED, 3)
            s += circle(spine, y, 4.5, RED, RED, 0)
        elif dest:
            s += rect(spine - 8, y - 8, 16, 16, "#fff", GREEN, 2.6, 3)
        else:
            s += circle(spine, y, 7, "#fff", col, 2.6)
        s += text(spine - 22, y + 5, yr, 12.5, (GREEN if dest else GREY), "end", "bold")
        s += text(spine + 26, y - 3, who, 15.5,
                  (RED if accent else (GREEN if dest else col)), "start", "bold")
        s += text(spine + 26, y + 17, q, 12, (INK if not dest else GREY), "start", style="italic")
    save("fig-39-0-1-timeline.svg", s)


# ── Рис. 39.0.2 — передбачення Максвелла ─────────────────────────────────────
def fig_maxwell():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 36, "Передбачення Максвелла: E і B породжують одне одного", 19, INK, "middle", "bold")
    s += text(W / 2, 58, "змінне електричне поле творить магнітне, змінне магнітне — електричне; так хвиля сама себе несе",
              12, GREY, "middle", style="italic")
    # цикл E→B→E
    cx, cy = 250, 210
    s += circle(170, cy, 50, LRED, RED, 2)
    s += text(170, cy - 4, "змінне", 11, RED, "middle", "bold")
    s += text(170, cy + 14, "E (§1)", 12, RED, "middle", "bold")
    s += circle(330, cy, 50, LBLUE, BLUE, 2)
    s += text(330, cy - 4, "змінне", 11, BLUE, "middle", "bold")
    s += text(330, cy + 14, "B (§8)", 12, BLUE, "middle", "bold")
    s += arrow(212, cy - 26, 290, cy - 26, INK, 2)
    s += text(251, cy - 36, "творить", 9.5, GREY, "middle")
    s += arrow(290, cy + 26, 212, cy + 26, INK, 2)
    s += text(251, cy + 44, "творить", 9.5, GREY, "middle")
    # → хвиля
    s += arrow(390, cy, 470, cy, GREEN, 2.6)
    s += text(430, cy - 10, "самопідтримна", 10, GREEN, "middle", "bold")
    s += sine(490, cy, 340, 36, 3, RED, 2.4)
    s += sine(490, cy, 340, 22, 3, BLUE, 2.0, phase=math.pi)
    s += text(660, cy - 56, "електромагнітна хвиля", 11.5, INK, "middle", "bold")
    s += text(660, cy + 60, "біжить зі швидкістю СВІТЛА", 11.5, GREEN, "middle", "bold")

    s += rect(60, 320, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 344, "Максвелл (1865) вивів це з рівнянь і додав: світло — це теж така хвиля, лише іншої частоти.",
              12, INK, "middle", "bold")
    s += text(W / 2, 364, "Та чи існує вона насправді — на папері не доведеш. Потрібен був дослід.",
              11, GREY, "middle", style="italic")
    save("fig-39-0-2-maxwell.svg", s)


# ── Рис. 39.0.3 — дослід Герца ───────────────────────────────────────────────
def fig_hertz_apparatus():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 34, "Дослід Герца: іскровий передавач і петля-приймач", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "іскра в передавачі породжує хвилю; за кілька метрів у петлі-приймачі проскакує крихітна іскра",
              12, GREY, "middle", style="italic")
    # передавач
    s += text(170, 100, "ПЕРЕДАВАЧ", 12.5, RED, "middle", "bold")
    s += rect(90, 250, 90, 60, "#fbfbfb", INK, 1.8, 6)
    s += text(135, 276, "котушка", 10, INK, "middle", "bold")
    s += text(135, 292, "Румкорфа", 8.5, GREY, "middle")
    s += text(135, 306, "~30 кВ", 8.5, RED, "middle", "bold")
    # диполь зі сферами й іскровим проміжком
    s += line(180, 200, 250, 200, METAL, 3)   # ліве плече
    s += line(290, 200, 360, 200, METAL, 3)   # праве плече
    s += circle(180, 200, 10, "#dadade", METAL, 1.6)
    s += circle(360, 200, 10, "#dadade", METAL, 1.6)
    s += line(180, 200, 180, 250, INK, 1.6)
    s += line(180, 250, 135, 250, INK, 1.6)
    s += line(360, 200, 360, 250, INK, 1.6)
    s += line(360, 250, 180, 250, INK, 1.4, dash="3,3")
    s += spark(270, 200, 12)
    s += text(270, 176, "іскровий проміжок", 9, SPARK, "middle", "bold")
    s += text(270, 230, "диполь (антена)", 9.5, GREY, "middle")

    # хвиля
    s += sine(380, 200, 320, 26, 3.5, GREEN, 2.2)
    s += arrow(380, 235, 700, 235, GREEN, 2, dash="5,4")
    s += text(540, 258, "невидима хвиля летить простором", 10.5, GREEN, "middle", "bold")

    # приймач — петля з мікропроміжком
    s += text(790, 100, "ПРИЙМАЧ", 12.5, BLUE, "middle", "bold")
    s += f'<path d="M 790,150 A 55 55 0 1 1 778,150" fill="none" stroke="{INK}" stroke-width="3"/>\n'
    s += spark(784, 150, 9)
    s += text(840, 150, "мікро-", 9, SPARK, "start", "bold")
    s += text(840, 164, "проміжок", 9, SPARK, "start", "bold")
    s += text(790, 240, "петля-резонатор", 10, GREY, "middle")
    s += text(790, 256, "тут проскакує крихітна іскра", 9, BLUE, "middle", "bold")

    s += rect(60, 320, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 344, "У темній кімнаті Герц бачив слабкі іскри в петлі — доказ, що хвиля перетнула порожній простір.",
              12, INK, "middle", "bold")
    s += text(W / 2, 364, "Передавач і приймач не з'єднані нічим — лише хвилею. Це і є народження радіо як факту.",
              11, GREY, "middle", style="italic")
    save("fig-39-0-3-hertz-apparatus.svg", s)


# ── Рис. 39.0.4 — хвиля поводиться як світло ─────────────────────────────────
def fig_like_light():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Що довів Герц: хвиля поводиться точно як світло", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "відбивається, заломлюється, поляризується й летить зі швидкістю світла — отже, це те саме явище",
              12, GREY, "middle", style="italic")
    props = [
        ("відбивається", "від металу — як від дзеркала"),
        ("заломлюється", "у призмі — як промінь"),
        ("поляризується", "має напрям коливань"),
        ("швидкість = c", "виміряв — як у світла"),
    ]
    x = 60
    for nm, desc in props:
        s += rect(x, 96, 200, 110, "#fbfbfb", GREEN, 2, 12)
        s += text(x + 100, 130, nm, 13, GREEN, "middle", "bold")
        for j, ln in enumerate([desc]):
            s += text(x + 100, 162, ln, 9.8, INK, "middle")
        x += 207

    s += rect(60, 226, W - 120, 100, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 252, "Висновок Максвелла-Герца: радіохвиля й світло — ОДНЕ явище, лише різної частоти.",
              12.5, INK, "middle", "bold")
    s += text(W / 2, 276, "Від радіо до видимого світла й рентгену — усе це електромагнітні хвилі в одному спектрі.",
              11.5, INK, "middle")
    s += text(W / 2, 300, "Тому всю інтуїцію про світло (відбиття, тінь, дальність) можна переносити на радіо.",
              11, GREY, "middle", style="italic")
    save("fig-39-0-4-like-light.svg", s)


# ── Рис. 39.0.5 — від «жодної користі» до радіо ──────────────────────────────
def fig_no_use():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "«Жодної користі» — і колективний шлях до радіо", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "Герц бачив лише доказ теорії; перетворити хвилю на зв'язок — заслуга інших, і досі спірна",
              12, GREY, "middle", style="italic")
    # цитата
    s += rect(90, 92, 720, 70, LGREY, GREY, 1.6, 12)
    s += text(450, 122, "«Це не має жодної користі… просто дослід, що доводить:", 13, INK, "middle", "italic")
    s += text(450, 144, "маестро Максвелл мав рацію.» — Г. Герц", 13, INK, "middle", "italic")
    # пізніше — піонери
    s += text(450, 196, "а далі з хвилі зробили РАДІО (різні люди, різні країни, спірний пріоритет):", 11.5, INK, "middle", "bold")
    names = ["Марконі", "Попов", "Тесла", "Боше", "Лодж"]
    x = 130
    for nm in names:
        s += rect(x, 216, 120, 44, "#fbfbfb", BLUE, 1.8, 8)
        s += text(x + 60, 242, nm, 11.5, INK, "middle", "bold")
        x += 130

    s += rect(60, 286, W - 120, 70, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 310, "Винахід радіо — НЕ один герой: над ним працювали багато, а суд за пріоритет тривав десятиліттями.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 332, "(Цю окрему історію — Марконі та інші — розкриваємо в Розділі 41.)",
              11, GREY, "middle", style="italic")
    s += text(W / 2, 350, "А одиницю частоти — герц (Гц) — назвали на честь того, хто хвилю першим упіймав.",
              10.5, GREY, "middle", style="italic")
    save("fig-39-0-5-no-use.svg", s)


# додатковий колір для сумісності
BTBLUE = "#0a3d91"


# ============================================================================
#  §39.1 — Електромагнітна хвиля: електрика й магнетизм у русі
# ============================================================================
def plus(cx, cy, r=11, color=RED, w=2.4):
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w)
            + line(cx, cy - r * 0.55, cx, cy + r * 0.55, color, w))


# ── Рис. 39.1.1 — будова ЕМ-хвилі: E ⊥ B ⊥ напрямок ──────────────────────────
def fig11_structure():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 34, "Будова електромагнітної хвилі: E і B перпендикулярні", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "електричне поле E коливається вгору-вниз, магнітне B — упоперек, а хвиля біжить уперед",
              12.5, GREY, "middle", style="italic")
    x0, axis = 110, 210
    length = 660
    # вісь поширення
    s += arrow(x0, axis, x0 + length + 20, axis, INK, 1.8)
    s += text(x0 + length + 26, axis + 4, "напрямок руху", 10.5, INK, "start", "bold")
    # E — червона синусоїда (вертикальна площина)
    s += sine(x0, axis, length, 80, 2.5, RED, 2.6)
    # стрілки E у пік
    for k in range(5):
        t = (k + 0.5) / 5
        px = x0 + t * length
        py = axis - 80 * math.sin(2 * math.pi * 2.5 * t)
        s += line(px, axis, px, py, RED, 1.4)
    s += text(x0 + 30, axis - 88, "E (електричне)", 12, RED, "start", "bold")
    # B — синя синусоїда у «перспективі» (перпендикулярна площина)
    bpts = []
    n = 120
    for i in range(n + 1):
        t = i / n
        px = x0 + t * length + 0.32 * 46 * math.sin(2 * math.pi * 2.5 * t)
        py = axis + 0.55 * 46 * math.sin(2 * math.pi * 2.5 * t)
        bpts.append((px, py))
    s += '<path d="M ' + " L ".join(f"{x:.1f},{y:.1f}" for x, y in bpts) + f'" fill="none" stroke="{BLUE}" stroke-width="2.4"/>\n'
    s += text(x0 + 200, axis + 64, "B (магнітне, упоперек)", 12, BLUE, "start", "bold")

    s += rect(60, 320, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 344, "E, B і напрямок руху — взаємно перпендикулярні (поперечна хвиля). Усі троє «під прямим кутом».",
              12, INK, "middle", "bold")
    s += text(W / 2, 364, "У вакуумі хвиля біжить зі швидкістю світла c ≈ 3×10⁸ м/с.",
              11, GREY, "middle", style="italic")
    save("fig-39-1-1-structure.svg", s)


# ── Рис. 39.1.2 — випромінює тільки ПРИСКОРЕНИЙ заряд ─────────────────────────
def fig12_accelerating():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Хвилю народжує лише ПРИСКОРЕНИЙ (коливний) заряд", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "нерухомий заряд має статичне поле; рівномірний рух — теж; а ось трясти заряд = випромінювати",
              12, GREY, "middle", style="italic")
    # нерухомий
    s += text(150, 96, "нерухомий", 12, INK, "middle", "bold")
    s += plus(150, 180, 12)
    for a in range(0, 360, 45):
        ang = math.radians(a)
        s += line(150 + 16 * math.cos(ang), 180 + 16 * math.sin(ang), 150 + 46 * math.cos(ang), 180 + 46 * math.sin(ang), RED, 1.2)
    s += text(150, 240, "статичне поле", 9.5, GREY, "middle")
    s += text(150, 256, "хвилі нема", 9.5, GREY, "middle")
    # рівномірний рух
    s += text(420, 96, "рівномірний рух", 12, INK, "middle", "bold")
    s += plus(420, 180, 12)
    s += arrow(440, 180, 500, 180, INK, 1.8)
    s += text(470, 168, "v=const", 9, GREY, "middle")
    s += text(420, 240, "поле просто їде з ним", 9.5, GREY, "middle")
    s += text(420, 256, "хвилі нема", 9.5, GREY, "middle")
    # прискорений
    s += text(720, 96, "коливається (a≠0)", 12, GREEN, "middle", "bold")
    s += plus(720, 180, 12)
    s += arrow(720, 160, 720, 130, GREEN, 1.8); s += arrow(720, 200, 720, 230, GREEN, 1.8)
    s += text(745, 178, "трясеться", 9.5, GREEN, "start", "bold")
    s += sine(740, 180, 110, 18, 2, GREEN, 2)
    s += text(720, 256, "→ ВИПРОМІНЮЄ хвилю", 9.5, GREEN, "middle", "bold")

    s += rect(60, 290, W - 120, 70, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 314, "Антена — це місце, де ми навмисне ТРЯСЕМО заряди (змінним струмом), щоб запустити хвилю.",
              12, INK, "middle", "bold")
    s += text(W / 2, 336, "Саме коливний струм у диполі Герца й породжував його хвилю — і так само в кожній антені (§41).",
              11, GREY, "middle", style="italic")
    save("fig-39-1-2-accelerating.svg", s)


# ── Рис. 39.1.3 — самопідтримка: E↔B по черзі ────────────────────────────────
def fig13_leapfrog():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Чому хвиля не згасає: E і B підхоплюють одне одного", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "змінне E творить B попереду, змінне B творить E ще далі — і так хвиля «крокує» сама",
              12, GREY, "middle", style="italic")
    y = 180
    steps = [("E", RED), ("B", BLUE), ("E", RED), ("B", BLUE), ("E", RED)]
    x = 130
    for i, (lab, col) in enumerate(steps):
        s += circle(x, y, 30, (LRED if col == RED else LBLUE), col, 2)
        s += text(x, y + 5, lab, 16, col, "middle", "bold")
        if i < len(steps) - 1:
            s += arrow(x + 32, y, x + 108, y, INK, 2)
            s += text(x + 70, y - 10, "творить", 8.5, GREY, "middle")
        x += 140
    s += arrow(130, 240, 770, 240, GREEN, 2.2)
    s += text(450, 262, "хвиля рухається вперед зі швидкістю світла", 11, GREEN, "middle", "bold")

    s += rect(60, 282, W - 120, 50, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 307, "Жодного середовища не треба: поля самі себе несуть. Енергію передає сама хвиля.",
              12, INK, "middle", "bold")
    s += text(W / 2, 326, "(Це той самий механізм Максвелла, тепер як рушій руху хвилі.)", 10.5, GREY, "middle", style="italic")
    save("fig-39-1-3-leapfrog.svg", s)


# ── Рис. 39.1.4 — поперечна проти поздовжньої ────────────────────────────────
def fig14_transverse():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Поперечна (ЕМ) проти поздовжньої (звук)", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "у ЕМ-хвилі поля коливаються УПОПЕРЕК руху; у звуці повітря стискається УЗДОВЖ нього",
              12, GREY, "middle", style="italic")
    # поперечна
    s += text(230, 100, "ЕМ-хвиля (поперечна)", 12.5, RED, "middle", "bold")
    s += arrow(90, 160, 380, 160, INK, 1.6)
    s += sine(100, 160, 270, 36, 2.5, RED, 2.4)
    s += arrow(235, 160, 235, 124, RED, 1.6)
    s += text(250, 134, "коливання ⊥ руху", 9.5, RED, "start", "bold")
    s += text(230, 210, "→ рух", 9.5, GREY, "middle")
    # поздовжня
    s += text(670, 100, "звук (поздовжня)", 12.5, BLUE, "middle", "bold")
    s += arrow(530, 160, 820, 160, INK, 1.6)
    for k in range(14):
        density = 1 + math.sin(2 * math.pi * k / 5)
        xx = 540 + k * 20
        gap = 6 if density > 0.5 else 14
        s += line(xx, 140, xx, 180, BLUE, 1.4 + density)
    s += text(670, 200, "стиски/розрідження УЗДОВЖ руху", 9.5, BLUE, "middle", "bold")
    s += text(670, 218, "→ рух", 9, GREY, "middle")

    s += rect(60, 248, W - 120, 92, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 274, "Звук — це коливання РЕЧОВИНИ вздовж руху, тож йому потрібне середовище (повітря).",
              12, INK, "middle", "bold")
    s += text(W / 2, 296, "ЕМ-хвиля — коливання ПОЛІВ упоперек руху, і середовища їй не треба зовсім.",
              12, INK, "middle")
    s += text(W / 2, 318, "Тому в космосі немає звуку — але є радіо й світло.", 11, GREY, "middle", style="italic")
    save("fig-39-1-4-transverse.svg", s)


# ── Рис. 39.1.5 — не потрібне середовище ─────────────────────────────────────
def fig15_no_medium():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "ЕМ-хвиля летить крізь ПОРОЖНЕЧУ — середовище не потрібне", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "поля самі собі «середовище»; саме тому світло Сонця й радіо долають порожній космос",
              12, GREY, "middle", style="italic")
    s += circle(150, 180, 40, "#fff4d6", AMBER, 2)
    s += text(150, 184, "Сонце", 11, "#a8801f", "middle", "bold")
    for k in range(3):
        s += sine(195, 180 - 20 + k * 20, 450, 8, 6, AMBER, 1.6)
    s += arrow(200, 180, 660, 180, AMBER, 2, dash="6,5")
    s += text(430, 130, "крізь порожній космос (вакуум)", 11, INK, "middle", "bold")
    s += circle(720, 180, 34, LBLUE, BLUE, 2)
    s += text(720, 184, "Земля", 11, BLUE, "middle", "bold")

    s += rect(60, 250, W - 120, 80, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 274, "Це була найрадикальніша частина теорії: хвиля без жодного дроту чи речовини між точками.",
              12, INK, "middle", "bold")
    s += text(W / 2, 296, "Для радіо це означає: сигнал летить простором сам, а «повітря» лише трохи його послаблює.",
              11.5, INK, "middle")
    s += text(W / 2, 316, "(Звук так не вміє — у вакуумі його нема; ЕМ-хвиля вміє.)", 11, GREY, "middle", style="italic")
    save("fig-39-1-5-no-medium.svg", s)


# ── Рис. 39.1.6 — хвиля несе енергію ─────────────────────────────────────────
def fig16_energy():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 34, "Хвиля переносить ЕНЕРГІЮ від передавача до приймача", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "енергію несуть самі поля (§1.3 — поле реальне); передавач її віддає, приймач вловлює",
              12, GREY, "middle", style="italic")
    s += rect(80, 150, 130, 70, "#eef6ef", GREEN, 2, 10)
    s += text(145, 182, "передавач", 11, GREEN, "middle", "bold")
    s += text(145, 200, "віддає енергію", 9, GREY, "middle")
    s += line(210, 150, 210, 135, GREEN, 2)
    for k in range(4):
        s += sine(230 + k * 0, 185 - 18 + k * 12, 440, 10, 6, GREEN, 1.6)
    s += arrow(235, 185, 690, 185, GREEN, 2, dash="6,5")
    s += text(450, 130, "потік енергії →", 11, GREEN, "middle", "bold")
    s += rect(700, 150, 130, 70, "#fbfbfb", INK, 2, 10)
    s += text(765, 182, "приймач", 11, INK, "middle", "bold")
    s += text(765, 200, "вловлює крихту", 9, GREY, "middle")

    s += rect(60, 246, W - 120, 70, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 270, "До приймача долітає лише КРИХІТНА частка енергії (більшість розходиться навсібіч — §39.6).",
              12, INK, "middle", "bold")
    s += text(W / 2, 292, "Та цього досить: приймач підсилює слабкий сигнал. Радіо — це передавання енергії без дроту.",
              11.5, INK, "middle")
    s += text(W / 2, 311, "(Те саме світло Сонця гріє Землю — теж енергія, принесена хвилею.)", 10.5, GREY, "middle", style="italic")
    save("fig-39-1-6-energy.svg", s)


# ── Рис. 39.1.7 — від тремтливого заряду до радіо ────────────────────────────
def fig17_antenna():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Антена: керовано трясемо заряди, щоб запустити хвилю", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "змінний струм жене заряди вгору-вниз по дроту — і той випромінює, як диполь Герца",
              12, GREY, "middle", style="italic")
    # дріт-антена
    s += line(180, 110, 180, 250, METAL, 4)
    s += plus(180, 140, 8)
    s += plus(180, 220, 8)
    s += arrow(180, 200, 180, 160, GREEN, 1.8)
    s += arrow(180, 160, 180, 200, GREEN, 1.8) if False else ""
    s += text(150, 180, "струм", 10, GREEN, "end", "bold")
    s += text(150, 196, "вгору-вниз", 9, GREY, "end")
    s += rect(160, 250, 40, 26, "#fbfbfb", INK, 1.4, 4)
    s += text(180, 267, "~", 12, INK, "middle", "bold")
    # хвилі
    for k in range(3):
        s += sine(210 + k * 0, 180 - 20 + k * 20, 540, 10, 6, GREEN, 1.6)
    s += arrow(215, 180, 760, 180, GREEN, 2, dash="6,5")
    s += text(480, 130, "випромінена хвиля →", 11, GREEN, "middle", "bold")
    s += text(480, 232, "частота струму = частота хвилі", 10.5, INK, "middle", "bold")

    s += rect(60, 256, W - 120, 70, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 280, "Уся фізика розділу зводиться сюди: трясеш заряди — народжується хвиля; ловиш хвилю — трясуться заряди.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 302, "Як саме добирати дріт під частоту (резонанс, чверть хвилі) — у Розділі 41 про антени.",
              11, INK, "middle")
    s += text(W / 2, 320, "А скільки разів за секунду трястись (частота) і яка тоді довжина хвилі — наступна тема.",
              10.5, GREY, "middle", style="italic")
    save("fig-39-1-7-antenna.svg", s)


# ============================================================================
#  §39.2 — Частота й довжина хвилі (c = λ·f)
# ============================================================================

# ── Рис. 39.2.1 — частота (час) проти довжини хвилі (простір) ─────────────────
def fig21_freq_vs_wave():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 34, "Дві мірки однієї хвилі: частота (в часі) і довжина (в просторі)", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "частота — скільки коливань за секунду; довжина хвилі — яка завдовжки одне коливання у просторі",
              12, GREY, "middle", style="italic")
    # частота — час
    s += rect(60, 90, 380, 200, "none", FAINT, 2, 12)
    s += text(250, 116, "погляд у ЧАСІ (частота f)", 12.5, RED, "middle", "bold")
    s += sine(90, 190, 320, 36, 3, RED, 2.4)
    s += arrow(90, 240, 410, 240, INK, 1.6)
    s += text(410, 258, "час →", 10, INK, "start")
    s += text(250, 274, "f = коливань за секунду (Гц)", 10.5, INK, "middle", "bold")
    # довжина — простір
    s += rect(480, 90, 380, 200, "none", FAINT, 2, 12)
    s += text(670, 116, "погляд у ПРОСТОРІ (довжина λ)", 12, BLUE, "middle", "bold")
    s += sine(510, 190, 320, 36, 3, BLUE, 2.4)
    s += arrow(510, 240, 830, 240, INK, 1.6)
    s += text(830, 258, "відстань →", 10, INK, "start")
    # позначка λ
    lam0 = 510 + 320 / 3 * 0.0
    s += arrow(510, 150, 510 + 320 / 3, 150, "#b08900", 1.6)
    s += arrow(510 + 320 / 3, 150, 510, 150, "#b08900", 1.6)
    s += text(510 + 320 / 6, 142, "λ", 13, "#b08900", "middle", "bold")
    s += text(670, 274, "λ = довжина одного коливання (м)", 10.5, INK, "middle", "bold")

    s += rect(60, 304, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 329, "Це одна й та сама хвиля з двох боків: як швидко вона хитається в часі — і яка завдовжки в просторі.",
              11.5, INK, "middle", "bold")
    save("fig-39-2-1-freq-vs-wave.svg", s)


# ── Рис. 39.2.2 — c = λ·f ────────────────────────────────────────────────────
def fig22_c_eq():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Зв'язок: c = λ · f (швидкість світла стала)", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "оскільки c незмінна, частота й довжина хвилі — обернено пропорційні: одне росте, інше падає",
              12, GREY, "middle", style="italic")
    s += text(W / 2, 118, "c = λ · f", 28, INK, "middle", "bold")
    s += text(W / 2, 146, "(швидкість світла = довжина хвилі × частота)", 11, GREY, "middle")
    # гойдалка
    cx, cy = 450, 230
    s += line(cx - 180, cy + 18, cx + 180, cy - 18, INK, 3)
    s += circle(cx, cy + 20, 8, INK, INK, 0)
    s += circle(cx - 150, cy + 33, 24, LRED, RED, 2); s += text(cx - 150, cy + 38, "f↑", 14, RED, "middle", "bold")
    s += circle(cx + 150, cy - 33, 24, LBLUE, BLUE, 2); s += text(cx + 150, cy - 28, "λ↓", 14, BLUE, "middle", "bold")
    s += text(cx - 150, cy + 70, "вища частота", 10, RED, "middle", "bold")
    s += text(cx + 150, cy - 56, "коротша хвиля", 10, BLUE, "middle", "bold")
    s += text(cx + 250, cy, "λ = c / f", 16, GREEN, "middle", "bold")

    s += rect(60, 290, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 315, "Знаєш частоту — одразу знаєш довжину хвилі: λ = c / f. І навпаки.",
              12, INK, "middle", "bold")
    save("fig-39-2-2-c-eq.svg", s)


# ── Рис. 39.2.3 — λ для поширених діапазонів ─────────────────────────────────
def fig23_bands():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "λ = c / f для поширених діапазонів", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "що вища частота, то коротша хвиля — від сотень метрів до сантиметрів",
              12.5, GREY, "middle", style="italic")
    bx, by, rw = 110, 92, 680
    s += rect(bx, by, rw, 34, "#f0f0f0", GREY, 1.3, 6)
    for h, dx in [("діапазон", 16), ("частота f", 230), ("довжина λ = c/f", 430)]:
        s += text(bx + dx, by + 22, h, 12, INK, "start", "bold")
    rows = [
        ("AM-радіо", "~1 МГц", "≈ 300 м", "#b08900"),
        ("FM-радіо", "~100 МГц", "≈ 3 м", "#b08900"),
        ("Wi-Fi / BT", "2.4 ГГц", "≈ 12.5 см", GREEN),
        ("Wi-Fi", "5 ГГц", "≈ 6 см", BLUE),
    ]
    yy = by + 34
    for nm, f, lam, col in rows:
        s += rect(bx, yy, rw, 44, ("#eef6ef" if col == GREEN else "#ffffff"), GREY, 1)
        s += text(bx + 16, yy + 28, nm, 12.5, col, "start", "bold")
        s += text(bx + 230, yy + 28, f, 12, INK, "start")
        s += text(bx + 430, yy + 28, lam, 13, col, "start", "bold")
        yy += 44

    s += rect(60, 304, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 328, "AM на 1 МГц має хвилю 300 м; Wi-Fi на 2.4 ГГц — 12.5 см. У 2400 разів вища частота → у 2400 коротша хвиля.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 348, "Саме тому 2.4 ГГц антена — крихітна, а AM-щогли — велетенські (про це далі).",
              11, GREY, "middle", style="italic")
    save("fig-39-2-3-bands.svg", s)


# ── Рис. 39.2.4 — висока проти низької частоти ───────────────────────────────
def fig24_high_low():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 34, "Та сама відстань: висока частота — короткі хвилі, низька — довгі", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "за один і той самий відрізок простору вкладається або багато коротких, або мало довгих коливань",
              12, GREY, "middle", style="italic")
    s += text(120, 110, "висока f:", 12, RED, "start", "bold")
    s += sine(110, 150, 680, 24, 10, RED, 2.2)
    s += text(450, 188, "багато коротких хвиль", 10.5, RED, "middle", "bold")
    s += text(120, 230, "низька f:", 12, BLUE, "start", "bold")
    s += sine(110, 250, 680, 30, 2.5, BLUE, 2.4)
    s += text(450, 296, "мало довгих хвиль", 10.5, BLUE, "middle", "bold")

    s += rect(60, 250 + 56, 1, 1, "none", "none", 0)
    save("fig-39-2-4-high-low.svg", s)


# ── Рис. 39.2.5 — розмір антени ~ довжина хвилі ──────────────────────────────
def fig25_antenna_size():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Розмір антени йде за довжиною хвилі", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "антену роблять часткою хвилі (зазвичай чверть λ) — тож висока частота = коротка хвиля = мала антена",
              12, GREY, "middle", style="italic")
    # 2.4 ГГц — крихітна
    s += rect(70, 92, 360, 200, "none", FAINT, 2, 12)
    s += text(250, 116, "2.4 ГГц: λ ≈ 12.5 см", 12.5, GREEN, "middle", "bold")
    s += line(250, 250, 250, 220, METAL, 4)
    s += rect(238, 250, 24, 16, "#fbfbfb", INK, 1.4, 3)
    s += text(250, 200, "≈ 3 см (¼λ)", 10.5, INK, "middle", "bold")
    s += text(250, 280, "крихітна — влазить у чип/плату", 9.5, GREY, "middle")
    # AM — велетенська
    s += rect(470, 92, 380, 200, "none", FAINT, 2, 12)
    s += text(660, 116, "AM 1 МГц: λ ≈ 300 м", 12.5, "#b08900", "middle", "bold")
    s += line(660, 280, 660, 150, METAL, 5)
    for yy in (170, 200, 230):
        s += line(640, yy, 680, yy, METAL, 1.6)
    s += text(720, 210, "десятки-сотні", 10, INK, "start", "bold")
    s += text(720, 226, "метрів заввишки", 10, INK, "start", "bold")
    s += text(660, 296, "велетенська щогла", 9.5, GREY, "middle")

    s += rect(60, 306, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 330, "Тому Wi-Fi-антена ховається в куточку плати, а AM-радіостанція має щоглу на десятки метрів.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 350, "Деталі (чверть хвилі, диполь, резонанс) — у Розділі 41; тут головне: РОЗМІР іде за λ.",
              11, GREY, "middle", style="italic")
    save("fig-39-2-5-antenna-size.svg", s)


# ── Рис. 39.2.6 — спектр електромагнітних хвиль ──────────────────────────────
def fig26_spectrum():
    W, H = 920, 360
    s = header(W, H)
    s += text(W / 2, 34, "Усе це — один спектр: радіо, світло, рентген", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "та сама ЕМ-хвиля від низьких частот (радіо) до високих (рентген), упорядкована за f і λ",
              12, GREY, "middle", style="italic")
    bx, by, bw = 70, 150, 780
    segs = [("радіо", "#d7e6f7"), ("мікро-\nхвилі", "#bcd6ef"), ("ІЧ", "#f3d6b0"),
            ("видиме", "#cdebcd"), ("УФ", "#d9c7ef"), ("рентген", "#e6c7c7"), ("гамма", "#efb8b8")]
    sw = bw / len(segs)
    for i, (nm, col) in enumerate(segs):
        s += rect(bx + i * sw, by, sw, 50, col, GREY, 1)
        for j, ln in enumerate(nm.split("\n")):
            s += text(bx + i * sw + sw / 2, by + 24 + j * 13, ln, 10, INK, "middle", "bold")
    s += arrow(bx, by - 12, bx + bw, by - 12, INK, 1.6)
    s += text(bx, by - 18, "нижча частота / довша хвиля", 9.5, GREY, "start")
    s += text(bx + bw, by - 18, "вища частота / коротша хвиля", 9.5, GREY, "end")
    # позначки наших діапазонів
    marks = [(0.06, "AM"), (0.10, "FM"), (0.16, "Wi-Fi/BT 2.4–5 ГГц"), (0.47, "світло, яке ми бачимо")]
    for frac, lab in marks:
        x = bx + bw * frac
        s += line(x, by + 50, x, by + 72, INK, 1.4)
        s += text(x, by + 86, lab, 9, INK, "middle", "bold")

    s += rect(60, 268, W - 120, 70, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 292, "Радіо, тепло, видиме світло, рентген — одне явище: різниться лише частота (і довжина хвилі).",
              12, INK, "middle", "bold")
    s += text(W / 2, 314, "Наші Wi-Fi і Bluetooth — це просто ділянка цього спектра трохи вище за мікрохвильову піч.",
              11, GREY, "middle", style="italic")
    save("fig-39-2-6-spectrum.svg", s)


# ── Рис. 39.2.7 — практичне читання частоти ──────────────────────────────────
def fig27_practical():
    W, H = 900, 320
    s = header(W, H)
    s += text(W / 2, 34, "Практика: побачив частоту — знаєш хвилю й розмір антени", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "одне число (частота) одразу каже й довжину хвилі, і приблизний розмір антени",
              12, GREY, "middle", style="italic")
    s += rect(80, 100, 200, 80, "#fbfbfb", INK, 2, 10)
    s += text(180, 134, "«2.4 ГГц»", 18, BLUE, "middle", "bold")
    s += text(180, 158, "(частота)", 10, GREY, "middle")
    s += arrow(282, 140, 360, 140, GREEN, 2.4)
    s += text(321, 128, "λ = c/f", 10, GREEN, "middle", "bold")
    s += rect(370, 100, 200, 80, "#eef6ef", GREEN, 2, 10)
    s += text(470, 134, "λ ≈ 12.5 см", 16, GREEN, "middle", "bold")
    s += text(470, 158, "(довжина хвилі)", 10, GREY, "middle")
    s += arrow(572, 140, 650, 140, GREEN, 2.4)
    s += text(611, 128, "¼λ", 10, GREEN, "middle", "bold")
    s += rect(660, 100, 200, 80, "#eef6ef", GREEN, 2, 10)
    s += text(760, 134, "антена ≈ 3 см", 15, GREEN, "middle", "bold")
    s += text(760, 158, "(розмір)", 10, GREY, "middle")

    s += rect(60, 210, W - 120, 80, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 234, "Це найшвидша оцінка «на серветці»: частота → довжина хвилі → розмір антени.",
              12, INK, "middle", "bold")
    s += text(W / 2, 256, "Побачив «868 МГц» — λ≈35 см, антена ≈9 см; «433 МГц» — λ≈70 см, антена ≈17 см.",
              11.5, INK, "middle")
    s += text(W / 2, 276, "Тому в чужому пристрої за частотою одразу впізнаєш, якого розміру антену шукати.",
              11, GREY, "middle", style="italic")
    save("fig-39-2-7-practical.svg", s)


# ============================================================================
#  §39.3 — Поширення й поляризація
# ============================================================================
def _tower(cx, base, h=46, col=METAL):
    s = line(cx, base, cx, base - h, col, 3)
    s += line(cx, base - h, cx - 6, base - h - 8, col, 2)
    s += line(cx, base - h, cx + 6, base - h - 8, col, 2)
    return s


# ── Рис. 39.3.1 — шляхи поширення ────────────────────────────────────────────
def fig31_paths():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 34, "Як хвиля доходить до приймача: кілька шляхів одразу", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "пряма видимість, відбиття, огинання краю, проникнення крізь стіну — усе працює водночас",
              12, GREY, "middle", style="italic")
    s += _tower(110, 300, 60, GREEN); s += text(110, 320, "TX", 11, GREEN, "middle", "bold")
    s += _tower(810, 300, 60, BLUE); s += text(810, 320, "RX", 11, BLUE, "middle", "bold")
    # перешкода
    s += rect(430, 150, 50, 150, "#e3ded2", "#9a9488", 2)
    s += text(455, 320, "стіна/будівля", 9, GREY, "middle")
    # пряма (заблокована частково)
    s += line(120, 244, 430, 200, GREEN, 1.6, dash="2,3")
    # відбиття від землі
    s += line(120, 250, 460, 330, "#b08900", 2)
    s += line(460, 330, 800, 250, "#b08900", 2)
    s += text(460, 348, "відбиття (від землі)", 9, "#b08900", "middle", "bold")
    # огинання краю
    s += f'<path d="M 120,238 Q 455,120 800,238" fill="none" stroke="{RED}" stroke-width="2"/>\n'
    s += text(455, 116, "огинання верхнього краю (дифракція)", 9.5, RED, "middle", "bold")
    # крізь стіну
    s += line(120, 244, 800, 244, BLUE, 1.6, dash="6,4")
    s += text(600, 234, "крізь стіну (ослаблено)", 9, BLUE, "middle", "bold")

    s += rect(60, 366, W - 120, 1, "none", "none", 0)
    save("fig-39-3-1-paths.svg", s)


# ── Рис. 39.3.2 — відбиття ───────────────────────────────────────────────────
def fig32_reflection():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 34, "Відбиття: хвиля відскакує від металу, як світло від дзеркала", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "кут падіння дорівнює куту відбиття — точно як у променя світла",
              12.5, GREY, "middle", style="italic")
    # поверхня
    s += rect(150, 240, 600, 16, "#d9d9de", METAL, 1.6)
    s += text(450, 274, "метал / стіна", 10, GREY, "middle")
    # падіння й відбиття
    s += arrow(220, 110, 420, 240, GREEN, 2.4)
    s += text(280, 150, "падає", 10, GREEN, "middle", "bold")
    s += arrow(420, 240, 620, 110, "#b08900", 2.4)
    s += text(560, 150, "відбивається", 10, "#b08900", "middle", "bold")
    s += line(420, 240, 420, 130, GREY, 1.2, dash="3,3")
    s += text(395, 200, "α", 11, INK, "end", "bold")
    s += text(445, 200, "α", 11, INK, "start", "bold")

    s += rect(60, 286, W - 120, 36, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 309, "Тому метал «відбиває» радіо: за металевою стіною — «радіотінь», а відбиття створюють зайві шляхи.",
              11.5, INK, "middle", "bold")
    save("fig-39-3-2-reflection.svg", s)


# ── Рис. 39.3.3 — дифракція (огинання) ───────────────────────────────────────
def fig33_diffraction():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Дифракція: хвиля огинає край і заходить «у тінь»", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "за перешкодою не повна темрява — хвиля загинається за ріг; що довша хвиля, то сильніше",
              12, GREY, "middle", style="italic")
    # перешкода
    s += rect(420, 150, 40, 160, "#e3ded2", "#9a9488", 2)
    # плоскі фронти зліва
    for x in (120, 160, 200):
        s += line(x, 130, x, 300, GREEN, 1.8)
    s += arrow(220, 215, 410, 215, GREEN, 2)
    s += text(230, 122, "фронти хвилі →", 10, GREEN, "start", "bold")
    # загинання за край
    for r in (30, 60, 90):
        s += f'<path d="M 440,150 A {r} {r} 0 0 1 {440-r*0.2:.0f},{150+r:.0f}" fill="none" stroke="{RED}" stroke-width="1.6"/>\n'
    s += text(560, 200, "загинається у «тінь» за краєм", 10, RED, "middle", "bold")
    s += text(520, 290, "зона тіні (сигнал слабший, але є)", 9.5, GREY, "middle", style="italic")

    s += rect(60, 286, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 311, "Тому за рогом будинку зв'язок є (хоч слабший); і саме тому НИЗЬКІ частоти краще «заходять» за перешкоди.",
              11.5, INK, "middle", "bold")
    save("fig-39-3-3-diffraction.svg", s)


# ── Рис. 39.3.4 — проникнення крізь стіни ────────────────────────────────────
def fig34_penetration():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Проникнення крізь стіни: ослаблюється, але проходить", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "нижчі частоти (довші хвилі) проходять крізь стіни легше за вищі",
              12, GREY, "middle", style="italic")
    s += rect(420, 110, 50, 200, "#e3ded2", "#9a9488", 2)
    s += text(445, 100, "стіна", 9.5, GREY, "middle")
    # низька частота — проходить добре
    s += sine(120, 160, 290, 22, 2, "#b08900", 2.6)
    s += sine(480, 160, 280, 18, 2, "#b08900", 2.2)
    s += text(120, 130, "низька f (довга λ):", 11, "#b08900", "start", "bold")
    s += text(620, 138, "проходить майже вся", 9.5, GREEN, "middle", "bold")
    # висока частота — гасне
    s += sine(120, 250, 290, 22, 6, BLUE, 2.6)
    s += sine(480, 250, 280, 8, 6, BLUE, 1.8)
    s += text(120, 230, "висока f (коротка λ):", 11, BLUE, "start", "bold")
    s += text(620, 234, "сильно гасне", 9.5, RED, "middle", "bold")

    s += rect(60, 286, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 311, "Тому Wi-Fi 2.4 ГГц «бере» крізь стіни краще за 5 ГГц — нижча частота проникає легше (деталі §39.4).",
              11.5, INK, "middle", "bold")
    save("fig-39-3-4-penetration.svg", s)


# ── Рис. 39.3.5 — багатопроменевість ─────────────────────────────────────────
def fig35_multipath():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Багатопроменевість: шляхи складаються — і підсилюють чи гасять", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "хвиля доходить кількома шляхами різної довжини; на приймачі вони можуть скластися або відняти",
              12, GREY, "middle", style="italic")
    s += _tower(110, 250, 50, GREEN); s += text(110, 270, "TX", 10, GREEN, "middle", "bold")
    s += _tower(790, 250, 50, BLUE); s += text(790, 270, "RX", 10, BLUE, "middle", "bold")
    s += line(120, 205, 780, 205, GREEN, 2)
    s += text(450, 196, "прямий шлях", 9.5, GREEN, "middle", "bold")
    s += line(120, 210, 450, 320, "#b08900", 2)
    s += line(450, 320, 780, 210, "#b08900", 2)
    s += text(450, 338, "відбитий шлях (довший)", 9.5, "#b08900", "middle", "bold")
    # складання
    s += rect(540, 100, 320, 70, LGREY, GREY, 1.3, 8)
    s += text(700, 124, "у фазі → ПІДСИЛЕННЯ", 10.5, GREEN, "middle", "bold")
    s += text(700, 146, "у протифазі → ГАСІННЯ (завмирання)", 10.5, RED, "middle", "bold")

    s += rect(60, 290, 1, 1, "none", "none", 0)
    save("fig-39-3-5-multipath.svg", s)


# ── Рис. 39.3.6 — поляризація ────────────────────────────────────────────────
def fig36_polarization():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Поляризація: у який бік коливається поле E", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "вертикальна, горизонтальна чи кругова — це напрямок коливань електричного поля",
              12.5, GREY, "middle", style="italic")
    # вертикальна
    s += text(180, 100, "вертикальна", 12, RED, "middle", "bold")
    s += arrow(180, 240, 180, 130, INK, 1.6)
    s += arrow(180, 185, 180, 140, RED, 2.4); s += arrow(180, 185, 180, 230, RED, 2.4)
    s += text(180, 268, "E вгору-вниз", 9.5, INK, "middle")
    # горизонтальна
    s += text(450, 100, "горизонтальна", 12, BLUE, "middle", "bold")
    s += arrow(450, 240, 450, 130, INK, 1.6)
    s += arrow(450, 185, 390, 185, BLUE, 2.4); s += arrow(450, 185, 510, 185, BLUE, 2.4)
    s += text(450, 268, "E вліво-вправо", 9.5, INK, "middle")
    # кругова
    s += text(720, 100, "кругова", 12, GREEN, "middle", "bold")
    s += circle(720, 185, 44, "none", GREEN, 2.4)
    s += f'<path d="M 764,185 A 44 44 0 0 1 720,229" fill="none" stroke="{GREEN}" stroke-width="2.4" marker-end="url(#aGreen)"/>\n'
    s += text(720, 268, "E обертається", 9.5, INK, "middle")

    s += rect(60, 286, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 311, "Антена «налаштована» на свою поляризацію: вертикальний штир випромінює й ловить вертикальну хвилю.",
              11.5, INK, "middle", "bold")
    save("fig-39-3-6-polarization.svg", s)


# ── Рис. 39.3.7 — узгодження поляризації ─────────────────────────────────────
def fig37_pol_match():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Антени мають збігатися поляризацією — інакше великі втрати", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "вертикальна найкраще «чує» вертикальну; перпендикулярна (90°) — майже глуха",
              12, GREY, "middle", style="italic")
    # збіг
    s += rect(70, 92, 360, 170, "#eef6ef", GREEN, 2, 12)
    s += text(250, 116, "збіг (обидві вертикальні)", 12, GREEN, "middle", "bold")
    s += line(160, 230, 160, 150, METAL, 4); s += line(340, 230, 340, 150, METAL, 4)
    s += sine(160, 190, 180, 14, 2, GREEN, 2)
    s += text(250, 252, "✓ максимум сигналу", 11, GREEN, "middle", "bold")
    # неузгодження
    s += rect(470, 92, 380, 170, "#fdeeee", RED, 2, 12)
    s += text(660, 116, "перпендикулярні (90°)", 12, RED, "middle", "bold")
    s += line(560, 230, 560, 150, METAL, 4)
    s += line(700, 195, 800, 195, METAL, 4)
    s += text(660, 240, "✗ майже нічого (велика втрата)", 11, RED, "middle", "bold")
    s += text(660, 256, "втрата ~ cos²(кут)", 9.5, GREY, "middle", style="italic")

    s += rect(60, 286, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 311, "Практика: орієнтуй антени ОДНАКОВО. Поверни приймальну на 90° — і сигнал майже зникне (−20 дБ і більше).",
              11.5, INK, "middle", "bold")
    save("fig-39-3-7-pol-match.svg", s)


# ============================================================================
#  §39.4 — Діапазони: чому різні частоти поводяться по-різному
# ============================================================================

# ── Рис. 39.4.1 — головний компроміс частоти ─────────────────────────────────
def fig41_tradeoff():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 34, "Головний компроміс: частота міняє ВСЕ — дальність, стіни, антену, швидкість", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "та сама хвиля; та підняв частоту — виграв швидкість і малу антену, програв дальність і проникність",
              11.5, GREY, "middle", style="italic")
    ox, oy, axw = 110, 110, 700
    s += arrow(ox, oy, ox + axw, oy, INK, 2)
    s += text(ox, oy - 12, "НИЗЬКА частота (довга λ)", 11, "#b08900", "start", "bold")
    s += text(ox + axw, oy - 12, "ВИСОКА частота (коротка λ)", 11, BLUE, "end", "bold")
    rows = [
        ("дальність", "далеко", "близько", GREEN, RED),
        ("крізь стіни", "проходить", "блокується", GREEN, RED),
        ("розмір антени", "велика", "крихітна", RED, GREEN),
        ("швидкість даних", "мала", "велика", RED, GREEN),
    ]
    yy = oy + 40
    for prop, lo, hi, locol, hicol in rows:
        s += text(ox - 8, yy + 5, prop, 11, INK, "end", "bold")
        s += text(ox + 30, yy + 5, lo, 11.5, locol, "start", "bold")
        s += text(ox + axw - 10, yy + 5, hi, 11.5, hicol, "end", "bold")
        s += line(ox, yy, ox + axw, yy, FAINT, 1)
        yy += 50

    s += rect(60, 330, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 354, "Немає «найкращої» частоти — є компроміс: дальність і проникність ПРОТИ швидкості й розміру.",
              12, INK, "middle", "bold")
    s += text(W / 2, 374, "Усі ці залежності — наслідки одного: довша хвиля краще огинає й проникає (§39.3), але потребує більшої антени (§39.2).",
              10.5, GREY, "middle", style="italic")
    save("fig-39-4-1-tradeoff.svg", s)


# ── Рис. 39.4.2 — дальність і проникність ────────────────────────────────────
def fig42_range():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Дальність і проникність: низька частота «бере» далі й крізь усе", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "довгі хвилі огинають і проникають (§39.3); короткі вимагають прямої видимості",
              12, GREY, "middle", style="italic")
    # низька — широке покриття
    s += text(230, 100, "низька частота", 12, "#b08900", "middle", "bold")
    s += _tower(120, 250, 50, "#b08900")
    s += f'<path d="M 120,210 m -10,0 a 110 80 0 1 0 220,0 a 110 80 0 1 0 -220,0" fill="#fbf3df" fill-opacity="0.5" stroke="#b08900" stroke-width="1.6"/>\n'
    s += rect(200, 200, 14, 50, "#9a9488", "#6b665c", 1)  # перешкода
    s += text(230, 280, "огинає, проходить крізь стіни", 9.5, GREEN, "middle", "bold")
    # висока — вузьке LOS
    s += text(670, 100, "висока частота", 12, BLUE, "middle", "bold")
    s += _tower(560, 250, 50, BLUE)
    s += f'<path d="M 565,210 L 800,170 L 800,250 Z" fill="#e9eefb" fill-opacity="0.6" stroke="{BLUE}" stroke-width="1.6"/>\n'
    s += rect(680, 200, 14, 50, "#9a9488", "#6b665c", 1)
    s += line(694, 215, 720, 215, RED, 2)
    s += text(720, 234, "тінь", 8.5, RED, "start", "bold")
    s += text(670, 280, "лише пряма видимість", 9.5, RED, "middle", "bold")

    s += rect(60, 296, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 321, "Тому LoRa на 433/868 МГц «дострілює» на кілометри крізь забудову, а 5 ГГц ледь крізь сусідню стіну.",
              11.5, INK, "middle", "bold")
    save("fig-39-4-2-range.svg", s)


# ── Рис. 39.4.3 — швидкість даних ────────────────────────────────────────────
def fig43_datarate():
    W, H = 900, 350
    s = header(W, H)
    s += text(W / 2, 34, "Швидкість даних: на вищій частоті більше «місця» під смугу", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "та сама частка спектра у відсотках дає В РАЗИ ширшу смугу на високій частоті → більше даних",
              12, GREY, "middle", style="italic")
    s += rect(120, 110, 300, 90, "#fbf3df", "#b08900", 2, 10)
    s += text(270, 134, "100 МГц", 13, "#b08900", "middle", "bold")
    s += text(270, 158, "1% смуги = 1 МГц", 11.5, INK, "middle", "bold")
    s += text(270, 180, "→ мало даних", 10.5, RED, "middle")
    s += text(450, 158, "vs", 16, GREY, "middle", "bold")
    s += rect(480, 110, 300, 90, "#eef6ef", GREEN, 2, 10)
    s += text(630, 134, "5 ГГц", 13, GREEN, "middle", "bold")
    s += text(630, 158, "1% смуги = 50 МГц", 11.5, INK, "middle", "bold")
    s += text(630, 180, "→ у 50 разів більше", 10.5, GREEN, "middle", "bold")

    s += rect(60, 226, W - 120, 100, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 252, "Більше абсолютної смуги = вища швидкість (натяк на межу Шеннона, §40).",
              12, INK, "middle", "bold")
    s += text(W / 2, 274, "Ось чому відео й швидкий Wi-Fi тягнуться на ВИСОКІ частоти, а далекий IoT — на низькі.",
              11.5, INK, "middle")
    s += text(W / 2, 296, "Низькі частоти просто «тісні»: там фізично мало місця під широкі канали.",
              11, GREY, "middle", style="italic")
    s += text(W / 2, 316, "Тому компроміс «далеко» проти «швидко» — фундаментальний, а не випадковий.",
              10.5, GREY, "middle", style="italic")
    save("fig-39-4-3-datarate.svg", s)


# ── Рис. 39.4.4 — розмір антени (нагадування) ────────────────────────────────
def fig44_antenna():
    W, H = 900, 320
    s = header(W, H)
    s += text(W / 2, 34, "Розмір антени (нагадування з §39.2)", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "низька частота → довга хвиля → велика антена; висока → коротка хвиля → крихітна",
              12.5, GREY, "middle", style="italic")
    items = [("433 МГц", "λ≈70 см", "≈17 см", "#b08900"), ("868 МГц", "λ≈35 см", "≈9 см", "#b08900"),
             ("2.4 ГГц", "λ≈12.5 см", "≈3 см", GREEN), ("5 ГГц", "λ≈6 см", "≈1.5 см", BLUE)]
    x = 90
    for f, lam, ant, col in items:
        s += rect(x, 100, 180, 110, "#fbfbfb", col, 1.8, 10)
        s += text(x + 90, 128, f, 13, col, "middle", "bold")
        s += text(x + 90, 152, lam, 11, INK, "middle")
        s += text(x + 90, 178, "антена " + ant, 11.5, col, "middle", "bold")
        x += 192

    s += rect(60, 228, W - 120, 40, LGREY, GREY, 1.3, 10)
    s += text(W / 2, 253, "За частотою одразу видно розмір антени — і чи влізе вона в корпус пристрою.",
              11.5, INK, "middle", "bold")
    save("fig-39-4-4-antenna.svg", s)


# ── Рис. 39.4.5 — карта діапазонів і застосувань ─────────────────────────────
def fig45_bandmap():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 34, "Карта діапазонів: характер і типове застосування", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "від «далеко й повільно» внизу спектра до «близько й швидко» вгорі",
              12, GREY, "middle", style="italic")
    bands = [
        ("AM / MF", "~1 МГц", "величезна дальність, мало даних", "радіомовлення"),
        ("HF (КХ)", "3–30 МГц", "відбиття від іоносфери → глобально", "далекий зв'язок"),
        ("VHF / UHF", "30 МГц–3 ГГц", "пряма видимість+, помірно", "FM, ТБ, рації"),
        ("433/868 МГц", "ISM", "далеко + крізь стіни, мало даних", "LoRa, далекий IoT"),
        ("2.4 ГГц", "ISM", "помірна дальність і дані", "Wi-Fi, BT, Zigbee"),
        ("5 ГГц", "ISM", "багато даних, мала дальність", "швидкий Wi-Fi"),
        ("мм-хвилі", "24–60 ГГц", "величезні дані, лише в межах кімнати", "5G, радари"),
    ]
    bx, by, rw = 70, 86, 780
    yy = by
    for nm, f, ch, use in bands:
        col = GREEN if "2.4" in nm else ("#b08900" if "433" in nm else INK)
        s += rect(bx, yy, rw, 38, ("#eef6ef" if col == GREEN else "#ffffff"), GREY, 1)
        s += text(bx + 12, yy + 24, nm, 11.5, col, "start", "bold")
        s += text(bx + 150, yy + 24, f, 10, GREY, "start")
        s += text(bx + 250, yy + 24, ch, 10.5, INK, "start")
        s += text(bx + 600, yy + 24, use, 10.5, BLUE, "start", "bold")
        yy += 40

    s += rect(60, by + 7 * 40 + 6, 1, 1, "none", "none", 0)
    save("fig-39-4-5-bandmap.svg", s)


# ── Рис. 39.4.6 — обирай частоту за потребою ─────────────────────────────────
def fig46_pick():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 34, "Обирай частоту за потребою", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "спершу вирішуєш «далеко чи швидко, крізь стіни чи ні» — і частота випливає сама",
              12.5, GREY, "middle", style="italic")
    rows = [
        ("далеко + мало даних (давач у полі)", "→ 433 / 868 МГц (LoRa)", "#b08900"),
        ("крізь стіни в домі, помірні дані", "→ 2.4 ГГц (Wi-Fi/BT)", GREEN),
        ("багато даних, пристрій поруч", "→ 5 ГГц (швидкий Wi-Fi)", BLUE),
        ("глобальна дальність без інфраструктури", "→ HF / супутник", INK),
    ]
    yy = 96
    for case, pick, col in rows:
        s += rect(110, yy, 680, 44, ("#eef6ef" if col == GREEN else "#fbfbfb"), col, 1.8, 10)
        s += text(130, yy + 28, case, 12, INK, "start", "bold")
        s += text(540, yy + 28, pick, 12, col, "start", "bold")
        yy += 54

    s += rect(60, 318, 1, 1, "none", "none", 0)
    save("fig-39-4-6-pick.svg", s)


# ── Рис. 39.4.7 — єдиний континуум ───────────────────────────────────────────
def fig47_continuum():
    W, H = 900, 300
    s = header(W, H)
    s += text(W / 2, 34, "Одна шкала: «далеко-повільно-велика антена» ↔ «близько-швидко-мала»", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "усе радіо — це рух по одній осі частоти; кожен крок угору міняє чотири властивості разом",
              11.5, GREY, "middle", style="italic")
    ox, oy, axw = 90, 150, 720
    # градієнтна смуга
    for i in range(60):
        t = i / 60
        col = "#%02x%02x%02x" % (int(202 - t * 170), int(162 + t * 0), int(74 + t * 100))
        s += rect(ox + t * axw, oy - 14, axw / 60 + 1, 28, col, "none", 0)
    s += rect(ox, oy - 14, axw, 28, "none", GREY, 1.4)
    s += text(ox, oy + 40, "низька f", 12, "#b08900", "start", "bold")
    s += text(ox, oy + 58, "далеко · повільно · велика антена · крізь стіни", 9.5, INK, "start")
    s += text(ox + axw, oy + 40, "висока f", 12, BLUE, "end", "bold")
    s += text(ox + axw, oy + 58, "близько · швидко · крихітна антена · пряма видимість", 9.5, INK, "end")

    s += rect(60, 240, W - 120, 44, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 265, "Запам'ятай цю вісь — і про будь-яку частоту одразу знатимеш її «характер».",
              12, INK, "middle", "bold")
    save("fig-39-4-7-continuum.svg", s)


# ============================================================================
#  §39.5 — Потужність і децибели (чому логарифмічна шкала)
# ============================================================================

# ── Рис. 39.5.1 — величезний діапазон потужностей ────────────────────────────
def fig51_range():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Чому логарифм: потужності радіо різняться в ТРИЛЬЙОНИ разів", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "передавач — близько вата, чутливість приймача — піковати; лінійні числа тут незручні",
              12, GREY, "middle", style="italic")
    ox, oy, axw = 110, 180, 700
    s += line(ox, oy, ox + axw, oy, INK, 2)
    marks = [(-13, "10⁻¹³ Вт", "чутливість RX"), (-9, "10⁻⁹", ""), (-6, "10⁻⁶", "1 мкВт"),
             (-3, "10⁻³", "1 мВт"), (0, "1 Вт", "передавач")]
    for p, lab, who in marks:
        x = ox + axw * (p + 13) / 13
        s += line(x, oy, x, oy - 7, INK, 1.4)
        s += text(x, oy + 18, lab, 9.5, GREY, "middle")
        if who:
            s += text(x, oy - 16, who, 9.5, (GREEN if "RX" in who else RED), "middle", "bold")
    s += text(ox + axw / 2, oy + 50, "розмах ≈ 13 порядків (× 10 000 000 000 000)", 12, RED, "middle", "bold")

    s += rect(60, 256, W - 120, 70, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 280, "Записувати «0.000000000001 Вт» незручно й помилконебезпечно. Логарифм стискає це в зручні числа.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 302, "Тому в радіо все міряють у ДЕЦИБЕЛАХ — логарифмічних відношеннях.",
              11.5, INK, "middle")
    s += text(W / 2, 320, "(Та сама логіка, що й логарифмічна шкала гучності звуку.)", 10.5, GREY, "middle", style="italic")
    save("fig-39-5-1-range.svg", s)


# ── Рис. 39.5.2 — dB = логарифмічне відношення ───────────────────────────────
def fig52_db_ratio():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Децибел (dB) — це ВІДНОШЕННЯ в логарифмічній шкалі", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "dB = 10·log₁₀(P₂/P₁); запам'ятай кілька орієнтирів — і переведеш будь-яке відношення",
              12, GREY, "middle", style="italic")
    s += text(W / 2, 96, "dB = 10 · log₁₀ ( P₂ / P₁ )", 18, INK, "middle", "bold")
    bx, by, rw = 200, 122, 500
    s += rect(bx, by, rw, 32, "#f0f0f0", GREY, 1.3, 6)
    s += text(bx + 16, by + 22, "децибели", 11.5, INK, "start", "bold")
    s += text(bx + 280, by + 22, "у скільки разів", 11.5, INK, "start", "bold")
    rows = [("+3 dB", "≈ × 2 (удвічі більше)", GREEN), ("+10 dB", "× 10", GREEN),
            ("+20 dB", "× 100", GREEN), ("0 dB", "× 1 (без зміни)", GREY),
            ("−3 dB", "≈ ÷ 2 (удвічі менше)", RED), ("−10 dB", "÷ 10", RED)]
    yy = by + 32
    for d, r, col in rows:
        s += rect(bx, yy, rw, 34, "#ffffff", GREY, 1)
        s += text(bx + 16, yy + 22, d, 12.5, col, "start", "bold")
        s += text(bx + 280, yy + 22, r, 11.5, INK, "start")
        yy += 34

    s += rect(60, 348, W - 120, 1, "none", "none", 0)
    save("fig-39-5-2-db-ratio.svg", s)


# ── Рис. 39.5.3 — чому логарифм: множення → додавання ────────────────────────
def fig53_why_log():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Головна зручність: множення стає ДОДАВАННЯМ", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "у разах довелося б множити; у децибелах підсилення й втрати просто ДОДАЮТЬ",
              12, GREY, "middle", style="italic")
    # у разах
    s += text(140, 110, "у разах:", 12, INK, "start", "bold")
    s += text(450, 114, "× 10  ·  ÷ 2  ·  × 4   =   × 20", 14, INK, "middle", "bold")
    s += text(450, 134, "(підсилювач, кабель, антена)", 9.5, GREY, "middle")
    # у дБ
    s += rect(120, 160, 660, 60, LGRN, GREEN, 1.8, 10)
    s += text(140, 184, "у децибелах:", 12, GREEN, "start", "bold")
    s += text(460, 190, "+10 dB  −3 dB  +6 dB   =   +13 dB", 15, INK, "middle", "bold")
    s += text(460, 210, "просто додаємо — і одразу маємо підсумок", 9.5, GREY, "middle")

    s += rect(60, 244, W - 120, 80, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 268, "Уся радіолінія — це ланцюг підсилень (+) і втрат (−); у дБ підсумок — звичайна сума.",
              12, INK, "middle", "bold")
    s += text(W / 2, 290, "+13 dB = +10 +3 = ×10 ×2 = ×20 — і навпаки. Складати в умі набагато простіше, ніж множити.",
              11.5, INK, "middle")
    s += text(W / 2, 310, "Саме тому бюджет радіолінії (§40.6) рахують у дБ — це проста арифметика додавання.",
              11, GREY, "middle", style="italic")
    save("fig-39-5-3-why-log.svg", s)


# ── Рис. 39.5.4 — dBm: абсолютна потужність ──────────────────────────────────
def fig54_dbm():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "dBm — абсолютна потужність відносно 1 мілівата", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "0 dBm = 1 мВт; далі та сама шкала «+10 = ×10», лише прив'язана до конкретної потужності",
              12, GREY, "middle", style="italic")
    ox, oy, axh = 450, 300, 200
    s += line(ox, oy, ox, oy - axh, INK, 2)
    ladder = [("+30 dBm", "1 Вт", RED), ("+20 dBm", "100 мВт", "#b08900"), ("+10 dBm", "10 мВт", "#b08900"),
              ("0 dBm", "1 мВт", INK), ("−30 dBm", "1 мкВт", BLUE), ("−60 dBm", "1 нВт", BLUE),
              ("−90 dBm", "1 пВт (≈ чутливість RX)", GREEN)]
    for i, (d, p, col) in enumerate(ladder):
        y = oy - axh * i / (len(ladder) - 1)
        s += line(ox - 6, y, ox + 6, y, INK, 1.4)
        s += text(ox - 14, y + 4, d, 11.5, col, "end", "bold")
        s += text(ox + 14, y + 4, p, 11, INK, "start")

    s += rect(60, 316, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 341, "Маленька «m» = «відносно 1 мВт». Передавач +20 dBm = 100 мВт; чутливий приймач ловить аж −90 dBm.",
              11.5, INK, "middle", "bold")
    save("fig-39-5-4-dbm.svg", s)


# ── Рис. 39.5.5 — правило трійок і десяток ───────────────────────────────────
def fig55_3and10():
    W, H = 900, 320
    s = header(W, H)
    s += text(W / 2, 34, "Правило «трійок і десяток»: будуй будь-яке відношення", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "тільки дві цеглинки: +3 dB ≈ ×2, +10 dB = ×10 — з них складеш усе в умі",
              12.5, GREY, "middle", style="italic")
    blocks = [("+3 dB", "×2", GREEN), ("+10 dB", "×10", GREEN)]
    x = 230
    for d, r, col in blocks:
        s += rect(x, 92, 200, 60, "#eef6ef", col, 2, 10)
        s += text(x + 100, 120, d + "  =  " + r, 15, col, "middle", "bold")
        x += 250
    examples = [
        ("+13 dB", "+10 +3", "×10 ×2 = ×20"),
        ("+23 dB", "+10 +10 +3", "×200"),
        ("−7 dB", "−10 +3", "÷10 ×2 = ÷5"),
    ]
    yy = 184
    for d, build, res in examples:
        s += text(180, yy, d, 13, INK, "start", "bold")
        s += text(290, yy, "= " + build, 11.5, GREY, "start")
        s += text(520, yy, "→ " + res, 12.5, GREEN, "start", "bold")
        yy += 30

    s += rect(60, 282, W - 120, 1, "none", "none", 0)
    save("fig-39-5-5-3and10.svg", s)


# ── Рис. 39.5.6 — дБ скрізь ──────────────────────────────────────────────────
def fig56_db_everywhere():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 34, "Децибели — спільна мова всього радіотракту", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "підсилення, втрати, шум, виграш антени — усе ВІДНОШЕННЯ, тож усе зручно в дБ",
              12.5, GREY, "middle", style="italic")
    items = [
        ("підсилення", "+дБ", "підсилювач додає", GREEN),
        ("втрати", "−дБ", "кабель, стіна, відстань", RED),
        ("SNR", "дБ", "сигнал / шум", BLUE),
        ("виграш антени", "dBi", "спрямованість антени", "#b08900"),
    ]
    x = 60
    for nm, unit, desc, col in items:
        s += rect(x, 96, 200, 120, "#fbfbfb", col, 2, 10)
        s += text(x + 100, 126, nm, 12.5, col, "middle", "bold")
        s += text(x + 100, 152, unit, 16, INK, "middle", "bold")
        s += text(x + 100, 180, desc, 9.3, GREY, "middle")
        x += 207

    s += rect(60, 236, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 260, "Раз усе — відношення, увесь шлях сигналу описують однією мовою дБ і просто складають.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 282, "dBi — виграш антени відносно ідеальної всебічної; теж логарифмічне відношення (§41).",
              10.5, GREY, "middle", style="italic")
    save("fig-39-5-6-db-everywhere.svg", s)


# ── Рис. 39.5.7 — практичне читання специфікації ─────────────────────────────
def fig57_practical():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Практика: читаємо радіоспецифікацію в дБ", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "потужність передавача й чутливість приймача в dBm — а їхня різниця і є «запас» на втрати",
              12, GREY, "middle", style="italic")
    s += rect(90, 96, 320, 70, "#eef6ef", GREEN, 2, 10)
    s += text(250, 122, "передавач: +20 dBm", 13, GREEN, "middle", "bold")
    s += text(250, 144, "(= 100 мВт)", 10, GREY, "middle")
    s += rect(490, 96, 320, 70, "#e9eefb", BLUE, 2, 10)
    s += text(650, 122, "чутливість: −95 dBm", 13, BLUE, "middle", "bold")
    s += text(650, 144, "(найслабший, що чує)", 10, GREY, "middle")
    s += text(W / 2, 200, "запас на всі втрати = +20 − (−95) = 115 дБ", 16, INK, "middle", "bold")
    s += text(W / 2, 224, "стільки децибел можна «втратити» по дорозі, поки зв'язок ще живий", 11, GREY, "middle", style="italic")

    s += rect(60, 250, W - 120, 70, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 274, "Цей «запас» — основа бюджету радіолінії: TX + виграші − втрати ≥ чутливість RX.",
              12, INK, "middle", "bold")
    s += text(W / 2, 296, "Уся арифметика — додавання дБ; саме її ми й складемо в бюджет лінії у §40.6.",
              11, INK, "middle")
    s += text(W / 2, 314, "Тому вміти читати dBm/дБ — обов'язкова навичка для будь-якого радіопроєкту.",
              10.5, GREY, "middle", style="italic")
    save("fig-39-5-7-practical.svg", s)


# ============================================================================
#  §39.6 — Загасання у просторі (чому сигнал слабшає)
# ============================================================================

# ── Рис. 39.6.1 — куля, що розпливається ─────────────────────────────────────
def fig61_sphere():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Чому сигнал слабшає навіть у порожнечі: куля розпливається", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "та сама потужність розмазується по дедалі більшій сфері (площа 4πr²) → густина падає як 1/r²",
              11.5, GREY, "middle", style="italic")
    cx, cy = 200, 210
    s += circle(cx, cy, 10, RED, RED, 0)
    s += text(cx, cy - 18, "TX", 11, RED, "middle", "bold")
    for r, lab in [(80, "r"), (160, "2r"), (240, "3r")]:
        s += f'<path d="M {cx},{cy-r} A {r} {r} 0 0 1 {cx},{cy+r}" fill="none" stroke="{GREEN}" stroke-width="1.8"/>\n'
        s += text(cx + r * 0.72, cy - r * 0.72, lab, 11, GREEN, "middle", "bold")
    # клаптик-приймач на дальній сфері
    s += rect(cx + 232, cy - 12, 18, 24, "#e9eefb", BLUE, 1.6)
    s += text(cx + 280, cy + 4, "RX ловить", 10, BLUE, "start", "bold")
    s += text(cx + 280, cy + 18, "крихітний клаптик", 9, GREY, "start")

    s += rect(60, 300, W - 120, 60, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 324, "Це той самий закон оберненого квадрата, що й у Кулона/поля (§1.2): вплив розбавляється по сфері.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 346, "Жодного поглинання — лише геометрія: що далі, то тоншим клаптиком хвилі дістається приймачу.",
              11, GREY, "middle", style="italic")
    save("fig-39-6-1-sphere.svg", s)


# ── Рис. 39.6.2 — обернений квадрат: 2× далі = −6 дБ ─────────────────────────
def fig62_inverse_square():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 34, "Закон оберненого квадрата: подвоїв відстань — у 4 рази менше", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "густина потужності ~ 1/r²: ×2 відстані → ÷4 потужності → це рівно −6 дБ",
              12, GREY, "middle", style="italic")
    bars = [("r", 1.0, 160, GREEN), ("2r", 0.25, 40, "#b08900"), ("3r", 0.111, 18, RED)]
    x0 = 200
    for i, (lab, frac, h, col) in enumerate(bars):
        x = x0 + i * 200
        s += rect(x, 230 - h, 80, h, ("#eef6ef" if col == GREEN else "#fbfbfb"), col, 1.8, 4)
        s += text(x + 40, 250, lab, 12, INK, "middle", "bold")
        s += text(x + 40, 230 - h - 8, "%.0f%%" % (frac * 100) if frac >= 0.1 else "11%", 11, col, "middle", "bold")
    s += text(x0 + 100, 130, "−6 дБ", 13, INK, "middle", "bold")
    s += arrow(x0 + 90, 150, x0 + 200, 150, INK, 1.6)
    s += text(x0 + 300, 130, "ще −3.5 дБ", 12, INK, "middle", "bold")

    s += rect(60, 270, W - 120, 50, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 294, "Кожне подвоєння відстані «з'їдає» 6 дБ. У 10 разів далі → −20 дБ (×100 слабше).",
              12, INK, "middle", "bold")
    s += text(W / 2, 313, "І це лише геометрія порожнечі — стіни й дощ додають втрат зверху.", 10.5, GREY, "middle", style="italic")
    save("fig-39-6-2-inverse-square.svg", s)


# ── Рис. 39.6.3 — частота теж збільшує втрати ────────────────────────────────
def fig63_frequency():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Чому вища частота = більші втрати у просторі", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "приймальна антена «зачерпує» площу ~λ²; коротша хвиля — менший зачерп — менше потужності",
              12, GREY, "middle", style="italic")
    # низька — велика «лійка»
    s += text(230, 100, "низька f (довга λ)", 12, "#b08900", "middle", "bold")
    s += f'<path d="M 130,150 L 330,130 L 330,230 L 130,210 Z" fill="#fbf3df" stroke="#b08900" stroke-width="1.6"/>\n'
    s += text(230, 260, "велика ефективна площа → ловить більше", 9.5, GREEN, "middle", "bold")
    # висока — мала «лійка»
    s += text(670, 100, "висока f (коротка λ)", 12, BLUE, "middle", "bold")
    s += f'<path d="M 600,170 L 760,160 L 760,210 L 600,200 Z" fill="#e9eefb" stroke="{BLUE}" stroke-width="1.6"/>\n'
    s += text(670, 260, "мала ефективна площа → ловить менше", 9.5, RED, "middle", "bold")

    s += rect(60, 280, W - 120, 50, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 304, "Тому втрати у вільному просторі ростуть і з відстанню, і з частотою: FSPL = (4π·d / λ)².",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 323, "Це ще одна причина, чому 5 ГГц «бере» ближче за 2.4 ГГц навіть без стін.", 10.5, GREY, "middle", style="italic")
    save("fig-39-6-3-frequency.svg", s)


# ── Рис. 39.6.4 — числа: FSPL на 2.4 ГГц ─────────────────────────────────────
def fig64_numbers():
    W, H = 900, 350
    s = header(W, H)
    s += text(W / 2, 34, "Числа: втрати у вільному просторі на 2.4 ГГц", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "навіть без перешкод відстань «з'їдає» десятки децибел — це найбільший пожирач бюджету",
              12, GREY, "middle", style="italic")
    bx, by, rw = 200, 96, 500
    s += rect(bx, by, rw, 32, "#f0f0f0", GREY, 1.3, 6)
    s += text(bx + 16, by + 22, "відстань", 12, INK, "start", "bold")
    s += text(bx + 280, by + 22, "втрати (приблизно)", 12, INK, "start", "bold")
    rows = [("1 м", "≈ 40 дБ"), ("10 м", "≈ 60 дБ"), ("100 м", "≈ 80 дБ"), ("1 км", "≈ 100 дБ")]
    yy = by + 32
    for d, loss in rows:
        s += rect(bx, yy, rw, 38, "#ffffff", GREY, 1)
        s += text(bx + 16, yy + 25, d, 13, INK, "start", "bold")
        s += text(bx + 280, yy + 25, loss, 13, RED, "start", "bold")
        yy += 38

    s += rect(60, 290, W - 120, 50, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 314, "Кожне ×10 відстані додає ≈20 дБ втрат. На 100 м уже −80 дБ — і це ще в чистому полі.",
              12, INK, "middle", "bold")
    s += text(W / 2, 333, "Пригадай запас 115 дБ із §39.5: відстань легко з'їдає більшу його частину.", 10.5, GREY, "middle", style="italic")
    save("fig-39-6-4-numbers.svg", s)


# ── Рис. 39.6.5 — поза вільним простором ─────────────────────────────────────
def fig65_beyond():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Поза порожнечею: до геометрії додаються ще втрати", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "базове розпливання неминуче; а реальний світ накладає зверху стіни, дощ, листя, тіло",
              12, GREY, "middle", style="italic")
    # стек втрат
    base = 300
    losses = [("розпливання (1/r²)", 120, GREEN, "неминуче — геометрія"),
              ("стіна", 40, "#b08900", "−кілька…десятки дБ кожна"),
              ("дощ / листя", 24, BLUE, "поглинають, надто на 2.4+"),
              ("тіло / метал поруч", 20, RED, "затуляють і відбивають")]
    x = 130
    acc = 0
    for nm, h, col, desc in losses:
        s += rect(x, base - acc - h, 110, h, col, "#333", 1.2)
        acc += h
        x = x  # stacked vertically
    s += text(185, base + 20, "сумарні втрати", 11, INK, "middle", "bold")
    # легенда
    ly = 110
    for nm, h, col, desc in losses:
        s += rect(360, ly, 16, 16, col, "#333", 1)
        s += text(384, ly + 13, nm + " — " + desc, 10.5, INK, "start")
        ly += 30

    s += rect(60, 296, W - 120, 1, "none", "none", 0)
    save("fig-39-6-5-beyond.svg", s)


# ── Рис. 39.6.6 — втрати домінують у бюджеті ─────────────────────────────────
def fig66_dominates():
    W, H = 900, 320
    s = header(W, H)
    s += text(W / 2, 34, "Загасання — найбільший пожирач бюджету радіолінії", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "із запасу ~115 дБ (§39.5) сама лише відстань забирає левову частку",
              12.5, GREY, "middle", style="italic")
    bx, by, bw = 120, 110, 660
    s += rect(bx, by, bw, 44, "#f4f4f4", GREY, 1.4, 6)
    s += text(bx - 8, by + 28, "115 дБ запасу:", 11, INK, "end", "bold")
    # сегменти
    parts = [("розпливання (відстань)", 0.62, RED), ("стіни/завмирання", 0.18, "#b08900"),
             ("запас на надійність", 0.20, GREEN)]
    x = bx
    for nm, frac, col in parts:
        w = bw * frac
        s += rect(x, by, w, 44, ("#fdeeee" if col == RED else ("#fbf3df" if col == "#b08900" else "#eef6ef")), col, 1.6)
        s += text(x + w / 2, by + 22, nm, 9.5, col, "middle", "bold")
        s += text(x + w / 2, by + 37, "%.0f%%" % (frac * 100), 9, GREY, "middle")
        x += w

    s += rect(60, 196, W - 120, 100, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 222, "Ось чому дальність обмежена: відстань поглинає більшість бюджету, лишаючи мало на решту.",
              12, INK, "middle", "bold")
    s += text(W / 2, 244, "І чому потрібні чутливі приймачі: що глибший «мінус» вони чують, то більший запас на втрати.",
              11.5, INK, "middle")
    s += text(W / 2, 266, "Повний підрахунок усіх «плюсів і мінусів» — бюджет радіолінії — складемо у §40.6.",
              11, GREY, "middle", style="italic")
    save("fig-39-6-6-dominates.svg", s)


# ── Рис. 39.6.7 — як збільшити дальність ─────────────────────────────────────
def fig67_extend():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 34, "Як подолати загасання: чотири важелі дальності", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "усе зводиться до збільшення бюджету в дБ — більше «плюсів» або менше «мінусів»",
              12.5, GREY, "middle", style="italic")
    levers = [
        ("більше потужності TX", "+дБ на старті", "обмежено законом і енергією", "#b08900"),
        ("кращі антени", "+dBi з обох боків", "спрямованість, виграш", GREEN),
        ("нижча частота", "менше FSPL + проникність", "ціна — менше даних", BLUE),
        ("нижча швидкість", "краща чутливість RX", "повільніше = далі (LoRa)", RED),
    ]
    x = 55
    for nm, gain, cost, col in levers:
        s += rect(x, 96, 200, 130, "#fbfbfb", col, 2, 10)
        s += text(x + 100, 124, nm, 11.5, col, "middle", "bold")
        s += text(x + 100, 150, gain, 10.5, INK, "middle", "bold")
        s += text(x + 100, 180, cost, 9, GREY, "middle")
        x += 207

    s += rect(60, 244, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 268, "Дальність — не магія, а арифметика дБ: підніми бюджет — і сигнал дотягнеться далі.",
              12, INK, "middle", "bold")
    s += text(W / 2, 290, "Цікаво: «повільніше = далі» — основа LoRa; знизивши швидкість, приймач чує глибший мінус.",
              10.5, GREY, "middle", style="italic")
    save("fig-39-6-7-extend.svg", s)


if __name__ == "__main__":
    # — історія (секція 0) —
    fig_timeline()
    fig_maxwell()
    fig_hertz_apparatus()
    fig_like_light()
    fig_no_use()
    # — §39.1 —
    fig11_structure()
    fig12_accelerating()
    fig13_leapfrog()
    fig14_transverse()
    fig15_no_medium()
    fig16_energy()
    fig17_antenna()
    # — §39.2 —
    fig21_freq_vs_wave()
    fig22_c_eq()
    fig23_bands()
    fig24_high_low()
    fig25_antenna_size()
    fig26_spectrum()
    fig27_practical()
    # — §39.3 —
    fig31_paths()
    fig32_reflection()
    fig33_diffraction()
    fig34_penetration()
    fig35_multipath()
    fig36_polarization()
    fig37_pol_match()
    # — §39.4 —
    fig41_tradeoff()
    fig42_range()
    fig43_datarate()
    fig44_antenna()
    fig45_bandmap()
    fig46_pick()
    fig47_continuum()
    # — §39.5 —
    fig51_range()
    fig52_db_ratio()
    fig53_why_log()
    fig54_dbm()
    fig55_3and10()
    fig56_db_everywhere()
    fig57_practical()
    # — §39.6 —
    fig61_sphere()
    fig62_inverse_square()
    fig63_frequency()
    fig64_numbers()
    fig65_beyond()
    fig66_dominates()
    fig67_extend()
    print("done.")
