# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 24 — «Таймери й керування часом» (Модуль 4).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи нумеруються посекційно
(Рис. C.S.N) у тексті розділу; історія розділу → C.0.N.

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


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ═════════════════════════════════════════════════════════════════════════════
# Історія розділу (📜) — fig-24-0-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 24.0.1 — що таке хороший «тік» ──────────────────────────────────────
def fig01_what_is_tick():
    W, H = 940, 410
    s = header(W, H)
    s += text(W / 2, 32, "Щоб міряти час, потрібен рівний «тік»", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "годинник — це лічильник однакових поштовхів; що їх більше за секунду й що вони стабільніші, то точніший час", 10.5, GREY, "middle", style="italic")
    # pendulum
    s += rect(60, 90, 380, 250, "none", FAINT, 1.6, 12)
    s += text(250, 116, "Маятник (~1927 і давніше)", 12, INK, "middle", "bold")
    s += line(250, 140, 250, 140, INK, 2)
    s += line(250, 140, 210, 230, INK, 2)
    s += circle(206, 240, 14, LBLUE, BLUE, 2)
    s += line(250, 140, 290, 230, GREY, 1.4, dash="3,3")
    s += circle(294, 240, 14, "none", GREY, 1.4)
    s += text(250, 290, "≈ 1 тік на секунду", 11, BLUE, "middle", "bold")
    s += text(250, 312, "залежить від тяжіння, тепла, руху", 9, GREY, "middle")
    # quartz
    s += rect(500, 90, 380, 250, "none", FAINT, 1.6, 12)
    s += text(690, 116, "Кварц (від 1927)", 12, INK, "middle", "bold")
    sq = [(560, 230), (590, 200), (620, 230), (650, 200), (680, 230), (710, 200), (740, 230), (770, 200), (800, 230)]
    s += poly(sq, GREEN, 2.4)
    s += text(690, 290, "тисячі-мільйони тіків на секунду", 11, GREEN, "middle", "bold")
    s += text(690, 312, "майже не «пливе» — дуже стабільний", 9, GREY, "middle")
    s += text(W / 2, 372, "Хороший тік = частий + стабільний. Уся історія точного часу — пошук кращого тіку.", 10.5, INK, "middle", "bold")
    s += text(W / 2, 394, "Кварц виявився надзвичайно хорошим — і досі тікає в кожному чипі.", 9.7, GREY, "middle")
    save("fig-24-0-1-what-is-tick.svg", s)


# ── Рис. 24.0.2 — п'єзоефект ─────────────────────────────────────────────────
def fig02_piezo():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "П'єзоефект: кварц перетворює тиск і струм одне в одне", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "відкрили брати Кюрі (Жак і П'єр), 1880 — і це працює в ОБИДВА боки", 11, GREY, "middle", style="italic")
    # direct: squeeze -> voltage
    s += rect(60, 90, 380, 240, "none", FAINT, 1.6, 12)
    s += text(250, 116, "Стиснути → з'являється напруга", 11.5, BLUE, "middle", "bold")
    s += arrow(170, 175, 210, 175, INK, 2.4)
    s += arrow(330, 175, 290, 175, INK, 2.4)
    s += rect(212, 150, 76, 60, "#eef3ff", BLUE, 1.8, 6)
    s += text(250, 185, "кварц", 10, INK, "middle", "bold")
    s += line(250, 210, 250, 250, INK, 2)
    s += text(150, 178, "тиск", 9, INK, "end")
    s += text(350, 178, "тиск", 9, INK, "start")
    s += rect(210, 250, 80, 34, LRED, RED, 1.6, 6)
    s += text(250, 272, "+ напруга −", 10, RED, "middle", "bold")
    s += text(250, 308, "(прямий п'єзоефект)", 9, GREY, "middle")
    # inverse: voltage -> deform
    s += rect(500, 90, 380, 240, "none", FAINT, 1.6, 12)
    s += text(690, 116, "Подати напругу → кварц деформується", 11, GREEN, "middle", "bold")
    s += rect(652, 150, 76, 60, "#eef6ef", GREEN, 1.8, 6)
    s += text(690, 185, "кварц", 10, INK, "middle", "bold")
    s += line(690, 150, 690, 120, INK, 2)
    s += rect(650, 90, 80, 30, LGRN, GREEN, 1.6, 6)
    s += text(690, 110, "+ напруга −", 9.5, GREEN, "middle", "bold")
    s += arrow(620, 230, 640, 200, RED, 2)
    s += arrow(760, 230, 740, 200, RED, 2)
    s += text(690, 252, "кристал злегка стискається/тягнеться", 8.7, INK, "middle")
    s += text(690, 308, "(зворотний п'єзоефект)", 9, GREY, "middle")
    s += text(W / 2, 360, "Саме зворотний ефект і дозволяє «розгойдати» кварц електрикою — змусити його вібрувати.", 10.3, INK, "middle", "bold")
    save("fig-24-0-2-piezo.svg", s)


# ── Рис. 24.0.3 — кварцовий генератор ────────────────────────────────────────
def fig03_oscillator():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Кварцовий генератор: кристал «співає» на точній частоті", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "Волтер Кади, 1921 — схема, що підтримує вібрацію кварцу на його власній частоті", 11, GREY, "middle", style="italic")
    # tuning fork analogy
    s += text(180, 110, "як камертон:", 11, INK, "middle", "bold")
    s += line(160, 130, 160, 220, METAL, 4)
    s += line(200, 130, 200, 220, METAL, 4)
    s += line(160, 220, 200, 220, METAL, 4)
    s += line(180, 220, 180, 260, METAL, 4)
    s += text(180, 285, "своя точна нота", 9, GREY, "middle")
    s += text(180, 300, "(стала частота)", 9, GREY, "middle")
    # crystal + circuit
    s += rect(360, 150, 120, 70, "#eef6ef", GREEN, 1.8, 8)
    s += text(420, 182, "кварц", 11, INK, "middle", "bold")
    s += text(420, 200, "резонатор", 9, GREY, "middle")
    s += rect(560, 150, 140, 70, "#fbfcff", INK, 1.8, 8)
    s += text(630, 178, "генератор", 11, INK, "middle", "bold")
    s += text(630, 198, "(підживлює вібрацію)", 8.3, GREY, "middle")
    s += arrow(480, 172, 560, 172, INK, 2)
    s += arrow(560, 200, 480, 200, INK, 2)
    s += text(520, 158, "коливання", 8, GREY, "middle")
    s += text(520, 216, "поштовх", 8, GREY, "middle")
    s += arrow(700, 185, 790, 185, GREEN, 2.4)
    swave = [(795, 185), (805, 168), (815, 202), (825, 168), (835, 202), (845, 168), (855, 202), (865, 185)]
    s += poly(swave, GREEN, 2)
    s += text(845, 230, "рівний сигнал", 9, GREEN, "middle", "bold")
    s += text(845, 245, "точної частоти", 9, GREEN, "middle")
    s += rect(120, 330, 700, 50, LAMB, GOLD, 1.4, 10)
    s += text(470, 354, "Частота кварцу задана його розміром і огранкою — і майже не «пливе».", 10.5, INK, "middle", "bold")
    s += text(470, 372, "Тому кварцовий генератор — надійне джерело точного «тіку» для будь-якої електроніки.", 9.5, GREY, "middle")
    save("fig-24-0-3-oscillator.svg", s)


# ── Рис. 24.0.4 — перший кварцовий годинник (1927) ───────────────────────────
def fig04_marrison_clock():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Перший кварцовий годинник: Маррісон і Гортон, Bell Labs, 1927", 17, INK, "middle", "bold")
    s += text(W / 2, 54, "кварц на 50 000 Гц + дільник частоти, що зводить його до 1 тіку на секунду", 11, GREY, "middle", style="italic")
    blocks = [
        (40, "кварц +\nгенератор", "50 000 Гц", LGRN, GREEN),
        (280, "дільник\nчастоти", "÷ 50 000", LAMB, GOLD),
        (520, "1 Гц", "1 тік / секунду", LBLUE, BLUE),
        (740, "циферблат", "показує час", "#fbfcff", INK),
    ]
    for x, t, sub, fill, col in blocks:
        s += rect(x, 130, 180, 90, fill, col, 1.8, 10)
        ls = t.split("\n")
        yy = 162 if len(ls) > 1 else 172
        for ln in ls:
            s += text(x + 90, yy, ln, 12, INK, "middle", "bold")
            yy += 20
        s += text(x + 90, 206, sub, 9.5, col, "middle", "bold")
    for x in (220, 460, 700):
        s += arrow(x, 175, x + 60, 175, INK, 2.4)
    s += rect(220, 260, 520, 56, LAMB, GOLD, 1.4, 10)
    s += text(480, 284, "Дільник частоти — це, по суті, ЛІЧИЛЬНИК: він рахує 50 000 коливань і видає один тік.", 10.3, INK, "middle", "bold")
    s += text(480, 304, "Саме такий лічильник-таймер — герой цього розділу. Кварц дає тік, таймер його рахує.", 9.7, GREY, "middle")
    s += text(W / 2, 350, "Маррісон — канадський інженер; працював із Гортоном у Bell Labs (Нью-Йорк).", 9.5, GREY, "middle", style="italic")
    save("fig-24-0-4-marrison-clock.svg", s)


# ── Рис. 24.0.5 — спадок: кварц у кожному чипі ───────────────────────────────
def fig05_legacy():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Спадок: кварц тікає в кожному пристрої — і в ESP32", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "від відкриття Кюрі до чипа у вас на столі — одна неперервна лінія", 11.5, GREY, "middle", style="italic")
    x0, x1 = 70, 880
    y = 150
    s += line(x0, y, x1, y, INK, 2.2)
    pts = [("1880", "Кюрі:\nп'єзоефект", 70), ("1921", "Кади:\nгенератор", 250),
           ("1927", "Маррісон,\nГортон: годинник", 450), ("1969", "Seiko:\nнаручний", 650),
           ("нині", "кожен чип", 850)]
    for yr, lab, x in pts:
        s += circle(x, y, 5, GOLD, GOLD, 0)
        s += text(x, y + 24, yr, 11, INK, "middle", "bold")
        ls = lab.split("\n")
        yy = y - 38 if len(ls) > 1 else y - 28
        for ln in ls:
            s += text(x, yy, ln, 8.7, GREY, "middle")
            yy += 13
    # esp32
    s += rect(330, 250, 280, 110, "none", BLUE, 2, 12)
    s += text(470, 278, "ESP32 сьогодні", 12, BLUE, "middle", "bold")
    s += rect(355, 296, 90, 44, "#eef6ef", GREEN, 1.6, 6)
    s += text(400, 318, "кварц", 10, INK, "middle", "bold")
    s += text(400, 333, "~40 МГц", 9, GREEN, "middle")
    s += arrow(445, 318, 495, 318, INK, 2)
    s += rect(495, 296, 90, 44, LAMB, GOLD, 1.6, 6)
    s += text(540, 314, "таймери", 10, INK, "middle", "bold")
    s += text(540, 330, "рахують тік", 8.5, GREY, "middle")
    s += text(W / 2, 386, "Той самий принцип, що 1927-го: кварц дає рівний тік, а лічильник-таймер його відмірює.", 10.3, INK, "middle", "bold")
    save("fig-24-0-5-legacy.svg", s)


def _sqpulses(x, y, n, w=22, h=26, col=INK):
    """Серія тактових імпульсів (меандр)."""
    pts = [(x, y)]
    cx = x
    for i in range(n):
        pts += [(cx, y - h), (cx + w / 2, y - h), (cx + w / 2, y), (cx + w, y)]
        cx += w
    return poly(pts, col, 2)


