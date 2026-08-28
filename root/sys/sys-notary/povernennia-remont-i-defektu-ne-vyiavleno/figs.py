# -*- coding: utf-8 -*-
"""figs.py — генератор ілюстрацій для теми povernennia-remont-i-defektu-ne-vyiavleno (sys-notary).
Генерує 2 SVG-схеми в ./img/ за допомогою спільного svgkit.
"""
import sys, os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
sys.path.insert(0, os.path.join(SCRIPT_DIR, '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(SCRIPT_DIR, "img"), exist_ok=True)

def polyline(pts, color=LINE, sw=1.5):
    """З'єднані відрізки ліній."""
    return "".join(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color=color, sw=sw) for i in range(len(pts)-1))


# ── Фігура 1: Діагностичний маршрут RMA та локалізація NFF ───────────────────
def fig_nff_diagnostic_flowchart():
    W, H = 1040, 680
    P = []
    P.append(text(W / 2, 28, "Діагностичний маршрут RMA: локалізація інтермітуючих дефектів і NFF", size=16, bold=True))

    # Колонка 1: Вхідний контроль і чорна скринька
    P.append(rect(25, 55, 230, 600, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    P.append(text(140, 80, "1. ВХІД І ТЕЛЕМЕТРІЯ", size=13, bold=True, color="#1e293b"))

    P.append(fitbox(40, 105, 200, 110, "Прийом виробу (RMA)\nРеєстрація скарги клієнта\nВізуальний огляд корпусу\nПеревірка пломб та вологи", size=11, fill="#e2e8f0", stroke="#64748b", bold=False))
    P.append(arrow(140, 215, 140, 240, color="#64748b", sw=2))

    P.append(fitbox(40, 240, 200, 125, "Зчитування Crash Dump\nВичитка енергонезалежної\nпам'яті (FRAM / Flash)\nАналіз лічильників BOR/WDT\nСкидання дампа регістрів", size=11, fill="#e0e7ff", stroke="#4338ca", bold=False))
    P.append(arrow(140, 365, 140, 390, color="#64748b", sw=2))

    P.append(fitbox(40, 390, 200, 110, "Стендовий статичний тест\nПеревірка за 25 °C і V_nom\nБазовий функціональний тест\nВимірювання струмів споживання", size=11, fill="#fef3c7", stroke="#d97706", bold=False))
    P.append(arrow(140, 500, 140, 525, color="#64748b", sw=2))

    P.append(fitbox(40, 525, 200, 105, "Початкова розвилка\nДефект є на столі?\nТАК → Прямий ремонт\nНІ → Підозра на NFF/CND", size=11, fill="#ecfdf5", stroke="#047857", bold=False))

    # Стрілка переходу від Колонки 1 до Колонки 2
    P.append(arrow(240, 577, 275, 577, color="#047857", sw=2))

    # Колонка 2: Багатофакторний стрес-комплекс (HALT / HASS)
    P.append(rect(280, 55, 460, 600, fill="#fdf4ff", stroke="#c084fc", sw=1.5, rx=8))
    P.append(text(510, 80, "2. БАГАТОФАКТОРНИЙ СТРЕС-ПРОСІВ (HALT / HASS)", size=13, bold=True, color="#581c87"))

    stress_blocks = [
        ("Термічний градієнт (Thermal Shock)", "Швидка зміна: -40 °C ↔ +85 °C (до 60 °C/хв)\nВиявлення CTE-розривів та мікротріщин BGA", "#fae8ff", "#a855f7", 105),
        ("Електричний марджинінг (Voltage Margining)", "Коливання живлення: V_core ±10%, V_io ±5%\nПеревірка часових затримок і просідання LDO", "#fce7f3", "#db2777", 225),
        ("Широкосмугова вібрація (6-DOF Vibration)", "Псевдовипадкова вібрація 10–2000 Гц (до 20 Grms)\nФретинг-корозія та деградація роз'ємів", "#ffe4e6", "#e11d48", 345),
        ("Граничне навантаження шин (Bus Saturation)", "100% навантаження DMA, SPI, PCIe, eMMC\nВиявлення збоїв синхронізації та джиттеру", "#ede9fe", "#7c3aed", 465)
    ]

    for title, desc, f_c, s_c, y_pos in stress_blocks:
        P.append(fitbox(300, y_pos, 420, 95, title + "\n" + desc, size=11, fill=f_c, stroke=s_c, bold=False))
        if y_pos < 465:
            P.append(arrow(510, y_pos + 95, 510, y_pos + 120, color="#a855f7", sw=1.8))

    # Стрілки з Колонки 2 до Колонки 3
    P.append(arrow(720, 272, 765, 272, color="#db2777", sw=2))
    P.append(arrow(720, 512, 765, 512, color="#7c3aed", sw=2))

    # Колонка 3: Сепарація та фінальні вердикти
    P.append(rect(770, 55, 245, 600, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    P.append(text(892, 80, "3. КЛАСИФІКАЦІЯ Й ДІЯ", size=13, bold=True, color="#1e293b"))

    P.append(fitbox(785, 115, 215, 120, "ДЕФЕКТ СПРОВОКОВАНО\nЛокалізовано збій BGA,\nдеградацію LDO/MLCC\nабо race condition\nШлях: Компонентний ремонт", size=11, fill="#dcfce7", stroke="#16a34a", bold=False))
    P.append(arrow(892, 235, 892, 275, color="#16a34a", sw=2))

    P.append(fitbox(785, 275, 215, 140, "8D / CAPA АНАЛІЗ\nОновлення трасування PCB\nКорекція профілю паяння\nПатч таймінгів прошивки\nЗниження рівня повернень", size=11, fill="#f0fdf4", stroke="#15803d", bold=False))
    P.append(arrow(892, 415, 892, 455, color="#64748b", sw=2))

    P.append(fitbox(785, 455, 215, 175, "ІСТИННИЙ NFF / CND\nДефект не проявився за\nвсіх стрес-границь HALT\n1. Перевірка кабелів клієнта\n2. Оновлення прошивки\n3. Встановлення логера\n4. Карантин або повернення", size=11, fill="#fee2e2", stroke="#b91c1c", bold=False))

    render("img/nff-diagnostic-flowchart.svg", W, H, *P)


# ── Фігура 2: Багатофакторний цикл відтворення інтермітуючих відмов ───────────
def fig_intermittent_fault_reproduction_cycle():
    W, H = 1000, 620
    P = []
    P.append(text(W / 2, 28, "Синхронний багатофакторний стрес-профіль для відтворення NFF-дефектів", size=16, bold=True))

    # Центральна область: взаємодія чотирьох векторів навантаження
    # Верхній лівий: Температурний профіль
    P.append(rect(40, 60, 440, 240, fill="#fffbeb", stroke="#f59e0b", sw=1.5, rx=8))
    P.append(text(260, 88, "ВЕКТОР 1: ТЕРМІЧНИЙ ДРЕЙФ І ДЕЛЬТА-Т", size=12, bold=True, color="#b45309"))
    P.append(line(55, 220, 450, 220, color="#d97706", sw=1.2, dash="4,4"))
    # Крива температури
    P.append(polyline([(65, 220), (120, 220), (170, 120), (270, 120), (320, 250), (410, 250), (440, 220)], color="#dc2626", sw=2.5))
    P.append(text(95, 210, "+25 °C", size=10, color="#4b5563"))
    P.append(text(220, 110, "+85 °C (CTE розширення)", size=10, color="#b91c1c", bold=True))
    P.append(text(360, 270, "-40 °C (стискання)", size=10, color="#1d4ed8", bold=True))
    P.append(fitbox(55, 135, 120, 65, "dT/dt до 60 °C/хв\nЗсув шарів BGA\nі відкриття тріщин", size=9.5, fill="#ffffff", stroke="#f59e0b"))

    # Верхній правий: Електричний марджинінг живлення
    P.append(rect(520, 60, 440, 240, fill="#f0fdf4", stroke="#10b981", sw=1.5, rx=8))
    P.append(text(740, 88, "ВЕКТОР 2: ДИНАМІЧНИЙ МАРДЖИНІНГ VDD", size=12, bold=True, color="#047857"))
    P.append(line(535, 175, 930, 175, color="#059669", sw=1.2, dash="4,4"))
    # Ступінчастий графік живлення
    P.append(polyline([(545, 175), (600, 175), (630, 130), (710, 130), (740, 220), (830, 220), (860, 175), (920, 175)], color="#059669", sw=2.5))
    P.append(text(575, 165, "3.30 В", size=10, color="#4b5563"))
    P.append(text(670, 120, "3.63 В (+10%) Fast Corner", size=10, color="#047857", bold=True))
    P.append(text(785, 240, "2.97 В (-10%) Slow Corner", size=10, color="#b91c1c", bold=True))
    P.append(fitbox(830, 135, 120, 65, "Граничні затримки\nsetup/hold time\nПросідання LDO", size=9.5, fill="#ffffff", stroke="#10b981"))

    # Нижній лівий: Вібраційний та ударний вплив
    P.append(rect(40, 320, 440, 240, fill="#fdf2f8", stroke="#ec4899", sw=1.5, rx=8))
    P.append(text(260, 348, "ВЕКТОР 3: ВИПАДКОВА ШИРОКОСМУГОВА ВІБРАЦІЯ", size=12, bold=True, color="#be185d"))
    # Вібраційна хвиля
    vib_pts = [(55, 440), (80, 410), (105, 470), (130, 390), (155, 490), (180, 380), (205, 500),
               (230, 400), (255, 480), (280, 410), (305, 470), (330, 390), (355, 490), (380, 420), (410, 460), (440, 440)]
    P.append(polyline(vib_pts, color="#db2777", sw=2))
    P.append(text(260, 375, "Спектр 10–2000 Гц, 6–20 Grms (6-DOF)", size=10.5, color="#9d174d", bold=True))
    P.append(fitbox(55, 490, 175, 55, "Динамічний вигин друкованої плати\nМікропереміщення контактів (фретинг)", size=9.5, fill="#ffffff", stroke="#ec4899"))
    P.append(fitbox(270, 490, 190, 55, "Короткочасні розмикання 10–500 нс\nВтрата пакетів інтерфейсів", size=9.5, fill="#ffffff", stroke="#ec4899"))

    # Нижній правий: Трафік шин і циклічні переривання
    P.append(rect(520, 320, 440, 240, fill="#f5f3ff", stroke="#8b5cf6", sw=1.5, rx=8))
    P.append(text(740, 348, "ВЕКТОР 4: АКТИВНІСТЬ ШИН ТА ПЕРЕРИВАНЬ", size=12, bold=True, color="#6d28d9"))
    # Імпульсні пачки
    burst_pts = [(545, 450), (565, 450), (565, 390), (615, 390), (615, 450), (635, 450),
                 (635, 380), (705, 380), (705, 450), (725, 450), (725, 390), (795, 390), (795, 450), (920, 450)]
    P.append(polyline(burst_pts, color="#7c3aed", sw=2))
    P.append(text(740, 375, "Синхронний DMA + SPI/eMMC + перемикання GPIO", size=10, color="#5b21b6", bold=True))
    P.append(fitbox(535, 475, 185, 65, "Струмові сплески dI/dt\nІндукування Ground Bounce\nі перехресних наводок (Crosstalk)", size=9.5, fill="#ffffff", stroke="#8b5cf6"))
    P.append(fitbox(745, 475, 195, 65, "Стрес-верифікація пам'яті\nВиявлення бітових фліпів\nта помилок CRC у реальному часі", size=9.5, fill="#ffffff", stroke="#8b5cf6"))

    # Нижній підсумковий банер
    P.append(rect(40, 575, 920, 35, fill="#1e293b", stroke="#0f172a", sw=1.5, rx=6))
    P.append(text(500, 597, "РЕЗУЛЬТАТ: ПЕРЕТВОРЕННЯ ПРИХОВАНИХ ІНТЕРМІТУЮЧИХ ЗБОЇВ НА ДЕТЕКТОВАНІ СИСТЕМНІ ПОМИЛКИ", size=11, bold=True, color="#38bdf8"))

    render("img/intermittent-fault-reproduction-cycle.svg", W, H, *P)


if __name__ == "__main__":
    fig_nff_diagnostic_flowchart()
    fig_intermittent_fault_reproduction_cycle()
    print("SVG figures generated successfully.")
