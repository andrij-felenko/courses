#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор векторних діаграм для теми LUKS2: формат заголовка шифрованого тому."""

import os
import sys

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_luks2_disk_layout():
    """Фігура 1: Розмітка блокового пристрою з форматом LUKS2."""
    w, h = 960, 480
    frags = []

    # Заголовок секції диска
    frags.append(text(w / 2, 28, "Розмітка блокового тома LUKS2 на фізичному носії", size=18, bold=True))

    # Загальний контейнер диска
    frags.append(rect(40, 55, 880, 110, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))

    # Секції диска
    # 1. Первинний заголовок + JSON (4 MiB)
    frags.append(rect(50, 65, 170, 90, fill="#e0f2fe", stroke="#0284c7", sw=1.8, rx=6))
    frags.append(mtext(135, 95, ["Первинний заголовок", "4 КіБ бінарний + JSON", "Зсув: 0x000000 (0)"], size=12, bold=True, color="#0369a1"))

    # 2. Вторинний заголовок + JSON (4 MiB)
    frags.append(rect(230, 65, 170, 90, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=6))
    frags.append(mtext(315, 95, ["Вторинний заголовок", "4 КіБ бінарний + JSON", "Зсув: 0x400000 (4 МіБ)"], size=12, bold=True, color="#b45309"))

    # 3. Область замкових шпарин (Keyslots binary area)
    frags.append(rect(410, 65, 190, 90, fill="#f3e8ff", stroke="#9333ea", sw=1.8, rx=6))
    frags.append(mtext(505, 95, ["Бінарні слоти ключів", "AFSplit-смуги (AF-stripes)", "Зсув: 0x800000 (8 МіБ)"], size=12, bold=True, color="#7e22ce"))

    # 4. Корисне навантаження (Payload data segment)
    frags.append(rect(610, 65, 300, 90, fill="#dcfce7", stroke="#16a34a", sw=1.8, rx=6))
    frags.append(mtext(760, 95, ["Сегмент даних (Payload)", "Зашифровані сектори файлової системи", "AES-XTS-512 / dm-crypt"], size=12, bold=True, color="#15803d"))

    # Деталізація заголовка 4 КіБ + метадані
    frags.append(text(220, 200, "Детальна структура бінарного заголовка luks2_hdr (4096 байтів):", size=14, bold=True))

    # Таблиця полів бінарного заголовка
    fields = [
        ("0x000..0x005", "magic (6 B)", "«LUKS\\xba\\xbe» або «SKUL\\xba\\xbe»"),
        ("0x006..0x007", "version (2 B)", "0x0002 (версія LUKS2)"),
        ("0x008..0x00f", "hdr_size (8 B)", "Загальний розмір заголовка (наприклад, 4 МіБ)"),
        ("0x010..0x017", "seqid (8 B)", "Монотонний лічильник транзакцій (seqid)"),
        ("0x018..0x047", "label (48 B)", "Мітка тому в ASCII"),
        ("0x048..0x067", "csum_alg (32 B)", "Алгоритм контрольної суми (sha256)"),
        ("0x068..0x0a7", "salt (64 B)", "Сіль контрольної суми заголовка"),
        ("0x0a8..0x0d3", "uuid (44 B)", "Унікальний ідентифікатор UUID"),
        ("0x100..0x13f", "csum (64 B)", "Контрольна сума CRC32 / SHA-256 метаданих"),
    ]

    x_start = 50
    y_start = 220
    row_w = 420
    row_h = 24

    for i, (offset, name, desc) in enumerate(fields):
        y = y_start + i * row_h
        frags.append(rect(x_start, y, 90, row_h, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=0))
        frags.append(text(x_start + 45, y + 16, offset, size=11, color=INK))

        frags.append(rect(x_start + 90, y, 110, row_h, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=0))
        frags.append(text(x_start + 145, y + 16, name, size=11, bold=True, color="#0f172a"))

        frags.append(rect(x_start + 200, y, 220, row_h, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=0))
        frags.append(text(x_start + 208, y + 16, desc, size=10, anchor="start", color=MUTED))

    # Права панель: текстова зона JSON
    frags.append(rect(490, 205, 420, 240, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(700, 230, "Текстова зона метаданих JSON (до 4 МіБ − 4 КіБ)", size=13, bold=True, color="#1e293b"))

    json_blocks = [
        ("keyslots", "Опис слотів: тип KDF (Argon2id), сіль, пам'ять, час, AFSplit"),
        ("tokens", "Апаратні токени: systemd-tpm2, systemd-fido2, PKCS#11"),
        ("segments", "Криптографічні сегменти: aes-xts-plain64, розмір сектора"),
        ("digests", "Контрольні геші Master Key для перевірки без розшифрування"),
        ("config", "Системні прапорці, вимоги ядра та вирівнювання пам'яті"),
    ]

    for j, (key, val) in enumerate(json_blocks):
        jy = 255 + j * 36
        frags.append(rect(505, jy, 90, 28, fill="#e2e8f0", stroke="#94a3b8", sw=1, rx=4))
        frags.append(text(550, jy + 18, key, size=11, bold=True, color="#334155"))
        frags.append(text(605, jy + 18, val, size=10, anchor="start", color="#475569"))

    render(os.path.join(IMG_DIR, "luks2-disk-layout.svg"), w, h, *frags)


def fig_luks2_keyslot_resolution():
    """Фігура 2: Послідовність відкриття тому через Keyslot, KDF, AFSplit та завантаження в dm-crypt."""
    w, h = 960, 430
    frags = []

    frags.append(text(w / 2, 26, "Ланцюжок розгортання ключа тому (Volume Key Resolution)", size=18, bold=True))

    # Крок 1: Введення пароля / Токен
    b1, _, _ = textbox(110, 85, "1. Автентифікація\nПароль користувача\nабо токен TPM2/FIDO2", size=12, fill="#e0f2fe", stroke="#0284c7", bold=True)
    frags.append(b1)

    frags.append(arrow(190, 85, 240, 85, color=LINE, sw=1.8))

    # Крок 2: Розтягування ключа через KDF
    b2, _, _ = textbox(330, 85, "2. Функція KDF\nArgon2id / PBKDF2\nПам'ять: 1 ГБ, Час: 2 с", size=12, fill="#fef3c7", stroke="#d97706", bold=True)
    frags.append(b2)

    frags.append(arrow(420, 85, 470, 85, color=LINE, sw=1.8))

    # Крок 3: Ключ розшифрування шпарини (VKDK)
    b3, _, _ = textbox(555, 85, "3. Ключ шпарини\nVKDK (512 біт)\nКлюч для зняття AFSplit", size=12, fill="#f3e8ff", stroke="#9333ea", bold=True)
    frags.append(b3)

    frags.append(arrow(645, 85, 695, 85, color=LINE, sw=1.8))

    # Крок 4: Читання й дешифрування AFSplit смуг
    b4, _, _ = textbox(810, 85, "4. Розшифрування смуг\nAES-XTS-512\n4000 AFSplit-смуг на диску", size=12, fill="#fce7f3", stroke="#db2777", bold=True)
    frags.append(b4)

    # Вертикальна стрілка до кроку 5
    frags.append(arrow(810, 130, 810, 180, color=LINE, sw=1.8))

    # Крок 5: Злиття смуг AFSplit
    b5, _, _ = textbox(810, 225, "5. AFSplit Merge\nXOR + дифузія гешу\nВідновлення Master Key", size=12, fill="#e0e7ff", stroke="#4f46e5", bold=True)
    frags.append(b5)

    frags.append(arrow(725, 225, 675, 225, color=LINE, sw=1.8))

    # Крок 6: Перевірка дайджесту
    b6, _, _ = textbox(555, 225, "6. Перевірка дайджесту\nPBKDF2(Master Key, Сіль)\nЗвірка з об'єктом digests", size=12, fill="#ffedd5", stroke="#ea580c", bold=True)
    frags.append(b6)

    frags.append(arrow(440, 225, 390, 225, color=LINE, sw=1.8))

    # Крок 7: Завантаження в ядро
    b7, _, _ = textbox(270, 225, "7. libcryptsetup ioctl\nDM_TABLE_LOAD\nСтворення crypt-пристрою", size=12, fill="#ecfdf5", stroke="#059669", bold=True)
    frags.append(b7)

    frags.append(arrow(155, 225, 105, 225, color=LINE, sw=1.8))

    # Крок 8: Активація dm-crypt
    b8, _, _ = textbox(55, 225, "8. Готово\n/dev/mapper/root\nОчищення пам'яті", size=12, fill="#dcfce7", stroke="#16a34a", bold=True)
    frags.append(b8)

    # Нижня панель інваріантів безпеки
    frags.append(rect(40, 305, 880, 105, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(480, 330, "Криптографічні гарантії на кожному етапі:", size=13, bold=True, color="#0f172a"))

    inv_points = [
        ("Захист від перебору:", "Argon2id вимагає 1 ГБ ОЗП на кожну спробу, нівелюючи перевагу паралельних ASIC/GPU-ферм"),
        ("Антикриміналістика (AFSplit):", "Пошкодження хоча б одного сектора шпарини безповоротно знищує Master Key"),
        ("Ізоляція в пам'яті:", "Master Key існує в просторі користувача частки секунди і стирається через crypt_safe_memzero()"),
    ]

    for k, (title_inv, text_inv) in enumerate(inv_points):
        frags.append(text(60, 355 + k * 20, title_inv, size=11, bold=True, anchor="start", color="#1e293b"))
        frags.append(text(270, 355 + k * 20, text_inv, size=11, anchor="start", color="#475569"))

    render(os.path.join(IMG_DIR, "luks2-keyslot-resolution.svg"), w, h, *frags)


def fig_luks2_dual_header_recovery():
    """Фігура 3: Атомарне оновлення заголовків та стійкість до збоїв живлення."""
    w, h = 960, 420
    frags = []

    frags.append(text(w / 2, 28, "Атомарне оновлення подвійного заголовка LUKS2 та відновлення", size=18, bold=True))

    # Стан 1: Стабільний стан
    frags.append(rect(40, 60, 270, 230, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(175, 85, "1. Початковий стан", size=13, bold=True, color="#0f172a"))

    frags.append(rect(55, 105, 240, 70, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=6))
    frags.append(mtext(175, 130, ["Первинний заголовок", "seqid = 42", "CRC32: ВАЛІДНИЙ (OK)"], size=11, bold=True, color="#0369a1"))

    frags.append(rect(55, 195, 240, 70, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(mtext(175, 220, ["Вторинний заголовок", "seqid = 42", "CRC32: ВАЛІДНИЙ (OK)"], size=11, bold=True, color="#b45309"))

    frags.append(arrow(315, 175, 360, 175, color=LINE, sw=1.8))

    # Стан 2: Збій під час запису вторинного заголовка
    frags.append(rect(365, 60, 270, 230, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(500, 85, "2. Збій живлення при записі", size=13, bold=True, color="#b91c1c"))

    frags.append(rect(380, 105, 240, 70, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=6))
    frags.append(mtext(500, 130, ["Первинний заголовок", "seqid = 42", "CRC32: ВАЛІДНИЙ (OK)"], size=11, bold=True, color="#0369a1"))

    frags.append(rect(380, 195, 240, 70, fill="#fee2e2", stroke="#ef4444", sw=1.8, rx=6))
    frags.append(mtext(500, 220, ["Вторинний заголовок", "seqid = 43 (обірвано)", "CRC32: ПОШКОДЖЕНО (FAIL)"], size=11, bold=True, color="#b91c1c"))

    frags.append(arrow(640, 175, 685, 175, color=LINE, sw=1.8))

    # Стан 3: Автоматичне відновлення
    frags.append(rect(690, 60, 230, 230, fill="#f8fafc", stroke="#16a34a", sw=1.8, rx=8))
    frags.append(text(805, 85, "3. Вибір та відновлення", size=13, bold=True, color="#15803d"))

    frags.append(rect(705, 105, 200, 80, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=6))
    frags.append(mtext(805, 130, ["Ядро обирає первинний:", "seqid = 42 (дійсний CRC)", "Том монтується штатно"], size=11, bold=True, color="#15803d"))

    frags.append(rect(705, 200, 200, 75, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(mtext(805, 225, ["Автоматичне виправлення:", "cryptsetup repair", "Копіює дійсний заголовок"], size=10, bold=True, color="#334155"))

    # Пояснювальний блок логіки арбітражу
    frags.append(rect(40, 310, 880, 95, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=8))
    frags.append(text(480, 335, "Алгоритм вибору активного заголовка при завантаженні:", size=13, bold=True, color="#1e40af"))

    steps = [
        "1. Читаються обидва бінарні заголовки (0 байт та 4 МіБ) і для кожного обчислюється контрольна сума CRC32.",
        "2. Відкидаються екземпляри з недійсним CRC або пошкодженою структурою JSON.",
        "3. З-поміж валідних екземплярів активним обирається заголовок із максимальним значенням монотонного seqid.",
    ]
    for m, s in enumerate(steps):
        frags.append(text(60, 360 + m * 18, s, size=11, anchor="start", color="#1e3a8a"))

    render(os.path.join(IMG_DIR, "luks2-dual-header-recovery.svg"), w, h, *frags)


def fig_luks2_integrity_stack():
    """Фігура 4: Стек автентифікованого шифрування LUKS2 + dm-integrity."""
    w, h = 960, 450
    frags = []

    frags.append(text(w / 2, 28, "Стек автентифікованого шифрування (LUKS2 + dm-integrity / AEAD)", size=18, bold=True))

    # Рівні стека
    layers = [
        ("Файлова система (VFS)", "ext4, btrfs, XFS — звичайні запити на читання/запис секторів", "#f1f5f9", "#475569", 65),
        ("Шар dm-crypt (Шифрування)", "Перетворення шифротексту: AES-XTS або AEAD (ChaCha20-Poly1305 / AES-GCM)", "#e0f2fe", "#0284c7", 135),
        ("Шар dm-integrity (Цілісність)", "Перевірка тегів HMAC-SHA256 / Poly1305 + журнал транзакцій (Journal)", "#fef3c7", "#d97706", 205),
        ("Фізичний диск / Блоковий пристрій", "NVMe / SSD / HDD — зберігання секторів даних та метаданих цілісності", "#dcfce7", "#16a34a", 275),
    ]

    for name, desc, fill, stroke, y in layers:
        frags.append(rect(60, y, 400, 55, fill=fill, stroke=stroke, sw=1.8, rx=6))
        frags.append(text(260, y + 23, name, size=12, bold=True, color=INK))
        frags.append(text(260, y + 42, desc, size=10, color=MUTED))

    # Стрілки між рівнями
    frags.append(arrow(260, 120, 260, 135, color=LINE, sw=1.8))
    frags.append(arrow(260, 190, 260, 205, color=LINE, sw=1.8))
    frags.append(arrow(260, 260, 260, 275, color=LINE, sw=1.8))

    # Права панель: Структура сектора з цілісністю
    frags.append(rect(490, 65, 420, 265, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(700, 90, "Анатомія сектора на диску з dm-integrity", size=13, bold=True, color="#0f172a"))

    # Сектор даних
    frags.append(rect(510, 115, 270, 75, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=4))
    frags.append(mtext(645, 145, ["Сектор даних (Data Sector)", "512 байтів або 4096 байтів", "Зашифровані дані (AES-XTS)"], size=11, bold=True, color="#0369a1"))

    # Тег автентифікації
    frags.append(rect(785, 115, 105, 75, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=4))
    frags.append(mtext(837, 145, ["Тег MAC", "28–32 B", "HMAC / Poly"], size=10, bold=True, color="#b45309"))

    # Журнал транзакцій
    frags.append(rect(510, 205, 380, 50, fill="#ffedd5", stroke="#ea580c", sw=1.5, rx=4))
    frags.append(mtext(700, 227, ["Журнал цілісності (Integrity Journal)", "Захист від розриву запису (Write-Tear Protection) при аварії живлення"], size=10, bold=True, color="#c2410c"))

    frags.append(text(700, 280, "Помилка при читанні: якщо MAC-тег не збігається,", size=10, bold=True, color="#b91c1c"))
    frags.append(text(700, 298, "ядро повертає -EILSEQ, блокуючи підроблені дані.", size=10, bold=True, color="#b91c1c"))

    # Нижній блок: Чому самого шифрування недостатньо
    frags.append(rect(60, 350, 850, 80, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=8))
    frags.append(text(485, 375, "Загроза підробки даних без контролю цілісності:", size=12, bold=True, color="#991b1b"))
    frags.append(text(485, 398, "Режим AES-XTS гарантує конфіденційність, але дозволяє зловмиснику маніпулювати бітами шифротексту.", size=11, color="#7f1d1d"))
    frags.append(text(485, 416, "Шар dm-integrity унеможливлює підміну виконавчого коду та структур файлової системи.", size=11, color="#7f1d1d"))

    render(os.path.join(IMG_DIR, "luks2-integrity-stack.svg"), w, h, *frags)


def main():
    fig_luks2_disk_layout()
    fig_luks2_keyslot_resolution()
    fig_luks2_dual_header_recovery()
    fig_luks2_integrity_stack()
    print("Усі 4 фігури успішно згенеровано.")


if __name__ == "__main__":
    main()
