# -*- coding: utf-8 -*-
"""
SVG-фігури для 🔌-вставки §3.7.4c — «Перші FPGA-плати хобіста: iCE40- і Gowin-клас».
Окремий генератор (головний figs.py розділу не чіпаємо), чистий Python без залежностей.
Вивід → ./img/. Стиль за AUTHORING §9: білий фон; «1»/«+» червоний, «0»/«−» синій;
висновок/поле — зелене; стрілки через marker; шрифт sans-serif.

Фігури:
  fig-r07-s4c-1-board-anatomy.svg — що розпаяно на платі iCE40-класу: чип, флеш конфігурації,
                                     USB-міст, кварц, стабілізатори, світлодіоди, кнопки, PMOD
  fig-r07-s4c-2-two-classes.svg   — контраст двох класів: зовнішня флеш (iCE40) vs вбудована (Gowin)
  fig-r07-s4c-3-first-byte.svg    — «перший байт»: PC → USB-міст → флеш → FPGA вантажиться → блимання
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
        f'  <marker id="aViol" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{VIOL}"/></marker>\n'
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'  <marker id="aTeal" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{TEAL}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey",
         VIOL: "aViol", AMBER: "aAmber", TEAL: "aTeal"}


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


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def chip(x, y, w, h, title, sub="", fill="#fbfbfb", stroke=INK):
    """Корпус-чип із ключем-виїмкою і підписом."""
    out = rect(x, y, w, h, fill, stroke, 2, 8)
    out += circle(x + 11, y + 11, 4.5, "#fff", stroke, 1.4)
    out += text(x + w / 2, y + h / 2 - 1, title, 14, stroke, "middle", "bold")
    if sub:
        out += text(x + w / 2, y + h / 2 + 16, sub, 9.5, GREY, "middle")
    return out


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── Фігура 1: анатомія плати iCE40-класу — що саме розпаяно ───────────────────
def fig1_board_anatomy():
    W, H = 840, 560
    b = header(W, H)
    b += text(W / 2, 30, "Що розпаяно на платі iCE40-класу: чип і його обов'язковий «почет»",
              17, INK, "middle", "bold")

    # контур плати
    bx, by, bw, bh = 40, 56, 760, 420
    b += rect(bx, by, bw, bh, "#f7fbf7", GREEN, 2, 14)
    b += text(bx + 14, by + 22, "плата (PCB)", 12, GREEN, "start", "bold")
    # монтажні отвори по кутах
    for cx2, cy2 in [(bx + 18, by + bh - 18), (bx + bw - 18, by + bh - 18),
                     (bx + bw - 18, by + 18)]:
        b += circle(cx2, cy2, 6, "#fff", GREY, 1.6)

    # ── центр: сам FPGA ──
    fx, fy, fw, fh = 350, 200, 150, 130
    b += rect(fx, fy, fw, fh, "#eef2ff", INK, 2.4, 10)
    b += circle(fx + 13, fy + 13, 5.5, "#fff", INK, 1.6)
    b += text(fx + fw / 2, fy + 52, "FPGA", 18, INK, "middle", "bold")
    b += text(fx + fw / 2, fy + 74, "iCE40-клас", 12, INK, "middle")
    b += text(fx + fw / 2, fy + 94, "(поле LUT+тригерів,", 9.5, GREY, "middle")
    b += text(fx + fw / 2, fy + 107, "§3.7.3, §3.3)", 9.5, GREY, "middle")
    # ніжки-банки натяком
    for i in range(5):
        yy = fy + 24 + i * 20
        b += line(fx - 8, yy, fx, yy, INK, 1.6)
        b += line(fx + fw, yy, fx + fw + 8, yy, INK, 1.6)

    def part(x, y, w, h, title, sub, col, note=None):
        out = rect(x, y, w, h, "#ffffff", col, 2, 8)
        out += text(x + w / 2, y + 19, title, 12, col, "middle", "bold")
        if sub:
            out += text(x + w / 2, y + h - 8, sub, 9, GREY, "middle")
        if note:
            out += text(x + w / 2, y + 34, note, 9, INK, "middle")
        return out

    # ── флеш конфігурації (ліворуч-зверху) — головний сусід ──
    cfx, cfy, cfw, cfh = 110, 120, 150, 60
    b += part(cfx, cfy, cfw, cfh, "Флеш конфігурації", "SPI · схема ззовні", AMBER,
              "тримає bitstream")
    b += arrow(cfx + cfw, cfy + cfh / 2, fx, fy + 28, AMBER, 2.2)
    b += text((cfx + cfw + fx) / 2 + 6, cfy + cfh / 2 - 6, "SPI: при старті", 9, AMBER, "middle")
    b += text((cfx + cfw + fx) / 2 + 6, cfy + cfh / 2 + 7, "ллє схему в чип", 9, AMBER, "middle")

    # ── USB-міст (ліворуч-знизу) ──
    ubx, uby, ubw, ubh = 110, 300, 150, 64
    b += part(ubx, uby, ubw, ubh, "USB-міст", "USB ↔ SPI/JTAG", VIOL,
              "програмує флеш")
    b += arrow(ubx + ubw, uby + 20, cfx + cfw / 2, cfy + cfh, VIOL, 2)
    # роз'єм USB зліва від плати
    b += rect(bx - 4, uby + 14, 16, 34, "#dfe3e8", GREY, 1.6, 3)
    b += text(bx + 4, uby + 64, "USB", 9, GREY, "middle")
    b += arrow(bx + 12, uby + 31, ubx, uby + 31, GREY, 2)

    # ── кварц / генератор (зверху) ──
    qx, qy, qw, qh = 350, 96, 150, 54
    b += part(qx, qy, qw, qh, "Кварц / MEMS-генератор", "спільний такт", TEAL)
    b += arrow(qx + qw / 2, qy + qh, fx + fw / 2, fy, TEAL, 2)
    b += text(qx + qw / 2 + 70, qy + qh + 18, "CLK", 9, TEAL, "middle")

    # ── стабілізатори (праворуч-зверху) ──
    rgx, rgy, rgw, rgh = 600, 120, 160, 70
    b += part(rgx, rgy, rgw, rgh, "Стабілізатори", "ядро 1.2 В + банки", RED,
              "кілька рівнів")
    b += arrow(rgx, rgy + 35, fx + fw, fy + 30, RED, 2)
    b += text((rgx + fx + fw) / 2, rgy + 24, "VCC", 9, RED, "middle")

    # ── світлодіоди + кнопки (праворуч-знизу) ──
    iox, ioy, iow, ioh = 600, 300, 160, 70
    b += rect(iox, ioy, iow, ioh, "#ffffff", BLUE, 2, 8)
    b += text(iox + iow / 2, ioy + 18, "Світлодіоди · кнопки", 11, BLUE, "middle", "bold")
    b += text(iox + iow / 2, ioy + 33, "DONE, LED, RESET", 9, GREY, "middle")
    # три світлодіоди
    for i, cc in enumerate([RED, GREEN, BLUE]):
        b += circle(iox + 34 + i * 26, ioy + 52, 6, cc, cc, 1)
    b += rect(iox + 110, ioy + 45, 16, 14, "#eee", INK, 1.4, 2)  # кнопка
    b += arrow(iox, ioy + 30, fx + fw, fy + fh - 24, BLUE, 1.8)

    # ── PMOD-гребінки (знизу) ──
    pmx, pmy, pmw, pmh = 330, 396, 190, 44
    b += rect(pmx, pmy, pmw, pmh, "#fff", GREY, 2, 6)
    b += text(pmx + pmw / 2, pmy + 17, "Роз'єми PMOD (GPIO назовні)", 10.5, INK, "middle", "bold")
    # ряд штирків
    for i in range(12):
        xx = pmx + 16 + i * (pmw - 30) / 11
        b += circle(xx, pmy + 32, 3, GREY, INK, 1)
    b += arrow(fx + fw / 2, fy + fh, pmx + pmw / 2, pmy, GREY, 1.8)

    # підпис-висновок
    b += text(W / 2, H - 30, "Чип сам по собі порожній: щоб ожити, йому потрібні флеш зі схемою, кварц такту,",
              12, INK, "middle")
    b += text(W / 2, H - 13, "кілька живлень і USB-міст, аби ту схему туди залити. Решта — світлодіоди й гребінки назовні.",
              12, GREEN, "middle", "bold")
    save("fig-r07-s4c-1-board-anatomy.svg", b)


# ── Фігура 2: два класи плат — зовнішня флеш (iCE40) vs вбудована (Gowin) ──────
def fig2_two_classes():
    W, H = 840, 470
    b = header(W, H)
    b += text(W / 2, 30, "Дві школи на платі хобіста: де живе схема після вимкнення",
              17, INK, "middle", "bold")

    # ── ЛІВА панель: iCE40-клас (зовнішня флеш) ──
    lx, ly, lw, lh = 40, 56, 370, 330
    b += rect(lx, ly, lw, lh, "#fcfaf3", AMBER, 2.2, 12)
    b += text(lx + lw / 2, ly + 26, "iCE40-клас", 16, AMBER, "middle", "bold")
    b += text(lx + lw / 2, ly + 44, "схема — у ЗОВНІШНІЙ флеші", 11, INK, "middle")

    # FPGA
    f1x, f1y, f1w, f1h = lx + 60, ly + 80, 130, 90
    b += chip(f1x, f1y, f1w, f1h, "FPGA", "порожня при старті", "#eef2ff", INK)
    # зовнішня флеш окремим чипом
    fl1x, fl1y, fl1w, fl1h = lx + 220, ly + 90, 110, 64
    b += rect(fl1x, fl1y, fl1w, fl1h, "#fff7ec", AMBER, 2, 8)
    b += text(fl1x + fl1w / 2, fl1y + 26, "Флеш SPI", 12, AMBER, "middle", "bold")
    b += text(fl1x + fl1w / 2, fl1y + 44, "(окремий чип)", 9, GREY, "middle")
    # стрілка флеш → FPGA при старті
    b += arrow(fl1x, fl1y + fl1h / 2, f1x + f1w, f1y + f1h / 2, AMBER, 2.4)
    b += text((f1x + f1w + fl1x) / 2, fl1y + fl1h / 2 - 8, "при кожному", 8.5, AMBER, "middle")
    b += text((f1x + f1w + fl1x) / 2, fl1y + fl1h / 2 + 4, "вмиканні", 8.5, AMBER, "middle")

    b += text(lx + lw / 2, ly + 210, "На платі — ДВА чипи поруч: FPGA + флеш.", 11, INK, "middle")
    b += text(lx + lw / 2, ly + 230, "Перші ~мс старту йде завантаження схеми;", 11, INK, "middle")
    b += text(lx + lw / 2, ly + 248, "доти виходи мовчать, аж поки DONE → «1».", 11, INK, "middle")
    b += text(lx + lw / 2, ly + 280, "+ відкритий набір інструментів (§3.7.6),", 10.5, GREEN, "middle", "bold")
    b += text(lx + lw / 2, ly + 297, "тому саме він став улюбленцем хобіста", 10.5, GREEN, "middle")
    b += text(lx + lw / 2, ly + 314, "(історію — у 📜 §10).", 10.5, GREY, "middle")

    # ── ПРАВА панель: Gowin-клас (вбудована флеш) ──
    rx, ry, rw, rh = 430, 56, 370, 330
    b += rect(rx, ry, rw, rh, "#f3f9f3", GREEN, 2.2, 12)
    b += text(rx + rw / 2, ry + 26, "Gowin-клас", 16, GREEN, "middle", "bold")
    b += text(rx + rw / 2, ry + 44, "флеш — УСЕРЕДИНІ чипа", 11, INK, "middle")

    # FPGA з вбудованою флеш
    f2x, f2y, f2w, f2h = rx + 110, ry + 80, 150, 110
    b += rect(f2x, f2y, f2w, f2h, "#eef7ee", INK, 2.4, 10)
    b += circle(f2x + 13, f2y + 13, 5.5, "#fff", INK, 1.6)
    b += text(f2x + f2w / 2, f2y + 34, "FPGA", 14, INK, "middle", "bold")
    # вбудована флеш — рамка всередині
    b += rect(f2x + 24, f2y + 52, f2w - 48, 40, "#fff7ec", AMBER, 1.8, 6)
    b += text(f2x + f2w / 2, f2y + 70, "вбудована", 10, AMBER, "middle", "bold")
    b += text(f2x + f2w / 2, f2y + 84, "флеш (eFlash)", 9.5, AMBER, "middle")

    b += text(rx + rw / 2, ry + 210, "На платі — ОДИН чип: флеш уже в ньому.", 11, INK, "middle")
    b += text(rx + rw / 2, ry + 230, "Вмикається фактично «миттєво» —", 11, INK, "middle")
    b += text(rx + rw / 2, ry + 248, "схема піднімається з внутрішньої пам'яті.", 11, INK, "middle")
    b += text(rx + rw / 2, ry + 280, "Менше деталей, простіша плата;", 10.5, GREEN, "middle", "bold")
    b += text(rx + rw / 2, ry + 297, "інструменти — переважно фірмові", 10.5, INK, "middle")
    b += text(rx + rw / 2, ry + 314, "(той самий HDL — §3.7.5).", 10.5, GREY, "middle")

    # спільний підпис-висновок
    b += text(W / 2, H - 28, "Та сама ідея «схему вантажать при старті» (§3.7.1) — тільки в одного флеш зовні,",
              12, INK, "middle")
    b += text(W / 2, H - 11, "а в іншого всередині. Звідси й різна кількість чипів на платі, і різне відчуття «миттєвості».",
              12, GREEN, "middle", "bold")
    save("fig-r07-s4c-2-two-classes.svg", b)


# ── Фігура 3: «перший байт» — шлях від ПК до блимання світлодіода ─────────────
def fig3_first_byte():
    W, H = 840, 430
    b = header(W, H)
    b += text(W / 2, 30, "«Перший байт»: як схема з комп'ютера доходить до світлодіода",
              16, INK, "middle", "bold")

    steps = [
        ("1. На ПК", ["набір інструментів", "робить bitstream", "(HDL → схема,", "§3.7.5–§3.7.6)"], VIOL),
        ("2. USB-міст", ["USB-кабель несе", "файл у плату", "через USB↔SPI", "(чип-міст)"], BLUE),
        ("3. У флеш", ["bitstream лягає", "у флеш: зовнішню", "(iCE40) або", "внутрішню (Gowin)"], AMBER),
        ("4. FPGA встає", ["при старті чип", "вливає схему,", "піднімає DONE,", "виходи оживають"], GREEN),
    ]
    n = len(steps)
    bw, bh = 178, 150
    gap = (W - n * bw) / (n + 1)
    y = 70
    centers = []
    for i, (title, lines, col) in enumerate(steps):
        x = gap + i * (bw + gap)
        centers.append((x + bw, y + bh / 2, x, col))
        b += rect(x, y, bw, bh, "#ffffff", col, 2.4, 10)
        b += rect(x, y, bw, 30, col, col, 0, 10)
        b += text(x + bw / 2, y + 20, title, 12.5, "#ffffff", "middle", "bold")
        ty = y + 52
        for ln in lines:
            b += text(x + bw / 2, ty, ln, 10.5, INK, "middle")
            ty += 18
    # стрілки між кроками
    for i in range(n - 1):
        b += arrow(centers[i][0] + 4, y + bh / 2, centers[i + 1][2] - 4, y + bh / 2, GREY, 2.4)

    # нижня частина: «блимання» як перша перемога + дві дороги в кроці 4
    cy = 255
    b += line(50, cy, W - 50, cy, FAINT, 1)
    b += text(W / 2, cy + 26, "Звідки знати, що чип «заговорив»", 13, INK, "middle", "bold")

    # ліворуч: DONE
    b += rect(70, cy + 40, 340, 92, "#f4f7ff", BLUE, 1.8, 8)
    b += text(240, cy + 62, "Сигнал DONE піднявся у «1»", 12, BLUE, "middle", "bold")
    b += text(240, cy + 82, "= конфігурація завантажилась успішно.", 10.5, INK, "middle")
    b += text(240, cy + 99, "Доти всі виходи мовчать — це норма,", 10.5, INK, "middle")
    b += text(240, cy + 116, "а не «мертвий» чип (як у §3.7.1).", 10.5, INK, "middle")

    # праворуч: блимання
    b += rect(W - 410, cy + 40, 340, 92, "#eef7ee", GREEN, 1.8, 8)
    b += text(W - 240, cy + 62, "Перша справжня перевірка — блимання", 12, GREEN, "middle", "bold")
    b += text(W - 240, cy + 82, "світлодіода: найменша схема, що", 10.5, INK, "middle")
    b += text(W - 240, cy + 99, "ділить кварц лічильником (§3.3) і", 10.5, INK, "middle")
    b += text(W - 240, cy + 116, "вмикає LED. Видно — отже, все живе.", 10.5, INK, "middle")
    save("fig-r07-s4c-3-first-byte.svg", b)


if __name__ == "__main__":
    fig1_board_anatomy()
    fig2_two_classes()
    fig3_first_byte()
    print("r07-s4-c-hobby-fpga-boards figures done.")
