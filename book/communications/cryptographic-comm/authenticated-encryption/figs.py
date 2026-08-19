# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра теми
ENC   = "#c0392b"     # зашифроване / небезпека
ENCF  = "#fdecea"
MAC   = "#2457d6"     # автентифікація / тег / MAC
MACF  = "#eaf0fd"
OK    = "#27ae60"     # автентифіковане / цілісне
OKF   = "#eafaf0"
WARN  = "#d97706"     # попередження / вразливість
WARNF = "#fef3c7"
CLR   = "#4b5563"     # відкриті дані / AAD
CLRF  = "#f3f4f6"
ACC   = "#6b21a8"     # математичні операції / перетворення
ACCF  = "#f5f3ff"


# ── 1. composition-paradigms: чотири підходи до поєднання шифрування й автентичності ──
def fig_composition_paradigms():
    W, H = 1080, 520
    p = []

    p.append(text(W / 2, 32, "Чотири архітектурні парадигми захисту повідомлення", size=16, color=INK, bold=True))

    cols = [
        (145, "Encrypt-and-MAC", "SSH-1",
         [("Відкритий текст P", CLRF, CLR),
          ("C = Enc(K1, P)\nT = MAC(K2, P)", ENCF, ENC),
          ("Вразливість:\nвитік рівності P\nчерез детермінований MAC", WARNF, WARN)]),

        (405, "MAC-then-Encrypt", "SSL 3.0 / TLS 1.0–1.2",
         [("Відкритий текст P", CLRF, CLR),
          ("P' = P || MAC(K2, P)\nC = Enc(K1, P' || Pad)", ENCF, ENC),
          ("Вразливість:\nPadding Oracle,\nLucky Thirteen, POODLE", WARNF, WARN)]),

        (665, "Encrypt-then-MAC", "IPsec ESP / TLS 1.2 EtM",
         [("Відкритий текст P", CLRF, CLR),
          ("C = Enc(K1, P)\nT = MAC(K2, AAD || C)", OKF, OK),
          ("Стійкий, але вимагає:\n2 проходів, 2 ключів\nі ручної збірки", CLRF, CLR)]),

        (925, "Інтегрований AEAD", "AES-GCM / ChaCha20-Poly",
         [("Plaintext P + AAD", CLRF, CLR),
          ("(C, T) = AEAD_Enc(K, N, A, P)", OKF, OK),
          ("Єдиний чорний ящик:\n1 прохід, захист AAD,\nдешифрування лише після тегу", OKF, OK)]),
    ]

    for cx, title, subtitle, boxes in cols:
        p.append(rect(cx - 115, 60, 230, 440, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
        p.append(text(cx, 84, title, size=13, color=INK, bold=True))
        p.append(text(cx, 102, subtitle, size=11, color=MUTED, italic=True))

        y_pos = [125, 230, 370]
        for i, (txt, fill_c, strk_c) in enumerate(boxes):
            p.append(fitbox(cx - 100, y_pos[i], 200, 84, txt, size=12, fill=fill_c, stroke=strk_c, sw=1.5))
            if i < 2:
                p.append(arrow(cx, y_pos[i] + 88, cx, y_pos[i + 1] - 4, color=LINE, sw=1.5))

    render(os.path.join(OUT, "composition-paradigms.svg"), W, H, *p)


# ── 2. aead-tuple-flow: анатомія параметрів AEAD та захисний бар'єр ───────────
def fig_aead_tuple_flow():
    W, H = 1080, 480
    p = []

    p.append(text(W / 2, 30, "Анатомія інтерфейсу AEAD та захисний бар'єр верифікації", size=16, color=INK, bold=True))

    # Вхідні параметри
    p.append(fitbox(50, 70, 220, 50, "Секретний ключ K\n(128 або 256 бітів)", size=13, fill=MACF, stroke=MAC, sw=1.6))
    p.append(fitbox(50, 140, 220, 50, "Одноразове число Nonce N\n(96 бітів, унікальне!)", size=13, fill=WARNF, stroke=WARN, sw=1.6))
    p.append(fitbox(50, 210, 220, 50, "Асоційовані дані AAD (A)\n(заголовки пакетів)", size=13, fill=CLRF, stroke=CLR, sw=1.6))
    p.append(fitbox(50, 280, 220, 50, "Відкритий текст Plaintext (P)\n(корисне навантаження)", size=13, fill=OKF, stroke=OK, sw=1.6))

    # Центральний блок AEAD
    p.append(fitbox(350, 130, 280, 150, "Інтегрований примітив\nAEAD Encrypt\n(AES-GCM / ChaCha20-Poly1305)\n\nОдночасне шифрування\nта формування доказу", size=13, fill="#ffffff", stroke=INK, sw=2))

    p.append(arrow(275, 95, 345, 155, color=MAC, sw=1.8))
    p.append(arrow(275, 165, 345, 180, color=WARN, sw=1.8))
    p.append(arrow(275, 235, 345, 215, color=CLR, sw=1.8))
    p.append(arrow(275, 305, 345, 245, color=OK, sw=1.8))

    # Вихідний кадр
    p.append(text(810, 75, "Структура мережевого кадру", size=13, color=INK, bold=True))
    p.append(fitbox(680, 95, 260, 42, "AAD: Заголовок пакета (відкритий)", size=12, fill=CLRF, stroke=CLR, sw=1.5))
    p.append(fitbox(680, 145, 260, 52, "Ciphertext C: Зашифроване тіло\n(довжина дорівнює P)", size=12, fill=ENCF, stroke=ENC, sw=1.6))
    p.append(fitbox(680, 205, 260, 45, "Tag T: Автентифікаційний тег\n(16 байтів / 128 бітів)", size=12, fill=MACF, stroke=MAC, sw=1.6))

    p.append(arrow(635, 180, 675, 120, color=CLR, sw=1.8))
    p.append(arrow(635, 205, 675, 170, color=ENC, sw=1.8))
    p.append(arrow(635, 230, 675, 225, color=MAC, sw=1.8))

    # Нижній бар'єр перевірки
    p.append(fitbox(50, 375, 980, 75, "Бар'єр дешифрування (Decryption Barrier):\nЯкщо Tag не зійшовся хоча б в одному біті — повідомлення негайно відкидається (⊥).\nЖоден байт Plaintext НЕ повертається у відкритий буфер до повної константно-часової верифікації тегу!", size=13, fill=OKF, stroke=OK, sw=1.8))

    render(os.path.join(OUT, "aead-tuple-flow.svg"), W, H, *p)


# ── 3. ghash-pipeline: конвеєр обчислення тегу та шифрування в AES-GCM ─────────
def fig_ghash_pipeline():
    W, H = 1080, 520
    p = []

    p.append(text(W / 2, 30, "Конвеєр AES-GCM: паралельний CTR-шифр та поліноміальний GHASH", size=16, color=INK, bold=True))

    # Верхній рівень: генерація підключа H та лічильників
    p.append(fitbox(50, 65, 210, 50, "Секретний ключ K", size=13, fill=MACF, stroke=MAC, sw=1.5))
    p.append(fitbox(320, 65, 200, 50, "Хеш-підключ H\nH = AES_K(0¹²⁸)", size=12, fill=ACCF, stroke=ACC, sw=1.5))
    p.append(fitbox(600, 65, 200, 50, "Початковий вектор J₀\nIV || 0³¹ || 1", size=12, fill=WARNF, stroke=WARN, sw=1.5))
    p.append(fitbox(850, 65, 180, 50, "Маска тегу\nS₀ = AES_K(J₀)", size=12, fill=ENCF, stroke=ENC, sw=1.5))

    p.append(arrow(265, 90, 315, 90, color=MAC, sw=1.5))
    p.append(arrow(525, 90, 595, 90, color=LINE, sw=1.5))
    p.append(arrow(805, 90, 845, 90, color=ENC, sw=1.5))

    # Середній рівень: блоки AAD, Ciphertext та довжин
    p.append(fitbox(50, 165, 180, 55, "Блок AAD: A₁\n(128 бітів)", size=12, fill=CLRF, stroke=CLR, sw=1.5))
    p.append(fitbox(290, 165, 180, 55, "Блок AAD: A_m\n(128 бітів)", size=12, fill=CLRF, stroke=CLR, sw=1.5))
    p.append(fitbox(530, 165, 180, 55, "Ciphertext: C₁\nP₁ ⊕ AES_K(J₁)", size=12, fill=ENCF, stroke=ENC, sw=1.5))
    p.append(fitbox(770, 165, 180, 55, "Блок довжин\nlen(A) || len(C)", size=12, fill=CLRF, stroke=CLR, sw=1.5))

    # Нижній рівень: ланцюг Горнера GHASH у GF(2¹²⁸)
    p.append(fitbox(50, 280, 180, 65, "Y₁ = A₁ · H\nу GF(2¹²⁸)", size=12, fill=ACCF, stroke=ACC, sw=1.5))
    p.append(fitbox(290, 280, 180, 65, "Y_m = (Y_{m-1} ⊕ A_m) · H\nу GF(2¹²⁸)", size=12, fill=ACCF, stroke=ACC, sw=1.5))
    p.append(fitbox(530, 280, 180, 65, "Y_{m+1} = (Y_m ⊕ C₁) · H\nу GF(2¹²⁸)", size=12, fill=ACCF, stroke=ACC, sw=1.5))
    p.append(fitbox(770, 280, 180, 65, "GHASH Результат Y_f\nФінальний поліном", size=12, fill=ACCF, stroke=ACC, sw=1.5))

    p.append(arrow(140, 225, 140, 275, color=CLR, sw=1.5))
    p.append(arrow(380, 225, 380, 275, color=CLR, sw=1.5))
    p.append(arrow(620, 225, 620, 275, color=ENC, sw=1.5))
    p.append(arrow(860, 225, 860, 275, color=CLR, sw=1.5))

    p.append(arrow(235, 312, 285, 312, color=ACC, sw=1.5))
    p.append(arrow(475, 312, 525, 312, color=ACC, sw=1.5))
    p.append(arrow(715, 312, 765, 312, color=ACC, sw=1.5))

    # Фінальне маскування тегу
    p.append(fitbox(400, 410, 280, 65, "Автентифікаційний тег T\nT = Y_f ⊕ AES_K(J₀)\n(128 бітів)", size=13, fill=OKF, stroke=OK, sw=1.8))

    p.append(arrow(860, 350, 685, 430, color=ACC, sw=1.8))
    p.append(arrow(940, 120, 685, 420, color=ENC, sw=1.8))

    render(os.path.join(OUT, "ghash-pipeline.svg"), W, H, *p)


# ── 4. nonce-reuse-catastrophe: колапс безпеки при повторі Nonce ───────────────
def fig_nonce_reuse_catastrophe():
    W, H = 1080, 480
    p = []

    p.append(text(W / 2, 30, "Катастрофічний колапс автентифікації та конфіденційності при повторі Nonce", size=16, color=INK, bold=True))

    # Ліва колонка: Повідомлення 1 та Повідомлення 2 з однаковим Nonce N
    p.append(fitbox(50, 75, 300, 75, "Пакет 1: Enc(K, N, A₁, P₁)\nC₁ = P₁ ⊕ KS(N)\nT₁ = GHASH_H(A₁, C₁) ⊕ AES_K(J₀)", size=12, fill=WARNF, stroke=WARN, sw=1.5))
    p.append(fitbox(50, 185, 300, 75, "Пакет 2: Enc(K, N, A₂, P₂)\nC₂ = P₂ ⊕ KS(N)   [той самий Nonce!]\nT₂ = GHASH_H(A₂, C₂) ⊕ AES_K(J₀)", size=12, fill=WARNF, stroke=WARN, sw=1.5))

    # Центральні наслідки
    p.append(fitbox(410, 75, 310, 85, "1. Витік відкритого тексту (Two-Time Pad)\nC₁ ⊕ C₂ = P₁ ⊕ P₂\nГамма повністю взаємознищується,\nрозкриваючи XOR відкритих даних", size=12, fill=ENCF, stroke=ENC, sw=1.6))
    p.append(fitbox(410, 185, 310, 95, "2. Знищення маски тегу\nT₁ ⊕ T₂ = GHASH_H(A₁, C₁) ⊕ GHASH_H(A₂, C₂)\nМаска AES_K(J₀) скоротилася!\nМаємо поліном від невідомого H", size=12, fill=ENCF, stroke=ENC, sw=1.6))

    p.append(arrow(355, 112, 405, 112, color=WARN, sw=1.6))
    p.append(arrow(355, 222, 405, 222, color=WARN, sw=1.6))

    # Фінальний фінал: Відновлення H та підробка будь-якого тегу
    p.append(fitbox(770, 115, 260, 140, "3. Відновлення ключа H\nЗнаходження коренів полінома\nу полі GF(2¹²⁸) дає підключ H.\n\nНаслідок:\nЗловмисник довільно підробляє\nтеги для будь-яких пакетів!", size=12, fill=ENCF, stroke=ENC, sw=2))

    p.append(arrow(725, 230, 765, 200, color=ENC, sw=1.8))

    # Нижній висновок: Як цьому запобігають
    p.append(fitbox(50, 360, 980, 80, "Захист у сучасних протоколах (TLS 1.3, WireGuard, QUIC):\n• Суворо монотонний 64-бітний лічильник sequence_number для кожного пакета (Nonce = IV_base ⊕ SeqNum).\n• Автоматичний розрив сесії / переузгодження ключів (rekeying) до досягнення ліміту лічильника.\n• Використання SIV-режимів (AES-GCM-SIV, RFC 8452), стійких до повтору одноразових чисел.", size=12, fill=OKF, stroke=OK, sw=1.6))

    render(os.path.join(OUT, "nonce-reuse-catastrophe.svg"), W, H, *p)


if __name__ == "__main__":
    fig_composition_paradigms()
    fig_aead_tuple_flow()
    fig_ghash_pipeline()
    fig_nonce_reuse_catastrophe()
    print("All figures generated successfully.")
