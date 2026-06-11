# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 10.5 — «Сонячна енергія і MPPT» (Модуль 10).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи: «Рис. 10.5.T.k»;
для історії до розділу — тема 0 (Рис. 10.5.0.k). Хелпери — копія з §10.4.

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


def _sun(cx, cy, r, c=AMBER):
    out = circle(cx, cy, r, "#fdf3d0", c, 2)
    for i in range(8):
        import math
        a = i * math.pi / 4
        out += line(cx + r * 1.2 * math.cos(a), cy + r * 1.2 * math.sin(a),
                    cx + r * 1.7 * math.cos(a), cy + r * 1.7 * math.sin(a), c, 2)
    return out


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── Рис. 10.5.0.1 — таймлайн фотоелектрики ───────────────────────────────────
def fig_timeline():
    W, H = 940, 700
    s = header(W, H)
    s += text(W / 2, 40, "Сонячний елемент: довга колективна історія", 20, INK, "middle", "bold")
    s += text(W / 2, 62, "ефект, прилад, теорія й практичний кремній — це різні люди, країни й століття",
              12.5, GREY, "middle", style="italic")
    spine = 250
    top, bot = 96, H - 70
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("1839", "Едмон Беккерель (Франція)", "відкрив фотовольтаїчний ефект: світло на електроді народжує струм", INK, False),
        ("1883", "Чарлз Фріттс (США)", "перший твердотільний фотоелемент (селен) — лише ~1% ККД, для живлення замало", INK, False),
        ("1905", "Альберт Айнштайн (Німеччина)", "пояснив фотоефект квантом світла — теоретичний фундамент усієї фотоелектрики", INK, False),
        ("1954", "Bell Labs (США): Чапін · Фуллер · Пірсон", "кремнієвий елемент ~6% — перший ПРАКТИЧНИЙ; інженер + хімік + фізик разом", GREEN, True),
        ("1958", "Vanguard I (США)", "перший супутник на сонячному живленні: сонячний передавач прожив 6+ років", BLUE, True),
    ]
    n = len(nodes)
    for i, (yr, who, what, c, hot) in enumerate(nodes):
        y = top + 28 + (bot - top - 56) * i / (n - 1)
        if hot:
            s += circle(spine, y, 10, "#fff", c, 3.2)
            s += circle(spine, y, 4.5, c, c, 0)
        else:
            s += circle(spine, y, 7, "#fff", c, 2.4)
        s += text(spine - 22, y + 5, yr, 13, GREY, "end", "bold")
        s += text(spine + 24, y - 4, who, 14, c, "start", "bold")
        s += text(spine + 24, y + 16, what, 11.5, INK, "start")
    s += text(W / 2, H - 30, "Жодного «винахідника сонячної батареї»: ефект — Беккереля, перший прилад — Фріттса, теорія — Айнштайна,",
              12, INK, "middle")
    s += text(W / 2, H - 12, "а практичний кремнієвий елемент — спільна робота ТРЬОХ людей у Bell Labs, що стала на плечі всіх попередників.",
              12, GREEN, "middle", style="italic")
    save("fig-10-0-1-timeline.svg", s)


# ── Рис. 10.5.0.2 — троє в Bell Labs ─────────────────────────────────────────
def fig_team():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 32, "Кремнієвий елемент 1954: троє ролей — один винахід", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "приклад того, що складна техніка майже завжди народжується командою, а не «генієм-одинаком»",
              12, GREY, "middle", style="italic")
    cards = [
        ("Дерил Чапін", "інженер", "ШУКАВ ЖИВЛЕННЯ для телефонії", "в глухих вологих місцях, де", "сідали сухі батареї → сонце", BLUE, 50),
        ("Келвін Фуллер", "хімік", "ЛЕГУВАВ КРЕМНІЙ", "дифузією — зробив сам p-n", "перехід, «серце» елемента", GREEN, 360),
        ("Джеральд Пірсон", "фізик", "ФІЗИКА Й ВИМІРИ", "переходу, без яких годі було", "довести й виміряти ефект", AMBER, 670),
    ]
    for name, role, l1, l2, l3, c, x in cards:
        s += rect(x, 80, 220, 200, "#ffffff", c, 2, 12)
        s += text(x + 110, 108, name, 13, c, "middle", "bold")
        s += text(x + 110, 127, role, 10, GREY, "middle", style="italic")
        s += line(x + 20, 138, x + 200, 138, FAINT, 1)
        s += text(x + 110, 164, l1, 9.5, INK, "middle", "bold")
        s += text(x + 110, 186, l2, 9, INK, "middle")
        s += text(x + 110, 202, l3, 9, INK, "middle")
        s += arrow(x + 110, 280, 470, 320, GREY, 1.6)
    s += rect(330, 320, 280, 50, "#eef8ef", GREEN, 2, 12)
    s += text(470, 342, "кремнієвий сонячний елемент", 12, GREEN, "middle", "bold")
    s += text(470, 360, "~6% ККД — перший практичний (1954)", 9.5, INK, "middle")
    save("fig-10-0-2-team.svg", s)


