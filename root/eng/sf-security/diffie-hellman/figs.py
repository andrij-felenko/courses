# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра
C_ALICE = "#2563eb"   # Синій — сторона Аліси
C_ALICEF = "#eff6ff"
C_BOB   = "#059669"   # Зелений — сторона Боба
C_BOBF  = "#ecfdf5"
C_PUB   = "#4b5563"   # Сірий — відкритий канал / публічні дані
C_PUBF  = "#f3f4f6"
C_WARN  = "#d97706"   # Помаранчевий — атака / вразливість
C_WARNF = "#fef3c7"
C_DANGER= "#dc2626"   # Червоний — компрометація / MITM
C_DANGERF="#fee2e2"
C_SEC   = "#7c3aed"   # Фіолетовий — спільний секрет / криптографія
C_SECF  = "#f5f3ff"


# ── 1. dh-key-exchange-flow: Протокол узгодження ключів Діффі — Геллмана ──
def fig_dh_flow():
    W, H = 1000, 520
    p = []

    # Заголовок
    p.append(text(W / 2, 28, "Протокол узгодження ключів Діффі — Геллмана (MODP)", size=16, color=INK, bold=True))

    # Три колони: Аліса (ліворуч), Відкритий канал (центр), Боб (праворуч)
    col_w = 260
    ax, cx, bx = 160, 500, 840

    # Фонори колонок
    p.append(rect(ax - col_w/2, 50, col_w, 450, fill=C_ALICEF, stroke=C_ALICE, sw=1.5, rx=8))
    p.append(rect(cx - col_w/2, 50, col_w, 450, fill=C_PUBF, stroke=C_PUB, sw=1.2, rx=8))
    p.append(rect(bx - col_w/2, 50, col_w, 450, fill=C_BOBF, stroke=C_BOB, sw=1.5, rx=8))

    # Заголовки сторін
    p.append(text(ax, 75, "Аліса (Клієнт)", size=14, color=C_ALICE, bold=True))
    p.append(text(cx, 75, "Відкритий канал (Єва бачить усе)", size=13, color=C_PUB, bold=True))
    p.append(text(bx, 75, "Боб (Сервер)", size=14, color=C_BOB, bold=True))

    # Етап 1: Спільні параметри
    p.append(fitbox(cx - 110, 95, 220, 50, "Публічні параметри:\nмодуль p, генератор g", size=12, fill="#ffffff", stroke=C_PUB, sw=1.2))

    # Етап 2: Генерація приватних секретів
    p.append(fitbox(ax - 115, 160, 230, 60, "Випадковий секрет a ∈ {2..p-2}\nОбчислення:\nA = g^a mod p", size=12, fill="#ffffff", stroke=C_ALICE, sw=1.5))
    p.append(fitbox(bx - 115, 160, 230, 60, "Випадковий секрет b ∈ {2..p-2}\nОбчислення:\nB = g^b mod p", size=12, fill="#ffffff", stroke=C_BOB, sw=1.5))

    # Етап 3: Обмін публічними ключами через відкритий канал
    # Стрілка Аліса -> Боб (передає A)
    p.append(arrow(ax + 115, 245, bx - 115, 245, color=C_ALICE, sw=2))
    p.append(fitbox(cx - 90, 225, 180, 38, "Відкритий ключ A = g^a mod p", size=11, fill="#ffffff", stroke=C_ALICE, sw=1.2))

    # Стрілка Боб -> Аліса (передає B)
    p.append(arrow(bx - 115, 295, ax + 115, 295, color=C_BOB, sw=2))
    p.append(fitbox(cx - 90, 275, 180, 38, "Відкритий ключ B = g^b mod p", size=11, fill="#ffffff", stroke=C_BOB, sw=1.2))

    # Етап 4: Перехоплювач (Єва)
    p.append(fitbox(cx - 115, 335, 230, 65, "Перехоплювач знає:\np, g, A, B\nЗнайти a чи b — задача DLP\n(обчислювально нездійсненна)", size=11, fill=C_WARNF, stroke=C_WARN, sw=1.5))

    # Етап 5: Обчислення спільного секрету
    p.append(fitbox(ax - 115, 415, 230, 70, "Спільний секрет K:\nK = B^a mod p\nK = (g^b)^a = g^(ab) mod p", size=12, fill=C_SECF, stroke=C_SEC, sw=2))
    p.append(fitbox(bx - 115, 415, 230, 70, "Спільний секрет K:\nK = A^b mod p\nK = (g^a)^b = g^(ab) mod p", size=12, fill=C_SECF, stroke=C_SEC, sw=2))

    render(os.path.join(OUT, "dh-key-exchange-flow.svg"), W, H, *p)


