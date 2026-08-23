# -*- coding: utf-8 -*-
"""Фігури для розбору 73-годинного збою Roblox (guide progarch / observability-and-operations / rozbir-roblox-73h).
Вивід — ./img/*.svg. svgkit імпортуємо, не переписуємо."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

COLOR_DANGER = "#e74c3c"
COLOR_WARN = "#f39c12"
COLOR_SAFE = "#2ecc71"
COLOR_INFO = "#3498db"
COLOR_BG_CARD = "#f8f9fa"


def fig_cascade_timeline():
    """Хронологія каскадного колапсу 73-годинного збою Roblox."""
    W, H = 940, 520
    els = []

    els.append(text(W / 2, 30, "Хронологія каскадного колапсу Roblox (28–31 жовтня 2021 року)", size=16, bold=True))

    steps = [
        ("15:00 PDT (0 год)", "Увімкнення Consul Streaming", "Активація прапорця стримінгу викликала масове зростання записів у KV-сховище", COLOR_INFO),
        ("+15 хв (0.25 год)", "Пастка Freelist у BoltDB", "Розростання списку вільних сторінок. Сортування O(N log N) блокує записи", COLOR_DANGER),
        ("+1 год", "Чехарда лідерів Raft", "Лідер запізнюється з серцебиттям через блокування BoltDB. Кластер зациклюється у виборах", COLOR_DANGER),
        ("+2 год", "Осліплення телеметрії", "Prometheus та Grafana втрачають Service Discovery. Інженери потрапляють у сліпу зону", COLOR_WARN),
        ("+4–30 год", "Метастабільний шторм", "18 000 агентів без джиттера безперервно штормлять відновлювані сервери", COLOR_DANGER),
        ("+30–73 год", "Офлайн-ремонт та шлюз", "Офлайн-компактизація BoltDB, мережевий шлюз допуску та покрокове повернення трафіку", COLOR_SAFE)
    ]

    x0 = 80
    y_start = 75
    step_y = 68

    # Центральна лінія часу
    els.append(line(x0, y_start, x0, y_start + (len(steps) - 1) * step_y, color=LINE, sw=3))

    for i, (time_label, title, desc, col) in enumerate(steps):
        cy = y_start + i * step_y
        els.append(circle(x0, cy, 10, fill=col, stroke=BG, sw=2))

        # Часова мітка ліворуч
        els.append(text(x0 - 18, cy + 5, time_label, size=12, bold=True, color=INK, anchor="end"))

        # Картка події праворуч
        card_x = x0 + 25
        card_w = 780
        card_h = 52

        els.append(rect(card_x, cy - 24, card_w, card_h, fill=COLOR_BG_CARD, stroke=col, sw=1.5, rx=6))
        els.append(text(card_x + 15, cy - 5, title, size=13.5, bold=True, color=INK, anchor="start"))
        els.append(text(card_x + 15, cy + 15, desc, size=12, color=MUTED, anchor="start"))

    els.append(text(W / 2, H - 15, "Загальний час відновлення платформи — 73 години", size=12.5, italic=True, color=MUTED))
    render(os.path.join(IMG, "cascade-timeline.svg"), W, H, *els)


def fig_boltdb_freelist_stall():
    """СхемаCopy-on-Write у BoltDB та виникнення заторів у Freelist."""
    W, H = 940, 480
    els = []

    els.append(text(W / 2, 28, "Механіка Copy-on-Write у BoltDB та блокування на Freelist", size=16, bold=True))

    # Секція 1: B+ tree Copy-on-Write
    els.append(rect(30, 50, 420, 380, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    els.append(text(240, 78, "1. Каскадне Copy-on-Write оновлення", size=14, bold=True, color=INK))

    els.append(fitbox(170, 105, 140, 42, "Корінь (Root Meta)", size=12.5, fill="#ebf5fb", stroke=COLOR_INFO, sw=1.5))
    els.append(fitbox(80, 185, 130, 40, "Гілка P_parent\n(Стара сторінка)", size=11.5, fill="#f9ebd2", stroke=COLOR_WARN, sw=1.5))
    els.append(fitbox(260, 185, 140, 40, "Гілка P_parent2\n(Нова CoW сторінка)", size=11.5, fill="#e8f8f5", stroke=COLOR_SAFE, sw=1.5))

    els.append(fitbox(50, 275, 120, 38, "Лист P1 (Старий)", size=11.5, fill="#f9ebd2", stroke=COLOR_WARN, sw=1.5))
    els.append(fitbox(200, 275, 120, 38, "Лист P2 (Новий)", size=11.5, fill="#e8f8f5", stroke=COLOR_SAFE, sw=1.5))

    els.append(arrow(240, 147, 145, 185, color=LINE, sw=1.5))
    els.append(arrow(240, 147, 330, 185, color=COLOR_SAFE, sw=1.8))
    els.append(arrow(145, 225, 110, 275, color=LINE, sw=1.5))
    els.append(arrow(330, 225, 260, 275, color=COLOR_SAFE, sw=1.8))

    els.append(text(240, 355, "Старі сторінки (P1, P_parent) не перезаписуються,", size=12, color=MUTED))
    els.append(text(240, 375, "а відправляються у Freelist Pending Queue", size=12, color=MUTED))

    # Секція 2: Freelist Bottleneck
    els.append(rect(480, 50, 430, 380, fill="#fdfefe", stroke=COLOR_DANGER, sw=1.5, rx=8))
    els.append(text(695, 78, "2. Ботлнек Freelist під час коміту", size=14, bold=True, color=COLOR_DANGER))

    els.append(fitbox(510, 110, 370, 48, "Ексклюзивне блокування metalock.Lock()\n(Лише один потік запису)", size=12, fill="#fadbd8", stroke=COLOR_DANGER, sw=2, bold=True))

    els.append(fitbox(510, 190, 370, 52, "Зріз pending []pgid → ids []pgid\nМільйони ідентифікаторів у пам'яті", size=12, fill=COLOR_BG_CARD, stroke=LINE, sw=1.5))

    els.append(fitbox(510, 270, 370, 52, "Сортування sort.Sort(pgids)\nСкладність O(N log N) → Затримка 5-10 сек!", size=12, fill="#fadbd8", stroke=COLOR_DANGER, sw=2, bold=True))

    els.append(arrow(695, 158, 695, 190, color=COLOR_DANGER, sw=2))
    els.append(arrow(695, 242, 695, 270, color=COLOR_DANGER, sw=2))

    els.append(text(695, 360, "Потік Raft коміту зависає у сортуванні freelist.", size=12, bold=True, color=COLOR_DANGER))
    els.append(text(695, 380, "Лідер втрачає серцебиття → Вибори", size=12, bold=True, color=COLOR_DANGER))

    render(os.path.join(IMG, "boltdb-freelist-stall.svg"), W, H, *els)


def fig_metastable_feedback_loop():
    """Петля зворотного зв'язку метастабільної відмови (Metastable Failure State)."""
    W, H = 940, 460
    els = []

    els.append(text(W / 2, 28, "Петля зворотного зв'язку метастабільного шторму повторів", size=16, bold=True))

    nodes = [
        (470, 80, "Вимкнення прапорця стримінгу\n(Первинну причину усунуто)", COLOR_SAFE),
        (760, 200, "18 000 агентів Consul\nодночасно роблять Re-register", COLOR_DANGER),
        (620, 360, "Шторм запитів підключається\nдо новообраного лідера Raft", COLOR_DANGER),
        (320, 360, "Блокування BoltDB / GC\nЛідер втрачає серцебиття", COLOR_DANGER),
        (180, 200, "Таймаут фоловерів →\nПовалення лідера та нові вибори", COLOR_DANGER)
    ]

    for x, y, label, col in nodes:
        els.append(fitbox(x - 120, y - 30, 240, 60, label, size=12.5, fill="#fff", stroke=col, sw=2, bold=True))

    # Стрілки кільцевого циклу
    els.append(arrow(350, 95, 650, 180, color=COLOR_SAFE, sw=2))
    els.append(arrow(760, 235, 660, 325, color=COLOR_DANGER, sw=2))
    els.append(arrow(500, 360, 440, 360, color=COLOR_DANGER, sw=2))
    els.append(arrow(220, 325, 180, 235, color=COLOR_DANGER, sw=2))
    els.append(arrow(200, 165, 340, 95, color=COLOR_DANGER, sw=2))

    els.append(text(W / 2, H - 20, "Система самостійно підтримує свій колапс через навантаження повторних спроб без джиттера", size=12.5, italic=True, color=MUTED))
    render(os.path.join(IMG, "metastable-feedback-loop.svg"), W, H, *els)


