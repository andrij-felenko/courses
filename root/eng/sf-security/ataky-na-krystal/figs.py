# -*- coding: utf-8 -*-
import sys, os

# Шлях до scripts/ у корені репозиторію (4 рівні вгору від root/eng/sf-security/ataky-na-krystal)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Кольорова палітра ────────────────────────────────────────────────
CLR_FAULT   = "#c0392b"     # Збої, ін'єкції, небезпека
CLR_FAULT_F = "#fdecea"
CLR_SAFE    = "#27ae60"     # Захист, норма, валідація
CLR_SAFE_F  = "#eafaf0"
CLR_WARN    = "#d97706"     # Попередження, витік, проміжний стан
CLR_WARN_F  = "#fef3c7"
CLR_CORE    = "#2457d6"     # Ядро, тактування, живлення
CLR_CORE_F  = "#eaf0fd"
CLR_BUS     = "#4b5563"     # Шини, провідники, сигнали
CLR_BUS_F   = "#f3f4f6"
CLR_SILICON = "#6b21a8"     # Кристал, шари металу, кремній
CLR_SILICON_F = "#f5f3ff"


# ── 1. Фізичні механізми ін'єкції збоїв ──────────────────────────────
def fig_glitch_mechanisms():
    W, H = 1040, 520
    p = []

    p.append(text(W / 2, 28, "Фізичні механізми апаратних збоїв (Fault Injection)", size=16, color=INK, bold=True))

    cols = [
        (180, "Voltage Glitching (Просідання живлення)",
         "Зниження напруги Vdd на 10–50 нс",
         [("Фізика процесу:\nЗниження напруги Vdd збільшує\nзатримку поширення вентилів t_pd:\nt_pd ~ Vdd / (Vdd - Vth)²", CLR_CORE_F, CLR_CORE),
          ("Наслідок для логіки:\nt_pd перевищує період такту T_clk.\nТригер D-типу фіксує старий\nабо метастабільний стан", CLR_FAULT_F, CLR_FAULT),
          ("Результат для процесора:\nІнструкція перевірки (CMP, BEQ)\nвиконується як NOP або\nскидає прапорець помилки", CLR_WARN_F, CLR_WARN)]),

        (520, "Clock Glitching (Тактовий збій)",
         "Введення надкороткого імпульсу такту",
         [("Фізика процесу:\nГенерація імпульсу з тривалістю\nt_pulse < t_min_high / t_min_low\nна зовнішньому тактовому вході", CLR_CORE_F, CLR_CORE),
          ("Наслідок для логіки:\nПорушення часу встановлення t_setup.\nКомбінаційна логіка АЛП не встигає\nзавершити обчислення", CLR_FAULT_F, CLR_FAULT),
          ("Результат для процесора:\nЛічильник команд PC пропускає крок,\nзчитується неправильний операнд,\nобхід циклу автентифікації", CLR_WARN_F, CLR_WARN)]),

        (860, "Laser Fault Injection (LFI)",
         "Локальне опромінення кремнію лазером",
         [("Фізика процесу:\nІЧ-лазер (1064 нм) крізь кремнієву\nпідкладку генерує пари електрон-дірка\nу зворотно зміщених p-n переходах", CLR_SILICON_F, CLR_SILICON),
          ("Наслідок для логіки:\nІмпульс фотоструму розряджає вузол\nSRAM-комірки чи тригера регістра.\nТочкове перемикання біта (Bit-Flip)", CLR_FAULT_F, CLR_FAULT),
          ("Результат для процесора:\nЗміна значення ключа в регістрі,\nпримусова модифікація пам'яті OTP,\nпомилка підпису RSA-CRT", CLR_WARN_F, CLR_WARN)]),
    ]

    for cx, title, subtitle, boxes in cols:
        p.append(rect(cx - 155, 52, 310, 448, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
        p.append(text(cx, 76, title, size=13, color=INK, bold=True))
        p.append(text(cx, 94, subtitle, size=11, color=MUTED, italic=True))

        y_pos = [118, 226, 334]
        for i, (txt, fill_c, strk_c) in enumerate(boxes):
            p.append(fitbox(cx - 145, y_pos[i], 290, 94, txt, size=12, fill=fill_c, stroke=strk_c, sw=1.4))

    return render(os.path.join(OUT, "glitch-injection-mechanisms.svg"), W, H, *p)


# ── 2. Аналіз побічних каналів: SPA проти DPA ────────────────────────
def fig_side_channel_analysis():
    W, H = 1040, 530
    p = []

    p.append(text(W / 2, 28, "Аналіз побічних каналів: пряме спостереження (SPA) та диференційний аналіз (DPA/CPA)", size=16, color=INK, bold=True))

    # Ліва секція: SPA (Simple Power Analysis)
    p.append(rect(30, 55, 460, 455, fill="#ffffff", stroke=CLR_CORE, sw=1.5, rx=8))
    p.append(text(260, 80, "Простий аналіз енергоспоживання (SPA)", size=13, color=CLR_CORE, bold=True))
    p.append(text(260, 98, "Візуальна реконструкція алгоритму за однією осцилограмою", size=11, color=MUTED, italic=True))

    p.append(rect(50, 115, 420, 160, fill="#f8fafc", stroke=LINE, sw=1.0, rx=6))
    p.append(text(260, 135, "Осцилограма струму I(t) під час RSA Square-and-Multiply", size=11, color=INK, bold=True))

    # Симуляція осцилограми SPA: піки для Square (S) та Multiply (M)
    p.append(rect(65, 155, 55, 80, fill=CLR_CORE_F, stroke=CLR_CORE, sw=1.2, rx=4))
    p.append(text(92, 195, "Square\n(біт 0)", size=11, color=CLR_CORE, bold=True))

    p.append(rect(130, 155, 55, 80, fill=CLR_CORE_F, stroke=CLR_CORE, sw=1.2, rx=4))
    p.append(text(157, 195, "Square", size=11, color=CLR_CORE, bold=True))

    p.append(rect(190, 155, 80, 80, fill=CLR_WARN_F, stroke=CLR_WARN, sw=1.4, rx=4))
    p.append(text(230, 195, "Multiply\n(біт 1)", size=11, color=CLR_WARN, bold=True))

    p.append(rect(280, 155, 55, 80, fill=CLR_CORE_F, stroke=CLR_CORE, sw=1.2, rx=4))
    p.append(text(307, 195, "Square\n(біт 0)", size=11, color=CLR_CORE, bold=True))

    p.append(rect(345, 155, 55, 80, fill=CLR_CORE_F, stroke=CLR_CORE, sw=1.2, rx=4))
    p.append(text(372, 195, "Square", size=11, color=CLR_CORE, bold=True))

    p.append(rect(405, 155, 60, 80, fill=CLR_WARN_F, stroke=CLR_WARN, sw=1.4, rx=4))
    p.append(text(435, 195, "Multiply\n(біт 1)", size=11, color=CLR_WARN, bold=True))

    p.append(fitbox(50, 290, 420, 205,
                    "Механізм атаки:\n• Різні математичні інструкції активують різні вузли АЛП.\n• Множення (MUL) містить каскади суматорів і споживає\n  значно більший струм, ніж піднесення до квадрата (SQR).\n• Атакуючий візуально зчитує секретний ключ d:\n  d = 0b0101...\n\nЗахист: алгоритми з постійним часом (Montgomery Ladder).",
                    size=11, fill="#ffffff", stroke=LINE, sw=1.0))

    # Права секція: DPA / CPA (Differential / Correlation Power Analysis)
    p.append(rect(510, 55, 500, 455, fill="#ffffff", stroke=CLR_FAULT, sw=1.5, rx=8))
    p.append(text(760, 80, "Диференційний та кореляційний аналіз (DPA/CPA)", size=13, color=CLR_FAULT, bold=True))
    p.append(text(760, 98, "Статистичне відновлення ключа через тисячі осцилограм", size=11, color=MUTED, italic=True))

    p.append(rect(530, 115, 460, 160, fill="#f8fafc", stroke=LINE, sw=1.0, rx=6))
    p.append(text(760, 135, "Модель витоку: Вага Геммінґа HW(S-Box(P ⊕ k_guess))", size=11, color=INK, bold=True))

    # Візуалізація кореляційного піка CPA
    p.append(line(550, 240, 970, 240, color=MUTED, sw=1.0)) # Нульова лінія
    p.append(text(540, 243, "0", size=10, color=MUTED))

    # Шумові гіпотези
    for x_noise in [580, 620, 660, 700, 780, 820, 860, 900, 940]:
        p.append(line(x_noise, 235, x_noise + 15, 245, color=CLR_BUS, sw=1.0))
        p.append(line(x_noise + 15, 245, x_noise + 30, 238, color=CLR_BUS, sw=1.0))

    # Правильна гіпотеза (величезний кореляційний пік)
    p.append(line(720, 240, 740, 160, color=CLR_FAULT, sw=2.2))
    p.append(line(740, 160, 760, 240, color=CLR_FAULT, sw=2.2))
    p.append(circle(740, 160, 4, fill=CLR_FAULT, stroke=CLR_FAULT))
    p.append(text(740, 150, "Пік кореляції: k* = 0x2B", size=11, color=CLR_FAULT, bold=True))

    p.append(fitbox(530, 290, 460, 205,
                    "Механізм атаки:\n1. Запис N = 10 000 осцилограм споживання при випадкових текстах P_i.\n2. Обчислення гіпотетичного значення байта проміжного стану:\n   V(i, k) = S-Box(P_i ⊕ k).\n3. Розрахунок моделі енергоспоживання (Hamming Weight HW(V)).\n4. Обчислення коефіцієнта кореляції Пірсона ρ(k) для всіх 256 ключів.\n5. Для правильного k* виникає статистичний сплеск ρ > 0.7.\n\nЗахист: маскування булевими частками (Boolean Masking).",
                    size=11, fill="#ffffff", stroke=LINE, sw=1.0))

    return render(os.path.join(OUT, "side-channel-power-analysis.svg"), W, H, *p)


# ── 3. Апаратний захист кристала (Silicon Die Hardening) ──────────────
def fig_hardware_die_protection():
    W, H = 1040, 520
    p = []

    p.append(text(W / 2, 28, "Апаратний захист кристала мікроконтролера на рівні кремнію", size=16, color=INK, bold=True))

    # Схема шарів кристала
    p.append(rect(40, 55, 450, 445, fill="#ffffff", stroke=CLR_SILICON, sw=1.5, rx=8))
    p.append(text(265, 80, "Топологія захищеного кристала (Secure Die)", size=13, color=CLR_SILICON, bold=True))

    layers = [
        ("Активний захисний екран (Active Metal Shield)\nВерхній шар металу M6/M7: серпантинна сітка під динамічним\nпсевдовипадковим сигналом PRNG (детектор обриву/КЗ зондом)", CLR_SILICON_F, CLR_SILICON),
        ("Шар внутрішнього екранування живлення (Power Mesh)\nВбудовані розподілені розв'язувальні конденсатори (Decoupling Caps)\nдля згладжування імпульсів динамічного струму ядра", CLR_CORE_F, CLR_CORE),
        ("Матриця фотодіодів та датчиків світла\nФіксація декапсуляції корпусу кислотою та імпульсів LFI-лазера.\nМиттєве апаратне занулення (Zeroization) ключів", CLR_FAULT_F, CLR_FAULT),
        ("Захищене процесорне ядро та криптоприскорювач\nПодвійне виконання в ногу (Dual-Core Lockstep), внутрішній RC-генератор\nіз рандомізацією такту (Jitter), маскована логіка", CLR_SAFE_F, CLR_SAFE),
    ]

    y_l = 105
    for title_txt, fill_c, strk_c in layers:
        p.append(fitbox(55, y_l, 420, 88, title_txt, size=11, fill=fill_c, stroke=strk_c, sw=1.3))
        y_l += 96

    # Права секція: Комплекс апаратних моніторів
    p.append(rect(510, 55, 490, 445, fill="#ffffff", stroke=CLR_SAFE, sw=1.5, rx=8))
    p.append(text(755, 80, "Апаратні сенсори та генератори безпеки", size=13, color=CLR_SAFE, bold=True))

    monitors = [
        ("Швидкодіючий аналоговий детектор збоїв (Glitch / Brown-out Detector)",
         "• Моніторинг швидкості спаду напруги dV/dt (компаратор із порогом < 5 нс).\n• Моніторинг виходу напруги за допустиме вікно (Under/Over-voltage).\n• Реакція: примусовий скид (Hardware Reset) або очищення RAM.",
         CLR_CORE_F, CLR_CORE),

        ("Внутрішній тактовий генератор із джитуванням (Clock Jittering)",
         "• Відмова від зовнішнього кварцу (неможливо перехопити такт на ніжці MCU).\n• Внутрішній Ring Oscillator із випадковою модуляцією частоти (PRNG Jitter).\n• Десинхронізація осцилограм для повного зриву атак DPA/CPA.",
         CLR_WARN_F, CLR_WARN),

        ("Апаратний механізм екстреного занулення (Tamper Wipe & Zeroization)",
         "• Активація за 1 такт при спрацюванні активного екрана або світлового сенсора.\n• Скидання ключів шифрування в батарейній пам'яті BBRAM та регістрах.\n• Блокування шин пам'яті та переходів JTAG/SWD у режим повної ізоляції.",
         CLR_SAFE_F, CLR_SAFE),
    ]

    y_m = 105
    for mon_title, mon_desc, fill_c, strk_c in monitors:
        p.append(rect(525, y_m, 460, 118, fill=fill_c, stroke=strk_c, sw=1.2, rx=6))
        p.append(text(755, y_m + 20, mon_title, size=11, color=strk_c, bold=True))
        p.append(fitbox(535, y_m + 32, 440, 80, mon_desc, size=11, fill="#ffffff", stroke=LINE, sw=0.8))
        y_m += 128

    return render(os.path.join(OUT, "hardware-countermeasures-die-protection.svg"), W, H, *p)


# ── 4. Програмний конвеєр захисту від збоїв ──────────────────────────
def fig_software_fault_pipeline():
    W, H = 1040, 520
    p = []

    p.append(text(W / 2, 28, "Програмна стійкість: захист логіки переходів від ін'єкції збоїв", size=16, color=INK, bold=True))

    steps = [
        (130, "1. Багатозначні токени",
         "Відмова від 0/1:\nSECURE_TRUE  = 0x55AA55AA\nSECURE_FALSE = 0xAA55AA55\nДистанція Геммінґа = 32 біти.\nОдиночний збій не підробить стан.",
         CLR_CORE_F, CLR_CORE),

        (380, "2. Крокові канарейки",
         "Control Flow Integrity:\nІніціалізація canary = 0x1337.\nКожен крок: canary ^= STEP_ID.\nНа виході: canary == FINAL_HASH.\nПропуск інструкції зламає чек.",
         CLR_WARN_F, CLR_WARN),

        (640, "3. Надлишкова верифікація",
         "Dual/Triple Checking:\nДві незалежні функції перевірки.\nПорівняння підпису з оригіналом,\nпотім оригіналу з підписом.\nВипадкові затримки (Software Jitter).",
         CLR_SILICON_F, CLR_SILICON),

        (900, "4. Панічна пастка",
         "Fault Detection Trap:\nБудь-яка невідповідність стану\nведе не у гілку 'else', а в\nнезворотний panic_trap():\nзанулення ключів і HardFault.",
         CLR_FAULT_F, CLR_FAULT),
    ]

    for cx, stitle, sdesc, fill_c, strk_c in steps:
        p.append(rect(cx - 115, 60, 230, 390, fill="#ffffff", stroke=strk_c, sw=1.5, rx=8))
        p.append(text(cx, 86, stitle, size=12, color=strk_c, bold=True))
        p.append(fitbox(cx - 105, 105, 210, 330, sdesc, size=11, fill=fill_c, stroke=strk_c, sw=1.0))

    # Стрілки між етапами
    p.append(arrow(245, 255, 265, 255, color=LINE, sw=2.0))
    p.append(arrow(495, 255, 525, 255, color=LINE, sw=2.0))
    p.append(arrow(755, 255, 785, 255, color=LINE, sw=2.0))

    # Нижній банер результату
    p.append(rect(50, 460, 940, 45, fill=CLR_SAFE_F, stroke=CLR_SAFE, sw=1.5, rx=6))
    p.append(text(W / 2, 488, "Результат: успішна атака вимагає одночасного точного збою в 32 бітах даних та 4 циклах програми", size=12, color=CLR_SAFE, bold=True))

    return render(os.path.join(OUT, "fault-resistant-software-pipeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_glitch_mechanisms()
    fig_side_channel_analysis()
    fig_hardware_die_protection()
    fig_software_fault_pipeline()
    print("Усі 4 фігури успішно згенеровано.")
