# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 3.9 — «Коди виявлення й корекції помилок» (Модуль 3).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; «1» червоний, «0» синій; «добре/поле» зелене;
стрілки через marker; шрифт sans-serif. Підписи — за темою (Рис. 3.9.T.k).
Імена файлів: fig-3-9-<T>-<k>-<slug>.svg. Скрипт нарощується по темах.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"   # «1», помилка, перевернутий біт
BLUE  = "#1f47b5"   # «0»
GREEN = "#1f8a3b"   # коректно, поле даних, «гоїться»
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"   # надлишковість, контроль
VIOL  = "#7a3da8"
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
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", AMBER: "aAmber"}


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


def polygon(points, fill="none", stroke=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── спільний помічник: намалювати ряд бітових клітинок ──────────────────────
def bitrow(x, y, bits, cell=30, gap=4, hi=RED, lo=BLUE, flip=None, faint=None,
           labels=None, size=16):
    """bits — рядок '0'/'1'. flip — множина індексів, обведених як помилка.
       faint — індекси, намальовані сірим (контекст). labels — підписи під клітинками."""
    out = ""
    flip = flip or set()
    faint = faint or set()
    for i, b in enumerate(bits):
        cx = x + i * (cell + gap)
        col = GREY if i in faint else (hi if b == "1" else lo)
        edge = RED if i in flip else "#cccccc"
        ew = 3 if i in flip else 1.2
        out += rect(cx, y, cell, cell, "#ffffff", edge, ew, 4)
        out += text(cx + cell / 2, y + cell * 0.71, b, size, col, "middle", "bold")
        if labels and i < len(labels) and labels[i]:
            out += text(cx + cell / 2, y + cell + 15, labels[i], 11, GREY, "middle")
    return out


# ════════════════════════════════════════════════════════════════════════════
#  ТЕМА 3.9.1 — Звідки беруться перевернуті біти
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 3.9.1.1 — карта джерел перевернутих бітів ──────────────────────────
def fig_1_sources():
    W, H = 880, 560
    s = header(W, H)
    s += text(W / 2, 36, "Звідки беруться перевернуті біти: чотири класи причин", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "у каналі (передача) і в комірці (зберігання) — фізика щоразу інша, наслідок один: 0↔1",
              12.5, GREY, "middle", style="italic")
    # центр — біт, що перевертається
    cx, cy = W / 2, 300
    s += circle(cx, cy, 56, "#fff", INK, 2.4)
    s += text(cx, cy - 8, "0 → 1", 22, RED, "middle", "bold")
    s += text(cx, cy + 16, "1 → 0", 22, BLUE, "middle", "bold")
    s += text(cx, cy + 40, "перевернутий біт", 12, GREY, "middle", style="italic")
    boxes = [
        (150, 150, "Тепловий шум", "теплове коливання носіїв; на межі рівнів (§3.1.3) «0» можна\nпрочитати як «1». Зростає з температурою.", BLUE),
        (590, 150, "Завади в каналі", "наведення, відбиття, перехресні\nперешкоди на довгому дроті чи в радіо; кадр приходить спотвореним.", AMBER),
        (150, 430, "Іонізуюча частинка", "космічний протон/нейтрон чи альфа\nвибиває заряд із комірки — SEU (§3.9.1m). Рідко, але невідворотно.", VIOL),
        (590, 430, "Знос комірки", "Flash/EEPROM мають скінченний ресурс\nперезапису; заряд «тече» з часом — retention. Биті ламаються.", GREEN),
    ]
    for bx, by, ttl, body, col in boxes:
        w, h = 250, 96
        x0 = bx - w / 2
        y0 = by - h / 2
        s += rect(x0, y0, w, h, "#fff", col, 2.2, 9)
        s += text(bx, y0 + 22, ttl, 15, col, "middle", "bold")
        for j, ln in enumerate(body.split("\n")):
            s += text(x0 + 12, y0 + 42 + j * 16, ln, 10.7, INK, "start")
        # стрілка до центру
        s += arrow(bx + (90 if bx < cx else -90) * (1 if bx < cx else 1) * 0, by, cx, cy, col, 1.8, "5 4")
    # коректні стрілки до центру (по діагоналях)
    s += line(265, 175, cx - 44, cy - 30, GREY, 1.4, "4 4")
    s += line(W - 265, 175, cx + 44, cy - 30, GREY, 1.4, "4 4")
    s += line(265, 410, cx - 44, cy + 30, GREY, 1.4, "4 4")
    s += line(W - 265, 410, cx + 44, cy + 30, GREY, 1.4, "4 4")
    s += text(W / 2, 540, "Висновок: помилки неминучі — питання лише в їхній частоті. Тому потрібен не «ідеальний канал», а КОД, що їх ловить.",
              12.5, INK, "middle", "bold")
    save("fig-3-9-1-1-sources.svg", s)


# ── Рис. 3.9.1.2 — масштаб: BER і скільки це помилок ────────────────────────
def fig_1_scale():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 36, "Масштаб проблеми: рідкісна подія × величезний потік = постійні помилки", 19, INK, "middle", "bold")
    s += text(W / 2, 57, "ймовірність помилки на біт (BER) мала, але бітів — мільярди щосекунди",
              12.5, GREY, "middle", style="italic")
    rows = [
        ("Тиха кімната, RAM", "1 fit/Мбіт", "сервер на 64 ГБ", "≈ кілька збоїв на рік", VIOL),
        ("UART, довгий шлейф", "BER 10⁻⁶", "1 Мбіт/с потік", "≈ 1 битий біт за секунду", AMBER),
        ("Радіо на межі", "BER 10⁻³", "кадр 256 байт", "≈ 2 биті біти в кадрі", RED),
        ("Зношена NAND", "10⁻² на комірку", "сторінка 16 кбіт", "сотні бітів — без ECC мертва", GREEN),
    ]
    x0, y0 = 60, 100
    colx = [70, 290, 470, 650]
    heads = ["Середовище", "Частота помилки", "Потік / обсяг", "Що це означає"]
    for i, hh in enumerate(heads):
        s += text(colx[i], y0 - 12, hh, 13, INK, "start", "bold")
    s += line(x0, y0 - 4, W - 50, y0 - 4, GREY, 1.5)
    for r, (env, ber, flow, res, col) in enumerate(rows):
        yy = y0 + 28 + r * 64
        s += rect(x0, yy - 20, W - 110, 52, "#fbfbfb", FAINT, 1.2, 6)
        s += text(colx[0], yy + 2, env, 13.5, col, "start", "bold")
        s += text(colx[1], yy + 2, ber, 14, INK, "start", "bold")
        s += text(colx[2], yy + 2, flow, 12.5, INK, "start")
        s += text(colx[3], yy + 2, res, 12.5, INK, "start")
        s += text(colx[3], yy + 20, "", 11, GREY, "start")
    s += text(W / 2, H - 18,
              "Одна помилка на мільйон бітів здається дрібницею — поки не згадаєш, що мільйон бітів пролітає за частку секунди.",
              12.5, INK, "middle", style="italic")
    save("fig-3-9-1-2-scale.svg", s)


