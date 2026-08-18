# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER   = "#e08a1e"
RED     = "#d9534f"
GREEN   = "#2e7d32"
BLUE    = "#1565c0"
PURPLE  = "#6a1b9a"
RED_T   = "#fdecea"
AMBER_T = "#fdf0dd"
GREEN_T = "#e7f6ec"
BLUE_T  = "#eaf0fd"
NEUT    = "#eef2f6"


def fig_cognitive_capacity_equation():
    """Візуалізація балансу когнітивного навантаження: переповнена робоча пам'ять при високому
    сторонньому навантаженні проти вивільненої ємності під доречну роботу після платформи."""
    W, H = 1000, 420
    f = []

    # ── Заголовок колонок ──
    f.append(fitbox(60, 40, 410, 36, "А. Високе стороннє навантаження (Хаос)", size=14, bold=True, fill=RED_T, stroke=RED))
    f.append(fitbox(530, 40, 410, 36, "Б. Збережена ємність після Платформи", size=14, bold=True, fill=GREEN_T, stroke=GREEN))

    # ── Колонка А: Переповнена ємність ──
    # Контейнер робочої пам'яті (разом 100%)
    f.append(fitbox(60, 95, 410, 160, "Стороннє навантаження (Extraneous)\n65% ємності\n(YAML, CI/CD, k8s, ручні розгортання, біганина)", size=12, fill="#ffebee", stroke=RED))
    f.append(fitbox(60, 260, 410, 90, "Внутрішнє навантаження (Intrinsic)\n30% ємності\n(складність бізнес-домену)", size=12, fill=AMBER_T, stroke=AMBER))
    f.append(fitbox(60, 355, 410, 30, "Доречне (Germane): 5% — Вигорання!", size=12, bold=True, fill="#ffe0b2", stroke="#e65100"))

    # ── Колонка Б: Оптимальний розподіл ──
    f.append(fitbox(530, 95, 410, 40, "Extraneous: 10% (Платформа)", size=12, fill=BLUE_T, stroke=BLUE))
    f.append(fitbox(530, 140, 410, 90, "Внутрішнє навантаження (Intrinsic)\n30% ємності\n(складність бізнес-домену)", size=12, fill=AMBER_T, stroke=AMBER))
    f.append(fitbox(530, 235, 410, 150, "Доречне навантаження (Germane)\n60% ємності\n(Доменне моделювання, якісний код,\nархітектурні рішення, перевірка інваріантів)", size=13, bold=True, fill=GREEN_T, stroke=GREEN))

    render(os.path.join(OUT, 'cognitive-capacity-equation.svg'), W, H, *f,
           title="Рівняння когнітивної ємності команди: вплив стороннього навантаження")


def fig_boundary_by_cognitive_load():
    """Порівняння підходів розкрою: наївний розрозріз за LOC/сутностями (когнітивне перевантаження)
    проти соціотехнічного розкрою за когнітивним навантаженням."""
    W, H = 1020, 440
    f = []

    # ── Ліва панель: Наївний розрозріз ──
    f.append(fitbox(40, 40, 440, 36, "Наївний розкроювання: 15 мікросервісів на 1 команду", size=13, bold=True, fill=RED_T, stroke=RED))
    
    # 15 дрібних блоків
    for i in range(3):
        for j in range(5):
            x = 55 + j * 82
            y = 95 + i * 55
            f.append(fitbox(x, y, 74, 44, f"Svc-{i*5+j+1}", size=11, fill=NEUT, stroke="#b0bec5"))
    
    f.append(fitbox(40, 280, 440, 130, "Результат:\n• 15 репозиторіїв та 15 CI/CD конвеєрів\n• Постійне перемикання контексту\n• Команда не тримає систему в голові\n• Високий Extraneous Load", size=12, fill="#fff3e0", stroke=AMBER))

    # ── Стрілка переходу ──
    f.append(arrow(490, 210, 520, 210, color=INK, sw=2))

    # ── Права панель: Розкроювання за когнітивним навантаженням ──
    f.append(fitbox(530, 40, 450, 36, "Розкроювання за когнітивним навантаженням", size=13, bold=True, fill=GREEN_T, stroke=GREEN))

    f.append(fitbox(545, 95, 200, 160, "Bounded Context A\n\nStream-aligned Team 1\n(2 сервіси в межах ємності)", size=12, fill=BLUE_T, stroke=BLUE))
    f.append(fitbox(765, 95, 200, 160, "Bounded Context B\n\nStream-aligned Team 2\n(Модульний моноліт)", size=12, fill=GREEN_T, stroke=GREEN))

    f.append(fitbox(545, 270, 420, 50, "Внутрішня платформа (Platform Team) — Golden Path", size=12, bold=True, fill="#f3e5f5", stroke=PURPLE))

    f.append(fitbox(530, 335, 450, 75, "Результат: Чітке володіння, низьке стороннє навантаження,\nсистема повністю влазить у голову кожного розробника", size=12, fill=GREEN_T, stroke=GREEN))

    render(os.path.join(OUT, 'boundary-by-cognitive-load.svg'), W, H, *f,
           title="Порівняння наївного розрозрізу та розкроювання за когнітивним навантаженням")


