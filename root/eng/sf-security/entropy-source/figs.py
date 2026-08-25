# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

PURPLE = "#7c3aed"
CYAN = "#0891b2"
AMBER = "#d97706"


# ══════════════════════════════════════════════════════════════════════════════
# 1. trng-pipeline.svg — Архітектура апаратного TRNG
# ══════════════════════════════════════════════════════════════════════════════
def fig_trng_pipeline():
    W, H = 840, 240
    p = []

    # Заголовок / фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#fbfcfd", stroke="#d1d5db", sw=1.2, rx=8))

    # Блоки конвеєра
    # 1. Фізичний шум
    b1, w1, h1 = textbox(95, 75, "Фізичне джерело\n(шум резистора,\nджиттер RO, лавина)", size=11, bold=True,
                         color=POS, fill="#fdf2f2", stroke=POS, sw=1.6, min_w=140)
    p.append(b1)

    # Стрілка 1
    p.append(arrow(170, 75, 205, 75, color=INK, sw=1.8))
    p.append(text(187, 60, "аналог", size=9, color=MUTED))

    # 2. Підсилювач / Оцифровщик
    b2, w2, h2 = textbox(275, 75, "Підсилювач та\nдискретизатор\n(АЦП / компаратор)", size=11, bold=True,
                         color=NEG, fill="#eff6ff", stroke=NEG, sw=1.6, min_w=130)
    p.append(b2)

    # Стрілка 2
    p.append(arrow(345, 75, 380, 75, color=INK, sw=1.8))
    p.append(text(362, 60, "сирі біти", size=9, color=MUTED))

    # 3. Онлайнові тести здоров'я
    b3, w3, h3 = textbox(455, 75, "Онлайн-тести SP 800-90B\n(RCT — залипання,\nAPT — баланс частот)", size=11, bold=True,
                         color=AMBER, fill="#fffbeb", stroke=AMBER, sw=1.6, min_w=140)
    p.append(b3)

    # Відгалуження на Аварію
    p.append(arrow(455, 115, 455, 160, color=POS, sw=1.5))
    err_box, ew, eh = textbox(455, 185, "Аварія: зупинка\nта тривога (Alarm)", size=10, bold=True,
                              color=POS, fill="#fee2e2", stroke=POS, sw=1.4, min_w=120)
    p.append(err_box)

    # Стрілка 3
    p.append(arrow(530, 75, 565, 75, color=INK, sw=1.8))
    p.append(text(547, 60, "перевірено", size=9, color=MUTED))

    # 4. Кондиціонування / Екстрактор
    b4, w4, h4 = textbox(635, 75, "Кондиціонування\n(фон Нейман, SHA-256,\nToeplitz matrix)", size=11, bold=True,
                         color=PURPLE, fill="#f5f3ff", stroke=PURPLE, sw=1.6, min_w=130)
    p.append(b4)

    # Стрілка 4
    p.append(arrow(705, 75, 735, 75, color=INK, sw=1.8))
    p.append(text(720, 60, "H_∞ ≈ 1", size=9, color=FIELD, bold=True))

    # 5. CSPRNG Seed
    b5, w5, h5 = textbox(775, 75, "CSPRNG\nSeed", size=11, bold=True,
                         color=FIELD, fill="#f0fdf4", stroke=FIELD, sw=1.6, min_w=65)
    p.append(b5)

    # Нижня анотація рівнів ентропії
    p.append(text(187, 135, "Мін-ентропія: H_∞ < 1 біт/символ", size=10, color=MUTED, anchor="start"))
    p.append(text(580, 135, "Мін-ентропія: H_∞ = 1.0 (повна)", size=10, color=FIELD, anchor="start", bold=True))

    render(os.path.join(OUT, "trng-pipeline.svg"), W, H, *p,
           title="Архітектура апаратного TRNG від фізичного шуму до повного зерна")


