#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор діаграм для теми: Нормативні вимоги до безпеки коду (CRA, RED 3.3, EN 303 645)."""

import os
import sys

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від кореня теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_regulatory_landscape():
    """Співвідношення нормативних актів: RED 3.3, ETSI EN 303 645 та Cyber Resilience Act (CRA)."""
    w, h = 940, 440
    frags = []
    
    # 1. ETSI EN 303 645 (Технічний стандарт)
    b1_x, b1_y, b1_w, b1_h = 30, 60, 270, 350
    frags.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#f8fafc", stroke=NEG, sw=2, rx=8))
    frags.append(text(b1_x + b1_w / 2, b1_y + 28, "ETSI EN 303 645", size=15, color=NEG, bold=True))
    frags.append(text(b1_x + b1_w / 2, b1_y + 48, "Галузевий технічний стандарт", size=11, color=MUTED, italic=True))
    frags.append(line(b1_x + 15, b1_y + 60, b1_x + b1_w - 15, b1_y + 60, color=NEG, sw=1))
    
    items1 = [
        "Об'єкт: Споживчий IoT (Consumer IoT)",
        "13 базових вимог кібербезпеки:",
        " • Заборона дефолтних паролів (5.1)",
        " • Політика вразливостей CVD (5.2)",
        " • Криптографічні оновлення (5.3)",
        " • Безпечне зберігання секретів (5.4)",
        " • Захист інтерфейсів зв'язку (5.5)",
        " • Контроль поверхні атак і телеметрії",
        "Статус: Гармонізована основа для RED"
    ]
    for i, itm in enumerate(items1):
        bold = (i in [0, 1, 8])
        col = INK if not bold else (NEG if i == 8 else INK)
        frags.append(text(b1_x + 14, b1_y + 88 + i * 28, itm, size=11.5, anchor="start", bold=bold, color=col))

    # 2. RED Article 3.3 (Директива 2014/53/EU)
    b2_x, b2_y, b2_w, b2_h = 335, 60, 275, 350
    frags.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#fdfbf7", stroke="#d97706", sw=2, rx=8))
    frags.append(text(b2_x + b2_w / 2, b2_y + 28, "RED Art. 3.3 (d / e / f)", size=15, color="#b45309", bold=True))
    frags.append(text(b2_x + b2_w / 2, b2_y + 48, "Делегований регламент (EU) 2022/30", size=11, color=MUTED, italic=True))
    frags.append(line(b2_x + 15, b2_y + 60, b2_x + b2_w - 15, b2_y + 60, color="#d97706", sw=1))
    
    items2 = [
        "Об'єкт: Бездротові пристрої (Wi-Fi/BLE/Cellular)",
        "Три обов'язкові юридичні статті:",
        " • 3.3(d) Захист мереж від перевантажень",
        " • 3.3(e) Захист персональних даних/приватності",
        " • 3.3(f) Захист фінансових транзакцій",
        "Стандарти: EN 18031-1, EN 18031-2, EN 18031-3",
        "Обов'язковість: З серпня 2025 року",
        "Наслідок: Заборона продажу без CE-RED"
    ]
    for i, itm in enumerate(items2):
        bold = (i in [0, 1, 7])
        col = INK if not bold else ("#b45309" if i == 7 else INK)
        frags.append(text(b2_x + 14, b2_y + 88 + i * 28, itm, size=11.5, anchor="start", bold=bold, color=col))

    # 3. CRA (Cyber Resilience Act)
    b3_x, b3_y, b3_w, b3_h = 645, 60, 270, 350
    frags.append(rect(b3_x, b3_y, b3_w, b3_h, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    frags.append(text(b3_x + b3_w / 2, b3_y + 28, "Cyber Resilience Act (CRA)", size=15, color=FIELD, bold=True))
    frags.append(text(b3_x + b3_w / 2, b3_y + 48, "Регламент (EU) 2024/2847", size=11, color=MUTED, italic=True))
    frags.append(line(b3_x + 15, b3_y + 60, b3_x + b3_w - 15, b3_y + 60, color=FIELD, sw=1))
    
    items3 = [
        "Об'єкт: УСІ цифрові продукти (ПЗ + залізо)",
        "Повний життєвий цикл виробу:",
        " • Security by Design / Security by Default",
        " • Обов'язковий маніфест SBOM (SPDX/CycloneDX)",
        " • Сповіщення ENISA/CSIRT про 0-day за 24 год",
        " • Обов'язкові патчі безпеки (до 5+ років)",
        "Класи: Звичайні / Важливі I-II / Критичні",
        "Штрафи: До 15 млн € або 2.5% річного обороту"
    ]
    for i, itm in enumerate(items3):
        bold = (i in [0, 1, 7])
        col = INK if not bold else (POS if i == 7 else INK)
        frags.append(text(b3_x + 14, b3_y + 88 + i * 28, itm, size=11.5, anchor="start", bold=bold, color=col))

    path = os.path.join(OUT_DIR, "regulatory-landscape.svg")
    render(path, w, h, *frags, title="Нормативний простір безпеки коду та вбудованих систем у ЄС")
    print(f"Згенеровано: {path}")


def fig_secure_firmware_pipeline():
    """Архітектура оновлення прошивки за вимогами CRA та EN 303 645."""
    w, h = 950, 380
    frags = []
    
    # 4 етапи ланцюга
    # 1. CI/CD & Build
    s1_x, s1_y, s1_w, s1_h = 25, 60, 205, 290
    frags.append(rect(s1_x, s1_y, s1_w, s1_h, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(s1_x + s1_w / 2, s1_y + 24, "1. Збирання та аудит", size=13, bold=True))
    frags.append(line(s1_x + 10, s1_y + 36, s1_x + s1_w - 10, s1_y + 36, color=LINE, sw=1))
    lines1 = [
        "Компіляція образу",
        "Генерація SBOM",
        "  (SPDX / CycloneDX)",
        "SAST / DAST перевірка",
        "CVE сканування коду",
        "Security Version (SVN)"
    ]
    for i, l in enumerate(lines1):
        frags.append(text(s1_x + 12, s1_y + 68 + i * 34, l, size=11, anchor="start", color=INK))
        
    # Стрілка 1 -> 2
    frags.append(arrow(s1_x + s1_w + 4, s1_y + 145, s1_x + s1_w + 24, s1_y + 145, color=LINE, sw=2))

    # 2. Asymmetric Signing
    s2_x, s2_y, s2_w, s2_h = 258, 60, 205, 290
    frags.append(rect(s2_x, s2_y, s2_w, s2_h, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(s2_x + s2_w / 2, s2_y + 24, "2. Криптографічний підпис", size=13, color=POS, bold=True))
    frags.append(line(s2_x + 10, s2_y + 36, s2_x + s2_w - 10, s2_y + 36, color=POS, sw=1))
    lines2 = [
        "HSM / KMS середовище",
        "Таємний ключ (Private Key)",
        "Алгоритм: Ed25519 /",
        "  RSA-3072 / ECDSA P-256",
        "Підпис заголовка образу",
        "Фіксація метаданих версії"
    ]
    for i, l in enumerate(lines2):
        frags.append(text(s2_x + 12, s2_y + 68 + i * 34, l, size=11, anchor="start", color=INK))

    # Стрілка 2 -> 3
    frags.append(arrow(s2_x + s2_w + 4, s2_y + 145, s2_x + s2_w + 24, s2_y + 145, color=LINE, sw=2))

    # 3. On-Device Verification
    s3_x, s3_y, s3_w, s3_h = 491, 60, 210, 290
    frags.append(rect(s3_x, s3_y, s3_w, s3_h, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(s3_x + s3_w / 2, s3_y + 24, "3. Верифікація в чипі", size=13, color=NEG, bold=True))
    frags.append(line(s3_x + 10, s3_y + 36, s3_x + s3_w - 10, s3_y + 36, color=NEG, sw=1))
    lines3 = [
        "Відкритий ключ у eFuse / OTP",
        "Обчислення SHA-256 хешу",
        "Перевірка цифрового підпису",
        "Anti-Rollback контроль:",
        "  нова версія ≥ поточної",
        "Захист від пониження версії"
    ]
    for i, l in enumerate(lines3):
        frags.append(text(s3_x + 12, s3_y + 68 + i * 34, l, size=11, anchor="start", color=INK))

    # Стрілка 3 -> 4
    frags.append(arrow(s3_x + s3_w + 4, s3_y + 145, s3_x + s3_w + 24, s3_y + 145, color=LINE, sw=2))

    # 4. Atomic Execution
    s4_x, s4_y, s4_w, s4_h = 729, 60, 200, 290
    frags.append(rect(s4_x, s4_y, s4_w, s4_h, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(s4_x + s4_w / 2, s4_y + 24, "4. Атомарний запуск", size=13, color=FIELD, bold=True))
    frags.append(line(s4_x + 10, s4_y + 36, s4_x + s4_w - 10, s4_y + 36, color=FIELD, sw=1))
    lines4 = [
        "Dual-Bank (A/B Flash)",
        "Запис у неактивний слот",
        "Атомарна зміна вказівника",
        "Пробний запуск (Trial Run)",
        "Watchdog самодіагностика",
        "Автоматичний відкат (Rollback)"
    ]
    for i, l in enumerate(lines4):
        frags.append(text(s4_x + 12, s4_y + 68 + i * 34, l, size=11, anchor="start", color=INK))

    path = os.path.join(OUT_DIR, "secure-firmware-pipeline.svg")
    render(path, w, h, *frags, title="Ланцюг захищеного оновлення прошивки (EN 303 645 Cl. 5.3 та CRA Annex I)")
    print(f"Згенеровано: {path}")


def fig_cra_conformity_classes():
    """Класифікація цифрових продуктів за CRA та процедури оцінки відповідності."""
    w, h = 940, 400
    frags = []
    
    # 3 колонки класів
    # Колонка 1: Звичайні продукти (Default)
    c1_x, c1_y, c1_w, c1_h = 30, 60, 275, 315
    frags.append(rect(c1_x, c1_y, c1_w, c1_h, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(c1_x + c1_w / 2, c1_y + 24, "Звичайні цифрові продукти", size=13.5, bold=True))
    frags.append(text(c1_x + c1_w / 2, c1_y + 42, "Близько 90% ринку (Default)", size=11, color=MUTED, italic=True))
    frags.append(line(c1_x + 10, c1_y + 52, c1_x + c1_w - 10, c1_y + 52, color=LINE, sw=1))
    
    lines_c1 = [
        "Приклади виробів:",
        " • Розумні побутові прилади",
        " • Фотокамери, аудіосистеми",
        " • Комп'ютерні ігри та утиліти",
        " • Текстові/графічні редактори",
        "Оцінка відповідності:",
        " • Модуль A (Самодекларація)",
        " • Внутрішній контроль виробництва",
        " • Без нотифікованого органу"
    ]
    for i, l in enumerate(lines_c1):
        bold = (i in [0, 5])
        col = FIELD if i >= 6 else (INK if not bold else INK)
        frags.append(text(c1_x + 12, c1_y + 78 + i * 25, l, size=11, anchor="start", bold=bold, color=col))

    # Колонка 2: Важливі продукти Клас I
    c2_x, c2_y, c2_w, c2_h = 332, 60, 275, 315
    frags.append(rect(c2_x, c2_y, c2_w, c2_h, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=6))
    frags.append(text(c2_x + c2_w / 2, c2_y + 24, "Важливі продукти Класу I", size=13.5, color="#854d0e", bold=True))
    frags.append(text(c2_x + c2_w / 2, c2_y + 42, "CRA Annex III — Class I", size=11, color=MUTED, italic=True))
    frags.append(line(c2_x + 10, c2_y + 52, c2_x + c2_w - 10, c2_y + 52, color="#ca8a04", sw=1))
    
    lines_c2 = [
        "Приклади виробів:",
        " • Менеджери паролів",
        " • Мережеві маршрутизатори",
        " • Антивірусне ПЗ, VPN-клієнти",
        " • Мікроконтролери з пам'яттю",
        "Оцінка відповідності:",
        " • Гармонізований стандарт → Модуль A",
        " • АБО Нотифікований орган (Module B+C)",
        " • АБО Повна якість (Module H)"
    ]
    for i, l in enumerate(lines_c2):
        bold = (i in [0, 5])
        col = "#854d0e" if i >= 6 else (INK if not bold else INK)
        frags.append(text(c2_x + 12, c2_y + 78 + i * 25, l, size=11, anchor="start", bold=bold, color=col))

    # Колонка 3: Важливі Клас II та Критичні
    c3_x, c3_y, c3_w, c3_h = 634, 60, 275, 315
    frags.append(rect(c3_x, c3_y, c3_w, c3_h, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(c3_x + c3_w / 2, c3_y + 24, "Важливі II та Критичні", size=13.5, color=POS, bold=True))
    frags.append(text(c3_x + c3_w / 2, c3_y + 42, "CRA Annex III (Cl. II) та Annex IV", size=11, color=MUTED, italic=True))
    frags.append(line(c3_x + 10, c3_y + 52, c3_x + c3_w - 10, c3_y + 52, color=POS, sw=1))
    
    lines_c3 = [
        "Приклади виробів:",
        " • Гіпервізори, ядра ОС, BIOS",
        " • Апаратні Secure Elements / TPM",
        " • Промислові міжмережеві екрани",
        " • Смарт-лічильники та робототехніка",
        "Оцінка відповідності:",
        " • ОБОВ'ЯЗКОВО Нотифікований орган",
        " • Експертиза типу ЄС (Module B+C)",
        " • АБО Сертифікація EUCC"
    ]
    for i, l in enumerate(lines_c3):
        bold = (i in [0, 5])
        col = POS if i >= 6 else (INK if not bold else INK)
        frags.append(text(c3_x + 12, c3_y + 78 + i * 25, l, size=11, anchor="start", bold=bold, color=col))

    path = os.path.join(OUT_DIR, "cra-conformity-classes.svg")
    render(path, w, h, *frags, title="Класи продуктів CRA та процедури оцінки відповідності (CE Marking)")
    print(f"Згенеровано: {path}")


def main():
    fig_regulatory_landscape()
    fig_secure_firmware_pipeline()
    fig_cra_conformity_classes()


if __name__ == "__main__":
    main()
