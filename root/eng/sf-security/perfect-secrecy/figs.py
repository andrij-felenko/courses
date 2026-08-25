# -*- coding: utf-8 -*-
"""Генератор фігур для теми «Досконала таємність Шеннона»."""

import os
import sys

# Підключення svgkit із кореня репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

# ── 1. shannon-secrecy-prob.svg ──────────────────────────────────────────────
def fig_shannon_secrecy_prob():
    W, H = 760, 360
    frags = []

    # Заголовок блоку 1: Досконала таємність
    b1_title, _, _ = textbox(190, 30, "Досконала таємність Шеннона", size=13, bold=True, fill="#e8f4fd", stroke="#2457d6")
    frags.append(b1_title)

    # Розподіли для досконалої таємниці
    frags.append(text(190, 75, "Апріорний розподіл P(M = m)", size=12, bold=True, color=INK))
    
    # Гістограма апріорна (Досконала)
    # m1
    frags.append(rect(50, 95, 120, 24, fill="#3b82f6", stroke="#1d4ed8", sw=1, rx=3))
    frags.append(text(110, 111, "m₁: P = 0.70", size=11, bold=True, color="#ffffff"))
    # m2
    frags.append(rect(180, 95, 60, 24, fill="#93c5fd", stroke="#1d4ed8", sw=1, rx=3))
    frags.append(text(210, 111, "m₂: 0.30", size=11, bold=True, color=INK))

    frags.append(arrow(190, 123, 190, 145, color="#2457d6", sw=1.8))
    b_ev, _, _ = textbox(190, 160, "Перехоплено шифротекст c", size=11, pad=6, fill="#ffffff", stroke="#2457d6")
    frags.append(b_ev)
    frags.append(arrow(190, 175, 190, 197, color="#2457d6", sw=1.8))

    frags.append(text(190, 215, "Апостеріорний розподіл P(M = m | C = c)", size=12, bold=True, color=INK))
    
    # Гістограма апостеріорна (Досконала) - тотожна!
    frags.append(rect(50, 235, 120, 24, fill="#3b82f6", stroke="#1d4ed8", sw=1, rx=3))
    frags.append(text(110, 251, "m₁: P = 0.70", size=11, bold=True, color="#ffffff"))
    frags.append(rect(180, 235, 60, 24, fill="#93c5fd", stroke="#1d4ed8", sw=1, rx=3))
    frags.append(text(210, 251, "m₂: 0.30", size=11, bold=True, color=INK))

    b_res1, _, _ = textbox(190, 305, "P(M = m | C = c) = P(M = m)\nНуль витоку інформації про повідомлення", size=11, pad=8, fill="#eafaf1", stroke="#27ae60", color="#1e8449", bold=True)
    frags.append(b_res1)

    # Розділювач
    frags.append(line(380, 20, 380, 340, color="#d1d5db", sw=1.5, dash="4 4"))

    # Заголовок блоку 2: Звичайний шифр / недосконалий
    b2_title, _, _ = textbox(570, 30, "Недосконалий / обчислювальний шифр", size=13, bold=True, fill="#fdedec", stroke="#c0392b")
    frags.append(b2_title)

    frags.append(text(570, 75, "Апріорний розподіл P(M = m)", size=12, bold=True, color=INK))
    
    # Гістограма апріорна (Звичайна)
    frags.append(rect(430, 95, 120, 24, fill="#3b82f6", stroke="#1d4ed8", sw=1, rx=3))
    frags.append(text(490, 111, "m₁: P = 0.70", size=11, bold=True, color="#ffffff"))
    frags.append(rect(560, 95, 60, 24, fill="#93c5fd", stroke="#1d4ed8", sw=1, rx=3))
    frags.append(text(590, 111, "m₂: 0.30", size=11, bold=True, color=INK))

    frags.append(arrow(570, 123, 570, 145, color="#c0392b", sw=1.8))
    b_ev2, _, _ = textbox(570, 160, "Перехоплено шифротекст c", size=11, pad=6, fill="#ffffff", stroke="#c0392b")
    frags.append(b_ev2)
    frags.append(arrow(570, 175, 570, 197, color="#c0392b", sw=1.8))

    frags.append(text(570, 215, "Апостеріорний розподіл P(M = m | C = c)", size=12, bold=True, color=INK))
    
    # Гістограма апостеріорна (Звичайна) - зміщена!
    frags.append(rect(430, 235, 16, 24, fill="#cbd5e1", stroke="#64748b", sw=1, rx=3))
    frags.append(text(438, 251, "0.05", size=9, bold=True, color=INK))
    frags.append(rect(455, 235, 190, 24, fill="#ef4444", stroke="#b91c1c", sw=1, rx=3))
    frags.append(text(550, 251, "m₂: P = 0.95 (витік структури)", size=11, bold=True, color="#ffffff"))

    b_res2, _, _ = textbox(570, 305, "P(M = m | C = c) ≠ P(M = m)\nШифротекст видає ймовірне повідомлення", size=11, pad=8, fill="#fdecea", stroke="#c0392b", color="#922b21", bold=True)
    frags.append(b_res2)

    render(os.path.join(OUT, "shannon-secrecy-prob.svg"), W, H, *frags)


