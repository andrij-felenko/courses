# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Чому людина не бачить того, що на екрані».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/.
"""
import sys, os

TOPIC_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.abspath(os.path.join(TOPIC_DIR, '..', '..', '..', '..', 'scripts'))
sys.path.insert(0, SCRIPTS_DIR)
from svgkit import *

IMG_DIR = os.path.join(TOPIC_DIR, "img")
os.makedirs(IMG_DIR, exist_ok=True)


# ── Фігура 1: Геометрія зорового поля та часовий цикл саккад ────────────────
def fig_foveal_vs_peripheral():
    W, H = 1040, 530
    P = []
    P.append(text(W / 2, 28, "Геометрія зорового поля людини та дискретна природа саккад",
                  size=16, bold=True))

    # Ліва колонка: Конус зорового поля на екрані
    box_w = 470
    box_h = 430
    x_l = 35
    y_top = 60

    P.append(rect(x_l, y_top, box_w, box_h, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=8))
    P.append(text(x_l + box_w / 2, y_top + 26, "А. ЗОНИ ЗОРОВОГО СПРИЙНЯТТЯ НА ЕКРАНІ",
                  size=12, bold=True, color="#1e293b"))

    # Екран (горизонтальна плашка вгорі)
    scr_y = y_top + 80
    scr_x0 = x_l + 35
    scr_x1 = x_l + box_w - 35
    P.append(rect(scr_x0, scr_y - 12, scr_x1 - scr_x0, 24, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=4))
    P.append(text(x_l + box_w / 2, scr_y - 20, "Площина операторського монітора", size=10.5, bold=True, color=INK))

    # Око спостерігача (посередині верхнього відсіку)
    eye_cx, eye_cy = x_l + box_w / 2, y_top + 200
    P.append(circle(eye_cx, eye_cy, 14, fill="#ffffff", stroke=INK, sw=1.8))
    P.append(circle(eye_cx, eye_cy, 6, fill=INK, stroke=INK))
    P.append(text(eye_cx, eye_cy + 22, "Око спостерігача (d ≈ 60 см)", size=10, color=MUTED))

    # Конуси зору (промені від ока до екрана — строго між y_top+80 та y_top+200)
    # Периферія (> 10 deg)
    p_peri_l = scr_x0 + 15
    p_peri_r = scr_x1 - 15
    P.append(line(eye_cx, eye_cy - 14, p_peri_l, scr_y + 12, color="#94a3b8", sw=1.2, dash="3,3"))
    P.append(line(eye_cx, eye_cy - 14, p_peri_r, scr_y + 12, color="#94a3b8", sw=1.2, dash="3,3"))

    # Парафовеа (2 - 5 deg)
    p_para_l = eye_cx - 70
    p_para_r = eye_cx + 70
    P.append(line(eye_cx, eye_cy - 14, p_para_l, scr_y + 12, color=NEG, sw=1.4, dash="4,2"))
    P.append(line(eye_cx, eye_cy - 14, p_para_r, scr_y + 12, color=NEG, sw=1.4, dash="4,2"))

    # Фовеа (1 - 2 deg)
    p_fov_l = eye_cx - 22
    p_fov_r = eye_cx + 22
    P.append(line(eye_cx, eye_cy - 14, p_fov_l, scr_y + 12, color=POS, sw=2.0))
    P.append(line(eye_cx, eye_cy - 14, p_fov_r, scr_y + 12, color=POS, sw=2.0))

    # Виділення сегментів на екрані
    P.append(rect(p_fov_l, scr_y - 10, p_fov_r - p_fov_l, 20, fill="#fdecea", stroke=POS, sw=1.8, rx=2))
    P.append(text(eye_cx, scr_y + 4, "2°", size=10.5, bold=True, color=POS))

    # Пояснення зон (розміщені НИЖЧЕ ока, щоб не перетинати жодної лінії)
    f_fov, _, _ = textbox(x_l + box_w / 2, y_top + 265,
                          "Фовеальний зір (1°–2° поля зору, діаметр ≈ 2 см на моніторі):\n"
                          "100% гострота, щільні колбочки. ЄДИНА зона для читання цифр і тексту.",
                          size=9.5, bold=False, fill="#fff5f5", stroke=POS, min_w=box_w - 30)
    P.append(f_fov)

    f_para, _, _ = textbox(x_l + box_w / 2, y_top + 330,
                           "Парафовеа (2°–5°): розпізнавання контурів слів та грубих піктограм.",
                           size=9.5, bold=False, fill="#f0f4ff", stroke=NEG, min_w=box_w - 30)
    P.append(f_para)

    f_peri, _, _ = textbox(x_l + box_w / 2, y_top + 390,
                           "Периферичний зір (> 10°): низька гострота, відсутність розрізнення тексту.\n"
                           "Палички реагують ВИКЛЮЧНО на швидкий рух, спалах та мерехтіння.",
                           size=9.5, bold=False, fill="#f8fafc", stroke="#64748b", min_w=box_w - 30)
    P.append(f_peri)

    # Права колонка: Часова лінійка саккадичного циклу
    x_r = W - 35 - box_w
    P.append(rect(x_r, y_top, box_w, box_h, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=8))
    P.append(text(x_r + box_w / 2, y_top + 26, "Б. ЧАСОВИЙ ЦИКЛ: ФІКСАЦІЇ ТА САККАДИЧНА СЛІПОТА",
                  size=12, bold=True, color="#1e293b"))

    # Часова шкала
    t_y0 = y_top + 75
    P.append(line(x_r + 30, t_y0, x_r + box_w - 30, t_y0, color=INK, sw=1.8))
    P.append(arrow(x_r + box_w - 40, t_y0, x_r + box_w - 20, t_y0, color=INK, sw=1.8))
    P.append(text(x_r + box_w - 22, t_y0 - 10, "Час t", size=10, bold=True, color=MUTED))

    # Блок 1: Фіксація 1 (250 мс)
    b1_x = x_r + 35
    b1_w = 145
    P.append(rect(b1_x, t_y0 + 20, b1_w, 75, fill="#e9f7ef", stroke=FIELD, sw=1.5, rx=4))
    P.append(text(b1_x + b1_w / 2, t_y0 + 45, "Фіксація 1 (Прилад)", size=10.5, bold=True, color=FIELD))
    P.append(text(b1_x + b1_w / 2, t_y0 + 65, "T_fix ≈ 200–350 мс", size=9.5, color=INK))
    P.append(text(b1_x + b1_w / 2, t_y0 + 82, "Зчитування даних", size=9.5, color=MUTED))

    # Блок 2: Саккада (стрибок очей)
    b2_x = b1_x + b1_w + 10
    b2_w = 70
    P.append(rect(b2_x, t_y0 + 20, b2_w, 75, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
    P.append(text(b2_x + b2_w / 2, t_y0 + 42, "Саккада", size=10, bold=True, color=POS))
    P.append(text(b2_x + b2_w / 2, t_y0 + 60, "30–80 мс", size=9.5, bold=True, color=POS))
    P.append(text(b2_x + b2_w / 2, t_y0 + 80, "СЛІПОТА!", size=9.5, bold=True, color=POS))

    # Блок 3: Фіксація 2 (250 мс)
    b3_x = b2_x + b2_w + 10
    b3_w = 145
    P.append(rect(b3_x, t_y0 + 20, b3_w, 75, fill="#e9f7ef", stroke=FIELD, sw=1.5, rx=4))
    P.append(text(b3_x + b3_w / 2, t_y0 + 45, "Фіксація 2 (Карта)", size=10.5, bold=True, color=FIELD))
    P.append(text(b3_x + b3_w / 2, t_y0 + 65, "T_fix ≈ 200–350 мс", size=9.5, color=INK))
    P.append(text(b3_x + b3_w / 2, t_y0 + 82, "Розпізнавання образу", size=9.5, color=MUTED))

    # Стрілка саккадичного придушення
    P.append(arrow(b2_x + b2_w / 2, t_y0 + 105, b2_x + b2_w / 2, t_y0 + 130, color=POS, sw=1.8))

    f_supp, _, _ = textbox(x_r + box_w / 2, t_y0 + 205,
                           "Саккадичне придушення (Saccadic Suppression):\n"
                           "Під час швидкого руху очного яблука (до 900°/с) мозок\n"
                           "повністю блокує зоровий потік, щоб уникнути розмиття.\n"
                           "До 10–15% часу сканування екрана людина функціонально сліпа.",
                           size=9.5, bold=False, fill="#fff5f5", stroke=POS, min_w=box_w - 30)
    P.append(f_supp)

    f_rule, _, _ = textbox(x_r + box_w / 2, t_y0 + 315,
                           "Інженерний наслідок:\n"
                           "Статичний червоний напис на периферії НЕ приверне погляд,\n"
                           "бо палички не бачать кольору й дрібних деталей без спалаху/руху.",
                           size=9.5, bold=True, fill="#ffffff", stroke=INK, min_w=box_w - 30)
    P.append(f_rule)

    # Загальний підсумок внизу
    fr_bot, _, _ = textbox(W / 2, 505,
                           "Людський зір — це вузький промінь високої чіткості (2°), що перестрибує по екрану дискретними стрибками (саккадами).",
                           size=11, bold=True, fill="#ffffff", stroke=INK)
    P.append(fr_bot)

    render(os.path.join(IMG_DIR, "foveal-vs-peripheral.svg"), W, H, *P)


# ── Фігура 2: Когнітивне тунелювання та звуження уваги під час стресу ────────
def fig_stress_tunnel_vision():
    W, H = 1000, 520
    P = []
    P.append(text(W / 2, 28, "Когнітивне тунелювання уваги оператора під час аварійного стресу",
                  size=16, bold=True))

    # Схема дисплея та зони фокусу (зліва)
    scr_w = 460
    scr_h = 350
    scr_x = 40
    scr_y = 65

    # Рамка дисплея
    P.append(rect(scr_x, scr_y, scr_w, scr_h, fill="#1e293b", stroke="#475569", sw=2.0, rx=8))
    P.append(text(scr_x + scr_w / 2, scr_y + 24, "Дисплей наземної станції (Аварійна ситуація)", size=11, color="#94a3b8", bold=True))

    # Периферійні тривожні повідомлення, які ігноруються
    P.append(rect(scr_x + 15, scr_y + 45, 180, 50, fill="#7f1d1d", stroke=POS, sw=2.0, rx=4))
    P.append(text(scr_x + 105, scr_y + 68, "⚠ FIRE: ENGINE 1", size=11, bold=True, color="#ffffff"))
    P.append(text(scr_x + 105, scr_y + 84, "Температура 135°C", size=9.5, color="#fca5a5"))

    P.append(rect(scr_x + scr_w - 195, scr_y + 45, 180, 50, fill="#7f1d1d", stroke=POS, sw=2.0, rx=4))
    P.append(text(scr_x + scr_w - 105, scr_y + 68, "⚠ BATTERY CRITICAL", size=11, bold=True, color="#ffffff"))
    P.append(text(scr_x + scr_w - 105, scr_y + 84, "Напруга 13.2 В (FAILSAFE)", size=9.5, color="#fca5a5"))

    # Карта та горизонт у центрі
    P.append(rect(scr_x + 60, scr_y + 110, scr_w - 120, 160, fill="#0f172a", stroke="#334155", sw=1.0, rx=4))
    P.append(text(scr_x + scr_w / 2, scr_y + 135, "Штучний авіагоризонт та карта", size=9.5, color="#64748b"))

    # Тунельний фокус (когнітивний прожектор)
    spot_cx, spot_cy = scr_x + scr_w / 2, scr_y + 200
    P.append(circle(spot_cx, spot_cy, 65, fill="none", stroke=POS, sw=2.5))
    P.append(rect(spot_cx - 50, spot_cy - 25, 100, 50, fill="#fee2e2", stroke=POS, sw=2.0, rx=4))
    P.append(text(spot_cx, spot_cy - 4, "GPS HDOP: 2.8", size=11, bold=True, color=POS))
    P.append(text(spot_cx, spot_cy + 14, "(Супутники: 4)", size=9.5, bold=True, color=INK))

    # Стрілка на тунельний фокус
    P.append(text(spot_cx, scr_y + 300, "ТОЧКА КОГНІТИВНОГО «ЗАЛИПАННЯ»", size=11, bold=True, color=POS))
    P.append(text(spot_cx, scr_y + 320, "Оператор 40 секунд намагається розібратися з якістю GPS", size=9.5, color="#e2e8f0"))

    # Стрілки ігнорування
    P.append(arrow(spot_cx - 40, spot_cy - 30, scr_x + 110, scr_y + 100, color="#ef4444", sw=1.8))
    P.append(text(scr_x + 110, scr_y + 120, "ІГНОРУЄТЬСЯ (Сліпота)", size=9.5, bold=True, color="#ef4444"))

    P.append(arrow(spot_cx + 40, spot_cy - 30, scr_x + scr_w - 110, scr_y + 100, color="#ef4444", sw=1.8))
    P.append(text(scr_x + scr_w - 110, scr_y + 120, "ІГНОРУЄТЬСЯ (Сліпота)", size=9.5, bold=True, color="#ef4444"))

    # Права колонка: Механізм психофізіологічного звуження
    box_r_w = 430
    x_r = W - 40 - box_r_w
    y_r0 = 65

    P.append(rect(x_r, y_r0, box_r_w, scr_h, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=8))
    P.append(text(x_r + box_r_w / 2, y_r0 + 26, "МЕХАНІЗМ COGNITIVE TUNNELING", size=12, bold=True, color="#1e293b"))

    # Сходинки стресу
    step_y = y_r0 + 65
    f_s1, _, _ = textbox(x_r + box_r_w / 2, step_y,
                         "1. Раптова відмова або критичний збій на борту\n"
                         "Викид адреналіну/кортизолу, різке зростання ЧСС (>140 уд/хв).",
                         size=9.5, bold=False, fill="#fff5f5", stroke=POS, min_w=box_r_w - 40)
    P.append(f_s1)

    P.append(arrow(x_r + box_r_w / 2, step_y + 22, x_r + box_r_w / 2, step_y + 45, color=INK, sw=1.6))

    step_y += 65
    f_s2, _, _ = textbox(x_r + box_r_w / 2, step_y,
                         "2. Перевантаження робочої пам'яті (Working Memory)\n"
                         "Префронтальна кора відсікає 95% вхідних стимулів як «шум»,\n"
                         "звужуючи увагу до одного єдиного параметра.",
                         size=9.5, bold=False, fill="#f0f4ff", stroke=NEG, min_w=box_r_w - 40)
    P.append(f_s2)

    P.append(arrow(x_r + box_r_w / 2, step_y + 25, x_r + box_r_w / 2, step_y + 48, color=INK, sw=1.6))

    step_y += 70
    f_s3, _, _ = textbox(x_r + box_r_w / 2, step_y,
                         "3. Неуважна сліпота та глухота (Inattentional Blindness)\n"
                         "Очі фізично ковзають по червоних банерах і вуха чують зумер,\n"
                         "але мозок НЕ інтерпретує сигнал: свідомість замкнена на GPS.",
                         size=9.5, bold=True, fill="#fef2f2", stroke=POS, min_w=box_r_w - 40)
    P.append(f_s3)

    # Підсумок внизу
    fr_bot, _, _ = textbox(W / 2, 475,
                           "У стані стресу людина втрачає здатність до оглядового сканування: другорядне завдання поглинає 100% ресурсу уваги.",
                           size=11, bold=True, fill="#ffffff", stroke=INK)
    P.append(fr_bot)

    render(os.path.join(IMG_DIR, "stress-tunnel-vision.svg"), W, H, *P)


# ── Фігура 3: Сліпота до повільних змін (Change Blindness) ───────────────────
def fig_change_blindness_drift():
    W, H = 1000, 490
    P = []
    P.append(text(W / 2, 28, "Сліпота до змін: чому мозок помічає стрибок і пропускає плавний витік",
                  size=16, bold=True))

    w_card = 440
    h_card = 350
    y_c = 65

    # Ліва картка: Різка зміна (Стрибок)
    x_l = 40
    P.append(rect(x_l, y_c, w_card, h_card, fill="#f8fafc", stroke=FIELD, sw=1.5, rx=8))
    P.append(text(x_l + w_card / 2, y_c + 26, "А. СТРИБКОПОДІБНА ЗМІНА (РІЗКИЙ КРАХ)", size=12, bold=True, color=FIELD))

    # Графік ліворуч
    gx_l = x_l + 45
    gy_l = y_c + 140
    gw = w_card - 80
    gh = 70

    P.append(line(gx_l, gy_l, gx_l + gw, gy_l, color="#94a3b8", sw=1.2))
    P.append(line(gx_l, gy_l + 30, gx_l, gy_l - gh, color="#94a3b8", sw=1.2))
    P.append(text(gx_l - 8, gy_l - gh + 5, "Тиск P", size=9.5, color=MUTED, anchor="end"))
    P.append(text(gx_l + gw, gy_l + 18, "Час t", size=9.5, color=MUTED, anchor="end"))

    # Крива стрибка
    p_step = [(gx_l, gy_l - gh + 15), (gx_l + gw * 0.4, gy_l - gh + 15),
              (gx_l + gw * 0.45, gy_l - 5), (gx_l + gw, gy_l - 5)]
    for i in range(len(p_step) - 1):
        P.append(line(p_step[i][0], p_step[i][1], p_step[i + 1][0], p_step[i + 1][1], color=FIELD, sw=2.5))

    # Сплеск похідної
    P.append(arrow(gx_l + gw * 0.42, gy_l - 10, gx_l + gw * 0.42, gy_l - gh - 5, color=POS, sw=2.0))
    P.append(text(gx_l + gw * 0.42, gy_l - gh - 12, "Висока похідна dP/dt!", size=10, bold=True, color=POS))

    f_l_desc, _, _ = textbox(x_l + w_card / 2, y_c + 255,
                             "Висока просторово-часова похідна (dI/dt >> threshold):\n"
                             "• Збуджує магноцелюлярний тракт зорової системи;\n"
                             "• Викликає мимовільне захоплення уваги (Bottom-Up Capture);\n"
                             "• Погляд рефлекторно переводиться саккадою за 150–200 мс.",
                             size=9.5, bold=False, fill="#e9f7ef", stroke=FIELD, min_w=w_card - 40)
    P.append(f_l_desc)

    # Права картка: Плавний дрейф (Change Blindness)
    x_r = W - 40 - w_card
    P.append(rect(x_r, y_c, w_card, h_card, fill="#fffbfb", stroke=POS, sw=1.5, rx=8))
    P.append(text(x_r + w_card / 2, y_c + 26, "Б. ПЛАВНИЙ ДРЕЙФ (CHANGE BLINDNESS)", size=12, bold=True, color=POS))

    # Графік праворуч
    gx_r = x_r + 45
    gy_r = y_c + 140

    P.append(line(gx_r, gy_r, gx_r + gw, gy_r, color="#94a3b8", sw=1.2))
    P.append(line(gx_r, gy_r + 30, gx_r, gy_r - gh, color="#94a3b8", sw=1.2))
    P.append(text(gx_r - 8, gy_r - gh + 5, "Тиск P", size=9.5, color=MUTED, anchor="end"))
    P.append(text(gx_r + gw, gy_r + 18, "Час t (хвилини)", size=9.5, color=MUTED, anchor="end"))

    # Крива повільного дрейфу
    p_drift = [(gx_r, gy_r - gh + 15), (gx_r + gw, gy_r - 5)]
    P.append(line(p_drift[0][0], p_drift[0][1], p_drift[1][0], p_drift[1][1], color=POS, sw=2.5))
    P.append(text(gx_r + gw * 0.5, gy_r - gh / 2 - 12, "Похідна dP/dt ≈ 0 (нижче порогу)", size=10, bold=True, color=POS))

    f_r_desc, _, _ = textbox(x_r + w_card / 2, y_c + 255,
                             "Швидкість зміни нижча за оптичний поріг руху:\n"
                             "• Оптичний потік відсутній — рецептори сітківки мовчать;\n"
                             "• Виявлення можливе ЛИШЕ через свідомий аудит (Top-Down Search);\n"
                             "• Оператор помічає аварію лише при повному знеструмленні/клині.",
                             size=9.5, bold=False, fill="#fdecea", stroke=POS, min_w=w_card - 40)
    P.append(f_r_desc)

    # Підсумок унизу
    fr_bot, _, _ = textbox(W / 2, 450,
                           "Захист від Change Blindness у софті: розрахунок похідних (Rate of Change) та підсвічування небезпечного тренду.",
                           size=11, bold=True, fill="#ffffff", stroke=INK)
    P.append(fr_bot)

    render(os.path.join(IMG_DIR, "change-blindness-drift.svg"), W, H, *P)


# ── Фігура 4: Візуальне захаращення проти High-Performance HMI (ISA-101) ─────
def fig_visual_clutter_hierarchy():
    W, H = 1040, 520
    P = []
    P.append(text(W / 2, 28, "Візуальне захаращення проти стандарту чистої кабіни (ANSI/ISA-101)",
                  size=16, bold=True))

    w_panel = 460
    h_panel = 400
    y_p = 60

    # Ліва панель: «Веселковий» захаращений інтерфейс (Погано)
    x_l = 35
    P.append(rect(x_l, y_p, w_panel, h_panel, fill="#0f172a", stroke=POS, sw=2.0, rx=8))
    P.append(text(x_l + w_panel / 2, y_p + 24, "ЗАХАРАЩЕНИЙ ДИСПЛЕЙ («НОВОРІЧНА ЯЛИНКА»)", size=11.5, bold=True, color="#f87171"))

    # Хаос елементів з яскравими барвами
    # Рядок 1
    P.append(rect(x_l + 15, y_p + 45, 95, 45, fill="#16a34a", stroke="#22c55e", rx=4))
    P.append(text(x_l + 62, y_p + 68, "RPM 1: 5420", size=9.5, bold=True, color="#ffffff"))
    P.append(text(x_l + 62, y_p + 82, "OK (NORMAL)", size=9.5, color="#dcfce7"))

    P.append(rect(x_l + 120, y_p + 45, 95, 45, fill="#2563eb", stroke="#3b82f6", rx=4))
    P.append(text(x_l + 167, y_p + 68, "VOLT: 22.41V", size=9.5, bold=True, color="#ffffff"))
    P.append(text(x_l + 167, y_p + 82, "STABLE", size=9.5, color="#dbeafe"))

    P.append(rect(x_l + 225, y_p + 45, 105, 45, fill="#d97706", stroke="#f59e0b", rx=4))
    P.append(text(x_l + 277, y_p + 68, "TEMP_INV: 68C", size=9.5, bold=True, color="#ffffff"))
    P.append(text(x_l + 277, y_p + 82, "WARM", size=9.5, color="#fef3c7"))

    P.append(rect(x_l + 340, y_p + 45, 105, 45, fill="#dc2626", stroke="#ef4444", rx=4))
    P.append(text(x_l + 392, y_p + 68, "ALT_BARO: 142m", size=9.5, bold=True, color="#ffffff"))
    P.append(text(x_l + 392, y_p + 82, "HIGH", size=9.5, color="#fee2e2"))

    # Рядок 2: Сирі графіки і миготіння
    P.append(rect(x_l + 15, y_p + 100, 205, 110, fill="#1e1b4b", stroke="#6366f1", rx=4))
    P.append(text(x_l + 117, y_p + 118, "Спектр вібрацій (60 смуг)", size=9.5, bold=True, color="#a5b4fc"))
    # Лінії шуму
    for k in range(12):
        bx = x_l + 25 + k * 16
        bh = (k * 7) % 55 + 15
        P.append(rect(bx, y_p + 195 - bh, 10, bh, fill="#818cf8"))

    P.append(rect(x_l + 230, y_p + 100, 215, 110, fill="#312e81", stroke="#818cf8", rx=4))
    P.append(text(x_l + 337, y_p + 118, "Логи подій (50 рядків/с)", size=9.5, bold=True, color="#c7d2fe"))
    P.append(text(x_l + 240, y_p + 140, "11:04:02.102 PKT_RECV #1491", size=9.5, color="#e0e7ff", anchor="start"))
    P.append(text(x_l + 240, y_p + 155, "11:04:02.124 IMU_CALIB_OFFSET", size=9.5, color="#e0e7ff", anchor="start"))
    P.append(text(x_l + 240, y_p + 170, "11:04:02.155 GPS_SATS_VISIBLE 14", size=9.5, color="#e0e7ff", anchor="start"))
    P.append(text(x_l + 240, y_p + 185, "11:04:02.180 MOTOR_CURRENT 18.2A", size=9.5, color="#e0e7ff", anchor="start"))

    f_bad_desc, _, _ = textbox(x_l + w_panel / 2, y_p + 295,
                               "Проблеми «веселки»:\n"
                               "• 100% площі кричить яскравими кольорами (нульовий контраст);\n"
                               "• Закон Міллера порушено: > 40 елементів на одному екрані;\n"
                               "• Справжню аварію неможливо виявити швидше ніж за 5–10 секунд.",
                               size=9.5, bold=False, fill="#fff5f5", stroke=POS, min_w=w_panel - 30)
    P.append(f_bad_desc)

    # Права панель: High-Performance HMI (ANSI/ISA-101 / Dark Cockpit)
    x_r = W - 35 - w_panel
    P.append(rect(x_r, y_p, w_panel, h_panel, fill="#1e293b", stroke=FIELD, sw=2.0, rx=8))
    P.append(text(x_r + w_panel / 2, y_p + 24, "HIGH-PERFORMANCE HMI (ISA-101 / DARK COCKPIT)", size=11.5, bold=True, color="#4ade80"))

    # Спокійний сірий базовий шар
    P.append(rect(x_r + 15, y_p + 45, w_panel - 30, 60, fill="#334155", stroke="#475569", rx=4))
    P.append(text(x_r + 30, y_p + 65, "СИСТЕМА: ВСІ КОНТУРИ В НОРМІ", size=10, bold=True, color="#94a3b8", anchor="start"))

    # Аналогові шкали нормального діапазону (сірі шкали)
    # Шкала 1: Напруга
    P.append(text(x_r + 30, y_p + 88, "Напруга", size=9.5, color="#cbd5e1", anchor="start"))
    P.append(rect(x_r + 85, y_p + 78, 120, 12, fill="#1e293b", stroke="#64748b", rx=2))
    P.append(rect(x_r + 115, y_p + 80, 60, 8, fill="#64748b", rx=1)) # normal zone
    P.append(line(x_r + 155, y_p + 75, x_r + 155, y_p + 93, color="#ffffff", sw=2.0)) # pointer

    # Шкала 2: Температура
    P.append(text(x_r + 235, y_p + 88, "Температура", size=9.5, color="#cbd5e1", anchor="start"))
    P.append(rect(x_r + 310, y_p + 78, 120, 12, fill="#1e293b", stroke="#64748b", rx=2))
    P.append(rect(x_r + 320, y_p + 80, 70, 8, fill="#64748b", rx=1)) # normal zone
    P.append(line(x_r + 360, y_p + 75, x_r + 360, y_p + 93, color="#ffffff", sw=2.0)) # pointer

    # ЄДИНА АНОМАЛІЯ: Яскравий контрастний аварійний банер (Pop-out effect)
    P.append(rect(x_r + 15, y_p + 120, w_panel - 30, 80, fill="#7f1d1d", stroke=POS, sw=2.2, rx=6))
    P.append(text(x_r + 35, y_p + 148, "⚠ КРИТИЧНИЙ ПЕРЕГРІВ ІНВЕРТОРА: 108°C (Норма < 85°C)", size=11, bold=True, color="#ffffff", anchor="start"))
    P.append(text(x_r + 35, y_p + 172, "Дія: Зменшити тягу до 40% або перемкнути на резервний мотор", size=9.5, color="#fecaca", anchor="start"))
    P.append(rect(x_r + w_panel - 120, y_p + 138, 90, 45, fill=POS, stroke="#ffffff", sw=1.5, rx=4))
    P.append(text(x_r + w_panel - 75, y_p + 165, "ПРИЙНЯТИ", size=10, bold=True, color="#ffffff"))

    f_good_desc, _, _ = textbox(x_r + w_panel / 2, y_p + 295,
                                "Переваги High-Performance HMI:\n"
                                "• Принцип Dark Cockpit: нормальні стани мовчать на сірому тлі;\n"
                                "• Аналогові шкали показують контекст (де норма, де межа);\n"
                                "• Ефект виринання (Visual Pop-Out): аномалія захоплює погляд за 50 мс.",
                                size=9.5, bold=False, fill="#e9f7ef", stroke=FIELD, min_w=w_panel - 30)
    P.append(f_good_desc)

    # Підсумок унизу
    fr_bot, _, _ = textbox(W / 2, 485,
                           "Колір в ергономічному інтерфейсі — це рідкісний дефіцитний ресурс, зарезервований виключно для аномалій.",
                           size=11, bold=True, fill="#ffffff", stroke=INK)
    P.append(fr_bot)

    render(os.path.join(IMG_DIR, "visual-clutter-hierarchy.svg"), W, H, *P)



if __name__ == "__main__":
    fig_foveal_vs_peripheral()
    fig_stress_tunnel_vision()
    fig_change_blindness_drift()
    fig_visual_clutter_hierarchy()
    print("OK: 4 figures generated into img/")