# ── 2. mitm-attack-and-pfs: Атака MITM та захист ефемерним DHE ──
def fig_mitm_and_pfs():
    W, H = 1000, 520
    p = []

    p.append(text(W / 2, 28, "Атака «людина посередині» (MITM) та захист через PFS", size=16, color=INK, bold=True))

    # Ліва панель: Неавтентифікований DH (MITM перехоплення)
    panel_w = 460
    p.append(rect(25, 50, panel_w, 450, fill="#ffffff", stroke=C_DANGER, sw=1.5, rx=8))
    p.append(text(25 + panel_w/2, 75, "Неавтентифікований DH: атака Меллорі", size=14, color=C_DANGER, bold=True))

    # Alice -> Mallory -> Bob
    p.append(fitbox(45, 100, 120, 50, "Аліса\nсекрет a", size=11, fill=C_ALICEF, stroke=C_ALICE, sw=1.2))
    p.append(fitbox(195, 100, 120, 50, "Меллорі (MITM)\nсекрети m1, m2", size=11, fill=C_DANGERF, stroke=C_DANGER, sw=1.5))
    p.append(fitbox(345, 100, 120, 50, "Боб\nсекрет b", size=11, fill=C_BOBF, stroke=C_BOB, sw=1.2))

    p.append(arrow(105, 160, 195, 190, color=C_ALICE, sw=1.5))
    p.append(text(140, 170, "A=g^a", size=10, color=C_ALICE))

    p.append(arrow(315, 190, 405, 160, color=C_DANGER, sw=1.5))
    p.append(text(370, 170, "M_A=g^m2", size=10, color=C_DANGER))

    p.append(arrow(405, 230, 315, 260, color=C_BOB, sw=1.5))
    p.append(text(370, 250, "B=g^b", size=10, color=C_BOB))

    p.append(arrow(195, 260, 105, 230, color=C_DANGER, sw=1.5))
    p.append(text(140, 250, "M_B=g^m1", size=10, color=C_DANGER))

    p.append(fitbox(45, 290, 185, 75, "Канал 1 (Аліса <-> Меллорі):\nK1 = (M_B)^a = g^(a·m1)\nМеллорі читає і підміняє!", size=11, fill=C_DANGERF, stroke=C_DANGER, sw=1.2))
    p.append(fitbox(280, 290, 185, 75, "Канал 2 (Меллорі <-> Боб):\nK2 = (M_A)^b = g^(b·m2)\nБоб упевнений, що це Аліса", size=11, fill=C_DANGERF, stroke=C_DANGER, sw=1.2))

    p.append(fitbox(45, 385, 420, 95, "Чому MITM можливий:\nDH гарантує конфіденційність, але НЕ автентифікацію.\nБез підтвердження особи відкриті ключі можна непомітно підмінити.\nРішення: цифровий підпис параметрів обміну (RSA / Ed25519 сертифікати).", size=11, fill=C_WARNF, stroke=C_WARN, sw=1.2))

    # Права панель: Ефемерний DH + Підпис (PFS)
    p.append(rect(515, 50, panel_w, 450, fill="#ffffff", stroke=C_SEC, sw=1.5, rx=8))
    p.append(text(515 + panel_w/2, 75, "Ефемерний DHE / ECDHE + Підпис (PFS)", size=14, color=C_SEC, bold=True))

    p.append(fitbox(535, 100, 190, 65, "Автентифікація:\nБоб підписує відкритий ключ:\nSig = Sign(PrivKey_Server, A||B)", size=11, fill=C_BOBF, stroke=C_BOB, sw=1.2))
    p.append(fitbox(745, 100, 210, 65, "Одноразові пари ключів:\n(a_eph, A_eph), (b_eph, B_eph)\nгенеруються на 1 сесію", size=11, fill=C_SECF, stroke=C_SEC, sw=1.2))

    p.append(fitbox(535, 185, 420, 120, "Життєвий цикл сесійного секрету:\n1. K = g^(a_eph · b_eph) mod p\n2. Виведення симетричних ключів: SessionKeys = HKDF(K)\n3. Негайне затирання в пам'яті (Secure Erasure): a_eph, b_eph, K = 0\n4. Довгостроковий ключ підпису НЕ бере участі в шифруванні даних!", size=11, fill="#ffffff", stroke=C_SEC, sw=1.5))

    p.append(fitbox(535, 325, 420, 155, "Гарантія Perfect Forward Secrecy (PFS):\n• Навіть якщо спецслужба записує гігабайти шифротексту роками...\n• І через 5 років компрометує сертифікат / PrivKey_Server...\n• Вона НЕ зможе розшифрувати минулі сесії, бо ключі a_eph і b_eph\n  були безповоротно знищені в момент завершення рукостискання!\n• TLS 1.3 повністю заборонив статичний RSA-обмін на користь PFS.", size=11, fill=C_ALICEF, stroke=C_ALICE, sw=1.5))

    render(os.path.join(OUT, "mitm-attack-and-pfs.svg"), W, H, *p)


