# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 22 — «GPIO глибоко» (Модуль 4).
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


def fet(x, y, w, h, label, state="struct"):
    """Транзистор як коробка-перемикач: on (зелений), off (сірий), on_red (КЗ), struct."""
    cfg = {"on": ("#eaf6ee", GREEN, "ВІДКР"), "off": ("#f0f0f0", GREY, "закр"),
           "on_red": ("#fdeded", RED, "ВІДКР"), "struct": ("#fbfcff", INK, "")}
    fill, col, tag = cfg[state]
    o = rect(x, y, w, h, fill, col, 2.2, 5)
    o += text(x + w / 2, y + h / 2 + (-4 if tag else 5), label, 14, col, "middle", "bold")
    if tag:
        o += text(x + w / 2, y + h / 2 + 15, tag, 9, col, "middle", "bold")
    return o


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── Рис. 22.1.1 — вихід мусить тримати лінію ─────────────────────────────────
def fig11_drive_the_line():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 34, "Що означає «вихід»: активно тримати лінію до VDD або GND", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "не «показати» число, а фізично приєднати й живити напругу", 12.5, GREY, "middle", style="italic")
    cx = 410
    s += line(cx - 200, 120, cx + 60, 120, RED, 3)
    s += text(cx - 200, 112, "VDD (3.3 В)", 12, RED, "start", "bold")
    s += line(cx - 200, 340, cx + 60, 340, BLUE, 3)
    s += text(cx - 200, 362, "GND (0 В)", 12, BLUE, "start", "bold")
    s += line(cx, 120, cx, 188, GREY, 1.6, dash="3,3")
    s += line(cx, 268, cx, 340, GREY, 1.6, dash="3,3")
    s += rect(cx - 70, 188, 140, 80, "#fffaf0", GOLD, 2, 10)
    s += text(cx, 214, "перемикач", 12, "#8a6a14", "middle", "bold")
    s += text(cx, 234, "(транзистори)", 9.5, GREY, "middle")
    s += text(cx, 254, "вгору=HIGH · вниз=LOW", 8.3, GREY, "middle")
    s += circle(cx, 228, 4, INK, INK, 0)
    s += line(cx + 70, 228, cx + 230, 228, INK, 2.4)
    s += text(cx + 235, 232, "ніжка", 12, INK, "start", "bold")
    s += text(cx + 90, 150, "↑ до VDD → HIGH", 11, RED, "start", "bold")
    s += text(cx + 90, 318, "↓ до GND → LOW", 11, BLUE, "start", "bold")
    s += text(W / 2, 388, "Щоб напруга БУЛА, потрібне джерело й шлях для струму (Модуль 1).", 11.5, INK, "middle", "bold")
    save("fig-22-1-1-drive-the-line.svg", s)


# ── Рис. 22.1.2 — двотактний каскад ──────────────────────────────────────────
def fig12_push_pull():
    W, H = 820, 480
    s = header(W, H)
    s += text(W / 2, 32, "Двотактний каскад: верхній P, нижній N, ніжка посередині", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "завжди відкритий лише один — рідня CMOS-пари (§12.9)", 12.5, GREY, "middle", style="italic")
    cx = 360
    s += line(cx - 120, 108, cx + 120, 108, RED, 3)
    s += text(cx - 120, 100, "VDD", 12, RED, "start", "bold")
    s += line(cx - 120, 412, cx + 120, 412, BLUE, 3)
    s += text(cx - 120, 434, "GND", 12, BLUE, "start", "bold")
    s += line(cx, 108, cx, 152, INK, 2.4)
    s += fet(cx - 35, 152, 70, 68, "P", "struct")
    s += line(cx, 220, cx, 250, INK, 2.4)
    s += circle(cx, 250, 5, INK, INK, 0)
    s += line(cx, 250, cx + 160, 250, INK, 2.6)
    s += text(cx + 165, 254, "ніжка", 13, INK, "start", "bold")
    s += line(cx, 250, cx, 280, INK, 2.4)
    s += fet(cx - 35, 280, 70, 68, "N", "struct")
    s += line(cx, 348, cx, 412, INK, 2.4)
    # control
    s += rect(60, 212, 150, 76, "#fffaf0", GOLD, 2, 10)
    s += text(135, 244, "керування", 11, "#8a6a14", "middle", "bold")
    s += text(135, 264, "(біт OUT, §20.3)", 8.5, GREY, "middle")
    s += line(210, 238, cx - 35, 186, GREY, 1.6)
    s += line(210, 262, cx - 35, 314, GREY, 1.6)
    s += text(cx + 95, 182, "відкр → ніжка до VDD", 9.5, RED, "start", "bold")
    s += text(cx + 95, 196, "(HIGH)", 9, GREY, "start")
    s += text(cx + 95, 320, "відкр → ніжка до GND", 9.5, BLUE, "start", "bold")
    s += text(cx + 95, 334, "(LOW)", 9, GREY, "start")
    s += rect(120, 446, 580, 28, LGRN, GREEN, 1.4, 8)
    s += text(410, 465, "Один біт у регістрі — і ніжка йде до однієї з двох шин.", 11.5, INK, "middle", "bold")
    save("fig-22-1-2-push-pull.svg", s)


# ── Рис. 22.1.3 — біт OUT керує затворами ────────────────────────────────────
def fig13_register_control():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 32, "Біт OUT керує затворами: 1 → верхній, 0 → нижній", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "абстрактний «біт» Розділу 20 стає реальним рухом заліза", 12.5, GREY, "middle", style="italic")
    s += text(150, 108, "регістр OUT", 12, INK, "middle", "bold")
    cw, x0 = 30, 60
    val = 0b00000100
    for i in range(8):
        bp = 7 - i
        b = (val >> bp) & 1
        on = (bp == 2)
        cx = x0 + i * cw
        s += rect(cx, 124, cw, 30, LRED if on else "#ffffff", RED if on else INK, 1.6 if on else 1.2)
        s += text(cx + cw / 2, 145, str(b), 13, RED if on else INK, "middle", "bold")
    s += text(x0 + 5 * cw + cw / 2, 176, "біт 2 = 1", 9.5, RED, "middle", "bold")
    s += arrow(308, 139, 362, 139, INK, 2.4)
    s += rect(368, 110, 150, 58, "#fffaf0", GOLD, 2, 10)
    s += text(443, 134, "внутрішня", 11, "#8a6a14", "middle", "bold")
    s += text(443, 152, "логіка", 11, "#8a6a14", "middle", "bold")
    s += arrow(520, 139, 590, 139, INK, 2.4)
    s += fet(606, 96, 80, 56, "P", "on")
    s += fet(606, 184, 80, 56, "N", "off")
    s += text(696, 124, "1 → відкрити", 10.5, GREEN, "start", "bold")
    s += text(696, 212, "0 → закрити", 10.5, GREY, "start", "bold")
    s += text(440, 304, "Запис у регістр фізично смикає затвори транзисторів.", 12, INK, "middle", "bold")
    s += text(440, 340, "(а 0 у біті — навпаки: верхній закр, нижній відкр)", 10, GREY, "middle", style="italic")
    save("fig-22-1-3-register-control.svg", s)


# ── Рис. 22.1.4 — HIGH і LOW ─────────────────────────────────────────────────
def fig14_high_low():
    W, H = 900, 460
    s = header(W, H)
    s += text(W / 2, 32, "HIGH і LOW — обидва «сильні»: віддає або приймає струм", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "push-pull жене лінію в обидва боки з малим опором", 12.5, GREY, "middle", style="italic")

    def stage(ox, title2, p_state, n_state, pin_rail, cur_dir, cur_col):
        cx = ox + 130
        o = rect(ox, 88, 360, 308, "none", FAINT, 2, 12)
        o += text(ox + 180, 114, title2, 13, cur_col, "middle", "bold")
        o += line(cx - 100, 150, cx + 70, 150, RED, 2.6)
        o += text(cx - 100, 142, "VDD", 10, RED, "start", "bold")
        o += line(cx - 100, 360, cx + 70, 360, BLUE, 2.6)
        o += text(cx - 100, 380, "GND", 10, BLUE, "start", "bold")
        o += line(cx, 150, cx, 172, INK, 2)
        o += fet(cx - 30, 172, 60, 54, "P", p_state)
        o += line(cx, 226, cx, 256, INK, 2)
        o += circle(cx, 256, 4, INK, INK, 0)
        o += line(cx, 256, cx + 150, 256, INK, 2.4)
        o += text(cx + 152, 250, "ніжка", 10, INK, "start", "bold")
        o += line(cx, 256, cx, 286, INK, 2)
        o += fet(cx - 30, 286, 60, 54, "N", n_state)
        o += line(cx, 340, cx, 360, INK, 2)
        if cur_dir == "out":
            o += arrow(cx + 55, 274, cx + 120, 274, cur_col, 2.4)
            o += text(cx + 88, 292, "віддає (source)", 9, cur_col, "middle", "bold")
        else:
            o += arrow(cx + 120, 274, cx + 55, 274, cur_col, 2.4)
            o += text(cx + 88, 292, "приймає (sink)", 9, cur_col, "middle", "bold")
        return o

    s += stage(40, "HIGH — верхній відкритий", "on", "off", "VDD", "out", RED)
    s += stage(500, "LOW — нижній відкритий", "off", "on", "GND", "in", BLUE)
    s += text(450, 430, "У кожному стані ніжку жорстко тримає відкритий транзистор — звідси «сильний» рівень.",
              11.5, INK, "middle", "bold")
    save("fig-22-1-4-high-low.svg", s)


# ── Рис. 22.1.5 — shoot-through ──────────────────────────────────────────────
def fig15_shoot_through():
    W, H = 860, 420
    s = header(W, H)
    s += text(W / 2, 32, "Заборонено: обидва відкриті — VDD коротне на GND", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "тому керування навперемінне за будовою", 12.5, GREY, "middle", style="italic")
    cx = 290
    s += line(cx - 100, 118, cx + 100, 118, RED, 3)
    s += text(cx - 100, 110, "VDD", 11, RED, "start", "bold")
    s += line(cx - 100, 360, cx + 100, 360, BLUE, 3)
    s += text(cx - 100, 382, "GND", 11, BLUE, "start", "bold")
    s += line(cx, 118, cx, 150, RED, 2.4)
    s += fet(cx - 32, 150, 64, 62, "P", "on_red")
    s += line(cx, 212, cx, 288, RED, 3)
    s += fet(cx - 32, 288, 64, 62, "N", "on_red")
    s += line(cx, 350, cx, 360, RED, 2.4)
    s += arrow(cx + 52, 138, cx + 52, 352, RED, 4)
    s += text(cx + 70, 244, "наскрізний струм", 11, RED, "start", "bold")
    s += text(cx + 70, 262, "(shoot-through)", 10, RED, "start")
    s += rect(560, 168, 264, 124, "#fdeded", RED, 2, 12)
    s += text(692, 198, "✗ ЗАБОРОНЕНО", 14, RED, "middle", "bold")
    s += text(692, 226, "коротке замикання", 10.5, INK, "middle")
    s += text(692, 244, "живлення!", 10.5, INK, "middle")
    s += text(692, 272, "гріє · марнує · псує", 9.5, GREY, "middle")
    s += text(430, 398, "При перемиканні є крихітна «мертва пауза», коли закриті обидва.", 11.5, INK, "middle", "bold")
    save("fig-22-1-5-shoot-through.svg", s)


# ── Рис. 22.1.6 — ніжка живить світлодіод ────────────────────────────────────
def fig16_led_drive():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 32, "Двотактний вихід (HIGH) живить світлодіод", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "ніжка сама проштовхує струм — без зовнішніх помічників", 12.5, GREY, "middle", style="italic")
    s += line(120, 108, 420, 108, RED, 3)
    s += text(120, 100, "VDD 3.3 В", 11, RED, "start", "bold")
    cx = 240
    s += line(cx, 108, cx, 148, RED, 2.4)
    s += fet(cx - 30, 148, 60, 54, "P", "on")
    s += line(cx, 202, cx, 232, INK, 2.4)
    s += circle(cx, 232, 4, INK, INK, 0)
    s += text(cx - 44, 222, "ніжка", 10, INK, "end", "bold")
    s += text(cx - 44, 236, "= HIGH", 9, GREY, "end")
    s += line(cx, 232, cx, 296, INK, 2)
    s += rect(cx - 22, 296, 44, 40, "#ffffff", INK, 1.6, 3)
    s += text(cx, 320, "330 Ω", 9.5, INK, "middle", "bold")
    s += line(cx, 336, cx, 364, INK, 2)
    s += f'<path d="M {cx - 14},{364} L {cx + 14},{364} L {cx},{386} Z" fill="{RED}" stroke="{RED}"/>\n'
    s += line(cx - 16, 386, cx + 16, 386, RED, 2.4)
    for dx, dy in [(16, -6), (18, 4)]:
        s += line(cx + 18, 372, cx + 18 + dx, 372 + dy, "#e0a72a", 2)
    s += text(cx + 44, 380, "світлодіод", 9.5, "#b07d12", "start", "bold")
    s += line(cx, 388, cx, 404, INK, 2)
    s += line(120, 404, 420, 404, BLUE, 3)
    s += text(120, 396, "", 1, INK, "start")
    s += text(390, 420, "", 1, INK, "start")
    s += text(126, 420, "GND", 11, BLUE, "start", "bold")
    s += arrow(cx + 30, 318, cx + 30, 352, RED, 2.2)
    s += text(cx + 46, 340, "I", 11, RED, "start", "bold")
    s += rect(440, 150, 400, 180, "#fbfbfb", FAINT, 1.6, 12)
    s += text(640, 178, "Скільки струму жене ніжка?", 12.5, INK, "middle", "bold")
    s += text(460, 210, "на резисторі:  3.3 − 2.0 = 1.3 В", 11.5, INK, "start")
    s += text(460, 240, "I = V / R = 1.3 / 330 ≈ 3.9 мА", 13, RED, "start", "bold")
    s += text(460, 274, "ніжка ВІДДАЄ ці 3.9 мА сама (source)", 10.5, GREEN, "start", "bold")
    s += text(460, 300, "— світлодіод світиться без помічників", 9.5, GREY, "start")
    s += text(640, 360, "Скільки витримає ніжка — межі в §22.6.", 10.5, INK, "middle", "bold")
    save("fig-22-1-6-led-drive.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §22.2 — Open-drain і навіщо він
# ─────────────────────────────────────────────────────────────────────────────

def _pullup(x, y_top, y_bot, vcol=RED, vlabel="VDD"):
    """Резистор-підтяжка від шини (y_top) до вузла (y_bot)."""
    o = line(x, y_top, x, y_top + 22, INK, 2)
    o += rect(x - 12, y_top + 22, 24, 36, "#ffffff", GOLD, 1.6, 3)
    o += line(x, y_top + 58, x, y_bot, INK, 2)
    return o


# ── Рис. 22.2.1 — open-drain: лише нижній транзистор ─────────────────────────
def fig21_open_drain():
    W, H = 860, 420
    s = header(W, H)
    s += text(W / 2, 32, "Open-drain: двотактний без верхнього транзистора", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "лишився тільки нижній (N) — тягне вниз або відпускає", 12.5, GREY, "middle", style="italic")
    cx = 240
    s += line(cx - 110, 118, cx + 90, 118, RED, 2.4)
    s += text(cx - 110, 110, "VDD", 11, RED, "start", "bold")
    s += text(cx + 14, 148, "✗ верхнього", 10, GREY, "start")
    s += text(cx + 14, 164, "транзистора нема", 10, GREY, "start")
    s += line(cx, 118, cx, 172, "#cccccc", 1.6, dash="4,3")
    s += circle(cx, 235, 5, INK, INK, 0)
    s += line(cx, 235, cx + 170, 235, INK, 2.6)
    s += text(cx + 175, 239, "ніжка", 12, INK, "start", "bold")
    s += line(cx, 235, cx, 270, INK, 2.4)
    s += fet(cx - 32, 270, 64, 58, "N", "struct")
    s += line(cx, 328, cx, 372, INK, 2.4)
    s += line(cx - 110, 372, cx + 90, 372, BLUE, 2.4)
    s += text(cx - 110, 392, "GND", 11, BLUE, "start", "bold")
    s += rect(520, 118, 320, 204, "none", FAINT, 2, 12)
    s += text(680, 146, "два стани ніжки", 12.5, INK, "middle", "bold")
    s += rect(540, 168, 280, 58, LGRN, GREEN, 1.6, 8)
    s += text(556, 192, "N відкритий → LOW", 12, GREEN, "start", "bold")
    s += text(556, 212, "сильний нуль, приймає струм (sink)", 8.7, INK, "start")
    s += rect(540, 238, 280, 58, "#f0f0f0", GREY, 1.6, 8)
    s += text(556, 262, "N закритий → ВІДПУЩЕНО", 12, GREY, "start", "bold")
    s += text(556, 282, "Hi-Z, «висить у повітрі» — це НЕ high!", 8.7, INK, "start")
    s += text(430, 406, "«Стік» (ніжка) лишається відкритим, коли транзистор закрито — звідси назва.", 11, INK, "middle", "bold")
    save("fig-22-2-1-open-drain.svg", s)


# ── Рис. 22.2.2 — потрібна підтяжка ──────────────────────────────────────────
def fig22_needs_pullup():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 32, "Open-drain потребує підтяжки: вона робить HIGH", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "HIGH тут слабкий (резистор), LOW сильний (транзистор)", 12.5, GREY, "middle", style="italic")

    def panel(ox, title2, n_state, line_state, t_col):
        cx = ox + 130
        o = rect(ox, 88, 400, 312, "none", FAINT, 2, 12)
        o += text(ox + 200, 114, title2, 12.5, t_col, "middle", "bold")
        o += line(cx - 70, 152, cx + 110, 152, RED, 2.2)
        o += text(cx - 70, 144, "VDD", 10, RED, "start", "bold")
        o += _pullup(cx + 80, 152, 256)
        o += text(cx + 96, 200, "підтяжка", 8.5, "#8a6a14", "start", "bold")
        o += circle(cx + 80, 256, 4, INK, INK, 0)
        o += line(cx, 256, cx + 80, 256, INK, 2)
        o += line(cx + 80, 256, cx + 150, 256, INK, 2.4)
        lc = RED if line_state == "high" else BLUE
        o += text(cx + 152, 250, "лінія", 9, INK, "start", "bold")
        o += text(cx + 152, 266, "= " + ("HIGH" if line_state == "high" else "LOW"), 11, lc, "start", "bold")
        o += line(cx, 256, cx, 282, INK, 2)
        o += fet(cx - 30, 282, 60, 52, "N", n_state)
        o += line(cx, 334, cx, 360, INK, 2)
        o += line(cx - 70, 360, cx + 110, 360, BLUE, 2.2)
        o += text(cx - 70, 380, "GND", 10, BLUE, "start", "bold")
        return o

    s += panel(30, "N закритий → підтяжка тягне HIGH", "off", "high", RED)
    s += panel(470, "N відкритий → транзистор садить LOW", "on", "low", BLUE)
    s += text(450, 426, "Без підтяжки відпущена ніжка просто «висіла» б — тож вона обов'язкова.", 11.5, INK, "middle", "bold")
    save("fig-22-2-2-needs-pullup.svg", s)