# ── Рис. 10.5.0.3 — Vanguard I: батарея проти сонця ──────────────────────────
def fig_vanguard():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Vanguard I (1958): чому сонце змінило космос", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "перший супутник із сонячними елементами — і наочний урок про джерела живлення", 12, GREY, "middle", style="italic")
    s += _sun(120, 150, 26)
    # battery transmitter
    s += rect(330, 90, 540, 110, "#fbe9e7", RED, 1.8, 12)
    s += text(360, 116, "Батарейний передавач", 12, RED, "start", "bold")
    s += text(360, 140, "ртутна батарея → замовк за ДНІ (тижні)", 11, INK, "start")
    s += text(360, 164, "запас енергії скінченний — місія коротка", 10, GREY, "start")
    s += text(360, 184, "✗ так живили перші супутники", 10, RED, "start", "bold")
    # solar transmitter
    s += rect(330, 220, 540, 120, "#eef8ef", GREEN, 1.8, 12)
    s += text(360, 246, "Сонячний передавач", 12, GREEN, "start", "bold")
    s += text(360, 270, "6 кремнієвих елементів → працював 6+ РОКІВ", 11, INK, "start")
    s += text(360, 294, "сонце поповнює енергію — місія довга", 10, GREY, "start")
    s += text(360, 314, "✓ відтоді сонце — штатне джерело супутників", 10, GREEN, "start", "bold")
    s += arrow(150, 150, 326, 130, AMBER, 1.6)
    s += arrow(150, 160, 326, 270, AMBER, 1.6)
    s += rect(70, H - 40, W - 140, 28, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 22, "Vanguard I був 4-м супутником (після двох «Супутників» і Explorer 1), але ПЕРШИМ на сонячному живленні. Він і досі —", 10, INK, "middle")
    s += text(W / 2, H - 8, "найстаріший рукотворний об'єкт на орбіті. Урок простий: батарея дає днів, сонце — роки; це й вирішило долю космічної енергетики.", 10, INK, "middle")
    save("fig-10-0-3-vanguard.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 10.5.1 — Фотоелемент: p-n перехід назустріч світлу
# ════════════════════════════════════════════════════════════════════════════

def _minus(cx, cy, r=9, c=BLUE):
    return circle(cx, cy, r, "#fff", c, 2) + line(cx - r * 0.5, cy, cx + r * 0.5, cy, c, 2.4)


# ── Рис. 10.5.1.1 — згадка про p-n перехід ───────────────────────────────────
def fig_junction_recap():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 32, "Той самий p-n перехід — згадка з §2.5", 18, INK, "middle", "bold")
    s += rect(80, 90, 300, 180, "#fbe9e7", RED, 1.8, 8)
    s += text(230, 114, "p-область", 12, RED, "middle", "bold")
    s += text(230, 132, "надлишок дірок (+)", 9.5, INK, "middle")
    for x, y in [(140, 175), (200, 205), (290, 165), (330, 215), (170, 240), (300, 240)]:
        s += plus(x, y, 8, RED)
    s += rect(520, 90, 300, 180, "#eef3fb", BLUE, 1.8, 8)
    s += text(670, 114, "n-область", 12, BLUE, "middle", "bold")
    s += text(670, 132, "надлишок електронів (−)", 9.5, INK, "middle")
    for x, y in [(580, 175), (640, 205), (720, 165), (770, 215), (610, 240), (740, 240)]:
        s += _minus(x, y, 8)
    s += rect(380, 90, 140, 180, "#f6f6f6", GREY, 1.4, 0)
    s += text(450, 116, "збіднена зона", 9, GREY, "middle", "bold")
    s += arrow(490, 180, 410, 180, INK, 2.4)
    s += text(450, 168, "вбудоване поле E", 8.3, INK, "middle", "bold")
    s += text(450, 208, "(штовхає заряди)", 8, GREY, "middle")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 26, "Звичайний діод (§2.5): на межі p та n виникає збіднена зона з вбудованим електричним полем. Це поле — ключ до всього.", 9.5, INK, "middle")
    s += text(W / 2, H - 11, "Як діод ми пускали ним струм в один бік. Тепер обернемо його НАЗУСТРІЧ СВІТЛУ — і він стане генератором.", 9.5, INK, "middle")
    save("fig-10-1-1-junction.svg", s)


# ── Рис. 10.5.1.2 — фотон вибиває пару ───────────────────────────────────────
def fig_photon_to_pair():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 32, "Фотон вибиває пару: електрон + дірка", 18, INK, "middle", "bold")
    s += _sun(110, 110, 24)
    s += text(210, 116, "фотон", 10, AMBER, "middle", "bold")
    s += arrow(150, 130, 360, 205, AMBER, 2.4)
    s += rect(360, 150, 420, 170, "#f3f6f3", GREEN, 1.4, 8)
    s += text(560, 172, "кремній", 10, GREEN, "middle", "bold")
    s += circle(470, 235, 14, "#fff", INK, 1.8)
    s += text(470, 239, "Si", 9, INK, "middle")
    s += _minus(565, 215, 10)
    s += text(565, 196, "електрон (−)", 8.5, BLUE, "middle", "bold")
    s += arrow(492, 230, 550, 218, BLUE, 1.8)
    s += plus(470, 280, 10, RED)
    s += text(470, 302, "дірка (+)", 8.5, RED, "middle", "bold")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 26, "Квант світла з достатньою енергією, влучивши в кремній, вибиває електрон зі зв'язку — народжується ПАРА: вільний електрон (−)", 9.3, INK, "middle")
    s += text(W / 2, H - 11, "і порожнє місце, дірка (+). Сама собою ця пара ще нічого не дає: електрон і дірка поряд і легко знову з'єднаються. Їх треба РОЗВЕСТИ.", 9.3, INK, "middle")
    save("fig-10-1-2-photon.svg", s)


# ── Рис. 10.5.1.3 — поле розводить пару (ядро) ───────────────────────────────
def fig_field_separates():
    W, H = 940, 410
    s = header(W, H)
    s += text(W / 2, 32, "Поле переходу розводить пару — і тече струм", 18, INK, "middle", "bold")
    s += rect(120, 90, 240, 150, "#fbe9e7", RED, 1.8, 8)
    s += text(240, 114, "p", 13, RED, "middle", "bold")
    s += rect(480, 90, 240, 150, "#eef3fb", BLUE, 1.8, 8)
    s += text(600, 114, "n", 13, BLUE, "middle", "bold")
    s += rect(360, 90, 120, 150, "#f6f6f6", GREY, 1.2, 0)
    s += arrow(460, 160, 380, 160, INK, 2)
    s += text(420, 148, "поле E", 8, INK, "middle", "bold")
    s += _sun(60, 70, 18)
    s += arrow(90, 85, 408, 145, AMBER, 2)
    s += plus(330, 178, 9, RED)
    s += _minus(450, 178, 9)
    s += arrow(330, 198, 250, 218, RED, 1.8)
    s += text(275, 234, "дірка → у p", 8, RED, "middle", "bold")
    s += arrow(450, 198, 600, 218, BLUE, 1.8)
    s += text(565, 234, "електрон → у n", 8, BLUE, "middle", "bold")
    s += line(240, 240, 240, 305, INK, 2)
    s += line(240, 305, 600, 305, INK, 2)
    s += line(600, 305, 600, 240, INK, 2)
    s += rect(380, 290, 80, 30, "#eef8ef", GREEN, 1.8, 6)
    s += text(420, 309, "навантаж.", 8, GREEN, "middle", "bold")
    s += arrow(330, 305, 288, 305, GREEN, 2.2)
    s += text(310, 296, "струм I", 8.5, GREEN, "middle", "bold")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 26, "Якщо пара народилася біля переходу, вбудоване поле РОЗВОДИТЬ її: дірку штовхає в p, електрон — у n. Накопичені заряди дають напругу,", 9.2, INK, "middle")
    s += text(W / 2, H - 11, "а під'єднане навантаження — шлях, і тече струм. Ось і вся суть: світло → пари → поле розводить → струм. Це фотоелемент.", 9.2, INK, "middle")
    save("fig-10-1-3-separate.svg", s)


