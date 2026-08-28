# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми ne-tilky-kod.
Вимоги: pure Python, svgkit, перевірка через svgcheck.py.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори для категорій активів
BG_CODE    = "#f0fdf4"  # Світло-зелений (відкритий код)
BRD_CODE   = "#16a34a"
BG_BLOB    = "#fff1f2"  # Світло-червоний (пропрієтарні блоби)
BRD_BLOB   = "#e11d48"
BG_FONT    = "#eff6ff"  # Світло-синій (шрифти)
BRD_FONT   = "#2563eb"
BG_ML      = "#faf5ff"  # Світло-фіолетовий (ваги нейромереж)
BRD_ML     = "#9333ea"
BG_CALIB   = "#fffbeb"  # Світло-жовтий (калібрування та NVM)
BRD_CALIB  = "#d97706"


def fig1_firmware_binary_anatomy():
    """Фігура 1: Анатомія прошивки — поділ на скомпільований код та не-кодові цифрові активи."""
    w, h = 960, 520
    parts = []

    parts.append(text(w / 2, 28, "Анатомія бінарного образу прошивки: кодові та не-кодові цифрові активи", size=15, bold=True))

    # Лівий блок: фізичний образ Flash-пам'яті (Flash ROM Layout)
    parts.append(rect(40, 60, 260, 430, fill="#f8fafc", stroke="#64748b", sw=2, rx=8))
    parts.append(text(170, 85, "Образ Flash-пам'яті (ROM)", size=13, color=INK, bold=True))
    parts.append(text(170, 103, "0x08000000 – 0x08400000 (4 МБ)", size=10, color=MUTED))

    # Секції у флеші
    s1 = fitbox(55, 120, 230, 60, "Код застосунку (C/C++)\n• Вектори переривань, main()\n• Відкриті бібліотеки (MIT/BSD)", size=10, fill=BG_CODE, stroke=BRD_CODE)
    s2 = fitbox(55, 190, 230, 65, "Вендорські блоби (HAL / PHY)\n• libwifi_phy.a, BLE контролер\n• Закритий DSP мікрокод", size=10, fill=BG_BLOB, stroke=BRD_BLOB)
    s3 = fitbox(55, 265, 230, 65, "Шрифтові ресурси GUI\n• Байткод TTF / OTF таблиці\n• Растровий C-масив гліфів (BDF)", size=10, fill=BG_FONT, stroke=BRD_FONT)
    s4 = fitbox(55, 340, 230, 65, "Ваги нейромережі (Edge AI)\n• INT8 тензори TFLite Micro\n• Фільтри CNN та зміщення (bias)", size=10, fill=BG_ML, stroke=BRD_ML)
    s5 = fitbox(55, 415, 230, 60, "Калібрувальні таблиці й NVM\n• RF LUT таблиці, підписи, сертифікати\n• Таблиці поправок сенсорів", size=10, fill=BG_CALIB, stroke=BRD_CALIB)
    parts.extend([s1, s2, s3, s4, s5])

    # Права частина: 4 детальні картки правового режиму активів
    # Картка 1: Вендорські блоби
    c1 = fitbox(330, 60, 590, 98,
                "1. Вендорські блоби (HAL, DSP, Radio PHY)\n"
                "• Юридична природа: пропрієтарний об'єктний код, clickwrap EULA, комерційні NDA.\n"
                "• Головні ризики: пряма заборона поширення третім особам, порушення GPL при статичному лінкуванні,\n"
                "  прив'язка ліцензії лише до конкретного SKU чипа (Evaluation-only застереження).",
                size=11, fill=BG_BLOB, stroke=BRD_BLOB)

    # Картка 2: Шрифти та гліфи
    c2 = fitbox(330, 170, 590, 98,
                "2. Шрифти та типографіка (Font Software vs Glyphs)\n"
                "• Юридична природа: файл .ttf/.otf є комп'ютерною програмою з байткодом хінтингу (Font Software).\n"
                "• Головні ризики: десктопна ліцензія забороняє вшивання у ROM пристрою (ROM Embedding License);\n"
                "  SIL OFL вимагає дотримання Reserved Font Name (RFN) та забороняє продаж шрифту окремо.",
                size=11, fill=BG_FONT, stroke=BRD_FONT)

    # Картка 3: Ваги нейромереж
    c3 = fitbox(330, 280, 590, 98,
                "3. Ваги нейромереж та параметри моделей (Model Weights & Tensors)\n"
                "• Юридична природа: масиви коефіцієнтів оптимізації; режим захисту даних та умов ліцензії ваг.\n"
                "• Головні ризики: юридична токсичність датасету (CC BY-NC забороняє комерційний edge-випуск);\n"
                "  поведінкові обмеження ліцензій OpenRAIL/RAIL (заборона військового або біометричного вжитку).",
                size=11, fill=BG_ML, stroke=BRD_ML)

    # Картка 4: Складений SBOM
    c4 = fitbox(330, 390, 590, 100,
                "4. Складений не-кодовий SBOM (Multi-Layer Asset Compliance)\n"
                "• Проблема: традиційні менеджери пакунків (cargo, vcpkg) бачать лише сирцевий код C/C++.\n"
                "• Рішення: повна інвентаризація бінарних ресурсів через SPDX 3.0 (AIModel/Dataset) та CycloneDX 1.6\n"
                "  з фіксацією SHA-256 хешів, походження датасетів, EULA-договорів та прав на вшивання.",
                size=11, fill="#f8fafc", stroke="#64748b")

    parts.extend([c1, c2, c3, c4])

    # Зв'язувальні стрілки від секцій ROM до карток
    parts.append(arrow(285, 222, 330, 110, color=BRD_BLOB, sw=1.5))
    parts.append(arrow(285, 297, 330, 215, color=BRD_FONT, sw=1.5))
    parts.append(arrow(285, 372, 330, 325, color=BRD_ML, sw=1.5))

    render(os.path.join(OUT, "firmware-binary-anatomy.svg"), w, h, *parts)


