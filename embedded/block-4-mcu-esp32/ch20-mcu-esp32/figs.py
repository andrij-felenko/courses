# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 20 — «Анатомія мікроконтролера й архітектура ESP32» (Модуль 4).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи нумеруються посекційно
(Рис. C.S.N) у тексті розділу; для історії до розділу — секція 0 (Рис. 20.0.N).

Скрипт нарощується по ітераціях: кожна тема додає свої функції-фігури.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра ─────────────────────────────────────────────────────────────────
RED   = "#c0271e"   # додатний (+)
BLUE  = "#1f47b5"   # від'ємний (−)
GREEN = "#1f8a3b"   # поле / акцент «усе на чипі»
INK   = "#1b1b1b"   # основний текст/лінії
GREY  = "#8a8a8a"   # допоміжне
FAINT = "#e4e4e4"   # дуже бліде тло
LRED  = "#fbecec"   # бліде червоне тло
LBLUE = "#e9eefb"   # бліде синє тло
LGRN  = "#eef6ef"   # бліде зелене тло
LAMB  = "#fff6e0"   # бліде бурштинове тло (виділити «весь комп'ютер»)
METAL = "#9a9aa0"   # метал/ніжки
SILI  = "#cfd6e6"   # кремнієвий кристал
GOLD  = "#caa24a"   # рамка-висновок
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


def chip_dip(cx, cy, w, h, label="", lcol="#ffffff", body="#2b2b2b", pins=4, psize=6):
    """Чорний DIP-корпус мікросхеми з ніжками з боків + білий підпис."""
    s = rect(cx - w / 2, cy - h / 2, w, h, body, "#000000", 1.2, 2)
    for i in range(pins):
        yy = cy - h / 2 + (i + 0.5) * h / pins
        s += rect(cx - w / 2 - psize, yy - 1.5, psize, 3, METAL, "#666666", 0.8)
        s += rect(cx + w / 2, yy - 1.5, psize, 3, METAL, "#666666", 0.8)
    s += circle(cx - w / 2 + 5, cy - h / 2 + 5, 1.6, "#000000", "#000000", 0)  # «зарубка»
    if label:
        s += text(cx, cy + 3.5, label, 9.5, lcol, "middle", "bold")
    return s


def blk(x, y, w, h, label, sub="", fill="#ffffff", stroke=INK, lcol=INK):
    """Прямокутний функційний блок із підписом (і необов'язковим дрібним підзаписом)."""
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


# ── Рис. 20.0.1 — вертикальний таймлайн «ланцюг питань» ──────────────────────
def fig_timeline():
    W, H = 900, 660
    s = header(W, H)
    s += text(W / 2, 38, "Ланцюг питань: як цілий комп'ютер уміщується в одну крихту", 20, INK, "middle", "bold")
    s += text(W / 2, 60, "кожен крок — нове питання, що штовхало далі (сірим — те, що стане змістом Розділу 20)",
              12.5, GREY, "middle", style="italic")
    spine = 218
    top, bot = 96, H - 30
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("до 1971", "Комп'ютер = шафа",
         "Логіка з сотень окремих чипів. Чи влізе ВЕСЬ комп'ютер на один кристал?", False, False),
        ("1960-ті", "Калькуляторна гонка / Busicom · TI · Sharp",
         "Десятки чипів на калькулятор — дорого. Як здешевити? → стиснути в один", False, False),
        ("1971", "Intel 4004 / Hoff · Faggin",
         "Процесор на чипі! Та ПЗП і ОЗП — ще ОКРЕМО. Це МІКРОПРОЦЕСОР", False, False),
        ("1971", "TI TMS0100 / Boone · Cochran",
         "Цілий комп'ютер на чипі: ПЗП+ОЗП+I/O всередині. Це МІКРОКОНТРОЛЕР", False, False),
        ("1974", "TMS1000",
         "Програмований МК за долар → сотні мільйонів штук у речах", False, True),
        ("Розділ 20", "ESP32",
         "З чого МК складається й чим ESP32 особливий?", True, False),
    ]
    n = len(nodes)
    for i, (yr, who, q, dest, accent) in enumerate(nodes):
        y = top + 30 + (bot - top - 60) * i / (n - 1)
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
    save("fig-20-0-1-timeline.svg", s)


# ── Рис. 20.0.2 — калькуляторна гонка: десятки чипів → один ───────────────────
def fig_calculator():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 36, "Калькуляторна гонка стиснула десятки чипів в один", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "тиск «дешевше, менше, універсальніше» виштовхнув на світ мікропроцесор і мікроконтролер",
              12.5, GREY, "middle", style="italic")

    # ліва панель — плата з багатьма чипами
    bx, by, bw, bh = 40, 100, 360, 300
    s += rect(bx, by, bw, bh, "#dfe7d8", "#4f7a3a", 2, 10)
    s += text(bx + bw / 2, by - 8, "калькулятор кінця 1960-х", 13.5, INK, "middle", "bold")
    for r in range(3):
        for c in range(4):
            cx = bx + 52 + c * 84
            cy = by + 70 + r * 86
            s += chip_dip(cx, cy, 50, 36, "IC", pins=4)
    s += text(bx + bw / 2, by + bh + 22, "десятки корпусів логіки, кожен — під одну модель", 12, GREY, "middle", style="italic")
    s += text(bx + bw / 2, by + bh + 40, "дорого проєктувати, виробляти, паяти", 12.5, RED, "middle", "bold")

    # стрілка переходу
    s += arrow(412, 244, 502, 244, INK, 3.5)
    s += text(457, 230, "стиснути", 12.5, INK, "middle", "bold")

    # права панель — один чіп
    px = 700
    s += rect(px - 110, 100, 220, 300, "none", FAINT, 2, 12)
    s += text(px, 92, "мета: один універсальний чіп", 13.5, INK, "middle", "bold")
    s += chip_dip(px, 224, 128, 128, "", body="#2b2b2b", pins=8, psize=10)
    s += text(px, 210, "1 ЧІП", 18, "#ffffff", "middle", "bold")
    s += text(px, 232, "роблять", 11, "#cfcfcf", "middle")
    s += text(px, 248, "мільйонами", 11, "#cfcfcf", "middle")
    s += rect(px - 100, 352, 200, 40, LGRN, GREEN, 1.4, 8)
    s += text(px, 368, "модель = інша", 12, INK, "middle", "bold")
    s += text(px, 384, "програма в ПЗП", 12, INK, "middle", "bold")
    save("fig-20-0-2-calculator.svg", s)


# ── Рис. 20.0.3 — Intel MCS-4: 4004 + окремі чипи пам'яті ─────────────────────
def fig_4004_set():
    W, H = 880, 540
    s = header(W, H)
    s += text(W / 2, 34, "Intel MCS-4 (1971): процесор окремо, пам'ять окремо", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "4004 — перший мікропроцесор: на чипі лише ядро, решта — сусідніми чипами по зовнішній шині",
              12, GREY, "middle", style="italic")
    cx, cy = 430, 300

    def satellite(x, y, w, h, name, sub):
        o = rect(x - w / 2, y - h / 2, w, h, "#2b2b2b", "#000000", 1.4, 4)
        o += text(x, y - 2, name, 13, "#ffffff", "middle", "bold")
        o += text(x, y + 15, sub, 10.5, "#d8d8d8", "middle")
        return o

    # зовнішні шини (під чипами)
    s += line(cx, cy - 72, cx, 178, GREY, 2.4)            # до ПЗП (зверху)
    s += line(cx + 95, cy, 575, cy, GREY, 2.4)            # до ОЗП (праворуч)
    s += line(cx, cy + 72, cx, 418, GREY, 2.4)            # до портів (знизу)
    s += text(cx + 10, 235, "шина", 10.5, GREY, "start", style="italic")

    # центр — 4004
    s += rect(cx - 95, cy - 72, 190, 144, SILI, INK, 2.4, 6)
    s += text(cx, cy - 50, "Intel 4004", 17, INK, "middle", "bold")
    s += text(cx, cy - 31, "МІКРОПРОЦЕСОР (CPU)", 10.5, RED, "middle", "bold")
    for i, lab in enumerate(["АЛП (арифметика)", "регістри", "керування", "≈ 2300 транзисторів"]):
        s += text(cx, cy - 9 + i * 19, "· " + lab, 12, INK, "middle")

    # супутники
    s += satellite(cx, 150, 156, 56, "4001 — ПЗП", "програма")
    s += satellite(650, cy, 150, 56, "4002 — ОЗП", "дані")
    s += satellite(cx, 446, 156, 56, "4003 — порти", "ввід-вивід (I/O)")

    s += rect(70, H - 52, W - 140, 34, LRED, RED, 1.4, 8)
    s += text(W / 2, H - 30, "Мікропроцесор = «комп'ютер мінус пам'ять і периферія»: щоб ожити, 4004 потребує сусідів.",
              13, INK, "middle", "bold")
    save("fig-20-0-3-4004-set.svg", s)


# ── Рис. 20.0.4 — мікропроцесор проти мікроконтролера (розріз кристала) ───────
def fig_uc_vs_up():
    W, H = 920, 500
    s = header(W, H)
    s += text(W / 2, 32, "Той самий вододіл, у розрізі кристала", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "мікропроцесор виносить пам'ять і периферію назовні; мікроконтролер тримає все на одному кристалі",
              12, GREY, "middle", style="italic")

    def die(x, y, w, h):
        o = rect(x, y, w, h, SILI, INK, 2.4, 8)
        o += circle(x + 14, y + 14, 4, "none", INK, 1.4)   # зарубка кристала
        return o

    # ── ліва панель: мікропроцесор ──
    s += rect(28, 78, 420, 404, "none", FAINT, 2, 14)
    s += text(238, 104, "Мікропроцесор (лінія 4004)", 15, RED, "middle", "bold")
    s += text(145, 146, "кристал", 11, GREY, "middle", style="italic")
    s += die(70, 156, 150, 120)
    s += blk(84, 182, 122, 74, "Ядро (CPU)", "АЛП·регістри", fill=LRED, stroke=RED)
    # зовнішні блоки
    s += blk(296, 160, 120, 46, "ПЗП", "програма")
    s += blk(296, 212, 120, 46, "ОЗП", "дані")
    s += blk(296, 264, 120, 46, "Периферія", "I/O")
    # зовнішня шина
    s += line(220, 216, 262, 216, GREY, 2.4)
    s += line(262, 183, 262, 287, GREY, 2.4)
    for yy in (183, 235, 287):
        s += line(262, yy, 296, yy, GREY, 2.4)
    s += text(250, 334, "шина — ЗЗОВНІ кристала", 11.5, GREY, "middle", "bold")
    s += rect(48, 420, 380, 52, LRED, RED, 1.4, 8)
    s += text(238, 440, "CPU на чипі — пам'ять і периферія окремо", 12, INK, "middle", "bold")
    s += text(238, 458, "→ «видимий» комп'ютер (ПК)", 11.5, INK, "middle")

    # ── права панель: мікроконтролер ──
    s += rect(472, 78, 420, 404, "none", LAMB, 2, 14)
    s += text(682, 104, "Мікроконтролер (лінія TMS1000)", 15, GREEN, "middle", "bold")
    s += text(682, 140, "ОДИН кристал", 11, GREEN, "middle", "bold")
    s += die(500, 150, 372, 236)
    # три колонки всередині
    c1, c2, c3, bw = 516, 636, 756, 108
    s += blk(c1, 170, bw, 52, "Ядро (CPU)", "АЛП·регістри", fill=LRED, stroke=RED)
    s += blk(c2, 170, bw, 52, "ПЗП", "програма")
    s += blk(c3, 170, bw, 52, "ОЗП", "дані")
    s += text(682, 252, "внутрішня шина", 11.5, GREEN, "middle", "bold")
    s += blk(c1, 312, bw, 52, "Такт", "генератор")
    s += blk(c2, 312, bw, 52, "Периферія", "I/O")
    s += blk(c3, 312, bw, 52, "Порти", "лічильники")
    # внутрішня шина + відгалуження
    s += line(545, 266, 825, 266, GREEN, 3)
    for xx in (c1 + bw / 2, c2 + bw / 2, c3 + bw / 2):
        s += line(xx, 222, xx, 266, GREEN, 2)
        s += line(xx, 266, xx, 312, GREEN, 2)
    s += rect(492, 420, 380, 52, LGRN, GREEN, 1.4, 8)
    s += text(682, 440, "усе в одному → самодостатній комп'ютер", 12, INK, "middle", "bold")
    s += text(682, 458, "саме цю праву колонку успадкує ESP32", 11.5, INK, "middle", style="italic")
    save("fig-20-0-4-uc-vs-up.svg", s)


# ── Рис. 20.0.5 — дві лінії від 1971 року (родовід) ──────────────────────────
def fig_lineages():
    W, H = 900, 560
    s = header(W, H)
    s += text(W / 2, 34, "Дві лінії від 1971 року: видимі й невидимі комп'ютери", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "розвилка, яку створив один рік: процесор-на-чипі проти комп'ютера-на-чипі",
              12, GREY, "middle", style="italic")
    rx, ry = W / 2, 98
    s += rect(rx - 130, ry - 22, 260, 44, "#efe9da", GOLD, 2, 8)
    s += text(rx, ry + 4, "1971: комп'ютер на чипі", 14.5, INK, "middle", "bold")

    def node(x, y, w, name, sub, accent=False, dim=False):
        fill = LGRN if accent else ("#f3f3f3" if dim else "#fbfbfb")
        stroke = GREEN if accent else (GREY if dim else INK)
        o = rect(x - w / 2, y - 22, w, 44, fill, stroke, 2.4 if accent else 1.8, 8)
        o += text(x, y - 2, name, 13.5, (GREEN if accent else INK), "middle", "bold")
        o += text(x, y + 14, sub, 10, GREY, "middle")
        return o

    ys = [192, 272, 352, 444]

    # ліва гілка — мікропроцесор
    lx = 215
    left = [("Intel 4004", "перший МП · 1971"),
            ("Intel 8080", "8-біт · 1974"),
            ("x86", "IBM PC і далі"),
            ("Персональний комп'ютер", "«видимий» — у центрі уваги")]
    s += text(lx, 150, "МІКРОПРОЦЕСОР", 13, GREY, "middle", "bold")
    s += text(lx, 167, "ядро + ЗОВНІШНЯ пам'ять", 10.5, GREY, "middle", style="italic")
    s += arrow(rx - 80, ry + 18, lx + 60, ys[0] - 26, GREY, 2.2)
    for i, (nm, sub) in enumerate(left):
        s += node(lx, ys[i], 206, nm, sub, dim=True)
        if i:
            s += arrow(lx, ys[i - 1] + 22, lx, ys[i] - 24, GREY, 2.2)

    # права гілка — мікроконтролер
    rxb = 685
    right = [("Калькулятор-чип · TMS0100", "1971"),
             ("TMS1000", "масовий МК · 1974"),
             ("8-біт МК", "8048 · PIC · AVR"),
             ("ESP32", "наш герой: МК + радіо")]
    s += text(rxb, 150, "МІКРОКОНТРОЛЕР", 13, GREEN, "middle", "bold")
    s += text(rxb, 167, "усе на чипі — самодостатній", 10.5, GREEN, "middle", style="italic")
    s += arrow(rx + 80, ry + 18, rxb - 60, ys[0] - 26, GREEN, 2.2)
    for i, (nm, sub) in enumerate(right):
        acc = (i == len(right) - 1)
        s += node(rxb, ys[i], 240, nm, sub, accent=acc)
        if i:
            s += arrow(rxb, ys[i - 1] + 22, rxb, ys[i] - 24, GREEN if acc else INK, 2.2)
    save("fig-20-0-5-lineages.svg", s)


