# -*- coding: utf-8 -*-
"""Фігури до теми «appsink і appsrc: міст між конвеєром і власним кодом»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def bridge():
    W, H = 1080, 300
    f = []
    # ланцюг: конвеєр → appsink → ваш код → appsrc → конвеєр
    f.append(fitbox(20, 118, 180, 64, "конвеєр:\nджерело, декодер"))
    f.append(arrow(202, 150, 232, 150))
    f.append(fitbox(240, 118, 140, 64, "appsink\n+ черга"))
    f.append(line(400, 58, 400, 250, color=MUTED, dash="6,5"))
    f.append(text(400, 48, "кадр стає вашим", size=12, color=MUTED))
    f.append(arrow(386, 150, 432, 150))
    f.append(fitbox(440, 110, 200, 80, "ваш код:\nчитає, змінює,\nвіддає"))
    f.append(line(660, 58, 660, 250, color=MUTED, dash="6,5"))
    f.append(text(660, 48, "кадр більше не ваш", size=12, color=MUTED))
    f.append(arrow(646, 150, 692, 150))
    f.append(fitbox(700, 118, 140, 64, "appsrc\n+ черга"))
    f.append(arrow(846, 150, 876, 150))
    f.append(fitbox(884, 118, 180, 64, "конвеєр:\nкодер, вихід"))
    # підписи меж
    f.append(text(310, 278, "межа: max-buffers, drop/leaky", size=12, color=MUTED))
    f.append(text(770, 278, "межа: max-bytes, block/leaky", size=12, color=MUTED))
    render(os.path.join(IMG, 'bridge.svg'), W, H, *f,
           title="Міст: дві черги й дві межі володіння")


def pull_push():
    W, H = 1000, 450
    f = []
    # ── панель «pull»
    f.append(rect(20, 60, 450, 360, fill=BG, stroke=MUTED, sw=1))
    f.append(text(245, 92, "pull — бере ваш потік", size=15, bold=True))
    f.append(fitbox(55, 115, 180, 50, "потік передавання"))
    f.append(arrow(145, 167, 145, 196))
    f.append(fitbox(55, 200, 180, 62, "черга в appsink\n(max-buffers)"))
    f.append(arrow(237, 231, 272, 231))
    f.append(fitbox(280, 200, 170, 62, "ваш потік:\npull_sample()"))
    f.append(mtext(245, 305, [
        "ваш потік чекає, поки кадру немає;",
        "конвеєр іде далі, поки черга не повна;",
        "ваш код нічого не гальмує напряму",
    ], size=12, color=MUTED))
    # ── панель «push»
    f.append(rect(510, 60, 450, 360, fill=BG, stroke=MUTED, sw=1))
    f.append(text(735, 92, "push — заходить конвеєр", size=15, bold=True))
    f.append(fitbox(545, 115, 180, 50, "потік передавання"))
    f.append(arrow(635, 167, 635, 196))
    f.append(fitbox(545, 200, 180, 62, "new_sample()\n— ВАШ код"))
    f.append(arrow(635, 264, 635, 293))
    f.append(fitbox(545, 297, 180, 50, "далі по конвеєру"))
    f.append(mtext(735, 378, [
        "поки ви працюєте — конвеєр стоїть;",
        "зайвого потоку й черги немає",
    ], size=12, color=MUTED))
    render(os.path.join(IMG, 'pull-push.svg'), W, H, *f,
           title="Дві дороги назовні")


def sample_stride():
    W, H = 1040, 420
    f = []
    # ── ліворуч: анатомія семпла
    f.append(rect(30, 70, 450, 320, fill=BG, stroke=MUTED, sw=1))
    f.append(text(255, 100, "GstSample", size=15, bold=True))
    f.append(fitbox(50, 118, 410, 78, "GstBuffer: PTS, DTS, тривалість,\nпрапорці, блоки пам'яті"))
    f.append(fitbox(50, 212, 410, 58, "GstCaps: video/x-raw, BGR, 640×480"))
    f.append(fitbox(50, 288, 410, 78, "GstSegment: як мітки часу\nпереводяться в час показу"))
    # ── праворуч: рядок у пам'яті
    f.append(text(765, 100, "рядок кадру в пам'яті", size=15, bold=True))
    f.append(rect(540, 120, 300, 46))
    f.append(rect(840, 120, 110, 46, fill="#e8ecf0"))
    f.append(text(690, 148, "640 × 3 = 1920 байтів", size=12))
    f.append(text(895, 148, "доповнення", size=12))
    f.append(rect(540, 176, 300, 46))
    f.append(rect(840, 176, 110, 46, fill="#e8ecf0"))
    f.append(text(690, 204, "наступний рядок", size=12))
    f.append(text(895, 204, "доповнення", size=12))
    f.append(line(540, 244, 540, 256))
    f.append(line(950, 244, 950, 256))
    f.append(line(540, 250, 950, 250))
    f.append(text(745, 272, "крок рядка = 1984 байти", size=12))
    f.append(mtext(765, 312, [
        "ширина × 3 ≠ довжина рядка;",
        "крок беруть із caps через GstVideoInfo",
    ], size=12, color=MUTED))
    render(os.path.join(IMG, 'sample-stride.svg'), W, H, *f,
           title="Що приходить у семплі й що лежить у пам'яті")


def backpressure():
    W, H = 1020, 390
    f = []
    f.append(fitbox(30, 110, 170, 64, "v4l2src\n(жива камера)"))
    f.append(arrow(202, 142, 232, 142))
    f.append(fitbox(240, 110, 120, 64, "queue"))
    f.append(arrow(362, 142, 392, 142))
    f.append(fitbox(400, 110, 170, 64, "appsink\nчерга повна"))
    f.append(arrow(572, 142, 610, 142))
    f.append(fitbox(618, 110, 180, 64, "ваш код\n(не встигає)"))
    f.append(arrow(398, 196, 198, 196, color=POS))
    f.append(text(298, 218, "протитиск іде вгору", size=12, color=POS))
    f.append(fitbox(30, 250, 300, 100,
                    "джерело — файл:\nчитання просто сповільнюється,\nнічого не втрачено"))
    f.append(fitbox(360, 250, 300, 100,
                    "джерело живе:\nкадри копляться в драйвері\nі губляться поза вашим кодом"))
    f.append(fitbox(690, 250, 300, 100,
                    "leaky-type / drop:\nappsink сам викидає кадр,\nконвеєр не зупиняється"))
    render(os.path.join(IMG, 'backpressure.svg'), W, H, *f,
           title="Переповнена черга приймача зупиняє конвеєр угору за течією")


def ownership():
    """Карта володіння: що стається з вашим посиланням на кожному виклику."""
    W, H = 1140, 512
    LX, LW = 30, 450          # ліва колонка — виклик
    RX, RW = 560, 550         # права колонка — доля вашого посилання
    f = []
    f.append(text(LX + LW / 2, 64, "виклик", size=14, bold=True, color=MUTED))
    f.append(text(RX + RW / 2, 64, "що стається з ВАШИМ посиланням",
                  size=14, bold=True, color=MUTED))

    rows = [
        ("gst_app_sink_pull_sample ()",
         "transfer full: семпл ВАШ —\ngst_sample_unref () обов'язковий", LINE),
        ("сигнал-дія pull-sample\n(шлях прив'язок до інших мов)",
         "теж transfer full: семпл звільнить\nзбирач сміття прив'язки", LINE),
        ("gst_app_src_push_buffer (buf)",
         "transfer full: буфер ЗАБРАЛИ —\nваш unref заборонений", POS),
        ("сигнал-дія push-buffer",
         "transfer none: узяли ЩЕ ОДНЕ посилання —\nваш unref лишається на вас", POS),
        ("gst_app_src_push_sample (s)",
         "transfer none: семпл лишається ВАШ", LINE),
    ]
    y = 84
    for left, right, col in rows:
        f.append(fitbox(LX, y, LW, 64, left, size=13))
        f.append(arrow(LX + LW + 12, y + 32, RX - 12, y + 32))
        f.append(fitbox(RX, y, RW, 64, right, size=13, stroke=col,
                        sw=2.0 if col is POS else 1.5))
        y += 78

    f.append(text(W / 2, 496,
                  "однакова назва — протилежне володіння: саме тут беруться "
                  "подвійне звільнення й витік",
                  size=13, color=MUTED))
    render(os.path.join(IMG, 'ownership.svg'), W, H, *f,
           title="Карта володіння на межі appsink / appsrc")


# ── фігури до вставки proj-frame-loop ──────────────────────────────────────

def copy_map():
    """Скільки байтів справді рухається на кожному кроці циклу."""
    W, H = 1010, 564
    f = []
    f.append(text(505, 40, "Один кадр 1280×720 BGR = 2 764 800 байтів",
                  size=15, bold=True))
    rows = [
        ("gst_video_frame_map () → cv::Mat поверх буфера", "0"),
        ("view.copyTo (dst) — у власний буфер", "запис 2.76 МБ"),
        ("cv::cvtColor (BGR → GRAY) в обробці", "запис 0.92 МБ"),
        ("рамка й напис поверх кадру", "запис ≈ 40 кБ"),
        ("gst_app_src_push_buffer ()", "0"),
        ("videoconvert: BGR → I420", "запис 1.38 МБ"),
        ("x264enc: I420 → H.264", "запис ≈ 17 кБ"),
    ]
    y0, rh = 66, 54
    f.append(rect(40, y0, 570, rh, fill="#eef1f4"))
    f.append(rect(610, y0, 360, rh, fill="#eef1f4"))
    f.append(text(58, y0 + 34, "крок у циклі", size=14, bold=True, anchor="start"))
    f.append(text(628, y0 + 34, "скільки байтів записано", size=14, bold=True,
                  anchor="start"))
    for i, (a, b) in enumerate(rows):
        y = y0 + rh * (i + 1)
        f.append(rect(40, y, 570, rh, fill=BG))
        f.append(rect(610, y, 360, rh, fill=BG))
        f.append(text(58, y + 34, a, size=13, anchor="start"))
        f.append(text(628, y + 34, b, size=13, anchor="start"))
    f.append(mtext(505, 530, [
        "разом ≈ 5.1 МБ запису на кадр, тобто 153 МБ/с при 30 к/с;",
        "видима в коді копія — трохи більш ніж половина",
    ], size=12, color=MUTED))
    render(os.path.join(IMG, 'copy-map.svg'), W, H, *f,
           title="Карта копій одного кадру")


def dangling_mat():
    """Чому незакопійований Mat не можна віддавати в інший потік."""
    W, H = 1030, 360
    f = []
    f.append(text(30, 78, "ваш цикл", size=13, bold=True, color=MUTED,
                  anchor="start"))
    f.append(fitbox(30, 88, 200, 58, "map (): Mat дивиться\nна пам'ять пулу"))
    f.append(fitbox(250, 88, 190, 58, "Mat кладеться\nв чергу"))
    f.append(fitbox(460, 88, 200, 58, "unref семпла:\nпам'ять у пул"))
    f.append(fitbox(700, 88, 300, 58,
                    "декодер бере той самий буфер\nі пише в нього новий кадр"))
    f.append(line(680, 70, 680, 300, color=POS, dash="6,5"))
    f.append(text(680, 60, "після цієї миті Mat недійсний", size=12, color=POS))
    f.append(text(30, 212, "потік обробки", size=13, bold=True, color=MUTED,
                  anchor="start"))
    f.append(fitbox(700, 225, 300, 58, "читає Mat — і бачить\nчужий, уже новий кадр"))
    f.append(arrow(350, 153, 350, 246))
    f.append(arrow(350, 250, 696, 250))
    f.append(text(505, 232, "Mat передано в інший потік", size=12, color=MUTED))
    f.append(mtext(505, 320, [
        "копія кадру коштує мілісекунди,",
        "читання чужої пам'яті не коштує нічого — і псує все",
    ], size=12, color=MUTED))
    render(os.path.join(IMG, 'dangling-mat.svg'), W, H, *f,
           title="Незакопійований Mat в іншому потоці")


if __name__ == '__main__':
    bridge()
    pull_push()
    sample_stride()
    backpressure()
    ownership()
    copy_map()
    dangling_mat()
    print("ok")
