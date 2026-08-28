# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фігура 1: Спектр розміщення приватного ключа ─────────────────────────────
def fig_key_storage_spectrum():
    W, H = 880, 520
    p = []
    
    p.append(text(W/2, 30, "Спектр ізоляції приватного ключа: від файлу на диску до апаратного HSM", size=16, color=INK, bold=True))
    
    col_w = 195
    h_box = 320
    y_top = 60
    
    # 1. Ноутбук / Сервер (Файл)
    x1 = 25
    p.append(rect(x1, y_top, col_w, h_box, fill="#fdf2e9", stroke=POS, sw=1.8, rx=8))
    p.append(text(x1 + col_w/2, y_top + 24, "1. Файл на диску", size=13, color=POS, bold=True))
    p.append(text(x1 + col_w/2, y_top + 42, "(«Ноутбук Петра» / Сервер)", size=10, color=MUTED, bold=True))
    p.append(line(x1 + 10, y_top + 54, x1 + col_w - 10, y_top + 54, color="#edbb99", sw=1))
    p.append(text(x1 + 12, y_top + 76, "• Носій: SSD, HDD, Flash", size=11, color=INK, anchor="start"))
    p.append(text(x1 + 12, y_top + 100, "• Межа: відсутня (ОС)", size=11, color=INK, anchor="start"))
    p.append(text(x1 + 12, y_top + 124, "• Пам'ять: відкритий у RAM", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(x1 + 12, y_top + 148, "• Копіювання: миттєве", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(x1 + 12, y_top + 172, "• Аудит витоку: нульовий", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(x1 + 12, y_top + 196, "• Продуктивність: CPU", size=11, color=INK, anchor="start"))
    p.append(text(x1 + 12, y_top + 220, "• Рівень FIPS: немає", size=11, color=MUTED, italic=True, anchor="start"))
    p.append(rect(x1 + 15, y_top + 260, col_w - 30, 32, fill="#f5b7b1", stroke=POS, sw=1.2, rx=4))
    p.append(text(x1 + col_w/2, y_top + 280, "КАТАСТРОФА", size=11, color=POS, bold=True))

    # 2. USB-токен / Смарт-картка
    x2 = 235
    p.append(rect(x2, y_top, col_w, h_box, fill="#eaf2f8", stroke=NEG, sw=1.8, rx=8))
    p.append(text(x2 + col_w/2, y_top + 24, "2. Апаратний токен", size=13, color=NEG, bold=True))
    p.append(text(x2 + col_w/2, y_top + 42, "(YubiKey, Smartcard, SE)", size=10, color=MUTED, bold=True))
    p.append(line(x2 + 10, y_top + 54, x2 + col_w - 10, y_top + 54, color="#a9cce3", sw=1))
    p.append(text(x2 + 12, y_top + 76, "• Носій: захищений чип", size=11, color=INK, anchor="start"))
    p.append(text(x2 + 12, y_top + 100, "• Межа: криптопроцесор", size=11, color=INK, anchor="start"))
    p.append(text(x2 + 12, y_top + 124, "• Пам'ять: замкнений у SE", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(x2 + 12, y_top + 148, "• Захист: PIN + дотик руки", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(x2 + 12, y_top + 172, "• Пропускна: 10-50 оп/с", size=11, color=INK, anchor="start"))
    p.append(text(x2 + 12, y_top + 196, "• Формат: USB / CCID", size=11, color=INK, anchor="start"))
    p.append(text(x2 + 12, y_top + 220, "• Рівень: FIPS 140-3 L2/3", size=11, color=MUTED, italic=True, anchor="start"))
    p.append(rect(x2 + 15, y_top + 260, col_w - 30, 32, fill="#d4e6f1", stroke=NEG, sw=1.2, rx=4))
    p.append(text(x2 + col_w/2, y_top + 280, "ОСОБИСТИЙ ЗАХИСТ", size=11, color=NEG, bold=True))

    # 3. Мережевий HSM
    x3 = 445
    p.append(rect(x3, y_top, col_w, h_box, fill="#eef7f0", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(x3 + col_w/2, y_top + 24, "3. Мережевий HSM", size=13, color=FIELD, bold=True))
    p.append(text(x3 + col_w/2, y_top + 42, "(Thales, Utimaco, Entrust)", size=10, color=MUTED, bold=True))
    p.append(line(x3 + 10, y_top + 54, x3 + col_w - 10, y_top + 54, color="#a9dfbf", sw=1))
    p.append(text(x3 + 12, y_top + 76, "• Носій: броньований сервер", size=11, color=INK, anchor="start"))
    p.append(text(x3 + 12, y_top + 100, "• Межа: активна сітка захисту", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(x3 + 12, y_top + 124, "• Пам'ять: нуліфікація ключа", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(x3 + 12, y_top + 148, "• Доступ: кворум m-of-n", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(x3 + 12, y_top + 172, "• Пропускна: 10 000+ оп/с", size=11, color=INK, anchor="start"))
    p.append(text(x3 + 12, y_top + 196, "• Інтерфейс: PKCS#11 / IP", size=11, color=INK, anchor="start"))
    p.append(text(x3 + 12, y_top + 220, "• Рівень: FIPS 140-3 L3/4", size=11, color=MUTED, italic=True, anchor="start"))
    p.append(rect(x3 + 15, y_top + 260, col_w - 30, 32, fill="#d5f5e3", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(x3 + col_w/2, y_top + 280, "КОРПОРАТИВНИЙ КОРІНЬ", size=11, color=FIELD, bold=True))

    # 4. Хмарний KMS / Cloud HSM
    x4 = 655
    p.append(rect(x4, y_top, col_w, h_box, fill="#fbfcfc", stroke="#566573", sw=1.8, rx=8))
    p.append(text(x4 + col_w/2, y_top + 24, "4. Хмарний KMS / HSM", size=13, color="#2c3e50", bold=True))
    p.append(text(x4 + col_w/2, y_top + 42, "(AWS KMS, GCP, Azure KV)", size=10, color=MUTED, bold=True))
    p.append(line(x4 + 10, y_top + 54, x4 + col_w - 10, y_top + 54, color="#d5dbdb", sw=1))
    p.append(text(x4 + 12, y_top + 76, "• Носій: HSM-as-a-Service", size=11, color=INK, anchor="start"))
    p.append(text(x4 + 12, y_top + 100, "• Межа: хмарний датацентр", size=11, color=INK, anchor="start"))
    p.append(text(x4 + 12, y_top + 124, "• Пам'ять: KMS KEK + DEK", size=11, color=INK, anchor="start"))
    p.append(text(x4 + 12, y_top + 148, "• Захист: IAM політики", size=11, color=INK, anchor="start"))
    p.append(text(x4 + 12, y_top + 172, "• Аудит: повний CloudTrail", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(x4 + 12, y_top + 196, "• Масштабування: еластичне", size=11, color=INK, anchor="start"))
    p.append(text(x4 + 12, y_top + 220, "• Рівень: FIPS 140-3 L3", size=11, color=MUTED, italic=True, anchor="start"))
    p.append(rect(x4 + 15, y_top + 260, col_w - 30, 32, fill="#eaeded", stroke="#566573", sw=1.2, rx=4))
    p.append(text(x4 + col_w/2, y_top + 280, "ХМАРНИЙ СЕРВІС", size=11, color="#2c3e50", bold=True))

    # Нижній банер висновку
    y_bot = 405
    p.append(rect(25, y_bot, 825, 95, fill="#f8f9fa", stroke="#34495e", sw=1.5, rx=8))
    p.append(text(W/2, y_bot + 26, "Головний принцип апаратної безпеки: «Ключ — це не дані, а обчислювальна спроможність»", size=13, color=INK, bold=True))
    p.append(text(W/2, y_bot + 52, "Приватний ключ ніколи не зчитується в RAM хоста. Хост надсилає лише геш даних, а чип повертає готовий підпис.", size=11, color=MUTED))
    p.append(text(W/2, y_bot + 74, "Компрометація операційної системи хоста не дозволяє зловмиснику скопіювати чи викрасти сам ключ.", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "key-storage-spectrum.svg"), W, H, *p)

# ── Фігура 2: Архітектура активного захисту та нуліфікації HSM ────────────────
def fig_hsm_tamper_zeroization():
    W, H = 880, 480
    p = []
    
    p.append(text(W/2, 28, "Криптографічна межа FIPS 140-3 Level 4: Активний захист і нуліфікація", size=15, color=INK, bold=True))
    
    # Зовнішній корпус HSM
    x0, y0, w0, h0 = 40, 55, 800, 400
    p.append(rect(x0, y0, w0, h0, fill="#f2f4f4", stroke="#2c3e50", sw=2.5, rx=12))
    p.append(text(x0 + 20, y0 + 26, "Шасі мережевого HSM (Заземлений екранований корпус від випромінювань TEMPEST)", size=12, color="#2c3e50", bold=True, anchor="start"))
    
    # Захисна сітка (Tamper Mesh)
    x_mesh, y_mesh, w_mesh, h_mesh = x0 + 25, y0 + 42, w0 - 50, h0 - 60
    p.append(rect(x_mesh, y_mesh, w_mesh, h_mesh, fill="#ebedef", stroke=POS, sw=2, rx=10))
    p.append(text(x_mesh + 20, y_mesh + 24, "Активна мікропровідна сітка (Tamper-Resistant Wire Mesh / Постійний контроль опору)", size=11, color=POS, bold=True, anchor="start"))
    
    # Епоксидний компаунд / Внутрішній анклав
    x_enc, y_enc, w_enc, h_enc = x_mesh + 20, y_mesh + 38, w_mesh - 40, h_mesh - 55
    p.append(rect(x_enc, y_enc, w_enc, h_enc, fill="#ffffff", stroke="#7f8c8d", sw=1.8, rx=8))
    p.append(text(W/2, y_enc + 24, "Непроникний епоксидний бар'єр із вбудованими датчиками загрози", size=12, color=INK, bold=True))
    
    # Датчики загрози
    sensor_w = 200
    sensor_h = 75
    ys = y_enc + 45
    
    # Датчик 1: Механічний / Свердління
    xs1 = x_enc + 25
    p.append(rect(xs1, ys, sensor_w, sensor_h, fill="#fdecea", stroke=POS, sw=1.2, rx=6))
    p.append(text(xs1 + sensor_w/2, ys + 22, "1. Датчик свердління", size=11, color=POS, bold=True))
    p.append(text(xs1 + sensor_w/2, ys + 42, "Розрив або замикання", size=10, color=INK))
    p.append(text(xs1 + sensor_w/2, ys + 60, "мікродоріжок сітки", size=10, color=MUTED))

    # Датчик 2: Температурний
    xs2 = xs1 + sensor_w + 35
    p.append(rect(xs2, ys, sensor_w, sensor_h, fill="#eaf2f8", stroke=NEG, sw=1.2, rx=6))
    p.append(text(xs2 + sensor_w/2, ys + 22, "2. Датчик температури", size=11, color=NEG, bold=True))
    p.append(text(xs2 + sensor_w/2, ys + 42, "Захист від заморожування", size=10, color=INK))
    p.append(text(xs2 + sensor_w/2, ys + 60, "і теплової деградації", size=10, color=MUTED))

    # Датчик 3: Напруги та світла
    xs3 = xs2 + sensor_w + 35
    p.append(rect(xs3, ys, sensor_w, sensor_h, fill="#fef9e7", stroke="#d4ac0d", sw=1.2, rx=6))
    p.append(text(xs3 + sensor_w/2, ys + 22, "3. Датчик живлення / фото", size=11, color="#b7950b", bold=True))
    p.append(text(xs3 + sensor_w/2, ys + 42, "Стрибки напруги (Glitch)", size=10, color=INK))
    p.append(text(xs3 + sensor_w/2, ys + 60, "або потрапляння світла", size=10, color=MUTED))

    # Лінії тригерів до блоку нуліфікації
    y_sig = ys + sensor_h
    y_trig = y_sig + 35
    p.append(arrow(xs1 + sensor_w/2, y_sig, xs1 + sensor_w/2, y_trig, color=POS, sw=1.5))
    p.append(arrow(xs2 + sensor_w/2, y_sig, xs2 + sensor_w/2, y_trig, color=POS, sw=1.5))
    p.append(arrow(xs3 + sensor_w/2, y_sig, xs3 + sensor_w/2, y_trig, color=POS, sw=1.5))
    
    # Блок апаратної нуліфікації (Zeroization Circuit)
    x_zero = x_enc + 40
    w_zero = w_enc - 80
    h_zero = 80
    p.append(rect(x_zero, y_trig, w_zero, h_zero, fill="#f9ebea", stroke=POS, sw=2, rx=8))
    p.append(text(W/2, y_trig + 24, "КОЛО МИТТЄВОЇ НУЛІФІКАЦІЇ (ZEROIZATION CIRCUITRY)", size=13, color=POS, bold=True))
    p.append(text(W/2, y_trig + 46, "Резервне живлення від суперконденсатора/батареї -> Миттєве скидання живлення енергозалежної SRAM", size=10, color=INK))
    p.append(text(W/2, y_trig + 66, "Майстер-ключі шифрування (Master Keys / LMK) знищуються за одиниці наносекунд без можливості відновлення", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "hsm-tamper-zeroization.svg"), W, H, *p)

# ── Фігура 3: Процес підпису через PKCS#11 без експорту ключа ────────────────
def fig_pkcs11_signing_flow():
    W, H = 880, 480
    p = []
    
    p.append(text(W/2, 28, "Криптографічний підпис через PKCS#11: Ізоляція закритого ключа", size=15, color=INK, bold=True))
    
    # Ліва колонка: Хост застосунку (Недовірена зона ОС)
    x_host = 35
    w_host = 350
    h_lane = 390
    y_lane = 55
    p.append(rect(x_host, y_lane, w_host, h_lane, fill="#f8f9f9", stroke="#7f8c8d", sw=1.5, rx=8))
    p.append(text(x_host + w_host/2, y_lane + 24, "Простір хоста (Host OS / User Space)", size=13, color="#2c3e50", bold=True))
    p.append(text(x_host + w_host/2, y_lane + 42, "Застосунок + PKCS#11 Driver (libykcs11 / softhsm)", size=10, color=MUTED))
    p.append(line(x_host + 15, y_lane + 52, x_host + w_host - 15, y_lane + 52, color="#bdc3c7", sw=1))

    # Права колонка: Апаратний чип токена / HSM (Довірена зона)
    x_hsm = 495
    w_hsm = 350
    p.append(rect(x_hsm, y_lane, w_hsm, h_lane, fill="#eafaf1", stroke=FIELD, sw=2, rx=8))
    p.append(text(x_hsm + w_hsm/2, y_lane + 24, "Апаратний анклав (Secure Element / HSM)", size=13, color=FIELD, bold=True))
    p.append(text(x_hsm + w_hsm/2, y_lane + 42, "Внутрішній криптопроцесор + Невитягуваний ключ", size=10, color=MUTED))
    p.append(line(x_hsm + 15, y_lane + 52, x_hsm + w_hsm - 15, y_lane + 52, color="#a9dfbf", sw=1))

    # Кроки протоколу
    y_step1 = 125
    # Крок 1: Гешування на хості
    p.append(rect(x_host + 20, y_step1, w_host - 40, 48, fill="#ffffff", stroke="#34495e", sw=1.2, rx=6))
    p.append(text(x_host + w_host/2, y_step1 + 20, "1. Обчислення гешу даних на хості", size=11, color=INK, bold=True))
    p.append(text(x_host + w_host/2, y_step1 + 38, "Digest = SHA-256(Document) [32 байти]", size=10, color=MUTED))

    # Крок 2: Передавання гешу та ID ключа
    y_step2 = 195
    p.append(arrow(x_host + w_host - 20, y_step2, x_hsm + 20, y_step2, color=NEG, sw=2))
    p.append(text(W/2, y_step2 - 12, "C_Sign(hSession, Digest, &Signature)", size=11, color=NEG, bold=True))
    p.append(text(W/2, y_step2 + 16, "Передається лише 32 байти гешу + дескриптор ключа", size=9, color=MUTED))

    # Крок 3: Перевірка PIN та фізичного дотику в HSM
    y_step3 = 245
    p.append(rect(x_hsm + 20, y_step3, w_hsm - 40, 52, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(x_hsm + w_hsm/2, y_step3 + 20, "2. Перевірка авторизації в чипі", size=11, color=FIELD, bold=True))
    p.append(text(x_hsm + w_hsm/2, y_step3 + 38, "Перевірка PIN-коду + Touch User Presence", size=10, color=MUTED))

    # Крок 4: Операція підпису всередині захищеного ядра
    y_step4 = 315
    p.append(rect(x_hsm + 20, y_step4, w_hsm - 40, 52, fill="#d5f5e3", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(x_hsm + w_hsm/2, y_step4 + 20, "3. Обчислення підпису в кремнії", size=11, color=FIELD, bold=True))
    p.append(text(x_hsm + w_hsm/2, y_step4 + 38, "Signature = ECDSA_Sign(PrivKey, Digest)", size=10, color=INK))

    # Крок 5: Повернення підпису
    y_step5 = 385
    p.append(arrow(x_hsm + 20, y_step5, x_host + w_host - 20, y_step5, color=FIELD, sw=2))
    p.append(text(W/2, y_step5 - 12, "Повернення байтів підпису (R, S)", size=11, color=FIELD, bold=True))
    p.append(text(W/2, y_step5 + 16, "Приватний ключ жодного разу не торкнувся RAM хоста", size=9, color=FIELD, bold=True))

    render(os.path.join(OUT, "pkcs11-hardware-signing-flow.svg"), W, H, *p)

# ── Фігура 4: Кворум m-of-n та розділення секретів Шаміра ────────────────────
def fig_mofn_quorum_ceremony():
    W, H = 880, 490
    p = []
    
    p.append(text(W/2, 28, "Кворум доступу m-of-n: Розділення секретів Шаміра для активації Root HSM", size=15, color=INK, bold=True))
    
    # 5 Офіцерів безпеки (Key Custodians)
    y_cust = 60
    w_card = 145
    h_card = 110
    dx_card = 165
    
    custodians = [
        ("Офіцер 1 (UK)", "Частка S1 (Смарт-картка 1)", True),
        ("Офіцер 2 (US)", "Частка S2 (Смарт-картка 2)", True),
        ("Офіцер 3 (DE)", "Частка S3 (Смарт-картка 3)", True),
        ("Офіцер 4 (JP)", "Частка S4 (Смарт-картка 4)", False),
        ("Офіцер 5 (AU)", "Частка S5 (Смарт-картка 5)", False)
    ]
    
    for i, (name, role, active) in enumerate(custodians):
        xc = 35 + i * dx_card
        fill_c = "#eafaf1" if active else "#f2f4f4"
        strk_c = FIELD if active else "#bdc3c7"
        p.append(rect(xc, y_cust, w_card, h_card, fill=fill_c, stroke=strk_c, sw=1.5, rx=6))
        p.append(text(xc + w_card/2, y_cust + 22, name, size=11, color=INK, bold=True))
        p.append(text(xc + w_card/2, y_cust + 42, role, size=9, color=MUTED))
        p.append(line(xc + 10, y_cust + 52, xc + w_card - 10, y_cust + 52, color="#d5dbdb", sw=1))
        status_txt = "✓ ПРИСУТНІЙ (Кворум)" if active else "— Відсутній (Запас)"
        status_col = FIELD if active else MUTED
        p.append(text(xc + w_card/2, y_cust + 75, status_txt, size=10, color=status_col, bold=active))
        
        if active:
            # Стрілка вниз до шлюзу верифікації
            p.append(arrow(xc + w_card/2, y_cust + h_card, W/2, 230, color=FIELD, sw=1.5))

    # Центральний вузол збирання часток (Математичне відновлення)
    y_gate = 235
    w_gate = 520
    h_gate = 85
    p.append(rect(W/2 - w_gate/2, y_gate, w_gate, h_gate, fill="#ffffff", stroke="#2c3e50", sw=2, rx=8))
    p.append(text(W/2, y_gate + 24, "Схема інтерполяції Лагранжа (Кворум 3-of-5)", size=13, color=INK, bold=True))
    p.append(text(W/2, y_gate + 48, "Будь-які m=3 частки з n=5 дозволяють відновити Master Activation Secret у захищеній пам'яті", size=10, color=MUTED))
    p.append(text(W/2, y_gate + 68, "Будь-які 2 або менше часток дають нуль інформації про ключ (Perfect Secrecy)", size=10, color=POS, bold=True))

    # Стрілка до активованого HSM
    p.append(arrow(W/2, y_gate + h_gate, W/2, 365, color=FIELD, sw=2.2))

    # Нижній блок: Активований Root HSM
    y_hsm = 370
    w_hsm_box = 780
    h_hsm_box = 90
    p.append(rect(W/2 - w_hsm_box/2, y_hsm, w_hsm_box, h_hsm_box, fill="#e8f8f5", stroke=FIELD, sw=2.2, rx=8))
    p.append(text(W/2, y_hsm + 26, "РОЗБЛОКОВАНИЙ КОРЕНЕВИЙ РОЗДІЛ HSM (ROOT SIGNING CEREMONY)", size=13, color=FIELD, bold=True))
    p.append(text(W/2, y_hsm + 50, "Кореневий приватний ключ CA / DNSSEC активовано для підписання проміжних сертифікатів або ZSK", size=11, color=INK))
    p.append(text(W/2, y_hsm + 72, "Жодна окрема людина не має одноосібного контролю над кореневим криптографічним ключем", size=10, color="#117864", bold=True))

    render(os.path.join(OUT, "mofn-quorum-ceremony.svg"), W, H, *p)

if __name__ == "__main__":
    fig_key_storage_spectrum()
    fig_hsm_tamper_zeroization()
    fig_pkcs11_signing_flow()
    fig_mofn_quorum_ceremony()
    print("Всі фігури згенеровано успішно.")
