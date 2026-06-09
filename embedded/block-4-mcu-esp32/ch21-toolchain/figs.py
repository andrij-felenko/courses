# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 21 — «Тулчейн: як код стає прошивкою» (Модуль 4).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи нумеруються посекційно
(Рис. C.S.N) у тексті розділу; для історії до розділу — секція 0 (Рис. 21.0.N).

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
PAPER = "#fbf6e9"   # тло «паперу» журналу
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


def ellipse(cx, cy, rx, ry, fill="none", stroke=INK, w=1.5):
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def blk(x, y, w, h, label, sub="", fill="#ffffff", stroke=INK, lcol=INK):
    o = rect(x, y, w, h, fill, stroke, 1.8, 4)
    if sub:
        o += text(x + w / 2, y + h / 2 - 3, label, 12.5, lcol, "middle", "bold")
        o += text(x + w / 2, y + h / 2 + 13, sub, 10, GREY, "middle")
    else:
        o += text(x + w / 2, y + h / 2 + 4, label, 12.5, lcol, "middle", "bold")
    return o


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── Рис. 21.0.1 — таймлайн «ланцюг питань» ───────────────────────────────────
def fig01_timeline():
    W, H = 940, 720
    s = header(W, H)
    s += text(W / 2, 38, "Ланцюг питань: чи може машина програмувати сама себе?", 20, INK, "middle", "bold")
    s += text(W / 2, 60, "від програмування числами до компілятора (сірим — зміст Розділу 21)", 12.5, GREY, "middle", style="italic")
    spine = 250
    top, bot = 92, H - 28
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("1940-ві", "Програмування числами / Mark I · ENIAC",
         "Людина вручну пише стовпці машинних кодів. Чи може машина програмувати себе?", False, False),
        ("1944", "Грейс Гоппер → Mark I",
         "Одна з перших програмісток велетня. Це МУСИТЬ бути простіше!", False, False),
        ("1947", "Метелик у реле (Mark II)",
         "Перший буквальний «баг» → народження «дебагу»", False, False),
        ("~1951", "Зухвала ідея",
         "Хай МАШИНА перекладає людський запис у код. «Не вірю» — кажуть скептики", False, False),
        ("1952", "A-0 — перший компілятор",
         "Машина сама збирає програму з бібліотеки. Стіну скепсису пробито", False, True),
        ("1959", "FLOW-MATIC → COBOL",
         "Команди англійськими словами; техніка служить людині", False, False),
        ("Розділ 21", "Тулчейн",
         "Як саме код стає прошивкою?", True, False),
    ]
    n = len(nodes)
    for i, (yr, who, q, dest, accent) in enumerate(nodes):
        y = top + 28 + (bot - top - 56) * i / (n - 1)
        col = GREY if dest else INK
        if accent:
            s += circle(spine, y, 10, "#ffffff", RED, 3)
            s += circle(spine, y, 4.5, RED, RED, 0)
        elif dest:
            s += rect(spine - 8, y - 8, 16, 16, "#ffffff", GREEN, 2.6, 3)
        else:
            s += circle(spine, y, 7, "#ffffff", col, 2.6)
        s += text(spine - 22, y + 5, yr, 12.5, (GREEN if dest else GREY), "end", "bold")
        s += text(spine + 26, y - 3, who, 15, (RED if accent else (GREEN if dest else col)), "start", "bold")
        s += text(spine + 26, y + 17, q, 12.5, (INK if not dest else GREY), "start", style="italic")
    save("fig-21-0-1-timeline.svg", s)


# ── Рис. 21.0.2 — програмування числами проти людського запису ───────────────
def fig02_programming_in_numbers():
    W, H = 920, 430
    s = header(W, H)
    s += text(W / 2, 34, "Доба програмування числами: людина думала як машина", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "увесь труд програміста — ручний переклад ясного наміру в стовпець кодів", 12.5, GREY, "middle", style="italic")
    # ліворуч — людський намір
    s += rect(40, 96, 320, 250, "none", FAINT, 2, 14)
    s += text(200, 122, "Як бачить людина", 13.5, INK, "middle", "bold")
    s += rect(80, 170, 240, 110, LGRN, GREEN, 2, 16)
    s += text(200, 210, "«склади два числа", 14, INK, "middle", "bold")
    s += text(200, 232, "й покажи суму»", 14, INK, "middle", "bold")
    s += text(200, 262, "— ясний намір", 11, GREY, "middle", style="italic")
    # стрілка
    s += arrow(372, 220, 470, 220, INK, 3.5)
    s += text(421, 204, "ручний", 11, RED, "middle", "bold")
    s += text(421, 240, "переклад", 11, RED, "middle", "bold")
    # праворуч — машинний код
    s += rect(490, 96, 390, 250, "none", FAINT, 2, 14)
    s += text(685, 122, "Як подати машині (1940-ві)", 13, INK, "middle", "bold")
    s += rect(540, 150, 290, 170, "#101418", "#000000", 1.5, 8)
    rows = [("адр 000", "76 0017"), ("адр 001", "31 0020"), ("адр 002", "55 0021"),
            ("адр 003", "20 0000"), ("адр 004", "…", )]
    for i, (a, code) in enumerate(rows):
        y = 178 + i * 28
        s += text(560, y, a, 12, "#7fa6bf", "start")
        s += text(700, y, code, 13, "#7fe0a0", "start", "bold")
    s += text(685, 336, "голі числа за точними адресами", 10.5, GREY, "middle", style="italic")
    s += rect(120, 372, 680, 40, LRED, RED, 1.4, 8)
    s += text(460, 396, "Повільно, помилконебезпечно, під силу лише втаємниченим — вузьке місце всієї науки.",
              12, INK, "middle", "bold")
    save("fig-21-0-2-programming-in-numbers.svg", s)


# ── Рис. 21.0.3 — метелик у журналі ──────────────────────────────────────────
def fig03_moth_bug():
    W, H = 880, 440
    s = header(W, H)
    s += text(W / 2, 34, "Перший справжній «баг»: метелик у реле, 1947", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "слово «bug» було й раніше — та цей випадок прославив його й дав «дебаг»", 12.5, GREY, "middle", style="italic")
    # сторінка журналу
    px, py, pw, ph = 130, 90, 470, 290
    s += rect(px, py, pw, ph, PAPER, "#c9bd9a", 2, 6)
    for i in range(7):
        ly = py + 70 + i * 30
        s += line(px + 24, ly, px + pw - 24, ly, "#d8ccab", 1.2)
    s += line(px + 70, py + 12, px + 70, py + ph - 12, "#e0b0b0", 1.2)  # поля
    s += text(px + 24, py + 34, "Robookъ log — Mark II", 12, "#9a7b46", "start", "bold")
    s += text(px + 24, py + 54, "9 Sept 1947", 11.5, "#9a7b46", "start")
    # метелик
    mx, my = px + 300, py + 150
    s += ellipse(mx - 17, my - 6, 17, 12, "#c8bfa8", "#8a7a5a", 1.4)
    s += ellipse(mx + 17, my - 6, 17, 12, "#c8bfa8", "#8a7a5a", 1.4)
    s += ellipse(mx - 12, my + 12, 12, 9, "#bcb29a", "#8a7a5a", 1.2)
    s += ellipse(mx + 12, my + 12, 12, 9, "#bcb29a", "#8a7a5a", 1.2)
    s += ellipse(mx, my, 5, 18, "#5a4a3a", "#3a2e22", 1.2)
    s += line(mx, my - 16, mx - 9, my - 28, "#5a4a3a", 1.4)
    s += line(mx, my - 16, mx + 9, my - 28, "#5a4a3a", 1.4)
    # скотч
    s += rect(mx - 30, my - 26, 16, 52, "#dfe7f0", "#b8c4d2", 1, 2)
    s += rect(mx + 14, my - 26, 16, 52, "#dfe7f0", "#b8c4d2", 1, 2)
    # підпис у журналі
    s += text(px + 24, py + 232, "First actual case of", 13, INK, "start", "bold")
    s += text(px + 24, py + 256, "bug being found.", 13, INK, "start", "bold")
    # стрілка до «дебаг»
    s += arrow(px + pw + 6, py + 140, px + pw + 90, py + 140, INK, 2.6)
    s += rect(px + pw + 96, py + 96, 150, 96, LGRN, GREEN, 2, 10)
    s += text(px + pw + 171, py + 128, "«debugging»", 14, GREEN, "middle", "bold")
    s += text(px + pw + 171, py + 152, "вилов багів —", 11, INK, "middle")
    s += text(px + pw + 171, py + 170, "ремесло й донині", 11, INK, "middle")
    s += text(W / 2, 410, "Мораль жива: причина збою буває не там, де шукаєш у коді, — навіть «комаха в реле».",
              11.5, INK, "middle", "bold")
    save("fig-21-0-3-moth-bug.svg", s)


# ── Рис. 21.0.4 — ідея компілятора ───────────────────────────────────────────
def fig04_compiler_idea():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 34, "Переломна ідея Гоппер: хай переклад робить програма", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "марудну механічну роботу перекладу — на саму машину", 12.5, GREY, "middle", style="italic")
    # верх — раніше (людина)
    s += rect(30, 84, 860, 130, "none", FAINT, 2, 12)
    s += text(50, 108, "Раніше: перекладає ЛЮДИНА", 13.5, RED, "start", "bold")
    s += blk(70, 130, 180, 56, "людський запис", "ясний намір", fill=LGRN, stroke=GREEN)
    s += circle(420, 158, 22, "#fbeaea", RED, 2)
    s += text(420, 163, "люд.", 11, RED, "middle", "bold")
    s += arrow(252, 158, 396, 158, RED, 2.4)
    s += arrow(444, 158, 600, 158, RED, 2.4)
    s += text(330, 148, "повільно,", 10, GREY, "middle")
    s += text(522, 148, "з помилками", 10, GREY, "middle")
    s += blk(602, 130, 180, 56, "машинний код", "числа", fill="#eef0f5", stroke=INK)
    # низ — ідея (програма)
    s += rect(30, 234, 860, 150, "none", LGRN, 2, 12)
    s += text(50, 258, "Ідея Гоппер: перекладає ПРОГРАМА", 13.5, GREEN, "start", "bold")
    s += blk(70, 286, 180, 60, "людський запис", "ясний намір", fill=LGRN, stroke=GREEN)
    s += rect(396, 282, 168, 68, LAMB, GOLD, 2.4, 10)
    s += text(480, 310, "Компілятор", 14, "#8a6a14", "middle", "bold")
    s += text(480, 330, "(програма-перекладач)", 9.5, GREY, "middle")
    s += arrow(252, 316, 392, 316, GREEN, 2.6)
    s += arrow(568, 316, 700, 316, GREEN, 2.6)
    s += blk(702, 286, 160, 60, "машинний код", "числа", fill="#eef0f5", stroke=INK)
    s += text(480, 372, "швидко · точно · щоразу однаково", 11, INK, "middle", "bold")
    save("fig-21-0-4-compiler-idea.svg", s)


