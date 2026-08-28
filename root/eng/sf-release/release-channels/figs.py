# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def box(cx, cy, s, size=13, pad=9, **kw):
    frag, w, h = textbox(cx, cy, s, size=size, pad=pad, **kw)
    return frag


# ── Фігура 1: Конвеєр просування артефакту крізь канали ───────────────────────
def fig_channel_promotion_pipeline():
    W, H = 1000, 460
    frags = []

    y_boxes = 140

    # 4 основні канали
    frags.append(box(110, y_boxes, "1. Nightly (Нічний)\n• Збірка щоночі з trunk\n• Автоматичні CI/HIL\n• Ризик: високий (95% SLI)",
                     size=11, bold=True, fill="#fdecea", stroke=POS, min_w=170))

    frags.append(box(370, y_boxes, "2. Beta (Тестовий)\n• Щотижневі збірки\n• Early adopters і пілоти\n• Ризик: помірний (99% SLI)",
                     size=11, bold=True, fill="#fff3e0", stroke="#e67e22", min_w=170))

    frags.append(box(630, y_boxes, "3. Stable (Стабільний)\n• Реліз раз на 4-6 тижнів\n• Масовий парк пристроїв\n• Ризик: мінімальний (99.95%)",
                     size=11, bold=True, fill="#e8f0ff", stroke=NEG, min_w=170))

    frags.append(box(890, y_boxes, "4. LTS (Довготривалий)\n• Цикл 1-3 роки\n• Промислові об'єкти\n• Лише патчі безпеки",
                     size=11, bold=True, fill="#eafaf0", stroke=FIELD, min_w=170))

    # Шлюзи просування (Gates) під лініями
    y_gate = 300

    frags.append(box(240, y_gate, "Шлюз 1 (Trunk → Beta)\n• 100% проходження тестів\n• Відсутність збоїв збірки\n• Статичний аналіз і ASan",
                     size=10, fill="#fdf6e3", stroke="#d35400", min_w=160))

    frags.append(box(500, y_gate, "Шлюз 2 (Beta → Stable)\n• Вікно витримування ≥ 14 днів\n• Crash-free rate ≥ 99.95%\n• Нуль регресій затримки/пам'яті",
                     size=10, fill="#eaf0fd", stroke=NEG, min_w=170))

    frags.append(box(760, y_gate, "Шлюз 3 (Stable → LTS)\n• Кваліфікація в бойових умовах\n• Заморозка API/ABI\n• Підпис кворумом ключів HSM",
                     size=10, fill="#eafaf0", stroke=FIELD, min_w=170))

    # Стрілки між каналами
    frags.append(arrow(200, y_boxes, 280, y_boxes, color=LINE, sw=2))
    frags.append(arrow(460, y_boxes, 540, y_boxes, color=LINE, sw=2))
    frags.append(arrow(720, y_boxes, 800, y_boxes, color=LINE, sw=2))

    # Пунктирні стрілки до шлюзів
    frags.append(line(240, y_boxes, 240, y_gate - 32, color=MUTED, sw=1.5, dash="4 3"))
    frags.append(line(500, y_boxes, 500, y_gate - 32, color=MUTED, sw=1.5, dash="4 3"))
    frags.append(line(760, y_boxes, 760, y_gate - 32, color=MUTED, sw=1.5, dash="4 3"))

    # Позначення незмінного артефакту
    frags.append(box(W / 2, 40, "Єдиний незмінний бінарний артефакт: SHA-256 не перекомпільовується при переході між каналами",
                     size=12, bold=True, fill="#f4f6f8", stroke=INK, pad=8))

    frags.append(text(W / 2, H - 20,
                      "Просування бінарника крізь канали гарантує поступове зниження ентропії та захист масового парку.",
                      size=12, color=MUTED))

    render(os.path.join(IMG, 'channel-promotion-pipeline.svg'), W, H, *frags,
           title="Конвеєр просування артефакту крізь канали")


