# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 13.1 — «Дисплеї і дотик як компоненти» (Модуль 13).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи нумеруються посекційно
(Рис. M.R.T.k) у тексті; для історії до розділу — тема 0 (Рис. 13.1.0.k).

Скрипт нарощується по ітераціях: кожна тема додає свої функції-фігури.
Допоміжні функції — спільні з рештою розділів курсу (копія, щоб loop'и не ділили файлів).
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра ─────────────────────────────────────────────────────────────────
RED   = "#c0271e"   # додатний (+)
BLUE  = "#1f47b5"   # від'ємний (−)
GREEN = "#1f8a3b"   # поле / світло проходить
INK   = "#1b1b1b"   # основний текст/лінії
GREY  = "#8a8a8a"   # допоміжне
FAINT = "#e4e4e4"   # дуже бліде тло
GLASS = "#a9c8dd"   # скло
MILK  = "#cfd4d8"   # молочне розсіяння
DARK  = "#33373b"   # «темний» піксель
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


def plus(cx, cy, r=12, color=RED, w=2.5):
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w)
            + line(cx, cy - r * 0.55, cx, cy + r * 0.55, color, w))


def minus(cx, cy, r=12, color=BLUE, w=2.5):
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w))


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── локальні помічники розділу: молекула-паличка, поляризатор ────────────────
def mol(cx, cy, ang_deg, L=10.5, color=INK, w=4.6):
    """Стрижнеподібна молекула рідкого кристала — відрізок під кутом ang_deg."""
    a = math.radians(ang_deg)
    dx, dy = L * math.cos(a), L * math.sin(a)
    return line(cx - dx, cy - dy, cx + dx, cy + dy, color, w)


def moldot(cx, cy, r=3.0, color=INK):
    """Молекула «торцем до глядача» (стоїть уздовж погляду/поля) — крапка з обідком."""
    return circle(cx, cy, r, color, color, 1) + circle(cx, cy, r + 2.4, "none", color, 1.4)


