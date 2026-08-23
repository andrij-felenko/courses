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


def fig_vector_compass():
    """П'ятивекторний компас інженерного росту архітектора після progarch."""
    W, H = 1020, 520
    f = []

    # Фундаментальне ядро PROGARCH
    f.append(fitbox(370, 210, 280, 100, "ФУНДАМЕНТ PROGARCH\n\n• Інженерне судження & Смак\n• Межі, контракти, атрибути якості\n• Керування еволюцією та боргом",
                    size=12, bold=True, fill=NEUT, stroke=INK, color=INK))

    # Вектор 1: Розподілені системи (згори)
    f.append(fitbox(370, 30, 280, 110, "1. Розподілені системи & Консенсус\n\n• CAP/PACELC, Jepsen-тестування\n• Raft, Paxos, CRDT, векторні годинники\n• Асинхронність та часткові відмови",
                    size=11, fill=BLUE_T, stroke=BLUE, color=BLUE))
    f.append(arrow(510, 140, 510, 210, color=BLUE, sw=2))

    # Вектор 2: Формальна верифікація (зліва згори)
    f.append(fitbox(40, 90, 270, 110, "2. Формальна верифікація\n\n• TLA+, Alloy, Dafny\n• Доведення інваріантів до коду\n• Пошук race conditions & deadlocks",
                    size=11, fill=PURP_T, stroke=PURPLE, color=PURPLE))
    f.append(arrow(310, 145, 370, 220, color=PURPLE, sw=2))

    # Вектор 3: FinOps (справа згори)
    f.append(fitbox(710, 90, 270, 110, "3. FinOps & Хмарна економіка\n\n• Unit Economics (Cost per User)\n• Cost-Aware Architecture & Tiering\n• Spot-інстанси та Cross-AZ оверхед",
                    size=11, fill=GREEN_T, stroke=GREEN, color=GREEN))
    f.append(arrow(710, 145, 650, 220, color=GREEN, sw=2))

    # Вектор 4: Соціотехнічний DDD (зліва знизу)
    f.append(fitbox(40, 330, 270, 110, "4. Соціотехнічний DDD\n\n• Strategic DDD & Event Storming\n• Inverse Conway Maneuver\n• Team Topologies & Context Maps",
                    size=11, fill=AMBER_T, stroke=AMBER, color=AMBER))
    f.append(arrow(310, 385, 370, 310, color=AMBER, sw=2))

    # Вектор 5: Домени-профілі (справа знизу)
    f.append(fitbox(710, 330, 270, 110, "5. Домени-профілі & Спеціалізація\n\n• Low-Latency Fintech / Game Engines\n• ML/AI Platforms & Big Data\n• Embedded, RTOS & Edge Systems",
                    size=11, fill=RED_T, stroke=RED, color=RED))
    f.append(arrow(710, 385, 650, 310, color=RED, sw=2))

    # Нижній опис
    f.append(fitbox(40, 465, 940, 40, "Результат: Перехід від загального архітектора до глибинного експерта спеціалізованого напрямку",
                    size=12, bold=True, fill=NEUT, stroke=INK, color=INK))

    render(os.path.join(OUT, 'vector-compass.svg'), W, H, *f,
           title="Компас п'яти векторів інженерного росту")