# ── Рис. 20.0.6 — клубок патентних претензій ─────────────────────────────────
def fig_patents():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Клубок претензій на «перший мікропроцесор»", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "кілька рівноправних претендентів — бо «перший» залежить від визначення",
              12, GREY, "middle", style="italic")
    axisY = 250
    s += line(72, axisY, 838, axisY, INK, 2.6)
    s += arrow(820, axisY, 858, axisY, INK, 2.6)
    s += text(862, axisY + 4, "рік", 11, INK, "start")

    marks = [
        (120, "1969", "Boysel — AL1 (Four-Phase)", "8-біт процесор-чип", "up", INK),
        (250, "1970", "Hyatt — заявка; Holt — обчислювач F-14", "(засекречено до 1998)", "down", GREY),
        (390, "1971", "Intel 4004 · Boone — заявка", "МП ‖ «мікрокомп'ютер»", "up", RED),
        (520, "1973", "Boone — патент 3 757 306", "комп'ютер на чипі", "down", GREEN),
        (670, "1990", "Hyatt — патент видано", "сенсація…", "up", INK),
        (800, "1996", "пріоритет → Boone (TI)", "за процедурою суперечки", "down", GREEN),
    ]
    for x, yr, t1, t2, side, col in marks:
        s += line(x, axisY - 6, x, axisY + 6, INK, 2)
        s += circle(x, axisY, 4.5, "#ffffff", col, 2)
        if side == "up":
            s += line(x, axisY - 6, x, axisY - 26, GREY, 1.2, dash="2,3")
            s += text(x, axisY - 58, yr, 12.5, col, "middle", "bold")
            s += text(x, axisY - 42, t1, 10.5, INK, "middle", "bold")
            s += text(x, axisY - 28, t2, 9.5, GREY, "middle", style="italic")
        else:
            s += line(x, axisY + 6, x, axisY + 26, GREY, 1.2, dash="2,3")
            s += text(x, axisY + 40, yr, 12.5, col, "middle", "bold")
            s += text(x, axisY + 56, t1, 10.5, INK, "middle", "bold")
            s += text(x, axisY + 70, t2, 9.5, GREY, "middle", style="italic")

    s += rect(70, 372, 760, 78, "#f7f4ea", GOLD, 1.6, 10)
    s += text(W / 2, 396, "Розв'язка: «перший» роздвоюється за визначенням", 13.5, INK, "middle", "bold")
    s += text(W / 2, 418, "• процесор на чипі (продається окремо)  →  Intel 4004", 12, RED, "middle", "bold")
    s += text(W / 2, 438, "• комп'ютер на чипі (= мікроконтролер)  →  Boone / Texas Instruments", 12, GREEN, "middle", "bold")
    save("fig-20-0-6-patents.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §20.1 — Мікроконтролер: комп'ютер на одному чіпі (проти мікропроцесора)
# ─────────────────────────────────────────────────────────────────────────────

# ── Рис. 20.1.1 — що таке МК: комп'ютер на чипі + ніжки у світ ────────────────
def fig11_what_is_mcu():
    W, H = 880, 540
    s = header(W, H)
    s += text(W / 2, 34, "Мікроконтролер: цілий комп'ютер на одному чіпі", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "усе для самостійної роботи — всередині; назовні лише ніжки до світу",
              12.5, GREY, "middle", style="italic")

    dx, dy, dw, dh = 120, 150, 320, 300
    s += text(dx + dw / 2, dy - 12, "ОДИН ЧІП (кристал)", 12, GREEN, "middle", "bold")
    s += rect(dx, dy, dw, dh, SILI, INK, 2.4, 10)
    s += circle(dx + 16, dy + 16, 4.5, "none", INK, 1.4)

    s += blk(140, 176, 132, 64, "Ядро (CPU)", "обчислення", fill=LRED, stroke=RED)
    s += blk(288, 176, 132, 64, "Програмна пам'ять", "код", fill="#ffffff")
    s += blk(140, 300, 132, 64, "Пам'ять даних", "змінні", fill="#ffffff")
    s += blk(288, 300, 132, 64, "Периферія", "ввід-вивід", fill="#ffffff")
    s += blk(170, 384, 220, 46, "Генератор такту · живлення", fill="#f3f3f3")

    s += line(150, 270, 410, 270, GREEN, 3)
    s += text(280, 262, "внутрішня шина", 10.5, GREEN, "middle", "bold")
    for xx in (206, 354):
        s += line(xx, 240, xx, 270, GREEN, 1.8)
        s += line(xx, 270, xx, 300, GREEN, 1.8)

    s += arrow(40, 230, dx, 230, RED, 2.6)
    s += text(44, 222, "живлення", 11.5, RED, "start", "bold")

    world = [(196, "кнопка", "in"), (266, "давач", "in"), (336, "мотор", "out"), (406, "світлодіод", "out")]
    wx = 660
    s += text(wx, 150, "СВІТ", 12, GREY, "middle", "bold")
    for py, name, d in world:
        s += rect(dx + dw, py - 4, 10, 8, METAL, "#666666", 0.8)
        s += rect(wx - 60, py - 20, 120, 40, "#fbfbfb", INK, 1.6, 6)
        s += text(wx, py + 4, name, 12.5, INK, "middle", "bold")
        if d == "in":
            s += arrow(wx - 62, py, dx + dw + 12, py, BLUE, 2.2)
        else:
            s += arrow(dx + dw + 12, py, wx - 62, py, GREEN, 2.2)
    s += text(250, 498, "сині стрілки — входи (читає світ)", 11, BLUE, "middle", "bold")
    s += text(660, 498, "зелені — виходи (керує світом)", 11, GREEN, "middle", "bold")
    save("fig-20-1-1-what-is-mcu.svg", s)


# ── Рис. 20.1.2 — MPU vs MCU на рівні плати ──────────────────────────────────
def fig12_mp_vs_mc_board():
    W, H = 920, 520
    s = header(W, H)
    s += text(W / 2, 32, "Мікропроцесор проти мікроконтролера — очима того, хто паяє плату", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "те саме завдання: зліва — ціла материнська плата, справа — один чіп",
              12.5, GREY, "middle", style="italic")

    # ліва панель — MPU: ціла плата
    s += rect(36, 84, 420, 380, "#dfe7d8", "#4f7a3a", 2, 12)
    s += text(246, 108, "Мікропроцесор: ціла плата", 14.5, INK, "middle", "bold")
    cxl, cyl = 246, 282
    sat = [(246, 172, "ПЗП"), (382, 282, "ОЗП"), (246, 392, "I/O"), (116, 282, "такт")]
    for sx, sy, nm in sat:
        s += line(cxl, cyl, sx, sy, GREY, 2)
    s += chip_dip(cxl, cyl, 96, 80, "MPU", pins=5, psize=8)
    s += text(cxl, cyl + 58, "лише ядро", 10.5, RED, "middle", "bold")
    for sx, sy, nm in sat:
        s += chip_dip(sx, sy, 70, 50, nm, pins=4, psize=6)
    s += text(246, 452, "+ десятки доріжок-шин", 11.5, GREY, "middle", style="italic")

    # права панель — MCU: один чіп
    s += rect(484, 84, 400, 380, "none", FAINT, 2, 12)
    s += text(684, 108, "Мікроконтролер: один чіп", 14.5, INK, "middle", "bold")
    s += chip_dip(684, 274, 150, 150, "", pins=9, psize=11)
    s += text(684, 256, "MCU", 18, "#ffffff", "middle", "bold")
    s += text(684, 280, "усе", 11, "#cfcfcf", "middle")
    s += text(684, 296, "всередині", 11, "#cfcfcf", "middle")
    s += arrow(556, 200, 604, 200, RED, 2.4)
    s += text(552, 192, "живлення", 11, RED, "end", "bold")
    s += text(684, 452, "+ майже нічого більше", 11.5, GREY, "middle", style="italic")

    s += rect(70, H - 42, W - 140, 30, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 22, "Один чіп замість плати чипів: менше з'єднань, місця й ціни — вища надійність.",
              13, INK, "middle", "bold")
    save("fig-20-1-2-mp-vs-mc-board.svg", s)


# ── Рис. 20.1.3 — порядки величин: ПК проти МК ───────────────────────────────
def fig13_scale():
    W, H = 920, 480
    s = header(W, H)
    s += text(W / 2, 32, "Порядки величин: настільний комп'ютер проти мікроконтролера", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "різниця у тисячі–мільйони разів — це не вада, а інша мета (орієнтовні значення)",
              12, GREY, "middle", style="italic")
    s += rect(346, 70, 16, 12, LBLUE, BLUE, 1.2)
    s += text(368, 80, "ПК (мікропроцесор + ОС)", 11.5, BLUE, "start", "bold")
    s += rect(612, 70, 16, 12, LGRN, GREEN, 1.2)
    s += text(634, 80, "МК (мікроконтролер)", 11.5, GREEN, "start", "bold")

    rows = [
        ("Тактова частота", "~3 ГГц", "десятки–сотні МГц", "× у тисячі"),
        ("Пам'ять даних", "~16 ГБ", "сотні КБ", "× у мільйони"),
        ("Сховище", "~1 ТБ", "одиниці МБ", "× у сотні тисяч"),
        ("Споживання", "десятки Вт", "мілівати", "× у тисячі"),
    ]
    y0, bx, full = 116, 210, 360
    for i, (name, pcv, mcv, ratio) in enumerate(rows):
        y = y0 + i * 64
        s += text(40, y + 12, name, 13.5, INK, "start", "bold")
        s += rect(bx, y, full, 16, LBLUE, BLUE, 1.4, 3)
        s += text(bx + full + 8, y + 13, pcv, 12, BLUE, "start", "bold")
        s += rect(bx, y + 22, 26, 16, LGRN, GREEN, 1.4, 3)
        s += text(bx + 34, y + 35, mcv, 12, GREEN, "start", "bold")
        s += rect(bx + full + 96, y + 4, 124, 28, "#f7f4ea", GOLD, 1.2, 8)
        s += text(bx + full + 158, y + 22, ratio, 11.5, INK, "middle", "bold")

    yr = y0 + 4 * 64 + 4
    s += line(40, yr, W - 40, yr, FAINT, 1.4)
    s += text(40, yr + 26, "Роль", 13.5, INK, "start", "bold")
    s += text(bx, yr + 22, "багато застосунків під операційною системою", 12, BLUE, "start", "bold")
    s += text(bx, yr + 42, "одна програма, що працює роками без перезавантажень", 12, GREEN, "start", "bold")
    save("fig-20-1-3-scale.svg", s)


# ── Рис. 20.1.4 — самодостатній старт (boot) ─────────────────────────────────
def fig14_boot():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 32, "Самодостатній старт: МК біжить одразу, комп'ютер вантажить ОС", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "що відбувається після ввімкнення живлення", 12.5, GREY, "middle", style="italic")

    def chain(y, title, steps, tag, col, accent):
        o = text(40, y - 12, title, 14, col, "start", "bold")
        w, gap = 104, 16
        x = 50
        for i, st in enumerate(steps):
            fill = LGRN if accent else "#f3f3f3"
            stroke = GREEN if accent else GREY
            o += rect(x, y, w, 50, fill, stroke, 1.8, 6)
            for j, ln in enumerate(st):
                o += text(x + w / 2, y + (28 if len(st) == 1 else 22) + j * 15, ln,
                          10.5, INK, "middle", "bold" if j == 0 else "normal")
            if i < len(steps) - 1:
                o += arrow(x + w, y + 25, x + w + gap + 1, y + 25, stroke, 2.2)
            x += w + gap
        o += rect(x + 4, y + 8, 124, 34, "#ffffff", col, 1.6, 8)
        o += text(x + 66, y + 30, tag, 12, col, "middle", "bold")
        return o

    s += chain(124, "Мікроконтролер",
               [["скидання"], ["читає код", "з пам'яті"], ["код", "працює"]],
               "≈ мілісекунди", GREEN, True)
    s += chain(286, "Комп'ютер (мікропроцесор + ОС)",
               [["скидання"], ["заван-", "тажувач"], ["пошук", "диска"], ["підняття", "ОС"], ["драй-", "вери"], ["робочий", "стіл"]],
               "≈ десятки с", GREY, False)
    s += text(W / 2, 404, "МК не «вмикається» — він просто одразу Є; комп'ютер мусить спершу зібрати себе докупи.",
              12, INK, "middle", style="italic")
    save("fig-20-1-4-boot.svg", s)


# ── Рис. 20.1.5 — шкала від МК до ПК, де ESP32 ───────────────────────────────
def fig15_spectrum():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 34, "Шкала обчислювальної ваги: де на ній ESP32", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "межа МК↔МП не різка — це неперервна шкала", 12.5, GREY, "middle", style="italic")
    axisY = 212
    s += line(70, axisY, 852, axisY, INK, 2.6)
    s += arrow(835, axisY, 870, axisY, INK, 2.6)
    s += text(W / 2, axisY + 72, "обчислювальна вага →", 12.5, INK, "middle", "bold")

    pts = [
        (170, "простий 8-біт МК", "КБ пам'яті · центи", False),
        (392, "потужний МК / SoC", "ESP32 · МБ · радіо", True),
        (612, "одноплатник з ОС", "Raspberry Pi · ГБ", False),
        (812, "ПК / сервер", "багатоядерний · ОС", False),
    ]
    for x, nm, sub, acc in pts:
        col = GREEN if acc else INK
        s += circle(x, axisY, 9 if acc else 7, "#ffffff", col, 3 if acc else 2.4)
        if acc:
            s += circle(x, axisY, 3.5, GREEN, GREEN, 0)
        s += rect(x - 92, axisY - 80, 184, 46, LGRN if acc else "#fbfbfb", col, 2.4 if acc else 1.6, 8)
        s += text(x, axisY - 58, nm, 12.5, col, "middle", "bold")
        s += text(x, axisY - 42, sub, 10.5, GREY, "middle")
        s += line(x, axisY - 34, x, axisY - 8, col, 1.4, dash="2,3")

    s += line(110, axisY + 28, 472, axisY + 28, GREEN, 2.4)
    s += text(291, axisY + 46, "МІКРОКОНТРОЛЕРИ (усе на чипі)", 11.5, GREEN, "middle", "bold")
    s += line(532, axisY + 28, 852, axisY + 28, GREY, 2.4)
    s += text(692, axisY + 46, "МІКРОПРОЦЕСОРИ + ОС", 11.5, GREY, "middle", "bold")
    save("fig-20-1-5-spectrum.svg", s)