# ── Рис. 21.0.5 — A-0: складач із бібліотеки ─────────────────────────────────
def fig05_a0_library():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 34, "A-0 (1952): машина сама збирає програму з бібліотеки", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "зародок і компілятора (переклад), і лінкера (зшивання шматків)", 12.5, GREY, "middle", style="italic")
    # ліворуч — номери підпрограм
    s += rect(40, 100, 180, 230, "none", FAINT, 2, 12)
    s += text(130, 124, "запис задачі", 12.5, INK, "middle", "bold")
    s += text(130, 142, "(номери підпрограм)", 9.5, GREY, "middle")
    for i, num in enumerate(["№12", "№7", "№31", "№4"]):
        s += rect(80, 160 + i * 40, 100, 30, "#eef3ff", BLUE, 1.6, 6)
        s += text(130, 181 + i * 40, num, 13, BLUE, "middle", "bold")
    # центр — A-0
    s += rect(320, 150, 180, 110, LAMB, GOLD, 2.4, 12)
    s += text(410, 196, "A-0", 20, "#8a6a14", "middle", "bold")
    s += text(410, 220, "складач", 12, INK, "middle", "bold")
    s += text(410, 240, "(compiler)", 10, GREY, "middle")
    s += arrow(222, 205, 318, 205, INK, 2.6)
    # бібліотека (стрічка) знизу
    s += rect(300, 300, 220, 64, "#efe7d2", "#b79a5e", 2, 8)
    s += text(410, 322, "бібліотека підпрограм", 11.5, "#8a6a14", "middle", "bold")
    s += text(410, 342, "(на стрічці)", 9.5, GREY, "middle")
    s += arrow(410, 298, 410, 262, "#8a6a14", 2.4)
    s += text(430, 285, "дістає потрібні", 9.5, GREY, "start", style="italic")
    # праворуч — готова програма
    s += rect(600, 120, 280, 200, "#101418", "#000000", 1.5, 8)
    s += text(740, 144, "одна машинна програма", 11.5, "#7fa6bf", "middle", "bold")
    for i in range(6):
        y = 170 + i * 24
        s += line(620, y, 860, y, "#2b3540", 1)
        s += text(632, y + 4, f"…{(i * 7 + 11) % 90:02d} {(i * 13 + 3) % 90:02d}{(i * 5) % 90:02d}", 11, "#7fe0a0", "start")
    s += arrow(502, 205, 598, 205, GREEN, 2.6)
    s += text(550, 195, "склеює", 10, GREEN, "middle", "bold")
    s += text(740, 336, "адреси узгоджено, шматки зшито", 10, GREY, "middle", style="italic")
    save("fig-21-0-5-a0-library.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §21.1 — Від тексту до машинного коду: що таке компіляція
# ─────────────────────────────────────────────────────────────────────────────

# ── Рис. 21.1.1 — два світи ──────────────────────────────────────────────────
def fig11_two_worlds():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Два світи: текст для людини, числа для машини", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "той самий намір — два геть різні описи", 12.5, GREY, "middle", style="italic")
    s += rect(50, 110, 330, 200, "#0f1b14", "#0a120d", 1.5, 8)
    s += text(70, 138, "вихідний код (для людини)", 11, "#8fcf9f", "start", "bold")
    s += text(70, 178, "OUT |= (1 << 2);", 15, "#eaf6ee", "start", "bold")
    s += text(70, 204, "// увімкнути біт 2", 12, "#7a9a86", "start", style="italic")
    s += text(215, 268, "легко читає людина", 11, GREY, "middle", style="italic")
    s += arrow(388, 200, 438, 200, RED, 2.6)
    s += text(450, 208, "?", 30, RED, "middle", "bold")
    s += arrow(462, 200, 512, 200, RED, 2.6)
    s += text(450, 244, "переклад", 10.5, RED, "middle", "bold")
    s += rect(520, 110, 330, 200, "#101418", "#000000", 1.5, 8)
    s += text(540, 138, "машинний код (для ядра)", 11, "#7fa6bf", "start", "bold")
    for i, code in enumerate(["3A 01 7C 4F", "2B 01 04 00", "3C 01 7C 4F"]):
        s += text(540, 174 + i * 26, code, 14, "#7fe0a0", "start", "bold")
    s += text(685, 268, "єдине, що розуміє кремній", 11, GREY, "middle", style="italic")
    s += rect(120, 344, 660, 34, LAMB, GOLD, 1.4, 8)
    s += text(450, 366, "Хтось мусить перекласти лівий опис на правий — це й робить компілятор.", 12, INK, "middle", "bold")
    save("fig-21-1-1-two-worlds.svg", s)


# ── Рис. 21.1.2 — що таке компіляція ─────────────────────────────────────────
def fig12_what_is_compilation():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 34, "Компіляція: текст → машинний код для конкретного ядра", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "які саме числа — залежить від ядра", 12.5, GREY, "middle", style="italic")
    s += rect(40, 168, 200, 84, "#0f1b14", "#0a120d", 1.5, 8)
    s += text(140, 198, "вихідний код", 12, "#8fcf9f", "middle", "bold")
    s += text(140, 224, "OUT |= (1<<2);", 11.5, "#eaf6ee", "middle", "bold")
    s += rect(310, 160, 180, 100, LAMB, GOLD, 2.4, 12)
    s += text(400, 205, "Компілятор", 14, "#8a6a14", "middle", "bold")
    s += text(400, 228, "перекладач", 10, GREY, "middle")
    s += arrow(242, 210, 306, 210, INK, 2.6)
    s += rect(580, 106, 300, 84, "#101418", "#000000", 1.5, 8)
    s += text(600, 132, "для Xtensa (ESP32, S3):", 10.5, "#7fa6bf", "start", "bold")
    s += text(600, 162, "3A 01 7C…  2B 01 04…", 13, "#7fe0a0", "start", "bold")
    s += rect(580, 228, 300, 84, "#101418", "#000000", 1.5, 8)
    s += text(600, 254, "для RISC-V (C3, C6):", 10.5, "#7fa6bf", "start", "bold")
    s += text(600, 284, "0C 1A 04…  93 81 41…", 13, "#7fe0a0", "start", "bold")
    s += arrow(492, 198, 576, 150, INK, 2.4)
    s += arrow(492, 222, 576, 270, INK, 2.4)
    s += text(534, 146, "під Xtensa", 9, GREY, "middle")
    s += text(534, 286, "під RISC-V", 9, GREY, "middle")
    s += rect(110, 360, 700, 40, LGRN, GREEN, 1.4, 8)
    s += text(460, 384, "Один текст → різні числа під різні ядра (звідси «зібрати ПІД ESP32 / ПІД C3»).", 11.5, INK, "middle", "bold")
    save("fig-21-1-2-what-is-compilation.svg", s)


# ── Рис. 21.1.3 — компільоване проти інтерпретованого ────────────────────────
def fig13_compiled_vs_interpreted():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "Перекласти раз наперед чи щоразу на ходу", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "мікроконтролери майже завжди обирають перший шлях", 12.5, GREY, "middle", style="italic")
    s += rect(30, 84, 420, 322, "none", LGRN, 2, 12)
    s += text(240, 108, "Компільований — переклад РАЗ наперед", 12, GREEN, "middle", "bold")
    s += blk(70, 142, 150, 50, "вихідний код", fill="#0f1b14", lcol="#eaf6ee")
    s += arrow(222, 167, 268, 167, INK, 2.2)
    s += text(245, 158, "раз", 9, GREY, "middle")
    s += blk(270, 142, 150, 50, "машинний код", fill="#101418", lcol="#7fe0a0")
    s += arrow(345, 194, 345, 238, GREEN, 2.4)
    s += rect(270, 240, 150, 54, LRED, RED, 1.8, 8)
    s += text(345, 264, "Чіп біжить", 12, RED, "middle", "bold")
    s += text(345, 282, "напряму", 9.5, GREY, "middle")
    s += text(240, 332, "швидко · мало пам'яті · без посередника", 10.5, INK, "middle", "bold")
    s += text(240, 362, "← так роблять мікроконтролери", 11, GREEN, "middle", "bold")
    s += rect(470, 84, 420, 322, "none", FAINT, 2, 12)
    s += text(680, 108, "Інтерпретований — переклад НА ХОДУ", 12, BLUE, "middle", "bold")
    s += blk(500, 142, 150, 50, "вихідний код", fill="#0f1b14", lcol="#eaf6ee")
    s += arrow(652, 167, 696, 167, BLUE, 2.2)
    s += rect(700, 136, 162, 62, LBLUE, BLUE, 1.8, 8)
    s += text(781, 162, "Інтерпретатор", 11, BLUE, "middle", "bold")
    s += text(781, 182, "у пам'яті чипа", 9, GREY, "middle")
    s += arrow(781, 198, 781, 240, BLUE, 2.4)
    s += text(800, 222, "щоразу читає", 9, GREY, "start")
    s += rect(700, 242, 162, 54, LRED, RED, 1.8, 8)
    s += text(781, 266, "виконує рядок", 11, INK, "middle", "bold")
    s += text(781, 284, "за рядком", 9.5, GREY, "middle")
    s += text(680, 332, "гнучко, але повільніше й важче", 10.5, INK, "middle", "bold")
    s += text(680, 362, "(на МК — виняток: MicroPython)", 10.5, GREY, "middle", style="italic")
    save("fig-21-1-3-compiled-vs-interpreted.svg", s)


# ── Рис. 21.1.4 — конвеєр тулчейну ───────────────────────────────────────────
def fig14_toolchain_pipeline():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 34, "Тулчейн: конвеєр від тексту до прошивки", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "«скомпілювати» — це не один крок, а кілька злагоджених", 12.5, GREY, "middle", style="italic")
    stages = [
        ("вихідний|код", "текст", LGRN, GREEN),
        ("Препроцесор", "готує текст", "#fbfbfb", INK),
        ("Компілятор", "→ команди", "#fbfbfb", INK),
        ("Асемблер", "→ числа", "#fbfbfb", INK),
        ("Лінкер", "зшиває все", "#fbfbfb", INK),
        ("Образ|прошивки", "готово!", LAMB, GOLD),
    ]
    x0, w, gap, y = 24, 138, 16, 148
    for i, (t1, t2, fill, col) in enumerate(stages):
        x = x0 + i * (w + gap)
        s += rect(x, y, w, 78, fill, col, 2.2 if col in (GREEN, GOLD) else 1.8, 10)
        lines = t1.split("|")
        for j, ln in enumerate(lines):
            s += text(x + w / 2, y + 30 + (j - (len(lines) - 1) / 2) * 16, ln, 12.5, col, "middle", "bold")
        s += text(x + w / 2, y + 62, t2, 9.5, GREY, "middle")
        if i < len(stages) - 1:
            s += arrow(x + w, y + 39, x + w + gap + 1, y + 39, INK, 2.4)
    s += text(W / 2, 272, "Кожен крок — окремий інструмент зі своєю вузькою роботою; разом вони і є тулчейн.",
              12, INK, "middle", "bold")
    s += text(W / 2, 298, "Стадії розберемо детально в §21.2–§21.3.", 11, GREY, "middle", style="italic")
    save("fig-21-1-4-toolchain-pipeline.svg", s)


# ── Рис. 21.1.5 — крос-компіляція ────────────────────────────────────────────
def fig15_cross_compilation():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Крос-компіляція: збираємо тут — а для туди", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "машина-будівельник і машина-ціль — різні", 12.5, GREY, "middle", style="italic")
    s += rect(60, 108, 320, 210, "none", FAINT, 2, 12)
    s += text(220, 134, "ПК (ядро x86)", 13.5, INK, "middle", "bold")
    s += rect(100, 158, 240, 70, LBLUE, BLUE, 2, 8)
    s += text(220, 188, "Тулчейн працює тут", 12, BLUE, "middle", "bold")
    s += text(220, 208, "(компілює, лінкує)", 10, GREY, "middle")
    s += text(220, 270, "✗ результат тут НЕ запуститься", 11, RED, "middle", "bold")
    s += text(220, 290, "це «чужі» для ПК числа", 9.5, GREY, "middle")
    s += arrow(388, 210, 510, 210, GREEN, 3.5)
    s += rect(408, 192, 84, 30, LAMB, GOLD, 1.6, 6)
    s += text(450, 212, "прошивка", 10, "#8a6a14", "middle", "bold")
    s += rect(520, 108, 320, 210, "none", FAINT, 2, 12)
    s += text(680, 134, "Мікроконтролер", 13.5, INK, "middle", "bold")
    s += text(680, 152, "(Xtensa / RISC-V)", 10, GREY, "middle")
    s += rect(560, 178, 240, 70, LGRN, GREEN, 2, 8)
    s += text(680, 208, "Код біжить тут", 12, GREEN, "middle", "bold")
    s += text(680, 228, "✓ це його рідні числа", 10, GREEN, "middle", "bold")
    s += text(680, 290, "для кожного чипа — своя «ціль» у тулчейні", 10.5, INK, "middle", "bold")
    save("fig-21-1-5-cross-compilation.svg", s)


# ── Рис. 21.1.6 — один рядок → багато команд → числа ─────────────────────────
def fig16_one_line_many():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 32, "Один рядок → кілька машинних команд → числа", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "компілятор робить за вас усю дрібну роботу, яку колись робили вручну", 12.5, GREY, "middle", style="italic")
    s += rect(300, 82, 300, 52, "#0f1b14", "#0a120d", 1.5, 8)
    s += text(450, 114, "OUT |= (1 << 2);", 15, "#eaf6ee", "middle", "bold")
    s += text(612, 110, "← один рядок C", 11, GREY, "start", style="italic")
    s += arrow(450, 136, 450, 166, INK, 2.6)
    s += rect(250, 170, 400, 112, "#13202a", "#0a141b", 1.5, 8)
    instrs = [("load  r1, [OUT]", "; прочитати"),
              ("or    r1, r1, 0x04", "; накласти маску 1<<2"),
              ("store [OUT], r1", "; записати назад")]
    for i, (ins, cm) in enumerate(instrs):
        s += text(270, 202 + i * 32, ins, 13, "#7fe0a0", "start", "bold")
        s += text(456, 202 + i * 32, cm, 10.5, "#6f8fa0", "start")
    s += text(662, 220, "← кілька", 11, GREY, "start", style="italic")
    s += text(662, 238, "  машинних команд", 11, GREY, "start", style="italic")
    s += arrow(450, 284, 450, 312, INK, 2.6)
    s += rect(300, 314, 300, 46, "#101418", "#000000", 1.5, 8)
    s += text(450, 343, "3A 01 ..  2B 01 04  3C 01 ..", 13.5, "#7fe0a0", "middle", "bold")
    s += text(612, 341, "← лише числа", 11, GREY, "start", style="italic")
    s += text(W / 2, 398, "І ці числа РІЗНІ для різних ядер. Оце розгортання й є, по суті, вся компіляція.", 12, INK, "middle", "bold")
    save("fig-21-1-6-one-line-many.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §21.2 — Препроцесор, компілятор, асемблер (стадії)
# ─────────────────────────────────────────────────────────────────────────────

# ── Рис. 21.2.1 — три стадії й дані на межах ─────────────────────────────────
def fig21_three_stages():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 34, "Перші три стадії: препроцесор → компілятор → асемблер", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "стежте, як код міняє форму на кожній межі", 12.5, GREY, "middle", style="italic")
    y = 158
    s += rect(16, y, 130, 80, LGRN, GREEN, 2, 10)
    s += text(81, y + 36, "файл коду", 12, GREEN, "middle", "bold")
    s += text(81, y + 56, "(.c / .cpp)", 9.5, GREY, "middle")
    s += blk(196, y, 150, 80, "Препроцесор")
    s += blk(404, y, 150, 80, "Компілятор")
    s += blk(612, y, 150, 80, "Асемблер")
    s += rect(810, y, 135, 80, "#101418", "#000000", 1.6, 10)
    s += text(877, y + 36, "об'єктний", 12, "#7fe0a0", "middle", "bold")
    s += text(877, y + 56, "файл  .o", 10.5, "#7fa6bf", "middle", "bold")
    arrows = [(146, 196, ""), (346, 404, "розгорн. текст"), (554, 612, "асемблер"), (762, 810, "числа")]
    for x1, x2, lbl in arrows:
        s += arrow(x1, y + 40, x2 - 2, y + 40, INK, 2.4)
        if lbl:
            s += text((x1 + x2) / 2, y - 4, lbl, 9.5, GREY, "middle", "bold")
    s += text(W / 2, 300, "Кожна стадія приймає вихід попередньої й опускає код на щабель нижче.", 12, INK, "middle", "bold")
    s += text(W / 2, 324, "Один файл коду → один об'єктний файл.", 11, GREY, "middle", style="italic")
    save("fig-21-2-1-three-stages.svg", s)


