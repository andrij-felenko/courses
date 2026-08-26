# -*- coding: utf-8 -*-
"""Фігури до теми «Скільки живе шина після провалу: hold-up і резервне живлення».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GREEN = FIELD        # норма / безпечно
RED   = POS          # небезпека / аварія / BOR
BLUE  = NEG          # сигнали керування / PVD / попередження
AMBER = "#b9770e"    # перехідна зона / розряд
DARK  = "#1e293b"    # темні блоки


# ── 1. Схемотехнічна архітектура Power Loss Protection ────────────────────────
def fig_holdup_architecture():
    W, H = 1000, 520
    f = [text(W / 2, 30, "Апаратна топологія захисту від знеструмлення: детектування ДО діода",
              size=18, bold=True)]
    f.append(text(W / 2, 52, "Розділення точок вимірювання та накопичення заряду для максимального вікна реакції",
                  size=12, color=MUTED, italic=True))

    # Ліва частина: Вхідна лінія і діодна розв'язка
    # Вхідний роз'єм
    b_in, _, _ = textbox(80, 150, "Вхід живлення\nVIN (9–24 В)", size=11.5, bold=True, fill="#e2e8f0", stroke=DARK)
    f.append(b_in)

    # Лінія від входу
    f.append(line(145, 150, 245, 150, color=DARK, sw=2))
    f.append(circle(195, 150, 3.5, fill=DARK, stroke=DARK))

    # Діод Шотткі / Ідеальний діод
    f.append(rect(245, 125, 80, 50, fill="#fef3c7", stroke=AMBER, sw=1.8))
    f.append(text(285, 146, "Ідеальний", size=11, bold=True, color=AMBER))
    f.append(text(285, 162, "діод (FET)", size=11, bold=True, color=AMBER))
    f.append(line(325, 150, 460, 150, color=DARK, sw=2))

    # Пре-діодна точка моніторингу
    f.append(line(195, 150, 195, 260, color=BLUE, sw=1.8, dash="4,3"))
    f.append(circle(195, 260, 3.5, fill=BLUE, stroke=BLUE))
    f.append(arrow(195, 260, 215, 260, color=BLUE, sw=1.8))

    # Блок компаратора раннього попередження (PFW)
    b_comp, _, _ = textbox(285, 260, "Компаратор PFW\nПоріг: VIN < 90%", size=10.5, bold=True, fill="#dbeafe", stroke=BLUE)
    f.append(b_comp)

    # Накопичувальна шина V_CAP
    f.append(circle(460, 150, 4, fill=DARK, stroke=DARK))
    f.append(text(460, 130, "Шина VCAP (12–24 В)", size=11.5, bold=True, color=DARK))

    # Банк буферних конденсаторів
    f.append(line(460, 150, 460, 235, color=DARK, sw=2))
    b_cap, _, _ = textbox(460, 275, "Буферний банк\nC_hold (Тантал/MLCC)\nE = ½·C·V²", size=10.5, bold=True, fill="#fee2e2", stroke=RED)
    f.append(b_cap)
    f.append(line(460, 315, 460, 340, color=DARK, sw=1.5))
    # Земля для конденсатора
    f.append(line(445, 340, 475, 340, color=DARK, sw=2))
    f.append(line(452, 345, 468, 345, color=DARK, sw=1.5))
    f.append(line(457, 350, 463, 350, color=DARK, sw=1))

    # Перетворювач DC-DC Buck
    f.append(arrow(460, 150, 545, 150, color=DARK, sw=2))
    b_buck, _, _ = textbox(595, 150, "DC-DC Buck\nСтабілізатор\nη ≈ 90%", size=11, bold=True, fill="#f1f5f9", stroke=DARK)
    f.append(b_buck)

    # Вихідна шина 3.3 В
    f.append(line(645, 150, 740, 150, color=GREEN, sw=2.5))
    f.append(circle(690, 150, 4, fill=GREEN, stroke=GREEN))
    f.append(text(690, 130, "Шина 3.3 В (VDD)", size=11.5, bold=True, color=GREEN))

    # Ключ скидання навантаження (Load Switch)
    f.append(line(690, 150, 690, 235, color=DARK, sw=2))
    b_sw, _, _ = textbox(690, 270, "Ключ навантаження\n(Load Switch / P-FET)", size=10.5, bold=True, fill="#fef3c7", stroke=AMBER)
    f.append(b_sw)

    # Периферія (скидається)
    f.append(arrow(690, 305, 690, 355, color=DARK, sw=1.8))
    b_aux, _, _ = textbox(690, 395, "Вторинна периферія:\nДисплей, Радіо, Мотори\n(Миттєво вимикаються)", size=10, fill="#f8fafc", stroke=MUTED)
    f.append(b_aux)

    # Мікроконтролер
    f.append(arrow(740, 150, 795, 150, color=GREEN, sw=2))
    b_mcu, _, _ = textbox(880, 195, "Мікроконтролер (MCU)\n• NMI / PVD переривання\n• Load Shedding (GPIO=0)\n• Екстрений запис\n• Стан сну перед BOR", size=11, bold=True, fill="#e0f2fe", stroke=BLUE, pad=10)
    f.append(b_mcu)

    # Енергонезалежна пам'ять
    f.append(arrow(880, 265, 880, 345, color=DARK, sw=1.8))
    b_mem, _, _ = textbox(880, 385, "Пам'ять стану:\nFRAM / MRAM / Flash\n(Заздалегідь стерта)", size=10.5, bold=True, fill="#dcfce7", stroke=GREEN)
    f.append(b_mem)

    # Сигнал тривоги від компаратора до MCU
    f.append(line(360, 260, 765, 260, color=BLUE, sw=1.8))
    f.append(arrow(765, 260, 795, 230, color=BLUE, sw=1.8))
    f.append(text(580, 250, "Сигнал тривоги NMI / EXTI (0.5 мкс)", size=10, bold=True, color=BLUE))

    # Сигнал відключення ключа від MCU
    f.append(arrow(795, 250, 765, 265, color=AMBER, sw=1.8))
    f.append(text(800, 285, "SHED_EN = 0", size=9.5, bold=True, color=AMBER))

    # Пояснювальний підпис унизу
    f.append(rect(60, 460, 880, 46, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=4))
    f.append(text(500, 480, "Ключовий принцип: моніторинг ДО діода бачить обрив за 1 мкс, поки діод блокує витік енергії з C_hold назад у вхідну мережу.", size=11.5, color=DARK))
    f.append(text(500, 496, "Це дає повний запас енергії буфера для живлення DC-DC та бекапу без жодних паразитних втрат.", size=10.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "holdup-architecture.svg"), W, H, *f)


# ── 2. Часова діаграма розряду та збереження даних ────────────────────────────
def fig_holdup_waveforms():
    W, H = 1000, 530
    f = [text(W / 2, 30, "Часова шкала події знеструмлення: від провалу до спрацювання BOR",
              size=18, bold=True)]
    f.append(text(W / 2, 52, "Послідовність реакції: тривога NMI → скидання навантаження → запис у пам'ять → захисне скидання",
                  size=12, color=MUTED, italic=True))

    ox, oy = 110, 80
    gw, gh = 810, 360

    # Сітка часу
    f.append(line(ox, oy, ox, oy + gh, color=INK, sw=1.8))            # вісь V
    f.append(line(ox, oy + gh, ox + gw, oy + gh, color=INK, sw=1.8))  # вісь t
    f.append(text(ox + gw - 20, oy + gh + 28, "Час (t) →", size=12, bold=True, color=INK))

    # Часові маркери
    t_fail = ox + 100
    t_nmi  = ox + 130
    t_shed = ox + 170
    t_save = ox + 430
    t_drop = ox + 600
    t_bor  = ox + 720

    # Вертикальні лінії подій
    events = [
        (t_fail, "t0: Обрив VIN", RED),
        (t_nmi,  "t1: Поріг PFW (NMI)", BLUE),
        (t_shed, "t2: Load Shedding", AMBER),
        (t_save, "t3: Запис завершено", GREEN),
        (t_drop, "t4: Dropout Buck", AMBER),
        (t_bor,  "t5: Скидання BOR", RED),
    ]

    for tx, lbl, col in events:
        f.append(line(tx, oy + 20, tx, oy + gh, color=col, sw=1.2, dash="4,3"))
        f.append(text(tx, oy + 12, lbl, size=10, bold=True, color=col))

    # 1. Графік VIN_RAW (падає миттєво до нуля)
    f.append(text(ox - 10, oy + 45, "VIN", size=11.5, bold=True, color=DARK, anchor="end"))
    f.append(line(ox, oy + 45, t_fail, oy + 45, color=DARK, sw=2))
    f.append(line(t_fail, oy + 45, t_nmi, oy + 240, color=DARK, sw=2))
    f.append(line(t_nmi, oy + 240, ox + gw - 30, oy + 240, color=DARK, sw=1.5))

    # 2. Графік V_CAP (розряджається спочатку швидко, після load shed — повільно)
    f.append(text(ox - 10, oy + 75, "VCAP", size=11.5, bold=True, color=RED, anchor="end"))
    f.append(line(ox, oy + 75, t_fail, oy + 75, color=RED, sw=2.5))
    # Спад до shed (крутіший)
    f.append(line(t_fail, oy + 75, t_shed, oy + 105, color=RED, sw=2.5))
    # Спад після shed (пологий, збереження)
    f.append(line(t_shed, oy + 105, t_drop, oy + 195, color=RED, sw=2.5))
    f.append(line(t_drop, oy + 195, t_bor + 50, oy + 290, color=RED, sw=2, dash="3,2"))

    # 3. Графік VDD 3.3 В (тримається стабільно аж до t_drop!)
    f.append(text(ox - 10, oy + 155, "VDD 3.3V", size=11.5, bold=True, color=GREEN, anchor="end"))
    f.append(line(ox, oy + 155, t_drop, oy + 155, color=GREEN, sw=3))
    # Падіння 3.3 В після вичерпання буфера
    f.append(line(t_drop, oy + 155, t_bor, oy + 235, color=GREEN, sw=2.5))
    f.append(line(t_bor, oy + 235, ox + gw - 30, oy + 320, color=MUTED, sw=1.8, dash="3,2"))

    # Пороги напруг
    f.append(line(ox, oy + 235, t_bor, oy + 235, color=RED, sw=1.2, dash="2,2"))
    f.append(text(ox - 10, oy + 238, "VBOR (2.7 В)", size=10, bold=True, color=RED, anchor="end"))

    # Інтервали: Вікно збереження та запас надійності (на рівні y=330..370)
    # Вікно Hold-Up Time
    f.append(line(t_fail, oy + 270, t_drop, oy + 270, color=BLUE, sw=2))
    f.append(line(t_fail, oy + 262, t_fail, oy + 278, color=BLUE, sw=2))
    f.append(line(t_drop, oy + 262, t_drop, oy + 278, color=BLUE, sw=2))
    f.append(text((t_fail + t_drop) / 2, oy + 263, "Час утримання стабільної шини (t_hold ≈ 10–50 мс)", size=10.5, bold=True, color=BLUE))

    # Вікно активного запису
    f.append(rect(t_shed + 2, oy + 285, t_save - t_shed - 4, 20, fill="#bbf7d0", stroke=GREEN, sw=1.2, rx=3))
    f.append(text((t_shed + t_save) / 2, oy + 299, "Екстрений Flash/FRAM запис (t_save ≈ 1–4 мс)", size=9.5, bold=True, color="#166534"))

    # Запас безпеки
    f.append(rect(t_save + 2, oy + 285, t_drop - t_save - 4, 20, fill="#fef08a", stroke=AMBER, sw=1.2, rx=3))
    f.append(text((t_save + t_drop) / 2, oy + 299, "Запас надійності (Safety Margin)", size=9.5, bold=True, color="#854d0e"))

    # Стан MCU внизу (на рівні y=395..425)
    f.append(rect(ox + 10, oy + gh - 40, t_shed - ox - 14, 28, fill="#e2e8f0", stroke=DARK, rx=4))
    f.append(text((ox + 10 + t_shed - 4) / 2, oy + gh - 22, "Нормальна робота", size=9.5, bold=True, color=DARK))

    f.append(rect(t_shed + 2, oy + gh - 40, t_save - t_shed - 4, 28, fill="#dbeafe", stroke=BLUE, rx=4))
    f.append(text((t_shed + t_save) / 2, oy + gh - 22, "Flush стану в NVRAM", size=9.5, bold=True, color=BLUE))

    f.append(rect(t_save + 2, oy + gh - 40, t_bor - t_save - 4, 28, fill="#f1f5f9", stroke=MUTED, rx=4))
    f.append(text((t_save + t_bor) / 2, oy + gh - 22, "Safe Sleep (WFI / Low-I)", size=9.5, bold=True, color=MUTED))

    f.append(rect(t_bor + 2, oy + gh - 40, ox + gw - t_bor - 24, 28, fill="#fee2e2", stroke=RED, rx=4))
    f.append(text((t_bor + ox + gw - 22) / 2, oy + gh - 22, "Апаратний BOR Reset", size=9.5, bold=True, color=RED))

    # Підсумковий напис
    f.append(text(W / 2, 505, "Головне інженерне правило: t_hold мусить щонайменше в 2–3 рази перевищувати найгірший час запису t_save.", size=11.5, bold=True, color=DARK))

    render(os.path.join(IMG, "holdup-waveforms.svg"), W, H, *f)


# ── 3. Порівняння технологій накопичувачів енергії ────────────────────────────
def fig_storage_technologies():
    W, H = 1000, 500
    f = [text(W / 2, 30, "Порівняння накопичувачів енергії для аварійного утримання шини",
              size=18, bold=True)]
    f.append(text(W / 2, 52, "Компроміси між питомою ємністю, паразитним опором (ESR), робочою напругою та надійністю",
                  size=12, color=MUTED, italic=True))

    cards = [
        {
            "x": 60, "w": 205,
            "title": "Кераміка (MLCC X7R)",
            "color": "#0284c7", "fill": "#f0f9ff",
            "time": "0.1 ... 2 мс",
            "esr": "1 ... 5 мОм (ідеально)",
            "volt": "до 50 В (висока)",
            "plus": "• Наднизький ESR\n• Немає старіння\n• Компактні SMD 0805–1210",
            "minus": "• DC-bias зрізає 70% C\n• П'єзотріск/тріщини\n• Мала ємність (<100 мкФ)"
        },
        {
            "x": 290, "w": 205,
            "title": "Полімерний тантал",
            "color": "#059669", "fill": "#ecfdf5",
            "time": "2 ... 30 мс",
            "esr": "10 ... 35 мОм (відмінно)",
            "volt": "6.3 ... 35 В (помірна)",
            "plus": "• Немає ефекту DC-bias\n• Стабільний ESR на морозі\n• Безпечна відмова (полімер)",
            "minus": "• Вища ціна\n• Струм витоку вищий\n• Потрібен derating 10–20%"
        },
        {
            "x": 520, "w": 205,
            "title": "Алюміній-електроліт",
            "color": "#d97706", "fill": "#fffbeb",
            "time": "10 ... 100 мс",
            "esr": "0.1 ... 1.5 Ом (посередньо)",
            "volt": "до 100 В (висока)",
            "plus": "• Найдешевша фарада\n• Величезний вибір\n• Стійкість до сплесків",
            "minus": "• Висихання при нагріві\n• ESR стрибає в 50× при -40°C\n• Великі габарити"
        },
        {
            "x": 750, "w": 205,
            "title": "Іоністори (Supercaps)",
            "color": "#7c3aed", "fill": "#faf5ff",
            "time": "0.1 ... 10 секунд",
            "esr": "0.05 ... 20 Ом (високий)",
            "volt": "2.7 В (низька, послід.)",
            "plus": "• Колосальна ємність (Ф)\n• Довгий бекап систем\n• Мільйони циклів",
            "minus": "• Потрібне балансування\n• Великий ESR (coin cell)\n• Струм заряджання inrush"
        }
    ]

    top_y = 85
    card_h = 360

    for c in cards:
        # Рамка картки
        f.append(rect(c["x"], top_y, c["w"], card_h, fill=c["fill"], stroke=c["color"], sw=2, rx=8))

        # Заголовок картки
        f.append(rect(c["x"], top_y, c["w"], 38, fill=c["color"], stroke=c["color"], rx=8))
        f.append(text(c["x"] + c["w"] / 2, top_y + 24, c["title"], size=13, bold=True, color="#ffffff"))

        # Параметри
        py = top_y + 60
        f.append(text(c["x"] + 12, py, "Час утримання:", size=10.5, bold=True, color=DARK, anchor="start"))
        f.append(text(c["x"] + c["w"] - 12, py, c["time"], size=11, bold=True, color=c["color"], anchor="end"))

        py += 24
        f.append(text(c["x"] + 12, py, "Паразитний ESR:", size=10.5, bold=True, color=DARK, anchor="start"))
        f.append(text(c["x"] + c["w"] - 12, py, c["esr"], size=10, color=DARK, anchor="end"))

        py += 24
        f.append(text(c["x"] + 12, py, "Робоча напруга:", size=10.5, bold=True, color=DARK, anchor="start"))
        f.append(text(c["x"] + c["w"] - 12, py, c["volt"], size=10, color=DARK, anchor="end"))

        f.append(line(c["x"] + 10, py + 14, c["x"] + c["w"] - 10, py + 14, color="#cbd5e1", sw=1))

        # Переваги
        py += 32
        f.append(text(c["x"] + 12, py, "Переваги:", size=11, bold=True, color=GREEN, anchor="start"))
        for line_txt in c["plus"].split("\n"):
            py += 18
            f.append(text(c["x"] + 12, py, line_txt, size=10.5, color=DARK, anchor="start"))

        # Недоліки
        py += 26
        f.append(text(c["x"] + 12, py, "Обмеження та ризики:", size=11, bold=True, color=RED, anchor="start"))
        for line_txt in c["minus"].split("\n"):
            py += 18
            f.append(text(c["x"] + 12, py, line_txt, size=10.5, color=DARK, anchor="start"))

    # Пояснення внизу
    f.append(text(W / 2, 475, "Золотий стандарт для надійних MCU-пристроїв: Полімерний тантал або комбінація MLCC + Тантал на високовольтній шині 12–24 В.", size=11.5, bold=True, color=DARK))

    render(os.path.join(IMG, "storage-technologies.svg"), W, H, *f)


if __name__ == '__main__':
    fig_holdup_architecture()
    fig_holdup_waveforms()
    fig_storage_technologies()
    print("All figures generated successfully.")
