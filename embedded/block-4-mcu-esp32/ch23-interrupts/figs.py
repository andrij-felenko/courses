# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 23 — «Переривання» (Модуль 4).
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
# Історія розділу (📜) — fig-23-0-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 23.0.1 — опитування проти переривання ───────────────────────────────
def fig01_polling_vs_interrupt():
    W, H = 920, 430
    s = header(W, H)
    s += text(W / 2, 32, "Дві стратегії: опитувати самому чи чекати «дзвоника»", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "стара ідея — раз у раз перепитувати; нова — дозволити пристрою покликати самому", 11.5, GREY, "middle", style="italic")
    # left: polling
    s += rect(40, 84, 400, 320, "none", FAINT, 1.6, 12)
    s += text(240, 110, "Опитування (polling)", 13, RED, "middle", "bold")
    s += rect(90, 150, 130, 60, LBLUE, BLUE, 1.6, 8)
    s += text(155, 180, "процесор", 11, INK, "middle", "bold")
    s += rect(300, 150, 110, 60, "#fbfcff", INK, 1.6, 8)
    s += text(355, 176, "пристрій", 10, INK, "middle", "bold")
    s += text(355, 196, "(повільний)", 8.5, GREY, "middle")
    s += arrow(220, 168, 300, 168, INK, 1.8)
    s += text(260, 160, "«готово?»", 8.5, INK, "middle")
    s += arrow(300, 192, 220, 192, GREY, 1.8)
    s += text(260, 204, "«ще ні»", 8.5, GREY, "middle")
    s += f'<path d="M 120 220 q -40 40 30 60 q 70 18 70 -30" fill="none" stroke="{RED}" stroke-width="2" stroke-dasharray="4,3" marker-end="url(#aRed)"/>\n'
    s += text(170, 300, "крутиться в циклі", 10.5, RED, "middle", "bold")
    s += text(240, 330, "і марнує весь час на перепитування,", 10, INK, "middle")
    s += text(240, 350, "навіть коли нічого не відбувається", 10, GREY, "middle", style="italic")
    s += text(240, 382, "= як бігати до дверей щохвилини", 10, RED, "middle", "bold")
    # right: interrupt
    s += rect(480, 84, 400, 320, "none", FAINT, 1.6, 12)
    s += text(680, 110, "Переривання (interrupt)", 13, GREEN, "middle", "bold")
    s += rect(530, 150, 130, 60, LBLUE, BLUE, 1.6, 8)
    s += text(595, 174, "процесор", 11, INK, "middle", "bold")
    s += text(595, 194, "робить СВОЮ роботу", 8, GREEN, "middle")
    s += rect(740, 150, 110, 60, "#fbfcff", INK, 1.6, 8)
    s += text(795, 176, "пристрій", 10, INK, "middle", "bold")
    s += text(795, 196, "(сам кличе)", 8.5, GREY, "middle")
    s += arrow(740, 240, 660, 240, RED, 2.4)
    s += text(700, 230, "↯ «дзвоник!»", 10, RED, "middle", "bold")
    s += text(680, 300, "процесор кидає все ТІЛЬКИ коли є подія,", 10, INK, "middle")
    s += text(680, 320, "обробляє її й вертається до роботи", 10, GREY, "middle", style="italic")
    s += text(680, 352, "= як почути дзвоник у двері", 10, GREEN, "middle", "bold")
    s += text(680, 382, "— реагуєш умить, не марнуєш часу", 10, GREEN, "middle")
    save("fig-23-0-1-polling-vs-interrupt.svg", s)


# ── Рис. 23.0.2 — хронологія перших переривань ───────────────────────────────
def fig02_timeline():
    W, H = 980, 360
    s = header(W, H)
    s += text(W / 2, 32, "Хто був «першим»? Залежить від визначення", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "переривання з'являлися паралельно в кількох машинах середини 1950-х", 12, GREY, "middle", style="italic")
    x0, x1 = 80, 900
    y = 150
    s += line(x0, y, x1, y, INK, 2.2)
    for yr, xx in [("1953", 80), ("1954", 230), ("1955", 410), ("1956", 590), ("1957", 770), ("1958", 900)]:
        s += line(xx, y - 6, xx, y + 6, INK, 1.6)
        s += text(xx, y + 24, yr, 11, INK, "middle", "bold")
    items = [
        (80, 1, "ERA 1103", "ще БЕЗ переривань", GREY, "(міф про «1953» — у мануалі їх нема)"),
        (230, -1, "DYSEAC (NBS)", "перше I/O-переривання", GREEN, "два лічильники команд; армія, 1954"),
        (430, 1, "NACA 1103", "Тернер і Ролінгс", BLUE, "переривання для аеродинам. труби, 1955"),
        (600, -1, "1103A", "перше комерційне", BLUE, "робоче з лют. 1956"),
        (775, 1, "IBM Stretch", "Брукс: маска+вектор", RED, "пріоритети, 1957"),
    ]
    for xx, d, t, sub, col, note in items:
        yb = y - 86 if d > 0 else y + 52
        s += line(xx, y, xx, yb + (40 if d > 0 else 0), col, 1.6, dash="3,3")
        ry = yb if d > 0 else yb
        s += rect(xx - 86, ry, 172, 46, "#fbfcff", col, 1.6, 8)
        s += text(xx, ry + 19, t, 11, col, "middle", "bold")
        s += text(xx, ry + 36, sub, 8.7, INK, "middle")
        ny = ry - 12 if d > 0 else ry + 60
        s += text(xx, ny, note, 7.8, GREY, "middle")
    s += text(W / 2, 332, "DYSEAC (1954) — перше I/O-переривання; 1103A (1956) — перше комерційне; Stretch (1957) — маски й вектори.", 10.3, INK, "middle", "bold")
    save("fig-23-0-2-timeline.svg", s)


# ── Рис. 23.0.3 — мотив: аеродинамічна труба ─────────────────────────────────
def fig03_wind_tunnel():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 32, "Навіщо це знадобилося: реальний час аеродинамічної труби", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "виміри приходять у НЕпередбачувані моменти — їх треба ловити вмить, не чекаючи", 11, GREY, "middle", style="italic")
    # tunnel
    s += poly([(70, 150), (250, 150), (300, 175), (300, 245), (250, 270), (70, 270), (70, 150)], INK, 2, "#f4f8ff")
    s += text(175, 135, "аеродинамічна труба", 11, INK, "middle", "bold")
    s += arrow(40, 175, 70, 175, BLUE, 2.2)
    s += arrow(40, 210, 70, 210, BLUE, 2.2)
    s += arrow(40, 245, 70, 245, BLUE, 2.2)
    s += text(30, 300, "потік повітря", 9.5, BLUE, "start")
    # model + sensors
    s += poly([(150, 210), (200, 200), (205, 210), (150, 220)], INK, 1.6, METAL)
    s += text(178, 240, "модель", 8.5, INK, "middle")
    for sx, sy in [(120, 175), (170, 195), (210, 230), (140, 255)]:
        s += circle(sx, sy, 4, LRED, RED, 1.6)
    s += text(175, 288, "датчики тиску/сили", 8.5, RED, "middle")
    # data arrivals at irregular times -> computer
    s += rect(640, 150, 220, 120, "none", BLUE, 2, 12)
    s += text(750, 178, "комп'ютер (1103)", 12, BLUE, "middle", "bold")
    s += text(750, 202, "має схопити КОЖЕН", 10, INK, "middle")
    s += text(750, 220, "вимір тієї ж миті", 10, INK, "middle")
    s += text(750, 244, "→ не можна «бути зайнятим»", 9, RED, "middle", "bold")
    for yy, lab in [(180, "t1"), (210, "t2"), (245, "t3")]:
        s += arrow(310, yy, 640, yy, RED, 1.8, dash="4,3")
    s += text(470, 168, "виміри надходять нерівномірно (t1, t2, t3 …)", 9.5, RED, "middle", "bold")
    s += text(470, 300, "Опитуванням такі випадкові події легко проґавити —", 10.5, INK, "middle")
    s += text(470, 320, "тому й додали переривання: пристрій сам кличе процесор.", 10.5, GREEN, "middle", "bold")
    save("fig-23-0-3-wind-tunnel.svg", s)


# ── Рис. 23.0.4 — як це працює: відволіктися й повернутися ────────────────────
def fig04_mechanism():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 32, "Механізм: відірватися, обробити, повернутися", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "процесор запам'ятовує, де спинився, виконує обробник і вертається точно туди ж", 11, GREY, "middle", style="italic")
    y = 150
    # main program line
    s += text(70, y - 24, "основна програма", 10.5, INK, "start", "bold")
    s += arrow(70, y, 360, y, BLUE, 2.6)
    s += circle(360, y, 5, RED, RED, 0)
    s += text(360, y - 14, "↯ сигнал від пристрою", 9.5, RED, "middle", "bold")
    # detour down to handler
    s += line(360, y, 360, y + 60, INK, 2, dash="4,3")
    s += text(372, y + 30, "зберегти, де спинилися (контекст)", 9, INK, "start")
    s += rect(300, y + 60, 320, 60, LGRN, GREEN, 1.8, 10)
    s += text(460, y + 86, "обробник переривання (ISR)", 11, GREEN, "middle", "bold")
    s += text(460, y + 104, "коротко зробити те, що треба", 9, INK, "middle")
    s += line(620, y + 90, 700, y + 90, INK, 2)
    s += line(700, y + 90, 700, y, INK, 2, dash="4,3")
    s += text(712, y + 50, "відновити контекст", 9, INK, "start")
    # resume
    s += arrow(700, y, 880, y, BLUE, 2.6)
    s += text(790, y - 14, "далі, мов нічого не було", 9.5, BLUE, "middle", "bold")
    s += rect(150, 320, 620, 44, LAMB, GOLD, 1.4, 8)
    s += text(460, 339, "Ключ — зберегти й відновити «де я був»: інакше процесор забув би думку.", 10.5, INK, "middle", "bold")
    s += text(460, 357, "У 1103A перехід вів у фіксовану комірку 2; DYSEAC перемикав другий лічильник команд.", 9.3, GREY, "middle")
    save("fig-23-0-4-mechanism.svg", s)


# ── Рис. 23.0.5 — маска й вектор (Stretch) ───────────────────────────────────
def fig05_mask_vector():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Внесок Stretch (Брукс, 1957): маска й вектор переривань", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "які переривання дозволені (маска) і куди стрибати по кожному (вектор)", 11.5, GREY, "middle", style="italic")
    # mask register
    s += text(220, 100, "Маска: дозволити / заборонити", 12, INK, "middle", "bold")
    bits = [1, 0, 1, 1, 0, 1, 0, 0]
    for i, b in enumerate(bits):
        cx = 70 + i * 46
        s += rect(cx, 116, 46, 46, (LGRN if b else "#f0f0f0"), (GREEN if b else GREY), 1.6)
        s += text(cx + 23, 145, ("1" if b else "0"), 15, (GREEN if b else GREY), "middle", "bold")
    s += text(220, 184, "1 = переривання дозволене, 0 = замаскований (ігнорується)", 9, GREY, "middle")
    s += text(220, 210, "→ можна тимчасово «не відволікатися» на дрібниці", 9.5, INK, "middle", "bold")
    # vector table
    s += text(720, 100, "Вектор: таблиця адрес обробників", 12, INK, "middle", "bold")
    rows = [("джерело 0 (таймер)", "→ адреса H0"), ("джерело 1 (ввід)", "→ адреса H1"), ("джерело 2 (помилка)", "→ адреса H2")]
    for i, (a, b) in enumerate(rows):
        yy = 120 + i * 40
        s += rect(540, yy, 200, 32, "#fbfcff", BLUE, 1.4, 6)
        s += text(550, yy + 21, a, 10, INK, "start")
        s += rect(760, yy, 130, 32, LBLUE, BLUE, 1.4, 6)
        s += text(770, yy + 21, b, 10, BLUE, "start", "bold")
    s += text(720, 258, "кожне джерело → свій обробник, без довгих перевірок", 9.5, INK, "middle", "bold")
    # footer note
    s += rect(120, 300, 700, 70, "none", FAINT, 1.6, 10)
    s += text(470, 326, "Так переривання стало керованим: пріоритети, маскування, кілька програм водночас.", 10.5, INK, "middle", "bold")
    s += text(470, 350, "Ці ідеї — маска й вектор — живуть і досі, зокрема в ESP32 (побачимо в темах розділу).", 9.7, GREY, "middle")
    save("fig-23-0-5-mask-vector.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §23.1 Переривання: реагувати на подію вмить — fig-23-1-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 23.1.1 — опитування в циклі: затримка й пропуск ──────────────────────
def fig11_polling_in_loop():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 32, "Опитування в loop(): реакція спізнюється, подію легко проґавити", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "поки цикл зайнятий іншим, натиск кнопки чекає своєї черги — або зникає непоміченим", 11, GREY, "middle", style="italic")
    y = 150
    tasks = [("читати\nдавач", 90, 120), ("оновити\nекран", 230, 200), ("перевірити\nкнопку", 450, 120), ("інша\nробота", 590, 170)]
    for lab, x, w in tasks:
        col = GREEN if "кнопку" in lab else GREY
        s += rect(x, y, w, 50, (LGRN if "кнопку" in lab else "#f2f2f2"), col, 1.6, 8)
        ls = lab.split("\n")
        s += text(x + w / 2, y + 22, ls[0], 9.5, INK, "middle", "bold")
        s += text(x + w / 2, y + 38, ls[1], 9.5, INK, "middle", "bold")
    s += arrow(80, y - 30, 770, y - 30, INK, 1.6)
    s += text(776, y - 26, "час", 9, INK, "start")
    s += line(70, y + 25, 90, y + 25, INK, 2)
    s += line(770, y + 25, 800, y + 25, INK, 2)
    s += text(800, y + 29, "↻ знову", 9, GREY, "start")
    # event arrives during 'update screen', check only later
    ex = 300
    s += line(ex, y + 50, ex, y + 110, RED, 2)
    s += circle(ex, y + 50, 4, RED, RED, 0)
    s += text(ex, y + 128, "натиск кнопки тут", 9.5, RED, "middle", "bold")
    cx = 510
    s += line(cx, y, cx, y + 110, GREEN, 2, dash="4,3")
    s += text(cx, y + 128, "перевірено аж тут", 9.5, GREEN, "middle", "bold")
    s += line(ex, y + 98, cx, y + 98, INK, 1.6)
    s += text((ex + cx) / 2, y + 92, "затримка реакції", 9, INK, "middle", "bold")
    s += rect(120, 320, 700, 70, LAMB, GOLD, 1.4, 8)
    s += text(470, 346, "Що довший цикл, то пізніша реакція. А коротку подію (швидкий імпульс)", 10.5, INK, "middle", "bold")
    s += text(470, 368, "опитування може взагалі не застати — між двома перевірками вона зникне.", 10, GREY, "middle")
    save("fig-23-1-1-polling-in-loop.svg", s)


