# -*- coding: utf-8 -*-
"""Фігури до теми «SCRAM: солений виклик-відповідь, що не лишає ключа на сервері»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SOFT = "#eef3fb"
WARM = "#fdf3e6"
PAPER = "#ffffff"
GREEN_BG = "#eafaf1"


def box(cx, cy, s, size=13, fill=FILL, bold=False, stroke=LINE, pad=10):
    body, w, h = textbox(cx, cy, s, size=size, fill=fill, bold=bold, stroke=stroke, pad=pad)
    return body, w / 2.0, h / 2.0


# ─────────────────────────────────────────────────────────────────────────────
# 1. Повний обмін SCRAM: два оберти, виведення та взаємна перевірка
# ─────────────────────────────────────────────────────────────────────────────
def fig_scram_flow():
    W, H = 1200, 780
    f = []
    xc, xs = 150, 1050
    top, bot = 96, 730

    for x, name in ((xc, "Клієнт"), (xs, "Сервер")):
        b, _, _ = box(x, 58, name, size=14, bold=True)
        f.append(b)
        f.append(line(x, top - 14, x, bot, color=MUTED, sw=1.2, dash="5,5"))

    def msg(y, x1, x2, label, color=INK):
        f.append(arrow(x1, y, x2, y, color=color))
        f.append(text((x1 + x2) / 2.0, y - 11, label, size=12, color=color))

    # 1. Client first
    msg(130, xc, xs, "1. client-first: ім'я користувача та випадковий nonce клієнта")
    cf, _, _ = box(600, 185,
                   'n=alice, r=fyko+d2lwyECACBYghMXFGW3\n'
                   '(заголовок зв\'язування n,, вказує: канал без TLS-binding)',
                   size=11, fill=SOFT, stroke="#c8d6ea")
    f.append(cf)

    # 2. Server first
    msg(270, xs, xc, "2. server-first: спільний nonce, сіль та лічильник ітерацій", color=POS)
    sf, _, _ = box(600, 335,
                   'r=fyko+d2lwyECACBYghMXFGW3B96duGRZSbNHH3ftuGJqtryh,\n'
                   's=QSXCR+Q6sek8bf92, i=4096\n'
                   'Сервер видобуває зі своєї БД: Salt, i, StoredKey, ServerKey',
                   size=11, fill=WARM, stroke="#e6d3b3")
    f.append(sf)

    # Local computation note
    comp_note, _, _ = box(xc + 180, 435,
                          "Клієнт рахує:\n"
                          "SaltedPassword = PBKDF2(Pass, Salt, i)\n"
                          "ClientKey = HMAC(SaltedPassword, \"Client Key\")\n"
                          "StoredKey = H(ClientKey)\n"
                          "ClientProof = ClientKey ⊕ HMAC(StoredKey, AuthMsg)",
                          size=11, fill=PAPER, stroke="#a5b4fc")
    f.append(comp_note)

    # 3. Client final
    msg(535, xc, xs, "3. client-final: канал, повний nonce і маскований доказ ClientProof")
    c_fin, _, _ = box(600, 585,
                      'c=biws, r=fyko+d2lwyECACBYghMXFGW3B96duGRZSbNHH3ftuGJqtryh,\n'
                      'p=v0X8v3Bz2T0CJGbJQII0GeKPxjw=\n'
                      'Сервер знімає маску: ClientKey\' = ClientProof ⊕ HMAC(StoredKey, AuthMsg)\n'
                      'Перевірка: H(ClientKey\') == StoredKey  ⇒  клієнт справжній!',
                      size=11, fill=SOFT, stroke="#c8d6ea")
    f.append(c_fin)

    # 4. Server final
    msg(665, xs, xc, "4. server-final: підпис сервера ServerSignature (v=...)", color=FIELD)
    s_fin, _, _ = box(600, 715,
                      'v=rmF9pqV8S7suAoZWja4TGst0VaE=\n'
                      'Клієнт звіряє з HMAC(ServerKey, AuthMsg)  ⇒  сервер справжній!',
                      size=11, fill=GREEN_BG, stroke="#a3e4d7")
    f.append(s_fin)

    render(os.path.join(OUT, 'scram-flow.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Дерево криптографічних перетворень SCRAM
# ─────────────────────────────────────────────────────────────────────────────
def fig_keys_derivation():
    W, H = 1220, 760
    f = []

    f.append(text(W / 2.0, 36, "Дерево виведення ключів та доказів у SCRAM", size=16, bold=True))

    # Top: Password + Salt + i
    inp, inpw, inph = box(610, 85, "Пароль користувача (Password)   +   Сіль (Salt)   +   Ітерації (i)",
                          size=13, fill=WARM, stroke="#e6d3b3", bold=True)
    f.append(inp)

    # Arrow to PBKDF2
    f.append(arrow(610, 110, 610, 150))
    pbk, pbkw, pbkh = box(610, 175, "PBKDF2-HMAC-SHA256 (Password, Salt, i)\nПовільне обчислення (тисячі ітерацій, захист від перебору)",
                          size=12, fill=PAPER, stroke="#a5b4fc")
    f.append(pbk)

    # Arrow to SaltedPassword
    f.append(arrow(610, 205, 610, 245))
    sp, spw, sph = box(610, 270, "SaltedPassword (солений майстер-секрет)\nНІКОЛИ не зберігається на сервері й не передається мережею!",
                       size=13, fill=WARM, stroke="#e6d3b3", bold=True)
    f.append(sp)

    # Split into ClientKey and ServerKey
    f.append(line(610, 305, 610, 335, color=MUTED, sw=1.5))
    f.append(line(310, 335, 910, 335, color=MUTED, sw=1.5))
    f.append(arrow(310, 335, 310, 365))
    f.append(arrow(910, 335, 910, 365))

    # Left Branch: Client Authentication
    ck, _, _ = box(310, 395, "ClientKey = HMAC(SaltedPassword, \"Client Key\")\nСекретний ключ клієнта",
                   size=12, fill=SOFT, stroke="#c8d6ea", bold=True)
    f.append(ck)

    f.append(arrow(310, 430, 310, 470))
    sk, _, _ = box(310, 500, "StoredKey = H(ClientKey)\nЗберігається в базі даних сервера!\nОдносторонній геш: з StoredKey не відновити ClientKey",
                   size=12, fill=GREEN_BG, stroke="#a3e4d7")
    f.append(sk)

    f.append(arrow(310, 545, 310, 585))
    csig, _, _ = box(310, 615, "ClientSignature = HMAC(StoredKey, AuthMessage)\nПідпис контенту переговорів на StoredKey",
                     size=12, fill=PAPER, stroke="#c8d6ea")
    f.append(csig)

    f.append(arrow(310, 650, 310, 685))
    cproof, _, _ = box(310, 715, "ClientProof = ClientKey ⊕ ClientSignature\nМаскований доказ: їде мережею, не розкриваючи ClientKey",
                       size=12, fill=SOFT, stroke="#2457d6", bold=True)
    f.append(cproof)

    # Right Branch: Server Authentication
    svk, _, _ = box(910, 395, "ServerKey = HMAC(SaltedPassword, \"Server Key\")\nЗберігається в базі даних сервера!\nСекретний ключ автентифікації сервера",
                    size=12, fill=GREEN_BG, stroke="#a3e4d7", bold=True)
    f.append(svk)

    f.append(arrow(910, 445, 910, 585))
    svsig, _, _ = box(910, 615, "ServerSignature = HMAC(ServerKey, AuthMessage)\nПідпис сервера: передається клієнту у виразі v=...",
                      size=12, fill=PAPER, stroke="#e6d3b3")
    f.append(svsig)

    f.append(arrow(910, 650, 910, 685))
    svver, _, _ = box(910, 715, "Клієнт звіряє ServerSignature зі своїм розрахунком\nГарантує захист від фальшивого сервера",
                      size=12, fill=WARM, stroke="#c0392b", bold=True)
    f.append(svver)

    render(os.path.join(OUT, 'scram-keys-derivation.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Межі захисту: порівняння трьох моделей загроз
# ─────────────────────────────────────────────────────────────────────────────
def fig_threat_model():
    W, H = 1240, 720
    f = []

    f.append(text(W / 2.0, 38, "Порівняння моделей безпеки: Plaintext vs Digest vs SCRAM", size=16, bold=True))

    cols = [
        (230, "1. Пасивне прослуховування каналу", [
            ("Відкритий текст (Plaintext)", "Пароль перехоплюється миттєво", POS),
            ("HTTP Digest / CRAM-MD5", "Пароль не їде, але виклик MD5 вразливий до швидкого офлайн-перебору", MUTED),
            ("SCRAM (PBKDF2 + XOR)", "Їде ClientProof; офлайн-перебір вимагає тисяч ітерацій PBKDF2 на пароль", FIELD),
        ]),
        (620, "2. Викрадення бази даних сервера", [
            ("Відкритий текст (Plaintext)", "Усі паролі скомпрометовано одразу", POS),
            ("HTTP Digest (H(A1))", "Хеш H(A1) є еквівалентом пароля — зловмисник входить без зламу хешу!", POS),
            ("SCRAM (StoredKey + ServerKey)", "StoredKey не дає увійти (потрібен ClientKey); перебір захищено сіллю та PBKDF2", FIELD),
        ]),
        (1010, "3. Фальшивий сервер / Man-in-the-Middle", [
            ("Відкритий текст (Plaintext)", "Фальшивий сервер забирає пароль", POS),
            ("HTTP Digest / CRAM-MD5", "Одностороння автентифікація: клієнт не перевіряє справжність сервера", POS),
            ("SCRAM-SHA-256-PLUS", "Взаємна автентифікація (ServerSignature) + прив'язка до TLS-каналу блокує MitM", FIELD),
        ]),
    ]

    for cx, title, items in cols:
        tb, _, _ = box(cx, 95, title, size=13, fill=WARM, stroke="#e6d3b3", bold=True)
        f.append(tb)

        y = 190
        for proto, desc, col in items:
            pb, _, _ = box(cx, y, proto, size=12, fill=SOFT if col != FIELD else GREEN_BG, stroke=col, bold=True)
            db, _, _ = box(cx, y + 65, desc, size=11, fill=PAPER, stroke="#d1d5db")
            f += [pb, db]
            f.append(arrow(cx, y + 25, cx, y + 42, color=MUTED))
            y += 160

    render(os.path.join(OUT, 'scram-threat-model.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Прив'язка до каналу (Channel Binding) у SCRAM-SHA-256-PLUS
# ─────────────────────────────────────────────────────────────────────────────
def fig_channel_binding():
    W, H = 1200, 680
    f = []

    f.append(text(W / 2.0, 36, "Прив'язка до каналу: блокування MitM-проксі у SCRAM-PLUS", size=16, bold=True))

    # Left: Client, Middle: MitM Proxy, Right: Server
    xc, xm, xs = 160, 600, 1040

    cb, _, _ = box(xc, 110, "Клієнт", size=14, bold=True, fill=SOFT)
    mb, _, _ = box(xm, 110, "Зловмисний MitM-проксі\n(підміняє сертифікат TLS)", size=13, bold=True, fill=WARM, stroke=POS)
    sb, _, _ = box(xs, 110, "Справжній Сервер", size=14, bold=True, fill=GREEN_BG)
    f += [cb, mb, sb]

    # TLS Leg 1
    f.append(arrow(xc + 70, 180, xm - 130, 180, color=NEG))
    f.append(text((xc + xm) / 2.0 - 30, 165, "TLS-з'єднання №1 (Сертифікат проксі)", size=12, color=NEG))

    # TLS Leg 2
    f.append(arrow(xm + 130, 180, xs - 80, 180, color=POS))
    f.append(text((xm + xs) / 2.0 + 30, 165, "TLS-з'єднання №2 (Сертифікат сервера)", size=12, color=POS))

    # Data inside Leg 1
    d1, _, _ = box(340, 270,
                   "Клієнт бере відбиток сертифіката із TLS №1:\n"
                   "tls-server-end-point = SHA-256(Сертифікат_Проксі)\n"
                   "Вставляє у поле c=... повідомлення AuthMessage",
                   size=11, fill=PAPER, stroke="#a5b4fc")
    f.append(d1)

    # Data inside Leg 2
    d2, _, _ = box(860, 270,
                   "Сервер бере відбиток сертифіката із TLS №2:\n"
                   "tls-server-end-point = SHA-256(Сертифікат_Сервера)\n"
                   "Очікує цей відбиток у полі c=... повідомлення AuthMessage",
                   size=11, fill=PAPER, stroke="#a5b4fc")
    f.append(d2)

    # MitM Proxy tries to forward
    f.append(arrow(340, 345, xm, 400, color=MUTED))
    f.append(arrow(xm, 400, 860, 345, color=MUTED))

    mb_action, _, _ = box(xm, 420,
                          "Проксі пересилає SCRAM ClientProof без змін.\n"
                          "Але змінити поле c=... проксі не може, бо воно накрите підписом ClientProof!\n"
                          "А розрахувати новий ClientProof без пароля проксі не вміє.",
                          size=12, fill=WARM, stroke=POS)
    f.append(mb_action)

    # Result at Server
    res, _, _ = box(W / 2.0, 560,
                    "Результат перевірки на сервері:\n"
                    "AuthMessage клієнта (з відбитком проксі)  ≠  AuthMessage сервера (з відбитком сервера)\n"
                    "Сервер виявляє розрив каналу і скидає сесію: e=channel-bindings-dont-match",
                    size=13, fill=GREEN_BG, stroke=FIELD, bold=True)
    f.append(res)

    f.append(text(W / 2.0, 650,
                  "SCRAM-SHA-256-PLUS робить підміну TLS-сертифіката безглуздою навіть за наявності скомпрометованого кореневого CA",
                  size=12, color=INK))

    render(os.path.join(OUT, 'channel-binding.svg'), W, H, *f)


if __name__ == '__main__':
    fig_scram_flow()
    fig_keys_derivation()
    fig_threat_model()
    fig_channel_binding()
    print("ok")
