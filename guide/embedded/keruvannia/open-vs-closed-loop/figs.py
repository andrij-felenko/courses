# -*- coding: utf-8 -*-
"""Фігури теми «Відкритий і замкнений контур». Запуск: python figs.py → ./img/*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: розімкнений ланцюг — без шляху назад ────────────────────────────
# Завдання → регулятор → виконавчий орган → об'єкт → вихід. Жодної стрілки назад:
# система виконує план, але ніколи не дізнається свого результату.
def fig_open_loop():
    W, H = 720, 230
    parts = []
    cy = 118
    # центри блоків
    ctrl_x, act_x, plant_x = 175, 360, 545
    b1 = textbox(ctrl_x, cy, "регулятор", size=13, fill="#eef2f7", stroke=NEG, sw=1.8, min_w=120)[0]
    b2 = textbox(act_x, cy, "виконавчий\nорган", size=13, fill="#f6f4ec", stroke=MUTED, sw=1.6, min_w=130)[0]
    b3 = textbox(plant_x, cy, "об'єкт", size=13, fill="#eafaf1", stroke=FIELD, sw=1.8, min_w=120)[0]
    parts += [b1, b2, b3]
    # завдання r → регулятор
    parts.append(arrow(60, cy, ctrl_x - 60, cy, color=NEG, sw=2.0))
    parts.append(text(95, cy - 10, "завдання r", 11, NEG, "middle", bold=True))
    # регулятор → орган → об'єкт
    parts.append(arrow(ctrl_x + 60, cy, act_x - 65, cy, color=INK, sw=2.0))
    parts.append(arrow(act_x + 65, cy, plant_x - 60, cy, color=INK, sw=2.0))
    # об'єкт → вихід y
    parts.append(arrow(plant_x + 60, cy, 680, cy, color=FIELD, sw=2.0))
    parts.append(text(655, cy - 10, "вихід y", 11, FIELD, "middle", bold=True))
    # підпис-висновок
    parts.append(text(W / 2, 198, "немає шляху назад — система не дивиться на результат і не знає, чи досягла мети",
                      11, POS, "middle", bold=True))
    render(os.path.join(IMG, "open-loop.svg"), W, H, *parts,
           title="Розімкнений контур: діє за планом, не перевіряючи наслідків")


# ── Фігура 2: замкнений контур — анатомія зворотного зв'язку ──────────────────
# Завдання r → суматор (−) → регулятор → орган → об'єкт → вихід y → давач → назад
# на суматор. Різниця r−y (помилка) керує впливом; знак на вузлі — «−».
def fig_closed_loop():
    W, H = 720, 340
    parts = []
    cy = 120
    sum_x, ctrl_x, plant_x = 215, 385, 575
    # суматор
    parts.append(circle(sum_x, cy, 22, fill="#fff8e1", stroke="#f0b429", sw=2))
    parts.append(text(sum_x - 6, cy + 5, "−", 18, NEG, "middle", bold=True))
    parts.append(text(sum_x - 6, cy + 22, "+", 15, INK, "middle", bold=True))
    # блоки
    b2 = textbox(ctrl_x, cy, "регулятор", size=13, fill="#eef2f7", stroke=NEG, sw=1.8, min_w=120)[0]
    b3 = textbox(plant_x, cy, "об'єкт", size=13, fill="#eafaf1", stroke=FIELD, sw=1.8, min_w=120)[0]
    parts += [b2, b3]
    # завдання r → суматор
    parts.append(arrow(70, cy, sum_x - 24, cy, color=NEG, sw=2.0))
    parts.append(text(105, cy - 10, "завдання r", 11, NEG, "middle", bold=True))
    # суматор → регулятор (помилка e)
    parts.append(arrow(sum_x + 24, cy, ctrl_x - 60, cy, color=POS, sw=2.0))
    parts.append(text((sum_x + ctrl_x) / 2 + 6, cy - 10, "помилка e", 11, POS, "middle", bold=True))
    # регулятор → об'єкт (вплив u)
    parts.append(arrow(ctrl_x + 60, cy, plant_x - 60, cy, color=INK, sw=2.0))
    parts.append(text((ctrl_x + plant_x) / 2, cy - 10, "вплив u", 10, MUTED, "middle"))
    # об'єкт → вихід y (праворуч, потім униз і назад)
    out_y = cy + 110
    parts.append(arrow(plant_x + 60, cy, 678, cy, color=FIELD, sw=2.0))
    parts.append(text(655, cy - 10, "вихід y", 11, FIELD, "middle", bold=True))
    # відведення вниз від виходу
    parts.append(line(660, cy, 660, out_y, color=INK, sw=1.8))
    # давач у зворотному шляху
    sens = textbox(440, out_y, "давач", size=13, fill="#eef2f7", stroke=NEG, sw=1.8, min_w=110)[0]
    parts.append(sens)
    parts.append(arrow(660, out_y, 440 + 55, out_y, color=INK, sw=1.8))
    parts.append(arrow(440 - 55, out_y, sum_x, out_y, color=INK, sw=1.8))
    parts.append(line(sum_x, out_y, sum_x, cy + 24, color=INK, sw=1.8))
    parts.append(text((sum_x + 385) / 2 - 30, out_y - 10, "виміряний вихід", 10, MUTED, "middle"))
    # підпис-висновок
    parts.append(text(W / 2, H - 20,
                      "коло замкнене: різниця «завдання − вимір» жене помилку до нуля десятки разів на секунду",
                      11, INK, "middle"))
    render(os.path.join(IMG, "closed-loop.svg"), W, H, *parts,
           title="Замкнений контур: міряти → знайти різницю → впливати → міряти знову")


# ── Фігура 3: помилка e = r − y у часі ───────────────────────────────────────
# Завдання r — горизонталь; вихід y підходить до неї знизу; затінений проміжок
# між ними — помилка, що тане до нуля. Регулятор працює, поки e ≠ 0.
def fig_error_signal():
    W, H = 700, 340
    ox, oy = 90, 290
    aw, ah = 540, 230
    parts = []
    # осі
    parts.append(arrow(ox - 6, oy, ox + aw + 14, oy, color=MUTED, sw=1.3))
    parts.append(arrow(ox, oy + 6, ox, oy - ah - 8, color=MUTED, sw=1.3))
    parts.append(text(ox + aw + 8, oy + 18, "час", 11, MUTED, "end"))
    parts.append(text(ox + 2, oy - ah - 14, "величина", 11, MUTED, "middle"))
    # лінія завдання r
    r_y = oy - ah + 40
    parts.append(line(ox, r_y, ox + aw, r_y, color=MUTED, sw=1.6, dash="6 5"))
    parts.append(text(ox + aw - 2, r_y - 8, "завдання r", 11, MUTED, "end", bold=True))
    # крива виходу y (експоненційний підхід до r)
    pts = []
    y0 = oy - 8
    for i in range(121):
        t = i / 120.0
        val = (oy - r_y) * (1 - math.exp(-3.4 * t))
        pts.append((ox + t * aw, y0 - val))
    py = " ".join("%.1f,%.1f" % p for p in pts)
    # затінення помилки (між y та r) у першій третині
    band = ['%.1f,%.1f' % (ox, r_y)]
    cut = int(121 * 0.55)
    for i in range(cut):
        band.append('%.1f,%.1f' % pts[i])
    band.append('%.1f,%.1f' % (pts[cut - 1][0], r_y))
    parts.append('<polygon points="%s" fill="#fdecea" stroke="none" opacity="0.85"/>' % " ".join(band))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (py, NEG))
    parts.append(text(ox + aw - 4, y0 - (oy - r_y) + 18, "вихід y", 11, NEG, "end", bold=True))
    # стрілка-підпис помилки
    ex = ox + aw * 0.16
    parts.append(line(ex, oy - 8, ex, r_y, color=POS, sw=1.4, dash="3 3"))
    parts.append(text(ex + 8, (oy - 8 + r_y) / 2, "помилка e = r − y", 11, POS, "start", bold=True))
    # позначка «заспокоївся»
    parts.append(text(ox + aw * 0.8, r_y + 22, "e → 0: регулятор заспокоюється", 10, FIELD, "middle"))
    render(os.path.join(IMG, "error-signal.svg"), W, H, *parts,
           title="Помилка — різниця між бажаним і виміряним, що тане до нуля")


# ── Фігура 4: придушення збурення — розімкнене лишається збитим ───────────────
# Обидві системи тримають завдання; раптом збурення. Розімкнена просіла й
# лишилася; замкнена просіла, помітила помилку й вернулася до завдання.
def fig_disturbance_rejection():
    W, H = 700, 360
    ox, oy = 80, 300
    aw, ah = 560, 250
    parts = []
    # осі
    parts.append(arrow(ox - 6, oy, ox + aw + 14, oy, color=MUTED, sw=1.3))
    parts.append(arrow(ox, oy + 6, ox, oy - ah - 8, color=MUTED, sw=1.3))
    parts.append(text(ox + aw + 8, oy + 18, "час", 11, MUTED, "end"))
    parts.append(text(ox + 2, oy - ah - 14, "вихід", 11, MUTED, "middle"))
    # лінія завдання
    set_y = oy - ah + 50
    parts.append(line(ox, set_y, ox + aw, set_y, color=MUTED, sw=1.6, dash="6 5"))
    parts.append(text(ox + 6, set_y - 8, "завдання", 11, MUTED, "start", bold=True))
    # момент збурення
    dist_t = 0.4
    dx = ox + dist_t * aw
    parts.append(line(dx, oy, dx, oy - ah, color="#999999", sw=1.0, dash="2 4"))
    parts.append(arrow(dx, set_y - 70, dx, set_y - 18, color=INK, sw=1.8))
    parts.append(text(dx, set_y - 78, "збурення", 11, INK, "middle", bold=True))
    # обидві системи тримають завдання до збурення
    parts.append(line(ox, set_y, dx, set_y, color=INK, sw=2.4))
    # розімкнена: просіла й лишилася
    drop = 70
    op = [(dx, set_y)]
    for i in range(61):
        t = i / 60.0
        # швидке падіння і плато
        val = drop * (1 - math.exp(-7 * t))
        op.append((dx + t * (ox + aw - dx), set_y + val))
    pop = " ".join("%.1f,%.1f" % p for p in op)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (pop, POS))
    parts.append(text(ox + aw - 4, set_y + drop + 16, "розімкнене: лишається збитим", 11, POS, "end", bold=True))
    # замкнена: просіла й вернулася
    cl = [(dx, set_y)]
    for i in range(61):
        t = i / 60.0
        val = drop * math.exp(-5 * t) * math.cos(3.0 * t)
        cl.append((dx + t * (ox + aw - dx), set_y + max(val, -6)))
    pcl = " ".join("%.1f,%.1f" % p for p in cl)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (pcl, FIELD))
    parts.append(text(ox + aw - 4, set_y - 14, "замкнене: вертається до завдання", 11, FIELD, "end", bold=True))
    render(os.path.join(IMG, "disturbance-rejection.svg"), W, H, *parts,
           title="Збурення: розімкнене лишається збитим, замкнене вертається")


# ── Фігура 5: кермо як контур — фіксоване з'їжджає, замкнене тримає смугу ──────
# Дві смуги. Угорі (розімкнено): кермо застигле, траєкторія повзе зі смуги.
# Унизу (замкнено): водій виправляє, траєкторія коливається довкола центру.
def fig_steering_loop():
    W, H = 700, 360
    parts = []

    def lane(cy_lane, label, color, drift):
        f = []
        lx, lw = 70, 560
        top, bot = cy_lane - 46, cy_lane + 46
        # межі смуги
        f.append(line(lx, top, lx + lw, top, color=MUTED, sw=1.4))
        f.append(line(lx, bot, lx + lw, bot, color=MUTED, sw=1.4))
        # осьова
        f.append(line(lx, cy_lane, lx + lw, cy_lane, color="#cfcfcf", sw=1.0, dash="10 8"))
        # траєкторія
        pts = []
        for i in range(121):
            t = i / 120.0
            if drift:
                y = cy_lane + 70 * t          # неухильно з'їжджає вниз
            else:
                y = cy_lane + 16 * math.sin(10 * t)   # коливання довкола центру
            pts.append((lx + t * lw, y))
        pl = " ".join("%.1f,%.1f" % p for p in pts)
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (pl, color))
        f.append(text(lx + 4, top - 10, label, 12, color, "start", bold=True))
        return f

    parts += lane(110, "розімкнено: кермо застигле — машина з'їжджає зі смуги", POS, True)
    parts += lane(265, "замкнено: водій бачить відхилення й виправляє — тримає смугу", FIELD, False)
    render(os.path.join(IMG, "steering-loop.svg"), W, H, *parts,
           title="Кермо як контур: та сама дорога — різниця лише в погляді на результат")


# ── Фігура 6: дозування реакції — мляво повзе, різко розгойдується ────────────
# Крокова відповідь. М'який регулятор спокійно підходить; надто різкий
# перестрілює, вертається, знову перестрілює — розгойдується.
def fig_controller_tuning():
    W, H = 700, 340
    ox, oy = 90, 280
    aw, ah = 540, 220
    parts = []
    parts.append(arrow(ox - 6, oy, ox + aw + 14, oy, color=MUTED, sw=1.3))
    parts.append(arrow(ox, oy + 6, ox, oy - ah - 8, color=MUTED, sw=1.3))
    parts.append(text(ox + aw + 8, oy + 18, "час", 11, MUTED, "end"))
    parts.append(text(ox + 2, oy - ah - 14, "вихід", 11, MUTED, "middle"))
    # завдання
    set_y = oy - ah + 40
    parts.append(line(ox, set_y, ox + aw, set_y, color=MUTED, sw=1.6, dash="6 5"))
    parts.append(text(ox + aw - 2, set_y - 8, "завдання", 11, MUTED, "end", bold=True))
    amp = oy - set_y
    # м'який: повільний підхід без перельоту
    soft = []
    for i in range(121):
        t = i / 120.0
        val = amp * (1 - math.exp(-2.4 * t))
        soft.append((ox + t * aw, oy - val))
    ps = " ".join("%.1f,%.1f" % p for p in soft)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (ps, FIELD))
    parts.append(text(ox + aw - 4, set_y + 26, "м'який: повзе до завдання", 11, FIELD, "end", bold=True))
    # різкий: згасальне коливання з перельотом
    harsh = []
    for i in range(121):
        t = i / 120.0
        val = amp * (1 - math.exp(-1.6 * t) * math.cos(7.5 * t))
        harsh.append((ox + t * aw, oy - val))
    ph = " ".join("%.1f,%.1f" % p for p in harsh)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (ph, POS))
    parts.append(text(ox + aw * 0.30, set_y - 30, "різкий: перестрілює й розгойдується", 11, POS, "middle", bold=True))
    render(os.path.join(IMG, "controller-tuning.svg"), W, H, *parts,
           title="Між «мляво» і «вразнос»: знайти середину означає спроєктувати регулятор")

# ═══════════════════════════════════════════════════════════════════════════
#  ФІГУРИ ДЛЯ ДЕТАЛЬНОЇ ВЕРСІЇ (open-vs-closed-loop-d.md)
# ═══════════════════════════════════════════════════════════════════════════

# ── Д-фігура 1: повний контур із трьома входами r, d, n ──────────────────────
# Показує, де в контур входять завдання r, збурення d (на об'єкт) і шум n
# (на вимір). Три різні входи — три різні передавальні функції до виходу.
def figd_three_inputs():
    W, H = 760, 360
    parts = []
    cy = 130
    sum_x, ctrl_x, dsum_x, plant_x = 180, 320, 445, 560
    # суматор помилки
    parts.append(circle(sum_x, cy, 20, fill="#fff8e1", stroke="#f0b429", sw=2))
    parts.append(text(sum_x - 6, cy + 4, "−", 16, NEG, "middle", bold=True))
    parts.append(text(sum_x - 6, cy + 20, "+", 13, INK, "middle", bold=True))
    # регулятор
    b_ctrl = textbox(ctrl_x, cy, "C", size=15, fill="#eef2f7", stroke=NEG, sw=1.8, min_w=64)[0]
    parts.append(b_ctrl)
    # суматор збурення (d додається до впливу перед об'єктом)
    parts.append(circle(dsum_x, cy, 16, fill="#fdecea", stroke=POS, sw=1.8))
    parts.append(text(dsum_x - 5, cy + 4, "+", 13, INK, "middle", bold=True))
    parts.append(text(dsum_x - 5, cy - 8, "+", 12, POS, "middle", bold=True))
    # об'єкт
    b_plant = textbox(plant_x, cy, "G", size=15, fill="#eafaf1", stroke=FIELD, sw=1.8, min_w=64)[0]
    parts.append(b_plant)
    # завдання r → суматор
    parts.append(arrow(70, cy, sum_x - 22, cy, color=NEG, sw=2.0))
    parts.append(text(96, cy - 10, "завдання r", 11, NEG, "middle", bold=True))
    # суматор → C (помилка e)
    parts.append(arrow(sum_x + 22, cy, ctrl_x - 34, cy, color=POS, sw=2.0))
    parts.append(text((sum_x + ctrl_x) / 2 + 4, cy - 10, "e", 12, POS, "middle", bold=True))
    # C → dsum (вплив u)
    parts.append(arrow(ctrl_x + 34, cy, dsum_x - 18, cy, color=INK, sw=2.0))
    parts.append(text((ctrl_x + dsum_x) / 2, cy - 10, "u", 11, MUTED, "middle"))
    # dsum → G
    parts.append(arrow(dsum_x + 18, cy, plant_x - 36, cy, color=INK, sw=2.0))
    # збурення d зверху в dsum
    parts.append(arrow(dsum_x, cy - 66, dsum_x, cy - 18, color=POS, sw=2.0))
    parts.append(text(dsum_x, cy - 74, "збурення d", 11, POS, "middle", bold=True))
    # G → вихід y
    yline_x = 690
    parts.append(arrow(plant_x + 36, cy, yline_x, cy, color=FIELD, sw=2.0))
    parts.append(text(yline_x - 22, cy - 10, "вихід y", 11, FIELD, "middle", bold=True))
    # зворотний шлях: від виходу вниз, суматор шуму, назад у суматор помилки
    back_y = cy + 130
    parts.append(line(yline_x - 20, cy, yline_x - 20, back_y, color=INK, sw=1.8))
    # суматор шуму n у зворотному шляху
    nsum_x = 400
    parts.append(circle(nsum_x, back_y, 16, fill="#fdecea", stroke=POS, sw=1.8))
    parts.append(text(nsum_x - 5, back_y + 4, "+", 13, INK, "middle", bold=True))
    parts.append(text(nsum_x - 5, back_y - 8, "+", 12, POS, "middle", bold=True))
    parts.append(arrow(yline_x - 20, back_y, nsum_x + 18, back_y, color=INK, sw=1.8))
    # шум n знизу
    parts.append(arrow(nsum_x, back_y + 58, nsum_x, back_y + 18, color=POS, sw=2.0))
    parts.append(text(nsum_x, back_y + 72, "шум давача n", 11, POS, "middle", bold=True))
    # nsum → суматор помилки (виміряний вихід)
    parts.append(arrow(nsum_x - 18, back_y, sum_x, back_y, color=INK, sw=1.8))
    parts.append(line(sum_x, back_y, sum_x, cy + 20, color=INK, sw=1.8))
    parts.append(text((sum_x + nsum_x) / 2 - 6, back_y - 10, "y + n (вимір)", 10, MUTED, "middle"))
    render(os.path.join(IMG, "three-inputs.svg"), W, H, *parts,
           title="Три входи контуру: завдання r, збурення d, шум давача n")


# ── Д-фігура 2: чутливість S і доповняльна T залежно від частоти ─────────────
# S = 1/(1+L) мала на низьких частотах (контур давить збурення) і росте до 1
# угорі; T = L/(1+L) ≈ 1 унизу (стежить за завданням) і падає вгорі.
# Скрізь S + T = 1. Показуємо «водяний матрац»: горб S над одиницею.
def figd_sensitivity_curves():
    W, H = 720, 360
    ox, oy = 80, 300
    aw, ah = 590, 250
    parts = []
    parts.append(arrow(ox - 6, oy, ox + aw + 14, oy, color=MUTED, sw=1.3))
    parts.append(arrow(ox, oy + 6, ox, oy - ah - 8, color=MUTED, sw=1.3))
    parts.append(text(ox + aw + 8, oy + 18, "частота (log)", 11, MUTED, "end"))
    parts.append(text(ox + 4, oy - ah - 14, "підсилення", 11, MUTED, "middle"))
    # рівень 1
    one_y = oy - ah * 0.42
    parts.append(line(ox, one_y, ox + aw, one_y, color=MUTED, sw=1.3, dash="5 5"))
    parts.append(text(ox - 8, one_y + 4, "1", 11, MUTED, "end", bold=True))
    top_y = oy - ah + 20  # рівень, до якого підходить T унизу / S угорі
    # S: мала зліва, горб над 1 в середині, →1 справа (масштаб: val=1 → рівень one_y)
    unit = oy - one_y  # пікселів на одиницю підсилення
    sp = []
    for i in range(161):
        t = i / 160.0
        base = 1.0 - math.exp(-3.4 * t)                            # 0→1
        bump = 0.30 * math.exp(-((t - 0.62) ** 2) / (2 * 0.010))   # горб над 1
        val = min(base + (bump if t > 0.35 else 0.0), 1.30)
        sp.append((ox + t * aw, oy - val * unit))
    ps = " ".join("%.1f,%.1f" % p for p in sp)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (ps, POS))
    parts.append(text(ox + aw * 0.16, oy - 22, "S = 1/(1+L)", 12, POS, "middle", bold=True))
    # T: ≈1 зліва, спадає справа
    tp = []
    for i in range(161):
        t = i / 160.0
        val = 1.0 / (1.0 + math.exp(12 * (t - 0.58)))              # логістичний спад від 1 до 0
        tp.append((ox + t * aw, oy - val * unit))
    pt = " ".join("%.1f,%.1f" % p for p in tp)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (pt, FIELD))
    parts.append(text(ox + aw * 0.83, one_y - 16, "T = L/(1+L)", 12, FIELD, "middle", bold=True))
    # позначки зон
    parts.append(mtext(ox + aw * 0.13, oy - ah + 6,
                       ["тут контур давить збурення", "(S мала) й стежить за r (T≈1)"], 10, MUTED, "middle"))
    parts.append(mtext(ox + aw * 0.63, one_y - (one_y - top_y) - 2,
                       ["горб S > 1: тут контур", "ПОГІРШУЄ — «водяний матрац»"], 10, POS, "middle"))
    render(os.path.join(IMG, "sensitivity-curves.svg"), W, H, *parts,
           title="Чутливість S і доповняльна T: скрізь S + T = 1")


# ── Д-фігура 3: множник 1/(1+L) — у скільки разів контур давить збурення ──────
# Стовпчики: на низьких частотах L велике → 1/(1+L) крихітне (сильне придушення);
# на кросовері L≈1 → множник ~0.5; вище L→0 → множник →1 (контур не допомагає).
def figd_rejection_factor():
    W, H = 700, 340
    ox, oy = 90, 280
    aw, ah = 560, 210
    parts = []
    parts.append(arrow(ox - 6, oy, ox + aw + 14, oy, color=MUTED, sw=1.3))
    parts.append(arrow(ox, oy + 6, ox, oy - ah - 8, color=MUTED, sw=1.3))
    parts.append(text(ox + aw + 8, oy + 18, "частота (log)", 11, MUTED, "end"))
    parts.append(text(ox + 4, oy - ah - 14, "лишок збурення = 1/(1+L)", 10, MUTED, "middle"))
    one_y = oy - ah + 24
    parts.append(line(ox, one_y, ox + aw, one_y, color=MUTED, sw=1.3, dash="5 5"))
    parts.append(text(ox - 8, one_y + 4, "1", 11, MUTED, "end", bold=True))
    # крива 1/(1+L): мала зліва, росте до 1
    pts = []
    for i in range(161):
        t = i / 160.0
        # L велике зліва (10^(2-4t)), спадає; множник = 1/(1+L)
        L = 10 ** (2.4 - 4.2 * t)
        val = 1.0 / (1.0 + L)
        y = oy - val * (oy - one_y)
        pts.append((ox + t * aw, y))
    pl = " ".join("%.1f,%.1f" % p for p in pts)
    # заливка під кривою
    band = ["%.1f,%.1f" % (ox, oy)] + ["%.1f,%.1f" % p for p in pts] + ["%.1f,%.1f" % (ox + aw, oy)]
    parts.append('<polygon points="%s" fill="#eafaf1" stroke="none" opacity="0.7"/>' % " ".join(band))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (pl, FIELD))
    # анотації
    parts.append(mtext(ox + aw * 0.16, oy - 20, ["L велике →", "збурення давиться сильно"], 10, FIELD, "middle"))
    # кросовер
    cx = ox + aw * 0.565
    parts.append(line(cx, oy, cx, one_y, color=MUTED, sw=1.0, dash="2 4"))
    parts.append(text(cx, one_y - 8, "L ≈ 1: лишок ≈ ½", 10, INK, "middle", bold=True))
    parts.append(mtext(ox + aw * 0.86, one_y + 20, ["L → 0:", "контур не", "допомагає"], 10, POS, "middle"))
    render(os.path.join(IMG, "rejection-factor.svg"), W, H, *parts,
           title="Множник придушення 1/(1+L): сильний унизу, зникає вгорі")


# ── Д-фігура 4: два ступені свободи — прямий зв'язок + зворотний ──────────────
# Feedforward F гонить наперед відому частину (з моделі об'єкта), а зворотний
# контур C ловить лишок: збурення й похибку моделі. Два незалежні канали.
def figd_feedforward_feedback():
    W, H = 780, 340
    parts = []
    cy = 150
    ff_x, sum_x, ctrl_x, usum_x, plant_x = 250, 250, 400, 520, 630
    # завдання r ліворуч, роздвоюється
    parts.append(text(70, cy + 4, "завдання r", 11, NEG, "middle", bold=True))
    parts.append(circle(150, cy, 4, fill=NEG, stroke=NEG, sw=1))
    parts.append(line(120, cy, 150, cy, color=NEG, sw=2.0))
    # гілка вгору до F (feedforward)
    ff_y = cy - 78
    parts.append(line(150, cy, 150, ff_y, color=NEG, sw=1.8))
    b_ff = textbox(ff_x, ff_y, "F (модель)", size=13, fill="#f6f4ec", stroke=MUTED, sw=1.7, min_w=110)[0]
    parts.append(b_ff)
    parts.append(arrow(150, ff_y, ff_x - 60, ff_y, color=NEG, sw=1.8))
    parts.append(text((150 + ff_x) / 2, ff_y - 8, "прямий зв'язок", 10, MUTED, "middle"))
    # гілка вниз до суматора помилки
    parts.append(line(150, cy, 150, cy, color=NEG, sw=1.8))
    parts.append(arrow(150, cy, sum_x - 20, cy, color=NEG, sw=2.0))
    # суматор помилки
    parts.append(circle(sum_x, cy, 18, fill="#fff8e1", stroke="#f0b429", sw=2))
    parts.append(text(sum_x - 6, cy + 4, "−", 15, NEG, "middle", bold=True))
    parts.append(text(sum_x - 18, cy - 6, "+", 12, INK, "middle", bold=True))
    # C (feedback)
    b_ctrl = textbox(ctrl_x, cy, "C", size=15, fill="#eef2f7", stroke=NEG, sw=1.8, min_w=60)[0]
    parts.append(b_ctrl)
    parts.append(arrow(sum_x + 20, cy, ctrl_x - 32, cy, color=POS, sw=2.0))
    parts.append(text((sum_x + ctrl_x) / 2 + 2, cy - 9, "e", 12, POS, "middle", bold=True))
    # суматор впливу (u = ff + fb)
    parts.append(circle(usum_x, cy, 16, fill="#fdecea", stroke=POS, sw=1.8))
    parts.append(text(usum_x - 5, cy + 4, "+", 13, INK, "middle", bold=True))
    parts.append(text(usum_x - 5, cy - 8, "+", 12, POS, "middle", bold=True))
    parts.append(arrow(ctrl_x + 32, cy, usum_x - 18, cy, color=INK, sw=2.0))
    # F зверху в суматор впливу
    parts.append(line(ff_x + 60, ff_y, usum_x, ff_y, color=MUTED, sw=1.8))
    parts.append(arrow(usum_x, ff_y, usum_x, cy - 18, color=MUTED, sw=1.8))
    # об'єкт
    b_plant = textbox(plant_x, cy, "G", size=15, fill="#eafaf1", stroke=FIELD, sw=1.8, min_w=60)[0]
    parts.append(b_plant)
    parts.append(arrow(usum_x + 18, cy, plant_x - 32, cy, color=INK, sw=2.0))
    parts.append(text((usum_x + plant_x) / 2, cy - 9, "u", 10, MUTED, "middle"))
    # вихід
    parts.append(arrow(plant_x + 32, cy, 745, cy, color=FIELD, sw=2.0))
    parts.append(text(722, cy - 10, "вихід y", 11, FIELD, "middle", bold=True))
    # зворотний шлях
    back_y = cy + 110
    parts.append(line(725, cy, 725, back_y, color=INK, sw=1.8))
    parts.append(arrow(725, back_y, sum_x, back_y, color=INK, sw=1.8))
    parts.append(line(sum_x, back_y, sum_x, cy + 18, color=INK, sw=1.8))
    parts.append(text((sum_x + 725) / 2, back_y + 18, "вимір виходу", 10, MUTED, "middle"))
    # підпис
    parts.append(text(W / 2, H - 16,
                      "F гонить наперед відому частину; C ловить лишок — збурення й похибку моделі",
                      11, INK, "middle"))
    render(os.path.join(IMG, "feedforward-feedback.svg"), W, H, *parts,
           title="Два ступені свободи: прямий зв'язок разом зі зворотним")


# ── Д-фігура 5: контур у дискретному часі — вибірка, обчислення, утримання ────
# Час поділено на такти T. У кожен такт: миттєвий вимір y, обчислення (займає
# Δ), тоді нове u тримається сходинкою до наступного такту. Звідси затримка.
def figd_discrete_timing():
    W, H = 720, 250
    ox, oy = 70, 150
    aw = 600
    parts = []
    n = 5
    step = aw / n
    # осі часу
    parts.append(arrow(ox - 6, oy, ox + aw + 14, oy, color=MUTED, sw=1.3))
    parts.append(text(ox + aw + 8, oy + 18, "час", 11, MUTED, "end"))
    # моменти вибірки: kT, (k+1)T, (k+2)T, …
    tick_lbl = ["kT", "(k+1)T", "(k+2)T", "(k+3)T", "(k+4)T", "(k+5)T"]
    for k in range(n + 1):
        x = ox + k * step
        parts.append(line(x, oy - 4, x, oy + 4, color=MUTED, sw=1.2))
        parts.append(text(x, oy + 20, tick_lbl[k], 9, MUTED, "middle"))
    # верхня доріжка: вимір y (крапки в моменти вибірки)
    ytop = oy - 96
    parts.append(text(ox - 10, ytop, "вимір y[k]", 10, NEG, "end", bold=True))
    for k in range(n):
        x = ox + k * step
        parts.append(circle(x, ytop, 4, fill=NEG, stroke=NEG, sw=1))
    # обчислення: сірий брусок ширини Δ одразу після вибірки
    comp = step * 0.22
    ymid = oy - 58
    parts.append(text(ox - 10, ymid, "обчислення", 10, MUTED, "end", bold=True))
    for k in range(n):
        x = ox + k * step
        parts.append(rect(x, ymid - 8, comp, 16, fill="#eef0f2", stroke=MUTED, sw=1.2, rx=3))
    parts.append(text(ox + comp / 2, ymid - 14, "Δ", 10, MUTED, "middle", bold=True))
    # нижня доріжка: u тримається сходинкою (ZOH), оновлюється після Δ
    yzoh = oy - 18
    levels = [30, 46, 40, 52, 44]
    parts.append(text(ox - 10, yzoh - 20, "вплив u (утримання)", 10, INK, "end", bold=True))
    prev = None
    for k in range(n):
        x0 = ox + k * step + comp
        x1 = ox + (k + 1) * step + comp
        lv = yzoh - levels[k] * 0.7
        parts.append(line(x0, lv, min(x1, ox + aw), lv, color=INK, sw=2.4))
        if prev is not None:
            parts.append(line(x0, prev, x0, lv, color=INK, sw=1.6, dash="2 2"))
        prev = lv
    # підпис-висновок
    parts.append(text(W / 2, oy + 44,
                      "вимір миттєвий, але нове u діє лише через Δ і тримається цілий такт T —",
                      11, INK, "middle"))
    parts.append(text(W / 2, oy + 60,
                      "звідси затримка в петлі, яку далі рахує «запас стійкості»",
                      11, MUTED, "middle"))
    render(os.path.join(IMG, "discrete-timing.svg"), W, H, *parts,
           title="Контур у дискретному часі: вибірка → обчислення Δ → утримання T")


# ═══════════════════════════════════════════════════════════════════════════
#  ФІГУРИ ДЛЯ ВСТАВКИ math-sensitivity-waterbed.md (інтеграл Боде)
# ═══════════════════════════════════════════════════════════════════════════

# ── М-фігура 1: баланс площ ln|S| — виїмка знизу = горб згори ─────────────────
# Крива ln|S(ω)| проти частоти. Там, де S<1 (придушення) — ln|S|<0, площа під
# віссю (зелена, «виїмка»). Там, де S>1 (підсилення) — ln|S|>0, площа над віссю
# (червона, «горб»). Для стійкого контуру з надлишком полюсів ці площі РІВНІ.
def figm_area_balance():
    W, H = 720, 360
    ox, oy = 80, 195           # oy — рівень ln|S| = 0 (вісь балансу)
    aw, ah = 600, 130          # ah — піврозмах по вертикалі
    parts = []
    # осі
    parts.append(line(ox, oy, ox + aw + 14, oy, color=MUTED, sw=1.3))
    parts.append(arrow(ox, oy + ah + 20, ox, oy - ah - 24, color=MUTED, sw=1.3))
    parts.append(text(ox + aw + 8, oy - 6, "частота ω (log)", 11, MUTED, "end"))
    parts.append(text(ox + 6, oy - ah - 30, "ln |S(ω)|", 12, MUTED, "middle", bold=True))
    # позначки знаку осі
    parts.append(text(ox - 10, oy + 4, "0", 11, MUTED, "end", bold=True))
    parts.append(text(ox - 10, oy - ah + 6, "+", 13, POS, "end", bold=True))
    parts.append(text(ox - 10, oy + ah - 2, "−", 13, FIELD, "end", bold=True))
    # крива ln|S|: глибока виїмка зліва (S<<1), горб над нулем у середині, →0 справа
    pts = []
    for i in range(241):
        t = i / 240.0
        # виїмка (від'ємна) на низьких частотах + горб (додатний) на середніх
        dip = -1.0 * math.exp(-((t - 0.20) ** 2) / (2 * 0.018))
        hump = 0.62 * math.exp(-((t - 0.55) ** 2) / (2 * 0.012))
        val = dip + hump
        pts.append((ox + t * aw, oy - val * ah))
    # заливка: розділяємо шматки над і під віссю
    def bands(pts, oy):
        segs, cur, sign = [], [], None
        for (x, y) in pts:
            s = 1 if y <= oy else -1  # y<=oy → над віссю (додатне ln|S|)
            if sign is None:
                sign = s
            if s != sign and cur:
                segs.append((sign, cur)); cur = []; sign = s
            cur.append((x, y))
        if cur:
            segs.append((sign, cur))
        return segs
    for sign, seg in bands(pts, oy):
        if len(seg) < 2:
            continue
        col = "#fdecea" if sign > 0 else "#eafaf1"
        poly = ["%.1f,%.1f" % (seg[0][0], oy)] + ["%.1f,%.1f" % p for p in seg] + ["%.1f,%.1f" % (seg[-1][0], oy)]
        parts.append('<polygon points="%s" fill="%s" stroke="none" opacity="0.9"/>' % (" ".join(poly), col))
    pl = " ".join("%.1f,%.1f" % p for p in pts)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pl, INK))
    # анотації площ
    parts.append(mtext(ox + aw * 0.20, oy + ah - 30, ["ВИЇМКА: S < 1", "тут давимо збурення"],
                       10, FIELD, "middle", bold=True))
    parts.append(mtext(ox + aw * 0.55, oy - ah + 4, ["ГОРБ: S > 1", "тут ПІДСИЛЮЄМО"],
                       10, POS, "middle", bold=True))
    parts.append(text(ox + aw * 0.86, oy - 12, "S ≈ 1 (контур спить)", 10, MUTED, "middle"))
    # головний підсумок
    parts.append(text(W / 2, H - 16,
                      "площа виїмки = площа горба:  ∫ ln|S| dω = 0  —  придушене тут неминуче випне там",
                      11, INK, "middle", bold=True))
    render(os.path.join(IMG, "bode-area-balance.svg"), W, H, *parts,
           title="Інтеграл Боде: сума ln|S| по всіх частотах фіксована")


# ── М-фігура 2: водяний матрац — форма горба залежить від того, як тиснеш ──────
# Той самий «бюджет площі» під нулем можна витратити по-різному: вузька глибока
# виїмка → високий вузький горб (небезпечно); широка мілка → низький горб.
def figm_waterbed():
    W, H = 720, 340
    parts = []

    def panel(ox, oy, ah, aw, dip_c, dip_w, dip_d, hump_c, hump_w, hump_h, label, danger):
        f = []
        f.append(line(ox, oy, ox + aw, oy, color=MUTED, sw=1.2))
        f.append(line(ox, oy - ah, ox, oy + ah, color=MUTED, sw=1.1))
        f.append(text(ox - 8, oy + 4, "1", 10, MUTED, "end"))
        pts = []
        for i in range(201):
            t = i / 200.0
            dip = -dip_d * math.exp(-((t - dip_c) ** 2) / (2 * dip_w))
            hump = hump_h * math.exp(-((t - hump_c) ** 2) / (2 * hump_w))
            val = dip + hump
            pts.append((ox + t * aw, oy - val * ah))
        # заливки
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]; x1, y1 = pts[i + 1]
            col = "#fdecea" if (y0 + y1) / 2 < oy else "#eafaf1"
            f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="none" opacity="0.85"/>'
                     % (x0, oy, x0, y0, x1, y1, x1, oy, col))
        pl = " ".join("%.1f,%.1f" % p for p in pts)
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (pl, INK))
        f.append(text(ox + aw / 2, oy + ah + 26, label, 11, INK if not danger else POS, "middle", bold=danger))
        return f

    # ліва панель: вузька глибока виїмка → високий вузький горб
    parts += panel(70, 150, 96, 260, 0.24, 0.006, 1.15, 0.62, 0.006, 0.95,
                   "вузько й глибоко тиснеш → високий горб (пік S) — близько до розгойдування", True)
    # права панель: широка мілка виїмка → низький широкий горб
    parts += panel(400, 150, 96, 260, 0.26, 0.028, 0.5, 0.66, 0.05, 0.28,
                   "широко й м'яко → низький горб — та сама площа, безпечніше", False)
    parts.append(text(W / 2, H - 14,
                      "площа під нулем однакова в обох — але «розмазаний» горб не б'є піком; вибираєш ФОРМУ, не наявність",
                      10, MUTED, "middle"))
    render(os.path.join(IMG, "waterbed.svg"), W, H, *parts,
           title="Водяний матрац: горб не прибрати, лише пересунути й розмазати")


# ── М-фігура 3: нестійкий полюс піднімає бюджет із нуля до π·Σp ────────────────
# Для стійкого об'єкта бюджет = 0 (виїмка = горб). Нестійкий полюс у ПРАВІЙ
# півплощині робить праву частину додатною: обов'язковий ДОДАТКОВИЙ горб.
def figm_rhp_penalty():
    W, H = 720, 350
    ox, oy = 80, 200
    aw, ah = 600, 120
    parts = []
    parts.append(line(ox, oy, ox + aw + 14, oy, color=MUTED, sw=1.3))
    parts.append(arrow(ox, oy + ah + 18, ox, oy - ah - 24, color=MUTED, sw=1.3))
    parts.append(text(ox + aw + 8, oy - 6, "частота ω (log)", 11, MUTED, "end"))
    parts.append(text(ox + 6, oy - ah - 30, "ln |S(ω)|", 12, MUTED, "middle", bold=True))
    parts.append(text(ox - 10, oy + 4, "0", 11, MUTED, "end", bold=True))

    def curve(hump_h, hump_c, color, dash=None, dip_d=1.0):
        pts = []
        for i in range(241):
            t = i / 240.0
            dip = -dip_d * math.exp(-((t - 0.20) ** 2) / (2 * 0.018))
            hump = hump_h * math.exp(-((t - hump_c) ** 2) / (2 * 0.020))
            val = dip + hump
            pts.append((ox + t * aw, oy - val * ah))
        pl = " ".join("%.1f,%.1f" % p for p in pts)
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return pts, ('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"%s/>' % (pl, color, d))

    # стійкий об'єкт: бюджет 0 (горб рівно компенсує виїмку) — пунктир, сірий
    pts0, poly0 = curve(0.62, 0.55, MUTED, dash="6 5")
    # нестійкий полюс: той самий контроль, але додатковий обов'язковий горб (більша площа згори)
    pts1, poly1 = curve(1.05, 0.55, POS)
    # заливка різниці (додаткова площа горба через полюс)
    band = []
    for (x0, y0), (x1, y1) in zip(pts1, pts0):
        band.append((x0, min(y0, y1)))
    # просто підсвітимо область над віссю для нестійкої кривої
    seg = [(x, y) for (x, y) in pts1 if y <= oy]
    if len(seg) >= 2:
        poly = ["%.1f,%.1f" % (seg[0][0], oy)] + ["%.1f,%.1f" % p for p in seg] + ["%.1f,%.1f" % (seg[-1][0], oy)]
        parts.append('<polygon points="%s" fill="#fdecea" stroke="none" opacity="0.85"/>' % " ".join(poly))
    parts.append(poly0)
    parts.append(poly1)
    # анотації
    parts.append(text(ox + aw * 0.20, oy + ah - 22, "виїмка (та сама)", 10, FIELD, "middle", bold=True))
    parts.append(mtext(ox + aw * 0.55, oy - ah + 2, ["стійкий об'єкт: бюджет = 0", "(сірий пунктир — горб = виїмці)"],
                       9, MUTED, "middle"))
    parts.append(mtext(ox + aw * 0.80, oy - ah + 36, ["нестійкий полюс:", "бюджет = π·Σ pₖ > 0", "— ВИЩИЙ горб примусово"],
                       10, POS, "middle", bold=True))
    parts.append(text(W / 2, H - 14,
                      "полюс у правій півплощині піднімає весь бюджет ln|S| над нулем — платити доводиться більшим горбом",
                      11, INK, "middle", bold=True))
    render(os.path.join(IMG, "rhp-penalty.svg"), W, H, *parts,
           title="Нестійкий об'єкт: бюджет чутливості вже не нуль, а π·Σ pₖ")


fig_open_loop()
fig_closed_loop()
fig_error_signal()
fig_disturbance_rejection()
fig_steering_loop()
fig_controller_tuning()
figd_three_inputs()
figd_sensitivity_curves()
figd_rejection_factor()
figd_feedforward_feedback()
figd_discrete_timing()
figm_area_balance()
figm_waterbed()
figm_rhp_penalty()
print("Done. SVG in", IMG)
