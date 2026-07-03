# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Multi-function Shield для Arduino UNO».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Карта плати: що на ній і на який вивід Arduino сидить ──────────────────
def fig_board_map():
    W, H = 860, 560
    f = [text(W / 2, 30, "Що на шилді та який вивід Arduino ним керує",
              size=16, bold=True)]

    # межа плати
    bx, by, bw, bh = 40, 56, W - 80, 400
    f.append(rect(bx, by, bw, bh, fill="#fafbfc", stroke=MUTED, sw=1.8, rx=14))
    f.append(text(bx + 130, by + 24, "Multi-function Shield", size=12.5, bold=True, color=MUTED))

    # блок-помічник: кольорова плитка з назвою і виводом
    def block(cx, cy, w, h, title, pin, fill, accent, sub=None):
        f.append(rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=accent, sw=1.8, rx=9))
        f.append(text(cx, cy - h / 2 + 20, title, size=12, bold=True, color=accent))
        if sub:
            f.append(text(cx, cy - h / 2 + 37, sub, size=9.5, color=MUTED))
        f.append(text(cx, cy + h / 2 - 12, pin, size=11, bold=True, color=INK))

    # верхній ряд: дисплей на всю ширину
    block(W / 2, by + 92, 560, 96,
          "4-розрядний 7-сегментний дисплей", "керується парою 74HC595 → D4 (латч) · D7 (такт) · D8 (дані)",
          "#eef2f8", NEG, "спільний анод, мультиплексований")

    # середній ряд: 4 світлодіоди + зумер + потенціометр
    row2y = by + 208
    block(bx + 150, row2y, 230, 78, "4 світлодіоди", "D13 · D12 · D11 · D10",
          "#fdecea", POS, "активні низьким рівнем")
    block(W / 2, row2y, 200, 78, "П'єзо-зумер", "D3 (широтно-імпульсний)",
          "#eef6ef", FIELD, "через транзистор")
    block(bx + bw - 150, row2y, 230, 78, "Потенціометр 10 кОм", "A0 (аналоговий вхід)",
          "#f3eefb", "#7c4dbe", "крутилка-дільник")

    # нижній ряд: 3 кнопки + роз'єми
    row3y = by + 316
    block(bx + 150, row3y, 230, 78, "3 кнопки  S1·S2·S3", "A1 · A2 · A3",
          "#fff6e6", "#c77f0a", "цифрові входи, підтяжка вгору")
    block(W / 2, row3y, 200, 78, "Роз'єм UART", "виводи D0/D1 (RX/TX)",
          "#e8f4f4", "#0a8f8f", "під Bluetooth / модуль")
    block(bx + bw - 150, row3y, 230, 78, "Гнізда давачів", "DS18B20 · LM35 · ІЧ-приймач",
          "#f0f0f0", MUTED, "окремі майданчики")

    # підсумок
    b, _, _ = textbox(W / 2, 512,
                      "усе вже розведено дорінками плати — надів шилд на гребінки UNO, і ці виводи задіяні самі",
                      size=11.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "board-map.svg"), W, H, *f)