# ═════════════════════════════════════════════════════════════════════════════
# §24.1 Таймер-лічильник: апаратний рахівник тактів — fig-24-1-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 24.1.1 — лічильник росте з кожним тактом ────────────────────────────
def fig11_counter_register():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Таймер — це лічильник, що росте з кожним тактом", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "кожен «тік» кварцу додає одиницю до регістра-лічильника — самотужки, без участі коду", 11, GREY, "middle", style="italic")
    # clock pulses
    s += text(70, 130, "такт:", 11, INK, "start", "bold")
    s += _sqpulses(140, 150, 8, 60, 26, BLUE)
    for i in range(8):
        s += line(140 + i * 60 + 15, 124, 140 + i * 60 + 15, 230, FAINT, 1, "3,3")
    # counter values
    s += text(70, 210, "лічильник:", 11, INK, "start", "bold")
    for i, v in enumerate(range(8)):
        x = 140 + i * 60
        s += rect(x, 192, 40, 36, LGRN, GREEN, 1.4, 5)
        s += text(x + 20, 216, str(v), 14, GREEN, "middle", "bold")
    s += arrow(165, 250, 165, 234, GREEN, 1.8)
    s += text(165, 268, "+1", 10, GREEN, "middle", "bold")
    s += text(500, 268, "…і так далі — лічильник рахує такти сам", 10, GREY, "middle", style="italic")
    s += rect(140, 300, 660, 56, LAMB, GOLD, 1.4, 10)
    s += text(470, 324, "Це той самий «дільник-лічильник», що в кварцовому годиннику 1927-го (історія розділу):", 10.3, INK, "middle", "bold")
    s += text(470, 344, "кварц дає рівний тік — апаратний лічильник його відмірює. Прочитав число — знаєш час.", 9.7, GREY, "middle")
    save("fig-24-1-1-counter-register.svg", s)


# ── Рис. 24.1.2 — апаратно проти програмного рахунку ─────────────────────────
def fig12_independent():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Чому апаратний: лічить сам, не забираючи процесора", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "програмний рахунок «з'їдає» ядро; апаратний таймер цокає паралельно, безкоштовно", 11, GREY, "middle", style="italic")
    # software
    s += rect(50, 90, 410, 270, "#fdf2f2", RED, 1.8, 12)
    s += text(255, 116, "Рахувати в коді — погано", 12.5, RED, "middle", "bold")
    s += rect(110, 145, 290, 60, "#ffffff", INK, 1.4, 8)
    s += text(255, 170, "for(i=0; i<N; i++) { /* нічого */ }", 10, INK, "middle", "bold")
    s += text(255, 192, "процесор зайнятий ЛИШЕ лічбою", 9, RED, "middle")
    s += text(255, 240, "✗ ядро стоїть, нічого не робить", 10.5, INK, "middle")
    s += text(255, 264, "✗ неточно: залежить від коду, перерви", 10.5, INK, "middle")
    s += text(255, 288, "✗ зупиниться, якщо код піде деінде", 10.5, INK, "middle")
    # hardware
    s += rect(480, 90, 410, 270, "#f3faf4", GREEN, 1.8, 12)
    s += text(685, 116, "Апаратний таймер — добре", 12.5, GREEN, "middle", "bold")
    s += rect(540, 145, 130, 60, LGRN, GREEN, 1.6, 8)
    s += text(605, 170, "таймер", 11, INK, "middle", "bold")
    s += text(605, 190, "цокає сам", 9, GREEN, "middle")
    s += rect(740, 145, 110, 60, LBLUE, BLUE, 1.6, 8)
    s += text(795, 170, "ядро", 11, INK, "middle", "bold")
    s += text(795, 190, "вільне!", 9, BLUE, "middle")
    s += text(685, 240, "✓ рахує паралельно, без тактів CPU", 10.5, INK, "middle")
    s += text(685, 264, "✓ точно: апаратно, без джитера коду", 10.5, INK, "middle")
    s += text(685, 288, "✓ цокає завжди, хоч що робить код", 10.5, INK, "middle")
    s += text(W / 2, 384, "Тому відлік часу віддають залізу: воно лічить незворушно, а процесор робить корисне.", 10.5, INK, "middle", "bold")
    save("fig-24-1-2-independent.svg", s)


# ── Рис. 24.1.3 — джерело такту й передільник ────────────────────────────────
def fig13_clock_prescaler():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Джерело такту й передільник: задаємо швидкість лічби", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "швидкий системний такт ділять передільником до зручного темпу лічильника", 11, GREY, "middle", style="italic")
    blocks = [
        (50, "системний такт", "80 МГц", LGRN, GREEN, "(APB, від ФАПЧ)"),
        (320, "передільник", "÷ 80", LAMB, GOLD, "(prescaler)"),
        (590, "лічильник", "+1 щомкс", LBLUE, BLUE, "= 1 МГц"),
    ]
    for x, t, sub, fill, col, note in blocks:
        s += rect(x, 130, 200, 90, fill, col, 1.8, 10)
        s += text(x + 100, 162, t, 12.5, INK, "middle", "bold")
        s += text(x + 100, 186, sub, 13, col, "middle", "bold")
        s += text(x + 100, 206, note, 8.7, GREY, "middle")
    for x in (250, 520):
        s += arrow(x, 175, x + 70, 175, INK, 2.4)
    s += rect(800, 150, 120, 50, "none", FAINT, 1.6, 8)
    s += text(860, 172, "1 тік =", 9.5, INK, "middle", "bold")
    s += text(860, 190, "1 мкс", 11, BLUE, "middle", "bold")
    s += arrow(790, 175, 800, 175, INK, 2)
    s += rect(150, 270, 660, 80, LAMB, GOLD, 1.4, 10)
    s += text(480, 296, "Передільник (дільник частоти!) керує роздільністю: ÷80 від 80 МГц дає темп 1 МГц,", 10.3, INK, "middle", "bold")
    s += text(480, 316, "тобто один тік на мікросекунду. Хочеш грубіше й надовше — ділиш сильніше;", 9.7, GREY, "middle")
    s += text(480, 334, "хочеш точніше — ділиш менше. Це той самий дільник, що в годиннику Маррісона.", 9.7, GREY, "middle")
    save("fig-24-1-3-clock-prescaler.svg", s)


# ── Рис. 24.1.4 — число лічильника = час ─────────────────────────────────────
def fig14_count_is_time():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 32, "Число в лічильнику — це і є виміряний час", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "кількість тіків × тривалість одного тіку = скільки часу минуло", 12, GREY, "middle", style="italic")
    s += rect(120, 110, 200, 70, LBLUE, BLUE, 1.8, 10)
    s += text(220, 140, "лічильник", 11, INK, "middle", "bold")
    s += text(220, 162, "= 1500", 15, BLUE, "middle", "bold")
    s += text(360, 150, "×", 18, INK, "middle", "bold")
    s += rect(400, 110, 200, 70, LGRN, GREEN, 1.8, 10)
    s += text(500, 140, "тік", 11, INK, "middle", "bold")
    s += text(500, 162, "= 1 мкс", 14, GREEN, "middle", "bold")
    s += text(640, 150, "=", 18, INK, "middle", "bold")
    s += rect(680, 110, 200, 70, LAMB, GOLD, 1.8, 10)
    s += text(780, 140, "час", 11, INK, "middle", "bold")
    s += text(780, 162, "= 1500 мкс", 14, "#8a6a14", "middle", "bold")
    s += text(780, 200, "= 1.5 мс", 11, GREY, "middle")
    s += rect(150, 250, 640, 80, "none", FAINT, 1.6, 10)
    s += text(470, 276, "Прочитав регістр лічильника — і одразу знаєш, скільки часу спливло.", 11, INK, "middle", "bold")
    s += text(470, 300, "Саме на цьому стоять millis() і micros(): вони повертають число тіків,", 10, INK, "middle")
    s += text(470, 320, "переведене в мілі- чи мікросекунди. Жодної магії — проста лічба.", 10, GREY, "middle")
    save("fig-24-1-4-count-is-time.svg", s)


# ── Рис. 24.1.5 — роздільність і діапазон ────────────────────────────────────
def fig15_resolution_range():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Роздільність і діапазон: біти й темп лічби", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "темп тіку задає ТОЧНІСТЬ, а число бітів — як ДОВГО можна лічити до переповнення", 11, GREY, "middle", style="italic")
    s += rect(50, 90, 410, 230, "none", BLUE, 1.8, 12)
    s += text(255, 116, "Роздільність = тривалість тіку", 11.5, BLUE, "middle", "bold")
    s += text(72, 146, "• тік 1 мкс → міряємо з точністю до мкс", 10, INK, "start")
    s += text(72, 170, "• тік 1 мс → лише до мілісекунди", 10, INK, "start")
    s += text(72, 200, "дрібніший тік = точніше,", 10.5, INK, "start", "bold")
    s += text(72, 222, "але швидше переповнюється", 10.5, INK, "start")
    s += text(72, 256, "(керується передільником)", 9.3, GREY, "start", style="italic")
    s += rect(480, 90, 410, 230, "none", GREEN, 1.8, 12)
    s += text(685, 116, "Діапазон = число бітів", 11.5, GREEN, "middle", "bold")
    s += text(502, 146, "• 16-біт @ 1 МГц → лише ~65 мс", 10, INK, "start")
    s += text(502, 170, "• 32-біт @ 1 МГц → ~71 хв", 10, INK, "start")
    s += text(502, 194, "• 64-біт (ESP32) → тисячоліття", 10, INK, "start")
    s += text(502, 224, "більше бітів = довше до", 10.5, INK, "start", "bold")
    s += text(502, 246, "переповнення (рахуємо далі)", 10.5, INK, "start")
    s += text(W / 2, 350, "Компроміс: дрібний тік дає точність, та малий лічильник швидко «обнуляється».", 10.5, INK, "middle", "bold")
    s += text(W / 2, 374, "Тому в ESP32 лічильники широкі (64 біти) — точність без частих переповнень.", 9.7, GREY, "middle")
    save("fig-24-1-5-resolution-range.svg", s)


