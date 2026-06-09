# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 7 — «Конденсатор» (Модуль 2).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи нумеруються посекційно
(Рис. C.S.N) у тексті розділу; для історії до розділу — секція 0 (Рис. 7.0.N).

Скрипт нарощується по ітераціях: кожна тема додає свої функції-фігури.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра ─────────────────────────────────────────────────────────────────
RED   = "#c0271e"   # додатний (+)
BLUE  = "#1f47b5"   # від'ємний (−)
GREEN = "#1f8a3b"   # поле
INK   = "#1b1b1b"   # основний текст/лінії
GREY  = "#8a8a8a"   # допоміжне
FAINT = "#e4e4e4"   # дуже бліде тло
AMBER = "#caa24a"   # бурштин
GLASS = "#a9c8dd"   # скло
SILK  = "#d8b24a"   # шовк
HEMP  = "#b08a5a"   # конопляна нитка
METAL = "#9a9aa0"   # метал/фольга
SKIN  = "#e7c4a0"   # шкіра (рука)
LRED  = "#fbecec"   # бліде червоне тло
LBLUE = "#e9eefb"   # бліде синє тло
LGRN  = "#eef6ef"   # бліде зелене тло
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


def plus(cx, cy, r=12, color=RED, w=2.5):
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w)
            + line(cx, cy - r * 0.55, cx, cy + r * 0.55, color, w))


def minus(cx, cy, r=12, color=BLUE, w=2.5):
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w))


def ground(cx, y, color=INK):
    """Стандартний символ землі під точкою (cx, y)."""
    s = line(cx, y, cx, y + 12, color, 2)
    s += line(cx - 16, y + 12, cx + 16, y + 12, color, 2.4)
    s += line(cx - 10, y + 18, cx + 10, y + 18, color, 2.4)
    s += line(cx - 5, y + 24, cx + 5, y + 24, color, 2.4)
    return s


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ─────────────────────────────────────────────────────────────────────────────
#  Спільний будівельник: лейденська банка в розрізі
# ─────────────────────────────────────────────────────────────────────────────
def jar_glass(cx, top, w, h, wall=11):
    """U-подібне скло (стінки + дно). Повертає (svg, bounds=(L,R,top,B))."""
    L, R, B = cx - w / 2, cx + w / 2, top + h
    s = rect(L, top, wall, h, GLASS, "#7fa6bf", 1.2)        # ліва стінка
    s += rect(R - wall, top, wall, h, GLASS, "#7fa6bf", 1.2)  # права стінка
    s += rect(L, B - wall, w, wall, GLASS, "#7fa6bf", 1.2)    # дно
    return s, (L, R, top, B)


def jar_coatings(bounds, wall=11, t=7, inner=("+", RED, LRED),
                 outer=("-", BLUE, LBLUE), outer_top_frac=0.32, signs=True):
    """Внутрішня та зовнішня обкладки на склі банки."""
    L, R, top, B = bounds
    s = ""
    isgn, icol, ifill = inner
    osgn, ocol, ofill = outer
    # внутрішня обкладка (на внутрішній поверхні скла)
    s += rect(L + wall, top, t, B - wall - top, ifill, icol, 1.4)
    s += rect(R - wall - t, top, t, B - wall - top, ifill, icol, 1.4)
    s += rect(L + wall, B - wall - t, R - L - 2 * wall, t, ifill, icol, 1.4)
    # зовнішня обкладка (на зовнішній поверхні, від частини висоти вниз)
    oy = top + (B - top) * outer_top_frac - top * 0  # верх зовнішньої обкладки
    oy = top + (B - top - 0) * outer_top_frac
    s += rect(L - t, oy, t, B - oy + t, ofill, ocol, 1.4)
    s += rect(R, oy, t, B - oy + t, ofill, ocol, 1.4)
    s += rect(L - t, B, R - L + 2 * t, t, ofill, ocol, 1.4)
    if signs:
        ys = [top + 40 + i * (B - wall - top - 50) / 3 for i in range(4)]
        for y in ys:
            sgn = plus if isgn == "+" else minus
            s += sgn(L + wall + t / 2 + 1, y, 6, icol, 1.8)
            s += sgn(R - wall - t / 2 - 1, y, 6, icol, 1.8)
        for y in ys[1:]:
            sgn = plus if osgn == "+" else minus
            s += sgn(L - t / 2, y, 6, ocol, 1.8)
            s += sgn(R + t / 2, y, 6, ocol, 1.8)
    return s


def jar_rod(cx, top, B, wall=11, ball=True):
    """Латунний стрижень з кулькою та ланцюжком до внутрішньої обкладки."""
    cork_y = top - 14
    s = rect(cx - 26, cork_y, 52, 16, "#caa46e", "#9c7b46", 1.4, 3)  # корок
    s += line(cx, cork_y - 40, cx, B - wall - 8, METAL, 3)            # стрижень
    if ball:
        s += circle(cx, cork_y - 46, 9, METAL, "#6f6f74", 1.6)       # кулька-клема
    # ланцюжок (пунктир) до дна-обкладки
    s += line(cx, B - wall - 8, cx, B - wall - 6, METAL, 2)
    return s


# ── Рис. 7.0.1 — вертикальний таймлайн «ланцюг питань» ───────────────────────
def fig_timeline():
    W, H = 860, 640
    s = header(W, H)
    s += text(W / 2, 38, "Ланцюг питань: як навчилися запасати електрику", 21, INK, "middle", "bold")
    s += text(W / 2, 60, "кожен крок — нове питання, що штовхало далі (сірим — те, що стане змістом Розділу 7)",
              12.5, GREY, "middle", style="italic")
    spine = 196
    top, bot = 96, H - 30
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("до 1745", "Машини тертя", "Заряд є — та миттєво розлітається. Чи можна його ЗАПАСТИ?", False, False),
        ("1745", "фон Кляйст / von Kleist", "Банка з цвяхом у руці б'є струмом — але рецепт неясний, ніхто не повторить", False, False),
        ("1746", "Мушенбрук, Кунеус / Leiden", "Удар, що звалив професора. «Не повторив би й за королівство Франції»", False, False),
        ("1746", "Нолле / Nollet", "Назва «лейденська банка»; розряд крізь ~200 ченців — а як ШВИДКО біжить?", False, False),
        ("1747–48", "Франклін / Franklin", "Де сидить заряд? — НЕ у воді, а на СКЛІ; + і − рівні; «батарея» банок", False, True),
        ("Розділ 7", "Конденсатор", "Скільки заряду й від чого це залежить? — ЄМНІСТЬ", True, False),
    ]
    n = len(nodes)
    for i, (yr, who, q, dest, accent) in enumerate(nodes):
        y = top + 30 + (bot - top - 60) * i / (n - 1)
        col = GREY if dest else INK
        if accent:
            s += circle(spine, y, 10, "#fff", RED, 3)
            s += circle(spine, y, 4.5, RED, RED, 0)
        elif dest:
            s += rect(spine - 8, y - 8, 16, 16, "#fff", GREEN, 2.6, 3)
        else:
            s += circle(spine, y, 7, "#fff", col, 2.6)
        s += text(spine - 22, y + 5, yr, 12.5, (GREEN if dest else GREY), "end", "bold")
        s += text(spine + 26, y - 3, who, 15.5,
                  (RED if accent else (GREEN if dest else col)), "start", "bold")
        s += text(spine + 26, y + 17, q, 12.5, (INK if not dest else GREY), "start", style="italic")
    save("fig-7-0-1-timeline.svg", s)


# ── Рис. 7.0.2 — будова лейденської банки в розрізі ──────────────────────────
def fig_jar():
    W, H = 760, 560
    s = header(W, H)
    s += text(W / 2, 36, "Лейденська банка в розрізі: дві обкладки й скло між ними", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "заряд тримається не «в банці», а розділений по два боки тонкого скла",
              12.5, GREY, "middle", style="italic")

    cx, top, w, h, wall = 360, 170, 150, 280, 11
    body, b = jar_glass(cx, top, w, h, wall)
    L, R, t0, B = b
    s += jar_coatings(b, wall=wall, t=8, outer_top_frac=0.30)
    s += body
    s += jar_rod(cx, top, B, wall)

    # поле крізь скло (зелені стрілки + → −)
    for k in range(3):
        yk = top + 70 + k * 70
        s += arrow(L + wall - 1, yk, L - 9, yk, GREEN, 2)          # ліва стінка: всередину→назовні
        s += arrow(R - wall + 1, yk, R + 9, yk, GREEN, 2)          # права стінка
    s += text(cx, top + 150, "поле крізь скло", 12, GREEN, "middle", "bold")
    s += text(cx, top + 168, "(+ тягне −)", 11.5, GREEN, "middle", style="italic")

    # виноски
    def lead(x1, y1, x2, y2):
        return line(x1, y1, x2, y2, GREY, 1.4)

    s += lead(cx + 9, top - 60, cx + 150, top - 60)
    s += text(cx + 156, top - 56, "латунний стрижень-клема", 13, INK, "start")
    s += lead(cx + 26, top - 6, cx + 150, top - 18)
    s += text(cx + 156, top - 14, "корок", 13, INK, "start")
    s += lead(R - wall - 8, top + 40, R + 120, top + 30)
    s += text(R + 126, top + 34, "внутрішня обкладка (+)", 13, RED, "start", "bold")
    s += text(R + 126, top + 51, "фольга або вода", 11.5, GREY, "start", style="italic")
    s += lead(R + 7, B - 60, R + 120, B - 70)
    s += text(R + 126, B - 66, "зовнішня обкладка (−)", 13, BLUE, "start", "bold")
    s += text(R + 126, B - 49, "часто — рука й тіло", 11.5, GREY, "start", style="italic")
    s += lead(L - 4, top + 200, L - 120, top + 210)
    s += text(L - 126, top + 214, "скло —", 13, INK, "end", "bold")
    s += text(L - 126, top + 231, "діелектрик", 12.5, INK, "end")

    s += rect(60, H - 58, W - 120, 40, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 33, "Конденсатор у зародку: два провідники, розділені тонким ізолятором.",
              13.5, INK, "middle", "bold")
    save("fig-7-0-2-jar.svg", s)


# ── Рис. 7.0.3 — чому банку треба тримати в руці ─────────────────────────────
def fig_hand():
    W, H = 860, 520
    s = header(W, H)
    s += text(W / 2, 36, "Чому банка «бере» заряд лише з другою обкладкою", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "зовнішній стороні скла потрібен протилежний заряд — інакше накопичується мізер",
              12.5, GREY, "middle", style="italic")

    def mini_jar(cx, top, outer_on):
        w, h, wall = 96, 170, 9
        body, b = jar_glass(cx, top, w, h, wall)
        L, R, t0, B = b
        out = ""
        ocol = BLUE if outer_on else GREY
        ofill = LBLUE if outer_on else "#f0f0f0"
        osgn = "-" if outer_on else None
        out += jar_coatings(b, wall=wall, t=6,
                            outer=(osgn or "-", ocol, ofill),
                            outer_top_frac=0.34, signs=False)
        out += body
        out += jar_rod(cx, top, B, wall)
        # внутрішні + завжди
        for k in range(3):
            yk = top + 34 + k * 42
            out += plus(L + wall + 4, yk, 6, RED, 1.8)
            out += plus(R - wall - 4, yk, 6, RED, 1.8)
        # зовнішні − лише якщо outer_on
        if outer_on:
            for k in range(3):
                yk = top + 60 + k * 42
                out += minus(L - 3, yk, 6, BLUE, 1.8)
                out += minus(R + 3, yk, 6, BLUE, 1.8)
        return out, b

    # ─ ліва панель: на ізоляторі ─
    s += rect(40, 92, 360, 400, "none", FAINT, 2, 14)
    s += text(220, 118, "на ізоляційній підставці", 15, INK, "middle", "bold")
    cxl, topl = 200, 150
    mj, bl = mini_jar(cxl, topl, outer_on=False)
    s += mj
    Ll, Rl, t0l, Bl = bl
    # підставка-ізолятор
    s += rect(cxl - 70, Bl + 14, 140, 22, "#efe2c6", "#b79a5e", 1.6, 4)
    s += text(cxl, Bl + 30, "ізолятор (віск/скло)", 11, "#9c7b46", "middle", style="italic")
    # провід від машини до клеми
    s += arrow(cxl - 120, topl - 60, cxl - 12, topl - 60, INK, 2)
    s += text(cxl - 124, topl - 64, "від машини", 11.5, INK, "end")
    s += text(220, 470, "зовнішній стороні нема куди «спертися»", 12.5, GREY, "middle", style="italic")
    s += text(220, 487, "→ заряду майже не береться", 13, INK, "middle", "bold")

    # ─ права панель: у руці ─
    s += rect(458, 92, 360, 400, "none", FAINT, 2, 14)
    s += text(638, 118, "у голій руці", 15, INK, "middle", "bold")
    cxr, topr = 600, 150
    mj2, br = mini_jar(cxr, topr, outer_on=True)
    s += mj2
    Lr, Rr, t0r, Br = br
    # рука, що тримає нижню частину
    s += rect(Lr - 30, Br - 70, 22, 96, SKIN, "#c79a72", 1.6, 8)       # передпліччя ліворуч від банки
    for fi in range(4):                                                # пальці поверх банки
        fy = Br - 58 + fi * 20
        s += rect(Lr - 12, fy, 30, 12, SKIN, "#c79a72", 1.4, 5)
    # шлях заряду через тіло до землі
    s += arrow(Lr - 19, Br + 30, Lr - 19, Br + 70, BLUE, 2.4)
    s += text(Lr - 24, Br + 55, "крізь тіло", 11.5, BLUE, "end")
    s += ground(Lr - 19, Br + 70, BLUE)
    # іскра з клеми
    s += line(cxr, topr - 60, cxr + 22, topr - 78, RED, 2.2)
    s += line(cxr + 22, topr - 78, cxr + 10, topr - 70, RED, 2.2)
    s += line(cxr + 10, topr - 70, cxr + 34, topr - 92, RED, 2.2)
    s += text(cxr + 40, topr - 86, "розряд", 11.5, RED, "start", "bold")
    s += text(638, 470, "тіло стає зовнішньою обкладкою і шляхом до землі", 12.5, GREY, "middle", style="italic")
    s += text(638, 487, "→ заряду в рази більше, аж до удару", 13, INK, "middle", "bold")
    save("fig-7-0-3-hand.svg", s)


# ── Рис. 7.0.4 — розряд крізь вервечку людей як одне коло ─────────────────────
def fig_chain():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 36, "Демонстрація Нолле: розряд крізь вервечку — одне замкнене коло", 19, INK, "middle", "bold")
    s += text(W / 2, 58, "усі смикаються РАЗОМ — перший грубий доказ, що електрика біжить майже миттєво",
              12.5, GREY, "middle", style="italic")

    # банка ліворуч
    jx, jtop, jw, jh, jwall = 120, 150, 78, 130, 8
    body, b = jar_glass(jx, jtop, jw, jh, jwall)
    L, R, t0, B = b
    s += jar_coatings(b, wall=jwall, t=6, outer_top_frac=0.32, signs=False)
    s += body
    s += jar_rod(jx, jtop, B, jwall)
    s += plus(L + jwall + 4, jtop + 50, 6, RED, 1.8)
    s += plus(R - jwall - 4, jtop + 50, 6, RED, 1.8)
    s += minus(L - 3, jtop + 70, 6, BLUE, 1.8)
    s += minus(R + 3, jtop + 70, 6, BLUE, 1.8)
    s += text(jx, B + 30, "лейденська банка", 12.5, INK, "middle", "bold")

    # вервечка людей
    people_x = [300, 410, 520, 630, 740]
    sh_y = 210            # рівень плечей (де тримаються за руки/дроти)
    gnd_y = 320
    for px in people_x:
        head_cy = 168
        s += circle(px, head_cy, 11, "#fff", INK, 2)        # голова
        s += line(px, head_cy + 11, px, sh_y + 26, INK, 2)  # тулуб
        s += line(px, sh_y + 26, px - 12, gnd_y, INK, 2)    # ноги
        s += line(px, sh_y + 26, px + 12, gnd_y, INK, 2)
        s += line(px, sh_y, px - 18, sh_y + 4, INK, 2)      # руки до лінії з'єднання
        s += line(px, sh_y, px + 18, sh_y + 4, INK, 2)
    s += text(people_x[2], 150, "≈ 200 людей, з'єднаних дротами", 12.5, INK, "middle", style="italic")

    # верхній провід: клема банки → перша людина → ... → остання
    s += line(jx, jtop - 60, jx, sh_y, RED, 2.4)
    s += line(jx, sh_y, people_x[0] - 18, sh_y + 4, RED, 2.4)
    for i in range(len(people_x) - 1):
        s += line(people_x[i] + 18, sh_y + 4, people_x[i + 1] - 18, sh_y + 4, RED, 2.4, dash="2,5")
    # струм по верхній лінії
    s += arrow((jx + people_x[0]) / 2 - 10, sh_y - 2, (jx + people_x[0]) / 2 + 30, sh_y, RED, 2.2)
    s += arrow(people_x[1] + 6, sh_y + 3, people_x[1] + 44, sh_y + 4, RED, 2.2)
    s += text(people_x[2], sh_y - 12, "умовний струм I →", 12.5, RED, "middle", "bold")

    # зворотний провід низом: остання людина → зовнішня обкладка банки
    ret_y = gnd_y + 50
    s += line(people_x[-1], gnd_y, people_x[-1], ret_y, BLUE, 2.4)
    s += line(people_x[-1], ret_y, R + 3, ret_y, BLUE, 2.4)
    s += line(R + 3, ret_y, R + 3, B + 8, BLUE, 2.4)
    s += arrow((R + people_x[-1]) / 2 + 30, ret_y, (R + people_x[-1]) / 2 - 20, ret_y, BLUE, 2.2)
    s += text((R + people_x[-1]) / 2 + 6, ret_y - 8, "зворотний провід (замикає коло)", 12, BLUE, "middle", style="italic")

    s += rect(60, H - 44, W - 120, 30, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 24, "Струму потрібна петля — той самий принцип замкненого кола, що й у Розділі 2.",
              13, INK, "middle", "bold")
    save("fig-7-0-4-chain.svg", s)


