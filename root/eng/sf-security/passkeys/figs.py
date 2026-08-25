# -*- coding: utf-8 -*-
"""Фігури теми «Passkeys і WebAuthn». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

REDFILL = "#fdecea"
GRNFILL = "#e7f6ec"
BLUFILL = "#eaf0fd"


# ── 1. Стійкість до фішингу: чому origin binding ламає зворотний проксі ───────
def fig_phishing_resistance():
    W, H = 1000, 480
    f = []

    # Верхній блок: Класичний фішинг паролів / TOTP
    b_top_title, _, _ = textbox(500, 45, "Класичний пароль або TOTP: проксі перехоплює спільний секрет",
                                size=14, bold=True, fill=REDFILL, stroke=POS, sw=1.5, pad=10)
    f.append(b_top_title)

    # Жертва -> Фішинговий сервер -> Справжній банк
    b_u1, w_u1, _ = textbox(130, 120, "Користувач\nв браузері", size=12, fill=FILL, stroke=LINE, pad=8)
    f.append(b_u1)

    b_p1, w_p1, _ = textbox(500, 120, "Фішинговий сайт (evil-bank.com)\nЗворотний проксі пересилає дані", size=12, fill=REDFILL, stroke=POS, pad=8)
    f.append(b_p1)

    b_s1, w_s1, _ = textbox(870, 120, "Справжній банк (bank.com)\nПриймає пароль і пускає", size=12, fill=FILL, stroke=LINE, pad=8)
    f.append(b_s1)

    f.append(arrow(130 + w_u1 / 2 + 6, 120, 500 - w_p1 / 2 - 6, 120, color=POS))
    f.append(text(315, 105, "пароль + SMS / TOTP", size=11, color=POS, bold=True))

    f.append(arrow(500 + w_p1 / 2 + 6, 120, 870 - w_s1 / 2 - 6, 120, color=POS))
    f.append(text(685, 105, "ретрансляція в банк", size=11, color=POS, bold=True))

    b_res1, _, _ = textbox(500, 180, "Крадіжка сесії успішна: секрет валідний на bank.com, бо він не прив'язаний до домену",
                           size=11, fill=REDFILL, stroke=POS, sw=1, pad=8)
    f.append(b_res1)

    # Розділювальна лінія
    f.append(line(50, 225, 950, 225, color=MUTED, sw=1, dash="4,4"))

    # Нижній блок: WebAuthn / Passkeys
    b_bot_title, _, _ = textbox(500, 265, "WebAuthn / Passkeys: браузер криптографічно підписує домен із адресного рядка",
                                size=14, bold=True, fill=GRNFILL, stroke=FIELD, sw=1.5, pad=10)
    f.append(b_bot_title)

    b_u2, w_u2, _ = textbox(130, 345, "Користувач\nна evil-bank.com", size=12, fill=FILL, stroke=LINE, pad=8)
    f.append(b_u2)

    b_p2, w_p2, _ = textbox(500, 345, "Фішинговий сайт (evil-bank.com)\nОтримує підпис для evil-bank.com", size=12, fill=REDFILL, stroke=POS, pad=8)
    f.append(b_p2)

    b_s2, w_s2, _ = textbox(870, 345, "Справжній банк (bank.com)\nОчікує origin: bank.com", size=12, fill=GRNFILL, stroke=FIELD, pad=8)
    f.append(b_s2)

    f.append(arrow(130 + w_u2 / 2 + 6, 345, 500 - w_p2 / 2 - 6, 345, color=LINE))
    f.append(text(315, 330, "підпис(origin=evil-bank.com)", size=11, color=LINE, bold=True))

    f.append(arrow(500 + w_p2 / 2 + 6, 345, 870 - w_s2 / 2 - 6, 345, color=POS))
    f.append(text(685, 330, "спроба підставити підпис", size=11, color=POS, bold=True))

    b_res2, _, _ = textbox(500, 425, "Банк відхиляє запит: origin не збігається з bank.com, а підробити підпис для bank.com фішер не може",
                           size=11, fill=GRNFILL, stroke=FIELD, sw=1.5, bold=True, pad=8)
    f.append(b_res2)

    render(out("phishing-resistance.svg"), W, H, *f,
           title="Прив'язка до походження (Origin Binding): захист від фішингу на рівні криптографії")


# ── 2. Церемонія реєстрації WebAuthn ──────────────────────────────────────────
def fig_registration_ceremony():
    W, H = 1000, 520
    f = []

    # Три колонки: Користувач/Автентифікатор, Браузер (Клієнт), Сервер (Relying Party)
    cx_auth, cx_br, cx_rp = 150, 500, 850

    b_a, _, ha = textbox(cx_auth, 65, "Автентифікатор\n(Secure Enclave / YubiKey)", size=13, bold=True, fill=BLUFILL, stroke=NEG, pad=10)
    b_b, _, hb = textbox(cx_br, 65, "Браузер (User Agent)\nWebAuthn API", size=13, bold=True, fill=FILL, stroke=LINE, pad=10)
    b_r, _, hr = textbox(cx_rp, 65, "Бекенд (Relying Party)\nСервер застосунку", size=13, bold=True, fill=GRNFILL, stroke=FIELD, pad=10)
    f.extend([b_a, b_b, b_r])

    # Крок 4: Локальна верифікація та генерація пари ключів
    b_act, _, ha_act = textbox(cx_auth, 275, "Біометрія / PIN\nГенерує пару ключів\n(PubKey, PrivKey)", size=11, fill=BLUFILL, stroke=NEG, pad=6)

    # Крок 7: Серверна перевірка та збереження
    b_srv, _, hs_act = textbox(cx_rp, 440, "Звіряє challenge й origin\nВитягує PubKey з COSE\nЗберігає (credId, PubKey, 0)", size=11, fill=GRNFILL, stroke=FIELD, pad=6)

    # Вертикальні лінії життя (розриваємо, щоб не перетинали блоки дії)
    y_top = 65 + ha / 2 + 6
    f.append(line(cx_auth, y_top, cx_auth, 275 - ha_act / 2 - 4, color=MUTED, sw=1.2, dash="4,4"))
    f.append(line(cx_auth, 275 + ha_act / 2 + 4, cx_auth, 490, color=MUTED, sw=1.2, dash="4,4"))

    f.append(line(cx_br, y_top, cx_br, 490, color=MUTED, sw=1.2, dash="4,4"))

    f.append(line(cx_rp, y_top, cx_rp, 440 - hs_act / 2 - 4, color=MUTED, sw=1.2, dash="4,4"))
    f.append(line(cx_rp, 440 + hs_act / 2 + 4, cx_rp, 490, color=MUTED, sw=1.2, dash="4,4"))

    # Крок 1: Запит реєстрації
    f.append(arrow(cx_br, 135, cx_rp, 135, color=LINE))
    f.append(text((cx_br + cx_rp) / 2, 123, "1. POST /register/start (пошта / логін)", size=11, color=INK))

    # Крок 2: Опції з челенджем
    f.append(arrow(cx_rp, 175, cx_br, 175, color=FIELD))
    f.append(text((cx_br + cx_rp) / 2, 163, "2. Challenge (32 байти) + rpId + userId + algs", size=11, color=FIELD, bold=True))

    # Крок 3: create() виклик до автентифікатора
    f.append(arrow(cx_br, 215, cx_auth, 215, color=NEG))
    f.append(text((cx_auth + cx_br) / 2, 203, "3. navigator.credentials.create()", size=11, color=NEG, bold=True))

    # Додаємо блок дії автентифікатора
    f.append(b_act)

    # Крок 5: Відповідь автентифікатора браузеру
    f.append(arrow(cx_auth, 335, cx_br, 335, color=NEG))
    f.append(text((cx_auth + cx_br) / 2, 323, "5. authData (PubKey) + Attestation", size=11, color=NEG))

    # Крок 6: Відправка на сервер
    f.append(arrow(cx_br, 385, cx_rp, 385, color=LINE))
    f.append(text((cx_br + cx_rp) / 2, 373, "6. POST /register/finish (clientDataJSON + attestationObject)", size=11, color=INK, bold=True))

    # Додаємо блок дії сервера
    f.append(b_srv)

    render(out("registration-ceremony.svg"), W, H, *f,
           title="Церемонія реєстрації: створення пари ключів і збереження відкритого ключа")


# ── 3. Церемонія автентифікації WebAuthn ──────────────────────────────────────
def fig_authentication_ceremony():
    W, H = 1000, 520
    f = []

    cx_auth, cx_br, cx_rp = 150, 500, 850

    b_a, _, ha = textbox(cx_auth, 65, "Автентифікатор\n(Пристрій із ключем)", size=13, bold=True, fill=BLUFILL, stroke=NEG, pad=10)
    b_b, _, hb = textbox(cx_br, 65, "Браузер (User Agent)\nWebAuthn API", size=13, bold=True, fill=FILL, stroke=LINE, pad=10)
    b_r, _, hr = textbox(cx_rp, 65, "Бекенд (Relying Party)\nСервер застосунку", size=13, bold=True, fill=GRNFILL, stroke=FIELD, pad=10)
    f.extend([b_a, b_b, b_r])

    # Блок дії автентифікатора
    b_act, _, ha_act = textbox(cx_auth, 275, "Біометрія / PIN (UV)\nЗнаходить PrivKey за rpId\nПідписує authData || hash(clientDataJSON)", size=11, fill=BLUFILL, stroke=NEG, pad=6)

    # Блок дії сервера
    b_srv, _, hs_act = textbox(cx_rp, 440, "Перевіряє origin, rpIdHash, challenge\nЗвіряє підпис збереженим PubKey\nПеревіряє лічильник signCount -> сесія", size=11, fill=GRNFILL, stroke=FIELD, pad=6)

    # Лінії життя з розривами
    y_top = 65 + ha / 2 + 6
    f.append(line(cx_auth, y_top, cx_auth, 275 - ha_act / 2 - 4, color=MUTED, sw=1.2, dash="4,4"))
    f.append(line(cx_auth, 275 + ha_act / 2 + 4, cx_auth, 490, color=MUTED, sw=1.2, dash="4,4"))

    f.append(line(cx_br, y_top, cx_br, 490, color=MUTED, sw=1.2, dash="4,4"))

    f.append(line(cx_rp, y_top, cx_rp, 440 - hs_act / 2 - 4, color=MUTED, sw=1.2, dash="4,4"))
    f.append(line(cx_rp, 440 + hs_act / 2 + 4, cx_rp, 490, color=MUTED, sw=1.2, dash="4,4"))

    # 1. Запит входу
    f.append(arrow(cx_br, 135, cx_rp, 135, color=LINE))
    f.append(text((cx_br + cx_rp) / 2, 123, "1. POST /login/start (або автозаповнення)", size=11, color=INK))

    # 2. Опції запиту
    f.append(arrow(cx_rp, 175, cx_br, 175, color=FIELD))
    f.append(text((cx_br + cx_rp) / 2, 163, "2. Свіжий challenge + rpId + [allowCredentials]", size=11, color=FIELD, bold=True))

    # 3. get()
    f.append(arrow(cx_br, 215, cx_auth, 215, color=NEG))
    f.append(text((cx_auth + cx_br) / 2, 203, "3. navigator.credentials.get()", size=11, color=NEG, bold=True))

    # 4. Дія автентифікатора
    f.append(b_act)

    # 5. Результат браузеру
    f.append(arrow(cx_auth, 335, cx_br, 335, color=NEG))
    f.append(text((cx_auth + cx_br) / 2, 323, "5. authenticatorData + signature", size=11, color=NEG))

    # 6. Відправка на сервер
    f.append(arrow(cx_br, 385, cx_rp, 385, color=LINE))
    f.append(text((cx_br + cx_rp) / 2, 373, "6. POST /login/finish (credentialId, signature, authData, clientDataJSON)", size=11, color=INK, bold=True))

    # 7. Дія сервера
    f.append(b_srv)

    render(out("authentication-ceremony.svg"), W, H, *f,
           title="Церемонія автентифікації: криптографічний доказ володіння закритим ключем")


# ── 4. Бінарна структура authData ────────────────────────────────────────────
def fig_authdata_layout():
    W, H = 1000, 480
    f = []

    # Загальний заголовок і обов'язкова частина (37 байтів)
    b_head, _, _ = textbox(500, 55, "Загальний заголовок authData: 37 байтів (присутній у реєстрації та вході)",
                           size=13, bold=True, fill=BLUFILL, stroke=NEG, pad=8)
    f.append(b_head)

    # Три обов'язкові блоки: rpIdHash (32B), flags (1B), signCount (4B)
    b1 = fitbox(60, 95, 360, 70, "rpIdHash (32 байти)\nSHA-256 від домену (наприклад, sha256(\"bank.com\"))\nЗахищає від підміни сервісу", size=12, fill=FILL, stroke=LINE)
    b2 = fitbox(435, 95, 230, 70, "flags (1 байт)\nБітові прапорці стану\n(UP, UV, BE, BS, AT, ED)", size=12, fill=GRNFILL, stroke=FIELD, bold=True)
    b3 = fitbox(680, 95, 260, 70, "signCount (4 байти, uint32 BE)\nЛічильник підписів автентифікатора\nЗахист від клонування токена", size=12, fill=FILL, stroke=LINE)
    f.extend([b1, b2, b3])

    # Прапорці детально (Flags breakdown)
    b_flags_det = fitbox(60, 185, 880, 95,
                         "Розкладка байта прапорців (flags, 8 бітів):\n"
                         "• Біт 0 (0x01) UP: User Present (присутність підтверджена дотиком)\n"
                         "• Біт 2 (0x04) UV: User Verified (користувача верифіковано PIN / біометрією)\n"
                         "• Біт 3 (0x08) BE: Backup Eligibility (ключ дозволено синхронізувати в хмару)\n"
                         "• Біт 4 (0x10) BS: Backup State (ключ наразі синхронізовано як Passkey)\n"
                         "• Біт 6 (0x40) AT: Attested Credential Data (присутні дані нового ключа при реєстрації)",
                         size=11, fill=BLUFILL, stroke=NEG, pad=8)
    f.append(b_flags_det)

    # Опційні дані реєстрації: attestedCredentialData (якщо прапорець AT=1)
    b_att_head, _, _ = textbox(500, 310, "Секція attestedCredentialData (додається ТІЛЬКИ при реєстрації, прапорець AT=1)",
                               size=13, bold=True, fill=GRNFILL, stroke=FIELD, pad=8)
    f.append(b_att_head)

    b4 = fitbox(60, 345, 230, 95, "AAGUID (16 байтів)\nІдентифікатор моделі\nавтентифікатора\n(або нулі для Passkey)", size=11, fill=FILL, stroke=LINE)
    b5 = fitbox(305, 345, 170, 95, "credIdLength (2 байти)\nДовжина ідентифікатора\nключа (uint16 BE, L байтів)", size=11, fill=FILL, stroke=LINE)
    b6 = fitbox(490, 345, 200, 95, "credentialId (L байтів)\nУнікальний ID ключа,\nякий видає пристрій", size=11, fill=FILL, stroke=LINE)
    b7 = fitbox(705, 345, 235, 95, "credentialPublicKey\nВідкритий ключ у форматі\nCOSE / CBOR (kty, alg, x, y)", size=11, fill=GRNFILL, stroke=FIELD, bold=True)
    f.extend([b4, b5, b6, b7])

    render(out("authdata-binary-layout.svg"), W, H, *f,
           title="Бінарна структура authData: 37 байтів фіксованого заголовка та дані відкритого ключа")


# ── 5. Апаратний ключ vs Синхронізований Passkey ─────────────────────────────
def fig_device_bound_vs_synced():
    W, H = 1000, 460
    f = []

    # Ліва колонка: Апаратний ключ (Device-bound)
    hb1, _, _ = textbox(270, 65, "Апаратний ключ (Device-Bound / FIDO2)\nПрив'язаний до одного фізичного чіпа",
                        size=13, bold=True, fill=BLUFILL, stroke=NEG, pad=10)
    f.append(hb1)

    b_hw = fitbox(60, 110, 420, 240,
                  "Особливості архітектури:\n\n"
                  "• Закритий ключ створюється всередині апаратного чіпа\n"
                  "  (YubiKey, Nitrokey, апаратний модуль TPM)\n"
                  "• Ключ НЕМОЖЛИВО експортувати чи скопіювати з чіпа\n"
                  "• Прапорці BE = 0, BS = 0 (не підлягає резервуванню)\n"
                  "• signCount суворо зростає на кожному підписі\n\n"
                  "Перевага: максимальний рівень захисту від крадіжки\n"
                  "Ризик: втрата фізичного ключа вимагає резервного методу входу",
                  size=11, fill=FILL, stroke=LINE, pad=8)
    f.append(b_hw)

    b_hw_res, _, _ = textbox(270, 395, "Підходить для: адмінів, інфраструктури,\nвисокоризикових корпоративних акаунтів",
                             size=11, fill=BLUFILL, stroke=NEG, pad=6)
    f.append(b_hw_res)

    # Права колонка: Синхронізований Passkey (Multi-device)
    hb2, _, _ = textbox(730, 65, "Синхронізований Passkey (Multi-Device)\nНаскрізне шифрування через хмарний брелок",
                        size=13, bold=True, fill=GRNFILL, stroke=FIELD, pad=10)
    f.append(hb2)

    b_sync = fitbox(520, 110, 420, 240,
                    "Особливості архітектури:\n\n"
                    "• Закритий ключ зберігається в захищеному сховищі ОС\n"
                    "  (iCloud Keychain, Google Password Manager, 1Password)\n"
                    "• Синхронізується між пристроями з наскрізним шифруванням (E2EE)\n"
                    "• Прапорці BE = 1, BS = 1 (резервування увімкнено)\n"
                    "• signCount зазвичай = 0 (бо стан розходиться між гаджетами)\n\n"
                    "Перевага: користувач не втрачає доступ при зміні телефону\n"
                    "Ризик: безпека залежить від захисту головного хмарного акаунта",
                    size=11, fill=FILL, stroke=LINE, pad=8)
    f.append(b_sync)

    b_sync_res, _, _ = textbox(730, 395, "Підходить для: масових користувацьких сервісів,\nбанкінгу, e-commerce, заміни паролів",
                               size=11, fill=GRNFILL, stroke=FIELD, pad=6)
    f.append(b_sync_res)

    render(out("device-bound-vs-synced.svg"), W, H, *f,
           title="Апаратний ключ (Device-Bound) проти синхронізованого Passkey (Multi-Device)")


if __name__ == '__main__':
    fig_phishing_resistance()
    fig_registration_ceremony()
    fig_authentication_ceremony()
    fig_authdata_layout()
    fig_device_bound_vs_synced()
    print("All figures generated successfully.")
