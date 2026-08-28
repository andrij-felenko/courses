# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Ієрархічна блок-карта розміщення компонентів на платі ────────────────
def fig_hierarchical_floorplan():
    W, H = 820, 520
    f = []

    # Заголовок фігури
    f.append(text(W / 2, 28, "Ієрархія пріоритетів просторового компонування компонентів плати", size=16, bold=True))

    # Контур друкованої плати (PCB Outline)
    px, py, pw, ph = 40, 60, 740, 430
    f.append(rect(px, py, pw, ph, fill="#fafbfc", stroke="#4b5563", sw=2.2, rx=8))
    f.append(text(px + 16, py - 8, "Межа друкованої плати (PCB Outline / 4-шаровий стек)", size=12, color=MUTED, anchor="start", bold=True))

    # Кріпильні отвори (Рівень 1 - Механіка)
    holes = [(px + 20, py + 20), (px + pw - 20, py + 20), (px + 20, py + ph - 20), (px + pw - 20, py + ph - 20)]
    for hx, hy in holes:
        f.append(circle(hx, hy, 10, fill="#ffffff", stroke="#9ca3af", sw=1.8))
        f.append(circle(hx, hy, 5, fill="#9ca3af", stroke="none"))
    f.append(text(px + 38, py + 24, "Отвори кріплення (М3)", size=10.5, color=MUTED, anchor="start"))

    # 1. Фіксовані механічні елементи (Верхній та лівий край)
    # Роз'єм живлення (DC Jack / USB-C)
    f.append(rect(px + 70, py - 4, 60, 20, fill="#e2e8f0", stroke="#334155", sw=1.6, rx=3))
    f.append(text(px + 100, py + 30, "USB-C / Живлення", size=11, color="#1e293b", bold=True))
    f.append(text(px + 100, py + 44, "Пріоритет 1: Механіка", size=9.5, color=MUTED))

    # Роз'єми зв'язку (Ethernet / UART / CAN)
    f.append(rect(px + 450, py - 4, 80, 20, fill="#e2e8f0", stroke="#334155", sw=1.6, rx=3))
    f.append(text(px + 490, py + 30, "Роз'єм Ethernet / CAN", size=11, color="#1e293b", bold=True))
    f.append(text(px + 490, py + 44, "Фіксований край", size=9.5, color=MUTED))

    # Кнопки та світлодіоди на правому краї
    f.append(rect(px + pw - 16, py + 120, 20, 40, fill="#fed7aa", stroke="#ea580c", sw=1.6, rx=3))
    f.append(text(px + pw - 80, py + 136, "Кнопка Reset / User", size=11, color="#c2410c", bold=True, anchor="end"))
    f.append(text(px + pw - 80, py + 150, "Пріоритет 1 (HMI)", size=9.5, color=MUTED, anchor="end"))

    # 3. Силовий вузол (Power Delivery) - Верхній лівий кут
    pwx, pwy, pww, pwh = px + 40, py + 66, 210, 160
    f.append(rect(pwx, pwy, pww, pwh, fill="#fef2f2", stroke=POS, sw=1.6, rx=6))
    f.append(text(pwx + pww / 2, pwy + 20, "Силовий вузол (Пріоритет 3)", size=13, color=POS, bold=True))
    
    # Всередині силового вузла: Hot Loop Buck, LDO, Фільтр
    f.append(rect(pwx + 14, pwy + 34, 80, 50, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    f.append(text(pwx + 54, pwy + 55, "Buck DC-DC", size=11, color=POS, bold=True))
    f.append(text(pwx + 54, pwy + 70, "Hot-loop L1", size=9.5, color=POS))

    f.append(rect(pwx + 110, pwy + 34, 85, 50, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    f.append(text(pwx + 152, pwy + 55, "Фільтр LC + TVS", size=10.5, color=POS, bold=True))
    f.append(text(pwx + 152, pwy + 70, "Захист входу", size=9.5, color=MUTED))

    f.append(rect(pwx + 14, pwy + 96, 181, 48, fill="#ffffff", stroke="#f87171", sw=1.2, rx=4))
    f.append(text(pwx + 104, pwy + 116, "Лінійний регулятор LDO 3.3V", size=11, color=POS, bold=True))
    f.append(text(pwx + 104, pwy + 132, "Чисте живлення аналогу та ядра", size=9.5, color=MUTED))

    # 2. Головний обчислювальний центр (MCU / SoC) - Центр плати
    mcux, mcuy, mcuw, mcuh = px + 280, py + 120, 200, 180
    f.append(rect(mcux, mcuy, mcuw, mcuh, fill="#eff6ff", stroke=NEG, sw=2, rx=6))
    f.append(text(mcux + mcuw / 2, mcuy + 24, "Головний SoC / MCU", size=14, color=NEG, bold=True))
    f.append(text(mcux + mcuw / 2, mcuy + 40, "Пріоритет 2: Ядро топології", size=10, color=NEG))

    # Кварцовий резонатор (упритул до MCU)
    f.append(rect(mcux + 20, mcuy + 56, 65, 34, fill="#ffffff", stroke=NEG, sw=1.2, rx=3))
    f.append(text(mcux + 52, mcuy + 72, "Кварц 25 МГц", size=10, color=NEG, bold=True))
    f.append(text(mcux + 52, mcuy + 84, "Впритул", size=9, color=MUTED))

    # Блокувальні конденсатори Decoupling (Пріоритет 6) по кутах MCU
    caps = [(mcux - 16, mcuy + 20), (mcux - 16, mcuy + mcuh - 30), 
            (mcux + mcuw + 4, mcuy + 20), (mcux + mcuw + 4, mcuy + mcuh - 30)]
    for cx, cy in caps:
        f.append(rect(cx, cy, 12, 18, fill="#dbeafe", stroke=NEG, sw=1.2, rx=2))
    f.append(text(mcux + mcuw / 2, mcuy + 125, "Коридори Fanout / Escape", size=11, color=NEG, bold=True))
    f.append(text(mcux + mcuw / 2, mcuy + 145, "Decoupling MLCC (Пріоритет 6)", size=10, color=FIELD, bold=True))
    f.append(text(mcux + mcuw / 2, mcuy + 160, "безпосередньо біля виводів", size=9.5, color=MUTED))

    # 5. Високошвидкісні шини та пам'ять (High-Speed Memory) - Праворуч від MCU
    memx, memy, memw, memh = px + 510, py + 120, 180, 130
    f.append(rect(memx, memy, memw, memh, fill="#fdf4ff", stroke="#a855f7", sw=1.6, rx=6))
    f.append(text(memx + memw / 2, memy + 24, "Пам'ять QSPI / DDR", size=13, color="#7e22ce", bold=True))
    f.append(text(memx + memw / 2, memy + 40, "Пріоритет 5: Швидкісні шини", size=10, color="#7e22ce"))
    f.append(rect(memx + 20, memy + 54, 140, 58, fill="#ffffff", stroke="#c084fc", sw=1.2, rx=4))
    f.append(text(memx + 90, memy + 76, "Короткі шини зв'язку", size=10.5, color="#7e22ce", bold=True))
    f.append(text(memx + 90, memy + 94, "Імпеданс 50 Ом / узгодження", size=9.5, color=MUTED))

    # 4. Чутливий аналоговий острів (Аналоговий тракт) - Нижній лівий кут
    anax, anay, anaw, anah = px + 40, py + 260, 240, 150
    f.append(rect(anax, anay, anaw, anah, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    f.append(text(anax + anaw / 2, anay + 22, "Чутливий аналоговий вузол", size=13, color=FIELD, bold=True))
    f.append(text(anax + anaw / 2, anay + 38, "Пріоритет 4: АЦП / Датчики / VREF", size=10, color=FIELD))

    # Всередині аналогового острова
    f.append(rect(anax + 14, anay + 50, 100, 44, fill="#ffffff", stroke=FIELD, sw=1.2, rx=3))
    f.append(text(anax + 64, anay + 68, "24-біт АЦП", size=11, color=FIELD, bold=True))
    f.append(text(anax + 64, anay + 82, "Чиста зона", size=9.5, color=MUTED))

    f.append(rect(anax + 124, anay + 50, 100, 44, fill="#ffffff", stroke=FIELD, sw=1.2, rx=3))
    f.append(text(anax + 174, anay + 68, "Опора VREF", size=11, color=FIELD, bold=True))
    f.append(text(anax + 174, anay + 82, "Термостабільна", size=9.5, color=MUTED))

    f.append(rect(anax + 14, anay + 100, 210, 38, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=3))
    f.append(text(anax + 119, anay + 116, "Ізольована земля / Екран Guard Ring", size=10.5, color=FIELD, bold=True))
    f.append(text(anax + 119, anay + 130, "Віддалено від імпульсного вузла", size=9.5, color=MUTED))

    # Зв'язки стрілками між вузлами
    # Живлення -> MCU
    f.append(arrow(pwx + pww, pwy + 110, mcux, mcuy + 40, color=POS, sw=2))
    f.append(text((pwx + pww + mcux) / 2 - 10, pwy + 82, "VDD 3.3V", size=10.5, color=POS, bold=True))

    # MCU -> Пам'ять
    f.append(arrow(mcux + mcuw, mcuy + 70, memx, memy + 70, color="#7e22ce", sw=2))
    f.append(text((mcux + mcuw + memx) / 2, mcuy + 60, "High-Speed Bus", size=10, color="#7e22ce", bold=True))

    # Аналог -> MCU (SPI/I2C)
    f.append(arrow(anax + anaw, anay + 70, mcux + 40, mcuy + mcuh, color=FIELD, sw=2))
    f.append(text(anax + anaw + 30, anay + 45, "SPI / Ізольована шина", size=10.5, color=FIELD, bold=True))

    # Пояснювальний підпис унизу
    f.append(text(W / 2, H - 12, "Принцип: Зменшення ступенів вільності — від фіксованої механіки до пасивної розв'язки", size=12, color=MUTED, bold=True))

    return render(os.path.join(IMG, "hierarchical-floorplan.svg"), W, H, *f)


# ── 2. Оптимізація потоку сигналів і просторове теплорозмежування ────────────
def fig_signal_thermal_flow():
    W, H = 820, 480
    f = []

    f.append(text(W / 2, 26, "Оптимізація потоку сигналів та захист термочутливих вузлів", size=16, bold=True))

    # Ліва половина: Спрямований потік сигналів (Signal Flow)
    bx1, by1, bw1, bh1 = 35, 54, 365, 380
    f.append(rect(bx1, by1, bw1, bh1, fill="#f8fafc", stroke="#0284c7", sw=1.8, rx=8))
    f.append(text(bx1 + bw1 / 2, by1 + 24, "А. Односпрямований потік сигналів", size=14, color="#0369a1", bold=True))
    f.append(text(bx1 + bw1 / 2, by1 + 40, "Усунення зворотних петель і перетинів", size=10.5, color=MUTED))

    # Етапи потоку згори донизу
    stages = [
        ("1. Вхідний роз'єм та захист", "Роз'єм живлення / EMI-фільтр / ESD", "#f1f5f9", "#475569"),
        ("2. Первинне перетворення", "Buck DC-DC регулятор / LDO", "#fee2e2", POS),
        ("3. Обробка сигналів", "Центральний MCU / DSP / Фільтри", "#eff6ff", NEG),
        ("4. Вихідний каскад та інтерфейси", "Драйвери / Буфери / Вихідні клеми", "#ecfdf5", FIELD)
    ]

    sy = by1 + 56
    for i, (stitle, ssub, sfill, scolor) in enumerate(stages):
        f.append(rect(bx1 + 25, sy, bw1 - 50, 52, fill=sfill, stroke=scolor, sw=1.4, rx=6))
        f.append(text(bx1 + bw1 / 2, sy + 22, stitle, size=12, color=scolor, bold=True))
        f.append(text(bx1 + bw1 / 2, sy + 38, ssub, size=10, color=MUTED))
        if i < len(stages) - 1:
            f.append(arrow(bx1 + bw1 / 2, sy + 52, bx1 + bw1 / 2, sy + 72, color="#0284c7", sw=2))
        sy += 74

    f.append(text(bx1 + bw1 / 2, by1 + bh1 - 14, "Чітка лінія: Вхід → Обробка → Вихід", size=11, color="#0369a1", bold=True))

    # Права половина: Теплове розмежування (Thermal Management)
    bx2, by2, bw2, bh2 = 420, 54, 365, 380
    f.append(rect(bx2, by2, bw2, bh2, fill="#fffbeb", stroke="#d97706", sw=1.8, rx=8))
    f.append(text(bx2 + bw2 / 2, by2 + 24, "Б. Просторове теплове зонування", size=14, color="#b45309", bold=True))
    f.append(text(bx2 + bw2 / 2, by2 + 40, "Ізоляція джерел тепла від чутливих сенсорів", size=10.5, color=MUTED))

    # Гаряча зона зверху (Power MOSFET / LDO)
    f.append(rect(bx2 + 25, by2 + 60, bw2 - 50, 80, fill="#fee2e2", stroke=POS, sw=1.6, rx=6))
    f.append(text(bx2 + bw2 / 2, by2 + 82, "Гаряча зона: Потужний LDO + FET", size=12.5, color=POS, bold=True))
    f.append(text(bx2 + bw2 / 2, by2 + 100, "Розсіювання тепла: 2.5 Вт (Т = 65°C)", size=10.5, color=POS))
    f.append(text(bx2 + bw2 / 2, by2 + 120, "Масив теплових отворів (Thermal Vias)", size=10, color=MUTED))

    # Тепловий бар'єр (Тепловий градієнт)
    gy = by2 + 155
    f.append(line(bx2 + 30, gy, bx2 + bw2 - 30, gy, color="#d97706", sw=2, dash="5 4"))
    f.append(text(bx2 + bw2 / 2, gy + 18, "Тепловий градієнт: ΔT / Δx = 2.8 °C/мм у текстоліті", size=10.5, color="#b45309", bold=True))
    f.append(text(bx2 + bw2 / 2, gy + 32, "Фізична відстань > 25 мм або проріз у платі", size=10, color=MUTED))

    # Холодна чутлива зона знизу (IMU, Precision ADC, TCXO)
    f.append(rect(bx2 + 25, by2 + 210, bw2 - 50, 110, fill="#eff6ff", stroke=NEG, sw=1.6, rx=6))
    f.append(text(bx2 + bw2 / 2, by2 + 234, "Холодна зона: Прецизійні давачі", size=12.5, color=NEG, bold=True))
    f.append(text(bx2 + bw2 / 2, by2 + 254, "IMU Гіроскоп / 24-біт АЦП / TCXO", size=11, color=NEG, bold=True))
    f.append(text(bx2 + bw2 / 2, by2 + 274, "Стабільна температура (T = 28°C ± 1°C)", size=10, color=FIELD, bold=True))
    f.append(text(bx2 + bw2 / 2, by2 + 296, "Захист від теплового дрейфу нуля й напружень", size=9.5, color=MUTED))

    f.append(text(bx2 + bw2 / 2, by2 + bh2 - 14, "Результат: Нульовий тепловий шум і стабільний дрейф", size=11, color="#b45309", bold=True))

    # Нижній загальний підпис
    f.append(text(W / 2, H - 12, "Дотримання топологічного потоку зменшує довжину ліній, а зонування усуває взаємний вплив", size=12, color=MUTED, bold=True))

    return render(os.path.join(IMG, "signal-thermal-flow.svg"), W, H, *f)


if __name__ == "__main__":
    fig_hierarchical_floorplan()
    fig_signal_thermal_flow()
    print("ok: 2 figures generated")