# ── Рис. 22.2.3 — wired-AND ──────────────────────────────────────────────────
def fig23_wired_and():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "Wired-AND: багато open-drain на одній лінії", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "будь-хто тягне вниз → вся лінія LOW; усі відпустили → HIGH", 12.5, GREY, "middle", style="italic")
    s += line(80, 108, 840, 108, RED, 2.4)
    s += text(80, 100, "VDD", 11, RED, "start", "bold")
    s += _pullup(130, 108, 210)
    s += text(146, 158, "підтяжка", 8.5, "#8a6a14", "start", "bold")
    s += line(130, 210, 800, 210, INK, 3)
    s += text(806, 214, "спільна лінія", 10.5, INK, "start", "bold")
    for name, st, x in [("№1", "on", 300), ("№2", "off", 480), ("№3", "off", 660)]:
        s += circle(x, 210, 4, INK, INK, 0)
        s += line(x, 210, x, 252, INK, 2)
        s += fet(x - 28, 252, 56, 50, "N", st)
        s += line(x, 302, x, 342, INK, 2)
        s += text(x, 364, name + (" (тягне)" if st == "on" else " (відпустив)"), 9, (GREEN if st == "on" else GREY), "middle", "bold")
    s += line(272, 342, 688, 342, BLUE, 2.4)
    s += text(694, 346, "GND", 10, BLUE, "start", "bold")
    s += rect(120, 384, 680, 46, LGRN, GREEN, 1.4, 10)
    s += text(460, 404, "Тут №1 тягне → вся лінія LOW. Логічне «І» — самим дротом,", 11.5, INK, "middle", "bold")
    s += text(460, 422, "без жодного вентиля (монтажне «І»).", 10, GREY, "middle")
    save("fig-22-2-3-wired-and.svg", s)


# ── Рис. 22.2.4 — push-pull на спільній лінії = КЗ ───────────────────────────
def fig24_pushpull_clash():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "Push-pull на спільній лінії — коротке між чипами", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "один жене HIGH, інший LOW → VDD коротне на GND крізь чипи", 12, GREY, "middle", style="italic")
    s += line(80, 110, 700, 110, RED, 2.4)
    s += text(80, 102, "VDD", 11, RED, "start", "bold")
    s += line(80, 360, 700, 360, BLUE, 2.4)
    s += text(80, 380, "GND", 11, BLUE, "start", "bold")
    lx, rx = 260, 520
    # chip A: drives HIGH (P on, N off)
    s += line(lx, 110, lx, 150, RED, 2.6)
    s += fet(lx - 28, 150, 56, 50, "P", "on_red")
    s += line(lx, 200, lx, 235, RED, 2.6)
    s += fet(lx - 28, 260, 56, 50, "N", "off")
    s += line(lx, 310, lx, 360, GREY, 1.4)
    s += text(lx, 398, "чіп A: жене HIGH", 10, RED, "middle", "bold")
    # chip B: drives LOW (P off, N on)
    s += line(rx, 110, rx, 150, GREY, 1.4)
    s += fet(rx - 28, 150, 56, 50, "P", "off")
    s += line(rx, 200, rx, 235, INK, 2)
    s += fet(rx - 28, 260, 56, 50, "N", "on_red")
    s += line(rx, 310, rx, 360, RED, 2.6)
    s += text(rx, 398, "чіп B: жене LOW", 10, BLUE, "middle", "bold")
    # shared line
    s += circle(lx, 235, 4, INK, INK, 0)
    s += circle(rx, 235, 4, INK, INK, 0)
    s += line(lx, 235, rx, 235, RED, 2.6)
    s += text(390, 228, "спільна лінія", 10, INK, "middle", "bold")
    s += text(390, 300, "VDD → P(A) → лінія → N(B) → GND = КЗ!", 11, RED, "middle", "bold")
    s += rect(700, 150, 180, 80, "#fdeded", RED, 2, 12)
    s += text(790, 184, "✗ КЗ", 16, RED, "middle", "bold")
    s += text(790, 208, "між чипами", 10, INK, "middle")
    save("fig-22-2-4-pushpull-clash.svg", s)


# ── Рис. 22.2.5 — застосування ───────────────────────────────────────────────
def fig25_uses():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 32, "Навіщо open-drain: спільна шина та сигнал «потрібна увага»", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "скрізь працює та сама магія «тягни вниз або відпусти»", 12.5, GREY, "middle", style="italic")
    # left: shared bus
    s += rect(40, 88, 400, 300, "none", FAINT, 2, 12)
    s += text(240, 114, "Спільна шина (як I2C)", 13, INK, "middle", "bold")
    for ly in (160, 196):
        s += line(90, ly, 400, ly, INK, 2.4)
        s += _pullup(110, 140, ly) if ly == 160 else ""
    s += rect(60, 138, 24, 24, "#fff7e6", GOLD, 1.2, 3)
    for dx in (200, 280, 360):
        s += rect(dx - 26, 250, 52, 56, "#fbfbfb", INK, 1.4, 6)
        s += text(dx, 282, "давач", 8.5, INK, "middle")
        s += line(dx - 8, 250, dx - 8, 160, GREY, 1.4)
        s += line(dx + 8, 250, dx + 8, 196, GREY, 1.4)
    s += text(240, 358, "багато пристроїв на 2 дротах — без зіткнень", 9.5, GREY, "middle")
    # right: attention line
    s += rect(480, 88, 400, 300, "none", FAINT, 2, 12)
    s += text(680, 114, "Сигнал «потрібна увага»", 13, INK, "middle", "bold")
    s += line(540, 150, 840, 150, RED, 2.2)
    s += text(540, 142, "VDD", 9, RED, "start", "bold")
    s += _pullup(566, 150, 200)
    s += line(566, 200, 820, 200, INK, 2.6)
    s += text(824, 204, "лінія", 9, INK, "start", "bold")
    for dx, st in ((620, "on"), (700, "off"), (780, "off")):
        s += circle(dx, 200, 3.5, INK, INK, 0)
        s += line(dx, 200, dx, 236, INK, 2)
        s += fet(dx - 22, 236, 44, 44, "N", st)
        s += line(dx, 280, dx, 312, INK, 2)
        s += text(dx, 332, "пристр.", 8, INK, "middle")
    s += line(598, 312, 802, 312, BLUE, 2.2)
    s += text(680, 360, "будь-який тягне вниз → «є подія!», не заважаючи іншим", 9.3, GREY, "middle")
    save("fig-22-2-5-uses.svg", s)


# ── Рис. 22.2.6 — зсув рівнів ────────────────────────────────────────────────
def fig26_level_shift():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "Зсув рівнів: open-drain зшиває 3.3 В і 5 В", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "ніхто не нав'язує свою напругу — «верх» задає спільна підтяжка", 12, GREY, "middle", style="italic")
    s += line(120, 120, 780, 120, GREEN, 2.4)
    s += text(120, 112, "VDD підтяжки = 3.3 В (нижча)", 10.5, GREEN, "start", "bold")
    s += _pullup(170, 120, 210)
    s += text(186, 168, "підтяжка → 3.3 В", 8.5, "#8a6a14", "start", "bold")
    s += line(170, 210, 720, 210, INK, 3)
    s += text(724, 214, "спільна лінія", 10, INK, "start", "bold")
    s += line(120, 360, 780, 360, BLUE, 2.4)
    s += text(120, 380, "GND (спільна)", 10, BLUE, "start", "bold")
    for x, lab, lc, lf in ((360, "чіп 5 В (OD)", RED, LRED), (560, "чіп 3.3 В (OD)", GREEN, LGRN)):
        s += circle(x, 210, 4, INK, INK, 0)
        s += line(x, 210, x, 250, INK, 2)
        s += fet(x - 28, 250, 56, 50, "N", "off")
        s += line(x, 300, x, 360, INK, 2)
        s += rect(x - 64, 384, 128, 28, lf, lc, 1.4, 6)
        s += text(x, 403, lab, 9.5, lc, "middle", "bold")
    s += text(640, 290, "кожен лише тягне вниз", 9.5, GREY, "middle", style="italic")
    s += text(640, 306, "або відпускає", 9.5, GREY, "middle", style="italic")
    save("fig-22-2-6-level-shift.svg", s)


def poly(points, color=INK, w=2, fill="none", dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return (f'<polyline points="{pts}" fill="{fill}" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round" stroke-linecap="round"/>\n')


# ── Рис. 22.3.1 — вхід слухає напругу ────────────────────────────────────────
def fig31_input_senses():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Ніжка-вхід: вона не жене напругу, а «нюхає» її", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "високоомний буфер міряє напругу на лінії й видає в ядро чистий 0 або 1", 12.5, GREY, "middle", style="italic")
    s += line(70, 210, 250, 210, INK, 2.6)
    s += circle(70, 210, 5, INK, INK, 0)
    s += text(70, 196, "ніжка-вхід", 12, INK, "start", "bold")
    s += text(120, 240, "Vin = ?", 12, GREY, "start", style="italic")
    s += rect(250, 150, 250, 120, "#fbfcff", INK, 2, 12)
    s += text(375, 176, "вхідний буфер", 12.5, INK, "middle", "bold")
    s += f'<polygon points="300,198 300,252 362,225" fill="{LBLUE}" stroke="{BLUE}" stroke-width="2"/>\n'
    s += text(395, 216, "компаратор", 10, BLUE, "start")
    s += text(395, 232, "+ тригер Шмітта", 9, GREY, "start")
    s += arrow(500, 210, 638, 210, INK, 2.6)
    s += rect(640, 184, 170, 52, LGRN, GREEN, 1.6, 8)
    s += text(725, 206, "0 або 1", 14, GREEN, "middle", "bold")
    s += text(725, 224, "чистий рівень → ядро", 8.5, INK, "middle")
    s += rect(130, 300, 640, 78, LAMB, GOLD, 1.6, 10)
    s += text(450, 324, "Вхід — високоомний: бере мікроскопічний струм (нано-/мікроампери),", 12, INK, "middle", "bold")
    s += text(450, 344, "тож майже не навантажує лінію — лише вимірює, хто її тримає.", 11, INK, "middle")
    s += text(450, 366, "Це протилежність виходу з §22.1, що активно ЖЕНЕ напругу.", 10, GREY, "middle", style="italic")
    save("fig-22-3-1-input-senses.svg", s)


# ── Рис. 22.3.2 — два пороги, три зони ───────────────────────────────────────
def fig32_threshold_band():
    W, H = 880, 460
    s = header(W, H)
    s += text(W / 2, 32, "Два пороги, три зони: як вхід ділить напругу на 0 і 1", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "нижче VIL — певний нуль; вище VIH — певна одиниця; між ними — невизначеність", 12, GREY, "middle", style="italic")
    bx, bw = 250, 120
    ytop, h = 90, 320
    ybot = ytop + h
    vmax, vil, vih = 3.3, 0.99, 2.31
    yv = lambda v: ybot - (v / vmax) * h
    s += rect(bx, yv(vil), bw, ybot - yv(vil), LGRN, GREEN, 1.6)
    s += rect(bx, yv(vih), bw, yv(vil) - yv(vih), "#f1f1f1", GREY, 1.6)
    s += rect(bx, ytop, bw, yv(vih) - ytop, LBLUE, BLUE, 1.6)
    s += line(bx - 14, ytop, bx - 14, ybot, INK, 2)
    for v in (0, 1, 2, 3):
        s += line(bx - 18, yv(v), bx - 14, yv(v), INK, 1.6)
        s += text(bx - 22, yv(v) + 4, f"{v} В", 10, INK, "end")
    s += text(bx + bw / 2, ytop - 12, "напруга на ніжці", 10.5, INK, "middle", "bold")
    s += line(bx, yv(vil), bx + bw + 30, yv(vil), GREEN, 2, dash="5,3")
    s += text(bx + bw + 36, yv(vil) + 4, "VIL ≈ 0.99 В  (≈0.3·VDD)", 11, GREEN, "start", "bold")
    s += line(bx, yv(vih), bx + bw + 30, yv(vih), BLUE, 2, dash="5,3")
    s += text(bx + bw + 36, yv(vih) + 4, "VIH ≈ 2.31 В  (≈0.7·VDD)", 11, BLUE, "start", "bold")
    s += text(bx + bw / 2, (yv(vil) + ybot) / 2 + 4, "0 (LOW)", 13, GREEN, "middle", "bold")
    s += text(bx + bw / 2, (yv(vih) + yv(vil)) / 2 - 3, "?", 18, GREY, "middle", "bold")
    s += text(bx + bw / 2, (yv(vih) + yv(vil)) / 2 + 15, "невизначено", 9.5, GREY, "middle")
    s += text(bx + bw / 2, (ytop + yv(vih)) / 2 + 4, "1 (HIGH)", 13, BLUE, "middle", "bold")
    s += rect(560, 250, 296, 168, "none", FAINT, 1.6, 10)
    s += text(708, 276, "Чому аж дві межі?", 12.5, INK, "middle", "bold")
    s += text(576, 302, "• нижче VIL — гарантований 0", 10.5, GREEN, "start")
    s += text(576, 324, "• вище VIH — гарантована 1", 10.5, BLUE, "start")
    s += text(576, 346, "• між ними вхід «не певний» —", 10.5, GREY, "start")
    s += text(588, 364, "такої напруги на виході уникають", 10.5, GREY, "start")
    s += text(576, 392, "Сіра смуга — це і є запас", 10, INK, "start", style="italic")
    s += text(576, 408, "проти завад (див. далі).", 10, INK, "start", style="italic")
    save("fig-22-3-2-threshold-band.svg", s)


# ── Рис. 22.3.3 — запас завадостійкості ──────────────────────────────────────
def fig33_noise_margin():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 32, "Запас завадостійкості: пороги не торкаються рівнів драйвера", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "між тим, що ВИДАЄ драйвер, і тим, що ВИМАГАЄ вхід, лишається подушка", 12, GREY, "middle", style="italic")
    ytop, h = 96, 300
    ybot = ytop + h
    vmax = 3.3
    yv = lambda v: ybot - (v / vmax) * h
    vol, voh, vil, vih = 0.2, 3.1, 0.99, 2.31
    s += line(120, ytop, 120, ybot, INK, 2)
    for v in (0, 1, 2, 3):
        s += line(116, yv(v), 120, yv(v), INK, 1.6)
        s += text(112, yv(v) + 4, f"{v}", 10, INK, "end")
    s += text(120, ybot + 20, "В", 10, INK, "middle")
    dx, dw = 200, 150
    s += rect(dx, yv(vol), dw, ybot - yv(vol), LGRN, GREEN, 1.6)
    s += rect(dx, yv(voh), dw, yv(vol) - yv(voh), "#fafafa", FAINT, 1.2)
    s += rect(dx, ytop, dw, yv(voh) - ytop, LBLUE, BLUE, 1.6)
    s += line(dx, yv(vol), dx + dw, yv(vol), GREEN, 2)
    s += line(dx, yv(voh), dx + dw, yv(voh), BLUE, 2)
    s += text(dx + dw / 2, ytop - 14, "драйвер ВИДАЄ", 12, INK, "middle", "bold")
    s += text(dx + dw / 2, yv(vol) + 20, "VOL", 11, GREEN, "middle", "bold")
    s += text(dx + dw / 2, yv(voh) - 8, "VOH", 11, BLUE, "middle", "bold")
    rx, rw = 520, 150
    s += rect(rx, yv(vil), rw, ybot - yv(vil), LGRN, GREEN, 1.6)
    s += rect(rx, yv(vih), rw, yv(vil) - yv(vih), "#f1f1f1", GREY, 1.6)
    s += rect(rx, ytop, rw, yv(vih) - ytop, LBLUE, BLUE, 1.6)
    s += line(rx, yv(vil), rx + rw, yv(vil), GREEN, 2)
    s += line(rx, yv(vih), rx + rw, yv(vih), BLUE, 2)
    s += text(rx + rw / 2, ytop - 14, "вхід ВИМАГАЄ", 12, INK, "middle", "bold")
    s += text(rx + rw / 2, yv(vil) + 16, "VIL", 11, GREEN, "middle", "bold")
    s += text(rx + rw / 2, yv(vih) - 8, "VIH", 11, BLUE, "middle", "bold")
    mx = (dx + dw + rx) / 2
    s += line(dx + dw, yv(vol), mx, yv(vol), GREEN, 1.2, dash="3,3")
    s += line(rx, yv(vil), mx, yv(vil), GREEN, 1.2, dash="3,3")
    s += arrow(mx, yv(vol), mx, yv(vil), GREEN, 2)
    s += arrow(mx, yv(vil), mx, yv(vol), GREEN, 2)
    s += f'<rect x="{mx-46:.1f}" y="{(yv(vol)+yv(vil))/2-13:.1f}" width="92" height="26" rx="6" fill="{LGRN}" stroke="{GREEN}" stroke-width="1.4"/>\n'
    s += text(mx, (yv(vol) + yv(vil)) / 2 + 5, "запас НИЗУ", 9.5, GREEN, "middle", "bold")
    s += line(dx + dw, yv(voh), mx, yv(voh), BLUE, 1.2, dash="3,3")
    s += line(rx, yv(vih), mx, yv(vih), BLUE, 1.2, dash="3,3")
    s += arrow(mx, yv(voh), mx, yv(vih), BLUE, 2)
    s += arrow(mx, yv(vih), mx, yv(voh), BLUE, 2)
    s += f'<rect x="{mx-46:.1f}" y="{(yv(voh)+yv(vih))/2-13:.1f}" width="92" height="26" rx="6" fill="{LBLUE}" stroke="{BLUE}" stroke-width="1.4"/>\n'
    s += text(mx, (yv(voh) + yv(vih)) / 2 + 5, "запас ВГОРІ", 9.5, BLUE, "middle", "bold")
    s += rect(700, 150, 192, 156, "none", FAINT, 1.6, 10)
    s += text(796, 176, "запас (noise margin)", 11, INK, "middle", "bold")
    s += text(716, 204, "NML = VIL − VOL", 11.5, GREEN, "start", "bold")
    s += text(716, 228, "NMH = VOH − VIH", 11.5, BLUE, "start", "bold")
    s += text(716, 258, "Завада, менша за", 9.7, INK, "start")
    s += text(716, 274, "цей запас, не зіб'є", 9.7, INK, "start")
    s += text(716, 290, "рівень. CMOS — щедрий.", 9.7, INK, "start")
    save("fig-22-3-3-noise-margin.svg", s)


