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
CYAN_T  = "#e0f7fa"
GREY_T  = "#f5f5f5"
NEUT    = "#eef2f6"

AMBER   = "#e08a1e"
GREEN   = "#2e7d32"
BLUE    = "#1565c0"
RED     = "#c62828"
PURPLE  = "#7b1fa2"
CYAN    = "#00838f"
GREY    = "#424242"


def fig_checklist_dimensions():
    """Мапа 7 критичних вимірів архітектурного чеклиста."""
    W, H = 1020, 520
    f = []

    # Центральне ядро
    f.append(fitbox(380, 205, 260, 110, "АРХІТЕКТУРНИЙ\nREADINESS GATE\n\n• 7 критичних вимірів\n• Суворі SLO & risk-бюджети\n• Валідація перед розгортанням",
                    size=13, bold=True, fill=AMBER_T, stroke=AMBER, color=AMBER))

    # 1. Стійкість (Верхній лівий)
    f.append(fitbox(40, 30, 280, 110, "1. Стійкість (Resilience)\n\n• Blast Radius & Cell Isolation\n• Circuit Breakers & Fallbacks\n• Load Shedding & Backpressure",
                    size=12, fill=RED_T, stroke=RED, color=RED))
    f.append(arrow(320, 85, 410, 205, color=RED, sw=2))

    # 2. Масштабованість (Верхній центр)
    f.append(fitbox(370, 30, 280, 110, "2. Масштабованість (Scalability)\n\n• Resource Saturation Limits\n• Sharding & Caching Topologies\n• Asynchronous Decoupling",
                    size=12, fill=BLUE_T, stroke=BLUE, color=BLUE))
    f.append(arrow(510, 140, 510, 205, color=BLUE, sw=2))

    # 3. Безпека (Верхній правий)
    f.append(fitbox(700, 30, 280, 110, "3. Безпека (Security)\n\n• STRIDE Threat Modeling\n• mTLS, PoLP & Secret Mgmt\n• Audit Logging & Sanitization",
                    size=12, fill=PURP_T, stroke=PURPLE, color=PURPLE))
    f.append(arrow(700, 85, 610, 205, color=PURPLE, sw=2))

    # 4. TCO & FinOps (Нижній лівий)
    f.append(fitbox(40, 370, 280, 110, "4. TCO & FinOps\n\n• Unit Economics per Request\n• Cloud Compute/Egress Limits\n• Maintenance & Lifecycle Costs",
                    size=12, fill=GREEN_T, stroke=GREEN, color=GREEN))
    f.append(arrow(320, 425, 410, 315, color=GREEN, sw=2))

    # 5. Еволіціонованість (Нижній центр)
    f.append(fitbox(370, 370, 280, 110, "5. Еволіціонованість (Evolvability)\n\n• SemVer & API Deprecation\n• Expand-Contract DB Migrations\n• Reversibility (2-way doors)",
                    size=12, fill=CYAN_T, stroke=CYAN, color=CYAN))
    f.append(arrow(510, 370, 510, 315, color=CYAN, sw=2))

    # 6. Соціотехнічний дизайн (Нижній правий)
    f.append(fitbox(700, 370, 280, 110, "6. Соціотехніка (Team Topologies)\n\n• Conway's Law Alignment\n• Team Cognitive Load Limits\n• Explicit Service Contracts",
                    size=12, fill=GREY_T, stroke=GREY, color=GREY))
    f.append(arrow(700, 425, 610, 315, color=GREY, sw=2))

    # 7. Спостережуваність (Лівий бічний центр)
    f.append(fitbox(40, 205, 280, 110, "7. Спостережуваність (Observability)\n\n• MELT (Metrics, Logs, Traces)\n• 4 Golden Signals & Burn Rates\n• W3C Trace Context & Runbooks",
                    size=12, fill=AMBER_T, stroke=AMBER, color=AMBER))
    f.append(arrow(320, 260, 380, 260, color=AMBER, sw=2))

    render(os.path.join(OUT, 'checklist-dimensions.svg'), W, H, *f,
           title="Мапа 7 критичних вимірів архітектурного чеклиста")


