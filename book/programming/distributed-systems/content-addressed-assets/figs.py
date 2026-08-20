# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми 'Незмінна статика: відбиток вмісту в адресі'."""

import os
import sys

# Шлях до scripts/ у корені репозиторію (4 рівні вгору від book/programming/distributed-systems/content-addressed-assets)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_mutable_vs_immutable_caching():
    """Порівняння мутабельних URL (revalidation RTT, 304, розсинхронізація) та контентно-адресованих URL (immutable, 0ms HIT)."""
    w, h = 940, 520
    frags = []

    # Тло двох колонок
    frags.append(rect(15, 20, 440, 480, fill="#fef2f2", stroke="#fecaca", sw=1.5, rx=8))
    frags.append(text(235, 50, "Мутабельна адресація (/app.js)", size=16, color=POS, bold=True))
    frags.append(text(235, 72, "Постійна ревалідація та ризик version skew", size=12, color=MUTED, italic=True))

    frags.append(rect(485, 20, 440, 480, fill="#f0fdf4", stroke="#bbf7d0", sw=1.5, rx=8))
    frags.append(text(705, 50, "Контентна адресація (/app.8f4a1c.js)", size=16, color=FIELD, bold=True))
    frags.append(text(705, 72, "Cache-Control: immutable — нульові RTT", size=12, color=MUTED, italic=True))

    # Ліва колонка (Мутабельна)
    b_m_cli, _, _ = textbox(110, 130, "Браузер (Клієнт)\nКеш: старий app.js", size=11, pad=6, fill="#ffffff", stroke=MUTED)
    b_m_srv, _, _ = textbox(360, 130, "Сервер / CDN Edge\nETag / If-Modified", size=11, pad=6, fill="#ffffff", stroke=POS)
    frags.extend([b_m_cli, b_m_srv])

    frags.append(arrow(180, 120, 290, 120, color=POS, sw=1.5))
    frags.append(text(235, 110, "GET /app.js", size=10, color=POS))
    frags.append(arrow(290, 145, 180, 145, color=MUTED, sw=1.5))
    frags.append(text(235, 160, "304 Not Modified (100 мс)", size=10, color=MUTED))

    b_m_warn, _, _ = textbox(235, 240, "Проблема 1: Шторм 304-запитів\nМільйони клієнтів перевіряють ETag на кожен перегляд,\nстворюючи навантаження на Origin і затримку RTT.", size=11, pad=8, fill="#fff5f5", stroke=POS)
    frags.append(b_m_warn)

    b_m_skew, _, _ = textbox(235, 360, "Проблема 2: Розсинхронізація (Version Skew)\nНовий index.html завантажився, але app.js взято зі старого\nкешу -> падіння функцій, невідповідність типів, 404 на чанках.", size=11, pad=8, fill="#fff5f5", stroke=POS)
    frags.append(b_m_skew)

    b_m_footer, _, _ = textbox(235, 460, "Підсумок: або затримка на кожному кроці,\nабо ризик зламаного інтерфейсу користувача", size=11, pad=6, fill="#ffffff", stroke=POS)
    frags.append(b_m_footer)

    # Права колонка (Контентна адресація)
    b_i_cli, _, _ = textbox(580, 130, "Браузер (Клієнт)\nLocal Disk Cache", size=11, pad=6, fill="#ffffff", stroke=FIELD)
    b_i_srv, _, _ = textbox(830, 130, "CDN Edge / Origin\nImmutable Storage", size=11, pad=6, fill="#ffffff", stroke=FIELD)
    frags.extend([b_i_cli, b_i_srv])

    frags.append(line(650, 130, 760, 130, color="#d1d5db", sw=1.5, dash="4,4"))
    frags.append(text(705, 115, "Мережевий запит ВІДСУТНІЙ", size=11, color=FIELD, bold=True))
    frags.append(text(705, 145, "0 мс HIT (max-age=31536000)", size=10, color=MUTED))

    b_i_adv1, _, _ = textbox(705, 240, "Перевага 1: Нульовий трафік на ревалідацію\nЗаголовок 'immutable' блокує умовні GET навіть при Reload (F5).\nБраузер гарантовано бере файл з пам'яті/диска.", size=11, pad=8, fill="#f0fdf4", stroke=FIELD)
    frags.append(b_i_adv1)

    b_i_adv2, _, _ = textbox(705, 360, "Перевага 2: Атомарне оновлення версії\nindex.html (no-cache) вказує на новий /app.9e3b4d.js.\nНові та старі клієнти працюють ізольовано без конфліктів.", size=11, pad=8, fill="#f0fdf4", stroke=FIELD)
    frags.append(b_i_adv2)

    b_i_footer, _, _ = textbox(705, 460, "Підсумок: 100% кеш-хіт на периферії,\nмиттєве відкриття та абсолютна узгодженість", size=11, pad=6, fill="#ffffff", stroke=FIELD)
    frags.append(b_i_footer)

    return render(os.path.join(IMG_DIR, "mutable-vs-immutable-caching.svg"), w, h, *frags)