# ══════════════════════════════════════════════════════════════════════════════
# 2. physical-entropy-mechanisms.svg — 4 фізичні механізми
# ══════════════════════════════════════════════════════════════════════════════
def fig_physical_mechanisms():
    W, H = 840, 360
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#fbfcfd", stroke="#d1d5db", sw=1.2, rx=8))

    # Заголовок
    p.append(text(W / 2, 36, "Чотири фізичні джерела непередбачуваності в кремнії", size=14, bold=True, color=INK))

    # 4 квадранти
    # Квадрант 1: Тепловий шум Джонсона-Найквіста (верхній лівий)
    q1 = fitbox(25, 60, 385, 130,
                "1. Тепловий шум Джонсона—Найквіста\n"
                "• Хаотичний броунівський рух електронів у резисторі\n"
                "• Білий спектр, напруга V_n² = 4·k_B·T·R·Δf\n"
                "• Працює завжди, не залежить від струму",
                size=11, bold=False, color=INK, fill="#fef2f2", stroke=POS, sw=1.5)
    p.append(q1)

    # Квадрант 2: Джиттер кільцевих генераторів (верхній правий)
    q2 = fitbox(430, 60, 385, 130,
                "2. Джиттер кільцевих генераторів (RO)\n"
                "• Непарна кількість інверторів у замкненій петлі\n"
                "• Фазовий шум накопичується на кожному фронті\n"
                "• Відлік швидкого RO повільнішим тактом дає випадковий біт",
                size=11, bold=False, color=INK, fill="#eff6ff", stroke=NEG, sw=1.5)
    p.append(q2)

    # Квадрант 3: Метастабільність тригерів (нижній лівий)
    q3 = fitbox(25, 205, 385, 130,
                "3. Метастабільність бістабільних комірок\n"
                "• Тригер виводиться на вістря рівноваги (V_in ≈ V_DD/2)\n"
                "• Найменший тепловий флуктуаційний поштовх скочує в 0 чи 1\n"
                "• Компактна цифрова реалізація всередині FPGA / ASIC",
                size=11, bold=False, color=INK, fill="#f5f3ff", stroke=PURPLE, sw=1.5)
    p.append(q3)

    # Квадрант 4: Лавинний пробій p-n переходу (нижній правий)
    q4 = fitbox(430, 205, 385, 130,
                "4. Лавинний та зенерівський пробій діода\n"
                "• Зворотне зміщення p-n переходу вище напруги пробою\n"
                "• Квантова ударна іонізація породжує мікроімпульси струму\n"
                "• Велика амплітуда шуму, висока швидкість генерації бітів",
                size=11, bold=False, color=INK, fill="#fffbeb", stroke=AMBER, sw=1.5)
    p.append(q4)

    render(os.path.join(OUT, "physical-entropy-mechanisms.svg"), W, H, *p,
           title="Фізичні механізми генерації ентропії в апаратних TRNG")


