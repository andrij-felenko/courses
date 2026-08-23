# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми cost-as-fitness-function (ProgArch)."""

import os
import sys

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))

from svgkit import (
    render, textbox, rect, line, arrow, mtext, text, circle,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))
os.makedirs(OUT_DIR, exist_ok=True)


def make_fig1():
    """Фігура 1: Порівняння традиційної фідбек-петлі FinOps та Shift-Left у CI."""
    dw, dh = 800, 360
    el = []
    
    # Фон та сітка порівняння
    el.append(rect(0, 0, dw, dh, fill=BG, stroke=LINE, sw=1))
    
    # Заголовок блоку 1: Традиційний реактивний FinOps
    el.append(rect(20, 20, 360, 320, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    el.append(text(200, 50, "Традиційна реактивна модель", size=16, color=POS, bold=True))
    el.append(text(200, 70, "(Затримка 30–45 днів)", size=12, color=MUTED, italic=True))
    
    b1_1, _, _ = textbox(200, 110, "Написання коду та PR\n(Розробник)", size=12, fill=BG, stroke=LINE)
    el.append(b1_1)
    el.append(arrow(200, 130, 200, 160, color=LINE))
    
    b1_2, _, _ = textbox(200, 180, "Злиття та деплой у продакшн\n(Без оцінки вартості)", size=12, fill=BG, stroke=LINE)
    el.append(b1_2)
    el.append(arrow(200, 200, 200, 230, color=LINE))
    
    b1_3, _, _ = textbox(200, 250, "Щомісячний хмарний рахунок\n(AWS / GCP Invoice)", size=12, fill="#f8d7da", stroke=POS)
    el.append(b1_3)
    
    # Пунктирна стрелка фідбеку
    el.append(arrow(110, 250, 110, 120, color=POS, sw=1.8))
    el.append(text(80, 180, "Шоковий рахунок\nза 30 днів", size=10, color=POS, bold=True))

    # Заголовок блоку 2: Shift-Left FinOps у CI
    el.append(rect(420, 20, 360, 320, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=8))
    el.append(text(600, 50, "Shift-Left FinOps у CI/CD", size=16, color=FIELD, bold=True))
    el.append(text(600, 70, "(Затримка 30–60 секунд)", size=12, color=MUTED, italic=True))
    
    b2_1, _, _ = textbox(600, 110, "Написання коду та PR\n(Розробник)", size=12, fill=BG, stroke=LINE)
    el.append(b2_1)
    el.append(arrow(600, 130, 600, 160, color=LINE))
    
    b2_2, _, _ = textbox(600, 180, "FinOps Fitness Function у CI\n(Infracost + OPA + Load Profile)", size=12, fill="#d4edda", stroke=FIELD)
    el.append(b2_2)
    
    # Шляхи вердикту
    el.append(arrow(530, 200, 480, 240, color=POS))
    b2_block, _, _ = textbox(480, 260, "Блокування PR\n(Дорого!)", size=11, fill="#f8d7da", stroke=POS)
    el.append(b2_block)
    
    el.append(arrow(670, 200, 720, 240, color=FIELD))
    b2_pass, _, _ = textbox(720, 260, "Злиття та деплой\n(Бюджет ОК)", size=11, fill="#d4edda", stroke=FIELD)
    el.append(b2_pass)
    
    # Петля швидкого зворотного зв'язку
    el.append(arrow(480, 280, 530, 120, color=POS, sw=1.8))
    el.append(text(490, 160, "Миттєве виправлення\nдо злиття", size=10, color=POS, bold=True))

    out_path = os.path.join(OUT_DIR, 'fig1-shift-left-finops.svg')
    render(out_path, dw, dh, "\n".join(el))
    print("Generated fig1-shift-left-finops.svg")


def make_fig2():
    """Фігура 2: Двошарова модель фітнес-функцій вартості (Static IaC vs Dynamic Unit-Cost)."""
    dw, dh = 800, 340
    el = []
    
    el.append(rect(0, 0, dw, dh, fill=BG, stroke=LINE, sw=1))
    el.append(text(400, 30, "Двошарова модель архітектурного контролю вартості", size=16, color=INK, bold=True))
    
    # Вхідна дія: Git Commit / PR
    b_in, _, _ = textbox(400, 75, "Вхідний комміт / Pull Request", size=13, fill=FILL, stroke=LINE, bold=True)
    el.append(b_in)
    
    el.append(arrow(320, 95, 230, 130, color=LINE))
    el.append(arrow(480, 95, 570, 130, color=LINE))
    
    # Шар 1: Статичний контроль (Static IaC)
    el.append(rect(40, 130, 340, 185, fill="#edf2ff", stroke=NEG, sw=1.5, rx=8))
    el.append(text(210, 155, "Шар 1: Статичний кошторис (IaC Static)", size=14, color=NEG, bold=True))
    
    tb1, _, _ = textbox(210, 195, "Terraform / OpenTofu / Pulumi AST", size=11, fill=BG, stroke=LINE)
    el.append(tb1)
    el.append(arrow(210, 212, 210, 230, color=LINE))
    tb2, _, _ = textbox(210, 248, "Infracost API + Cloud Price Engine", size=11, fill=BG, stroke=LINE)
    el.append(tb2)
    el.append(text(210, 290, "Ловить: додаткові бази, NAT-шлюзи, диски", size=10, color=MUTED, italic=True))
    
    # Шар 2: Динамічний контроль (Dynamic Unit-Cost)
    el.append(rect(420, 130, 340, 185, fill="#feefea", stroke=POS, sw=1.5, rx=8))
    el.append(text(590, 155, "Шар 2: Динамічний юніт-кост (Runtime Profiling)", size=14, color=POS, bold=True))
    
    tb3, _, _ = textbox(590, 195, "CI Load Test (k6) + Profiling (CPU/RAM/DB)", size=11, fill=BG, stroke=LINE)
    el.append(tb3)
    el.append(arrow(590, 212, 590, 230, color=LINE))
    tb4, _, _ = textbox(590, 248, "Unit-Cost Model ($ / 1M бізнес-запитів)", size=11, fill=BG, stroke=LINE)
    el.append(tb4)
    el.append(text(590, 290, "Ловить: N+1 запити, деградацію CPU/пам'яті", size=10, color=MUTED, italic=True))

    out_path = os.path.join(OUT_DIR, 'fig2-two-layer-fitness-model.svg')
    render(out_path, dw, dh, "\n".join(el))
    print("Generated fig2-two-layer-fitness-model.svg")


def make_fig3():
    """Фігура 3: Наскрізний конвеєр CI/CD з FinOps-вартовими (Guardrail Pipeline)."""
    dw, dh = 820, 320
    el = []
    
    el.append(rect(0, 0, dw, dh, fill=BG, stroke=LINE, sw=1))
    el.append(text(410, 30, "Архітектура CI/CD конвеєра з FinOps Guardrails", size=16, color=INK, bold=True))
    
    # Крок 1: Developer PR
    b1, _, _ = textbox(80, 100, "1. Git Push / PR\n(Розробник)", size=11, fill=FILL, stroke=LINE)
    el.append(b1)
    el.append(arrow(135, 100, 175, 100, color=LINE))
    
    # Крок 2: Static IaC Diff
    b2, _, _ = textbox(245, 100, "2. IaC Diff Engine\n(Infracost CLI)", size=11, fill="#edf2ff", stroke=NEG)
    el.append(b2)
    el.append(arrow(315, 100, 355, 100, color=LINE))
    
    # Крок 3: OPA Policy Check
    b3, _, _ = textbox(435, 100, "3. Policy Evaluator\n(OPA / Rego Rules)", size=11, fill="#fef5e7", stroke=LINE)
    el.append(b3)
    el.append(arrow(515, 100, 555, 100, color=LINE))
    
    # Крок 4: PR Bot Comment & Gate
    b4, _, _ = textbox(635, 100, "4. Guardrail Gate\n(PR Comment / Status)", size=11, fill=BG, stroke=LINE, bold=True)
    el.append(b4)
    
    # Гілки рішення від Кроку 4
    el.append(arrow(635, 125, 520, 200, color=POS, sw=1.8))
    b_block, _, _ = textbox(520, 225, "🚫 BLOCKED\n(Перевищення бюджету)", size=11, fill="#f8d7da", stroke=POS)
    el.append(b_block)
    
    el.append(arrow(635, 125, 730, 200, color=FIELD, sw=1.8))
    b_pass, _, _ = textbox(730, 225, "✅ PASSED\n(Бюджет дотримано)", size=11, fill="#d4edda", stroke=FIELD)
    el.append(b_pass)
    
    # Крок 5: Canary Unit-Cost Check від PASSED
    el.append(arrow(730, 250, 410, 280, color=FIELD))
    b5, _, _ = textbox(250, 280, "5. Canary Release & Unit-Cost Monitoring\n(Авто-відкат при регресії >10%)", size=11, fill="#eafaf1", stroke=FIELD)
    el.append(b5)

    out_path = os.path.join(OUT_DIR, 'fig3-ci-finops-pipeline.svg')
    render(out_path, dw, dh, "\n".join(el))
    print("Generated fig3-ci-finops-pipeline.svg")


if __name__ == '__main__':
    make_fig1()
    make_fig2()
    make_fig3()
