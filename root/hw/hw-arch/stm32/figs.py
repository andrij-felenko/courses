# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── periph-philosophy: дві філософії інтеграції STM32 vs ESP32 ────────────────
# Ідея: один чип ставить на точну провідну периферію (таймери/АЦП/DMA), другий —
# на радіо й гнучкі програмовані блоки; колонка проти колонки робить вибір зримим.

def fig_periph_philosophy():
    W, H = 820, 470
    p = []
    BLU1, BLU2 = "#1a5276", "#2471a3"

    def column(x0, head, headfill, headcol, rows, rowfill):
        out = [rect(x0, 55, 310, 44, fill=headfill, stroke=headcol, sw=2.5, rx=8),
               text(x0 + 155, 83, head, size=14, color=headcol, bold=True)]
        ry = 110
        for title, sub in rows:
            out.append(rect(x0 + 8, ry, 294, 50, fill=rowfill, stroke=headcol, sw=1.2, rx=5))
            out.append(text(x0 + 18, ry + 18, "▸ " + title, size=12, color=headcol, anchor="start", bold=True))
            out.append(mtext(x0 + 18, ry + 36, sub, size=10, color=MUTED, anchor="start"))
            ry += 60
        return out

    stm = [("Advanced-таймери", "мертвий час, 6 компл. ШІМ\n(трифазний міст)"),
           ("АЦП × кілька синхронно", "запуск від таймера, у фазі з ШІМ"),
           ("DMA багатоканальний", "незалежні канали з пріоритетами"),
           ("SWD / JTAG на борту", "відлагодження одразу, без містків"),
           ("Без радіо", "потрібен зовнішній модуль")]
    esp = [("MCPWM / RMT / I2S", "гнучкі, та фіксовані блоки"),
           ("АЦП нелінійний", "обмежена точність вибірки"),
           ("DMA при SPI/I2S", "прив'язаний до інтерфейсів"),
           ("Wi-Fi + BLE на борту", "ключова перевага класу"),
           ("Більший струм спокою", "радіо їсть, поки не вимкнеш")]

    p += column(60, "STM32-клас (Cortex-M)", "#d6eaf8", BLU1, stm, "#eaf3fc")
    p += column(450, "ESP32 (Xtensa / RISC-V)", "#d2e4f5", BLU2, esp, "#e5f0fa")
    p.append(text(W / 2, 452, "STM32 виграє точною провідною периферією; ESP32 — вбудованим радіо.",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "periph-philosophy.svg"), W, H, *p,
           title="Дві філософії інтеграції: точна периферія STM32 проти радіо ESP32")


# ── three-phase: чому трифазний міст любить advanced-таймер ───────────────────
# Ідея: один advanced-таймер тримає три комплементарні пари (верх/низ кожного
# плеча) з мертвим часом, а в тій самій точці циклу синхронно ловить струм АЦП.

def fig_three_phase():
    W, H = 740, 380
    p = []
    GRN, RED = "#1e8449", "#c0392b"

    # центр — advanced-таймер
    tb, tw, th = textbox(W / 2, 80, "Advanced-control таймер\n(один блок)",
                         size=13, bold=True, fill="#d6eaf8", stroke="#1a5276", sw=2.2, pad=12)
    p.append(tb)

    # три плеча мосту
    legs = ["A", "B", "C"]
    bx0 = 110
    gap = 210
    by = 210
    for i, lab in enumerate(legs):
        cx = bx0 + i * gap
        # пара комплементарних ключів
        p.append(rect(cx - 46, by, 42, 40, fill="#fdecea", stroke=RED, sw=1.8, rx=5))
        p.append(text(cx - 25, by + 25, "верх", size=11, color=RED, bold=True))
        p.append(rect(cx + 4, by, 42, 40, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=5))
        p.append(text(cx + 25, by + 25, "низ", size=11, color=NEG, bold=True))
        # від таймера до плеча
        p.append(arrow(W / 2 + (cx - W / 2) * 0.18, 80 + th / 2, cx, by - 4, color="#1a5276", sw=1.6))
        p.append(text(cx, by - 10, "пара " + lab + " (мертвий час)", size=10, color=MUTED))
        # точка вимірювання струму
        p.append(circle(cx, by + 78, 16, fill="#d5f5e3", stroke=GRN, sw=2))
        p.append(text(cx, by + 82, "Iₓ", size=12, color=GRN, bold=True))
        p.append(line(cx, by + 40, cx, by + 62, color=GRN, sw=1.6))

    # синхронний захват: таймер диктує момент вибірки
    sy = 318
    p.append(line(bx0, sy, bx0 + 2 * gap, sy, color=GRN, sw=1.6, dash="6 4"))
    p.append(text(W / 2, sy - 8, "АЦП × 3 — захват струму в тій самій точці ШІМ-циклу",
                  size=11, color=GRN, bold=True))
    p.append(text(W / 2, H - 16,
                  "шість узгоджених виходів і синхронний захват — з одного таймера",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "three-phase.svg"), W, H, *p,
           title="Трифазний міст: три комплементарні пари + синхронний захват струму")