# ── Рис. 24.1.6 — таймер ESP32 ───────────────────────────────────────────────
def fig16_esp32_timer():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Таймери ESP32: широкі лічильники від 80-мегагерцового такту", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "чотири універсальні таймери; на них стоять millis() і micros()", 12, GREY, "middle", style="italic")
    s += rect(60, 100, 150, 60, LGRN, GREEN, 1.6, 8)
    s += text(135, 126, "такт APB", 10.5, INK, "middle", "bold")
    s += text(135, 144, "80 МГц", 10, GREEN, "middle")
    s += arrow(210, 130, 270, 130, INK, 2.2)
    s += rect(270, 100, 160, 60, LAMB, GOLD, 1.6, 8)
    s += text(350, 124, "передільник", 10, INK, "middle", "bold")
    s += text(350, 144, "16-біт (÷2…65536)", 8.7, "#8a6a14", "middle")
    s += arrow(430, 130, 490, 130, INK, 2.2)
    s += rect(490, 100, 200, 60, LBLUE, BLUE, 1.6, 8)
    s += text(590, 124, "лічильник", 10.5, INK, "middle", "bold")
    s += text(590, 144, "64 біти, вгору/вниз", 8.7, BLUE, "middle")
    s += rect(730, 100, 170, 60, "none", FAINT, 1.6, 8)
    s += text(815, 124, "×4 таймери", 10.5, INK, "middle", "bold")
    s += text(815, 144, "(2 групи по 2)", 8.7, GREY, "middle")
    s += arrow(590, 160, 590, 210, INK, 2.2)
    s += rect(420, 210, 340, 60, "#eef6ef", GREEN, 1.8, 10)
    s += text(590, 236, "millis() · micros()", 13, GREEN, "middle", "bold")
    s += text(590, 256, "готові функції поверх апаратного лічильника", 9, INK, "middle")
    s += rect(150, 300, 660, 76, LAMB, GOLD, 1.4, 10)
    s += text(480, 326, "У коді ви задаєте передільник (темп тіку) і читаєте лічильник — або берете готові", 10.3, INK, "middle", "bold")
    s += text(480, 346, "millis()/micros(). Той самий принцип, що 1927-го: кварц цокає, лічильник рахує,", 9.7, GREY, "middle")
    s += text(480, 364, "код читає результат. Просто тепер усе вміщається в куточку кремнієвого чипа.", 9.7, GREY, "middle")
    save("fig-24-1-6-esp32-timer.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §24.2 Період і переповнення — fig-24-2-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 24.2.1 — переповнення (wrap) ────────────────────────────────────────
def fig21_overflow():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Переповнення: лічильник дійшов до максимуму й «обнулився»", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "лічильник скінченний; за максимумом наступний тік повертає його в нуль — і лічба триває", 11, GREY, "middle", style="italic")
    ox, oy = 90, 270
    s += arrow(ox, oy, ox, 90, INK, 2)
    s += arrow(ox, oy, 880, oy, INK, 2)
    s += text(ox - 8, 96, "значення", 10, INK, "end", "bold")
    s += text(880, oy + 22, "час", 10, INK, "end")
    top = 110
    # sawtooth
    saw = [(ox, oy), (300, top), (300, oy), (560, top), (560, oy), (820, top), (820, oy)]
    s += poly(saw, GREEN, 2.6)
    s += line(ox, top, 880, top, GREY, 1.2, dash="4,3")
    s += text(ox - 8, top + 4, "макс", 9.5, RED, "end", "bold")
    s += text(ox - 8, top - 8, "(2^N − 1)", 8, GREY, "end")
    for x in (300, 560, 820):
        s += circle(x, top, 5, RED, RED, 0)
        s += line(x, top, x, oy, RED, 1, "2,2")
        s += text(x, top - 10, "↯ переповнення", 8.5, RED, "middle", "bold")
    s += text(430, 300, "період переповнення = (макс+1) × тривалість тіку", 10, INK, "middle", "bold")
    s += text(430, 332, "16-біт @ 1 мкс → ~65 мс; 32-біт → ~71 хв; 64-біт → тисячоліття", 9.7, GREY, "middle")
    save("fig-24-2-1-overflow.svg", s)


# ── Рис. 24.2.2 — переповнення смикає переривання ────────────────────────────
def fig22_overflow_interrupt():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 32, "Переповнення — це подія: воно може смикнути переривання", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "щойно лічильник обнулився, таймер кличе обробник — точно й без участі коду", 11, GREY, "middle", style="italic")
    ox, oy = 90, 200
    s += arrow(ox, oy, 760, oy, INK, 2)
    saw = [(ox, oy), (250, 100), (250, oy), (450, 100), (450, oy), (650, 100), (650, oy)]
    s += poly(saw, GREEN, 2.4)
    s += line(ox, 100, 700, 100, GREY, 1.2, dash="4,3")
    s += text(ox - 6, 104, "макс", 9, RED, "end", "bold")
    for x in (250, 450, 650):
        s += circle(x, 100, 4, RED, RED, 0)
        s += arrow(x, 100, x, 60, RED, 2)
        s += text(x, 50, "↯", 13, RED, "middle", "bold")
    s += text(450, 36, "переривання за переповненням", 9.5, RED, "middle", "bold")
    s += rect(760, 150, 150, 70, "#eef6ef", GREEN, 1.8, 10)
    s += text(835, 178, "обробник", 11, GREEN, "middle", "bold")
    s += text(835, 198, "(ISR таймера)", 9, INK, "middle")
    s += arrow(700, 100, 800, 150, RED, 2)
    s += rect(150, 270, 640, 70, LAMB, GOLD, 1.4, 10)
    s += text(470, 296, "Так таймер сам, без опитування, сповіщає «минув проміжок!» — і обробник реагує.", 10.3, INK, "middle", "bold")
    s += text(470, 318, "Це поєднання таймера (Розділ 24) і переривання (Розділ 23) — основа всієї роботи з часом.", 9.7, GREY, "middle")
    save("fig-24-2-2-overflow-interrupt.svg", s)


# ── Рис. 24.2.3 — авто-перезавантаження задає період ─────────────────────────
def fig23_period_reload():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Авто-перезавантаження: задаємо СВІЙ період, а не весь діапазон", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "лічильник доходить до заданого «верху» (не максимуму), скидається й починає знову", 11, GREY, "middle", style="italic")
    ox, oy = 90, 280
    s += arrow(ox, oy, ox, 90, INK, 2)
    s += arrow(ox, oy, 900, oy, INK, 2)
    s += text(ox - 8, 96, "значення", 10, INK, "end", "bold")
    full = 110
    top = 180
    s += line(ox, full, 900, full, GREY, 1, "3,3")
    s += text(ox - 8, full + 4, "макс", 9, GREY, "end")
    s += line(ox, top, 900, top, GOLD, 1.6, dash="5,3")
    s += text(ox - 8, top + 4, "ВЕРХ", 9.5, "#8a6a14", "end", "bold")
    s += text(ox - 8, top - 8, "(reload)", 8, GREY, "end")
    saw = [(ox, oy), (230, top), (230, oy), (440, top), (440, oy), (650, top), (650, oy), (860, top), (860, oy)]
    s += poly(saw, GREEN, 2.6)
    for x in (230, 440, 650, 860):
        s += circle(x, top, 4, RED, RED, 0)
        s += arrow(x, top, x, top - 30, RED, 1.8)
    s += text(545, 138, "↯ кожне досягнення ВЕРХУ = один період (і переривання)", 9.5, RED, "middle", "bold")
    s += text(150, oy + 26, "період", 9, INK, "middle")
    s += line(230, oy + 14, 440, oy + 14, INK, 1.4)
    s += text(335, oy + 30, "= ВЕРХ × тік", 9, INK, "middle", "bold")
    s += text(W / 2, 350, "ВЕРХ (значення перезавантаження) і визначає період: менший ВЕРХ — частіше, більший — рідше.", 10.3, INK, "middle", "bold")
    s += text(W / 2, 374, "Так дістають рівні події будь-якого періоду — серце «годинника» в коді.", 9.7, GREY, "middle")
    save("fig-24-2-3-period-reload.svg", s)


# ── Рис. 24.2.4 — формула періоду ────────────────────────────────────────────
def fig24_period_formula():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 32, "Формула періоду: дві ручки задають будь-який інтервал", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "період = (значення ВЕРХУ) × (тривалість тіку), а тік задає передільник", 11.5, GREY, "middle", style="italic")
    s += rect(120, 100, 700, 56, "#0f1115", INK, 1.6, 10)
    s += '<text x="470" y="136" font-family="Consolas, monospace" font-size="17" fill="#e8e8e8" text-anchor="middle" font-weight="bold">T = ВЕРХ × передільник / частота_такту</text>\n'
    s += text(470, 188, "Приклад: період 1 мс на ESP32", 12.5, INK, "middle", "bold")
    s += rect(120, 206, 700, 90, "none", FAINT, 1.6, 10)
    s += text(140, 232, "частота такту = 80 МГц", 11, INK, "start")
    s += text(140, 256, "передільник ÷80  →  тік = 1 мкс", 11, BLUE, "start", "bold")
    s += text(140, 280, "ВЕРХ = 1000  →  T = 1000 × 1 мкс = 1 мс ✓", 11, GREEN, "start", "bold")
    s += text(560, 244, "1000 тіків по 1 мкс", 10, GREY, "middle")
    s += text(560, 264, "= 1000 мкс = 1 мс", 10, GREY, "middle")
    s += text(W / 2, 328, "Хочеш інший період — міняй ВЕРХ (або передільник). Дві ручки покривають усе.", 10.3, INK, "middle", "bold")
    save("fig-24-2-4-period-formula.svg", s)


# ── Рис. 24.2.5 — вибір передільника й верху ─────────────────────────────────
def fig25_choosing():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Дві ручки під один період: передільник і ВЕРХ", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "ту саму ціль (напр., 1 мс) можна набрати по-різному — обирай зручне число", 11, GREY, "middle", style="italic")
    s += rect(60, 86, 300, 36, "#f7f7f7", GREY, 1.4, 6)
    s += text(210, 110, "тік (від передільника)", 11, INK, "middle", "bold")
    s += rect(370, 86, 250, 36, "#f7f7f7", GREY, 1.4, 6)
    s += text(495, 110, "ВЕРХ", 11, INK, "middle", "bold")
    s += rect(630, 86, 270, 36, "#eef6ef", GREEN, 1.4, 6)
    s += text(765, 110, "= період", 11, GREEN, "middle", "bold")
    rows = [("÷80 → 1 мкс", "1000", "1 мс"), ("÷800 → 10 мкс", "100", "1 мс"), ("÷8000 → 100 мкс", "10", "1 мс")]
    y = 130
    for a, b, c in rows:
        s += rect(60, y, 300, 44, "#fff", BLUE, 1.2, 6)
        s += text(210, y + 28, a, 11, INK, "middle", "bold")
        s += rect(370, y, 250, 44, "#fff", GOLD, 1.2, 6)
        s += text(495, y + 28, b, 12, "#8a6a14", "middle", "bold")
        s += rect(630, y, 270, 44, "#fff", GREEN, 1.2, 6)
        s += text(765, y + 28, c, 12, GREEN, "middle", "bold")
        y += 50
    s += rect(120, 300, 720, 64, LAMB, GOLD, 1.4, 10)
    s += text(480, 326, "Усі три рядки дають 1 мс. Звичай: бери дрібний тік (точніше), а період — числом ВЕРХУ.", 10.3, INK, "middle", "bold")
    s += text(480, 348, "Слідкуй лише, щоб ВЕРХ уліз у лічильник (не перевищив його розрядність).", 9.7, GREY, "middle")
    save("fig-24-2-5-choosing.svg", s)


