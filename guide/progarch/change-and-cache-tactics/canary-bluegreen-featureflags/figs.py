# -*- coding: utf-8 -*-
"""Фігури до теми «Canary, blue-green, feature-flags»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_blue_green_deployment():
    """Схема Blue-Green розгортання з маршрутизатором трафіку та спільною БД."""
    W, H = 960, 480
    frags = []

    # ── Вхідний трафік та балансувальник ──
    frags.append(rect(40, 210, 140, 60, fill="#eef2f7", stroke=INK, sw=1.8, rx=8))
    frags.append(text(110, 235, "Вхідний трафік", size=13, bold=True, color=INK))
    frags.append(text(110, 253, "HTTP / gRPC", size=11, color=MUTED))

    frags.append(rect(230, 190, 160, 100, fill="#fdf6e3", stroke=POS, sw=2.0, rx=8))
    frags.append(text(310, 220, "Маршрутизатор", size=14, bold=True, color=POS))
    frags.append(text(310, 240, "L7 Router / ALB", size=11, color=INK))
    frags.append(text(310, 265, "Cutover: 0% → 100%", size=11, bold=True, color=POS))

    frags.append(arrow(180, 240, 230, 240, color=INK, sw=2.0))

    # ── Blue Environment (Active) ──
    frags.append(rect(450, 40, 260, 170, fill="#e8f4f8", stroke="#1b6ec2", sw=2.0, rx=10))
    frags.append(text(580, 68, "BLUE (Активне / v1.0)", size=14, bold=True, color="#1b6ec2"))
    frags.append(rect(470, 95, 100, 45, fill="#ffffff", stroke="#1b6ec2", sw=1.2, rx=6))
    frags.append(text(520, 122, "App v1.0 (A)", size=12, color=INK))
    frags.append(rect(590, 95, 100, 45, fill="#ffffff", stroke="#1b6ec2", sw=1.2, rx=6))
    frags.append(text(640, 122, "App v1.0 (B)", size=12, color=INK))
    frags.append(text(580, 185, "Обслуговує 100% користувачів", size=11, color="#1b6ec2", bold=True))

    # ── Green Environment (Standby / New) ──
    frags.append(rect(450, 270, 260, 170, fill="#eafaf0", stroke=FIELD, sw=2.0, rx=10))
    frags.append(text(580, 298, "GREEN (Нове / v1.1)", size=14, bold=True, color=FIELD))
    frags.append(rect(470, 325, 100, 45, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(520, 352, "App v1.1 (A)", size=12, color=INK))
    frags.append(rect(590, 325, 100, 45, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(640, 352, "App v1.1 (B)", size=12, color=INK))
    frags.append(text(580, 415, "Стенд тестування / Готовий до перемикання", size=10, color=FIELD))

    # ── Маршрути з роутера ──
    frags.append(arrow(390, 220, 450, 130, color="#1b6ec2", sw=2.5))
    frags.append(text(405, 160, "100%", size=12, bold=True, color="#1b6ec2"))

    frags.append(line(390, 260, 450, 350, color=MUTED, sw=1.5, dash="6,4"))
    frags.append(text(405, 320, "0%", size=12, bold=True, color=MUTED))

    # ── Спільна База Даних ──
    frags.append(rect(780, 160, 150, 160, fill="#fdecea", stroke=POS, sw=2.0, rx=10))
    frags.append(text(855, 190, "Спільна БД", size=14, bold=True, color=POS))
    frags.append(text(855, 215, "Shared Database", size=11, color=MUTED))
    frags.append(line(800, 235, 910, 235, color=MUTED, sw=1, dash="4,4"))
    frags.append(text(855, 260, "Expand-Contract", size=11, bold=True, color=POS))
    frags.append(text(855, 280, "Зворотно-сумісна", size=10, color=INK))
    frags.append(text(855, 298, "схема (v1.0 & v1.1)", size=10, color=INK))

    # З'єднання Blue/Green з БД
    frags.append(arrow(710, 130, 780, 210, color="#1b6ec2", sw=1.8))
    frags.append(arrow(710, 350, 780, 270, color=FIELD, sw=1.8))

    render(os.path.join(IMG, "blue-green-deployment.svg"), W, H, *frags,
           title="Blue-Green розгортання: миттєве перемикання між двома середовищами")


def fig_canary_rollout_pipeline():
    """Етапи розкочування канарейкового випуску із автоматичним аналізом (ACA)."""
    W, H = 960, 460
    frags = []

    # ── Лінія фаз канарки ──
    phases = [
        ("Фаза 0: Baseline", "100% v1.0", "Перевірка SLI baseline", "#eef2f7", INK),
        ("Фаза 1: Canary 1%", "99% v1.0 / 1% v1.1", "ACA оцінка (5-15 хв)", "#fdf6e3", POS),
        ("Фаза 2: Canary 25%", "75% v1.0 / 25% v1.1", "Аналіз p99 latency & 5xx", "#fff3cd", POS),
        ("Фаза 3: Full Rollout", "0% v1.0 / 100% v1.1", "Реліз завершено", "#eafaf0", FIELD),
    ]

    x_start = 30
    box_w = 210
    gap = 25
    y_top = 50

    for i, (title_str, dist_str, note_str, fill_col, border_col) in enumerate(phases):
        x = x_start + i * (box_w + gap)
        frags.append(rect(x, y_top, box_w, 130, fill=fill_col, stroke=border_col, sw=1.8, rx=8))
        frags.append(text(x + box_w / 2, y_top + 30, title_str, size=13, bold=True, color=border_col))
        frags.append(text(x + box_w / 2, y_top + 60, dist_str, size=12, bold=True, color=INK))
        frags.append(line(x + 15, y_top + 80, x + box_w - 15, y_top + 80, color=MUTED, sw=1, dash="4,4"))
        frags.append(text(x + box_w / 2, y_top + 105, note_str, size=11, color=MUTED))

        if i < len(phases) - 1:
            frags.append(arrow(x + box_w, y_top + 65, x + box_w + gap, y_top + 65, color=border_col, sw=2.0))

    # ── Блок Автоматичного Аналізу Канарки (ACA) ──
    frags.append(rect(180, 230, 600, 180, fill="#fdf7f7", stroke=POS, sw=2.0, rx=10))
    frags.append(text(480, 260, "Автоматичний аналіз канарки (Automated Canary Analysis)", size=14, bold=True, color=POS))

    # Порівняння груп
    frags.append(rect(210, 285, 240, 75, fill="#ffffff", stroke="#1b6ec2", sw=1.2, rx=6))
    frags.append(text(330, 308, "Baseline (v1.0 Контроль)", size=12, bold=True, color="#1b6ec2"))
    frags.append(text(330, 330, "Метрики: 5xx = 0.01%, p99 = 42ms", size=10, color=INK))

    frags.append(text(480, 322, "VS", size=14, bold=True, color=POS))

    frags.append(rect(510, 285, 240, 75, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(630, 308, "Canary (v1.1 Канарейка)", size=12, bold=True, color=FIELD))
    frags.append(text(630, 330, "Метрики: 5xx = 0.01%, p99 = 44ms", size=10, color=INK))

    # Рішення
    frags.append(rect(210, 375, 260, 25, fill="#eafaf0", stroke=FIELD, sw=1.0, rx=4))
    frags.append(text(340, 392, "✓ Відхилення < 2% → Продовжити", size=10, bold=True, color=FIELD))

    frags.append(rect(490, 375, 260, 25, fill="#fdecea", stroke=POS, sw=1.0, rx=4))
    frags.append(text(620, 392, "✗ Аномалія Latency/5xx → Авто-відкат", size=10, bold=True, color=POS))

    render(os.path.join(IMG, "canary-rollout-pipeline.svg"), W, H, *frags,
           title="Канарейковий конвеєр: фазове збільшення частки та автоматичний аналіз метрик")


def fig_feature_flag_decoupling():
    """Розділення часу деплою коду від часу випуску функціональності за допомогою Feature Flags."""
    W, H = 960, 420
    frags = []

    # ── Часова вісь ──
    frags.append(arrow(80, 340, 900, 340, color=INK, sw=2.0))
    frags.append(text(890, 365, "Час (Time)", size=12, bold=True, color=INK))

    # Події на часовій осі
    events = [
        (160, "1. Deploy Code", "Деплой коду на прод\n(Flag = FALSE)", "#1b6ec2"),
        (380, "2. Dark Launch", "Трафік тестування\n(Flag = USER_ID % 100 < 5)", POS),
        (620, "3. Business Release", "Увімкнення для всіх\n(Flag = TRUE)", FIELD),
        (820, "4. Cleanup Debt", "Видалення прапорця\n(Код спрощено)", MUTED),
    ]

    for x, label, desc, col in events:
        frags.append(line(x, 100, x, 340, color=col, sw=1.8, dash="6,4"))
        frags.append(rect(x - 80, 50, 160, 40, fill="#ffffff", stroke=col, sw=1.5, rx=6))
        frags.append(text(x, 74, label, size=12, bold=True, color=col))

        # Опис під віссю
        lines = desc.split('\n')
        for idx, l_str in enumerate(lines):
            frags.append(text(x, 370 + idx * 18, l_str, size=11, color=INK))

    # ── Блок журналу стану прапорця ──
    frags.append(rect(140, 130, 680, 160, fill="#fafafa", stroke=INK, sw=1.5, rx=8))
    frags.append(text(480, 155, "Динамічний оцінювач прапорців (Feature Flag Evaluator)", size=13, bold=True, color=INK))

    # Стан 1: OFF
    frags.append(rect(160, 175, 180, 95, fill="#fdecea", stroke=POS, sw=1.2, rx=6))
    frags.append(text(250, 195, "Код у проді, але OFF", size=11, bold=True, color=POS))
    frags.append(text(250, 218, "if (flags.isOff()) {", size=10, color=INK))
    frags.append(text(250, 235, "  runLegacyCode();", size=10, color=MUTED))
    frags.append(text(250, 252, "}", size=10, color=INK))

    # Стан 2: Targeted
    frags.append(rect(360, 175, 240, 95, fill="#fdf6e3", stroke=POS, sw=1.2, rx=6))
    frags.append(text(480, 195, "Канарейка / Dark Launch", size=11, bold=True, color=POS))
    frags.append(text(480, 218, "if (eval(flag, userCtx)) {", size=10, color=INK))
    frags.append(text(480, 235, "  runNewFeature();", size=10, color=FIELD))
    frags.append(text(480, 252, "}", size=10, color=INK))

    # Стан 3: ON
    frags.append(rect(620, 175, 180, 95, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(710, 195, "100% Реліз (ON)", size=11, bold=True, color=FIELD))
    frags.append(text(710, 218, "if (true) {", size=10, color=INK))
    frags.append(text(710, 235, "  runNewFeature();", size=10, color=FIELD))
    frags.append(text(710, 252, "}", size=10, color=INK))

    render(os.path.join(IMG, "feature-flag-decoupling.svg"), W, H, *frags,
           title="Feature Flags: відокремлення задеплоєного коду від моментального випуску")


if __name__ == "__main__":
    fig_blue_green_deployment()
    fig_canary_rollout_pipeline()
    fig_feature_flag_decoupling()
    print("Figures generated successfully.")