# ── Рис. 10.5.1.4 — заборонена зона й спектр ─────────────────────────────────
def fig_bandgap():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Чому навіть ідеальний елемент не на 100%: заборонена зона", 16.5, INK, "middle", "bold")
    s += line(120, 240, 820, 240, INK, 1.6)
    s += text(124, 258, "поріг поглинання (заборонена зона Si ≈ 1.1 еВ)", 9, INK, "start", "bold")
    cases = [
        ("ІЧ: мало енергії", BLUE, 230, 0),
        ("якраз над порогом", GREEN, 470, 1),
        ("синій / УФ: забагато", RED, 710, 2),
    ]
    for title, c, x, k in cases:
        s += text(x, 100, title, 9.5, c, "middle", "bold")
        s += circle(x, 134, 16, "#fff", c, 2.2)
        s += text(x, 138, "hν", 9, c, "middle", "bold")
        if k == 0:
            s += arrow(x, 152, x, 300, c, 1.8, dash="4,3")
            s += text(x, 318, "наскрізь, не вловлено", 8, c, "middle")
        elif k == 1:
            s += arrow(x, 152, x, 236, c, 2.2)
            s += text(x, 300, "✓ уся — у струм", 8.5, c, "middle", "bold")
        else:
            s += arrow(x, 152, x, 236, c, 2.2)
            s += text(x, 300, "частина → струм,", 8, INK, "middle")
            s += text(x, 314, "надлишок → тепло", 8, c, "middle", "bold")
    s += rect(70, H - 58, W - 140, 46, "#fbf7ec", AMBER, 1.4, 9)
    s += text(W / 2, H - 40, "Кремній бере лише фотони ПОНАД свій поріг (~1.1 еВ). Менш енергійні (інфрачервоні) проходять наскрізь намарно, а в надто", 9.2, INK, "middle")
    s += text(W / 2, H - 25, "енергійних (синіх, УФ) надлишок енергії губиться теплом. Через цю невідповідність спектру навіть ідеальний кремній перетворює", 9.2, INK, "middle")
    s += text(W / 2, H - 10, "лише частину сонця — звідси і скромні ~6% піонерів, і «стеля» сучасних елементів далеко не в 100%.", 9.2, INK, "middle")
    save("fig-10-1-4-bandgap.svg", s)


# ── Рис. 10.5.1.5 — модель: джерело струму ───────────────────────────────────
def fig_cell_model():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 32, "Освітлений елемент — це джерело струму", 18, INK, "middle", "bold")
    s += circle(250, 180, 34, "#fff", GREEN, 2)
    s += arrow(250, 206, 250, 154, GREEN, 2.2)
    s += text(250, 244, "джерело струму", 9.5, GREEN, "middle", "bold")
    s += text(250, 260, "Iсв ∝ світло", 9, INK, "middle")
    s += line(250, 146, 250, 110, INK, 2)
    s += line(250, 110, 420, 110, INK, 2)
    s += line(420, 110, 420, 250, INK, 2)
    s += line(250, 214, 250, 250, INK, 2)
    s += line(250, 250, 420, 250, INK, 2)
    s += poly([(408, 165), (432, 165), (420, 186), (408, 165)], INK, 2)
    s += line(408, 186, 432, 186, INK, 2)
    s += text(448, 182, "діод (сам перехід)", 9, INK, "start")
    s += line(420, 110, 520, 110, RED, 2)
    s += circle(520, 110, 4, RED, RED, 0)
    s += text(530, 106, "+", 13, RED, "start", "bold")
    s += line(420, 250, 520, 250, BLUE, 2)
    s += circle(520, 250, 4, BLUE, BLUE, 0)
    s += text(530, 255, "−", 13, BLUE, "start", "bold")
    s += text(560, 178, "≈ 0.5–0.6 В", 13, INK, "start", "bold")
    s += text(560, 198, "на елемент", 9, GREY, "start")
    s += text(560, 220, "(майже без огляду на розмір!)", 8.3, GREY, "start")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 26, "Модель: джерело струму (тим більше, чим яскравіше світло й більша площа) паралельно з діодом (самим переходом).", 9.2, INK, "middle")
    s += text(W / 2, H - 11, "Напруга одного кремнієвого елемента ~0.5–0.6 В і майже не залежить від розміру — її задає хімія переходу. Площа задає СТРУМ.", 9.2, INK, "middle")
    save("fig-10-1-5-model.svg", s)