# ── Рис. 23.1.2 — три виграші переривання ────────────────────────────────────
def fig12_interrupt_benefits():
    W, H = 920, 360
    s = header(W, H)
    s += text(W / 2, 32, "Що дає переривання: три виграші", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "подія сама кличе процесор — і це міняє все", 12, GREY, "middle", style="italic")
    cards = [
        (60, "Миттєва реакція", ["процесор відгукується", "за мікросекунди після", "події, а не «колись потім»"], GREEN),
        (340, "Процесор вільний", ["поки події нема — ядро", "робить свою роботу, а не", "крутить порожній цикл"], BLUE),
        (620, "Нічого не проґавиш", ["навіть коротку подію", "залізо зафіксує й покличе", "обробник вчасно"], RED),
    ]
    for ox, t, lines, col in cards:
        s += rect(ox, 90, 240, 220, "#fbfcff", col, 1.8, 12)
        s += text(ox + 120, 122, t, 13.5, col, "middle", "bold")
        s += line(ox + 20, 136, ox + 220, 136, col, 1.2)
        yy = 170
        for ln in lines:
            s += text(ox + 120, yy, ln, 10.5, INK, "middle")
            yy += 24
    s += text(W / 2, 338, "Ціна — складніший код: обробник треба писати обережно (про це далі в розділі).", 10.5, INK, "middle", "bold")
    save("fig-23-1-2-interrupt-benefits.svg", s)


# ── Рис. 23.1.3 — потік переривання ──────────────────────────────────────────
def fig13_interrupt_flow():
    W, H = 920, 360
    s = header(W, H)
    s += text(W / 2, 32, "Як це відбувається: пауза → обробник → повернення", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "процесор кидає основний код, виконує короткий обробник і вертається точно туди ж", 11, GREY, "middle", style="italic")
    y = 170
    s += text(70, y - 26, "основний код (loop)", 10.5, BLUE, "start", "bold")
    s += arrow(70, y, 350, y, BLUE, 2.6)
    s += circle(350, y, 5, RED, RED, 0)
    s += text(350, y - 14, "↯ подія на ніжці", 9.5, RED, "middle", "bold")
    s += line(350, y, 350, y + 56, INK, 2, dash="4,3")
    s += text(362, y + 30, "пауза, зберегти контекст", 9, INK, "start")
    s += rect(290, y + 56, 320, 58, LGRN, GREEN, 1.8, 10)
    s += text(450, y + 81, "обробник (ISR)", 12, GREEN, "middle", "bold")
    s += text(450, y + 100, "коротко зробити потрібне", 9, INK, "middle")
    s += line(610, y + 85, 690, y + 85, INK, 2)
    s += line(690, y + 85, 690, y, INK, 2, dash="4,3")
    s += text(702, y + 46, "відновити контекст", 9, INK, "start")
    s += arrow(690, y, 880, y, BLUE, 2.6)
    s += text(800, y - 14, "далі, мов нічого не було", 9.3, BLUE, "middle", "bold")
    s += text(W / 2, 330, "Збереження й відновлення «де я був» ESP32 робить за вас — ви пишете лише сам обробник.", 10.5, INK, "middle", "bold")
    save("fig-23-1-3-interrupt-flow.svg", s)


# ── Рис. 23.1.4 — анатомія attachInterrupt ───────────────────────────────────
def fig14_attach_interrupt():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 32, "Як підключити переривання в коді: attachInterrupt", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "три речі: яка ніжка, яка функція-обробник і на яку подію", 12, GREY, "middle", style="italic")
    s += rect(120, 110, 680, 56, "#0f1115", INK, 1.6, 10)
    s += f'<text x="140" y="146" font-family="Consolas, monospace" font-size="17" fill="#e8e8e8" font-weight="bold">attachInterrupt(<tspan fill="#7fb4ff">digitalPinToInterrupt(PIN)</tspan>, <tspan fill="#7ee0a0">onPress</tspan>, <tspan fill="#ff8a7a">FALLING</tspan>);</text>\n'
    parts = [
        (250, "1 · яка ніжка", "digitalPinToInterrupt(PIN)", BLUE),
        (480, "2 · обробник (ISR)", "onPress — ваша функція", GREEN),
        (650, "3 · подія", "FALLING / RISING / CHANGE", RED),
    ]
    xcards = [(60, parts[0]), (340, parts[1]), (620, parts[2])]
    for ox, (px, t, d, col) in xcards:
        s += line(px, 166, px, 210, col, 1.6, dash="3,3")
        s += rect(ox, 210, 240, 90, "#fbfcff", col, 1.8, 12)
        s += text(ox + 120, 238, t, 12, col, "middle", "bold")
        s += text(ox + 120, 264, d, 9.5, INK, "middle")
        s += text(ox + 120, 286, ("спад / наростання / зміна" if col == RED else ("викликається на подію" if col == GREEN else "номер «лінії» переривання")), 8.7, GREY, "middle")
    s += text(W / 2, 338, "FALLING — спад (натиск кнопки з підтяжкою), RISING — наростання, CHANGE — будь-яка зміна.", 10.3, INK, "middle", "bold")
    s += text(W / 2, 360, "Сам обробник: void onPress() { … } — короткий і обережний (правила — у §23.3).", 9.7, GREY, "middle")
    save("fig-23-1-4-attach-interrupt.svg", s)


# ── Рис. 23.1.5 — час реакції ────────────────────────────────────────────────
def fig15_latency():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 32, "Час реакції: опитування «колись», переривання — вмить", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "опитування реагує в межах періоду циклу; переривання — за мікросекунди", 11.5, GREY, "middle", style="italic")
    ex = 250
    # polling timeline
    yP = 150
    s += text(70, yP - 24, "Опитування", 11, RED, "start", "bold")
    s += line(120, yP, 860, yP, INK, 1.6)
    for i in range(5):
        cxp = 160 + i * 150
        s += line(cxp, yP - 5, cxp, yP + 5, GREY, 1.4)
        s += text(cxp, yP + 18, "перевірка", 7.5, GREY, "middle")
    s += line(ex, yP - 40, ex, yP, RED, 2)
    s += circle(ex, yP - 40, 4, RED, RED, 0)
    s += text(ex, yP - 48, "подія", 9, RED, "middle", "bold")
    s += arrow(ex, yP - 30, 310, yP - 30, RED, 2)
    s += text(360, yP - 34, "чекає до наступної перевірки (до цілого періоду циклу)", 9, RED, "start", "bold")
    # interrupt timeline
    yI = 270
    s += text(70, yI - 24, "Переривання", 11, GREEN, "start", "bold")
    s += line(120, yI, 860, yI, INK, 1.6)
    s += line(ex, yI - 40, ex, yI, GREEN, 2)
    s += circle(ex, yI - 40, 4, GREEN, GREEN, 0)
    s += text(ex, yI - 48, "подія", 9, GREEN, "middle", "bold")
    s += arrow(ex, yI - 20, ex + 26, yI - 20, GREEN, 2)
    s += text(ex + 32, yI - 16, "обробник майже відразу (~мікросекунди)", 9, GREEN, "start", "bold")
    s += text(W / 2, 350, "Для рідкісних чи коротких подій різниця між «вмить» і «колись» — вирішальна.", 10.5, INK, "middle", "bold")
    save("fig-23-1-5-latency.svg", s)


