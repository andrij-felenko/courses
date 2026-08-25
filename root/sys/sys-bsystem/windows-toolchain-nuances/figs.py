# -*- coding: utf-8 -*-
"""Фігури до теми «Нюанси Windows: MSVC, рантайми, шляхи, кодування»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

PANEL = "#f8fafc"
MSVC_COLOR = "#047857"
DLL_COLOR = "#1d4ed8"
ERR_COLOR = "#b91c1c"
WARN_BG = "#fef2f2"
WARN_STROKE = "#ef4444"
OK_BG = "#f0fdf4"
OK_STROKE = "#22c55e"


# ── 1. Конфлікт рантаймів CRT та руйнування купи (Heap Corruption) ────────────
def fig_crt_heap_mismatch():
    W, H = 1080, 520
    p = []

    # Загальний простір процесу
    p.append(rect(20, 20, 1040, 480, fill=PANEL, stroke=LINE, sw=1.5))
    p.append(text(540, 45, "Адресний простір одного процесу (Windows Virtual Memory)", size=16, bold=True))

    # Лівий блок: Модуль EXE (зібраний з /MD)
    p.append(rect(40, 70, 430, 410, fill=BG, stroke=DLL_COLOR, sw=1.8))
    p.append(text(255, 95, "Головний застосунок (app.exe — /MD)", size=14.5, bold=True, color=DLL_COLOR))
    p.append(fitbox(60, 115, 390, 45, "Динамічний рантайм: ucrtbase.dll\nДескриптор купи: _crtheap_A (HeapCreate)", size=12.5, fill="#eff6ff", stroke=DLL_COLOR))
    p.append(fitbox(60, 175, 390, 55, "Виклик бібліотеки:\nvoid* ptr = mylib_get_data();", size=12.5, fill=BG))
    p.append(arrow(255, 235, 255, 265, color=LINE, sw=1.5))
    p.append(fitbox(60, 265, 390, 60, "Спроба звільнення чужої пам'яті:\nfree(ptr);  → HeapFree(_crtheap_A, 0, ptr);", size=12.5, fill=WARN_BG, stroke=ERR_COLOR, bold=True))
    p.append(arrow(255, 330, 255, 360, color=ERR_COLOR, sw=1.8))
    p.append(fitbox(60, 360, 390, 100, "Крах процесу: STATUS_HEAP_CORRUPTION (0xC0000374)\nМенеджер купи NT виявляє, що блок пам'яті ptr\nне належить дескриптору _crtheap_A або пошкоджено\nслужбові метадані сегмента купи.", size=12, fill="#fee2e2", stroke=ERR_COLOR, color=ERR_COLOR, bold=True))

    # Правий блок: Модуль DLL (зібраний з /MT)
    p.append(rect(610, 70, 430, 410, fill=BG, stroke=MSVC_COLOR, sw=1.8))
    p.append(text(825, 95, "Динамічна бібліотека (plugin.dll — /MT)", size=14.5, bold=True, color=MSVC_COLOR))
    p.append(fitbox(630, 115, 390, 45, "Статичний рантайм: вшита копія libucrt.lib\nДескриптор купи: _crtheap_B (HeapCreate)", size=12.5, fill="#ecfdf5", stroke=MSVC_COLOR))
    p.append(fitbox(630, 175, 390, 70, "Виділення пам'яті всередині DLL:\nvoid* ptr = malloc(1024);\n→ HeapAlloc(_crtheap_B, 0, 1024);\nПовертає адресу блоку з Купи B", size=12, fill=BG))
    p.append(fitbox(630, 265, 390, 65, "Фізичний блок пам'яті [ Купа B ]\n[ Метадані купи B | Корисні дані 1024 B ]\nАдреса ptr вказує на цей сегмент", size=12, fill="#fef3c7", stroke="#d97706"))

    # Стрілка передачі покажчика між модулями
    p.append(arrow(630, 202, 450, 202, color=DLL_COLOR, sw=1.8))
    p.append(textbox(540, 187, "Передача ptr", size=11, fill="#ffffff", stroke=DLL_COLOR)[0])

    # Стрілка невідповідності дескрипторів
    p.append(line(450, 295, 630, 295, color=ERR_COLOR, sw=1.8, dash="4,4"))
    p.append(textbox(540, 310, "Невідповідність:\n_crtheap_A != B", size=10.5, pad=5, fill="#ffffff", stroke=ERR_COLOR, color=ERR_COLOR)[0])

    render(os.path.join(IMG, "crt-heap-mismatch.svg"), W, H, *p)


# ── 2. Механізм експорту та імпорту символів у Windows DLL ────────────────────
def fig_dll_import_export_flow():
    W, H = 1060, 500
    p = []

    # Ліва частина: Збірка DLL
    p.append(rect(30, 30, 460, 440, fill=PANEL, stroke=DLL_COLOR, sw=1.5))
    p.append(text(260, 60, "Створення бібліотеки (mylib.dll)", size=15, bold=True, color=DLL_COLOR))

    p.append(fitbox(50, 85, 420, 65, "Сирцевий код бібліотеки (.cpp / .h):\n#define MYLIB_API __declspec(dllexport)\nMYLIB_API int calculate_sum(int a, int b);", size=12.5, fill=BG))
    p.append(arrow(260, 155, 260, 185, color=LINE, sw=1.5))

    p.append(fitbox(50, 185, 420, 60, "Компіляція: cl.exe /c\nГенерує секцію .drectve в mylib.obj\nз директивою -export:calculate_sum", size=12.5, fill=BG))
    p.append(arrow(260, 250, 260, 280, color=LINE, sw=1.5))

    p.append(fitbox(50, 280, 420, 80, "Компонування: link.exe /DLL\n1. Створює mylib.dll (PE-образ з таблицею EAT)\n2. Генерує mylib.lib (Import Library — бібліотека імпорту)\n   що містить записи для прив'язки до IAT", size=12, fill="#e0f2fe", stroke=DLL_COLOR))
    p.append(arrow(260, 365, 260, 395, color=LINE, sw=1.5))

    p.append(fitbox(50, 395, 420, 60, "Артефакти на диску:\n• mylib.dll (виконуваний код + EAT)\n• mylib.lib (короткі COFF-заглушки імпорту)", size=12.5, fill=OK_BG, stroke=OK_STROKE))

    # Права частина: Збірка споживача EXE
    p.append(rect(570, 30, 460, 440, fill=PANEL, stroke=MSVC_COLOR, sw=1.5))
    p.append(text(800, 60, "Споживач бібліотеки (app.exe)", size=15, bold=True, color=MSVC_COLOR))

    p.append(fitbox(590, 85, 420, 65, "Сирцевий код застосунку (.cpp):\n#define MYLIB_API __declspec(dllimport)\nMYLIB_API int calculate_sum(int a, int b);", size=12.5, fill=BG))
    p.append(arrow(800, 155, 800, 185, color=LINE, sw=1.5))

    p.append(fitbox(590, 185, 420, 60, "Компіляція з __declspec(dllimport):\nГенерує пряме непряме звернення:\ncall qword ptr [__imp_calculate_sum]", size=12.5, fill=BG))
    p.append(arrow(800, 250, 800, 280, color=LINE, sw=1.5))

    p.append(fitbox(590, 280, 420, 80, "Компонування: link.exe app.obj mylib.lib\nЛінкер бере символ __imp_calculate_sum з mylib.lib\nі формує таблицю IAT (Import Address Table)\nу заголовку app.exe", size=12, fill="#ecfdf5", stroke=MSVC_COLOR))
    p.append(arrow(800, 365, 800, 395, color=LINE, sw=1.5))

    p.append(fitbox(590, 395, 420, 60, "Завантаження процесу (NT Loader):\nЗавантажувач кладе адресу функції з mylib.dll\nбезпосередньо у комірку IAT app.exe", size=12.5, fill=OK_BG, stroke=OK_STROKE))

    # Міжмодульний зв'язок: mylib.lib передається лінкеру
    p.append(arrow(470, 320, 590, 320, color="#d97706", sw=1.8))
    p.append(textbox(530, 305, "mylib.lib", size=11, pad=5, fill="#ffffff", stroke="#d97706", color="#d97706", bold=True)[0])

    render(os.path.join(IMG, "dll-import-export-flow.svg"), W, H, *p)


# ── 3. Конвеєр шляхів, префікс \\?\ та кодування символів ─────────────────────
def fig_path_encoding_pipeline():
    W, H = 1000, 490
    p = []

    # Рівень 1: Вихідний код та компілятор MSVC
    p.append(rect(30, 25, 940, 110, fill=PANEL, stroke=LINE, sw=1.5))
    p.append(text(500, 48, "Рівень коду та компілятора (MSVC cl.exe)", size=14.5, bold=True))
    p.append(fitbox(50, 65, 420, 55, "Вихідний текст у UTF-8 без BOM:\nconst char* path = \"C:/проєкт/data.txt\";", size=12, fill=BG))
    p.append(fitbox(530, 65, 420, 55, "Прапорець /utf-8:\n• /source-charset:utf-8 (парсинг коду)\n• /execution-charset:utf-8 (байти в .rdata)", size=12, fill="#eff6ff", stroke=DLL_COLOR))

    p.append(arrow(500, 135, 500, 165, color=LINE, sw=1.5))

    # Рівень 2: Підсистема процесу та маніфест
    p.append(rect(30, 165, 940, 130, fill=PANEL, stroke=LINE, sw=1.5))
    p.append(text(500, 188, "Рівень середовища процесу (PEB / Win32 Subsystem)", size=14.5, bold=True))
    p.append(fitbox(50, 205, 420, 75, "Традиційний режим (Legacy ACP):\nANSI кодова сторінка (CP1251 / CP1252)\nВиклики *A конвертують байти через ACP;\nсимволи поза сторінкою замінюються на '?'", size=11.5, fill=WARN_BG, stroke=ERR_COLOR))
    p.append(fitbox(530, 205, 420, 75, "Маніфест застосунку (Windows 10 1903+):\n<activeCodePage>UTF-8</activeCodePage>\nВстановлює CP_UTF8 (65001) як системну ACP;\nфункції *A сприймають char* як чесний UTF-8", size=11.5, fill=OK_BG, stroke=OK_STROKE))

    p.append(arrow(500, 295, 500, 325, color=LINE, sw=1.5))

    # Рівень 3: Файлова система та ліміти довжини
    p.append(rect(30, 325, 940, 140, fill=PANEL, stroke=LINE, sw=1.5))
    p.append(text(500, 348, "Рівень Win32 API та ядра NT (Filesystem Limits)", size=14.5, bold=True))
    p.append(fitbox(50, 365, 420, 85, "Обмеження MAX_PATH (260 символів):\nCreateFileA / fopen / GetFullPathName\nФіксований буфер: char szPath[260];\nПеревищення → ERROR_PATH_NOT_FOUND (3)", size=11.5, fill=WARN_BG, stroke=ERR_COLOR))
    p.append(fitbox(530, 365, 420, 85, "Розширений префікс \\\\?\\ та UTF-16LE:\nCreateFileW(L\"\\\\?\\\\C:\\\\довгий_шлях...\", ...)\nОбходить перевірку MAX_PATH та нормалізацію;\nЯдро NT (NtCreateFile) підтримує 32 767 символів", size=11.5, fill=OK_BG, stroke=OK_STROKE))

    render(os.path.join(IMG, "path-encoding-pipeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_crt_heap_mismatch()
    fig_dll_import_export_flow()
    fig_path_encoding_pipeline()
    print("All figures generated successfully.")