def fig_chunk_graph_cascade_invalidation():
    """Каскадна інвалідація хешів у графі залежностей та її вирішення через runtime-маніфест."""
    w, h = 940, 480
    frags = []

    # Ліва частина: Каскадне оновлення (Hash Churn)
    frags.append(rect(15, 20, 440, 440, fill="#fff7ed", stroke="#fed7aa", sw=1.5, rx=8))
    frags.append(text(235, 45, "Каскадний зсув хешів (Hash Churn)", size=15, color=POS, bold=True))
    frags.append(text(235, 65, "Прямі імпорти хешованих імен", size=11, color=MUTED, italic=True))

    b_entry_bad, _, _ = textbox(235, 110, "entry.a1b2.js\nimport './vendor.c3d4.js'\nimport './utils.e5f6.js'", size=11, pad=8, fill="#ffffff", stroke=POS)
    b_vend_bad, _, _ = textbox(135, 220, "vendor.c3d4.js\nReact / Lodash (1.2 MB)\n(не змінювався)", size=11, pad=8, fill="#ffffff", stroke=MUTED)
    b_util_bad, _, _ = textbox(335, 220, "utils.NEW_HASH.js\nВиправлено 1 рядок!\nХеш e5f6 -> 7a8b", size=11, pad=8, fill="#fef2f2", stroke=POS)
    frags.extend([b_entry_bad, b_vend_bad, b_util_bad])

    frags.append(arrow(200, 145, 155, 185, color=MUTED, sw=1.5))
    frags.append(arrow(270, 145, 315, 185, color=POS, sw=1.5))

    b_bad_result, _, _ = textbox(235, 340, "Каскадний ефект:\n1. Зміна в utils змінює його URL;\n2. entry містить текст нового URL -> тіло entry змінюється;\n3. Хеш entry.a1b2.js стає entry.f9e8.js;\n4. Усі користувачі змушені повторно качати entry!", size=11, pad=8, fill="#fff5f5", stroke=POS)
    frags.append(b_bad_result)

    # Права частина: Ізоляція через Маніфест і Runtime
    frags.append(rect(485, 20, 440, 440, fill="#f0f9ff", stroke="#bae6fd", sw=1.5, rx=8))
    frags.append(text(705, 45, "Ізоляція через Маніфест (Vite / Webpack)", size=15, color=NEG, bold=True))
    frags.append(text(705, 65, "Числовий/символьний ID модулів + Import Map", size=11, color=MUTED, italic=True))

    b_html_good, _, _ = textbox(705, 105, "index.html (no-cache)\n<script type='importmap'>\n{ 'utils': '/chunks/utils.7a8b.js' }", size=10, pad=6, fill="#ffffff", stroke=FIELD)
    b_entry_good, _, _ = textbox(705, 205, "entry.a1b2.js (НЕ ЗМІНИВСЯ!)\nimport('utils')  // посилання на ID", size=11, pad=6, fill="#ffffff", stroke=FIELD)
    b_vend_good, _, _ = textbox(600, 305, "vendor.c3d4.js\n100% Cache HIT\n(1.2 MB збережено)", size=11, pad=6, fill="#ffffff", stroke=FIELD)
    b_util_good, _, _ = textbox(810, 305, "utils.7a8b.js\nЗавантажується лише\nоновлений чанк (4 KB)", size=11, pad=6, fill="#f0fdf4", stroke=NEG)
    frags.extend([b_html_good, b_entry_good, b_vend_good, b_util_good])

    frags.append(arrow(705, 140, 705, 175, color=FIELD, sw=1.5))
    frags.append(arrow(665, 235, 620, 275, color=FIELD, sw=1.5))
    frags.append(arrow(745, 235, 790, 275, color=NEG, sw=1.5))

    b_good_result, _, _ = textbox(705, 400, "Результат оптимізації:\nХеш-маніфест винесено в точку входу (HTML/runtime);\nЗміна одного модуля не викликає інвалідації сусідніх чанків.", size=11, pad=6, fill="#ffffff", stroke=FIELD)
    frags.append(b_good_result)

    return render(os.path.join(IMG_DIR, "chunk-graph-cascade-invalidation.svg"), w, h, *frags)


