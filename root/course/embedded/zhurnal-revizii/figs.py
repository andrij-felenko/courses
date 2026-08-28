# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «Журнал ревізії А».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Життєвий цикл і трасування плат прототипної партії ───────────────────
def fig_board_id_tracking():
    W, H = 860, 400
    el = []
    el.append(text(W/2, 26, "Трасування партії прототипів: від голої плати до рольового призначення", size=16, bold=True))

    stages = [
        ("1. Реєстрація ID", "#f8fafc", "#e2e8f0", [
            "• Присвоєння Serial ID",
            "• QR-код / маркування",
            "• Зв'язування з MCU UID",
            "• Запис дати й монтажника"
        ]),
        ("2. Холодний аудит", "#f8fafc", "#fef3c7", [
            "• Опір рейок до GND",
            "• Діодна продзвонка ESD",
            "• Контроль ключа Pin 1",
            "• Оптична інспекція QFN"
        ]),
        ("3. Перший вольт", "#f8fafc", "#fee2e2", [
            "• Струм у скиданні (NRST=0)",
            "• Напруги в точках TP",
            "• Тепловізорний скринінг",
            "• Осцилограма рейок LDO"
        ]),
        ("4. Прошивка й ролі", "#f8fafc", "#dcfce7", [
            "• Тестовий ранер (UID/I2C)",
            "• Робочий струм (Active/Sleep)",
            "• Фіксація патчів у журналі",
            "• Розподіл плат за ролями"
        ])
    ]

    col_w = 185
    col_gap = 25
    x_start = 28
    y0 = 60
    h_box = 215

    for i, (title, f_body, f_head, items) in enumerate(stages):
        x = x_start + i * (col_w + col_gap)
        el.append(rect(x, y0, col_w, h_box, fill=f_body, stroke=LINE, sw=1.5, rx=8))
        el.append(rect(x, y0, col_w, 36, fill=f_head, stroke=LINE, sw=1.5, rx=8))
        el.append(text(x + col_w/2, y0 + 23, title, size=12.5, bold=True, color=INK))

        for j, it in enumerate(items):
            el.append(text(x + 12, y0 + 64 + j * 36, it, size=11, anchor="start", color=INK))

        if i < 3:
            ax1 = x + col_w + 3
            ax2 = x + col_w + col_gap - 3
            ay = y0 + h_box/2
            el.append(arrow(ax1, ay, ax2, ay, color=LINE, sw=1.8))

    # Нижній блок розподілу ролей
    el.append(rect(28, 295, 804, 85, fill="#f1f5f9", stroke=LINE, sw=1.2, rx=6))
    el.append(text(430, 316, "Розподіл плат партії за інженерними завданнями (Board Disposition)", size=12.5, bold=True, color=INK))
    
    roles = [
        ("SN-01: Golden Sample", "Еталон без патчів для калібрування"),
        ("SN-02..03: Firmware Bench", "Основний стенд розробки драйверів"),
        ("SN-04: Stress & Thermal", "Кліматична камера та граничні струми"),
        ("SN-05: Patch Pioneer", "Плата для первинної перевірки доробок")
    ]
    for k, (r_name, r_desc) in enumerate(roles):
        rx = 42 + (k % 2) * 400
        ry = 340 + (k // 2) * 26
        el.append(text(rx, ry, f"• {r_name}:", size=11, bold=True, anchor="start", color=INK))
        el.append(text(rx + 155, ry, r_desc, size=11, anchor="start", color=MUTED))

    render(os.path.join(IMG, "board-id-tracking.svg"), W, H, *el)


# ── 2. Анатомія апаратного патчу (Bodge Wire / Patch Log) ───────────────────
def fig_hardware_patch_anatomy():
    W, H = 860, 420
    el = []
    el.append(text(W/2, 26, "Анатомія інженерного патчу: перерізання доріжки, синій дріт і фіксація", size=16, bold=True))

    # Ліва панель: графічне зображення ділянки плати з патчем
    x_pcb, y_pcb, w_pcb, h_pcb = 30, 60, 420, 335
    el.append(rect(x_pcb, y_pcb, w_pcb, h_pcb, fill="#1e3a1e", stroke=LINE, sw=1.5, rx=8)) # темно-зелена маска PCB
    el.append(text(x_pcb + 20, y_pcb + 26, "Топологія ділянки PCB з апаратним патчем", size=12, bold=True, color="#ffffff", anchor="start"))

    # Мідні контактні майданчики мікросхеми U2 (SOIC / DFN)
    for p in range(4):
        py = y_pcb + 70 + p * 38
        # ліві виводи
        el.append(rect(x_pcb + 60, py, 28, 14, fill="#d4af37", stroke="#856404", sw=1.0, rx=2))
        el.append(text(x_pcb + 48, py + 11, f"Pin {p+1}", size=9.5, color="#e2e8f0", anchor="end"))
        # праві виводи
        el.append(rect(x_pcb + 140, py, 28, 14, fill="#d4af37", stroke="#856404", sw=1.0, rx=2))
        el.append(text(x_pcb + 180, py + 11, f"Pin {8-p}", size=9.5, color="#e2e8f0", anchor="start"))

    # Корпус мікросхеми U2
    el.append(rect(x_pcb + 88, y_pcb + 60, 52, 145, fill="#2b2b2b", stroke="#555555", sw=1.5, rx=4))
    el.append(circle(x_pcb + 100, y_pcb + 74, 3, fill="#888888", stroke="#aaaaaa", sw=0.8)) # Pin 1 dot
    el.append(text(x_pcb + 114, y_pcb + 135, "U2", size=13, bold=True, color="#ffffff"))

    # Резистор R12 (SMD 0603)
    rx0, ry0 = x_pcb + 280, y_pcb + 100
    el.append(rect(rx0, ry0, 16, 26, fill="#d4af37", stroke="#856404", sw=1.0, rx=2))
    el.append(rect(rx0 + 16, ry0 + 3, 30, 20, fill="#1a1a1a", stroke="#444444", sw=1.0, rx=2))
    el.append(rect(rx0 + 46, ry0, 16, 26, fill="#d4af37", stroke="#856404", sw=1.0, rx=2))
    el.append(text(rx0 + 31, ry0 + 18, "R12", size=9.5, bold=True, color="#ffffff"))

    # Доріжка від U2 Pin 2 до R12 (початкова помилкова)
    el.append(line(x_pcb + 74, y_pcb + 115, rx0, ry0 + 13, color="#d4af37", sw=3.0))

    # Місце перерізання доріжки (Trace Cut)
    cut_x = x_pcb + 185
    cut_y = y_pcb + 115
    el.append(line(cut_x - 8, cut_y - 8, cut_x + 8, cut_y + 8, color=POS, sw=2.5))
    el.append(line(cut_x - 8, cut_y + 8, cut_x + 8, cut_y - 8, color=POS, sw=2.5))
    el.append(f'<circle cx="{cut_x}" cy="{cut_y}" r="12" fill="none" stroke="{POS}" stroke-width="1.5" stroke-dasharray="3,3"/>')

    # Тестова точка TP4
    tp_x, tp_y = x_pcb + 320, y_pcb + 260
    el.append(circle(tp_x, tp_y, 14, fill="#d4af37", stroke="#856404", sw=1.5))
    el.append(text(tp_x, tp_y + 4, "TP4", size=9, bold=True, color="#1e3a1e"))

    # Синій провідник патчу (Bodge Wire Kynar 30 AWG)
    # З'єднує U2 Pin 2 з TP4
    path_d = f"M {x_pcb + 74} {y_pcb + 115} Q {x_pcb + 30} {y_pcb + 220} {x_pcb + 130} {y_pcb + 270} T {tp_x} {tp_y}"
    el.append(f'<path d="{path_d}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')

    # Краплі УФ-маски для механічного розвантаження (Strain Relief)
    el.append(circle(x_pcb + 80, y_pcb + 195, 7, fill="#27ae60", stroke="#1e824c", sw=1.2))
    el.append(circle(x_pcb + 210, y_pcb + 280, 8, fill="#27ae60", stroke="#1e824c", sw=1.2))

    # Підписи до елементів топології
    el.append(text(cut_x, cut_y - 18, "1. Переріз доріжки (Cut)", size=10, bold=True, color="#ff7675"))
    el.append(text(x_pcb + 65, y_pcb + 295, "2. Дріт Kynar AWG 30", size=10, bold=True, color="#74b9ff", anchor="start"))
    el.append(text(x_pcb + 225, y_pcb + 300, "3. Фіксація клеєм (UV)", size=10, bold=True, color="#55efc4", anchor="start"))

    # Права панель: Обов'язкова структура картки в журналі патчів
    x_card, y_card, w_card, h_card = 475, 60, 355, 335
    el.append(rect(x_card, y_card, w_card, h_card, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    el.append(rect(x_card, y_card, w_card, 36, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=8))
    el.append(text(x_card + w_card/2, y_card + 23, "Картка апаратного патчу (Patch Log Entry)", size=12.5, bold=True, color=INK))

    fields = [
        ("Ідентифікатор:", "PATCH-REV_A-003"),
        ("Першопричина:", "Переплутано TX/RX на UART1"),
        ("Дія 1 (Cut):", "Різ доріжки між U2.Pin2 та R12"),
        ("Дія 2 (Bodge):", "Дріт 30 AWG: U2.Pin2 → TP4"),
        ("Фіксація:", "2 краплі УФ-маски зелені"),
        ("Плат зачеплено:", "Всі (SN-01..SN-05)"),
        ("Вплив на FW:", "Без змін (відповідає схемі)"),
        ("Статус для Rev B:", "ECO-104: Swap UART1 nets")
    ]

    for i, (label, val) in enumerate(fields):
        fy = y_card + 62 + i * 33
        el.append(text(x_card + 14, fy, label, size=11, bold=True, anchor="start", color=INK))
        el.append(text(x_card + 130, fy, val, size=11, anchor="start", color="#1e40af" if i == 0 or i == 7 else MUTED))

    render(os.path.join(IMG, "hardware-patch-anatomy.svg"), W, H, *el)


# ── 3. Тепловізійні патерни типових апаратних дефектів ──────────────────────
def fig_thermal_profile_faults():
    W, H = 860, 390
    el = []
    el.append(text(W/2, 26, "Тепловий моніторинг першого старту: сигнатури дефектів", size=16, bold=True))

    cards = [
        ("A. Точковий пробій MLCC", "#fee2e2", "#ef4444", [
            "• Hotspot: > 75 °C на площі 1 мм²",
            "• Причина: мікротріщина кераміки",
            "• Струм реал: 200–600 мА",
            "• Дія: демонтаж конденсатора"
        ]),
        ("B. Самозбудження LDO", "#fef3c7", "#f59e0b", [
            "• Hotspot: 60–90 °C на всьому чіпі",
            "• Причина: невідповідний ESR MLCC",
            "• Осцилограф: ВЧ-дзвін 2 МГц",
            "• Дія: додати послідовно 0.5 Ом"
        ]),
        ("C. Переполюсовка танталу", "#fce7f3", "#ec4899", [
            "• Hotspot: > 110 °C за 1 секунду",
            "• Причина: смуга на плюсі (не мінус)",
            "• Ризик: займання діелектрика",
            "• Дія: негайне знеструмлення"
        ]),
        ("D. Нормальний MCU Idle", "#dcfce7", "#10b981", [
            "• Температура: 24–28 °C (+3 °C)",
            "• Рівномірний градієнт кристала",
            "• Струм споживання: 12–25 мА",
            "• Статус: норма, готовність до FW"
        ])
    ]

    col_w = 190
    col_gap = 16
    x_start = 23
    y0 = 60
    h_box = 210

    for i, (title, f_bg, f_border, items) in enumerate(cards):
        x = x_start + i * (col_w + col_gap)
        el.append(rect(x, y0, col_w, h_box, fill="#ffffff", stroke=f_border, sw=1.8, rx=8))
        el.append(rect(x, y0, col_w, 36, fill=f_bg, stroke=f_border, sw=1.8, rx=8))
        el.append(text(x + col_w/2, y0 + 23, title, size=11.5, bold=True, color=INK))

        for j, it in enumerate(items):
            el.append(text(x + 10, y0 + 64 + j * 35, it, size=10.5, anchor="start", color=INK))

    # Нижній аналітичний блок: Експрес-діагностика без тепловізора
    el.append(rect(23, 290, 814, 80, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    el.append(text(430, 312, "Альтернатива тепловізору: тест ізопропіловим спиртом (IPA Evaporation)", size=12.5, bold=True, color=INK))
    
    ipa_steps = [
        "1. Нанести тонкий шар IPA пензлем на знеструмлену плату.",
        "2. Подати живлення з лімітом струму 100 мА.",
        "3. Точка дефекту (КЗ / пробій) миттєво висихає за 1–2 с через локальний нагрів (суха пляма на вологому тлі)."
    ]
    for k, st in enumerate(ipa_steps):
        el.append(text(38, 335 + k * 18, st, size=10.5, anchor="start", color=MUTED))

    render(os.path.join(IMG, "thermal-profile-faults.svg"), W, H, *el)


# ── 4. Матриця тріажу дефектів та переходу до ревізії B ───────────────────────
def fig_revision_transition_matrix():
    W, H = 860, 400
    el = []
    el.append(text(W/2, 26, "Класифікація відхилень Bring-up та маршрут до серійної ревізії B", size=16, bold=True))

    # Вхідний блок: Аномалія першого пуску
    bx0, by0, bw0, bh0 = 340, 60, 180, 50
    el.append(rect(bx0, by0, bw0, bh0, fill="#fee2e2", stroke=POS, sw=1.8, rx=6))
    el.append(text(bx0 + bw0/2, by0 + 22, "Виявлено дефект", size=12, bold=True, color=INK))
    el.append(text(bx0 + bw0/2, by0 + 38, "(Bring-up Anomaly)", size=10, color=MUTED))

    # Стрілки розгалуження на 3 класи
    el.append(arrow(bx0 + bw0/2, by0 + bh0, 140, 160, color=LINE, sw=1.5))
    el.append(arrow(bx0 + bw0/2, by0 + bh0, 430, 160, color=LINE, sw=1.5))
    el.append(arrow(bx0 + bw0/2, by0 + bh0, 720, 160, color=LINE, sw=1.5))

    # 3 Категорії першопричин
    cat_w = 230
    cat_h = 100
    cat_y = 160

    # Клас 1: Дефект монтажу
    cx1 = 25
    el.append(rect(cx1, cat_y, cat_w, cat_h, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    el.append(rect(cx1, cat_y, cat_w, 28, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=6))
    el.append(text(cx1 + cat_w/2, cat_y + 19, "1. Дефект монтажу / фабрики", size=11.5, bold=True, color=INK))
    el.append(text(cx1 + 10, cat_y + 48, "• Спайка припою під QFN", size=10.5, anchor="start", color=INK))
    el.append(text(cx1 + 10, cat_y + 68, "• Зсув чіпа, непропай виводу", size=10.5, anchor="start", color=INK))
    el.append(text(cx1 + 10, cat_y + 88, "• Бракований пасивний SMD", size=10.5, anchor="start", color=INK))

    # Клас 2: Помилка схеми / трасування
    cx2 = 315
    el.append(rect(cx2, cat_y, cat_w, cat_h, fill="#f8fafc", stroke=POS, sw=1.8, rx=6))
    el.append(rect(cx2, cat_y, cat_w, 28, fill="#fef3c7", stroke=POS, sw=1.8, rx=6))
    el.append(text(cx2 + cat_w/2, cat_y + 19, "2. Помилка проектування (Design)", size=11.5, bold=True, color=INK))
    el.append(text(cx2 + 10, cat_y + 48, "• Інверсія ліній RX/TX, SDA/SCL", size=10.5, anchor="start", color=INK))
    el.append(text(cx2 + 10, cat_y + 68, "• Помилковий футпринт роз'єму", size=10.5, anchor="start", color=INK))
    el.append(text(cx2 + 10, cat_y + 88, "• Відсутність Pull-Up резистора", size=10.5, anchor="start", color=INK))

    # Клас 3: Ерата кремнію (Silicon Errata)
    cx3 = 605
    el.append(rect(cx3, cat_y, cat_w, cat_h, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    el.append(rect(cx3, cat_y, cat_w, 28, fill="#e0e7ff", stroke=LINE, sw=1.5, rx=6))
    el.append(text(cx3 + cat_w/2, cat_y + 19, "3. Апаратний баг чіпа (Errata)", size=11.5, bold=True, color=INK))
    el.append(text(cx3 + 10, cat_y + 48, "• Збій таймера в режимі DMA", size=10.5, anchor="start", color=INK))
    el.append(text(cx3 + 10, cat_y + 68, "• Зависання I2C при розтягуванні", size=10.5, anchor="start", color=INK))
    el.append(text(cx3 + 10, cat_y + 88, "• Нелінійність АЦП при 3.3 В", size=10.5, anchor="start", color=INK))

    # Стрілки дій
    el.append(arrow(cx1 + cat_w/2, cat_y + cat_h, cx1 + cat_w/2, 305, color=LINE, sw=1.5))
    el.append(arrow(cx2 + cat_w/2, cat_y + cat_h, cx2 + cat_w/2, 305, color=LINE, sw=1.8))
    el.append(arrow(cx3 + cat_w/2, cat_y + cat_h, cx3 + cat_w/2, 305, color=LINE, sw=1.5))

    # Нижні результативні блоки
    act_h = 70
    act_y = 305

    el.append(rect(cx1, act_y, cat_w, act_h, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=6))
    el.append(text(cx1 + cat_w/2, act_y + 24, "Локальний ремонт", size=11.5, bold=True, color=INK))
    el.append(mtext(cx1 + cat_w/2, act_y + 44, ["Перепайка на столі.", "CAD без змін."], size=10, color=MUTED))

    el.append(rect(cx2, act_y, cat_w, act_h, fill="#fef2f2", stroke=POS, sw=1.8, rx=6))
    el.append(text(cx2 + cat_w/2, act_y + 22, "ECO для Ревізії B + Патч", size=11.5, bold=True, color=POS))
    el.append(text(cx2 + cat_w/2, act_y + 40, "Синій дріт на Rev A.", size=10, bold=True, color=INK))
    el.append(text(cx2 + cat_w/2, act_y + 56, "Правка схеми й PCB у CAD.", size=10, color=MUTED))

    el.append(rect(cx3, act_y, cat_w, act_h, fill="#eef2ff", stroke=LINE, sw=1.5, rx=6))
    el.append(text(cx3 + cat_w/2, act_y + 24, "Firmware Workaround", size=11.5, bold=True, color=INK))
    el.append(mtext(cx3 + cat_w/2, act_y + 44, ["Програмний обхід бага.", "Запис у специфікацію."], size=10, color=MUTED))

    render(os.path.join(IMG, "revision-transition-matrix.svg"), W, H, *el)


if __name__ == "__main__":
    fig_board_id_tracking()
    fig_hardware_patch_anatomy()
    fig_thermal_profile_faults()
    fig_revision_transition_matrix()
    print("Figures generated successfully.")