# ── Рис. 7.0.5 — дослід Франкліна: заряд лишається на склі ───────────────────
def fig_glass():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Дослід Франкліна: заряд тримається на склі, а не на металі", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "розбірна банка — метал виймається майже порожнім, та зібрана знову вона б'є повним розрядом",
              12, GREY, "middle", style="italic")

    def panel(x0, title):
        out = rect(x0, 78, 268, 330, "none", FAINT, 2, 14)
        out += text(x0 + 134, 102, title, 14.5, INK, "middle", "bold")
        return out

    # (1) заряджаємо — зібрана банка
    s += panel(24, "1. Заряджаємо")
    cx1, top1 = 158, 150
    w1, h1, wl1 = 86, 150, 9
    body1, b1 = jar_glass(cx1, top1, w1, h1, wl1)
    L1, R1, _, B1 = b1
    # внутрішній метал-стакан
    s += rect(L1 + wl1 + 6, top1 + 6, R1 - L1 - 2 * wl1 - 12, h1 - wl1 - 12, "#dadade", METAL, 1.4, 3)
    s += jar_coatings(b1, wall=wl1, t=6, outer_top_frac=0.30)
    s += body1
    s += jar_rod(cx1, top1, B1, wl1)
    s += text(cx1, B1 + 28, "+ на внутр. боці скла,", 11.5, RED, "middle")
    s += text(cx1, B1 + 44, "− на зовнішньому (порівну)", 11.5, BLUE, "middle")

    # (2) розбираємо — три частини
    s += panel(316, "2. Розбираємо")
    bx = 316
    # внутрішній метал (порожній)
    s += rect(bx + 24, 150, 40, 120, "#dadade", METAL, 1.6, 4)
    s += text(bx + 44, 286, "метал", 11.5, INK, "middle")
    s += text(bx + 44, 302, "≈ порожній", 11, GREY, "middle", style="italic")
    s += text(bx + 44, 200, "0", 16, GREY, "middle", "bold")
    # скло (тримає заряд)
    gx = bx + 118
    s += rect(gx - 14, 150, 28, 120, GLASS, "#7fa6bf", 1.4, 4)
    for k in range(3):
        yk = 176 + k * 36
        s += plus(gx - 7, yk, 6, RED, 1.8)
        s += minus(gx + 7, yk, 6, BLUE, 1.8)
    s += text(gx, 286, "СКЛО", 12, INK, "middle", "bold")
    s += text(gx, 302, "тримає заряд", 11, INK, "middle", style="italic")
    # зовнішній метал (порожній)
    s += rect(bx + 190, 150, 40, 120, "#dadade", METAL, 1.6, 4)
    s += text(bx + 210, 286, "метал", 11.5, INK, "middle")
    s += text(bx + 210, 302, "≈ порожній", 11, GREY, "middle", style="italic")
    s += text(bx + 210, 200, "0", 16, GREY, "middle", "bold")

    # (3) складаємо знову — розряд
    s += panel(608, "3. Складаємо знову")
    cx3, top3 = 742, 150
    body3, b3 = jar_glass(cx3, top3, w1, h1, wl1)
    L3, R3, _, B3 = b3
    s += rect(L3 + wl1 + 6, top3 + 6, R3 - L3 - 2 * wl1 - 12, h1 - wl1 - 12, "#dadade", METAL, 1.4, 3)
    s += jar_coatings(b3, wall=wl1, t=6, outer_top_frac=0.30)
    s += body3
    s += jar_rod(cx3, top3, B3, wl1)
    # іскра
    s += line(cx3, top3 - 60, cx3 + 20, top3 - 80, RED, 2.4)
    s += line(cx3 + 20, top3 - 80, cx3 + 8, top3 - 72, RED, 2.4)
    s += line(cx3 + 8, top3 - 72, cx3 + 30, top3 - 94, RED, 2.4)
    s += text(cx3, B3 + 28, "б'є повним", 12.5, RED, "middle", "bold")
    s += text(cx3, B3 + 44, "розрядом!", 12.5, RED, "middle", "bold")
    s += text(cx3, top3 - 100, "навіть із новим металом", 11, GREY, "middle", style="italic")

    s += rect(60, H - 44, W - 120, 30, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 24, "Накопичує заряд сам ізолятор (діелектрик) — це ключ до всього Розділу 7.",
              13, INK, "middle", "bold")
    save("fig-7-0-5-glass.svg", s)


# ── Рис. 7.0.6 — батарея банок і пласка пластина ─────────────────────────────
def fig_battery():
    W, H = 880, 460
    s = header(W, H)
    s += text(W / 2, 34, "Дві ідеї Франкліна: «батарея» банок і пласка пластина", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "форма посудини виявилась зайвою — суть лише у двох обкладках і тонкому ізоляторі",
              12.5, GREY, "middle", style="italic")

    # ─ ліва панель: батарея банок ─
    s += rect(28, 78, 420, 350, "none", FAINT, 2, 14)
    s += text(238, 102, "«електрична батарея» — банки разом", 14.5, INK, "middle", "bold")
    xs = [110, 190, 270, 350]
    top, w, h, wl = 168, 56, 120, 7
    bus_top = top - 58
    bus_bot = top + h + 22
    for jx in xs:
        body, b = jar_glass(jx, top, w, h, wl)
        L, R, _, B = b
        s += jar_coatings(b, wall=wl, t=5, outer_top_frac=0.30, signs=False)
        s += body
        # стрижень до верхньої шини
        s += line(jx, bus_top, jx, B - wl - 6, METAL, 2.4)
        s += circle(jx, bus_top, 4, METAL, "#6f6f74", 1.2)
        # зовнішня обкладка до нижньої шини
        s += line(R + 5, B, R + 5, bus_bot, BLUE, 2)
        s += plus(L + wl + 3, top + 40, 5, RED, 1.6)
        s += minus(R + 2.5, top + 60, 5, BLUE, 1.6)
    # шини
    s += line(xs[0], bus_top, xs[-1], bus_top, RED, 3)
    s += line(xs[0] + 56 / 2 + 5, bus_bot, xs[-1] + 56 / 2 + 5, bus_bot, BLUE, 3)
    s += text(xs[0] - 10, bus_top - 8, "спільний +", 12, RED, "start", "bold")
    s += text(xs[-1] + 14, bus_bot + 16, "спільний −", 12, BLUE, "start", "bold")
    s += text(238, 410, "більше банок → більший сумарний запас заряду", 12.5, INK, "middle", style="italic")
    s += text(238, 78 + 350 - 6, "", 1, INK, "middle")

    # ─ права панель: пласка пластина ─
    s += rect(470, 78, 386, 350, "none", FAINT, 2, 14)
    s += text(663, 102, "пласка пластина (перший плаский конденсатор)", 13.5, INK, "middle", "bold")
    # скло (вид збоку — тонка пластина), фольга з обох боків зі зсувом
    gx, gy, gw, gh = 620, 160, 26, 180
    s += rect(gx - 60, gy, 60, gh, LRED, RED, 1.6)         # передня фольга (+)
    s += rect(gx, gy, gw, gh, GLASS, "#7fa6bf", 1.4)        # скло
    s += rect(gx + gw, gy, 60, gh, LBLUE, BLUE, 1.6)        # задня фольга (−)
    for k in range(4):
        yk = gy + 26 + k * 44
        s += plus(gx - 30, yk, 7, RED, 1.8)
        s += minus(gx + gw + 30, yk, 7, BLUE, 1.8)
    # поле крізь скло
    for k in range(3):
        yk = gy + 40 + k * 52
        s += arrow(gx + 2, yk, gx + gw - 2, yk, GREEN, 2)
    s += text(gx - 30, gy - 8, "фольга +", 12, RED, "middle", "bold")
    s += text(gx + gw + 30, gy - 8, "фольга −", 12, BLUE, "middle", "bold")
    s += text(gx + gw / 2, gy + gh + 20, "скло", 12, INK, "middle", "bold")
    s += text(gx + gw / 2, gy + gh + 36, "(діелектрик)", 11, GREY, "middle", style="italic")
    # виводи
    s += line(gx - 30, gy, gx - 30, gy - 26, RED, 2.4)
    s += line(gx + gw + 30, gy, gx + gw + 30, gy - 26, BLUE, 2.4)
    s += text(663, 410, "та сама фізика — без зайвої банки", 12.5, INK, "middle", style="italic")
    save("fig-7-0-6-battery.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §7.1 — спільні будівельники конденсатора
# ─────────────────────────────────────────────────────────────────────────────
def dim_h(x1, x2, y, label, color=GREY):
    s = arrow((x1 + x2) / 2, y, x1, y, color, 1.5)
    s += arrow((x1 + x2) / 2, y, x2, y, color, 1.5)
    s += text((x1 + x2) / 2, y - 6, label, 12, color, "middle", "bold")
    return s


def dim_v(x, y1, y2, label, color=GREY):
    s = arrow(x, (y1 + y2) / 2, x, y1, color, 1.5)
    s += arrow(x, (y1 + y2) / 2, x, y2, color, 1.5)
    s += text(x + 7, (y1 + y2) / 2 + 4, label, 12, color, "start", "bold")
    return s


def cap_plates(cx, cy, ph=150, gap=90, pt=12,
               lfill="#d9d9dd", lstroke=METAL,
               rfill="#d9d9dd", rstroke=METAL, leads=True, lead=46):
    """Вертикальні обкладки плаского конденсатора з виводами."""
    li, ri = cx - gap / 2, cx + gap / 2
    lo, ro = li - pt, ri + pt
    s = rect(lo, cy - ph / 2, pt, ph, lfill, lstroke, 1.6)
    s += rect(ri, cy - ph / 2, pt, ph, rfill, rstroke, 1.6)
    if leads:
        s += line(lo, cy, lo - lead, cy, INK, 2.4)
        s += line(ro, cy, ro + lead, cy, INK, 2.4)
    return s, dict(li=li, ri=ri, lo=lo, ro=ro, ll=lo - lead, rl=ro + lead, ph=ph, cy=cy)


def cap_h(cx, cy, pw=86, gap=22, pt=9, top=("#f7dada", RED), bot=("#dbe3f7", BLUE), lead=28):
    """Горизонтальні обкладки (для схем-петель): виводи вгору й вниз."""
    tf, ts = top
    bf, bs = bot
    ty = cy - gap / 2 - pt
    by = cy + gap / 2
    s = rect(cx - pw / 2, ty, pw, pt, tf, ts, 1.8)
    s += rect(cx - pw / 2, by, pw, pt, bf, bs, 1.8)
    s += line(cx, ty, cx, ty - lead, INK, 2.4)
    s += line(cx, by + pt, cx, by + pt + lead, INK, 2.4)
    return s, (cx, ty - lead), (cx, by + pt + lead)


def battery(cx, cy):
    """Вертикальний символ батареї: + угорі, − унизу. Повертає (svg, top, bottom)."""
    s = line(cx, cy - 32, cx, cy - 9, INK, 2.4)
    s += line(cx - 17, cy - 9, cx + 17, cy - 9, INK, 2.6)   # довга риска (+)
    s += line(cx - 9, cy + 2, cx + 9, cy + 2, INK, 5)       # коротка товста (−)
    s += line(cx, cy + 2, cx, cy + 32, INK, 2.4)
    s += plus(cx + 28, cy - 9, 7, RED, 1.8)
    s += minus(cx + 26, cy + 2, 7, BLUE, 1.8)
    return s, (cx, cy - 32), (cx, cy + 32)


def source_ac(cx, cy, r=24):
    """Джерело змінної напруги: коло із синусоїдою. Повертає (svg, top, bottom)."""
    s = circle(cx, cy, r, "#fff", INK, 2)
    pts = []
    for i in range(0, 41):
        t = i / 40
        x = cx - r * 0.72 + 1.44 * r * t
        y = cy - 0.52 * r * math.sin(2 * math.pi * t * 1.5)
        pts.append((x, y))
    path = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    s += f'<path d="{path}" fill="none" stroke="{INK}" stroke-width="2"/>\n'
    s += line(cx, cy - r, cx, cy - r - 18, INK, 2.4)
    s += line(cx, cy + r, cx, cy + r + 18, INK, 2.4)
    return s, (cx, cy - r - 18), (cx, cy + r + 18)


def voltmeter(cx, cy, reading, rcol=INK, r=20):
    s = circle(cx, cy, r, "#fff", INK, 2)
    s += text(cx, cy + 6, "V", 16, INK, "middle", "bold")
    s += text(cx, cy + r + 16, reading, 13, rcol, "middle", "bold")
    return s


# ── Рис. 7.1.1 — будова конденсатора ─────────────────────────────────────────
def fig11_anatomy():
    W, H = 720, 430
    s = header(W, H)
    s += text(W / 2, 34, "Будова конденсатора: дві обкладки й діелектрик", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "два провідники, розділені ізолятором — жодного провідного містка між ними",
              12.5, GREY, "middle", style="italic")
    cx, cy = 340, 232
    plates, c = cap_plates(cx, cy, ph=160, gap=98, pt=14)
    s += rect(c["li"], cy - 80, c["ri"] - c["li"], 160, "#f3efe6", "none", 0)  # діелектрик
    s += plates
    s += text(c["lo"] - 4, cy - 92, "обкладка", 13, INK, "middle", "bold")
    s += text(c["ro"] + 4, cy - 92, "обкладка", 13, INK, "middle", "bold")
    s += dim_h(c["li"], c["ri"], cy - 102, "d (зазор)")
    s += dim_v(c["ro"] + 14 + 40, cy - 80, cy + 80, "A")
    s += text(c["ro"] + 60, cy + 100, "площа обкладки", 11.5, GREY, "start", style="italic")
    s += text(c["ll"] - 2, cy - 12, "вивід", 12, GREY, "middle")
    s += text(c["rl"] + 2, cy - 12, "вивід", 12, GREY, "middle")
    s += line(cx, cy + 84, cx, cy + 116, GREY, 1.4)
    s += text(cx, cy + 132, "діелектрик (ізолятор)", 13, "#9c7b46", "middle", "bold")
    s += rect(70, H - 50, W - 140, 32, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 29, "Між обкладками — лише ізолятор: провідного шляху з пластини на пластину немає.",
              13, INK, "middle", "bold")
    save("fig-7-1-1-anatomy.svg", s)


# ── Рис. 7.1.2 — рівний і протилежний заряд, сумарно нуль ────────────────────
def fig11_equal_opposite():
    W, H = 760, 430
    s = header(W, H)
    s += text(W / 2, 34, "Заряд не накопичується, а РОЗДІЛЯЄТЬСЯ", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "скільки електронів пішло з однієї обкладки, стільки прийшло на іншу",
              12.5, GREY, "middle", style="italic")
    cx, cy = 320, 222
    plates, c = cap_plates(cx, cy, ph=158, gap=120, pt=14,
                           lfill="#dbe3f7", lstroke=BLUE, rfill="#f7dada", rstroke=RED)
    s += rect(c["li"], cy - 79, c["ri"] - c["li"], 158, "#faf7f0", "none", 0)
    s += plates
    for k in range(4):
        yk = cy - 54 + k * 36
        s += minus(c["li"] - 6, yk, 6, BLUE, 1.8)
        s += plus(c["ri"] + 6, yk, 6, RED, 1.8)
    s += text(c["lo"] - 6, cy - 92, "−Q", 16, BLUE, "middle", "bold")
    s += text(c["ro"] + 6, cy - 92, "+Q", 16, RED, "middle", "bold")
    s += text(c["lo"] - 6, cy + 102, "надлишок", 11.5, BLUE, "middle")
    s += text(c["lo"] - 6, cy + 117, "електронів", 11.5, BLUE, "middle")
    s += text(c["ro"] + 6, cy + 102, "брак", 11.5, RED, "middle")
    s += text(c["ro"] + 6, cy + 117, "електронів", 11.5, RED, "middle")
    # accounting box
    s += rect(520, 150, 210, 150, "#fbfbfb", GREY, 1.4, 10)
    s += text(625, 178, "бухгалтерія заряду", 13.5, INK, "middle", "bold")
    s += text(625, 218, "(+Q) + (−Q) = 0", 16, INK, "middle", "bold")
    s += text(625, 252, "пристрій загалом", 12, GREY, "middle", style="italic")
    s += text(625, 270, "лишається нейтральним", 12, GREY, "middle", style="italic")
    s += rect(70, H - 50, W - 140, 32, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 29, "Джерело лише ПЕРЕКЛАЛО заряд — це збереження заряду (§1.1), а не його народження.",
              12.5, INK, "middle", "bold")
    save("fig-7-1-2-equal-opposite.svg", s)


# ── Рис. 7.1.3 — однорідне поле в зазорі ─────────────────────────────────────
def fig11_field():
    W, H = 760, 440
    s = header(W, H)
    s += text(W / 2, 34, "Поле в зазорі — носій запасеної енергії", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "між пластинами поле однорідне; на краях лінії трохи розходяться (крайовий ефект)",
              12.5, GREY, "middle", style="italic")
    cx, cy = 350, 234
    plates, c = cap_plates(cx, cy, ph=176, gap=160, pt=14,
                           lfill="#f7dada", lstroke=RED, rfill="#dbe3f7", rstroke=BLUE)
    s += rect(c["li"], cy - 88, c["ri"] - c["li"], 176, "#f4faf4", "none", 0)
    s += plates
    for k in range(5):
        yk = cy - 68 + k * 34
        s += plus(c["li"] - 6, yk, 6, RED, 1.8)
        s += minus(c["ri"] + 6, yk, 6, BLUE, 1.8)
        s += arrow(c["li"] + 12, yk, c["ri"] - 12, yk, GREEN, 2)
    # крайовий ефект — дуги, що вибухають назовні
    s += f'<path d="M {c["li"]+6:.1f},{cy-88:.1f} Q {c["li"]-26:.1f},{cy-112:.1f} {c["ri"]-6:.1f},{cy-88:.1f}" fill="none" stroke="{GREEN}" stroke-width="1.6" stroke-dasharray="4,4"/>\n'
    s += f'<path d="M {c["li"]+6:.1f},{cy+88:.1f} Q {c["li"]-26:.1f},{cy+112:.1f} {c["ri"]-6:.1f},{cy+88:.1f}" fill="none" stroke="{GREEN}" stroke-width="1.6" stroke-dasharray="4,4"/>\n'
    s += text(cx, cy - 120, "крайовий ефект", 12, GREEN, "middle", style="italic")
    s += text(cx, cy + 2, "однорідне поле E", 14, GREEN, "middle", "bold")
    s += text(c["lo"] - 6, cy - 100, "+", 18, RED, "middle", "bold")
    s += text(c["ro"] + 6, cy - 100, "−", 18, BLUE, "middle", "bold")
    s += rect(70, H - 50, W - 140, 32, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 29, "Поле × зазор = напруга (§1.6): більше розділеного заряду → сильніше поле → вища напруга.",
              12, INK, "middle", "bold")
    save("fig-7-1-3-field.svg", s)


# ── Рис. 7.1.4 — зарядка: джерело переганяє електрони ────────────────────────
def fig11_charging():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 34, "Зарядка: джерело переганяє електрони по дротах", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "струм тече в дротах, поки конденсатор заповнюється — але не крізь діелектрик",
              12.5, GREY, "middle", style="italic")
    bat, bt, bb = battery(150, 232)
    s += bat
    s += text(150, 318, "батарея", 12.5, INK, "middle")
    capsvg, ctop, cbot = cap_h(620, 218, pw=120, gap=34, pt=11, lead=30)
    s += capsvg
    s += text(700, 210, "конденсатор", 12.5, INK, "start", "bold")
    s += text(700, 226, "(заповнюється)", 11.5, GREY, "start", style="italic")
    s += plus(620 - 70, 218 - 17 - 5, 6, RED, 1.8)
    s += minus(620 - 70, 218 + 17 + 5, 6, BLUE, 1.8)
    topY, botY = 140, 322
    s += line(bt[0], bt[1], bt[0], topY, INK, 2.4)
    s += line(bt[0], topY, ctop[0], topY, INK, 2.4)
    s += line(ctop[0], topY, ctop[0], ctop[1], INK, 2.4)
    s += line(bb[0], bb[1], bb[0], botY, INK, 2.4)
    s += line(bb[0], botY, cbot[0], botY, INK, 2.4)
    s += line(cbot[0], botY, cbot[0], cbot[1], INK, 2.4)
    # умовний струм (червоний)
    s += arrow(300, topY, 430, topY, RED, 2.6)
    s += text(380, topY - 9, "умовний струм I", 12.5, RED, "middle", "bold")
    s += arrow(430, botY, 300, botY, RED, 2.6)
    # електрони (сині −) у протилежний бік
    for x in (340, 400, 460):
        s += minus(x, topY + 12, 6, BLUE, 1.6)
    s += arrow(470, topY + 12, 330, topY + 12, BLUE, 1.8)
    for x in (340, 400, 460):
        s += minus(x, botY - 12, 6, BLUE, 1.6)
    s += arrow(330, botY - 12, 470, botY - 12, BLUE, 1.8)
    s += text(540, botY + 16, "електрони e⁻ — у зворотний бік", 12, BLUE, "middle", style="italic")
    # заборона крізь зазор
    s += text(620, 218 + 2, "✗", 18, GREEN, "middle", "bold")
    s += text(620 + 96, 218 + 2, "крізь діелектрик — ні", 11.5, GREEN, "start", "bold")
    save("fig-7-1-4-charging.svg", s)