# ── Рис. 10.5.1.6 — будова й послідовне з'єднання ────────────────────────────
def fig_cell_construction():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Будова елемента й послідовне з'єднання", 18, INK, "middle", "bold")
    s += text(250, 70, "Розріз елемента", 11, INK, "middle", "bold")
    x0, w = 80, 330
    s += _sun(x0 + 40, 50, 13)
    s += f'<rect x="{x0}" y="88" width="{w}" height="14" fill="#3a6bd6"/>\n'
    s += text(x0 + w + 8, 99, "антивідблиск (синій)", 8.3, INK, "start")
    s += f'<rect x="{x0}" y="102" width="{w}" height="22" fill="#dfeefb" stroke="{BLUE}" stroke-width="1"/>\n'
    s += text(x0 + w + 8, 116, "n-шар (тонкий, до світла)", 8.3, INK, "start")
    s += line(x0, 124, x0 + w, 124, INK, 1.6, dash="4,3")
    s += text(x0 + w + 8, 128, "p-n перехід", 8.3, INK, "start")
    s += f'<rect x="{x0}" y="124" width="{w}" height="60" fill="#fbe9e7" stroke="{RED}" stroke-width="1"/>\n'
    s += text(x0 + w + 8, 158, "p-шар (товстий)", 8.3, INK, "start")
    s += f'<rect x="{x0}" y="184" width="{w}" height="14" fill="#bbbbbb"/>\n'
    s += text(x0 + w + 8, 195, "задній контакт", 8.3, INK, "start")
    for fx in range(x0 + 26, x0 + w - 10, 48):
        s += rect(fx, 84, 5, 20, "#999999", "#777", 0.5, 1)
    s += text(x0 + w / 2, 78, "пальці сітки (тонкі, щоб не затуляти)", 7.3, GREY, "middle")
    s += text(740, 70, "Послідовно — на напругу", 11, INK, "middle", "bold")
    cx = 595
    for i in range(6):
        x = cx + i * 48
        s += rect(x, 110, 38, 70, "#eef8ef", GREEN, 1.4, 4)
        s += text(x + 19, 150, "0.5В", 7.3, GREEN, "middle", "bold")
        if i < 5:
            s += line(x + 38, 145, x + 48, 145, INK, 1.4)
    s += text(740, 204, "6 × 0.5 В ≈ 3 В", 11, INK, "middle", "bold")
    s += text(740, 222, "(струм — як в однієї)", 8.5, GREY, "middle")
    s += rect(70, H - 58, W - 140, 46, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 40, "Фізично елемент — тонка кремнієва пластина: зверху тонкий n-шар «до світла» й сітка контактів (тонка, щоб менше затуляти),", 9, INK, "middle")
    s += text(W / 2, H - 25, "знизу товстий p-шар і суцільний контакт, а синій антивідблисковий шар не дає світлу відбитися. Один елемент дає ~0.5 В,", 9, INK, "middle")
    s += text(W / 2, H - 10, "тож для потрібної напруги їх з'єднують ПОСЛІДОВНО (як комірки батареї, тема 10.4.1): десяток — і вже ~5 В, аби заряджати літій.", 9, INK, "middle")
    save("fig-10-1-6-construction.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 10.5.2 — ВАХ панелі
# ════════════════════════════════════════════════════════════════════════════

_IV = [(0, 0.50), (1.5, 0.498), (3, 0.49), (4, 0.48), (4.8, 0.45),
       (5.3, 0.38), (5.7, 0.22), (5.9, 0.08), (6, 0)]


# ── Рис. 10.5.2.1 — ВАХ ──────────────────────────────────────────────────────
def fig_iv_curve():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "ВАХ панелі: струм проти напруги", 18, INK, "middle", "bold")
    x0, y0, pw, ph, Voc, Isc = 110, 340, 680, 270, 6.0, 0.5
    s += line(x0, y0, x0 + pw, y0, INK, 1.6)
    s += line(x0, y0, x0, y0 - ph, INK, 1.6)
    s += text(x0 + pw, y0 + 20, "напруга V →", 9.5, INK, "end")
    s += text(x0 - 9, y0 - ph - 2, "струм I", 9.5, INK, "end", "bold")

    def px(v):
        return x0 + v / Voc * pw

    def py(i):
        return y0 - i / (Isc * 1.1) * ph

    s += poly([(px(v), py(i)) for v, i in _IV], GREEN, 3)
    s += circle(px(0), py(0.5), 5, RED, RED, 0)
    s += text(px(0) - 8, py(0.5) - 6, "Isc (КЗ)", 9.5, RED, "end", "bold")
    s += text(px(0) - 8, py(0.5) + 9, "макс. струм", 8, GREY, "end")
    s += circle(px(6), py(0), 5, BLUE, BLUE, 0)
    s += text(px(6) + 8, py(0) - 6, "Voc (ХХ)", 9.5, BLUE, "start", "bold")
    s += text(px(6) + 8, py(0) + 9, "макс. напруга", 8, GREY, "start")
    s += text(px(4.9) + 12, py(0.45) - 6, "«коліно»", 9, INK, "start", "bold")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 26, "Закоротили виходи (V=0) — тече весь фотострум Isc (∝ світло). Розімкнули (I=0) — на клемах повна напруга Voc (~0.5 В × N елементів).", 9, INK, "middle")
    s += text(W / 2, H - 11, "Між ними — характерна крива з «коліном»: майже сталий струм, тоді різке падіння напруги. Уся практика панелі — про цю криву.", 9, INK, "middle")
    save("fig-10-2-1-iv.svg", s)


# ── Рис. 10.5.2.2 — горб потужності ──────────────────────────────────────────
def fig_power_hump():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 32, "Потужність P = V·I: чому є «горб»", 18, INK, "middle", "bold")
    x0, y0, pw, ph, Voc, Isc = 110, 340, 700, 270, 6.0, 0.5
    s += line(x0, y0, x0 + pw, y0, INK, 1.6)
    s += line(x0, y0, x0, y0 - ph, INK, 1.6)
    s += line(x0 + pw, y0, x0 + pw, y0 - ph, GREY, 1.2)
    s += text(x0 + pw / 2, y0 + 20, "напруга V →", 9.5, INK, "middle")
    s += text(x0 - 9, y0 - ph - 2, "струм I", 9, GREEN, "end", "bold")
    s += text(x0 + pw + 9, y0 - ph - 2, "потужність P", 9, AMBER, "start", "bold")

    def px(v):
        return x0 + v / Voc * pw

    def py(i):
        return y0 - i / (Isc * 1.1) * ph

    s += poly([(px(v), py(i)) for v, i in _IV], GREEN, 2.6)
    s += text(px(1.6), py(0.50) - 8, "ВАХ (струм)", 9, GREEN, "start", "bold")
    Pmax = 4.8 * 0.45

    def pyP(p):
        return y0 - p / (Pmax * 1.15) * ph

    s += poly([(px(v), pyP(v * i)) for v, i in _IV], AMBER, 2.8)
    s += circle(px(4.8), pyP(Pmax), 6, RED, RED, 0)
    s += text(px(4.8), pyP(Pmax) - 10, "MPP (макс. P)", 9.5, RED, "middle", "bold")
    s += line(px(4.8), pyP(Pmax), px(4.8), y0, RED, 1, dash="4,3")
    s += text(px(4.8), y0 + 18, "Vmp", 8.5, RED, "middle", "bold")
    s += text(px(0) + 6, y0 - 10, "V=0 → P=0", 8, GREY, "start")
    s += text(px(6) - 6, y0 - 10, "I=0 → P=0", 8, GREY, "end")
    s += rect(70, H - 44, W - 140, 32, "#fbf7ec", AMBER, 1.4, 9)
    s += text(W / 2, H - 26, "Потужність — це ДОБУТОК V·I. На краях вона нульова: при КЗ нема напруги, при ХХ нема струму. Тож десь усередині, біля «коліна»,", 9, INK, "middle")
    s += text(W / 2, H - 11, "P сягає МАКСИМУМУ — це й є точка максимальної потужності (MPP). Саме на ній варто тримати панель, щоб узяти від неї найбільше.", 9, INK, "middle")
    save("fig-10-2-2-power.svg", s)


