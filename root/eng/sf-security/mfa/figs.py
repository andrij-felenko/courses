# -*- coding: utf-8 -*-
"""Фігури теми «Багатофакторна автентифікація (MFA)». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

REDFILL = "#fdecea"
GRNFILL = "#e7f6ec"
BLUFILL = "#eaf0fd"
AMBFILL = "#fef6e7"


# ── 1. Незалежність факторів: 2FA vs 2 кроки одного фактора ───────────────────
def fig_mfa_concept_independence():
    W, H = 1000, 440
    f = []

    # Заголовок блоків: Хибне 2FA (зліва) vs Справжнє MFA (справа)
    f.append(text(250, 35, "Хибний захист: 2 кроки одного фактора", size=15, color=POS, bold=True))
    f.append(text(750, 35, "Справжній захист: 2 різні фактори (MFA)", size=15, color=FIELD, bold=True))

    # Ліва колонка — Хибне 2FA
    b_pw1, _, _ = textbox(250, 95, "Крок 1: Пароль до акаунта\n(Фактор: знання)", size=13, fill=REDFILL, stroke=POS, sw=1.5, pad=12)
    b_pw2, _, _ = textbox(250, 205, "Крок 2: Дівоче прізвище матері / PIN\n(Фактор: знову знання!)", size=13, fill=REDFILL, stroke=POS, sw=1.5, pad=12)
    b_vuln, _, _ = textbox(250, 320, "Спільна вразливість:\nклавіатурний шпигун, фішинг\nабо витік бази краде обидва секрети", size=12, fill=FILL, stroke=MUTED, pad=10)
    
    f.append(b_pw1)
    f.append(arrow(250, 130, 250, 175))
    f.append(b_pw2)
    f.append(arrow(250, 240, 250, 285))
    f.append(b_vuln)
    f.append(minus(250, 395))
    f.append(text(250, 420, "Один злам знищує обидва бар'єри", size=12, color=POS, bold=True))

    # Розділювач
    f.append(line(500, 30, 500, 420, color=LINE, dash="4,4"))

    # Права колонка — Справжнє MFA
    b_f1, _, _ = textbox(750, 95, "Крок 1: Пароль до акаунта\n(Фактор: знання — у голові)", size=13, fill=BLUFILL, stroke=NEG, sw=1.5, pad=12)
    b_f2, _, _ = textbox(750, 205, "Крок 2: Одноразовий код TOTP / ключ\n(Фактор: володіння — фізичний пристрій)", size=13, fill=GRNFILL, stroke=FIELD, sw=1.5, pad=12)
    b_safe, _, _ = textbox(750, 320, "Ортогональні канали:\nвитік пароля з бази НЕ дає зловмиснику\nдоступу до мікросхеми в кишені", size=12, fill=FILL, stroke=MUTED, pad=10)

    f.append(b_f1)
    f.append(arrow(750, 130, 750, 175))
    f.append(b_f2)
    f.append(arrow(750, 240, 750, 285))
    f.append(b_safe)
    f.append(plus(750, 395))
    f.append(text(750, 420, "Для зламу потрібні дві різні атаки водночас", size=12, color=FIELD, bold=True))

    render(out("mfa-concept-independence.svg"), W, H, *f,
           title="Незалежність факторів: чому два паролі не створюють MFA")


# ── 2. Алгоритм TOTP (RFC 6238) ───────────────────────────────────────────────
def fig_totp_generation_flow():
    W, H = 1020, 400
    f = []

    # Вхідні дані зліва: Час і Секрет
    b_time, tw, _ = textbox(160, 90, "Поточний час Unix\nt = 1718928015 с\nКрок X = 30 с", size=12, fill=AMBFILL, stroke=LINE, pad=10)
    b_tcalc, _, _ = textbox(160, 190, "Лічильник кроків\nT = floor(t / 30)\n8 байтів Big-Endian", size=12, fill=BLUFILL, stroke=NEG, pad=10)
    b_secret, _, _ = textbox(160, 305, "Спільний секрет K\n(Base32 у сховищі)\n20 байтів випадковості", size=12, fill=BLUFILL, stroke=NEG, pad=10)

    f.append(b_time)
    f.append(arrow(160, 130, 160, 155))
    f.append(b_tcalc)
    f.append(b_secret)

    # Центральний блок — HMAC-SHA1 / SHA256
    b_hmac, hw, _ = textbox(470, 245, "HMAC-SHA-1(K, T)\nОднобічний криптографічний хеш\nРезультат: 20 байтів відбитка", size=13, fill=REDFILL, stroke=POS, sw=1.8, pad=14)
    f.append(b_hmac)

    f.append(arrow(160 + tw/2, 190, 470 - hw/2 - 6, 225))
    f.append(arrow(160 + tw/2, 305, 470 - hw/2 - 6, 265))

    # Справа — Динамічне усікання
    b_trunc, trw, _ = textbox(790, 130, "Динамічне усікання (Truncate)\n1. offset = байт[19] & 0x0F\n2. беремо 4 байти з offset\n3. скидаємо знаковий біт (P & 0x7FFFFFFF)", size=12, fill=GRNFILL, stroke=FIELD, pad=12)
    b_code, cw, _ = textbox(790, 290, "Шестизначний код\nCode = P mod 1 000 000\nРезультат: «482 910»\n(діє рівно 30 секунд)", size=14, fill=GRNFILL, stroke=FIELD, sw=2, pad=14)

    f.append(b_trunc)
    f.append(arrow(470 + hw/2, 225, 790 - trw/2 - 6, 150))
    f.append(arrow(790, 195, 790, 235))
    f.append(b_code)

    render(out("totp-generation-flow.svg"), W, H, *f,
           title="Генерація коду TOTP за RFC 6238: від часу до 6 цифр")


# ── 3. Вікно зсуву часу та захист від повтору ─────────────────────────────────
def fig_totp_drift_window():
    W, H = 1000, 360
    f = []

    # Три часові інтервали: T-1, T, T+1
    boxes = [
        ("Попередній крок (T − 1)\n[−30 с .. 0 с]\nдопуск відставання", 200, BLUFILL, NEG),
        ("Поточний крок (T)\n[0 с .. +30 с]\nідеальний збіг часу", 500, GRNFILL, FIELD),
        ("Наступний крок (T + 1)\n[+30 с .. +60 с]\nдопуск поспішання", 800, BLUFILL, NEG),
    ]

    for title, cx, bg, col in boxes:
        bx, bw, bh = textbox(cx, 110, title, size=13, fill=bg, stroke=col, sw=1.5, pad=12)
        f.append(bx)

    # Стрілка загального вікна
    f.append(arrow(80, 190, 920, 190, color=LINE, sw=1.5))
    f.append(text(500, 175, "Вікно валідації сервера: 3 кроки (90 секунд)", size=13, color=INK, bold=True))

    # Нижній блок: Захист від повтору (Anti-Replay)
    b_cache, _, _ = textbox(500, 275, "Таблиця погашених кроків (Redis / БД):\nSET mfa_used:user_123:step_57297600 EX 180\nПовторне надсилання того самого 6-значного коду в межах 90 с ВІДХИЛЯЄТЬСЯ", size=12, fill=AMBFILL, stroke=POS, sw=1.5, pad=12)
    f.append(b_cache)

    render(out("totp-drift-window.svg"), W, H, *f,
           title="Вікно зсуву годинника та реєстр використаних кодів для захисту від повтору")


# ── 4. Стан сесії на бекенді: перехід від mfa_pending до повної сесії ──────────
def fig_mfa_session_state_machine():
    W, H = 1020, 360
    f = []

    # Стан 1: Анонім
    s1, w1, _ = textbox(130, 180, "1. Анонімний гість\n(немає прав)", size=12, fill=FILL, stroke=LINE, pad=10)
    f.append(s1)

    # Стан 2: Тимчасовий жетон mfa_pending
    s2, w2, _ = textbox(480, 180, "2. Стан: mfa_pending\nТимчасовий жетон (TTL 5 хв)\nДозволено ТІЛЬКИ маршрут\nPOST /api/auth/mfa/verify", size=12, fill=AMBFILL, stroke=POS, sw=1.5, pad=12)
    f.append(s2)

    # Стан 3: Повна сесія
    s3, w3, _ = textbox(860, 180, "3. Повна сесія користувача\nВидано постійний Session ID / JWT\namr: [\"pwd\", \"totp\"]\nПовний доступ до системи", size=12, fill=GRNFILL, stroke=FIELD, sw=2, pad=12)
    f.append(s3)

    # Переходи
    f.append(arrow(130 + w1/2 + 6, 180, 480 - w2/2 - 6, 180, color=LINE, sw=1.5))
    f.append(text(285, 160, "POST /login\n(логін + пароль OK)", size=11, color=NEG))

    f.append(arrow(480 + w2/2 + 6, 180, 860 - w3/2 - 6, 180, color=FIELD, sw=2))
    f.append(text(670, 160, "POST /mfa/verify\n(TOTP або WebAuthn OK)", size=11, color=FIELD, bold=True))

    # Гілка відхилення / блокування
    b_fail, _, _ = textbox(480, 305, "3 невдалі спроби введення коду → тимчасове блокування (Rate Limit) + анулювання mfa_pending", size=11, fill=REDFILL, stroke=POS, pad=8)
    f.append(arrow(480, 235, 480, 280, color=POS))
    f.append(b_fail)

    render(out("mfa-session-state-machine.svg"), W, H, *f,
           title="Автомат станів автентифікації на бекенді: розділення етапів входу")


# ── 5. Фішинг-проксі (Evilginx) проти криптографічної прив'язки FIDO2 ─────────
def fig_phishing_mitm_vs_fido():
    W, H = 1000, 420
    f = []

    # Верхній блок: TOTP перед фішинг-посередником (AitM)
    f.append(text(500, 30, "Вразливість TOTP/SMS: Фішинг-посередник (Adversary-in-the-Middle)", size=14, color=POS, bold=True))
    
    b_u1, _, _ = textbox(160, 95, "Користувач\nвводить пароль і TOTP", size=12, fill=BLUFILL, stroke=NEG, pad=8)
    b_proxy, pw, _ = textbox(500, 95, "Фішинговий сайт (evil-login.com)\nПерехоплює пароль і TOTP\nі миттєво пересилає на справжній сайт", size=12, fill=REDFILL, stroke=POS, sw=1.5, pad=10)
    b_srv1, _, _ = textbox(840, 95, "Справжній сервер\nПриймає валідний TOTP\nі віддає сесію хакеру!", size=12, fill=REDFILL, stroke=POS, pad=8)

    f.append(b_u1)
    f.append(arrow(160 + 80, 95, 500 - pw/2 - 6, 95))
    f.append(b_proxy)
    f.append(arrow(500 + pw/2 + 6, 95, 840 - 80, 95))
    f.append(b_srv1)

    # Розділювач
    f.append(line(50, 175, 950, 175, color=LINE, dash="4,4"))

    # Нижній блок: FIDO2 / WebAuthn — стійкість до фішингу через Origin Binding
    f.append(text(500, 210, "Захист FIDO2/Passkeys: Криптографічна прив'язка до домену (Origin Binding)", size=14, color=FIELD, bold=True))

    b_u2, _, _ = textbox(160, 295, "Браузер користувача\nна домені evil-login.com\nпередає origin у ключ", size=12, fill=BLUFILL, stroke=NEG, pad=8)
    b_key, kw, _ = textbox(500, 295, "Апаратний ключ / Passkey\nПідписує challenge разом із\nхешем домену: SHA256(\"evil-login.com\")", size=12, fill=GRNFILL, stroke=FIELD, sw=1.5, pad=10)
    b_srv2, _, _ = textbox(840, 295, "Справжній сервер (bank.com)\nЗвіряє RP ID у підписі:\n\"evil-login.com\" != \"bank.com\" → ВІДХИЛЕНО", size=12, fill=GRNFILL, stroke=FIELD, sw=1.5, pad=10)

    f.append(b_u2)
    f.append(arrow(160 + 80, 295, 500 - kw/2 - 6, 295))
    f.append(b_key)
    f.append(arrow(500 + kw/2 + 6, 295, 840 - 80, 295))
    f.append(b_srv2)

    render(out("phishing-mitm-vs-fido.svg"), W, H, *f,
           title="Чому TOTP вразливий до фішинг-проксі, а FIDO2/WebAuthn зупиняє їх підписом походження")


if __name__ == "__main__":
    fig_mfa_concept_independence()
    fig_totp_generation_flow()
    fig_totp_drift_window()
    fig_mfa_session_state_machine()
    fig_phishing_mitm_vs_fido()
    print("All MFA figures generated successfully.")