# ── Рис. 23.1.6 — опитування проти переривання: коли що ───────────────────────
def fig16_polling_vs_interrupt():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 32, "Опитування чи переривання: коротке порівняння", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "обидва потрібні; вибір — за задачею (докладно у §23.7)", 12, GREY, "middle", style="italic")
    cols = [(330, "Опитування", RED), (630, "Переривання", GREEN)]
    s += text(170, 96, "", 11, INK, "middle", "bold")
    for x, t, col in cols:
        s += rect(x - 130, 80, 260, 34, ("#fbecec" if col == RED else "#eef6ef"), col, 1.6, 8)
        s += text(x, 103, t, 12.5, col, "middle", "bold")
    rows = [
        ("Реакція", "у межах періоду циклу", "майже миттєва (мкс)"),
        ("Навантаження CPU", "марнує час на перевірки", "ядро вільне між подіями"),
        ("Складність коду", "проста, передбачувана", "вища: обережний обробник"),
        ("Коли доречно", "часті/очікувані події", "рідкісні/термінові події"),
    ]
    y = 130
    for name, a, b in rows:
        s += rect(40, y, 200, 52, "#f7f7f7", GREY, 1.2, 6)
        s += text(50, y + 31, name, 11, INK, "start", "bold")
        s += rect(250, y, 240, 52, "#fff", RED, 1.2, 6)
        s += text(370, y + 31, a, 9.7, INK, "middle")
        s += rect(500, y, 240, 52, "#fff", GREEN, 1.2, 6)
        s += text(620, y + 31, b, 9.7, INK, "middle")
        y += 60
    s += text(W / 2, 368, "Правило-орієнтир: рідкісне й термінове — перериванням; часте й рівномірне — опитуванням.", 10.3, INK, "middle", "bold")
    save("fig-23-1-6-polling-vs-interrupt.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §23.2 Контролер переривань і вектор — fig-23-2-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 23.2.1 — контролер переривань як регулювальник ───────────────────────
def fig21_controller():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Контролер переривань: регулювальник між пристроями і ядром", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "збирає запити від багатьох джерел, відсіює заборонені, обирає важливіший — і кличе ядро", 11, GREY, "middle", style="italic")
    srcs = [("таймер", 110), ("GPIO", 170), ("UART", 230), ("…", 290)]
    for lab, yy in srcs:
        s += rect(60, yy, 120, 44, "#fbfcff", INK, 1.4, 8)
        s += text(120, yy + 27, lab, 10.5, INK, "middle", "bold")
        col = RED if lab == "GPIO" else GREY
        s += arrow(180, yy + 22, 360, 200, col, (2.2 if lab == "GPIO" else 1.4), None if lab == "GPIO" else "3,3")
    s += text(120, 96, "джерела подій", 10, INK, "middle", "bold")
    s += rect(360, 150, 230, 120, LAMB, GOLD, 2, 12)
    s += text(475, 178, "контролер переривань", 12, INK, "middle", "bold")
    s += text(475, 204, "• дозволено? (маска)", 9.5, INK, "middle")
    s += text(475, 224, "• який пріоритет?", 9.5, INK, "middle")
    s += text(475, 244, "• кого пустити першим", 9.5, INK, "middle")
    s += arrow(590, 210, 720, 210, RED, 2.6)
    s += text(655, 200, "переривання!", 9.5, RED, "middle", "bold")
    s += rect(720, 160, 160, 100, LBLUE, BLUE, 2, 12)
    s += text(800, 200, "процесор", 13, BLUE, "middle", "bold")
    s += text(800, 224, "(ядро)", 10, GREY, "middle")
    s += text(W / 2, 340, "Без контролера ядро потонуло б у сигналах: він — той, хто вирішує, КОГО і КОЛИ пускати.", 10.5, INK, "middle", "bold")
    s += text(W / 2, 362, "Тут активний GPIO (червоним); інші джерела поки мовчать.", 9.5, GREY, "middle", style="italic")
    save("fig-23-2-1-controller.svg", s)


# ── Рис. 23.2.2 — повний потік у вісім кроків ────────────────────────────────
def fig22_full_flow():
    W, H = 960, 430
    s = header(W, H)
    s += text(W / 2, 32, "Повний шлях переривання — крок за кроком", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "від сигналу пристрою до повернення в основний код — і все це за мікросекунди", 11.5, GREY, "middle", style="italic")
    steps = [
        ("1", "Джерело", "піднімає запит", GREY),
        ("2", "Контролер", "дозволено? пріоритет?", GOLD),
        ("3", "Сигнал", "у процесор", GREY),
        ("4", "Зберегти контекст", "(де я був + регістри)", BLUE),
        ("5", "Вектор", "знайти адресу обробника", GOLD),
        ("6", "Стрибок", "в обробник (ISR)", GREEN),
        ("7", "Обробник", "виконується", GREEN),
        ("8", "Відновити контекст", "далі, як було", BLUE),
    ]
    pos = [(40, 110), (260, 110), (480, 110), (700, 110), (700, 280), (480, 280), (260, 280), (40, 280)]
    for i, ((num, t, d, col), (x, y)) in enumerate(zip(steps, pos)):
        s += rect(x, y, 200, 64, "#fbfcff", col, 1.8, 10)
        s += circle(x + 20, y + 20, 13, col, col, 0)
        s += text(x + 20, y + 25, num, 12, "#ffffff", "middle", "bold")
        s += text(x + 116, y + 26, t, 11, INK, "middle", "bold")
        s += text(x + 116, y + 48, d, 8.7, GREY, "middle")
    # row1 L->R arrows
    for x in (240, 460, 680):
        s += arrow(x, 142, x + 20, 142, INK, 2)
    # down 4->5
    s += arrow(800, 174, 800, 280, INK, 2)
    # row2 R->L arrows
    for x in (700, 480, 260):
        s += arrow(x, 312, x - 20, 312, INK, 2)
    s += text(W / 2, 392, "Кроки 4 і 8 — серце механізму: зберегти й точно повернути «де я був». Решту робить залізо.", 10.5, INK, "middle", "bold")
    save("fig-23-2-2-full-flow.svg", s)


# ── Рис. 23.2.3 — таблиця-вектор ─────────────────────────────────────────────
def fig23_vector_table():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 32, "Вектор переривань: телефонна книга обробників", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "кожному номеру переривання зіставлено адресу його обробника — стрибаємо прямо туди", 11, GREY, "middle", style="italic")
    rows = [("0", "таймер", "0x4008_8120", False), ("1", "GPIO", "0x4008_81F4", True),
            ("2", "UART", "0x4008_8260", False), ("…", "…", "…", False), ("n", "інше", "0x4008_8xxx", False)]
    x0, y0 = 330, 96
    s += text(x0 + 130, y0 - 8, "вектор (таблиця адрес)", 10.5, INK, "middle", "bold")
    for i, (num, src, addr, hot) in enumerate(rows):
        yy = y0 + i * 46
        col = RED if hot else GREY
        s += rect(x0, yy, 60, 40, (LRED if hot else "#f4f4f4"), col, 1.4, 5)
        s += text(x0 + 30, yy + 26, num, 12, col, "middle", "bold")
        s += rect(x0 + 64, yy, 100, 40, "#ffffff", col, 1.2, 5)
        s += text(x0 + 114, yy + 25, src, 10, INK, "middle")
        s += rect(x0 + 168, yy, 160, 40, (LRED if hot else "#fbfcff"), col, 1.2, 5)
        s += text(x0 + 248, yy + 25, addr, 10.5, (RED if hot else INK), "middle", "bold")
    # incoming interrupt -> row 1
    s += rect(60, 150, 180, 80, LAMB, GOLD, 1.8, 10)
    s += text(150, 178, "прийшло переривання", 10, INK, "middle", "bold")
    s += text(150, 200, "№ 1 (GPIO)", 13, RED, "middle", "bold")
    s += arrow(240, 190, x0 - 6, y0 + 1 * 46 + 20, RED, 2.4)
    # jump to handler
    s += arrow(x0 + 330, y0 + 1 * 46 + 20, 760, y0 + 1 * 46 + 20, RED, 2.4)
    s += rect(760, y0 + 1 * 46, 120, 40, LGRN, GREEN, 1.6, 8)
    s += text(820, y0 + 1 * 46 + 25, "обробник", 10, GREEN, "middle", "bold")
    s += text(W / 2, 372, "Замість «перебрати всіх по черзі» — один погляд у вектор і прямий стрибок. Швидко й чітко.", 10.3, INK, "middle", "bold")
    save("fig-23-2-3-vector-table.svg", s)


# ── Рис. 23.2.4 — збереження контексту на стек ───────────────────────────────
def fig24_context_save():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 32, "Збереження контексту: закладка, щоб не забути думку", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "перед обробником ядро ховає на стек, «де воно було» й свої робочі значення, а потім повертає", 11, GREY, "middle", style="italic")
    # CPU registers
    s += rect(60, 110, 200, 200, "#fbfcff", BLUE, 1.8, 12)
    s += text(160, 134, "регістри ядра", 11, BLUE, "middle", "bold")
    for i, r in enumerate(["PC (де я був)", "статус", "R0", "R1", "…"]):
        s += rect(78, 148 + i * 30, 164, 24, LBLUE, BLUE, 1.2, 4)
        s += text(160, 165 + i * 30, r, 9.5, INK, "middle")
    # arrows to stack
    s += arrow(260, 170, 380, 170, RED, 2.2)
    s += text(320, 160, "1) зберегти", 9, RED, "middle", "bold")
    s += arrow(380, 360, 260, 360, GREEN, 2.2)
    s += text(320, 380, "3) відновити", 9, GREEN, "middle", "bold")
    # stack
    s += rect(400, 110, 160, 270, "#fbfcff", INK, 1.8, 12)
    s += text(480, 134, "стек", 11, INK, "middle", "bold")
    for i, r in enumerate(["PC", "статус", "R0", "R1"]):
        s += rect(416, 150 + i * 40, 128, 32, LAMB, GOLD, 1.4, 5)
        s += text(480, 171 + i * 40, r, 10, INK, "middle", "bold")
    s += text(480, 348, "(росте вниз)", 8.5, GREY, "middle")
    # handler
    s += rect(620, 150, 260, 110, LGRN, GREEN, 1.8, 12)
    s += text(750, 178, "2) обробник (ISR)", 12, GREEN, "middle", "bold")
    s += text(750, 204, "вільно користається регістрами —", 9.3, INK, "middle")
    s += text(750, 222, "вони ж збережені на стеку,", 9.3, INK, "middle")
    s += text(750, 240, "тож основний код не постраждає", 9.3, INK, "middle")
    s += text(W / 2, 404, "«Контекст» = лічильник команд (PC) + статус + робочі регістри. Без точного повернення — хаос.", 10.3, INK, "middle", "bold")
    save("fig-23-2-4-context-save.svg", s)


# ── Рис. 23.2.5 — матриця переривань ESP32 ───────────────────────────────────
def fig25_esp32_matrix():
    W, H = 960, 420
    s = header(W, H)
    s += text(W / 2, 32, "Як це в ESP32: матриця переривань і два ядра", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "десятки джерел маршрутизуються «матрицею» до слотів переривань кожного ядра", 11, GREY, "middle", style="italic")
    # many sources
    for i in range(6):
        yy = 100 + i * 38
        s += rect(50, yy, 120, 28, "#fbfcff", GREY, 1.2, 5)
        lab = ["таймер 0", "GPIO", "UART 0", "SPI", "Wi-Fi", "… (до ~70)"][i]
        s += text(110, yy + 19, lab, 9, INK, "middle")
        s += line(170, yy + 14, 360, 230, GREY, 1, "2,2")
    s += text(110, 88, "периферійні джерела", 9.5, INK, "middle", "bold")
    # matrix
    s += rect(360, 150, 200, 160, LAMB, GOLD, 2, 12)
    s += text(460, 178, "матриця переривань", 11.5, INK, "middle", "bold")
    s += text(460, 202, "комутатор:", 9.5, GREY, "middle")
    s += text(460, 222, "будь-яке джерело →", 9.5, INK, "middle")
    s += text(460, 240, "будь-який слот ядра", 9.5, INK, "middle")
    s += text(460, 266, "+ рівень пріоритету 1–7", 9.3, RED, "middle", "bold")
    # two cores
    for j, name in enumerate(["ядро PRO", "ядро APP"]):
        yy = 130 + j * 110
        s += arrow(560, 200 + j * 20, 700, yy + 40, BLUE, 2)
        s += rect(700, yy, 200, 80, LBLUE, BLUE, 1.8, 10)
        s += text(800, yy + 30, name, 12, BLUE, "middle", "bold")
        s += text(800, yy + 54, "свої слоти й рівні", 9, GREY, "middle")
    s += text(W / 2, 392, "Кожне ядро має власну логіку переривань; рівні 1–7 задають, що важливіше (деталі — §23.4).", 10.3, INK, "middle", "bold")
    save("fig-23-2-5-esp32-matrix.svg", s)