# ══════════════════════════════════════════════════════════════════════════════
# 3. von-neumann-unbiasing.svg — Алгоритм Джона фон Неймана
# ══════════════════════════════════════════════════════════════════════════════
def fig_von_neumann():
    W, H = 820, 280
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#fbfcfd", stroke="#d1d5db", sw=1.2, rx=8))

    p.append(text(W / 2, 34, "Коректор Джона фон Неймана: усунення асиметрії пари бітів", size=13, bold=True, color=INK))

    # Вхідний потік
    in_box, iw, ih = textbox(110, 120, "Сирий потік бітів\nз асиметрією:\nP(1) = p ≠ 0.5\nP(0) = 1 − p",
                             size=11, bold=True, color=INK, fill="#f3f4f6", stroke="#9ca3af", sw=1.5, min_w=140)
    p.append(in_box)

    # Стрілка на розбиття пар
    p.append(arrow(190, 120, 240, 120, color=INK, sw=1.8))
    p.append(text(215, 105, "пари (b₁, b₂)", size=10, color=MUTED))

    # Таблиця / Розгалуження пар
    # Пара 01 -> 0
    p.append(rect(250, 60, 130, 36, fill="#ecfdf5", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(315, 82, "01  →  Вихід «0»", size=11, bold=True, color=FIELD))
    p.append(text(460, 82, "Ймовірність: (1 − p) · p", size=11, color=INK, anchor="start"))

    # Пара 10 -> 1
    p.append(rect(250, 105, 130, 36, fill="#ecfdf5", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(315, 127, "10  →  Вихід «1»", size=11, bold=True, color=FIELD))
    p.append(text(460, 127, "Ймовірність: p · (1 − p)", size=11, color=INK, anchor="start"))

    # Пара 00 -> drop
    p.append(rect(250, 150, 130, 36, fill="#fef2f2", stroke=POS, sw=1.5, rx=4))
    p.append(text(315, 172, "00  →  Відкинути", size=11, bold=True, color=POS))
    p.append(text(460, 172, "Ймовірність: (1 − p)²", size=11, color=MUTED, anchor="start"))

    # Пара 11 -> drop
    p.append(rect(250, 195, 130, 36, fill="#fef2f2", stroke=POS, sw=1.5, rx=4))
    p.append(text(315, 217, "11  →  Відкинути", size=11, bold=True, color=POS))
    p.append(text(460, 217, "Ймовірність: p²", size=11, color=MUTED, anchor="start"))

    # Стрілка до висновку
    p.append(arrow(620, 105, 660, 105, color=FIELD, sw=1.8))

    # Висновок: ідеальний біт
    out_box, ow, oh = textbox(730, 105, "Ідеальний біт:\nP(0) = P(1) = ½\nПропускна здатність:\n≤ 25% від сирої",
                              size=11, bold=True, color=FIELD, fill="#f0fdf4", stroke=FIELD, sw=1.6, min_w=125)
    p.append(out_box)

    p.append(text(W / 2, 255, "P(01) = P(10) гарантує рівномірність для незалежних бітів, ціна — скидання однакових пар", size=10, italic=True, color=MUTED))

    render(os.path.join(OUT, "von-neumann-unbiasing.svg"), W, H, *p,
           title="Усунення зміщення методом фон Неймана")


# ══════════════════════════════════════════════════════════════════════════════
# 4. linux-entropy-flow.svg — Пул ентропії ядра Linux та ChaCha20
# ══════════════════════════════════════════════════════════════════════════════
def fig_linux_entropy():
    W, H = 840, 340
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#fbfcfd", stroke="#d1d5db", sw=1.2, rx=8))

    p.append(text(W / 2, 34, "Потік ентропії в ядрі Linux (ChaCha20 CRNG)", size=13, bold=True, color=INK))

    # Вхідні джерела (лівий стовпчик)
    s1, _, _ = textbox(110, 75, "Таймінги переривань (IRQ)\nта дискових операцій", size=10, bold=False, color=INK, fill="#f3f4f6", stroke="#9ca3af", min_w=160)
    s2, _, _ = textbox(110, 125, "Ввід користувача\n(клавіатура, миша, тачпад)", size=10, bold=False, color=INK, fill="#f3f4f6", stroke="#9ca3af", min_w=160)
    s3, _, _ = textbox(110, 175, "Апаратний CPU джиттер\nта RDRAND / RDSEED / TPM", size=10, bold=False, color=INK, fill="#f3f4f6", stroke="#9ca3af", min_w=160)
    p.extend([s1, s2, s3])

    # Зведення вхідних стрілок у Fast Pool
    p.append(arrow(200, 75, 250, 125, color=INK, sw=1.5))
    p.append(arrow(200, 125, 250, 125, color=INK, sw=1.5))
    p.append(arrow(200, 175, 250, 125, color=INK, sw=1.5))

    # Первинний накопичувач / Fast Pool
    fp, _, _ = textbox(320, 125, "Швидкий пул (Fast Pool)\nBLAKE2s хешування\nОцінка ентропії (біти)",
                       size=11, bold=True, color=NEG, fill="#eff6ff", stroke=NEG, sw=1.6, min_w=130)
    p.append(fp)

    # Стрілка ініціалізації
    p.append(arrow(395, 125, 435, 125, color=INK, sw=1.8))
    p.append(text(415, 110, "256 бітів", size=9, color=MUTED))

    # Головний CRNG (ChaCha20)
    crng, _, _ = textbox(525, 125, "Головний CRNG\n(ChaCha20 стан)\ncrng_ready() = true\nFast Key Erasure",
                         size=11, bold=True, color=PURPLE, fill="#f5f3ff", stroke=PURPLE, sw=1.8, min_w=150)
    p.append(crng)

    # Вихідні стрілки до інтерфейсів простору користувача
    p.append(arrow(610, 110, 660, 75, color=FIELD, sw=1.8))
    p.append(arrow(610, 125, 660, 125, color=FIELD, sw=1.8))
    p.append(arrow(610, 140, 660, 175, color=FIELD, sw=1.8))

    # Інтерфейси простору користувача (правий стовпчик)
    u1, _, _ = textbox(735, 75, "getrandom(2)\nблокує до crng_ready", size=10, bold=True, color=FIELD, fill="#f0fdf4", stroke=FIELD, min_w=135)
    u2, _, _ = textbox(735, 125, "getentropy(3)\nбезпечний виклик libc", size=10, bold=True, color=FIELD, fill="#f0fdf4", stroke=FIELD, min_w=135)
    u3, _, _ = textbox(735, 175, "/dev/urandom\n/dev/random (Linux 5.6+)", size=10, bold=True, color=FIELD, fill="#f0fdf4", stroke=FIELD, min_w=135)
    p.extend([u1, u2, u3])

    # Нижній статус: Рівні готовності
    stat_box, _, _ = textbox(420, 265, "Стани crng_init: 0 (неініціалізовано) → 1 (перші 64 біти) → 2 (повна готовність, crng_ready)",
                             size=11, bold=False, color=INK, fill="#fffbeb", stroke=AMBER, sw=1.4, min_w=680)
    p.append(stat_box)

    render(os.path.join(OUT, "linux-entropy-flow.svg"), W, H, *p,
           title="Архітектура збору ентропії та генерації випадковості в ядрі Linux")


if __name__ == "__main__":
    fig_trng_pipeline()
    fig_physical_mechanisms()
    fig_von_neumann()
    fig_linux_entropy()
    print("Усі 4 фігури для entropy-source згенеровано успішно.")
