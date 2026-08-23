# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: конвеєр експорту й розгортання ────────────────────────────────
def fig_pipeline():
    W, H = 820, 430
    p = []
    p.append(text(W/2, 26, 'Дорога моделі: від хмари до чипа', size=17, bold=True))

    # Дві зони: хмара (навчання) і пристрій (інференс), а між ними — місток експорту
    p.append(rect(24, 50, 360, 150, fill='#eaf0fd', stroke=NEG, sw=1.5, rx=10))
    p.append(text(204, 70, 'ХМАРА — навчання', size=13, bold=True, color=NEG))
    p.append(rect(436, 50, 360, 150, fill='#eafaf1', stroke=FIELD, sw=1.5, rx=10))
    p.append(text(616, 70, 'ПРИСТРІЙ — інференс', size=13, bold=True, color=FIELD))

    # Кроки в хмарі
    b, w, h = textbox(120, 120, 'навчена\nмодель\n(PyTorch/TF)', size=12, fill=BG, stroke=NEG)
    p.append(b)
    b, w, h = textbox(290, 120, 'ЕКСПОРТ\nграф + ваги', size=12, fill='#fff', stroke=POS, bold=True)
    p.append(b)
    p.append(arrow(168, 120, 248, 120, color=NEG))

    # Місток
    b, w, h = textbox(410, 130, 'один\nфайл', size=11, fill='#fdf6e3', stroke=MUTED)
    p.append(b)
    p.append(arrow(330, 120, 388, 128, color=INK))
    p.append(arrow(432, 128, 500, 120, color=INK))

    # Кроки на пристрої
    b, w, h = textbox(560, 120, 'вшити у Flash\n(масив C)', size=12, fill=BG, stroke=FIELD)
    p.append(b)
    b, w, h = textbox(720, 120, 'Invoke()\nна кадр', size=12, fill='#fff', stroke=FIELD, bold=True)
    p.append(b)
    p.append(arrow(626, 120, 660, 120, color=FIELD))

    # Нижня стрічка — реальні фази експорту
    y = 250
    p.append(text(W/2, y-12, 'Що насправді робить «експорт» — чотири фази', size=13, bold=True))
    steps = [
        ('1. ЗАФІКСУВАТИ', 'застиглі ваги +\nграф операцій', FIELD),
        ('2. ПЕРЕКЛАСТИ', 'у формат рушія\n(.tflite / ONNX)', NEG),
        ('3. КВАНТУВАТИ', 'float32 → int8\nна калібрувальних\nданих', POS),
        ('4. ПЕРЕВІРИТИ', 'той самий вихід,\nщо й в оригіналі?', MUTED),
    ]
    bw, gap = 178, 12
    x0 = (W - (bw*4 + gap*3)) / 2
    for i, (head, body, col) in enumerate(steps):
        x = x0 + i*(bw+gap)
        p.append(rect(x, y+4, bw, 110, fill=FILL, stroke=col, sw=1.6, rx=8))
        p.append(text(x+bw/2, y+28, head, size=12, bold=True, color=col))
        p.append(mtext(x+bw/2, y+50, body, size=11, color=INK))
        if i < 3:
            p.append(arrow(x+bw+1, y+58, x+bw+gap-1, y+58, color=INK, sw=1.6))

    p.append(text(W/2, 400, 'Помилка тут не «впаде» — модель просто почне тихо помилятися на чипі.',
                  size=11, italic=True, color=MUTED))
    render(os.path.join(IMG, 'export-pipeline.svg'), W, H, *p)


# ── Фігура 2: проміжний формат як спільна мова ──────────────────────────────
def fig_interchange():
    W, H = 760, 360
    p = []
    p.append(text(W/2, 26, 'Проміжний формат — спільна мова рамок і чипів', size=17, bold=True))

    # Ліворуч — рамки навчання (різні)
    frameworks = ['PyTorch', 'TensorFlow', 'JAX / Keras']
    fy = [80, 160, 240]
    for name, y in zip(frameworks, fy):
        b, w, h = textbox(110, y, name, size=13, fill='#eaf0fd', stroke=NEG, bold=True, min_w=150)
        p.append(b)

    # Центр — проміжний формат
    p.append(rect(320, 110, 160, 120, fill='#fdf6e3', stroke=POS, sw=2, rx=12))
    p.append(text(400, 150, 'ПРОМІЖНИЙ', size=13, bold=True, color=POS)),
    p.append(text(400, 172, 'ФОРМАТ', size=13, bold=True, color=POS))
    p.append(text(400, 198, '.tflite · ONNX', size=12, color=INK))
    p.append(text(400, 216, 'граф + ваги', size=11, color=MUTED))

    # Праворуч — цілі (різні)
    targets = ['МК + TFLite\nMicro', 'бортовий\nкомп\'ютер', 'мобільний\nGPU / NPU']
    ty = [80, 160, 240]
    for name, y in zip(targets, ty):
        b, w, h = textbox(650, y, name, size=12, fill='#eafaf1', stroke=FIELD, bold=True, min_w=150)
        p.append(b)

    # Стрілки досередини і назовні
    for y in fy:
        p.append(arrow(190, y, 318, 150 if y == 160 else (130 if y < 160 else 200), color=NEG, sw=1.6))
    for y in ty:
        p.append(arrow(482, 150 if y == 160 else (130 if y < 160 else 200), 572, y, color=FIELD, sw=1.6))

    p.append(text(W/2, 300, 'M рамок навчають у K цілей через ОДИН формат —', size=12, color=INK))
    p.append(text(W/2, 320, 'замість M×K окремих конвертерів. Це й уся ідея ONNX.', size=12, color=INK))
    render(os.path.join(IMG, 'interchange-format.svg'), W, H, *p)