# ── Рис. 7.1.5 — блокує постійний, пропускає зміну ───────────────────────────
def fig11_blocks_dc():
    W, H = 820, 410
    s = header(W, H)
    s += text(W / 2, 32, "Конденсатор реагує на ЗМІНУ напруги, а не на її рівень", 19, INK, "middle", "bold")

    def loop(x_src, src_svg, src_top, src_bot, cap_cx, cur):
        out = src_svg
        cap_svg, ct, cb = cap_h(cap_cx, 232, pw=92, gap=28, pt=10, lead=26)
        out += cap_svg
        topY, botY = 150, 322
        out += line(src_top[0], src_top[1], src_top[0], topY, INK, 2.2)
        out += line(src_top[0], topY, ct[0], topY, INK, 2.2)
        out += line(ct[0], topY, ct[0], ct[1], INK, 2.2)
        out += line(src_bot[0], src_bot[1], src_bot[0], botY, INK, 2.2)
        out += line(src_bot[0], botY, cb[0], botY, INK, 2.2)
        out += line(cb[0], botY, cb[0], cb[1], INK, 2.2)
        mid = (src_top[0] + cap_cx) / 2
        if cur:
            out += arrow(mid - 40, topY, mid + 40, topY, RED, 2.4)
            out += arrow(mid + 40, botY, mid - 40, botY, RED, 2.4)
            out += text(mid, topY - 9, "I ≠ 0", 14, RED, "middle", "bold")
        else:
            out += text(mid, topY - 9, "I = 0", 14, GREY, "middle", "bold")
            out += line(mid - 12, topY - 6, mid + 12, topY + 6, GREY, 2)  # перекреслення
        return out

    # ліва панель — стала напруга
    s += rect(30, 70, 370, 320, "none", FAINT, 2, 14)
    s += text(215, 96, "стала напруга (DC)", 15, INK, "middle", "bold")
    bat, bt, bb = battery(140, 232)
    s += loop(140, bat, bt, bb, 300, cur=False)
    s += text(300, 300, "заряджений →", 12, GREY, "middle")
    s += text(300, 316, "діє як РОЗРИВ", 13, INK, "middle", "bold")

    # права панель — змінна напруга
    s += rect(420, 70, 370, 320, "none", FAINT, 2, 14)
    s += text(605, 96, "напруга змінюється", 15, INK, "middle", "bold")
    src, st, sb = source_ac(530, 232)
    s += loop(530, src, st, sb, 690, cur=True)
    s += text(690, 300, "увесь час дозаряд-", 12, GREY, "middle")
    s += text(690, 316, "жається → струм є", 13, INK, "middle", "bold")
    save("fig-7-1-5-blocks-dc.svg", s)


# ── Рис. 7.1.6 — водогінна аналогія: пружна перетинка ────────────────────────
def fig11_water():
    W, H = 820, 440
    s = header(W, H)
    s += text(W / 2, 34, "Конденсатор як пружна перетинка в трубі", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "вода крізь мембрану не тече ніколи; під тиском вона вигинається й запасає",
              12.5, GREY, "middle", style="italic")
    x0, x1, pipeY, pipeH = 80, 740, 150, 130
    midY = pipeY + pipeH / 2
    xm = 430
    # труба
    s += line(x0, pipeY, x1, pipeY, INK, 2.6)
    s += line(x0, pipeY + pipeH, x1, pipeY + pipeH, INK, 2.6)
    # вода ліворуч (під тиском) і праворуч
    s += rect(x0, pipeY + 2, xm - x0 - 6, pipeH - 4, "#cfe3f3", "none", 0)
    s += rect(xm + 30, pipeY + 2, x1 - (xm + 30) - 2, pipeH - 4, "#e6f0f8", "none", 0)
    # мембрана, вигнута праворуч
    s += f'<path d="M {xm:.1f},{pipeY+4:.1f} Q {xm+46:.1f},{midY:.1f} {xm:.1f},{pipeY+pipeH-4:.1f}" fill="none" stroke="{GREEN}" stroke-width="4"/>\n'
    s += text(xm + 4, pipeY - 8, "пружна перетинка", 12.5, GREEN, "middle", "bold")
    # тиск зліва
    s += arrow(x0 + 30, midY, x0 + 120, midY, BLUE, 3)
    s += text(x0 + 78, midY - 12, "тиск (напруга)", 12.5, BLUE, "middle", "bold")
    s += text(x0 + 70, midY + 26, "= високий бік (−Q)", 11.5, GREY, "middle", style="italic")
    s += arrow(xm + 80, midY, xm + 150, midY, INK, 2.2)
    s += text(xm + 150, midY + 22, "воду виштовхнуто рівно стільки ж (+Q)", 11.5, GREY, "start", style="italic")
    s += text(xm + 70, pipeY + pipeH + 26, "крізь мембрану вода не тече (постійний потік блокується)",
              12, INK, "middle", style="italic")
    # де ламається — пробій
    by = 360
    s += rect(60, by, W - 120, 56, "#fdeded", RED, 1.6, 10)
    s += text(86, by + 24, "Де аналогія ламається:", 13, RED, "start", "bold")
    s += text(86, by + 43, "при завеликій напрузі діелектрик не «розправляється», а ПРОБИВАЄТЬСЯ наскрізь (§7.5) — мембрана рветься.",
              12, INK, "start")
    save("fig-7-1-6-water.svg", s)


# ── Рис. 7.1.7 — пам'ять: конденсатор vs резистор ────────────────────────────
def fig11_memory():
    W, H = 820, 440
    s = header(W, H)
    s += text(W / 2, 32, "Конденсатор пам'ятає, резистор — забуває", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "той самий дослід: від'єднати джерело й поміряти напругу на елементі",
              12.5, GREY, "middle", style="italic")

    def mini(cx, cy, elem, vread, vcol, spark=False):
        # елемент із виводами вгору й вниз до вузла, поряд вольтметр
        out = ""
        if elem == "R":
            out += rect(cx - 16, cy - 26, 32, 52, "#fff", INK, 2, 3)
            out += text(cx, cy + 6, "R", 16, INK, "middle", "bold")
            out += line(cx, cy - 26, cx, cy - 46, INK, 2.2)
            out += line(cx, cy + 26, cx, cy + 46, INK, 2.2)
            top, bot = cy - 46, cy + 46
        else:
            csvg, ct, cb = cap_h(cx, cy, pw=52, gap=18, pt=7,
                                 top=("#f7dada", RED), bot=("#dbe3f7", BLUE), lead=20)
            out += csvg
            top, bot = ct[1], cb[1]
        # вольтметр праворуч, під'єднаний паралельно
        vx = cx + 70
        out += line(cx, top, vx, top, INK, 2)
        out += line(cx, bot, vx, bot, INK, 2)
        out += line(vx, top, vx, cy - 20, INK, 2)
        out += line(vx, bot, vx, cy + 20, INK, 2)
        out += voltmeter(vx, cy, vread, vcol)
        if spark:
            out += line(cx - 30, cy - 6, cx - 44, cy - 18, RED, 2)
            out += line(cx - 44, cy - 18, cx - 36, cy - 12, RED, 2)
            out += line(cx - 36, cy - 12, cx - 50, cy - 24, RED, 2)
            out += text(cx - 58, cy - 8, "ще б'є!", 11, RED, "end", "bold")
        return out

    # рядок резистора
    s += text(120, 110, "РЕЗИСТОР", 15, INK, "start", "bold")
    s += rect(96, 124, 300, 150, "none", FAINT, 1.6, 12)
    s += text(170, 150, "поки під'єднано", 12, GREY, "middle")
    s += mini(170, 210, "R", "U", INK)
    s += arrow(250, 200, 300, 200, GREY, 2)
    s += text(345, 150, "від'єднали", 12, GREY, "middle")
    s += mini(345, 210, "R", "0 В", GREY)
    s += text(255, 262, "забув миттєво — енергію спалив на тепло (§3.6)", 11.5, INK, "middle", style="italic")

    # рядок конденсатора
    s += text(120, 312, "КОНДЕНСАТОР", 15, INK, "start", "bold")
    s += rect(96, 326, 300, 100, "none", FAINT, 1.6, 12)
    s += text(170, 350, "поки під'єднано", 12, GREY, "middle")
    s += mini(170, 384, "C", "U", INK)
    s += arrow(250, 374, 300, 374, GREY, 2)
    s += text(345, 350, "від'єднали", 12, GREY, "middle")
    s += mini(345, 384, "C", "U (тримає!)", RED, spark=True)
    # підсумкова панель праворуч
    s += rect(430, 124, 360, 302, LGRN, GREEN, 1.6, 12)
    s += text(610, 156, "у чому різниця", 15, INK, "middle", "bold")
    s += text(452, 196, "Резистор:", 13.5, INK, "start", "bold")
    s += text(452, 218, "немає пам'яті — прибрав напругу,", 12.5, INK, "start")
    s += text(452, 236, "струму вмить нема; енергію", 12.5, INK, "start")
    s += text(452, 254, "безповоротно віддав теплом.", 12.5, INK, "start")
    s += text(452, 296, "Конденсатор:", 13.5, INK, "start", "bold")
    s += text(452, 318, "має пам'ять — розділений заряд", 12.5, INK, "start")
    s += text(452, 336, "лишається, напруга тримається,", 12.5, INK, "start")
    s += text(452, 354, "він готовий віддати струм.", 12.5, INK, "start")
    s += text(452, 392, "⚠ Велика «банка» на платі б'є", 12.5, RED, "start", "bold")
    s += text(452, 410, "струмом і після вимкнення.", 12.5, RED, "start", "bold")
    save("fig-7-1-7-memory.svg", s)


# ── Рис. 7.1.8 — умовні позначення на схемі ──────────────────────────────────
def fig11_symbol():
    W, H = 760, 380
    s = header(W, H)
    s += text(W / 2, 34, "Умовні позначення конденсатора на схемі", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "малюнок прямо повторює будову — дві обкладки із зазором", 12.5, GREY, "middle", style="italic")

    # неполярний
    s += rect(40, 84, 220, 230, "none", FAINT, 1.6, 12)
    s += text(150, 110, "неполярний", 14, INK, "middle", "bold")
    nx, ny = 150, 200
    s += line(nx - 8, ny - 34, nx - 8, ny + 34, INK, 3)
    s += line(nx + 8, ny - 34, nx + 8, ny + 34, INK, 3)
    s += line(nx - 8, ny, nx - 58, ny, INK, 2.4)
    s += line(nx + 8, ny, nx + 58, ny, INK, 2.4)
    s += text(nx, ny - 50, "C", 17, INK, "middle", "bold")
    s += text(150, 296, "дві однакові риски", 12, GREY, "middle", style="italic")

    # полярний (електролітичний)
    s += rect(280, 84, 220, 230, "none", FAINT, 1.6, 12)
    s += text(390, 110, "полярний (електролітичний)", 12.5, INK, "middle", "bold")
    px, py = 390, 200
    s += line(px - 8, py - 34, px - 8, py + 34, INK, 3)  # пряма обкладка (+)
    s += f'<path d="M {px+8:.1f},{py-34:.1f} Q {px+22:.1f},{py:.1f} {px+8:.1f},{py+34:.1f}" fill="none" stroke="{INK}" stroke-width="3"/>\n'  # зігнута (−)
    s += line(px - 8, py, px - 58, py, INK, 2.4)
    s += line(px + 8, py, px + 58, py, INK, 2.4)
    s += plus(px - 30, py - 20, 7, RED, 1.8)
    s += text(390, 296, "одна обкладка зігнута; «+» обов'язковий", 11.5, GREY, "middle", style="italic")

    # відповідність будові
    s += rect(520, 84, 200, 230, "none", FAINT, 1.6, 12)
    s += text(620, 110, "= дві обкладки", 13.5, INK, "middle", "bold")
    pl, c = cap_plates(620, 205, ph=90, gap=44, pt=9, lead=26)
    s += pl
    s += arrow(620, 150, 620, 168, GREY, 1.8)
    s += text(620, 142, "символ", 12, GREY, "middle", style="italic")
    s += text(620, 286, "реальні провідники", 11.5, GREY, "middle", style="italic")
    save("fig-7-1-8-symbol.svg", s)


# ── Рис. 7.2.1 — означення Q = C·V (графік) ──────────────────────────────────
def fig21_definition():
    W, H = 700, 440
    s = header(W, H)
    s += text(W / 2, 34, "Заряд прямо пропорційний напрузі: Q = C·V", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "нахил прямої «заряд–напруга» і є ємність C", 12.5, GREY, "middle", style="italic")
    ox, oy = 120, 370
    s += arrow(ox, oy, ox, 80, INK, 2)
    s += arrow(ox, oy, 640, oy, INK, 2)
    s += text(648, oy + 4, "V", 15, INK, "start", "bold")
    s += text(ox - 8, 74, "Q", 15, INK, "middle", "bold")
    s += text(ox - 10, oy + 22, "0", 12, GREY, "middle")
    # дві прямі з різним нахилом
    s += line(ox, oy, ox + 470, oy - 264, RED, 2.8)
    s += line(ox, oy, ox + 470, oy - 132, BLUE, 2.8)
    s += text(ox + 480, oy - 262, "більша C", 13.5, RED, "start", "bold")
    s += text(ox + 480, oy - 130, "менша C", 13.5, BLUE, "start", "bold")
    # точка на «більшій» прямій + пунктири
    px, py = ox + 470 * 0.6, oy - 264 * 0.6
    s += line(px, oy, px, py, GREY, 1.4, dash="4,4")
    s += line(ox, py, px, py, GREY, 1.4, dash="4,4")
    s += circle(px, py, 4.5, RED, RED, 0)
    s += text(px, oy + 20, "V₁", 13, GREY, "middle", "bold")
    s += text(ox - 10, py + 4, "Q₁", 13, GREY, "end", "bold")
    s += text(px + 10, py - 10, "Q₁ = C · V₁", 14, INK, "start", "bold")
    s += rect(70, H - 46, W - 140, 30, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 26, "Подвоїв напругу — подвоївся заряд; відношення Q/V (нахил) стале — це і є C.",
              12.5, INK, "middle", "bold")
    save("fig-7-2-1-definition.svg", s)


# ── Рис. 7.2.2 — шкала ємностей пФ…Ф ─────────────────────────────────────────
def fig21_farad():
    W, H = 820, 330
    s = header(W, H)
    s += text(W / 2, 34, "Реальні ємності: від пікофарад до фарад", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "практичний діапазон займає понад дванадцять порядків", 12.5, GREY, "middle", style="italic")
    x0, x1, y = 80, 760, 220

    def X(exp):
        return x0 + (exp + 12) / 12 * (x1 - x0)

    s += line(x0, y, x1, y, INK, 2.4)
    for e in range(-12, 1):
        s += line(X(e), y - 5, X(e), y + 5, INK, 1.4)
    majors = {-12: "1 пФ", -9: "1 нФ", -6: "1 мкФ", -3: "1 мФ", 0: "1 Ф"}
    for e, lab in majors.items():
        s += line(X(e), y - 9, X(e), y + 9, INK, 2.6)
        s += text(X(e), y + 30, lab, 13, INK, "middle", "bold")
    # смуги застосувань
    def band(e1, e2, yy, col, lab):
        out = rect(X(e1), yy, X(e2) - X(e1), 18, col, "none", 0, 4)
        out += text((X(e1) + X(e2)) / 2, yy + 13, lab, 11.5, INK, "middle", "bold")
        return out

    s += band(-12, -6, 120, "#fdeecf", "кераміка")
    s += band(-9, -4, 144, "#e7f0e0", "плівка")
    s += band(-6, -2, 168, "#dbe7f5", "електролітичні")
    s += band(-0.5, 0.3, 120, "#f3dede", "суперкон.")
    s += text(W / 2, H - 22, "«104» = 100 нФ · «4u7» = 4.7 мкФ — типове маркування на деталях.",
              12.5, GREY, "middle", style="italic")
    save("fig-7-2-2-farad.svg", s)


