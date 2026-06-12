# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для історичної вставки до Розділу 2.12 —
«Ганс Камензінд і таймер 555» (Модуль 2, Розділ 12, історія до розділу).

Чистий Python, без сторонніх залежностей. Вивід → ./img/.
ОКРЕМИЙ скрипт: не чіпає головний figs.py розділу. Імена SVG унікальні
(префікс fig-r12-h555-*), щоб не зіткнутися з фігурами тем розділу.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи історії до розділу —
секція 0 (Рис. 2.12.0.k). Допоміжні функції скопійовано з figs.py розділу 13.
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
COPP  = "#b5732e"
SUN   = "#e0a32e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LSUN  = "#fbf3e0"
LGREY = "#f2f2f2"
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


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" rx="{rx}"/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def save(name, body):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", path)


# ---------------------------------------------------------------------------
# Рис. 2.12.0.1 — Родовід: від PLL до найтиражнішої мікросхеми світу
# ---------------------------------------------------------------------------
def fig_timeline():
    W, H = 920, 360
    body = text(W / 2, 34, "Шлях таймера 555: від побічної ідеї до мільярдів на рік",
                size=19, anchor="middle", weight="bold")

    # вісь часу
    y0 = 150
    body += line(70, y0, W - 50, y0, color=GREY, w=3)

    stops = [
        (130, "1968", "Камензінд приходить у Signetics —", "розробляти ФАПЧ (PLL)", BLUE, "up"),
        (300, "1970", "криза, звільнення;", "ФАПЧ заморожено", RED, "down"),
        (470, "1971", "555 спроєктовано", "вдома, на контракті", GREEN, "up"),
        (640, "1972", "Signetics випускає", "NE555 на ринок", INK, "down"),
        (820, "сьогодні", "мільярди штук на рік;", "≈ найтиражніша ІМС", GREEN, "up"),
    ]
    for x, yr, l1, l2, col, side in stops:
        body += circle(x, y0, 8, fill="#ffffff", stroke=col, w=3)
        body += circle(x, y0, 3, fill=col, stroke=col, w=1)
        if side == "up":
            body += line(x, y0 - 8, x, y0 - 36, color=col, w=2)
            body += text(x, y0 - 60, yr, size=17, anchor="middle", weight="bold", color=col)
            body += text(x, y0 - 44, l1, size=12.5, anchor="middle")
            body += text(x, y0 - 28, l2, size=12.5, anchor="middle")
        else:
            body += line(x, y0 + 8, x, y0 + 36, color=col, w=2)
            body += text(x, y0 + 52, yr, size=17, anchor="middle", weight="bold", color=col)
            body += text(x, y0 + 70, l1, size=12.5, anchor="middle")
            body += text(x, y0 + 86, l2, size=12.5, anchor="middle")

    # підпис-висновок знизу
    body += text(W / 2, H - 18,
                 "Універсальний таймер народився як побічний продукт зупиненого проєкту ФАПЧ.",
                 size=13.5, anchor="middle", style="italic", color=GREY)

    return header(W, H) + body + footer()