# ── Фігура 2: Сегментація парку пристроїв ─────────────────────────────────────
def fig_fleet_segmentation():
    W, H = 960, 440
    frags = []

    y = 160

    # 4 когорти
    frags.append(box(125, y, "Nightly (~0.5% парку)\n\n• Розробники ядра\n• Лабораторія HIL-тестів\n• Експериментальні стенди\n\nТолерантність: критичні збої",
                     size=11, bold=True, fill="#fdecea", stroke=POS, min_w=190))

    frags.append(box(355, y, "Beta (~5% парку)\n\n• Early adopters і співробітники\n• Пілотні об'єкти партнерів\n• Нечутливі до збоїв вузли\n\nТолерантність: окремі баги",
                     size=11, bold=True, fill="#fff3e0", stroke="#e67e22", min_w=190))

    frags.append(box(595, y, "Stable (~85% парку)\n\n• Кінцеві споживачі\n• Основна комерційна мережа\n• Виробничі сервери\n\nТолерантність: нульова",
                     size=11, bold=True, fill="#e8f0ff", stroke=NEG, min_w=200))

    frags.append(box(835, y, "LTS (~9.5% парку)\n\n• Енергопідстанції та лікарні\n• Авіоніка та регульовані вузли\n• Air-gapped середовища\n\nТолерантність: абсолютний нуль",
                     size=11, bold=True, fill="#eafaf0", stroke=FIELD, min_w=200))

    # Стрілка наростання вимог стабільності
    y_arrow = 330
    frags.append(arrow(60, y_arrow, 900, y_arrow, color=INK, sw=2.5))
    frags.append(box(W / 2, y_arrow, "Напрямок зростання ціни збою та вимог до надійності (SLO)",
                     size=11, bold=True, fill="#ffffff", stroke=INK, pad=6))

    # Верхній опис
    frags.append(box(W / 2, 45, "Сегментація парку пристроїв: мінімізація радіуса ураження через диверсифікацію ризику",
                     size=13, bold=True, fill="#f4f6f8", stroke=LINE, pad=7))

    frags.append(text(W / 2, H - 20,
                      "Чим вища критичність вузла, тим довша затримка оновлення і жорсткіші критерії стабільності.",
                      size=12, color=MUTED))

    render(os.path.join(IMG, 'fleet-channel-segmentation.svg'), W, H, *frags,
           title="Сегментація парку пристроїв за каналами оновлення")


# ── Фігура 3: Протокол взаємодії пристрою з сервером конфігурацій ─────────────
def fig_subscription_handshake():
    W, H = 960, 480
    frags = []

    # Колонка клієнта і сервера
    x_client = 200
    x_server = 760

    frags.append(box(x_client, 50, "Клієнтський пристрій\n(Daemon / Agent)", size=13, bold=True, fill="#e8f0ff", stroke=NEG, min_w=220))
    frags.append(box(x_server, 50, "Сервер конфігурацій\n(OTA / Config Server)", size=13, bold=True, fill="#eafaf0", stroke=FIELD, min_w=220))

    # Вертикальні лінії життя
    frags.append(line(x_client, 85, x_client, 410, color=MUTED, sw=1.5, dash="5 4"))
    frags.append(line(x_server, 85, x_server, 410, color=MUTED, sw=1.5, dash="5 4"))

    # Крок 1: Запит оновлення
    y1 = 130
    frags.append(arrow(x_client, y1, x_server, y1, color=LINE, sw=1.8))
    frags.append(box((x_client + x_server) / 2, y1 - 18, "1. POST /v1/update-check {board_rev: \"v2.1\", channel: \"beta\", token: \"...\"}",
                     size=10, fill="#ffffff", stroke=LINE, pad=4))

    # Крок 2: Обробка сервером
    y2 = 195
    frags.append(box(x_server + 80, y2, "2. Валідація токена,\nпошук релізу каналу beta,\nгенерація маніфесту",
                     size=10, fill="#fdf6e3", stroke="#d35400", min_w=150))

    # Крок 3: Відповідь з маніфестом
    y3 = 265
    frags.append(arrow(x_server, y3, x_client, y3, color=LINE, sw=1.8))
    frags.append(box((x_client + x_server) / 2, y3 - 18, "3. 200 OK {version: \"2.4.0-beta.2\", sha256: \"...\", sig: \"Ed25519...\"}",
                     size=10, fill="#ffffff", stroke=LINE, pad=4))

    # Крок 4: Перевірка підпису та встановлення
    y4 = 345
    frags.append(box(x_client - 80, y4, "4. Перевірка підпису ключем Beta,\nзапис у пасивний A/B банк,\nфіксація успішного буту",
                     size=10, fill="#e8f0ff", stroke=NEG, min_w=160))

    frags.append(text(W / 2, H - 20,
                      "Протокол гарантує криптографічну автентичність артефакту та захист від підміни каналу.",
                      size=12, color=MUTED))

    render(os.path.join(IMG, 'channel-subscription-handshake.svg'), W, H, *frags,
           title="Протокол опитування та підписки на канали оновлення")


