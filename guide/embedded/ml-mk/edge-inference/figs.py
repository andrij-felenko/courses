# -*- coding: utf-8 -*-
"""Фігури до теми «Інференс на пристрої (Edge AI)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Інференс як прошивкова процедура: разове налаштування vs цикл ──────────
def fig_pipeline():
    W, H = 760, 430
    els = []
    # blob -> завантаження
    b, bw, bh = textbox(120, 70, ".tflite\n(граф + ваги int8)", size=13, bold=True,
                        fill="#eef2f7", stroke=NEG, min_w=170)
    els.append(b)

    # Разовий блок (один раз при старті)
    setup_x, setup_y, setup_w, setup_h = 40, 120, 300, 130
    els.append(rect(setup_x, setup_y, setup_w, setup_h, fill="#f0f7f0", stroke=FIELD, sw=1.6))
    els.append(text(setup_x + setup_w / 2, setup_y + 22, "ОДИН РАЗ при старті", size=13, bold=True, color=FIELD))
    s1, _, _ = textbox(setup_x + setup_w / 2, setup_y + 55, "розібрати модель\n(resolver, ops)", size=11, fill=BG, stroke=LINE, min_w=180)
    els.append(s1)
    s2, _, _ = textbox(setup_x + setup_w / 2, setup_y + 100, "AllocateTensors():\nрозкласти арену в RAM", size=11, fill=BG, stroke=LINE, min_w=220)
    els.append(s2)

    # Цикл (на кожен кадр)
    loop_x, loop_y, loop_w, loop_h = 410, 120, 320, 250
    els.append(rect(loop_x, loop_y, loop_w, loop_h, fill="#fdf3f2", stroke=POS, sw=1.6))
    els.append(text(loop_x + loop_w / 2, loop_y + 22, "НА КОЖЕН КАДР (Invoke)", size=13, bold=True, color=POS))
    i1, _, _ = textbox(loop_x + loop_w / 2, loop_y + 55, "вхід → input-тензор (int8)", size=11, fill=BG, stroke=LINE, min_w=230)
    els.append(i1)
    i2, _, _ = textbox(loop_x + loop_w / 2, loop_y + 110, "граф int8-операцій\nшар за шаром у топ-порядку", size=11, fill="#eef2f7", stroke=NEG, min_w=250)
    els.append(i2)
    i3, _, _ = textbox(loop_x + loop_w / 2, loop_y + 165, "output-тензор (int8)", size=11, fill=BG, stroke=LINE, min_w=230)
    els.append(i3)
    i4, _, _ = textbox(loop_x + loop_w / 2, loop_y + 215, "деквантувати → число", size=11, fill="#f0f7f0", stroke=FIELD, min_w=230)
    els.append(i4)

    # стрілки
    els.append(arrow(120, 92, 120, 118))                       # blob -> setup
    els.append(arrow(setup_x + setup_w, setup_y + setup_h / 2, loop_x, loop_y + setup_h / 2))  # setup -> loop
    # цикл назад (повтор)
    els.append(line(loop_x + loop_w + 5, loop_y + 55, loop_x + loop_w + 25, loop_y + 55, color=POS, sw=1.6))
    els.append(line(loop_x + loop_w + 25, loop_y + 55, loop_x + loop_w + 25, loop_y + 165, color=POS, sw=1.6))
    els.append(arrow(loop_x + loop_w + 25, loop_y + 165, loop_x + loop_w + 5, loop_y + 165, color=POS))
    els.append(text(loop_x + loop_w + 18, loop_y + 110, "знов", size=10, color=POS, anchor="start"))

    els.append(text(W / 2, H - 14, "Граф і ваги — сталі; «навчання» вже позаду. Кожен Invoke — детермінований прохід.",
                    size=12, color=MUTED))
    render(os.path.join(IMG, "inference-pipeline.svg"), W, H, *els,
           title="Інференс на чипі: налаштувати раз, викликати на кожен кадр")


# ── 2. Карта пам'яті: ваги у Flash, активації в арені (RAM) ──────────────────
def fig_memory_map():
    W, H = 720, 400
    els = []
    col_w = 250
    fx, rx = 80, 400
    top, bot = 80, 350

    # FLASH
    els.append(text(fx + col_w / 2, top - 22, "FLASH (нелетка, тільки читання)", size=13, bold=True, color=NEG))
    # код
    els.append(rect(fx, top, col_w, 70, fill="#eef2f7", stroke=NEG, sw=1.5))
    els.append(text(fx + col_w / 2, top + 40, "код прошивки", size=12))
    # ваги (велике)
    els.append(rect(fx, top + 80, col_w, 190, fill="#dbe6f7", stroke=NEG, sw=1.8))
    els.append(mtext(fx + col_w / 2, top + 150, ["ВАГИ МОДЕЛІ (int8)", "сталі, лежать на місці,", "читаються прямо звідси"], size=12, bold=True))
    els.append(text(fx + col_w / 2, top + 250, "найбільший шматок", size=11, color=MUTED))

    # RAM
    els.append(text(rx + col_w / 2, top - 22, "RAM (летка, читання/запис)", size=13, bold=True, color=POS))
    els.append(rect(rx, top, col_w, 55, fill="#f4f6f8", stroke=LINE, sw=1.5))
    els.append(text(rx + col_w / 2, top + 32, "стек і купа прошивки", size=12))
    # арена
    els.append(rect(rx, top + 65, col_w, 205, fill="#fdecea", stroke=POS, sw=1.8))
    els.append(mtext(rx + col_w / 2, top + 130, ["ТЕНЗОРНА АРЕНА", "активації між шарами +", "робочі буфери", "(перезаписується щоразу)"], size=12, bold=True))
    els.append(text(rx + col_w / 2, top + 250, "її розмір ти задаєш сам", size=11, color=MUTED))

    # стрілка читання ваг у обчислення
    els.append(arrow(fx + col_w, top + 175, rx, top + 150, color=INK))
    els.append(text((fx + col_w + rx) / 2, top + 150, "MAC-и", size=11, color=INK))

    els.append(text(W / 2, H - 16, "Ваги переживають вимкнення живлення у Flash; арену чіп ліпить у RAM наново після кожного скидання.",
                    size=12, color=MUTED))
    render(os.path.join(IMG, "memory-map.svg"), W, H, *els,
           title="Де живуть байти моделі: Flash тримає ваги, RAM — арену")


# ── 3. Інференс у профілі споживання: латентність = ширина активного блоку ────
def fig_energy_block():
    W, H = 740, 380
    els = []
    base = 300
    left = 70
    span = 600
    # вісь часу
    els.append(line(left, base, left + span, base, color=INK, sw=1.6))
    els.append(text(left + span, base + 20, "час", size=12, color=MUTED, anchor="end"))
    els.append(text(left - 8, 80, "струм", size=12, color=MUTED, anchor="end"))

    def block(x, w, top, fill, stroke, label):
        out = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
               'fill-opacity="0.30" stroke="%s" stroke-width="1.6"/>'
               % (x, top, w, base - top, fill, stroke))
        out += text(x + w / 2, top - 8, label, size=10, color=stroke)
        return out

    # сон
    els.append(line(left, base - 6, left + 90, base - 6, color=NEG, sw=2))
    els.append(text(left + 45, base - 14, "сон", size=10, color=NEG))
    # пробудження + вимір
    els.append(block(left + 90, 60, base - 70, MUTED, LINE, "вимір"))
    # ІНФЕРЕНС (широкий блок)
    els.append(block(left + 150, 150, base - 130, POS, POS, "ІНФЕРЕНС (Invoke)"))
    els.append(text(left + 225, base - 60, "латентність =", size=10, color=POS))
    els.append(text(left + 225, base - 46, "ширина блоку", size=10, color=POS))
    # передача
    els.append(block(left + 300, 70, base - 180, NEG, NEG, "радіо"))
    # сон далі
    els.append(line(left + 370, base - 6, left + span, base - 6, color=NEG, sw=2))

    # та сама задача швидше (CMSIS-NN / int8): вужчий блок, нижче заряд
    els.append(line(left + 150, base - 130, left + 150, base + 14, color=POS, sw=1, dash="3,3"))
    els.append(line(left + 215, base - 130, left + 215, base + 14, color=FIELD, sw=1, dash="3,3"))
    els.append(arrow(left + 300, base + 30, left + 220, base + 30, color=FIELD))
    els.append(text(left + 360, base + 34, "пришвидшив Invoke → вужче → менше заряду за цикл",
                    size=11, color=FIELD, anchor="start"))

    els.append(text(W / 2, H - 16, "Площа блоку інференсу (струм × латентність) лягає в заряд циклу — той самий, з якого рахують час життя батареї.",
                    size=11, color=MUTED))
    render(os.path.join(IMG, "energy-block.svg"), W, H, *els,
           title="Інференс у профілі струму: латентність стає зарядом")


# ── 4. Бойовий харнес: запобіжники старту → вимірюваний прохід ────────────────
def fig_harness_guards():
    """Вставка proj: повний шлях бойового харнеса двома колонками — ланцюг
    запобіжників на старті (ліворуч) і вимірюваний прохід на кожен кадр
    (праворуч). Кожна перевірка — місце впасти раніше, ніж чіп піде у HardFault."""
    W, H = 780, 470
    els = []
    lcx, rcx = 215, 565           # центри колонок
    box_w = 320
    top = 64

    els.append(text(lcx, 30, "model_init() — ОДИН РАЗ", size=14, bold=True, color=FIELD))
    els.append(text(rcx, 30, "model_run(frame) — НА КОЖЕН КАДР", size=13, bold=True, color=POS))
    els.append(line(390, 50, 390, H - 80, color=LINE, sw=1, dash="2,5"))

    steps = [
        ("alignas(16) арена", "інакше векторні ядра → HardFault", "#eef2f7", NEG),
        ("GetModel()->version()\n== TFLITE_SCHEMA_VERSION?", "стара схема → стоп", "#fdf3f2", POS),
        ("резолвер: усі ops моделі", "забута op → Invoke = kTfLiteError", "#eef2f7", NEG),
        ("AllocateTensors() == kTfLiteOk?", "замала арена → стоп", "#fdf3f2", POS),
        ("arena_used_bytes()\n+ запас < kArenaSize?", "впритул → роздути зараз", "#f0f7f0", FIELD),
    ]
    y = top
    lcenters = []
    for label, note, fill, stroke in steps:
        b, bw, bh = textbox(lcx, y + 22, label, size=11, bold=True, fill=fill,
                            stroke=stroke, min_w=box_w)
        els.append(b)
        els.append(text(lcx, y + 22 + bh / 2 + 12, note, size=9, color=MUTED))
        lcenters.append((y + 22, bh))
        y += 72
    for i in range(len(steps) - 1):
        yc, bh = lcenters[i]
        els.append(arrow(lcx, yc + bh / 2, lcx, lcenters[i + 1][0] - bh / 2 + 2, color=FIELD))

    run = [
        ("t0 = DWT->CYCCNT", "#f4f6f8", LINE),
        ("кадр давача → int8\nза input->params", "#eef2f7", NEG),
        ("Invoke() == kTfLiteOk?", "#fdf3f2", POS),
        ("деквантувати вихід", "#f0f7f0", FIELD),
        ("такти = CYCCNT − t0", "#f4f6f8", LINE),
    ]
    y = top
    rcenters = []
    for label, fill, stroke in run:
        b, bw, bh = textbox(rcx, y + 22, label, size=11, bold=True, fill=fill,
                            stroke=stroke, min_w=300)
        els.append(b)
        rcenters.append((y + 22, bh, bw))
        y += 72
    for i in range(len(run) - 1):
        yc, bh, _ = rcenters[i]
        els.append(arrow(rcx, yc + bh / 2, rcx, rcenters[i + 1][0] - bh / 2 + 2, color=POS))

    # дужка «вимірюваний інтервал» праворуч від колонки кадру
    bx = rcx + 300 / 2 + 18
    y0, y1 = rcenters[0][0], rcenters[-1][0]
    els.append(line(bx, y0, bx, y1, color="#8e44ad", sw=2))
    els.append(line(bx - 8, y0, bx, y0, color="#8e44ad", sw=2))
    els.append(line(bx - 8, y1, bx, y1, color="#8e44ad", sw=2))
    els.append(text(bx - 4, (y0 + y1) / 2, "латентність", size=10, color="#8e44ad",
                    anchor="middle"))

    # один блок помилки знизу під колонкою старту
    fy = lcenters[-1][0] + lcenters[-1][1] / 2 + 40
    fb, fbw, fbh = textbox(lcx, fy, "будь-яке «ні» → повернути false,\nдіагностика в MicroPrintf, далі НЕ йти",
                           size=10, bold=True, fill="#fdecea", stroke=POS, min_w=300)
    els.append(fb)
    els.append(arrow(lcx, lcenters[-1][0] + lcenters[-1][1] / 2 + 2, lcx, fy - fbh / 2, color=POS))

    render(os.path.join(IMG, "harness-guards.svg"), W, H, *els,
           title="Бойовий харнес: ланцюг запобіжників на старті, вимірюваний прохід на кадр")


# ── 5. Пастка масштабу входу: те саме фізичне число → різний int8 ─────────────
def fig_scale_mismatch():
    """Чому не можна «просто запхати» сирий байт давача у вхідний тензор: модель
    чекає int8 у СВОЄМУ масштабі (input->params), а не в одиницях давача."""
    W, H = 760, 360
    els = []
    # фізичне число
    src, sw_, sh_ = textbox(110, 90, "кадр давача\n0.65 g\n(сире АЦП = 166)", size=12, bold=True,
                            fill="#f4f6f8", stroke=LINE, min_w=150)
    els.append(src)

    # гілка ПРАВИЛЬНО
    els.append(text(470, 40, "ПРАВИЛЬНО: масштаб моделі", size=12, bold=True, color=FIELD))
    r1, w1, h1 = textbox(360, 90, "scale = 0.0078\nzero_point = −1", size=11,
                         fill="#f0f7f0", stroke=FIELD, min_w=150)
    els.append(r1)
    r2, w2, h2 = textbox(600, 90, "q = 0.65/0.0078 + (−1)\n= 82  (int8)", size=11, bold=True,
                         fill="#f0f7f0", stroke=FIELD, min_w=170)
    els.append(r2)
    els.append(arrow(110 + sw_ / 2, 75, 360 - w1 / 2, 80, color=FIELD))
    els.append(arrow(360 + w1 / 2, 90, 600 - w2 / 2, 90, color=FIELD))
    els.append(text(560, 145, "модель бачить те, на чому вчилась → правильний клас",
                    size=10, color=FIELD))

    # гілка ПОМИЛКА
    els.append(text(470, 215, "ПОМИЛКА: «просто сирий байт»", size=12, bold=True, color=POS))
    e1, ew1, eh1 = textbox(360, 265, "взяли АЦП як є", size=11,
                           fill="#fdecea", stroke=POS, min_w=150)
    els.append(e1)
    e2, ew2, eh2 = textbox(600, 265, "q = 166 → переповнення\nint8 → −90  (сміття)", size=11, bold=True,
                           fill="#fdecea", stroke=POS, min_w=170)
    els.append(e2)
    els.append(arrow(110 + sw_ / 2, 105, 360 - ew1 / 2, 255, color=POS))
    els.append(arrow(360 + ew1 / 2, 265, 600 - ew2 / 2, 265, color=POS))
    els.append(text(560, 320, "те саме фізичне число — інший код → модель «бачить» інше",
                    size=10, color=POS))

    render(os.path.join(IMG, "scale-mismatch.svg"), W, H, *els,
           title="Масштаб входу: те саме фізичне число дає різний int8")


# ── 6. Розклад однієї MAC: цілий кістяк + самотній дробовий M (math) ──────────
def fig_quant_mac():
    """Вставка math: одна MAC-операція розпадається на цілу частину (різниці int8,
    добутки, накопичення в int32, int32-зсув) і єдиний дробовий множник M=S1S2/S3."""
    W, H = 780, 360
    els = []
    # входи у своїх сітках
    a, aw, ah = textbox(110, 80, "вхід q₁\nсітка S₁, Z₁", size=12, bold=True,
                        fill="#eef2f7", stroke=NEG, min_w=150)
    els.append(a)
    b, bw, bh = textbox(110, 175, "вага q₂\nсітка S₂, Z₂", size=12, bold=True,
                        fill="#dbe6f7", stroke=NEG, min_w=150)
    els.append(b)

    # ціла частина (зелена дужка)
    gx, gy, gw, gh = 230, 50, 320, 200
    els.append(rect(gx, gy, gw, gh, fill="#f0f7f0", stroke=FIELD, sw=1.8))
    els.append(text(gx + gw / 2, gy + 22, "ЦІЛИЙ КІСТЯК (за такт)", size=12, bold=True, color=FIELD))
    s1, _, _ = textbox(gx + gw / 2, gy + 60, "(q₁−Z₁)·(q₂−Z₂)\nусе int8 → int", size=11,
                       fill=BG, stroke=LINE, min_w=200)
    els.append(s1)
    s2, _, _ = textbox(gx + gw / 2, gy + 120, "Σ … + зсув(int32)\n→ int32-акумулятор", size=11,
                       fill=BG, stroke=LINE, min_w=220)
    els.append(s2)

    # самотній дробовий M (червона рамка)
    m, mw, mh = textbox(670, 130, "× M = S₁S₂/S₃\n(єдиний дріб)\n→ int8-вихід q₃", size=12, bold=True,
                        fill="#fdecea", stroke=POS, min_w=160)
    els.append(m)

    els.append(arrow(110 + aw / 2, 80, gx, 95))
    els.append(arrow(110 + bw / 2, 175, gx, 175))
    els.append(arrow(gx + gw, gy + gh / 2, 670 - mw / 2, 130, color=POS))

    els.append(text(W / 2, H - 16,
                    "Зелене — цілі множення-накопичення в int32 (дешево); червоне — самотній дробовий M.",
                    size=11, color=MUTED))
    render(os.path.join(IMG, "quant-mac.svg"), W, H, *els,
           title="Одна MAC: цілий кістяк у int32 + самотній дробовий множник")


# ── 7. M = 2⁻ⁿ·M0: дробовий множник двома цілочисельними діями (math) ─────────
def fig_requant_fixedpoint():
    """Як дробовий M спрацьовує без FPU: нормування M=2⁻ⁿ·M0, тоді ціле множення
    на заморожену сталу M0·2³¹ зі зсувом 31, і арифметичний зсув праворуч на n."""
    W, H = 760, 350
    els = []
    top, _, _ = textbox(W / 2, 70, "дробовий M ∈ (0, 1)  —  відомий офлайн", size=13, bold=True,
                        fill="#fdecea", stroke=POS, min_w=360)
    els.append(top)
    norm, nw, nh = textbox(W / 2, 140, "нормуємо:  M = 2⁻ⁿ · M₀,   M₀ ∈ [0.5, 1)", size=13, bold=True,
                           fill="#f4f6f8", stroke=LINE, min_w=380)
    els.append(norm)
    els.append(arrow(W / 2, 88, W / 2, 140 - nh / 2))

    # дві гілки
    l, lw, lh = textbox(220, 250, "M₀ → ціле:\nM₀_fixed ≈ M₀·2³¹\nмнож. ×, зсув >> 31", size=12, bold=True,
                        fill="#f0f7f0", stroke=FIELD, min_w=230)
    els.append(l)
    r, rw, rh = textbox(560, 250, "2⁻ⁿ → зсув:\nарифметичний\n>> n біт", size=12, bold=True,
                        fill="#f0f7f0", stroke=FIELD, min_w=230)
    els.append(r)
    els.append(arrow(W / 2 - 60, 140 + nh / 2, 220, 250 - lh / 2, color=FIELD))
    els.append(arrow(W / 2 + 60, 140 + nh / 2, 560, 250 - rh / 2, color=FIELD))

    els.append(text(W / 2, H - 16, "Жодного float — лише цілі множення й зсуви.",
                    size=12, color=MUTED))
    render(os.path.join(IMG, "requant-fixedpoint.svg"), W, H, *els,
           title="Переквантування: дробовий M = 2⁻ⁿ·M₀ двома цілими діями")


# ── 8. Per-tensor проти per-axis: одна сітка vs сітка на канал (math) ─────────
def fig_per_tensor_vs_axis():
    """Чому per-axis рятує тонкі фільтри: одна спільна сітка душить тихий фільтр,
    окрема сітка на канал дає кожному всі 256 рівнів."""
    W, H = 780, 380
    els = []

    def grid(cx, cy, span, used_lo, used_hi, label, color):
        # вісь сітки -128..127 та зайнята ділянка
        out = line(cx - span / 2, cy, cx + span / 2, cy, color=INK, sw=1.6)
        # позначки кінців
        out += text(cx - span / 2, cy + 18, "−128", size=9, color=MUTED)
        out += text(cx + span / 2, cy + 18, "127", size=9, color=MUTED)
        # зайнята фільтром ділянка
        x0 = cx - span / 2 + span * (used_lo + 128) / 255.0
        x1 = cx - span / 2 + span * (used_hi + 128) / 255.0
        out += ('<rect x="%.1f" y="%.1f" width="%.1f" height="14" fill="%s" '
                'fill-opacity="0.35" stroke="%s" stroke-width="1.4"/>'
                % (x0, cy - 7, max(x1 - x0, 3), color, color))
        out += text(cx, cy - 16, label, size=10, color=color)
        return out

    # ЛІВОРУЧ: per-tensor (одна сітка)
    els.append(text(200, 50, "PER-TENSOR: одна сітка на тензор", size=12, bold=True, color=POS))
    els.append(grid(200, 130, 300, -120, 120, "гучний фільтр ±2.0 → усі рівні", POS))
    els.append(grid(200, 210, 300, -2, 2, "тихий фільтр ±0.02 → 3 рівні (гине)", POS))
    els.append(text(200, 270, "масштаб мусить покрити найгучніший →", size=10, color=MUTED))
    els.append(text(200, 286, "тихий фільтр майже без роздільності", size=10, color=MUTED))

    # ПРАВОРУЧ: per-axis (сітка на канал)
    els.append(text(580, 50, "PER-AXIS: сітка на кожен канал", size=12, bold=True, color=FIELD))
    els.append(grid(580, 130, 300, -118, 118, "гучний: свій S → усі рівні", FIELD))
    els.append(grid(580, 210, 300, -118, 118, "тихий: свій дрібний S → усі рівні", FIELD))
    els.append(text(580, 270, "кожному каналу власний масштаб →", size=10, color=MUTED))
    els.append(text(580, 286, "обидва беруть усі 256 рівнів", size=10, color=MUTED))

    els.append(line(390, 70, 390, 300, color=LINE, sw=1, dash="2,5"))
    els.append(text(W / 2, H - 14,
                    "Вісь — лише вихідні канали: тільки там масштаб ваг спільний усередині MAC-суми.",
                    size=11, color=MUTED))
    render(os.path.join(IMG, "per-tensor-vs-axis.svg"), W, H, *els,
           title="Per-tensor проти per-axis: одна сітка душить тихі фільтри")


if __name__ == "__main__":
    fig_pipeline()
    fig_memory_map()
    fig_energy_block()
    fig_harness_guards()
    fig_scale_mismatch()
    fig_quant_mac()
    fig_requant_fixedpoint()
    fig_per_tensor_vs_axis()
    print("OK: 8 фігур у", IMG)
