# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. token-bucket-mechanics: Механіка накопичувача маркерів (Token Bucket) ─
def fig_token_bucket():
    W, H = 760, 320
    p = []

    # Генератор маркерів зверху
    p.append(rect(230, 20, 300, 50, fill="#f8fafc", stroke=INK, sw=1.6, rx=6))
    p.append(text(380, 42, "Генератор маркерів (поповнення)", size=12, color=INK, bold=True))
    p.append(text(380, 60, "Швидкість поповнення: r маркерів/сек", size=11, color=FIELD, bold=True))

    # Стрілка надходження маркерів у відро
    p.append(arrow(380, 70, 380, 105, color=FIELD, sw=2))

    # Накопичувач (Відро)
    p.append(rect(250, 110, 260, 130, fill="#f0f9ff", stroke=LINE, sw=2, rx=8))
    p.append(text(380, 132, "Накопичувач (Bucket)", size=13, color=INK, bold=True))
    p.append(text(380, 150, "Максимальна місткість: C маркерів", size=10, color=MUTED))

    # Візуалізація наявних маркерів всередині
    for i in range(4):
        p.append(rect(275 + i * 55, 170, 45, 26, fill="#27ae60", stroke="#1e8449", sw=1.2, rx=4))
        p.append(text(297 + i * 55, 187, "Токен", size=10, color="#ffffff", bold=True))
    p.append(text(380, 222, "Поточний запас: T(t) маркерів", size=11, color=FIELD, bold=True))

    # Скидання надлишку (якщо T > C)
    p.append(arrow(510, 140, 640, 140, color=MUTED, sw=1.5))
    p.append(text(645, 135, "Надлишок маркерів", size=10, color=MUTED, anchor="start"))
    p.append(text(645, 150, "скидається (Overflow)", size=10, color=MUTED, anchor="start"))

    # Вхідний запит (ліворуч)
    p.append(rect(30, 140, 150, 65, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    p.append(text(105, 163, "Вхідний запит", size=12, color=INK, bold=True))
    p.append(text(105, 185, "Потребує 1 токен", size=10, color=MUTED))
    p.append(arrow(180, 172, 245, 172, color=INK, sw=2))

    # Рішення внизу
    p.append(line(380, 240, 380, 265, color=LINE, sw=1.8))

    # Гілка успіху (зелена)
    p.append(arrow(380, 265, 170, 265, color=FIELD, sw=2))
    p.append(rect(30, 240, 135, 50, fill="#e8f8f0", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(97, 260, "T ≥ 1: Пропустити", size=11, color=FIELD, bold=True))
    p.append(text(97, 278, "T ← T - 1 (OK)", size=10, color=INK))

    # Гілка відхилення (червона)
    p.append(arrow(380, 265, 590, 265, color=POS, sw=2))
    p.append(rect(595, 240, 135, 50, fill="#fdf2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(662, 260, "T < 1: Відхилити", size=11, color=POS, bold=True))
    p.append(text(662, 278, "HTTP 429 Too Many", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "token-bucket-mechanics.svg"), W, H, *p,
           title="Механіка алгоритму Token Bucket")


# ── 2. leaky-bucket-shaping: Діряве відро як шейпер трафіку ─────────────────
def fig_leaky_bucket():
    W, H = 760, 310
    p = []

    # Вхідний нерівномірний трафік (ліворуч)
    p.append(rect(30, 45, 170, 75, fill="#fef9e7", stroke="#d4ac0d", sw=1.5, rx=6))
    p.append(text(115, 68, "Нерівномірний трафік", size=12, color=INK, bold=True))
    p.append(text(115, 88, "Пакети надходять пачками", size=10, color=MUTED))
    p.append(text(115, 105, "Піки (Bursts) > r", size=10, color=POS, bold=True))

    p.append(arrow(200, 82, 265, 82, color=LINE, sw=2))

    # Відро / Черга (Буфер)
    p.append(rect(270, 30, 220, 180, fill="#f0f4f8", stroke=LINE, sw=2, rx=8))
    p.append(text(380, 52, "Черга / Буфер (Queue)", size=13, color=INK, bold=True))
    p.append(text(380, 70, "Максимальний розмір: B пакетів", size=10, color=MUTED))

    # Елементи в буфері
    for i in range(3):
        p.append(rect(295, 95 + i * 28, 170, 22, fill="#e2e8f0", stroke="#94a3b8", sw=1.2, rx=4))
        p.append(text(380, 110 + i * 28, f"Запит #{3-i} у черзі", size=10, color=INK))

    # Переповнення черги (Overflow)
    p.append(arrow(490, 80, 580, 80, color=POS, sw=2))
    p.append(rect(585, 55, 145, 50, fill="#fdf2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(657, 75, "Черга повна (Q > B)", size=11, color=POS, bold=True))
    p.append(text(657, 92, "Скидання запиту (Drop)", size=10, color=POS))

    # Витік із дна відра
    p.append(arrow(380, 210, 380, 255, color=FIELD, sw=2.2))
    p.append(text(395, 235, "Витік", size=11, color=FIELD, bold=True, anchor="start"))

    # Вихідний згладжений потік
    p.append(rect(200, 255, 360, 45, fill="#e8f8f0", stroke=FIELD, sw=1.6, rx=6))
    p.append(text(380, 274, "Згладжений стабільний вихідний потік", size=12, color=FIELD, bold=True))
    p.append(text(380, 290, "Постійна швидкість витоку: r_out запитів/сек", size=10, color=INK))

    render(os.path.join(OUT, "leaky-bucket-shaping.svg"), W, H, *p,
           title="Діряве відро (Leaky Bucket) для згладжування трафіку")


# ── 3. fixed-vs-sliding-window: Вразливість фіксованого вікна та ковзне вікно
def fig_fixed_vs_sliding():
    W, H = 760, 310
    p = []

    # Верхня панель: Фіксоване вікно
    p.append(rect(30, 20, 700, 125, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(50, 42, "Фіксоване вікно (Fixed Window) — Ліміт: 100 зап/хв", size=12, color=POS, bold=True, anchor="start"))

    # Вісь часу для фіксованого вікна
    p.append(arrow(60, 105, 680, 105, color=LINE, sw=1.8))
    p.append(line(240, 75, 240, 115, color=MUTED, sw=1.5))
    p.append(line(460, 75, 460, 115, color=POS, sw=2))
    p.append(line(660, 75, 660, 115, color=MUTED, sw=1.5))

    p.append(text(240, 128, "00:00:00", size=10, color=MUTED))
    p.append(text(460, 128, "00:01:00 (Межа скидання)", size=10, color=POS, bold=True))
    p.append(text(660, 128, "00:02:00", size=10, color=MUTED))

    # Сплески трафіку на межі вікна
    p.append(rect(370, 60, 85, 38, fill="#fadbd8", stroke=POS, sw=1.2, rx=4))
    p.append(text(412, 76, "100 запитів", size=10, color=POS, bold=True))
    p.append(text(412, 90, "в кінці хвилини", size=9, color=INK))

    p.append(rect(465, 60, 85, 38, fill="#fadbd8", stroke=POS, sw=1.2, rx=4))
    p.append(text(507, 76, "100 запитів", size=10, color=POS, bold=True))
    p.append(text(507, 90, "на початку нової", size=9, color=INK))

    p.append(text(595, 42, "200 запитів за 20 секунд!", size=11, color=POS, bold=True))

    # Нижня панель: Ковзне вікно (Sliding Window Counter)
    p.append(rect(30, 160, 700, 135, fill="#e8f8f0", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(50, 182, "Ковзне вікно (Sliding Window Counter) — Зважена оцінка", size=12, color=FIELD, bold=True, anchor="start"))

    p.append(arrow(60, 245, 680, 245, color=LINE, sw=1.8))
    p.append(line(220, 220, 220, 255, color=MUTED, sw=1.5))
    p.append(line(460, 220, 460, 255, color=MUTED, sw=1.5))

    # Рамка ковзного вікна
    p.append(rect(310, 215, 240, 50, fill="#d1f2eb", stroke=FIELD, sw=2, rx=6))
    p.append(text(430, 203, "Поточне ковзне вікно тривалістю 60 с", size=10, color=FIELD, bold=True))

    p.append(text(380, 280, "Формула: Count = N_попереднє · (1 - t/W) + N_поточне", size=11, color=INK, bold=True))
    p.append(text(620, 280, "Помилка < 1-2%", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "fixed-vs-sliding-window.svg"), W, H, *p,
           title="Порівняння фіксованого та ковзного вікон")


# ── 4. gcra-tat-timeline: Алгоритм GCRA та теоретичний час прибуття (TAT) ────
def fig_gcra_tat():
    W, H = 760, 280
    p = []

    # Вісь часу
    p.append(arrow(40, 90, 715, 90, color=LINE, sw=2))
    p.append(text(710, 115, "Час (t)", size=11, color=MUTED, anchor="end"))

    # Маркери на шкалі
    p.append(line(160, 75, 160, 105, color=LINE, sw=1.5))
    p.append(text(160, 120, "t₁ (Запит 1)", size=11, color=INK, bold=True))

    p.append(line(360, 75, 360, 105, color=FIELD, sw=2))
    p.append(text(360, 120, "TAT (Очікуваний час)", size=11, color=FIELD, bold=True))

    # Зона допуску сплеску (Limit Tolerance tau)
    p.append(rect(240, 55, 120, 30, fill="#d1f2eb", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(300, 74, "Допуск сплеску (τ)", size=10, color=FIELD, bold=True))

    # Границя відхилення: TAT - tau
    p.append(line(240, 45, 240, 105, color=POS, sw=2, dash="3,2"))
    p.append(text(240, 38, "TAT - τ", size=11, color=POS, bold=True))

    # Зона неприпустимого раннього прибуття (Reject)
    p.append(text(140, 60, "Зона відхилення (t < TAT - τ)", size=10, color=POS, bold=True))

    # Оновлення TAT при успішному проходженні
    p.append(rect(460, 140, 260, 110, fill="#f8fafc", stroke=INK, sw=1.5, rx=8))
    p.append(text(590, 165, "Правило оновлення GCRA:", size=12, color=INK, bold=True))
    p.append(text(590, 188, "Якщо t ≥ TAT - τ: ПРИЙНЯТИ", size=11, color=FIELD, bold=True))
    p.append(text(590, 208, "TAT_новий = max(t, TAT) + T", size=11, color=INK))
    p.append(text(590, 230, "Інакше: ВІДХИЛИТИ (без зміни TAT)", size=11, color=POS, bold=True))

    # Опис параметрів ліворуч
    p.append(rect(40, 140, 390, 110, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    p.append(text(235, 165, "Параметри віртуального планувальника:", size=12, color=INK, bold=True))
    p.append(text(235, 188, "• T = 1 / r — інтервал між запитами при стабільній швидкості", size=10, color=INK))
    p.append(text(235, 208, "• τ (tau) — часовий ліміт сплеску (Burst Tolerance)", size=10, color=INK))
    p.append(text(235, 230, "• Пам'ять: рівно 1 число (64-бітне значення TAT) на ключ!", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "gcra-tat-timeline.svg"), W, H, *p,
           title="Часова шкала алгоритму GCRA (Generic Cell Rate Algorithm)")


# ── 5. distributed-redis-limiter: Архітектура розподіленого обмеження швидкості
def fig_distributed_limiter():
    W, H = 760, 320
    p = []

    # Клієнти
    p.append(rect(20, 110, 110, 90, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    p.append(text(75, 135, "Клієнти", size=12, color=INK, bold=True))
    p.append(text(75, 155, "Мобільні апки", size=9, color=MUTED))
    p.append(text(75, 172, "Браузери, боти", size=9, color=MUTED))
    p.append(text(75, 188, "Хмарні сервіси", size=9, color=MUTED))

    p.append(arrow(135, 155, 185, 155, color=LINE, sw=2))

    # Шлюз / API Gateways (Балансувальник)
    p.append(rect(190, 35, 230, 245, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    p.append(text(305, 60, "API Gateways / Вузли кластера", size=12, color=INK, bold=True))

    for i in range(3):
        p.append(rect(205, 80 + i * 58, 200, 48, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
        p.append(text(305, 100 + i * 58, f"Gateway Вузол #{i+1}", size=11, color=INK, bold=True))
        p.append(text(305, 118 + i * 58, "Без локального стану або кеш", size=9, color=MUTED))

    # Стрілки між Gateway та Redis
    p.append(arrow(425, 140, 505, 140, color=FIELD, sw=2))
    p.append(arrow(505, 170, 425, 170, color=FIELD, sw=2))
    p.append(text(465, 130, "EVALSHA", size=9, color=FIELD, bold=True))
    p.append(text(465, 190, "OK / 429", size=9, color=FIELD, bold=True))

    # Спільний стан: Redis Cluster
    p.append(rect(510, 55, 225, 205, fill="#f0f9ff", stroke=FIELD, sw=2, rx=8))
    p.append(text(622, 82, "Центральний Redis Cluster", size=12, color=INK, bold=True))
    p.append(text(622, 102, "Атомарний стан лімітерів", size=10, color=FIELD, bold=True))

    p.append(rect(525, 118, 195, 40, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(622, 135, "Lua-скрипт (Token Bucket)", size=10, color=INK, bold=True))
    p.append(text(622, 149, "1 RTT, без race condition", size=9, color=MUTED))

    p.append(rect(525, 168, 195, 40, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(622, 185, "Ключ: rate:{user_id}", size=10, color=INK, bold=True))
    p.append(text(622, 199, "Хеш: tokens + last_updated", size=9, color=MUTED))

    p.append(text(622, 240, "TTL: автоочищення пам'яті", size=10, color=MUTED))

    # Резервний режим знизу
    p.append(rect(20, 285, 715, 30, fill="#fff8e1", stroke="#f57f17", sw=1.2, rx=4))
    p.append(text(377, 305, "Резервний режим (Fallback): при недоступності Redis вузли переходять на локальний In-Memory Bucket", size=10, color="#f57f17", bold=True))

    render(os.path.join(OUT, "distributed-redis-limiter.svg"), W, H, *p,
           title="Розподілена архітектура обмеження швидкості з Redis")


if __name__ == "__main__":
    fig_token_bucket()
    fig_leaky_bucket()
    fig_fixed_vs_sliding()
    fig_gcra_tat()
    fig_distributed_limiter()
    print("All figures generated successfully.")