def fig_team_topologies_load_offloading():
    """Схема зняття когнітивного навантаження через топології команд (Stream-aligned, Platform, Complicated Subsystem)."""
    W, H = 980, 400
    f = []

    # Stream-aligned team (у центрі)
    f.append(fitbox(330, 140, 320, 120, "Stream-Aligned Team\n(Основний потік цінності)\n\nФокус: Доменне моделювання\nта Germane Load", size=13, bold=True, fill=GREEN_T, stroke=GREEN))

    # Platform team (знизу - знімає Extraneous load)
    f.append(fitbox(240, 300, 500, 65, "Platform Team (Внутрішня платформа / IDP)\nЗнімає Extraneous Load: CI/CD, Kubernetes, Observability, IAM", size=12, bold=True, fill=BLUE_T, stroke=BLUE))
    f.append(arrow(490, 300, 490, 260, color=BLUE, sw=2))
    f.append(text(505, 285, "X-as-a-Service", size=11, color=BLUE))

    # Complicated subsystem team (ліворуч - забрала важкий Intrinsic load)
    f.append(fitbox(40, 140, 230, 120, "Complicated Subsystem\nTeam\n(напр. Відеокодеки/ML)\n\nЗабирає важкий Intrinsic Load", size=12, bold=True, fill=AMBER_T, stroke=AMBER))
    f.append(arrow(270, 200, 330, 200, color=AMBER, sw=2))

    # Enabling team (праворуч - розширює ємність через навчання)
    f.append(fitbox(700, 140, 240, 120, "Enabling Team\n(напр. Безпека / Архитектура)\n\nТимчасово підвищує\nнавички Stream-команди", size=12, fill="#fff3e0", stroke="#e65100"))
    f.append(arrow(700, 200, 650, 200, color="#e65100", sw=2))
    f.append(text(675, 190, "Facilitating", size=11, color="#e65100"))

    render(os.path.join(OUT, 'team-topologies-load-offloading.svg'), W, H, *f,
           title="Розподіл когнітивного навантаження між топологіями команд")


def fig_dh_cognitive_redesign():
    """Соціотехнічна трансформація Digital Homes: від перевантаженої єдиної команди до розподілених меж."""
    W, H = 1020, 420
    f = []

    # Ліворуч: До реорганізації
    f.append(fitbox(40, 40, 420, 36, "До: 1 команда відповідає за 14 сервісів DH", size=13, bold=True, fill=RED_T, stroke=RED))
    f.append(fitbox(40, 90, 420, 220, "Команда DH Core (7 осіб)\n\n• IoT Hub • Device Twins • Telemetry Ingestion\n• Rule Automations • Video Streaming • Billing\n• OTA Updates • User Auth • Push Notifications\n• Kubernetes Manifests • Terraform • Grafana\n\nРезультат: Постійні пожежі, нульова швидкість", size=12, fill="#ffebee", stroke=RED))

    # Стрілка
    f.append(arrow(480, 200, 520, 200, color=INK, sw=2))

    # Праворуч: Після соціотехнічного рефакторингу
    f.append(fitbox(540, 40, 440, 36, "Після: Розкрій за когнітивним навантаженням", size=13, bold=True, fill=GREEN_T, stroke=GREEN))

    f.append(fitbox(540, 90, 210, 110, "Stream Team A\n\nПристрої та Твіни\n(Bounded Context 1)", size=12, fill=GREEN_T, stroke=GREEN))
    f.append(fitbox(770, 90, 210, 110, "Stream Team B\n\nАвтоматизації та Правила\n(Bounded Context 2)", size=12, fill=GREEN_T, stroke=GREEN))

    f.append(fitbox(540, 215, 440, 75, "Complicated Subsystem Team: Відеоаналітика та потік\n(Високе математичне Intrinsic Load винесене)", size=12, fill=AMBER_T, stroke=AMBER))

    f.append(fitbox(540, 305, 440, 85, "Platform Team: Внутрішня платформа DH (Golden Path)\n(Забрала Kubernetes, CI/CD, Observability)", size=12, fill=BLUE_T, stroke=BLUE))

    render(os.path.join(OUT, 'dh-cognitive-redesign.svg'), W, H, *f,
           title="Соціотехнічний рефакторинг Digital Homes за когнітивним навантаженням")


if __name__ == "__main__":
    fig_cognitive_capacity_equation()
    fig_boundary_by_cognitive_load()
    fig_team_topologies_load_offloading()
    fig_dh_cognitive_redesign()
    print("Усі фігури успішно згенеровано.")
