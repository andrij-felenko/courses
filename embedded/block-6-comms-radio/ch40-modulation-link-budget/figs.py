# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 40 — «Радіо: модуляція й бюджет лінії» (Модуль 6).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; несуча синя, корисний сигнал/звук зелений,
шум/проблема червоні; стрілки через marker; шрифт sans-serif.
Підписи посекційно (Рис. C.S.N); історія — секція 0 (Рис. 40.0.N).
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"   # шум / проблема
BLUE  = "#1f47b5"   # несуча
GREEN = "#1f8a3b"   # корисний сигнал / висновок
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#b08900"
SPARK = "#e8b53a"
METAL = "#9a9aa0"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LAMB  = "#fbf3df"
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
        f'  <marker id="aAmb" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey", AMBER: "aAmb"}


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


def _poly(pts, color, w):
    return ('<path d="M ' + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
            + f'" fill="none" stroke="{color}" stroke-width="{w}"/>\n')


def sine(x0, y0, length, amp, periods, color, w=2.4, phase=0.0):
    pts = []
    n = max(60, int(length / 2))
    for i in range(n + 1):
        t = i / n
        x = x0 + t * length
        y = y0 - amp * math.sin(2 * math.pi * periods * t + phase)
        pts.append((x, y))
    return _poly(pts, color, w)


def amwave(x0, y0, length, amp, fc, fm, depth, color, w=2.2):
    """Амплітудно-модульована несуча: огинаюча 1+depth·sin(2π fm t)."""
    pts = []
    n = max(160, int(length / 1.5))
    for i in range(n + 1):
        t = i / n
        env = 1.0 + depth * math.sin(2 * math.pi * fm * t)
        y = y0 - amp * env * math.sin(2 * math.pi * fc * t)
        pts.append((x0 + t * length, y))
    return _poly(pts, color, w)


def fmwave(x0, y0, length, amp, fc, fdev, fm, color, w=2.2):
    """Частотно-модульована несуча: миттєва фаза = 2π fc t + (fdev/fm)·sin(2π fm t)."""
    pts = []
    n = max(200, int(length / 1.2))
    for i in range(n + 1):
        t = i / n
        ph = 2 * math.pi * fc * t + (fdev / fm) * math.sin(2 * math.pi * fm * t)
        pts.append((x0 + t * length, y0 - amp * math.sin(ph)))
    return _poly(pts, color, w)


def noisy(x0, y0, length, amp, color, w=1.5):
    """Детермінований «шум» — сума несумірних синусів (без random, відтворювано)."""
    pts = []
    n = max(120, int(length / 3))
    for i in range(n + 1):
        t = i / n
        v = (math.sin(t * 53.1) + 0.7 * math.sin(t * 97.7 + 1.3)
             + 0.5 * math.sin(t * 191.3 + 0.7) + 0.35 * math.sin(t * 331.0 + 2.1))
        pts.append((x0 + t * length, y0 - amp * 0.32 * v))
    return _poly(pts, color, w)


def spark(cx, cy, r=12, col=RED, w=1.8):
    pts = []
    for k in range(8):
        ang = k * math.pi / 4
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    path = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"
    return f'<path d="{path}" fill="none" stroke="{col}" stroke-width="{w}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ============================================================================
#  Історія (секція 0) — Едвін Армстронг і FM
# ============================================================================

# ── Рис. 40.0.1 — таймлайн життя ─────────────────────────────────────────────
def fig_timeline():
    W, H = 920, 640
    s = header(W, H)
    s += text(W / 2, 38, "Едвін Армстронг: геній, що подарував світу чисте радіо", 20.5, INK, "middle", "bold")
    s += text(W / 2, 60, "три фундаментальні винаходи — і десятиліття патентних воєн, що його зламали",
              12.5, GREY, "middle", style="italic")
    spine = 250
    top, bot = 92, H - 26
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("1890", "Народився в Нью-Йорку", "З дитинства одержимий радіо й горищними антенами", "born"),
        ("1912", "Регенеративна схема", "Студент Columbia робить лампу гучною — і генератором хвиль", "win"),
        ("1918", "Супергетеродин", "На війні у Франції — архітектура кожного приймача й досі", "win"),
        ("1933", "Широкосмугова FM", "Чотири патенти на радикально нову, безшумну модуляцію", "fm"),
        ("1935", "Демонстрація FM", "Наживо: радіо без статики — слухачі не вірять вухам", "fm"),
        ("1945", "FCC переносить FM", "Тиск RCA: смугу зсунуто — пів мільйона приймачів мертві за ніч", "bad"),
        ("1954", "Трагічний кінець", "Розорений судами, зломлений — стрибає з 13-го поверху", "bad"),
        ("1954–67", "Посмертне виправдання", "Вдова Меріон виграє ВСІ 21 позов: RCA, Motorola, Zenith", "win"),
    ]
    n = len(nodes)
    for i, (yr, who, q, kind) in enumerate(nodes):
        y = top + 26 + (bot - top - 52) * i / (n - 1)
        if kind == "fm":
            s += circle(spine, y, 10, "#fff", GREEN, 3)
            s += circle(spine, y, 4.5, GREEN, GREEN, 0)
            wcol = GREEN
        elif kind == "bad":
            s += rect(spine - 8, y - 8, 16, 16, "#fff", RED, 2.6, 3)
            wcol = RED
        elif kind == "win":
            s += circle(spine, y, 7.5, "#fff", BLUE, 2.8)
            wcol = BLUE
        else:
            s += circle(spine, y, 7, "#fff", GREY, 2.6)
            wcol = INK
        s += text(spine - 22, y + 5, yr, 12.5, GREY, "end", "bold")
        s += text(spine + 26, y - 3, who, 15.5, wcol, "start", "bold")
        s += text(spine + 26, y + 17, q, 11.5, INK, "start", style="italic")
    save("fig-40-0-1-timeline.svg", s)


# ── Рис. 40.0.2 — три дарунки до FM ──────────────────────────────────────────
def fig_three_gifts():
    W, H = 920, 360
    s = header(W, H)
    s += text(W / 2, 36, "Три винаходи однієї людини, на яких стоїть усе радіо", 19.5, INK, "middle", "bold")
    s += text(W / 2, 58, "Армстронг подарував світу підсилення, архітектуру приймача й чистий звук",
              12.5, GREY, "middle", style="italic")
    cards = [
        ("1912", "Регенерація", "Позитивний зворотний зв'язок: лампа підсилює в тисячі разів — і сама стає генератором хвиль.",
         "вперше радіо стало гучним і дешевим", BLUE),
        ("1918", "Супергетеродин", "Зсув будь-якої частоти на одну зручну проміжну (ПЧ), де її легко підсилити й відфільтрувати.",
         "архітектура майже КОЖНОГО приймача досі", BLUE),
        ("1933", "Широкосмугова FM", "Інформація — у частоті, не в амплітуді. Чистий, безшумний звук, про який мріяли.",
         "її трагічна доля — серце цієї історії", GREEN),
    ]
    x = 40
    for yr, name, body, foot, col in cards:
        s += rect(x, 86, 270, 230, "#fbfbfb", col, 2, 12)
        s += text(x + 135, 118, yr, 13, GREY, "middle", "bold")
        s += text(x + 135, 144, name, 16.5, col, "middle", "bold")
        # перенос тіла по словах
        words = body.split()
        ln, yy = "", 176
        for wd in words:
            if len(ln) + len(wd) > 30:
                s += text(x + 135, yy, ln.strip(), 10.8, INK, "middle")
                ln, yy = "", yy + 18
            ln += wd + " "
        s += text(x + 135, yy, ln.strip(), 10.8, INK, "middle")
        s += line(x + 24, 286, x + 246, 286, FAINT, 1.2)
        s += text(x + 135, 304, foot, 9.8, (GREEN if col == GREEN else GREY), "middle", "bold")
        x += 290
    save("fig-40-0-2-three-gifts.svg", s)


# ── Рис. 40.0.3 — чому AM ловить статику ─────────────────────────────────────
def fig_am_noise():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 34, "Чому AM-радіо тріщить: шум сідає просто на амплітуду", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "блискавка, мотор, іскра додають сплески амплітуди — а саме в ній AM несе звук",
              12, GREY, "middle", style="italic")
    # AM-хвиля з огинаючою
    y1 = 150
    s += text(70, y1 - 64, "Передано (AM):", 12, INK, "start", "bold")
    s += amwave(70, y1, 480, 34, 26, 2, 0.55, BLUE, 2)
    # огинаюча
    env_up = []
    env_dn = []
    for i in range(81):
        t = i / 80
        e = 1 + 0.55 * math.sin(2 * math.pi * 2 * t)
        env_up.append((70 + t * 480, y1 - 34 * e))
        env_dn.append((70 + t * 480, y1 + 34 * e))
    s += _poly(env_up, GREEN, 1.6)
    s += _poly(env_dn, GREEN, 1.6)
    s += text(560, y1 - 28, "← огинаюча = звук", 11, GREEN, "start", "bold")
    # блискавка-шум
    s += spark(610, y1, 16, RED, 2.2)
    # прийнято з шумом
    y2 = 300
    s += text(70, y2 - 60, "Прийнято: шум спотворює гучність → тріск", 12, RED, "start", "bold")
    s += amwave(70, y2, 480, 34, 26, 2, 0.55, BLUE, 1.6)
    s += noisy(70, y2, 480, 30, RED, 1.5)
    s += text(560, y2 - 6, "шум невіддільний", 11, RED, "start", "bold")
    s += text(560, y2 + 12, "від корисної амплітуди", 10, GREY, "start")
    save("fig-40-0-3-am-noise.svg", s)


# ── Рис. 40.0.4 — контрінтуїтивна ідея: широка смуга ─────────────────────────
def fig_wideband():
    W, H = 920, 410
    s = header(W, H)
    s += text(W / 2, 34, "Парадокс Армстронга: ширша смуга → ТИХІШЕ", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "Карсон (1922) «довів», що FM марна; Армстронг зрозумів — треба не вузьку, а ШИРОКУ FM",
              12, GREY, "middle", style="italic")
    # ліворуч — вузька FM (мало девіації) + шум
    s += text(245, 92, "вузька FM", 13, AMBER, "middle", "bold")
    s += text(245, 110, "(мала девіація — як вважали)", 9.5, GREY, "middle")
    s += fmwave(70, 165, 350, 26, 20, 6, 2.5, AMBER, 2)
    s += noisy(70, 165, 350, 18, RED, 1.3)
    s += text(245, 214, "шум ще чутно", 10.5, RED, "middle", "bold")
    # праворуч — широка FM + амплітуду можна зрізати
    s += text(680, 92, "широка FM", 13, GREEN, "middle", "bold")
    s += text(680, 110, "(велика девіація — здогад Армстронга)", 9.5, GREY, "middle")
    s += fmwave(500, 165, 350, 26, 20, 22, 2.5, GREEN, 2)
    s += text(680, 214, "шум амплітуди просто зрізають → тиша", 10, GREEN, "middle", "bold")
    s += arrow(430, 165, 495, 165, INK, 2)
    s += text(462, 152, "ширше", 9.5, INK, "middle", "bold")

    s += rect(60, 250, W - 120, 132, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 276, "Ключ: інформація у FM — у ЧАСТОТІ. Тож приймач сміливо зрізає всі коливання амплітуди,",
              12, INK, "middle", "bold")
    s += text(W / 2, 297, "а з ними — майже весь шум. Що ширша смуга (девіація), то глибше тоне шум.",
              12, INK, "middle", "bold")
    s += text(W / 2, 322, "Армстронг СВІДОМО «розтринькав» смугу — і виграв тишу. Це обмін: смуга ⇄ завадостійкість.",
              11.5, GREEN, "middle", "bold")
    s += text(W / 2, 346, "Той самий обмін «смуга проти шуму» 1948-го формалізує Клод Шеннон —",
              11, GREY, "middle", style="italic")
    s += text(W / 2, 364, "ми торкнемося його межі у §40.4. Армстронг намацав цю істину руками, за 15 років до теорії.",
              11, GREY, "middle", style="italic")
    save("fig-40-0-4-wideband.svg", s)


# ── Рис. 40.0.5 — перенесення FM-діапазону 1945 ──────────────────────────────
def fig_band_move():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 34, "Удар 1945-го: FCC переносить FM-діапазон — і вбиває його", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "під тиском RCA смугу зсунули; усі наявні FM-приймачі та передавачі Армстронга — мертві за ніч",
              11.5, GREY, "middle", style="italic")
    # вісь частот
    ax_y = 210
    s += line(70, ax_y, 850, ax_y, INK, 2)
    for mhz, px in [(40, 110), (50, 250), (88, 560), (108, 800)]:
        s += line(px, ax_y - 5, px, ax_y + 5, INK, 1.6)
        s += text(px, ax_y + 22, f"{mhz} МГц", 11, INK, "middle", "bold")
    # старий діапазон
    s += rect(110, ax_y - 46, 140, 36, LGRN, GREEN, 2, 5)
    s += text(180, ax_y - 23, "стара FM", 11.5, GREEN, "middle", "bold")
    s += text(180, ax_y - 60, "42–50 МГц", 11, GREEN, "middle", "bold")
    s += text(180, ax_y - 76, "тут було радіо Армстронга", 9.5, GREY, "middle")
    # нова FM
    s += rect(560, ax_y - 46, 240, 36, LBLUE, BLUE, 2, 5)
    s += text(680, ax_y - 23, "нова FM (досі!)", 11.5, BLUE, "middle", "bold")
    s += text(680, ax_y - 60, "88–108 МГц", 11, BLUE, "middle", "bold")
    # стрілка перенесення
    s += arrow(255, ax_y - 28, 555, ax_y - 28, RED, 2.4)
    s += text(405, ax_y - 38, "примусовий зсув", 11, RED, "middle", "bold")
    # на старе місце — ТБ
    s += text(180, ax_y + 52, "на колишню смугу зайшло ТБ", 10, AMBER, "middle", "bold")
    s += arrow(180, ax_y + 38, 180, ax_y + 8, AMBER, 1.8)

    s += rect(60, ax_y + 70, W - 120, 70, LRED, RED, 1.4, 10)
    s += text(W / 2, ax_y + 94, "Наслідок: ~півмільйона FM-приймачів і станції Армстронга стали непотребом за одну ніч.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, ax_y + 116, "Це й досі причина, чому ваша FM-шкала — саме 88–108 МГц. Технічне рішення, ухвалене у війні корпорацій.",
              10.5, GREY, "middle", style="italic")
    save("fig-40-0-5-band-move.svg", s)


# ── Рис. 40.0.6 — колективна й спірна правда ─────────────────────────────────
def fig_collective():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 34, "Чесно про авторство: що безперечне, а що — спірне", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "винаходи рідко мають одного героя; розділімо доведене, спірне й чуже",
              12, GREY, "middle", style="italic")
    rows = [
        ("Широкосмугова FM", "Армстронг — безперечно", GREEN,
         "Концепція FM існувала; Карсон (1922) описав смугу, але вважав FM марною.",
         "Саме Армстронг зробив її РОБОЧОЮ і довів цінність широкої смуги."),
        ("Регенерація (1912)", "спірно — суд проти інженерів", AMBER,
         "Верховний суд США (1934) присудив пріоритет Лі де Форесту.",
         "Більшість інженерів і досі вважають це помилкою суду; незалежно — Майснер у Німеччині."),
        ("Супергетеродин", "Армстронг, але не на самоті", BLUE,
         "Ідею перетворення частоти розробляли паралельно (зокрема Леві у Франції).",
         "Армстронг дав практичну, працездатну архітектуру приймача."),
    ]
    y = 86
    for title, verdict, col, l1, l2 in rows:
        s += rect(50, y, W - 100, 92, "#fbfbfb", col, 1.8, 10)
        s += text(70, y + 30, title, 14.5, INK, "start", "bold")
        s += rect(70, y + 44, 250, 26, ("#eef6ef" if col == GREEN else ("#fbf3df" if col == AMBER else "#e9eefb")), col, 1.4, 5)
        s += text(195, y + 62, verdict, 11.5, col, "middle", "bold")
        s += text(345, y + 38, l1, 11, INK, "start")
        s += text(345, y + 60, l2, 10.5, GREY, "start", style="italic")
        y += 102
    save("fig-40-0-6-collective.svg", s)