# ── Рис. 21.2.2 — препроцесор ────────────────────────────────────────────────
def fig22_preprocessor():
    W, H = 940, 440
    s = header(W, H)
    s += text(W / 2, 34, "Препроцесор: суто текстові операції", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "ріже й клеїть текст, не розуміючи коду", 12.5, GREY, "middle", style="italic")
    rows = [
        ("вклеїти файл", "#include <Arduino.h>", "→ весь вміст файлу вклеєно"),
        ("підставити визначення", "#define LED 2 … LED", "→ … 2"),
        ("умовне включення", "#ifdef ESP32 … #endif", "→ код лишити або викинути"),
    ]
    y0 = 108
    for i, (what, before, after) in enumerate(rows):
        y = y0 + i * 98
        s += text(60, y - 8, what, 12, INK, "start", "bold")
        s += rect(60, y, 380, 56, "#0f1b14", "#0a120d", 1.4, 8)
        s += text(78, y + 34, before, 12.5, "#eaf6ee", "start", "bold")
        s += arrow(448, y + 28, 506, y + 28, GOLD, 2.6)
        s += rect(516, y, 360, 56, "#13202a", "#0a141b", 1.4, 8)
        s += text(534, y + 34, after, 12, "#7fe0a0", "start", "bold")
    s += rect(120, 402, 700, 30, LAMB, GOLD, 1.4, 8)
    s += text(470, 422, "На виході — суцільний текст без жодного «#». Стадія «дурна»: лише ріже й клеїть.",
              11.5, INK, "middle", "bold")
    save("fig-21-2-2-preprocessor.svg", s)


# ── Рис. 21.2.3 — компілятор ─────────────────────────────────────────────────
def fig23_compiler():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Компілятор: серце перекладу — три справи заразом", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "чистий текст → асемблер для цільового ядра", 12.5, GREY, "middle", style="italic")
    s += rect(40, 168, 160, 76, "#0f1b14", "#0a120d", 1.4, 8)
    s += text(120, 198, "чистий текст", 11.5, "#8fcf9f", "middle", "bold")
    s += text(120, 222, "(від препроцесора)", 9, GREY, "middle")
    s += rect(280, 108, 300, 204, LAMB, GOLD, 2.4, 12)
    s += text(430, 132, "Компілятор", 14, "#8a6a14", "middle", "bold")
    jobs = [("1. Розбирає", "граматика, типи → ПОМИЛКИ", RED),
            ("2. Породжує", "команди цільового ядра", INK),
            ("3. Оптимізує", "коротше / швидше", GREEN)]
    for i, (t, d, col) in enumerate(jobs):
        yy = 158 + i * 50
        s += rect(298, yy, 264, 42, "#ffffff", col, 1.6, 6)
        s += text(310, yy + 19, t, 12, col, "start", "bold")
        s += text(310, yy + 34, d, 9.5, GREY, "start")
    s += arrow(204, 206, 278, 206, INK, 2.4)
    s += rect(660, 168, 200, 76, "#13202a", "#0a141b", 1.4, 8)
    s += text(760, 198, "асемблер", 11.5, "#7fe0a0", "middle", "bold")
    s += text(760, 222, "(мнемоніки)", 9, GREY, "middle")
    s += arrow(582, 206, 656, 206, INK, 2.4)
    s += text(450, 360, "«Помилки компіляції» родяться на РОЗБОРІ — і це добре: видно ще до заливання.",
              11.5, INK, "middle", "bold")
    save("fig-21-2-3-compiler.svg", s)


# ── Рис. 21.2.4 — оптимізація ────────────────────────────────────────────────
def fig24_optimization():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 32, "Оптимізація: той самий результат — меншими командами", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "компілятор зберігає результат, але вільний переписати шлях до нього", 12.5, GREY, "middle", style="italic")
    s += rect(40, 96, 400, 256, "none", FAINT, 2, 12)
    s += text(240, 120, "Як написано (наївно)", 13, INK, "middle", "bold")
    s += rect(60, 142, 360, 168, "#0f1b14", "#0a120d", 1.4, 8)
    naive = ["x = 2 * 3;        // рахуємо в коді", "y = x;            // зайва копія",
             "// y далі ніде не вжито", "while (0) { ... }  // 0 разів"]
    for i, ln in enumerate(naive):
        s += text(76, 172 + i * 34, ln, 10.5, "#cfe0d6", "start")
    s += text(240, 338, "багато зайвих кроків", 10.5, RED, "middle", "bold")
    s += arrow(448, 224, 502, 224, GREEN, 3.5)
    s += rect(512, 96, 368, 256, "none", LGRN, 2, 12)
    s += text(696, 120, "Що згенерував компілятор", 13, GREEN, "middle", "bold")
    s += rect(532, 142, 328, 130, "#13202a", "#0a141b", 1.4, 8)
    s += text(548, 178, "// x = 6  (пораховано наперед)", 10.5, "#7fe0a0", "start")
    s += text(548, 208, "// y і цикл — викинуто (мертві)", 10.5, "#7fe0a0", "start")
    s += text(548, 238, "…лишилось тільки потрібне", 10.5, "#7fe0a0", "start")
    s += text(696, 300, "стале пораховано, мертве викинуто", 10.5, GREEN, "middle", "bold")
    s += text(696, 322, "→ коротше й швидше", 11, INK, "middle", "bold")
    save("fig-21-2-4-optimization.svg", s)


# ── Рис. 21.2.5 — асемблер ───────────────────────────────────────────────────
def fig25_assembler():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 34, "Асемблер: кожна мнемоніка → одна машинна команда (число)", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "майже дослівно, один-в-один — ніякого розуму, лише словник", 12.5, GREY, "middle", style="italic")
    s += text(250, 104, "асемблер (мнемоніка)", 12, INK, "middle", "bold")
    s += text(670, 104, "машинний код (число)", 12, INK, "middle", "bold")
    rows = [("load  r1, [GPIO_OUT]", "3A 01 7C"),
            ("or    r1, r1, 0x04", "2B 01 04"),
            ("store [GPIO_OUT], r1", "3C 01 7C")]
    for i, (asm, code) in enumerate(rows):
        y = 130 + i * 62
        s += rect(60, y, 380, 46, "#13202a", "#0a141b", 1.4, 8)
        s += text(78, y + 29, asm, 13, "#7fe0a0", "start", "bold")
        s += arrow(450, y + 23, 512, y + 23, GOLD, 2.6)
        s += rect(522, y, 300, 46, "#101418", "#000000", 1.4, 8)
        s += text(672, y + 29, code, 14, "#7fe0a0", "middle", "bold")
    s += rect(120, 332, 640, 44, LAMB, GOLD, 1.4, 8)
    s += text(440, 352, "Результат — об'єктний файл (.o): машинний код, але ще НЕ готова програма", 11.5, INK, "middle", "bold")
    s += text(440, 369, "(адреси й посилання на інші файли — заповнить лінкер, §21.3)", 10, GREY, "middle")
    save("fig-21-2-5-assembler.svg", s)


# ── Рис. 21.2.6 — простежмо фрагмент крізь стадії ────────────────────────────
def fig26_trace():
    W, H = 900, 540
    s = header(W, H)
    s += text(W / 2, 32, "Один фрагмент крізь три стадії — у чотирьох формах", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "один крок конвеєра — одне перетворення форми", 12.5, GREY, "middle", style="italic")
    forms = [
        ("1. вихідний код (з директивою)", "#define LED_PIN 2   ·   GPIO_OUT |= (1 << LED_PIN);", "#0f1b14", "#eaf6ee", "препроцесор ↓"),
        ("2. після препроцесора", "GPIO_OUT |= (1 << 2);     // «#» зникли, текст підставлено", "#0f1b14", "#eaf6ee", "компілятор ↓"),
        ("3. після компілятора (асемблер)", "load r1,[GPIO_OUT]  ·  or r1,r1,0x04  ·  store [GPIO_OUT],r1", "#13202a", "#7fe0a0", "асемблер ↓"),
        ("4. після асемблера (числа)", "3A 01 7C    2B 01 04    3C 01 7C", "#101418", "#7fe0a0", None),
    ]
    y0 = 92
    for i, (label, code, bg, fg, albl) in enumerate(forms):
        y = y0 + i * 108
        s += text(70, y - 6, label, 11.5, INK, "start", "bold")
        s += rect(60, y, 780, 56, bg, "#0a120d", 1.4, 8)
        s += text(78, y + 34, code, 12, fg, "start", "bold")
        if albl:
            s += arrow(450, y + 60, 450, y + 96, GOLD, 2.4)
            s += text(560, y + 82, albl, 10.5, GOLD, "middle", "bold")
    save("fig-21-2-6-trace.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §21.3 — Лінкування: збираємо все докупи
# ─────────────────────────────────────────────────────────────────────────────

# ── Рис. 21.3.1 — лінкер: багато .o + бібліотеки → одна програма ─────────────
def fig31_linker_overview():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 34, "Лінкер: багато об'єктних файлів + бібліотеки → одна програма", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "із розрізнених деталей — готовий механізм", 12.5, GREY, "middle", style="italic")
    for i, o in enumerate(["main.o", "blink.o", "sensor.o"]):
        y = 108 + i * 58
        s += rect(60, y, 150, 46, "#101418", "#000000", 1.4, 6)
        s += text(135, y + 28, o, 12.5, "#7fe0a0", "middle", "bold")
        s += arrow(214, y + 23, 304, 212, GREY, 2)
    s += rect(60, 300, 150, 52, "#efe7d2", "#b79a5e", 1.6, 8)
    s += text(135, 322, "бібліотеки", 12, "#8a6a14", "middle", "bold")
    s += text(135, 340, "(Arduino, IDF…)", 9, GREY, "middle")
    s += arrow(214, 326, 304, 244, GREY, 2)
    s += rect(312, 168, 180, 112, LAMB, GOLD, 2.4, 12)
    s += text(402, 216, "Лінкер", 18, "#8a6a14", "middle", "bold")
    s += text(402, 240, "зшиває все", 11, GREY, "middle")
    s += arrow(494, 224, 582, 224, GREEN, 3)
    s += rect(592, 168, 290, 112, LGRN, GREEN, 2, 12)
    s += text(737, 208, "одна повна програма", 13, GREEN, "middle", "bold")
    s += text(737, 232, "дірки заповнено,", 10, INK, "middle")
    s += text(737, 250, "адреси роздано", 10, INK, "middle")
    s += text(460, 392, "Лінкер — той, хто з деталей збирає готовий механізм.", 12, INK, "middle", "bold")
    save("fig-21-3-1-linker-overview.svg", s)


