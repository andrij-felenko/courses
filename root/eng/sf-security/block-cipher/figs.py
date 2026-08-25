# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра теми
ENC   = "#c0392b"     # зашифроване / небезпека / S-Box
ENCF  = "#fdecea"
DIFF  = "#2457d6"     # дифузія / лінійне перемішування / ShiftRows / MixColumns
DIFFF = "#eaf0fd"
KEYC  = "#27ae60"     # раундовий ключ / AddRoundKey
KEYCF = "#eafaf0"
OK    = "#27ae60"     # безпечний / рекомендований
OKF   = "#eafaf0"
WARN  = "#d97706"     # попередження / вразливість / ECB
WARNF = "#fef3c7"
BOXC  = "#4b5563"     # нейтральний блок / стан
BOXCF = "#f3f4f6"
ACC   = "#6b21a8"     # операції XOR / математика
ACCF  = "#f5f3ff"


# ── 1. feistel-vs-spn: Порівняння мережі Фейстеля та SP-мережі ──
def fig_feistel_vs_spn():
    W, H = 1040, 500
    p = []

    p.append(text(W / 2, 28, "Порівняння архітектур: Мережа Фейстеля проти SP-мережі (AES)", size=16, color=INK, bold=True))

    # Ліва колонка: Мережа Фейстеля
    p.append(rect(30, 48, 470, 436, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    p.append(text(265, 74, "Мережа Фейстеля (DES, Blowfish)", size=14, color=INK, bold=True))
    p.append(text(265, 92, "Асиметричний раунд: перетворення половини блоку", size=11, color=MUTED, italic=True))

    # Вхідні блоки
    p.append(fitbox(70, 110, 160, 36, "Ліва половина L[i-1]", size=12, fill=BOXCF, stroke=BOXC))
    p.append(fitbox(300, 110, 160, 36, "Права половина R[i-1]", size=12, fill=BOXCF, stroke=BOXC))

    # Лінії вниз від входів
    p.append(arrow(150, 146, 150, 240, color=LINE, sw=1.5))
    p.append(line(380, 146, 380, 175, color=LINE, sw=1.5))
    p.append(arrow(380, 175, 305, 175, color=LINE, sw=1.5))

    # Блок раундової функції F
    p.append(fitbox(195, 160, 110, 44, "Функція F(R, K)", size=11, fill=ENCF, stroke=ENC, bold=True))
    p.append(arrow(140, 182, 195, 182, color=KEYC, sw=1.5))
    p.append(text(105, 186, "Ключ K[i]", size=11, color=KEYC, bold=True))

    # XOR вузол
    p.append(circle(150, 252, 12, fill=ACCF, stroke=ACC, sw=1.5))
    p.append(text(150, 256, "⊕", size=16, color=ACC, bold=True))
    p.append(arrow(250, 204, 150, 240, color=LINE, sw=1.5))

    # Перехрестя (Swap)
    p.append(line(380, 175, 380, 310, color=LINE, sw=1.5))
    p.append(line(150, 264, 150, 310, color=LINE, sw=1.5))

    p.append(arrow(380, 310, 150, 370, color=LINE, sw=1.5))
    p.append(arrow(150, 310, 380, 370, color=LINE, sw=1.5))

    # Вихідні блоки
    p.append(fitbox(70, 380, 160, 36, "L[i] = R[i-1]", size=12, fill=BOXCF, stroke=BOXC))
    p.append(fitbox(300, 380, 160, 36, "R[i] = L[i-1] ⊕ F(R, K)", size=11, fill=BOXCF, stroke=BOXC))

    p.append(fitbox(50, 430, 430, 38, "Властивість: F не обов'язково оборотна; дешифрування ідентичне", size=11, fill="#f9fafb", stroke=MUTED))

    # Права колонка: SP-мережа
    p.append(rect(540, 48, 470, 436, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    p.append(text(775, 74, "SP-мережа (AES / Rijndael)", size=14, color=INK, bold=True))
    p.append(text(775, 92, "Симетричний раунд: паралельна зміна всього стану", size=11, color=MUTED, italic=True))

    # Вхідний стан
    p.append(fitbox(645, 110, 260, 36, "Вхідний стан State (128 бітів / 16 байтів)", size=11, fill=BOXCF, stroke=BOXC))
    p.append(arrow(775, 146, 775, 170, color=LINE, sw=1.5))

    # Шар S-боксів (SubBytes)
    p.append(fitbox(615, 170, 320, 44, "Шар підстановки: SubBytes (S-Box GF(2⁸))\nКонфузія: нелінійне збурення кожного байта", size=10, fill=ENCF, stroke=ENC, bold=True))
    p.append(arrow(775, 214, 775, 238, color=LINE, sw=1.5))

    # Шар дифузії (ShiftRows + MixColumns)
    p.append(fitbox(615, 238, 320, 52, "Шар дифузії: ShiftRows + MixColumns (MDS)\nДифузія: розмазування байтів по матриці стану", size=10, fill=DIFFF, stroke=DIFF, bold=True))
    p.append(arrow(775, 290, 775, 314, color=LINE, sw=1.5))

    # Шар додавання ключа (AddRoundKey)
    p.append(fitbox(615, 314, 320, 44, "Шар ключа: AddRoundKey (State ⊕ RoundKey)\nВведення секрету: лінійне накладання раундового ключа", size=10, fill=KEYCF, stroke=KEYC, bold=True))
    p.append(arrow(775, 358, 775, 380, color=LINE, sw=1.5))

    # Вихідний стан
    p.append(fitbox(645, 380, 260, 36, "Вихідний стан раунду (повна дифузія за 2 раунди)", size=11, fill=BOXCF, stroke=BOXC))

    p.append(fitbox(560, 430, 430, 38, "Властивість: усі операції оборотно розраховуються; повний паралелізм", size=11, fill="#f9fafb", stroke=MUTED))

    render(os.path.join(OUT, "feistel-vs-spn.svg"), W, H, *p)


# ── 2. aes-round-anatomy: Анатомія одного раунду AES ──
def fig_aes_round_anatomy():
    W, H = 1060, 380
    p = []

    p.append(text(W / 2, 26, "Анатомія стандартного раунду AES: перетворення матриці стану 4×4", size=16, color=INK, bold=True))

    steps = [
        (130, "1. SubBytes", "Нелінійна заміна",
         "Кожен байт s[i,j] замінюється\nчерез інверсію в GF(2⁸)\nта афінне перетворення",
         ENCF, ENC),
        (380, "2. ShiftRows", "Циклічний зсув",
         "Рядок 0: зсув 0 байтів\nРядок 1: зсув 1 ліворуч\nРядок 2: зсув 2 ліворуч\nРядок 3: зсув 3 ліворуч",
         DIFFF, DIFF),
        (630, "3. MixColumns", "MDS-множення",
         "Множення кожного стовпчика\nна многочлен c(x) у GF(2⁸)\nBranch Number = 5",
         DIFFF, DIFF),
        (880, "4. AddRoundKey", "XOR з ключем",
         "Поелементний XOR стану 4×4\nіз 128-бітним раундовим\nключем W[4r...4r+3]",
         KEYCF, KEYC),
    ]

    for cx, title, subtitle, desc, fill_c, strk_c in steps:
        p.append(rect(cx - 110, 52, 220, 290, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
        p.append(text(cx, 78, title, size=13, color=INK, bold=True))
        p.append(text(cx, 96, subtitle, size=11, color=MUTED, italic=True))

        # Міні-матриця 4x4
        mx, my = cx - 44, 114
        csz = 22
        for r in range(4):
            for c in range(4):
                p.append(rect(mx + c * csz, my + r * csz, csz, csz, fill=fill_c, stroke=strk_c, sw=1.0, rx=2))
        p.append(text(cx, my + 44, "4 × 4", size=11, color=strk_c, bold=True))

        # Опис трансформації
        p.append(fitbox(cx - 100, 215, 200, 110, desc, size=10, fill=fill_c, stroke=strk_c, sw=1.2))

    # Стрілки переходу між кроками
    p.append(arrow(240, 160, 270, 160, color=LINE, sw=1.8))
    p.append(arrow(490, 160, 520, 160, color=LINE, sw=1.8))
    p.append(arrow(740, 160, 770, 160, color=LINE, sw=1.8))

    # Підпис фінального раунду
    p.append(text(W / 2, 362, "* У фінальному раунді (10, 12 або 14) операцію MixColumns пропущено для симетрії дешифрування", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "aes-round-anatomy.svg"), W, H, *p)


# ── 3. block-cipher-modes: Режими роботи блокового шифру ──
def fig_block_cipher_modes():
    W, H = 1080, 520
    p = []

    p.append(text(W / 2, 28, "Режими роботи блокового шифру: порівняння архітектурних гарантій", size=16, color=INK, bold=True))

    modes = [
        (145, "ECB (Codebook)", "Небезпечний",
         [("C[i] = Enc(K, P[i])", WARNF, WARN),
          ("Детерміністичний:\nоднакові блоки дають\nоднаковий шифротекст", WARNF, WARN),
          ("Вразливість:\nзберігає патерни («Tux»)\nЗаборонено для N > 1", WARNF, WARN)]),

        (405, "CBC (Chaining)", "Зчеплення + IV",
         [("C[i] = Enc(K, P[i] ⊕ C[i-1])\nC[0] = IV", BOXCF, BOXC),
          ("Послідовний:\nшифрування не паралелиться,\nдешифрування паралельне", BOXCF, BOXC),
          ("Вразливість:\nPadding Oracle (PKCS#7)\nпри помилках перевірки", WARNF, WARN)]),

        (665, "CTR (Counter)", "Потоковий режим",
         [("C[i] = P[i] ⊕ Enc(K, Nonce||i)", OKF, OK),
          ("Паралельний:\nмиттєвий довільний доступ,\nне потребує padding", OKF, OK),
          ("Вимога безпеки:\nкатастрофа при повторі\nпари (Key, Nonce)", WARNF, WARN)]),

        (925, "GCM (AEAD)", "CTR + GHASH",
         [("C = CTR_Enc(K, IV, P)\nT = GHASH(H, AAD, C)", OKF, OK),
          ("Автентифікований:\nконфіденційність P +\nцілісність AAD і C", OKF, OK),
          ("Золотий стандарт:\nTLS 1.3, SSH, IPsec,\nапаратне прискорення", OKF, OK)]),
    ]

    for cx, title, subtitle, boxes in modes:
        p.append(rect(cx - 115, 54, 230, 444, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
        p.append(text(cx, 80, title, size=13, color=INK, bold=True))
        p.append(text(cx, 98, subtitle, size=11, color=MUTED, italic=True))

        y_pos = [118, 226, 350]
        for i, (txt, fill_c, strk_c) in enumerate(boxes):
            p.append(fitbox(cx - 102, y_pos[i], 204, 98, txt, size=11, fill=fill_c, stroke=strk_c, sw=1.5))

    render(os.path.join(OUT, "block-cipher-modes.svg"), W, H, *p)


# ── 4. cache-timing-attack-vector: Вектор кеш-таймінг атаки на T-таблиці ──
def fig_cache_timing():
    W, H = 1000, 390
    p = []

    p.append(text(W / 2, 26, "Вектор таймінг-атаки на табличну реалізацію AES (T-tables у L1-кеші)", size=16, color=INK, bold=True))

    # Блок обчислення індексу
    p.append(fitbox(40, 60, 260, 90, "Відкритий байт p[i] ⊕ Ключ k[i]\n\nІндекс T-таблиці:\nidx = p[i] ⊕ k[i]", size=11, fill=BOXCF, stroke=BOXC, bold=True))
    p.append(arrow(300, 105, 360, 105, color=LINE, sw=1.8))

    # Блок звернення до пам'яті
    p.append(fitbox(360, 60, 270, 90, "Доступ до пам'яті:\nval = T_table[idx]\n\nАдреса = База + (idx × 4)", size=11, fill=ENCF, stroke=ENC, bold=True))
    p.append(arrow(630, 105, 690, 105, color=LINE, sw=1.8))

    # Блок ліній кешу L1
    p.append(rect(690, 52, 270, 316, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    p.append(text(825, 76, "L1 Cache Lines (64 байти)", size=12, color=INK, bold=True))

    cache_lines = [
        (825, 110, "Line 0: T[0..15] (HIT: ~4 такти)", OKF, OK),
        (825, 160, "Line 1: T[16..31] (HIT: ~4 такти)", OKF, OK),
        (825, 210, "Line 2: T[32..47] (MISS: ~40 тактів)", WARNF, WARN),
        (825, 260, "Line 3: T[48..63] (HIT: ~4 такти)", OKF, OK),
        (825, 310, "Line 4..15: решта ліній...", BOXCF, BOXC),
    ]
    for cx, cy, txt, fill_c, strk_c in cache_lines:
        p.append(fitbox(cx - 120, cy - 18, 240, 36, txt, size=10, fill=fill_c, stroke=strk_c, sw=1.2))

    # Нижній блок: Витік інформації
    p.append(fitbox(40, 190, 590, 178, "Механізм витоку секретного ключа k[i]:\n1. Супротивник контролює p[i] і вимірює час шифрування (Flush+Reload / Prime+Probe);\n2. Різниця часу HIT (~4 такти) та MISS (~40 тактів) викриває, до якої кеш-лінії звертався процесор;\n3. Знаючи p[i] та номер активної кеш-лінії, зловмисник звужує можливі значення k[i] до кількох бітів;\n4. Захист: константний час через апаратні інструкції AES-NI або програмний бітслайсинг.", size=11, fill=WARNF, stroke=WARN))

    render(os.path.join(OUT, "cache-timing-attack-vector.svg"), W, H, *p)


if __name__ == "__main__":
    fig_feistel_vs_spn()
    fig_aes_round_anatomy()
    fig_block_cipher_modes()
    fig_cache_timing()
    print("All figures generated successfully.")