# ── Рис. 40.0.7 — трагедія і виправдання ─────────────────────────────────────
def fig_vindication():
    W, H = 920, 360
    s = header(W, H)
    s += text(W / 2, 34, "Трагедія людини — і перемога правди (запізно)", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "патентні війни виснажили його статок і сили; справедливість прийшла після смерті",
              12, GREY, "middle", style="italic")
    # ліва панель — трагедія
    s += rect(50, 84, 390, 230, LRED, RED, 1.8, 12)
    s += text(245, 114, "1954 — кінець", 15, RED, "middle", "bold")
    for i, ln in enumerate([
        "Десятиліття судів проти RCA висотали",
        "майже весь статок і здоров'я.",
        "Розрив із дружиною. Самотній і хворий,",
        "у ніч проти 1 лютого 1954-го Армстронг",
        "стрибає з вікна 13-го поверху в Мангеттені.",
    ]):
        s += text(245, 146 + i * 26, ln, 11, INK, "middle")
    s += text(245, 300, "він так і не побачив свого виправдання", 10, GREY, "middle", style="italic")
    # стрілка
    s += arrow(445, 200, 475, 200, INK, 2.2)
    # права панель — виправдання
    s += rect(480, 84, 390, 230, LGRN, GREEN, 1.8, 12)
    s += text(675, 114, "1954–1967 — Меріон", 15, GREEN, "middle", "bold")
    for i, ln in enumerate([
        "Вдова Меріон підхопила всі позови",
        "й довела їх до кінця сама.",
        "21 судова справа — і ВСІ виграні:",
        "RCA, Motorola, Zenith та інші.",
        ">$10 млн відшкодувань; пріоритет FM —",
        "за Армстронгом. Правда перемогла.",
    ]):
        s += text(675, 142 + i * 25, ln, 11, INK, "middle")
    s += text(W / 2, 342, "Мораль: технологію творить фізика, але її долю вирішують патенти, гроші й воля людей.",
              11.5, INK, "middle", "bold")
    save("fig-40-0-7-vindication.svg", s)


# ============================================================================
#  §40.1 — Навіщо модуляція: посадити інформацію на несучу
# ============================================================================

# ── Рис. 40.1.1 — чому не можна випромінювати звук напряму ───────────────────
def fig11_antenna():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 34, "Чому звук не можна випромінювати напряму: антена", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "ефективна антена має бути порядку λ/4; для низьких частот це кілометри",
              12, GREY, "middle", style="italic")
    # ліва панель — звук 3 кГц
    s += rect(40, 80, 410, 300, LRED, RED, 1.8, 12)
    s += text(245, 108, "Звук напряму: 3 кГц", 14.5, RED, "middle", "bold")
    s += text(245, 132, "λ = c / f = 3×10⁸ / 3×10³ = 100 км", 12, INK, "middle", "bold")
    s += text(245, 152, "λ/4 ≈ 25 км антени", 12.5, RED, "middle", "bold")
    # величезна щогла
    s += line(245, 360, 245, 200, METAL, 4)
    s += text(245, 192, "▲", 14, METAL, "middle", "bold")
    # людинка для масштабу
    s += circle(330, 350, 5, INK, INK, 0)
    s += line(330, 355, 330, 368, INK, 2)
    s += text(355, 366, "людина", 9.5, GREY, "start")
    s += text(245, 374, "25 км — вища за будь-яку вежу. Нереально.", 10.5, RED, "middle", "bold")
    # права панель — несуча 100 МГц
    s += rect(470, 80, 410, 300, LGRN, GREEN, 1.8, 12)
    s += text(675, 108, "На несучій: 100 МГц", 14.5, GREEN, "middle", "bold")
    s += text(675, 132, "λ = 3×10⁸ / 10⁸ = 3 м", 12, INK, "middle", "bold")
    s += text(675, 152, "λ/4 = 0.75 м — паличка", 12.5, GREEN, "middle", "bold")
    s += line(675, 360, 675, 300, METAL, 3)
    s += text(675, 292, "▲", 12, METAL, "middle", "bold")
    s += circle(720, 350, 5, INK, INK, 0)
    s += line(720, 355, 720, 368, INK, 2)
    s += text(745, 366, "людина", 9.5, GREY, "start")
    s += text(675, 386, "75 см — звичайна антена. Реально!", 10.5, GREEN, "middle", "bold")
    save("fig-40-1-1-antenna.svg", s)


# ── Рис. 40.1.2 — спільний ефір: чому без несучих хаос ───────────────────────
def fig12_sharing():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 34, "Другий привід: як багатьом станціям ужитися в ефірі", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "усі сигнали голосу лежать в одній низькій смузі; рознести їх можна лише різними несучими",
              11.5, GREY, "middle", style="italic")
    # ліворуч — усі баребенд, накладаються
    s += text(245, 92, "Без несучих: усі в одній смузі", 12.5, RED, "middle", "bold")
    ax1 = 250
    s += line(60, ax1, 440, ax1, INK, 2)
    s += text(250, ax1 + 22, "частота →", 10, GREY, "middle")
    for col, dx in [(RED, 0), (AMBER, 8), (BLUE, -8), (GREEN, 4)]:
        env = []
        for i in range(41):
            t = i / 40
            env.append((110 + t * 120 + dx, ax1 - 70 * math.exp(-((t - 0.5) * 4) ** 2)))
        s += _poly(env, col, 1.8)
    s += text(170, ax1 - 78, "усі накладені", 10, RED, "middle", "bold")
    s += text(250, ax1 + 44, "не розрізнити — суцільна каша", 10.5, RED, "middle")
    # праворуч — кожна на своїй несучій
    s += text(680, 92, "На різних несучих: кожна окремо", 12.5, GREEN, "middle", "bold")
    ax2 = 250
    s += line(480, ax2, 870, ax2, INK, 2)
    s += text(680, ax2 + 22, "частота →", 10, GREY, "middle")
    for col, cx, lab in [(BLUE, 540, "f₁"), (GREEN, 620, "f₂"), (AMBER, 700, "f₃"), (RED, 790, "f₄")]:
        env = []
        for i in range(31):
            t = i / 30
            env.append((cx - 30 + t * 60, ax2 - 64 * math.exp(-((t - 0.5) * 4.5) ** 2)))
        s += _poly(env, col, 2)
        s += text(cx, ax2 + 40, lab, 11, col, "middle", "bold")
    s += text(680, ax2 - 76, "кожна — у своєму «вікні»", 10, GREEN, "middle", "bold")

    s += rect(60, 300, W - 120, 76, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 326, "Модуляція переносить кожне повідомлення на власну несучу частоту —",
              12, INK, "middle", "bold")
    s += text(W / 2, 347, "і тепер десятки станцій спокійно ділять ефір, не глушачи одна одну (частотний поділ).",
              12, INK, "middle", "bold")
    s += text(W / 2, 368, "Саме тому в тебе є «налаштування на станцію»: ти обираєш, яку несучу слухати.",
              10.5, GREY, "middle", style="italic")
    save("fig-40-1-2-sharing.svg", s)


# ── Рис. 40.1.3 — несуча сама собою нічого не несе ───────────────────────────
def fig13_carrier():
    W, H = 920, 330
    s = header(W, H)
    s += text(W / 2, 34, "Несуча: чиста хвиля, що сама собою НІЧОГО не повідомляє", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "ідеальна синусоїда абсолютно передбачувана — а отже, не містить жодної інформації",
              11.5, GREY, "middle", style="italic")
    s += sine(70, 170, 780, 56, 14, BLUE, 2.6)
    s += line(70, 170, 850, 170, FAINT, 1, "4 4")
    s += text(80, 122, "несуча (carrier): стала амплітуда, стала частота", 12, BLUE, "start", "bold")
    s += text(460, 250, "знаючи перший період, ти знаєш усе наперед → 0 інформації", 11.5, GREY, "middle", style="italic")
    s += rect(60, 278, W - 120, 40, LBLUE, BLUE, 1.3, 9)
    s += text(W / 2, 303, "Щоб щось передати, несучу треба ЗМІНИТИ в такт із повідомленням. Це і є модуляція.",
              12, INK, "middle", "bold")
    save("fig-40-1-3-carrier.svg", s)


# ── Рис. 40.1.4 — три ручки синусоїди ────────────────────────────────────────
def fig14_three_knobs():
    W, H = 920, 430
    s = header(W, H)
    s += text(W / 2, 34, "Три ручки несучої: що саме можна змінювати", 19.5, INK, "middle", "bold")
    s += text(W / 2, 58, "y(t) = A · sin(2π f t + φ)  — рівно три параметри, отже три родини модуляції",
              13, INK, "middle", "bold")
    cols = [
        ("A", "амплітуда", "AM", "висота хвилі", RED, 0),
        ("f", "частота", "FM", "частота хвилі", GREEN, 1),
        ("φ", "фаза", "PM", "зсув хвилі", AMBER, 2),
    ]
    for sym, name, mod, desc, col, i in cols:
        x = 50 + i * 290
        s += rect(x, 92, 270, 300, "#fbfbfb", col, 2, 12)
        s += text(x + 135, 120, sym, 22, col, "middle", "bold")
        s += text(x + 135, 142, name, 13, INK, "middle", "bold")
        # міні-хвиля
        if i == 0:
            s += amwave(x + 25, 215, 220, 26, 16, 2, 0.6, col, 2)
        elif i == 1:
            s += fmwave(x + 25, 215, 220, 26, 12, 16, 2.5, col, 2)
        else:
            # фазова: різкий розворот фази посередині (як BPSK)
            s += sine(x + 25, 215, 110, 26, 7, col, 2)
            s += sine(x + 135, 215, 110, 26, 7, col, 2, phase=math.pi)
            s += line(x + 135, 188, x + 135, 242, GREY, 1.2, "3 3")
        s += text(x + 135, 280, "міняємо " + desc, 11, INK, "middle")
        s += rect(x + 75, 300, 120, 34, ("#fdeeee" if col == RED else ("#eef6ef" if col == GREEN else "#fbf3df")), col, 1.6, 6)
        s += text(x + 135, 323, mod, 16, col, "middle", "bold")
        s += text(x + 135, 360, ("амплітудна модуляція" if i == 0 else ("частотна модуляція" if i == 1 else "фазова модуляція")),
                  10, GREY, "middle", style="italic")
    save("fig-40-1-4-three-knobs.svg", s)


# ── Рис. 40.1.5 — ланцюг: модулятор → ефір → демодулятор ─────────────────────
def fig15_chain():
    W, H = 920, 340
    s = header(W, H)
    s += text(W / 2, 34, "Повний шлях: посадити інформацію, передати, зняти", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "модулятор «садить» повідомлення на несучу; демодулятор знімає його назад",
              12, GREY, "middle", style="italic")
    y = 170
    # повідомлення
    s += text(70, y - 50, "повідомлення", 11, GREEN, "middle", "bold")
    s += sine(30, y, 80, 16, 1.2, GREEN, 2)
    s += arrow(115, y, 150, y, INK, 2)
    # модулятор
    s += rect(150, y - 34, 110, 68, LBLUE, BLUE, 2, 8)
    s += text(205, y - 4, "МОДУ-", 12.5, BLUE, "middle", "bold")
    s += text(205, y + 14, "ЛЯТОР", 12.5, BLUE, "middle", "bold")
    s += text(205, y - 46, "+ несуча", 10, GREY, "middle")
    s += arrow(260, y, 300, y, INK, 2)
    # передавач-антена
    s += line(330, y + 30, 330, y - 10, METAL, 3)
    s += line(322, y - 18, 338, y - 18, METAL, 3)
    s += amwave(350, y, 150, 18, 18, 2, 0.6, BLUE, 1.8)
    # ефір
    s += text(560, y - 50, "))) ефір )))", 12, GREY, "middle", "bold")
    s += amwave(500, y, 150, 18, 18, 2, 0.6, BLUE, 1.8)
    # приймач-антена
    s += line(660, y + 30, 660, y - 10, METAL, 3)
    s += line(652, y - 18, 668, y - 18, METAL, 3)
    s += arrow(680, y, 720, y, INK, 2)
    # демодулятор
    s += rect(720, y - 34, 110, 68, LGRN, GREEN, 2, 8)
    s += text(775, y - 4, "ДЕМОДУ-", 11.5, GREEN, "middle", "bold")
    s += text(775, y + 14, "ЛЯТОР", 11.5, GREEN, "middle", "bold")
    s += arrow(830, y, 868, y, INK, 2)
    s += text(848, y - 46, "повідомлення", 10, GREEN, "start", "bold")

    s += rect(60, 280, W - 120, 44, LGREY, GREY, 1.2, 9)
    s += text(W / 2, 300, "База (низька частота) → переносимо на несучу (passband) → знімаємо назад у базу.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 317, "Несуча — лише «вантажівка»: довозить повідомлення туди, куди база сама не дістанеться.",
              10.5, GREY, "middle", style="italic")
    save("fig-40-1-5-chain.svg", s)


# ── Рис. 40.1.6 — спектр: база → passband → база ─────────────────────────────
def fig16_spectrum():
    W, H = 920, 360
    s = header(W, H)
    s += text(W / 2, 34, "Що робить модуляція зі спектром: піднімає базу до несучої", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "повідомлення живе біля 0 Гц (база); модуляція переносить його вгору, до несучої fₒ",
              11.5, GREY, "middle", style="italic")
    ax = 250
    s += line(70, ax, 850, ax, INK, 2)
    s += text(850, ax + 20, "частота", 10, GREY, "end")
    s += text(80, ax + 20, "0", 10, GREY, "middle")
    # база біля 0
    env = []
    for i in range(31):
        t = i / 30
        env.append((90 + t * 90, ax - 60 * math.exp(-((t - 0.1) * 3.5) ** 2)))
    s += _poly(env, GREEN, 2.2)
    s += text(120, ax - 70, "база", 11, GREEN, "middle", "bold")
    s += text(120, ax + 36, "повідомлення", 9.5, GREEN, "middle")
    # стрілка переносу
    s += arrow(200, ax - 40, 560, ax - 40, RED, 2.4)
    s += text(380, ax - 52, "модуляція переносить угору", 11, RED, "middle", "bold")
    # passband біля fc
    cx = 640
    s += line(cx, ax + 6, cx, ax - 6, INK, 2)
    s += text(cx, ax + 20, "fₒ (несуча)", 10, BLUE, "middle", "bold")
    for sgn in (-1, 1):
        env = []
        for i in range(31):
            t = i / 30
            env.append((cx + sgn * (20 + t * 70), ax - 58 * math.exp(-((t) * 3.0) ** 2)))
        s += _poly(env, BLUE, 2.2)
    s += text(cx, ax - 68, "passband", 11, BLUE, "middle", "bold")
    s += text(cx, ax + 40, "сигнал «обернувся» навколо несучої", 9.5, GREY, "middle")

    s += rect(60, ax + 56, W - 120, 56, LBLUE, BLUE, 1.3, 9)
    s += text(W / 2, ax + 80, "Демодуляція в приймачі робить зворотне — зсуває спектр назад до 0 і дістає повідомлення.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, ax + 100, "Ширина «горба» навколо несучої — це смуга сигналу; вона зростає зі швидкістю даних (про це §40.4).",
              10, GREY, "middle", style="italic")
    save("fig-40-1-6-spectrum.svg", s)


# ── Рис. 40.1.7 — три причини модулювати ─────────────────────────────────────
def fig17_why():
    W, H = 920, 320
    s = header(W, H)
    s += text(W / 2, 34, "Навіщо модуляція: три причини в одному погляді", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "усе зводиться до того, що низькочастотне повідомлення саме по собі радіо не зробить",
              11.5, GREY, "middle", style="italic")
    cards = [
        ("📡", "Реальна антена", "Висока несуча → коротка λ → антена в сантиметри-метри, а не кілометри.", BLUE),
        ("🔢", "Спільний ефір", "Кожній станції — своя несуча; десятки сигналів уживаються, не глушачи одне одного.", GREEN),
        ("🎯", "Під середовище", "Несучу обирають під діапазон: дальність, проникність, вільні смуги (§39.4).", AMBER),
    ]
    x = 45
    for ico, title, body, col in cards:
        s += rect(x, 88, 277, 200, "#fbfbfb", col, 2, 12)
        s += text(x + 138, 128, ico, 24, INK, "middle")
        s += text(x + 138, 158, title, 14.5, col, "middle", "bold")
        words = body.split()
        ln, yy = "", 188
        for wd in words:
            if len(ln) + len(wd) > 32:
                s += text(x + 138, yy, ln.strip(), 10.8, INK, "middle")
                ln, yy = "", yy + 19
            ln += wd + " "
        s += text(x + 138, yy, ln.strip(), 10.8, INK, "middle")
        x += 290
    save("fig-40-1-7-why.svg", s)