# ── Рис. 24.2.6 — переповнення millis() і безпечне віднімання ────────────────
def fig26_millis_wraparound():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Переповнення millis(): чому віднімання все одно працює", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "millis() теж переповнюється (~49.7 дня), та різниця (now − last) лишається правильною", 11, GREY, "middle", style="italic")
    ox, oy = 80, 200
    s += arrow(ox, oy, 700, oy, INK, 2)
    s += poly([(ox, oy), (300, 90), (300, oy), (560, 90), (560, oy)], GREEN, 2.4)
    s += line(ox, 90, 620, 90, GREY, 1, "3,3")
    s += text(ox - 6, 94, "2^32", 9, RED, "end", "bold")
    s += circle(300, 90, 4, RED, RED, 0)
    s += text(300, 78, "↯ wrap (~49.7 дня)", 8.7, RED, "middle", "bold")
    s += text(360, oy + 24, "далі лічба з нуля", 9, GREY, "middle")
    # right vs wrong
    s += rect(60, 250, 420, 120, "#f3faf4", GREEN, 1.8, 10)
    s += text(270, 276, "ПРАВИЛЬНО (стійко до wrap)", 11, GREEN, "middle", "bold")
    s += '<text x="80" y="304" font-family="Consolas, monospace" font-size="13" fill="#1b1b1b">if (millis() - last >= interval)</text>\n'
    s += text(270, 330, "віднімання беззнакове → wrap", 9.3, INK, "middle")
    s += text(270, 348, "сам себе компенсує. Завжди так.", 9.3, INK, "middle")
    s += rect(500, 250, 420, 120, "#fdf2f2", RED, 1.8, 10)
    s += text(710, 276, "НЕПРАВИЛЬНО (ламається на wrap)", 10.5, RED, "middle", "bold")
    s += '<text x="520" y="304" font-family="Consolas, monospace" font-size="13" fill="#1b1b1b">if (millis() >= last + interval)</text>\n'
    s += text(710, 330, "після переповнення порівняння", 9.3, INK, "middle")
    s += text(710, 348, "збивається — подія застрягне.", 9.3, INK, "middle")
    save("fig-24-2-6-millis-wraparound.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §24.3 Захоплення й порівняння — fig-24-3-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 24.3.1 — захоплення (input capture) ─────────────────────────────────
def fig31_capture_concept():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Захоплення (capture): залізо миттєво «фотографує» лічильник на фронті", 16.5, INK, "middle", "bold")
    s += text(W / 2, 54, "прийшов фронт на ніжку — апаратура тієї ж миті копіює значення лічильника в регістр", 10.5, GREY, "middle", style="italic")
    # counter ramp
    ox, oy = 90, 210
    s += arrow(ox, oy, 760, oy, INK, 2)
    s += poly([(ox, oy), (300, 110), (300, oy), (560, 110), (560, oy)], GREEN, 2)
    s += text(64, 130, "лічильник", 10, GREEN, "start", "bold")
    # external signal with edge
    s += text(64, 260, "сигнал", 10, BLUE, "start", "bold")
    s += poly([(ox, 290), (360, 290), (360, 250), (760, 250)], BLUE, 2.4)
    s += circle(360, 250, 5, RED, RED, 0)
    s += text(360, 240, "↑ фронт тут", 9, RED, "middle", "bold")
    s += line(360, 250, 360, oy, RED, 1.4, dash="3,3")
    s += circle(360, 174, 4, RED, RED, 0)
    s += arrow(360, 174, 470, 150, RED, 2)
    s += rect(470, 130, 200, 50, LRED, RED, 1.8, 8)
    s += text(570, 152, "регістр захоплення", 10, RED, "middle", "bold")
    s += text(570, 170, "= значення лічильника", 8.7, INK, "middle")
    s += rect(150, 310, 640, 56, LAMB, GOLD, 1.4, 10)
    s += text(470, 334, "Знімок робить ЗАЛІЗО тієї ж наносекунди — без затримки коду й джитера переривань.", 10, INK, "middle", "bold")
    s += text(470, 354, "Це точна апаратна «мітка часу» зовнішньої події.", 9.5, GREY, "middle")
    save("fig-24-3-1-capture-concept.svg", s)


# ── Рис. 24.3.2 — вимір ширини імпульсу захопленням ──────────────────────────
def fig32_capture_measure():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Навіщо захоплення: точно виміряти тривалість і період", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "захопи значення на двох фронтах, відніми — і знаєш тривалість із точністю до тіку", 11, GREY, "middle", style="italic")
    ox = 100
    yb = 170
    s += text(64, 150, "сигнал", 10, BLUE, "start", "bold")
    s += poly([(ox, yb + 40), (260, yb + 40), (260, yb), (560, yb), (560, yb + 40), (820, yb + 40)], BLUE, 2.6)
    s += circle(260, yb, 5, GREEN, GREEN, 0)
    s += text(260, yb - 12, "захоплення A", 9, GREEN, "middle", "bold")
    s += text(260, yb - 28, "(фронт ↑)", 8, GREY, "middle")
    s += circle(560, yb, 5, RED, RED, 0)
    s += text(560, yb - 12, "захоплення B", 9, RED, "middle", "bold")
    s += text(560, yb - 28, "(спад ↓)", 8, GREY, "middle")
    s += line(260, yb + 60, 560, yb + 60, INK, 1.6)
    s += text(410, yb + 78, "ширина імпульсу = (B − A) × тік", 11, INK, "middle", "bold")
    s += rect(150, 290, 660, 70, "none", FAINT, 1.6, 10)
    s += text(480, 316, "Так апаратно міряють тривалість імпульсу, період і частоту зовнішніх сигналів:", 10.3, INK, "middle", "bold")
    s += text(480, 338, "ультразвуковий далекомір, тахометр, декодування сигналів — усе через захоплення.", 9.7, GREY, "middle")
    save("fig-24-3-2-capture-measure.svg", s)


# ── Рис. 24.3.3 — порівняння (output compare) ────────────────────────────────
def fig33_compare_concept():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Порівняння (compare): дія, щойно лічильник дійде до мітки", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "залізо весь час звіряє лічильник із заданим числом; збіг → автоматична дія на ніжці", 10.5, GREY, "middle", style="italic")
    ox, oy = 90, 230
    s += arrow(ox, oy, 760, oy, INK, 2)
    s += poly([(ox, oy), (760, 90)], GREEN, 2.4)
    s += text(64, 110, "лічильник", 10, GREEN, "start", "bold")
    cmp_y = 150
    s += line(ox, cmp_y, 760, cmp_y, GOLD, 1.8, dash="5,3")
    s += text(764, cmp_y + 4, "значення порівняння", 9.5, "#8a6a14", "start", "bold")
    # match point
    mx = ox + (760 - ox) * (oy - cmp_y) / (oy - 90)
    s += circle(mx, cmp_y, 6, RED, RED, 0)
    s += text(mx, cmp_y - 12, "збіг!", 10, RED, "middle", "bold")
    s += arrow(mx, cmp_y, mx, 300, RED, 2)
    s += rect(mx - 110, 300, 220, 50, LRED, RED, 1.8, 8)
    s += text(mx, 322, "дія: перемкнути ніжку", 10, RED, "middle", "bold")
    s += text(mx, 340, "та/або переривання", 8.7, INK, "middle")
    s += text(W / 2, 372, "Залізо саме «натискає» в потрібний тік — без жодної затримки коду. Точність ідеальна.", 10.3, INK, "middle", "bold")
    save("fig-24-3-3-compare-concept.svg", s)


# ── Рис. 24.3.4 — порівняння → хвиля ─────────────────────────────────────────
def fig34_compare_waveform():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Перемикання на збіг → точна прямокутна хвиля", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "якщо на кожен збіг перемикати ніжку, дістанемо рівний меандр заданої частоти", 11, GREY, "middle", style="italic")
    ox, oy = 90, 190
    s += arrow(ox, oy, 820, oy, INK, 2)
    # sawtooth counter
    saw = [(ox, oy), (210, 110), (210, oy), (370, 110), (370, oy), (530, 110), (530, oy), (690, 110), (690, oy)]
    s += poly(saw, GREEN, 1.8)
    s += line(ox, 130, 760, 130, GOLD, 1.4, dash="4,3")
    s += text(64, 134, "поріг", 9, "#8a6a14", "start", "bold")
    for x in (190, 350, 510, 670):
        s += circle(x, 130, 3.5, RED, RED, 0)
    # output square wave below
    yo = 280
    s += text(64, 270, "ніжка", 10, BLUE, "start", "bold")
    sq = [(ox, yo + 30), (190, yo + 30), (190, yo), (350, yo), (350, yo + 30), (510, yo + 30), (510, yo), (670, yo), (670, yo + 30), (760, yo + 30)]
    s += poly(sq, BLUE, 2.6)
    for x in (190, 350, 510, 670):
        s += line(x, 130, x, yo + 30, FAINT, 1, "3,3")
    s += text(W / 2, 350, "Це й є фундамент ШІМ (PWM): рівні апаратні імпульси без участі процесора (наступний розділ).", 10, INK, "middle", "bold")
    save("fig-24-3-4-compare-waveform.svg", s)


# ── Рис. 24.3.5 — апаратно проти програмно ───────────────────────────────────
def fig35_hw_vs_sw():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Чому апаратно: точність до тіку, а не «коли код устигне»", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "програмна реакція «пливе» від затримки переривань; апаратна — рівно в потрібну мить", 10.5, GREY, "middle", style="italic")
    # hardware
    s += rect(50, 90, 410, 240, "#f3faf4", GREEN, 1.8, 12)
    s += text(255, 116, "Апаратно (capture/compare)", 11.5, GREEN, "middle", "bold")
    s += text(72, 150, "подія / дія прив'язана", 10.5, INK, "start")
    s += text(72, 172, "просто до значення лічильника", 10.5, INK, "start")
    for i in range(4):
        x = 100 + i * 80
        s += line(x, 210, x, 250, GREEN, 2.4)
    s += text(255, 280, "✓ рівні інтервали, точність до тіку", 10, INK, "middle")
    s += text(255, 304, "✓ не залежить від зайнятості коду", 10, INK, "middle")
    # software
    s += rect(480, 90, 410, 240, "#fdf2f2", RED, 1.8, 12)
    s += text(685, 116, "Програмно (в обробнику)", 11.5, RED, "middle", "bold")
    s += text(502, 150, "код міряє/смикає ніжку сам —", 10.5, INK, "start")
    s += text(502, 172, "із затримкою й джитером", 10.5, INK, "start")
    for i, dx in enumerate([0, 14, -8, 20]):
        x = 530 + i * 80 + dx
        s += line(x, 210, x, 250, RED, 2.4)
    s += text(685, 280, "✗ інтервали «пливуть» (джитер)", 10, INK, "middle")
    s += text(685, 304, "✗ збивається, коли код зайнятий", 10, INK, "middle")
    s += text(W / 2, 360, "Для точного вимірювання й генерації сигналів захоплення/порівняння незамінні.", 10.5, INK, "middle", "bold")
    save("fig-24-3-5-hw-vs-sw.svg", s)


# ── Рис. 24.3.6 — де це в ESP32 ──────────────────────────────────────────────
def fig36_esp32_peripherals():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Де це в ESP32: спеціальні периферійні блоки", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "базовий таймер дає лічбу й «будильник»; захоплення й PWM — в окремих модулях", 11, GREY, "middle", style="italic")
    cards = [
        (50, "GP-таймер (TIMG)", "лічба часу, alarm", "періоди, millis/micros", BLUE),
        (290, "MCPWM (capture)", "захоплення фронтів", "вимір тривалості/частоти", GREEN),
        (530, "LEDC / MCPWM", "порівняння → вихід", "ШІМ, точні імпульси (§25)", GOLD),
        (770, "PCNT", "лічильник імпульсів", "рахує фронти на ніжці", RED),
    ]
    for ox, t, l1, l2, col in cards:
        s += rect(ox, 100, 210, 150, "#fbfcff", col, 1.8, 12)
        s += text(ox + 105, 130, t, 11.5, col, "middle", "bold")
        s += line(ox + 16, 144, ox + 194, 144, col, 1.2)
        s += text(ox + 105, 176, l1, 10, INK, "middle", "bold")
        s += text(ox + 105, 210, l2, 9, GREY, "middle")
    s += rect(120, 290, 720, 80, LAMB, GOLD, 1.4, 10)
    s += text(480, 316, "Ідеї ті самі (захоплення = мітка входу, порівняння = дія на виході),", 10.3, INK, "middle", "bold")
    s += text(480, 338, "та в ESP32 їх рознесено по спеціалізованих блоках замість «усе в одному таймері».", 9.7, GREY, "middle")
    s += text(480, 358, "Для вас це означає: під задачу — свій модуль; принцип скрізь однаковий.", 9.7, GREY, "middle")
    save("fig-24-3-6-esp32-peripherals.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §24.4 millis/micros зсередини — fig-24-4-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 24.4.1 — що повертають millis/micros ────────────────────────────────
def fig41_what_they_return():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 32, "millis() і micros(): скільки минуло ВІД СТАРТУ чипа", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "не «котра година», а лічильник часу, що пішов із нуля в мить увімкнення", 11, GREY, "middle", style="italic")
    ox = 90
    s += circle(ox, 150, 8, RED, RED, 0)
    s += text(ox, 124, "увімкнення", 10, RED, "middle", "bold")
    s += text(ox, 110, "(t = 0)", 9, GREY, "middle")
    s += arrow(ox, 150, 860, 150, INK, 2.4)
    for frac, lab in [(0.3, ""), (0.55, ""), (0.8, "")]:
        x = ox + (860 - ox) * frac
        s += line(x, 145, x, 155, GREY, 1.4)
    s += text(820, 176, "час →", 10, INK, "middle")
    s += rect(330, 210, 130, 50, LGRN, GREEN, 1.6, 8)
    s += text(395, 232, "millis()", 12, GREEN, "middle", "bold")
    s += text(395, 250, "= мс від старту", 8.7, INK, "middle")
    s += rect(560, 210, 130, 50, LBLUE, BLUE, 1.6, 8)
    s += text(625, 232, "micros()", 12, BLUE, "middle", "bold")
    s += text(625, 250, "= мкс від старту", 8.7, INK, "middle")
    s += line(395, 150, 395, 210, GREEN, 1.2, "3,3")
    s += line(625, 150, 625, 210, BLUE, 1.2, "3,3")
    s += text(W / 2, 312, "Обидві просто читають апаратний лічильник часу й переводять його в мс або мкс.", 10.5, INK, "middle", "bold")
    s += text(W / 2, 334, "Скинеться лічильник лише при перезавантаженні — тоді відлік знову з нуля.", 9.7, GREY, "middle")
    save("fig-24-4-1-what-they-return.svg", s)


# ── Рис. 24.4.2 — як це в AVR (Uno) ──────────────────────────────────────────
def fig42_avr_internals():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Як усередині AVR (Arduino Uno): переривання щомілісекунди", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "малий таймер переповнюється ~раз на мс і ISR додає 1 до лічильника мілісекунд", 11, GREY, "middle", style="italic")
    ox, oy = 80, 200
    s += arrow(ox, oy, 560, oy, INK, 2)
    saw = [(ox, oy), (180, 120), (180, oy), (320, 120), (320, oy), (460, 120), (460, oy)]
    s += poly(saw, GREEN, 2)
    s += text(64, 110, "Timer0", 9.5, GREEN, "start", "bold")
    for x in (180, 320, 460):
        s += circle(x, 120, 4, RED, RED, 0)
        s += arrow(x, 120, x, 80, RED, 1.8)
    s += text(320, 66, "↯ переповнення ~кожні 1.024 мс", 9, RED, "middle", "bold")
    s += rect(600, 150, 300, 56, "#fbfcff", INK, 1.6, 8)
    s += text(750, 174, "ISR переповнення:", 10.5, INK, "middle", "bold")
    s += text(750, 194, "ms_count++  (лічильник мс)", 10, INK, "middle")
    s += arrow(560, 110, 600, 160, RED, 2)
    s += rect(250, 270, 460, 90, "none", FAINT, 1.6, 10)
    s += text(480, 296, "millis() → повертає ms_count", 11, GREEN, "middle", "bold")
    s += text(480, 320, "micros() → ms_count×1000 + (Timer0 × 4)", 11, BLUE, "middle", "bold")
    s += text(480, 344, "(на Uno micros має крок ~4 мкс — обмеження передільника)", 9, GREY, "middle")
    save("fig-24-4-2-avr-internals.svg", s)


# ── Рис. 24.4.3 — як це в ESP32 ──────────────────────────────────────────────
def fig43_esp32_internals():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Як усередині ESP32: широкий лічильник у мікросекундах", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "64-бітний системний таймер сам рахує мкс; жодного переривання щомілісекунди не треба", 10.5, GREY, "middle", style="italic")
    s += rect(80, 110, 250, 80, LBLUE, BLUE, 1.8, 10)
    s += text(205, 138, "системний таймер", 11, BLUE, "middle", "bold")
    s += text(205, 160, "64 біти, лічить у мкс", 9.5, INK, "middle")
    s += text(205, 178, "(тікає сам від кварцу)", 8.5, GREY, "middle")
    s += arrow(330, 140, 420, 140, INK, 2.4)
    s += rect(420, 110, 230, 44, LBLUE, BLUE, 1.6, 8)
    s += text(535, 138, "micros() = читати його", 10.5, INK, "middle", "bold")
    s += arrow(330, 150, 420, 178, INK, 2.4)
    s += rect(420, 168, 230, 44, LGRN, GREEN, 1.6, 8)
    s += text(535, 196, "millis() = ÷ 1000", 10.5, INK, "middle", "bold")
    s += rect(700, 110, 200, 102, "none", FAINT, 1.6, 10)
    s += text(800, 134, "Переваги:", 10.5, INK, "middle", "bold")
    s += text(716, 158, "• крок micros ~1 мкс", 9.3, INK, "start")
    s += text(716, 178, "• 64 біти — майже", 9.3, INK, "start")
    s += text(726, 194, "не переповнюється", 9.3, INK, "start")
    s += rect(150, 250, 660, 100, LAMB, GOLD, 1.4, 10)
    s += text(480, 276, "Прямо читати лічильник простіше й точніше, ніж колупати переривання щомілісекунди.", 10.3, INK, "middle", "bold")
    s += text(480, 300, "Увага: Arduino-функції повертають 32-біт, тож millis обгортається ~49.7 дня,", 9.7, GREY, "middle")
    s += text(480, 320, "а micros ~71 хв (§24.2) — хоч сам лічильник усередині 64-бітний. Порівнюй відніманням!", 9.7, GREY, "middle")
    save("fig-24-4-3-esp32-internals.svg", s)


# ── Рис. 24.4.4 — роздільність ───────────────────────────────────────────────
def fig44_resolution():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Роздільність: millis() крокує по 1 мс, micros() — тонше", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "значення міняється сходинками; дрібніший крок — точніший вимір коротких проміжків", 11, GREY, "middle", style="italic")
    # millis staircase (coarse)
    ox = 90
    s += text(64, 130, "millis()", 10, GREEN, "start", "bold")
    st = [(ox, 170)]
    for i in range(5):
        st += [(ox + i * 120 + 120, 170 - 0), (ox + i * 120 + 120, 170 - 22)]
        st[-2] = (ox + i * 120 + 120, 170 - i * 0)
    # simpler: draw step staircase
    pts = [(ox, 190)]
    for i in range(5):
        pts.append((ox + (i + 1) * 110, 190 - (i + 1) * 0))
    # explicit coarse steps
    g = [(ox, 200), (ox + 130, 200), (ox + 130, 170), (ox + 260, 170), (ox + 260, 140), (ox + 390, 140), (ox + 390, 110), (ox + 520, 110)]
    s += poly(g, GREEN, 2.4)
    s += text(ox + 65, 216, "крок 1 мс", 8.5, GREEN, "middle")
    # micros staircase (fine)
    bx = 90
    f = [(bx, 320)]
    yy = 320
    for i in range(26):
        f.append((bx + (i + 1) * 20, 320 - (i + 1) * 4))
    s += poly(f, BLUE, 2.2)
    s += text(64, 300, "micros()", 10, BLUE, "start", "bold")
    s += text(bx + 250, 336, "крок ~1 мкс (у 1000× дрібніший)", 9, BLUE, "middle", "bold")
    s += rect(640, 110, 270, 130, "none", FAINT, 1.6, 10)
    s += text(775, 136, "Що обрати:", 10.5, INK, "middle", "bold")
    s += text(656, 162, "• інтервали від мс — millis()", 9.5, INK, "start")
    s += text(656, 186, "• короткі/точні — micros()", 9.5, INK, "start")
    s += text(656, 212, "(на Uno крок micros ~4 мкс,", 9, GREY, "start")
    s += text(666, 228, "на ESP32 ~1 мкс)", 9, GREY, "start")
    save("fig-24-4-4-resolution.svg", s)


# ── Рис. 24.4.5 — точність = точність кварцу ─────────────────────────────────
def fig45_accuracy_crystal():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Точність millis/micros = точність кварцу", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "лічба ідеально рівна, та сам кварц трохи «біжить» чи «відстає» — на скільки, каже ppm", 10.5, GREY, "middle", style="italic")
    s += rect(60, 100, 400, 110, "none", BLUE, 1.8, 10)
    s += text(260, 126, "Що таке ppm", 11.5, BLUE, "middle", "bold")
    s += text(78, 152, "ppm = частин на мільйон похибки.", 10, INK, "start")
    s += text(78, 174, "±10 ppm  →  ±~0.86 секунди на добу", 10, INK, "start")
    s += text(78, 196, "±50 ppm  →  ±~4.3 секунди на добу", 10, INK, "start")
    s += rect(490, 100, 400, 110, "none", GREEN, 1.8, 10)
    s += text(690, 126, "Що з цим робити", 11.5, GREEN, "middle", "bold")
    s += text(508, 152, "• короткі інтервали — точні", 10, INK, "start")
    s += text(508, 174, "• за години/дні набігає дрейф", 10, INK, "start")
    s += text(508, 196, "• треба «справжній час» — RTC/мережа", 10, INK, "start")
    s += rect(150, 250, 640, 100, LAMB, GOLD, 1.4, 10)
    s += text(470, 276, "Сам лічильник не помиляється — він чесно лічить тіки. Уся похибка йде від кварцу:", 10.3, INK, "middle", "bold")
    s += text(470, 298, "тепло, старіння, розкид примірників зрушують його частоту на ті самі ppm.", 9.7, GREY, "middle")
    s += text(470, 320, "Тому millis() чудовий для проміжків, але не годинник на роки без звірки.", 9.7, GREY, "middle")
    save("fig-24-4-5-accuracy-crystal.svg", s)


# ── Рис. 24.4.6 — як вживати ─────────────────────────────────────────────────
def fig46_usage():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Як вживати: мітка, інтервал, тайм-аут", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "три типові прийоми — і скрізь час порівнюють ВІДНІМАННЯМ (стійко до переповнення)", 10.5, GREY, "middle", style="italic")
    cards = [
        (50, "Мітка часу", "t = micros();", "запам'ятати мить події", BLUE),
        (340, "Інтервал", "dt = micros() − t0;", "скільки тривало", GREEN),
        (630, "Тайм-аут", "if (millis() − t0 > LIMIT)", "чи не задовго чекаємо", GOLD),
    ]
    for ox, t, code, note, col in cards:
        s += rect(ox, 90, 280, 150, "#fbfcff", col, 1.8, 12)
        s += text(ox + 140, 120, t, 13, col, "middle", "bold")
        s += line(ox + 20, 134, ox + 260, 134, col, 1.2)
        s += rect(ox + 20, 150, 240, 32, "#0f1115", INK, 1.2, 5)
        s += f'<text x="{ox+140}" y="171" font-family="Consolas, monospace" font-size="11.5" fill="#7ee0a0" text-anchor="middle">{_esc(code)}</text>\n'
        s += text(ox + 140, 210, note, 9.5, GREY, "middle")
    s += rect(150, 300, 660, 56, LAMB, GOLD, 1.4, 10)
    s += text(480, 326, "Усі три безпечні до переповнення, бо працюють із РІЗНИЦЕЮ часів, а не з абсолютом.", 10.3, INK, "middle", "bold")
    s += text(480, 346, "millis()/micros() — дешеві: викликай скільки треба, вони лише читають лічильник.", 9.7, GREY, "middle")
    save("fig-24-4-6-usage.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §24.5 Чому delay() — зло; неблокуючий час — fig-24-5-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 24.5.1 — delay() заморожує все ──────────────────────────────────────
def fig51_delay_blocks():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "delay() заморожує ВЕСЬ процесор на час очікування", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "поки delay чекає, програма стоїть і не може ані прочитати кнопку, ані зробити щось інше", 10.5, GREY, "middle", style="italic")
    ox, oy = 90, 160
    s += text(64, 140, "loop()", 10, INK, "start", "bold")
    s += line(ox, oy, 250, oy, GREEN, 3)
    s += rect(250, oy - 16, 440, 32, LRED, RED, 2, 6)
    s += text(470, oy + 6, "delay(1000) — процесор СТОЇТЬ", 12, RED, "middle", "bold")
    s += line(690, oy, 850, oy, GREEN, 3)
    # button press during delay
    s += circle(470, 250, 5, GOLD, GOLD, 0)
    s += text(470, 272, "натиск кнопки тут", 9.5, "#8a6a14", "middle", "bold")
    s += line(470, 244, 470, oy + 16, GOLD, 1.4, dash="3,3")
    s += text(470, 300, "✗ проґавлено — код не дивиться", 10, RED, "middle", "bold")
    s += rect(150, 320, 640, 46, LAMB, GOLD, 1.4, 8)
    s += text(470, 348, "Одна команда delay(1000) = секунда повної бездіяльності всієї програми.", 10.5, INK, "middle", "bold")
    save("fig-24-5-1-delay-blocks.svg", s)


# ── Рис. 24.5.2 — два діла одночасно не виходять ─────────────────────────────
def fig52_two_things():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "З delay() не зробиш двох справ із різним ритмом", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "блимати одним LED раз на 500 мс, іншим — раз на 300 мс: delay одного блокує другий", 10.5, GREY, "middle", style="italic")
    # desired
    s += text(64, 120, "треба:", 10, INK, "start", "bold")
    s += text(120, 120, "LED-A кожні 500 мс", 10, GREEN, "start", "bold")
    s += text(120, 142, "LED-B кожні 300 мс", 10, BLUE, "start", "bold")
    # with delay - blocked
    yb = 210
    s += text(64, yb - 18, "delay:", 10, RED, "start", "bold")
    s += rect(120, yb - 14, 200, 28, LGRN, GREEN, 1.6, 5)
    s += text(220, yb + 5, "A, delay(500)", 9.5, INK, "middle", "bold")
    s += rect(330, yb - 14, 200, 28, LRED, RED, 1.6, 5)
    s += text(430, yb + 5, "B ЧЕКАЄ ці 500 мс", 8.7, RED, "middle", "bold")
    s += rect(540, yb - 14, 200, 28, LBLUE, BLUE, 1.6, 5)
    s += text(640, yb + 5, "B, delay(300)", 9.5, INK, "middle", "bold")
    s += rect(750, yb - 14, 140, 28, LRED, RED, 1.6, 5)
    s += text(820, yb + 5, "A збився!", 9, RED, "middle", "bold")
    s += text(480, yb + 40, "Ритми збиваються: поки чекає один delay, другий LED стоїть. Так двох ритмів не втримати.", 10, INK, "middle", "bold")
    s += rect(150, 300, 660, 56, LAMB, GOLD, 1.4, 10)
    s += text(480, 326, "Корінь проблеми: delay() монополізує процесор. Доки він чекає, більше НІЩО не діється.", 10.3, INK, "middle", "bold")
    s += text(480, 346, "А реальні пристрої мусять робити багато справ «водночас».", 9.7, GREY, "middle")
    save("fig-24-5-2-two-things.svg", s)