# ── Рис. 7.2.3 — залежність від площі ────────────────────────────────────────
def fig21_area():
    W, H = 760, 410
    s = header(W, H)
    s += text(W / 2, 34, "Більша площа обкладок — більша ємність", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "за тієї самої напруги вдвічі більші пластини приймають вдвічі більший заряд",
              12.5, GREY, "middle", style="italic")
    # ліворуч — мала площа
    plL, cL = cap_plates(210, 232, ph=86, gap=70, pt=12, lfill="#f7dada", lstroke=RED,
                         rfill="#dbe3f7", rstroke=BLUE)
    s += plL
    for k in range(2):
        s += plus(cL["li"] - 6, 218 + k * 28, 5, RED, 1.6)
        s += minus(cL["ri"] + 6, 218 + k * 28, 5, BLUE, 1.6)
    s += dim_v(cL["ro"] + 40, 232 - 43, 232 + 43, "A")
    s += text(210, 320, "ємність C, заряд Q", 12.5, INK, "middle", "bold")
    # праворуч — подвійна площа
    plR, cR = cap_plates(550, 232, ph=176, gap=70, pt=12, lfill="#f7dada", lstroke=RED,
                         rfill="#dbe3f7", rstroke=BLUE)
    s += plR
    for k in range(4):
        s += plus(cR["li"] - 6, 188 + k * 28, 5, RED, 1.6)
        s += minus(cR["ri"] + 6, 188 + k * 28, 5, BLUE, 1.6)
    s += dim_v(cR["ro"] + 40, 232 - 88, 232 + 88, "2A")
    s += text(550, 348, "ємність 2C, заряд 2Q", 12.5, INK, "middle", "bold")
    s += text(W / 2, H - 24, "та сама напруга V    ·    C ∝ A", 14, GREEN, "middle", "bold")
    save("fig-7-2-3-area.svg", s)


# ── Рис. 7.2.4 — залежність від зазору ───────────────────────────────────────
def fig21_gap():
    W, H = 760, 410
    s = header(W, H)
    s += text(W / 2, 34, "Менший зазор — більша ємність", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "за тієї самої напруги тонший зазор дає сильніше поле — і вміщає більше заряду",
              12.5, GREY, "middle", style="italic")
    # ліворуч — широкий зазор
    plL, cL = cap_plates(200, 232, ph=150, gap=120, pt=12, lfill="#f7dada", lstroke=RED,
                         rfill="#dbe3f7", rstroke=BLUE)
    s += rect(cL["li"], 232 - 75, cL["ri"] - cL["li"], 150, "#f4faf4", "none", 0)
    s += plL
    for k in range(3):
        yk = 200 + k * 32
        s += arrow(cL["li"] + 8, yk, cL["ri"] - 8, yk, GREEN, 1.8)
    s += dim_h(cL["li"], cL["ri"], 232 - 90, "d")
    s += text(200, 326, "слабше поле → ємність C", 12, INK, "middle")
    # праворуч — вузький зазор
    plR, cR = cap_plates(560, 232, ph=150, gap=48, pt=12, lfill="#f7dada", lstroke=RED,
                         rfill="#dbe3f7", rstroke=BLUE)
    s += rect(cR["li"], 232 - 75, cR["ri"] - cR["li"], 150, "#f4faf4", "none", 0)
    s += plR
    for k in range(6):
        yk = 186 + k * 22
        s += arrow(cR["li"] + 6, yk, cR["ri"] - 6, yk, GREEN, 1.8)
    s += dim_h(cR["li"], cR["ri"], 232 - 90, "d/2")
    s += text(560, 326, "сильніше поле → ємність 2C", 12, INK, "middle")
    s += text(W / 2, H - 24, "та сама напруга V    ·    C ∝ 1/d", 14, GREEN, "middle", "bold")
    save("fig-7-2-4-gap.svg", s)


# ── Рис. 7.2.5 — механізм діелектрика ────────────────────────────────────────
def fig21_dielectric_mech():
    W, H = 760, 430
    s = header(W, H)
    s += text(W / 2, 34, "Діелектрик послаблює поле — і вміщає більше заряду", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "молекули-диполі вишиковуються вздовж поля, а їхні зв'язані заряди дають зустрічне поле",
              12.5, GREY, "middle", style="italic")
    cx, cy = 360, 240
    plL, c = cap_plates(cx, cy, ph=180, gap=200, pt=14, lfill="#f7dada", lstroke=RED,
                       rfill="#dbe3f7", rstroke=BLUE)
    s += rect(c["li"], cy - 90, c["ri"] - c["li"], 180, "#f6f3ee", "none", 0)
    s += plL
    # заряди обкладок
    for k in range(5):
        yk = cy - 72 + k * 36
        s += plus(c["li"] - 6, yk, 5, RED, 1.6)
        s += minus(c["ri"] + 6, yk, 5, BLUE, 1.6)
    # сітка диполів: − ліворуч (до + плити), + праворуч
    for ix in range(3):
        for iy in range(4):
            dx = c["li"] + 34 + ix * 50
            dy = cy - 54 + iy * 36
            s += f'<ellipse cx="{dx:.1f}" cy="{dy:.1f}" rx="18" ry="9" fill="#ffffff" stroke="{GREY}" stroke-width="1.3"/>\n'
            s += minus(dx - 9, dy, 4.5, BLUE, 1.4)
            s += plus(dx + 9, dy, 4.5, RED, 1.4)
    s += text(cx, cy + 110, "диполі вишиковуються вздовж поля; зв'язані заряди — зустрічне поле", 12, "#9c7b46", "middle", style="italic")
    # підсумок
    s += rect(70, H - 46, W - 140, 30, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 26, "Слабше поле → нижча напруга за того ж заряду → за тієї ж напруги влазить більше: C × εr.",
              12, INK, "middle", "bold")
    save("fig-7-2-5-dielectric-mech.svg", s)


# ── Рис. 7.2.6 — таблиця діелектричної проникності ───────────────────────────
def fig21_dielectric_table():
    W, H = 760, 430
    s = header(W, H)
    s += text(W / 2, 34, "Відносна діелектрична проникність εr матеріалів", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "логарифмічна шкала: від 1 (вакуум) до тисяч (сегнетоелектрична кераміка)",
              12.5, GREY, "middle", style="italic")
    mats = [("вакуум", 1.0), ("повітря", 1.0006), ("тефлон (PTFE)", 2.1),
            ("плівка (поліестер)", 3.2), ("папір", 3.5), ("скло, слюда", 6.0),
            ("кераміка NP0", 30.0), ("кераміка X7R", 3000.0)]
    x0, ytop = 200, 92
    scale = 150.0  # px на декаду
    for i, (name, er) in enumerate(mats):
        y = ytop + i * 38
        w = max(math.log10(er), 0.0) * scale
        s += text(x0 - 12, y + 14, name, 12.5, INK, "end")
        s += rect(x0, y, max(w, 2), 22, "#dbe7f5", BLUE, 1.4, 3)
        val = f"{er:g}"
        s += text(x0 + max(w, 2) + 8, y + 16, val, 12, INK, "start", "bold")
    s += text(x0, ytop + len(mats) * 38 + 6, "вода ≈ 80 — але проводить, тож як діелектрик не годиться (§2.11)",
              11.5, GREY, "start", style="italic")
    save("fig-7-2-6-dielectric-table.svg", s)


# ── Рис. 7.2.7 — формула плаского конденсатора ───────────────────────────────
def fig21_formula():
    W, H = 760, 360
    s = header(W, H)
    s += text(W / 2, 36, "Формула плаского конденсатора", 20, INK, "middle", "bold")
    cy = 170
    # C = ε₀ · εr · A / d  — по частинах
    s += text(150, cy, "C", 40, INK, "middle", "bold")
    s += text(196, cy, "=", 32, INK, "middle")
    s += text(250, cy, "ε₀", 30, GREY, "middle", "bold")
    s += text(292, cy, "·", 28, INK, "middle")
    s += text(336, cy, "εr", 30, "#9c7b46", "middle", "bold")
    s += text(372, cy, "·", 28, INK, "middle")
    # дріб A/d
    s += text(430, cy - 16, "A", 30, GREEN, "middle", "bold")
    s += line(404, cy + 2, 456, cy + 2, INK, 2.4)
    s += text(430, cy + 34, "d", 30, RED, "middle", "bold")
    # анотації
    s += arrow(430, cy - 60, 430, cy - 34, GREEN, 1.8)
    s += text(430, cy - 68, "↑ площа → ↑ C", 13, GREEN, "middle", "bold")
    s += arrow(430, cy + 78, 430, cy + 50, RED, 1.8)
    s += text(430, cy + 96, "↑ зазор → ↓ C", 13, RED, "middle", "bold")
    s += arrow(336, cy + 40, 336, cy + 16, "#9c7b46", 1.8)
    s += text(336, cy + 58, "↑ εr → ↑ C", 13, "#9c7b46", "middle", "bold")
    s += text(250, cy + 40, "стала природи", 11.5, GREY, "middle", style="italic")
    s += rect(120, 260, W - 240, 56, "#fbfbfb", GREY, 1.4, 10)
    s += text(W / 2, 284, "ε₀ = 8.854 × 10⁻¹² Ф/м  (проникність вакууму, з §1.2)", 14, INK, "middle", "bold")
    s += text(W / 2, 305, "точна для пласких обкладок (без крайового ефекту)", 11.5, GREY, "middle", style="italic")
    save("fig-7-2-7-formula.svg", s)


# ── Рис. 7.2.8 — конструкція: велика площа в малому тілі ──────────────────────
def fig21_construction():
    W, H = 800, 400
    s = header(W, H)
    s += text(W / 2, 34, "Як отримати велику ємність у малому тілі", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "велику площу згортають у рулон, а діелектрик роблять якнайтоншим",
              12.5, GREY, "middle", style="italic")
    # ліворуч — пласка пачка стрічок
    s += text(190, 96, "стрічки: фольга — плівка — фольга", 12.5, INK, "middle", "bold")
    lx, ly, lw = 70, 130, 240
    layers = [("фольга (+)", "#f7dada", RED), ("діелектрична плівка", "#f6f3ee", "#9c7b46"),
              ("фольга (−)", "#dbe3f7", BLUE), ("діелектрична плівка", "#f6f3ee", "#9c7b46")]
    for i, (lab, fill, col) in enumerate(layers):
        yy = ly + i * 30
        s += rect(lx, yy, lw, 22, fill, col, 1.4, 2)
        s += text(lx + lw + 8, yy + 16, lab, 11.5, col, "start")
    s += dim_h(lx, lx + lw, ly - 12, "велика довжина (= площа A)")
    s += text(190, ly + 150, "тонка плівка → малий d", 12, RED, "middle", "bold")
    # стрілка згортання
    s += arrow(330, 230, 430, 230, INK, 2.6)
    s += text(380, 218, "згорнути", 12, INK, "middle", "bold")
    # праворуч — рулон (циліндр зі спіраллю)
    rcx, rcy = 600, 232
    s += f'<ellipse cx="{rcx}" cy="{rcy-70}" rx="60" ry="18" fill="#eef2f6" stroke="{INK}" stroke-width="2"/>\n'
    s += rect(rcx - 60, rcy - 70, 120, 140, "#eef2f6", "none", 0)
    s += line(rcx - 60, rcy - 70, rcx - 60, rcy + 70, INK, 2)
    s += line(rcx + 60, rcy - 70, rcx + 60, rcy + 70, INK, 2)
    s += f'<ellipse cx="{rcx}" cy="{rcy+70}" rx="60" ry="18" fill="#eef2f6" stroke="{INK}" stroke-width="2"/>\n'
    # спіраль на верхньому торці
    pts = []
    for a in range(0, 720, 12):
        rr = 4 + a / 720 * 54
        xa = rcx + rr * math.cos(math.radians(a))
        ya = (rcy - 70) + rr * math.sin(math.radians(a)) * 0.30
        pts.append(f"{xa:.1f},{ya:.1f}")
    sp = "M " + " L ".join(pts)
    s += f'<path d="{sp}" fill="none" stroke="{BLUE}" stroke-width="1.4"/>\n'
    # виводи
    s += line(rcx - 24, rcy - 86, rcx - 24, rcy - 120, INK, 2.4)
    s += line(rcx + 24, rcy - 86, rcx + 24, rcy - 120, INK, 2.4)
    s += text(rcx, rcy + 104, "рулон у малому корпусі", 12, INK, "middle", "bold")
    s += text(rcx, rcy + 122, "(зоопарк типів — §7.5)", 11, GREY, "middle", style="italic")
    save("fig-7-2-8-construction.svg", s)


# ── Рис. 7.3.1 — робота проти зростання напруги ──────────────────────────────
def fig31_work_to_charge():
    W, H = 820, 410
    s = header(W, H)
    s += text(W / 2, 34, "Звідки енергія: кожну порцію заряду тягнути все важче", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "напруга росте від нуля, тож середня «вартість» переносу — V/2",
              12.5, GREY, "middle", style="italic")
    snaps = [(1, "V/3", "легко"), (2, "2V/3", "важче"), (3, "повна V", "найважче")]
    for i, (nq, vlab, eff) in enumerate(snaps):
        cx, cy = 180 + i * 250, 220
        pl, c = cap_plates(cx, cy, ph=120, gap=64, pt=12, lfill="#f7dada", lstroke=RED,
                           rfill="#dbe3f7", rstroke=BLUE)
        s += rect(c["li"], cy - 60, c["ri"] - c["li"], 120, "#faf7f0", "none", 0)
        s += pl
        for k in range(nq):
            yk = cy - 30 + k * 26
            s += plus(c["li"] - 6, yk, 5, RED, 1.6)
            s += minus(c["ri"] + 6, yk, 5, BLUE, 1.6)
        # стрілка «зусилля» згори — росте
        alen = 24 + i * 24
        s += arrow(cx, cy - 70 - alen, cx, cy - 70, INK, 2 + i)
        s += text(cx, cy - 78 - alen, eff, 12.5, INK, "middle", "bold")
        s += text(cx, cy + 92, "напруга: " + vlab, 12.5, INK, "middle", "bold")
        s += text(cx, cy + 110, "+ ще порція заряду", 11, GREY, "middle", style="italic")
    s += rect(70, H - 44, W - 140, 30, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 24, "Перша порція — майже задарма (V≈0), остання — проти повної V. Тому W = Q·(V/2) = ½·Q·V.",
              12, INK, "middle", "bold")
    save("fig-7-3-1-work-to-charge.svg", s)


# ── Рис. 7.3.2 — енергія як площа трикутника під Q–V ─────────────────────────
def fig31_half_triangle():
    W, H = 700, 430
    s = header(W, H)
    s += text(W / 2, 34, "Енергія — площа під прямою «заряд–напруга»", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "пряма йде з нуля → площа це трикутник → рівно половина від Q·V",
              12.5, GREY, "middle", style="italic")
    ox, oy = 130, 360
    Vx, Qy = ox + 430, oy - 250
    # прямокутник Q·V (пунктир)
    s += rect(ox, Qy, Vx - ox, oy - Qy, "none", GREY, 1.4, 0)
    s += f'<rect x="{ox:.1f}" y="{Qy:.1f}" width="{Vx-ox:.1f}" height="{oy-Qy:.1f}" fill="none" stroke="{GREY}" stroke-width="1.4" stroke-dasharray="5,5"/>\n'
    # трикутник під прямою (залитий)
    s += f'<path d="M {ox:.1f},{oy:.1f} L {Vx:.1f},{oy:.1f} L {Vx:.1f},{Qy:.1f} Z" fill="#f4d9d6" stroke="none"/>\n'
    # осі
    s += arrow(ox, oy, ox, 80, INK, 2)
    s += arrow(ox, oy, 640, oy, INK, 2)
    s += text(648, oy + 4, "V", 15, INK, "start", "bold")
    s += text(ox - 8, 74, "Q", 15, INK, "middle", "bold")
    s += text(ox - 10, oy + 22, "0", 12, GREY, "middle")
    # пряма
    s += line(ox, oy, Vx, Qy, RED, 2.8)
    s += text((ox + Vx) / 2 + 30, (oy + Qy) / 2 - 60, "½·Q·V", 17, "#9a2b22", "middle", "bold")
    s += text((ox + Vx) / 2 + 30, (oy + Qy) / 2 - 40, "(трикутник)", 12, "#9a2b22", "middle", style="italic")
    s += text(ox + 80, Qy - 10, "прямокутник Q·V (якби V була стала)", 12, GREY, "start", style="italic")
    s += text(Vx, oy + 22, "V", 13, GREY, "middle", "bold")
    s += text(ox - 12, Qy + 4, "Q", 13, GREY, "end", "bold")
    save("fig-7-3-2-half-triangle.svg", s)


# ── Рис. 7.3.3 — три форми енергії ───────────────────────────────────────────
def fig31_three_forms():
    W, H = 760, 300
    s = header(W, H)
    s += text(W / 2, 36, "Три рівноцінні форми однієї енергії", 20, INK, "middle", "bold")
    forms = [("½ · Q · V", "знаєш заряд і напругу"),
             ("½ · C · V²", "знаєш ємність і напругу"),
             ("½ · Q² / C", "знаєш заряд і ємність")]
    for i, (f, when) in enumerate(forms):
        cx = 150 + i * 230
        s += rect(cx - 96, 90, 192, 96, "#fbfbfb", GREEN if i == 1 else GREY, 1.6 + (i == 1) * 0.6, 12)
        s += text(cx, 134, f, 21, INK, "middle", "bold")
        s += text(cx, 166, when, 11.5, GREY, "middle", style="italic")
        if i < 2:
            s += text(cx + 115, 142, "=", 24, INK, "middle")
    s += text(W / 2, 232, "усі дають однакові джоулі:  [½·C·V²] = (Кл/В)·В² = Кл·В = Дж", 13.5, INK, "middle", "bold")
    s += text(W / 2, 258, "(через Q = C·V із §7.2)", 12, GREY, "middle", style="italic")
    save("fig-7-3-3-three-forms.svg", s)


# ── Рис. 7.3.4 — енергія ∝ квадрат напруги ───────────────────────────────────
def fig31_vsquared():
    W, H = 700, 420
    s = header(W, H)
    s += text(W / 2, 34, "Енергія росте з квадратом напруги: W ∝ V²", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "удвічі вища напруга — вчетверо більше енергії", 12.5, GREY, "middle", style="italic")
    ox, oy = 120, 360
    s += arrow(ox, oy, ox, 80, INK, 2)
    s += arrow(ox, oy, 640, oy, INK, 2)
    s += text(648, oy + 4, "V", 15, INK, "start", "bold")
    s += text(ox - 8, 74, "W", 15, INK, "middle", "bold")
    # парабола W = k V²; беремо V=3 -> повна висота
    Vmax = 3.0
    px_per_V = 150
    Wfull = 260
    pts = []
    for j in range(0, 91):
        v = Vmax * j / 90
        x = ox + v * px_per_V
        y = oy - (v * v / (Vmax * Vmax)) * Wfull
        pts.append(f"{x:.1f},{y:.1f}")
    s += f'<path d="M {" L ".join(pts)}" fill="none" stroke="{RED}" stroke-width="2.8"/>\n'
    for v, lab in [(1, "V → W"), (2, "2V → 4W"), (3, "3V → 9W")]:
        x = ox + v * px_per_V
        y = oy - (v * v / 9.0) * Wfull
        s += line(x, oy, x, y, GREY, 1.3, dash="4,4")
        s += line(ox, y, x, y, GREY, 1.3, dash="4,4")
        s += circle(x, y, 4.5, RED, RED, 0)
        s += text(x + 6, y - 8, lab, 12.5, INK, "start", "bold")
    save("fig-7-3-4-vsquared.svg", s)