# ============================================================================
#  §40.2 — Амплітудна й частотна модуляція (AM/FM)
# ============================================================================

def _stem(x, y_base, h, color, w=3):
    return line(x, y_base, x, y_base - h, color, w)


# ── Рис. 40.2.1 — будова AM ──────────────────────────────────────────────────
def fig21_am_build():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 32, "Амплітудна модуляція (AM): повідомлення стає огинаючою", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "s(t) = A · [1 + μ·m(t)] · sin(2π fₒ t) — гучність несучої повторює форму звуку",
              12, GREY, "middle", style="italic")
    # рядок 1 — повідомлення
    s += text(40, 92, "повідомлення m(t):", 11.5, GREEN, "start", "bold")
    s += sine(60, 130, 780, 26, 2, GREEN, 2.4)
    # рядок 2 — несуча
    s += text(40, 196, "несуча:", 11.5, BLUE, "start", "bold")
    s += sine(60, 232, 780, 26, 26, BLUE, 2)
    # рядок 3 — AM
    s += text(40, 300, "AM-сигнал = несуча з огинаючою:", 11.5, INK, "start", "bold")
    yc = 360
    s += amwave(60, yc, 780, 50, 26, 2, 0.7, BLUE, 2)
    # огинаюча
    up, dn = [], []
    for i in range(121):
        t = i / 120
        e = 1 + 0.7 * math.sin(2 * math.pi * 2 * t)
        up.append((60 + t * 780, yc - 50 * e))
        dn.append((60 + t * 780, yc + 50 * e))
    s += _poly(up, GREEN, 1.8)
    s += _poly(dn, GREEN, 1.8)
    s += text(850, yc - 86, "огинаюча", 11, GREEN, "end", "bold")
    s += text(850, yc - 72, "= m(t)", 10, GREEN, "end")
    s += rect(60, 426, W - 120, 34, LGRN, GREEN, 1.3, 8)
    s += text(W / 2, 448, "Приймач AM до смішного простий: діод + конденсатор «обводять» огинаючу — і ось звук.",
              11.5, INK, "middle", "bold")
    save("fig-40-2-1-am-build.svg", s)


# ── Рис. 40.2.2 — глибина модуляції μ ────────────────────────────────────────
def fig22_am_index():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 32, "Глибина модуляції μ: скільки можна «гойдати» амплітуду", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "μ = (A_max − A_min) / (A_max + A_min);  μ ≤ 1 — добре, μ > 1 — спотворення",
              11.5, GREY, "middle", style="italic")
    panels = [
        ("μ = 0.5", 0.5, GREEN, "недомодуляція:", "сигнал слабкий, потужність марнується"),
        ("μ = 1.0", 1.0, BLUE, "повна модуляція:", "максимум без спотворень — ідеал"),
        ("μ = 1.5", 1.5, RED, "перемодуляція:", "огинаюча «провалюється» → спотворення"),
    ]
    for i, (lab, mu, col, t1, t2) in enumerate(panels):
        x0 = 40 + i * 290
        yc = 170
        s += text(x0 + 135, 92, lab, 14, col, "middle", "bold")
        s += amwave(x0 + 10, yc, 250, 44, 22, 2, mu, BLUE, 1.6)
        up, dn = [], []
        for k in range(81):
            t = k / 80
            e = 1 + mu * math.sin(2 * math.pi * 2 * t)
            up.append((x0 + 10 + t * 250, yc - 44 * e))
            dn.append((x0 + 10 + t * 250, yc + 44 * e))
        s += _poly(up, col, 1.6)
        s += _poly(dn, col, 1.6)
        if mu > 1:
            s += line(x0 + 10, yc, x0 + 260, yc, RED, 1, "3 3")
        s += text(x0 + 135, 262, t1, 11, col, "middle", "bold")
        s += text(x0 + 135, 280, t2, 9.8, GREY, "middle")
    save("fig-40-2-2-am-index.svg", s)


# ── Рис. 40.2.3 — спектр AM: несуча + дві бічні смуги ─────────────────────────
def fig23_am_sidebands():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 32, "Спектр AM: несуча плюс дві бічні смуги", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "тон fₘ породжує лінії на fₒ та fₒ ± fₘ; уся інформація — у бічних смугах",
              12, GREY, "middle", style="italic")
    ax = 250
    s += line(80, ax, 820, ax, INK, 2)
    s += text(820, ax + 20, "частота", 10, GREY, "end")
    fc_x = 450
    s += _stem(fc_x, ax, 150, BLUE, 4)
    s += text(fc_x, ax - 158, "несуча fₒ", 12, BLUE, "middle", "bold")
    s += text(fc_x, ax + 20, "fₒ", 11, INK, "middle", "bold")
    s += _stem(fc_x - 130, ax, 70, RED, 4)
    s += _stem(fc_x + 130, ax, 70, RED, 4)
    s += text(fc_x - 130, ax + 20, "fₒ−fₘ", 10.5, RED, "middle", "bold")
    s += text(fc_x + 130, ax + 20, "fₒ+fₘ", 10.5, RED, "middle", "bold")
    s += text(fc_x - 130, ax - 78, "бічна", 10, RED, "middle", "bold")
    s += text(fc_x + 130, ax - 78, "бічна", 10, RED, "middle", "bold")
    # дужка смуги
    s += line(fc_x - 130, ax - 110, fc_x + 130, ax - 110, GREEN, 1.6)
    s += line(fc_x - 130, ax - 105, fc_x - 130, ax - 115, GREEN, 1.6)
    s += line(fc_x + 130, ax - 105, fc_x + 130, ax - 115, GREEN, 1.6)
    s += text(fc_x, ax - 118, "смуга = 2·fₘ", 11, GREEN, "middle", "bold")

    s += rect(60, ax + 56, W - 120, 70, LGREY, GREY, 1.2, 9)
    s += text(W / 2, ax + 80, "Приклад: несуча 1000 кГц + тон 5 кГц → лінії 995, 1000, 1005 кГц; смуга = 10 кГц.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, ax + 102, "Несуча — половина-дві третини потужності, але інформації в ній нуль; вона лише «тримає» бічні смуги.",
              10.5, GREY, "middle", style="italic")
    save("fig-40-2-3-am-sidebands.svg", s)


# ── Рис. 40.2.4 — будова FM ──────────────────────────────────────────────────
def fig24_fm_build():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Частотна модуляція (FM): повідомлення керує частотою", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "амплітуда стала; густо = висока миттєва частота, рідко = низька — у такт зі звуком",
              12, GREY, "middle", style="italic")
    # рядок 1 — повідомлення
    s += text(40, 96, "повідомлення m(t):", 11.5, GREEN, "start", "bold")
    s += sine(60, 134, 780, 26, 2, GREEN, 2.4)
    # рядок 2 — FM
    s += text(40, 222, "FM-сигнал (стала амплітуда):", 11.5, INK, "start", "bold")
    yc = 290
    s += fmwave(60, yc, 780, 52, 20, 30, 2, GREEN, 2)
    # сталі межі амплітуди
    s += line(60, yc - 52, 840, yc - 52, BLUE, 1.2, "5 4")
    s += line(60, yc + 52, 840, yc + 52, BLUE, 1.2, "5 4")
    s += text(850, yc - 52, "амплітуда", 10, BLUE, "end")
    s += text(850, yc - 40, "стала!", 10, BLUE, "end", "bold")
    s += text(170, yc + 86, "тут m велике → густо", 9.5, GREEN, "middle", "bold")
    s += text(560, yc + 86, "тут m мале → рідко", 9.5, GREEN, "middle", "bold")
    s += rect(60, 360, W - 120, 34, LGRN, GREEN, 1.3, 8)
    s += text(W / 2, 382, "Інформація — у частоті; амплітуда не несе нічого, тож її можна сміливо зрізати разом із шумом.",
              11.5, INK, "middle", "bold")
    save("fig-40-2-4-fm-build.svg", s)


# ── Рис. 40.2.5 — AM проти FM під шумом ──────────────────────────────────────
def fig25_noise():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Чому FM тихіше: доля AM і FM під тим самим шумом", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "шум — це сплески амплітуди; AM несе звук в амплітуді, FM — у частоті",
              12, GREY, "middle", style="italic")
    # AM
    s += text(40, 96, "AM + шум:", 11.5, RED, "start", "bold")
    yc1 = 140
    s += amwave(60, yc1, 780, 36, 24, 2, 0.7, BLUE, 1.5)
    s += noisy(60, yc1, 780, 30, RED, 1.4)
    s += text(850, yc1 - 50, "шум псує гучність → тріск", 10, RED, "end", "bold")
    # FM
    s += text(40, 240, "FM + той самий шум → обмежувач зрізає амплітуду:", 11.5, GREEN, "start", "bold")
    yc2 = 300
    s += fmwave(60, yc2, 780, 44, 18, 26, 2, GREEN, 1.8)
    s += line(60, yc2 - 44, 840, yc2 - 44, INK, 1.4, "4 4")
    s += line(60, yc2 + 44, 840, yc2 + 44, INK, 1.4, "4 4")
    s += text(850, yc2 - 60, "амплітуду (і шум) зрізано;", 10, GREEN, "end", "bold")
    s += text(850, yc2 - 46, "частота ціла → чистий звук", 10, GREEN, "end")
    s += rect(60, 360, W - 120, 34, LGRN, GREEN, 1.3, 8)
    s += text(W / 2, 382, "Це і є відкриття Армстронга (історія розділу): ширша FM ховає шум глибше — обмін «смуга ⇄ тиша».",
              11, INK, "middle", "bold")
    save("fig-40-2-5-noise.svg", s)


# ── Рис. 40.2.6 — смуга FM, правило Карсона ──────────────────────────────────
def fig26_fm_bandwidth():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 32, "Ціна тиші — смуга: правило Карсона", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "B ≈ 2·(Δf + fₘ): що більша девіація Δf, то ширша смуга й глибша завадостійкість",
              12, GREY, "middle", style="italic")
    # вузька FM
    s += text(230, 96, "вузька FM (мала Δf)", 12.5, AMBER, "middle", "bold")
    ax1 = 230
    s += line(80, ax1, 400, ax1, INK, 1.8)
    for dx in (-30, 0, 30):
        s += _stem(230 + dx, ax1, 70 if dx == 0 else 44, AMBER, 3)
    s += line(200, ax1 - 90, 260, ax1 - 90, GREEN, 1.4)
    s += text(230, ax1 - 96, "вузько", 9.5, GREEN, "middle", "bold")
    s += text(230, ax1 + 22, "тісно, але шумніше", 9.5, GREY, "middle")
    # широка FM
    s += text(650, 96, "широка FM (велика Δf)", 12.5, GREEN, "middle", "bold")
    ax2 = 230
    s += line(480, ax2, 820, ax2, INK, 1.8)
    for dx in (-90, -60, -30, 0, 30, 60, 90):
        s += _stem(650 + dx, ax2, 70 if dx == 0 else (52 if abs(dx) <= 60 else 32), GREEN, 3)
    s += line(560, ax2 - 90, 740, ax2 - 90, GREEN, 1.4)
    s += text(650, ax2 - 96, "широко → тихо", 9.5, GREEN, "middle", "bold")
    s += text(650, ax2 + 22, "багато смуги, зате чисто", 9.5, GREY, "middle")

    s += rect(60, 278, W - 120, 78, LBLUE, BLUE, 1.3, 9)
    s += text(W / 2, 302, "FM-мовлення: Δf = 75 кГц, звук до fₘ = 15 кГц → B ≈ 2·(75+15) = 180 кГц (канал 200 кГц).",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 324, "Порівняй: AM-канал — лише 10 кГц. FM займає у ~20 разів ширше — і цим купує свою чистоту.",
              11, INK, "middle")
    s += text(W / 2, 346, "Той самий обмін смуга↔якість Шеннон зробить точним законом — про межу йтиметься у §40.4.",
              10, GREY, "middle", style="italic")
    save("fig-40-2-6-fm-bandwidth.svg", s)


# ── Рис. 40.2.7 — AM проти FM: підсумкове порівняння ─────────────────────────
def fig27_tradeoff():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "AM проти FM: чесне порівняння", 19.5, INK, "middle", "bold")
    s += text(W / 2, 54, "немає «кращої» — є компроміс між простотою, смугою та завадостійкістю",
              12, GREY, "middle", style="italic")
    rows = [
        ("Смуга", "вузька (2·fₘ)", "широка (2(Δf+fₘ))"),
        ("Шум / статика", "вразлива", "стійка (зрізає амплітуду)"),
        ("Приймач", "простий: діод+RC", "складніший: дискримінатор/ФАПЧ"),
        ("Потужність", "несуча марнує", "стала огинаюча → ККД підсилювача"),
        ("Типове вживання", "AM-мовлення, авіація, КХ", "FM-радіо, рації, звук ТБ"),
    ]
    x0, y0, wlab, wcol = 60, 92, 200, 280
    s += rect(x0, y0, wlab, 38, "#f0f0f0", GREY, 1.3)
    s += rect(x0 + wlab, y0, wcol, 38, LRED, RED, 1.4)
    s += rect(x0 + wlab + wcol, y0, wcol, 38, LGRN, GREEN, 1.4)
    s += text(x0 + wlab / 2, y0 + 25, "критерій", 12, INK, "middle", "bold")
    s += text(x0 + wlab + wcol / 2, y0 + 25, "AM", 14, RED, "middle", "bold")
    s += text(x0 + wlab + wcol + wcol / 2, y0 + 25, "FM", 14, GREEN, "middle", "bold")
    yy = y0 + 38
    for lab, am, fm in rows:
        s += rect(x0, yy, wlab, 44, "#fafafa", GREY, 1)
        s += rect(x0 + wlab, yy, wcol, 44, "#fff", "#e0c4c4", 1)
        s += rect(x0 + wlab + wcol, yy, wcol, 44, "#fff", "#c4dcc8", 1)
        s += text(x0 + 12, yy + 27, lab, 11.5, INK, "start", "bold")
        s += text(x0 + wlab + wcol / 2, yy + 27, am, 10.3, INK, "middle")
        s += text(x0 + wlab + wcol + wcol / 2, yy + 27, fm, 10.3, INK, "middle")
        yy += 44
    save("fig-40-2-7-tradeoff.svg", s)


# ============================================================================
#  §40.3 — Цифрова модуляція: FSK, PSK
# ============================================================================

def dig_wave(x0, y0, seg, amp, bits, kind, color, w=2):
    """Цифрова модуляція бітів: kind ∈ {'ask','fsk','psk'}; цілі цикли на сегмент."""
    pts = []
    npc = 48
    for bi, b in enumerate(bits):
        if kind == "fsk":
            cyc = 4 if b == 1 else 2
        else:
            cyc = 3
        ph = math.pi if (kind == "psk" and b == 0) else 0.0
        a = amp if not (kind == "ask" and b == 0) else amp * 0.10
        for i in range(npc + 1):
            t = i / npc
            x = x0 + (bi + t) * seg
            y = y0 - a * math.sin(2 * math.pi * cyc * t + ph)
            pts.append((x, y))
    return _poly(pts, color, w)


def constel(cx, cy, r, pts, color, dot=5):
    s = line(cx - r - 16, cy, cx + r + 16, cy, GREY, 1.4)
    s += line(cx, cy + r + 16, cx, cy - r - 16, GREY, 1.4)
    s += text(cx + r + 22, cy + 4, "I", 10, GREY, "middle")
    s += text(cx + 4, cy - r - 20, "Q", 10, GREY, "middle")
    for (px, py) in pts:
        s += circle(cx + px * r, cy - py * r, dot, color, color, 0)
    return s