# ── Рис. 21.3.2 — таблиця символів ───────────────────────────────────────────
def fig32_symbols():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 34, "Таблиця символів: що файл визначає й що потребує", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "кожен .o — і постачальник одних імен, і прохач інших", 12.5, GREY, "middle", style="italic")
    s += rect(260, 96, 360, 214, "#0f1b14", "#0a120d", 1.6, 10)
    s += text(440, 126, "blink.o", 14, "#eaf6ee", "middle", "bold")
    s += line(280, 140, 600, 140, "#2b3540", 1)
    s += text(360, 168, "визначає (дає):", 11, "#8fcf9f", "middle", "bold")
    s += rect(310, 182, 100, 40, "#13351f", "#1f8a3b", 1.4, 6)
    s += text(360, 207, "blink", 13, "#9be8b0", "middle", "bold")
    s += text(520, 168, "потребує (кличе):", 11, "#e0a0a0", "middle", "bold")
    s += rect(456, 182, 124, 40, "#351313", "#c0271e", 1.4, 6)
    s += text(518, 207, "digitalWrite", 11, "#f0b0b0", "middle", "bold")
    s += text(518, 250, "↑ це «дірка»:", 10, "#e0a0a0", "middle", "bold")
    s += text(518, 266, "коду нема, лише виклик", 9.5, GREY, "middle")
    s += text(440, 344, "Лінкер мусить знайти, ХТО дасть кожне «потребує».", 12, INK, "middle", "bold")
    save("fig-21-3-2-symbols.svg", s)


# ── Рис. 21.3.3 — розв'язання символів ───────────────────────────────────────
def fig33_resolution():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "Розв'язання символів: з'єднати кожне «потребує» з «визначає»", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "знайшов на кожне «треба» своє «є» — програма зшита", 12.5, GREY, "middle", style="italic")
    s += text(180, 100, "ПОТРЕБУЄ", 12, RED, "middle", "bold")
    needs = [("main → blink", 148), ("main → digitalWrite", 206), ("blink → digitalWrite", 264)]
    for lbl, y in needs:
        s += rect(56, y - 18, 250, 36, "#351313", RED, 1.4, 6)
        s += text(181, y + 5, lbl, 11.5, "#f0b0b0", "middle", "bold")
    s += text(720, 100, "ВИЗНАЧАЄ", 12, GREEN, "middle", "bold")
    defs = [("blink   (у blink.o)", 148), ("digitalWrite  (у libArduino)", 232)]
    for lbl, y in defs:
        s += rect(556, y - 18, 308, 36, "#13351f", GREEN, 1.4, 6)
        s += text(710, y + 5, lbl, 11, "#9be8b0", "middle", "bold")
    s += arrow(308, 148, 554, 148, GOLD, 2.2)
    s += arrow(308, 206, 554, 232, GOLD, 2.2)
    s += arrow(308, 264, 554, 232, GOLD, 2.2)
    s += text(460, 306, "усі стрілки знайшли мету → програма зшита ✓", 12, GREEN, "middle", "bold")
    s += rect(110, 338, 700, 72, "#fdeded", RED, 1.4, 10)
    s += text(460, 362, "«потребує» без пари  →  undefined reference (забули файл/бібліотеку)", 11.5, RED, "middle", "bold")
    s += text(460, 388, "двоє визначають те саме  →  multiple definition", 11.5, RED, "middle", "bold")
    save("fig-21-3-3-resolution.svg", s)


# ── Рис. 21.3.4 — бібліотека як склад ────────────────────────────────────────
def fig34_libraries():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "Бібліотека — склад готового коду; лінкер бере лише потрібне", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "архів наперед скомпільованих об'єктних файлів", 12.5, GREY, "middle", style="italic")
    s += rect(60, 100, 360, 256, "#efe7d2", "#b79a5e", 2, 10)
    s += text(240, 124, "libArduino (архів готових .o)", 12, "#8a6a14", "middle", "bold")
    tiles = ["digitalWrite", "pinMode", "Serial", "analogRead", "millis", "delay", "map", "tone"]
    for i, t in enumerate(tiles):
        r, c = divmod(i, 2)
        x = 78 + c * 172
        y = 144 + r * 50
        hot = (t == "digitalWrite")
        s += rect(x, y, 160, 40, "#13351f" if hot else "#fff7e6", "#1f8a3b" if hot else "#caa24a", 2 if hot else 1.2, 6)
        s += text(x + 80, y + 25, t, 11, ("#9be8b0" if hot else INK), "middle", "bold" if hot else "normal")
    s += rect(560, 178, 200, 96, LAMB, GOLD, 2.4, 12)
    s += text(660, 212, "Лінкер", 14, "#8a6a14", "middle", "bold")
    s += text(660, 236, "потребує digitalWrite", 9.5, GREY, "middle")
    s += text(660, 256, "→ тягне лише її", 9.5, GREEN, "middle", "bold")
    s += arrow(242, 164, 558, 214, GREEN, 2.6)
    s += text(420, 168, "бере ЛИШЕ потрібне", 10.5, GREEN, "middle", "bold")
    s += text(460, 396, "До прошивки входить тільки використане — не весь архів.", 12, INK, "middle", "bold")
    save("fig-21-3-4-libraries.svg", s)


# ── Рис. 21.3.5 — розкладання по адресах ─────────────────────────────────────
def fig35_addresses():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 32, "Розкладання по адресах: лінкер кладе шматки на карту пам'яті", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "кожному фрагменту — остаточна адреса, тоді дірки заповнюються нею", 12.5, GREY, "middle", style="italic")
    cx, w = 300, 210
    s += rect(cx, 94, w, 304, "#fbfcff", INK, 2, 8)
    s += text(cx + w / 2, 114, "карта пам'яті чипа", 11.5, GREY, "middle", "bold")
    s += rect(cx + 10, 128, w - 20, 156, "#eef3ff", BLUE, 1.6, 6)
    s += text(cx + w / 2, 146, "Код (Flash)", 11, BLUE, "middle", "bold")
    for nm, addr, y in [("main", "0x4000_0100", 162), ("blink", "0x4000_0140", 202), ("digitalWrite", "0x4000_0190", 242)]:
        s += rect(cx + 24, y, w - 48, 30, "#ffffff", INK, 1.2, 4)
        s += text(cx + 34, y + 20, nm, 10.5, INK, "start", "bold")
        s += text(cx - 8, y + 20, addr, 9.5, GREY, "end")
    s += rect(cx + 10, 296, w - 20, 94, "#eef6ef", GREEN, 1.6, 6)
    s += text(cx + w / 2, 314, "Дані (RAM)", 11, GREEN, "middle", "bold")
    s += text(cx + w / 2, 344, "змінні…", 10, GREY, "middle")
    s += rect(560, 150, 300, 150, "none", FAINT, 1.6, 10)
    s += text(710, 176, "тепер дірки заповнено:", 11.5, INK, "middle", "bold")
    s += text(710, 208, "«виклик digitalWrite»", 11, GREY, "middle")
    s += text(710, 228, "↓ стає", 10, GREY, "middle")
    s += text(710, 254, "«виклик 0x4000_0190»", 12.5, GREEN, "middle", "bold")
    s += text(710, 282, "справжня адреса замість дірки", 9.5, GREY, "middle")
    s += text(450, 420, "Орієнтир — сценарій лінкування (linker script), що знає карту цього чипа.", 11.5, INK, "middle", "bold")
    save("fig-21-3-5-addresses.svg", s)


# ── Рис. 21.3.6 — лінкування на прикладі ─────────────────────────────────────
def fig36_link_trace():
    W, H = 920, 470
    s = header(W, H)
    s += text(W / 2, 32, "Лінкування на прикладі: символи розв'язано, адреси роздано", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "два ваші файли + бібліотека → один повний образ", 12.5, GREY, "middle", style="italic")
    inputs = [("main.o", "дає: main", "треба: blink, digitalWrite", 104),
              ("blink.o", "дає: blink", "треба: digitalWrite", 180),
              ("libArduino", "дає: digitalWrite, …", "(склад готового)", 256)]
    for nm, d, n, y in inputs:
        s += rect(50, y, 232, 62, "#101418", "#000000", 1.4, 8)
        s += text(64, y + 22, nm, 12, "#7fe0a0", "start", "bold")
        s += text(64, y + 40, d, 9.5, "#9be8b0", "start")
        s += text(64, y + 55, n, 9, "#e0a0a0", "start")
    s += arrow(288, 200, 362, 200, INK, 2.4)
    s += rect(372, 98, 254, 236, "none", FAINT, 1.8, 10)
    s += text(499, 122, "крок 1: розв'язати символи", 11, INK, "middle", "bold")
    for ln, y in [("main → blink ✓", 148), ("main → digitalWrite ✓", 168), ("blink → digitalWrite ✓", 188)]:
        s += text(499, y, ln, 10.5, GREEN, "middle")
    s += line(388, 206, 610, 206, FAINT, 1)
    s += text(499, 230, "крок 2: роздати адреси", 11, INK, "middle", "bold")
    for ln, y in [("main → 0x…100", 254), ("blink → 0x…140", 274), ("digitalWrite → 0x…190", 294)]:
        s += text(499, y, ln, 10, GREY, "middle")
    s += text(499, 320, "→ дірок не лишилось", 10.5, GREEN, "middle", "bold")
    s += arrow(630, 216, 704, 216, GREEN, 3)
    s += rect(712, 160, 180, 112, LGRN, GREEN, 2, 12)
    s += text(802, 200, "один повний", 12.5, GREEN, "middle", "bold")
    s += text(802, 220, "образ", 12.5, GREEN, "middle", "bold")
    s += text(802, 244, "готовий стати", 9.5, INK, "middle")
    s += text(802, 260, "прошивкою", 9.5, INK, "middle")
    s += text(460, 412, "Якби blink.o не під'єднали — «main → blink» лишилось би без пари (undefined reference).",
              11, INK, "middle", "bold")
    save("fig-21-3-6-trace.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §21.4 — Образ прошивки й секції .text/.data/.bss
# ─────────────────────────────────────────────────────────────────────────────

# ── Рис. 21.4.1 — сортуємо вміст за потребою ─────────────────────────────────
def fig41_why_sections():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Програма неоднорідна: сортуємо вміст за потребою", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "що має пережити вимкнення — у Flash; що міняється — в RAM", 12.5, GREY, "middle", style="italic")
    s += rect(60, 116, 200, 210, "none", FAINT, 2, 12)
    s += text(160, 140, "вміст програми", 12, INK, "middle", "bold")
    items = [("код (інструкції)", "ніколи не змінний", BLUE, 162),
             ("сталі / початкові", "незмінні дані", BLUE, 216),
             ("змінні", "міняються на ходу", GREEN, 270)]
    for lbl, sub, col, y in items:
        s += rect(78, y, 164, 44, "#ffffff", col, 1.6, 6)
        s += text(160, y + 19, lbl, 10.5, col, "middle", "bold")
        s += text(160, y + 35, sub, 8.5, GREY, "middle")
    s += rect(560, 104, 300, 112, "#eef3ff", BLUE, 2, 10)
    s += text(710, 132, "Flash", 14, BLUE, "middle", "bold")
    s += text(710, 156, "переживає вимкнення", 10, GREY, "middle")
    s += text(710, 182, "код + сталі дані", 11, INK, "middle", "bold")
    s += rect(560, 238, 300, 112, "#eef6ef", GREEN, 2, 10)
    s += text(710, 266, "RAM", 14, GREEN, "middle", "bold")
    s += text(710, 290, "швидка, але стирається", 10, GREY, "middle")
    s += text(710, 316, "змінні", 11, INK, "middle", "bold")
    s += arrow(244, 184, 558, 150, BLUE, 2.2)
    s += arrow(244, 238, 558, 176, BLUE, 2.2)
    s += arrow(244, 292, 558, 292, GREEN, 2.2)
    save("fig-21-4-1-why-sections.svg", s)


# ── Рис. 21.4.2 — три секції ─────────────────────────────────────────────────
def fig42_three_sections():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 34, "Три класичні секції: .text, .data, .bss", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "назви дивні, та зміст простий", 12.5, GREY, "middle", style="italic")
    cards = [
        (".text", "код (інструкції)", "int main(){…}", "Flash", "тільки читається", BLUE, 40),
        (".data", "змінні з ненульовим початком", "int x = 5;", "RAM + Flash", "значення у Flash, живе в RAM", "#b9890f", 330),
        (".bss", "нульові змінні й буфери", "int y;  int z=0;", "RAM", "у Flash — 0 байтів", GREEN, 620),
    ]
    for name, what, ex, loc, note, col, x in cards:
        s += rect(x, 98, 260, 304, "#fbfbfb", col, 2, 12)
        s += text(x + 130, 130, name, 18, col, "middle", "bold")
        s += line(x + 20, 144, x + 240, 144, col, 1.2)
        s += text(x + 130, 170, what, 10.5, INK, "middle", "bold")
        s += rect(x + 30, 188, 200, 40, "#0f1b14", "#0a120d", 1.2, 6)
        s += text(x + 130, 213, ex, 11, "#7fe0a0", "middle", "bold")
        s += text(x + 130, 264, "живе у:", 10, GREY, "middle")
        s += rect(x + 60, 274, 140, 36, "#ffffff", col, 1.6, 6)
        s += text(x + 130, 297, loc, 12, col, "middle", "bold")
        s += text(x + 130, 348, note, 9.3, GREY, "middle")
    save("fig-21-4-2-three-sections.svg", s)