def polarizer(x, y, w, h, axis, label):
    """Поляризатор: блок зі штрихуванням уздовж осі пропускання + підпис осі.
    axis: 'h' (↔) або 'v' (↕)."""
    out = rect(x, y, w, h, "#f3f4f6", GREY, 1.6, 3)
    if axis == "h":
        n = max(3, int(h // 7))
        for i in range(n):
            yy = y + h * (i + 0.5) / n
            out += line(x + 4, yy, x + w - 4, yy, GREY, 1.1)
        out += text(x + w + 8, y + h / 2 + 5, "↔", 18, INK, "start", "bold")
    else:
        n = max(3, int(w // 7))
        for i in range(n):
            xx = x + w * (i + 0.5) / n
            out += line(xx, y + 4, xx, y + h - 4, GREY, 1.1)
        out += text(x + w + 8, y + h / 2 + 5, "↕", 18, INK, "start", "bold")
    if label:
        out += text(x + w / 2, y - 6, label, 11.5, GREY, "middle")
    return out


def glassplate(x, y, w, label=None, side="top"):
    """Скляна пластина з прозорим електродом (тонка смуга)."""
    out = rect(x, y, w, 9, GLASS, "#5d7e93", 1.4, 2)
    if label:
        ly = y - 5 if side == "top" else y + 22
        out += text(x + w / 2, ly, label, 11, "#5d7e93", "middle")
    return out


def ellipse(cx, cy, rx, ry, fill="none", stroke=INK, w=2):
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n')


def eye(cx, cy, look=1, color=INK):
    """Око: мигдалеподібний контур + зіниця; look=+1 дивиться вниз, −1 вгору."""
    return (ellipse(cx, cy, 16, 9, "#ffffff", color, 2)
            + circle(cx, cy + look * 2, 4.5, color, color, 1))


# ── Рис. 13.1.0.1 — вертикальний таймлайн історії рідкокристалічного дисплея ──
def fig_timeline():
    W, H = 900, 760
    s = header(W, H)
    s += text(W / 2, 36, "Рідкий кристал → дисплей: ланцюг від ботаніки до годинника", 20, INK, "middle", "bold")
    s += text(W / 2, 57, "наука була готова за 70 років до приладу; синім — те, що сталося ПОЗА RCA",
              12.5, GREY, "middle", style="italic")
    spine = 250
    top, bot = 92, H - 30
    s += line(spine, top, spine, bot, GREY, 3)
    # faint=True → подія поза RCA (передісторія науки або вже втеча технології)
    nodes = [
        ("1888", "Райнітцер / Reinitzer", "Холестерилбензоат має ДВІ точки плавлення — каламутний проміжний стан", True),
        ("1889", "Леманн / Lehmann", "Це «рідкий кристал»: тече як рідина, а світло заломлює як кристал", True),
        ("1911", "Можен / Mauguin", "Закручений шар нематика повертає площину поляризації світла", True),
        ("1962", "Вільямс / Williams · RCA", "Електричне поле збурює нематик у смуги-домени — є електрооптика!", False),
        ("1968", "Гайльмаєр / Heilmeier · RCA", "Динамічне розсіяння: прозоре скло мутніє від струму — ПЕРШИЙ LCD", False),
        ("1970", "Гельфріх / Helfrich", "Іде з RCA до Roche: ідею «закрученого нематика» в RCA зустріли байдуже", True),
        ("1971", "Шадт+Гельфріх · Ферґасон", "Twisted nematic (TN): польовий ефект, копійки енергії — оце й переможе", True),
        ("1973", "Sharp · Seiko · Японія", "Калькулятор і годинник на LCD — виробництво їде в Азію", True),
        ("1976", "RCA продає LC-бізнес", "Винахід остаточно йде з компанії, що його породила", False),
    ]
    n = len(nodes)
    for i, (yr, who, q, away) in enumerate(nodes):
        y = top + 24 + (bot - top - 46) * i / (n - 1)
        col = BLUE if away else INK
        if i == 4:  # Гайльмаєр 1968 — кульмінація
            s += circle(spine, y, 10.5, RED, RED, 3)
            s += circle(spine, y, 5, "#fff", "#fff", 0)
        else:
            s += circle(spine, y, 7, "#fff", col, 2.6)
        s += text(spine - 22, y + 5, yr, 13, GREY, "end", "bold")
        s += text(spine + 26, y - 3, who, 15, (RED if i == 4 else col), "start", "bold")
        s += text(spine + 26, y + 16, q, 12.3, INK if not away else "#4a5a86", "start", style="italic")
    s += text(W / 2, H - 8,
              "Іронія: RCA зробила перший дисплей (1968) і випустила з рук обидві ключові ідеї — DSM і TN.",
              12.5, GREY, "middle", style="italic")
    save("fig-13-1-0-1-timeline.svg", s)


# ── Рис. 13.1.0.2 — динамічне розсіяння (DSM): порядок → каламуть ─────────────
def fig_dsm():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 34, "Динамічне розсіяння (DSM) — те, що зробив Гайльмаєр у RCA", 19, INK, "middle", "bold")
    s += text(W / 2, 55, "струм ганяє іони → турбулентність ламає порядок → прозоре скло мутніє",
              12.5, GREY, "middle", style="italic")
    yt, yb = 110, 290          # межі шару рідкого кристала
    rows = [140, 180, 220, 255]

    def cell(cx, on):
        out = ""
        x0, x1 = cx - 118, cx + 118
        # каламутне (молочне) тло шару — лише в увімкненому стані, ПІД молекулами
        if on:
            out += rect(x0 + 3, yt + 1, (x1 - x0) - 6, (yb - yt) - 2, MILK, "none", 0, 0)
        # скляні пластини з прозорими електродами
        out += glassplate(x0, yt - 10, x1 - x0)
        out += glassplate(x0, yb + 1, x1 - x0)
        # падаюче світло знизу (в обох станах світло входить однакове)
        for xx in (cx - 64, cx - 21, cx + 21, cx + 64):
            out += arrow(xx, H - 64, xx, yb + 14, GREEN, 2.2)
        out += text(cx, H - 48, "падаюче світло", 11.5, GREEN, "middle")
        if not on:
            for yy in rows:
                for cxx in range(-3, 4):
                    out += mol(cx + cxx * 30, yy, 0, 12, INK, 4.6)
            out += text(cx, 84, "ПРОЗОРО", 16, GREEN, "middle", "bold")
            out += text(cx, yb + 30, "U = 0 — порядок", 12, GREY, "middle")
        else:
            out += plus(x0 + 15, yt - 5.5, 8.5, RED)
            out += minus(x0 + 15, yb + 5.5, 8.5, BLUE)
            out += arrow(x0 + 30, yb - 8, x1 - 18, yt + 10, BLUE, 1.5, "5 4")
            angles = [18, -40, 70, -12, 52, -64, 8, 80, -30, 40, -54, 24, 66, -8, 36, -72, 60, -22, 48, -68]
            k = 0
            for yy in rows:
                for cxx in range(-3, 4):
                    out += mol(cx + cxx * 30, yy, angles[k % len(angles)], 10.5, INK, 4.6)
                    k += 1
            out += text(cx, 84, "МОЛОЧНО-БІЛО", 16, "#6f767b", "middle", "bold")
            out += text(cx, yb + 30, "U > 0 — потік іонів (СТРУМ)", 12, BLUE, "middle")
        out += rect(x0, yt, x1 - x0, yb - yt, "none", FAINT, 1.4, 0)
        return out

    s += cell(212, False)
    s += cell(608, True)
    s += line(410, 78, 410, 320, FAINT, 1.4, "4 5")
    s += text(W / 2, 406,
              "DSM світить струмом і дає мутно-білі знаки на темному тлі; енергії — багато. Це був глухий кут.",
              12.5, GREY, "middle", style="italic")
    save("fig-13-1-0-2-dsm.svg", s)


# ── Рис. 13.1.0.3 — twisted nematic (TN): закрут проводить світло ────────────
def fig_tn():
    W, H = 820, 480
    s = header(W, H)
    s += text(W / 2, 34, "Twisted nematic (TN) — ідея, що вийшла з RCA за двері й перемогла", 19, INK, "middle", "bold")
    s += text(W / 2, 55, "90° закрут веде поляризацію крізь схрещені поляризатори; поле випрямляє закрут",
              12.5, GREY, "middle", style="italic")
    yan, ypo = 104, 316            # аналізатор (верх) і поляризатор (низ)
    yt, yb = 132, 300             # межі шару (світло йде знизу вгору)
    rows = [292, 253, 214, 175, 136]   # 5 шарів, знизу вгору

    def cell(cx, on):
        out = ""
        x0, x1 = cx - 92, cx + 92
        # схрещені поляризатори: низ ↔, верх ↕
        out += polarizer(x0, ypo, x1 - x0, 14, "h", "")
        out += polarizer(x0, yan, x1 - x0, 14, "v", "")
        # скляні пластини з електродами
        out += glassplate(x0, yb + 2, x1 - x0)
        out += glassplate(x0, yt - 11, x1 - x0)
        # світло знизу
        out += arrow(cx, H - 64, cx, ypo + 30, GREEN, 2.4)
        out += text(cx, H - 48, "світло", 11.5, GREEN, "middle")
        if not on:
            twist = [0, 22.5, 45, 67.5, 90]
            for yy, ang in zip(rows, twist):
                for cxx in (-2, -1, 0, 1, 2):
                    out += mol(cx + cxx * 30, yy, ang, 11, INK, 4.6)
            out += text(x1 + 10, rows[0] + 5, "↔", 16, GREEN, "start", "bold")
            out += text(x1 + 10, rows[2] + 5, "⤢", 16, GREEN, "start", "bold")
            out += text(x1 + 10, rows[4] + 5, "↕", 16, GREEN, "start", "bold")
            out += arrow(cx, yan - 2, cx, 96, GREEN, 2.4)     # світло виходить
            out += text(cx, 86, "ЯСКРАВО", 16, GREEN, "middle", "bold")
            out += text(cx, ypo + 44, "поле вимкнено (U = 0)", 12, GREY, "middle")
        else:
            out += plus(x0 + 12, yt - 6.5, 8, RED)
            out += minus(x0 + 12, yb + 7.5, 8, BLUE)
            out += arrow(x0 + 24, yt + 6, x0 + 24, yb - 6, GREEN, 1.7, "5 4")
            out += text(x0 + 33, (yt + yb) / 2, "E", 13, GREEN, "start", "bold")
            for yy in rows:
                for cxx in (-2, -1, 0, 1, 2):
                    out += moldot(cx + cxx * 30, yy, 3, INK)
            out += text(x1 + 10, rows[2] + 5, "↔", 16, RED, "start", "bold")
            out += line(cx - 15, 92, cx + 15, 116, RED, 3)    # світло перекрите ✕
            out += line(cx + 15, 92, cx - 15, 116, RED, 3)
            out += text(cx, 80, "ТЕМНО", 16, DARK, "middle", "bold")
            out += text(cx, ypo + 44, "поле увімкнено (U > U₀)", 12, GREY, "middle")
        out += rect(x0, yt, x1 - x0, yb - yt, "none", FAINT, 1.4, 0)
        return out

    s += cell(214, False)
    s += cell(606, True)
    s += line(410, 96, 410, 360, FAINT, 1.4, "4 5")
    s += text(W / 2, 462,
              "TN перемикає полем, майже без струму — годинник на ньому живе роками. Основа майже всіх LCD.",
              12.5, GREY, "middle", style="italic")
    save("fig-13-1-0-3-tn.svg", s)


# ── Рис. 13.1.1.1 — три класи за джерелом світла ─────────────────────────────
def fig_classes_map():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 34, "Три класи дисплеїв — за тим, ЗВІДКИ береться світло", 19, INK, "middle", "bold")
    s += text(W / 2, 55, "одне це питання вирішує енергію, чорний колір і читаність на сонці", 12.5, GREY, "middle", style="italic")

    def panel(cx, kind, head, tech):
        out = rect(cx - 110, 76, 220, 320, "none", FAINT, 1.4, 8)
        out += text(cx, 100, head, 16, INK, "middle", "bold")
        eyey = 132
        out += eye(cx, eyey, 1, INK)
        out += text(cx + 26, eyey + 5, "око", 11.5, GREY, "start")
        py = 250
        for i, col in enumerate([RED, GREEN, BLUE]):
            out += rect(cx - 30 + i * 20, py - 16, 18, 32, col, "#ffffff", 1)
        out += rect(cx - 32, py - 18, 62, 36, "none", INK, 1.5)
        out += text(cx, py + 34, "піксель (R·G·B)", 11, GREY, "middle")
        if kind == "emit":
            for dx in (-14, 0, 14):
                out += arrow(cx + dx, py - 22, cx + dx * 0.4, eyey + 14, GREEN, 2)
            out += text(cx, 200, "світиться сам", 12.5, GREEN, "middle", "bold")
        elif kind == "trans":
            out += rect(cx - 90, 350, 180, 16, "#fff4c2", "#caa24a", 1.4, 3)
            out += text(cx, 362, "підсвітка (лампа)", 10.5, "#9a7d2e", "middle")
            out += arrow(cx, 348, cx, py + 20, "#caa24a", 2)
            out += arrow(cx, py - 22, cx, eyey + 14, GREEN, 2)
            out += text(cx + 44, 300, "крізь", 12, GREY, "middle")
        else:
            sx, sy = cx - 76, 158
            out += circle(sx, sy, 10, "#fff4c2", "#caa24a", 2)
            for a in range(0, 360, 45):
                rad = math.radians(a)
                out += line(sx + 12 * math.cos(rad), sy + 12 * math.sin(rad),
                            sx + 17 * math.cos(rad), sy + 17 * math.sin(rad), "#caa24a", 1.5)
            out += text(sx, sy - 22, "світло", 10.5, "#9a7d2e", "middle")
            out += arrow(sx + 8, sy + 8, cx - 20, py - 22, "#caa24a", 2)
            out += arrow(cx - 8, py - 22, cx - 2, eyey + 14, GREEN, 2)
            out += text(cx + 40, 205, "відбиває", 12, GREY, "middle")
        out += text(cx, 390, tech, 13, INK, "middle", "bold")
        return out

    s += panel(150, "emit", "ВИПРОМІНЮЄ", "OLED")
    s += panel(410, "trans", "ПРОПУСКАЄ", "TFT-LCD")
    s += panel(670, "reflect", "ВІДБИВАЄ", "e-ink")
    save("fig-13-1-1-1-classes.svg", s)


# ── Рис. 13.1.1.2 — стос пікселя TFT-LCD ─────────────────────────────────────
def fig_lcd_stack():
    W, H = 780, 360
    s = header(W, H)
    s += text(W / 2, 34, "Піксель TFT-LCD: заслінка з рідкого кристала перед лампою", 18, INK, "middle", "bold")
    s += text(W / 2, 55, "світло підсвітки йде знизу вгору крізь стос шарів; колір дає фільтр", 12.5, GREY, "middle", style="italic")
    cx = 260
    x0, x1 = cx - 150, cx + 150
    eyey = 78
    s += eye(cx, eyey, 1, INK)
    s += text(cx + 26, eyey + 5, "око", 11.5, GREY, "start")
    layers = [
        (98, 12, GLASS, "#5d7e93", "скло (переднє)"),
        (112, 14, "#eceff1", GREY, "поляризатор ↕"),
        (128, 22, None, INK, "кольорофільтр — R · G · B"),
        (152, 32, "#eaf3ff", "#9bbdd6", "рідкий кристал (заслінка)"),
        (186, 20, "#dfe6ea", "#5d7e93", "скло + TFT + ITO-електрод"),
        (208, 14, "#eceff1", GREY, "поляризатор ↔"),
    ]
    for (y0, h, fill, stroke, name) in layers:
        if name.startswith("кольорофільтр"):
            cw = (x1 - x0) / 3
            for i, col in enumerate([RED, GREEN, BLUE]):
                s += rect(x0 + i * cw, y0, cw, h, col, "#ffffff", 1)
            s += rect(x0, y0, x1 - x0, h, "none", INK, 1.2)
        else:
            s += rect(x0, y0, x1 - x0, h, fill if fill else "none", stroke, 1.4)
        if name.startswith("рідкий"):
            for mx in range(5):
                s += mol(x0 + 34 + mx * 58, y0 + h / 2, 28, 10, INK, 4)
        s += text(x1 + 14, y0 + h / 2 + 4, name, 12, INK, "start")
    s += rect(x0, 246, x1 - x0, 24, "#fff4c2", "#caa24a", 1.6, 3)
    s += text(x1 + 14, 260, "підсвітка (біле світло)", 12, "#9a7d2e", "start")
    s += arrow(x0 - 18, 246, x0 - 18, 94, GREEN, 2.4)
    s += text(x0 - 24, 175, "світло", 11.5, GREEN, "end")
    s += text(W / 2, 300, "Лампа світить завжди (звідси й споживання), а заслінка лише дозує, скільки пройде.", 12, GREY, "middle", style="italic")
    s += text(W / 2, 320, "«Чорний» — це закрита заслінка, та трохи світла все одно протікає: чорний виходить сіруватим.", 12, GREY, "middle", style="italic")
    save("fig-13-1-1-2-lcd-stack.svg", s)


# ── Рис. 13.1.1.3 — активна матриця: транзистор тримає піксель ────────────────
def fig_active_matrix():
    W, H = 740, 340
    s = header(W, H)
    s += text(W / 2, 34, "Активна матриця: чому на кожному пікселі сидить транзистор (TFT)", 18, INK, "middle", "bold")
    s += text(W / 2, 55, "транзистор заряджає піксель і тримає заряд, доки рядок не виберуть знову", 12.5, GREY, "middle", style="italic")
    gy, dx = 130, 200
    s += line(70, gy, 360, gy, INK, 2.6)
    s += text(64, gy - 7, "РЯДОК", 12, INK, "end", "bold")
    s += text(64, gy + 9, "(gate)", 10.5, GREY, "end")
    s += line(dx, 90, dx, gy, INK, 2.6)
    s += text(dx, 84, "СТОВПЕЦЬ (data)", 12, INK, "middle", "bold")
    s += rect(dx - 26, gy + 12, 52, 28, "#eef2f5", INK, 1.8, 5)
    s += text(dx, gy + 31, "TFT", 13, INK, "middle", "bold")
    s += line(dx, gy, dx, gy + 12, INK, 2)
    ny = gy + 40
    s += line(dx, ny, dx, ny + 22, INK, 2)
    node = ny + 22
    s += line(dx - 64, node, dx + 80, node, INK, 2)
    cxs = dx - 64
    s += line(cxs, node, cxs, node + 16, INK, 2)
    s += line(cxs - 15, node + 16, cxs + 15, node + 16, INK, 3)
    s += line(cxs - 15, node + 24, cxs + 15, node + 24, INK, 3)
    s += line(cxs, node + 24, cxs, node + 42, INK, 2)
    s += text(cxs - 21, node + 12, "C", 13, INK, "end", "bold")
    s += text(cxs, node + 58, "пам'ять", 10.5, GREY, "middle")
    cxl = dx + 80
    s += line(cxl, node, cxl, node + 16, INK, 2)
    s += line(cxl - 17, node + 16, cxl + 17, node + 16, "#5d7e93", 3)
    s += mol(cxl, node + 20, 60, 6.5, INK, 3.4)
    s += line(cxl - 17, node + 24, cxl + 17, node + 24, "#5d7e93", 3)
    s += line(cxl, node + 24, cxl, node + 42, INK, 2)
    s += text(cxl + 23, node + 14, "піксель", 11, INK, "start")
    s += text(cxl + 23, node + 28, "(LC)", 11, GREY, "start")
    s += line(cxs, node + 42, cxl, node + 42, INK, 2)
    s += text((cxs + cxl) / 2, node + 58, "спільний електрод", 10.5, GREY, "middle")
    seq = [
        "1 · вибрали РЯДОК → TFT відкрився",
        "2 · напруга СТОВПЦЯ зарядила C і піксель",
        "3 · рядок зняли → TFT закрився",
        "4 · C ТРИМАЄ напругу весь кадр",
    ]
    for i, t in enumerate(seq):
        s += text(400, 120 + i * 30, t, 12.5, INK, "start")
    save("fig-13-1-1-3-active-matrix.svg", s)


# ── Рис. 13.1.1.4 — стос пікселя OLED ────────────────────────────────────────
def fig_oled_stack():
    W, H = 780, 360
    s = header(W, H)
    s += text(W / 2, 34, "Піксель OLED: органічний шар світиться сам", 18, INK, "middle", "bold")
    s += text(W / 2, 55, "електрон і дірка зустрічаються в емісійному шарі — народжується фотон (див. §2.5.7)", 12, GREY, "middle", style="italic")
    cx = 270
    x0, x1 = cx - 150, cx + 150
    eyey = 78
    s += eye(cx, eyey, 1, INK)
    s += text(cx + 26, eyey + 5, "око", 11.5, GREY, "start")
    layers = [
        (98, 12, GLASS, "#5d7e93", "скло / інкапсуляція"),
        (112, 12, "#cfd8dc", GREY, "катод (−)"),
        (126, 12, "#e8eef0", "#9bbdd6", "ETL — транспорт електронів"),
        (140, 22, None, INK, "EML — емісійний шар R · G · B"),
        (164, 12, "#e8eef0", "#9bbdd6", "HTL — транспорт дірок"),
        (178, 12, "#f0d6a8", "#caa24a", "анод (+)"),
        (192, 24, "#dfe6ea", "#5d7e93", "підкладка + TFT-основа"),
    ]
    for (y0, h, fill, stroke, name) in layers:
        if name.startswith("EML"):
            cw = (x1 - x0) / 3
            for i, col in enumerate([RED, GREEN, BLUE]):
                s += rect(x0 + i * cw, y0, cw, h, col, "#ffffff", 1)
            s += rect(x0, y0, x1 - x0, h, "none", INK, 1.2)
        else:
            s += rect(x0, y0, x1 - x0, h, fill if fill else "none", stroke, 1.4)
        s += text(x1 + 14, y0 + h / 2 + 4, name, 11.5, INK, "start")
    s += minus(x0 - 30, 124, 6, BLUE)
    s += arrow(x0 - 24, 128, x0 + 26, 148, BLUE, 1.8)
    s += text(x0 - 40, 120, "e⁻", 12, BLUE, "end", "bold")
    s += plus(x0 - 30, 182, 6, RED)
    s += arrow(x0 - 24, 178, x0 + 26, 158, RED, 1.8)
    s += text(x0 - 40, 198, "дірка", 11, RED, "end", "bold")
    s += arrow(cx + 64, 140, cx + 64, 94, GREEN, 2.4)
    s += text(cx + 72, 120, "фотон", 11, GREEN, "start")
    s += text(W / 2, 280, "Жодної лампи й заслінки: вимкнений піксель = справжній чорний.", 12, GREY, "middle", style="italic")
    s += text(W / 2, 300, "Світло народжується прямо в пікселі — але органіка поступово старіє (вигоряння).", 12, GREY, "middle", style="italic")
    save("fig-13-1-1-4-oled-stack.svg", s)


# ── Рис. 13.1.1.5 — мікрокапсула e-ink ───────────────────────────────────────
def fig_eink_capsule():
    W, H = 780, 420
    s = header(W, H)
    s += text(W / 2, 34, "Піксель e-ink: заряджені частинки в мікрокапсулі", 18, INK, "middle", "bold")
    s += text(W / 2, 55, "поле піднімає білі або чорні частинки до поверхні — і ТРИМАЄ їх без струму", 12.5, GREY, "middle", style="italic")

    def band(cx, ytop, n, fill, stroke, rr):
        out = ""
        for i in range(n):
            gx = cx - 33 + (i % 4) * 22
            gy = ytop + (i // 4) * 20
            out += circle(gx, gy, rr, fill, stroke, 1.4)
        return out

    def capsule(cx, white_up, title):
        out = ""
        cy, r = 210, 92
        out += rect(cx - r, cy - r - 18, 2 * r, 12, "#dfe6ea", "#5d7e93", 1.4)
        out += rect(cx - r, cy + r + 6, 2 * r, 12, "#cfd8dc", "#5d7e93", 1.4)
        out += (minus(cx - r + 16, cy - r - 12, 6, BLUE) if white_up else plus(cx - r + 16, cy - r - 12, 6, RED))
        out += (plus(cx - r + 16, cy + r + 12, 6, RED) if white_up else minus(cx - r + 16, cy + r + 12, 6, BLUE))
        out += circle(cx, cy, r, "#f4fbff", "#7fa9c4", 2)
        if white_up:
            out += band(cx, cy - r + 28, 8, "#ffffff", "#9bbdd6", 8)
            out += band(cx, cy + r - 44, 8, "#2b2f33", "#2b2f33", 6)
        else:
            out += band(cx, cy - r + 28, 8, "#2b2f33", "#2b2f33", 6)
            out += band(cx, cy + r - 44, 8, "#ffffff", "#9bbdd6", 8)
        out += arrow(cx - r - 8, cy - r - 34, cx - 18, cy - r - 4, "#caa24a", 2)
        if white_up:
            out += arrow(cx - 6, cy - r - 4, cx + 34, cy - r - 36, GREEN, 2)
        out += text(cx, cy + r + 42, title, 13, INK, "middle", "bold")
        out += text(cx, cy + r + 60, "тримається без струму", 11, GREY, "middle")
        return out

    s += capsule(230, True, "БІЛИЙ піксель — відбиває")
    s += capsule(560, False, "ЧОРНИЙ піксель — поглинає")
    s += text(W / 2, 108, "білі частинки (+) ·  чорні частинки (−)  у прозорій рідині", 12, GREY, "middle", style="italic")
    save("fig-13-1-1-5-eink-capsule.svg", s)


# ── Рис. 13.1.1.6 — карта компромісів ────────────────────────────────────────
def fig_compare():
    W, H = 824, 320
    s = header(W, H)
    s += text(W / 2, 34, "Карта компромісів: TFT-LCD · OLED · e-ink", 19, INK, "middle", "bold")
    headers = ["", "Джерело світла", "Чорний колір", "Статична P", "На сонці", "Рух / відео"]
    rows = [
        ("TFT-LCD", [("підсвітка ззаду", "n"), ("сіруватий", "b"), ("висока (лампа)", "b"), ("добре", "g"), ("відмінно", "g")]),
        ("OLED", [("сам піксель", "g"), ("ідеальний", "g"), ("за вмістом", "n"), ("блики", "n"), ("відмінно", "g")]),
        ("e-ink", [("відбите", "g"), ("як папір", "g"), ("нуль", "g"), ("ідеально", "g"), ("ні (повільно)", "b")]),
    ]
    colw = [108, 152, 132, 132, 118, 130]
    tone_fill = {"g": "#e7f5ea", "b": "#fdeceb", "n": "#fff8e8"}
    tone_edge = {"g": GREEN, "b": RED, "n": "#b07d18"}
    x0, y0, rowh = 42, 70, 58
    cx = x0
    for j, htxt in enumerate(headers):
        s += rect(cx, y0, colw[j], 36, "#eef0f2", GREY, 1.2)
        if htxt:
            s += text(cx + colw[j] / 2, y0 + 22, htxt, 12.5, INK, "middle", "bold")
        cx += colw[j]
    for i, (name, cells) in enumerate(rows):
        ry = y0 + 36 + i * rowh
        cx = x0
        s += rect(cx, ry, colw[0], rowh, "#f6f7f8", GREY, 1.2)
        s += text(cx + colw[0] / 2, ry + rowh / 2 + 5, name, 13, INK, "middle", "bold")
        cx += colw[0]
        for j, (txt, tone) in enumerate(cells):
            s += rect(cx, ry, colw[j + 1], rowh, tone_fill[tone], GREY, 1.2)
            s += text(cx + colw[j + 1] / 2, ry + rowh / 2 + 5, txt, 12, tone_edge[tone], "middle", "bold")
            cx += colw[j + 1]
    s += text(W / 2, 300, "Жодна не «найкраща»: вибір — це питання живлення, світла довкола і того, що показуємо.",
              12, GREY, "middle", style="italic")
    save("fig-13-1-1-6-compare.svg", s)


# ── Рис. 13.1.1.7 — потужність у часі для статичного екрана ───────────────────
def fig_power_profile():
    W, H = 780, 380
    s = header(W, H)
    s += text(W / 2, 34, "Потужність у часі для майже статичного екрана", 19, INK, "middle", "bold")
    s += text(W / 2, 55, "чому для рідко оновлюваної інформації e-ink виграє на порядки", 12.5, GREY, "middle", style="italic")
    ox, oy, ax1, ay1 = 96, 300, 700, 88
    s += arrow(ox, oy, ax1, oy, INK, 2)
    s += arrow(ox, oy, ox, ay1, INK, 2)
    s += text(ax1, oy + 22, "час →", 12, INK, "end")
    s += text(ox - 6, ay1 - 4, "потужність ↑", 12, INK, "start")
    s += line(ox, 128, ax1 - 12, 128, RED, 2.6)
    s += text(ax1 - 8, 122, "TFT-LCD (лампа завжди)", 12, RED, "end")
    s += line(ox, 196, ax1 - 12, 196, BLUE, 2.4, "6 4")
    s += text(ax1 - 8, 190, "OLED (за вмістом)", 12, BLUE, "end")
    base = 288
    s += line(ox, base, ax1 - 12, base, GREEN, 2.6)
    for px in (200, 380, 560):
        s += line(px, base, px, base - 66, GREEN, 2.4)
        s += line(px, base - 66, px + 8, base - 66, GREEN, 2.4)
        s += line(px + 8, base - 66, px + 8, base, GREEN, 2.4)
    s += text(ax1 - 8, base - 6, "e-ink (нуль між оновленнями)", 12, GREEN, "end")
    s += text(380, 322, "↑ короткі піки лише коли картинка змінюється", 11.5, GREEN, "middle")
    save("fig-13-1-1-7-power.svg", s)


# ── Рис. 13.1.2.1 — роздільність і PPI: кутовий розмір пікселя ────────────────
def fig_ppi():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 34, "Роздільність і PPI: коли пікселі зливаються для ока", 19, INK, "middle", "bold")
    s += text(W / 2, 55, "важить не кількість пікселів сама по собі, а їхній КУТОВИЙ розмір на оці", 12.5, GREY, "middle", style="italic")
    ex, ey = 110, 200
    s += eye(ex, ey, 0, INK)
    s += text(ex, ey + 34, "око", 11, GREY, "middle")
    gx, gy, cell = 520, 150, 18
    for r in range(4):
        for c in range(5):
            fill = "#dff0e2" if (r == 0 and c == 0) else "#ffffff"
            s += rect(gx + c * cell, gy + r * cell, cell, cell, fill, GREY, 1)
    s += text(gx + 5 * cell / 2, gy + 4 * cell + 18, "сітка пікселів екрана", 11, GREY, "middle")
    s += line(ex + 18, ey, gx, ey, GREY, 1.4, "5 4")
    s += text((ex + gx) / 2, ey - 8, "відстань d", 12, INK, "middle")
    s += line(ex + 18, ey, gx, gy, INK, 1.6)
    s += line(ex + 18, ey, gx, gy + cell, INK, 1.6)
    s += text(gx - 26, gy + cell / 2 + 4, "α", 14, INK, "end", "bold")
    s += text(gx + 5 * cell + 12, gy + cell / 2 + 4, "1 піксель", 11, INK, "start")
    s += text(W / 2, 318, "PPI = (пікселів по діагоналі) ÷ (діагональ панелі, дюйми)", 13, INK, "middle")
    s += text(W / 2, 344, "кутовий розмір пікселя:  α = крок пікселя ÷ d", 13, INK, "middle")
    s += text(W / 2, 370, "око розрізняє ≈ 1′ = 1/60°", 13, INK, "middle")
    s += text(W / 2, 396, "якщо α < 1′ — окремих пікселів не видно (ефект «retina»)", 13, GREEN, "middle", "bold")
    save("fig-13-1-2-1-ppi.svg", s)


# ── Рис. 13.1.2.2 — яскравість у нітах для середовищ ─────────────────────────
def fig_nits():
    W, H = 820, 300
    s = header(W, H)
    s += text(W / 2, 34, "Яскравість у нітах (кд/м²): скільки треба для середовища", 19, INK, "middle", "bold")
    s += text(W / 2, 55, "одна цифра «нітів» нічого не варта без середовища, де екран читатимуть", 12.5, GREY, "middle", style="italic")
    ax0, ax1, ay = 70, 760, 165

    def xp(n):
        return ax0 + math.log10(n) / 4 * (ax1 - ax0)

    bands = [(1, 50, "ніч", "#dfe7ef"), (50, 300, "кімната / офіс", "#cfe6d3"),
             (300, 700, "день", "#fff0c2"), (700, 10000, "пряме сонце", "#f7d7c0")]
    for (a, b, lbl, col) in bands:
        xa, xb = xp(a), xp(b)
        s += rect(xa, ay - 56, xb - xa, 30, col, GREY, 1)
        s += text((xa + xb) / 2, ay - 37, lbl, 11.5, INK, "middle")
    s += line(ax0, ay, ax1, ay, INK, 2)
    for n in (1, 10, 100, 1000, 10000):
        x = xp(n)
        s += line(x, ay - 6, x, ay + 6, INK, 1.6)
        s += text(x, ay + 22, str(n), 11, INK, "middle")
    for (n, lbl) in [(200, "типовий TFT"), (600, "вулиця"), (1500, "для сонця")]:
        x = xp(n)
        s += circle(x, ay, 5, GREEN, GREEN, 1)
        s += text(x, ay - 12, lbl, 10.5, GREEN, "middle", "bold")
    s += text(W / 2, 250, "Контраст і яскравість на сонці «з'їдає» відблиск: справжня читаність нижча за цифру в даташиті.",
              12, GREY, "middle", style="italic")
    save("fig-13-1-2-2-nits.svg", s)


# ── Рис. 13.1.2.3 — контраст і рівень чорного ────────────────────────────────
def fig_contrast():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 34, "Контраст = білий ÷ чорний; на світлі він падає", 19, INK, "middle", "bold")

    def panel(cx, name, blk_fill, blk_txt, ratio):
        sq, y0 = 150, 96
        x0 = cx - sq / 2
        out = text(cx, y0 - 8, name, 14, INK, "middle", "bold")
        out += rect(x0, y0, sq, sq / 2, "#ffffff", INK, 1.5)
        out += rect(x0, y0 + sq / 2, sq, sq / 2, blk_fill, INK, 1.5)
        out += text(cx, y0 + sq / 4 + 5, "білий ≈ 300", 11, INK, "middle")
        out += text(cx, y0 + 3 * sq / 4 + 5, blk_txt, 11, "#ffffff", "middle")
        out += text(cx, y0 + sq + 24, "контраст ≈ " + ratio, 13, GREEN, "middle", "bold")
        return out

    s += panel(235, "LCD (заслінка протікає)", "#3b3f44", "чорний ≈ 0.3", "1000 : 1")
    s += panel(585, "OLED (піксель вимкнено)", "#0b0b0b", "чорний = 0", "∞")
    sx, sy = 410, 96
    s += circle(sx, sy, 11, "#fff4c2", "#caa24a", 2)
    for a in range(0, 360, 45):
        rad = math.radians(a)
        s += line(sx + 13 * math.cos(rad), sy + 13 * math.sin(rad),
                  sx + 19 * math.cos(rad), sy + 19 * math.sin(rad), "#caa24a", 1.5)
    s += arrow(sx - 8, sy + 14, 235 + 20, 96 + 120, "#caa24a", 1.8)
    s += arrow(sx + 8, sy + 14, 585 - 20, 96 + 120, "#caa24a", 1.8)
    s += text(W / 2, 300, "Відблиск додає світла ЧОРНОМУ — реальний контраст просідає, надто в LCD з його сіруватим чорним.",
              12, GREY, "middle", style="italic")
    save("fig-13-1-2-3-contrast.svg", s)


# ── Рис. 13.1.2.4 — механізм кутів огляду: TN проти IPS ──────────────────────
def fig_angles_mech():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Кути огляду: чому TN блякне збоку, а IPS — майже ні", 19, INK, "middle", "bold")

    def cell(cx, kind, head):
        x0, x1 = cx - 92, cx + 92
        yt, yb = 152, 244
        out = glassplate(x0, yt - 10, x1 - x0) + glassplate(x0, yb, x1 - x0)
        out += text(cx, 122, head, 14, INK, "middle", "bold")
        ang = 72 if kind == "TN" else 0
        for i in range(5):
            out += mol(x0 + 32 + i * 32, (yt + yb) / 2, ang, 13, INK, 4.6)
        note = "молекули нахилені з площини" if kind == "TN" else "молекули лежать У площині"
        out += text(cx, yb + 26, note, 10.5, GREY, "middle")
        out += eye(cx, yt - 44, 1, INK)
        out += text(cx, yt - 54, "прямо", 10, GREY, "middle")
        out += eye(x1 + 48, (yt + yb) / 2, 0, INK)
        out += arrow(x1 + 42, (yt + yb) / 2, x1 + 8, (yt + yb) / 2 - 8, INK, 1.5)
        out += text(x1 + 48, (yt + yb) / 2 + 22, "збоку", 10, GREY, "middle")
        return out

    s += cell(230, "TN", "TN — вузький кут")
    s += cell(580, "IPS", "IPS — широкий кут (~178°)")
    s += text(W / 2, 322, "Збоку ви дивитеся крізь іншу «товщину» кристала: у TN це сильно міняє яскравість і колір, в IPS майже ні.",
              12, GREY, "middle", style="italic")
    save("fig-13-1-2-4-angles-mech.svg", s)


# ── Рис. 13.1.2.5 — контраст проти кута огляду ───────────────────────────────
def fig_angle_curve():
    W, H = 760, 400
    s = header(W, H)
    s += text(W / 2, 34, "Відносний контраст проти кута огляду", 19, INK, "middle", "bold")
    ox, oy, ax1, ay1 = 86, 320, 700, 86

    def X(a):
        return ox + a / 80 * (ax1 - ox)

    def Y(p):
        return oy - p / 100 * (oy - ay1)

    s += arrow(ox, oy, ax1 + 6, oy, INK, 2)
    s += arrow(ox, oy, ox, ay1 - 6, INK, 2)
    for a in (0, 20, 40, 60, 80):
        s += line(X(a), oy, X(a), oy + 6, INK, 1.4)
        s += text(X(a), oy + 22, str(a) + "°", 11, INK, "middle")
    for p in (0, 50, 100):
        s += line(ox - 6, Y(p), ox, Y(p), INK, 1.4)
        s += text(ox - 10, Y(p) + 4, str(p), 11, INK, "end")
    s += text(ox - 10, ay1 - 6, "контраст, %", 12, INK, "start")
    s += text(ax1, oy + 22, "кут огляду", 12, INK, "end")

    def poly(pts, color, dash=None):
        out = ""
        for i in range(len(pts) - 1):
            out += line(X(pts[i][0]), Y(pts[i][1]), X(pts[i + 1][0]), Y(pts[i + 1][1]), color, 2.6, dash)
        return out

    curves = [
        ("TN", RED, None, [(0, 100), (20, 68), (40, 34), (60, 15), (80, 6)]),
        ("VA", "#caa24a", "6 4", [(0, 100), (20, 85), (40, 60), (60, 35), (80, 18)]),
        ("IPS", BLUE, None, [(0, 100), (20, 97), (40, 92), (60, 82), (80, 65)]),
        ("OLED", GREEN, None, [(0, 100), (20, 98), (40, 95), (60, 90), (80, 80)]),
    ]
    ly = 100
    for (name, col, dash, pts) in curves:
        s += poly(pts, col, dash)
        s += line(ax1 - 150, ly, ax1 - 120, ly, col, 2.6, dash)
        s += text(ax1 - 114, ly + 4, name, 12, col, "start", "bold")
        ly += 22
    s += text(W / 2, 372, "TN падає швидко; IPS і OLED тримають контраст майже до краю. Це й вирішує, з якого боку дивитимуться.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-1-2-5-angle-curve.svg", s)


# ── Рис. 13.1.2.6 — ШІМ-димінг і мерехтіння ──────────────────────────────────
def fig_pwm():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 32, "ШІМ-димінг: шпаруватість задає яскравість, частота — мерехтіння", 18, INK, "middle", "bold")
    s += text(W / 2, 53, "однакова яскравість (duty ≈ 35%), різна частота — і зовсім різний результат для ока", 12, GREY, "middle", style="italic")

    def pulses(x0, x1, yb, yh, period, width, color):
        out = ""
        x = x0
        prev = x0
        while x < x1:
            top = min(x + width, x1)
            nxt = min(x + period, x1)
            out += line(prev, yb, x, yb, color, 2.4)
            out += line(x, yb, x, yh, color, 2.4)
            out += line(x, yh, top, yh, color, 2.4)
            out += line(top, yh, top, yb, color, 2.4)
            prev = top
            x += period
        out += line(prev, yb, x1, yb, color, 2.4)
        return out

    s += pulses(90, 470, 168, 120, 90, 31, RED)
    s += text(90, 102, "низька частота (сотні Гц)", 12, RED, "start", "bold")
    s += text(280, 186, "→ око бачить мерехтіння, болять очі", 11.5, RED, "middle")
    # камера: смуги від мерехтіння
    s += rect(520, 96, 200, 92, "#ffffff", GREY, 1.4)
    for i in range(8):
        if i % 2 == 0:
            s += rect(521, 97 + i * 11.3, 198, 11.3, "#e2e6ea", "none", 0)
    s += text(620, 206, "камера ловить смуги", 11, GREY, "middle")
    s += pulses(90, 720, 300, 252, 30, 10.5, GREEN)
    s += text(90, 234, "висока частота (>2 кГц)", 12, GREEN, "start", "bold")
    s += text(405, 318, "→ око бачить рівне світло", 11.5, GREEN, "middle")
    s += text(W / 2, 360, "Найгірше: низька частота + низька яскравість (короткі рідкі спалахи).", 12, INK, "middle")
    s += text(W / 2, 382, "Добре: ШІМ понад кілька кГц або аналоговий (струмовий) димінг без миготіння.", 12, GREY, "middle", style="italic")
    save("fig-13-1-2-6-pwm.svg", s)