# ── 2. Як світиться дисплей: два регістри в каскаді + мультиплексування ───────
def fig_display_wiring():
    W, H = 900, 540
    f = [text(W / 2, 30, "Дисплей: два 74HC595 у каскаді — сегменти й вибір розряду",
              size=16, bold=True)]

    # Arduino ліворуч
    ax, ay, aw, ah = 40, 96, 118, 240
    f.append(rect(ax, ay, aw, ah, fill="#eef2f8", stroke=INK, sw=1.8, rx=10))
    f.append(text(ax + aw / 2, ay + 26, "Arduino", size=13, bold=True))
    f.append(text(ax + aw / 2, ay + 44, "UNO", size=11, color=MUTED))
    pins = [("D8  дані", ay + 96), ("D7  такт", ay + 148), ("D4  латч", ay + 200)]
    for lbl, py in pins:
        f.append(text(ax + aw / 2, py, lbl, size=11, bold=True, color=INK))

    # перший регістр — сегменти
    r1x, r1y, rw, rh = 300, 96, 150, 150
    f.append(rect(r1x, r1y, rw, rh, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=10))
    f.append(text(r1x + rw / 2, r1y + 24, "74HC595 №1", size=12.5, bold=True, color=NEG))
    f.append(text(r1x + rw / 2, r1y + 44, "байт сегментів", size=10.5, color=INK))
    f.append(text(r1x + rw / 2, r1y + 64, "a b c d e f g dp", size=10, color=MUTED))
    f.append(text(r1x + rw / 2, r1y + 108, "→ дільники струму", size=9.5, color=MUTED))
    f.append(text(r1x + rw / 2, r1y + 126, "→ сегменти цифри", size=9.5, color=MUTED))

    # другий регістр — вибір розряду
    r2x, r2y = 300, r1y + rh + 46
    f.append(rect(r2x, r2y, rw, rh, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=10))
    f.append(text(r2x + rw / 2, r2y + 24, "74HC595 №2", size=12.5, bold=True, color=NEG))
    f.append(text(r2x + rw / 2, r2y + 44, "вибір розряду", size=10.5, color=INK))
    f.append(text(r2x + rw / 2, r2y + 64, "0xF1 0xF2 0xF4 0xF8", size=10, color=MUTED))
    f.append(text(r2x + rw / 2, r2y + 108, "→ один спільний", size=9.5, color=MUTED))
    f.append(text(r2x + rw / 2, r2y + 126, "анод під напругу", size=9.5, color=MUTED))

    # лінії Arduino → регістр №1 (три спільні)
    def bus3(x1, x2, ys, labels_at=None):
        for i, dy in enumerate((-8, 0, 8)):
            f.append(line(x1, ys + dy, x2, ys + dy, color=INK, sw=1.6))

    bx1 = ax + aw
    # дані на №1
    f.append(line(bx1, ay + 96, r1x, r1y + 60, color=POS, sw=2.0))
    f.append(text((bx1 + r1x) / 2, ay + 84, "дані", size=9.5, color=POS, bold=True))
    # такт і латч — спільні на обидва (ведемо збоку)
    f.append(line(bx1, ay + 148, r1x - 20, ay + 148, color=INK, sw=1.8))
    f.append(line(bx1, ay + 200, r1x - 30, ay + 200, color=INK, sw=1.8))
    f.append(text((bx1 + r1x) / 2 - 8, ay + 138, "такт+латч —", size=9, color=INK))
    f.append(text((bx1 + r1x) / 2 - 8, ay + 214, "спільні на обидва", size=9, color=INK))
    # вертикаль такт+латч униз до №2
    f.append(line(r1x - 20, ay + 148, r1x - 20, r2y + 40, color=INK, sw=1.6))
    f.append(line(r1x - 30, ay + 200, r1x - 30, r2y + 70, color=INK, sw=1.6))
    f.append(line(r1x - 20, ay + 148, r1x, r1y + 84, color=INK, sw=1.6))
    f.append(line(r1x - 30, ay + 200, r1x, r1y + 104, color=INK, sw=1.6))
    f.append(line(r1x - 20, r2y + 40, r2x, r2y + 40, color=INK, sw=1.6))
    f.append(line(r1x - 30, r2y + 70, r2x, r2y + 70, color=INK, sw=1.6))

    # каскад: дані №1 → №2
    f.append(line(r1x + rw / 2, r1y + rh, r1x + rw / 2, r2y, color=POS, sw=2.0))
    f.append(text(r1x + rw / 2 + 66, (r1y + rh + r2y) / 2, "перенос", size=9.5, color=POS, bold=True))
    f.append(text(r1x + rw / 2 + 66, (r1y + rh + r2y) / 2 + 15, "даних", size=9.5, color=POS, bold=True))

    # дисплей праворуч: 4 розряди у власних клітинах-віконцях
    dx, dy, dw, dh = 600, 150, 260, 150
    f.append(rect(dx, dy, dw, dh, fill="#111318", stroke=INK, sw=1.8, rx=10))
    for i in range(4):
        cell = dx + 14 + i * 60
        col = FIELD if i == 1 else "#3a4048"
        f.append(rect(cell, dy + 24, 46, dh - 60, fill="#181b21", stroke="#242830", sw=1.2, rx=4))
        f.append(text(cell + 23, dy + dh / 2 + 20, "8", size=46, color=col, bold=True))
    f.append(text(dx + dw / 2, dy - 12, "4-розрядний дисплей (спільний анод)", size=11, bold=True))
    f.append(text(dx + dw / 2, dy + dh + 22, "світиться один розряд — решта згашені", size=10, color=MUTED))

    # сегменти №1 → дисплей
    f.append(line(r1x + rw, r1y + rh / 2, dx, dy + 40, color=NEG, sw=2.0))
    f.append(text((r1x + rw + dx) / 2, r1y + rh / 2 - 8, "8 ліній сегментів", size=9.5, color=NEG, bold=True))
    # розряди №2 → дисплей
    f.append(line(r2x + rw, r2y + rh / 2, dx, dy + dh - 30, color="#c77f0a", sw=2.0))
    f.append(text((r2x + rw + dx) / 2, r2y + rh / 2 + 16, "4 лінії аноду", size=9.5, color="#c77f0a", bold=True))

    b, _, _ = textbox(W / 2, 512,
                      "око не встигає за швидким перебором розрядів — і бачить усі чотири цифри разом; це і є мультиплексування",
                      size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "display-wiring.svg"), W, H, *f)


