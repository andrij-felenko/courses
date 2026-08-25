# -*- coding: utf-8 -*-
"""Фігури до теми «Буфери й пам'ять: передача кадру без копіювання»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def p(name):
    return os.path.join(OUT, name)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Конверт і вміст: два GstBuffer над одним GstMemory
# ─────────────────────────────────────────────────────────────────────────────
def fig_buffer_memory():
    W, H = 940, 520
    f = []

    # два конверти
    f.append(fitbox(60, 62, 360, 140,
                    "GstBuffer A\n"
                    "PTS 3.200 с, тривалість 33 мс\n"
                    "прапорці, GstVideoMeta",
                    size=15))
    f.append(fitbox(520, 62, 360, 140,
                    "GstBuffer B\n"
                    "PTS 3.200 с, інші прапорці\n"
                    "своя мітка гілки",
                    size=15))

    f.append(text(240, 48, "конверт гілки запису", size=13, color=MUTED))
    f.append(text(700, 48, "конверт гілки показу", size=13, color=MUTED))

    # стрілки вниз до пам'яті
    f.append(arrow(240, 202, 240, 322))
    f.append(arrow(700, 202, 700, 322))
    f.append(text(252, 268, "посилання", size=13, color=MUTED, anchor="start"))
    f.append(text(712, 268, "посилання", size=13, color=MUTED, anchor="start"))

    # блок пам'яті
    f.append(text(470, 312, "maxsize — усе, що виділив алокатор", size=13, color=MUTED))
    f.append(rect(170, 322, 600, 96, fill="#ffffff"))
    f.append(rect(252, 340, 376, 60, fill="#e8f4ec", stroke=FIELD))
    f.append(text(440, 376, "offset … offset+size — видимі байти", size=13))
    f.append(text(211, 376, "offset", size=11, color=MUTED))
    f.append(text(699, 376, "запас", size=11, color=MUTED))

    f.append(text(470, 448, "GstMemory  ·  лічильник посилань = 2", size=15, bold=True))
    f.append(text(470, 478, "жоден із конвертів не володіє цією пам'яттю сам,", size=13, color=MUTED))
    f.append(text(470, 498, "тож писати в неї не може ані A, ані B", size=13, color=MUTED))

    render(p('buffer-memory.svg'), W, H, *f,
           title="Конверт описує кадр, пам'ять його зберігає")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Крок рядка й запас до вирівнювання
# ─────────────────────────────────────────────────────────────────────────────
def fig_stride():
    W, H = 940, 400
    f = []

    x0, vis, pad = 130, 380, 42
    rows, rh, gap = 5, 30, 6
    y0 = 76

    for i in range(rows):
        y = y0 + i * (rh + gap)
        f.append(rect(x0, y, vis, rh, fill=FILL))
        f.append(rect(x0 + vis, y, pad, rh, fill="#f7e6e6", stroke="#c9a2a2"))

    # стрілка кроку рядка ліворуч від рядків
    f.append(arrow(103, y0 + 4, 103, y0 + rh + gap + 4))
    f.append(text(95, y0 + 24, "крок", size=13, color=MUTED, anchor="end"))

    y_end = y0 + rows * (rh + gap)
    f.append(text(x0 + vis / 2, y_end + 24, "рядок кадру", size=13, color=MUTED))

    # легенда праворуч
    lx = 620
    f.append(rect(lx, 86, 24, 18, fill=FILL))
    f.append(text(lx + 34, 100, "байти пікселів рядка", size=13, anchor="start"))
    f.append(rect(lx, 126, 24, 18, fill="#f7e6e6", stroke="#c9a2a2"))
    f.append(text(lx + 34, 140, "запас до вирівнювання", size=13, anchor="start"))
    f.append(text(lx, 186, "ширина = 1920 пікселів", size=13, anchor="start"))
    f.append(text(lx, 210, "крок рядка = 2048 байтів", size=13, anchor="start", bold=True))

    f.append(fitbox(130, 296, 680, 62,
                    "Адреса пікселя (x, y) у площині яскравості:\n"
                    "base + y · крок_рядка + x — ширина кадру тут не бере участі",
                    size=14))

    render(p('stride-padding.svg'), W, H, *f,
           title="Рядок у пам'яті довший за рядок у кадрі")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Запит на алокацію
# ─────────────────────────────────────────────────────────────────────────────
def fig_allocation():
    W, H = 960, 430
    f = []

    f.append(fitbox(60, 108, 210, 74, "v4l2src\nкамера", size=15))
    f.append(fitbox(375, 108, 210, 74, "videoconvert\nперетворення", size=15))
    f.append(fitbox(690, 108, 210, 74, "glimagesink\nдисплей", size=15))

    # 1. запит униз за потоком
    f.append(text(480, 62, "1. запит ALLOCATION іде за потоком", size=14))
    f.append(arrow(165, 82, 795, 82))

    # 2. відповіді вгору
    f.append(text(480, 210, "2. кожен долучає свої вимоги і повертає їх угору", size=14))
    f.append(arrow(795, 228, 165, 228))

    f.append(fitbox(90, 262, 780, 108,
                    "Споживач відповідає: «ось мій пул, розмір буфера 3 110 400 байтів,\n"
                    "крок рядка 2048, щонайменше 4 буфери, я розумію GstVideoMeta».\n"
                    "Джерело бере цей пул — і кадр від початку лежить там, де його покажуть.",
                    size=14))

    render(p('allocation-query.svg'), W, H, *f,
           title="Спершу домовитися про пам'ять, потім передавати кадри")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Де лежать байти і що означає map
# ─────────────────────────────────────────────────────────────────────────────
def fig_map_domains():
    W, H = 960, 450
    f = []

    cols = [
        (50, "Системна пам'ять\n(звичайний алокатор)",
             "map віддає вказівник\nі більше нічого не робить\n— безкоштовно"),
        (350, "Пам'ять відеокарти\n(текстура GL)",
              "map тягне вміст\nчерез шину в процесор\n— сотні мікросекунд"),
        (650, "Буфер драйвера\n(dmabuf, V4L2)",
              "map відображає дескриптор\nі узгоджує кеш\n— системний виклик"),
    ]
    for x, top, bottom in cols:
        f.append(fitbox(x, 78, 260, 86, top, size=14))
        f.append(arrow(x + 130, 168, x + 130, 218))
        f.append(fitbox(x, 220, 260, 100, bottom, size=13))

    f.append(fitbox(50, 356, 860, 62,
                    "gst_buffer_map — не «взяти вказівник», а «зробити цю пам'ять доступною мені».\n"
                    "Той самий рядок коду коштує від нуля до кількох мілісекунд на кадр.",
                    size=14))

    render(p('map-domains.svg'), W, H, *f,
           title="Байти кадру не завжди у вашому адресному просторі")


# ─────────────────────────────────────────────────────────────────────────────
# 5. Анатомія буфера до і після 1.0 (до вставки hist-memory-model-rewrite)
# ─────────────────────────────────────────────────────────────────────────────
def fig_010_vs_10():
    W, H = 1000, 545
    f = []

    f.append(text(250, 44, "0.10: байти всередині буфера", size=16, bold=True))
    f.append(text(750, 44, "1.0: буфер посилається на пам'ять", size=16, bold=True))

    # ── ліва колонка ────────────────────────────────────────────────────────
    f.append(fitbox(50, 66, 400, 150,
                    "GstBuffer\n"
                    "data → байти, size\n"
                    "malloc_data, free_func\n"
                    "caps, timestamp, parent",
                    size=14))
    f.append(arrow(250, 220, 250, 262))
    f.append(fitbox(50, 266, 400, 100,
                    "GstXvImageBuffer, GstGLBuffer, …\n"
                    "окремий підклас на кожен тип пам'яті",
                    size=14))
    f.append(fitbox(50, 396, 400, 122,
                    "Один суцільний блок.\n"
                    "Один підклас — або той, або інший.\n"
                    "Суббуфер тримає батька вказівником.",
                    size=13))

    # ── права колонка ───────────────────────────────────────────────────────
    f.append(fitbox(550, 66, 400, 96,
                    "GstBuffer\n"
                    "PTS, DTS, тривалість, прапорці",
                    size=14))
    f.append(arrow(645, 166, 645, 262))
    f.append(arrow(855, 166, 855, 262))
    f.append(fitbox(550, 266, 190, 100,
                    "GstMemory × N\nсвій лічильник\nсвій алокатор",
                    size=13))
    f.append(fitbox(760, 266, 190, 100,
                    "GstMeta × N\nGstVideoMeta,\nобрізання, …",
                    size=13))
    f.append(fitbox(550, 396, 400, 122,
                    "Кілька окремих блоків.\n"
                    "Жодного підкласу — метадані складаються.\n"
                    "Алокатор підмінний: dmabuf, GL, драйвер.",
                    size=13))

    render(p('buffer-010-vs-10.svg'), W, H, *f,
           title="Що саме переписали між 0.10 і 1.0")


# ─────────────────────────────────────────────────────────────────────────────
# 6. Ланцюг викликів appsink: що повертає кожен і хто чим володіє
# ─────────────────────────────────────────────────────────────────────────────
def fig_pull_chain():
    W, H = 980, 590
    f = []

    LX, LW = 70, 400          # ліва колонка — виклики
    RX, RW = 520, 390         # права колонка — володіння

    rows = [
        (70, 70,
         "GstSample *s =\ngst_app_sink_pull_sample (sink)",
         "ВОЛОДІЄМО\nнаприкінці — gst_sample_unref (s)"),
        (180, 78,
         "GstBuffer *b = gst_sample_get_buffer (s)\n"
         "GstCaps   *c = gst_sample_get_caps (s)",
         "ПОЗИЧЕНІ\nживуть, поки живий s\nсвого unref не мають"),
        (298, 70,
         "gst_video_info_from_caps (&info, c)",
         "лише коли caps змінилися\nрозкладка з формату"),
        (408, 78,
         "gst_video_frame_map (&fr, &info, b,\n                     GST_MAP_READ)",
         "справжні кроки з GstVideoMeta\nкожна площина мапиться окремо"),
    ]

    for i, (y, h, left, right) in enumerate(rows):
        f.append(fitbox(LX, y, LW, h, left, size=14))
        f.append(fitbox(RX, y, RW, h, right, size=13, fill="#eef3f8"))
        if i + 1 < len(rows):
            ny = rows[i + 1][0]
            f.append(arrow(LX + LW / 2, y + h + 4, LX + LW / 2, ny - 6))

    f.append(fitbox(70, 516, 840, 54,
                    "Жодного байта кадру не переміщено: усі чотири виклики "
                    "передають тільки права й адреси.",
                    size=15, fill="#e8f4ec", stroke=FIELD))

    render(p('zero-copy-pull.svg'), W, H, *f,
           title="Один кадр з appsink: чотири виклики й чотири різні володіння")


# ─────────────────────────────────────────────────────────────────────────────
# 7. Вікно дійсності вказівника й що буває за ним
# ─────────────────────────────────────────────────────────────────────────────
def fig_pointer_lifetime():
    W, H = 1000, 500
    f = []

    X0, X1 = 250, 960

    # ── смуга 1: що робить ваш код ──────────────────────────────────────────
    f.append(text(24, 100, "Ваш код", size=14, bold=True, anchor="start"))
    segs = [
        (250, 145, "pull_sample", FILL),
        (395, 145, "frame_map", FILL),
        (540, 160, "обхід рядків", "#e8f4ec"),
        (700, 130, "frame_unmap", FILL),
        (830, 130, "sample_unref", FILL),
    ]
    for x, w, label, fill in segs:
        f.append(fitbox(x, 72, w, 56, label, size=13, fill=fill))

    # ── смуга 2: та сама пам'ять із пулу ────────────────────────────────────
    f.append(text(24, 210, "Пам'ять із пулу", size=14, bold=True, anchor="start"))
    f.append(fitbox(250, 182, 710, 56, "байти кадру N", size=14))
    f.append(fitbox(830, 182, 130, 56, "кадр N+1", size=13,
                    fill="#fdecea", stroke=POS))

    # межа повернення в пул
    f.append(line(830, 62, 830, 330, color=POS, sw=1.6, dash="6 5"))
    f.append(text(824, 52, "тут буфер лягає назад у пул", size=12,
                  color=POS, anchor="end"))

    # ── смуга 3: збережений вказівник ───────────────────────────────────────
    f.append(text(24, 300, "Збережений", size=14, bold=True, anchor="start"))
    f.append(text(24, 320, "вказівник", size=14, bold=True, anchor="start"))
    f.append(line(560, 292, 950, 292, color=POS, sw=2.2, dash="8 5"))
    f.append(arrow(940, 292, 962, 292, color=POS))
    f.append(text(560, 276, "адреса лишається дійсною — і після unmap, і після unref",
                  size=13, color=POS, anchor="start"))

    f.append(fitbox(60, 356, 900, 118,
                    "Дійсний вказівник ≠ ваші байти. Після unmap відображення знято, "
                    "після unref буфер повернувся в пул —\n"
                    "і наступний кадр декодер пише в ті самі адреси. "
                    "Читання не падає й нічого не повідомляє:\n"
                    "картинка просто «плутається» раз на кілька секунд, "
                    "і шукати це доводиться тижнями.",
                    size=14))

    render(p('pointer-lifetime.svg'), W, H, *f,
           title="Вікно, у якому вказівник на кадр справді ваш")


# ─────────────────────────────────────────────────────────────────────────────
# 6. Розкладка блоку GstMemory (до вставки api-buffer-memory)
# ─────────────────────────────────────────────────────────────────────────────
def fig_memory_layout():
    W, H = 980, 420
    f = []

    x0, x1 = 90, 890
    px = 210           # кінець префікса / початок видимих байтів
    pd = 770           # початок запасу

    # maxsize — подвійна стрілка над смугою
    f.append(text(490, 62, "maxsize — усе, що виділив алокатор", size=13, color=MUTED))
    f.append(arrow(490, 82, x0, 82))
    f.append(arrow(490, 82, x1, 82))

    # сама смуга
    f.append(rect(x0, 110, px - x0, 70, fill="#f7e6e6", stroke="#c9a2a2"))
    f.append(rect(px, 110, pd - px, 70, fill="#e8f4ec", stroke=FIELD))
    f.append(rect(pd, 110, x1 - pd, 70, fill="#f7e6e6", stroke="#c9a2a2"))

    f.append(text(150, 148, "prefix", size=14))
    f.append(text(150, 170, "ZERO_PREFIXED", size=10, color=MUTED))
    f.append(text(490, 148, "видимі байти кадру", size=15, bold=True))
    f.append(text(830, 148, "padding", size=14))
    f.append(text(830, 170, "ZERO_PADDED", size=10, color=MUTED))

    # проміри під смугою
    for a, b, label in ((x0, px, "offset"), (px, pd, "size"), (pd, x1, "padding")):
        mid = (a + b) / 2
        f.append(arrow(mid, 202, a, 202))
        f.append(arrow(mid, 202, b, 202))
        f.append(text(mid, 226, label, size=13, color=MUTED))

    f.append(fitbox(90, 252, 800, 66,
                    "gst_allocator_alloc (allocator, size, params)\n"
                    "виділено ≥ prefix + size + padding · адреса видимого початку кратна (align + 1)",
                    size=14))
    f.append(fitbox(90, 336, 800, 62,
                    "Після map: info.data — перший видимий байт,\n"
                    "info.size = size, info.maxsize = maxsize − offset",
                    size=13))

    render(p('memory-layout.svg'), W, H, *f,
           title="Що саме описують GstAllocationParams")


fig_buffer_memory()
fig_stride()
fig_allocation()
fig_map_domains()
fig_010_vs_10()
fig_pull_chain()
fig_pointer_lifetime()
fig_memory_layout()
print("ok")