# ── Рис. 20.1.6 — бюджет пам'яті (worked example) ────────────────────────────
def fig16_budget():
    W, H = 860, 430
    s = header(W, H)
    s += text(W / 2, 34, "Бюджет пам'яті: чи влізе програма в мікроконтролер", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "на МК пам'ять рахують у кілобайтах — код в одну посудину, змінні в іншу",
              12.5, GREY, "middle", style="italic")

    def bar(y, title, cap_label, cap, used, used_label, ucol, ufill):
        o = text(40, y - 10, title, 14, INK, "start", "bold")
        bx, bw, bh = 40, 700, 44
        o += rect(bx, y, bw, bh, "#fbfbfb", INK, 1.8, 6)
        frac = used / cap
        fw = max(8, bw * frac)
        o += rect(bx, y, fw, bh, ufill, ucol, 1.6, 6)
        if fw > 70:
            o += text(bx + fw / 2, y + bh / 2 + 4, used_label, 11.5, "#1b1b1b", "middle", "bold")
        else:
            o += text(bx + fw + 8, y + bh / 2 + 4, used_label, 11.5, ucol, "start", "bold")
        o += text(bx + bw - 8, y + bh + 16, cap_label, 11.5, GREY, "end")
        o += text(bx + bw - 8, y - 10, f"{frac * 100:.1f}% зайнято", 11.5, ucol, "end", "bold")
        return o

    s += bar(112, "Програмна пам'ять (код)", "ємність 4 МБ = 4096 КБ", 4096, 180, "180 КБ", RED, LRED)
    s += bar(242, "Пам'ять даних (змінні)", "ємність 320 КБ", 320, 45, "45 КБ", BLUE, LBLUE)

    s += rect(40, 330, 700, 72, "#f7f4ea", GOLD, 1.6, 10)
    s += text(56, 354, "Урок:", 13, INK, "start", "bold")
    s += text(56, 374, "обидві посудини вимірюють у КБ, а не ГБ; заповнювати «по вінця» не можна —", 12, INK, "start")
    s += text(56, 393, "лишають запас на стек і непередбачене. Складніша задача — і запас тане вмить.", 12, INK, "start")
    save("fig-20-1-6-budget.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §20.2 — Складові МК: ядро, пам'ять (Flash/SRAM), периферія
# ─────────────────────────────────────────────────────────────────────────────

def blk2(x, y, w, h, label, sublines, fill="#ffffff", stroke=INK, lcol=INK):
    """Блок із підписом і кількома дрібними підрядками."""
    o = rect(x, y, w, h, fill, stroke, 1.8, 4)
    o += text(x + w / 2, y + 26, label, 13.5, lcol, "middle", "bold")
    for i, ln in enumerate(sublines):
        o += text(x + w / 2, y + 44 + i * 15, ln, 10, GREY, "middle")
    return o


def _card(x, y, w, h, title, tcol, items):
    """Картка-група для каталогу периферії."""
    o = rect(x, y, w, h, "#fbfbfb", tcol, 2, 8)
    o += text(x + 12, y + 22, title, 12.5, tcol, "start", "bold")
    o += line(x + 12, y + 30, x + w - 12, y + 30, tcol, 1.4)
    for i, (nm, desc) in enumerate(items):
        yy = y + 52 + i * 30
        o += text(x + 12, yy, "• " + nm, 11.5, INK, "start", "bold")
        o += text(x + 24, yy + 14, desc, 9.6, GREY, "start")
    return o


def _sqwave(x0, y_hi, y_lo, widths, color, start_hi=False, sw=2.6):
    """Меандр (square wave) із заданими ширинами півперіодів."""
    hi = start_hi
    y = y_hi if hi else y_lo
    d = f"M {x0:.1f},{y:.1f}"
    x = x0
    for i, w in enumerate(widths):
        x += w
        d += f" H {x:.1f}"
        if i != len(widths) - 1:
            hi = not hi
            y = y_hi if hi else y_lo
            d += f" V {y:.1f}"
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linejoin="miter"/>\n'


# ── Рис. 20.2.1 — блок-схема МК ──────────────────────────────────────────────
def fig21_block_diagram():
    W, H = 900, 545
    s = header(W, H)
    s += text(W / 2, 34, "Блок-схема мікроконтролера: ядро, дві пам'яті, периферія на шині", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "карта, яку ви впізнаєте на першій сторінці будь-якого даташита", 12.5, GREY, "middle", style="italic")
    s += rect(50, 80, 800, 430, "#fbfcff", INK, 2.4, 14)
    s += text(70, 100, "Мікроконтролер (один чіп)", 12, GREY, "start", "bold")
    # ядро
    s += blk2(360, 116, 180, 76, "Ядро (CPU)", ["вибірка–декод–виконання"], fill=LRED, stroke=RED, lcol=RED)
    # шина
    busY = 240
    s += line(110, busY, 800, busY, GREEN, 6)
    s += text(796, busY - 10, "внутрішня шина — спільна карта адрес", 11.5, GREEN, "end", "bold")
    s += line(450, 192, 450, busY, GREEN, 3)
    # пам'ять
    s += line(185, busY, 185, 286, GREEN, 3)
    s += line(360, busY, 360, 286, GREEN, 3)
    s += blk2(110, 286, 150, 96, "Flash", ["програма (код)", "енергонезалежна"], fill="#eef3ff", stroke=BLUE, lcol=BLUE)
    s += blk2(285, 286, 150, 96, "SRAM", ["дані (змінні)", "енергозалежна"], fill="#eef6ef", stroke=GREEN, lcol=GREEN)
    # периферія
    s += line(635, busY, 635, 286, GREEN, 3)
    s += rect(470, 286, 330, 172, "#fafafa", INK, 1.8, 10)
    s += text(635, 306, "Периферія", 13, INK, "middle", "bold")
    s += blk(484, 316, 140, 40, "GPIO")
    s += blk(636, 316, 150, 40, "Таймери · ШІМ")
    s += blk(484, 364, 140, 40, "АЦП · ЦАП")
    s += blk(636, 364, 150, 40, "UART · I2C · SPI")
    s += blk(484, 412, 302, 34, "перерив. · DMA · RTC · watchdog")
    # ніжки знизу
    for i in range(12):
        s += rect(120 + i * 60, 510, 8, 14, METAL, "#666666", 0.8)
    s += text(W / 2, 536, "ніжки (pins) — у світ", 11, GREY, "middle", "bold")
    save("fig-20-2-1-block-diagram.svg", s)


# ── Рис. 20.2.2 — зум у ядро ─────────────────────────────────────────────────
def fig22_core():
    W, H = 840, 420
    s = header(W, H)
    s += text(W / 2, 34, "Усередині ядра: лічильник команд, декодер, АЛП, регістри", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "той самий процесор із Модуля 3 — фундамент будь-якого МК", 12.5, GREY, "middle", style="italic")
    s += blk2(36, 168, 124, 84, "Програмна", ["пам'ять", "(Flash)"], fill="#eef3ff", stroke=BLUE, lcol=BLUE)
    s += rect(196, 104, 608, 232, "#fbfcff", RED, 2.4, 12)
    s += text(500, 126, "Ядро (CPU)", 14, RED, "middle", "bold")
    s += blk2(226, 156, 124, 64, "Лічильник", ["команд (PC)"])
    s += blk(384, 156, 110, 64, "Декодер")
    s += blk2(540, 156, 120, 64, "АЛП", ["арифметика/логіка"])
    s += blk(540, 250, 234, 60, "Регістри")
    s += blk2(384, 250, 124, 60, "Керування", ["+ такт"])
    s += arrow(160, 196, 226, 188, INK, 2.2)
    s += text(193, 180, "інструкція", 9.5, GREY, "middle")
    s += arrow(350, 188, 384, 188, INK, 2.2)
    s += arrow(494, 188, 540, 188, INK, 2.2)
    s += arrow(596, 220, 596, 250, INK, 2.2)
    s += arrow(620, 250, 620, 220, INK, 2.2)
    s += text(720, 244, "дані", 10, GREY, "middle")
    s += line(446, 250, 446, 220, GREY, 1.6, dash="3,3")
    s += line(446, 220, 470, 200, GREY, 1.6, dash="3,3")
    s += text(500, 326, "розрядність: 8 / 16 / 32 біт — ширина даних за один прийом", 11.5, GREEN, "middle", "bold")
    save("fig-20-2-2-core.svg", s)


# ── Рис. 20.2.3 — Flash vs SRAM ──────────────────────────────────────────────
def fig23_memory():
    W, H = 860, 460
    s = header(W, H)
    s += text(W / 2, 32, "Дві пам'яті: Flash для коду (постійна), SRAM для даних (тимчасова)", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "програма «живе» у Flash, а «думає» у SRAM", 12.5, GREY, "middle", style="italic")

    def memcol(x, title, tcol, fill, cells, badges):
        o = rect(x, 80, 360, 300, "none", FAINT, 2, 14)
        o += text(x + 180, 106, title, 14.5, tcol, "middle", "bold")
        cy = 128
        o += rect(x + 110, cy, 140, 150, "#ffffff", tcol, 2, 4)
        for i, c in enumerate(cells):
            yy = cy + i * 50
            o += rect(x + 110, yy, 140, 50, fill, tcol, 1.2)
            o += text(x + 180, yy + 30, c, 12, INK, "middle", "bold")
        for j, (b, ok) in enumerate(badges):
            by = 292 + j * 28
            col = GREEN if ok else RED
            o += text(x + 30, by, ("✓ " if ok else "✗ ") + b, 11.5, col, "start", "bold")
        return o

    s += memcol(30, "Flash — програмна пам'ять", BLUE, "#eef3ff",
                ["код", "константи", "рядки"],
                [("енергонезалежна — переживає вимкнення", True),
                 ("пишеться рідко, читається весь час", True)])
    s += memcol(470, "SRAM — пам'ять даних", GREEN, "#eef6ef",
                ["змінні", "стек", "купа"],
                [("швидка, вільний перезапис", True),
                 ("енергозалежна — стирається без живлення", False)])

    s += rect(60, 398, W - 120, 46, "#f7f4ea", GOLD, 1.6, 10)
    s += text(W / 2, 418, "Вимкнули живлення:  Flash — код на місці ✓     SRAM — увесь вміст стерто ✗",
              12.5, INK, "middle", "bold")
    s += text(W / 2, 436, "Тому код кладуть у Flash, а мінливі дані — у SRAM; маленькі налаштування — в окрему незалежну комірку.",
              11, GREY, "middle")
    save("fig-20-2-3-memory.svg", s)


# ── Рис. 20.2.4 — каталог периферії ──────────────────────────────────────────
def fig24_peripheral_catalog():
    W, H = 920, 520
    s = header(W, H)
    s += text(W / 2, 32, "Каталог периферії: апаратні «органи» зв'язку зі світом", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "кожен вузол — окреме залізо, що працює само; це й різнить мікроконтролери",
              12.5, GREY, "middle", style="italic")
    s += _card(30, 78, 280, 180, "Цифровий ввід-вивід", BLUE,
               [("GPIO", "універсальні ніжки: 0 або 1"),
                ("читання / запис", "кнопки, світлодіоди, лінії")])
    s += _card(320, 78, 280, 180, "Час", GREEN,
               [("Таймери / лічильники", "міряють і задають інтервали"),
                ("ШІМ (PWM)", "«аналог» цифровою ніжкою")])
    s += _card(610, 78, 280, 180, "Аналог", RED,
               [("АЦП", "напруга → число"),
                ("ЦАП", "число → напруга")])
    s += _card(30, 278, 425, 200, "Зв'язок із іншими чипами", INK,
               [("UART", "асинхронний послідовний потік"),
                ("I2C", "дві лінії — багато пристроїв"),
                ("SPI", "швидка повнодуплексна шина")])
    s += _card(465, 278, 425, 200, "Системне", "#6a6a6a",
               [("контролер переривань", "реагувати на подію вмить"),
                ("DMA", "перекидати дані без ядра"),
                ("RTC · watchdog", "годинник реального часу · захист від зависань")])
    s += text(W / 2, 502, "Ядро лише налаштовує вузол — далі той працює сам, паралельно з ядром.",
              12, INK, "middle", "bold")
    save("fig-20-2-4-peripheral-catalog.svg", s)


# ── Рис. 20.2.5 — периферія розвантажує ядро ─────────────────────────────────
def fig25_offload():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 32, "Чому периферія, а не «все програмою»", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "та сама задача — видати рівний сигнал — двома способами", 12.5, GREY, "middle", style="italic")

    # верх — програмою (bit-bang)
    s += rect(30, 78, 840, 150, "none", FAINT, 2, 12)
    s += text(50, 100, "Програмою (bit-bang)", 14, RED, "start", "bold")
    s += rect(60, 120, 150, 80, LRED, RED, 1.8, 6)
    s += text(135, 150, "Ядро", 13, INK, "middle", "bold")
    s += text(135, 170, "зайняте 100%", 11, RED, "middle", "bold")
    s += text(135, 186, "у циклі увімк–вимк", 9.5, GREY, "middle")
    s += text(300, 132, "вихід — тремтить (jitter):", 11, GREY, "start", style="italic")
    s += _sqwave(300, 150, 188, [22, 38, 26, 30, 18, 44, 28, 20], RED, start_hi=False, sw=2.6)
    s += text(760, 210, "будь-яка перерва — і збій", 10.5, RED, "middle", style="italic")

    # низ — периферією (таймер)
    s += rect(30, 244, 840, 160, "none", LGRN, 2, 12)
    s += text(50, 266, "Периферією (таймер)", 14, GREEN, "start", "bold")
    s += rect(60, 286, 150, 80, "#ffffff", GREEN, 1.8, 6)
    s += text(135, 316, "Ядро", 13, INK, "middle", "bold")
    s += text(135, 336, "вільне", 11, GREEN, "middle", "bold")
    s += text(135, 352, "робить інше", 9.5, GREY, "middle")
    s += arrow(212, 326, 250, 326, GREEN, 2.2)
    s += rect(252, 296, 120, 60, LGRN, GREEN, 1.8, 6)
    s += text(312, 322, "Таймер", 12.5, GREEN, "middle", "bold")
    s += text(312, 340, "(залізо)", 10, GREY, "middle")
    s += text(420, 286, "вихід — ідеально рівний:", 11, GREY, "start", style="italic")
    s += _sqwave(420, 348, 300, [30, 30, 30, 30, 30, 30, 30, 30], GREEN, start_hi=False, sw=2.6)
    s += text(770, 392, "точно, поки ядро вільне", 10.5, GREEN, "middle", style="italic")
    save("fig-20-2-5-offload.svg", s)


