# -*- coding: utf-8 -*-
"""Фігури до теми «DNSSEC: підписи зони і ланцюг довіри до відповіді DNS»."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SOFT = "#eef3fb"
WARM = "#fdf3e6"
GREEN_BG = "#eafaf1"
RED_BG = "#fdecea"
PAPER = "#ffffff"


def box(cx, cy, s, size=13, fill=FILL, bold=False, stroke=LINE, sw=1.5):
    body, w, h = textbox(cx, cy, s, size=size, fill=fill, bold=bold, stroke=stroke, sw=sw)
    return body, w / 2.0, h / 2.0


# ─────────────────────────────────────────────────────────────────────────────
# 1. Атака Камінські (Cache Poisoning) проти DNSSEC
# ─────────────────────────────────────────────────────────────────────────────
def fig_kaminsky_poisoning():
    W, H = 1060, 680
    f = []

    f.append(text(W / 2, 34, "Атака Камінські: підміна авторитетного сервера в кеші рекурсивного резолвера",
                  size=16, color=INK, bold=True))

    xr, xa, xauth = 200, 530, 860
    top, bot = 80, 620

    for x, title, bg_col, b_col in [
        (xr, "Рекурсивний резолвер\n(Кеш DNS)", SOFT, "#3b82f6"),
        (xa, "Зловмисник (Атакуючий)\nГенерує випадкові запити", RED_BG, POS),
        (xauth, "Справжній сервер зони\n(Auth NS: example.com)", GREEN_BG, FIELD),
    ]:
        b, _, _ = box(x, top + 26, title, size=12, fill=bg_col, stroke=b_col, bold=True)
        f.append(b)
        f.append(line(x, top + 56, x, bot, color=MUTED, sw=1.2, dash="5,5"))

    def msg(y, x1, x2, label, color=INK, dash=None):
        if dash:
            f.append(line(x1, y, x2, y, color=color, sw=1.5, dash=dash))
        else:
            f.append(arrow(x1, y, x2, y, color=color, sw=1.8))
        f.append(text((x1 + x2) / 2.0, y - 9, label, size=11, color=color))

    # Крок 1: Зловмисник запитує неіснуюче ім'я
    msg(190, xa, xr, "1. Запит: a891f.example.com (у кеші немає)", color=POS)

    # Крок 2: Резолвер надсилає запит до авторитетного сервера
    msg(240, xr, xauth, "2. Рекурсивний запит a891f.example.com (TxID: ? Port: ?)", color=INK)

    # Крок 3: Шквал підроблених відповідей
    msg(300, xa, xr, "3. Шквал фальшивих відповідей (перебір TxID 0..65535)", color=POS)

    poison_box, _, _ = box(365, 390,
                           "Підроблений пакет:\n"
                           "• Answer: a891f.example.com → 1.2.3.4\n"
                           "• Authority: example.com NS evil.attacker.net  ← ОТРУТА!\n"
                           "• Additional: evil.attacker.net A 6.6.6.6",
                           size=11, fill=RED_BG, stroke=POS, bold=False)
    f.append(poison_box)

    # Крок 4: Справжня відповідь запізнюється
    msg(470, xauth, xr, "4. Справжня відповідь: NXDOMAIN (запізнилася)", color=MUTED)

    # Підсумок у рамці внизу
    res_box, _, _ = box(W / 2, 570,
                        "Наслідок без DNSSEC: Резолвер кешує evil.attacker.net як новий NS для ВСІЄЇ зони example.com!\n"
                        "Захист із DNSSEC: Відповідь 3 відкидається, бо в ній немає валідного RRSIG від справжнього KSK/ZSK зони.",
                        size=12, fill=WARM, stroke="#d97706", bold=True)
    f.append(res_box)

    render(os.path.join(OUT, 'kaminsky-poisoning.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Підпис набору записів (RRset) замість окремих записів
# ─────────────────────────────────────────────────────────────────────────────
def fig_rrset_signing():
    W, H = 1080, 600
    f = []

    f.append(text(W / 2, 34, "Чому DNSSEC підписує весь RRset як неподільний блок даних",
                  size=16, color=INK, bold=True))

    # Ліва колонка: Небезпека роздільного підпису
    left_x = 270
    lh, _, _ = box(left_x, 80, "Помилкова схема: підпис окремих записів", size=13, fill=RED_BG, stroke=POS, bold=True)
    f.append(lh)

    rec1, _, _ = box(left_x, 145, "example.com. IN A 193.0.2.1\n+ SIG(Record 1)", size=11, fill=FILL, stroke=MUTED)
    rec2, _, _ = box(left_x, 215, "example.com. IN A 193.0.2.2\n+ SIG(Record 2)", size=11, fill=FILL, stroke=MUTED)
    rec3, _, _ = box(left_x, 285, "example.com. IN AAAA 2001:db8::1\n+ SIG(Record 3)", size=11, fill=FILL, stroke=MUTED)
    f.append(rec1)
    f.append(rec2)
    f.append(rec3)

    warn_box, _, _ = box(left_x, 410,
                         "Вразливість до вирізання (Stripping Attack):\n"
                         "Зловмисник перехоплює відповідь і викидає\n"
                         "запис AAAA та один із записів A.\n"
                         "Клієнт перевіряє валідний підпис для залишеного\n"
                         "запису A і не підозрює, що відповідь обрізано!",
                         size=11, fill=RED_BG, stroke=POS)
    f.append(warn_box)

    # Розділювальна лінія
    f.append(line(540, 70, 540, 560, color=MUTED, sw=1.2, dash="4,4"))

    # Права колонка: DNSSEC RRset
    right_x = 810
    rh, _, _ = box(right_x, 80, "Канонічний DNSSEC: підпис набору RRset", size=13, fill=GREEN_BG, stroke=FIELD, bold=True)
    f.append(rh)

    # Канонічно відсортований блок
    rrset_box = rect(right_x - 220, 120, 440, 160, fill=SOFT, stroke="#3b82f6", sw=1.5, rx=6)
    f.append(rrset_box)
    f.append(text(right_x, 142, "Єдиний неподільний блок RRset (тип A):", size=12, color=INK, bold=True))
    f.append(text(right_x, 172, "1. example.com. 3600 IN A 193.0.2.1", size=11, color=INK))
    f.append(text(right_x, 196, "2. example.com. 3600 IN A 193.0.2.2", size=11, color=INK))
    f.append(text(right_x, 222, "3. example.com. 3600 IN A 193.0.2.3", size=11, color=INK))
    f.append(text(right_x, 256, "(Канонічне сортування за двійковим представленням RDATA)", size=10, color=MUTED, italic=True))

    f.append(arrow(right_x, 285, right_x, 325, color=FIELD, sw=2.0))
    f.append(text(right_x + 90, 305, "Підписується ZSK", size=11, color=FIELD, bold=True))

    rrsig_box, _, _ = box(right_x, 410,
                          "Запис RRSIG(A):\n"
                          "• Type Covered: A | Algorithm: 13 (ECDSA P-256)\n"
                          "• Labels: 2 | Original TTL: 3600\n"
                          "• Signature Expiration: 2026-09-01 00:00:00\n"
                          "• Key Tag: 34129 | Signer: example.com.\n"
                          "• Signature: [Криптографічний підпис над усім RRset]",
                          size=11, fill=GREEN_BG, stroke=FIELD)
    f.append(rrsig_box)

    f.append(text(W / 2, 575, "Будь-яка зміна, додавання або видалення хоча б одного запису з набору робить RRSIG недійсним",
                  size=12, color=INK, bold=True))

    render(os.path.join(OUT, 'rrset-signing.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Розділення ключів: ZSK проти KSK та запис DS
# ─────────────────────────────────────────────────────────────────────────────
def fig_key_separation():
    W, H = 1080, 620
    f = []

    f.append(text(W / 2, 34, "Архітектура розділення ключів у DNSSEC: ZSK, KSK та міст довіри DS",
                  size=16, color=INK, bold=True))

    # Батьківська зона
    parent_bg = rect(60, 70, 960, 140, fill="#faf5ff", stroke="#8b5cf6", sw=1.5, rx=8)
    f.append(parent_bg)
    f.append(text(190, 96, "Батьківська зона (наприклад, .com)", size=13, color="#6b21a8", bold=True))

    ds_box, _, _ = box(680, 140,
                       "Запис DS (Delegation Signer) для example.com:\n"
                       "Key Tag: 54109 | Alg: 13 (ECDSA) | Digest Type: 2 (SHA-256)\n"
                       "Digest: SHA-256( «example.com.» + DNSKEY_KSK )",
                       size=11, fill=PAPER, stroke="#8b5cf6", bold=True)
    f.append(ds_box)

    # Стрілка криптографічного зв'язку DS -> KSK
    f.append(arrow(680, 215, 680, 265, color="#8b5cf6", sw=2.2))
    f.append(text(785, 240, "Криптографічний геш-зліпок (хеш KSK)", size=11, color="#6b21a8", bold=True))

    # Дочірня авторитетна зона
    child_bg = rect(60, 270, 960, 310, fill=FILL, stroke=LINE, sw=1.5, rx=8)
    f.append(child_bg)
    f.append(text(200, 296, "Авторитетна зона (example.com)", size=13, color=INK, bold=True))

    # KSK блок
    ksk_box, _, _ = box(300, 375,
                        "Ключ підпису ключів: KSK (Flag 257)\n"
                        "• Довгоживучий (ротація раз на 1–2 роки)\n"
                        "• Зберігається у захищеному сховищі (HSM)\n"
                        "• Підписує ВИКЛЮЧНО набір DNSKEY RRset\n"
                        "• Його публічна частина гешується в DS",
                        size=11, fill=WARM, stroke="#d97706", bold=False)
    f.append(ksk_box)

    # ZSK блок
    zsk_box, _, _ = box(760, 375,
                        "Ключ підпису зони: ZSK (Flag 256)\n"
                        "• Короткоживучий (ротація кожні 1–3 місяці)\n"
                        "• Зберігається на сервері підпису зони\n"
                        "• Підписує всі прикладні RRset (A, MX, NSEC)\n"
                        "• Ротується локально без участі батьківської зони",
                        size=11, fill=SOFT, stroke="#3b82f6", bold=False)
    f.append(zsk_box)

    # Внутрішній підпис: KSK підписує DNSKEY RRset
    f.append(arrow(460, 375, 595, 375, color="#d97706", sw=1.8))
    f.append(text(525, 355, "RRSIG(DNSKEY)", size=11, color="#b45309", bold=True))

    # ZSK підписує дані зони
    data_box, _, _ = box(760, 520,
                         "Прикладні записи зони: A, AAAA, MX, TXT, NSEC3...\n"
                         "Підписані щомісячним ZSK → валідні записи RRSIG",
                         size=11, fill=GREEN_BG, stroke=FIELD)
    f.append(data_box)
    f.append(arrow(760, 445, 760, 480, color=FIELD, sw=1.8))
    f.append(text(830, 462, "RRSIG(Data)", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, 'key-separation.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Повний ланцюг довіри (Chain of Trust)
# ─────────────────────────────────────────────────────────────────────────────
def fig_chain_of_trust():
    W, H = 1080, 780
    f = []

    f.append(text(W / 2, 30, "Ланцюг довіри DNSSEC від кореневого якоря (.) до вебсервера",
                  size=16, color=INK, bold=True))

    y_root = 120
    y_tld = 340
    y_sld = 560

    # Якір довіри
    anchor_box, _, _ = box(190, y_root,
                           "Вбудований якір довіри:\n"
                           "Root KSK Trust Anchor\n"
                           "(«Зашитий» у конфігурацію резолвера)",
                           size=11, fill=GREEN_BG, stroke=FIELD, bold=True)
    f.append(anchor_box)

    # Рівень 1: Коренева зона
    root_panel = rect(370, 60, 670, 140, fill=PAPER, stroke="#6b7280", sw=1.5, rx=6)
    f.append(root_panel)
    f.append(text(460, 85, "Коренева зона: .", size=13, color=INK, bold=True))

    r_ksk, _, _ = box(480, 135, "Root DNSKEY (KSK)", size=11, fill=WARM, stroke="#d97706")
    r_zsk, _, _ = box(670, 135, "Root DNSKEY (ZSK)", size=11, fill=SOFT, stroke="#3b82f6")
    r_ds, _, _ = box(890, 135, ".com DS Record\n(Хеш com KSK)", size=11, fill=PAPER, stroke="#8b5cf6", bold=True)
    f.append(r_ksk)
    f.append(r_zsk)
    f.append(r_ds)

    f.append(arrow(310, y_root, 405, y_root, color=FIELD, sw=2.0))
    f.append(arrow(545, 135, 605, 135, color="#d97706", sw=1.5))
    f.append(arrow(735, 135, 805, 135, color="#3b82f6", sw=1.5))

    # Зв'язок Root DS -> com KSK
    f.append(arrow(890, 175, 480, y_tld - 35, color="#8b5cf6", sw=2.0))
    f.append(text(720, 245, "1. Звірка хешу DS з публічним KSK .com", size=11, color="#6b21a8", bold=True))

    # Рівень 2: Зона .com
    tld_panel = rect(370, y_tld - 50, 670, 140, fill=PAPER, stroke="#6b7280", sw=1.5, rx=6)
    f.append(tld_panel)
    f.append(text(460, y_tld - 25, "Зона TLD: .com", size=13, color=INK, bold=True))

    t_ksk, _, _ = box(480, y_tld + 25, ".com DNSKEY (KSK)", size=11, fill=WARM, stroke="#d97706")
    t_zsk, _, _ = box(670, y_tld + 25, ".com DNSKEY (ZSK)", size=11, fill=SOFT, stroke="#3b82f6")
    t_ds, _, _ = box(890, y_tld + 25, "example.com DS\n(Хеш KSK example)", size=11, fill=PAPER, stroke="#8b5cf6", bold=True)
    f.append(t_ksk)
    f.append(t_zsk)
    f.append(t_ds)

    f.append(arrow(545, y_tld + 25, 605, y_tld + 25, color="#d97706", sw=1.5))
    f.append(arrow(735, y_tld + 25, 805, y_tld + 25, color="#3b82f6", sw=1.5))

    # Зв'язок com DS -> example KSK
    f.append(arrow(890, y_tld + 65, 480, y_sld - 35, color="#8b5cf6", sw=2.0))
    f.append(text(720, y_tld + 115, "2. Звірка хешу DS з публічним KSK example.com", size=11, color="#6b21a8", bold=True))

    # Рівень 3: Зона example.com
    sld_panel = rect(370, y_sld - 50, 670, 160, fill=PAPER, stroke="#6b7280", sw=1.5, rx=6)
    f.append(sld_panel)
    f.append(text(490, y_sld - 25, "Авторитетна зона: example.com", size=13, color=INK, bold=True))

    s_ksk, _, _ = box(480, y_sld + 35, "example.com KSK", size=11, fill=WARM, stroke="#d97706")
    s_zsk, _, _ = box(670, y_sld + 35, "example.com ZSK", size=11, fill=SOFT, stroke="#3b82f6")
    s_rec, _, _ = box(890, y_sld + 35, "www.example.com\nIN A 193.0.2.1\n+ RRSIG(A)", size=11, fill=GREEN_BG, stroke=FIELD, bold=True)
    f.append(s_ksk)
    f.append(s_zsk)
    f.append(s_rec)

    f.append(arrow(545, y_sld + 35, 605, y_sld + 35, color="#d97706", sw=1.5))
    f.append(arrow(735, y_sld + 35, 805, y_sld + 35, color=FIELD, sw=2.0))

    # Фінал валідації
    f.append(text(W / 2, 745,
                  "Результат валідації: неперервний ланцюг цифрових підписів і геш-зліпків від кореня → Прапорець AD = 1 (Authenticated Data)",
                  size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, 'dnssec-chain-of-trust.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 5. Доведення неіснування: NSEC проти NSEC3
# ─────────────────────────────────────────────────────────────────────────────
def fig_nsec_vs_nsec3():
    W, H = 1080, 580
    f = []

    f.append(text(W / 2, 34, "Криптографічне доведення неіснування запису: NSEC проти NSEC3",
                  size=16, color=INK, bold=True))

    # Ліва половина: NSEC
    f.append(text(270, 75, "NSEC: Лексикографічне кільце імен", size=14, color=INK, bold=True))

    n1, _, _ = box(150, 140, "api.example.com.\n[A, RRSIG, NSEC]", size=11, fill=SOFT, stroke="#3b82f6")
    n2, _, _ = box(390, 140, "mail.example.com.\n[A, MX, RRSIG, NSEC]", size=11, fill=SOFT, stroke="#3b82f6")
    n3, _, _ = box(270, 270, "www.example.com.\n[A, RRSIG, NSEC]", size=11, fill=SOFT, stroke="#3b82f6")
    f.append(n1)
    f.append(n2)
    f.append(n3)

    f.append(arrow(220, 140, 305, 140, color="#3b82f6", sw=1.8))
    f.append(arrow(390, 185, 330, 240, color="#3b82f6", sw=1.8))
    f.append(arrow(210, 250, 160, 185, color="#3b82f6", sw=1.8))

    nsec_proof, _, _ = box(270, 390,
                           "Запит: blog.example.com (не існує)\n"
                           "Відповідь: NSEC запис від api до mail.\n"
                           "«Між api та mail інших імен немає!»\n"
                           "Доказ валідний, але розкриває структуру зони.\n"
                           "⚠️ Вразливість Zone Walking: перебір усіх доменів.",
                           size=11, fill=RED_BG, stroke=POS)
    f.append(nsec_proof)

    # Розділювач
    f.append(line(540, 60, 540, 540, color=MUTED, sw=1.2, dash="4,4"))

    # Права половина: NSEC3
    f.append(text(810, 75, "NSEC3: Гешоване кільце із сіллю", size=14, color=INK, bold=True))

    h1, _, _ = box(680, 140, "0P9... (H(api))\nNext: 7T8...", size=11, fill=GREEN_BG, stroke=FIELD)
    h2, _, _ = box(940, 140, "7T8... (H(mail))\nNext: B4U...", size=11, fill=GREEN_BG, stroke=FIELD)
    h3, _, _ = box(810, 270, "B4U... (H(www))\nNext: 0P9...", size=11, fill=GREEN_BG, stroke=FIELD)
    f.append(h1)
    f.append(h2)
    f.append(h3)

    f.append(arrow(755, 140, 865, 140, color=FIELD, sw=1.8))
    f.append(arrow(940, 185, 875, 240, color=FIELD, sw=1.8))
    f.append(arrow(750, 250, 690, 185, color=FIELD, sw=1.8))

    nsec3_proof, _, _ = box(810, 390,
                            "Запит: blog.example.com → H(blog) = 3K2...\n"
                            "Відповідь: NSEC3 запис з інтервалом 0P9... → 7T8...\n"
                            "Хеш 3K2... строго потрапляє в інтервал [0P9..7T8]!\n"
                            "✓ Доказ неіснування без розкриття відкритого імені.\n"
                            "Ітерований хеш SHA-1/SHA-256 із сіллю (Salt).",
                            size=11, fill=GREEN_BG, stroke=FIELD)
    f.append(nsec3_proof)

    f.append(text(W / 2, 545, "NSEC3 захищає приватність внутрішньої топології зони від автоматизованого сканування",
                  size=12, color=INK, bold=True))

    render(os.path.join(OUT, 'nsec-vs-nsec3.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 6. Стан валідатора: Secure, Insecure, Bogus, Indeterminate
# ─────────────────────────────────────────────────────────────────────────────
def fig_validator_state_machine():
    W, H = 1060, 640
    f = []

    f.append(text(W / 2, 32, "Стани валідації резолвера та формування прапорців AD / SERVFAIL",
                  size=16, color=INK, bold=True))

    # Старт: Отримання відповіді DNS
    start_b, _, _ = box(W / 2, 85,
                        "Отримано відповідь DNS із секціями Answer, Authority та RRSIG\n"
                        "(Клієнт надіслав запит з EDNS0 DO=1 «DNSSEC OK»)",
                        size=12, fill=SOFT, stroke="#3b82f6", bold=True)
    f.append(start_b)

    f.append(arrow(W / 2, 120, W / 2, 160, color="#3b82f6", sw=2.0))

    # Перевірка наявності DS у батьківській зоні
    cond_ds, _, _ = box(W / 2, 195,
                        "Чи делеговано зону з криптографічним DS-записом у батька?",
                        size=12, fill=WARM, stroke="#d97706", bold=True)
    f.append(cond_ds)

    # Гілка Вліво: DS немає (Insecure)
    f.append(arrow(340, 195, 200, 195, color=MUTED, sw=1.8))
    f.append(arrow(200, 195, 200, 270, color=MUTED, sw=1.8))
    f.append(text(260, 180, "Ні (Непідписана)", size=11, color=MUTED, bold=True))

    insecure_box, _, _ = box(200, 360,
                             "Стан: INSECURE\n\n"
                             "Зона або домен законно не використовує\n"
                             "DNSSEC (є валідний доказ відсутності DS).\n"
                             "Відповідь повертається клієнту\n"
                             "із прапорцем AD = 0 (Не автентифіковано).",
                             size=11, fill=FILL, stroke=MUTED, bold=False)
    f.append(insecure_box)

    # Гілка Вниз: DS є, перевіряємо криптографію
    f.append(arrow(W / 2, 230, W / 2, 290, color=FIELD, sw=2.0))
    f.append(text(W / 2 + 80, 255, "Так (Підписана)", size=11, color=FIELD, bold=True))

    cond_crypto, _, _ = box(W / 2, 340,
                            "Перевірка ланцюга: DS → KSK → ZSK → RRSIG(Data)\n"
                            "1. Чи чинні часові мітки Inception / Expiration?\n"
                            "2. Чи збігаються хеші DS та відкритий ключ KSK?\n"
                            "3. Чи математично сходиться підпис RRSIG над RRset?",
                            size=11, fill=PAPER, stroke=LINE)
    f.append(cond_crypto)

    # Успіх -> Secure
    f.append(arrow(W / 2 + 190, 340, 840, 340, color=FIELD, sw=2.0))
    f.append(arrow(840, 340, 840, 420, color=FIELD, sw=2.0))
    f.append(text(730, 325, "Усі підписи валідні", size=11, color=FIELD, bold=True))

    secure_box, _, _ = box(840, 500,
                           "Стан: SECURE\n\n"
                           "Дані автентичні й цілісні.\n"
                           "Ланцюг перевірено до кореня.\n"
                           "Резолвер встановлює у відповіді\n"
                           "прапорець AD = 1 (Authenticated Data).",
                           size=11, fill=GREEN_BG, stroke=FIELD, bold=False)
    f.append(secure_box)

    # Помилка -> Bogus
    f.append(arrow(W / 2 - 190, 340, 490, 420, color=POS, sw=2.0))
    f.append(text(460, 370, "Незбіг підпису / час минув", size=11, color=POS, bold=True))

    bogus_box, _, _ = box(490, 500,
                          "Стан: BOGUS\n\n"
                          "Підпис сфальсифіковано, ключ підмінено\n"
                          "або термін RRSIG вичерпано.\n"
                          "Резолвер БЛОКУЄ відповідь і повертає\n"
                          "клієнту помилку SERVFAIL (RCODE 2).",
                          size=11, fill=RED_BG, stroke=POS, bold=False)
    f.append(bogus_box)

    f.append(text(W / 2, 615, "Якщо клієнт надсилає прапорець CD=1 (Checking Disabled), резолвер повертає Bogus-дані для локальної діагностики",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, 'validator-state-machine.svg'), W, H, *f)


if __name__ == '__main__':
    fig_kaminsky_poisoning()
    fig_rrset_signing()
    fig_key_separation()
    fig_chain_of_trust()
    fig_nsec_vs_nsec3()
    fig_validator_state_machine()
    print("All figures generated successfully.")