def fig_multi_system_cas_ecosystem():
    """Єдина архітектурна модель CAS у 4 розподілених доменах: Web, Git, Docker/OCI, Nix."""
    w, h = 940, 480
    frags = []

    # 4 колонки систем
    cols = [
        ("Web Assets (CDN)", "#eff6ff", "#bfdbfe", NEG, [
            "Об'єкт: JS / CSS / WASM",
            "Хеш: SHA-256 / BLAKE3",
            "Адреса: /app.8f4a1c.js",
            "Гарантія: immutable HTTP",
            "Вигода: Edge HIT, 0ms RTT"
        ]),
        ("Git Object Store", "#f0fdf4", "#bbf7d0", FIELD, [
            "Об'єкт: Blob, Tree, Commit",
            "Хеш: SHA-1 / SHA-256",
            "Адреса: .git/objects/8f/4a...",
            "Гарантія: Merkle DAG",
            "Вигода: Цілісність історії"
        ]),
        ("Docker / OCI", "#fefce8", "#fef08a", INK, [
            "Об'єкт: Layer Tarball (RootFS)",
            "Хеш: sha256:7e8b9a...",
            "Адреса: Registry Blob Store",
            "Гарантія: Content Digest",
            "Вигода: Layer Dedup на ноді"
        ]),
        ("Nix / Guix Store", "#faf5ff", "#e9d5ff", POS, [
            "Об'єкт: Compiled Package / Lib",
            "Хеш: SHA-256 від графа білда",
            "Адреса: /nix/store/7z3k...-pkg",
            "Гарантія: Hermetic sandbox",
            "Вигода: 100% відтворюваність"
        ]),
    ]

    cw = 215
    spacing = 15
    start_x = 20

    for i, (title, f_bg, f_border, f_color, points) in enumerate(cols):
        cx = start_x + i * (cw + spacing)
        frags.append(rect(cx, 25, cw, 340, fill=f_bg, stroke=f_border, sw=1.5, rx=8))
        frags.append(text(cx + cw // 2, 55, title, size=13, color=f_color, bold=True))

        for j, pt in enumerate(points):
            py = 95 + j * 48
            b_box, _, _ = textbox(cx + cw // 2, py, pt, size=10, pad=5, fill="#ffffff", stroke=f_border)
            frags.append(b_box)

    # Фундаментальний інваріант CAS унизу
    frags.append(rect(20, 385, 900, 75, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(470, 412, "Універсальний закон контентної адресації: Address = Hash(Content)", size=14, color=INK, bold=True))
    frags.append(text(470, 438, "Незмінність даних (Immutability) гарантує дедуплікацію, безпеку та кешування на вічність у будь-якій системі.", size=12, color=MUTED))

    return render(os.path.join(IMG_DIR, "multi-system-cas-ecosystem.svg"), w, h, *frags)


def fig_content_defined_chunking_dedup():
    """Фіксоване розбиття (Fixed-size) проти Content-Defined Chunking (FastCDC) при зсуві байтів."""
    w, h = 940, 500
    frags = []

    # Верхній блок: Fixed-size Chunking
    frags.append(rect(15, 20, 910, 215, fill="#fef2f2", stroke="#fecaca", sw=1.5, rx=8))
    frags.append(text(470, 45, "Фіксоване розбиття (Fixed-Size Chunking, напр. 64 КБ): Проблема зсуву меж", size=14, color=POS, bold=True))

    # Файл до і після
    frags.append(text(80, 80, "Оригінал:", size=12, color=INK, bold=True, anchor="start"))
    frags.append(rect(160, 65, 160, 30, fill="#e0e7ff", stroke="#818cf8", sw=1))
    frags.append(text(240, 85, "Блок 1 (Хеш: A1)", size=11, color=INK))
    frags.append(rect(330, 65, 160, 30, fill="#e0e7ff", stroke="#818cf8", sw=1))
    frags.append(text(410, 85, "Блок 2 (Хеш: B2)", size=11, color=INK))
    frags.append(rect(500, 65, 160, 30, fill="#e0e7ff", stroke="#818cf8", sw=1))
    frags.append(text(580, 85, "Блок 3 (Хеш: C3)", size=11, color=INK))
    frags.append(rect(670, 65, 160, 30, fill="#e0e7ff", stroke="#818cf8", sw=1))
    frags.append(text(750, 85, "Блок 4 (Хеш: D4)", size=11, color=INK))

    frags.append(text(80, 135, "+1 байт на початок:", size=11, color=POS, bold=True, anchor="start"))
    frags.append(rect(160, 120, 20, 30, fill=POS, stroke=POS, sw=1))
    frags.append(rect(180, 120, 160, 30, fill="#fee2e2", stroke="#f87171", sw=1))
    frags.append(text(260, 140, "Блок 1' (Хеш: X9)", size=11, color=POS))
    frags.append(rect(350, 120, 160, 30, fill="#fee2e2", stroke="#f87171", sw=1))
    frags.append(text(430, 140, "Блок 2' (Хеш: Y8)", size=11, color=POS))
    frags.append(rect(520, 120, 160, 30, fill="#fee2e2", stroke="#f87171", sw=1))
    frags.append(text(600, 140, "Блок 3' (Хеш: Z7)", size=11, color=POS))
    frags.append(rect(690, 120, 160, 30, fill="#fee2e2", stroke="#f87171", sw=1))
    frags.append(text(770, 140, "Блок 4' (Хеш: W6)", size=11, color=POS))

    b_fix_warn, _, _ = textbox(470, 195, "Наслідок: Зсув на 1 байт повністю змінив хеші ВСІХ наступних блоків. Дедуплікація = 0%!", size=11, pad=6, fill="#ffffff", stroke=POS)
    frags.append(b_fix_warn)

    # Нижній блок: Content-Defined Chunking (CDC)
    frags.append(rect(15, 255, 910, 225, fill="#f0fdf4", stroke="#bbf7d0", sw=1.5, rx=8))
    frags.append(text(470, 280, "Контентно-визначене розбиття (FastCDC / Rabin): Стійкість до зсуву", size=14, color=FIELD, bold=True))

    frags.append(text(80, 320, "Оригінал (CDC):", size=11, color=INK, bold=True, anchor="start"))
    frags.append(rect(160, 305, 140, 30, fill="#dcfce7", stroke="#4ade80", sw=1))
    frags.append(text(230, 325, "Чанк 1 (A1)", size=11, color=INK))
    frags.append(rect(310, 305, 180, 30, fill="#dcfce7", stroke="#4ade80", sw=1))
    frags.append(text(400, 325, "Чанк 2 (B2)", size=11, color=INK))
    frags.append(rect(500, 305, 130, 30, fill="#dcfce7", stroke="#4ade80", sw=1))
    frags.append(text(565, 325, "Чанк 3 (C3)", size=11, color=INK))
    frags.append(rect(640, 305, 190, 30, fill="#dcfce7", stroke="#4ade80", sw=1))
    frags.append(text(735, 325, "Чанк 4 (D4)", size=11, color=INK))

    frags.append(text(80, 375, "+1 байт на початок:", size=11, color=FIELD, bold=True, anchor="start"))
    frags.append(rect(160, 360, 150, 30, fill="#fef2f2", stroke=POS, sw=1))
    frags.append(text(235, 380, "Чанк 1' (НОВИЙ)", size=11, color=POS))
    frags.append(rect(320, 360, 180, 30, fill="#dcfce7", stroke="#4ade80", sw=1))
    frags.append(text(410, 380, "Чанк 2 (B2) ЗБЕРЕЖЕНО", size=11, color=FIELD, bold=True))
    frags.append(rect(510, 360, 130, 30, fill="#dcfce7", stroke="#4ade80", sw=1))
    frags.append(text(575, 380, "Чанк 3 (C3)", size=11, color=FIELD, bold=True))
    frags.append(rect(650, 360, 190, 30, fill="#dcfce7", stroke="#4ade80", sw=1))
    frags.append(text(745, 380, "Чанк 4 (D4)", size=11, color=FIELD, bold=True))

    b_cdc_good, _, _ = textbox(470, 445, "Наслідок: Межі чанків визначаються вмістом даних (маскою плаваючого вікна).\nЗмінився лише 1-й чанк; чанки 2, 3, 4 повторно використані. Дедуплікація = 75–98%!", size=11, pad=6, fill="#ffffff", stroke=FIELD)
    frags.append(b_cdc_good)

    return render(os.path.join(IMG_DIR, "content-defined-chunking-dedup.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_mutable_vs_immutable_caching()
    fig_chunk_graph_cascade_invalidation()
    fig_multi_system_cas_ecosystem()
    fig_content_defined_chunking_dedup()
    print("Усі фігури успішно згенеровано в %s" % IMG_DIR)