# ── Рис. 22.3.4 — гістерезис / тригер Шмітта ─────────────────────────────────
def fig34_hysteresis():
    W, H = 940, 440
    s = header(W, H)
    s += text(W / 2, 32, "Гістерезис (тригер Шмітта): дві межі замість однієї", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "вмикається на VT+, вимикається на нижчому VT− — і шум не «брязкає»", 12, GREY, "middle", style="italic")
    ox, oy = 110, 360
    w2, h2 = 300, 230
    s += rect(70, 86, 380, 320, "none", FAINT, 1.6, 12)
    s += text(260, 110, "Передавальна крива", 12.5, INK, "middle", "bold")
    s += arrow(ox, oy, ox + w2 + 20, oy, INK, 2)
    s += arrow(ox, oy, ox, oy - h2 - 20, INK, 2)
    s += text(ox + w2 + 24, oy + 4, "Vin", 11, INK, "start", "bold")
    s += text(ox - 4, oy - h2 - 26, "Vout", 11, INK, "middle", "bold")
    vtm, vtp = ox + 110, ox + 190
    ylo, yhi = oy, oy - h2
    s += line(ox, ylo, vtp, ylo, RED, 2.6)
    s += arrow((ox + vtp) / 2 - 8, ylo, (ox + vtp) / 2 + 8, ylo, RED, 2.6)
    s += line(vtp, ylo, vtp, yhi, RED, 2.6)
    s += line(vtp, yhi, ox + w2, yhi, RED, 2.6)
    s += arrow((vtp + ox + w2) / 2 - 8, yhi, (vtp + ox + w2) / 2 + 8, yhi, RED, 2.6)
    s += line(ox + w2, yhi - 7, vtm, yhi - 7, BLUE, 2.6)
    s += arrow((vtm + ox + w2) / 2 + 8, yhi - 7, (vtm + ox + w2) / 2 - 8, yhi - 7, BLUE, 2.6)
    s += line(vtm, yhi - 7, vtm, ylo - 7, BLUE, 2.6)
    s += line(vtm, ylo - 7, ox + 7, ylo - 7, BLUE, 2.6)
    s += arrow((vtm + ox) / 2 + 8, ylo - 7, (vtm + ox) / 2 - 8, ylo - 7, BLUE, 2.6)
    s += line(vtm, oy + 4, vtm, yhi, GREY, 1.2, dash="4,3")
    s += text(vtm, oy + 20, "VT−", 11, BLUE, "middle", "bold")
    s += line(vtp, oy + 4, vtp, yhi, GREY, 1.2, dash="4,3")
    s += text(vtp, oy + 20, "VT+", 11, RED, "middle", "bold")
    s += line(vtm, 250, vtp, 250, GOLD, 2)
    s += line(vtm, 244, vtm, 256, GOLD, 2)
    s += line(vtp, 244, vtp, 256, GOLD, 2)
    s += text((vtm + vtp) / 2, 242, "гістерезис", 9.5, "#8a6a14", "middle", "bold")
    s += text(ox - 8, ylo + 4, "0", 10, INK, "end")
    s += text(ox - 8, yhi + 4, "1", 10, INK, "end")
    px = 500
    s += rect(px - 10, 86, 440, 320, "none", FAINT, 1.6, 12)
    s += text(px + 200, 110, "Повільний шумний фронт → один чистий перепад", 11.5, INK, "middle", "bold")
    bx0, bx1 = px + 20, px + 405
    yvtp, yvtm = 165, 230
    s += line(bx0, yvtp, bx1, yvtp, RED, 1.4, dash="5,3")
    s += text(bx1 + 4, yvtp + 4, "VT+", 9.5, RED, "start", "bold")
    s += line(bx0, yvtm, bx1, yvtm, BLUE, 1.4, dash="5,3")
    s += text(bx1 + 4, yvtm + 4, "VT−", 9.5, BLUE, "start", "bold")
    pts = [(bx0, 300), (px + 70, 295), (px + 110, 278), (px + 150, 266), (px + 180, 250),
           (px + 205, 232), (px + 225, 238), (px + 245, 210), (px + 265, 222), (px + 285, 196),
           (px + 305, 200), (px + 325, 178), (px + 350, 166), (px + 380, 150), (bx1, 122)]
    s += poly(pts, INK, 2.2)
    s += text(px + 60, 318, "вхід (шумний)", 9.5, INK, "start")
    xcross = px + 292
    yO0, yO1 = 360, 332
    s += line(bx0, yO0, xcross, yO0, GREEN, 2.6)
    s += line(xcross, yO0, xcross, yO1, GREEN, 2.6)
    s += line(xcross, yO1, bx1, yO1, GREEN, 2.6)
    s += text(px + 60, yO0 + 18, "вихід (чистий 0→1)", 9.5, GREEN, "start", "bold")
    s += text(px + 200, 400, "без гістерезису тут був би «брязкіт» — кілька 0/1 поспіль", 9.3, GREY, "middle", style="italic")
    save("fig-22-3-4-hysteresis.svg", s)


# ── Рис. 22.3.5 — TTL vs CMOS ────────────────────────────────────────────────
def fig35_ttl_cmos():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 32, "Дві родини порогів: TTL і CMOS (чому їх не можна плутати)", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "TTL міряє від «низьких» фіксованих вольтів; CMOS — від частки живлення", 12, GREY, "middle", style="italic")
    ytop, h = 110, 290
    ybot = ytop + h
    vmax = 5.0
    yv = lambda v: ybot - (v / vmax) * h
    s += line(90, ytop, 90, ybot, INK, 2)
    for v in range(0, 6):
        s += line(86, yv(v), 90, yv(v), INK, 1.6)
        s += text(82, yv(v) + 4, f"{v}", 10, INK, "end")
    s += text(120, ybot + 20, "В (живлення 5 В)", 10, INK, "start")

    def fam(cx, name, vil, vih, sub):
        bw = 150
        o = rect(cx, yv(vil), bw, ybot - yv(vil), LGRN, GREEN, 1.6)
        o += rect(cx, yv(vih), bw, yv(vil) - yv(vih), "#f1f1f1", GREY, 1.6)
        o += rect(cx, ytop, bw, yv(vih) - ytop, LBLUE, BLUE, 1.6)
        o += line(cx, yv(vil), cx + bw, yv(vil), GREEN, 2)
        o += line(cx, yv(vih), cx + bw, yv(vih), BLUE, 2)
        o += text(cx + bw / 2, ytop - 30, name, 14, INK, "middle", "bold")
        o += text(cx + bw / 2, ytop - 13, sub, 9.3, GREY, "middle")
        o += text(cx + bw + 8, yv(vil) + 4, f"VIL={vil} В", 10, GREEN, "start", "bold")
        o += text(cx + bw + 8, yv(vih) + 4, f"VIH={vih} В", 10, BLUE, "start", "bold")
        o += text(cx + bw / 2, (yv(vil) + ybot) / 2, "0", 13, GREEN, "middle", "bold")
        o += text(cx + bw / 2, (ytop + yv(vih)) / 2, "1", 13, BLUE, "middle", "bold")
        return o

    s += fam(200, "TTL", 0.8, 2.0, "пороги «внизу», несиметричні")
    s += fam(560, "CMOS", 1.5, 3.5, "≈0.3 і 0.7 живлення")
    s += rect(150, 412, 600, 50, LAMB, GOLD, 1.6, 10)
    s += text(450, 434, "Пастка: TTL-вихід дає в «1» лише ~2.4 В — а CMOS-вхід хоче ≥3.5 В.", 11.5, INK, "middle", "bold")
    s += text(450, 452, "TTL→CMOS без підтяжки часто не дотягує до одиниці.", 10, GREY, "middle")
    save("fig-22-3-5-ttl-cmos.svg", s)


# ── Рис. 22.3.6 — вхід ESP32 + застереження 5 В ──────────────────────────────
def fig36_esp32_input():
    W, H = 920, 470
    s = header(W, H)
    s += text(W / 2, 32, "Вхід ESP32: пороги CMOS від 3.3 В + тригер Шмітта", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "VIL ≈ 0.25·VDD, VIH ≈ 0.75·VDD; вхід зі Шміттом — стійкий до шуму", 12, GREY, "middle", style="italic")
    ytop, h = 96, 300
    ybot = ytop + h
    vmax, vil, vih = 3.3, 0.83, 2.48
    yv = lambda v: ybot - (v / vmax) * h
    bx, bw = 220, 130
    s += rect(bx, yv(vil), bw, ybot - yv(vil), LGRN, GREEN, 1.6)
    s += rect(bx, yv(vih), bw, yv(vil) - yv(vih), "#f1f1f1", GREY, 1.6)
    s += rect(bx, ytop, bw, yv(vih) - ytop, LBLUE, BLUE, 1.6)
    s += line(bx - 14, ytop, bx - 14, ybot, INK, 2)
    for v in (0, 1, 2, 3):
        s += line(bx - 18, yv(v), bx - 14, yv(v), INK, 1.6)
        s += text(bx - 22, yv(v) + 4, f"{v} В", 10, INK, "end")
    s += text(bx + bw / 2, ytop - 12, "ніжка ESP32 (VDD=3.3 В)", 10.5, INK, "middle", "bold")
    s += line(bx, yv(vil), bx + bw + 30, yv(vil), GREEN, 2, dash="5,3")
    s += text(bx + bw + 36, yv(vil) + 4, "VIL ≈ 0.83 В (0.25·VDD)", 10.5, GREEN, "start", "bold")
    s += line(bx, yv(vih), bx + bw + 30, yv(vih), BLUE, 2, dash="5,3")
    s += text(bx + bw + 36, yv(vih) + 4, "VIH ≈ 2.48 В (0.75·VDD)", 10.5, BLUE, "start", "bold")
    s += text(bx + bw / 2, (yv(vil) + ybot) / 2 + 4, "0", 13, GREEN, "middle", "bold")
    s += text(bx + bw / 2, (yv(vih) + yv(vil)) / 2 + 4, "?", 16, GREY, "middle", "bold")
    s += text(bx + bw / 2, (ytop + yv(vih)) / 2 + 4, "1", 13, BLUE, "middle", "bold")
    sx, sy = 600, 150
    s += rect(sx, sy, 190, 104, "#fbfcff", INK, 1.8, 10)
    s += f'<polygon points="{sx+34},{sy+28} {sx+34},{sy+78} {sx+96},{sy+53}" fill="{LBLUE}" stroke="{BLUE}" stroke-width="2"/>\n'
    gx, gy = sx + 48, sy + 53
    s += line(gx, gy + 7, gx + 11, gy + 7, INK, 1.6)
    s += line(gx + 11, gy + 7, gx + 11, gy - 7, INK, 1.6)
    s += line(gx + 6, gy - 7, gx + 17, gy - 7, INK, 1.6)
    s += line(gx + 6, gy - 7, gx + 6, gy + 7, INK, 1.6)
    s += text(sx + 95, sy - 8, "тригер Шмітта на вході", 10, INK, "middle", "bold")
    s += text(sx + 95, sy + 96, "чистить повільні/шумні фронти", 9, GREY, "middle")
    s += rect(560, 300, 340, 152, "#fdeded", RED, 2, 12)
    s += text(730, 326, "⚠ НЕ 5-вольтотерпимий!", 14, RED, "middle", "bold")
    s += text(578, 352, "Гранична напруга на ніжці ≈ VDD+0.3 = 3.6 В.", 10.3, INK, "start")
    s += text(578, 372, "Подати 5 В прямо на пін — спалити вхід.", 10.3, INK, "start")
    s += text(578, 398, "5-вольтовий сигнал заводь через:", 10.3, INK, "start", "bold")
    s += text(578, 416, "• дільник напруги (два резистори), або", 10, INK, "start")
    s += text(578, 434, "• перетворювач рівнів / open-drain + підтяжку 3.3 В", 10, INK, "start")
    save("fig-22-3-6-esp32-input.svg", s)


def _res_v(x, ya, yb, col=GOLD):
    """Вертикальний резистор між ya і yb з коробкою посередині."""
    mid = (ya + yb) / 2
    o = line(x, ya, x, mid - 18, INK, 2)
    o += rect(x - 12, mid - 18, 24, 36, "#ffffff", col, 1.6, 3)
    o += line(x, mid + 18, x, yb, INK, 2)
    return o


# ── Рис. 22.4.1 — плаваючий вхід ─────────────────────────────────────────────
def fig41_floating():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "Плаваючий вхід: ніжка без джерела ловить шум", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "нічого не тримає рівень → вхід «висить» у невизначеній зоні й читається випадково", 11.5, GREY, "middle", style="italic")
    s += text(120, 150, "✗ нічого не", 11, RED, "start", "bold")
    s += text(120, 166, "приєднано", 11, RED, "start", "bold")
    s += circle(150, 210, 5, "none", RED, 2)
    pts = [(150, 210), (185, 196), (205, 224), (232, 188), (258, 226), (284, 194), (312, 216), (340, 200)]
    s += poly(pts, GREY, 2, dash="3,2")
    s += text(245, 256, "наводки з ефіру / сусідніх доріжок", 9.5, GREY, "middle", style="italic")
    s += arrow(340, 200, 430, 210, INK, 2.4)
    s += rect(430, 175, 150, 70, "#fbfcff", INK, 2, 10)
    s += f'<polygon points="455,192 455,228 505,210" fill="{LBLUE}" stroke="{BLUE}" stroke-width="2"/>\n'
    s += text(518, 214, "вхід", 10, INK, "start")
    s += arrow(580, 210, 660, 210, INK, 2.4)
    s += rect(660, 182, 180, 58, LRED, RED, 1.6, 8)
    s += text(750, 206, "0? 1? 0? 1?", 15, RED, "middle", "bold")
    s += text(750, 226, "читається випадково", 8.7, INK, "middle")
    s += rect(140, 300, 620, 84, LAMB, GOLD, 1.6, 10)
    s += text(450, 324, "Високоомний вхід сам рівня не має. Якщо його ніхто не тримає,", 12, INK, "middle", "bold")
    s += text(450, 346, "ніжка плаває біля середини шкали — у тій самій «забороненій зоні» з §22.3,", 10.5, INK, "middle")
    s += text(450, 368, "і дрібна наводка перекидає рішення 0↔1. Цю біду й прибирають підтяжкою.", 10.5, GREY, "middle", style="italic")
    save("fig-22-4-1-floating.svg", s)


# ── Рис. 22.4.2 — pull-up і pull-down ────────────────────────────────────────
def fig42_pullup_pulldown():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 32, "Підтяжки: резистор задає рівень спокою", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "pull-up тримає лінію в HIGH; pull-down — у LOW. Тепер ніжка не плаває", 12, GREY, "middle", style="italic")
    s += rect(40, 84, 400, 320, "none", FAINT, 1.6, 12)
    s += text(240, 110, "Pull-up (підтяжка вгору)", 13, INK, "middle", "bold")
    s += line(120, 150, 360, 150, RED, 2.4)
    s += text(120, 142, "VDD", 10, RED, "start", "bold")
    s += _res_v(160, 150, 250)
    s += text(176, 204, "R", 11, "#8a6a14", "start", "bold")
    s += circle(160, 250, 4, INK, INK, 0)
    s += line(160, 250, 330, 250, INK, 2.4)
    s += circle(330, 250, 5, "none", INK, 2)
    s += text(336, 254, "ніжка", 10, INK, "start", "bold")
    s += rect(120, 300, 200, 44, LBLUE, BLUE, 1.4, 8)
    s += text(220, 327, "спокій → HIGH (1)", 12, BLUE, "middle", "bold")
    s += text(240, 374, "ніщо не тягне вниз → R підтягує до VDD", 9.3, GREY, "middle")
    s += rect(460, 84, 400, 320, "none", FAINT, 1.6, 12)
    s += text(660, 110, "Pull-down (підтяжка вниз)", 13, INK, "middle", "bold")
    s += circle(560, 160, 5, "none", INK, 2)
    s += text(554, 164, "ніжка", 10, INK, "end", "bold")
    s += line(560, 160, 750, 160, INK, 2.4)
    s += circle(750, 160, 4, INK, INK, 0)
    s += _res_v(750, 160, 320)
    s += text(766, 244, "R", 11, "#8a6a14", "start", "bold")
    s += line(660, 320, 840, 320, BLUE, 2.4)
    s += text(660, 340, "GND", 10, BLUE, "start", "bold")
    s += rect(510, 250, 190, 44, LGRN, GREEN, 1.4, 8)
    s += text(605, 277, "спокій → LOW (0)", 12, GREEN, "middle", "bold")
    s += text(660, 374, "ніщо не тягне вгору → R стягує до GND", 9.3, GREY, "middle")
    save("fig-22-4-2-pullup-pulldown.svg", s)


# ── Рис. 22.4.3 — кнопка з pull-up ───────────────────────────────────────────
def fig43_button_pullup():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "Класична кнопка з pull-up: натиснуто = 0", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "у спокої R тримає HIGH; кнопка замикає ніжку на GND → LOW", 12, GREY, "middle", style="italic")

    def panel(ox, title2, pressed):
        o = rect(ox, 84, 410, 320, "none", FAINT, 1.6, 12)
        o += text(ox + 205, 110, title2, 12.5, INK, "middle", "bold")
        cx = ox + 150
        o += line(cx - 60, 146, cx + 90, 146, RED, 2.2)
        o += text(cx - 60, 138, "VDD", 10, RED, "start", "bold")
        o += _res_v(cx, 146, 224)
        o += text(cx + 16, 190, "R (pull-up)", 9, "#8a6a14", "start", "bold")
        o += circle(cx, 224, 4, INK, INK, 0)
        o += line(cx, 224, cx + 130, 224, INK, 2.2)
        o += circle(cx + 130, 224, 5, "none", INK, 2)
        o += text(cx + 136, 228, "ніжка", 9.5, INK, "start", "bold")
        o += line(cx, 224, cx, 280, INK, 2)
        if pressed:
            o += line(cx, 280, cx, 316, GREEN, 2.6)
            o += text(cx + 28, 302, "замкнено", 9.5, GREEN, "start", "bold")
        else:
            o += line(cx - 16, 286, cx + 18, 278, INK, 2)
            o += text(cx + 28, 290, "розімкнено", 9.5, GREY, "start")
            o += line(cx, 296, cx, 316, INK, 2)
        o += line(cx - 60, 316, cx + 90, 316, BLUE, 2.2)
        o += text(cx - 60, 336, "GND", 10, BLUE, "start", "bold")
        lvl, lc, lf = ("LOW (0)", GREEN, LGRN) if pressed else ("HIGH (1)", BLUE, LBLUE)
        o += rect(ox + 252, 150, 140, 54, lf, lc, 1.6, 8)
        o += text(ox + 322, 172, "читаємо:", 9.5, INK, "middle")
        o += text(ox + 322, 192, lvl, 13, lc, "middle", "bold")
        return o

    s += panel(30, "Кнопка відпущена", False)
    s += panel(480, "Кнопка натиснута", True)
    s += text(460, 426, "Контрінтуїтивно, та логічно: спокій = 1, натиск = 0 (active-low).", 11.5, INK, "middle", "bold")
    save("fig-22-4-3-button-pullup.svg", s)


# ── Рис. 22.4.4 — вибір номіналу ─────────────────────────────────────────────
def fig44_resistor_value():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 32, "Який номінал підтяжки: компроміс струму й надійності", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "замала — палить струм; завелика — кволо тягне й ловить шум; ~10 кОм — золота середина", 11, GREY, "middle", style="italic")
    cards = [
        (60, "Замала R", "напр. 1 кОм", LRED, RED,
         ["+ міцно тримає рівень", "+ швидша (мала ємність)", "− багато струму в LOW", "  3.3 В / 1 кОм = 3.3 мА"]),
        (340, "Саме те", "~10 кОм (типово)", LGRN, GREEN,
         ["+ розумний струм", "  3.3 В / 10 кОм = 0.33 мА", "+ надійний рівень", "= баланс для більшості"]),
        (620, "Завелика R", "напр. 1 МОм", LBLUE, BLUE,
         ["+ майже не споживає", "− кволо тягне, повільно", "− чутлива до витоку/шуму", "  вхід може «плисти»"]),
    ]
    for ox, t, sub, fill, col, lines in cards:
        s += rect(ox, 92, 250, 250, fill, col, 1.8, 12)
        s += text(ox + 125, 122, t, 15, col, "middle", "bold")
        s += text(ox + 125, 144, sub, 11, INK, "middle")
        y = 180
        for ln in lines:
            s += text(ox + 18, y, ln, 10.5, INK, "start")
            y += 26
    s += text(W / 2, 372, "Правило: бери найбільший R, що ще певно тримає рівень на твоїй швидкості — економніше.", 11, INK, "middle", "bold")
    s += text(W / 2, 392, "Для звичайної кнопки 10 кОм — майже завжди добре.", 10, GREY, "middle")
    save("fig-22-4-4-resistor-value.svg", s)