# ── nucleo-anatomy: дві плати в одній + Blue Pill для контрасту ───────────────
# Ідея: верх плати Nucleo — повноцінний ST-Link-зонд, низ — цільовий STM32, між
# ними лінія розламу; праворуч голий Blue Pill, де зонда нема й SWD виведено назовні.

def fig_nucleo_anatomy():
    W, H = 820, 480
    p = []
    BLU, GRN, ORA, RED = "#1a5276", "#1e8449", "#d68910", "#c0392b"

    # ── ліва панель: Nucleo ──
    p.append(rect(20, 48, 490, 400, fill="#f8f9fa", stroke=INK, sw=2, rx=10))
    p.append(text(265, 66, "Nucleo (дві плати в одній)", size=13, color=INK, bold=True))

    # верх: зонд
    p.append(rect(30, 76, 470, 160, fill="#d6eaf8", stroke=BLU, sw=2, rx=7))
    p.append(text(265, 95, "ST-Link-зонд (верхня частина плати)", size=12, color=BLU, bold=True))
    p.append(fitbox(58, 125, 64, 46, "USB\n(до ПК)", size=11, fill="#d5e8fc", stroke=BLU))
    p.append(arrow(125, 148, 185, 148, color=BLU, sw=1.8))
    b, bw, bh = textbox(225, 135, "ST-Link MCU\n(програматор)", size=11, bold=True,
                        fill="#d6eaf8", stroke=BLU, sw=2)
    p.append(b)
    p.append(fitbox(141, 150, 168, 56,
                    "прошиває по SWD\nвідлагоджує (breakpoint)\nVCP (virtual COM port)",
                    size=10, fill="#eaf3fb", stroke=BLU, sw=1.0))
    p.append(arrow(265, 206, 265, 240, color=BLU, sw=2))
    p.append(fitbox(291, 208, 38, 31, "SWD", size=11, fill="#d6eaf8", stroke=BLU))

    # лінія розламу
    p.append(line(30, 244, 500, 244, color=RED, sw=2.5, dash="8 4"))
    p.append(text(265, 256, "break-apart: відламай → окремий програматор",
                  size=11, color=RED, bold=True))

    # низ: ціль
    p.append(rect(30, 266, 470, 167, fill="#d5f5e3", stroke=GRN, sw=2, rx=7))
    p.append(text(265, 282, "Цільовий STM32 (нижня частина плати)", size=12, color=GRN, bold=True))
    b, bw, bh = textbox(110, 308, "STM32\n(ціль)", size=13, bold=True,
                        fill="#d5f5e3", stroke=GRN, sw=2)
    p.append(b)
    p.append(fitbox(217, 296, 76, 31, "LDO 3.3 В", size=11, fill="#d5f5e3", stroke=GRN))
    p.append(fitbox(324, 290, 112, 50, "Гребінки\nArduino + Morpho\n(всі ніжки)",
                    size=10, fill="#d5f5e3", stroke=GRN, sw=1.5))
    p.append(fitbox(120, 390, 70, 31, "RESET", size=11, fill=FILL, stroke=INK))
    p.append(fitbox(206, 390, 128, 31, "LED користувача", size=11, fill=FILL, stroke=INK))
    p.append(fitbox(352, 390, 96, 31, "3.3 В логіка", size=11, fill="#d5f5e3", stroke=GRN))

    # ── права панель: Blue Pill ──
    p.append(rect(525, 48, 275, 400, fill="#fef9f0", stroke=ORA, sw=2, rx=10))
    p.append(text(662, 66, "Blue Pill", size=13, color=ORA, bold=True))
    p.append(text(662, 84, "(голий чип, зонда нема)", size=11, color=MUTED))
    p.append(text(662, 122, "бортового зонда немає", size=11, color=RED, bold=True))
    b, bw, bh = textbox(662, 160, "STM32\n(той самий клас)", size=13, bold=True,
                        fill="#fdebd0", stroke=ORA, sw=2)
    p.append(b)
    p.append(fitbox(595, 214, 134, 43, "Кварц + LDO\n+ 2 LED + USB", size=10,
                    fill="#fef5e7", stroke=ORA, sw=1.5))
    p.append(rect(590, 285, 144, 64, fill="#fdebd0", stroke=RED, sw=2, rx=5))
    p.append(text(662, 307, "4-пін SWD (зовні)", size=11, color=RED, bold=True))
    p.append(text(662, 325, "SWCLK · SWDIO · GND · 3V3", size=10, color=MUTED))
    p.append(arrow(662, 349, 662, 376, color=RED, sw=1.8))
    p.append(fitbox(603, 372, 118, 43, "Зовнішній ST-Link\n(або від Nucleo)", size=10,
                    fill="#fdecea", stroke=RED, sw=1.5))

    p.append(text(410, 470,
                  "Nucleo: USB → ST-Link → SWD → ціль; відламав верх → програматор для Blue Pill.",
                  size=10, color=MUTED))

    render(os.path.join(OUT, "nucleo-anatomy.svg"), W, H, *p,
           title="Анатомія Nucleo і Blue Pill")


