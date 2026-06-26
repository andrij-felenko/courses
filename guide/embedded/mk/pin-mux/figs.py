# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

PIN  = "#8a6a1e"   # бурштин — ніжка / контакт
WARM = "#fbf3e0"   # фон ніжки
GP   = FIELD       # зелений — GPIO / прямий швидкий шлях
PERI = NEG         # синій — периферійний блок / повільне
HOT  = POS         # червоний — затримка / небезпека / швидке критичне


# ── why-mux: без мультиплексора сотня ніжок vs з ним удвічі менший корпус ──────
# Ідея: простір функцій більший за простір ніжок → ніжки доводиться ділити.
def fig_why_mux():
    W, H = 820, 360
    p = []
    p.append(line(W/2, 64, W/2, 312, color="#dcdcdc", sw=1.4, dash="5 5"))

    # ── ліворуч: без мультиплексора ──
    p.append(text(210, 60, "Без мультиплексора", size=14, color=PERI, bold=True))
    p.append(text(210, 80, "кожному сигналу — своя ніжка", size=10.5, color=MUTED, italic=True))
    # пучок блоків, від кожного — окрема лінія до своєї ніжки
    blocks = ["UART×3", "SPI×2", "I2C×2", "ШІМ", "АЦП"]
    for i, b in enumerate(blocks):
        y = 118 + i * 34
        p.append(fitbox(56, y - 14, 120, 28, b, size=10.5, color=PERI,
                        stroke=PERI, fill="#eef2fb", bold=True))
        # три «віяла» ліній від блоку до стовпа ніжок
        for k in range(3):
            p.append(line(176, y, 300, 96 + (i*3 + k) * 13, color=PERI, sw=1.1))
    # стовп із багатьох ніжок
    p.append(rect(300, 88, 26, 210, fill=WARM, stroke=PIN, sw=1.6))
    for k in range(15):
        p.append(line(326, 96 + k*13, 338, 96 + k*13, color=PIN, sw=2))
    p.append(text(313, 318, ">100 ніжок", size=11.5, color=HOT, bold=True))
    p.append(text(210, 340, "великий дорогий корпус", size=11, color=PERI, bold=True))

    # ── праворуч: з мультиплексором ──
    p.append(text(610, 60, "З мультиплексором", size=14, color=GP, bold=True))
    p.append(text(610, 80, "кілька призначень — на одну ніжку", size=10.5, color=MUTED, italic=True))
    for i, b in enumerate(blocks):
        y = 118 + i * 34
        p.append(fitbox(456, y - 14, 120, 28, b, size=10.5, color=PERI,
                        stroke=PERI, fill="#eef2fb", bold=True))
        p.append(line(576, y, 690, 150 + (i % 4) * 30, color=PERI, sw=1.2))
    # мультиплексор-вузол
    p.append(fitbox(660, 132, 60, 120, "MUX", size=13, color=INK,
                    stroke=INK, fill="#f3f6ff", bold=True))
    # малий стовп ніжок
    p.append(rect(742, 150, 26, 92, fill=WARM, stroke=PIN, sw=1.6))
    for k in range(6):
        p.append(line(742, 158 + k*14, 730, 158 + k*14, color=PIN, sw=2))
        p.append(line(768, 158 + k*14, 780, 158 + k*14, color=PIN, sw=2))
    p.append(text(755, 262, "удвічі менше", size=11.5, color=GP, bold=True))
    p.append(text(610, 340, "малий дешевий корпус", size=11, color=GP, bold=True))

    render(os.path.join(OUT, "why-mux.svg"), W, H, *p,
           title="Простір функцій більший за простір ніжок — тож ніжки ділять")