# ── Рис. 21.4.3 — парадокс початкових значень ────────────────────────────────
def fig43_data_bss_twist():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "Парадокс початкових значень: RAM при старті порожня", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "то звідки береться «5» у int x = 5?", 12.5, GREY, "middle", style="italic")
    s += text(70, 118, ".data  —  int x = 5;", 13, "#8a6a14", "start", "bold")
    s += rect(60, 136, 200, 62, "#eef3ff", BLUE, 1.8, 8)
    s += text(160, 162, "Flash", 11, BLUE, "middle", "bold")
    s += text(160, 182, "тримає «5»", 10, INK, "middle")
    s += arrow(266, 167, 422, 167, GREEN, 2.6)
    s += text(344, 155, "копія при старті", 9.5, GREEN, "middle", "bold")
    s += rect(432, 136, 210, 62, "#eef6ef", GREEN, 1.8, 8)
    s += text(537, 162, "RAM (x)", 11, GREEN, "middle", "bold")
    s += text(537, 182, "= 5, далі мінятиметься", 9.5, INK, "middle")
    s += text(770, 170, "коштує і Flash, і RAM", 11, INK, "middle", "bold")
    s += text(70, 268, ".bss  —  int y;", 13, GREEN, "start", "bold")
    s += rect(60, 286, 200, 62, "#f0f0f0", GREY, 1.8, 8)
    s += text(160, 312, "Flash", 11, GREY, "middle", "bold")
    s += text(160, 332, "нічого (0 байтів)", 10, GREY, "middle")
    s += arrow(266, 317, 422, 317, GREEN, 2.6)
    s += text(344, 305, "просто обнулити", 9.5, GREEN, "middle", "bold")
    s += rect(432, 286, 210, 62, "#eef6ef", GREEN, 1.8, 8)
    s += text(537, 312, "RAM (y)", 11, GREEN, "middle", "bold")
    s += text(537, 332, "= 0", 10, INK, "middle")
    s += text(770, 320, "коштує лише RAM", 11, INK, "middle", "bold")
    s += text(460, 404, "Ініціалізована змінна має «склад» у Flash і «дім» у RAM; нульова — лише дім.", 12, INK, "middle", "bold")
    save("fig-21-4-3-data-bss-twist.svg", s)


# ── Рис. 21.4.4 — стартова копія/обнулення ───────────────────────────────────
def fig44_startup_copy():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Старт (ще до main()): копія .data у RAM, обнулення .bss", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "крихітний стартовий код готує змінним правильний початок", 12.5, GREY, "middle", style="italic")
    s += rect(120, 104, 200, 246, "#fbfcff", INK, 2, 8)
    s += text(220, 124, "Flash (образ)", 11.5, BLUE, "middle", "bold")
    s += rect(135, 138, 170, 92, "#eef3ff", BLUE, 1.4, 6)
    s += text(220, 189, ".text (код)", 11, BLUE, "middle", "bold")
    s += rect(135, 240, 170, 52, "#fff3d6", "#b9890f", 1.4, 6)
    s += text(220, 262, ".data — поч.", 9.5, "#8a6a14", "middle", "bold")
    s += text(220, 278, "значення", 9.5, "#8a6a14", "middle", "bold")
    s += rect(580, 104, 200, 246, "#fbfcff", INK, 2, 8)
    s += text(680, 124, "RAM", 11.5, GREEN, "middle", "bold")
    s += rect(595, 138, 170, 52, "#fff3d6", "#b9890f", 1.4, 6)
    s += text(680, 168, ".data (живі змінні)", 9.5, "#8a6a14", "middle", "bold")
    s += rect(595, 200, 170, 92, "#eef6ef", GREEN, 1.4, 6)
    s += text(680, 250, ".bss (нулі)", 11, GREEN, "middle", "bold")
    s += arrow(310, 262, 592, 164, GREEN, 2.6)
    s += text(450, 196, "① копіювати", 10, GREEN, "middle", "bold")
    s += text(680, 226, "② обнулити", 9.5, GREEN, "middle", "bold")
    s += text(460, 378, "Аж після цього змінні мають правильний початок — і запускається ваш код.", 11.5, INK, "middle", "bold")
    save("fig-21-4-4-startup-copy.svg", s)


# ── Рис. 21.4.5 — образ vs RAM ───────────────────────────────────────────────
def fig45_image_vs_ram():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "Образ у Flash проти вмісту RAM — це різні числа", 19, INK, "middle", "bold")
    s += text(W / 2, 54, ".bss образу не роздуває; стек і купа з'їдають RAM", 12.5, GREY, "middle", style="italic")
    s += rect(120, 96, 220, 308, "#fbfcff", INK, 2, 8)
    s += text(230, 118, "Образ у Flash (заливають)", 10.5, BLUE, "middle", "bold")
    s += rect(135, 134, 190, 150, "#eef3ff", BLUE, 1.4, 6)
    s += text(230, 213, ".text (код)", 12, BLUE, "middle", "bold")
    s += rect(135, 290, 190, 42, "#fff3d6", "#b9890f", 1.4, 6)
    s += text(230, 316, ".data (поч. значення)", 9.3, "#8a6a14", "middle", "bold")
    s += rect(135, 338, 190, 28, "#f0f0f0", GREY, 1.2, 6)
    s += text(230, 357, ".bss — лише розмір", 9, GREY, "middle")
    s += text(230, 390, "= код + поч. дані", 10, INK, "middle", "bold")
    s += rect(580, 96, 220, 308, "#fbfcff", INK, 2, 8)
    s += text(690, 118, "RAM (під час роботи)", 10.5, GREEN, "middle", "bold")
    s += rect(595, 134, 190, 36, "#fff3d6", "#b9890f", 1.4, 6)
    s += text(690, 157, ".data", 10.5, "#8a6a14", "middle", "bold")
    s += rect(595, 174, 190, 64, "#eef6ef", GREEN, 1.4, 6)
    s += text(690, 210, ".bss (обнулено)", 10.5, GREEN, "middle", "bold")
    s += rect(595, 250, 190, 44, "#fdeded", RED, 1.2, 6)
    s += text(690, 277, "стек ↓", 10.5, RED, "middle", "bold")
    s += text(690, 312, "…", 16, GREY, "middle")
    s += rect(595, 326, 190, 44, "#fdeded", RED, 1.2, 6)
    s += text(690, 353, "купа ↑", 10.5, RED, "middle", "bold")
    s += text(460, 424, "Розмір образу й витрата RAM рахують окремо.", 11.5, INK, "middle", "bold")
    save("fig-21-4-5-image-vs-ram.svg", s)


# ── Рис. 21.4.6 — звіт збірки ────────────────────────────────────────────────
def fig46_size_report():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "Звіт збірки: дві цифри з розмірів секцій", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "Flash = .text + .data;   RAM = .data + .bss (+ стек/купа)", 12.5, GREY, "middle", style="italic")
    s += text(160, 108, "секції", 12, INK, "middle", "bold")
    secs = [(".text", "180 КБ", BLUE, 130), (".data", "2 КБ", "#b9890f", 168), (".bss", "40 КБ", GREEN, 206)]
    for nm, sz, col, y in secs:
        s += rect(70, y, 180, 30, "#ffffff", col, 1.6, 6)
        s += text(96, y + 20, nm, 11, col, "start", "bold")
        s += text(232, y + 20, sz, 11, INK, "end", "bold")
    s += text(150, 254, ".data — в обидва числа!", 9.5, "#8a6a14", "middle", style="italic")
    s += rect(360, 122, 230, 86, "#eef3ff", BLUE, 2, 10)
    s += text(475, 146, "Flash (образ)", 12, BLUE, "middle", "bold")
    s += text(475, 168, ".text + .data", 10, GREY, "middle")
    s += text(475, 194, "= 182 КБ", 14, BLUE, "middle", "bold")
    s += rect(360, 238, 230, 86, "#eef6ef", GREEN, 2, 10)
    s += text(475, 262, "RAM", 12, GREEN, "middle", "bold")
    s += text(475, 284, ".data + .bss  (+стек/купа)", 9, GREY, "middle")
    s += text(475, 310, "= 42 КБ +", 14, GREEN, "middle", "bold")
    s += arrow(254, 145, 356, 162, INK, 1.8)
    s += arrow(254, 183, 356, 176, INK, 1.8)
    s += arrow(254, 183, 356, 268, INK, 1.8)
    s += arrow(254, 221, 356, 282, INK, 1.8)
    s += rect(630, 132, 250, 180, "#101418", "#000000", 1.5, 8)
    s += text(755, 160, "звіт збірки:", 10, "#7fa6bf", "middle", "bold")
    s += text(648, 196, "program storage:", 9.5, "#cfe0d6", "start")
    s += text(648, 214, "  182 KB   (Flash)", 10.5, "#7fe0a0", "start", "bold")
    s += text(648, 252, "dynamic memory:", 9.5, "#cfe0d6", "start")
    s += text(648, 270, "  42 KB   (RAM)", 10.5, "#7fe0a0", "start", "bold")
    s += text(450, 396, "«програмна пам'ять» = Flash, «динамічна» = RAM — тепер це не загадка.", 11.5, INK, "middle", "bold")
    save("fig-21-4-6-size-report.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §21.5 — Прошивка у Flash: як код потрапляє в чіп
# ─────────────────────────────────────────────────────────────────────────────

# ── Рис. 21.5.1 — шлях образу ────────────────────────────────────────────────
def fig51_the_link():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 34, "Шлях образу: ПК → USB → перетворювач → UART → чіп", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "образ їде послідовним дротом — байт за байтом", 12.5, GREY, "middle", style="italic")
    y = 180
    s += rect(40, y - 40, 150, 90, LBLUE, BLUE, 2, 10)
    s += text(115, y, "ПК", 14, BLUE, "middle", "bold")
    s += text(115, y + 22, "образ .bin", 9.5, GREY, "middle")
    s += arrow(192, y + 5, 250, y + 5, INK, 2.4)
    s += text(221, y - 8, "USB", 9.5, GREY, "middle", "bold")
    s += rect(252, y - 40, 180, 90, "#fbfbfb", INK, 1.8, 10)
    s += text(342, y, "перетворювач", 12, INK, "middle", "bold")
    s += text(342, y + 22, "USB ↔ UART", 9.5, GREY, "middle")
    s += arrow(434, y + 5, 492, y + 5, INK, 2.4)
    s += text(463, y - 8, "TX/RX", 9, GREY, "middle", "bold")
    s += rect(494, y - 46, 210, 102, "#fbfcff", INK, 2, 10)
    s += text(599, y - 24, "Мікроконтролер", 12, INK, "middle", "bold")
    s += rect(510, y - 4, 178, 50, "#eef3ff", BLUE, 1.4, 6)
    s += text(599, y + 26, "Flash (сюди ляже образ)", 9.5, BLUE, "middle", "bold")
    s += rect(120, 300, 680, 46, LGRN, GREEN, 1.4, 10)
    s += text(460, 320, "Новіші чипи (S3, C3…) мають ВЛАСНИЙ USB — перетворювач зайвий,", 11, INK, "middle", "bold")
    s += text(460, 338, "і чіп під'єднується до ПК прямо.", 11, INK, "middle")
    save("fig-21-5-1-the-link.svg", s)


# ── Рис. 21.5.2 — два режими ─────────────────────────────────────────────────
def fig52_run_vs_flash_mode():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Два режими чипа: біжить чи слухає", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "щоб прошитися, чіп має завмерти й слухати лінію", 12.5, GREY, "middle", style="italic")
    s += rect(50, 88, 360, 212, "none", FAINT, 2, 12)
    s += text(230, 114, "Звичайний режим", 14, GREEN, "middle", "bold")
    s += rect(120, 148, 220, 82, LGRN, GREEN, 2, 10)
    s += text(230, 182, "ВИКОНУЄ", 14, GREEN, "middle", "bold")
    s += text(230, 204, "вашу програму", 10, INK, "middle")
    s += text(230, 272, "після ввімкнення — одразу біжить", 10, GREY, "middle", style="italic")
    s += rect(490, 88, 360, 212, "none", FAINT, 2, 12)
    s += text(670, 114, "Режим прошивки", 14, BLUE, "middle", "bold")
    s += rect(560, 148, 220, 82, LBLUE, BLUE, 2, 10)
    s += text(670, 182, "СЛУХАЄ", 14, BLUE, "middle", "bold")
    s += text(670, 204, "лінію, чекає команд запису", 9.3, INK, "middle")
    s += text(670, 272, "завмер і чекає, що скаже ПК", 10, GREY, "middle", style="italic")
    s += rect(140, 328, 620, 60, LAMB, GOLD, 1.6, 10)
    s += text(450, 352, "Перемикає: скидання + затиснута завантажувальна ніжка (GPIO0)", 11.5, INK, "middle", "bold")
    s += text(450, 374, "— і робить це автоматично плата, а не ваші руки.", 11, GREY, "middle")
    save("fig-21-5-2-run-vs-flash-mode.svg", s)