# ── Рис. 10.5.2.3 — MPP і fill factor ────────────────────────────────────────
def fig_mpp_fill():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "MPP, Vmp, Imp і «квадратність» (fill factor)", 17, INK, "middle", "bold")
    x0, y0, pw, ph, Voc, Isc = 110, 340, 680, 270, 6.0, 0.5
    s += line(x0, y0, x0 + pw, y0, INK, 1.6)
    s += line(x0, y0, x0, y0 - ph, INK, 1.6)
    s += text(x0 + pw, y0 + 20, "V →", 9.5, INK, "end")
    s += text(x0 - 9, y0 - ph - 2, "I", 9.5, INK, "end", "bold")

    def px(v):
        return x0 + v / Voc * pw

    def py(i):
        return y0 - i / (Isc * 1.1) * ph

    s += rect(px(0), py(0.5), px(6) - px(0), py(0) - py(0.5), "none", GREY, 1.2)
    s += text(px(6) - 6, py(0.5) - 6, "Voc × Isc (ідеал)", 8.5, GREY, "end")
    s += f'<rect x="{px(0):.0f}" y="{py(0.45):.0f}" width="{px(4.8)-px(0):.0f}" height="{py(0)-py(0.45):.0f}" fill="#caa24a" fill-opacity="0.18" stroke="{AMBER}" stroke-width="1.6"/>\n'
    s += poly([(px(v), py(i)) for v, i in _IV], GREEN, 3)
    s += circle(px(4.8), py(0.45), 6, RED, RED, 0)
    s += text(px(4.8) + 8, py(0.45) - 6, "MPP", 10, RED, "start", "bold")
    s += line(px(4.8), py(0.45), px(4.8), y0, RED, 1, dash="3,3")
    s += text(px(4.8), y0 + 18, "Vmp", 8.5, RED, "middle", "bold")
    s += line(px(0), py(0.45), px(4.8), py(0.45), RED, 1, dash="3,3")
    s += text(px(0) - 9, py(0.45) + 4, "Imp", 8.5, RED, "end", "bold")
    s += text(px(2.3), py(0.22), "Vmp × Imp = реальна P", 9, AMBER, "middle", "bold")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 26, "MPP лежить трохи нижче Voc і трохи нижче Isc — у точці (Vmp, Imp). Її прямокутник Vmp×Imp і є реальна максимальна потужність.", 9, INK, "middle")
    s += text(W / 2, H - 11, "Наскільки він заповнює ідеальний Voc×Isc — це «коефіцієнт заповнення» (fill factor): що крива «квадратніша», то він ближчий до 1.", 9, INK, "middle")
    save("fig-10-2-3-mpp.svg", s)


# ── Рис. 10.5.2.4 — навантажувальні прямі ────────────────────────────────────
def fig_load_line():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 32, "Навантаження вирішує, де на кривій ти сидиш", 18, INK, "middle", "bold")
    x0, y0, pw, ph, Voc, Isc = 110, 340, 700, 270, 6.0, 0.5
    s += line(x0, y0, x0 + pw, y0, INK, 1.6)
    s += line(x0, y0, x0, y0 - ph, INK, 1.6)
    s += text(x0 + pw, y0 + 20, "V →", 9.5, INK, "end")
    s += text(x0 - 9, y0 - ph - 2, "I", 9.5, INK, "end", "bold")

    def px(v):
        return x0 + v / Voc * pw

    def py(i):
        return y0 - i / (Isc * 1.1) * ph

    s += poly([(px(v), py(i)) for v, i in _IV], GREEN, 3)
    s += text(px(1.6), py(0.50) - 8, "ВАХ панелі", 9, GREEN, "start", "bold")
    s += circle(px(4.8), py(0.45), 5, RED, RED, 0)
    s += text(px(4.8) + 8, py(0.45) - 8, "MPP (ціль)", 9, RED, "start", "bold")
    s += line(px(3.7), y0, px(3.7), y0 - ph, BLUE, 2, dash="5,4")
    s += text(px(3.7), y0 - ph - 2, "батарея 3.7 В", 8.5, BLUE, "middle", "bold")
    s += circle(px(3.7), py(0.485), 5, BLUE, BLUE, 0)
    s += text(px(3.7) - 8, py(0.485) + 16, "робоча точка", 8, BLUE, "end")
    s += line(px(0), py(0), px(5.0), py(0.42), AMBER, 2, dash="4,3")
    s += text(px(5.0) + 4, py(0.42), "резистор (V=IR)", 8.5, AMBER, "start", "bold")
    s += rect(70, H - 58, W - 140, 46, "#fbf7ec", AMBER, 1.4, 9)
    s += text(W / 2, H - 40, "Панель — джерело, а навантаження накладає свою умову: резистор — пряма крізь нуль (V=IR), батарея — майже вертикаль на своїй напрузі.", 9, INK, "middle")
    s += text(W / 2, H - 25, "Робоча точка — там, де ця умова перетинає ВАХ. Якщо батарея 3.7 В, панель ЗМУШЕНА сидіти на 3.7 В — ЛІВІШЕ за MPP (4.8 В),", 9, INK, "middle")
    s += text(W / 2, H - 10, "а отже, віддає менше, ніж могла б. Прибрати цей розрив — і є задача MPPT (теми 10.5.4–5).", 9, GREEN, "middle", "bold")
    save("fig-10-2-4-loadline.svg", s)