# ── Рис. 24.5.3 — патерн millis ──────────────────────────────────────────────
def fig53_nonblocking_pattern():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Неблокуючий патерн: «чи вже час?» замість «зачекай»", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "не зупиняємось — лише перевіряємо різницю часів і йдемо далі", 11, GREY, "middle", style="italic")
    s += rect(120, 90, 720, 150, "#0f1115", INK, 1.6, 10)
    s += '<text x="140" y="120" font-family="Consolas, monospace" font-size="14.5" fill="#7fb4ff">unsigned long last = 0;</text>\n'
    s += '<text x="140" y="146" font-family="Consolas, monospace" font-size="14.5" fill="#e8e8e8">void loop() {</text>\n'
    s += '<text x="140" y="172" font-family="Consolas, monospace" font-size="14.5" fill="#e8e8e8">  if (millis() - last &gt;= interval) {</text>\n'
    s += '<text x="140" y="198" font-family="Consolas, monospace" font-size="14.5" fill="#7ee0a0">    last += interval;   // наступний строк</text>\n'
    s += '<text x="140" y="224" font-family="Consolas, monospace" font-size="14.5" fill="#e8e8e8">    /* зробити дію */ }</text>\n'
    s += '<text x="600" y="224" font-family="Consolas, monospace" font-size="14.5" fill="#caa24a">// + інша робота</text>\n'
    s += text(250, 280, "ще НЕ час → нічого не робимо,", 11, INK, "middle")
    s += text(250, 300, "просто йдемо далі по loop()", 11, INK, "middle", "bold")
    s += text(710, 280, "ВЖЕ час → робимо дію", 11, GREEN, "middle")
    s += text(710, 300, "й запам'ятовуємо новий строк", 11, GREEN, "middle", "bold")
    s += rect(180, 330, 600, 50, LAMB, GOLD, 1.4, 10)
    s += text(480, 356, "Ключ: loop() НЕ зупиняється. Він лиш питає «чи минув інтервал?» — і завжди вільний", 10, INK, "middle", "bold")
    s += text(480, 374, "робити інше. Це і є «блимання без delay».", 9.5, GREY, "middle")
    save("fig-24-5-3-nonblocking-pattern.svg", s)