# ── Фігура 3: калібрування — звідки експорт бере діапазон для int8 ──────────
def fig_calibration():
    W, H = 760, 380
    p = []
    p.append(text(W/2, 26, 'Калібрування: реальні дані задають межі int8', size=17, bold=True))

    # Вісь активацій
    ax_y = 150
    p.append(line(90, ax_y, 670, ax_y, color=INK, sw=1.6))
    p.append(text(380, ax_y+34, 'значення активацій (float32)', size=12, color=MUTED))

    # Гістограма «реальних» активацій — горб
    import math
    cx, span = 360, 150
    bars = 24
    for i in range(bars):
        t = (i - bars/2) / (bars/2)
        height = 70 * math.exp(-3.0*t*t)
        x = cx - span + i*(2*span/bars)
        p.append(rect(x, ax_y-height, (2*span/bars)-2, height, fill='#cfe3f7', stroke=NEG, sw=0.8, rx=2))

    # Межі min/max, що їх «бачить» калібрувальний набір
    lo, hi = cx-span, cx+span
    p.append(line(lo, ax_y-95, lo, ax_y+10, color=POS, sw=2, dash='5 4'))
    p.append(line(hi, ax_y-95, hi, ax_y+10, color=POS, sw=2, dash='5 4'))
    p.append(text(lo, ax_y-104, 'min', size=12, bold=True, color=POS))
    p.append(text(hi, ax_y-104, 'max', size=12, bold=True, color=POS))

    # 256 поділок int8 під віссю
    grid_y = ax_y+58
    p.append(text(380, grid_y-8, '256 рівнів int8 розкладають РІВНО на цей діапазон', size=12, color=INK))
    for i in range(33):
        x = lo + i*(2*span/32)
        p.append(line(x, grid_y, x, grid_y+14, color=FIELD, sw=1.0))
    p.append(line(lo, grid_y+14, hi, grid_y+14, color=FIELD, sw=1.6))
    p.append(text(lo-4, grid_y+30, '-128', size=10, color=FIELD, anchor='middle'))
    p.append(text(hi+4, grid_y+30, '+127', size=10, color=FIELD, anchor='middle'))

    # Висновок-рамка
    b, w, h = textbox(380, 330,
                      'Замало даних → межі вузькі → реальні піки в польоті обрізаються (clip).\n'
                      'Дані не з тієї задачі → межі завеликі → поділки грубі, точність тоне.',
                      size=11, fill='#fdf6e3', stroke=MUTED)
    p.append(b)
    render(os.path.join(IMG, 'calibration-range.svg'), W, H, *p)


# ── Фігура 4 (для hist-tflite-litert): формат відв'язується від рамки ────────
def fig_tflite_timeline():
    W, H = 820, 470
    p = []
    p.append(text(W/2, 26, 'Як .tflite відв\'язувався від TensorFlow', size=17, bold=True))

    # Вертикальна вісь часу зліва
    ax_x = 150
    top, bot = 70, 380
    p.append(line(ax_x, top, ax_x, bot, color=INK, sw=2))
    p.append(arrow(ax_x, bot, ax_x, bot+14, color=INK, sw=2))

    # Віхи: (рік, заголовок, опис, колір)
    rows = [
        (top+0,   '2017', 'TFLite дебютує під TensorFlow.\nФормат .tflite = FlatBuffer; читати\nвмієш лише з TensorFlow.', NEG),
        (top+105, '2020-2023', 'Конвертери вчаться брати моделі\nз PyTorch, JAX, Keras. Формат той\nсамий — а рамка вже не одна.', MUTED),
        (top+210, '4 вер. 2024', 'Перейменування на LiteRT (Lite\nRuntime). Назва нарешті збіглася\nз дійсністю: рушій багаторамковий.', POS),
        (top+300, 'після', 'Розширення .tflite лишилось,\nстарі файли читаються, продакшн\nне зламався. Змінилась вивіска.', FIELD),
    ]
    for y, year, body, col in rows:
        p.append(circle(ax_x, y+22, 7, fill=col, stroke=col, sw=1))
        p.append(text(ax_x-14, y+27, year, size=12, bold=True, color=col, anchor='end'))
        b, w, h = textbox(ax_x+220, y+28, body, size=11, fill=FILL, stroke=col, min_w=380)
        p.append(b)

    p.append(text(W/2, bot+44, 'Файл не змінився ні разу — змінювалося тільки те, ЗВІДКИ він міг прийти.',
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, 'tflite-litert-timeline.svg'), W, H, *p)


