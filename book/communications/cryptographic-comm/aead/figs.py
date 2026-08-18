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
WARN  = "#d97706"     # попередження / пробиття
WARNF = "#fef3c7"
CLR   = "#4b5563"     # відкриті дані / AAD
CLRF  = "#f3f4f6"


# ── 1. composition-models: чотири підходи до поєднання шифрування й автентичності ──
def fig_composition_models():
    W, H = 1060, 520
    p = []

    # Заголовок зверху
    p.append(text(W / 2, 32, "Чотири архітектурні парадигми захисту повідомлення", size=16, color=INK, bold=True))

    cols = [
        (140, "Encrypt-and-MAC", "SSH-1",
         [("Відкритий текст P", CLRF, CLR),
          ("C = Enc(P)\nT = MAC(P)", ENCF, ENC),
          ("Вразливість:\nвитік рівності P\nчерез детермінований MAC", WARNF, WARN)]),

        (390, "MAC-then-Encrypt", "SSL 3.0 / TLS 1.0–1.2",
         [("Відкритий текст P", CLRF, CLR),
          ("P' = P || MAC(P)\nC = Enc(P' || Pad)", ENCF, ENC),
          ("Вразливість:\nPadding Oracle,\nLucky 13, POODLE", WARNF, WARN)]),

        (640, "Encrypt-then-MAC", "IPsec ESP / TLS 1.2 EtM",
         [("Відкритий текст P", CLRF, CLR),
          ("C = Enc(P)\nT = MAC(AAD || C)", OKF, OK),
          ("Стійкий, але вимагає\n2 проходів, 2 ключів\nі ручної збірки", CLRF, CLR)]),

        (890, "Інтегрований AEAD", "AES-GCM / ChaCha20-Poly",
         [("Plaintext P + AAD", CLRF, CLR),
          ("(C, T) = AEAD_Enc(K, N, A, P)", OKF, OK),
          ("Єдиний чорний ящик:\n1 прохід, захист AAD,\nнеможливість розшифрувати до T", OKF, OK)]),
    ]

    for cx, title, subtitle, boxes in cols:
        p.append(rect(cx - 110, 60, 220, 440, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
        p.append(text(cx, 84, title, size=13, color=INK, bold=True))
        p.append(text(cx, 102, subtitle, size=11, color=MUTED, italic=True))

        # Блоки всередині колонки
        y_pos = [125, 230, 370]
        for i, (txt, fill_c, strk_c) in enumerate(boxes):
            p.append(fitbox(cx - 95, y_pos[i], 190, 84, txt, size=12, fill=fill_c, stroke=strk_c, sw=1.5))
            if i < 2:
                p.append(arrow(cx, y_pos[i] + 88, cx, y_pos[i + 1] - 4, color=LINE, sw=1.5))

    render(os.path.join(OUT, "composition-models.svg"), W, H, *p)


# ── 2. aead-frame-anatomy: анатомія параметрів AEAD та захисний бар'єр ───────────
def fig_aead_frame_anatomy():
    W, H = 1060, 460
    p = []

    p.append(text(W / 2, 30, "Анатомія параметрів AEAD та бар'єр верифікації", size=16, color=INK, bold=True))

    # Вхідні параметри
    p.append(fitbox(50, 70, 210, 50, "Секретний ключ K\n(128 або 256 бітів)", size=13, fill=MACF, stroke=MAC, sw=1.6))
    p.append(fitbox(50, 140, 210, 50, "Одноразове число Nonce N\n(96 бітів, унікальне!)", size=13, fill=WARNF, stroke=WARN, sw=1.6))
    p.append(fitbox(50, 210, 210, 50, "Асоційовані дані AAD (A)\n(заголовки, незашифровані)", size=13, fill=CLRF, stroke=CLR, sw=1.6))
    p.append(fitbox(50, 280, 210, 50, "Відкритий текст Plaintext (P)\n(корисне навантаження)", size=13, fill=OKF, stroke=OK, sw=1.6))

    # Центральний блок AEAD
    p.append(fitbox(340, 130, 260, 150, "Інтегрований примітив\nAEAD Encrypt\n(AES-GCM / ChaCha20-Poly1305)\n\nОдночасне шифрування\nта криптографічний доказ", size=13, fill="#ffffff", stroke=INK, sw=2))

    p.append(arrow(265, 95, 335, 155, color=MAC, sw=1.8))
    p.append(arrow(265, 165, 335, 180, color=WARN, sw=1.8))
    p.append(arrow(265, 235, 335, 215, color=CLR, sw=1.8))
    p.append(arrow(265, 305, 335, 245, color=OK, sw=1.8))

    # Вихідний кадр
    p.append(text(800, 75, "Структура захищеного мережевого кадру", size=13, color=INK, bold=True))
    p.append(fitbox(670, 95, 260, 42, "AAD: Заголовок пакета (відкритий)", size=12, fill=CLRF, stroke=CLR, sw=1.5))
    p.append(fitbox(670, 145, 260, 52, "Ciphertext C: Зашифроване тіло\n(довжина дорівнює P)", size=12, fill=ENCF, stroke=ENC, sw=1.6))
    p.append(fitbox(670, 205, 260, 45, "Tag T: Автентифікаційний тег\n(16 байтів / 128 бітів)", size=12, fill=MACF, stroke=MAC, sw=1.6))

    p.append(arrow(605, 180, 665, 120, color=CLR, sw=1.8))
    p.append(arrow(605, 205, 665, 170, color=ENC, sw=1.8))
    p.append(arrow(605, 230, 665, 225, color=MAC, sw=1.8))

    # Нижній бар'єр перевірки
    p.append(fitbox(50, 370, 960, 70, "Бар'єр дешифрування (Decryption Barrier):\nЯкщо Tag не зійшовся хоча б в одному біті — все повідомлення негайно відкидається (⊥).\nЖоден байт Plaintext НЕ повертається у відкритий доступ до повної верифікації тегу!", size=13, fill=OKF, stroke=OK, sw=1.8))

    render(os.path.join(OUT, "aead-frame-anatomy.svg"), W, H, *p)


# ── 3. aes-gcm-pipeline: конвеєр обчислень у режимі AES-GCM ──────────────────────
def fig_aes_gcm_pipeline():
    W, H = 1080, 560
    p = []

    p.append(text(W / 2, 28, "Архітектура та конвеєр режиму AES-GCM (NIST SP 800-38D)", size=16, color=INK, bold=True))

    # Ключ H
    p.append(fitbox(50, 60, 220, 50, "Хеш-ключ Галуа:\nH = AES_K(0¹²⁸)", size=13, fill=MACF, stroke=MAC, sw=1.6))

    # CTR гілка
    p.append(fitbox(340, 60, 180, 50, "Лічильник CTR:\nY₀ = Nonce || 1", size=13, fill=WARNF, stroke=WARN, sw=1.6))
    p.append(fitbox(550, 60, 180, 50, "Блоки CTR:\nY₁, Y₂, ..., Yₙ", size=13, fill=WARNF, stroke=WARN, sw=1.6))

    p.append(fitbox(550, 140, 180, 45, "AES_K(Yᵢ) (шифрогамма)", size=13, fill=ENCF, stroke=ENC, sw=1.5))
    p.append(arrow(640, 115, 640, 135, color=LINE, sw=1.5))

    p.append(fitbox(790, 140, 210, 45, "Plaintext (P₁, P₂, ...)", size=13, fill=OKF, stroke=OK, sw=1.5))
    p.append(fitbox(670, 220, 240, 50, "Ciphertext Cᵢ = Pᵢ ⊕ AES_K(Yᵢ)", size=13, fill=ENCF, stroke=ENC, sw=1.8))

    p.append(arrow(640, 190, 740, 215, color=LINE, sw=1.5))
    p.append(arrow(890, 190, 810, 215, color=LINE, sw=1.5))

    # GHASH гілка
    p.append(fitbox(50, 220, 220, 50, "AAD (A₁, A₂, ...)\nдоповнені нулями до 16 Б", size=13, fill=CLRF, stroke=CLR, sw=1.5))
    p.append(fitbox(50, 310, 220, 50, "Блок довжин:\nlen(A) || len(C)", size=13, fill=CLRF, stroke=CLR, sw=1.5))

    # Центральний блок GHASH
    p.append(fitbox(340, 240, 250, 140, "Функція GHASH над GF(2¹²⁸):\nS = (...((A₁·H ⊕ A₂)·H ⊕ ...\n  ... ⊕ C₁)·H ⊕ ... ⊕ len)·H\n\nНезвідний поліном:\nf(x) = x¹²⁸ + x⁷ + x² + x + 1", size=12, fill=MACF, stroke=MAC, sw=2))

    p.append(arrow(160, 115, 370, 235, color=MAC, sw=1.6))
    p.append(arrow(275, 245, 335, 275, color=CLR, sw=1.6))
    p.append(arrow(665, 250, 595, 285, color=ENC, sw=1.6))
    p.append(arrow(275, 335, 335, 335, color=CLR, sw=1.6))

    # Фінальна маска тегу
    p.append(fitbox(340, 420, 180, 50, "Маска тегу:\nAES_K(Y₀)", size=13, fill=ENCF, stroke=ENC, sw=1.6))
    p.append(arrow(430, 115, 430, 415, color=LINE, sw=1.5))

    p.append(fitbox(640, 420, 280, 50, "Автентифікаційний тег:\nTag T = GHASH(...) ⊕ AES_K(Y₀)", size=13, fill=OKF, stroke=OK, sw=2))

    p.append(arrow(595, 350, 710, 415, color=MAC, sw=1.8))
    p.append(arrow(525, 445, 635, 445, color=ENC, sw=1.8))

    # Нижня плашка
    p.append(fitbox(50, 500, 980, 44, "Апаратне прискорення: Інструкції AES-NI для шифрування лічильника та PCLMULQDQ / PMULL для множення в полі GF(2¹²⁸)", size=12, fill=FILL, stroke=LINE, sw=1.4))

    render(os.path.join(OUT, "aes-gcm-pipeline.svg"), W, H, *p)


# ── 4. chacha20-poly1305-pipeline: конвеєр ChaCha20-Poly1305 ────────────────────
def fig_chacha20_poly1305_pipeline():
    W, H = 1080, 540
    p = []

    p.append(text(W / 2, 28, "Конвеєр та генерація одноразового ключа в ChaCha20-Poly1305 (RFC 8439)", size=16, color=INK, bold=True))

    # Входи
    p.append(fitbox(60, 60, 240, 50, "Key (256b) + Nonce (96b)\nСпільні секретні параметри", size=13, fill=WARNF, stroke=WARN, sw=1.6))

    # Блок 0 і Блоки 1..N
    p.append(fitbox(380, 60, 260, 60, "ChaCha20 Блок 0 (Counter = 0)\nГенерує перші 64 байти гами", size=13, fill=FILL, stroke=LINE, sw=1.6))
    p.append(arrow(305, 85, 375, 85, color=LINE, sw=1.6))

    p.append(fitbox(710, 60, 310, 60, "ChaCha20 Блоки 1..N (Counter ≥ 1)\nШифрують відкритий текст P ⊕ KeyStream", size=13, fill=ENCF, stroke=ENC, sw=1.8))
    p.append(arrow(305, 95, 705, 85, color=LINE, sw=1.6))

    # Одноразовий ключ Poly1305
    p.append(fitbox(380, 160, 260, 90, "Розподіл 64 байтів Блока 0:\n• Перші 16 Б → ключ r (затискається / clamped)\n• Наступні 16 Б → секрет s\n• Решта 32 Б відкидаються", size=12, fill=MACF, stroke=MAC, sw=1.8))
    p.append(arrow(510, 125, 510, 155, color=LINE, sw=1.6))

    # Шифротекст
    p.append(fitbox(710, 160, 310, 60, "Ciphertext C\n(тіло захищеного пакета)", size=13, fill=ENCF, stroke=ENC, sw=1.8))
    p.append(arrow(865, 125, 865, 155, color=ENC, sw=1.6))

    # Вхід AAD
    p.append(fitbox(60, 260, 240, 50, "AAD (асоційовані дані)\n(заголовки, pad16)", size=13, fill=CLRF, stroke=CLR, sw=1.5))

    # Обчислювач Poly1305
    p.append(fitbox(350, 280, 420, 130, "Автентифікатор Poly1305 за модулем 2¹³⁰ − 5:\n\nAcc = (...((pad(A)·r + pad(C))·r + len(A)||len(C))·r)\n      mod (2¹³⁰ − 5)\n\nФінальний тег T = (Acc + s) mod 2¹²⁸", size=12, fill=OKF, stroke=OK, sw=2))

    p.append(arrow(180, 315, 345, 335, color=CLR, sw=1.6))
    p.append(arrow(510, 255, 510, 275, color=MAC, sw=1.8))
    p.append(arrow(810, 225, 680, 275, color=ENC, sw=1.8))

    # Результат: Тег
    p.append(fitbox(820, 310, 200, 60, "16-байтовий тег T\n(Poly1305 Tag)", size=13, fill=OKF, stroke=OK, sw=2))
    p.append(arrow(775, 340, 815, 340, color=OK, sw=2))

    # Нижня плашка переваг
    p.append(fitbox(60, 450, 960, 60, "Перевага над AES-GCM: Абсолютно константний час виконання без табличних підстановок і без потреби в спеціальних апаратних інструкціях CPU. Виняткова стійкість до атак по сторонніх каналах (Side-Channel Attacks).", size=12, fill=FILL, stroke=LINE, sw=1.4))

    render(os.path.join(OUT, "chacha20-poly1305-pipeline.svg"), W, H, *p)


# ── 5. nonce-reuse-catastrophe: розкриття хеш-ключа H при колізії Nonce ─────────
def fig_nonce_reuse_catastrophe():
    W, H = 1060, 500
    p = []

    p.append(text(W / 2, 28, "Катастрофа повторного використання Nonce у GCM (Атака Джукса)", size=16, color=POS, bold=True))

    # Два повідомлення з однаковим Nonce
    p.append(fitbox(60, 70, 440, 80, "Повідомлення 1 (під Nonce N):\nC₁ = P₁ ⊕ AES_K(CTR₁)\nTag T₁ = GHASH(H, C₁) ⊕ AES_K(Y₀)", size=13, fill=WARNF, stroke=WARN, sw=1.6))

    p.append(fitbox(560, 70, 440, 80, "Повідомлення 2 (під ТИМ САМИМ Nonce N):\nC₂ = P₂ ⊕ AES_K(CTR₂)\nTag T₂ = GHASH(H, C₂) ⊕ AES_K(Y₀)", size=13, fill=WARNF, stroke=WARN, sw=1.6))

    # Почленне додавання (XOR)
    p.append(fitbox(230, 185, 600, 70, "Почленне віднімання / додавання тегів (XOR у GF(2¹²⁸)):\nT₁ ⊕ T₂ = GHASH(H, C₁) ⊕ GHASH(H, C₂)\nСпільна маска AES_K(Y₀) повністю скорочується!", size=13, fill=ENCF, stroke=ENC, sw=2))

    p.append(arrow(280, 155, 430, 180, color=POS, sw=1.8))
    p.append(arrow(780, 155, 630, 180, color=POS, sw=1.8))

    # Поліноміальне рівняння
    p.append(fitbox(150, 290, 760, 75, "Розкриття через многочлен у полі GF(2¹²⁸):\n(T₁ ⊕ T₂) = (C₁,₁ ⊕ C₂,₁)·H³ ⊕ (C₁,₂ ⊕ C₂,₂)·H² ⊕ (L₁ ⊕ L₂)·H\nОтримуємо многочлен P(H) = 0 відомого степеня від невідомого ключа H!", size=13, fill=MACF, stroke=MAC, sw=2))

    p.append(arrow(530, 260, 530, 285, color=LINE, sw=1.8))

    # Наслідки
    p.append(fitbox(60, 400, 440, 75, "1. Відновлення хеш-ключа H:\nЗнаходження коренів многочлена в GF(2¹²⁸)\nдає невелику кількість кандидатів на H", size=13, fill=WARNF, stroke=WARN, sw=1.8))

    p.append(fitbox(560, 400, 440, 75, "2. Повна фальсифікація (Universal Forgery):\nЗловмисник обчислює маску AES_K(Y₀) = T₁ ⊕ GHASH(H, C₁)\nі може підробити Tag для БУДЬ-ЯКОГО пакета!", size=13, fill=ENCF, stroke=ENC, sw=2))

    p.append(arrow(400, 370, 330, 395, color=POS, sw=1.8))
    p.append(arrow(660, 370, 730, 395, color=POS, sw=1.8))

    render(os.path.join(OUT, "nonce-reuse-catastrophe.svg"), W, H, *p)


fig_composition_models()
fig_aead_frame_anatomy()
fig_aes_gcm_pipeline()
fig_chacha20_poly1305_pipeline()
fig_nonce_reuse_catastrophe()
print("All figures generated successfully.")
