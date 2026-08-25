# -*- coding: utf-8 -*-
"""Фігури до теми «Апаратне декодування: VA-API, NVDEC, V4L2, MediaCodec»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Дві памʼяті й ціна переходу між ними ────────────────────────────────
def fig_memory_domains():
    W, H = 960, 505
    f = []

    # панелі
    f.append(rect(40, 80, 380, 400, fill="#ffffff"))
    f.append(rect(580, 80, 340, 400, fill="#ffffff"))
    f.append(text(230, 106, "Памʼять процесу", size=14, bold=True))
    f.append(text(750, 106, "Памʼять пристрою", size=14, bold=True))

    # ліворуч
    f.append(fitbox(120, 145, 220, 52, "Стиснений бітпотік\nH.264 / H.265", size=13))
    f.append(fitbox(105, 375, 250, 60, "Копія кадру в RAM\n187 МБ/с при 1080p60",
                    size=12, stroke=POS, color=POS))

    # праворуч
    f.append(fitbox(650, 145, 200, 52, "Рушій декодування\nфіксована логіка", size=13))
    f.append(fitbox(645, 265, 210, 58, "Пул поверхонь NV12\nтайлова розкладка", size=12))
    f.append(fitbox(650, 390, 200, 56, "Показ, GL, кодер\nу тій самій памʼяті",
                    size=12, stroke=FIELD, color=FIELD))

    # стрілки
    f.append(arrow(345, 171, 645, 171))
    f.append(mtext(500, 140, ["стиснений потік", "≈ 0.5 МБ/с"], size=11, color=MUTED))

    f.append(arrow(750, 202, 750, 262))
    f.append(text(848, 236, "записує кадр", size=11, color=MUTED))

    f.append(arrow(750, 328, 750, 386, color=FIELD))
    f.append(text(645, 360, "0 копій", size=11, color=FIELD))

    f.append(arrow(645, 305, 360, 390, color=POS))
    f.append(mtext(500, 292, ["мапування поверхні", "в памʼять процесу"], size=11, color=POS))

    render(os.path.join(IMG, 'memory-domains.svg'), W, H, *f,
           title="Де живе декодований кадр і що коштує перехід межі")


# ── 2. Ознака памʼяті в caps визначає ціну ─────────────────────────────────
def fig_caps_features():
    W, H = 1020, 525
    f = []

    f.append(text(80, 116, "Наступний елемент", size=12, color=MUTED, italic=True))
    f.append(text(80, 232, "Узгоджені caps", size=12, color=MUTED, italic=True))
    f.append(text(80, 357, "Що з кадром", size=12, color=MUTED, italic=True))
    f.append(text(80, 466, "Ціна за кадр", size=12, color=MUTED, italic=True))

    cols = [160, 445, 730]
    cw = 265
    centres = [x + cw / 2 for x in cols]

    row1 = ["vapostproc\nvah264enc",
            "waylandsink\nglimagesink",
            "videoconvert\nappsink → ваш код"]
    row2 = ["video/x-raw\n(memory:VAMemory)",
            "video/x-raw\n(memory:DMABuf)\ndrm-format=NV12:0x…",
            "video/x-raw\nformat=NV12\nбез ознаки памʼяті"]
    row3 = ["поверхня лишається\nу памʼяті пристрою",
            "передається дескриптор\nfd; імпорт без копії",
            "рушій мапує поверхню,\nпроцесор читає її"]
    row4 = ["0 МБ/с", "0 МБ/с", "187 МБ/с + затримка"]
    col4 = [FIELD, FIELD, POS]

    for i, x in enumerate(cols):
        f.append(fitbox(x, 85, cw, 62, row1[i], size=13, bold=True))
        f.append(fitbox(x, 195, cw, 74, row2[i], size=13))
        f.append(fitbox(x, 320, cw, 74, row3[i], size=12))
        f.append(fitbox(x, 440, cw, 52, row4[i], size=13,
                        stroke=col4[i], color=col4[i], bold=True))

    for cx in centres:
        f.append(arrow(cx, 147, cx, 193))
        f.append(arrow(cx, 269, cx, 318))
        f.append(arrow(cx, 394, cx, 438))

    render(os.path.join(IMG, 'caps-features.svg'), W, H, *f,
           title="Одна ознака памʼяті в caps вирішує, чи буде копія")


# ── 3. Порядок декодування проти порядку показу ────────────────────────────
def fig_decode_order():
    W, H = 780, 310
    f = []

    xs = [210, 280, 350, 420, 490, 560, 630]
    stream = ["I0", "P3", "B1", "B2", "P6", "B4", "B5"]
    shown = ["I0", "B1", "B2", "P3", "B4", "B5", "P6"]
    # A[i] показується на позиції mapping[i]
    mapping = [0, 3, 1, 2, 6, 4, 5]

    f.append(text(105, 106, "декодування", size=12, color=MUTED, italic=True))
    f.append(text(105, 231, "показ", size=12, color=MUTED, italic=True))

    for i, cx in enumerate(xs):
        hot = stream[i] == "P3"
        f.append(fitbox(cx - 29, 80, 58, 44, stream[i], size=14, bold=True,
                        stroke=POS if hot else LINE,
                        color=POS if hot else INK))
    for i, cx in enumerate(xs):
        hot = shown[i] == "P3"
        f.append(fitbox(cx - 29, 205, 58, 44, shown[i], size=14, bold=True,
                        stroke=POS if hot else LINE,
                        color=POS if hot else INK))

    for i, cx in enumerate(xs):
        tx = xs[mapping[i]]
        col = POS if stream[i] == "P3" else MUTED
        f.append(line(cx, 124, tx, 205, color=col, sw=1.4,
                      dash=None if col == POS else "4 3"))

    f.append(mtext(705, 152, ["утримання", "2 кадри"], size=11, color=POS))

    render(os.path.join(IMG, 'decode-order.svg'), W, H, *f,
           title="Порядок у потоці не збігається з порядком показу")


# ── 4. Три відповіді на одне питання (вставка hist) ────────────────────────
def fig_api_lineage():
    W, H = 1080, 420
    f = []

    lanes = [
        (58, "Розширення X-сервера: кадр показує X", [
            (40, 230, "XvMC · 2000\nлише MPEG-2, mo-comp та iDCT", None),
            (300, 240, "VDPAU · кінець 2008\nNVIDIA, драйвер серії 180", None),
            (570, 240, "XvBA · 2008\nAMD, SDK відкрито 2011", None),
        ]),
        (178, "Бібліотека чи служба від виробника заліза", [
            (40, 250, "VA-API · чорновик 2006,\nперший випуск 2008 (Intel)", None),
            (320, 250, "мости під VA-API · 2008–09\nvdpau-video, xvba-video", None),
            (600, 210, "NVDEC\nкадр у памʼяті CUDA", None),
            (840, 200, "MediaCodec · 2012\nдекодер в іншому процесі", None),
        ]),
        (298, "Ядро як спільний знаменник", [
            (40, 250, "V4L2 mem2mem · 2009–10\nдві черги буферів у драйвері", None),
            (320, 250, "DMA-BUF · Linux 3.3, 2012\nбуфер = файловий дескриптор", FIELD),
            (600, 270, "stateless V4L2 · Linux 4.20, 2018\nрозбір потоку — у програмі", None),
        ]),
    ]

    for y_title, title_s, boxes in lanes:
        f.append(text(40, y_title, title_s, size=13, bold=True,
                      anchor="start", color=MUTED))
        for x, w, s, col in boxes:
            kw = {}
            if col:
                kw = dict(stroke=col, color=col)
            f.append(fitbox(x, y_title + 14, w, 58, s, size=12, **kw))

    render(os.path.join(IMG, 'api-lineage.svg'), W, H, *f,
           title="Три різні відповіді на питання «як віддати кадр програмі»")


# ── 5. Дві черги V4L2 mem2mem і шлях буфера (вставка api) ──────────────────
def fig_m2m_queues():
    W, H = 1020, 450
    f = []

    f.append(fitbox(700, 130, 270, 200, "Апаратний рушій\nдекодування",
                    size=14, bold=True))

    # смуга OUTPUT
    f.append(fitbox(50, 95, 240, 74, "Стиснений вхід:\nодиниця доступу або зріз", size=13))
    f.append(arrow(292, 120, 408, 120))
    f.append(text(350, 105, "VIDIOC_QBUF", size=11, color=MUTED))
    f.append(arrow(408, 152, 292, 152))
    f.append(text(350, 176, "VIDIOC_DQBUF", size=11, color=MUTED))
    f.append(fitbox(410, 90, 190, 90, "черга OUTPUT\nпристрій ЧИТАЄ", size=13))
    f.append(text(505, 206, "V4L2_BUF_TYPE_VIDEO_OUTPUT", size=11, color=MUTED))
    f.append(arrow(602, 135, 698, 135))
    f.append(text(650, 120, "читає", size=11, color=MUTED))

    # смуга CAPTURE
    f.append(fitbox(50, 285, 240, 74, "Порожній буфер\nпід кадр", size=13))
    f.append(arrow(292, 310, 408, 310))
    f.append(text(350, 295, "VIDIOC_QBUF", size=11, color=MUTED))
    f.append(arrow(408, 342, 292, 342))
    f.append(text(350, 366, "VIDIOC_DQBUF", size=11, color=MUTED))
    f.append(fitbox(410, 280, 190, 90, "черга CAPTURE\nпристрій ПИШЕ", size=13))
    f.append(text(505, 396, "V4L2_BUF_TYPE_VIDEO_CAPTURE", size=11, color=MUTED))
    f.append(arrow(698, 325, 602, 325))
    f.append(text(650, 310, "пише", size=11, color=MUTED))

    f.append(text(510, 432,
                  "Черги рухаються незалежно: один поданий зріз ≠ один готовий кадр",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, 'm2m-queues.svg'), W, H, *f,
           title="Назви черг дано з погляду пристрою, а не програми")


# ── 6. Запит як пакет: контроли плюс буфер (вставка api) ────────────────────
def fig_stateless_request():
    W, H = 1000, 430
    f = []

    f.append(rect(50, 80, 470, 260, fill=BG, stroke=MUTED, sw=1.5))
    f.append(text(285, 106, "Запит — окремий дескриптор", size=13, bold=True))
    f.append(fitbox(75, 125, 420, 82,
                    "VIDIOC_S_EXT_CTRLS\nwhich = V4L2_CTRL_WHICH_REQUEST_VAL\n"
                    "SPS · PPS · DECODE_PARAMS · SLICE_PARAMS", size=12))
    f.append(fitbox(75, 232, 420, 82,
                    "VIDIOC_QBUF на OUTPUT\nflags |= V4L2_BUF_FLAG_REQUEST_FD\n"
                    "байти одного зрізу", size=12))

    f.append(arrow(522, 127, 578, 127))

    f.append(fitbox(580, 90, 380, 74,
                    "MEDIA_REQUEST_IOC_QUEUE\nядро вкладає контроли й пускає рушій", size=12))
    f.append(arrow(770, 166, 770, 196))
    f.append(fitbox(580, 198, 380, 74,
                    "poll(request_fd, POLLPRI)\nзапит виконано", size=12))
    f.append(arrow(770, 274, 770, 304))
    f.append(fitbox(580, 306, 380, 74,
                    "VIDIOC_DQBUF на CAPTURE\nкадр готовий", size=12,
                    stroke=FIELD, color=FIELD))

    f.append(text(500, 410,
                  "Далі MEDIA_REQUEST_IOC_REINIT — і той самий запит наповнюють знову",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, 'stateless-request.svg'), W, H, *f,
           title="Профіль stateless: параметри кадру їдуть у запиті разом із буфером")


if __name__ == '__main__':
    fig_memory_domains()
    fig_caps_features()
    fig_decode_order()
    fig_api_lineage()
    fig_m2m_queues()
    fig_stateless_request()
    print("ok")
