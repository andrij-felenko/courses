# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фігура 1: Трилема відкликання у вбудованих системах ─────────────────────
def fig_revocation_trilemma():
    W, H = 920, 480
    p = []
    
    # 3 стовпці: три шляхи та їхні наслідки
    col_w = 270
    h_box = 270
    y_top = 55
    
    # 1. Soft-Fail (Відкритий відвал)
    x1 = 25
    p.append(rect(x1, y_top, col_w, h_box, fill="#fdf2f2", stroke=POS, sw=1.8, rx=8))
    p.append(rect(x1 + 10, y_top + 10, col_w - 20, 34, fill="#fadbd8", stroke=POS, sw=1, rx=5))
    p.append(text(x1 + col_w/2, y_top + 32, "1. Режим Soft-Fail (Fail-Open)", size=12.5, color=POS, bold=True))
    
    p.append(text(x1 + 15, y_top + 68, "• Поведінка: якщо сервер OCSP/CRL", size=11, color=INK, anchor="start"))
    p.append(text(x1 + 15, y_top + 88, "  не відповідає — довіряти сертифікату", size=11, color=INK, anchor="start"))
    p.append(text(x1 + 15, y_top + 114, "• Стійкість зв'язку: 100% працездатність", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(x1 + 15, y_top + 140, "• Вразливість: фатальна діра безпеки", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(x1 + 15, y_top + 162, "  Зловмисник блокує пакети до CA", size=10.5, color=MUTED, anchor="start"))
    p.append(text(x1 + 15, y_top + 182, "  і підсовує скомпрометований ключ", size=10.5, color=MUTED, anchor="start"))
    
    p.append(rect(x1 + 15, y_top + 215, col_w - 30, 38, fill="#ffffff", stroke=POS, sw=1.2, rx=5))
    p.append(text(x1 + col_w/2, y_top + 238, "НАСЛІДОК: ІЛЮЗІЯ БЕЗПЕКИ", size=10.5, color=POS, bold=True))

    # 2. Hard-Fail (Жорстке блокування)
    x2 = 325
    p.append(rect(x2, y_top, col_w, h_box, fill="#fef9e7", stroke="#d4ac0d", sw=1.8, rx=8))
    p.append(rect(x2 + 10, y_top + 10, col_w - 20, 34, fill="#fcf3cf", stroke="#d4ac0d", sw=1, rx=5))
    p.append(text(x2 + col_w/2, y_top + 32, "2. Режим Hard-Fail (Fail-Closed)", size=12.5, color="#7d6608", bold=True))
    
    p.append(text(x2 + 15, y_top + 68, "• Поведінка: без свіжого доказу", size=11, color=INK, anchor="start"))
    p.append(text(x2 + 15, y_top + 88, "  відкликання сесія суворо блокується", size=11, color=INK, anchor="start"))
    p.append(text(x2 + 15, y_top + 114, "• Рівень захисту: нульова довіра", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(x2 + 15, y_top + 140, "• Вразливість: ризик відмови парку", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(x2 + 15, y_top + 162, "  Падіння сервера CA або збій мережі", size=10.5, color=MUTED, anchor="start"))
    p.append(text(x2 + 15, y_top + 182, "  миттєво вимикає 100 000 пристроїв", size=10.5, color=MUTED, anchor="start"))
    
    p.append(rect(x2 + 15, y_top + 215, col_w - 30, 38, fill="#ffffff", stroke="#d4ac0d", sw=1.2, rx=5))
    p.append(text(x2 + col_w/2, y_top + 238, "НАСЛІДОК: БЛОКУВАННЯ ПАРКУ", size=10.5, color="#7d6608", bold=True))

    # 3. Resource Starvation (Ресурсний колапс)
    x3 = 625
    p.append(rect(x3, y_top, col_w, h_box, fill="#ebf5fb", stroke=NEG, sw=1.8, rx=8))
    p.append(rect(x3 + 10, y_top + 10, col_w - 20, 34, fill="#d4e6f1", stroke=NEG, sw=1, rx=5))
    p.append(text(x3 + col_w/2, y_top + 32, "3. Ресурсні обмеження IoT", size=12.5, color=NEG, bold=True))
    
    p.append(text(x3 + 15, y_top + 68, "• Поведінка: завантаження повних", size=11, color=INK, anchor="start"))
    p.append(text(x3 + 15, y_top + 88, "  списків CRL або прямі OCSP-запити", size=11, color=INK, anchor="start"))
    p.append(text(x3 + 15, y_top + 114, "• Пам'ять: CRL на 5 МБ не влізе у 128 КБ RAM", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(x3 + 15, y_top + 140, "• Трафік: вузький канал (LoRa/NB-IoT)", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(x3 + 15, y_top + 162, "  OCSP додає затримку RTT до кожного", size=10.5, color=MUTED, anchor="start"))
    p.append(text(x3 + 15, y_top + 182, "  з'єднання та виснажує батарею живлення", size=10.5, color=MUTED, anchor="start"))
    
    p.append(rect(x3 + 15, y_top + 215, col_w - 30, 38, fill="#ffffff", stroke=NEG, sw=1.2, rx=5))
    p.append(text(x3 + col_w/2, y_top + 238, "НАСЛІДОК: ВИСНАЖЕННЯ РЕСУРСІВ", size=10.5, color=NEG, bold=True))

    # Нижній блок: Інженерний вихід із трилеми
    y_bot = 350
    w_bot = 870
    p.append(rect(25, y_bot, w_bot, 110, fill="#eef7f0", stroke=FIELD, sw=1.6, rx=8))
    p.append(text(W/2, y_bot + 24, "Архітектурний вихід: комбінований багаторівневий захист", size=13, color=FIELD, bold=True))
    p.append(text(45, y_bot + 52, "• Мережевий трафік TLS: OCSP Stapling + Must-Staple (сервер кешує доказ, клієнт не робить запитів до CA)", size=11, color=INK, anchor="start"))
    p.append(text(45, y_bot + 75, "• Безпечне завантаження (Secure Boot): апаратні таблиці eFuse + монотонні лічильники версій Anti-Rollback", size=11, color=INK, anchor="start"))
    p.append(text(45, y_bot + 98, "• Зміна кореневих ключів (Root Rollover): заздалегідь прошиті резервні слоти OEM + період подвійного підпису", size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "revocation-trilemma.svg"), W, H, *p,
           title="Трилема відкликання у розподілених та вбудованих системах")


# ── Фігура 2: Порівняння мережевих потоків CRL vs OCSP vs Stapling ─────────
def fig_crl_ocsp_stapling_flow():
    W, H = 940, 520
    p = []
    
    # 3 вертикальні секції
    sec_w = 285
    y_sec = 55
    h_sec = 445
    
    # Секція 1: CRL
    x1 = 20
    p.append(rect(x1, y_sec, sec_w, h_sec, fill="#fafafa", stroke="#7f8c8d", sw=1.4, rx=8))
    p.append(rect(x1 + 10, y_sec + 10, sec_w - 20, 32, fill="#eaeded", stroke="#7f8c8d", sw=1, rx=5))
    p.append(text(x1 + sec_w/2, y_sec + 31, "1. Списки відкликань (CRL)", size=12, color=INK, bold=True))
    
    p.append(rect(x1 + 20, y_sec + 60, 100, 34, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(x1 + 70, y_sec + 81, "IoT Клієнт", size=11, color=INK, bold=True))
    
    p.append(rect(x1 + 165, y_sec + 60, 100, 34, fill="#ebf5fb", stroke=NEG, sw=1.2, rx=4))
    p.append(text(x1 + 215, y_sec + 81, "CRL Сервер", size=11, color=NEG, bold=True))
    
    p.append(arrow(x1 + 70, y_sec + 120, x1 + 215, y_sec + 120, color=LINE, sw=1.5))
    p.append(text(x1 + 142, y_sec + 112, "HTTP GET /list.crl", size=9.5, color=MUTED))
    
    p.append(arrow(x1 + 215, y_sec + 160, x1 + 70, y_sec + 160, color=POS, sw=1.5))
    p.append(text(x1 + 142, y_sec + 152, "CRL (2..10 МБ ASN.1)", size=9.5, color=POS, bold=True))
    
    p.append(rect(x1 + 15, y_sec + 195, sec_w - 30, 235, fill="#ffffff", stroke="#bdc3c7", sw=1, rx=6))
    p.append(text(x1 + sec_w/2, y_sec + 218, "Характеристики CRL:", size=11, color=INK, bold=True))
    p.append(text(x1 + 25, y_sec + 242, "• Обсяг: O(N) — зростає з часом", size=10.5, color=POS, bold=True, anchor="start"))
    p.append(text(x1 + 25, y_sec + 266, "• Пам'ять: парсинг великих DER", size=10.5, color=INK, anchor="start"))
    p.append(text(x1 + 25, y_sec + 288, "  дерев вимагає мегабайти RAM", size=10, color=MUTED, anchor="start"))
    p.append(text(x1 + 25, y_sec + 312, "• Свіжість: кешується на дні/тижні", size=10.5, color=INK, anchor="start"))
    p.append(text(x1 + 25, y_sec + 334, "  (вікно для атаки до оновлення)", size=10, color=MUTED, anchor="start"))
    p.append(text(x1 + 25, y_sec + 358, "• Трафік: катастрофічний для IoT", size=10.5, color=POS, bold=True, anchor="start"))
    p.append(text(x1 + 25, y_sec + 382, "• Автономність: підтримує оффлайн", size=10.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(x1 + 25, y_sec + 404, "  роботу після завантаження", size=10, color=MUTED, anchor="start"))

    # Секція 2: Прямий OCSP
    x2 = 325
    p.append(rect(x2, y_sec, sec_w, h_sec, fill="#fafafa", stroke="#7f8c8d", sw=1.4, rx=8))
    p.append(rect(x2 + 10, y_sec + 10, sec_w - 20, 32, fill="#eaeded", stroke="#7f8c8d", sw=1, rx=5))
    p.append(text(x2 + sec_w/2, y_sec + 31, "2. Прямий онлайн-запит (OCSP)", size=12, color=INK, bold=True))
    
    p.append(rect(x2 + 20, y_sec + 60, 100, 34, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(x2 + 70, y_sec + 81, "IoT Клієнт", size=11, color=INK, bold=True))
    
    p.append(rect(x2 + 165, y_sec + 60, 100, 34, fill="#fef9e7", stroke="#d4ac0d", sw=1.2, rx=4))
    p.append(text(x2 + 215, y_sec + 81, "OCSP Сервер", size=11, color="#7d6608", bold=True))
    
    p.append(arrow(x2 + 70, y_sec + 120, x2 + 215, y_sec + 120, color=LINE, sw=1.5))
    p.append(text(x2 + 142, y_sec + 112, "OCSPRequest(CertID)", size=9.5, color=MUTED))
    
    p.append(arrow(x2 + 215, y_sec + 160, x2 + 70, y_sec + 160, color=NEG, sw=1.5))
    p.append(text(x2 + 142, y_sec + 152, "OCSPResp (Good/Revoked)", size=9.5, color=NEG, bold=True))
    
    p.append(rect(x2 + 15, y_sec + 195, sec_w - 30, 235, fill="#ffffff", stroke="#bdc3c7", sw=1, rx=6))
    p.append(text(x2 + sec_w/2, y_sec + 218, "Характеристики OCSP:", size=11, color=INK, bold=True))
    p.append(text(x2 + 25, y_sec + 242, "• Обсяг: компактна відповідь (~1 КБ)", size=10.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(x2 + 25, y_sec + 266, "• Затримка: +1 мережевий RTT", size=10.5, color=POS, bold=True, anchor="start"))
    p.append(text(x2 + 25, y_sec + 288, "  до встановлення кожного TLS", size=10, color=MUTED, anchor="start"))
    p.append(text(x2 + 25, y_sec + 312, "• Приватність: CA бачить IP клієнта", size=10.5, color=POS, bold=True, anchor="start"))
    p.append(text(x2 + 25, y_sec + 334, "  та адреси всіх його з'єднань", size=10, color=MUTED, anchor="start"))
    p.append(text(x2 + 25, y_sec + 358, "• Вразливість CA: точка DDoS-атаки", size=10.5, color=POS, bold=True, anchor="start"))
    p.append(text(x2 + 25, y_sec + 382, "• Збій зв'язку: штовхає в Soft-Fail", size=10.5, color=MUTED, anchor="start"))
    p.append(text(x2 + 25, y_sec + 404, "  (пропуск неперевіреного ключа)", size=10, color=MUTED, anchor="start"))

    # Секція 3: OCSP Stapling
    x3 = 630
    p.append(rect(x3, y_sec, sec_w, h_sec, fill="#f4fbf6", stroke=FIELD, sw=1.6, rx=8))
    p.append(rect(x3 + 10, y_sec + 10, sec_w - 20, 32, fill="#d5f5e3", stroke=FIELD, sw=1, rx=5))
    p.append(text(x3 + sec_w/2, y_sec + 31, "3. OCSP Stapling (Must-Staple)", size=12, color=FIELD, bold=True))
    
    # 3 вузли: Клієнт, Шлюз/Сервер, CA
    p.append(rect(x3 + 12, y_sec + 55, 76, 28, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(x3 + 50, y_sec + 73, "IoT Клієнт", size=10, color=INK, bold=True))
    
    p.append(rect(x3 + 100, y_sec + 55, 78, 28, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(x3 + 139, y_sec + 73, "TLS Сервер", size=10, color=FIELD, bold=True))

    p.append(rect(x3 + 190, y_sec + 55, 82, 28, fill="#fef9e7", stroke="#d4ac0d", sw=1.2, rx=4))
    p.append(text(x3 + 231, y_sec + 73, "CA Сервер", size=10, color="#7d6608", bold=True))
    
    p.append(arrow(x3 + 145, y_sec + 95, x3 + 225, y_sec + 95, color="#7d6608", sw=1.2))
    p.append(arrow(x3 + 225, y_sec + 118, x3 + 145, y_sec + 118, color=FIELD, sw=1.2))
    p.append(text(x3 + 185, y_sec + 110, "Кеш OCSP", size=10, color=MUTED))
    
    p.append(arrow(x3 + 50, y_sec + 145, x3 + 135, y_sec + 145, color=LINE, sw=1.4))
    p.append(text(x3 + 92, y_sec + 138, "status_request", size=10, color=MUTED))
    
    p.append(arrow(x3 + 135, y_sec + 175, x3 + 50, y_sec + 175, color=FIELD, sw=1.6))
    p.append(text(x3 + 92, y_sec + 168, "Stapled OCSP", size=10, color=FIELD, bold=True))

    p.append(rect(x3 + 15, y_sec + 195, sec_w - 30, 235, fill="#ffffff", stroke=FIELD, sw=1, rx=6))
    p.append(text(x3 + sec_w/2, y_sec + 218, "Переваги OCSP Stapling:", size=11, color=FIELD, bold=True))
    p.append(text(x3 + 25, y_sec + 242, "• 0 додаткових RTT для клієнта", size=10.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(x3 + 25, y_sec + 266, "• 0 контактів клієнта з CA", size=10.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(x3 + 25, y_sec + 288, "  (повна конфіденційність вузла)", size=10, color=MUTED, anchor="start"))
    p.append(text(x3 + 25, y_sec + 312, "• Кешування: сервер бере на себе", size=10.5, color=INK, anchor="start"))
    p.append(text(x3 + 25, y_sec + 334, "  навантаження запитів до CA", size=10, color=MUTED, anchor="start"))
    p.append(text(x3 + 25, y_sec + 358, "• Захист від MITM: прапорець", size=10.5, color=INK, anchor="start"))
    p.append(text(x3 + 25, y_sec + 380, "  Must-Staple блокує спроби", size=10, color=MUTED, anchor="start"))
    p.append(text(x3 + 25, y_sec + 402, "  зловмисника вирізати статус", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "crl-ocsp-stapling-flow.svg"), W, H, *p,
           title="Порівняння мережевих механізмів перевірки статусу сертифікатів")


# ── Фігура 3: Апаратне відкликання ключів у кремнії (eFuse & Anti-Rollback) ──
def fig_hardware_key_revocation_efuse():
    W, H = 940, 500
    p = []
    
    # Лівий блок: Матриця кореневих ключів у кремнії (OTP / eFuse Hash Slots)
    x_l = 25
    w_l = 430
    p.append(rect(x_l, 55, w_l, 420, fill="#fdfefe", stroke=NEG, sw=1.6, rx=8))
    p.append(rect(x_l + 10, 65, w_l - 20, 32, fill="#ebf5fb", stroke=NEG, sw=1, rx=5))
    p.append(text(x_l + w_l/2, 86, "Апаратна матриця публічних ключів (OTP / ROM)", size=12.5, color=NEG, bold=True))
    
    # 4 слоти ключів
    slots = [
        ("Слот 0 (OEM Root Key A)", "SHA-256 Digest 0", "АКТИВНИЙ / АНУЛЬОВАНИЙ", POS, "#fdecea", "eFuse Revocation Bit 0 = 1 (ПЕРЕПАЛЕНО)"),
        ("Слот 1 (OEM Root Key B)", "SHA-256 Digest 1", "АКТИВНИЙ (ПОТОЧНИЙ ЧИННИЙ)", FIELD, "#eef7f0", "eFuse Revocation Bit 1 = 0 (ЧИСТИЙ)"),
        ("Слот 2 (OEM Root Key C)", "SHA-256 Digest 2", "РЕЗЕРВНИЙ (STANDBY)", MUTED, "#f4f6f8", "eFuse Revocation Bit 2 = 0 (ЧИСТИЙ)"),
        ("Слот 3 (Emergency Key D)", "SHA-256 Digest 3", "АВАРІЙНИЙ ХОЛОДНИЙ (COLD)", MUTED, "#f4f6f8", "eFuse Revocation Bit 3 = 0 (ЧИСТИЙ)"),
    ]
    
    for i, (s_name, s_hash, s_st, s_col, s_bg, s_fuse) in enumerate(slots):
        ys = 110 + i * 85
        p.append(rect(x_l + 15, ys, w_l - 30, 75, fill=s_bg, stroke=s_col, sw=1.2, rx=6))
        p.append(text(x_l + 25, ys + 20, s_name, size=11, color=INK, bold=True, anchor="start"))
        p.append(text(x_l + w_l - 25, ys + 20, s_st, size=10, color=s_col, bold=True, anchor="end"))
        p.append(text(x_l + 25, ys + 42, f"• Хеш відкритого ключа: {s_hash}", size=10, color=MUTED, anchor="start"))
        p.append(text(x_l + 25, ys + 62, f"• Стан анулювання: {s_fuse}", size=10, color=s_col, bold=True, anchor="start"))

    # Правий блок: Монотонний лічильник захисту від відкату (Anti-Rollback)
    x_r = 485
    w_r = 430
    p.append(rect(x_r, 55, w_r, 420, fill="#fdfefe", stroke=POS, sw=1.6, rx=8))
    p.append(rect(x_r + 10, 65, w_r - 20, 32, fill="#fadbd8", stroke=POS, sw=1, rx=5))
    p.append(text(x_r + w_r/2, 86, "Монотонний лічильник версій (Anti-Rollback Counter)", size=12.5, color=POS, bold=True))
    
    p.append(text(x_r + 20, 120, "Принцип однобічного перепалювання бітів eFuse:", size=11, color=INK, bold=True, anchor="start"))
    p.append(text(x_r + 20, 142, "• Перемичка eFuse фізично плавиться імпульсом струму", size=10.5, color=INK, anchor="start"))
    p.append(text(x_r + 20, 162, "• Стан 0 -> 1 є незворотним (повернути 1 -> 0 неможливо)", size=10.5, color=POS, bold=True, anchor="start"))

    # Схема бітового масиву
    p.append(rect(x_r + 20, 180, w_r - 40, 60, fill="#ffffff", stroke="#bdc3c7", sw=1, rx=4))
    p.append(text(x_r + w_r/2, 200, "Масив 32 бітів eFuse Security Counter:", size=10.5, color=MUTED, bold=True))
    
    # 8 видимих комірок-бітів
    for b in range(8):
        xb = x_r + 40 + b * 43
        b_val = "1" if b < 4 else "0"
        b_col = POS if b < 4 else "#bdc3c7"
        b_bg = "#fdecea" if b < 4 else "#ffffff"
        p.append(rect(xb, 212, 36, 20, fill=b_bg, stroke=b_col, sw=1.2, rx=3))
        p.append(text(xb + 18, 226, b_val, size=11, color=POS if b < 4 else MUTED, bold=True))

    p.append(text(x_r + w_r/2, 258, "Поточне значення апаратного лічильника: Версія 4 (4 біти спалено)", size=10.5, color=POS, bold=True))

    # Логіка верифікації прошивки
    p.append(rect(x_r + 20, 275, w_r - 40, 185, fill="#f4f6f8", stroke="#7f8c8d", sw=1.2, rx=6))
    p.append(text(x_r + w_r/2, 296, "Алгоритм перевірки під час Secure Boot:", size=11, color=INK, bold=True))
    p.append(text(x_r + 30, 320, "1. ROM читає заголовок прошивки: FW_Ver та Key_Index", size=10, color=INK, anchor="start"))
    p.append(text(x_r + 30, 342, "2. Перевірка слота: eFuse_Revoked[Key_Index] == 0?", size=10, color=NEG, bold=True, anchor="start"))
    p.append(text(x_r + 30, 364, "   (якщо 1 — негайна зупинка: КЛЮЧ АНУЛЬОВАНО)", size=10, color=POS, anchor="start"))
    p.append(text(x_r + 30, 386, "3. Перевірка версії: FW_Ver >= HW_AntiRollback_Ver?", size=10, color=NEG, bold=True, anchor="start"))
    p.append(text(x_r + 30, 408, "   (якщо менше — відхилення: СПРОБА ВІДКАТУ FW)", size=10, color=POS, anchor="start"))
    p.append(text(x_r + 30, 430, "4. Якщо FW_Ver > HW_Ver: прожиг бітів eFuse до FW_Ver", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(x_r + 30, 448, "   (фіксація мінімальної допустимої версії)", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "hardware-key-revocation-efuse.svg"), W, H, *p,
           title="Апаратне відкликання ключів і захист від відкату у кристалі")


# ── Фігура 4: Життєвий цикл безперервної ротації кореневого ключа ────────────
def fig_dual_key_rollover_lifecycle():
    W, H = 940, 500
    p = []
    
    # 4 послідовні фази ротації зліва направо
    col_w = 210
    y_box = 60
    h_box = 410
    
    phases = [
        ("Фаза 1: Штатна робота", "#ebf5fb", NEG, [
            ("Стан парку:", INK, True),
            ("• Активний: Ключ 0 (Key_0)", FIELD, True),
            ("• Резервний: Ключ 1 (Key_1)", MUTED, False),
            ("• Резерв в OTP прошитий", MUTED, False),
            ("  ще на етапі фабрики", MUTED, False),
            ("Формат оновлень:", INK, True),
            ("• Прошивки підписані", INK, False),
            ("  виключно Key_0", INK, False),
            ("Подія запуску:", POS, True),
            ("• Виявлено витік або", POS, False),
            ("  плановий кінець Key_0", POS, False),
        ]),
        ("Фаза 2: Подвійний підпис", "#fef9e7", "#d4ac0d", [
            ("Стан оновлення:", INK, True),
            ("• Пакет містить підписи:", INK, False),
            ("  Sig(Key_0) + Sig(Key_1)", FIELD, True),
            ("• Інструкція міграції:", INK, False),
            ("  Set_Active_Key(Slot 1)", NEG, True),
            ("Розгортання у парку:", INK, True),
            ("• Старі пристрої валідують", INK, False),
            ("  образ через Key_0", INK, False),
            ("• Нові вузли вже готові", INK, False),
            ("  до розпізнавання Key_1", INK, False),
        ]),
        ("Фаза 3: Атомарне перемикання", "#fdf2f2", POS, [
            ("Дії завантажувача:", INK, True),
            ("• Запис образу у Банк B", INK, False),
            ("• Верифікація обох підписів", INK, False),
            ("• Тестове завантаження B", INK, False),
            ("• Watchdog перевіряє зв'язок", FIELD, True),
            ("Фіксація ротації:", POS, True),
            ("• Апаратний прожиг eFuse:", POS, False),
            ("  Revoke_Slot(0) = 1", POS, True),
            ("• Key_0 мертвий назавжди", POS, True),
        ]),
        ("Фаза 4: Нова норма", "#eef7f0", FIELD, [
            ("Новий стан парку:", INK, True),
            ("• Активний: Ключ 1 (Key_1)", FIELD, True),
            ("• Ключ 0 заблокований", POS, True),
            ("  на рівні кремнію", POS, False),
            ("• Резервний: Ключ 2 (Key_2)", MUTED, False),
            ("  (готовий до наступної)", MUTED, False),
            ("Результат:", FIELD, True),
            ("• 0 секунд простою парку", FIELD, True),
            ("• Жоден пристрій не став", FIELD, True),
            ("  «цеглиною» під час ротації", FIELD, True),
        ])
    ]
    
    for i, (title_ph, bg_col, stroke_col, items) in enumerate(phases):
        x = 25 + i * 225
        p.append(rect(x, y_box, col_w, h_box, fill=bg_col, stroke=stroke_col, sw=1.6, rx=8))
        p.append(rect(x + 8, y_box + 10, col_w - 16, 32, fill="#ffffff", stroke=stroke_col, sw=1, rx=5))
        p.append(text(x + col_w/2, y_box + 31, title_ph, size=11.5, color=stroke_col, bold=True))
        
        y_text = y_box + 60
        for it_txt, it_col, it_bld in items:
            p.append(text(x + 12, y_text, it_txt, size=10, color=it_col, bold=it_bld, anchor="start"))
            y_text += 22

        # Стрілка переходу між фазами
        if i < 3:
            p.append(arrow(x + col_w + 3, y_box + 190, x + col_w + 22, y_box + 190, color=LINE, sw=1.6))

    render(os.path.join(OUT, "dual-key-rollover-lifecycle.svg"), W, H, *p,
           title="Життєвий цикл безперервної міграції кореневого ключа парку")


if __name__ == "__main__":
    fig_revocation_trilemma()
    fig_crl_ocsp_stapling_flow()
    fig_hardware_key_revocation_efuse()
    fig_dual_key_rollover_lifecycle()
    print("All figures generated successfully.")