# ── Рис. 23.2.6 — як влаштовано attachInterrupt: лійка GPIO ───────────────────
def fig26_gpio_funnel():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 32, "Під капотом attachInterrupt: усі ніжки — крізь одну лійку", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "усі GPIO ділять одне переривання; обробник читає, ХТО спрацював, і кличе вашу функцію", 11, GREY, "middle", style="italic")
    # pins
    for i, p in enumerate(["GPIO2", "GPIO4", "GPIO5"]):
        yy = 110 + i * 50
        s += rect(50, yy, 90, 36, "#fbfcff", INK, 1.4, 6)
        s += text(95, yy + 23, p, 10, INK, "middle", "bold")
        col = RED if p == "GPIO4" else GREY
        s += arrow(140, yy + 18, 250, 200, col, (2.2 if col == RED else 1.3), None if col == RED else "3,3")
    # single GPIO interrupt
    s += rect(250, 170, 150, 70, LAMB, GOLD, 1.8, 10)
    s += text(325, 196, "одне переривання", 10, INK, "middle", "bold")
    s += text(325, 216, "GPIO (на ядро)", 9.5, GREY, "middle")
    # status register
    s += arrow(400, 205, 470, 205, INK, 2.2)
    s += text(560, 150, "регістр GPIO_STATUS", 10, INK, "middle", "bold")
    bitvals = [0, 0, 1, 0, 0, 0]
    for i, b in enumerate(bitvals):
        cx = 472 + i * 34
        s += rect(cx, 168, 34, 34, (LRED if b else "#ffffff"), (RED if b else GREY), 1.4)
        s += text(cx + 17, 191, str(b), 13, (RED if b else GREY), "middle", "bold")
    s += text(560, 226, "біт каже: спрацював GPIO4", 9, RED, "middle", "bold")
    # dispatcher -> your handler
    s += arrow(560, 240, 560, 290, INK, 2.2)
    s += rect(440, 290, 240, 50, "#fbfcff", INK, 1.6, 8)
    s += text(560, 312, "диспетчер ядра Arduino", 10.5, INK, "middle", "bold")
    s += text(560, 330, "за бітом обирає, кого кликати", 8.7, GREY, "middle")
    s += arrow(680, 315, 760, 315, GREEN, 2.4)
    s += rect(760, 292, 150, 48, LGRN, GREEN, 1.6, 8)
    s += text(835, 313, "ваш onPress()", 10.5, GREEN, "middle", "bold")
    s += text(835, 330, "(для GPIO4)", 8.5, INK, "middle")
    s += text(W / 2, 398, "Ось чому ISR має бути швидким: він спільний для всіх ніжок, і затримка в ньому б'є по всіх.", 10.3, INK, "middle", "bold")
    save("fig-23-2-6-gpio-funnel.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §23.3 Обробник (ISR): чому коротко — fig-23-3-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 23.3.1 — поки ISR працює, світ на паузі ─────────────────────────────
def fig31_isr_on_hold():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Поки обробник працює — решта світу на паузі", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "довгий ISR блокує і основний код, і інші переривання: усі чекають, доки він завершиться", 11, GREY, "middle", style="italic")
    y = 150
    s += text(70, y - 24, "основний код", 10.5, BLUE, "start", "bold")
    s += line(120, y, 320, y, BLUE, 3)
    s += line(320, y, 320, y + 4, BLUE, 1)
    # ISR block
    s += rect(320, y - 18, 300, 36, LRED, RED, 2, 6)
    s += text(470, y + 6, "обробник (ISR) виконується", 11, RED, "middle", "bold")
    s += line(620, y, 860, y, BLUE, 3)
    s += text(740, y - 8, "далі", 9, BLUE, "middle")
    # second event waiting
    s += line(440, y + 70, 440, y + 18, GREY, 2, dash="3,3")
    s += circle(440, y + 70, 4, GOLD, GOLD, 0)
    s += text(440, y + 88, "інша подія прийшла тут…", 9.5, "#8a6a14", "middle", "bold")
    s += arrow(440, y + 60, 620, y + 60, GOLD, 2)
    s += text(640, y + 64, "…а обслужать аж тут (чекала!)", 9.5, "#8a6a14", "start", "bold")
    s += line(620, y + 70, 620, y, GOLD, 1.4, dash="3,3")
    s += rect(150, 300, 640, 56, LAMB, GOLD, 1.4, 8)
    s += text(470, 324, "Що довший обробник, то довше «висить» уся система: спізнюються інші події,", 10.3, INK, "middle", "bold")
    s += text(470, 344, "зростає джитер, гальмує планувальник. Звідси головне правило: ISR — якнайкоротший.", 10, GREY, "middle")
    save("fig-23-3-1-isr-on-hold.svg", s)


# ── Рис. 23.3.2 — короткий проти довгого ISR ─────────────────────────────────
def fig32_short_vs_long():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Короткий обробник встигає все; довгий — губить події", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "три події підряд: швидкий ISP обробляє кожну, повільний — пропускає", 11, GREY, "middle", style="italic")
    evs = [200, 330, 460]
    # short
    yS = 150
    s += text(70, yS - 24, "Короткий ISR", 11, GREEN, "start", "bold")
    s += line(120, yS, 820, yS, INK, 1.6)
    for ex in evs:
        s += line(ex, yS - 34, ex, yS, GREEN, 2)
        s += circle(ex, yS - 34, 4, GREEN, GREEN, 0)
        s += rect(ex, yS - 12, 26, 24, LGRN, GREEN, 1.4, 4)
    s += text(470, yS + 28, "кожна подія оброблена вмить ✓", 9.5, GREEN, "middle", "bold")
    # long
    yL = 280
    s += text(70, yL - 24, "Довгий ISR", 11, RED, "start", "bold")
    s += line(120, yL, 820, yL, INK, 1.6)
    for ex in evs:
        s += line(ex, yL - 34, ex, yL, (RED if ex != 200 else GREEN), 2)
        s += circle(ex, yL - 34, 4, (RED if ex != 200 else GREEN), (RED if ex != 200 else GREEN), 0)
    s += rect(200, yL - 12, 150, 24, LRED, RED, 1.4, 4)
    s += text(275, yL + 4, "довгий обробник", 8.5, RED, "middle", "bold")
    s += text(395, yL - 22, "✗ ці дві — проґавлено / спізнено", 9.5, RED, "start", "bold")
    s += line(330, yL - 16, 330, yL, RED, 1.2, dash="2,2")
    s += line(460, yL - 16, 460, yL, RED, 1.2, dash="2,2")
    s += text(W / 2, 366, "Довгий обробник усе ще «зайнятий», коли надходять наступні події, — і вони пропадають.", 10.3, INK, "middle", "bold")
    save("fig-23-3-2-short-vs-long.svg", s)


# ── Рис. 23.3.3 — можна / не можна в ISR ──────────────────────────────────────
def fig33_dos_donts():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 32, "Що в обробнику можна, а чого — категорично ні", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "правило одне: лише швидке й безпечне; усе повільне чи блокувальне — у loop", 11, GREY, "middle", style="italic")
    s += rect(50, 84, 410, 300, "#f3faf4", GREEN, 1.8, 12)
    s += text(255, 110, "МОЖНА / ТРЕБА", 13, GREEN, "middle", "bold")
    cans = ["підняти прапорець: flag = true;", "збільшити лічильник: count++;",
            "прочитати / скинути регістр (W1TC)", "запам'ятати мить: t = micros();",
            "покласти подію в чергу (FromISR)"]
    for i, c in enumerate(cans):
        s += text(72, 148 + i * 38, "✓", 14, GREEN, "start", "bold")
        s += text(96, 148 + i * 38, c, 10.5, INK, "start")
    s += rect(480, 84, 410, 300, "#fdf2f2", RED, 1.8, 12)
    s += text(685, 110, "НЕ МОЖНА", 13, RED, "middle", "bold")
    donts = ["delay() чи активне очікування", "Serial.print(...) — повільно",
             "мережа, файли, I2C/SPI з очікуванням", "malloc / new (захоплення купи)",
             "важка математика, float"]
    for i, c in enumerate(donts):
        s += text(502, 148 + i * 38, "✗", 14, RED, "start", "bold")
        s += text(526, 148 + i * 38, c, 10.5, INK, "start")
    s += text(W / 2, 406, "Сумнів? Винось у loop(). Обробник має лише ВІДМІТИТИ подію, а не обробляти її.", 10.5, INK, "middle", "bold")
    save("fig-23-3-3-dos-donts.svg", s)


# ── Рис. 23.3.4 — патерн відкладеної роботи ──────────────────────────────────
def fig34_deferred_pattern():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Золотий патерн: обробник відмічає, loop() робить", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "уся важка робота переноситься з ISR у звичайний код — там вона нікому не заважає", 11, GREY, "middle", style="italic")
    s += rect(60, 120, 250, 110, "#fdf2f2", RED, 1.8, 12)
    s += text(185, 148, "обробник (ISR)", 12, RED, "middle", "bold")
    s += text(185, 176, "flag = true;", 12, INK, "middle", "bold")
    s += text(185, 200, "усе — коротко, мікросекунди", 8.7, GREY, "middle")
    s += arrow(310, 175, 420, 175, GOLD, 2.6)
    s += text(365, 165, "прапорець", 9, "#8a6a14", "middle", "bold")
    s += rect(420, 120, 300, 110, "#eef6ef", GREEN, 1.8, 12)
    s += text(570, 148, "loop() / задача", 12, GREEN, "middle", "bold")
    s += text(570, 174, "if (flag) { flag=false;", 11, INK, "middle", "bold")
    s += text(570, 196, "…важка робота тут… }", 11, INK, "middle", "bold")
    s += text(570, 218, "друк, обчислення, мережа — будь-що", 8.7, GREY, "middle")
    s += rect(760, 120, 130, 110, "none", FAINT, 1.6, 10)
    s += text(825, 150, "Чому добре:", 10, INK, "middle", "bold")
    s += text(825, 174, "ISR не блокує", 9, INK, "middle")
    s += text(825, 192, "систему; робота", 9, INK, "middle")
    s += text(825, 210, "діє без поспіху", 9, INK, "middle")
    s += text(W / 2, 320, "Це той самий шаблон «прапорець у ISR — обробка в loop», що ми бачили в §23.1.", 10.5, INK, "middle", "bold")
    s += text(W / 2, 342, "Складніший варіант — черга подій (FromISR), про неї докладніше з RTOS далі в курсі.", 9.7, GREY, "middle")
    save("fig-23-3-4-deferred-pattern.svg", s)


# ── Рис. 23.3.5 — навіщо IRAM_ATTR ───────────────────────────────────────────
def fig35_iram_attr():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Навіщо IRAM_ATTR: щоб ISR працював, коли флеш зайнятий", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "код живе у флеш-пам'яті, та вона часом недоступна — і ISR звідти впав би", 11, GREY, "middle", style="italic")
    # bad: ISR in flash
    s += rect(50, 90, 410, 280, "#fdf2f2", RED, 1.8, 12)
    s += text(255, 116, "Без IRAM_ATTR — ризик", 12.5, RED, "middle", "bold")
    s += rect(90, 140, 150, 80, "#fbfcff", INK, 1.6, 10)
    s += text(165, 168, "флеш-пам'ять", 10, INK, "middle", "bold")
    s += text(165, 188, "(тут лежить код)", 8.7, GREY, "middle")
    s += text(165, 206, "ISR теж тут", 9, RED, "middle", "bold")
    s += rect(300, 140, 120, 80, LRED, RED, 1.6, 10)
    s += text(360, 166, "флеш ЗАЙНЯТА", 9.5, RED, "middle", "bold")
    s += text(360, 184, "(запис / кеш-", 8.7, INK, "middle")
    s += text(360, 200, "промах)", 8.7, INK, "middle")
    s += arrow(240, 250, 360, 250, RED, 2)
    s += text(255, 300, "прийшло переривання →", 9.3, INK, "middle")
    s += text(255, 318, "код ISR недосяжний →", 9.3, RED, "middle", "bold")
    s += text(255, 336, "ЗБІЙ (краш)", 11, RED, "middle", "bold")
    # good: ISR in IRAM
    s += rect(480, 90, 410, 280, "#f3faf4", GREEN, 1.8, 12)
    s += text(685, 116, "З IRAM_ATTR — надійно", 12.5, GREEN, "middle", "bold")
    s += rect(540, 150, 140, 90, LGRN, GREEN, 1.6, 10)
    s += text(610, 180, "IRAM (ОЗП)", 10.5, GREEN, "middle", "bold")
    s += text(610, 200, "обробник тут —", 9, INK, "middle")
    s += text(610, 216, "завжди доступний", 9, INK, "middle")
    s += rect(720, 150, 120, 90, "#fbfcff", INK, 1.6, 10)
    s += text(780, 180, "флеш ЗАЙНЯТА", 8.8, GREY, "middle")
    s += text(780, 200, "— байдуже:", 8.8, INK, "middle")
    s += text(780, 216, "ISR не звідти", 8.8, GREEN, "middle", "bold")
    s += text(685, 300, "void IRAM_ATTR onEvent() { … }", 11, INK, "middle", "bold")
    s += text(685, 326, "одне слово кладе обробник у швидку RAM", 9.3, GREY, "middle")
    save("fig-23-3-5-iram-attr.svg", s)


