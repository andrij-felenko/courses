# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра теми
ENC   = "#c0392b"     # зашифроване / небезпека / атака
ENCF  = "#fdecea"
DIFF  = "#2457d6"     # дифузія / потоки / стан
DIFFF = "#eaf0fd"
KEYC  = "#27ae60"     # ключ / нонс / безпечне
KEYCF = "#eafaf0"
OK    = "#27ae60"     # рекомендований / захищений
OKF   = "#eafaf0"
WARN  = "#d97706"     # попередження / вразливість / RC4 / LFSR
WARNF = "#fef3c7"
BOXC  = "#4b5563"     # нейтральний блок / стан
BOXCF = "#f3f4f6"
ACC   = "#6b21a8"     # операції XOR / математика
ACCF  = "#f5f3ff"


# ── 1. stream-cipher-concept: Фундаментальна модель синхронного потокового шифру ──
def fig_stream_cipher_concept():
    W, H = 1000, 520
    p = []

    p.append(text(W / 2, 28, "Фундаментальна модель синхронного потокового шифру", size=16, color=INK, bold=True))

    # Контейнер генератора гами
    p.append(rect(30, 52, 940, 240, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    p.append(text(210, 76, "Генератор псевдовипадкової гами (PRG / CSPRNG)", size=14, color=INK, bold=True))

    # Входи: Ключ і Nonce
    p.append(fitbox(50, 100, 160, 44, "Секретний ключ K\n(128 / 256 бітів)", size=11, fill=KEYCF, stroke=KEYC, bold=True))
    p.append(fitbox(50, 160, 160, 44, "Одноразовий Nonce / IV\n(64 / 96 бітів)", size=11, fill=KEYCF, stroke=KEYC, bold=True))

    p.append(arrow(210, 122, 270, 150, color=KEYC, sw=1.8))
    p.append(arrow(210, 182, 270, 154, color=KEYC, sw=1.8))

    # Внутрішній стан
    p.append(rect(270, 96, 380, 168, fill=BOXCF, stroke=BOXC, sw=1.2, rx=6))
    p.append(text(460, 120, "Еволюція внутрішнього стану S[t]", size=12, color=INK, bold=True))

    p.append(fitbox(290, 140, 100, 40, "Стан S[0]", size=11, fill="#ffffff", stroke=BOXC))
    p.append(arrow(390, 160, 420, 160, color=DIFF, sw=1.5))
    p.append(fitbox(420, 140, 100, 40, "Стан S[t]", size=11, fill=DIFFF, stroke=DIFF, bold=True))
    p.append(arrow(520, 160, 550, 160, color=DIFF, sw=1.5))
    p.append(fitbox(550, 140, 90, 40, "S[t+1]", size=11, fill="#ffffff", stroke=BOXC))

    p.append(text(460, 210, "Перехід стану: S[t+1] = f(S[t]) | Вихід гами: z[t] = g(S[t])", size=10.5, color=MUTED))
    p.append(text(460, 235, "Автономна синхронна робота: гама не залежить від відкритого тексту", size=10, color=MUTED, italic=True))

    # Вихід гами
    p.append(arrow(650, 160, 720, 160, color=DIFF, sw=2.0))
    p.append(fitbox(720, 138, 220, 44, "Потік гами z[t] (Keystream)\nz₀, z₁, z₂, z₃, ..., zₙ", size=11, fill=DIFFF, stroke=DIFF, bold=True))

    # Нижня частина: Шифрування та Дешифрування
    # Шифрування (зліва)
    p.append(rect(30, 310, 455, 190, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    p.append(text(257, 334, "Шифрування (Encryption)", size=13, color=INK, bold=True))

    p.append(fitbox(50, 360, 160, 36, "Відкритий текст P[t]", size=11, fill=BOXCF, stroke=BOXC))
    p.append(fitbox(270, 360, 190, 36, "Гама z[t] (від PRG)", size=11, fill=DIFFF, stroke=DIFF))

    p.append(arrow(130, 396, 230, 432, color=LINE, sw=1.5))
    p.append(arrow(365, 396, 266, 432, color=DIFF, sw=1.5))

    p.append(circle(248, 440, 14, fill=ACCF, stroke=ACC, sw=1.8))
    p.append(text(248, 445, "⊕", size=18, color=ACC, bold=True))

    p.append(arrow(248, 454, 248, 480, color=ENC, sw=1.8))
    p.append(text(248, 492, "Шифротекст C[t] = P[t] ⊕ z[t]", size=11, color=ENC, bold=True))

    # Дешифрування (справа)
    p.append(rect(515, 310, 455, 190, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    p.append(text(742, 334, "Дешифрування (Decryption)", size=13, color=INK, bold=True))

    p.append(fitbox(535, 360, 160, 36, "Шифротекст C[t]", size=11, fill=ENCF, stroke=ENC))
    p.append(fitbox(755, 360, 190, 36, "Гама z[t] (від PRG)", size=11, fill=DIFFF, stroke=DIFF))

    p.append(arrow(615, 396, 715, 432, color=ENC, sw=1.5))
    p.append(arrow(850, 396, 751, 432, color=DIFF, sw=1.5))

    p.append(circle(733, 440, 14, fill=ACCF, stroke=ACC, sw=1.8))
    p.append(text(733, 445, "⊕", size=18, color=ACC, bold=True))

    p.append(arrow(733, 454, 733, 480, color=OK, sw=1.8))
    p.append(text(733, 492, "Відновлений текст P[t] = C[t] ⊕ z[t]", size=11, color=OK, bold=True))

    render(os.path.join(OUT, "stream-cipher-concept.svg"), W, H, *p)


# ── 2. lfsr-berlekamp-massey: LFSR та злам лінійної складності ──
def fig_lfsr_berlekamp_massey():
    W, H = 1020, 520
    p = []

    p.append(text(W / 2, 26, "Регістр зсуву LFSR та злам лінійної складності алгоритмом Берлекампа-Мессі", size=15, color=INK, bold=True))

    # Верхня панель: Структура LFSR довжини L
    p.append(rect(30, 48, 960, 246, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    p.append(text(510, 72, "Структура регістру зсуву з лінійним зворотним зв'язком (LFSR довжини L)", size=13, color=INK, bold=True))

    # Комірки регістру
    cells = [("s[t+L-1]", 80), ("s[t+L-2]", 200), ("...", 320), ("s[t+2]", 440), ("s[t+1]", 560), ("s[t]", 680)]
    for name, cx in cells:
        if name == "...":
            p.append(rect(cx, 95, 80, 44, fill=BG, stroke="none"))
            p.append(text(cx + 40, 122, "• • •", size=16, color=MUTED, bold=True))
        else:
            p.append(fitbox(cx, 95, 90, 44, name, size=12, fill=BOXCF, stroke=BOXC, bold=True))

    # Стрілки зсуву між комірками (вправо)
    p.append(arrow(170, 117, 200, 117, color=DIFF, sw=1.5))
    p.append(arrow(290, 117, 320, 117, color=DIFF, sw=1.5))
    p.append(arrow(400, 117, 440, 117, color=DIFF, sw=1.5))
    p.append(arrow(530, 117, 560, 117, color=DIFF, sw=1.5))
    p.append(arrow(650, 117, 680, 117, color=DIFF, sw=1.5))

    # Вихідний біт праворуч
    p.append(arrow(770, 117, 850, 117, color=OK, sw=2.0))
    p.append(fitbox(850, 95, 120, 44, "Вихідний біт\ns[t]", size=11, fill=OKF, stroke=OK, bold=True))

    # Відводи зворотного зв'язку (Feedback taps)
    p.append(line(725, 139, 725, 190, color=LINE, sw=1.3))
    p.append(fitbox(695, 190, 60, 26, "c[L]", size=10, fill=WARNF, stroke=WARN))
    p.append(arrow(725, 216, 525, 252, color=WARN, sw=1.3))

    p.append(line(605, 139, 605, 190, color=LINE, sw=1.3))
    p.append(fitbox(575, 190, 60, 26, "c[L-1]", size=10, fill=WARNF, stroke=WARN))
    p.append(arrow(605, 216, 517, 252, color=WARN, sw=1.3))

    p.append(line(485, 139, 485, 190, color=LINE, sw=1.3))
    p.append(fitbox(455, 190, 60, 26, "c[2]", size=10, fill=WARNF, stroke=WARN))
    p.append(arrow(485, 216, 503, 252, color=WARN, sw=1.3))

    p.append(line(245, 139, 245, 190, color=LINE, sw=1.3))
    p.append(fitbox(215, 190, 60, 26, "c[1]", size=10, fill=WARNF, stroke=WARN))
    p.append(arrow(245, 216, 495, 252, color=WARN, sw=1.3))

    # Центральний XOR суматор
    p.append(circle(510, 260, 13, fill=ACCF, stroke=ACC, sw=1.8))
    p.append(text(510, 265, "⊕", size=16, color=ACC, bold=True))

    # Зворотний зв'язок на вхід s[t+L]
    p.append(line(497, 260, 50, 260, color=WARN, sw=1.5))
    p.append(line(50, 260, 50, 117, color=WARN, sw=1.5))
    p.append(arrow(50, 117, 80, 117, color=WARN, sw=1.8))
    p.append(text(62, 105, "s[t+L]", size=10, color=WARN, bold=True))

    # Нижня панель: Вразливість та Берлекамп-Мессі
    p.append(rect(30, 310, 960, 192, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    p.append(text(510, 332, "Крах лінійності: Відновлення полінома за алгоритмом Берлекампа-Мессі", size=13, color=ENC, bold=True))

    p.append(fitbox(50, 355, 270, 70, "Помилкова інтуїція:\nПростір станів = 2ᴸ - 1 бітів\nПотрібно перебирати O(2ᴸ) ключів", size=11, fill=WARNF, stroke=WARN))
    p.append(fitbox(370, 355, 280, 70, "Реальність (Берлекамп-Мессі):\nДостатньо лише 2L послідовних бітів\nСкладність відновлення: O(L²)", size=11, fill=ENCF, stroke=ENC, bold=True))
    p.append(fitbox(690, 355, 280, 70, "Наслідки в інженерії:\nЧистий LFSR НЕПРИДАТНИЙ для крипто\nПотрібні нелінійні комбінатори / ARX", size=11, fill=BOXCF, stroke=BOXC))

    p.append(line(50, 442, 970, 442, color=LINE, sw=0.8, dash="4,4"))
    p.append(text(510, 464, "Характеристичний многочлен: C(D) = 1 + c₁D + c₂D² + ... + c_L D^L  (над GF(2))", size=11, color=INK, bold=True))
    p.append(text(510, 486, "Алгоритм Берлекампа-Мессі знаходить мінімальний поліном та весь початковий стан за лінійний час", size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "lfsr-berlekamp-massey.svg"), W, H, *p)


# ── 3. rc4-state-permutation: Внутрішній стан та цикл генерації RC4 ──
def fig_rc4_state_permutation():
    W, H = 1020, 520
    p = []

    p.append(text(W / 2, 26, "Внутрішній стан та цикл генерації шифру RC4 (байт-орієнтована перестановка)", size=15, color=INK, bold=True))

    # Ліва частина: Масив перестановки S[256]
    p.append(rect(30, 48, 300, 452, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    p.append(text(180, 74, "Масив перестановки S[0..255]", size=13, color=INK, bold=True))
    p.append(text(180, 94, "256 байтів стану (2048 бітів ентропії)", size=10.5, color=MUTED))

    slots = [("S[0]", "0x42", 116), ("S[1]", "0x17", 154), ("...", "...", 192), ("S[i]", "S[i]", 230),
             ("...", "...", 268), ("S[j]", "S[j]", 306), ("...", "...", 344), ("S[255]", "0x9A", 382)]

    for idx, val, cy in slots:
        if idx == "...":
            p.append(text(180, cy + 18, "• • •", size=14, color=MUTED, bold=True))
        else:
            is_hl = idx in ("S[i]", "S[j]")
            fcol = WARNF if is_hl else BOXCF
            scol = WARN if is_hl else BOXC
            p.append(fitbox(60, cy, 100, 32, idx, size=11, fill=fcol, stroke=scol, bold=is_hl))
            p.append(fitbox(180, cy, 110, 32, val, size=11, fill=fcol, stroke=scol, bold=is_hl))

    p.append(fitbox(50, 430, 260, 52, "Покажчики стану:\n• i = (i + 1) mod 256\n• j = (j + S[i]) mod 256", size=10.5, fill=WARNF, stroke=WARN, bold=True))

    # Середня частина: Алгоритм PRGA крок за кроком
    p.append(rect(350, 48, 340, 452, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    p.append(text(520, 74, "Генерація гами (PRGA)", size=13, color=INK, bold=True))

    steps = [
        ("Крок 1: Інкремент i", "i = (i + 1) mod 256", 110, BOXCF, BOXC),
        ("Крок 2: Накопичення j", "j = (j + S[i]) mod 256", 175, BOXCF, BOXC),
        ("Крок 3: Обмін значень", "swap(S[i], S[j])", 240, WARNF, WARN),
        ("Крок 4: Розрахунок індексу", "t = (S[i] + S[j]) mod 256", 305, DIFFF, DIFF),
        ("Крок 5: Байт гами", "K_byte = S[t]", 370, OKF, OK)
    ]

    for title_s, code_s, sy, fbg, sbg in steps:
        p.append(fitbox(370, sy, 300, 48, title_s + "\n" + code_s, size=11, fill=fbg, stroke=sbg, bold=True))
        if sy < 370:
            p.append(arrow(520, sy + 48, 520, sy + 65, color=LINE, sw=1.4))

    p.append(fitbox(370, 435, 300, 48, "Шифрування байта:\nC[k] = P[k] ⊕ K_byte", size=11, fill=ACCF, stroke=ACC, bold=True))

    # Права частина: Критичні вразливості та фатальні зсуви
    p.append(rect(710, 48, 280, 452, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    p.append(text(850, 74, "Фатальні вади RC4", size=13, color=ENC, bold=True))

    p.append(fitbox(725, 105, 250, 72, "1. Зсув другого байта (MS):\nP(Z₂ = 0) ≈ 1/128\n(замість 1/256)\nВитік у перших байтах", size=10.5, fill=ENCF, stroke=ENC, bold=True))
    p.append(fitbox(725, 195, 250, 76, "2. Атака FMS на WEP:\nПрефікс IV (3 байти) + Key\nСлабкі ключі дозволяють\nвідновити майстер-ключ", size=10.5, fill=ENCF, stroke=ENC, bold=True))
    p.append(fitbox(725, 290, 250, 80, "3. Атаки на TLS (2013-15):\nЗсуви пар байтів (ABPPS)\nВідновлення cookie HTTP\nпісля 2²⁴-2³⁰ запитів", size=10.5, fill=ENCF, stroke=ENC, bold=True))

    p.append(fitbox(725, 390, 250, 92, "RFC 7465 (2015):\nПОВНА ЗАБОРОНА RC4\nу протоколах TLS.\nАлгоритм не підлягає\nвикористанню!", size=10.5, fill=ENCF, stroke=ENC, bold=True))

    render(os.path.join(OUT, "rc4-state-permutation.svg"), W, H, *p)


# ── 4. chacha20-state-matrix: Матриця стану та раунди ARX у ChaCha20 ──
def fig_chacha20_state_matrix():
    W, H = 1040, 560
    p = []

    p.append(text(W / 2, 26, "Матриця стану 4x4, раунди ARX та додавання Feed-Forward у ChaCha20", size=15, color=INK, bold=True))

    # Ліва частина: Матриця стану 4x4 (16 слів по 32 біти)
    p.append(rect(30, 48, 480, 492, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    p.append(text(270, 74, "Матриця стану ChaCha20 (64 байти / 512 бітів)", size=13, color=INK, bold=True))

    grid = [
        # Рядок 0: Константи
        [("c0: 0x61707865", OKF, OK), ("c1: 0x3320646e", OKF, OK), ("c2: 0x79622d32", OKF, OK), ("c3: 0x6b206574", OKF, OK)],
        # Рядок 1: Ключ 0-3
        [("k0: Key[0..31]", KEYCF, KEYC), ("k1: Key[32..63]", KEYCF, KEYC), ("k2: Key[64..95]", KEYCF, KEYC), ("k3: Key[96..127]", KEYCF, KEYC)],
        # Рядок 2: Ключ 4-7
        [("k4: Key[128..159]", KEYCF, KEYC), ("k5: Key[160..191]", KEYCF, KEYC), ("k6: Key[192..223]", KEYCF, KEYC), ("k7: Key[224..255]", KEYCF, KEYC)],
        # Рядок 3: Лічильник та Нонс (RFC 8439)
        [("b0: Block Count", DIFFF, DIFF), ("n0: Nonce[0..31]", WARNF, WARN), ("n1: Nonce[32..63]", WARNF, WARN), ("n2: Nonce[64..95]", WARNF, WARN)]
    ]

    gy0 = 95
    for r_idx, row in enumerate(grid):
        for c_idx, (label, fbg, sbg) in enumerate(row):
            gx = 48 + c_idx * 110
            gy = gy0 + r_idx * 70
            p.append(fitbox(gx, gy, 102, 58, label, size=9.5, fill=fbg, stroke=sbg, bold=True))

    p.append(fitbox(50, 390, 440, 40, "Рядок 0: Константа \"expand 32-byte k\" (фіксує базис простору)", size=10.5, fill=OKF, stroke=OK))
    p.append(fitbox(50, 435, 440, 40, "Рядки 1-2: 256-бітний ключ | Рядок 3: Лічильник (32 біти) + Nonce (96 бітів)", size=10.5, fill=BOXCF, stroke=BOXC))
    p.append(fitbox(50, 480, 440, 46, "Прямий доступ (Random Access): для блоку N лічильник ставиться в N\nбез потреби обчислювати всі попередні байти!", size=10, fill=DIFFF, stroke=DIFF, bold=True))

    # Права частина: Чвертьраунд (QR) та Feed-Forward
    p.append(rect(530, 48, 480, 492, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    p.append(text(770, 74, "Чвертьраунд QR(a, b, c, d) та 20 раундів", size=13, color=INK, bold=True))

    # Формули QR
    qr_text = "1. a += b;  d ^= a;  d <<<= 16;\n2. c += d;  b ^= c;  b <<<= 12;\n3. a += b;  d ^= a;  d <<<= 8;\n4. c += d;  b ^= c;  b <<<= 7;"
    p.append(fitbox(550, 98, 440, 88, "Базова операція ARX (константний час CPU):\n" + qr_text, size=11, fill=ACCF, stroke=ACC, bold=True))

    # Раунди
    p.append(fitbox(550, 198, 210, 70, "Колонкові раунди:\nQR(0, 4, 8, 12)\nQR(1, 5, 9, 13)\nQR(2, 6, 10, 14)\nQR(3, 7, 11, 15)", size=10, fill=BOXCF, stroke=DIFF, bold=True))
    p.append(fitbox(780, 198, 210, 70, "Діагональні раунди:\nQR(0, 5, 10, 15)\nQR(1, 6, 11, 12)\nQR(2, 7, 8, 13)\nQR(3, 4, 9, 14)", size=10, fill=BOXCF, stroke=DIFF, bold=True))

    p.append(arrow(655, 272, 770, 290, color=DIFF, sw=1.5))
    p.append(arrow(885, 272, 770, 290, color=DIFF, sw=1.5))
    p.append(fitbox(550, 292, 440, 32, "10 подвійних раундів = 20 раундів повної дифузії стану", size=11, fill=DIFFF, stroke=DIFF, bold=True))

    # Feed-Forward (Пряме додавання)
    p.append(rect(550, 338, 440, 188, fill=KEYCF, stroke=KEYC, sw=1.2, rx=6))
    p.append(text(770, 360, "Критичний бар'єр: Пряме додавання (Feed-Forward)", size=11.5, color=KEYC, bold=True))

    p.append(fitbox(565, 372, 190, 42, "Початковий стан\nS_init[0..15]", size=10.5, fill="#ffffff", stroke=BOXC))
    p.append(fitbox(785, 372, 190, 42, "Переставлений стан\nS_perm[0..15]", size=10.5, fill="#ffffff", stroke=DIFF))

    p.append(arrow(660, 414, 755, 438, color=KEYC, sw=1.5))
    p.append(arrow(880, 414, 785, 438, color=KEYC, sw=1.5))

    p.append(circle(770, 444, 12, fill="#ffffff", stroke=KEYC, sw=1.6))
    p.append(text(770, 448, "+", size=16, color=KEYC, bold=True))

    p.append(arrow(770, 456, 770, 474, color=KEYC, sw=1.8))
    p.append(fitbox(565, 476, 410, 40, "S_final[i] = S_init[i] + S_perm[i] mod 2³²  (64 байти гами)\nЗапобігає оберненню раундів для відновлення ключа!", size=10, fill="#ffffff", stroke=KEYC, bold=True))

    render(os.path.join(OUT, "chacha20-state-matrix.svg"), W, H, *p)


# ── 5. nonce-reuse-and-bitflip: Вразливості потокового шифрування та AEAD ──
def fig_nonce_reuse_and_bitflip():
    W, H = 1040, 530
    p = []

    p.append(text(W / 2, 26, "Вразливості потокових шифрів та захист через ChaCha20-Poly1305 (AEAD)", size=15, color=INK, bold=True))

    # Ліва верхня панель: Катастрофа повторного нонсу (Two-Time Pad)
    p.append(rect(30, 48, 475, 230, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    p.append(text(267, 72, "1. Катастрофа повторного Nonce (Two-Time Pad)", size=12.5, color=ENC, bold=True))

    p.append(fitbox(45, 92, 210, 42, "C₁ = P₁ ⊕ Keystream\n(Зашифровано на Nonce N)", size=10.5, fill=ENCF, stroke=ENC))
    p.append(fitbox(280, 92, 210, 42, "C₂ = P₂ ⊕ Keystream\n(Повторно той самий Nonce N)", size=10.5, fill=ENCF, stroke=ENC))

    p.append(arrow(150, 134, 250, 160, color=ENC, sw=1.5))
    p.append(arrow(385, 134, 284, 160, color=ENC, sw=1.5))

    p.append(circle(267, 166, 12, fill=ACCF, stroke=ACC, sw=1.5))
    p.append(text(267, 171, "⊕", size=15, color=ACC, bold=True))

    p.append(arrow(267, 178, 267, 196, color=ENC, sw=1.6))
    p.append(fitbox(45, 198, 445, 66, "C₁ ⊕ C₂ = (P₁ ⊕ K) ⊕ (P₂ ⊕ K) = P₁ ⊕ P₂\nКлюч і гама ПОВНІСТЮ ЗНИЩЕНІ!\nАтака Crib Dragging відновлює обидва тексти за секунди.", size=10.5, fill=WARNF, stroke=WARN, bold=True))

    # Права верхня панель: Пластичність та Біт-фліппінг
    p.append(rect(535, 48, 475, 230, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    p.append(text(772, 72, "2. Пластичність (Malleability) та Біт-фліппінг", size=12.5, color=ENC, bold=True))

    p.append(fitbox(550, 92, 445, 42, "Перехоплення шифротексту: C = P ⊕ Keystream", size=10.5, fill=BOXCF, stroke=BOXC))

    p.append(fitbox(550, 142, 445, 44, "Зловмисник інжектує маску маніпуляції Δ:\nC' = C ⊕ Δ", size=10.5, fill=ENCF, stroke=ENC, bold=True))

    p.append(fitbox(550, 194, 445, 70, "Дешифрування без автентифікації:\nP' = C' ⊕ Keystream = (P ⊕ Keystream ⊕ Δ) ⊕ Keystream = P ⊕ Δ\nТочна зміна рахунку отримувача або прапорця прав без помилки!", size=10.5, fill=WARNF, stroke=WARN, bold=True))

    # Нижня панель: Конструкція AEAD ChaCha20-Poly1305 (RFC 8439)
    p.append(rect(30, 292, 980, 224, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    p.append(text(520, 316, "Сучасне вирішення: Автентифіковане шифрування ChaCha20-Poly1305 (RFC 8439)", size=13, color=OK, bold=True))

    # Крок 1: Блок 0 для Poly1305 ключа
    p.append(fitbox(50, 335, 260, 68, "Блок 0 ChaCha20 (Counter = 0):\nГенерація одноразового ключа\nPoly1305: One-Time Key (r, s)\n(32 байти з першого блоку гами)", size=10.5, fill=KEYCF, stroke=KEYC, bold=True))

    p.append(arrow(310, 369, 360, 369, color=KEYC, sw=1.8))

    # Крок 2: Шифрування даних ChaCha20 з блоку 1
    p.append(fitbox(360, 335, 280, 68, "Блоки 1..N ChaCha20 (Counter ≥ 1):\nШифрування корисного навантаження:\nC = Plaintext ⊕ ChaCha20(K, Nonce, Counter)", size=10.5, fill=DIFFF, stroke=DIFF, bold=True))

    p.append(arrow(640, 369, 690, 369, color=DIFF, sw=1.8))

    # Крок 3: Poly1305 MAC тег
    p.append(fitbox(690, 335, 300, 68, "Обчислення тегу Poly1305 MAC:\nTag = Poly1305(r, s, AAD || C || Lens)\n16-байтний криптографічний тег автентичності", size=10.5, fill=OKF, stroke=OK, bold=True))

    # Фінальне повідомлення
    p.append(fitbox(50, 420, 940, 80, "Повний пакет: [ Нешифрований Nonce ] + [ Шифротекст C ] + [ 16-байтний MAC Tag ]\nПриймач СПЕРШУ перевіряє Tag. Якщо хоч один біт C або AAD змінено — дешифрування НЕ ВІДБУВАЄТЬСЯ!\nПовний захист від підробок (Integrity), біт-фліппінгу та витоків через неавтентифіковані дані.", size=10.5, fill=OKF, stroke=OK, bold=True))

    render(os.path.join(OUT, "nonce-reuse-and-bitflip.svg"), W, H, *p)


if __name__ == "__main__":
    fig_stream_cipher_concept()
    fig_lfsr_berlekamp_massey()
    fig_rc4_state_permutation()
    fig_chacha20_state_matrix()
    fig_nonce_reuse_and_bitflip()
    print("All stream-cipher figures successfully rendered!")