# ── Рис. 22.4.5 — внутрішня підтяжка ─────────────────────────────────────────
def fig45_internal_pullup():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 32, "Внутрішня підтяжка: резистор уже всередині чипа", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "вмикається бітом (INPUT_PULLUP) — зовнішній резистор часто не потрібен", 12, GREY, "middle", style="italic")
    s += rect(80, 90, 470, 300, "none", BLUE, 2, 14)
    s += text(110, 114, "мікроконтролер (ESP32)", 11.5, BLUE, "start", "bold")
    s += line(150, 150, 480, 150, RED, 2.2)
    s += text(150, 142, "VDD (внутр.)", 10, RED, "start", "bold")
    s += _res_v(250, 150, 214)
    s += text(266, 186, "R ≈ 45 кОм", 9.5, "#8a6a14", "start", "bold")
    s += fet(218, 214, 64, 46, "ключ", "on")
    s += text(292, 232, "вмик. бітом", 9, GREEN, "start", "bold")
    s += text(292, 246, "(INPUT_PULLUP)", 8.5, GREY, "start")
    s += line(250, 260, 250, 300, INK, 2)
    s += circle(250, 300, 4, INK, INK, 0)
    s += f'<polygon points="320,286 320,316 360,301 320,286" fill="{LBLUE}" stroke="{BLUE}" stroke-width="2"/>\n'
    s += line(250, 300, 320, 300, INK, 2)
    s += text(366, 304, "→ ядро", 9.5, INK, "start")
    s += line(250, 300, 250, 350, INK, 2)
    s += rect(238, 350, 24, 14, METAL, INK, 1.4, 2)
    s += line(250, 364, 250, 386, INK, 2)
    s += circle(250, 386, 4, INK, INK, 0)
    s += text(268, 380, "ніжка (пад)", 9, INK, "start")
    s += rect(600, 90, 270, 300, "none", FAINT, 1.6, 12)
    s += text(735, 116, "Що це дає", 12.5, INK, "middle", "bold")
    s += text(616, 150, "✓ менше деталей на платі", 10.5, GREEN, "start")
    s += text(616, 176, "✓ менше місця й пайки", 10.5, GREEN, "start")
    s += text(616, 202, "✓ вмикаєш/вимикаєш кодом", 10.5, GREEN, "start")
    s += text(616, 238, "Але: внутрішня — «слабка»", 10.5, INK, "start", "bold")
    s += text(616, 260, "(~45 кОм), тож для довгих,", 10, INK, "start")
    s += text(616, 278, "швидких чи шумних ліній", 10, INK, "start")
    s += text(616, 296, "усе одно беруть зовнішню.", 10, INK, "start")
    s += text(735, 332, "Зовні лишається тільки кнопка", 9.7, GREY, "middle", style="italic")
    s += text(735, 350, "до GND — без резистора.", 9.7, GREY, "middle", style="italic")
    save("fig-22-4-5-internal-pullup.svg", s)


# ── Рис. 22.4.6 — підтяжки на ESP32: винятки ─────────────────────────────────
def fig46_esp32_pins():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 32, "Підтяжки на ESP32: не всі ніжки однакові", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "більшість GPIO мають внутрішні pull-up/down — та є важливі винятки", 12, GREY, "middle", style="italic")
    rows = [
        ("Звичайні GPIO", "є внутрішні pull-up і pull-down — вмикай кодом (INPUT_PULLUP / INPUT_PULLDOWN)", LGRN, GREEN, "OK"),
        ("Тільки-вхід: GPIO34, 35, 36(VP), 39(VN)", "НЕМАЄ внутрішніх підтяжок і виходу — лише зовнішній резистор", LRED, RED, "X"),
        ("Strapping-піни: GPIO0, 2, 5, 12, 15", "підтяжка тут впливає на режим завантаження — чіпляй обережно", LAMB, GOLD, "!"),
    ]
    y = 96
    for title2, body, fill, col, mark in rows:
        s += rect(60, y, 820, 92, fill, col, 1.8, 12)
        s += circle(104, y + 46, 22, "#ffffff", col, 2)
        s += text(104, y + 53, mark, 16, col, "middle", "bold")
        s += text(150, y + 40, title2, 14, INK, "start", "bold")
        s += text(150, y + 66, body, 11.3, INK, "start")
        y += 104
    save("fig-22-4-6-esp32-pins.svg", s)


# ── Рис. 22.5.1 — осцилограма дребезгу ───────────────────────────────────────
def fig51_bounce_scope():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 32, "Дребезг контактів: один натиск — пачка перемикань", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "механічні контакти, стикаючись, кілька разів відскакують, перш ніж завмерти", 12, GREY, "middle", style="italic")
    x0, x1 = 110, 860
    yH1, yL1 = 110, 160
    s += text(60, 100, "Намір", 12, GREEN, "start", "bold")
    s += line(x0, yH1, 400, yH1, GREEN, 2.6)
    s += line(400, yH1, 400, yL1, GREEN, 2.6)
    s += line(400, yL1, x1, yL1, GREEN, 2.6)
    s += text(x0, yH1 - 8, "HIGH (відпущено)", 9, GREY, "start")
    s += text(404, yL1 + 26, "один чистий перепад", 9.5, GREEN, "start", "bold")
    yH2, yL2 = 250, 320
    s += text(60, 240, "Реальність", 12, RED, "start", "bold")
    s += line(x0, yH2, 400, yH2, RED, 2.6)
    bounce = [(400, yH2), (400, yL2), (414, yL2), (414, yH2), (430, yH2), (430, yL2),
              (446, yL2), (446, yH2), (462, yH2), (462, yL2), (484, yL2), (484, yH2),
              (500, yH2), (500, yL2), (520, yL2)]
    s += poly(bounce, RED, 2.4)
    s += line(520, yL2, x1, yL2, RED, 2.6)
    s += line(400, 350, 520, 350, INK, 1.6)
    s += line(400, 345, 400, 355, INK, 1.6)
    s += line(520, 345, 520, 355, INK, 1.6)
    s += text(460, 370, "дребезг ~1–10 мс (буває й більше)", 10, INK, "middle", "bold")
    s += text(690, yL2 + 26, "далі — стабільний LOW", 9.5, RED, "start")
    save("fig-22-5-1-bounce-scope.svg", s)


# ── Рис. 22.5.2 — чому це біда ───────────────────────────────────────────────
def fig52_why_bad():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Чому це біда: один натиск порахується як багато", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "кожен відскік — окремий «перепад», і код, що рахує перепади, збивається", 12, GREY, "middle", style="italic")
    x0, yb = 90, 150
    edges = [120, 150, 180, 210, 240]
    s += line(x0, yb, 280, yb, RED, 2)
    for i, ex in enumerate(edges):
        s += line(ex, yb, ex, yb - 40, RED, 2)
        s += arrow(ex, yb - 40, ex, yb - 56, RED, 1.8)
        s += text(ex, yb - 62, str(i + 1), 9, RED, "middle", "bold")
    s += text(180, yb + 24, "5 відскоків = 5 «натисків»", 10.5, RED, "middle", "bold")
    s += rect(360, 110, 230, 90, LGRN, GREEN, 1.8, 12)
    s += text(475, 138, "Чого хотіли", 12, GREEN, "middle", "bold")
    s += text(475, 178, "лічильник: 1", 18, GREEN, "middle", "bold")
    s += rect(630, 110, 230, 90, LRED, RED, 1.8, 12)
    s += text(745, 138, "Що сталося", 12, RED, "middle", "bold")
    s += text(745, 178, "лічильник: 5", 18, RED, "middle", "bold")
    s += rect(150, 250, 600, 112, LAMB, GOLD, 1.6, 10)
    s += text(450, 278, "Симптоми дребезгу в проєкті:", 12, INK, "middle", "bold")
    s += text(175, 304, "• меню «перестрибує» через пункт", 10.5, INK, "start")
    s += text(175, 326, "• лічильник натисків біжить уперед", 10.5, INK, "start")
    s += text(175, 348, "• світло вмикається через раз", 10.5, INK, "start")
    s += text(475, 304, "• «вмк/вимк» поводиться хаотично", 10.5, INK, "start")
    s += text(475, 326, "• подвійні спрацювання на один натиск", 10.5, INK, "start")
    s += text(475, 348, "• важко відтворити — «то є, то нема»", 10.5, INK, "start")
    save("fig-22-5-2-why-bad.svg", s)


# ── Рис. 22.5.3 — RC-фільтр + Шмітт ──────────────────────────────────────────
def fig53_rc_filter():
    W, H = 940, 440
    s = header(W, H)
    s += text(W / 2, 32, "Апаратне придушення: RC-фільтр + тригер Шмітта", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "конденсатор згладжує відскоки, а Шмітт робить із пологого фронту чистий перепад", 11.5, GREY, "middle", style="italic")
    s += rect(40, 84, 360, 320, "none", FAINT, 1.6, 12)
    cx = 150
    s += line(cx - 50, 120, cx + 60, 120, RED, 2.2)
    s += text(cx - 50, 112, "VDD", 10, RED, "start", "bold")
    s += _res_v(cx, 120, 190)
    s += text(cx + 14, 158, "R", 10, "#8a6a14", "start", "bold")
    s += circle(cx, 190, 4, INK, INK, 0)
    s += line(cx, 190, cx + 150, 190, INK, 2.2)
    s += text(cx + 156, 194, "→ Шмітт", 9, INK, "start", "bold")
    s += line(cx, 190, cx, 238, INK, 2)
    s += line(cx - 16, 238, cx + 16, 238, INK, 2.6)
    s += line(cx - 16, 248, cx + 16, 248, INK, 2.6)
    s += text(cx - 24, 250, "C", 10, BLUE, "end", "bold")
    s += line(cx, 248, cx, 300, INK, 2)
    s += circle(cx + 80, 190, 3.5, INK, INK, 0)
    s += line(cx + 80, 190, cx + 80, 250, INK, 2)
    s += line(cx + 64, 256, cx + 96, 248, INK, 2)
    s += line(cx + 80, 262, cx + 80, 300, INK, 2)
    s += text(cx + 88, 240, "кнопка", 9, INK, "start")
    s += line(cx - 50, 300, cx + 150, 300, BLUE, 2.2)
    s += text(cx - 50, 320, "GND", 10, BLUE, "start", "bold")
    s += text(cx + 30, 362, "τ = R·C ≈ кілька мс", 10.5, INK, "middle", "bold")
    s += text(cx + 30, 380, "(довше за дребезг)", 9, GREY, "middle")
    bx = 440

    def wf(y, label, col):
        o = text(bx - 10, y - 34, label, 11, col, "start", "bold")
        o += line(bx, y, bx + 440, y, FAINT, 1)
        return o

    yb = 150
    s += wf(yb, "1) до фільтра — дребезг", RED)
    bb = [(bx, yb - 24), (bx + 60, yb - 24), (bx + 60, yb), (bx + 72, yb), (bx + 72, yb - 24),
          (bx + 88, yb - 24), (bx + 88, yb), (bx + 104, yb), (bx + 104, yb - 24),
          (bx + 120, yb - 24), (bx + 120, yb), (bx + 440, yb)]
    s += poly(bb, RED, 2)
    yr = 252
    s += wf(yr, "2) після RC — згладжений спад", BLUE)
    rr = [(bx, yr - 24), (bx + 60, yr - 24), (bx + 160, yr - 2), (bx + 440, yr)]
    s += poly(rr, BLUE, 2.2)
    yc = 354
    s += wf(yc, "3) після Шмітта — чистий перепад", GREEN)
    cc = [(bx, yc - 24), (bx + 110, yc - 24), (bx + 110, yc), (bx + 440, yc)]
    s += poly(cc, GREEN, 2.4)
    save("fig-22-5-3-rc-filter.svg", s)


# ── Рис. 22.5.4 — SR-засувка ─────────────────────────────────────────────────
def fig54_sr_latch():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 32, "Ідеальне залізо: SR-засувка з перекидним перемикачем", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "перекидний контакт + засувка «запам'ятовують» перший дотик і не зважають на відскоки", 11, GREY, "middle", style="italic")
    s += circle(120, 225, 4, INK, INK, 0)
    s += text(66, 229, "спіл.", 9, INK, "start")
    s += line(120, 225, 200, 162, INK, 2.4)
    s += circle(200, 150, 5, "none", INK, 2)
    s += text(206, 150, "A", 11, INK, "start", "bold")
    s += circle(200, 300, 5, "none", INK, 2)
    s += text(206, 304, "B", 11, INK, "start", "bold")
    s += line(200, 110, 320, 110, RED, 2)
    s += text(200, 102, "VDD", 9, RED, "start", "bold")
    s += _res_v(240, 110, 150)
    s += _res_v(280, 110, 300)
    s += text(90, 380, "GND", 9, BLUE, "start", "bold")
    s += line(90, 360, 160, 360, BLUE, 2)
    s += line(120, 225, 120, 360, INK, 2)

    def nand(x, y):
        o = rect(x, y, 72, 50, "#fbfcff", INK, 1.8, 6)
        o += circle(x + 80, y + 25, 5, "#ffffff", INK, 1.6)
        o += text(x + 36, y + 30, "І-НЕ", 11, INK, "middle", "bold")
        return o

    s += nand(420, 150)
    s += nand(420, 250)
    s += line(200, 150, 420, 165, INK, 1.8)
    s += line(200, 300, 420, 285, INK, 1.8)
    s += line(505, 175, 545, 175, INK, 1.8)
    s += line(545, 175, 545, 322, INK, 1.8)
    s += line(545, 322, 412, 290, INK, 1.8)
    s += line(505, 275, 565, 275, INK, 1.8)
    s += line(565, 275, 565, 138, INK, 1.8)
    s += line(565, 138, 412, 160, INK, 1.8)
    s += line(505, 175, 620, 175, GREEN, 2.4)
    s += text(626, 179, "Q (чистий)", 11, GREEN, "start", "bold")
    s += rect(655, 235, 240, 128, LGRN, GREEN, 1.6, 10)
    s += text(775, 261, "Чому без дребезгу:", 11.5, INK, "middle", "bold")
    s += text(671, 285, "контакт торкнувся A —", 10, INK, "start")
    s += text(671, 303, "засувка стала в Q=1 і тримає.", 10, INK, "start")
    s += text(671, 327, "Відскоки від A нічого не міняють:", 10, INK, "start")
    s += text(671, 345, "полюса B контакт не торкався.", 10, INK, "start")
    save("fig-22-5-4-sr-latch.svg", s)


# ── Рис. 22.5.5 — програмно: зачекати й перечитати ───────────────────────────
def fig55_sw_wait():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "Програмно: побачив зміну — зачекай і перечитай", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "пропусти час дребезгу й перевір рівень ще раз: стабільний — приймай", 12, GREY, "middle", style="italic")
    steps = [
        (70, "1. Помітили", "зміну рівня", LBLUE, BLUE),
        (282, "2. Зачекати", "~20 мс", LAMB, GOLD),
        (494, "3. Перечитати", "рівень", LBLUE, BLUE),
        (706, "4. Той самий?", "приймаємо", LGRN, GREEN),
    ]
    for x, l1, l2, fill, col in steps:
        s += rect(x, 108, 150, 78, fill, col, 1.8, 12)
        s += text(x + 75, 142, l1, 11.5, INK, "middle", "bold")
        s += text(x + 75, 164, l2, 11.5, INK, "middle", "bold")
    for x in (228, 440, 652):
        s += arrow(x, 147, x + 50, 147, INK, 2.2)
    s += text(70, 248, "На осі часу:", 11, INK, "start", "bold")
    yb = 300
    s += line(90, yb, 860, yb, INK, 1.6)
    bb = [(180, yb), (180, yb - 30), (192, yb - 30), (192, yb), (206, yb), (206, yb - 30),
          (222, yb - 30), (222, yb), (240, yb), (240, yb - 30), (300, yb - 30)]
    s += poly(bb, RED, 2)
    s += line(300, yb - 30, 760, yb - 30, GREEN, 2.4)
    s += text(120, yb - 40, "натиск", 9, INK, "start")
    s += line(180, yb + 6, 300, yb + 6, GREY, 1.4)
    s += text(240, yb + 22, "дребезг", 9, RED, "middle")
    s += line(480, yb - 30, 480, yb + 42, BLUE, 1.6, dash="4,3")
    s += text(480, yb + 58, "перечитуємо тут (через ~20 мс) → стабільно", 9.5, BLUE, "middle", "bold")
    save("fig-22-5-5-sw-wait.svg", s)


# ── Рис. 22.5.6 — програмно: N однакових відліків ────────────────────────────
def fig56_sw_counter():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 32, "Програмно надійніше: N однакових відліків поспіль", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "опитуй щокілька мс; зміну приймай, лише коли рівень тримається стабільно", 11.5, GREY, "middle", style="italic")
    x0, x1 = 110, 860
    yH, yL = 120, 180
    s += text(64, 110, "вхід", 10, INK, "start", "bold")
    inb = [(x0, yH), (250, yH), (250, yL), (266, yL), (266, yH), (284, yH), (284, yL),
           (310, yL), (310, yH), (330, yH), (330, yL), (820, yL)]
    s += poly(inb, RED, 2.2)
    s += text(64, 250, "відліки", 10, INK, "start", "bold")
    for sx in range(150, 820, 26):
        s += line(sx, 235, sx, 245, GREY, 1.4)
    s += line(x0, 300, x1, 300, INK, 1.4)
    s += text(64, 296, "лічильник", 9.5, INK, "start")
    cb = [(150, 300), (250, 300), (258, 300), (258, 288), (266, 300), (284, 288), (284, 300),
          (330, 300), (356, 290), (382, 280), (408, 270), (434, 262)]
    s += poly(cb, BLUE, 2)
    s += line(434, 262, 434, 300, BLUE, 1.2, dash="3,2")
    s += circle(434, 262, 5, LGRN, GREEN, 2)
    s += text(442, 258, "досягнуто N → приймаємо зміну (надійно)", 10, GREEN, "start", "bold")
    s += text(300, 366, "Поки дребезг — лічильник раз у раз скидається; рівень завмер — добирає N і фіксує.", 10.5, INK, "middle", "bold")
    save("fig-22-5-6-sw-counter.svg", s)


def _led_v(x, ytop, ybot, col=GOLD):
    """Світлодіод по вертикалі: анод угорі, катод унизу (струм тече вниз)."""
    o = line(x, ytop, x, ytop + 16, INK, 2)
    o += f'<polygon points="{x-12},{ytop+16} {x+12},{ytop+16} {x},{ytop+36}" fill="{LAMB}" stroke="{INK}" stroke-width="2"/>\n'
    o += line(x - 12, ytop + 36, x + 12, ytop + 36, INK, 2.6)
    o += line(x, ytop + 36, x, ybot, INK, 2)
    o += arrow(x + 13, ytop + 20, x + 26, ytop + 11, col, 1.6)
    o += arrow(x + 15, ytop + 28, x + 28, ytop + 19, col, 1.6)
    return o


