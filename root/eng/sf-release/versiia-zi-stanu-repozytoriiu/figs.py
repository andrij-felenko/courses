# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Наскрізний конвеєр перенесення стану репозиторію в бінарний образ ──────
def fig_repo_state_to_binary_pipeline():
    W, H = 1000, 480
    frags = []

    frags.append(text(500, 25, "Наскрізний конвеєр перенесення стану репозиторію у виділену секцію бінарного образу",
                      size=15, bold=True, color=INK))

    # Блок 1: Стан репозиторію Git
    b1_bg = rect(30, 60, 260, 360, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8)
    frags.append(b1_bg)
    frags.append(text(160, 85, "1. Стан репозиторію (Git)", size=13, bold=True, color=INK))

    frags.append(rect(45, 110, 230, 60, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(160, 130, "Граф комітів (DAG)", size=11, bold=True, color=INK))
    frags.append(text(160, 150, "Останній тег: v2.4.1 + 14 комітів", size=10, color=MUTED))

    frags.append(rect(45, 190, 230, 60, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(160, 210, "Робоче дерево (Worktree)", size=11, bold=True, color=INK))
    frags.append(text(160, 230, "Стан: Clean / Dirty (індекс і файли)", size=10, color=MUTED))

    frags.append(rect(45, 270, 230, 70, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(160, 292, "git describe --tags --always --dirty", size=10, bold=True, color=NEG))
    frags.append(text(160, 312, "Результат: v2.4.1-14-g7a3f89b", size=10, color=INK))
    frags.append(text(160, 328, "Хеш: 0x7a3f89b, Прапорець: CLEAN", size=9, italic=True, color=MUTED))

    # Стрілка 1 -> 2
    frags.append(arrow(290, 240, 350, 240, color=INK, sw=2.0))
    frags.append(text(320, 230, "Витяг", size=10, bold=True, color=MUTED))

    # Блок 2: Генерація коду під час збірки
    b2_bg = rect(350, 60, 280, 360, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=8)
    frags.append(b2_bg)
    frags.append(text(490, 85, "2. Генератор метаданих (Build Step)", size=13, bold=True, color="#b45309"))

    frags.append(rect(365, 110, 250, 80, fill="#ffffff", stroke="#fcd34d", sw=1.2, rx=6))
    frags.append(text(490, 130, "Скрипт екстракції (CMake / Py)", size=11, bold=True, color=INK))
    frags.append(text(490, 150, "Розбір SemVer: major=2, minor=4, patch=1", size=10, color=MUTED))
    frags.append(text(490, 170, "SOURCE_DATE_EPOCH = timestamp коміту", size=10, color=MUTED))

    frags.append(rect(365, 210, 250, 90, fill="#ffffff", stroke="#fcd34d", sw=1.2, rx=6))
    frags.append(text(490, 230, "Атомарне оновлення файлу", size=11, bold=True, color=INK))
    frags.append(text(490, 250, "version_info.h.tmp -> version_info.h", size=10, color=NEG))
    frags.append(text(490, 270, "Захист кешу збірки (без зайвого rebuild)", size=9, italic=True, color=MUTED))
    frags.append(text(490, 286, "Ворота чистоти: fail якщо -dirty у релізі", size=9, bold=True, color=POS))

    frags.append(rect(365, 320, 250, 80, fill="#ffffff", stroke="#fcd34d", sw=1.2, rx=6))
    frags.append(text(490, 340, "Структура version_info_t", size=11, bold=True, color=INK))
    frags.append(text(490, 360, "Типізовані константи + бітові прапорці", size=10, color=MUTED))
    frags.append(text(490, 380, "__attribute__((section(\".version_header\")))", size=9, color=NEG))

    # Стрілка 2 -> 3
    frags.append(arrow(630, 240, 690, 240, color=INK, sw=2.0))
    frags.append(text(660, 230, "Лінковка", size=10, bold=True, color=MUTED))

    # Блок 3: Бінарний образ ELF / Firmware
    b3_bg = rect(690, 60, 280, 360, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8)
    frags.append(b3_bg)
    frags.append(text(830, 85, "3. Двійковий образ (ELF / BIN)", size=13, bold=True, color=FIELD))

    frags.append(rect(705, 110, 250, 45, fill="#ffffff", stroke="#86efac", sw=1.2, rx=6))
    frags.append(text(830, 137, "Секція коду: .text", size=11, bold=True, color=INK))

    frags.append(rect(705, 165, 250, 135, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    frags.append(text(830, 185, "СЕКЦІЯ .version_header", size=11, bold=True, color=NEG))
    frags.append(text(830, 205, "Magic: 0x56455253 (\"VERS\")", size=10, bold=True, color=INK))
    frags.append(text(830, 225, "SemVer: 2.4.1 | Build: 14", size=10, color=INK))
    frags.append(text(830, 245, "Git SHA: 7a3f89b0... | Flags: 0x00", size=10, color=INK))
    frags.append(text(830, 265, "Фіксоване зміщення у флеш / ROM", size=10, italic=True, color=MUTED))
    frags.append(text(830, 285, "Доступ ззовні: readelf / OTA / flasher", size=9, bold=True, color=FIELD))

    frags.append(rect(705, 310, 250, 45, fill="#ffffff", stroke="#86efac", sw=1.2, rx=6))
    frags.append(text(830, 337, "Секція констант: .rodata", size=11, bold=True, color=INK))

    frags.append(rect(705, 365, 250, 45, fill="#ffffff", stroke="#86efac", sw=1.2, rx=6))
    frags.append(text(830, 392, "Секція даних: .data / .bss", size=11, bold=True, color=INK))

    render(os.path.join(IMG, 'repo-state-to-binary-pipeline.svg'), W, H, *frags,
           title="Конвеєр перенесення стану репозиторію в бінарний образ")


# ── Фігура 2: Анатомія рядка git describe ─────────────────────────────────────
def fig_git_describe_anatomy():
    W, H = 960, 380
    frags = []

    frags.append(text(480, 25, "Анатомія рядка версії: з чого складається ідентифікатор git describe",
                      size=15, bold=True, color=INK))

    # Головний блок з моноширинним рядком
    main_box = rect(120, 60, 720, 65, fill="#1e293b", stroke="#0f172a", sw=2.0, rx=8)
    frags.append(main_box)

    # Сегменти версії кольоровим моноширинним текстом
    frags.append(text(200, 100, "v2.4.1", size=24, bold=True, color="#38bdf8"))
    frags.append(text(300, 100, "-", size=24, bold=True, color="#94a3b8"))
    frags.append(text(350, 100, "14", size=24, bold=True, color="#facc15"))
    frags.append(text(410, 100, "-", size=24, bold=True, color="#94a3b8"))
    frags.append(text(440, 100, "g", size=24, bold=True, color="#a78bfa"))
    frags.append(text(540, 100, "7a3f89b", size=24, bold=True, color="#4ade80"))
    frags.append(text(665, 100, "-", size=24, bold=True, color="#94a3b8"))
    frags.append(text(745, 100, "dirty", size=24, bold=True, color="#f87171"))

    # Пояснювальні картки знизу
    # Картка 1: Тег
    frags.append(rect(30, 190, 190, 160, fill="#f0f9ff", stroke="#38bdf8", sw=1.5, rx=6))
    frags.append(text(125, 215, "Найближчий тег", size=12, bold=True, color="#0284c7"))
    frags.append(text(125, 235, "v2.4.1", size=14, bold=True, color=INK))
    frags.append(text(125, 260, "Анотований або легкий", size=10, color=MUTED))
    frags.append(text(125, 280, "тег у графі предків.", size=10, color=MUTED))
    frags.append(text(125, 300, "Базова точка відліку", size=10, color=MUTED))
    frags.append(text(125, 320, "семантичної версії.", size=10, italic=True, color=MUTED))
    frags.append(arrow(125, 190, 200, 130, color="#38bdf8", sw=1.8))

    # Картка 2: Відстань у комітах
    frags.append(rect(240, 190, 180, 160, fill="#fefce8", stroke="#facc15", sw=1.5, rx=6))
    frags.append(text(330, 215, "Зсув у комітах", size=12, bold=True, color="#ca8a04"))
    frags.append(text(330, 235, "14", size=14, bold=True, color=INK))
    frags.append(text(330, 260, "Кількість комітів,", size=10, color=MUTED))
    frags.append(text(330, 280, "внесених у гілку", size=10, color=MUTED))
    frags.append(text(330, 300, "після тегу. Якщо 0 —", size=10, color=MUTED))
    frags.append(text(330, 320, "чистий реліз (тег єдиний).", size=10, italic=True, color=MUTED))
    frags.append(arrow(330, 190, 350, 130, color="#ca8a04", sw=1.8))

    # Картка 3: Префікс та Хеш
    frags.append(rect(440, 190, 230, 160, fill="#f0fdf4", stroke="#4ade80", sw=1.5, rx=6))
    frags.append(text(555, 215, "Префікс 'g' + Хеш коміту", size=12, bold=True, color="#16a34a"))
    frags.append(text(555, 235, "g7a3f89b", size=14, bold=True, color=INK))
    frags.append(text(555, 260, "'g' означає систему Git.", size=10, color=MUTED))
    frags.append(text(555, 280, "7a3f89b — скорочений", size=10, color=MUTED))
    frags.append(text(555, 300, "SHA-хеш поточного HEAD.", size=10, color=MUTED))
    frags.append(text(555, 320, "Точний крипто-стан сирців.", size=10, italic=True, color=MUTED))
    frags.append(arrow(555, 190, 520, 130, color="#16a34a", sw=1.8))

    # Картка 4: Брудний суфікс
    frags.append(rect(690, 190, 240, 160, fill="#fef2f2", stroke="#f87171", sw=1.5, rx=6))
    frags.append(text(810, 215, "Маркер модифікацій", size=12, bold=True, color=POS))
    frags.append(text(810, 235, "-dirty", size=14, bold=True, color=POS))
    frags.append(text(810, 260, "Наявні незакомічені зміни", size=10, color=MUTED))
    frags.append(text(810, 280, "в робочому дереві або індексі.", size=10, color=MUTED))
    frags.append(text(810, 300, "Блокує релізний випуск!", size=10, bold=True, color=POS))
    frags.append(text(810, 320, "Сирці не відновлювані.", size=10, italic=True, color=POS))
    frags.append(arrow(810, 190, 745, 130, color=POS, sw=1.8))

    render(os.path.join(IMG, 'git-describe-anatomy.svg'), W, H, *frags,
           title="Анатомія рядка версії git describe")


# ── Фігура 3: Структура дескриптора версії в секції .version_header ──────────
def fig_elf_version_header_layout():
    W, H = 980, 470
    frags = []

    frags.append(text(490, 25, "Двійкова розкладка структури version_info_t у секції .version_header",
                      size=15, bold=True, color=INK))

    # Таблиця зміщень і полів пам'яті
    # Заголовок таблиці
    frags.append(rect(40, 60, 900, 35, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=4))
    frags.append(text(100, 82, "Зміщення (Offset)", size=11, bold=True, color=INK))
    frags.append(text(250, 82, "Поле структури", size=11, bold=True, color=INK))
    frags.append(text(400, 82, "Тип даних", size=11, bold=True, color=INK))
    frags.append(text(540, 82, "Приклад значення", size=11, bold=True, color=INK))
    frags.append(text(760, 82, "Призначення та інваріанти", size=11, bold=True, color=INK))

    rows = [
        ("0x00 .. 0x03 (4 B)", "magic", "uint32_t", "0x56455253 ('VERS')", "Магічне число для швидкого пошуку в дампі"),
        ("0x04 .. 0x05 (2 B)", "struct_version", "uint16_t", "0x0001 (v1)", "Версія самої структури дескриптора"),
        ("0x06 .. 0x07 (2 B)", "flags", "uint16_t", "0x0001 (BIT_DIRTY)", "Бітові прапорці (Dirty, Debug, Prerelease, CI)"),
        ("0x08 .. 0x09 (2 B)", "major", "uint16_t", "2", "Старший номер версії (злам сумісності)"),
        ("0x0A .. 0x0B (2 B)", "minor", "uint16_t", "4", "Молодший номер (нова сумісна функціональність)"),
        ("0x0C .. 0x0D (2 B)", "patch", "uint16_t", "1", "Номер патчу (виправлення дефектів)"),
        ("0x0E .. 0x0F (2 B)", "reserved", "uint16_t", "0x0000", "Вирівнювання до 32-бітної межі"),
        ("0x10 .. 0x13 (4 B)", "commit_count", "uint32_t", "14", "Кількість комітів після останнього тегу"),
        ("0x14 .. 0x1B (8 B)", "git_sha_short", "uint8_t[8]", "\"7a3f89b\\0\"", "Скорочений криптографічний хеш коміту HEAD"),
        ("0x1C .. 0x23 (8 B)", "timestamp", "uint64_t", "1724803200", "Час коміту (SOURCE_DATE_EPOCH, Unix time)"),
        ("0x24 .. 0x43 (32 B)", "tag_name", "char[32]", "\"v2.4.1\\0...\"", "Рядок назви найближчого тегу в репозиторії"),
        ("0x44 .. 0x47 (4 B)", "crc32", "uint32_t", "0xA3B94F12", "Контрольна сума CRC32 заголовка для валідації"),
    ]

    y = 100
    for i, (off, name, typ, val, desc) in enumerate(rows):
        bg_col = "#ffffff" if i % 2 == 0 else "#f8fafc"
        if "magic" in name:
            bg_col = "#eff6ff"
        elif "flags" in name:
            bg_col = "#fef2f2"
        elif "crc32" in name:
            bg_col = "#f0fdf4"

        frags.append(rect(40, y, 900, 27, fill=bg_col, stroke="#cbd5e1", sw=1.0, rx=0))
        frags.append(text(100, y + 18, off, size=10, color=INK))
        frags.append(text(250, y + 18, name, size=10, bold=True, color=NEG if "magic" in name else (POS if "flags" in name else INK)))
        frags.append(text(400, y + 18, typ, size=10, color=MUTED))
        frags.append(text(540, y + 18, val, size=10, bold=True, color=INK))
        frags.append(text(760, y + 18, desc, size=10, italic=True, color=INK))
        y += 27

    frags.append(rect(40, y + 10, 900, 30, fill="#f1f5f9", stroke="#94a3b8", sw=1.0, rx=4))
    frags.append(text(490, y + 29, "Загальний розмір фіксованого заголовка: 72 байти (0x48). Вирівнювання: 8 байтів.",
                      size=10, bold=True, color=INK))

    render(os.path.join(IMG, 'elf-version-header-layout.svg'), W, H, *frags,
           title="Двійкова розкладка структури version_info_t")


# ── Фігура 4: Дерево рішень і ворота чистоти збірки (Release Build Gate) ─────
def fig_dirty_build_release_gate():
    W, H = 980, 480
    frags = []

    frags.append(text(490, 25, "Дерево перевірок у Release Build Gate: фільтрація релізних і чорнових бінарників",
                      size=15, bold=True, color=INK))

    # Початок процесу збірки
    b_start, _, _ = textbox(490, 65, "Старт конвеєра збірки (CI / Developer Build)\nКоманда: make release / cmake --build",
                            size=11, bold=True, fill="#ffffff", stroke=LINE, sw=1.5, pad=8)
    frags.append(b_start)

    frags.append(arrow(490, 90, 490, 125, color=INK, sw=1.8))

    # Ромб / Блок 1: Перевірка git status --porcelain
    b_check1, _, _ = textbox(490, 155, "Перевірка 1: Чи чисте робоче дерево?\n(git status --porcelain повертає порожній вивід?)",
                             size=11, bold=True, fill="#fffbeb", stroke="#d97706", sw=1.5, pad=8)
    frags.append(b_check1)

    # Гілка НІ (Брудне дерево)
    frags.append(arrow(340, 155, 200, 155, color=POS, sw=2.0))
    frags.append(text(270, 145, "НІ (Є зміни)", size=10, bold=True, color=POS))

    # Блок обробки брудного дерева
    b_dirty, _, _ = textbox(200, 220, "Виявлено -dirty стан\nПрапорець: BUILD_FLAG_DIRTY",
                            size=11, bold=True, fill="#fef2f2", stroke=POS, sw=1.5, pad=8)
    frags.append(b_dirty)
    frags.append(arrow(200, 175, 200, 195, color=POS, sw=1.8))

    # Перевірка профілю збірки для брудного дерева
    frags.append(arrow(200, 245, 200, 280, color=POS, sw=1.8))
    b_prof_check, _, _ = textbox(200, 310, "Цільовий профіль збірки?\n(Target == RELEASE ?)",
                                 size=11, bold=True, fill="#fff9db", stroke="#f59e0b", sw=1.5, pad=8)
    frags.append(b_prof_check)

    # Релізний профіль + Dirty -> Помилка
    frags.append(arrow(120, 310, 80, 360, color=POS, sw=2.0))
    b_fail, _, _ = textbox(80, 405, "РЕЖИМ RELEASE:\nВІДХИЛЕННЯ ЗБІРКИ\nПомилка: exit code 1\nЗаборонено випускати бінарник\nіз незбереженими сирцями",
                           size=10, bold=True, fill="#fee2e2", stroke=POS, sw=2.0, pad=8)
    frags.append(b_fail)

    # Дев профіль + Dirty -> Дозволено з маркуванням
    frags.append(arrow(280, 310, 320, 360, color="#64748b", sw=1.8))
    b_dev_ok, _, _ = textbox(320, 405, "РЕЖИМ DEBUG / DEV:\nДОЗВОЛЕНО З МАРКУВАННЯМ\nГенерація прапорця DIRTY\nЯвний суфікс у версії\n(Для локального тестування)",
                             size=10, bold=True, fill="#f1f5f9", stroke="#64748b", sw=1.5, pad=8)
    frags.append(b_dev_ok)

    # Гілка ТАК (Чисте дерево)
    frags.append(arrow(640, 155, 780, 155, color=FIELD, sw=2.0))
    frags.append(text(710, 145, "ТАК (Чисто)", size=10, bold=True, color=FIELD))

    # Блок перевірки тегу
    b_check2, _, _ = textbox(780, 220, "Перевірка 2: Чи є точний тег на HEAD?\n(git describe --exact-match)",
                             size=11, bold=True, fill="#eff6ff", stroke=NEG, sw=1.5, pad=8)
    frags.append(b_check2)
    frags.append(arrow(780, 175, 780, 195, color=FIELD, sw=1.8))

    # Точний тег є -> Офіційний реліз
    frags.append(arrow(720, 245, 650, 320, color=FIELD, sw=2.0))
    frags.append(text(660, 275, "ТАК (v2.4.1)", size=10, bold=True, color=FIELD))
    b_official, _, _ = textbox(630, 405, "ОФІЦІЙНИЙ РЕЛІЗ (RELEASE)\nВерсія: v2.4.1 (Чиста)\nВідсутній суфікс комітів\nПрапорці: RELEASE_BUILD\nАртефакт іде в прод/OTA",
                               size=10, bold=True, fill="#dcfce7", stroke=FIELD, sw=2.0, pad=8)
    frags.append(b_official)

    # Точного тегу немає, але дерево чисте -> Проміжний пре-реліз / snapshot
    frags.append(arrow(840, 245, 910, 320, color=NEG, sw=1.8))
    frags.append(text(900, 275, "НІ (+14 комітів)", size=10, bold=True, color=NEG))
    b_snapshot, _, _ = textbox(910, 405, "ЗНІМОК ГІЛКИ (SNAPSHOT)\nВерсія: v2.4.1-14-g7a3f89b\nОднозначний крипто-стан\nТестовий артефакт (Staging/CI)\nБезпечний для аналізу аварій",
                               size=10, bold=True, fill="#eff6ff", stroke=NEG, sw=1.5, pad=8)
    frags.append(b_snapshot)

    render(os.path.join(IMG, 'dirty-build-release-gate.svg'), W, H, *frags,
           title="Дерево перевірок у Release Build Gate")


if __name__ == '__main__':
    fig_repo_state_to_binary_pipeline()
    fig_git_describe_anatomy()
    fig_elf_version_header_layout()
    fig_dirty_build_release_gate()
    print("Всі фігури згенеровано успішно.")
