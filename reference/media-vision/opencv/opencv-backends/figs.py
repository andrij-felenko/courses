# -*- coding: utf-8 -*-
"""Фігури до теми «Бекенди й прискорення: UMat, OpenCL, апаратна збірка»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

HOSTF = '#eef2fb'      # заливка хостового боку
DEVF  = '#fdf0ec'      # заливка боку пристрою


# ── 1. Один керівний блок, дві копії пікселів ──────────────────────────────
def fig_two_copies():
    W, H = 1000, 640
    f = []

    # заголовки колонок
    f.append(text(180, 52, 'Хост: системна памʼять', size=15, bold=True, color=NEG))
    f.append(text(820, 52, 'Пристрій: памʼять прискорювача', size=15, bold=True, color=POS))
    f.append(text(500, 52, 'Керівний блок UMatData', size=15, bold=True))

    # ── центральна колонка: поля керівного блоку
    f.append(rect(370, 70, 260, 300, fill='#ffffff', stroke=LINE, sw=2))
    rows = [
        ('refcount', 'заголовків Mat'),
        ('data', 'адреса в системній'),
        ('urefcount', 'заголовків UMat'),
        ('handle', 'буфер прискорювача'),
        ('flags', 'котра копія застаріла'),
    ]
    y = 86
    for name, note in rows:
        f.append(fitbox(384, y, 232, 32, name, size=14, bold=True,
                        fill=FILL, stroke=MUTED))
        f.append(text(500, y + 48, note, size=11, color=MUTED))
        y += 54

    # ── ліворуч: заголовки Mat і байти
    f.append(fitbox(60, 90, 240, 40, 'cv::Mat  ×  refcount', size=13, fill=HOSTF, stroke=NEG))
    f.append(fitbox(60, 152, 240, 84, 'байти, які процесор\nчитає напряму', size=13,
                    fill=HOSTF, stroke=NEG))
    f.append(arrow(368, 156, 306, 180))          # data →  байти
    f.append(arrow(58, 110, 366, 102))           # Mat → refcount (через верх)

    # ── праворуч: заголовки UMat і буфер
    f.append(fitbox(700, 90, 240, 40, 'cv::UMat  ×  urefcount', size=13, fill=DEVF, stroke=POS))
    f.append(fitbox(700, 152, 240, 84, 'cl_mem — процесор\nне читає його напряму', size=13,
                    fill=DEVF, stroke=POS))
    f.append(arrow(632, 264, 698, 202))          # handle → буфер
    f.append(arrow(942, 110, 634, 102))          # UMat → urefcount

    # ── нижня смуга: три стани прапорців
    f.append(line(50, 404, 950, 404, color=MUTED, sw=1, dash='6,5'))
    f.append(text(500, 432, 'Прапорці кажуть, котра копія зараз є правдою', size=14, bold=True))

    states = [
        ('обидві свіжі', 'жодного прапорця', 'нічого пересилати\nне треба'),
        ('HOST_COPY_OBSOLETE', 'писало ядро на пристрої', 'getMat забере\nдані з пристрою'),
        ('DEVICE_COPY_OBSOLETE', 'писав процесор', 'наступне ядро\nдочекається відсилання'),
    ]
    bw, gap = 288, 18
    for i, (title_, cause, cost) in enumerate(states):
        x = 50 + i * (bw + gap)
        f.append(rect(x, 452, bw, 140, fill='#ffffff', stroke=MUTED, sw=1.5))
        f.append(fitbox(x + 14, 466, bw - 28, 32, title_, size=12, bold=True,
                        fill=FILL, stroke=MUTED))
        f.append(text(x + bw / 2, 522, cause, size=12, color=MUTED))
        f.append(mtext(x + bw / 2, 552, cost.split('\n'), size=12))

    render(os.path.join(OUT, 'umatdata-two-copies.svg'), W, H, *f)


# ── 2. Перетини межі хост ↔ пристрій ───────────────────────────────────────
def lane_diagram(y0, steps, label):
    """steps — список (назва, 'h'|'d'). Повертає (фрагменти, кількість перетинів)."""
    f = []
    LX, X0, BW, GAP = 50, 210, 150, 24
    HY, DY, BH = y0, y0 + 118, 52

    f.append(text(LX, HY + 30, 'хост', size=14, bold=True, color=NEG, anchor='start'))
    f.append(text(LX, DY + 30, 'пристрій', size=14, bold=True, color=POS, anchor='start'))
    f.append(line(40, HY + 88, 960, HY + 88, color=MUTED, sw=1, dash='7,6'))

    prev_lane, prev_cx, crossings = None, None, 0
    for i, (name, lane) in enumerate(steps):
        x = X0 + i * (BW + GAP)
        y = HY if lane == 'h' else DY
        fill = HOSTF if lane == 'h' else DEVF
        stroke = NEG if lane == 'h' else POS
        f.append(fitbox(x, y, BW, BH, name, size=12, fill=fill, stroke=stroke))
        cx = x + BW / 2
        if prev_lane is not None:
            if prev_lane == lane:
                f.append(arrow(prev_cx + BW / 2 - 2, y + BH / 2, x - 4, y + BH / 2))
            else:
                crossings += 1
                y_prev = HY if prev_lane == 'h' else DY
                sy = y_prev + (BH if prev_lane == 'h' else 0)
                ey = y + (0 if lane == 'd' else BH)
                f.append(arrow(prev_cx, sy + 3, cx, ey - 3, color=POS, sw=2.2))
        prev_lane, prev_cx = lane, cx

    # вхід і вихід кадру
    f.append(text(X0 - 12, (HY + DY) / 2 + 34, label, size=13, anchor='end', color=MUTED))
    return f, crossings


def fig_crossings():
    W, H = 1000, 620
    f = []

    a, na = lane_diagram(78, [('кольори', 'd'), ('розмиття', 'd'),
                              ('своя обробка', 'd'), ('поріг', 'd')], 'кадр')
    f.extend(a)
    f.append(text(500, 46, 'Усі кроки мають гілку для прискорювача', size=15, bold=True))
    f.append(fitbox(760, 78, 200, 52, 'перетинів межі: 2\n(вхід і вихід)', size=13,
                    fill='#ffffff', stroke=FIELD))

    b, nb = lane_diagram(390, [('кольори', 'd'), ('розмиття', 'd'),
                               ('своя обробка', 'h'), ('поріг', 'd')], 'кадр')
    f.extend(b)
    f.append(text(500, 358, 'Один крок без гілки — і кадр ходить туди й назад',
                  size=15, bold=True))
    f.append(fitbox(760, 390, 200, 52, 'перетинів межі: 4\n+ дві точки очікування', size=13,
                    fill='#ffffff', stroke=POS))

    f.append(fitbox(50, 566, 910, 38,
                    'Кожен перетин — це і байти через шину, і зупинка: одна сторона чекає, поки друга допрацює',
                    size=13, fill=FILL, stroke=MUTED))

    render(os.path.join(OUT, 'boundary-crossings.svg'), W, H, *f)


# ── 3. Три маршрути від декодера до показу ─────────────────────────────────
def fig_routes():
    W, H = 1060, 600
    f = []
    f.append(text(530, 44, 'Той самий кадр від декодера до показу — три маршрути',
                  size=16, bold=True))

    routes = [
        ('Наскрізь через системну памʼять',
         [('декодер', 'd'), ('Mat', 'h'), ('UMat: обробка', 'd'), ('показ', 'h')],
         '4 перетини', POS),
        ('Апаратне декодування одразу в UMat',
         [('декодер', 'd'), ('UMat: обробка', 'd'), ('показ', 'h')],
         '1 перетин', MUTED),
        ('Спільний контекст: convertFromVASurface',
         [('декодер', 'd'), ('UMat: обробка', 'd'), ('показ на пристрої', 'd')],
         '0 перетинів', FIELD),
    ]

    X0, BW, GAP, BH = 60, 170, 26, 54
    VX, VW = 846, 174                     # колонка з підсумком — за найдовшим рядом
    for r, (title_, steps, verdict, color) in enumerate(routes):
        y = 92 + r * 162
        f.append(text(60, y, title_, size=14, bold=True, anchor='start'))
        prev = None
        for i, (name, lane) in enumerate(steps):
            x = X0 + i * (BW + GAP)
            fill = HOSTF if lane == 'h' else DEVF
            stroke = NEG if lane == 'h' else POS
            f.append(fitbox(x, y + 20, BW, BH, name, size=12, fill=fill, stroke=stroke))
            if prev is not None:
                crossed = prev != lane
                f.append(arrow(x - GAP + 4, y + 20 + BH / 2, x - 6, y + 20 + BH / 2,
                               color=POS if crossed else MUTED, sw=2.4 if crossed else 1.6))
                if crossed:
                    f.append(text(x - GAP / 2 - 1, y + 16, 'шина', size=10, color=POS))
            prev = lane
        f.append(fitbox(VX, y + 20, VW, BH, verdict, size=13,
                        bold=True, fill='#ffffff', stroke=color))

    f.append(fitbox(60, 536, 960, 40,
                    'Синє — системна памʼять, помаранчеве — памʼять прискорювача; '
                    'маршрут визначає не алгоритм, а спільність контексту',
                    size=13, fill=FILL, stroke=MUTED))

    render(os.path.join(OUT, 'three-routes.svg'), W, H, *f)


# ── 4. Дві гілки прискорення: порядок подій (до вставки hist-tapi-birth) ───
def fig_two_lineages():
    W, H = 1180, 520
    f = []

    X0, XW = 60, 1060          # смуга під ряди подій
    BH = 96                    # висота коробки

    def lane(y_label, y_box, label, color, items):
        f.append(text(X0, y_label, label, size=15, bold=True,
                      color=color, anchor='start'))
        n = len(items)
        slot = XW / float(n)
        bw = slot - 26
        for i, txt in enumerate(items):
            x = X0 + i * slot + 13
            f.append(fitbox(x, y_box, bw, BH, txt, size=13,
                            fill='#ffffff', stroke=color))
            if i:
                f.append(arrow(x - 24, y_box + BH / 2, x - 4, y_box + BH / 2,
                               color=MUTED, sw=1.8))

    lane(78, 94, 'Прозорий шлях: OpenCL', NEG, [
        '2011\nтека ocl заведена\nяк копія теки gpu',
        '2012 · 2.4.3\nмодуль ocl як прев’ю:\ncv::ocl::resize окремо',
        '2013 · жовтень\nперша чернетка\nT-API і класу UMat',
        '2014 · січень\nмодуль ocl\nвидалено з гілки',
        '3.0 · червень 2015\nUMat входить\nу звичайний cv::resize',
    ])

    lane(258, 274, 'Явний шлях: CUDA', POS, [
        '2.2 · грудень 2010\nмодуль gpu\nі клас cv::gpu::GpuMat',
        '2013 · вересень\nмодуль gpu\nперейменовано на cuda',
        '3.0 · 2015\ncv::cuda::GpuMat\nз upload і download',
        '4.0 · 2018\nмодулі cuda переїхали\nв opencv_contrib',
    ])

    f.append(line(X0, 412, X0 + XW, 412, color=MUTED, sw=1, dash='6,5'))
    f.append(fitbox(X0, 428, XW, 62,
                    'Порядок подій, а не масштаб часу. Обидві гілки почалися з того самого коду;\n'
                    'розійшлися вони в одному питанні — хто вирішує, де лежать пікселі.',
                    size=14, fill=FILL, stroke=MUTED))

    render(os.path.join(OUT, 'two-lineages.svg'), W, H, *f)


# ── Чотири моменти, коли важіль спрацьовує (до вставки api-tapi-controls) ───
def fig_control_moments():
    W, H = 1144, 520
    f = []

    f.append(text(572, 74, 'час: від складання бібліотеки до окремого кадру',
                  size=13, color=MUTED))
    f.append(arrow(56, 100, 1088, 100, color=MUTED, sw=1.6))

    cols = [
        ('1 · Збірка бібліотеки\ncmake',
         'чи є в бінарнику\nкод для цього шляху',
         ['WITH_OPENCL',
          'WITH_IPP · BUILD_IPP_IW',
          'WITH_TBB · WITH_OPENMP',
          'CPU_BASELINE · CPU_DISPATCH',
          'WITH_CUDA · WITH_VA_INTEL'],
         'міняється лише перезбіркою:\nна робочій машині\nважіль недосяжний',
         NEG),
        ('2 · Старт процесу\nзмінні середовища',
         'який пристрій узяти\nі що писати в кеш',
         ['OPENCV_OPENCL_DEVICE',
          'OPENCV_OPENCL_RUNTIME',
          'OPENCV_OPENCL_CACHE_*',
          'OPENCV_OPENCL_RAISE_ERROR',
          'OPENCV_TRACE',
          'OPENCV_THREAD_POOL_*'],
         'читаються один раз,\nпри першому дотику:\nputenv посеред роботи пізно',
         MUTED),
        ('3 · Виклики в коді\nпід час роботи',
         'увімкнути шлях, спитати\nпристрій, закрити чергу',
         ['ocl::haveOpenCL()',
          'ocl::setUseOpenCL()',
          'ocl::finish()',
          'ocl::Device::getDefault()',
          'setNumThreads()',
          'setUseOptimized()'],
         'діють з наступного виклику;\nsetUseOpenCL живе\nокремо в кожному потоці',
         FIELD),
        ('4 · Створення буфера\nтип і прапорці',
         'де лежать пікселі\nсаме цього кадру',
         ['cv::UMat проти cv::Mat',
          'USAGE_ALLOCATE_HOST_MEMORY',
          'AccessFlag',
          'getUMat() · getMat()',
          'CAP_PROP_HW_ACCELERATION'],
         'вирішується наново\nдля кожного буфера —\nі саме тут платять байтами',
         POS),
    ]

    X0, BW, GAP = 50, 240, 28
    for i, (title_, what, levers, late, color) in enumerate(cols):
        x = X0 + i * (BW + GAP)
        cx = x + BW / 2
        f.append(line(cx, 92, cx, 108, color=MUTED, sw=1.6))
        f.append(fitbox(x, 124, BW, 46, title_, size=13, bold=True,
                        fill=FILL, stroke=color, sw=2))
        f.append(mtext(cx, 196, what.split('\n'), size=12, color=MUTED))
        f.append(rect(x, 228, BW, 132, fill='#ffffff', stroke=MUTED, sw=1.2))
        ly = 252
        for s in levers:
            f.append(text(cx, ly, s, size=12))
            ly += 20
        f.append(mtext(cx, 390, late.split('\n'), size=11, color=color))

    f.append(fitbox(50, 450, 1044, 44,
                    'Важіль лівіше не обійти важелем правіше: чого немає у збірці, '
                    'того не створять ані змінна середовища, ані виклик',
                    size=13, fill=FILL, stroke=MUTED))

    render(os.path.join(OUT, 'control-moments.svg'), W, H, *f,
           title='Чотири моменти, коли важіль керування спрацьовує')


if __name__ == '__main__':
    fig_two_copies()
    fig_crossings()
    fig_routes()
    fig_two_lineages()
    fig_control_moments()
    print('ok:', os.listdir(OUT))


# ── Фігури до вставки proj-umat-boundaries ─────────────────────────────────
def fig_two_brackets():
    """Два секундоміри над одним кадром: постановка в чергу проти цілої роботи."""
    W, H = 1020, 540
    f = []
    f.append(text(510, 40, 'Той самий кадр, два секундоміри', size=17, bold=True))

    HY, DY, BH = 92, 250, 54
    f.append(text(46, HY + 32, 'ваш потік', size=14, bold=True, color=NEG, anchor='start'))
    f.append(text(46, DY + 32, 'черга пристрою', size=13, bold=True, color=POS, anchor='start'))

    # чотири виклики на хості — вузькі смужки: це лише постановка в чергу
    for i in range(4):
        x = 200 + i * 50
        f.append(rect(x, HY, 34, BH, fill=HOSTF, stroke=NEG, sw=1.5, rx=4))
    f.append(text(302, HY - 14, 'чотири виклики над UMat', size=12, color=MUTED))

    # довге очікування на хості
    f.append(fitbox(404, HY, 406, BH, 'finish() / copyTo у Mat / imshow — потік стоїть',
                    size=13, fill='#ffffff', stroke=NEG))

    # ядра на пристрої
    kernels = [('ядро cvtColor', 120), ('ядро розмиття', 210),
               ('ядро LUT', 90), ('ядро порога', 110)]
    x = 250
    for name, w in kernels:
        f.append(fitbox(x, DY, w, BH, name, size=12, fill=DEVF, stroke=POS))
        x += w + 10

    # вісь часу
    f.append(arrow(180, 336, 900, 336, color=MUTED, sw=1.4))
    f.append(text(920, 341, 'час', size=13, color=MUTED, anchor='start'))

    def bracket(x1, x2, y, color):
        return (line(x1, y, x2, y, color=color, sw=2.2) +
                line(x1, y - 8, x1, y + 8, color=color, sw=2.2) +
                line(x2, y - 8, x2, y + 8, color=color, sw=2.2))

    f.append(bracket(200, 404, 362, POS))
    f.append(text(302, 386, 'наївний секундомір: 0.42 мс', size=13, color=POS))
    f.append(bracket(200, 810, 414, FIELD))
    f.append(text(505, 438, 'finish() → робота → finish(): 2.25 мс', size=13, color=FIELD))

    f.append(fitbox(60, 466, 900, 46,
                    'Виклик над UMat повертається одразу — заплачено буде на першому ж '
                    'запиті готового результату',
                    size=13, fill=FILL, stroke=MUTED))

    render(os.path.join(OUT, 'measure-two-brackets.svg'), W, H, *f)


def fig_warmup():
    """Перші кадри повільні: драйвер компілює ядра під конкретний пристрій."""
    import math
    W, H = 880, 560
    f = []
    f.append(text(440, 40, 'Час першого кадру — це не час кадру', size=17, bold=True))

    vals = [210.0, 38.0, 6.1, 2.4, 2.3, 2.2, 2.3, 2.2, 2.3, 2.2]
    BW, GAP, X0 = 54, 14, 120
    BASE, PER_DEC = 430.0, 129.0          # y для 1 мс і пікселів на декаду

    def ytop(v):
        return BASE - PER_DEC * math.log10(v)

    f.append(fitbox(114, 58, 3 * (BW + GAP) - GAP + 6, 38,
                    'прогрів: драйвер\nкомпілює ядра', size=11,
                    fill='#fdecea', stroke=POS))
    f.append(fitbox(322, 58, 464, 38, 'сталий режим — звідси й міряти',
                    size=12, fill='#eef7f0', stroke=FIELD))

    for v, lab in ((1, '1 мс'), (10, '10 мс'), (100, '100 мс')):
        y = ytop(v)
        f.append(line(110, y, 800, y, color=MUTED, sw=1, dash='6,5'))
        f.append(text(104, y + 4, lab, size=12, color=MUTED, anchor='end'))

    for i, v in enumerate(vals):
        x = X0 + i * (BW + GAP)
        y = ytop(v)
        warm = i < 3
        f.append(rect(x, y, BW, BASE - y, fill='#fdecea' if warm else '#eef7f0',
                      stroke=POS if warm else FIELD, sw=1.5, rx=3))
        f.append(text(x + BW / 2.0, y - 8,
                      ('%.1f' % v) if v < 10 else '%d' % int(round(v)),
                      size=11, color=INK))
        f.append(text(x + BW / 2.0, BASE + 20, str(i + 1), size=12, color=MUTED))

    f.append(text(440, 476, 'номер кадру', size=13, color=MUTED))
    f.append(fitbox(60, 496, 760, 46,
                    'Форма важлива, числа — ні: скомпільовані ядра лягають у дисковий кеш, '
                    'тож наступний запуск коротший, але не нульовий',
                    size=12, fill=FILL, stroke=MUTED))

    render(os.path.join(OUT, 'warmup-first-frames.svg'), W, H, *f)


if __name__ == '__main__':
    fig_two_brackets()
    fig_warmup()
