# -*- coding: utf-8 -*-
"""Фігури до теми «Стани конвеєра й переходи між ними»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── 1. Сходинка станів: що додає кожен перехід ──────────────────────────────
def fig_state_ladder():
    W, H = 1020, 590

    rows = [
        ("state", "NULL", ["об'єкт елемента існує в пам'яті,",
                           "зовні не зайнято нічого"]),
        ("trans", "NULL → READY", ["відкрити пристрій, завантажити бібліотеку,",
                                   "зайняти те, що дається лише одному"]),
        ("state", "READY", ["пристрій відкрито й тримається,",
                            "потоків немає, дані не рухаються"]),
        ("trans", "READY → PAUSED", ["активувати пади, запустити потоки,",
                                     "наповнити конвеєр даними наперед"]),
        ("state", "PAUSED", ["перший кадр дійшов до приймача",
                             "й стоїть там; формат уже відомий"]),
        ("trans", "PAUSED → PLAYING", ["роздати годинник і базовий час,",
                                       "приймачі відпускають кадри"]),
        ("state", "PLAYING", ["дані течуть і виводяться",
                              "за спільним годинником"]),
    ]

    x_name, w_name = 40, 250
    x_desc, w_desc = 340, 640
    h_state, h_trans, gap = 62, 66, 12

    parts = []
    y = 52
    for kind, name, desc in rows:
        h = h_state if kind == "state" else h_trans
        if kind == "state":
            parts.append(fitbox(x_name, y, w_name, h, [name], size=19, bold=True,
                                fill="#eafaf1", stroke=FIELD))
            parts.append(fitbox(x_desc, y, w_desc, h, desc, size=14,
                                fill=FILL, stroke=LINE))
        else:
            # стрілка вниз у колонці назв
            parts.append(arrow(x_name + w_name / 2, y + 6,
                               x_name + w_name / 2, y + h - 6, color=NEG))
            parts.append(fitbox(x_desc, y, w_desc, h, desc, size=14,
                                fill="#eaf0fd", stroke=NEG))
            parts.append(text(x_name + w_name / 2 - 14, y + h / 2 + 5, name,
                              size=13, color=NEG, anchor="end"))
        y += h + gap

    render(os.path.join(IMG, 'state-ladder.svg'), W, H, *parts,
           title="Чотири стани — чотири шари готовності, що накопичуються")


# ── 2. Попереднє наповнення й асинхронний перехід ───────────────────────────
def fig_preroll():
    W, H = 1040, 520
    parts = []

    b1, w1, _ = textbox(230, 80, ["застосунок:", "set_state(PAUSED)"], size=15)
    b2, w2, _ = textbox(760, 80, ["одразу повертається ASYNC:", "стану ще не досягнуто"],
                        size=15, fill="#fdecea", stroke=POS)
    parts += [b1, b2]
    parts.append(arrow(230 + w1 / 2 + 14, 80, 760 - w2 / 2 - 14, 80))

    parts.append(line(40, 140, W - 40, 140, color=MUTED, sw=1, dash="6,6"))

    cy = 205
    e1, we1, _ = textbox(160, cy, ["джерело"], size=15, min_w=180)
    e2, we2, _ = textbox(500, cy, ["декодер"], size=15, min_w=180)
    e3, we3, _ = textbox(860, cy, ["приймач"], size=15, min_w=180,
                         fill="#eafaf1", stroke=FIELD)
    parts += [e1, e2, e3]
    parts.append(arrow(160 + we1 / 2 + 12, cy, 500 - we2 / 2 - 12, cy, color=FIELD))
    parts.append(arrow(500 + we2 / 2 + 12, cy, 860 - we3 / 2 - 12, cy, color=FIELD))
    parts.append(text(330, cy - 24, "перший буфер", size=13, color=FIELD))
    parts.append(text(680, cy - 24, "перший буфер", size=13, color=FIELD))

    parts.append(mtext(860, cy + 52, ["приймач приймає його,",
                                      "тримає й далі блокує потік"],
                       size=13, color=MUTED, lh=1.3))

    parts.append(line(40, 320, W - 40, 320, color=MUTED, sw=1, dash="6,6"))

    m1, wm1, _ = textbox(250, 385, ["шина: ASYNC_START", "перехід почався"], size=14)
    m2, wm2, _ = textbox(790, 385, ["шина: ASYNC_DONE", "наповнення завершено"],
                         size=14, fill="#eafaf1", stroke=FIELD)
    parts += [m1, m2]
    parts.append(arrow(250 + wm1 / 2 + 14, 385, 790 - wm2 / 2 - 14, 385))
    parts.append(text(520, 362, "поки триває — стан ще не PAUSED", size=13, color=MUTED))

    parts.append(text(W / 2, 470,
                      "лише після ASYNC_DONE конвеєр справді в PAUSED, і PLAYING настане миттєво",
                      size=14, color=INK))

    render(os.path.join(IMG, 'preroll.svg'), W, H, *parts,
           title="Чому перехід у PAUSED не завершується одразу")


# ── 3. Порядок обходу елементів у контейнері ────────────────────────────────
def fig_traversal_order():
    W, H = 1000, 470
    parts = []
    parts.append(line(500, 56, 500, 440, color=MUTED, sw=1, dash="5,5"))

    parts.append(text(255, 82, "вгору: до PAUSED і PLAYING", size=15, bold=True))
    parts.append(text(745, 82, "вниз: до READY і NULL", size=15, bold=True))

    names = ["джерело", "перетворювач", "приймач"]
    ys = [140, 225, 310]

    for cx, order in ((255, [3, 2, 1]), (745, [1, 2, 3])):
        prev_h = None
        for i, (nm, y) in enumerate(zip(names, ys)):
            box, w, h = textbox(cx, y, [nm], size=15, min_w=210)
            parts.append(box)
            parts.append(circle(cx + 145, y, 17, fill="#eaf0fd", stroke=NEG, sw=2))
            parts.append(text(cx + 145, y + 6, str(order[i]), size=16,
                              color=NEG, bold=True))
            if i > 0:
                parts.append(line(cx, ys[i - 1] + prev_h / 2 + 4,
                                  cx, y - h / 2 - 4, color=MUTED, sw=1.2))
            prev_h = h

    parts.append(mtext(255, 385, ["приймач готовий раніше,",
                                  "ніж джерело почне слати дані"],
                       size=13, color=MUTED, lh=1.35))
    parts.append(mtext(745, 385, ["джерело замовкає раніше,",
                                  "ніж приймач розбирає своє"],
                       size=13, color=MUTED, lh=1.35))

    render(os.path.join(IMG, 'traversal-order.svg'), W, H, *parts,
           title="Контейнер перемикає дітей від приймача до джерела")


# ── 4. Карта потоків драйвера (до вставки proj-state-driver) ────────────────
def fig_driver_threads():
    W, H = 1140, 620
    parts = []

    # заголовки колонок
    hA, _, _ = textbox(170, 80, ["Головний потік"], size=17, bold=True,
                       fill="#eafaf1", stroke=FIELD)
    hB, _, _ = textbox(570, 80, ["Шина повідомлень"], size=17, bold=True)
    hC, _, _ = textbox(970, 80, ["Потоки конвеєра"], size=17, bold=True,
                       fill="#eaf0fd", stroke=NEG)
    parts += [hA, hB, hC]

    colA = [(130, 56, ["gst_element_set_state()", "вгору й униз"]),
            (206, 56, ["чекати повідомлення", "з таймаутом"]),
            (282, 76, ["розбір ERROR, EOS,", "STATE_CHANGED,", "ASYNC_DONE"]),
            (384, 56, ["рішення: грати,", "спинити, вийти"])]
    for y, h, lines in colA:
        parts.append(fitbox(40, y, 260, h, lines, size=14))

    colC = [(130, 56, ["потік джерела:", "читає файл або камеру"]),
            (206, 56, ["потік декодера:", "обробляє буфери"]),
            (282, 76, ["приймач: тримає кадр", "у PAUSED, віддає", "у PLAYING"]),
            (384, 56, ["звідси назовні —", "лише post_message()"])]
    for y, h, lines in colC:
        parts.append(fitbox(840, y, 260, h, lines, size=14))

    queue = [(155, "ERROR"), (207, "ASYNC_DONE"),
             (259, "STATE_CHANGED"), (311, "EOS")]
    for y, nm in queue:
        parts.append(fitbox(440, y, 260, 44, [nm], size=15))
    parts.append(text(570, 402, "черга — єдиний легальний провід між потоками",
                      size=14, color=MUTED))

    parts.append(arrow(830, 250, 712, 250, color=NEG))
    parts.append(text(771, 231, "кладе", size=13, color=NEG))
    parts.append(arrow(428, 250, 310, 250, color=FIELD))
    parts.append(text(369, 231, "забирає", size=13, color=FIELD))

    # заборонений шлях
    parts.append(line(970, 442, 970, 500, color=POS, sw=2, dash="7,5"))
    parts.append(arrow(970, 500, 190, 500, color=POS, sw=2.2))
    parts.append(line(190, 500, 190, 448, color=POS, sw=2, dash="7,5"))
    parts.append(text(575, 548,
                      "✖ set_state() із потоку конвеєра: перехід чекатиме на зупинку "
                      "цього самого потоку",
                      size=15, color=POS, bold=True))

    render(os.path.join(IMG, 'driver-threads.svg'), W, H, *parts,
           title="Хто в якому потоці живе і що кому вільно робити")


# ── 5. Чотири гілки старту (до вставки proj-state-driver) ───────────────────
def fig_startup_branches():
    W, H = 1200, 520
    parts = []

    top, _, th = textbox(600, 82,
                         ["ret = gst_element_set_state (pipeline, GST_STATE_PAUSED)"],
                         size=16, bold=True)
    parts.append(top)

    parts.append(line(600, 82 + th / 2, 600, 125, color=LINE, sw=1.5))
    parts.append(line(165, 125, 1035, 125, color=LINE, sw=1.5))

    cols = [
        (35, "FAILURE", POS, "#fdecea",
         ["перехід зламався,", "стан невизначений"],
         ["вигребти шину —", "там причина;", "set_state(NULL)", "і вихід"]),
        (325, "NO_PREROLL", FIELD, "#eafaf1",
         ["джерело живе —", "наповнення не буде"],
         ["одразу PLAYING,", "не чекати нічого", "(інакше — вічне", "чекання)"]),
        (615, "ASYNC", NEG, "#eaf0fd",
         ["наповнення почалося,", "триває невідомо скільки"],
         ["читати шину до", "ASYNC_DONE від", "самого конвеєра", "або до ERROR"]),
        (905, "SUCCESS", FIELD, "#eafaf1",
         ["уже в PAUSED,", "чекати нема чого"],
         ["одразу PLAYING"]),
    ]
    for x, name, col, bg, meaning, action in cols:
        cx = x + 130
        parts.append(arrow(cx, 125, cx, 144, color=LINE))
        parts.append(fitbox(x, 146, 260, 48, [name], size=17, bold=True,
                            fill=bg, stroke=col, color=col))
        parts.append(fitbox(x, 208, 260, 76, meaning, size=14))
        parts.append(fitbox(x, 298, 260, 112, action, size=14,
                            fill="#ffffff", stroke=MUTED))

    parts.append(text(600, 470,
                      "Чотири відповіді — чотири різні дії; злити їх в одне "
                      "«вдалося чи ні» не можна",
                      size=15, color=INK))

    render(os.path.join(IMG, 'startup-branches.svg'), W, H, *parts,
           title="Старт конвеєра: одна відповідь із чотирьох, і для кожної свій хід")


# ── 6. Маршрут повідомлень про стани (до вставки api-state-api) ─────────────
def fig_message_routing():
    W, H = 1040, 520
    parts = []

    x_left, w_left = 175, 270
    x_band, w_band = 510, 230
    x_right, w_right = 835, 340

    parts.append(rect(x_band - w_band / 2, 105, w_band, 365,
                      fill="#eaf0fd", stroke=NEG, sw=1.5))

    parts.append(text(x_left, 72, "постить елемент", size=15, bold=True))
    parts.append(text(x_band, 72, "GstBin / GstPipeline", size=15, bold=True, color=NEG))
    parts.append(text(x_right, 72, "шина застосунку", size=15, bold=True))

    rows = [
        ("STATE_CHANGED", "pass", ["видно від кожного елемента —",
                                   "фільтруй за GST_MESSAGE_SRC"]),
        ("ERROR", "pass", ["причина провалу;", "приходить від винуватця"]),
        ("ASYNC_START", "stop", ["застосунок не бачить ніколи"]),
        ("ASYNC_DONE", "own", ["лише своє — від конвеєра", "верхнього рівня"]),
        ("RESET_TIME", "stop", ["внутрішнє: переставити відлік"]),
    ]

    y = 150
    for name, kind, note in rows:
        box, wb, _ = textbox(x_left, y, [name], size=15, min_w=w_left)
        parts.append(box)
        x_out = x_left + wb / 2 + 12
        x_in = x_right - w_right / 2 - 12

        if kind == "pass":
            parts.append(arrow(x_out, y, x_in, y, color=FIELD))
            nb, _, _ = textbox(x_right, y, note, size=13, min_w=w_right,
                               fill="#eafaf1", stroke=FIELD)
            parts.append(nb)
        else:
            parts.append(arrow(x_out, y, x_band - 60, y, color=MUTED))
            parts.append(line(x_band - 11, y - 11, x_band + 11, y + 11, color=POS, sw=3))
            parts.append(line(x_band - 11, y + 11, x_band + 11, y - 11, color=POS, sw=3))
            if kind == "own":
                parts.append(arrow(x_band + 60, y, x_in, y, color=FIELD))
                nb, _, _ = textbox(x_right, y, note, size=13, min_w=w_right,
                                   fill="#eafaf1", stroke=FIELD)
                parts.append(nb)
            else:
                parts.append(mtext(x_right, y + 5, note, size=13, color=MUTED))
        y += 70

    render(os.path.join(IMG, 'message-routing.svg'), W, H, *parts,
           title="Що контейнер перехоплює, а що випускає застосункові")


if __name__ == '__main__':
    fig_state_ladder()
    fig_preroll()
    fig_traversal_order()
    fig_driver_threads()
    fig_startup_branches()
    fig_message_routing()
    print("ok")