# ── Фігура 5 (для hist-tflite-litert): три імені після 2024 ──────────────────
def fig_brand_split():
    W, H = 780, 360
    p = []
    p.append(text(W/2, 26, 'Що як зветься після 2024-го', size=17, bold=True))

    # Корінь — TensorFlow (лишається)
    b, w, h = textbox(W/2, 78, 'TensorFlow\n(велика рамка — НЕ перейменована)', size=12,
                      fill='#eaf0fd', stroke=NEG, bold=True, min_w=340)
    p.append(b)

    # Дві гілки вниз: LiteRT (телефон/борт) і LiteRT for MCU
    y2 = 200
    b, w, h = textbox(230, y2, 'LiteRT\n(колишній TensorFlow Lite)\nтелефони, борт, GPU/NPU', size=12,
                      fill='#fdf6e3', stroke=POS, bold=True, min_w=300)
    p.append(b)
    b, w, h = textbox(560, y2, 'LiteRT for Microcontrollers\n(колишній TFLite Micro)\nчип без ОС, кілобайти', size=12,
                      fill='#eafaf1', stroke=FIELD, bold=True, min_w=300)
    p.append(b)

    p.append(arrow(W/2-70, 98, 250, y2-30, color=INK, sw=1.6))
    p.append(arrow(W/2+70, 98, 540, y2-30, color=INK, sw=1.6))

    # Спільний знаменник унизу
    b, w, h = textbox(W/2, 300, 'обидві читають той самий файл .tflite (FlatBuffer)', size=12,
                      fill=BG, stroke=MUTED, min_w=440)
    p.append(b)
    p.append(arrow(230, y2+34, W/2-90, 282, color=MUTED, sw=1.4))
    p.append(arrow(560, y2+34, W/2+90, 282, color=MUTED, sw=1.4))

    render(os.path.join(IMG, 'litert-brand-split.svg'), W, H, *p)


# ── Фігура (proj): стенд перевірки — спільний вхід у дві гілки + вердикт ─────
def fig_validation_bench():
    W, H = 820, 470
    p = []
    p.append(text(W/2, 26, 'Стенд перевірки: один набір — дві гілки — вердикт', size=17, bold=True))

    # Спільний тестовий набір
    b, w, h = textbox(110, 145, 'спільний\nтестовий\nнабір\n(N кадрів)', size=12,
                      fill='#fdf6e3', stroke=MUTED, bold=True, min_w=150)
    p.append(b)

    # Гілка А — оригінальна float-модель (еталон)
    p.append(rect(280, 70, 250, 70, fill='#eaf0fd', stroke=NEG, sw=1.6, rx=10))
    p.append(text(405, 94, 'ОРИГІНАЛ (float32)', size=12, bold=True, color=NEG))
    p.append(text(405, 116, 'еталонний вихід ref[i]', size=11, color=INK))

    # Гілка Б — експортований .tflite через ТОЙ САМИЙ рушій
    p.append(rect(280, 180, 250, 70, fill='#eafaf1', stroke=FIELD, sw=1.6, rx=10))
    p.append(text(405, 204, 'ЕКСПОРТ .tflite (int8)', size=12, bold=True, color=FIELD))
    p.append(text(405, 226, 'той самий рушій → lite[i]', size=11, color=INK))

    p.append(arrow(186, 120, 278, 105, color=NEG, sw=1.6))
    p.append(arrow(186, 160, 278, 215, color=FIELD, sw=1.6))

    # Вузол метрик
    p.append(rect(580, 118, 215, 124, fill=FILL, stroke=INK, sw=1.6, rx=10))
    p.append(text(687, 140, 'МЕТРИКА РОЗБІЖНОСТІ', size=11, bold=True, color=INK))
    p.append(mtext(687, 162,
                   'макс |ref − lite|\nсереднє |ref − lite|\nзбіг класу-переможця\nпадіння точності',
                   size=11, color=INK))
    p.append(arrow(532, 105, 578, 150, color=NEG, sw=1.4))
    p.append(arrow(532, 215, 578, 185, color=FIELD, sw=1.4))

    # Вердикт — дві гілки
    gy = 330
    p.append(text(W/2, gy-22, 'Автоматичний вердикт за порогом', size=13, bold=True))
    b, w, h = textbox(250, gy+30, 'розбіжність ≤ поріг\nі точність не впала\n→ ПРОШИВАТИ', size=12,
                      fill='#eafaf1', stroke=FIELD, bold=True, min_w=250)
    p.append(b)
    b, w, h = textbox(580, gy+30, 'розбіжність > поріг\nабо точність впала\n→ РОЗБИРАТИСЯ', size=12,
                      fill='#fdecea', stroke=POS, bold=True, min_w=250)
    p.append(b)
    p.append(arrow(665, 244, 300, gy+2, color=FIELD, sw=1.4))
    p.append(arrow(715, 244, 560, gy+2, color=POS, sw=1.4))

    p.append(text(W/2, 448,
                  'Ловиться на столі, поки апарат ще не злетів — найдешевше місце спіймати тиху похибку.',
                  size=11, italic=True, color=MUTED))
    render(os.path.join(IMG, 'validation-bench.svg'), W, H, *p)


