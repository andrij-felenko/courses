# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. e2ee-vs-transport: TLS проти E2EE ─────────────────────────────────────
def fig_e2ee_vs_transport():
    W, H = 760, 310
    p = []

    # Верхній блок: Транспортне шифрування (TLS / HTTPS)
    p.append(rect(30, 25, 700, 120, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(380, 46, "Транспортне шифрування (TLS) — термінація на сервері", size=13, color=POS, bold=True))
    
    # Клієнт А
    b_ca, _, _ = textbox(110, 85, "Клієнт А\n(Аліса)", size=11, color=INK, fill="#ffffff", stroke=LINE, min_w=100)
    p.append(b_ca)
    
    # Сервер (посередині)
    b_srv, _, _ = textbox(380, 85, "Сервер / Провайдер\n[ВІДКРИТИЙ ТЕКСТ У RAM]", size=11, color=POS, fill="#fff5f5", stroke=POS, bold=True, min_w=190)
    p.append(b_srv)
    
    # Клієнт Б
    b_cb, _, _ = textbox(650, 85, "Клієнт Б\n(Боб)", size=11, color=INK, fill="#ffffff", stroke=LINE, min_w=100)
    p.append(b_cb)

    # Канали
    p.append(arrow(170, 85, 275, 85, color=FIELD, sw=2))
    p.append(text(222, 75, "TLS-тунель 1", size=10, color=FIELD, bold=True))
    
    p.append(arrow(485, 85, 590, 85, color=FIELD, sw=2))
    p.append(text(537, 75, "TLS-тунель 2", size=10, color=FIELD, bold=True))
    
    p.append(text(380, 130, "Загроза: злам сервера, інсайдер або запит спецслужб відкриває листування", size=10, color=POS))

    # Нижній блок: Наскрізне шифрування (E2EE)
    p.append(rect(30, 160, 700, 130, fill="#f0f9f2", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(380, 181, "Наскрізне шифрування (E2EE) — ключ є лише у відправника й отримувача", size=13, color=FIELD, bold=True))

    # Клієнт А
    b_ea, _, _ = textbox(110, 225, "Клієнт А\n[Шифрування]", size=11, color=INK, fill="#ffffff", stroke=FIELD, bold=True, min_w=100)
    p.append(b_ea)

    # Сервер (посередник)
    b_esrv, _, _ = textbox(380, 225, "Релей-сервер\n(Бачить лише шифротекст)", size=11, color=MUTED, fill="#ffffff", stroke=MUTED, min_w=190)
    p.append(b_esrv)

    # Клієнт Б
    b_eb, _, _ = textbox(650, 225, "Клієнт Б\n[Дешифрування]", size=11, color=INK, fill="#ffffff", stroke=FIELD, bold=True, min_w=100)
    p.append(b_eb)

    # Наскрізний потік
    p.append(arrow(170, 225, 275, 225, color=NEG, sw=2))
    p.append(text(222, 215, "Шифротекст C", size=10, color=NEG, bold=True))
    
    p.append(arrow(485, 225, 590, 225, color=NEG, sw=2))
    p.append(text(537, 215, "Шифротекст C", size=10, color=NEG, bold=True))

    p.append(text(380, 274, "Безпека: навіть повний контроль над сервером не дає змоги прочитати повідомлення", size=10, color=FIELD))

    render(os.path.join(OUT, "e2ee-vs-transport.svg"), W, H, *p,
           title="Транспортне шифрування проти наскрізного")


# ── 2. x3dh-handshake: 4-компонентний обмін X3DH ────────────────────────────
def fig_x3dh_handshake():
    W, H = 760, 370
    p = []

    # Верхній ряд — Актори
    # Аліса (ініціатор)
    p.append(rect(30, 20, 210, 110, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    p.append(text(135, 42, "Аліса (ініціатор онлайн)", size=11, color=INK, bold=True))
    p.append(text(135, 65, "IK_A (довгостроковий)", size=10, color=MUTED))
    p.append(text(135, 85, "EK_A (ефемерний X25519)", size=10, color=MUTED))
    p.append(text(135, 107, "Генерує сесію асинхронно", size=9.5, color=FIELD))

    # Сервер ключів
    p.append(rect(275, 20, 210, 110, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=8))
    p.append(text(380, 42, "Сервер (Prekey Bundle)", size=11, color=INK, bold=True))
    p.append(text(380, 63, "IK_B (ідентифікатор)", size=9.5, color=INK))
    p.append(text(380, 80, "SPK_B + Sig(SPK_B)", size=9.5, color=FIELD))
    p.append(text(380, 97, "OPK_B (одноразовий)", size=9.5, color=NEG))
    p.append(text(380, 116, "Боб офлайн у сховищі", size=9, color=MUTED, italic=True))

    # Боб (отримувач)
    p.append(rect(520, 20, 210, 110, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    p.append(text(625, 42, "Боб (отримувач офлайн)", size=11, color=INK, bold=True))
    p.append(text(625, 65, "IK_B (приватний ключ)", size=10, color=MUTED))
    p.append(text(625, 85, "SPK_B (приватний прекей)", size=10, color=MUTED))
    p.append(text(625, 107, "OPK_B (одноразовий приватний)", size=9.5, color=MUTED))

    # Стрілка отримання бандла
    p.append(arrow(240, 60, 275, 60, color=MUTED, sw=1.5))
    p.append(text(257, 52, "GET", size=9, color=MUTED))

    # Середній блок: Обчислення 4x DH
    p.append(rect(30, 145, 700, 145, fill="#f7f9fc", stroke=NEG, sw=1.5, rx=8))
    p.append(text(380, 168, "Комбінація чотирьох обмінів Діффі — Геллмана (Extended Triple Diffie-Hellman)", size=12, color=NEG, bold=True))

    # 4 блоки DH усередині
    # DH1
    p.append(rect(45, 185, 155, 60, fill="#ffffff", stroke=LINE, sw=1, rx=6))
    p.append(text(122, 205, "DH1 = DH(IK_A, SPK_B)", size=10, color=INK, bold=True))
    p.append(text(122, 225, "Автентифікація Аліси", size=9.5, color=MUTED))

    # DH2
    p.append(rect(210, 185, 155, 60, fill="#ffffff", stroke=LINE, sw=1, rx=6))
    p.append(text(287, 205, "DH2 = DH(EK_A, IK_B)", size=10, color=INK, bold=True))
    p.append(text(287, 225, "Пряма секретність (PFS)", size=9.5, color=MUTED))

    # DH3
    p.append(rect(375, 185, 155, 60, fill="#ffffff", stroke=LINE, sw=1, rx=6))
    p.append(text(452, 205, "DH3 = DH(EK_A, SPK_B)", size=10, color=INK, bold=True))
    p.append(text(452, 225, "Сесійна пряма секретність", size=9.5, color=MUTED))

    # DH4
    p.append(rect(540, 185, 175, 60, fill="#ffffff", stroke=LINE, sw=1, rx=6))
    p.append(text(627, 205, "DH4 = DH(EK_A, OPK_B)", size=10, color=INK, bold=True))
    p.append(text(627, 225, "Захист від повтору (Replay)", size=9.5, color=MUTED))

    p.append(text(380, 268, "Майстер-ключ:  SK = KDF(DH1 || DH2 || DH3 || DH4)", size=11, color=FIELD, bold=True))

    # Нижній блок: Результат
    p.append(rect(30, 305, 700, 48, fill="#eef8f1", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(380, 334, "Результат: взаємна автентифікація та спільний секрет без одночасного перебування в мережі", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "x3dh-handshake.svg"), W, H, *p,
           title="Асинхронний протокол узгодження ключів X3DH")


# ── 3. double-ratchet-architecture: Дворівнева структура храповика ───────────
def fig_double_ratchet_architecture():
    W, H = 760, 350
    p = []

    # Верхній рівень: Асиметричний DH-храповик (Root KDF)
    p.append(rect(40, 25, 680, 130, fill="#edf4ff", stroke=NEG, sw=1.5, rx=8))
    p.append(text(380, 48, "Верхній рівень: Асиметричний DH-храповик (Root KDF Chain)", size=12, color=NEG, bold=True))
    p.append(text(380, 68, "Крок виконується при кожній зміні черги повідомлень (отримано новий публічний ключ DH)", size=10, color=MUTED))

    b_rk0, _, _ = textbox(130, 105, "Root Key (i)", size=11, color=INK, fill="#ffffff", stroke=LINE, min_w=110)
    p.append(b_rk0)

    p.append(arrow(190, 105, 270, 105, color=NEG, sw=2))
    p.append(text(230, 95, "+ DH secret", size=9, color=NEG, bold=True))

    b_kdf_root, _, _ = textbox(340, 105, "Root KDF\n(HKDF-Extract/Expand)", size=10, color=NEG, fill="#ffffff", stroke=NEG, min_w=130)
    p.append(b_kdf_root)

    p.append(arrow(410, 105, 490, 105, color=NEG, sw=2))
    p.append(text(450, 95, "новий RK", size=9, color=NEG, bold=True))

    b_rk1, _, _ = textbox(570, 105, "Root Key (i+1)", size=11, color=INK, fill="#ffffff", stroke=LINE, min_w=110)
    p.append(b_rk1)

    # Стрілка вниз до симетричного ланцюга
    p.append(arrow(340, 128, 340, 185, color=FIELD, sw=2))
    p.append(text(420, 160, "ініціалізує Chain Key", size=9, color=FIELD, bold=True))

    # Нижній рівень: Симетричний KDF-храповик (Sending / Receiving Chain)
    p.append(rect(40, 190, 680, 140, fill="#f2f9f4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(380, 212, "Нижній рівень: Симетричний KDF-храповик (Message KDF Chains)", size=12, color=FIELD, bold=True))
    p.append(text(380, 230, "Крок виконується на КОЖНЕ надіслане або отримане повідомлення", size=10, color=MUTED))

    b_ck0, _, _ = textbox(130, 270, "Chain Key (0)", size=10, color=INK, fill="#ffffff", stroke=LINE, min_w=100)
    p.append(b_ck0)

    p.append(arrow(185, 270, 255, 270, color=FIELD, sw=1.8))
    p.append(text(220, 260, "KDF_CK", size=9, color=FIELD))

    b_ck1, _, _ = textbox(310, 270, "Chain Key (1)", size=10, color=INK, fill="#ffffff", stroke=LINE, min_w=100)
    p.append(b_ck1)

    p.append(arrow(365, 270, 435, 270, color=FIELD, sw=1.8))
    p.append(text(400, 260, "KDF_CK", size=9, color=FIELD))

    b_ck2, _, _ = textbox(490, 270, "Chain Key (2)", size=10, color=INK, fill="#ffffff", stroke=LINE, min_w=100)
    p.append(b_ck2)

    # Message Keys стрілки вниз
    p.append(arrow(130, 290, 130, 315, color=POS, sw=1.5))
    p.append(text(130, 323, "MK 0 (AEAD)", size=9, color=POS, bold=True))

    p.append(arrow(310, 290, 310, 315, color=POS, sw=1.5))
    p.append(text(310, 323, "MK 1 (AEAD)", size=9, color=POS, bold=True))

    p.append(arrow(490, 290, 490, 315, color=POS, sw=1.5))
    p.append(text(490, 323, "MK 2 (AEAD)", size=9, color=POS, bold=True))

    render(os.path.join(OUT, "double-ratchet-architecture.svg"), W, H, *p,
           title="Архітектура подвійного храповика (Double Ratchet)")


# ── 4. kdf-chain-step: Односторонній крок симетричного ланцюга ───────────────
def fig_kdf_chain_step():
    W, H = 760, 240
    p = []

    p.append(rect(40, 25, 680, 195, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    p.append(text(380, 48, "Один крок симетричного KDF-ланцюга: пряма секретність (PFS)", size=12, color=INK, bold=True))

    b_ck_in, _, _ = textbox(130, 115, "Поточний ключ ланцюга\nCK_i", size=11, color=INK, fill="#ffffff", stroke=LINE, min_w=150)
    p.append(b_ck_in)

    p.append(arrow(210, 115, 300, 115, color=LINE, sw=2))

    # Блок HMAC/KDF
    b_kdf, _, _ = textbox(380, 115, "HMAC-SHA256\nКонстанти 0x01 / 0x02", size=11, color=NEG, fill="#eaf0fd", stroke=NEG, bold=True, min_w=150)
    p.append(b_kdf)

    # Вихід 1: Наступний Chain Key
    p.append(arrow(460, 95, 550, 95, color=FIELD, sw=2))
    b_ck_next, _, _ = textbox(630, 95, "Наступний ключ\nCK_{i+1}", size=10, color=FIELD, fill="#edf8f1", stroke=FIELD, bold=True, min_w=130)
    p.append(b_ck_next)

    # Вихід 2: Message Key
    p.append(arrow(460, 135, 550, 135, color=POS, sw=2))
    b_mk, _, _ = textbox(630, 135, "Ключ повідомлення\nMK_i (AEAD)", size=10, color=POS, fill="#fef2f2", stroke=POS, bold=True, min_w=130)
    p.append(b_mk)

    # Пояснення знизу
    p.append(text(380, 190, "Ключ CK_i та MK_i негайно стираються з пам'яті після використання. Злам CK_{i+1} не дає змоги обчислити MK_i назад.", size=9.5, color=MUTED))

    render(os.path.join(OUT, "kdf-chain-step.svg"), W, H, *p,
           title="Крок симетричного KDF-ланцюга")


# ── 5. break-in-recovery: Відновлення секретності після зламу ────────────────
def fig_break_in_recovery():
    W, H = 760, 270
    p = []

    p.append(rect(30, 20, 700, 230, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    p.append(text(380, 42, "Відновлення після компрометації (Post-Compromise Security / Break-in Recovery)", size=12, color=INK, bold=True))

    # Стан 1: Злам
    p.append(rect(50, 65, 190, 130, fill="#fee2e2", stroke=POS, sw=1.5, rx=6))
    p.append(text(145, 88, "Стан зламано", size=11, color=POS, bold=True))
    p.append(text(145, 110, "Зловмисник зняв дамп RAM:", size=9.5, color=INK))
    p.append(text(145, 126, "викрадено RK_0, CK_0, dh_priv", size=9, color=POS, bold=True))
    p.append(text(145, 155, "Пасивне читання поточних даних", size=9, color=MUTED))
    p.append(text(145, 175, "Минулі дані захищені (PFS)", size=9, color=FIELD))

    # Стрілка переходу
    p.append(arrow(245, 130, 285, 130, color=LINE, sw=2))

    # Стан 2: Генерація нової пари DH
    p.append(rect(290, 65, 180, 130, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    p.append(text(380, 88, "Крок DH-храповика", size=11, color=NEG, bold=True))
    p.append(text(380, 110, "Аліса генерує нову пару:", size=9.5, color=INK))
    p.append(text(380, 128, "(dh_priv_new, dh_pub_new)", size=9, color=NEG, bold=True))
    p.append(text(380, 155, "Надсилає dh_pub_new Бобу", size=9.5, color=INK))
    p.append(text(380, 175, "у заголовку повідомлення", size=9, color=MUTED))

    # Стрілка переходу
    p.append(arrow(475, 130, 515, 130, color=LINE, sw=2))

    # Стан 3: Повне зцілення
    p.append(rect(520, 65, 190, 130, fill="#eef8f1", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(615, 88, "Секретність відновлено", size=11, color=FIELD, bold=True))
    p.append(text(615, 110, "Боб надсилає відповідь:", size=9.5, color=INK))
    p.append(text(615, 128, "новий спільний секрет DH", size=9, color=FIELD, bold=True))
    p.append(text(615, 155, "Зловмисник не знає dh_priv_new", size=9, color=INK))
    p.append(text(615, 175, "Майбутній трафік знову таємний", size=9, color=FIELD, bold=True))

    p.append(text(380, 225, "Злам пам'яті тимчасовий: один повноцінний обмін повідомленнями повертає абсолютну таємницю", size=10, color=INK))

    render(os.path.join(OUT, "break-in-recovery.svg"), W, H, *p,
           title="Відновлення після компрометації")


# ── 6. out-of-order-skipped-keys: Буферизація пропущених ключів ─────────────
def fig_out_of_order_skipped_keys():
    W, H = 760, 270
    p = []

    p.append(rect(30, 20, 700, 230, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    p.append(text(380, 42, "Доставка з порушенням порядку (Out-of-Order) та збереження пропущених ключів", size=12, color=INK, bold=True))

    # Ліва частина: Вхідні повідомлення
    p.append(rect(50, 65, 200, 135, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=6))
    p.append(text(150, 88, "Послідовність у мережі", size=11, color=INK, bold=True))
    p.append(text(150, 112, "1. Повідомлення #0 (отримано)", size=9.5, color=FIELD))
    p.append(text(150, 132, "2. Повідомлення #1 (затримано)", size=9.5, color=POS))
    p.append(text(150, 152, "3. Повідомлення #2 (затримано)", size=9.5, color=POS))
    p.append(text(150, 172, "4. Повідомлення #3 (надійшло зараз)", size=9.5, color=NEG, bold=True))

    p.append(arrow(255, 130, 305, 130, color=LINE, sw=2))

    # Центральна частина: Механізм перемотування
    p.append(rect(310, 65, 190, 135, fill="#edf4ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(405, 88, "Перемотування KDF", size=11, color=NEG, bold=True))
    p.append(text(405, 112, "Розрахунок MK_1 → зберегти", size=9.5, color=INK))
    p.append(text(405, 132, "Розрахунок MK_2 → зберегти", size=9.5, color=INK))
    p.append(text(405, 152, "Розрахунок MK_3 → розшифрувати #3", size=9.5, color=FIELD, bold=True))
    p.append(text(405, 175, "CK оновлено до CK_4", size=9.5, color=NEG))

    p.append(arrow(505, 130, 555, 130, color=LINE, sw=2))

    # Права частина: Таблиця пропущених ключів (Skipped Keys Table)
    p.append(rect(560, 65, 150, 135, fill="#fffaf0", stroke="#d97706", sw=1.5, rx=6))
    p.append(text(635, 88, "Skipped Keys Table", size=11, color="#b45309", bold=True))
    p.append(text(635, 112, "Key: (DH, 1) → MK_1", size=9.5, color=INK))
    p.append(text(635, 132, "Key: (DH, 2) → MK_2", size=9.5, color=INK))
    p.append(text(635, 160, "Ліміт розміру (M)", size=9.5, color=MUTED))
    p.append(text(635, 178, "Таймаут життя ключів", size=9.5, color=MUTED))

    p.append(text(380, 225, "Коли повідомлення #1 та #2 надійдуть пізніше, вони розшифруються збереженими MK без відкочування ланцюга", size=9.5, color=MUTED))

    render(os.path.join(OUT, "out-of-order-skipped-keys.svg"), W, H, *p,
           title="Обробка повідомлень з порушенням порядку")


if __name__ == "__main__":
    fig_e2ee_vs_transport()
    fig_x3dh_handshake()
    fig_double_ratchet_architecture()
    fig_kdf_chain_step()
    fig_break_in_recovery()
    fig_out_of_order_skipped_keys()
    print("All figures generated successfully.")
