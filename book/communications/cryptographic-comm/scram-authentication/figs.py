#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Фігури до теми «SCRAM: солений виклик-відповідь замість дайджесту»."""

import os
import sys

# Шлях до scripts/ у корені репо (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# 1. Повний обмін SCRAM: два оберти, виведення та взаємна перевірка
def fig_scram_protocol_stages():
    W, H = 960, 560
    f = []

    # Заголовок
    f.append(text(W / 2.0, 30, "Повний протокольний обмін SCRAM (два оберти повідомлень)", size=16, bold=True))

    # Стовпці клієнта та сервера
    f.append(rect(40, 55, 230, 480, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    f.append(text(155, 80, "Клієнт (Client)", size=14, bold=True, color=NEG))
    f.append(text(155, 98, "Володіє паролем Password", size=11, color=MUTED))

    f.append(rect(690, 55, 230, 480, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    f.append(text(805, 80, "Сервер (Server)", size=14, bold=True, color=POS))
    f.append(text(805, 98, "База: Salt, i, StoredKey, ServerKey", size=11, color=MUTED))

    # Вертикальні лінії життя (розбиті на сегменти, щоб не перетинати блоки обробки)
    f.append(line(155, 115, 155, 290, color=MUTED, sw=1, dash="4,4"))
    f.append(line(155, 360, 155, 520, color=MUTED, sw=1, dash="4,4"))

    f.append(line(805, 115, 805, 190, color=MUTED, sw=1, dash="4,4"))
    f.append(line(805, 245, 805, 410, color=MUTED, sw=1, dash="4,4"))
    f.append(line(805, 480, 805, 520, color=MUTED, sw=1, dash="4,4"))

    # Повідомлення 1: Client-First
    f.append(arrow(155, 150, 800, 150, color=NEG, sw=2))
    b1, _, _ = textbox(480, 140, "1. client-first-message: n,,n=alice,r=r1_nonce", size=11, pad=6, fill="#eaf0fd", stroke=NEG, bold=True)
    f.append(b1)
    f.append(text(480, 172, "GS2-заголовок (n,,) + ім'я користувача alice + випадковий виклик r1", size=10, color=MUTED))

    # Обробка на сервері після повідомлення 1
    f.append(fitbox(700, 195, 210, 45, "Вибірка з БД за іменем:\nзнаходить Salt, i, StoredKey, ServerKey\nгенерує свій виклик r2", size=9, pad=4, fill="#ffffff", stroke=LINE))

    # Повідомлення 2: Server-First
    f.append(arrow(805, 260, 160, 260, color=POS, sw=2))
    b2, _, _ = textbox(480, 250, "2. server-first-message: r=r1_nonce||r2_nonce,s=salt,i=4096", size=11, pad=6, fill="#fdecea", stroke=POS, bold=True)
    f.append(b2)
    f.append(text(480, 282, "Об'єднаний виклик r1||r2 + сіль користувача s + число ітерацій i", size=10, color=MUTED))

    # Обчислення клієнта
    f.append(fitbox(50, 295, 210, 60, "SaltedPassword = PBKDF2(Pass, s, i)\nClientKey = HMAC(SaltedPass, 'Client Key')\nStoredKey = H(ClientKey)\nClientSig = HMAC(StoredKey, AuthMessage)\nClientProof = ClientKey XOR ClientSig", size=9, pad=4, fill="#ffffff", stroke=LINE))

    # Повідомлення 3: Client-Final
    f.append(arrow(155, 385, 800, 385, color=NEG, sw=2))
    b3, _, _ = textbox(480, 375, "3. client-final-message: c=biws,r=r1_nonce||r2_nonce,p=ClientProof", size=11, pad=6, fill="#eaf0fd", stroke=NEG, bold=True)
    f.append(b3)
    f.append(text(480, 407, "Канал зв'язку c=biws (Base64 'n,,') + виклик r + замаскований доказ p", size=10, color=MUTED))

    # Обробка та перевірка на сервері
    f.append(fitbox(700, 415, 210, 60, "ClientSig = HMAC(StoredKey, AuthMessage)\nClientKey' = ClientProof XOR ClientSig\nПеревірка: H(ClientKey') == StoredKey\nServerSig = HMAC(ServerKey, AuthMessage)", size=9, pad=4, fill="#ffffff", stroke=LINE))

    # Повідомлення 4: Server-Final
    f.append(arrow(805, 495, 160, 495, color=POS, sw=2))
    b4, _, _ = textbox(480, 485, "4. server-final-message: v=ServerSignature", size=11, pad=6, fill="#fdecea", stroke=POS, bold=True)
    f.append(b4)
    f.append(text(480, 517, "Підтвердження сервера v: клієнт перевіряє ServerSig == HMAC(ServerKey, AuthMessage)", size=10, color=MUTED))

    render(os.path.join(OUT, 'scram-protocol-stages.svg'), W, H, *f)


# 2. Дерево криптографічних перетворень SCRAM
def fig_scram_key_hierarchy():
    W, H = 960, 520
    f = []

    f.append(text(W / 2.0, 30, "Дерево виведення ключів та формування доказів у SCRAM", size=16, bold=True))

    # Корінь: Пароль, сіль, ітерації
    b_root, _, _ = textbox(480, 75, "Вхідні дані: Password + Salt + Iteration count (i)", size=13, pad=8, fill="#ffffff", stroke=LINE, bold=True)
    f.append(b_root)

    # Стрілка до PBKDF2
    f.append(arrow(480, 95, 480, 130, color=LINE, sw=1.8))
    f.append(text(545, 115, "PBKDF2-HMAC-SHA-256", size=10, color=MUTED))

    # SaltedPassword
    b_sp, _, _ = textbox(480, 150, "SaltedPassword = PBKDF2(Password, Salt, i, 32)", size=12, pad=7, fill="#fff2e6", stroke="#d35400", bold=True)
    f.append(b_sp)

    # Розгалуження на ClientKey та ServerKey
    f.append(arrow(410, 170, 240, 215, color=LINE, sw=1.8))
    f.append(text(285, 185, "HMAC(..., 'Client Key')", size=10, color=MUTED))

    f.append(arrow(550, 170, 720, 215, color=LINE, sw=1.8))
    f.append(text(675, 185, "HMAC(..., 'Server Key')", size=10, color=MUTED))

    # ClientKey та ServerKey
    b_ck, _, _ = textbox(240, 235, "ClientKey = HMAC(SaltedPassword, 'Client Key')", size=11, pad=6, fill="#eaf0fd", stroke=NEG, bold=True)
    f.append(b_ck)

    b_sk, _, _ = textbox(720, 235, "ServerKey = HMAC(SaltedPassword, 'Server Key')", size=11, pad=6, fill="#fdecea", stroke=POS, bold=True)
    f.append(b_sk)

    # Ліва гілка: StoredKey
    f.append(arrow(240, 258, 240, 305, color=LINE, sw=1.8))
    f.append(text(285, 282, "H = SHA-256", size=10, color=MUTED))

    b_stk, _, _ = textbox(240, 325, "StoredKey = SHA-256(ClientKey)", size=11, pad=6, fill="#e8f8f5", stroke=FIELD, bold=True)
    f.append(b_stk)

    # Рамка збереження на сервері
    f.append(rect(100, 355, 760, 45, fill="#f4f6f8", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(480, 375, "Зберігається в базі даних сервера: Salt, i, StoredKey, ServerKey", size=12, bold=True, color=FIELD))
    f.append(text(480, 392, "Сервер НЕ володіє Password, SaltedPassword та ClientKey (односторонній геш SHA-256)", size=10, color=MUTED))

    # Стрілка вниз до ClientSignature та ClientProof
    f.append(arrow(240, 400, 240, 435, color=LINE, sw=1.8))
    f.append(text(355, 418, "ClientSignature = HMAC(StoredKey, AuthMessage)", size=10, color=MUTED))

    b_cp, _, _ = textbox(240, 465, "ClientProof = ClientKey XOR ClientSignature\n(Надсилається клієнтом у мережу)", size=11, pad=6, fill="#eaf0fd", stroke=NEG, bold=True)
    f.append(b_cp)

    # Права гілка: ServerSignature
    f.append(arrow(720, 400, 720, 435, color=LINE, sw=1.8))
    f.append(text(720, 418, "HMAC над AuthMessage", size=10, color=MUTED))

    b_ss, _, _ = textbox(720, 465, "ServerSignature = HMAC(ServerKey, AuthMessage)\n(Надсилається сервером для взаємного доказу)", size=11, pad=6, fill="#fdecea", stroke=POS, bold=True)
    f.append(b_ss)

    render(os.path.join(OUT, 'scram-key-hierarchy.svg'), W, H, *f)


# 3. Порівняння моделей безпеки
def fig_scram_security_boundaries():
    W, H = 940, 480
    f = []

    f.append(text(W / 2.0, 30, "Порівняння моделей стійкості: Plaintext vs HTTP Digest vs SCRAM", size=16, bold=True))

    # Заголовки колонок
    col_w = 270
    f.append(rect(40, 60, col_w, 40, fill="#fdecea", stroke=POS, sw=1.2, rx=6))
    f.append(text(40 + col_w / 2.0, 85, "Відкритий пароль / CRAM-MD5", size=12, bold=True, color=POS))

    f.append(rect(335, 60, col_w, 40, fill="#fff2e6", stroke="#d35400", sw=1.2, rx=6))
    f.append(text(335 + col_w / 2.0, 85, "HTTP Digest (RFC 7616 / HA1)", size=12, bold=True, color="#d35400"))

    f.append(rect(630, 60, col_w, 40, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=6))
    f.append(text(630 + col_w / 2.0, 85, "SCRAM-SHA-256 (RFC 7677)", size=12, bold=True, color=FIELD))

    # Рядок 1: Збереження в базі даних сервера
    f.append(text(W / 2.0, 125, "Що зберігається в базі даних сервера?", size=12, bold=True))

    f.append(fitbox(40, 140, col_w, 85, "Зберігається відкритий пароль\n(CRAM-MD5 потребує його для HMAC)\n\nНаслідок витоку:\nМиттєвий повний компромат усіх акаунтів", size=10, pad=6, fill="#fff5f5", stroke=POS))

    f.append(fitbox(335, 140, col_w, 85, "Зберігається HA1 = MD5(user:realm:pass)\n(Геш без солі або зі слабким захистом)\n\nНаслідок витоку:\nPass-the-Hash: HA1 сам є ключем входу!", size=10, pad=6, fill="#fff9f5", stroke="#d35400"))

    f.append(fitbox(630, 140, col_w, 85, "Зберігаються Salt, i, StoredKey, ServerKey\n(StoredKey = SHA-256(ClientKey))\n\nНаслідок витоку:\nStoredKey НЕ дозволяє увійти клієнтом!", size=10, pad=6, fill="#f5fff9", stroke=FIELD))

    # Рядок 2: Перехоплення в мережі (Eavesdropping)
    f.append(text(W / 2.0, 245, "Що бачить зловмисник у мережевому трафіку?", size=12, bold=True))

    f.append(fitbox(40, 260, col_w, 85, "Plaintext: бачить чистий пароль.\nCRAM-MD5: бачить HMAC(Pass, Challenge).\n\nЗахист від перебору:\nШвидкий офлайн MD5-перебір за словником", size=10, pad=6, fill="#fff5f5", stroke=POS))

    f.append(fitbox(335, 260, col_w, 85, "Бачить nonce, cnonce, response.\n\nЗахист від перебору:\nОфлайн перебір одного раунду MD5/SHA-256\n(Мільйони гешів на секунду на GPU)", size=10, pad=6, fill="#fff9f5", stroke="#d35400"))

    f.append(fitbox(630, 260, col_w, 85, "Бачить nonces, salt, i, ClientProof.\n\nЗахист від перебору:\nОфлайн перебір вимагає i ітерацій PBKDF2\nдля кожного пароля-кандидата!", size=10, pad=6, fill="#f5fff9", stroke=FIELD))

    # Рядок 3: Взаємна автентифікація та MITM
    f.append(text(W / 2.0, 365, "Взаємна перевірка та стійкість до посередника (MITM)", size=12, bold=True))

    f.append(fitbox(40, 380, col_w, 85, "Взаємна автентифікація: Відсутня.\nСервер ніяк не доводить знання пароля.\n\nЗахист від MITM:\nПовністю відсутній", size=10, pad=6, fill="#fff5f5", stroke=POS))

    f.append(fitbox(335, 380, col_w, 85, "Взаємна автентифікація: Обмежена (rspauth).\nСкладна та рідко реалізована.\n\nЗахист від MITM:\nНемає зв'язування з каналом TLS", size=10, pad=6, fill="#fff9f5", stroke="#d35400"))

    f.append(fitbox(630, 380, col_w, 85, "Взаємна автентифікація: Вбудована (ServerSignature).\nСервер доводить володіння ServerKey.\n\nЗахист від MITM:\nSCRAM-PLUS з прив'язкою до каналу TLS (RFC 5929)", size=10, pad=6, fill="#f5fff9", stroke=FIELD))

    render(os.path.join(OUT, 'scram-security-boundaries.svg'), W, H, *f)


# 4. Прив'язка до каналу TLS (Channel Binding)
def fig_scram_channel_binding():
    W, H = 940, 440
    f = []

    f.append(text(W / 2.0, 30, "Прив'язка до каналу в SCRAM-SHA-256-PLUS (Channel Binding)", size=16, bold=True))

    # Верхній блок: Легітимне пряме з'єднання TLS
    f.append(rect(40, 60, 860, 160, fill="#f8fafc", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(70, 85, "Сценарій А: Пряме з'єднання клієнт ↔ сервер", size=12, bold=True, color=FIELD, anchor="start"))

    f.append(fitbox(60, 105, 200, 95, "Клієнт (Client)\nВитягує з TLS:\ntls-server-end-point\n= SHA-256(Сертифікат сервера)\ngs2-header: p=tls-server-end-point,,", size=9, pad=4, fill="#ffffff", stroke=NEG))

    f.append(arrow(270, 150, 660, 150, color=FIELD, sw=2))
    f.append(fitbox(300, 115, 330, 40, "TLS 1.3 Тунель (Сертифікат сервера CERT_A)\nAuthMessage містить hash(CERT_A)", size=10, pad=4, fill="#e8f8f5", stroke=FIELD))
    f.append(text(465, 175, "Обидві сторони мають однаковий hash(CERT_A) → Автентифікація успішна!", size=10, bold=True, color=FIELD))

    f.append(fitbox(680, 105, 200, 95, "Сервер (Server)\nВитягує з TLS:\ntls-server-end-point\n= SHA-256(Свій сертифікат CERT_A)\nПеревіряє gs2-header у AuthMessage", size=9, pad=4, fill="#ffffff", stroke=POS))

    # Нижній блок: Атака MITM (Перехоплювач із підміною сертифіката)
    f.append(rect(40, 245, 860, 175, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    f.append(text(70, 270, "Сценарій Б: Спроба перехоплення MITM (TLS-проксі розриває сесію)", size=12, bold=True, color=POS, anchor="start"))

    f.append(fitbox(60, 290, 190, 115, "Клієнт\nTLS-сесія 1 із MITM\nБачить підроблений CERT_MITM\ngs2-header містить:\nhash(CERT_MITM)\nAuthMessage_1", size=9, pad=4, fill="#ffffff", stroke=NEG))

    f.append(arrow(260, 345, 370, 345, color=POS, sw=2))
    f.append(text(315, 335, "TLS Сесія 1", size=9, color=MUTED))

    f.append(fitbox(380, 290, 180, 115, "Зловмисник (MITM)\nМає дві окремі сесії:\n1. Клієнт ↔ MITM (CERT_MITM)\n2. MITM ↔ Сервер (CERT_A)\nНе може змінити ClientProof!", size=9, pad=4, fill="#fdecea", stroke=POS))

    f.append(arrow(570, 345, 680, 345, color=POS, sw=2))
    f.append(text(625, 335, "TLS Сесія 2", size=9, color=MUTED))

    f.append(fitbox(690, 290, 190, 115, "Сервер\nTLS-сесія 2 із MITM\nОчікує в gs2-header:\nhash(CERT_A)\nОтримує ClientProof від AuthMessage_1:\nНЕСХОДЖЕННЯ! Відхилено!", size=9, pad=4, fill="#ffffff", stroke=POS))

    render(os.path.join(OUT, 'scram-channel-binding.svg'), W, H, *f)


if __name__ == '__main__':
    fig_scram_protocol_stages()
    fig_scram_key_hierarchy()
    fig_scram_security_boundaries()
    fig_scram_channel_binding()
    print("Всі 4 фігури згенеровано успішно.")
