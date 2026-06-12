# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для історичної вставки до теми 3.8.6 — «SD-картка зсередини»
(Розділ 3.8 «Зовнішня пам'ять», Модуль 3): війна карток пам'яті (CF, SmartMedia,
MMC, Memory Stick, SD) і чому перемогла SD.

ОКРЕМИЙ скрипт лише цієї вставки (головний figs.py розділу не чіпаємо).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; стрілки через marker; шрифт sans-serif.
Підписи історії до теми — секція «h»: Рис. 3.8.6h.k → файли fig-r08-s6h-k-*.
Допоміжні функції — копія спільних із рештою розділів, щоб вигляд був єдиний.
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
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen"}


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
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def path(d, fill="none", stroke=INK, w=2):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _wrap(s, n):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= n:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _check(x, y, col=GREEN, r=9):
    out = circle(x, y, r, "#eef7ee", col, 1.6)
    out += polyline([(x - 4.2, y), (x - 1.2, y + 3.4), (x + 4.6, y - 3.8)], col, 2.2)
    return out


def _cross(x, y, col=RED, r=9):
    out = circle(x, y, r, "#fdf4f4", col, 1.6)
    out += line(x - 3.8, y - 3.8, x + 3.8, y + 3.8, col, 2.2)
    out += line(x - 3.8, y + 3.8, x + 3.8, y - 3.8, col, 2.2)
    return out


def _tilde(x, y, col=AMBER, r=9):
    out = circle(x, y, r, "#fff8e8", col, 1.6)
    out += path(f"M{x-4.4},{y+1} Q{x-2.2},{y-3.4} {x},{y} T{x+4.4},{y-1}", "none", col, 2.0)
    return out


# ── мініатюрна «картка» з підписаними пропорціями ───────────────────────────
def _card(x, y, w, h, col, bg, label, sub):
    out = rect(x, y, w, h, bg, col, 2, 6)
    # зрізаний кут — характерна риса карток пам'яті
    out += polyline([(x + w - 12, y), (x + w, y + 12)], col, 2)
    out += rect(x + w - 12, y, 12, 12, "#ffffff", "#ffffff", 0, 0)
    out += polyline([(x + w - 12, y), (x + w, y + 12)], col, 2)
    out += text(x + w / 2, y + h / 2 - 2, label, 12, col, "middle", "bold")
    out += text(x + w / 2, y + h / 2 + 14, sub, 9, GREY, "middle")
    return out


# ═══════════ Рис. 3.8.6h.1 — таймлайн «війни форматів» ══════════════════════
def fig_timeline():
    W, H = 920, 712
    s = header(W, H)
    s += text(W / 2, 38, "Війна карток пам'яті: десять років, шість форматів, один переможець",
              20, INK, "middle", "bold")
    s += text(W / 2, 60, "кожна фірма штовхала СВІЙ формат; ринок терпів зоопарк роз'ємів — аж поки SD не зібрала найкращий компроміс",
              12, GREY, "middle", style="italic")
    spine = 270
    top, bot = 100, H - 26
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("1994", "CompactFlash (SanDisk)",
         "Велика, міцна, з КОНТРОЛЕРОМ усередині. Профі люблять її й досі — але для кишені завелика", BLUE),
        ("1995", "SmartMedia (Toshiba)",
         "Тонша й дешевша — бо це ГОЛА NAND без контролера. Та сама дешевизна її згодом і вб'є", RED),
        ("1997", "MMC (SanDisk + Siemens + Nokia)",
         "Крихітна (32×24 мм) картка для телефонів і плеєрів — основа, на якій виросте SD", GREEN),
        ("1998", "Memory Stick (Sony)",
         "Sony йде СВОЇМ, закритим шляхом: «жуйка» лише для пристроїв Sony (відлуння Betamax)", AMBER),
        ("1999", "SD (SanDisk + Panasonic + Toshiba)",
         "Беруть інтерфейс MMC, додають захист від запису, міцніший корпус і DRM — і ВІДКРИВАЮТЬ стандарт", GREEN),
        ("січ. 2000", "засновано SD Association",
         "Троє фундаторів кличуть усіх: ліцензія для будь-якого виробника. Зоопарк починає сходитися до одного", GREEN),
        ("2002", "xD (Olympus + Fujifilm)",
         "Остання спроба «голої NAND» — спадкоємиця SmartMedia. Спізнилася: ринок уже обирав SD", RED),
        ("листоп. 2003", "SD виходить уперед",
         "У США: SD ≈ 42% · CompactFlash ≈ 26% · Memory Stick ≈ 16%. Перелом стався", GREEN),
        ("2005→", "microSD у кожному телефоні",
         "Крихітна SD вростає у смартфони — і остаточно закриває питання. Sony здається й бере SD (2010)", GREEN),
    ]
    n = len(nodes)
    for i, (yr, who, q, col) in enumerate(nodes):
        y = top + 26 + (bot - top - 52) * i / (n - 1)
        win = (col == GREEN and "SD" in who) or "вперед" in who or "microSD" in who
        if win:
            s += circle(spine, y, 11, "#fff", GREEN, 0)
            s += circle(spine, y, 10, "none", GREEN, 3.2)
            s += circle(spine, y, 4.5, GREEN, GREEN, 1)
        else:
            s += circle(spine, y, 7, "#fff", col, 2.6)
        s += text(spine - 22, y + 5, yr, 12, GREY, "end", "bold")
        s += text(spine + 26, y - 3, who, 14.5, col, "start", "bold")
        for j, ln in enumerate(_wrap(q, 64)):
            s += text(spine + 26, y + 16 + j * 16, ln, 11.5, INK, "start", style="italic")
    save("fig-r08-s6h-1-timeline.svg", s)


