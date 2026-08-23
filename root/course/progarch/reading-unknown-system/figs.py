# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

BLUE_T  = "#eaf0fd"
GREEN_T = "#e7f6ec"
AMBER_T = "#fdf0dd"
RED_T   = "#fdecea"
PURP_T  = "#f3e8ff"
NEUT    = "#eef2f6"

AMBER   = "#e08a1e"
GREEN   = "#2e7d32"
BLUE    = "#1565c0"
RED     = "#c62828"
PURPLE  = "#7b1fa2"


def fig_recon_three_vectors():
    """Три вектори дослідницької археології чужої системи:
    згори (трафік і C4), знизу (телеметрія й БД), збоку (git і люди)."""
    W, H = 1000, 480
    f = []

    # Центральне ядро: Мапа домену й Безпечна сітка
    f.append(fitbox(380, 200, 240, 100, "Мапа домену й безпечна сітка\n\n(C4 + Трейси + Hotspot Map)",
                    size=13, bold=True, fill=BG, stroke=INK, color=INK))

    # Вектор 1: Згори (Top-Down)
    f.append(fitbox(50, 40, 260, 110, "1. Згори (Top-Down)\n\n• Зовнішній трафік & Ingress\n• Точки входу API / MQTT / Webhook\n• Реконструкція C4 (L1/L2)",
                    size=12, fill=BLUE_T, stroke=BLUE, color=BLUE))
    f.append(arrow(310, 95, 420, 200, color=BLUE, sw=2))

    # Вектор 2: Знизу (Bottom-Up)
    f.append(fitbox(690, 40, 260, 110, "2. Знизу (Bottom-Up)\n\n• Телеметрія & Trace-ідентифікатори\n• Схеми БД & обсяги таблиць\n• Пошук швів (Seams) і херек-тестів",
                    size=12, fill=GREEN_T, stroke=GREEN, color=GREEN))
    f.append(arrow(690, 95, 580, 200, color=GREEN, sw=2))

    # Вектор 3: Збоку (Side-Channel)
    f.append(fitbox(370, 340, 260, 110, "3. Збоку (Side-Channel)\n\n• Git Forensics (Churn × Complexity)\n• Авторство комітів & Закон Конвея\n• Реконструкція ADR (чому так збудовано)",
                    size=12, fill=PURP_T, stroke=PURPLE, color=PURPLE))
    f.append(arrow(500, 340, 500, 300, color=PURPLE, sw=2))

    # Результат розвідки
    f.append(fitbox(50, 210, 250, 80, "Результат: Керована еволюція\n\n(замість панічного rewrite)",
                    size=12, bold=True, fill=AMBER_T, stroke=AMBER, color=AMBER))
    f.append(arrow(380, 250, 300, 250, color=AMBER, sw=2))

    render(os.path.join(OUT, 'recon-three-vectors.svg'), W, H, *f,
           title="Три вектори дослідницької археології чужої системи")