# ── Рис. 40.3.1 — три цифрові keying: ASK / FSK / PSK ────────────────────────
def fig31_keyings():
    W, H = 920, 470
    s = header(W, H)
    s += text(W / 2, 32, "Цифрова модуляція: ті самі три ручки, але дискретно", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "біти 0/1 перемикають амплітуду (ASK), частоту (FSK) або фазу (PSK) несучої",
              12, GREY, "middle", style="italic")
    bits = [1, 0, 1, 1, 0, 0, 1, 0]
    seg = 96
    x0 = 70
    # бітова доріжка
    s += text(40, 92, "біти:", 11, INK, "start", "bold")
    for bi, b in enumerate(bits):
        s += text(x0 + (bi + 0.5) * seg, 92, str(b), 13, INK, "middle", "bold")
        s += line(x0 + bi * seg, 100, x0 + bi * seg, 430, FAINT, 1, "3 3")
    s += line(x0 + len(bits) * seg, 100, x0 + len(bits) * seg, 430, FAINT, 1, "3 3")
    # ASK
    s += text(40, 150, "ASK", 12, RED, "start", "bold")
    s += text(40, 166, "(амплітуда)", 8.5, GREY, "start")
    s += dig_wave(x0, 158, seg, 30, bits, "ask", RED, 1.9)
    # FSK
    s += text(40, 258, "FSK", 12, GREEN, "start", "bold")
    s += text(40, 274, "(частота)", 8.5, GREY, "start")
    s += dig_wave(x0, 266, seg, 30, bits, "fsk", GREEN, 1.9)
    # PSK
    s += text(40, 366, "PSK", 12, BLUE, "start", "bold")
    s += text(40, 382, "(фаза)", 8.5, GREY, "start")
    s += dig_wave(x0, 374, seg, 30, bits, "psk", BLUE, 1.9)
    s += text(x0 + 2.5 * seg, 410, "↑ розворот фази на межі біта", 9, BLUE, "middle", "bold")
    save("fig-40-3-1-keyings.svg", s)


# ── Рис. 40.3.2 — символ vs біт ──────────────────────────────────────────────
def fig32_symbols():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 32, "Символ і біт: один стан несучої може нести кілька бітів", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "якщо станів M, то один символ кодує log₂M бітів — основа всіх швидких ліній",
              11.5, GREY, "middle", style="italic")
    rows = [
        ("BPSK", "2", "1", "найнадійніша, найповільніша"),
        ("QPSK", "4", "2", "удвічі швидша за ту саму смугу"),
        ("8-PSK", "8", "3", "ще швидша, але тісніша"),
        ("16-QAM", "16", "4", "Wi-Fi/LTE; треба добрий сигнал"),
        ("256-QAM", "256", "8", "максимум швидкості, лише поблизу"),
    ]
    x0, y0 = 110, 92
    cols = [("схема", 150), ("станів M", 150), ("біт/символ", 160), ("характер", 300)]
    cx = x0
    for nm, wd in cols:
        s += rect(cx, y0, wd, 36, "#f0f0f0", GREY, 1.3)
        s += text(cx + wd / 2, y0 + 24, nm, 11.5, INK, "middle", "bold")
        cx += wd
    yy = y0 + 36
    for sch, m, bps, note in rows:
        cx = x0
        vals = [(sch, BLUE, "bold"), (m, INK, "normal"), (bps, GREEN, "bold"), (note, GREY, "italic")]
        for (val, col, wt), (nm, wd) in zip(vals, cols):
            s += rect(cx, yy, wd, 40, "#fff", "#e2e2e2", 1)
            st = "italic" if wt == "italic" else "normal"
            we = "bold" if wt == "bold" else "normal"
            s += text(cx + (12 if nm == "характер" else wd / 2), yy + 26, val, 11,
                      col, ("start" if nm == "характер" else "middle"), we, st)
            cx += wd
        yy += 40
    s += text(W / 2, yy + 26, "біт/символ = log₂M → подвоїти кількість станів = +1 біт на символ",
              11.5, INK, "middle", "bold")
    save("fig-40-3-2-symbols.svg", s)


# ── Рис. 40.3.3 — сузір'я ────────────────────────────────────────────────────
def fig33_constellation():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 32, "Сузір'я: карта станів несучої на площині I/Q", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "кожна точка — це амплітуда (відстань від центру) і фаза (кут); біти кодують позицією",
              11.5, GREY, "middle", style="italic")
    # BPSK
    s += constel(180, 200, 70, [(-0.85, 0), (0.85, 0)], BLUE)
    s += text(180, 300, "BPSK — 2 точки", 12, BLUE, "middle", "bold")
    s += text(180, 318, "1 біт/символ", 10, GREY, "middle")
    # QPSK
    q = 0.7
    s += constel(450, 200, 70, [(q, q), (-q, q), (-q, -q), (q, -q)], GREEN)
    s += text(450, 300, "QPSK — 4 точки", 12, GREEN, "middle", "bold")
    s += text(450, 318, "2 біти/символ", 10, GREY, "middle")
    # 16-QAM
    levels = [-1, -1 / 3, 1 / 3, 1]
    pts = [(i, j) for i in levels for j in levels]
    s += constel(720, 200, 70, pts, AMBER, 4)
    s += text(720, 300, "16-QAM — 16 точок", 12, AMBER, "middle", "bold")
    s += text(720, 318, "4 біти/символ", 10, GREY, "middle")
    save("fig-40-3-3-constellation.svg", s)


# ── Рис. 40.3.4 — шум розмиває точки ─────────────────────────────────────────
def fig34_noise():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 32, "Чому не можна нескінченно ущільнювати: шум розмиває точки", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "шум перетворює кожну точку на «хмарку»; перекрилися хмарки — приймач плутає біти",
              11.5, GREY, "middle", style="italic")
    # QPSK — хмарки далеко
    q = 0.72
    for (px, py) in [(q, q), (-q, q), (-q, -q), (q, -q)]:
        cx, cy = 230 + px * 90, 200 - py * 90
        s += circle(cx, cy, 26, "none", GREEN, 1.2)
        s += circle(cx, cy, 4, GREEN, GREEN, 0)
    s += line(140, 200, 320, 200, GREY, 1.2)
    s += line(230, 110, 230, 290, GREY, 1.2)
    s += text(230, 320, "QPSK: хмарки далеко", 12, GREEN, "middle", "bold")
    s += text(230, 338, "→ помилок мало", 10, GREEN, "middle")
    # 16-QAM — хмарки близько, перекриття
    levels = [-1, -1 / 3, 1 / 3, 1]
    for i in levels:
        for j in levels:
            cx, cy = 670 + i * 95, 200 - j * 95
            s += circle(cx, cy, 15, "none", RED, 1)
            s += circle(cx, cy, 3, RED, RED, 0)
    s += line(560, 200, 780, 200, GREY, 1.2)
    s += line(670, 95, 670, 305, GREY, 1.2)
    s += text(670, 320, "16-QAM: хмарки тісні", 12, RED, "middle", "bold")
    s += text(670, 338, "→ треба сильніший сигнал (вищий SNR)", 9.5, RED, "middle")
    save("fig-40-3-4-noise.svg", s)


# ── Рис. 40.3.5 — бод vs біт/с ───────────────────────────────────────────────
def fig35_baud():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 32, "Бод проти біт/с: чому це не одне й те саме", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "бод — символів за секунду; біт/с = бод × (біт/символ)", 12, GREY, "middle", style="italic")
    s += text(W / 2, 92, "бітова швидкість = символьна швидкість (бод) × log₂M", 14, INK, "middle", "bold")
    s += text(W / 2, 118, "приклад: символьна швидкість 1 Мбод (термін «бод» — із Розділу 35)", 10.5, GREY, "middle", style="italic")
    bars = [("BPSK", 1, BLUE), ("QPSK", 2, GREEN), ("16-QAM", 4, AMBER)]
    yy = 150
    for nm, bps, col in bars:
        s += text(135, yy + 23, nm, 12, col, "start", "bold")
        fill = "#e9eefb" if col == BLUE else ("#eef6ef" if col == GREEN else LAMB)
        s += rect(245, yy, bps * 120, 34, fill, col, 1.8, 5)
        s += text(245 + bps * 120 + 12, yy + 23, f"= 1 Мбод × {bps} = {bps} Мбіт/с", 11.5, INK, "start", "bold")
        yy += 50
    s += rect(60, 300, W - 120, 30, LGRN, GREEN, 1.3, 8)
    s += text(W / 2, 320, "Та сама смуга (1 Мбод) — а біт/с різні: ось як ущільнення символів прискорює лінію.",
              11.5, INK, "middle", "bold")
    save("fig-40-3-5-baud.svg", s)


# ── Рис. 40.3.6 — надійність проти швидкості ─────────────────────────────────
def fig36_tradeoff():
    W, H = 900, 350
    s = header(W, H)
    s += text(W / 2, 32, "Головний компроміс: надійність ↔ швидкість", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "що більше точок у сузір'ї, то швидше — але то сильніший потрібен сигнал",
              12, GREY, "middle", style="italic")
    ax_y = 250
    s += arrow(80, ax_y, 840, ax_y, INK, 2)
    s += text(80, ax_y + 26, "надійно / повільно", 11, GREEN, "start", "bold")
    s += text(840, ax_y + 26, "швидко / крихко", 11, RED, "end", "bold")
    items = [("FSK\nBPSK", 130, GREEN), ("QPSK", 320, GREEN), ("16-QAM", 510, AMBER), ("64-QAM", 660, AMBER), ("256-QAM", 800, RED)]
    for lab, x, col in items:
        s += _stem(x, ax_y, 90, col, 3)
        s += circle(x, ax_y - 90, 6, col, col, 0)
        for k, part in enumerate(lab.split("\n")):
            s += text(x, ax_y - 104 - (len(lab.split('\n')) - 1 - k) * 15, part, 11, col, "middle", "bold")
    s += text(W / 2, 96, "потрібний рівень сигналу (SNR) росте зліва направо →", 11, INK, "middle", style="italic")
    s += rect(60, 290, W - 120, 50, LBLUE, BLUE, 1.3, 9)
    s += text(W / 2, 312, "Сучасні лінії (Wi-Fi, LTE) міняють модуляцію НА ЛЬОТУ: близько й чисто — 256-QAM;",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 331, "далеко чи завадно — падають до QPSK/BPSK. Це адаптивна модуляція.", 11, GREY, "middle", style="italic")
    save("fig-40-3-6-tradeoff.svg", s)


# ── Рис. 40.3.7 — що вживають реальні радіо Модуля 6 ─────────────────────────
def fig37_real():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 32, "Що насправді вживають радіо з нашого курсу", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "за знайомими назвами з Розділу 38 — цілком конкретні цифрові модуляції",
              12, GREY, "middle", style="italic")
    cards = [
        ("Bluetooth / BLE", "GFSK", "згладжена FSK — проста й ощадна до енергії", BLUE),
        ("Wi-Fi", "OFDM:\nBPSK→256-QAM", "багато піднесучих + адаптивне сузір'я", GREEN),
        ("LoRa", "CSS (чирп)", "розширений спектр заради дальності", AMBER),
        ("RC / телеметрія", "FSK / GFSK", "надійність важливіша за швидкість", RED),
    ]
    x = 40
    for nm, mod, desc, col in cards:
        s += rect(x, 88, 205, 200, "#fbfbfb", col, 2, 12)
        s += text(x + 102, 120, nm, 13, INK, "middle", "bold")
        yy = 150
        for part in mod.split("\n"):
            s += text(x + 102, yy, part, 13.5, col, "middle", "bold")
            yy += 20
        words = desc.split()
        ln, ty = "", yy + 14
        for wd in words:
            if len(ln) + len(wd) > 24:
                s += text(x + 102, ty, ln.strip(), 9.8, GREY, "middle")
                ln, ty = "", ty + 16
            ln += wd + " "
        s += text(x + 102, ty, ln.strip(), 9.8, GREY, "middle")
        x += 213
    save("fig-40-3-7-real.svg", s)


# ============================================================================
#  §40.4 — Смуга й швидкість (натяк на межу Шеннона)
# ============================================================================

# ── Рис. 40.4.1 — формула Шеннона ────────────────────────────────────────────
def fig41_formula():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 36, "Межа Шеннона: абсолютна стеля швидкості будь-якої лінії", 19, INK, "middle", "bold")
    s += text(W / 2, 58, "1948 рік — закон, який не обійти жодною модуляцією чи кодуванням",
              12, GREY, "middle", style="italic")
    # формула
    s += rect(230, 96, 440, 86, LBLUE, BLUE, 2, 14)
    s += text(W / 2, 152, "C = B · log₂(1 + S/N)", 30, INK, "middle", "bold")
    # підписи
    s += text(300, 230, "C", 18, GREEN, "middle", "bold")
    s += text(300, 252, "макс. біт/с", 11, GREEN, "middle", "bold")
    s += text(300, 268, "(пропускна здатність)", 9.5, GREY, "middle")
    s += arrow(300, 210, 360, 178, GREEN, 1.8)
    s += text(470, 230, "B", 18, BLUE, "middle", "bold")
    s += text(470, 252, "смуга (Гц)", 11, BLUE, "middle", "bold")
    s += text(470, 268, "ширина каналу", 9.5, GREY, "middle")
    s += arrow(470, 210, 470, 184, BLUE, 1.8)
    s += text(650, 230, "S/N", 18, RED, "middle", "bold")
    s += text(650, 252, "сигнал/шум", 11, RED, "middle", "bold")
    s += text(650, 268, "(у разах, не дБ!)", 9.5, GREY, "middle")
    s += arrow(640, 210, 600, 178, RED, 1.8)
    s += rect(60, 300, W - 120, 30, LGRN, GREEN, 1.3, 8)
    s += text(W / 2, 320, "Нижче за C — зв'язок без помилок можливий; вище за C — неможливий у принципі. Крапка.",
              11.5, INK, "middle", "bold")
    save("fig-40-4-1-formula.svg", s)


# ── Рис. 40.4.2 — два важелі: смуга й потужність ─────────────────────────────
def fig42_two_levers():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Два важелі ємності — і вони дуже різні", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "смуга піднімає C лінійно, а потужність (S/N) — лише логарифмічно",
              12, GREY, "middle", style="italic")
    # смуга — лінійно
    s += rect(60, 86, 380, 230, "#fbfbfb", BLUE, 2, 12)
    s += text(250, 114, "Смуга B — щедрий важіль", 13.5, BLUE, "middle", "bold")
    s += text(250, 138, "×2 смуги → ×2 швидкості", 12, INK, "middle", "bold")
    for i, (b, h) in enumerate([(1, 50), (2, 100), (4, 200)]):
        x = 110 + i * 110
        s += rect(x, 300 - h, 60, h, LBLUE, BLUE, 1.6, 4)
        s += text(x + 30, 300 - h - 8, f"×{b}", 11, BLUE, "middle", "bold")
        s += text(x + 30, 312, f"B={b}", 9.5, GREY, "middle")
    # потужність — логарифмічно
    s += rect(460, 86, 380, 230, "#fbfbfb", RED, 2, 12)
    s += text(650, 114, "Потужність S/N — скупий важіль", 12.5, RED, "middle", "bold")
    s += text(650, 138, "×2 потужності → лише +1 біт/с/Гц", 11.5, INK, "middle", "bold")
    for i, (lab, h) in enumerate([("S/N", 120), ("×2", 150), ("×4", 175), ("×8", 195)]):
        x = 500 + i * 82
        s += rect(x, 300 - h, 50, h, LRED, RED, 1.6, 4)
        s += text(x + 25, 300 - h - 8, lab, 10, RED, "middle", "bold")
    s += text(650, 250, "+1   +1   +1 ...", 11, GREY, "middle", style="italic")
    s += text(650, 295, "вісім разів потужності — лише +3 біти", 9.5, GREY, "middle")
    save("fig-40-4-2-two-levers.svg", s)