def fig_readiness_gate_pipeline():
    """Конвеєр Readiness Gate перед продакшном."""
    W, H = 1020, 400
    f = []

    # Фаза 1: Проєктування та ADR
    f.append(fitbox(40, 80, 210, 180, "1. АРХІТЕКТУРНА ГІПОТЕЗА\n\n• Draft ADR & Threat Model\n• SLO & Budget Specs\n• Capacity Projections\n\nВхід: Проєктний документ",
                    size=12, fill=BLUE_T, stroke=BLUE, color=BLUE))

    # Фаза 2: Автоматизовані Fitness Functions
    f.append(fitbox(290, 80, 220, 180, "2. CI/CD FITNESS HARNESS\n\n• Static Dependency Check\n• Contract & Schema Linter\n• Automated Load & Chaos\n\nВхід: Код та Тести",
                    size=12, fill=CYAN_T, stroke=CYAN, color=CYAN))

    # Фаза 3: Peer Review Readiness Gate
    f.append(fitbox(550, 80, 210, 180, "3. READINESS REVIEW GATE\n\n• 7-Dimension Checklist\n• Operational Runbooks\n• Risk Budget Approval\n\nВхід: Матриця перевірки",
                    size=12, bold=True, fill=AMBER_T, stroke=AMBER, color=AMBER))

    # Фаза 4: Канарейка та Продакшн
    f.append(fitbox(800, 80, 180, 180, "4. CANARY & PROD\n\n• Dark Launch (1%)\n• Burn Rate Monitor\n• Full Traffic Rollout\n\nВихід: Жива система",
                    size=12, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # Переходи між фазами
    f.append(arrow(250, 170, 290, 170, color=BLUE, sw=2))
    f.append(arrow(510, 170, 550, 170, color=CYAN, sw=2))
    f.append(arrow(760, 170, 800, 170, color=AMBER, sw=2))

    # Нижній блок відкату при вето
    f.append(fitbox(290, 300, 470, 60, "ВЕТО ТА ПОВЕРНЕННЯ (Gate Veto): Якщо хоча б 1 блокуючий вимір має НЕПРОХІДНИЙ бал, реліз повертається на доопрацювання",
                    size=12, bold=True, fill=RED_T, stroke=RED, color=RED))
    f.append(arrow(655, 260, 655, 300, color=RED, sw=2))

    render(os.path.join(OUT, 'readiness-gate-pipeline.svg'), W, H, *f,
           title="Конвеєр Readiness Gate перед продакшном")


def fig_blast_radius_matrix():
    """Матриця аналізу blast radius та ізоляції збоїв."""
    W, H = 1020, 420
    f = []

    # Небезпечна зона без ізоляції
    f.append(fitbox(40, 40, 450, 160, "БЕЗ ІЗОЛЯЦІЇ\n(Каскадний колапс)\n\nЗбій у дрібній залежності →\nВичерпання пулу сокетів →\nБлокування асинхронного ядра →\nПовний даунтайм платформи",
                    size=12, fill=RED_T, stroke=RED, color=RED))

    # Зона захисту через 4 механізми
    f.append(fitbox(530, 40, 450, 160, "ЗАХИЩЕНА АРХІТЕКТУРА\n(Ізольований радіус)\n\nЗбій залежності →\nCircuit Breaker відсікає виклики →\nFallback повертає стан з кешу →\nОсновний сервіс продовжує роботу",
                    size=12, bold=True, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # 4 Елементи захисту стійкості
    f.append(fitbox(40, 250, 210, 130, "A. Bulkheads\n(Перегородки)\n\nІзольовані пули потоків\nі сокетів для кожного\ndownstream-сервісу",
                    size=12, fill=BLUE_T, stroke=BLUE, color=BLUE))

    f.append(fitbox(280, 250, 210, 130, "B. Circuit Breaker\n\nАвтоматичне розмикання\nкола при зростанні\nпомилок > 5%",
                    size=12, fill=CYAN_T, stroke=CYAN, color=CYAN))

    f.append(fitbox(520, 250, 210, 130, "C. Graceful Fallback\n\nПовернення дегродваного\nвідповідника замість\n500 Internal Error",
                    size=12, fill=AMBER_T, stroke=AMBER, color=AMBER))

    f.append(fitbox(760, 250, 210, 130, "D. Load Shedding\n\nВідкидання некритичного\nтрафіку при сатурації\nCPU > 85%",
                    size=12, fill=PURP_T, stroke=PURPLE, color=PURPLE))

    render(os.path.join(OUT, 'blast-radius-matrix.svg'), W, H, *f,
           title="Матриця аналізу blast radius та ізоляції збоїв")


if __name__ == '__main__':
    fig_checklist_dimensions()
    fig_readiness_gate_pipeline()
    fig_blast_radius_matrix()
    print("Figures generated successfully.")