# ── pin-switch: перемикач-стрілка біля ніжки вибирає одне джерело з кількох ────
# Ідея: меню на ніжці — невелике число в регістрі ставить «стрілку».
def fig_pin_switch():
    W, H = 760, 330
    p = []
    sources = [("GPIO", GP, "#eaf6ee"), ("UART", PERI, "#eef2fb"),
               ("SPI", PERI, "#eef2fb"), ("таймер", PERI, "#eef2fb")]
    hub_x, hub_y = 470, 165
    for i, (name, col, fill) in enumerate(sources):
        y = 80 + i * 56
        b, w, h = textbox(150, y, name, size=12, color=col, stroke=col,
                          fill=fill, bold=True, min_w=120)
        p.append(b)
        # лінія до вузла-стрілки; вибрана (UART, i==1) — жирна суцільна, решта — бліда
        chosen = (i == 1)
        p.append(line(210, y, hub_x - 10, hub_y,
                      color=(INK if chosen else "#c9ced6"),
                      sw=(3 if chosen else 1.3),
                      dash=(None if chosen else "4 4")))
    # вузол-стрілка
    p.append(circle(hub_x, hub_y, 16, fill="#f3f6ff", stroke=INK, sw=2))
    p.append(text(hub_x, hub_y + 5, "⇄", size=18, color=INK, bold=True))
    # від вузла до ніжки
    p.append(line(hub_x + 16, hub_y, 600, hub_y, color=INK, sw=3))
    p.append(rect(600, hub_y - 16, 30, 32, fill=WARM, stroke=PIN, sw=1.8))
    p.append(line(630, hub_y, 660, hub_y, color=PIN, sw=3))
    p.append(text(615, hub_y - 26, "ніжка", size=11, color=PIN, bold=True))
    # керівний регістр
    p.append(fitbox(380, 268, 200, 36, "регістр ніжки: 1 → UART", size=11.5,
                    color=INK, stroke=MUTED, fill="#fafafa", bold=True))
    p.append(arrow(hub_x, 252, hub_x, hub_y + 22, color=MUTED, sw=1.8))
    p.append(text(W/2, 318, "Невелике число в регістрі ставить «стрілку»: "
                  "під'єднане рівно одне джерело.", size=11, color=INK, bold=True))
    render(os.path.join(OUT, "pin-switch.svg"), W, H, *p,
           title="Меню на ніжці: перемикач вибирає одне джерело з кількох")


