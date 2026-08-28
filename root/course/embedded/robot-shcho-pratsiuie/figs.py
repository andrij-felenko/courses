# -*- coding: utf-8 -*-
"""Генератор фігур для теми robot-shcho-pratsiuie."""
import sys
import os

# scripts/ у корені репо — 4 рівні вгору від root/course/embedded/robot-shcho-pratsiuie
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_delivery_vs_interaction():
    """Фігура 1: Порівняння дрона-візника та робота силової взаємодії."""
    w, h = 820, 480
    frags = []

    # Заголовки двох колонок
    frags.append(fitbox(30, 20, 360, 44, "ДРОН-ВІЗНИК (ПАСИВНИЙ ТРАНСПОРТ)\nВільний простір, відкритий ланцюг",
                        fill="#edf2f7", stroke="#4a5568", bold=True, size=13))
    frags.append(fitbox(430, 20, 360, 44, "РОБОТ-РОБІТНИК (СИЛОВА ВЗАЄМОДІЯ)\nКонтакт із середовищем, замкнений ланцюг",
                        fill="#fef3c7", stroke="#d97706", bold=True, size=13))

    # Ліва колонка: Дрон-візник
    frags.append(rect(30, 75, 360, 385, fill="#f8fafc", stroke="#cbd5e1", sw=1.2))

    frags.append(fitbox(45, 90, 330, 58,
                        "Вантаж = пасивна маса m_p\nЗсуває центр мас (ЦМ) і тензор інерції I\nЖодних зовнішніх кінематичних в'язей",
                        fill="#ffffff", stroke="#94a3b8", size=12))

    frags.append(fitbox(45, 160, 330, 68,
                        "Контур керування: Позиційний ПІД (SE(3))\nПомилка: e(t) = x_d(t) - x(t)\nЦіль: звести e(t) до 0 будь-якою тягою",
                        fill="#ffffff", stroke="#94a3b8", size=12))

    frags.append(fitbox(45, 240, 330, 60,
                        "Зовнішня сила = невідоме збурення F_dist\nВітер чи інерція вантажу придушуються\nінтегральною ланкою регулятора",
                        fill="#ffffff", stroke="#94a3b8", size=12))

    frags.append(fitbox(45, 312, 330, 70,
                        "Наслідок аварійного контакту зі стіною:\nПозиційний ПІД нарощує інтегратор,\nмотори виходять на 100% тяги -> удар/зрив",
                        fill="#fee2e2", stroke=POS, size=12, color="#991b1b"))

    frags.append(fitbox(45, 394, 330, 52,
                        "Сенсорний фокус: Глобальна навігація\nGNSS, барометр, оглядовий лідар (SLAM)",
                        fill="#ffffff", stroke="#94a3b8", size=11))

    # Права колонка: Робот-робітник
    frags.append(rect(430, 75, 360, 385, fill="#fffbeb", stroke="#fde68a", sw=1.2))

    frags.append(fitbox(445, 90, 330, 58,
                        "Довкілля = пружна або жорстка опора\nЗамикання кінематичного ланцюга\nСила реакції зв'язку: F_ext = K_env · delta_x",
                        fill="#ffffff", stroke="#f59e0b", size=12))

    frags.append(fitbox(445, 160, 330, 68,
                        "Контур: Гібридний / Імпедансний\nM_d · e'' + D_d · e' + K_d · e = -F_ext\nЦіль: баланс між положенням і силою",
                        fill="#ffffff", stroke="#f59e0b", size=12))

    frags.append(fitbox(445, 240, 330, 60,
                        "Зовнішня сила = цільова керована змінна\nСила притискання інструмента до поверхні\nзадається і вимірюється в реальному часі",
                        fill="#ffffff", stroke="#f59e0b", size=12))

    frags.append(fitbox(445, 312, 330, 70,
                        "Реакція на контакт зі стіною:\nІмпеданс віддає інструмент назад (Compliance),\nтяга скидається, сила стабілізується на нормі",
                        fill="#dcfce7", stroke=FIELD, size=12, color="#166534"))

    frags.append(fitbox(445, 394, 330, 52,
                        "Сенсорний фокус: Локальний контакт\n6-DOF F/T сенсор на зап'ястку, RGB-D нормалі",
                        fill="#ffffff", stroke="#f59e0b", size=11))

    render(os.path.join(OUT_DIR, "delivery-vs-interaction.svg"), w, h, *frags)