def databus(x0, y, x1, label, n, color=INK):
    """Товста «шина» з косою рискою й підписом ×n (як у схемах)."""
    out = line(x0, y, x1, y, color, 4)
    mx = (x0 + x1) / 2
    out += line(mx - 6, y + 7, mx + 6, y - 7, color, 1.6)
    out += text(mx, y - 11, label + " ×" + str(n), 11, color, "middle", "bold")
    return out


def box(x, y, w, h, title, sub=None, fill="#eef2f5"):
    out = rect(x, y, w, h, fill, INK, 1.8, 6)
    out += text(x + w / 2, y + (20 if sub else h / 2 + 5), title, 13, INK, "middle", "bold")
    if sub:
        out += text(x + w / 2, y + 38, sub, 11, GREY, "middle")
    return out


# ── Рис. 13.1.3.1 — пропускна здатність проти роздільності ────────────────────
def fig_bw_demand():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "Пропускна здатність проти роздільності: хто кого тягне", 19, INK, "middle", "bold")
    s += text(W / 2, 55, "вісь — Мбіт/с, логарифмічна;  ↑ скільки ПОТРІБНО,  ↓ скільки ДАЄ інтерфейс", 12.5, GREY, "middle", style="italic")
    ax0, ax1, ay = 90, 760, 205
    lo, hi = 10.0, 4000.0

    def xp(v):
        return ax0 + (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (ax1 - ax0)

    s += line(ax0, ay, ax1, ay, INK, 2)
    for n in (10, 30, 100, 300, 1000, 3000):
        x = xp(n)
        s += line(x, ay - 5, x, ay + 5, INK, 1.4)
        s += text(x, ay + 20, str(n), 10.5, GREY, "middle")
    s += text(ax1 + 4, ay + 20, "Мбіт/с", 11, INK, "start")
    dem = [("320×240@60 ≈ 74", 73.7, 0), ("480×320@60 ≈ 147", 147, 1),
           ("800×480@60 ≈ 369", 369, 0), ("1024×600@60 ≈ 590", 590, 1)]
    for (lbl, v, hi2) in dem:
        x = xp(v)
        yy = ay - 34 - hi2 * 30
        s += circle(x, ay, 4, INK, INK, 1)
        s += arrow(x, yy + 8, x, ay - 5, INK, 1.5)
        s += text(x, yy, lbl, 10.5, INK, "middle", "bold")
    cap = [("SPI ~80", 80, RED, 0), ("8080-16b ~320", 320, "#b07d18", 1),
           ("RGB-24b ~800", 800, GREEN, 0), ("MIPI-DSI ~1500+", 1500, BLUE, 1)]
    for (lbl, v, col, hi2) in cap:
        x = xp(v)
        yy = ay + 42 + hi2 * 30
        s += circle(x, ay, 4, col, col, 1)
        s += arrow(x, yy - 8, x, ay + 5, col, 1.7)
        s += text(x, yy + 6, lbl, 10.5, col, "middle", "bold")
    s += text(W / 2, 360, "SPI ледве тягне дрібні панелі; великі роздільності годує лише RGB або MIPI-DSI.", 12, GREY, "middle", style="italic")
    save("fig-13-1-3-1-bw-demand.svg", s)


# ── Рис. 13.1.3.2 — SPI-дисплей ──────────────────────────────────────────────
def fig_spi_wiring():
    W, H = 800, 360
    s = header(W, H)
    s += text(W / 2, 34, "SPI-дисплей: мало дротів, але вузька труба", 19, INK, "middle", "bold")
    s += box(60, 120, 140, 120, "МК")
    s += rect(560, 104, 180, 152, "#eef2f5", INK, 1.8, 6)
    s += text(650, 124, "контролер + GRAM", 12, INK, "middle", "bold")
    s += rect(580, 138, 140, 96, "#ffffff", GREY, 1.2)
    for r in range(4):
        s += line(580, 138 + (r + 1) * 19.2, 720, 138 + (r + 1) * 19.2, "#e4e4e4", 1)
    s += text(650, 248, "своя памʼять кадру (GRAM)", 10, GREY, "middle")
    wires = [("SCK", INK), ("MOSI", INK), ("CS", GREY), ("DC", GREY), ("RST", GREY), ("MISO", "#b0b0b0")]
    for i, (nm, col) in enumerate(wires):
        y = 132 + i * 18
        dash = "4 3" if nm == "MISO" else None
        s += line(200, y, 560, y, col, 1.8, dash)
        s += text(380, y - 5, nm, 10.5, col, "middle")
    s += text(380, 132 + 6 * 18 + 4, "1 біт за такт SCK", 11, RED, "middle", "bold")
    s += text(W / 2, 300, "Хост шле команди (DC=0) і дані пікселів (DC=1); контролер сам тримає картинку й освіжає скло.", 12, GREY, "middle", style="italic")
    s += text(W / 2, 322, "Тож по SPI ганяють лише ЗМІНИ — це й рятує вузьку шину на дрібних екранах.", 12, GREY, "middle", style="italic")
    save("fig-13-1-3-2-spi.svg", s)


# ── Рис. 13.1.3.3 — паралельний 8080 ─────────────────────────────────────────
def fig_8080_bus():
    W, H = 800, 380
    s = header(W, H)
    s += text(W / 2, 34, "Паралельний 8080: ціле слово за один строб WR", 19, INK, "middle", "bold")
    s += box(60, 96, 130, 110, "МК")
    s += rect(560, 90, 180, 122, "#eef2f5", INK, 1.8, 6)
    s += text(650, 112, "контролер + GRAM", 12, INK, "middle", "bold")
    s += rect(580, 124, 140, 74, "#ffffff", GREY, 1.2)
    s += databus(190, 132, 560, "D", 16, INK)
    for i, nm in enumerate(["WR", "RD", "CS", "DC"]):
        y = 156 + i * 16
        s += line(190, y, 560, y, GREY, 1.6)
        s += text(178, y + 4, nm, 10, GREY, "end")
    # тайминг: WR пульсує, слова фіксуються на фронті
    tx0, tx1, ty = 150, 700, 290
    s += text(tx0 - 16, ty - 18, "WR", 11, INK, "end", "bold")
    x = tx0
    yb, yh = ty, ty - 26
    words = ["D₀", "D₁", "D₂", "D₃"]
    for k in range(4):
        s += line(x, yb, x + 30, yb, INK, 2)
        s += line(x + 30, yb, x + 30, yh, INK, 2)
        s += line(x + 30, yh, x + 70, yh, INK, 2)
        s += line(x + 70, yh, x + 70, yb, INK, 2)
        s += line(x + 70, ty + 18, x + 70, ty + 40, GREY, 1, "3 3")
        s += text(x + 50, ty + 54, words[k], 11, INK, "middle", "bold")
        x += 100
    s += text(tx0 + 200, ty + 36, "слово фіксується на фронті WR ↑", 11, GREEN, "middle", "bold")
    s += text(W / 2, 348, "Ширша за SPI у стільки разів, скільки ліній даних (8 чи 16) — ціною стількох пінів.", 12, GREY, "middle", style="italic")
    save("fig-13-1-3-3-8080.svg", s)


# ── Рис. 13.1.3.4 — RGB-паралельний (DPI) ────────────────────────────────────
def fig_rgb_scan():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 34, "RGB-паралельний (DPI): панель без памʼяті — гнати щокадру без упину", 18, INK, "middle", "bold")
    s += rect(50, 100, 168, 160, "#eef2f5", INK, 1.8, 6)
    s += text(134, 122, "LCD-контролер (§4.9)", 11.5, INK, "middle", "bold")
    s += text(134, 140, "framebuffer у RAM", 10.5, GREY, "middle")
    s += rect(70, 152, 128, 92, "#ffffff", GREY, 1.2)
    sig = [("R·G·B ×(18–24)", INK), ("PCLK", INK), ("HSYNC", GREY), ("VSYNC", GREY), ("DE", GREEN)]
    for i, (nm, col) in enumerate(sig):
        y = 118 + i * 26
        s += arrow(218, y, 470, y, col, 1.8)
        s += text(344, y - 5, nm, 10.5, col, "middle")
    # панель з растром
    px, py, pw, ph = 488, 96, 250, 188
    s += rect(px, py, pw, ph, "#fbfbfb", INK, 1.8, 4)
    s += text(px + pw / 2, py - 6, "панель (без GRAM)", 11.5, INK, "middle", "bold")
    ax, ay, aw, ah = px + 40, py + 44, pw - 70, ph - 78
    s += rect(ax, ay, aw, ah, "#eaf3ff", "#9bbdd6", 1.4)
    s += text(ax + aw / 2, ay + ah / 2 + 4, "активні пікселі", 10.5, "#5d7e93", "middle")
    for r in range(4):
        yy = ay + 10 + r * (ah - 20) / 3
        s += arrow(ax + 6, yy, ax + aw - 6, yy, "#caa24a", 1.4)
    s += text(px + pw / 2, py + ph - 8, "порожні поля (porch) — H/V гасіння", 9.5, GREY, "middle")
    s += text(px + 18, ay + ah / 2, "VSYNC", 9, GREY, "middle")
    s += text(W / 2, 372, "Жодної памʼяті в панелі: контролер безперервно сканує кадр рядок за рядком, інакше картинка розсиплеться.", 11.5, GREY, "middle", style="italic")
    save("fig-13-1-3-4-rgb.svg", s)