# ── Рис. 3.9.1.3 — звужена «яма» рівнів як корінь помилки (місток до §3.1.3) ─
def fig_1_margin():
    W, H = 880, 430
    s = header(W, H)
    s += text(W / 2, 34, "Корінь усього: шум поїдає запас між «0» і «1» (місток до §3.1.3)", 19, INK, "middle", "bold")
    # дві панелі: свіжа vs зношена/зашумлена комірка
    def panel(ox, title, gap, ok, subtitle):
        out = text(ox + 150, 78, title, 15, INK, "middle", "bold")
        out += text(ox + 150, 96, subtitle, 11.5, GREY, "middle", style="italic")
        bx, bw, btop, bbot = ox + 40, 220, 120, 320
        out += rect(bx, btop, bw, bbot - btop, "#fff", INK, 1.6)
        # рівні «0» (низ) і «1» (верх)
        lo_top = bbot - 40
        hi_bot = btop + 40
        out += rect(bx, lo_top, bw, bbot - lo_top, "#eaf0ff", BLUE, 0)
        out += rect(bx, btop, bw, hi_bot - btop, "#fdeceb", RED, 0)
        out += text(bx + bw + 8, hi_bot - 6, "«1»", 13, RED, "start", "bold")
        out += text(bx + bw + 8, lo_top + 18, "«0»", 13, BLUE, "start", "bold")
        # «яма» між ними
        mid = (hi_bot + lo_top) / 2
        out += line(bx - 14, hi_bot, bx - 14, lo_top, GREEN if ok else RED, 3)
        out += line(bx - 18, hi_bot, bx - 10, hi_bot, GREEN if ok else RED, 3)
        out += line(bx - 18, lo_top, bx - 10, lo_top, GREEN if ok else RED, 3)
        out += text(bx - 22, mid + 4, "запас", 12, GREEN if ok else RED, "end", "bold")
        # хмарка шуму
        import math
        pts = []
        amp = 8 if ok else 30
        for k in range(0, 121):
            xx = bx + bw * k / 120
            yy = mid + amp * math.sin(k / 6.0) * (0.6 + 0.4 * math.sin(k / 2.3))
            pts.append((xx, yy))
        out += polyline(pts, GREY, 1.6)
        out += text(bx + bw / 2, mid - amp - 8 if ok else btop + 16, "розмах шуму", 11, GREY, "middle", style="italic")
        return out
    s += panel(20, "Свіжа комірка / тихий канал", 120, True,
               "широка «яма» — шум не дістає сусіднього рівня")
    s += panel(460, "Зношена комірка / завада", 60, False,
               "«яма» звузилась — пік шуму перестрибує межу → біт перевернувся")
    s += text(W / 2, H - 18,
              "Тепло, знос, частинка, завада — усе зводиться до одного: пік шуму перетнув межу рівня. Звідси й усі помилки.",
              12.5, INK, "middle", style="italic")
    save("fig-3-9-1-3-margin.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  ТЕМА 3.9.2 — Біт парності
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 3.9.2.1 — як рахується біт парності (XOR усіх бітів) ────────────────
def fig_2_parity():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 34, "Біт парності: один зайвий біт робить кількість одиниць парною", 19, INK, "middle", "bold")
    s += text(W / 2, 55, "парність (parity) = XOR усіх бітів даних (§3.2.4); додаємо його — і одиниць стає парне число",
              12.5, GREY, "middle", style="italic")
    data = "1011010"
    x0, y0 = 150, 110
    s += text(x0 - 14, y0 + 21, "дані:", 13, INK, "end")
    s += bitrow(x0, y0, data, 34, 6)
    nx = x0 + len(data) * 40 + 18
    # P-біт
    ones = data.count("1")
    p = "1" if ones % 2 else "0"
    s += rect(nx, y0, 34, 34, "#fff8e8", AMBER, 2.6, 4)
    s += text(nx + 17, y0 + 24, p, 16, AMBER, "middle", "bold")
    s += text(nx + 17, y0 + 50, "P", 12, AMBER, "middle", "bold")
    s += text(nx + 60, y0 + 21, "= біт парності", 12.5, AMBER, "start", "bold")
    # підрахунок
    yc = y0 + 95
    s += text(x0 - 14, yc + 4, "лічимо:", 13, INK, "end")
    s += text(x0, yc + 4, f"одиниць у даних = {ones} (непарно)", 13.5, INK, "start")
    s += text(x0, yc + 26, f"щоб разом стало ПАРНО, ставимо P = {p}", 13.5, AMBER, "start", "bold")
    s += text(x0, yc + 48, f"тепер одиниць = {ones + int(p)} — парно ✓ (even parity)", 13.5, GREEN, "start", "bold")
    # передаємо й перевіряємо
    yb = y0 + 250
    s += line(60, yb - 22, W - 60, yb - 22, FAINT, 1.4)
    s += text(60, yb - 4, "Приймач рахує одиниці в усіх 8 бітах:", 13.5, INK, "start", "bold")
    s += text(80, yb + 22, "• сума парна  → помилки (однієї) не було", 13, GREEN, "start")
    s += text(80, yb + 44, "• сума непарна → один біт перевернувся — кадр битий!", 13, RED, "start")
    s += text(80, yb + 66, "Самого P досить, щоб ПОБАЧИТИ помилку, але не щоб знати ДЕ вона.", 12.5, GREY, "start", style="italic")
    save("fig-3-9-2-1-parity.svg", s)