# ── Рис. 21.5.3 — ROM-завантажувач ───────────────────────────────────────────
def fig53_rom_bootloader():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Чіп прошиває сам себе: ROM-завантажувач", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "ПК лише диктує — внутрішній загрузчик пише Flash", 12.5, GREY, "middle", style="italic")
    s += rect(40, 150, 140, 84, LBLUE, BLUE, 2, 10)
    s += text(110, 186, "ПК", 13, BLUE, "middle", "bold")
    s += text(110, 208, "диктує байти", 9.5, GREY, "middle")
    s += arrow(182, 192, 252, 192, INK, 2.6)
    s += text(217, 180, "дріт", 9, GREY, "middle")
    s += rect(262, 110, 420, 204, "#fbfcff", INK, 2.2, 12)
    s += text(472, 134, "Мікроконтролер", 12, GREY, "middle", "bold")
    s += rect(285, 156, 184, 84, LAMB, GOLD, 2, 10)
    s += text(377, 190, "ROM-завантажувач", 11, "#8a6a14", "middle", "bold")
    s += text(377, 210, "(заводський, незмінний)", 8.5, GREY, "middle")
    s += arrow(471, 198, 542, 198, GREEN, 2.6)
    s += text(507, 186, "пише", 9.5, GREEN, "middle", "bold")
    s += rect(548, 156, 120, 84, "#eef3ff", BLUE, 2, 10)
    s += text(608, 192, "Flash", 13, BLUE, "middle", "bold")
    s += text(608, 212, "образ", 9.5, GREY, "middle")
    s += text(450, 350, "ПК не пише в чіп напряму — диктує; загрузчик пише Flash сам.", 11.5, INK, "middle", "bold")
    s += text(450, 372, "ROM незнищенний → чіп ніколи не «закам'яніє».", 10.5, GREY, "middle")
    save("fig-21-5-3-rom-bootloader.svg", s)


# ── Рис. 21.5.4 — протокол прошивки ──────────────────────────────────────────
def fig54_protocol():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 32, "Протокол прошивки: стерти → блоки з перевіркою → звірити", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "розмова ПК із ROM-завантажувачем", 12.5, GREY, "middle", style="italic")
    steps = [("1. Стерти", "флеш пишеться лише", "по чистому місцю", RED, 70),
             ("2. Передати блоки", "порціями, до кожної —", "контрольна сума", BLUE, 350),
             ("3. Звірити", "чи лягло саме те,", "що слали", GREEN, 630)]
    for t, l1, l2, col, x in steps:
        s += rect(x, 100, 230, 140, "#fbfbfb", col, 2, 12)
        s += text(x + 115, 130, t, 13, col, "middle", "bold")
        s += line(x + 20, 142, x + 210, 142, col, 1.2)
        s += text(x + 115, 172, l1, 10.5, INK, "middle")
        s += text(x + 115, 192, l2, 10.5, INK, "middle")
        if x < 630:
            s += arrow(x + 234, 170, x + 346, 170, INK, 2.6)
    s += rect(160, 296, 600, 58, "#13202a", "#0a141b", 1.4, 8)
    s += text(186, 330, "блок даних", 11, "#7fe0a0", "start", "bold")
    s += rect(560, 308, 184, 36, "#351313", RED, 1.4, 6)
    s += text(652, 332, "контр. сума", 10, "#f0b0b0", "middle", "bold")
    s += text(460, 392, "Дріт неідеальний — тому кожен блок перевіряють контрольною сумою.", 11.5, INK, "middle", "bold")
    save("fig-21-5-4-protocol.svg", s)


# ── Рис. 21.5.5 — повний цикл Upload ─────────────────────────────────────────
def fig55_upload_sequence():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 34, "Натиснув «Upload» — що сталося за кадром", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "усе — за кілька секунд, без жодної вашої кнопки", 12.5, GREY, "middle", style="italic")
    steps = [("1", "скидання", "→ режим прошивки", GOLD),
             ("2", "ROM-загрузчик", "слухає лінію", BLUE),
             ("3", "стерти", "ділянку Flash", RED),
             ("4", "передати блоки", "загрузчик пише", BLUE),
             ("5", "звірити", "контр. суми", GREEN),
             ("6", "скинути", "→ біжить НОВЕ", GOLD)]
    x0, w, gap, y = 24, 140, 12, 150
    for i, (n, t1, t2, col) in enumerate(steps):
        x = x0 + i * (w + gap)
        s += rect(x, y, w, 92, "#fbfbfb", col, 2, 10)
        s += circle(x + 20, y + 20, 12, "#ffffff", col, 2)
        s += text(x + 20, y + 24, n, 12, col, "middle", "bold")
        s += text(x + w / 2 + 8, y + 50, t1, 11, col, "middle", "bold")
        s += text(x + w / 2, y + 70, t2, 9, GREY, "middle")
        if i < len(steps) - 1:
            s += arrow(x + w, y + 46, x + w + gap + 1, y + 46, INK, 2.2)
    s += text(W / 2, 300, "«Upload» = скидання → слухати → стерти → записати з перевіркою → скинути → бігти.",
              12, INK, "middle", "bold")
    save("fig-21-5-5-upload-sequence.svg", s)


# ── Рис. 21.5.6 — час передачі від швидкості ─────────────────────────────────
def fig56_transfer_time():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Скільки триває заливання: розмір ÷ швидкість", 19, INK, "middle", "bold")
    s += text(W / 2, 58, "образ 182 КБ ≈ 186 000 байтів · ~10 бітів на байт", 12, GREY, "middle", style="italic")
    s += text(250, 96, "швидкість", 11, INK, "middle", "bold")
    s += text(640, 96, "час заливання", 11, INK, "middle", "bold")
    rows = [("460800 бод", "46 080 байтів/с", "≈ 4 с", 120, GREEN, LGRN, 150),
            ("115200 бод", "11 520 байтів/с", "≈ 16 с", 480, RED, LRED, 240)]
    for baud, thru, t, barw, col, fill, y in rows:
        s += text(60, y + 4, baud, 12.5, INK, "start", "bold")
        s += text(60, y + 22, thru, 9.5, GREY, "start")
        s += rect(200, y - 14, barw, 40, fill, col, 1.8, 6)
        s += text(200 + barw + 12, y + 10, t, 15, col, "start", "bold")
    s += rect(120, 320, 660, 56, LAMB, GOLD, 1.4, 10)
    s += text(450, 344, "Швидкість задирають якомога вище — прошивка летить, а не повзе.", 11.5, INK, "middle", "bold")
    s += text(450, 364, "(завелику дріт не тягне — спотворення, доводиться відступати)", 10, GREY, "middle", style="italic")
    save("fig-21-5-6-transfer-time.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §21.6 — Завантажувач і reset-послідовність
# ─────────────────────────────────────────────────────────────────────────────

# ── Рис. 21.6.1 — скидання ───────────────────────────────────────────────────
def fig61_reset():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Скидання: ядро у відомий стан, старт із вектора скидання", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "чіп знає лише, ЗВІДКИ почати", 12.5, GREY, "middle", style="italic")
    s += rect(50, 150, 150, 84, LRED, RED, 2, 10)
    s += text(125, 184, "Живлення / RESET", 10.5, RED, "middle", "bold")
    s += text(125, 206, "стартовий постріл", 9, GREY, "middle")
    s += arrow(202, 192, 270, 192, INK, 2.6)
    s += rect(280, 150, 200, 84, "#fbfcff", INK, 2, 10)
    s += text(380, 182, "Ядро", 13, INK, "middle", "bold")
    s += text(380, 206, "примусово у відомий стан", 9, GREY, "middle")
    s += arrow(482, 192, 550, 192, INK, 2.6)
    s += text(516, 180, "старт із", 8.5, GREY, "middle")
    s += rect(560, 150, 300, 100, "#eef3ff", BLUE, 2, 10)
    s += text(710, 178, "вектор скидання", 12, BLUE, "middle", "bold")
    s += text(710, 200, "одна фіксована адреса —", 9.5, INK, "middle")
    s += text(710, 216, "там перша сходинка", 9.5, INK, "middle")
    s += text(450, 322, "Усе подальше — ланцюжок передавання естафети від цієї точки.", 12, INK, "middle", "bold")
    save("fig-21-6-1-reset.svg", s)


# ── Рис. 21.6.2 — робота завантажувача ───────────────────────────────────────
def fig62_bootloader_job():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Завантажувач: розпорядник, що обирає й запускає", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "сам нічого корисного не робить — він ЗАПУСКАЄ інших", 12.5, GREY, "middle", style="italic")
    s += rect(40, 162, 150, 70, "#eef3ff", BLUE, 1.8, 10)
    s += text(115, 194, "вектор скидання", 10.5, BLUE, "middle", "bold")
    s += text(115, 214, "→ сюди", 9, GREY, "middle")
    s += arrow(192, 197, 260, 197, INK, 2.6)
    s += rect(270, 140, 260, 116, LAMB, GOLD, 2.4, 12)
    s += text(400, 168, "Завантажувач", 14, "#8a6a14", "middle", "bold")
    for i, t in enumerate(["• вирішує, ЩО запускати", "• готує найнеобхідніше", "• передає естафету далі"]):
        s += text(292, 196 + i * 22, t, 9.8, INK, "start")
    s += arrow(532, 197, 600, 197, GREEN, 2.6)
    s += text(566, 185, "запуск", 9, GREEN, "middle", "bold")
    s += rect(610, 162, 240, 70, LGRN, GREEN, 1.8, 10)
    s += text(730, 190, "обрана програма", 12, GREEN, "middle", "bold")
    s += text(730, 212, "(ваш застосунок)", 9.5, GREY, "middle")
    s += text(450, 332, "За вектором скидання — не ваш код, а маленький розпорядник.", 12, INK, "middle", "bold")
    save("fig-21-6-2-bootloader-job.svg", s)


# ── Рис. 21.6.3 — два щаблі завантаження ─────────────────────────────────────
def fig63_two_stage():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Два щаблі завантаження на ESP32", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "ROM → завантажувач у Flash → ваш застосунок", 12.5, GREY, "middle", style="italic")
    s += rect(30, 168, 120, 74, LRED, RED, 1.8, 10)
    s += text(90, 204, "Скидання", 12, RED, "middle", "bold")
    s += arrow(152, 205, 212, 205, INK, 2.4)
    s += rect(222, 148, 212, 114, "#fbfcff", GOLD, 2.2, 12)
    s += text(328, 174, "1-й: ROM-загрузчик", 11, "#8a6a14", "middle", "bold")
    s += text(328, 198, "GPIO0? — прошивка", 9.3, INK, "middle")
    s += text(328, 216, "ні → звичайний запуск", 9.3, INK, "middle")
    s += text(328, 238, "дістає з Flash наступного", 8.3, GREY, "middle")
    s += arrow(436, 205, 496, 205, INK, 2.4)
    s += rect(506, 148, 232, 114, "#fbfcff", GOLD, 2.2, 12)
    s += text(622, 174, "2-й: загрузчик у Flash", 10.3, "#8a6a14", "middle", "bold")
    s += text(622, 198, "таблиця розділів", 9.3, INK, "middle")
    s += text(622, 216, "PLL → робоча частота", 9.3, INK, "middle")
    s += text(622, 238, "знайти застосунок", 9.3, INK, "middle")
    s += arrow(740, 205, 800, 205, GREEN, 2.4)
    s += rect(810, 168, 120, 74, LGRN, GREEN, 1.8, 10)
    s += text(870, 198, "ваш", 12, GREEN, "middle", "bold")
    s += text(870, 220, "застосунок", 11, GREEN, "middle", "bold")
    s += text(470, 342, "Естафету передано — далі ваш образ (а в ньому — C-стартап).", 12, INK, "middle", "bold")
    save("fig-21-6-3-two-stage.svg", s)


# ── Рис. 21.6.4 — C-стартап ──────────────────────────────────────────────────
def fig64_c_startup():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "C-стартап: підготувати пам'ять перед main()", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "поки змінні не готові — покладатися на них не можна", 12.5, GREY, "middle", style="italic")
    s += rect(40, 168, 132, 74, LGRN, GREEN, 1.8, 10)
    s += text(106, 198, "ваш образ", 11.5, GREEN, "middle", "bold")
    s += text(106, 220, "(дістав керування)", 8, GREY, "middle")
    s += arrow(174, 205, 232, 205, INK, 2.4)
    s += rect(242, 128, 384, 154, LAMB, GOLD, 2.2, 12)
    s += text(434, 154, "C-стартап (crt0)", 13, "#8a6a14", "middle", "bold")
    for i, t in enumerate(["①  копіювати .data:  Flash → RAM", "②  обнулити .bss", "③  поставити вказівник стека", "④  дрібні апаратні приготування"]):
        s += text(264, 184 + i * 23, t, 10, INK, "start")
    s += arrow(628, 205, 686, 205, GREEN, 2.6)
    s += text(657, 193, "тоді", 8.5, GREEN, "middle", "bold")
    s += rect(696, 168, 174, 74, LGRN, GREEN, 1.8, 10)
    s += text(783, 196, "виклик", 12, GREEN, "middle", "bold")
    s += text(783, 216, "точки входу", 11, GREEN, "middle", "bold")
    s += text(450, 344, "До цього кроку глобальні змінні — сміття.", 11.5, INK, "middle", "bold")
    save("fig-21-6-4-c-startup.svg", s)


