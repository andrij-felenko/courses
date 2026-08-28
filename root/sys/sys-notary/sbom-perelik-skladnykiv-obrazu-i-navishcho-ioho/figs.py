# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми sbom-perelik-skladnykiv-obrazu-i-navishcho-ioho.
Вимоги: pure Python, svgkit, перевірка через svgcheck.py.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра для фігур теми SBOM
BG_COMP    = "#eaf5ea"  # Зеленуватий (Компоненти, пакети)
BRD_COMP   = "#27ae60"
BG_TOOL    = "#eef2ff"  # Блакитний (Тулчейн, білд, генератори)
BRD_TOOL   = "#2563eb"
BG_META    = "#fff7ed"  # Помаранчевий (Метадані, ліцензії, хеші)
BRD_META   = "#ea580c"
BG_VEX     = "#fef2f2"  # Рожево-червоний (VEX, вразливості)
BRD_VEX    = "#dc2626"
BG_SEC     = "#f5f3ff"  # Фіолетовий (Підпис, атестація, політики)
BRD_SEC    = "#7c3aed"
BG_CARD    = "#f8fafc"  # Світло-сірий фон карток
BRD_CARD   = "#94a3b8"


def fig1_sbom_concept_graph():
    """Фігура 1: Графова модель SBOM: компоненти, метадані та зв'язки."""
    w, h = 920, 480
    parts = []

    parts.append(text(w / 2, 28, "Графова структура Software Bill of Materials (SBOM)", size=15, bold=True))

    # Ліва колонка: Джерела та артефакти
    parts.append(fitbox(40, 60, 230, 95, "Вихідний код і модулі\n• Git-коміт, дерево сирців\n• Власний прикладний код\n• Source Hash (SHA-256)", size=11, fill=BG_COMP, stroke=BRD_COMP))
    parts.append(fitbox(40, 190, 230, 95, "Сторонні залежності\n• glibc / musl, OpenSSL, curl\n• HAL мікроконтролера, RTOS\n• Пакетний URL: pkg:generic/...", size=11, fill=BG_COMP, stroke=BRD_COMP))
    parts.append(fitbox(40, 320, 230, 95, "Система збірки й тулчейн\n• GCC / Clang, CMake, BitBake\n• Прапорці оптимізації, дефайни\n• Специфікація середовища", size=11, fill=BG_TOOL, stroke=BRD_TOOL))

    # Центральний блок: SBOM Документ (DAG Граф)
    parts.append(rect(320, 50, 280, 380, fill=BG_CARD, stroke=BRD_CARD, sw=1.5, rx=8))
    parts.append(text(460, 78, "SBOM: Спрямований граф (DAG)", size=13, bold=True))
    parts.append(line(335, 92, 585, 92, color=BRD_CARD, sw=1, dash="2,2"))

    parts.append(fitbox(340, 105, 240, 55, "Корінь: Образ прошивки / rootfs\npkg:yocto/gateway-image@2.4", size=10, fill=BG_SEC, stroke=BRD_SEC))
    parts.append(fitbox(340, 195, 240, 60, "Компонент: libcrypto.so.3\n• SHA-256: 7f8a91c...\n• Ліцензія: Apache-2.0", size=10, fill=BG_META, stroke=BRD_META))
    parts.append(fitbox(340, 290, 240, 60, "Компонент: kernel-module-wifi\n• SHA-256: b341e0...\n• Ліцензія: GPL-2.0-only", size=10, fill=BG_META, stroke=BRD_META))
    parts.append(fitbox(340, 370, 240, 45, "Відношення: DEPENDS_ON, CONTAINS", size=10, fill=BG_TOOL, stroke=BRD_TOOL))

    # Права колонка: Споживачі SBOM
    parts.append(fitbox(650, 60, 230, 95, "Сканери вразливостей\n• Зіставлення CPE / PURL\n• Моніторинг CVE у базах\n• Trivy, Grype, Dependency-Track", size=11, fill=BG_VEX, stroke=BRD_VEX))
    parts.append(fitbox(650, 190, 230, 95, "Юридичний аудит ліцензій\n• Перевірка сумісності ліцензій\n• Відсікання копілефту (GPLv3)\n• Автоматична генерація Notice", size=11, fill=BG_META, stroke=BRD_META))
    parts.append(fitbox(650, 320, 230, 95, "Ланцюг довіри й криптографія\n• Підпис через cosign / in-toto\n• Відповідність CRA / EO 14028\n• Валідація цілісності перед OTA", size=11, fill=BG_SEC, stroke=BRD_SEC))

    # Стрілки зліва направо
    parts.append(arrow(270, 107, 320, 130, color=BRD_COMP, sw=1.8))
    parts.append(arrow(270, 237, 320, 225, color=BRD_COMP, sw=1.8))
    parts.append(arrow(270, 367, 320, 320, color=BRD_TOOL, sw=1.8))

    parts.append(arrow(600, 130, 650, 107, color=BRD_VEX, sw=1.8))
    parts.append(arrow(600, 225, 650, 237, color=BRD_META, sw=1.8))
    parts.append(arrow(600, 320, 650, 367, color=BRD_SEC, sw=1.8))

    render(os.path.join(OUT, "sbom-concept-graph.svg"), w, h, *parts)