# ═══════════ Рис. 3.8.6h.2 — гола NAND проти «NAND + контролер» ═════════════
def fig_controller():
    W, H = 920, 540
    s = header(W, H)
    s += text(W / 2, 36, "Серце суперечки: ГОЛА NAND проти «NAND + контролер»", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "це не дрібниця корпусу, а РІЗНИЙ поділ праці — і саме він вирішив, хто переживе зростання флешу",
              11.5, GREY, "middle", style="italic")

    # ── ліворуч: гола NAND (SmartMedia, xD) ──
    s += rect(50, 84, 400, 392, "#fdf6f6", RED, 2, 12)
    s += text(250, 110, "SmartMedia · xD — ГОЛА NAND", 14, RED, "middle", "bold")
    s += text(250, 128, "(картка = просто чип пам'яті)", 10, GREY, "middle", style="italic")
    # картка = лише NAND
    s += rect(150, 146, 200, 56, "#ffffff", RED, 1.8, 6)
    s += text(250, 170, "NAND-флеш", 12.5, RED, "middle", "bold")
    s += text(250, 188, "(плавучий затвор, §3.6.8)", 9.5, GREY, "middle")
    # уся «брудна робота» лягає на пристрій
    s += arrow(250, 206, 250, 244, RED, 2.4)
    s += text(366, 226, "уся робота — на ПРИСТРІЙ", 10, RED, "start", "bold")
    s += rect(96, 250, 308, 150, "#ffffff", INK, 1.6, 8)
    s += text(250, 272, "ПРИСТРІЙ (камера) мусить сам:", 11.5, INK, "middle", "bold")
    for i, t in enumerate([
        "• вести таблицю зношення (wear leveling)",
        "• обходити биті комірки (bad blocks)",
        "• рахувати й виправляти помилки (ECC, §3.9)",
        "• знати ТОЧНУ організацію цього чипа",
    ]):
        s += text(116, 296 + i * 22, t, 11, INK, "start")
    s += rect(96, 412, 308, 50, "#fdf4f4", RED, 1.6, 8)
    s += text(250, 432, "Новий, більший чип NAND → камера його", 10.5, RED, "middle", "bold")
    s += text(250, 449, "вже НЕ розуміє. Стелю вперлися на 128 МБ.", 10.5, RED, "middle", "bold")

    # ── праворуч: NAND + контролер (CF, SD) ──
    s += rect(470, 84, 400, 392, "#f4f7f4", GREEN, 2, 12)
    s += text(670, 110, "CompactFlash · SD — NAND + КОНТРОЛЕР", 13, GREEN, "middle", "bold")
    s += text(670, 128, "(картка ховає всю складність у собі)", 10, GREY, "middle", style="italic")
    s += rect(560, 146, 220, 116, "#ffffff", GREEN, 1.8, 8)
    s += text(670, 168, "усередині КАРТКИ:", 11, GREEN, "middle", "bold")
    s += rect(580, 180, 80, 60, "#eef7ee", GREEN, 1.5, 5)
    s += text(620, 206, "NAND", 11, GREEN, "middle", "bold")
    s += text(620, 222, "чип(и)", 9.5, GREY, "middle")
    s += rect(680, 180, 80, 60, "#eef7ee", GREEN, 1.5, 5)
    s += text(720, 202, "контро-", 10.5, GREEN, "middle", "bold")
    s += text(720, 216, "лер", 10.5, GREEN, "middle", "bold")
    s += arrow(660, 210, 678, 210, GREEN, 2)
    s += rect(560, 274, 220, 126, "#ffffff", INK, 1.6, 8)
    s += text(670, 296, "контролер сам, ПРИХОВАНО:", 11, INK, "middle", "bold")
    for i, t in enumerate([
        "• рознесе запис рівномірно",
        "• обійде биті комірки",
        "• порахує ECC і сховає помилки",
        "• віддасть назовні рівні «сектори»",
    ]):
        s += text(580, 320 + i * 22, t, 11, INK, "start")
    s += rect(560, 412, 220, 50, "#eef7ee", GREEN, 1.6, 8)
    s += text(670, 432, "Пристрій бачить ПРОСТИЙ диск.", 10.5, GREEN, "middle", "bold")
    s += text(670, 449, "Новий чип? Картка сама все ховає.", 10.5, GREEN, "middle", "bold")

    # стрілка-висновок
    s += text(W / 2, 500, "Гола NAND дешевша СЬОГОДНІ — та прив'язує картку до конкретного чипа й валить тягар ECC на камеру.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 524, "Контролер у картці коштує копійки, зате робить її САМОДОСТАТНЬОЮ й сумісною наперед. Цю ставку SD виграла.",
              11, GREY, "middle", style="italic")
    save("fig-r08-s6h-2-controller.svg", s)


