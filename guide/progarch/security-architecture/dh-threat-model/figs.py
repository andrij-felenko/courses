# -*- coding: utf-8 -*-
"""Фігури до теми «Threat model Digital Homes» (модуль 28)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

TINT_G = "#eef7f0"   # світло-зелений фон (безпека / валідація)
TINT_R = "#fdecea"   # світло-червоний фон (вектори загроз / атака)
TINT_B = "#eef2fd"   # світло-синій фон (ядро / компоненти)
TINT_Y = "#fffceb"   # світло-жовтий фон (межа довіри / перевірка)


def fig_dh_trust_boundaries():
    """Мапа меж довіри та векторів загроз STRIDE у Digital Homes."""
    W, H = 1080, 680
    frags = []

    # Заголовок
    frags.append(text(540, 35, "Мапа меж довіри та загроз STRIDE у платформі Digital Homes",
                      size=16, bold=True, color=INK))

    # Зони довіри (Контейнери/Сегменти)
    # Зона 1: Периферія та Локальна мережа
    frags.append(rect(40, 65, 230, 580, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(155, 95, "Зона 1: Периферія та IoT", size=14, bold=True, color=INK))
    frags.append(text(155, 115, "(Zigbee, Matter, BLE)", size=11, color=MUTED))

    box_dev1, _, _ = textbox(155, 180, "Датчики руху / витоку\n(Нізька обчислювальна сила)", size=12, fill=FILL, stroke=LINE)
    box_dev2, _, _ = textbox(155, 300, "Розумний замок / Реле\n(Критичний виклик дії)", size=12, fill=TINT_Y, stroke=NEG, bold=True)
    box_dev3, _, _ = textbox(155, 420, "IP-камера спостереження\n(RTSP / H.264 потік)", size=12, fill=FILL, stroke=LINE)
    box_dev4, _, _ = textbox(155, 540, "Гостьова Wi-Fi мережа\n(Ненадійне середовище)", size=12, fill=TINT_R, stroke=LINE)
    frags.extend([box_dev1, box_dev2, box_dev3, box_dev4])

    # МЕЖА ДОВІРИ 1 (Local / Hub)
    frags.append(rect(285, 65, 20, 580, fill=TINT_R, stroke=NEG, sw=1, rx=2))
    frags.append(text(295, 350, "МЕЖА ДОВІРИ 1: Локальна мережа ↔ Хаб", size=11, bold=True, color=NEG, anchor="middle"))

    # Зона 2: Домашній хаб (Linux Gateway)
    frags.append(rect(320, 65, 320, 580, fill=TINT_B, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(480, 95, "Зона 2: Розумний хаб (Linux Gateway)", size=14, bold=True, color=INK))
    frags.append(text(480, 115, "(TPM 2.0 / Read-Only RootFS / cgroups)", size=11, color=MUTED))

    box_hub1, _, _ = textbox(480, 180, "Zigbee / Matter Daemon\n(Ізольований seccomp процес)", size=12, fill=FILL, stroke=LINE)
    box_hub2, _, _ = textbox(480, 300, "Local Rule Engine & Twin\n(Валідація команд та стану)", size=12, fill=FILL, stroke=LINE, bold=True)
    box_hub3, _, _ = textbox(480, 420, "OTA & Key Manager\n(Перевірка Ed25519 підпису)", size=12, fill=TINT_G, stroke=FIELD, bold=True)
    box_hub4, _, _ = textbox(480, 540, "MQTT Agent (mTLS Client)\n(Автентифікація пристрою)", size=12, fill=FILL, stroke=LINE)
    frags.extend([box_hub1, box_hub2, box_hub3, box_hub4])

    # МЕЖА ДОВІРИ 2 (Hub / Cloud Edge)
    frags.append(rect(655, 65, 20, 580, fill=TINT_R, stroke=NEG, sw=1, rx=2))
    frags.append(text(665, 350, "МЕЖА ДОВІРИ 2: Публічний Інтернет (TLS 1.3 / mTLS)", size=11, bold=True, color=NEG, anchor="middle"))

    # Зона 3: Хмарний периметр та Сервіси
    frags.append(rect(690, 65, 350, 580, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(865, 95, "Зона 3: Хмарна платформа DH", size=14, bold=True, color=INK))
    frags.append(text(865, 115, "(MQTT Broker, BFF, Storage)", size=11, color=MUTED))

    box_cloud1, _, _ = textbox(865, 180, "MQTT Broker Cluster\n(Захист від DDoS & Rate Limit)", size=12, fill=FILL, stroke=LINE)
    box_cloud2, _, _ = textbox(865, 300, "Telemetry Ingestion & Authz\n(Аудит та перевірка токенів)", size=12, fill=FILL, stroke=LINE)
    box_cloud3, _, _ = textbox(865, 420, "Secure OTA Vault\n(Підписання прошивок HSM)", size=12, fill=TINT_G, stroke=FIELD, bold=True)
    box_cloud4, _, _ = textbox(865, 540, "Mobile BFF & API Gateway\n(OAuth2 / OIDC + Audit Log)", size=12, fill=FILL, stroke=LINE)
    frags.extend([box_cloud1, box_cloud2, box_cloud3, box_cloud4])

    # Стрілки потоків даних
    frags.append(arrow(210, 300, 370, 300, color=LINE, sw=1.6))
    frags.append(arrow(590, 540, 740, 180, color=LINE, sw=1.6))
    frags.append(arrow(740, 420, 590, 420, color=FIELD, sw=2.0))

    render(os.path.join(IMG, "dh-trust-boundaries.svg"), W, H, *frags,
           title="Мапа меж довіри та загроз STRIDE у платформі Digital Homes")


def fig_ota_verification_sequence():
    """Ланцюжок криптографічної перевірки оновлення прошивки (OTA)."""
    W, H = 1080, 520
    frags = []

    frags.append(text(540, 35, "Ланцюжок довіри криптографічної перевірки оновлення прошивки (OTA)",
                      size=16, bold=True, color=INK))

    steps = [
        ("1. CI/CD & HSM Підпис", TINT_B, LINE,
         "Публікація артефакту:\nБільд прошивки v2.4 + Ed25519 підпис HSM ключем розробника."),

        ("2. Завантаження на Хаб", TINT_Y, LINE,
         "Передача по mTLS:\nОтримання артефакту через HTTPS/mTLS у тимчасове сховище RAM."),

        ("3. Hardware Root of Trust", TINT_Y, NEG,
         "Перевірка eFuse / TPM:\nВерсія v2.4 ≥ поточна v2.3. Захист від відкату (Anti-Rollback)."),

        ("4. Валідація Ed25519", TINT_G, FIELD,
         "Криптографічний підпис:\nПублічний ключ із Read-Only flash підтверджує цілісність."),

        ("5. Атомний Boot A/B", TINT_G, FIELD,
         "Запис у банк B та Reboot:\nПеремикання bootloader. У разі збою — відкат у банк A."),
    ]

    x0, w = 50, 180
    gap = 25
    y = 80
    box_h = 380

    for i, (title_str, tint, border_col, desc_str) in enumerate(steps):
        cx = x0 + i * (w + gap) + w // 2
        frags.append(rect(cx - w // 2, y, w, box_h, fill=tint, stroke=border_col, sw=1.6, rx=8))
        frags.append(text(cx, y + 35, title_str, size=13, color=INK, bold=True))

        lines = desc_str.split("\n")
        frags.append(text(cx, y + 80, lines[0], size=12, color=MUTED, bold=True))
        frags.append(text(cx, y + 120, lines[1], size=11.5, color=INK))

        if i < len(steps) - 1:
            arrow_x1 = cx + w // 2
            arrow_x2 = arrow_x1 + gap
            frags.append(arrow(arrow_x1, y + box_h // 2, arrow_x2, y + box_h // 2, color=LINE, sw=2.0))

    render(os.path.join(IMG, "ota-verification-sequence.svg"), W, H, *frags,
           title="Ланцюжок криптографічної перевірки оновлення прошивки (OTA)")


if __name__ == "__main__":
    fig_dh_trust_boundaries()
    fig_ota_verification_sequence()
    print("OK: dh-trust-boundaries.svg, ota-verification-sequence.svg")