# ── Рис. 23.3.6 — анатомія правильного ISR ───────────────────────────────────
def fig36_isr_anatomy():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Анатомія правильного обробника", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "чотири ознаки доброго ISR — короткий, у RAM, через volatile, без «важкого»", 11, GREY, "middle", style="italic")
    s += rect(120, 100, 700, 130, "#0f1115", INK, 1.6, 10)
    s += '<text x="150" y="134" font-family="Consolas, monospace" font-size="15.5" fill="#e8e8e8" font-weight="bold">volatile bool flag = false;<tspan fill="#caa24a">   // 1</tspan></text>\n'
    s += '<text x="150" y="162" font-family="Consolas, monospace" font-size="15.5" fill="#e8e8e8" font-weight="bold">void <tspan fill="#7fb4ff">IRAM_ATTR</tspan> onEvent() {<tspan fill="#caa24a">   // 2</tspan></text>\n'
    s += '<text x="150" y="190" font-family="Consolas, monospace" font-size="15.5" fill="#e8e8e8" font-weight="bold">  flag = true;<tspan fill="#caa24a">             // 3</tspan></text>\n'
    s += '<text x="150" y="218" font-family="Consolas, monospace" font-size="15.5" fill="#e8e8e8" font-weight="bold">}<tspan fill="#caa24a">                          // 4</tspan></text>\n'
    notes = [
        (60, "1 · volatile", "змінну міняє ISR — компілятор", "не має її «оптимізувати» (§23.5)", GOLD),
        (360, "2 · IRAM_ATTR", "обробник у швидкій RAM —", "працює навіть коли флеш зайнятий", BLUE),
        (660, "3 · коротке тіло", "лише прапорець; жодних", "delay, Serial, malloc, мережі", GREEN),
    ]
    for ox, t, l1, l2, col in notes:
        s += rect(ox, 256, 270, 96, "#fbfcff", col, 1.6, 10)
        s += text(ox + 135, 282, t, 12, col, "middle", "bold")
        s += text(ox + 135, 306, l1, 9.3, INK, "middle")
        s += text(ox + 135, 324, l2, 9.3, GREY, "middle")
    save("fig-23-3-6-isr-anatomy.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §23.4 Пріоритети й вкладеність — fig-23-4-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 23.4.1 — навіщо пріоритети ──────────────────────────────────────────
def fig41_why_priority():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Навіщо пріоритети: не всі події однаково термінові", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "аварійний сигнал не може чекати, поки обробляється натиск кнопки — комусь треба «вперед»", 11, GREY, "middle", style="italic")
    items = [
        ("аварія живлення", "ДУЖЕ терміново", RED, "вищий", 120),
        ("таймер реального часу", "важливо, точно", GOLD, "середній", 195),
        ("натиск кнопки", "може зачекати", GREEN, "нижчий", 270),
    ]
    for lab, urg, col, pr, yy in items:
        s += rect(60, yy, 260, 56, "#fbfcff", col, 1.8, 10)
        s += text(80, yy + 24, lab, 11.5, INK, "start", "bold")
        s += text(80, yy + 44, urg, 9.5, col, "start", "bold")
        s += arrow(320, yy + 28, 470, 200, col, 2)
        s += rect(770, yy, 110, 56, ("#fdf2f2" if col == RED else "#fbfcff"), col, 1.6, 8)
        s += text(825, yy + 24, "пріоритет:", 8.5, GREY, "middle")
        s += text(825, yy + 44, pr, 11, col, "middle", "bold")
    s += rect(470, 150, 230, 110, LAMB, GOLD, 2, 12)
    s += text(585, 180, "контролер", 12, INK, "middle", "bold")
    s += text(585, 204, "розставляє чергу", 10, INK, "middle")
    s += text(585, 224, "за пріоритетом:", 9.5, GREY, "middle")
    s += text(585, 244, "важливіший — першим", 9.5, RED, "middle", "bold")
    s += arrow(700, 205, 765, 148, INK, 1.6, "3,3")
    s += text(W / 2, 348, "Пріоритет каже контролеру, кого пускати першим і хто кого може перебити.", 10.5, INK, "middle", "bold")
    save("fig-23-4-1-why-priority.svg", s)


# ── Рис. 23.4.2 — витіснення (preemption) ────────────────────────────────────
def fig42_preemption():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Витіснення: важливіше переривання перебиває менш важливе", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "поки працює низькопріоритетний обробник, високопріоритетний може його перервати", 11, GREY, "middle", style="italic")
    # main lane
    yM = 130
    s += text(64, yM - 22, "основний код", 10, BLUE, "start", "bold")
    s += line(110, yM, 250, yM, BLUE, 3)
    s += line(810, yM, 880, yM, BLUE, 3)
    # low ISR
    yL = 210
    s += text(64, yL - 22, "низький ISR", 10, GREEN, "start", "bold")
    s += line(250, yM, 250, yL, GREEN, 1.4, dash="3,3")
    s += rect(250, yL - 16, 130, 32, LGRN, GREEN, 1.8, 6)
    s += rect(560, yL - 16, 250, 32, LGRN, GREEN, 1.8, 6)
    s += text(700, yL + 6, "низький ISR — далі", 9, GREEN, "middle", "bold")
    s += line(810, yL, 810, yM, GREEN, 1.4, dash="3,3")
    # high ISR preempts
    yH = 300
    s += text(64, yH - 22, "високий ISR", 10, RED, "start", "bold")
    s += circle(380, yL, 4, RED, RED, 0)
    s += text(380, yL - 24, "↯ високе переривання", 9, RED, "middle", "bold")
    s += line(380, yL, 380, yH, RED, 1.4, dash="3,3")
    s += rect(380, yH - 16, 180, 32, LRED, RED, 1.8, 6)
    s += text(470, yH + 6, "високий ISR (перебив!)", 9.5, RED, "middle", "bold")
    s += line(560, yH, 560, yL, RED, 1.4, dash="3,3")
    s += text(470, yH + 38, "відпрацював → низький продовжує з того ж місця", 9, INK, "middle")
    s += text(W / 2, 384, "Низький поступається високому, а коли той завершиться — спокійно доробляє своє.", 10.5, INK, "middle", "bold")
    save("fig-23-4-2-preemption.svg", s)


# ── Рис. 23.4.3 — вкладеність і стек ─────────────────────────────────────────
def fig43_nesting_stack():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 32, "Вкладеність: контексти складаються на стек", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "кожне витіснення кладе ще один контекст згори; повернення — у зворотному порядку", 11, GREY, "middle", style="italic")
    steps = [
        ("основний код", ["—"], BLUE, 70),
        ("+ низький ISR", ["контекст осн."], GREEN, 270),
        ("+ високий ISR", ["контекст осн.", "контекст низ."], RED, 470),
        ("повертаємось", ["контекст осн."], GREEN, 670),
    ]
    for lab, frames, col, ox in steps:
        s += text(ox + 90, 100, lab, 10.5, col, "middle", "bold")
        s += rect(ox, 120, 180, 200, "#fbfcff", INK, 1.4, 8)
        s += text(ox + 90, 312, "стек", 9, GREY, "middle")
        n = len([f for f in frames if f != "—"])
        for i, f in enumerate(frames):
            if f == "—":
                continue
            yy = 300 - (i + 1) * 36
            s += rect(ox + 16, yy, 148, 30, LAMB, GOLD, 1.4, 5)
            s += text(ox + 90, yy + 20, f, 9, INK, "middle")
        if n == 0:
            s += text(ox + 90, 220, "(порожній)", 8.5, GREY, "middle", style="italic")
    for x in (250, 450, 650):
        s += arrow(x, 210, x + 20, 210, INK, 2)
    s += text(W / 2, 360, "Що глибша вкладеність, то більше контекстів на стеку. Повертаються вони строго навпаки:", 10.3, INK, "middle", "bold")
    s += text(W / 2, 382, "останній покладений знімається першим — як стопка тарілок.", 9.7, GREY, "middle")
    save("fig-23-4-3-nesting-stack.svg", s)


# ── Рис. 23.4.4 — однаковий рівень не витісняє ───────────────────────────────
def fig44_same_level():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 32, "Однаковий пріоритет: не перебивають, а чекають у черзі", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "переривання того ж рівня не витісняє чинний обробник — воно дочікується його кінця", 11, GREY, "middle", style="italic")
    yA = 150
    s += text(64, yA - 22, "обробник A", 10, GREEN, "start", "bold")
    s += rect(150, yA - 16, 240, 32, LGRN, GREEN, 1.8, 6)
    s += text(270, yA + 6, "A виконується", 10, GREEN, "middle", "bold")
    # B event during A
    s += circle(280, yA + 60, 4, GOLD, GOLD, 0)
    s += text(280, yA + 80, "B (той самий рівень) прийшло тут", 9, "#8a6a14", "middle", "bold")
    s += line(280, yA + 54, 280, yA + 16, GOLD, 1.4, dash="3,3")
    s += text(280, yA + 100, "↓ але мусить чекати", 9, RED, "middle", "bold")
    yB = 250
    s += rect(390, yB - 16, 200, 32, LBLUE, BLUE, 1.8, 6)
    s += text(490, yB + 6, "B виконується", 10, BLUE, "middle", "bold")
    s += line(390, yA + 16, 390, yB - 16, INK, 1.4, dash="3,3")
    s += text(490, yB + 34, "аж коли A завершився", 9, INK, "middle")
    s += text(W / 2, 332, "Тому на ESP32 ваші обробники з attachInterrupt (усі рівня 1) НЕ перебивають один одного.", 10.3, INK, "middle", "bold")
    save("fig-23-4-4-same-level.svg", s)


# ── Рис. 23.4.5 — рівні переривань ESP32 ─────────────────────────────────────
def fig45_esp32_levels():
    W, H = 960, 420
    s = header(W, H)
    s += text(W / 2, 32, "Рівні переривань ESP32 (Xtensa): від 1 до 7", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "вищий рівень витісняє нижчий; ваші обробники зазвичай на рівні 1", 12, GREY, "middle", style="italic")
    rows = [
        ("7", "NMI — немаскований", "найвищий, особливий", RED),
        ("5–6", "високі / службові", "лагодження, критичне", RED),
        ("4", "високий", "тільки на асемблері", GOLD),
        ("2–3", "середній", "можна на C", GREEN),
        ("1", "низький — GPIO, більшість периферії", "ваш attachInterrupt тут", GREEN),
    ]
    y = 92
    for lv, name, note, col in rows:
        h = 54
        s += rect(120, y, 720, h, ("#fdf2f2" if col == RED else ("#fff8e8" if col == GOLD else "#f3faf4")), col, 1.6, 8)
        s += rect(120, y, 70, h, col, col, 0, 8)
        s += text(155, y + 34, lv, 17, "#ffffff", "middle", "bold")
        s += text(210, y + 23, name, 12, INK, "start", "bold")
        s += text(210, y + 43, note, 9.5, GREY, "start")
        y += 62
    # arrow showing higher preempts lower
    s += arrow(880, y - 20, 880, 100, RED, 2.4)
    s += text(905, (100 + y) / 2, "вищий", 9.5, RED, "middle", "bold")
    s += text(905, (100 + y) / 2 + 16, "витісняє", 9.5, RED, "middle")
    s += text(905, (100 + y) / 2 + 32, "нижчий", 9.5, RED, "middle")
    save("fig-23-4-5-esp32-levels.svg", s)


# ── Рис. 23.4.6 — небезпека глибокої вкладеності ─────────────────────────────
def fig46_stack_danger():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Небезпека: глибока вкладеність переповнює стек", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "кожен вкладений обробник з'їдає шматок стека — забагато рівнів, і пам'ять закінчиться", 11, GREY, "middle", style="italic")
    # stack filling
    bx, bw = 360, 220
    by, bh = 100, 230
    s += rect(bx, by, bw, bh, "#fbfcff", INK, 1.8, 8)
    s += text(bx + bw / 2, by - 8, "стек", 11, INK, "middle", "bold")
    frames = [("основний код", LBLUE), ("ISR рів.1", LGRN), ("ISR рів.2", LAMB), ("ISR рів.3", "#ffe3d6"), ("ISR рів.4 …", LRED)]
    fy = by + bh - 8
    for lab, col in frames:
        fh = 40
        fy -= fh
        s += rect(bx + 10, fy, bw - 20, fh - 4, col, INK, 1.2, 4)
        s += text(bx + bw / 2, fy + 24, lab, 9.5, INK, "middle", "bold")
    s += text(bx + bw / 2, by + 14, "← межа пам'яті!", 9.5, RED, "middle", "bold")
    s += arrow(bx - 20, by + bh - 20, bx - 20, by + 20, RED, 2)
    s += text(bx - 36, (by + bh / 2), "росте", 9, RED, "middle", "bold")
    s += rect(620, 130, 290, 170, "none", FAINT, 1.6, 10)
    s += text(765, 156, "Як убезпечитися:", 11.5, INK, "middle", "bold")
    s += text(636, 182, "• тримати обробники короткими", 10, INK, "start")
    s += text(636, 204, "• не плодити багато рівнів", 10, INK, "start")
    s += text(636, 226, "• на Arduino все рівня 1 —", 10, INK, "start")
    s += text(648, 246, "вкладеності нема, тож безпечно", 9.3, GREEN, "start", "bold")
    s += text(636, 272, "• глибока вкладеність — лише", 10, INK, "start")
    s += text(648, 290, "коли свідомо ставиш рівні", 9.3, GREY, "start")
    save("fig-23-4-6-stack-danger.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §23.5 volatile — fig-23-5-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 23.5.1 — баг: змінну закешовано в регістрі ──────────────────────────
def fig51_cached_in_register():
    W, H = 940, 410
    s = header(W, H)
    s += text(W / 2, 32, "Баг без volatile: цикл дивиться в регістр, а не в пам'ять", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "компілятор «закешував» прапорець у регістрі — і цикл не бачить, що ISR змінив пам'ять", 11, GREY, "middle", style="italic")
    # memory
    s += rect(60, 110, 200, 90, "#fbfcff", INK, 1.8, 12)
    s += text(160, 134, "пам'ять", 11, INK, "middle", "bold")
    s += rect(82, 148, 156, 40, LGRN, GREEN, 1.6, 6)
    s += text(160, 166, "flag = true", 12, GREEN, "middle", "bold")
    s += text(160, 182, "(ISR щойно записав)", 8, GREY, "middle")
    s += arrow(180, 240, 160, 200, RED, 2.2)
    s += text(230, 250, "ISR пише сюди →", 9, RED, "middle", "bold")
    s += rect(120, 250, 120, 44, LRED, RED, 1.6, 8)
    s += text(180, 277, "обробник", 10, RED, "middle", "bold")
    # register (cached, stale)
    s += rect(480, 110, 200, 90, "#fbfcff", BLUE, 1.8, 12)
    s += text(580, 134, "регістр (кеш)", 11, BLUE, "middle", "bold")
    s += rect(502, 148, 156, 40, LRED, RED, 1.6, 6)
    s += text(580, 172, "flag = false", 12, RED, "middle", "bold")
    s += text(580, 188, "застаріле!", 8, RED, "middle", "bold")
    # loop reads register
    s += rect(740, 130, 150, 90, "none", GREY, 1.6, 10)
    s += text(815, 156, "while(!flag){}", 11, INK, "middle", "bold")
    s += text(815, 180, "дивиться в РЕГІСТР", 8.5, BLUE, "middle")
    s += text(815, 198, "→ завжди false", 9, RED, "middle", "bold")
    s += arrow(740, 175, 682, 165, BLUE, 2)
    # disconnect
    s += line(280, 160, 470, 160, RED, 2, dash="6,5")
    s += text(375, 150, "✗ зв'язок розірвано", 9.5, RED, "middle", "bold")
    s += text(375, 174, "(цикл не перечитує пам'ять)", 8.5, GREY, "middle")
    s += rect(150, 320, 640, 64, LRED, RED, 1.4, 10)
    s += text(470, 346, "Результат: ISR давно поставив flag=true в пам'яті, а цикл крутиться вічно,", 10.5, INK, "middle", "bold")
    s += text(470, 366, "бо звіряється з застарілою копією в регістрі. Класичне «зависання» з перериваннями.", 10, GREY, "middle")
    save("fig-23-5-1-cached-in-register.svg", s)


# ── Рис. 23.5.2 — volatile лагодить ──────────────────────────────────────────
def fig52_volatile_fix():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "volatile: завжди перечитувати з пам'яті", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "ключове слово забороняє кешувати — кожна перевірка йде прямо в пам'ять і бачить зміну", 11, GREY, "middle", style="italic")
    s += rect(60, 120, 200, 100, "#fbfcff", INK, 1.8, 12)
    s += text(160, 146, "пам'ять", 11, INK, "middle", "bold")
    s += rect(82, 160, 156, 44, LGRN, GREEN, 1.6, 6)
    s += text(160, 180, "flag = true", 12, GREEN, "middle", "bold")
    s += text(160, 197, "(ISR записав)", 8, GREY, "middle")
    s += rect(140, 250, 120, 44, LRED, RED, 1.6, 8)
    s += text(200, 277, "обробник", 10, RED, "middle", "bold")
    s += arrow(200, 250, 175, 204, RED, 2)
    # loop reads memory each time
    s += rect(620, 120, 270, 100, "none", GREEN, 1.8, 12)
    s += text(755, 146, "while(!flag){}", 12, INK, "middle", "bold")
    s += text(755, 172, "flag — volatile →", 9.5, GREEN, "middle", "bold")
    s += text(755, 190, "щоразу читає ПАМ'ЯТЬ", 9.5, INK, "middle")
    s += text(755, 208, "→ бачить true → виходить ✓", 9, GREEN, "middle", "bold")
    s += arrow(620, 170, 262, 178, GREEN, 2.4)
    s += text(440, 162, "кожна перевірка — свіже читання з пам'яті", 9.5, GREEN, "middle", "bold")
    s += text(W / 2, 340, "volatile = «ця змінна може змінитися поза твоїм кодом — не кешуй, читай заново щоразу».", 10.5, INK, "middle", "bold")
    save("fig-23-5-2-volatile-fix.svg", s)


