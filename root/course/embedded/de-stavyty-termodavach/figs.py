# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_parasitic_heat_sources():
    w, h = 820, 440
    frags = []

    # Тло друкованої плати
    frags.append(rect(30, 45, 760, 380, fill="#f8fafc", stroke="#0f172a", sw=2, rx=10))
    frags.append(text(410, 72, "Друкована плата: джерела паразитного тепла та мідні шляхи поширення", size=15, bold=True, color="#0f172a"))

    # Мідний полігон землі (GND Plane)
    frags.append(rect(50, 95, 720, 270, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(410, 118, "Суцільний мідний шар GND (товщина 35 мкм, k = 385 Вт/(м·К)) — теплова магістраль", size=12, bold=True, color="#92400e"))

    # Джерело 1: LDO-стабілізатор
    frags.append(rect(75, 140, 170, 110, fill="#fee2e2", stroke=POS, sw=2, rx=6))
    frags.append(text(160, 166, "LDO (5V → 3.3V)", size=13, bold=True, color=POS))
    frags.append(text(160, 188, "Струм: 150 мА", size=11, color="#7f1d1d"))
    frags.append(text(160, 208, "P = (5−3.3)·0.15 = 255 мВт", size=11, bold=True, color=POS))
    frags.append(text(160, 230, "Гаряча точка: +52 °C", size=11, color="#991b1b"))

    # Джерело 2: MCU + Wi-Fi радіотрансивер (ESP32)
    frags.append(rect(295, 135, 210, 130, fill="#fee2e2", stroke=POS, sw=2, rx=6))
    frags.append(text(400, 162, "MCU + Wi-Fi SoC", size=14, bold=True, color=POS))
    frags.append(text(400, 184, "TX сплески: 240 мА", size=11, color="#7f1d1d"))
    frags.append(text(400, 204, "P_сер = 650 мВт", size=12, bold=True, color=POS))
    frags.append(text(400, 226, "ККД PA ~25%, тепло ~400 мВт", size=11, color="#7f1d1d"))
    frags.append(text(400, 248, "Гаряча точка: +65 °C", size=11, bold=True, color="#991b1b"))

    # Джерело 3: DC-DC перетворювач
    frags.append(rect(100, 265, 160, 85, fill="#ffedd5", stroke="#ea580c", sw=1.5, rx=6))
    frags.append(text(180, 290, "DC-DC дросель + ключ", size=12, bold=True, color="#c2410c"))
    frags.append(text(180, 310, "Втрати DCR + комутація", size=11, color="#7c2d12"))
    frags.append(text(180, 330, "P = 180 мВт | +46 °C", size=11, color="#9a3412"))

    # Тепловий потік стрілками
    frags.append(arrow(250, 195, 290, 195, color=POS, sw=2.5))
    frags.append(arrow(510, 195, 595, 195, color=POS, sw=3))
    frags.append(arrow(510, 235, 595, 245, color=POS, sw=2.5))
    frags.append(text(555, 180, "Тепловий потік Q", size=11, bold=True, color=POS))

    # Давач без теплової ізоляції (помилка)
    frags.append(rect(605, 150, 150, 130, fill="#fef2f2", stroke="#dc2626", sw=2, rx=6))
    frags.append(text(680, 178, "Термодавач IC", size=13, bold=True, color="#dc2626"))
    frags.append(text(680, 200, "На суцільній міді", size=11, color="#991b1b"))
    frags.append(text(680, 225, "T_raw = +29.4 °C", size=13, bold=True, color=POS))
    frags.append(text(680, 248, "T_довкілля = +22.0 °C", size=11, color="#1e293b"))
    frags.append(text(680, 268, "Похибка: +7.4 °C!", size=12, bold=True, color="#b91c1c"))

    # Нижній підпис із поясненням механізму
    frags.append(rect(60, 380, 700, 30, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(410, 400, "Мідний шар (k = 385 Вт/(м·К)) проводить тепло у 1200 разів швидше за склотекстоліт FR4 (k = 0.3 Вт/(м·К))", size=11, color="#334155"))

    render(os.path.join(IMG_DIR, "parasitic-heat-sources.svg"), w, h, *frags)


def fig_pcb_thermal_isolation():
    w, h = 840, 440
    frags = []

    frags.append(text(420, 26, "Топологічні прийоми теплової розв'язки термодавача", size=16, bold=True, color="#0f172a"))

    # Ліва панель: Помилкове розміщення
    frags.append(rect(20, 48, 385, 375, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=8))
    frags.append(text(212, 74, "Помилка: давач у суцільному полігоні", size=13, bold=True, color="#b91c1c"))

    # Текстоліт з міддю
    frags.append(rect(40, 95, 345, 230, fill="#fee2e2", stroke="#f87171", sw=1.2, rx=6))
    frags.append(rect(55, 115, 105, 75, fill="#fca5a5", stroke="#dc2626", sw=1.5, rx=4))
    frags.append(text(107, 145, "MCU / LDO", size=12, bold=True, color="#7f1d1d"))
    frags.append(text(107, 168, "+55 °C", size=12, bold=True, color="#991b1b"))

    frags.append(rect(250, 115, 115, 75, fill="#fecaca", stroke="#dc2626", sw=1.5, rx=4))
    frags.append(text(307, 145, "Термодавач", size=12, bold=True, color="#7f1d1d"))
    frags.append(text(307, 168, "+28.8 °C", size=12, bold=True, color="#991b1b"))

    # Стрілка теплового зв'язку
    frags.append(arrow(165, 152, 245, 152, color="#dc2626", sw=3))
    frags.append(text(205, 140, "Q_паразитне", size=10, bold=True, color="#991b1b"))

    frags.append(text(212, 215, "Суцільна мідь GND на всіх шарах", size=11, color="#7f1d1d"))
    frags.append(text(212, 235, "Низький тепловий опір: R_th = 8 К/Вт", size=11, bold=True, color="#991b1b"))
    frags.append(text(212, 258, "Широкий переріз теплопередачі", size=11, color="#7f1d1d"))
    frags.append(text(212, 280, "Постійна часу нагріву: τ ~ 12 с", size=11, color="#7f1d1d"))
    frags.append(text(212, 305, "Паразитний підйом: ΔT = +6.8 °C", size=12, bold=True, color="#b91c1c"))

    frags.append(rect(35, 345, 355, 65, fill="#ffffff", stroke="#fca5a5", sw=1, rx=4))
    frags.append(text(212, 368, "Висновок: давач вимірює нагрів власної плати,", size=10.5, color="#7f1d1d"))
    frags.append(text(212, 388, "а не реальну температуру навколишнього повітря", size=10.5, bold=True, color="#991b1b"))

    # Права панель: Правильне розміщення
    frags.append(rect(435, 48, 385, 375, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=8))
    frags.append(text(627, 74, "Правильно: прорізи та виносний язичок", size=13, bold=True, color="#15803d"))

    # Плата з прорізом
    frags.append(rect(455, 95, 345, 230, fill="#dcfce7", stroke="#86efac", sw=1.2, rx=6))

    # Гарячий блок
    frags.append(rect(470, 115, 95, 75, fill="#fee2e2", stroke="#ef4444", sw=1.5, rx=4))
    frags.append(text(517, 145, "MCU / LDO", size=12, bold=True, color="#7f1d1d"))
    frags.append(text(517, 168, "+55 °C", size=12, bold=True, color="#991b1b"))

    # Фрезерований U-подібний проріз (білий виріз у платі)
    frags.append(rect(580, 105, 14, 150, fill="#ffffff", stroke="#0f172a", sw=1.5, rx=2))
    frags.append(rect(580, 245, 175, 14, fill="#ffffff", stroke="#0f172a", sw=1.5, rx=2))
    frags.append(rect(745, 105, 14, 150, fill="#ffffff", stroke="#0f172a", sw=1.5, rx=2))
    frags.append(text(665, 255, "Фрезерований проріз (Thermal Relief Slot)", size=9.5, bold=True, color="#0f172a"))

    # Виносний язичок
    frags.append(rect(605, 115, 130, 120, fill="#ffffff", stroke="#16a34a", sw=1.8, rx=4))
    frags.append(text(670, 138, "Виносний язичок", size=11, bold=True, color="#15803d"))
    frags.append(rect(625, 150, 90, 45, fill="#bbf7d0", stroke="#16a34a", sw=1.2, rx=3))
    frags.append(text(670, 170, "Термодавач", size=11, bold=True, color="#14532d"))
    frags.append(text(670, 187, "+22.4 °C", size=12, bold=True, color="#15803d"))
    frags.append(text(670, 210, "Keepout під чіпом", size=9.5, color="#166534"))
    frags.append(text(670, 226, "Мідь видалена", size=9.5, color="#166534"))

    # Тонкі доріжки перешийка
    frags.append(line(565, 130, 605, 130, color="#15803d", sw=1.2))
    frags.append(line(565, 140, 605, 140, color="#15803d", sw=1.2))
    frags.append(text(545, 205, "Вузький перешийок", size=9.5, bold=True, color="#15803d"))
    frags.append(text(545, 218, "доріжки 0.15 мм", size=9.5, color="#166534"))

    frags.append(text(627, 278, "Тепловий опір бар'єра: R_th = 145 К/Вт", size=11, bold=True, color="#15803d"))
    frags.append(text(627, 298, "Паразитний нагрів зменшено до: ΔT = +0.4 °C", size=11, bold=True, color="#16a34a"))
    frags.append(text(627, 318, "Ізоляція від конвекції всередині корпусу", size=10, color="#14532d"))

    frags.append(rect(450, 345, 355, 65, fill="#ffffff", stroke="#86efac", sw=1, rx=4))
    frags.append(text(627, 368, "Вирізи відтинають магістралі міді й FR4;", size=10.5, color="#14532d"))
    frags.append(text(627, 388, "давач перебуває в тепловій рівновазі з довкіллям", size=10.5, bold=True, color="#15803d"))

    render(os.path.join(IMG_DIR, "pcb-thermal-isolation.svg"), w, h, *frags)


def fig_thermal_contact_coupling():
    w, h = 820, 420
    frags = []

    frags.append(text(410, 26, "Організація теплового контакту з вимірюваним об'єктом", size=16, bold=True, color="#0f172a"))

    # Об'єкт вимірювання (внизу)
    frags.append(rect(70, 310, 680, 65, fill="#94a3b8", stroke="#475569", sw=2, rx=6))
    frags.append(text(410, 338, "Вимірюваний об'єкт: металевий радіатор / акумулятор / корпус мотора", size=13, bold=True, color="#0f172a"))
    frags.append(text(410, 358, "T_об'єкта = +65.0 °C (низький власний тепловий опір)", size=11, color="#1e293b"))

    # Теплопровідна прокладка (TIM / Gap Pad)
    frags.append(rect(140, 275, 540, 25, fill="#fed7aa", stroke="#f97316", sw=1.5, rx=3))
    frags.append(text(410, 292, "Теплопровідна прокладка TIM (k = 1.5–6.0 Вт/(м·К), товщина 0.5 мм)", size=11, bold=True, color="#9a3412"))

    # Плата FR4 в розрізі
    frags.append(rect(80, 130, 660, 135, fill="#ecfdf5", stroke="#059669", sw=2, rx=6))
    frags.append(text(140, 195, "FR4 плата", size=13, bold=True, color="#047857"))
    frags.append(text(140, 215, "h = 1.6 мм", size=11, color="#065f46"))

    # Нижній відкритий мідний полігон (Bottom Exposed Copper Pad)
    frags.append(rect(230, 255, 360, 10, fill="#f59e0b", stroke="#b45309", sw=1.2, rx=1))

    # Верхній відкритий мідний полігон (Top Exposed Thermal Pad)
    frags.append(rect(270, 120, 280, 10, fill="#f59e0b", stroke="#b45309", sw=1.2, rx=1))

    # Масив металізованих отворів (Thermal Vias Array)
    vias_x = [300, 330, 360, 390, 420, 450, 480, 510]
    for vx in vias_x:
        # Стовпчики переходів
        frags.append(rect(vx - 4, 130, 8, 125, fill="#fde68a", stroke="#d97706", sw=1.2, rx=1))
        # Стрілки передачі тепла вгору
        frags.append(arrow(vx, 240, vx, 145, color=POS, sw=1.5))

    # Пояснювальний блок праворуч
    frags.append(rect(565, 145, 160, 105, fill="#ffffff", stroke="#d97706", sw=1.2, rx=4))
    frags.append(text(645, 168, "Масив 16 отворів", size=11, bold=True, color="#b45309"))
    frags.append(text(645, 188, "Thermal Vias 0.3 мм", size=10, color="#78350f"))
    frags.append(text(645, 208, "Міднення: 25 мкм", size=10, color="#78350f"))
    frags.append(text(645, 230, "R_th(vias) ≈ 3.2 К/Вт", size=10.5, bold=True, color=POS))

    # Термодавач (DFN/QFN корпус)
    frags.append(rect(340, 65, 140, 55, fill="#1e293b", stroke="#0f172a", sw=1.8, rx=4))
    frags.append(text(410, 90, "Термодавач IC", size=12, bold=True, color="#ffffff"))
    frags.append(text(410, 108, "DFN-6 Thermal Pad", size=10, color="#94a3b8"))

    # Теплоізоляційний ковпачок зверху
    frags.append(rect(310, 42, 200, 20, fill="#e2e8f0", stroke="#64748b", sw=1, rx=3))
    frags.append(text(410, 56, "Теплоізоляційна кришка (захист від повітря)", size=9.5, bold=True, color="#334155"))

    # Стрілка теплового контакту знизу
    frags.append(arrow(410, 305, 410, 270, color=POS, sw=2.5))
    frags.append(text(410, 395, "Низький тепловий опір контакту R_th(contact) < 5 К/Вт гарантує швидкий відгук (< 1.5 с)", size=11, color="#334155"))

    render(os.path.join(IMG_DIR, "thermal-contact-coupling.svg"), w, h, *frags)


def fig_thermal_rc_compensation():
    w, h = 840, 420
    frags = []

    frags.append(text(420, 26, "Динамічна алгоритмічна компенсація самонагріву плати", size=16, bold=True, color="#0f172a"))

    # Ліва частина: Еквівалентна теплова RC-схема (Foster Ladder)
    frags.append(rect(25, 55, 370, 345, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(210, 80, "Еквівалентна теплова RC-модель", size=13, bold=True, color="#0f172a"))

    # Джерело теплової потужності P_heat(t)
    frags.append(circle(75, 150, 22, fill="#fee2e2", stroke=POS, sw=2))
    frags.append(text(75, 154, "P(t)", size=13, bold=True, color=POS))
    frags.append(text(75, 190, "Тепловиділення", size=10, color="#7f1d1d"))
    frags.append(text(75, 204, "MCU + RF", size=10, bold=True, color="#991b1b"))

    # Ланка 1: Корпус чіпа (швидка)
    frags.append(line(97, 150, 135, 150, color=LINE, sw=2))
    frags.append(rect(135, 138, 50, 24, fill="#ffffff", stroke="#2563eb", sw=1.8, rx=2))
    frags.append(text(160, 154, "R_th1", size=11, bold=True, color="#1d4ed8"))
    frags.append(line(185, 150, 225, 150, color=LINE, sw=2))

    frags.append(line(205, 150, 205, 185, color=LINE, sw=1.5))
    frags.append(line(195, 185, 215, 185, color="#2563eb", sw=2))
    frags.append(line(195, 192, 215, 192, color="#2563eb", sw=2))
    frags.append(text(235, 190, "C_th1", size=11, bold=True, color="#1d4ed8"))
    frags.append(line(205, 192, 205, 230, color=LINE, sw=1.5))

    frags.append(text(175, 125, "τ_1 ≈ 8 с (чіп)", size=10, bold=True, color="#1e40af"))

    # Ланка 2: Масив плати (повільна)
    frags.append(rect(235, 138, 50, 24, fill="#ffffff", stroke="#059669", sw=1.8, rx=2))
    frags.append(text(260, 154, "R_th2", size=11, bold=True, color="#047857"))
    frags.append(line(285, 150, 325, 150, color=LINE, sw=2))

    frags.append(line(305, 150, 305, 185, color=LINE, sw=1.5))
    frags.append(line(295, 185, 315, 185, color="#059669", sw=2))
    frags.append(line(295, 192, 315, 192, color="#059669", sw=2))
    frags.append(text(335, 190, "C_th2", size=11, bold=True, color="#047857"))
    frags.append(line(305, 192, 305, 230, color=LINE, sw=1.5))

    frags.append(text(275, 125, "τ_2 ≈ 120 с (плата)", size=10, bold=True, color="#065f46"))

    # Спільна земля (T_ambient)
    frags.append(line(170, 230, 340, 230, color=LINE, sw=2))
    frags.append(text(255, 250, "Опора: T_довкілля (GND)", size=11, bold=True, color="#334155"))

    # Формула моделі
    frags.append(rect(40, 275, 340, 110, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=6))
    frags.append(text(210, 298, "Дискретне диференціальне рівняння:", size=11, bold=True, color="#0f172a"))
    frags.append(text(210, 322, "ΔT[n] = α·ΔT[n−1] + (1−α)·R_th·P_heat[n]", size=11, bold=True, color="#2563eb"))
    frags.append(text(210, 344, "де α = exp(−Δt / τ)", size=10.5, color="#475569"))
    frags.append(text(210, 368, "T_відновлене = T_raw[n] − ΔT_модель[n]", size=11, bold=True, color=FIELD))

    # Права частина: Графік перехідного процесу
    frags.append(rect(415, 55, 400, 345, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(615, 80, "Перехідний процес під час сплеску активності", size=13, bold=True, color="#0f172a"))

    # Осі графіка
    frags.append(line(460, 330, 780, 330, color=LINE, sw=1.5))  # Вісь часу
    frags.append(line(460, 330, 460, 110, color=LINE, sw=1.5))  # Вісь температури
    frags.append(text(780, 345, "Час t", size=10, bold=True, color="#475569", anchor="end"))
    frags.append(text(450, 105, "Температура T", size=10, bold=True, color="#475569", anchor="start"))

    # Лінії сітки
    frags.append(line(460, 270, 780, 270, color="#f1f5f9", sw=1, dash="4,3"))
    frags.append(line(460, 190, 780, 190, color="#f1f5f9", sw=1, dash="4,3"))
    frags.append(text(450, 274, "22 °C", size=9.5, color="#64748b", anchor="end"))
    frags.append(text(450, 194, "28 °C", size=9.5, color="#64748b", anchor="end"))

    # Крива 1: Сирі вимірювання T_raw(t) (червона пунктирна)
    # Стрибок з 22 до 28 за експонентою
    p_raw = "M 460 270 C 500 270, 520 200, 620 190 L 770 190"
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6,4"/>' % (p_raw, POS))
    frags.append(text(720, 178, "T_raw (сирі виміри)", size=10.5, bold=True, color=POS))

    # Крива 2: Розрахована поправка ΔT_self(t) (помаранчева)
    p_delta = "M 460 330 C 500 330, 520 260, 620 250 L 770 250"
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (p_delta, "#f59e0b"))
    frags.append(text(720, 240, "ΔT_self (модель нагріву)", size=10, bold=True, color="#d97706"))

    # Крива 3: Відновлена реальна температура довкілля (зелена товста)
    frags.append(line(460, 270, 770, 270, color=FIELD, sw=3))
    frags.append(text(620, 286, "T_довкілля (після компенсації, похибка ±0.2 °C)", size=10.5, bold=True, color="#15803d"))

    # Початок і кінець передачі Wi-Fi TX
    frags.append(line(500, 335, 500, 115, color="#94a3b8", sw=1, dash="2,2"))
    frags.append(text(500, 350, "Старт TX", size=9.5, color="#64748b"))

    frags.append(line(680, 335, 680, 115, color="#94a3b8", sw=1, dash="2,2"))
    frags.append(text(680, 350, "Кінець TX", size=9.5, color="#64748b"))

    render(os.path.join(IMG_DIR, "thermal-rc-compensation.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_parasitic_heat_sources()
    fig_pcb_thermal_isolation()
    fig_thermal_contact_coupling()
    fig_thermal_rc_compensation()
    print("All figures generated successfully.")