# ── Рис. 40.4.3 — крива ємності від SNR ──────────────────────────────────────
def fig43_curve():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Спектральна ефективність від сигнал/шум: логарифм", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "C/B = log₂(1 + S/N): кожні +10 дБ потужності додають лише ~3.3 біт/с/Гц",
              11.5, GREY, "middle", style="italic")
    ox, oy = 110, 330
    axw, axh = 700, 250
    s += arrow(ox, oy, ox + axw, oy, INK, 2)
    s += arrow(ox, oy, ox, oy - axh, INK, 2)
    s += text(ox + axw - 4, oy + 24, "S/N, дБ", 11, INK, "end", "bold")
    s += text(ox - 70, oy - axh + 10, "біт/с/Гц", 11, INK, "start", "bold")
    # вісь X: -5..40 дБ ; Y: 0..14
    def X(db):
        return ox + (db + 5) / 45 * axw
    def Y(bits):
        return oy - bits / 14 * axh
    for db in range(0, 41, 10):
        s += line(X(db), oy, X(db), oy + 5, INK, 1.4)
        s += text(X(db), oy + 22, str(db), 10, GREY, "middle")
    for bt in range(0, 15, 2):
        s += line(ox - 5, Y(bt), ox, Y(bt), INK, 1.4)
        s += text(ox - 12, Y(bt) + 4, str(bt), 10, GREY, "end")
    # крива
    pts = []
    db = -5.0
    while db <= 40.01:
        snr = 10 ** (db / 10)
        bits = math.log2(1 + snr)
        pts.append((X(db), Y(bits)))
        db += 1.0
    s += _poly(pts, GREEN, 2.8)
    # позначки
    for db, lab in [(0, "0 дБ → 1.0"), (10, "10 дБ → 3.5"), (20, "20 дБ → 6.7"), (30, "30 дБ → 10")]:
        snr = 10 ** (db / 10)
        bits = math.log2(1 + snr)
        s += circle(X(db), Y(bits), 4, RED, RED, 0)
        s += text(X(db) + 8, Y(bits) - 8, lab, 9.5, RED, "start", "bold")
    s += text(ox + axw - 30, Y(13) - 6, "діагональ діє лінійно зі смугою,", 9.5, BLUE, "end", style="italic")
    s += text(ox + axw - 30, Y(13) + 8, "а тут — логарифм від потужності", 9.5, BLUE, "end", style="italic")
    save("fig-40-4-3-curve.svg", s)


# ── Рис. 40.4.4 — стіна Шеннона ──────────────────────────────────────────────
def fig44_wall():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 34, "Стіна Шеннона: межа можливого й неможливого", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "нижче межі — є кодування, що дає зв'язок майже без помилок; вище — жодне не врятує",
              11.5, GREY, "middle", style="italic")
    bx, by, bw, bh = 120, 90, 660, 170
    # зелена зона
    s += rect(bx, by, bw * 0.62, bh, LGRN, GREEN, 1.6, 8)
    s += text(bx + bw * 0.31, by + 70, "МОЖЛИВО", 18, GREEN, "middle", "bold")
    s += text(bx + bw * 0.31, by + 98, "зв'язок без помилок (з кодуванням)", 11, INK, "middle")
    # червона зона
    s += rect(bx + bw * 0.62, by, bw * 0.38, bh, LRED, RED, 1.6, 8)
    s += text(bx + bw * 0.81, by + 70, "НЕМОЖЛИВО", 15, RED, "middle", "bold")
    s += text(bx + bw * 0.81, by + 98, "за жодних хитрощів", 10.5, INK, "middle")
    # межа
    s += line(bx + bw * 0.62, by - 12, bx + bw * 0.62, by + bh + 12, INK, 3)
    s += text(bx + bw * 0.62, by - 20, "C = B·log₂(1+S/N)", 12, INK, "middle", "bold")
    s += text(W / 2, by + bh + 44, "Інженер може підійти до межі скільзавгодно близько — але не перетнути її.",
              12, INK, "middle", "bold")
    save("fig-40-4-4-wall.svg", s)


# ── Рис. 40.4.5 — телефонна лінія й модем ────────────────────────────────────
def fig45_modem():
    W, H = 900, 350
    s = header(W, H)
    s += text(W / 2, 34, "Класичний приклад: чому дозвонний модем застряг на 33.6k", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "межа Шеннона для телефонної лінії пояснює стелю старих модемів точним числом",
              11.5, GREY, "middle", style="italic")
    s += rect(90, 86, 720, 96, LGREY, GREY, 1.4, 10)
    s += text(120, 116, "Дано (телефонна лінія):", 12.5, INK, "start", "bold")
    s += text(140, 140, "смуга B ≈ 3100 Гц", 12, BLUE, "start", "bold")
    s += text(140, 162, "сигнал/шум ≈ 30 дБ  =  1000 разів", 12, RED, "start", "bold")
    s += text(470, 140, "C = 3100 · log₂(1 + 1000)", 13, INK, "start", "bold")
    s += text(470, 162, "C ≈ 3100 · 9.97 ≈ 30 900 біт/с", 13, GREEN, "start", "bold")
    s += rect(90, 200, 720, 120, LGRN, GREEN, 1.5, 10)
    s += text(W / 2, 228, "≈ 31 кбіт/с — і ось чому дозвонні модеми вперлися в 33.6 кбіт/с!", 13.5, INK, "middle", "bold")
    s += text(W / 2, 254, "Це не вада техніки, а фізична стеля самої лінії. Жоден модем її не обійшов.", 11, GREY, "middle", style="italic")
    s += text(W / 2, 282, "А «56k» зміг більше лише тому, що зробив один бік лінії повністю цифровим —", 10.5, INK, "middle")
    s += text(W / 2, 300, "тобто змінив саму задачу (підняв S/N), а не переміг закон Шеннона.", 10.5, INK, "middle")
    save("fig-40-4-5-modem.svg", s)


# ── Рис. 40.4.6 — Шеннон пояснює весь розділ ─────────────────────────────────
def fig46_connects():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 34, "Один закон під усім розділом", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "усі модуляції, що ми бачили, — це різні способи торгувати смугою й потужністю в межах Шеннона",
              11, GREY, "middle", style="italic")
    items = [
        ("FM (Армстронг)", "міняє СМУГУ на запас від шуму", "ширше → тихіше", GREEN),
        ("QAM / сузір'я", "міняє S/N на БІТИ за символ", "більше SNR → щільніше", BLUE),
        ("Розширений спектр", "міняє смугу на стійкість/секретність", "далі — §40.5", AMBER),
    ]
    x = 45
    for nm, what, how, col in items:
        s += rect(x, 90, 270, 150, "#fbfbfb", col, 2, 12)
        s += text(x + 135, 122, nm, 14, col, "middle", "bold")
        words = what.split()
        ln, yy = "", 152
        for wd in words:
            if len(ln) + len(wd) > 24:
                s += text(x + 135, yy, ln.strip(), 11, INK, "middle", "bold")
                ln, yy = "", yy + 19
            ln += wd + " "
        s += text(x + 135, yy, ln.strip(), 11, INK, "middle", "bold")
        s += text(x + 135, 224, how, 10, GREY, "middle", style="italic")
        x += 290
    s += rect(60, 256, W - 120, 30, LBLUE, BLUE, 1.3, 8)
    s += text(W / 2, 276, "Шеннон не дає рецепту «як», але ставить стелю «скільки» — і під цією стелею живе вся радіотехніка.",
              11.5, INK, "middle", "bold")
    save("fig-40-4-6-connects.svg", s)


# ── Рис. 40.4.7 — Клод Шеннон ────────────────────────────────────────────────
def fig47_shannon():
    W, H = 900, 320
    s = header(W, H)
    s += text(W / 2, 34, "Людина за межею: Клод Шеннон і народження теорії інформації", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "1948 рік, Bell Labs — стаття, що заснувала цілу науку про передавання даних",
              11.5, GREY, "middle", style="italic")
    # центральна постать
    s += circle(170, 170, 46, LBLUE, BLUE, 2)
    s += text(170, 166, "Клод", 14, BLUE, "middle", "bold")
    s += text(170, 186, "Шеннон", 14, BLUE, "middle", "bold")
    s += text(170, 240, "1916–2001", 10.5, GREY, "middle")
    # внески
    facts = [
        "«A Mathematical Theory of Communication» (1948) — заснувала теорію інформації",
        "Увів у науку біт як одиницю інформації",
        "Довів межу C — і що до неї можна підійти скільзавгодно близько хорошим кодуванням",
    ]
    yy = 116
    for f in facts:
        s += circle(280, yy - 4, 3.5, GREEN, GREEN, 0)
        s += text(296, yy, f, 11, INK, "start")
        yy += 30
    # попередники
    s += rect(280, 212, 580, 70, LGREY, GREY, 1.3, 8)
    s += text(296, 236, "Чесно про попередників (наука — колективна):", 11, INK, "start", "bold")
    s += text(296, 258, "Гаррі Найквіст (1924) і Ралф Гартлі (1928), теж із Bell Labs, заклали підвалини —", 10, GREY, "start")
    s += text(296, 274, "тому й «Шеннон–Гартлі». Та саме синтез 1948 року, що дав точну межу, належить Шеннону.", 10, GREY, "start")
    save("fig-40-4-7-shannon.svg", s)


# ============================================================================
#  §40.5 — Завадостійкість і розширений спектр (стрибки частоти)
# ============================================================================

def sq_wave(x0, y0, length, amp, pattern, color, w=2.2):
    """Прямокутна хвиля за списком ±1; вертикалі на переходах."""
    seg = length / len(pattern)
    pts = []
    prev = None
    for i, v in enumerate(pattern):
        y = y0 - amp * v
        x1, x2 = x0 + i * seg, x0 + (i + 1) * seg
        if prev is not None and prev != v:
            pts.append((x1, y0 - amp * prev))
        pts.append((x1, y))
        pts.append((x2, y))
        prev = v
    return _poly(pts, color, w)


def _bump(cx, base, w, h, color, wid=2):
    pts = []
    for i in range(31):
        t = i / 30
        pts.append((cx - w / 2 + t * w, base - h * math.exp(-((t - 0.5) * 4.2) ** 2)))
    return _poly(pts, color, wid)


# ── Рис. 40.5.1 — ідея розширення спектра ────────────────────────────────────
def fig51_spread_idea():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Розширений спектр: навмисне «розмазати» сигнал по широкій смузі", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "та сама потужність, але розкидана так тонко, що ледь вища за шум — зате стійка й непомітна",
              11, GREY, "middle", style="italic")
    # вузький
    ax1 = 250
    s += line(70, ax1, 410, ax1, INK, 1.8)
    s += _bump(200, ax1, 60, 150, RED, 2.4)
    s += text(200, 90, "вузька смуга", 12, RED, "middle", "bold")
    s += text(200, ax1 + 22, "висока, помітна, вразлива", 9.5, GREY, "middle")
    # стрілка
    s += arrow(420, ax1 - 60, 480, ax1 - 60, INK, 2.2)
    s += text(450, ax1 - 72, "розмазати", 9.5, INK, "middle", "bold")
    # широкий
    ax2 = 250
    s += line(500, ax2, 840, ax2, INK, 1.8)
    s += rect(540, ax2 - 38, 260, 38, LGRN, GREEN, 2, 3)
    s += text(670, 90, "широка смуга", 12, GREEN, "middle", "bold")
    s += text(670, ax2 + 22, "низька, схожа на шум, стійка", 9.5, GREY, "middle")
    s += line(540, ax2 - 60, 800, ax2 - 60, GREY, 1.2, "4 3")
    s += text(810, ax2 - 56, "рівень шуму", 9, GREY, "start")
    s += rect(60, 300, W - 120, 30, LGRN, GREEN, 1.3, 8)
    s += text(W / 2, 320, "Дивно, але корисно: ширша смуга тут — не заради швидкості, а заради надійності й скритності.",
              11.5, INK, "middle", "bold")
    save("fig-40-5-1-spread-idea.svg", s)


# ── Рис. 40.5.2 — стрибки частоти (FHSS) ─────────────────────────────────────
def fig52_fhss():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Стрибки частоти (FHSS): передавач і приймач скачуть разом", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "обидва міняють частоту за однією псевдовипадковою послідовністю, відомою лише їм",
              11, GREY, "middle", style="italic")
    ox, oy = 110, 320
    cols, rows = 12, 8
    cw, rh = 60, 30
    # сітка
    for c in range(cols + 1):
        s += line(ox + c * cw, oy, ox + c * cw, oy - rows * rh, FAINT, 1)
    for r in range(rows + 1):
        s += line(ox, oy - r * rh, ox + cols * cw, oy - r * rh, FAINT, 1)
    s += text(ox - 16, oy - rows * rh / 2, "частота", 11, INK, "middle", "bold", )
    s += text(ox + cols * cw / 2, oy + 26, "час →", 11, INK, "middle", "bold")
    hops = [3, 6, 1, 7, 2, 5, 0, 4, 6, 2, 7, 3]
    for c, r in enumerate(hops):
        s += rect(ox + c * cw + 4, oy - (r + 1) * rh + 4, cw - 8, rh - 8, LBLUE, BLUE, 1.8, 3)
        if c > 0:
            pr = hops[c - 1]
            s += line(ox + (c - 0.5) * cw, oy - (pr + 0.5) * rh, ox + (c + 0.5) * cw, oy - (r + 0.5) * rh, BLUE, 1, "3 2")
    s += text(ox + cols * cw / 2, 92, "сигнал «перестрибує» каналами — щомиті на новій частоті", 10.5, BLUE, "middle", "bold")
    save("fig-40-5-2-fhss.svg", s)


# ── Рис. 40.5.3 — чому FHSS оминає заваду ────────────────────────────────────
def fig53_fhss_jam():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Чому стрибки б'ють заваду: губимо лише кілька хопів", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "постійна завада сидить на одній частоті; стрибучий сигнал зачіпає її лише зрідка",
              11, GREY, "middle", style="italic")
    ox, oy = 110, 320
    cols, rows = 12, 8
    cw, rh = 60, 30
    for c in range(cols + 1):
        s += line(ox + c * cw, oy, ox + c * cw, oy - rows * rh, FAINT, 1)
    for r in range(rows + 1):
        s += line(ox, oy - r * rh, ox + cols * cw, oy - r * rh, FAINT, 1)
    # завада на каналі 5
    jam = 5
    s += rect(ox, oy - (jam + 1) * rh, cols * cw, rh, "#fde3e3", RED, 1.6)
    s += text(ox + cols * cw + 8, oy - (jam + 0.5) * rh + 4, "завада", 10, RED, "start", "bold")
    s += text(ox + cols * cw + 8, oy - (jam + 0.5) * rh + 18, "(Wi-Fi)", 9, GREY, "start")
    hops = [3, 6, 1, 5, 2, 7, 0, 5, 6, 2, 7, 3]
    for c, r in enumerate(hops):
        hit = (r == jam)
        s += rect(ox + c * cw + 4, oy - (r + 1) * rh + 4, cw - 8, rh - 8,
                  ("#fde3e3" if hit else LGRN), (RED if hit else GREEN), 1.8, 3)
        if hit:
            s += text(ox + (c + 0.5) * cw, oy - (r + 0.5) * rh + 4, "✗", 13, RED, "middle", "bold")
    s += text(ox + cols * cw / 2, 92, "лише 2 з 12 хопів зіпсовано — їх легко перевідправити; решта чисті",
              10.5, GREEN, "middle", "bold")
    s += rect(60, 348, W - 120, 36, LBLUE, BLUE, 1.3, 8)
    s += text(W / 2, 371, "Bluetooth робить ~1600 стрибків/с по 79 каналах, ще й оминає зайняті (адаптивні стрибки, AFH).",
              11, INK, "middle", "bold")
    save("fig-40-5-3-fhss-jam.svg", s)


