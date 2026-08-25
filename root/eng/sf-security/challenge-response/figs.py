# -*- coding: utf-8 -*-
"""Генератор векторних ілюстрацій для теми challenge-response."""

import sys
import os

# Імпортуємо svgkit із кореня репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_symmetric_vs_asymmetric():
    """Порівняння симетричної та асиметричної схеми виклик-відповідь."""
    w, h = 820, 420
    frags = []

    # Заголовок / розділення колонок
    frags.append(rect(15, 15, 385, 390, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(rect(420, 15, 385, 390, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))

    frags.append(text(207, 42, "Симетрична схема (CHAP / Digest)", size=15, bold=True, color=INK))
    frags.append(text(612, 42, "Асиметрична схема (SSH / TLS / FIDO2)", size=15, bold=True, color=INK))

    # Ліва колонка: Симетрія
    frags.append(fitbox(35, 65, 150, 60, "Клієнт (Prover)\nСпільний секрет K", size=12, bold=True, fill="#e8f4fd", stroke="#2457d6"))
    frags.append(fitbox(230, 65, 150, 60, "Сервер (Verifier)\nСпільний секрет K", size=12, bold=True, fill="#fdecea", stroke="#c0392b"))

    frags.append(arrow(230, 155, 185, 155, color="#c0392b", sw=1.8))
    frags.append(text(207, 145, "1. Challenge (nonce)", size=11, bold=True, color="#c0392b"))

    frags.append(arrow(185, 205, 230, 205, color="#2457d6", sw=1.8))
    frags.append(text(207, 195, "2. HMAC(K, nonce)", size=11, bold=True, color="#2457d6"))

    frags.append(rect(35, 240, 345, 145, fill="#ffffff", stroke="#d97706", sw=1.2, rx=6))
    frags.append(text(207, 262, "Вразливість сховища перевіряльника", size=12, bold=True, color="#d97706"))
    msg_sym = (
        "• Сервер зберігає спільний ключ K (або пароль)\n"
        "• Компрометація БД сервера розкриває облікові дані\n"
        "• Зловмисник може клонувати клієнта й автентифікуватися\n"
        "• Немає невідмовности: сервер може підробити відповідь"
    )
    frags.append(mtext(45, 282, msg_sym.split("\n"), size=11, color=INK, anchor="start", lh=1.35))

    # Права колонка: Асиметрія
    frags.append(fitbox(440, 65, 155, 60, "Клієнт (Prover)\nЗакритий ключ sk", size=12, bold=True, fill="#e8f4fd", stroke="#2457d6"))
    frags.append(fitbox(635, 65, 155, 60, "Сервер (Verifier)\nВідкритий ключ pk", size=12, bold=True, fill="#eafaf1", stroke="#27ae60"))

    frags.append(arrow(635, 155, 595, 155, color="#27ae60", sw=1.8))
    frags.append(text(615, 145, "1. Challenge (nonce)", size=11, bold=True, color="#27ae60"))

    frags.append(arrow(595, 205, 635, 205, color="#2457d6", sw=1.8))
    frags.append(text(615, 195, "2. Sign(sk, nonce)", size=11, bold=True, color="#2457d6"))

    frags.append(rect(440, 240, 350, 145, fill="#ffffff", stroke="#27ae60", sw=1.2, rx=6))
    frags.append(text(615, 262, "Ізоляція секрету на боці клієнта", size=12, bold=True, color="#27ae60"))
    msg_asym = (
        "• Сервер зберігає лише публічний ключ pk (публічні дані)\n"
        "• Злам сервера НЕ дає зловмиснику змоги увійти за клієнта\n"
        "• Закритий ключ sk захищений у Secure Enclave / TPM\n"
        "• Невідмовність: лише клієнт міг створити цифровий підпис"
    )
    frags.append(mtext(450, 282, msg_asym.split("\n"), size=11, color=INK, anchor="start", lh=1.35))

    render(os.path.join(IMG_DIR, "symmetric-vs-asymmetric-challenge.svg"), w, h, *frags)


def fig_schnorr_zkp():
    """Трикроковий протокол нульового розголошення Шнора (Sigma-protocol)."""
    w, h = 820, 430
    frags = []

    frags.append(rect(15, 15, 790, 400, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))

    frags.append(fitbox(45, 35, 230, 65, "Доводжувач (Alice / Prover)\nСекрет: x, Публічний: Y = g^x", size=12, bold=True, fill="#e8f4fd", stroke="#2457d6"))
    frags.append(fitbox(545, 35, 230, 65, "Перевіряльник (Bob / Verifier)\nЗнає лише відкритий ключ Y", size=12, bold=True, fill="#eafaf1", stroke="#27ae60"))

    frags.append(line(160, 105, 160, 395, color="#94a3b8", sw=1.5, dash="4,4"))
    frags.append(line(660, 105, 660, 395, color="#94a3b8", sw=1.5, dash="4,4"))

    # Крок 1: Commitment
    frags.append(rect(45, 120, 230, 48, fill="#ffffff", stroke="#2457d6", sw=1.2, rx=5))
    frags.append(text(160, 138, "Обирає випадковий v ∈ Zq", size=11, bold=False, color=INK))
    frags.append(text(160, 155, "Обчислює R = g^v mod p", size=11, bold=True, color="#2457d6"))

    frags.append(arrow(275, 150, 545, 150, color="#2457d6", sw=2.0))
    frags.append(text(410, 140, "1. Зобов'язання (Commitment) R", size=12, bold=True, color="#2457d6"))

    # Крок 2: Challenge
    frags.append(rect(545, 195, 230, 48, fill="#ffffff", stroke="#27ae60", sw=1.2, rx=5))
    frags.append(text(660, 213, "Генерує випадковий виклик", size=11, bold=False, color=INK))
    frags.append(text(660, 230, "c ∈ {0, ..., 2^t - 1}", size=11, bold=True, color="#27ae60"))

    frags.append(arrow(545, 225, 275, 225, color="#27ae60", sw=2.0))
    frags.append(text(410, 215, "2. Виклик (Challenge) c", size=12, bold=True, color="#27ae60"))

    # Крок 3: Response
    frags.append(rect(45, 270, 230, 48, fill="#ffffff", stroke="#2457d6", sw=1.2, rx=5))
    frags.append(text(160, 288, "Маскує секрет x викликом c:", size=11, bold=False, color=INK))
    frags.append(text(160, 305, "s = v + c·x mod q", size=11, bold=True, color="#2457d6"))

    frags.append(arrow(275, 300, 545, 300, color="#2457d6", sw=2.0))
    frags.append(text(410, 290, "3. Відповідь (Response) s", size=12, bold=True, color="#2457d6"))

    # Крок 4: Перевірка
    frags.append(rect(545, 340, 230, 55, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=5))
    frags.append(text(660, 358, "Перевірка рівності в групі:", size=11, bold=True, color="#d97706"))
    frags.append(text(660, 376, "g^s ≡ R · Y^c (mod p)", size=12, bold=True, color="#1e293b"))

    frags.append(rect(290, 340, 240, 55, fill="#f1f5f9", stroke="#64748b", sw=1.0, rx=5))
    frags.append(text(410, 358, "Zero-Knowledge інваріант:", size=10, bold=True, color="#475569"))
    frags.append(text(410, 375, "Секрет x надійно схований за v", size=10, color="#475569"))

    render(os.path.join(IMG_DIR, "schnorr-zkp-flow.svg"), w, h, *frags)


def fig_replay_and_mitm():
    """Вектори атак (Replay, MitM/Relay) та криптографічні механізми протидії."""
    w, h = 820, 440
    frags = []

    frags.append(rect(15, 15, 790, 410, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))

    # Верхня половина: Replay Attack vs Nonce Freshness
    frags.append(rect(30, 30, 760, 180, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(410, 52, "Захист від повтору (Replay Attack): Свіжість та Одноразовість виклику", size=13, bold=True, color=INK))

    frags.append(fitbox(45, 75, 170, 55, "Клієнт A\n(Генерує відповідь)", size=11, bold=True, fill="#e8f4fd", stroke="#2457d6"))
    frags.append(fitbox(320, 75, 170, 55, "Зловмисник (Eve)\nПерехоплює Resp(N1)", size=11, bold=True, fill="#fee2e2", stroke="#ef4444"))
    frags.append(fitbox(600, 75, 175, 55, "Сервер B\nВидає свіжий Nonce N2", size=11, bold=True, fill="#eafaf1", stroke="#27ae60"))

    frags.append(arrow(215, 102, 320, 102, color="#2457d6", sw=1.5))
    frags.append(arrow(490, 102, 600, 102, color="#ef4444", sw=1.5))
    frags.append(text(545, 92, "Повтор Resp(N1)", size=10, bold=True, color="#ef4444"))

    frags.append(rect(45, 145, 730, 52, fill="#ffffff", stroke="#27ae60", sw=1.0, rx=4))
    rep_text = (
        "Перевірка свіжості: Сервер очікує відповідь саме на N2. Стара відповідь на N1 не збігається з HMAC(K, N2).\n"
        "Стан перевіряльника: кеш використаних nonce з TTL або мітка часу + підпис HMAC (Stateless Nonce token)."
    )
    frags.append(mtext(410, 163, rep_text.split("\n"), size=10.5, color=INK, anchor="middle", lh=1.35))

    # Нижня половина: MitM / Relay Attack vs Channel & Origin Binding
    frags.append(rect(30, 225, 760, 185, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(410, 247, "Захист від посередника (MitM / Relay): Прив'язка до каналу й контексту", size=13, bold=True, color=INK))

    frags.append(fitbox(45, 270, 165, 55, "Легітимний клієнт\nПрагне зайти на bank.ua", size=11, bold=True, fill="#e8f4fd", stroke="#2457d6"))
    frags.append(fitbox(315, 270, 180, 55, "Фішинговий сайт (MitM)\nfake-bank.ua", size=11, bold=True, fill="#fee2e2", stroke="#ef4444"))
    frags.append(fitbox(600, 270, 175, 55, "Справжній банк\nbank.ua (Relying Party)", size=11, bold=True, fill="#eafaf1", stroke="#27ae60"))

    frags.append(arrow(210, 297, 315, 297, color="#2457d6", sw=1.5))
    frags.append(arrow(495, 297, 600, 297, color="#ef4444", sw=1.5))
    frags.append(text(548, 287, "Ретрансляція", size=10, bold=True, color="#ef4444"))

    frags.append(rect(45, 340, 730, 58, fill="#ffffff", stroke="#27ae60", sw=1.0, rx=4))
    mitm_text = (
        "Origin Binding (WebAuthn): Браузер укладає origin = 'fake-bank.ua' в clientDataJSON. Банк відхиляє підпис.\n"
        "Channel Binding (RFC 5929): Відповідь криптографічно зв'язується з хешем TLS-сертифіката сервера (tls-server-end-point)."
    )
    frags.append(mtext(410, 358, mitm_text.split("\n"), size=10.5, color=INK, anchor="middle", lh=1.35))

    render(os.path.join(IMG_DIR, "replay-and-mitm-defenses.svg"), w, h, *frags)


def fig_webauthn_assertion():
    """Життєвий цикл перевірки виклику у стандарті FIDO2 / WebAuthn."""
    w, h = 820, 420
    frags = []

    frags.append(rect(15, 15, 790, 390, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))

    frags.append(fitbox(35, 35, 190, 50, "Сервер (Relying Party)\nexample.com", size=12, bold=True, fill="#eafaf1", stroke="#27ae60"))
    frags.append(fitbox(315, 35, 190, 50, "Клієнт / Браузер\nUser Agent", size=12, bold=True, fill="#f8fafc", stroke="#64748b"))
    frags.append(fitbox(595, 35, 190, 50, "Автентифікатор (FIDO2)\nTPM / YubiKey / Enclave", size=12, bold=True, fill="#e8f4fd", stroke="#2457d6"))

    frags.append(line(130, 90, 130, 385, color="#94a3b8", sw=1.5, dash="4,4"))
    frags.append(line(410, 90, 410, 385, color="#94a3b8", sw=1.5, dash="4,4"))
    frags.append(line(690, 90, 690, 385, color="#94a3b8", sw=1.5, dash="4,4"))

    # Крок 1: Challenge
    frags.append(arrow(130, 120, 410, 120, color="#27ae60", sw=1.8))
    frags.append(text(270, 110, "1. getAssertion(challenge, rpId)", size=11, bold=True, color="#27ae60"))

    # Крок 2: Браузер збирає clientDataJSON
    frags.append(rect(290, 140, 240, 42, fill="#ffffff", stroke="#64748b", sw=1.0, rx=4))
    frags.append(text(410, 156, "clientDataJSON = {challenge,", size=10.5, color=INK))
    frags.append(text(410, 172, "origin: 'https://example.com'}", size=10.5, bold=True, color="#2457d6"))

    # Крок 3: Запит до апаратного ключа
    frags.append(arrow(410, 195, 690, 195, color="#64748b", sw=1.8))
    frags.append(text(550, 185, "2. SHA-256(clientDataJSON), rpId", size=10.5, bold=True, color="#64748b"))

    # Крок 4: Автентифікатор підписує
    frags.append(rect(570, 215, 230, 52, fill="#e8f4fd", stroke="#2457d6", sw=1.2, rx=4))
    frags.append(text(685, 233, "Тест присутності користувача (UP)", size=10.5, color="#1e293b"))
    frags.append(text(685, 252, "sig = Sign(sk, authData || hash)", size=10.5, bold=True, color="#2457d6"))

    # Крок 5: Відповідь назад браузеру
    frags.append(arrow(690, 280, 410, 280, color="#2457d6", sw=1.8))
    frags.append(text(550, 270, "3. authenticatorData, signature", size=10.5, bold=True, color="#2457d6"))

    # Крок 6: Відповідь серверу
    frags.append(arrow(410, 310, 130, 310, color="#2457d6", sw=1.8))
    frags.append(text(270, 300, "4. Assertion Response", size=11, bold=True, color="#2457d6"))

    # Крок 7: Верифікація на сервері
    frags.append(rect(35, 330, 190, 55, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
    frags.append(text(130, 348, "5. Перевірка:", size=10.5, bold=True, color="#d97706"))
    frags.append(text(130, 363, "• challenge збігається", size=10, color=INK))
    frags.append(text(130, 376, "• Verify(pk, signature)", size=10, bold=True, color="#1e293b"))

    render(os.path.join(IMG_DIR, "webauthn-assertion-flow.svg"), w, h, *frags)


def main():
    fig_symmetric_vs_asymmetric()
    fig_schnorr_zkp()
    fig_replay_and_mitm()
    fig_webauthn_assertion()
    print("Усі 4 фігури успішно згенеровано.")


if __name__ == "__main__":
    main()
