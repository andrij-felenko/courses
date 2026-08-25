# -*- coding: utf-8 -*-
"""Фігури до теми «Будова OpenCV: модулі, версії, як її збирають»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def row(x0, width, n, y, h, names, size=13, gap=12, fill=FILL, stroke=LINE, bold=False):
    """Рівномірний ряд із n рамок у смузі [x0, x0+width]."""
    w = (width - gap * (n - 1)) / float(n)
    out = ''
    for i, s in enumerate(names):
        out += fitbox(x0 + i * (w + gap), y, w, h, s, size=size,
                      fill=fill, stroke=stroke, bold=bold)
    return out


# ── 1. Шари модулів ────────────────────────────────────────────────────────
def fig_layers():
    W, H = 940, 600
    X0, BW = 50, 560          # смуга рамок головного репозиторію
    f = []

    f.append(row(X0 + 130, 300, 1, 60, 46, ['stitching'], size=13))
    f.append(row(X0, BW, 3, 130, 46, ['dnn', 'objdetect', 'photo'], size=13))
    f.append(row(X0, BW, 3, 200, 46, ['features2d', 'calib3d', 'video'], size=13))
    f.append(row(X0, BW, 5, 270, 46,
                 ['imgproc', 'imgcodecs', 'videoio', 'highgui', 'flann'], size=12))
    f.append(fitbox(X0, 350, BW, 58, 'core — cv::Mat, алокатор, паралелізм, HAL',
                    size=15, fill='#eaf4ec', stroke=FIELD, bold=True))

    # стрілка «залежить від» у власному коридорі
    f.append(text(645, 55, 'залежить', size=12, color=MUTED))
    f.append(text(645, 71, 'від', size=12, color=MUTED))
    f.append(arrow(645, 84, 645, 344))

    # contrib
    f.append(rect(690, 50, 210, 358, fill='#ffffff', stroke=MUTED, sw=1.5))
    f.append(mtext(795, 76, ['opencv_contrib', '(окремий репозиторій)'],
                   size=12, color=MUTED, bold=True))
    f.append(row(706, 178, 1, 110, 40, ['cudaimgproc'], size=12))
    f.append(row(706, 178, 1, 162, 40, ['aruco'], size=12))
    f.append(row(706, 178, 1, 214, 40, ['ximgproc'], size=12))
    f.append(row(706, 178, 1, 266, 40, ['xfeatures2d'], size=12))
    f.append(mtext(795, 340, ['теж спираються', 'на core'], size=11, color=MUTED))

    f.append(fitbox(50, 440, 850, 52,
                    'Стрілки йдуть лише вниз: core не знає про жоден модуль над собою, '
                    'циклів у графі немає', size=13, fill='#ffffff', stroke=MUTED))
    f.append(mtext(475, 528,
                   ['Набір модулів — станом на гілку 4.x. У 5.0 calib3d розділено на',
                    'geometry, calib і stereo, features2d перейменовано на features,',
                    'а ml і gapi переїхали в opencv_contrib.'],
                   size=12, color=MUTED))

    render(os.path.join(OUT, 'module-layers.svg'), W, H, *f,
           title='Модулі OpenCV: шари над одним типом даних')


# ── 2. Конфігурація вирішує, що вміє бінарник ──────────────────────────────
def fig_config():
    W, H = 980, 620
    f = []

    # джерела
    f.append(fitbox(40, 90, 210, 50, 'джерела opencv', size=13, bold=True))
    f.append(fitbox(40, 155, 210, 50, 'джерела opencv_contrib', size=12))
    f.append(mtext(145, 235, ['те саме дерево', 'у всіх'], size=11, color=MUTED))

    f.append(arrow(258, 130, 316, 130))

    # конфігурація
    f.append(rect(324, 62, 300, 232, fill=FILL, stroke=LINE, sw=1.5))
    f.append(text(474, 86, 'крок конфігурації', size=13, bold=True))
    f.append(mtext(474, 116,
                   ['BUILD_LIST=core,imgproc,videoio',
                    'OPENCV_EXTRA_MODULES_PATH=...',
                    'WITH_FFMPEG=ON',
                    'WITH_GSTREAMER=OFF',
                    'CPU_DISPATCH=AVX2,AVX512_SKX',
                    'BUILD_SHARED_LIBS=ON'],
                   size=12, lh=1.55))
    f.append(mtext(474, 322, ['звіт конфігурації —', 'єдина правда про бінарник'],
                   size=11, color=MUTED))

    f.append(arrow(632, 130, 690, 130))

    # артефакти
    f.append(fitbox(698, 62, 250, 44, 'libopencv_core.so.413', size=12))
    f.append(fitbox(698, 116, 250, 44, 'заголовки opencv2/', size=12))
    f.append(fitbox(698, 170, 250, 44, 'OpenCVConfig.cmake', size=12))
    f.append(fitbox(698, 224, 250, 52, 'libopencv_videoio_ffmpeg.so\n(плагін, якщо замовлено)', size=11))

    # той самий виклик — два результати
    f.append(line(40, 380, 940, 380, color=MUTED, sw=1, dash='6 5'))
    f.append(fitbox(40, 410, 330, 60, 'той самий рядок у вашому коді:\nVideoCapture("rtsp://cam/live")',
                    size=12, bold=True))
    f.append(arrow(378, 428, 448, 402))
    f.append(arrow(378, 452, 448, 494))
    f.append(fitbox(456, 372, 484, 58, 'збірка з FFmpeg: потік відкрито,\nкадр у cv::Mat',
                    size=12, fill='#eaf4ec', stroke=FIELD))
    f.append(fitbox(456, 466, 484, 58, 'збірка без нього: isOpened() == false,\nжодного повідомлення',
                    size=12, fill='#fdecea', stroke=POS))

    f.append(mtext(490, 566,
                   ['Номер версії однаковий в обох випадках — він не описує',
                    'ані набір модулів, ані набір бекендів вводу-виводу.'],
                   size=12, color=MUTED))

    render(os.path.join(OUT, 'build-config.svg'), W, H, *f,
           title='Що саме вирішує конфігурація збірки')


# ── 3. Дві OpenCV в одному процесі ─────────────────────────────────────────
def fig_two_abis():
    W, H = 980, 520
    f = []

    f.append(rect(30, 52, 920, 372, fill='#ffffff', stroke=MUTED, sw=1.5))
    f.append(text(95, 74, 'один процес', size=12, color=MUTED, italic=True))

    # ліва колонка
    f.append(fitbox(55, 92, 250, 48, 'ваш застосунок', size=13, bold=True))
    f.append(arrow(180, 142, 180, 182))
    f.append(fitbox(55, 188, 250, 48, 'libopencv_core.so.413', size=12))
    f.append(fitbox(55, 258, 250, 62, 'алокатор і розкладка\ncv::Mat версії 4.13', size=12))

    # права колонка
    f.append(fitbox(640, 92, 270, 48, 'сторонній плагін', size=13, bold=True))
    f.append(arrow(775, 142, 775, 182))
    f.append(fitbox(640, 188, 270, 48, 'libopencv_core.so.412', size=12))
    f.append(fitbox(640, 258, 270, 62, 'інший алокатор,\nінша розкладка cv::Mat', size=12))

    # передача кадру
    f.append(arrow(312, 112, 632, 112))
    f.append(fitbox(330, 132, 288, 44, 'кадр cv::Mat передано в плагін', size=12,
                    fill='#ffffff', stroke=MUTED))

    # місце поломки
    f.append(fitbox(330, 200, 288, 120,
                    'деструктор Mat спрацював\nу чужій версії:\nчужий лічильник посилань,\nчужий free()',
                    size=12, fill='#fdecea', stroke=POS))

    f.append(fitbox(55, 344, 855, 56,
                    'SONAME різні (413 і 412) — завантажувач тримає обидві бібліотеки; '
                    'імена символів не конфліктують, а розкладка даних — так',
                    size=12, fill='#ffffff', stroke=MUTED))

    f.append(mtext(490, 466,
                   ['Аварія стається не там, де причина: пам\'ять уже зіпсовано,',
                    'а падіння покаже стек зовсім іншого виклику.'],
                   size=12, color=MUTED))

    render(os.path.join(OUT, 'two-abis.svg'), W, H, *f,
           title='Дві збірки OpenCV в одному процесі')


# ── 4. Хто опікувався бібліотекою (вставка hist-opencv-origin) ─────────────
def fig_stewards():
    W = 960
    ROWS = [
        # (рік, подія, опікун)
        ('1999',      'Intel відкриває проєкт: вільна бібліотека зору, щоб було чим', 0),
        ('',          'навантажити процесор (ініціатива Гарі Бредскі)', 0),
        ('2000',      'Перша публічна альфа — на конференції CVPR', 0),
        ('2001-2005', "П'ять бет; бібліотека живе як внутрішня ініціатива", 0),
        ('2006',      'Реліз 1.0: інтерфейс мовою C, IplImage', 0),
        ('2008',      'Опіка переходить до Willow Garage (робототехніка)', 1),
        ('2009',      "Реліз 2.0: з'являється cv::Mat і лічильник посилань", 1),
        ('2012',      'Серпень: некомерційний фонд OpenCV.org; щоденну', 2),
        ('',          'розробку веде Itseez', 2),
        ('2013',      'Вересень: заведено окремий репозиторій opencv_contrib', 2),
        ('2015',      'Червень: реліз 3.0 — contrib окремо, UMat', 2),
        ('2016',      'Травень: Intel купує Itseez', 3),
        ('2020',      'Жовтень: 4.5.0 виходить під ліцензією Apache 2', 3),
    ]
    TINT = ['#eef2f7', '#f3eef7', '#eaf4ec', '#fdf1e7']
    TOP, STEP, BH = 56, 44, 34
    H = TOP + STEP * len(ROWS) + 74
    AX = 178                      # вісь часу
    f = []

    f.append(line(AX, TOP - 18, AX, TOP + STEP * (len(ROWS) - 1) + 20,
                  color=MUTED, sw=2))
    for i, (year, what, who) in enumerate(ROWS):
        y = TOP + i * STEP
        if year:
            f.append(circle(AX, y + BH / 2, 6, fill=BG, stroke=LINE, sw=2))
            f.append(text(AX - 22, y + BH / 2 + 5, year, size=13,
                          anchor='end', bold=True))
        f.append(fitbox(AX + 24, y, W - AX - 64, BH, what, size=13,
                        fill=TINT[who], stroke=MUTED))

    legend = ['Заливка = хто опікувався: Intel (1999-2008), Willow Garage (2008-2012),',
              'фонд OpenCV.org разом з Itseez (2012-2016), Intel знову як власник Itseez (з 2016).']
    f.append(mtext(W / 2, H - 46, legend, size=12, color=MUTED))

    render(os.path.join(OUT, 'stewards-timeline.svg'), W, H, *f,
           title='Хто опікувався OpenCV: чверть століття зміни рук')


# ── 5. Життя одного параметра: WITH_FFMPEG ─────────────────────────────────
def fig_option_life():
    W, H = 1020, 500
    GREEN, RED = '#eaf4ec', '#fdecea'
    f = []

    # те, що задає людина
    f.append(fitbox(40, 150, 240, 58, 'cmake -DWITH_FFMPEG=ON', size=13, bold=True))
    f.append(arrow(160, 212, 160, 240))
    f.append(fitbox(40, 244, 240, 88,
                    'розвідка: pkg-config шукає\nlibavcodec, libavformat,\nlibavutil, libswscale',
                    size=11))
    f.append(mtext(160, 362, ['крок конфігурації минає',
                              'без помилки в обох гілках'], size=11, color=MUTED))

    f.append(arrow(288, 266, 342, 152))
    f.append(arrow(288, 302, 342, 342))

    # гілка «знайдено»
    f.append(fitbox(350, 100, 200, 76, 'знайдено:\nHAVE_FFMPEG в означеннях videoio',
                    size=11, fill=GREEN, stroke=FIELD))
    f.append(arrow(558, 138, 582, 138))
    f.append(fitbox(590, 100, 200, 76, 'у звіті:\nFFMPEG: YES\navcodec: YES (60.31.102)',
                    size=11, fill=GREEN, stroke=FIELD))
    f.append(arrow(798, 138, 822, 138))
    f.append(fitbox(830, 100, 180, 76, 'CAP_FFMPEG у реєстрі,\ncap.isOpened() == true',
                    size=11, fill=GREEN, stroke=FIELD))

    # гілка «не знайдено»
    f.append(fitbox(350, 300, 200, 76, "не знайдено:\nHAVE_FFMPEG не з'явиться",
                    size=11, fill=RED, stroke=POS))
    f.append(arrow(558, 338, 582, 338))
    f.append(fitbox(590, 300, 200, 76, 'у звіті:\nFFMPEG: NO',
                    size=11, fill=RED, stroke=POS))
    f.append(arrow(798, 338, 822, 338))
    f.append(fitbox(830, 300, 180, 76, 'бекенда немає,\nisOpened() == false',
                    size=11, fill=RED, stroke=POS))

    f.append(mtext(560, 432,
                   ['WITH_ — дозвіл шукати, HAVE_ — результат пошуку.',
                    'Різницю між гілками видно тільки у звіті конфігурації.'],
                   size=12, color=MUTED))

    render(os.path.join(OUT, 'option-life.svg'), W, H, *f,
           title='Шлях параметра WITH_FFMPEG від командного рядка до поведінки')


# ── 6. Сходинки доказу (вставка proj-inspect-build) ────────────────────────
def fig_evidence():
    W, H = 980, 600
    f = []

    f.append(text(490, 54, 'питання: «чи прочитає ця збірка потік через FFmpeg?»',
                  size=14, italic=True, color=MUTED))

    rows = [
        ('звіт конфігурації:\nVideo I/O → FFMPEG: YES',
         'що знайшов CMake на машині складача.\nПро машину, де програма працює, — нічого.',
         FILL, MUTED),
        ('getStreamBackends()\nмістить CAP_FFMPEG',
         'бекенд оголошено в реєстрі й не вимкнено.\nЧи є файл плагіна — ще ніхто не питав.',
         FILL, MUTED),
        ('hasBackend(CAP_FFMPEG)\n== true',
         'плагін відкрито, версія ABI зійшлася.\nЩо саме всередині нього — ще невідомо.',
         FILL, LINE),
        ('VideoCapture відкрила\nсправжнє джерело',
         'є демультиплексор, кодек і доступ до джерела.\nЄдина відповідь без «але».',
         '#eaf4ec', FIELD),
    ]

    y = 88
    for i, (left, right, fill, stroke) in enumerate(rows):
        f.append(fitbox(40, y, 350, 84, left, size=13, fill=fill, stroke=stroke))
        f.append(fitbox(420, y, 520, 84, right, size=13, fill='#ffffff', stroke=stroke))
        if i < len(rows) - 1:
            f.append(arrow(215, y + 88, 215, y + 106))
        y += 110

    f.append(mtext(490, 546,
                   ['Кожна сходинка доводить більше за попередню —',
                    'і жодна не доводить наступної.'],
                   size=13, color=MUTED))

    render(os.path.join(OUT, 'evidence-ladder.svg'), W, H, *f,
           title='Чотири різні відповіді на одне питання')


if __name__ == '__main__':
    fig_layers()
    fig_config()
    fig_two_abis()
    fig_stewards()
    fig_option_life()
    fig_evidence()
    print('ok')