# ── Рис. 24.5.4 — loop крутиться швидко ──────────────────────────────────────
def fig54_loop_spinning():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 32, "loop() крутиться тисячі разів на секунду — і встигає все", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "без блокувань цикл блискавичний; кожен прохід перевіряє, що «настало», й рухається далі", 10.5, GREY, "middle", style="italic")
    ox, oy = 90, 160
    s += arrow(ox, oy, 860, oy, INK, 2)
    for i in range(14):
        x = ox + 30 + i * 56
        s += circle(x, oy, 4, GREEN, GREEN, 0)
        s += line(x, oy - 8, x, oy + 8, GREEN, 1.4)
    s += text(470, oy - 22, "проходи loop() — дуже часті", 10, GREEN, "middle", "bold")
    s += text(470, oy + 28, "(тисячі за секунду, бо ніщо не блокує)", 9, GREY, "middle")
    # tasks fire occasionally
    for x, lab, col in [(230, "блимнути LED", GREEN), (470, "прочитати давач", BLUE), (710, "оновити екран", GOLD)]:
        s += arrow(x, 230, x, 178, col, 1.8)
        s += rect(x - 70, 230, 140, 30, "#fbfcff", col, 1.4, 6)
        s += text(x, 250, lab, 9, INK, "middle", "bold")
    s += text(470, 300, "Більшість проходів — «ще не час, далі». Зрідка щось «настає» — і робиться вмить.", 10.3, INK, "middle", "bold")
    s += text(470, 322, "Так один швидкий цикл веде багато справ нібито «водночас» (кооперативно).", 9.7, GREY, "middle")
    save("fig-24-5-4-loop-spinning.svg", s)


# ── Рис. 24.5.5 — багато задач у одному циклі ────────────────────────────────
def fig55_multiple_tasks():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Багато незалежних задач — кожна зі своїм строком", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "у кожної своя пара (last, interval); усі перевіряються щопрохід — і не заважають одна одній", 10.5, GREY, "middle", style="italic")
    tasks = [
        ("блимати LED", "interval = 500 мс", GREEN),
        ("опитати давач", "interval = 100 мс", BLUE),
        ("оновити дисплей", "interval = 1000 мс", GOLD),
    ]
    y = 100
    for t, iv, col in tasks:
        s += rect(120, y, 720, 60, "#fbfcff", col, 1.6, 10)
        s += text(150, y + 26, t, 12, col, "start", "bold")
        s += text(150, y + 47, "if (millis() - last_n >= " + iv.split("= ")[1] + ") { … }", 10, INK, "start")
        s += text(720, y + 36, iv, 10, GREY, "middle")
        y += 78
    s += rect(180, 340, 600, 50, LAMB, GOLD, 1.4, 10)
    s += text(480, 366, "Три рядки `if` в одному loop() — і три діла йдуть кожне у своєму ритмі, незалежно.", 10.3, INK, "middle", "bold")
    s += text(480, 384, "Це проста «кооперативна багатозадачність» без жодної операційної системи.", 9.5, GREY, "middle")
    save("fig-24-5-5-multiple-tasks.svg", s)


