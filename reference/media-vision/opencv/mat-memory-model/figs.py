# -*- coding: utf-8 -*-
"""Фігури до теми «cv::Mat: пам'ять, лічильник посилань і володіння»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def box_with_title(x, y, w, h, title, lines, size=12, fill=FILL, stroke=LINE):
    """Рамка з жирним заголовком угорі й рядками під ним."""
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.6)
    out += text(x + w / 2, y + 22, title, size=size + 2, bold=True)
    out += mtext(x + w / 2, y + 44, lines, size=size, color=INK)
    return out


# ── 1. Заголовок і блок пікселів ───────────────────────────────────────────
def fig_header_and_data():
    W, H = 980, 540
    f = []

    cols = [(40, 'Mat a'), (390, 'Mat b'), (740, 'roi')]
    body = [
        ['rows=1080  cols=1920', 'step[0]=5760', 'data  →', 'u  →'],
        ['rows=1080  cols=1920', 'step[0]=5760', 'data  →', 'u  →'],
        ['rows=480  cols=640', 'step[0]=5760', 'data  → (зсув)', 'u  →'],
    ]
    for (x, name), lines in zip(cols, body):
        f.append(box_with_title(x, 56, 200, 128, name, lines))

    # UMatData посередині
    f.append(box_with_title(340, 246, 300, 92, 'UMatData',
                            ['refcount = 3', 'data · origdata · size'],
                            fill='#eef4ff', stroke=NEG))

    # стрілки заголовок → UMatData
    f.append(arrow(140, 184, 380, 246, color=NEG))
    f.append(arrow(490, 184, 490, 246, color=NEG))
    f.append(arrow(840, 184, 600, 246, color=NEG))
    f.append(text(40, 214, 'поле u', size=12, color=NEG, anchor='start'))

    # блок пікселів
    f.append(rect(40, 400, 900, 84, fill='#eaf7ef', stroke=FIELD, sw=1.8))
    f.append(mtext(490, 432, ['блок пікселів: 1920 · 1080 · 3 = 6 220 800 байтів',
                              'виділений один раз, з місця не рухається'], size=13))
    f.append(arrow(490, 338, 490, 400, color=FIELD))

    f.append(text(490, 516, 'копія заголовка — десятки байтів; пікселі нікуди не копіюються',
                  size=13, color=MUTED))
    return render(os.path.join(IMG, 'header-and-data.svg'), W, H, *f,
                  title='Заголовок і блок пікселів живуть окремо')


# ── 2. Геометрія буфера: step, вид, покажчики ──────────────────────────────
def fig_step_and_view():
    W, H = 980, 460
    f = []

    x0, y0, seg, hgt = 60, 108, 140, 62
    n = 6
    # стрічка пам'яті
    f.append(rect(x0, y0, seg * n, hgt, fill='#f7f7f7', stroke=LINE, sw=1.6))
    for i in range(1, n):
        f.append(line(x0 + seg * i, y0, x0 + seg * i, y0 + hgt, color=MUTED, sw=1.0))
    for i in range(n):
        f.append(text(x0 + seg * i + seg / 2, y0 + 20, 'рядок %d' % i, size=11, color=MUTED))

    # зелений вид усередині рядків 1..3
    for i in (1, 2, 3):
        gx = x0 + seg * i + 38
        f.append(rect(gx, y0 + 30, 72, 24, fill='#cdebd9', stroke=FIELD, sw=1.4, rx=3))

    # step[0] над рядком 2
    f.append(line(x0 + seg * 2, 88, x0 + seg * 3, 88, color=POS, sw=1.6))
    f.append(line(x0 + seg * 2, 82, x0 + seg * 2, 94, color=POS, sw=1.6))
    f.append(line(x0 + seg * 3, 82, x0 + seg * 3, 94, color=POS, sw=1.6))
    f.append(text(x0 + seg * 2.5, 74, 'step[0] = 5760 Б', size=12, color=POS))

    # ширина вида
    f.append(text(x0 + seg * 2 + 74, 200, 'cols · elemSize = 1920 Б', size=12, color=FIELD))
    f.append(line(x0 + seg * 2 + 74, 190, x0 + seg * 2 + 74, 172, color=FIELD, sw=1.2, dash='3,3'))

    # покажчики знизу
    marks = [(x0, 'datastart'), (x0 + seg + 38, 'data'), (x0 + seg * n, 'datalimit')]
    for mx, name in marks:
        f.append(line(mx, y0 + hgt, mx, 252, color=MUTED, sw=1.0, dash='3,3'))
        f.append(text(mx, 268, name, size=12, color=INK))

    notes = [
        'data — перший байт вида; datastart і datalimit лишаються від УСЬОГО буфера;',
        'step[0] лишається кроком повного кадру — між рядками вида стоять чужі байти;',
        'тому isContinuous() = false, і однопрохідний цикл по всіх пікселях заборонений.',
    ]
    for i, s in enumerate(notes):
        f.append(text(60, 322 + i * 26, '• ' + s, size=13, anchor='start'))

    return render(os.path.join(IMG, 'step-and-view.svg'), W, H, *f,
                  title='Вид ділить буфер: що змінюється, а що лишається')


# ── 3. Три режими володіння ────────────────────────────────────────────────
def fig_ownership_modes():
    W, H = 980, 470
    f = []

    cx = [170, 490, 810]
    heads = [['1. OpenCV виділила', 'памʼять сама'],
             ['2. Заголовок над', 'чужим буфером'],
             ['3. Чужий буфер', 'і власний алокатор']]
    mid = [['UMatData', 'refcount = 2'],
           ['u = nullptr', 'лічильника нема'],
           ['UMatData', 'USER_ALLOCATED']]
    midcolor = [(NEG, '#eef4ff'), (POS, '#fdecea'), (FIELD, '#eaf7ef')]
    buf = ['пікселі від fastMalloc', 'пікселі GstBuffer', 'пікселі GstBuffer']
    foot = [['звільняє release(),', 'коли лічильник упав до нуля'],
            ['release() не звільняє нічого —', 'буфер мусить пережити Mat'],
            ['release() кличе твій deallocate() —', 'той відпускає буфер сам']]

    for i, x in enumerate(cx):
        f.append(mtext(x, 62, heads[i], size=13, bold=True))
        f.append(fitbox(x - 70, 106, 140, 44, 'Mat', size=14, bold=True))
        f.append(arrow(x, 150, x, 190))
        st, fl = midcolor[i]
        f.append(rect(x - 108, 190, 216, 60, fill=fl, stroke=st, sw=1.6))
        f.append(mtext(x, 214, mid[i], size=12, color=INK))
        f.append(arrow(x, 250, x, 292, color=st))
        f.append(fitbox(x - 100, 292, 200, 42, buf[i], size=12))
        f.append(mtext(x, 368, foot[i], size=11, color=MUTED))

    return render(os.path.join(IMG, 'ownership-modes.svg'), W, H, *f,
                  title='Три режими володіння пікселями')


# ── 4. Де жив лічильник у трьох поколіннях API (до вставки hist-) ──────────
def fig_counter_homes():
    W, H = 1020, 470
    f = []

    cx = [180, 510, 840]
    era = [['C-API, з 2000-го', 'IplImage / CvMat'],
           ['C++-інтерфейс, 2.0 (2009)', 'Mat з int* refcount'],
           ['T-API, 3.0 (2015)', 'Mat + UMat через UMatData']]
    accent = [(POS, '#fdecea'), (FIELD, '#eaf7ef'), (NEG, '#eef4ff')]

    top = [['IplImage', 'imageData →', 'лічильника НЕМА'],
           ['Mat', 'data →', 'refcount →'],
           ['Mat        UMat', 'data →      handle →', 'u →              u →']]
    blk = [['блок пікселів', '(і більше нічого)'],
           ['блок пікселів', '⟨вирівняно⟩  [ refcount ]'],
           ['UMatData:  refcount · urefcount', 'data · origdata · handle']]
    foot = [['звільняє людина:', 'cvReleaseImage(&img)'],
            ['звільняє останній Mat;', 'лічильник — у хвості того самого', 'блоку, поряд із пікселями'],
            ['звільняє останній власник —', 'байдуже, Mat він чи UMat;', 'лічильник відірвано від пікселів']]

    for i, x in enumerate(cx):
        st, fl = accent[i]
        f.append(mtext(x, 62, era[i], size=13, bold=True))
        f.append(rect(x - 140, 96, 280, 76, fill=FILL, stroke=LINE, sw=1.6))
        f.append(mtext(x, 120, top[i], size=12))
        f.append(arrow(x, 172, x, 214, color=st))
        f.append(rect(x - 150, 214, 300, 62, fill=fl, stroke=st, sw=1.6))
        f.append(mtext(x, 240, blk[i], size=12))
        f.append(mtext(x, 328, foot[i], size=11, color=MUTED))

    return render(os.path.join(IMG, 'counter-homes.svg'), W, H, *f,
                  title='Де жив лічильник власників: три покоління API')


# ── 5. Ланцюг звільнення до gst_sample_unref (до вставки proj-) ────────────
def fig_release_chain():
    W, H = 1000, 540
    f = []

    steps = [
        ('~Mat() → release()',
         ['поки живий бодай один заголовок,', 'лічильник до нуля не дійде'],
         (LINE, FILL)),
        ('CV_XADD(&u->refcount, −1) вернув 1',
         ['старе значення 1 → нове 0:', 'цей заголовок був останнім'],
         (LINE, FILL)),
        ('Mat::deallocate()',
         ['бере u->currAllocator —', 'поле Mat::allocator тут ні до чого'],
         (LINE, FILL)),
        ('MatAllocator::unmap(u) — БАЗОВА',
         ['звіряє urefcount == 0 і refcount == 0', 'і сама кличе deallocate(u)'],
         (NEG, '#eef4ff')),
        ('GstMatAllocator::deallocate(u) — НАША',
         ['прапорець USER_ALLOCATED стоїть →', 'fastFree(origdata) не викликається'],
         (FIELD, '#eaf7ef')),
        ('gst_buffer_unmap → gst_sample_unref',
         ['саме в цьому порядку;', 'слот повертається в пул конвеєра'],
         (FIELD, '#eaf7ef')),
    ]

    x, w, h = 80, 520, 52
    for i, (head, note, (st, fl)) in enumerate(steps):
        y = 62 + i * 70
        f.append(fitbox(x, y, w, h, head, size=14, stroke=st, fill=fl, sw=1.6))
        f.append(mtext(650, y + 21, note, size=12, color=MUTED, anchor='start'))
        if i + 1 < len(steps):
            f.append(arrow(x + w / 2, y + h, x + w / 2, y + 70, color=st))

    f.append(text(500, 508, 'про GStreamer знає лише останній крок — той, який пишемо ми',
                  size=13, color=MUTED))
    return render(os.path.join(IMG, 'release-chain.svg'), W, H, *f,
                  title='Ланцюг звільнення: від останнього Mat до gst_sample_unref')


# ── 6. Тиск на пул буферів конвеєра (до вставки proj-) ─────────────────────
def fig_pool_pressure():
    W, H = 1000, 500
    f = []

    f.append(text(500, 62, 'пул буферів конвеєра — чотири слоти', size=13, bold=True))

    xs = [120, 310, 500, 690]
    held = ['слот 0\nвідданий', 'слот 1\nвідданий', 'слот 2\nвідданий', 'слот 3\nвільний']
    for i, sx in enumerate(xs):
        st, fl = ((POS, '#fdecea') if i < 3 else (FIELD, '#eaf7ef'))
        f.append(fitbox(sx, 76, 170, 52, held[i], size=12, stroke=st, fill=fl, sw=1.6))

    mats = ['cv::Mat #1\nу черзі детектора', 'cv::Mat #2\nу черзі детектора',
            'cv::Mat #3\nвиріз 32×32']
    for i in range(3):
        f.append(arrow(xs[i] + 85, 128, xs[i] + 85, 186, color=POS))
        f.append(fitbox(xs[i], 186, 170, 52, mats[i], size=12))

    f.append(text(500, 272, 'поки живий заголовок — слот не повертається в пул',
                  size=13, color=INK))
    f.append(line(60, 296, 940, 296, color=MUTED, sw=1.0, dash='4,4'))

    f.append(fitbox(60, 320, 420, 110,
                    ['max-buffers=2, drop=false',
                     'appsink не бере наступний кадр,',
                     'джерело впирається в порожній пул',
                     'і стає — картинка «завмирає»'],
                    size=13, stroke=POS, fill='#fdecea', sw=1.6))
    f.append(fitbox(520, 320, 420, 110,
                    ['drop=true (з 1.28 — leaky-type)',
                     'старий кадр викидають мовчки,',
                     'конвеєр живий, але детектор',
                     'бачить не кожен кадр'],
                    size=13, stroke=NEG, fill='#eef4ff', sw=1.6))

    f.append(text(500, 468, 'clone() повертає слот негайно — ціною копії всього кадру',
                  size=13, color=MUTED))
    return render(os.path.join(IMG, 'pool-pressure.svg'), W, H, *f,
                  title='Хто тримає слоти пулу, поки живі заголовки')


# ── 7. Розкладка бітів поля flags (до вставки api-) ────────────────────────
def fig_flags_bits():
    W, H = 1060, 470
    f = []

    x0, bar_y, bar_h, unit = 60, 150, 62, 28.125
    groups = [
        (16, '31–16', FILL, LINE),
        (1, '15', '#fdecea', POS),
        (1, '14', '#eaf7ef', FIELD),
        (2, '13–12', '#ffffff', MUTED),
        (9, '11–3', '#eef4ff', NEG),
        (3, '2–0', '#e9e4f7', '#6b4fbb'),
    ]

    xs = []
    x = x0
    for bits, label, fill, stroke in groups:
        w = unit * bits
        xs.append(x + w / 2)
        f.append(fitbox(x, bar_y, w, bar_h, label, size=13, fill=fill, stroke=stroke, sw=1.6))
        x += w

    # два вузькі біти — підписи згори, щоб не тіснитися
    f.append(fitbox(150, 74, 300, 44,
                    'біт 15 · CV_SUBMAT_FLAG · 0x8000', size=12, stroke=POS, fill='#fdecea'))
    f.append(line(300, 118, xs[1], bar_y - 4, color=POS, sw=1.2, dash='3,3'))
    f.append(fitbox(660, 74, 320, 44,
                    'біт 14 · CV_MAT_CONT_FLAG · 0x4000', size=12, stroke=FIELD, fill='#eaf7ef'))
    f.append(line(820, 118, xs[2], bar_y - 4, color=FIELD, sw=1.2, dash='3,3'))

    # три широкі групи — підписи знизу, у два яруси
    f.append(fitbox(80, 258, 300, 52, 'магія 0x42FF\nMAGIC_MASK = 0xFFFF0000',
                    size=12, stroke=LINE, fill=FILL))
    f.append(line(230, 258, xs[0], bar_y + bar_h + 4, color=LINE, sw=1.2, dash='3,3'))

    f.append(fitbox(600, 258, 380, 52, 'канали − 1\nCV_MAT_CN(f) = ((f & 0xFF8) >> 3) + 1',
                    size=12, stroke=NEG, fill='#eef4ff'))
    f.append(line(790, 258, xs[4], bar_y + bar_h + 4, color=NEG, sw=1.2, dash='3,3'))

    f.append(fitbox(660, 348, 320, 52, 'глибина\nCV_MAT_DEPTH(f) = f & 7',
                    size=12, stroke='#6b4fbb', fill='#e9e4f7'))
    f.append(line(940, 348, xs[5], bar_y + bar_h + 4, color='#6b4fbb', sw=1.2, dash='3,3'))

    f.append(fitbox(80, 348, 300, 52, 'біти 13–12\nне використані', size=12,
                    stroke=MUTED, fill='#ffffff'))
    f.append(line(300, 374, xs[3], bar_y + bar_h + 4, color=MUTED, sw=1.2, dash='3,3'))

    f.append(text(530, 436, '0x42FF4010  →  CV_8UC3, суцільний, не підматриця',
                  size=13, color=MUTED))
    return render(os.path.join(IMG, 'flags-bits.svg'), W, H, *f,
                  title='Поле flags: 32 біти, п’ять різних відповідей')


if __name__ == '__main__':
    print(fig_header_and_data())
    print(fig_step_and_view())
    print(fig_ownership_modes())
    print(fig_counter_homes())
    print(fig_release_chain())
    print(fig_pool_pressure())
    print(fig_flags_bits())