# ---------------------------------------------------------------------------
# Рис. 2.12.0.2 — «Спроєктовано вдома»: угода, ручна робота, склад кристала
# ---------------------------------------------------------------------------
def fig_designed_at_home():
    W, H = 920, 430
    body = header(W, H)
    body += text(W / 2, 32, "Як один інженер спроєктував чип вручну, без комп'ютера",
                 size=19, anchor="middle", weight="bold")

    # --- ліва панель: угода з Signetics ---
    bx, by, bw, bh = 40, 60, 360, 200
    body += rect(bx, by, bw, bh, fill=LSUN, stroke=SUN, sw=2, rx=12)
    body += text(bx + bw / 2, by + 26, "Угода замість звільнення (1970)",
                 size=15.5, anchor="middle", weight="bold", color=COPP)
    deal = [
        "• половина зарплати на рік",
        "• уся потрібна апаратура — у борг",
        "• працює сам, як зовнішній консультант",
        "• ідея: зробити з генератора ФАПЧ",
        "   універсальний таймер на продаж",
    ]
    yy = by + 54
    for ln in deal:
        body += text(bx + 22, yy, ln, size=13.5)
        yy += 27

    # стрілка між панелями
    body += arrow(bx + bw + 6, by + bh / 2, bx + bw + 70, by + bh / 2, color=INK, w=2.5)
    body += text(bx + bw + 38, by + bh / 2 - 12, "рік", size=12, anchor="middle", color=GREY)
    body += text(bx + bw + 38, by + bh / 2 + 22, "праці", size=12, anchor="middle", color=GREY)

    # --- права панель: ручна робота / Rubylith ---
    cx, cy, cw, ch = bx + bw + 80, 60, 360, 200
    body += rect(cx, cy, cw, ch, fill=LGREY, stroke=GREY, sw=2, rx=12)
    body += text(cx + cw / 2, cy + 26, "Усе руками, без комп'ютера",
                 size=15.5, anchor="middle", weight="bold", color=INK)
    # стилізований лист рубіліту з прорізаними доріжками
    rb_x, rb_y, rb_w, rb_h = cx + 26, cy + 44, 150, 130
    body += rect(rb_x, rb_y, rb_w, rb_h, fill="#7a1622", stroke="#54101a", sw=1.5, rx=4)
    # прорізані «вікна» (світлі) — імітація макета під фотошаблон
    cuts = [(12, 12, 56, 26), (80, 12, 54, 40), (12, 50, 40, 60),
            (60, 64, 30, 30), (98, 64, 36, 50), (12, 120, 122, 0)]
    for ux, uy, uw, uh in cuts:
        if uh == 0:
            continue
        body += rect(rb_x + ux, rb_y + uy, uw, uh, fill="#fbe8b0", stroke="#caa84e", sw=1, rx=2)
    body += text(rb_x + rb_w / 2, rb_y + rb_h + 18, "лист рубіліту (Rubylith),",
                 size=12, anchor="middle", color=GREY)
    body += text(rb_x + rb_w / 2, rb_y + rb_h + 33, "доріжки прорізано ножем",
                 size=12, anchor="middle", color=GREY)
    # підпис справа від рубіліту
    body += text(rb_x + rb_w + 22, cy + 70, "≈ рік на макетах:", size=13.5, weight="bold")
    body += text(rb_x + rb_w + 22, cy + 92, "паяти, міряти,", size=13)
    body += text(rb_x + rb_w + 22, cy + 110, "креслити схему", size=13)
    body += text(rb_x + rb_w + 22, cy + 128, "на папері,", size=13)
    body += text(rb_x + rb_w + 22, cy + 146, "різати фотошаблон", size=13)

    # --- нижня смуга: склад готового кристала ---
    ny, nh = 290, 100
    body += rect(40, ny, W - 80, nh, fill=LGRN, stroke=GREEN, sw=2, rx=12)
    body += text(60, ny + 30, "Готовий кристал (біполярний NE555):",
                 size=15, weight="bold", color=GREEN)
    # три «чипи-лічильники»
    chips = [("23", "транзистори"), ("16", "резисторів"), ("2", "діоди")]
    chx = 470
    for big, small in chips:
        body += rect(chx, ny + 18, 120, 64, fill="#ffffff", stroke=GREEN, sw=2, rx=8)
        body += text(chx + 60, ny + 50, big, size=30, anchor="middle", weight="bold", color=INK)
        body += text(chx + 60, ny + 72, small, size=12.5, anchor="middle", color=GREY)
        chx += 140

    body += text(W / 2, H - 14,
                 "У різних джерелах склад трохи різниться (напр. 25 транзисторів / 15 резисторів) — наводимо власні цифри Камензінда.",
                 size=11.5, anchor="middle", style="italic", color=GREY)

    return body + footer()


if __name__ == "__main__":
    save("fig-r12-h555-timeline.svg", fig_timeline())
    save("fig-r12-h555-designed-at-home.svg", fig_designed_at_home())
    print("done.")
