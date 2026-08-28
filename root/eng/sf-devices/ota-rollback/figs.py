# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── ab-partition-state-machine: Машина станів A/B розділів та відкату ────────
def fig_ab_partition_state_machine():
    W, H = 880, 520
    p = []

    # Заголовок блоків станів
    # Стан 1: EMPTY / INVALID
    b_empty, w_emp, h_emp = textbox(160, 110, "INVALID / EMPTY\nСлот не містить\nвалідної прошивки",
                                    size=12, pad=12, fill="#fef2f2", stroke=POS, sw=1.8, color=POS, bold=True, min_w=190)
    p.append(b_empty)

    # Стан 2: PENDING_VERIFY (Кандидат на випробуванні)
    b_pending, w_pend, h_pend = textbox(440, 110, "PENDING_VERIFY\nПробний запуск образу\n(boot_count < max_retries)",
                                        size=12, pad=12, fill="#fef9c3", stroke="#ca8a04", sw=2.0, color="#854d0e", bold=True, min_w=220)
    p.append(b_pending)

    # Стан 3: VALID / ACTIVE (Підтверджений робочий)
    b_valid, w_val, h_val = textbox(720, 110, "VALID / SUCCESS\nПідтверджений образ\n(self-test пройдено)",
                                    size=12, pad=12, fill="#ecfdf5", stroke=FIELD, sw=2.2, color=FIELD, bold=True, min_w=190)
    p.append(b_valid)

    # Стан 4: MARKED_BAD / ROLLBACK (Відкинутий, відкат)
    b_bad, w_bad, h_bad = textbox(440, 360, "MARKED_BAD / ROLLBACK\nСлот визнано збійним\nВідкат на робочий слот",
                                  size=12, pad=12, fill="#fef2f2", stroke=POS, sw=2.2, color=POS, bold=True, min_w=220)
    p.append(b_bad)

    # Переходи (стрілки та підписи)
    # 1 -> 2: Запис OTA та перевірка сигнатури
    p.append(arrow(160 + w_emp/2, 110, 440 - w_pend/2, 110, color=LINE, sw=1.8))
    p.append(text(300, 92, "1. Запис образу + SHA-256/ECDSA", size=10.5, color=INK, bold=True))

    # 2 -> 3: Підтвердження від застосунку
    p.append(arrow(440 + w_pend/2, 110, 720 - w_val/2, 110, color=FIELD, sw=2.0))
    p.append(text(580, 92, "2. ota_mark_valid()", size=10.5, color=FIELD, bold=True))

    # 2 -> 4: Збій (WDT reset / HardFault / boot_count > max)
    p.append(arrow(440, 110 + h_pend/2, 440, 360 - h_bad/2, color=POS, sw=2.2))
    p.append(text(448, 235, "3. Збій / WDT / паніка", size=10.5, color=POS, bold=True, anchor="start"))
    p.append(text(448, 252, "(boot_count >= max)", size=9.5, color=MUTED, anchor="start"))

    # 4 -> 3: Повернення керування на старий робочий слот
    p.append(arrow(440 + w_bad/2, 360, 720, 110 + h_val/2, color=NEG, sw=2.0))
    p.append(text(650, 270, "4. Активація слота B/A", size=10.5, color=NEG, bold=True))

    # 4 -> 1: Перезапис під час наступного OTA
    p.append(arrow(440 - w_bad/2, 360, 160, 110 + h_emp/2, color=MUTED, sw=1.6))
    p.append(text(240, 270, "Нове оновлення", size=10, color=MUTED, bold=True))

    # Нижній пояснювальний блок
    p.append(rect(60, 435, W - 120, 65, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(W / 2, 458,
                  "Ключовий інваріант: завантажувач перемикає активний слот у PENDING_VERIFY лише після валідації підпису.",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, 478,
                  "Якщо нова прошивка падає або не скидає watchdog, boot_count перевищує ліміт і спричиняє негайний відкат.",
                  size=10.5, color=MUTED))

    render(os.path.join(OUT, "ab-partition-state-machine.svg"), W, H, *p,
           title="Машина станів A/B розділів та відкату")


# ── ota-firmware-verification-pipeline: Конвеєр верифікації прошивки ─────────
def fig_ota_firmware_verification_pipeline():
    W, H = 900, 480
    p = []

    steps = [
        ("1. Мережевий потік", "TLS Socket / Chunks\nПеревірка розміру\nБуферизація блоків", "#e0e7ff", NEG),
        ("2. Запис у Flash", "Стирання секторів\nCRC32 сторінок\nЦілісність XIP-банку", "#f1f5f9", LINE),
        ("3. Хеш і підпис", "MCUboot Header\nSHA-256 Digest\nECDSA P-256 / RSA", "#fef3c7", "#b45309"),
        ("4. Anti-Rollback", "Security Counter\neFuse / OTP перевірка\nЗахист від downgrade", "#fee2e2", POS),
        ("5. Атомарний стан", "otadata / NVRAM\nSequence + CRC32\nСтан PENDING_VERIFY", "#dcfce7", FIELD)
    ]

    bx, by, bw, bh, gap = 40, 90, 150, 110, 25
    for i, (title, desc, fill_c, stroke_c) in enumerate(steps):
        x = bx + i * (bw + gap)
        p.append(rect(x, by, bw, bh, fill=fill_c, stroke=stroke_c, sw=1.8, rx=8))
        p.append(text(x + bw / 2, by + 24, title, size=11, color=stroke_c, bold=True))
        p.append(mtext(x + bw / 2, by + 50, desc, size=9.5, color=INK, lh=1.35))

        if i < len(steps) - 1:
            p.append(arrow(x + bw + 2, by + bh / 2, x + bw + gap - 4, by + bh / 2, color=LINE, sw=1.8))

    # Нижній рівень: Дії завантажувача після перезавантаження
    y2 = 250
    p.append(rect(40, y2, W - 80, 140, fill="#ffffff", stroke=MUTED, sw=1.5, rx=10))
    p.append(text(60, y2 + 26, "Етап виконання: Bootloader -> Kernel -> Self-Test -> Confirmation",
                  size=12, color=INK, bold=True, anchor="start"))

    # Підблоки в етапі виконання
    sub_w = 230
    # Підблок 1
    p.append(rect(60, y2 + 42, sub_w, 75, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(60 + sub_w/2, y2 + 62, "Завантажувач (Bootloader)", size=10.5, color=NEG, bold=True))
    p.append(mtext(60 + sub_w/2, y2 + 82, "Інкремент boot_count\nЗапуск Boot Watchdog (30с)\nСтрибок на Entry Point", size=9, color=INK))

    p.append(arrow(60 + sub_w + 5, y2 + 78, 60 + sub_w + 35, y2 + 78, color=LINE, sw=1.6))

    # Підблок 2
    p.append(rect(330, y2 + 42, sub_w, 75, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(330 + sub_w/2, y2 + 62, "Застосунок (Application)", size=10.5, color="#b45309", bold=True))
    p.append(mtext(330 + sub_w/2, y2 + 82, "Апаратний POST / BIST\nІніціалізація радіо/датчиків\nЗв'язок із хмарою (MQTT)", size=9, color=INK))

    p.append(arrow(330 + sub_w + 5, y2 + 78, 330 + sub_w + 35, y2 + 78, color=LINE, sw=1.6))

    # Підблок 3
    p.append(rect(600, y2 + 42, sub_w, 75, fill="#ecfdf5", stroke=FIELD, sw=1.6, rx=6))
    p.append(text(600 + sub_w/2, y2 + 62, "Фіксація (Commit)", size=10.5, color=FIELD, bold=True))
    p.append(mtext(600 + sub_w/2, y2 + 82, "ota_mark_valid()\nСкидання boot_count = 0\notadata -> VALID / SUCCESS", size=9, color=FIELD))

    # Рамка підсумку
    p.append(fitbox(40, 410, W - 80, 50,
                    "Повна лінія захисту: помилка на будь-якому кроці до ota_mark_valid() повертає пристрій на робочий слот.",
                    size=11, fill="#f8fafc", stroke=MUTED, sw=1.2, bold=True))

    render(os.path.join(OUT, "ota-firmware-verification-pipeline.svg"), W, H, *p,
           title="Конвеєр верифікації та валідації прошивки OTA")


if __name__ == "__main__":
    fig_ab_partition_state_machine()
    fig_ota_firmware_verification_pipeline()
    print("OK: figures generated in", OUT)