# ── Рис. 13.1.3.5 — MIPI-DSI ─────────────────────────────────────────────────
def fig_dsi_lanes():
    W, H = 800, 340
    s = header(W, H)
    s += text(W / 2, 34, "MIPI-DSI: шалена швидкість по кількох диференційних парах", 18, INK, "middle", "bold")
    s += box(70, 110, 150, 130, "хост (SoC /", "потужний МК)")
    s += box(580, 110, 150, 130, "панель", "(DSI-приймач)")
    lanes = [("CLK", "тактова пара", BLUE), ("D0", "смуга даних 1", INK),
             ("D1", "смуга даних 2", INK), ("D2…D3", "ще смуги (до 4)", GREY)]
    for i, (nm, desc, col) in enumerate(lanes):
        y = 130 + i * 30
        s += line(220, y - 3, 580, y - 3, col, 1.8)
        s += line(220, y + 3, 580, y + 3, col, 1.8)
        s += text(212, y + 3, nm, 10.5, col, "end", "bold")
        s += text(400, y - 7, desc, 9.5, GREY, "middle")
        s += text(236, y - 9, "+", 9, col, "middle")
        s += text(236, y + 15, "−", 9, col, "middle")
    s += text(400, 268, "кожна смуга — пара проводів (+/−), Гбіт/с на смугу (диференційно, як у §6.3)", 11.5, INK, "middle", "bold")
    s += text(W / 2, 312, "Кілька тонких пар несуть більше, ніж десятки ліній RGB, — але потрібен хост із DSI й складніший протокол.", 11.5, GREY, "middle", style="italic")
    save("fig-13-1-3-5-dsi.svg", s)


# ── Рис. 13.1.3.6 — карта вибору інтерфейсу ──────────────────────────────────
def fig_iface_compare():
    W, H = 824, 320
    s = header(W, H)
    s += text(W / 2, 34, "Карта інтерфейсів: піни проти швидкості проти ноші на хост", 19, INK, "middle", "bold")
    headers = ["", "Дроти", "Смуга", "Памʼять у панелі", "Ноша на хост", "Типове застосування"]
    rows = [
        ("SPI", [("3–5", "g"), ("вузька", "b"), ("є (GRAM)", "g"), ("мала", "g"), ("дрібні екрани", "n")]),
        ("8080", [("12–24", "n"), ("середня", "n"), ("є (GRAM)", "g"), ("мала", "g"), ("середні, простий МК", "n")]),
        ("RGB", [("28–40", "b"), ("широка", "g"), ("нема", "b"), ("велика", "b"), ("великі, є LCD-контролер", "n")]),
        ("MIPI-DSI", [("4–10", "g"), ("дуже широка", "g"), ("нема", "b"), ("велика", "b"), ("телефонні роздільності", "n")]),
    ]
    colw = [104, 92, 116, 134, 116, 158]
    tf = {"g": "#e7f5ea", "b": "#fdeceb", "n": "#fff8e8"}
    te = {"g": GREEN, "b": RED, "n": "#b07d18"}
    x0, y0, rowh = 28, 70, 52
    cx = x0
    for j, htxt in enumerate(headers):
        s += rect(cx, y0, colw[j], 36, "#eef0f2", GREY, 1.2)
        if htxt:
            s += text(cx + colw[j] / 2, y0 + 22, htxt, 12, INK, "middle", "bold")
        cx += colw[j]
    for i, (name, cells) in enumerate(rows):
        ry = y0 + 36 + i * rowh
        cx = x0
        s += rect(cx, ry, colw[0], rowh, "#f6f7f8", GREY, 1.2)
        s += text(cx + colw[0] / 2, ry + rowh / 2 + 5, name, 12.5, INK, "middle", "bold")
        cx += colw[0]
        for j, (txt, tone) in enumerate(cells):
            s += rect(cx, ry, colw[j + 1], rowh, tf[tone], GREY, 1.2)
            s += text(cx + colw[j + 1] / 2, ry + rowh / 2 + 5, txt, 11, te[tone], "middle", "bold")
            cx += colw[j + 1]
    s += text(W / 2, 304, "Що ширша труба — то більше дротів або складніший хост: безкоштовної пропускної здатності не буває.", 11.5, GREY, "middle", style="italic")
    save("fig-13-1-3-6-compare.svg", s)


# ── Рис. 13.1.4.1 — дві роботи дисплея: памʼять кадру і освіження ─────────────
def fig_two_jobs():
    W, H = 820, 300
    s = header(W, H)
    s += text(W / 2, 34, "Дві роботи кожного дисплея: памʼять кадру і вічне освіження", 19, INK, "middle", "bold")
    s += box(60, 118, 180, 92, "памʼять кадру", "(framebuffer)")
    s += box(320, 118, 180, 92, "двигун освіження", "(refresh ~60 Гц)")
    s += rect(580, 118, 180, 92, "#eaf3ff", "#9bbdd6", 1.8, 6)
    s += text(670, 152, "скло", 13, "#5d7e93", "middle", "bold")
    s += text(670, 172, "(піксельна матриця)", 10, GREY, "middle")
    s += arrow(240, 164, 320, 164, INK, 2.2)
    s += arrow(500, 164, 580, 164, INK, 2.2)
    s += text(410, 150, "читає 60×/с", 10.5, GREY, "middle")
    s += text(150, 234, "«що має бути на екрані зараз»", 10.5, GREY, "middle")
    s += text(410, 234, "перечитує памʼять, засвічує рядки", 10.5, GREY, "middle")
    s += text(670, 234, "забуває без постійного освіження", 10.5, GREY, "middle")
    s += text(W / 2, 274, "Хтось мусить володіти обома роботами. Уся тема — про те, ХТО: панель чи мікроконтролер.", 12, INK, "middle", "bold")
    save("fig-13-1-4-1-two-jobs.svg", s)


# ── Рис. 13.1.4.2 — framebuffer «на склі»: розумна панель ─────────────────────
def fig_smart_panel():
    W, H = 820, 300
    s = header(W, H)
    s += text(W / 2, 34, "Варіант А: framebuffer «на склі» — розумна панель", 19, INK, "middle", "bold")
    s += box(70, 120, 150, 100, "МК", "(трохи RAM)")
    s += rect(360, 92, 400, 152, "#f4f7f9", INK, 1.8, 8)
    s += text(560, 86, "модуль панелі", 11, GREY, "middle")
    s += box(380, 122, 150, 92, "контролер", "+ GRAM")
    s += rect(560, 122, 180, 92, "#eaf3ff", "#9bbdd6", 1.5, 4)
    s += text(650, 160, "скло", 12, "#5d7e93", "middle", "bold")
    s += text(650, 180, "(матриця)", 9.5, GREY, "middle")
    s += arrow(220, 162, 378, 162, INK, 2.2)
    s += text(300, 151, "команди + зміни", 10, GREY, "middle")
    s += arrow(530, 168, 560, 168, GREEN, 2)
    s += text(560, 230, "освіження — всередині панелі", 10, GREEN, "middle")
    s += text(W / 2, 272, "Памʼять кадру лежить У ПАНЕЛІ; МК шле лише зміни й вільний між оновленнями. Це SPI / 8080-дисплеї.", 12, INK, "middle", "bold")
    save("fig-13-1-4-2-smart-panel.svg", s)


# ── Рис. 13.1.4.3 — вікно адрес у GRAM (часткове оновлення) ───────────────────
def fig_gram_window():
    W, H = 760, 360
    s = header(W, H)
    s += text(W / 2, 34, "Часткове оновлення: вікно адрес у GRAM", 19, INK, "middle", "bold")
    gx, gy, gw, gh = 250, 116, 300, 190
    s += rect(gx, gy, gw, gh, "#fbfbfb", INK, 1.8)
    s += text(gx + gw / 2, gy - 8, "GRAM — уся памʼять кадру панелі", 11, GREY, "middle")
    wx, wy, ww, wh = gx + 96, gy + 58, 120, 78
    s += rect(wx, wy, ww, wh, "#dff0e2", GREEN, 2)
    s += text(wx + ww / 2, wy + wh / 2 + 4, "вікно", 12, GREEN, "middle", "bold")
    s += text(wx + ww / 2, wy - 6, "(x0,y0)…(x1,y1)", 9.5, GREEN, "middle")
    s += box(50, 168, 130, 86, "МК")
    s += arrow(180, 196, wx - 2, wy + wh / 2, INK, 2)
    s += text(196, 182, "1) задати вікно", 10, INK, "start")
    s += text(196, 210, "2) лити пікселі", 10, INK, "start")
    s += text(W / 2, 336, "Оновлюється лише прямокутник, а не весь екран — головний трюк економії шини на розумних панелях.", 11.5, GREY, "middle", style="italic")
    save("fig-13-1-4-3-gram-window.svg", s)


# ── Рис. 13.1.4.4 — framebuffer у МК: дурна панель + LTDC ─────────────────────
def fig_host_fb():
    W, H = 820, 300
    s = header(W, H)
    s += text(W / 2, 34, "Варіант Б: framebuffer у МК — дурна панель + контролер-периферія", 18, INK, "middle", "bold")
    s += rect(56, 92, 338, 150, "#f4f7f9", INK, 1.8, 8)
    s += text(225, 86, "мікроконтролер", 11, GREY, "middle")
    s += box(76, 122, 156, 92, "framebuffer", "у RAM хоста")
    s += box(244, 122, 132, 92, "LCD-контр.", "(LTDC §4.9)")
    s += arrow(232, 168, 244, 168, INK, 2)
    s += rect(560, 122, 184, 92, "#eaf3ff", "#9bbdd6", 1.5, 4)
    s += text(652, 158, "панель", 12, "#5d7e93", "middle", "bold")
    s += text(652, 178, "дурна (без GRAM)", 9.5, GREY, "middle")
    s += arrow(394, 168, 560, 168, GREEN, 2.2)
    s += text(477, 156, "безперервний потік", 10, GREEN, "middle")
    s += text(W / 2, 266, "Памʼять кадру У ХОСТІ; периферія сама без упину женеться нею в панель. Повний контроль, та багато RAM.", 12, INK, "middle", "bold")
    save("fig-13-1-4-4-host-fb.svg", s)


# ── Рис. 13.1.4.5 — де живе контролер: три розміщення ────────────────────────
def fig_ctrl_placement():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 34, "Де живе контролер дисплея: у панелі · у МК · окремим чипом", 18, INK, "middle", "bold")

    def col(cx, head, boxes, cap):
        out = text(cx, 70, head, 13, INK, "middle", "bold")
        y = 88
        for i, (t1, t2, fill) in enumerate(boxes):
            out += rect(cx - 96, y, 192, 46, fill, INK, 1.6, 5)
            out += text(cx, y + (19 if t2 else 28), t1, 11.5, INK, "middle", "bold")
            if t2:
                out += text(cx, y + 36, t2, 9.5, GREY, "middle")
            if i < len(boxes) - 1:
                out += arrow(cx, y + 46, cx, y + 62, INK, 1.8)
            y += 62
        out += text(cx, y + 8, cap, 10, GREY, "middle")
        return out

    s += col(148, "у ПАНЕЛІ",
             [("МК", None, "#eef2f5"), ("панель", "ctrl + GRAM + скло", "#eaf3ff")],
             "SPI / 8080, DSI-cmd")
    s += col(410, "у МК",
             [("МК", "ctrl + framebuffer", "#eef2f5"), ("панель", "дурна + скло", "#eaf3ff")],
             "RGB, DSI-video")
    s += col(672, "окремим ЧИПОМ",
             [("МК", None, "#eef2f5"), ("чип", "ctrl + GRAM", "#fff4c2"), ("панель", "скло", "#eaf3ff")],
             "малий МК + велика панель")
    save("fig-13-1-4-5-placement.svg", s)


# ── Рис. 13.1.4.6 — порівняння архітектур ────────────────────────────────────
def fig_arch_compare():
    W, H = 824, 280
    s = header(W, H)
    s += text(W / 2, 34, "Дві архітектури: де тримати кадр", 19, INK, "middle", "bold")
    headers = ["", "RAM хоста", "Шина", "Гнучкість пікселів", "Розмір панелі", "Складність МК"]
    rows = [
        ("«на склі»\n(розумна панель)", [("майже 0", "g"), ("шле зміни", "g"), ("обмежена", "b"), ("малі/середні", "n"), ("проста", "g")]),
        ("«в МК»\n(хост-буфер)", [("багато", "b"), ("безперервна", "b"), ("повна", "g"), ("аж до великих", "g"), ("потужний МК", "b")]),
    ]
    colw = [128, 104, 110, 142, 128, 110]
    tf = {"g": "#e7f5ea", "b": "#fdeceb", "n": "#fff8e8"}
    te = {"g": GREEN, "b": RED, "n": "#b07d18"}
    x0, y0, rowh = 22, 66, 64
    cx = x0
    for j, htxt in enumerate(headers):
        s += rect(cx, y0, colw[j], 36, "#eef0f2", GREY, 1.2)
        if htxt:
            s += text(cx + colw[j] / 2, y0 + 22, htxt, 11.5, INK, "middle", "bold")
        cx += colw[j]
    for i, (name, cells) in enumerate(rows):
        ry = y0 + 36 + i * rowh
        cx = x0
        s += rect(cx, ry, colw[0], rowh, "#f6f7f8", GREY, 1.2)
        parts = name.split("\n")
        s += text(cx + colw[0] / 2, ry + rowh / 2 - 4, parts[0], 11.5, INK, "middle", "bold")
        s += text(cx + colw[0] / 2, ry + rowh / 2 + 13, parts[1], 9.5, GREY, "middle")
        cx += colw[0]
        for j, (txt, tone) in enumerate(cells):
            s += rect(cx, ry, colw[j + 1], rowh, tf[tone], GREY, 1.2)
            s += text(cx + colw[j + 1] / 2, ry + rowh / 2 + 4, txt, 11, te[tone], "middle", "bold")
            cx += colw[j + 1]
    save("fig-13-1-4-6-arch-compare.svg", s)


# ── Рис. 13.1.5.1 — будова підсвітки (edge-lit) ──────────────────────────────
def fig_backlight_structure():
    W, H = 820, 350
    s = header(W, H)
    s += text(W / 2, 34, "Підсвітка збоку: світлодіоди + світловод розганяють світло вгору", 18, INK, "middle", "bold")
    s += eye(400, 72, 1, INK)
    s += text(426, 77, "око", 11, GREY, "start")
    lx, rx = 170, 600
    s += rect(lx, 104, rx - lx, 26, "#eaf3ff", "#9bbdd6", 1.5)
    s += text(rx + 12, 121, "LCD-панель (заслінка)", 11, "#5d7e93", "start")
    s += rect(lx, 134, rx - lx, 12, "#f2f2f2", GREY, 1.2)
    s += text(rx + 12, 144, "розсіювач", 10, GREY, "start")
    s += rect(lx, 150, rx - lx, 40, "#fff8e0", "#caa24a", 1.5)
    s += text(rx + 12, 174, "світловод", 11, "#9a7d2e", "start")
    s += rect(lx, 194, rx - lx, 10, "#dcdcdc", GREY, 1.2)
    s += text(rx + 12, 203, "відбивач", 10, GREY, "start")
    for i in range(3):
        s += rect(lx - 24, 156 + i * 11, 20, 8, "#fff4c2", "#caa24a", 1.2)
    s += text(lx - 26, 150, "білі LED", 10, "#9a7d2e", "end")
    s += arrow(lx - 2, 170, 320, 170, "#caa24a", 1.6)
    for xx in (250, 350, 450, 550):
        s += arrow(xx, 150, xx, 132, GREEN, 1.8)
    s += arrow(400, 104, 400, 88, GREEN, 2)
    s += text(W / 2, 250, "Світло LED входить у світловод збоку, розсіюється рівно по площині й виходить угору крізь заслінку до ока.", 12, GREY, "middle", style="italic")
    s += text(W / 2, 274, "Яскравість панелі йде за яскравістю підсвітки, а та — за СТРУМОМ крізь світлодіоди.", 12, INK, "middle", "bold")
    save("fig-13-1-5-1-backlight.svg", s)