# ── gpio-matrix: ґратка сигнали×ніжки, на перетині — перемикач ─────────────────
# Ідея: повний комутатор — будь-який сигнал на будь-яку ніжку.
def fig_gpio_matrix():
    W, H = 760, 400
    p = []
    sigs = ["UART1_TX", "SPI_MOSI", "I2C_SDA", "ШІМ_CH"]
    pins = ["GPIO 2", "GPIO 4", "GPIO 17", "GPIO 23", "GPIO 25"]
    x0, y0 = 200, 110          # лівий-верхній кут ґратки
    cw, ch = 96, 56            # крок стовпців/рядків
    # підписи стовпців (ніжки)
    for j, pn in enumerate(pins):
        cx = x0 + j * cw
        p.append(rect(cx - 38, 60, 76, 30, fill=WARM, stroke=PIN, sw=1.4))
        p.append(text(cx, 80, pn, size=10, color=PIN, bold=True))
        p.append(line(cx, 90, cx, y0 - 8, color="#c9ced6", sw=1))
    # підписи рядків (сигнали) + горизонталі
    for i, sg in enumerate(sigs):
        cy = y0 + i * ch
        p.append(fitbox(40, cy - 14, 120, 28, sg, size=10, color=PERI,
                        stroke=PERI, fill="#eef2fb", bold=True))
        p.append(line(164, cy, x0 + (len(pins)-1)*cw + 8, cy, color="#c9ced6", sw=1))
        # вертикалі домалюємо нижче
    for j in range(len(pins)):
        cx = x0 + j * cw
        p.append(line(cx, y0 - 8, cx, y0 + (len(sigs)-1)*ch + 8, color="#c9ced6", sw=1))
    # перемикачі на перетинах: маленькі кружечки; кілька «замкнених» — кольорові
    closed = {(0, 2), (1, 0), (2, 4), (3, 1)}   # (рядок-сигнал, стовп-ніжка)
    for i in range(len(sigs)):
        for j in range(len(pins)):
            cx, cy = x0 + j * cw, y0 + i * ch
            if (i, j) in closed:
                p.append(circle(cx, cy, 9, fill="#eaf6ee", stroke=GP, sw=2.4))
                p.append(text(cx, cy + 4, "•", size=16, color=GP, bold=True))
            else:
                p.append(circle(cx, cy, 5, fill=BG, stroke="#c9ced6", sw=1.2))
    p.append(text(W/2, 372, "Будь-який сигнал → будь-яка ніжка: замкнений перетин "
                  "задає число в регістрі. Повна свобода розведення.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "gpio-matrix.svg"), W, H, *p,
           title="GPIO matrix: повний комутатор сигнали × ніжки")


# ── two-paths: довгий шлях через матрицю (+такт) vs короткий через IO_MUX ──────
# Ідея: гнучкість матриці коштує такту затримки; IO_MUX — прямо, без нього.
def fig_two_paths():
    W, H = 820, 380
    p = []
    # спільне джерело
    b, w, h = textbox(120, 190, "периферія\n(SPI)", size=12, color=PERI, stroke=PERI,
                      fill="#eef2fb", bold=True, min_w=140)
    p.append(b)

    # ── верхній шлях: GPIO matrix із засувкою ──
    b, w, h = textbox(360, 96, "GPIO matrix\nкомутатор", size=12, color=INK, stroke=INK,
                      fill="#f3f6ff", bold=True, min_w=170)
    p.append(b)
    b, w, h = textbox(560, 96, "засувка\n80 МГц", size=11.5, color=HOT, stroke=HOT,
                      fill="#fff4f3", bold=True, min_w=120)
    p.append(b)
    b, w, h = textbox(740, 96, "будь-яка\nніжка", size=11.5, color=PIN, stroke=PIN,
                      fill=WARM, bold=True, min_w=110)
    p.append(b)
    p.append(arrow(180, 176, 300, 110, color=INK, sw=2))
    p.append(arrow(445, 96, 500, 96, color=INK, sw=2))
    p.append(arrow(620, 96, 686, 96, color=INK, sw=2))
    p.append(text(470, 150, "+1 такт затримки → стеля ~40 МГц", size=11, color=HOT, bold=True))

    # ── нижній шлях: IO_MUX прямо ──
    b, w, h = textbox(440, 286, "IO_MUX — прямий перемикач", size=12, color=GP, stroke=GP,
                      fill="#eaf6ee", bold=True, min_w=300)
    p.append(b)
    b, w, h = textbox(740, 286, "привілейована\nніжка", size=11, color=PIN, stroke=PIN,
                      fill=WARM, bold=True, min_w=130)
    p.append(b)
    p.append(arrow(180, 206, 300, 280, color=GP, sw=2.4))
    p.append(arrow(595, 286, 672, 286, color=GP, sw=2.4))
    p.append(text(470, 330, "без зайвого такту → повна швидкість SPI (>40…80 МГц)",
                  size=11, color=GP, bold=True))

    render(os.path.join(OUT, "two-paths.svg"), W, H, *p,
           title="Два шляхи до ніжки: матриця (гнучко, +такт) vs IO_MUX (швидко, прямо)")


# ── afr-split: AFRL ловить ніжки 0–7, AFRH — 8–15; типова пастка з PA9 ─────────
# Ідея (для proj-вставки): чотирибітне поле ніжки лежить у РІЗНИХ регістрах
# залежно від номера ніжки; переплутав регістр — налаштував не ту ніжку.
def fig_afr_split():
    W, H = 820, 360
    p = []
    p.append(text(W/2, 34, "Чотири біти на ніжку, але у двох регістрах",
                  size=14, color=INK, bold=True))

    # два регістри як стрічки по 8 полів
    def reg(x, y, name, lo, hi, hot_idx=None):
        cellw = 40
        p.append(text(x - 14, y + 22, name, size=12, color=PERI, bold=True, anchor="end"))
        for k in range(8):
            idx = lo + k
            cx = x + k * cellw
            isfield = (idx == hot_idx)
            p.append(rect(cx, y, cellw, 32,
                          fill=("#fff4f3" if isfield else "#eef2fb"),
                          stroke=(HOT if isfield else PERI),
                          sw=(2.4 if isfield else 1.3)))
            p.append(text(cx + cellw/2, y + 21, str(idx), size=11,
                          color=(HOT if isfield else PERI),
                          bold=isfield))
        p.append(text(x + 4*cellw, y + 50, "ніжки %d…%d" % (lo, hi),
                      size=10.5, color=MUTED, anchor="middle", italic=True))

    reg(120, 90,  "AFR[0] (AFRL)", 0, 7)
    reg(120, 200, "AFR[1] (AFRH)", 8, 15, hot_idx=9)

    # стрілка-помилка: «шукаю PA9 — лізу не в той регістр»
    p.append(text(120 + 8.0*40 + 70, 106,
                  "PA9 → AFR[1], а НЕ AFR[0]!", size=11.5, color=HOT, bold=True,
                  anchor="start"))
    p.append(arrow(120 + 8.0*40 + 64, 112, 120 + (9-8)*40 + 20, 200,
                   color=HOT, sw=2))
    p.append(text(W/2, 320,
                  "Ніжка 9 лежить у AFR[1], зсув (9−8)·4. Переплутав AFRL/AFRH "
                  "для ніжок 8–15 — налаштував чужу ніжку.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "afr-split.svg"), W, H, *p,
           title="STM32 AFR: поле ніжки 0–7 у AFRL, 8–15 у AFRH")


# ── esp-route: вихід і вхід через матрицю — це ДВА різні реєстри ───────────────
# Ідея (для proj-вставки): connect_out_signal і connect_in_signal — окремі дроти;
# IO_MUX обходить матрицю для швидкого SPI.
def fig_esp_route():
    W, H = 820, 400
    p = []
    p.append(text(W/2, 30, "ESP32: вихід і вхід — два окремі шляхи матриці",
                  size=14, color=INK, bold=True))

    # центр — ніжка
    px, py = 600, 200
    p.append(rect(px, py - 26, 34, 52, fill=WARM, stroke=PIN, sw=1.8))
    p.append(text(px + 17, py - 36, "GPIO 17", size=10.5, color=PIN, bold=True))
    p.append(line(px + 34, py, px + 70, py, color=PIN, sw=3))

    # вихід: периферія → матриця → ніжка
    b, w, h = textbox(120, 110, "U1TXD_OUT_IDX\n(вихід блоку)", size=11, color=PERI,
                      stroke=PERI, fill="#eef2fb", bold=True, min_w=180)
    p.append(b)
    b, w, h = textbox(355, 110, "connect_out_signal\n(реєстр виходу ніжки)", size=11,
                      color=INK, stroke=INK, fill="#f3f6ff", bold=True, min_w=240)
    p.append(b)
    p.append(arrow(214, 110, 232, 110, color=PERI, sw=2))
    p.append(arrow(482, 124, px + 6, py - 18, color=PERI, sw=2))

    # вхід: ніжка → матриця → периферія
    b, w, h = textbox(355, 290, "connect_in_signal\n(вибір ніжки-джерела)", size=11,
                      color=INK, stroke=INK, fill="#f3f6ff", bold=True, min_w=240)
    p.append(b)
    b, w, h = textbox(120, 290, "U1RXD_IN_IDX\n(вхід блоку)", size=11, color=PERI,
                      stroke=PERI, fill="#eef2fb", bold=True, min_w=180)
    p.append(b)
    p.append(arrow(px + 4, py + 18, 474, 290, color=GP, sw=2))
    p.append(arrow(232, 290, 214, 290, color=GP, sw=2))

    p.append(text(300, 88, "вихід →", size=10.5, color=PERI, bold=True))
    p.append(text(300, 332, "← вхід", size=10.5, color=GP, bold=True))

    # IO_MUX-натяк
    p.append(text(px + 17, py + 60, "IO_MUX (швидкий SPI)\nобходить матрицю",
                  size=10, color=HOT, bold=True, anchor="middle"))
    p.append(text(W/2, 378,
                  "Один сигнал = один дріт: вихід і вхід вмикають окремо. "
                  "Дзеркальна пара inversion-прапорців живе в обох викликах.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "esp-route.svg"), W, H, *p,
           title="ESP32 GPIO matrix: connect_out_signal і connect_in_signal — окремі шляхи")


if __name__ == "__main__":
    fig_why_mux()
    fig_pin_switch()
    fig_gpio_matrix()
    fig_two_paths()
    fig_afr_split()
    fig_esp_route()
    print("OK: figs written to", OUT)