# ── Рис. 20.2.6 — рядок даташита розкладено на складові ───────────────────────
def fig26_datasheet():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 32, "Рядок даташита, розкладений на складові", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "за сухим переліком — знайома будова: ядро · пам'ять · периферія", 12.5, GREY, "middle", style="italic")

    chips = [
        ("32-біт", RED, LRED), ("160 МГц", RED, LRED),
        ("Flash 4 МБ", BLUE, LBLUE), ("SRAM 320 КБ", GREEN, LGRN),
        ("34×GPIO", INK, "#f1f1f1"), ("8×АЦП", INK, "#f1f1f1"),
        ("4×Timer", INK, "#f1f1f1"), ("UART/I2C/SPI", INK, "#f1f1f1"),
    ]
    xs = [40, 260, 480, 700]
    cw = 180
    for i, (label, col, fill) in enumerate(chips):
        row, c = divmod(i, 4)
        x = xs[c]
        y = 110 + row * 70
        s += rect(x, y, cw, 46, fill, col, 2, 8)
        s += text(x + cw / 2, y + 29, label, 14, col, "middle", "bold")

    s += line(60, 256, 860, 256, FAINT, 1.4)
    legend = [("ядро (розрядність, частота)", RED), ("програма — Flash", BLUE),
              ("дані — SRAM", GREEN), ("периферія", INK)]
    lx = 70
    for name, col in legend:
        s += rect(lx, 278, 18, 14, "#ffffff", col, 2)
        s += text(lx + 26, 290, name, 12, col, "start", "bold")
        lx += 28 + len(name) * 7.6
    s += text(W / 2, 340, "Читати даташит — це звіряти цей список складових із потребами задачі.",
              12.5, INK, "middle", "bold")
    save("fig-20-2-6-datasheet.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §20.3 — Регістри периферії: memory-mapped IO
# ─────────────────────────────────────────────────────────────────────────────

def _tint(col):
    return {RED: LRED, GREEN: LGRN, BLUE: LBLUE}.get(col, "#eef0f5")


def _bitword(x, y, value, nbits=8, hi=None, hicol=RED, cw=34, ch=30, idx=True):
    """Рядок бітів (MSB ліворуч). hi — множина позицій бітів для підсвічування."""
    hi = hi or set()
    o = ""
    for i in range(nbits):
        bitpos = nbits - 1 - i
        b = (value >> bitpos) & 1
        cx = x + i * cw
        on = bitpos in hi
        o += rect(cx, y, cw, ch, _tint(hicol) if on else "#ffffff", hicol if on else INK, 1.8 if on else 1.2)
        o += text(cx + cw / 2, y + ch * 0.68, str(b), 14, hicol if on else INK, "middle", "bold")
        if idx:
            o += text(cx + cw / 2, y + ch + 12, str(bitpos), 8.5, GREY, "middle")
    return o


# ── Рис. 20.3.1 — карта адрес: пам'ять + периферія ───────────────────────────
def fig31_address_map():
    W, H = 820, 545
    s = header(W, H)
    s += text(W / 2, 34, "Карта адрес: код, дані й периферія в одному просторі", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "звернення за адресою з периферійного діапазону керує залізом, а не пам'яттю",
              12.5, GREY, "middle", style="italic")
    cx, cw = 250, 210

    def band(y, h, label, sub, fill, stroke):
        o = rect(cx, y, cw, h, fill, stroke, 1.8)
        o += text(cx + cw / 2, y + h / 2 - 2, label, 13, INK, "middle", "bold")
        if sub:
            o += text(cx + cw / 2, y + h / 2 + 15, sub, 10, GREY, "middle")
        return o

    # периферія (вгорі) з під-блоками
    s += rect(cx, 104, cw, 188, LAMB, "#b9912f", 2)
    s += text(cx + cw / 2, 120, "Периферія (регістри)", 12.5, "#8a6a14", "middle", "bold")
    peris = ["GPIO  0x4000_8000", "Timer 0x4000_9000", "ADC   0x4000_A000", "UART  0x4000_B000"]
    for i, p in enumerate(peris):
        yy = 130 + i * 38
        s += rect(cx + 14, yy, cw - 28, 32, "#fff7e6", "#caa24a", 1.2, 3)
        s += text(cx + cw / 2, yy + 21, p, 11, INK, "middle", "bold")
    s += band(312, 70, "SRAM — дані", "змінні, стек", "#eef6ef", GREEN)
    s += band(394, 78, "Flash — код", "програма", "#eef3ff", BLUE)

    # адреси ліворуч
    for y, a in [(104, "0x5FFF_FFFF"), (292, "0x4000_0000"), (312, "0x3FFF_FFFF"),
                 (382, "0x2000_0000"), (394, "0x1FFF_FFFF"), (472, "0x0000_0000")]:
        s += line(cx - 8, y, cx, y, GREY, 1.2)
        s += text(cx - 12, y + 4, a, 10, GREY, "end")

    # праворуч — наслідки
    s += rect(540, 130, 250, 120, "none", FAINT, 1.6, 10)
    s += arrow(cx + cw + 2, 180, 540, 165, RED, 2.4)
    s += text(548, 156, "запис сюди →", 12, RED, "start", "bold")
    s += text(548, 174, "КЕРУЄ залізом", 13, RED, "start", "bold")
    s += text(548, 196, "(ніжки, мотор, АЦП…)", 11, GREY, "start")
    s += text(548, 224, "— не зберігає число,", 11, INK, "start")
    s += text(548, 240, "а діє", 11, INK, "start", "bold")
    s += arrow(cx + cw + 2, 400, 560, 400, GREY, 2.2)
    s += text(566, 396, "звичайна пам'ять", 12, GREY, "start", "bold")
    s += text(566, 414, "(зберігає значення)", 10.5, GREY, "start")
    s += text(cx + cw / 2, 512, "Memory-mapped IO: керування залізом «відображене» на адреси, наче пам'ять.",
              12, INK, "middle", "bold")
    save("fig-20-3-1-address-map.svg", s)


# ── Рис. 20.3.2 — регістр як рядок бітів, заведених на залізо ─────────────────
def fig32_register_bits():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Регістр периферії — не пам'ять, а панель керування з адресою", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "кожен біт дротом заведений на лінію заліза: запис керує, читання знімає стан",
              12.5, GREY, "middle", style="italic")
    nbits, cw, x0, ry = 16, 46, 80, 150
    s += text(x0, ry - 14, "регістр @ 0x4000_8004", 11.5, INK, "start", "bold")
    s += _bitword(x0, ry, 0b0000000100010011, nbits, {0, 1, 4, 8}, RED, cw, 36, idx=True)

    def cx_of(bitpos):
        return x0 + (nbits - 1 - bitpos) * cw + cw / 2

    # керувальні біти (вниз, червоні)
    ctl = [(0, "EN — увімкнути вузол"), (1, "DIR — напрям ніжки"), (4, "MODE — режим")]
    for bp, lab in ctl:
        x = cx_of(bp)
        s += arrow(x, ry + 50, x, ry + 96, RED, 2.2)
        s += text(x, ry + 112, lab, 10, RED, "middle", "bold")
    # біт стану (вгору, синій)
    xs = cx_of(8)
    s += arrow(xs, ry - 6, xs, ry - 44, BLUE, 2.2)
    s += text(xs, ry - 52, "READY — стан (від заліза)", 10, BLUE, "middle", "bold")

    s += rect(70, 360, W - 140, 44, LAMB, GOLD, 1.4, 10)
    s += text(W / 2, 380, "Записати в регістр = смикнути за важелі; прочитати = зняти показання.", 12.5, INK, "middle", "bold")
    s += text(W / 2, 397, "Те саме число, записане вдруге, нічого не змінить; читання двічі може дати різне.", 10.5, GREY, "middle")
    save("fig-20-3-2-register-bits.svg", s)


# ── Рис. 20.3.3 — три види регістрів ─────────────────────────────────────────
def fig33_register_kinds():
    W, H = 880, 370
    s = header(W, H)
    s += text(W / 2, 34, "Три види регістрів: керування, стану, даних", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "майже вся робота з периферією — танець цих трьох", 12.5, GREY, "middle", style="italic")
    s += rect(60, 150, 120, 90, LRED, RED, 2, 8)
    s += text(120, 190, "Ядро", 14, INK, "middle", "bold")
    s += text(120, 208, "(CPU)", 11, GREY, "middle")
    s += rect(700, 140, 150, 150, "#fafafa", INK, 2, 8)
    s += text(775, 205, "Периферія", 13, INK, "middle", "bold")
    s += text(775, 223, "(залізо)", 11, GREY, "middle")

    s += blk(380, 108, 180, 46, "Керування / config")
    s += blk(380, 182, 180, 46, "Стан / status")
    s += blk(380, 256, 180, 46, "Дані / data")

    # control: CPU -> reg -> залізо (write, red)
    s += arrow(182, 168, 378, 134, RED, 2.2)
    s += arrow(562, 131, 698, 175, RED, 2.2)
    s += text(360, 96, "пишемо (команда) →", 11, RED, "middle", "bold")
    # status: залізо -> reg -> CPU (read, blue)
    s += arrow(698, 225, 562, 205, BLUE, 2.2)
    s += arrow(378, 205, 200, 214, BLUE, 2.2)
    s += text(360, 244, "← читаємо (стан)", 11, BLUE, "middle", "bold")
    # data: both (green)
    s += arrow(200, 240, 378, 272, GREEN, 2.2)
    s += arrow(562, 279, 698, 258, GREEN, 2.2)
    s += text(360, 322, "↔ туди-сюди (корисний вантаж)", 11, GREEN, "middle", "bold")
    save("fig-20-3-3-register-kinds.svg", s)


# ── Рис. 20.3.4 — побітові операції (маски) ──────────────────────────────────
def fig34_bit_ops():
    W, H = 920, 540
    s = header(W, H)
    s += text(W / 2, 32, "Маски: точкове керування бітами (читай-зміни-запиши)", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "пишемо ціле слово, тож сусідні біти зберігаємо маскою", 12.5, GREY, "middle", style="italic")

    def panel(px, py, title, tcol, before, op, mask, after, hibit, note):
        o = rect(px, py, 430, 212, "#fbfbfb", FAINT, 1.6, 10)
        o += text(px + 16, py + 26, title, 12.5, tcol, "start", "bold")
        o += text(px + 16, py + 60, "до:", 10.5, GREY, "start")
        o += _bitword(px + 92, py + 44, before, 8, {hibit}, tcol, 34, 26, idx=False)
        o += text(px + 16, py + 106, op, 10.5, GREY, "start")
        o += _bitword(px + 92, py + 90, mask, 8, {hibit}, tcol, 34, 26, idx=False)
        o += text(px + 16, py + 152, "після:", 10.5, GREY, "start")
        o += _bitword(px + 92, py + 136, after, 8, {hibit}, tcol, 34, 26, idx=True)
        o += text(px + 215, py + 200, note, 10.5, tcol, "middle", "bold")
        return o

    v = 0x96  # 1001 0110
    s += panel(30, 82, "set — встановити біт 5", RED, v, "маска 1<<5:", 0x20, v | 0x20, 5,
               "АБО кладе 1, сусідні цілі")
    s += panel(470, 82, "clear — скинути біт 1", BLUE, v, "маска ~(1<<1):", 0xFD, v & ~0x02, 1,
               "І з ~маскою кладе 0")
    s += panel(30, 308, "toggle — перемкнути біт 4", GREEN, v, "маска 1<<4:", 0x10, v ^ 0x10, 4,
               "XOR перевертає біт")
    s += panel(470, 308, "test — перевірити біт 2", "#8a6a14", v, "маска 1<<2:", 0x04, v & 0x04, 2,
               "І → ≠0, отже біт встановлено")
    save("fig-20-3-4-bit-ops.svg", s)


# ── Рис. 20.3.5 — запалення світлодіода через регістри GPIO ───────────────────
def fig35_gpio_blink():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "Запалити світлодіод через регістри GPIO: DIR → OUT → ніжка", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "три побітові записи за трьома адресами — і залізо послухалось", 12.5, GREY, "middle", style="italic")
    s += rect(40, 80, 470, 320, "#fbfcff", INK, 2, 12)
    s += text(60, 102, "Вузол GPIO (узагальнено)", 13, INK, "start", "bold")
    cw, x0 = 34, 150

    def cx2(bitpos):
        return x0 + (8 - 1 - bitpos) * cw + cw / 2

    regs = [("DIR", 1 << 2, True, "①"), ("OUT", 1 << 2, True, "②"), ("IN", 0, False, "")]
    ys = [140, 220, 300]
    for (nm, val, hot, tag), y in zip(regs, ys):
        if tag:
            s += text(70, y + 24, tag, 13, RED, "start", "bold")
        s += text(96, y + 24, nm, 12.5, (RED if hot else GREY), "start", "bold")
        s += _bitword(x0, y, val, 8, {2} if hot else set(), RED, cw, 30, idx=(nm == "IN"))

    # вивід від OUT біт2 до ніжки й світлодіода
    bx = cx2(2)
    s += line(bx, 250, bx, 360, RED, 2.2)
    s += line(bx, 360, 540, 360, RED, 2.2)
    s += rect(540, 348, 16, 24, METAL, "#666666", 1)
    s += text(548, 392, "ніжка 2", 10.5, INK, "middle", "bold")
    s += line(556, 360, 640, 360, RED, 2.4)
    # світлодіод (трикутник + риска) зі сяйвом
    s += circle(690, 360, 26, "#fff4d6", "#e0a72a", 2)
    s += f'<path d="M 680,348 L 680,372 L 702,360 Z" fill="{RED}" stroke="{RED}"/>\n'
    s += line(702, 346, 702, 374, RED, 2.4)
    for dx, dy in [(18, -14), (22, 0), (18, 14)]:
        s += line(718, 360, 718 + dx, 360 + dy, "#e0a72a", 2)
    s += text(690, 406, "③ світлодіод світить", 11, "#b07d12", "middle", "bold")
    # підказки коду праворуч угорі
    s += rect(600, 90, 300, 150, "#fbfbfb", FAINT, 1.4, 10)
    s += text(616, 114, "DIR |= (1<<2);", 12.5, INK, "start", "bold")
    s += text(616, 138, "OUT |= (1<<2);   // увімк", 12.5, RED, "start", "bold")
    s += text(616, 162, "OUT &= ~(1<<2);  // вимк", 12.5, BLUE, "start", "bold")
    s += line(616, 178, 884, 178, FAINT, 1.2)
    s += text(616, 202, "digitalWrite(2, HIGH)", 11.5, GREY, "start")
    s += text(616, 222, "усередині робить те саме →", 10.5, GREY, "start", style="italic")
    save("fig-20-3-5-gpio-blink.svg", s)


# ── Рис. 20.3.6 — карта регістрів із даташита ────────────────────────────────
def fig36_register_map():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "Карта регістрів із даташита: база + зсуви + сенс бітів", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "адреса регістра = базова адреса + зсув; кожен біт має призначення", 12.5, GREY, "middle", style="italic")
    # таблиця
    s += text(60, 92, "база вузла: 0x4000_8000", 12.5, INK, "start", "bold")
    tx, ty, rw, rh = 60, 104, 360, 40
    rows = [("зсув", "регістр", True), ("0x00", "(резерв)", False), ("0x04", "CTRL — керування", False),
            ("0x08", "DIR — напрям", False), ("0x0C", "OUT — вихід", False),
            ("0x10", "IN — вхід", False), ("0x14", "STATUS — стан", False)]
    for i, (a, nm, hdr) in enumerate(rows):
        y = ty + i * rh
        fill = "#eef0f5" if hdr else ("#fff7e6" if a == "0x04" else "#ffffff")
        s += rect(tx, y, 90, rh, fill, INK, 1.2)
        s += rect(tx + 90, y, 270, rh, fill, INK, 1.2)
        s += text(tx + 45, y + 25, a, 11.5, INK, "middle", "bold" if hdr else "normal")
        s += text(tx + 100, y + 25, nm, 11.5, (RED if a == "0x04" else INK), "start", "bold" if (hdr or a == "0x04") else "normal")

    # розшифровка CTRL праворуч
    s += text(640, 92, "CTRL (0x04) по бітах:", 12.5, RED, "start", "bold")
    bx, by, cw = 470, 150, 40
    s += _bitword(bx, by, 0b00010110, 8, {0, 1, 5}, RED, cw, 36, idx=True)
    fields = [(0, "EN — дозвіл вузла"), (1, "MODE — режим"), (5, "IRQ-EN — дозвіл переривання")]
    for k, (bp, lab) in enumerate(fields):
        cxp = bx + (8 - 1 - bp) * cw + cw / 2
        ly = by + 60 + k * 26
        s += line(cxp, by + 50, cxp, ly, GREY, 1.2, dash="2,3")
        s += line(cxp, ly, bx + 40, ly, GREY, 1.2, dash="2,3")
        s += text(bx + 46, ly + 4, lab, 11, INK, "start", "bold")
    s += text(bx + 4 * cw, by - 18, "біти 2–3: SPEED (поле з 2 біт)", 10, GREY, "middle", style="italic")
    s += rect(440, 372, 440, 44, LAMB, GOLD, 1.4, 10)
    s += text(660, 392, "адреса CTRL = 0x4000_8000 + 0x04", 12, INK, "middle", "bold")
    s += text(660, 409, "= 0x4000_8004", 12, RED, "middle", "bold")
    save("fig-20-3-6-register-map.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §20.4 — Тактування й живлення МК (джерела такту; режими сну)
# ─────────────────────────────────────────────────────────────────────────────

def _dot(cx, cy, state):
    """on=зелений повний, off=сірий порожній, half=бурштиновий напівповний."""
    if state == "on":
        return circle(cx, cy, 7, GREEN, GREEN, 0) + circle(cx, cy, 7, "none", "#0d5a23", 1.2)
    if state == "half":
        return circle(cx, cy, 7, "#f3d27a", "#caa24a", 1.4)
    return circle(cx, cy, 7, "#ffffff", GREY, 1.6)


# ── Рис. 20.4.1 — такт як пульс ──────────────────────────────────────────────
def fig41_clock_pulse():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 34, "Такт — спільний пульс чипа: на кожному фронті ядро робить крок", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "прямокутна хвиля сталої частоти; період T = 1/f", 12.5, GREY, "middle", style="italic")
    y_hi, y_lo, x0 = 150, 214, 90
    s += _sqwave(x0, y_hi, y_lo, [50] * 10, INK, start_hi=False, sw=2.6)
    edges = [x0 + 50 + k * 100 for k in range(5)]
    for ex in edges:
        s += circle(ex, y_hi, 4, RED, RED, 0)
        s += arrow(ex, y_hi - 8, ex, y_hi - 32, RED, 1.8)
        s += text(ex, y_hi - 38, "крок", 9.5, RED, "middle", "bold")
    # період між двома фронтами
    s += arrow((edges[0] + edges[1]) / 2, 240, edges[0], 240, GREY, 1.6)
    s += arrow((edges[0] + edges[1]) / 2, 240, edges[1], 240, GREY, 1.6)
    s += text((edges[0] + edges[1]) / 2, 258, "T", 13, INK, "middle", "bold")
    s += line(edges[0], y_lo, edges[0], 246, GREY, 1, dash="2,3")
    s += line(edges[1], y_lo, edges[1], 246, GREY, 1, dash="2,3")
    s += text(x0 - 8, y_hi - 6, "1", 11, GREY, "end")
    s += text(x0 - 8, y_lo + 4, "0", 11, GREY, "end")
    s += rect(560, 286, 260, 50, LAMB, GOLD, 1.4, 10)
    s += text(690, 306, "f = 80 МГц  →  T = 1/f = 12.5 нс", 12.5, INK, "middle", "bold")
    s += text(690, 324, "80 млн кроків за секунду", 10.5, GREY, "middle")
    save("fig-20-4-1-clock-pulse.svg", s)


