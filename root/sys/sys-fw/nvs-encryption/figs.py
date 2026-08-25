# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── conflict: чому стандартний Flash Encryption несумісний з NVS ──────────────
def fig_conflict():
    W, H = 760, 330
    p = []

    # Ліва колонка — Flash Encryption
    lx, ly, lw, lh = 40, 60, 320, 210
    p.append(rect(lx, ly, lw, lh, fill="#fff8f6", stroke=POS, sw=1.8, rx=10))
    p.append(text(lx + lw / 2, ly + 24, "Апаратний Flash Encryption", size=13, color=POS, bold=True))
    p.append(text(lx + lw / 2, ly + 44, "Блочний шифр AES-XTS (по 32 байти)", size=10, color=MUTED))

    p.append(rect(lx + 16, ly + 62, lw - 32, 46, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    p.append(text(lx + lw / 2, ly + 80, "Зміна стану: 11 → 10 (гасимо 1 біт)", size=11, color=INK, bold=True))
    p.append(text(lx + lw / 2, ly + 96, "Лавинний ефект: усі 32 байти шифру інші", size=10, color=POS))

    p.append(rect(lx + 16, ly + 120, lw - 32, 72, fill="#fdecea", stroke=POS, sw=1.2, rx=6))
    p.append(text(lx + lw / 2, ly + 140, "ПОМИЛКА ЗАПИСУ FLASH", size=11, color=POS, bold=True))
    p.append(text(lx + lw / 2, ly + 158, "Шифротекст вимагає 0 → 1 без стирання;", size=10, color=INK))
    p.append(text(lx + lw / 2, ly + 176, "потрібно прати весь сектор 4 КБ!", size=10, color=POS, bold=True))

    # Права колонка — NVS Encryption
    rx, ry, rw, rh = 400, 60, 320, 210
    p.append(rect(rx, ry, rw, rh, fill="#f6fbf7", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(rx + rw / 2, ry + 24, "Шифрування NVS (ESP-IDF)", size=13, color=FIELD, bold=True))
    p.append(text(rx + rw / 2, ry + 44, "Дворівневе розділення заголовків і даних", size=10, color=MUTED))

    p.append(rect(rx + 16, ry + 62, rw - 32, 46, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(rx + rw / 2, ry + 80, "Заголовки й бітова карта — ВІДКРИТІ", size=11, color=INK, bold=True))
    p.append(text(rx + rw / 2, ry + 96, "Біти 11 → 10 → 00 гасяться прямо у Flash", size=10, color=FIELD))

    p.append(rect(rx + 16, ry + 120, rw - 32, 72, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(rx + rw / 2, ry + 140, "ТІЛО ЗАПИСУ — ЗАШИФРОВАНЕ", size=11, color=FIELD, bold=True))
    p.append(text(rx + rw / 2, ry + 158, "Кожен запис шифрується AES-XTS окремо;", size=10, color=INK))
    p.append(text(rx + rw / 2, ry + 176, "tweak прив'язаний до адреси запису", size=10, color=FIELD, bold=True))

    p.append(text(W / 2, H - 18,
                  "NVS лишає службові прапорці відкритими для гасіння бітів 1→0, шифруючи лише корисні дані",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "conflict.svg"), W, H, *p,
           title="Чому Flash Encryption несумісний із прямим оновленням NVS")


# ── page-anatomy: анатомія зашифрованої сторінки NVS ─────────────────────────
def fig_page_anatomy():
    W, H = 760, 360
    p = []

    # Загальна рамка сторінки 4096 байтів
    px, py, pw, ph = 30, 56, 700, 256
    p.append(rect(px, py, pw, ph, fill="#fbfbff", stroke=INK, sw=1.8, rx=10))
    p.append(text(px + 16, py + 24, "Сторінка NVS (розмір 4096 байтів = 1 сектор Flash)", size=13, color=INK, anchor="start", bold=True))

    # Блок 1: Заголовок сторінки (32 байти, відкритий)
    b1_x, b1_y, b1_w, b1_h = px + 16, py + 42, 200, 175
    p.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#fff8f0", stroke="#d97706", sw=1.5, rx=6))
    p.append(text(b1_x + b1_w / 2, b1_y + 22, "Заголовок сторінки", size=12, color="#d97706", bold=True))
    p.append(text(b1_x + b1_w / 2, b1_y + 38, "32 байти (ВІДКРИТИЙ)", size=10, color=MUTED, bold=True))
    p.append(line(b1_x + 10, b1_y + 48, b1_x + b1_w - 10, b1_y + 48, color="#d97706", sw=0.8))
    p.append(text(b1_x + 14, b1_y + 70, "• Стан: Active / Full / Freeing", size=10, color=INK, anchor="start"))
    p.append(text(b1_x + 14, b1_y + 92, "• Порядковий номер (seq)", size=10, color=INK, anchor="start"))
    p.append(text(b1_x + 14, b1_y + 114, "• Версія формату NVS", size=10, color=INK, anchor="start"))
    p.append(text(b1_x + 14, b1_y + 136, "• CRC32 заголовка", size=10, color=INK, anchor="start"))
    p.append(text(b1_x + b1_w / 2, b1_y + 160, "Гасіння бітів без стирання", size=9, color="#d97706", italic=True))

    # Блок 2: Бітова карта стану записів (32 байти, відкрита)
    b2_x, b2_y, b2_w, b2_h = px + 228, py + 42, 210, 175
    p.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#fff8f0", stroke="#d97706", sw=1.5, rx=6))
    p.append(text(b2_x + b2_w / 2, b2_y + 22, "Бітова карта записів", size=12, color="#d97706", bold=True))
    p.append(text(b2_x + b2_w / 2, b2_y + 38, "32 байти = 256 бітів (ВІДКРИТА)", size=10, color=MUTED, bold=True))
    p.append(line(b2_x + 10, b2_y + 48, b2_x + b2_w - 10, b2_y + 48, color="#d97706", sw=0.8))
    p.append(text(b2_x + 14, b2_y + 70, "• 128 слотів × 2 біти стану", size=10, color=INK, anchor="start"))
    p.append(text(b2_x + 14, b2_y + 92, "• 11 = Порожній (Empty)", size=10, color=MUTED, anchor="start", bold=True))
    p.append(text(b2_x + 14, b2_y + 114, "• 10 = Записаний (Written)", size=10, color=FIELD, anchor="start", bold=True))
    p.append(text(b2_x + 14, b2_y + 136, "• 00 = Стертий (Erased)", size=10, color=POS, anchor="start", bold=True))
    p.append(text(b2_x + b2_w / 2, b2_y + 160, "Керує збиранням сміття", size=9, color="#d97706", italic=True))

    # Блок 3: 126 слотів записів (ЗАШИФРОВАНІ)
    b3_x, b3_y, b3_w, b3_h = px + 450, py + 42, 234, 175
    p.append(rect(b3_x, b3_y, b3_w, b3_h, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(b3_x + b3_w / 2, b3_y + 22, "126 слотів записів", size=12, color=FIELD, bold=True))
    p.append(text(b3_x + b3_w / 2, b3_y + 38, "126 × 32 байти (AES-XTS-256)", size=10, color=FIELD, bold=True))
    p.append(line(b3_x + 10, b3_y + 48, b3_x + b3_w - 10, b3_y + 48, color=FIELD, sw=0.8))
    p.append(text(b3_x + 14, b3_y + 70, "• Простір імен (Namespace ID)", size=10, color=INK, anchor="start"))
    p.append(text(b3_x + 14, b3_y + 92, "• Ім'я ключа (до 15 символів)", size=10, color=INK, anchor="start"))
    p.append(text(b3_x + 14, b3_y + 114, "• Тип даних, розмір, Span", size=10, color=INK, anchor="start"))
    p.append(text(b3_x + 14, b3_y + 136, "• Значення / зсув блоба", size=10, color=INK, anchor="start"))
    p.append(text(b3_x + b3_w / 2, b3_y + 160, "Tweak = зміщення слота у розділі", size=9, color=FIELD, bold=True))

    p.append(text(W / 2, py + 232,
                  "Заголовки сторінки й карта стану лишаються відкритими; тіло кожного 32-байтового слота шифрується окремо",
                  size=11, color=INK, bold=True))

    p.append(text(W / 2, H - 10,
                  "Унікальний tweak (зсув запису у розділі) захищає від атак перестановки шифроблоків між позиціями Flash",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "page-anatomy.svg"), W, H, *p,
           title="Анатомія зашифрованої сторінки NVS")


# ── key-hierarchy: багаторівнева ієрархія ключів ─────────────────────────────
def fig_key_hierarchy():
    W, H = 760, 310
    p = []

    steps = [
        ("eFuse (BLOCK4..9)", "Апаратний ключ Flash Enc", "Захист від читання ззовні", POS, "#fff8f6"),
        ("Flash Encryption", "AES-XTS дешифрування", "Прозорий доступ через MMU", "#d97706", "#fffbf0"),
        ("Розділ nvs_keys", "64-байтовий ключ XTS", "Зашифрований у Flash (4 КБ)", FIELD, "#f6fbf7"),
        ("Ключ у RAM", "nvs_sec_cfg_t", "Ключі шифрування + tweak", NEG, "#f0f6ff"),
        ("Розділ nvs", "Зашифровані записи", "Wi-Fi паролі, сертифікати", FIELD, "#eafaf0"),
    ]

    sw, sh = 132, 160
    gap = (W - 5 * sw) / 6
    y = 65

    for i, (title, sub, note, col, fill) in enumerate(steps):
        x = gap + i * (sw + gap)
        p.append(rect(x, y, sw, sh, fill=fill, stroke=col, sw=1.7, rx=8))
        p.append(text(x + sw / 2, y + 24, "Рівень %d" % (i + 1), size=10, color=MUTED, bold=True))
        p.append(text(x + sw / 2, y + 46, title, size=10, color=col, bold=True))
        p.append(line(x + 8, y + 58, x + sw - 8, y + 58, color=col, sw=0.8))
        p.append(mtext(x + sw / 2, y + 78, sub, size=10, color=INK, bold=True, lh=1.25))
        p.append(mtext(x + sw / 2, y + 124, note, size=9, color=MUTED, lh=1.25))

        if i < len(steps) - 1:
            ax1 = x + sw + 2
            ax2 = x + sw + gap - 2
            p.append(arrow(ax1, y + sh / 2, ax2, y + sh / 2, color=LINE, sw=1.6))

    p.append(text(W / 2, H - 38,
                  "Ієрархія довіри: Апаратний eFuse → Flash Encryption → nvs_keys → RAM nvs_sec_cfg_t → NVS дані",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, H - 16,
                  "Компрометація Flash пам'яті не розкриває секретів: без зашитого eFuse розшифрувати nvs_keys неможливо",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "key-hierarchy.svg"), W, H, *p,
           title="Багаторівнева ієрархія ключів шифрування NVS")


# ── init-flow: послідовність безпечної ініціалізації ──────────────────────────
def fig_init_flow():
    W, H = 760, 310
    p = []

    boxes = [
        (40, 70, 150, 80, "1. Знайти розділи", "nvs та nvs_key\nу Partition Table", INK, FILL),
        (230, 70, 150, 80, "2. Читати ключ", "nvs_flash_read_\nsecurity_cfg()", NEG, "#f0f6ff"),
        (420, 70, 150, 80, "3. Перевірити ключ", "Знайдено? Чи ключ\nще не записано?", "#d97706", "#fffbf0"),
        (610, 70, 120, 80, "4а. Генерація", "Генерація TRNG\nта запис у Flash", POS, "#fff8f6"),
        (420, 190, 150, 70, "4б. Secure Init", "nvs_flash_secure_\ninit_partition()", FIELD, "#eafaf0"),
        (40, 190, 340, 70, "5. Готово до роботи", "nvs_open_from_partition() → get / set / commit\nПовне шифрування прозоре для програми", FIELD, "#f6fbf7"),
    ]

    for bx, by, bw, bh, title, desc, col, fill in boxes:
        p.append(rect(bx, by, bw, bh, fill=fill, stroke=col, sw=1.6, rx=8))
        p.append(text(bx + bw / 2, by + 20, title, size=11, color=col, bold=True))
        p.append(mtext(bx + bw / 2, by + 42, desc, size=10, color=INK, lh=1.25))

    # Стрілки
    p.append(arrow(190, 110, 230, 110, color=LINE, sw=1.5))
    p.append(arrow(380, 110, 420, 110, color=LINE, sw=1.5))

    # Якщо немає ключів -> генерація (праворуч)
    p.append(arrow(570, 110, 610, 110, color=POS, sw=1.5))
    p.append(text(590, 98, "Немає", size=10, color=POS, bold=True))

    # З генерації -> вниз до Secure Init
    p.append('<path d="M670 150 L670 225 L570 225" fill="none" stroke="%s" stroke-width="1.5" marker-end="url(#arrow)"/>' % POS)

    # Якщо є ключі -> вниз до Secure Init
    p.append(arrow(495, 150, 495, 190, color=FIELD, sw=1.5))
    p.append(text(515, 170, "Є ключ", size=10, color=FIELD, bold=True))

    # З Secure Init -> ліворуч до Готово
    p.append(arrow(420, 225, 380, 225, color=FIELD, sw=1.5))

    p.append(text(W / 2, H - 14,
                  "Автоматичний життєвий цикл: читання наявних ключів або безпечна одноразова генерація через TRNG",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "init-flow.svg"), W, H, *p,
           title="Послідовність безпечної ініціалізації NVS")


# ── host-vs-device: генерація на хості проти генерації на чіпі ────────────────
def fig_host_vs_device():
    W, H = 760, 310
    p = []

    # Ліва половина — Хост (Виробництво)
    lx, ly, lw, lh = 40, 60, 320, 195
    p.append(rect(lx, ly, lw, lh, fill="#f0f6ff", stroke=NEG, sw=1.8, rx=10))
    p.append(text(lx + lw / 2, ly + 24, "1. Підготовка на хості (Виробництво)", size=12, color=NEG, bold=True))
    p.append(text(lx + lw / 2, ly + 42, "Масове виготовлення однакових/унікальних партій", size=10, color=MUTED))

    p.append(rect(lx + 16, ly + 56, lw - 32, 38, fill="#ffffff", stroke=NEG, sw=1.1, rx=5))
    p.append(text(lx + lw / 2, ly + 72, "nvs_partition_gen.py generate-key", size=10, color=INK, bold=True))
    p.append(text(lx + lw / 2, ly + 86, "Створює бінарний файл nvs_keys.bin (64B)", size=9, color=MUTED))

    p.append(rect(lx + 16, ly + 100, lw - 32, 38, fill="#ffffff", stroke=NEG, sw=1.1, rx=5))
    p.append(text(lx + lw / 2, ly + 116, "nvs_partition_gen.py encrypt", size=10, color=INK, bold=True))
    p.append(text(lx + lw / 2, ly + 130, "Попередній запис заводських сертифікатів", size=9, color=MUTED))

    p.append(rect(lx + 16, ly + 144, lw - 32, 38, fill="#eaf0fd", stroke=NEG, sw=1.1, rx=5))
    p.append(text(lx + lw / 2, ly + 160, "esptool.py write_flash --encrypt", size=10, color=NEG, bold=True))
    p.append(text(lx + lw / 2, ly + 174, "Прошивання з апаратним Flash Encryption", size=9, color=INK))

    # Права половина — Чип (Self-provisioning)
    rx, ry, rw, rh = 400, 60, 320, 195
    p.append(rect(rx, ry, rw, rh, fill="#f6fbf7", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(rx + rw / 2, ry + 24, "2. Автономна генерація на чіпі", size=12, color=FIELD, bold=True))
    p.append(text(rx + rw / 2, ry + 42, "Самостійне створення ключів під час першого запуску", size=10, color=MUTED))

    p.append(rect(rx + 16, ry + 56, rw - 32, 38, fill="#ffffff", stroke=FIELD, sw=1.1, rx=5))
    p.append(text(rx + rw / 2, ry + 72, "Апаратний генератор випадкових чисел (TRNG)", size=10, color=INK, bold=True))
    p.append(text(rx + rw / 2, ry + 86, "esp_fill_random() генерує 64 байти в RAM", size=9, color=MUTED))

    p.append(rect(rx + 16, ry + 100, rw - 32, 38, fill="#ffffff", stroke=FIELD, sw=1.1, rx=5))
    p.append(text(rx + rw / 2, ry + 116, "nvs_flash_generate_keys()", size=10, color=INK, bold=True))
    p.append(text(rx + rw / 2, ry + 130, "Записує nvs_sec_cfg_t у розділ nvs_key", size=9, color=MUTED))

    p.append(rect(rx + 16, ry + 144, rw - 32, 38, fill="#eafaf0", stroke=FIELD, sw=1.1, rx=5))
    p.append(text(rx + rw / 2, ry + 160, "Апаратний Flash Enc захищає nvs_key", size=10, color=FIELD, bold=True))
    p.append(text(rx + rw / 2, ry + 174, "Ключі NVS надійно замкнені у Flash пам'яті", size=9, color=INK))

    p.append(text(W / 2, H - 26,
                  "Хостовий підхід дозволяє прошивати попередньо заповнений NVS; автономний спрощує конвеєр збірки",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, H - 10,
                  "В обох випадках кінцева стійкість гарантована апаратним шифруванням Flash Encryption",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "host-vs-device.svg"), W, H, *p,
           title="Два шляхи налаштування ключів NVS")


if __name__ == "__main__":
    fig_conflict()
    fig_page_anatomy()
    fig_key_hierarchy()
    fig_init_flow()
    fig_host_vs_device()
    print("OK: 5 figures written to", OUT)
