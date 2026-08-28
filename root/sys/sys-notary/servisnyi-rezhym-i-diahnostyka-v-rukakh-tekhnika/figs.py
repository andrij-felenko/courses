# -*- coding: utf-8 -*-
import os
import sys

# Додаємо шлях до спільного модуля svgkit у scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    render, rect, line, arrow, text, mtext, textbox, fitbox, circle,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_service_mode_authentication_flow():
    """Послідовність криптографічної автентифікації техніка та керування сервісною сесією."""
    w, h = 980, 560
    frags = []

    # Заголовок
    frags.append(text(w / 2, 26, "Протокол автентифікації техніка, перевірки повноважень та аудиту сесії", size=15, bold=True))

    # Стовпчики учасників
    x_tech = 150    # Сервісний інструмент техніка
    x_agent = 490   # Вбудований діагностичний агент
    x_sec = 830     # Secure Enclave та криптографічний аудит

    # Заголовки стовпчиків
    frags.append(fitbox(x_tech - 110, 48, 220, 42, "Сервісний прилад техніка\n(Field Diagnostic Tool)", size=12, bold=True, fill="#eaf0fd", stroke=NEG))
    frags.append(fitbox(x_agent - 120, 48, 240, 42, "Вбудований агент діагностики\n(Embedded Service Agent)", size=12, bold=True, fill="#f4fbf7", stroke=FIELD))
    frags.append(fitbox(x_sec - 110, 48, 220, 42, "Secure Enclave / TPM\n(Crypto Engine & Audit Log)", size=12, bold=True, fill="#fef6f5", stroke=POS))

    # Вертикальні лінії життя
    y_start = 98
    y_end = 510
    frags.append(line(x_tech, y_start, x_tech, y_end, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(line(x_agent, y_start, x_agent, y_end, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(line(x_sec, y_start, x_sec, y_end, color=MUTED, sw=1.2, dash="4,4"))

    # Крок 1: Запит на вхід у сервісний режим
    y1 = 120
    frags.append(arrow(x_tech, y1, x_agent, y1, color=NEG, sw=1.6))
    frags.append(fitbox(x_tech + 20, y1 - 22, 300, 20, "1. SERVICE_ENTER_REQ (Tech_ID, Requested_Role)", size=10, bold=True, fill="#ffffff", stroke="#c8ddfa"))

    # Крок 2: Генерація випадкового виклику (Nonce)
    y2 = 160
    frags.append(arrow(x_agent, y2, x_sec, y2, color=FIELD, sw=1.5))
    frags.append(fitbox(x_agent + 15, y2 - 22, 310, 20, "2. Get_TRNG_Nonce() + Read_Monotonic_Counter()", size=10, bold=False, fill="#ffffff", stroke="#c3e6d5"))

    # Крок 2b: Повернення Nonce
    y3 = 195
    frags.append(arrow(x_sec, y3, x_agent, y3, color=POS, sw=1.5))
    frags.append(fitbox(x_agent + 35, y3 - 22, 270, 20, "Nonce [32B] || Device_UID || Counter", size=10, bold=False, fill="#ffffff", stroke="#f8c9c4"))

    # Крок 3: Передача виклику техніку
    y4 = 235
    frags.append(arrow(x_agent, y4, x_tech, y4, color=FIELD, sw=1.6))
    frags.append(fitbox(x_tech + 20, y4 - 22, 300, 20, "3. AUTH_CHALLENGE (Nonce, Device_UID, Lease_Limit)", size=10, bold=True, fill="#ffffff", stroke="#c3e6d5"))

    # Крок 4: Локальне підписання виклику сервісним токеном
    y5 = 280
    frags.append(fitbox(x_tech - 100, y5 - 15, 200, 32, "Ed25519_Sign(Tech_Key, Nonce || Scope)\nФормування ефемерного квитка", size=9, bold=False, fill="#eaf0fd", stroke=NEG))

    # Крок 5: Відправка підписаного відгуку
    y6 = 330
    frags.append(arrow(x_tech, y6, x_agent, y6, color=NEG, sw=1.6))
    frags.append(fitbox(x_tech + 15, y6 - 22, 310, 20, "4. AUTH_RESPONSE (Signature, Scope_Mask, Cert_Chain)", size=10, bold=True, fill="#ffffff", stroke="#c8ddfa"))

    # Крок 6: Апаратна верифікація та перевірка прав
    y7 = 370
    frags.append(arrow(x_agent, y7, x_sec, y7, color=FIELD, sw=1.5))
    frags.append(fitbox(x_agent + 15, y7 - 22, 310, 20, "5. Verify_Signature() + Validate_Cert_Chain()", size=10, bold=False, fill="#ffffff", stroke="#c3e6d5"))

    # Крок 7: Запис у незмінний журнал аудиту
    y8 = 410
    frags.append(arrow(x_agent, y8, x_sec, y8, color=POS, sw=1.5))
    frags.append(fitbox(x_agent + 10, y8 - 22, 320, 20, "6. Append_Audit_Log (Event_Auth_OK, Hash_Chain)", size=10, bold=False, fill="#ffffff", stroke="#f8c9c4"))

    # Крок 8: Розблокування сесії з таймаутом
    y9 = 455
    frags.append(arrow(x_agent, y9, x_tech, y9, color=FIELD, sw=1.6))
    frags.append(fitbox(x_tech + 10, y9 - 22, 320, 20, "7. SESSION_ACTIVE (Token, Granted_Mask, Timeout=1800s)", size=10, bold=True, fill="#e1f5eb", stroke=FIELD))

    # Стан завершення за таймаутом / безпечний скид
    y10 = 495
    frags.append(fitbox(x_agent - 180, y10 - 14, 360, 28, "Таймаут неактивності або спрацювання тампера -> Скидання маски прав у 0", size=10, bold=True, fill="#fef6f5", stroke=POS))

    frags.append(text(w / 2, h - 10, "Захищений цикл: одноразовий виклик унеможливлює повтор, а журнал аудиту фіксує кожен сервісний крок", size=11, color=MUTED, italic=True))

    out_path = os.path.join(OUT_DIR, "service-mode-authentication-flow.svg")
    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")


def fig_technician_privilege_matrix():
    """Матриця рівнів привілеїв та зон відповідальності сервісного техніка."""
    w, h = 980, 520
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 26, "Матриця рівнів привілеїв та розмежування прав сервісного обслуговування", size=15, bold=True))

    col_w = 225
    col_gap = 15
    top_y = 52
    col_h = 435

    # Рівень 1: Діагностика (Read-Only)
    x1 = 20
    frags.append(rect(x1, top_y, col_w, col_h, fill="#f4f8fe", stroke=NEG, sw=2, rx=8))
    frags.append(rect(x1, top_y, col_w, 44, fill="#e2edfd", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(x1 + col_w / 2, top_y + 18, "Рівень 1: Діагностика", size=13, color=NEG, bold=True))
    frags.append(text(x1 + col_w / 2, top_y + 34, "Read-Only / Телеметрія", size=10, color=MUTED, bold=False))

    items1 = [
        ("Дозволені операції", "Зчитування кодів помилок DTC,\nекспорт логів, жива телеметрія,\nоцінка стану батареї (SOH)"),
        ("Вплив на пристрій", "Повна відсутність змін стану,\nбезпечно під час роботи машини"),
        ("Автентифікація", "Базовий сертифікат техніка або\nфізичний сервісний ключ"),
        ("Захисні бар'єри", "Заборона запису в пам'ять,\nзаборона запуску приводів"),
    ]
    cur_y = top_y + 54
    for title, desc in items1:
        frags.append(fitbox(x1 + 8, cur_y, col_w - 16, 85, f"{title}\n{desc}", size=10, pad=4, fill="#ffffff", stroke="#c8ddfa", bold=False))
        cur_y += 93

    # Рівень 2: Калібрування та тести (Actuator / Sensor Calib)
    x2 = x1 + col_w + col_gap
    frags.append(rect(x2, top_y, col_w, col_h, fill="#f4fbf7", stroke=FIELD, sw=2, rx=8))
    frags.append(rect(x2, top_y, col_w, 44, fill="#e1f5eb", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(x2 + col_w / 2, top_y + 18, "Рівень 2: Калібрування", size=13, color=FIELD, bold=True))
    frags.append(text(x2 + col_w / 2, top_y + 34, "Сенсори та самотести", size=10, color=MUTED, bold=False))

    items2 = [
        ("Дозволені операції", "Калібрування нуля та шкали,\nтестування клапанів і моторів,\nручне скидання сервісних лічильників"),
        ("Вплив на пристрій", "Зміна калібрувальних таблиць,\nкороткочасний рух приводів"),
        ("Автентифікація", "Кваліфікований сертифікат інженера\n+ обов'язковий апаратний блокіратор"),
        ("Захисні бар'єри", "Валідація діапазонів (BBox),\nатомарний запис у Flash з CRC32"),
    ]
    cur_y = top_y + 54
    for title, desc in items2:
        frags.append(fitbox(x2 + 8, cur_y, col_w - 16, 85, f"{title}\n{desc}", size=10, pad=4, fill="#ffffff", stroke="#c3e6d5", bold=False))
        cur_y += 93

    # Рівень 3: Ремонт і прив'язка (Re-Pairing & Update)
    x3 = x2 + col_w + col_gap
    frags.append(rect(x3, top_y, col_w, col_h, fill="#fffaf0", stroke="#d97706", sw=2, rx=8))
    frags.append(rect(x3, top_y, col_w, 44, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(x3 + col_w / 2, top_y + 18, "Рівень 3: Ремонт вузлів", size=13, color="#b45309", bold=True))
    frags.append(text(x3 + col_w / 2, top_y + 34, "Прив'язка плат і прошивка", size=10, color=MUTED, bold=False))

    items3 = [
        ("Дозволені операції", "Криптоприв'язка нових деталей,\nпрошивка підписаних патчів,\nскидання лічильників блокувань"),
        ("Вплив на пристрій", "Зміна апаратного профілю вузлів,\nмодифікація бінарного образу"),
        ("Автентифікація", "Ефемерний хмарний квиток (Ticket)\nз підписом KMS вендора"),
        ("Захисні бар'єри", "Захист від відкату (Anti-rollback),\nперевірка підписів вузлів через HSM"),
    ]
    cur_y = top_y + 54
    for title, desc in items3:
        frags.append(fitbox(x3 + 8, cur_y, col_w - 16, 85, f"{title}\n{desc}", size=10, pad=4, fill="#ffffff", stroke="#fde68a", bold=False))
        cur_y += 93

    # Рівень 4: Заводське скидання (Decommissioning)
    x4 = x3 + col_w + col_gap
    frags.append(rect(x4, top_y, col_w, col_h, fill="#fef6f5", stroke=POS, sw=2, rx=8))
    frags.append(rect(x4, top_y, col_w, 44, fill="#fde6e4", stroke=POS, sw=1.5, rx=8))
    frags.append(text(x4 + col_w / 2, top_y + 18, "Рівень 4: Скидання / Кінець", size=13, color=POS, bold=True))
    frags.append(text(x4 + col_w / 2, top_y + 34, "Знищення ключів / eFuse", size=10, color=MUTED, bold=False))

    items4 = [
        ("Дозволені операції", "Криптографічне стирання ключів,\nостаточне скидання утилізації,\nпропалювання eFuse виведення"),
        ("Вплив на пристрій", "Незворотне знищення персональних даних\nта робочих сертифікатів"),
        ("Автентифікація", "Мультипідпис (Multi-Sig, 2 із 3)\nабо сервісний Master Key"),
        ("Захисні бар'єри", "Апаратний захист від помилкового виклику,\nнезмивний запис у чорну скриньку"),
    ]
    cur_y = top_y + 54
    for title, desc in items4:
        frags.append(fitbox(x4 + 8, cur_y, col_w - 16, 85, f"{title}\n{desc}", size=10, pad=4, fill="#ffffff", stroke="#f8c9c4", bold=False))
        cur_y += 93

    frags.append(text(w / 2, h - 8, "Принцип мінімальних привілеїв (PoLP): кожна дія техніка обмежена суворим криптографічним скоупом і таймаутом", size=11, color=MUTED, italic=True))

    out_path = os.path.join(OUT_DIR, "technician-privilege-matrix.svg")
    render(out_path, w, h, *frags)
    print(f"Generated {out_path}")


if __name__ == "__main__":
    fig_service_mode_authentication_flow()
    fig_technician_privilege_matrix()
