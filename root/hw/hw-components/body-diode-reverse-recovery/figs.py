# -*- coding: utf-8 -*-
"""Фігури до теми «Body-діод MOSFET і зворотне відновлення».
Генерує 4 SVG-діаграми у ./img/:
  1. mosfet-parasitic-structure.svg  — Внутрішня структура MOSFET, body-діод та паразитний BJT
  2. reverse-recovery-waveform.svg   — Осцилограми зворотного відновлення: Soft проти Snappy
  3. halfbridge-commutation.svg      — Комутація напівмоста та наскрізний кидок струму
  4. parasitic-bjt-latchup.svg       — Механізм хибного відмикання паразитного BJT та пробою
Запуск: python figs.py
"""
import sys, os

# Додаємо шлях до svgkit у scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. mosfet-parasitic-structure.svg ──────────────────────────────────────
def make_mosfet_parasitic_structure(path):
    w, h = 880, 520
    out = []

    # Заголовки панелей
    out.append(fitbox(20, 15, 420, 38, "Кристал силового VDMOS / Trench MOSFET", fill=FILL, stroke=LINE, bold=True, size=13))
    out.append(fitbox(460, 15, 400, 38, "Еквівалентна схема транзистора", fill=FILL, stroke=LINE, bold=True, size=13))

    # ── Ліва панель: поперечний розріз напівпровідникової структури ──
    # Металізація витоку (Source Metal) — три роздільні контакти
    out.append(rect(40, 65, 105, 24, fill="#b0bec5", stroke=INK, sw=1.5))
    out.append(text(92, 81, "Source", size=11, color=INK, bold=True))

    out.append(rect(188, 65, 84, 24, fill="#b0bec5", stroke=INK, sw=1.5))
    out.append(text(230, 81, "Source / Body", size=10, color=INK, bold=True))

    out.append(rect(315, 65, 105, 24, fill="#b0bec5", stroke=INK, sw=1.5))
    out.append(text(367, 81, "Source", size=11, color=INK, bold=True))

    # Затворні електроди (Gate Polysilicon)
    out.append(rect(148, 65, 38, 45, fill="#90caf9", stroke=INK, sw=1.3))
    out.append(text(167, 90, "Gate", size=10, color=INK, bold=True))
    out.append(rect(274, 65, 38, 45, fill="#90caf9", stroke=INK, sw=1.3))
    out.append(text(293, 90, "Gate", size=10, color=INK, bold=True))

    # Витік n+ (Source n+)
    out.append(rect(65, 89, 80, 34, fill="#ffe082", stroke=INK, sw=1.4))
    out.append(text(105, 110, "n+ Source", size=11, color=INK, bold=True))

    out.append(rect(315, 89, 80, 34, fill="#ffe082", stroke=INK, sw=1.4))
    out.append(text(355, 110, "n+ Source", size=11, color=INK, bold=True))

    # Контакт p+ для закорочування підкладки
    out.append(rect(190, 89, 80, 34, fill="#ab47bc", stroke=INK, sw=1.4))
    out.append(text(230, 110, "p+ контакт", size=11, color="#ffffff", bold=True))

    # Дрейфова зона n- (Drift region)
    out.append(rect(40, 200, 380, 160, fill="#fff9c4", stroke=INK, sw=1.4))
    out.append(text(230, 240, "n- Дрейфова епітаксія (n- Drift)", size=13, color=INK, bold=True))
    out.append(text(230, 265, "Область блокування високої напруги", size=11, color=MUTED))

    # Підкладка n+ (Substrate)
    out.append(rect(40, 360, 380, 50, fill="#ffe082", stroke=INK, sw=1.4))
    out.append(text(230, 390, "n+ Підкладка (Substrate)", size=12, color=INK, bold=True))

    # Метал стоку (Drain Metal)
    out.append(rect(40, 410, 380, 26, fill="#b0bec5", stroke=INK, sw=1.5))
    out.append(text(230, 427, "Металізація стоку (Drain Contact)", size=12, color=INK, bold=True))

    # Стрілки та позначення p-n переходу body-діода
    out.append(line(40, 200, 420, 200, color=POS, sw=2, dash="5,3"))
    out.append(text(230, 192, "Металургійний p-n перехід body-діода", size=11, color=POS, bold=True))

    # ── Права панель: схемне відображення ──
    # Вузол Source
    out.append(text(640, 65, "Витік (Source)", size=13, color=INK, bold=True))
    out.append(line(640, 75, 640, 120, color=INK, sw=2))
    out.append(circle(640, 120, 4, fill=INK, stroke=INK))

    # Розгалуження на MOSFET, Body-діод та BJT
    out.append(line(540, 120, 740, 120, color=INK, sw=2))

    # MOSFET символ
    out.append(rect(515, 160, 50, 70, fill="#ffffff", stroke=INK, sw=1.5, rx=4))
    out.append(text(540, 195, "Канал\nMOSFET", size=10, color=INK, bold=True))
    out.append(line(540, 120, 540, 160, color=INK, sw=2))
    out.append(line(540, 230, 540, 340, color=INK, sw=2))

    # Body Diode символ
    out.append(line(640, 120, 640, 170, color=POS, sw=2))
    # Анод до Source, Катод до Drain
    out.append(line(625, 195, 655, 195, color=POS, sw=2))
    out.append(f'<polygon points="625,195 655,195 640,170" fill="#ffcdd2" stroke="{POS}" stroke-width="1.8"/>')
    out.append(line(625, 170, 655, 170, color=POS, sw=2))
    out.append(line(640, 195, 640, 340, color=POS, sw=2))
    out.append(text(675, 185, "Body-\nдіод", size=11, color=POS, bold=True))

    # Паразитний NPN BJT
    out.append(rect(715, 160, 50, 70, fill="#ffffff", stroke=NEG, sw=1.5, rx=4))
    out.append(text(740, 190, "Параз.\nNPN", size=10, color=NEG, bold=True))
    out.append(line(740, 120, 740, 160, color=NEG, sw=2))
    out.append(line(740, 230, 740, 340, color=NEG, sw=2))
    out.append(text(775, 165, "R_body", size=10, color=MUTED))

    # Об'єднання в стік
    out.append(circle(640, 340, 4, fill=INK, stroke=INK))
    out.append(line(540, 340, 740, 340, color=INK, sw=2))
    out.append(line(640, 340, 640, 385, color=INK, sw=2))
    out.append(text(640, 405, "Стік (Drain)", size=13, color=INK, bold=True))

    # Пояснювальний блок унизу
    out.append(fitbox(460, 425, 400, 75,
                      "Закорочування Source-Body об'єднує емітер і базу NPN,\n"
                      "але неминуче утворює інтегральний діод між\n"
                      "Source (анод) і Drain (катод).",
                      fill="#e8f5e9", stroke=FIELD, size=11, color=INK))

    render(path, w, h, *out)