def fig_c4_top_down_reconstruction():
    """Реконструкція мапи контейнерів C4 згори вниз: простеження трафіку."""
    W, H = 1020, 440
    f = []

    # Шари згори вниз
    # 1. Зовнішні джерела трафіку
    f.append(fitbox(40, 40, 940, 60, "Зовнішній світ: IoT Hub (MQTT) · Mobile App (HTTPS) · Webhooks (REST)",
                    size=13, bold=True, fill=BLUE_T, stroke=BLUE, color=BLUE))

    f.append(arrow(200, 100, 200, 150, color=BLUE, sw=2))
    f.append(arrow(510, 100, 510, 150, color=BLUE, sw=2))
    f.append(arrow(820, 100, 820, 150, color=BLUE, sw=2))

    # 2. Точка входу / API Gateway & Ingress
    f.append(fitbox(40, 150, 940, 60, "Точка входу: TLS Termination · API Gateway · EMQX Broker (Первинна межа)",
                    size=13, bold=True, fill=AMBER_T, stroke=AMBER, color=AMBER))

    f.append(arrow(240, 210, 240, 260, color=AMBER, sw=2))
    f.append(arrow(510, 210, 510, 260, color=AMBER, sw=2))
    f.append(arrow(780, 210, 780, 260, color=AMBER, sw=2))

    # 3. Внутрішній граф викликів (Контейнери C4)
    f.append(fitbox(40, 260, 280, 70, "Device Registry\n(Авторизація й метадані)", size=12, fill=NEUT, stroke=INK))
    f.append(fitbox(370, 260, 280, 70, "Telemetry Ingest\n(Потік подій давачів)", size=12, fill=NEUT, stroke=INK))
    f.append(fitbox(700, 260, 280, 70, "Rule Engine / Automation\n(Монолітне legacy-ядро)", size=12, fill=RED_T, stroke=RED, color=RED))

    f.append(arrow(180, 330, 180, 370, color=INK, sw=1.5))
    f.append(arrow(510, 330, 510, 370, color=INK, sw=1.5))
    f.append(arrow(840, 330, 840, 370, color=INK, sw=1.5))

    # 4. Сховища даних (БД знизу)
    f.append(fitbox(40, 370, 280, 50, "PostgreSQL (пристрої)", size=12, fill=GREEN_T, stroke=GREEN, color=GREEN))
    f.append(fitbox(370, 370, 280, 50, "TimescaleDB / Kafka (телеметрія)", size=12, fill=GREEN_T, stroke=GREEN, color=GREEN))
    f.append(fitbox(700, 370, 280, 50, "Redis (стан правил)", size=12, fill=GREEN_T, stroke=GREEN, color=GREEN))

    render(os.path.join(OUT, 'c4-top-down-reconstruction.svg'), W, H, *f,
           title="Реконструкція мапи контейнерів C4 згори вниз")


def fig_thirty_day_playbook():
    """30-денний календар археології legacy-системи: 4 фази."""
    W, H = 1000, 380
    f = []

    phases = [
        ("Дні 1–5: Огородження", "Запуск у сендбоксі\nТрейси & SLO baseline\nРуки геть від коду!", BLUE_T, BLUE, 40),
        ("Дні 6–15: Мапування", "Реконструкція C4 L1/L2\nСхеми БД & каталог API\nGit Hotspot-аналіз", GREEN_T, GREEN, 280),
        ("Дні 16–22: Безпека", "Виявлення швів (Seams)\nХарактеризаційні тести\nФормування ADR-0", AMBER_T, AMBER, 520),
        ("Дні 23–30: Перша зміна", "Мала реструктуризація\nBranch by Abstraction\nШвидка перемога (Quick Win)", PURP_T, PURPLE, 760),
    ]

    for title, desc, bg, stroke, x in phases:
        f.append(fitbox(x, 40, 200, 60, title, size=13, bold=True, fill=bg, stroke=stroke, color=stroke))
        f.append(fitbox(x, 120, 200, 180, desc, size=12, fill=NEUT, stroke=stroke))

    # Стрілки фазового переходу
    f.append(arrow(240, 70, 280, 70, color=BLUE, sw=2))
    f.append(arrow(480, 70, 520, 70, color=GREEN, sw=2))
    f.append(arrow(720, 70, 760, 70, color=AMBER, sw=2))

    # Нижня вісь результату
    f.append(fitbox(40, 320, 920, 45, "Результат: Довіра бізнесу + Зняття страху перед системою + Керована еволюція",
                    size=13, bold=True, fill=BG, stroke=INK, color=INK))

    render(os.path.join(OUT, 'thirty-day-playbook.svg'), W, H, *f,
           title="30-денний календар археології legacy-системи")


if __name__ == '__main__':
    fig_recon_three_vectors()
    fig_c4_top_down_reconstruction()
    fig_thirty_day_playbook()
    print("Figures generated successfully!")
