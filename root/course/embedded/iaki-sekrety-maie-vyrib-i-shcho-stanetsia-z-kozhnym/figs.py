# -*- coding: utf-8 -*-
"""Фігури для статті «Які секрети має виріб і що станеться з кожним при витоку».
Генерує SVG у ./img/ за допомогою svgkit.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "scripts"))
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

from svgkit import (
    render, text, mtext, rect, line, arrow, circle, fitbox,
    INK, MUTED, POS, NEG, FIELD, FILL, LINE, BG
)

IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

# Палітра для безпекових рівнів
SEC_FATAL   = "#b91c1c"   # критичний червоний
SEC_WARN    = "#d97706"   # застережливий бурштиновий
SEC_SAFE    = "#047857"   # безпечний зелений
SEC_BLUE    = "#1d4ed8"   # системний синій
SEC_PURPLE  = "#7c3aed"   # криптографічний фіолетовий
CARD_BG     = "#ffffff"


def fig_secrets_hierarchy():
    """1. secrets-hierarchy-pyramid.svg — Ієрархія та класифікація секретів виробу."""
    W, H = 880, 520
    parts = []

    # Загальний фон
    parts.append(rect(15, 15, W - 30, H - 30, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=10))
    parts.append(text(W / 2, 42, "Ієрархія секретів вбудованого виробу за рівнями ізоляції", size=16, color=INK, bold=True))

    levels = [
        {
            "y": 68, "h": 76, "stroke": SEC_FATAL, "header_bg": "#fee2e2", "header_c": SEC_FATAL,
            "title": "1. Корпоративні ключі підпису прошивки (OEM Signing Authority)",
            "where": "Де живе: Виключно в ізольованому HSM / KMS сервері збірки (НЕМАЄ на пристрої!)",
            "role": "Приватні ключі ECDSA / RSA для підпису офіційних оновлень OTA та образів ОС",
            "impact": "Витік: Повна катастрофа всього модельного ряду (100% пристроїв під загрозою фальшивої OTA)"
        },
        {
            "y": 154, "h": 76, "stroke": SEC_PURPLE, "header_bg": "#f3e8ff", "header_c": SEC_PURPLE,
            "title": "2. Апаратні кореневі секрети кристала (Silicon Root of Trust & Flash Encryption)",
            "where": "Де живе: Одноразові апаратні перемички eFuse / OTP, PUF-генератор всередині SoC",
            "role": "Ключ розшифрування зовнішньої Flash (FEK), геш публічного ключа Secure Boot",
            "impact": "Витік: Дешифрування прошивки конкретного зразка; глобальний крах, якщо ключ однаковий у партії"
        },
        {
            "y": 240, "h": 76, "stroke": SEC_SAFE, "header_bg": "#dcfce7", "header_c": SEC_SAFE,
            "title": "3. Унікальна ідентичність екземпляра (Device Identity & mTLS Client Keys)",
            "where": "Де живе: Криптографічний Secure Element (ATECC608, TPM), апаратний анклав",
            "role": "Приватний ключ клієнтського сертифіката для взаємної автентифікації з хмарою (mTLS / MQTT)",
            "impact": "Витік: Підміна одного скомпрометованого приладу; миттєво відкликається на сервері без шкоди парку"
        },
        {
            "y": 326, "h": 76, "stroke": SEC_WARN, "header_bg": "#fef3c7", "header_c": SEC_WARN,
            "title": "4. Мережеві та локальні облікові дані (Network Credentials)",
            "where": "Де живе: Енергонезалежна пам'ять NVS / Flash мікроконтролера, захищена апаратно",
            "role": "Паролі Wi-Fi (WPA2/WPA3 PSK), ключі зв'язування Bluetooth (LTK), ключі LoRaWAN AppKey",
            "impact": "Витік: Компрометація локальної мережі замовника (Pivot Attack); заміна пароля на точці доступу"
        },
        {
            "y": 412, "h": 76, "stroke": SEC_BLUE, "header_bg": "#dbeafe", "header_c": SEC_BLUE,
            "title": "5. Операційні, сервісні та користувацькі токени (User Data & Session Tokens)",
            "where": "Де живе: Зашифрований розділ NVS, оперативна пам'ять RAM у процесі виконання",
            "role": "API-токени зовнішніх служб, паролі сервісного меню, тимчасові сесійні ключі TLS",
            "impact": "Витік: Порушення приватності власника або скидання налаштувань конкретного екземпляра"
        }
    ]

    for lvl in levels:
        by, bh = lvl["y"], lvl["h"]
        bx, bw = 35, W - 70
        parts.append(rect(bx, by, bw, bh, fill=CARD_BG, stroke=lvl["stroke"], sw=1.5, rx=6))
        parts.append(rect(bx, by, bw, 24, fill=lvl["header_bg"], stroke=lvl["stroke"], sw=1, rx=6))
        parts.append(text(bx + 15, by + 16, lvl["title"], size=12, color=lvl["header_c"], bold=True, anchor="start"))
        parts.append(text(bx + 15, by + 40, lvl["where"], size=10.5, color=INK, anchor="start"))
        parts.append(text(bx + 15, by + 56, lvl["role"], size=10.5, color=MUTED, anchor="start"))
        parts.append(text(bx + 15, by + 70, lvl["impact"], size=10.5, color=lvl["header_c"], bold=True, anchor="start"))

    return render(out("secrets-hierarchy-pyramid.svg"), W, H, "".join(parts))


def fig_blast_radius():
    """2. blast-radius-comparison.svg — Порівняння радіуса ураження при витоку різних секретів."""
    W, H = 880, 480
    parts = []

    parts.append(rect(15, 15, W - 30, H - 30, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=10))
    parts.append(text(W / 2, 42, "Порівняння радіуса ураження (Blast Radius) при витоку ключів", size=16, color=INK, bold=True))

    col_w = 260
    col_h = 390
    cols = [
        {
            "x": 35, "stroke": SEC_SAFE, "header_bg": "#dcfce7", "header_c": SEC_SAFE,
            "title": "Локальний (1 : 1)",
            "subtitle": "Унікальний ключ екземпляра",
            "items": [
                ("Об'єкт атаки:", "Приватний ключ mTLS конкретної плати"),
                ("Масштаб:", "1 пристрій із 100 000 у парку"),
                ("Загроза:", "Фальсифікація показників одного сенсора, витрата квоти трафіку"),
                ("Реагування:", "Миттєве відкликання сертифіката через хмарний реєстр / CRL"),
                ("Наслідки для парку:", "Нульові: решта 99 999 приладів працюють у штатному режимі"),
                ("Оцінка ризику:", "Низький (контрольований інцидент)")
            ]
        },
        {
            "x": 310, "stroke": SEC_WARN, "header_bg": "#fef3c7", "header_c": SEC_WARN,
            "title": "Периметровий (1 : Сегмент)",
            "subtitle": "Мережеві та сервісні паролі",
            "items": [
                ("Об'єкт атаки:", "Wi-Fi PSK, BLE ключ, пароль діагностики"),
                ("Масштаб:", "Локальна інфраструктура замовника"),
                ("Загроза:", "Перехідна атака (Pivot) з розумного датчика на корпоративну мережу"),
                ("Реагування:", "Зміна пароля Wi-Fi роутера, скидання конфігурації приладу"),
                ("Наслідки для парку:", "Обмежені об'єктом, де встановлено скомпрометований пристрій"),
                ("Оцінка ризику:", "Середній (загроза інфраструктурі)")
            ]
        },
        {
            "x": 585, "stroke": SEC_FATAL, "header_bg": "#fee2e2", "header_c": SEC_FATAL,
            "title": "Глобальний (1 : Усі пристрої)",
            "subtitle": "Кореневий ключ підпису / Мастер-ключ",
            "items": [
                ("Об'єкт атаки:", "Приватний ключ підпису OTA оновлень"),
                ("Масштаб:", "100% приладів модельного ряду у світі"),
                ("Загроза:", "Масове перепрошивання шкідливим ПЗ, створення ботнетів, блокування"),
                ("Реагування:", "Катастрофічне: неможливість безпечного OTA без відкликання заліза"),
                ("Наслідки для парку:", "Повна втрата довіри, знищення бренду, відкликання виробів"),
                ("Оцінка ризику:", "Критичний (загибель продукту)")
            ]
        }
    ]

    for col in cols:
        cx = col["x"]
        parts.append(rect(cx, 68, col_w, col_h, fill=CARD_BG, stroke=col["stroke"], sw=2, rx=8))
        parts.append(rect(cx, 68, col_w, 48, fill=col["header_bg"], stroke=col["stroke"], sw=1, rx=8))
        parts.append(text(cx + col_w / 2, 90, col["title"], size=13, color=col["header_c"], bold=True))
        parts.append(text(cx + col_w / 2, 107, col["subtitle"], size=10.5, color=INK, bold=False))

        cy = 135
        for label, val in col["items"]:
            parts.append(text(cx + 12, cy, label, size=10.5, color=col["header_c"], bold=True, anchor="start"))
            cy += 16
            lines = []
            words = val.split(" ")
            cur = ""
            for w in words:
                if len(cur + " " + w) > 34:
                    lines.append(cur)
                    cur = w
                else:
                    cur = (cur + " " + w).strip()
            if cur:
                lines.append(cur)
            for ln in lines:
                parts.append(text(cx + 12, cy, ln, size=10, color=INK, anchor="start"))
                cy += 14
            cy += 6

    return render(out("blast-radius-comparison.svg"), W, H, "".join(parts))


def fig_secret_lifecycle():
    """3. secret-lifecycle-flow.svg — Життєвий цикл секрету у виробі."""
    W, H = 880, 440
    parts = []

    parts.append(rect(15, 15, W - 30, H - 30, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=10))
    parts.append(text(W / 2, 42, "Повний життєвий цикл секрету: від випадковості до знищення", size=16, color=INK, bold=True))

    steps = [
        {
            "num": "1", "title": "Генерація", "sub": "CSPRNG / HSM",
            "desc": "Справжня апаратна ентропія\nв середині Secure Element\nабо заводського HSM",
            "color": SEC_BLUE, "bg": "#dbeafe"
        },
        {
            "num": "2", "title": "Прошивання", "sub": "Factory Provisioning",
            "desc": "Запис в eFuse / OTP\nна захищеному стенді\nбез витоку в логи збірки",
            "color": SEC_PURPLE, "bg": "#f3e8ff"
        },
        {
            "num": "3", "title": "Ізоляція", "sub": "Hardware Enclave",
            "desc": "Ключ не залишає крипточип;\nоперації підпису/шифрування\nвиконуються всередині",
            "color": SEC_SAFE, "bg": "#dcfce7"
        },
        {
            "num": "4", "title": "Ротація", "sub": "Zero-Touch Re-keying",
            "desc": "Регулярне оновлення\nсесійних і транспортних ключів\nчерез безпечний mTLS",
            "color": SEC_WARN, "bg": "#fef3c7"
        },
        {
            "num": "5", "title": "Знищення", "sub": "Zeroization & Shred",
            "desc": "Апаратне очищення пам'яті\nпри розтині (Tamper)\nабо списанні пристрою",
            "color": SEC_FATAL, "bg": "#fee2e2"
        }
    ]

    card_w = 145
    card_h = 240
    gap = 24
    start_x = 35
    card_y = 80

    for i, st in enumerate(steps):
        cx = start_x + i * (card_w + gap)
        # Рамка картки
        parts.append(rect(cx, card_y, card_w, card_h, fill=CARD_BG, stroke=st["color"], sw=2, rx=8))
        # Шапка картки
        parts.append(rect(cx, card_y, card_w, 42, fill=st["bg"], stroke=st["color"], sw=1, rx=8))
        parts.append(circle(cx + 20, card_y + 21, 12, fill=st["color"], stroke=st["color"], sw=1))
        parts.append(text(cx + 20, card_y + 25, st["num"], size=12, color="#ffffff", bold=True))
        parts.append(text(cx + 80, card_y + 26, st["title"], size=13, color=st["color"], bold=True))

        # Підзаголовок
        parts.append(text(cx + card_w / 2, card_y + 64, st["sub"], size=10, color=MUTED, bold=True))
        parts.append(line(cx + 10, card_y + 76, cx + card_w - 10, card_y + 76, color="#e2e8f0", sw=1))

        # Опис
        desc_lines = st["desc"].split("\n")
        dy = card_y + 105
        for d_ln in desc_lines:
            parts.append(text(cx + card_w / 2, dy, d_ln, size=10.5, color=INK))
            dy += 22

        # Стрілка переходу
        if i < len(steps) - 1:
            ax1 = cx + card_w + 3
            ax2 = ax1 + gap - 6
            ay = card_y + card_h / 2
            parts.append(arrow(ax1, ay, ax2, ay, color=LINE, sw=2))

    # Нижній висновок-панель
    parts.append(rect(35, 345, W - 70, 60, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    parts.append(text(W / 2, 368, "Золоте правило життєвого циклу: Секрет не повинен з'являтися у відкритому вигляді", size=12, color=SEC_FATAL, bold=True))
    parts.append(text(W / 2, 388, "ні в коді репозиторію, ні в логах збірки, ні в незахищеній пам'яті RAM, ні на незашифрованій шині SPI Flash", size=11, color=INK))

    return render(out("secret-lifecycle-flow.svg"), W, H, "".join(parts))


def fig_asymmetric_vs_symmetric():
    """4. asymmetric-vs-symmetric-trust.svg — Симетрична пастка проти асиметричної довіри."""
    W, H = 880, 500
    parts = []

    parts.append(rect(15, 15, W - 30, H - 30, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=10))
    parts.append(text(W / 2, 42, "Архітектура довіри: Симетрична пастка проти Асиметричного захисту", size=16, color=INK, bold=True))

    # Верхня панель: Симетрична пастка
    top_y = 65
    top_h = 195
    parts.append(rect(35, top_y, W - 70, top_h, fill="#fff5f5", stroke=SEC_FATAL, sw=2, rx=8))
    parts.append(rect(35, top_y, W - 70, 28, fill="#fee2e2", stroke=SEC_FATAL, sw=1, rx=8))
    parts.append(text(50, top_y + 19, "СИМЕТРИЧНА ПАСТКА (Фатальний антипатерн: один секрет для підпису й перевірки)", size=12, color=SEC_FATAL, bold=True, anchor="start"))

    # Сервер
    parts.append(rect(55, top_y + 45, 170, 125, fill=CARD_BG, stroke=SEC_FATAL, sw=1.5, rx=6))
    parts.append(text(140, top_y + 68, "Сервер виробника", size=12, color=INK, bold=True))
    parts.append(rect(65, top_y + 85, 150, 32, fill="#fee2e2", stroke=SEC_FATAL, sw=1, rx=4))
    parts.append(text(140, top_y + 105, "Ключ K (симетричний)", size=10.5, color=SEC_FATAL, bold=True))
    parts.append(text(140, top_y + 138, "Підписує прошивку: HMAC(K)", size=9.5, color=MUTED))

    # Стрілка передачі оновлення
    parts.append(arrow(230, top_y + 108, 335, top_y + 108, color=SEC_FATAL, sw=2))
    parts.append(text(282, top_y + 98, "OTA образ", size=10, color=INK, bold=True))

    # Пристрої
    parts.append(rect(340, top_y + 45, 230, 125, fill=CARD_BG, stroke=SEC_FATAL, sw=1.5, rx=6))
    parts.append(text(455, top_y + 68, "100 000 серійних пристроїв", size=12, color=INK, bold=True))
    parts.append(rect(355, top_y + 85, 200, 32, fill="#fee2e2", stroke=SEC_FATAL, sw=1, rx=4))
    parts.append(text(455, top_y + 105, "Той самий Ключ K у пам'яті!", size=10.5, color=SEC_FATAL, bold=True))
    parts.append(text(455, top_y + 138, "Перевіряє: HMAC(K) == образ.hmac", size=9.5, color=MUTED))

    # Злом 1 пристрою
    parts.append(arrow(575, top_y + 108, 645, top_y + 108, color=SEC_FATAL, sw=2))
    parts.append(rect(650, top_y + 45, 180, 125, fill="#fee2e2", stroke=SEC_FATAL, sw=2, rx=6))
    parts.append(text(740, top_y + 68, "Злом 1 плати ($50)", size=11.5, color=SEC_FATAL, bold=True))
    parts.append(text(740, top_y + 92, "Зчитування Flash / RAM", size=10, color=INK))
    parts.append(text(740, top_y + 110, "→ Витік Ключа K!", size=11, color=SEC_FATAL, bold=True))
    parts.append(text(740, top_y + 135, "Наслідок: Атакуючий підписує", size=9.5, color=SEC_FATAL))
    parts.append(text(740, top_y + 150, "прошивку для ВСЬОГО парку!", size=9.5, color=SEC_FATAL, bold=True))

    # Нижня панель: Асиметрична архітектура
    bot_y = 275
    bot_h = 200
    parts.append(rect(35, bot_y, W - 70, bot_h, fill="#f0fdf4", stroke=SEC_SAFE, sw=2, rx=8))
    parts.append(rect(35, bot_y, W - 70, 28, fill="#dcfce7", stroke=SEC_SAFE, sw=1, rx=8))
    parts.append(text(50, bot_y + 19, "АСИМЕТРИЧНА ДОБРОЧЕСНІСТЬ (Канонічний дизайн: розділення підпису та перевірки)", size=12, color=SEC_SAFE, bold=True, anchor="start"))

    # Сервер HSM
    parts.append(rect(55, bot_y + 45, 170, 135, fill=CARD_BG, stroke=SEC_SAFE, sw=1.5, rx=6))
    parts.append(text(140, bot_y + 68, "Сервер HSM виробника", size=12, color=INK, bold=True))
    parts.append(rect(65, bot_y + 85, 150, 32, fill="#fee2e2", stroke=SEC_FATAL, sw=1, rx=4))
    parts.append(text(140, bot_y + 105, "Приватний ключ SK_oem", size=10.5, color=SEC_FATAL, bold=True))
    parts.append(text(140, bot_y + 135, "Ніколи не залишає HSM", size=10, color=SEC_SAFE, bold=True))
    parts.append(text(140, bot_y + 155, "Підпис: ECDSA_Sign(SK, FW)", size=9.5, color=MUTED))

    # Стрілка OTA
    parts.append(arrow(230, bot_y + 110, 335, bot_y + 110, color=SEC_SAFE, sw=2))
    parts.append(text(282, bot_y + 100, "Підписана OTA", size=10, color=INK, bold=True))

    # Пристрої з публічним ключем
    parts.append(rect(340, bot_y + 45, 230, 135, fill=CARD_BG, stroke=SEC_SAFE, sw=1.5, rx=6))
    parts.append(text(455, bot_y + 68, "100 000 серійних пристроїв", size=12, color=INK, bold=True))
    parts.append(rect(355, bot_y + 85, 200, 32, fill="#dbeafe", stroke=SEC_BLUE, sw=1, rx=4))
    parts.append(text(455, bot_y + 105, "Публічний ключ PK_oem", size=10.5, color=SEC_BLUE, bold=True))
    parts.append(text(455, bot_y + 135, "Зашитий в OTP eFuse / ROM", size=10, color=MUTED))
    parts.append(text(455, bot_y + 155, "Перевірка: ECDSA_Verify(PK)", size=9.5, color=MUTED))

    # Злом 1 пристрою в асиметричній моделі
    parts.append(arrow(575, bot_y + 110, 645, bot_y + 110, color=SEC_SAFE, sw=2))
    parts.append(rect(650, bot_y + 45, 180, 135, fill="#f0fdf4", stroke=SEC_SAFE, sw=2, rx=6))
    parts.append(text(740, bot_y + 68, "Злом 1 плати ($50)", size=11.5, color=SEC_SAFE, bold=True))
    parts.append(text(740, bot_y + 92, "Зчитування Flash / RAM", size=10, color=INK))
    parts.append(text(740, bot_y + 112, "Знайдено: Публічний PK", size=10.5, color=SEC_BLUE, bold=True))
    parts.append(text(740, bot_y + 135, "Наслідок: Нульова загроза!", size=10, color=SEC_SAFE, bold=True))
    parts.append(text(740, bot_y + 152, "Публічний ключ відкритий,", size=9.5, color=MUTED))
    parts.append(text(740, bot_y + 167, "підробити підпис неможливо", size=9.5, color=SEC_SAFE, bold=True))

    return render(out("asymmetric-vs-symmetric-trust.svg"), W, H, "".join(parts))


def main():
    fig_secrets_hierarchy()
    fig_blast_radius()
    fig_secret_lifecycle()
    fig_asymmetric_vs_symmetric()
    print("Всі 4 фігури для теми згенеровано успішно в img/")


if __name__ == "__main__":
    main()
