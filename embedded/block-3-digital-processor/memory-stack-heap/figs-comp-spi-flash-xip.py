# -*- coding: utf-8 -*-
"""
Генератор SVG для 🔌-вставки §3.6.3c — «Чип W25Q-класу поруч із ESP32».
Окремий від головного figs.py (його не чіпаємо). Чистий Python, без залежностей.
Вивід → ./img/. Стиль (AUTHORING §9) — спільні допоміжні функції скопійовано
з figs.py розділу, щоб вигляд був єдиний: білий фон, «1» червоний, «0» синій,
стрілки через marker, sans-serif.

Фігури тут — три, кожна несе вагу (§9):
  fig-19-3c-1  блок-схема: SoC ↔ зовнішній SPI-NOR-чип, де живе прошивка
  fig-19-3c-2  розпіновка SOIC-8 і чотири лінії SPI до контролера
  fig-19-3c-3  XIP: чому код «живе» у флеші — кеш між шиною та повільною флешшю
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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
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
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ════════════ Рис. 3.6.3c.1 — блок-схема: де живе прошивка ═══════════════════
def fig_blockdiagram():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Прошивка живе в окремому чипі — зовнішній SPI-флеші поруч із SoC", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "у ESP32 ядро та RAM на кристалі, а власне програму тримає сусідній флеш-чип, з'єднаний шиною SPI",
              11.5, GREY, "middle", style="italic")

    # ── SoC (ESP32) ліворуч ──
    sx, sy, sw, sh = 70, 110, 330, 250
    s += rect(sx, sy, sw, sh, "#f7f9fc", BLUE, 2.2, 12)
    s += text(sx + sw / 2, sy + 26, "SoC (ESP32)", 16, BLUE, "middle", "bold")
    s += text(sx + sw / 2, sy + 44, "усе на одному кристалі", 10.5, GREY, "middle", style="italic")
    # ядро
    s += rect(sx + 24, sy + 60, 130, 56, "#ffffff", INK, 1.8, 8)
    s += text(sx + 89, sy + 84, "ядро CPU", 12.5, INK, "middle", "bold")
    s += text(sx + 89, sy + 101, "виконує код", 10, GREY, "middle")
    # SRAM
    s += rect(sx + 176, sy + 60, 130, 56, "#ffffff", INK, 1.8, 8)
    s += text(sx + 241, sy + 84, "SRAM", 12.5, INK, "middle", "bold")
    s += text(sx + 241, sy + 101, "змінні (летка)", 10, GREY, "middle")
    # кеш + контролер SPI-флеші
    s += rect(sx + 24, sy + 132, 130, 50, "#f4f7f4", GREEN, 1.8, 8)
    s += text(sx + 89, sy + 152, "кеш", 12, GREEN, "middle", "bold")
    s += text(sx + 89, sy + 168, "тримає гарячий код", 9, GREY, "middle")
    s += rect(sx + 176, sy + 132, 130, 50, "#fff8e8", AMBER, 1.8, 8)
    s += text(sx + 241, sy + 152, "контролер", 11.5, INK, "middle", "bold")
    s += text(sx + 241, sy + 168, "SPI-флеші", 11.5, INK, "middle", "bold")
    # підпис «крихітна вбудована Flash тільки на завантажувач»
    s += text(sx + sw / 2, sy + 212, "вбудована Flash тут крихітна або відсутня —", 10, GREY, "middle", style="italic")
    s += text(sx + sw / 2, sy + 228, "місця на цілу програму бракує", 10, GREY, "middle", style="italic")

    # ── шина SPI (4 лінії) ──
    bx0 = sx + sw
    bx1 = 560
    ys = [sy + 132, sy + 146, sy + 160, sy + 174]
    labs = ["CS", "CLK", "MOSI", "MISO"]
    cols = [INK, INK, RED, BLUE]
    for y, lab, col in zip(ys, labs, cols):
        s += line(bx0, y, bx1, y, col, 2)
    # стрілки напряму: команда йде до флеші, дані — назад
    s += arrow((bx0 + bx1) / 2 - 4, ys[2], (bx0 + bx1) / 2 + 18, ys[2], RED, 2)
    s += arrow((bx0 + bx1) / 2 + 18, ys[3], (bx0 + bx1) / 2 - 4, ys[3], BLUE, 2)
    s += text((bx0 + bx1) / 2, sy + 118, "шина SPI · 4 дроти", 11.5, INK, "middle", "bold")
    s += text(bx0 + 8, ys[0] - 4, "CS", 9, GREY, "start")
    s += text(bx0 + 8, ys[1] - 0, "CLK", 9, GREY, "start")

    # ── зовнішній флеш-чип праворуч ──
    fx, fy, fw, fh = 560, 130, 270, 210
    s += rect(fx, fy, fw, fh, "#fdf4f4", RED, 2.2, 12)
    s += text(fx + fw / 2, fy + 26, "зовнішній чип SPI-NOR-флеші", 12.5, RED, "middle", "bold")
    s += text(fx + fw / 2, fy + 44, "клас W25Q · корпус SOIC-8", 10.5, GREY, "middle", style="italic")
    s += rect(fx + 30, fy + 60, fw - 60, 64, "#ffffff", INK, 1.8, 8)
    s += text(fx + fw / 2, fy + 86, "прошивка (код + сталі)", 12, INK, "middle", "bold")
    s += text(fx + fw / 2, fy + 105, ".text · .rodata · ресурси", 10, GREY, "middle")
    s += text(fx + fw / 2, fy + 146, "нелетка: лишається після вимкнення (§3.6.3)", 10, GREY, "middle", style="italic")
    s += text(fx + fw / 2, fy + 166, "об'єм — мегабайти, недорого", 10, GREY, "middle", style="italic")
    s += text(fx + fw / 2, fy + 192, "як читає й пише — NOR і XIP, §3.8.5", 10, GREEN, "middle", "bold")

    # нижня плашка-висновок
    s += rect(60, 392, W - 120, 60, "#f4f7f4", GREEN, 1.8, 10)
    s += text(W / 2, 416, "Поділ той самий, що в §3.6.3: змінні — у швидкій леткій SRAM на кристалі; код і сталі — у місткій нелеткій флеші.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 438, "Лише тепер флеш — НЕ всередині мікросхеми процесора, а окремим чипом поруч, на спільній платі, через шину SPI.",
              10.5, GREY, "middle", style="italic")
    save("fig-19-3c-1-blockdiagram.svg", s)


# ════════════ Рис. 3.6.3c.2 — розпіновка SOIC-8 і 4 лінії ════════════════════
def fig_pinout():
    W, H = 900, 488
    s = header(W, H)
    s += text(W / 2, 34, "Розпіновка SOIC-8 і чотири дроти до контролера", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "вісім ніжок чипа; чотири з них — це шина SPI, ще чотири — живлення та дві службові лінії (тримати високими)",
              11.5, GREY, "middle", style="italic")

    # корпус
    bx, by, bw, bh = 350, 110, 200, 260
    s += rect(bx, by, bw, bh, "#fafafa", INK, 2.2, 10)
    s += circle(bx + 22, by + 24, 6, "#fff", INK, 1.8)  # маркер 1-ї ніжки
    s += text(bx + bw / 2, by + 34, "SPI-NOR", 14, INK, "middle", "bold")
    s += text(bx + bw / 2, by + 54, "флеш", 13, INK, "middle", "bold")
    s += text(bx + bw / 2, by + 78, "(W25Q-клас)", 10.5, GREY, "middle", style="italic")
    s += text(bx + bw / 2, by + bh - 16, "вид зверху", 10, GREY, "middle", style="italic")

    left = [
        ("1", "CS#", "вибір чипа (низький = слухай мене)", INK),
        ("2", "DO (MISO)", "дані ВІД чипа до контролера", BLUE),
        ("3", "WP#", "захист запису — тримати високим", GREY),
        ("4", "GND", "земля", INK),
    ]
    right = [
        ("8", "VCC", "живлення 3.3 В", RED),
        ("7", "HOLD#", "пауза — тримати високим", GREY),
        ("6", "CLK", "такт від контролера", INK),
        ("5", "DI (MOSI)", "дані ВІД контролера до чипа", RED),
    ]
    pin_y = [by + 56, by + 116, by + 176, by + 236]
    # ліві ніжки
    for (num, name, desc, col), y in zip(left, pin_y):
        s += line(bx - 34, y, bx, y, col, 2)
        s += rect(bx - 30, y - 9, 18, 18, "#fff", col, 1.6, 3)
        s += text(bx - 21, y + 5, num, 11, col, "middle", "bold")
        s += text(bx - 44, y - 4, name, 12, col, "end", "bold")
        s += text(bx - 44, y + 13, desc, 9.5, GREY, "end")
    # праві ніжки
    for (num, name, desc, col), y in zip(right, pin_y):
        s += line(bx + bw, y, bx + bw + 34, y, col, 2)
        s += rect(bx + bw + 12, y - 9, 18, 18, "#fff", col, 1.6, 3)
        s += text(bx + bw + 21, y + 5, num, 11, col, "middle", "bold")
        s += text(bx + bw + 44, y - 4, name, 12, col, "start", "bold")
        s += text(bx + bw + 44, y + 13, desc, 9.5, GREY, "start")

    # легенда чотирьох SPI-ліній
    s += rect(60, 396, W - 120, 76, "#f7f9fc", BLUE, 1.8, 10)
    s += text(W / 2, 418, "Чотири лінії SPI — серце підключення:", 12.5, INK, "middle", "bold")
    items = [
        ("CS#", "обрати чип", INK),
        ("CLK", "такт", INK),
        ("DI/MOSI", "команда→чип", RED),
        ("DO/MISO", "дані→контролер", BLUE),
    ]
    cx0 = 130
    for i, (k, v, col) in enumerate(items):
        x = cx0 + i * 195
        s += text(x, 444, k, 12, col, "start", "bold")
        s += text(x, 462, v, 10, GREY, "start")
    s += text(W / 2, 462, "", 9, GREY, "middle")
    s += text(W - 90, 444, "+VCC, GND", 11, RED, "end", "bold")
    s += text(W - 90, 462, "WP#, HOLD# → високі", 10, GREY, "end")
    save("fig-19-3c-2-pinout.svg", s)


# ════════════ Рис. 3.6.3c.3 — XIP: код «живе» у флеші через кеш ═══════════════
def fig_xip():
    W, H = 900, 452
    s = header(W, H)
    s += text(W / 2, 34, "XIP: код «живе» у флеші, а виконується наче з RAM — завдяки кешу", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "контролер сам підкачує шматки коду з повільної флеші у швидкий кеш; ядро бачить суцільний адресний простір",
              11.5, GREY, "middle", style="italic")

    # ядро
    cx, cy = 130, 150
    s += rect(cx, cy, 150, 90, "#f7f9fc", BLUE, 2, 10)
    s += text(cx + 75, cy + 32, "ядро CPU", 13, BLUE, "middle", "bold")
    s += text(cx + 75, cy + 52, "просить байт коду", 10, GREY, "middle")
    s += text(cx + 75, cy + 70, "за його адресою", 10, GREY, "middle")

    # кеш
    kx, ky = 380, 150
    s += rect(kx, ky, 150, 90, "#f4f7f4", GREEN, 2, 10)
    s += text(kx + 75, ky + 30, "кеш", 13, GREEN, "middle", "bold")
    s += text(kx + 75, ky + 50, "швидкий, малий", 10, GREY, "middle")
    s += text(kx + 75, ky + 68, "копія гарячого коду", 10, GREY, "middle")

    # флеш
    fx, fy = 640, 150
    s += rect(fx, fy, 180, 90, "#fdf4f4", RED, 2, 10)
    s += text(fx + 90, fy + 30, "SPI-NOR-флеш", 12.5, RED, "middle", "bold")
    s += text(fx + 90, fy + 50, "уся прошивка", 10, GREY, "middle")
    s += text(fx + 90, fy + 68, "повільна, але містка", 10, GREY, "middle")

    # стрілки попадання в кеш
    s += arrow(cx + 150, cy + 30, kx, ky + 30, INK, 2)
    s += text((cx + 150 + kx) / 2, cy + 22, "адреса", 10, INK, "middle", "bold")
    s += arrow(kx, ky + 58, cx + 150, cy + 58, GREEN, 2)
    s += text((cx + 150 + kx) / 2, cy + 78, "є в кеші → миттєво", 9.5, GREEN, "middle", "bold")

    # промах → підкачка з флеші
    s += arrow(kx + 150, ky + 30, fx, fy + 30, AMBER, 2, dash="5,4")
    s += text((kx + 150 + fx) / 2, cy + 22, "промах →", 9.5, AMBER, "middle", "bold")
    s += text((kx + 150 + fx) / 2, cy + 36, "читай блок", 9.5, AMBER, "middle")
    s += arrow(fx, fy + 58, kx + 150, ky + 58, RED, 2, dash="5,4")
    s += text((kx + 150 + fx) / 2, cy + 78, "блок коду по SPI", 9.5, RED, "middle")

    # плашка пояснення
    s += rect(60, 286, W - 120, 70, "#f7f9fc", BLUE, 1.6, 10)
    s += text(W / 2, 310, "Execute-In-Place (XIP): процесор виконує код прямо «на місці» — не копіюючи всю програму в RAM наперед.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 332, "Потрібен байт — кеш або вже має його (миттєво), або підкачує блок із флеші по SPI (рідше, повільніше) і віддає ядру.",
              10.5, GREY, "middle", style="italic")
    s += text(W / 2, 348, "", 9, GREY, "middle")

    # місток уперед
    s += rect(60, 366, W - 120, 66, "#f4f7f4", GREEN, 1.8, 10)
    s += text(W / 2, 390, "Чому саме NOR-флеш дозволяє таке читання «байт за адресою», а NAND — ні, і як влаштований XIP усередині —",
              11, INK, "middle", "bold")
    s += text(W / 2, 412, "це тема §3.8.5. Тут досить картини: код лишається у флеші, а кеш робить його швидким на вигляд.",
              11, INK, "middle", "bold")
    save("fig-19-3c-3-xip.svg", s)


if __name__ == "__main__":
    fig_blockdiagram()
    fig_pinout()
    fig_xip()
    print("done.")