# ── 2. otp-keyspace-mapping.svg ──────────────────────────────────────────────
def fig_otp_keyspace_mapping():
    W, H = 760, 370
    frags = []

    # Ліва колонка: Повідомлення M
    frags.append(text(120, 35, "Простір повідомлень M", size=13, bold=True, color=INK))
    bm1, _, _ = textbox(120, 85, "m₁ = 00", size=12, bold=True, pad=8, fill="#e8f4fd", stroke="#2457d6")
    bm2, _, _ = textbox(120, 155, "m₂ = 01", size=12, bold=True, pad=8, fill="#e8f4fd", stroke="#2457d6")
    bm3, _, _ = textbox(120, 225, "m₃ = 10", size=12, bold=True, pad=8, fill="#e8f4fd", stroke="#2457d6")
    bm4, _, _ = textbox(120, 295, "m₄ = 11", size=12, bold=True, pad=8, fill="#e8f4fd", stroke="#2457d6")
    frags.extend([bm1, bm2, bm3, bm4])

    # Права колонка: Шифротекст C (фіксований c = 10)
    frags.append(text(640, 35, "Шифротекст c", size=13, bold=True, color=INK))
    bc, _, _ = textbox(640, 190, "c = 10", size=14, bold=True, pad=12, fill="#fef3c7", stroke="#d97706")
    frags.append(bc)

    # Зв'язки ключів K
    # m1 (00) -> c (10) via k = 10
    frags.append(arrow(180, 85, 580, 175, color="#16a34a", sw=1.8))
    bk1, _, _ = textbox(370, 105, "Ключ k₁ = 10  (P = 1/4)", size=10, pad=4, fill="#ffffff", stroke="#16a34a")
    frags.append(bk1)

    # m2 (01) -> c (10) via k = 11
    frags.append(arrow(180, 155, 580, 185, color="#2563eb", sw=1.8))
    bk2, _, _ = textbox(370, 155, "Ключ k₂ = 11  (P = 1/4)", size=10, pad=4, fill="#ffffff", stroke="#2563eb")
    frags.append(bk2)

    # m3 (10) -> c (10) via k = 00
    frags.append(arrow(180, 225, 580, 195, color="#9333ea", sw=1.8))
    bk3, _, _ = textbox(370, 205, "Ключ k₃ = 00  (P = 1/4)", size=10, pad=4, fill="#ffffff", stroke="#9333ea")
    frags.append(bk3)

    # m4 (11) -> c (10) via k = 01
    frags.append(arrow(180, 295, 580, 205, color="#ea580c", sw=1.8))
    bk4, _, _ = textbox(370, 255, "Ключ k₄ = 01  (P = 1/4)", size=10, pad=4, fill="#ffffff", stroke="#ea580c")
    frags.append(bk4)

    # Висновок унизу
    b_bot, _, _ = textbox(380, 335, "Для будь-якого шифротексту c КОЖНЕ повідомлення m породжує c рівно з одним ключем k.\nОскільки всі 4 ключі рівноймовірні (P = 1/4), кожен відкритий текст однаково правдоподібний.", size=11, pad=8, fill="#f4f6f8", stroke="#6b7280", bold=False)
    frags.append(b_bot)

    render(os.path.join(OUT, "otp-keyspace-mapping.svg"), W, H, *frags)


