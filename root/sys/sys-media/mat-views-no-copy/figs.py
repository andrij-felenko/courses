# -*- coding: utf-8 -*-
"""Фігури до теми «Види без копії: ROI і заголовок над чужим буфером»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

GREEN_FILL = "#e3f6ea"
GREY_FILL  = "#eef1f4"
RED_FILL   = "#fdecea"
BLUE_FILL  = "#eaf0fd"


# ─────────────────────────────────────────────────────────────────────────────
# 1. Вид як гребінець: рядки виду розділені рештою рядка батька
# ─────────────────────────────────────────────────────────────────────────────
def fig_comb():
    W, H = 1040, 560
    f = []

    x0, bw, bh = 190, 660, 34
    ys = [86 + i * 58 for i in range(5)]          # 86 144 202 260 318, низ 352
    band_x, band_w = x0 + 200, 210

    # підписи покажчиків над стосом
    f.append(text(x0 + 4, 64, "img.data", size=13, color=MUTED, anchor="start"))
    f.append(text(band_x, 64, "roi.data", size=13, color=FIELD, anchor="middle", bold=True))
    f.append(line(band_x, 70, band_x, ys[0], color=FIELD, sw=1.4))

    for i, y in enumerate(ys):
        f.append(rect(x0, y, bw, bh, fill=GREY_FILL, stroke=LINE, sw=1.2, rx=3))
        f.append(rect(band_x, y, band_w, bh, fill=GREEN_FILL, stroke=FIELD, sw=2, rx=3))
        f.append(text(x0 - 22, y + bh * 0.68, "рядок %d" % (100 + i),
                      size=13, color=MUTED, anchor="end"))

    # штрихова вертикаль по лівому краю смуги
    f.append(line(band_x, ys[0] + bh, band_x, ys[-1], color=FIELD, sw=1.2, dash="4,4"))

    # мірка кроку рядка
    ym = 388
    f.append(arrow(x0, ym, x0 + bw, ym, color=INK, sw=1.4))
    f.append(arrow(x0 + bw, ym, x0, ym, color=INK, sw=1.4))
    f.append(text(x0 + bw / 2, ym + 24, "step[0] = 5760 байтів — увесь рядок батька",
                  size=14, color=INK))

    # мірка корисної ширини
    ym2 = 446
    f.append(arrow(band_x, ym2, band_x + band_w, ym2, color=FIELD, sw=1.4))
    f.append(arrow(band_x + band_w, ym2, band_x, ym2, color=FIELD, sw=1.4))
    f.append(text(band_x + band_w / 2, ym2 + 24,
                  "cols · elemSize() = 192 байти — стільки бачить вид",
                  size=14, color=FIELD))

    note = fitbox(150, 490, 740, 52,
                  "Заголовок виду зберігає крок батька, тому його рядки в пам'яті НЕ суміжні:\n"
                  "між кінцем одного й початком наступного лежать 5568 чужих байтів.",
                  size=13, fill="#ffffff", stroke=MUTED, sw=1.2, color=INK)
    f.append(note)

    render(os.path.join(OUT, 'roi-comb.svg'), W, H, *f,
           title="ROI: той самий блок пікселів, інший заголовок")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Два роди виду: спільне володіння проти чужого буфера
# ─────────────────────────────────────────────────────────────────────────────
def fig_ownership():
    W, H = 1060, 540
    f = []

    f.append(line(530, 52, 530, 486, color=MUTED, sw=1.2, dash="6,5"))

    # ── ліворуч: вид над cv::Mat ──
    f.append(text(265, 70, "Вид над cv::Mat", size=15, bold=True, color=INK))

    f.append(fitbox(70, 96, 180, 62, "img\nu = блок A", size=13,
                    fill=BLUE_FILL, stroke=NEG, sw=1.6))
    f.append(fitbox(288, 96, 180, 62, "roi\nu = блок A", size=13,
                    fill=BLUE_FILL, stroke=NEG, sw=1.6))

    f.append(arrow(160, 158, 210, 236, color=NEG, sw=1.6))
    f.append(arrow(378, 158, 330, 236, color=NEG, sw=1.6))

    f.append(fitbox(90, 238, 350, 60, "блок A: пікселі + лічильник", size=13,
                    fill=GREY_FILL, stroke=LINE, sw=1.6))

    f.append(fitbox(90, 322, 350, 46, "refcount = 2", size=14,
                    fill="#ffffff", stroke=FIELD, sw=1.8, color=FIELD, bold=True))

    f.append(fitbox(70, 392, 390, 76,
                    "Блок живий, поки живий хоч один заголовок.\n"
                    "Помер img — roi далі законно тримає пікселі.\n"
                    "Останній заголовок звільняє пам'ять сам.",
                    size=13, fill="#ffffff", stroke=MUTED, sw=1.2))

    # ── праворуч: заголовок над чужим буфером ──
    f.append(text(795, 70, "Заголовок над чужим буфером", size=15, bold=True, color=INK))

    f.append(fitbox(700, 96, 190, 62, "view\nu = nullptr", size=13,
                    fill=RED_FILL, stroke=POS, sw=1.6))
    f.append(arrow(795, 158, 795, 236, color=POS, sw=1.6))

    f.append(fitbox(600, 238, 390, 60, "буфер конвеєра: лише пікселі", size=13,
                    fill=GREY_FILL, stroke=LINE, sw=1.6))

    f.append(fitbox(600, 322, 390, 46, "лічильника немає", size=14,
                    fill="#ffffff", stroke=POS, sw=1.8, color=POS, bold=True))

    f.append(fitbox(580, 392, 430, 76,
                    "Час життя цілком на власникові буфера.\n"
                    "Зняли відображення — заголовок висить у нікуди,\n"
                    "і Mat про це не дізнається й не попередить.",
                    size=13, fill="#ffffff", stroke=MUTED, sw=1.2))

    render(os.path.join(OUT, 'view-ownership.svg'), W, H, *f,
           title="Хто володіє пікселями: те саме на вигляд, різне за наслідками")


# ─────────────────────────────────────────────────────────────────────────────
# 3. create(): де ланцюг без копії тримається, а де тихо рветься
# ─────────────────────────────────────────────────────────────────────────────
def fig_create():
    W, H = 1040, 500
    f = []

    f.append(fitbox(360, 62, 320, 56,
                    "функція викликає dst.create(size, type)", size=13,
                    fill=GREY_FILL, stroke=LINE, sw=1.6))

    f.append(fitbox(320, 148, 400, 58,
                    "розмір і тип уже такі, як треба?", size=14,
                    fill="#ffffff", stroke=INK, sw=1.8, bold=True))

    f.append(arrow(520, 118, 520, 146, color=LINE, sw=1.6))

    # ліва гілка — так
    f.append(arrow(320, 177, 230, 177, color=FIELD, sw=1.6))
    f.append(text(272, 166, "так", size=13, color=FIELD, bold=True))
    f.append(arrow(230, 177, 230, 236, color=FIELD, sw=1.6))
    f.append(fitbox(60, 238, 340, 66,
                    "create() нічого не робить:\nбуфер лишається тим самим", size=13,
                    fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    f.append(arrow(230, 304, 230, 348, color=FIELD, sw=1.6))
    f.append(fitbox(60, 350, 340, 66,
                    "результат лягає ПРЯМО в пікселі батька\n— саме цього ми й хотіли", size=13,
                    fill="#ffffff", stroke=FIELD, sw=1.6, color=FIELD))

    # права гілка — ні
    f.append(arrow(720, 177, 812, 177, color=POS, sw=1.6))
    f.append(text(768, 166, "ні", size=13, color=POS, bold=True))
    f.append(arrow(812, 177, 812, 236, color=POS, sw=1.6))
    f.append(fitbox(640, 238, 340, 66,
                    "create() виділяє новий блок\nі перечіпляє на нього заголовок", size=13,
                    fill=RED_FILL, stroke=POS, sw=1.8))
    f.append(arrow(812, 304, 812, 348, color=POS, sw=1.6))
    f.append(fitbox(640, 350, 340, 66,
                    "у батька не потрапляє нічого,\nа помилки ніхто не показав", size=13,
                    fill="#ffffff", stroke=POS, sw=1.6, color=POS))

    f.append(fitbox(230, 440, 580, 40,
                    "Мовчазна різниця: канал, глибина чи один зайвий піксель — і гілка інша.",
                    size=13, fill="#ffffff", stroke=MUTED, sw=1.2))

    render(os.path.join(OUT, 'create-branch.svg'), W, H, *f,
           title="Запис у ROI: коли він доходить до батька")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Історична вставка: ROI як стан зображення (IplImage) проти ROI як значення
# ─────────────────────────────────────────────────────────────────────────────
def fig_state_vs_value():
    W, H = 1100, 600
    f = []

    f.append(text(280, 44, "IplImage: ділянка — поле в зображенні",
                  size=15, color=POS, bold=True))
    f.append(text(820, 44, "cv::Mat: ділянка — окреме значення",
                  size=15, color=FIELD, bold=True))
    f.append(line(550, 62, 550, 540, color=MUTED, sw=1.2, dash="6,6"))

    # ── ліворуч: одне зображення, одне поле roi ──────────────────────────────
    f.append(rect(120, 80, 320, 150, fill=RED_FILL, stroke=POS, sw=2))
    f.append(mtext(140, 108, ["IplImage", "width, height", "widthStep",
                              "imageData →", "roi →"],
                   size=13, color=INK, anchor="start", lh=1.35))
    f.append(rect(120, 268, 320, 106, fill="#ffffff", stroke=POS, sw=1.6))
    f.append(mtext(140, 296, ["IplROI", "xOffset, yOffset", "width, height, coi"],
                   size=13, color=INK, anchor="start", lh=1.35))
    f.append(arrow(300, 232, 300, 266, color=POS, sw=1.6))

    f.append(fitbox(80, 408, 400, 60,
                    "cvSetImageROI(img, rect) міняє САМЕ зображення:\n"
                    "усі, хто тримає img, дістають нову ділянку",
                    size=13, fill="#ffffff", stroke=POS, sw=1.6, color=POS))
    f.append(fitbox(80, 486, 400, 52,
                    "друга ділянка одночасно — неможлива;\n"
                    "забутий cvResetImageROI — тиха помилка",
                    size=13, fill="#ffffff", stroke=MUTED, sw=1.2, color=MUTED))

    # ── праворуч: три заголовки над одним блоком ────────────────────────────
    hx = [600, 748, 896]
    for i, x in enumerate(hx):
        f.append(rect(x, 84, 128, 96, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
        f.append(mtext(x + 64, 110, ["вид %s" % "ABC"[i], "rows, cols",
                                     "data, step"],
                       size=12, color=INK, lh=1.35))
        f.append(arrow(x + 64, 182, x + 64, 252, color=FIELD, sw=1.6))

    f.append(rect(600, 256, 424, 92, fill=GREY_FILL, stroke=LINE, sw=1.8))
    f.append(mtext(812, 292, ["один блок пікселів",
                              "лічильник посилань = 3"], size=13, color=INK, lh=1.35))

    f.append(fitbox(600, 408, 424, 60,
                    "frame(Rect(...)) повертає НОВЕ значення;\n"
                    "сам frame не змінюється й нічого не «вмикає»",
                    size=13, fill="#ffffff", stroke=FIELD, sw=1.6, color=FIELD))
    f.append(fitbox(600, 486, 424, 52,
                    "видів може бути скільки завгодно;\n"
                    "останній, хто пішов, звільняє блок",
                    size=13, fill="#ffffff", stroke=MUTED, sw=1.2, color=MUTED))

    render(os.path.join(OUT, 'roi-state-vs-value.svg'), W, H, *f,
           title="ROI як стан зображення проти ROI як окремого значення")


# ─────────────────────────────────────────────────────────────────────────────
# 5. Проєктна вставка: п'ять чисел кадру GStreamer → аргументи cv::Mat
# ─────────────────────────────────────────────────────────────────────────────
def fig_gst_mat_bridge():
    W, H = 1120, 520
    f = []

    f.append(text(300, 68, "GstVideoFrame після map", size=15, bold=True, color=INK))
    f.append(text(875, 68, "cv::Mat над чужим буфером", size=15, bold=True, color=INK))

    rows = [
        ("GST_VIDEO_FRAME_HEIGHT(&f)",          "rows",            False),
        ("GST_VIDEO_FRAME_WIDTH(&f)",           "cols",            False),
        ("формат із caps: BGR",                 "type = CV_8UC3",  False),
        ("GST_VIDEO_FRAME_PLANE_DATA(&f, 0)",   "data",            False),
        ("GST_VIDEO_FRAME_PLANE_STRIDE(&f, 0)", "step[0]",         True),
    ]

    for i, (lhs, rhs, hot) in enumerate(rows):
        y = 92 + i * 66
        col = FIELD if hot else LINE
        fill = GREEN_FILL if hot else GREY_FILL
        f.append(fitbox(70, y, 460, 50, lhs, size=14,
                        fill=fill, stroke=col, sw=1.8 if hot else 1.4))
        f.append(arrow(540, y + 25, 692, y + 25, color=col, sw=1.6))
        f.append(fitbox(700, y, 350, 50, rhs, size=14,
                        fill="#ffffff", stroke=col, sw=1.8 if hot else 1.4,
                        color=FIELD if hot else INK, bold=hot))

    f.append(fitbox(70, 424, 460, 58,
                    "Усі п'ять чисел дійсні лише між map і unmap.",
                    size=13, fill="#ffffff", stroke=MUTED, sw=1.2, color=MUTED))
    f.append(fitbox(700, 424, 350, 58,
                    "✗ cols · elemSize()\nкрок звідси брати НЕ можна",
                    size=13, fill=RED_FILL, stroke=POS, sw=1.8, color=POS))
    f.append(arrow(875, 422, 875, 404, color=POS, sw=1.6))

    render(os.path.join(OUT, 'gst-mat-bridge.svg'), W, H, *f,
           title="Стик: звідки береться кожен аргумент конструктора")


# ─────────────────────────────────────────────────────────────────────────────
# 6. Проєктна вставка: смуга, у якій заголовок над буфером конвеєра чинний
# ─────────────────────────────────────────────────────────────────────────────
def fig_map_window():
    W, H = 1120, 600
    f = []

    steps = [
        "sample = gst_app_sink_pull_sample()",
        "buf = gst_buffer_ref(буфер із sample)",
        "gst_sample_unref(sample)",
        "buf = gst_buffer_make_writable(buf)",
        "gst_video_frame_map(READ | WRITE)",
        "cv::Mat над площиною — і вся робота",
        "gst_video_frame_unmap()",
        "gst_app_src_push_buffer(buf)",
    ]
    ys = [76 + i * 54 for i in range(8)]           # 76 … 454, низ 498

    for i, s in enumerate(steps):
        hot = i in (4, 5, 6)
        f.append(fitbox(70, ys[i], 430, 44, s, size=13,
                        fill=GREEN_FILL if hot else GREY_FILL,
                        stroke=FIELD if hot else LINE, sw=1.6 if hot else 1.2))

    # смуга «буфер наш» — від власного посилання до передавання володіння
    f.append(text(605, 66, "буфер наш", size=13, color=NEG, bold=True))
    f.append(rect(540, ys[1], 130, ys[7] + 44 - ys[1], fill=BLUE_FILL,
                  stroke=NEG, sw=1.6))

    # смуга дійсності пікселів і те, що починається за нею
    f.append(text(765, 66, "пікселі чинні", size=13, color=FIELD, bold=True))
    f.append(rect(690, ys[4], 150, ys[6] + 44 - ys[4], fill=GREEN_FILL,
                  stroke=FIELD, sw=1.8))
    f.append(fitbox(690, ys[7] - 4, 150, 48, "чужа пам'ять",
                    size=13, fill=RED_FILL, stroke=POS, sw=1.8, color=POS))

    f.append(fitbox(870, 190, 210, 150,
                    "Заголовок, збережений\nу члені класу, виходить\nза нижній край зеленої\n"
                    "смуги — і показує вже\nінший кадр із того\nсамого пулу.",
                    size=13, fill="#ffffff", stroke=POS, sw=1.6, color=POS))
    f.append(arrow(868, 460, 846, 460, color=POS, sw=1.6))

    f.append(fitbox(70, 520, 770, 56,
                    "Порядок не декоративний: доки живий sample, у буфера два власники — і запис у нього\n"
                    "коштуватиме копії; після unmap адреса лишається дійсною, а байти за нею вже чужі.",
                    size=13, fill="#ffffff", stroke=MUTED, sw=1.2))

    render(os.path.join(OUT, 'map-window.svg'), W, H, *f,
           title="Вікно, у якому заголовок над буфером конвеєра має сенс")


# ─────────────────────────────────────────────────────────────────────────────
# 7. Проєктна вставка: NV12 — два заголовки на один кадр
# ─────────────────────────────────────────────────────────────────────────────
def fig_nv12_headers():
    W, H = 1100, 520
    f = []

    # площина Y
    f.append(rect(70, 110, 340, 150, fill=GREY_FILL, stroke=LINE, sw=1.4))
    f.append(fitbox(70, 110, 280, 150, "площина 0 — яскравість Y\nh рядків по w байтів",
                    size=13, fill=GREEN_FILL, stroke=FIELD, sw=1.8))

    # площина UV
    f.append(rect(70, 290, 340, 90, fill=GREY_FILL, stroke=LINE, sw=1.4))
    f.append(fitbox(70, 290, 280, 90, "площина 1 — U та V поруч\nh/2 рядків по w байтів",
                    size=13, fill=BLUE_FILL, stroke=NEG, sw=1.8))

    f.append(arrow(414, 185, 616, 175, color=FIELD, sw=1.6))
    f.append(arrow(414, 335, 616, 345, color=NEG, sw=1.6))

    f.append(fitbox(620, 130, 430, 90,
                    "cv::Mat y(h, w, CV_8UC1,\n"
                    "  PLANE_DATA(&f, 0), PLANE_STRIDE(&f, 0));",
                    size=13, fill="#ffffff", stroke=FIELD, sw=1.8))
    f.append(fitbox(620, 300, 430, 90,
                    "cv::Mat uv(h/2, w/2, CV_8UC2,\n"
                    "  PLANE_DATA(&f, 1), PLANE_STRIDE(&f, 1));",
                    size=13, fill="#ffffff", stroke=NEG, sw=1.8))

    f.append(fitbox(70, 424, 980, 62,
                    "Сірим — запас до вирівнювання: він сидить у кроці й не входить у ширину.\n"
                    "У кожної площини свій крок, а часом і свій блок пам'яті — тому заголовків два.",
                    size=13, fill="#ffffff", stroke=MUTED, sw=1.2))

    render(os.path.join(OUT, 'nv12-headers.svg'), W, H, *f,
           title="NV12: один кадр, дві площини, два заголовки")


# ─────────────────────────────────────────────────────────────────────────────
# 8. Довідка з API: розкладка 32 бітів поля flags
# ─────────────────────────────────────────────────────────────────────────────
def fig_flags_bits():
    W, H = 1080, 440
    f = []

    x0, y0, hh = 90, 96, 58
    segs = [
        ("31…16", "MAGIC_VAL = 0x42FF", 300, GREY_FILL, LINE),
        ("15",    "SUB",                 90, RED_FILL,   POS),
        ("14",    "CONT",                90, GREEN_FILL, FIELD),
        ("13…12", "—",                   70, "#ffffff",  MUTED),
        ("11…3",  "канали − 1",         220, BLUE_FILL,  NEG),
        ("2…0",   "глибина",            130, BLUE_FILL,  NEG),
    ]

    x = x0
    for bits, name, w, fill, stroke in segs:
        f.append(fitbox(x, y0, w, hh, name, size=14, fill=fill, stroke=stroke, sw=1.6, rx=3))
        f.append(text(x + w / 2.0, y0 - 12, bits, size=12, color=MUTED))
        x += w

    yb = y0 + hh + 14                       # дужка під бітами 11…0 — це дістає type()
    f.append(line(640, yb, 990, yb, color=NEG, sw=1.4))
    f.append(line(640, yb - 6, 640, yb + 6, color=NEG, sw=1.4))
    f.append(line(990, yb - 6, 990, yb + 6, color=NEG, sw=1.4))
    f.append(text(815, yb + 26, "TYPE_MASK = 0x00000FFF → type()", size=13, color=NEG))

    legend = [
        (GREY_FILL,  LINE,  "біти 31…16 — MAGIC_VAL = 0x42FF: підпис «це заголовок Mat»"),
        (RED_FILL,   POS,   "біт 15 — SUBMATRIX_FLAG: заголовок вужчий чи нижчий за батька → isSubmatrix()"),
        (GREEN_FILL, FIELD, "біт 14 — CONTINUOUS_FLAG: у рядках немає розривів → isContinuous()"),
        ("#ffffff",  MUTED, "біти 13…12 — не використані"),
        (BLUE_FILL,  NEG,   "біти 11…3 — канали мінус один (CV_CN_SHIFT = 3) → channels()"),
        (BLUE_FILL,  NEG,   "біти 2…0 — глибина, 0…7 (CV_MAT_DEPTH_MASK = 7) → depth()"),
    ]
    for i, (fill, stroke, s) in enumerate(legend):
        yy = 236 + i * 34
        f.append(rect(90, yy - 11, 15, 15, fill=fill, stroke=stroke, sw=1.4, rx=2))
        f.append(text(118, yy, s, size=13, color=INK, anchor="start"))

    render(os.path.join(OUT, 'api-flags-bits.svg'), W, H, *f,
           title="flags: 32 біти, у яких лежить усе про заголовок (OpenCV 4.x)")


# ─────────────────────────────────────────────────────────────────────────────
# 9. Довідка з API: чотири покажчики заголовка над одним блоком
# ─────────────────────────────────────────────────────────────────────────────
def fig_data_pointers():
    W, H = 1080, 470
    f = []

    ys = [96 + i * 44 for i in range(6)]
    roi_rows = (1, 2, 3)

    for i, y in enumerate(ys):
        f.append(rect(210, y, 220, 38, fill=GREY_FILL, stroke=LINE, sw=1.0, rx=2))
        if i in roi_rows:
            f.append(rect(430, y, 200, 38, fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=2))
        else:
            f.append(rect(430, y, 200, 38, fill=GREY_FILL, stroke=LINE, sw=1.0, rx=2))
        f.append(rect(630, y, 200, 38, fill=GREY_FILL, stroke=LINE, sw=1.0, rx=2))
        f.append(rect(830, y, 90, 38, fill="#ffffff", stroke=MUTED, sw=1.0, rx=2))

    f.append(text(118, 101, "datastart", size=13, color=NEG, anchor="start"))
    f.append(arrow(192, 97, 207, 97, color=NEG, sw=1.5))

    f.append(text(430, 74, "data — початок виду", size=13, color=FIELD, bold=True))
    f.append(arrow(430, 80, 430, 136, color=FIELD, sw=1.5))

    f.append(arrow(830, 390, 830, 358, color=POS, sw=1.5))
    f.append(text(830, 406, "dataend", size=13, color=POS))

    f.append(arrow(920, 424, 920, 358, color=MUTED, sw=1.5))
    f.append(text(920, 440, "datalimit", size=13, color=MUTED))

    legend = [
        (GREEN_FILL, FIELD, "вид: cols·elemSize() корисних байтів, далі стрибок на step[0]"),
        (GREY_FILL,  LINE,  "корисні байти рядка батька"),
        ("#ffffff",  MUTED, "хвіст рядка до step[0] — байти доповнення"),
    ]
    for i, (fill, stroke, s) in enumerate(legend):
        yy = 372 + i * 32
        f.append(rect(120, yy - 11, 15, 15, fill=fill, stroke=stroke, sw=1.4, rx=2))
        f.append(text(146, yy, s, size=13, color=INK, anchor="start"))

    render(os.path.join(OUT, 'api-data-pointers.svg'), W, H, *f,
           title="Чотири покажчики заголовка: вид успадковує межі батька")


fig_comb()
fig_ownership()
fig_create()
fig_state_vs_value()
fig_gst_mat_bridge()
fig_map_window()
fig_nv12_headers()
fig_flags_bits()
fig_data_pointers()
print("ok")