def fig_whole_body_control_layers():
    """Фігура 2: Архітектура часових доменів та контурів керування мобільного маніпулятора."""
    w, h = 820, 500
    frags = []

    # Заголовок зверху
    frags.append(fitbox(40, 15, 740, 36, "ІЄРАРХІЯ ЧАСОВИХ ДОМЕНІВ ТА КОНТУРІВ КЕРУВАННЯ РОБОТА-РОБІТНИКА",
                        fill="#f1f5f9", stroke="#64748b", bold=True, size=13))

    # Рівень 1: Сприйняття та цілепокладання (10-30 Гц)
    frags.append(rect(40, 62, 740, 100, fill="#f0fdf4", stroke="#86efac", sw=1.5))
    frags.append(text(60, 84, "РІВЕНЬ 1: СПРИЙНЯТТЯ ТА СЕМАНТИКА (10–30 Гц, Асинхронний / Soft RT)", size=12, bold=True, color="#15803d", anchor="start"))

    frags.append(fitbox(60, 94, 215, 56, "RGB-D камери та лідари\nХмара точок робочої зони\nТочність: міліметри (ToF / Stereo)", fill="#ffffff", stroke="#bbf7d0", size=11))
    frags.append(fitbox(295, 94, 230, 56, "Оцінка геометрії взаємодії\nДетекція поверхні, нормалі n,\nосі обертання вентиля чи ручки", fill="#ffffff", stroke="#bbf7d0", size=11))
    frags.append(fitbox(545, 94, 215, 56, "Генератор цільового завдання\nТраєкторія x_d(t) та вектор\nцільового зусилля F_d(t)", fill="#ffffff", stroke="#bbf7d0", size=11))

    # Стрілка вниз від рівня 1 до рівня 2
    frags.append(arrow(410, 163, 410, 185, color="#059669", sw=2))
    frags.append(text(420, 177, "x_d, F_d, n", size=11, color="#059669", anchor="start", bold=True))

    # Рівень 2: Координація всієї системи (Whole-Body Coordination, 50-100 Гц)
    frags.append(rect(40, 188, 740, 120, fill="#eff6ff", stroke="#93c5fd", sw=1.5))
    frags.append(text(60, 210, "РІВЕНЬ 2: КООРДИНАЦІЯ ВСІЄЇ СИСТЕМИ (50–100 Гц, Whole-Body Coordination)", size=12, bold=True, color="#1d4ed8", anchor="start"))

    frags.append(fitbox(60, 220, 215, 76, "Кінематична надлишковість\nСпільний якобіан J_wb(q)\nБаза (SE(3)) + Рука (q_1..q_n)\nРозмірність q > 6", fill="#ffffff", stroke="#bfdbfe", size=11))
    frags.append(fitbox(295, 220, 230, 76, "Проекція в нуль-простір N(J)\nГоловна задача: інструмент у x_d\nВторинна: стійкість бази,\nвіддалення від упорів суглобів", fill="#ffffff", stroke="#bfdbfe", size=11))
    frags.append(fitbox(545, 220, 215, 76, "Узгодження динаміки\nПовільна масивна база (10 Гц)\n+\nШвидка легка рука (500 Гц)", fill="#ffffff", stroke="#bfdbfe", size=11))

    # Стрілка вниз від рівня 2 до рівня 3
    frags.append(arrow(410, 309, 410, 331, color="#2563eb", sw=2))
    frags.append(text(420, 323, "q_cmd, q'_cmd", size=11, color="#2563eb", anchor="start", bold=True))

    # Рівень 3: Силовий контур реального часу (500-1000 Гц)
    frags.append(rect(40, 334, 740, 148, fill="#fef2f2", stroke="#fca5a5", sw=1.5))
    frags.append(text(60, 356, "РІВЕНЬ 3: СИЛОВИЙ КОНТУР РЕАЛЬНОГО ЧАСУ (500–1000 Гц, Hard Real-Time)", size=12, bold=True, color="#b91c1c", anchor="start"))

    frags.append(fitbox(60, 366, 170, 104, "6-DOF F/T сенсор\nВимірювання F_ext, tau_ext\nФільтрація брязкоту\nЗатримка < 1 мс", fill="#ffffff", stroke="#fecaca", size=11))
    frags.append(fitbox(245, 366, 235, 104, "Адмітансний / Імпедансний регулятор\nM_d e'' + D_d e' + K_d e = -F_ext\nОбчислення віртуальної піддатливості\nКорекція траєкторії Delta_x", fill="#ffffff", stroke="#fecaca", size=11))
    frags.append(fitbox(495, 366, 140, 104, "FOC драйвери моторів\nКонтур моменту / струму\nШина CAN FD / EtherCAT\nПряма реакція на зріз", fill="#ffffff", stroke="#fecaca", size=11))
    frags.append(fitbox(645, 366, 120, 104, "Захист Failsafe\nОбмеження F_max\nАварійне втягування\n(Retract)", fill="#fee2e2", stroke=POS, size=11, color="#991b1b"))

    render(os.path.join(OUT_DIR, "whole-body-control-layers.svg"), w, h, *frags)


if __name__ == '__main__':
    fig_delivery_vs_interaction()
    fig_whole_body_control_layers()
    print("Figures generated successfully.")
