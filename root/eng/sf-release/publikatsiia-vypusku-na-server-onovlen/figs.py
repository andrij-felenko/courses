# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Топологія системи публікації оновлень на OTA-сервер ─────────────
def fig_ota_publication_architecture():
    W, H = 1000, 560
    frags = []

    frags.append(text(500, 25, "Архітектура публікації випуску на сервер оновлень (OTA Control Plane)",
                      size=15, bold=True, color=INK))

    # Верхній лівий блок: CI/CD Конвеєр збірки
    cicd_bg = rect(40, 60, 280, 130, fill="#f8fafc", stroke=INK, sw=1.5, rx=8)
    frags.append(cicd_bg)
    frags.append(text(180, 85, "КОНВЕЄР ЗБІРКИ (CI/CD)", size=12, bold=True, color=INK))
    frags.append(text(180, 108, "• Генерація rootfs, бінарників, delta", size=10, color=INK))
    frags.append(text(180, 126, "• Обчислення хешів SHA-256/BLAKE3", size=10, color=INK))
    frags.append(text(180, 144, "• Формування чернетки маніфесту", size=10, color=INK))
    frags.append(text(180, 162, "• Передача на підпис у KMS/HSM", size=10, color=MUTED))

    # Верхній правий блок: Криптографічний модуль підпису (HSM / KMS)
    hsm_bg = rect(680, 60, 280, 130, fill="#fdf2f8", stroke="#be185d", sw=1.5, rx=8)
    frags.append(hsm_bg)
    frags.append(text(820, 85, "МОДУЛЬ ПІДПИСУ (HSM / KMS)", size=12, bold=True, color="#be185d"))
    frags.append(text(820, 108, "• Апаратне збереження приватного ключа", size=10, color=INK))
    frags.append(text(820, 126, "• Асиметричний підпис (Ed25519 / RSA-PSS)", size=10, color=INK))
    frags.append(text(820, 144, "• Захист від витоку ключів релізу", size=10, color=INK))
    frags.append(text(820, 162, "• Додавання відбитку відкритого ключа", size=10, color=MUTED))

    # Стрілки від CI/CD та HSM до Сервера оновлень
    frags.append(arrow(180, 190, 320, 230, color=INK, sw=1.8))
    frags.append(text(215, 205, "Завантаження артефактів", size=9, bold=True, color=INK))

    frags.append(arrow(820, 190, 680, 230, color="#be185d", sw=1.8))
    frags.append(text(785, 205, "Підписаний маніфест", size=9, bold=True, color="#be185d"))

    # Центральний блок: СЕРВЕР ОНОВЛЕНЬ (OTA Control Plane)
    server_bg = rect(260, 225, 480, 175, fill="#fffbf0", stroke="#d97706", sw=2.0, rx=8)
    frags.append(server_bg)
    frags.append(text(500, 250, "СЕРВЕР КЕРУВАННЯ ОНОВЛЕННЯМИ (OTA CONTROL PLANE)", size=13, bold=True, color="#b45309"))
    frags.append(text(500, 268, "(Eclipse hawkBit / Mender Server / AWS IoT OTA / RAUC Backend)", size=10, italic=True, color=MUTED))

    # Лінії та підкомпоненти сервера
    frags.append(line(275, 280, 725, 280, color="#d97706", sw=1.0))
    frags.append(text(340, 305, "Шлюз прийому", size=11, bold=True, color=INK))
    frags.append(text(340, 323, "валідація схеми JSON", size=9, color=MUTED))

    frags.append(line(420, 285, 420, 335, color="#d97706", sw=1.0))

    frags.append(text(500, 305, "Двигун перевірки", size=11, bold=True, color=INK))
    frags.append(text(500, 323, "підписи Ed25519 та хеші", size=9, color=MUTED))

    frags.append(line(580, 285, 580, 335, color="#d97706", sw=1.0))

    frags.append(text(655, 305, "Матриця заліза", size=11, bold=True, color=INK))
    frags.append(text(655, 323, "сумісність ревізій плат", size=9, color=MUTED))

    frags.append(line(275, 345, 725, 345, color="#d97706", sw=1.0))
    frags.append(text(500, 365, "Реєстр випусків • Автомат станів: Draft → Staged → Published", size=10, bold=True, color="#b45309"))
    frags.append(text(500, 385, "Гарантія незмінності: після публікації бінарники та маніфест заблоковані від змін", size=9, color=INK))

    # Нижній лівий блок: Об'єктне сховище та CDN
    storage_bg = rect(40, 430, 400, 110, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8)
    frags.append(storage_bg)
    frags.append(text(240, 455, "ОБ'ЄКТНЕ СХОВИЩЕ ТА CDN (S3 / CloudFront)", size=11, bold=True, color=NEG))
    frags.append(text(240, 477, "• Збереження бінарних блоків та образів rootfs", size=10, color=INK))
    frags.append(text(240, 495, "• Генерація підписаних тимчасових посилань (Presigned URLs)", size=10, color=INK))
    frags.append(text(240, 513, "• Розподілене кешування на крайових вузлах CDN", size=10, color=MUTED))

    # Нижній правий блок: Парк пристроїв
    fleet_bg = rect(560, 430, 400, 110, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8)
    frags.append(fleet_bg)
    frags.append(text(760, 455, "ПАРК ПРИСТРОЇВ (Edge Devices & IoT Fleet)", size=11, bold=True, color=FIELD))
    frags.append(text(760, 477, "• Агенти оновлення (RAUC, Mender-client, SWUpdate)", size=10, color=INK))
    frags.append(text(760, 495, "• Локальна верифікація відкритого ключа заліза", size=10, color=INK))
    frags.append(text(760, 513, "• Атомарне перемикання A/B слотів пам'яті", size=10, color=MUTED))

    # Зв'язки між сервером, сховищем та парком
    frags.append(arrow(380, 400, 240, 430, color=NEG, sw=1.8))
    frags.append(text(285, 415, "Реплікація артефактів", size=9, bold=True, color=NEG))

    frags.append(arrow(620, 400, 760, 430, color=FIELD, sw=1.8))
    frags.append(text(725, 415, "Кампанія доставки маніфесту", size=9, bold=True, color=FIELD))

    frags.append(line(440, 485, 560, 485, color=INK, sw=1.5, dash="4,3"))
    frags.append(text(500, 475, "Пряме завантаження payload", size=9, italic=True, color=INK))

    render(os.path.join(IMG, 'ota-publication-architecture.svg'), W, H, *frags,
           title="Архітектура публікації випуску на сервер оновлень")


