# -*- coding: utf-8 -*-
"""Фігури до теми «Гігієна заголовків і час перезбірки»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Каскад транзитивних включень проти графа з Forward Declarations ───────
def fig_include_graph_explosion():
    W, H = 960, 480
    f = []

    f.append(text(480, 25, "Транзитивний каскад включень проти розв'язаного графа з неповними типами", size=16, color=INK, anchor="middle", bold=True))

    # Ліва колонка: Антипатерн — Транзитивне пекло
    f.append(rect(30, 50, 430, 410, fill="#fdf7f7", stroke=POS, sw=1.5, rx=8))
    f.append(text(245, 75, "Транзитивний каскад: O(N · M) токенів", size=14, color=POS, bold=True))

    f.append(fitbox(50, 95, 175, 65, "UserSession.h\n#include <vector>\n#include <string>\n#include \"Database.h\"", size=11, fill="#fff", stroke=POS))
    f.append(fitbox(265, 95, 175, 65, "Database.h\n#include <memory>\n#include <map>\n#include \"Network.h\"", size=11, fill="#fff", stroke=POS))

    f.append(arrow(225, 127, 263, 127, color=POS, sw=2))

    f.append(fitbox(265, 180, 175, 65, "Network.h\n#include <iostream>\n#include <openssl/ssl.h>", size=11, fill="#fff", stroke=POS))
    f.append(arrow(352, 160, 352, 178, color=POS, sw=2))

    f.append(fitbox(50, 265, 175, 80, "AuthHandler.cpp\n#include \"UserSession.h\"\nКопіює 850 000 рядків\nЧас парсингу: 1.8 с", size=11, fill="#ffebee", stroke=POS))
    f.append(fitbox(265, 265, 175, 80, "BillingService.cpp\n#include \"UserSession.h\"\nКопіює 850 000 рядків\nЧас парсингу: 1.8 с", size=11, fill="#ffebee", stroke=POS))

    f.append(arrow(137, 160, 137, 263, color=POS, sw=2))
    f.append(arrow(352, 245, 352, 263, color=POS, sw=2))

    f.append(fitbox(50, 365, 390, 80, "Наслідок: Зміна 1 приватного поля в Network.h\nперекомпільовує UserSession.h, Database.h,\nAuthHandler.cpp та BillingService.cpp.\nПовна перезбірка 400 TU: ~12 хвилин.", size=11, fill="#fbe9e7", stroke=POS, bold=False))

    # Права колонка: Ідеальна архітектура — Forward Declarations
    f.append(rect(490, 50, 440, 410, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(710, 75, "Розв'язані залежності: Forward Declarations", size=14, color=FIELD, bold=True))

    f.append(fitbox(510, 95, 185, 65, "UserSession.h\nclass Database;\nclass Network;\nstd::unique_ptr<Database> db;", size=11, fill="#fff", stroke=FIELD))
    f.append(fitbox(725, 95, 185, 65, "Database.h\nclass Network;\nstruct SslContext;\nNetwork* m_net;", size=11, fill="#fff", stroke=FIELD))

    f.append(arrow(695, 127, 723, 127, color=FIELD, sw=2))

    f.append(fitbox(510, 180, 185, 65, "AuthHandler.cpp\n#include \"UserSession.h\"\n#include \"Database.h\"\nПрепроцесинг: 12 000 рядків", size=11, fill="#e8f5e9", stroke=FIELD))
    f.append(fitbox(725, 180, 185, 65, "Network.h\n(ізольований заголовок)", size=11, fill="#fff", stroke=FIELD))

    f.append(arrow(602, 160, 602, 178, color=FIELD, sw=2))

    f.append(fitbox(510, 265, 400, 80, "UserSession.cpp (файл реалізації)\n#include \"UserSession.h\"\n#include \"Database.h\"\n#include \"Network.h\"\nПовний тип розгортається лише тут, локально в одному TU.", size=11, fill="#fff", stroke=FIELD))

    f.append(arrow(602, 245, 602, 263, color=FIELD, sw=2))
    f.append(arrow(817, 245, 817, 263, color=FIELD, sw=2))

    f.append(fitbox(510, 365, 400, 80, "Результат: Зміна приватних деталей Network.h\nперекомпільовує ТІЛЬКИ Network.cpp та UserSession.cpp.\nAuthHandler та BillingService НЕ чіпаються.\nЧас інкрементальної збірки: 1.5 секунди.", size=11, fill="#e8f8f0", stroke=FIELD))

    render(os.path.join(OUT, 'include-graph-explosion.svg'), W, H, *f)


# ── 2. Механізм Include Guards проти #pragma once ────────────────────────────
def fig_pragma_once_vs_guard():
    W, H = 960, 460
    f = []

    f.append(text(480, 25, "Внутрішній механізм: Include Guard (MIOpt) проти #pragma once (FileID Table)", size=16, color=INK, anchor="middle", bold=True))

    # Секція 1: Include Guard
    f.append(rect(30, 50, 435, 390, fill="#fdfdfe", stroke=NEG, sw=1.5, rx=8))
    f.append(text(247, 75, "Include Guard (#ifndef ... #define)", size=14, color=NEG, bold=True))

    f.append(fitbox(50, 95, 395, 75, "1. Препроцесор зустрічає #include \"header.h\"\nВикликає системний open() / read() файлу з диска.\nПочинає сканування та лексичний аналіз перших токенів.", size=11, fill="#f4f6f8", stroke=LINE))

    f.append(arrow(247, 170, 247, 195, color=NEG, sw=2))

    f.append(fitbox(50, 195, 395, 95, "2. Перевірка макросу в Symbol Table\n• Якщо HEADER_H не визначено → парсимо тіло і робимо #define\n• Якщо визначено → пропускаємо текст до #endif.\nОптимізація MIOpt: якщо файл чистий від тексту ззовні guard,\nкомпілятор кешує макрос і не викликає open() повторно.", size=11, fill="#eef2fa", stroke=NEG))

    f.append(arrow(247, 290, 247, 315, color=NEG, sw=2))

    f.append(fitbox(50, 315, 395, 110, "Властивості та обмеження:\n✓ 100% переносимий стандарт C та C++.\n✗ Ризик колізій макросів (наприклад, _COMMON_H_ у двох лібах).\n✗ Якщо до або після guard є коментар чи токен, MIOpt\nвимикається, змушуючи читати файл на кожне включення.", size=11, fill="#fff", stroke=LINE))

    # Секція 2: #pragma once
    f.append(rect(495, 50, 435, 390, fill="#fdfdfe", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(712, 75, "#pragma once (Кеш дескрипторів файлів)", size=14, color=FIELD, bold=True))

    f.append(fitbox(515, 95, 395, 75, "1. Препроцесор зустрічає #include \"header.h\"\nОтримує File ID файлу (Linux: st_dev + st_ino; Win: FileIndex).\nПеревіряє хеш-таблицю visited_files у пам'яті компілятора.", size=11, fill="#f4f6f8", stroke=LINE))

    f.append(arrow(712, 170, 712, 195, color=FIELD, sw=2))

    f.append(fitbox(515, 195, 395, 95, "2. Миттєве відсікання на рівні фронтенду\n• Якщо File ID є в таблиці → файл взагалі НЕ відкривається,\n  токенайзер і парсер пропускають директиву миттєво.\n• Якщо File ID відсутній → читаємо файл і додаємо ID в таблицю.", size=11, fill="#e8f8f0", stroke=FIELD))

    f.append(arrow(712, 290, 712, 315, color=FIELD, sw=2))

    f.append(fitbox(515, 315, 395, 110, "Властивості та обмеження:\n✓ Найвища швидкість: нульовий парсинг при повторі.\n✓ Немає забруднення препроцесора макросами guard.\n✗ Нестандартне розширення (де-факто підтримується всіма).\n✗ Пастка Symlinks/Hardlinks або копіювання в build-каталог.", size=11, fill="#fff", stroke=LINE))

    render(os.path.join(OUT, 'pragma-once-vs-guard.svg'), W, H, *f)


# ── 3. Порівняння конвеєрів: Текстовий include, PCH та Модулі C++20 ──────────
def fig_compilation_timeline_pch_modules():
    W, H = 960, 470
    f = []

    f.append(text(480, 25, "Конвеєри трансляції: Текстовий #include проти PCH та C++20 Модулів", size=16, color=INK, anchor="middle", bold=True))

    # 1. Текстовий include
    f.append(text(40, 60, "1. Текстове включення (#include): O(N) парсинг на кожен TU", size=13, color=POS, anchor="start", bold=True))
    f.append(fitbox(40, 75, 160, 50, "TU 1: Препроцесинг\nSTL (400k рядків)", size=10, fill="#ffebee", stroke=POS))
    f.append(fitbox(205, 75, 160, 50, "TU 1: Парсинг AST\nта інстанціювання", size=10, fill="#ffcdd2", stroke=POS))
    f.append(fitbox(370, 75, 110, 50, "TU 1: Codegen\nОб'єкт .o", size=10, fill="#e0e0e0", stroke=LINE))

    f.append(fitbox(500, 75, 160, 50, "TU 2: Препроцесинг\nSTL (400k рядків)", size=10, fill="#ffebee", stroke=POS))
    f.append(fitbox(665, 75, 160, 50, "TU 2: Парсинг AST\nта інстанціювання", size=10, fill="#ffcdd2", stroke=POS))
    f.append(fitbox(830, 75, 90, 50, "TU 2: .o", size=10, fill="#e0e0e0", stroke=LINE))

    # 2. PCH (Precompiled Headers)
    f.append(text(40, 160, "2. Попередньо скомпільовані заголовки (PCH): Дамп AST стану", size=13, color=NEG, anchor="start", bold=True))
    f.append(fitbox(40, 175, 230, 50, "Один раз: Збірка pch.h\nSTL -> pch.gch (дамп AST 180MB)", size=10, fill="#e8eaf6", stroke=NEG))

    f.append(fitbox(300, 175, 150, 50, "TU 1: Завантаження PCH\nМиттєве відображення пам'яті", size=10, fill="#c5cae9", stroke=NEG))
    f.append(fitbox(455, 175, 130, 50, "TU 1: Парсинг коду\nта генерація .o", size=10, fill="#e0e0e0", stroke=LINE))

    f.append(fitbox(610, 175, 150, 50, "TU 2: Завантаження PCH\nМиттєве відображення пам'яті", size=10, fill="#c5cae9", stroke=NEG))
    f.append(fitbox(765, 175, 130, 50, "TU 2: Парсинг коду\nта генерація .o", size=10, fill="#e0e0e0", stroke=LINE))

    # 3. C++20 Модулі
    f.append(text(40, 260, "3. C++20 Модулі (import std; / BMI): Семантична бінарна ізоляція", size=13, color=FIELD, anchor="start", bold=True))
    f.append(fitbox(40, 275, 230, 50, "Один раз: Збірка модуля std\nГенерація std.pcm / std.ifc (BMI)", size=10, fill="#e8f5e9", stroke=FIELD))

    f.append(fitbox(300, 275, 160, 50, "TU 1: import std;\nШвидке читання символів BMI\nЖодного витоку макросів!", size=10, fill="#c8e6c9", stroke=FIELD))
    f.append(fitbox(465, 275, 120, 50, "TU 1: Codegen\nЧистий .o", size=10, fill="#e0e0e0", stroke=LINE))

    f.append(fitbox(610, 275, 160, 50, "TU 2: import std;\nШвидке читання символів BMI\nІзольований контекст", size=10, fill="#c8e6c9", stroke=FIELD))
    f.append(fitbox(775, 275, 120, 50, "TU 2: Codegen\nЧистий .o", size=10, fill="#e0e0e0", stroke=LINE))

    # Порівняльна плашка внизу
    f.append(rect(40, 355, 880, 95, fill="#fcfcfc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(480, 375, "Порівняльний підсумок властивостей архітектур", size=12, color=INK, bold=True))
    f.append(text(55, 400, "• Текстові заголовки: Макроси витікають, парсинг O(N · M), залежність від порядку включення.", size=11, color=POS, anchor="start"))
    f.append(text(55, 420, "• PCH: Швидка чиста збірка, але монолітний, вразливий до прапорців компілятора та макросів.", size=11, color=NEG, anchor="start"))
    f.append(text(55, 440, "• C++20 Модулі: Повна ізоляція символів, відсутність експорту макросів, максимальна швидкість.", size=11, color=FIELD, anchor="start"))

    render(os.path.join(OUT, 'compilation-timeline-pch-modules.svg'), W, H, *f)


# ── 4. Флеймграф профілювання компіляції за ftime-trace ──────────────────────
def fig_ftime_trace_flamegraph():
    W, H = 960, 440
    f = []

    f.append(text(480, 25, "Ієрархія витрат часу компіляції у Clang -ftime-trace (Chrome Tracing)", size=16, color=INK, anchor="middle", bold=True))

    # Контейнер флеймграфа
    f.append(rect(40, 55, 880, 310, fill="#f9f9fb", stroke=LINE, sw=1.5, rx=8))

    # Рівень 1: Загальний час TU
    f.append(fitbox(55, 70, 850, 45, "ExecuteCompiler: Total Time 4.82 s (UserSession.cpp)", size=12, fill="#e2e8f0", stroke="#475569", bold=True))

    # Рівень 2: Frontend проти Backend
    f.append(fitbox(55, 125, 620, 45, "Frontend: 3.52 s (73% часу) — Синтаксичний аналіз та інстанціювання", size=11, fill="#fed7aa", stroke="#ea580c", bold=True))
    f.append(fitbox(685, 125, 220, 45, "Backend: 1.30 s (27%)\nОптимізація та кодогенерація", size=11, fill="#e2e8f0", stroke="#64748b"))

    # Рівень 3: Деталізація фронтенду (Source vs Instantiation)
    f.append(fitbox(55, 180, 380, 45, "Source: <boost/json.hpp> (2.15 s)\nПарсинг 90 000 рядків чужого AST", size=11, fill="#fecaca", stroke=POS))
    f.append(fitbox(445, 180, 230, 45, "InstantiateFunction / Class (1.10 s)\nШаблони std::map, vector", size=11, fill="#fed7aa", stroke="#ea580c"))

    # Рівень 4: Деталізація Source
    f.append(fitbox(55, 235, 210, 45, "Source: <boost/spirit.hpp>\n(1.35 s)", size=10, fill="#fee2e2", stroke=POS))
    f.append(fitbox(270, 235, 165, 45, "Source: <regex>\n(0.65 s)", size=10, fill="#fee2e2", stroke=POS))
    f.append(fitbox(445, 235, 110, 45, "ParseClass\nSession (0.08 s)", size=10, fill="#dcfce7", stroke=FIELD))
    f.append(fitbox(560, 235, 115, 45, "OptFunction\nserialize (0.4s)", size=10, fill="#f1f5f9", stroke=LINE))

    # Рівень 5: Локальний код
    f.append(fitbox(55, 290, 850, 40, "Локальний код UserSession.cpp займає лише 0.12 s (2.5% загального часу TU)!\n97.5% часу компілятор парсив транзитивно підключені важкі бібліотеки.", size=11, fill="#fff", stroke=POS, bold=True))

    # Пояснення знизу
    f.append(fitbox(40, 380, 880, 45, "Діагностичний висновок ClangBuildAnalyzer: Винесення <boost/json.hpp> у .cpp через Pimpl\nабо винесення у PCH скорочує час збірки файлу з 4.82 с до 0.45 с (прискорення у 10.7 разів).", size=11, fill="#eff6ff", stroke=NEG))

    render(os.path.join(OUT, 'ftime-trace-flamegraph.svg'), W, H, *f)


def main():
    fig_include_graph_explosion()
    fig_pragma_once_vs_guard()
    fig_compilation_timeline_pch_modules()
    fig_ftime_trace_flamegraph()
    print("Всі фігури успішно згенеровано.")


if __name__ == '__main__':
    main()
