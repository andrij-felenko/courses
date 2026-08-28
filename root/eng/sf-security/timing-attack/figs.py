# -*- coding: utf-8 -*-
"""Фігури для теми «Побічні канали: час і кеш» (timing-attack)."""
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


def fig1_timing_leak_early_exit():
    """Фігура 1: Порівняння дострокового виходу (early-exit) та константного часу виконання."""
    W, H = 960, 490
    frags = []

    # Заголовок
    tb_title, _, _ = textbox(480, 28, "Порівняння алгоритмів перевірки: ранній вихід проти константного часу",
                             size=15, bold=True, fill=COLOR_HEADER, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(tb_title)

    # Ліва колонка: Вразливий memcmp (Early Exit)
    frags.append(rect(25, 60, 440, 410, fill=COLOR_PANEL, stroke="#fca5a5", sw=1.8, rx=8))
    frags.append(textbox(245, 88, "Вразливий алгоритм: достроковий вихід (Early Exit)", size=12, bold=True, color="#991b1b", fill="#fee2e2", stroke="#ef4444", pad=6)[0])

    # Сходинки байтів
    frags.append(textbox(245, 140, "Спроба 1: Помилка у байті 0 -> вихід на 1-й ітерації\nЧас виконання: T0 = t_base + 1·Δt (найкоротший час)", size=9.5, fill="#ffffff", stroke="#ef4444", pad=6)[0])
    frags.append(textbox(245, 205, "Спроба 2: Байт 0 вгадано, помилка у байті 1 -> вихід на 2-й\nЧас виконання: T1 = t_base + 2·Δt (+1 дельта затримки)", size=9.5, fill="#ffffff", stroke="#f97316", pad=6)[0])
    frags.append(textbox(245, 270, "Спроба 3: Байти 0..k-1 вгадано, помилка у байті k\nЧас виконання: Tk = t_base + (k+1)·Δt (лінійне зростання)", size=9.5, fill="#ffffff", stroke="#d97706", pad=6)[0])

    frags.append(textbox(245, 345, "Сходинковий витік секрету (Timing Leakage):\nАтакуючий перебирає 256 варіантів кожного байта.\nПравильний байт дає вимірюваний сплеск латентності (+Δt).\nСкладність зламу 32-байтного HMAC: 32 x 256 = 8192 спроби!", size=9.5, bold=True, color="#991b1b", fill="#fef2f2", stroke="#b91c1c", pad=8)[0])

    frags.append(textbox(245, 430, "Повний крах стійкості: 2^256 варіантів -> 8192 заміри часу", size=10, bold=True, color="#ffffff", fill="#dc2626", stroke="#991b1b", pad=6)[0])

    # Права колонка: Безпечний ct_memcmp (Constant Time)
    frags.append(rect(495, 60, 440, 410, fill=COLOR_PANEL, stroke="#86efac", sw=1.8, rx=8))
    frags.append(textbox(715, 88, "Безпечний алгоритм: константний час (Constant-Time)", size=12, bold=True, color="#166534", fill="#dcfce7", stroke="#22c55e", pad=6)[0])

    frags.append(textbox(715, 140, "Спроба 1: Помилка у байті 0 -> цикл триває до кінця (N байтів)\nАкумулятор: diff |= a[0] ^ b[0]; час: T_const = t_base + N·Δt", size=9.5, fill="#ffffff", stroke="#22c55e", pad=6)[0])
    frags.append(textbox(715, 205, "Спроба 2: Байти збігаються -> цикл так само триває до кінця\nАкумулятор: diff |= a[i] ^ b[i]; час: T_const = t_base + N·Δt", size=9.5, fill="#ffffff", stroke="#22c55e", pad=6)[0])
    frags.append(textbox(715, 270, "Спроба 3: Довільні дані -> виконання завжди проходить N кроків\nФінальна перевірка: return (diff == 0) без раннього виходу", size=9.5, fill="#ffffff", stroke="#22c55e", pad=6)[0])

    frags.append(textbox(715, 345, "Повна відсутність часового каналу (Zero Timing Leak):\nЧас виконання суворо однаковий для будь-яких вхідних даних.\nРозподіл затримок однаковий для хибних та істинних підписів.\nВитягти інформацію через статистичний аналіз неможливо.", size=9.5, bold=True, color="#166534", fill="#f0fdf4", stroke="#15803d", pad=8)[0])

    frags.append(textbox(715, 430, "Математична стійкість збережена: повний простір 2^256 ключів", size=10, bold=True, color="#ffffff", fill="#059669", stroke="#047857", pad=6)[0])

    render(os.path.join(IMG, "timing-leak-early-exit.svg"), W, H, *frags)


def fig2_constant_time_bitwise_multiplexing():
    """Фігура 2: Умовне розгалуження в конвеєрі процесора проти безгалузевого мультиплексування."""
    W, H = 960, 480
    frags = []

    # Заголовок
    tb_title, _, _ = textbox(480, 28, "Виконання умовного вибору: розгалуження процесора проти бітової маски",
                             size=15, bold=True, fill=COLOR_HEADER, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(tb_title)

    # Ліва колонка: if (secret_bit)
    frags.append(rect(25, 60, 440, 400, fill=COLOR_PANEL, stroke="#fca5a5", sw=1.8, rx=8))
    frags.append(textbox(245, 88, "Умовне розгалуження: if (secret_bit)", size=12, bold=True, color="#991b1b", fill="#fee2e2", stroke="#ef4444", pad=6)[0])

    frags.append(textbox(245, 145, "Інструкція умовного переходу (JNE / JEQ / CBZ)\nБлок прогнозування переходів (Branch Predictor: BTB / BHT)", size=10, fill="#ffffff", stroke="#ef4444", pad=6)[0])

    frags.append(textbox(245, 225, "Гілка 1: secret_bit = 1\nВиконується операція (MUL / ADD)\nЧас: T_true = N тактів CPU", size=9.5, fill="#fef2f2", stroke="#ef4444", pad=6)[0])
    frags.append(textbox(245, 295, "Гілка 0: secret_bit = 0\nОперація пропускається\nЧас: T_false = M тактів CPU", size=9.5, fill="#fef2f2", stroke="#ef4444", pad=6)[0])

    frags.append(textbox(245, 385, "Штраф за хибне передбачення (Branch Misprediction):\nОчищення конвеєра (Pipeline Flush) додає 15-20 тактів затримки.\nІсторія переходів залишає слід у стані апаратного предиктора!\nСекретний біт безпосередньо модулює час обчислення.", size=9.5, bold=True, color="#991b1b", fill="#fee2e2", stroke="#dc2626", pad=8)[0])

    # Права колонка: Branchless ct_select
    frags.append(rect(495, 60, 440, 400, fill=COLOR_PANEL, stroke="#86efac", sw=1.8, rx=8))
    frags.append(textbox(715, 88, "Безгалузевий мультиплексор: ct_select(mask, a, b)", size=12, bold=True, color="#166534", fill="#dcfce7", stroke="#22c55e", pad=6)[0])

    frags.append(textbox(715, 145, "Формування бітової маски з секретного біта:\nmask = -(secret_bit)  ->  0x00000000 або 0xFFFFFFFF", size=10, fill="#ffffff", stroke="#22c55e", pad=6)[0])

    frags.append(textbox(715, 225, "Побітове комбінування без стрибків адреси:\nresult = (a & mask) | (b & ~mask)\nОбчислюються обидва операнди в однаковий спосіб", size=9.5, fill="#f0fdf4", stroke="#22c55e", pad=6)[0])
    frags.append(textbox(715, 295, "Лінійна послідовність інструкцій АЛП (AND, OR, NOT, NEG)\nНемає переходів, немає передбачення, немає стрибків адреси", size=9.5, fill="#f0fdf4", stroke="#22c55e", pad=6)[0])

    frags.append(textbox(715, 385, "Детермінований час конвеєра (Constant Cycles):\nРівно 3-4 такти АЛП незалежно від значення secret_bit.\nЖодного скидання черги інструкцій та впливу на стан BTB.\nКомпіляторні бар'єри гарантують збереження безгалузевості.", size=9.5, bold=True, color="#166534", fill="#dcfce7", stroke="#15803d", pad=8)[0])

    render(os.path.join(IMG, "constant-time-bitwise-multiplexing.svg"), W, H, *frags)


def fig3_cache_line_lookup_leak():
    """Фігура 3: Витік через патерни звернення до ліній кеш-пам'яті при табличних підстановках AES S-box."""
    W, H = 960, 480
    frags = []

    # Заголовок
    tb_title, _, _ = textbox(480, 28, "Побічний канал кеш-пам'яті: витік секретного індексу при табличних перетвореннях",
                             size=15, bold=True, fill=COLOR_HEADER, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(tb_title)

    # Верхній блок: Таблиця підстановок S-box / T-table у пам'яті
    frags.append(rect(25, 60, 910, 130, fill=COLOR_PANEL, stroke=COLOR_BORDER, sw=1.5, rx=8))
    frags.append(text(480, 82, "Структура таблиці підстановок AES S-Box у пам'яті (256 байтів = 4 кеш-лінії по 64 байти)", size=12, bold=True, color="#1e3a8a"))

    # 4 кеш-лінії
    frags.append(textbox(140, 135, "Кеш-лінія 0 (байти 0..63)\nЕлементи S-Box: 0x00..0x3F\nСтан: Холодна (DRAM)", size=9.5, fill="#ffffff", stroke="#94a3b8")[0])
    frags.append(textbox(370, 135, "Кеш-лінія 1 (байти 64..127)\nЕлементи S-Box: 0x40..0x7F\nСтан: Завантажена в L1 (Hot!)", size=9.5, bold=True, fill="#fee2e2", stroke="#dc2626")[0])
    frags.append(textbox(600, 135, "Кеш-лінія 2 (байти 128..191)\nЕлементи S-Box: 0x80..0xBF\nСтан: Холодна (DRAM)", size=9.5, fill="#ffffff", stroke="#94a3b8")[0])
    frags.append(textbox(820, 135, "Кеш-лінія 3 (байти 192..255)\nЕлементи S-Box: 0xC0..0xFF\nСтан: Холодна (DRAM)", size=9.5, fill="#ffffff", stroke="#94a3b8")[0])

    # Нижній лівий блок: Процес шифрування та звернення до пам'яті
    frags.append(rect(25, 205, 440, 255, fill=COLOR_PANEL, stroke=COLOR_BORDER, sw=1.5, rx=8))
    frags.append(text(245, 228, "Крок 1: Обчислення індексу в AES", size=12, bold=True, color="#1e3a8a"))

    frags.append(textbox(245, 275, "Операція SubBytes: index = state[i] ^ key[i]\nІндекс безпосередньо залежить від секретного ключа key[i]!", size=9.5, fill="#ffffff", stroke="#2563eb", pad=6)[0])
    frags.append(textbox(245, 340, "Процесор читає пам'ять: SBox[index]\nДо L1-кешу підтягується відповідна 64-байтна кеш-лінія.\nЯкщо index ∈ [64..127], у кеш потрапляє Кеш-лінія 1.", size=9.5, fill="#fef3c7", stroke="#d97706", pad=6)[0])
    frags.append(textbox(245, 415, "Побічний ефект: Стан апаратного кешу змінюється залежно від key[i]", size=9.5, bold=True, color="#991b1b", fill="#fee2e2", stroke="#dc2626", pad=6)[0])

    # Нижній правий блок: Спостереження атакуючого (Flush+Reload / Prime+Probe)
    frags.append(rect(495, 205, 440, 255, fill=COLOR_PANEL, stroke=COLOR_BORDER, sw=1.5, rx=8))
    frags.append(text(715, 228, "Крок 2: Замір латентності атакуючим", size=12, bold=True, color="#1e3a8a"))

    frags.append(textbox(715, 275, "Атакуючий вимірює час доступу до кеш-ліній таблиці S-Box:\nІнструкція таймера: rdtsc / rdtscp (високоточні цикли CPU)", size=9.5, fill="#ffffff", stroke="#2563eb", pad=6)[0])
    frags.append(textbox(715, 340, "Лінія 1: Швидкий доступ ~4 такти (L1 Cache Hit -> Було звернення!)\nЛінії 0, 2, 3: Повільний доступ ~200 тактів (DRAM Cache Miss)", size=9.5, bold=True, fill="#dcfce7", stroke="#059669", pad=6)[0])
    frags.append(textbox(715, 415, "Відновлення ключа: key[i] = index ^ state[i] через серію запитів", size=9.5, bold=True, color="#1e3a8a", fill="#eff6ff", stroke="#3b82f6", pad=6)[0])

    render(os.path.join(IMG, "cache-line-lookup-leak.svg"), W, H, *frags)


if __name__ == "__main__":
    fig1_timing_leak_early_exit()
    fig2_constant_time_bitwise_multiplexing()
    fig3_cache_line_lookup_leak()
    print("Фігури успішно згенеровано в img/")
