# -*- coding: utf-8 -*-
"""
SVG-фігури для 🔌-вставки §3.9.4c — «Апаратний CRC: блок у МК (STM32-клас)
і CRC усередині SD- та CAN-контролерів».

ОКРЕМИЙ генератор лише цієї вставки (головний figs.py розділу не чіпаємо).
Чистий Python без залежностей. Вивід → ./img/.
Стиль за AUTHORING §9: білий фон; «1»/«+» червоний, «0»/«−» синій;
висновок/поле — зелене; стрілки через marker; шрифт sans-serif.
Нумерація підписів — §3.9.4c.k → файли fig-r09-s4c-k-*.

Фігури:
  fig-r09-s4c-1-block.svg   — блок CRC у МК: пишеш слова в регістр, читаєш остачу; бітовий цикл — у залізі
  fig-r09-s4c-2-inline.svg  — CRC «на дроті» в CAN- і SD-контролерах: лічить сам, повз процесор
  fig-r09-s4c-3-gotchas.svg — чому апаратний і програмний CRC не сходяться + коли брати блок
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
VIOL  = "#7a3ea8"
TEAL  = "#1f8a8a"
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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'  <marker id="aViol" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{VIOL}"/></marker>\n'
        f'  <marker id="aTeal" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{TEAL}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         GREY: "aGrey", AMBER: "aAmber", VIOL: "aViol", TEAL: "aTeal"}


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


def mono(x, y, s, size=13, color=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Consolas, \'Courier New\', monospace" '
            f'font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def path(d, color=INK, w=2.4, fill="none", dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w}"{da}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── Фігура 1: блок CRC у МК (STM32-клас) — пишеш слова, читаєш остачу ──────────
def fig1_block():
    W, H = 920, 600
    b = header(W, H)
    b += text(W/2, 30,
              "Апаратний CRC у мікроконтролері (STM32-клас): бітовий цикл §3.9.4 зашитий у залізо",
              16, INK, "middle", "bold")
    b += text(W/2, 50,
              "Процесор лише пише слова в регістр і читає готову остачу — усі такти зсуву й XOR блок робить сам",
              11.5, GREY, "middle", style="italic")

    # ── шина ──
    bus_y = 150
    b += line(60, bus_y, W - 60, bus_y, INK, 3)
    b += text(70, bus_y - 10, "внутрішня шина МК (AHB/APB)", 11, GREY, "start", "bold")

    # ── процесор зліва ──
    b += rect(70, 92, 150, 100, "#f4f7ff", BLUE, 2, 10)
    b += text(145, 116, "Ядро (CPU)", 13, BLUE, "middle", "bold")
    b += text(145, 138, "пише слово →", 10.5, INK, "middle")
    b += text(145, 154, "← читає остачу", 10.5, INK, "middle")
    b += text(145, 176, "звільнене для іншого", 9.5, GREEN, "middle", style="italic")
    b += arrow(145, 192, 145, bus_y - 2, BLUE, 2)

    # ── блок CRC праворуч від шини, нижче ──
    bx, by, bw, bh = 300, 210, 540, 270
    b += rect(bx, by, bw, bh, "#fffdf6", AMBER, 2.4, 12)
    b += text(bx + bw/2, by + 24, "Периферійний блок CRC", 14.5, AMBER, "middle", "bold")
    b += arrow(560, bus_y + 2, 560, by - 2, AMBER, 2)
    b += text(575, (bus_y + by)/2 + 4, "адресується як регістри", 10, GREY, "start")

    # вхідний регістр даних (32 біти)
    drx, dry = bx + 30, by + 50
    b += rect(drx, dry, 200, 54, "#fff", BLUE, 2, 8)
    b += text(drx + 100, dry + 20, "DR — регістр даних", 11.5, BLUE, "middle", "bold")
    b += mono(drx + 100, dry + 40, "CRC->DR = word;", 11, INK, "middle")
    b += text(drx + 100, dry + 70, "сюди процесор кладе", 9.5, GREY, "middle")
    b += text(drx + 100, dry + 84, "32-бітне слово (чи байт)", 9.5, GREY, "middle")

    # ядро: зсувний регістр з XOR-відводами
    sx, sy = bx + 30, by + 150
    b += rect(sx, sy, 200, 86, "#fdeeee", RED, 2, 8)
    b += text(sx + 100, sy + 20, "зсувний регістр + XOR", 11, RED, "middle", "bold")
    # маленькі комірки
    ncell = 8
    cw = 18
    cx0 = sx + 100 - ncell*cw/2
    for i in range(ncell):
        col = RED if i in (0, 5, 6) else GREY
        b += rect(cx0 + i*cw, sy + 30, cw - 3, 18, "#fff", col, 1.4, 2)
    b += text(sx + 100, sy + 64, "відводи = поліном (§3.9.4)", 9.5, INK, "middle")
    b += text(sx + 100, sy + 78, "за такт — один зсув і XOR", 9.5, INK, "middle")

    # стрілка від DR у ядро
    b += arrow(drx + 100, dry + 54, sx + 100, sy - 2, INK, 2.2)
    b += text(drx + 210, dry + 86, "8 чи 32 такти", 10, GREY, "start")
    b += text(drx + 210, dry + 100, "за одне записане слово", 10, GREY, "start")

    # вихідний регістр остачі
    orx, ory = bx + 320, by + 96
    b += rect(orx, ory, 190, 54, "#f0fff2", GREEN, 2, 8)
    b += text(orx + 95, ory + 20, "акумулятор остачі", 11.5, GREEN, "middle", "bold")
    b += mono(orx + 95, ory + 40, "crc = CRC->DR;", 11, INK, "middle")
    b += arrow(sx + 200, sy + 10, orx + 95, ory + 54, GREEN, 2.2)
    b += text(orx + 95, ory + 70, "тримає поточну остачу;", 9.5, GREY, "middle")
    b += text(orx + 95, ory + 84, "читання = готовий CRC", 9.5, GREY, "middle")

    # керування / параметри блока
    px, py = bx + 320, by + 175
    b += rect(px, py, 190, 70, "#fff", VIOL, 1.8, 8)
    b += text(px + 95, py + 18, "що фіксоване в залізі", 10.5, VIOL, "middle", "bold")
    b += text(px + 14, py + 36, "• поліном (часто 0x04C11DB7)", 9.5, INK, "start")
    b += text(px + 14, py + 50, "• init (часто 0xFFFFFFFF)", 9.5, INK, "start")
    b += text(px + 14, py + 64, "• деякі блоки — рефлексії, init настроювані", 9.0, GREY, "start")

    # підпис-висновок знизу
    b += rect(60, 506, W - 120, 66, "#f0fff2", GREEN, 1.8, 9)
    b += text(80, 530, "Суть:", 12.5, GREEN, "start", "bold")
    b += text(128, 530,
              "апаратний CRC — це той самий бітовий цикл §3.9.4a, але виконаний електронікою за частку такту на біт.",
              11, INK, "start")
    b += text(80, 552,
              "Процесор не крутить цикл — він лише годує блок словами й наприкінці читає остачу. Розвантажує ядро на великих блоках.",
              11, INK, "start")
    save("fig-r09-s4c-1-block.svg", b)


# ── Фігура 2: CRC «на дроті» в CAN- і SD-контролерах ──────────────────────────
def fig2_inline():
    W, H = 920, 620
    b = header(W, H)
    b += text(W/2, 30,
              "Інша оселя того ж CRC: усередині контролерів CAN і SD він живе прямо на лінії",
              16, INK, "middle", "bold")
    b += text(W/2, 50,
              "Тут CRC не «лічильна послуга» для процесора, а вартовий на дроті: рахується сам, на льоту, повз ядро",
              11.5, GREY, "middle", style="italic")

    # ── ВЕРХ: передавач ──
    b += text(70, 86, "Передавання кадру", 13, INK, "start", "bold")
    # потік байтів даних
    sx = 70
    sy = 100
    fields = [("ідентиф.", BLUE), ("дані", BLUE), ("дані", BLUE), ("дані", BLUE)]
    fw = 84
    for i, (lab, col) in enumerate(fields):
        x = sx + i*fw
        b += rect(x, sy, fw - 6, 40, "#f4f7ff", col, 1.8, 6)
        b += text(x + (fw-6)/2, sy + 24, lab, 11, col, "middle", "bold")
    # CRC-поле, що додає залізо
    cx = sx + 4*fw
    b += rect(cx, sy, fw - 6, 40, "#fdeeee", RED, 2.2, 6)
    b += text(cx + (fw-6)/2, sy + 18, "CRC", 11.5, RED, "middle", "bold")
    b += text(cx + (fw-6)/2, sy + 33, "(15 чи 16 біт)", 8.5, RED, "middle")
    b += text(cx + fw, sy + 24, "→ на шину", 10.5, GREY, "start")

    # генератор CRC під полем даних
    gx, gy = sx + 90, sy + 78
    b += rect(gx, gy, 230, 56, "#fffdf6", AMBER, 2, 9)
    b += text(gx + 115, gy + 22, "апаратний генератор CRC", 11, AMBER, "middle", "bold")
    b += text(gx + 115, gy + 42, "рахує остачу з усіх байтів кадру", 9.5, INK, "middle")
    # відводи з даних у генератор
    for i in range(3):
        b += arrow(sx + (i+1)*fw + 30, sy + 40, gx + 40 + i*60, gy - 2, GREY, 1.6)
    # генератор -> CRC-поле
    b += arrow(gx + 230, gy + 10, cx + (fw-6)/2, sy + 40, RED, 2.2)
    b += text(gx + 250, gy + 4, "сам дописує", 10, RED, "start", "bold")
    b += text(gx + 250, gy + 18, "у кінець кадру", 10, RED, "start")

    # ── СЕРЕД: лінія/шина ──
    midy = 250
    b += line(60, midy, W - 60, midy, INK, 3)
    b += text(W/2, midy - 8, "фізична лінія (CAN-шина / SPI до картки) — біти летять як є", 11, GREY, "middle", "bold")
    b += arrow(W/2 - 4, sy + 120, W/2 - 4, midy - 2, INK, 2)

    # ── НИЗ: приймач ──
    b += text(70, midy + 40, "Приймання кадру", 13, INK, "start", "bold")
    ry = midy + 54
    for i, (lab, col) in enumerate(fields):
        x = sx + i*fw
        b += rect(x, ry, fw - 6, 40, "#f4f7ff", col, 1.8, 6)
        b += text(x + (fw-6)/2, ry + 24, lab, 11, col, "middle", "bold")
    b += rect(cx, ry, fw - 6, 40, "#fdeeee", RED, 2.2, 6)
    b += text(cx + (fw-6)/2, ry + 24, "CRC", 11.5, RED, "middle", "bold")

    # приймальний генератор рахує свій CRC і звіряє
    gx2, gy2 = sx + 90, ry + 78
    b += rect(gx2, gy2, 230, 56, "#fffdf6", AMBER, 2, 9)
    b += text(gx2 + 115, gy2 + 22, "той самий генератор у приймачі", 10.5, AMBER, "middle", "bold")
    b += text(gx2 + 115, gy2 + 42, "рахує CRC заново з прийнятих байтів", 9.5, INK, "middle")
    for i in range(3):
        b += arrow(sx + (i+1)*fw + 30, ry + 40, gx2 + 40 + i*60, gy2 - 2, GREY, 1.6)

    # компаратор — праворуч, щоб обидва входи (свій CRC і CRC з кадру) читались окремо
    cmpx, cmpy = 600, gy2 - 2
    b += rect(cmpx, cmpy, 250, 60, "#f0fff2", GREEN, 2, 9)
    b += text(cmpx + 125, cmpy + 24, "звіряє: свій CRC = CRC з кадру?", 11, GREEN, "middle", "bold")
    b += text(cmpx + 125, cmpy + 44, "збіглися → кадр прийнято · ні → відкинуто", 9.5, RED, "middle", "bold")
    # свій (перерахований) CRC → компаратор
    b += arrow(gx2 + 230, gy2 + 24, cmpx - 2, cmpy + 22, GREEN, 2.2)
    b += text(gx2 + 248, gy2 + 18, "свій CRC", 9.5, GREEN, "start", "bold")
    # CRC, прийнятий у кадрі → компаратор
    b += arrow(cx + (fw - 6), ry + 24, cmpx + 60, cmpy - 2, RED, 1.8)
    b += text(cx + fw + 8, ry + 18, "CRC із кадру", 9.5, RED, "start")

    # ── підсумок-смуга ──
    by = 556
    b += rect(60, by, W - 120, 52, "#f4f7ff", BLUE, 1.8, 9)
    b += text(80, by + 22, "Ключова відмінність від блока в МК:", 12, BLUE, "start", "bold")
    b += text(80, by + 40,
              "тут CRC вбудований у протокол і працює автоматично — апаратура сама додає його при передачі й перевіряє при прийомі, ще до того, як байти дійдуть до вашого коду.",
              10.5, INK, "start")
    save("fig-r09-s4c-2-inline.svg", b)


# ── Фігура 3: чому апаратний і програмний CRC не сходяться + коли брати блок ───
def fig3_gotchas():
    W, H = 920, 600
    b = header(W, H)
    b += text(W/2, 30,
              "Граблі апаратного CRC: те саме число виходить лише за повного збігу всіх правил",
              16, INK, "middle", "bold")
    b += text(W/2, 50,
              "Поліном — лише одне з п'яти (§3.9.4a). Розбіжність у будь-якому пункті — і блок та бібліотека дають різні остачі",
              11.5, GREY, "middle", style="italic")

    # ── ліва колонка: чотири типові розбіжності ──
    items = [
        ("Порядок згодовування", RED,
         ["блок ковтає 32-бітні слова,", "бібліотека — окремі байти;", "при тому ж поліномі вийде", "інша остача, якщо не звести", "порядок байтів у слові"]),
        ("Рефлексії бітів", AMBER,
         ["частина блоків НЕ перевертає", "біти (refin/refout = ні), а", "ходові CRC-32 у софті —", "перевертають; це міняє все"]),
        ("init та xorout", VIOL,
         ["блок може стартувати з", "0xFFFFFFFF і не робити", "фінального XOR, або навпаки;", "звіряти обидва кінці"]),
        ("Поліном за замовчуванням", BLUE,
         ["у простих блоках поліном", "зашитий жорстко (часто", "0x04C11DB7) — не той, що", "у вашій бібліотеці CRC-16"]),
    ]
    ix, iy = 50, 84
    iw, ih = 410, 104
    for i, (title, col, lines) in enumerate(items):
        y = iy + i*(ih + 8)
        b += rect(ix, y, iw, ih, "#fcfcfc", col, 2, 9)
        b += rect(ix, y, 6, ih, col, col, 0, 0)
        b += text(ix + 18, y + 24, title, 12.5, col, "start", "bold")
        for k, ln in enumerate(lines):
            b += text(ix + 18, y + 44 + k*15, ln, 10.5, INK, "start")

    # ── права колонка зверху: симптом ──
    rx = 500
    b += rect(rx, 84, 370, 92, "#fff7ec", AMBER, 2, 9)
    b += text(rx + 185, 108, "Симптом, який усіх ловить", 12.5, AMBER, "middle", "bold")
    b += text(rx + 18, 130, "«CRC рахується і там, і там, обидва", 10.5, INK, "start")
    b += text(rx + 18, 146, "коди коректні — а числа різні».", 10.5, INK, "start")
    b += text(rx + 18, 164, "Причина майже завжди — один із пунктів зліва.", 10.5, GREY, "start")

    # ── права колонка: рецепт звірки (п'ятірка) ──
    b += rect(rx, 188, 370, 150, "#f0fff2", GREEN, 2, 9)
    b += text(rx + 185, 212, "Рецепт: звіряти всю п'ятірку", 12.5, GREEN, "middle", "bold")
    pent = [
        "1. поліном",
        "2. ширина (8 / 16 / 32 біти)",
        "3. init — чим заряджено регістр",
        "4. refin / refout — рефлексії",
        "5. xorout — фінальний XOR",
    ]
    for k, ln in enumerate(pent):
        b += text(rx + 24, 236 + k*19, ln, 11, INK, "start")
    b += text(rx + 185, 332, "збіглася п'ятірка → збіглися числа", 9.5, GREY, "middle", style="italic")

    # ── низ: коли брати апаратний блок (дерево рішень) ──
    b += line(50, 372, W - 50, 372, FAINT, 1.4)
    b += text(W/2, 396, "Коли вмикати апаратний блок, а коли лишитися на софті", 13.5, GREEN, "middle", "bold")
    dx = 70
    dy = 414
    rows = [
        ("Великі блоки даних (кілобайти): прошивка, лог, кадр", "→ блок МК: розвантажує ядро, рахує на льоту", GREEN),
        ("CRC уже робить периферія (CAN, SD-контролер)", "→ нічого не пишемо — він рахується сам (Рис. 3.9.4c.2)", BLUE),
        ("Треба формат чужого протоколу (Modbus, своя п'ятірка)", "→ часто легше софт: блок не завжди дає потрібні рефлексії", AMBER),
        ("Кілька байтів зрідка, блок зайнятий чи економимо код", "→ табличний софт (§3.9.4a) — простий і переносний", VIOL),
    ]
    for i, (cond, act, col) in enumerate(rows):
        y = dy + i*34
        b += circle(dx, y + 6, 5, col, col, 1)
        b += text(dx + 16, y + 10, cond, 11.5, INK, "start", "bold")
        b += arrow(dx + 430, y + 6, dx + 470, y + 6, col, 2)
        b += text(dx + 480, y + 10, act, 11, col, "start")

    b += line(50, H - 36, W - 50, H - 36, FAINT, 1.2)
    b += text(W/2, H - 16,
              "Апаратний CRC економить такти, але не звільняє від домовленості: остача однакова лише тоді, коли однакова вся п'ятірка параметрів.",
              11.5, GREEN, "middle", "bold")
    save("fig-r09-s4c-3-gotchas.svg", b)


if __name__ == "__main__":
    fig1_block()
    fig2_inline()
    fig3_gotchas()
    print("r09-s4-c-hardware-crc figures done.")