# ── Рис. 24.5.6 — коли delay усе ж можна ─────────────────────────────────────
def fig56_when_delay_ok():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 32, "Коли delay() усе ж припустимий, а коли — ні", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "delay не «заборонений» — він просто блокує; інколи блокувати нічого", 11, GREY, "middle", style="italic")
    s += rect(50, 90, 410, 220, "#f3faf4", GREEN, 1.8, 12)
    s += text(255, 116, "delay() припустимий", 12.5, GREEN, "middle", "bold")
    for i, c in enumerate(["крихітні паузи в setup()", "найпростіший навчальний скетч", "коли в програмі лиш одне діло", "коротка пауза, де нічого не чекає"]):
        s += text(72, 150 + i * 34, "✓ " + c, 10.5, INK, "start")
    s += rect(480, 90, 410, 220, "#fdf2f2", RED, 1.8, 12)
    s += text(685, 116, "delay() — зло", 12.5, RED, "middle", "bold")
    for i, c in enumerate(["треба читати кнопки/входи", "кілька справ із різним ритмом", "пристрій має лишатись чуйним", "будь-що серйозне й «живе»"]):
        s += text(502, 150 + i * 34, "✗ " + c, 10.5, INK, "start")
    s += text(W / 2, 340, "Правило: сумніваєшся — пиши неблокуюче. Звичка до millis-патерну окупається завжди.", 10.5, INK, "middle", "bold")
    save("fig-24-5-6-when-delay-ok.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §24.6 Періодичні події й планування — fig-24-6-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 24.6.1 — таблиця задач (розклад) ────────────────────────────────────
def fig61_task_table():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Розклад: таблиця задач, у кожної свій період", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "замість купи окремих if — один список «що, як часто й коли востаннє»", 11, GREY, "middle", style="italic")
    cols = [(80, "задача", 230), (320, "період", 140), (470, "востаннє", 150), (630, "дія", 250)]
    for x, t, w in cols:
        s += rect(x, 90, w, 34, "#eef1f8", BLUE, 1.4, 6)
        s += text(x + w / 2, 113, t, 11, BLUE, "middle", "bold")
    rows = [("блимати LED", "500 мс", "t1", "toggleLed()", GREEN),
            ("опитати давач", "100 мс", "t2", "readSensor()", BLUE),
            ("оновити екран", "1000 мс", "t3", "updateLcd()", GOLD)]
    y = 130
    for name, per, last, act, col in rows:
        s += rect(80, y, 230, 38, "#fbfcff", col, 1.2, 5)
        s += text(95, y + 24, name, 11, INK, "start", "bold")
        s += rect(320, y, 140, 38, "#fff", GREY, 1.2, 5)
        s += text(390, y + 24, per, 11, "#8a6a14", "middle", "bold")
        s += rect(470, y, 150, 38, "#fff", GREY, 1.2, 5)
        s += text(545, y + 24, last, 11, INK, "middle")
        s += rect(630, y, 250, 38, "#fff", GREY, 1.2, 5)
        s += text(645, y + 24, act, 10.5, INK, "start")
        y += 46
    s += rect(150, 300, 660, 70, LAMB, GOLD, 1.4, 10)
    s += text(480, 326, "Кожен рядок — окрема періодична задача. Цикл лише перебирає таблицю", 10.3, INK, "middle", "bold")
    s += text(480, 348, "й запускає ті, чий час настав. Це і є найпростіший планувальник.", 9.7, GREY, "middle")
    save("fig-24-6-1-task-table.svg", s)


# ── Рис. 24.6.2 — цикл-планувальник ──────────────────────────────────────────
def fig62_scheduler_loop():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Планувальник: цикл перебирає задачі й запускає «дозрілі»", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "один прохід по таблиці замінює десяток окремих if — і легко додавати нові задачі", 11, GREY, "middle", style="italic")
    s += rect(120, 90, 720, 150, "#0f1115", INK, 1.6, 10)
    s += '<text x="140" y="120" font-family="Consolas, monospace" font-size="14" fill="#e8e8e8">void loop() {</text>\n'
    s += '<text x="140" y="146" font-family="Consolas, monospace" font-size="14" fill="#e8e8e8">  unsigned long now = millis();</text>\n'
    s += '<text x="140" y="172" font-family="Consolas, monospace" font-size="14" fill="#7fb4ff">  for (Task &amp;t : tasks)</text>\n'
    s += '<text x="140" y="198" font-family="Consolas, monospace" font-size="14" fill="#e8e8e8">    if (now - t.last &gt;= t.period) {</text>\n'
    s += '<text x="140" y="224" font-family="Consolas, monospace" font-size="14" fill="#7ee0a0">      t.last += t.period;  t.run(); }</text>\n'
    s += '<text x="640" y="224" font-family="Consolas, monospace" font-size="14" fill="#caa24a">// дозріла → пуск</text>\n'
    s += text(480, 280, "Додати нову періодичну справу = додати рядок у таблицю tasks.", 11, INK, "middle", "bold")
    s += text(480, 304, "Жодного delay, жодного дублювання — чистий, масштабований розклад.", 10, GREY, "middle")
    s += rect(180, 330, 600, 50, LAMB, GOLD, 1.4, 10)
    s += text(480, 356, "Це вже «фреймворк часу»: маленький планувальник на millis() для багатьох задач.", 10.3, INK, "middle", "bold")
    s += text(480, 374, "Простий, передбачуваний, без операційної системи.", 9.5, GREY, "middle")
    save("fig-24-6-2-scheduler-loop.svg", s)


# ── Рис. 24.6.3 — кооперативність: довга задача затримує інших ────────────────
def fig63_cooperative_limit():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Межа кооперативності: довга задача затримує всіх", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "планувальник на millis НЕ витісняє — кожна задача має добігти сама, тож має бути короткою", 10.5, GREY, "middle", style="italic")
    ox, oy = 90, 170
    s += arrow(ox, oy, 880, oy, INK, 2)
    s += rect(140, oy - 16, 90, 32, LGRN, GREEN, 1.6, 5)
    s += text(185, oy + 6, "A коротка", 8.7, INK, "middle", "bold")
    s += rect(250, oy - 16, 320, 32, LRED, RED, 1.6, 5)
    s += text(410, oy + 6, "B — ДОВГА (блокує)", 10, RED, "middle", "bold")
    s += rect(590, oy - 16, 90, 32, LBLUE, BLUE, 1.6, 5)
    s += text(635, oy + 6, "C", 9, INK, "middle", "bold")
    # C was due earlier
    s += circle(330, 250, 5, GOLD, GOLD, 0)
    s += text(330, 272, "C мала спрацювати тут", 9, "#8a6a14", "middle", "bold")
    s += line(330, 244, 330, oy + 16, GOLD, 1.4, dash="3,3")
    s += arrow(330, 240, 590, 240, GOLD, 2)
    s += text(620, 244, "…а дочекалась аж тут (B тримала час)", 9, "#8a6a14", "start", "bold")
    s += rect(150, 300, 660, 56, LAMB, GOLD, 1.4, 10)
    s += text(480, 326, "Жодна задача нікого не перебиває — лише чемно чекає черги. Тому кожна МУСИТЬ бути", 10, INK, "middle", "bold")
    s += text(480, 346, "короткою (як ISR §23.3): одна «жадібна» задача псує таймінг усіх інших.", 9.7, GREY, "middle")
    save("fig-24-6-3-cooperative-limit.svg", s)


# ── Рис. 24.6.4 — м'який проти жорсткого реального часу ───────────────────────
def fig64_soft_vs_hard():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "М'який і жорсткий реальний час: чи страшно спізнитися", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "скрізь є строки (дедлайни); питання в тому, що буде, як їх пропустити", 11, GREY, "middle", style="italic")
    s += rect(50, 90, 410, 230, "#eef6ef", GREEN, 1.8, 12)
    s += text(255, 116, "М'який реальний час", 12.5, GREEN, "middle", "bold")
    s += text(72, 146, "пропуск строку — НЕ катастрофа,", 10.5, INK, "start")
    s += text(72, 166, "лише трохи гірша якість", 10.5, INK, "start")
    for i, c in enumerate(["блимання індикатора", "оновлення дисплея", "логування, опитування"]):
        s += text(72, 198 + i * 28, "• " + c, 10, INK, "start")
    s += text(255, 300, "millis-планувальник — саме сюди", 9.5, GREEN, "middle", "bold")
    s += rect(480, 90, 410, 230, "#fdf2f2", RED, 1.8, 12)
    s += text(685, 116, "Жорсткий реальний час", 12.5, RED, "middle", "bold")
    s += text(502, 146, "пропуск строку — ВІДМОВА,", 10.5, INK, "start")
    s += text(502, 166, "інколи з небезпекою", 10.5, INK, "start")
    for i, c in enumerate(["крок двигуна точно в строк", "подушка безпеки", "керування реактором"]):
        s += text(502, 198 + i * 28, "• " + c, 10, INK, "start")
    s += text(685, 300, "потрібні апаратні таймери / RTOS", 9.5, RED, "middle", "bold")
    save("fig-24-6-4-soft-vs-hard.svg", s)


# ── Рис. 24.6.5 — системний тік ──────────────────────────────────────────────
def fig65_system_tick():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Системний «тік»: переривання таймера задає ритм планувальнику", 16.5, INK, "middle", "bold")
    s += text(W / 2, 54, "таймер б'є перериманням рівно (напр., щомілісекунди), а лічильник тіків керує задачами", 10.5, GREY, "middle", style="italic")
    ox, oy = 90, 150
    s += arrow(ox, oy, 880, oy, INK, 2)
    for i in range(9):
        x = ox + 40 + i * 95
        s += line(x, oy - 18, x, oy, RED, 2.2)
        s += text(x, oy - 24, "↯", 11, RED, "middle", "bold")
        s += text(x, oy + 18, str(i + 1), 9, INK, "middle")
    s += text(470, oy - 44, "тіки таймера (рівні, апаратні)", 10, RED, "middle", "bold")
    s += text(64, oy + 18, "№:", 9, INK, "end")
    # tasks on multiples
    s += rect(140, 230, 680, 70, "none", FAINT, 1.6, 10)
    s += text(480, 254, "задача A — кожен тік;  B — кожен 5-й;  C — кожен 100-й", 11, INK, "middle", "bold")
    s += text(480, 278, "планувальник лише дивиться на лічильник тіків і запускає, що настало.", 9.7, GREY, "middle")
    s += text(W / 2, 340, "Цей «системний тік» — серце операційної системи реального часу (далі в курсі).", 10.3, INK, "middle", "bold")
    s += text(W / 2, 362, "Той самий принцип, що в дільнику Маррісона: рівний тік + лічба = розклад подій.", 9.5, GREY, "middle")
    save("fig-24-6-5-system-tick.svg", s)


# ── Рис. 24.6.6 — до RTOS ────────────────────────────────────────────────────
def fig66_toward_rtos():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Куди це веде: від суперциклу до справжнього планувальника", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "кооперативний розклад на millis — перший щабель; наступний — витісняюча RTOS", 10.5, GREY, "middle", style="italic")
    s += rect(50, 90, 410, 220, "#fff8e8", GOLD, 1.8, 12)
    s += text(255, 116, "Суперцикл на millis (тут)", 12, "#8a6a14", "middle", "bold")
    for i, c in enumerate(["задачі чемно чекають черги", "кожна мусить бути короткою", "немає витіснення", "просто, передбачувано", "досить для м'якого реального часу"]):
        s += text(72, 148 + i * 30, "• " + c, 10, INK, "start")
    s += rect(480, 90, 410, 220, "#eef6ef", GREEN, 1.8, 12)
    s += text(685, 116, "RTOS (далі в курсі)", 12, GREEN, "middle", "bold")
    for i, c in enumerate(["планувальник може ВИТІСНИТИ задачу", "пріоритети, як у переривань", "довга задача не блокує термінову", "складніше, зате потужніше", "для жорсткіших вимог"]):
        s += text(502, 148 + i * 30, "• " + c, 10, INK, "start")
    s += text(W / 2, 348, "Опанувавши неблокуючий розклад, ви вже мислите як планувальник — і RTOS дасться легко.", 10.3, INK, "middle", "bold")
    save("fig-24-6-6-toward-rtos.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §24.7 Watchdog — fig-24-7-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 24.7.1 — проблема зависання ─────────────────────────────────────────
def fig71_hang_problem():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Проблема: прошивка зависла — і пристрій мертвий", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "вічний цикл, глухий кут, очікування пристрою, що не відповідає — і програма стоїть назавжди", 10.5, GREY, "middle", style="italic")
    ox, oy = 120, 180
    s += text(64, 160, "loop()", 10, INK, "start", "bold")
    s += line(ox, oy, 320, oy, GREEN, 3)
    s += circle(330, oy, 8, RED, RED, 0)
    s += text(330, oy - 18, "тут завис", 9.5, RED, "middle", "bold")
    # frozen loop arrow
    s += f'<path d="M 360 180 a 40 40 0 1 1 -1 0" fill="none" stroke="{RED}" stroke-width="3" marker-end="url(#aRed)"/>\n'
    s += text(400, 250, "крутиться вічно", 10, RED, "middle", "bold")
    s += text(400, 268, "(або стоїть)", 9, GREY, "middle")
    s += rect(560, 130, 320, 110, "none", FAINT, 1.6, 12)
    s += text(720, 156, "Наслідки:", 11, INK, "middle", "bold")
    s += text(576, 182, "• не реагує ні на що", 10, INK, "start")
    s += text(576, 204, "• допомогти може лише перезапуск", 10, INK, "start")
    s += text(576, 226, "• а пристрій часто НЕДОСЯЖНИЙ", 10, RED, "start", "bold")
    s += rect(150, 310, 640, 50, LAMB, GOLD, 1.4, 10)
    s += text(470, 336, "Датчик на горі, у стіні, в космосі — руками не перезавантажиш. Потрібен автоматичний рятівник.", 10, INK, "middle", "bold")
    save("fig-24-7-1-hang-problem.svg", s)


# ── Рис. 24.7.2 — як працює watchdog ─────────────────────────────────────────
def fig72_watchdog_concept():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Watchdog: таймер, що скине чип, якщо його вчасно не «погодувати»", 16.5, INK, "middle", "bold")
    s += text(W / 2, 54, "сторожовий таймер відлічує вниз; програма раз у раз скидає його, доводячи «я живий»", 10.5, GREY, "middle", style="italic")
    # healthy
    s += rect(50, 84, 410, 150, "#f3faf4", GREEN, 1.8, 12)
    s += text(255, 110, "Живий: годуємо вчасно", 11.5, GREEN, "middle", "bold")
    ox, oy = 70, 190
    s += arrow(ox, oy, 440, oy, INK, 1.6)
    for i in range(4):
        x = ox + 30 + i * 95
        s += poly([(x - 20, oy), (x - 20, oy - 30), (x, oy)], GREEN, 2)
        s += arrow(x, oy - 32, x, oy - 8, GREEN, 1.6)
        s += text(x, oy - 38, "год.", 7.5, GREEN, "middle", "bold")
    s += text(255, 220, "лічильник не доходить до 0 → усе гаразд", 9, INK, "middle")
    # hung
    s += rect(500, 84, 410, 150, "#fdf2f2", RED, 1.8, 12)
    s += text(705, 110, "Завис: годувати нікому", 11.5, RED, "middle", "bold")
    bx, by = 520, 190
    s += arrow(bx, by, 890, by, INK, 1.6)
    s += poly([(bx + 10, by), (bx + 10, by - 30), (bx + 50, by)], GREEN, 2)
    s += text(bx + 30, by - 36, "год.", 7.5, GREEN, "middle")
    s += poly([(bx + 50, by - 5), (bx + 320, by - 25)], RED, 2.4)
    s += text(bx + 220, by - 30, "не годують…", 8.5, RED, "middle", "bold")
    s += circle(bx + 330, by - 25, 5, RED, RED, 0)
    s += text(bx + 330, by - 38, "0 → СКИД", 9, RED, "middle", "bold")
    s += text(705, 222, "лічильник доходить до 0 → чип перезавантажується", 8.6, INK, "middle")
    s += rect(150, 300, 660, 70, LAMB, GOLD, 1.4, 10)
    s += text(480, 326, "«Погодувати» (feed / kick) = скинути лічильник watchdog назад до старту.", 10.3, INK, "middle", "bold")
    s += text(480, 348, "Поки програма крутиться — вона годує; зависла — годувати нікому, і чип сам рятує себе скидом.", 9.5, GREY, "middle")
    save("fig-24-7-2-watchdog-concept.svg", s)


# ── Рис. 24.7.3 — аналогія: запобіжник машиніста ─────────────────────────────
def fig73_deadmans_switch():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 32, "Аналогія: «запобіжник пильності» машиніста", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "машиніст мусить раз у раз натискати педаль; знепритомнів — поїзд сам зупиняється", 11, GREY, "middle", style="italic")
    s += rect(80, 100, 360, 180, "none", GREEN, 1.8, 12)
    s += text(260, 126, "Усе гаразд", 12, GREEN, "middle", "bold")
    s += circle(180, 180, 26, "#ffe0c0", INK, 1.6)
    s += text(180, 186, "машиніст", 8.5, INK, "middle")
    s += arrow(180, 218, 180, 244, GREEN, 2)
    s += rect(150, 244, 60, 24, LGRN, GREEN, 1.4, 5)
    s += text(180, 261, "педаль", 8, INK, "middle")
    s += text(330, 180, "натискає", 10, GREEN, "middle", "bold")
    s += text(330, 198, "вчасно →", 10, INK, "middle")
    s += text(330, 220, "поїзд їде", 10, GREEN, "middle", "bold")
    s += rect(500, 100, 360, 180, "none", RED, 1.8, 12)
    s += text(680, 126, "Машиніст знепритомнів", 11.5, RED, "middle", "bold")
    s += circle(600, 180, 26, "#f0d0d0", RED, 1.6)
    s += text(600, 186, "✗", 16, RED, "middle", "bold")
    s += text(760, 178, "педаль", 10, RED, "middle")
    s += text(760, 196, "відпущено →", 10, INK, "middle")
    s += text(760, 218, "ПОЇЗД СТАЄ", 10.5, RED, "middle", "bold")
    s += text(W / 2, 326, "Watchdog — це той самий «запобіжник пильності» для прошивки:", 11, INK, "middle", "bold")
    s += text(W / 2, 348, "годуєш регулярно — живеш; перестав (завис) — система сама себе перезапускає.", 9.7, GREY, "middle")
    save("fig-24-7-3-deadmans-switch.svg", s)