# ── Рис. 23.5.3 — що робить оптимізатор ──────────────────────────────────────
def fig53_what_compiler_does():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Чому так стається: компілятор «надто розумний»", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "оптимізатор припускає, що змінні міняє лише видимий код, — і це ламається з ISR", 11, GREY, "middle", style="italic")
    tricks = [
        ("Кешує в регістрі", "тримає змінну в регістрі,", "не бігаючи в пам'ять щоразу", BLUE),
        ("Прибирає «зайві» читання", "якщо в коді нема запису —", "навіщо перечитувати?", GOLD),
        ("Переставляє доступи", "міняє порядок читань/", "записів задля швидкості", RED),
    ]
    for i, (t, l1, l2, col) in enumerate(tricks):
        ox = 50 + i * 295
        s += rect(ox, 90, 270, 110, "#fbfcff", col, 1.8, 12)
        s += text(ox + 135, 118, t, 12, col, "middle", "bold")
        s += text(ox + 135, 148, l1, 9.7, INK, "middle")
        s += text(ox + 135, 168, l2, 9.7, GREY, "middle")
    s += rect(80, 230, 360, 110, "#f3faf4", GREEN, 1.6, 10)
    s += text(260, 256, "Для звичайного коду — ДОБРЕ", 11.5, GREEN, "middle", "bold")
    s += text(260, 282, "якщо змінну міняє лише ваш код,", 10, INK, "middle")
    s += text(260, 302, "ці хитрощі прискорюють і нічого", 10, INK, "middle")
    s += text(260, 322, "не ламають — все коректно.", 10, INK, "middle")
    s += rect(500, 230, 360, 110, "#fdf2f2", RED, 1.6, 10)
    s += text(680, 256, "З перериванням — ПОМИЛКА", 11.5, RED, "middle", "bold")
    s += text(680, 282, "ISR міняє змінну «за спиною»", 10, INK, "middle")
    s += text(680, 302, "оптимізатора — і той працює зі", 10, INK, "middle")
    s += text(680, 322, "старою копією. Тут і треба volatile.", 10, INK, "middle")
    save("fig-23-5-3-what-compiler-does.svg", s)


# ── Рис. 23.5.4 — коли потрібен volatile ─────────────────────────────────────
def fig54_when_to_use():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Яким змінним потрібен volatile, а яким — ні", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "правило: спільна з обробником (чи з іншим контекстом) — volatile; суто локальна — ні", 11, GREY, "middle", style="italic")
    s += rect(50, 84, 410, 290, "#f3faf4", GREEN, 1.8, 12)
    s += text(255, 110, "ПОТРІБЕН volatile", 13, GREEN, "middle", "bold")
    yes = ["прапорець, який ставить ISR", "лічильник подій із обробника", "індекс/буфер, спільний з ISR",
           "будь-що, що пише ISR, а читає loop", "(і навпаки)"]
    for i, c in enumerate(yes):
        s += text(72, 148 + i * 40, "✓", 14, GREEN, "start", "bold")
        s += text(96, 148 + i * 40, c, 10.5, INK, "start")
    s += rect(480, 84, 410, 290, "#f7f7f7", GREY, 1.8, 12)
    s += text(685, 110, "НЕ потрібен", 13, GREY, "middle", "bold")
    no = ["локальна змінна в функції", "значення, яке ISR не чіпає", "тимчасова в обчисленні",
          "константа", "(volatile лише сповільнив би)"]
    for i, c in enumerate(no):
        s += text(502, 148 + i * 40, "•", 14, GREY, "start", "bold")
        s += text(524, 148 + i * 40, c, 10.5, INK, "start")
    s += text(W / 2, 394, "volatile — не «про всяк випадок»: лиш там, де змінну справді міняють поза видимим кодом.", 10.3, INK, "middle", "bold")
    save("fig-23-5-4-when-to-use.svg", s)


# ── Рис. 23.5.5 — volatile ≠ атомарність ─────────────────────────────────────
def fig55_volatile_not_atomic():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Важливо: volatile дає СВІЖІСТЬ, але не АТОМАРНІСТЬ", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "voltatile гарантує читання з пам'яті, та не захищає від переривання посеред дії", 11, GREY, "middle", style="italic")
    s += rect(60, 90, 380, 130, "#f3faf4", GREEN, 1.8, 12)
    s += text(250, 118, "Що volatile ДАЄ", 12.5, GREEN, "middle", "bold")
    s += text(82, 146, "✓ завжди читати/писати в пам'ять", 10.5, INK, "start")
    s += text(82, 170, "✓ не кешувати в регістрі", 10.5, INK, "start")
    s += text(82, 194, "✓ не прибирати «зайві» доступи", 10.5, INK, "start")
    s += rect(500, 90, 380, 130, "#fdf2f2", RED, 1.8, 12)
    s += text(690, 118, "Чого volatile НЕ дає", 12.5, RED, "middle", "bold")
    s += text(522, 146, "✗ не робить дію неподільною", 10.5, INK, "start")
    s += text(522, 170, "✗ багатобайтне читання ще можна", 10.5, INK, "start")
    s += text(540, 190, "перервати посередині (розрив)", 10, GREY, "start")
    s += text(522, 214, "✗ не замінює критичну секцію", 10.5, INK, "start")
    # tearing illustration
    s += text(250, 256, "Розрив (tearing) 64-біт значення:", 10.5, INK, "middle", "bold")
    s += rect(120, 270, 130, 34, LBLUE, BLUE, 1.4, 5)
    s += text(185, 292, "читаю старші", 9, INK, "middle")
    s += circle(265, 287, 5, RED, RED, 0)
    s += text(265, 320, "↯ ISR змінив усе", 8.5, RED, "middle", "bold")
    s += rect(280, 270, 130, 34, LRED, RED, 1.4, 5)
    s += text(345, 292, "читаю молодші", 9, INK, "middle")
    s += text(265, 340, "→ половина стара + половина нова = сміття", 9, RED, "middle", "bold")
    s += rect(560, 250, 320, 100, LAMB, GOLD, 1.6, 10)
    s += text(720, 276, "Тому для багатобайтних / складених", 10, INK, "middle", "bold")
    s += text(720, 296, "даних треба ще й захист від переривання", 10, INK, "middle")
    s += text(720, 320, "(критична секція) — це наступна тема §23.6.", 9.7, GREY, "middle", "bold")
    save("fig-23-5-5-volatile-not-atomic.svg", s)