# ── Рис. 20.4.2 — джерела такту ──────────────────────────────────────────────
def fig42_clock_sources():
    W, H = 900, 480
    s = header(W, H)
    s += text(W / 2, 34, "Звідки береться такт: внутрішній RC, кварц і множення PLL", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "вибір між дешевизною й точністю", 12.5, GREY, "middle", style="italic")

    # RC
    s += rect(40, 92, 250, 150, "#fbfbfb", GREY, 2, 10)
    s += text(165, 116, "Внутрішній RC", 13.5, INK, "middle", "bold")
    s += f'<path d="M 90,150 q 12,-22 24,0 q 12,22 24,0 q 12,-22 24,0" fill="none" stroke="{GREY}" stroke-width="2"/>\n'
    s += text(165, 180, "усередині чипа · миттєвий старт", 10.5, GREY, "middle")
    s += text(165, 202, "дешево, без зовнішніх деталей", 10.5, GREY, "middle")
    s += text(165, 226, "неточно: ±1–5 %", 12, RED, "middle", "bold")

    # кварц
    s += rect(325, 92, 250, 150, "#fbfbfb", BLUE, 2, 10)
    s += text(450, 116, "Кварцовий резонатор", 13.5, BLUE, "middle", "bold")
    # символ кварцу
    s += line(420, 140, 420, 170, INK, 2)
    s += rect(428, 138, 44, 34, "#eef3ff", INK, 1.6)
    s += line(480, 140, 480, 170, INK, 2)
    s += text(450, 192, "зовнішня деталь (кристалик)", 10.5, GREY, "middle")
    s += text(450, 214, "повільніший старт, трохи дорожче", 10.5, GREY, "middle")
    s += text(450, 234, "дуже точно: ±10–50 ppm", 12, GREEN, "middle", "bold")

    # PLL ланцюг
    s += rect(610, 92, 250, 150, "#fbfbfb", FAINT, 2, 10)
    s += text(735, 116, "PLL — множник частоти", 13, INK, "middle", "bold")
    s += blk(626, 150, 90, 44, "кварц", "40 МГц")
    s += blk(742, 150, 56, 44, "×6")
    s += text(820, 176, "→", 16, INK, "middle", "bold")
    s += arrow(716, 172, 742, 172, INK, 2)
    s += blk2(640, 206, 180, 30, "ядро 240 МГц", [])
    s += arrow(770, 194, 730, 206, INK, 1.8)
    s += text(735, 232, "точність кварцу + швидкість", 10, GREY, "middle", style="italic")

    s += rect(120, 420, 660, 40, LGRN, GREEN, 1.4, 10)
    s += text(450, 444, "Більшість МК мають і внутрішній RC, і вхід для кварцу — джерело обирають під задачу.",
              12.5, INK, "middle", "bold")
    save("fig-20-4-2-clock-sources.svg", s)


# ── Рис. 20.4.3 — точність такту й наслідки ──────────────────────────────────
def fig43_accuracy():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 32, "Точність такту: коли вона критична", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "приймач зчитує біти за власним тактом — якщо він «тікає», момент схибить",
              12.5, GREY, "middle", style="italic")
    bits = [1, 0, 1, 1, 0, 0, 1, 0]
    cw, x0, y = 92, 80, 96
    for i, b in enumerate(bits):
        cx = x0 + i * cw
        s += rect(cx, y, cw, 40, "#f3f6fb", INK, 1.2)
        s += text(cx + cw / 2, y + 27, str(b), 14, INK, "middle", "bold")
    s += text(x0 - 10, y + 27, "дані:", 11, GREY, "end", "bold")

    def centers(off_fn):
        return [(x0 + i * cw + cw / 2 + off_fn(i), i) for i in range(len(bits))]

    # кварц — точно по центрах
    yc = 196
    s += text(x0 - 10, yc + 4, "Кварц", 11.5, GREEN, "end", "bold")
    s += text(x0 - 10, yc + 20, "±20 ppm", 9.5, GREY, "end")
    for cx, i in centers(lambda i: 0):
        s += arrow(cx, yc + 8, cx, y + 42, GREEN, 1.8)
        s += circle(cx, yc + 8, 3, GREEN, GREEN, 0)
    s += text(x0 + 8 * cw + 12, yc + 8, "✓ усі біти зчитано вірно", 12, GREEN, "start", "bold")

    # RC — момент «тікає»
    yr = 300
    s += text(x0 - 10, yr + 4, "RC", 11.5, RED, "end", "bold")
    s += text(x0 - 10, yr + 20, "±3 %", 9.5, GREY, "end")
    for cx, i in centers(lambda i: i * 13):
        col = RED if i >= 6 else "#c98"
        s += arrow(cx, yr + 8, cx, y + 42, col, 1.8)
        s += circle(cx, yr + 8, 3, col, col, 0)
        if i == 7:
            s += text(cx, yr + 26, "✗", 15, RED, "middle", "bold")
    s += text(x0 + 8 * cw + 12, yr + 8, "✗ момент «поплив» → хибний біт", 12, RED, "start", "bold")
    s += text(W / 2, 410, "Кварц відхиляється у тисячі разів менше за RC — для зв'язку це межа між «чисто» і «каша».",
              11.5, INK, "middle", "bold")
    save("fig-20-4-3-accuracy.svg", s)


# ── Рис. 20.4.4 — тактове дерево ─────────────────────────────────────────────
def fig44_clock_tree():
    W, H = 880, 450
    s = header(W, H)
    s += text(W / 2, 32, "Тактове дерево: один пульс — багато ритмів", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "майстер-частота ділиться на простих дільниках для різних споживачів",
              12.5, GREY, "middle", style="italic")
    s += blk2(40, 200, 150, 76, "Майстер", ["240 МГц"], fill=LRED, stroke=RED, lcol=RED)
    mx, my = 190, 238
    rows = [("Ядро", "240 МГц", None, 110), ("Шина", "120 МГц", "÷2", 200),
            ("Таймер", "30 МГц", "÷8", 290), ("UART-такт", "3.75 МГц", "÷64", 380)]
    for name, freq, div, y in rows:
        if div:
            s += line(mx, my, 360, y + 22, GREY, 2)
            s += blk(360, y, 70, 44, div)
            s += arrow(430, y + 22, 560, y + 22, GREEN, 2.2)
        else:
            s += arrow(mx, my, 560, y + 22, GREEN, 2.4)
            s += text((mx + 560) / 2, y + 12, "напряму", 10, GREY, "middle", style="italic")
        s += blk2(560, y, 200, 44, name, [freq])
    s += rect(120, 414, 640, 30, LGRN, GREEN, 1.4, 8)
    s += text(440, 434, "Рідше цокає — менше споживає: поділ частоти ще й ощадливий.", 12, INK, "middle", "bold")
    save("fig-20-4-4-clock-tree.svg", s)


# ── Рис. 20.4.5 — сходи режимів сну ──────────────────────────────────────────
def fig45_sleep_modes():
    W, H = 920, 480
    s = header(W, H)
    s += text(W / 2, 32, "Сходи сну: вимикаємо те, що не потрібно", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "що нижче — то менше споживання, але повільніше прокидання й більше втраченого стану",
              12, GREY, "middle", style="italic")
    cols = [("Ядро", 250), ("Периферія", 340), ("RAM", 430), ("Будильник", 525)]
    s += text(70, 104, "режим", 11.5, INK, "start", "bold")
    for nm, cx in cols:
        s += text(cx, 104, nm, 11, INK, "middle", "bold")
    s += text(660, 104, "споживання", 11, INK, "middle", "bold")
    s += text(820, 104, "прокидання", 11, INK, "middle", "bold")
    s += line(60, 114, 880, 114, FAINT, 1.4)

    modes = [
        ("Активний", ["on", "on", "on", "on"], 1.0, RED, "—", 150),
        ("Легкий сон", ["off", "on", "on", "on"], 0.4, "#caa24a", "миттєво", 230),
        ("Глибокий сон", ["off", "off", "half", "on"], 0.04, GREEN, "повільніше", 310),
    ]
    for name, states, pw, pcol, wake, y in modes:
        s += rect(60, y - 26, 820, 64, "#fcfcfc", FAINT, 1.2, 8)
        s += text(74, y + 8, name, 12.5, INK, "start", "bold")
        for (nm, cx), st in zip(cols, states):
            s += _dot(cx, y + 4, st)
        # бар споживання
        s += rect(600, y - 6, 120, 18, "#f1f1f1", GREY, 1)
        s += rect(600, y - 6, max(6, 120 * pw), 18, pcol, pcol, 0)
        lab = "повне" if pw == 1.0 else ("середнє" if pw > 0.1 else "мікроампери")
        s += text(660, y + 30, lab, 9.5, pcol, "middle", "bold")
        s += text(820, y + 8, wake, 11, INK, "middle", "bold")
    s += text(250, 372, "● увімкнено", 10.5, GREEN, "start", "bold")
    s += text(370, 372, "○ вимкнено", 10.5, GREY, "start", "bold")
    s += text(480, 372, "◐ лише крихта стану", 10.5, "#caa24a", "start", "bold")
    s += rect(120, 396, 680, 56, LGRN, GREEN, 1.4, 10)
    s += text(460, 418, "Прокидає подія: ніжка, маловитратний таймер-будильник або дані.", 12, INK, "middle", "bold")
    s += text(460, 438, "Робота наскоками (duty cycling): спить ~99 % часу — звідси місяці від батарейки.", 11, GREY, "middle")
    save("fig-20-4-5-sleep-modes.svg", s)


# ── Рис. 20.4.6 — робота наскоками (duty cycling) ────────────────────────────
def fig46_duty_cycle():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Робота наскоками: короткі піки струму на тлі довгого сну", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "довгі долини сну тягнуть середній струм донизу", 12.5, GREY, "middle", style="italic")
    x0, x1 = 90, 840
    ybase, ytop = 320, 110
    s += arrow(x0, ybase, x0, 90, INK, 2)
    s += text(x0 - 8, 100, "струм", 11, INK, "end", "bold")
    s += arrow(x0, ybase, 860, ybase, INK, 2)
    s += text(852, ybase + 18, "час", 11, INK, "start")
    # без сну — пунктир угорі
    s += line(x0, ytop, x1, ytop, GREY, 1.4, dash="6,4")
    s += text(x1, ytop - 6, "без сну: 40 мА весь час", 10.5, GREY, "end", style="italic")
    # піки
    spikes = [150, 340, 530, 720]
    sw = 16
    d = f"M {x0:.0f},{ybase:.0f}"
    for sx in spikes:
        d += f" H {sx:.0f} V {ytop:.0f} H {sx + sw:.0f} V {ybase:.0f}"
    d += f" H {x1:.0f}"
    s += f'<path d="{d}" fill="none" stroke="{RED}" stroke-width="2.4"/>\n'
    for sx in spikes:
        s += text(sx + sw / 2, ytop - 8, "40 мА", 9.5, RED, "middle", "bold")
    s += text(spikes[0] + sw / 2, ybase + 16, "100 мс", 9, RED, "middle")
    # період
    s += arrow((spikes[0] + spikes[1]) / 2, ybase + 30, spikes[0] + sw / 2, ybase + 30, GREY, 1.4)
    s += arrow((spikes[0] + spikes[1]) / 2, ybase + 30, spikes[1] + sw / 2, ybase + 30, GREY, 1.4)
    s += text((spikes[0] + spikes[1]) / 2, ybase + 44, "10 с", 10, INK, "middle", "bold")
    s += text(x1, ybase - 6, "сон: 10 мкА", 10, GREEN, "end", "bold")
    # середній
    yavg = ybase - 6
    s += line(x0, yavg, x1, yavg, GREEN, 1.8, dash="4,3")
    s += text(x0 + 6, yavg - 6, "середній ≈ 0.41 мА", 11, GREEN, "start", "bold")
    s += rect(560, 96, 300, 56, LAMB, GOLD, 1.4, 10)
    s += text(710, 118, "1000 мА·год / 0.41 мА ≈ 102 доби", 11.5, INK, "middle", "bold")
    s += text(710, 138, "без сну: лише ~1 доба", 11, RED, "middle", "bold")
    save("fig-20-4-6-duty-cycle.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §20.5 — Архітектура ESP32: два ядра, радіо, багата периферія
# ─────────────────────────────────────────────────────────────────────────────

def _antenna(x, y_base, h=40, col=INK):
    o = line(x, y_base, x, y_base - h, col, 2.4)
    o += circle(x, y_base - h, 3, col, col, 0)
    return o


def _waves(x, y, n=3, col=GREEN, r0=16, dr=13):
    o = ""
    for k in range(n):
        r = r0 + k * dr
        o += (f'<path d="M {x:.0f},{y - r:.0f} A {r},{r} 0 0 1 {x:.0f},{y + r:.0f}" '
              f'fill="none" stroke="{col}" stroke-width="1.8"/>\n')
    return o


# ── Рис. 20.5.1 — блок-схема ESP32 (SoC) ─────────────────────────────────────
def fig51_esp32_soc():
    W, H = 920, 545
    s = header(W, H)
    s += text(W / 2, 34, "ESP32 — система-на-чипі: анатомія §20.2, подвоєна, плюс радіо", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "один чіп завбільшки з ніготь несе повноцінний бездротовий комп'ютер", 12, GREY, "middle", style="italic")
    s += rect(60, 96, 800, 400, "#fbfcff", INK, 2.4, 14)
    s += text(80, 116, "ESP32 (кристал)", 11.5, GREY, "start", "bold")
    # ядра
    s += blk2(90, 138, 150, 64, "Ядро 0", ["240 МГц"], fill=LRED, stroke=RED, lcol=RED)
    s += blk2(256, 138, 150, 64, "Ядро 1", ["240 МГц"], fill=LRED, stroke=RED, lcol=RED)
    s += blk2(422, 148, 96, 44, "ULP", ["ощадний"])
    # радіо
    s += rect(560, 130, 280, 92, "#fff1e6", "#d2772a", 2, 8)
    s += text(700, 156, "Радіо", 14, "#b9560f", "middle", "bold")
    s += text(700, 176, "Wi-Fi 2.4 ГГц + Bluetooth/BLE", 10.5, INK, "middle", "bold")
    s += text(700, 194, "приймач-передавач", 9.5, GREY, "middle")
    s += _antenna(820, 130, 42, "#b9560f")
    s += _waves(826, 100, 2, "#d2772a", 10, 9)
    s += text(820, 80, "антена", 10, "#b9560f", "middle", "bold")
    # шина
    busY = 250
    s += line(96, busY, 824, busY, GREEN, 5)
    s += text(820, busY - 9, "внутрішня шина", 10.5, GREEN, "end", "bold")
    for x in (165, 331, 470):
        s += line(x, 202, x, busY, GREEN, 2)
    s += line(700, 222, 700, busY, GREEN, 2)
    # пам'ять
    s += blk2(90, 286, 150, 70, "SRAM", ["~520 КБ · дані"], fill="#eef6ef", stroke=GREEN, lcol=GREEN)
    s += blk2(256, 286, 130, 70, "ROM", ["boot-код"])
    s += blk2(402, 286, 150, 70, "RTC-пам'ять", ["живе у сні"])
    for x in (165, 321, 477):
        s += line(x, busY, x, 286, GREEN, 2)
    # периферія
    s += rect(560, 268, 280, 152, "#fafafa", INK, 1.8, 10)
    s += text(700, 288, "Багата периферія", 12.5, INK, "middle", "bold")
    for i, p in enumerate(["GPIO ×34 (матриця)", "SPI · I2C · UART · I2S",
                           "ШІМ ×16 · ADC · DAC", "CAN · дотик · Холл", "крипто (AES/SHA/RSA)"]):
        s += text(700, 310 + i * 22, p, 10.5, INK, "middle")
    s += line(700, busY, 700, 268, GREEN, 2)
    s += text(W / 2, 520, "Зовні чипа — лише кварц, флеш-пам'ять і антена; решта вся всередині.",
              12, INK, "middle", "bold")
    save("fig-20-5-1-esp32-soc.svg", s)


# ── Рис. 20.5.2 — два ядра + ULP ─────────────────────────────────────────────
def fig52_two_cores():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Два ядра ESP32 (і ще одне крихітне)", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "справжня паралельність: радіо на одному ядрі, ваша логіка — на другому", 12, GREY, "middle", style="italic")
    s += blk2(110, 132, 230, 92, "Ядро 0 (PRO)", ["Xtensa LX6 · 240 МГц"], fill=LRED, stroke=RED, lcol=RED)
    s += text(225, 250, "↳ типово: радіо-стек", 11, "#b9560f", "middle", "bold")
    s += blk2(460, 132, 230, 92, "Ядро 1 (APP)", ["Xtensa LX6 · 240 МГц"], fill=LRED, stroke=RED, lcol=RED)
    s += text(575, 250, "↳ типово: ваша програма", 11, GREEN, "middle", "bold")
    s += text(400, 124, "паралельно", 11, GREY, "middle", style="italic")
    s += blk2(730, 150, 150, 76, "ULP", ["ультраощадний", "живе у сні"])
    s += rect(110, 288, 580, 60, "#eef6ef", GREEN, 1.8, 8)
    s += text(400, 314, "спільна пам'ять і периферія", 12.5, INK, "middle", "bold")
    s += text(400, 332, "(обидва ядра — по тій самій шині)", 10, GREY, "middle")
    s += arrow(225, 224, 225, 288, INK, 2)
    s += arrow(575, 224, 575, 288, INK, 2)
    s += arrow(805, 226, 690, 300, GREY, 1.8, dash="4,3")
    s += rect(110, 368, 770, 38, LGRN, GREEN, 1.4, 8)
    s += text(495, 391, "Друге ядро — рятунок для зв'язку: радіо не краде час у вашої логіки.", 12, INK, "middle", "bold")
    save("fig-20-5-2-two-cores.svg", s)


# ── Рис. 20.5.3 — пам'ять: своя + зовнішня флеш через кеш ─────────────────────
def fig53_flash_cache():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 34, "Пам'ять ESP32: своя на чипі та зовнішня флеш через кеш", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "код лежить у зовнішній флеш, але ядро виконує його так, ніби він на чипі", 12, GREY, "middle", style="italic")
    s += rect(50, 96, 520, 300, "#fbfcff", INK, 2.2, 12)
    s += text(70, 118, "ESP32 (кристал)", 11.5, GREY, "start", "bold")
    s += blk2(80, 146, 150, 70, "Ядро", ["виконує код"], fill=LRED, stroke=RED, lcol=RED)
    s += blk2(300, 146, 240, 70, "Кеш + MMU", ["відображає флеш у пам'ять"], fill=LAMB, stroke=GOLD, lcol="#8a6a14")
    s += arrow(300, 181, 232, 181, INK, 2.2)
    s += blk2(80, 250, 150, 64, "SRAM ~520 КБ", ["дані"], fill="#eef6ef", stroke=GREEN, lcol=GREEN)
    s += blk2(250, 250, 120, 64, "ROM", ["boot"])
    s += blk2(390, 250, 150, 64, "RTC-пам'ять", ["живе у сні"])
    # зовнішня флеш
    s += rect(645, 175, 200, 120, "#2b2b2b", "#000000", 1.6, 8)
    s += text(745, 222, "Зовнішня", 12, "#ffffff", "middle", "bold")
    s += text(745, 244, "флеш 4 МБ", 13, "#ffffff", "middle", "bold")
    s += text(745, 264, "(програма)", 10, "#cfcfcf", "middle")
    s += text(745, 312, "окремий корпус на платі", 10, GREY, "middle", style="italic")
    s += arrow(645, 210, 542, 178, INK, 2.4)
    s += text(600, 182, "SPI", 10, GREY, "middle", "bold")
    s += rect(110, 408, 700, 26, LGRN, GREEN, 1.2, 8)
    s += text(460, 425, "Для коду це непомітно: зовнішня флеш «бачиться» як звичайна пам'ять (§20.3).", 11.5, INK, "middle", "bold")
    save("fig-20-5-3-flash-cache.svg", s)