# ═══════════ Рис. 3.8.6h.3 — чому перемогла саме SD (матриця) ═══════════════
def fig_why_sd():
    W, H = 940, 486
    s = header(W, H)
    s += text(W / 2, 34, "Чому перемогла саме SD: не один козир, а найкращий КОМПРОМІС", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "жоден формат не вигравав за всіма осями; SD програвала дрібницями, та зібрала разом усе, що важило ринку",
              11.5, GREY, "middle", style="italic")

    cols = [
        ("CompactFlash", BLUE),
        ("SmartMedia", RED),
        ("Memory Stick", AMBER),
        ("SD", GREEN),
    ]
    rows = [
        "Відкритий стандарт\n(будь-хто робить картки)",
        "Контролер у КАРТЦІ\n(сумісність наперед)",
        "Маленька, для кишені\n(телефони, плеєри)",
        "Захист від запису\nй міцний корпус",
        "Широка коаліція фірм\n(а не один власник)",
    ]
    # значення: 1 = так(✓), 0 = ні(✗), 2 = частково(~)
    M = [
        [1, 1, 0, 2],   # відкритий
        [1, 0, 1, 1],   # контролер у картці
        [0, 1, 1, 1],   # маленька
        [0, 0, 1, 1],   # захист/корпус
        [1, 0, 0, 1],   # коаліція
    ]
    x0, y0 = 360, 92
    cw, rh = 138, 64
    # заголовки колонок
    for c, (name, col) in enumerate(cols):
        cx = x0 + c * cw + cw / 2
        hl = (name == "SD")
        s += rect(x0 + c * cw + 6, 70, cw - 12, 28, col if hl else "#ffffff", col, 2 if hl else 1.4, 6)
        s += text(cx, 89, name, 12, "#ffffff" if hl else col, "middle", "bold")
    # рядки-критерії + клітинки
    for r, label in enumerate(rows):
        ry = y0 + r * rh
        s += rect(40, ry, x0 - 52, rh - 8, "#fafafa", GREY, 1.2, 6)
        for j, ln in enumerate(label.split("\n")):
            s += text(54, ry + 24 + j * 17, ln, 11, INK, "start", "bold" if j == 0 else "normal")
        for c, (name, col) in enumerate(cols):
            cx = x0 + c * cw + cw / 2
            cy = ry + (rh - 8) / 2
            if name == "SD":
                s += rect(x0 + c * cw + 6, ry, cw - 12, rh - 8, "#f4faf4", GREEN, 1.2, 6)
            v = M[r][c]
            if v == 1:
                s += _check(cx, cy)
            elif v == 0:
                s += _cross(cx, cy)
            else:
                s += _tilde(cx, cy)
    # легенда
    ly = y0 + len(rows) * rh + 8
    s += _check(60, ly); s += text(74, ly + 4, "так", 11, INK, "start")
    s += _tilde(150, ly); s += text(164, ly + 4, "частково", 11, INK, "start")
    s += _cross(280, ly); s += text(294, ly + 4, "ні", 11, INK, "start")
    s += text(W / 2, ly + 2, "SD: ✓ у кожному рядку, що важив (відкритість — «~»: ліцензія платна,",
              10.5, GREY, "middle", style="italic")
    s += text(W / 2, ly + 19, "та доступна всім — на відміну від закритого Memory Stick).",
              10.5, GREY, "middle", style="italic")
    s += rect(40, ly + 34, W - 80, 44, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, ly + 58, "Підсумок: CF — завелика, SmartMedia — гола й глуха до росту, Memory Stick — закрита й «лише для Sony». "
                              "SD не була найкращою в жодній графі — вона була ДОСИТЬ доброю в усіх.",
              11, INK, "middle", "bold")
    save("fig-r08-s6h-3-why-sd.svg", s)


if __name__ == "__main__":
    fig_timeline()
    fig_controller()
    fig_why_sd()
    print("done:", OUT)
