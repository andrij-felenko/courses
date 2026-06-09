# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 27 — «Модель виконання й RTOS» (Модуль 4).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи нумеруються посекційно
(Рис. C.S.N) у тексті розділу; історія до розділу — C.0.N.

Скрипт нарощується по ітераціях: кожна тема додає свої функції-фігури.
"""
import os
import math

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
PURP  = "#7a4fb0"
LPURP = "#efe9f7"
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
# 📜 Історія до розділу — поділ часу (CTSS, 1961) — fig-27-0-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 27.0.1 — головне питання: одна машина — багатьом ─────────────────────
def figh1_the_question():
    W, H = 960, 420
    s = header(W, H)
    s += text(W / 2, 32, "Питання, з якого почалися ОС: як одній машині служити багатьом?", 17, INK, "middle", "bold")
    s += text(W / 2, 54, "дорогий комп'ютер один, охочих рахувати — багато; хто має чекати?", 10.3, GREY, "middle", style="italic")
    # одна машина
    s += rect(420, 92, 120, 70, LBLUE, BLUE, 2, 10)
    s += text(480, 124, "ОДНА", 12, BLUE, "middle", "bold")
    s += text(480, 142, "машина", 10, INK, "middle")
    # варіант 1: черга (пакетно)
    s += text(160, 210, "Пакетно: усі чекають у черзі", 11, RED, "middle", "bold")
    for i in range(4):
        s += rect(60 + i * 56, 230, 44, 40, LRED, RED, 1.4, 6)
        s += text(82 + i * 56, 255, "№" + str(i + 1), 9, RED, "middle", "bold")
    s += text(160, 296, "один рахує — троє нудяться годинами", 9, GREY, "middle")
    # варіант 2: поділ часу
    s += text(760, 210, "Поділ часу: швидко по черзі — усім «одразу»", 10.5, GREEN, "middle", "bold")
    for i in range(4):
        s += rect(620 + i * 56, 230, 44, 40, LGRN, GREEN, 1.4, 6)
        s += text(642 + i * 56, 255, "№" + str(i + 1), 9, GREEN, "middle", "bold")
    s += text(760, 296, "кожному — крихітний шматочок часу, дуже часто", 9, GREY, "middle")
    s += arrow(540, 120, 620, 230, GREEN, 1.6, dash="4,3")
    s += arrow(420, 120, 340, 230, RED, 1.6, dash="4,3")
    s += rect(150, 330, 660, 70, LAMB, GOLD, 1.5, 12)
    s += text(480, 356, "Розв'язок виявився хитрим: перемикатися між людьми так ШВИДКО,", 11, INK, "middle", "bold")
    s += text(480, 378, "щоб кожному здавалося, ніби велика машина належить тільки йому.", 11, INK, "middle", "bold")
    s += text(480, 394, "Цю ілюзію й назвали поділом часу (time-sharing).", 9, GREY, "middle")
    save("fig-27-0-1-the-question.svg", s)


# ── Рис. 27.0.2 — від пакетної до поділу часу: завантаження процесора ─────────
def figh2_utilization():
    W, H = 960, 420
    s = header(W, H)
    s += text(W / 2, 30, "Не марнувати простій: пакетна → мультипрограмування → поділ часу", 16, INK, "middle", "bold")
    s += text(W / 2, 52, "як крок за кроком навчилися заповнювати «дірки», коли процесор чекає на повільне введення-виведення", 9.6, GREY, "middle", style="italic")
    rows = [
        ("Пакетно", 88, [("A", 0, 0.18, BLUE), ("очікує В/В", 0.18, 0.45, FAINT), ("B", 0.45, 0.62, GREEN), ("очікує В/В", 0.62, 0.9, FAINT)], "процесор простоює, поки йде повільне В/В"),
        ("Мультипрограмування", 200, [("A", 0, 0.18, BLUE), ("B", 0.18, 0.45, GREEN), ("A", 0.45, 0.6, BLUE), ("C", 0.6, 0.82, PURP), ("B", 0.82, 1.0, GREEN)], "поки A чекає В/В — рахуємо B; дірки заповнено"),
        ("Поділ часу", 312, [(c, i * 0.1, (i + 1) * 0.1, [BLUE, GREEN, PURP][i % 3]) for i, c in enumerate("ABCABCABCA")], "ще й дрібно нарізано — кожен інтерактивний"),
    ]
    ox, bw = 230, 640
    for lab, y, segs, note in rows:
        s += text(ox - 14, y + 22, lab, 10.5, INK, "end", "bold")
        for seg in segs:
            c, a, b, col = seg
            s += rect(ox + bw * a, y, bw * (b - a), 32, col if col != FAINT else FAINT, INK, 0.8)
            if b - a > 0.05 and col != FAINT:
                s += text(ox + bw * (a + b) / 2, y + 21, c, 9.5, "#ffffff", "middle", "bold")
        s += text(ox + bw / 2, y + 52, note, 9, GREY, "middle")
    s += text(ox + bw / 2, 384, "Сіре — змарнований простій процесора. Що тонше нарізаєш — то «живіша» машина для кожного.", 9.4, INK, "middle", "bold")
    save("fig-27-0-2-utilization.svg", s)


# ── Рис. 27.0.3 — стрічка часу ───────────────────────────────────────────────
def figh3_timeline():
    W, H = 980, 360
    s = header(W, H)
    s += text(W / 2, 30, "Від ідеї до всюдисущості: стрічка поділу часу", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "дві незалежні ідеї 1959-го, перша жива система 1961-го — і далі до кожного пристрою", 10, GREY, "middle", style="italic")
    ax = 210
    x0, x1 = 70, 910
    s += line(x0, ax, x1, ax, INK, 2.4)
    for yr in range(1955, 1976, 5):
        x = x0 + (x1 - x0) * (yr - 1955) / (1972 - 1955)
        s += line(x, ax - 5, x, ax + 5, GREY, 1.4)
        s += text(x, ax + 22, str(yr), 9, GREY, "middle")

    def xof(yr):
        return x0 + (x1 - x0) * (yr - 1955) / (1972 - 1955)

    miles = [
        (1959, "1959  Маккарті й Стрейчі", "США / Британія · дві ідеї нарізно", BLUE, True, 0),
        (1961, "1961  CTSS ★", "MIT, Корбато — перша жива система", RED, False, 0),
        (1965, "1965  Multics", "велика ОС поділу часу", GOLD, True, 1),
        (1969, "1969  Unix", "Bell Labs — поділ часу всюди", GREEN, False, 0),
    ]
    for yr, nm, sub, col, above, lvl in miles:
        x = xof(yr)
        s += circle(x, ax, 6, col, col, 0)
        if above:
            box_y = ax - 44 - lvl * 64
            s += line(x, ax - 6, x, box_y + 44, col, 1.6)
        else:
            box_y = ax + 42 + lvl * 64
            s += line(x, ax + 6, x, box_y, col, 1.6)
        bw, bh = 210, 44
        bx = min(max(x - bw / 2, 6), W - bw - 6)
        s += rect(bx, box_y, bw, bh, "#ffffff", col, 1.8, 8)
        s += text(bx + bw / 2, box_y + 19, nm, 10.5, col, "middle", "bold")
        s += text(bx + bw / 2, box_y + 35, sub, 8.4, INK, "middle")
    s += text(W / 2, 338, "★ CTSS (1961) — перша загального призначення система поділу часу; команда: Корбато, Маржорі Дагґетт, Роберт Дейлі.", 9, RED, "middle", "bold")
    save("fig-27-0-3-timeline.svg", s)


# ── Рис. 27.0.4 — механізм: планувальник, квант, перемикання контексту ────────
def figh4_mechanism():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 30, "Як працює ілюзія: планувальник + квант + перемикання контексту", 16, INK, "middle", "bold")
    s += text(W / 2, 52, "один процесор по черзі віддає крихітні «кванти» задачам, зберігаючи й відновлюючи їхній стан", 9.6, GREY, "middle", style="italic")
    # таймлайн одного процесора
    ox, y, bw = 80, 110, 800
    tasks = [("A", BLUE), ("B", GREEN), ("C", PURP), ("A", BLUE), ("B", GREEN), ("C", PURP), ("A", BLUE), ("B", GREEN)]
    n = len(tasks)
    for i, (c, col) in enumerate(tasks):
        x = ox + bw * i / n
        s += rect(x, y, bw / n - 4, 40, col, INK, 0.8, 3)
        s += text(x + (bw / n - 4) / 2, y + 26, c, 11, "#ffffff", "middle", "bold")
        if i > 0:
            s += line(x - 2, y - 6, x - 2, y + 46, RED, 1.6)
    s += text(ox, y - 14, "час процесора →", 9.5, INK, "start", "bold")
    s += text(ox + bw + 6, y + 26, "...", 12, INK, "start", "bold")
    s += text(ox + bw / 2, y + 64, "червоні риски — «тік» таймера: мить перемкнутися (квант ≈ мілісекунди)", 9, RED, "middle", "bold")
    # блок перемикання контексту
    s += rect(120, 200, 320, 150, LBLUE, BLUE, 1.6, 12)
    s += text(280, 226, "Перемикання контексту", 11, BLUE, "middle", "bold")
    s += text(140, 254, "1. зберегти стан задачі A", 9.6, INK, "start")
    s += text(155, 272, "(регістри, лічильник команд, стек)", 8.4, GREY, "start")
    s += text(140, 298, "2. вибрати наступну (планувальник)", 9.6, INK, "start")
    s += text(140, 324, "3. відновити стан задачі B → бігти", 9.6, INK, "start")
    # звідки «тік»
    s += rect(540, 200, 340, 150, LAMB, GOLD, 1.6, 12)
    s += text(710, 226, "Звідки «тік»?", 11, GOLD, "middle", "bold")
    s += text(560, 256, "Таймер (Розділ 24) цокає через рівні", 9.6, INK, "start")
    s += text(560, 274, "проміжки й перериванням (Розділ 23)", 9.6, INK, "start")
    s += text(560, 292, "змушує процесор перемкнутися.", 9.6, INK, "start")
    s += text(560, 320, "Це і є витіснення (preemption):", 9.4, RED, "start", "bold")
    s += text(560, 338, "задачу спиняють, не питаючи її згоди.", 9.2, GREY, "start")
    save("fig-27-0-4-mechanism.svg", s)


# ── Рис. 27.0.5 — спадок: від залу до чипа (RTOS) ────────────────────────────
def figh5_legacy():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 30, "Спадок: та сама ідея 1961 року — тепер у твоєму чипі", 17, INK, "middle", "bold")
    s += text(W / 2, 52, "поділ часу зменшився від машинного залу до RTOS на мікроконтролері", 10, GREY, "middle", style="italic")
    # 1961 mainframe
    s += rect(70, 110, 200, 150, LBLUE, BLUE, 2, 12)
    s += text(170, 138, "1961: CTSS", 12, BLUE, "middle", "bold")
    s += text(170, 162, "машинний зал", 9.5, INK, "middle")
    s += text(170, 182, "багато людей", 9, GREY, "middle")
    s += text(170, 200, "один процесор", 9, GREY, "middle")
    s += text(170, 230, "планувальник +", 8.8, INK, "middle")
    s += text(170, 245, "перемикання контексту", 8.8, INK, "middle")
    s += arrow(280, 185, 400, 185, INK, 2.4)
    s += text(340, 175, "та сама ідея,", 9, GREEN, "middle", "bold")
    s += text(340, 200, "менший масштаб", 9, GREY, "middle")
    # сьогодні ESP32
    s += rect(430, 110, 200, 150, LGRN, GREEN, 2, 12)
    s += text(530, 138, "сьогодні: RTOS", 12, GREEN, "middle", "bold")
    s += text(530, 162, "чип ESP32", 9.5, INK, "middle")
    s += text(530, 182, "багато задач", 9, GREY, "middle")
    s += text(530, 200, "два ядра", 9, GREY, "middle")
    s += text(530, 230, "FreeRTOS:", 8.8, INK, "middle")
    s += text(530, 245, "ті самі планувальник + кванти", 8.4, INK, "middle")
    # відмінність — реальний час
    s += rect(670, 110, 230, 150, LAMB, GOLD, 1.6, 12)
    s += text(785, 136, "Що додалося:", 10.5, GOLD, "middle", "bold")
    s += text(688, 164, "реальний час —", 9.6, RED, "start", "bold")
    s += text(688, 182, "не лише «справедливо»,", 9.2, INK, "start")
    s += text(688, 198, "а й ВЧАСНО (до дедлайну).", 9.2, INK, "start")
    s += text(688, 224, "пріоритети задач,", 9.2, INK, "start")
    s += text(688, 240, "передбачувані затримки.", 9.2, INK, "start")
    s += rect(150, 300, 660, 50, LGRN, GREEN, 1.4, 10)
    s += text(480, 322, "Те, що колись займало цілий зал і служило людям, тепер живе в крихітному чипі", 9.6, INK, "middle", "bold")
    s += text(480, 340, "й керує задачами — це і є RTOS, тема цього розділу.", 9.2, GREY, "middle")
    save("fig-27-0-5-legacy.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §27.1 Super-loop — fig-27-1-k
# ═════════════════════════════════════════════════════════════════════════════

def _codebox(x, y, w, h, lines, title=None, col=GREY):
    s = rect(x, y, w, h, "#fbfcff", col, 1.4, 8)
    yy = y + 24
    if title:
        s += text(x + w / 2, yy, title, 10.5, col, "middle", "bold")
        yy += 22
    for ln in lines:
        s += text(x + 16, yy, ln, 11, INK, "start")
        yy += 20
    return s


# ── Рис. 27.1.1 — setup() раз, loop() вічно ──────────────────────────────────
def fig11_setup_loop():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 32, "Super-loop: setup() — раз, loop() — вічно", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "найпростіша модель виконання: одне налаштування, потім нескінченне повторення", 10.3, GREY, "middle", style="italic")
    s += circle(110, 180, 26, LGRN, GREEN, 2)
    s += text(110, 184, "старт", 9.5, GREEN, "middle", "bold")
    s += arrow(136, 180, 200, 180, INK, 2.2)
    s += rect(200, 150, 180, 60, LBLUE, BLUE, 1.8, 10)
    s += text(290, 178, "setup()", 13, BLUE, "middle", "bold")
    s += text(290, 197, "виконується ОДИН раз", 8.6, GREY, "middle")
    s += arrow(380, 180, 450, 180, INK, 2.2)
    s += rect(450, 150, 180, 60, LAMB, GOLD, 1.8, 10)
    s += text(540, 178, "loop()", 13, GOLD, "middle", "bold")
    s += text(540, 197, "повторюється БЕЗ КІНЦЯ", 8.6, GREY, "middle")
    # петля назад
    s += line(630, 180, 660, 180, INK, 2)
    s += line(660, 180, 660, 260, INK, 2)
    s += line(660, 260, 540, 260, INK, 2)
    s += arrow(540, 260, 540, 212, INK, 2)
    s += text(665, 250, "знову й знову", 9, GOLD, "start", "bold")
    s += _codebox(700, 130, 210, 110, ["void setup() {", "  // один раз", "}", "void loop() {", "  // знову й знову", "}"], col=GREY)
    s += rect(150, 300, 640, 44, LGRN, GREEN, 1.3, 9)
    s += text(470, 320, "Налаштував раз (піни, зв'язок), а тоді вічно крутиш робочий цикл.", 10, INK, "middle", "bold")
    s += text(470, 337, "Це модель Arduino — і найприродніший спосіб думати про мікроконтролер.", 9, GREY, "middle")
    save("fig-27-1-1-setup-loop.svg", s)


# ── Рис. 27.1.2 — що під капотом: main() з вічним циклом ──────────────────────
def fig12_under_hood():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 32, "Що під капотом: звичайний main() із вічним циклом", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "Arduino це ховає, та насправді є все знайоме з Розділу 21: скидання → завантажувач → main()", 9.8, GREY, "middle", style="italic")
    chain = [
        ("Скидання", LRED, RED),
        ("Завантажувач", LBLUE, BLUE),
        ("main()", LBLUE, BLUE),
        ("setup()", LGRN, GREEN),
        ("loop() ∞", LAMB, GOLD),
    ]
    x = 40
    for i, (lab, bg, col) in enumerate(chain):
        s += rect(x, 110, 150, 50, bg, col, 1.8, 9)
        s += text(x + 75, 140, lab, 11, col, "middle", "bold")
        if i < len(chain) - 1:
            s += arrow(x + 150, 135, x + 188, 135, INK, 2)
        x += 188
    s += text(40 + 75, 178, "(Розділ 21)", 8.4, GREY, "middle")
    s += _codebox(250, 210, 460, 130, ["int main() {", "    setup();           // раз", "    for (;;) {          // вічно", "        loop();", "    }", "}"], title="насправді в коді:", col=INK)
    s += rect(150, 320, 0, 0)  # spacer-free
    s += text(W / 2, 352, "«Super-loop» — це просто setup() один раз і loop() у нескінченному for(;;). Жодної магії.", 9.6, INK, "middle", "bold")
    save("fig-27-1-2-under-hood.svg", s)


# ── Рис. 27.1.3 — цикл «читай — обчисли — дій» ───────────────────────────────
def fig13_read_compute_act():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Класичний цикл: читай → обчисли → дій → знову", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "щооберту мікроконтролер опитує світ, думає й відповідає", 10.3, GREY, "middle", style="italic")
    cx, cy, r = 450, 230, 110
    nodes = [
        (cx, cy - r, "ЧИТАЙ входи", "давачі, кнопки", BLUE),
        (cx + r * 0.87, cy + r * 0.5, "ДІЙ на виходи", "LED, мотор, дані", RED),
        (cx - r * 0.87, cy + r * 0.5, "ОБЧИСЛИ", "логіка, рішення", GREEN),
    ]
    # стрілки по колу
    s += f'<path d="M {cx+44} {cy-r+10} A {r} {r} 0 0 1 {cx+r*0.87+8} {cy+r*0.5-34}" fill="none" stroke="{INK}" stroke-width="2.2" marker-end="url(#aInk)"/>\n'
    s += f'<path d="M {cx+r*0.87-40} {cy+r*0.5+28} A {r} {r} 0 0 1 {cx-r*0.87+40} {cy+r*0.5+28}" fill="none" stroke="{INK}" stroke-width="2.2" marker-end="url(#aInk)"/>\n'
    s += f'<path d="M {cx-r*0.87-8} {cy+r*0.5-34} A {r} {r} 0 0 1 {cx-44} {cy-r+10}" fill="none" stroke="{INK}" stroke-width="2.2" marker-end="url(#aInk)"/>\n'
    for nx, ny, t1, t2, col in nodes:
        s += circle(nx, ny, 50, "#fbfcff", col, 2)
        s += text(nx, ny - 2, t1, 10, col, "middle", "bold")
        s += text(nx, ny + 15, t2, 8.2, GREY, "middle")
    s += text(cx, cy + 4, "loop()", 12, GOLD, "middle", "bold")
    s += rect(150, 350, 600, 40, LBLUE, BLUE, 1.3, 9)
    s += text(450, 368, "Один прохід loop() = один такт «опитати → подумати → відповісти».", 9.8, INK, "middle", "bold")
    s += text(450, 384, "Просто, передбачувано, легко читати згори вниз.", 9, GREY, "middle")
    save("fig-27-1-3-read-compute-act.svg", s)


# ── Рис. 27.1.4 — дві сцени: головний цикл + переривання ─────────────────────
def fig14_foreground_background():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 32, "Дві сцени: головний цикл (рутина) + переривання (термінове)", 16.5, INK, "middle", "bold")
    s += text(W / 2, 54, "loop() робить неквапну роботу; ISR (Розділ 23) вихоплює процесор на термінові події", 9.8, GREY, "middle", style="italic")
    ox, y = 70, 150
    s += text(ox, y - 14, "час →", 9.5, INK, "start", "bold")
    s += line(ox, y, 880, y, FAINT, 1.2)
    # головний цикл — суцільна смуга
    for i in range(6):
        x = ox + i * 135
        s += rect(x, y, 120, 34, LAMB, GOLD, 1.2, 4)
        s += text(x + 60, y + 22, "loop()", 9.5, GOLD, "middle", "bold")
    # переривання — спайки згори
    for sx in [ox + 150, ox + 470, ox + 700]:
        s += line(sx, y, sx, y - 60, RED, 2.4)
        s += poly([(sx - 30, y - 60), (sx + 30, y - 60), (sx, y - 60), (sx, y)], RED, 0)
        s += rect(sx - 34, y - 86, 68, 26, LRED, RED, 1.4, 5)
        s += text(sx, y - 68, "ISR", 9.5, RED, "middle", "bold")
    s += text(ox + 150, y - 96, "термінова подія", 8.2, RED, "middle")
    s += rect(150, 250, 640, 92, "#fbfcff", GREY, 1.4, 10)
    s += text(470, 276, "Класична «передній план / тло»: рутину тягне цикл, а на термінове —", 10, INK, "middle", "bold")
    s += text(470, 296, "натискання, прихід байта, переповнення таймера — миттєво відгукується ISR.", 10, INK, "middle", "bold")
    s += text(470, 322, "Так навіть простий super-loop устигає й за повільним, і за швидким (Розділ 23).", 9.2, GREY, "middle")
    save("fig-27-1-4-foreground-background.svg", s)


# ── Рис. 27.1.5 — як швидко крутиться цикл ───────────────────────────────────
def fig15_loop_timing():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 32, "Цикл крутиться так швидко, як дозволяє найповільніший крок", 16.5, INK, "middle", "bold")
    s += text(W / 2, 54, "короткий loop() — мільйони обертів за секунду; один довгий крок розтягує весь оберт", 9.8, GREY, "middle", style="italic")
    # короткий цикл
    ox = 80
    s += text(ox, 110, "короткий loop(): багато швидких обертів", 10, GREEN, "start", "bold")
    for i in range(12):
        x = ox + i * 60
        s += rect(x, 124, 50, 28, LGRN, GREEN, 1.2, 3)
    s += text(ox, 174, "кожен оберт крихітний — реакція майже миттєва", 8.6, GREY, "start")
    # цикл із довгим кроком
    s += text(ox, 222, "один довгий крок (напр., delay чи довге читання):", 10, RED, "start", "bold")
    s += rect(ox, 236, 70, 28, LGRN, GREEN, 1.2, 3)
    s += rect(ox + 75, 236, 420, 28, LRED, RED, 1.6, 3)
    s += text(ox + 285, 255, "ДОВГИЙ крок — усе інше чекає", 9.5, RED, "middle", "bold")
    s += rect(ox + 500, 236, 70, 28, LGRN, GREEN, 1.2, 3)
    s += text(ox, 286, "поки тягнеться довгий крок, оберт не завершується — реакція гальмує", 8.6, GREY, "start")
    s += rect(150, 312, 640, 34, LAMB, GOLD, 1.3, 8)
    s += text(470, 333, "Звідси й головний клопіт super-loop: не давати жодному кроку надовго «захопити» цикл.", 9.4, INK, "middle", "bold")
    save("fig-27-1-5-loop-timing.svg", s)


# ── Рис. 27.1.6 — кілька справ в одному циклі (патерн millis) ─────────────────
def fig16_several_jobs():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Кілька справ в одному циклі — без блокування (патерн millis)", 16, INK, "middle", "bold")
    s += text(W / 2, 54, "щооберту loop() питає «кому вже час?» і робить лише дозрілі справи (Розділ 24.5)", 9.8, GREY, "middle", style="italic")
    jobs = [
        ("Блимати LED", 1.0, GREEN),
        ("Читати давач", 0.4, BLUE),
        ("Серцебиття", 2.0, PURP),
    ]
    ox, t0 = 200, 80
    span = 700
    s += text(ox - 14, t0 - 14, "час →", 9, INK, "end", "bold")
    for r, (lab, period, col) in enumerate(jobs):
        y = t0 + 20 + r * 70
        s += text(ox - 16, y + 5, lab, 10, col, "end", "bold")
        s += line(ox, y, ox + span, y, FAINT, 1.2)
        t = period
        while t < 4.05:
            x = ox + span * t / 4.0
            s += circle(x, y, 5, col, col, 0)
            t += period
        s += text(ox + span + 10, y + 4, f"кожні {period:g} с", 8.4, GREY, "start")
    s += text(ox + span / 2, t0 + 20 + 3 * 70 - 6, "кожна справа спрацьовує у свій час — цикл нікого не блокує", 9, INK, "middle", "bold")
    s += rect(150, 320, 660, 44, LGRN, GREEN, 1.3, 9)
    s += text(480, 340, "Замість delay() — перевірка millis (§24.5): «чи минув мій інтервал?»", 9.8, INK, "middle", "bold")
    s += text(480, 357, "Так один super-loop тягне кілька незалежних справ «водночас».", 9, GREY, "middle")
    save("fig-27-1-6-several-jobs.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §27.2 Чому super-loop не масштабується — fig-27-2-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 27.2.1 — блокування заморожує все ───────────────────────────────────
def fig21_blocking():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 32, "Блокування: одна пауза заморожує ВЕСЬ цикл", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "будь-який виклик, що ЧЕКАЄ (delay, повільне читання, мережа), спиняє все інше", 10, GREY, "middle", style="italic")
    ox, y = 70, 140
    s += text(ox, y - 14, "час процесора →", 9.5, INK, "start", "bold")
    s += line(ox, y, 890, y, FAINT, 1.2)
    s += rect(ox, y, 90, 34, LGRN, GREEN, 1.2, 4)
    s += text(ox + 45, y + 22, "робота", 9, GREEN, "middle", "bold")
    s += rect(ox + 95, y, 520, 34, LRED, RED, 1.8, 4)
    s += text(ox + 355, y + 22, "delay(1000) / повільне читання — ЧЕКАЄМО", 11, RED, "middle", "bold")
    s += rect(ox + 620, y, 90, 34, LGRN, GREEN, 1.2, 4)
    s += text(ox + 665, y + 22, "робота", 9, GREEN, "middle", "bold")
    # що завмерло
    s += text(ox + 355, y - 26, "проста секунда — а пристрій «мертвий»", 8.6, RED, "middle", "bold")
    for lab, yy in [("LED не блимає", 220), ("кнопку не помічено", 244), ("екран не оновлюється", 268)]:
        s += text(ox + 150, yy, "✗ " + lab, 10, RED, "start", "bold")
    s += text(ox + 470, 244, "процесор простоює,", 9.5, GREY, "start")
    s += text(ox + 470, 262, "та зайнятий очікуванням —", 9.5, GREY, "start")
    s += text(ox + 470, 280, "користі нуль", 9.5, GREY, "start")
    s += rect(150, 312, 660, 34, LAMB, GOLD, 1.3, 8)
    s += text(480, 333, "У super-loop усе йде по черзі: поки один крок ЧЕКАЄ, решта просто не виконується.", 9.6, INK, "middle", "bold")
    save("fig-27-2-1-blocking.svg", s)


# ── Рис. 27.2.2 — чуйність = найдовший прохід ────────────────────────────────
def fig22_responsiveness():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 32, "Чуйність = найдовший прохід циклу", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "у найгіршому разі подію помітять аж наприкінці поточного оберту", 10.3, GREY, "middle", style="italic")
    ox, y = 70, 150
    s += line(ox, y, 890, y, FAINT, 1.2)
    steps = [("крок A", 90, GREEN), ("крок B (довгий)", 380, GOLD), ("крок C", 120, BLUE)]
    x = ox
    for lab, w, col in steps:
        s += rect(x, y, w, 34, "#fbfcff", col, 1.6, 4)
        s += text(x + w / 2, y + 22, lab, 9.5, col, "middle", "bold")
        x += w + 6
    # кнопку натиснули на початку
    s += line(ox + 95, y, ox + 95, y - 50, RED, 2)
    s += text(ox + 95, y - 56, "кнопку натиснули тут", 9, RED, "middle", "bold")
    # помітили аж наприкінці
    s += line(x, y, x, y - 50, GREEN, 2)
    s += text(x, y - 56, "помітили аж тут", 9, GREEN, "middle", "bold")
    s += f'<path d="M {ox+95} {y+50} Q {(ox+95+x)/2} {y+86} {x} {y+50}" fill="none" stroke="{RED}" stroke-width="2" stroke-dasharray="5,3"/>\n'
    s += text((ox + 95 + x) / 2, y + 92, "затримка = майже весь прохід", 9.5, RED, "middle", "bold")
    s += rect(150, 300, 660, 46, LBLUE, BLUE, 1.3, 9)
    s += text(480, 320, "Додаєш кроки (чи довжиш їх) — росте найгірша затримка реакції.", 9.8, INK, "middle", "bold")
    s += text(480, 337, "Переривання рятує для термінового, та головний потік усе одно гальмує (§23).", 9, GREY, "middle")
    save("fig-27-2-2-responsiveness.svg", s)


# ── Рис. 27.2.3 — millis рятує, але не завжди ────────────────────────────────
def fig23_millis_limit():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 32, "Патерн millis рятує — лише якщо все можна «нарізати»", 16.5, INK, "middle", "bold")
    s += text(W / 2, 54, "коротку справу ділять на крихітні шматки; та багато операцій блокують ЗСЕРЕДИНИ", 10, GREY, "middle", style="italic")
    # ліворуч: можна нарізати
    s += text(240, 96, "Можна нарізати ✓", 12, GREEN, "middle", "bold")
    ox = 70
    for i in range(10):
        s += rect(ox + i * 34, 120, 28, 28, LGRN, GREEN, 1.2, 3)
    s += text(240, 172, "блимання, лічба, опитування —", 9, GREY, "middle")
    s += text(240, 188, "легко робити по шматочку щооберту", 9, GREY, "middle")
    # праворуч: не нарізати
    s += text(720, 96, "Не нарізати ✗", 12, RED, "middle", "bold")
    s += rect(560, 120, 320, 28, LRED, RED, 1.8, 3)
    s += text(720, 139, "бібліотечний виклик, що ЧЕКАЄ всередині", 8.8, RED, "middle", "bold")
    s += text(720, 172, "мережевий запит, читання SD,", 9, GREY, "middle")
    s += text(720, 188, "повільний давач — суцільний блок", 9, GREY, "middle")
    s += rect(150, 230, 660, 116, "#fbfcff", GREY, 1.4, 12)
    s += text(480, 256, "Патерн millis вимагає, щоб КОЖНА справа вміла зупинятися й продовжуватися", 9.8, INK, "middle", "bold")
    s += text(480, 276, "крихітними кроками. Та чимало операцій так не вміють: вони блокують усередині", 9.8, INK, "middle", "bold")
    s += text(480, 296, "себе, і поділити їх ви не можете — хіба що переписати з нуля.", 9.8, INK, "middle", "bold")
    s += text(480, 324, "А ще один довгий шматок усе одно затримує решту — бо потік один.", 9.2, RED, "middle", "bold")
    save("fig-27-2-3-millis-limit.svg", s)


# ── Рис. 27.2.4 — ручні машини станів вибухають ──────────────────────────────
def fig24_state_explosion():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Щоб не блокувати — пишеш машини станів; для багатьох справ це спагеті", 15.5, INK, "middle", "bold")
    s += text(W / 2, 54, "просту послідовність «зроби — почекай — зроби» доводиться вивертати у плутані стани", 9.8, GREY, "middle", style="italic")
    # ліворуч: простий послідовний код
    s += text(210, 96, "Як хочеться (послідовно):", 10.5, GREEN, "middle", "bold")
    seq = ["зроби A", "почекай 1 с", "зроби B", "почекай 2 с", "зроби C"]
    for i, st in enumerate(seq):
        y = 118 + i * 34
        s += rect(120, y, 180, 26, LGRN, GREEN, 1.4, 5)
        s += text(210, y + 18, st, 9.5, INK, "middle")
        if i < len(seq) - 1:
            s += line(210, y + 26, 210, y + 34, GREEN, 1.6)
    s += text(210, 300, "просто читати згори вниз", 8.6, GREY, "middle")
    # праворуч: плутана машина станів
    s += text(680, 96, "Як виходить (машина станів):", 10.5, RED, "middle", "bold")
    nodes = [(560, 150, "S0"), (760, 140, "S1"), (860, 220, "S2"), (660, 250, "S3"), (560, 320, "S4"), (780, 300, "S5")]
    for nx, ny, lab in nodes:
        s += circle(nx, ny, 20, LRED, RED, 1.6)
        s += text(nx, ny + 4, lab, 9, RED, "middle", "bold")
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (3, 4), (4, 5), (5, 1), (1, 3), (2, 5)]
    for a, b in edges:
        ax, ay, _ = nodes[a]
        bx, by, _ = nodes[b]
        s += arrow(ax, ay, bx, by, GREY, 1.3)
    s += text(700, 348, "а тут — три такі, переплетені між собою", 8.6, RED, "middle", "bold")
    s += rect(150, 356, 660, 0)
    save("fig-27-2-4-state-explosion.svg", s)


# ── Рис. 27.2.5 — немає пріоритетів ──────────────────────────────────────────
def fig25_no_priority():
    W, H = 940, 350
    s = header(W, H)
    s += text(W / 2, 32, "Немає пріоритетів: усе — строго в порядку коду", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "терміновому не пробитися вперед — воно чекає своєї черги нарівні з рутиною", 10, GREY, "middle", style="italic")
    ox, y = 120, 150
    jobs = [("оновити екран", GREEN, False), ("записати лог", BLUE, False), ("порахувати", GOLD, False), ("АВАРІЙНИЙ СТОП", RED, True)]
    x = ox
    for lab, col, urgent in jobs:
        w = 180
        s += rect(x, y, w, 44, LRED if urgent else "#fbfcff", col, (2.4 if urgent else 1.4), 8)
        s += text(x + w / 2, y + 21, lab, 10 if not urgent else 10.5, col, "middle", "bold")
        s += text(x + w / 2, y + 37, ("ТЕРМІНОВО, та в кінці!" if urgent else "рутина"), 8, (RED if urgent else GREY), "middle", "bold" if urgent else "normal")
        if x + w < 860:
            s += arrow(x + w, y + 22, x + w + 14, y + 22, INK, 2)
        x += w + 16
    s += text(ox + 90, y - 16, "перевіряються по черзі →", 9, GREY, "start")
    s += rect(150, 250, 640, 80, LAMB, GOLD, 1.4, 12)
    s += text(470, 276, "Цикл перевіряє справи в тому порядку, як вони написані в коді.", 9.8, INK, "middle", "bold")
    s += text(470, 296, "Терміновий «аварійний стоп» мусить чекати, доки відпрацюють рутинні кроки перед ним.", 9.4, INK, "middle", "bold")
    s += text(470, 318, "Сказати «це важливіше, виконай першим» super-loop просто не вміє.", 9.2, RED, "middle", "bold")
    save("fig-27-2-5-no-priority.svg", s)


# ── Рис. 27.2.6 — чого ми насправді хочемо ───────────────────────────────────
def fig26_what_we_want():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Чого ми хочемо: кожна справа — окрема проста програма", 16.5, INK, "middle", "bold")
    s += text(W / 2, 54, "писати кожну послідовно, ніби вона сама на машині, а перемикання довірити планувальникові", 9.6, GREY, "middle", style="italic")
    progs = [
        (110, "Задача 1", GREEN, ["блимати:", "увімк → чекай", "вимк → чекай"]),
        (110 + 250, "Задача 2", BLUE, ["давач:", "читай → чекай", "повтори"]),
        (110 + 500, "Задача 3", PURP, ["зв'язок:", "прийми → відповідж", "чекай"]),
    ]
    for x, title, col, lines in progs:
        s += rect(x, 90, 200, 120, "#fbfcff", col, 1.8, 10)
        s += text(x + 100, 114, title, 11, col, "middle", "bold")
        s += line(x + 16, 124, x + 184, 124, FAINT, 1.2)
        for i, ln in enumerate(lines):
            s += text(x + 100, 146 + i * 20, ln, 9.2, INK, "middle")
        s += text(x + 100, 226, "проста, послідовна,", 8.4, GREY, "middle")
        s += text(x + 100, 240, "з власними «чекай»", 8.4, GREY, "middle")
    # планувальник унизу
    s += rect(230, 280, 500, 44, LAMB, GOLD, 1.8, 10)
    s += text(480, 300, "ПЛАНУВАЛЬНИК перемикає між задачами", 11, GOLD, "middle", "bold")
    s += text(480, 317, "кожна гадає, що володіє процесором сама", 8.8, GREY, "middle")
    for x, *_ in progs:
        s += arrow(x + 100, 210, 480 if x == 360 else (x + 100), 278, GREY, 1.4)
    s += text(480, 352, "Це і є поділ часу з історії розділу — лише на одному чипі. Так працюють ЗАДАЧІ (далі).", 9.4, GREEN, "middle", "bold")
    save("fig-27-2-6-what-we-want.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §27.3 Задачі (tasks) — fig-27-3-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 27.3.1 — задача — це окрема маленька програма ───────────────────────
def fig31_task_is_program():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 32, "Задача — це окрема маленька програма зі своїм циклом", 17, INK, "middle", "bold")
    s += text(W / 2, 54, "кожну пишемо просто й послідовно, наче власний super-loop, з власними «чекай»", 9.8, GREY, "middle", style="italic")
    tasks = [
        (60, "Задача: блимати", GREEN, ["for (;;) {", "  увімкнути LED", "  чекай 500 мс", "  вимкнути LED", "  чекай 500 мс", "}"]),
        (370, "Задача: давач", BLUE, ["for (;;) {", "  прочитати давач", "  обробити", "  чекай 1 с", "}"]),
        (680, "Задача: зв'язок", PURP, ["for (;;) {", "  чекай запит", "  відповісти", "}"]),
    ]
    for x, title, col, lines in tasks:
        s += rect(x, 92, 220, 190, "#fbfcff", col, 1.8, 10)
        s += text(x + 110, 116, title, 11, col, "middle", "bold")
        s += line(x + 16, 126, x + 204, 126, FAINT, 1.2)
        yy = 150
        for ln in lines:
            s += text(x + 24, yy, ln, 10.5, INK, "start")
            yy += 21
    s += rect(150, 300, 660, 44, LGRN, GREEN, 1.3, 9)
    s += text(480, 320, "Три прості лінійні програми замість одного заплутаного циклу з машинами станів.", 9.6, INK, "middle", "bold")
    s += text(480, 337, "Кожна читається згори вниз — і нічого не знає про інших.", 9, GREY, "middle")
    save("fig-27-3-1-task-is-program.svg", s)


# ── Рис. 27.3.2 — «чекати», не морозячи інших ────────────────────────────────
def fig32_block_no_freeze():
    W, H = 960, 370
    s = header(W, H)
    s += text(W / 2, 32, "Чарівна зміна: «чекати» більше не морозить інших", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "коли задача чекає, процесор не простоює — його одразу забирає інша задача", 10, GREY, "middle", style="italic")
    ox, y = 70, 150
    s += text(ox, y - 14, "час процесора →", 9.5, INK, "start", "bold")
    s += line(ox, y, 890, y, FAINT, 1.2)
    segs = [("A", 0, 120, GREEN), ("B", 120, 360, BLUE), ("A", 360, 480, GREEN), ("C", 480, 640, PURP), ("A", 640, 760, GREEN)]
    for c, a, b, col in segs:
        s += rect(ox + a, y, b - a, 34, col, INK, 0.8, 3)
        s += text(ox + (a + b) / 2, y + 22, "Задача " + c, 9, "#ffffff", "middle", "bold")
    # позначка, де A чекає
    s += line(ox + 120, y, ox + 120, y - 44, RED, 1.8)
    s += text(ox + 120, y - 50, "A каже «чекаю» → процесор іде до B", 8.8, RED, "middle", "bold")
    s += line(ox + 360, y, ox + 360, y - 44, GREEN, 1.8)
    s += text(ox + 360, y - 50, "пауза A минула → A біжить далі", 8.8, GREEN, "middle", "bold")
    s += rect(150, 250, 660, 96, "#fbfcff", GREY, 1.4, 10)
    s += text(480, 276, "Те саме очікування, що в super-loop морозило ВСЕ (рис. 27.2.1),", 9.8, INK, "middle", "bold")
    s += text(480, 296, "тут стає корисною паузою: поки A чекає, працюють B і C.", 9.8, INK, "middle", "bold")
    s += text(480, 322, "Блокувальний давач більше не «вішає» пристрій — він лише поступається чергою.", 9.2, GREEN, "middle", "bold")
    save("fig-27-3-2-block-no-freeze.svg", s)


# ── Рис. 27.3.3 — у кожної задачі свій стек ──────────────────────────────────
def fig33_own_stack():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 32, "У кожної задачі — свій стек (своє «де я зараз»)", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "власні локальні змінні, ланцюг викликів і збережена точка — тому задачі не плутаються", 9.8, GREY, "middle", style="italic")
    stacks = [(110, "Стек задачі A", GREEN), (400, "Стек задачі B", BLUE), (690, "Стек задачі C", PURP)]
    for x, title, col in stacks:
        s += text(x + 70, 96, title, 10.5, col, "middle", "bold")
        for i in range(5):
            yy = 110 + i * 30
            s += rect(x, yy, 140, 28, "#fbfcff", col, 1.4, 0)
        s += text(x + 70, 128, "локальні змінні", 8.4, GREY, "middle")
        s += text(x + 70, 158, "виклик → виклик", 8.4, GREY, "middle")
        s += text(x + 70, 218, "збережений контекст", 8.2, INK, "middle", "bold")
        s += text(x + 70, 246, "(регістри, лічильник", 8, GREY, "middle")
        s += text(x + 70, 260, "команд)", 8, GREY, "middle")
    s += rect(150, 300, 660, 46, LAMB, GOLD, 1.3, 10)
    s += text(480, 320, "Окремий стек у кожної задачі й дає змогу їй мати власне місце в програмі.", 9.6, INK, "middle", "bold")
    s += text(480, 337, "Скільки пам'яті відвести під стек — окрема важлива тема (§27.7).", 9, GREY, "middle")
    save("fig-27-3-3-own-stack.svg", s)


# ── Рис. 27.3.4 — стани задачі ───────────────────────────────────────────────
def fig34_states():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Стани задачі: біжить, готова, заблокована", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "одночасно БІЖИТЬ лише одна (на ядро); решта чекають своєї черги або події", 10, GREY, "middle", style="italic")
    run = (470, 130)
    ready = (220, 270)
    block = (720, 270)
    s += circle(*run, 52, LGRN, GREEN, 2.2)
    s += text(run[0], run[1] - 2, "БІЖИТЬ", 11, GREEN, "middle", "bold")
    s += text(run[0], run[1] + 15, "(виконується)", 8, GREY, "middle")
    s += circle(*ready, 52, LBLUE, BLUE, 2.2)
    s += text(ready[0], ready[1] - 2, "ГОТОВА", 11, BLUE, "middle", "bold")
    s += text(ready[0], ready[1] + 15, "(хоче процесор)", 8, GREY, "middle")
    s += circle(*block, 52, LAMB, GOLD, 2.2)
    s += text(block[0], block[1] - 2, "ЗАБЛОК.", 11, GOLD, "middle", "bold")
    s += text(block[0], block[1] + 15, "(чекає подію)", 8, GREY, "middle")
    s += arrow(ready[0] + 40, ready[1] - 30, run[0] - 44, run[1] + 34, BLUE, 2)
    s += text(310, 195, "планувальник дав чергу", 8.4, BLUE, "middle", "bold")
    s += arrow(run[0] - 44, run[1] + 40, ready[0] + 44, ready[1] - 24, GREY, 2)
    s += text(330, 230, "витіснено (вийшов час)", 8.4, GREY, "middle")
    s += arrow(run[0] + 44, run[1] + 34, block[0] - 40, block[1] - 30, GOLD, 2)
    s += text(640, 195, "чекає (delay, дані, подія)", 8.4, GOLD, "middle", "bold")
    s += arrow(block[0] - 44, block[1] + 30, ready[0] + 90, ready[1] + 20, GREEN, 2, dash="5,3")
    s += text(470, 320, "подія настала → знову готова", 8.6, GREEN, "middle", "bold")
    s += text(470, 352, "Саме перехід «БІЖИТЬ → ЗАБЛОКОВАНА» (а не простій) і дає корисне «чекати».", 9.4, INK, "middle", "bold")
    save("fig-27-3-4-states.svg", s)


# ── Рис. 27.3.5 — як створюють задачу ────────────────────────────────────────
def fig35_xtaskcreate():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Як створюють задачу: один виклик xTaskCreate", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "функція-задача — це вічний цикл, що НІКОЛИ не повертається (як власний loop)", 9.8, GREY, "middle", style="italic")
    s += _codebox(80, 90, 460, 150, ["void taskBlink(void *p) {", "    pinMode(2, OUTPUT);    // налаштування", "    for (;;) {              // вічний цикл", "        digitalWrite(2, HIGH);", "        vTaskDelay(500);    // чекай, не морозячи", "        digitalWrite(2, LOW);", "        vTaskDelay(500);", "    }", "}"], title="функція-задача:", col=GREEN)
    # виклик з підписами
    s += text(720, 120, "створення:", 10.5, BLUE, "middle", "bold")
    s += rect(580, 134, 360, 40, "#fbfcff", BLUE, 1.4, 8)
    s += text(600, 159, "xTaskCreate(taskBlink, \"blink\",", 10.5, INK, "start", "bold")
    s += text(620, 178, "        2048, NULL, 1, NULL);", 10.5, INK, "start", "bold")
    labels = ["taskBlink — яку функцію запускати", "\"blink\" — ім'я (для діагностики)", "2048 — розмір стека (§27.7)", "1 — пріоритет (§27.8)"]
    yy = 210
    for lab in labels:
        s += text(600, yy, "• " + lab, 9.2, GREY, "start")
        yy += 20
    s += rect(150, 320, 660, 44, LGRN, GREEN, 1.3, 9)
    s += text(480, 340, "Створив задачу — і вона живе сама, поряд з іншими. Скільки треба — стільки й створиш.", 9.6, INK, "middle", "bold")
    s += text(480, 357, "Деталі FreeRTOS і двох ядер ESP32 — у наступній темі.", 9, GREY, "middle")
    save("fig-27-3-5-xtaskcreate.svg", s)


# ── Рис. 27.3.6 — ілюзія багатьох програм на одному ядрі ─────────────────────
def fig36_illusion():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 32, "Ілюзія: багато програм на одному ядрі", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "одне ядро швидко перемикається — а ззовні здається, ніби всі задачі біжать водночас", 9.8, GREY, "middle", style="italic")
    # ядро
    s += rect(410, 90, 140, 50, LRED, RED, 2, 10)
    s += text(480, 114, "ОДНЕ ядро", 11, RED, "middle", "bold")
    s += text(480, 130, "робить одне за раз", 8, GREY, "middle")
    # швидке перемикання вниз до трьох «програм»
    progs = [(180, "Задача A", GREEN), (480, "Задача B", BLUE), (780, "Задача C", PURP)]
    for x, lab, col in progs:
        s += rect(x - 80, 210, 160, 50, "#fbfcff", col, 1.8, 10)
        s += text(x, 234, lab, 10.5, col, "middle", "bold")
        s += text(x, 250, "наче біжить весь час", 8, GREY, "middle")
        s += arrow(480, 142, x, 208, GREY, 1.6, dash="4,3")
    s += text(480, 180, "перемикається десятки-сотні разів за секунду", 8.8, RED, "middle", "bold")
    s += rect(150, 290, 660, 56, LAMB, GOLD, 1.4, 10)
    s += text(480, 312, "Це та сама ілюзія, що й у поділі часу 1961 року (історія розділу) —", 9.6, INK, "middle", "bold")
    s += text(480, 330, "лише тепер «користувачі» — це задачі, а зал — один чип. (Два ядра ESP32 — §27.5.)", 9.2, GREY, "middle")
    save("fig-27-3-6-illusion.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §27.4 Планувальник — fig-27-4-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 27.4.1 — планувальник: розпорядник процесорного часу ─────────────────
def fig41_scheduler():
    W, H = 960, 370
    s = header(W, H)
    s += text(W / 2, 32, "Планувальник — розпорядник процесорного часу", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "серед ГОТОВИХ задач він обирає, кому віддати процесор просто зараз", 10.3, GREY, "middle", style="italic")
    # готові задачі
    s += text(160, 96, "ГОТОВІ (хочуть процесор)", 10, BLUE, "middle", "bold")
    for i, lab in enumerate(["A", "B", "C"]):
        s += rect(70, 110 + i * 46, 180, 38, LBLUE, BLUE, 1.6, 8)
        s += text(160, 134 + i * 46, "Задача " + lab, 10, BLUE, "middle", "bold")
    # планувальник
    s += rect(380, 150, 180, 70, LAMB, GOLD, 2, 12)
    s += text(470, 180, "ПЛАНУВАЛЬНИК", 11, GOLD, "middle", "bold")
    s += text(470, 200, "обирає одного", 8.6, GREY, "middle")
    s += arrow(250, 165, 380, 175, INK, 2)
    # процесор
    s += rect(690, 150, 180, 70, LGRN, GREEN, 2, 12)
    s += text(780, 180, "ПРОЦЕСОР", 11, GREEN, "middle", "bold")
    s += text(780, 200, "виконує обрану", 8.6, GREY, "middle")
    s += arrow(560, 185, 690, 185, INK, 2.2)
    # заблоковані осторонь
    s += text(780, 270, "ЗАБЛОКОВАНІ — осторонь", 9.5, GOLD, "middle", "bold")
    s += rect(690, 282, 180, 30, "#f4f0e6", GOLD, 1.2, 6)
    s += text(780, 302, "чекають події, не змагаються", 8.2, GREY, "middle")
    s += rect(150, 326, 660, 36, LGRN, GREEN, 1.3, 8)
    s += text(480, 348, "Планувальник дивиться лише на ГОТОВИХ; заблоковані в черзі за процесор не стоять.", 9.6, INK, "middle", "bold")
    save("fig-27-4-1-scheduler.svg", s)


# ── Рис. 27.4.2 — коли перемикати: три приводи ───────────────────────────────
def fig42_triggers():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 32, "Коли перемикати задачі: три приводи", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "планувальник вступає в дію не безперервно, а в ці три моменти", 10.3, GREY, "middle", style="italic")
    cards = [
        (60, "1. Задача заблокувалася", GREEN, ["сама сказала «чекаю»", "(пауза, дані, подія)", "→ віддала процесор"]),
        (350, "2. Готова важливіша", RED, ["прокинулась задача", "з ВИЩИМ пріоритетом", "→ витісняє поточну"]),
        (640, "3. Тік таймера", BLUE, ["настав «тік»", "(періодичне переривання)", "→ черга рівним по колу"]),
    ]
    for x, title, col, lines in cards:
        s += rect(x, 92, 280, 170, "#fbfcff", col, 1.8, 12)
        s += text(x + 140, 120, title, 11, col, "middle", "bold")
        s += line(x + 20, 132, x + 260, 132, FAINT, 1.2)
        yy = 162
        for ln in lines:
            s += text(x + 140, yy, ln, 9.6, INK, "middle")
            yy += 26
    s += rect(150, 286, 660, 56, LAMB, GOLD, 1.4, 10)
    s += text(480, 308, "Перший привід — добровільний (кооперативний бік); другий і третій — примусові (витісняючий).", 9.4, INK, "middle", "bold")
    s += text(480, 328, "Саме примусові перемикання й роблять систему по-справжньому чуйною.", 9, GREY, "middle")
    save("fig-27-4-2-triggers.svg", s)


# ── Рис. 27.4.3 — кооперативний: задача сама поступається ─────────────────────
def fig43_cooperative():
    W, H = 960, 370
    s = header(W, H)
    s += text(W / 2, 32, "Кооперативний: кожен біжить, доки САМ не поступиться", 17, INK, "middle", "bold")
    s += text(W / 2, 54, "простіше й менше гонок — та жадібна задача здатна заморозити всіх", 10, GREY, "middle", style="italic")
    ox = 70
    # норма
    s += text(ox, 100, "Як задумано: кожен попрацював і поступився", 9.6, GREEN, "start", "bold")
    segs = [("A", 0, 150, GREEN), ("B", 150, 320, BLUE), ("C", 320, 470, PURP), ("A", 470, 600, GREEN)]
    for c, a, b, col in segs:
        s += rect(ox + a * 1.3, 114, (b - a) * 1.3, 30, col, INK, 0.8, 3)
        s += text(ox + (a + b) / 2 * 1.3, 134, c, 9.5, "#ffffff", "middle", "bold")
        if c != "A" or a == 0:
            s += line(ox + a * 1.3, 110, ox + a * 1.3, 148, GREY, 1)
    s += text(ox, 162, "↑ кожна риска — задача сама сказала «годі, далі ти»", 8.4, GREY, "start")
    # збій
    s += text(ox, 220, "Біда: задача A зажерлася й не поступається", 9.6, RED, "start", "bold")
    s += rect(ox, 234, 700, 30, LRED, RED, 1.8, 3)
    s += text(ox + 350, 254, "Задача A крутиться без кінця — НЕ поступається", 10, RED, "middle", "bold")
    s += text(ox, 284, "✗ B і C не біжать узагалі — система «зависла», як старий super-loop", 9, RED, "start", "bold")
    s += rect(150, 314, 660, 34, LAMB, GOLD, 1.3, 8)
    s += text(480, 335, "Кооперативний тримається на чесності задач. Одна нечесна — і всі стоять.", 9.6, INK, "middle", "bold")
    save("fig-27-4-3-cooperative.svg", s)


# ── Рис. 27.4.4 — витісняючий: планувальник забирає силою ─────────────────────
def fig44_preemptive():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 32, "Витісняючий: планувальник забирає процесор СИЛОЮ", 16.5, INK, "middle", "bold")
    s += text(W / 2, 54, "на тіку чи коли прокинувся важливіший — поточну задачу спиняють, не питаючи її згоди", 9.8, GREY, "middle", style="italic")
    ox, y = 70, 150
    s += line(ox, y, 890, y, FAINT, 1.2)
    s += rect(ox, y, 250, 34, BLUE, INK, 0.8, 3)
    s += text(ox + 125, y + 22, "Задача B (низький пріор.)", 9, "#ffffff", "middle", "bold")
    s += rect(ox + 250, y, 300, 34, RED, INK, 0.8, 3)
    s += text(ox + 400, y + 22, "Задача A (високий) — витіснила!", 9, "#ffffff", "middle", "bold")
    s += rect(ox + 550, y, 270, 34, BLUE, INK, 0.8, 3)
    s += text(ox + 685, y + 22, "B біжить далі", 9, "#ffffff", "middle", "bold")
    s += line(ox + 250, y - 50, ox + 250, y + 44, RED, 2.2)
    s += text(ox + 250, y - 56, "A прокинулась → B спинено НЕГАЙНО", 9, RED, "middle", "bold")
    s += line(ox + 550, y, ox + 550, y + 54, GREEN, 1.8)
    s += text(ox + 600, y + 70, "A заблокувалась → B повертається", 8.6, GREEN, "start", "bold")
    s += rect(150, 250, 660, 92, "#fbfcff", GREY, 1.4, 10)
    s += text(480, 276, "Задача B не давала згоди — її просто відсунули заради важливішої A.", 9.8, INK, "middle", "bold")
    s += text(480, 296, "Жодна задача не може «зажерти» процесор: планувальник завжди сильніший.", 9.8, INK, "middle", "bold")
    s += text(480, 322, "Це і робить систему чуйною та придатною до реального часу (§27.8).", 9.2, GREEN, "middle", "bold")
    save("fig-27-4-4-preemptive.svg", s)


# ── Рис. 27.4.5 — тік: серцебиття планувальника ──────────────────────────────
def fig45_tick():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 32, "Тік — серцебиття планувальника (таймер + переривання)", 16.5, INK, "middle", "bold")
    s += text(W / 2, 54, "періодичне таймер-переривання (напр., щомілісекунди) запускає планувальника", 10, GREY, "middle", style="italic")
    ox, y = 80, 170
    s += line(ox, y, 890, y, INK, 1.6)
    for i in range(11):
        x = ox + i * 78
        s += line(x, y - 8, x, y + 8, RED, 2)
        s += text(x, y + 24, "тік", 8, RED, "middle", "bold")
    s += text(ox, y - 26, "час →", 9, INK, "start", "bold")
    s += arrow(ox + 156, y - 44, ox + 156, y - 10, RED, 1.8)
    s += text(ox + 156, y - 50, "кожен тік: ISR → планувальник вирішує, чи перемкнути", 8.6, RED, "middle", "bold")
    s += rect(120, 230, 320, 70, LBLUE, BLUE, 1.4, 10)
    s += text(280, 256, "звідки тік:", 10, BLUE, "middle", "bold")
    s += text(280, 278, "таймер (§24) + переривання (§23)", 9.4, INK, "middle")
    s += rect(520, 230, 340, 70, LGRN, GREEN, 1.4, 10)
    s += text(690, 256, "що дає тік:", 10, GREEN, "middle", "bold")
    s += text(690, 278, "витіснення й поділ часу між рівними", 9.4, INK, "middle")
    s += text(W / 2, 330, "Це і є той самий механізм з історії розділу: таймер-переривання, що рухає поділ часу.", 9.4, INK, "middle", "bold")
    save("fig-27-4-5-tick.svg", s)


# ── Рис. 27.4.6 — як FreeRTOS обирає: пріоритет + round-robin ─────────────────
def fig46_freertos_rule():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Правило FreeRTOS: біжить найвищий готовий; рівні — по черзі", 16, INK, "middle", "bold")
    s += text(W / 2, 54, "пріоритетно-витісняючий планувальник: пріоритет вирішує, round-robin ділить рівних", 9.8, GREY, "middle", style="italic")
    levels = [
        ("Високий", RED, ["Давач (готова) ← БІЖИТЬ"]),
        ("Середній", GOLD, ["—"]),
        ("Низький", BLUE, ["Лог (готова)", "Дисплей (готова)"]),
    ]
    y = 92
    for lab, col, tasks in levels:
        s += rect(70, y, 150, 70, "#fbfcff", col, 1.8, 8)
        s += text(145, y + 30, lab, 11, col, "middle", "bold")
        s += text(145, y + 50, "пріоритет", 8, GREY, "middle")
        tx = 250
        for t in tasks:
            run = "БІЖИТЬ" in t
            s += rect(tx, y + 18, 230, 36, LRED if run else "#f4f6fb", col if run else GREY, 1.6 if run else 1.2, 7)
            s += text(tx + 115, y + 40, t, 9.4, col if run else INK, "middle", "bold" if run else "normal")
            tx += 250
        y += 86
    s += text(620, 92 + 86 * 2 + 36, "два рівні низькі — діляться по черзі (round-robin)", 8.6, BLUE, "middle", "bold")
    s += rect(150, 344, 660, 0)
    s += text(W / 2, 348, "Поки давач (високий) готовий — біжить лише він; щойно він засне, чергу ділять лог і дисплей.", 9.2, INK, "middle", "bold")
    save("fig-27-4-6-freertos-rule.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §27.5 RTOS і FreeRTOS на ESP32 — fig-27-5-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 27.5.1 — що таке RTOS: невелике ядро-набір ──────────────────────────
def fig51_what_is_rtos():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "RTOS — невелике ядро, що дає готові «цеглинки» багатозадачності", 16, INK, "middle", "bold")
    s += text(W / 2, 54, "«реального часу» означає ПЕРЕДБАЧУВАНО вчасно, а не обов'язково швидко", 10, GREY, "middle", style="italic")
    s += rect(120, 90, 720, 180, LBLUE, BLUE, 2, 14)
    s += text(480, 116, "Ядро RTOS", 13, BLUE, "middle", "bold")
    tools = [
        (210, "Задачі", "кілька програм", GREEN),
        (400, "Планувальник", "хто й коли (§27.4)", RED),
        (600, "Час", "тіки, паузи", GOLD),
        (210, "Обмін", "черги, семафори (§27.6)", PURP),
        (470, "Пам'ять", "стеки задач (§27.7)", "#2aa198"),
    ]
    positions = [(200, 140), (390, 140), (590, 140), (230, 210), (520, 210)]
    for (x, y), (cx, t, sub, col) in zip(positions, tools):
        s += rect(x, y, 170, 56, "#ffffff", col, 1.6, 8)
        s += text(x + 85, y + 24, t, 11, col, "middle", "bold")
        s += text(x + 85, y + 43, sub, 8.4, GREY, "middle")
    s += rect(150, 296, 660, 56, LAMB, GOLD, 1.4, 10)
    s += text(480, 318, "RTOS — не велика «настільна» ОС: ні файлів, ні вікон. Це крихітний набір засобів,", 9.6, INK, "middle", "bold")
    s += text(480, 338, "що перетворює голий чип на багатозадачну систему з передбачуваним часом.", 9.4, GREY, "middle")
    save("fig-27-5-1-what-is-rtos.svg", s)


# ── Рис. 27.5.2 — FreeRTOS: вже у твоєму ESP32 ───────────────────────────────
def fig52_freertos():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 32, "FreeRTOS — конкретний RTOS, що вже працює у твоєму ESP32", 16, INK, "middle", "bold")
    s += text(W / 2, 54, "крихітне (кілька кілобайт), вільне ядро; ти користуєшся ним, навіть не помічаючи", 9.8, GREY, "middle", style="italic")
    # лінійка історії
    s += rect(70, 92, 380, 130, "#fbfcff", GREY, 1.4, 12)
    s += text(260, 116, "Коротка історія", 11, INK, "middle", "bold")
    s += text(90, 144, "• 2003 — Річард Баррі створює FreeRTOS", 9.6, INK, "start")
    s += text(90, 168, "• вільне, відкрите, переносне ядро", 9.6, INK, "start")
    s += text(90, 192, "• 2017 — опіку бере Amazon (AWS)", 9.6, INK, "start")
    s += text(90, 212, "  ", 8, GREY, "start")
    # вже в ESP32
    s += rect(510, 92, 380, 130, LGRN, GREEN, 1.6, 12)
    s += text(700, 116, "У твоєму ESP32 — вже там", 11, GREEN, "middle", "bold")
    s += text(530, 144, "• Arduino працює ПОВЕРХ FreeRTOS", 9.6, INK, "start")
    s += text(530, 168, "• твій loop() — це задача loopTask", 9.6, INK, "start")
    s += text(530, 192, "• xTaskCreate, vTaskDelay — усе це FreeRTOS", 9.4, INK, "start")
    s += rect(150, 250, 660, 96, LBLUE, BLUE, 1.4, 12)
    s += text(480, 276, "RTOS — не велика програма, а БІБЛІОТЕКА-ядро, вшита у прошивку поряд із вашим кодом.", 9.6, INK, "middle", "bold")
    s += text(480, 298, "Тож на ESP32 вам не треба «ставити» RTOS — він уже працює;", 9.6, INK, "middle", "bold")
    s += text(480, 320, "ви просто починаєте створювати власні задачі поряд із loopTask.", 9.2, GREY, "middle")
    save("fig-27-5-2-freertos.svg", s)


# ── Рис. 27.5.3 — ESP32: два ядра ────────────────────────────────────────────
def fig53_two_cores():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 32, "Козир ESP32: ДВА ядра (рідкість серед мікроконтролерів)", 16, INK, "middle", "bold")
    s += text(W / 2, 54, "одне традиційно тягне радіо, друге — ваш застосунок; обидва — під одним FreeRTOS", 9.8, GREY, "middle", style="italic")
    s += rect(120, 100, 720, 170, LBLUE, BLUE, 2, 14)
    s += text(480, 124, "чип ESP32", 11, BLUE, "middle", "bold")
    s += rect(160, 140, 300, 110, LRED, RED, 1.8, 12)
    s += text(310, 166, "Ядро 0 (PRO_CPU)", 11.5, RED, "middle", "bold")
    s += text(310, 190, "«протокольне»", 9, GREY, "middle")
    s += text(310, 214, "за умовчанням — Wi-Fi", 9.4, INK, "middle")
    s += text(310, 232, "і Bluetooth", 9.4, INK, "middle")
    s += rect(500, 140, 300, 110, LGRN, GREEN, 1.8, 12)
    s += text(650, 166, "Ядро 1 (APP_CPU)", 11.5, GREEN, "middle", "bold")
    s += text(650, 190, "«застосункове»", 9, GREY, "middle")
    s += text(650, 214, "за умовчанням — ваш", 9.4, INK, "middle")
    s += text(650, 232, "setup() і loop()", 9.4, INK, "middle")
    s += rect(150, 290, 660, 56, LAMB, GOLD, 1.4, 10)
    s += text(480, 312, "Два ядра — велика рідкість для МК. (Увага: не всі ESP32 такі — S2, C3 одноядерні, §20.7.)", 9.4, INK, "middle", "bold")
    s += text(480, 332, "Завдяки традиційному поділу радіо й застосунок майже не заважають одне одному.", 9.2, GREY, "middle")
    save("fig-27-5-3-two-cores.svg", s)


# ── Рис. 27.5.4 — ілюзія на одному vs справжня паралельність на двох ──────────
def fig54_illusion_vs_real():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 32, "Одне ядро — ілюзія по черзі; два ядра — СПРАВЖНЯ паралельність", 15.5, INK, "middle", "bold")
    s += text(W / 2, 54, "на двох ядрах дві задачі справді виконуються в ту саму мить, а не лише почергово", 9.6, GREY, "middle", style="italic")
    # ліворуч: одне ядро
    s += text(245, 92, "Одне ядро (ілюзія)", 11, BLUE, "middle", "bold")
    ox, y = 70, 110
    segs = [("A", 0, BLUE), ("B", 1, GREEN), ("A", 2, BLUE), ("C", 3, PURP), ("B", 4, GREEN), ("A", 5, BLUE)]
    for c, i, col in segs:
        s += rect(ox + i * 58, y, 54, 30, col, INK, 0.6, 3)
        s += text(ox + i * 58 + 27, y + 21, c, 9, "#ffffff", "middle", "bold")
    s += text(245, y + 52, "по черзі — «наче» водночас", 8.6, GREY, "middle")
    # праворуч: два ядра
    s += text(720, 92, "Два ядра (по-справжньому)", 11, GREEN, "middle", "bold")
    ox2 = 500
    s += text(ox2 - 26, y + 21, "Я0", 9, RED, "end", "bold")
    s += text(ox2 - 26, y + 61, "Я1", 9, GREEN, "end", "bold")
    for i, (c, col) in enumerate([("A", RED), ("A", RED), ("A", RED)]):
        s += rect(ox2 + i * 110, y, 104, 30, RED, INK, 0.6, 3)
        s += text(ox2 + i * 110 + 52, y + 21, "Wi-Fi", 9, "#ffffff", "middle", "bold")
    for i in range(3):
        s += rect(ox2 + i * 110, y + 40, 104, 30, GREEN, INK, 0.6, 3)
        s += text(ox2 + i * 110 + 52, y + 61, "ваш код", 9, "#ffffff", "middle", "bold")
    s += line(ox2 + 55, y - 4, ox2 + 55, y + 74, GOLD, 1.4, dash="3,3")
    s += text(ox2 + 165, y + 92, "ту саму мить — обидва ядра працюють", 8.6, GREEN, "middle", "bold")
    s += rect(150, 250, 660, 96, LGRN, GREEN, 1.4, 12)
    s += text(480, 276, "На одному ядрі багатозадачність — майстерна ілюзія (швидке перемикання, §27.3).", 9.6, INK, "middle", "bold")
    s += text(480, 298, "Два ядра ESP32 дають і справжню паралельність: радіо на одному, ваша робота — на іншому,", 9.4, INK, "middle", "bold")
    s += text(480, 320, "і вони не крадуть час одне в одного. На кожному ядрі — той самий планувальник (§27.4).", 9.2, GREY, "middle")
    save("fig-27-5-4-illusion-vs-real.svg", s)


# ── Рис. 27.5.5 — прив'язування задач до ядра ────────────────────────────────
def fig55_pinning():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 32, "Можна «прив'язати» задачу до ядра: xTaskCreatePinnedToCore", 15.5, INK, "middle", "bold")
    s += text(W / 2, 54, "указуєш номер ядра (0, 1) — або «байдуже», і планувальник сам обере вільне", 9.8, GREY, "middle", style="italic")
    s += _codebox(70, 90, 470, 110, ["xTaskCreatePinnedToCore(", "    taskCtrl, \"ctrl\", 4096, NULL,", "    2, NULL,  1 );   // ← ядро 1", "//  ...функ., ім'я, стек, парам., пріор., деск., ЯДРО"], title="створення з прив'язкою:", col=GREEN)
    # типовий поділ
    s += rect(580, 90, 320, 110, "#fbfcff", GREY, 1.4, 10)
    s += text(740, 114, "типовий поділ", 10.5, INK, "middle", "bold")
    s += text(600, 140, "Ядро 0: Wi-Fi / мережа", 9.6, RED, "start", "bold")
    s += text(600, 162, "Ядро 1: ваша важлива робота", 9.6, GREEN, "start", "bold")
    s += text(600, 184, "→ радіо не «затинає» керування", 8.8, GREY, "start")
    s += rect(150, 230, 660, 116, LBLUE, BLUE, 1.4, 12)
    s += text(480, 256, "Прив'язка корисна, коли задача мусить бігти без перешкод від іншого ядра —", 9.6, INK, "middle", "bold")
    s += text(480, 278, "наприклад, точне керування мотором окремо від мережевого стека.", 9.6, INK, "middle", "bold")
    s += text(480, 304, "Не прив'язуєш (tskNO_AFFINITY) — задача побіжить на будь-якому вільному ядрі.", 9.2, GREY, "middle")
    s += text(480, 326, "Звичайний loop() за умовчанням живе на ядрі 1.", 9.2, GREY, "middle")
    save("fig-27-5-5-pinning.svg", s)


# ── Рис. 27.5.6 — два ядра роблять спільні дані ще небезпечнішими ─────────────
def fig56_shared_harder():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 32, "Зворотний бік: два ядра роблять спільні дані ще небезпечнішими", 15, INK, "middle", "bold")
    s += text(W / 2, 54, "тепер дві задачі можуть торкнутися однієї змінної не «по черзі», а в ТУ САМУ мить", 9.6, GREY, "middle", style="italic")
    # два ядра пишуть в одну змінну
    s += rect(120, 110, 200, 60, LRED, RED, 1.8, 10)
    s += text(220, 136, "Ядро 0: задача X", 9.8, RED, "middle", "bold")
    s += text(220, 154, "пише змінну", 8.6, GREY, "middle")
    s += rect(640, 110, 200, 60, LGRN, GREEN, 1.8, 10)
    s += text(740, 136, "Ядро 1: задача Y", 9.8, GREEN, "middle", "bold")
    s += text(740, 154, "пише ту саму", 8.6, GREY, "middle")
    s += rect(420, 200, 120, 56, LAMB, GOLD, 2, 10)
    s += text(480, 226, "спільна", 10, INK, "middle", "bold")
    s += text(480, 244, "змінна", 10, INK, "middle", "bold")
    s += arrow(320, 150, 430, 205, RED, 2.2)
    s += arrow(640, 150, 530, 205, GREEN, 2.2)
    s += text(480, 290, "одночасний доступ → зіпсоване значення (гонка)", 10, RED, "middle", "bold")
    s += rect(150, 312, 660, 34, LBLUE, BLUE, 1.3, 8)
    s += text(480, 333, "Тому в багатозадачності (а надто на двох ядрах) спільні дані треба захищати — це тема §27.6.", 9.2, INK, "middle", "bold")
    save("fig-27-5-6-shared-harder.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §27.6 Обмін між задачами — fig-27-6-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 27.6.1 — проблема: задачі мусять спілкуватися безпечно ───────────────
def fig61_problem():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 32, "Задачі незалежні — та мусять і спілкуватися, і ділити ресурси", 16, INK, "middle", "bold")
    s += text(W / 2, 54, "«голі» спільні змінні дають гонку (§27.5); потрібні БЕЗПЕЧНІ канали", 10, GREY, "middle", style="italic")
    s += rect(80, 110, 180, 60, LGRN, GREEN, 1.8, 10)
    s += text(170, 136, "Задача A", 11, GREEN, "middle", "bold")
    s += text(170, 154, "має дані", 8.6, GREY, "middle")
    s += rect(700, 110, 180, 60, LBLUE, BLUE, 1.8, 10)
    s += text(790, 136, "Задача B", 11, BLUE, "middle", "bold")
    s += text(790, 154, "потребує їх", 8.6, GREY, "middle")
    # небезпечний шлях
    s += rect(400, 100, 160, 36, LRED, RED, 1.8, 8)
    s += text(480, 123, "гола змінна", 9.6, RED, "middle", "bold")
    s += arrow(260, 130, 398, 118, RED, 2)
    s += arrow(700, 130, 562, 118, RED, 2)
    s += text(480, 156, "✗ одночасний доступ → гонка", 9.2, RED, "middle", "bold")
    # дві потреби
    s += rect(140, 220, 300, 56, "#fbfcff", GREY, 1.4, 10)
    s += text(290, 244, "1) передати ДАНІ", 10, INK, "middle", "bold")
    s += text(290, 262, "(A → B: відлік, команда…)", 8.6, GREY, "middle")
    s += rect(520, 220, 300, 56, "#fbfcff", GREY, 1.4, 10)
    s += text(670, 244, "2) поділити РЕСУРС", 10, INK, "middle", "bold")
    s += text(670, 262, "(шина, периферія, змінна)", 8.6, GREY, "middle")
    s += rect(150, 300, 660, 44, LAMB, GOLD, 1.4, 10)
    s += text(480, 322, "RTOS дає для цього готові БЕЗПЕЧНІ засоби: чергу, семафор, м'ютекс —", 9.6, INK, "middle", "bold")
    s += text(480, 339, "усі вони поступливі (блокуються, не морозячи) й захищені від гонок.", 9, GREY, "middle")
    save("fig-27-6-1-problem.svg", s)


# ── Рис. 27.6.2 — черга: безпечно передати дані ──────────────────────────────
def fig62_queue():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 32, "Черга: безпечна труба «перший прийшов — перший пішов»", 16, INK, "middle", "bold")
    s += text(W / 2, 54, "одна задача кладе дані, інша бере; дані КОПІЮЮТЬСЯ, тож спільної змінної й гонки нема", 9.6, GREY, "middle", style="italic")
    s += rect(70, 130, 160, 60, LGRN, GREEN, 1.8, 10)
    s += text(150, 156, "виробник", 10.5, GREEN, "middle", "bold")
    s += text(150, 174, "xQueueSend", 8.6, INK, "middle")
    s += arrow(230, 160, 300, 160, INK, 2.2)
    # черга — комірки FIFO
    s += text(490, 116, "ЧЕРГА (FIFO)", 10, GOLD, "middle", "bold")
    for i in range(5):
        x = 310 + i * 72
        filled = i < 3
        s += rect(x, 142, 64, 36, LAMB if filled else "#ffffff", GOLD, 1.6, 5)
        if filled:
            s += text(x + 32, 165, "дані", 8.6, INK, "middle", "bold")
    s += text(346, 200, "вихід ←", 8.4, GREY, "middle")
    s += text(670, 200, "← вхід", 8.4, GREY, "middle")
    s += arrow(680, 160, 750, 160, INK, 2.2)
    s += rect(750, 130, 160, 60, LBLUE, BLUE, 1.8, 10)
    s += text(830, 156, "споживач", 10.5, BLUE, "middle", "bold")
    s += text(830, 174, "xQueueReceive", 8.4, INK, "middle")
    s += rect(150, 240, 660, 102, "#fbfcff", GREY, 1.4, 12)
    s += text(480, 266, "Черга пуста — споживач БЛОКУЄТЬСЯ (поступливо чекає), доки щось прийде;", 9.6, INK, "middle", "bold")
    s += text(480, 286, "переповнена — виробник чекає, доки звільниться місце. Жодних гонок.", 9.6, INK, "middle", "bold")
    s += text(480, 312, "Це найчистіший спосіб передати дані між задачами — і він їх ще й розв'язує в часі.", 9.2, GREEN, "middle", "bold")
    s += text(480, 332, "(виробник і споживач можуть бігти у власному ритмі)", 8.6, GREY, "middle")
    save("fig-27-6-2-queue.svg", s)


# ── Рис. 27.6.3 — семафор: подати сигнал про подію ───────────────────────────
def fig63_semaphore():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 32, "Семафор: сигнал «сталася подія» (а не самі дані)", 16.5, INK, "middle", "bold")
    s += text(W / 2, 54, "класика: переривання будить задачу — короткий ISR лише сигналить, робота йде в задачі (§23.3)", 9.4, GREY, "middle", style="italic")
    s += rect(70, 120, 170, 56, LRED, RED, 1.8, 10)
    s += text(155, 144, "ISR (подія)", 10.5, RED, "middle", "bold")
    s += text(155, 162, "коротка!", 8.4, GREY, "middle")
    s += arrow(240, 148, 360, 148, RED, 2.2)
    s += text(300, 138, "give (дати)", 8.6, RED, "middle", "bold")
    # семафор-прапорець
    s += circle(410, 148, 30, LAMB, GOLD, 2)
    s += text(410, 152, "сем.", 9.5, GOLD, "middle", "bold")
    s += arrow(440, 148, 560, 148, GREEN, 2.2)
    s += text(500, 138, "take (взяти)", 8.6, GREEN, "middle", "bold")
    s += rect(560, 120, 180, 56, LGRN, GREEN, 1.8, 10)
    s += text(650, 144, "задача-обробник", 9.6, GREEN, "middle", "bold")
    s += text(650, 162, "спала → прокинулась", 8.2, GREY, "middle")
    s += arrow(740, 148, 850, 148, INK, 2)
    s += text(805, 138, "робить діло", 8.4, INK, "middle", "bold")
    s += rect(150, 220, 660, 122, "#fbfcff", GREY, 1.4, 12)
    s += text(480, 246, "Бінарний семафор — це «дзвоник»: одна сторона дає сигнал, інша на нього чекає (спить).", 9.5, INK, "middle", "bold")
    s += text(480, 268, "Так важку роботу виносять з ISR у задачу: ISR лише дзвонить, задача — працює (§23.3).", 9.5, INK, "middle", "bold")
    s += text(480, 294, "Лічильний семафор схожий, але РАХУЄ: скільки одиниць ресурсу вільно", 9.2, GREY, "middle")
    s += text(480, 312, "(узяв — на одиницю менше; дав — на одиницю більше; нуль — чекай).", 9.2, GREY, "middle")
    s += text(480, 332, "Семафор передає СИГНАЛ, а не дані — для даних бери чергу.", 8.8, GREEN, "middle", "bold")
    save("fig-27-6-3-semaphore.svg", s)


# ── Рис. 27.6.4 — м'ютекс: один за раз до спільного ресурсу ───────────────────
def fig64_mutex():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 32, "М'ютекс: «один за раз» до спільного ресурсу", 17, INK, "middle", "bold")
    s += text(W / 2, 54, "як «паличка, що дає право говорити»: хто тримає замок — користується; решта чекають", 9.6, GREY, "middle", style="italic")
    # ресурс
    s += rect(410, 230, 140, 60, LAMB, GOLD, 2, 10)
    s += text(480, 254, "спільний", 9.6, INK, "middle", "bold")
    s += text(480, 272, "ресурс (шина)", 9, GREY, "middle")
    # задача A тримає замок
    s += rect(120, 110, 180, 60, LGRN, GREEN, 2, 10)
    s += text(210, 134, "Задача A 🔒", 10.5, GREEN, "middle", "bold")
    s += text(210, 152, "взяла замок — працює", 8, GREY, "middle")
    s += arrow(250, 170, 430, 232, GREEN, 2.2)
    s += text(330, 215, "користується", 8.6, GREEN, "middle", "bold")
    # задача B чекає
    s += rect(660, 110, 180, 60, LRED, RED, 2, 10)
    s += text(750, 134, "Задача B", 10.5, RED, "middle", "bold")
    s += text(750, 152, "хоче — ЧЕКАЄ (блок)", 8, GREY, "middle")
    s += line(710, 170, 540, 232, RED, 2, dash="6,3")
    s += text(660, 215, "✗ зайнято — чекає, доки A віддасть", 8.4, RED, "middle", "bold")
    s += rect(150, 308, 660, 34, LBLUE, BLUE, 1.3, 8)
    s += text(480, 329, "Бере замок → користується спільним → віддає замок. Лише тоді B дістає доступ. Гонки нема.", 9.2, INK, "middle", "bold")
    save("fig-27-6-4-mutex.svg", s)


# ── Рис. 27.6.5 — м'ютекс проти семафора: власник + успадкування пріоритету ───
def fig65_mutex_vs_sem():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "М'ютекс — не просто сигнал: має власника й успадкування пріоритету", 14.5, INK, "middle", "bold")
    s += text(W / 2, 54, "дві відмінності від бінарного семафора, що роблять його правильним для захисту ресурсу", 9.4, GREY, "middle", style="italic")
    s += rect(70, 86, 380, 90, "#fbfcff", GOLD, 1.6, 10)
    s += text(260, 110, "1) Власник", 11, GOLD, "middle", "bold")
    s += text(90, 134, "замок віддає ЛИШЕ той, хто взяв", 9.4, INK, "start")
    s += text(90, 156, "(семафор може дати будь-хто)", 8.6, GREY, "start")
    s += rect(510, 86, 380, 90, "#fbfcff", RED, 1.6, 10)
    s += text(700, 110, "2) Успадкування пріоритету", 10.5, RED, "middle", "bold")
    s += text(530, 134, "власник тимчасово отримує пріоритет", 9.2, INK, "start")
    s += text(530, 156, "того, хто на нього чекає", 9.2, INK, "start")
    # інверсія пріоритетів
    s += text(W / 2, 206, "Навіщо? Проти ІНВЕРСІЇ ПРІОРИТЕТІВ:", 10.5, INK, "middle", "bold")
    s += text(150, 232, "• низькопріоритетна тримає замок", 9.4, BLUE, "start")
    s += text(150, 252, "• високопріоритетна чекає на той замок", 9.4, RED, "start")
    s += text(150, 272, "• середня витісняє низьку → висока «голодує» через середню!", 9.4, GOLD, "start")
    s += text(150, 296, "Успадкування: низька на час замка стає «високою» → швидко віддасть і розблокує.", 9.4, GREEN, "start", "bold")
    s += rect(150, 318, 660, 50, LAMB, GOLD, 1.3, 9)
    s += text(480, 338, "Класичний випадок — марсіанський «Pathfinder» (1997): інверсія пріоритетів перезавантажувала", 8.8, INK, "middle", "bold")
    s += text(480, 356, "апарат, аж доки віддалено не ввімкнули успадкування пріоритету на м'ютексі.", 8.6, GREY, "middle")
    save("fig-27-6-5-mutex-vs-sem.svg", s)


# ── Рис. 27.6.6 — що коли обирати ────────────────────────────────────────────
def fig66_decision():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 32, "Що коли обирати: засіб під потребу", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "чотири потреби — чотири інструменти", 10.3, GREY, "middle", style="italic")
    rows = [
        ("Передати ДАНІ між задачами", "Черга (queue)", GREEN, "копіює дані, FIFO, блокує"),
        ("Сигнал про ПОДІЮ (сталося!)", "Бінарний семафор", BLUE, "дзвоник; ISR будить задачу"),
        ("Порахувати вільні РЕСУРСИ", "Лічильний семафор", GOLD, "скільки одиниць доступно"),
        ("Захистити СПІЛЬНИЙ ресурс", "М'ютекс (mutex)", RED, "один за раз; власник + успадк."),
    ]
    y = 92
    for need, tool, col, note in rows:
        s += rect(60, y, 360, 50, "#fbfcff", GREY, 1.2, 8)
        s += text(80, y + 30, need, 10.5, INK, "start", "bold")
        s += arrow(425, y + 25, 470, y + 25, INK, 2)
        s += rect(480, y, 240, 50, "#f4f6fb", col, 1.8, 8)
        s += text(600, y + 30, tool, 10.5, col, "middle", "bold")
        s += text(740, y + 30, note, 8.6, GREY, "start")
        y += 62
    save("fig-27-6-6-decision.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §27.7 Пам'ять у RTOS: стеки задач — fig-27-7-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 27.7.1 — що лежить у стеку задачі ───────────────────────────────────
def fig71_stack_contents():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Стек задачі: що в ньому лежить", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "локальні змінні, ланцюг викликів і збережений контекст — усе у власному блоці RAM задачі", 9.6, GREY, "middle", style="italic")
    bx, bw = 360, 220
    layers = [
        ("збережений контекст", LRED, RED, "(регістри, лічильник команд —", "коли задачу перемкнули)"),
        ("кадр виклику func C", LBLUE, BLUE, "локальні C, адреса повернення", ""),
        ("кадр виклику func B", LBLUE, BLUE, "локальні B, адреса повернення", ""),
        ("кадр виклику func A", LBLUE, BLUE, "локальні A, адреса повернення", ""),
        ("локальні задачі", LGRN, GREEN, "змінні самого тіла задачі", ""),
    ]
    y = 92
    for lab, bg, col, sub, sub2 in layers:
        h = 50
        s += rect(bx, y, bw, h, bg, col, 1.6, 0)
        s += text(bx + bw / 2, y + 20, lab, 10, col, "middle", "bold")
        s += text(bx + bw / 2, y + 36, sub, 7.8, GREY, "middle")
        y += h
    s += text(bx - 16, 100, "верх", 8.5, GREY, "end")
    s += text(bx - 16, y - 6, "низ", 8.5, GREY, "end")
    s += line(bx - 30, 100, bx - 30, y - 10, INK, 1.4)
    s += text(bx + bw + 30, (100 + y) / 2, "росте з кожним", 9, INK, "start")
    s += text(bx + bw + 30, (100 + y) / 2 + 16, "вкладеним викликом ↓", 9, INK, "start", "bold")
    s += rect(150, y + 6, 640, 36, LAMB, GOLD, 1.3, 8)
    s += text(470, y + 29, "У кожної задачі — свій окремий стек; його розмір ви задаєте при створенні (§27.3).", 9.4, INK, "middle", "bold")
    save("fig-27-7-1-stack-contents.svg", s)


# ── Рис. 27.7.2 — переповнення стека ─────────────────────────────────────────
def fig72_overflow():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 32, "Замало стека → переповнення: задача псує сусідню пам'ять", 15.5, INK, "middle", "bold")
    s += text(W / 2, 54, "задача використала більше, ніж їй відвели, — і «вилізла» за межу у чужу пам'ять", 9.6, GREY, "middle", style="italic")
    # стек A (переповнюється)
    s += text(230, 96, "Стек задачі A", 10.5, GREEN, "middle", "bold")
    s += rect(120, 110, 220, 110, "#ffffff", GREEN, 1.8, 0)
    s += rect(120, 110, 220, 110, LGRN, GREEN, 0, 0)
    s += text(230, 150, "відведено A", 9.2, INK, "middle")
    s += line(120, 220, 340, 220, RED, 2.4)
    s += text(230, 236, "← межа стека A", 8.6, RED, "middle", "bold")
    # переповнення
    s += rect(120, 220, 220, 56, LRED, RED, 1.8, 0)
    s += text(230, 244, "ПЕРЕПОВНЕННЯ", 10, RED, "middle", "bold")
    s += text(230, 262, "вилізло за межу!", 8.4, RED, "middle")
    # сусідня пам'ять
    s += text(560, 96, "Сусідня пам'ять (стек B / дані)", 10.5, BLUE, "middle", "bold")
    s += rect(450, 220, 220, 56, LBLUE, BLUE, 1.8, 0)
    s += text(560, 244, "← сюди вписалося сміття", 8.8, BLUE, "middle", "bold")
    s += text(560, 262, "дані B зіпсовано", 8.2, GREY, "middle")
    s += arrow(340, 248, 448, 248, RED, 2.4)
    s += rect(150, 300, 640, 46, LAMB, GOLD, 1.4, 10)
    s += text(470, 322, "Найгірше: збій з'являється ДАЛЕКО від причини — у задачі B, хоч винна A.", 9.4, INK, "middle", "bold")
    s += text(470, 339, "Тому переповнення стека — одна з найпідступніших помилок RTOS.", 9, GREY, "middle")
    save("fig-27-7-2-overflow.svg", s)


# ── Рис. 27.7.3 — бюджет RAM: усе має вміститися ─────────────────────────────
def fig73_ram_budget():
    W, H = 940, 340
    s = header(W, H)
    s += text(W / 2, 32, "Бюджет RAM: усі стеки + купа + глобальні мусять уміститися", 15.5, INK, "middle", "bold")
    s += text(W / 2, 54, "забагато стека теж погано — завеликі стеки марнують дорогу пам'ять чипа", 9.8, GREY, "middle", style="italic")
    ox, y, total = 70, 130, 800
    parts = [
        ("глобальні", 0.12, GREY),
        ("стек loop", 0.12, GOLD),
        ("стек задачі 1", 0.16, GREEN),
        ("стек задачі 2", 0.16, BLUE),
        ("стек задачі 3", 0.14, PURP),
        ("купа (heap)", 0.22, "#2aa198"),
        ("вільно", 0.08, FAINT),
    ]
    x = ox
    for lab, frac, col in parts:
        w = total * frac
        s += rect(x, y, w, 50, col if col != FAINT else "#ffffff", INK, 1, 0)
        if frac > 0.1:
            s += text(x + w / 2, y + 24, lab, 8.4, "#ffffff" if col not in (FAINT, GOLD) else INK, "middle", "bold")
            s += text(x + w / 2, y + 40, "", 7, GREY, "middle")
        x += w
    s += text(ox, y - 10, "вся RAM чипа (в ESP32 — сотні кілобайтів)", 9, INK, "start", "bold")
    s += text(ox + total, y + 70, "→ переповнити цей рядок не можна", 8.8, RED, "end", "bold")
    s += rect(150, 250, 640, 70, LBLUE, BLUE, 1.4, 12)
    s += text(470, 276, "Кожен зайвий кілобайт стека — це кілобайт, якого бракуватиме деінде.", 9.6, INK, "middle", "bold")
    s += text(470, 296, "Тому розмір стека шукають не «з запасом про всяк випадок», а виміряний —", 9.4, INK, "middle", "bold")
    s += text(470, 314, "достатній із розумним запасом, але не марнотратний.", 9, GREY, "middle")
    save("fig-27-7-3-ram-budget.svg", s)


# ── Рис. 27.7.4 — водяний знак: виміряти найглибше використання ───────────────
def fig74_high_water():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 32, "Як підібрати розмір: «водяний знак» стека", 17, INK, "middle", "bold")
    s += text(W / 2, 54, "система каже, скільки стека лишалося незайманим у найгіршу мить — звідси й добираєш розмір", 9.4, GREY, "middle", style="italic")
    bx, bw, top, bot = 380, 200, 100, 300
    s += rect(bx, top, bw, bot - top, "#ffffff", INK, 1.8, 0)
    # використана частина (знизу)
    usedtop = 190
    s += rect(bx, usedtop, bw, bot - usedtop, LRED, RED, 0, 0)
    s += text(bx + bw / 2, (usedtop + bot) / 2, "найглибше", 9, RED, "middle", "bold")
    s += text(bx + bw / 2, (usedtop + bot) / 2 + 16, "використання", 9, RED, "middle", "bold")
    s += line(bx - 8, usedtop, bx + bw + 8, usedtop, RED, 2.2, dash="6,3")
    s += text(bx + bw + 16, usedtop + 4, "водяний знак", 9.5, RED, "start", "bold")
    s += text(bx + bw + 16, usedtop + 20, "(uxTaskGetStackHighWaterMark)", 7.6, GREY, "start")
    # вільний запас
    s += rect(bx, top, bw, usedtop - top, LGRN, GREEN, 0, 0)
    s += text(bx + bw / 2, (top + usedtop) / 2, "лишалося вільним", 8.8, GREEN, "middle", "bold")
    s += line(bx - 8, top, bx + bw + 8, top, INK, 2)
    s += text(bx - 16, top + 4, "межа стека", 8.4, INK, "end", "bold")
    s += rect(150, 320, 640, 0)
    s += text(470, 322, "Рецепт: погониш задачу під навантаженням → глянеш водяний знак → лишиш розумний запас.", 9.2, INK, "middle", "bold")
    save("fig-27-7-4-high-water.svg", s)


# ── Рис. 27.7.5 — великий локальний масив рве стек ───────────────────────────
def fig75_big_array():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 32, "Головний винуватець: великий локальний масив", 17, INK, "middle", "bold")
    s += text(W / 2, 54, "буфер, оголошений усередині функції, лягає на СТЕК — і легко його переповнює", 9.6, GREY, "middle", style="italic")
    s += _codebox(70, 90, 420, 80, ["void task(void*) {", "    char buf[4096];   // ← на СТЕКУ! рве його", "    ...", "}"], title="погано:", col=RED)
    s += _codebox(70, 200, 420, 80, ["void task(void*) {", "    static char buf[4096]; // не на стеку", "    ...                       // (або з купи)", "}"], title="краще:", col=GREEN)
    s += rect(530, 90, 360, 190, "#fbfcff", GREY, 1.4, 12)
    s += text(710, 116, "що ще їсть стек:", 10.5, INK, "middle", "bold")
    s += text(550, 144, "• великі локальні масиви/буфери", 9.4, RED, "start", "bold")
    s += text(550, 168, "• глибока вкладеність викликів", 9.4, INK, "start")
    s += text(550, 192, "• рекурсія (на МК — уникай)", 9.4, INK, "start")
    s += text(550, 216, "• printf, float, складні бібліотеки", 9.4, INK, "start")
    s += text(550, 248, "Великі буфери — у static чи купу,", 9, GREEN, "start", "bold")
    s += text(550, 266, "а не на стек.", 9, GREEN, "start", "bold")
    s += rect(150, 300, 660, 0)
    s += text(480, 322, "Найшвидший спосіб переповнити стек — оголосити в задачі великий масив. Виносьте його зі стека.", 9, INK, "middle", "bold")
    save("fig-27-7-5-big-array.svg", s)


# ── Рис. 27.7.6 — стек проти купи ────────────────────────────────────────────
def fig76_stack_vs_heap():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 32, "Стек і купа: два різні види пам'яті", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "стек — у кожної задачі свій і фіксований; купа — спільний пул для динамічного", 9.8, GREY, "middle", style="italic")
    s += rect(80, 90, 380, 180, LGRN, GREEN, 1.8, 12)
    s += text(270, 116, "СТЕК (кожної задачі свій)", 11, GREEN, "middle", "bold")
    s += text(100, 144, "• локальні змінні, виклики", 9.4, INK, "start")
    s += text(100, 168, "• розмір фіксований при створенні", 9.4, INK, "start")
    s += text(100, 192, "• окремий у кожної задачі", 9.4, INK, "start")
    s += text(100, 216, "• переповнення = крах", 9.4, RED, "start", "bold")
    s += text(100, 244, "на ESP32 розмір задають у БАЙТАХ", 8.8, GREY, "start")
    s += rect(480, 90, 380, 180, LBLUE, BLUE, 1.8, 12)
    s += text(670, 116, "КУПА (heap, спільна)", 11, BLUE, "middle", "bold")
    s += text(500, 144, "• динамічне виділення (malloc/new)", 9.4, INK, "start")
    s += text(500, 168, "• звідси й самі об'єкти RTOS:", 9.4, INK, "start")
    s += text(515, 188, "задачі, черги, семафори", 8.8, GREY, "start")
    s += text(500, 212, "• спільна на всю систему", 9.4, INK, "start")
    s += text(500, 236, "• скінчиться — виділення впаде", 9.4, RED, "start", "bold")
    s += rect(150, 300, 660, 0)
    s += text(480, 322, "Стеки задач + купа + глобальні живуть в одній RAM (§21); разом вони й складають бюджет пам'яті.", 9, INK, "middle", "bold")
    save("fig-27-7-6-stack-vs-heap.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §27.8 Реальний час: детермінованість і пріоритети — fig-27-8-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 27.8.1 — реальний час = передбачуваність, не швидкість ───────────────
def fig81_predictable():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "«Реальний час» — це ПЕРЕДБАЧУВАНО вчасно, а не швидко", 16.5, INK, "middle", "bold")
    s += text(W / 2, 54, "важить не гарний середній час, а гарантований НАЙГІРШИЙ випадок", 10, GREY, "middle", style="italic")
    dl = 250  # лінія дедлайну (y)
    # система A — швидка, та зі сплеском
    ox = 80
    s += text(230, 92, "Швидка, та інколи зволікає", 10.5, RED, "middle", "bold")
    bars_a = [40, 36, 44, 38, 130, 42, 35]
    for i, b in enumerate(bars_a):
        x = ox + i * 46
        col = RED if dl - b * 1.0 < dl - 95 else GREEN
        over = b > 95
        s += rect(x, dl - b, 34, b, LRED if over else LGRN, RED if over else GREEN, 1.4, 2)
    s += line(ox - 6, dl - 95, ox + 7 * 46, dl - 95, INK, 2, dash="6,3")
    s += text(ox - 10, dl - 95 + 4, "дедлайн", 8.2, INK, "end", "bold")
    s += text(230, dl + 22, "✗ один сплеск зірвав дедлайн", 8.8, RED, "middle", "bold")
    # система B — рівна, завжди в межах
    ox2 = 560
    s += text(710, 92, "Не найшвидша, та ЗАВЖДИ в межах", 10, GREEN, "middle", "bold")
    bars_b = [70, 74, 68, 72, 76, 70, 73]
    for i, b in enumerate(bars_b):
        x = ox2 + i * 46
        s += rect(x, dl - b, 34, b, LGRN, GREEN, 1.4, 2)
    s += line(ox2 - 6, dl - 95, ox2 + 7 * 46, dl - 95, INK, 2, dash="6,3")
    s += text(ox2 + 7 * 46 + 6, dl - 95 + 4, "дедлайн", 8.2, INK, "start", "bold")
    s += text(710, dl + 22, "✓ жоден раз не перейшла межу", 8.8, GREEN, "middle", "bold")
    s += rect(150, 300, 660, 56, LAMB, GOLD, 1.4, 10)
    s += text(480, 324, "Реальний час обирає ПРАВУ систему: повільнішу в середньому, зате таку, що НІКОЛИ", 9.6, INK, "middle", "bold")
    s += text(480, 344, "не запізнюється понад межу. Передбачуваність важливіша за рекордну швидкість.", 9.2, GREY, "middle")
    save("fig-27-8-1-predictable.svg", s)


# ── Рис. 27.8.2 — жорсткий і м'який реальний час ─────────────────────────────
def fig82_hard_soft():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 32, "Дедлайн: жорсткий і м'який реальний час", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "встигнути до строку; різниця — у ціні запізнення", 10.3, GREY, "middle", style="italic")
    s += rect(70, 90, 400, 200, LRED, RED, 1.8, 12)
    s += text(270, 116, "ЖОРСТКИЙ", 13, RED, "middle", "bold")
    s += text(270, 138, "зрив дедлайну = ВІДМОВА", 9.6, INK, "middle", "bold")
    s += text(90, 170, "• подушка безпеки авто", 9.6, INK, "start")
    s += text(90, 194, "• керування мотором/верстатом", 9.6, INK, "start")
    s += text(90, 218, "• кардіостимулятор", 9.6, INK, "start")
    s += text(270, 256, "запізнився — катастрофа,", 9, RED, "middle", "bold")
    s += text(270, 274, "строк абсолютний", 8.6, GREY, "middle")
    s += rect(490, 90, 400, 200, LGRN, GREEN, 1.8, 12)
    s += text(690, 116, "М'ЯКИЙ", 13, GREEN, "middle", "bold")
    s += text(690, 138, "зрив = ПОГІРШЕННЯ якості", 9.6, INK, "middle", "bold")
    s += text(510, 170, "• звук (інколи «затинка»)", 9.6, INK, "start")
    s += text(510, 194, "• відео (пропущений кадр)", 9.6, INK, "start")
    s += text(510, 218, "• оновлення дисплея", 9.6, INK, "start")
    s += text(690, 256, "запізнився зрідка — терпимо,", 9, GREEN, "middle", "bold")
    s += text(690, 274, "аби не часто", 8.6, GREY, "middle")
    s += text(W / 2, 320, "Знай, який реальний час тобі потрібен: жорсткий вимагає суворого аналізу, м'який — поблажливіший.", 9.2, INK, "middle", "bold")
    save("fig-27-8-2-hard-soft.svg", s)


# ── Рис. 27.8.3 — детермінованість: обмежений найгірший випадок ───────────────
def fig83_determinism():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 32, "Детермінованість: знати й обмежити НАЙГІРШИЙ випадок", 16.5, INK, "middle", "bold")
    s += text(W / 2, 54, "RTOS гарантує, що відгук укладеться у відомий стелевий час — це й дає змогу обіцяти дедлайн", 9.4, GREY, "middle", style="italic")
    ox, base = 90, 240
    # розкид часів відгуку
    s += line(ox, base, 760, base, INK, 1.6)
    s += text(ox, base + 22, "час відгуку →", 9, INK, "start", "bold")
    import math as _m
    pts = []
    for i in range(201):
        x = ox + 520 * i / 200
        c = 250
        y = base - 120 * _m.exp(-((i - 70) ** 2) / 500)
        pts.append((x, y))
    s += poly(pts, BLUE, 2)
    s += text(ox + 180, base - 130, "типово (середнє)", 9, BLUE, "middle", "bold")
    # межа найгіршого випадку
    wx = ox + 520 * 0.86
    s += line(wx, base - 150, wx, base, RED, 2.4)
    s += text(wx, base - 158, "СТЕЛЯ (найгірший випадок)", 9.2, RED, "middle", "bold")
    s += line(wx, base - 150, 770, base - 150, RED, 1.6, dash="5,3")
    s += text(wx + 90, base + 22, "далі — ніколи", 8.6, RED, "start", "bold")
    s += rect(150, 280, 660, 70, LBLUE, BLUE, 1.4, 12)
    s += text(480, 304, "Звичайна ОС оптимізує СЕРЕДНЄ, та її найгірший випадок може бути необмеженим.", 9.4, INK, "middle", "bold")
    s += text(480, 324, "RTOS натомість обмежує НАЙГІРШИЙ: затримку переривань, перемикання, роботу планувальника.", 9.2, INK, "middle", "bold")
    s += text(480, 343, "Гарантувати можна лише те, чий найгірший випадок ти знаєш.", 8.8, GREEN, "middle", "bold")
    save("fig-27-8-3-determinism.svg", s)


# ── Рис. 27.8.4 — пріоритети кодують терміновість ────────────────────────────
def fig84_priorities():
    W, H = 960, 370
    s = header(W, H)
    s += text(W / 2, 32, "Пріоритети — це закодовані дедлайни", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "найтерміновіша задача отримує найвищий пріоритет — і витісняє все, щоб устигнути", 9.8, GREY, "middle", style="italic")
    rows = [
        ("керування мотором", "кожні 1 мс — тісно", "ВИСОКИЙ", RED),
        ("опитування кнопок", "кожні 20 мс", "середній", GOLD),
        ("оновлення дисплея", "кожні 200 мс — вільно", "низький", BLUE),
    ]
    y = 96
    for task, deadline, prio, col in rows:
        s += rect(70, y, 300, 56, "#fbfcff", GREY, 1.3, 8)
        s += text(90, y + 26, task, 10.5, INK, "start", "bold")
        s += text(90, y + 44, deadline, 8.6, GREY, "start")
        s += arrow(380, y + 28, 430, y + 28, INK, 2)
        s += rect(440, y, 200, 56, "#f4f6fb", col, 1.8, 8)
        s += text(540, y + 32, prio, 11, col, "middle", "bold")
        y += 72
    s += rect(680, 96, 220, 200, LGRN, GREEN, 1.4, 12)
    s += text(790, 122, "правило (rate-", 9.6, GREEN, "middle", "bold")
    s += text(790, 138, "monotonic):", 9.6, GREEN, "middle", "bold")
    s += text(700, 166, "що частіше / тісніший", 9, INK, "start")
    s += text(700, 184, "дедлайн — то ВИЩИЙ", 9, INK, "start")
    s += text(700, 202, "пріоритет.", 9, INK, "start")
    s += text(700, 232, "Критична задача витісняє", 8.6, GREY, "start")
    s += text(700, 248, "решту й завжди встигає", 8.6, GREY, "start")
    s += text(700, 264, "до свого строку.", 8.6, GREY, "start")
    save("fig-27-8-4-priorities.svg", s)


# ── Рис. 27.8.5 — вороги реального часу ──────────────────────────────────────
def fig85_enemies():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 32, "Вороги реального часу: що руйнує передбачуваність", 16.5, INK, "middle", "bold")
    s += text(W / 2, 54, "уникай їх на критичному шляху, інакше найгірший випадок «попливе»", 9.8, GREY, "middle", style="italic")
    cards = [
        (60, "Інверсія пріоритетів", RED, ["низька тримає замок,", "висока чекає (§27.6)", "→ успадкування пріор."]),
        (320, "Задовге блокування", GOLD, ["тримаєш замок/чекаєш", "надто довго", "→ тримай коротко"]),
        (580, "Необмежені операції", BLUE, ["купа, довга ISR,", "busy-wait, рекурсія", "→ геть із критичного"]),
    ]
    for x, title, col, lines in cards:
        s += rect(x, 90, 280, 150, "#fbfcff", col, 1.8, 12)
        s += text(x + 140, 116, title, 10.5, col, "middle", "bold")
        s += line(x + 20, 126, x + 260, 126, FAINT, 1.2)
        yy = 150
        for ln in lines:
            s += text(x + 140, yy, ln, 9, INK, "middle")
            yy += 24
    s += rect(150, 264, 660, 80, LAMB, GOLD, 1.4, 12)
    s += text(480, 290, "Плюс ГОЛОДУВАННЯ (§27.4): зажерлива високопріоритетна задача не дає бігти нижчим.", 9.4, INK, "middle", "bold")
    s += text(480, 312, "Усі ці вороги мають одне спільне: вони роблять найгірший випадок невідомим або величезним —", 9.2, INK, "middle", "bold")
    s += text(480, 330, "а без відомого найгіршого випадку гарантувати реальний час неможливо.", 8.8, GREY, "middle")
    save("fig-27-8-5-enemies.svg", s)


# ── Рис. 27.8.6 — як усе сходиться: від super-loop до реального часу ──────────
def fig86_convergence():
    W, H = 980, 360
    s = header(W, H)
    s += text(W / 2, 32, "Як усе сходиться: увесь розділ вів до реального часу", 16.5, INK, "middle", "bold")
    s += text(W / 2, 54, "від простого циклу без жодних гарантій — до системи, що встигає вчасно гарантовано", 9.6, GREY, "middle", style="italic")
    steps = [
        ("Super-loop", "§27.1–2", GREY, "просто, та без гарантій"),
        ("Задачі", "§27.3", GREEN, "кожна — проста програма"),
        ("Планувальник", "§27.4", GOLD, "пріоритети, витіснення"),
        ("FreeRTOS", "§27.5", BLUE, "ядро + два ядра ESP32"),
        ("Обмін", "§27.6", PURP, "черги, м'ютекси"),
        ("Реальний час", "§27.8", RED, "ГАРАНТОВАНО вчасно"),
    ]
    n = len(steps)
    bw = 138
    gap = (980 - n * bw) / (n + 1)
    y = 110
    for i, (lab, sec, col, note) in enumerate(steps):
        x = gap + i * (bw + gap)
        hot = i == n - 1
        s += rect(x, y, bw, 84, LRED if hot else "#fbfcff", col, 2.4 if hot else 1.6, 10)
        s += text(x + bw / 2, y + 30, lab, 10.5, col, "middle", "bold")
        s += text(x + bw / 2, y + 48, sec, 8.4, GREY, "middle")
        s += text(x + bw / 2, y + 70, note, 7.6, INK, "middle")
        if i < n - 1:
            s += arrow(x + bw + 2, y + 42, x + bw + gap - 2, y + 42, INK, 2)
    s += rect(150, 240, 680, 100, LGRN, GREEN, 1.5, 12)
    s += text(490, 268, "Super-loop не міг ОБІЦЯТИ час; задачі з пріоритетним витісненням, обмеженими", 9.6, INK, "middle", "bold")
    s += text(490, 290, "затримками RTOS і дбайливим дизайном — можуть. Це й є реальний час:", 9.6, INK, "middle", "bold")
    s += text(490, 314, "не «якось працює», а «гарантовано встигає». Сюди вів увесь розділ — і весь Модуль 4.", 9.4, GREEN, "middle", "bold")
    save("fig-27-8-6-convergence.svg", s)


if __name__ == "__main__":
    # 📜 Історія до розділу — поділ часу (CTSS, 1961)
    figh1_the_question()
    figh2_utilization()
    figh3_timeline()
    figh4_mechanism()
    figh5_legacy()
    # §27.1 Super-loop
    fig11_setup_loop()
    fig12_under_hood()
    fig13_read_compute_act()
    fig14_foreground_background()
    fig15_loop_timing()
    fig16_several_jobs()
    # §27.2 Чому super-loop не масштабується
    fig21_blocking()
    fig22_responsiveness()
    fig23_millis_limit()
    fig24_state_explosion()
    fig25_no_priority()
    fig26_what_we_want()
    # §27.3 Задачі (tasks)
    fig31_task_is_program()
    fig32_block_no_freeze()
    fig33_own_stack()
    fig34_states()
    fig35_xtaskcreate()
    fig36_illusion()
    # §27.4 Планувальник
    fig41_scheduler()
    fig42_triggers()
    fig43_cooperative()
    fig44_preemptive()
    fig45_tick()
    fig46_freertos_rule()
    # §27.5 RTOS і FreeRTOS на ESP32
    fig51_what_is_rtos()
    fig52_freertos()
    fig53_two_cores()
    fig54_illusion_vs_real()
    fig55_pinning()
    fig56_shared_harder()
    # §27.6 Обмін між задачами
    fig61_problem()
    fig62_queue()
    fig63_semaphore()
    fig64_mutex()
    fig65_mutex_vs_sem()
    fig66_decision()
    # §27.7 Пам'ять у RTOS: стеки задач
    fig71_stack_contents()
    fig72_overflow()
    fig73_ram_budget()
    fig74_high_water()
    fig75_big_array()
    fig76_stack_vs_heap()
    # §27.8 Реальний час: детермінованість і пріоритети
    fig81_predictable()
    fig82_hard_soft()
    fig83_determinism()
    fig84_priorities()
    fig85_enemies()
    fig86_convergence()
    print("OK - figures for Section 27 (27.0.x..27.8.x) generated in", OUT)
