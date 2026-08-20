#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор архітектурних схем для теми distributed-caching-architectures."""

import os
import sys

# Підключаємо svgkit з кореня репо (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def fig_topologies():
    """Порівняння трьох архітектурних топологій кешування: In-process, Remote Distributed та Near-Cache."""
    w, h = 960, 480
    body = []
    
    # 3 великі панелі для трьох топологій
    col_w = 290
    gap = 25
    x_start = 25
    
    # Панель 1: In-Process (Локальний)
    x1 = x_start
    body.append(rect(x1, 20, col_w, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    body.append(textbox(x1 + col_w/2, 45, "1. Локальний (In-Process)", size=14, bold=True, color="#0f172a", fill="#e2e8f0")[0])
    
    # Вузол Додатка 1
    body.append(rect(x1 + 20, 80, col_w - 40, 110, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    body.append(text(x1 + col_w/2, 105, "Екземпляр Сервісу А", size=13, bold=True, color=INK))
    body.append(rect(x1 + 35, 120, col_w - 70, 55, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    body.append(text(x1 + col_w/2, 142, "Вбудований кеш (L1)", size=12, bold=True, color=POS))
    body.append(text(x1 + col_w/2, 160, "RAM процесу (~20-50 нс)", size=11, color=MUTED))
    
    # Вузол Додатка 2
    body.append(rect(x1 + 20, 210, col_w - 40, 110, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    body.append(text(x1 + col_w/2, 235, "Екземпляр Сервісу B", size=13, bold=True, color=INK))
    body.append(rect(x1 + 35, 250, col_w - 70, 55, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    body.append(text(x1 + col_w/2, 272, "Вбудований кеш (L1)", size=12, bold=True, color=POS))
    body.append(text(x1 + col_w/2, 290, "RAM процесу (~20-50 нс)", size=11, color=MUTED))
    
    # Властивості панелі 1
    body.append(rect(x1 + 15, 340, col_w - 30, 105, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
    body.append(text(x1 + 25, 362, "• Затримка: ультранизька", size=11, anchor="start", bold=True, color=FIELD))
    body.append(text(x1 + 25, 382, "• Дублювання даних у RAM", size=11, anchor="start", color=POS))
    body.append(text(x1 + 25, 402, "• Розсинхронізація станів", size=11, anchor="start", color=POS))
    body.append(text(x1 + 25, 422, "• Холодний старт при деплої", size=11, anchor="start", color=MUTED))
    
    # Панель 2: Distributed Remote Cache
    x2 = x1 + col_w + gap
    body.append(rect(x2, 20, col_w, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    body.append(textbox(x2 + col_w/2, 45, "2. Віддалений (Distributed)", size=14, bold=True, color="#0f172a", fill="#e2e8f0")[0])
    
    # Додатки без локального кешу
    body.append(rect(x2 + 20, 80, int((col_w-50)/2), 60, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    body.append(text(x2 + 20 + int((col_w-50)/4), 115, "Сервіс A", size=12, bold=True, color=INK))
    
    body.append(rect(x2 + 30 + int((col_w-50)/2), 80, int((col_w-50)/2), 60, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    body.append(text(x2 + 30 + 3*int((col_w-50)/4), 115, "Сервіс B", size=12, bold=True, color=INK))
    
    # Стрілки мережевого виклику
    body.append(arrow(x2 + 20 + int((col_w-50)/4), 145, x2 + 75, 195, color=NEG, sw=1.5))
    body.append(arrow(x2 + 30 + 3*int((col_w-50)/4), 145, x2 + col_w - 75, 195, color=NEG, sw=1.5))
    body.append(text(x2 + col_w/2, 170, "Мережа: TCP / RTT ~1-2 мс", size=11, color=NEG, bold=True))
    
    # Кластер віддаленого кешу
    body.append(rect(x2 + 15, 200, col_w - 30, 120, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    body.append(text(x2 + col_w/2, 222, "Розподілений кластер (L2)", size=12, bold=True, color=NEG))
    body.append(rect(x2 + 25, 235, 75, 45, fill="#ffffff", stroke=NEG, sw=1, rx=4))
    body.append(text(x2 + 62, 260, "Шард 1", size=11, color=INK))
    body.append(rect(x2 + 107, 235, 75, 45, fill="#ffffff", stroke=NEG, sw=1, rx=4))
    body.append(text(x2 + 144, 260, "Шард 2", size=11, color=INK))
    body.append(rect(x2 + 190, 235, 75, 45, fill="#ffffff", stroke=NEG, sw=1, rx=4))
    body.append(text(x2 + 227, 260, "Шард 3", size=11, color=INK))
    body.append(text(x2 + col_w/2, 305, "Єдине джерело правди", size=11, color=MUTED))
    
    # Властивості панелі 2
    body.append(rect(x2 + 15, 340, col_w - 30, 105, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
    body.append(text(x2 + 25, 362, "• Узгодженість для всіх вузлів", size=11, anchor="start", bold=True, color=FIELD))
    body.append(text(x2 + 25, 382, "• Масштабування обсягу RAM", size=11, anchor="start", color=FIELD))
    body.append(text(x2 + 25, 402, "• Витрати на серіалізацію", size=11, anchor="start", color=POS))
    body.append(text(x2 + 25, 422, "• Мережева затримка (RTT)", size=11, anchor="start", color=POS))
    
    # Панель 3: Дворівневий Near-Cache
    x3 = x2 + col_w + gap
    body.append(rect(x3, 20, col_w, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    body.append(textbox(x3 + col_w/2, 45, "3. Гібридний (Near-Cache)", size=14, bold=True, color="#0f172a", fill="#e2e8f0")[0])
    
    # Вузол сервісу з L1
    body.append(rect(x3 + 20, 80, col_w - 40, 95, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    body.append(text(x3 + col_w/2, 100, "Сервіс із L1 Near-Cache", size=12, bold=True, color=INK))
    body.append(rect(x3 + 30, 112, col_w - 60, 50, fill="#fef3c7", stroke="#d97706", sw=1, rx=4))
    body.append(text(x3 + col_w/2, 130, "L1 Локальний кеш", size=11, bold=True, color="#b45309"))
    body.append(text(x3 + col_w/2, 148, "Гарячі ключі (Tracking)", size=10, color=MUTED))
    
    # Шина інвалідації
    body.append(line(x3 + 40, 185, x3 + col_w - 40, 185, color="#d97706", sw=1.5, dash="4,3"))
    body.append(text(x3 + col_w/2, 200, "Шина інвалідації (Pub/Sub / RESP3)", size=10, color="#b45309", bold=True))
    
    # Кластер L2
    body.append(rect(x3 + 20, 220, col_w - 40, 100, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    body.append(text(x3 + col_w/2, 242, "L2 Спільний кластер", size=12, bold=True, color=NEG))
    body.append(text(x3 + col_w/2, 265, "Повний обсяг даних", size=11, color=MUTED))
    body.append(text(x3 + col_w/2, 285, "Синхронізація інвалідацій", size=11, color=MUTED))
    body.append(arrow(x3 + col_w/2, 175, x3 + col_w/2, 215, color=NEG, sw=1.5))
    
    # Властивості панелі 3
    body.append(rect(x3 + 15, 340, col_w - 30, 105, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
    body.append(text(x3 + 25, 362, "• Швидкість L1 + Ємність L2", size=11, anchor="start", bold=True, color=FIELD))
    body.append(text(x3 + 25, 382, "• Захист від гарячих ключів", size=11, anchor="start", color=FIELD))
    body.append(text(x3 + 25, 402, "• Складність інвалідації L1", size=11, anchor="start", color=POS))
    body.append(text(x3 + 25, 422, "• Ризик штормів анулювання", size=11, anchor="start", color=POS))
    
    render(os.path.join(IMG_DIR, 'cache-topologies-comparison.svg'), w, h, *body)

def fig_consistent_hashing():
    """Кільце узгодженого гешування (Consistent Hashing Ring) з віртуальними вузлами."""
    w, h = 900, 520
    body = []
    
    # Заголовок
    body.append(textbox(w/2, 30, "Кільце узгодженого гешування: простір 2³²-1 та віртуальні вузли", size=15, bold=True, fill="#f1f5f9")[0])
    
    # Центр кільця
    cx, cy, r = 380, 270, 180
    
    # Коло кільця
    body.append(circle(cx, cy, r, fill="none", stroke="#94a3b8", sw=3))
    
    # Стрілка напрямку обходу (за годинниковою стрілкою)
    body.append(text(cx, cy - 20, "Простір хешів", size=14, bold=True, color="#475569"))
    body.append(text(cx, cy + 5, "[0 ... 2³² - 1]", size=12, color=MUTED))
    body.append(text(cx, cy + 30, "↻ Рух за годинниковою", size=12, bold=True, color=NEG))
    
    import math
    
    def pt(deg, radius=r):
        rad = math.radians(deg - 90)
        return cx + radius * math.cos(rad), cy + radius * math.sin(rad)
    
    # Вузли
    nodes = [
        (0, "A#1", POS), (45, "B#1", NEG), (90, "C#1", FIELD),
        (135, "A#2", POS), (180, "B#2", NEG), (225, "C#2", FIELD),
        (270, "A#3", POS), (315, "B#3", NEG)
    ]
    
    for deg, label, col in nodes:
        nx, ny = pt(deg)
        body.append(circle(nx, ny, 16, fill="#ffffff", stroke=col, sw=2.5))
        body.append(text(nx, ny + 4, label, size=10, bold=True, color=col))
    
    # Ключі даних K1, K2, K3
    keys = [
        (25, "Ключ 1", "B#1", NEG),
        (70, "Ключ 2", "C#1", FIELD),
        (110, "Ключ 3", "A#2", POS),
        (250, "Ключ 4", "A#3", POS)
    ]
    
    for deg, klabel, target, col in keys:
        kx, ky = pt(deg, r - 35)
        body.append(circle(kx, ky, 8, fill=col, stroke="#ffffff", sw=1.5))
        tx, ty = pt(deg, r - 58)
        body.append(text(tx, ty, klabel, size=11, bold=True, color=INK))
        nx, ny = pt(deg)
        body.append(line(kx, ky, nx, ny, color=col, sw=1.5, dash="2,2"))
    
    # Новий вузол D, що додається на 200 градусів
    dx, dy = pt(200)
    body.append(circle(dx, dy, 18, fill="#fef3c7", stroke="#d97706", sw=2.5))
    body.append(text(dx, dy + 4, "D#1", size=10, bold=True, color="#b45309"))
    
    body.append(text(dx + 35, dy - 20, "Новий вузол D", size=11, bold=True, color="#b45309"))
    body.append(text(dx + 35, dy - 5, "Перехоплює лише дугу C#2 ➔ D", size=10, color=MUTED))
    
    # Легенда праворуч
    lx = 660
    body.append(rect(lx, 70, 220, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    body.append(text(lx + 110, 95, "Принцип розподілу", size=13, bold=True, color=INK))
    
    body.append(circle(lx + 25, 130, 8, fill=POS, stroke=POS, sw=1))
    body.append(text(lx + 40, 134, "Фізичний сервер A (A#1..3)", size=11, anchor="start", color=INK))
    
    body.append(circle(lx + 25, 160, 8, fill=NEG, stroke=NEG, sw=1))
    body.append(text(lx + 40, 164, "Фізичний сервер B (B#1..3)", size=11, anchor="start", color=INK))
    
    body.append(circle(lx + 25, 190, 8, fill=FIELD, stroke=FIELD, sw=1))
    body.append(text(lx + 40, 194, "Фізичний сервер C (C#1..3)", size=11, anchor="start", color=INK))
    
    body.append(circle(lx + 25, 220, 8, fill="#d97706", stroke="#d97706", sw=1))
    body.append(text(lx + 40, 224, "Новий сервер D (D#1)", size=11, anchor="start", color=INK))
    
    body.append(line(lx + 15, 245, lx + 205, 245, color="#e2e8f0", sw=1))
    
    body.append(text(lx + 20, 270, "1. Маршрутизація ключа:", size=11, anchor="start", bold=True, color=INK))
    body.append(text(lx + 20, 290, "   hash(key) ➔ позиція", size=11, anchor="start", color=MUTED))
    body.append(text(lx + 20, 310, "   Рух за годинниковою ➔ вузол", size=11, anchor="start", color=MUTED))
    
    body.append(text(lx + 20, 345, "2. Масштабування (N+1):", size=11, anchor="start", bold=True, color=INK))
    body.append(text(lx + 20, 365, "   Мігрує лише K/N ключів", size=11, anchor="start", color=FIELD, bold=True))
    body.append(text(lx + 20, 385, "   (в modulo мігрувало б ~100%)", size=10, anchor="start", color=POS))
    
    body.append(text(lx + 20, 420, "3. Віртуальні вузли (vnodes):", size=11, anchor="start", bold=True, color=INK))
    body.append(text(lx + 20, 440, "   Усувають дисбаланс часток", size=11, anchor="start", color=MUTED))
    body.append(text(lx + 20, 460, "   і гарячі точки на кільці", size=11, anchor="start", color=MUTED))
    
    render(os.path.join(IMG_DIR, 'consistent-hashing-ring.svg'), w, h, *body)

def fig_access_patterns():
    """Патерни доступу до кешу: Cache-Aside, Write-Through, Write-Behind."""
    w, h = 960, 490
    body = []
    
    # 3 колонки для трьох патернів
    col_w = 290
    gap = 25
    x_start = 25
    
    # 1. Cache-Aside (Lazy Loading)
    x1 = x_start
    body.append(rect(x1, 20, col_w, 450, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    body.append(textbox(x1 + col_w/2, 45, "1. Cache-Aside (Осторонь)", size=14, bold=True, color="#0f172a", fill="#e2e8f0")[0])
    
    body.append(rect(x1 + 20, 80, col_w - 40, 45, fill="#ffffff", stroke="#64748b", sw=1.5, rx=4))
    body.append(text(x1 + col_w/2, 107, "Застосунок (Клієнт)", size=12, bold=True, color=INK))
    
    body.append(rect(x1 + 20, 185, col_w - 40, 45, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    body.append(text(x1 + col_w/2, 212, "Розподілений Кеш", size=12, bold=True, color=POS))
    
    body.append(rect(x1 + 20, 290, col_w - 40, 45, fill="#eff6ff", stroke=NEG, sw=1.5, rx=4))
    body.append(text(x1 + col_w/2, 317, "База даних (СУБД)", size=12, bold=True, color=NEG))
    
    # Стрілки Cache-Aside
    body.append(arrow(x1 + 70, 125, x1 + 70, 185, color=POS, sw=1.5))
    body.append(text(x1 + 55, 155, "1. Get", size=10, bold=True, color=POS))
    
    body.append(arrow(x1 + col_w - 70, 125, x1 + col_w - 70, 290, color=NEG, sw=1.5))
    body.append(text(x1 + col_w - 50, 170, "2. Miss: SQL", size=10, bold=True, color=NEG))
    
    body.append(arrow(x1 + col_w - 90, 125, x1 + col_w - 90, 185, color=FIELD, sw=1.5))
    body.append(text(x1 + col_w - 115, 155, "3. Set", size=10, bold=True, color=FIELD))
    
    body.append(rect(x1 + 15, 355, col_w - 30, 95, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
    body.append(text(x1 + 25, 375, "• Кешуються лише запитані дані", size=10, anchor="start", color=FIELD))
    body.append(text(x1 + 25, 395, "• При записі: оновлення БД", size=10, anchor="start", color=INK))
    body.append(text(x1 + 25, 415, "  і видалення (Delete) з кешу", size=10, anchor="start", bold=True, color=POS))
    body.append(text(x1 + 25, 435, "• Стійкість до падіння кешу", size=10, anchor="start", color=MUTED))
    
    # 2. Write-Through (Наскрізний запис)
    x2 = x1 + col_w + gap
    body.append(rect(x2, 20, col_w, 450, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    body.append(textbox(x2 + col_w/2, 45, "2. Write-Through (Наскрізний)", size=14, bold=True, color="#0f172a", fill="#e2e8f0")[0])
    
    body.append(rect(x2 + 20, 80, col_w - 40, 45, fill="#ffffff", stroke="#64748b", sw=1.5, rx=4))
    body.append(text(x2 + col_w/2, 107, "Застосунок (Клієнт)", size=12, bold=True, color=INK))
    
    body.append(rect(x2 + 20, 185, col_w - 40, 45, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    body.append(text(x2 + col_w/2, 212, "Кеш-Шлюз (Inline)", size=12, bold=True, color=POS))
    
    body.append(rect(x2 + 20, 290, col_w - 40, 45, fill="#eff6ff", stroke=NEG, sw=1.5, rx=4))
    body.append(text(x2 + col_w/2, 317, "База даних (СУБД)", size=12, bold=True, color=NEG))
    
    body.append(arrow(x2 + col_w/2, 125, x2 + col_w/2, 185, color=POS, sw=1.5))
    body.append(text(x2 + col_w/2 + 35, 155, "1. Write(K,V)", size=10, bold=True, color=POS))
    
    body.append(arrow(x2 + col_w/2, 230, x2 + col_w/2, 290, color=NEG, sw=1.5))
    body.append(text(x2 + col_w/2 + 50, 260, "2. Синхронний Save", size=10, bold=True, color=NEG))
    
    body.append(rect(x2 + 15, 355, col_w - 30, 95, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
    body.append(text(x2 + 25, 375, "• Дані в кеші завжди свіжі", size=10, anchor="start", color=FIELD))
    body.append(text(x2 + 25, 395, "• Кеш сам пише у СУБД", size=10, anchor="start", color=INK))
    body.append(text(x2 + 25, 415, "• Висока затримка запису (RTT)", size=10, anchor="start", color=POS))
    body.append(text(x2 + 25, 435, "• Засмічення рідкісними даними", size=10, anchor="start", color=MUTED))
    
    # 3. Write-Behind (Асинхронний запис)
    x3 = x2 + col_w + gap
    body.append(rect(x3, 20, col_w, 450, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    body.append(textbox(x3 + col_w/2, 45, "3. Write-Behind (Асинхронний)", size=14, bold=True, color="#0f172a", fill="#e2e8f0")[0])
    
    body.append(rect(x3 + 20, 80, col_w - 40, 45, fill="#ffffff", stroke="#64748b", sw=1.5, rx=4))
    body.append(text(x3 + col_w/2, 107, "Застосунок (Клієнт)", size=12, bold=True, color=INK))
    
    body.append(rect(x3 + 20, 185, col_w - 40, 45, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    body.append(text(x3 + col_w/2, 205, "Кеш + Черга змін", size=12, bold=True, color=POS))
    body.append(text(x3 + col_w/2, 222, "[Dirty Queue]", size=10, color=MUTED))
    
    body.append(rect(x3 + 20, 290, col_w - 40, 45, fill="#eff6ff", stroke=NEG, sw=1.5, rx=4))
    body.append(text(x3 + col_w/2, 317, "База даних (СУБД)", size=12, bold=True, color=NEG))
    
    body.append(arrow(x3 + 60, 125, x3 + 60, 185, color=POS, sw=1.5))
    body.append(text(x3 + 45, 155, "1. Write", size=10, bold=True, color=POS))
    
    body.append(arrow(x3 + 120, 185, x3 + 120, 125, color=FIELD, sw=1.5))
    body.append(text(x3 + 145, 155, "2. Ack (швидко)", size=10, bold=True, color=FIELD))
    
    body.append(line(x3 + col_w/2, 230, x3 + col_w/2, 290, color=NEG, sw=1.5, dash="3,3"))
    body.append(text(x3 + col_w/2 + 55, 260, "3. Асинхронний батч", size=10, bold=True, color="#d97706"))
    
    body.append(rect(x3 + 15, 355, col_w - 30, 95, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
    body.append(text(x3 + 25, 375, "• Максимальна швидкість запису", size=10, anchor="start", color=FIELD))
    body.append(text(x3 + 25, 395, "• Злиття частих оновлень (Batch)", size=10, anchor="start", color=FIELD))
    body.append(text(x3 + 25, 415, "• Ризик втрати даних при збої", size=10, anchor="start", bold=True, color=POS))
    body.append(text(x3 + 25, 435, "• Складність відновлення черги", size=10, anchor="start", color=MUTED))
    
    render(os.path.join(IMG_DIR, 'cache-access-patterns-flow.svg'), w, h, *body)

def fig_resiliency_modes():
    """Відмовні режими розподіленого кешу: Avalanche, Stampede, Penetration та їх усунення."""
    w, h = 960, 480
    body = []
    
    # 3 панелі
    col_w = 290
    gap = 25
    x_start = 25
    
    # 1. Cache Avalanche (Лавина)
    x1 = x_start
    body.append(rect(x1, 20, col_w, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    body.append(textbox(x1 + col_w/2, 45, "Лавина кешу (Avalanche)", size=13, bold=True, color="#0f172a", fill="#fee2e2")[0])
    
    body.append(text(x1 + col_w/2, 85, "Проблема: Одночасний TTL", size=11, bold=True, color=POS))
    body.append(rect(x1 + 20, 100, col_w - 40, 70, fill="#ffffff", stroke=POS, sw=1, rx=4))
    body.append(text(x1 + col_w/2, 122, "100 000 ключів вичерпують", size=10, color=INK))
    body.append(text(x1 + col_w/2, 140, "TTL в одну й ту ж секунду", size=10, bold=True, color=POS))
    body.append(text(x1 + col_w/2, 158, "➔ Масовий промах ➔ Краш СУБД", size=10, color=POS))
    
    body.append(arrow(x1 + col_w/2, 180, x1 + col_w/2, 220, color=FIELD, sw=2))
    body.append(text(x1 + col_w/2 + 45, 202, "Захист", size=11, bold=True, color=FIELD))
    
    body.append(rect(x1 + 20, 230, col_w - 40, 100, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=4))
    body.append(text(x1 + col_w/2, 252, "TTL Jitter (Рандомізація)", size=11, bold=True, color=FIELD))
    body.append(text(x1 + col_w/2, 275, "TTL_fact = TTL + rand(0, Δ)", size=11, bold=True, color=INK))
    body.append(text(x1 + col_w/2, 298, "Розмиття піку в часі", size=10, color=MUTED))
    body.append(text(x1 + col_w/2, 316, "+ Дворівневий прогрів кешу", size=10, color=MUTED))
    
    body.append(rect(x1 + 15, 350, col_w - 30, 95, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
    body.append(text(x1 + 25, 372, "• Девіація TTL: 10-20%", size=10, anchor="start", color=INK))
    body.append(text(x1 + 25, 392, "• Плавне вимивання ключів", size=10, anchor="start", color=FIELD))
    body.append(text(x1 + 25, 412, "• Захист пулу коннектів БД", size=10, anchor="start", color=FIELD))
    body.append(text(x1 + 25, 432, "• Плавний рестарт кластера", size=10, anchor="start", color=MUTED))
    
    # 2. Cache Stampede (Навала за ключем)
    x2 = x1 + col_w + gap
    body.append(rect(x2, 20, col_w, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    body.append(textbox(x2 + col_w/2, 45, "Навала запитів (Stampede)", size=13, bold=True, color="#0f172a", fill="#fee2e2")[0])
    
    body.append(text(x2 + col_w/2, 85, "Проблема: Гарячий промах", size=11, bold=True, color=POS))
    body.append(rect(x2 + 20, 100, col_w - 40, 70, fill="#ffffff", stroke=POS, sw=1, rx=4))
    body.append(text(x2 + col_w/2, 122, "1 суперпопулярний ключ щез", size=10, color=INK))
    body.append(text(x2 + col_w/2, 140, "50 000 паралельних воркерів", size=10, bold=True, color=POS))
    body.append(text(x2 + col_w/2, 158, "одночасно роблять важкий SQL", size=10, color=POS))
    
    body.append(arrow(x2 + col_w/2, 180, x2 + col_w/2, 220, color=FIELD, sw=2))
    body.append(text(x2 + col_w/2 + 45, 202, "Захист", size=11, bold=True, color=FIELD))
    
    body.append(rect(x2 + 20, 230, col_w - 40, 100, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=4))
    body.append(text(x2 + col_w/2, 252, "Singleflight / XFetch", size=11, bold=True, color=FIELD))
    body.append(text(x2 + col_w/2, 275, "М'ютекс злиття запитів", size=11, bold=True, color=INK))
    body.append(text(x2 + col_w/2, 298, "Лише 1 запит іде в СУБД,", size=10, color=MUTED))
    body.append(text(x2 + col_w/2, 316, "інші 49 999 чекають на результат", size=10, color=FIELD))
    
    body.append(rect(x2 + 15, 350, col_w - 30, 95, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
    body.append(text(x2 + 25, 372, "• Блокування на рівні клієнта", size=10, anchor="start", color=INK))
    body.append(text(x2 + 25, 392, "• Ймовірнісне раннє оновлення", size=10, anchor="start", color=FIELD))
    body.append(text(x2 + 25, 412, "• Алгоритм XFetch (Vattani)", size=10, anchor="start", color=FIELD))
    body.append(text(x2 + 25, 432, "• 0 дублюючих запитів у БД", size=10, anchor="start", color=MUTED))
    
    # 3. Cache Penetration (Пробиття)
    x3 = x2 + col_w + gap
    body.append(rect(x3, 20, col_w, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    body.append(textbox(x3 + col_w/2, 45, "Пробиття (Penetration)", size=13, bold=True, color="#0f172a", fill="#fee2e2")[0])
    
    body.append(text(x3 + col_w/2, 85, "Проблема: Неіснуючі ключі", size=11, bold=True, color=POS))
    body.append(rect(x3 + 20, 100, col_w - 40, 70, fill="#ffffff", stroke=POS, sw=1, rx=4))
    body.append(text(x3 + col_w/2, 122, "Запити ID = -9999 / UUID_rnd", size=10, color=INK))
    body.append(text(x3 + col_w/2, 140, "Даних нема ні в кеші, ні в БД", size=10, bold=True, color=POS))
    body.append(text(x3 + col_w/2, 158, "➔ 100% запитів б'ють у диск", size=10, color=POS))
    
    body.append(arrow(x3 + col_w/2, 180, x3 + col_w/2, 220, color=FIELD, sw=2))
    body.append(text(x3 + col_w/2 + 45, 202, "Захист", size=11, bold=True, color=FIELD))
    
    body.append(rect(x3 + 20, 230, col_w - 40, 100, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=4))
    body.append(text(x3 + col_w/2, 252, "Фільтр Блума / Null-кеш", size=11, bold=True, color=FIELD))
    body.append(text(x3 + col_w/2, 275, "Відсікання на вході", size=11, bold=True, color=INK))
    body.append(text(x3 + col_w/2, 298, "Кешування NULL на 30-60 с", size=10, color=MUTED))
    body.append(text(x3 + col_w/2, 316, "Швидкий відбій без звернення в БД", size=10, color=FIELD))
    
    body.append(rect(x3 + 15, 350, col_w - 30, 95, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
    body.append(text(x3 + 25, 372, "• Bloom Filter у RAM процесу", size=10, anchor="start", color=INK))
    body.append(text(x3 + 25, 392, "• O(1) перевірка існування ID", size=10, anchor="start", color=FIELD))
    body.append(text(x3 + 25, 412, "• Захист від сканувань і атак", size=10, anchor="start", color=FIELD))
    body.append(text(x3 + 25, 432, "• Нульове навантаження на СУБД", size=10, anchor="start", color=MUTED))
    
    render(os.path.join(IMG_DIR, 'resiliency-failure-modes.svg'), w, h, *body)

def fig_redis_cluster():
    """Топологія Redis Cluster: 16384 хеш-слоти, пряма маршрутизація та MOVED/ASK редиректи."""
    w, h = 960, 500
    body = []
    
    # Заголовок
    body.append(textbox(w/2, 30, "Маршрутизація в Redis Cluster: 16 384 слоти, Gossip та редиректи MOVED / ASK", size=14, bold=True, fill="#f1f5f9")[0])
    
    # Розумний клієнт зліва
    cx = 120
    body.append(rect(cx - 80, 100, 160, 280, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    body.append(text(cx, 125, "Smart Client", size=13, bold=True, color=INK))
    body.append(text(cx, 145, "(Драйвер додатка)", size=11, color=MUTED))
    
    body.append(rect(cx - 70, 170, 140, 80, fill="#ffffff", stroke="#94a3b8", sw=1, rx=4))
    body.append(text(cx, 190, "Локальна таблиця", size=11, bold=True, color=INK))
    body.append(text(cx, 208, "слотів (Slot Map):", size=10, color=MUTED))
    body.append(text(cx, 226, "0..5460 ➔ Node 1", size=10, color=NEG))
    body.append(text(cx, 242, "5461..10922 ➔ Node 2", size=10, color=FIELD))
    
    body.append(rect(cx - 70, 270, 140, 95, fill="#eff6ff", stroke=NEG, sw=1, rx=4))
    body.append(text(cx, 290, "Обчислення слота:", size=11, bold=True, color=NEG))
    body.append(text(cx, 310, "CRC16(key) % 16384", size=11, bold=True, color=INK))
    body.append(text(cx, 330, "➔ Прямий сокет", size=10, color=MUTED))
    body.append(text(cx, 348, "до потрібного вузла", size=10, color=MUTED))
    
    # 3 мастер-вузли кластера
    nx = 480
    
    # Node 1
    body.append(rect(nx, 80, 200, 95, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    body.append(text(nx + 100, 105, "Master Node 1", size=13, bold=True, color=NEG))
    body.append(text(nx + 100, 128, "Слоти: 0 ... 5 460", size=11, bold=True, color=INK))
    body.append(text(nx + 100, 150, "TCP: 6379 (Client) | 16379 (Bus)", size=10, color=MUTED))
    
    # Node 2
    body.append(rect(nx, 200, 200, 95, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    body.append(text(nx + 100, 225, "Master Node 2", size=13, bold=True, color=FIELD))
    body.append(text(nx + 100, 248, "Слоти: 5 461 ... 10 922", size=11, bold=True, color=INK))
    body.append(text(nx + 100, 270, "TCP: 6379 (Client) | 16379 (Bus)", size=10, color=MUTED))
    
    # Node 3 (В процесі міграції слота 12000)
    body.append(rect(nx, 320, 200, 95, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    body.append(text(nx + 100, 345, "Master Node 3", size=13, bold=True, color=POS))
    body.append(text(nx + 100, 368, "Слоти: 10 923 ... 16 383", size=11, bold=True, color=INK))
    body.append(text(nx + 100, 390, "Міграція слота 12000 ➔ Node 2", size=10, color=POS, bold=True))
    
    # Gossip Bus між вузлами
    body.append(line(nx + 200, 130, nx + 230, 130, color="#94a3b8", sw=1.5))
    body.append(line(nx + 230, 130, nx + 230, 370, color="#94a3b8", sw=1.5))
    body.append(line(nx + 200, 370, nx + 230, 370, color="#94a3b8", sw=1.5))
    body.append(line(nx + 200, 250, nx + 230, 250, color="#94a3b8", sw=1.5))
    body.append(text(nx + 240, 250, "Gossip Protocol (Cluster Bus)", size=10, anchor="start", color="#64748b", bold=True))
    
    # Стрілки запитів від клієнта
    body.append(arrow(cx + 80, 180, nx - 10, 120, color=FIELD, sw=2))
    body.append(text(300, 135, "1. GET user:100 (Слот 3500) ➔ OK", size=11, bold=True, color=FIELD))
    
    body.append(arrow(cx + 80, 220, nx - 10, 240, color=NEG, sw=1.5))
    body.append(line(nx - 10, 260, cx + 80, 260, color=POS, sw=1.5, dash="3,3"))
    body.append(text(300, 275, "2. Відповідь: -MOVED 12000 10.0.0.3", size=10, bold=True, color=POS))
    
    # Панель редиректів праворуч
    rx = 740
    body.append(rect(rx, 80, 200, 335, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    body.append(text(rx + 100, 105, "Протокол редиректів", size=12, bold=True, color=INK))
    
    body.append(text(rx + 15, 135, "• MOVED <slot> <ip:port>", size=11, anchor="start", bold=True, color=POS))
    body.append(text(rx + 15, 155, "  Постійне переміщення.", size=10, anchor="start", color=MUTED))
    body.append(text(rx + 15, 175, "  Клієнт оновлює свою", size=10, anchor="start", color=MUTED))
    body.append(text(rx + 15, 195, "  карту слотів (Slot Map).", size=10, anchor="start", color=MUTED))
    
    body.append(line(rx + 10, 215, rx + 190, 215, color="#e2e8f0", sw=1))
    
    body.append(text(rx + 15, 240, "• ASK <slot> <ip:port>", size=11, anchor="start", bold=True, color="#d97706"))
    body.append(text(rx + 15, 260, "  Тимчасовий стан під час", size=10, anchor="start", color=MUTED))
    body.append(text(rx + 15, 280, "  міграції слота.", size=10, anchor="start", color=MUTED))
    body.append(text(rx + 15, 300, "  Клієнт відсилає ASKING", size=10, anchor="start", color=MUTED))
    body.append(text(rx + 15, 320, "  і НЕ оновлює Slot Map.", size=10, anchor="start", color=MUTED))
    
    body.append(text(rx + 15, 355, "• Hash Tags: {user:123}.cart", size=10, anchor="start", bold=True, color=FIELD))
    body.append(text(rx + 15, 375, "  Гешується лише вміст {}", size=10, anchor="start", color=MUTED))
    body.append(text(rx + 15, 395, "  ➔ ко-локація на одному шарді", size=10, anchor="start", color=FIELD))
    
    # Нижня плашка
    body.append(rect(20, 430, 920, 50, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=6))
    body.append(text(w/2, 460, "Redis Cluster не використовує централізований координатор (ZooKeeper/Etcd) — стан кластера підтримується через децентралізований Gossip-протокол", size=11, color="#334155", bold=True))
    
    render(os.path.join(IMG_DIR, 'redis-cluster-slot-routing.svg'), w, h, *body)

def main():
    fig_topologies()
    fig_consistent_hashing()
    fig_access_patterns()
    fig_resiliency_modes()
    fig_redis_cluster()
    print("All 5 figures generated successfully in img/")

if __name__ == '__main__':
    main()