# ── Рис. 13.1.5.2 — ВАХ світлодіода: чому струм, а не напруга ─────────────────
def fig_led_iv():
    W, H = 760, 400
    s = header(W, H)
    s += text(W / 2, 34, "Світлодіодом керують струмом, а не напругою", 19, INK, "middle", "bold")
    ox, oy, ax1, ay1 = 92, 330, 680, 78

    def X(v):
        return ox + v / 4.0 * (ax1 - ox)

    def Y(i):
        return oy - i / 30.0 * (oy - ay1)

    s += arrow(ox, oy, ax1 + 6, oy, INK, 2)
    s += arrow(ox, oy, ox, ay1 - 6, INK, 2)
    s += text(ax1, oy + 22, "Vf, В", 12, INK, "end")
    s += text(ox - 8, ay1 - 6, "I, мА", 12, INK, "start")
    for v in (1, 2, 3, 4):
        s += line(X(v), oy, X(v), oy + 5, INK, 1.3)
        s += text(X(v), oy + 20, str(v), 10, GREY, "middle")
    for i in (10, 20, 30):
        s += line(ox - 5, Y(i), ox, Y(i), INK, 1.3)
        s += text(ox - 9, Y(i) + 4, str(i), 10, GREY, "end")
    pts = []
    for k in range(0, 41):
        v = k * 0.1
        i = 0.0 if v < 2.5 else min(30.0, 0.02 * math.exp((v - 2.5) / 0.14))
        pts.append((v, i))
    for j in range(len(pts) - 1):
        s += line(X(pts[j][0]), Y(pts[j][1]), X(pts[j + 1][0]), Y(pts[j + 1][1]), RED, 2.6)
    # маленький ΔV → величезний ΔI на крутій ділянці
    v1, v2 = 3.25, 3.4
    i1 = min(30.0, 0.02 * math.exp((v1 - 2.5) / 0.14))
    i2 = min(30.0, 0.02 * math.exp((v2 - 2.5) / 0.14))
    s += line(X(v1), oy, X(v1), Y(i1), BLUE, 1.4, "4 3")
    s += line(X(v2), oy, X(v2), Y(i2), BLUE, 1.4, "4 3")
    s += line(ox, Y(i1), X(v1), Y(i1), BLUE, 1.4, "4 3")
    s += line(ox, Y(i2), X(v2), Y(i2), BLUE, 1.4, "4 3")
    s += text(X(v1) - 4, oy + 34, "ΔV крихітний", 10.5, BLUE, "middle", "bold")
    s += arrow(X(v1) + 6, oy + 30, X(v2) - 6, oy + 30, BLUE, 1.3)
    s += text(ox - 16, (Y(i1) + Y(i2)) / 2, "ΔI", 11, BLUE, "end", "bold")
    s += text(ox - 16, (Y(i1) + Y(i2)) / 2 + 16, "величезний", 9, BLUE, "end")
    s += text(420, 150, "Задаєш напругу — струм (а отже й", 11, INK, "start")
    s += text(420, 167, "яскравість) непередбачуваний.", 11, INK, "start")
    s += text(420, 190, "Задаєш СТРУМ — яскравість рівна", 11, GREEN, "start", "bold")
    s += text(420, 207, "й світлодіод у безпеці.", 11, GREEN, "start", "bold")
    save("fig-13-1-5-2-led-iv.svg", s)


# ── Рис. 13.1.5.3 — баластний резистор ───────────────────────────────────────
def fig_resistor_ballast():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 34, "Найпростіший струмовий «регулятор»: баластний резистор", 18, INK, "middle", "bold")
    # коло: Vsupply — R — LED — GND
    s += text(110, 130, "V₊", 13, RED, "middle", "bold")
    s += line(110, 140, 110, 200, INK, 2)
    s += line(110, 200, 230, 200, INK, 2)
    # резистор (зигзаг прямокутник)
    s += rect(230, 188, 70, 24, "#fff", INK, 1.6)
    s += text(265, 204, "R", 13, INK, "middle", "bold")
    s += line(300, 200, 400, 200, INK, 2)
    # LED символ (трикутник + риска)
    s += line(400, 188, 400, 212, INK, 2)
    s += line(400, 188, 424, 200, INK, 2)
    s += line(424, 188, 424, 212, INK, 2)
    s += line(400, 212, 424, 200, INK, 2)
    s += line(424, 200, 520, 200, INK, 2)
    s += line(520, 200, 520, 240, INK, 2)
    s += line(505, 240, 535, 240, INK, 2)
    s += text(540, 244, "GND", 11, GREY, "start")
    s += text(412, 178, "LED", 10.5, "#9a7d2e", "middle")
    s += arrow(150, 200, 200, 200, GREEN, 2)
    s += text(175, 190, "I", 12, GREEN, "middle", "bold")
    s += text(W / 2, 270, "I = (V₊ − V_LED) ÷ R.  Просто й дешево, але резистор гріється, а струм «гуляє» з напругою живлення й теплом.",
              12, GREY, "middle", style="italic")
    save("fig-13-1-5-3-ballast.svg", s)


# ── Рис. 13.1.5.4 — boost-драйвер зі зворотним звʼязком по струму ─────────────
def fig_boost_driver():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 34, "Boost-драйвер: підняти напругу й тримати ЗАДАНИЙ струм", 18, INK, "middle", "bold")
    y = 150
    s += text(60, y + 4, "Vᵢₙ", 12, INK, "end", "bold")
    s += line(64, y, 110, y, INK, 2)
    # котушка L (півхвильки)
    lx = 110
    for k in range(4):
        s += line(lx + k * 14, y, lx + k * 14 + 7, y - 10, INK, 1.8)
        s += line(lx + k * 14 + 7, y - 10, lx + k * 14 + 14, y, INK, 1.8)
    s += text(lx + 28, y - 18, "L", 11, INK, "middle")
    s += line(lx + 56, y, 210, y, INK, 2)
    s += rect(210, y - 34, 150, 70, "#eef2f5", INK, 1.8, 6)
    s += text(285, y - 6, "BOOST", 13, INK, "middle", "bold")
    s += text(285, y + 14, "+ регулятор I", 10, GREY, "middle")
    s += line(360, y, 430, y, INK, 2)
    s += rect(430, y - 24, 150, 48, "#fff8e0", "#caa24a", 1.6, 5)
    s += text(505, y + 4, "LED-нитка (N шт.)", 11, "#9a7d2e", "middle")
    s += line(580, y, 650, y, INK, 2)
    s += rect(650, y - 12, 40, 24, "#fff", INK, 1.6)
    s += text(670, y + 4, "Rₛ", 11, INK, "middle", "bold")
    s += line(690, y, 730, y, INK, 2)
    s += line(730, y, 730, y + 40, INK, 2)
    s += line(715, y + 40, 745, y + 40, INK, 2)
    # зворотний звʼязок по струму
    s += arrow(670, y + 12, 670, y + 70, GREY, 1.6)
    s += line(670, y + 70, 285, y + 70, GREY, 1.6, "5 4")
    s += arrow(285, y + 70, 285, y + 36, GREY, 1.6)
    s += text(478, y + 84, "зворотний звʼязок: тримай I = заданому", 10.5, GREEN, "middle", "bold")
    s += text(W / 2, 300, "Перетворювач піднімає напругу, доки крізь нитку не піде задане I; струм «читає» резистор Rₛ. Так живлять довгі нитки.",
              12, GREY, "middle", style="italic")
    save("fig-13-1-5-4-boost.svg", s)


# ── Рис. 13.1.5.5 — димінг: ШІМ проти аналогового ────────────────────────────
def fig_dimming():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "Димінг: ШІМ (час) проти аналогового (рівень струму)", 18, INK, "middle", "bold")

    def axis(y0, lbl):
        out = arrow(70, y0, 760, y0, INK, 1.6)
        out += arrow(70, y0, 70, y0 - 64, INK, 1.6)
        out += text(58, y0 - 58, "I", 11, INK, "end", "bold")
        out += text(70, y0 + 18, lbl, 11, INK, "start", "bold")
        return out

    # ШІМ: повні імпульси, duty ~40%
    yA = 150
    s += axis(yA, "ШІМ: повний струм, міняємо ЧАС")
    x = 90
    while x < 740:
        s += line(x, yA, x, yA - 50, RED, 2.2)
        s += line(x, yA - 50, x + 40, yA - 50, RED, 2.2)
        s += line(x + 40, yA - 50, x + 40, yA, RED, 2.2)
        s += line(x + 40, yA, x + 100, yA, RED, 2.2)
        x += 100
    s += text(540, yA - 56, "колір сталий; важлива частота (тема 13.1.2)", 10.5, GREY, "start")
    # аналог: нижчий сталий рівень
    yB = 320
    s += axis(yB, "аналог: рівний струм, міняємо РІВЕНЬ")
    s += line(90, yB - 26, 740, yB - 26, GREEN, 2.4)
    s += line(90, yB, 90, yB - 26, GREEN, 2.4)
    s += text(540, yB - 32, "без миготіння; на малих струмах колір трохи «пливе»", 10.5, GREY, "start")
    s += text(250, yB - 40, "рівень = яскравість", 10.5, GREEN, "middle")
    save("fig-13-1-5-5-dimming.svg", s)


# ── Рис. 13.1.5.6 — нитки LED: послідовно проти паралельно ────────────────────
def fig_led_strings():
    W, H = 760, 320
    s = header(W, H)
    s += text(W / 2, 34, "Нитки світлодіодів: послідовно проти паралельно", 18, INK, "middle", "bold")

    def led(x, y):
        return (line(x, y - 10, x, y + 10, INK, 1.8) + line(x, y - 10, x + 18, y, INK, 1.8)
                + line(x + 18, y - 10, x + 18, y + 10, INK, 1.8) + line(x, y + 10, x + 18, y, INK, 1.8))

    # послідовно: один струм крізь усі
    s += text(190, 78, "послідовно", 13, INK, "middle", "bold")
    yy = 130
    s += line(70, yy, 100, yy, INK, 2)
    px = 100
    for i in range(3):
        s += led(px, yy)
        s += line(px + 18, yy, px + 50, yy, INK, 2)
        px += 50
    s += arrow(75, yy, 95, yy, GREEN, 2)
    s += text(190, 168, "один струм крізь усі → яскравість однакова", 10.5, GREEN, "middle")
    s += text(190, 184, "але треба висока напруга (N × V_LED)", 10.5, GREY, "middle")
    # паралельно
    s += text(560, 78, "паралельно", 13, INK, "middle", "bold")
    for r in range(2):
        yy = 120 + r * 34
        s += line(430, yy, 460, yy, INK, 2)
        px = 460
        for i in range(2):
            s += led(px, yy)
            s += line(px + 18, yy, px + 40, yy, INK, 2)
            px += 40
        s += line(px, yy, px + 10, yy, INK, 2)
    s += text(560, 192, "нижча напруга, але струм між нитками", 10.5, "#b07d18", "middle")
    s += text(560, 208, "ділиться нерівно — треба балансувати", 10.5, "#b07d18", "middle")
    s += text(W / 2, 268, "Послідовно — однаковий струм даром, та висока напруга (тут і потрібен boost); паралельно — навпаки.",
              11.5, GREY, "middle", style="italic")
    s += text(W / 2, 290, "Бережися й обриву нитки: boost задере напругу до межі — потрібен захист від перенапруги.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-1-5-6-strings.svg", s)


def pathd(d, color=INK, w=1.6, dash=None, fill="none"):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w}"{da}/>\n'


def finger(cx, tip_y, color="#f0d2b4"):
    """Спрощений палець: округлений прямокутник, кінчик унизу на (cx, tip_y)."""
    return rect(cx - 15, tip_y - 78, 30, 78, color, "#b78a5a", 1.5, 15)


# ── Рис. 13.1.6.1 — дотик двома фізиками ─────────────────────────────────────
def fig_touch_overview():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 34, "Дотик двома фізиками: натиск проти ємності", 19, INK, "middle", "bold")
    cx = 210
    s += text(cx, 74, "РЕЗИСТИВНИЙ", 14, INK, "middle", "bold")
    s += rect(cx - 110, 168, 220, 8, "#cfe0ee", "#5d7e93", 1.4)
    s += rect(cx - 110, 132, 220, 8, "#cfe0ee", "#5d7e93", 1.4)
    for dx in (-72, -36, 36, 72):
        s += circle(cx + dx, 152, 3, GREY, GREY, 1)
    s += finger(cx, 126)
    s += line(cx, 140, cx, 168, RED, 2.4)
    s += text(cx, 196, "натиск зʼєднує два шари", 10.5, GREY, "middle")
    cx2 = 610
    s += text(cx2, 74, "ЄМНІСНИЙ", 14, INK, "middle", "bold")
    s += rect(cx2 - 110, 158, 220, 12, "#eaf3ff", "#9bbdd6", 1.4)
    s += rect(cx2 - 30, 170, 60, 6, "#caa24a", "#9a7d2e", 1.2)
    s += finger(cx2, 140)
    for dx in (-20, 0, 20):
        s += pathd(f"M {cx2 + dx} 142 Q {cx2 + dx * 1.5} 162 {cx2 + dx * 0.3} 173", GREEN, 1.4, "3 3")
    s += text(cx2, 196, "палець міняє ємність електрода", 10.5, GREY, "middle")
    s += text(W / 2, 250, "Резистивний відчуває МЕХАНІЧНИЙ натиск; ємнісний — ЕЛЕКТРИЧНУ присутність пальця.", 12, INK, "middle", "bold")
    s += text(W / 2, 276, "Звідси й уся різниця: чим торкатися, чи є мультитач, яка міцність і чіткість.", 11.5, GREY, "middle", style="italic")
    save("fig-13-1-6-1-overview.svg", s)


# ── Рис. 13.1.6.2 — резистивний: подільник напруги ───────────────────────────
def fig_resistive():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Резистивний дотик: контакт читається як подільник напруги", 18, INK, "middle", "bold")
    # розріз
    x0, x1 = 90, 470
    s += finger((x0 + x1) / 2 - 40, 96)
    s += rect(x0, 110, x1 - x0, 8, "#cfe0ee", "#5d7e93", 1.4)
    s += text(x1 + 8, 116, "верхній шар (гнучкий)", 10, "#5d7e93", "start")
    s += rect(x0, 150, x1 - x0, 8, "#cfe0ee", "#5d7e93", 1.4)
    s += text(x1 + 8, 156, "нижній шар", 10, "#5d7e93", "start")
    for dx in range(6):
        s += circle(x0 + 40 + dx * 70, 132, 3, GREY, GREY, 1)
    px = (x0 + x1) / 2 - 40
    s += line(px, 118, px, 150, RED, 2.4)
    s += text(px, 96 + 6, "", 1)
    s += text(px, 174, "точка контакту", 10, RED, "middle", "bold")
    # подільник: градієнт напруги по шару X
    gy = 250
    s += text(x0 - 4, gy - 22, "по шару X — градієнт напруги:", 11, INK, "start")
    s += line(x0, gy, x1, gy, INK, 3)
    s += plus(x0, gy, 8, RED)
    s += text(x0 - 4, gy + 24, "V₊ (3.3 В)", 10, RED, "middle")
    s += minus(x1, gy, 8, BLUE)
    s += text(x1 + 2, gy + 24, "0 В", 10, BLUE, "middle")
    tx = x0 + (x1 - x0) / 3
    s += line(tx, gy - 18, tx, gy + 10, GREEN, 2, "4 3")
    s += text(tx, gy - 24, "дотик", 10, GREEN, "middle", "bold")
    s += arrow(tx, gy + 24, 560, gy + 24, GREEN, 1.8)
    s += text(640, gy + 10, "АЦП читає", 11, INK, "middle")
    s += text(640, gy + 27, "≈ 2.2 В → X", 11, GREEN, "middle", "bold")
    s += text(640, gy + 50, "(потім міняють", 10, GREY, "middle")
    s += text(640, gy + 65, "ролі шарів → Y)", 10, GREY, "middle")
    s += text(W / 2, 340, "Два виміри подільника (X, тоді Y) дають координату. Працює з будь-чим: палець, рукавиця, стилус, бруд.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-1-6-2-resistive.svg", s)


# ── Рис. 13.1.6.3 — взаємна ємність на перетині ──────────────────────────────
def fig_pcap_mutual():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 34, "Проєктивно-ємнісний: палець краде поле на перетині", 18, INK, "middle", "bold")

    def panel(cx, finger_on, head):
        base = 244
        p1x, p2x = cx - 50, cx + 50
        out = text(cx, 70, head, 12.5, INK, "middle", "bold")
        out += rect(p1x - 24, base, 48, 10, "#caa24a", "#9a7d2e", 1.2)
        out += rect(p2x - 24, base, 48, 10, "#5d7e93", "#3f5b6d", 1.2)
        out += text(p1x, base + 24, "привід", 9.5, "#9a7d2e", "middle")
        out += text(p2x, base + 24, "сенс", 9.5, "#5d7e93", "middle")
        if not finger_on:
            for h in (30, 50, 70):
                out += pathd(f"M {p1x} {base} Q {cx} {base - 2 * h} {p2x} {base}", GREEN, 1.5)
            out += text(cx, base + 46, "повна взаємна ємність Cm", 10.5, GREEN, "middle", "bold")
        else:
            out += finger(cx, base - 70)
            for h in (24, 38):
                out += pathd(f"M {p1x} {base} Q {cx} {base - 2 * h} {p2x} {base}", GREEN, 1.5)
            out += pathd(f"M {p1x} {base} Q {cx - 34} {base - 96} {cx - 13} {base - 72}", RED, 1.5, "4 3")
            out += pathd(f"M {p2x} {base} Q {cx + 34} {base - 96} {cx + 13} {base - 72}", RED, 1.5, "4 3")
            out += text(cx, base + 46, "Cm падає → дотик помічено", 10.5, RED, "middle", "bold")
        return out

    s += panel(228, False, "без пальця")
    s += panel(600, True, "палець над перетином")
    s += line(414, 80, 414, 300, FAINT, 1.4, "4 5")
    s += text(W / 2, 322, "Контролер веде «привід», слухає «сенс» на кожному перетині рядок×стовпець; провал Cm видає, де торкнулися.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-1-6-3-pcap-mutual.svg", s)


