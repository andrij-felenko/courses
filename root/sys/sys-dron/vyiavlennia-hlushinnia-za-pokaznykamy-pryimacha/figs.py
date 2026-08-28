# -*- coding: utf-8 -*-
"""Генератор векторних діаграм (SVG) для теми:
«Виявлення глушіння за показниками приймача»
"""
import sys, os

# Шлях до svgkit у scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_front_end_agc_loop():
    """Фігура 1: Структурна схема радіотракту GNSS та контур автоматичного регулювання підсилення (АРП / AGC)."""
    w, h = 960, 520
    frags = []

    # Тло
    frags.append(rect(15, 15, 930, 490, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Заголовок фігури
    frags.append(text(480, 42, "Радіочастотний тракт GNSS-приймача та контур автоматичного регулювання підсилення (АРП / AGC)", size=15, bold=True, color="#0f172a"))

    # ── Блок 1: Вхідна антена та аналоговий RF тракт ──────────────────────────
    # Антена
    frags.append(rect(35, 90, 80, 50, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=4))
    frags.append(text(75, 112, "GNSS Антена", size=11, bold=True, color="#1e293b"))
    frags.append(text(75, 128, "RHCP (L1/L2)", size=10, color="#64748b"))

    # Сигнал стрілка від антени до LNA
    frags.append(line(115, 115, 145, 115, color="#2563eb", sw=2))

    # Первинний LNA
    frags.append(rect(145, 90, 75, 50, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=4))
    frags.append(text(182, 112, "LNA", size=12, bold=True, color="#1e40af"))
    frags.append(text(182, 128, "Gain +26 dB", size=9, color="#1d4ed8"))

    # Стрілка від LNA до SAW
    frags.append(line(220, 115, 250, 115, color="#2563eb", sw=2))

    # Смуговий фільтр SAW
    frags.append(rect(250, 90, 75, 50, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    frags.append(text(287, 112, "SAW / BAW", size=11, bold=True, color="#92400e"))
    frags.append(text(287, 128, "Фільтр L1", size=10, color="#b45309"))

    # Стрілка від SAW до Змішувача
    frags.append(line(325, 115, 355, 115, color="#2563eb", sw=2))

    # Змішувач (Mixer) + Гетеродин (LO)
    frags.append(circle(375, 115, 20, fill="#f1f5f9", stroke="#0f172a", sw=1.5))
    frags.append(text(375, 120, "⨂", size=16, bold=True, color="#0f172a"))
    frags.append(line(375, 160, 375, 135, color="#475569", sw=1.5))
    frags.append(rect(345, 160, 60, 28, fill="#f1f5f9", stroke="#64748b", sw=1.2, rx=3))
    frags.append(text(375, 178, "LO Синт.", size=10, bold=True, color="#334155"))

    # Стрілка від змішувача до VGA
    frags.append(line(395, 115, 435, 115, color="#2563eb", sw=2))
    frags.append(text(415, 105, "IF", size=10, bold=True, color="#475569"))

    # Підсилювач зі змінним підсиленням (VGA)
    frags.append(rect(435, 85, 95, 60, fill="#fee2e2", stroke="#dc2626", sw=1.8, rx=4))
    frags.append(text(482, 110, "VGA (АРП)", size=12, bold=True, color="#991b1b"))
    frags.append(text(482, 128, "Змінне Gain", size=10, color="#b91c1c"))

    # Стрілка від VGA до АЦП
    frags.append(line(530, 115, 570, 115, color="#2563eb", sw=2))

    # Квантування в АЦП (ADC)
    frags.append(rect(570, 85, 95, 60, fill="#f3e8ff", stroke="#7e22ce", sw=1.5, rx=4))
    frags.append(text(617, 110, "АЦП (ADC)", size=12, bold=True, color="#6b21a8"))
    frags.append(text(617, 128, "2/3-bit I & Q", size=10, color="#7e22ce"))

    # Стрілка від АЦП до DSP
    frags.append(line(665, 115, 715, 115, color="#2563eb", sw=2))

    # Цифровий сигнальний процесор (DSP & Корелятори)
    frags.append(rect(715, 75, 210, 140, fill="#ecfdf5", stroke="#059669", sw=1.5, rx=6))
    frags.append(text(820, 100, "Baseband DSP & Корелятори", size=12, bold=True, color="#065f46"))
    frags.append(text(820, 125, "• Стеження за кодом (DLL)", size=10, color="#047857"))
    frags.append(text(820, 145, "• Стеження за фазою (PLL)", size=10, color="#047857"))
    frags.append(text(820, 165, "• Оцінка C/N0 та детекція зриву", size=10, color="#047857"))
    frags.append(text(820, 195, "Вихід: C/N0, Doppler, Псевдодальності", size=9, bold=True, color="#0f766e"))

    # ── Петля зворотного зв'язку АРП (AGC Control Loop) ───────────────────────
    # Відбір відліків після АЦП
    frags.append(line(630, 145, 630, 200, color="#dc2626", sw=1.8))
    frags.append(circle(630, 145, 3, fill="#dc2626"))

    # Блок детектора потужності АЦП
    frags.append(rect(555, 200, 150, 48, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=4))
    frags.append(text(630, 220, "Оцінювач потужності", size=11, bold=True, color="#991b1b"))
    frags.append(text(630, 236, "Дисперсія відліків I/Q", size=9, color="#b91c1c"))

    # Стрілка від оцінювача до петльового фільтра АРП
    frags.append(line(555, 224, 505, 224, color="#dc2626", sw=1.8))

    # Петльовий цифровий фільтр / Інтегратор АРП
    frags.append(rect(395, 200, 110, 48, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=4))
    frags.append(text(450, 220, "Петльовий фільтр", size=11, bold=True, color="#991b1b"))
    frags.append(text(450, 236, "Інтегратор АРП", size=9, color="#b91c1c"))

    # Зворотний зв'язок на VGA
    frags.append(line(450, 200, 450, 145, color="#dc2626", sw=2))
    frags.append(text(418, 172, "Керування Gain", size=9, bold=True, color="#dc2626"))

    # Відвід значення AGC у діагностичний регістр
    frags.append(line(450, 248, 450, 280, color="#7c3aed", sw=1.5))
    frags.append(rect(330, 280, 240, 36, fill="#f5f3ff", stroke="#7c3aed", sw=1.5, rx=4))
    frags.append(text(450, 296, "Регістр UBX-MON-RF (agcCnt)", size=11, bold=True, color="#5b21b6"))
    frags.append(text(450, 310, "AGC Monitor Value (0...8191)", size=9, color="#6d28d9"))

    # ── Нижні порівняльні панелі: Норма vs РЕБ ────────────────────────────────
    # Ліва панель: Нормальний ефір
    frags.append(rect(35, 335, 430, 155, fill="#ffffff", stroke="#22c55e", sw=1.5, rx=6))
    frags.append(rect(35, 335, 430, 26, fill="#f0fdf4", stroke="#22c55e", sw=1, rx=6))
    frags.append(text(250, 352, "Нормальний стан (Чистий ефір / Clean RF)", size=12, bold=True, color="#15803d"))
    frags.append(text(50, 380, "• Вхідна потужність: P_in ≈ -111 dBm (тільки фоновий тепловий шум)", size=10, color="#166534", anchor="start"))
    frags.append(text(50, 402, "• Підсилення VGA: максимальне (Gain 100%, agcCnt ≈ 7000...8191)", size=10, color="#166534", anchor="start"))
    frags.append(text(50, 424, "• Квантування АЦП: оптимальне співвідношення бітів Знаку/Величини", size=10, color="#166534", anchor="start"))
    frags.append(text(50, 446, "• C/N0 супутників: 40...48 dB-Hz, стабільне супроводження коду й фази", size=10, color="#166534", anchor="start"))
    frags.append(text(50, 468, "• Статус РЕБ: jamInd < 30, jammingState = OK (загрози немає)", size=10, bold=True, color="#15803d", anchor="start"))

    # Права панель: Дія завади РЕБ
    frags.append(rect(495, 335, 430, 155, fill="#ffffff", stroke="#ef4444", sw=1.5, rx=6))
    frags.append(rect(495, 335, 430, 26, fill="#fef2f2", stroke="#ef4444", sw=1, rx=6))
    frags.append(text(710, 352, "Дія РЕБ (Широкосмугова або тональна завада)", size=12, bold=True, color="#b91c1c"))
    frags.append(text(510, 380, "• Вхідна потужність: P_in зростає до -80...-50 dBm (+30...+60 dB)", size=10, color="#991b1b", anchor="start"))
    frags.append(text(510, 402, "• Підсилення VGA: петля АРП миттєво скидає Gain (agcCnt < 1000)", size=10, color="#991b1b", anchor="start"))
    frags.append(text(510, 424, "• Наслідок: сигнал супутника тоне в заваді нижче шуму квантування", size=10, color="#991b1b", anchor="start"))
    frags.append(text(510, 446, "• C/N0 супутників: синхронний обвал до < 25 dB-Hz, зрив PLL/DLL", size=10, color="#991b1b", anchor="start"))
    frags.append(text(510, 468, "• Статус РЕБ: jamInd > 180, jammingState = CRITICAL (втрата фіксу)", size=10, bold=True, color="#b91c1c", anchor="start"))

    render(os.path.join(OUT_DIR, "gnss-front-end-agc-loop.svg"), w, h, *frags)


def fig_jamming_metrics_timeline():
    """Фігура 2: Динаміка показників GNSS-приймача при вході в зону радіоелектронного придушення (РЕБ)."""
    w, h = 960, 520
    frags = []

    # Тло
    frags.append(rect(15, 15, 930, 490, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))

    # Заголовок
    frags.append(text(480, 40, "Динаміка внутрішніх метрик приймача при вході в зону дії РЕБ (Jamming Profile)", size=15, bold=True, color="#0f172a"))

    # Верхні заголовки фаз над графіками (без перекриття з нижніми блоками)
    frags.append(rect(120, 60, 190, 24, fill="#f0fdf4", stroke="#86efac", sw=1, rx=3))
    frags.append(text(215, 76, "1. Чистий ефір (Clean)", size=11, bold=True, color="#166534"))

    frags.append(rect(310, 60, 150, 24, fill="#fffbeb", stroke="#fde68a", sw=1, rx=3))
    frags.append(text(385, 76, "2. Вхід у РЕБ (Onset)", size=11, bold=True, color="#b45309"))

    frags.append(rect(460, 60, 240, 24, fill="#fef2f2", stroke="#fca5a5", sw=1, rx=3))
    frags.append(text(580, 76, "3. Критичне глушіння (Severe)", size=11, bold=True, color="#991b1b"))

    frags.append(rect(700, 60, 180, 24, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=3))
    frags.append(text(790, 76, "4. Вихід / Відновлення", size=11, bold=True, color="#475569"))

    # Розділові вертикальні лінії між фазами
    frags.append(line(310, 85, 310, 410, color="#e2e8f0", sw=1.5, dash="4,3"))
    frags.append(line(460, 85, 460, 410, color="#e2e8f0", sw=1.5, dash="4,3"))
    frags.append(line(700, 85, 700, 410, color="#e2e8f0", sw=1.5, dash="4,3"))

    # ── Графік 1: Потужність завади на антені ──────────────────────────────────
    frags.append(line(120, 160, 880, 160, color="#94a3b8", sw=1))
    frags.append(text(110, 115, "Потужність завади", size=10, bold=True, color="#1e293b", anchor="end"))
    frags.append(text(110, 130, "P_rf (dBm)", size=9, color="#64748b", anchor="end"))
    frags.append(text(110, 158, "-110", size=9, color="#94a3b8", anchor="end"))
    frags.append(text(110, 105, "-60", size=9, color="#94a3b8", anchor="end"))

    # Крива потужності завади (червона)
    p_rf = "M 120,158 L 310,158 C 360,158 400,105 460,105 L 700,105 C 750,105 800,158 880,158"
    frags.append(f'<path d="{p_rf}" fill="none" stroke="#dc2626" stroke-width="2.5"/>')

    # ── Графік 2: AGC Monitor Value (Підсилення АРП) ──────────────────────────
    frags.append(line(120, 250, 880, 250, color="#94a3b8", sw=1))
    frags.append(text(110, 205, "АРП (AGC Gain)", size=10, bold=True, color="#1e293b", anchor="end"))
    frags.append(text(110, 220, "agcCnt (0..8191)", size=9, color="#64748b", anchor="end"))
    frags.append(text(110, 248, "500", size=9, color="#94a3b8", anchor="end"))
    frags.append(text(110, 195, "7500", size=9, color="#94a3b8", anchor="end"))

    # Крива AGC (фіолетова) - миттєво падає при появі завади
    p_agc = "M 120,195 L 310,195 C 330,195 360,248 460,248 L 700,248 C 740,248 780,195 880,195"
    frags.append(f'<path d="{p_agc}" fill="none" stroke="#7c3aed" stroke-width="2.5"/>')
    frags.append(text(390, 235, "Різкий спад Gain", size=9, bold=True, color="#6d28d9"))

    # ── Графік 3: C/N0 супутників (Синхронне просідання) ──────────────────────
    frags.append(line(120, 350, 880, 350, color="#94a3b8", sw=1))
    frags.append(text(110, 295, "Рівні C/N0 (dB-Hz)", size=10, bold=True, color="#1e293b", anchor="end"))
    frags.append(text(110, 310, "Супутники L1", size=9, color="#64748b", anchor="end"))
    frags.append(text(110, 348, "15", size=9, color="#94a3b8", anchor="end"))
    frags.append(text(110, 285, "45", size=9, color="#94a3b8", anchor="end"))

    # 4 супутники різного кольору - синхронне падіння
    # SV 1 (високий кут 70°)
    frags.append('<path d="M 120,285 L 310,285 C 360,288 430,345 460,348 L 700,348 C 740,348 800,285 880,285" fill="none" stroke="#0284c7" stroke-width="1.8"/>')
    # SV 2 (кут 50°)
    frags.append('<path d="M 120,295 L 310,295 C 355,298 420,348 460,350 L 700,350 C 745,350 810,295 880,295" fill="none" stroke="#16a34a" stroke-width="1.8"/>')
    # SV 3 (кут 30°)
    frags.append('<path d="M 120,305 L 310,305 C 350,310 410,350 460,350 L 700,350 C 750,350 820,305 880,305" fill="none" stroke="#f59e0b" stroke-width="1.8"/>')
    # SV 4 (кут 18°)
    frags.append('<path d="M 120,318 L 310,318 C 340,325 390,350 460,350 L 700,350 C 760,350 830,318 880,318" fill="none" stroke="#ec4899" stroke-width="1.8"/>')

    frags.append(text(580, 335, "Синхронний обвал C/N0 усіх SV (втрата супроводу)", size=9, bold=True, color="#b91c1c"))

    # ── Графік 4: Стан детектора РЕБ (Jamming State & EKF) ─────────────────────
    frags.append(text(110, 430, "Стан детектора", size=10, bold=True, color="#1e293b", anchor="end"))
    frags.append(text(110, 444, "FSM State", size=9, color="#64748b", anchor="end"))

    # Блоки станів автомата
    # 1. CLEAN (зелений)
    frags.append(rect(120, 420, 190, 30, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=3))
    frags.append(text(215, 439, "STATE_CLEAN (GNSS Fix OK)", size=10, bold=True, color="#15803d"))

    # 2. WARNING (жовтий)
    frags.append(rect(310, 420, 150, 30, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=3))
    frags.append(text(385, 439, "WARNING (ΔAGC Drop)", size=9, bold=True, color="#92400e"))

    # 3. CRITICAL / EKF REJECT (червоний)
    frags.append(rect(460, 420, 240, 30, fill="#fee2e2", stroke="#dc2626", sw=1.8, rx=3))
    frags.append(text(580, 435, "CRITICAL: РЕБ ВИЯВЛЕНО", size=10, bold=True, color="#991b1b"))
    frags.append(text(580, 446, "EKF відкидає GNSS → ІВБ Dead-Reckoning", size=9, bold=True, color="#b91c1c"))

    # 4. RECOVERY (синій)
    frags.append(rect(700, 420, 180, 30, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=3))
    frags.append(text(790, 439, "RECOVERY (Валідація фіксу)", size=9, bold=True, color="#0369a1"))

    # Горизонтальна вісь часу
    frags.append(line(120, 465, 880, 465, color="#475569", sw=1.5))
    frags.append(text(120, 480, "0 с", size=9, color="#64748b"))
    frags.append(text(310, 480, "15 с", size=9, color="#64748b"))
    frags.append(text(460, 480, "25 с", size=9, color="#64748b"))
    frags.append(text(700, 480, "45 с", size=9, color="#64748b"))
    frags.append(text(880, 480, "60 с", size=9, color="#64748b"))
    frags.append(text(500, 495, "Час польоту t (секунди)", size=11, bold=True, color="#334155"))

    render(os.path.join(OUT_DIR, "jamming-detection-metrics-timeline.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_front_end_agc_loop()
    fig_jamming_metrics_timeline()
    print("Фігури успішно згенеровано.")
