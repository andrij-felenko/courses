# -*- coding: utf-8 -*-
"""Фігури для теми «Атаки по побічних каналах у криптографії»
(book/algorithms/complexity-computability/side-channel-attacks)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

COLOR_HEADER = "#e2e8f0"
COLOR_ACCENT = "#2563eb"
COLOR_ALERT = "#dc2626"
COLOR_WARN = "#d97706"
COLOR_SUCCESS = "#059669"
COLOR_PANEL = "#f8fafc"
COLOR_BORDER = "#cbd5e1"
COLOR_MUTED = "#64748b"
COLOR_LINE = "#333333"

def fig1_side_channel_taxonomy():
    """Фігура 1: Таксономія атак по побічних каналах: фізичні канали, методи спостереження та моделі витоку."""
    W, H = 960, 520
    frags = []

    # Заголовок
    tb_title, _, _ = textbox(480, 30, "Таксономія витоків інформації та класифікація атак по побічних каналах",
                             size=15, bold=True, fill=COLOR_HEADER, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(tb_title)

    # Ліва колонка: Класифікація за фізичним носієм (Physical Modality)
    frags.append(rect(25, 70, 285, 430, fill=COLOR_PANEL, stroke=COLOR_BORDER, sw=1.5, rx=10))
    frags.append(text(167, 98, "Фізичний носій витоку", size=13, bold=True, color="#1e3a8a"))
    frags.append(text(167, 116, "Фізичні еманації процесу обчислень", size=10, italic=True, color=COLOR_MUTED))

    frags.append(textbox(167, 160, "Часові витоки (Timing)\n• Розгалуження за секретними даними\n• Варіація кеш-латентності пам'яті", size=10.5, fill="#ffffff", stroke="#2563eb", pad=8)[0])
    frags.append(textbox(167, 245, "Споживання струму (Power)\n• Простий аналіз (SPA)\n• Диференційний/кореляційний (DPA/CPA)", size=10.5, fill="#ffffff", stroke="#dc2626", pad=8)[0])
    frags.append(textbox(167, 330, "Електромагнітне випромінювання\n• Near-field зондування чіпа (SEMA/DEMA)\n• Просторове локалізування блоків", size=10.5, fill="#ffffff", stroke="#7c3aed", pad=8)[0])
    frags.append(textbox(167, 420, "Акустичні та фотонні еманації\n• Акустичний шум керамічних конденсаторів\n• Фотонна емісія перемикання транзисторів", size=10, fill="#ffffff", stroke="#059669", pad=8)[0])

    # Центральна колонка: Класифікація за способом доступу (Invasiveness & Access)
    frags.append(rect(335, 70, 290, 430, fill=COLOR_PANEL, stroke=COLOR_BORDER, sw=1.5, rx=10))
    frags.append(text(480, 98, "Рівень втручання та доступ", size=13, bold=True, color="#1e3a8a"))
    frags.append(text(480, 116, "Ступінь деструктивного впливу", size=10, italic=True, color=COLOR_MUTED))

    frags.append(textbox(480, 165, "Неінвазивні (Non-invasive)\n• Тільки зовнішні вимірювання\n• Осцилограф, таймер, зонд струму\n• Чіп і корпус залишаються неушкодженими", size=10.5, fill="#ffffff", stroke="#059669", pad=8)[0])
    frags.append(textbox(480, 280, "Напівінвазивні (Semi-invasive)\n• Декапсуляція корпусу (зняття пластику)\n• Доступ до кремнієвого кристала без зондів\n• Лазерне збурення, фотонні вимірювання", size=10.5, fill="#ffffff", stroke="#d97706", pad=8)[0])
    frags.append(textbox(480, 405, "Повністю інвазивні (Invasive)\n• Пряме мікрозондування шин чіпа\n• Використання FIB (фокусованого пучка)\n• Модифікація внутрішніх провідників", size=10.5, fill="#ffffff", stroke="#dc2626", pad=8)[0])

    # Права колонка: Класифікація за типом взаємодії (Interaction Model)
    frags.append(rect(650, 70, 285, 430, fill=COLOR_PANEL, stroke=COLOR_BORDER, sw=1.5, rx=10))
    frags.append(text(792, 98, "Режим впливу на систему", size=13, bold=True, color="#1e3a8a"))
    frags.append(text(792, 116, "Пасивне читання vs активні збої", size=10, italic=True, color=COLOR_MUTED))

    frags.append(textbox(792, 180, "Пасивні атаки (Passive SCA)\n• Тільки моніторинг побічних сигналів\n• Специфікація алгоритму не порушується\n• Не залишають слідів у системі\n• Мета: вилучення секретного ключа", size=10.5, fill="#ffffff", stroke="#2563eb", pad=8)[0])
    frags.append(textbox(792, 335, "Активні атаки (Fault Injection / DFA)\n• Навмисне внесення фізичних збоїв\n• Перепади напруги живлення (Glitching)\n• Тактові збої, лазерне перемикання бітів\n• Диференційний аналіз помилок (DFA)", size=10.5, fill="#ffffff", stroke="#dc2626", pad=8)[0])
    frags.append(textbox(792, 455, "Комбіновані атаки (Combined Attacks)\n• Індукування збоїв та аналіз SPA/DPA", size=9.5, fill="#fef2f2", stroke="#b91c1c", pad=6)[0])

    render(os.path.join(IMG, "side-channel-taxonomy.svg"), W, H, *frags)


def fig2_dpa_correlation_pipeline():
    """Фігура 2: Конвеєр кореляційного аналізу споживання потужності (CPA) та пік кореляції."""
    W, H = 960, 500
    frags = []

    # Заголовок
    tb_title, _, _ = textbox(480, 30, "Математичний конвеєр кореляційного аналізу потужності (CPA)",
                             size=15, bold=True, fill=COLOR_HEADER, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(tb_title)

    # Верхній контур: Експеримент та збір осцилограм
    frags.append(rect(25, 65, 910, 160, fill=COLOR_PANEL, stroke=COLOR_BORDER, sw=1.5, rx=8))
    frags.append(text(140, 88, "Етап 1: Фізичний збір трас", size=12, bold=True, color="#1e3a8a"))

    frags.append(textbox(130, 145, "Відкриті вхідні дані\nm₁, m₂, ..., m_N\n(Відомі вектори)", size=10, fill="#ffffff", stroke="#2563eb")[0])
    frags.append(arrow(210, 145, 270, 145, color=COLOR_LINE, sw=1.8))
    frags.append(text(240, 135, "Шифрування", size=9.5, color=COLOR_MUTED))

    frags.append(textbox(380, 145, "Криптографічний пристрій\nAES / RSA (невідомий ключ k*)\nРезистор R_shunt на лінії V_dd", size=10, fill="#fef3c7", stroke="#d97706")[0])
    frags.append(arrow(490, 145, 550, 145, color=COLOR_LINE, sw=1.8))
    frags.append(text(520, 135, "Осцилограф", size=9.5, color=COLOR_MUTED))

    frags.append(textbox(740, 145, "Матриця фізичних трас струму T[N × M]\nN запитів, M часових відліків на трасу\nT_i(t) = P_device(t) + Шум(t)", size=10, fill="#ffffff", stroke="#dc2626")[0])

    # Нижній лівий блок: Гіпотетична модель витоку
    frags.append(rect(25, 245, 435, 235, fill=COLOR_PANEL, stroke=COLOR_BORDER, sw=1.5, rx=8))
    frags.append(text(242, 268, "Етап 2: Гіпотетична модель витоку H", size=12, bold=True, color="#1e3a8a"))

    frags.append(textbox(242, 320, "Перебір гіпотез байта ключа: k_g ∈ {0, 1, ..., 255}\nПроміжне значення: v_{i, k_g} = Sbox(m_i ⊕ k_g)", size=10, fill="#ffffff", stroke="#7c3aed")[0])
    frags.append(textbox(242, 395, "Модель ваги Геммінґа (Hamming Weight):\nH_{i, k_g} = HW(v_{i, k_g}) = ∑ бітів v_{i, k_g}\nМатриця прогнозів H розміром [N × 256]", size=10, bold=True, fill="#f3e8ff", stroke="#7e22ce")[0])

    # Нижній правий блок: Статистичний кореляційний аналізатор
    frags.append(rect(480, 245, 455, 235, fill=COLOR_PANEL, stroke=COLOR_BORDER, sw=1.5, rx=8))
    frags.append(text(707, 268, "Етап 3: Обчислення кореляції Пірсона та пік", size=12, bold=True, color="#1e3a8a"))

    frags.append(textbox(707, 320, "Коефіцієнт кореляції Пірсона ρ(k_g, t):\nρ = Cov(H_{k_g}, T(t)) / [ σ(H_{k_g}) · σ(T(t)) ]", size=10, fill="#ffffff", stroke="#059669")[0])
    frags.append(textbox(707, 400, "Ідентифікація істинного ключа k*:\n• Для k_g = k* виникає гострий пік |ρ| >> 0 на моменті S-box\n• Для хибних k_g ≠ k* кореляція залишається в шумі |ρ| ≈ 0\nk* = argmax_{k_g} max_t |ρ(k_g, t)|", size=9.5, bold=True, fill="#d1fae5", stroke="#059669")[0])

    render(os.path.join(IMG, "dpa-correlation-pipeline.svg"), W, H, *frags)


def fig3_cache_timing_flush_reload():
    """Фігура 3: Мікроархітектурна атака по кеш-пам'яті Flush+Reload."""
    W, H = 960, 470
    frags = []

    # Заголовок
    tb_title, _, _ = textbox(480, 30, "Мікроархітектурний канал витоку: хронологія атаки Flush+Reload",
                             size=15, bold=True, fill=COLOR_HEADER, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(tb_title)

    # 3 Кроки атаки
    step_w = 285
    # Фаза 1: Flush
    frags.append(rect(25, 70, step_w, 375, fill=COLOR_PANEL, stroke=COLOR_BORDER, sw=1.5, rx=10))
    frags.append(textbox(167, 98, "Крок 1: Очищення (Flush)", size=12, bold=True, fill="#fee2e2", stroke="#ef4444", pad=6)[0])
    frags.append(text(167, 132, "Атакуючий витісняє лінію", size=10, italic=True, color=COLOR_MUTED))

    frags.append(textbox(167, 185, "Атакуючий виконує інструкцію:\nclflush(&T_table[line_idx])", size=10, fill="#ffffff", stroke="#dc2626")[0])
    frags.append(textbox(167, 275, "Стан кеш-ієрархії L1 / L2 / L3:\nЦільова лінія гарантовано\nвидалена з усіх рівнів кешу.\nБудь-який доступ викличе Cache Miss.", size=10, fill="#ffffff", stroke=COLOR_BORDER)[0])
    frags.append(textbox(167, 375, "Очікування жертви:\nАтакуючий віддає квант часу CPU", size=9.5, fill="#f8fafc", stroke=COLOR_MUTED)[0])

    # Фаза 2: Victim execution
    frags.append(rect(335, 70, step_w, 375, fill=COLOR_PANEL, stroke=COLOR_BORDER, sw=1.5, rx=10))
    frags.append(textbox(477, 98, "Крок 2: Виконання жертви", size=12, bold=True, fill="#fef3c7", stroke="#f59e0b", pad=6)[0])
    frags.append(text(477, 132, "Криптографічна операція", size=10, italic=True, color=COLOR_MUTED))

    frags.append(textbox(477, 185, "Жертва шифрує блок даних:\nВиконує доступ до таблиці T-box:\ny = T_table[k ⊕ p]", size=10, fill="#ffffff", stroke="#d97706")[0])
    frags.append(textbox(477, 280, "Зміна мікроархітектурного стану:\n• Якщо (k ⊕ p) потрапляє в line_idx,\n  рядок завантажується в кеш L1/L3\n• Якщо жертва не зверталась до рядка,\n  він залишається в оперативній пам'яті (RAM)", size=9.5, bold=True, fill="#fffbeb", stroke="#b45309")[0])
    frags.append(textbox(477, 380, "Побічний ефект:\nСекретний ключ k змінює стан кешу", size=9.5, fill="#fef2f2", stroke="#dc2626")[0])

    # Фаза 3: Reload & Measure
    frags.append(rect(645, 70, step_w, 375, fill=COLOR_PANEL, stroke=COLOR_BORDER, sw=1.5, rx=10))
    frags.append(textbox(787, 98, "Крок 3: Перезавантаження й замір", size=12, bold=True, fill="#d1fae5", stroke="#10b981", pad=6)[0])
    frags.append(text(787, 132, "Вимірювання часу доступу", size=10, italic=True, color=COLOR_MUTED))

    frags.append(textbox(787, 190, "Атакуючий заміряє час доступу:\nt_start = __rdtsc();\nvolatile uint32_t val = *addr;\nt_delta = __rdtsc() - t_start;", size=9.5, fill="#ffffff", stroke="#059669")[0])
    frags.append(textbox(787, 290, "Класифікація за порогом T_th:\n• t_delta < 80 циклів (Cache Hit):\n  Жертва зверталась до рядка → k ⊕ p = line\n• t_delta > 200 циклів (Cache Miss):\n  Жертва не зверталась до рядка", size=9.5, bold=True, fill="#ecfdf5", stroke="#059669")[0])
    frags.append(textbox(787, 385, "Результат:\nПовне відновлення байтів ключа k", size=10, bold=True, fill="#dbeafe", stroke="#2563eb")[0])

    render(os.path.join(IMG, "cache-timing-flush-reload.svg"), W, H, *frags)


if __name__ == "__main__":
    fig1_side_channel_taxonomy()
    fig2_dpa_correlation_pipeline()
    fig3_cache_timing_flush_reload()
    print("Всі 3 фігури успішно згенеровано.")