# ── 3. dh-security-levels-vs-ecdh: Порівняння розміру ключів MODP проти ECDH ──
def fig_security_levels():
    W, H = 1000, 480
    p = []

    p.append(text(W / 2, 28, "Порівняння криптографічної стійкості: MODP DH проти ECDH", size=16, color=INK, bold=True))

    # Стовпчики таблиці / діаграми
    headers = [
        (130, "Рівень безпеки\n(симетричний еквівалент)"),
        (370, "Класичний DH (MODP)\nСубекспоненційний NFS: L[1/3]"),
        (640, "Еліптичні криві ECDH\nЕкспоненційний Pollard's rho: O(√n)"),
        (880, "Співвідношення\nрозмірів ключів")
    ]

    for cx, h_txt in headers:
        p.append(fitbox(cx - 110, 55, 220, 50, h_txt, size=12, fill=C_PUBF, stroke=C_PUB, sw=1.2, bold=True))

    rows = [
        ("80 бітів (застарілий)", "1024 біти (MODP-1024)\nУразливий до Logjam!", "160 бітів (secp160r1)", "6.4 : 1", C_DANGERF, C_DANGER),
        ("112 бітів (мінімальний)", "2048 бітів (MODP-2048)\nБазовий мінімум RFC 3526", "224 біти (secp224r1)", "9.1 : 1", C_WARNF, C_WARN),
        ("128 бітів (стандарт TLS 1.3)", "3072 біти (MODP-3072)\nВеликі пакети, важкий CPU", "256 бітів (X25519 / P-256)\n32 байти, миттєвий розрахунок", "12.0 : 1", C_BOBF, C_BOB),
        ("192 біти (підвищений)", "7680 бітів (MODP-7680)\nНепрактичний для мережі", "384 біти (P-384)", "20.0 : 1", C_ALICEF, C_ALICE),
        ("256 бітів (максимальний)", "15360 бітів (MODP-15360)\nКолосальні затримки", "512 бітів (X448 / P-521)\nКомпактний і швидкий", "30.0 : 1", C_SECF, C_SEC),
    ]

    y_start = 120
    row_h = 55
    for i, (sec, modp, ecdh, ratio, r_fill, r_stroke) in enumerate(rows):
        cy = y_start + i * (row_h + 10)
        p.append(fitbox(20, cy, 220, row_h, sec, size=12, fill=r_fill, stroke=r_stroke, sw=1.2, bold=True))
        p.append(fitbox(260, cy, 220, row_h, modp, size=11, fill="#ffffff", stroke=r_stroke, sw=1.2))
        p.append(fitbox(530, cy, 220, row_h, ecdh, size=11, fill="#ffffff", stroke=r_stroke, sw=1.2))
        p.append(fitbox(800, cy, 160, row_h, ratio, size=13, fill=r_fill, stroke=r_stroke, sw=1.5, bold=True))

    render(os.path.join(OUT, "dh-security-levels-vs-ecdh.svg"), W, H, *p)


