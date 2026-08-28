# -*- coding: utf-8 -*-
"""Генератор векторних діаграм (SVG) для теми:
«Бортовий комп'ютер (companion)»
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_dual_board_architecture():
    """Фігура 1: Апаратна архітектура двопроцесорного борту (FC + Companion SBC)."""
    w, h = 920, 500
    frags = []

    # Загальний фон полотна
    frags.append(rect(15, 15, 890, 470, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Заголовок
    frags.append(text(460, 42, "Апаратна архітектура двопроцесорного борту: FC (MCU) та Companion (SBC)", size=15, bold=True, color="#0f172a"))

    # ── Лівий блок: Політний контролер (FC) ──
    frags.append(rect(35, 65, 340, 310, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=6))
    frags.append(text(205, 90, "ПОЛІТНИЙ КОНТРОЛЕР (FC / MCU)", size=13, bold=True, color="#14532d"))
    frags.append(text(205, 108, "STM32H743 / F765 (Cortex-M7 @ 480 МГц)", size=10, color="#166534"))

    # Підблоки всередині FC
    frags.append(rect(50, 122, 310, 48, fill="#ffffff", stroke="#4ade80", sw=1.2, rx=4))
    frags.append(text(205, 142, "Контури жорсткого реального часу (Hard RTOS)", size=11, bold=True, color="#14532d"))
    frags.append(text(205, 158, "Rate PID (1–8 кГц) · Attitude (400 Гц) · DShot600", size=9.5, color="#334155"))

    frags.append(rect(50, 178, 310, 48, fill="#ffffff", stroke="#4ade80", sw=1.2, rx=4))
    frags.append(text(205, 198, "Оцінювач стану та навігація (EKF3)", size=11, bold=True, color="#14532d"))
    frags.append(text(205, 214, "IMU SPI 24 МГц · Baro · Mag · GNSS (100–400 Гц)", size=9.5, color="#334155"))

    frags.append(rect(50, 234, 310, 48, fill="#ffffff", stroke="#4ade80", sw=1.2, rx=4))
    frags.append(text(205, 254, "Апаратний монітор та Failsafe", size=11, bold=True, color="#14532d"))
    frags.append(text(205, 270, "Таймаут уставки Offboard/Guided · Hard-Watchdog", size=9.5, color="#dc2626"))

    frags.append(rect(50, 290, 310, 70, fill="#ffffff", stroke="#4ade80", sw=1.2, rx=4))
    frags.append(text(205, 308, "Апаратні інтерфейси зв'язку", size=11, bold=True, color="#14532d"))
    frags.append(text(205, 324, "UART (DMA) 921.6k–3.0M бод (MAVLink)", size=9.5, color="#2563eb"))
    frags.append(text(205, 340, "Ethernet PHY 100BASE-TX (micro-XRCE-DDS)", size=9.5, color="#2563eb"))
    frags.append(text(205, 354, "Лінія Hard-Reset Watchdog (GPIO до SBC)", size=9.5, color="#d97706"))

    # ── Правий блок: Бортовий комп'ютер (Companion SBC) ──
    frags.append(rect(545, 65, 340, 310, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=6))
    frags.append(text(715, 90, "БОРТОВИЙ КОМП'ЮТЕР (Companion SBC)", size=13, bold=True, color="#1e40af"))
    frags.append(text(715, 108, "Jetson Orin Nano / RPi CM4 (Linux / ROS 2)", size=10, color="#1e3a8a"))

    # Підблоки всередині SBC
    frags.append(rect(560, 122, 310, 48, fill="#ffffff", stroke="#60a5fa", sw=1.2, rx=4))
    frags.append(text(715, 142, "Сенсорне сприйняття та бачення (CV / SLAM)", size=11, bold=True, color="#1e3a8a"))
    frags.append(text(715, 158, "Visual Odometry (VIO) · LiDAR SLAM (15–30 Гц)", size=9.5, color="#334155"))

    frags.append(rect(560, 178, 310, 48, fill="#ffffff", stroke="#60a5fa", sw=1.2, rx=4))
    frags.append(text(715, 198, "Нейромережі та виявлення цілей (AI / ML)", size=11, bold=True, color="#1e3a8a"))
    frags.append(text(715, 214, "YOLOv8 / TensorRT · Трекінг (20–40 TOPS GPU)", size=9.5, color="#334155"))

    frags.append(rect(560, 234, 310, 48, fill="#ffffff", stroke="#60a5fa", sw=1.2, rx=4))
    frags.append(text(715, 254, "Планування траєкторій та місій", size=11, bold=True, color="#1e3a8a"))
    frags.append(text(715, 270, "3D Occupancy Grid · Обхід перешкод (10–20 Гц)", size=9.5, color="#334155"))

    frags.append(rect(560, 290, 310, 70, fill="#ffffff", stroke="#60a5fa", sw=1.2, rx=4))
    frags.append(text(715, 308, "Програмний міст зв'язку (Bridge)", size=11, bold=True, color="#1e3a8a"))
    frags.append(text(715, 324, "MAVROS / pymavlink / MAVSDK (UART)", size=9.5, color="#2563eb"))
    frags.append(text(715, 340, "micro-ROS Agent / FastDDS (Ethernet)", size=9.5, color="#2563eb"))
    frags.append(text(715, 354, "Daemon-сторож (скидання живлення при збої)", size=9.5, color="#d97706"))

    # ── Центральні зв'язки ──
    # UART шина
    frags.append(arrow(375, 305, 545, 305, color="#2563eb", sw=1.8))
    frags.append(arrow(545, 315, 375, 315, color="#2563eb", sw=1.8))
    frags.append(rect(390, 295, 140, 30, fill="#ffffff", stroke="#3b82f6", sw=1, rx=4))
    frags.append(text(460, 314, "UART 921.6k–3.0M", size=9.5, bold=True, color="#1e40af"))

    # Ethernet шина
    frags.append(arrow(375, 340, 545, 340, color="#059669", sw=1.8))
    frags.append(arrow(545, 348, 375, 348, color="#059669", sw=1.8))
    frags.append(rect(390, 332, 140, 26, fill="#ffffff", stroke="#10b981", sw=1, rx=4))
    frags.append(text(460, 349, "Ethernet 100BASE-TX", size=9.5, bold=True, color="#065f46"))

    # Лінія апаратного скидання (Watchdog Line)
    frags.append(arrow(375, 365, 545, 365, color="#d97706", sw=1.5))
    frags.append(text(460, 380, "SYS_RESET# / Power Gate", size=9, bold=True, color="#b45309"))

    # ── Нижній рівень: Ізоляція доменів живлення ──
    frags.append(rect(35, 395, 850, 75, fill="#fef2f2", stroke="#fca5a5", sw=1.5, rx=6))
    frags.append(text(125, 420, "ДОМЕНИ ЖИВЛЕННЯ", size=11, bold=True, color="#991b1b"))
    frags.append(text(125, 438, "Ізольовані DC-DC", size=9.5, color="#dc2626"))

    # Блок живлення FC
    frags.append(rect(220, 405, 300, 55, fill="#ffffff", stroke="#f87171", sw=1.2, rx=4))
    frags.append(text(370, 423, "DC-DC BEC 5.3V / 2.5A (Чистий домен FC)", size=10, bold=True, color="#7f1d1d"))
    frags.append(text(370, 439, "Фільтрація LDO, шум низький для IMU", size=9, color="#475569"))

    # Блок живлення SBC
    frags.append(rect(540, 405, 330, 55, fill="#ffffff", stroke="#f87171", sw=1.2, rx=4))
    frags.append(text(705, 423, "DC-DC 5V/5A або 12V/4A (Силовий домен SBC)", size=10, bold=True, color="#7f1d1d"))
    frags.append(text(705, 439, "Ізоляція сплесків струму GPU/CPU до 3.5–5.0 А", size=9, color="#475569"))

    render(os.path.join(OUT_DIR, "dual-board-architecture.svg"), w, h, *frags)


def fig_realtime_vs_soft_domains():
    """Фігура 2: Поділ Hard Real-Time та Soft Real-Time (часові шкали та дедлайни)."""
    w, h = 920, 480
    frags = []

    # Загальний фон
    frags.append(rect(15, 15, 890, 450, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Заголовок
    frags.append(text(460, 40, "Часовий детермінізм: Жорсткий (FC) проти М'якого (Companion) реального часу", size=15, bold=True, color="#0f172a"))

    # ── Ліва панель: Hard Real-Time на FC ──
    frags.append(rect(35, 60, 410, 390, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=6))
    frags.append(text(240, 85, "ЖОРСТКИЙ РЕАЛЬНИЙ ЧАС (Hard Real-Time: FC)", size=13, bold=True, color="#14532d"))
    frags.append(text(240, 102, "Строгий детермінізм, нульовий допуск до запізнень", size=10, color="#166534"))

    # Такт контуру
    frags.append(rect(50, 115, 380, 105, fill="#ffffff", stroke="#4ade80", sw=1.2, rx=4))
    frags.append(text(240, 134, "Контур кутової швидкості: T = 1.0 мс (1000 Гц)", size=11, bold=True, color="#14532d"))

    # Шкала такту
    frags.append(line(70, 175, 410, 175, color="#64748b", sw=1.5))
    frags.append(line(70, 165, 70, 185, color="#64748b", sw=2))
    frags.append(line(240, 165, 240, 185, color="#64748b", sw=2))
    frags.append(line(410, 165, 410, 185, color="#64748b", sw=2))
    frags.append(text(70, 198, "0.0 мс", size=9, color="#64748b"))
    frags.append(text(240, 198, "0.5 мс", size=9, color="#64748b"))
    frags.append(text(410, 198, "1.0 мс (Дедлайн)", size=9, bold=True, color="#dc2626"))

    # Робочий інтервал
    frags.append(rect(70, 160, 120, 16, fill="#22c55e", stroke="#15803d", sw=1, rx=2))
    frags.append(text(130, 153, "Обчислення: 0.35 мс", size=9.5, bold=True, color="#14532d"))
    frags.append(rect(190, 160, 220, 16, fill="#e2e8f0", stroke="#94a3b8", sw=1, rx=2))
    frags.append(text(300, 153, "Запас часу: 0.65 мс", size=9.5, color="#475569"))

    # Характеристики жорсткого контуру
    frags.append(rect(50, 230, 380, 205, fill="#ffffff", stroke="#4ade80", sw=1.2, rx=4))
    frags.append(text(240, 250, "ХАРАКТЕРИСТИКИ ТА НАСЛІДКИ ЗРИВУ:", size=11, bold=True, color="#14532d"))
    frags.append(text(65, 272, "• Джиттер виконання: менше 5 мікросекунд", size=9.5, color="#334155", anchor="start"))
    frags.append(text(65, 292, "• Найгірший час виконання (WCET) до 0.6 мс", size=9.5, color="#334155", anchor="start"))
    frags.append(text(65, 312, "• Апаратне виконання на Cortex-M7 (FPU, DMA)", size=9.5, color="#334155", anchor="start"))
    frags.append(text(65, 332, "• Пропуск 1–2 тактів: деградація фази контуру", size=9.5, color="#dc2626", anchor="start"))
    frags.append(text(65, 352, "• Пропуск понад 20 мс: розгойдування та зрив у штопор", size=9.5, color="#7f1d1d", bold=True, anchor="start"))
    frags.append(text(65, 372, "• Поведінка при збої: апаратний Watchdog 250 мс", size=9.5, color="#059669", anchor="start"))
    frags.append(text(65, 392, "• Статус: критично для виживання апарата", size=9.5, color="#14532d", bold=True, anchor="start"))
    frags.append(text(65, 412, "• Не залежить від стану та завантаження Linux", size=9.5, color="#2563eb", anchor="start"))

    # ── Права панель: Soft Real-Time на Companion ──
    frags.append(rect(475, 60, 410, 390, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=6))
    frags.append(text(680, 85, "М'ЯКИЙ РЕАЛЬНИЙ ЧАС (Soft Real-Time: SBC)", size=13, bold=True, color="#1e40af"))
    frags.append(text(680, 102, "Важкі обчислення, середня пропускна здатність", size=10, color="#1e3a8a"))

    # Такт контуру
    frags.append(rect(490, 115, 380, 105, fill="#ffffff", stroke="#60a5fa", sw=1.2, rx=4))
    frags.append(text(680, 134, "Контур планування: T = 33.3 мс (30 Гц)", size=11, bold=True, color="#1e3a8a"))

    # Шкала такту
    frags.append(line(510, 175, 850, 175, color="#64748b", sw=1.5))
    frags.append(line(510, 165, 510, 185, color="#64748b", sw=2))
    frags.append(line(680, 165, 680, 185, color="#64748b", sw=2))
    frags.append(line(850, 165, 850, 185, color="#64748b", sw=2))
    frags.append(text(510, 198, "0 мс", size=9, color="#64748b"))
    frags.append(text(680, 198, "33 мс (Ціль)", size=9, color="#64748b"))
    frags.append(text(850, 198, "100 мс (Затримка)", size=9, bold=True, color="#d97706"))

    # Робочий інтервал
    frags.append(rect(510, 160, 230, 16, fill="#3b82f6", stroke="#1d4ed8", sw=1, rx=2))
    frags.append(text(625, 153, "YOLOv8 + VIO + ROS 2: 25–45 мс", size=9.5, bold=True, color="#1e3a8a"))
    frags.append(rect(740, 160, 110, 16, fill="#fed7aa", stroke="#f97316", sw=1, rx=2))
    frags.append(text(795, 153, "джиттер ОС: 10–60 мс", size=9.5, color="#9a3412"))

    # Характеристики м'якого контуру
    frags.append(rect(490, 230, 380, 205, fill="#ffffff", stroke="#60a5fa", sw=1.2, rx=4))
    frags.append(text(680, 250, "ХАРАКТЕРИСТИКИ ТА НАСЛІДКИ ЗРИВУ:", size=11, bold=True, color="#1e3a8a"))
    frags.append(text(505, 272, "• Джиттер виконання: 5–50 мілісекунд", size=9.5, color="#334155", anchor="start"))
    frags.append(text(505, 292, "• Затримка планувальника Linux, I/O затримки", size=9.5, color="#334155", anchor="start"))
    frags.append(text(505, 312, "• Виконання: Multi-core ARM Cortex-A + GPU / NPU", size=9.5, color="#334155", anchor="start"))
    frags.append(text(505, 332, "• Затримка 50–100 мс: застаріла уставка траєкторії", size=9.5, color="#d97706", anchor="start"))
    frags.append(text(505, 352, "• Зависання понад 500 мс: FC переходить у Hold / Loiter", size=9.5, color="#059669", bold=True, anchor="start"))
    frags.append(text(505, 372, "• Поведінка при падінні: FC тримає політ, SBC ребутиться", size=9.5, color="#059669", anchor="start"))
    frags.append(text(505, 392, "• Статус: розширення інтелекту, а не виживання", size=9.5, color="#1e3a8a", bold=True, anchor="start"))
    frags.append(text(505, 412, "• Дозволяє безпечний збій без падіння апарата", size=9.5, color="#2563eb", anchor="start"))

    render(os.path.join(OUT_DIR, "realtime-vs-soft-domains.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_dual_board_architecture()
    fig_realtime_vs_soft_domains()
    print("All 2 figures generated successfully in img/")
