# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Топології розгалуження ──────────────────────────────────────────
def fig_branching_models_topology():
    W, H = 1000, 520
    frags = []

    models = [
        ("Trunk-Based Development", "Єдиний основний стовбур", [
            ("main (стовбур)", "Безперервна інтеграція щодня", "#eef4ff", INK),
            ("Короткі гілки", "Життя: 2–6 годин, швидкий злив", "#f6faf7", FIELD),
            ("Прапорці фіч", "Ізоляція логіки без розриву графу", "#fff9e6", "#d97706"),
            ("Теги випуску", "Фіксація релізів прямо на стовбурі", "#eef4ff", NEG),
        ], "Конфлікти: Мінімальні O(1)\nШвидкість: Максимальна\nПідходить: SaaS, веб, мікросервіси"),

        ("Класичний GitFlow", "Ієрархія довгоживучих гілок", [
            ("develop / master", "Паралельні вічні стовбури", "#fee2e2", POS),
            ("feature-гілки", "Живуть тижнями, відхиляються", "#fff9e6", "#d97706"),
            ("release-гілки", "Тривала ручна стабілізація", "#fff9e6", "#d97706"),
            ("hotfix двобічний", "Злиття і в master, і в develop", "#fee2e2", POS),
        ], "Конфлікти: Merge Hell, високі\nШвидкість: Затримки тижнями\nПідходить: Застарілі моноліти"),

        ("Гілки випуску (Release Branches)", "Стовбур + гілки супроводу", [
            ("main (активний)", "Весь новий код іде сюди першим", "#eef4ff", INK),
            ("support/v1.x", "Ізольована гілка для версії 1.x", "#f6faf7", FIELD),
            ("support/v2.x", "Ізольована гілка для версії 2.x", "#f6faf7", FIELD),
            ("Cherry-Pick -x", "Точковий бекпорт лише виправлень", "#fff9e6", "#d97706"),
        ], "Конфлікти: Локалізовані\nШвидкість: Висока + контроль\nПідходить: Embedded, SDK, LTS"),
    ]

    col_w = 290
    col_gap = 25
    left_m = 35
    top_m = 50

    for idx, (title, subtitle, stages, summary) in enumerate(models):
        cx = left_m + idx * (col_w + col_gap) + col_w / 2
        cy = top_m

        hdr_box, hw, hh = textbox(cx, cy + 20, f"{title}\n({subtitle})", size=13, bold=True,
                                  fill="#f3f4f6", stroke=INK, sw=1.8, pad=10)
        frags.append(hdr_box)

        curr_y = cy + 70
        for st_title, st_desc, bg_col, border_col in stages:
            st_box, sw_b, sh_b = textbox(cx, curr_y + 35, f"{st_title}\n{st_desc}", size=11, bold=True,
                                         fill=bg_col, stroke=border_col, sw=1.4, pad=8)
            frags.append(st_box)
            curr_y += 75

        sum_box, sum_w, sum_h = textbox(cx, curr_y + 55, summary, size=11, bold=False,
                                        fill="#ffffff", stroke=MUTED, sw=1.2, pad=10)
        frags.append(sum_box)

    render(os.path.join(IMG, 'branching-models-topology.svg'), W, H, *frags,
           title="Порівняння топологій розгалуження кодової бази")


# ── Фігура 2: Драбина супроводу LTS ──────────────────────────────────────────
def fig_lts_maintenance_ladder():
    W, H = 960, 480
    frags = []

    rows = [
        ("main (Стовбур)", "Активна розробка наступного покоління (v3.0.0-dev)\nУсі нові можливості, масштабні архітектурні зміни та рефакторинг",
         "#eef4ff", INK, "Статус: ACTIVE TRUNK", 70),
        ("support/v2.x (LTS 2)", "Активна довготривала підтримка (v2.4.x)\nПланові виправлення дефектів, оновлення сумісності та патчі безпеки",
         "#f6faf7", FIELD, "Статус: ACTIVE LTS", 160),
        ("support/v1.x (LTS 1)", "Підтримка безпеки та критичних збоїв (v1.8.x)\nЖодних нових функцій: виключно закриття вразливостей CVE та фатальних аварій",
         "#fff9e6", "#d97706", "Статус: SECURITY-ONLY", 250),
        ("v0.9.x (Застаріла)", "Завершення життєвого циклу (End of Life, EOL)\nПідтримку зупинено: репозиторій заморожено, бекпорти більше не приймаються",
         "#fee2e2", POS, "Статус: DEPRECATED / EOL", 340),
    ]

    for name, desc, bg_col, border_col, badge, y in rows:
        b_box, bw, bh = textbox(130, y + 25, f"{name}\n{badge}", size=11, bold=True,
                                fill=bg_col, stroke=border_col, sw=1.5, pad=8)
        frags.append(b_box)

        d_box, dw, dh = textbox(570, y + 25, desc, size=11, bold=False,
                                fill="#ffffff", stroke=MUTED, sw=1.2, pad=10)
        frags.append(d_box)

        if y < 340:
            frags.append(arrow(130, y + 55, 130, y + 80, color=border_col, sw=1.5))
            frags.append(text(215, y + 68, "Бекпорт патчів", size=10, color=MUTED, bold=False))

    render(os.path.join(IMG, 'lts-maintenance-ladder.svg'), W, H, *frags,
           title="Драбина супроводу версій LTS та фази життєвого циклу релізів")