# ── Рис. 7.3.5 — енергія сидить у полі ───────────────────────────────────────
def fig31_field_storage():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 34, "Енергія захована в полі; розряд = поле спадає й віддає її", 19, INK, "middle", "bold")
    # ліворуч — заряджений
    cx1, cy = 200, 210
    pl, c = cap_plates(cx1, cy, ph=140, gap=86, pt=12, lfill="#f7dada", lstroke=RED,
                       rfill="#dbe3f7", rstroke=BLUE)
    s += rect(c["li"], cy - 70, c["ri"] - c["li"], 140, "#f4faf4", "none", 0)
    s += pl
    for k in range(4):
        yk = cy - 48 + k * 32
        s += plus(c["li"] - 6, yk, 5, RED, 1.6)
        s += minus(c["ri"] + 6, yk, 5, BLUE, 1.6)
        s += arrow(c["li"] + 10, yk, c["ri"] - 10, yk, GREEN, 1.8)
    s += text(cx1, cy + 96, "заряджений", 13, INK, "middle", "bold")
    s += text(cx1, cy + 113, "енергія — у полі", 12, GREEN, "middle", "bold")
    # стрілка розряду
    s += arrow(335, cy, 420, cy, INK, 2.6)
    s += text(378, cy - 10, "розряд", 12.5, INK, "middle", "bold")
    # праворуч — розряджений + навантаження світить
    cx2 = 560
    pl2, c2 = cap_plates(cx2, cy, ph=140, gap=86, pt=12)
    s += pl2
    s += text(cx2, cy + 96, "розряджений", 13, INK, "middle", "bold")
    s += text(cx2, cy + 113, "поле спало → 0", 12, GREY, "middle", "bold")
    # коло до лампи
    lampx = 720
    s += line(c2["rl"], cy, lampx, cy, INK, 2)
    s += line(lampx, cy, lampx, cy - 0, INK, 2)
    s += circle(lampx, cy, 22, "#fff7e0", "#caa24a", 2)
    s += line(lampx - 15, cy - 15, lampx + 15, cy + 15, "#caa24a", 2)
    s += line(lampx - 15, cy + 15, lampx + 15, cy - 15, "#caa24a", 2)
    for a in range(0, 360, 45):
        xa = lampx + 30 * math.cos(math.radians(a))
        ya = cy + 30 * math.sin(math.radians(a))
        xb = lampx + 38 * math.cos(math.radians(a))
        yb = cy + 38 * math.sin(math.radians(a))
        s += line(xa, ya, xb, yb, "#caa24a", 1.6)
    s += text(lampx, cy + 60, "енергія робить", 11.5, INK, "middle")
    s += text(lampx, cy + 76, "роботу в колі", 11.5, INK, "middle")
    save("fig-7-3-5-field-storage.svg", s)


# ── Рис. 7.3.6 — запас (C) проти розсіяння (R) ───────────────────────────────
def fig31_store_vs_dissipate():
    W, H = 760, 380
    s = header(W, H)
    s += text(W / 2, 34, "Доля енергії: конденсатор повертає, резистор спалює", 19, INK, "middle", "bold")

    def box(x, y, w, h, lab, col, fill):
        out = rect(x, y, w, h, fill, col, 1.8, 8)
        out += text(x + w / 2, y + h / 2 + 5, lab, 14, INK, "middle", "bold")
        return out

    # рядок резистора
    s += text(70, 110, "РЕЗИСТОР", 14, INK, "start", "bold")
    s += box(70, 124, 90, 56, "джерело", GREY, "#fbfbfb")
    s += arrow(160, 152, 240, 152, INK, 2.4)
    s += text(200, 142, "енергія", 11, INK, "middle")
    s += box(240, 124, 90, 56, "R", RED, "#fdeded")
    # тепло
    for k in range(3):
        xx = 360 + k * 26
        s += f'<path d="M {xx},170 q 6,-12 12,0 q 6,12 12,0" fill="none" stroke="{RED}" stroke-width="1.8"/>\n'
    s += text(420, 134, "100% → тепло", 12.5, RED, "start", "bold")
    s += text(420, 152, "безповоротно", 11.5, GREY, "start", style="italic")

    # рядок конденсатора
    s += text(70, 250, "КОНДЕНСАТОР", 14, INK, "start", "bold")
    s += box(70, 264, 90, 56, "джерело", GREY, "#fbfbfb")
    s += arrow(160, 286, 240, 286, INK, 2.4)
    s += text(200, 276, "енергія", 11, INK, "middle")
    s += box(240, 264, 110, 56, "C (поле)", GREEN, "#eef6ef")
    # повертається — зворотна стрілка
    s += arrow(240, 306, 162, 306, GREEN, 2.4)
    s += text(200, 326, "повертається", 11, GREEN, "middle", "bold")
    s += text(370, 280, "запас у полі →", 12.5, GREEN, "start", "bold")
    s += text(370, 298, "віддається назад (оборотно)", 11.5, GREY, "start", style="italic")
    s += rect(60, H - 44, W - 120, 30, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 24, "Тому конденсатор — реактивний (запасає), а резистор — той, що розсіює (гріється).",
              12, INK, "middle", "bold")
    save("fig-7-3-6-store-vs-dissipate.svg", s)