# ── Рис. 10.5.2.5 — зсув кривої ──────────────────────────────────────────────
def fig_shift():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 32, "Світло й тепло зсувають криву — MPP «гуляє»", 18, INK, "middle", "bold")
    x0, y0, pw, ph, Voc, Isc = 110, 330, 700, 260, 6.0, 0.5
    s += line(x0, y0, x0 + pw, y0, INK, 1.6)
    s += line(x0, y0, x0, y0 - ph, INK, 1.6)
    s += text(x0 + pw, y0 + 20, "V →", 9.5, INK, "end")
    s += text(x0 - 9, y0 - ph - 2, "I", 9.5, INK, "end", "bold")

    def px(v):
        return x0 + v / Voc * pw

    def py(i):
        return y0 - i / (Isc * 1.15) * ph

    def curve(isc, voc, c, w=2.6, dash=None):
        sv, si = voc / 6.0, isc / 0.5
        return poly([(px(v * sv), py(i * si)) for v, i in _IV], c, w, dash)

    s += curve(0.5, 6.0, GREEN, 3)
    s += text(px(2.5), py(0.50) - 6, "норма", 8.5, GREEN, "start", "bold")
    s += curve(0.32, 6.0, BLUE, 2.2, dash="5,4")
    s += text(px(2.5), py(0.32) - 6, "менше світла (Isc↓)", 8, BLUE, "start", "bold")
    s += curve(0.5, 5.0, RED, 2.2, dash="5,4")
    s += text(px(4.4), py(0.14), "гаряче (Voc↓)", 8, RED, "start", "bold")
    s += circle(px(4.8), py(0.45), 4, GREEN, GREEN, 0)
    s += circle(px(4.8), py(0.288), 4, BLUE, BLUE, 0)
    s += circle(px(4.0), py(0.45), 4, RED, RED, 0)
    s += text(px(4.8), py(0.45) - 12, "MPP гуляє", 8, INK, "middle", "bold")
    s += rect(70, H - 58, W - 140, 46, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 40, "Більше світла піднімає Isc (крива вгору), менше — опускає. Нагрів знижує Voc (крива вліво). Тож точка MPP не стоїть на місці —", 9, INK, "middle")
    s += text(W / 2, H - 25, "вона рухається з хмарами, сонцем і температурою. Саме тому MPP не можна виставити РАЗ — за нею треба СТЕЖИТИ (MPPT), про що далі.", 9, INK, "middle")
    s += text(W / 2, H - 10, "Дрібний виняток: Voc слабко росте з яскравістю (логарифмічно), тож світло б'є переважно по струму, а тепло — по напрузі.", 8.5, GREY, "middle")
    save("fig-10-2-5-shift.svg", s)


# ── Рис. 10.5.2.6 — послідовно/паралельно ────────────────────────────────────
def fig_series_parallel():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 32, "З елементів у панель: послідовно й паралельно", 18, INK, "middle", "bold")
    x0, y0, pw, ph, Vmax, Imax = 110, 330, 700, 260, 3.0, 1.1
    s += line(x0, y0, x0 + pw, y0, INK, 1.6)
    s += line(x0, y0, x0, y0 - ph, INK, 1.6)
    s += text(x0 + pw, y0 + 20, "V →", 9.5, INK, "end")
    s += text(x0 - 9, y0 - ph - 2, "I", 9.5, INK, "end", "bold")

    def px(v):
        return x0 + v / Vmax * pw

    def py(i):
        return y0 - i / Imax * ph

    base = [(0, 1.0), (0.3, 0.99), (0.4, 0.97), (0.46, 0.9), (0.5, 0.6), (0.53, 0.2), (0.55, 0)]

    def curve(voc, isc, c, w=2.6, dash=None):
        sv, si = voc / 0.55, isc / 1.0
        return poly([(px(v * sv), py(i * si)) for v, i in base], c, w, dash)

    s += curve(0.55, 0.5, GREEN, 2.6)
    s += text(px(0.58), py(0.27), "1 елемент", 8.5, GREEN, "start", "bold")
    s += curve(2.2, 0.5, BLUE, 2.6, dash="5,4")
    s += text(px(2.1), py(0.27), "4 послідовно (V×4)", 8.5, BLUE, "start", "bold")
    s += arrow(px(0.65), py(0.5), px(2.0), py(0.5), BLUE, 1.6)
    s += text(px(1.3), py(0.5) - 8, "послідовно → V росте", 8, BLUE, "middle")
    s += curve(0.55, 1.0, RED, 2.6, dash="5,4")
    s += text(px(0.6), py(1.0) - 6, "2 паралельно (I×2)", 8.5, RED, "start", "bold")
    s += arrow(px(0.32), py(0.55), px(0.32), py(0.95), RED, 1.6)
    s += text(px(0.5), py(0.78), "паралельно → I", 8, RED, "start")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 26, "Послідовно елементи додають НАПРУГУ (Voc і Vmp множаться на N), струм лишається як в одного. Паралельно — навпаки:", 9, INK, "middle")
    s += text(W / 2, H - 11, "додають СТРУМ (Isc, Imp ×N), напруга та сама. Крива панелі — це крива елемента, розтягнута по осях. Так із ~0.5 В будують панель.", 9, INK, "middle")
    save("fig-10-2-6-array.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 10.5.3 — Реальне сонце: кут, температура, затінення
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 10.5.3.1 — три злодії ───────────────────────────────────────────────
def fig_real_vs_ideal():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Реальне сонце: три злодії крадуть «паспортну» потужність", 16.5, INK, "middle", "bold")
    s += rect(50, 150, 130, 80, "#eef8ef", GREEN, 2, 10)
    s += text(115, 182, "паспортна", 10, GREEN, "middle", "bold")
    s += text(115, 200, "Pmax (STC)", 9, INK, "middle")
    thieves = [
        ("Кут", "cos θ: косе сонце —|менше світла", BLUE, 280),
        ("Тепло", "гаряча панель —|нижча напруга", RED, 500),
        ("Тінь", "затінена комірка|душить весь ряд", AMBER, 720),
    ]
    s += arrow(180, 190, 250, 190, GREY, 1.8)
    for title, body, c, x in thieves:
        s += rect(x, 150, 170, 80, "#ffffff", c, 1.8, 10)
        s += text(x + 85, 174, title, 11, c, "middle", "bold")
        for j, ln in enumerate(body.split("|")):
            s += text(x + 85, 194 + j * 15, ln, 8.5, INK, "middle")
        if x > 280:
            s += arrow(x - 32, 190, x - 2, 190, GREY, 1.8)
    s += rect(70, H - 44, W - 140, 32, "#fbf7ec", AMBER, 1.4, 9)
    s += text(W / 2, H - 26, "Цифра «5 Вт» на панелі — за ідеального сонця (STC). У полі від неї відкушують одразу троє: кут падіння, нагрів і, найзубастіший,", 9, INK, "middle")
    s += text(W / 2, H - 11, "затінення. Тому реально розраховувати треба не на паспорт, а на те, що лишиться після всіх трьох. Розгляньмо кожного.", 9, INK, "middle")
    save("fig-10-3-1-real.svg", s)


# ── Рис. 10.5.3.2 — кут (cos θ) ──────────────────────────────────────────────
def fig_angle():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Кут падіння: світло йде як cos θ", 18, INK, "middle", "bold")
    s += line(110, 250, 330, 250, INK, 3)
    s += text(220, 268, "панель", 9, INK, "middle")
    s += line(220, 250, 220, 130, GREY, 1.4, dash="4,3")
    s += text(226, 138, "нормаль", 8, GREY, "start")
    s += arrow(220, 120, 220, 235, GREEN, 2.2)
    s += text(238, 130, "0°  ×1.0", 9, GREEN, "start", "bold")
    s += arrow(120, 130, 208, 238, AMBER, 2)
    s += text(108, 126, "30°  ×0.87", 8.5, AMBER, "end", "bold")
    s += arrow(70, 205, 200, 244, RED, 2)
    s += text(60, 200, "60°  ×0.5", 8.5, RED, "end", "bold")
    s += _sun(150, 95, 13)
    s += rect(560, 90, 330, 200, "#f6f6f6", GREY, 1.4, 10)
    s += text(725, 116, "Чому cos θ", 11, INK, "middle", "bold")
    for i, t in enumerate(["та сама «жменя» променів, падаючи", "косо, розмазується по БІЛЬШІЙ площі →", "на одиницю площі світла менше"]):
        s += text(578, 142 + i * 16, t, 9, INK, "start")
    s += text(578, 208, "0° — у лоб: повне", 9, GREEN, "start", "bold")
    s += text(578, 228, "60° — удвічі менше (cos 60° = 0.5)", 9, RED, "start", "bold")
    s += text(578, 252, "а сонце ходить небом цілий день,", 8.5, GREY, "start")
    s += text(578, 268, "тож нерухома панель майже завжди коса", 8.5, GREY, "start")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 26, "Панель ловить світло пропорційно КОСИНУСУ кута між сонцем і її нормаллю: у лоб — повне, під 60° — лише половина. А сонце", 9, INK, "middle")
    s += text(W / 2, H - 11, "повзе небом, тож нерухома панель майже весь день «коса». Звідси — чому орієнтація й нахил важать, а ранок із вечором дають мало.", 9, INK, "middle")
    save("fig-10-3-2-angle.svg", s)