# ── Фігура 3: Потік Upstream-First ───────────────────────────────────────────
def fig_upstream_first_backport_flow():
    W, H = 980, 480
    frags = []

    steps = [
        (120, 100, "Крок 1: Локалізація", "Виявлення дефекту\nСтворення гілки\nfix/memleak", "#eef4ff", INK),
        (370, 100, "Крок 2: Злиття в main", "Pull Request у стовбур\nCode Review + CI\nКоміт SHA: 8f4a21", "#eef4ff", INK),
        (620, 100, "Крок 3: Cherry-Pick -x", "git cherry-pick -x 8f4a21\nПеренесення в support/v2.1\nЗбереження походження", "#fff9e6", "#d97706"),
        (870, 100, "Крок 4: Реліз патчу", "Матричний прогін CI\nТег v2.1.5\nКоміт SHA: c39e12", "#f6faf7", FIELD),
    ]

    for cx, cy, title, desc, bg, stroke_col in steps:
        box, w, h = textbox(cx, cy + 30, f"{title}\n{desc}", size=11, bold=True,
                            fill=bg, stroke=stroke_col, sw=1.5, pad=10)
        frags.append(box)

    frags.append(arrow(200, 130, 275, 130, color=INK, sw=1.8))
    frags.append(arrow(465, 130, 520, 130, color=INK, sw=1.8))
    frags.append(arrow(720, 130, 775, 130, color=FIELD, sw=1.8))

    meta_desc = (
        "Структура метаданих коміту бекпорту:\n"
        "commit c39e1284fa... (HEAD -> support/v2.1)\n"
        "Author: Security Team <security@example.com>\n"
        "    [v2.1] fix(net): resolve buffer overflow during packet framing\n"
        "    (cherry picked from commit 8f4a21b3c990a174f82d1c9b3a0e4)\n"
        "    Upstream-commit: 8f4a21b3c990a174f82d1c9b3a0e4\n"
        "    Fixes: CVE-2026-4401"
    )
    meta_box, mw, mh = textbox(490, 330, meta_desc, size=11, bold=False,
                               fill="#f8fafc", stroke=MUTED, sw=1.3, pad=12)
    frags.append(meta_box)

    render(os.path.join(IMG, 'upstream-first-backport-flow.svg'), W, H, *frags,
           title="Потік бекпорту за принципом Upstream-First із фіксацією походження")


# ── Фігура 4: Ізоляція радіуса ураження ───────────────────────────────────────
def fig_hotfix_blast_radius_isolation():
    W, H = 960, 480
    frags = []

    left_x = 240
    frags.append(textbox(left_x, 60, "Забруднений коміт (Антипатерн)\nЗмішування фіксу з рефакторингом",
                         size=12, bold=True, fill="#fee2e2", stroke=POS, sw=1.5, pad=8)[0])

    left_steps = [
        ("Виправлення дефекту (2 рядки)", "#f6faf7", FIELD),
        ("Перейменування функцій (15 файлів)", "#fee2e2", POS),
        ("Зміна форматування / clang-format", "#fee2e2", POS),
        ("Оновлення версії компілятора C++", "#fee2e2", POS),
    ]
    curr_y = 130
    for st_text, bg, strk in left_steps:
        frags.append(textbox(left_x, curr_y, st_text, size=11, bold=False, fill=bg, stroke=strk, sw=1.2, pad=6)[0])
        curr_y += 50

    frags.append(textbox(left_x, 370, "Наслідки для LTS:\n• Десятки конфліктів при cherry-pick\n• Непередбачувані семантичні регресії\n• Злам бінарної сумісності ABI",
                         size=11, bold=False, fill="#ffffff", stroke=POS, sw=1.4, pad=8)[0])

    right_x = 720
    frags.append(textbox(right_x, 60, "Атомарний коміт (Канон)\nСувора ізоляція виправлення",
                         size=12, bold=True, fill="#f6faf7", stroke=FIELD, sw=1.5, pad=8)[0])

    right_steps = [
        ("Виправлення дефекту (2 рядки)", "#f6faf7", FIELD),
        ("Модульний тест на регресію", "#f6faf7", FIELD),
        ("Жодного косметичного форматування", "#f6faf7", FIELD),
        ("Збереження існуючого ABI/API", "#f6faf7", FIELD),
    ]
    curr_y = 130
    for st_text, bg, strk in right_steps:
        frags.append(textbox(right_x, curr_y, st_text, size=11, bold=False, fill=bg, stroke=strk, sw=1.2, pad=6)[0])
        curr_y += 50

    frags.append(textbox(right_x, 370, "Наслідки для LTS:\n• 100% чистий бекпорт без конфліктів\n• Мінімальний радіус ураження\n• Проста ізольована верифікація",
                         size=11, bold=False, fill="#ffffff", stroke=FIELD, sw=1.4, pad=8)[0])

    render(os.path.join(IMG, 'hotfix-blast-radius-isolation.svg'), W, H, *frags,
           title="Ізоляція радіуса ураження: атомарний бекпорт проти змішаного з рефакторингом")


if __name__ == '__main__':
    fig_branching_models_topology()
    fig_lts_maintenance_ladder()
    fig_upstream_first_backport_flow()
    fig_hotfix_blast_radius_isolation()
    print("Figures generated successfully.")
