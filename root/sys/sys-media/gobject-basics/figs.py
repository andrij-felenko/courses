# -*- coding: utf-8 -*-
"""Фігури до теми «GObject: об'єктна система, на якій стоїть GStreamer»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Ланцюг типів ────────────────────────────────────────────────────────
def fig_type_chain():
    W, H = 1040, 700
    f = []

    rows = [
        ("GObject", "лічильник посилань · властивості\nсигнали · GValue", "#eef2f8"),
        ("GInitiallyUnowned", "перше посилання — плавальне\n(нічиє, доки хтось не привласнить)", "#eef2f8"),
        ("GstObject", "ім'я · батько-контейнер\nм'ютекс об'єкта · прив'язки керування", "#eef6ee"),
        ("GstElement", "стани й переходи · пади\nшина · годинник", "#eef6ee"),
        ("GstBaseTransform", "готовий кістяк фільтра:\nузгодження caps, обробка на місці", "#eef6ee"),
        ("GstX264Enc  (з плагіна)", "поля bitrate, speed-preset, tune\nвласний change_state", "#f7f4ee"),
    ]

    x0, bw = 60, 380
    dx, dw = 500, 470
    y = 70
    rh = 78
    gap = 34

    f.append(text(x0 + bw / 2, 44, "тип у таблиці типів", size=14, bold=True, color=MUTED))
    f.append(text(dx + dw / 2, 44, "що цей рівень додає", size=14, bold=True, color=MUTED))

    for i, (name, what, col) in enumerate(rows):
        yy = y + i * (rh + gap)
        f.append(fitbox(x0, yy, bw, rh, name, size=17, bold=True, fill=col))
        f.append(fitbox(dx, yy, dw, rh, what, size=14, fill="#ffffff"))
        if i:
            f.append(arrow(x0 + bw / 2, yy - gap + 4, x0 + bw / 2, yy - 4))

    yy = y + len(rows) * (rh + gap)
    f.append(fitbox(x0, yy + 6, dx + dw - x0, 66,
                    "ядро зібрано до рівня GstElement; усе, що нижче, реєструється "
                    "в тій самій таблиці вже під час роботи — коли завантажили плагін",
                    size=15, fill="#f7f4ee"))

    render(os.path.join(OUT, 'type-chain.svg'), W, H, *f,
           title="Ланцюг типів від GObject до елемента з плагіна")


# ── 2. Клас і примірник ────────────────────────────────────────────────────
def fig_instance_class():
    W, H = 1060, 660
    f = []

    # два примірники
    for i, nm in enumerate(("примірник enc1", "примірник enc2")):
        x = 60
        yy = 90 + i * 250
        f.append(rect(x, yy, 380, 200, fill="#ffffff"))
        f.append(text(x + 190, yy + 26, nm, size=15, bold=True))
        f.append(fitbox(x + 20, yy + 40, 340, 44, "GstObject → GObject → g_class", size=13,
                        fill="#eef2f8"))
        f.append(fitbox(x + 20, yy + 94, 340, 40, "поля GstElement: стан, пади", size=13,
                        fill="#eef6ee"))
        f.append(fitbox(x + 20, yy + 144, 340, 40,
                        "власні поля: bitrate = %d" % (4096 if i == 0 else 1500),
                        size=13, fill="#f7f4ee"))
        f.append(arrow(x + 390, yy + 62, 615, 210 if i == 0 else 250))

    f.append(text(520, 176, "g_class", size=13, color=MUTED))

    # клас
    cx, cw = 625, 380
    f.append(rect(cx, 120, cw, 400, fill="#ffffff"))
    f.append(text(cx + cw / 2, 148, "GstX264EncClass — один на тип", size=15, bold=True))
    f.append(fitbox(cx + 20, 166, cw - 40, 84,
                    "копія GstElementClass:\nусі батьківські вказівники на функції",
                    size=13, fill="#eef2f8"))
    f.append(fitbox(cx + 20, 262, cw - 40, 60,
                    "change_state → власна реалізація", size=13, fill="#eef6ee"))
    f.append(fitbox(cx + 20, 334, cw - 40, 60,
                    "метадані · шаблони падів", size=13, fill="#eef6ee"))
    f.append(fitbox(cx + 20, 406, cw - 40, 94,
                    "описи властивостей:\nbitrate · speed-preset · tune",
                    size=13, fill="#f7f4ee"))

    f.append(fitbox(60, 570, 945, 62,
                    "стан — у кожного свій; код і описи — спільні: "
                    "структуру класу створюють один раз, копіюючи батьківську і перекриваючи потрібне",
                    size=15, fill="#f7f4ee"))

    render(os.path.join(OUT, 'instance-class.svg'), W, H, *f,
           title="Примірники окремо, клас один на тип")


# ── 3. Шлях властивості ────────────────────────────────────────────────────
def fig_property_path():
    W, H = 780, 860
    f = []

    steps = [
        ('bitrate=4096  — текст у рядку конвеєра', "#f7f4ee"),
        ('пошук опису на ім\'я "bitrate"\nвгору по ланцюгу класів', "#ffffff"),
        ('опис знайдено: беззнакове ціле\nмежі 1 … 2048000, типове 2048', "#eef2f8"),
        ('текст "4096" → GValue типу uint', "#ffffff"),
        ('звірка з межами опису\n(вилізло за край — притиснути й попередити)', "#ffffff"),
        ('клас->set_property (об\'єкт, номер, GValue, опис)', "#eef6ee"),
        ('self->bitrate = 4096  — поле структури', "#eef6ee"),
    ]

    x, bw = 70, 640
    y = 60
    rh = 86
    gap = 32
    for i, (s, col) in enumerate(steps):
        yy = y + i * (rh + gap)
        f.append(fitbox(x, yy, bw, rh, s, size=15, fill=col))
        if i:
            f.append(arrow(x + bw / 2, yy - gap + 4, x + bw / 2, yy - 4))

    yy = y + len(steps) * (rh + gap)
    f.append(fitbox(x, yy + 4, bw, 56,
                    "ядро знає ім'я й опис — і жодного разу не торкається поля напряму",
                    size=14, fill="#f7f4ee"))

    render(os.path.join(OUT, 'property-path.svg'), W, H, *f,
           title="Від тексту до поля структури")


# ── 4. Плавальне посилання й посилання у власність ─────────────────────────
def fig_floating_ref():
    W, H = 1080, 620
    f = []

    lx, rx, bw = 60, 580, 440

    f.append(fitbox(lx, 56, bw, 52, "створення елемента", size=16, bold=True, fill="#eef6ee"))
    f.append(fitbox(rx, 56, bw, 52, "отримання шини конвеєра", size=16, bold=True, fill="#eef2f8"))

    left = [
        'gst_element_factory_make ("x264enc")',
        'лічильник 1, посилання ПЛАВАЛЬНЕ\n(нічиє)',
        'gst_bin_add (bin, enc)\n→ контейнер робить ref_sink',
        'лічильник лишився 1,\nпрапорець знято: власник — контейнер',
        'вашого unref тут БУТИ НЕ ПОВИННО',
    ]
    right = [
        'gst_element_get_bus (pipeline)',
        'лічильник 1 → 2:\nвам видали ВЛАСНЕ посилання',
        'ви користуєтеся шиною',
        'gst_object_unref (bus)\n→ лічильник назад 1',
        'пропущений unref = тихий витік',
    ]

    y0, rh, gap = 128, 74, 26
    for i in range(5):
        yy = y0 + i * (rh + gap)
        f.append(fitbox(lx, yy, bw, rh, left[i], size=14,
                        fill="#ffffff" if i < 4 else "#fdecea"))
        f.append(fitbox(rx, yy, bw, rh, right[i], size=14,
                        fill="#ffffff" if i < 4 else "#fdecea"))
        if i:
            f.append(arrow(lx + bw / 2, yy - gap + 3, lx + bw / 2, yy - 3))
            f.append(arrow(rx + bw / 2, yy - gap + 3, rx + bw / 2, yy - 3))

    render(os.path.join(OUT, 'floating-ref.svg'), W, H, *f,
           title="Хто кому винен посилання")


# ── 5. Хронологія об'єктної системи (до вставки hist-gobject-birth) ────────
def fig_gobject_timeline():
    W, H = 1240, 820
    f = []

    cx0, cw0 = 40, 170          # колонка дат
    cx1, cw1 = 240, 470         # колонка GTK / GLib
    cx2, cw2 = 740, 460         # колонка GStreamer

    f.append(text(cx0 + cw0 / 2, 46, "коли", size=15, bold=True, color=MUTED))
    f.append(text(cx1 + cw1 / 2, 46, "GTK і GLib", size=15, bold=True, color=MUTED))
    f.append(text(cx2 + cw2 / 2, 46, "GStreamer", size=15, bold=True, color=MUTED))

    rows = [
        ("1996 — 1998",
         "об'єктна система росте всередині GTK:\nGtkObject, сигнали, типи під час роботи",
         ""),
        ("січень 2000",
         "",
         "перший gstobject.h:\nструктура починається з GtkObject,\nа поряд — власний атомарний лічильник"),
        ("11 січня 2001",
         "",
         "перший публічний випуск 0.1.0"),
        ("25 червня 2001",
         "нова тип-система ще в розробці\n(гілка GLib 2.0)",
         "злиття гілки GOBJECT1: шар gobject2gtk\nдає збірку і на GTK 1.2, і на нову GLib"),
        ("11 березня 2002",
         "GTK+ 2.0: об'єктну систему винесено\nз GTK у GLib окремим GObject",
         ""),
        ("27 лютого 2006",
         "GLib 2.10: GInitiallyUnowned —\nплавальне посилання приходить у GObject",
         "своя реалізація плавального посилання\nлишається ще на чотири роки"),
        ("7 грудня 2010",
         "",
         "GstObject переведено на GInitiallyUnowned,\nпрапорець GST_FLOATING прибрано"),
        ("24 вересня 2012",
         "",
         "випуск 1.0.0 — зміна доходить до тих,\nхто пише конвеєри"),
    ]

    y0, rh, gap = 72, 80, 12
    for i, (when, gtk, gst) in enumerate(rows):
        yy = y0 + i * (rh + gap)
        f.append(fitbox(cx0, yy, cw0, rh, when, size=14, bold=True, fill="#f7f4ee"))
        if gtk:
            f.append(fitbox(cx1, yy, cw1, rh, gtk, size=13, fill="#eef2f8"))
        if gst:
            f.append(fitbox(cx2, yy, cw2, rh, gst, size=13, fill="#eef6ee"))
        if i:
            f.append(line(cx0 + cw0 / 2, yy - gap - 2, cx0 + cw0 / 2, yy + 2,
                          color=MUTED, sw=2))

    render(os.path.join(OUT, 'gobject-timeline.svg'), W, H, *f,
           title="Хронологія: об'єктна система від GTK до GStreamer 1.0")


# ── 6. Сходи до опису: що доступно на кожному кроці ────────────────────────
def fig_inspect_steps():
    W, H = 1140, 760
    f = []

    x0, bw = 56, 430
    dx, dw = 546, 540
    y0, rh, gap = 84, 92, 26

    f.append(text(x0 + bw / 2, 52, "виклик", size=15, bold=True, color=MUTED))
    f.append(text(dx + dw / 2, 52, "що після нього можна прочитати",
                  size=15, bold=True, color=MUTED))

    rows = [
        ("gst_init ()",
         "реєстр у пам'яті: імена, ранги й категорії\nусіх фабрик — код плагінів ще не в процесі",
         "#eef2f8"),
        ("gst_element_factory_find (\"x264enc\")",
         "фабрика: людська назва, автор, категорія,\nшаблони падів у вигляді рядків",
         "#eef2f8"),
        ("gst_plugin_feature_load (…)",
         "файл плагіна завантажено в процес;\nповертає ІНШИЙ об'єкт — беремо його",
         "#eef6ee"),
        ("gst_element_factory_get_element_type (…)",
         "GType елемента — до завантаження тут був 0",
         "#eef6ee"),
        ("g_type_class_ref (type)",
         "виконано class_init: властивості, сигнали\nй шаблони падів з'явилися в таблиці типів",
         "#f7f4ee"),
    ]

    for i, (call, gain, col) in enumerate(rows):
        yy = y0 + i * (rh + gap)
        f.append(fitbox(x0, yy, bw, rh, call, size=15, bold=True, fill=col))
        f.append(fitbox(dx, yy, dw, rh, gain, size=14, fill="#ffffff"))
        if i:
            f.append(arrow(x0 + bw / 2, yy - gap + 3, x0 + bw / 2, yy - 3))

    yy = y0 + len(rows) * (rh + gap)
    f.append(fitbox(x0, yy + 8, dx + dw - x0, 78,
                    "жодного елемента ще не створено — увесь опис лежить у класі, "
                    "тому інспектор працює й з тими елементами,\n"
                    "які не вдалося б увімкнути: немає камери, немає ліцензії, "
                    "немає вільного пристрою кодування",
                    size=15, fill="#f7f4ee"))

    render(os.path.join(OUT, 'inspect-steps.svg'), W, H, *f,
           title="Що доступно інспекторові на кожному кроці до класу")


# ── Карта 32 бітів прапорців властивості ───────────────────────────────────
def fig_param_flags_bits():
    W, H = 1140, 640
    f = []

    x0, cell = 84, 28
    ytop, ch = 108, 54

    f.append(text(x0 + 16 * cell, 40, "один прапорець — один біт 32-розрядного числа",
                  size=16, bold=True))

    zones = [
        (0, 8, "#eef2f8"),    # ядро GObject
        (8, 9, "#fdecea"),    # межа
        (9, 15, "#eef6ee"),   # GStreamer
        (15, 16, "#ffffff"),  # вільний
        (16, 30, "#f7f4ee"),  # сторонні
        (30, 32, "#eef2f8"),  # знову GObject
    ]
    for lo, hi, col in zones:
        f.append(rect(x0 + lo * cell, ytop, (hi - lo) * cell, ch, fill=col))

    for b in range(1, 32):
        f.append(line(x0 + b * cell, ytop + 4, x0 + b * cell, ytop + ch - 4,
                      color="#c8ccd2", sw=1))

    for b in (0, 4, 8, 12, 16, 20, 24, 28, 31):
        f.append(text(x0 + b * cell + cell / 2, ytop + ch + 26, str(b),
                      size=13, color=MUTED))
    f.append(text(x0 - 24, ytop + ch + 26, "біт", size=13, color=MUTED, anchor="end"))

    bx = x0 + 8 * cell + cell / 2
    f.append(line(bx, ytop - 30, bx, ytop - 6, color=POS, sw=2))
    f.append(text(bx, ytop - 38, "G_PARAM_USER_SHIFT = 8", size=13, color=POS, bold=True))

    rows = [
        ("#eef2f8", "біти 0–7 — сам GObject: READABLE, WRITABLE, CONSTRUCT, "
                    "CONSTRUCT_ONLY, LAX_VALIDATION, STATIC_NAME/NICK/BLURB"),
        ("#fdecea", "біт 8 — межа: усе, що вище, віддано бібліотекам поверх GObject"),
        ("#eef6ee", "біти 9–14 — GStreamer: CONTROLLABLE, MUTABLE_READY / PAUSED / "
                    "PLAYING, DOC_SHOW_DEFAULT, CONDITIONALLY_AVAILABLE"),
        ("#ffffff", "біт 15 — поки не зайнятий ніким"),
        ("#f7f4ee", "біти 16–29 — GST_PARAM_USER_SHIFT: для стороннього коду понад GStreamer"),
        ("#eef2f8", "біти 30–31 — знову GObject: EXPLICIT_NOTIFY і DEPRECATED, "
                    "дописані з протилежного краю"),
    ]
    ly, lh, gap = 240, 50, 14
    for i, (col, txt) in enumerate(rows):
        yy = ly + i * (lh + gap)
        f.append(rect(x0, yy, 46, lh, fill=col))
        f.append(fitbox(x0 + 62, yy, 936, lh, txt, size=14,
                        fill="#ffffff", stroke="#ffffff"))

    render(os.path.join(OUT, 'param-flags-bits.svg'), W, H, *f,
           title="Хто володіє якими бітами прапорців властивості")


# ── Порядок виклику під час емісії сигналу ─────────────────────────────────
def fig_signal_emission():
    W, H = 1180, 720
    f = []

    mx, mw = 70, 560
    steps = [
        ("g_signal_emit_by_name (елемент, \"pad-added\", pad)", "#f7f4ee"),
        ("RUN_FIRST — метод класу,\nякщо сигнал оголошено з цим прапорцем", "#eef2f8"),
        ("обробники g_signal_connect\nу порядку підключення", "#ffffff"),
        ("RUN_LAST — метод класу\n(звичний вибір у GStreamer)", "#eef2f8"),
        ("обробники g_signal_connect_after", "#ffffff"),
        ("RUN_CLEANUP — метод класу,\nколи сигнал оголошено ще й так", "#eef2f8"),
    ]
    y0, rh, gap = 84, 76, 30
    for i, (s, col) in enumerate(steps):
        yy = y0 + i * (rh + gap)
        f.append(fitbox(mx, yy, mw, rh, s, size=14, fill=col))
        if i:
            f.append(arrow(mx + mw / 2, yy - gap + 4, mx + mw / 2, yy - 4))

    nx, nw = 700, 400
    notes = [
        (1, "деталь відсіює ще до першого виклику:\n«notify::bitrate» будить лише тих,\nхто підписався саме на цю деталь"),
        (2, "накопичувач бачить кожне повернене\nзначення й може обірвати ланцюг\n(так робиться «перший, хто відповів»)"),
        (4, "g_signal_stop_emission_by_name\nобриває решту з будь-якого місця"),
    ]
    for idx, s in notes:
        yy = y0 + idx * (rh + gap) - 6
        f.append(fitbox(nx, yy, nw, rh + 12, s, size=13, fill="#ffffff"))
        f.append(line(mx + mw + 10, yy + (rh + 12) / 2, nx - 10, yy + (rh + 12) / 2,
                      color=MUTED, sw=1.2, dash="5 4"))

    f.append(fitbox(mx, y0 + len(steps) * (rh + gap) + 10, 1030, 58,
                    "усе це — один синхронний виклик у нитці, що випустила сигнал: "
                    "поки ланцюг не добіг до кінця, ця нитка нічого іншого не робить",
                    size=15, fill="#f7f4ee"))

    render(os.path.join(OUT, 'signal-emission.svg'), W, H, *f,
           title="Порядок виклику під час емісії сигналу")


if __name__ == '__main__':
    fig_type_chain()
    fig_gobject_timeline()
    fig_instance_class()
    fig_property_path()
    fig_floating_ref()
    fig_inspect_steps()
    fig_param_flags_bits()
    fig_signal_emission()
    print("ok:", os.listdir(OUT))
