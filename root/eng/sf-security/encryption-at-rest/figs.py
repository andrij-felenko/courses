# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── storage-levels: 4 рівні шифрування у спокої ─────────────────────────────
# Ідея: захист можна вбудувати на 4 різних рівнях системи; чим вище рівень,
# тим вища вибірковість і захист від привілейованих процесів, але більша інтеграція.

def fig_storage_levels():
    W, H = 820, 360
    p = []
    
    levels = [
        ("Апаратний (SED / NVMe OPAL)", "Шифрування контролером накопичувача", "Захист: крадіжка фізичного носія", "#f4f6f8", LINE),
        ("Блоковий (dm-crypt / LUKS)", "Прозоре шифрування секторів/розділів ОС", "Захист: вилучення диска з сервера", "#eaf0fd", NEG),
        ("Файловий (fscrypt / eCryptfs)", "Шифрування окремих каталогів під юзера", "Захист: доступ між користувачами ОС", "#fff6e0", "#caa24a"),
        ("Прикладний (Конвертне / KMS)", "Шифрування об'єктів у коді додатка", "Захист: злив бази, зловмисний root/DBA", "#eaf6ec", FIELD)
    ]
    
    y = 50
    for title, desc, threat, fill, stroke in levels:
        p.append(rect(40, y, 740, 62, fill=fill, stroke=stroke, sw=1.8, rx=8))
        p.append(text(60, y + 26, title, size=13, color=INK, bold=True, anchor="start"))
        p.append(text(60, y + 48, desc, size=11, color=MUTED, anchor="start"))
        p.append(rect(480, y + 14, 285, 34, fill="#ffffff", stroke=stroke, sw=1.2, rx=6))
        p.append(text(622, y + 36, threat, size=11, color=stroke, bold=True, anchor="middle"))
        y += 72

    p.append(text(W / 2, 342, "Чим вище рівень в ієрархії, тим вужче межа довіри й вища гранулярність ключів.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "storage-levels.svg"), W, H, *p,
           title="Рівні шифрування даних у спокої та межі загроз")


# ── envelope-hierarchy: ієрархія ключів HSM -> KEK -> DEK -> Дані ──────────
# Ідея: корінь у HSM захищає KEK, KEK захищає DEK, DEK шифрує корисні дані.

def fig_envelope_hierarchy():
    W, H = 820, 320
    p = []
    
    # 1. HSM / Корінь
    p.append(rect(40, 50, 220, 190, fill="#fbecec", stroke=POS, sw=2, rx=10))
    p.append(text(150, 78, "Апаратний HSM", size=13, color=POS, bold=True))
    p.append(text(150, 98, "Апаратний корінь довіри", size=10, color=MUTED))
    b1, _, _ = textbox(150, 145, "Master / Root Key\n(Незмінний апаратний корінь)", size=10, color=POS,
                       fill="#ffffff", stroke=POS, bold=True, min_w=190)
    p.append(b1)
    p.append(text(150, 205, "Ключ не покидає чип", size=10, color=POS, bold=True))
    
    # Стрілка 1 -> 2
    p.append(arrow(260, 145, 300, 145, color=INK, sw=2))
    p.append(text(280, 135, "огортає", size=9, color=MUTED))
    
    # 2. KMS / KEK
    p.append(rect(300, 50, 220, 190, fill="#fff6e0", stroke="#caa24a", sw=2, rx=10))
    p.append(text(410, 78, "Сервіс KMS", size=13, color="#8a6d1a", bold=True))
    p.append(text(410, 98, "Керування доступом та аудитом", size=10, color=MUTED))
    b2, _, _ = textbox(410, 145, "KEK (Key Encryption Key)\n(Ключ шифрування ключів)", size=10, color="#8a6d1a",
                       fill="#ffffff", stroke="#caa24a", bold=True, min_w=190)
    p.append(b2)
    p.append(text(410, 205, "Автоматична ротація", size=10, color="#8a6d1a", bold=True))
    
    # Стрілка 2 -> 3
    p.append(arrow(520, 145, 560, 145, color=INK, sw=2))
    p.append(text(540, 135, "шифрує", size=9, color=MUTED))
    
    # 3. Додаток / DEK + Дані
    p.append(rect(560, 50, 220, 190, fill="#eaf6ec", stroke=FIELD, sw=2, rx=10))
    p.append(text(670, 78, "Сховище / Додаток", size=13, color=FIELD, bold=True))
    p.append(text(670, 98, "Швидке локальне шифрування", size=10, color=MUTED))
    b3, _, _ = textbox(670, 130, "DEK (Data Encryption Key)\n(Унікальний для запису/файлу)", size=10, color=FIELD,
                       fill="#ffffff", stroke=FIELD, bold=True, min_w=190)
    p.append(b3)
    b4, _, _ = textbox(670, 190, "Зашифроване тіло даних\n(AES-256-GCM шифротекст)", size=10, color=INK,
                       fill="#ffffff", stroke=LINE, min_w=190)
    p.append(b4)
    
    p.append(fitbox(60, 255, 700, 48,
                    "Ієрархія розділяє обов'язки: KMS управляє та ротує KEK без передачі сирих ключів додатку,\n"
                    "а додаток локально шифрує гігабайти даних унікальним DEK без мережевих затримок на кожен блок.",
                    size=10, color=INK, fill="#fbfbfb", stroke=MUTED, sw=1.2))
    render(os.path.join(OUT, "envelope-hierarchy.svg"), W, H, *p,
           title="Ієрархія ключів: Root Key -> KEK -> DEK -> Дані")


# ── envelope-flow: двофазний життєвий цикл конверта ─────────────────────────
# Ідея: шифрування (запит DEK -> шифрування локально -> зачистка RAM -> збереження)
# та розшифрування (читання -> розгортання DEK у KMS -> розшифрування -> зачистка).

def fig_envelope_flow():
    W, H = 820, 360
    p = []
    
    # Ліва колонка — Шифрування
    p.append(rect(40, 40, 355, 270, fill="#f9fbf9", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(217, 65, "1. Процес шифрування (Запис)", size=13, color=FIELD, bold=True))
    
    enc_steps = [
        "1. Додаток шле GenerateDataKey(KEK, AAD)",
        "2. KMS генерує DEK і повертає {Plain, Wrapped}",
        "3. Додаток шифрує payload ключем Plain DEK",
        "4. Plain DEK негайно затирається в RAM (zeroize)",
        "5. Збереження {Wrapped DEK + Ciphertext + Tag}"
    ]
    ey = 95
    for st in enc_steps:
        p.append(rect(55, ey, 325, 30, fill="#ffffff", stroke=FIELD, sw=1.1, rx=5))
        p.append(text(65, ey + 19, st, size=10, color=INK, anchor="start"))
        ey += 38
        
    # Права колонка — Розшифрування
    p.append(rect(425, 40, 355, 270, fill="#f0f4fd", stroke=NEG, sw=1.8, rx=10))
    p.append(text(602, 65, "2. Процес розшифрування (Читання)", size=13, color=NEG, bold=True))
    
    dec_steps = [
        "1. Додаток зчитує {Wrapped DEK, Ciphertext, Tag}",
        "2. Додаток шле Decrypt(Wrapped DEK, AAD) до KMS",
        "3. KMS перевіряє права та повертає Plain DEK",
        "4. Додаток розшифровує та верифікує Tag",
        "5. Plain DEK негайно затирається в RAM (zeroize)"
    ]
    dy = 95
    for st in dec_steps:
        p.append(rect(440, dy, 325, 30, fill="#ffffff", stroke=NEG, sw=1.1, rx=5))
        p.append(text(450, dy + 19, st, size=10, color=INK, anchor="start"))
        dy += 38

    p.append(text(W / 2, 335, "Відкритий ключ DEK живе в пам'яті лише мілісекунди під час операції AES-GCM.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "envelope-flow.svg"), W, H, *p,
           title="Двофазний потік конвертного шифрування та розшифрування")


# ── crypto-shredding: миттєве знищення та дешева ротація ─────────────────────
# Ідея: знищення 256 бітів ключа стирає петабайти; ротація KEK не вимагає перешифрування даних.

def fig_crypto_shredding():
    W, H = 820, 270
    p = []
    
    # Ліва картка — Миттєве криптографічне стирання
    p.append(rect(40, 45, 355, 175, fill="#fbecec", stroke=POS, sw=1.8, rx=10))
    p.append(text(217, 72, "Криптографічне стирання (Crypto-Shredding)", size=12, color=POS, bold=True))
    p.append(text(217, 95, "Знищення 256-бітного ключа KEK або DEK", size=10, color=INK))
    
    b1, _, _ = textbox(217, 135, "Петабайти шифротексту на диску\nстають нерозрізненним шумом",
                       size=10, color=POS, fill="#ffffff", stroke=POS, bold=True, min_w=310)
    p.append(b1)
    p.append(text(217, 185, "Миттєве виконання GDPR Right to be Forgotten", size=9, color=MUTED))
    
    # Права картка — Дешева ротація ключів
    p.append(rect(425, 45, 355, 175, fill="#eaf6ec", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(602, 72, "Безперервна ротація KEK (Re-wrapping)", size=12, color=FIELD, bold=True))
    p.append(text(602, 95, "Оновлення KEKv1 -> KEKv2 у KMS", size=10, color=INK))
    
    b2, _, _ = textbox(602, 135, "Перешифровується лише 32 байти DEK,\nсамі гігабайти даних лишаються без змін",
                       size=10, color=FIELD, fill="#ffffff", stroke=FIELD, bold=True, min_w=310)
    p.append(b2)
    p.append(text(602, 185, "Нульовий оверхед на дискове I/O", size=9, color=MUTED))

    p.append(text(W / 2, 248, "Конвертна архітектура перетворює важкі операції з даними на легкі операції над ключами.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "crypto-shredding.svg"), W, H, *p,
           title="Криптографічне знищення даних та дешева ротація ключів")


if __name__ == "__main__":
    fig_storage_levels()
    fig_envelope_hierarchy()
    fig_envelope_flow()
    fig_crypto_shredding()
    print("figs: 4 written to", OUT)