def _coil_v(x, ytop, ybot):
    """Котушка індуктивності по вертикалі (горбики праворуч)."""
    o = line(x, ytop, x, ytop + 8, INK, 2)
    n = 4
    seg = (ybot - 8 - (ytop + 8)) / n
    path = f'M {x:.1f} {ytop+8:.1f} '
    for i in range(n):
        y0 = ytop + 8 + i * seg
        path += f'Q {x+16:.1f} {y0+seg/2:.1f} {x:.1f} {y0+seg:.1f} '
    o += f'<path d="{path}" fill="none" stroke="{INK}" stroke-width="2"/>\n'
    o += line(x, ybot - 8, x, ybot, INK, 2)
    return o


# ── Рис. 22.6.1 — source і sink ──────────────────────────────────────────────
def fig61_source_sink():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "Source і sink: ніжка віддає або приймає струм", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "у HIGH вона живить навантаження до GND (source); у LOW приймає його з VDD (sink)", 11.5, GREY, "middle", style="italic")
    s += rect(40, 84, 400, 330, "none", FAINT, 1.6, 12)
    s += text(240, 110, "SOURCE — ніжка ВІДДАЄ струм", 12.5, GREEN, "middle", "bold")
    cx = 180
    s += rect(cx - 60, 140, 120, 50, LBLUE, BLUE, 1.6, 8)
    s += text(cx, 162, "ніжка", 11, INK, "middle", "bold")
    s += text(cx, 180, "HIGH (вгорі вкл.)", 9, BLUE, "middle")
    s += line(cx, 190, cx, 220, INK, 2)
    s += circle(cx, 220, 4, INK, INK, 0)
    s += _led_v(cx, 220, 320)
    s += text(cx + 34, 252, "LED", 10, INK, "start", "bold")
    s += line(cx, 320, cx, 360, INK, 2)
    s += line(cx - 60, 360, cx + 60, 360, BLUE, 2.2)
    s += text(cx - 60, 380, "GND", 10, BLUE, "start", "bold")
    s += arrow(cx + 80, 230, cx + 80, 350, GREEN, 2.2)
    s += text(cx + 86, 296, "I тече з ніжки", 9.5, GREEN, "start")
    s += rect(480, 84, 400, 330, "none", FAINT, 1.6, 12)
    s += text(680, 110, "SINK — ніжка ПРИЙМАЄ струм", 12.5, RED, "middle", "bold")
    dx = 680
    s += line(dx - 60, 150, dx + 60, 150, RED, 2.2)
    s += text(dx - 60, 142, "VDD", 10, RED, "start", "bold")
    s += line(dx, 150, dx, 180, INK, 2)
    s += _led_v(dx, 180, 280)
    s += text(dx + 34, 212, "LED", 10, INK, "start", "bold")
    s += line(dx, 280, dx, 300, INK, 2)
    s += circle(dx, 300, 4, INK, INK, 0)
    s += rect(dx - 60, 300, 120, 50, LGRN, GREEN, 1.6, 8)
    s += text(dx, 322, "ніжка", 11, INK, "middle", "bold")
    s += text(dx, 340, "LOW (внизу вкл.)", 9, GREEN, "middle")
    s += arrow(dx + 80, 160, dx + 80, 300, RED, 2.2)
    s += text(dx + 86, 235, "I тече в ніжку", 9.5, RED, "start")
    save("fig-22-6-1-source-sink.svg", s)


# ── Рис. 22.6.2 — межі струму ────────────────────────────────────────────────
def fig62_limits():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "Скільки струму витримує ніжка: безпечно, межа, пошкодження", 17, INK, "middle", "bold")
    s += text(W / 2, 54, "у ESP32 ніжка тримає ~20 мА у роботі; абсолютна стеля близько 40 мА", 12, GREY, "middle", style="italic")
    x0, x1 = 90, 820
    y = 160
    imax = 50.0
    xv = lambda i: x0 + (i / imax) * (x1 - x0)
    s += rect(x0, y, xv(20) - x0, 60, LGRN, GREEN, 1.6)
    s += rect(xv(20), y, xv(40) - xv(20), 60, LAMB, GOLD, 1.6)
    s += rect(xv(40), y, x1 - xv(40), 60, LRED, RED, 1.6)
    s += text((x0 + xv(20)) / 2, y + 36, "безпечно (≤ ~20 мА)", 11, GREEN, "middle", "bold")
    s += text((xv(20) + xv(40)) / 2, y + 36, "межа (до 40 мА)", 9.5, "#8a6a14", "middle", "bold")
    s += text((xv(40) + x1) / 2, y + 36, "пошкодження", 11, RED, "middle", "bold")
    s += line(x0, y + 60, x1, y + 60, INK, 1.6)
    for i in (0, 10, 20, 30, 40, 50):
        s += line(xv(i), y + 60, xv(i), y + 66, INK, 1.4)
        s += text(xv(i), y + 80, str(i), 9.5, INK, "middle")
    s += text((x0 + x1) / 2, y + 100, "струм через одну ніжку, мА", 10, INK, "middle")
    s += line(xv(20), y - 12, xv(20), y, GREEN, 1.4)
    s += text(xv(20), y - 16, "робоча межа", 9, GREEN, "middle", "bold")
    s += line(xv(40), y - 12, xv(40), y, RED, 1.4)
    s += text(xv(40), y - 16, "абсолютний максимум", 9, RED, "middle", "bold")
    s += rect(120, 300, 660, 96, "none", FAINT, 1.6, 10)
    s += text(450, 326, "Що буде, якщо перевищити:", 12, INK, "middle", "bold")
    s += text(150, 352, "• напруга «просідає» — рівень не втримати", 10.5, INK, "start")
    s += text(150, 374, "• ніжка й чіп гріються — аж до вигоряння", 10.5, INK, "start")
    s += text(498, 352, "• можливий «защіпок» (latch-up)", 10.5, INK, "start")
    s += text(498, 374, "• сумарний струм усіх ніжок теж обмежений!", 10.5, RED, "start")
    save("fig-22-6-2-limits.svg", s)


# ── Рис. 22.6.3 — LED і резистор ─────────────────────────────────────────────
def fig63_led_resistor():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 32, "Резистор біля LED: і яскравість задає, і ніжку береже", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "опір обмежує струм у безпечну для ніжки зону — без нього струм злетів би", 11.5, GREY, "middle", style="italic")
    cx = 230
    s += rect(cx - 60, 108, 120, 48, LBLUE, BLUE, 1.6, 8)
    s += text(cx, 130, "ніжка", 11, INK, "middle", "bold")
    s += text(cx, 148, "HIGH = 3.3 В", 9, BLUE, "middle")
    s += line(cx, 156, cx, 186, INK, 2)
    s += _res_v(cx, 186, 248)
    s += text(cx + 16, 220, "R", 11, "#8a6a14", "start", "bold")
    s += _led_v(cx, 248, 330)
    s += text(cx + 32, 282, "LED", 10, INK, "start", "bold")
    s += line(cx, 330, cx, 358, INK, 2)
    s += line(cx - 60, 358, cx + 60, 358, BLUE, 2.2)
    s += text(cx - 60, 378, "GND", 10, BLUE, "start", "bold")
    s += arrow(cx + 78, 168, cx + 78, 350, GREEN, 2)
    s += text(cx + 84, 262, "I (однаковий усюди)", 9.5, GREEN, "start")
    s += rect(460, 116, 420, 184, "none", FAINT, 1.6, 10)
    s += text(670, 142, "Порахуймо струм", 12.5, INK, "middle", "bold")
    s += text(480, 170, "I = (VDD − Vf) / R", 13, INK, "start", "bold")
    s += text(480, 196, "Vf(LED) ≈ 2.0 В,  VDD = 3.3 В", 11, INK, "start")
    s += text(480, 220, "хочемо I ≈ 10 мА:", 11, INK, "start")
    s += text(480, 246, "R = (3.3 − 2.0) / 0.010 = 130 Ω", 12, GREEN, "start", "bold")
    s += text(480, 270, "беремо 150–220 Ω → ще менший, безпечніший струм", 9.5, GREY, "start")
    s += rect(460, 318, 420, 64, LRED, RED, 1.4, 10)
    s += text(670, 342, "Без резистора струм обмежує лише крихітний", 10, INK, "middle", "bold")
    s += text(670, 362, "опір LED — він злетить за межу й спалить ніжку.", 10, RED, "middle")
    save("fig-22-6-3-led-resistor.svg", s)


# ── Рис. 22.6.4 — транзистор-ключ ────────────────────────────────────────────
def fig64_transistor_driver():
    W, H = 940, 440
    s = header(W, H)
    s += text(W / 2, 32, "Велике навантаження — через транзистор-ключ", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "ніжка дає крихту струму на затвор, а транзистор комутує великий струм мотора/реле", 11, GREY, "middle", style="italic")
    s += rect(60, 200, 110, 48, LBLUE, BLUE, 1.6, 8)
    s += text(115, 222, "ніжка", 11, INK, "middle", "bold")
    s += text(115, 240, "(мА — крихта)", 8.5, GREY, "middle")
    s += line(170, 224, 232, 224, INK, 2)
    s += rect(232, 214, 22, 20, "#ffffff", GOLD, 1.4, 3)
    s += text(243, 208, "Rg", 8.5, "#8a6a14", "middle")
    s += line(254, 224, 312, 224, INK, 2)
    s += rect(312, 190, 110, 110, "#fbfcff", INK, 2, 8)
    s += text(367, 214, "N-MOS", 12, INK, "middle", "bold")
    s += text(367, 232, "(ключ)", 9.5, GREY, "middle")
    s += text(320, 262, "G", 10, INK, "start", "bold")
    s += text(414, 206, "D", 10, INK, "end", "bold")
    s += text(414, 296, "S", 10, INK, "end", "bold")
    s += line(367, 190, 367, 150, INK, 2)
    s += circle(367, 125, 24, "none", INK, 2)
    s += text(367, 131, "M", 14, INK, "middle", "bold")
    s += line(367, 101, 367, 80, INK, 2)
    s += line(290, 80, 450, 80, RED, 2.2)
    s += text(286, 72, "+V (окреме живлення, напр. 12 В)", 10, RED, "start", "bold")
    s += line(367, 300, 367, 350, INK, 2)
    s += line(115, 350, 470, 350, BLUE, 2.2)
    s += text(115, 370, "GND (спільна!)", 10, BLUE, "start", "bold")
    s += line(115, 248, 115, 350, INK, 2)
    s += rect(540, 150, 360, 210, "none", FAINT, 1.6, 10)
    s += text(720, 176, "Чому так:", 12.5, INK, "middle", "bold")
    s += text(558, 204, "• ніжка керує лише ЗАТВОРОМ —", 11, INK, "start")
    s += text(572, 224, "це майже нуль струму", 10.5, GREY, "start")
    s += text(558, 252, "• великий струм іде з ОКРЕМОГО +V", 11, INK, "start")
    s += text(572, 272, "крізь транзистор, оминаючи ніжку", 10.5, GREY, "start")
    s += text(558, 300, "• «маси» (GND) мусять бути спільні", 11, INK, "start")
    s += text(558, 328, "• для індуктивних — ще й діод (далі)", 11, RED, "start")
    save("fig-22-6-4-transistor-driver.svg", s)


# ── Рис. 22.6.5 — флайбек-діод ───────────────────────────────────────────────
def fig65_flyback_diode():
    W, H = 940, 440
    s = header(W, H)
    s += text(W / 2, 32, "Індуктивне навантаження: захисний (флайбек) діод", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "котушка реле/мотор при вимкненні «бризкає» викидом напруги — діод гасить його", 11, GREY, "middle", style="italic")

    def circuit(ox, with_diode):
        o = rect(ox, 84, 360, 330, "none", FAINT, 1.6, 12)
        o += text(ox + 180, 110, "З діодом" if with_diode else "Без діода", 13, (GREEN if with_diode else RED), "middle", "bold")
        cx = ox + 130
        o += line(ox + 40, 140, ox + 300, 140, RED, 2.2)
        o += text(ox + 40, 132, "+V", 10, RED, "start", "bold")
        o += _coil_v(cx, 150, 250)
        o += text(cx - 50, 205, "котушка", 9, INK, "start")
        o += text(cx - 36, 219, "(L)", 9, INK, "start")
        o += circle(cx, 250, 4, INK, INK, 0)
        o += line(cx, 250, cx, 280, INK, 2)
        o += fet(cx - 30, 280, 60, 46, "ключ", "off")
        o += line(cx, 326, cx, 356, INK, 2)
        o += line(ox + 40, 356, ox + 300, 356, BLUE, 2.2)
        o += text(ox + 40, 376, "GND", 10, BLUE, "start", "bold")
        if with_diode:
            dx = cx + 72
            o += line(cx, 250, dx, 250, INK, 2)
            o += line(dx, 250, dx, 232, INK, 2)
            o += f'<polygon points="{dx-10},{232} {dx+10},{232} {dx},{214}" fill="{LBLUE}" stroke="{INK}" stroke-width="2"/>\n'
            o += line(dx - 10, 214, dx + 10, 214, INK, 2.4)
            o += line(dx, 214, dx, 140, INK, 2)
            o += text(dx + 14, 232, "діод", 9, BLUE, "start", "bold")
            o += text(ox + 180, 400, "викид замикається в діод і згасає (~0.7 В)", 9.3, GREEN, "middle", "bold")
        else:
            o += text(cx + 36, 232, "↯ сотні вольт!", 11, RED, "start", "bold")
            o += text(ox + 180, 400, "викид б'є по транзистору — пробій", 9.3, RED, "middle", "bold")
        return o

    s += circuit(40, False)
    s += circuit(520, True)
    save("fig-22-6-5-flyback-diode.svg", s)


# ── Рис. 22.6.6 — захист входу ───────────────────────────────────────────────
def fig66_input_protection():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 32, "Захист входу: послідовний резистор і вбудовані діоди", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "усередині ніжки є діоди-обмежувачі до VDD і GND; зовнішній R обмежує струм аварії", 11, GREY, "middle", style="italic")
    s += rect(40, 180, 110, 48, "none", INK, 1.6, 8)
    s += text(95, 202, "сигнал", 10.5, INK, "middle", "bold")
    s += text(95, 220, "(може стрибнути)", 8, GREY, "middle")
    s += line(150, 204, 200, 204, INK, 2)
    s += rect(200, 194, 62, 20, "#ffffff", GOLD, 1.4, 3)
    s += text(231, 208, "R посл.", 8.5, "#8a6a14", "middle")
    s += line(262, 204, 330, 204, INK, 2)
    s += rect(330, 110, 300, 250, "none", BLUE, 2, 12)
    s += text(480, 132, "усередині ніжки", 11, BLUE, "middle", "bold")
    s += line(390, 150, 560, 150, RED, 2)
    s += text(566, 144, "VDD", 9, RED, "start", "bold")
    s += line(390, 300, 560, 300, BLUE, 2)
    s += text(566, 304, "GND", 9, BLUE, "start", "bold")
    s += line(330, 204, 470, 204, INK, 2)
    s += circle(470, 204, 4, INK, INK, 0)
    s += line(470, 204, 470, 186, INK, 2)
    s += f'<polygon points="462,186 478,186 470,166" fill="{LRED}" stroke="{INK}" stroke-width="2"/>\n'
    s += line(462, 166, 478, 166, INK, 2.4)
    s += line(470, 166, 470, 150, INK, 2)
    s += text(486, 174, "діод до VDD", 8.5, INK, "start")
    s += line(470, 204, 470, 262, INK, 2)
    s += line(462, 262, 478, 262, INK, 2.4)
    s += f'<polygon points="462,282 478,282 470,262" fill="{LBLUE}" stroke="{INK}" stroke-width="2"/>\n'
    s += line(470, 282, 470, 300, INK, 2)
    s += text(486, 274, "діод до GND", 8.5, INK, "start")
    s += line(470, 204, 540, 204, INK, 2)
    s += f'<polygon points="540,190 540,218 575,204" fill="{LBLUE}" stroke="{BLUE}" stroke-width="2"/>\n'
    s += text(556, 236, "буфер", 8.5, INK, "middle")
    s += rect(666, 150, 236, 176, "none", FAINT, 1.6, 10)
    s += text(784, 176, "Як це береже:", 11.5, INK, "middle", "bold")
    s += text(682, 202, "стрибок вище VDD →", 10, INK, "start")
    s += text(682, 220, "верхній діод відводить", 10, INK, "start")
    s += text(682, 238, "його у VDD;", 10, INK, "start")
    s += text(682, 264, "R обмежує струм, щоб", 10, INK, "start")
    s += text(682, 282, "діод не згорів.", 10, INK, "start")
    s += text(682, 308, "Те саме знизу — у GND.", 10, GREY, "start")
    save("fig-22-6-6-input-protection.svg", s)


def _bits(x, y, vals, cell=34, idx0=0, showidx=True):
    """Рядок бітів зліва(старший)→направо; одиниці підсвічено."""
    o = ""
    n = len(vals)
    for i, v in enumerate(vals):
        cx = x + i * cell
        bit_index = idx0 + (n - 1 - i)
        o += rect(cx, y, cell, cell, (LBLUE if v else "#ffffff"), INK, 1.4)
        o += text(cx + cell / 2, y + cell * 0.66, str(v), 15, (BLUE if v else GREY), "middle", "bold")
        if showidx:
            o += text(cx + cell / 2, y + cell + 13, str(bit_index), 8.5, GREY, "middle")
    return o


# ── Рис. 22.7.1 — регістр GPIO_OUT ───────────────────────────────────────────
def fig71_register_bits():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 32, "Регістр GPIO_OUT: один біт — одна ніжка", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "стан усіх ніжок порту лежить у комірці пам'яті; біт n керує ніжкою GPIOn", 12, GREY, "middle", style="italic")
    vals = [0, 0, 1, 0, 0, 1, 0, 0]
    bx = 270
    s += text(bx + 4 * 50, 92, "GPIO_OUT (показано біти 7…0; усього 32)", 10.5, INK, "middle")
    s += _bits(bx, 108, vals, 50, 0)
    s += text(bx - 16, 140, "біт:", 10, INK, "end", "bold")
    s += arrow(bx + 2 * 50 + 25, 162, bx + 2 * 50 + 25, 208, BLUE, 1.8)
    s += text(bx + 2 * 50 + 25, 224, "GPIO5 = 1 (HIGH)", 10, BLUE, "middle", "bold")
    s += arrow(bx + 5 * 50 + 25, 162, bx + 5 * 50 + 25, 208, BLUE, 1.8)
    s += text(bx + 5 * 50 + 25, 224, "GPIO2 = 1 (HIGH)", 10, BLUE, "middle", "bold")
    s += text(W / 2, 282, "Записати «1» у біт n → ніжка GPIOn стає HIGH; «0» → LOW.", 12, INK, "middle", "bold")
    s += text(W / 2, 306, "Прочитати рівень входів — із регістра GPIO_IN (так само побітно).", 10.5, GREY, "middle")
    save("fig-22-7-1-register-bits.svg", s)


