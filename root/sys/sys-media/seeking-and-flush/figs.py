# -*- coding: utf-8 -*-
"""Фігури до теми «Перемотування і скидання конвеєра: seek-події та флаш»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── 1. Що саме лежить у конвеєрі в мить перемотування ───────────────────────
def fig_in_flight():
    W, H = 1220, 560

    cols = [
        ("джерело", ["читає файл", "з байтового", "зміщення"],
         "стоїть у push:\nчерга попереду повна", POS),
        ("черга", ["2 секунди", "стиснених даних", "уже прочитано"],
         "заповнена по вінця", POS),
        ("декодер", ["опорні кадри", "для наступних", "у своїй пам'яті"],
         "працює", MUTED),
        ("перетворювач", ["кадр у роботі", "напівперекладений", "у RGB"],
         "працює", MUTED),
        ("приймач", ["кадр на 00:03.2", "утримується", "до своєї миті"],
         "спить на годиннику", POS),
    ]

    x0, wcol, gap = 40, 216, 20
    y_el, h_el = 78, 52
    y_hold, h_hold = 156, 84
    y_thr, h_thr = 268, 62

    parts = []
    for i, (name, hold, thr, col) in enumerate(cols):
        x = x0 + i * (wcol + gap)
        parts.append(fitbox(x, y_el, wcol, h_el, [name], size=17, bold=True,
                            fill="#eafaf1", stroke=FIELD))
        parts.append(fitbox(x, y_hold, wcol, h_hold, hold, size=13))
        parts.append(fitbox(x, y_thr, wcol, h_thr, thr.split("\n"), size=13,
                            color=col, stroke=col,
                            fill="#fdecea" if col == POS else "#ffffff"))
        if i:
            parts.append(arrow(x - gap - 4, y_el + h_el / 2, x + 4,
                               y_el + h_el / 2, color=FIELD))

    parts.append(text(W / 2, 372, "чого хоче застосунок: показувати з 12:30",
                      size=16, bold=True))
    parts.append(text(W / 2, 412,
                      "зміна одного числа в джерелі цього не дає — усе перелічене вище "
                      "лишиться в конвеєрі й вийде на екран першим",
                      size=14, color=INK))
    parts.append(text(W / 2, 470,
                      "два з трьох потоків стоять заблоковані, тож зупинити їх "
                      "і чекати на їхнє повернення теж не вийде",
                      size=14, color=POS))

    render(os.path.join(IMG, 'in-flight.svg'), W, H, *parts,
           title="Конвеєр у мить перемотування: що він тримає і хто де стоїть")


# ── 2. Порядок дій перемотування з очищенням ────────────────────────────────
def fig_flush_sequence():
    W, H = 1200, 700

    rows = [
        ("проти течії", NEG,
         "seek-подія від застосунку",
         "швидкість, позиція, прапорці; конвеєр віддає її приймачам"),
        ("проти течії", NEG,
         "подія піднімається ланцюгом",
         "від приймача вгору, доки хтось не візьметься — зазвичай демультиплексор"),
        ("за течією", POS,
         "FLUSH_START, позачергово",
         "обганяє буфери; пади перестають приймати, черги порожніють"),
        ("за течією", POS,
         "чекання обриваються",
         "приймач кидає сон на годиннику, заблоковані push повертаються"),
        ("на місці", MUTED,
         "потік зупинено, позицію змінено",
         "індекс дає байтове зміщення; тепер дорога вільна"),
        ("за течією", FIELD,
         "FLUSH_STOP, серіалізовано",
         "пади знову приймають, EOS знято, час програвання в нуль"),
        ("за течією", FIELD,
         "новий SEGMENT і перші буфери",
         "правило перекладу міток мусить прийти раніше за дані"),
        ("на шину", FIELD,
         "наповнення й ASYNC_DONE",
         "приймач набирає перший кадр наново — аж тепер перемотування завершене"),
    ]

    x_dir, w_dir = 40, 190
    x_act, w_act = 258, 400
    x_note, w_note = 686, 474
    y, h, gap = 68, 62, 15

    parts = []
    for i, (direction, col, action, note) in enumerate(rows):
        parts.append(fitbox(x_dir, y, w_dir, h, [direction], size=14,
                            color=col, stroke=col, fill="#ffffff"))
        parts.append(fitbox(x_act, y, w_act, h, [action], size=15, bold=True,
                            fill="#f4f6f8", stroke=col))
        parts.append(fitbox(x_note, y, w_note, h, [note], size=13))
        if i < len(rows) - 1:
            parts.append(arrow(x_act + w_act / 2, y + h + 1,
                               x_act + w_act / 2, y + h + gap - 1, color=MUTED))
        y += h + gap

    render(os.path.join(IMG, 'flush-sequence.svg'), W, H, *parts,
           title="Перемотування з очищенням: вісім дій у трьох напрямках")


# ── 3. Ключовий кадр і три способи в нього влучити ──────────────────────────
def fig_keyframe_snap():
    W, H = 1180, 620

    x_axis0, x_axis1 = 90, 1090
    y_axis = 118
    parts = [line(x_axis0, y_axis, x_axis1, y_axis, color=LINE, sw=2)]

    # ключові кадри — рідкі, звичайні — часті
    keys = [90, 290, 490, 690, 890, 1090]
    for kx in keys:
        parts.append(rect(kx - 7, y_axis - 22, 14, 44, fill="#eafaf1",
                          stroke=FIELD, sw=2, rx=2))
    for i in range(len(keys) - 1):
        step = (keys[i + 1] - keys[i]) / 5.0
        for j in range(1, 5):
            fx = keys[i] + j * step
            parts.append(line(fx, y_axis - 11, fx, y_axis + 11, color=MUTED, sw=1))

    parts.append(text(90, y_axis + 48, "10.0 с", size=13, color=MUTED))
    parts.append(text(490, y_axis + 48, "12.0 с", size=13, color=MUTED))
    parts.append(text(690, y_axis + 48, "14.0 с", size=13, color=MUTED))
    parts.append(text(300, 64, "зелені — ключові кадри, сірі — залежні від сусідів",
                      size=14, color=MUTED))

    tx = 590
    parts.append(line(tx, y_axis - 62, tx, y_axis - 26, color=POS, sw=2, dash="5,4"))
    parts.append(text(tx + 120, y_axis - 72, "просили 12.5 с", size=15,
                      color=POS, bold=True))

    variants = [
        ("KEY_UNIT", FIELD, "#eafaf1",
         ["сегмент починається з 12.0 —", "з найближчого ключового кадру"],
         ["картинка миттєва;", "повзунок стрибає на пів секунди назад"]),
        ("ACCURATE", NEG, "#eaf0fd",
         ["сегмент починається з 12.5,", "а декодування — з 12.0"],
         ["кадри до 12.5 обрізає сегмент;", "перший показ пізніше на пів секунди роботи"]),
        ("без індексу", POS, "#fdecea",
         ["бісекція по байтах:", "оцінка за швидкістю потоку"],
         ["влучання приблизне;", "у контейнері без таблиці інакше не буває"]),
    ]

    y = 236
    for name, col, bg, what, cost in variants:
        parts.append(fitbox(40, y, 236, 96, [name], size=17, bold=True,
                            fill=bg, stroke=col, color=col))
        parts.append(fitbox(306, y, 376, 96, what, size=14))
        parts.append(fitbox(712, y, 428, 96, cost, size=14,
                            fill="#ffffff", stroke=MUTED))
        y += 122

    parts.append(text(W / 2, 578,
                      "вибір не про точність проти неточності, а про те, "
                      "хто платить: око чи процесор",
                      size=15, color=INK))

    render(os.path.join(IMG, 'keyframe-snap.svg'), W, H, *parts,
           title="Почати можна лише з ключового кадру — далі варіанти")


# ── 4. Час програвання після перемотування з флашем і без ───────────────────
def fig_segment_base():
    W, H = 1160, 560

    def panel(y_top, title, col, bg, seg2_x0, labels):
        p = [text(70, y_top, title, size=17, bold=True, color=col, anchor="start")]
        y_ax = y_top + 96
        p.append(line(70, y_ax, 1090, y_ax, color=LINE, sw=2))
        p.append(text(1090, y_ax + 40, "час програвання", size=13,
                      color=MUTED, anchor="end"))

        p.append(rect(70, y_ax - 34, 330, 68, fill="#f4f6f8", stroke=LINE))
        p.append(text(235, y_ax + 6, "перший сегмент: 0.0 → 4.0", size=14))

        p.append(line(430, y_ax - 62, 430, y_ax + 40, color=POS, sw=2, dash="6,4"))
        p.append(text(430, y_ax - 74, "перемотування", size=14, color=POS, bold=True))

        p.append(rect(seg2_x0, y_ax - 34, 1090 - seg2_x0, 68, fill=bg, stroke=col))
        p.append(text((seg2_x0 + 1090) / 2, y_ax + 6, labels[0], size=14, color=col))
        p.append(text((seg2_x0 + 1090) / 2, y_ax + 62, labels[1], size=13, color=MUTED))
        return p

    parts = []
    parts += panel(70, "з очищенням", NEG, "#eaf0fd", 470,
                   ["другий сегмент: base = 0.0",
                    "відлік почато наново, конвеєр отримав новий базовий час"])
    parts += panel(330, "без очищення", FIELD, "#eafaf1", 630,
                   ["другий сегмент: base = 4.0",
                    "відлік триває, бо нічого не викидали й показ не переривався"])

    parts.append(text(W / 2, 528,
                      "мітки кадрів в обох випадках однакові — різниться лише те, "
                      "на яку мить конвеєр їх переводить",
                      size=15, color=INK))

    render(os.path.join(IMG, 'segment-base.svg'), W, H, *parts,
           title="Що робить із відліком часу наявність або відсутність флаша")


# ── 5. Куди лягає кожен аргумент seek-події (довідка) ───────────────────────
def fig_seek_field_map():
    W, H = 1220, 640

    parts = [
        text(260, 74, "що передає застосунок", size=16, bold=True, color=MUTED),
        text(935, 74, "куди це лягає в GstSegment", size=16, bold=True, color=MUTED),
    ]

    rows = [
        (["rate", "gdouble; знак задає напрям"],
         ["segment.rate", "приймач ділить відстань на |rate|"], NEG),
        (["format", "TIME, BYTES, DEFAULT, PERCENT…"],
         ["segment.format", "мусить збігтися з форматом сегмента"], NEG),
        (["flags", "GstSeekFlags — бітова маска"],
         ["segment.flags", "переїжджають лише SEGMENT і TRICKMODE*"], FIELD),
        (["start_type + start", "SET — значення, END — від кінця, NONE — не чіпати"],
         ["segment.start", "NONE лишає те, що вже було"], POS),
        (["stop_type + stop", "те саме для кінця відрізка"],
         ["segment.stop", "−1 означає «до кінця потоку»"], POS),
    ]

    xl, wl = 50, 420
    xr, wr = 700, 470
    y, h, gap = 100, 62, 16

    for left, right, col in rows:
        parts.append(fitbox(xl, y, wl, h, left, size=14, fill="#f4f6f8", stroke=col))
        parts.append(fitbox(xr, y, wr, h, right, size=14, fill="#ffffff", stroke=col))
        parts.append(arrow(xl + wl + 6, y + h / 2, xr - 6, y + h / 2, color=col))
        y += h + gap

    parts.append(text(W / 2, 502,
                      "решту полів сегмента не передають — їх рахує gst_segment_do_seek()",
                      size=16, bold=True))
    parts.append(fitbox(50, 518, 1120, 76,
                        ["base = 0, якщо стоїть FLUSH; інакше — накопичений час програвання",
                         "offset, position, time перераховуються від start і напрямку"],
                        size=14, fill="#ffffff", stroke=MUTED))

    parts.append(text(W / 2, 622,
                      "вихідний параметр update каже, чи змінилася позиція, "
                      "чи сама лише швидкість",
                      size=14, color=MUTED))

    render(os.path.join(IMG, 'seek-field-map.svg'), W, H, *parts,
           title="Аргументи seek-події та поля GstSegment, у які вони лягають")


# ── 6. Прапорці як біти однієї маски: групи й конфлікти ─────────────────────
def fig_seek_flag_map():
    W, H = 1240, 700

    parts = [text(W / 2, 70,
                  "прапорці — біти однієї маски; групи незалежні, "
                  "конфлікти бувають лише всередині групи",
                  size=16, bold=True)]

    bands = [
        ("як виконувати", POS, "#fdecea",
         [["FLUSH", "1<<0   (1)"]], 300),
        ("куди влучати", NEG, "#eaf0fd",
         [["ACCURATE", "1<<1   (2)"],
          ["KEY_UNIT", "1<<2   (4)"],
          ["SNAP_BEFORE", "1<<5   (32)"],
          ["SNAP_AFTER", "1<<6   (64)"],
          ["SNAP_NEAREST", "32|64   (96)"]], 168),
        ("що робити в кінці", FIELD, "#eafaf1",
         [["SEGMENT", "1<<3   (8)"]], 300),
        ("пришвидшений хід", MUTED, "#f4f6f8",
         [["TRICKMODE = SKIP", "1<<4   (16)", "від 1.6"],
          ["TRICKMODE_KEY_UNITS", "1<<7   (128)", "від 1.6"],
          ["TRICKMODE_NO_AUDIO", "1<<8   (256)", "від 1.6"],
          ["TRICKMODE_FORWARD_PREDICTED", "1<<9   (512)", "від 1.18"]], 213),
        ("швидкість без стрибка", POS, "#fdecea",
         [["INSTANT_RATE_CHANGE", "1<<10   (1024)", "від 1.18"]], 300),
    ]

    x_lab, w_lab = 40, 250
    x_chip = 306
    y, h, gap = 106, 68, 20

    for label, col, bg, chips, wch in bands:
        parts.append(fitbox(x_lab, y, w_lab, h, [label], size=15, bold=True,
                            color=col, stroke=col, fill="#ffffff"))
        x = x_chip
        for chip in chips:
            parts.append(fitbox(x, y, wch, h, chip, size=13, fill=bg, stroke=col))
            x += wch + 13
        y += h + gap

    notes = [
        "ACCURATE і KEY_UNIT одне одного не виключають — визначені всі чотири поєднання",
        "SNAP_NEAREST — це SNAP_BEFORE | SNAP_AFTER, тож «без прив'язки» задає лише відсутність обох",
        "SKIP і TRICKMODE — той самий біт: перевірка на SKIP спрацює й на TRICKMODE",
        "INSTANT_RATE_CHANGE несумісний із FLUSH, зі зміною позиції та зі зміною знака швидкості",
    ]
    ny = 578
    for n in notes:
        parts.append(text(W / 2, ny, n, size=14, color=INK))
        ny += 28

    render(os.path.join(IMG, 'seek-flag-map.svg'), W, H, *parts,
           title="GstSeekFlags: групи прапорців і конфлікти між ними")


# ── 7. Рукостискання застосунку з конвеєром (до вставки proj-seek-driver) ───
def fig_seek_handshake():
    W, H = 1280, 706

    rows = [
        ("застосунок", MUTED, "#ffffff",
         ["вичищаємо з шини старі ASYNC_DONE"],
         ["інакше перший же pop віддасть чуже —",
          "від наповнення при пуску конвеєра"]),
        ("застосунок", NEG, "#eaf0fd",
         ["gst_element_seek(… FLUSH …) → TRUE"],
         ["повертається за мілісекунди;",
          "TRUE означає «прохання прийняте», не «зроблено»"]),
        ("конвеєр", POS, "#fdecea",
         ["приймачі шлють ASYNC_START"],
         ["наповнення втрачено: ціль PLAYING,",
          "а показувати ще нічого"]),
        ("конвеєр", POS, "#fdecea",
         ["флаш, зміна позиції, новий SEGMENT"],
         ["у цю мить query_position віддає СТАРУ позицію —",
          "ту, з якої перемотували"]),
        ("конвеєр", FIELD, "#eafaf1",
         ["кожен приймач шле свій ASYNC_DONE"],
         ["наповнилася одна гілка;",
          "у відео зі звуком їх щонайменше дві"]),
        ("шина", FIELD, "#eafaf1",
         ["ASYNC_DONE від САМОГО конвеєра"],
         ["бін звів звіти дітей — оце й є",
          "справжній кінець перемотування"]),
        ("застосунок", NEG, "#eaf0fd",
         ["query_position — аж тепер правда"],
         ["і саме тепер видно, куди насправді влучили:",
          "прив'язка до ключового кадру могла зсунути"]),
    ]

    x_who, w_who = 40, 176
    x_act, w_act = 238, 436
    x_note, w_note = 696, 544
    y, h, gap = 68, 62, 15

    parts = []
    for i, (who, col, bg, act, note) in enumerate(rows):
        parts.append(fitbox(x_who, y, w_who, h, [who], size=15,
                            color=col, stroke=col, fill="#ffffff"))
        parts.append(fitbox(x_act, y, w_act, h, act, size=15, bold=True,
                            fill=bg, stroke=col))
        parts.append(fitbox(x_note, y, w_note, h, note, size=13))
        if i < len(rows) - 1:
            parts.append(arrow(x_act + w_act / 2, y + h + 1,
                               x_act + w_act / 2, y + h + gap - 1, color=MUTED))
        y += h + gap

    parts.append(fitbox(40, 622, 1200, 62,
                        ["без прапорця FLUSH асинхронного переходу не буде взагалі —",
                         "а отже, не буде й ASYNC_DONE: чекання на нього достоїть до таймауту"],
                        size=14, fill="#ffffff", stroke=POS, color=POS))

    render(os.path.join(IMG, 'seek-handshake.svg'), W, H, *parts,
           title="Що бачить застосунок між викликом seek і готовим кадром")


# ── 8. Злиття прохань під час шкрябання (до вставки proj-seek-driver) ───────
def fig_scrub_coalesce():
    W, H = 1260, 560

    states = [
        (60, "спокій", MUTED, "#ffffff",
         ["перемотування в польоті немає"]),
        (490, "у польоті", NEG, "#eaf0fd",
         ["seek надіслано,", "чекаємо на ASYNC_DONE"]),
        (890, "у польоті + чекає", POS, "#fdecea",
         ["під час польоту прийшло", "нове положення повзунка"]),
    ]

    w_st, h_st, y_st = 310, 104, 116
    parts = []
    for x, name, col, bg, note in states:
        parts.append(fitbox(x, y_st, w_st, h_st, [name] + note, size=15,
                            fill=bg, stroke=col, color=col))

    parts.append(arrow(60 + w_st + 8, y_st + h_st / 2, 490 - 8,
                       y_st + h_st / 2, color=FIELD))
    parts.append(text((60 + w_st + 490) / 2, y_st - 14,
                      "рух повзунка → шлемо seek", size=14, color=FIELD))

    parts.append(arrow(490 + w_st + 8, y_st + h_st / 2, 890 - 8,
                       y_st + h_st / 2, color=FIELD))
    parts.append(text((490 + w_st + 890) / 2, y_st - 14,
                      "ще рух → лише запам'ятали", size=14, color=FIELD))

    rows = [
        ("ASYNC_DONE, нового положення не було", MUTED,
         "повертаємося в «спокій»: конвеєр стоїть там, куди останнє прохання й вело"),
        ("ASYNC_DONE, а положення змінилося", POS,
         "шлемо seek на ОСТАННЄ значення й знову «у польоті»; проміжні гинуть непоказаними"),
    ]
    y = 288
    for label, col, note in rows:
        parts.append(fitbox(60, y, 470, 64, [label], size=14,
                            color=col, stroke=col, fill="#ffffff"))
        parts.append(arrow(536, y + 32, 574, y + 32, color=col))
        parts.append(fitbox(582, y, 618, 64, [note], size=13))
        y += 80

    parts.append(fitbox(60, 452, 1140, 74,
                        ["без злиття сорок рухів руки дають сорок перемотувань поспіль,",
                         "і кожне чесно чекає свого наповнення — картинка наздоганяє руку секундами"],
                        size=14, fill="#ffffff", stroke=NEG, color=NEG))

    render(os.path.join(IMG, 'scrub-coalesce.svg'), W, H, *parts,
           title="Шкрябання: одне перемотування в польоті, решта прохань зливаються")


if __name__ == '__main__':
    fig_in_flight()
    fig_flush_sequence()
    fig_keyframe_snap()
    fig_segment_base()
    fig_seek_field_map()
    fig_seek_flag_map()
    fig_seek_handshake()
    fig_scrub_coalesce()
    print("ok")