# ── Рис. 40.5.4 — пряма послідовність (DSSS) ─────────────────────────────────
def fig54_dsss():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Пряма послідовність (DSSS): кожен біт множать на швидкий код", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "1 повільний біт даних × N швидких «чипів» псевдокоду = широкий розмазаний сигнал",
              11, GREY, "middle", style="italic")
    code = [1, -1, 1, 1, -1, 1, -1, -1, 1, -1, 1]  # 11-чиповий (як Barker у Wi-Fi)
    # дані: один біт = +1
    s += text(40, 110, "даних:", 11, GREEN, "start", "bold")
    s += sq_wave(150, 130, 620, 26, [1] * 11, GREEN, 2.6)
    s += text(780, 134, "= 1", 11, GREEN, "start", "bold")
    # код
    s += text(40, 200, "код:", 11, BLUE, "start", "bold")
    s += sq_wave(150, 220, 620, 26, code, BLUE, 2.2)
    s += text(780, 224, "11 чипів", 10, BLUE, "start", "bold")
    # добуток
    s += text(40, 292, "у ефір:", 11, INK, "start", "bold")
    prod = [d * c for d, c in zip([1] * 11, code)]
    s += sq_wave(150, 312, 620, 26, prod, INK, 2.2)
    s += text(780, 316, "= код", 10, GREY, "start")
    s += text(W / 2, 356, "Один біт «розтягнувся» на 11 чипів → смуга у 11 разів ширша, густина — у 11 разів нижча.",
              11, INK, "middle", "bold")
    save("fig-40-5-4-dsss.svg", s)


# ── Рис. 40.5.5 — диво розгортання (processing gain) ─────────────────────────
def fig55_despread():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Диво приймача: код збирає сигнал, а заваду — розмазує", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "множення на той самий код стискає корисний сигнал у вузьку смугу, а вузьку заваду — розпорошує",
              10.5, GREY, "middle", style="italic")
    ax = 250
    s += line(80, ax, 820, ax, INK, 1.8)
    s += text(820, ax + 20, "частота", 10, GREY, "end")
    # розмазаний сигнал (широкий низький) + вузька завада (до розгортання)
    s += rect(150, ax - 30, 240, 30, "#eef6ef", GREEN, 1.4)
    s += text(270, ax - 38, "сигнал (розмазаний)", 9.5, GREEN, "middle", "bold")
    s += _stem(300, ax, 120, RED, 4)
    s += text(300, ax - 128, "вузька завада", 9.5, RED, "middle", "bold")
    s += arrow(420, ax - 60, 500, ax - 60, INK, 2.4)
    s += text(460, ax - 72, "× код", 10, INK, "middle", "bold")
    # після розгортання: сигнал вузький високий, завада розмазана низька
    s += _stem(640, ax, 130, GREEN, 5)
    s += text(640, ax - 138, "сигнал зібрано!", 9.5, GREEN, "middle", "bold")
    s += rect(560, ax - 22, 240, 22, "#fdecec", RED, 1.2)
    s += text(680, ax - 30, "завада розмазана", 9.5, RED, "middle", "bold")
    s += rect(60, ax + 56, W - 120, 76, LGRN, GREEN, 1.3, 9)
    s += text(W / 2, ax + 80, "Виграш від розгортання (processing gain) піднімає сигнал над завадою — у стільки разів, скільки чипів.",
              11, INK, "middle", "bold")
    s += text(W / 2, ax + 102, "Саме так GPS працює, хоч його сигнал слабший за шум: код «витягує» його з-під шумового рівня.",
              10.5, INK, "middle")
    s += text(W / 2, ax + 122, "GPS: код 1.023 млн чипів/с на 50 біт/с даних → виграш ~43 дБ.", 9.5, GREY, "middle", style="italic")
    save("fig-40-5-5-despread.svg", s)


# ── Рис. 40.5.6 — три дарунки розширеного спектра ────────────────────────────
def fig56_benefits():
    W, H = 900, 320
    s = header(W, H)
    s += text(W / 2, 34, "Три дарунки розширеного спектра", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "за «зайву» смугу платять — а натомість дістають одразу три цінні властивості",
              11.5, GREY, "middle", style="italic")
    cards = [
        ("🛡️", "Стійкість до завад", "Вузька завада чи глушилка псує лише частину — решта проходить.", GREEN),
        ("🕵️", "Скритність (LPI)", "Без коду сигнал не відрізнити від шуму — важко виявити й підслухати.", BLUE),
        ("👥", "Множинний доступ", "Багато пар із різними кодами говорять в одній смузі (CDMA).", AMBER),
    ]
    x = 45
    for ico, title, body, col in cards:
        s += rect(x, 88, 270, 200, "#fbfbfb", col, 2, 12)
        s += text(x + 135, 126, ico, 24, INK, "middle")
        s += text(x + 135, 156, title, 14, col, "middle", "bold")
        words = body.split()
        ln, yy = "", 186
        for wd in words:
            if len(ln) + len(wd) > 30:
                s += text(x + 135, yy, ln.strip(), 10.5, INK, "middle")
                ln, yy = "", yy + 19
            ln += wd + " "
        s += text(x + 135, yy, ln.strip(), 10.5, INK, "middle")
        x += 290
    save("fig-40-5-6-benefits.svg", s)


# ── Рис. 40.5.7 — що вживає розширений спектр ────────────────────────────────
def fig57_real():
    W, H = 900, 320
    s = header(W, H)
    s += text(W / 2, 34, "Хто користується розширеним спектром (а ти й не знав)", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "ця «військова» ідея давно живе в кишені кожного з нас", 12, GREY, "middle", style="italic")
    cards = [
        ("Bluetooth", "FHSS", "1600 стрибків/с, 79 каналів", BLUE),
        ("Wi-Fi (b)", "DSSS", "11-чиповий код Баркера", GREEN),
        ("GPS", "DSSS", "сигнал з-під шуму", AMBER),
        ("LoRa", "CSS (чирп)", "дальність на кілометри", RED),
    ]
    x = 40
    for nm, tech, desc, col in cards:
        s += rect(x, 88, 205, 190, "#fbfbfb", col, 2, 12)
        s += text(x + 102, 126, nm, 14.5, INK, "middle", "bold")
        s += rect(x + 50, 142, 105, 32, ("#e9eefb" if col == BLUE else ("#eef6ef" if col == GREEN else (LAMB if col == AMBER else LRED))), col, 1.5, 6)
        s += text(x + 102, 164, tech, 13, col, "middle", "bold")
        words = desc.split()
        ln, yy = "", 200
        for wd in words:
            if len(ln) + len(wd) > 22:
                s += text(x + 102, yy, ln.strip(), 10, GREY, "middle")
                ln, yy = "", yy + 16
            ln += wd + " "
        s += text(x + 102, yy, ln.strip(), 10, GREY, "middle")
        x += 213
    s += text(W / 2, 300, "А винайшли стрибки частоти геть несподівані люди — про це історія до цієї теми.",
              11, INK, "middle", "bold")
    save("fig-40-5-7-real.svg", s)


# ============================================================================
#  Історія до §40.5 — Геді Ламарр (секція 0, продовження: 40.0.8+)
# ============================================================================

# ── Рис. 40.0.8 — таймлайн ───────────────────────────────────────────────────
def figh_timeline():
    W, H = 940, 640
    s = header(W, H)
    s += text(W / 2, 36, "Геді Ламарр: кінозірка, що запатентувала стрибки частоти", 19.5, INK, "middle", "bold")
    s += text(W / 2, 58, "геніальна ідея 1942 року, відкинута флотом і забута на півстоліття",
              12, GREY, "middle", style="italic")
    spine = 280
    top, bot = 92, H - 24
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("1914", "Народилася у Відні", "Гедвіґа Кіслер, з єврейської родини в Австрії", "bio"),
        ("1933", "Кіно + шлюб з Мандлем", "На ділових зустрічах чоловіка-зброяра вбирає знання про озброєння", "bio"),
        ("~1937", "Втеча до Голлівуду", "Тікає від чоловіка й нацистської Європи; стає зіркою MGM", "bio"),
        ("1940", "Зустріч з Антайлом", "З композитором-авангардистом задумує незаглушуване радіо", "win"),
        ("1942", "Патент 2 292 387", "«Secret Communication System» — стрибки по 88 частотах", "win"),
        ("1942", "Флот відкидає", "«Завелике для торпеди» — винахід кладуть під сукно", "bad"),
        ("1959", "Патент згасає", "Так і не використаний; винахідники не дістали ні цента", "bad"),
        ("1962", "Військові беруть ідею", "Схожу техніку впроваджують — уже після згасання патенту", "neut"),
        ("1997", "Нарешті визнання", "Премія EFF Pioneer повертає їй ім'я винахідниці", "win"),
        ("2014", "Зала слави (посмертно)", "Національна зала слави винахідників — справедливість запізно", "win"),
    ]
    n = len(nodes)
    for i, (yr, who, q, kind) in enumerate(nodes):
        y = top + 24 + (bot - top - 48) * i / (n - 1)
        if kind == "win":
            s += circle(spine, y, 9, "#fff", GREEN, 3)
            s += circle(spine, y, 4, GREEN, GREEN, 0)
            wc = GREEN
        elif kind == "bad":
            s += rect(spine - 8, y - 8, 16, 16, "#fff", RED, 2.6, 3)
            wc = RED
        elif kind == "bio":
            s += circle(spine, y, 7, "#fff", BLUE, 2.6)
            wc = BLUE
        else:
            s += circle(spine, y, 6, "#fff", GREY, 2.4)
            wc = GREY
        s += text(spine - 22, y + 5, yr, 12, GREY, "end", "bold")
        s += text(spine + 26, y - 2, who, 15, wc, "start", "bold")
        s += text(spine + 26, y + 17, q, 11, INK, "start", style="italic")
    save("fig-40-0-8-hl-timeline.svg", s)


# ── Рис. 40.0.9 — проблема: торпеду глушать ──────────────────────────────────
def figh_problem():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Проблема 1940 року: радіокеровану торпеду легко заглушити", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "торпеда слухає одну керівну частоту — ворог глушить саме її, і ціль утрачено",
              11.5, GREY, "middle", style="italic")
    # корабель
    s += rect(70, 140, 90, 30, LBLUE, BLUE, 1.8, 4)
    s += text(115, 130, "корабель", 10, BLUE, "middle", "bold")
    s += line(115, 140, 115, 110, METAL, 2)
    # сигнал керування
    s += sine(165, 170, 360, 14, 6, GREEN, 2)
    s += text(330, 150, "одна керівна частота", 10.5, GREEN, "middle", "bold")
    # торпеда
    s += rect(560, 158, 110, 26, LGREY, INK, 1.6, 13)
    s += circle(670, 171, 6, INK, INK, 0)
    s += text(615, 150, "торпеда", 10, INK, "middle", "bold")
    # глушилка
    s += spark(420, 230, 18, RED, 2.4)
    s += text(420, 268, "ворожа глушилка", 11, RED, "middle", "bold")
    s += arrow(420, 248, 360, 188, RED, 2)
    s += text(700, 230, "ціль", 11, RED, "start", "bold")
    s += text(700, 246, "втрачено", 10, RED, "start")
    s += rect(60, 290, W - 120, 36, LRED, RED, 1.3, 8)
    s += text(W / 2, 313, "Глуши одну частоту — і дорога зброя стає некерованою. Потрібен сигнал, який неможливо «прибити».",
              11.5, INK, "middle", "bold")
    save("fig-40-0-9-hl-problem.svg", s)


# ── Рис. 40.0.10 — ідея: стрибати по 88 частотах ─────────────────────────────
def figh_idea():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Ідея Ламарр: хай керівний сигнал СТРИБАЄ по частотах", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "корабель і торпеда міняють частоту разом, за таємним розкладом — глушилці нема за чим гнатися",
              11, GREY, "middle", style="italic")
    ox, oy = 110, 300
    cols, rows = 11, 6
    cw, rh = 62, 34
    for c in range(cols + 1):
        s += line(ox + c * cw, oy, ox + c * cw, oy - rows * rh, FAINT, 1)
    for r in range(rows + 1):
        s += line(ox, oy - r * rh, ox + cols * cw, oy - r * rh, FAINT, 1)
    s += text(ox - 16, oy - rows * rh / 2, "частота", 10.5, INK, "middle", "bold")
    s += text(ox + cols * cw / 2, oy + 24, "час →", 10.5, INK, "middle", "bold")
    hops = [2, 5, 1, 4, 0, 3, 5, 2, 4, 1, 3]
    for c, r in enumerate(hops):
        s += rect(ox + c * cw + 4, oy - (r + 1) * rh + 4, cw - 8, rh - 8, LGRN, GREEN, 1.8, 3)
        if c > 0:
            pr = hops[c - 1]
            s += line(ox + (c - 0.5) * cw, oy - (pr + 0.5) * rh, ox + (c + 0.5) * cw, oy - (r + 0.5) * rh, GREEN, 1, "3 2")
    s += text(ox + cols * cw / 2, 92, "це — те саме FHSS із §40.5, але придумане за 60 років до Bluetooth!",
              11, GREEN, "middle", "bold")
    save("fig-40-0-10-hl-idea.svg", s)


# ── Рис. 40.0.11 — синхронізація стрічкою піаноли ────────────────────────────
def figh_pianoroll():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Геніальний хід: синхронізація стрічкою від механічного піаніно", 17, INK, "middle", "bold")
    s += text(W / 2, 56, "внесок Антайла: однакові перфострічки в передавачі й приймачі задають той самий розклад стрибків",
              10.5, GREY, "middle", style="italic")
    # дві перфострічки
    def roll(y, lab, col):
        out = rect(120, y, 520, 44, "#fbf7ec", AMBER, 1.6, 4)
        holes = [0, 3, 1, 5, 2, 4, 6, 1, 7, 3, 5, 0]
        for i, h in enumerate(holes):
            cxx = 150 + i * 40
            cyy = y + 6 + h * 5
            out += circle(cxx, cyy, 3.2, "#3a3a3a", "#3a3a3a", 0)
        out += text(110, y + 26, lab, 10.5, col, "end", "bold")
        return out
    s += roll(110, "передавач", BLUE)
    s += roll(180, "приймач", GREEN)
    s += text(380, 250, "однакові дірочки → однакова послідовність частот → ідеальна синхронність",
              10.5, INK, "middle", "bold")
    # клавіатура: 88 = піаніно
    kx, ky = 300, 280
    for i in range(14):
        s += rect(kx + i * 16, ky, 16, 46, "#fff", INK, 1)
    blacks = [0, 1, 3, 4, 5, 7, 8, 10, 11, 12]
    for i in blacks:
        s += rect(kx + i * 16 + 11, ky, 10, 28, "#222", "#222", 0)
    s += text(kx + 112, ky + 66, "88 частот = 88 клавіш фортепіано", 10.5, AMBER, "middle", "bold")
    save("fig-40-0-11-hl-pianoroll.svg", s)


# ── Рис. 40.0.12 — чесно про авторство ───────────────────────────────────────
def figh_collective():
    W, H = 900, 410
    s = header(W, H)
    s += text(W / 2, 34, "Чесно: що належить їм, а що — ні (міф проти правди)", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "віддати належне забутій винахідниці — і не вдатися в протилежний міф",
              11.5, GREY, "middle", style="italic")
    rows = [
        ("Їхня справжня заслуга", GREEN,
         "Конкретна, запатентована реалізація стрибків частоти (синхронізація піанолою, 88 частот)",
         "для незаглушуваної торпеди — сміливо й на десятиліття випереджаючи час."),
        ("Чого вони НЕ робили", AMBER,
         "Стрибки частоти як ідея існували й раніше (ранні патенти, Тесла й інші).",
         "Сучасний розширений спектр інженери розвинули значною мірою НЕЗАЛЕЖНО, у 1950–60-х."),
        ("Тож міф «винайшла Wi-Fi»", RED,
         "перебільшення: прямої лінії «її патент → Wi-Fi» немає.",
         "Правда тонша й чесніша — вона видатна ПОПЕРЕДНИЦЯ, чий внесок несправедливо стерли."),
    ]
    y = 84
    for title, col, l1, l2 in rows:
        s += rect(50, y, W - 100, 98, "#fbfbfb", col, 1.8, 10)
        s += text(70, y + 28, title, 14, col, "start", "bold")
        s += text(70, y + 54, l1, 11, INK, "start")
        s += text(70, y + 76, l2, 11, INK, "start")
        y += 108
    save("fig-40-0-12-hl-collective.svg", s)