# ── Рис. 22.7.2 — digitalWrite vs регістр ────────────────────────────────────
def fig72_digitalwrite_vs_reg():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "digitalWrite зручний, але повільний; регістр — миттєвий", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "обгортка робить багато зайвого; прямий запис у регістр — кілька тактів", 12, GREY, "middle", style="italic")
    s += text(70, 110, "digitalWrite(2, HIGH):", 12, INK, "start", "bold")
    boxes = [("виклик", "функції"), ("знайти регістр", "і біт за № піна"), ("перевірки", "безпеки"), ("запис у", "регістр")]
    bx = 70
    for i, (l1, l2) in enumerate(boxes):
        x = bx + i * 200
        col = GREEN if i == 3 else GREY
        s += rect(x, 130, 170, 56, ("#eef6ef" if i == 3 else "#f2f2f2"), col, 1.6, 8)
        s += text(x + 85, 153, l1, 10.5, INK, "middle", "bold")
        s += text(x + 85, 171, l2, 9, GREY, "middle")
        if i < 3:
            s += arrow(x + 170, 158, x + 200, 158, INK, 2)
    s += text(822, 162, "≈ 1 мкс", 13, RED, "start", "bold")
    s += text(70, 250, "GPIO.out_w1ts = (1<<2):", 12, INK, "start", "bold")
    s += rect(70, 270, 170, 56, "#eef6ef", GREEN, 1.6, 8)
    s += text(155, 293, "запис у", 10.5, INK, "middle", "bold")
    s += text(155, 311, "регістр", 9, GREY, "middle")
    s += text(266, 302, "≈ одиниці–десятки нс  (у десятки разів швидше)", 12, GREEN, "start", "bold")
    s += rect(70, 350, 800, 36, LAMB, GOLD, 1.4, 8)
    s += text(470, 373, "Платиш зручністю за швидкість: для рідких перемикань digitalWrite добрий; для «гарячих» — регістр.", 10.3, INK, "middle", "bold")
    save("fig-22-7-2-digitalwrite-vs-reg.svg", s)


# ── Рис. 22.7.3 — бітові операції ────────────────────────────────────────────
def fig73_bit_ops():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 32, "Бітові маски: увімкнути, вимкнути, перемкнути, прочитати", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "одну ніжку чіпаємо, не зачепивши сусідніх — через маску (1<<n), тут n=3", 12, GREY, "middle", style="italic")

    def demo(x, y, before, after):
        o = _bits(x, y, before, 20, 0, showidx=False)
        o += text(x + 8 * 20 + 12, y + 14, "→", 15, INK, "start", "bold")
        o += _bits(x + 8 * 20 + 30, y, after, 20, 0, showidx=False)
        return o

    rows = [
        ("set", "REG |= (1<<3)", [0, 0, 1, 0, 0, 1, 0, 0], [0, 0, 1, 0, 1, 1, 0, 0], GREEN, "біт3 → 1, решта без змін"),
        ("clear", "REG &= ~(1<<3)", [0, 0, 1, 0, 1, 1, 0, 0], [0, 0, 1, 0, 0, 1, 0, 0], RED, "біт3 → 0, решта без змін"),
        ("toggle", "REG ^= (1<<3)", [0, 0, 1, 0, 0, 1, 0, 0], [0, 0, 1, 0, 1, 1, 0, 0], BLUE, "біт3 міняє стан"),
    ]
    y = 90
    for name, code, bef, aft, col, expl in rows:
        s += rect(50, y, 250, 66, "#fbfcff", col, 1.6, 8)
        s += text(64, y + 28, name, 13, col, "start", "bold")
        s += text(64, y + 52, code, 12, INK, "start", "bold")
        s += demo(330, y + 14, bef, aft)
        s += text(722, y + 38, expl, 10.5, INK, "start")
        y += 84
    s += rect(50, y, 250, 66, "#fbfcff", INK, 1.6, 8)
    s += text(64, y + 28, "read", 13, INK, "start", "bold")
    s += text(64, y + 52, "(GPIO_IN>>3)&1", 12, INK, "start", "bold")
    s += _bits(330, y + 14, [0, 0, 1, 0, 1, 1, 0, 0], 20, 0, showidx=False)
    s += text(330 + 8 * 20 + 14, y + 28, "→ біт3 =", 12, INK, "start", "bold")
    s += text(330 + 8 * 20 + 96, y + 28, "1", 16, GREEN, "start", "bold")
    s += text(722, y + 38, "лишається лише потрібний біт", 10.5, INK, "start")
    save("fig-22-7-3-bit-ops.svg", s)


# ── Рис. 22.7.4 — W1TS / W1TC ────────────────────────────────────────────────
def fig74_w1ts_w1tc():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 32, "Атомарні W1TS / W1TC: без «прочитав-змінив-записав»", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "запис маски прямо встановлює або скидає лише потрібні біти — одним рухом", 12, GREY, "middle", style="italic")
    s += rect(50, 80, 840, 150, "none", RED, 1.6, 12)
    s += text(70, 104, "Небезпека: REG |= mask — це три дії (read-modify-write)", 12, RED, "start", "bold")
    steps = ["1) прочитати REG", "2) АБО з маскою", "3) записати назад"]
    for i, st in enumerate(steps):
        x = 100 + i * 250
        s += rect(x, 120, 180, 46, "#ffffff", GREY, 1.4, 8)
        s += text(x + 90, 148, st, 11, INK, "middle", "bold")
        if i < 2:
            s += arrow(x + 180, 143, x + 250, 143, INK, 2)
    s += text(470, 202, "Якщо між кроками 1 і 3 переривання змінить REG — твій запис ЗАТРЕ ту зміну (гонка).", 10.5, RED, "middle", "bold")
    s += rect(50, 250, 840, 150, "none", GREEN, 1.6, 12)
    s += text(70, 274, "Безпечно: GPIO.out_w1ts = mask — одна атомарна дія", 12, GREEN, "start", "bold")
    s += text(90, 304, "W1TS (write-1-to-set):", 11, INK, "start", "bold")
    s += text(110, 326, "де в масці 1 — той біт стає 1; де 0 — біт без змін.", 10.5, INK, "start")
    s += text(90, 354, "W1TC (write-1-to-clear):", 11, INK, "start", "bold")
    s += text(110, 376, "де в масці 1 — той біт стає 0; де 0 — біт без змін.", 10.5, INK, "start")
    s += text(710, 322, "Залізо саме чіпає лише", 10.5, GREEN, "middle", "bold")
    s += text(710, 340, "потрібні біти — читати", 10.5, GREEN, "middle")
    s += text(710, 358, "нічого не треба.", 10.5, GREEN, "middle")
    save("fig-22-7-4-w1ts-w1tc.svg", s)


# ── Рис. 22.7.5 — кілька ніжок одним записом ─────────────────────────────────
def fig75_multipin():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Кілька ніжок одним записом — синхронно", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "маска міняє багато ніжок в ОДНУ мить; послідовні digitalWrite «розповзаються» в часі", 11.5, GREY, "middle", style="italic")
    pins = ["GPIO2", "GPIO3", "GPIO4", "GPIO5"]
    s += text(70, 96, "4× digitalWrite — по черзі:", 11.5, RED, "start", "bold")
    for i, p in enumerate(pins):
        y = 124 + i * 30
        s += text(64, y + 4, p, 8.5, INK, "end")
        xr = 180 + i * 60
        s += line(120, y, xr, y, GREY, 2)
        s += line(xr, y, xr, y - 16, RED, 2)
        s += line(xr, y - 16, 430, y - 16, RED, 2)
    s += text(290, 268, "фронти зсунуті (кожен ~1 мкс пізніше) — НЕ синхронні", 9.5, RED, "middle", "bold")
    s += text(540, 96, "1× запис маски — разом:", 11.5, GREEN, "start", "bold")
    xr = 700
    for i, p in enumerate(pins):
        y = 124 + i * 30
        s += text(534, y + 4, p, 8.5, INK, "end")
        s += line(560, y, xr, y, GREY, 2)
        s += line(xr, y, xr, y - 16, GREEN, 2)
        s += line(xr, y - 16, 870, y - 16, GREEN, 2)
    s += line(xr, 112, xr, 256, GREEN, 1.4, dash="4,3")
    s += text(700, 268, "усі фронти на одній лінії часу — синхронно", 9.5, GREEN, "middle", "bold")
    s += rect(110, 300, 720, 58, LAMB, GOLD, 1.4, 8)
    s += text(470, 324, "GPIO.out_w1ts = (1<<2)|(1<<3)|(1<<4)|(1<<5);  // чотири ніжки HIGH однією дією", 10.3, INK, "middle", "bold")
    s += text(470, 345, "Критично для паралельних шин, кроку моторів, точних фронтів.", 10, GREY, "middle")
    save("fig-22-7-5-multipin.svg", s)


# ── Рис. 22.7.6 — карта GPIO-регістрів ESP32 ─────────────────────────────────
def fig76_esp32_gpio_regs():
    W, H = 940, 440
    s = header(W, H)
    s += text(W / 2, 32, "Карта GPIO-регістрів ESP32 (memory-mapped, §20.3)", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "кожен регістр — комірка з фіксованою адресою; ніжки 0–31 і 32–39 у різних регістрах", 11.5, GREY, "middle", style="italic")
    rows = [
        ("GPIO_OUT / GPIO_OUT1", "стан виходів (читати/писати)", "OUT: 0–31 · OUT1: 32–39", BLUE),
        ("GPIO_OUT_W1TS / _W1TC", "атомарно встановити / скинути біти", "set і clear без read-modify-write", GREEN),
        ("GPIO_ENABLE / _ENABLE1", "напрям ніжки: вихід чи вхід", "1 = вихід увімкнено", GOLD),
        ("GPIO_IN / GPIO_IN1", "читати рівні входів", "IN: 0–31 · IN1: 32–39", INK),
    ]
    y = 92
    for name, purpose, who, col in rows:
        s += rect(60, y, 820, 68, "#fbfcff", col, 1.6, 10)
        s += text(80, y + 30, name, 13, col, "start", "bold")
        s += text(80, y + 54, purpose, 11, INK, "start")
        s += text(610, y + 38, who, 10, GREY, "start")
        y += 78
    s += text(W / 2, y + 20, "Звертаються через GPIO.out_w1ts = …, REG_WRITE(addr, val) або (в IDF) gpio_set_level().", 10, INK, "middle", "bold")
    save("fig-22-7-6-esp32-gpio-regs.svg", s)


# ── Рис. 22.8.1 — модуль як чорна скринька ───────────────────────────────────
def fig81_module_blackbox():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Модуль як «чорна скринька»: думай про піни, не про нутрощі", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "будь-яку периферію зручно бачити як коробку з кількома виводами й відомою поведінкою", 11, GREY, "middle", style="italic")
    s += rect(120, 120, 260, 200, "#fbfcff", INK, 2, 12)
    s += text(250, 150, "МОДУЛЬ", 14, INK, "middle", "bold")
    s += text(250, 170, "(давач / периферія)", 10, GREY, "middle")
    s += text(250, 222, "усередині:", 10, GREY, "middle")
    s += text(250, 242, "транзистори? чіп?", 11, INK, "middle", "bold")
    s += text(250, 260, "— нам байдуже", 10, GREY, "middle", style="italic")
    s += line(120, 180, 70, 180, RED, 2.2)
    s += text(64, 184, "VCC", 10, RED, "end", "bold")
    s += line(120, 300, 70, 300, BLUE, 2.2)
    s += text(64, 304, "GND", 10, BLUE, "end", "bold")
    s += circle(380, 210, 4, INK, INK, 0)
    s += text(386, 200, "OUT (сигнал)", 10, INK, "start", "bold")
    s += arrow(384, 210, 560, 210, INK, 2.4)
    s += text(472, 200, "у вхід", 9, GREY, "middle")
    s += rect(560, 150, 260, 140, "none", BLUE, 2, 12)
    s += text(690, 178, "мікроконтролер", 12, BLUE, "middle", "bold")
    s += text(690, 230, "читає один біт:", 10, INK, "middle")
    s += text(690, 250, "є сигнал / нема", 11, INK, "middle", "bold")
    s += rect(150, 344, 600, 44, LAMB, GOLD, 1.4, 8)
    s += text(450, 368, "Та сама абстракція, що з функціями в коді чи регістрами (§20.3): нутрощі сховані за інтерфейсом.", 10.2, INK, "middle", "bold")
    save("fig-22-8-1-module-blackbox.svg", s)


# ── Рис. 22.8.2 — чотири питання ─────────────────────────────────────────────
def fig82_four_questions():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 32, "Чотири питання, щоб підмкнути будь-який модуль", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "відповіси на них — і з'єднання працюватиме; пропустиш — ловитимеш «загадки»", 11.5, GREY, "middle", style="italic")
    cards = [
        (40, "1 · Живлення", "Яка напруга — 3.3 чи 5 В?", ["сумісність рівнів (§22.3);", "ESP32 не 5-В-терпимий"], RED),
        (270, "2 · Напрям", "Жене сам чи «відпускає»?", ["push-pull → прямо;", "перемикач → підтяжка (§22.4)"], BLUE),
        (500, "3 · Логіка", "Активний рівень — 1 чи 0?", ["active-high / active-low;", "як читати в коді (§22.4)"], GREEN),
        (730, "4 · Захист", "Струми й пороги в нормі?", ["послідовний R, межі струму,", "діоди (§22.3, §22.6)"], GOLD),
    ]
    for ox, t, q, note, col in cards:
        s += rect(ox, 90, 210, 250, "#fbfcff", col, 1.8, 12)
        s += text(ox + 105, 120, t, 13, col, "middle", "bold")
        s += line(ox + 16, 134, ox + 194, 134, col, 1.2)
        s += text(ox + 105, 164, q, 10, INK, "middle", "bold")
        yy = 212
        for ln in note:
            s += text(ox + 105, yy, ln, 9.2, GREY, "middle")
            yy += 18
    s += text(W / 2, 372, "Спільна земля (GND) — завжди обов'язкова (§22.6). Без неї модуль і МК не «бачать» одне одного.", 11, INK, "middle", "bold")
    save("fig-22-8-2-four-questions.svg", s)


# ── Рис. 22.8.3 — дискретний давач ───────────────────────────────────────────
def fig83_discrete_sensor():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 32, "Дискретний (двійковий) давач: лише два стани", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "його вихід — один біт «є подія / нема», як у кнопки, лише замикає не палець, а явище", 11, GREY, "middle", style="italic")
    for name, x in [("рух (PIR)", 130), ("геркон", 310), ("кінцевик", 490), ("ІЧ-перешкода", 680)]:
        s += rect(x - 72, 88, 144, 56, "#fbfcff", INK, 1.6, 10)
        s += text(x, 114, name, 11, INK, "middle", "bold")
        s += text(x, 132, "0 або 1", 9, GREY, "middle")
    s += text(W / 2, 176, "усі видають лише два рівні — на відміну від аналогових давачів (далі в модулі)", 10, GREY, "middle", style="italic")
    x0, x1, yH, yL = 120, 780, 222, 272
    s += text(64, 250, "OUT", 10, INK, "start", "bold")
    seg = [(x0, yL), (240, yL), (240, yH), (420, yH), (420, yL), (560, yL), (560, yH), (700, yH), (700, yL), (x1, yL)]
    s += poly(seg, GREEN, 2.6)
    s += text(330, yH - 8, "є подія (HIGH)", 9, GREEN, "middle")
    s += text(180, yL + 18, "спокій (LOW)", 9, GREY, "middle")
    s += text(W / 2, 332, "Прошивка читає його як звичайний цифровий вхід — з усім, що ми вивчили: пороги, підтяжка, дребезг.", 10.3, INK, "middle", "bold")
    save("fig-22-8-3-discrete-sensor.svg", s)


# ── Рис. 22.8.4 — давач-перемикач + підтяжка ─────────────────────────────────
def fig84_connect_switch_sensor():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "Давач-«перемикач»: підтяжка + логіка active-low", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "якщо модуль лише замикає лінію на GND (open-collector / контакт) — потрібна підтяжка", 11, GREY, "middle", style="italic")
    s += line(120, 120, 600, 120, RED, 2.2)
    s += text(120, 112, "VCC = 3.3 В", 10, RED, "start", "bold")
    s += _res_v(300, 120, 190)
    s += text(316, 160, "pull-up (можна внутрішню)", 9, "#8a6a14", "start", "bold")
    s += circle(300, 190, 4, INK, INK, 0)
    s += line(300, 190, 470, 190, INK, 2.2)
    s += rect(470, 150, 200, 90, "none", BLUE, 2, 10)
    s += text(570, 176, "вхід МК", 11, BLUE, "middle", "bold")
    s += text(570, 200, "INPUT_PULLUP", 9, GREY, "middle")
    s += text(570, 222, "чекаємо LOW", 10, INK, "middle", "bold")
    s += line(300, 190, 300, 262, INK, 2)
    s += rect(250, 262, 100, 58, "#fbfcff", INK, 1.6, 8)
    s += text(300, 286, "давач", 10, INK, "middle", "bold")
    s += text(300, 304, "(ключ на GND)", 8.5, GREY, "middle")
    s += line(300, 320, 300, 360, INK, 2)
    s += line(120, 360, 600, 360, BLUE, 2.2)
    s += text(120, 380, "GND (спільна)", 10, BLUE, "start", "bold")
    s += rect(700, 150, 200, 168, "none", FAINT, 1.6, 10)
    s += text(800, 176, "Логіка active-low:", 11, INK, "middle", "bold")
    s += text(716, 202, "спокій → підтяжка", 10, INK, "start")
    s += text(716, 220, "тримає HIGH (1)", 10, INK, "start")
    s += text(716, 246, "спрацював → давач", 10, INK, "start")
    s += text(716, 264, "садить LOW (0)", 10, GREEN, "start", "bold")
    s += text(716, 292, "if (read == LOW)", 9.5, INK, "start", "bold")
    s += text(716, 308, "{ /* подія */ }", 9.5, GREY, "start")
    save("fig-22-8-4-connect-switch-sensor.svg", s)


# ── Рис. 22.8.5 — давач із двотактним виходом ────────────────────────────────
def fig85_connect_driven_sensor():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "Давач із двотактним виходом: прямо або через зсув", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "якщо модуль сам жене HIGH/LOW — підтяжка не потрібна; та звіряй напруги", 11, GREY, "middle", style="italic")
    s += rect(40, 84, 400, 330, "none", FAINT, 1.6, 12)
    s += text(240, 110, "Однакова напруга (3.3 В) → прямо", 11.5, GREEN, "middle", "bold")
    s += rect(70, 170, 120, 70, "#fbfcff", INK, 1.6, 8)
    s += text(130, 200, "давач 3.3 В", 10, INK, "middle", "bold")
    s += text(130, 220, "push-pull OUT", 8.5, GREY, "middle")
    s += arrow(190, 205, 300, 205, INK, 2.2)
    s += text(245, 196, "прямо", 9, GREEN, "middle", "bold")
    s += rect(300, 170, 100, 70, "none", BLUE, 2, 8)
    s += text(350, 208, "вхід МК", 10, BLUE, "middle", "bold")
    s += text(240, 290, "однакові рівні — просто з'єднати", 10, INK, "middle")
    s += text(240, 312, "(і спільна земля)", 9, GREY, "middle")
    s += rect(480, 84, 400, 330, "none", FAINT, 1.6, 12)
    s += text(680, 110, "Давач 5 В → ОБОВ'ЯЗКОВО зсув", 11.5, RED, "middle", "bold")
    s += rect(510, 170, 110, 70, "#fbfcff", INK, 1.6, 8)
    s += text(565, 200, "давач 5 В", 10, INK, "middle", "bold")
    s += text(565, 220, "OUT = 5 В", 8.5, RED, "middle")
    s += line(620, 205, 658, 205, INK, 2)
    s += rect(658, 180, 74, 50, LAMB, GOLD, 1.6, 6)
    s += text(695, 202, "зсув", 9.5, "#8a6a14", "middle", "bold")
    s += text(695, 218, "рівнів", 9, "#8a6a14", "middle")
    s += line(732, 205, 770, 205, INK, 2)
    s += rect(770, 170, 90, 70, "none", BLUE, 2, 8)
    s += text(815, 208, "вхід МК", 10, BLUE, "middle", "bold")
    s += text(680, 300, "5 В прямо = спалена ніжка (§22.3)!", 10, RED, "middle", "bold")
    s += text(680, 322, "лише через дільник чи перетворювач рівнів", 9.2, GREY, "middle")
    save("fig-22-8-5-connect-driven-sensor.svg", s)