# ── Рис. 20.5.4 — радіо на чипі ──────────────────────────────────────────────
def fig54_radio():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Радіо на чипі: Wi-Fi і Bluetooth зі спільним трактом 2.4 ГГц", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "те, чого не було в загальній анатомії — і головна риса ESP32", 12, GREY, "middle", style="italic")
    s += rect(60, 150, 300, 200, "#fbfcff", INK, 2.2, 12)
    s += text(210, 176, "ESP32", 12, GREY, "middle", "bold")
    s += rect(90, 198, 240, 92, "#fff1e6", "#d2772a", 2, 8)
    s += text(210, 224, "Радіо 2.4 ГГц", 13, "#b9560f", "middle", "bold")
    s += text(210, 246, "приймач-передавач", 10, GREY, "middle")
    s += text(210, 268, "(спільний тракт)", 10, GREY, "middle")
    s += _antenna(340, 198, 64, "#b9560f")
    s += text(340, 122, "антена", 10, "#b9560f", "middle", "bold")
    s += _waves(360, 210, 3, "#d2772a", 16, 13)
    s += rect(560, 108, 290, 92, "#fbfbfb", BLUE, 1.8, 10)
    s += text(705, 134, "Wi-Fi → роутер / інтернет", 12.5, BLUE, "middle", "bold")
    s += text(705, 156, "своя мережа · вебсервер · хмара", 10, GREY, "middle")
    s += text(705, 178, "TCP/UDP", 10, GREY, "middle", style="italic")
    s += arrow(366, 184, 558, 150, BLUE, 2.2, dash="5,4")
    s += rect(560, 252, 290, 92, "#fbfbfb", GREEN, 1.8, 10)
    s += text(705, 278, "Bluetooth/BLE → смартфон", 12.5, GREEN, "middle", "bold")
    s += text(705, 300, "гаджети · гарнітури · додатки", 10, GREY, "middle")
    s += arrow(366, 250, 558, 292, GREEN, 2.2, dash="5,4")
    s += rect(120, 372, 700, 32, LAMB, GOLD, 1.4, 8)
    s += text(470, 392, "Бездротовий зв'язок — прямо в чипі (фізика й протоколи радіо — Модуль 6).", 11.5, INK, "middle", "bold")
    save("fig-20-5-4-radio.svg", s)


# ── Рис. 20.5.5 — багата периферія + матриця ніжок ───────────────────────────
def fig55_peripherals_matrix():
    W, H = 920, 470
    s = header(W, H)
    s += text(W / 2, 34, "Багата периферія й гнучка матриця ніжок", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "мультиплексування виводів (§20.2), доведене до крайньої гнучкості", 12, GREY, "middle", style="italic")
    # каталог
    s += rect(40, 88, 300, 350, "#fbfbfb", INK, 1.8, 10)
    s += text(190, 112, "Периферія ESP32", 13, INK, "middle", "bold")
    for i, it in enumerate(["≈34 × GPIO", "4 × SPI  ·  2 × I2C", "3 × UART  ·  2 × I2S",
                            "16 × ШІМ (LEDC)", "2 × ЦАП  ·  12-біт АЦП", "дотик · Холл · термо",
                            "CAN · карти пам'яті", "крипто: AES/SHA/RSA/RNG"]):
        s += text(60, 148 + i * 35, "• " + it, 11.5, INK, "start")
    # матриця
    s += text(640, 112, "Матриця ніжок (GPIO matrix)", 13, INK, "middle", "bold")
    s += rect(560, 150, 160, 232, LAMB, GOLD, 2, 10)
    s += text(640, 172, "крос-комутатор", 10.5, "#8a6a14", "middle", "bold")
    sigs = ["UART_TX", "SPI_CLK", "I2C_SDA", "PWM0"]
    pins = ["IO4", "IO5", "IO17", "IO21", "IO23"]
    for i, sg in enumerate(sigs):
        y = 206 + i * 44
        s += text(548, y + 4, sg, 10.5, INK, "end", "bold")
        s += line(550, y, 560, y, GREY, 1.6)
    for j, pn in enumerate(pins):
        y = 192 + j * 40
        s += text(732, y + 4, pn, 10.5, INK, "start", "bold")
        s += line(720, y, 730, y, GREY, 1.6)
    for i in range(4):
        s += line(566, 206 + i * 44, 714, 206 + i * 44, FAINT, 1)
    for j in range(5):
        s += line(578 + j * 30, 184, 578 + j * 30, 372, FAINT, 1)
    # підсвічений маршрут UART_TX -> IO17
    s += line(560, 206, 638, 206, RED, 2.2)
    s += line(638, 206, 638, 272, RED, 2.2)
    s += line(638, 272, 720, 272, RED, 2.2)
    s += text(640, 408, "будь-який сигнал → майже будь-яка ніжка", 11, "#8a6a14", "middle", "bold")
    save("fig-20-5-5-peripherals-matrix.svg", s)


# ── Рис. 20.5.6 — глибокий сон з ULP ─────────────────────────────────────────
def fig56_deep_sleep_ulp():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 34, "Глибокий сон ESP32: великі ядра сплять, ULP і RTC живі", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "апаратне втілення «роботи наскоками» з §20.4", 12, GREY, "middle", style="italic")
    s += rect(60, 96, 640, 250, "#f4f4f4", GREY, 2, 12)
    s += text(80, 118, "ESP32 у глибокому сні", 11.5, GREY, "start", "bold")
    s += blk2(80, 146, 180, 66, "Ядро 0", ["✕ вимкнено"], fill="#ececec", stroke=GREY, lcol=GREY)
    s += blk2(278, 146, 180, 66, "Ядро 1", ["✕ вимкнено"], fill="#ececec", stroke=GREY, lcol=GREY)
    s += blk2(476, 146, 150, 66, "Радіо", ["✕ вимкнено"], fill="#ececec", stroke=GREY, lcol=GREY)
    s += rect(80, 240, 546, 86, LGRN, GREEN, 2, 10)
    s += text(353, 262, "живі (майже нуль споживання):", 11.5, GREEN, "middle", "bold")
    s += blk(100, 278, 140, 36, "ULP")
    s += blk(262, 278, 150, 36, "RTC-периферія")
    s += blk(434, 278, 172, 36, "RTC-пам'ять")
    s += rect(720, 110, 160, 232, "#fbfbfb", FAINT, 1.6, 10)
    s += text(800, 134, "ULP сам:", 12, INK, "middle", "bold")
    for i, st in enumerate(["прокинутись", "зняти давач", "вирішити", "спати далі", "або збудити ядра"]):
        s += text(736, 162 + i * 30, "• " + st, 10.5, INK, "start")
    s += rect(120, 372, 700, 44, LGRN, GREEN, 1.4, 10)
    s += text(470, 392, "ULP опитує давач сам і будить великі ядра лише за потреби.", 11.5, INK, "middle", "bold")
    s += text(470, 409, "Звідси — місяці автономності (duty cycling із §20.4).", 10.5, GREY, "middle")
    save("fig-20-5-6-deep-sleep-ulp.svg", s)


# ── Рис. 20.5.7 — специфікація ESP32 за анатомією ────────────────────────────
def fig57_spec():
    W, H = 920, 430
    s = header(W, H)
    s += text(W / 2, 34, "Специфікація ESP32, розкладена на знайому анатомію", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "жодної незнайомої графи — лише складові з тем §20.1–§20.4", 12, GREY, "middle", style="italic")
    s += line(40, 86, 880, 86, FAINT, 1.2)
    rows = [
        ("ЯДРО", RED, ["2 × 32-біт", "240 МГц"]),
        ("ПАМ'ЯТЬ", GREEN, ["520 КБ SRAM", "4 МБ флеш (зовні)"]),
        ("РАДІО", "#d2772a", ["Wi-Fi 2.4 ГГц", "Bluetooth / BLE"]),
        ("ПЕРИФЕРІЯ", BLUE, ["~34 GPIO", "ADC · DAC", "SPI/I2C/UART", "ШІМ ×16"]),
        ("ЖИВЛЕННЯ", "#8a6a14", ["40 МГц+PLL→240", "глибокий сон + ULP"]),
    ]
    y0 = 100
    for r, (cat, col, chips) in enumerate(rows):
        y = y0 + r * 58
        s += text(48, y + 26, cat, 12.5, col, "start", "bold")
        x = 210
        for c in chips:
            w = max(110, int(len(c) * 8.4) + 28)
            fill = _tint(col) if col in (RED, GREEN, BLUE) else "#f7f4ea"
            s += rect(x, y + 4, w, 36, fill, col, 2, 8)
            s += text(x + w / 2, y + 27, c, 11.5, col, "middle", "bold")
            x += w + 14
    s += rect(120, 394, 680, 28, LAMB, GOLD, 1.2, 8)
    s += text(460, 413, "Ми не «вчили ESP32» окремо — ми зрозуміли мікроконтролер, а ESP32 — його багате втілення.",
              11.5, INK, "middle", "bold")
    save("fig-20-5-7-spec.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  📜 Історія до §20.5 — ESP8266 → ESP32 (фігури 20.5i.N)
# ─────────────────────────────────────────────────────────────────────────────

# ── Рис. 20.5i.1 — таймлайн «як ESP підкорив аматорів» ───────────────────────
def fig5i1_timeline():
    W, H = 920, 660
    s = header(W, H)
    s += text(W / 2, 38, "Як ESP підкорив аматорів: ланцюг подій", 20, INK, "middle", "bold")
    s += text(W / 2, 60, "від дорогого Wi-Fi до стандарту IoT — кожен щабель нове питання", 12.5, GREY, "middle", style="italic")
    spine = 250
    top, bot = 96, H - 30
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("до 2014", "Дорогий Wi-Fi",
         "Плата зв'язку $30–40 — дорожча за весь проєкт. Як вивести саморобку в мережу?", False, False),
        ("2014", "ESP8266 / Espressif · AI-Thinker",
         "Дешевий «перехідник на Wi-Fi» за $5. Невже лише причіп до Arduino?", False, False),
        ("2014–15", "Відкриття спільноти",
         "А всередині — справжній 32-біт комп'ютер! Та документація китайською", False, False),
        ("2015", "NodeMCU + ядро Arduino",
         "Чіп за $3 програмують як Arduino — стіни впали → вибух проєктів", False, False),
        ("2016", "ESP32 / Espressif",
         "Два ядра, +Bluetooth, готова екосистема з першого дня", False, True),
        ("сьогодні", "Стандарт IoT",
         "Чому саме ESP підкорив аматорів?", True, False),
    ]
    n = len(nodes)
    for i, (yr, who, q, dest, accent) in enumerate(nodes):
        y = top + 30 + (bot - top - 60) * i / (n - 1)
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
    save("fig-20-5i-1-timeline.svg", s)