# ── 2. reverse-recovery-waveform.svg ──────────────────────────────────────
def make_reverse_recovery_waveform(path):
    w, h = 900, 520
    out = []

    # Заголовок
    out.append(fitbox(20, 15, 860, 38, "Часові діаграми зворотного відновлення body-діода: Soft проти Snappy", fill=FILL, stroke=LINE, bold=True, size=14))

    # ── Графік струму i_D(t) ──
    out.append(fitbox(30, 65, 400, 25, "Струм діода i_D(t)", fill="#f5f5f5", stroke=LINE, bold=True, size=12))

    # Вісь часу струму
    out.append(line(50, 180, 440, 180, color=LINE, sw=1.5))
    out.append(text(435, 172, "t", size=12, color=INK, bold=True))
    out.append(line(80, 80, 80, 270, color=LINE, sw=1.5))
    out.append(text(70, 95, "i_D", size=12, color=INK, bold=True))
    out.append(text(65, 180, "0", size=11, color=MUTED))

    # Рівні струму
    out.append(line(75, 120, 85, 120, color=LINE, sw=1.2))
    out.append(text(60, 124, "+I_F", size=11, color=POS, bold=True))
    out.append(line(75, 245, 85, 245, color=LINE, sw=1.2))
    out.append(text(55, 249, "−I_rrm", size=11, color=NEG, bold=True))

    # Крива прямого струму та спаду di/dt
    out.append(line(80, 120, 140, 120, color=POS, sw=2.5)) # I_F
    out.append(line(140, 120, 200, 180, color=INK, sw=2.2)) # спад до 0
    out.append(line(200, 180, 260, 245, color=NEG, sw=2.2)) # фаза t_a до -I_rrm

    # М'яке відновлення (Soft) - синя лінія
    out.append(f'<path d="M 260,245 Q 310,240 370,180" fill="none" stroke="{NEG}" stroke-width="2.5"/>')
    out.append(text(340, 220, "Soft (S ≥ 1)", size=11, color=NEG, bold=True))

    # Жорстке відновлення (Snappy) - червона пунктирна лінія
    out.append(f'<path d="M 260,245 L 275,180 L 285,165 L 295,190 L 305,180" fill="none" stroke="{POS}" stroke-width="2" stroke-dasharray="4,3"/>')
    out.append(text(305, 160, "Snappy (S ≪ 1)", size=11, color=POS, bold=True))

    # Заштрихована область заряду Q_rr
    out.append(f'<polygon points="200,180 260,245 370,180" fill="#e3f2fd" opacity="0.6"/>')
    out.append(text(275, 200, "Q_rr", size=13, color=NEG, bold=True))

    # Інтервали t_a, t_b, t_rr
    out.append(line(200, 255, 200, 275, color=MUTED, sw=1, dash="2,2"))
    out.append(line(260, 255, 260, 275, color=MUTED, sw=1, dash="2,2"))
    out.append(line(370, 185, 370, 275, color=MUTED, sw=1, dash="2,2"))

    out.append(arrow(200, 270, 260, 270, color=INK, sw=1.2))
    out.append(arrow(260, 270, 200, 270, color=INK, sw=1.2))
    out.append(text(230, 265, "t_a", size=11, color=INK, bold=True))

    out.append(arrow(260, 270, 370, 270, color=INK, sw=1.2))
    out.append(arrow(370, 270, 260, 270, color=INK, sw=1.2))
    out.append(text(315, 265, "t_b", size=11, color=INK, bold=True))

    # ── Графік напруги v_DS(t) ──
    out.append(fitbox(470, 65, 400, 25, "Напруга сток-витік v_DS(t)", fill="#f5f5f5", stroke=LINE, bold=True, size=12))

    # Вісь часу напруги
    out.append(line(490, 240, 870, 240, color=LINE, sw=1.5))
    out.append(text(865, 232, "t", size=12, color=INK, bold=True))
    out.append(line(520, 80, 520, 270, color=LINE, sw=1.5))
    out.append(text(510, 95, "v_DS", size=12, color=INK, bold=True))

    # Рівні напруги
    out.append(line(515, 170, 525, 170, color=LINE, sw=1.2))
    out.append(text(485, 174, "V_bus", size=11, color=INK, bold=True))

    out.append(line(515, 105, 525, 105, color=POS, sw=1.2))
    out.append(text(465, 109, "V_spike", size=11, color=POS, bold=True))

    # Крива напруги під час прямої провідності (-V_F)
    out.append(line(520, 250, 640, 250, color=POS, sw=2)) # -V_F
    out.append(text(570, 262, "−V_F", size=10, color=POS))

    # Наростання напруги при закриванні
    out.append(line(640, 250, 700, 170, color=NEG, sw=2.5)) # плавне наростання до V_bus
    out.append(line(700, 170, 840, 170, color=NEG, sw=2.5)) # рівень V_bus

    # Викид напруги при Snappy recovery
    out.append(f'<path d="M 640,250 L 685,105 L 705,200 L 725,155 L 745,175 L 765,170 L 840,170" fill="none" stroke="{POS}" stroke-width="2" stroke-dasharray="4,3"/>')
    out.append(text(710, 120, "L_loop · (di_rr/dt)", size=11, color=POS, bold=True))

    # ── Нижня частина: порівняння параметрів ──
    out.append(fitbox(30, 310, 410, 185,
                      "Фази відновлення:\n"
                      "• t_a: винесення носіїв, i_D падає від 0 до −I_rrm.\n"
                      "• t_b: відновлення збідненого шару, спад струму до 0.\n"
                      "• Q_rr = ∫ i_rr dt = ½ · I_rrm · t_rr (заряд).\n"
                      "• Коефіцієнт м'якості: S = t_b / t_a.",
                      fill="#f0f4c3", stroke="#c0ca33", size=11, color=INK))

    out.append(fitbox(470, 310, 400, 185,
                      "Небезпека Snappy Recovery (S ≪ 1):\n"
                      "• Миттєвий обрив струму (snap-off) під час t_b.\n"
                      "• Гігантська швидкість спаду di_rr/dt (> 5000 А/мкс).\n"
                      "• Сплеск V_spike = L_loop · di_rr/dt пробиває MOSFET.\n"
                      "• Високочастотний дзвін генерує сильні EMI.",
                      fill="#ffebee", stroke=POS, size=11, color=INK))

    render(path, w, h, *out)