# ── Рис. 22.8.6 — повна модель ніжки (підсумок розділу) ──────────────────────
def fig86_recap_pin_model():
    W, H = 960, 470
    s = header(W, H)
    s += text(W / 2, 32, "Повна модель ніжки: усе, що ми вивчили в розділі", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "від транзисторів усередині до коду зовні — ніжка як цілісний інтерфейс", 11.5, GREY, "middle", style="italic")
    cx, cy = 480, 258
    nodes = [
        (210, 150, "Вихід", ["push-pull §22.1", "open-drain §22.2"], BLUE),
        (750, 150, "Вхід", ["пороги §22.3", "підтяжки §22.4"], GREEN),
        (210, 370, "Захист", ["струм/діоди §22.6", "дребезг §22.5"], RED),
        (750, 370, "Код", ["регістри §22.7", "маски, W1TS"], GOLD),
    ]
    for x, y, t, lines, col in nodes:
        s += line(cx, cy, x, y, col, 1.6, dash="5,3")
    s += circle(cx, cy, 54, LAMB, GOLD, 2.6)
    s += text(cx, cy - 4, "НІЖКА", 13, INK, "middle", "bold")
    s += text(cx, cy + 14, "(GPIO)", 10, GREY, "middle")
    for x, y, t, lines, col in nodes:
        s += rect(x - 112, y - 44, 224, 88, "#fbfcff", col, 1.8, 12)
        s += text(x, y - 16, t, 13, col, "middle", "bold")
        yy = y + 6
        for ln in lines:
            s += text(x, yy, ln, 10, INK, "middle")
            yy += 18
    s += text(W / 2, 450, "Ось і весь розділ однією картинкою: вихід, вхід, захист і код — навколо однієї ніжки.", 10.5, INK, "middle", "bold")
    save("fig-22-8-6-recap-pin-model.svg", s)


# ── 🔌 вставка до 4.4.5 — тактова кнопка ─────────────────────────────────────
def _tint5c(col):
    return {RED: LRED, GREEN: LGRN, BLUE: LBLUE, GOLD: LAMB}.get(col, "#eef0f5")


def fig5c1_inside():
    W, H = 880, 340
    s = header(W, H)
    s += text(W / 2, 32, "Тактова кнопка зсередини: 4 ніжки — це 2 пари", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "ніжки по один бік уже з'єднані всередині; кнопка замикає одну пару з іншою",
              10.3, GREY, "middle", style="italic")
    # body of button
    bx, by, bw, bh = 300, 100, 280, 150
    s += rect(bx, by, bw, bh, "#fbfbff", INK, 2, 12)
    s += text(bx + bw / 2, by + 26, "корпус кнопки", 10.5, GREY, "middle", "bold")
    # dome
    s += ('<path d="M{a},{b} Q {c},{d} {e},{b}" fill="none" stroke="{col}" stroke-width="2.4"/>\n'
          ).format(a=bx + 90, b=by + 110, c=bx + bw / 2, d=by + 70, e=bx + bw - 90, col=RED)
    s += text(bx + bw / 2, by + 100, "пружна мембрана (купол)", 9.3, RED, "middle")
    # 4 pins, two pairs
    pins = [(bx, by + 30, "1"), (bx, by + bh - 30, "2"),
            (bx + bw, by + 30, "3"), (bx + bw, by + bh - 30, "4")]
    for px, py, n in pins:
        side = -1 if px == bx else 1
        s += line(px, py, px + side * 40, py, METAL, 3)
        s += circle(px + side * 40, py, 4, METAL, METAL, 1)
        s += text(px + side * 52, py + 4, n, 11, INK, "middle", "bold")
    # internal pairing (1-2 connected, 3-4 connected)
    s += line(bx, by + 30, bx, by + bh - 30, GREEN, 2.4)
    s += line(bx + bw, by + 30, bx + bw, by + bh - 30, GREEN, 2.4)
    s += text(bx - 4, by + bh / 2 + 4, "1–2 з'єднані", 8.6, GREEN, "end")
    s += text(bx + bw + 4, by + bh / 2 + 4, "3–4 з'єднані", 8.6, GREEN, "start")
    s += text(bx + bw / 2, by + bh + 30, "натиск → купол замикає ліву пару (1,2) з правою (3,4)",
              10, INK, "middle", "bold")
    s += rect(150, 296, 580, 34, "#fbfbfb", GREY, 1.4, 8)
    s += text(440, 318, "Тиснемо — пари зчіпаються; відпускаємо — розходяться. Між дотиками контакт «дзвенить».",
              9.3, INK, "middle")
    save("fig-22-5c-1-inside.svg", s)


def fig5c2_wiring():
    W, H = 880, 300
    s = header(W, H)
    s += text(W / 2, 32, "Підключення кнопки: ніжка з підтяжкою, інший бік — на землю", 16.5, INK, "middle", "bold")
    s += text(W / 2, 54, "натиснута кнопка тягне ніжку в LOW; підтяжка тримає HIGH, поки не натиснуто",
              10, GREY, "middle", style="italic")
    # 3V3 rail
    s += line(120, 96, 760, 96, RED, 2)
    s += text(110, 100, "3.3 В", 10, RED, "end", "bold")
    # pull-up resistor
    s += rect(300, 110, 26, 50, "#fff", INK, 1.6, 3)
    s += text(348, 138, "10 кОм", 9, GREY, "start")
    s += line(313, 96, 313, 110, INK, 1.6)
    # node to GPIO
    s += line(313, 160, 313, 200, INK, 1.6)
    s += line(313, 180, 470, 180, INK, 1.6)
    s += rect(470, 158, 150, 44, LBLUE, BLUE, 1.8, 8)
    s += text(545, 185, "GPIO (вхід)", 11, BLUE, "middle", "bold")
    # button to GND
    s += rect(286, 200, 54, 34, "#fbfbff", INK, 1.8, 5)
    s += text(313, 222, "S", 11, INK, "middle", "bold")
    s += line(313, 234, 313, 262, INK, 1.6)
    s += line(250, 262, 376, 262, INK, 2)
    s += text(313, 280, "GND", 10, INK, "middle", "bold")
    s += text(150, 250, "не натиснуто → HIGH", 10, GREEN, "start", "bold")
    s += text(600, 250, "натиснуто → LOW", 10, RED, "start", "bold")
    save("fig-22-5c-2-wiring.svg", s)


# ── 🔌 вставка до 4.4.8 — розширювачі GPIO ───────────────────────────────────
def fig8c1_concept():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 32, "Розширювач портів: віддав 2 ніжки — дістав 8", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "дві лінії I²C керують чипом, що дає цілий банк нових GPIO",
              11, GREY, "middle", style="italic")
    # MCU
    s += rect(70, 110, 150, 110, LBLUE, BLUE, 2, 10)
    s += text(145, 150, "ESP32", 13, BLUE, "middle", "bold")
    s += text(145, 176, "SDA · SCL", 10, INK, "middle", "bold")
    s += text(145, 196, "(лише 2 ніжки)", 8.6, GREY, "middle")
    # bus
    s += arrow(220, 165, 330, 165, INK, 2.4)
    s += text(275, 153, "I²C", 10, INK, "middle", "bold")
    # expander
    s += rect(330, 100, 200, 130, LAMB, GOLD, 2, 12)
    s += text(430, 128, "розширювач", 12.5, "#8a6d1a", "middle", "bold")
    s += text(430, 148, "PCF8574-клас", 9.5, GREY, "middle")
    # 8 output pins
    for i in range(8):
        y = 108 + i * 15
        s += line(530, y, 560, y, METAL, 2)
    s += text(600, 150, "8 нових", 12, GREEN, "middle", "bold")
    s += text(600, 170, "GPIO (P0…P7)", 11, GREEN, "middle", "bold")
    s += rect(150, 262, 600, 52, "#fbfbfb", GREY, 1.4, 10)
    s += text(450, 284, "А ніжки A0–A2 дають кожному чипу свою адресу:", 10.5, INK, "middle", "bold")
    s += text(450, 304, "2 ніжки ESP32 → до 8 чипів на шині → до 64 нових GPIO.", 10, GREY, "middle")
    save("fig-22-8c-1-concept.svg", s)


def fig8c2_wiring():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 32, "Підключення розширювача по I²C", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "дві спільні лінії з підтяжками; адресні ніжки на землю; INT економить опитування",
              10, GREY, "middle", style="italic")
    s += rect(70, 110, 140, 120, LBLUE, BLUE, 2, 10)
    s += text(140, 150, "ESP32", 12.5, BLUE, "middle", "bold")
    s += rect(560, 96, 160, 150, LAMB, GOLD, 2, 12)
    s += text(640, 122, "розширювач", 11.5, "#8a6d1a", "middle", "bold")
    # 3V3 rail + pullups
    s += line(250, 92, 520, 92, RED, 2)
    s += text(250, 86, "3.3 В", 9, RED, "middle", "bold")
    # SDA / SCL with pullups
    for i, (lab, yy) in enumerate([("SDA", 150), ("SCL", 174)]):
        s += line(210, yy, 560, yy, BLUE, 1.8)
        s += text(385, yy - 5, lab, 9, BLUE, "middle", "bold")
        rx = 320 + i * 40
        s += rect(rx, 100, 16, 30, "#fff", INK, 1.4, 3)
        s += line(rx + 8, 92, rx + 8, 100, INK, 1.4)
        s += line(rx + 8, 130, rx + 8, yy, INK, 1.4)
    s += text(360, 120, "підтяжки", 8, GREY, "middle")
    # power + address
    s += line(210, 200, 560, 200, GREEN, 1.6)
    s += text(385, 195, "VCC · GND", 8.6, GREEN, "middle")
    s += text(640, 200, "A0–A2 → GND", 8.6, GREY, "middle")
    s += text(640, 218, "(задає адресу)", 8, GREY, "middle")
    # expander out: LED + button
    s += line(720, 130, 760, 130, METAL, 2)
    s += circle(772, 130, 9, LGRN, GREEN, 1.6)
    s += text(792, 134, "світлодіод", 8.6, GREEN, "start")
    s += line(720, 170, 760, 170, METAL, 2)
    s += rect(760, 162, 22, 16, "#fff", INK, 1.4, 3)
    s += text(792, 174, "кнопка", 8.6, INK, "start")
    # INT
    s += arrow(560, 224, 210, 224, RED, 1.8)
    s += text(385, 238, "INT → ESP32 (необов'язково): «щось змінилось»", 8.6, RED, "middle", "bold")
    s += rect(150, 286, 600, 34, "#fbfbfb", GREY, 1.4, 8)
    s += text(450, 308, "Шина I²C спільна; INT дозволяє не опитувати, а чекати сигналу про зміну.", 9.3, INK, "middle")
    save("fig-22-8c-2-wiring.svg", s)


# ── ⚙️ вставка до 4.4.5 — антидребезг у коді ─────────────────────────────────
def fig5a1_three():
    W, H = 900, 320
    s = header(W, H)
    s += text(W / 2, 32, "Антидребезг у коді: три підходи", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "усі ловлять одну ідею — «вважати пачку дрижань за одну подію» — по-різному",
              10.3, GREY, "middle", style="italic")
    cols = [(BLUE, "Лічильник", "рахуй N однакових", "відліків поспіль;", "набралось — приймай", "тримає: лічильник"),
            (GREEN, "Мітка часу", "запам'ятай час зміни;", "ігноруй зміни,", "поки не минув час T", "тримає: час зміни"),
            (GOLD, "Автомат", "стани: стабільний →", "під підозрою →", "знову стабільний", "тримає: стан + час")]
    x = 60
    for col, title, a, b, c, foot in cols:
        fill = {BLUE: LBLUE, GREEN: LGRN, GOLD: LAMB}[col]
        s += rect(x, 86, 260, 160, fill, col, 2, 12)
        s += text(x + 130, 114, title, 13.5, col, "middle", "bold")
        for i, ln in enumerate([a, b, c]):
            s += text(x + 130, 142 + i * 22, ln, 10, INK, "middle")
        s += text(x + 130, 226, foot, 9, GREY, "middle", "bold")
        x += 280
    s += text(W / 2, 286, "Лічильник — найпростіший; мітка часу — не блокує цикл; автомат — найнадійніший.",
              11, INK, "middle", "bold")
    save("fig-22-5a-1-three.svg", s)


def fig5a2_fsm():
    W, H = 900, 300
    s = header(W, H)
    s += text(W / 2, 32, "Скінченний автомат антидребезгу", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "не вірити першій зміні: дочекатись, поки рівень устоїться, і лише тоді визнати подію",
              10, GREY, "middle", style="italic")
    # three states
    s += circle(170, 160, 56, LGRN, GREEN, 2.2)
    s += text(170, 156, "СТАБІЛЬНИЙ", 11, GREEN, "middle", "bold")
    s += text(170, 174, "(рівень тримається)", 8, GREY, "middle")
    s += circle(450, 160, 56, LAMB, GOLD, 2.2)
    s += text(450, 156, "ПІД ПІДОЗРОЮ", 10.5, "#8a6d1a", "middle", "bold")
    s += text(450, 174, "(чекаємо час T)", 8, GREY, "middle")
    s += circle(730, 160, 56, LGRN, GREEN, 2.2)
    s += text(730, 152, "СТАБІЛЬНИЙ′", 11, GREEN, "middle", "bold")
    s += text(730, 170, "подія!", 9, RED, "middle", "bold")
    s += arrow(226, 150, 394, 150, INK, 2)
    s += text(310, 138, "зміна помічена", 9, INK, "middle")
    s += arrow(506, 150, 674, 150, GREEN, 2)
    s += text(590, 138, "T минув, рівень той самий", 8.6, GREEN, "middle")
    # bounce-back
    s += ('<path d="M{a},{b} Q {c},{d} {e},{f}" fill="none" stroke="{col}" stroke-width="1.8" '
          'stroke-dasharray="5 4" marker-end="url(#aRed)"/>\n').format(
        a=430, b=216, c=300, d=270, e=200, f=216, col=RED)
    s += text(310, 262, "рівень повернувся — хибна тривога, назад", 9, RED, "middle")
    s += text(W / 2, 294, "Дрижання застрягає у стані «під підозрою» й не доходить до події — саме цього ми й хотіли.",
              9.6, INK, "middle", "bold")
    save("fig-22-5a-2-fsm.svg", s)


# ── ⚙️ вставка до 4.4.7 — біт-бенгінг ────────────────────────────────────────
def fig7a1_idea():
    W, H = 900, 300
    s = header(W, H)
    s += text(W / 2, 32, "Біт-бенгінг: ти сам стаєш протоколом", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "нема апаратного блока — вручну смикаєш ніжки в потрібному порядку й ритмі",
              10.3, GREY, "middle", style="italic")
    # DATA waveform for bits 1,0,1
    bits = [1, 0, 1]
    x0, w = 180, 160
    yD, yC, hi = 110, 200, 34
    s += text(140, yD + 5, "DATA", 11, BLUE, "end", "bold")
    s += text(140, yC + 5, "CLK", 11, GREEN, "end", "bold")
    for i, b in enumerate(bits):
        x = x0 + i * w
        # DATA level
        dy = yD - hi if b else yD
        s += line(x, dy, x + w, dy, BLUE, 2.4)
        if i < 2:
            ny = yD - hi if bits[i + 1] else yD
            s += line(x + w, dy, x + w, ny, BLUE, 1.6)
        s += text(x + w / 2, yD + 24, str(b), 11, BLUE, "middle", "bold")
        # CLK pulse: low, up at mid, down
        s += line(x, yC, x + w * 0.3, yC, GREEN, 2.2)
        s += line(x + w * 0.3, yC, x + w * 0.3, yC - hi, GREEN, 2.2)
        s += line(x + w * 0.3, yC - hi, x + w * 0.7, yC - hi, GREEN, 2.2)
        s += line(x + w * 0.7, yC - hi, x + w * 0.7, yC, GREEN, 2.2)
        s += line(x + w * 0.7, yC, x + w, yC, GREEN, 2.2)
    s += rect(150, 244, 600, 44, "#fbfbfb", GREY, 1.4, 8)
    s += text(450, 264, "На кожен біт: 1) постав біт на DATA → 2) CLK ↑ → 3) CLK ↓.", 10.5, INK, "middle", "bold")
    s += text(450, 282, "Протокол — це лише точна послідовність станів ніжок у часі; відтвори її — і він готовий.", 9.3, GREY, "middle")
    save("fig-22-7a-1-idea.svg", s)


def fig7a2_cost():
    W, H = 900, 320
    s = header(W, H)
    s += text(W / 2, 32, "Чесна ціна тактів", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "кожне смикання ніжки коштує процесорного часу — і поки бенгаємо, ядро зайняте",
              10.3, GREY, "middle", style="italic")
    # speed comparison
    s += rect(60, 86, 380, 100, LRED, RED, 1.8, 10)
    s += text(250, 112, "digitalWrite()", 12, RED, "middle", "bold")
    s += text(250, 136, "~2 мкс на перемикання (пошук + виклик)", 9.6, INK, "middle")
    s += text(250, 158, "→ шина ледача", 10.5, RED, "middle", "bold")
    s += rect(460, 86, 380, 100, LGRN, GREEN, 1.8, 10)
    s += text(650, 112, "прямо в регістр (W1TS/W1TC)", 11.5, GREEN, "middle", "bold")
    s += text(650, 136, "наносекунди на перемикання (§4.4.7)", 9.6, INK, "middle")
    s += text(650, 158, "→ шина в рази швидша", 10.5, GREEN, "middle", "bold")
    # cpu busy comparison
    s += rect(60, 200, 380, 96, LAMB, GOLD, 1.8, 10)
    s += text(250, 226, "Біт-бенгінг", 12, "#8a6d1a", "middle", "bold")
    s += text(250, 250, "ядро зайняте весь час передачі —", 9.6, INK, "middle")
    s += text(250, 270, "більше нічого не встигає", 9.6, GREY, "middle")
    s += rect(460, 200, 380, 96, LBLUE, BLUE, 1.8, 10)
    s += text(650, 226, "Апаратний блок (SPI/I²C)", 11.5, BLUE, "middle", "bold")
    s += text(650, 250, "крутиться у фоні сам —", 9.6, INK, "middle")
    s += text(650, 270, "ядро вільне для іншого", 9.6, GREY, "middle")
    s += text(W / 2, 312, "Біт-бенгінг — запасний вихід, коли блока нема; є блок — бери блок.", 10.5, INK, "middle", "bold")
    save("fig-22-7a-2-cost.svg", s)


