# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: Розрив відтворюваності (Abstract Intent vs Concrete Lock) ───────
def fig_reproducibility_gap():
    W, H = 940, 450
    f = []

    # Заголовки панелей
    f.append(text(230, 40, "Абстрактна декларація (pyproject.toml)", size=14, bold=True, color=POS))
    f.append(text(230, 60, "Діапазони версій · Недетермінований стан", size=11, color=MUTED))

    f.append(text(710, 40, "Файл-замок (uv.lock / poetry.lock)", size=14, bold=True, color=FIELD))
    f.append(text(710, 60, "Точні версії · Повний транзитивний граф · Хеші SHA-256", size=11, color=MUTED))

    # Ліва колонка — Абстрактний вхід
    box_req, _, _ = textbox(230, 120, "dependencies = [\n  \"fastapi >= 0.110.0\",\n  \"pydantic >= 2.0, < 3.0\"\n]",
                            size=12, min_w=340, fill="#fdf2f2", stroke=POS, sw=1.5)
    f.append(box_req)

    # Дві різні збірки у часі (проблема дрейфу)
    box_run1, _, _ = textbox(230, 230, "Збірка розробника (День 1):\n• fastapi == 0.110.0\n• pydantic == 2.6.4\n• pydantic-core == 2.16.3\nРезультат: Працює стабільно",
                             size=11, min_w=340, fill=FILL, stroke=MUTED)
    f.append(box_run1)

    box_run2, _, _ = textbox(230, 360, "Збірка на CI / Продакшені (День 30):\n• fastapi == 0.110.0\n• pydantic == 2.7.0 (мінорне оновлення)\n• pydantic-core == 2.18.1 (новий баг/зміна поведінки)\nРезультат: Помилка або падіння в рантаймі!",
                             size=11, min_w=340, fill="#fdecea", stroke=POS, sw=1.5)
    f.append(box_run2)

    f.append(arrow(230, 160, 230, 195, color=MUTED))
    f.append(text(245, 180, "дрейф версій", size=10, color=MUTED, anchor="start"))
    f.append(arrow(230, 275, 230, 310, color=POS))
    f.append(text(245, 295, "неконтрольоване оновлення", size=10, color=POS, anchor="start"))

    # Центральний розділювач
    f.append(line(470, 30, 470, 420, color=LINE, sw=1, dash="4,4"))

    # Права колонка — Детермінований замок
    box_lock, _, _ = textbox(710, 140, "[[package]]\nname = \"fastapi\"\nversion = \"0.110.0\"\nsdist = { hash = \"sha256:4a8e...\" }\n\n[[package]]\nname = \"pydantic\"\nversion = \"2.6.4\"\nwheels = [\n  { file = \"...cp312-manylinux_x86_64.whl\", hash = \"sha256:7b1c...\" }\n]",
                             size=11, min_w=380, fill="#eafaf1", stroke=FIELD, sw=1.5)
    f.append(box_lock)

    box_rep, _, _ = textbox(710, 320, "Гарантія абсолютної відтворюваності:\n✔ Усі вузли графа зафіксовані до найменшої залежності\n✔ Байти пакетів перевіряються за криптографічним хешем\n✔ На машині розробника, у Docker і на CI однаковий результат",
                            size=11, min_w=380, fill="#eaf0fd", stroke=NEG, sw=1.5)
    f.append(box_rep)

    f.append(arrow(710, 225, 710, 270, color=FIELD))
    f.append(text(725, 250, "детермінована синхронізація", size=10, color=FIELD, anchor="start"))

    render(os.path.join(OUT, 'reproducibility-gap.svg'), W, H, *f)


