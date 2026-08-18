# -*- coding: utf-8 -*-
"""Фігури до теми «День витоку DH» ( security-architecture / dh-leak-day )."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

TINT_G = "#eef7f0"   # світло-зелений фон (безпека / відновимо)
TINT_R = "#fdecea"   # світло-червоний фон (витік / компрометація)
TINT_B = "#eef2fd"   # світло-синій фон (система / процеси)
TINT_Y = "#fffceb"   # світло-жовтий фон (проміжні секрети)

def fig_blast_radius_cascade():
    """Граф каскадного поширення компрометації при витоку CI-ключа."""
    W, H = 1000, 520
    frags = []

    frags.append(text(500, 30, "Граф каскадного поширення компрометації (Blast Radius)", size=16, bold=True, color=INK))

    # Колонка 1: Джерело витоку
    frags.append(rect(30, 65, 230, 420, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(145, 95, "1. Джерело витоку", size=14, bold=True, color=INK))
    frags.append(text(145, 115, "(Публічний коміт GitHub)", size=11, color=MUTED))

    b1, _, _ = textbox(145, 180, "Файл .env.production\n+ ci-deployer.pem", size=12, fill=TINT_R, stroke=POS, bold=True)
    b2, _, _ = textbox(145, 300, "Автоматичні боти\n(Сканування за 3-8 с)", size=12, fill=FILL, stroke=LINE)
    b3, _, _ = textbox(145, 400, "Компрометація IAM роли\n(AWS / K8s Cluster Admin)", size=12, fill=TINT_R, stroke=POS)
    frags.extend([b1, b2, b3])

    # Стрілка 1 -> 2
    frags.append(arrow(260, 400, 320, 400, color=POS, sw=2))

    # Колонка 2: Захоплений периметр
    frags.append(rect(320, 65, 300, 420, fill=TINT_R, stroke=POS, sw=1.5, rx=8))
    frags.append(text(470, 95, "2. Зламана інфраструктура", size=14, bold=True, color=POS))
    frags.append(text(470, 115, "(Прямий доступ до Prod)", size=11, color=POS))

    b4, _, _ = textbox(470, 180, "Доступ до KMS & Secrets Vault\n(KEK / Master Secrets)", size=12, fill=BG, stroke=POS, bold=True)
    b5, _, _ = textbox(470, 300, "JWT Signing Private Key\n(Ed25519 Root Key)", size=12, fill=BG, stroke=POS, bold=True)
    b6, _, _ = textbox(470, 400, "mTLS Fleet Intermediate CA\n(Ключ видачі сертифікатів)", size=12, fill=BG, stroke=POS, bold=True)
    frags.extend([b4, b5, b6])

    # Стрілка 2 -> 3
    frags.append(arrow(620, 180, 680, 180, color=POS, sw=2))
    frags.append(arrow(620, 300, 680, 300, color=POS, sw=2))
    frags.append(arrow(620, 400, 680, 400, color=POS, sw=2))

    # Колонка 3: Вплив на кінцеві ресурси
    frags.append(rect(680, 65, 290, 420, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(825, 95, "3. Зкомпрометовані активи", size=14, bold=True, color=INK))
    frags.append(text(825, 115, "(Обсяг ураження)", size=11, color=MUTED))

    b7, _, _ = textbox(825, 180, "Бази даних & Video Storage\n(Розшифрування PII / медіа)", size=12, fill=TINT_Y, stroke=LINE)
    b8, _, _ = textbox(825, 300, "Підробка сесій користувачів\n(Генерація будь-яких JWT)", size=12, fill=TINT_Y, stroke=LINE)
    b9, _, _ = textbox(825, 400, "Доступ до 1.2M хабів DH\n(Підробка команд замкам)", size=12, fill=TINT_R, stroke=POS, bold=True)
    frags.extend([b7, b8, b9])

    render(os.path.join(IMG, "blast-radius-cascade.svg"), W, H, *frags)

def fig_revocation_sequence():
    """Етапи каскадного реагування та відкликання секретів."""
    W, H = 1000, 480
    frags = []

    frags.append(text(500, 30, "Послідовність каскадного реагування на витік ключів", size=16, bold=True, color=INK))

    steps = [
        ("Фаза 1: Containment", "0–15 хв", "· Revoke CI credentials\n· K8s IAM isolation\n· Bloom filter for JWT", TINT_R, POS),
        ("Фаза 2: Core Secrets", "15–60 хв", "· DB / Redis secret rotation\n· JWKS rollover (kid_v2)\n· Service restart", TINT_Y, LINE),
        ("Фаза 3: KMS & Storage", "1–4 години", "· KMS KEK rotation\n· Re-wrap DEK headers\n· Audit log freeze", TINT_B, NEG),
        ("Фаза 4: Fleet Migration", "1–14 днів", "· Dual-CA deployment\n· Staggered mTLS re-issue\n· Legacy CA revocation", TINT_G, FIELD),
    ]

    x = 40
    for i, (title_str, time_str, desc_str, bg_col, border_col) in enumerate(steps):
        frags.append(rect(x, 70, 210, 370, fill=bg_col, stroke=border_col, sw=1.5, rx=8))
        frags.append(text(x + 105, 100, title_str, size=13, bold=True, color=INK))
        frags.append(text(x + 105, 122, time_str, size=12, bold=True, color=border_col))
        
        box, _, _ = textbox(x + 105, 240, desc_str, size=11, fill=BG, stroke=border_col)
        frags.append(box)

        if i < 3:
            frags.append(arrow(x + 210, 245, x + 230, 245, color=LINE, sw=2))

        x += 230

    render(os.path.join(IMG, "revocation-sequence.svg"), W, H, *frags)

def fig_fleet_rotation_timeline():
    """Часова шкала та динаміка оновлення секретів і ключів у розподіленій системі."""
    W, H = 960, 420
    frags = []

    frags.append(text(480, 30, "Часова шкала зрізу ротації: Хмара vs Поле (Fleet)", size=16, bold=True, color=INK))

    # Вісь часу
    frags.append(arrow(60, 350, 900, 350, color=LINE, sw=2))
    frags.append(text(920, 354, "Час", size=12, bold=True, color=INK, anchor="start"))

    ticks = [
        (100, "t=0", "Витік CI"),
        (250, "15 хв", "JWT Bloom filter"),
        (420, "1 год", "JWKS kid_v2"),
        (590, "24 год", "KMS KEK done"),
        (760, "14 днів", "Fleet mTLS 100%"),
    ]

    for tx, tlbl, sub in ticks:
        frags.append(line(tx, 345, tx, 355, color=LINE, sw=2))
        frags.append(text(tx, 375, tlbl, size=12, bold=True, color=INK))
        frags.append(text(tx, 395, sub, size=10, color=MUTED))

    # Смуги систем
    # Cloud API & Edge (0 - 1 год)
    frags.append(rect(100, 80, 320, 45, fill=TINT_R, stroke=POS, sw=1, rx=4))
    frags.append(text(260, 107, "Cloud Edge & API (Негайний розрив сесій)", size=11, bold=True, color=POS))

    # Backend Services (15 хв - 24 год)
    frags.append(rect(250, 145, 340, 45, fill=TINT_Y, stroke=LINE, sw=1, rx=4))
    frags.append(text(420, 172, "Backend Services & KEK (Ротація секретів БД)", size=11, bold=True, color=INK))

    # Gateway Hubs (1 год - 14 днів)
    frags.append(rect(420, 210, 340, 45, fill=TINT_B, stroke=NEG, sw=1, rx=4))
    frags.append(text(590, 237, "1.2M Home Hubs (Staggered mTLS rollover)", size=11, bold=True, color=NEG))

    # Battery IoT Sensors (1 день - 30 днів)
    frags.append(rect(590, 275, 280, 45, fill=TINT_G, stroke=FIELD, sw=1, rx=4))
    frags.append(text(730, 302, "Автономні датчики (Lazy re-bind)", size=11, bold=True, color=FIELD))

    render(os.path.join(IMG, "fleet-rotation-timeline.svg"), W, H, *frags)

if __name__ == "__main__":
    fig_blast_radius_cascade()
    fig_revocation_sequence()
    fig_fleet_rotation_timeline()
    print("Generated all SVGs for dh-leak-day")