# ── Рис. 40.0.13 — забуття й визнання ────────────────────────────────────────
def figh_recognition():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Несправедливість — і запізніле визнання", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "десятиліттями її бачили «лише гарним обличчям»; винахідницю розгледіли надто пізно",
              11.5, GREY, "middle", style="italic")
    s += rect(50, 84, 390, 220, LRED, RED, 1.8, 12)
    s += text(245, 112, "Забуття", 15, RED, "middle", "bold")
    for i, ln in enumerate([
        "«Найвродливіша жінка кіно» —",
        "і нікого не цікавив її розум.",
        "Патент згас раніше, ніж техніку",
        "застосували → ні визнання, ні грошей.",
        "Десятиліття її внесок мовчазно",
        "приписували «комусь розумному».",
    ]):
        s += text(245, 142 + i * 26, ln, 10.8, INK, "middle")
    s += arrow(445, 194, 475, 194, INK, 2.2)
    s += rect(480, 84, 390, 220, LGRN, GREEN, 1.8, 12)
    s += text(675, 112, "Визнання", 15, GREEN, "middle", "bold")
    for i, ln in enumerate([
        "1997 — премія EFF Pioneer:",
        "світ нарешті назвав її винахідницею.",
        "2014 — Національна зала слави",
        "винахідників (посмертно).",
        "Сьогодні 9 листопада (її день народження)",
        "відзначають як День винахідника в Європі.",
    ]):
        s += text(675, 142 + i * 26, ln, 10.6, INK, "middle")
    save("fig-40-0-13-hl-recognition.svg", s)


# ── Рис. 40.0.14 — що з цього лишилось ───────────────────────────────────────
def figh_legacy():
    W, H = 900, 320
    s = header(W, H)
    s += text(W / 2, 34, "Що лишилось: ідея — всюди, а урок — подвійний", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "її стрибки частоти живуть у кожному радіо, а доля — застерігає від упереджень",
              11.5, GREY, "middle", style="italic")
    cards = [
        ("📡", "Ідея — у кишені", "Стрибки частоти (§40.5) — серце Bluetooth; родинні техніки — у Wi-Fi, GPS.", BLUE),
        ("⚖️", "Кредит — чесно", "Видатна попередниця, чий внесок стерли; не «винайшла все», але й не «ніщо».", AMBER),
        ("👤", "Урок — про упередження", "Талант не питає про зовнішність чи фах: винахідником буває й кінозірка.", GREEN),
    ]
    x = 45
    for ico, title, body, col in cards:
        s += rect(x, 86, 270, 200, "#fbfbfb", col, 2, 12)
        s += text(x + 135, 126, ico, 23, INK, "middle")
        s += text(x + 135, 156, title, 13.5, col, "middle", "bold")
        words = body.split()
        ln, yy = "", 186
        for wd in words:
            if len(ln) + len(wd) > 30:
                s += text(x + 135, yy, ln.strip(), 10.5, INK, "middle")
                ln, yy = "", yy + 19
            ln += wd + " "
        s += text(x + 135, yy, ln.strip(), 10.5, INK, "middle")
        x += 290
    save("fig-40-0-14-hl-legacy.svg", s)


# ============================================================================
#  §40.6 — Бюджет радіолінії (потужність, підсилення, втрати, чутливість)
# ============================================================================

# ── Рис. 40.6.1 — ланцюг бюджету ─────────────────────────────────────────────
def fig61_chain():
    W, H = 940, 340
    s = header(W, H)
    s += text(W / 2, 34, "Бюджет радіолінії: усе складаємо в децибелах", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "потужність на вході приймача = старт + усі «плюси» підсилень − усі «мінуси» втрат",
              11.5, GREY, "middle", style="italic")
    blocks = [
        ("Передавач", "P_tx", "+дБм", BLUE),
        ("Антена TX", "+G_tx", "+дБі", GREEN),
        ("Шлях у просторі", "−L_path", "−дБ", RED),
        ("Стіни, кабель", "−L_misc", "−дБ", RED),
        ("Антена RX", "+G_rx", "+дБі", GREEN),
        ("Приймач", "P_rx", "=дБм", BLUE),
    ]
    x = 36
    bw = 132
    y = 150
    for i, (nm, sym, unit, col) in enumerate(blocks):
        s += rect(x, y, bw, 80, "#fbfbfb", col, 2, 10)
        s += text(x + bw / 2, y + 28, nm, 11.5, INK, "middle", "bold")
        s += text(x + bw / 2, y + 50, sym, 13.5, col, "middle", "bold")
        s += text(x + bw / 2, y + 68, unit, 10, GREY, "middle")
        if i < len(blocks) - 1:
            s += arrow(x + bw + 2, y + 40, x + bw + 18, y + 40, INK, 2)
        x += bw + 20
    s += rect(60, 256, W - 120, 60, LBLUE, BLUE, 1.3, 9)
    s += text(W / 2, 280, "P_rx = P_tx + G_tx − L_path − L_misc + G_rx   (усе в дБ/дБм)", 14, INK, "middle", "bold")
    s += text(W / 2, 302, "Логарифм перетворює множення разів на просте додавання — ось навіщо децибели (§39.5).",
              10.5, GREY, "middle", style="italic")
    save("fig-40-6-1-chain.svg", s)


# ── Рис. 40.6.2 — складники з типовими числами ───────────────────────────────
def fig62_terms():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Складники бюджету та їхні типові значення", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "кожен доданок — окреме фізичне явище з попередніх тем, зведене в одне рівняння",
              11.5, GREY, "middle", style="italic")
    rows = [
        ("P_tx", "потужність передавача", "+4 дБм (BLE) … +20 (Wi-Fi)", BLUE),
        ("G_tx", "підсилення антени TX", "+2 дБі (штир) … +20 (тарілка)", GREEN),
        ("L_path", "втрати у просторі (§39.6)", "60 дБ на 10 м (2.4 ГГц)", RED),
        ("L_misc", "стіни, кабель, дощ, тіло", "5…30 дБ", RED),
        ("G_rx", "підсилення антени RX", "+2 дБі …", GREEN),
        ("S_rx", "чутливість приймача", "−95 дБм (BLE), −137 (LoRa)", AMBER),
    ]
    x0, y0 = 90, 86
    s += rect(x0, y0, 110, 34, "#f0f0f0", GREY, 1.3)
    s += rect(x0 + 110, y0, 320, 34, "#f0f0f0", GREY, 1.3)
    s += rect(x0 + 430, y0, 290, 34, "#f0f0f0", GREY, 1.3)
    s += text(x0 + 55, y0 + 23, "символ", 11.5, INK, "middle", "bold")
    s += text(x0 + 270, y0 + 23, "що це", 11.5, INK, "middle", "bold")
    s += text(x0 + 575, y0 + 23, "типово", 11.5, INK, "middle", "bold")
    yy = y0 + 34
    for sym, what, val, col in rows:
        s += rect(x0, yy, 110, 40, "#fff", "#e2e2e2", 1)
        s += rect(x0 + 110, yy, 320, 40, "#fff", "#e2e2e2", 1)
        s += rect(x0 + 430, yy, 290, 40, "#fff", "#e2e2e2", 1)
        s += text(x0 + 55, yy + 26, sym, 13, col, "middle", "bold")
        s += text(x0 + 124, yy + 26, what, 11, INK, "start")
        s += text(x0 + 575, yy + 26, val, 10.5, INK, "middle", "bold")
        yy += 40
    save("fig-40-6-2-terms.svg", s)


# ── Рис. 40.6.3 — EIRP: антена концентрує потужність ─────────────────────────
def fig63_eirp():
    W, H = 900, 350
    s = header(W, H)
    s += text(W / 2, 34, "EIRP: антена не додає енергії, а концентрує її", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "EIRP = P_tx + G_tx — ефективна випромінена потужність; саме її обмежує закон",
              11.5, GREY, "middle", style="italic")
    # всебічна
    s += text(230, 100, "всебічна антена (0 дБі)", 12, BLUE, "middle", "bold")
    s += circle(230, 180, 55, "none", BLUE, 2)
    for a in range(0, 360, 30):
        rad = a * math.pi / 180
        s += line(230, 180, 230 + 55 * math.cos(rad), 180 + 55 * math.sin(rad), BLUE, 0.8)
    s += text(230, 256, "енергія рівно навсібіч", 10, GREY, "middle")
    # спрямована
    s += text(670, 100, "спрямована (+12 дБі)", 12, GREEN, "middle", "bold")
    s += f'<path d="M 600,180 Q 670,110 760,180 Q 670,200 600,180 Z" fill="#eef6ef" stroke="{GREEN}" stroke-width="2"/>\n'
    s += arrow(600, 180, 770, 180, GREEN, 2.4)
    s += text(670, 256, "той самий ват — але в промінь", 10, GREEN, "middle")
    s += rect(60, 286, W - 120, 50, LAMB, AMBER, 1.4, 9)
    s += text(W / 2, 308, "Тому виграш антени (дБі) входить у бюджет як «плюс» — і для TX, і для RX.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 327, "Але EIRP обмежений регулятором (напр. +20 дБм у смузі 2.4 ГГц у ЄС) — не можна світити як завгодно гучно.",
              10, GREY, "middle", style="italic")
    save("fig-40-6-3-eirp.svg", s)


# ── Рис. 40.6.4 — водоспад бюджету (приклад BLE) ─────────────────────────────
def fig64_waterfall():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Водоспад бюджету: приклад BLE на 10 м крізь стіну", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "крокуємо від потужності передавача до входу приймача, додаючи й віднімаючи децибели",
              11, GREY, "middle", style="italic")
    ox, oy = 80, 360
    pw = 740
    pmax, pmin = 12.0, -100.0

    def Y(v):
        return oy - (v - pmin) / (pmax - pmin) * 280
    # вісь
    for v in range(0, -101, -20):
        s += line(ox - 5, Y(v), ox, Y(v), GREY, 1)
        s += text(ox - 10, Y(v) + 4, f"{v}", 9.5, GREY, "end")
    s += text(ox - 38, Y(-40), "дБм", 10, GREY, "middle", "bold")
    steps = [
        ("P_tx", 4, "+4", BLUE),
        ("+G_tx", 6, "+2", GREEN),
        ("−FSPL", -54, "−60", RED),
        ("−стіна", -64, "−10", RED),
        ("+G_rx", -62, "+2", GREEN),
    ]
    sw = pw / (len(steps) + 1)
    prev = None
    for i, (nm, lvl, delta, col) in enumerate(steps):
        x = ox + 30 + i * sw
        s += line(x, Y(lvl), x + sw * 0.7, Y(lvl), col, 3)
        s += text(x + sw * 0.35, Y(lvl) - 8, nm, 9.5, INK, "middle", "bold")
        s += text(x + sw * 0.35, Y(lvl) + 14, delta, 9, col, "middle", "bold")
        if prev is not None:
            s += line(x, Y(prev), x, Y(lvl), col, 1.6, "3 2")
        prev = lvl
    prx = -62
    s += text(ox + 30 + (len(steps) - 1) * sw + sw * 0.35, Y(prx) - 24, "P_rx=−62", 10, BLUE, "middle", "bold")
    # лінія чутливості
    srx = -95
    s += line(ox, Y(srx), ox + pw, Y(srx), AMBER, 2, "6 4")
    s += text(ox + pw, Y(srx) - 6, "чутливість S_rx = −95 дБм", 10.5, AMBER, "end", "bold")
    # запас
    xm = ox + 30 + (len(steps) - 1) * sw + sw * 0.35
    s += line(xm + 40, Y(prx), xm + 40, Y(srx), GREEN, 2)
    s += line(xm + 35, Y(prx), xm + 45, Y(prx), GREEN, 2)
    s += line(xm + 35, Y(srx), xm + 45, Y(srx), GREEN, 2)
    s += text(xm + 52, (Y(prx) + Y(srx)) / 2, "запас 33 дБ", 11, GREEN, "start", "bold")
    s += rect(60, 388, W - 120, 34, LGRN, GREEN, 1.3, 8)
    s += text(W / 2, 410, "P_rx = 4+2−60−10+2 = −62 дБм; запас = −62 − (−95) = 33 дБ → лінія працює з добрим резервом.",
              11, INK, "middle", "bold")
    save("fig-40-6-4-waterfall.svg", s)


# ── Рис. 40.6.5 — чутливість залежить від модуляції ──────────────────────────
def fig65_sensitivity():
    W, H = 900, 350
    s = header(W, H)
    s += text(W / 2, 34, "Чутливість приймача: проста модуляція чує глибше", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "що нижчий поріг S_rx (дБм), то слабший сигнал ще читається → то більша дальність",
              11, GREY, "middle", style="italic")
    items = [("256-QAM", -70, RED), ("Wi-Fi (низька)", -90, AMBER), ("BLE (GFSK)", -95, GREEN), ("LoRa (SF12)", -137, BLUE)]
    ox, oy = 120, 250
    axw = 680
    smin, smax = -140.0, -60.0

    def X(s_):
        return ox + (s_ - smin) / (smax - smin) * axw
    s += line(ox, oy, ox + axw, oy, INK, 2)
    for v in range(-140, -59, 20):
        s += line(X(v), oy, X(v), oy + 5, INK, 1)
        s += text(X(v), oy + 22, f"{v}", 10, GREY, "middle")
    s += text(ox + axw, oy + 40, "чутливість, дБм", 10, INK, "end", "bold")
    s += text(ox, oy - 150, "← чує глибше = далі", 11, GREEN, "start", "bold")
    s += text(ox + axw, oy - 150, "треба гучніше = ближче →", 11, RED, "end", "bold")
    for nm, val, col in items:
        s += _stem(X(val), oy, 120, col, 4)
        s += circle(X(val), oy - 120, 6, col, col, 0)
        s += text(X(val), oy - 132, nm, 10.5, col, "middle", "bold")
        s += text(X(val), oy - 100, f"{val}", 9.5, GREY, "middle")
    s += rect(60, 300, W - 120, 36, LBLUE, BLUE, 1.3, 8)
    s += text(W / 2, 323, "Ось чому LoRa бере на кілометри, а швидке 256-QAM — лише поблизу: різниця чутливості — десятки дБ.",
              11, INK, "middle", "bold")
    save("fig-40-6-5-sensitivity.svg", s)


# ── Рис. 40.6.6 — запас лінії та запас на завмирання ─────────────────────────
def fig66_margin():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Запас лінії: ніколи не проєктуй «упритул»", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "над чутливістю лишають резерв на завмирання, рух, дощ — інакше зв'язок «дихатиме» й рватиметься",
              10.5, GREY, "middle", style="italic")
    bx = 360
    # шкала
    s += line(bx, 90, bx, 300, INK, 2)
    levels = [("P_rx = −62 дБм", 96, GREEN, "прийнятий сигнал"),
              ("запас на завмирання", 150, AMBER, "10–20 дБ резерву (§40.7)"),
              ("S_rx = −95 дБм", 240, RED, "поріг: нижче — зв'язку нема")]
    s += rect(bx - 10, 96, 20, 144, "#eef6ef", GREEN, 1.4)
    s += rect(bx - 10, 240, 20, 0, "none", "none", 0)
    for lab, y, col, desc in levels:
        s += line(bx - 16, y, bx + 16, y, col, 2.5)
        s += text(bx - 26, y + 4, lab, 11, col, "end", "bold")
        s += text(bx + 26, y + 4, desc, 10, GREY, "start")
    # дужка повного запасу
    s += line(bx + 150, 96, bx + 150, 240, BLUE, 1.8)
    s += line(bx + 145, 96, bx + 155, 96, BLUE, 1.8)
    s += line(bx + 145, 240, bx + 155, 240, BLUE, 1.8)
    s += text(bx + 160, 168, "повний запас 33 дБ", 10.5, BLUE, "start", "bold")
    s += rect(60, 308, W - 120, 26, LGRN, GREEN, 1.2, 7)
    s += text(W / 2, 326, "Правило: тримай 10–20 дБ «зверху» на завмирання. Запас 0 дБ = зв'язок, що рветься від кожної хмари.",
              10.5, INK, "middle", "bold")
    save("fig-40-6-6-margin.svg", s)