# ── Рис. 13.1.6.4 — self проти mutual ────────────────────────────────────────
def fig_self_vs_mutual():
    W, H = 820, 330
    s = header(W, H)
    s += text(W / 2, 34, "Дві схеми вимірювання: self проти mutual", 19, INK, "middle", "bold")
    # self
    cx = 210
    s += text(cx, 74, "SELF — ємність на землю", 12.5, INK, "middle", "bold")
    s += finger(cx, 120)
    s += rect(cx - 50, 150, 100, 8, "#caa24a", "#9a7d2e", 1.2)
    s += text(cx, 172, "електрод", 9.5, "#9a7d2e", "middle")
    for dx in (-16, 0, 16):
        s += pathd(f"M {cx + dx} 122 Q {cx + dx} 138 {cx + dx} 150", GREEN, 1.4, "3 3")
    s += text(cx, 200, "палець додає ємність до землі (Cs росте)", 10, GREY, "middle")
    s += text(cx, 224, "просто, але два пальці → «привиди»", 10.5, "#b07d18", "middle", "bold")
    # mutual
    cx2 = 610
    s += text(cx2, 74, "MUTUAL — ємність рядок↔стовпець", 12.5, INK, "middle", "bold")
    s += finger(cx2, 120)
    s += rect(cx2 - 60, 150, 44, 8, "#caa24a", "#9a7d2e", 1.2)
    s += rect(cx2 + 16, 150, 44, 8, "#5d7e93", "#3f5b6d", 1.2)
    s += pathd(f"M {cx2 - 38} 150 Q {cx2} 120 {cx2 + 38} 150", GREEN, 1.5)
    s += pathd(f"M {cx2 - 38} 150 Q {cx2 - 10} 126 {cx2 - 6} 124", RED, 1.4, "4 3")
    s += text(cx2, 200, "палець краде поле між ними (Cm падає)", 10, GREY, "middle")
    s += text(cx2, 224, "кожен перетин окремо → справжній мультитач", 10.5, GREEN, "middle", "bold")
    s += text(W / 2, 286, "Тому сучасні екрани — mutual: сітка рядків і стовпців дає повну 2D-карту дотиків, а не одну пляму.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-1-6-4-self-mutual.svg", s)


# ── Рис. 13.1.6.5 — контролери дотику ────────────────────────────────────────
def fig_touch_controller():
    W, H = 820, 330
    s = header(W, H)
    s += text(W / 2, 34, "Контролери: резистивний — АЦП; ємнісний — розумний чип", 18, INK, "middle", "bold")
    # ємнісний ланцюг
    s += text(150, 84, "ЄМНІСНИЙ", 12.5, INK, "middle", "bold")
    s += rect(70, 100, 160, 70, "#fbfbfb", INK, 1.6, 4)
    for r in range(3):
        s += line(80, 116 + r * 18, 220, 116 + r * 18, "#caa24a", 1.4)
    for c in range(5):
        s += line(86 + c * 32, 106, 86 + c * 32, 164, "#5d7e93", 1.4)
    s += text(150, 184, "сітка електродів", 10, GREY, "middle")
    s += arrow(230, 135, 300, 135, INK, 2)
    s += rect(300, 104, 150, 62, "#eef2f5", INK, 1.8, 6)
    s += text(375, 128, "контролер", 12, INK, "middle", "bold")
    s += text(375, 146, "(FT6206/GT911)", 9.5, GREY, "middle")
    s += arrow(450, 135, 540, 135, INK, 2)
    s += text(495, 124, "I²C + INT", 10, GREEN, "middle", "bold")
    s += box(540, 104, 120, 62, "МК", "читає (x,y)")
    s += text(365, 196, "чип сам міряє фемтофаради, фільтрує, рахує центр дотику й видає координати",
              10.5, GREY, "middle", style="italic")
    # резистивний ланцюг
    s += text(150, 236, "РЕЗИСТИВНИЙ", 12.5, INK, "middle", "bold")
    s += rect(70, 250, 120, 44, "#fbfbfb", INK, 1.6, 4)
    s += text(130, 276, "4 дроти", 11, INK, "middle")
    s += arrow(190, 272, 250, 272, INK, 2)
    s += rect(250, 250, 110, 44, "#eef2f5", INK, 1.8, 6)
    s += text(305, 270, "АЦП", 12, INK, "middle", "bold")
    s += text(305, 286, "(або XPT2046)", 9, GREY, "middle")
    s += arrow(360, 272, 420, 272, INK, 2)
    s += box(420, 250, 110, 44, "МК")
    s += text(660, 272, "МК сам робить аналогову роботу", 10.5, GREY, "middle", style="italic")
    save("fig-13-1-6-5-controller.svg", s)


# ── Рис. 13.1.6.6 — порівняння резистивного й ємнісного ──────────────────────
def fig_touch_compare():
    W, H = 824, 280
    s = header(W, H)
    s += text(W / 2, 34, "Резистивний проти ємнісного: що під виріб", 19, INK, "middle", "bold")
    headers = ["", "Чим торкатися", "Мультитач", "Натиск", "Чіткість/міцність", "Середовище"]
    rows = [
        ("резистивний", [("будь-чим", "g"), ("ні (базово)", "b"), ("так, тиск", "n"), ("нижча, мʼякший", "b"), ("бруд, волога — ок", "g")]),
        ("ємнісний\n(PCAP)", [("палець/спец.", "n"), ("так", "g"), ("ні (дотик)", "n"), ("скло, чітке", "g"), ("боїться води/завад", "b")]),
    ]
    colw = [120, 130, 116, 116, 162, 158]
    tf = {"g": "#e7f5ea", "b": "#fdeceb", "n": "#fff8e8"}
    te = {"g": GREEN, "b": RED, "n": "#b07d18"}
    x0, y0, rowh = 22, 66, 64
    cx = x0
    for j, htxt in enumerate(headers):
        s += rect(cx, y0, colw[j], 36, "#eef0f2", GREY, 1.2)
        if htxt:
            s += text(cx + colw[j] / 2, y0 + 22, htxt, 11.5, INK, "middle", "bold")
        cx += colw[j]
    for i, (name, cells) in enumerate(rows):
        ry = y0 + 36 + i * rowh
        cx = x0
        s += rect(cx, ry, colw[0], rowh, "#f6f7f8", GREY, 1.2)
        parts = name.split("\n")
        if len(parts) == 2:
            s += text(cx + colw[0] / 2, ry + rowh / 2 - 4, parts[0], 11.5, INK, "middle", "bold")
            s += text(cx + colw[0] / 2, ry + rowh / 2 + 13, parts[1], 9.5, GREY, "middle")
        else:
            s += text(cx + colw[0] / 2, ry + rowh / 2 + 5, parts[0], 11.5, INK, "middle", "bold")
        cx += colw[0]
        for j, (txt, tone) in enumerate(cells):
            s += rect(cx, ry, colw[j + 1], rowh, tf[tone], GREY, 1.2)
            s += text(cx + colw[j + 1] / 2, ry + rowh / 2 + 4, txt, 10.5, te[tone], "middle", "bold")
            cx += colw[j + 1]
    s += text(W / 2, 262, "Промисловий пульт у рукавицях — резистивний; споживчий ґаджет із жестами — ємнісний.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-1-6-6-compare.svg", s)


def thumb(x, y, w, h, kind, label=None):
    """Мініатюра екрана e-ink: kind = img/black/white."""
    fill = "#1b1b1b" if kind == "black" else "#ffffff"
    out = rect(x, y, w, h, fill, INK, 1.4, 2)
    if kind == "img" and label:
        out += text(x + w / 2, y + h / 2 + 5, label, 14, INK, "middle", "bold")
    elif kind == "ghost" and label:
        out += rect(x, y, w, h, "#ffffff", INK, 1.4, 2)
        out += text(x + w / 2, y + h / 2 + 5, label, 14, INK, "middle", "bold")
        out += text(x + w / 2 - 2, y + h / 2 + 2, label, 14, "#d8d8d8", "middle", "bold")
    return out


# ── Рис. 13.1.7.1 — e-ink повільний (рухає речовину) ─────────────────────────
def fig_eink_speed():
    W, H = 820, 300
    s = header(W, H)
    s += text(W / 2, 34, "Оновлення e-ink повільне — бо рухає РЕЧОВИНУ, а не світло", 18, INK, "middle", "bold")
    s += text(W / 2, 55, "логарифмічна шкала часу одного оновлення пікселя", 12.5, GREY, "middle", style="italic")
    ax0, ax1, ay = 110, 720, 210
    lo, hi = 1e-6, 2.0

    def xp(t):
        return ax0 + (math.log10(t) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (ax1 - ax0)

    s += line(ax0, ay, ax1, ay, INK, 2)
    for t, lbl in [(1e-6, "1 мкс"), (1e-3, "1 мс"), (1e-2, "10 мс"), (1e-1, "100 мс"), (1.0, "1 с")]:
        s += line(xp(t), ay - 5, xp(t), ay + 5, INK, 1.3)
        s += text(xp(t), ay + 22, lbl, 10, GREY, "middle")
    marks = [("OLED ≈ 10 мкс", 1e-5, GREEN, 0), ("LCD ≈ 10 мс", 1e-2, BLUE, 1), ("e-ink ≈ 0.3–2 с", 0.6, RED, 0)]
    for (lbl, t, col, hi2) in marks:
        x = xp(t)
        yy = ay - 38 - hi2 * 34
        s += circle(x, ay, 6, col, col, 1)
        s += arrow(x, yy + 8, x, ay - 6, col, 1.6)
        s += text(x, yy, lbl, 11.5, col, "middle", "bold")
    s += text(W / 2, 274, "Світло й заряд перемикаються за мікросекунди; частинки пігменту повзуть у рідині — на порядки довше.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-1-7-1-speed.svg", s)


# ── Рис. 13.1.7.2 — хвилеформа e-ink ─────────────────────────────────────────
def fig_eink_waveform():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 34, "Хвилеформа: послідовність імпульсів, а не одне «увімкнути»", 18, INK, "middle", "bold")
    ox, oy, ax1 = 90, 180, 720
    s += line(ox, oy, ax1, oy, INK, 1.6)
    s += text(ax1, oy + 18, "час", 11, INK, "end")
    s += line(ox, oy - 60, ax1, oy - 60, GREY, 1, "4 3")
    s += line(ox, oy + 60, ax1, oy + 60, GREY, 1, "4 3")
    s += text(ox - 8, oy - 58, "+15 В", 10, RED, "end")
    s += text(ox - 8, oy + 64, "−15 В", 10, BLUE, "end")
    s += text(ox - 8, oy + 4, "0", 10, GREY, "end")
    seq = [(0, 40), (60, 70), (-60, 60), (60, 60), (-60, 70), (0, 90)]
    x = ox + 10
    py = oy
    for (lvl, dur) in seq:
        ny = oy - lvl
        s += line(x, py, x, ny, INK, 2.2)
        s += line(x, ny, x + dur, ny, INK, 2.2)
        x += dur
        py = ny
    s += text(360, oy - 90, "імпульси з таблиці (LUT)", 11, INK, "middle", "bold")
    s += text(x - 60, oy + 84, "наприкінці 0 В — піксель тримається сам", 10.5, GREEN, "middle", "bold")
    s += text(W / 2, 300, "Щоб точно перегнати частинки в потрібний стан (і градацію сірого), драйвер «програє» задану послідовність ±15 В.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-1-7-2-waveform.svg", s)


# ── Рис. 13.1.7.3 — повне оновлення (спалах) ─────────────────────────────────
def fig_eink_full_refresh():
    W, H = 820, 290
    s = header(W, H)
    s += text(W / 2, 34, "Повне оновлення: спалах інверсій чистить екран начисто", 18, INK, "middle", "bold")
    seq = [("img", "abc", "старе"), ("black", None, "чорне"), ("white", None, "біле"),
           ("black", None, "чорне"), ("img", "XYZ", "нове")]
    tw, th, y0 = 110, 90, 96
    gap = (820 - 40 - len(seq) * tw) / (len(seq) - 1)
    x = 20
    for i, (kind, lbl, cap) in enumerate(seq):
        s += thumb(x, y0, tw, th, kind, lbl)
        s += text(x + tw / 2, y0 + th + 18, cap, 10.5, GREY, "middle")
        if i < len(seq) - 1:
            s += arrow(x + tw + 4, y0 + th / 2, x + tw + gap - 4, y0 + th / 2, INK, 2)
        x += tw + gap
    s += text(W / 2, 256, "Кілька інверсій «перемішують» частинки до повного скидання — звідси видиме блимання й найдовший час, зате чистий, без привидів кадр.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-1-7-3-full-refresh.svg", s)


# ── Рис. 13.1.7.4 — часткове оновлення і привид ──────────────────────────────
def fig_eink_partial_ghost():
    W, H = 820, 300
    s = header(W, H)
    s += text(W / 2, 34, "Часткове оновлення: швидко й без спалаху — та копиться привид", 18, INK, "middle", "bold")
    # ліворуч: вікно оновлення
    x0, y0, tw, th = 80, 90, 150, 110
    s += thumb(x0, y0, tw, th, "white")
    s += text(x0 + tw / 2, y0 + 26, "12:00", 17, INK, "middle", "bold")
    s += rect(x0 + 36, y0 + 12, 78, 28, "none", GREEN, 2, 3)
    s += text(x0 + tw / 2, y0 + th + 18, "оновлюємо лише вікно", 10.5, GREEN, "middle")
    s += arrow(x0 + tw + 16, y0 + th / 2, x0 + tw + 70, y0 + th / 2, INK, 2)
    s += text(x0 + tw + 43, y0 + th / 2 - 10, "× багато", 10, GREY, "middle")
    # праворуч: накопичений привид
    x1 = x0 + tw + 86
    s += rect(x1, y0, tw, th, "#ffffff", INK, 1.4, 2)
    s += text(x1 + tw / 2, y0 + 26, "12:47", 17, INK, "middle", "bold")
    for gx, gy, gt in [(x1 + 40, 24, "12:"), (x1 + 64, 24, "0")]:
        s += text(gx, y0 + gy, gt, 17, "#dcdcdc", "middle", "bold")
    s += text(x1 + tw / 2, y0 + th + 18, "привиди старих цифр", 10.5, "#b07d18", "middle")
    s += text(560, 120, "Пропускаємо спалах-скидання → оновлення", 11, INK, "start")
    s += text(560, 138, "за десятки мс, без блимання, лише в вікні.", 11, INK, "start")
    s += text(560, 166, "Але частинки не сідають до кінця, і сліди", 11, "#b07d18", "start")
    s += text(560, 184, "старого копичаться — час від часу треба", 11, "#b07d18", "start")
    s += text(560, 202, "повне оновлення, щоб стерти привид.", 11, "#b07d18", "start")
    save("fig-13-1-7-4-partial-ghost.svg", s)


# ── Рис. 13.1.7.5 — температура командує ─────────────────────────────────────
def fig_eink_temperature():
    W, H = 760, 360
    s = header(W, H)
    s += text(W / 2, 34, "Температура командує: на холоді частинки повзуть ледь-ледь", 18, INK, "middle", "bold")
    ox, oy, ax1, ay1 = 96, 300, 690, 86

    def X(t):
        return ox + (t + 10) / 50.0 * (ax1 - ox)

    def Y(s2):
        return oy - s2 / 3.0 * (oy - ay1)

    s += arrow(ox, oy, ax1 + 6, oy, INK, 2)
    s += arrow(ox, oy, ox, ay1 - 6, INK, 2)
    for t in (-10, 0, 10, 20, 30, 40):
        s += line(X(t), oy, X(t), oy + 5, INK, 1.3)
        s += text(X(t), oy + 20, str(t) + "°", 10, GREY, "middle")
    s += text(ax1, oy + 22, "темп., °C", 11, INK, "end")
    s += text(ox - 8, ay1 - 6, "час оновлення", 11, INK, "start")
    pts = [(-10, 3.0), (0, 2.0), (10, 1.2), (20, 0.7), (30, 0.5), (40, 0.4)]
    for j in range(len(pts) - 1):
        s += line(X(pts[j][0]), Y(pts[j][1]), X(pts[j + 1][0]), Y(pts[j + 1][1]), RED, 2.6)
    s += line(X(0), oy, X(0), ay1, BLUE, 1.4, "5 4")
    s += text(X(-5), ay1 + 18, "нижче 0 °C —", 10, BLUE, "middle", "bold")
    s += text(X(-5), ay1 + 33, "часто не оновити", 10, BLUE, "middle")
    s += text(X(32), Y(0.4) - 16, "тепло — швидко", 10.5, GREEN, "middle", "bold")
    s += text(W / 2, 338, "Тому контролер читає термодавач і бере хвилеформу (LUT) під поточну температуру — інакше привид або зрив оновлення.",
              11, GREY, "middle", style="italic")
    save("fig-13-1-7-5-temperature.svg", s)


# ── Рис. 13.1.7.6 — як цим керують ───────────────────────────────────────────
def fig_eink_driving():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 34, "Керування e-ink: хост, контролер із LUT і високовольтні шини", 18, INK, "middle", "bold")
    s += box(60, 130, 130, 80, "хост (МК)", "образ + режим")
    s += arrow(190, 170, 250, 170, INK, 2)
    s += text(220, 159, "SPI", 10, GREEN, "middle", "bold")
    s += rect(250, 108, 230, 124, "#eef2f5", INK, 1.8, 6)
    s += text(365, 130, "контролер e-ink", 12.5, INK, "middle", "bold")
    s += text(365, 152, "генератор хвилеформ", 10, GREY, "middle")
    s += text(365, 172, "LUT за температурою", 10, GREY, "middle")
    s += text(365, 192, "зарядна помпа ±15 В", 10, "#9a7d2e", "middle")
    s += box(548, 130, 200, 80, "панель", "драйвери + капсули")
    s += arrow(480, 170, 548, 170, INK, 2)
    s += text(514, 159, "рядки/", 9, GREY, "middle")
    s += text(514, 186, "стовпці", 9, GREY, "middle")
    s += rect(300, 256, 130, 30, "#fff8e0", "#caa24a", 1.4, 4)
    s += text(365, 276, "термодавач", 10.5, "#9a7d2e", "middle")
    s += arrow(365, 256, 365, 232, "#caa24a", 1.8)
    s += text(W / 2, 308, "Хост лише шле образ і команду «онови (повністю / частково)»; усю важку хвилеформну роботу й високу напругу робить контролер.",
              11, GREY, "middle", style="italic")
    save("fig-13-1-7-6-driving.svg", s)