# ── Рис. 7.3.7 — енергія vs потужність ───────────────────────────────────────
def fig31_power():
    W, H = 760, 400
    s = header(W, H)
    s += text(W / 2, 34, "Та сама енергія, віддана швидко — це велика потужність", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "конденсатор довго накопичує (мала потужність), а віддає ривком (велика)",
              12.5, GREY, "middle", style="italic")
    ox, oy = 90, 330
    s += arrow(ox, oy, ox, 90, INK, 2)
    s += arrow(ox, oy, 700, oy, INK, 2)
    s += text(706, oy + 4, "час", 13, INK, "start", "bold")
    s += text(ox - 6, 84, "потужність", 12.5, INK, "middle", "bold")
    # зарядка: широкий низький прямокутник (площа = енергія)
    s += rect(130, oy - 46, 250, 46, "#e7f0e0", GREEN, 1.8)
    s += text(255, oy - 56, "зарядка: довго, мала потужність", 11.5, GREEN, "middle", "bold")
    s += text(255, oy - 24, "площа = енергія", 11, INK, "middle", style="italic")
    # розряд: вузький високий пік (та сама площа)
    s += rect(470, oy - 230, 24, 230, "#f3dede", RED, 1.8)
    s += text(560, oy - 150, "розряд: мить,", 12, RED, "middle", "bold")
    s += text(560, oy - 132, "велика потужність", 12, RED, "middle", "bold")
    s += text(482, oy - 244, "(та сама площа)", 10.5, GREY, "middle", style="italic")
    s += rect(60, H - 40, W - 120, 28, "#fdeded", RED, 1.4, 8)
    s += text(W / 2, H - 21, "Спалах і дефібрилятор: накопичити поволі від слабкого джерела — віддати кіловатним імпульсом.",
              11.5, INK, "middle", "bold")
    save("fig-7-3-7-power.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §7.4 — будівельники для RC
# ─────────────────────────────────────────────────────────────────────────────
def resistor_h(x1, x2, y, label="R", col=INK):
    n = 6
    seg = (x2 - x1) / n
    pts = [(x1, y)]
    for i in range(n):
        xx = x1 + seg * (i + 0.5)
        yy = y - 9 if i % 2 == 0 else y + 9
        pts.append((xx, yy))
    pts.append((x2, y))
    path = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    s = f'<path d="{path}" fill="none" stroke="{col}" stroke-width="2"/>\n'
    s += text((x1 + x2) / 2, y - 16, label, 14, INK, "middle", "bold")
    return s


def exp_path(ox, oy, w, h, kind, ncyc=5):
    pts = []
    for j in range(0, 101):
        t = ncyc * j / 100.0
        yf = (1 - math.exp(-t)) if kind == "charge" else math.exp(-t)
        x = ox + (t / ncyc) * w
        y = oy - yf * h
        pts.append(f"{x:.1f},{y:.1f}")
    return "M " + " L ".join(pts)


def _axes(ox, oy, w, h, xlab, ylab):
    s = arrow(ox, oy, ox, oy - h - 14, INK, 2)
    s += arrow(ox, oy, ox + w + 14, oy, INK, 2)
    s += text(ox + w + 18, oy + 4, xlab, 13, INK, "start", "bold")
    s += text(ox - 4, oy - h - 22, ylab, 13, INK, "middle", "bold")
    return s


# ── Рис. 7.4.1 — RC-коло (заряд/розряд) ──────────────────────────────────────
def fig41_rc_circuit():
    W, H = 760, 400
    s = header(W, H)
    s += text(W / 2, 34, "RC-коло: резистор задає темп, конденсатор накопичує", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "перемикач обирає: заряджати від джерела чи розрядити на резистор",
              12.5, GREY, "middle", style="italic")
    # батарея
    bat, bt, bb = battery(120, 285)
    s += bat
    s += text(120, 330 + 0, "", 1, INK, "middle")
    s += text(96, 285, "джерело", 12, INK, "end")
    # земляна шина
    s += line(120, 330, 600, 330, INK, 2.4)
    s += line(bb[0], bb[1], 120, 330, INK, 2.4)
    # батарея + вгору до контакту T1 (заряд)
    s += line(bt[0], bt[1], 120, 108, INK, 2.4)
    s += line(120, 108, 225, 108, INK, 2.4)
    s += circle(225, 108, 3.5, INK, INK, 0)
    s += text(205, 100, "заряд", 12, RED, "end", "bold")
    # контакт T2 (розряд) — донизу до землі
    s += circle(225, 168, 3.5, INK, INK, 0)
    s += line(225, 168, 225, 330, INK, 2.2, dash="4,4")
    s += text(205, 176, "розряд", 12, BLUE, "end", "bold")
    # полюс перемикача + важіль (зараз на «заряд»)
    pole = (272, 138)
    s += circle(pole[0], pole[1], 3.5, INK, INK, 0)
    s += line(pole[0], pole[1], 225, 108, INK, 2.6)              # важіль до T1
    s += line(pole[0], pole[1], 225, 168, GREY, 1.4, dash="3,4")  # альтернатива до T2
    # від полюса праворуч до резистора → конденсатора
    s += line(pole[0], pole[1], 300, 138, INK, 2.4)
    s += resistor_h(300, 410, 138, "R")
    s += line(410, 138, 560, 138, INK, 2.4)
    cap_svg, ct, cb = cap_h(560, 235, pw=92, gap=30, pt=10, lead=24)
    s += line(560, 138, ct[0], ct[1], INK, 2.4)
    s += cap_svg
    s += line(cb[0], cb[1], 560, 330, INK, 2.4)
    s += text(596, 235, "C", 15, INK, "start", "bold")
    # струм заряду
    s += arrow(445, 138, 510, 138, RED, 2.4)
    s += text(478, 128, "I (заряд)", 12, RED, "middle", "bold")
    save("fig-7-4-1-rc-circuit.svg", s)


# ── Рис. 7.4.2 — крива заряджання ────────────────────────────────────────────
def fig41_charge_curve():
    W, H = 720, 420
    s = header(W, H)
    s += text(W / 2, 34, "Заряджання: напруга росте за експонентою", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "круто спочатку, далі все повільніше — до напруги джерела", 12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 110, 350, 540, 250
    # асимптота
    s += f'<line x1="{ox}" y1="{oy-h}" x2="{ox+w}" y2="{oy-h}" stroke="{GREY}" stroke-width="1.4" stroke-dasharray="6,5"/>\n'
    s += text(ox + w, oy - h - 8, "V₀ (джерело)", 12.5, GREY, "end", "bold")
    # x-ticks 1τ..5τ
    for k in range(1, 6):
        x = ox + (k / 5) * w
        s += line(x, oy, x, oy + 6, INK, 1.4)
        s += text(x, oy + 22, f"{k}τ", 12, GREY, "middle", "bold")
    s += _axes(ox, oy, w, h, "час t", "напруга V")
    s += f'<path d="{exp_path(ox, oy, w, h, "charge")}" fill="none" stroke="{RED}" stroke-width="2.8"/>\n'
    for k, lab in [(1, "63%"), (5, "99%")]:
        yf = 1 - math.exp(-k)
        x = ox + (k / 5) * w
        y = oy - yf * h
        s += line(ox, y, x, y, GREY, 1.2, dash="4,4")
        s += circle(x, y, 4.5, RED, RED, 0)
        s += text(x - 8, y - 8, lab, 12.5, "#9a2b22", "end", "bold")
    save("fig-7-4-2-charge-curve.svg", s)


# ── Рис. 7.4.3 — крива розряджання ───────────────────────────────────────────
def fig41_discharge_curve():
    W, H = 720, 420
    s = header(W, H)
    s += text(W / 2, 34, "Розряджання: дзеркальна спадна експонента", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "за одну сталу часу напруга падає до 37% (це 1/e)", 12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 110, 350, 540, 250
    for k in range(1, 6):
        x = ox + (k / 5) * w
        s += line(x, oy, x, oy + 6, INK, 1.4)
        s += text(x, oy + 22, f"{k}τ", 12, GREY, "middle", "bold")
    s += _axes(ox, oy, w, h, "час t", "напруга V")
    s += f'<path d="{exp_path(ox, oy, w, h, "discharge")}" fill="none" stroke="{BLUE}" stroke-width="2.8"/>\n'
    s += text(ox + 6, oy - h - 6, "V₀", 12.5, GREY, "start", "bold")
    for k, lab in [(1, "37%"), (2, "14%"), (5, "<1%")]:
        yf = math.exp(-k)
        x = ox + (k / 5) * w
        y = oy - yf * h
        s += line(ox, y, x, y, GREY, 1.2, dash="4,4")
        s += circle(x, y, 4.5, BLUE, BLUE, 0)
        s += text(x + 8, y - 8, lab, 12.5, "#15347f", "start", "bold")
    save("fig-7-4-3-discharge-curve.svg", s)


# ── Рис. 7.4.4 — крива струму ────────────────────────────────────────────────
def fig41_current_curve():
    W, H = 720, 400
    s = header(W, H)
    s += text(W / 2, 34, "Струм заряджання спадає від V/R до нуля", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "найбільший на старті (порожній конденсатор як «коротке»), далі згасає",
              12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 110, 330, 540, 230
    for k in range(1, 6):
        x = ox + (k / 5) * w
        s += line(x, oy, x, oy + 6, INK, 1.4)
        s += text(x, oy + 22, f"{k}τ", 12, GREY, "middle", "bold")
    s += _axes(ox, oy, w, h, "час t", "струм I")
    s += f'<path d="{exp_path(ox, oy, w, h, "discharge")}" fill="none" stroke="{GREEN}" stroke-width="2.8"/>\n'
    s += circle(ox, oy - h, 4.5, GREEN, GREEN, 0)
    s += text(ox + 8, oy - h - 6, "I₀ = V/R", 13, GREEN, "start", "bold")
    s += text(ox + w * 0.5, oy - h * 0.28, "площа під кривою = увесь заряд Q", 12, GREY, "middle", style="italic")
    save("fig-7-4-4-current-curve.svg", s)


# ── Рис. 7.4.5 — що означає τ = R·C ──────────────────────────────────────────
def fig41_tau_meaning():
    W, H = 720, 420
    s = header(W, H)
    s += text(W / 2, 34, "Стала часу τ = R·C розтягує або стискає криву", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "більший опір або ємність → повільніше заряджання", 12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 110, 350, 540, 250
    s += f'<line x1="{ox}" y1="{oy-h}" x2="{ox+w}" y2="{oy-h}" stroke="{GREY}" stroke-width="1.4" stroke-dasharray="6,5"/>\n'
    s += text(ox + w, oy - h - 8, "V₀", 12.5, GREY, "end", "bold")
    s += _axes(ox, oy, w, h, "час t", "напруга V")
    tmax = 5.0
    curves = [(0.5, RED, "мала τ — швидко"), (1.0, "#9c7b46", "середня τ"),
              (2.2, BLUE, "велика τ — повільно")]
    for tau, col, lab in curves:
        pts = []
        for j in range(0, 101):
            t = tmax * j / 100
            yf = 1 - math.exp(-t / tau)
            x = ox + (t / tmax) * w
            y = oy - yf * h
            pts.append(f"{x:.1f},{y:.1f}")
        s += f'<path d="M {" L ".join(pts)}" fill="none" stroke="{col}" stroke-width="2.6"/>\n'
    s += text(ox + 120, oy - h + 28, "мала τ — швидко", 12.5, RED, "start", "bold")
    s += text(ox + 250, oy - 150, "середня τ", 12.5, "#9c7b46", "start", "bold")
    s += text(ox + 330, oy - 70, "велика τ — повільно", 12.5, BLUE, "start", "bold")
    save("fig-7-4-5-tau-meaning.svg", s)


# ── Рис. 7.4.6 — чому експонента (залишок × 0.37 за крок) ─────────────────────
def fig41_why_exponential():
    W, H = 720, 420
    s = header(W, H)
    s += text(W / 2, 34, "Чому експонента: темп зміни ∝ відстані до мети", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "за кожну сталу часу залишок до мети скорочується на ті самі 63%",
              12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 110, 350, 540, 250
    s += f'<line x1="{ox}" y1="{oy-h}" x2="{ox+w}" y2="{oy-h}" stroke="{GREY}" stroke-width="1.4" stroke-dasharray="6,5"/>\n'
    s += text(ox + w, oy - h - 8, "V₀ (мета)", 12.5, GREY, "end", "bold")
    s += _axes(ox, oy, w, h, "час t", "напруга V")
    s += f'<path d="{exp_path(ox, oy, w, h, "charge")}" fill="none" stroke="{RED}" stroke-width="2.6"/>\n'
    # стовпчики «залишок до мети» в t=0,1,2,3 τ
    for k in range(0, 4):
        x = ox + (k / 5) * w
        yf = 1 - math.exp(-k)
        yc = oy - yf * h
        s += line(x, oy, x, oy + 6, INK, 1.2)
        s += text(x, oy + 22, f"{k}τ", 12, GREY, "middle", "bold")
        s += f'<line x1="{x}" y1="{yc:.1f}" x2="{x}" y2="{oy-h}" stroke="{GREEN}" stroke-width="6" opacity="0.5"/>\n'
        gap = math.exp(-k) * 100
        s += text(x + 12, (yc + (oy - h)) / 2, f"{gap:.0f}%", 11.5, GREEN, "start", "bold")
    s += text(ox + w * 0.55, oy - h * 0.2, "залишок (зелене) × 0.37 щокроку", 12, GREEN, "middle", "bold")
    save("fig-7-4-6-why-exponential.svg", s)


# ── Рис. 7.4.7 — правило 5·τ (таблиця наближення) ────────────────────────────
def fig41_5tau_table():
    W, H = 720, 360
    s = header(W, H)
    s += text(W / 2, 34, "Правило 5·τ: «практично заряджено»", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "за кожну τ закривається 63% залишку; на 5·τ — уже 99%", 12.5, GREY, "middle", style="italic")
    rows = [(1, 63), (2, 86), (3, 95), (4, 98), (5, 99)]
    x0, ytop, barmax = 150, 92, 400
    for i, (k, pct) in enumerate(rows):
        y = ytop + i * 44
        s += text(x0 - 14, y + 16, f"{k}·τ", 13, INK, "end", "bold")
        s += rect(x0, y, barmax, 24, "#eef2f6", "#c9d3dc", 1, 3)
        col = GREEN if k >= 5 else BLUE
        s += rect(x0, y, barmax * pct / 100, 24, "#dbe7f5" if k < 5 else "#e1f0e1", col, 1.6, 3)
        s += text(x0 + barmax * pct / 100 + 10, y + 17, f"{pct}%", 13, col, "start", "bold")
    s += line(x0 + barmax, ytop - 6, x0 + barmax, ytop + len(rows) * 44 - 6, GREY, 1.3, dash="4,4")
    s += text(x0 + barmax, ytop - 12, "100% (мета)", 11.5, GREY, "middle")
    save("fig-7-4-7-5tau-table.svg", s)


# ── Рис. 7.4.8 — RC як затримка/таймер ───────────────────────────────────────
def fig41_rc_timing():
    W, H = 720, 400
    s = header(W, H)
    s += text(W / 2, 34, "RC задає затримку: напруга повзе до порога", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "коли напруга перетне поріг — спрацьовує подія (мерехтіння, скидання, таймер)",
              12.5, GREY, "middle", style="italic")
    ox, oy, w, h = 110, 330, 520, 230
    s += _axes(ox, oy, w, h, "час t", "напруга V")
    s += f'<line x1="{ox}" y1="{oy-h}" x2="{ox+w}" y2="{oy-h}" stroke="{GREY}" stroke-width="1.2" stroke-dasharray="6,5"/>\n'
    s += text(ox + w, oy - h - 8, "V₀", 12, GREY, "end")
    # поріг
    thr = 0.66
    yt = oy - thr * h
    s += f'<line x1="{ox}" y1="{yt:.1f}" x2="{ox+w}" y2="{yt:.1f}" stroke="{GREEN}" stroke-width="1.8" stroke-dasharray="7,4"/>\n'
    s += text(ox + w, yt - 8, "поріг", 12.5, GREEN, "end", "bold")
    # крива заряджання
    s += f'<path d="{exp_path(ox, oy, w, h, "charge")}" fill="none" stroke="{RED}" stroke-width="2.6"/>\n'
    # момент перетину порога: 1-e^{-t}=thr -> t=-ln(1-thr)
    tc = -math.log(1 - thr)
    xc = ox + (tc / 5) * w
    s += line(xc, oy, xc, yt, INK, 1.4, dash="4,4")
    s += circle(xc, yt, 4.5, GREEN, GREEN, 0)
    s += arrow(ox, oy + 30, xc, oy + 30, INK, 1.8)
    s += text((ox + xc) / 2, oy + 26, "затримка", 12, INK, "middle", "bold")
    # LED off → on
    s += circle(ox + 70, oy - h - 0 + 0, 0, "none", "none", 0)  # placeholder
    s += text(xc + 60, yt - 30, "→ спрацювало", 12.5, GREEN, "start", "bold")
    s += text(W / 2, H - 18, "інші R·C — інша затримка: той самий важіль τ = R·C.", 12, GREY, "middle", style="italic")
    save("fig-7-4-8-rc-timing.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §7.5 — будівельники
# ─────────────────────────────────────────────────────────────────────────────
def inductor_h(x1, x2, y, label="L", col=INK):
    n = 4
    seg = (x2 - x1) / n
    s = ""
    for i in range(n):
        xa = x1 + seg * i
        xb = x1 + seg * (i + 1)
        s += f'<path d="M {xa:.1f},{y:.1f} A {seg/2:.1f} {seg/2:.1f} 0 0 1 {xb:.1f},{y:.1f}" fill="none" stroke="{col}" stroke-width="2"/>\n'
    if label:
        s += text((x1 + x2) / 2, y - 13, label, 13, INK, "middle", "bold")
    return s


def cap_sym(cx, cy, half=16, gap=9, col=INK):
    """Схемний символ неполярного конденсатора (дві вертикальні риски). Повертає (svg, lx, rx)."""
    s = line(cx - gap / 2, cy - half, cx - gap / 2, cy + half, col, 2.6)
    s += line(cx + gap / 2, cy - half, cx + gap / 2, cy + half, col, 2.6)
    return s, cx - gap / 2, cx + gap / 2


def cap_sym_polar(cx, cy, half=16, gap=9):
    """Полярний (електролітичний): пряма + зігнута обкладка, знак +. Повертає (svg, lx, rx)."""
    s = line(cx - gap / 2, cy - half, cx - gap / 2, cy + half, INK, 2.6)
    s += f'<path d="M {cx+gap/2+4:.1f},{cy-half:.1f} Q {cx+gap/2+13:.1f},{cy:.1f} {cx+gap/2+4:.1f},{cy+half:.1f}" fill="none" stroke="{INK}" stroke-width="2.6"/>\n'
    s += plus(cx - gap / 2 - 12, cy - half - 2, 5, RED, 1.6)
    return s, cx - gap / 2, cx + gap / 2 + 8


def boom(cx, cy, r=26, col=RED):
    s = ""
    for a in range(0, 360, 30):
        x2 = cx + r * math.cos(math.radians(a))
        y2 = cy + r * math.sin(math.radians(a))
        s += line(cx, cy, x2, y2, col, 2)
    s += text(cx, cy + 5, "БАХ", 13, col, "middle", "bold")
    return s


def heatwaves(cx, cy, col=RED):
    s = ""
    for k in range(3):
        xx = cx + (k - 1) * 16
        s += f'<path d="M {xx:.1f},{cy:.1f} q 5,-10 10,0 q 5,10 10,0" fill="none" stroke="{col}" stroke-width="1.8"/>\n'
    return s


# ── Рис. 7.5.1 — реальна модель конденсатора ─────────────────────────────────
def fig51_real_model():
    W, H = 720, 430
    s = header(W, H)
    s += text(W / 2, 34, "Реальний конденсатор = ідеальна ємність плюс паразити", 19, INK, "middle", "bold")
    # ідеальний (зверху)
    s += text(W / 2, 86, "ідеальний: сама ємність C", 13.5, GREY, "middle", "bold")
    s += line(150, 120, 330, 120, INK, 2.4)
    cs, lx, rx = cap_sym(360, 120, 18, 10)
    s += line(330, 120, lx, 120, INK, 2.4)
    s += cs
    s += line(rx, 120, 570, 120, INK, 2.4)
    s += text(360, 156, "C", 14, INK, "middle", "bold")
    # реальний (знизу)
    s += text(W / 2, 210, "реальний: C + ESR + ESL + витік", 14, INK, "middle", "bold")
    yb = 260
    s += line(90, yb, 140, yb, INK, 2.4)
    s += inductor_h(140, 220, yb, "ESL")
    s += line(220, yb, 250, yb, INK, 2.4)
    s += resistor_h(250, 330, yb, "ESR")
    s += line(330, yb, 372, yb, INK, 2.4)
    cs2, lx2, rx2 = cap_sym(390, yb, 18, 10)
    s += cs2
    s += text(390, yb + 36, "C", 13, INK, "middle", "bold")
    s += line(rx2, yb, 630, yb, INK, 2.4)
    # паралельний витік
    s += line(120, yb, 120, yb + 70, GREY, 2)
    s += line(600, yb, 600, yb + 70, GREY, 2)
    s += resistor_h(300, 420, yb + 70, "витік", GREY)
    s += line(120, yb + 70, 300, yb + 70, GREY, 2)
    s += line(420, yb + 70, 600, yb + 70, GREY, 2)
    s += text(360, yb + 102, "опір витоку (дуже великий)", 11.5, GREY, "middle", style="italic")
    s += rect(60, H - 40, W - 120, 28, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 21, "На низьких частотах паразитами нехтують; на швидкості, нагріві й точності — вони головні.",
              11.5, INK, "middle", "bold")
    save("fig-7-5-1-real-model.svg", s)


# ── Рис. 7.5.2 — основні типи ────────────────────────────────────────────────
def fig51_types():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 34, "Чотири головні типи конденсаторів", 20, INK, "middle", "bold")
    cards = [
        ("Керамічний", "#fdeecf", ["пФ…десятки мкФ", "неполярний", "малий ESR/ESL", "клас 2 «пливе»", "розв'язка, ВЧ"]),
        ("Електролітичний", "#dbe7f5", ["мкФ…мФ", "ПОЛЯРНИЙ", "великий ESR", "обмежений ресурс", "накопичення"]),
        ("Танталовий", "#e7f0e0", ["мкФ, компактний", "ПОЛЯРНИЙ", "стабільний", "боїться перенапруги", "живлення"]),
        ("Плівковий", "#f3dede", ["нФ…мкФ", "неполярний", "малі втрати", "більший розмір", "точність, ВН"]),
    ]
    for i, (name, col, traits) in enumerate(cards):
        x = 30 + i * 195
        s += rect(x, 70, 180, 320, col, "#b9b9bf", 1.4, 12)
        s += text(x + 90, 98, name, 14.5, INK, "middle", "bold")
        # піктограма
        if "олярний" in "".join(traits) or name in ("Електролітичний", "Танталовий"):
            cs, lx, rx = cap_sym_polar(x + 90, 138, 16, 10)
        else:
            cs, lx, rx = cap_sym(x + 90, 138, 16, 10)
        s += line(lx - 18, 138, lx, 138, INK, 2)
        s += line(rx, 138, rx + 18, 138, INK, 2)
        s += cs
        for j, tr in enumerate(traits):
            y = 184 + j * 36
            bold = "bold" if tr.isupper() or "ПОЛЯРНИЙ" in tr else "normal"
            colr = RED if "ПОЛЯРНИЙ" in tr or "боїться" in tr else INK
            s += text(x + 90, y, tr, 12, colr, "middle", bold)
    save("fig-7-5-2-types.svg", s)


# ── Рис. 7.5.3 — ESR гріється ────────────────────────────────────────────────
def fig51_esr():
    W, H = 720, 360
    s = header(W, H)
    s += text(W / 2, 34, "ESR: послідовний опір, що гріється від струму", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "пульсівний струм крізь ESR виділяє тепло P = I²·ESR", 12.5, GREY, "middle", style="italic")
    y = 200
    s += line(120, y, 220, y, INK, 2.4)
    s += resistor_h(220, 320, y, "ESR", RED)
    s += line(320, y, 372, y, INK, 2.4)
    cs, lx, rx = cap_sym(390, y, 20, 11)
    s += cs
    s += text(390, y + 40, "C", 13, INK, "middle", "bold")
    s += line(rx, y, 600, y, INK, 2.4)
    # пульсівний струм
    s += arrow(140, y - 30, 200, y - 30, INK, 2.2)
    s += text(170, y - 40, "пульсівний струм", 11.5, INK, "middle", "bold")
    # тепло на ESR
    s += heatwaves(270, y - 26, RED)
    s += text(270, y - 40, "тепло", 11.5, RED, "middle", "bold")
    s += rect(60, H - 56, W - 120, 40, "#fdeded", RED, 1.4, 8)
    s += text(W / 2, H - 38, "Низький ESR — критично для живлення: інакше конденсатор гріється, втрачає ємність,",
              11.5, INK, "middle", "bold")
    s += text(W / 2, H - 22, "висихає й «здувається». Звідси позначка Low-ESR.", 11.5, INK, "middle", "bold")
    save("fig-7-5-3-esr.svg", s)


# ── Рис. 7.5.4 — ESL виводів ─────────────────────────────────────────────────
def fig51_esl():
    W, H = 720, 360
    s = header(W, H)
    s += text(W / 2, 34, "ESL: індуктивність виводів заважає на високих частотах", 18, INK, "middle", "bold")
    # довгі виводи — погано
    s += rect(40, 80, 320, 230, "none", FAINT, 1.6, 12)
    s += text(200, 106, "довгі виводи — погано", 13, RED, "middle", "bold")
    cs, lx, rx = cap_sym(200, 190, 22, 12)
    s += cs
    s += inductor_h(90, 188, 190, "", RED)
    s += inductor_h(212, 310, 190, "", RED)
    s += line(60, 190, 90, 190, INK, 2.2)
    s += line(310, 190, 340, 190, INK, 2.2)
    s += text(200, 250, "велика ESL на фронтах", 11.5, RED, "middle", "bold")
    # короткі — добре
    s += rect(400, 80, 280, 230, "none", FAINT, 1.6, 12)
    s += text(540, 106, "короткі виводи — добре", 13, GREEN, "middle", "bold")
    cs2, lx2, rx2 = cap_sym(540, 190, 22, 12)
    s += cs2
    s += line(500, 190, lx2, 190, INK, 2.2)
    s += line(rx2, 190, 580, 190, INK, 2.2)
    s += text(540, 250, "мала ESL — конденсатор ближче до ідеалу", 11, GREEN, "middle", "bold")
    s += text(W / 2, H - 28, "Що таке індуктивність — Розділ 8; поведінка з частотою — Розділ 9.",
              12, GREY, "middle", style="italic")
    save("fig-7-5-4-esl.svg", s)


# ── Рис. 7.5.5 — гранична напруга й пробій ───────────────────────────────────
def fig51_voltage_breakdown():
    W, H = 760, 400
    s = header(W, H)
    s += text(W / 2, 34, "Гранична напруга: вище за межу — пробій діелектрика", 19, INK, "middle", "bold")
    # OK
    s += rect(40, 78, 330, 200, "none", FAINT, 1.6, 12)
    s += text(205, 104, "V < гранична — діелектрик тримає", 12.5, GREEN, "middle", "bold")
    cx, cy = 205, 180
    plL, c = cap_plates(cx, cy, ph=90, gap=46, pt=12, lfill="#f7dada", lstroke=RED, rfill="#dbe3f7", rstroke=BLUE)
    s += rect(c["li"], cy - 45, c["ri"] - c["li"], 90, "#f3efe6", "none", 0)
    s += plL
    s += text(205, 250, "OK", 14, GREEN, "middle", "bold")
    # breakdown
    s += rect(400, 78, 330, 200, "none", FAINT, 1.6, 12)
    s += text(565, 104, "V > гранична — ПРОБІЙ", 12.5, RED, "middle", "bold")
    cx2 = 565
    plR, c2 = cap_plates(cx2, cy, ph=90, gap=46, pt=12, lfill="#f7dada", lstroke=RED, rfill="#dbe3f7", rstroke=BLUE)
    s += rect(c2["li"], cy - 45, c2["ri"] - c2["li"], 90, "#f3efe6", "none", 0)
    s += plR
    # іскра пробою крізь діелектрик
    s += line(c2["li"], cy, cx2, cy - 14, RED, 2.4)
    s += line(cx2, cy - 14, cx2 - 6, cy + 6, RED, 2.4)
    s += line(cx2 - 6, cy + 6, c2["ri"], cy, RED, 2.4)
    s += text(565, 250, "канал пробою → коротке", 11.5, RED, "middle", "bold")
    # дерейтинг
    s += rect(60, 300, W - 120, 78, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 324, "Дерейтинг: робоча напруга помітно нижча за номінальну (часто вдвічі).",
              12.5, INK, "middle", "bold")
    s += line(120, 352, 360, 352, GREEN, 8)
    s += line(120, 352, 640, 352, GREY, 2)
    s += text(118, 372, "робоча", 11, GREEN, "start", "bold")
    s += text(642, 372, "номінальна (межа)", 11, GREY, "end", "bold")
    save("fig-7-5-5-voltage-rating-breakdown.svg", s)


# ── Рис. 7.5.6 — полярність ──────────────────────────────────────────────────
def fig51_polarity():
    W, H = 760, 360
    s = header(W, H)
    s += text(W / 2, 34, "Полярний конденсатор: лише в один бік", 20, INK, "middle", "bold")
    # правильно
    s += rect(40, 78, 330, 220, "none", FAINT, 1.6, 12)
    s += text(205, 104, "правильно: + до +", 13, GREEN, "middle", "bold")
    cs, lx, rx = cap_sym_polar(205, 180, 26, 12)
    s += plus(150, 150, 8, RED, 2)
    s += minus(265, 150, 8, BLUE, 2)
    s += line(120, 180, lx, 180, INK, 2.2)
    s += line(rx, 180, 290, 180, INK, 2.2)
    s += cs
    s += text(205, 250, "оксид тримається — працює", 12, GREEN, "middle", "bold")
    # навпаки
    s += rect(400, 78, 330, 220, "none", FAINT, 1.6, 12)
    s += text(565, 104, "навпаки: + до −", 13, RED, "middle", "bold")
    cs2, lx2, rx2 = cap_sym_polar(540, 180, 26, 12)
    s += minus(485, 150, 8, BLUE, 2)
    s += plus(620, 150, 8, RED, 2)
    s += line(455, 180, lx2, 180, INK, 2.2)
    s += line(rx2, 180, 600, 180, INK, 2.2)
    s += cs2
    s += boom(545, 180, 30, RED)
    s += text(565, 256, "оксид руйнується — роздування/вибух", 11.5, RED, "middle", "bold")
    s += text(W / 2, H - 24, "Неполярні (кераміка, плівка) — будь-яким боком; полярні — тільки за маркуванням.",
              12, GREY, "middle", style="italic")
    save("fig-7-5-6-polarity.svg", s)


# ── Рис. 7.5.7 — витік, дрейф, допуск ────────────────────────────────────────
def fig51_leakage_coeff():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "«10 мкФ» — лише орієнтир: витік, дрейф, допуск", 19, INK, "middle", "bold")
    # (a) витік — саморозряд
    s += rect(30, 70, 250, 250, "none", FAINT, 1.6, 12)
    s += text(155, 96, "витік → саморозряд", 12.5, INK, "middle", "bold")
    ox, oy, w, h = 60, 280, 180, 150
    s += _axes(ox, oy, w, h, "t", "V")
    s += f'<path d="{exp_path(ox, oy, w, h, "discharge", 5)}" fill="none" stroke="{BLUE}" stroke-width="2.4"/>\n'
    s += text(155, 308, "повільно сам розряджається (§7.4)", 10.5, GREY, "middle", style="italic")
    # (b) дрейф ємності з напругою
    s += rect(296, 70, 250, 250, "none", FAINT, 1.6, 12)
    s += text(421, 96, "кераміка класу 2 «пливе»", 12, INK, "middle", "bold")
    ox2, oy2, w2, h2 = 326, 280, 180, 150
    s += _axes(ox2, oy2, w2, h2, "V", "C")
    pts = []
    for j in range(0, 101):
        v = j / 100
        cf = 1 - 0.45 * v * v
        x = ox2 + v * w2
        yv = oy2 - cf * h2
        pts.append(f"{x:.1f},{yv:.1f}")
    s += f'<path d="M {" L ".join(pts)}" fill="none" stroke="{RED}" stroke-width="2.4"/>\n'
    s += text(421, 308, "ємність падає з напругою й нагрівом", 10.5, GREY, "middle", style="italic")
    # (c) допуск
    s += rect(562, 70, 228, 250, "none", FAINT, 1.6, 12)
    s += text(676, 96, "допуск ±20%", 12.5, INK, "middle", "bold")
    cx3 = 676
    s += line(cx3, 140, cx3, 280, GREY, 1.4)
    s += rect(cx3 - 60, 180, 120, 60, "#e1f0e1", GREEN, 1.6, 6)
    s += text(cx3, 170, "номінал", 11, INK, "middle", "bold")
    s += text(cx3, 215, "10 мкФ", 14, INK, "middle", "bold")
    s += text(cx3 - 66, 235, "8", 11, GREY, "end")
    s += text(cx3 + 66, 235, "12", 11, GREY, "start")
    s += text(676, 308, "реальна ємність гуляє в межах", 10.5, GREY, "middle", style="italic")
    save("fig-7-5-7-leakage-coeff.svg", s)


# ── Рис. 7.5.8 — як обрати конденсатор ───────────────────────────────────────
def fig51_choose():
    W, H = 760, 300
    s = header(W, H)
    s += text(W / 2, 36, "Як обрати конденсатор: три кроки", 20, INK, "middle", "bold")
    steps = [("1. ЄМНІСТЬ", "скільки фарад потрібно", "#fdeecf"),
             ("2. НАПРУГА", "гранична — із запасом\nнад робочою", "#dbe7f5"),
             ("3. ТИП", "кераміка / електроліт /\nплівка — під задачу", "#e1f0e1")]
    for i, (t, d, col) in enumerate(steps):
        x = 60 + i * 230
        s += rect(x, 80, 190, 130, col, "#b9b9bf", 1.6, 12)
        s += text(x + 95, 116, t, 15, INK, "middle", "bold")
        for j, ln in enumerate(d.split("\n")):
            s += text(x + 95, 146 + j * 20, ln, 12, INK, "middle")
        if i < 2:
            s += arrow(x + 192, 145, x + 228, 145, INK, 2.4)
    s += text(W / 2, 250, "+ паразити (ESR/ESL) — для швидких і силових кіл",
              12.5, GREY, "middle", style="italic")
    save("fig-7-5-8-choose.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §7.6 — будівельники
# ─────────────────────────────────────────────────────────────────────────────
def _frame(x, y, w, h, title=""):
    s = rect(x, y, w, h, "#ffffff", "#c9d3dc", 1.4, 6)
    if title:
        s += text(x + w / 2, y - 6, title, 12, INK, "middle", "bold")
    return s


def _poly(pts, col, wv=2.4, fill="none"):
    return f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{fill}" stroke="{col}" stroke-width="{wv}"/>\n'


# ── Рис. 7.6.1 — властивості → ролі ──────────────────────────────────────────
def fig61_roles_overview():
    W, H = 820, 430
    s = header(W, H)
    s += text(W / 2, 34, "Одна деталь — багато робіт", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "кожне застосування конденсатора — грань уже відомої фізики (теми 7.1–7.4)",
              12.5, GREY, "middle", style="italic")
    props = ["тримає й віддає\nзаряд миттєво", "повільно\nрозряджається",
             "блокує постійне,\nпропускає зміну", "RC задає\nсталу часу τ"]
    roles = ["розв'язка", "накопичувач", "згладжування", "AC-зв'язок", "відлік часу"]
    py = [110, 190, 270, 350]
    ry = [98, 168, 238, 308, 378]
    lx, rx = 60, 600
    for i, p in enumerate(props):
        s += rect(lx, py[i] - 28, 210, 56, "#eef2f6", "#9bb0c2", 1.5, 8)
        for j, ln in enumerate(p.split("\n")):
            s += text(lx + 105, py[i] - 6 + j * 18, ln, 12.5, INK, "middle", "bold")
    for i, r in enumerate(roles):
        s += rect(rx, ry[i] - 22, 180, 44, "#eef6ef", GREEN, 1.6, 8)
        s += text(rx + 90, ry[i] + 5, r, 13.5, INK, "middle", "bold")
    links = [(0, 0), (0, 1), (1, 2), (2, 3), (3, 4)]
    for pi, ri in links:
        s += line(lx + 210, py[pi], rx, ry[ri], GREY, 1.6)
    save("fig-7-6-1-roles-overview.svg", s)


# ── Рис. 7.6.2 — розв'язка ───────────────────────────────────────────────────
def fig61_decoupling():
    W, H = 820, 440
    s = header(W, H)
    s += text(W / 2, 34, "Розв'язка: локальний запас тримає напругу під час ривка струму", 18, INK, "middle", "bold")
    # схема зверху
    bat, bt, bb = battery(110, 150)
    s += bat
    s += text(110, 196, "живлення", 11.5, INK, "middle")
    s += line(bt[0], bt[1], 110, 110, INK, 2.2)
    s += resistor_h(150, 300, 110, "опір доріжки")
    s += line(300, 110, 470, 110, INK, 2.2)
    # вузол + конденсатор до землі
    cs, lxc, rxc = cap_sym(470, 145, 18, 10)
    s += line(470, 110, 470, 127, INK, 2.2)
    s += cs
    s += line(470, 163, 470, 195, INK, 2.2)
    s += text(500, 150, "C розв'язки", 11.5, GREEN, "start", "bold")
    # чип
    s += rect(560, 80, 90, 70, "#eef2f6", INK, 1.8, 6)
    s += text(605, 120, "чип", 14, INK, "middle", "bold")
    s += line(470, 110, 560, 110, INK, 2.2)
    s += arrow(605, 152, 605, 185, RED, 2.4)
    s += text(640, 172, "ривок струму", 11, RED, "start", "bold")
    # земля
    s += line(110, 195, 605, 195, INK, 2.2)
    s += line(605, 150, 605, 195, INK, 2.2)
    # дві осцилограми
    s += _frame(70, 250, 320, 150, "без конденсатора")
    ox, oy, w, h = 90, 380, 280, 110
    s += line(ox, oy - h, ox, oy, GREY, 1)
    s += line(ox, oy - h * 0.7, ox + 120, oy - h * 0.7, RED, 2.4)
    s += _poly([(ox + 120, oy - h * 0.7), (ox + 135, oy - h * 0.18), (ox + 165, oy - h * 0.18),
                (ox + 180, oy - h * 0.7), (ox + 280, oy - h * 0.7)], RED)
    s += text(ox + 150, oy - h * 0.06, "провал!", 11, RED, "middle", "bold")
    s += _frame(430, 250, 320, 150, "з конденсатором")
    ox2 = 450
    s += line(ox2, oy - h, ox2, oy, GREY, 1)
    s += _poly([(ox2, oy - h * 0.7), (ox2 + 120, oy - h * 0.7), (ox2 + 135, oy - h * 0.62),
                (ox2 + 165, oy - h * 0.62), (ox2 + 180, oy - h * 0.7), (ox2 + 280, oy - h * 0.7)], GREEN)
    s += text(ox2 + 150, oy - h * 0.95, "напруга тримається", 11, GREEN, "middle", "bold")
    save("fig-7-6-2-decoupling.svg", s)


# ── Рис. 7.6.3 — розташування розв'язки ──────────────────────────────────────
def fig61_decoupling_placement():
    W, H = 760, 330
    s = header(W, H)
    s += text(W / 2, 34, "Розв'язку ставлять упритул до мікросхеми", 19, INK, "middle", "bold")
    # добре
    s += _frame(40, 80, 330, 200, "")
    s += text(205, 104, "близько — добре", 13, GREEN, "middle", "bold")
    s += rect(120, 150, 80, 60, "#eef2f6", INK, 1.8, 6)
    s += text(160, 185, "чип", 13, INK, "middle", "bold")
    cs, lx, rx = cap_sym(240, 180, 16, 9)
    s += line(200, 165, 232, 165, INK, 2.2)
    s += line(232, 165, 232, 168, INK, 2.2)
    s += cs
    s += text(240, 224, "коротка доріжка", 11, GREEN, "middle", "bold")
    s += text(240, 240, "мала ESL", 10.5, GREY, "middle", style="italic")
    # погано
    s += _frame(400, 80, 330, 200, "")
    s += text(565, 104, "далеко — погано", 13, RED, "middle", "bold")
    s += rect(440, 150, 80, 60, "#eef2f6", INK, 1.8, 6)
    s += text(480, 185, "чип", 13, INK, "middle", "bold")
    cs2, lx2, rx2 = cap_sym(680, 180, 16, 9)
    s += _poly([(520, 165), (560, 165), (560, 200), (620, 200), (620, 165), (lx2, 165)], INK, 2.2)
    s += cs2
    s += text(620, 230, "довга доріжка → ESL", 11, RED, "middle", "bold")
    s += text(W / 2, H - 18, "Правило: своя кераміка ~100 нФ на кожну мікросхему, упритул.", 12, GREY, "middle", style="italic")
    save("fig-7-6-3-decoupling-placement.svg", s)


# ── Рис. 7.6.4 — згладжування ────────────────────────────────────────────────
def fig61_smoothing():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Згладжування: конденсатор засипає провали пульсівної напруги", 18, INK, "middle", "bold")
    # вхід — горби
    s += _frame(40, 80, 300, 200, "пульсівна напруга (вхід)")
    ox, oy, w, h = 60, 250, 260, 150
    s += line(ox, oy, ox + w, oy, GREY, 1)
    pts = []
    for j in range(0, 261):
        x = ox + j
        v = abs(math.sin(j / 260 * math.pi * 4))
        pts.append((x, oy - v * h * 0.9))
    s += _poly(pts, GREY, 2)
    # конденсатор
    cs, lx, rx = cap_sym(410, 160, 22, 12)
    s += line(360, 130, 410 - 6, 130, INK, 2.2)
    s += line(410 - 6, 130, 410 - 6, 138, INK, 2.2)
    s += cs
    s += line(410 - 6, 182, 410 - 6, 210, INK, 2.2)
    s += text(410, 235, "C", 13, INK, "middle", "bold")
    s += arrow(360, 130, 470, 130, INK, 2.2)
    # вихід — гладко
    s += _frame(490, 80, 290, 200, "згладжена напруга (вихід)")
    ox2 = 510
    s += line(ox2, oy, ox2 + 250, oy, GREY, 1)
    pts2 = []
    for j in range(0, 251):
        x = ox2 + j
        ripple = 0.04 * abs(math.sin(j / 250 * math.pi * 4))
        pts2.append((x, oy - (0.82 - ripple) * h))
    s += _poly(pts2, GREEN, 2.4)
    s += text(ox2 + 125, oy - 0.95 * h, "майже рівно (мала пульсація)", 11, GREEN, "middle", "bold")
    save("fig-7-6-4-smoothing.svg", s)


# ── Рис. 7.6.5 — накопичувач (пережити провал) ───────────────────────────────
def fig61_reservoir():
    W, H = 740, 380
    s = header(W, H)
    s += text(W / 2, 34, "Накопичувач: тримати навантаження під час провалу живлення", 18, INK, "middle", "bold")
    ox, oy, w, h = 100, 320, 540, 230
    s += _axes(ox, oy, w, h, "час t", "напруга")
    # джерело: рівне, потім провал до 0, потім назад
    s += _poly([(ox, oy - h * 0.85), (ox + 180, oy - h * 0.85), (ox + 180, oy - 4),
                (ox + 320, oy - 4), (ox + 320, oy - h * 0.85), (ox + w, oy - h * 0.85)],
               GREY, 2, "none")
    s += text(ox + 250, oy - 18, "джерело зникло", 11.5, GREY, "middle", style="italic")
    # навантаження з конденсатором: тримається, повільно сідає під час провалу
    load = [(ox, oy - h * 0.82), (ox + 180, oy - h * 0.82)]
    for j in range(0, 141):
        t = j / 140 * 1.6
        x = ox + 180 + (j / 140) * 140
        v = 0.82 * math.exp(-t)
        load.append((x, oy - v * h))
    load.append((ox + 320, oy - h * 0.82))
    load.append((ox + w, oy - h * 0.82))
    s += _poly(load, GREEN, 2.6)
    s += text(ox + 250, oy - h * 0.62, "конденсатор тримає", 11.5, GREEN, "middle", "bold")
    s += text(ox + 250, oy - h * 0.5, "навантаження живленим", 11.5, GREEN, "middle", "bold")
    s += text(ox + w * 0.78, oy - h * 0.9, "живлення повернулось", 11, INK, "middle", style="italic")
    save("fig-7-6-5-reservoir.svg", s)


# ── Рис. 7.6.6 — AC-зв'язок ──────────────────────────────────────────────────
def fig61_ac_coupling():
    W, H = 820, 360
    s = header(W, H)
    s += text(W / 2, 34, "Розділовий конденсатор: пропустити змінне, відсікти постійне", 18, INK, "middle", "bold")
    # вхід: синус на зміщенні
    s += _frame(40, 80, 300, 220, "вхід: сигнал на зміщенні")
    ox, oy, w, h = 60, 290, 260, 200
    base_in = oy - h * 0.62
    s += line(ox, base_in, ox + w, base_in, GREY, 1.2, )
    s += text(ox + w, base_in - 4, "зміщення", 10.5, GREY, "end")
    pts = [(ox + j, base_in - 0.22 * h * math.sin(j / 260 * math.pi * 4)) for j in range(0, 261)]
    s += _poly(pts, INK, 2.2)
    # конденсатор послідовно
    cs, lx, rx = cap_sym(410, 150, 20, 11)
    s += line(360, 150, lx, 150, INK, 2.2)
    s += cs
    s += arrow(rx, 150, 480, 150, INK, 2.2)
    s += text(410, 120, "C", 13, INK, "middle", "bold")
    s += text(410, 186, "послідовно", 10.5, GREY, "middle", style="italic")
    # вихід: синус навколо нуля
    s += _frame(490, 80, 300, 220, "вихід: навколо нуля")
    ox2 = 510
    base_out = oy - h * 0.32
    s += line(ox2, base_out, ox2 + w, base_out, GREEN, 1.4, dash="5,4")
    s += text(ox2 + w, base_out + 14, "0", 11, GREEN, "end", "bold")
    pts2 = [(ox2 + j, base_out - 0.22 * h * math.sin(j / 260 * math.pi * 4)) for j in range(0, 261)]
    s += _poly(pts2, GREEN, 2.4)
    save("fig-7-6-6-ac-coupling.svg", s)


# ── Рис. 7.6.7 — відлік часу ─────────────────────────────────────────────────
def fig61_timing():
    W, H = 760, 320
    s = header(W, H)
    s += text(W / 2, 34, "Відлік часу: та сама τ = R·C на службі", 19, INK, "middle", "bold")
    apps = [("мерехтіння / затримка", "заряд до порога → подія"),
            ("антидребезг кнопки", "RC згладжує брязкіт"),
            ("скидання при ввімкненні", "тримає reset, поки встане живлення")]
    for i, (t, d) in enumerate(apps):
        x = 40 + i * 240
        s += _frame(x, 80, 220, 170, "")
        # мінікоо: R + C
        s += line(x + 30, 130, x + 60, 130, INK, 2)
        s += resistor_h(x + 60, x + 120, 130, "R")
        cs, lx, rx = cap_sym(x + 140, 150, 16, 9)
        s += line(x + 120, 130, x + 134, 130, INK, 2)
        s += line(x + 134, 130, x + 134, 134, INK, 2)
        s += cs
        s += line(x + 134, 166, x + 134, 180, INK, 2)
        s += line(x + 30, 180, x + 134, 180, INK, 2)
        s += line(x + 30, 130, x + 30, 180, INK, 2)
        s += text(x + 110, 210, t, 12, INK, "middle", "bold")
        s += text(x + 110, 230, d, 10.5, GREY, "middle", style="italic")
    s += text(W / 2, H - 16, "Цінують передбачуваність заряджання: знаєш τ — знаєш час.", 12, GREY, "middle", style="italic")
    save("fig-7-6-7-timing.svg", s)


# ── Рис. 7.6.8 — карта конденсаторів на платі ────────────────────────────────
def fig61_board_map():
    W, H = 820, 420
    s = header(W, H)
    s += text(W / 2, 34, "Хто є хто: конденсатори на типовій платі", 19, INK, "middle", "bold")
    s += rect(50, 70, 720, 320, "#f7f7f4", "#b9b9bf", 2, 12)
    # роз'єм живлення + великий електроліт
    s += rect(70, 200, 36, 60, "#eceae2", INK, 1.6, 4)
    s += text(88, 280, "живлення", 10.5, INK, "middle")
    cs, lx, rx = cap_sym_polar(150, 230, 26, 12)
    s += line(106, 230, lx, 230, INK, 2)
    s += cs
    s += line(rx, 230, 200, 230, INK, 2)
    s += text(150, 290, "великий електроліт →", 10.5, INK, "middle", "bold")
    s += text(150, 305, "ЗГЛАДЖУВАННЯ", 11, RED, "middle", "bold")
    # два чипи з розв'язкою
    for k, cx in enumerate((330, 470)):
        s += rect(cx - 35, 120, 70, 55, "#eef2f6", INK, 1.6, 6)
        s += text(cx, 152, "чип", 12, INK, "middle", "bold")
        c2, l2, r2 = cap_sym(cx + 55, 150, 13, 7)
        s += line(cx + 35, 147, cx + 49, 147, INK, 1.8)
        s += c2
    s += text(400, 100, "дрібна кераміка 100 нФ біля кожного чипа = РОЗВ'ЯЗКА", 10.5, GREEN, "middle", "bold")
    # накопичувач біля ненажерливого вузла
    s += rect(330, 250, 90, 50, "#fdeded", INK, 1.6, 6)
    s += text(375, 280, "радіо / мотор", 10.5, INK, "middle", "bold")
    cs3, l3, r3 = cap_sym_polar(470, 275, 20, 11)
    s += line(420, 275, l3, 275, INK, 2)
    s += cs3
    s += text(500, 270, "← НАКОПИЧУВАЧ", 10.5, RED, "start", "bold")
    # розділовий у сигнальному шляху
    s += line(560, 150, 600, 150, INK, 2)
    cs4, l4, r4 = cap_sym(612, 150, 14, 8)
    s += cs4
    s += arrow(r4, 150, 700, 150, INK, 2)
    s += text(630, 128, "AC-ЗВ'ЯЗОК", 10.5, BLUE, "middle", "bold")
    s += text(630, 175, "(сигнал)", 10, GREY, "middle", style="italic")
    # RC біля МК
    s += line(560, 320, 590, 320, INK, 2)
    s += resistor_h(590, 640, 320, "R")
    cs5, l5, r5 = cap_sym(656, 332, 13, 7)
    s += line(640, 320, 650, 320, INK, 2)
    s += line(650, 320, 650, 325, INK, 2)
    s += cs5
    s += text(620, 360, "RC → ВІДЛІК ЧАСУ", 10.5, "#9c7b46", "middle", "bold")
    save("fig-7-6-8-board-map.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
#  §7.7 — будівельники
# ─────────────────────────────────────────────────────────────────────────────
def cap_sym_v(cx, cy, half=15, gap=9, col=INK):
    """Символ конденсатора з горизонтальними обкладками (для вертикальних гілок)."""
    s = line(cx - half, cy - gap / 2, cx + half, cy - gap / 2, col, 2.6)
    s += line(cx - half, cy + gap / 2, cx + half, cy + gap / 2, col, 2.6)
    return s, cy - gap / 2, cy + gap / 2


# ── Рис. 7.7.1 — паралельне з'єднання ────────────────────────────────────────
def fig71_parallel():
    W, H = 700, 380
    s = header(W, H)
    s += text(W / 2, 34, "Паралельно: ємності додаються", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "спільна напруга, заряди складаються", 12.5, GREY, "middle", style="italic")
    yt, yb = 140, 270
    xL, xR = 180, 420
    s += line(xL, yt, xR, yt, INK, 2.6)
    s += line(xL, yb, xR, yb, INK, 2.6)
    for cx, lab in [(250, "C₁"), (350, "C₂")]:
        cs, ty, by = cap_sym_v(cx, (yt + yb) / 2)
        s += line(cx, yt, cx, ty, INK, 2.2)
        s += line(cx, by, cx, yb, INK, 2.2)
        s += cs
        s += text(cx + 26, (yt + yb) / 2 + 4, lab, 13, INK, "start", "bold")
    # напруга
    s += line(xL, yt, xL - 30, yt, INK, 2.2)
    s += line(xL, yb, xL - 30, yb, INK, 2.2)
    s += arrow(xL - 30, yt, xL - 30, yb, BLUE, 2)
    s += text(xL - 38, (yt + yb) / 2, "V", 14, BLUE, "end", "bold")
    s += text(xL - 38, (yt + yb) / 2 + 18, "спільна", 10.5, GREY, "end")
    # результат
    s += rect(470, 150, 200, 110, "#eef6ef", GREEN, 1.6, 10)
    s += text(570, 188, "C = C₁ + C₂", 18, INK, "middle", "bold")
    s += text(570, 220, "заряди додаються", 12, GREY, "middle", style="italic")
    s += text(570, 240, "Q = Q₁ + Q₂", 13, INK, "middle", "bold")
    save("fig-7-7-1-parallel.svg", s)


# ── Рис. 7.7.2 — послідовне з'єднання ────────────────────────────────────────
def fig71_series():
    W, H = 720, 360
    s = header(W, H)
    s += text(W / 2, 34, "Послідовно: додаються обернені ємності", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "спільний заряд, напруги складаються — разом менше за найменшу", 12.5, GREY, "middle", style="italic")
    y = 170
    s += line(120, y, 200, y, INK, 2.4)
    cs1, l1, r1 = cap_sym(220, y, 22, 12)
    s += cs1
    s += text(220, y - 34, "C₁", 13, INK, "middle", "bold")
    s += line(r1, y, 360, y, INK, 2.4)
    cs2, l2, r2 = cap_sym(380, y, 22, 12)
    s += cs2
    s += text(380, y - 34, "C₂", 13, INK, "middle", "bold")
    s += line(r2, y, 480, y, INK, 2.4)
    # спільний заряд
    s += plus(l1 - 4, y, 5, RED, 1.6)
    s += minus(r1 + 4, y, 5, BLUE, 1.6)
    s += plus(l2 - 4, y, 5, RED, 1.6)
    s += minus(r2 + 4, y, 5, BLUE, 1.6)
    s += text(300, y + 36, "однаковий заряд Q крізь обидва", 11.5, INK, "middle", style="italic")
    # результат
    s += rect(510, 110, 190, 120, "#fbfbfb", GREY, 1.6, 10)
    s += text(605, 144, "1/C = 1/C₁ + 1/C₂", 15, INK, "middle", "bold")
    s += text(605, 176, "C = C₁·C₂/(C₁+C₂)", 13, INK, "middle")
    s += text(605, 208, "менше за найменшу!", 12, RED, "middle", "bold")
    save("fig-7-7-2-series.svg", s)


# ── Рис. 7.7.3 — дзеркало резисторів ─────────────────────────────────────────
def fig71_mirror():
    W, H = 720, 360
    s = header(W, H)
    s += text(W / 2, 34, "Конденсатори додаються дзеркально до резисторів", 19, INK, "middle", "bold")
    x0, y0, cw, ch = 200, 110, 230, 90
    # заголовки стовпців
    s += text(x0 + cw / 2, y0 - 14, "ПОСЛІДОВНО", 14, INK, "middle", "bold")
    s += text(x0 + cw + cw / 2, y0 - 14, "ПАРАЛЕЛЬНО", 14, INK, "middle", "bold")
    # рядки
    rows = [("РЕЗИСТОР", "R = R₁ + R₂", "1/R = 1/R₁ + 1/R₂", True, False),
            ("КОНДЕНСАТОР", "1/C = 1/C₁ + 1/C₂", "C = C₁ + C₂", False, True)]
    for i, (lab, cser, cpar, sum_ser, sum_par) in enumerate(rows):
        y = y0 + i * ch
        s += text(x0 - 14, y + ch / 2 + 5, lab, 12.5, INK, "end", "bold")
        s += rect(x0, y, cw, ch, "#eef6ef" if sum_ser else "#fbfbfb", GREEN if sum_ser else "#c9d3dc", 1.6 if sum_ser else 1.2)
        s += rect(x0 + cw, y, cw, ch, "#eef6ef" if sum_par else "#fbfbfb", GREEN if sum_par else "#c9d3dc", 1.6 if sum_par else 1.2)
        s += text(x0 + cw / 2, y + ch / 2 + 5, cser, 14, INK, "middle", "bold")
        s += text(x0 + cw + cw / 2, y + ch / 2 + 5, cpar, 14, INK, "middle", "bold")
    s += text(W / 2, y0 + 2 * ch + 26, "зелене — «просто сума»: у резистора послідовно, у конденсатора паралельно",
              12, GREEN, "middle", "bold")
    save("fig-7-7-3-mirror.svg", s)


# ── Рис. 7.7.4 — чому паралельні додаються (площа) ───────────────────────────
def fig71_parallel_why():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 34, "Паралельно = більша сумарна площа обкладок", 19, INK, "middle", "bold")
    # дві окремі пари
    def pair(cx, cy, ph):
        out = rect(cx - 10, cy - ph / 2, 8, ph, "#f7dada", RED, 1.4)
        out += rect(cx + 2, cy - ph / 2, 8, ph, "#dbe3f7", BLUE, 1.4)
        return out
    s += pair(180, 160, 60)
    s += text(180, 210, "A₁", 13, INK, "middle", "bold")
    s += pair(180, 240, 60)
    s += text(220, 240, "A₂", 13, INK, "middle", "bold")
    s += text(180, 110, "дві пари обкладок", 11.5, GREY, "middle", style="italic")
    s += arrow(280, 200, 360, 200, INK, 2.6)
    s += text(320, 188, "поряд", 11, INK, "middle")
    # одна велика пара
    s += rect(440, 110, 10, 180, "#f7dada", RED, 1.4)
    s += rect(454, 110, 10, 180, "#dbe3f7", BLUE, 1.4)
    s += text(490, 200, "A₁ + A₂", 14, INK, "start", "bold")
    s += text(560, 200, "→ C = C₁ + C₂", 13, GREEN, "start", "bold")
    s += text(W / 2, H - 16, "C ∝ площа (§7.2), тож паралельні ємності просто додаються.", 12, GREY, "middle", style="italic")
    save("fig-7-7-4-parallel-why.svg", s)


# ── Рис. 7.7.5 — чому послідовні дають менше (зазор) ─────────────────────────
def fig71_series_why():
    W, H = 720, 320
    s = header(W, H)
    s += text(W / 2, 34, "Послідовно = більший сумарний зазор", 19, INK, "middle", "bold")
    # дві окремі (малий зазор кожна)
    s += rect(150, 120, 70, 8, "#f7dada", RED, 1.4)
    s += rect(150, 138, 70, 8, "#dbe3f7", BLUE, 1.4)
    s += text(250, 134, "d₁", 13, INK, "start", "bold")
    s += rect(150, 180, 70, 8, "#f7dada", RED, 1.4)
    s += rect(150, 198, 70, 8, "#dbe3f7", BLUE, 1.4)
    s += text(250, 194, "d₂", 13, INK, "start", "bold")
    s += text(185, 110, "малий зазор кожна", 11, GREY, "middle", style="italic")
    s += arrow(300, 160, 380, 160, INK, 2.6)
    s += text(340, 148, "стек", 11, INK, "middle")
    # одна з великим зазором
    s += rect(450, 120, 70, 8, "#f7dada", RED, 1.4)
    s += rect(450, 200, 70, 8, "#dbe3f7", BLUE, 1.4)
    s += line(485, 128, 485, 200, GREY, 1.4, dash="4,3")
    s += text(540, 164, "d₁ + d₂", 14, INK, "start", "bold")
    s += text(540, 184, "→ менша C", 13, RED, "start", "bold")
    s += text(W / 2, H - 16, "C ∝ 1/зазор (§7.2), тож більший сумарний зазор дає меншу ємність.", 12, GREY, "middle", style="italic")
    save("fig-7-7-5-series-why.svg", s)


# ── Рис. 7.7.6 — поділ напруги в послідовному (підняти рейтинг) ───────────────
def fig71_voltage_sharing():
    W, H = 700, 340
    s = header(W, H)
    s += text(W / 2, 34, "Послідовно — піднімаємо допустиму напругу", 19, INK, "middle", "bold")
    bat, bt, bb = battery(120, 170)
    s += bat
    s += text(90, 170, "10 В", 12, INK, "end", "bold")
    # дві ємності послідовно у вертикальній гілці праворуч
    topY, botY = 110, 250
    xc = 420
    s += line(bt[0], bt[1], bt[0], topY, INK, 2.2)
    s += line(bt[0], topY, xc, topY, INK, 2.2)
    cs1, t1, b1 = cap_sym_v(xc, 150)
    s += line(xc, topY, xc, t1, INK, 2.2)
    s += cs1
    s += text(xc + 26, 150, "5 В", 12.5, RED, "start", "bold")
    cs2, t2, b2 = cap_sym_v(xc, 210)
    s += line(xc, b1, xc, t2, INK, 2.2)
    s += cs2
    s += text(xc + 26, 210, "5 В", 12.5, RED, "start", "bold")
    s += line(xc, b2, xc, botY, INK, 2.2)
    s += line(bb[0], bb[1], bb[0], botY, INK, 2.2)
    s += line(bb[0], botY, xc, botY, INK, 2.2)
    s += text(xc, 290, "кожен бачить лише половину", 12, GREEN, "middle", "bold")
    s += rect(500, 130, 180, 90, "#eef6ef", GREEN, 1.6, 10)
    s += text(590, 162, "2 × напруга", 14, INK, "middle", "bold")
    s += text(590, 188, "ціна: ½ ємності", 12, GREY, "middle", style="italic")
    save("fig-7-7-6-voltage-sharing.svg", s)


# ── Рис. 7.7.7 — розподіл заряду й напруги ───────────────────────────────────
def fig71_distribution():
    W, H = 760, 340
    s = header(W, H)
    s += text(W / 2, 34, "Як діляться заряд і напруга", 20, INK, "middle", "bold")
    # паралельно: Q ∝ C
    s += _frame(40, 80, 320, 210, "паралельно: спільна V")
    s += text(200, 116, "Q ∝ C  (більший бере більше заряду)", 11.5, INK, "middle", "bold")
    s += rect(90, 150, 90, 90, "#f7dada", RED, 1.4, 6)
    s += text(135, 200, "C, Q", 12, INK, "middle", "bold")
    s += rect(220, 180, 60, 60, "#f7dada", RED, 1.4, 6)
    s += text(250, 215, "½C", 12, INK, "middle", "bold")
    s += text(250, 232, "½Q", 11, INK, "middle")
    # послідовно: V ∝ 1/C
    s += _frame(420, 80, 320, 210, "послідовно: спільний Q")
    s += text(580, 116, "V ∝ 1/C  (менший бере більшу напругу)", 11.5, INK, "middle", "bold")
    s += rect(470, 150, 60, 90, "#dbe3f7", BLUE, 1.4, 6)
    s += text(500, 200, "малий C", 11, INK, "middle", "bold")
    s += text(500, 217, "велика V", 11, RED, "middle", "bold")
    s += rect(580, 180, 110, 60, "#dbe3f7", BLUE, 1.4, 6)
    s += text(635, 213, "великий C → мала V", 10.5, INK, "middle")
    save("fig-7-7-7-distribution.svg", s)


# ── Рис. 7.7.8 — застосування ────────────────────────────────────────────────
def fig71_applications():
    W, H = 760, 340
    s = header(W, H)
    s += text(W / 2, 34, "Паралельно — для ємності, послідовно — для напруги", 18, INK, "middle", "bold")
    # паралельно: електроліт + кераміка
    s += _frame(40, 80, 320, 210, "паралель: об'єм + швидкість")
    yt, yb = 150, 250
    s += line(90, yt, 310, yt, INK, 2.2)
    s += line(90, yb, 310, yb, INK, 2.2)
    cse, te, be = cap_sym_v(150, 200, 18, 10)
    s += line(150, yt, 150, te, INK, 2)
    s += line(150, be, 150, yb, INK, 2)
    s += cse
    s += plus(150 - 26, te - 4, 5, RED, 1.6)
    s += text(150, 270, "електроліт", 11, INK, "middle", "bold")
    csc, tc, bc = cap_sym_v(260, 200, 13, 7)
    s += line(260, yt, 260, tc, INK, 2)
    s += line(260, bc, 260, yb, INK, 2)
    s += csc
    s += text(260, 270, "кераміка", 11, INK, "middle", "bold")
    s += text(200, 130, "велика ємність + малий ESL", 11, GREEN, "middle", "bold")
    # послідовно: суперконденсатори + балансир
    s += _frame(420, 80, 320, 210, "послідовно: вища напруга")
    xc = 520
    s += line(xc, 130, xc, 150, INK, 2)
    cs1, t1, b1 = cap_sym_v(xc, 165, 16, 9)
    s += cs1
    cs2, t2, b2 = cap_sym_v(xc, 215, 16, 9)
    s += line(xc, b1, xc, t2, INK, 2)
    s += cs2
    s += line(xc, b2, xc, 250, INK, 2)
    s += text(xc, 125, "5 В", 11, INK, "middle")
    s += text(xc + 34, 165, "2.5 В", 11, RED, "start", "bold")
    s += text(xc + 34, 215, "2.5 В", 11, RED, "start", "bold")
    s += text(600, 270, "суперконденсатори на вищу напругу", 10.5, GREEN, "middle", "bold")
    save("fig-7-7-8-applications.svg", s)


if __name__ == "__main__":
    # Історія до Розділу 7 — лейденська банка
    fig_timeline()
    fig_jar()
    fig_hand()
    fig_chain()
    fig_glass()
    fig_battery()
    # §7.1 Що таке конденсатор
    fig11_anatomy()
    fig11_equal_opposite()
    fig11_field()
    fig11_charging()
    fig11_blocks_dc()
    fig11_water()
    fig11_memory()
    fig11_symbol()
    # §7.2 Ємність
    fig21_definition()
    fig21_farad()
    fig21_area()
    fig21_gap()
    fig21_dielectric_mech()
    fig21_dielectric_table()
    fig21_formula()
    fig21_construction()
    # §7.3 Енергія
    fig31_work_to_charge()
    fig31_half_triangle()
    fig31_three_forms()
    fig31_vsquared()
    fig31_field_storage()
    fig31_store_vs_dissipate()
    fig31_power()
    # §7.4 Зарядка й розрядка: RC
    fig41_rc_circuit()
    fig41_charge_curve()
    fig41_discharge_curve()
    fig41_current_curve()
    fig41_tau_meaning()
    fig41_why_exponential()
    fig41_5tau_table()
    fig41_rc_timing()
    # §7.5 Типи, паразити, гранична напруга
    fig51_real_model()
    fig51_types()
    fig51_esr()
    fig51_esl()
    fig51_voltage_breakdown()
    fig51_polarity()
    fig51_leakage_coeff()
    fig51_choose()
    # §7.6 Навіщо конденсатори
    fig61_roles_overview()
    fig61_decoupling()
    fig61_decoupling_placement()
    fig61_smoothing()
    fig61_reservoir()
    fig61_ac_coupling()
    fig61_timing()
    fig61_board_map()
    # §7.7 Послідовно й паралельно
    fig71_parallel()
    fig71_series()
    fig71_mirror()
    fig71_parallel_why()
    fig71_series_why()
    fig71_voltage_sharing()
    fig71_distribution()
    fig71_applications()
    print("OK — фігури Розділу 7 (історія + §7.1–§7.7) згенеровано в", OUT)