def fig2_font_licensing_matrix():
    """Фігура 2: Життєвий цикл шрифту в прошивці та правові режими вшивання."""
    w, h = 940, 480
    parts = []

    parts.append(text(w / 2, 28, "Шрифтові ресурси у вбудованих системах: шляхи інтеграції та ліцензійні пастки", size=15, bold=True))

    # Стовпець 1: Джерело шрифту
    s1 = fitbox(40, 70, 200, 160,
                "Векторний шрифт\n(TTF / OTF)\n\n"
                "• Байткод TrueType\n"
                "• Криві Безьє, кернінг\n"
                "• Юридично: програма\n"
                "  (Font Software)",
                size=11, fill=BG_FONT, stroke=BRD_FONT)

    # Стовпець 2: Перетворення / Інтеграція
    s2_a = fitbox(280, 70, 220, 100,
                  "Варіант А: FreeType у ROM\n\n"
                  "• Пряме читання .ttf з Flash\n"
                  "• Рендеринг кривих у растр\n"
                  "➔ Вшивання Font Software",
                  size=11, fill="#fff7ed", stroke="#ea580c")

    s2_b = fitbox(280, 190, 220, 100,
                  "Варіант Б: Конвертер у C-масив\n\n"
                  "• lv_font_conv, bdf2c\n"
                  "• Фіксований растр (14px, 18px)\n"
                  "➔ Похідний твір чи растр?",
                  size=11, fill="#fff7ed", stroke="#ea580c")

    # Стовпець 3: Кінцевий пристрій
    s3 = fitbox(540, 110, 170, 140,
                "Вбудований GUI\nдисплей пристрою\n\n"
                "• Flash ROM мікроконтролера\n"
                "• Масове тиражування\n"
                "• Продаж споживачам",
                size=11, fill="#f8fafc", stroke="#64748b")

    parts.extend([s1, s2_a, s2_b, s3])

    # Стрілки конвеєра
    parts.append(arrow(240, 120, 280, 120, color=LINE, sw=1.8))
    parts.append(arrow(240, 180, 280, 240, color=LINE, sw=1.8))
    parts.append(arrow(500, 120, 540, 160, color=LINE, sw=1.8))
    parts.append(arrow(500, 240, 540, 190, color=LINE, sw=1.8))

    # Праворуч: Юридичні наслідки (3 типи ліцензій)
    parts.append(rect(740, 60, 160, 230, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    parts.append(text(820, 82, "Типи ліцензій", size=12, color=INK, bold=True))

    l1 = fitbox(748, 98, 144, 52, "SIL OFL 1.1\n• Дозволяє вшивання\n• RFN вимога", size=9.5, fill=BG_CODE, stroke=BRD_CODE)
    l2 = fitbox(748, 158, 144, 58, "Десктопна EULA\n• ЗАБОРОНЯЄ ROM\n• Ризик позову", size=9.5, fill=BG_BLOB, stroke=BRD_BLOB)
    l3 = fitbox(748, 224, 144, 58, "OEM Hardware\n• Дорога ліцензія\n• Роялті за одиницю", size=9.5, fill="#fffbeb", stroke="#d97706")
    parts.extend([l1, l2, l3])

    # Нижня частина: Порівняльна таблиця юридичних зон
    parts.append(rect(40, 310, 860, 150, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(470, 332, "Ключові юридичні правила роботи зі шрифтами у прошивках", size=13, color=INK, bold=True))

    t1 = fitbox(60, 348, 260, 95,
                "1. Статус Font Software\n"
                "Векторний шрифт — це виконуваний код.\n"
                "Звичайна ліцензія (Desktop/Web)\n"
                "не дає права вшивати бінарник у ROM.",
                size=10.5, fill=BG_FONT, stroke=BRD_FONT)

    t2 = fitbox(340, 348, 260, 95,
                "2. Reserved Font Name (RFN)\n"
                "При зміні гліфів під SIL OFL заборонено\n"
                "використовувати оригінальну назву\n"
                "шрифту у назві продукту та меню.",
                size=10.5, fill=BG_CODE, stroke=BRD_CODE)

    t3 = fitbox(620, 348, 260, 95,
                "3. Растеризація та похідний твір\n"
                "Конвертація TTF у растровий C-масив\n"
                "часто трактується правовласниками як\n"
                "похідний твір (Derivative Work).",
                size=10.5, fill="#fef2f2", stroke="#ef4444")
    parts.extend([t1, t2, t3])

    render(os.path.join(OUT, "font-licensing-matrix.svg"), w, h, *parts)


def fig3_ml_model_ip_provenance():
    """Фігура 3: Тріада інтелектуальної власності в Edge AI — датасет, архітектура, ваги, рантайм."""
    w, h = 940, 480
    parts = []

    parts.append(text(w / 2, 28, "Ланцюг походження прав (IP Provenance) у машинному навчанні для мікроконтролерів", size=15, bold=True))

    # Блок 1: Навчальний датасет
    b1 = fitbox(40, 70, 200, 150,
                "1. Навчальний датасет\n(Training Dataset)\n\n"
                "• Зображення, аудіо, спектри\n"
                "• Ліцензії: CC0, CC BY, CC BY-NC\n"
                "➔ NC ліцензія блокує\n"
                "   комерційне використання!",
                size=11, fill="#fff1f2", stroke="#e11d48")

    # Блок 2: Архітектура та код навчання
    b2 = fitbox(270, 70, 190, 150,
                "2. Код моделі\n(Model Source)\n\n"
                "• PyTorch / Keras скрипти\n"
                "• Описи шарів CNN, RNN\n"
                "• Ліцензії: MIT, Apache 2.0,\n"
                "  GPLv3 (копілефт на скрипт)",
                size=11, fill=BG_CODE, stroke=BRD_CODE)

    # Блок 3: Збережені ваги та квантування
    b3 = fitbox(490, 70, 200, 150,
                "3. Тензори та ваги\n(Model Weights .tflite)\n\n"
                "• INT8 коефіцієнти, зміщення\n"
                "• OpenRAIL / Custom EULA\n"
                "➔ Юридична токсичність\n"
                "   передається від датасету",
                size=11, fill=BG_ML, stroke=BRD_ML)

    # Блок 4: Виконуваний рантайм
    b4 = fitbox(720, 70, 180, 150,
                "4. Рантайм інференсу\n(Inference Engine)\n\n"
                "• TFLite Micro / ONNX RT\n"
                "• C/C++ бібліотека у ROM\n"
                "• Ліцензія: Apache 2.0\n"
                "  (чистий дозвільний код)",
                size=11, fill=BG_CODE, stroke=BRD_CODE)

    parts.extend([b1, b2, b3, b4])

    # Стрілки походження
    parts.append(arrow(240, 145, 270, 145, color=LINE, sw=2))
    parts.append(arrow(460, 145, 490, 145, color=LINE, sw=2))
    parts.append(arrow(690, 145, 720, 145, color=LINE, sw=2))

    # Підписи під стрілками
    parts.append(text(255, 130, "Навчання", size=9, color=MUTED))
    parts.append(text(475, 130, "Експорт", size=9, color=MUTED))
    parts.append(text(705, 130, "Вшивання", size=9, color=MUTED))

    # Нижній блок: Юридичні пастки поєднання активів
    parts.append(rect(40, 250, 860, 200, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(470, 275, "Юридичні ризики та пастки походження ваг нейромереж", size=13, color=INK, bold=True))

    p1 = fitbox(60, 295, 260, 135,
                "Пастка CC BY-NC датасетів\n\n"
                "Якщо базова модель тренувалася\n"
                "на академічному датасеті (Non-Commercial),\n"
                "комерційний реліз пристрою з цими вагами\n"
                "є прямим порушенням авторських прав.",
                size=10.5, fill="#fef2f2", stroke="#ef4444")

    p2 = fitbox(340, 295, 260, 135,
                "Поведінкові ліцензії (OpenRAIL)\n\n"
                "Сучасні ваги часто ліцензуються під OpenRAIL.\n"
                "Вони прямо забороняють використання моделі\n"
                "у військовій сфері, системах стеження\n"
                "чи критичній медичній діагностиці.",
                size=10.5, fill=BG_ML, stroke=BRD_ML)

    p3 = fitbox(620, 295, 260, 135,
                "Патентні гарантії та чистота\n\n"
                "Архітектура моделі може бути під Apache 2.0,\n"
                "але самі ваги не мають патентного захисту.\n"
                "Захист від патентних претензій на алгоритми\n"
                "потребує окремого патентного клірингу.",
                size=10.5, fill="#fffbeb", stroke="#d97706")

    parts.extend([p1, p2, p3])

    render(os.path.join(OUT, "ml-model-ip-provenance.svg"), w, h, *parts)


def fig4_non_code_sbom_pipeline():
    """Фігура 4: Автоматизований аудит не-кодових активів та генерація SBOM у CI/CD."""
    w, h = 940, 460
    parts = []

    parts.append(text(w / 2, 28, "Автоматизований конвеєр аудиту не-кодових артефактів та генерації SBOM", size=15, bold=True))

    # 4 кроки аудиту
    s1 = fitbox(40, 70, 190, 120,
                "1. Бінарний образ\n(Firmware Inputs)\n\n"
                "• target.elf, flash.bin\n"
                "• Секції .rodata, .data\n"
                "• Бінарні блоби .a / .fw\n"
                "• Вшиті C-масиви ваг і шрифтів",
                size=10.5, fill=FILL, stroke=LINE)

    s2 = fitbox(260, 70, 190, 120,
                "2. Сканер сигнатур\n(Asset Extractor)\n\n"
                "• Аналіз ентропії (блоби)\n"
                "• Пошук магічних чисел TTF/TFLite\n"
                "• Парсер секцій objdump/readelf\n"
                "• Витяг SHA-256 та розмірів",
                size=10.5, fill=BG_FONT, stroke=BRD_FONT)

    s3 = fitbox(480, 70, 200, 120,
                "3. Верифікатор ліцензій\n(Policy Compliance)\n\n"
                "• Звірка з базою ліцензій EULA\n"
                "• Перевірка прав вшивання шрифтів\n"
                "• Контроль походження ML-датасетів\n"
                "• Детекція заборонених NC/GPL лінків",
                size=10.5, fill=BG_ML, stroke=BRD_ML)

    s4 = fitbox(710, 70, 190, 120,
                "4. Вихідні SBOM-артефакти\n(Compliance Deliverables)\n\n"
                "• CycloneDX 1.6 (ML + Font)\n"
                "• SPDX 3.0 AI Model Package\n"
                "• Реєстр ліцензій для нотаріуса\n"
                "• Пакунок для аудиту OEM",
                size=10.5, fill=BG_CODE, stroke=BRD_CODE)

    parts.extend([s1, s2, s3, s4])

    # Стрілки
    parts.append(arrow(230, 130, 260, 130, color=LINE, sw=2))
    parts.append(arrow(450, 130, 480, 130, color=LINE, sw=2))
    parts.append(arrow(680, 130, 710, 130, color=LINE, sw=2))

    # Нижній блок: Шлюзи якості (CI/CD Quality Gate)
    parts.append(rect(40, 225, 860, 205, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(470, 250, "Критерії шлюзу валідації не-кодових активів (CI/CD Release Gate)", size=13, color=INK, bold=True))

    gate_fail = fitbox(60, 270, 390, 140,
                       "✖ БЛОКУВАННЯ РЕЛІЗУ (Gate FAILED):\n\n"
                       "• Виявлено вшитий комерційний TTF-шрифт без OEM ROM ліцензії\n"
                       "• Ваги нейромережі мають походження від CC BY-NC датасету\n"
                       "• Вендорський HAL-блоб не має дозволу на субліцензування\n"
                       "• Виявлено статичне компонування GPL-коду з закритим блобом",
                       size=10.5, fill="#fef2f2", stroke=POS)

    gate_pass = fitbox(480, 270, 400, 140,
                       "✔ ДОЗВІЛ НА РЕЛІЗ (Gate PASSED):\n\n"
                       "• Усі шрифти мають верифіковану ліцензію SIL OFL (із врахуванням RFN)\n"
                       "• Ваги ML навчені на дозволених комерційних датасетах (Apache/CC-BY)\n"
                       "• Для вендорських блобів підтверджено дистрибуційні права виробника\n"
                       "• Сформовано повний CycloneDX 1.6 SBOM із метаданими моделей",
                       size=10.5, fill="#f0fdf4", stroke=FIELD)

    parts.extend([gate_fail, gate_pass])

    render(os.path.join(OUT, "non-code-sbom-pipeline.svg"), w, h, *parts)


if __name__ == "__main__":
    fig1_firmware_binary_anatomy()
    fig2_font_licensing_matrix()
    fig3_ml_model_ip_provenance()
    fig4_non_code_sbom_pipeline()
    print("Всі 4 фігури успішно згенеровано.")