# ── Рис. 20.5i.2 — цінова революція ──────────────────────────────────────────
def fig5i2_price_shock():
    W, H = 900, 460
    s = header(W, H)
    s += text(W / 2, 34, "Цінова революція: вхід у мережу подешевшав у ~10 разів", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "не «трохи дешевше», а зміна того, що взагалі можна собі дозволити", 12.5, GREY, "middle", style="italic")
    s += rect(50, 96, 360, 330, "none", FAINT, 2, 14)
    s += text(230, 122, "до 2014: Wi-Fi-плата розширення", 13, INK, "middle", "bold")
    s += rect(110, 310, 240, 70, "#dfe7d8", "#4f7a3a", 2, 8)
    s += text(230, 350, "ваш проєкт", 11, GREY, "middle")
    s += rect(120, 210, 220, 86, "#cdd8ea", BLUE, 2, 8)
    s += text(230, 248, "Wi-Fi shield", 13, BLUE, "middle", "bold")
    s += text(230, 268, "громіздкий, вередливий", 9.5, GREY, "middle")
    s += rect(150, 168, 160, 34, "#ffffff", RED, 2, 8)
    s += text(230, 190, "$30–40", 15, RED, "middle", "bold")
    s += text(230, 406, "дорожче за весь інший проєкт", 11, RED, "middle", "bold")
    s += arrow(420, 250, 490, 250, INK, 4)
    s += text(455, 236, "÷10", 14, INK, "middle", "bold")
    s += rect(500, 96, 360, 330, "none", FAINT, 2, 14)
    s += text(680, 122, "2014: модуль ESP8266", 13, INK, "middle", "bold")
    s += rect(620, 250, 120, 76, "#2f7d4a", "#1c5530", 2, 8)
    s += text(680, 284, "ESP8266", 13, "#ffffff", "middle", "bold")
    s += text(680, 304, "Wi-Fi усередині", 9.5, "#d6efdd", "middle")
    s += _antenna(740, 250, 28, "#8fcf9f")
    s += rect(620, 200, 120, 34, "#ffffff", GREEN, 2, 8)
    s += text(680, 222, "~$3", 15, GREEN, "middle", "bold")
    s += text(680, 360, "Wi-Fi + комп'ютер", 11, GREEN, "middle", "bold")
    s += text(680, 378, "за ціну чашки кави", 10.5, GREEN, "middle")
    save("fig-20-5i-2-price-shock.svg", s)


# ── Рис. 20.5i.3 — «перехідник» виявився комп'ютером ─────────────────────────
def fig5i3_accidental_computer():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Маскування: «перехідник» виявився комп'ютером", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "копійчану скриньку продавали як причіп — а в ній ховався мережевий комп'ютер",
              12.5, GREY, "middle", style="italic")
    s += rect(40, 88, 400, 300, "none", FAINT, 2, 14)
    s += text(240, 114, "Очікували: німий перехідник", 13.5, INK, "middle", "bold")
    s += arrow(70, 212, 150, 212, INK, 2)
    s += text(66, 208, "UART", 10, GREY, "end")
    s += rect(150, 178, 180, 72, "#eef0f5", GREY, 2, 8)
    s += text(240, 210, "AT-перехідник", 12.5, INK, "middle", "bold")
    s += text(240, 230, "serial → Wi-Fi", 10, GREY, "middle")
    s += _antenna(330, 178, 30, GREY)
    s += _waves(346, 178, 2, GREY, 10, 8)
    s += text(240, 302, "лише з'єднує ЧУЖУ плату з Wi-Fi", 11, GREY, "middle")
    s += text(240, 322, "за текстовими AT-командами", 10, GREY, "middle")
    s += rect(460, 88, 400, 300, "none", LGRN, 2, 14)
    s += text(660, 114, "Виявилось: цілий комп'ютер", 13.5, GREEN, "middle", "bold")
    s += rect(540, 150, 210, 160, "#fbfcff", GREEN, 2, 10)
    s += blk(556, 168, 178, 40, "Ядро 32-біт · ~80 МГц")
    s += blk(556, 216, 82, 40, "RAM")
    s += blk(652, 216, 82, 40, "Wi-Fi")
    s += text(645, 300, "САМ виконує власний код", 11, GREEN, "middle", "bold")
    s += _antenna(770, 150, 28, "#b9560f")
    s += _waves(784, 150, 2, "#d2772a", 10, 8)
    s += text(660, 332, "жодної головної плати не треба", 9.5, GREY, "middle")
    save("fig-20-5i-3-accidental-computer.svg", s)


# ── Рис. 20.5i.4 — спільнота відчиняє чіп ────────────────────────────────────
def fig5i4_community_unlock():
    W, H = 900, 480
    s = header(W, H)
    s += text(W / 2, 34, "Як спільнота відчинила ESP8266 для всіх", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "те, на що бракувало фірми, гурт незнайомців зробив за місяці", 12.5, GREY, "middle", style="italic")
    stages = [
        ("Дешевий чіп з усім потенціалом", "…але документація — китайською, уривками", "#fff7e6", "#b9890f", 90),
        ("Глобальна спільнота", "розбирає · перекладає · пише свою документацію", "#fbfbfb", INK, 174),
        ("Зручні способи програмувати", "NodeMCU (скрипти Lua)  ·  ядро Arduino для ESP", "#eef3ff", BLUE, 258),
        ("Wi-Fi-комп'ютер за $3 — як Arduino", "→ вибух аматорських проєктів «розумних речей»", "#eef6ef", GREEN, 342),
    ]
    for i, (t1, t2, fill, col, y) in enumerate(stages):
        s += rect(190, y, 520, 64, fill, col, 2, 10)
        s += text(450, y + 27, t1, 13.5, col, "middle", "bold")
        s += text(450, y + 47, t2, 10.5, GREY, "middle")
        if i < len(stages) - 1:
            s += arrow(450, y + 64, 450, y + 80, INK, 2.4)
    s += text(W / 2, 438, "Звідси — велетенська спільнота, гори прикладів і бібліотек ESP донині.", 12, INK, "middle", "bold")
    save("fig-20-5i-4-community-unlock.svg", s)


# ── Рис. 20.5i.5 — ESP8266 → ESP32 ───────────────────────────────────────────
def fig5i5_esp8266_vs_esp32():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Від ESP8266 (2014) до ESP32 (2016): що змінилось", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "залізо стало кращим — але переможним його зробила готова екосистема",
              12.5, GREY, "middle", style="italic")
    s += rect(300, 86, 260, 46, "#eef3ff", BLUE, 2, 8)
    s += text(430, 114, "ESP8266 · 2014", 13.5, BLUE, "middle", "bold")
    s += rect(600, 86, 260, 46, "#eef6ef", GREEN, 2, 8)
    s += text(730, 114, "ESP32 · 2016", 13.5, GREEN, "middle", "bold")
    rows = [
        ("Ядра", "одне (~80 МГц)", "два (до 240 МГц)"),
        ("Радіо", "лише Wi-Fi", "Wi-Fi + Bluetooth/BLE"),
        ("Периферія, ніжки", "небагато", "щедро (матриця ніжок)"),
        ("Документація, SDK", "«зроби сам» (спільнота)", "офіційна: ESP-IDF + Arduino"),
    ]
    for i, (lab, a, b) in enumerate(rows):
        y = 146 + i * 64
        s += text(60, y + 30, lab, 12.5, INK, "start", "bold")
        s += rect(300, y, 260, 52, "#fbfdff", BLUE, 1.4, 8)
        s += text(430, y + 31, a, 11, INK, "middle")
        s += rect(600, y, 260, 52, "#fbfefb", GREEN, 1.4, 8)
        s += text(730, y + 31, b, 11, INK, "middle", "bold")
    s += rect(120, 420, 660, 34, LGRN, GREEN, 1.4, 8)
    s += text(450, 441, "ESP32 вийшов одразу з екосистемою — і став стандартом аматорського IoT.", 12, INK, "middle", "bold")
    save("fig-20-5i-5-esp8266-vs-esp32.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §20.6 — ESP32 проти простого 8-біт МК
# ─────────────────────────────────────────────────────────────────────────────

# ── Рис. 20.6.1 — два кінці шкали ────────────────────────────────────────────
def fig61_two_ends():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Два кінці шкали — і обидва це мікроконтролери", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "«потужніший» не означає «кращий» — лише «правіше на шкалі»", 12.5, GREY, "middle", style="italic")
    axisY = 220
    s += line(120, axisY, 780, axisY, INK, 2.4)
    s += arrow(770, axisY, 806, axisY, INK, 2.4)
    s += text(W / 2, axisY + 84, "обчислювальна вага →", 12, INK, "middle", "bold")
    # 8-біт ліворуч
    s += rect(70, 92, 230, 92, LBLUE, BLUE, 2, 10)
    s += text(185, 114, "Простий 8-біт", 13.5, BLUE, "middle", "bold")
    for i, t in enumerate(["1× 8-біт · 8–20 МГц", "кілобайти пам'яті", "без радіо · копійки · мкВт"]):
        s += text(185, 134 + i * 18, t, 10, INK, "middle")
    s += circle(180, axisY, 8, "#ffffff", BLUE, 3)
    s += line(185, 184, 180, axisY - 8, BLUE, 1.4, dash="2,3")
    # ESP32 праворуч
    s += rect(600, 92, 250, 92, LGRN, GREEN, 2, 10)
    s += text(725, 114, "ESP32", 13.5, GREEN, "middle", "bold")
    for i, t in enumerate(["2× 32-біт · до 240 МГц", "сотні КБ · мегабайти флеш", "радіо · багата периферія"]):
        s += text(725, 134 + i * 18, t, 10, INK, "middle")
    s += circle(720, axisY, 9, "#ffffff", GREEN, 3)
    s += line(725, 184, 720, axisY - 8, GREEN, 1.4, dash="2,3")
    # дужка спільності
    s += line(180, axisY + 30, 720, axisY + 30, GREY, 1.6)
    s += line(180, axisY + 24, 180, axisY + 30, GREY, 1.6)
    s += line(720, axisY + 24, 720, axisY + 30, GREY, 1.6)
    s += text(450, axisY + 50, "усе це — мікроконтролери (та сама анатомія §20.2)", 12, INK, "middle", "bold")
    save("fig-20-6-1-two-ends.svg", s)


# ── Рис. 20.6.2 — порівняння по осях (діаграма-розкид) ───────────────────────
def fig62_axes():
    W, H = 920, 500
    s = header(W, H)
    s += text(W / 2, 32, "По яких осях вони різняться", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "ESP32 переважає згори, простий 8-біт — знизу: кожен кращий у своєму", 12, GREY, "middle", style="italic")
    cx = 460
    s += line(cx, 100, cx, 452, GREY, 1.4)
    s += text(250, 92, "◀ перевага 8-біт", 11.5, BLUE, "middle", "bold")
    s += text(672, 92, "перевага ESP32 ▶", 11.5, GREEN, "middle", "bold")
    axes = [
        ("Обчислення", 1, 0.95), ("Пам'ять", 1, 0.92), ("Радіо (Wi-Fi/BT)", 1, 0.86),
        ("Периферія", 1, 0.7),
        ("Дешевизна", -1, 0.82), ("Простота, надійність", -1, 0.74),
        ("Малий розмір", -1, 0.6), ("Ощадність уві сні", -1, 0.46),
    ]
    y0, rh, full = 122, 42, 300
    for i, (name, side, mag) in enumerate(axes):
        y = y0 + i * rh
        w = full * mag
        if side > 0:
            s += rect(cx, y, w, 24, _tint(GREEN), GREEN, 1.4, 4)
            s += text(cx + w + 8, y + 17, name, 11.5, INK, "start", "bold")
        else:
            s += rect(cx - w, y, w, 24, _tint(BLUE), BLUE, 1.4, 4)
            s += text(cx - w - 8, y + 17, name, 11.5, INK, "end", "bold")
    save("fig-20-6-2-axes.svg", s)


# ── Рис. 20.6.3 — коли що (дві колонки тригерів) ─────────────────────────────
def fig63_when_which():
    W, H = 920, 470
    s = header(W, H)
    s += text(W / 2, 32, "Коли ESP32, а коли простий 8-біт", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "часто задача чітко світиться однією з колонок", 12.5, GREY, "middle", style="italic")
    s += rect(40, 86, 400, 350, "#eef6ef", GREEN, 2, 12)
    s += text(240, 112, "→ тягне до ESP32", 14, GREEN, "middle", "bold")
    for i, t in enumerate(["потрібен бездротовий зв'язок (Wi-Fi/BT)",
                           "важкі обчислення (звук, сигнали, зображення)",
                           "багато пам'яті: буфери, вебсторінки",
                           "багато периферії або два потоки роботи"]):
        s += text(62, 156 + i * 62, "•", 13, GREEN, "start", "bold")
        s += text(80, 156 + i * 62, t, 11, INK, "start")
    s += rect(480, 86, 400, 350, "#eef3ff", BLUE, 2, 12)
    s += text(680, 112, "→ тягне до 8-біт", 14, BLUE, "middle", "bold")
    for i, t in enumerate(["копійки × мільйони штук — цент важить",
                           "роки від монетної батарейки",
                           "крихітний розмір, місце в обріз",
                           "гранична простота й надійність",
                           "радіо НЕ потрібне"]):
        s += text(502, 150 + i * 56, "•", 13, BLUE, "start", "bold")
        s += text(520, 150 + i * 56, t, 11, INK, "start")
    save("fig-20-6-3-when-which.svg", s)


# ── Рис. 20.6.4 — дерево рішень ──────────────────────────────────────────────
def fig64_decision_flow():
    W, H = 900, 500
    s = header(W, H)
    s += text(W / 2, 32, "Дерево рішень: ESP32 чи простий 8-біт", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "кілька питань по черзі — і вибір стає очевидним", 12.5, GREY, "middle", style="italic")

    def diamond(cx, cy, w, h, l1, l2):
        pts = f"{cx:.0f},{cy - h / 2:.0f} {cx + w / 2:.0f},{cy:.0f} {cx:.0f},{cy + h / 2:.0f} {cx - w / 2:.0f},{cy:.0f}"
        o = f'<polygon points="{pts}" fill="#fffaf0" stroke="{GOLD}" stroke-width="2"/>\n'
        o += text(cx, cy - 3, l1, 11, INK, "middle", "bold")
        o += text(cx, cy + 13, l2, 10.5, INK, "middle", "bold")
        return o

    s += diamond(300, 150, 270, 92, "Потрібен бездротовий", "зв'язок (Wi-Fi/BT)?")
    s += diamond(300, 290, 290, 92, "Важкі обчислення", "або багато пам'яті?")
    s += diamond(300, 422, 310, 100, "Ціна×масштаб, роки від", "батарейки, простота?")
    s += rect(620, 250, 230, 72, LGRN, GREEN, 2, 10)
    s += text(735, 282, "ESP32", 15, GREEN, "middle", "bold")
    s += text(735, 302, "(потужність потрібна)", 9.5, GREY, "middle")
    s += rect(620, 402, 230, 72, LBLUE, BLUE, 2, 10)
    s += text(735, 434, "Простий 8-біт", 14, BLUE, "middle", "bold")
    s += text(735, 454, "(ціна · простота · сон)", 9.5, GREY, "middle")
    s += arrow(300, 196, 300, 244, INK, 2)
    s += text(312, 224, "ні", 10, GREY, "start")
    s += arrow(436, 150, 620, 274, GREEN, 2.2)
    s += text(512, 196, "так", 10.5, GREEN, "start", "bold")
    s += arrow(300, 336, 300, 372, INK, 2)
    s += text(312, 358, "ні", 10, GREY, "start")
    s += arrow(446, 290, 620, 288, GREEN, 2.2)
    s += text(516, 274, "так", 10.5, GREEN, "start", "bold")
    s += arrow(456, 422, 620, 438, BLUE, 2.2)
    s += text(540, 416, "так", 10.5, BLUE, "start", "bold")
    save("fig-20-6-4-decision-flow.svg", s)


# ── Рис. 20.6.5 — ціна й споживання на масштабі ──────────────────────────────
def fig65_cost_power_scale():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 32, "Чому копійки й мікроампери вирішують на масштабі", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "дві осі, де переважує простий чіп, коли його досить", 12.5, GREY, "middle", style="italic")
    # ліворуч — ціна×масштаб
    s += rect(40, 88, 400, 320, "none", FAINT, 2, 12)
    s += text(240, 114, "Ціна × масштаб", 13, INK, "middle", "bold")
    s += text(150, 162, "8-біт  $0.40", 10.5, BLUE, "end", "bold")
    s += rect(160, 150, 32, 24, LBLUE, BLUE, 1.4, 4)
    s += text(150, 204, "ESP32  $2.50", 10.5, GREEN, "end", "bold")
    s += rect(160, 192, 200, 24, LGRN, GREEN, 1.4, 4)
    s += text(240, 252, "× 1 000 000 штук", 12.5, INK, "middle", "bold")
    s += rect(70, 280, 340, 56, "#fdeded", RED, 1.6, 8)
    s += text(240, 304, "різниця у ціні чипів:", 11, INK, "middle")
    s += text(240, 325, "≈ $2 100 000", 16, RED, "middle", "bold")
    # праворуч — життя від батарейки
    s += rect(460, 88, 400, 320, "none", FAINT, 2, 12)
    s += text(660, 114, "Життя від тієї самої батарейки", 12.5, INK, "middle", "bold")
    s += text(660, 136, "(коли радіо не потрібне)", 10, GREY, "middle")
    s += text(540, 192, "8-біт", 11, BLUE, "end", "bold")
    s += rect(550, 180, 260, 26, LBLUE, BLUE, 1.4, 4)
    s += text(680, 198, "роки (одиниці мкА уві сні)", 10.5, INK, "middle", "bold")
    s += text(540, 244, "ESP32", 11, GREEN, "end", "bold")
    s += rect(550, 232, 110, 26, LGRN, GREEN, 1.4, 4)
    s += text(605, 250, "менше", 10, INK, "middle", "bold")
    s += text(660, 312, "простіший чіп уві сні бере менше", 10.5, GREY, "middle")
    s += text(660, 330, "і має менше що живити", 10.5, GREY, "middle")
    save("fig-20-6-5-cost-power-scale.svg", s)


