# -*- coding: utf-8 -*-
"""Фігури до теми «HMAC і коди автентичності повідомлень»."""

import os
import sys

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SOFT_BLUE  = "#eef3fb"
SOFT_WARN  = "#fdf3e6"
SOFT_GREEN = "#eafaf1"
SOFT_RED   = "#fdeeed"
BORDER_BLUE  = "#c8d6ea"
BORDER_WARN  = "#e6d3b3"
BORDER_GREEN = "#a9dfbf"
BORDER_RED   = "#f5b7b1"


# ─────────────────────────────────────────────────────────────────────────────
# 1. Атака подовження довжини (Length Extension Attack) на Merkle-Damgard
# ─────────────────────────────────────────────────────────────────────────────
def fig_length_extension():
    W, H = 1200, 720
    f = []

    # Заголовок блоку легітимного гешу
    h1, _, _ = textbox(340, 50, "Легітимне обчислення H(Key || Message) сервером",
                       size=14, bold=True, fill=SOFT_BLUE, stroke=BORDER_BLUE)
    f.append(h1)

    # Блоки Merkle-Damgard: IV -> Блок 1 -> Дайджест
    iv_box, _, _ = textbox(120, 140, "Стандартний IV\n(фіксований у стандарті)",
                           size=11, fill=FILL, stroke=LINE)
    f.append(iv_box)

    f.append(arrow(205, 140, 265, 140, color=LINE))

    b1_box, _, _ = textbox(410, 140,
                           "Блок 1 (64 байти): [ Таємний Ключ || Message || Доповнення Pad₁ ]\n"
                           "«amount=100&to=bob» + біт 1, нулі та довжина",
                           size=11, fill=SOFT_GREEN, stroke=BORDER_GREEN)
    f.append(b1_box)

    f.append(arrow(555, 140, 615, 140, color=LINE))

    tag1_box, _, _ = textbox(810, 140,
                             "Внутрішній стан після Блоку 1 = Хеш H(Key || Message)\n"
                             "h = [a, b, c, d, e, f, g, h] (відкритий у мережі підпис)",
                             size=11, fill=SOFT_WARN, stroke=BORDER_WARN, bold=True)
    f.append(tag1_box)

    # Розділювальна лінія
    f.append(line(80, 240, 1120, 240, color=MUTED, sw=1.2, dash="6,6"))
    f.append(text(600, 265, "Перехоплення зловмисником: підпис H відомий, але таємний ключ НЕВІДОМИЙ",
                  size=12, color=POS, bold=True))

    # Заголовок атаки
    h2, _, _ = textbox(360, 320, "Атака подовженням: зловмисник продовжує ланцюг обчислень",
                       size=14, bold=True, fill=SOFT_RED, stroke=BORDER_RED)
    f.append(h2)

    # Зловмисник бере h замість IV
    atk_iv, _, _ = textbox(190, 420,
                           "Новий стартовий стан IV' = h\n(перехоплений дайджест)",
                           size=11, fill=SOFT_WARN, stroke=BORDER_WARN, bold=True)
    f.append(atk_iv)

    f.append(arrow(320, 420, 390, 420, color=POS, sw=2.0))

    # Блок подовження
    b2_box, _, _ = textbox(570, 420,
                           "Блок 2 (подовження): [ Шкідливий хвіст || Доповнення Pad₂ ]\n"
                           "«&to=eve&amount=999999» + нове доповнення",
                           size=11, fill=SOFT_RED, stroke=BORDER_RED)
    f.append(b2_box)

    f.append(arrow(750, 420, 820, 420, color=POS, sw=2.0))

    # Сфальсифікований тег
    forged_box, _, _ = textbox(990, 420,
                               "Сфальсифікований тег H'\n"
                               "Валідний для розширеного тіла!",
                               size=11, fill=SOFT_RED, stroke=BORDER_RED, bold=True)
    f.append(forged_box)

    # Пояснювальний висновок
    summary_box, _, _ = textbox(600, 590,
                                "Сервер отримує [ Message || Pad₁ || Шкідливий хвіст ] разом із тегом H'.\n"
                                "Під час перевірки сервер рахує H(Key || Message || Pad₁ || Шкідливий хвіст)\n"
                                "і отримує ТОЙ САМИЙ тег H'! Автентичність скомпрометовано без знання ключа.",
                                size=12, fill=FILL, stroke=LINE)
    f.append(summary_box)

    f.append(text(600, 685,
                  "Меркле-Дамґорд видає внутрішній стан як результат — це дозволяє дописувати дані в кінець",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'fig-length-extension.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Вкладена двопрохідна структура HMAC
# ─────────────────────────────────────────────────────────────────────────────
def fig_hmac_structure():
    W, H = 1200, 780
    f = []

    # Вхідний ключ
    k_box, _, _ = textbox(600, 50,
                          "Вхідний секретний ключ K (довільної довжини)\n"
                          "Якщо |K| > B: K' = H(K); якщо |K| < B: K' = K || 0x00...",
                          size=12, fill=SOFT_BLUE, stroke=BORDER_BLUE, bold=True)
    f.append(k_box)

    # Розгалуження на ipad та opad
    f.append(arrow(470, 85, 300, 150, color=LINE, sw=1.8))
    f.append(arrow(730, 85, 900, 150, color=LINE, sw=1.8))

    # Ліва гілка: Внутрішній прохід (ipad)
    ipad_xor, _, _ = textbox(300, 180,
                             "K_in = K' ⊕ ipad\n(ipad = 0x36, повторений B разів)",
                             size=12, fill=SOFT_GREEN, stroke=BORDER_GREEN, bold=True)
    f.append(ipad_xor)

    f.append(arrow(300, 220, 300, 280, color=LINE, sw=1.8))

    # Повідомлення m
    msg_box, _, _ = textbox(110, 280, "Повідомлення m\n(довільна довжина)",
                            size=12, fill=FILL, stroke=LINE)
    f.append(msg_box)
    f.append(arrow(190, 280, 210, 340, color=LINE, sw=1.8))
    f.append(arrow(300, 220, 300, 340, color=LINE, sw=1.8))

    inner_concat, _, _ = textbox(300, 370,
                                 "Конкатенація: [ K_in || Повідомлення m ]",
                                 size=12, fill=SOFT_GREEN, stroke=BORDER_GREEN)
    f.append(inner_concat)

    f.append(arrow(300, 405, 300, 470, color=LINE, sw=1.8))

    inner_hash, _, _ = textbox(300, 500,
                               "Внутрішній геш H: d_in = H(K_in || m)\n"
                               "Фіксований дайджест (наприклад, 32 байти для SHA-256)",
                               size=12, fill=SOFT_GREEN, stroke=BORDER_GREEN, bold=True)
    f.append(inner_hash)

    # Права гілка: Зовнішній прохід (opad)
    opad_xor, _, _ = textbox(900, 180,
                             "K_out = K' ⊕ opad\n(opad = 0x5C, повторений B разів)",
                             size=12, fill=SOFT_WARN, stroke=BORDER_WARN, bold=True)
    f.append(opad_xor)

    # Стрілка від d_in до зовнішньої конкатенації
    f.append(arrow(460, 500, 740, 500, color=FIELD, sw=2.0))

    outer_concat, _, _ = textbox(900, 500,
                                 "Конкатенація: [ K_out || Внутрішній дайджест d_in ]\n"
                                 "Рівно B + L байтів (наприклад, 64 + 32 = 96 байтів)",
                                 size=12, fill=SOFT_WARN, stroke=BORDER_WARN)
    f.append(outer_concat)

    f.append(arrow(900, 220, 900, 460, color=LINE, sw=1.8))
    f.append(arrow(900, 545, 900, 610, color=LINE, sw=1.8))

    # Зовнішній геш -> Результат HMAC
    final_hmac, _, _ = textbox(900, 650,
                               "Зовнішній геш H: HMAC(K, m) = H(K_out || d_in)\n"
                               "Фінальний код автентичності повідомлення",
                               size=13, fill=SOFT_BLUE, stroke=BORDER_BLUE, bold=True)
    f.append(final_hmac)

    # Примітка про захист
    f.append(text(600, 745,
                  "Зовнішній геш закриває вихід внутрішнього геша — стан внутрішнього стиснення не виходить назовні",
                  size=12, color=FIELD, bold=True))

    render(os.path.join(OUT, 'fig-hmac-structure.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Екосистема застосування HMAC у мережевих протоколах
# ─────────────────────────────────────────────────────────────────────────────
def fig_protocol_roles():
    W, H = 1220, 760
    f = []

    # Центральний вузол HMAC
    core, _, _ = textbox(610, 80,
                         "HMAC: Універсальний криптографічний примітив автентичності\n"
                         "RFC 2104 / FIPS 198-1 (Псевдовипадкова функція PRF)",
                         size=14, fill=SOFT_BLUE, stroke=BORDER_BLUE, bold=True)
    f.append(core)

    protocols = [
        ("IPsec (AH / ESP)",
         "Захист мережевого рівня L3:\n"
         "Автентифікація IP-пакетів,\n"
         "захист від підміни заголовків\n"
         "та ін'єкції шкідливого трафіку",
         150, 260, SOFT_GREEN, BORDER_GREEN),

        ("TLS 1.2 / 1.3 (HKDF)",
         "Захист транспортного рівня:\n"
         "Контроль цілісності записів,\n"
         "деривація ключів сесії у TLS 1.3\n"
         "через функцію HKDF (RFC 5869)",
         380, 480, SOFT_BLUE, BORDER_BLUE),

        ("JSON Web Tokens (JWT)",
         "Веб-автентифікація без стану:\n"
         "Підпис заголовка і корисного\n"
         "навантаження алгоритмом HS256\n"
         "(HMAC-SHA256)",
         610, 260, SOFT_WARN, BORDER_WARN),

        ("PBKDF2 (Зберігання паролів)",
         "Захист від перебору за словником:\n"
         "Тисячі ітерацій HMAC(пароль, сіль)\n"
         "для сповільнення атак на GPU\n"
         "та формування ключів шифрування",
         840, 480, SOFT_GREEN, BORDER_GREEN),

        ("TOTP / HOTP (2FA)",
         "Двофакторна автентифікація:\n"
         "HMAC-SHA1(секрет, лічильник/час)\n"
         "із динамічним усіканням до\n"
         "6-значного одноразового коду",
         1070, 260, SOFT_BLUE, BORDER_BLUE),
    ]

    for title, desc, cx, cy, fill, stroke in protocols:
        b, _, _ = textbox(cx, cy, title + "\n" + desc, size=11, fill=fill, stroke=stroke)
        f.append(b)
        f.append(arrow(610, 120, cx, cy - 65, color=MUTED, sw=1.5))

    f.append(text(610, 710,
                  "HMAC є фундаментом як цілісності даних у мережі, так і деривації ключів та автентифікації користувачів",
                  size=12, color=INK, bold=True))

    render(os.path.join(OUT, 'fig-protocol-roles.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Атака за часом виконання (Timing Attack) проти Constant-Time перевірки
# ─────────────────────────────────────────────────────────────────────────────
def fig_timing_attack():
    W, H = 1200, 720
    f = []

    # Ліва колонка: Вразлива перевірка memcmp
    h_vuln, _, _ = textbox(300, 60,
                           "Вразливо: Ранній вихід (memcmp / operator==)\n"
                           "if (a[i] != b[i]) return false;",
                           size=13, fill=SOFT_RED, stroke=BORDER_RED, bold=True)
    f.append(h_vuln)

    v1, _, _ = textbox(300, 160,
                       "Кандидат 1: [ 0xAA ... ] != Очікуваний [ 0x55 ... ]\n"
                       "Незбіг на байті 0 -> Миттєвий вихід (t = 12 нс)",
                       size=11, fill=FILL, stroke=LINE)
    f.append(v1)

    v2, _, _ = textbox(300, 260,
                       "Кандидат 2: [ 0x55, 0xBB ... ] != [ 0x55, 0x77 ... ]\n"
                       "Незбіг на байті 1 -> Вихід після 2 порівнянь (t = 18 нс)",
                       size=11, fill=FILL, stroke=LINE)
    f.append(v2)

    v3, _, _ = textbox(300, 360,
                       "Кандидат 3: [ 0x55, 0x77, 0xCC ... ] != [ 0x55, 0x77, 0x33 ... ]\n"
                       "Незбіг на байті 2 -> Вихід після 3 порівнянь (t = 24 нс)",
                       size=11, fill=FILL, stroke=LINE)
    f.append(v3)

    leak_box, _, _ = textbox(300, 480,
                             "Витік інформації через час відповіді:\n"
                             "Зловмисник підбирає підпис побайтово!\n"
                             "256 варіантів * 32 байти = 8192 спроби\n"
                             "замість 2^256 варіантів повного перебору.",
                             size=11, fill=SOFT_RED, stroke=BORDER_RED, bold=True)
    f.append(leak_box)

    # Розділювач
    f.append(line(600, 40, 600, 640, color=MUTED, sw=1.5, dash="6,6"))

    # Права колонка: Безпечна константна перевірка
    h_safe, _, _ = textbox(900, 60,
                           "Безпечно: Константний час (CRYPTO_memcmp)\n"
                           "diff |= (a[i] ^ b[i]); ... return (diff == 0);",
                           size=13, fill=SOFT_GREEN, stroke=BORDER_GREEN, bold=True)
    f.append(h_safe)

    s1, _, _ = textbox(900, 160,
                       "Кандидат 1: [ 0xAA ... ]\n"
                       "Обробляються ВСІ 32 байти -> Час t = 85 нс",
                       size=11, fill=FILL, stroke=LINE)
    f.append(s1)

    s2, _, _ = textbox(900, 260,
                       "Кандидат 2: [ 0x55, 0xBB ... ]\n"
                       "Обробляються ВСІ 32 байти -> Час t = 85 нс",
                       size=11, fill=FILL, stroke=LINE)
    f.append(s2)

    s3, _, _ = textbox(900, 360,
                       "Кандидат 3: [ 0x55, 0x77, 0xCC ... ]\n"
                       "Обробляються ВСІ 32 байти -> Час t = 85 нс",
                       size=11, fill=FILL, stroke=LINE)
    f.append(s3)

    safe_box, _, _ = textbox(900, 480,
                             "Нульовий витік інформації:\n"
                             "Час виконання суворо однаковий\n"
                             "незалежно від кількості співпалих байтів.\n"
                             "Побайтовий підбір стає неможливим.",
                             size=11, fill=SOFT_GREEN, stroke=BORDER_GREEN, bold=True)
    f.append(safe_box)

    f.append(text(600, 680,
                  "Перевірка автентичності підпису вимагає константного часу виконання без умовних переходів",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'fig-timing-attack.svg'), W, H, *f)


if __name__ == '__main__':
    fig_length_extension()
    fig_hmac_structure()
    fig_protocol_roles()
    fig_timing_attack()
    print("Всі 4 фігури згенеровано успішно.")
