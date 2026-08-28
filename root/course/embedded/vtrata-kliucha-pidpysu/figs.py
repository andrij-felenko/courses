# -*- coding: utf-8 -*-
"""Фігури для статті vtrata-kliucha-pidpysu («Втрата ключа підпису»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. hardware-boot-lock: Кремнієвий замок апаратної верифікації ───────────
def fig_hardware_boot_lock():
    W, H = 820, 400
    p = []

    # Заголовок та фон панелей
    p.append(rect(20, 20, 780, 360, fill="#fafafc", stroke=MUTED, sw=1.2, rx=8))

    # Ліва частина: Flash пам'ять з образом прошивки
    p.append(rect(40, 50, 220, 300, fill="#ffffff", stroke=INK, sw=1.5, rx=4))
    b, _, _ = textbox(150, 75, "Flash: образ оновлення", size=13, color=INK, bold=True)
    p.append(b)

    # Розділи всередині образу Flash
    p.append(rect(55, 105, 190, 45, fill="#edf2f7", stroke=MUTED, sw=1.0, rx=3))
    p.append(text(150, 132, "Відкритий ключ (PK)", size=11, color=INK, bold=True, anchor="middle"))

    p.append(rect(55, 160, 190, 45, fill="#edf2f7", stroke=MUTED, sw=1.0, rx=3))
    p.append(text(150, 187, "Цифровий підпис (Sign)", size=11, color=INK, bold=True, anchor="middle"))

    p.append(rect(55, 215, 190, 115, fill="#edf2f7", stroke=MUTED, sw=1.0, rx=3))
    p.append(text(150, 260, "Тіло прошивки", size=12, color=INK, bold=True, anchor="middle"))
    p.append(text(150, 285, "(код застосунку / OS)", size=10, color=MUTED, italic=True, anchor="middle"))

    # Центральна частина: Апаратний кремній MCU (ROM + eFuse)
    p.append(rect(300, 50, 250, 300, fill="#f0f4f8", stroke="#2b6cb0", sw=1.8, rx=6))
    p.append(text(425, 75, "Кремній MCU (Secure Boot)", size=13, color="#2b6cb0", bold=True, anchor="middle"))

    # Апаратний SHA-256 блок
    p.append(rect(320, 105, 210, 45, fill="#ffffff", stroke="#2b6cb0", sw=1.2, rx=4))
    p.append(text(425, 132, "Апаратний SHA-256", size=11, color="#2b6cb0", bold=True, anchor="middle"))

    # eFuse OTP сховище
    p.append(rect(320, 165, 210, 50, fill="#fff5f5", stroke=NEG, sw=1.4, rx=4))
    p.append(text(425, 186, "eFuse OTP (незмінно)", size=11, color=NEG, bold=True, anchor="middle"))
    p.append(text(425, 204, "SHA-256(PK_root) еталон", size=10, color=INK, anchor="middle"))

    # Компаратор
    p.append(rect(345, 245, 160, 45, fill="#ffffff", stroke=INK, sw=1.4, rx=4))
    p.append(text(425, 273, "Апаратний компаратор", size=11, color=INK, bold=True, anchor="middle"))

    # Зв'язки між Flash та MCU
    p.append(arrow(245, 128, 320, 128, color="#2b6cb0", sw=1.5))
    p.append(arrow(425, 150, 425, 165, color="#2b6cb0", sw=1.2))
    p.append(arrow(425, 215, 425, 245, color=NEG, sw=1.5))

    # Права частина: Результат верифікації
    # Успіх (старий ключ)
    p.append(rect(590, 80, 190, 80, fill="#f0fff4", stroke=POS, sw=1.5, rx=6))
    p.append(text(685, 112, "Хеш збігся: ПІДТВЕРДЖЕНО", size=11, color=POS, bold=True, anchor="middle"))
    p.append(text(685, 137, "Запуск виконання прошивки", size=10, color=INK, anchor="middle"))

    # Катастрофа (новий ключ без старого)
    p.append(rect(590, 220, 190, 110, fill="#fff5f5", stroke=NEG, sw=1.6, rx=6))
    p.append(text(685, 250, "Невідповідність хешу!", size=12, color=NEG, bold=True, anchor="middle"))
    p.append(text(685, 277, "Ключ відкинуто залізом.", size=10, color=INK, bold=True, anchor="middle"))
    p.append(text(685, 302, "Парк заблоковано назавжди", size=10, color=NEG, italic=True, anchor="middle"))

    # Стрілки від компаратора до результатів
    p.append(arrow(505, 255, 590, 130, color=POS, sw=1.5))
    p.append(text(535, 175, "Збіг", size=10, color=POS, bold=True))

    p.append(arrow(505, 275, 590, 275, color=NEG, sw=1.8))
    p.append(text(525, 295, "Розбіжність", size=10, color=NEG, bold=True))

    render(os.path.join(OUT, "hardware-boot-lock.svg"), W, H, *p)


# ── 2. multi-slot-rot: Багатослотовий корінь довіри з бітами відкликання ─────
def fig_multi_slot_rot():
    W, H = 820, 380
    p = []

    p.append(rect(20, 20, 780, 340, fill="#fafafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(410, 50, "Багатослотовий корінь довіри (Multi-Slot Root of Trust) в eFuse", size=14, color=INK, bold=True, anchor="middle"))

    # Таблиця 4 слотів ключів
    slots = [
        ("Слот 0 (SRK0)", "Хеш ключа A (SHA-256)", "СПАЛЕНО (REVOKED = 1)", "#fff5f5", NEG, "Втрачено / скомпрометовано"),
        ("Слот 1 (SRK1)", "Хеш ключа B (SHA-256)", "АКТИВНИЙ (REVOKED = 0)", "#f0fff4", POS, "Чинний робочий ключ"),
        ("Слот 2 (SRK2)", "Хеш ключа C (SHA-256)", "РЕЗЕРВ (REVOKED = 0)", "#ffffff", "#2b6cb0", "Холодний сейф №1 (кворум)"),
        ("Слот 3 (SRK3)", "Хеш ключа D (SHA-256)", "РЕЗЕРВ (REVOKED = 0)", "#ffffff", "#2b6cb0", "Холодний сейф №2 (кворум)"),
    ]

    sy = 80
    for i, (name, digest, status, bg, status_col, note) in enumerate(slots):
        y = sy + i * 65
        # Рядок слота
        p.append(rect(45, y, 730, 55, fill=bg, stroke=MUTED, sw=1.0, rx=4))

        # Назва слота
        p.append(text(65, y + 34, name, size=12, color=INK, bold=True))

        # Хеш
        p.append(rect(205, y + 10, 210, 35, fill="#edf2f7", stroke=MUTED, sw=0.8, rx=3))
        p.append(text(310, y + 32, digest, size=10, color=INK, anchor="middle"))

        # Статус eFuse біта
        p.append(rect(430, y + 10, 185, 35, fill="#ffffff", stroke=status_col, sw=1.2, rx=3))
        p.append(text(522, y + 32, status, size=10, color=status_col, bold=True, anchor="middle"))

        # Примітка
        p.append(text(630, y + 34, note, size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "multi-slot-rot.svg"), W, H, *p)


# ── 3. pki-trust-chain: Трирівнева ієрархія сертифікатів (PKI) ───────────────
def fig_pki_trust_chain():
    W, H = 840, 380
    p = []

    p.append(rect(20, 20, 800, 340, fill="#fafafc", stroke=MUTED, sw=1.2, rx=8))

    # Рівень 1: Кореневий CA (Root)
    p.append(rect(40, 60, 220, 260, fill="#fffaf0", stroke="#d69e2e", sw=1.6, rx=6))
    p.append(text(150, 90, "Кореневий CA (Root)", size=13, color="#b7791f", bold=True, anchor="middle"))
    p.append(rect(55, 115, 190, 50, fill="#ffffff", stroke="#d69e2e", sw=1.0, rx=3))
    p.append(text(150, 138, "Root Private Key", size=11, color=NEG, bold=True, anchor="middle"))
    p.append(text(150, 155, "Офлайн HSM / Сейф (Шамір)", size=9, color=MUTED, italic=True, anchor="middle"))

    p.append(rect(55, 180, 190, 55, fill="#ffffff", stroke=MUTED, sw=1.0, rx=3))
    p.append(text(150, 203, "Root Certificate (X.509)", size=10, color=INK, bold=True, anchor="middle"))
    p.append(text(150, 223, "Хеш зашитий в eFuse", size=9, color=POS, bold=True, anchor="middle"))

    p.append(text(150, 290, "Термін дії: 15–20 років", size=10, color=MUTED, italic=True, anchor="middle"))

    # Рівень 2: Проміжний CA (Intermediate)
    p.append(rect(310, 60, 230, 260, fill="#ebf8ff", stroke="#3182ce", sw=1.6, rx=6))
    p.append(text(425, 90, "Проміжний CA (Sub-CA)", size=13, color="#2b6cb0", bold=True, anchor="middle"))
    p.append(rect(325, 115, 200, 50, fill="#ffffff", stroke="#3182ce", sw=1.0, rx=3))
    p.append(text(425, 138, "Intermediate Key", size=11, color=INK, bold=True, anchor="middle"))
    p.append(text(425, 155, "Захищене внутрішнє сховище", size=9, color=MUTED, italic=True, anchor="middle"))

    p.append(rect(325, 180, 200, 55, fill="#ffffff", stroke=MUTED, sw=1.0, rx=3))
    p.append(text(425, 203, "Intermediate Cert", size=10, color=INK, bold=True, anchor="middle"))
    p.append(text(425, 223, "Підписаний Root CA", size=9, color="#2b6cb0", bold=True, anchor="middle"))

    p.append(text(425, 290, "Ротація: кожні 2–3 роки", size=10, color=MUTED, italic=True, anchor="middle"))

    # Рівень 3: Ключ випуску збірки (Release Signer)
    p.append(rect(590, 60, 210, 260, fill="#f0fff4", stroke=POS, sw=1.6, rx=6))
    p.append(text(695, 90, "Релізний ключ (CI/CD)", size=13, color=POS, bold=True, anchor="middle"))
    p.append(rect(605, 115, 180, 50, fill="#ffffff", stroke=POS, sw=1.0, rx=3))
    p.append(text(695, 138, "Release Signing Key", size=11, color=INK, bold=True, anchor="middle"))
    p.append(text(695, 155, "Мережевий HSM / Build CI", size=9, color=MUTED, italic=True, anchor="middle"))

    p.append(rect(605, 180, 180, 55, fill="#ffffff", stroke=MUTED, sw=1.0, rx=3))
    p.append(text(695, 203, "Release Certificate", size=10, color=INK, bold=True, anchor="middle"))
    p.append(text(695, 223, "Підписаний Sub-CA", size=9, color=POS, bold=True, anchor="middle"))

    p.append(text(695, 290, "Ротація: кожні 6–12 місяців", size=10, color=MUTED, italic=True, anchor="middle"))

    # Стрілки делегування підпису
    p.append(arrow(260, 140, 310, 140, color="#d69e2e", sw=1.8))
    p.append(text(285, 130, "видає", size=9, color="#b7791f", bold=True, anchor="middle"))

    p.append(arrow(540, 140, 590, 140, color="#3182ce", sw=1.8))
    p.append(text(565, 130, "видає", size=9, color="#2b6cb0", bold=True, anchor="middle"))

    render(os.path.join(OUT, "pki-trust-chain.svg"), W, H, *p)


# ── 4. bridge-firmware-flow: Схема міграції через перехідну прошивку ─────────
def fig_bridge_firmware_flow():
    W, H = 840, 380
    p = []

    p.append(rect(20, 20, 800, 340, fill="#fafafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(420, 50, "Чотири фази міграції парку через перехідну прошивку (Bridge Firmware)", size=13, color=INK, bold=True, anchor="middle"))

    steps = [
        ("Фаза 1: Старий парк", "Підпис: Ключ A", "Довіра в ROM: Ключ A", "Нормальна робота парку", "#ffffff", INK),
        ("Фаза 2: Місток (Bridge)", "Підпис: Ключ A", "Містить: Публічний Ключ B", "Встановлює Bootloader v2", "#fffaf0", "#b7791f"),
        ("Фаза 3: Перемикання", "Оновлення Flash", "Запис Key B у сховище", "Активація нового довіреного кореня", "#ebf8ff", "#2b6cb0"),
        ("Фаза 4: Новий стан", "Підпис: Ключ B", "Довіра: Ключ B", "Ключ A виведено з обігу", "#f0fff4", POS),
    ]

    bx = 40
    bw = 175
    gap = 20

    for i, (title, l1, l2, l3, bg, border_col) in enumerate(steps):
        x = bx + i * (bw + gap)
        y = 80
        p.append(rect(x, y, bw, 240, fill=bg, stroke=border_col, sw=1.5, rx=6))

        p.append(text(x + bw / 2, y + 30, title, size=11, color=border_col, bold=True, anchor="middle"))

        p.append(rect(x + 10, y + 55, bw - 20, 45, fill="#edf2f7", stroke=MUTED, sw=0.8, rx=3))
        p.append(text(x + bw / 2, y + 82, l1, size=10, color=INK, bold=True, anchor="middle"))

        p.append(rect(x + 10, y + 115, bw - 20, 45, fill="#edf2f7", stroke=MUTED, sw=0.8, rx=3))
        p.append(text(x + bw / 2, y + 142, l2, size=9, color=INK, anchor="middle"))

        p.append(rect(x + 10, y + 175, bw - 20, 50, fill="#ffffff", stroke=border_col, sw=1.0, rx=3))
        p.append(text(x + bw / 2, y + 204, l3, size=9, color=border_col, bold=True, anchor="middle"))

        if i < 3:
            p.append(arrow(x + bw + 2, y + 120, x + bw + gap - 2, y + 120, color=INK, sw=1.6))

    render(os.path.join(OUT, "bridge-firmware-flow.svg"), W, H, *p)


if __name__ == "__main__":
    fig_hardware_boot_lock()
    fig_multi_slot_rot()
    fig_pki_trust_chain()
    fig_bridge_firmware_flow()
    print("Фігури успішно згенеровано у ./img/")