# ── Рис. 20.6.6 — два сценарії ───────────────────────────────────────────────
def fig66_scenarios():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "Два сценарії — дві протилежні правильні відповіді", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "правильний чіп визначає задача, а не амбіція", 12.5, GREY, "middle", style="italic")

    def card(x, title, sub):
        o = rect(x, 86, 400, 312, "none", FAINT, 2, 12)
        o += text(x + 200, 112, title, 13, INK, "middle", "bold")
        o += text(x + 200, 136, sub, 10.5, GREY, "middle")
        return o

    s += card(40, "A · метеостанція в інтернет", "вимога: Wi-Fi (зв'язок у мережу)")
    s += rect(70, 158, 150, 96, "#fbfdff", BLUE, 1.6, 8)
    s += text(145, 188, "8-біт", 13, BLUE, "middle", "bold")
    s += text(145, 212, "✗ радіо немає", 10.5, RED, "middle", "bold")
    s += text(145, 232, "задача неможлива", 9.5, GREY, "middle")
    s += rect(260, 158, 150, 96, "#fbfefb", GREEN, 1.6, 8)
    s += text(335, 188, "ESP32", 13, GREEN, "middle", "bold")
    s += text(335, 212, "✓ Wi-Fi на борту", 10.5, GREEN, "middle", "bold")
    s += text(335, 232, "єдиний вибір", 9.5, GREY, "middle")
    s += rect(70, 300, 340, 44, LGRN, GREEN, 1.4, 8)
    s += text(240, 327, "→ ESP32 (потужність потрібна)", 12, INK, "middle", "bold")

    s += card(480, "B · логер на батарейці ×1 млн", "2 роки автономності, без зв'язку")
    s += rect(510, 158, 150, 96, "#fbfefb", GREEN, 1.6, 8)
    s += text(585, 188, "ESP32", 13, GREEN, "middle", "bold")
    s += text(585, 212, "✗ +$2 млн", 10.5, RED, "middle", "bold")
    s += text(585, 232, "вище споживання", 9.5, GREY, "middle")
    s += rect(700, 158, 150, 96, "#fbfdff", BLUE, 1.6, 8)
    s += text(775, 188, "8-біт", 13, BLUE, "middle", "bold")
    s += text(775, 212, "✓ дешево, мкА", 10.5, BLUE, "middle", "bold")
    s += text(775, 232, "роки життя", 9.5, GREY, "middle")
    s += rect(510, 300, 340, 44, LBLUE, BLUE, 1.4, 8)
    s += text(680, 327, "→ простий 8-біт (дешевше, довше)", 12, INK, "middle", "bold")
    save("fig-20-6-6-scenarios.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §20.7 — Сімейство ESP32 (S2/S3/C3/C6): що обирати
# ─────────────────────────────────────────────────────────────────────────────

# ── Рис. 20.7.1 — родина ESP32 ───────────────────────────────────────────────
def fig71_family():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 34, "Не один чіп, а ціла родина ESP32", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "варіанти під різні потреби — фірмове Xtensa та новіші відкриті RISC-V", 12, GREY, "middle", style="italic")
    s += rect(370, 86, 200, 62, LBLUE, BLUE, 2, 10)
    s += text(470, 110, "ESP32 (2016)", 13.5, BLUE, "middle", "bold")
    s += text(470, 130, "оригінал · 2× Xtensa", 9.5, GREY, "middle")
    variants = [
        ("ESP32-S2", "1× Xtensa", "Wi-Fi, USB, без BT", LBLUE, BLUE, 60),
        ("ESP32-S3", "2× Xtensa", "Wi-Fi+BLE, AI", LBLUE, BLUE, 270),
        ("ESP32-C3", "1× RISC-V", "дешевий Wi-Fi+BLE", LGRN, GREEN, 480),
        ("ESP32-C6", "1× RISC-V", "Wi-Fi 6 + Thread", LGRN, GREEN, 700),
    ]
    vy = 252
    for nm, arch, role, fill, col, x in variants:
        s += line(470, 148, x + 85, vy - 6, GREY, 1.4)
        s += rect(x, vy, 180, 86, fill, col, 2, 10)
        s += text(x + 90, vy + 26, nm, 13, col, "middle", "bold")
        s += text(x + 90, vy + 46, arch, 10.5, INK, "middle", "bold")
        s += text(x + 90, vy + 64, role, 9.5, GREY, "middle")
    s += rect(300, 384, 20, 14, LBLUE, BLUE, 1.4)
    s += text(326, 396, "Xtensa (фірмове ядро)", 11, BLUE, "start", "bold")
    s += rect(560, 384, 20, 14, LGRN, GREEN, 1.4)
    s += text(586, 396, "RISC-V (відкрите ядро)", 11, GREEN, "start", "bold")
    save("fig-20-7-1-family.svg", s)


# ── Рис. 20.7.2 — осі відмінностей ───────────────────────────────────────────
def fig72_axes():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "По яких осях різняться члени родини", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "насправді їх лише кілька — є на що дивитися", 12.5, GREY, "middle", style="italic")
    axes = [
        ("Архітектура ядра", "Xtensa  ↔  RISC-V"),
        ("Кількість ядер", "одне  ↔  два"),
        ("Покоління Wi-Fi", "Wi-Fi 4  ↔  Wi-Fi 6"),
        ("Bluetooth", "немає  /  BLE  /  + класичний"),
        ("Вбудований USB", "немає  ↔  є"),
        ("Особливі здатності", "AI-прискорення (S3) · Thread/Matter (C6)"),
    ]
    y0 = 104
    for i, (name, spread) in enumerate(axes):
        y = y0 + i * 48
        s += text(60, y + 6, name, 12.5, INK, "start", "bold")
        s += rect(320, y - 16, 540, 36, "#fbfbfb", FAINT, 1.4, 8)
        s += text(590, y + 6, spread, 12, INK, "middle", "bold")
    s += rect(120, 392, 660, 30, LGRN, GREEN, 1.4, 8)
    s += text(450, 412, "Решта (пам'ять, число ніжок) — другорядні відмінності.", 12, INK, "middle", "bold")
    save("fig-20-7-2-axes.svg", s)


# ── Рис. 20.7.3 — Xtensa → RISC-V ────────────────────────────────────────────
def fig73_xtensa_riscv():
    W, H = 900, 410
    s = header(W, H)
    s += text(W / 2, 34, "Великий зсув: від фірмового Xtensa до відкритого RISC-V", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "новіші, дешевші члени родини йдуть відкритим шляхом", 12.5, GREY, "middle", style="italic")
    s += rect(60, 100, 320, 220, LBLUE, BLUE, 2, 12)
    s += text(220, 128, "Xtensa", 15, BLUE, "middle", "bold")
    s += text(220, 150, "ESP32 · S2 · S3", 12, INK, "middle", "bold")
    for i, t in enumerate(["фірмове, ліцензоване ядро", "перевірене, потужне", "оригінал і серія S"]):
        s += text(220, 184 + i * 28, "• " + t, 11, INK, "middle")
    s += arrow(395, 210, 500, 210, INK, 4)
    s += text(447, 194, "новіші,", 10.5, GREY, "middle", "bold")
    s += text(447, 226, "дешевші", 10.5, GREY, "middle", "bold")
    s += rect(515, 100, 325, 220, LGRN, GREEN, 2, 12)
    s += text(677, 128, "RISC-V", 15, GREEN, "middle", "bold")
    s += text(677, 150, "C3 · C6 · …", 12, INK, "middle", "bold")
    for i, t in enumerate(["відкритий стандарт — без ліцензій", "дешевше, сучасно, вільно", "майбутнє лінійки"]):
        s += text(677, 184 + i * 28, "• " + t, 11, INK, "middle")
    s += rect(120, 360, 660, 34, LAMB, GOLD, 1.4, 8)
    s += text(450, 382, "У коді різниця майже невидима — Arduino та ESP-IDF ховають ядро.", 12, INK, "middle", "bold")
    save("fig-20-7-3-xtensa-riscv.svg", s)


# ── Рис. 20.7.4 — зв'язок по членах родини ───────────────────────────────────
def fig74_connectivity():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "Хто що вміє по бездротовому зв'язку", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "найважливіша вісь вибору — який саме зв'язок потрібен", 12.5, GREY, "middle", style="italic")
    s += text(120, 108, "чіп", 11.5, INK, "middle", "bold")
    for name, x in [("Wi-Fi", 430), ("BT класич.", 560), ("BLE", 680), ("802.15.4", 812)]:
        s += text(x, 108, name, 11, INK, "middle", "bold")
    s += text(812, 124, "Thread/Matter", 8.5, GREY, "middle", style="italic")
    s += line(60, 134, 884, 134, FAINT, 1.4)
    members = [
        ("ESP32", "Wi-Fi 4", "✓", "✓", "—"),
        ("ESP32-S2", "Wi-Fi 4", "—", "—", "—"),
        ("ESP32-S3", "Wi-Fi 4", "—", "✓", "—"),
        ("ESP32-C3", "Wi-Fi 4", "—", "✓", "—"),
        ("ESP32-C6", "Wi-Fi 6", "—", "✓", "✓"),
    ]
    for i, (nm, wifi, btc, ble, t154) in enumerate(members):
        y = 162 + i * 52
        s += rect(60, y - 22, 824, 44, "#fcfcfc" if i % 2 == 0 else "#f4f7fb", FAINT, 1, 6)
        s += text(120, y + 4, nm, 11.5, INK, "middle", "bold")
        s += text(430, y + 4, wifi, 11, (GREEN if "6" in wifi else INK), "middle", "bold")
        for val, x in ((btc, 560), (ble, 680), (t154, 812)):
            s += text(x, y + 4, val, 13, (GREEN if val == "✓" else GREY), "middle", "bold")
    save("fig-20-7-4-connectivity.svg", s)


# ── Рис. 20.7.5 — порадник вибору ────────────────────────────────────────────
def fig75_chooser():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Що обирати: короткий порадник", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "щойно чесно сформулюєш потребу — вибір майже очевидний", 12.5, GREY, "middle", style="italic")
    needs = [
        ("найдешевший простий Wi-Fi + BLE", "ESP32-C3", GREEN),
        ("потужність + камера / звук / ML", "ESP32-S3", BLUE),
        ("USB + Wi-Fi, без Bluetooth, дешево", "ESP32-S2", BLUE),
        ("Matter / Thread / Zigbee (розумний дім)", "ESP32-C6", GREEN),
        ("загальне навчання, максимум прикладів", "ESP32 (оригінал)", BLUE),
    ]
    y0 = 100
    for i, (need, chip, col) in enumerate(needs):
        y = y0 + i * 66
        s += rect(46, y, 520, 50, "#fbfbfb", FAINT, 1.4, 8)
        s += text(66, y + 31, need, 12, INK, "start")
        s += arrow(576, y + 25, 640, y + 25, INK, 2.6)
        s += rect(650, y, 204, 50, _tint(col), col, 2, 8)
        s += text(752, y + 31, chip, 13, col, "middle", "bold")
    save("fig-20-7-5-chooser.svg", s)


# ── Рис. 20.7.6 — добір під проєкт ───────────────────────────────────────────
def fig76_picks():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 32, "Добір під проєкт: три приклади", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "кожен вибір диктує одна-дві ключові вимоги, а не «загальна крутість»", 12.5, GREY, "middle", style="italic")
    cards = [
        ("Розумна розетка", "масовий тираж · простий Wi-Fi", "ESP32-C3", "найдешевший · RISC-V", GREEN, 40),
        ("Камера з розпізнаванням", "RAM · два ядра · прискорення", "ESP32-S3", "AI-інструкції · багато RAM", BLUE, 327),
        ("Давач розумного дому", "Matter / Thread", "ESP32-C6", "802.15.4 + Wi-Fi 6", GREEN, 614),
    ]
    for title2, need, chip, why, col, x in cards:
        s += rect(x, 88, 270, 286, "none", FAINT, 2, 12)
        s += text(x + 135, 116, title2, 12.5, INK, "middle", "bold")
        s += text(x + 135, 140, need, 9.8, GREY, "middle")
        s += arrow(x + 135, 158, x + 135, 196, INK, 2.6)
        s += rect(x + 35, 202, 200, 62, _tint(col), col, 2, 10)
        s += text(x + 135, 232, chip, 14.5, col, "middle", "bold")
        s += text(x + 135, 252, "✓ підходить", 9.5, col, "middle", "bold")
        s += text(x + 135, 300, why, 10.5, INK, "middle", "bold")
        s += text(x + 135, 322, "ключова вимога вирішила", 9, GREY, "middle", style="italic")
    save("fig-20-7-6-picks.svg", s)


if __name__ == "__main__":
    # Історія до Розділу 20 — перший мікроконтролер
    fig_timeline()
    fig_calculator()
    fig_4004_set()
    fig_uc_vs_up()
    fig_lineages()
    fig_patents()
    # 📜 Історія до §20.5 — ESP8266 → ESP32
    fig5i1_timeline()
    fig5i2_price_shock()
    fig5i3_accidental_computer()
    fig5i4_community_unlock()
    fig5i5_esp8266_vs_esp32()
    # §20.1 Мікроконтролер: комп'ютер на одному чіпі
    fig11_what_is_mcu()
    fig12_mp_vs_mc_board()
    fig13_scale()
    fig14_boot()
    fig15_spectrum()
    fig16_budget()
    # §20.2 Складові МК: ядро, пам'ять, периферія
    fig21_block_diagram()
    fig22_core()
    fig23_memory()
    fig24_peripheral_catalog()
    fig25_offload()
    fig26_datasheet()
    # §20.3 Регістри периферії: memory-mapped IO
    fig31_address_map()
    fig32_register_bits()
    fig33_register_kinds()
    fig34_bit_ops()
    fig35_gpio_blink()
    fig36_register_map()
    # §20.4 Тактування й живлення
    fig41_clock_pulse()
    fig42_clock_sources()
    fig43_accuracy()
    fig44_clock_tree()
    fig45_sleep_modes()
    fig46_duty_cycle()
    # §20.5 Архітектура ESP32
    fig51_esp32_soc()
    fig52_two_cores()
    fig53_flash_cache()
    fig54_radio()
    fig55_peripherals_matrix()
    fig56_deep_sleep_ulp()
    fig57_spec()
    # §20.6 ESP32 проти простого 8-біт МК
    fig61_two_ends()
    fig62_axes()
    fig63_when_which()
    fig64_decision_flow()
    fig65_cost_power_scale()
    fig66_scenarios()
    # §20.7 Сімейство ESP32
    fig71_family()
    fig72_axes()
    fig73_xtensa_riscv()
    fig74_connectivity()
    fig75_chooser()
    fig76_picks()
    print("OK - figures for Section 20 (history + 20.1..20.7 — ПОВНИЙ розділ) generated in", OUT)