def bichromal(cx, cy, r, black_top):
    """Двоколірна кулька Gyricon: одна півкуля чорна, інша біла."""
    out = circle(cx, cy, r, "#ffffff", INK, 1.6)
    sweep = 1 if black_top else 0
    out += pathd(f"M {cx - r:.1f} {cy:.1f} A {r:.1f} {r:.1f} 0 0 {sweep} {cx + r:.1f} {cy:.1f} Z", "none", 0, None, "#1b1b1b")
    out += circle(cx, cy, r, "none", INK, 1.6)
    return out


# ── Рис. 13.1.7і.1 — два механізми електронного паперу ───────────────────────
def fig_eink_hist_mechanisms():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Дві мрії про електронний папір: кулька проти капсули", 18, INK, "middle", "bold")
    cx = 210
    s += text(cx, 72, "GYRICON — обертання кульки", 12.5, INK, "middle", "bold")
    for (sx, black_top, lab) in [(cx - 62, False, "видно біле"), (cx + 62, True, "видно чорне")]:
        s += circle(sx, 152, 30, "#eef4f8", "#9bbdd6", 1.2)
        s += bichromal(sx, 152, 22, black_top)
        s += (minus(sx, 112, 7) if not black_top else plus(sx, 112, 7))
        s += (plus(sx, 192, 7) if not black_top else minus(sx, 192, 7))
        s += text(sx, 224, lab, 10, GREY, "middle")
    s += text(cx, 250, "двоколірна кулька в олії повертається полем", 10.5, GREY, "middle")
    cx2 = 610
    s += text(cx2, 72, "E INK — переміщення частинок", 12.5, INK, "middle", "bold")
    for (sx, white_up, lab) in [(cx2 - 62, True, "видно біле"), (cx2 + 62, False, "видно чорне")]:
        s += circle(sx, 152, 30, "#f4fbff", "#7fa9c4", 1.6)
        wy = 138 if white_up else 166
        by = 166 if white_up else 138
        for dx in (-11, 0, 11):
            s += circle(sx + dx, wy, 5, "#ffffff", "#9bbdd6", 1)
            s += circle(sx + dx, by, 4, "#2b2f33", "#2b2f33", 1)
        s += (minus(sx, 112, 7) if white_up else plus(sx, 112, 7))
        s += (plus(sx, 192, 7) if white_up else minus(sx, 192, 7))
        s += text(sx, 224, lab, 10, GREY, "middle")
    s += text(cx2, 250, "білі й чорні частинки в капсулі переганяє поле", 10.5, GREY, "middle")
    s += text(W / 2, 300, "Обидві дають чорно-білий відбивний бістабільний піксель — Gyricon крутить кульку, E Ink переміщає частинки.",
              11.5, GREY, "middle", style="italic")
    s += text(W / 2, 324, "Перемогла капсула: саме мікрокапсула розвʼязала давню біду електрофорезу — злипання частинок.",
              11.5, INK, "middle", "bold")
    save("fig-13-1-7i-1-mechanisms.svg", s)


# ── Рис. 13.1.7і.2 — таймлайн електронного паперу ────────────────────────────
def fig_eink_hist_timeline():
    W, H = 880, 500
    s = header(W, H)
    s += text(W / 2, 36, "Електронний папір: від ідеї до Kindle", 20, INK, "middle", "bold")
    s += text(W / 2, 57, "ідея електрофорезу — з 1970-х; до приладу в кожних руках — понад 35 років", 12.5, GREY, "middle", style="italic")
    spine = 250
    top, bot = 92, H - 30
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("~1970", "Ота / Ota · Matsushita", "Електрофорез: рухати заряджені частинки полем — але вони ЗЛИПАЮТЬСЯ", False),
        ("1974", "Шерідон / Sheridon · Xerox PARC", "Gyricon: двоколірні кульки крутяться полем — перший «електронний папір»", False),
        ("1980-ті", "Xerox кладе Gyricon на полицю", "Ідея є, продукту нема — знайома історія, як з LCD у RCA", True),
        ("1995", "Джейкобсон / Jacobson · MIT", "Мрія про «останню книгу»: сторінки, що міняються; бере двох студентів", False),
        ("1997", "Коміскі + Альберт / Comiskey + Albert", "МІКРОКАПСУЛА розвʼязує злипання — робочий прототип; засновано E Ink", False),
        ("2007", "Amazon Kindle", "Електронний папір у кожних руках — мрія стала товаром", False),
    ]
    n = len(nodes)
    for i, (yr, who, q, faint) in enumerate(nodes):
        y = top + 24 + (bot - top - 44) * i / (n - 1)
        col = BLUE if faint else INK
        if i == 4:
            s += circle(spine, y, 10.5, RED, RED, 3)
            s += circle(spine, y, 5, "#fff", "#fff", 0)
        else:
            s += circle(spine, y, 7, "#fff", col, 2.6)
        s += text(spine - 22, y + 5, yr, 12.5, GREY, "end", "bold")
        s += text(spine + 26, y - 3, who, 15, (RED if i == 4 else col), "start", "bold")
        s += text(spine + 26, y + 16, q, 12, INK if not faint else "#4a5a86", "start", style="italic")
    s += text(W / 2, H - 6, "Ідею мали в Японії, перший папір зробили в Xerox, а спрацювати все змусила мікрокапсула з MIT.",
              12, GREY, "middle", style="italic")
    save("fig-13-1-7i-2-timeline.svg", s)


# ── Рис. 13.1.8.1 — лійка вибору: сценарій → обмеження → технологія ───────────
def fig_choose_funnel():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Вибір дисплея: від СЦЕНАРІЮ до технології, а не навпаки", 18, INK, "middle", "bold")
    bands = [
        (700, 70, "#eef4f8", "СЦЕНАРІЙ", "хто? де? що показує? як часто? скільки живе? почім? у якому корпусі?"),
        (540, 158, "#fff8e0", "ТВЕРДІ ОБМЕЖЕННЯ", "світло · енергія · вартість · кабель · розмір · дотик"),
        (360, 246, "#e7f5ea", "КАНДИДАТИ", "TFT-LCD · OLED · e-ink"),
    ]
    for (w, y, fill, head, sub) in bands:
        s += rect(W / 2 - w / 2, y, w, 60, fill, INK, 1.6, 8)
        s += text(W / 2, y + 24, head, 13, INK, "middle", "bold")
        s += text(W / 2, y + 44, sub, 11.5, GREY, "middle")
    s += arrow(W / 2, 130, W / 2, 156, INK, 2.4)
    s += text(W / 2 + 90, 148, "вивести", 10, GREY, "middle")
    s += arrow(W / 2, 218, W / 2, 244, INK, 2.4)
    s += text(W / 2 + 90, 236, "звузити", 10, GREY, "middle")
    s += text(W / 2, 336, "Спершу обмеження викидають більшість варіантів — і лише потім порівнюємо те, що лишилось.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-1-8-1-funnel.svg", s)


# ── Рис. 13.1.8.2 — світлове середовище → клас ───────────────────────────────
def fig_environment_class():
    W, H = 820, 300
    s = header(W, H)
    s += text(W / 2, 34, "Сонце: світлове середовище — перший фільтр", 19, INK, "middle", "bold")
    regions = [
        (80, 250, "#2a2f36", "#ffffff", "темрява", "OLED — ідеальний чорний"),
        (250, 450, "#cfe0ee", INK, "кімната", "TFT-LCD або OLED"),
        (450, 600, "#fff0c2", INK, "яскравий день", "яскравий TFT + антивідблиск"),
        (600, 760, "#f7d7c0", INK, "пряме сонце", "e-ink / трансфлектив"),
    ]
    for (xa, xb, fill, tcol, lbl, rec) in regions:
        s += rect(xa, 120, xb - xa, 44, fill, GREY, 1.2)
        s += text((xa + xb) / 2, 147, lbl, 11.5, tcol, "middle", "bold")
        s += text((xa + xb) / 2, 186, rec, 10.5, INK, "middle", "bold")
    s += text(80, 104, "менше світла довкола", 10, GREY, "start")
    s += text(760, 104, "більше світла довкола →", 10, GREY, "end")
    s += text(W / 2, 240, "Де темно — світи сам (OLED); де яскраво — відбивай чуже світло (e-ink). Це часто відсіває клас одразу.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-1-8-2-environment.svg", s)


# ── Рис. 13.1.8.3 — енергія: 2×2 рішення ─────────────────────────────────────
def fig_energy_decision():
    W, H = 760, 360
    s = header(W, H)
    s += text(W / 2, 34, "Енергія: живлення × вміст відсівають половину", 19, INK, "middle", "bold")
    gx, gy, cw, ch = 220, 90, 230, 100
    cells = [
        (0, 0, "e-ink", "≈0 у спокої — місяці", "#e7f5ea", GREEN),
        (1, 0, "OLED (темний UI)", "світло лише там, де треба", "#fff8e8", "#b07d18"),
        (0, 1, "будь-який", "живлення не тисне", "#eef4f8", INK),
        (1, 1, "TFT або OLED", "повна свобода", "#eef4f8", INK),
    ]
    for (cxi, ryi, t1, t2, fill, col) in cells:
        x = gx + cxi * cw
        y = gy + ryi * ch
        s += rect(x, y, cw, ch, fill, INK, 1.4)
        s += text(x + cw / 2, y + 40, t1, 13, col, "middle", "bold")
        s += text(x + cw / 2, y + 64, t2, 10, GREY, "middle")
    s += text(gx + cw / 2, gy - 14, "статичний вміст", 11, INK, "middle", "bold")
    s += text(gx + cw + cw / 2, gy - 14, "динамічний вміст", 11, INK, "middle", "bold")
    s += text(gx - 12, gy + ch / 2, "батарея", 11, INK, "end", "bold")
    s += text(gx - 12, gy + ch + ch / 2, "мережа", 11, INK, "end", "bold")
    s += text(W / 2, 320, "Найжорсткіший кут — батарея + статичний вміст: тут e-ink поза конкуренцією. Мережа знімає питання.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-1-8-3-energy.svg", s)


# ── Рис. 13.1.8.4 — справжня ціна дисплея ────────────────────────────────────
def fig_true_cost():
    W, H = 760, 380
    s = header(W, H)
    s += text(W / 2, 34, "Вартість: ціна не лише в самій панелі", 19, INK, "middle", "bold")
    base = 320
    # видима ціна
    s += rect(150, base - 60, 90, 60, "#cfe0ee", INK, 1.4)
    s += text(195, base - 28, "панель", 11, INK, "middle", "bold")
    s += text(195, base + 20, "«видима ціна»", 11, GREY, "middle")
    # справжня ціна — стос
    stack = [("панель", "#cfe0ee", 40), ("контролер", "#dfe6ea", 26), ("драйвер підсвітки", "#fff4c2", 24),
             ("контролер дотику", "#e7f5ea", 24), ("розʼєм + шлейф", "#f3e0e0", 22),
             ("більший МК", "#e0e0f0", 28), ("більша батарея", "#f7d7c0", 30)]
    x = 470
    y = base
    for (lbl, fill, h) in stack:
        s += rect(x - 70, y - h, 140, h, fill, INK, 1.2)
        s += text(x, y - h / 2 + 4, lbl, 9.5, INK, "middle")
        y -= h
    s += text(x, y - 12, "«справжня ціна»", 11, RED, "middle", "bold")
    s += arrow(270, base - 30, 392, base - 60, GREY, 1.8, "5 4")
    s += text(330, base - 58, "тягне за собою", 10, GREY, "middle")
    s += text(W / 2, 354, "Панель тягне контролер, драйвери, розʼєм — і часто диктує дорожчий МК та більшу батарею. Рахуйте все.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-1-8-4-cost.svg", s)


# ── Рис. 13.1.8.5 — фізичний слід: кабель, розʼєм, монтаж ─────────────────────
def fig_display_footprint():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 34, "Кабель: інтерфейс, розʼєм і механіка — теж критерій", 18, INK, "middle", "bold")
    # панель
    s += rect(90, 90, 230, 150, "#eaf3ff", "#5d7e93", 1.8, 4)
    s += text(205, 168, "панель", 13, "#5d7e93", "middle", "bold")
    for (mx, my) in [(102, 102), (308, 102), (102, 228), (308, 228)]:
        s += circle(mx, my, 5, "#fff", GREY, 1.4)
    s += text(205, 256, "отвори/клей кріплення", 9.5, GREY, "middle")
    # FPC шлейф
    s += pathd("M 320 215 C 380 215 400 250 470 250", "#caa24a", 8)
    s += text(400, 238, "шлейф (FPC)", 10, "#9a7d2e", "middle")
    # розʼєм на платі
    s += rect(470, 238, 70, 24, "#2a2f36", INK, 1.4, 2)
    s += text(505, 254, "розʼєм", 9.5, "#ffffff", "middle")
    s += rect(470, 262, 250, 60, "#f2f2f2", GREY, 1.4, 3)
    s += text(595, 296, "плата (МК)", 11, GREY, "middle")
    s += arrow(540, 250, 600, 250, INK, 1.8)
    s += text(640, 246, "N контактів", 10, INK, "middle")
    s += text(640, 262, "(інтерфейс → §13.1.3)", 9, GREY, "middle")
    s += text(560, 120, "Слабкі місця інтеграції:", 11, RED, "start", "bold")
    s += text(560, 140, "• розʼєм FPC — часта точка відмови", 10, INK, "start")
    s += text(560, 158, "• число контактів = тип інтерфейсу", 10, INK, "start")
    s += text(560, 176, "• кріплення, рамка, ущільнення", 10, INK, "start")
    s += text(560, 194, "• товщина стосу зі склом і дотиком", 10, INK, "start")
    save("fig-13-1-8-5-footprint.svg", s)


# ── Рис. 13.1.8.6 — приклад: два вироби, дві відповіді ───────────────────────
def fig_decision_scorecard():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 34, "Той самий метод — дві різні відповіді", 19, INK, "middle", "bold")

    def card(cx, title, rows, pick, pick_col):
        out = rect(cx - 170, 64, 340, 210, "#fbfbfb", INK, 1.6, 8)
        out += text(cx, 88, title, 13, INK, "middle", "bold")
        y = 112
        for (k, v) in rows:
            out += text(cx - 154, y, k, 10.5, GREY, "start")
            out += text(cx + 154, y, v, 10.5, INK, "end", "bold")
            y += 22
        out += rect(cx - 120, 230, 240, 32, pick_col, INK, 1.6, 6)
        out += text(cx, 251, pick, 12.5, INK, "middle", "bold")
        return out

    s += card(220, "Польовий лічильник",
              [("середовище", "вулиця, сонце"), ("живлення", "батарея, роки"),
               ("вміст", "число раз на хв"), ("дотик", "кнопки"), ("ціна", "низька")],
              "→ e-ink", "#e7f5ea")
    s += card(600, "Кухонний прилад",
              [("середовище", "кімната"), ("живлення", "мережа"),
               ("вміст", "анімація, жести"), ("дотик", "мультитач"), ("ціна", "середня")],
              "→ TFT-LCD + ємнісний дотик", "#eef4f8")
    s += text(W / 2, 300, "Жодна відповідь не «правильніша» — кожна випливає зі свого сценарію. У цьому вся суть вибору.",
              11.5, GREY, "middle", style="italic")
    s += text(W / 2, 322, "Обирайте дисплей РАНО: він формує і МК, і живлення, і корпус — пізно міняти його боляче.",
              11.5, INK, "middle", "bold")
    save("fig-13-1-8-6-scorecard.svg", s)


# ── Рис. 13.1.1c.1 — сторінкова відеопамʼять SSD1306 ─────────────────────────
def fig_ssd1306_pages():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 34, "SSD1306: відеопамʼять — 8 сторінок, байт = 8 вертикальних пікселів", 17, INK, "middle", "bold")
    gx, gy, gw = 78, 92, 410
    for p in range(8):
        py = gy + p * 28
        s += rect(gx, py, gw, 28, "#f0f4f7" if p % 2 == 0 else "#fbfbfb", GREY, 1)
        s += text(gx - 8, py + 18, "стор." + str(p), 10, GREY, "end")
    s += text(gx + gw / 2, gy - 8, "128 стовпців →", 10, GREY, "middle")
    colx = gx + 196
    s += rect(colx, gy + 2 * 28, 6, 28, "#dff0e2", GREEN, 1.8)
    zx, zy, cell = 588, 108, 24
    s += text(zx + cell / 2, zy - 12, "1 байт = 1 стовпець сторінки", 11, INK, "middle", "bold")
    bits = [1, 1, 0, 1, 0, 0, 1, 0]
    for b in range(8):
        yy = zy + b * cell
        s += rect(zx, yy, cell, cell, INK if bits[b] else "#ffffff", INK, 1.2)
        s += text(zx - 8, yy + cell / 2 + 4, "b" + str(b), 9, GREY, "end")
        s += text(zx + cell + 8, yy + cell / 2 + 4, ("1" if bits[b] else "0"), 10, (INK if bits[b] else GREY), "start")
    s += text(zx + cell / 2, zy + 8 * cell + 18, "8 вертикальних", 10, GREY, "middle")
    s += text(zx + cell / 2, zy + 8 * cell + 32, "пікселів", 10, GREY, "middle")
    s += arrow(colx + 6, gy + 2 * 28 + 14, zx - 12, zy + 4 * cell, GREEN, 1.6, "4 3")
    s += text(W / 2, 352, "8 сторінок × 128 стовпців = 1024 байти (1 КБ). Щоб змінити 1 піксель, чіпаєш цілий байт-стовпець із 8 пікселів.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-1-1c-1-pages.svg", s)