def fig2_spdx_vs_cyclonedx():
    """Фігура 2: Порівняння архітектури та профілів SPDX і CycloneDX."""
    w, h = 900, 460
    parts = []

    parts.append(text(w / 2, 28, "Порівняння архітектури стандартів SPDX та CycloneDX", size=15, bold=True))

    # Лівий блок: SPDX (ISO/IEC 5962)
    parts.append(rect(40, 55, 390, 380, fill=BG_CARD, stroke=BRD_TOOL, sw=1.8, rx=8))
    parts.append(text(235, 82, "SPDX 2.3 / 3.0 (Linux Foundation / ISO)", size=13, color=BRD_TOOL, bold=True))
    parts.append(line(55, 96, 415, 96, color=BRD_TOOL, sw=1, dash="2,2"))

    parts.append(fitbox(55, 110, 360, 60, "Первинна мета:\nЮридична відповідність та аудит ліцензій (License Compliance)", size=11, fill=BG_TOOL, stroke=BRD_TOOL))
    parts.append(fitbox(55, 180, 360, 75, "Модель даних:\n• Пакети (SPDXID:SPDXRef-Package-...)\n• Окремі файли та сніпети коду (Snippets)\n• Явні типи зв'язків (DEPENDS_ON, CONTAINS)", size=10, fill=BG_META, stroke=BRD_META))
    parts.append(fitbox(55, 265, 360, 75, "SPDX 3.0 Профілі:\n• Core, Software, Licensing, Security\n• Build Profile (хеші тулчейну, вхідні файли)\n• AI / Dataset Profile (ваги, датасети)", size=10, fill=BG_SEC, stroke=BRD_SEC))
    parts.append(fitbox(55, 350, 360, 65, "Формати серіалізації:\nJSON, Tag-Value (.spdx), YAML, RDF/XML\nСтандарт ISO/IEC 5962:2021", size=10, fill=BG_CARD, stroke=BRD_CARD))

    # Правий блок: CycloneDX (OWASP)
    parts.append(rect(470, 55, 390, 380, fill=BG_CARD, stroke=BRD_COMP, sw=1.8, rx=8))
    parts.append(text(665, 82, "CycloneDX 1.5 / 1.6 (OWASP Foundation)", size=13, color=BRD_COMP, bold=True))
    parts.append(line(485, 96, 845, 96, color=BRD_COMP, sw=1, dash="2,2"))

    parts.append(fitbox(485, 110, 360, 60, "Первинна мета:\nDevSecOps, аналіз вразливостей (CVE) та ланцюг постачання", size=11, fill=BG_COMP, stroke=BRD_COMP))
    parts.append(fitbox(485, 180, 360, 75, "Модель даних:\n• Компоненти (bom-ref, type: library/framework/os)\n• Дерево залежностей (dependencies.ref)\n• Вбудовані блоки вразливостей (vulnerabilities)", size=10, fill=BG_VEX, stroke=BRD_VEX))
    parts.append(fitbox(485, 265, 360, 75, "Розширені можливості (BOM-сімейство):\n• Вбудований VEX (статуси експлуатованості)\n• HBOM (апаратний склад), CBOM (криптографія)\n• SaaS-BOM (хмарні ендпоінти, API-потоки)", size=10, fill=BG_SEC, stroke=BRD_SEC))
    parts.append(fitbox(485, 350, 360, 65, "Формати серіалізації:\nJSON (RFC 8259), XML (XSD-валідація), Protobuf\nСпецифікація OWASP Flagship Standard", size=10, fill=BG_CARD, stroke=BRD_CARD))

    render(os.path.join(OUT, "spdx-vs-cyclonedx.svg"), w, h, *parts)