# ── 3. two-time-pad-leak.svg ────────────────────────────────────────────────
def fig_two_time_pad_leak():
    W, H = 760, 380
    frags = []

    # Верхній блок: Повідомлення 1
    bm1, _, _ = textbox(130, 60, "Повідомлення M₁\n«ATTACK_AT_DAWN»", size=11, bold=True, pad=8, fill="#e8f4fd", stroke="#2457d6")
    bk1, _, _ = textbox(330, 60, "Спільний ключ K\n(випадковий потік)", size=11, bold=True, pad=8, fill="#fef3c7", stroke="#d97706")
    bc1, _, _ = textbox(570, 60, "Шифротекст C₁\nC₁ = M₁ ⊕ K", size=11, bold=True, pad=8, fill="#f4f6f8", stroke="#333333")
    frags.extend([bm1, bk1, bc1])

    frags.append(arrow(215, 60, 255, 60, color="#2457d6", sw=1.8))
    frags.append(arrow(405, 60, 495, 60, color="#d97706", sw=1.8))

    # Середній блок: Повідомлення 2
    bm2, _, _ = textbox(130, 150, "Повідомлення M₂\n«RETREAT_ACROSS»", size=11, bold=True, pad=8, fill="#e8f4fd", stroke="#2457d6")
    bk2, _, _ = textbox(330, 150, "Спільний ключ K\n(ПОВТОРНЕ ВЖИТТЯ!)", size=11, bold=True, pad=8, fill="#fee2e2", stroke="#ef4444", color="#b91c1c")
    bc2, _, _ = textbox(570, 150, "Шифротекст C₂\nC₂ = M₂ ⊕ K", size=11, bold=True, pad=8, fill="#f4f6f8", stroke="#333333")
    frags.extend([bm2, bk2, bc2])

    frags.append(arrow(215, 150, 240, 150, color="#2457d6", sw=1.8))
    frags.append(arrow(420, 150, 495, 150, color="#ef4444", sw=1.8))

    # Перехоплення противником: стрілки з правого боку
    # Стрілка від C1 в обхід вниз до блоку XOR
    frags.append(line(650, 60, 680, 60, color="#dc2626", sw=1.8))
    frags.append(line(680, 60, 680, 240, color="#dc2626", sw=1.8))
    frags.append(arrow(680, 240, 660, 240, color="#dc2626", sw=1.8))

    # Стрілка від C2 прямо вниз до блоку XOR
    frags.append(arrow(570, 180, 570, 215, color="#dc2626", sw=1.8))

    # Блок обчислення різниці шифротекстів
    b_xor, _, _ = textbox(550, 260, "Криптоаналітик обчислює:\nC₁ ⊕ C₂ = (M₁ ⊕ K) ⊕ (M₂ ⊕ K)\n= M₁ ⊕ M₂ ⊕ (K ⊕ K)\n= M₁ ⊕ M₂", size=11, bold=True, pad=8, fill="#fef2f2", stroke="#dc2626", color="#991b1b")
    frags.append(b_xor)

    # Атака методом Crib Dragging
    b_crib, _, _ = textbox(200, 260, "Атака Crib Dragging:\nПідставляємо шаблон «_THE_» або «_AND_»\nЯкщо (M₁ ⊕ M₂) ⊕ «_THE_» дає змістовне слово,\nрозкриваються фрагменти ОБОХ повідомлень!", size=10, pad=8, fill="#fffbeb", stroke="#f59e0b", color="#92400e")
    frags.append(b_crib)

    frags.append(arrow(415, 260, 360, 260, color="#dc2626", sw=2))

    # Підсумковий висновок
    b_foot, _, _ = textbox(380, 345, "Ключ K повністю самознищується (K ⊕ K = 0). Досконала таємність миттєво падає до нуля.", size=11, bold=True, pad=6, fill="#eafaf1", stroke="#16a34a", color="#166534")
    frags.append(b_foot)

    render(os.path.join(OUT, "two-time-pad-leak.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_shannon_secrecy_prob()
    fig_otp_keyspace_mapping()
    fig_two_time_pad_leak()
    print("All figures generated successfully.")
