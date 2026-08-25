# -*- coding: utf-8 -*-
"""Фігури для теми «Час поїхав: стрибок годинника, лог із майбутнього й завдання, що не спрацювало»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"

def fig_drift_and_sources():
    """drift-and-sources.svg: Три домени часу та виникнення апаратного дрейфу частоти."""
    W, H = 960, 480
    frags = []

    # Заголовок
    frags.append(text(480, 28, "Три домени часу: від кристала кварцу до еталона Stratum 0", size=15, bold=True, color="#1e293b"))

    # Блок 1: Апаратний рівень (Кварц, TSC, RTC)
    frags.append(rect(30, 55, 275, 395, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=8))
    b1_h, _, _ = textbox(167, 85, "Апаратні джерела часу", size=12, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b1_h)

    items_hw = [
        ("RTC (32.768 кГц):", True, "#1e293b"),
        ("• Живиться від батарейки CR2032", False, "#475569"),
        ("• Термочутливий зріз кварцу", False, "#475569"),
        ("• Похибка: ±20–50 ppm (1–4 с/добу)", False, RED_S),
        ("TSC / HPET / ACPI таймери:", True, "#1e293b"),
        ("• Лічильники тактів CPU / шини", False, "#475569"),
        ("• Частота залежить від температури", False, "#475569"),
        ("• Не зберігає абсолютну дату", False, "#475569"),
        ("Наслідок: неминучий Clock Drift", True, RED_S)
    ]
    for i, (t_str, bld, col) in enumerate(items_hw):
        frags.append(text(45, 120 + i * 26, t_str, size=10, bold=bld, color=col, anchor="start"))

    # Стрілка між 1 і 2
    frags.append(arrow(305, 250, 345, 250, color=AMBER_S, sw=2))
    frags.append(text(325, 240, "Такти", size=10, bold=True, color=AMBER_S))

    # Блок 2: Простір ядра Linux (Timekeeping & Шкали)
    frags.append(rect(345, 55, 275, 395, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=8))
    b2_h, _, _ = textbox(482, 85, "Ядро Linux (timekeeping)", size=12, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b2_h)

    items_k = [
        ("Підсистема tk_core:", True, "#1e293b"),
        ("• Переводить такти в наносекунди", False, "#475569"),
        ("• Множники mult/shift для ділення", False, "#475569"),
        ("• Фазова автопідстройка частоти", False, "#475569"),
        ("Шкали системного часу:", True, "#1e293b"),
        ("• CLOCK_MONOTONIC_RAW (сирий)", False, "#475569"),
        ("• CLOCK_MONOTONIC (керований)", False, "#475569"),
        ("• CLOCK_REALTIME (настінний)", False, "#475569"),
        ("Стан: STA_UNSYNC (синхр. відсутня)", True, RED_S)
    ]
    for i, (t_str, bld, col) in enumerate(items_k):
        frags.append(text(360, 120 + i * 26, t_str, size=10, bold=bld, color=col, anchor="start"))

    # Стрілка між 2 і 3
    frags.append(arrow(660, 250, 620, 250, color=TEAL_S, sw=2))
    frags.append(text(640, 240, "NTP/adj", size=10, bold=True, color=TEAL_S))

    # Блок 3: Мережевий еталон (NTP / PTP)
    frags.append(rect(660, 55, 270, 395, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=8))
    b3_h, _, _ = textbox(795, 85, "Мережеві сервери часу", size=12, bold=True, fill=TEAL_F, stroke=TEAL_S)
    frags.append(b3_h)

    items_net = [
        ("Stratum 0 / Stratum 1:", True, "#1e293b"),
        ("• Атомні годинники (цезій, рубідій)", False, "#475569"),
        ("• Супутникові сигнали GPS / Galileo", False, "#475569"),
        ("• Похибка: < 1 мікросекунди", False, GREEN_S),
        ("Мережевий транспорт (NTP/UDP):", True, "#1e293b"),
        ("• Затримка поширення (RTT)", False, "#475569"),
        ("• Джиттер (коливання затримки)", False, "#475569"),
        ("• Асиметрія каналів (вхід ≠ вихід)", False, RED_S),
        ("Ціль: корекція зміщення (Offset)", True, TEAL_S)
    ]
    for i, (t_str, bld, col) in enumerate(items_net):
        frags.append(text(675, 120 + i * 26, t_str, size=10, bold=bld, color=col, anchor="start"))

    render(os.path.join(IMG, "drift-and-sources.svg"), W, H, *frags)

def fig_step_vs_slew():
    """step-vs-slew.svg: Порівняння стрибкоподібної корекції (Step) та плавного зсуву частоти (Slew)."""
    W, H = 960, 470
    frags = []

    frags.append(text(480, 26, "Стрибок часу (Step) проти плавного підстроювання частоти (Slew)", size=15, bold=True, color="#1e293b"))

    # Ліва половина: Стрибок часу (Step)
    frags.append(rect(30, 50, 435, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    b_step, _, _ = textbox(247, 80, "Стрибок часу (Step: clock_settime / settimeofday)", size=11.5, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_step)

    # Графік стрибка
    # Осі
    frags.append(line(70, 220, 420, 220, color="#94a3b8", sw=1.2)) # вісь X (реальний час)
    frags.append(line(70, 220, 70, 110, color="#94a3b8", sw=1.2))  # вісь Y (системний час)
    frags.append(text(420, 235, "Реальний час t", size=10, color="#64748b", anchor="end"))
    frags.append(text(65, 115, "Системний час", size=10, color="#64748b", anchor="end"))

    # Лінія часу зі стрибком назад
    frags.append(line(70, 200, 220, 140, color=RED_S, sw=2.5))
    frags.append(line(220, 140, 220, 180, color=RED_S, sw=2, dash="4,3")) # вертикальний розрив
    frags.append(line(220, 180, 390, 120, color=RED_S, sw=2.5))
    frags.append(circle(220, 140, 4, fill=RED_S))
    frags.append(circle(220, 180, 4, fill="#ffffff", stroke=RED_S, sw=2))
    frags.append(text(230, 162, "Стрибок назад (Δt < 0)", size=10, bold=True, color=RED_S, anchor="start"))

    conseq_step = [
        ("Наслідки різкого стрибка:", True, RED_S),
        ("• Порушення монотонності: t₂ < t₁ у логах", False, "#334155"),
        ("• cron: пропускає хвилини (якщо вперед) або запускає двічі (якщо назад)", False, "#334155"),
        ("• Безпека: падіння сесій TLS, інвалідація JWT/Kerberos", False, "#334155"),
        ("• Бази даних: колізії версій LWW (Cassandra), порушення лідерства Raft", False, "#334155")
    ]
    for i, (t_str, bld, col) in enumerate(conseq_step):
        frags.append(text(50, 260 + i * 22, t_str, size=10, bold=bld, color=col, anchor="start"))

    # Права половина: Плавний зсув (Slewing)
    frags.append(rect(495, 50, 435, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    b_slew, _, _ = textbox(712, 80, "Плавний зсув (Slew: adjtimex / ntp_adjtime)", size=11.5, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_slew)

    # Графік плавного зсуву
    frags.append(line(535, 220, 885, 220, color="#94a3b8", sw=1.2)) # вісь X
    frags.append(line(535, 220, 535, 110, color="#94a3b8", sw=1.2)) # вісь Y
    frags.append(text(885, 235, "Реальний час t", size=10, color="#64748b", anchor="end"))
    frags.append(text(530, 115, "Системний час", size=10, color="#64748b", anchor="end"))

    # Лінія часу: плавний вигин частоти (без розриву)
    frags.append(line(535, 190, 645, 150, color="#94a3b8", sw=1.5, dash="3,3")) # траєкторія з дрейфом
    frags.append(line(535, 190, 650, 155, color=GREEN_S, sw=2.5))
    frags.append(line(650, 155, 780, 130, color=GREEN_S, sw=2.5)) # уповільнений нахил
    frags.append(line(780, 130, 865, 115, color=GREEN_S, sw=2.5))
    frags.append(text(690, 138, "Плавне гальмування/прискорення (±500 ppm)", size=10, bold=True, color=GREEN_S, anchor="start"))

    conseq_slew = [
        ("Переваги плавного регулювання:", True, GREEN_S),
        ("• Сувора монотонність: d(час)/dt > 0 завжди", False, "#334155"),
        ("• cron: жодна хвилина не втрачається й не дублюється", False, "#334155"),
        ("• Таймери: epoll, timerfd, nanosleep не зависають і не спрацьовують раніше", False, "#334155"),
        ("• Обмеження ядра: макс. зсув 0.5 мс/с (1 с різниці компенсується 2000 с)", False, "#334155")
    ]
    for i, (t_str, bld, col) in enumerate(conseq_slew):
        frags.append(text(515, 260 + i * 22, t_str, size=9.5, bold=bld, color=col, anchor="start"))

    render(os.path.join(IMG, "step-vs-slew.svg"), W, H, *frags)

def fig_marzullo_and_daemons():
    """marzullo-and-daemons.svg: Порівняння systemd-timesyncd та chrony / фільтра Марцулло."""
    W, H = 960, 480
    frags = []

    frags.append(text(480, 26, "Демони синхронізації: простота SNTP проти стійкості алгоритму Марцулло", size=15, bold=True, color="#1e293b"))

    # Ліва колонка: systemd-timesyncd
    frags.append(rect(30, 50, 435, 410, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    b_sync, _, _ = textbox(247, 80, "systemd-timesyncd (SNTP-клієнт)", size=12, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_sync)

    sync_points = [
        ("Принцип дії: простий SNTP (RFC 4330)", True, "#1e293b"),
        ("• Підключається лише до одного сервера за раз", False, "#475569"),
        ("• Не має фільтрації викидів та статистичного аналізу", False, "#475569"),
        ("• Зберігає позначку на диск (/var/lib/systemd/timesync/clock)", False, "#475569"),
        ("Поведінка під час розбіжності:", True, "#1e293b"),
        ("• При зміщенні < 0.4 с: викликає adjtimex (slew)", False, "#475569"),
        ("• При зміщенні > 0.4 с: робить різкий STEP (clock_settime)", False, RED_S),
        ("• Сліпо довіряє єдиному обраному серверу", False, RED_S),
        ("Сфера застосування: десктопи, вбудовані системи", True, "#1e293b")
    ]
    for i, (t_str, bld, col) in enumerate(sync_points):
        frags.append(text(50, 115 + i * 23, t_str, size=9.5, bold=bld, color=col, anchor="start"))

    # Права колонка: chrony + Marzullo
    frags.append(rect(495, 50, 435, 410, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    b_chr, _, _ = textbox(712, 80, "chrony / ntpd (Повний NTP + фільтр Марцулло)", size=12, bold=True, fill=TEAL_F, stroke=TEAL_S)
    frags.append(b_chr)

    # Міні-візуалізація перетину інтервалів Марцулло
    frags.append(rect(515, 105, 395, 115, fill="#ffffff", stroke=TEAL_S, sw=1, rx=5))
    frags.append(text(712, 122, "Алгоритм перетину інтервалів довіри (Marzullo)", size=9.5, bold=True, color=TEAL_S))

    # Джерело A [10, 30]
    frags.append(line(535, 142, 675, 142, color=BLUE_S, sw=3))
    frags.append(text(530, 145, "A", size=10, bold=True, color=BLUE_S, anchor="end"))

    # Джерело B [15, 35]
    frags.append(line(570, 158, 710, 158, color=BLUE_S, sw=3))
    frags.append(text(530, 161, "B", size=10, bold=True, color=BLUE_S, anchor="end"))

    # Джерело C [20, 40]
    frags.append(line(605, 174, 745, 174, color=BLUE_S, sw=3))
    frags.append(text(530, 177, "C", size=10, bold=True, color=BLUE_S, anchor="end"))

    # Falseticker D [75, 95] (збійне джерело)
    frags.append(line(785, 158, 895, 158, color=RED_S, sw=3))
    frags.append(text(780, 161, "D (збій)", size=10, bold=True, color=RED_S, anchor="end"))

    # Зона консенсусу
    frags.append(rect(605, 134, 70, 48, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=3))
    frags.append(text(640, 198, "Перетин більшості (Truechimers)", size=10, bold=True, color=GREEN_S))

    chr_points = [
        ("Переваги chrony:", True, "#1e293b"),
        ("• Опитує пул із 3–7 джерел, відсікає фальшиві (falsetickers)", False, "#475569"),
        ("• Зберігає коефіцієнт дрейфу в driftfile між перезавантаженнями", False, "#475569"),
        ("• Компенсує асиметрію мережі та термодрейф процесора", False, "#475569"),
        ("• Може тримати точність у субмілісекундному діапазоні", False, GREEN_S),
        ("Сфера: сервери баз даних, високонавантажені кластери", True, "#1e293b")
    ]
    for i, (t_str, bld, col) in enumerate(chr_points):
        frags.append(text(515, 235 + i * 23, t_str, size=9.5, bold=bld, color=col, anchor="start"))

    render(os.path.join(IMG, "marzullo-and-daemons.svg"), W, H, *frags)

if __name__ == "__main__":
    fig_drift_and_sources()
    fig_step_vs_slew()
    fig_marzullo_and_daemons()
    print("Згенеровано 3 фігури у", IMG)
