# -*- coding: utf-8 -*-
"""Фігури до теми «std::chrono»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_chrono_architecture():
    W, H = 940, 440
    f = []

    # Заголовок
    f.append(text(50, 35, "Архітектура точок часу та тривалостей у std::chrono", size=16, color=INK, anchor="start", bold=True))

    # Вісь часу (Часова вісь)
    f.append(line(70, 130, 870, 130, color=LINE, sw=2))
    # Стрілка осі часу
    f.append(arrow(860, 130, 890, 130, color=LINE, sw=2))
    f.append(text(890, 150, "Час (t)", size=12, color=MUTED, anchor="end", italic=True))

    # Точка 1: Епоха (Epoch)
    f.append(line(120, 115, 120, 145, color=POS, sw=2.5))
    f.append(text(120, 105, "Епоха (Epoch)", size=12, color=POS, anchor="middle", bold=True))
    f.append(text(120, 160, "t = 0 (1970-01-01 / boot)", size=11, color=MUTED, anchor="middle"))

    # Точка 2: TP1 (Time Point 1)
    f.append(line(360, 115, 360, 145, color=FIELD, sw=2.5))
    f.append(text(360, 105, "time_point t1", size=12, color=FIELD, anchor="middle", bold=True))

    # Точка 3: TP2 (Time Point 2)
    f.append(line(720, 115, 720, 145, color=NEG, sw=2.5))
    f.append(text(720, 105, "time_point t2", size=12, color=NEG, anchor="middle", bold=True))

    # Тривалість 1: Епоха -> t1 (Duration d1)
    f.append(line(120, 185, 360, 185, color=FIELD, sw=1.8, dash="4 4"))
    f.append(arrow(120, 185, 360, 185, color=FIELD, sw=1.8))
    f.append(text(240, 178, "d1 = t1 - Epoch", size=11, color=FIELD, anchor="middle", bold=True))

    # Тривалість ∆t: t1 -> t2 (Duration d2 = t2 - t1)
    f.append(line(360, 185, 720, 185, color=NEG, sw=2))
    f.append(arrow(360, 185, 720, 185, color=NEG, sw=2))
    f.append(text(540, 178, "∆t = t2 - t1 (duration: count × ratio)", size=12, color=NEG, anchor="middle", bold=True))

    # Нижній блок 1: duration<Rep, Period>
    f.append(fitbox(50, 225, 400, 180,
                    "std::chrono::duration<Rep, Period>\n"
                    "• Rep: тип лічильника (int64_t, double)\n"
                    "• Period: std::ratio<Num, Denom> (секунди, мс, нс)\n"
                    "• Збереження: типізований скаляр без оверхеду\n"
                    "• Арифметика: перевірка одиниць під час компіляції",
                    size=12, fill="#e8f6ee", stroke=FIELD))

    # Нижній блок 2: time_point<Clock, Duration>
    f.append(fitbox(490, 225, 400, 180,
                    "std::chrono::time_point<Clock, Duration>\n"
                    "• Clock: зв'язує точку з фізичним годинником\n"
                    "• Duration: тривалість від епохи годинника\n"
                    "• Афінний простір: Point - Point = Duration\n"
                    "• Зміщення: Point + Duration = Point",
                    size=12, fill="#eef2f7", stroke=LINE))

    render(os.path.join(OUT, 'chrono-architecture.svg'), W, H, *f,
           title="Архітектура точок часу та тривалостей у std::chrono")


def fig_chrono_clocks_map():
    W, H = 940, 460
    f = []

    f.append(text(50, 35, "Ієрархія та класифікація годинників у C++11 / C++20", size=16, color=INK, anchor="start", bold=True))

    # Блок 1: steady_clock
    f.append(fitbox(50, 70, 410, 160,
                    "std::chrono::steady_clock (Монотонний годинник)\n"
                    "• Гарантія: час лише зростає, без стрибків назад\n"
                    "• Застосування: вимірювання інтервалів, таймаути\n"
                    "• Не залежить від системного часу чи NTP\n"
                    "• Епоха: момент завантаження ОС / старт CPU",
                    size=12, fill="#e8f6ee", stroke=FIELD))

    # Блок 2: system_clock
    f.append(fitbox(480, 70, 410, 160,
                    "std::chrono::system_clock (Астрономічний час)\n"
                    "• Прив'язка до реального календарного часу (UTC)\n"
                    "• Піддається коригуванню NTP та ручному зсуву\n"
                    "• Може стрибати назад чи вперед (немонотонний!)\n"
                    "• Епоха: UNIX Epoch (1970-01-01 00:00:00 UTC)",
                    size=12, fill="#fff7e6", stroke=POS))

    # Блок 3: high_resolution_clock
    f.append(fitbox(50, 255, 410, 165,
                    "std::chrono::high_resolution_clock\n"
                    "• Найменший період тику на даній платформі\n"
                    "• Псевдонім (alias) до steady_clock або system_clock\n"
                    "• Увага: портуваність залежить від реалізації компілятора\n"
                    "• Рекомендація: для бенчмарків явно вживати steady_clock",
                    size=12, fill="#f4f6f8", stroke=LINE))

    # Блок 4: C++20 Спеціалізовані годинники
    f.append(fitbox(480, 255, 410, 165,
                    "Спеціалізовані годинники C++20\n"
                    "• utc_clock: UTC з урахуванням високосних секунд\n"
                    "• tai_clock: Міжнародний атомний час (без високосних с)\n"
                    "• gps_clock: Супутниковий час GPS (зсув 19с від TAI)\n"
                    "• file_clock: Точки часу файлової системи (filesystem)",
                    size=12, fill="#eef2f7", stroke=LINE))

    render(os.path.join(OUT, 'chrono-clocks-map.svg'), W, H, *f,
           title="Класифікація та призначення годинників у std::chrono")


if __name__ == '__main__':
    fig_chrono_architecture()
    fig_chrono_clocks_map()
    print("Фігури успішно згенеровано.")
