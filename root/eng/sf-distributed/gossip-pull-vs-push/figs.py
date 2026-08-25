# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми 'Pull vs push плітки'."""

import sys
import os

# scripts/ знаходиться на 4 рівні вище
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_push_vs_pull_mechanics():
    """Фігура 1: Механіка передачі: Push, Pull та симетричний Push-Pull."""
    w, h = 880, 430
    frags = []

    frags.append(text(w / 2, 26, "Механіка передачі даних у пліткових протоколах: Push, Pull та Push-Pull", size=15, bold=True))

    # Колонка 1: Push Gossip
    frags.append(rect(20, 50, 265, 360, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(152, 75, "1. Стратегія Push", size=14, bold=True, color=POS))
    frags.append(text(152, 93, "Ініціатор: інфікований вузол", size=11, color=MUTED))

    # Вузол A (інфікований) -> Вузол B (сприйнятливий)
    frags.append(rect(35, 115, 110, 45, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    frags.append(text(90, 134, "Вузол A", size=12, bold=True, color=POS))
    frags.append(text(90, 149, "Стан: v2 (нове)", size=10, color=POS))

    frags.append(rect(160, 115, 110, 45, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(215, 134, "Вузол B", size=12, bold=True, color=INK))
    frags.append(text(215, 149, "Стан: v1 (старе)", size=10, color=MUTED))

    # Стрілка Push Payload
    frags.append(arrow(145, 137, 160, 137, color=POS, sw=2))
    frags.append(text(152, 175, "Пакет: [Payload v2]", size=11, bold=True, color=POS))
    frags.append(text(152, 190, "(активне штовхання)", size=10, color=MUTED))

    frags.append(rect(35, 210, 235, 85, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=5))
    frags.append(text(152, 230, "Динаміка поширення:", size=11, bold=True, color=INK))
    frags.append(text(152, 248, "• Старт: O((1+k)ᵗ) експонента", size=10, color=FIELD))
    frags.append(text(152, 266, "• Фініш: колізії, O(N log N) трафік", size=10, color=POS))
    frags.append(text(152, 284, "• Проблема купонів колекціонера", size=10, color=POS))

    frags.append(rect(35, 310, 235, 85, fill="#fef2f2", stroke=POS, sw=1, rx=5))
    frags.append(text(152, 328, "Ціна й трафік:", size=11, bold=True, color=POS))
    frags.append(text(152, 346, "Повне тіло оновлення летить", size=10, color=INK))
    frags.append(text(152, 364, "навіть якщо вузол B вже має v2", size=10, color=INK))
    frags.append(text(152, 382, "(марне витрачання смуги)", size=10, color=POS))

    # Колонка 2: Pull Gossip
    frags.append(rect(305, 50, 265, 360, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(437, 75, "2. Стратегія Pull", size=14, bold=True, color=NEG))
    frags.append(text(437, 93, "Ініціатор: неінфікований вузол", size=11, color=MUTED))

    frags.append(rect(320, 115, 110, 45, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(375, 134, "Вузол A", size=12, bold=True, color=INK))
    frags.append(text(375, 149, "Стан: v1 (старе)", size=10, color=MUTED))

    frags.append(rect(445, 115, 110, 45, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    frags.append(text(500, 134, "Вузол B", size=12, bold=True, color=POS))
    frags.append(text(500, 149, "Стан: v2 (нове)", size=10, color=POS))

    # Стрілки Pull: Запит і Відповідь
    frags.append(arrow(430, 128, 445, 128, color=NEG, sw=1.5))
    frags.append(text(437, 121, "1. GetState()", size=9, bold=True, color=NEG))
    frags.append(arrow(445, 148, 430, 148, color=FIELD, sw=1.5))
    frags.append(text(437, 163, "2. [Payload v2]", size=9, bold=True, color=FIELD))

    frags.append(rect(320, 210, 235, 85, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=5))
    frags.append(text(437, 230, "Динаміка поширення:", size=11, bold=True, color=INK))
    frags.append(text(437, 248, "• Старт: O(1/N) повільний пошук", size=10, color=POS))
    frags.append(text(437, 266, "• Фініш: квадратична збіжність", size=10, color=FIELD))
    frags.append(text(437, 284, "• s_{t+1} ≈ s_t^(k+1) — лавина", size=10, color=FIELD))

    frags.append(rect(320, 310, 235, 85, fill="#f0fdf4", stroke=FIELD, sw=1, rx=5))
    frags.append(text(437, 328, "Ціна й трафік:", size=11, bold=True, color=FIELD))
    frags.append(text(437, 346, "Порожні опитування на старті,", size=10, color=INK))
    frags.append(text(437, 364, "але нульове дублювання", size=10, color=INK))
    frags.append(text(437, 382, "корисного навантаження у кінці", size=10, color=FIELD))

    # Колонка 3: Гібридний Push-Pull
    frags.append(rect(590, 50, 270, 360, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(725, 75, "3. Гібрид Push-Pull", size=14, bold=True, color=FIELD))
    frags.append(text(725, 93, "Симетричний обмін дайджестами", size=11, color=MUTED))

    frags.append(rect(605, 115, 115, 45, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(662, 134, "Вузол A", size=12, bold=True, color=NEG))
    frags.append(text(662, 149, "v_A = {X:2, Y:1}", size=9, color=INK))

    frags.append(rect(735, 115, 115, 45, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(792, 134, "Вузол B", size=12, bold=True, color=FIELD))
    frags.append(text(792, 149, "v_B = {X:1, Y:3}", size=9, color=INK))

    # Стрілки обміну дайджестами і дельтами
    frags.append(arrow(720, 125, 735, 125, color=NEG, sw=1.5))
    frags.append(text(725, 120, "1. Digest_A + Δ(X:2)", size=9, bold=True, color=NEG))
    frags.append(arrow(735, 145, 720, 145, color=FIELD, sw=1.5))
    frags.append(text(725, 161, "2. Δ(Y:3)", size=9, bold=True, color=FIELD))

    frags.append(rect(605, 210, 240, 85, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=5))
    frags.append(text(725, 230, "Динаміка поширення:", size=11, bold=True, color=INK))
    frags.append(text(725, 248, "• Експоненційний старт (Push)", size=10, color=FIELD))
    frags.append(text(725, 266, "• Квадратичний фініш (Pull)", size=10, color=FIELD))
    frags.append(text(725, 284, "• Раунди: O(log N) — оптимум", size=10, color=FIELD))

    frags.append(rect(605, 310, 240, 85, fill="#f0fdf4", stroke=FIELD, sw=1, rx=5))
    frags.append(text(725, 328, "Оптимальність:", size=11, bold=True, color=FIELD))
    frags.append(text(725, 346, "Сумарні повідомлення:", size=10, color=INK))
    frags.append(text(725, 364, "O(N log log N) повідомлень", size=11, bold=True, color=FIELD))
    frags.append(text(725, 382, "проти O(N log N) у чистому Push", size=10, color=MUTED))

    return render(os.path.join(OUT, "push-vs-pull-mechanics.svg"), w, h, *frags)


def fig_convergence_curves():
    """Фігура 2: Графік збіжності епідемії: Push, Pull та Push-Pull."""
    w, h = 820, 380
    frags = []

    frags.append(text(w / 2, 26, "Криві збіжності епідемічного поширення (N = 10 000 вузлів)", size=15, bold=True))

    # Область графіка
    gx, gy, gw, gh = 80, 60, 680, 250
    frags.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=4))

    # Горизонтальні сітки (0%, 25%, 50%, 75%, 100%)
    for pct in [0, 25, 50, 75, 100]:
        y_pos = gy + gh - (pct / 100.0) * gh
        frags.append(line(gx, y_pos, gx + gw, y_pos, color="#e2e8f0", sw=1, dash="4,4"))
        frags.append(text(gx - 25, y_pos + 4, f"{pct}%", size=11, color=MUTED, anchor="middle"))

    # Вертикальні сітки (раунди від 0 до 24)
    rounds = [0, 4, 8, 12, 16, 20, 24]
    for r_val in rounds:
        x_pos = gx + (r_val / 24.0) * gw
        frags.append(line(x_pos, gy, x_pos, gy + gh, color="#e2e8f0", sw=1, dash="4,4"))
        frags.append(text(x_pos, gy + gh + 18, f"t={r_val}", size=11, color=MUTED, anchor="middle"))

    frags.append(text(gx + gw / 2, gy + gh + 36, "Раунди протоколу (t)", size=12, bold=True, color=INK))
    frags.append(text(gx - 55, gy + gh / 2, "Частка інфікованих вузлів", size=12, bold=True, color=INK, anchor="middle"))

    # Крива 1: Pure Push (червона) - стрімкий старт, плоский повільний хвіст
    push_pts = [
        (0, 0.0001), (2, 0.03), (4, 0.15), (6, 0.52), (8, 0.82), (10, 0.92),
        (12, 0.96), (14, 0.978), (16, 0.988), (18, 0.994), (20, 0.997), (24, 0.999)
    ]
    path_push = []
    for i, (r_val, frac) in enumerate(push_pts):
        px = gx + (r_val / 24.0) * gw
        py = gy + gh - frac * gh
        cmd = "M" if i == 0 else "L"
        path_push.append(f"{cmd} {px:.1f} {py:.1f}")
    frags.append(f'<path d="{" ".join(path_push)}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    # Крива 2: Pure Pull (синя) - повільний старт, вибуховий фініш
    pull_pts = [
        (0, 0.0001), (4, 0.001), (7, 0.01), (9, 0.05), (11, 0.18), (13, 0.55),
        (15, 0.94), (16, 0.999), (17, 1.0), (24, 1.0)
    ]
    path_pull = []
    for i, (r_val, frac) in enumerate(pull_pts):
        px = gx + (r_val / 24.0) * gw
        py = gy + gh - frac * gh
        cmd = "M" if i == 0 else "L"
        path_pull.append(f"{cmd} {px:.1f} {py:.1f}")
    frags.append(f'<path d="{" ".join(path_pull)}" fill="none" stroke="{NEG}" stroke-width="2.5" stroke-dasharray="6,3"/>')

    # Крива 3: Hybrid Push-Pull (зелена) - експоненційний старт + квадратичний фініш
    hybrid_pts = [
        (0, 0.0001), (2, 0.04), (4, 0.22), (6, 0.72), (8, 0.985), (9, 0.9999), (10, 1.0), (24, 1.0)
    ]
    path_hyb = []
    for i, (r_val, frac) in enumerate(hybrid_pts):
        px = gx + (r_val / 24.0) * gw
        py = gy + gh - frac * gh
        cmd = "M" if i == 0 else "L"
        path_hyb.append(f"{cmd} {px:.1f} {py:.1f}")
    frags.append(f'<path d="{" ".join(path_hyb)}" fill="none" stroke="{FIELD}" stroke-width="3"/>')

    # Анотації на графіку
    frags.append(rect(gx + 260, gy + 15, 230, 48, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=5))
    frags.append(text(gx + 375, gy + 34, "Push-Pull: 100% за 10 раундів", size=11, bold=True, color=FIELD))
    frags.append(text(gx + 375, gy + 50, "Ідеальне поєднання фаз", size=10, color=INK))

    frags.append(rect(gx + 470, gy + 110, 195, 45, fill="#fdecea", stroke=POS, sw=1.5, rx=5))
    frags.append(text(gx + 567, gy + 128, "Push: плоский хвіст", size=11, bold=True, color=POS))
    frags.append(text(gx + 567, gy + 144, "Колізії між інфікованими", size=10, color=POS))

    # Легенда праворуч знизу
    lx, ly = gx + 420, gy + 180
    frags.append(rect(lx, ly, 245, 60, fill="#fafbfc", stroke="#cbd5e1", sw=1, rx=5))
    frags.append(line(lx + 12, ly + 16, lx + 35, ly + 16, color=FIELD, sw=3))
    frags.append(text(lx + 45, ly + 20, "Гібрид Push-Pull (найшвидший)", size=10, bold=True, color=FIELD, anchor="start"))

    frags.append(line(lx + 12, ly + 32, lx + 35, ly + 32, color=POS, sw=2.5))
    frags.append(text(lx + 45, ly + 36, "Pure Push (швидкий старт, хвіст)", size=10, color=POS, anchor="start"))

    frags.append(line(lx + 12, ly + 48, lx + 35, ly + 48, color=NEG, sw=2.5, dash="5,3"))
    frags.append(text(lx + 45, ly + 52, "Pure Pull (лавина у кінці)", size=10, color=NEG, anchor="start"))

    return render(os.path.join(OUT, "convergence-curves.svg"), w, h, *frags)


def fig_scuttlebutt_reconciliation():
    """Фігура 3: Двофазна звірка станів за протоколом Scuttlebutt."""
    w, h = 860, 440
    frags = []

    frags.append(text(w / 2, 26, "Двофазне рукостискання Scuttlebutt: симетричний обмін дайджестами та дельтами", size=15, bold=True))

    # Вузол A (ліворуч)
    frags.append(rect(30, 55, 230, 365, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(145, 80, "Вузол A (Ініціатор)", size=14, bold=True, color=NEG))

    frags.append(rect(45, 100, 200, 110, fill="#ffffff", stroke="#94a3b8", sw=1, rx=5))
    frags.append(text(145, 118, "Локальний стан вузла A:", size=11, bold=True, color=INK))
    frags.append(text(145, 138, "Вузол 1 (A): версія 12 (нове)", size=10, bold=True, color=FIELD))
    frags.append(text(145, 156, "Вузол 2 (B): версія 4 (старе)", size=10, color=POS))
    frags.append(text(145, 174, "Вузол 3 (C): версія 8 (рівно)", size=10, color=MUTED))
    frags.append(text(145, 192, "Вузол 4 (D): версія 1 (старе)", size=10, color=POS))

    frags.append(rect(45, 225, 200, 75, fill="#eaf0fd", stroke=NEG, sw=1, rx=5))
    frags.append(text(145, 245, "Дайджест A:", size=11, bold=True, color=NEG))
    frags.append(text(145, 265, "{1:12, 2:4, 3:8, 4:1}", size=11, bold=True, color=INK))
    frags.append(text(145, 283, "(компактний вектор версій)", size=9, color=MUTED))

    frags.append(rect(45, 315, 200, 90, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=5))
    frags.append(text(145, 335, "Оновлення стану A:", size=11, bold=True, color=FIELD))
    frags.append(text(145, 355, "Приймає дельту від B:", size=10, color=INK))
    frags.append(text(145, 373, "• Вузол 2: версії 5..7", size=10, color=FIELD))
    frags.append(text(145, 391, "• Вузол 4: версії 2..3", size=10, color=FIELD))

    # Вузол B (праворуч)
    frags.append(rect(600, 55, 230, 365, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(715, 80, "Вузол B (Одержувач)", size=14, bold=True, color=FIELD))

    frags.append(rect(615, 100, 200, 110, fill="#ffffff", stroke="#94a3b8", sw=1, rx=5))
    frags.append(text(715, 118, "Локальний стан вузла B:", size=11, bold=True, color=INK))
    frags.append(text(715, 138, "Вузол 1 (A): версія 9 (старе)", size=10, color=POS))
    frags.append(text(715, 156, "Вузол 2 (B): версія 7 (нове)", size=10, bold=True, color=FIELD))
    frags.append(text(715, 174, "Вузол 3 (C): версія 8 (рівно)", size=10, color=MUTED))
    frags.append(text(715, 192, "Вузол 4 (D): версія 3 (нове)", size=10, bold=True, color=FIELD))

    frags.append(rect(615, 225, 200, 75, fill="#f0fdf4", stroke=FIELD, sw=1, rx=5))
    frags.append(text(715, 245, "Порівняння дайджестів:", size=11, bold=True, color=FIELD))
    frags.append(text(715, 265, "A випереджає по Вузлу 1", size=10, color=POS))
    frags.append(text(715, 283, "B випереджає по Вузлах 2, 4", size=10, color=FIELD))

    frags.append(rect(615, 315, 200, 90, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=5))
    frags.append(text(715, 335, "Оновлення стану B:", size=11, bold=True, color=FIELD))
    frags.append(text(715, 355, "Приймає дельту від A:", size=10, color=INK))
    frags.append(text(715, 373, "• Вузол 1: версії 10..12", size=10, color=FIELD))
    frags.append(text(715, 391, "Стани повністю збіглися!", size=10, bold=True, color=FIELD))

    # Центральна область: Протокольні повідомлення (Крок 1, 2, 3)
    # Крок 1: A -> B (Gossip Digest Syn)
    frags.append(arrow(265, 130, 595, 130, color=NEG, sw=2))
    frags.append(rect(310, 105, 240, 42, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=5))
    frags.append(text(430, 122, "1. DIGEST_SYN", size=11, bold=True, color=NEG))
    frags.append(text(430, 138, "Дайджест: {1:12, 2:4, 3:8, 4:1}", size=10, color=INK))

    # Крок 2: B -> A (Gossip Digest Ack + Delta)
    frags.append(arrow(595, 230, 265, 230, color=FIELD, sw=2))
    frags.append(rect(290, 200, 280, 52, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=5))
    frags.append(text(430, 218, "2. DIGEST_ACK + DELTA (Pull/Push)", size=11, bold=True, color=FIELD))
    frags.append(text(430, 234, "Дельта для A: {2:[v5..v7], 4:[v2..v3]}", size=10, bold=True, color=FIELD))
    frags.append(text(430, 248, "Запит для B: {1: потрібні версії > 9}", size=9, color=POS))

    # Крок 3: A -> B (Gossip Digest Ack2 + Delta)
    frags.append(arrow(265, 340, 595, 340, color=POS, sw=2))
    frags.append(rect(300, 315, 260, 48, fill="#fdecea", stroke=POS, sw=1.5, rx=5))
    frags.append(text(430, 333, "3. DIGEST_ACK2 + DELTA", size=11, bold=True, color=POS))
    frags.append(text(430, 350, "Дельта для B: {1:[v10..v12]}", size=10, bold=True, color=POS))

    return render(os.path.join(OUT, "scuttlebutt-reconciliation.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_push_vs_pull_mechanics()
    fig_convergence_curves()
    fig_scuttlebutt_reconciliation()
    print("Figures generated successfully.")
