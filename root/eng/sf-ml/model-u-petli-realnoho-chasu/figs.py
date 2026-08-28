# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_dual_rate_timing():
    W, H = 880, 430
    p = []

    # Тло та заголовна плашка
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    p.append(rect(15, 12, W - 30, 44, fill=FILL, stroke="#c9d2dc", sw=1.2, rx=6))
    p.append(text(W / 2, 39, "Часова діаграма розділення контурів: 500 Гц керування та асинхронний ML-інференс",
                  size=14, color=INK, bold=True))

    # Секція 1: Швидкий контур керування (500 Гц, період T_ctrl = 2 мс)
    y_ctrl = 95
    p.append(rect(25, y_ctrl - 15, 170, 26, fill="#e8f4fc", stroke=NEG, sw=1.2, rx=4))
    p.append(text(110, y_ctrl + 2, "Швидкий контур (500 Гц)", size=11, color=NEG, bold=True))

    # Часова вісь швидкого контуру
    p.append(line(210, y_ctrl, 840, y_ctrl, color="#7f8c8d", sw=1.5))
    p.append(arrow(830, y_ctrl, 850, y_ctrl, color="#7f8c8d", sw=1.5))
    p.append(text(855, y_ctrl + 4, "t", size=11, color=MUTED, italic=True))

    # Імпульси тактів 500 Гц
    for i in range(25):
        x = 220 + i * 25
        p.append(line(x, y_ctrl - 9, x, y_ctrl + 9, color=NEG, sw=1.8))
        if i % 5 == 0:
            p.append(text(x, y_ctrl + 20, "%d мс" % (i * 2), size=10, color=MUTED))

    # Секція 2: Повільний ML-інференс (20 Гц, номінальний дедлайн T_ml = 50 мс)
    y_ml = 185
    p.append(rect(25, y_ml - 15, 170, 26, fill="#fef5e7", stroke="#d35400", sw=1.2, rx=4))
    p.append(text(110, y_ml + 2, "ML-інференс (20 Гц)", size=11, color="#d35400", bold=True))

    p.append(line(210, y_ml, 840, y_ml, color="#7f8c8d", sw=1.5))
    p.append(arrow(830, y_ml, 850, y_ml, color="#7f8c8d", sw=1.5))
    p.append(text(855, y_ml + 4, "t", size=11, color=MUTED, italic=True))

    # Кадр 1: Нормальне виконання (32 мс, встиг у дедлайн 50 мс)
    p.append(rect(220, y_ml - 20, 160, 40, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=5))
    p.append(text(300, y_ml - 4, "Кадр 1: Інференс (32 мс)", size=10, color=FIELD, bold=True))
    p.append(text(300, y_ml + 12, "Вивід готовий вчасно", size=9.5, color=MUTED))

    # Дедлайн кадру 1 (50 мс -> x = 470)
    p.append(line(470, y_ml - 25, 470, y_ml + 25, color=POS, sw=1.5, dash="3,3"))
    p.append(text(470, y_ml - 30, "Дедлайн 1 (50 мс)", size=9.5, color=POS))

    # Кадр 2: Пропуск дедлайну (Джиттер/Контеншн, триває 68 мс)
    p.append(rect(470, y_ml - 20, 240, 40, fill="#fdedec", stroke=POS, sw=1.5, rx=5))
    p.append(text(590, y_ml - 4, "Кадр 2: Затримка / Джиттер (68 мс)", size=10, color=POS, bold=True))
    p.append(text(590, y_ml + 12, "ПРОПУСК ДЕДЛАЙНУ (LATE ARRIVAL)", size=9.5, color=POS))

    # Дедлайн кадру 2 (100 мс -> x = 720)
    p.append(line(720, y_ml - 25, 720, y_ml + 25, color=POS, sw=1.5, dash="3,3"))
    p.append(text(720, y_ml - 30, "Дедлайн 2 (100 мс)", size=9.5, color=POS))

    # Кадр 3: Відновлення
    p.append(rect(720, y_ml - 20, 110, 40, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=5))
    p.append(text(775, y_ml + 4, "Кадр 3", size=10, color=FIELD, bold=True))

    # Секція 3: Режим роботи контуру стабілізації (Джерело поправок)
    y_sig = 295
    p.append(rect(25, y_sig - 15, 170, 26, fill="#f4f6f8", stroke=INK, sw=1.2, rx=4))
    p.append(text(110, y_sig + 2, "Джерело поправок", size=11, color=INK, bold=True))

    p.append(line(210, y_sig, 840, y_sig, color="#7f8c8d", sw=1.5))
    p.append(arrow(830, y_sig, 850, y_sig, color="#7f8c8d", sw=1.5))

    # Фаза 1: Свіжі дані ML (до 50 мс)
    p.append(rect(220, y_sig - 18, 250, 36, fill="#d4efdf", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(345, y_sig + 4, "Свіжий вивід ML (Кадр 1)", size=10, color=FIELD, bold=True))

    # Фаза 2: Екстраполяція (ZOH / Кінематика, 50..80 мс)
    p.append(rect(470, y_sig - 18, 140, 36, fill="#fef9e7", stroke="#f39c12", sw=1.4, rx=4))
    p.append(text(540, y_sig - 3, "Екстраполяція ZOH", size=10, color="#b7950b", bold=True))
    p.append(text(540, y_sig + 11, "Згасання довіри", size=9.5, color=MUTED))

    # Фаза 3: Перехід на Fallback PID (80..100 мс)
    p.append(rect(610, y_sig - 18, 110, 36, fill="#fadbd8", stroke=POS, sw=1.4, rx=4))
    p.append(text(665, y_sig - 3, "Fallback PID", size=10, color=POS, bold=True))
    p.append(text(665, y_sig + 11, "Bumpless Transfer", size=9.5, color=POS))

    # Фаза 4: Відновлення ML (після 100 мс)
    p.append(rect(720, y_sig - 18, 110, 36, fill="#d4efdf", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(775, y_sig + 4, "Свіжий ML (Кадр 3)", size=10, color=FIELD, bold=True))

    # Пояснювальна плашка внизу
    p.append(rect(25, 360, W - 50, 52, fill=FILL, stroke="#c9d2dc", sw=1.2, rx=6))
    p.append(mtext(W / 2, 377,
                   "Швидкий контур (500 Гц) не зупиняється на очікування інференсу (20 Гц). При пропуску дедлайну контур\n"
                   "послідовно застосовує екстраполяцію попереднього виходу, а при перевищенні ліміту часу — переходить на бекап-регулятор.",
                   size=10.5, color=INK, anchor="middle", lh=1.35))

    render(os.path.join(OUT, "dual-rate-timing.svg"), W, H, *p,
           title="Часова діаграма розділення контурів керування")


def fig_deadline_miss_fallback():
    W, H = 880, 480
    p = []

    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    p.append(rect(15, 12, W - 30, 44, fill=FILL, stroke="#c9d2dc", sw=1.2, rx=6))
    p.append(text(W / 2, 39, "Архітектура обробки пропуску дедлайну та автомат аварійного перемикання",
                  size=14, color=INK, bold=True))

    # Блок 1: Вхідні сенсори (ліворуч)
    p.append(rect(25, 80, 140, 80, fill="#ebf5fb", stroke=NEG, sw=1.5, rx=6))
    p.append(text(95, 105, "Потік давачів", size=11, color=NEG, bold=True))
    p.append(text(95, 123, "IMU (1000 Гц)", size=10, color=INK))
    p.append(text(95, 140, "Камера (30 к/с)", size=10, color=INK))

    # Стрілка від сенсорів до швидкого контуру та ML
    p.append(arrow(165, 105, 230, 105, color=NEG, sw=1.5))
    p.append(text(197, 95, "Direct", size=9.5, color=NEG))

    p.append(arrow(165, 135, 230, 230, color="#d35400", sw=1.5))
    p.append(text(190, 190, "DMA", size=9.5, color="#d35400"))

    # Блок 2: Lock-free Triple Buffer
    p.append(rect(230, 195, 160, 75, fill="#fef5e7", stroke="#d35400", sw=1.5, rx=6))
    p.append(text(310, 218, "Triple Buffer", size=11, color="#d35400", bold=True))
    p.append(text(310, 236, "Lock-free обмін", size=10, color=INK))
    p.append(text(310, 253, "Atomic exchange", size=9.5, color=MUTED))

    # Блок 3: ML Inference з Watchdog
    p.append(rect(230, 290, 160, 65, fill="#fef5e7", stroke="#d35400", sw=1.5, rx=6))
    p.append(text(310, 312, "ML Inference", size=11, color="#d35400", bold=True))
    p.append(text(310, 330, "Watchdog Timer", size=10, color=POS))
    p.append(arrow(310, 290, 310, 270, color="#d35400", sw=1.4))

    # Блок 4: Диспетчер стану та оцінки дедлайну
    p.append(rect(430, 80, 180, 190, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=6))
    p.append(text(520, 103, "Диспетчер дедлайнів", size=11, color=INK, bold=True))
    p.append(line(440, 113, 600, 113, color="#c9d2dc", sw=1.0))

    p.append(rect(442, 123, 156, 30, fill="#d4efdf", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(520, 142, "1. Свіжий вивід ML", size=10, color=FIELD, bold=True))

    p.append(rect(442, 160, 156, 30, fill="#fcf3cf", stroke="#f39c12", sw=1.2, rx=4))
    p.append(text(520, 179, "2. Екстраполяція ZOH / EKF", size=9.5, color="#b7950b", bold=True))

    p.append(rect(442, 197, 156, 30, fill="#fadbd8", stroke=POS, sw=1.2, rx=4))
    p.append(text(520, 216, "3. Fallback PID / LQR", size=10, color=POS, bold=True))

    p.append(rect(442, 234, 156, 30, fill="#ebedef", stroke="#7f8c8d", sw=1.2, rx=4))
    p.append(text(520, 253, "4. Безпечна зупинка", size=10, color=INK, bold=True))

    # Зв'язок буфера з диспетчером
    p.append(arrow(390, 220, 430, 220, color=INK, sw=1.5))

    # Зв'язок датчиків напряму до швидкого оцінювача (EKF / PID)
    p.append(rect(230, 80, 160, 50, fill="#ebf5fb", stroke=NEG, sw=1.5, rx=6))
    p.append(text(310, 101, "Швидкий EKF стан", size=11, color=NEG, bold=True))
    p.append(text(310, 118, "500 Гц прогностик", size=9.5, color=MUTED))
    p.append(arrow(390, 105, 430, 105, color=NEG, sw=1.5))

    # Блок 5: Bumpless Transfer та Бар'єри Безпеки (Safety Envelope)
    p.append(rect(650, 110, 200, 130, fill="#e8f8f5", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(750, 134, "Контур безпеки (CBF)", size=11, color=FIELD, bold=True))
    p.append(text(750, 153, "Bumpless Transfer", size=10, color=INK))
    p.append(text(750, 171, "Захисні інваріанти", size=10, color=INK))
    p.append(text(750, 190, "Обмеження струму/кутів", size=9.5, color=MUTED))
    p.append(text(750, 218, "Вихід на мотори (PWM)", size=10.5, color=NEG, bold=True))

    # Стрілка від диспетчера до контуру безпеки
    p.append(arrow(610, 175, 650, 175, color=INK, sw=1.8))

    # Нижня інформаційна панель
    p.append(rect(25, 385, W - 50, 75, fill=FILL, stroke="#c9d2dc", sw=1.2, rx=6))
    p.append(mtext(W / 2, 403,
                   "Ієрархія захисту: При настанні дедлайну система не зависає, а автоматично деградує якість оцінки:\n"
                   "від екстраполяції кінематики до детермінованого ПІД-регулятора. Механізм Bumpless Transfer узгоджує\n"
                   "інтегратор регулятора, запобігаючи механічним ударам та стрибкам струму приводів.",
                   size=10.5, color=INK, anchor="middle", lh=1.35))

    render(os.path.join(OUT, "deadline-miss-fallback.svg"), W, H, *p,
           title="Архітектура обробки пропуску дедлайну та fallback-контролер")


if __name__ == "__main__":
    fig_dual_rate_timing()
    fig_deadline_miss_fallback()
    print("All figures regenerated successfully.")