# ── 3. halfbridge-commutation.svg ──────────────────────────────────────────
def make_halfbridge_commutation(path):
    w, h = 880, 500
    out = []

    # Заголовок
    out.append(fitbox(20, 15, 840, 38, "Комутація напівмоста: зворотне відновлення body-діода нижнього ключа", fill=FILL, stroke=LINE, bold=True, size=14))

    # ── Ліва частина: Фаза 1 — Мертвий час (Dead Time) ──
    out.append(fitbox(40, 65, 370, 30, "Фаза 1: Dead Time (струм через body-діод)", fill="#e8eaf6", stroke=LINE, bold=True, size=12))

    # Шина живлення +V_bus
    out.append(line(80, 115, 360, 115, color=POS, sw=2))
    out.append(text(220, 108, "+V_bus (400 В)", size=11, color=POS, bold=True))

    # Верхній ключ Q_H (ВИМКНЕНИЙ)
    out.append(rect(100, 140, 70, 50, fill="#ffffff", stroke=MUTED, sw=1.5, rx=4))
    out.append(text(135, 165, "Q_H\n(OFF)", size=10, color=MUTED, bold=True))

    # Середня точка (Switch Node)
    out.append(circle(135, 230, 4, fill=INK, stroke=INK))
    out.append(line(135, 115, 135, 140, color=MUTED, sw=1.5))
    out.append(line(135, 190, 135, 270, color=INK, sw=2))

    # Нижній ключ Q_L (ВИМКНЕНИЙ, але діод проводить)
    out.append(rect(100, 270, 70, 50, fill="#ffffff", stroke=POS, sw=1.8, rx=4))
    out.append(text(135, 290, "Q_L (OFF)", size=10, color=MUTED))
    out.append(text(135, 308, "D_body (ON)", size=10, color=POS, bold=True))

    # Земля
    out.append(line(135, 320, 135, 350, color=INK, sw=2))
    out.append(line(80, 350, 360, 350, color=INK, sw=2))
    out.append(text(220, 368, "GND (0 В)", size=11, color=INK, bold=True))

    # Навантаження (Індуктивність L_load)
    out.append(line(135, 230, 240, 230, color=INK, sw=2))
    out.append(rect(240, 210, 80, 40, fill="#fff9c4", stroke=INK, sw=1.5, rx=4))
    out.append(text(280, 234, "L_load", size=12, color=INK, bold=True))

    # Струм навантаження I_L замикається знизу вгору
    out.append(arrow(135, 340, 135, 240, color=POS, sw=2.5))
    out.append(arrow(135, 230, 235, 230, color=POS, sw=2.5))
    out.append(text(175, 280, "I_load\n(дірки в n-)", size=10, color=POS, bold=True))

    out.append(fitbox(40, 390, 370, 85,
                      "Під час мертвого часу індуктивний струм\n"
                      "відкриває body-діод Q_L. У дрейфовій зоні\n"
                      "накопичується величезний заряд неосновних\n"
                      "носіїв (дірок) Q_rr.",
                      fill="#f3e5f5", stroke="#ab47bc", size=11, color=INK))

    # ── Права частина: Фаза 2 — Увімкнення верхнього ключа ──
    out.append(fitbox(470, 65, 370, 30, "Фаза 2: Вмикання Q_H (наскрізний струм)", fill="#ffebee", stroke=POS, bold=True, size=12))

    # Шина живлення +V_bus
    out.append(line(510, 115, 790, 115, color=POS, sw=2))
    out.append(text(650, 108, "+V_bus (400 В)", size=11, color=POS, bold=True))

    # Паразитна індуктивність контуру L_loop
    out.append(rect(540, 105, 45, 20, fill="#ffffff", stroke=POS, sw=1.2))
    out.append(text(562, 119, "L_loop", size=9, color=POS))

    # Верхній ключ Q_H (ВМИКАЄТЬСЯ)
    out.append(rect(530, 140, 70, 50, fill="#e8f5e9", stroke=FIELD, sw=2, rx=4))
    out.append(text(565, 165, "Q_H\n(ВМИК)", size=10, color=FIELD, bold=True))

    # Середня точка
    out.append(circle(565, 230, 4, fill=INK, stroke=INK))
    out.append(line(565, 115, 565, 140, color=POS, sw=2.5))
    out.append(line(565, 190, 565, 270, color=POS, sw=2.5))

    # Нижній ключ Q_L (D_body розсмоктує Q_rr)
    out.append(rect(530, 270, 70, 50, fill="#ffebee", stroke=POS, sw=2, rx=4))
    out.append(text(565, 290, "Q_L (OFF)", size=10, color=MUTED))
    out.append(text(565, 308, "D_body (Q_rr)", size=10, color=POS, bold=True))

    # Земля
    out.append(line(565, 320, 565, 350, color=POS, sw=2.5))
    out.append(line(510, 350, 790, 350, color=INK, sw=2))
    out.append(text(650, 368, "GND (0 В)", size=11, color=INK, bold=True))

    # Навантаження
    out.append(line(565, 230, 670, 230, color=INK, sw=2))
    out.append(rect(670, 210, 80, 40, fill="#fff9c4", stroke=INK, sw=1.5, rx=4))
    out.append(text(710, 234, "L_load", size=12, color=INK, bold=True))

    # Кидок наскрізного струму
    out.append(arrow(565, 125, 565, 340, color=POS, sw=3))
    out.append(text(615, 165, "I_QH = I_load + I_rrm", size=10, color=POS, bold=True))
    out.append(text(615, 295, "−I_rrm крізь діод", size=10, color=POS, bold=True))

    out.append(fitbox(470, 390, 370, 85,
                      "Q_H вмикається на закорочену шину!\n"
                      "Через Q_H тече сумарний струм I_L + I_rrm.\n"
                      "Додаткові динамічні втрати: E_rr ≈ Q_rr · V_bus.\n"
                      "Спад I_rrm генерує перенапругу на Q_L.",
                      fill="#ffebee", stroke=POS, size=11, color=INK))

    render(path, w, h, *out)