def fig3_yocto_spdx_build_pipeline():
    """Фігура 3: Формування SBOM всередині системи збірки Yocto / BitBake."""
    w, h = 920, 470
    parts = []

    parts.append(text(w / 2, 28, "Генерація SBOM у процесі збірки образу (Yocto create-spdx)", size=15, bold=True))

    # 4 етапи бітбейк-пайплайну
    steps = [
        ("1. do_fetch & do_unpack", "Отримання сирців\n• Фіксація git commit / SHA-256\n• Перелік патчів (.patch)\n• Запис ліцензійних файлів", BG_TOOL, BRD_TOOL, 40),
        ("2. do_compile & do_install", "Компіляція й інсталяція\n• Прапорці CFLAGS, тулчейн\n• Формування бінарних артефактів\n• Генерація package.spdx.json", BG_COMP, BRD_COMP, 255),
        ("3. do_package & rootfs", "Складання файлової системи\n• Трасування залежностей пакунків\n• Виключення build-time утиліт\n• Створення image.spdx.json", BG_META, BRD_META, 470),
        ("4. Атестація та сканування", "Контроль та верифікація\n• Криптографічний підпис (cosign)\n• Сканування вразливостей (CVE)\n• Формування VEX-висновку", BG_SEC, BRD_SEC, 685),
    ]

    col_w = 195
    for title, desc, bg_c, brd_c, x in steps:
        parts.append(rect(x, 65, col_w, 230, fill=bg_c, stroke=brd_c, sw=1.8, rx=8))
        parts.append(text(x + col_w / 2, 92, title, size=11, color=INK, bold=True))
        parts.append(line(x + 10, 105, x + col_w - 10, 105, color=brd_c, sw=1, dash="2,2"))
        parts.append(fitbox(x + 10, 115, col_w - 20, 165, desc, size=10, fill=bg_c, stroke=bg_c))

    # Стрілки між етапами
    parts.append(arrow(235, 180, 255, 180, color=LINE, sw=2))
    parts.append(arrow(450, 180, 470, 180, color=LINE, sw=2))
    parts.append(arrow(665, 180, 685, 180, color=LINE, sw=2))

    # Нижній блок: Результуючий архів метаданих
    parts.append(rect(40, 320, 840, 120, fill=BG_CARD, stroke=BRD_CARD, sw=1.5, rx=8))
    parts.append(text(460, 345, "Фінальний артефакт збірки: image-machine.spdx.tar.zst", size=12, bold=True))
    parts.append(line(55, 358, 865, 358, color=BRD_CARD, sw=1, dash="2,2"))

    parts.append(fitbox(55, 370, 250, 55, "rootfs.spdx.json\nПовний граф зв'язків образу", size=10, fill=BG_META, stroke=BRD_META))
    parts.append(fitbox(335, 370, 250, 55, "recipes/*.spdx.json\nПоходження кожного пакета і сирців", size=10, fill=BG_COMP, stroke=BRD_COMP))
    parts.append(fitbox(615, 370, 250, 55, "license.manifest.csv\nТаблиця ліцензій для комплаєнсу", size=10, fill=BG_TOOL, stroke=BRD_TOOL))

    render(os.path.join(OUT, "yocto-spdx-build-pipeline.svg"), w, h, *parts)