# ── Рис. 13.1.3m.1 — бюджет: потрібно проти того, що дає шина ─────────────────
def fig_bw_budget_check():
    W, H = 820, 330
    s = header(W, H)
    s += text(W / 2, 34, "Бюджет: ПОТРІБНО (з накладними) проти ДАЄ шина (з ефективністю)", 17, INK, "middle", "bold")
    ax0, ax1, ay = 130, 760, 272

    def xp(v):
        return ax0 + v / 120.0 * (ax1 - ax0)

    s += line(ax0, ay, ax1, ay, INK, 2)
    for v in (0, 40, 80, 120):
        s += line(xp(v), ay - 4, xp(v), ay + 4, INK, 1.3)
        s += text(xp(v), ay + 20, str(v), 10, GREY, "middle")
    s += text(ax1 + 4, ay + 20, "Мбіт/с", 10, INK, "start")
    # стеля шини SPI 40, ефективна 32
    s += line(xp(40), 86, xp(40), ay, BLUE, 1.6, "5 4")
    s += text(xp(40), 78, "SPI 40 МГц", 10, BLUE, "middle", "bold")
    s += line(xp(32), 100, xp(32), ay, "#9aa7c8", 1.4, "3 3")
    s += text(xp(32), 250, "ефект. ≈32", 9, "#6a78a0", "middle")
    # рядок 1 — повний кадр
    y1 = 130
    s += rect(ax0, y1 - 13, xp(74) - ax0, 22, "#fdeceb", RED, 1.4)
    s += rect(xp(74), y1 - 13, xp(92) - xp(74), 22, "#f3c0bd", "#c0271e", 1.2)
    s += text(ax0, y1 - 22, "повний кадр 320×240@60", 10, INK, "start", "bold")
    s += text(xp(92) + 8, y1, "≈92 ✗ не влазить", 10.5, RED, "start", "bold")
    s += text(xp(74) / 2 + ax0 / 2, y1 + 2, "74 + накладні", 8.5, "#7a2a24", "middle")
    # рядок 2 — часткове
    y2 = 196
    s += rect(ax0, y2 - 13, max(3, xp(0.6) - ax0), 22, "#cdeccd", GREEN, 1.4)
    s += text(ax0, y2 - 22, "часткове 100×40@10 (розумна панель)", 10, INK, "start", "bold")
    s += text(ax0 + 16, y2, "≈0.6 Мбіт/с ✓ влазить легко", 10.5, GREEN, "start", "bold")
    s += text(W / 2, 312, "Перевірка: D·(1+накладні) ≤ C·ефективність. Розумна панель шле лише зміни — і бюджет падає в рази.",
              11.5, GREY, "middle", style="italic")
    save("fig-13-1-3m-1-budget.svg", s)


# ── Рис. 13.1.4c.1 — SPI-TFT: вікно адрес + DMA ──────────────────────────────
def fig_spi_tft_dma():
    W, H = 820, 370
    s = header(W, H)
    s += text(W / 2, 32, "SPI-TFT (ST7789 / ILI9341): вікно адрес + DMA женуть пікселі", 17, INK, "middle", "bold")
    s += rect(60, 80, 150, 120, "#eef2f5", INK, 1.8, 6)
    s += text(135, 100, "МК", 13, INK, "middle", "bold")
    s += rect(76, 116, 118, 34, "#e0e0f0", INK, 1.4, 4)
    s += text(135, 138, "DMA", 12, INK, "middle", "bold")
    s += rect(580, 72, 180, 140, "#f4f7f9", INK, 1.8, 8)
    s += text(670, 66, "модуль SPI-TFT", 10, GREY, "middle")
    s += rect(598, 90, 164, 48, "#dfe6ea", "#5d7e93", 1.4, 3)
    s += text(680, 110, "контролер + GRAM", 10.5, INK, "middle", "bold")
    s += rect(598, 146, 164, 50, "#eaf3ff", "#9bbdd6", 1.4, 3)
    s += text(680, 167, "TFT-скло", 10.5, "#5d7e93", "middle", "bold")
    s += text(680, 185, "+ підсвітка", 9, "#9a7d2e", "middle")
    pins = [("SCK", INK), ("MOSI", INK), ("CS", GREY), ("DC", GREY), ("RST", GREY), ("BLK", "#9a7d2e")]
    for i, (nm, col) in enumerate(pins):
        y = 96 + i * 17
        s += line(210, y, 580, y, col, 1.6)
        s += text(395, y - 4, nm, 9.5, col, "middle")
    cy = 272
    s += text(72, cy - 24, "послідовність малювання вікна:", 11, INK, "start", "bold")
    steps = [("DC=0", "0x2A", "стовпці", GREY), ("DC=0", "0x2B", "рядки", GREY),
             ("DC=0", "0x2C", "писати", GREY), ("DC=1", "RGB565", "← DMA", GREEN)]
    x = 78
    for k, (dc, cmd, sub, col) in enumerate(steps):
        s += rect(x, cy - 14, 148, 46, "#fbfbfb", col, 1.5, 4)
        s += text(x + 18, cy + 4, dc, 9, GREY, "start")
        s += text(x + 90, cy - 1, cmd, 12, INK, "middle", "bold")
        s += text(x + 90, cy + 16, sub, 9.5, col, "middle")
        if k < 3:
            s += arrow(x + 148, cy + 8, x + 170, cy + 8, INK, 1.8)
        x += 170
    s += text(W / 2, 344, "RGB565 = 2 байти/піксель; DMA жене їх у задане вікно, поки CPU рахує наступне. Без DMA процесор стоїть над кожним байтом.",
              11, GREY, "middle", style="italic")
    save("fig-13-1-4c-1-spi-tft.svg", s)


# ── Рис. 13.1.5c.1 — boost-драйвер підсвітки зі зворотним звʼязком по струму ──
def fig_backlight_driver_ic():
    W, H = 820, 380
    s = header(W, H)
    s += text(W / 2, 32, "Boost-драйвер підсвітки: задаєш Rₛ — чип сам тримає струм", 17, INK, "middle", "bold")
    icx, icy, icw, ich = 250, 150, 150, 120
    s += rect(icx, icy, icw, ich, "#eef2f5", INK, 1.8, 6)
    s += text(icx + icw / 2, icy + 32, "boost-драйвер", 12, INK, "middle", "bold")
    s += text(icx + icw / 2, icy + 52, "(TPS61165-клас)", 9.5, GREY, "middle")
    swy = icy + 30
    s += text(60, swy + 4, "Vᵢₙ", 12, INK, "end", "bold")
    s += line(64, swy, 96, swy, INK, 2)
    lx = 96
    for k in range(4):
        s += line(lx + k * 14, swy, lx + k * 14 + 7, swy - 10, INK, 1.8)
        s += line(lx + k * 14 + 7, swy - 10, lx + k * 14 + 14, swy, INK, 1.8)
    s += text(lx + 28, swy - 18, "L", 11, INK, "middle")
    s += line(lx + 56, swy, icx, swy, INK, 2)
    s += text(icx - 6, swy - 6, "SW", 8.5, GREY, "end")
    eny = icy + 92
    s += line(icx, eny, 196, eny, INK, 2)
    s += text(icx - 6, eny - 4, "EN", 8.5, GREY, "end")
    s += text(150, eny - 14, "ШІМ-димінг", 9, GREEN, "middle")
    sx = 138
    s += line(sx, eny + 12, sx + 8, eny + 12, GREEN, 1.6)
    s += line(sx + 8, eny + 12, sx + 8, eny + 4, GREEN, 1.6)
    s += line(sx + 8, eny + 4, sx + 18, eny + 4, GREEN, 1.6)
    s += line(sx + 18, eny + 4, sx + 18, eny + 12, GREEN, 1.6)
    s += line(sx + 18, eny + 12, sx + 28, eny + 12, GREEN, 1.6)
    voutx = icx + icw
    s += line(voutx, swy, 560, swy, INK, 2)
    s += text(voutx + 6, swy - 8, "Vout (скільки треба)", 9, GREY, "start")
    lsx = 560
    s += line(lsx, swy, lsx, swy + 8, INK, 2)
    yy = swy + 8
    for i in range(4):
        s += line(lsx - 10, yy, lsx + 10, yy, INK, 1.8)
        s += line(lsx - 10, yy, lsx, yy + 15, INK, 1.8)
        s += line(lsx + 10, yy, lsx, yy + 15, INK, 1.8)
        s += line(lsx, yy + 15, lsx, yy + 23, INK, 2)
        yy += 23
    rsy = yy
    s += rect(lsx - 22, rsy, 44, 20, "#ffffff", INK, 1.6)
    s += text(lsx, rsy + 14, "Rₛ", 11, INK, "middle", "bold")
    s += line(lsx, rsy + 20, lsx, rsy + 36, INK, 2)
    s += line(lsx - 14, rsy + 36, lsx + 14, rsy + 36, INK, 2)
    s += line(lsx, rsy, lsx + 56, rsy, GREY, 1.6)
    s += line(lsx + 56, rsy, lsx + 56, eny, GREY, 1.6)
    s += line(lsx + 56, eny, voutx, eny, GREY, 1.6)
    s += text(voutx + 6, eny - 4, "FB", 8.5, GREY, "start")
    s += text(lsx + 60, rsy - 6, "струм «читає» Rₛ", 9, GREY, "start")
    s += rect(120, 304, 300, 38, "#e7f5ea", GREEN, 1.4, 6)
    s += text(270, 328, "I_LED = V_FB(ref) ÷ Rₛ", 13, INK, "middle", "bold")
    s += text(W / 2, 366, "Чип піднімає Vout рівно до тієї, за якої крізь нитку йде заданий Rₛ струм. Обрив нитки → Vout злітає → потрібен OVP.",
              10.5, GREY, "middle", style="italic")
    save("fig-13-1-5c-1-driver.svg", s)


# ── Рис. 13.1.6c.1 — контролер дотику: INT + I²C ─────────────────────────────
def fig_touch_ctrl_i2c():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 32, "Ємнісний контролер дотику: INT + I²C віддають готові точки", 17, INK, "middle", "bold")
    s += rect(60, 92, 116, 90, "#fbfbfb", GREY, 1.2)
    for r in range(3):
        s += line(66, 104 + r * 24, 170, 104 + r * 24, "#caa24a", 1.2)
    for c in range(5):
        s += line(74 + c * 22, 98, 74 + c * 22, 176, "#5d7e93", 1.2)
    s += text(118, 198, "сітка електродів", 9.5, GREY, "middle")
    s += arrow(176, 137, 222, 137, INK, 2)
    s += rect(222, 102, 150, 72, "#eef2f5", INK, 1.8, 6)
    s += text(297, 130, "контролер", 12, INK, "middle", "bold")
    s += text(297, 148, "(FT6206/GT911)", 9.5, GREY, "middle")
    s += line(372, 120, 524, 120, RED, 1.8)
    s += text(448, 112, "INT (є дотик!)", 9.5, RED, "middle", "bold")
    s += line(372, 150, 524, 150, INK, 1.8)
    s += text(448, 144, "I²C (SCL/SDA)", 9.5, INK, "middle")
    s += rect(524, 102, 120, 72, "#eef2f5", INK, 1.8, 6)
    s += text(584, 130, "МК", 12, INK, "middle", "bold")
    s += text(584, 150, "читає точки", 9.5, GREY, "middle")
    cy = 258
    s += text(72, cy - 24, "коли INT↓ — хост вичитує буфер точок по I²C:", 11, INK, "start", "bold")
    seq = [("лічильник", "= 2 дотики", GREY), ("точка 0", "X, Y · id 0", GREEN), ("точка 1", "X, Y · id 1", BLUE)]
    x = 72
    for k, (t1, t2, col) in enumerate(seq):
        s += rect(x, cy - 14, 200, 46, "#fbfbfb", col, 1.5, 4)
        s += text(x + 100, cy + 1, t1, 12, INK, "middle", "bold")
        s += text(x + 100, cy + 19, t2, 10, col, "middle")
        if k < 2:
            s += arrow(x + 200, cy + 8, x + 224, cy + 8, INK, 1.8)
        x += 224
    s += text(W / 2, 338, "Контролер сам зміряв ємність, знайшов центри й видав готові (X,Y); кожна точка має свій ID — це й є мультитач.",
              11, GREY, "middle", style="italic")
    save("fig-13-1-6c-1-touch-ctrl.svg", s)


# ── Рис. 13.1.7c.1 — послідовність оновлення e-ink по SPI ────────────────────
def fig_eink_module_seq():
    W, H = 820, 330
    s = header(W, H)
    s += text(W / 2, 32, "E-ink модуль по SPI: послідовність оновлення з BUSY і LUT", 17, INK, "middle", "bold")
    steps = [("скидання", "RST"), ("ініт + LUT", "хвилеформа"), ("образ", "→ RAM"),
             ("команда", "«оновити»"), ("чекати", "BUSY"), ("глибокий", "сон")]
    bw = 118
    gap = (820 - 40 - 6 * bw) / 5.0
    x = 20
    y = 84
    for k, (t1, t2) in enumerate(steps):
        s += rect(x, y, bw, 54, "#eef2f5", INK, 1.6, 5)
        s += text(x + bw / 2, y + 23, t1, 11, INK, "middle", "bold")
        s += text(x + bw / 2, y + 41, t2, 10, GREY, "middle")
        if k < 5:
            s += arrow(x + bw, y + 27, x + bw + gap, y + 27, INK, 1.8)
        x += bw + gap
    by, hi = 218, 174
    s += text(34, by + 4, "BUSY", 10, INK, "end", "bold")
    s += line(40, by, 547, by, INK, 2)
    s += line(547, by, 547, hi, INK, 2)
    s += line(547, hi, 683, hi, INK, 2)
    s += line(683, hi, 683, by, INK, 2)
    s += line(683, by, 790, by, INK, 2)
    s += text(615, hi - 10, "панель зайнята (секунди)", 10, RED, "middle", "bold")
    s += text(290, by - 8, "вільно: можна слати команди", 9.5, GREY, "middle")
    s += text(W / 2, 270, "LUT — це хвилеформа з §13.1.7: повне оновлення бере вбудовану, часткове часто потребує своєї.",
              11, GREY, "middle", style="italic")
    s += text(W / 2, 292, "Після оновлення панель присипляють (deep sleep), щоб не лишати її під напругою — інакше псується.",
              11, GREY, "middle", style="italic")
    save("fig-13-1-7c-1-eink-seq.svg", s)


if __name__ == "__main__":
    # Історія до розділу
    fig_timeline()
    fig_dsm()
    fig_tn()
    # Тема 13.1.1 — класи дисплеїв
    fig_classes_map()
    fig_lcd_stack()
    fig_active_matrix()
    fig_oled_stack()
    fig_eink_capsule()
    fig_compare()
    fig_power_profile()
    # Тема 13.1.2 — параметри панелі
    fig_ppi()
    fig_nits()
    fig_contrast()
    fig_angles_mech()
    fig_angle_curve()
    fig_pwm()
    # Тема 13.1.3 — інтерфейси панелей
    fig_bw_demand()
    fig_spi_wiring()
    fig_8080_bus()
    fig_rgb_scan()
    fig_dsi_lanes()
    fig_iface_compare()
    # Тема 13.1.4 — контролер дисплея
    fig_two_jobs()
    fig_smart_panel()
    fig_gram_window()
    fig_host_fb()
    fig_ctrl_placement()
    fig_arch_compare()
    # Тема 13.1.5 — підсвітка
    fig_backlight_structure()
    fig_led_iv()
    fig_resistor_ballast()
    fig_boost_driver()
    fig_dimming()
    fig_led_strings()
    # Тема 13.1.6 — дотик
    fig_touch_overview()
    fig_resistive()
    fig_pcap_mutual()
    fig_self_vs_mutual()
    fig_touch_controller()
    fig_touch_compare()
    # Тема 13.1.7 — e-ink особливо
    fig_eink_speed()
    fig_eink_waveform()
    fig_eink_full_refresh()
    fig_eink_partial_ghost()
    fig_eink_temperature()
    fig_eink_driving()
    # Історія до теми 13.1.7 — електронне чорнило
    fig_eink_hist_mechanisms()
    fig_eink_hist_timeline()
    # Тема 13.1.8 — вибір дисплея
    fig_choose_funnel()
    fig_environment_class()
    fig_energy_decision()
    fig_true_cost()
    fig_display_footprint()
    fig_decision_scorecard()
    # Вставка 🔌 13.1.1c — SSD1306
    fig_ssd1306_pages()
    # Вставка 🧮 13.1.3m — бюджет пропускної здатності
    fig_bw_budget_check()
    # Вставка 🔌 13.1.4c — SPI-TFT ST7789/ILI9341
    fig_spi_tft_dma()
    # Вставка 🔌 13.1.5c — boost-драйвер підсвітки
    fig_backlight_driver_ic()
    # Вставка 🔌 13.1.6c — контролер дотику
    fig_touch_ctrl_i2c()
    # Вставка 🔌 13.1.7c — e-ink модулі по SPI
    fig_eink_module_seq()
    print("done.")