# ── Рис. 3.9.2.2 — сліпа пляма: парне число помилок невидиме ─────────────────
def fig_2_blindspot():
    W, H = 880, 440
    s = header(W, H)
    s += text(W / 2, 34, "Сліпа пляма парності: дві помилки маскують одна одну", 19, INK, "middle", "bold")
    s += text(W / 2, 55, "парність ловить НЕПАРНЕ число помилок (1, 3, 5…) і ПРОПУСКАЄ парне (2, 4…)",
              12.5, GREY, "middle", style="italic")
    base = "10110100"   # 7 даних + P, парна
    x0 = 230
    rows = [
        (110, "0 помилок", base, set(), "сума парна → OK ✓", GREEN, True),
        (200, "1 помилка", "10010100", {2}, "сума непарна → ВИЯВЛЕНО ✓", GREEN, True),
        (290, "2 помилки", "10010110", {2, 6}, "сума знову ПАРНА → пропущено ✗", RED, False),
    ]
    for yy, label, bits, flip, verdict, col, good in rows:
        s += text(x0 - 16, yy + 21, label, 13, INK, "end", "bold")
        s += bitrow(x0, yy, bits, 32, 6, flip=flip)
        nx = x0 + 8 * 38 + 16
        s += text(nx, yy + 21, verdict, 13.5, col, "start", "bold")
    s += text(W / 2, H - 26,
              "Перевернути будь-які ДВА біти — і кількість одиниць лишається парною. Детектор мовчить, дані зіпсуто.",
              13, RED, "middle", "bold")
    s += text(W / 2, H - 8,
              "Звідси висновок: парність — найдешевший детектор для каналів, де помилки рідкі й поодинокі (як UART). Для пакетних завад її замало.",
              11.5, GREY, "middle", style="italic")
    save("fig-3-9-2-2-blindspot.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  ТЕМА 3.9.3 — Контрольні суми
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 3.9.3.1 — проста сума й чому вона сліпа до перестановки ─────────────
def fig_3_sum():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 34, "Проста контрольна сума: складаємо байти — і одне число «підпис» цілого блоку", 18, INK, "middle", "bold")
    s += text(W / 2, 55, "checksum = (b₁ + b₂ + … + bₙ) mod 256 — дешево, але «глуха» до порядку",
              12.5, GREY, "middle", style="italic")
    bytes_ = [0x12, 0x34, 0x56, 0x78]
    x0, y0 = 90, 110
    for i, b in enumerate(bytes_):
        bx = x0 + i * 90
        s += rect(bx, y0, 70, 38, "#eaf0ff", BLUE, 1.6, 5)
        s += text(bx + 35, y0 + 25, f"0x{b:02X}", 15, INK, "middle", "bold")
        if i < 3:
            s += text(bx + 80, y0 + 25, "+", 18, INK, "middle", "bold")
    summ = sum(bytes_) & 0xFF
    bx = x0 + 4 * 90 + 10
    s += text(bx - 8, y0 + 25, "=", 18, INK, "middle", "bold")
    s += rect(bx + 12, y0, 78, 38, "#fff8e8", AMBER, 2.4, 5)
    s += text(bx + 51, y0 + 25, f"0x{summ:02X}", 15, AMBER, "middle", "bold")
    s += text(bx + 51, y0 + 56, "checksum", 11.5, AMBER, "middle", "bold")
    # сліпа пляма — перестановка
    yb = 250
    s += line(60, yb - 18, W - 60, yb - 18, FAINT, 1.4)
    s += text(60, yb, "Сліпа пляма: переставимо байти місцями —", 14, RED, "start", "bold")
    perm = [0x34, 0x12, 0x78, 0x56]
    for i, b in enumerate(perm):
        bx = x0 + i * 90
        s += rect(bx, yb + 16, 70, 36, "#fdeceb", RED, 1.6, 5)
        s += text(bx + 35, yb + 40, f"0x{b:02X}", 14, INK, "middle", "bold")
        if i < 3:
            s += text(bx + 80, yb + 40, "+", 16, INK, "middle")
    s += text(x0 + 4 * 90 + 2, yb + 40, "=", 16, INK, "middle")
    s += rect(x0 + 4 * 90 + 22, yb + 16, 78, 36, "#fff8e8", AMBER, 2.4, 5)
    s += text(x0 + 4 * 90 + 61, yb + 40, f"0x{summ:02X}", 14, AMBER, "middle", "bold")
    s += text(W / 2, yb + 92, "Сума ТА САМА — а дані інші! Проста сума не бачить перестановки байтів і взаємних +1/−1.",
              13.5, RED, "middle", "bold")
    s += text(W / 2, yb + 116, "Саме цю діру закриває Флетчер: він зважує байти за позицією.",
              12.5, GREY, "middle", style="italic")
    save("fig-3-9-3-1-sum.svg", s)