# ── 3. getButton(): одне натискання → потік подій, і як упакований байт ───────
def fig_button_events():
    W, H = 900, 560
    f = [text(W / 2, 30, "getButton(): одне натискання породжує потік подій",
              size=16, bold=True)]

    # верх: дві гілки подій від однієї кнопки
    lane_y1 = 92
    lane_y2 = 214
    x0 = 70
    xstep = 196

    def evbox(cx, cy, title, sub, accent, fill):
        w, h = 168, 62
        f.append(rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=accent, sw=1.8, rx=9))
        f.append(text(cx, cy - 9, title, size=11.5, bold=True, color=accent))
        f.append(text(cx, cy + 12, sub, size=9.5, color=MUTED))

    # гілка А — короткий тик
    f.append(text(x0 - 8, lane_y1 - 44, "коротко натиснув і відпустив", size=11, bold=True,
                  color=FIELD, anchor="start"))
    evbox(x0 + 84, lane_y1, "натиснута", "PRESSED_IND", INK, "#eef2f8")
    f.append(arrow(x0 + 168, lane_y1, x0 + xstep + 0, lane_y1, color=INK, sw=1.8))
    evbox(x0 + xstep + 84, lane_y1, "коротко відпущена", "SHORT_RELEASE_IND", FIELD, "#eef6ef")
    f.append(text(x0 + xstep + 84, lane_y1 + 52, "← ось тут реагуємо на «клац»", size=9.5,
                  color=FIELD))

    # гілка Б — довге утримання
    f.append(text(x0 - 8, lane_y2 - 44, "натиснув і тримаєш", size=11, bold=True,
                  color=POS, anchor="start"))
    evbox(x0 + 84, lane_y2, "натиснута", "PRESSED_IND", INK, "#eef2f8")
    f.append(arrow(x0 + 168, lane_y2, x0 + xstep, lane_y2, color=INK, sw=1.8))
    evbox(x0 + xstep + 84, lane_y2, "довго тримається", "LONG_PRESSED_IND", "#c77f0a", "#fff6e6")
    f.append(text(x0 + xstep + 84, lane_y2 + 52, "летить повторно, поки тримаєш", size=9.5,
                  color="#c77f0a"))
    f.append(arrow(x0 + xstep + 168, lane_y2, x0 + 2 * xstep, lane_y2, color=INK, sw=1.8))
    evbox(x0 + 2 * xstep + 84, lane_y2, "довго відпущена", "LONG_RELEASE_IND", POS, "#fdecea")

    # низ: як упакований байт від getButton()
    by = 336
    f.append(text(W / 2, by, "байт, що повертає getButton() — номер кнопки + дія в одному числі",
                  size=12.5, bold=True))

    # 8 клітинок біта
    cw = 58
    total = 8 * cw
    bx0 = W / 2 - total / 2
    bits = [("b7", "b6", "#c77f0a", "дія"),
            ("b5", "b4", None, None), ("b3", None, None, None),
            ("b2", None, None, None), ("b1", None, None, None), ("b0", None, "#2457d6", "№")]
    # намалюємо 8 клітинок; перші дві (старші) — дія, молодші шість — номер
    for i in range(8):
        cx = bx0 + i * cw
        is_action = i < 2      # b7,b6
        col = "#fff6e6" if is_action else "#eaf0fd"
        acc = "#c77f0a" if is_action else "#2457d6"
        f.append(rect(cx, by + 20, cw - 6, 46, fill=col, stroke=acc, sw=1.6, rx=6))
        f.append(text(cx + (cw - 6) / 2, by + 40, "b%d" % (7 - i), size=11, bold=True, color=INK))
    # дужки-підписи
    f.append(line(bx0, by + 74, bx0 + 2 * cw - 6, by + 74, color="#c77f0a", sw=2))
    f.append(text(bx0 + (2 * cw - 6) / 2, by + 90, "дія (0..3)", size=10.5, bold=True, color="#c77f0a"))
    f.append(text(bx0 + (2 * cw - 6) / 2, by + 106, "PRESSED / SHORT_REL /", size=9, color=MUTED))
    f.append(text(bx0 + (2 * cw - 6) / 2, by + 120, "LONG_PRESS / LONG_REL", size=9, color=MUTED))
    f.append(line(bx0 + 2 * cw, by + 74, bx0 + 8 * cw - 6, by + 74, color="#2457d6", sw=2))
    f.append(text(bx0 + 2 * cw + (6 * cw - 6) / 2, by + 90, "номер кнопки (1, 2, 3)", size=10.5,
                  bold=True, color="#2457d6"))
    f.append(text(bx0 + 2 * cw + (6 * cw - 6) / 2, by + 108,
                  "btn & 0b00111111 → номер;  btn & 0b11000000 → дія", size=9.5, color=MUTED))

    b, _, _ = textbox(W / 2, 522,
                      "тому btn == BUTTON_1_SHORT_RELEASE ловить саме «S1 коротко клацнули» — і номер, і дію разом",
                      size=11.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "button-events.svg"), W, H, *f)