# ── Рис. 21.6.5 — повна reset-послідовність ──────────────────────────────────
def fig65_full_chain():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 34, "Уся reset-послідовність: від скидання до loop()", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "кожна ланка готує наступну; жодна не «диво»", 12.5, GREY, "middle", style="italic")
    steps = [("Скидання", "вектор", RED), ("ROM-загр.", "прошивка? ні", GOLD),
             ("Загр. у Flash", "розділи, такт", GOLD), ("C-стартап", ".data/.bss/стек", BLUE),
             ("main()", "фреймворку", INK), ("setup()", "раз", GREEN), ("loop()", "вічно", GREEN)]
    x0, w, gap, y = 18, 124, 8, 160
    for i, (t1, t2, col) in enumerate(steps):
        x = x0 + i * (w + gap)
        s += rect(x, y, w, 82, "#fbfbfb", col, 2, 10)
        s += text(x + w / 2, y + 36, t1, 11, col, "middle", "bold")
        s += text(x + w / 2, y + 56, t2, 8.3, GREY, "middle")
        if i < len(steps) - 1:
            s += arrow(x + w, y + 41, x + w + gap + 1, y + 41, INK, 2)
    s += text(W / 2, 304, "Від скидання до вашого коду — чіткий ланцюг помічників, кожен зі своїм кроком.",
              12, INK, "middle", "bold")
    save("fig-21-6-5-full-chain.svg", s)


# ── Рис. 21.6.6 — де ваші setup()/loop() ─────────────────────────────────────
def fig66_setup_loop():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Де насправді ваші setup() і loop()", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "ваш код — начинка прихованого main() фреймворку", 12.5, GREY, "middle", style="italic")
    s += rect(110, 96, 680, 248, "#fbfcff", INK, 2.2, 14)
    s += text(450, 124, "main()  —  надає ФРЕЙМВОРК (прихований від вас)", 13, INK, "middle", "bold")
    s += rect(150, 150, 180, 64, "#f3f3f3", GREY, 1.6, 8)
    s += text(240, 182, "приготування", 11, INK, "middle", "bold")
    s += text(240, 200, "(фреймворк)", 8.5, GREY, "middle")
    s += arrow(332, 182, 378, 182, INK, 2.2)
    s += rect(388, 150, 150, 64, LGRN, GREEN, 2, 8)
    s += text(463, 180, "setup()", 13, GREEN, "middle", "bold")
    s += text(463, 200, "раз", 9, INK, "middle")
    s += arrow(540, 182, 586, 182, INK, 2.2)
    s += rect(596, 150, 150, 64, LGRN, GREEN, 2, 8)
    s += text(671, 180, "loop()", 13, GREEN, "middle", "bold")
    s += text(671, 200, "вічно", 9, INK, "middle")
    s += line(746, 182, 770, 182, GREEN, 2)
    s += line(770, 182, 770, 250, GREEN, 2)
    s += line(770, 250, 671, 250, GREEN, 2)
    s += arrow(671, 250, 671, 216, GREEN, 2)
    s += text(560, 282, "↻ loop() повторюється без кінця", 10, GREEN, "middle", "bold")
    s += text(467, 232, "← ВАШ код", 10.5, GREEN, "middle", "bold")
    s += text(450, 372, "Навіть «початок програми» — на щабель вищий, ніж здається (деталі — §21.7).", 11.5, INK, "middle", "bold")
    save("fig-21-6-6-setup-loop.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §21.7 — «Голе залізо» vs фреймворк
# ─────────────────────────────────────────────────────────────────────────────

# ── Рис. 21.7.1 — два способи ────────────────────────────────────────────────
def fig71_two_ways():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Та сама дія — дві дороги до регістра", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "різниця в тому, ХТО складає запис: ви чи бібліотека", 12.5, GREY, "middle", style="italic")
    s += rect(40, 86, 360, 116, "none", FAINT, 2, 12)
    s += text(220, 110, "Голе залізо", 13.5, RED, "middle", "bold")
    s += rect(70, 126, 300, 44, "#0f1b14", "#0a120d", 1.4, 8)
    s += text(220, 154, "GPIO_OUT |= (1 << 2);", 13, "#eaf6ee", "middle", "bold")
    s += text(220, 190, "ви самі складаєте запис", 9.5, GREY, "middle")
    s += rect(40, 232, 360, 116, "none", LGRN, 2, 12)
    s += text(220, 256, "Фреймворк", 13.5, GREEN, "middle", "bold")
    s += rect(70, 272, 300, 44, "#0f1b14", "#0a120d", 1.4, 8)
    s += text(220, 300, "digitalWrite(2, HIGH);", 13, "#7fe0a0", "middle", "bold")
    s += text(220, 336, "бібліотека складе запис за вас", 9.5, GREY, "middle")
    s += arrow(404, 150, 524, 208, INK, 2.4)
    s += arrow(404, 298, 524, 248, INK, 2.4)
    s += rect(534, 186, 330, 84, "#eef3ff", BLUE, 2, 10)
    s += text(699, 214, "один і той самий", 11, INK, "middle")
    s += text(699, 234, "запис у РЕГІСТР", 13, BLUE, "middle", "bold")
    s += text(699, 256, "→ ніжка перемикається", 9.5, GREY, "middle")
    save("fig-21-7-1-two-ways.svg", s)


# ── Рис. 21.7.2 — шари абстракції ────────────────────────────────────────────
def fig72_layers():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 32, "Шари абстракції: ваш код → фреймворк → регістри → залізо", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "кожен шар ховає складність нижчого", 12.5, GREY, "middle", style="italic")
    layers = [("Ваш код", "digitalWrite(2, HIGH)", LGRN, GREEN, 110),
              ("Фреймворк (Arduino / ESP-IDF)", "перекладає виклик на регістри", LAMB, GOLD, 182),
              ("Регістри (§20.3)", "GPIO_OUT |= (1<<2)", LBLUE, BLUE, 254),
              ("Залізо: ніжка", "напруга на виводі", "#f0f0f0", INK, 326)]
    for nm, sub, fill, col, y in layers:
        s += rect(232, y, 440, 56, fill, col, 2, 8)
        s += text(452, y + 24, nm, 12.5, col, "middle", "bold")
        s += text(452, y + 42, sub, 9.5, GREY, "middle")
    for y in (166, 238, 310):
        s += arrow(452, y, 452, y + 14, INK, 2.2)
    s += line(232, 138, 150, 138, RED, 2, dash="4,3")
    s += line(150, 138, 150, 282, RED, 2, dash="4,3")
    s += arrow(150, 282, 230, 282, RED, 2.2, dash="4,3")
    s += text(108, 206, "голе", 10.5, RED, "middle", "bold")
    s += text(108, 222, "залізо", 10.5, RED, "middle", "bold")
    s += text(108, 240, "(без шару)", 8.5, GREY, "middle")
    s += text(450, 408, "Голе залізо = прибрати середній шар і писати в регістри самому.", 11.5, INK, "middle", "bold")
    save("fig-21-7-2-layers.svg", s)


# ── Рис. 21.7.3 — дає і бере ──────────────────────────────────────────────────
def fig73_buys_costs():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 32, "Будь-яка абстракція щось дає і щось бере", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "інженерія — свідомо зважувати цю торгівлю", 12.5, GREY, "middle", style="italic")
    s += rect(40, 92, 400, 256, "none", LGRN, 2, 12)
    s += text(240, 122, "ДАЄ", 16, GREEN, "middle", "bold")
    for i, t in enumerate(["читабельність (ясний намір)", "швидкість розробки", "переносність (різні чипи)", "менше помилок (уже налагоджено)"]):
        s += text(64, 162 + i * 44, "✓  " + t, 11.5, INK, "start")
    s += rect(480, 92, 400, 256, "none", LRED, 2, 12)
    s += text(680, 122, "БЕРЕ", 16, RED, "middle", "bold")
    for i, t in enumerate(["накладні витрати (виклик довший)", "трохи більший розмір", "менше контролю", "віддаль від «правди» заліза"]):
        s += text(504, 162 + i * 44, "✗  " + t, 11.5, INK, "start")
    s += text(460, 240, "⚖", 34, "#8a6a14", "middle", "bold")
    s += text(460, 388, "Не «уникати» абстракцій — а зважувати під кожну задачу.", 11.5, INK, "middle", "bold")
    save("fig-21-7-3-buys-costs.svg", s)


# ── Рис. 21.7.4 — коли що ─────────────────────────────────────────────────────
def fig74_when_which():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "Фреймворк за замовчуванням, голе залізо — точково", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "і це не «або-або» — їх змішують", 12.5, GREY, "middle", style="italic")
    s += rect(40, 92, 500, 268, LGRN, GREEN, 2, 12)
    s += text(290, 122, "Фреймворк — за замовчуванням", 14, GREEN, "middle", "bold")
    s += text(290, 148, "швидко · надійно · переносно", 10.5, INK, "middle")
    s += text(290, 178, "≈ 99 % коду", 17, GREEN, "middle", "bold")
    s += rect(110, 206, 360, 134, "#fdeded", RED, 2, 10)
    s += text(290, 230, "Голе залізо — точково", 12.5, RED, "middle", "bold")
    for i, t in enumerate(["• гранична швидкість (гарячий цикл)", "• тонкий контроль (нема в обгортці)", "• мінімальний розмір", "• зрозуміти / відлагодити"]):
        s += text(150, 256 + i * 20, t, 9.8, INK, "start")
    s += rect(570, 138, 300, 184, "none", FAINT, 1.6, 10)
    s += text(720, 166, "Не «або-або»:", 12, INK, "middle", "bold")
    s += text(720, 192, "здебільшого фреймворк,", 10.5, INK, "middle")
    s += text(720, 212, "а в гарячих місцях —", 10.5, INK, "middle")
    s += text(720, 230, "прямий доступ до регістрів.", 10.5, INK, "middle")
    s += text(720, 268, "Так роблять і профі.", 10.5, GREEN, "middle", "bold")
    save("fig-21-7-4-when-which.svg", s)


# ── Рис. 21.7.5 — Arduino vs ESP-IDF ─────────────────────────────────────────
def fig75_arduino_idf():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Фреймворки на шкалі: від тонкого Arduino до повносилого ESP-IDF", 17.5, INK, "middle", "bold")
    axisY = 210
    s += line(120, axisY, 780, axisY, INK, 2.6)
    s += arrow(770, axisY, 806, axisY, INK, 2.6)
    s += text(130, axisY + 66, "тонше, дружніше", 10.5, GREY, "start")
    s += text(800, axisY + 66, "потужніше, офіційніше", 10.5, GREY, "end")
    s += rect(120, axisY - 92, 250, 78, LGRN, GREEN, 2, 10)
    s += text(245, axisY - 68, "Arduino", 13.5, GREEN, "middle", "bold")
    s += text(245, axisY - 48, "setup()/loop(), гори прикладів", 8.7, INK, "middle")
    s += text(245, axisY - 30, "навчання · прототипи · «стеля»", 8.5, GREY, "middle")
    s += line(245, axisY - 14, 245, axisY - 8, GREEN, 1.4)
    s += circle(245, axisY, 9, "#ffffff", GREEN, 3)
    s += rect(520, axisY - 92, 260, 78, LBLUE, BLUE, 2, 10)
    s += text(650, axisY - 68, "ESP-IDF", 13.5, BLUE, "middle", "bold")
    s += text(650, axisY - 48, "офіційний, усі можливості", 8.7, INK, "middle")
    s += text(650, axisY - 30, "на ОС реального часу · крутіший", 8.5, GREY, "middle")
    s += line(650, axisY - 14, 650, axisY - 8, BLUE, 1.4)
    s += circle(650, axisY, 9, "#ffffff", BLUE, 3)
    s += rect(150, axisY + 28, 600, 32, LAMB, GOLD, 1.4, 8)
    s += text(450, axisY + 49, "Arduino збудовано ПОВЕРХ IDF — не суперники, а рівні тієї самої драбини.", 11, INK, "middle", "bold")
    save("fig-21-7-5-arduino-idf.svg", s)