# ── Рис. 3.9.3.2 — Флетчер: дві суми, одна зважена позицією ──────────────────
def fig_3_fletcher():
    W, H = 880, 500
    s = header(W, H)
    s += text(W / 2, 34, "Контрольна сума Флетчера: друга сума «запам'ятовує» позицію", 19, INK, "middle", "bold")
    s += text(W / 2, 55, "sum1 накопичує байти; sum2 накопичує sum1 — тож вага байта залежить від місця",
              12.5, GREY, "middle", style="italic")
    data = [0x12, 0x34, 0x56, 0x78]
    x0, y0 = 110, 100
    # таблиця кроків
    heads = ["крок", "байт", "sum1 += байт", "sum2 += sum1"]
    colx = [x0, x0 + 110, x0 + 230, x0 + 430]
    for i, hh in enumerate(heads):
        s += text(colx[i], y0, hh, 13, INK, "start", "bold")
    s += line(x0, y0 + 8, x0 + 600, y0 + 8, GREY, 1.4)
    s1 = s2 = 0
    for i, b in enumerate(data):
        s1 = (s1 + b) % 255
        s2 = (s2 + s1) % 255
        yy = y0 + 36 + i * 34
        s += text(colx[0], yy, str(i + 1), 13, GREY, "start")
        s += text(colx[1], yy, f"0x{b:02X}", 13.5, BLUE, "start", "bold")
        s += text(colx[2], yy, f"{s1}", 13.5, INK, "start")
        s += text(colx[3], yy, f"{s2}", 13.5, AMBER, "start", "bold")
    yy = y0 + 36 + 4 * 34 + 8
    s += line(x0, yy - 4, x0 + 600, yy - 4, FAINT, 1.2)
    s += text(colx[1], yy + 16, "Контрольна сума:", 13.5, INK, "start", "bold")
    s += text(colx[2], yy + 16, f"sum1 = {s1}", 13.5, INK, "start", "bold")
    s += text(colx[3], yy + 16, f"sum2 = {s2}", 13.5, AMBER, "start", "bold")
    # чому ловить перестановку
    yb = 380
    s += line(60, yb - 14, W - 60, yb - 14, FAINT, 1.4)
    s += text(60, yb + 6, "Чому Флетчер ловить те, що проста сума пропускає:", 13.5, GREEN, "start", "bold")
    s += text(80, yb + 30, "• байт на позиції 1 додається до sum1 чотири рази (на кожному наступному кроці теж),", 12.5, INK, "start")
    s += text(80, yb + 50, "  а байт на позиції 4 — лише раз. Тож переставлені байти дають ІНШУ sum2.", 12.5, INK, "start")
    s += text(80, yb + 72, "Ціна — вдвічі ширша контрольна сума й трохи більше обчислень. Виявлення майже як у CRC, дешевше.", 12.5, GREY, "start", style="italic")
    save("fig-3-9-3-2-fletcher.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  ТЕМА 3.9.4 — CRC
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 3.9.4.1 — CRC як ділення в стовпчик над GF(2) (XOR) ─────────────────
def fig_4_division():
    W, H = 880, 560
    s = header(W, H)
    s += text(W / 2, 34, "CRC: дані ділимо «в стовпчик» на многочлен, остача — і є контроль", 18, INK, "middle", "bold")
    s += text(W / 2, 55, "ділення двійкове, але без позик: віднімання — це XOR (§3.2.4). Остача коротша за дільник.",
              12.5, GREY, "middle", style="italic")
    # ілюстративне ділення: 11010011 . 000 / 1011  (CRC-3, поліном 1011)
    mono = "x³+x+1  →  1011"
    s += text(W / 2, 84, f"дільник (поліном): {mono}", 14, AMBER, "middle", "bold")
    # рядки ділення
    lines = [
        ("11010011000", 0, INK, "дані з 3 нулями в хвості"),
        ("1011", 0, RED, "XOR"),
        ("01100011000", 1, INK, ""),
        (" 1011", 2, RED, "XOR"),
        ("00111011000", 1, INK, ""),
        ("  1011", 3, RED, "XOR"),
        ("00010111000", 1, INK, ""),
        ("    1011", 5, RED, "XOR"),
        ("00000001100", 1, INK, ""),
        ("          ", 0, INK, ""),
    ]
    x0, y0 = 250, 130
    chw = 15
    for i, (txt, sh, col, note) in enumerate(lines):
        yy = y0 + i * 30
        # моноширинний рядок
        for j, ch in enumerate(txt):
            if ch == " ":
                continue
            cx = x0 + (j) * chw
            cc = RED if (col == RED) else (RED if ch == "1" else BLUE)
            if col == RED:
                cc = AMBER
            s += text(cx, yy, ch, 16, cc, "middle", "bold")
        if note:
            s += text(x0 + 12 * chw + 30, yy, note, 12, GREY, "start", style="italic")
        if col == RED:
            # лінія XOR
            s += line(x0 - 6 + sh * chw - chw / 2, yy + 6, x0 + sh * chw + 4 * chw - chw / 2, yy + 6, GREY, 1.2)
    # остача
    yrem = y0 + 9 * 30 + 6
    s += text(x0, yrem, "остача (CRC) = 100", 16, GREEN, "start", "bold")
    s += text(x0 + 220, yrem, "← її дописують до даних замість нулів", 12.5, GREY, "start", style="italic")
    # перевірка
    s += text(60, yrem + 40, "Приймач ділить ВЕСЬ прийнятий блок (дані+CRC) на той самий поліном:", 13, INK, "start", "bold")
    s += text(80, yrem + 64, "• остача 0 → помилки немає;   • остача ≠ 0 → блок битий.", 13, INK, "start")
    s += text(80, yrem + 86, "Один зсувний регістр зі зворотним XOR робить це апаратно за такт на біт (§3.9.4c).", 12.5, GREY, "start", style="italic")
    save("fig-3-9-4-1-division.svg", s)


# ── Рис. 3.9.4.2 — зсувний регістр зі зворотним зв'язком (LFSR) ──────────────
def fig_4_lfsr():
    W, H = 880, 360
    s = header(W, H)
    s += text(W / 2, 34, "Залізо CRC: зсувний регістр зі зворотними XOR за одиницями полінома", 18, INK, "middle", "bold")
    s += text(W / 2, 55, "поліном 1011 → XOR-крани там, де в ньому одиниці; біти даних «вливаються» по одному",
              12.5, GREY, "middle", style="italic")
    # 3 тригери
    n = 3
    bx, by, bw = 250, 150, 90
    gap = 60
    for i in range(n):
        x = bx + i * (bw + gap)
        s += rect(x, by, bw, 56, "#fff", INK, 2, 6)
        s += text(x + bw / 2, by + 35, f"D{i}", 18, INK, "middle", "bold")
        s += text(x + bw / 2, by - 8, f"біт {i}", 11, GREY, "middle")
        if i < n - 1:
            s += arrow(x + bw, by + 28, x + bw + gap, by + 28, INK, 2)
    # вхід даних
    s += arrow(120, by + 28, bx, by + 28, GREEN, 2.2)
    s += text(120, by + 14, "біти даних →", 12.5, GREEN, "start", "bold")
    # зворотний зв'язок з виходу
    outx = bx + (n - 1) * (bw + gap) + bw
    s += line(outx, by + 28, outx + 30, by + 28, INK, 2)
    s += line(outx + 30, by + 28, outx + 30, by + 110, INK, 2)
    s += line(outx + 30, by + 110, 120, by + 110, INK, 2)
    s += line(120, by + 110, 120, by + 28, INK, 2)
    # XOR-крани (за одиницями 1011 між розрядами)
    for i, tapx in enumerate([bx + bw + gap / 2, bx + 2 * (bw + gap) - gap / 2 - bw]):
        pass
    # позначка XOR на вході та між D0/D1 (поліном x^3+x+1 → крани на 0 і 1)
    xor1 = bx + bw + gap / 2
    s += circle(xor1, by + 28, 12, "#fff", RED, 2)
    s += text(xor1, by + 33, "⊕", 16, RED, "middle", "bold")
    s += line(xor1, by + 110, xor1, by + 40, RED, 1.8, "4 3")
    s += text(W / 2, H - 26, "Кожен такт: зсув праворуч + XOR у «кранах». Після останнього біта в регістрі лежить готова CRC.",
              12.5, INK, "middle", style="italic")
    s += text(W / 2, H - 8, "Саме тому CRC коштує апаратно майже нічого — і стоїть у CAN, Ethernet, SD, USB, у кадрах поверх UART.",
              12, GREY, "middle", style="italic")
    save("fig-3-9-4-2-lfsr.svg", s)


# ── Рис. 3.9.4.3 — де живе CRC: карта застосувань ───────────────────────────
def fig_4_everywhere():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "Чому CRC скрізь: один і той самий прийом у кожному надійному каналі", 18, INK, "middle", "bold")
    items = [
        ("CAN-шина", "CRC-15", "кадр у машині/дроні — §6.4.5", RED),
        ("Ethernet", "CRC-32", "кінець кожного кадру — §6.10.1", BLUE),
        ("SD-карта", "CRC-7/16", "команди й блоки даних — §3.8", GREEN),
        ("USB", "CRC-5/16", "токени й пакети даних", VIOL),
        ("Кадр поверх UART", "CRC-16", "ваш протокол — §6.1.6", AMBER),
        ("ZIP / PNG", "CRC-32", "цілісність файлу на диску", INK),
    ]
    cols, rows = 3, 2
    cw, ch = 260, 120
    ox, oy = 50, 90
    for k, (name, crc, where, col) in enumerate(items):
        r, c = divmod(k, cols)
        x = ox + c * (cw + 12)
        y = oy + r * (ch + 20)
        s += rect(x, y, cw, ch, "#fff", col, 2.2, 9)
        s += text(x + cw / 2, y + 30, name, 16, col, "middle", "bold")
        s += text(x + cw / 2, y + 60, crc, 18, INK, "middle", "bold")
        s += text(x + cw / 2, y + 88, where, 11.5, GREY, "middle")
    s += text(W / 2, H - 16,
              "Скрізь та сама ідея: дописати остачу від ділення на поліном. Різні лише ширина CRC і сам поліном.",
              12.5, INK, "middle", style="italic")
    save("fig-3-9-4-3-everywhere.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  ТЕМА 3.9.5 — Відстань Геммінга
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 3.9.5.1 — куб 3-біт: відстань як кількість ребер ────────────────────
def fig_5_cube():
    W, H = 880, 520
    s = header(W, H)
    s += text(W / 2, 34, "Відстань Геммінга: скільки бітів різнить два слова = скільки «кроків» по кубу", 17.5, INK, "middle", "bold")
    s += text(W / 2, 55, "усі 3-бітні слова — вершини куба; ребро з'єднує слова, що різняться рівно одним бітом",
              12.5, GREY, "middle", style="italic")
    # ізометричний куб
    cx, cy = 300, 300
    S = 120
    dx, dy = 70, 40
    def P(x, y, z):
        return (cx + (x - 0.5) * S + (z - 0.5) * dx, cy - (y - 0.5) * S + (z - 0.5) * dy)
    verts = {
        "000": P(0, 0, 0), "100": P(1, 0, 0), "110": P(1, 1, 0), "010": P(0, 1, 0),
        "001": P(0, 0, 1), "101": P(1, 0, 1), "111": P(1, 1, 1), "011": P(0, 1, 1),
    }
    edges = [("000", "100"), ("100", "110"), ("110", "010"), ("010", "000"),
             ("001", "101"), ("101", "111"), ("111", "011"), ("011", "001"),
             ("000", "001"), ("100", "101"), ("110", "111"), ("010", "011")]
    for a, b in edges:
        xa, ya = verts[a]
        xb, yb = verts[b]
        s += line(xa, ya, xb, yb, FAINT, 2)
    # підсвітити шлях 000 -> 011 (відстань 2)
    for a, b in [("000", "010"), ("010", "011")]:
        xa, ya = verts[a]
        xb, yb = verts[b]
        s += line(xa, ya, xb, yb, RED, 3)
    for name, (vx, vy) in verts.items():
        hi = name in ("000", "011")
        s += circle(vx, vy, 17, "#fff", INK if not hi else RED, 2.4 if hi else 1.6)
        col = RED if hi else INK
        s += text(vx, vy + 5, name, 12, col, "middle", "bold")
    s += text(verts["000"][0] - 24, verts["000"][1] + 6, "", 12, RED, "end")
    s += text(cx, cy + 200, "d(000, 011) = 2  (два ребра)", 15, RED, "middle", "bold")
    # права панель — правило
    rx = 600
    s += rect(rx, 110, 250, 330, "#fbfbfb", FAINT, 1.4, 10)
    s += text(rx + 125, 138, "Правило коду", 15, INK, "middle", "bold")
    s += text(rx + 16, 172, "d — мінімальна відстань", 12.5, INK, "start", "bold")
    s += text(rx + 16, 190, "між БУДЬ-ЯКИМИ двома", 12.5, INK, "start")
    s += text(rx + 16, 208, "дозволеними словами коду.", 12.5, INK, "start")
    s += line(rx + 16, 224, rx + 234, 224, FAINT, 1.2)
    s += text(rx + 16, 250, "виявити помилок:", 12.5, GREEN, "start", "bold")
    s += text(rx + 16, 270, "до  d − 1", 16, GREEN, "start", "bold")
    s += text(rx + 16, 304, "виправити помилок:", 12.5, RED, "start", "bold")
    s += text(rx + 16, 324, "до  ⌊(d − 1) / 2⌋", 16, RED, "start", "bold")
    s += line(rx + 16, 344, rx + 234, 344, FAINT, 1.2)
    s += text(rx + 16, 368, "Більша відстань —", 12, GREY, "start", style="italic")
    s += text(rx + 16, 386, "більше зайвих бітів,", 12, GREY, "start", style="italic")
    s += text(rx + 16, 404, "але й більша стійкість.", 12, GREY, "start", style="italic")
    save("fig-3-9-5-1-cube.svg", s)


# ── Рис. 3.9.5.2 — кулі навколо кодових слів: виявлення vs виправлення ───────
def fig_5_spheres():
    W, H = 880, 450
    s = header(W, H)
    s += text(W / 2, 34, "Геометрія: дозволені слова — острівці, помилка зсуває нас від берега", 18, INK, "middle", "bold")
    s += text(W / 2, 55, "що далі острівці один від одного (більше d), то більше помилок ми «бачимо» й «вертаємо»",
              12.5, GREY, "middle", style="italic")
    def island(cx, cy, name, d, can_correct):
        out = circle(cx, cy, 60, "#eef7ef", GREEN, 0)  # «куля виправлення»
        out += circle(cx, cy, 60, "none", GREEN, 1.6, )
        out += circle(cx, cy, 14, "#fff", INK, 2.4)
        out += text(cx, cy + 5, name, 12, INK, "middle", "bold")
        return out
    # дві кодові точки
    ax, ay = 270, 230
    bx, by = 610, 230
    s += line(ax, ay, bx, by, FAINT, 2, "6 5")
    s += text((ax + bx) / 2, ay - 80, "відстань d між словами", 12.5, GREY, "middle", style="italic")
    # кулі виправлення радіуса t
    s += circle(ax, ay, 70, "#eef7ef", GREEN, 1.6)
    s += circle(bx, by, 70, "#eef7ef", GREEN, 1.6)
    s += circle(ax, ay, 15, "#fff", BLUE, 2.6)
    s += text(ax, ay + 5, "A", 14, BLUE, "middle", "bold")
    s += circle(bx, by, 15, "#fff", BLUE, 2.6)
    s += text(bx, by + 5, "B", 14, BLUE, "middle", "bold")
    s += text(ax, ay + 92, "куля A: радіус t", 11.5, GREEN, "middle")
    s += text(bx, by + 92, "куля B: радіус t", 11.5, GREEN, "middle")
    # помилкова точка біля A
    ex, ey = ax + 38, ay - 28
    s += circle(ex, ey, 8, RED, RED, 0)
    s += text(ex + 12, ey - 6, "прийнято з помилкою", 11, RED, "start", "bold")
    s += arrow(ex, ey, ax + 13, ay - 10, RED, 1.8, "4 3")
    s += text(ax + 30, ay + 40, "ближче до A → вертаємо в A ✓", 11, RED, "middle")
    # пояснення відстаней
    yb = 360
    s += line(60, yb - 16, W - 60, yb - 16, FAINT, 1.4)
    s += text(60, yb + 4, "Якщо помилок ≤ t = ⌊(d−1)/2⌋ — точка ще в «своїй» кулі → виправимо однозначно.", 13, GREEN, "start", "bold")
    s += text(60, yb + 26, "Якщо помилок до d−1 — точка вийшла зі своєї кулі, але не дійшла чужої → бачимо, що щось не так (виявлення).", 13, AMBER, "start")
    s += text(60, yb + 48, "Якщо помилок ≥ d — могли потрапити в ЧУЖУ кулю → приймемо хибне слово за правильне (тиха помилка).", 13, RED, "start")
    save("fig-3-9-5-2-spheres.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  ТЕМА 3.9.6 — Код Геммінга (7,4)
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 3.9.6.1 — розкладка (7,4): де дані, де парності ─────────────────────
def fig_6_layout():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 34, "Код Геммінга (7,4): 4 біти даних + 3 біти парності = 7-бітне слово", 18, INK, "middle", "bold")
    s += text(W / 2, 55, "біти парності стоять на позиціях-степенях двійки (1, 2, 4); решта — дані",
              12.5, GREY, "middle", style="italic")
    pos = ["1", "2", "3", "4", "5", "6", "7"]
    kind = ["P1", "P2", "D1", "P4", "D2", "D3", "D4"]
    isP = [True, True, False, True, False, False, False]
    x0, y0 = 130, 110
    cw = 78
    for i in range(7):
        x = x0 + i * cw
        col = AMBER if isP[i] else GREEN
        fill = "#fff8e8" if isP[i] else "#eef7ef"
        s += rect(x, y0, cw - 8, 50, fill, col, 2.2, 6)
        s += text(x + (cw - 8) / 2, y0 + 33, kind[i], 17, col, "middle", "bold")
        s += text(x + (cw - 8) / 2, y0 - 8, f"поз. {pos[i]}", 11, GREY, "middle")
    # яка парність які позиції накриває
    s += text(x0 - 16, y0 + 100, "P1 (поз.1) перевіряє позиції 1,3,5,7  (молодший біт номера = 1)", 12.5, AMBER, "start")
    s += text(x0 - 16, y0 + 124, "P2 (поз.2) перевіряє позиції 2,3,6,7  (середній біт = 1)", 12.5, AMBER, "start")
    s += text(x0 - 16, y0 + 148, "P4 (поз.4) перевіряє позиції 4,5,6,7  (старший біт = 1)", 12.5, AMBER, "start")
    # діаграма Венна-натяк: позиції в двійці
    yv = y0 + 190
    s += line(60, yv, W - 60, yv, FAINT, 1.4)
    s += text(60, yv + 24, "Ключ — двійковий НОМЕР позиції:", 13.5, INK, "start", "bold")
    rows = [(1, "001"), (2, "010"), (3, "011"), (4, "100"), (5, "101"), (6, "110"), (7, "111")]
    bx = 360
    for i, (p, b) in enumerate(rows):
        x = bx + i * 70
        s += text(x, yv + 24, str(p), 13, INK, "middle", "bold")
        for j, ch in enumerate(b):
            s += text(x - 10 + j * 10, yv + 48, ch, 13, RED if ch == "1" else BLUE, "middle", "bold")
    s += text(60, yv + 80, "Кожна парність відповідає одному біту номера. Тому, як побачимо, три перевірки прямо вкажуть НОМЕР битої позиції.",
              12.5, GREY, "start", style="italic")
    save("fig-3-9-6-1-layout.svg", s)


# ── Рис. 3.9.6.2 — синдром прямо вказує номер битого біта ────────────────────
def fig_6_syndrome():
    W, H = 880, 500
    s = header(W, H)
    s += text(W / 2, 34, "Виправлення на пальцях: три перевірки дають двійковий НОМЕР битого біта", 17.5, INK, "middle", "bold")
    s += text(W / 2, 55, "приклад: передали коректне слово, у каналі перевернувся біт на позиції 5",
              12.5, GREY, "middle", style="italic")
    # слово з помилкою на позиції 5 (індекс 4)
    word = "0110011"  # ілюстративне
    x0, y0 = 200, 95
    cw = 62
    for i, b in enumerate(word):
        x = x0 + i * cw
        flip = (i == 4)
        s += rect(x, y0, cw - 8, 46, "#fff", RED if flip else "#cccccc", 3 if flip else 1.4, 6)
        s += text(x + (cw - 8) / 2, y0 + 31, b, 18, (RED if b == "1" else BLUE), "middle", "bold")
        s += text(x + (cw - 8) / 2, y0 - 8, str(i + 1), 11, (RED if flip else GREY), "middle", "bold")
    s += text(x0 + 4 * cw + (cw - 8) / 2, y0 + 66, "↑ тут помилка", 12, RED, "middle", "bold")
    # три перевірки
    yb = 200
    checks = [
        ("c4 = парність поз. 4,5,6,7", "не сходиться → 1", 1, AMBER),
        ("c2 = парність поз. 2,3,6,7", "сходиться → 0", 0, INK),
        ("c1 = парність поз. 1,3,5,7", "не сходиться → 1", 1, AMBER),
    ]
    for i, (lbl, res, bit, col) in enumerate(checks):
        yy = yb + i * 40
        s += text(120, yy, lbl, 13.5, INK, "start")
        s += text(470, yy, res, 13.5, col, "start", "bold")
        s += rect(650, yy - 18, 26, 26, "#fff8e8" if bit else "#fff", col, 2, 5)
        s += text(663, yy, str(bit), 15, col, "middle", "bold")
    # синдром
    ys = yb + 150
    s += line(60, ys - 14, W - 60, ys - 14, FAINT, 1.4)
    s += text(120, ys + 8, "синдром = c4 c2 c1 =", 15, INK, "start", "bold")
    for j, ch in enumerate("101"):
        s += text(380 + j * 26, ys + 8, ch, 18, RED if ch == "1" else BLUE, "middle", "bold")
    s += text(470, ys + 8, "= 5 у двійковій", 15, RED, "start", "bold")
    s += text(120, ys + 40, "Синдром 101₂ = 5 → перевертаємо біт на позиції 5 — і слово виправлено. ", 14, GREEN, "start", "bold")
    s += text(120, ys + 66, "Синдром 000 означав би «помилки немає». Геніальність: перевірки самі складаються в АДРЕСУ помилки.",
              12.5, GREY, "start", style="italic")
    save("fig-3-9-6-2-syndrome.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  ТЕМА 3.9.7 — ECC у RAM і Flash
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 3.9.7.1 — чому ECC-DIMM ширший на 8 біт (64 → 72) ───────────────────
def fig_7_dimm():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "ECC-пам'ять: до 64 бітів даних додають 8 бітів контролю → шина 72 біти", 17.5, INK, "middle", "bold")
    s += text(W / 2, 55, "SECDED — Single Error Correct, Double Error Detect: виправити 1 біт, помітити 2",
              12.5, GREY, "middle", style="italic")
    # 64 біти даних (8 груп) + 8 ECC
    x0, y0 = 60, 110
    cell = 11
    # дані
    for g in range(8):
        gx = x0 + g * (8 * cell + 8)
        for b in range(8):
            s += rect(gx + b * cell, y0, cell - 1.5, 22, "#eaf0ff", BLUE, 0.8, 1)
    s += text(x0, y0 - 8, "64 біти даних (8 байтів)", 13, BLUE, "start", "bold")
    # ECC
    ex = x0 + 8 * (8 * cell + 8) + 14
    for b in range(8):
        s += rect(ex + b * cell, y0, cell - 1.5, 22, "#fff8e8", AMBER, 0.8, 1)
    s += text(ex, y0 - 8, "+8 ECC", 13, AMBER, "start", "bold")
    s += text(ex + 8 * cell + 16, y0 + 16, "= 72-бітне слово на шині", 13, INK, "start", "bold")
    # що дає
    yb = 190
    s += rect(80, yb, 340, 150, "#eef7ef", GREEN, 1.8, 10)
    s += text(250, yb + 26, "1 перевернутий біт", 14, GREEN, "middle", "bold")
    s += text(250, yb + 50, "ECC знаходить ЯКИЙ і", 13, INK, "middle")
    s += text(250, yb + 70, "виправляє його на льоту —", 13, INK, "middle")
    s += text(250, yb + 90, "програма нічого не помічає.", 13, INK, "middle")
    s += text(250, yb + 120, "лічильник «corrected errors» росте", 11.5, GREY, "middle", style="italic")
    s += rect(460, yb, 340, 150, "#fdeceb", RED, 1.8, 10)
    s += text(630, yb + 26, "2 перевернуті біти", 14, RED, "middle", "bold")
    s += text(630, yb + 50, "виправити вже не може,", 13, INK, "middle")
    s += text(630, yb + 70, "але ТОЧНО бачить, що дані", 13, INK, "middle")
    s += text(630, yb + 90, "зіпсуто → зупинка/перезапуск", 13, INK, "middle")
    s += text(630, yb + 120, "краще впасти, ніж тихо збрехати", 11.5, GREY, "middle", style="italic")
    s += text(W / 2, H - 14, "8 зайвих бітів на 64 (≈ 12.5% пам'яті) — ціна за те, щоб поодинокий збій не валив сервер.",
              12.5, INK, "middle", style="italic")
    save("fig-3-9-7-1-dimm.svg", s)


# ── Рис. 3.9.7.2 — BCH у NAND: запасні байти на сторінку ────────────────────
def fig_7_nand():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 34, "Flash NAND: кожна сторінка має «запасну» зону під сильніший код (BCH)", 17.5, INK, "middle", "bold")
    s += text(W / 2, 55, "комірки NAND зношуються й течуть — тому ECC тут не розкіш, а умова роботи",
              12.5, GREY, "middle", style="italic")
    # сторінка: дані + spare
    x0, y0 = 70, 100
    dw, sw, hh = 540, 200, 60
    s += rect(x0, y0, dw, hh, "#eaf0ff", BLUE, 1.8, 6)
    s += text(x0 + dw / 2, y0 + 36, "дані сторінки  (напр. 2048 байт)", 15, BLUE, "middle", "bold")
    s += rect(x0 + dw, y0, sw, hh, "#fff8e8", AMBER, 1.8, 6)
    s += text(x0 + dw + sw / 2, y0 + 30, "spare-зона", 13.5, AMBER, "middle", "bold")
    s += text(x0 + dw + sw / 2, y0 + 48, "(ECC + службове)", 11.5, AMBER, "middle")
    s += text(x0, y0 - 10, "одна фізична сторінка NAND", 12.5, GREY, "start")
    # шкала зносу
    yb = 210
    s += text(70, yb, "Що більше циклів стирання — то більше бітів «пливе», то сильніший код потрібен:", 13, INK, "start", "bold")
    stages = [
        ("свіжа NAND", "1–4 биті/сектор", GREEN),
        ("середина ресурсу", "8 бітів/сектор", AMBER),
        ("під кінець ресурсу", "24–40+ бітів/сектор", RED),
    ]
    for i, (lbl, val, col) in enumerate(stages):
        x = 90 + i * 250
        s += rect(x, yb + 20, 220, 70, "#fff", col, 1.8, 8)
        s += text(x + 110, yb + 46, lbl, 13.5, col, "middle", "bold")
        s += text(x + 110, yb + 70, val, 14, INK, "middle", "bold")
        if i < 2:
            s += arrow(x + 224, yb + 55, x + 246, yb + 55, GREY, 2)
    s += text(W / 2, H - 14,
              "Тому контролер NAND рахує BCH/LDPC на десятки бітів. «Зношений» накопичувач — це той, де код уже не встигає за дефектами.",
              12, GREY, "middle", style="italic")
    save("fig-3-9-7-2-nand.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  ТЕМА 3.9.8 — Рід–Соломон якісно
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 3.9.8.1 — символи замість бітів: пакетна помилка = 1 битий символ ───
def fig_8_symbols():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 34, "Рід–Соломон: рахуємо не бітами, а СИМВОЛАМИ (групами бітів)", 18, INK, "middle", "bold")
    s += text(W / 2, 55, "подряпина б'є багато сусідніх бітів поспіль — але це лише кілька символів, а їх RS і вертає",
              12.5, GREY, "middle", style="italic")
    # стрічка з 12 символів по 8 біт; подряпина накриває символи 4-5
    x0, y0 = 60, 110
    symw, n = 62, 12
    burst = {4, 5}
    for i in range(n):
        x = x0 + i * symw
        col = RED if i in burst else (GREEN if i >= 9 else BLUE)
        fill = "#fdeceb" if i in burst else ("#eef7ef" if i >= 9 else "#eaf0ff")
        s += rect(x, y0, symw - 6, 44, fill, col, 2 if i in burst else 1.4, 5)
        lbl = "пар." if i >= 9 else f"S{i}"
        s += text(x + (symw - 6) / 2, y0 + 28, lbl, 12.5, col, "middle", "bold")
    s += text(x0, y0 - 10, "дані (символи S0…S8)", 12, BLUE, "start", "bold")
    s += text(x0 + 9 * symw, y0 - 10, "контроль", 12, GREEN, "start", "bold")
    # подряпина
    bx0 = x0 + 4 * symw - 4
    bx1 = x0 + 6 * symw - 6
    s += polygon([(bx0, y0 - 18), (bx1, y0 - 18), (bx1 + 10, y0 + 62), (bx0 - 10, y0 + 62)], "none", RED, 2.4, "5 4")
    s += text((bx0 + bx1) / 2, y0 + 80, "подряпина / завмирання радіо", 12, RED, "middle", "bold")
    # ключова думка
    yb = 230
    s += rect(70, yb, W - 140, 90, "#fbfbfb", FAINT, 1.4, 10)
    s += text(W / 2, yb + 26, "Для коду це лише 2 биті символи — байдуже, що зіпсуто всі 16 бітів усередині них.", 14, INK, "middle", "bold")
    s += text(W / 2, yb + 52, "RS, що додав t контрольних символів, виправляє до t/2 битих символів — хоч де в них помилки.", 13, GREEN, "middle")
    s += text(W / 2, yb + 74, "Бітовий код (Геммінг) тут захлинувся б: 16 помилок поспіль — це далеко за його межею.", 12.5, RED, "middle", style="italic")
    # порівняння носіїв
    yc = 360
    s += text(120, yc, "CD/DVD: подряпина — суцільний пакет помилок → RS вертає звук без чутного дефекту.", 13, INK, "start")
    s += text(120, yc + 24, "QR-код: бруд чи затертий куток — теж пакет → RS читає код навіть при втраті частини.", 13, INK, "start")
    s += text(120, yc + 48, "Саме «символьність» робить RS королем носіїв і каналів із ПАКЕТНИМИ, а не поодинокими помилками.", 12.5, GREY, "start", style="italic")
    save("fig-3-9-8-1-symbols.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  ТЕМА 3.9.9 — Інженерія надійності даних
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 3.9.9.1 — дерево рішень: що ставити де ──────────────────────────────
def fig_9_decision():
    W, H = 900, 620
    s = header(W, H)
    s += text(W / 2, 34, "Що ставити де: від найдешевшого детектора до повного виправлення", 18, INK, "middle", "bold")
    s += text(W / 2, 55, "три питання вибирають інструмент: чи треба ВИПРАВЛЯТИ? які помилки — поодинокі чи ПАКЕТНІ? наскільки дешево?",
              12, GREY, "middle", style="italic")
    # рівні-сходинки
    steps = [
        (90, "Парність / 1 біт", "1 біт контролю. Бачить 1 помилку, не виправляє.\nДе: UART-кадр, простий регістр, дешеві лінії.", AMBER, "виявлення"),
        (210, "Контрольна сума (сума / Флетчер)", "кілька байтів. Ловить більшість помилок, дешева в коді.\nДе: легкі протоколи, заголовки, файли — коли заліза CRC нема.", AMBER, "виявлення"),
        (330, "CRC", "потужне виявлення пакетів, апаратно майже безкоштовне.\nДе: CAN, Ethernet, SD, USB, серйозний кадр поверх UART.", RED, "виявлення (сильне)"),
        (450, "ECC: Геммінг/SECDED, BCH", "ВИПРАВЛЯЄ на льоту. Платимо зайвими бітами.\nДе: RAM серверів, Flash/NAND, регістри в радіації.", GREEN, "виправлення"),
        (570, "Рід–Соломон / каскад", "виправляє ПАКЕТИ символів; стійкий до подряпин і завмирань.\nДе: носії (CD/QR), супутник, далекий космос (§3.9.8 — Вояджери).", GREEN, "виправлення (пакети)"),
    ]
    x0 = 70
    for i, (yy, ttl, body, col, tag) in enumerate(steps):
        w = 560
        s += rect(x0 + i * 8, yy, w, 96, "#fff", col, 2.2, 9)
        s += text(x0 + i * 8 + 18, yy + 28, ttl, 16, col, "start", "bold")
        for j, ln in enumerate(body.split("\n")):
            s += text(x0 + i * 8 + 18, yy + 50 + j * 18, ln, 11.8, INK, "start")
        # тег праворуч
        s += rect(x0 + i * 8 + w + 16, yy + 28, 200, 38, "#fbfbfb", col, 1.6, 8)
        s += text(x0 + i * 8 + w + 116, yy + 52, tag, 12.5, col, "middle", "bold")
        if i < len(steps) - 1:
            s += arrow(x0 + i * 8 + 30, yy + 96, x0 + (i + 1) * 8 + 30, steps[i + 1][0], GREY, 2)
    s += text(40, H - 14, "Стрілка вниз = «треба більше надійності й готовий платити дорожче». Більшість систем поєднує кілька рівнів одразу.",
              12, GREY, "start", style="italic")
    save("fig-3-9-9-1-decision.svg", s)


# ── Рис. 3.9.9.2 — рівні захисту як шари в реальному пакеті (місток до М6) ───
def fig_9_layers():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "Шари захисту в реальному пакеті — місток до Модуля 6 (зв'язок)", 18, INK, "middle", "bold")
    s += text(W / 2, 55, "коди не змагаються — вони складаються в шари: кожен ловить те, що пропустив попередній",
              12.5, GREY, "middle", style="italic")
    # концентричні «обгортки» пакета
    rows = [
        ("байт у пам'яті / комірці", "ECC (Геммінг/BCH)", "поодинокі біт-фліпи в RAM і Flash", GREEN),
        ("символи на носії / в радіоканалі", "Рід–Соломон / FEC", "пакетні помилки, завмирання, подряпини", VIOL),
        ("кадр на шині / у протоколі", "CRC", "усе, що проскочило крізь канал", RED),
        ("логічний пакет (заголовок+дані)", "checksum / парність полів", "груба перевірка структури, дешево", AMBER),
    ]
    x0, y0 = 90, 95
    bw = 700
    for i, (scope, code, catches, col) in enumerate(rows):
        yy = y0 + i * 72
        s += rect(x0, yy, bw, 58, "#fff", col, 2, 8)
        s += text(x0 + 18, yy + 24, scope, 13.5, INK, "start", "bold")
        s += text(x0 + 18, yy + 46, "ловить: " + catches, 11.8, GREY, "start")
        s += rect(x0 + bw - 220, yy + 12, 200, 34, "#fbfbfb", col, 1.6, 7)
        s += text(x0 + bw - 120, yy + 34, code, 13.5, col, "middle", "bold")
    s += text(W / 2, H - 16,
              "У Модулі 6 ці кадри з CRC, довжиною й заголовком ми зберемо в повноцінні протоколи зв'язку. Тут — їхній фундамент.",
              12.5, INK, "middle", style="italic")
    save("fig-3-9-9-2-layers.svg", s)


# ── головний прогін ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    fig_1_sources()
    fig_1_scale()
    fig_1_margin()
    fig_2_parity()
    fig_2_blindspot()
    fig_3_sum()
    fig_3_fletcher()
    fig_4_division()
    fig_4_lfsr()
    fig_4_everywhere()
    fig_5_cube()
    fig_5_spheres()
    fig_6_layout()
    fig_6_syndrome()
    fig_7_dimm()
    fig_7_nand()
    fig_8_symbols()
    fig_9_decision()
    fig_9_layers()
    print("done.")
