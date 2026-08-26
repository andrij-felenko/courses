# -*- coding: utf-8 -*-
"""Генератор фігур для теми toctou-race (Гонка між перевіркою й використанням)."""

import os
import sys

# Додаємо шлях до scripts/ у корені репо (4 рівні вгору від root/eng/sf-security/toctou-race)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_toctou_timeline():
    """Фігура 1: Часова діаграма вразливості TOCTOU."""
    w, h = 860, 390
    path = os.path.join(IMG_DIR, "toctou-timeline.svg")

    frags = []

    # Загальна панель-підкладка
    frags.append(rect(20, 20, 820, 350, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))

    # Смуги процесів
    frags.append(rect(40, 50, 780, 100, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(rect(40, 170, 780, 100, fill="#fff7ed", stroke="#fed7aa", sw=1.5, rx=6))

    # Підписи процесів
    frags.append(text(140, 90, "Привілейований процес (root)", size=12, color=INK, bold=True))
    frags.append(text(140, 110, "UID = 0, EUID = 0", size=10, color=MUTED))

    frags.append(text(140, 210, "Атакуючий процес (user)", size=12, color=POS, bold=True))
    frags.append(text(140, 230, "UID = 1000, EUID = 1000", size=10, color=MUTED))

    # Часова вісь знизу
    frags.append(line(50, 310, 780, 310, color=LINE, sw=2))
    frags.append(arrow(770, 310, 800, 310, color=LINE, sw=2))
    frags.append(text(800, 335, "Час (t)", size=11, color=INK, bold=True))

    # Вікно гонки (позначка згори)
    frags.append(line(370, 40, 560, 40, color=POS, sw=2))
    frags.append(line(370, 35, 370, 45, color=POS, sw=2))
    frags.append(line(560, 35, 560, 45, color=POS, sw=2))
    frags.append(text(465, 30, "ВІКНО ГОНКИ (Δt = t3 - t0)", size=11, color=POS, bold=True))

    # Крок 1: access()
    b1, _, _ = textbox(310, 100, "1. access(path, W_OK)\nРезультат: дозволено", size=10, pad=5, fill="#eff6ff", stroke=NEG, sw=1.5)
    frags.append(b1)
    frags.append(line(310, 130, 310, 310, color=NEG, sw=1, dash="4,4"))
    frags.append(circle(310, 310, 4, fill=NEG, stroke=NEG))
    frags.append(text(310, 330, "t0 (TOC)", size=10, color=NEG, bold=True))

    # Крок 2: unlink & symlink
    b2, _, _ = textbox(470, 220, "2. unlink(path)\n3. symlink(\"/etc/shadow\", path)", size=10, pad=5, fill="#fef2f2", stroke=POS, sw=1.5)
    frags.append(b2)
    frags.append(line(470, 190, 470, 150, color=POS, sw=1, dash="4,4"))
    frags.append(line(470, 250, 470, 310, color=POS, sw=1, dash="4,4"))
    frags.append(circle(470, 310, 4, fill=POS, stroke=POS))
    frags.append(text(470, 330, "t1..t2 (Підміна)", size=10, color=POS, bold=True))

    # Крок 3: open()
    b3, _, _ = textbox(650, 100, "4. open(path, O_WRONLY)\nЗапис у цільовий файл!", size=10, pad=5, fill="#fee2e2", stroke=POS, sw=1.5)
    frags.append(b3)
    frags.append(line(650, 130, 650, 310, color=POS, sw=1, dash="4,4"))
    frags.append(circle(650, 310, 4, fill=POS, stroke=POS))
    frags.append(text(650, 330, "t3 (TOU)", size=10, color=POS, bold=True))

    # Стрілки переходів
    frags.append(arrow(375, 100, 410, 210, color=POS, sw=1.5))
    frags.append(arrow(545, 210, 580, 100, color=POS, sw=1.5))

    render(path, w, h, *frags)


def fig_symlink_race_attack():
    """Фігура 2: Механізм заміни dentry в VFS під час symlink race."""
    w, h = 860, 340
    path = os.path.join(IMG_DIR, "symlink-race-attack.svg")

    frags = []

    # Фаза 1 (Легітимний стан під час перевірки)
    frags.append(rect(30, 30, 380, 280, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(220, 55, "Стан під час перевірки (TOC)", size=12, color=INK, bold=True))

    b_p1, _, _ = textbox(120, 110, "Каталог /tmp/\n(dentry)", size=10, pad=5, fill=FILL, stroke=LINE)
    b_f1, _, _ = textbox(280, 110, "Файл job.log\n(inode 4018, UID 1000)", size=10, pad=5, fill="#eff6ff", stroke=NEG)
    frags.append(b_p1)
    frags.append(b_f1)
    frags.append(arrow(165, 110, 205, 110, color=LINE, sw=1.5))

    b_res1, _, _ = textbox(220, 210, "access(\"/tmp/job.log\", W_OK)\nРезультат: 0 (OK)\nПрава перевірено для UID 1000", size=10, pad=6, fill="#f0fdf4", stroke=FIELD)
    frags.append(b_res1)
    frags.append(arrow(220, 140, 220, 175, color=FIELD, sw=1.5))

    # Фаза 2 (Підміна під час використання)
    frags.append(rect(450, 30, 380, 280, fill="#fef2f2", stroke="#f87171", sw=1.5, rx=8))
    frags.append(text(640, 55, "Стан під час дії (TOU після атаки)", size=12, color=POS, bold=True))

    b_p2, _, _ = textbox(530, 105, "Каталог /tmp/\n(dentry)", size=10, pad=5, fill=FILL, stroke=LINE)
    b_sym, _, _ = textbox(670, 105, "Симлінк job.log\n-> /etc/shadow", size=10, pad=5, fill="#fee2e2", stroke=POS)
    frags.append(b_p2)
    frags.append(b_sym)
    frags.append(arrow(570, 105, 605, 105, color=LINE, sw=1.5))

    b_tgt, _, _ = textbox(730, 195, "Файл /etc/shadow\n(inode 102, UID 0)", size=10, pad=5, fill="#fef2f2", stroke=POS)
    frags.append(b_tgt)
    frags.append(arrow(680, 130, 715, 170, color=POS, sw=1.5))

    b_res2, _, _ = textbox(550, 240, "open(\"/tmp/job.log\", O_WRONLY)\nVFS розв'язує лінк на /etc/shadow\nПерезапис конфіденційних даних!", size=10, pad=6, fill="#fff1f2", stroke=POS)
    frags.append(b_res2)

    render(path, w, h, *frags)


def fig_descriptor_pinning_defense():
    """Фігура 3: Дескрипторно-орієнтований захист та атомарна фіксація."""
    w, h = 860, 340
    path = os.path.join(IMG_DIR, "descriptor-pinning-defense.svg")

    frags = []

    # Небезпечний підхід (зліва)
    frags.append(rect(30, 30, 380, 280, fill="#fff1f2", stroke="#fca5a5", sw=1.5, rx=8))
    frags.append(text(220, 55, "Небезпечно: шлях між викликами", size=12, color=POS, bold=True))

    b_u1, _, _ = textbox(220, 105, "1. stat(\"/tmp/dir/file.txt\", &st)", size=10, pad=5, fill=FILL, stroke=LINE)
    b_u_gap, _, _ = textbox(220, 165, "Вікно гонки: підміна шляху\n(unlink, rename, symlink)", size=10, pad=5, fill="#fee2e2", stroke=POS)
    b_u2, _, _ = textbox(220, 230, "2. open(\"/tmp/dir/file.txt\", O_RDWR)", size=10, pad=5, fill=FILL, stroke=LINE)
    frags.append(b_u1)
    frags.append(b_u_gap)
    frags.append(b_u2)
    frags.append(arrow(220, 125, 220, 142, color=POS, sw=1.5))
    frags.append(arrow(220, 190, 220, 208, color=POS, sw=1.5))

    # Безпечний дескрипторний підхід (справа)
    frags.append(rect(450, 30, 380, 280, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(640, 55, "Безпечно: дескрипторна фіксація", size=12, color=FIELD, bold=True))

    b_s1, _, _ = textbox(640, 105, "1. fd = openat(dirfd, \"file\",\n   O_RDWR | O_NOFOLLOW | O_CLOEXEC)", size=10, pad=5, fill=FILL, stroke=FIELD)
    b_s_pin, _, _ = textbox(640, 165, "Дескриптор прив'язано до struct file / inode\nЗміни імен у каталозі більше не діють", size=10, pad=5, fill="#dcfce7", stroke=FIELD)
    b_s2, _, _ = textbox(640, 230, "2. fstat(fd, &st) + перевірка типу\n   та прав на зафіксованому дескрипторі", size=10, pad=5, fill=FILL, stroke=FIELD)
    frags.append(b_s1)
    frags.append(b_s_pin)
    frags.append(b_s2)
    frags.append(arrow(640, 128, 640, 145, color=FIELD, sw=1.5))
    frags.append(arrow(640, 188, 640, 208, color=FIELD, sw=1.5))

    render(path, w, h, *frags)


if __name__ == "__main__":
    fig_toctou_timeline()
    fig_symlink_race_attack()
    fig_descriptor_pinning_defense()
    print("Всі фігури згенеровано успішно.")