def fig4_vex_triage_flow():
    """Фігура 4: Фільтрація та оцінка вразливостей через маніфести VEX."""
    w, h = 920, 460
    parts = []

    parts.append(text(w / 2, 28, "Фільтрація вразливостей через VEX (Vulnerability Exploitability eXchange)", size=15, bold=True))

    # Вхідний потік: Сканер знайшов CVE
    parts.append(fitbox(40, 70, 220, 100, "Сканер безпеки (Trivy/Grype)\n• Аналіз за PURL / CPE\n• 50+ знайдених CVE\n• Величезний інформаційний шум", size=11, fill=BG_VEX, stroke=BRD_VEX))

    # Центральний вузол: Тріаж та VEX-аналіз
    parts.append(rect(310, 60, 300, 360, fill=BG_CARD, stroke=BRD_CARD, sw=1.5, rx=8))
    parts.append(text(460, 85, "VEX: Інженерна оцінка впливу", size=12, bold=True))
    parts.append(line(325, 98, 595, 98, color=BRD_CARD, sw=1, dash="2,2"))

    parts.append(fitbox(325, 110, 270, 65, "Статус: not_affected\n• code_not_reachable (мертвий код)\n• code_not_present (вимкнено дефайном)\n• inline_mitigations_already_exist", size=10, fill=BG_COMP, stroke=BRD_COMP))
    parts.append(fitbox(325, 185, 270, 55, "Статус: affected\n• Вразливість підтверджена\n• Експлуатація можлива у цій системі", size=10, fill=BG_VEX, stroke=BRD_VEX))
    parts.append(fitbox(325, 250, 270, 50, "Статус: fixed\n• Накладено бекпорт-патч\n• Виправлено у прошивці", size=10, fill=BG_TOOL, stroke=BRD_TOOL))
    parts.append(fitbox(325, 310, 270, 50, "Статус: under_investigation\n• Триває аналіз вектору атаки", size=10, fill=BG_META, stroke=BRD_META))

    # Вихідний результат
    parts.append(fitbox(660, 100, 220, 80, "Відфільтровані шуми\n• 46 CVE позначено not_affected\n• CI/CD пайплайн не блокується", size=11, fill=BG_COMP, stroke=BRD_COMP))
    parts.append(fitbox(660, 220, 220, 80, "Реальні загрози до дії\n• 4 критичні CVE вимагають патча\n• Автоматичний таск у трекері", size=11, fill=BG_VEX, stroke=BRD_VEX))
    parts.append(fitbox(660, 335, 220, 80, "Машиночитний VEX-звіт\n• Відправка споживачам / регулятору\n• Доказ кіберстійкості виробу", size=11, fill=BG_SEC, stroke=BRD_SEC))

    # Стрілки
    parts.append(arrow(260, 120, 310, 135, color=BRD_VEX, sw=1.8))
    parts.append(arrow(610, 142, 660, 140, color=BRD_COMP, sw=1.8))
    parts.append(arrow(610, 212, 660, 260, color=BRD_VEX, sw=1.8))
    parts.append(arrow(610, 335, 660, 375, color=BRD_SEC, sw=1.8))

    render(os.path.join(OUT, "vex-triage-flow.svg"), w, h, *parts)


if __name__ == "__main__":
    fig1_sbom_concept_graph()
    fig2_spdx_vs_cyclonedx()
    fig3_yocto_spdx_build_pipeline()
    fig4_vex_triage_flow()
    print("All figures successfully generated in", OUT)