# ── Фігура (proj): дві осі розбіжності — амплітуда виходу vs саме рішення ────
def fig_two_axes():
    W, H = 760, 410
    p = []
    p.append(text(W/2, 26, 'Дві різні розбіжності: число виходу і саме рішення', size=16, bold=True))

    # Ліва панель — амплітуда
    p.append(rect(40, 56, 330, 320, fill='#f7f9fc', stroke=NEG, sw=1.4, rx=10))
    p.append(text(205, 80, 'ВІСЬ 1 — амплітуда виходу', size=13, bold=True, color=NEG))
    p.append(text(205, 100, '|ref − lite| на кожному виході', size=11, color=MUTED))
    ax = 190
    p.append(line(70, ax+40, 340, ax+40, color=INK, sw=1.4))
    p.append(circle(150, ax+40, 5, fill=NEG, stroke=NEG))
    p.append(text(150, ax+24, 'ref 0.92', size=11, color=NEG))
    p.append(circle(178, ax+40, 5, fill=FIELD, stroke=FIELD))
    p.append(text(200, ax+62, 'lite 0.90', size=11, color=FIELD))
    p.append(text(205, ax+98, 'Δ = 0.02 — мало', size=12, bold=True, color=INK))
    p.append(mtext(205, ax+122,
                   'але це ще НЕ вирок:\nважить, чи Δ перекинув\nрішення на сусідній клас',
                   size=11, color=MUTED))

    # Права панель — рішення
    p.append(rect(390, 56, 330, 320, fill='#f7fcf9', stroke=FIELD, sw=1.4, rx=10))
    p.append(text(555, 80, 'ВІСЬ 2 — клас-переможець', size=13, bold=True, color=FIELD))
    p.append(text(555, 100, 'argmax(ref) == argmax(lite)?', size=11, color=MUTED))
    base = 280
    p.append(text(467, 132, 'оригінал', size=11, color=NEG))
    p.append(rect(440, base-70, 24, 70, fill='#cfe3f7', stroke=NEG, sw=1)); p.append(text(452, base+16, 'A', size=10))
    p.append(rect(472, base-40, 24, 40, fill='#cfe3f7', stroke=NEG, sw=1)); p.append(text(484, base+16, 'B', size=10))
    p.append(text(645, 132, 'експорт', size=11, color=FIELD))
    p.append(rect(610, base-64, 24, 64, fill='#c7eed8', stroke=FIELD, sw=1)); p.append(text(622, base+16, 'A', size=10))
    p.append(rect(642, base-44, 24, 44, fill='#c7eed8', stroke=FIELD, sw=1)); p.append(text(654, base+16, 'B', size=10))
    p.append(text(555, base+46, 'A виграв в обох → збіг ✔', size=12, bold=True, color=INK))
    p.append(text(555, base+66, 'саме це й вирішує долю', size=11, color=MUTED))

    render(os.path.join(IMG, 'two-axes.svg'), W, H, *p)


if __name__ == '__main__':
    fig_pipeline()
    fig_interchange()
    fig_calibration()
    fig_tflite_timeline()
    fig_brand_split()
    fig_validation_bench()
    fig_two_axes()
    print('figs done')