# ── ⚙️ вставка до 4.4.8 — матриця кнопок 4×4 ─────────────────────────────────
def fig8a1_grid():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 32, "Матриця кнопок: 16 клавіш — 8 ніжок", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "сканування: подаємо сигнал у рядок, читаємо стовпці; натиснута клавіша з'єднує їх",
              10, GREY, "middle", style="italic")
    cols_x = [330, 420, 510, 600]
    rows_y = [120, 165, 210, 255]
    driven = 1   # R1 active
    pressed = (1, 2)
    # column lines
    for j, cx in enumerate(cols_x):
        col = GREEN if j == pressed[1] else GREY
        s += line(cx, 100, cx, 275, col, 2.2 if j == pressed[1] else 1.4)
        s += text(cx, 90, "C" + str(j), 10, col, "middle", "bold")
    # row lines
    for i, ry in enumerate(rows_y):
        col = GREEN if i == driven else GREY
        s += line(310, ry, 620, ry, col, 2.4 if i == driven else 1.4)
        s += text(290, ry + 4, "R" + str(i), 10, col, "end", "bold")
        for j, cx in enumerate(cols_x):
            on = (i, j) == pressed
            s += circle(cx, ry, 6, (LGRN if on else "#fff"), (GREEN if on else GREY), 1.6)
    s += text(150, 130, "R1 активний →", 9.5, GREEN, "start", "bold")
    s += text(660, 165, "натиск (R1,C2)", 9.5, GREEN, "start", "bold")
    s += text(660, 120, "C2 озвався", 9, GREEN, "start")
    s += rect(150, 296, 600, 52, "#fbfbfb", GREY, 1.4, 10)
    s += text(450, 318, "R рядків + C стовпців = R+C ніжок дають R×C клавіш.", 11, INK, "middle", "bold")
    s += text(450, 338, "4 + 4 = 8 ніжок → 16 клавіш (а не 16 ніжок по одній на клавішу).", 9.6, GREY, "middle")
    save("fig-22-8a-1-grid.svg", s)


def fig8a2_ghost():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 32, "Привид (ghosting) і ліки — діод у кожній клавіші", 18, INK, "middle", "bold")

    def cell(ox, oy, with_diode, title, col):
        o = text(ox + 90, oy - 12, title, 12, col, "middle", "bold")
        xs = [ox + 40, ox + 140]
        ys = [oy + 30, oy + 110]
        for cx in xs:
            o2 = line(cx, oy + 10, cx, oy + 130, GREY, 1.4)
            o += o2
        for ry in ys:
            o += line(ox + 20, ry, ox + 160, ry, GREY, 1.4)
        # pressed keys: (0,0),(0,1),(1,0) ; phantom (1,1)
        pressed = {(0, 0), (0, 1), (1, 0)}
        for ii, ry in enumerate(ys):
            for jj, cx in enumerate(xs):
                on = (ii, jj) in pressed
                phantom = (ii, jj) == (1, 1) and not with_diode
                fill = LGRN if on else ("#fff")
                stroke = GREEN if on else GREY
                if phantom:
                    fill, stroke = LRED, RED
                o += circle(cx, ry, 7, fill, stroke, 1.8)
                if phantom:
                    o += text(cx + 16, ry + 4, "✗ привид", 8.6, RED, "start", "bold")
                if with_diode:
                    o += ('<path d="M{a},{b} l 8,5 l -8,5 Z" fill="{c}"/>\n').format(a=cx - 14, b=ry - 5, c=GOLD)
        return o

    s += cell(80, 110, False, "Без діодів", RED)
    # sneak path on left
    s += line(120, 140, 220, 140, RED, 1.8, dash="5 4")
    s += line(220, 140, 220, 220, RED, 1.8, dash="5 4")
    s += text(170, 256, "струм «крадеться» в обхід → фальшива 4-та", 8.6, RED, "middle")
    s += cell(560, 110, True, "З діодами", GREEN)
    s += text(650, 256, "діод пускає струм лише в один бік →", 8.6, GREEN, "middle")
    s += text(650, 272, "обхідний шлях закрито ✓", 8.6, GREEN, "middle", "bold")
    s += text(W / 2, 312, "Три натиснуті в прямокутнику без діодів дають уявну четверту; діод у кожній клавіші це лікує.",
              9.6, INK, "middle", "bold")
    save("fig-22-8a-2-ghost.svg", s)


# ── 🧮 вставка до 4.4.4 — чому підтяжка саме 10 кОм ──────────────────────────
def fig4m1_tradeoff():
    W, H = 900, 300
    s = header(W, H)
    s += text(W / 2, 32, "Чому ~10 кОм: затиснуто з двох боків", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "малий резистор жере струм; великий — слабкий, повільний і ловить витік",
              10.3, GREY, "middle", style="italic")
    # axis
    s += line(120, 170, 780, 170, INK, 2)
    for x, lab in [(160, "1 кОм"), (360, "10 кОм"), (560, "100 кОм"), (740, "1 МОм")]:
        s += line(x, 165, x, 175, INK, 1.6)
        s += text(x, 192, lab, 10, INK, "middle", "bold")
    s += text(120, 162, "менший R", 9, GREY, "start")
    s += text(780, 162, "більший R", 9, GREY, "end")
    # left pressure
    s += arrow(300, 120, 180, 120, RED, 2.2)
    s += text(300, 110, "марнує струм (I = V/R більший)", 9.6, RED, "start")
    # right pressure
    s += arrow(440, 142, 600, 142, BLUE, 2.2)
    s += text(440, 134, "шум · витік · повільний фронт", 9.6, BLUE, "start")
    # sweet spot
    s += circle(360, 170, 12, LGRN, GREEN, 2.4)
    s += text(360, 232, "золота середина", 10.5, GREEN, "middle", "bold")
    s += text(W / 2, 272, "~10 кОм мирить обидва тиски: тримає рівень упевнено й майже не жере струму.",
              10.5, INK, "middle", "bold")
    save("fig-22-4m-1-tradeoff.svg", s)


def fig4m2_numbers():
    W, H = 900, 300
    s = header(W, H)
    s += text(W / 2, 32, "Підтяжка під 3.3 В: число за числом", 19, INK, "middle", "bold")
    cols = ["R", "струм у LOW  (I=V/R)", "фронт  (τ=R·C, C≈50 пФ)", "стійкість до шуму"]
    cx = [130, 330, 560, 780]
    s += rect(70, 70, 760, 30, "#eef1f8", BLUE, 1.4, 6)
    for c, x in zip(cols, cx):
        s += text(x, 90, c, 10.5, BLUE, "middle", "bold")
    rows = [("1 кОм", "3.3 мА", "50 нс — дуже швидкий", "відмінна", INK),
            ("10 кОм", "0.33 мА", "0.5 мкс — швидкий", "добра", GREEN),
            ("100 кОм", "33 мкА", "5 мкс — повільніший", "слабша", INK),
            ("1 МОм", "3.3 мкА", "50 мкс — повільний", "погана (витік!)", RED)]
    y = 116
    for r, cur, fr, noise, col in rows:
        hl = col == GREEN
        if hl:
            s += rect(74, y - 18, 752, 30, LGRN, GREEN, 1.4, 5)
        s += text(cx[0], y, r, 11, col, "middle", "bold")
        s += text(cx[1], y, cur, 10, INK, "middle")
        s += text(cx[2], y, fr, 9.6, INK, "middle")
        s += text(cx[3], y, noise, 9.6, col if col == RED else INK, "middle")
        if hl:
            s += text(cx[0], y + 13, "← звичайний вибір", 7.6, GREEN, "middle")
        y += 40
    s += text(W / 2, 286, "10 кОм — типовий компроміс. Швидка шина I²C → 2–4.7 кОм; глибокий сон → 100 кОм і більше.",
              10, INK, "middle", "bold")
    save("fig-22-4m-2-numbers.svg", s)


# ── 🧮 вставка до 4.4.6 — бюджет ніжки й порту ───────────────────────────────
def fig6m1_two_budgets():
    W, H = 900, 320
    s = header(W, H)
    s += text(W / 2, 32, "Два бюджети: окрема ніжка й увесь чіп", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "як розетка й головний автомат: тримати треба обидві межі заразом",
              10.3, GREY, "middle", style="italic")
    # per-pin
    s += rect(60, 84, 360, 190, LBLUE, BLUE, 2, 12)
    s += text(240, 110, "Бюджет ніжки («розетка»)", 12, BLUE, "middle", "bold")
    for i in range(4):
        y = 134 + i * 30
        s += text(110, y, "ніжка " + str(i), 10, INK, "start")
        s += rect(200, y - 12, 150, 18, "#fff", BLUE, 1.2, 3)
        s += rect(200, y - 12, 90, 18, LBLUE, BLUE, 0, 3)
        s += text(360, y, "≤ ~20 мА", 9.5, BLUE, "end", "bold")
    s += text(240, 262, "кожна окремо — не більш як ~20 мА (стеля 40)", 8.8, GREY, "middle")
    # chip total
    s += rect(480, 84, 360, 190, LAMB, GOLD, 2, 12)
    s += text(660, 110, "Бюджет чипа («автомат»)", 12, "#8a6d1a", "middle", "bold")
    s += text(660, 150, "Σ усіх ніжок", 13, INK, "middle", "bold")
    s += text(660, 178, "≤ межа живлення чипа", 11, "#8a6d1a", "middle", "bold")
    s += text(660, 214, "8 світлодіодів × 10 мА = 80 мА", 9.6, INK, "middle")
    s += text(660, 234, "— це вже привід перевірити суму", 9, GREY, "middle")
    s += text(660, 262, "забагато → притишити струм або драйвер", 8.8, RED, "middle")
    s += text(W / 2, 304, "Мало, щоб кожна ніжка була в межах — їхня СУМА теж мусить уміститися.",
              10.5, INK, "middle", "bold")
    save("fig-22-6m-1-two-budgets.svg", s)


def fig6m2_led_color():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 32, "Резистор світлодіода: R = (V_ніжки − V_LED) / I", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "за кольором різний V_LED — а отже, різний запас на 3.3 В",
              10.5, GREY, "middle", style="italic")
    cols = ["колір", "V_LED (Vf)", "R для 10 мА на 3.3 В", "запас"]
    cx = [150, 340, 560, 770]
    s += rect(70, 76, 760, 28, "#eef1f8", BLUE, 1.4, 6)
    for c, x in zip(cols, cx):
        s += text(x, 95, c, 10.5, BLUE, "middle", "bold")
    rows = [("червоний", "2.0 В", "130 Ом", "добрий", GREEN),
            ("зелений / жовтий", "2.1 В", "120 Ом", "добрий", GREEN),
            ("синій / білий", "3.0 В", "30 Ом", "МАЛИЙ", RED)]
    y = 122
    for color, vf, r, hr, col in rows:
        s += text(cx[0], y, color, 11, INK, "middle")
        s += text(cx[1], y, vf, 10.5, INK, "middle")
        s += text(cx[2], y, r, 10.5, INK, "middle")
        s += text(cx[3], y, hr, 10.5, col, "middle", "bold")
        y += 34
    s += rect(120, 232, 660, 84, LRED, RED, 1.4, 10)
    s += text(450, 256, "Синій/білий мають V_LED близьке до 3.3 В — на резистор лишається крихта.", 10.5, INK, "middle", "bold")
    s += text(450, 278, "Тоді струм дуже чутливий до розкиду Vf, і LED або ледь світить, або перевантажений.", 9.6, GREY, "middle")
    s += text(450, 300, "Висновок: на 3.3 В сині/білі капризні — їм комфортніше від 5 В.", 9.8, RED, "middle", "bold")
    save("fig-22-6m-2-led-color.svg", s)


# ── 📜 історія до 4.4.5 — дребезг старший за електроніку ──────────────────────
def fig5i1_timeline():
    W, H = 920, 250
    s = header(W, H)
    s += text(W / 2, 32, "Дребезг контактів: понад півтора століття ворогові", 18, INK, "middle", "bold")
    s += line(70, 150, 850, 150, INK, 2)
    marks = [(120, "1840-ві", "телеграфні реле:", "контакт клацає, іскрить", BLUE),
             (320, "1888–91", "Строуджер —", "автоматична АТС", GREEN),
             (500, "1892", "перша АТС", "(Ла-Порт, Індіана)", GREEN),
             (680, "XX ст.", "мільйони контактів", "у телефонних мережах", INK),
             (835, "сьогодні", "пара рядків", "коду в МК (§4.4.5)", GOLD)]
    for x, yr, a, b, col in marks:
        s += circle(x, 150, 6, col, col, 1)
        s += text(x, 130, yr, 10.5, col, "middle", "bold")
        s += text(x, 178, a, 8.8, INK, "middle")
        s += text(x, 193, b, 8.8, GREY, "middle")
    s += text(W / 2, 230, "Дрижання металевого контакту мучило інженерів задовго до мікроконтролерів.",
              10.5, INK, "middle", "bold")
    save("fig-22-5i-1-timeline.svg", s)


def fig5i2_stepping():
    W, H = 900, 320
    s = header(W, H)
    s += text(W / 2, 32, "Крокова АТС Строуджера: цифра крокує по контактах", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "номеронабирач шле пачку імпульсів; кожен імпульс — один крок по дузі контактів",
              10, GREY, "middle", style="italic")
    # dial sends pulses
    s += circle(150, 170, 50, LBLUE, BLUE, 2)
    s += text(150, 168, "диск", 11, BLUE, "middle", "bold")
    s += text(150, 186, "набору", 9, GREY, "middle")
    # pulses
    py = 130
    s += text(255, 120, "імпульси:", 9, INK, "middle")
    for i in range(4):
        x = 230 + i * 24
        s += line(x, py, x, py - 20, GREEN, 2)
        s += line(x, py - 20, x + 12, py - 20, GREEN, 2)
        s += line(x + 12, py - 20, x + 12, py, GREEN, 2)
        s += line(x + 12, py, x + 24, py, GREEN, 2)
    s += arrow(340, 170, 420, 170, INK, 2.2)
    # contact arc with wiper
    cx, cy, r = 600, 180, 90
    for k in range(7):
        ang = -70 + k * 22
        import math
        ax = cx + r * math.cos(math.radians(ang))
        ay = cy + r * math.sin(math.radians(ang))
        on = (k == 4)
        s += circle(ax, ay, 7, (LGRN if on else "#fff"), (GREEN if on else GREY), 1.6)
        if on:
            s += text(ax + 18, ay + 4, "потрібна лінія", 8.6, GREEN, "start", "bold")
    s += line(cx, cy, cx + r * math.cos(math.radians(18)), cy + r * math.sin(math.radians(18)), INK, 2.4)
    s += circle(cx, cy, 5, INK, INK, 1)
    s += text(cx, cy + 40, "рухома щітка", 9, INK, "middle")
    s += rect(120, 280, 660, 34, LRED, RED, 1.4, 8)
    s += text(450, 302, "Брудний чи «дзвінкий» контакт → зайвий крок → не той номер. Чистота контакту — питання зв'язку.",
              9.4, INK, "middle", "bold")
    save("fig-22-5i-2-stepping.svg", s)


def fig5i3_cures():
    W, H = 900, 280
    s = header(W, H)
    s += text(W / 2, 32, "Століття ліків за чистий контакт", 19, INK, "middle", "bold")
    cures = [("самоочисні контакти", "труться, стираючи бруд", BLUE),
             ("благородні метали", "золото, срібло — не окисляються", GOLD),
             ("ртутні реле", "контакт у ртуті — дребезгу нема", GREEN)]
    x = 60
    for t, sub, col in cures:
        fill = {BLUE: LBLUE, GOLD: LAMB, GREEN: LGRN}[col]
        s += rect(x, 86, 250, 96, fill, col, 1.8, 12)
        s += text(x + 125, 120, t, 11.5, col, "middle", "bold")
        s += text(x + 125, 148, sub, 9, INK, "middle")
        x += 270
    s += text(W / 2, 222, "Телефонні інженери били дрижання залізом і ртуттю; ви б'єте його кодом (§4.4.5).",
              11, INK, "middle", "bold")
    s += text(W / 2, 246, "Той самий ворог — куди легша зброя.", 10, GREY, "middle")
    save("fig-22-5i-3-cures.svg", s)


if __name__ == "__main__":
    # §22.1 Ніжка на рівні заліза: вихід push-pull
    fig11_drive_the_line()
    fig12_push_pull()
    fig13_register_control()
    fig14_high_low()
    fig15_shoot_through()
    fig16_led_drive()
    # §22.2 Open-drain
    fig21_open_drain()
    fig22_needs_pullup()
    fig23_wired_and()
    fig24_pushpull_clash()
    fig25_uses()
    fig26_level_shift()
    # §22.3 Логічні пороги входу
    fig31_input_senses()
    fig32_threshold_band()
    fig33_noise_margin()
    fig34_hysteresis()
    fig35_ttl_cmos()
    fig36_esp32_input()
    # §22.4 Плаваючий пін і підтяжки
    fig41_floating()
    fig42_pullup_pulldown()
    fig43_button_pullup()
    fig44_resistor_value()
    fig45_internal_pullup()
    fig46_esp32_pins()
    # §22.5 Дребезг контактів
    fig51_bounce_scope()
    fig52_why_bad()
    fig53_rc_filter()
    fig54_sr_latch()
    fig55_sw_wait()
    fig56_sw_counter()
    # §22.6 Навантажувальна здатність і захист ніжки
    fig61_source_sink()
    fig62_limits()
    fig63_led_resistor()
    fig64_transistor_driver()
    fig65_flyback_diode()
    fig66_input_protection()
    # §22.7 GPIO у прошивці: регістри й маски
    fig71_register_bits()
    fig72_digitalwrite_vs_reg()
    fig73_bit_ops()
    fig74_w1ts_w1tc()
    fig75_multipin()
    fig76_esp32_gpio_regs()
    # §22.8 Абстрактна модель «модуля»
    fig81_module_blackbox()
    fig82_four_questions()
    fig83_discrete_sensor()
    fig84_connect_switch_sensor()
    fig85_connect_driven_sensor()
    fig86_recap_pin_model()
    # 🔌 вставка до 4.4.5 — тактова кнопка
    fig5c1_inside()
    fig5c2_wiring()
    # 🔌 вставка до 4.4.8 — розширювачі GPIO
    fig8c1_concept()
    fig8c2_wiring()
    # ⚙️ вставка до 4.4.5 — антидребезг у коді
    fig5a1_three()
    fig5a2_fsm()
    # ⚙️ вставка до 4.4.7 — біт-бенгінг
    fig7a1_idea()
    fig7a2_cost()
    # ⚙️ вставка до 4.4.8 — матриця кнопок 4×4
    fig8a1_grid()
    fig8a2_ghost()
    # 🧮 вставка до 4.4.4 — чому підтяжка саме 10 кОм
    fig4m1_tradeoff()
    fig4m2_numbers()
    # 🧮 вставка до 4.4.6 — бюджет ніжки й порту
    fig6m1_two_budgets()
    fig6m2_led_color()
    # 📜 історія до 4.4.5 — дребезг старший за електроніку
    fig5i1_timeline()
    fig5i2_stepping()
    fig5i3_cures()
    print("OK - figures for Section 22 (22.1..22.8 + s5c s8c s5a s7a s8a s4m s6m s5i) generated in", OUT)