# ── Рис. 23.5.6 — приклад до/після ───────────────────────────────────────────
def fig56_volatile_example():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "До й після: одне слово, що все вирішує", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "той самий код зависає без volatile і працює з ним", 12, GREY, "middle", style="italic")
    # before
    s += rect(60, 90, 400, 150, "#0f1115", RED, 1.8, 10)
    s += text(260, 84, "", 1, INK, "middle")
    s += '<text x="80" y="120" font-family="Consolas, monospace" font-size="14" fill="#ff8a7a" font-weight="bold">bool flag = false;</text>\n'
    s += '<text x="80" y="146" font-family="Consolas, monospace" font-size="14" fill="#e8e8e8">void IRAM_ATTR isr(){ flag=true; }</text>\n'
    s += '<text x="80" y="180" font-family="Consolas, monospace" font-size="14" fill="#e8e8e8">// очікуємо подію:</text>\n'
    s += '<text x="80" y="206" font-family="Consolas, monospace" font-size="14" fill="#e8e8e8">while(!flag){ }</text>\n'
    s += '<text x="80" y="230" font-family="Consolas, monospace" font-size="13" fill="#ff8a7a" font-weight="bold">// ЗАВИСАЄ назавжди ✗</text>\n'
    s += text(260, 262, "без volatile — баг", 11, RED, "middle", "bold")
    # after
    s += rect(490, 90, 400, 150, "#0f1115", GREEN, 1.8, 10)
    s += '<text x="510" y="120" font-family="Consolas, monospace" font-size="14" fill="#7ee0a0" font-weight="bold">volatile bool flag = false;</text>\n'
    s += '<text x="510" y="146" font-family="Consolas, monospace" font-size="14" fill="#e8e8e8">void IRAM_ATTR isr(){ flag=true; }</text>\n'
    s += '<text x="510" y="180" font-family="Consolas, monospace" font-size="14" fill="#e8e8e8">// очікуємо подію:</text>\n'
    s += '<text x="510" y="206" font-family="Consolas, monospace" font-size="14" fill="#e8e8e8">while(!flag){ }</text>\n'
    s += '<text x="510" y="230" font-family="Consolas, monospace" font-size="13" fill="#7ee0a0" font-weight="bold">// виходить, щойно подія ✓</text>\n'
    s += text(690, 262, "з volatile — працює", 11, GREEN, "middle", "bold")
    s += rect(180, 300, 580, 50, LAMB, GOLD, 1.4, 8)
    s += text(470, 324, "Різниця — одне слово volatile перед типом. Воно й перетворює «зависання» на робочий код.", 10.3, INK, "middle", "bold")
    s += text(470, 342, "Звичка: КОЖНУ змінну, спільну з обробником, оголошуй volatile.", 9.7, GREY, "middle")
    save("fig-23-5-6-volatile-example.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §23.6 Атомарність і гонки даних — fig-23-6-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 23.6.1 — гонка даних (втрачене оновлення) ───────────────────────────
def fig61_race_condition():
    W, H = 960, 430
    s = header(W, H)
    s += text(W / 2, 32, "Гонка даних: одне оновлення губиться", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "і loop(), і обробник роблять count++ — та через перекриття замість +2 виходить лише +1", 11, GREY, "middle", style="italic")
    # value track at top
    s += text(80, 96, "count:", 11, INK, "start", "bold")
    for x, v, col in [(150, "5", INK), (470, "5", INK), (760, "6", RED)]:
        s += rect(x, 80, 50, 28, "#fbfcff", col, 1.4, 5)
        s += text(x + 25, 100, v, 13, col, "middle", "bold")
    # main lane
    yM = 180
    s += text(64, yM - 22, "loop()", 10, BLUE, "start", "bold")
    s += line(110, yM, 880, yM, "#dfe6f5", 2)
    s += rect(150, yM - 16, 90, 32, LBLUE, BLUE, 1.6, 5)
    s += text(195, yM + 5, "читає 5", 9.5, INK, "middle", "bold")
    s += rect(700, yM - 16, 140, 32, LBLUE, BLUE, 1.6, 5)
    s += text(770, yM + 5, "пише 5+1=6", 9, INK, "middle", "bold")
    s += line(240, yM, 700, yM, BLUE, 1.4, dash="3,3")
    s += text(470, yM - 6, "...перервано, своє «5» забуто...", 8.5, GREY, "middle", style="italic")
    # ISR lane
    yI = 300
    s += text(64, yI - 22, "обробник", 10, RED, "start", "bold")
    s += circle(330, yM, 4, RED, RED, 0)
    s += text(330, yM - 22, "↯ ISR перебив", 9, RED, "middle", "bold")
    s += line(330, yM, 330, yI - 16, RED, 1.4, dash="3,3")
    s += rect(330, yI - 16, 280, 32, LRED, RED, 1.6, 5)
    s += text(470, yI + 5, "читає 5 → +1 → пише 6", 10, RED, "middle", "bold")
    s += line(610, yI, 610, yM, RED, 1.4, dash="3,3")
    s += rect(150, 350, 660, 60, LAMB, GOLD, 1.4, 10)
    s += text(480, 376, "Було два «+1», а count став лише 6 замість 7: loop писав, спираючись на застаріле «5».", 10.3, INK, "middle", "bold")
    s += text(480, 396, "Це й є гонка: результат залежить від того, ХТО коли встиг. Одне оновлення зникло.", 9.7, GREY, "middle")
    save("fig-23-6-1-race-condition.svg", s)


# ── Рис. 23.6.2 — що таке атомарність ────────────────────────────────────────
def fig62_what_is_atomic():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Атомарність: неподільна дія проти дії в кілька кроків", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "count++ — це насправді ТРИ кроки, і між ними може втрутитися переривання", 11, GREY, "middle", style="italic")
    # non-atomic: 3 steps with interrupt between
    s += text(250, 100, "count++ — НЕ атомарна (3 кроки):", 11.5, RED, "middle", "bold")
    steps = [("прочитати", 80), ("додати 1", 250), ("записати", 420)]
    for lab, x in steps:
        s += rect(x, 120, 130, 44, "#fbfcff", INK, 1.6, 8)
        s += text(x + 65, 147, lab, 10.5, INK, "middle", "bold")
    for x in (210, 380):
        s += arrow(x, 142, x + 40, 142, INK, 2)
    s += circle(295, 190, 5, RED, RED, 0)
    s += line(295, 190, 295, 164, RED, 2, dash="3,3")
    s += text(295, 210, "↯ ISR може втрутитися тут → гонка", 9.5, RED, "middle", "bold")
    # atomic: single step
    s += text(720, 100, "одне читання/запис слова —", 11, GREEN, "middle", "bold")
    s += text(720, 118, "атомарне (1 крок):", 11, GREEN, "middle", "bold")
    s += rect(640, 132, 160, 44, LGRN, GREEN, 1.8, 8)
    s += text(720, 159, "неподільно", 11, GREEN, "middle", "bold")
    s += text(720, 196, "перервати «всередині»", 9, INK, "middle")
    s += text(720, 212, "нема де — або до, або після", 9, GREY, "middle")
    s += rect(120, 260, 700, 90, "none", FAINT, 1.6, 10)
    s += text(470, 286, "Атомарна = «все або нічого», її не можна застати на півдорозі.", 11, INK, "middle", "bold")
    s += text(470, 312, "Багатокрокову дію (count++, читання 64-біт, оновлення структури) переривання може", 10, INK, "middle")
    s += text(470, 332, "розрізати посередині — і саме її треба захищати критичною секцією.", 10, GREY, "middle")
    save("fig-23-6-2-what-is-atomic.svg", s)


# ── Рис. 23.6.3 — критична секція ────────────────────────────────────────────
def fig63_critical_section():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Критична секція: на мить вимкнути переривання", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "поки переривання вимкнені, обробник не втрутиться — дія виконується цілісно", 11, GREY, "middle", style="italic")
    # fence
    bx0, bx1 = 300, 660
    yb = 200
    s += line(110, yb, bx0, yb, BLUE, 3)
    s += line(bx1, yb, 880, yb, BLUE, 3)
    s += rect(bx0, yb - 30, bx1 - bx0, 60, LGRN, GREEN, 2, 10)
    s += text((bx0 + bx1) / 2, yb - 6, "робота зі спільними даними", 10.5, GREEN, "middle", "bold")
    s += text((bx0 + bx1) / 2, yb + 14, "(цілісно, без втручань)", 9, INK, "middle")
    s += line(bx0, yb - 44, bx0, yb + 44, RED, 2)
    s += text(bx0, yb - 54, "noInterrupts()", 10, RED, "middle", "bold")
    s += text(bx0, yb + 60, "↑ вимкнути", 8.5, RED, "middle")
    s += line(bx1, yb - 44, bx1, yb + 44, GREEN, 2)
    s += text(bx1, yb - 54, "interrupts()", 10, GREEN, "middle", "bold")
    s += text(bx1, yb + 60, "↑ увімкнути назад", 8.5, GREEN, "middle")
    # ISR blocked
    s += circle(480, 110, 5, GOLD, GOLD, 0)
    s += text(480, 100, "↯ подія прийшла тут", 9, "#8a6a14", "middle", "bold")
    s += line(480, 116, 480, yb - 30, GOLD, 1.6, dash="4,3")
    s += text(480, 150, "обробник ЧЕКАЄ — поки секція не скінчиться", 8.8, "#8a6a14", "middle", "bold")
    s += arrow(480, yb + 30, 690, yb + 30, GOLD, 2)
    s += text(720, yb + 34, "виконається тут", 9, "#8a6a14", "start", "bold")
    s += text(W / 2, 360, "Подія не губиться — вона лише чекає кілька тактів, поки дія завершиться неподільно.", 10.5, INK, "middle", "bold")
    save("fig-23-6-3-critical-section.svg", s)


# ── Рис. 23.6.4 — патерн «знімок» ────────────────────────────────────────────
def fig64_snapshot_pattern():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Патерн «знімок»: швидко скопіювати, потім працювати", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "критичну секцію тримають МІНІМАЛЬНОЮ — лише копіювання, а обробку роблять поза нею", 11, GREY, "middle", style="italic")
    s += rect(110, 100, 720, 130, "#0f1115", INK, 1.6, 10)
    s += '<text x="130" y="132" font-family="Consolas, monospace" font-size="14.5" fill="#ff8a7a" font-weight="bold">noInterrupts();</text>\n'
    s += '<text x="130" y="158" font-family="Consolas, monospace" font-size="14.5" fill="#e8e8e8">  uint32_t n = pulses;  pulses = 0;<tspan fill="#caa24a">  // лише копія</tspan></text>\n'
    s += '<text x="130" y="184" font-family="Consolas, monospace" font-size="14.5" fill="#7ee0a0" font-weight="bold">interrupts();</text>\n'
    s += '<text x="130" y="214" font-family="Consolas, monospace" font-size="14.5" fill="#e8e8e8">Serial.println(n);<tspan fill="#caa24a">  // обробка — ПОЗА секцією</tspan></text>\n'
    s += text(180, 270, "у секції — мить", 10, RED, "middle", "bold")
    s += line(130, 256, 470, 256, RED, 1.6)
    s += text(640, 270, "уся «важка» робота — вже з копією, без поспіху", 10, GREEN, "middle", "bold")
    s += line(490, 256, 820, 256, GREEN, 1.6)
    s += text(W / 2, 322, "Спершу швидко «фотографуємо» спільні дані в локальну змінну під захистом,", 10.5, INK, "middle", "bold")
    s += text(W / 2, 344, "а тоді спокійно працюємо з копією — переривання вже знову ввімкнені.", 10, GREY, "middle")
    save("fig-23-6-4-snapshot-pattern.svg", s)


# ── Рис. 23.6.5 — критичну секцію тримати короткою ───────────────────────────
def fig65_keep_short():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Критична секція має бути короткою — як і обробник", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "поки переривання вимкнені, СЛІПНЕ вся система; що довша секція, то більший ризик", 11, GREY, "middle", style="italic")
    # short
    yS = 140
    s += text(64, yS - 22, "Коротка", 10.5, GREEN, "start", "bold")
    s += line(120, yS, 820, yS, INK, 1.6)
    s += rect(360, yS - 12, 60, 24, LRED, RED, 1.4, 4)
    s += text(390, yS + 5, "off", 8.5, RED, "middle", "bold")
    s += circle(450, yS - 30, 4, GREEN, GREEN, 0)
    s += line(450, yS - 30, 450, yS, GREEN, 1.4, dash="3,3")
    s += text(450, yS - 38, "подія", 8.5, GREEN, "middle")
    s += text(470, yS - 14, "обробляється майже відразу ✓", 9, GREEN, "start", "bold")
    # long
    yL = 270
    s += text(64, yL - 22, "Довга", 10.5, RED, "start", "bold")
    s += line(120, yL, 820, yL, INK, 1.6)
    s += rect(260, yL - 12, 360, 24, LRED, RED, 1.4, 4)
    s += text(440, yL + 5, "переривання вимкнені надовго", 8.7, RED, "middle", "bold")
    s += circle(360, yL - 30, 4, RED, RED, 0)
    s += line(360, yL - 30, 360, yL, RED, 1.4, dash="3,3")
    s += text(360, yL - 38, "подія", 8.5, RED, "middle")
    s += arrow(360, yL - 8, 620, yL - 8, RED, 1.8)
    s += text(650, yL - 12, "чекає весь час → джитер, втрати ✗", 9, RED, "start", "bold")
    s += text(W / 2, 350, "Правило те саме, що для ISR (§23.3): захищай лише мінімальну дію, не більше.", 10.5, INK, "middle", "bold")
    save("fig-23-6-5-keep-short.svg", s)


# ── Рис. 23.6.6 — два ядра ESP32 і спінлок ───────────────────────────────────
def fig66_esp32_spinlock():
    W, H = 960, 420
    s = header(W, H)
    s += text(W / 2, 32, "Два ядра ESP32: noInterrupts мало — потрібен спінлок", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "вимкнення переривань діє лише на СВОЄ ядро; інше ядро тим часом не спить", 11, GREY, "middle", style="italic")
    # bad
    s += rect(50, 90, 410, 250, "#fdf2f2", RED, 1.8, 12)
    s += text(255, 116, "noInterrupts() на 1 ядрі — НЕ досить", 11, RED, "middle", "bold")
    s += rect(80, 140, 150, 80, LBLUE, BLUE, 1.6, 8)
    s += text(155, 170, "ядро 0", 11, BLUE, "middle", "bold")
    s += text(155, 190, "перерив. вимк.", 9, RED, "middle")
    s += rect(280, 140, 150, 80, LBLUE, BLUE, 1.6, 8)
    s += text(355, 170, "ядро 1", 11, BLUE, "middle", "bold")
    s += text(355, 190, "працює собі!", 9, RED, "middle", "bold")
    s += rect(150, 250, 210, 60, "#ffffff", RED, 1.4, 8)
    s += text(255, 274, "обидва лізуть у спільні дані", 9.3, INK, "middle")
    s += text(255, 294, "→ гонка лишилася", 10, RED, "middle", "bold")
    # good
    s += rect(500, 90, 410, 250, "#f3faf4", GREEN, 1.8, 12)
    s += text(705, 116, "portMUX-спінлок — захищає обидва", 10.5, GREEN, "middle", "bold")
    s += rect(530, 145, 350, 70, "#0f1115", INK, 1.4, 8)
    s += '<text x="548" y="170" font-family="Consolas, monospace" font-size="12.5" fill="#7ee0a0">portENTER_CRITICAL(&amp;mux);</text>\n'
    s += '<text x="548" y="190" font-family="Consolas, monospace" font-size="12.5" fill="#e8e8e8">  …спільні дані…</text>\n'
    s += '<text x="548" y="208" font-family="Consolas, monospace" font-size="12.5" fill="#7ee0a0">portEXIT_CRITICAL(&amp;mux);</text>\n'
    s += text(705, 240, "спінлок не пускає й друге ядро,", 9.5, INK, "middle")
    s += text(705, 258, "поки секція триває", 9.5, INK, "middle")
    s += text(705, 286, "(в обробнику — варіант …_ISR)", 9, GREY, "middle")
    s += text(705, 312, "потрібен, коли дані ділять різні ядра", 9.3, GREEN, "middle", "bold")
    s += text(W / 2, 372, "Для звичайного коду «один loop + обробник на тім самім ядрі» досить noInterrupts().", 10.3, INK, "middle", "bold")
    s += text(W / 2, 394, "Спінлок беруть, коли дані справді спільні між ядрами.", 9.7, GREY, "middle")
    save("fig-23-6-6-esp32-spinlock.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §23.7 Polling vs переривання: коли що — fig-23-7-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 23.7.1 — два інструменти, обидва потрібні ───────────────────────────
def fig71_two_tools():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Два інструменти, не суперники: кожен сильний у своєму", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "опитування й переривання доповнюють одне одного — інженер володіє обома", 11.5, GREY, "middle", style="italic")
    s += rect(50, 90, 410, 270, "#fdf2f2", RED, 1.8, 12)
    s += text(255, 116, "Опитування", 14, RED, "middle", "bold")
    s += text(255, 138, "сильне, коли:", 10, GREY, "middle")
    pol = ["події часті й очікувані", "таймінг рівномірний", "потрібна простота й передбачуваність", "реакція «в межах циклу» влаштовує"]
    for i, c in enumerate(pol):
        s += text(72, 168 + i * 30, "•", 13, RED, "start", "bold")
        s += text(92, 168 + i * 30, c, 10.5, INK, "start")
    s += text(255, 320, "ціна: марнує час, може проґавити коротке", 9, GREY, "middle", style="italic")
    s += rect(480, 90, 410, 270, "#f3faf4", GREEN, 1.8, 12)
    s += text(685, 116, "Переривання", 14, GREEN, "middle", "bold")
    s += text(685, 138, "сильне, коли:", 10, GREY, "middle")
    intr = ["події рідкісні чи випадкові", "треба реагувати вмить", "не можна проґавити подію", "процесор має бути вільний"]
    for i, c in enumerate(intr):
        s += text(502, 168 + i * 30, "•", 13, GREEN, "start", "bold")
        s += text(522, 168 + i * 30, c, 10.5, INK, "start")
    s += text(685, 320, "ціна: складніший код (ISR, volatile, гонки)", 9, GREY, "middle", style="italic")
    s += text(W / 2, 384, "Питання не «що краще взагалі», а «що краще для ЦІЄЇ задачі».", 11, INK, "middle", "bold")
    save("fig-23-7-1-two-tools.svg", s)


# ── Рис. 23.7.2 — блок-схема вибору ──────────────────────────────────────────
def fig72_decision_flow():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 32, "Як обрати: проста блок-схема рішення", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "три питання — і відповідь зазвичай очевидна", 12, GREY, "middle", style="italic")

    def diamond(cx, cy, w, h, txt1, txt2):
        o = f'<polygon points="{cx},{cy-h/2} {cx+w/2},{cy} {cx},{cy+h/2} {cx-w/2},{cy}" fill="{LAMB}" stroke="{GOLD}" stroke-width="2"/>\n'
        o += text(cx, cy - 4, txt1, 10, INK, "middle", "bold")
        o += text(cx, cy + 12, txt2, 9, INK, "middle")
        return o

    s += rect(70, 110, 110, 40, LBLUE, BLUE, 1.6, 8)
    s += text(125, 135, "старт", 11, BLUE, "middle", "bold")
    s += arrow(180, 130, 230, 130, INK, 2)
    s += diamond(330, 130, 200, 90, "Подія рідкісна", "чи випадкова в часі?")
    s += diamond(330, 290, 200, 90, "Треба вмить /", "не можна проґавити?")
    s += arrow(330, 175, 330, 245, INK, 2)
    s += text(345, 215, "ні ↓", 9, GREY, "start")
    s += text(430, 124, "так →", 9, GREEN, "start", "bold")
    s += arrow(430, 130, 640, 130, GREEN, 2)
    s += text(345, 338, "ні ↓", 9, GREY, "start")
    s += arrow(330, 335, 330, 380, RED, 2)
    s += text(430, 284, "так →", 9, GREEN, "start", "bold")
    s += arrow(430, 290, 640, 290, GREEN, 2)
    # outcomes
    s += rect(640, 105, 230, 50, "#eef6ef", GREEN, 2, 10)
    s += text(755, 128, "ПЕРЕРИВАННЯ", 13, GREEN, "middle", "bold")
    s += text(755, 146, "(подія сама покличе)", 8.5, INK, "middle")
    s += rect(640, 265, 230, 50, "#eef6ef", GREEN, 2, 10)
    s += text(755, 288, "ПЕРЕРИВАННЯ", 13, GREEN, "middle", "bold")
    s += text(755, 306, "(реакція має бути миттєвою)", 8.3, INK, "middle")
    s += rect(215, 385, 230, 40, "#fbecec", RED, 2, 10)
    s += text(330, 410, "ОПИТУВАННЯ (простіше)", 11.5, RED, "middle", "bold")
    s += text(W / 2, 400, "часте, очікуване,", 9, GREY, "middle")
    save("fig-23-7-2-decision-flow.svg", s)


# ── Рис. 23.7.3 — критерії вибору ────────────────────────────────────────────
def fig73_criteria():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "П'ять критеріїв: куди хилить кожен", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "зважте задачу за ними — і побачите, який інструмент пасує", 12, GREY, "middle", style="italic")
    s += rect(330, 78, 300, 34, "#fbecec", RED, 1.6, 8)
    s += text(480, 101, "← Опитування", 12, RED, "middle", "bold")
    s += rect(650, 78, 270, 34, "#eef6ef", GREEN, 1.6, 8)
    s += text(785, 101, "Переривання →", 12, GREEN, "middle", "bold")
    rows = [
        ("Частота подій", "часті, потоком", "рідкісні, поодинокі"),
        ("Терміновість", "можна зачекати", "реагувати вмить"),
        ("Передбачуваність", "рівномірні, очікувані", "випадкові в часі"),
        ("Ціна пропуску", "проґавити не страшно", "втрата неприпустима"),
        ("Складність коду", "простота важлива", "готові до ISR і гонок"),
    ]
    y = 122
    for name, a, b in rows:
        s += rect(40, y, 280, 48, "#f7f7f7", GREY, 1.2, 6)
        s += text(52, y + 29, name, 11, INK, "start", "bold")
        s += rect(330, y, 300, 48, "#fff", RED, 1.2, 6)
        s += text(480, y + 29, a, 10, INK, "middle")
        s += rect(650, y, 270, 48, "#fff", GREEN, 1.2, 6)
        s += text(785, y + 29, b, 10, INK, "middle")
        y += 54
    save("fig-23-7-3-criteria.svg", s)