# ── Рис. 24.7.4 — де годувати правильно ──────────────────────────────────────
def fig74_feed_correctly():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Де годувати: тільки там, де це ДОВОДИТЬ поступ", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "годувати треба як доказ «я просуваюся», а не сліпо — інакше watchdog утратить сенс", 10.5, GREY, "middle", style="italic")
    s += rect(50, 84, 410, 250, "#f3faf4", GREEN, 1.8, 12)
    s += text(255, 110, "ПРАВИЛЬНО", 12.5, GREEN, "middle", "bold")
    s += text(72, 140, "годувати в кінці головного циклу,", 10, INK, "start")
    s += text(72, 160, "коли він дійшов донизу здоровим", 10, INK, "start")
    s += text(72, 192, "loop() {", 10, INK, "start")
    s += text(92, 212, "...уся робота...", 10, GREY, "start")
    s += text(92, 232, "feedWatchdog();  // дійшли!", 10, GREEN, "start", "bold")
    s += text(72, 252, "}", 10, INK, "start")
    s += text(255, 296, "завис десь усередині → не нагодує → скид ✓", 9, INK, "middle")
    s += rect(500, 84, 410, 250, "#fdf2f2", RED, 1.8, 12)
    s += text(705, 110, "НЕПРАВИЛЬНО", 12.5, RED, "middle", "bold")
    s += text(522, 140, "годувати в окремому перериванні", 10, INK, "start")
    s += text(522, 160, "таймера, що тікає завжди", 10, INK, "start")
    s += text(522, 192, "ISR_таймера() {", 10, INK, "start")
    s += text(542, 212, "feedWatchdog();  // байдуже", 10, RED, "start", "bold")
    s += text(542, 232, "до стану loop()!", 10, RED, "start")
    s += text(522, 252, "}", 10, INK, "start")
    s += text(705, 296, "loop завис, а годівля йде → скиду НЕ буде ✗", 9, INK, "middle")
    s += text(W / 2, 360, "Годівля має бути ОЗНАКОЮ життя програми, а не автоматичним цоканням збоку.", 10.3, INK, "middle", "bold")
    save("fig-24-7-4-feed-correctly.svg", s)


# ── Рис. 24.7.5 — спершу переривання, потім скид ─────────────────────────────
def fig75_interrupt_then_reset():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 32, "Часто watchdog спершу попереджає, а вже потім скидає", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "коротке переривання дає шанс зберегти стан чи записати причину — і лише тоді reset", 10.5, GREY, "middle", style="italic")
    ox, oy = 90, 170
    s += arrow(ox, oy, 880, oy, INK, 2)
    s += poly([(ox, oy - 70), (350, oy)], RED, 2.4)
    s += text(150, oy - 50, "лічильник вниз (не годують)", 9, RED, "start")
    s += circle(350, oy, 5, GOLD, GOLD, 0)
    s += arrow(350, oy, 350, oy - 40, GOLD, 2)
    s += rect(270, oy - 80, 160, 36, LAMB, GOLD, 1.6, 8)
    s += text(350, oy - 57, "1) переривання-", 9, "#8a6a14", "middle", "bold")
    s += text(350, oy - 45, "попередження", 9, "#8a6a14", "middle")
    s += text(350, oy + 24, "(зберегти стан, лог)", 8.5, GREY, "middle")
    s += line(350, oy, 600, oy, GREY, 2, "4,3")
    s += circle(600, oy, 6, RED, RED, 0)
    s += arrow(600, oy, 600, oy - 40, RED, 2)
    s += rect(530, oy - 78, 140, 34, LRED, RED, 1.6, 8)
    s += text(600, oy - 56, "2) СКИД чипа", 10, RED, "middle", "bold")
    s += line(600, oy, 850, oy, GREEN, 2.4)
    s += text(740, oy - 8, "→ чистий старт", 9.5, GREEN, "middle", "bold")
    s += text(W / 2, 330, "Так пристрій не лише оживає, а й може лишити «передсмертну записку» — чому завис.", 10.3, INK, "middle", "bold")
    save("fig-24-7-5-interrupt-then-reset.svg", s)


# ── Рис. 24.7.6 — watchdog в ESP32 ───────────────────────────────────────────
def fig76_esp32_watchdog():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Watchdog у ESP32: сторож для задач і для переривань", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "два сторожі стережуть різні види зависань; навіть Arduino-скетч під їхнім наглядом", 10.5, GREY, "middle", style="italic")
    s += rect(60, 90, 410, 180, "none", BLUE, 1.8, 12)
    s += text(265, 116, "Task WDT (задачний)", 12, BLUE, "middle", "bold")
    s += text(80, 144, "стежить, чи задачі дістають час", 10, INK, "start")
    s += text(80, 166, "якщо задача (чи loop) надовго", 10, INK, "start")
    s += text(80, 186, "«захопила» ядро — скид", 10, INK, "start")
    s += text(80, 216, "→ ось чому довгий loop без", 9.3, GREEN, "start", "bold")
    s += text(96, 234, "delay/yield інколи «падає»", 9.3, GREEN, "start")
    s += rect(490, 90, 410, 180, "none", RED, 1.8, 12)
    s += text(695, 116, "Interrupt WDT (перерив.)", 12, RED, "middle", "bold")
    s += text(510, 144, "стежить, чи переривання не", 10, INK, "start")
    s += text(510, 166, "вимкнені занадто довго", 10, INK, "start")
    s += text(510, 186, "(довга критична секція §23.6", 10, INK, "start")
    s += text(510, 206, "чи завислий обробник)", 10, INK, "start")
    s += text(510, 236, "→ ловить «німі» зависання в ISR", 9.3, RED, "start", "bold")
    s += rect(150, 295, 660, 70, LAMB, GOLD, 1.4, 10)
    s += text(480, 321, "У коді: увімкнути watchdog із таймаутом і регулярно годувати (esp_task_wdt_reset).", 10.3, INK, "middle", "bold")
    s += text(480, 343, "Таймаут беруть більший за найдовшу чесну операцію — щоб не було хибних скидів.", 9.7, GREY, "middle")
    save("fig-24-7-6-esp32-watchdog.svg", s)


if __name__ == "__main__":
    # Історія розділу (📜)
    fig01_what_is_tick()
    fig02_piezo()
    fig03_oscillator()
    fig04_marrison_clock()
    fig05_legacy()
    # §24.1 Таймер-лічильник
    fig11_counter_register()
    fig12_independent()
    fig13_clock_prescaler()
    fig14_count_is_time()
    fig15_resolution_range()
    fig16_esp32_timer()
    # §24.2 Період і переповнення
    fig21_overflow()
    fig22_overflow_interrupt()
    fig23_period_reload()
    fig24_period_formula()
    fig25_choosing()
    fig26_millis_wraparound()
    # §24.3 Захоплення й порівняння
    fig31_capture_concept()
    fig32_capture_measure()
    fig33_compare_concept()
    fig34_compare_waveform()
    fig35_hw_vs_sw()
    fig36_esp32_peripherals()
    # §24.4 millis/micros зсередини
    fig41_what_they_return()
    fig42_avr_internals()
    fig43_esp32_internals()
    fig44_resolution()
    fig45_accuracy_crystal()
    fig46_usage()
    # §24.5 Чому delay() — зло
    fig51_delay_blocks()
    fig52_two_things()
    fig53_nonblocking_pattern()
    fig54_loop_spinning()
    fig55_multiple_tasks()
    fig56_when_delay_ok()
    # §24.6 Періодичні події й планування
    fig61_task_table()
    fig62_scheduler_loop()
    fig63_cooperative_limit()
    fig64_soft_vs_hard()
    fig65_system_tick()
    fig66_toward_rtos()
    # §24.7 Watchdog
    fig71_hang_problem()
    fig72_watchdog_concept()
    fig73_deadmans_switch()
    fig74_feed_correctly()
    fig75_interrupt_then_reset()
    fig76_esp32_watchdog()
    print("OK - figures for Section 24 (history + 24.1..24.7, complete) generated in", OUT)