# ── Фігура 2: Анатомія та структура релізного маніфесту ──────────────────────
def fig_release_manifest_structure():
    W, H = 1000, 540
    frags = []

    frags.append(text(500, 25, "Анатомія та криптографічні шари релізного маніфесту",
                      size=15, bold=True, color=INK))

    # 4 секції маніфесту
    col_w = 215
    start_x = 40
    gap = 25
    top_y = 65
    card_h = 440

    # Блок 1: Метадані випуску
    x1 = start_x
    frags.append(rect(x1, top_y, col_w, card_h, fill="#f8fafc", stroke=INK, sw=1.5, rx=8))
    frags.append(text(x1 + col_w/2, top_y + 30, "1. МЕТАДАНІ РЕЛІЗУ", size=12, bold=True, color=INK))
    frags.append(line(x1 + 10, top_y + 45, x1 + col_w - 10, top_y + 45, color=MUTED, sw=1.0))
    
    meta_items = [
        "release_id: UUIDv4",
        "name: Gateway Linux",
        "version: 3.4.0-prod",
        "build_id: 20260828.14",
        "created_at: ISO-8601",
        "security_epoch: 4",
        "urgency: mandatory",
        "reboot_required: true"
    ]
    for i, item in enumerate(meta_items):
        frags.append(text(x1 + 15, top_y + 75 + i * 28, item, size=10, anchor="start", color=INK))

    frags.append(text(x1 + col_w/2, top_y + 340, "Anti-Rollback захист:", size=10, bold=True, color=POS))
    frags.append(text(x1 + col_w/2, top_y + 360, "security_epoch гарантує,", size=9, color=INK))
    frags.append(text(x1 + col_w/2, top_y + 375, "що старі вразливі релізи", size=9, color=INK))
    frags.append(text(x1 + col_w/2, top_y + 390, "не можуть бути встановлені", size=9, color=INK))
    frags.append(text(x1 + col_w/2, top_y + 405, "поверх нового ПЗ.", size=9, color=INK))

    # Блок 2: Матриця сумісності заліза
    x2 = x1 + col_w + gap
    frags.append(rect(x2, top_y, col_w, card_h, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(x2 + col_w/2, top_y + 30, "2. СУМІСНІСТЬ ЗАЛІЗА", size=12, bold=True, color=FIELD))
    frags.append(line(x2 + 10, top_y + 45, x2 + col_w - 10, top_y + 45, color=FIELD, sw=1.0))

    hw_items = [
        "device_type: edge-gw",
        "board_family: imx8mp",
        "hw_revision_min: 2.0",
        "hw_revision_max: 2.9",
        "min_flash_size: 16 GB",
        "min_ram_size: 2 GB",
        "bootloader_min: 2024.04",
        "dtb_compatible: gw-v2"
    ]
    for i, item in enumerate(hw_items):
        frags.append(text(x2 + 15, top_y + 75 + i * 28, item, size=10, anchor="start", color=INK))

    frags.append(text(x2 + col_w/2, top_y + 340, "Gating сумісності:", size=10, bold=True, color=FIELD))
    frags.append(text(x2 + col_w/2, top_y + 360, "Захист від завантаження", size=9, color=INK))
    frags.append(text(x2 + col_w/2, top_y + 375, "образу на несумісні плати", size=9, color=INK))
    frags.append(text(x2 + col_w/2, top_y + 390, "(запобігання окрирпичуванню", size=9, color=INK))
    frags.append(text(x2 + col_w/2, top_y + 405, "через несумісний DTB).", size=9, color=INK))

    # Блок 3: Перелік артефактів та хеші
    x3 = x2 + col_w + gap
    frags.append(rect(x3, top_y, col_w, card_h, fill="#eff6ff", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(x3 + col_w/2, top_y + 30, "3. АРТЕФАКТИ ТА ХЕШІ", size=12, bold=True, color=NEG))
    frags.append(line(x3 + 10, top_y + 45, x3 + col_w - 10, top_y + 45, color=NEG, sw=1.0))

    art_items = [
        "name: rootfs.ext4",
        "type: raw-image",
        "target_slot: rootfs.B",
        "size_bytes: 440401920",
        "sha256: e3b0c442...",
        "blake3: 9f86d081...",
        "chunk_size: 4096 KB",
        "uri: s3://firmware/..."
    ]
    for i, item in enumerate(art_items):
        frags.append(text(x3 + 15, top_y + 75 + i * 28, item, size=10, anchor="start", color=INK))

    frags.append(text(x3 + col_w/2, top_y + 340, "Контроль цілісності:", size=10, bold=True, color=NEG))
    frags.append(text(x3 + col_w/2, top_y + 360, "Хеш перевіряється двічі:", size=9, color=INK))
    frags.append(text(x3 + col_w/2, top_y + 375, "1) сервером при публікації,", size=9, color=INK))
    frags.append(text(x3 + col_w/2, top_y + 390, "2) пристроєм під час запису", size=9, color=INK))
    frags.append(text(x3 + col_w/2, top_y + 405, "блоків у розділ пам'яті.", size=9, color=INK))

    # Блок 4: Цифровий підпис
    x4 = x3 + col_w + gap
    frags.append(rect(x4, top_y, col_w, card_h, fill="#fdf2f8", stroke="#be185d", sw=1.5, rx=8))
    frags.append(text(x4 + col_w/2, top_y + 30, "4. ЦИФРОВИЙ ПІДПИС", size=12, bold=True, color="#be185d"))
    frags.append(line(x4 + 10, top_y + 45, x4 + col_w - 10, top_y + 45, color="#be185d", sw=1.0))

    sig_items = [
        "algorithm: Ed25519",
        "key_id: key-prod-2026-v1",
        "key_type: public-key",
        "signature_format: raw",
        "sig_value: 7f8a91b...",
        "canonical_json: true",
        "expires_at: 2027-08-28",
        "timestamp_sig: valid"
    ]
    for i, item in enumerate(sig_items):
        frags.append(text(x4 + 15, top_y + 75 + i * 28, item, size=10, anchor="start", color=INK))

    frags.append(text(x4 + col_w/2, top_y + 340, "Криптографічний захист:", size=10, bold=True, color="#be185d"))
    frags.append(text(x4 + col_w/2, top_y + 360, "Підпис охоплює маніфест", size=9, color=INK))
    frags.append(text(x4 + col_w/2, top_y + 375, "разом з усіма хешами.", size=9, color=INK))
    frags.append(text(x4 + col_w/2, top_y + 390, "Підміна навіть одного біта", size=9, color=INK))
    frags.append(text(x4 + col_w/2, top_y + 405, "робить маніфест недійсним.", size=9, color=INK))

    render(os.path.join(IMG, 'release-manifest-structure.svg'), W, H, *frags,
           title="Анатомія та криптографічні шари релізного маніфесту")


# ── Фігура 3: Скінченний автомат станів публікації ────────────────────────────
def fig_publication_state_machine():
    W, H = 1000, 520
    frags = []

    frags.append(text(500, 25, "Скінченний автомат життєвого циклу публікації релізу на OTA-сервері",
                      size=15, bold=True, color=INK))

    # Стан 1: DRAFT
    b1, _, _ = textbox(130, 130, "1. DRAFT (Чернетка)\nІніціалізація випуску,\nзавантаження артефактів",
                       size=11, bold=True, fill="#f8fafc", stroke=INK, sw=1.5, pad=10)
    frags.append(b1)

    # Стан 2: VALIDATING
    b2, _, _ = textbox(400, 130, "2. VALIDATING (Перевірка)\nРозрахунок хешів, валідація\nEd25519, перевірка схеми",
                       size=11, bold=True, fill="#fff9e6", stroke="#d97706", sw=1.8, pad=10)
    frags.append(b2)

    # Стрілка 1 -> 2
    frags.append(arrow(220, 130, 305, 130, color=INK, sw=1.8))
    frags.append(text(262, 118, "Commit upload", size=9, color=INK))

    # Стан 2а: VALIDATION FAILED (Помилка)
    b2a, _, _ = textbox(400, 310, "ПОМИЛКА ВАЛІДАЦІЇ\n(Validation Failed)\nНевідповідність хешу,\nнедійсний підпис, битий DTB",
                        size=11, bold=True, fill="#fee2e2", stroke=POS, sw=1.8, pad=10)
    frags.append(b2a)

    # Стрілка 2 -> 2а
    frags.append(arrow(400, 180, 400, 260, color=POS, sw=1.8))
    frags.append(text(465, 215, "Збій перевірки", size=9, bold=True, color=POS))

    # Стан 2а -> Aborted / Quarantined
    b_abort, _, _ = textbox(130, 310, "КАРАНТИН / АНУЛЬОВАНО\n(Quarantined / Rejected)\nАртефакти блокуються,\nвипуск відхилено",
                            size=10, bold=False, fill="#ffffff", stroke=POS, sw=1.2, pad=8)
    frags.append(b_abort)
    frags.append(arrow(300, 310, 215, 310, color=POS, sw=1.5))
    frags.append(text(255, 298, "Ізоляція", size=9, color=POS))

    # Стан 3: STAGED
    b3, _, _ = textbox(690, 130, "3. STAGED (Випробування)\nДоступно ТІЛЬКИ для стендів\nі внутрішньої канарки (QA)",
                       size=11, bold=True, fill="#eff6ff", stroke=NEG, sw=1.8, pad=10)
    frags.append(b3)

    # Стрілка 2 -> 3
    frags.append(arrow(495, 130, 585, 130, color=FIELD, sw=1.8))
    frags.append(text(540, 118, "Усі перевірки OK", size=9, bold=True, color=FIELD))

    # Стан 4: PUBLISHED / ACTIVE
    b4, _, _ = textbox(690, 310, "4. PUBLISHED (Опубліковано)\nВипуск закріплено (Immutable).\nДоступний для бойових кампаній",
                       size=11, bold=True, fill="#f0fdf4", stroke=FIELD, sw=2.0, pad=10)
    frags.append(b4)

    # Стрілка 3 -> 4
    frags.append(arrow(690, 180, 690, 260, color=FIELD, sw=2.0))
    frags.append(text(760, 215, "Апрув релізу (Sign-off)", size=9, bold=True, color=FIELD))

    # Стан 5: DEPRECATED / REVOKED
    b5, _, _ = textbox(690, 450, "5. DEPRECATED / REVOKED (Відкликано)\nЗамінено новою версією або анульовано\nчерез критичну вразливість 0-day",
                       size=10, bold=False, fill="#f8fafc", stroke=MUTED, sw=1.5, pad=8)
    frags.append(b5)

    # Стрілка 4 -> 5
    frags.append(arrow(690, 360, 690, 420, color=MUTED, sw=1.5))
    frags.append(text(760, 390, "Вихід нового релізу", size=9, color=MUTED))

    # Блок правил інваріантів знизу ліворуч
    inv_box, _, _ = textbox(300, 450, "ІНВАРІАНТ НЕЗМІННОСТІ (IMMUTABILITY):\nОпублікований реліз заборонено модифікувати або перезаписувати.\nБудь-яке виправлення дефекту вимагає створення нового релізу з інкрементом SemVer.",
                            size=10, bold=True, fill="#fefce8", stroke="#ca8a04", sw=1.2, pad=10)
    frags.append(inv_box)

    render(os.path.join(IMG, 'publication-state-machine.svg'), W, H, *frags,
           title="Скінченний автомат станів публікації випуску")


# ── Фігура 4: Конвеєр передрелізної перевірки (Pre-flight Validation) ────────
def fig_pre_flight_verification_pipeline():
    W, H = 1000, 520
    frags = []

    frags.append(text(500, 25, "Конвеєр автоматизованої передрелізної верифікації (Pre-flight Checks)",
                      size=15, bold=True, color=INK))

    # 4 етапи перевірки в лінію зверху вниз
    steps = [
        ("Етап 1: Валідація схеми та синтаксису",
         "Перевірка JSON Schema / Proto маніфесту: валідність обов'язкових полів, формат SemVer, UUID, типи артефактів",
         "#f8fafc", INK),
        ("Етап 2: Верифікація криптографічного підпису",
         "Перевірка підпису Ed25519/RSA-PSS публічним ключем довіреного ланцюга. Перевірка терміну дії ключів (Not After)",
         "#fdf2f8", "#be185d"),
        ("Етап 3: Обчислення та звірка хешів артефактів",
         "Потокове зчитування файлів з об'єктного сховища: перевірка SHA-256 та BLAKE3 проти значень у маніфесті",
         "#eff6ff", NEG),
        ("Етап 4: Аудит сумісності з парком пристроїв",
         "Звірка з Device Registry: перевірка наявності цільових моделей заліза, ревізій плат та версій завантажувача",
         "#f0fdf4", FIELD),
    ]

    top_y = 65
    step_h = 75
    gap_y = 25

    for i, (title, desc, fill_c, stroke_c) in enumerate(steps):
        sy = top_y + i * (step_h + gap_y)
        frags.append(rect(60, sy, 880, step_h, fill=fill_c, stroke=stroke_c, sw=1.5, rx=8))
        frags.append(text(100, sy + 25, str(i + 1), size=14, bold=True, color=stroke_c))
        frags.append(circle(100, sy + 21, 14, fill="#ffffff", stroke=stroke_c, sw=1.5))
        frags.append(text(130, sy + 26, title, size=12, bold=True, anchor="start", color=stroke_c))
        frags.append(text(130, sy + 52, desc, size=10, anchor="start", color=INK))

        # Стрілка переходу до наступного кроку
        if i < len(steps) - 1:
            frags.append(arrow(500, sy + step_h, 500, sy + step_h + gap_y, color=stroke_c, sw=1.8))

    # Нижній блок підсумку
    res_box, _, _ = textbox(500, 480, "Результат: Якщо ВСІ 4 етапи пройдено успішно → статус релізу переводиться у 'Approved/Published'.\nУ разі хоча б однієї помилки → публікація атомарно блокується з генерацією діагностичного звіту.",
                            size=10, bold=True, fill="#fefce8", stroke="#ca8a04", sw=1.2, pad=8)
    frags.append(res_box)

    render(os.path.join(IMG, 'pre-flight-verification-pipeline.svg'), W, H, *frags,
           title="Конвеєр передрелізної перевірки артефактів")


if __name__ == '__main__':
    fig_ota_publication_architecture()
    fig_release_manifest_structure()
    fig_publication_state_machine()
    fig_pre_flight_verification_pipeline()
    print("All figures generated successfully.")
