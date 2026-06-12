# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для компонентної вставки 2.10.8c — «MEMS-осцилятор
проти кварцу». НЕ чіпає головний figs.py розділу. Вивід → ./img/ з
УНІКАЛЬНИМИ іменами (fig-r10-s8c-*). Стиль (AUTHORING §9): білий фон;
'+' червоний, '−' синій; поле зелене; стрілки через marker; шрифт
sans-serif. Допоміжні функції скопійовано з figs.py розділу (єдиний
вигляд між розділами).
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
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
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
        f'  <marker id="aCopp" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{COPP}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey", COPP: "aCopp"}


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


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _block(x, y, w, h, title, sub=None, fill=LBLUE, stroke=BLUE):
    """Прямокутний блок із заголовком (і дрібним підписом)."""
    s = rect(x, y, w, h, fill, stroke, 2.2, rx=7)
    if sub:
        s += text(x + w / 2, y + h / 2 - 4, title, 14.5, INK, "middle", "bold")
        s += text(x + w / 2, y + h / 2 + 15, sub, 11.5, GREY, "middle", style="italic")
    else:
        s += text(x + w / 2, y + h / 2 + 5, title, 14.5, INK, "middle", "bold")
    return s


# ── Рис. 2.10.8c.1 — блок-схема: кварц П'єрса проти MEMS-осцилятора ──────────
def fig_mems_block():
    """Два рядки. Угорі — пасивний кварц + інвертор МК + 2 конденсатори,
    частота жорстко = частоті пластинки. Унизу — MEMS XO однією мікросхемою:
    кремнієвий резонатор → підтримка → (термодавач) → дробовий PLL → вихідна
    частота довільна. Показує, ЧОМУ MEMS дає програмовану частоту."""
    W, H = 940, 560
    s = header(W, H)
    s += text(W / 2, 34, "Кварцовий вузол П'єрса проти MEMS-осцилятора: де народжується частота",
              19, INK, "middle", "bold")
    s += text(W / 2, 56, "у кварці вихід = частота пластинки; у MEMS дробовий PLL синтезує будь-яку частоту з «незручної» опорної",
              12.5, GREY, "middle", style="italic")

    # ── Верхній рядок: кварц + інвертор у МК (генератор П'єрса) ──────────────
    # Дві шини XIN/XOUT горизонтально; кристал містком між ними, два навантажу-
    # вальні конденсатори вниз на землю, інвертор у МК між шинами. Ортогональне
    # розведення — без діагональних дротів і стрілок-стубів.
    ytop = 92
    s += text(70, ytop + 4, "Кварц (§2.10.5)", 14, INK, "start", "bold")

    # межа мікроконтролера (праворуч)
    mcx, mcy, mcw, mch = 470, ytop + 12, 370, 150
    s += rect(mcx, mcy, mcw, mch, "#fcfcfc", GREY, 1.6, rx=8)
    s += text(mcx + mcw - 12, mcy + 20, "мікроконтролер", 12, GREY, "end", style="italic")

    yA = ytop + 42          # шина XIN (верхня нога кристала)
    yB = ytop + 112         # шина XOUT (нижня нога кристала)

    # кристал XTAL — символ містком на верхній шині yA
    qx = 150
    s += rect(qx - 11, yA - 22, 22, 44, LGRN, GREEN, 2.2, rx=3)    # пластинка
    s += line(qx - 26, yA - 16, qx - 26, yA + 16, INK, 3)          # лівий електрод
    s += line(qx + 26, yA - 16, qx + 26, yA + 16, INK, 3)          # правий електрод
    s += line(qx - 26, yA, qx - 11, yA, INK, 2)
    s += line(qx + 11, yA, qx + 26, yA, INK, 2)
    s += text(qx, yA - 32, "кристал XTAL", 12.5, GREEN, "middle", "bold")
    s += text(qx + 70, yA - 14, "пасивна пластинка", 11, GREY, "start", style="italic")

    # ліва вертикаль: лівий електрод вниз до шини XOUT (yB)
    xL = qx - 26
    s += line(xL, yA, xL, yB, INK, 2)
    # права вертикаль під'єднання кристала до шини XIN (yA) — уже на yA
    xR = qx + 26

    # шини в МК
    s += line(xL, yB, mcx, yB, INK, 2)      # XOUT-шина
    s += line(xR, yA, mcx, yA, INK, 2)      # XIN-шина
    s += text(mcx + 8, yA - 6, "XIN", 11.5, INK, "start", "bold")
    s += text(mcx + 8, yB + 16, "XOUT", 11.5, INK, "start", "bold")

    # два навантажувальні конденсатори CL: з кожної шини вниз на землю
    ygnd = yB + 54
    for nx, ybus, lab in ((qx + 110, yA, "CL"), (qx + 250, yB, "CL")):
        s += line(nx, ybus, nx, ygnd - 20, INK, 2)          # відгалуження від шини
        # для XIN-шини беремо точку всередині відрізка xR..mcx; для XOUT — теж
        s += line(nx - 13, ygnd - 20, nx + 13, ygnd - 20, INK, 2.4)   # верхня обкладка
        s += line(nx - 13, ygnd - 14, nx + 13, ygnd - 14, INK, 2.4)   # нижня обкладка
        s += line(nx, ygnd - 14, nx, ygnd, INK, 2)
        s += line(nx - 10, ygnd, nx + 10, ygnd, INK, 2)               # земля
        s += line(nx - 6, ygnd + 4, nx + 6, ygnd + 4, INK, 2)
        s += line(nx - 3, ygnd + 8, nx + 3, ygnd + 8, INK, 2)
        s += text(nx + 17, ygnd - 16, lab, 11, GREY, "start")
    # точки-вузли, де конденсатори чіпляються до шин
    s += circle(qx + 110, yA, 3, INK, INK, 1)
    s += circle(qx + 250, yB, 3, INK, INK, 1)

    # інвертор-підсилювач у МК між XIN та XOUT
    tx, ty = mcx + 150, mcy + mch / 2
    s += f'<path d="M {tx:.1f},{ty-24:.1f} L {tx:.1f},{ty+24:.1f} L {tx+44:.1f},{ty:.1f} Z" fill="{LBLUE}" stroke="{BLUE}" stroke-width="2.2"/>\n'
    s += circle(tx + 50, ty, 5.5, "#fff", BLUE, 2.2)
    s += text(tx + 22, ty + 5, "−1", 13, BLUE, "middle", "bold")
    s += text(tx + 24, ty - 32, "інвертор-підсилювач", 11.5, BLUE, "middle", style="italic")
    # XIN(yA) → вхід інвертора: від піна вправо-вниз до вершини трикутника
    xin_drop = mcx + 60
    s += line(mcx, yA, xin_drop, yA, INK, 2)
    s += line(xin_drop, yA, xin_drop, ty - 12, INK, 2)
    s += line(xin_drop, ty - 12, tx, ty - 12, INK, 2)
    # вихід інвертора → XOUT(yB): вправо, вниз до рівня XOUT, вліво до піна
    xout_ret = tx + 130
    s += line(tx + 55, ty, xout_ret, ty, INK, 2)
    s += line(xout_ret, ty, xout_ret, yB, INK, 2)
    s += line(xout_ret, yB, mcx, yB, INK, 2)

    # вихід частоти
    s += text(mcx + mcw - 120, mcy + mch - 18, "f = f_пластинки", 13, RED, "end", "bold")
    s += text(mcx + mcw - 120, mcy + mch - 2, "(жорстко!)", 11, GREY, "end", style="italic")

    # ── Роздільник ──────────────────────────────────────────────────────────
    s += line(40, 300, W - 40, 300, FAINT, 1.6, "6 5")

    # ── Нижній рядок: MEMS XO однією мікросхемою ────────────────────────────
    ybot = 326
    s += text(70, ybot + 4, "MEMS-осцилятор", 14, INK, "start", "bold")

    # межа мікросхеми
    chx, chy, chw, chh = 70, ybot + 18, W - 250, 168
    s += rect(chx, chy, chw, chh, "#fbfbff", BLUE, 2.0, rx=9)
    s += text(chx + chw - 12, chy + 20, "одна мікросхема (XO)", 12, GREY, "end", style="italic")

    # головний рядок блоків — нижче, щоб над PLL лишилось місце для термодавача
    cy = chy + chh / 2 + 24
    # 1) кремнієвий MEMS-резонатор
    bx = chx + 26
    s += _block(bx, cy - 32, 150, 64, "MEMS-резонатор", "кремній, напр. 48 МГц", LGRN, GREEN)
    # 2) підтримувальна схема
    bx2 = bx + 176
    s += _block(bx2, cy - 32, 130, 64, "підтримка", "sustaining amp", LBLUE, BLUE)
    # 3) дробовий PLL
    bx3 = bx2 + 156
    s += _block(bx3, cy - 32, 150, 64, "дробовий PLL", "fractional-N", LRED, RED)
    # термодавач (над PLL, коригує його через петлю)
    tdx = bx3 + 4
    s += _block(tdx, chy + 14, 142, 40, "термодавач", None, "#fff7e6", COPP)
    # видима стрілка вниз від давача у блок PLL
    s += line(tdx + 71, chy + 54, tdx + 71, cy - 32, COPP, 2.2, "4 4")
    s += arrow(tdx + 71, cy - 44, tdx + 71, cy - 32, COPP, 2.2)
    s += text(tdx + 150, chy + 38, "коригує дрейф", 11, COPP, "start", style="italic")
    s += text(tdx + 150, chy + 54, "(ppm, §2.10.6)", 11, COPP, "start", style="italic")

    # стрілки потоку
    s += arrow(bx + 150, cy, bx2, cy, INK, 2.4)
    s += arrow(bx2 + 130, cy, bx3, cy, INK, 2.4)
    s += arrow(bx3 + 150, cy, chx + chw, cy, INK, 2.4)

    # вихід — довільна частота
    s += text(chx + chw + 14, cy - 6, "OUT", 13, INK, "start", "bold")
    s += text(chx + chw + 14, cy + 14, "25 / 27 / 33.333 МГц…", 12.5, RED, "start", "bold")
    s += text(chx + chw + 14, cy + 32, "будь-яка частота", 11, GREY, "start", style="italic")

    save("fig-r10-s8c-1-mems-block.svg", s)


if __name__ == "__main__":
    fig_mems_block()
    print("done r10-s8c figures")