# ── Фігура 4: Захист промислового контуру від нічних бінарників ────────────────
def fig_industrial_airgap():
    W, H = 980, 480
    frags = []

    y = 200

    # 4 бар'єри захисту
    frags.append(box(130, y, "1. Зовнішня зона\n(Public Cloud)\n\n• Nightly / Beta / Stable\n• Автоматичний CI/CD\n• Відкриті мережі",
                     size=11, bold=True, fill="#fdecea", stroke=POS, min_w=170))

    frags.append(box(370, y, "2. Ключова ізоляція\n(HSM Key Rings)\n\n• Nightly: CI ключ\n• Beta: Dev ключ\n• LTS: Кворум HSM 3-з-5",
                     size=11, bold=True, fill="#fff3e0", stroke="#e67e22", min_w=170))

    frags.append(box(610, y, "3. Шлюз безпеки\n(Air-Gap Gateway)\n\n• Whitelist лише LTS\n• Блокування URL Nightly\n• Дезінфекція маніфестів",
                     size=11, bold=True, fill="#eaf0fd", stroke=NEG, min_w=170))

    frags.append(box(850, y, "4. Промисловий вузол\n(Hardware Lock)\n\n• eFuse апаратний ключ\n• Захист BootROM\n• Відхилення не-LTS бінарників",
                     size=11, bold=True, fill="#eafaf0", stroke=FIELD, min_w=170))

    # Стрілки між бар'єрами
    frags.append(arrow(220, y, 280, y, color=LINE, sw=2))
    frags.append(arrow(460, y, 520, y, color=LINE, sw=2))
    frags.append(arrow(700, y, 760, y, color=LINE, sw=2))

    # Нижня стрілка: рівні захисту
    y_bot = 370
    frags.append(box(W / 2, y_bot, "Ешелонована оборона: навіть при компрометації сервера OTA залізо відкине нічну збірку",
                     size=12, bold=True, fill="#f4f6f8", stroke=INK, pad=8))

    frags.append(box(W / 2, 45, "Архітектура багаторівневого захисту промислового контуру від нестабільних релізів",
                     size=13, bold=True, fill="#ffffff", stroke=LINE, pad=7))

    frags.append(text(W / 2, H - 20,
                      "Апаратні ф'юзи та кворумні криптографічні підписи унеможливлюють випадковий апдейт промисловості.",
                      size=12, color=MUTED))

    render(os.path.join(IMG, 'industrial-airgap-protection.svg'), W, H, *frags,
           title="Захист промислового контуру від потрапляння нічних бінарників")


if __name__ == '__main__':
    fig_channel_promotion_pipeline()
    fig_fleet_segmentation()
    fig_subscription_handshake()
    fig_industrial_airgap()
    print("All figures generated successfully.")
