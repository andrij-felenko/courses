# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «5V реле-модуль (Songle SRD-05VDC)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Що всередині: керуючий ланцюг МК → опто → транзистор → котушка ─────────
def fig_inside():
    W, H = 940, 500
    f = [text(W / 2, 30, "Сигнальний бік і силовий бік — між ними лише світло",
              size=16, bold=True)]

    # межа ізоляції — вертикальна пунктирна лінія
    isox = 470
    f.append(line(isox, 70, isox, 430, color=MUTED, sw=1.6, dash="7 6"))
    f.append(text(isox, 60, "бар'єр ізоляції (оптопара)", size=11, color=MUTED, bold=True))

    # ── лівий (керуючий) бік ──
    f.append(text(210, 92, "КЕРУЮЧИЙ БІК  ·  логіка 5 В", size=12, color=NEG, bold=True))

    # вивід IN
    f.append(circle(70, 150, 8, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(text(70, 132, "IN", size=12, color=NEG, bold=True))
    # резистор на світлодіод оптопари
    f.append(line(78, 150, 150, 150, color=INK, sw=2))
    f.append(rect(150, 142, 46, 16, fill=BG, stroke=INK, sw=1.5, rx=3))
    f.append(text(173, 154, "R", size=10, color=INK))
    # світлодіод оптопари
    f.append(line(196, 150, 250, 150, color=INK, sw=2))
    f.append(text(280, 130, "світлодіод", size=10, color=MUTED))
    f.append(text(280, 144, "оптопари", size=10, color=MUTED))
    # трикутник-діод
    f.append('<path d="M300 138 L300 162 L322 150 Z" fill="%s" stroke="%s" stroke-width="1.5"/>' % ("#fdf6e3", INK))
    f.append(line(322, 138, 322, 162, color=INK, sw=2))
    # промінь світла до фототранзистора
    f.append(line(322, 150, isox, 150, color=POS, sw=2.2, dash="3 4"))
    f.append(text(400, 140, "світло", size=9.5, color=POS, italic=True))
    # VCC-логіка вгорі-ліворуч
    f.append(circle(70, 220, 8, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(text(70, 242, "VCC", size=11, color=NEG, bold=True))
    f.append(text(150, 224, "живлення логіки (5 В)", size=10, color=MUTED, anchor="start"))
    # GND
    f.append(circle(70, 290, 8, fill=BG, stroke=INK, sw=2))
    f.append(text(70, 312, "GND", size=11, color=INK, bold=True))

    # ── правий (силовий) бік ──
    f.append(text(710, 92, "СИЛОВИЙ БІК  ·  котушка й контакти", size=12, color=POS, bold=True))

    # фототранзистор
    f.append(circle(isox + 40, 150, 16, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(isox + 40, 178, "фото-", size=9, color=POS))
    f.append(text(isox + 40, 190, "транзистор", size=9, color=POS))
    # драйвер-транзистор
    dx = 620
    f.append(circle(dx, 150, 18, fill="#fdf6e3", stroke=INK, sw=1.8))
    f.append(text(dx, 154, "Q", size=13, color=INK, bold=True))
    f.append(text(dx, 186, "ключ-транзистор", size=9.5, color=MUTED))
    f.append(line(isox + 56, 150, dx - 18, 150, color=INK, sw=2))

    # котушка реле (прямокутник з витками)
    cx, cy, cw, ch = 720, 110, 120, 60
    f.append(rect(cx, cy, cw, ch, fill="#fafbfc", stroke=INK, sw=1.7, rx=8))
    f.append(text(cx + cw / 2, cy + 26, "КОТУШКА", size=12, color=INK, bold=True))
    f.append(text(cx + cw / 2, cy + 44, "70 Ω · 71 мА", size=10, color=MUTED))
    # від транзистора вгору до котушки (колектор виходить збоку від «Q», не крізь напис)
    f.append(line(dx + 18, 150, dx + 40, 150, color=INK, sw=2))
    f.append(line(dx + 40, 150, dx + 40, cy + ch, color=INK, sw=2))
    f.append(line(dx + 40, cy + ch, cx, cy + ch, color=INK, sw=2))
    # JD-VCC живить котушку згори
    f.append(circle(cx + cw + 20, cy + 10, 8, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(cx + cw + 20, cy - 8, "JD-VCC", size=10, color=POS, bold=True))
    f.append(line(cx + cw, cy + 10, cx + cw + 12, cy + 10, color=POS, sw=2))

    # діод-глушник паралельно котушці
    diox = cx - 40
    f.append('<path d="M%d %d L%d %d L%d %d Z" fill="%s" stroke="%s" stroke-width="1.5"/>'
             % (diox - 8, cy + 8, diox - 8, cy + 24, diox + 6, cy + 16, "#eef6ef", FIELD))
    f.append(line(diox + 6, cy + 6, diox + 6, cy + 26, color=FIELD, sw=2))
    f.append(line(diox - 8, cy - 6, diox - 8, cy + 8, color=FIELD, sw=1.8))
    f.append(line(diox - 8, cy - 6, cx, cy - 6, color=FIELD, sw=1.8))
    f.append(line(cx, cy - 6, cx, cy, color=FIELD, sw=1.8))
    f.append(line(diox + 6, cy + 26, diox + 6, cy + ch, color=FIELD, sw=1.8))
    f.append(line(diox - 8, cy + 8, diox - 8, cy + 24, color=FIELD, sw=1.8))
    f.append(text(diox - 60, cy + 4, "діод-", size=9.5, color=FIELD, bold=True, anchor="start"))
    f.append(text(diox - 60, cy + 18, "глушник", size=9.5, color=FIELD, bold=True, anchor="start"))
    f.append(text(diox - 60, cy + 32, "(flyback)", size=8.5, color=FIELD, anchor="start"))

    # контактна група (COM/NO/NC) внизу праворуч
    ky = 330
    f.append(text(720, ky - 22, "контактна група (SPDT)", size=11, color=POS, bold=True))
    f.append(circle(650, ky, 7, fill=BG, stroke=INK, sw=2))
    f.append(text(650, ky + 24, "COM", size=10, color=INK, bold=True))
    f.append(circle(790, ky - 26, 7, fill=BG, stroke=POS, sw=2))
    f.append(text(818, ky - 22, "NO", size=10, color=POS, bold=True, anchor="start"))
    f.append(circle(790, ky + 26, 7, fill=BG, stroke=NEG, sw=2))
    f.append(text(818, ky + 30, "NC", size=10, color=NEG, bold=True, anchor="start"))
    # рухомий контакт (спокій — на NC)
    f.append(line(657, ky, 786, ky + 24, color=INK, sw=2.4))
    # стрілка «котушка тягне»
    f.append(line(720, cy + ch + 8, 720, ky - 34, color=MUTED, sw=1.4, dash="4 4"))
    f.append(text(736, (cy + ch + ky) / 2, "тягне якір", size=9, color=MUTED, italic=True, anchor="start"))

    b, bw, bh = textbox(W / 2, H - 26,
                        "струм у ніжку IN засвічує оптопару; світло вмикає транзистор, той пускає струм у котушку — і магніт перекидає контакт із NC на NO",
                        size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "inside.svg"), W, H, *f)


# ── 2. Механізм: як котушка перекидає контакт (спокій vs увімкнено) ───────────
def fig_mechanism():
    W, H = 880, 470
    f = [text(W / 2, 30, "Електромагніт перекидає пружинний контакт", size=16, bold=True)]

    def draw_state(ox, title, energized):
        # рамка стану
        f.append(rect(ox, 70, 340, 300, fill="#fafbfc", stroke=MUTED, sw=1.4, rx=12))
        f.append(text(ox + 170, 96, title, size=13, bold=True,
                      color=(POS if energized else NEG)))

        # осердя + котушка
        coil_x, coil_y = ox + 40, 150
        f.append(rect(coil_x, coil_y, 60, 150, fill="#eef2f8", stroke=INK, sw=1.6, rx=6))
        # витки
        for i in range(6):
            yy = coil_y + 16 + i * 22
            f.append(line(coil_x, yy, coil_x + 60, yy, color=(POS if energized else MUTED), sw=2))
        f.append(text(coil_x + 30, coil_y + 170, "котушка", size=10.5, color=INK))
        if energized:
            f.append(text(coil_x + 30, coil_y - 12, "N ↕ S", size=12, color=POS, bold=True))
            f.append(text(coil_x + 30, coil_y - 28, "магніт", size=9.5, color=POS))

        # якір (рухома пластина) — шарнір угорі
        hinge_x, hinge_y = coil_x + 120, coil_y - 6
        f.append(circle(hinge_x, hinge_y, 5, fill=INK, stroke=INK, sw=1))
        f.append(text(hinge_x + 8, hinge_y - 4, "шарнір", size=9, color=MUTED, anchor="start"))
        if energized:
            # притягнутий до осердя
            arm_end = (coil_x + 66, coil_y + 120)
            f.append(text(coil_x + 96, coil_y + 60, "притягнуто", size=9, color=POS, italic=True, anchor="start"))
        else:
            # відпущений пружиною
            arm_end = (coil_x + 130, coil_y + 128)
        f.append(line(hinge_x, hinge_y, arm_end[0], arm_end[1], color=INK, sw=3))

        # пружина повернення
        sx = hinge_x + 40
        f.append(line(sx, hinge_y + 6, sx, hinge_y + 40, color=FIELD, sw=1.8))
        f.append(text(sx + 6, hinge_y + 26, "пружина", size=9, color=FIELD, anchor="start"))

        # три контакти праворуч
        cxx = ox + 250
        com_y = coil_y + 70
        no_y = coil_y + 30
        nc_y = coil_y + 116
        f.append(circle(cxx, no_y, 6, fill=BG, stroke=POS, sw=2))
        f.append(text(cxx + 14, no_y + 4, "NO", size=10, color=POS, bold=True, anchor="start"))
        f.append(circle(cxx, nc_y, 6, fill=BG, stroke=NEG, sw=2))
        f.append(text(cxx + 14, nc_y + 4, "NC", size=10, color=NEG, bold=True, anchor="start"))
        f.append(circle(cxx - 60, com_y, 6, fill=BG, stroke=INK, sw=2))
        f.append(text(cxx - 60, com_y + 20, "COM", size=10, color=INK, bold=True))
        # рухомий місток від якоря до COM, а COM торкається NO або NC
        f.append(line(arm_end[0], arm_end[1], cxx - 60, com_y, color=INK, sw=2))
        if energized:
            f.append(line(cxx - 54, com_y, cxx - 6, no_y, color=POS, sw=2.6))
        else:
            f.append(line(cxx - 54, com_y, cxx - 6, nc_y, color=NEG, sw=2.6))

    draw_state(30, "СПОКІЙ  ·  котушка знеструмлена", False)
    draw_state(500, "УВІМКНЕНО  ·  котушка під струмом", True)

    b, bw, bh = textbox(W / 2, H - 24,
                        "у спокої пружина тримає COM на NC; струм у котушці робить магніт, що перетягує якір — COM переходить на NO",
                        size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "mechanism.svg"), W, H, *f)


# ── 3. Розводка пін-у-пін: МК → модуль → навантаження (мережа) ────────────────
def fig_wiring():
    W, H = 940, 500
    f = [text(W / 2, 30, "Слабкий бік до мікроконтролера, силовий — у розрив дроту навантаження",
              size=15, bold=True)]

    # МК ліворуч
    mkx, mky, mkw, mkh = 40, 110, 160, 190
    f.append(rect(mkx, mky, mkw, mkh, fill="#eef2f8", stroke=INK, sw=1.7, rx=10))
    f.append(text(mkx + mkw / 2, mky + 26, "Мікроконтролер", size=12.5, bold=True))
    f.append(text(mkx + mkw / 2, mky + 44, "(Arduino / ESP32)", size=10, color=MUTED))
    mk = [("5V", POS, mky + 90), ("GPIO", NEG, mky + 130), ("GND", INK, mky + 168)]
    for lbl, col, y in mk:
        f.append(text(mkx + mkw - 12, y, lbl, size=11.5, bold=True, color=col, anchor="end"))

    # модуль у центрі
    ax, ay, aw, ah = 340, 90, 200, 230
    f.append(rect(ax, ay, aw, ah, fill="#fafbfc", stroke=MUTED, sw=1.7, rx=12))
    f.append(text(ax + aw / 2, ay + 24, "Реле-модуль", size=12.5, bold=True))
    f.append(text(ax + aw / 2, ay + 42, "SRD-05VDC + опто", size=10, color=MUTED))
    # три входи ліворуч (VCC/IN/GND)
    ins = [("VCC", POS, mky + 90), ("IN", NEG, mky + 130), ("GND", INK, mky + 168)]
    for lbl, col, y in ins:
        f.append(text(ax + 14, y, lbl, size=11, bold=True, color=col, anchor="start"))
        f.append(line(mkx + mkw, y, ax, y, color=col, sw=2.0))
    # блок-клема праворуч (COM/NO/NC)
    f.append(text(ax + aw / 2, ay + ah - 70, "гвинтова клема", size=10, color=INK))
    outs = [("NO", POS, ay + ah - 46), ("COM", INK, ay + ah - 26), ("NC", NEG, ay + ah - 6)]
    for i, (lbl, col, y) in enumerate(outs):
        f.append(text(ax + aw - 14, y, lbl, size=10.5, bold=True, color=col, anchor="end"))

    # мережа + лампа праворуч (силове коло)
    # джерело мережі
    nx, ny = 720, 130
    f.append(rect(nx, ny, 150, 60, fill="#fdecea", stroke=POS, sw=1.7, rx=8))
    f.append(text(nx + 75, ny + 26, "~230 В мережа", size=11.5, color=POS, bold=True))
    f.append(text(nx + 75, ny + 44, "(силове коло)", size=9.5, color=MUTED))
    # навантаження — лампа
    lx, ly = 795, 320
    f.append(circle(lx, ly, 26, fill="#fdf6e3", stroke=INK, sw=1.8))
    f.append(text(lx, ly + 5, "лампа", size=10.5, color=INK, bold=True))

    # силове коло: фаза → COM ; NO → лампа ; лампа → нейтраль
    comx = ax + aw
    comy = ay + ah - 26
    nox = ax + aw
    noy = ay + ah - 46
    # фаза мережі до COM (напис — над горизонтальним відрізком, не на ньому)
    f.append(line(nx, ny + 40, nx - 40, ny + 40, color=POS, sw=2.2))
    f.append(line(nx - 40, ny + 40, nx - 40, comy, color=POS, sw=2.2))
    f.append(line(nx - 40, comy, comx, comy, color=POS, sw=2.2))
    f.append(text((comx + nx - 40) / 2, comy - 14, "фаза → COM", size=9, color=POS, bold=True))
    # NO до лампи (напис зсунуто праворуч від вертикалі й нижче горизонталі COM)
    f.append(line(nox, noy, nox + 60, noy, color=INK, sw=2.2))
    f.append(line(nox + 60, noy, nox + 60, ly, color=INK, sw=2.2))
    f.append(line(nox + 60, ly, lx - 26, ly, color=INK, sw=2.2))
    f.append(text(nox + 70, noy + 34, "NO → лампа", size=9, color=INK, bold=True, anchor="start"))
    # лампа до нейтралі
    f.append(line(lx + 26, ly, nx + 150 + 10, ly, color=NEG, sw=2.2))
    f.append(line(nx + 160, ly, nx + 160, ny + 20, color=NEG, sw=2.2))
    f.append(line(nx + 160, ny + 20, nx + 150, ny + 20, color=NEG, sw=2.2))
    f.append(text(nx + 100, ly + 20, "нейтраль", size=9, color=NEG, bold=True))

    b, bw, bh = textbox(W / 2, H - 24,
                        "мікроконтролер керує лише лівими трьома ніжками; мережа тече крізь COM–NO і НЕ має спільної землі з логікою",
                        size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 4. Пастка старту: клац на завантаженні vs безпечний порядок ────────────
def fig_boot_glitch():
    """Дві часові діаграми поряд: наївний старт (реле клацає) і безпечний."""
    W, H = 940, 470
    f = [text(W / 2, 30, "Ніж клацнути на старті: порядок ініціалізації виводу",
              size=16, bold=True)]

    # осі: час іде праворуч; дві доріжки — рівень IN і стан реле
    def panel(ox, title, bad):
        col = POS if bad else FIELD
        f.append(rect(ox, 60, 400, 350, fill="#fafbfc", stroke=col, sw=1.6, rx=12))
        f.append(text(ox + 200, 86, title, size=13, bold=True, color=col))

        left = ox + 90        # де починаються доріжки
        right = ox + 380      # де закінчуються
        boot = ox + 175       # мить, коли setup() виставляє ніжку
        # позначка «живлення подано»
        f.append(line(left, 105, left, 390, color=MUTED, sw=1.2, dash="3 4"))
        f.append(text(left, 118, "живлення", size=8.5, color=MUTED, anchor="middle"))
        f.append(text(left, 130, "подано", size=8.5, color=MUTED, anchor="middle"))
        # позначка setup()
        f.append(line(boot, 105, boot, 390, color=NEG, sw=1.2, dash="3 4"))
        f.append(text(boot, 118, "setup()", size=8.5, color=NEG, anchor="middle"))

        # ── доріжка 1: рівень на IN ──
        y_hi, y_lo = 175, 225
        f.append(text(ox + 20, (y_hi + y_lo) / 2, "IN", size=11, color=INK, bold=True, anchor="middle"))
        f.append(text(right + 6, y_hi, "HIGH", size=8.5, color=MUTED, anchor="start"))
        f.append(text(right + 6, y_lo, "LOW", size=8.5, color=MUTED, anchor="start"))
        if bad:
            # до setup ніжка «висить» і просідає в LOW (вхід без підтяжки)
            f.append(line(left, y_lo, boot, y_lo, color=POS, sw=2.6))         # висить у LOW
            f.append(line(boot, y_lo, boot, y_hi, color=POS, sw=2.6))         # setup виставив HIGH
            f.append(line(boot, y_hi, right, y_hi, color=POS, sw=2.6))
            f.append(text((left + boot) / 2, y_lo + 16, "ніжка висить → LOW", size=8.5, color=POS, anchor="middle"))
        else:
            # ніжку тримає HIGH від початку (pull-up + правильний порядок)
            f.append(line(left, y_hi, right, y_hi, color=FIELD, sw=2.6))
            f.append(text((left + right) / 2, y_hi - 10, "тримаємо HIGH від початку", size=8.5, color=FIELD, anchor="middle"))

        # ── доріжка 2: стан реле (active-low: LOW на IN = увімкнено) ──
        yr_off, yr_on = 320, 280
        f.append(text(ox + 20, (yr_off + yr_on) / 2, "реле", size=10.5, color=INK, bold=True, anchor="middle"))
        f.append(text(right + 6, yr_on, "ON", size=8.5, color=MUTED, anchor="start"))
        f.append(text(right + 6, yr_off, "OFF", size=8.5, color=MUTED, anchor="start"))
        if bad:
            f.append(line(left, yr_on, boot, yr_on, color=POS, sw=2.6))       # клацнуло увімкнене
            f.append(line(boot, yr_on, boot, yr_off, color=POS, sw=2.6))
            f.append(line(boot, yr_off, right, yr_off, color=POS, sw=2.6))
            # виділити небажаний імпульс
            f.append(text((left + boot) / 2, yr_on - 12, "КЛАЦ", size=11, color=POS, bold=True, anchor="middle"))
            f.append(text((left + boot) / 2, yr_off + 18, "небажаний імпульс", size=8.5, color=POS, anchor="middle"))
        else:
            f.append(line(left, yr_off, right, yr_off, color=FIELD, sw=2.6))  # тихо, жодного клацання
            f.append(text((left + right) / 2, yr_off + 18, "жодного клацання", size=8.5, color=FIELD, anchor="middle"))

    panel(30, "НАЇВНО: pinMode перший", True)
    panel(490, "БЕЗПЕЧНО: спершу HIGH, тоді OUTPUT", False)

    b, bw, bh = textbox(W / 2, H - 24,
                        "на active-low модулі просіла ніжка = увімкнене реле; вистав HIGH ще ДО pinMode(OUTPUT) — і старт тихий",
                        size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "boot-glitch.svg"), W, H, *f)


if __name__ == "__main__":
    fig_inside()
    fig_mechanism()
    fig_wiring()
    fig_boot_glitch()
    print("OK: 4 figures ->", IMG)