# ── Рис. 23.7.4 — гібрид: найкраще з двох ────────────────────────────────────
def fig74_hybrid():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Гібрид: переривання ловить, опитування обробляє", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "найпоширеніше рішення поєднує обидва — і це той самий патерн «прапорець»", 11, GREY, "middle", style="italic")
    s += rect(60, 110, 250, 110, "#eef6ef", GREEN, 1.8, 12)
    s += text(185, 138, "ПЕРЕРИВАННЯ", 12, GREEN, "middle", "bold")
    s += text(185, 162, "ловить подію вмить,", 10, INK, "middle")
    s += text(185, 182, "ставить прапорець", 10, INK, "middle")
    s += text(185, 204, "(не губить, реагує миттєво)", 8.5, GREY, "middle")
    s += arrow(310, 165, 420, 165, GOLD, 2.6)
    s += text(365, 155, "flag", 9, "#8a6a14", "middle", "bold")
    s += rect(420, 110, 280, 110, "#fbecec", RED, 1.8, 12)
    s += text(560, 138, "ОПИТУВАННЯ в loop()", 12, RED, "middle", "bold")
    s += text(560, 162, "у спокої перевіряє прапорець", 10, INK, "middle")
    s += text(560, 182, "і неквапом обробляє подію", 10, INK, "middle")
    s += text(560, 204, "(просто, без обмежень ISR)", 8.5, GREY, "middle")
    s += rect(730, 120, 160, 90, "none", FAINT, 1.6, 10)
    s += text(810, 146, "Виграш:", 10.5, INK, "middle", "bold")
    s += text(810, 168, "миттєвість —", 9.3, GREEN, "middle")
    s += text(810, 184, "від переривання,", 9.3, INK, "middle")
    s += text(810, 200, "простота — від loop", 9.3, RED, "middle")
    s += text(W / 2, 300, "Це й є «золотий патерн» із §23.3: обробник лише відмічає, а робота діється в loop().", 10.5, INK, "middle", "bold")
    s += text(W / 2, 326, "Більшість реальних проєктів — саме такі гібриди, а не «чисте» опитування чи переривання.", 9.7, GREY, "middle")
    save("fig-23-7-4-hybrid.svg", s)


# ── Рис. 23.7.5 — приклади на осі ────────────────────────────────────────────
def fig75_examples():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Приклади на осі «опитування ↔ переривання»", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "де лягає типова задача — підказує, який інструмент брати", 12, GREY, "middle", style="italic")
    x0, x1, y = 90, 870, 200
    s += line(x0, y, x1, y, INK, 2.4)
    s += text(x0, y + 40, "ОПИТУВАННЯ", 12, RED, "start", "bold")
    s += text(x1, y + 40, "ПЕРЕРИВАННЯ", 12, GREEN, "end", "bold")
    items = [
        ("навігація меню", 150, -1, RED),
        ("читати давач раз на 100 мс", 300, 1, "#b06a1e"),
        ("кнопка (з усуненням дребезгу)", 480, -1, GOLD),
        ("лічильник швидких імпульсів", 660, 1, GREEN),
        ("аварійний стоп", 820, -1, GREEN),
    ]
    for lab, x, d, col in items:
        s += circle(x, y, 6, col, col, 0)
        ty = y - 22 if d > 0 else y + 70
        s += line(x, y, x, ty + (8 if d > 0 else -8), col, 1.2, dash="2,2")
        s += text(x, ty, lab, 9.5, INK, "middle", "bold")
    s += text(W / 2, 320, "Періодичне (раз на 100 мс) найкраще робити таймером — це наступний розділ.", 10.3, INK, "middle", "bold")
    s += text(W / 2, 344, "Аварійний стоп — переривання: проґавити не можна й реагувати треба вмить.", 9.7, GREY, "middle")
    save("fig-23-7-5-examples.svg", s)


# ── Рис. 23.7.6 — підсумок розділу (хаб) ─────────────────────────────────────
def fig76_chapter_recap():
    W, H = 960, 470
    s = header(W, H)
    s += text(W / 2, 32, "Розділ про переривання — однією картинкою", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "від ідеї «подія сама кличе» до тонкощів безпечного обміну даними", 11.5, GREY, "middle", style="italic")
    cx, cy = 480, 262
    nodes = [
        (190, 150, "Ідея", ["подія кличе §23.1", "проти опитування"], GREEN),
        (480, 130, "Машинерія", ["контролер, вектор,", "контекст §23.2"], BLUE),
        (770, 150, "Обробник", ["короткий, IRAM §23.3", "відмітити, не робити"], GOLD),
        (770, 374, "Пріоритети", ["витіснення §23.4", "вкладеність, рівні"], RED),
        (480, 394, "volatile", ["свіжість §23.5", "не атомарність"], BLUE),
        (190, 374, "Гонки", ["крит. секція §23.6", "вибір §23.7"], RED),
    ]
    for x, y, t, lines, col in nodes:
        s += line(cx, cy, x, y, col, 1.4, dash="5,3")
    s += circle(cx, cy, 56, LAMB, GOLD, 2.6)
    s += text(cx, cy - 4, "ПЕРЕ-", 13, INK, "middle", "bold")
    s += text(cx, cy + 14, "РИВАННЯ", 13, INK, "middle", "bold")
    for x, y, t, lines, col in nodes:
        s += rect(x - 112, y - 40, 224, 80, "#fbfcff", col, 1.8, 12)
        s += text(x, y - 14, t, 12.5, col, "middle", "bold")
        yy = y + 6
        for ln in lines:
            s += text(x, yy, ln, 9.3, INK, "middle")
            yy += 17
    s += text(W / 2, 452, "Опанувавши переривання, ви навчили мікроконтролер реагувати на світ умить — основа всього далі.", 10, INK, "middle", "bold")
    save("fig-23-7-6-chapter-recap.svg", s)


if __name__ == "__main__":
    # Історія розділу (📜)
    fig01_polling_vs_interrupt()
    fig02_timeline()
    fig03_wind_tunnel()
    fig04_mechanism()
    fig05_mask_vector()
    # §23.1 Переривання: реагувати на подію вмить
    fig11_polling_in_loop()
    fig12_interrupt_benefits()
    fig13_interrupt_flow()
    fig14_attach_interrupt()
    fig15_latency()
    fig16_polling_vs_interrupt()
    # §23.2 Контролер переривань і вектор
    fig21_controller()
    fig22_full_flow()
    fig23_vector_table()
    fig24_context_save()
    fig25_esp32_matrix()
    fig26_gpio_funnel()
    # §23.3 Обробник (ISR): чому коротко
    fig31_isr_on_hold()
    fig32_short_vs_long()
    fig33_dos_donts()
    fig34_deferred_pattern()
    fig35_iram_attr()
    fig36_isr_anatomy()
    # §23.4 Пріоритети й вкладеність
    fig41_why_priority()
    fig42_preemption()
    fig43_nesting_stack()
    fig44_same_level()
    fig45_esp32_levels()
    fig46_stack_danger()
    # §23.5 volatile
    fig51_cached_in_register()
    fig52_volatile_fix()
    fig53_what_compiler_does()
    fig54_when_to_use()
    fig55_volatile_not_atomic()
    fig56_volatile_example()
    # §23.6 Атомарність і гонки даних
    fig61_race_condition()
    fig62_what_is_atomic()
    fig63_critical_section()
    fig64_snapshot_pattern()
    fig65_keep_short()
    fig66_esp32_spinlock()
    # §23.7 Polling vs переривання
    fig71_two_tools()
    fig72_decision_flow()
    fig73_criteria()
    fig74_hybrid()
    fig75_examples()
    fig76_chapter_recap()
    print("OK - figures for Section 23 (history + 23.1..23.7, complete) generated in", OUT)
