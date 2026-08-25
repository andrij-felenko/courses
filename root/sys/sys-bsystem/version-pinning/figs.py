#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-діаграм для теми «Закріплення версій і замки залежностей»."""

import sys
import os

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_version_resolution_vs_lockfile():
    """Діаграма 1: Плаваючі діапазони версій проти детермінізму замкового файлу."""
    w, h = 960, 530
    frags = []

    frags.append(text(480, 26, "Плаваючі версії проти детермінізму замкового файлу (Lockfile)", size=17, bold=True))
    frags.append(text(480, 48, "Як неявний дрейф залежностей руйнує збірки й як замок фіксує точний стан", size=12, color=MUTED))

    # Секція 1: Плаваючі діапазони (Верхня половина)
    frags.append(rect(15, 70, 930, 205, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    frags.append(text(35, 95, "НЕЗАКРІПЛЕНІ ВЕРСІЇ (Floating Ranges: ^1.2.0, ~2.0, latest)", size=13, bold=True, color=POS, anchor="start"))

    # Блок 1.1: Маніфест
    b1, _, _ = textbox(155, 160, "Маніфест проєкту\nconanfile / Cargo.toml\nboost = '^1.80'\nopenssl = '>=3.0'", size=11, pad=10, fill="#ffffff", stroke="#94a3b8")
    frags.append(b1)

    # Блок 1.2: День 1
    b2, _, _ = textbox(445, 160, "День 1: Резолвер реєстру\nВирішено: Boost 1.80.0\nOpenSSL 3.0.2\nСтатус: Збірка успішна", size=11, pad=10, fill="#f0fdf4", stroke=FIELD, bold=False)
    frags.append(b2)
    frags.append(arrow(265, 160, 335, 160, color="#64748b", sw=1.5))

    # Блок 1.3: День 30
    b3, _, _ = textbox(775, 160, "День 30: Той самий код проєкту\nАле в реєстрі вийшов Boost 1.80.2\nАвтоматично стягнуто 1.80.2!\nРезультат: Поломка ABI / SIGSEGV", size=11, pad=10, fill="#fee2e2", stroke=POS, bold=True, color=POS)
    frags.append(b3)
    frags.append(arrow(555, 160, 625, 160, color=POS, sw=1.8))
    frags.append(text(590, 148, "Час і релізи", size=10.5, color=MUTED))

    # Секція 2: Замковий файл (Нижня половина)
    frags.append(rect(15, 295, 930, 215, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(35, 320, "ЗАМКОВИЙ ФАЙЛ (Lockfile Pinning: conan.lock, Cargo.lock, vcpkg baselines)", size=13, bold=True, color=FIELD, anchor="start"))

    # Блок 2.1: Маніфест + Замок
    b4, _, _ = textbox(155, 395, "Маніфест + Замковий файл\nconan.lock / Cargo.lock\nboost = 1.80.0 (sha256: a1b2...)\nopenssl = 3.0.2 (sha256: c3d4...)", size=11, pad=10, fill="#ffffff", stroke="#94a3b8")
    frags.append(b4)

    # Блок 2.2: День 1
    b5, _, _ = textbox(445, 395, "День 1: Фіксація графа\nЗавантаження за SHA-256\nПеревірка цілісності бінарників\nСтатус: Детермінована збірка", size=11, pad=10, fill="#ffffff", stroke=FIELD)
    frags.append(b5)
    frags.append(arrow(265, 395, 335, 395, color=FIELD, sw=1.5))

    # Блок 2.3: День 30
    b6, _, _ = textbox(775, 395, "День 30: CI-агент (--locked)\nРезолвер пропущено!\nСтягнуто виключно 1.80.0 (хеш збігся)\nРезультат: 100% Гарантований успіх", size=11, pad=10, fill="#ffffff", stroke=FIELD, bold=True, color=FIELD)
    frags.append(b6)
    frags.append(arrow(555, 395, 625, 395, color=FIELD, sw=1.8))
    frags.append(text(590, 383, "Імунітет до змін", size=10.5, color=FIELD))

    render(os.path.join(IMG_DIR, "version-resolution-vs-lockfile.svg"), w, h, *frags)


def fig_semver_vs_abi_breakage():
    """Діаграма 2: Ілюзія безпеки SemVer у C/C++ та поломка ABI."""
    w, h = 960, 500
    frags = []

    frags.append(text(480, 26, "Ілюзія безпеки SemVer у C/C++: чому PATCH ламає бінарний контракт", size=17, bold=True))
    frags.append(text(480, 48, "Семантичне версіонування гарантує синтаксис API, але безсиле перед двійковим ABI та законом Хайрума", size=12, color=MUTED))

    # Ліва колонка: SemVer API контракт
    frags.append(rect(30, 75, 425, 395, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(242, 105, "Обіцянка SemVer (Рівень вихідного коду API)", size=13, bold=True, color=NEG))

    frags.append(rect(50, 130, 385, 135, fill="#ffffff", stroke="#cbd5e1", rx=6))
    frags.append(text(65, 155, "Версія 1.4.0 (Оригінальна)", size=12, bold=True, anchor="start"))
    frags.append(text(65, 180, "struct Session {", size=11.5, anchor="start", color="#334155"))
    frags.append(text(85, 202, "uint64_t id;       // 8 байтів", size=11, anchor="start", color=MUTED))
    frags.append(text(85, 222, "char token[32];    // 32 байти", size=11, anchor="start", color=MUTED))
    frags.append(text(65, 245, "}; // Загальний sizeof: 40 байтів", size=11.5, bold=True, anchor="start", color=FIELD))

    frags.append(rect(50, 290, 385, 160, fill="#ffffff", stroke="#cbd5e1", rx=6))
    frags.append(text(65, 315, "Версія 1.4.1 (PATCH: «лише багфікс»)", size=12, bold=True, anchor="start", color=POS))
    frags.append(text(65, 340, "struct Session {", size=11.5, anchor="start", color="#334155"))
    frags.append(text(85, 360, "uint64_t id;       // 8 байтів", size=11, anchor="start", color=MUTED))
    frags.append(text(85, 380, "char token[32];    // 32 байти", size=11, anchor="start", color=MUTED))
    frags.append(text(85, 400, "bool is_authenticated; // +1 байт (вирівн. до 48)", size=11, bold=True, anchor="start", color=POS))
    frags.append(text(65, 428, "}; // Сигнатури функцій ті самі! Але sizeof = 48", size=11.5, bold=True, anchor="start", color=POS))

    # Права колонка: ABI руйнація в пам'яті
    frags.append(rect(495, 75, 435, 395, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    frags.append(text(712, 105, "Фізична пам'ять процесу (ABI Collision)", size=13, bold=True, color=POS))

    # Стек головної програми
    b_caller, _, _ = textbox(712, 185, "Головна програма (скомпільована з v1.4.0)\nВиділяє на стеку об'єкт Session\nРозмір у стековому кадрі: рівно 40 байтів\n[ 0..7: id ] [ 8..39: token ] [ 40..47: RetAddr ]", size=11.5, pad=10, fill="#ffffff", stroke="#94a3b8")
    frags.append(b_caller)

    frags.append(arrow(712, 235, 712, 275, color=POS, sw=2))
    frags.append(text(712, 258, "Передавання вказівника Session* у v1.4.1", size=11, color=POS, bold=True))

    # Поведінка оновленої бібліотеки
    b_lib, _, _ = textbox(712, 360, "Динамічна бібліотека (підмінена на v1.4.1)\nВиконує: session->is_authenticated = true;\nЗапис відбувається за зміщенням +40 байтів!\nПерезапис адреси повернення / пам'яті стека!\nРезультат: Негайний краш SIGSEGV / RCE", size=11.5, pad=10, fill="#fee2e2", stroke=POS, bold=True, color=POS)
    frags.append(b_lib)

    render(os.path.join(IMG_DIR, "semver-vs-abi-breakage.svg"), w, h, *frags)


def fig_lockfile_integrity_hash_tree():
    """Діаграма 3: Анатомія вузла замкового файлу та криптографічний граф."""
    w, h = 960, 520
    frags = []

    frags.append(text(480, 26, "Анатомія вузла в замковому файлі: криптографічна фіксація графа", size=17, bold=True))
    frags.append(text(480, 48, "Як lockfile унеможливлює підміну коду та комбінаторну розбіжність бінарних конфігурацій", size=12, color=MUTED))

    # Головний вузол (Центр)
    frags.append(rect(280, 80, 400, 265, fill="#f8fafc", stroke=NEG, sw=2, rx=8))
    frags.append(text(480, 108, "Вузол графа залежностей (Locked Node)", size=14, bold=True, color=NEG))

    # Складові вузла
    node_fields = [
        ("Ідентифікатор і точна версія", "pkg: zlib / version: 1.3.1 (без діапазонів ^, ~)", 145),
        ("Source Checksum (Хеш вихідного коду)", "sha256: 9a7fa265902b... (архів / git commit)", 185),
        ("Recipe Revision (RREV / Порт)", "rrev: d82e41... (хеш інструкцій збірки)", 225),
        ("Package ID (PREV / Двійковий хеш)", "pkg_id: 8c1b... (GCC 13, C++20, Release, CRT: MD)", 265),
        ("Locked Dependencies (Ребра графа)", "direct_deps: ['libpng/1.6.43#rrev2', 'zstd/1.5.5']", 305),
    ]

    for title_f, desc_f, y_pos in node_fields:
        frags.append(rect(295, y_pos - 16, 370, 34, fill="#ffffff", stroke="#cbd5e1", rx=4))
        frags.append(text(305, y_pos - 3, title_f, size=10.5, bold=True, anchor="start", color=INK))
        frags.append(text(305, y_pos + 11, desc_f, size=9.5, anchor="start", color=MUTED))

    # Лівий блок: Джерело даних
    b_src, _, _ = textbox(130, 210, "Реєстр пакетів\nTarball / Git\n(Зовнішній світ)", size=12, pad=10, fill="#fef3c7", stroke="#d97706")
    frags.append(b_src)
    frags.append(arrow(200, 210, 275, 185, color="#d97706", sw=1.5))
    frags.append(text(238, 185, "SHA-256 Check", size=10, color="#d97706", bold=True))

    # Правий блок: Бінарний кеш
    b_bin, _, _ = textbox(830, 210, "Бінарний кеш\nСкомпільовані .a / .so\n(Точний Package ID)", size=12, pad=10, fill="#e0e7ff", stroke=NEG)
    frags.append(b_bin)
    frags.append(arrow(685, 265, 755, 210, color=NEG, sw=1.5))
    frags.append(text(725, 252, "ABI Match", size=10, color=NEG, bold=True))

    # Нижній рівень: Транзитивне дерево
    frags.append(rect(40, 380, 880, 115, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(480, 405, "Повний розв'язаний транзитивний граф (Resolved Transitive Graph)", size=13, bold=True, color=FIELD))

    sub_nodes = [
        ("App (Root)", 150, 445),
        ("Boost.Asio 1.83.0", 370, 445),
        ("OpenSSL 3.1.4", 590, 445),
        ("Zlib 1.3.1", 810, 445),
    ]

    for name_s, x_s, y_s in sub_nodes:
        frags.append(rect(x_s - 85, y_s - 18, 170, 36, fill="#ffffff", stroke=FIELD, rx=5))
        frags.append(text(x_s, y_s + 4, name_s, size=11, bold=True, color=INK))

    frags.append(arrow(235, 445, 280, 445, color=FIELD, sw=1.5))
    frags.append(arrow(455, 445, 500, 445, color=FIELD, sw=1.5))
    frags.append(arrow(675, 445, 720, 445, color=FIELD, sw=1.5))

    render(os.path.join(IMG_DIR, "lockfile-integrity-hash-tree.svg"), w, h, *frags)


def fig_ci_supply_chain_pipeline():
    """Діаграма 4: Конвеєр CI/CD, режим --locked та захист ланцюга постачання."""
    w, h = 960, 490
    frags = []

    frags.append(text(480, 26, "Конвеєр CI/CD: детермінізм збірки та захист ланцюга постачання", size=17, bold=True))
    frags.append(text(480, 48, "Як режим заборони мутацій замків унеможливлює атаки типу Dependency Confusion та отруєння репозиторіїв", size=12, color=MUTED))

    steps = [
        ("1. Робоча станція", "Розробник оновлює версії:\ncargo update / conan lock\nФіксація diff у Git PR", 130, "#eef2f7", "#475569"),
        ("2. CI Gate: --locked", "Суворий режим білд-агента:\n--frozen-lockfile / --locked\nЗаборона будь-яких мутацій!", 365, "#fef2f2", POS),
        ("3. Аудит безпеки", "Сканування зафіксованих SHA:\ncargo-audit / osv-scanner\nПеревірка CVE бази даних", 600, "#fef3c7", "#d97706"),
        ("4. Герметична збірка", "Стягування виключно за хешами:\nВерифікація цілісності SHA-256\nДетермінований артефакт", 830, "#f0fdf4", FIELD),
    ]

    for title_st, desc_st, x_pos, fill_c, stroke_c in steps:
        frags.append(rect(x_pos - 105, 95, 210, 160, fill=fill_c, stroke=stroke_c, sw=1.8, rx=8))
        frags.append(text(x_pos, 125, title_st, size=12.5, bold=True, color=stroke_c))
        frags.append(line(x_pos - 85, 140, x_pos + 85, 140, color=stroke_c, sw=1, dash="2,2"))
        
        lines_d = desc_st.split("\n")
        for idx_l, line_t in enumerate(lines_d):
            frags.append(text(x_pos, 165 + idx_l * 20, line_t, size=10.5, color=INK))

    frags.append(arrow(240, 175, 255, 175, color="#475569", sw=2))
    frags.append(arrow(475, 175, 490, 175, color=POS, sw=2))
    frags.append(arrow(710, 175, 720, 175, color="#d97706", sw=2))

    # Нижня частина: Захист від векторів атак
    frags.append(rect(25, 290, 910, 175, fill="#fafafa", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(480, 318, "Які вектори атак блокує незмінний замковий файл у CI/CD", size=13.5, bold=True, color=INK))

    attacks = [
        ("Dependency Confusion", "Спроба підсунути шкідливий пакет із публічного реєстру замість приватного блокується точним хешем та зафіксованим репозиторієм.", 175),
        ("Typosquatting & Account Hijack", "Якщо зловмисник захопив акаунт мейнтейнера й випустив шкідливий патч v1.2.1, CI не завантажить його без явного оновлення замка.", 480),
        ("XZ-Style Tarball Injection", "Підміна архіву на серверах джерела виявляється миттєво: SHA-256 хеш завантаженого файлу не збігається із записом у lockfile.", 785),
    ]

    for title_a, desc_a, x_a in attacks:
        frags.append(rect(x_a - 140, 340, 280, 105, fill="#ffffff", stroke="#cbd5e1", rx=6))
        frags.append(text(x_a, 362, title_a, size=11.5, bold=True, color=POS))
        
        # Word wrap desc into multiple lines
        words = desc_a.split()
        lines_a = []
        cur_l = []
        for w_item in words:
            cur_l.append(w_item)
            if len(" ".join(cur_l)) > 32:
                lines_a.append(" ".join(cur_l))
                cur_l = []
        if cur_l:
            lines_a.append(" ".join(cur_l))
            
        for i_l, l_txt in enumerate(lines_a[:3]):
            frags.append(text(x_a, 385 + i_l * 16, l_txt, size=9.5, color=MUTED))

    render(os.path.join(IMG_DIR, "ci-supply-chain-pipeline.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_version_resolution_vs_lockfile()
    fig_semver_vs_abi_breakage()
    fig_lockfile_integrity_hash_tree()
    fig_ci_supply_chain_pipeline()
    print("Згенеровано 4 SVG-діаграми у теці img/")
