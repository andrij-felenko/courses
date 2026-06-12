# -*- coding: utf-8 -*-
"""
Генератор SVG для 🔌-вставки §3.6.8c — «PSRAM: додаткові мегабайти по SPI»
(Модуль 3, Розділ 3.6, до теми 3.6.8).

Окремий скрипт вставки (головний figs.py розділу НЕ чіпаємо). Чистий Python,
без сторонніх залежностей. Вивід → ./img/ тієї самої папки розділу.
Імена файлів унікальні: fig-19-8c-*.svg (8c = компонентна вставка до теми 3.6.8).

Стиль (AUTHORING §9): білий фон; sans-serif; стрілки через marker; єдиний
вигляд із рештою розділу — допоміжні функції скопійовано з figs.py розділу.
Підписи у тексті — «Рис. 3.6.8c.k».
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


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ════════════ Рис. 3.6.8c.1 — клас пристрою + блок-схема ═════════════════════
# PSRAM як третій чип поряд із SoC і Flash; усередині — комірка DRAM + логіка
# самооновлення, а назовні — простий інтерфейс SPI/QSPI (вдає SRAM).
def fig_blockdiagram():
    W, H = 900, 560
    s = header(W, H)
    s += text(W / 2, 34, "PSRAM: ще один чип пам'яті поряд із процесором — лише летка й по тій самій шині",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "клас пристрою: pseudo-static RAM — щільна комірка DRAM усередині, а назовні простий інтерфейс SPI, що вдає SRAM",
              11.2, GREY, "middle", style="italic")

    # ── SoC (ESP32) ліворуч ──
    sx, sy, sw, sh = 60, 96, 340, 300
    s += rect(sx, sy, sw, sh, "#f7f9fc", BLUE, 2.2, 12)
    s += text(sx + sw / 2, sy + 24, "SoC (ESP32)", 15.5, BLUE, "middle", "bold")
    s += text(sx + sw / 2, sy + 42, "ядро + пам'ять на одному кристалі", 10, GREY, "middle", style="italic")
    # ядро
    s += rect(sx + 22, sy + 58, 134, 52, "#ffffff", INK, 1.8, 8)
    s += text(sx + 89, sy + 80, "ядро CPU", 12.5, INK, "middle", "bold")
    s += text(sx + 89, sy + 97, "виконує код", 9.5, GREY, "middle")
    # вбудована SRAM
    s += rect(sx + 184, sy + 58, 134, 52, "#ffffff", INK, 1.8, 8)
    s += text(sx + 251, sy + 78, "вбудована SRAM", 11, INK, "middle", "bold")
    s += text(sx + 251, sy + 95, "сотні КіБ · дуже швидка", 9, GREY, "middle")
    # кеш
    s += rect(sx + 22, sy + 126, 134, 50, "#f4f7f4", GREEN, 1.8, 8)
    s += text(sx + 89, sy + 146, "кеш", 12, GREEN, "middle", "bold")
    s += text(sx + 89, sy + 162, "тримає гарячі дані", 9, GREY, "middle")
    # контролер зовнішньої пам'яті
    s += rect(sx + 184, sy + 126, 134, 50, "#fff8e8", AMBER, 1.8, 8)
    s += text(sx + 251, sy + 146, "контролер", 11, INK, "middle", "bold")
    s += text(sx + 251, sy + 162, "зовнішньої пам'яті", 10, INK, "middle")
    # підпис: чому потрібна зовнішня
    s += text(sx + sw / 2, sy + 206, "вбудованої SRAM — лічені сотні КіБ:", 10, GREY, "middle", style="italic")
    s += text(sx + sw / 2, sy + 222, "на кадр дисплея чи довгий звук не вистачає", 10, GREY, "middle", style="italic")
    # дві шини вниз: до флеші та PSRAM (спільний контролер)
    s += text(sx + sw / 2, sy + 252, "одна периферія обслуговує ОБИДВА зовнішні чипи", 9.5, INK, "middle", "bold")
    s += text(sx + sw / 2, sy + 268, "(часто на спільних лініях, різні CS)", 9, GREY, "middle", style="italic")

    # ── шина SPI/QSPI ──
    bx0 = sx + sw
    bx1 = 560
    ys = [sy + 132, sy + 148, sy + 164]
    s += text((bx0 + bx1) / 2, sy + 118, "шина SPI / QSPI", 11.5, INK, "middle", "bold")
    s += line(bx0, ys[0], bx1, ys[0], INK, 2)   # CS/CLK
    s += line(bx0, ys[1], bx1, ys[1], RED, 2)    # дані туди
    s += line(bx0, ys[2], bx1, ys[2], BLUE, 2)   # дані назад
    s += arrow((bx0 + bx1) / 2 - 6, ys[1], (bx0 + bx1) / 2 + 16, ys[1], RED, 2)
    s += arrow((bx0 + bx1) / 2 + 16, ys[2], (bx0 + bx1) / 2 - 6, ys[2], BLUE, 2)
    s += text(bx0 + 6, ys[0] - 5, "CS · CLK", 9, GREY, "start")
    s += text((bx0 + bx1) / 2, sy + 192, "1 лінія даних (SPI) або 4 (QSPI)", 9, GREY, "middle", style="italic")

    # ── зовнішній чип PSRAM праворуч ──
    fx, fy, fw, fh = 560, 96, 290, 300
    s += rect(fx, fy, fw, fh, "#fdf4f4", RED, 2.2, 12)
    s += text(fx + fw / 2, fy + 24, "зовнішній чип PSRAM", 13.5, RED, "middle", "bold")
    s += text(fx + fw / 2, fy + 42, "корпус SOIC-8 · 2–16 МіБ", 10, GREY, "middle", style="italic")
    # верх: інтерфейс
    s += rect(fx + 26, fy + 58, fw - 52, 44, "#ffffff", INK, 1.8, 8)
    s += text(fx + fw / 2, fy + 78, "логіка інтерфейсу SPI", 11.5, INK, "middle", "bold")
    s += text(fx + fw / 2, fy + 94, "назовні поводиться як SRAM", 9, GREY, "middle")
    # середина: масив комірок DRAM
    s += rect(fx + 26, fy + 116, fw - 52, 56, "#fff8e8", AMBER, 1.8, 8)
    s += text(fx + fw / 2, fy + 138, "масив комірок: транзистор + конденсатор", 10, INK, "middle", "bold")
    s += text(fx + fw / 2, fy + 155, "щільно й дешево (як DRAM, §3.6.3)", 9.5, GREY, "middle", style="italic")
    # низ: схований лічильник оновлення
    s += rect(fx + 26, fy + 186, fw - 52, 50, "#f4f7f4", GREEN, 1.8, 8)
    s += text(fx + fw / 2, fy + 206, "вбудоване самооновлення", 11, GREEN, "middle", "bold")
    s += text(fx + fw / 2, fy + 222, "чип сам освіжає заряд — зовні не видно", 9, GREY, "middle")
    s += text(fx + fw / 2, fy + 258, "летка: при вимкненні все зникає (§3.6.3)", 9.5, GREY, "middle", style="italic")
    s += text(fx + fw / 2, fy + 276, "звідси й «pseudo-SRAM»: DRAM, що вдає SRAM", 9.5, RED, "middle", "bold")

    # нижня плашка-висновок
    s += rect(60, 414, W - 120, 64, "#f7f9fc", BLUE, 1.8, 10)
    s += text(W / 2, 438, "PSRAM розширює саме RAM (летку, для змінних і буферів) — на відміну від NOR-флеші поруч (§3.6.3c), що тримає код.",
              11.2, INK, "middle", "bold")
    s += text(W / 2, 460, "Плата за дешевину й місткість — доступ через повільну послідовну шину, а не напряму, як до вбудованої SRAM.",
              10.5, GREY, "middle", style="italic")
    save("fig-19-8c-1-blockdiagram.svg", s)


# ════════════ Рис. 3.6.8c.2 — розпіновка SOIC-8 і підключення ════════════════
# Та сама вісімка ніжок, що й у флеші: 4 лінії QSPI + живлення; на платі модуля
# PSRAM і Flash часто сидять на спільних лініях, відрізняючись лише CS.
def fig_pinout():
    W, H = 900, 520
    s = header(W, H)
    s += text(W / 2, 34, "Розпіновка SOIC-8 і підключення: ті самі лінії, що й у флеші", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "вісім ніжок; у режимі QSPI всі чотири лінії даних возять і команду, і дані — це й дає вищу швидкість, ніж проста SPI",
              11.0, GREY, "middle", style="italic")

    # корпус
    bx, by, bw, bh = 350, 96, 200, 250
    s += rect(bx, by, bw, bh, "#fafafa", INK, 2.2, 10)
    s += circle(bx + 22, by + 22, 6, "#fff", INK, 1.8)  # маркер 1-ї ніжки
    s += text(bx + bw / 2, by + 36, "PSRAM", 14, INK, "middle", "bold")
    s += text(bx + bw / 2, by + 56, "pseudo-SRAM", 11, GREY, "middle", style="italic")
    s += text(bx + bw / 2, by + 80, "(інтерфейс QSPI)", 10, GREY, "middle", style="italic")
    s += text(bx + bw / 2, by + bh - 14, "вид зверху", 10, GREY, "middle", style="italic")

    left = [
        ("1", "CE#", "вибір чипа (низький = слухай мене)", INK),
        ("2", "SO / IO1", "дані (у QSPI — одна з 4 ліній)", BLUE),
        ("3", "IO2", "лінія даних (тримати з підтяжкою)", GREY),
        ("4", "GND", "земля", INK),
    ]
    right = [
        ("8", "VCC", "живлення 3.3 В", RED),
        ("7", "IO3", "лінія даних (тримати з підтяжкою)", GREY),
        ("6", "SCLK", "такт від контролера", INK),
        ("5", "SI / IO0", "дані (у QSPI — одна з 4 ліній)", RED),
    ]
    pin_y = [by + 52, by + 110, by + 168, by + 226]
    for (num, name, desc, col), y in zip(left, pin_y):
        s += line(bx - 34, y, bx, y, col, 2)
        s += rect(bx - 30, y - 9, 18, 18, "#fff", col, 1.6, 3)
        s += text(bx - 21, y + 5, num, 11, col, "middle", "bold")
        s += text(bx - 44, y - 4, name, 12, col, "end", "bold")
        s += text(bx - 44, y + 13, desc, 9.0, GREY, "end")
    for (num, name, desc, col), y in zip(right, pin_y):
        s += line(bx + bw, y, bx + bw + 34, y, col, 2)
        s += rect(bx + bw + 12, y - 9, 18, 18, "#fff", col, 1.6, 3)
        s += text(bx + bw + 21, y + 5, num, 11, col, "middle", "bold")
        s += text(bx + bw + 44, y - 4, name, 12, col, "start", "bold")
        s += text(bx + bw + 44, y + 13, desc, 9.0, GREY, "start")

    # легенда: чотири лінії даних QSPI + живлення
    s += rect(60, 372, W - 120, 60, "#f7f9fc", BLUE, 1.8, 10)
    s += text(W / 2, 394, "QSPI: чотири лінії даних IO0–IO3 працюють разом — учетверо більше бітів за такт, ніж проста SPI з однією лінією.",
              11.0, INK, "middle", "bold")
    s += text(W / 2, 416, "Плюс CE# (вибір чипа), SCLK (такт), VCC = 3.3 В і GND. Це та сама вісімка ніжок, що в SPI-флеші поруч.",
              10.3, GREY, "middle", style="italic")

    # плашка: спільна шина, різні CS (місток до «перший байт» і граблів)
    s += rect(60, 442, W - 120, 64, "#f4f7f4", GREEN, 1.8, 10)
    s += text(W / 2, 466, "На готовому модулі PSRAM і Flash часто сидять на СПІЛЬНИХ лініях CLK/IO, а розрізняє їх лише окремий CE#:",
              10.8, INK, "middle", "bold")
    s += text(W / 2, 488, "контролер опускає потрібний CE# — і говорить саме з тим чипом. Тому «зайняти» ці піни під щось інше не можна.",
              10.3, GREY, "middle", style="italic")
    save("fig-19-8c-2-pinout.svg", s)


# ════════════ Рис. 3.6.8c.3 — сходинки затримки + коли вмикати ═══════════════
# Чому PSRAM повільніша: драбина «реєстр → SRAM → влучання в кеш → промах у
# PSRAM», і панель рішення «що лишати у вбудованій SRAM, що можна в PSRAM».
def fig_speed_decision():
    W, H = 900, 560
    s = header(W, H)
    s += text(W / 2, 34, "Чим повільніша за вбудовану SRAM — і коли її варто вмикати", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "що далі від ядра живе байт, то довша дорога до нього: вбудована SRAM — поряд, PSRAM — за повільною шиною через кеш",
              11.0, GREY, "middle", style="italic")

    # ── драбина затримки (горизонтальні смуги, довжина ∝ затримці, лог-шкала) ──
    bx = 250
    rows = [
        ("регістр у ядрі", 8,  GREEN, "0 тактів — вже в ядрі (§3.5.2)"),
        ("вбудована SRAM", 26, GREEN, "≈1–2 такти — поряд, на кристалі"),
        ("PSRAM: влучання в кеш", 70, AMBER, "як SRAM — копія вже у швидкому кеші"),
        ("PSRAM: промах (по шині)", 300, RED, "десятки тактів — їхати по SPI/QSPI"),
    ]
    y0 = 92
    rh = 30
    gap = 18
    s += text(bx, y0 - 10, "час доступу (умовно, що довша смуга — то довше чекати)", 10, GREY, "start", style="italic")
    for i, (lab, length, col, note) in enumerate(rows):
        y = y0 + i * (rh + gap)
        s += text(bx - 12, y + rh / 2 + 5, lab, 11.5, INK, "end", "bold")
        s += rect(bx, y, length, rh, col, col, 1, 5)
        s += text(bx + length + 10, y + rh / 2 + 5, note, 10, GREY, "start")
    # підпис масштабу
    s += text(bx, y0 + 4 * (rh + gap) - 4, "(шкала стиснена — реальний розрив «промах vs SRAM» ще більший)",
              9, GREY, "start", style="italic")

    # ── панель рішення: що лишати у вбудованій SRAM / що можна в PSRAM ──
    py = 300
    s += text(W / 2, py, "Коли вмикати PSRAM — і що в ній НЕ тримати", 14, INK, "middle", "bold")

    # ліва колонка: годиться для PSRAM (велике й нечасте)
    lx, lw = 60, 380
    s += rect(lx, py + 16, lw, 150, "#f4f7f4", GREEN, 1.8, 10)
    s += text(lx + lw / 2, py + 38, "✓ годиться для PSRAM", 12.5, GREEN, "middle", "bold")
    s += text(lx + lw / 2, py + 56, "велике й нечасте — повільність губиться", 9.5, GREY, "middle", style="italic")
    good = [
        "кадр дисплея (десятки–сотні КіБ)",
        "буфер звуку чи запису",
        "великий рядок JSON / HTML",
        "кеш зображень, таблиці, історія логів",
    ]
    for i, g in enumerate(good):
        yy = py + 78 + i * 21
        s += text(lx + 24, yy, "•", 12, GREEN, "start", "bold")
        s += text(lx + 40, yy, g, 10.5, INK, "start")

    # права колонка: лишати у вбудованій SRAM (гаряче й критичне за часом)
    rx2, rw2 = 460, 380
    s += rect(rx2, py + 16, rw2, 150, "#fdf4f4", RED, 1.8, 10)
    s += text(rx2 + rw2 / 2, py + 38, "✗ лишати у вбудованій SRAM", 12.5, RED, "middle", "bold")
    s += text(rx2 + rw2 / 2, py + 56, "гаряче й критичне за часом — кожен такт важить", 9.5, GREY, "middle", style="italic")
    bad = [
        "змінні в гарячих циклах",
        "обробники переривань (мають бути швидкі)",
        "буфери, які смикає периферія напряму",
        "стек задач реального часу",
    ]
    for i, b in enumerate(bad):
        yy = py + 78 + i * 21
        s += text(rx2 + 24, yy, "•", 12, RED, "start", "bold")
        s += text(rx2 + 40, yy, b, 10.5, INK, "start")

    # нижній підсумок
    s += rect(60, py + 178, W - 120, 56, "#f7f9fc", BLUE, 1.8, 10)
    s += text(W / 2, py + 200, "Правило те саме, що для будь-якої повільної пам'яті: тримай поряд лише гаряче, а велике й рідкісне відправ далі.",
              10.8, INK, "middle", "bold")
    s += text(W / 2, py + 220, "PSRAM не «прискорює» МК — вона дає МІСЦЕ під те, що інакше просто не влізло б у вбудовану SRAM.",
              10.3, GREY, "middle", style="italic")
    save("fig-19-8c-3-speed-decision.svg", s)


if __name__ == "__main__":
    fig_blockdiagram()
    fig_pinout()
    fig_speed_decision()
    print("done.")