# ── power-jumpers: звідки живиться чип на Nucleo і на Blue Pill ───────────────
# Ідея: на Nucleo джерело обирають фізичні джемпери (кілька шляхів), на Blue Pill —
# два взаємовиключні шляхи (через LDO або в обхід); скрізь логіка 3.3 В.

def fig_power_jumpers():
    W, H = 800, 420
    p = []
    BLU, ORA, RED, GRN = "#1a5276", "#d68910", "#c0392b", "#1e8449"

    # ── Nucleo ──
    p.append(rect(20, 50, 380, 330, fill="#f4f9fd", stroke=BLU, sw=2, rx=10))
    p.append(text(210, 70, "Nucleo: джемпери обирають джерело", size=12, color=BLU, bold=True))
    sources = [
        ("USB через ST-Link", "#d6eaf8"),
        ("зовнішні 5 В (VIN)", "#d6eaf8"),
        ("готові 3.3 В", "#d6eaf8"),
        ("живити зовнішню ціль\nвід бортового ST-Link", "#eaf3fb"),
    ]
    sy = 92
    for lab, fill in sources:
        p.append(fitbox(40, sy, 200, 46, lab, size=10, fill=fill, stroke=BLU, sw=1.4))
        p.append(text(252, sy + 20, "джемпер", size=10, color=MUTED, anchor="start"))
        p.append(arrow(248, sy + 23, 300, sy + 23, color=BLU, sw=1.5))
        sy += 58
    b, bw, bh = textbox(330, 230, "ціль\n3.3 В", size=12, bold=True,
                        fill="#d5f5e3", stroke=GRN, sw=2, min_w=80)
    p.append(b)
    p.append(text(210, 366, "кілька шляхів — але один за раз", size=10, color=MUTED, italic=True))

    # ── Blue Pill ──
    p.append(rect(420, 50, 360, 330, fill="#fef9f0", stroke=ORA, sw=2, rx=10))
    p.append(text(600, 70, "Blue Pill: два взаємовиключні шляхи", size=12, color=ORA, bold=True))

    p.append(fitbox(445, 110, 120, 46, "5 В на USB / 5V-пін", size=10, fill="#fdebd0", stroke=ORA))
    p.append(arrow(566, 133, 612, 133, color=ORA, sw=1.6))
    p.append(fitbox(612, 110, 70, 46, "LDO\n3.3 В", size=11, fill="#fef5e7", stroke=ORA))
    p.append(arrow(682, 133, 720, 133, color=ORA, sw=1.6))

    p.append(fitbox(445, 200, 120, 46, "готові 3.3 В\nна 3V3-пін", size=10, fill="#fdebd0", stroke=ORA))
    p.append(text(600, 224, "в обхід LDO", size=10, color=MUTED))
    p.append(arrow(566, 223, 720, 223, color=ORA, sw=1.6))

    b, bw, bh = textbox(745, 178, "чип\n3.3 В", size=11, bold=True,
                        fill="#fdebd0", stroke=ORA, sw=2, min_w=56)
    p.append(b)

    p.append(rect(445, 280, 310, 64, fill="#fdecea", stroke=RED, sw=2, rx=6))
    p.append(text(600, 302, "не подавати з двох боків разом", size=11, color=RED, bold=True))
    p.append(text(600, 322, "конфлікт джерел псує LDO або чип", size=10, color=MUTED))

    p.append(text(W / 2, H - 14,
                  "Скрізь логіка 3.3 В; перевернутий джемпер — найчастіша причина «плата мертва».",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "power-jumpers.svg"), W, H, *p,
           title="Звідки живиться чип: джемпери Nucleo проти двох шляхів Blue Pill")


if __name__ == "__main__":
    fig_periph_philosophy()
    fig_three_phase()
    fig_nucleo_anatomy()
    fig_power_jumpers()
    print("OK: figures written to", OUT)
