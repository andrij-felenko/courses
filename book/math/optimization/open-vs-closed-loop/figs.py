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


fig_open_loop()
fig_closed_loop()
fig_error_signal()
fig_disturbance_rejection()
fig_steering_loop()
fig_controller_tuning()
print("Done. SVG in", IMG)