# ── Рис. 40.6.7 — три реальні бюджети ────────────────────────────────────────
def fig67_examples():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 34, "Три лінії — три бюджети: чому в кожної своя дальність", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "та сама арифметика дБ пояснює, чому BLE — кімната, Wi-Fi — будинок, LoRa — місто",
              11, GREY, "middle", style="italic")
    cols = [
        ("BLE у кімнаті", ["P_tx = +4 дБм", "втрати ~66 дБ", "S_rx = −95 дБм", "запас ~33 дБ"], "≈ 10–30 м", GREEN),
        ("Wi-Fi у домі", ["P_tx = +18 дБм", "втрати ~88 дБ", "S_rx = −90 дБм", "запас ~20 дБ"], "≈ 30–50 м", BLUE),
        ("LoRa по місту", ["P_tx = +14 дБм", "втрати ~115 дБ", "S_rx = −137 дБм", "запас ~38 дБ"], "≈ кілька км", AMBER),
    ]
    x = 50
    for title, lines, rng, col in cols:
        s += rect(x, 86, 280, 240, "#fbfbfb", col, 2, 12)
        s += text(x + 140, 116, title, 14.5, col, "middle", "bold")
        yy = 150
        for ln in lines:
            s += text(x + 24, yy, ln, 11.5, INK, "start")
            yy += 30
        s += line(x + 20, 268, x + 260, 268, FAINT, 1.2)
        s += text(x + 140, 292, "дальність:", 10.5, GREY, "middle")
        s += text(x + 140, 312, rng, 14, col, "middle", "bold")
        x += 295
    save("fig-40-6-7-examples.svg", s)


# ============================================================================
#  §40.7 — Багатопроменевість і завмирання
# ============================================================================

# ── Рис. 40.7.1 — хвиля приходить багатьма шляхами ───────────────────────────
def fig71_multipath():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Багатопроменевість: хвиля доходить не одним шляхом", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "пряма хвиля плюс відбиття від стін, землі, будівель — у приймач приходить кілька копій",
              11, GREY, "middle", style="italic")
    # передавач і приймач
    s += line(120, 300, 120, 200, METAL, 3)
    s += line(112, 192, 128, 192, METAL, 3)
    s += text(120, 320, "TX", 12, BLUE, "middle", "bold")
    s += line(780, 300, 780, 200, METAL, 3)
    s += line(772, 192, 788, 192, METAL, 3)
    s += text(780, 320, "RX", 12, GREEN, "middle", "bold")
    # пряма
    s += arrow(135, 196, 765, 196, GREEN, 2.4)
    s += text(450, 186, "пряма (найкоротша)", 10.5, GREEN, "middle", "bold")
    # відбиття від стелі
    s += line(135, 188, 450, 100, RED, 1.8)
    s += line(450, 100, 765, 188, RED, 1.8)
    s += text(450, 92, "відбиття від стелі", 10, RED, "middle", "bold")
    # відбиття від підлоги
    s += line(135, 208, 450, 300, AMBER, 1.8)
    s += line(450, 300, 765, 208, AMBER, 1.8)
    s += text(450, 318, "відбиття від підлоги/землі", 10, AMBER, "middle", "bold")
    # стеля й підлога
    s += line(60, 86, 840, 86, FAINT, 3)
    s += line(60, 310, 840, 310, FAINT, 3)
    s += rect(60, 340, W - 120, 30, LBLUE, BLUE, 1.3, 8)
    s += text(W / 2, 360, "Копії проходять різну відстань → приходять із різною затримкою й фазою. Що з ними буде далі — головне питання.",
              10.5, INK, "middle", "bold")
    save("fig-40-7-1-multipath.svg", s)


# ── Рис. 40.7.2 — копії складаються за фазою ──────────────────────────────────
def fig72_addition():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Копії складаються — і тут вирішує фаза", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "у фазі — підсилення (до +6 дБ); у протифазі — взаємне знищення (глибокий провал)",
              11.5, GREY, "middle", style="italic")
    # у фазі
    s += text(40, 100, "У ФАЗІ:", 12, GREEN, "start", "bold")
    s += sine(150, 120, 280, 18, 3, BLUE, 1.8)
    s += sine(150, 120, 280, 18, 3, RED, 1.8)
    s += arrow(440, 120, 480, 120, INK, 2)
    s += text(460, 108, "=", 13, INK, "middle", "bold")
    s += sine(500, 120, 280, 34, 3, GREEN, 2.6)
    s += text(640, 86, "сильний сигнал (×2)", 10.5, GREEN, "middle", "bold")
    # у протифазі
    s += text(40, 250, "У ПРОТИФАЗІ:", 12, RED, "start", "bold")
    s += sine(150, 280, 280, 18, 3, BLUE, 1.8)
    s += sine(150, 280, 280, 18, 3, RED, 1.8, phase=math.pi)
    s += arrow(440, 280, 480, 280, INK, 2)
    s += text(460, 268, "=", 13, INK, "middle", "bold")
    s += line(500, 280, 780, 280, GREEN, 2.6)
    s += text(640, 250, "майже нуль — «провал»", 10.5, RED, "middle", "bold")
    s += rect(60, 350, W - 120, 36, LGREY, GREY, 1.3, 8)
    s += text(W / 2, 373, "Зсув лише на пів довжини хвилі обертає підсилення на знищення. На 2.4 ГГц це лише ~6 см!",
              11.5, INK, "middle", "bold")
    save("fig-40-7-2-addition.svg", s)


# ── Рис. 40.7.3 — карта завмирань у просторі ─────────────────────────────────
def fig73_fading_map():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Завмирання у просторі: піки й «мертві зони» поряд", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "сила сигналу то злітає, то провалюється що кілька сантиметрів — варто лише трохи зрушити",
              11, GREY, "middle", style="italic")
    ox, oy = 80, 250
    axw = 740
    s += arrow(ox, oy, ox + axw, oy, INK, 2)
    s += arrow(ox, oy, ox, oy - 170, INK, 2)
    s += text(ox + axw, oy + 22, "положення (см)", 10, INK, "end", "bold")
    s += text(ox - 16, oy - 165, "сила", 10, INK, "middle", "bold")
    # завмираюча крива: сума інтерференцій
    pts = []
    for i in range(301):
        t = i / 300
        x = ox + t * axw
        env = abs(math.cos(2 * math.pi * 3.2 * t) * 0.7 + 0.3 * math.cos(2 * math.pi * 5.1 * t + 1))
        y = oy - 30 - env * 120
        pts.append((x, y))
    s += _poly(pts, BLUE, 2.4)
    # позначки піка й нуля
    s += circle(ox + 0.156 * axw, oy - 30 - 0.97 * 120, 5, GREEN, GREEN, 0)
    s += text(ox + 0.156 * axw, oy - 175, "пік", 10, GREEN, "middle", "bold")
    s += circle(ox + 0.235 * axw, oy - 30 - 0.05 * 120, 5, RED, RED, 0)
    s += text(ox + 0.30 * axw, oy - 40, "«мертва зона»", 10, RED, "middle", "bold")
    s += line(ox + 0.156 * axw, oy + 6, ox + 0.235 * axw, oy + 6, AMBER, 2)
    s += text(ox + 0.19 * axw, oy + 22, "~6 см", 9.5, AMBER, "middle", "bold")
    s += rect(60, 300, W - 120, 36, LBLUE, BLUE, 1.3, 8)
    s += text(W / 2, 323, "Ось чому, посунувши телефон на долоню чи інакше взявши його, ти раптом ловиш сигнал.",
              11.5, INK, "middle", "bold")
    save("fig-40-7-3-fading-map.svg", s)


# ── Рис. 40.7.4 — завмирання в часі ──────────────────────────────────────────
def fig74_fading_time():
    W, H = 900, 350
    s = header(W, H)
    s += text(W / 2, 34, "Завмирання в часі: сигнал «дихає» — ось навіщо запас", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "коли все довкола рухається, копії то збігаються, то гасять одна одну — рівень стрибає",
              11, GREY, "middle", style="italic")
    ox, oy = 80, 250
    axw = 740
    s += arrow(ox, oy, ox + axw, oy, INK, 2)
    s += arrow(ox, oy, ox, oy - 170, INK, 2)
    s += text(ox + axw, oy + 22, "час", 10, INK, "end", "bold")
    s += text(ox - 16, oy - 165, "P_rx", 10, INK, "middle", "bold")
    # середній рівень
    mean_y = oy - 110
    s += line(ox, mean_y, ox + axw, mean_y, GREY, 1.2, "5 4")
    s += text(ox + axw, mean_y - 6, "середній P_rx", 9.5, GREY, "end")
    # поріг
    thr_y = oy - 40
    s += line(ox, thr_y, ox + axw, thr_y, RED, 1.8, "6 4")
    s += text(ox + axw, thr_y + 16, "поріг чутливості", 9.5, RED, "end", "bold")
    # завмираючий сигнал
    pts = []
    for i in range(361):
        t = i / 360
        x = ox + t * axw
        v = (math.sin(t * 21) * 0.5 + math.sin(t * 37 + 1) * 0.3 + math.sin(t * 67 + 2) * 0.2)
        # випадкові глибокі провали
        dip = -0.8 if (0.34 < t < 0.37 or 0.71 < t < 0.735) else 0
        y = mean_y - (v + dip) * 60
        pts.append((x, y))
    s += _poly(pts, BLUE, 2)
    s += circle(ox + 0.355 * axw, thr_y + 6, 6, "none", RED, 2)
    s += text(ox + 0.355 * axw, oy - 6, "обрив!", 9.5, RED, "middle", "bold")
    s += rect(60, 300, W - 120, 36, LGRN, GREEN, 1.3, 8)
    s += text(W / 2, 323, "Глибокий провал на мить кидає сигнал під поріг → пакет утрачено. Запас 10–20 дБ (§40.6) рятує від цього.",
              10.5, INK, "middle", "bold")
    save("fig-40-7-4-fading-time.svg", s)


# ── Рис. 40.7.5 — міжсимвольна інтерференція ─────────────────────────────────
def fig75_isi():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Луна розмиває символи: міжсимвольна інтерференція (ISI)", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "затримані копії «наповзають» на наступні символи — на високій швидкості це плутає біти",
              11, GREY, "middle", style="italic")
    # прямий потік символів
    syms = [1, -1, 1, 1, -1]
    s += text(40, 108, "пряма:", 11, GREEN, "start", "bold")
    s += sq_wave(150, 130, 600, 26, syms, GREEN, 2.4)
    # затримана луна (зсунута)
    s += text(40, 198, "луна (затримка):", 11, RED, "start", "bold")
    s += sq_wave(174, 220, 600, 20, syms, RED, 1.8)
    # сума — розмита
    s += text(40, 290, "що чує приймач:", 11, INK, "start", "bold")
    pts = []
    seg = 600 / len(syms)
    for i in range(241):
        t = i / 240
        x = 150 + t * 600
        # груба «розмита» суміш
        idx = min(len(syms) - 1, int(t * len(syms)))
        idx2 = min(len(syms) - 1, int((t * 600 - 24) / seg)) if (t * 600 - 24) >= 0 else 0
        v = 0.6 * syms[idx] + 0.4 * syms[idx2]
        y = 312 - v * 22
        pts.append((x, y))
    s += _poly(pts, INK, 2)
    s += text(450, 344, "що швидші символи, то сильніше луна накладається → затримка (delay spread) обмежує швидкість",
              10, GREY, "middle", style="italic")
    save("fig-40-7-5-isi.svg", s)


# ── Рис. 40.7.6 — засоби проти завмирань ─────────────────────────────────────
def fig76_remedies():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Арсенал проти завмирань", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "інженер не бореться з фізикою, а пристосовується — кількома взаємодоповняльними прийомами",
              11.5, GREY, "middle", style="italic")
    cards = [
        ("Рознесені антени", "Дві антени за кілька см: одна в «провалі» — друга ні (просторове рознесення).", GREEN),
        ("OFDM", "Багато вузьких піднесучих: кожна завмирає рівно, її легко вирівняти. Wi-Fi, LTE.", BLUE),
        ("Розширений спектр", "Стрибки/коди (§40.5): не всі частоти завмирають разом.", AMBER),
        ("Код + повтор", "Завадостійке кодування й перевідправлення (§35, §38) латають провали.", RED),
    ]
    x, y = 50, 88
    for i, (title, body, col) in enumerate(cards):
        cx = x + (i % 2) * 410
        cy = y + (i // 2) * 130
        s += rect(cx, cy, 390, 116, "#fbfbfb", col, 2, 12)
        s += text(cx + 16, cy + 30, title, 13.5, col, "start", "bold")
        words = body.split()
        ln, yy = "", cy + 56
        for wd in words:
            if len(ln) + len(wd) > 46:
                s += text(cx + 16, yy, ln.strip(), 10.8, INK, "start")
                ln, yy = "", yy + 19
            ln += wd + " "
        s += text(cx + 16, yy, ln.strip(), 10.8, INK, "start")
    save("fig-40-7-6-remedies.svg", s)


# ── Рис. 40.7.7 — MIMO: ворог стає другом ────────────────────────────────────
def fig77_mimo():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Несподіваний фінал: MIMO робить багатопроменевість другом", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "те, що псувало зв'язок, сучасні системи обертають на ДОДАТКОВУ ємність",
              11.5, GREY, "middle", style="italic")
    # дві антени TX, дві RX, перехресні шляхи
    for i, yy in enumerate([150, 230]):
        s += line(180, yy, 200, yy - 20, BLUE, 3)
        s += circle(180, yy, 5, BLUE, BLUE, 0)
        s += text(150, yy + 4, f"TX{i+1}", 10, BLUE, "middle", "bold")
        s += line(720, yy, 740, yy - 20, GREEN, 3)
        s += circle(720, yy, 5, GREEN, GREEN, 0)
        s += text(760, yy + 4, f"RX{i+1}", 10, GREEN, "middle", "bold")
    paths = [(150, 150, GREEN), (150, 230, AMBER), (230, 150, AMBER), (230, 230, GREEN)]
    for ty, ry, col in paths:
        s += line(190, ty, 710, ry, col, 1, "4 3")
    s += text(450, 130, "кілька незалежних шляхів", 10.5, INK, "middle", "bold")
    s += text(450, 270, "= кілька паралельних потоків даних", 11, GREEN, "middle", "bold")
    s += rect(60, 300, W - 120, 50, LGRN, GREEN, 1.4, 9)
    s += text(W / 2, 322, "MIMO (multiple-in, multiple-out): різні відбиття дають різні «канали» → в кілька разів більше даних.",
              11, INK, "middle", "bold")
    s += text(W / 2, 341, "Так Wi-Fi і 5G перетворили колишнього ворога на джерело швидкості. Антени — у Розділі 41.",
              10, GREY, "middle", style="italic")
    save("fig-40-7-7-mimo.svg", s)


if __name__ == "__main__":
    # — історія (секція 0) —
    fig_timeline()
    fig_three_gifts()
    fig_am_noise()
    fig_wideband()
    fig_band_move()
    fig_collective()
    fig_vindication()
    # — §40.1 —
    fig11_antenna()
    fig12_sharing()
    fig13_carrier()
    fig14_three_knobs()
    fig15_chain()
    fig16_spectrum()
    fig17_why()
    # — §40.2 —
    fig21_am_build()
    fig22_am_index()
    fig23_am_sidebands()
    fig24_fm_build()
    fig25_noise()
    fig26_fm_bandwidth()
    fig27_tradeoff()
    # — §40.3 —
    fig31_keyings()
    fig32_symbols()
    fig33_constellation()
    fig34_noise()
    fig35_baud()
    fig36_tradeoff()
    fig37_real()
    # — §40.4 —
    fig41_formula()
    fig42_two_levers()
    fig43_curve()
    fig44_wall()
    fig45_modem()
    fig46_connects()
    fig47_shannon()
    # — §40.5 —
    fig51_spread_idea()
    fig52_fhss()
    fig53_fhss_jam()
    fig54_dsss()
    fig55_despread()
    fig56_benefits()
    fig57_real()
    # — історія до §40.5 (Геді Ламарр) —
    figh_timeline()
    figh_problem()
    figh_idea()
    figh_pianoroll()
    figh_collective()
    figh_recognition()
    figh_legacy()
    # — §40.6 —
    fig61_chain()
    fig62_terms()
    fig63_eirp()
    fig64_waterfall()
    fig65_sensitivity()
    fig66_margin()
    fig67_examples()
    # — §40.7 —
    fig71_multipath()
    fig72_addition()
    fig73_fading_map()
    fig74_fading_time()
    fig75_isi()
    fig76_remedies()
    fig77_mimo()
    print("done.")