# ── Рис. 10.5.3.3 — температура ──────────────────────────────────────────────
def fig_temperature():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Нагрів: яскраве сонце водночас і шкодить", 18, INK, "middle", "bold")
    x0, y0, pw, ph = 110, 300, 360, 200
    s += line(x0, y0, x0 + pw, y0, INK, 1.5)
    s += line(x0, y0, x0, y0 - ph, INK, 1.5)
    s += text(x0 + pw / 2, y0 + 20, "температура →", 9, INK, "middle")
    s += text(x0 - 9, y0 - ph - 2, "Voc, P", 9, INK, "end", "bold")
    s += poly([(x0, y0 - 0.9 * ph), (x0 + pw, y0 - 0.55 * ph)], RED, 2.8)
    s += text(x0 + pw * 0.42, y0 - 0.62 * ph, "напруга й P падають", 9, RED, "start", "bold")
    for t, lab in [(0, "+25°"), (0.5, "+45°"), (1, "+65°")]:
        xx = x0 + t * pw
        s += line(xx, y0, xx, y0 + 5, INK, 1)
        s += text(xx, y0 + 18, lab, 8.5, GREY, "middle")
    s += rect(520, 100, 380, 200, "#fbe9e7", RED, 1.6, 10)
    s += text(710, 126, "Прикрий парадокс", 11, RED, "middle", "bold")
    for i, t in enumerate(["яскравіше сонце → більше струму (добре),", "але воно ж ГРІЄ панель → менше напруги", "(погано) → частина виграшу з'їдається", "", "на сонці панель буває на +25…35 °C", "гарячіша за повітря; чорна й нерухома", "в застої — особливо"]):
        if t:
            s += text(538, 152 + i * 19, t, 9, INK, "start")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 26, "З теми 10.5.2 ми знаємо: нагрів знижує Voc (~0.3%/°C), а з ним і потужність. Іронія в тому, що саме яскраве сонце, дане", 9, INK, "middle")
    s += text(W / 2, H - 11, "для струму, заодно РОЗІГРІВАЄ панель і відбирає напругу. Тому панелям дають дихати: провітрювання й зазор за ними рятують відсотки.", 9, INK, "middle")
    save("fig-10-3-3-temp.svg", s)


# ── Рис. 10.5.3.4 — затінення душить ряд (ядро) ──────────────────────────────
def fig_shading_string():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 32, "Тінь: одна комірка душить увесь ряд", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "у послідовному ряду струм СПІЛЬНИЙ (тема 10.5.2) — тож тече стільки, скільки пропустить найслабша", 11, GREY, "middle", style="italic")
    n, x0, cw, y = 6, 120, 110, 110
    for i in range(n):
        x = x0 + i * cw
        shaded = (i == 3)
        c = GREY if shaded else GREEN
        fill = "#dddddd" if shaded else "#eef8ef"
        s += rect(x, y, 80, 60, fill, c, 1.8, 6)
        s += text(x + 40, y + 30, "тінь" if shaded else "сонце", 8.5, c, "middle", "bold")
        s += text(x + 40, y + 46, "0.1 А" if shaded else "0.5 А", 8.5, INK, "middle")
        if i < n - 1:
            s += line(x + 80, y + 30, x + cw, y + 30, INK, 2)
    s += text(W / 2, y + 96, "↓ струм ряду = найменший = 0.1 А (а не 0.5)", 11, RED, "middle", "bold")
    s += rect(150, 244, 300, 110, "#eef8ef", GREEN, 1.6, 10)
    s += text(300, 268, "Усе на сонці", 11, GREEN, "middle", "bold")
    s += text(300, 292, "6 × 0.5 В × 0.5 А", 10, INK, "middle")
    s += text(300, 316, "≈ 1.5 Вт", 14, GREEN, "middle", "bold")
    s += rect(500, 244, 300, 110, "#fbe9e7", RED, 1.6, 10)
    s += text(650, 268, "Одна комірка в тіні", 11, RED, "middle", "bold")
    s += text(650, 292, "увесь ряд душиться до 0.1 А", 10, INK, "middle")
    s += text(650, 316, "≈ 0.3 Вт  (−80%!)", 14, RED, "middle", "bold")
    s += rect(70, H - 44, W - 140, 32, "#fbe9e7", RED, 1.4, 9)
    s += text(W / 2, H - 26, "Затінити одну комірку з шести — це НЕ «мінус шоста». Бо ряд послідовний: спільний струм падає до того, що пропускає затінена,", 9, INK, "middle")
    s += text(W / 2, H - 11, "і ВЕСЬ ряд віддає крихти. «Половина тіні — не половина потужності»: мала тінь коштує величезної частки врожаю.", 9, INK, "middle")
    save("fig-10-3-4-shading.svg", s)