def fig_staged_ingress_gate():
    """Схема покрокового відновлення трафіку (Staged Admission Gate)."""
    W, H = 940, 440
    els = []

    els.append(text(W / 2, 28, "Архітектура покрокового відновлення (Staged Admission Gate)", size=16, bold=True))

    # Джерело шторму
    els.append(fitbox(40, 160, 160, 100, "18 000 Агентів\nConsul\n(Повторні спроби)", size=13, fill="#fadbd8", stroke=COLOR_DANGER, sw=2, bold=True))

    # Мережевий шлюз / Шлюз допуску
    els.append(rect(240, 100, 220, 220, fill="#fef9e7", stroke=COLOR_WARN, sw=2, rx=8))
    els.append(text(350, 125, "Шлюз допуску", size=14, bold=True, color=COLOR_WARN))
    els.append(text(350, 145, "(iptables / Rate-Limiter)", size=12, color=MUTED))

    els.append(fitbox(260, 175, 180, 45, "Відкидання 99% трафіку\n(Drop / Rate Limit)", size=11.5, fill="#f5b7b1", stroke=COLOR_DANGER, sw=1.5))
    els.append(fitbox(260, 245, 180, 45, "Покроковий допуск\n(1% → 5% → 25% → 100%)", size=11.5, fill="#abebc6", stroke=COLOR_SAFE, sw=1.5))

    # Кластер Consul
    els.append(rect(520, 100, 170, 220, fill="#ebf5fb", stroke=COLOR_INFO, sw=2, rx=8))
    els.append(text(605, 130, "Ядро Consul", size=14, bold=True, color=COLOR_INFO))
    els.append(fitbox(535, 160, 140, 40, "Стабільний лідер", size=12, fill="#fff", stroke=COLOR_INFO, sw=1.5))
    els.append(fitbox(535, 215, 140, 40, "Оновлений BoltDB", size=12, fill="#fff", stroke=COLOR_INFO, sw=1.5))
    els.append(fitbox(535, 270, 140, 40, "Raft Heartbeats OK", size=12, fill="#fff", stroke=COLOR_SAFE, sw=1.5))

    # Сервісний шар Roblox
    els.append(rect(730, 100, 170, 220, fill="#e8f8f5", stroke=COLOR_SAFE, sw=2, rx=8))
    els.append(text(815, 130, "Сервіси Roblox", size=14, bold=True, color=COLOR_SAFE))
    els.append(text(815, 160, "Ярус 1: Auth/KV", size=11.5, color=INK))
    els.append(text(815, 190, "Ярус 2: Data Stores", size=11.5, color=INK))
    els.append(text(815, 220, "Ярус 3: Matchmaking", size=11.5, color=INK))
    els.append(text(815, 250, "Ярус 4: Game Engines", size=11.5, color=INK))

    els.append(arrow(200, 210, 240, 210, color=COLOR_DANGER, sw=2))
    els.append(arrow(460, 267, 520, 267, color=COLOR_SAFE, sw=2))
    els.append(arrow(690, 210, 730, 210, color=COLOR_SAFE, sw=2))

    els.append(text(W / 2, H - 20, "Керований допуск дозволяє зберегти стабільність Raft під час розігріву сервісів", size=12.5, italic=True, color=MUTED))
    render(os.path.join(IMG, "staged-ingress-gate.svg"), W, H, *els)


if __name__ == "__main__":
    fig_cascade_timeline()
    fig_boltdb_freelist_stall()
    fig_metastable_feedback_loop()
    fig_staged_ingress_gate()
    print("Всі 4 фігури успішно згенеровано у ./img/")
