# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори
AMBER   = "#caa24a"
AMBERBG = "#fff6e0"
AMBERTX = "#8a6d1a"
GREENBG = "#eef6ef"
BLUEBG  = "#e9eefb"
REDBG   = "#fbecec"
PURPLE  = "#8e44ad"
PURPLETX= "#6c3483"
PURPLEBG= "#f4ecf7"
CARD_BG = "#fcfdfe"


# ── Фігура 1: Анатомія релізу як неподільного об'єкта ────────────────────────
def fig_release_anatomy():
    W, H = 860, 460
    p = []
    
    # Заголовок
    p.append(text(W / 2, 28, "Реліз як криптографічно зв'язаний об'єкт (Release Capsule)", size=15, color=INK, bold=True))
    
    # Зовнішня капсула
    p.append(rect(20, 46, 820, 396, fill=FILL, stroke=LINE, sw=2, rx=12))
    p.append(text(40, 72, "ПАКУНОК РЕЛІЗУ (Одиниця постачання та розгортання)", size=12, color=MUTED, anchor="start", bold=True))
    
    # Чотири стовпи
    # 1. Образ
    p.append(rect(40, 90, 180, 330, fill=BLUEBG, stroke=NEG, sw=1.8, rx=8))
    p.append(text(130, 118, "1. ОБРАЗ (Payload)", size=12.5, color=NEG, bold=True))
    p.append(text(130, 140, "Бінарні артефакти", size=10, color=MUTED))
    
    payload_items = [
        "• .bin / .hex образ",
        "• Таблиця векторів",
        "• Секція .text (код)",
        "• Секція .rodata (конст.)",
        "• Секція .data (ініц.)",
        "• Образ ФС (LittleFS)",
        "• Патчі NVM / конфіг"
    ]
    for i, item in enumerate(payload_items):
        p.append(text(55, 175 + i * 22, item, size=9.5, color=INK, anchor="start"))
        
    p.append(rect(52, 345, 156, 60, fill="#ffffff", stroke=NEG, sw=1, rx=4))
    p.append(text(130, 366, "Невиконуваний без", size=9, color=NEG, bold=True))
    p.append(text(130, 384, "маніфесту й адрес", size=9, color=NEG))

    # 2. Маніфест
    p.append(rect(235, 90, 190, 330, fill=GREENBG, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(330, 118, "2. МАНІФЕСТ", size=12.5, color=FIELD, bold=True))
    p.append(text(330, 140, "Паспорт і правила", size=10, color=MUTED))
    
    manifest_items = [
        "• Версія SemVer (1.4.0)",
        "• HW ID (сумісність)",
        "• Діапазон ревізій PCB",
        "• Адреса flash / entry",
        "• Розмір у байтах",
        "• SHA-256 геш образу",
        "• Anti-rollback індекс"
    ]
    for i, item in enumerate(manifest_items):
        p.append(text(250, 175 + i * 22, item, size=9.5, color=INK, anchor="start"))
        
    p.append(rect(247, 345, 166, 60, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    p.append(text(330, 366, "Зв'язує залізо,", size=9, color=FIELD, bold=True))
    p.append(text(330, 384, "версію та пам'ять", size=9, color=FIELD))

    # 3. Підпис
    p.append(rect(440, 90, 185, 330, fill=PURPLEBG, stroke=PURPLE, sw=1.8, rx=8))
    p.append(text(532, 118, "3. ПІДПИС & ДОВІРА", size=12.5, color=PURPLETX, bold=True))
    p.append(text(532, 140, "Криптографічний захист", size=10, color=MUTED))
    
    sig_items = [
        "• Асиметричний підпис",
        "• Ed25519 / ECDSA P-256",
        "• Підпис НАД маніфестом",
        "• Публічний ключ в OTP",
        "• Монотонний лічильник",
        "• Захист від відкату",
        "• Ланцюг сертифікатів"
    ]
    for i, item in enumerate(sig_items):
        p.append(text(452, 175 + i * 22, item, size=9.5, color=INK, anchor="start"))
        
    p.append(rect(452, 345, 160, 60, fill="#ffffff", stroke=PURPLE, sw=1, rx=4))
    p.append(text(532, 366, "Гарантує авторство", size=9, color=PURPLETX, bold=True))
    p.append(text(532, 384, "й цілісність пакунка", size=9, color=PURPLETX))

    # 4. Контекст і нотатки
    p.append(rect(640, 90, 180, 330, fill=AMBERBG, stroke=AMBER, sw=1.8, rx=8))
    p.append(text(730, 118, "4. КОНТЕКСТ", size=12.5, color=AMBERTX, bold=True))
    p.append(text(730, 140, "Походження та нотатки", size=10, color=MUTED))
    
    ctx_items = [
        "• Git commit & tag",
        "• Відтворювана збірка",
        "• SBOM (FreeRTOS, HAL)",
        "• Нотатки (Changelog)",
        "• Breaking changes",
        "• Правила міграції NVM",
        "• Звіт валідації в CI"
    ]
    for i, item in enumerate(ctx_items):
        p.append(text(652, 175 + i * 22, item, size=9.5, color=INK, anchor="start"))
        
    p.append(rect(652, 345, 156, 60, fill="#ffffff", stroke=AMBER, sw=1, rx=4))
    p.append(text(730, 366, "Аудит, супровід", size=9, color=AMBERTX, bold=True))
    p.append(text(730, 384, "й безпечна міграція", size=9, color=AMBERTX))

    render(os.path.join(OUT, "release-object-anatomy.svg"), W, H, *p)


# ── Фігура 2: Структура бінарного заголовка маніфесту ────────────────────────
def fig_manifest_header():
    W, H = 840, 480
    p = []
    
    p.append(text(W / 2, 26, "Анатомія бінарного дескриптора прошивки (Firmware Header)", size=15, color=INK, bold=True))
    
    # Пояснення структури пам'яті
    p.append(rect(30, 48, 780, 416, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    
    # Поля структури у вигляді таблиці пам'яті
    fields = [
        ("0x00..0x03", "4 B", "magic_word", "0x46574D46 ('FWMF')", "Сигнатура валідності заголовка", BLUEBG, NEG),
        ("0x04..0x07", "4 B", "header_version", "0x00000001 (v1)", "Формат структури дескриптора", BLUEBG, NEG),
        ("0x08..0x0B", "4 B", "target_hw_id", "0x0000A1F0", "Ідентифікатор сімейства плати", GREENBG, FIELD),
        ("0x0C..0x0F", "4 B", "hw_rev_min / max", "min=0x01, max=0x03", "Діапазон сумісних ревізій PCB", GREENBG, FIELD),
        ("0x10..0x13", "4 B", "fw_version", "1.4.0.128 (SemVer)", "Версія корисного коду прошивки", GREENBG, FIELD),
        ("0x14..0x17", "4 B", "security_version", "0x00000004", "Anti-rollback монотонний лічильник", REDBG, POS),
        ("0x18..0x1B", "4 B", "payload_size", "245 760 байтів", "Фактичний розмір бінарного коду", BLUEBG, NEG),
        ("0x1C..0x1F", "4 B", "load_address", "0x08020000", "Цільова адреса у Flash пам'яті", BLUEBG, NEG),
        ("0x20..0x3F", "32 B", "payload_sha256", "e3b0c44298fc1c14...", "Криптографічний геш образу коду", AMBERBG, AMBER),
        ("0x40..0x7F", "64 B", "signature", "Ed25519 R+S signature", "Асиметричний підпис полів 0x00..0x3F", PURPLEBG, PURPLE),
    ]
    
    # Заголовки стовпців
    p.append(rect(45, 60, 750, 28, fill=FILL, stroke=LINE, sw=1, rx=4))
    p.append(text(85, 78, "Зсув (Offset)", size=10.5, color=INK, bold=True))
    p.append(text(145, 78, "Розмір", size=10.5, color=INK, bold=True))
    p.append(text(235, 78, "Ім'я поля структури", size=10.5, color=INK, bold=True))
    p.append(text(375, 78, "Значення / Приклад", size=10.5, color=INK, bold=True))
    p.append(text(600, 78, "Призначення та семантика для Bootloader'а", size=10.5, color=INK, bold=True))
    
    y = 96
    for off, sz, name, val, desc, bg, st in fields:
        h_row = 32
        p.append(rect(45, y, 750, h_row, fill=bg, stroke=st, sw=1, rx=4))
        p.append(text(85, y + 20, off, size=10, color=INK))
        p.append(text(145, y + 20, sz, size=9.5, color=MUTED))
        p.append(text(175, y + 20, name, size=10, color=INK, anchor="start", bold=True))
        p.append(text(315, y + 20, val, size=9.5, color=st, anchor="start"))
        p.append(text(495, y + 20, desc, size=9.5, color=INK, anchor="start"))
        y += 36

    render(os.path.join(OUT, "manifest-header-layout.svg"), W, H, *p)


# ── Фігура 3: Ланцюг підпису та верифікації ──────────────────────────────────
def fig_signing_chain():
    W, H = 860, 480
    p = []
    
    p.append(text(W / 2, 26, "Ланцюг довіри: підписання в релізному конвеєрі та перевірка на чипі", size=15, color=INK, bold=True))
    
    # Ліва колонка: Конвеєр збірки та підпису
    p.append(rect(24, 46, 390, 416, fill=FILL, stroke=LINE, sw=1.5, rx=10))
    p.append(text(219, 74, "1. ЗБІРКА Й ПІДПИСАННЯ (Сервер / HSM)", size=12.5, color=NEG, bold=True))
    
    # Кроки підпису
    p.append(rect(44, 94, 350, 46, fill="#ffffff", stroke=LINE, sw=1, rx=6))
    p.append(text(60, 114, "Корисний код:", size=10, color=MUTED, anchor="start"))
    p.append(text(150, 114, "firmware.bin (компіляція)", size=10.5, color=INK, anchor="start", bold=True))
    p.append(text(60, 130, "Розмір: 240 КБ, вектори за адресою 0x08020000", size=9, color=MUTED, anchor="start"))
    
    p.append(arrow(219, 140, 219, 156, color=INK, sw=1.5))
    
    p.append(rect(44, 158, 350, 46, fill=BLUEBG, stroke=NEG, sw=1.2, rx=6))
    p.append(text(60, 178, "Обчислення гешу:", size=10, color=NEG, anchor="start"))
    p.append(text(175, 178, "SHA-256(firmware.bin)", size=10.5, color=INK, anchor="start", bold=True))
    p.append(text(60, 194, "Отримуємо 32-байтний відбиток коду", size=9, color=MUTED, anchor="start"))
    
    p.append(arrow(219, 204, 219, 220, color=INK, sw=1.5))
    
    p.append(rect(44, 222, 350, 54, fill=GREENBG, stroke=FIELD, sw=1.2, rx=6))
    p.append(text(60, 242, "Генерація маніфесту:", size=10, color=FIELD, anchor="start"))
    p.append(text(195, 242, "Header (поля 0x00..0x3F)", size=10.5, color=INK, anchor="start", bold=True))
    p.append(text(60, 260, "Записуємо HW ID, SemVer, Security Version, SHA-256", size=9, color=MUTED, anchor="start"))
    
    p.append(arrow(219, 276, 219, 292, color=INK, sw=1.5))
    
    p.append(rect(44, 294, 350, 60, fill=PURPLEBG, stroke=PURPLE, sw=1.5, rx=6))
    p.append(text(60, 314, "Накладання підпису:", size=10, color=PURPLETX, anchor="start"))
    p.append(text(190, 314, "HSM / Release Private Key", size=10.5, color=PURPLETX, anchor="start", bold=True))
    p.append(text(60, 332, "Ed25519 Sign(Header_Data, PrivKey) -> 64 B", size=9.5, color=INK, anchor="start"))
    p.append(text(60, 346, "Приватний ключ захищено в HSM", size=9.5, color=POS, anchor="start"))
    
    p.append(arrow(219, 354, 219, 370, color=INK, sw=1.5))
    
    p.append(rect(44, 372, 350, 76, fill=AMBERBG, stroke=AMBER, sw=1.2, rx=6))
    p.append(text(60, 394, "Зшивання капсули:", size=10, color=AMBERTX, anchor="start"))
    p.append(text(180, 394, "Release Bundle (.fwpkg)", size=10.5, color=INK, anchor="start", bold=True))
    p.append(text(60, 412, "[Header 128B (вкл. підпис)] + [firmware.bin]", size=9.5, color=INK, anchor="start"))
    p.append(text(60, 430, "Постачається на OTA сервер або утиліту програмування", size=9, color=MUTED, anchor="start"))
    
    # Права колонка: Верифікація завантажувачем на залізі
    p.append(rect(446, 46, 390, 416, fill=FILL, stroke=LINE, sw=1.5, rx=10))
    p.append(text(641, 74, "2. ПЕРЕВІРКА НА ЗАЛІЗІ (Bootloader)", size=12.5, color=FIELD, bold=True))
    
    # Кроки перевірки
    p.append(rect(466, 94, 350, 52, fill="#ffffff", stroke=LINE, sw=1, rx=6))
    p.append(text(482, 114, "Крок 1. Перевірка заліза:", size=10, color=MUTED, anchor="start"))
    p.append(text(635, 114, "HW ID & PCB Rev", size=10.5, color=INK, anchor="start", bold=True))
    p.append(text(482, 132, "Чи сумісний реліз із цією платою? (Ні -> Відхилити)", size=9, color=POS, anchor="start"))
    
    p.append(arrow(641, 146, 641, 160, color=INK, sw=1.5))
    
    p.append(rect(466, 162, 350, 52, fill=REDBG, stroke=POS, sw=1.2, rx=6))
    p.append(text(482, 182, "Крок 2. Захист від відкату:", size=10, color=POS, anchor="start"))
    p.append(text(645, 182, "Anti-rollback Check", size=10.5, color=INK, anchor="start", bold=True))
    p.append(text(482, 200, "Header.SecVer >= Device.SecVer (eFuse/OTP лічильник)", size=9, color=INK, anchor="start"))
    
    p.append(arrow(641, 214, 641, 228, color=INK, sw=1.5))
    
    p.append(rect(466, 230, 350, 54, fill=PURPLEBG, stroke=PURPLE, sw=1.2, rx=6))
    p.append(text(482, 250, "Крок 3. Перевірка підпису:", size=10, color=PURPLETX, anchor="start"))
    p.append(text(645, 250, "Ed25519 Verify", size=10.5, color=PURPLETX, anchor="start", bold=True))
    p.append(text(482, 268, "Публічний ключ зашитий у ROM/eFuse чипа", size=9, color=MUTED, anchor="start"))
    
    p.append(arrow(641, 284, 641, 298, color=INK, sw=1.5))
    
    p.append(rect(466, 300, 350, 54, fill=BLUEBG, stroke=NEG, sw=1.2, rx=6))
    p.append(text(482, 320, "Крок 4. Цілісність коду:", size=10, color=NEG, anchor="start"))
    p.append(text(630, 320, "SHA-256(Payload)", size=10.5, color=INK, anchor="start", bold=True))
    p.append(text(482, 338, "Обчислений геш == Header.payload_sha256", size=9, color=MUTED, anchor="start"))
    
    p.append(arrow(641, 354, 641, 368, color=INK, sw=1.5))
    
    p.append(rect(466, 370, 350, 78, fill=GREENBG, stroke=FIELD, sw=1.5, rx=6))
    p.append(text(482, 392, "Крок 5. Активація образу:", size=10, color=FIELD, anchor="start"))
    p.append(text(635, 392, "Flash & Boot Jump", size=11, color=FIELD, anchor="start", bold=True))
    p.append(text(482, 412, "Оновлення eFuse лічильника -> Запис у Flash ->", size=9, color=INK, anchor="start"))
    p.append(text(482, 430, "Скидання MSP/PC і передача керування новій прошивці", size=9, color=INK, anchor="start"))

    render(os.path.join(OUT, "signing-verification-chain.svg"), W, H, *p)


# ── Фігура 4: Життєвий цикл і конвеєр випуску ────────────────────────────────
def fig_release_lifecycle():
    W, H = 840, 380
    p = []
    
    p.append(text(W / 2, 26, "Життєвий цикл релізу: від Git-тегу до цільового парку пристроїв", size=15, color=INK, bold=True))
    
    stages = [
        (25, 100, "1. ФІКСАЦІЯ", NEG, BLUEBG,
         ["Git tag v1.4.0", "Заморозка коду", "Формування", "Changelog"]),
        (190, 100, "2. ЗБІРКА", NEG, BLUEBG,
         ["Герметичний CI", "Крос-компіляція", "Генерація .elf/.bin", "Збереження .map"]),
        (355, 100, "3. ВАЛІДАЦІЯ", AMBER, AMBERBG,
         ["HIL-тести на платі", "Sizecheck пам'яті", "Статичний аналіз", "Звіт сумісності"]),
        (520, 100, "4. ПІДПИСАННЯ", PURPLE, PURPLEBG,
         ["Маніфест (паспорт)", "HSM підпис Ed25519", "Anti-rollback індекс", "Пакет .bundle"]),
        (685, 100, "5. РОЗГОРТАННЯ", FIELD, GREENBG,
         ["Canary парк (1%)", "Бета-тестування", "Масовий OTA випуск", "Моніторинг збоїв"]),
    ]
    
    sw, sh = 130, 170
    for x, y, title, col, bg, lines in stages:
        p.append(rect(x, y, sw, sh, fill=bg, stroke=col, sw=1.8, rx=8))
        tagcol = AMBERTX if col == AMBER else PURPLETX if col == PURPLE else col
        p.append(text(x + sw / 2, y + 26, title, size=11, color=tagcol, bold=True))
        
        for i, ln in enumerate(lines):
            p.append(text(x + sw / 2, y + 58 + i * 22, ln, size=9.5, color=INK))
            
    # Стрілки між етапами
    p.append(arrow(155, 185, 190, 185, color=INK, sw=1.8))
    p.append(arrow(320, 185, 355, 185, color=INK, sw=1.8))
    p.append(arrow(485, 185, 520, 185, color=INK, sw=1.8))
    p.append(arrow(650, 185, 685, 185, color=INK, sw=1.8))
    
    # Нижня стрічка контролю якості
    p.append(rect(25, 290, 790, 46, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    p.append(text(50, 318, "Критерій воротаря:", size=10, color=MUTED, anchor="start", bold=True))
    p.append(text(170, 318, "Провал будь-якого тесту або розбіжність гешу негайно зупиняє публікацію релізу", size=9.5, color=POS, anchor="start"))

    render(os.path.join(OUT, "release-lifecycle-pipeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_release_anatomy()
    fig_manifest_header()
    fig_signing_chain()
    fig_release_lifecycle()
    print("All figures generated successfully.")