# ── 4. parasitic-bjt-latchup.svg ──────────────────────────────────────────
def make_parasitic_bjt_latchup(path):
    w, h = 880, 500
    out = []

    # Заголовок
    out.append(fitbox(20, 15, 840, 38, "Фізика замикання паразитного BJT та динамічного пробою dV/dt", fill=FILL, stroke=LINE, bold=True, size=14))

    # ── Поперечний розріз комірки з траєкторією струму ──
    # Металізація витоку
    out.append(rect(40, 70, 420, 25, fill="#b0bec5", stroke=INK, sw=1.5))
    out.append(text(250, 87, "Металізація витоку (Source)", size=12, color=INK, bold=True))

    # n+ Source
    out.append(rect(60, 95, 100, 45, fill="#ffe082", stroke=INK, sw=1.4))
    out.append(text(110, 122, "n+ Source (Емітер)", size=11, color=INK, bold=True))

    out.append(rect(340, 95, 100, 45, fill="#ffe082", stroke=INK, sw=1.4))
    out.append(text(390, 122, "n+ Source (Емітер)", size=11, color=INK, bold=True))

    # p+ Body контакт
    out.append(rect(200, 95, 100, 45, fill="#ab47bc", stroke=INK, sw=1.4))
    out.append(text(250, 122, "p+ контакт", size=11, color="#ffffff", bold=True))

    # p-Body шар
    out.append(rect(40, 140, 420, 90, fill="#ce93d8", stroke=INK, sw=1.4))
    out.append(text(250, 165, "p-Body область (База паразитного BJT)", size=12, color=INK, bold=True))

    # Опір тіла R_body під n+ витоком
    out.append(rect(75, 180, 70, 20, fill="#ffffff", stroke=POS, sw=1.5))
    out.append(text(110, 194, "R_body", size=11, color=POS, bold=True))

    out.append(rect(355, 180, 70, 20, fill="#ffffff", stroke=POS, sw=1.5))
    out.append(text(390, 194, "R_body", size=11, color=POS, bold=True))

    # n- Drift зона
    out.append(rect(40, 230, 420, 140, fill="#fff9c4", stroke=INK, sw=1.4))
    out.append(text(250, 265, "n- Drift зона (Колектор BJT)", size=12, color=INK, bold=True))

    # Ємнісний струм C_j · dV/dt та струм розсмоктування дірок
    out.append(arrow(110, 330, 110, 210, color=POS, sw=2.2))
    out.append(arrow(110, 200, 200, 140, color=POS, sw=2.2))
    out.append(text(130, 310, "I_hole + C_j·(dV/dt)", size=10, color=POS, bold=True))

    out.append(arrow(390, 330, 390, 210, color=POS, sw=2.2))
    out.append(arrow(390, 200, 300, 140, color=POS, sw=2.2))

    # Металізація стоку
    out.append(rect(40, 370, 420, 25, fill="#b0bec5", stroke=INK, sw=1.5))
    out.append(text(250, 387, "Стік (Drain) — високий потенціал +V_bus", size=12, color=INK, bold=True))

    # ── Права частина: ланцюг аварійного процесу (Causal Chain) ──
    out.append(fitbox(490, 65, 360, 400,
                      "Ланцюг катастрофічного відмикання BJT:\n\n"
                      "1. Snappy-відновлення спричиняє екстремальне\n"
                      "   наростання напруги dV/dt на стоку.\n\n"
                      "2. Струм винесення дірок I_rr та ємнісний\n"
                      "   струм C_oss·(dV/dt) течуть горизонтально\n"
                      "   крізь p-body до контакту витоку.\n\n"
                      "3. На розподіленому опорі R_body під n+ шаром\n"
                      "   виникає падіння напруги:\n"
                      "   V_BE = I_body · R_body.\n\n"
                      "4. Якщо V_BE ≥ 0.7 В, емітерний перехід\n"
                      "   паразитного NPN відкривається!\n\n"
                      "5. NPN входить у лавинне шнурування струму\n"
                      "   (secondary breakdown) → миттєвий\n"
                      "   локальний пропал кристала.",
                      fill="#ffebee", stroke=POS, size=11, color=INK))

    # Формула внизу ліворуч
    out.append(fitbox(40, 410, 420, 65,
                      "Умова безпеки від Latch-up:\n"
                      "V_BE = [ (C_j · dV/dt) + I_rr ] · R_body < 0.7 В",
                      fill="#e8f5e9", stroke=FIELD, bold=True, size=12, color=INK))

    render(path, w, h, *out)


def main():
    figs = {
        "mosfet-parasitic-structure.svg": make_mosfet_parasitic_structure,
        "reverse-recovery-waveform.svg": make_reverse_recovery_waveform,
        "halfbridge-commutation.svg": make_halfbridge_commutation,
        "parasitic-bjt-latchup.svg": make_parasitic_bjt_latchup
    }
    for name, func in figs.items():
        path = os.path.join(IMG, name)
        func(path)
        print(f"Generated {name}")


if __name__ == "__main__":
    main()