# ── Фігура 2: Транзитивний граф залежностей та розв'язання через SAT ──────────
def fig_transitive_graph():
    W, H = 920, 460
    f = []

    # Кореневий проєкт
    root_box, _, _ = textbox(460, 50, "Мій проєкт (Root)\nВимоги: A >= 1.0, B >= 1.0",
                             size=12, min_w=240, fill="#eef2f7", stroke=INK, bold=True)
    f.append(root_box)

    # Прямі залежності A та B
    box_a, _, _ = textbox(230, 170, "Пакет A (v2.1.0)\nВимагає: C >= 1.2, < 2.0",
                          size=12, min_w=220, fill=FILL, stroke=NEG)
    f.append(box_a)

    box_b, _, _ = textbox(690, 170, "Пакет B (v1.4.0)\nВимагає: C >= 1.5, < 3.0",
                          size=12, min_w=220, fill=FILL, stroke=NEG)
    f.append(box_b)

    f.append(arrow(370, 75, 270, 140, color=INK))
    f.append(arrow(550, 75, 650, 140, color=INK))

    # Перетин версій для C
    box_c, _, _ = textbox(460, 310, "Пакет C (Вибір версії)\nДіапазон A: [1.2, 2.0)\nДіапазон B: [1.5, 3.0)\nПеретин: [1.5, 2.0)\nРезолвер обирає: C == 1.8.0",
                          size=11, min_w=280, fill="#eafaf1", stroke=FIELD, sw=2, bold=False)
    f.append(box_c)

    f.append(arrow(230, 205, 360, 275, color=FIELD))
    f.append(text(275, 255, "C ∈ [1.2, 2.0)", size=10, color=FIELD))

    f.append(arrow(690, 205, 560, 275, color=FIELD))
    f.append(text(645, 255, "C ∈ [1.5, 3.0)", size=10, color=FIELD))

    # Конфліктна гілка (Backjump / Clause Learning)
    box_conflict, _, _ = textbox(460, 415, "Якщо B вимагає C >= 2.0 → Перетин порожній ∅ (Конфлікт!)\nАлгоритм PubGrub виводить несумісність (Clause) і стрибає назад (Backjump)",
                                 size=11, min_w=680, fill="#fdecea", stroke=POS, sw=1.5)
    f.append(box_conflict)

    f.append(arrow(460, 360, 460, 390, color=POS))

    render(os.path.join(OUT, 'transitive-resolution-graph.svg'), W, H, *f)


# ── Фігура 3: Універсальний крос-платформний замок (Universal Lock) ───────────
def fig_universal_lock():
    W, H = 940, 470
    f = []

    # Центральний універсальний замок
    box_univ, _, _ = textbox(470, 70, "Універсальний замок uv.lock (Єдиний файл на репозиторій)\nМістить повне дерево рішень для всіх платформ, ОС та версій Python",
                             size=13, min_w=620, fill="#fdf6e3", stroke=POS, bold=True)
    f.append(box_univ)

    # Три цільові середовища
    # Платформа 1: Linux x86_64, Python 3.12
    box_p1, _, _ = textbox(170, 230, "Середовище: Linux x86_64 · Py 3.12\nEnvironment Markers:\nsys_platform == 'linux'\npython_version == '3.12'\n\nВибрані колеса:\n• uvloop-0.19.0-cp312-manylinux_x86_64.whl\n• pydantic_core-2.18.1-cp312-manylinux.whl",
                           size=10, min_w=280, fill="#eaf0fd", stroke=NEG)
    f.append(box_p1)

    # Платформа 2: macOS ARM64 (Apple Silicon), Python 3.12
    box_p2, _, _ = textbox(470, 230, "Середовище: macOS arm64 · Py 3.12\nEnvironment Markers:\nsys_platform == 'darwin'\nplatform_machine == 'arm64'\n\nВибрані колеса:\n• uvloop-0.19.0-cp312-macosx_11_0_arm64.whl\n• pydantic_core-2.18.1-cp312-macosx_arm64.whl",
                           size=10, min_w=280, fill="#eafaf1", stroke=FIELD)
    f.append(box_p2)

    # Платформа 3: Windows x86_64, Python 3.11
    box_p3, _, _ = textbox(770, 230, "Середовище: Windows x64 · Py 3.11\nEnvironment Markers:\nsys_platform == 'win32'\npython_version == '3.11'\n\nВибрані колеса:\n• pywin32-306-cp311-win_amd64.whl\n• colorama-0.4.6-py2.py3-none-any.whl\n(uvloop не підтримується на Windows)",
                           size=10, min_w=280, fill=FILL, stroke=INK)
    f.append(box_p3)

    f.append(arrow(360, 95, 210, 160, color=NEG))
    f.append(arrow(470, 95, 470, 160, color=FIELD))
    f.append(arrow(580, 95, 730, 160, color=INK))

    # Нижній висновок: Швидкість синхронізації
    box_bot, _, _ = textbox(470, 395, "Миттєве розгортання: uv sync оцінює маркери середовища локально за O(N)\nБез повторного вирішення SAT-задачі · Без запитів до мережі PyPI · Повна ізоляція платформ",
                            size=11, min_w=780, fill="#f4f6f8", stroke=MUTED, bold=False)
    f.append(box_bot)

    f.append(arrow(170, 305, 340, 365, color=NEG))
    f.append(arrow(470, 305, 470, 365, color=FIELD))
    f.append(arrow(770, 305, 600, 365, color=INK))

    render(os.path.join(OUT, 'universal-lock-matrix.svg'), W, H, *f)