# ── Рис. 21.7.6 — ціна в тактах ──────────────────────────────────────────────
def fig76_two_ways_cost():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Ціна зручності в тактах (на 240 МГц: 1 такт ≈ 4 нс)", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "різниця велика у разах, та крихітна в часі", 12.5, GREY, "middle", style="italic")
    rows = [("digitalWrite(2, HIGH)", "перевірки + запис", "≈ 40 тактів ≈ 0.17 мкс", 360, GREEN, LGRN, 150),
            ("GPIO_OUT |= (1<<2)", "один запис", "≈ 2 такти ≈ 0.008 мкс", 30, RED, LRED, 240)]
    for code, what, res, barw, col, fill, y in rows:
        s += text(60, y, code, 12, col, "start", "bold")
        s += text(60, y + 18, what, 9, GREY, "start")
        s += rect(360, y - 16, barw, 36, fill, col, 1.8, 6)
        s += text(360 + barw + 12, y + 8, res, 12, col, "start", "bold")
    s += rect(110, 308, 680, 74, LAMB, GOLD, 1.4, 10)
    s += text(450, 332, "Різниця у ~10–50 разів! Та для звичайної дії — частки мікросекунди,", 11.5, INK, "middle", "bold")
    s += text(450, 354, "яких НІХТО не помітить. Важить лише в гарячому циклі (мільйони/с).", 11.5, INK, "middle", "bold")
    s += text(450, 374, "Тому: довіряй абстракції, але знай, де й чому від неї відмовитись.", 10, GREY, "middle", style="italic")
    save("fig-21-7-6-two-ways-cost.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §21.8 — Відлагодження: Serial, JTAG/SWD
# ─────────────────────────────────────────────────────────────────────────────

# ── Рис. 21.8.1 — чому на МК сліпо ───────────────────────────────────────────
def fig81_why_special():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Чому на МК відлагоджувати сліпо", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "код біжить не на вашій машині, а на окремому чипі", 12.5, GREY, "middle", style="italic")
    s += rect(40, 90, 360, 250, "none", LGRN, 2, 12)
    s += text(220, 116, "На ПК", 14, GREEN, "middle", "bold")
    s += text(220, 140, "програма біжить на вашій же машині", 9.3, INK, "middle")
    for i, t in enumerate(["✓ спинити на паузу", "✓ зазирнути в будь-яку змінну", "✓ пройти код по рядку"]):
        s += text(78, 174 + i * 32, t, 11.5, GREEN, "start", "bold")
    s += text(220, 294, "видно все, як на долоні", 10, GREY, "middle", style="italic")
    s += rect(480, 90, 360, 250, "none", LRED, 2, 12)
    s += text(660, 116, "На МК", 14, RED, "middle", "bold")
    s += text(660, 140, "код біжить на окремому запечатаному чипі", 8.7, INK, "middle")
    for i, t in enumerate(["✗ зсередини не видно", "✗ впав — мовчить або скидається", "✗ пауза / змінні недосяжні"]):
        s += text(518, 174 + i * 32, t, 11, RED, "start", "bold")
    s += text(660, 294, "сліпа коробка — треба ЗАЗИРНУТИ", 9.5, GREY, "middle", style="italic")
    s += text(450, 372, "Тому й потрібні особливі інструменти: Serial і апаратний налагоджувач.", 11.5, INK, "middle", "bold")
    save("fig-21-8-1-why-special.svg", s)


# ── Рис. 21.8.2 — Serial ─────────────────────────────────────────────────────
def fig82_serial():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Serial: розкидати «крихти» й читати їх у моніторі", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "найпростіше — і найуживаніше — відлагодження на МК", 12.5, GREY, "middle", style="italic")
    s += rect(40, 100, 360, 226, "#0f1b14", "#0a120d", 1.5, 10)
    s += text(60, 126, "ваш код", 10, "#8fcf9f", "start", "bold")
    lines = [("void loop() {", "#cfe0d6"), ("  x = read();", "#cfe0d6"),
             ("  Serial.println(x);", "#7fe0a0"), ("  if (err) Serial.println(\"err!\");", "#7fe0a0"), ("}", "#cfe0d6")]
    for i, (ln, col) in enumerate(lines):
        s += text(58, 156 + i * 30, ln, 10.5, col, "start")
    s += arrow(404, 213, 470, 213, GOLD, 2.6)
    s += text(437, 201, "дріт", 9, GREY, "middle")
    s += rect(480, 100, 380, 226, "#101418", "#000000", 1.5, 10)
    s += text(500, 126, "монітор порту (ПК)", 10, "#7fa6bf", "start", "bold")
    for i, m in enumerate(["x = 512", "x = 530", "x = 0", "err!", "x = 0", "err!"]):
        s += text(500, 156 + i * 26, "> " + m, 11.5, "#7fe0a0", "start", "bold")
    s += text(450, 368, "Без заліза, всюди — та сповільнює й показує лише те, що ви надрукували.", 11, INK, "middle", "bold")
    save("fig-21-8-2-serial.svg", s)


# ── Рис. 21.8.3 — що друкувати ───────────────────────────────────────────────
def fig83_what_to_print():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Що друкувати: значення, маркери, помилки", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "спершу гіпотеза — тоді крихта, що її перевіряє", 12.5, GREY, "middle", style="italic")
    cards = [("Значення", "перевірити припущення", "println(x);", "«я думаю, тут x=5»", BLUE, 40),
             ("Маркери проходження", "простежити потік", "println(\"тут\");", "останній = місце зависання", GREEN, 320),
             ("Помилки", "гілки, що «не мали б»", "println(\"не туди\");", "спіймати неможливе", RED, 600)]
    for t, sub, code, note, col, x in cards:
        s += rect(x, 96, 270, 234, "#fbfbfb", col, 2, 12)
        s += text(x + 135, 124, t, 12.5, col, "middle", "bold")
        s += line(x + 20, 136, x + 250, 136, col, 1.2)
        s += text(x + 135, 162, sub, 10, INK, "middle")
        s += rect(x + 24, 178, 222, 38, "#0f1b14", "#0a120d", 1.2, 6)
        s += text(x + 135, 202, code, 10.5, "#7fe0a0", "middle", "bold")
        s += text(x + 135, 250, note, 9.3, GREY, "middle")
    s += text(450, 372, "Відлагодження — наукова робота: гіпотеза → доказ → звузити коло.", 12, INK, "middle", "bold")
    save("fig-21-8-3-what-to-print.svg", s)


# ── Рис. 21.8.4 — JTAG/SWD ───────────────────────────────────────────────────
def fig84_jtag():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "JTAG/SWD: зонд дотягується всередину живого чипа", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "робить чіп прозорим, як на ПК", 12.5, GREY, "middle", style="italic")
    s += rect(40, 158, 130, 84, LBLUE, BLUE, 2, 10)
    s += text(105, 194, "ПК + зонд", 11.5, BLUE, "middle", "bold")
    s += text(105, 214, "(JTAG/SWD)", 9, GREY, "middle")
    s += arrow(172, 200, 250, 200, GOLD, 2.6)
    s += text(211, 188, "відлагодж.", 8.3, GREY, "middle")
    s += text(211, 214, "ніжки", 8.3, GREY, "middle")
    s += rect(260, 108, 420, 204, "#fbfcff", INK, 2.2, 12)
    s += text(470, 132, "живий чіп — тепер прозорий", 11, GREY, "middle", "bold")
    for i, p in enumerate(["спинити (halt)", "пройти по рядку (step)", "зазирнути в змінну / регістр", "точка зупину / сторожок на дані"]):
        s += rect(285, 150 + i * 37, 370, 30, "#eef3ff", BLUE, 1.4, 6)
        s += text(470, 170 + i * 37, p, 10.5, INK, "middle", "bold")
    s += text(450, 346, "ESP32 має JTAG на борту (у S3/C3/C6 — навіть через USB).", 11, INK, "middle", "bold")
    s += text(450, 368, "Сила велика, та й ціна: зайве залізо й налаштування.", 10, GREY, "middle")
    save("fig-21-8-4-jtag.svg", s)


# ── Рис. 21.8.5 — Serial vs JTAG ─────────────────────────────────────────────
def fig85_serial_vs_jtag():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Serial vs JTAG: за замовчуванням і для важких випадків", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "та сама мудрість, що й фреймворк vs голе залізо (§21.7)", 12.5, GREY, "middle", style="italic")
    s += rect(40, 96, 400, 252, "none", LGRN, 2, 12)
    s += text(240, 124, "Serial — за замовчуванням", 13.5, GREEN, "middle", "bold")
    s += text(240, 146, "легкий, завжди напохваті", 9.5, GREY, "middle")
    for i, t in enumerate(["перевірити значення", "простежити потік виконання", "більшість багів", "без зайвого заліза"]):
        s += text(70, 182 + i * 34, "•  " + t, 11.5, INK, "start")
    s += rect(460, 96, 400, 252, "none", LBLUE, 2, 12)
    s += text(660, 124, "JTAG/SWD — для важких", 13.5, BLUE, "middle", "bold")
    s += text(660, 146, "важка артилерія", 9.5, GREY, "middle")
    for i, t in enumerate(["чіп падає до першого друку", "баг тікає від друку (час)", "роздивитись усе нутро", "ціна: залізо + налаштування"]):
        s += text(490, 182 + i * 34, "•  " + t, 11.5, INK, "start")
    s += text(450, 376, "Більшість живуть на Serial; тягнуться до JTAG зрідка — і це нормально.", 12, INK, "middle", "bold")
    save("fig-21-8-5-serial-vs-jtag.svg", s)


# ── Рис. 21.8.6 — розшифровка аварії ─────────────────────────────────────────
def fig86_decode_crash():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 32, "Розшифровка аварії: адреси backtrace → ваш рядок коду", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "текст → адреси «туди», адреси → текст «назад» — тим самим тулчейном", 11.5, GREY, "middle", style="italic")
    s += rect(40, 100, 360, 124, "#1a0f0f", "#3a1a1a", 1.6, 10)
    s += text(60, 126, "паніка від чипа:", 10, "#e0a0a0", "start", "bold")
    s += text(58, 152, "Guru Meditation Error", 11, "#f0b0b0", "start", "bold")
    s += text(58, 176, "(LoadProhibited)", 9.5, "#cc9988", "start")
    s += text(58, 204, "Backtrace: 0x400d1a3c …", 11, "#f0c0a0", "start", "bold")
    s += text(220, 244, "числа = АДРЕСИ команд (§21.4)", 9.5, GREY, "middle", style="italic")
    s += arrow(404, 160, 470, 160, GOLD, 3)
    s += text(437, 148, "зворотно", 8.3, GREY, "middle")
    s += rect(480, 120, 200, 90, LAMB, GOLD, 2.2, 12)
    s += text(580, 150, "addr2line", 13, "#8a6a14", "middle", "bold")
    s += text(580, 172, "+ ваш .elf", 10, INK, "middle")
    s += text(580, 192, "(§21.3)", 8.5, GREY, "middle")
    s += arrow(682, 165, 750, 165, GREEN, 3)
    s += rect(760, 120, 140, 90, "#0f1b14", "#0a120d", 1.5, 10)
    s += text(830, 148, "ваш код:", 9, "#8fcf9f", "middle", "bold")
    s += text(830, 172, "sensor.cpp", 11, "#7fe0a0", "middle", "bold")
    s += text(830, 192, "рядок 42", 11, "#7fe0a0", "middle", "bold")
    s += rect(110, 300, 700, 86, LGRN, GREEN, 1.4, 10)
    s += text(460, 326, "Компілятор і лінкер зробили з тексту адреси (§21.1–21.4),", 11.5, INK, "middle", "bold")
    s += text(460, 348, "а тепер той самий тулчейн вертає адресу аварії назад у текст.", 11.5, INK, "middle", "bold")
    s += text(460, 370, "(сучасні середовища роблять це самі)", 9.5, GREY, "middle", style="italic")
    save("fig-21-8-6-decode-crash.svg", s)


if __name__ == "__main__":
    # Історія до Розділу 21 — Грейс Гоппер
    fig01_timeline()
    fig02_programming_in_numbers()
    fig03_moth_bug()
    fig04_compiler_idea()
    fig05_a0_library()
    # §21.1 Від тексту до машинного коду
    fig11_two_worlds()
    fig12_what_is_compilation()
    fig13_compiled_vs_interpreted()
    fig14_toolchain_pipeline()
    fig15_cross_compilation()
    fig16_one_line_many()
    # §21.2 Препроцесор, компілятор, асемблер
    fig21_three_stages()
    fig22_preprocessor()
    fig23_compiler()
    fig24_optimization()
    fig25_assembler()
    fig26_trace()
    # §21.3 Лінкування
    fig31_linker_overview()
    fig32_symbols()
    fig33_resolution()
    fig34_libraries()
    fig35_addresses()
    fig36_link_trace()
    # §21.4 Образ прошивки й секції
    fig41_why_sections()
    fig42_three_sections()
    fig43_data_bss_twist()
    fig44_startup_copy()
    fig45_image_vs_ram()
    fig46_size_report()
    # §21.5 Прошивка у Flash
    fig51_the_link()
    fig52_run_vs_flash_mode()
    fig53_rom_bootloader()
    fig54_protocol()
    fig55_upload_sequence()
    fig56_transfer_time()
    # §21.6 Завантажувач і reset-послідовність
    fig61_reset()
    fig62_bootloader_job()
    fig63_two_stage()
    fig64_c_startup()
    fig65_full_chain()
    fig66_setup_loop()
    # §21.7 Голе залізо vs фреймворк
    fig71_two_ways()
    fig72_layers()
    fig73_buys_costs()
    fig74_when_which()
    fig75_arduino_idf()
    fig76_two_ways_cost()
    # §21.8 Відлагодження
    fig81_why_special()
    fig82_serial()
    fig83_what_to_print()
    fig84_jtag()
    fig85_serial_vs_jtag()
    fig86_decode_crash()
    print("OK - figures for Section 21 (history + 21.1..21.8 — ПОВНИЙ розділ) generated in", OUT)
