# -*- coding: utf-8 -*-
"""Фігури до теми «Контролер і вектор переривань» та вставки про контролери.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Контролер: збирає запити, відсіює заборонені, обирає важливіший ─────────
def fig_controller():
    W, H = 820, 380
    f = [text(W / 2, 30, "Контролер переривань: збирає запити, відсіює заборонені, обирає важливіший",
              size=15, bold=True)]

    # джерела ліворуч
    srcs = [("таймер", 1), ("GPIO", 1), ("UART", 0), ("радіо", 1)]
    sx, sw, sh = 70, 130, 40
    ys = [90, 150, 210, 270]
    cxL = sx + sw
    for (lab, en), y in zip(srcs, ys):
        col = INK if en else MUTED
        f.append(rect(sx, y, sw, sh, fill="#f4f6f8", stroke=col, sw=1.5))
        f.append(text(sx + sw / 2, y + 25, lab, size=12, color=col, bold=True))
        # лінія до контролера (стрілка для дозволених, пунктир-глухо для замаскованих)
        acol = INK if en else MUTED
        if en:
            f.append(arrow(cxL, y + sh / 2, 306, 190, color=acol, sw=1.8))
        else:
            f.append(line(cxL, y + sh / 2, 306, 190, color=acol, sw=1.2, dash="4,4"))
            f.append(text(cxL + 40, y + sh / 2 - 6, "замасковано", size=9.5, color=MUTED, italic=True))

    # контролер у центрі
    b, bw, bh = textbox(420, 190, "КОНТРОЛЕР\nдозвіл · пріоритет · вибір", size=12.5,
                        fill="#fff6e0", stroke="#caa24a", sw=2, bold=True, min_w=200)
    f.append(b)

    # ядро праворуч
    f.append(line(420 + bw / 2, 190, 660, 190, color=POS, sw=2.4))
    cb, _, _ = textbox(720, 190, "ЯДРО\n(процесор)", size=12.5, fill="#fdecea", stroke=POS, sw=2, bold=True)
    f.append(cb)
    f.append(text(560, 178, "пускає важливіший", size=10, color=POS, italic=True))

    b2, _, _ = textbox(W / 2, 350,
                       "без контролера ядро потонуло б у сигналах: він вирішує, кого і коли пустити",
                       size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b2)
    render(os.path.join(IMG, "controller.svg"), W, H, *f)


# ── 2. Повний шлях переривання у вісім кроків ─────────────────────────────────
def fig_full_flow():
    W, H = 900, 380
    f = [text(W / 2, 30, "Повний шлях переривання: вісім кроків від сигналу пристрою до повернення",
              size=15, bold=True)]

    steps = [
        ("1", "джерело\nпіднімає запит", INK),
        ("2", "контролер:\nдозвіл, пріоритет", INK),
        ("3", "сигнал\nпроцесору", INK),
        ("4", "ЗБЕРЕГТИ\nконтекст", POS),
        ("5", "знайти адресу\nу векторі", INK),
        ("6", "стрибок\nв обробник", INK),
        ("7", "обробник\nвиконується", INK),
        ("8", "ВІДНОВИТИ\nконтекст", POS),
    ]
    # дві лінії по 4
    bw, bh = 180, 70
    gapx = 30
    x0 = (W - (4 * bw + 3 * gapx)) / 2
    rows = [(90, steps[:4]), (230, steps[4:])]
    centers = {}
    for ry, row in rows:
        for i, (n, lab, col) in enumerate(row):
            x = x0 + i * (bw + gapx)
            fillc = "#fdecea" if col == POS else "#f4f6f8"
            f.append(rect(x, ry, bw, bh, fill=fillc, stroke=col, sw=2 if col == POS else 1.5))
            f.append(circle(x + 18, ry + 18, 12, fill=BG, stroke=col, sw=1.5))
            f.append(text(x + 18, ry + 23, n, size=14, color=col, bold=True, anchor="middle"))
            for j, ln in enumerate(lab.split("\n")):
                f.append(text(x + bw / 2 + 12, ry + 30 + j * 19, ln, size=11,
                              color=col, bold=(col == POS)))
            centers[n] = (x, x + bw, ry, ry + bh)
    # стрілки в межах рядка
    for a, b in [("1", "2"), ("2", "3"), ("3", "4"), ("5", "6"), ("6", "7"), ("7", "8")]:
        f.append(arrow(centers[a][1], (centers[a][2] + centers[a][3]) / 2,
                       centers[b][0], (centers[b][2] + centers[b][3]) / 2, sw=1.8))
    # перехід 4 → 5: охайний коліно-маршрут смугою між рядками (y=195)
    yb = (centers["4"][3] + centers["5"][2]) / 2          # ≈195, порожня смуга
    x4 = (centers["4"][0] + centers["4"][1]) / 2
    x5 = (centers["5"][0] + centers["5"][1]) / 2
    f.append(line(x4, centers["4"][3], x4, yb, color=INK, sw=1.8))
    f.append(line(x4, yb, x5, yb, color=INK, sw=1.8))
    f.append(arrow(x5, yb, x5, centers["5"][2], sw=1.8))
    f.append(text((x4 + x5) / 2, yb - 6, "далі — другий рядок", size=10, color=MUTED, italic=True))

    b2, _, _ = textbox(W / 2, 340,
                       "кроки 4 і 8 (червоні) — серце механізму: без збереження й відновлення контексту не повернутися",
                       size=11, fill="#fdecea", stroke=POS)
    f.append(b2)
    render(os.path.join(IMG, "full-flow.svg"), W, H, *f)


# ── 3. Вектор: номер переривання → адреса обробника ──────────────────────────
def fig_vector_table():
    W, H = 900, 380
    f = [text(W / 2, 30, "Вектор переривань: номер джерела → адреса його обробника, прямий стрибок",
              size=15, bold=True)]

    rows = [("0", "таймер", "0x4008_8120", False),
            ("1", "GPIO", "0x4008_81F4", True),
            ("2", "UART", "0x4008_8260", False),
            ("…", "…", "…", False),
            ("n", "інше", "0x4008_8xxx", False)]
    tx, rh = 330, 44
    ty = 96
    f.append(text(tx + 160, ty - 14, "вектор (таблиця адрес)", size=11, color=INK, bold=True))
    for i, (num, who, addr, hot) in enumerate(rows):
        y = ty + i * rh
        col = POS if hot else MUTED
        # номер
        f.append(rect(tx, y, 56, rh - 4, fill=("#fdecea" if hot else "#f4f6f8"), stroke=col, sw=1.5))
        f.append(text(tx + 28, y + 27, num, size=13, color=col, bold=True))
        # хто
        f.append(rect(tx + 60, y, 100, rh - 4, fill=BG, stroke=col, sw=1.2))
        f.append(text(tx + 110, y + 26, who, size=11, color=INK))
        # адреса
        f.append(rect(tx + 164, y, 160, rh - 4, fill=("#fdecea" if hot else "#fbfcff"), stroke=col, sw=1.2))
        f.append(text(tx + 244, y + 26, addr, size=11.5, color=(POS if hot else INK), bold=True))

    # «прийшло переривання» ліворуч
    b, bw, bh = textbox(150, 190, "прийшло\nпереривання\n№1 (GPIO)", size=11.5,
                        fill="#fff6e0", stroke="#caa24a", sw=1.8, bold=True)
    f.append(b)
    f.append(arrow(150 + bw / 2, 190, tx - 6, ty + rh + (rh - 4) / 2, color=POS, sw=2.4))

    # стрибок в обробник праворуч
    yhot = ty + rh + (rh - 4) / 2
    f.append(arrow(tx + 324, yhot, 760, yhot, color=POS, sw=2.4))
    hb, _, _ = textbox(810, yhot, "обробник", size=11, fill="#eef6ef", stroke=FIELD, sw=1.6, bold=True)
    f.append(hb)

    b2, _, _ = textbox(W / 2, 350,
                       "замість «перебрати всіх по черзі» — один погляд у вектор і прямий стрибок",
                       size=11, fill=FILL, stroke=LINE)
    f.append(b2)
    render(os.path.join(IMG, "vector-table.svg"), W, H, *f)


# ── 4. Контекст на стек і назад ───────────────────────────────────────────────
def fig_context_save():
    W, H = 880, 380
    f = [text(W / 2, 30, "Контекст складають на стек перед обробником і знімають після — як закладку",
              size=15, bold=True)]

    # три колонки-кроки
    cols = [
        (70, "1. вхід у переривання", "ядро КЛАДЕ на стек:\nлічильник команд (PC)\nрегістр статусу\nробочі регістри", POS),
        (330, "2. обробник працює", "вільно міняє регістри —\nїхні старі значення\nу безпеці на стеку", INK),
        (590, "3. вихід", "ядро ЗНІМАЄ зі стека\nі повертається точно\nтуди, де перервали", FIELD),
    ]
    cw = 220
    for x, title, body, col in cols:
        f.append(rect(x, 70, cw, 150, fill=("#fdecea" if col == POS else ("#eef6ef" if col == FIELD else "#f4f6f8")),
                      stroke=col, sw=1.8, rx=10))
        f.append(text(x + cw / 2, 96, title, size=12, color=col, bold=True))
        for j, ln in enumerate(body.split("\n")):
            f.append(text(x + cw / 2, 124 + j * 22, ln, size=11, color=INK))
    # стрілки між колонками
    f.append(arrow(290, 145, 330, 145, sw=1.8))
    f.append(arrow(550, 145, 590, 145, sw=1.8))

    # зображення стека внизу
    f.append(text(W / 2, 256, "стек: «останнім поклав — першим узяв»", size=12, color=INK, bold=True))
    bx, bw2 = 320, 240
    labels = ["PC", "статус", "R0…Rn"]
    for i, lab in enumerate(labels):
        f.append(rect(bx, 270 + i * 30, bw2, 28, fill="#f4f6f8", stroke=NEG, sw=1.4))
        f.append(text(bx + bw2 / 2, 290 + i * 30, lab, size=11, color=NEG, bold=True))
    f.append(text(bx - 12, 284, "верх", size=10, color=MUTED, anchor="end"))

    render(os.path.join(IMG, "context-save.svg"), W, H, *f)


# ── 5. Матриця переривань ESP32: джерела → слоти двох ядер ────────────────────
def fig_esp32_matrix():
    W, H = 900, 400
    f = [text(W / 2, 30, "Матриця переривань ESP32: 71 джерело маршрутизується на 32 слоти кожного ядра",
              size=15, bold=True)]

    # джерела ліворуч (стовпчик)
    srcs = ["таймери", "GPIO", "UART/SPI", "Wi-Fi/BT", "…(71)"]
    sx, sw, sh = 60, 120, 34
    for i, lab in enumerate(srcs):
        y = 90 + i * 50
        f.append(rect(sx, y, sw, sh, fill="#f4f6f8", stroke=INK, sw=1.4))
        f.append(text(sx + sw / 2, y + 22, lab, size=11, color=INK))
        f.append(line(sx + sw, y + sh / 2, 330, 200, color=MUTED, sw=1.2))

    # матриця в центрі
    b, bw, bh = textbox(420, 200, "МАТРИЦЯ\nпереривань\n(комутатор)", size=12.5,
                        fill="#fff6e0", stroke="#caa24a", sw=2, bold=True, min_w=180)
    f.append(b)

    # два ядра праворуч
    cores = [("ядро PRO\n32 слоти · рівні 1–7", 120), ("ядро APP\n32 слоти · рівні 1–7", 270)]
    for lab, y in cores:
        f.append(line(420 + bw / 2, 200, 640, y + 35, color=POS, sw=2))
        cb, _, _ = textbox(740, y + 35, lab, size=11.5, fill="#fdecea", stroke=POS, sw=1.8, bold=True, min_w=190)
        f.append(cb)

    b2, _, _ = textbox(W / 2, 366,
                       "будь-яке джерело — на будь-який вільний слот потрібного ядра: звідси гнучкість",
                       size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b2)
    render(os.path.join(IMG, "esp32-matrix.svg"), W, H, *f)


# ── 6. Усі GPIO крізь одну лійку ──────────────────────────────────────────────
def fig_gpio_funnel():
    W, H = 880, 400
    f = [text(W / 2, 30, "Усі ніжки GPIO ділять одне переривання: спільний обробник за бітом статусу кличе вашу функцію",
              size=14, bold=True)]

    # ніжки ліворуч
    pins = ["GPIO2", "GPIO4", "GPIO5", "GPIO18"]
    sx, sw, sh = 60, 100, 32
    hot = 1  # GPIO4 спрацював
    for i, lab in enumerate(pins):
        y = 90 + i * 48
        col = POS if i == hot else MUTED
        f.append(rect(sx, y, sw, sh, fill=("#fdecea" if i == hot else "#f4f6f8"), stroke=col, sw=1.6 if i == hot else 1.3))
        f.append(text(sx + sw / 2, y + 21, lab, size=11, color=col, bold=(i == hot)))
        f.append(line(sx + sw, y + sh / 2, 300, 186, color=col, sw=2 if i == hot else 1.1,
                      dash=None if i == hot else "4,4"))

    # лійка: спільне переривання GPIO
    b, bw, bh = textbox(390, 186, "одне переривання GPIO\n(спільне на ядро)", size=12,
                        fill="#fff6e0", stroke="#caa24a", sw=2, bold=True, min_w=200)
    f.append(b)

    # обробник читає GPIO_STATUS і кличе onPress
    f.append(arrow(390 + bw / 2, 186, 600, 186, sw=2))
    steps = ["читає GPIO_STATUS", "біт → ніжка GPIO4", "кличе onPress()"]
    bx2 = 600
    for i, s in enumerate(steps):
        y = 130 + i * 44
        col = FIELD if i == 2 else INK
        f.append(rect(bx2, y, 230, 34, fill=("#eef6ef" if i == 2 else "#f4f6f8"), stroke=col, sw=1.5))
        f.append(text(bx2 + 115, y + 22, s, size=11, color=col, bold=(i == 2)))
        if i < 2:
            f.append(arrow(bx2 + 115, y + 34, bx2 + 115, y + 44, sw=1.4))

    b2, _, _ = textbox(W / 2, 372,
                       "затримка у спільному обробнику б'є по ВСІХ ніжках — тому він мусить бути швидким",
                       size=11, fill="#fdecea", stroke=POS)
    f.append(b2)
    render(os.path.join(IMG, "gpio-funnel.svg"), W, H, *f)


# ── 7. (вставка) NVIC: кожне джерело має вектор і пріоритет, вкладеність авто ──
def fig_nvic():
    W, H = 880, 380
    f = [text(W / 2, 30, "NVIC у Cortex-M: кожне джерело має свій вектор і пріоритет, вкладеність автоматична",
              size=14, bold=True)]

    # джерела з власними векторами
    rows = [("SysTick", "вектор", "пріор. 1"),
            ("UART", "вектор", "пріор. 2"),
            ("GPIO", "вектор", "пріор. 3")]
    tx, rh = 90, 50
    ty = 92
    for i, (who, vec, pr) in enumerate(rows):
        y = ty + i * rh
        f.append(rect(tx, y, 120, rh - 8, fill="#f4f6f8", stroke=INK, sw=1.4))
        f.append(text(tx + 60, y + 26, who, size=11.5, color=INK, bold=True))
        f.append(arrow(tx + 120, y + (rh - 8) / 2, tx + 180, y + (rh - 8) / 2, sw=1.6))
        f.append(rect(tx + 180, y, 120, rh - 8, fill="#fbfcff", stroke=NEG, sw=1.3))
        f.append(text(tx + 240, y + 17, vec, size=10.5, color=NEG, bold=True))
        f.append(text(tx + 240, y + 33, pr, size=10, color=MUTED))

    # вкладеність праворуч
    bx = 470
    f.append(text(bx + 150, ty - 14, "вкладеність — у залізі", size=12, color=POS, bold=True))
    seq = ["іде обробник пріор. 3",
           "прийшов пріор. 1 (вищий)",
           "NVIC витісняє → пріор. 1",
           "повертає назад у пріор. 3"]
    for i, s in enumerate(seq):
        y = ty + i * 46
        col = POS if i in (1, 2) else INK
        f.append(rect(bx, y, 300, 36, fill=("#fdecea" if col == POS else "#f4f6f8"), stroke=col, sw=1.5))
        f.append(text(bx + 150, y + 23, s, size=11, color=col, bold=(col == POS)))
        if i < 3:
            f.append(arrow(bx + 150, y + 36, bx + 150, y + 46, sw=1.4))

    b2, _, _ = textbox(W / 2, 356,
                       "той самий NVIC на кожному Cortex-M (M0…M7) — код переривань переноситься",
                       size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b2)
    render(os.path.join(IMG, "nvic.svg"), W, H, *f)


# ── 8. (вставка) Матриця ESP32: багато джерел на небагато слотів, два ядра ─────
def fig_matrix():
    W, H = 880, 380
    f = [text(W / 2, 30, "Матриця ESP32: 71 джерело на 32 слоти кожного CPU, ядра два — маршрут обираєш сам",
              size=14, bold=True)]

    # стовпчик джерел
    f.append(text(150, 70, "71 джерело периферії", size=12, color=INK, bold=True))
    sx, sw, sh = 80, 140, 28
    for i in range(4):
        y = 90 + i * 40
        lab = ["таймери", "GPIO", "UART/SPI/I2C", "Wi-Fi/BT/…"][i]
        f.append(rect(sx, y, sw, sh, fill="#f4f6f8", stroke=INK, sw=1.3))
        f.append(text(sx + sw / 2, y + 19, lab, size=10.5, color=INK))
        f.append(line(sx + sw, y + sh / 2, 360, 180, color=MUTED, sw=1.1))

    # матриця
    b, bw, bh = textbox(430, 180, "МАТРИЦЯ\n(комутатор)", size=12.5,
                        fill="#fff6e0", stroke="#caa24a", sw=2, bold=True, min_w=160)
    f.append(b)

    # два ядра по ~32 слоти
    for lab, y in [("CPU PRO\n~32 слоти", 110), ("CPU APP\n~32 слоти", 240)]:
        f.append(line(430 + bw / 2, 180, 640, y + 28, color=POS, sw=2))
        cb, _, _ = textbox(730, y + 28, lab, size=11.5, fill="#fdecea", stroke=POS, sw=1.8, bold=True, min_w=150)
        f.append(cb)

    b2, _, _ = textbox(W / 2, 356,
                       "гнучко — будь-яке джерело на будь-який слот, — але ядро, слот і рівень (1–7) обираєш сам",
                       size=11, fill=FILL, stroke=LINE)
    f.append(b2)
    render(os.path.join(IMG, "matrix.svg"), W, H, *f)


if __name__ == "__main__":
    fig_controller()
    fig_full_flow()
    fig_vector_table()
    fig_context_save()
    fig_esp32_matrix()
    fig_gpio_funnel()
    fig_nvic()
    fig_matrix()
    print("OK: 8 figures ->", IMG)