# ── 4. Чому бібліотека зручна: фонове переривання веде дисплей само ───────────
def fig_isr_timeline():
    W, H = 900, 470
    f = [text(W / 2, 30, "Фонове переривання веде дисплей само — loop() вільний",
              size=16, bold=True)]

    # смуга часу
    tx, ty, tw = 60, 158, W - 120
    f.append(text(tx, ty - 96, "згори — рідкі довгі шматки твого коду", size=10.5, color=FIELD, anchor="start"))
    f.append(text(tx + tw, ty - 96, "час →", size=11, color=MUTED, anchor="end"))

    # твій loop() — довгі спокійні блоки згори
    loops = [(0, 150), (200, 150), (400, 150), (600, 150)]
    for i, (off, wblk) in enumerate(loops):
        x = tx + 10 + off
        f.append(rect(x, ty - 80, wblk, 34, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=7))
        f.append(text(x + wblk / 2, ty - 58, "твій loop(): рахуй, читай кнопку", size=10,
                      color=FIELD, bold=True))

    # вісь часу
    f.append(line(tx, ty, tx + tw, ty, color=MUTED, sw=1.4))

    # тики переривання — часті вузькі спалахи знизу від осі (нижче — вільно від тексту)
    n_ticks = 18
    for k in range(n_ticks):
        x = tx + 14 + k * (tw - 28) / (n_ticks - 1)
        f.append(line(x, ty, x, ty + 34, color=NEG, sw=2.2))
    f.append(rect(tx + 10, ty + 46, tw - 20, 42, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=7))
    f.append(text(tx + tw / 2, ty + 64, "переривання по таймеру (щось коло 1 кГц): засвіти наступний розряд,",
                  size=10.5, color=NEG, bold=True))
    f.append(text(tx + tw / 2, ty + 80, "опроси кнопки з дебордом, відрахуй тривалість писку — і поверни керування",
                  size=10, color=MUTED))

    f.append(text(tx, ty + 108, "знизу — часті крихітні тики бібліотеки між ними", size=10.5,
                  color=NEG, anchor="start"))

    # висновок
    b, _, _ = textbox(W / 2, 430,
                      ["дисплей світиться рівно, кнопки відбиті, писк відрахований — і все це «саме»,",
                       "поки твій loop() займається лічильником; за це береться один із таймерів МК"],
                      size=11.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "isr-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_board_map()
    fig_display_wiring()
    fig_button_events()
    fig_isr_timeline()
    print("OK: 4 figures ->", IMG)