# ── Фігура 4: Детермінізм у CI/CD: uv sync vs legacy pip ──────────────────────
def fig_cicd_sync():
    W, H = 940, 440
    f = []

    # Верхній трек — Старий підхід (pip install requirements.txt)
    f.append(text(470, 35, "Традиційний підхід: pip install -r requirements.txt (Недетермінований та повільний)", size=13, bold=True, color=POS))

    box_pip1, _, _ = textbox(130, 90, "1. Читання requirements\n(Без хешів або лише\nверхній рівень)", size=10, min_w=170, fill="#fdf2f2", stroke=POS)
    f.append(box_pip1)

    box_pip2, _, _ = textbox(360, 90, "2. Звернення до PyPI\n(Пошук коліс у мережі,\nлатентність 500-2000 мс)", size=10, min_w=190, fill="#fdf2f2", stroke=POS)
    f.append(box_pip2)

    box_pip3, _, _ = textbox(600, 90, "3. Резолвінг бектрекінгом\n(Потенційний несподіваний\nдрейф підпакетів)", size=10, min_w=200, fill="#fdf2f2", stroke=POS)
    f.append(box_pip3)

    box_pip4, _, _ = textbox(830, 90, "4. Повільна інсталяція\n(Розпакування tar/whl,\nчас: 30-120 сек)", size=10, min_w=180, fill="#fdf2f2", stroke=POS)
    f.append(box_pip4)

    f.append(arrow(220, 90, 260, 90, color=POS))
    f.append(arrow(460, 90, 495, 90, color=POS))
    f.append(arrow(705, 90, 735, 90, color=POS))

    # Розділювач
    f.append(line(50, 160, 890, 160, color=LINE, sw=1, dash="4,4"))

    # Нижній трек — Сучасний підхід (uv sync --frozen)
    f.append(text(470, 200, "Сучасний підхід: uv sync --frozen (Атомарний, верифікований та миттєвий)", size=13, bold=True, color=FIELD))

    box_uv1, _, _ = textbox(130, 265, "1. Зчитування uv.lock\n(Повне дерево рішень,\nстатичний файл)", size=10, min_w=170, fill="#eafaf1", stroke=FIELD)
    f.append(box_uv1)

    box_uv2, _, _ = textbox(360, 265, "2. Валідація SHA-256\n(Перевірка цілісності коліс,\nзахист від підміни)", size=10, min_w=190, fill="#eafaf1", stroke=FIELD)
    f.append(box_uv2)

    box_uv3, _, _ = textbox(600, 265, "3. Синхронізація venv\n(Hardlink/Reflink з кешу,\nвидалення зайвого)", size=10, min_w=200, fill="#eafaf1", stroke=FIELD)
    f.append(box_uv3)

    box_uv4, _, _ = textbox(830, 265, "4. Готове середовище\n(Ідентичне до байта,\nчас: 10-50 мс!)", size=10, min_w=180, fill="#eafaf1", stroke=FIELD)
    f.append(box_uv4)

    f.append(arrow(220, 265, 260, 265, color=FIELD))
    f.append(arrow(460, 265, 495, 265, color=FIELD))
    f.append(arrow(705, 265, 735, 265, color=FIELD))

    # Нижній підсумок
    box_sum, _, _ = textbox(470, 375, "Результат для CI/CD: 0% ризику падіння через зовнішній PyPI · 100% захист Supply Chain · Економія 95% часу пайплайну",
                            size=11, min_w=820, fill="#eaf0fd", stroke=NEG)
    f.append(box_sum)

    f.append(arrow(470, 310, 470, 345, color=NEG))

    render(os.path.join(OUT, 'cicd-sync-pipeline.svg'), W, H, *f)


if __name__ == '__main__':
    fig_reproducibility_gap()
    fig_transitive_graph()
    fig_universal_lock()
    fig_cicd_sync()
    print("All figures generated successfully.")
