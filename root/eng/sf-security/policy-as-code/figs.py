# -*- coding: utf-8 -*-
import sys
import os

# scripts/ directory is 4 levels up: book/programming/security/policy-as-code -> ../../../..
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. pep-pdp-decoupling: Точка застосування (PEP) та Точка ухвалення (PDP) ──
def fig_pep_pdp_decoupling():
    W, H = 820, 320
    p = []

    # Клієнтський запит ліворуч
    p.append(rect(30, 110, 130, 80, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(95, 142, "Суб'єкт", size=13, color=INK, bold=True))
    p.append(text(95, 164, "клієнт / сервіс", size=11, color=MUTED))

    # Стрілка запиту до PEP
    p.append(arrow(160, 150, 240, 150, color=INK, sw=2))
    p.append(text(200, 140, "Запит", size=11, color=INK))

    # Блок PEP (Policy Enforcement Point)
    p.append(rect(240, 70, 200, 160, fill="#eaf0fd", stroke=NEG, sw=2, rx=10))
    p.append(text(340, 100, "PEP", size=15, color=NEG, bold=True))
    p.append(text(340, 122, "Точка застосування", size=12, color=INK, bold=True))
    p.append(text(340, 144, "API Gateway / K8s / Proxy", size=11, color=MUTED))
    p.append(text(340, 180, "зупиняє запит і чекає вердикт", size=10, color=NEG, italic=True))
    p.append(text(340, 200, "сам логіки правил НЕ знає", size=10, color=MUTED))

    # Стрілки між PEP та PDP
    p.append(arrow(440, 120, 560, 120, color=NEG, sw=2))
    p.append(text(500, 110, "1. JSON payload", size=11, color=NEG, bold=True))

    p.append(arrow(560, 180, 440, 180, color=FIELD, sw=2))
    p.append(text(500, 170, "2. allow / deny", size=11, color=FIELD, bold=True))

    # Блок PDP (Policy Decision Point)
    p.append(rect(560, 50, 230, 200, fill="#eaf6ec", stroke=FIELD, sw=2, rx=10))
    p.append(text(675, 80, "PDP", size=15, color=FIELD, bold=True))
    p.append(text(675, 102, "Точка ухвалення рішення", size=12, color=INK, bold=True))
    p.append(text(675, 124, "Рушій політик (напр. OPA)", size=11, color=MUTED))

    # Входи в PDP
    b1, _, _ = textbox(675, 165, "Декларативні правила (Rego)", size=11, color=INK,
                       fill="#ffffff", stroke=FIELD, sw=1.2, min_w=200)
    p.append(b1)
    b2, _, _ = textbox(675, 205, "Контекстні дані (data JSON)", size=11, color=INK,
                       fill="#ffffff", stroke=FIELD, sw=1.2, min_w=200)
    p.append(b2)

    # Виконання запиту далі або блокування
    p.append(arrow(340, 230, 340, 280, color=POS, sw=1.8))
    p.append(text(340, 300, "403 Forbidden (якщо deny)", size=11, color=POS, bold=True))

    # Стрілка праворуч до цільового ресурсу (якщо allow)
    p.append(arrow(340, 70, 340, 25, color=FIELD, sw=2))
    p.append(text(340, 15, "Пропуск до захищеного сервісу (allow)", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "pep-pdp-decoupling.svg"), W, H, *p,
           title="Архітектурне розділення PEP та PDP")


# ── 2. rego-evaluation-model: Модель обчислення в OPA ─────────────────────────
def fig_rego_evaluation_model():
    W, H = 820, 310
    p = []

    # Ліва колонка: Вхідні дані (input) та База знань (data)
    # Блок Input
    p.append(rect(30, 40, 200, 100, fill="#fdf6e2", stroke="#b58900", sw=1.8, rx=8))
    p.append(text(130, 65, "Вхідний документ (input)", size=12, color="#b58900", bold=True))
    p.append(text(130, 88, "HTTP method, path, headers", size=10, color=INK))
    p.append(text(130, 106, "K8s Pod manifest, JWT claims", size=10, color=INK))
    p.append(text(130, 124, "Terraform plan JSON", size=10, color=MUTED))

    # Блок Data
    p.append(rect(30, 170, 200, 100, fill="#f0f4f8", stroke="#475569", sw=1.8, rx=8))
    p.append(text(130, 195, "База контексту (data)", size=12, color="#475569", bold=True))
    p.append(text(130, 218, "Ролі користувачів (RBAC)", size=10, color=INK))
    p.append(text(130, 236, "Дозволені реєстри образів", size=10, color=INK))
    p.append(text(130, 254, "Списки винятків і ліміти", size=10, color=MUTED))

    # Центральний блок: Ядро оцінки OPA
    p.append(rect(290, 30, 260, 250, fill="#eaf6ec", stroke=FIELD, sw=2, rx=10))
    p.append(text(420, 60, "Рушій OPA (Rego Core)", size=14, color=FIELD, bold=True))
    p.append(text(420, 82, "Декларативне обчислення Datalog", size=11, color=INK))

    p.append(rect(310, 105, 220, 60, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(420, 125, "default allow = false", size=11, color=POS, bold=True))
    p.append(text(420, 145, "allow { input.role == \"admin\" }", size=10, color=INK))

    p.append(rect(310, 180, 220, 80, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(420, 200, "deny[msg] {", size=10, color=NEG, bold=True))
    p.append(text(420, 218, "  input.user.mfa == false", size=10, color=INK))
    p.append(text(420, 236, "  msg := \"MFA required\"", size=10, color=INK))
    p.append(text(420, 252, "}", size=10, color=NEG, bold=True))

    # Стрілки від входів до OPA
    p.append(arrow(230, 90, 290, 90, color="#b58900", sw=2))
    p.append(arrow(230, 220, 290, 220, color="#475569", sw=2))

    # Стрілки до виходу
    p.append(arrow(550, 155, 610, 155, color=FIELD, sw=2))

    # Правий блок: Результат рішення
    p.append(rect(610, 50, 180, 210, fill="#ffffff", stroke=INK, sw=1.8, rx=8))
    p.append(text(700, 78, "Структурований", size=12, color=INK, bold=True))
    p.append(text(700, 96, "результат (JSON)", size=12, color=INK, bold=True))

    p.append(rect(625, 120, 150, 45, fill="#eaf6ec", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(700, 140, "allow: true/false", size=11, color=FIELD, bold=True))
    p.append(text(700, 154, "булевий вердикт", size=9, color=MUTED))

    p.append(rect(625, 180, 150, 65, fill="#fbecec", stroke=POS, sw=1.5, rx=6))
    p.append(text(700, 202, "deny: [ \"...\" ]", size=11, color=POS, bold=True))
    p.append(text(700, 220, "список порушень", size=9, color=MUTED))
    p.append(text(700, 234, "та мутацій (patch)", size=9, color=MUTED))

    render(os.path.join(OUT, "rego-evaluation-model.svg"), W, H, *p,
           title="Модель обчислення запитів у Policy-as-Code")


# ── 3. pac-lifecycle-shift-left: Життєвий цикл політик ────────────────────────
def fig_pac_lifecycle_shift_left():
    W, H = 820, 260
    p = []

    # 4 етапи конвеєра: Редактор -> CI/CD перевірка -> K8s Admission -> Runtime Mesh
    stages = [
        (30, "1. Локальна розробка", "IDE / Conftest / CLI", "перевірка маніфестів на машині автора", "#f8fafc", LINE),
        (225, "2. CI/CD конвеєр", "Shift-Left сканування", "блокування PR за порушення безпеки", "#eaf0fd", NEG),
        (425, "3. Контролер допуску", "K8s Gatekeeper / Kyverno", "перевірка API-запитів перед записом в etcd", "#fff6e0", "#caa24a"),
        (625, "4. Runtime авторизація", "Envoy / Sidecar OPA", "авторизація RPC та HTTP викликів", "#eaf6ec", FIELD)
    ]

    for x, title, sub, desc, fill, stroke in stages:
        p.append(rect(x, 60, 165, 130, fill=fill, stroke=stroke, sw=1.8, rx=8))
        p.append(text(x + 82, 85, title, size=11, color=INK, bold=True))
        p.append(text(x + 82, 108, sub, size=10, color=stroke, bold=True))
        # Дворядковий опис
        lines = [desc[:22], desc[22:]] if len(desc) > 22 else [desc]
        if len(desc) > 22:
            p.append(text(x + 82, 138, lines[0], size=9, color=MUTED))
            p.append(text(x + 82, 154, lines[1], size=9, color=MUTED))
        else:
            p.append(text(x + 82, 142, desc, size=9, color=MUTED))

    # Стрілки між етапами
    p.append(arrow(195, 125, 225, 125, color=INK, sw=1.8))
    p.append(arrow(390, 125, 425, 125, color=INK, sw=1.8))
    p.append(arrow(590, 125, 625, 125, color=INK, sw=1.8))

    # Загальна стрілка під ними «Зсув ліворуч (Shift-Left)»
    p.append(line(50, 220, 770, 220, color=NEG, sw=2))
    p.append(arrow(750, 220, 50, 220, color=NEG, sw=2))
    p.append(text(410, 210, "Зсув ліворуч (Shift-Left): виявлення порушень до потрапляння в продакшн", size=11, color=NEG, bold=True))
    p.append(text(410, 242, "Єдине джерело істини — спільний репозиторій політик у Git", size=10, color=MUTED))

    render(os.path.join(OUT, "pac-lifecycle-shift-left.svg"), W, H, *p,
           title="Життєвий цикл перевірки політик: від коду до рантайму")


# ── 4. data-distribution-modes: Три способи доставки контексту ───────────────
def fig_data_distribution_modes():
    W, H = 820, 280
    p = []

    # 3 способи: Push у токені, Багатошаровий Bundle, Pull під час запиту
    modes = [
        (30, "1. Push у запиті (JWT)", "Дані приходять усередині payload", "Швидко (< 1 мс), без запитів до мережі.", "Мінус: розмір токена, важко відкликати.", "#eaf6ec", FIELD),
        (295, "2. Синхронізація Bundles", "Фонові архіви політик і даних", "Автономність PDP, висока швидкість.", "Мінус: затримка оновлення (eventual).", "#eaf0fd", NEG),
        (560, "3. Pull під час оцінки", "Виклик http.send() до API/БД", "Завжди свіжі дані з джерела істини.", "Мінус: затримка мережі (10-100 мс).", "#fdf6e2", "#b58900")
    ]

    for x, title, sub, pro, con, fill, stroke in modes:
        p.append(rect(x, 40, 230, 210, fill=fill, stroke=stroke, sw=1.8, rx=8))
        p.append(text(x + 115, 68, title, size=12, color=INK, bold=True))
        p.append(text(x + 115, 92, sub, size=10, color=stroke, bold=True))

        p.append(rect(x + 15, 115, 200, 48, fill="#ffffff", stroke=stroke, sw=1, rx=6))
        p.append(text(x + 115, 134, "Плюс:", size=9, color=FIELD, bold=True))
        p.append(text(x + 115, 150, pro, size=9, color=INK))

        p.append(rect(x + 15, 175, 200, 58, fill="#ffffff", stroke=POS, sw=1, rx=6))
        p.append(text(x + 115, 194, "Компроміс:", size=9, color=POS, bold=True))
        # розбивка con
        c1, c2 = con.split(":") if ":" in con else ("", con)
        p.append(text(x + 115, 210, "Мінус: " + c2.replace("Мінус:", "").strip()[:26], size=9, color=MUTED))
        p.append(text(x + 115, 224, c2.replace("Мінус:", "").strip()[26:], size=9, color=MUTED))

    render(os.path.join(OUT, "data-distribution-modes.svg"), W, H, *p,
           title="Стратегії доставки контекстних даних до рушія політик")


if __name__ == "__main__":
    fig_pep_pdp_decoupling()
    fig_rego_evaluation_model()
    fig_pac_lifecycle_shift_left()
    fig_data_distribution_modes()
    print("All figures generated successfully.")