def fig_depth_matrix():
    """Матриця вибору спеціалізації: Доменна складність vs Інфраструктурна складність."""
    W, H = 1020, 460
    f = []

    # Вісі координат
    f.append(arrow(80, 400, 960, 400, color=INK, sw=2))  # Горизонтальна ось (Інфраструктурна складність)
    f.append(arrow(80, 400, 80, 40, color=INK, sw=2))   # Вертикальна ось (Доменна складність)

    # Підписи осей
    f.append(fitbox(640, 415, 320, 30, "Операційна / Інфраструктурна складність →", size=11, bold=True, fill=NEUT, stroke=INK, color=INK))
    f.append(fitbox(15, 10, 220, 30, "↑ Доменна складність", size=11, bold=True, fill=NEUT, stroke=INK, color=INK))

    # Квадрант 1: Низька інфраструктура / Високий домен (Enterprise / Fintech Domain)
    f.append(fitbox(110, 70, 390, 145, "КВАДРАНТ: ГЛИБОКИЙ ДОМЕННИЙ АНАЛІЗ\n\n• Fintech, Banking, Insurance, Healthcare\n• Складна бізнес-логіка, регуляції, правила\n• Ключ: Strategic DDD, Ubiquitous Language, TLA+",
                    size=11, fill=AMBER_T, stroke=AMBER, color=AMBER))

    # Квадрант 2: Висока інфраструктура / Високий домен (Low-Latency / ML Platforms)
    f.append(fitbox(530, 70, 390, 145, "КВАДРАНТ: МАКСИМАЛЬНА СПЕЦІАЛІЗАЦІЯ\n\n• High-Frequency Trading, Real-Time Game Engines, ML Infra\n• Екстремальна латентність, розподілені алгоритми, FinOps\n• Ключ: Kernel bypass, Lock-free, Raft, GPU clusters",
                    size=11, fill=RED_T, stroke=RED, color=RED))

    # Квадрант 3: Низька інфраструктура / Низький домен (Standard SaaS)
    f.append(fitbox(110, 235, 390, 145, "КВАДРАНТ: БАЗОВА АРХІТЕКТУРА (PROGARCH)\n\n• Типові Web/SaaS застосунки, CRUD-сервіси\n• Стандартні паттерни, моноліт або легкі сервіси\n• Ключ: Clean Architecture, модульність, базові SLO",
                    size=11, fill=BLUE_T, stroke=BLUE, color=BLUE))

    # Квадрант 4: Висока інфраструктура / Низький домен (Cloud Platforms / Compute)
    f.append(fitbox(530, 235, 390, 145, "КВАДРАНТ: ІНФРАСТРУКТУРНІ ПЛАТФОРМИ\n\n• Cloud Infrastructure, Service Mesh, High-Load Edge\n• Мільйони RPS, висока доступність, мережевий оверхед\n• Ключ: Distributed Consensus, FinOps, Cell-Based Ops",
                    size=11, fill=GREEN_T, stroke=GREEN, color=GREEN))

    render(os.path.join(OUT, 'depth-matrix.svg'), W, H, *f,
           title="Матриця складності домену та інфраструктури")


def fig_t_shaped_architect():
    """Модель T-подібного профілю інженера."""
    W, H = 1020, 440
    f = []

    # Горизонтальна планка (Progarch Foundation)
    f.append(fitbox(60, 40, 900, 90, "ШИРОКИЙ ФУНДАМЕНТ (PROGARCH FOUNDATION)\n\nЯкісні атрибути • Межі контекстів • Смак & Компроміси • Еволюція & Борг • Соціотехнічний дизайн",
                    size=12, bold=True, fill=BLUE_T, stroke=BLUE, color=BLUE))

    # Вертикальні ніжки спеціалізації (Pi / T profile)
    # Ніжка 1: Розподілені системи
    f.append(fitbox(120, 150, 240, 230, "ВЕРТИКАЛЬ 1\n\nРозподілені системи\n& Консенсус\n\n• Raft / Paxos\n• CAP / PACELC\n• Jepsen verification\n• Vector clocks\n\nГлибина: Експерт",
                    size=11, fill=PURP_T, stroke=PURPLE, color=PURPLE))

    # Ніжка 2: FinOps & Cost Architecture
    f.append(fitbox(390, 150, 240, 230, "ВЕРТИКАЛЬ 2\n\nFinOps & Хмарна\nекономіка\n\n• Unit Economics\n• Tiered Storage\n• Spot Automation\n• Cross-AZ profiling\n\nГлибина: Практик",
                    size=11, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # Ніжка 3: Спеціалізований домен (напр. Low-Latency / Embedded)
    f.append(fitbox(660, 150, 240, 230, "ВЕРТИКАЛЬ 3 (За вибором)\n\nLow-Latency / Edge / ML\n\n• Kernel bypass (io_uring)\n• Data-Oriented Design\n• Feature Stores / Model Ops\n• Lock-free C++/Rust\n\nГлибина: Спеціаліст",
                    size=11, fill=AMBER_T, stroke=AMBER, color=AMBER))

    # Опис знизу
    f.append(fitbox(60, 395, 900, 35, "Модель Pi-подібного інженера: Широке архітектурне бачення + 2-3 глибинні інструментальні вертикалі",
                    size=11, bold=True, fill=NEUT, stroke=INK, color=INK))

    render(os.path.join(OUT, 't-shaped-architect.svg'), W, H, *f,
           title="Модель T-подібного та Pi-подібного профілю архітектора")


if __name__ == '__main__':
    fig_vector_compass()
    fig_depth_matrix()
    fig_t_shaped_architect()
    print("Figures generated successfully.")
