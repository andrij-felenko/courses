# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми «Глушіння GNSS: як це виглядає з боку приймача»."""

import os
import sys

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від теми: root/sys/sys-dron/hlushinnia-gnss)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    FONT, BG, INK, LINE, MUTED, POS, NEG, FIELD, FILL,
    text, mtext, rect, line, arrow, circle, textbox, fitbox, render
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_link_budget_vs_jamming():
    """Фігура 1: Енергетичний бюджет супутникового сигналу GNSS проти теплового шуму та завад."""
    w, h = 920, 500
    frags = []

    # Загальний контур
    frags.append(rect(15, 15, 890, 470, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))

    # Ліва частина: Шкала потужності (dBm)
    frags.append(rect(30, 35, 410, 435, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(235, 60, "Рівні потужності на вході антени (дБм)", size=13, bold=True, color=INK))

    # Вісь рівнів
    frags.append(line(75, 80, 75, 415, color=LINE, sw=1.8))
    frags.append(line(71, 90, 75, 80, color=LINE, sw=1.8))
    frags.append(line(79, 90, 75, 80, color=LINE, sw=1.8))

    # Відмітки на осі (рознесені без накладань)
    levels = [
        ("0 / -30 дБм", 95, "#b91c1c", "Ближня зона РЕБ (10–50 Вт, <1 км)"),
        ("-60 дБм", 145, "#ea580c", "Малопотужний глушник (100 мВт, 1 км)"),
        ("-90 дБм", 195, "#d97706", "Поріг зриву захоплення (J/S ≈ 30 дБ)"),
        ("-111 дБм", 245, "#2563eb", "Тепловий шум у смузі 2 МГц (k_B·T·B)"),
        ("-130 дБм", 295, "#16a34a", "Сигнал супутника GNSS на Землі"),
        ("-160 дБм", 345, "#475569", "Рівень сигналу на 1 Гц смуги"),
        ("-174 дБм/Гц", 390, "#64748b", "Густина теплового шуму N₀")
    ]

    for lbl, y_pos, col, desc in levels:
        frags.append(line(70, y_pos, 80, y_pos, color=col, sw=1.5))
        frags.append(text(65, y_pos + 4, lbl, size=10, bold=True, color=col, anchor="end"))
        frags.append(line(80, y_pos, 120, y_pos, color=col, sw=1, dash="2,2"))
        frags.append(rect(120, y_pos - 11, 305, 22, fill="#ffffff", stroke=col, sw=1, rx=4))
        frags.append(text(272, y_pos + 4, desc, size=10, color=col, bold=True))

    # Виділення зони внизу
    frags.append(rect(45, 425, 380, 30, fill="#dcfce7", stroke="#16a34a", sw=1.2, rx=4))
    frags.append(text(235, 444, "Сигнал супутника на 19 дБ нижчий за тепловий шум!", size=10.5, bold=True, color="#15803d"))

    # Права частина: Механізм виділення сигналу (DSSS) та вплив завади
    frags.append(rect(455, 35, 450, 435, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(680, 60, "Кореляційне підсилення (Processing Gain)", size=13, bold=True, color=INK))

    # Блок 1: Корелятор у чистих умовах
    frags.append(rect(470, 80, 420, 165, fill="#ffffff", stroke="#16a34a", sw=1.2, rx=6))
    frags.append(text(680, 102, "Чистий ефір: кореляція з PRN-кодом Голда", size=11, bold=True, color="#15803d"))

    # Графік кореляційного піка (чистий)
    frags.append(line(490, 205, 870, 205, color="#94a3b8", sw=1))
    frags.append(line(680, 125, 680, 205, color="#94a3b8", sw=1, dash="2,2"))
    frags.append(line(490, 200, 640, 200, color="#22c55e", sw=1.5))
    frags.append(line(640, 200, 680, 130, color="#16a34a", sw=2.5))
    frags.append(line(680, 130, 720, 200, color="#16a34a", sw=2.5))
    frags.append(line(720, 200, 870, 200, color="#22c55e", sw=1.5))
    frags.append(circle(680, 130, 4, fill="#16a34a", stroke=LINE, sw=1))
    frags.append(text(680, 120, "Гострий пік кореляції (C/N₀ ≈ 44 дБ-Гц)", size=10, bold=True, color="#15803d"))
    frags.append(text(680, 224, "Підсилення обробки G_p = 10·log₁₀(1023) ≈ 30.1 дБ", size=10, color=MUTED))

    # Блок 2: Корелятор під дією завади
    frags.append(rect(470, 260, 420, 195, fill="#ffffff", stroke="#dc2626", sw=1.2, rx=6))
    frags.append(text(680, 282, "Під дією завади (J/S > 35 дБ): Затоплення шумом", size=11, bold=True, color="#b91c1c"))

    # Графік завади
    frags.append(line(490, 395, 870, 395, color="#94a3b8", sw=1))
    noise_points = [
        (490, 365), (520, 350), (550, 370), (580, 345), (610, 365),
        (640, 340), (680, 335), (720, 350), (760, 360), (800, 345),
        (840, 365), (870, 355)
    ]
    for i in range(len(noise_points) - 1):
        x1, y1 = noise_points[i]
        x2, y2 = noise_points[i+1]
        frags.append(line(x1, y1, x2, y2, color="#ef4444", sw=1.8))

    frags.append(text(680, 325, "Кореляційний пік потонув у шумах завади", size=10, bold=True, color="#b91c1c"))
    frags.append(text(680, 415, "C/N₀ падає < 25 дБ-Гц → Зрив стеження DLL / PLL", size=10, bold=True, color="#991b1b"))
    frags.append(text(680, 435, "Насичення АЦП (ADC Clipping) та блокування АРП (AGC)", size=9.5, color=MUTED))

    return render(os.path.join(OUT_DIR, "gnss-link-budget-vs-jamming.svg"), w, h, *frags)


def fig_jamming_waveforms():
    """Фігура 2: Типи завад (Barrage, CW, Chirp, Pulsed) та їхні спектрограми."""
    w, h = 920, 480
    frags = []

    frags.append(rect(15, 15, 890, 450, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(460, 42, "Спектрально-часові профілі основних типів глушників GNSS", size=14, bold=True, color=INK))

    cards = [
        ("1. Загороджувальний шум (Barrage)", 35, 65, 410, 180, "#2563eb",
         "Широкосмуговий шум (20–50 МГц)\nРівномірно піднімає шумову полицю\nЗнижує C/N₀ усіх супутників одночасно\nВимагає значної потужності передавача"),

        ("2. Тональна завада (CW / Multi-Tone)", 475, 65, 410, 180, "#0891b2",
         "Вузькосмугова гармоніка на несучій L1/L2\nСтворює паразитний біт-сигнал у змішувачі\nЛегко фільтрується режекторними фільтрами\nВикликає перекіс у 2-бітному АЦП"),

        ("3. ЛЧМ / Чирп-глушник (Chirp / Swept)", 35, 265, 410, 180, "#dc2626",
         "Пилкоподібне сканування (10–50 мкс, 20 МГц)\nНайдешевший і наймасовіший тип глушника\nОбходить режекторні решітки та зриває DLL\nМиттєво перевантажує вхідний тракт і АЦП"),

        ("4. Імпульсна завада (Pulsed Jammer)", 475, 265, 410, 180, "#d97706",
         "Короткі надпотужні імпульси (1–100 мкс)\nВводить вхідний МШУ (LNA) у компресію\nБлокує часову константу петлі АРП (AGC)\nСпричиняє циклічні зриви фазового супроводу")
    ]

    for title, x, y, cw, ch, col, desc in cards:
        frags.append(rect(x, y, cw, ch, fill="#f8fafc", stroke=col, sw=1.2, rx=6))
        frags.append(rect(x + 10, y + 10, cw - 20, 26, fill=col, stroke=col, sw=1, rx=4))
        frags.append(text(x + cw / 2, y + 27, title, size=11, bold=True, color="#ffffff"))

        # Міні-спектрограма зліва (130x110)
        sx, sy, sw, sh = x + 15, y + 45, 130, 115
        frags.append(rect(sx, sy, sw, sh, fill="#0f172a", stroke="#334155", sw=1, rx=4))
        # Осі: t (праворуч), f (вгору)
        frags.append(line(sx + 15, sy + sh - 15, sx + sw - 10, sy + sh - 15, color="#64748b", sw=1))
        frags.append(line(sx + 15, sy + sh - 15, sx + 15, sy + 10, color="#64748b", sw=1))
        frags.append(text(sx + sw - 6, sy + sh - 10, "t", size=9.5, color="#94a3b8"))
        frags.append(text(sx + 8, sy + 16, "f", size=9.5, color="#94a3b8"))

        # Специфічний малюнок на спектрограмі
        if "Barrage" in title:
            frags.append(rect(sx + 20, sy + 20, sw - 35, sh - 40, fill="#3b82f6", stroke="#60a5fa", sw=1))
            frags.append(text(sx + sw / 2 + 5, sy + sh / 2, "Шум B > 20 МГц", size=9.5, bold=True, color="#ffffff"))
        elif "CW" in title:
            frags.append(line(sx + 18, sy + 50, sx + sw - 12, sy + 50, color="#22d3ee", sw=3))
            frags.append(text(sx + sw / 2 + 5, sy + 40, "f₀ (L1)", size=9.5, bold=True, color="#22d3ee"))
        elif "Chirp" in title:
            for k in range(3):
                lx1 = sx + 22 + k * 32
                ly1 = sy + sh - 20
                lx2 = sx + 46 + k * 32
                ly2 = sy + 22
                frags.append(line(lx1, ly1, lx2, ly2, color="#f87171", sw=2.2))
            frags.append(text(sx + sw / 2 + 5, sy + sh - 25, "df/dt ≈ const", size=9.5, bold=True, color="#fca5a5"))
        elif "Pulsed" in title:
            for k in range(3):
                px = sx + 30 + k * 32
                frags.append(rect(px, sy + 20, 10, sh - 40, fill="#fbbf24", stroke="#f59e0b", sw=1))
            frags.append(text(sx + sw / 2 + 5, sy + sh - 25, "P_peak імпульс", size=9.5, bold=True, color="#fef08a"))

        # Текстовий опис справа від спектрограми
        lines = desc.split("\n")
        for idx, ln in enumerate(lines):
            frags.append(text(x + 160, y + 66 + idx * 26, "• " + ln, size=10.5, color=INK, anchor="start"))

    return render(os.path.join(OUT_DIR, "jamming-waveforms-comparison.svg"), w, h, *frags)


def fig_ekf_jamming_response():
    """Фігура 3: Ланцюг деградації та реакція навігаційного фільтра EKF2/EKF3 на глушіння."""
    w, h = 940, 520
    frags = []

    frags.append(rect(15, 15, 910, 490, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(470, 42, "Ланцюг деградації: від ВЧ тракту до аварійних режимів автопілота", size=14, bold=True, color=INK))

    stages = [
        ("1. Вхідний ВЧ тракт", 35, 70, 195, 415, "#2563eb", [
            ("Антена GNSS", "Прийом L1/L2 сигналів"),
            ("МШУ (LNA)", "Компресія 1 дБ (P1dB)"),
            ("АРП (AGC)", "Зниження коеф. підсилення"),
            ("АЦП (1-2 біти)", "Кліпінг та насичення"),
            ("Наслідок:", "Падіння C/N₀ на 20–40 дБ")
        ]),
        ("2. Петлі супроводу", 260, 70, 195, 415, "#0891b2", [
            ("Корелятор", "Розмивання піка R(τ)"),
            ("Петля DLL", "Зрив кодового стеження"),
            ("Петля PLL/FLL", "Зрив фазового стеження"),
            ("Вимірювання", "Стрибки дисперсії σ_ρ²"),
            ("Наслідок:", "Loss of Lock, Cycle Slips")
        ]),
        ("3. Навігаційний фільтр EKF", 485, 70, 195, 415, "#d97706", [
            ("Інновація y_k", "y_k = z_k − h(x̂_k⁻)"),
            ("Chi-Square Gate", "y_kᵀ S_k⁻¹ y_k > Порогу"),
            ("GPS Glitch", "Відкидання супутників"),
            ("Timeout (1–2 с)", "Повне відключення GNSS"),
            ("Наслідок:", "Перехід у Dead Reckoning")
        ]),
        ("4. Автопілот і Failsafe", 710, 70, 195, 415, "#dc2626", [
            ("Чистий IMU", "Експоненційний дрейф ~t²"),
            ("Дрейф позиції", "100–500 м за 30–60 с"),
            ("Зміна режиму", "Втрата POSCTL / LOITER"),
            ("Аварійні заходи", "ALT_HOLD / LAND / FLOW"),
            ("Наслідок:", "Зрив автономної місії")
        ])
    ]

    for title, x, y, cw, ch, col, items in stages:
        frags.append(rect(x, y, cw, ch, fill="#f8fafc", stroke=col, sw=1.2, rx=6))
        frags.append(rect(x + 8, y + 8, cw - 16, 26, fill=col, stroke=col, sw=1, rx=4))
        frags.append(text(x + cw / 2, y + 25, title, size=11, bold=True, color="#ffffff"))

        # Елементи всередині стадії
        for idx, (sub_title, sub_desc) in enumerate(items):
            iy = y + 46 + idx * 72
            is_conseq = (idx == len(items) - 1)
            bg_col = "#fee2e2" if is_conseq else "#ffffff"
            st_col = "#dc2626" if is_conseq else "#cbd5e1"
            txt_col = "#991b1b" if is_conseq else INK

            frags.append(rect(x + 10, iy, cw - 20, 60, fill=bg_col, stroke=st_col, sw=1, rx=4))
            frags.append(text(x + cw / 2, iy + 22, sub_title, size=10.5, bold=True, color=txt_col))
            frags.append(text(x + cw / 2, iy + 44, sub_desc, size=9.5, color=MUTED if not is_conseq else "#b91c1c"))

    # Стрілки між колонками
    frags.append(arrow(233, 275, 256, 275, color=LINE, sw=2))
    frags.append(arrow(458, 275, 481, 275, color=LINE, sw=2))
    frags.append(arrow(683, 275, 706, 275, color=LINE, sw=2))

    return render(os.path.join(OUT_DIR, "ekf-jamming-response-pipeline.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_link_budget_vs_jamming()
    fig_jamming_waveforms()
    fig_ekf_jamming_response()
    print("Всі 3 фігури згенеровано успішно.")
