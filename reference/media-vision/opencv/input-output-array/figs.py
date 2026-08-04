# -*- coding: utf-8 -*-
"""Фігури до теми «InputArray і OutputArray: спільний вхід для Mat, UMat і вектора»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

CALLF = '#eef2fb'      # бік того, хто викликає
LIBF  = '#fdf0ec'      # бік зібраної бібліотеки
FREE  = '#eef7f0'      # безплатно
COST  = '#fdecea'      # платимо


# ── 1. Один параметр, багато типів: що складає компілятор на місці виклику ──
def fig_call_site():
    W, H = 1180, 660
    f = []

    f.append(text(590, 38, 'Один параметр приймає різні типи — і жоден із них не копіюється',
                  size=17, bold=True))

    f.append(text(190, 84, 'об’єкт того, хто викликає', size=14, bold=True, color=NEG))
    f.append(text(590, 84, 'тимчасовий проксі на стеку', size=14, bold=True))
    f.append(text(985, 84, 'тіло функції в бібліотеці', size=14, bold=True, color=POS))

    callers = [
        ('cv::Mat frame', 'MAT'),
        ('cv::UMat gpuFrame', 'UMAT'),
        ('std::vector<Point2f> pts', 'STD_VECTOR\n+ FIXED_TYPE'),
        ('cv::Matx33d homography', 'MATX + FIXED_TYPE\n+ FIXED_SIZE'),
    ]

    BY, BH, GAP = 118, 78, 26
    for i, (name, kindtxt) in enumerate(callers):
        y = BY + i * (BH + GAP)
        f.append(fitbox(60, y, 264, BH, name, size=13, fill=CALLF, stroke=NEG))
        f.append(arrow(330, y + BH / 2, 424, y + BH / 2, color=MUTED, sw=1.8))
        f.append(fitbox(430, y, 320, BH, 'flags = ' + kindtxt + '\nobj = адреса об’єкта',
                        size=12, fill='#ffffff', stroke=LINE))

    # права колонка: одне зібране тіло
    f.append(rect(820, 118, 330, 372, fill=LIBF, stroke=POS, sw=2))
    f.append(text(985, 150, 'libopencv_imgproc.so', size=13, bold=True, color=POS))
    f.append(text(985, 176, 'зібране один раз, шаблонів немає', size=11, color=MUTED))
    body = [
        'switch (_src.kind())',
        'MAT → копія заголовка',
        'UMAT → відображення буфера',
        'STD_VECTOR → заголовок',
        'STD_BOOL_VECTOR → копія',
    ]
    yy = 216
    for s in body:
        f.append(text(985, yy, s, size=12))
        yy += 28
    f.append(fitbox(846, 388, 278, 84,
                    'тег поставив компілятор,\nрозбирає його бібліотека\nпід час роботи',
                    size=12, fill='#ffffff', stroke=MUTED))

    for i in range(4):
        y = BY + i * (BH + GAP) + BH / 2
        f.append(arrow(756, y, 814, 304 if i in (1, 2) else (250 if i == 0 else 360),
                       color=MUTED, sw=1.6))

    f.append(fitbox(60, 546, 1060, 74,
                    'InputArray — це typedef на const _InputArray&: проксі народжується як тимчасовий об’єкт\n'
                    'на місці виклику, живе до кінця виразу і не володіє нічим — ані пікселями, ані вектором',
                    size=13, fill=FILL, stroke=MUTED))

    render(os.path.join(OUT, 'call-site-proxy.svg'), W, H, *f)


# ── 2. Одне ціле число з чотирма незалежними відповідями ───────────────────
def fig_flags_layout():
    W, H = 1160, 620
    f = []
    f.append(text(580, 40, 'Поле flags: чотири незалежні відповіді в одному int',
                  size=17, bold=True))

    # смуга бітів 31 … 0
    X0, XW, SY, SH = 70, 1020, 96, 60
    bw = XW / 32.0
    f.append(text(X0 + bw / 2, SY - 14, '31', size=11, color=MUTED))
    f.append(text(X0 + XW - bw / 2, SY - 14, '0', size=11, color=MUTED))
    f.append(rect(X0, SY, XW, SH, fill='#ffffff', stroke=LINE, sw=1.8))

    zones = [
        (31, 31, '#fdecea', POS, '1'),
        (30, 30, '#fdecea', POS, '2'),
        (26, 24, '#eaf0fd', NEG, '3'),
        (20, 16, '#eef7f0', FIELD, '4'),
        (11, 0, FILL, MUTED, '5'),
    ]
    for hi, lo, fill, stroke, mark in zones:
        x1 = X0 + (31 - hi) * bw
        x2 = X0 + (31 - lo + 1) * bw
        f.append(rect(x1, SY + 3, x2 - x1, SH - 6, fill=fill, stroke=stroke, sw=1.8, rx=3))
        f.append(text((x1 + x2) / 2, SY + SH / 2 + 6, mark, size=16, bold=True, color=stroke))

    f.append(text(580, SY + SH + 26, 'сірі проміжки між зонами не використовуються',
                  size=12, color=MUTED))

    legend = [
        ('4', 'KIND_MASK = 31 << 16', 'звідки прийшли пікселі',
         'MAT · UMAT · STD_VECTOR · STD_BOOL_VECTOR · CUDA_GPU_MAT · NONE …', FIELD),
        ('3', 'ACCESS_READ = 1 << 24,  ACCESS_WRITE = 1 << 25', 'читати чи писати',
         'проксі входу ставить READ, проксі виходу — WRITE, спільний — обидва', NEG),
        ('1', 'FIXED_TYPE = 0x8000 << 16', 'тип змінювати не можна',
         'вектор Point2f — це завжди CV_32FC2, іншим типом він не стане', POS),
        ('2', 'FIXED_SIZE = 0x4000 << 16', 'розмір змінювати не можна',
         'Matx33d — це рівно 3 × 3, перевиділяти нема де', POS),
        ('5', 'молодші дванадцять бітів', 'тип елемента',
         'звичайний CV_8UC3 — глибина плюс кількість каналів', MUTED),
    ]

    RY, RH, GAP = 216, 66, 12
    for i, (mark, name, what, detail, color) in enumerate(legend):
        y = RY + i * (RH + GAP)
        f.append(circle(96, y + RH / 2, 17, fill='#ffffff', stroke=color, sw=2))
        f.append(text(96, y + RH / 2 + 6, mark, size=15, bold=True, color=color))
        f.append(fitbox(130, y, 366, RH, name, size=13, bold=True, fill='#ffffff', stroke=color))
        f.append(fitbox(508, y, 236, RH, what, size=13, fill=FILL, stroke=MUTED))
        f.append(fitbox(756, y, 334, RH, detail, size=11, fill='#ffffff', stroke=MUTED))

    render(os.path.join(OUT, 'flags-layout.svg'), W, H, *f)


# ── 3. getMat(): той самий виклик, чотири різні ціни ────────────────────────
def fig_getmat_cost():
    W, H = 1120, 620
    f = []
    f.append(text(560, 40, 'getMat(): один рядок коду, чотири різні ціни', size=17, bold=True))

    rows = [
        ('kind() == MAT', 'копія заголовка,\nлічильник +1',
         'нуль байтів', FREE, FIELD,
         'пікселі спільні з тим, хто викликав'),
        ('kind() == STD_VECTOR', 'заголовок над буфером\nвектора',
         'нуль байтів', FREE, FIELD,
         'нічим не володіє: вектор мусить пережити Mat'),
        ('kind() == STD_BOOL_VECTOR', 'виділення + побайтова\nкопія в циклі',
         'O(n) байтів', COST, POS,
         'у vector<bool> немає масиву байтів, на який можна вказати'),
        ('kind() == UMAT', 'відображення буфера\nприскорювача',
         'очікування черги,\nможливе пересилання', COST, POS,
         'доки Mat живий, буфер лишається відображеним'),
    ]

    Y0, RH, GAP = 96, 106, 18
    for i, (kind, what, cost, fill, stroke, note) in enumerate(rows):
        y = Y0 + i * (RH + GAP)
        f.append(fitbox(60, y, 268, RH, kind, size=13, bold=True, fill='#ffffff', stroke=LINE))
        f.append(arrow(334, y + RH / 2, 372, y + RH / 2, color=MUTED, sw=1.6))
        f.append(fitbox(378, y, 274, RH, what, size=12, fill=FILL, stroke=MUTED))
        f.append(fitbox(668, y, 224, RH, cost, size=13, bold=True, fill=fill, stroke=stroke))
        f.append(fitbox(908, y, 152, RH, note, size=11, fill='#ffffff', stroke=MUTED))

    f.append(fitbox(60, 552, 1000, 46,
                    'Тип аргументу вибрав гілку ще на місці виклику — у самому рядку '
                    'Mat src = _src.getMat(); ціни не видно',
                    size=13, fill=FILL, stroke=MUTED))

    render(os.path.join(OUT, 'getmat-cost.svg'), W, H, *f)


# ── 4. create() на боці виходу: чотири різні наслідки ───────────────────────
def fig_create_outcomes():
    W, H = 1160, 640
    f = []
    f.append(text(580, 40, '_dst.create(size, type): що станеться з пам’яттю того, хто викликав',
                  size=17, bold=True))

    cases = [
        ('dst порожній', 'Mat dst;',
         'виділити буфер\nі записати заголовок',
         'один malloc\nна перший кадр', FREE, FIELD),
        ('dst збігається', 'той самий dst\nз минулого кадру',
         'нічого не робити:\nранній вихід у Mat::create',
         'нуль виділень\nна кадр — ось ціль', FREE, FIELD),
        ('dst — виріз іншого\nрозміру', 'Mat roi = canvas(r);',
         'відпустити старе,\nвиділити нове',
         'запис іде в новий буфер,\nа canvas лишається чистим', COST, POS),
        ('dst фіксований', 'Matx33d H;\nvector<Point2f> pts;',
         'перевиділити ніде —\nCV_Assert падає',
         'виняток під час роботи\nзамість помилки компіляції', COST, POS),
    ]

    X0, BW, GAP = 52, 260, 22
    for i, (title_, code, act, res, fill, stroke) in enumerate(cases):
        x = X0 + i * (BW + GAP)
        f.append(fitbox(x, 84, BW, 56, title_, size=14, bold=True, fill='#ffffff', stroke=stroke, sw=2))
        f.append(fitbox(x, 156, BW, 62, code, size=12, fill=CALLF, stroke=NEG))
        f.append(arrow(x + BW / 2, 224, x + BW / 2, 258, color=MUTED, sw=1.6))
        f.append(fitbox(x, 264, BW, 82, act, size=12, fill=FILL, stroke=MUTED))
        f.append(arrow(x + BW / 2, 352, x + BW / 2, 386, color=MUTED, sw=1.6))
        f.append(fitbox(x, 392, BW, 88, res, size=12, bold=True, fill=fill, stroke=stroke))

    f.append(line(52, 510, 1108, 510, color=MUTED, sw=1, dash='6,5'))
    f.append(fitbox(52, 528, 1056, 84,
                    'Третій випадок — не помилка бібліотеки, а прямий наслідок правила: create міняє\n'
                    'сам об’єкт того, хто викликав, і виріз після перевиділення перестає бути вирізом.\n'
                    'Жодного попередження не буде — просто результат опиниться не там, де на нього чекають.',
                    size=13, fill=FILL, stroke=MUTED))

    render(os.path.join(OUT, 'create-outcomes.svg'), W, H, *f)


# ── 5. Каркас власної функції: чому саме такий порядок (вставка proj) ───────
def fig_own_order():
    W, H = 1180, 720
    f = []

    f.append(text(590, 40, 'Шість рядків каркаса: кожен стоїть на своєму місці не випадково',
                  size=17, bold=True))

    f.append(text(300, 78, 'порядок у тілі функції', size=13, bold=True, color=NEG))
    f.append(text(880, 78, 'що ламається, якщо переставити', size=13, bold=True, color=POS))

    steps = [
        ('CV_Assert(_src.type() == CV_8UC1);',
         'Питаємо проксі, а не дані: неправильний тип\nвидно ще до першого доступу до пікселів.'),
        ('CVX_OCL_RUN(_dst.isUMat(), ocl_localRange(...));',
         'Після getMat пізно — кадр уже стягнуто на хост,\nі гілка прискорювача втратила сенс.'),
        ('cv::Mat src = _src.getMat();',
         'Заголовок бере лічильник на себе: старий буфер\nдоживе до кінця, навіть якщо приймач переїде.'),
        ('_dst.create(src.size(), CV_8UC1);',
         'Саме тут вирішується, буде виділення чи ні —\nі саме тут виріз може відв’язатися від полотна.'),
        ('cv::Mat dst = _dst.getMat();',
         'Раніше — узяли б заголовок на буфер,\nякий create щойно замінив новим.'),
        ('if (overlaps(src, dst)) → тимчасовий буфер',
         'Віконна операція читає сусідів: писати\nв той самий буфер не можна.'),
    ]

    LX, LW, RX, RW, BH, GAP, Y0 = 56, 452, 552, 572, 74, 24, 108
    for i, (code, why) in enumerate(steps):
        y = Y0 + i * (BH + GAP)
        f.append(fitbox(LX, y, LW, BH, code, size=13, fill=CALLF, stroke=NEG))
        f.append(fitbox(RX, y, RW, BH, why, size=12, fill=COST, stroke=POS))
        if i < len(steps) - 1:
            f.append(arrow(LX + LW / 2, y + BH + 2, LX + LW / 2, y + BH + GAP - 2,
                           color=MUTED, sw=1.6))

    render(os.path.join(OUT, 'own-function-order.svg'), W, H, *f)


# ── 6. Чому віконна операція не працює на місці (вставка proj) ──────────────
def fig_inplace_window():
    W, H = 1140, 560
    f = []

    f.append(text(570, 38, 'Поточкова операція переживе in-place, віконна — ні',
                  size=17, bold=True))

    src_vals = ['10', '40', '42', '90', '91', '12', '13', '80', '82', '20']

    CW, CH, X0 = 62, 46, 300

    def row(y, vals, hot=(), done=0):
        out = []
        for i, v in enumerate(vals):
            x = X0 + i * CW
            fill, stroke = '#ffffff', MUTED
            if i < done:
                fill, stroke = COST, POS
            elif i in hot:
                fill, stroke = FREE, FIELD
            out.append(fitbox(x, y, CW - 4, CH, v, size=14, fill=fill, stroke=stroke, sw=1.6))
        return out

    # ── правильний варіант ──
    f.append(text(56, 112, 'окремий приймач', size=14, bold=True, color=FIELD, anchor='start'))
    f.append(text(56, 134, 'читаємо src, пишемо dst', size=12, color=MUTED, anchor='start'))
    f.extend(row(96, src_vals, hot=(2, 3, 4)))
    f.append(text(X0 + 3.5 * CW - 2, 172, 'вікно бачить 42 90 91 — справжні пікселі',
                  size=12, color=FIELD))
    f.append(text(X0 + 3.5 * CW - 2, 200, 'dst[3] = 91 − 42 = 49  ✔', size=14, bold=True, color=FIELD))

    f.append(line(56, 232, 1084, 232, color=MUTED, sw=1, dash='6,5'))

    # ── in-place ──
    f.append(text(56, 296, 'in-place: localRange(m, m)', size=14, bold=True, color=POS, anchor='start'))
    f.append(text(56, 318, 'той самий буфер', size=12, color=MUTED, anchor='start'))
    mixed = ['30', '32', '50'] + src_vals[3:]
    f.extend(row(280, mixed, hot=(3, 4), done=3))
    f.append(text(X0 + 3.5 * CW - 2, 356, 'на місці 42 вже лежить записаний результат 50',
                  size=12, color=POS))
    f.append(text(X0 + 3.5 * CW - 2, 384, 'dst[3] = 91 − 50 = 41  ✘  (мало бути 49)',
                  size=14, bold=True, color=POS))

    f.append(fitbox(180, 420, 800, 84,
                    'Поточкова операція читає рівно той піксель, який пише, — їй in-place байдужий.\n'
                    'Віконна читає сусідів, а сусіди зліва вже переписані: помилка не падає й не\n'
                    'помітна на око, вона просто повзе рядком і накопичується.',
                    size=13, fill=FILL, stroke=MUTED))

    render(os.path.join(OUT, 'inplace-window.svg'), W, H, *f)


# ── 7. Історія: де живе відповідь на питання «якого це типу» (вставка hist) ──
def fig_type_question():
    W, H = 1300, 580
    f = []

    f.append(text(650, 40, 'Питання одне — «якого типу цей аргумент?»; місце відповіді мінялося чотири рази',
                  size=17, bold=True))

    AXIS = 300
    f.append(line(60, AXIS, 1240, AXIS, color=MUTED, sw=2))

    cols = [
        (190,
         '1999–2006 · C-інтерфейс\n\ntypedef void CvArr;\ncvResize(const CvArr* src, ...)',
         'тег лежить у перших 4 байтах\nсамого об’єкта; функція його\nчитає й вгадує тип',
         'чужий тип → падіння\nпід час роботи', POS),
        (490,
         '2009 · OpenCV 2.0\n\ncv::Mat із лічильником\nresize(const Mat& src, Mat& dst)',
         'тег не потрібен: тип знає\nкомпілятор і перевіряє його\nна місці виклику',
         'зате тип мусить бути\nрівно один', POS),
        (800,
         '2011 · OpenCV 2.3\n\nclass _InputArray\nresize(InputArray, OutputArray)',
         'тег ставить компілятор\nу поле flags тимчасового\nпроксі на стеку',
         'чужий тип → програма\nне збереться', FIELD),
        (1110,
         '2015 · OpenCV 3.0\n\nвид UMAT + T-API',
         'новий контейнер — новий\nрядок у тому самому переліку\nвидів',
         'підписи функцій\nне змінилися', FIELD),
    ]

    for cx, top, mid, note, ncol in cols:
        f.append(fitbox(cx - 140, 84, 280, 130, top, size=13, fill=CALLF, stroke=NEG))
        f.append(line(cx, 214, cx, AXIS - 12, color=MUTED, sw=1.5, dash='5,4'))
        f.append(circle(cx, AXIS, 9, fill='#ffffff', stroke=INK, sw=2))
        f.append(fitbox(cx - 140, 336, 280, 96, mid, size=13, fill=FILL, stroke=LINE))
        f.append(fitbox(cx - 140, 452, 280, 62, note, size=13, fill='#ffffff', stroke=ncol))

    render(os.path.join(OUT, 'type-question-timeline.svg'), W, H, *f)


if __name__ == '__main__':
    fig_call_site()
    fig_flags_layout()
    fig_getmat_cost()
    fig_create_outcomes()
    fig_own_order()
    fig_inplace_window()
    fig_type_question()
    print('ok:', sorted(os.listdir(OUT)))
