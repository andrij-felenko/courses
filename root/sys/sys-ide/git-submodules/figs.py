# -*- coding: utf-8 -*-
"""Фігури до статті «Звідки в образі чужий код: підмодуль, вендоринг, менеджер пакетів». Вивід — ./img/*.svg."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_FILL = "#eafaf1"
BLUE_FILL = "#eaf0fd"
RED_FILL = "#fdecea"
GRAY_FILL = "#f4f6f8"
YELLOW_FILL = "#fef9e7"


# ── 1. Порівняння архітектури Git Submodule та Git Subtree ───────────────────
def fig_submodule_vs_subtree():
    W, H = 1040, 560
    p = []

    # ── Ліва колонка: Git Submodule ──────────────────────────────────────────
    p.append(rect(30, 40, 470, 480, fill=BG, stroke=LINE, sw=1.5, rx=8))
    p.append(text(265, 75, "Git Submodule (Вказівник на зовнішній коміт)", size=15, bold=True, color=INK))
    
    # Батьківське дерево об'єктів
    b_parent, _, _ = textbox(265, 130, "Батьківський репозиторій (Main Tree)\n.git/objects/ — зберігає лише дерево проєкту", size=13, pad=10, fill=BLUE_FILL, stroke=NEG, sw=1.5)
    p.append(b_parent)
    
    # Gitlink запис у дереві
    b_link, _, _ = textbox(265, 215, "Дерево Git (mode 160000 commit)\nlibs/lwip -> 7e9f3b2a… (фіксований SHA-1/256)", size=12, pad=10, fill=YELLOW_FILL, stroke=POS, sw=1.5)
    p.append(b_link)
    p.append(arrow(265, 158, 265, 190, color=LINE, sw=1.6))
    
    # Файл .gitmodules
    b_mod, _, _ = textbox(150, 310, "Конфігурація .gitmodules\n[submodule \"lwip\"]\n  path = libs/lwip\n  url = https://…/lwip.git", size=11, pad=8, fill=GRAY_FILL, stroke=MUTED, sw=1.2)
    p.append(b_mod)
    
    # Відокремлене сховище
    b_subrepo, _, _ = textbox(380, 310, "Відокремлене сховище\n.git/modules/lwip/\nВласна історія та ref-и\nHEAD -> 7e9f3b2a", size=11, pad=8, fill=GREEN_FILL, stroke=FIELD, sw=1.2)
    p.append(b_subrepo)
    
    p.append(arrow(220, 248, 160, 275, color=MUTED, sw=1.4))
    p.append(arrow(310, 248, 370, 275, color=MUTED, sw=1.4))
    
    # Робоча копія
    b_worktree, _, _ = textbox(265, 435, "Робоче дерево підмодуля: libs/lwip/\nМістить файл .git: gitdir: ../../.git/modules/lwip\nВимагає окремого клонування (git submodule update)", size=12, pad=10, fill=FILL, stroke=LINE, sw=1.4)
    p.append(b_worktree)
    p.append(arrow(150, 355, 220, 400, color=MUTED, sw=1.4))
    p.append(arrow(380, 355, 310, 400, color=MUTED, sw=1.4))

    # ── Права колонка: Git Subtree ───────────────────────────────────────────
    p.append(rect(540, 40, 470, 480, fill=BG, stroke=LINE, sw=1.5, rx=8))
    p.append(text(775, 75, "Git Subtree (Вбудований граф і монолітне дерево)", size=15, bold=True, color=INK))
    
    # Батьківське дерево
    b_st_parent, _, _ = textbox(775, 130, "Батьківський репозиторій (Main Tree)\n.git/objects/ — містить усі блоби та дерева бібліотеки", size=13, pad=10, fill=BLUE_FILL, stroke=NEG, sw=1.5)
    p.append(b_st_parent)
    
    # Злиття історії
    b_st_merge, _, _ = textbox(775, 215, "Синтетичний коміт злиття (Merge Commit)\nPrefix rewrite: імпортує вміст у libs/lwip/\nЗберігає зв'язок із батьківськими комітами", size=12, pad=10, fill=GREEN_FILL, stroke=FIELD, sw=1.5)
    p.append(b_st_merge)
    p.append(arrow(775, 158, 775, 190, color=LINE, sw=1.6))
    
    # Прямий запис у дерево
    b_st_tree, _, _ = textbox(775, 310, "Звичайний запис директорії (mode 040000 tree)\nlibs/lwip/ — звичайні блоби в дереві проєкту\nНемає файлів .gitmodules чи gitdir-покажчиків", size=12, pad=10, fill=YELLOW_FILL, stroke=POS, sw=1.5)
    p.append(b_st_tree)
    p.append(arrow(775, 252, 775, 280, color=LINE, sw=1.6))
    
    # Робоча копія
    b_st_work, _, _ = textbox(775, 435, "Робоче дерево: libs/lwip/\nДоступне одразу після стандартного git clone\nЗбірка автономна, але історія проєкту роздута", size=12, pad=10, fill=FILL, stroke=LINE, sw=1.4)
    p.append(b_st_work)
    p.append(arrow(775, 350, 775, 400, color=LINE, sw=1.6))

    render(os.path.join(IMG, "submodule-vs-subtree-architecture.svg"), W, H, *p,
           title="Архітектурна різниця між Git Submodule та Git Subtree")


# ── 2. Конвеєр вендорингу та фіксації залежностей ─────────────────────────────
def fig_vendoring_pipeline():
    W, H = 1040, 520
    p = []

    # 1. Зовнішнє джерело
    b_upstream, _, _ = textbox(150, 110, "Зовнішній апстрім\n(GitHub / GitLab / Tarball)\nРелізні теги, рухомі гілки", size=13, pad=12, fill=BLUE_FILL, stroke=NEG, sw=1.5)
    p.append(b_upstream)
    
    # 2. Верифікація цілісності
    b_verify, _, _ = textbox(440, 110, "Верифікація цілісності\nКриптографічний SHA-256\nLock-файл (Cargo/Conan/vcpkg)", size=13, pad=12, fill=YELLOW_FILL, stroke=POS, sw=1.5)
    p.append(b_verify)
    p.append(arrow(265, 110, 315, 110, color=LINE, sw=1.8))
    
    # 3. Локальна фіксація в репозиторії (Vendoring)
    b_vendor, _, _ = textbox(780, 110, "Локальне дерево репозиторію\nvendor/ або third_party/\nФіксація вихідних текстів", size=13, pad=12, fill=GREEN_FILL, stroke=FIELD, sw=1.5)
    p.append(b_vendor)
    p.append(arrow(565, 110, 645, 110, color=LINE, sw=1.8))
    
    # 4. Шар локальних патчів
    b_patches, _, _ = textbox(780, 260, "Шар локальних патчів\npatches/0001-fix-arm-cortex-m.patch\npatches/0002-custom-allocator.patch\nВідстеження відхилень від апстріму", size=12, pad=12, fill=RED_FILL, stroke=POS, sw=1.5)
    p.append(b_patches)
    p.append(arrow(780, 160, 780, 210, color=LINE, sw=1.8))
    
    # 5. Детерміністична збірка (Build System)
    b_build, _, _ = textbox(440, 260, "Детерміністична збірка\nCMake / Meson / Make\nФіксований Sysroot, прапорці C99/C++20\nІзольоване оточення (Air-Gapped)", size=12, pad=12, fill=GRAY_FILL, stroke=MUTED, sw=1.5)
    p.append(b_build)
    p.append(arrow(650, 260, 580, 260, color=LINE, sw=1.8))
    
    # 6. Кінцевий бінарний образ та аудит
    b_target, _, _ = textbox(440, 420, "Кінцевий бінарний образ (ELF / Firmware)\n+ Генерація SBOM (SPDX/CycloneDX)\n+ Повний аудит ліцензій та походження коду", size=13, pad=14, fill=BLUE_FILL, stroke=NEG, sw=1.5)
    p.append(b_target)
    p.append(arrow(440, 325, 440, 365, color=LINE, sw=1.8))

    render(os.path.join(IMG, "vendoring-dependency-pipeline.svg"), W, H, *p,
           title="Конвеєр вендорингу, накладання патчів та детерміністичної збірки")


if __name__ == "__main__":
    fig_submodule_vs_subtree()
    fig_vendoring_pipeline()
    print("Фігури згенеровано успішно.")
