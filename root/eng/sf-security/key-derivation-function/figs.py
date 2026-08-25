# -*- coding: utf-8 -*-
import sys
import os

# scripts/ directory is 4 levels up from root/eng/sf-security/key-derivation-function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. hkdf-extract-expand: Двоетапна парадигма HKDF (RFC 5869) ──────────────
def fig_hkdf_extract_expand():
    W, H = 880, 480
    p = []

    # Фонова панель
    p.append(rect(15, 15, 850, 450, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))

    # ── ЕТАП 1: EXTRACT ──
    p.append(rect(30, 30, 820, 160, fill="#f0f4f8", stroke=NEG, sw=1.5, rx=6))
    p.append(text(440, 52, "ФАЗА 1: HKDF-Extract (Вилучення рівномірної ентропії)", size=13, color=NEG, bold=True))

    # Входи: IKM та Salt
    b_ikm, _, _ = textbox(130, 95, "IKM (Вхідний секрет)\nНерівномірна ентропія\n(ECDH спільна точка)",
                          size=10, color=INK, fill="#ffffff", stroke=MUTED, sw=1.2, min_w=160)
    p.append(b_ikm)

    b_salt, _, _ = textbox(130, 155, "Salt (Випадкова сіль)\nОпціональна (CSPRNG)\nАбо нулі за замовчанням",
                           size=10, color=INK, fill="#ffffff", stroke=MUTED, sw=1.2, min_w=160)
    p.append(b_salt)

    # Стрілки до HMAC
    p.append(arrow(215, 95, 295, 115, color=NEG, sw=1.8))
    p.append(arrow(215, 155, 295, 135, color=NEG, sw=1.8))

    # Блок HMAC-Extract
    b_hmac_ext, _, _ = textbox(415, 125, "HMAC-Hash(Key = Salt, Data = IKM)\nВитягує непередбачуваність\nLeftover Hash Lemma",
                               size=11, color=NEG, fill="#ffffff", stroke=NEG, sw=1.8, bold=True, min_w=220)
    p.append(b_hmac_ext)

    # Вихід фази 1: PRK
    p.append(arrow(535, 125, 615, 125, color=NEG, sw=2.0))
    b_prk, _, _ = textbox(725, 125, "PRK (Pseudorandom Key)\nФіксована довжина HashLen\nРівномірний розподіл",
                          size=11, color=FIELD, fill="#eefaf0", stroke=FIELD, sw=1.8, bold=True, min_w=195)
    p.append(b_prk)

    # ── ПЕРЕХІД ──
    p.append(arrow(725, 160, 725, 210, color=FIELD, sw=2.0))

    # ── ЕТАП 2: EXPAND ──
    p.append(rect(30, 210, 820, 240, fill="#fdfdfd", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(440, 232, "ФАЗА 2: HKDF-Expand (Розгортання у робочі підключі потрібної довжини)", size=13, color=FIELD, bold=True))

    # Входи фази 2
    b_info, _, _ = textbox(130, 290, "info (Контекстний рядок)\n\"tls13 client write key\"\nРозділення доменів",
                           size=10, color=INK, fill="#ffffff", stroke=MUTED, sw=1.2, min_w=160)
    p.append(b_info)

    b_len, _, _ = textbox(130, 365, "L (Бажана довжина OKM)\nКількість потрібних байтів\nL ≤ 255 · HashLen",
                          size=10, color=INK, fill="#ffffff", stroke=MUTED, sw=1.2, min_w=160)
    p.append(b_len)

    # Ланцюг блоків T(i)
    # T(1)
    b_t1, _, _ = textbox(330, 310, "Блок T(1)\nHMAC(PRK,\n\"\" || info || 0x01)",
                         size=10, color=INK, fill="#ffffff", stroke=FIELD, sw=1.4, min_w=115)
    p.append(b_t1)

    # T(2)
    b_t2, _, _ = textbox(470, 310, "Блок T(2)\nHMAC(PRK,\nT(1) || info || 0x02)",
                         size=10, color=INK, fill="#ffffff", stroke=FIELD, sw=1.4, min_w=115)
    p.append(b_t2)

    # T(N)
    b_tn, _, _ = textbox(610, 310, "Блок T(N)\nHMAC(PRK,\nT(N-1) || info || byte(N))",
                         size=10, color=INK, fill="#ffffff", stroke=FIELD, sw=1.4, min_w=115)
    p.append(b_tn)

    # Стрілки ланцюга
    p.append(arrow(395, 310, 405, 310, color=FIELD, sw=1.5))
    p.append(line(535, 310, 545, 310, color=FIELD, sw=1.5, dash="2,2"))

    # Стрілки від PRK, info до блоків
    p.append(arrow(725, 210, 680, 275, color=FIELD, sw=1.4))
    p.append(arrow(215, 290, 265, 310, color=MUTED, sw=1.4))

    # Вихід OKM та підключі
    p.append(arrow(330, 345, 330, 395, color=FIELD, sw=1.5))
    p.append(arrow(470, 345, 470, 395, color=FIELD, sw=1.5))
    p.append(arrow(610, 345, 610, 395, color=FIELD, sw=1.5))

    b_okm, _, _ = textbox(470, 415, "OKM = Перші L байтів від ( T(1) || T(2) || ... || T(N) )\nІзольовані підключі: K_cipher (AES/ChaCha) + K_mac (Poly1305) + IV (Nonce)",
                          size=11, color=FIELD, fill="#eefaf0", stroke=FIELD, sw=1.8, bold=True, min_w=520)
    p.append(b_okm)

    render(os.path.join(OUT, "hkdf-extract-expand.svg"), W, H, *p,
           title="Парадигма Extract-then-Expand у HKDF (RFC 5869)")


# ── 2. tls13-key-schedule: Ланцюг виведення секретів у TLS 1.3 ───────────────
def fig_tls13_key_schedule():
    W, H = 860, 460
    p = []

    # Фонова панель
    p.append(rect(15, 15, 830, 430, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(430, 40, "Ланцюг виведення секретів і сесійних ключів у TLS 1.3 (RFC 8446)", size=14, color=INK, bold=True))

    # Стовпчик 1: Early Secret
    p.append(rect(35, 65, 240, 360, fill="#fdf4f4", stroke=POS, sw=1.5, rx=6))
    p.append(text(155, 88, "Фаза 0-RTT: Early Secret", size=12, color=POS, bold=True))

    b_e_in, _, _ = textbox(155, 125, "Вхід: PSK або 0\n(Попередній спільний ключ)",
                           size=10, color=INK, fill="#ffffff", stroke=MUTED, sw=1.2, min_w=200)
    p.append(b_e_in)

    p.append(arrow(155, 150, 155, 180, color=POS, sw=1.8))

    b_e_sec, _, _ = textbox(155, 205, "Early Secret\n= HKDF-Extract(0, PSK)",
                            size=11, color=POS, fill="#ffffff", stroke=POS, sw=1.5, bold=True, min_w=200)
    p.append(b_e_sec)

    p.append(arrow(155, 235, 155, 265, color=POS, sw=1.5))

    b_e_out, _, _ = textbox(155, 320, "Ключі ранніх даних (0-RTT):\n• client_early_traffic_secret\n• early_exporter_master_secret\n(Derive-Secret через HKDF-Expand)",
                            size=10, color=INK, fill="#ffffff", stroke=MUTED, sw=1.2, min_w=210)
    p.append(b_e_out)

    # Перехід до Handshake Secret
    p.append(arrow(260, 205, 315, 205, color=LINE, sw=1.8))
    p.append(text(287, 195, "Derive", size=9, color=MUTED))

    # Стовпчик 2: Handshake Secret
    p.append(rect(305, 65, 250, 360, fill="#f0f7ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(430, 88, "Фаза рукостискання: Handshake Secret", size=12, color=NEG, bold=True))

    b_hs_in, _, _ = textbox(430, 125, "Вхід: Спільний секрет ECDHE\n(Крива X25519 / P-256)",
                            size=10, color=INK, fill="#ffffff", stroke=MUTED, sw=1.2, min_w=210)
    p.append(b_hs_in)

    p.append(arrow(430, 150, 430, 180, color=NEG, sw=1.8))

    b_hs_sec, _, _ = textbox(430, 205, "Handshake Secret\n= HKDF-Extract(derived_e, ECDHE)",
                             size=11, color=NEG, fill="#ffffff", stroke=NEG, sw=1.5, bold=True, min_w=210)
    p.append(b_hs_sec)

    p.append(arrow(430, 235, 430, 265, color=NEG, sw=1.5))

    b_hs_out, _, _ = textbox(430, 320, "Захист повідомлень Handshake:\n• client_handshake_traffic_secret\n• server_handshake_traffic_secret\n(Шифрування сертифікатів та Finished)",
                             size=10, color=INK, fill="#ffffff", stroke=MUTED, sw=1.2, min_w=225)
    p.append(b_hs_out)

    # Перехід до Master Secret
    p.append(arrow(560, 205, 605, 205, color=LINE, sw=1.8))
    p.append(text(582, 195, "Derive", size=9, color=MUTED))

    # Стовпчик 3: Master Secret
    p.append(rect(595, 65, 230, 360, fill="#eefaf0", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(710, 88, "Фаза трафіку: Master Secret", size=12, color=FIELD, bold=True))

    b_m_in, _, _ = textbox(710, 125, "Вхід: Нульовий IKM (0^HashLen)\n(Фіксація стека після автентифікації)",
                           size=10, color=INK, fill="#ffffff", stroke=MUTED, sw=1.2, min_w=195)
    p.append(b_m_in)

    p.append(arrow(710, 150, 710, 180, color=FIELD, sw=1.8))

    b_m_sec, _, _ = textbox(710, 205, "Master Secret\n= HKDF-Extract(derived_hs, 0)",
                            size=11, color=FIELD, fill="#ffffff", stroke=FIELD, sw=1.5, bold=True, min_w=195)
    p.append(b_m_sec)

    p.append(arrow(710, 235, 710, 265, color=FIELD, sw=1.5))

    b_m_out, _, _ = textbox(710, 320, "Трафік сесії та відновлення:\n• client_application_traffic_secret_0\n• server_application_traffic_secret_0\n• resumption_master_secret (квитки)",
                            size=10, color=INK, fill="#ffffff", stroke=MUTED, sw=1.2, min_w=205)
    p.append(b_m_out)

    render(os.path.join(OUT, "tls13-key-schedule.svg"), W, H, *p,
           title="Ланцюг виведення секретів у TLS 1.3")


# ── 3. kdf-memory-hardness: Спектр стійкості KDF до апаратного перебору ───────
def fig_kdf_memory_hardness():
    W, H = 860, 420
    p = []

    # Фонова панель
    p.append(rect(15, 15, 830, 390, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(430, 40, "Еволюція KDF для паролів: механізми стримування GPU та ASIC", size=14, color=INK, bold=True))

    # 4 блоки
    # 1. PBKDF2
    p.append(rect(30, 65, 190, 320, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    p.append(text(125, 90, "PBKDF2 (2000)", size=12, color=POS, bold=True))
    p.append(text(125, 110, "Ітерації CPU", size=10, color=MUTED))

    b_pbkdf_res, _, _ = textbox(125, 160, "Пам'ять: 0 байтів\n(Лише стан HMAC)\nОбчислення: CPU-bound",
                                size=10, color=INK, fill="#ffffff", stroke=MUTED, sw=1.2, min_w=165)
    p.append(b_pbkdf_res)

    b_pbkdf_atk, _, _ = textbox(125, 240, "Атака (ASIC / GPU):\nМасивний паралелізм.\nМільярди спроб/с.\nКонвеєр без затримок.",
                                size=9.5, color=POS, fill="#ffffff", stroke=POS, sw=1.2, min_w=165)
    p.append(b_pbkdf_atk)

    b_pbkdf_st, _, _ = textbox(125, 335, "Статус: Застарілий\n(Не захищає від ASIC)",
                               size=10, color=POS, fill="#fee2e2", stroke=POS, sw=1.4, bold=True, min_w=165)
    p.append(b_pbkdf_st)

    # 2. bcrypt
    p.append(rect(235, 65, 190, 320, fill="#fdfbf0", stroke="#d97706", sw=1.5, rx=6))
    p.append(text(330, 90, "bcrypt (1999)", size=12, color="#d97706", bold=True))
    p.append(text(330, 110, "Таблиці Blowfish", size=10, color=MUTED))

    b_bc_res, _, _ = textbox(330, 160, "Пам'ять: 4 КБ RAM\n(S-блоки Blowfish)\nВипадкові читання",
                             size=10, color=INK, fill="#ffffff", stroke=MUTED, sw=1.2, min_w=165)
    p.append(b_bc_res)

    b_bc_atk, _, _ = textbox(330, 240, "Атака (ASIC / GPU):\n4 КБ у L1 кеш або\nFPGA блочну пам'ять.\nGPU стають ефективнішими.",
                             size=9.5, color="#d97706", fill="#ffffff", stroke="#d97706", sw=1.2, min_w=165)
    p.append(b_bc_atk)

    b_bc_st, _, _ = textbox(330, 335, "Статус: Прийнятний\n(Але має ліміт 72 байти)",
                            size=10, color="#d97706", fill="#fef3c7", stroke="#d97706", sw=1.4, bold=True, min_w=165)
    p.append(b_bc_st)

    # 3. scrypt
    p.append(rect(440, 65, 190, 320, fill="#f0f7ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(535, 90, "scrypt (2009)", size=12, color=NEG, bold=True))
    p.append(text(535, 110, "ROMix (RAM-hard)", size=10, color=MUTED))

    b_sc_res, _, _ = textbox(535, 160, "Пам'ять: 16-128 МБ RAM\n(Великий буфер V)\nПсевдовипадкове читання",
                             size=10, color=INK, fill="#ffffff", stroke=MUTED, sw=1.2, min_w=165)
    p.append(b_sc_res)

    b_sc_atk, _, _ = textbox(535, 240, "Атака (ASIC / GPU):\nВимагає багато RAM.\nData-dependent доступ\nдозволяє компроміс TMTO.",
                             size=9.5, color=NEG, fill="#ffffff", stroke=NEG, sw=1.2, min_w=165)
    p.append(b_sc_atk)

    b_sc_st, _, _ = textbox(535, 335, "Статус: Стійкий\n(Висока вартість атак)",
                            size=10, color=NEG, fill="#dbeafe", stroke=NEG, sw=1.4, bold=True, min_w=165)
    p.append(b_sc_st)

    # 4. Argon2id
    p.append(rect(645, 65, 190, 320, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(740, 90, "Argon2id (2015)", size=12, color=FIELD, bold=True))
    p.append(text(740, 110, "Переможець PHC", size=10, color=MUTED))

    b_ar_res, _, _ = textbox(740, 160, "Пам'ять: 64-1024 МБ RAM\nМатриця блоків Blake2b\nБагатопотоковість",
                             size=10, color=INK, fill="#ffffff", stroke=MUTED, sw=1.2, min_w=165)
    p.append(b_ar_res)

    b_ar_atk, _, _ = textbox(740, 240, "Захист:\n• Data-indep 1-й прохід\n(проти side-channel витоків)\n• Data-dep решта фаз\n(проти GPU/ASIC і TMTO)",
                             size=9.5, color=FIELD, fill="#ffffff", stroke=FIELD, sw=1.2, min_w=165)
    p.append(b_ar_atk)

    b_ar_st, _, _ = textbox(740, 335, "Статус: Золотий стандарт\n(RFC 9106, рекомендовано)",
                            size=10, color=FIELD, fill="#dcfce7", stroke=FIELD, sw=1.4, bold=True, min_w=165)
    p.append(b_ar_st)

    render(os.path.join(OUT, "kdf-memory-hardness.svg"), W, H, *p,
           title="Еволюція KDF для паролів та захист від апаратного перебору")


if __name__ == "__main__":
    fig_hkdf_extract_expand()
    fig_tls13_key_schedule()
    fig_kdf_memory_hardness()
    print("Figures generated successfully.")