# ── 4. small-subgroup-confinement: Атака на малі підгрупи та захист ──
def fig_small_subgroup():
    W, H = 1000, 500
    p = []

    p.append(text(W / 2, 28, "Атака на малі підгрупи (Small Subgroup Confinement) та захист", size=16, color=INK, bold=True))

    panel_w = 460
    # Ліва панель: Анатомія атаки
    p.append(rect(25, 50, panel_w, 430, fill="#ffffff", stroke=C_DANGER, sw=1.5, rx=8))
    p.append(text(25 + panel_w/2, 75, "Вразливість: Складений порядок групи p-1", size=13, color=C_DANGER, bold=True))

    p.append(fitbox(45, 95, 420, 75, "Порядок мультиплікативної групи Z_p* дорівнює p - 1.\nЯкщо p - 1 = 2 · q1 · q2 · ... · qk (містить малі прості дільники qi),\nу групі існують малі підгрупи порядку qi.", size=11, fill=C_DANGERF, stroke=C_DANGER, sw=1.2))

    p.append(fitbox(45, 185, 420, 120, "Сценарій атаки (Lim — Lee / Small Subgroup):\n1. Зловмисник надсилає фіктивний публічний ключ A' з малої підгрупи: (A')^qi ≡ 1 mod p.\n2. Жертва обчислює K = (A')^b mod p.\n3. Секрет K може набувати лише qi можливих значень!\n4. Зловмисник перебирає всі qi варіантів і дізнається (b mod qi).", size=11, fill="#ffffff", stroke=C_DANGER, sw=1.5))

    p.append(fitbox(45, 320, 420, 140, "Відновлення повного ключа b:\nПовторивши атаку для кількох малих підгруп q1, q2, q3...\nатакуючий об'єднує результати через Китайську теорему про залишки (CRT)\nза алгоритмом Поліга — Геллмана і повністю відновлює секрет b\nбез розв'язання повного дискретного логарифма!", size=11, fill=C_WARNF, stroke=C_WARN, sw=1.2))

    # Права панель: Захист
    p.append(rect(515, 50, panel_w, 430, fill="#ffffff", stroke=C_BOB, sw=1.5, rx=8))
    p.append(text(515 + panel_w/2, 75, "Методи інженерного захисту", size=13, color=C_BOB, bold=True))

    p.append(fitbox(535, 95, 420, 95, "1. Безпечні прості числа (Safe Primes, RFC 3526):\n• Просте число p обирають як p = 2q + 1, де q — також велике просте.\n• Дільниками p - 1 є лише {1, 2, q, 2q}.\n• Єдині малі підгрупи мають порядок 1 і 2 (значення 1 і p - 1),\n  які легко відсікти елементарною перевіркою.", size=11, fill=C_BOBF, stroke=C_BOB, sw=1.2))

    p.append(fitbox(535, 205, 420, 110, "2. Валідація публічного ключа (Subgroup Check):\n• Перевірка діапазону: 1 < A < p - 1.\n• Перевірка порядку підгрупи: A^q ≡ 1 mod p.\n• Якщо умова не виконується — ключ негайно відхиляється,\n  запобігаючи потраплянню в малі підгрупи.", size=11, fill="#ffffff", stroke=C_BOB, sw=1.5))

    p.append(fitbox(535, 330, 420, 130, "3. Захист на еліптичних кривих (Curve25519 Clamping):\n• Curve25519 має кофактор h = 8 (порядок кривої 8 · q).\n• Щоб нівелювати малу підгрупу порядку 8, у приватному скалярі\n  примусово скидають молодші 3 біти (scalar &= ~7).\n• Тоді множення на 8 гарантовано переводить точку в нейтральний елемент\n  малої підгрупи, роблячи атаку математично неможливою!", size=11, fill=C_ALICEF, stroke=C_ALICE, sw=1.5))

    render(os.path.join(OUT, "small-subgroup-confinement.svg"), W, H, *p)


if __name__ == "__main__":
    fig_dh_flow()
    fig_mitm_and_pfs()
    fig_security_levels()
    fig_small_subgroup()
    print("All figures generated successfully.")
