# -*- coding: utf-8 -*-
"""Фігури до теми «Вимірювання профілю струму» (модуль mk, курс embedded).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── GPIO-маркер: крива струму + доріжка маркера на тій самій осі часу ─────────
def fig_gpio_marker():
    W, H = 760, 480
    f = [text(W / 2, 28,
              "GPIO-маркер підписує криву: фронти маркера = межі фази в коді",
              size=15, bold=True)]

    ox = 86                       # ліва межа графіків (вісь струму)
    span = 600                    # ширина осі часу
    # --- верхня панель: струм I(t) ---
    cur_base = 230                # базова лінія струму (низ)
    cur_top = 70                  # верх осі струму
    f.append(line(ox, cur_base, ox + span, cur_base, color=MUTED, sw=1.4))
    f.append(line(ox, cur_base, ox, cur_top, color=MUTED, sw=1.4))
    f.append(text(ox - 64, cur_top + 4, "струм", size=11, color=MUTED, anchor="start"))
    f.append(text(ox - 64, cur_top + 18, "I(t)", size=11, color=MUTED, anchor="start"))

    # рівні струму в px: лог-подібне стиснення, як у сусідніх темах
    def y_of(ma):
        return cur_base - (math.log10(ma + 1) / math.log10(201)) * (cur_base - cur_top)

    # межі фази передачі по осі часу (px від ox)
    tx_x0, tx_x1 = 250, 410
    sleep_y = y_of(0.01)
    sense_y = y_of(22)
    tx_y = y_of(185)

    # профіль як ламана: сон → невеликий вимір → ПІК передачі → сон
    pts = [(ox, sleep_y), (150, sleep_y),
           (150, sense_y), (tx_x0, sense_y),
           (tx_x0, tx_y), (tx_x1, tx_y),
           (tx_x1, sleep_y), (ox + span, sleep_y)]
    # заливка площі під піком передачі (заряд фази)
    fillpts = [(tx_x0, cur_base), (tx_x0, tx_y), (tx_x1, tx_y), (tx_x1, cur_base)]
    f.append('<polygon points="%s" fill="%s" fill-opacity="0.16" stroke="none"/>'
             % (" ".join("%.1f,%.1f" % p for p in fillpts), POS))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (" ".join("%.1f,%.1f" % p for p in pts), POS))
    # підписи фаз
    f.append(text((ox + 150) / 2 + 6, sleep_y - 8, "сон", size=10.5, color=NEG))
    f.append(text((150 + tx_x0) / 2, sense_y - 8, "вимір", size=10.5, color=INK))
    f.append(text((tx_x0 + tx_x1) / 2, tx_y - 8, "пік TX", size=11, bold=True, color=POS))
    f.append(text((tx_x1 + ox + span) / 2 - 30, sleep_y - 8, "сон", size=10.5, color=NEG))
    # підпис «заряд цієї фази» всередині залитого піку
    f.append(text((tx_x0 + tx_x1) / 2, (tx_y + cur_base) / 2 + 30,
                  "заряд фази", size=10, color=POS, italic=True))

    # --- нижня панель: рівень GPIO-маркера ---
    mk_lo = 360                   # маркер «0»
    mk_hi = 300                   # маркер «1»
    f.append(line(ox, mk_lo + 22, ox + span, mk_lo + 22, color=MUTED, sw=1.2))
    f.append(text(ox + span, mk_lo + 40, "час →", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 64, (mk_lo + mk_hi) / 2 + 4, "GPIO", size=11, color=MUTED, anchor="start"))
    f.append(text(ox - 64, (mk_lo + mk_hi) / 2 + 18, "маркер", size=11, color=MUTED, anchor="start"))
    # доріжка маркера: 0 поки сон/вимір, 1 рівно на час фази TX, 0 далі
    mkpts = [(ox, mk_lo), (tx_x0, mk_lo), (tx_x0, mk_hi),
             (tx_x1, mk_hi), (tx_x1, mk_lo), (ox + span, mk_lo)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (" ".join("%.1f,%.1f" % p for p in mkpts), FIELD))
    f.append(text(tx_x0 - 4, mk_lo - 6, "0", size=10, color=MUTED, anchor="end"))
    f.append(text((tx_x0 + tx_x1) / 2, mk_hi - 6, "маркер фази TX = 1",
                  size=10.5, bold=True, color=FIELD))

    # вертикальні лінії-збіги фронтів між панелями
    for xx in (tx_x0, tx_x1):
        f.append(line(xx, tx_y, xx, mk_hi, color=FIELD, sw=1.0, dash="3,4"))
    f.append(text((tx_x0 + tx_x1) / 2, cur_base + 22,
                  "фронти збігаються", size=10, color=FIELD, italic=True))

    b, _, _ = textbox(W / 2, 452,
                      "Прошивка піднімає GPIO на вході у фазу й опускає на виході — площа під піком належить саме цій ділянці коду",
                      size=11, fill="#eafaf1", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "gpio-marker.svg"), W, H, *f)


# ── Карта вибору приладу: динамічний діапазон × смуга ────────────────────────
def fig_tool_selection():
    W, H = 760, 470
    f = [text(W / 2, 28,
              "Вибір приладу: розмах струмів (вісь X) проти потрібної смуги (вісь Y)",
              size=15, bold=True)]

    ox, oy = 110, 360             # початок осей
    span_x = 560
    top = 70
    f.append(line(ox, oy, ox + span_x, oy, color=MUTED, sw=1.4))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.4))
    # вісь X — порядки динамічного діапазону
    f.append(text(ox + span_x / 2, oy + 42, "динамічний діапазон вузла (порядки струму) →",
                  size=11, color=MUTED, anchor="middle"))
    for i, lab in enumerate(["1–2", "3–4", "5–6", "7+"]):
        xx = ox + span_x * (i + 0.5) / 4
        f.append(line(xx, oy, xx, oy + 5, color=MUTED, sw=1.0))
        f.append(text(xx, oy + 20, lab, size=10.5, color=MUTED))
    # вісь Y — потрібна смуга / частота вибірки
    f.append(text(ox - 90, top + 4, "смуга /", size=11, color=MUTED, anchor="start"))
    f.append(text(ox - 90, top + 18, "вибірка", size=11, color=MUTED, anchor="start"))
    f.append(text(ox - 90, top + 32, "↑", size=13, color=MUTED, anchor="start"))
    for frac, lab in [(0.18, "МSPS"), (0.52, "100 kSPS"), (0.86, "~kSPS")]:
        yy = top + (oy - top) * frac
        f.append(text(ox - 8, yy + 4, lab, size=10, color=MUTED, anchor="end"))

    # маркери класів приладів: (центр x-частка 0..1, центр y px, колір, назва, підпис)
    def tool(fx, fy_frac, col, name, sub):
        cx = ox + span_x * fx
        cy = top + (oy - top) * fy_frac
        f.append(circle(cx, cy, 9, fill="#ffffff", stroke=col, sw=2.4))
        f.append(circle(cx, cy, 3.2, fill=col, stroke=col, sw=1))
        b, w, h = textbox(cx, cy - 30, name, size=11, bold=True,
                          fill="#ffffff", stroke=col, sw=1.4)
        f.append(b)
        f.append(text(cx, cy + 22, sub, size=9.5, color=MUTED))

    # шунт+осцилограф: вузький діапазон (1-2), зате будь-яка смуга осцилографа
    tool(0.12, 0.22, INK,   "шунт + осцил.", "1–2 порядки, дешево")
    # Power-Profiler-клас: широкий діапазон, середня смуга
    tool(0.62, 0.50, FIELD, "Power-Profiler", "нА→А з коробки")
    # Joulescope: найширший діапазон + найвища смуга
    tool(0.90, 0.20, POS,   "Joulescope", "метрологія")
    # Otii/SMU: широкий діапазон, нижча смуга, зате джерело+автотести
    tool(0.66, 0.84, NEG,   "Otii / SMU", "живлення + автотест")

    b, _, _ = textbox(W / 2, 444,
                      ["Бери найдешевше, що покриває твій розмах і смугу:",
                       "вузький — шунт · повний профіль — Power-Profiler · метрологія — Joulescope · автотести — Otii"],
                      size=10, fill=FILL, stroke=MUTED)
    f.append(b)
    render(os.path.join(IMG, "tool-selection.svg"), W, H, *f)


# ── Вставка comp: розпіновка цифрового порту й спільний Vref ─────────────────
def fig_marker_wiring():
    W, H = 760, 430
    f = [text(W / 2, 28,
              "Підключення маркерних ліній: GPIO чипа → цифровий порт приладу",
              size=15, bold=True)]

    # DUT (зліва)
    dx, dy, dw, dh = 60, 110, 200, 210
    f.append(rect(dx, dy, dw, dh, fill=FILL, stroke=INK, sw=1.6))
    f.append(text(dx + dw / 2, dy - 12, "Пристрій під тестом (DUT)", size=11.5, bold=True))
    f.append(text(dx + dw / 2, dy + 24, "МК / ESP32", size=11, color=MUTED))
    # три виводи маркера + Vref-точка живлення
    pins = [("GPIO25", 70, "фаза, біт 0"),
            ("GPIO26", 110, "фаза, біт 1"),
            ("GPIO27", 150, "фаза, біт 2")]
    for name, off, _ in pins:
        py = dy + off
        f.append(text(dx + dw - 8, py + 4, name, size=10, color=INK, anchor="end"))
        f.append(circle(dx + dw, py, 3.4, fill=FIELD, stroke=FIELD, sw=1))
    # лінія живлення (Vref / VDD)
    vy = dy + 190
    f.append(text(dx + dw - 8, vy + 4, "VDD (3.3 В)", size=10, color=POS, anchor="end"))
    f.append(circle(dx + dw, vy, 3.4, fill=POS, stroke=POS, sw=1))

    # Профілювальник (справа)
    px, pyt, pw, ph = 480, 110, 220, 210
    f.append(rect(px, pyt, pw, ph, fill="#eafaf1", stroke=FIELD, sw=1.6))
    f.append(text(px + pw / 2, pyt - 12, "Профілювальник", size=11.5, bold=True))
    f.append(text(px + pw / 2, pyt + 24, "цифровий порт", size=11, color=MUTED))
    ins = [("IN0", 70), ("IN1", 110), ("IN2", 150)]
    for name, off in ins:
        py = pyt + off
        f.append(text(px + 8, py + 4, name, size=10, color=INK, anchor="start"))
        f.append(circle(px, py, 3.4, fill=FIELD, stroke=FIELD, sw=1))
    f.append(text(px + 8, vy + 4, "Vref", size=10, color=POS, anchor="start"))
    f.append(circle(px, vy, 3.4, fill=POS, stroke=POS, sw=1))

    # дроти GPIO→IN
    for (_, off, _), (_, off2) in zip(pins, ins):
        f.append(line(dx + dw, dy + off, px, pyt + off2, color=FIELD, sw=1.8))
    # дріт VDD→Vref (поріг = Vref/2)
    f.append(line(dx + dw, vy, px, vy, color=POS, sw=1.8, dash="5,4"))
    f.append(text((dx + dw + px) / 2, vy - 8,
                  "Vref = живлення DUT → поріг входу = Vref/2", size=9.5,
                  color=POS, italic=True))

    # спільна земля
    gy = 360
    f.append(line(dx + 20, dy + dh, dx + 20, gy, color=MUTED, sw=1.4))
    f.append(line(px + pw - 20, pyt + ph, px + pw - 20, gy, color=MUTED, sw=1.4))
    f.append(line(dx + 20, gy, px + pw - 20, gy, color=MUTED, sw=1.6))
    f.append(text((dx + 20 + px + pw - 20) / 2, gy + 16, "спільна земля (GND)",
                  size=10, color=MUTED))

    b, _, _ = textbox(W / 2, 405,
                      "Три лінії несуть номер фази двійково; Vref беруть від живлення DUT, щоб поріг входу збігся з логікою чипа",
                      size=10.5, fill="#fdf6ec", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "marker-wiring.svg"), W, H, *f)


# ── Вставка comp: три класи на осі прив'язки коду до профілю ──────────────────
def fig_code_binding_matrix():
    W, H = 760, 460
    f = [text(W / 2, 28,
              "Прив'язка коду до профілю: що дає кожен клас приладів",
              size=15, bold=True)]

    # стовпці = класи, рядки = можливості прив'язки
    cols = [("PPK2-клас", FIELD), ("Joulescope JS220", POS), ("Otii Arc Pro", NEG)]
    rows = ["цифрові\nмаркери",
            "відліки\nза секунду",
            "ціна біта\nструму за GPI",
            "синхронний\nUART-лог",
            "автоматизація\n(API)"]
    cells = [
        ["8 входів", "4 GPI + 2 GPO", "немає (лог)"],
        ["100 kSPS", "2 MSPS", "≈4 kSPS"],
        ["—", "0 біт", "—"],
        ["—", "—", "так, з виділенням"],
        ["—", "скрипти", "TCP / JSON"],
    ]
    okmask = [
        [True, True, False],
        [True, True, False],
        [False, True, False],
        [False, False, True],
        [False, True, True],
    ]

    x0 = 150
    cw = (W - x0 - 30) / 3
    y0 = 70
    rh = 64
    # заголовки стовпців
    for j, (name, col) in enumerate(cols):
        cx = x0 + cw * (j + 0.5)
        b, _, _ = textbox(cx, y0 - 6, name, size=11, bold=True,
                          fill="#ffffff", stroke=col, sw=1.6)
        f.append(b)
    # рядки
    for i, rname in enumerate(rows):
        ry = y0 + 24 + rh * i
        f.append(mtext(x0 - 12, ry + rh / 2 - 6, rname, size=10.5,
                       color=MUTED, anchor="end"))
        for j in range(3):
            cx = x0 + cw * j + 6
            cell_w = cw - 12
            fill = "#eafaf1" if okmask[i][j] else "#f4f6f8"
            stroke = cols[j][1] if okmask[i][j] else MUTED
            f.append(fitbox(cx, ry + 6, cell_w, rh - 12, cells[i][j],
                            size=10.5, fill=fill, stroke=stroke,
                            sw=1.4 if okmask[i][j] else 1.0,
                            bold=okmask[i][j]))

    b, _, _ = textbox(W / 2, 436,
                      ["PPK2 — найбільше маркерних ліній дешево · JS220 — маркери без втрати точності + найвища смуга",
                       "Otii — лог і автоматизація для регресійних енерготестів"],
                      size=10, fill=FILL, stroke=MUTED)
    f.append(b)
    render(os.path.join(IMG, "code-binding-matrix.svg"), W, H, *f)


if __name__ == "__main__":
    fig_gpio_marker()
    fig_tool_selection()
    fig_marker_wiring()
    fig_code_binding_matrix()
    print("OK: 4 figures ->", IMG)