# ── Рис. 10.5.3.5 — bypass-діод ──────────────────────────────────────────────
def fig_bypass_diode():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Bypass-діод: шлях струму ПОВЗ затінену комірку", 17.5, INK, "middle", "bold")
    n, x0, cw, y = 4, 150, 150, 120
    s += arrow(x0 - 36, y + 28, x0 - 6, y + 28, RED, 2.4)
    s += text(x0 - 44, y + 22, "I", 9, RED, "end", "bold")
    for i in range(n):
        x = x0 + i * cw
        shaded = (i == 2)
        c = GREY if shaded else GREEN
        fill = "#dddddd" if shaded else "#eef8ef"
        s += rect(x, y, 80, 56, fill, c, 1.8, 6)
        s += text(x + 40, y + 27, "тінь" if shaded else "сонце", 8.3, c, "middle", "bold")
        s += text(x + 40, y + 44, "комірка", 8, INK, "middle")
        s += line(x, y + 56, x, y + 90, INK, 1.4)
        s += line(x + 80, y + 56, x + 80, y + 90, INK, 1.4)
        s += line(x, y + 90, x + 80, y + 90, INK, 1.4)
        dc = GREEN if shaded else GREY
        s += poly([(x + 50, y + 82), (x + 50, y + 98), (x + 30, y + 90), (x + 50, y + 82)], dc, 1.8)
        s += line(x + 30, y + 82, x + 30, y + 98, dc, 1.8)
        if shaded:
            s += text(x + 40, y + 118, "↑ ВІДКРИВСЯ:", 8, GREEN, "middle", "bold")
            s += text(x + 40, y + 132, "струм в обхід", 8, GREEN, "middle")
        if i < n - 1:
            s += line(x + 80, y + 28, x + cw, y + 28, INK, 2)
    s += rect(70, H - 58, W - 140, 46, "#eef8ef", GREEN, 1.4, 9)
    s += text(W / 2, H - 40, "Поруч із групою комірок ставлять діод. Поки комірка освітлена — діод закритий, не заважає. Затінилася — на ній", 9, INK, "middle")
    s += text(W / 2, H - 25, "з'являється зворотна напруга, діод ВІДКРИВАЄТЬСЯ й пускає струм в обхід неї. Ряд тече далі (мінус ця група), а не глухне зовсім —", 9, INK, "middle")
    s += text(W / 2, H - 10, "і заразом зникає «гаряча пляма»: затінена комірка більше не палиться чужим струмом. Тому реальні панелі мають bypass-діоди.", 9, INK, "middle")
    save("fig-10-3-5-bypass.svg", s)


# ── Рис. 10.5.3.6 — кілька горбів ────────────────────────────────────────────
def fig_multipeak():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Часткова тінь робить КІЛЬКА горбів на кривій P-V", 17, INK, "middle", "bold")
    x0, y0, pw, ph = 110, 310, 720, 250
    s += line(x0, y0, x0 + pw, y0, INK, 1.6)
    s += line(x0, y0, x0, y0 - ph, INK, 1.6)
    s += text(x0 + pw, y0 + 20, "напруга V →", 9.5, INK, "end")
    s += text(x0 - 9, y0 - ph - 2, "потужність P", 9.5, INK, "end", "bold")
    pts1 = [(0, 0), (0.2, 0.4), (0.45, 0.85), (0.6, 1.0), (0.75, 0.85), (0.9, 0.4), (1.0, 0)]
    s += poly([(x0 + v * pw, y0 - p * ph) for v, p in pts1], GREEN, 2.2, dash="5,4")
    s += text(x0 + 0.6 * pw, y0 - 1.0 * ph - 4, "без тіні: один горб", 8.5, GREEN, "middle", "bold")
    pts2 = [(0, 0), (0.15, 0.45), (0.28, 0.55), (0.4, 0.4), (0.5, 0.45), (0.65, 0.72), (0.78, 0.6), (0.9, 0.25), (1.0, 0)]
    s += poly([(x0 + v * pw, y0 - p * ph) for v, p in pts2], RED, 2.8)
    s += circle(x0 + 0.28 * pw, y0 - 0.55 * ph, 5, AMBER, AMBER, 0)
    s += text(x0 + 0.28 * pw, y0 - 0.55 * ph - 8, "локальний", 8, AMBER, "middle", "bold")
    s += circle(x0 + 0.65 * pw, y0 - 0.72 * ph, 5, RED, RED, 0)
    s += text(x0 + 0.65 * pw, y0 - 0.72 * ph - 8, "ГЛОБАЛЬНИЙ (справжній)", 8, RED, "middle", "bold")
    s += text(x0 + 0.08 * pw, y0 - 0.28 * ph, "часткова тінь:", 8.5, RED, "start", "bold")
    s += rect(70, H - 44, W - 140, 32, "#fbf7ec", AMBER, 1.4, 9)
    s += text(W / 2, H - 26, "Коли частина панелі в тіні, bypass-діоди роблять криву P-V «горбатою» — з кількома піками. Простий алгоритм MPPT легко", 9, INK, "middle")
    s += text(W / 2, H - 11, "«застрягає» на ЛОКАЛЬНОМУ горбі, проґавивши вищий глобальний. Як цьому раду дають — у темі про алгоритми MPPT (10.5.5).", 9, INK, "middle")
    save("fig-10-3-6-multipeak.svg", s)


if __name__ == "__main__":
    fig_timeline()
    fig_team()
    fig_vanguard()
    # тема 10.5.1
    fig_junction_recap()
    fig_photon_to_pair()
    fig_field_separates()
    fig_bandgap()
    fig_cell_model()
    fig_cell_construction()
    # тема 10.5.2
    fig_iv_curve()
    fig_power_hump()
    fig_mpp_fill()
    fig_load_line()
    fig_shift()
    fig_series_parallel()
    # тема 10.5.3
    fig_real_vs_ideal()
    fig_angle()
    fig_temperature()
    fig_shading_string()
    fig_bypass_diode()
    fig_multipeak()
    print("done r05 figures")
