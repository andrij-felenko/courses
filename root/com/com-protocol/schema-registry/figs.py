# -*- coding: utf-8 -*-
"""Фігури теми «Еволюція схем і schema-registry». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

GREEN_F = "#d4edda"
RED_F   = "#fdecea"
BLUE_F  = "#e8f0fe"
WARN_F  = "#fff3cd"

# ── 1. poison-pill-vs-registry: некерована зміна проти реєстру схем ─────────
def fig_poison_pill_vs_registry():
    W, H = 1000, 440
    f = []

    # Ліва половина: Некоординована зміна (отруйне повідомлення)
    f.append(rect(15, 15, 475, 410, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    f.append(text(252, 45, "Некоординована зміна: отруйне повідомлення", size=13, bold=True, color=POS))

    # Продюсер зліва
    p_box, _, _ = textbox(95, 140, "Продюсер V2\n(нова схема)\n\nЗміна поля:\namount: 49.95\nзамість int",
                          size=10.5, bold=True, min_w=125, pad=6, fill=FILL, stroke=LINE)
    f.append(p_box)

    # Черга посередині лівої панелі
    q_box, _, _ = textbox(235, 140, "Журнал подій\n(Kafka Topic)\n\n[msg_1: OK]\n[msg_2: BAD!]",
                          size=10.5, bold=True, min_w=95, pad=6, fill=WARN_F, stroke="#d39e00")
    f.append(q_box)
    f.append(arrow(160, 140, 185, 140, color=POS, sw=1.5))

    # Споживачі зліва
    c1_box, _, _ = textbox(385, 95, "Споживач A (Білінг)\n⚠ Крах десеріалізації\n(Poison Pill / Партиція стала)",
                           size=10, bold=True, min_w=145, pad=6, fill=RED_F, stroke=POS)
    c2_box, _, _ = textbox(385, 175, "Споживач B (Аналітика)\n⚠ Тихе спотворення\namount спарсено як 0 (NULL)",
                           size=10, bold=True, min_w=145, pad=6, fill=WARN_F, stroke="#856404")
    c3_box, _, _ = textbox(385, 255, "Споживач C (Склад)\nОчікує старий контракт\nЧерга завмирає",
                           size=10, min_w=145, pad=6, fill=FILL, stroke=LINE)
    f.append(c1_box)
    f.append(c2_box)
    f.append(c3_box)

    f.append(arrow(285, 125, 310, 95, color=POS, sw=1.3))
    f.append(arrow(285, 140, 310, 175, color="#d39e00", sw=1.3))
    f.append(arrow(285, 155, 310, 255, color=MUTED, sw=1.3))

    f.append(text(252, 345, "✗ Відкат продюсера не лікує журнал: биті повідомлення вже записані", size=10.5, color=POS, italic=True))
    f.append(text(252, 370, "✗ Потрібне ручне скидання офсетів і зупинка конвеєра", size=10.5, color=POS, italic=True))

    # Права половина: Реєстр схем (контроль сумісності)
    f.append(rect(510, 15, 475, 410, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    f.append(text(747, 45, "Централізований реєстр схем: гарантія контракту", size=13, bold=True, color=FIELD))

    # Реєстр зверху правої половини
    reg_box, _, _ = textbox(747, 105, "РЕЄСТР СХЕМ (Schema Registry)\n• Перевірка сумісності (BACKWARD/FULL)\n• Призначення глобального ID схеми\n• Єдине джерело правди про версії",
                            size=10.5, bold=True, min_w=280, pad=8, fill=BLUE_F, stroke=NEG, sw=1.5)
    f.append(reg_box)

    # Продюсер справа
    p2_box, _, _ = textbox(595, 215, "Продюсер V2\n1. Валідація в CI\n2. Отримання ID=42\n3. Запис 5-байт кадру",
                           size=10, bold=True, min_w=130, pad=6, fill=FILL, stroke=LINE)
    f.append(p2_box)

    # Журнал подій справа
    q2_box, _, _ = textbox(747, 215, "Журнал подій\n(5-байт заголовок\n+ двійкове тіло)",
                           size=10, bold=True, min_w=105, pad=6, fill=GREEN_F, stroke=FIELD)
    f.append(q2_box)

    # Споживачі справа
    c4_box, _, _ = textbox(895, 215, "Споживачі A, B, C\n1. Читання ID=42\n2. Кеш схеми в RAM\n3. Безпечна резолюція",
                           size=10, bold=True, min_w=135, pad=6, fill=GREEN_F, stroke=FIELD)
    f.append(c4_box)

    # Стрілки взаємодії
    f.append(arrow(600, 180, 640, 140, color=NEG, sw=1.3))
    f.append(arrow(662, 215, 692, 215, color=FIELD, sw=1.3))
    f.append(arrow(802, 215, 825, 215, color=FIELD, sw=1.3))
    f.append(arrow(885, 180, 850, 140, color=NEG, sw=1.3))

    f.append(text(747, 335, "✓ Несумісна зміна відхиляється ще на етапі CI або реєстрації", size=10.5, color=FIELD, italic=True))
    f.append(text(747, 355, "✓ Споживачі автоматично адаптують поля за правилами резолюції", size=10.5, color=FIELD, italic=True))
    f.append(text(747, 375, "✓ Повідомлення компактні (без надлишкових імен полів)", size=10.5, color=FIELD, italic=True))

    render(out("poison-pill-vs-registry.svg"), W, H, *f,
           title="Інцидент отруєного повідомлення проти контролю реєстром схем")


# ── 2. wire-format-framing: структура кадру Confluent Wire Format ──────────
def fig_wire_format_framing():
    W, H = 960, 360
    f = []

    f.append(rect(15, 15, 930, 330, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(480, 42, "Структура 5-байтового кадру (Wire Format) для бінарної серіалізації", size=14, bold=True))

    # Верхня діаграма: байти кадру
    # Magic Byte (1 байт)
    f.append(rect(70, 80, 120, 90, fill=WARN_F, stroke="#d39e00", sw=1.5, rx=4))
    f.append(text(130, 105, "Байт 0 (Magic)", size=11, bold=True, color="#856404"))
    f.append(text(130, 128, "0x00", size=15, bold=True, color=INK))
    f.append(text(130, 153, "Маркер формату", size=10, color=MUTED))

    # Schema ID (4 байти)
    f.append(rect(200, 80, 240, 90, fill=BLUE_F, stroke=NEG, sw=1.5, rx=4))
    f.append(text(320, 105, "Байти 1–4 (Schema ID)", size=11, bold=True, color=NEG))
    f.append(text(320, 128, "0x00 0x00 0x01 0x2A  (= 298)", size=13, bold=True, color=INK))
    f.append(text(320, 153, "32-бітний Big-Endian ID у реєстрі", size=10, color=MUTED))

    # Binary Payload (N байтів)
    f.append(rect(450, 80, 440, 90, fill=GREEN_F, stroke=FIELD, sw=1.5, rx=4))
    f.append(text(670, 105, "Байти 5...N (Бінарне корисне навантаження)", size=11, bold=True, color=FIELD))
    f.append(text(670, 128, "0x12 0x7F 0x00 0x8C 0xA4 0x02 0x3E ...", size=13, bold=True, color=INK))
    f.append(text(670, 153, "Чисті двійкові дані Avro / Protobuf (без метаданих та імен полів)", size=10, color=MUTED))

    # Дужка-пояснення під заголовком
    f.append(line(70, 180, 440, 180, color=MUTED, sw=1.2))
    f.append(line(70, 175, 70, 185, color=MUTED, sw=1.2))
    f.append(line(440, 175, 440, 185, color=MUTED, sw=1.2))
    f.append(text(255, 198, "Службовий заголовок: рівно 5 байтів оверхеду", size=10.5, bold=True, color=INK))

    # Нижня частина: порівняння навантаження на мережу
    f.append(rect(40, 225, 420, 100, fill="#fafbfc", stroke=MUTED, sw=1, rx=6))
    f.append(text(250, 248, "Текстовий JSON (Самоописний формат)", size=11, bold=True, color=POS))
    f.append(text(250, 272, "{\"order_id\": 98124, \"customer_id\": \"usr_42\", \"amount\": 4990, ...}", size=10, color=MUTED))
    f.append(text(250, 295, "Розмір: ~350–800 байтів / повідомлення (75% — повтор імен полів)", size=10, bold=True, color=POS))

    f.append(rect(500, 225, 420, 100, fill="#fafbfc", stroke=MUTED, sw=1, rx=6))
    f.append(text(710, 248, "Wire Format + Avro Binary (Схема в реєстрі)", size=11, bold=True, color=FIELD))
    f.append(text(710, 272, "5 байтів заголовка + 24 байти двійкового тіла = 29 байтів", size=10, color=MUTED))
    f.append(text(710, 295, "Розмір: ~25–45 байтів / повідомлення (економія трафіку 85–95%)", size=10, bold=True, color=FIELD))

    render(out("wire-format-framing.svg"), W, H, *f,
           title="Структура кадру Wire Format та порівняння розміру")


# ── 3. schema-registry-flow: архітектура та шлях повідомлення ──────────────
def fig_schema_registry_flow():
    W, H = 1000, 480
    f = []

    f.append(rect(15, 15, 970, 450, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 42, "Архітектура взаємодії: життєвий цикл повідомлення з реєстром схем", size=14, bold=True))

    # Зверху: Кластер Schema Registry + внутрішній топік _schemas
    f.append(rect(340, 70, 320, 110, fill=BLUE_F, stroke=NEG, sw=1.5, rx=6))
    f.append(text(500, 93, "SCHEMA REGISTRY CLUSTER", size=12, bold=True, color=NEG))
    f.append(text(500, 113, "Лідер (Raft / Kafka Leader) + Фоловері", size=10, color=INK))
    f.append(line(360, 124, 640, 124, color=MUTED, sw=0.8))
    f.append(text(500, 142, "Внутрішній топік: _schemas (compacted, RF=3)", size=10, bold=True, color="#1e429f"))
    f.append(text(500, 160, "Незмінні ID схем: id=42 ↔ version=2 (orders-value)", size=10, color=MUTED))

    # Зліва: Продюсер
    f.append(rect(40, 210, 240, 220, fill=FILL, stroke=LINE, sw=1.3, rx=6))
    f.append(text(160, 235, "ПРОДЮСЕР (Writer)", size=12, bold=True, color=INK))
    f.append(line(55, 245, 265, 245, color=MUTED, sw=0.8))
    f.append(text(160, 265, "Локальна схема Order.avsc (v2)", size=10, bold=True, color=INK))
    f.append(rect(55, 280, 210, 50, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    f.append(text(160, 298, "Локальний кеш (RAM):", size=10, bold=True, color=MUTED))
    f.append(text(160, 316, "Schema Hash ➔ ID: 42", size=10.5, bold=True, color=FIELD))
    f.append(text(160, 350, "1. Серіалізує об'єкт в Avro", size=10, color=INK))
    f.append(text(160, 370, "2. Додає [0x00, ID:42] заголовок", size=10, color=INK))
    f.append(text(160, 390, "3. Відправляє в Kafka топік", size=10, color=INK))
    f.append(text(160, 412, "0 HTTP-запитів на гарячому шляху", size=10, bold=True, color=FIELD))

    # По центру: Брокер повідомлень (Kafka)
    f.append(rect(370, 250, 260, 140, fill=WARN_F, stroke="#d39e00", sw=1.3, rx=6))
    f.append(text(500, 275, "БРОКЕР ПОВІДОМЛЕНЬ (Kafka)", size=12, bold=True, color="#856404"))
    f.append(line(385, 287, 615, 287, color="#d39e00", sw=0.8))
    f.append(text(500, 308, "Топік: orders.placed (partition 0..N)", size=10.5, bold=True, color=INK))
    f.append(rect(390, 323, 220, 45, fill="#ffffff", stroke="#d39e00", sw=1, rx=4))
    f.append(text(500, 342, "Кадр: [0x00][ID:42][Binary Payload]", size=10, bold=True, color=INK))
    f.append(text(500, 358, "Компактне зберігання в журналі", size=9.5, color=MUTED))

    # Справа: Споживач
    f.append(rect(720, 210, 240, 220, fill=FILL, stroke=LINE, sw=1.3, rx=6))
    f.append(text(840, 235, "СПОЖИВАЧ (Reader)", size=12, bold=True, color=INK))
    f.append(line(735, 245, 945, 245, color=MUTED, sw=0.8))
    f.append(text(840, 265, "Локальна схема Reader (v1)", size=10, bold=True, color=INK))
    f.append(rect(735, 280, 210, 50, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    f.append(text(840, 298, "Локальний кеш (RAM):", size=10, bold=True, color=MUTED))
    f.append(text(840, 316, "ID: 42 ➔ Writer Schema v2", size=10.5, bold=True, color=FIELD))
    f.append(text(840, 350, "1. Витягує ID=42 з перших 5 байт", size=10, color=INK))
    f.append(text(840, 370, "2. Дістає Writer Schema з кешу", size=10, color=INK))
    f.append(text(840, 390, "3. Резолюція: Writer v2 ➔ Reader v1", size=10, color=INK))
    f.append(text(840, 412, "Швидка десеріалізація в пам'яті", size=10, bold=True, color=FIELD))

    # Зв'язки (Стрілки)
    # 1. Продюсер -> Registry (реєстрація / перевірка)
    f.append(arrow(180, 210, 380, 180, color=NEG, sw=1.5))
    f.append(text(235, 175, "POST /subjects/... (при старті / miss)", size=10, bold=True, color=NEG))

    # 2. Продюсер -> Kafka (публікація)
    f.append(arrow(280, 320, 368, 320, color=FIELD, sw=1.8))
    f.append(text(324, 310, "Produce", size=10, bold=True, color=FIELD))

    # 3. Kafka -> Споживач (читання)
    f.append(arrow(630, 320, 718, 320, color=FIELD, sw=1.8))
    f.append(text(674, 310, "Consume", size=10, bold=True, color=FIELD))

    # 4. Споживач -> Registry (отримання схеми за ID при промаху кешу)
    f.append(arrow(820, 210, 620, 180, color=NEG, sw=1.5))
    f.append(text(765, 175, "GET /schemas/ids/42 (раз на версію)", size=10, bold=True, color=NEG))

    render(out("schema-registry-flow.svg"), W, H, *f,
           title="Життєвий цикл повідомлення та архітектура взаємодії з реєстром схем")


# ── 4. compatibility-matrix: режими сумісності схем ────────────────────────
def fig_compatibility_matrix():
    W, H = 1000, 380
    f = []

    f.append(rect(15, 15, 970, 350, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 40, "Режими сумісності схем та правила оновлення сервісів", size=14, bold=True))

    modes = [
        ("BACKWARD (Зворотна)",
         "Reader(нова) читає Writer(стара)",
         "Споживачі (Consumers)",
         "• Видалення полів\n• Додавання необов'язкових\n  полів зі значенням за замовчуванням\n• Заборонено: нові обов'язкові поля",
         BLUE_F, NEG, 170),
        ("FORWARD (Пряма)",
         "Reader(стара) читає Writer(нова)",
         "Продюсери (Producers)",
         "• Додавання нових полів\n• Видалення необов'язкових\n  полів (зі старим дефолтом)\n• Заборонено: видаляти обов'язкові",
         WARN_F, "#856404", 500),
        ("FULL (Повна двостороння)",
         "Reader(нова) ↔ Writer(стара)\nі Reader(стара) ↔ Writer(нова)",
         "Будь-який (незалежно)",
         "• Додавання лише полів із дефолтом\n• Видалення лише полів із дефолтом\n• Найвища безпека для мікросервісів\n• Canary / Blue-Green релізи",
         GREEN_F, FIELD, 830),
    ]

    for title, rule, order, changes, bg_c, strk_c, cx in modes:
        f.append(rect(cx - 150, 70, 300, 270, fill=bg_c, stroke=strk_c, sw=1.5, rx=6))
        f.append(text(cx, 95, title, size=12.5, bold=True, color=INK))
        f.append(line(cx - 135, 107, cx + 135, 107, color=strk_c, sw=1))

        # Формула сумісності
        f.append(rect(cx - 135, 118, 270, 38, fill="#ffffff", stroke=strk_c, sw=0.8, rx=4))
        f.append(mtext(cx, 134, rule.split("\n"), size=10, bold=True, color=strk_c, lh=1.2))

        # Хто оновлюється першим
        f.append(text(cx, 175, "Хто оновлюється першим:", size=10, color=MUTED))
        f.append(text(cx, 195, order, size=11, bold=True, color=INK))

        # Дозволені зміни
        f.append(line(cx - 135, 210, cx + 135, 210, color=MUTED, sw=0.6))
        f.append(text(cx, 226, "Дозволені операції над схемою:", size=10, bold=True, color=INK))
        f.append(mtext(cx - 125, 245, changes.split("\n"), size=9.5, color=INK, anchor="start", lh=1.3))

    render(out("compatibility-matrix.svg"), W, H, *f,
           title="Матриця режимів сумісності схем")


# ── 5. avro-reader-writer-resolution: механіка резолюції полів ─────────────
def fig_avro_reader_writer_resolution():
    W, H = 1000, 420
    f = []

    f.append(rect(15, 15, 970, 390, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 40, "Механізм резолюції схем Avro: зіставлення схеми писаря та схеми читача", size=14, bold=True))

    # Лівий блок: Схема писаря (Writer Schema v1, отримана з реєстру за ID)
    f.append(rect(40, 70, 270, 310, fill=FILL, stroke=LINE, sw=1.3, rx=6))
    f.append(text(175, 95, "СХЕМА ПИСАРЯ (Writer v1)", size=11.5, bold=True, color=INK))
    f.append(text(175, 112, "Отримана з реєстру (Schema ID: 42)", size=10, color=MUTED))
    f.append(line(55, 122, 295, 122, color=MUTED, sw=0.8))

    w_fields = [
        ("order_id: long", 150, "Ідентифікатор замовлення", BLUE_F),
        ("amount: int", 210, "Сума у центах (int 32-bit)", WARN_F),
        ("legacy_note: string", 270, "Старий коментар (видалено у v2)", RED_F),
        ("user_id: string", 330, "ID покупця", BLUE_F)
    ]
    for fn, y, desc, bg in w_fields:
        f.append(rect(55, y - 18, 240, 46, fill=bg, stroke=MUTED, sw=0.8, rx=4))
        f.append(text(70, y, fn, size=10.5, bold=True, color=INK, anchor="start"))
        f.append(text(70, y + 18, desc, size=9.5, color=MUTED, anchor="start"))

    # Правий блок: Схема читача (Reader Schema v2, скомпільована в коді споживача)
    f.append(rect(690, 70, 270, 310, fill=FILL, stroke=LINE, sw=1.3, rx=6))
    f.append(text(825, 95, "СХЕМА ЧИТАЧА (Reader v2)", size=11.5, bold=True, color=INK))
    f.append(text(825, 112, "Вбудована в код споживача", size=10, color=MUTED))
    f.append(line(705, 122, 945, 122, color=MUTED, sw=0.8))

    r_fields = [
        ("order_id: long", 150, "Прямий збіг типу й імені", BLUE_F),
        ("amount: long", 210, "Розширення типу: int ➔ long", WARN_F),
        ("currency: string = \"USD\"", 270, "Нове поле з дефолтним значенням", GREEN_F),
        ("user_id: string", 330, "Прямий збіг типу й імені", BLUE_F)
    ]
    for fn, y, desc, bg in r_fields:
        f.append(rect(705, y - 18, 240, 46, fill=bg, stroke=MUTED, sw=0.8, rx=4))
        f.append(text(720, y, fn, size=10.5, bold=True, color=INK, anchor="start"))
        f.append(text(720, y + 18, desc, size=9.5, color=MUTED, anchor="start"))

    # Центральний блок: Резолюція (Правила зіставлення)
    f.append(rect(340, 70, 320, 310, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=6))
    f.append(text(500, 95, "РЕЗОЛЮЦІЯ В ПАМ'ЯТІ", size=12, bold=True, color=FIELD))
    f.append(line(360, 108, 640, 108, color=MUTED, sw=0.8))

    # Стрілки та правила зіставлення
    # order_id
    f.append(arrow(295, 150, 705, 150, color=FIELD, sw=1.5))
    f.append(text(500, 142, "1. Точний збіг: читається без змін", size=9.5, bold=True, color=FIELD))

    # amount
    f.append(arrow(295, 210, 705, 210, color="#d39e00", sw=1.5))
    f.append(text(500, 202, "2. Type promotion: 32-bit int ➔ 64-bit long", size=9.5, bold=True, color="#856404"))

    # legacy_note vs currency
    f.append(line(295, 270, 430, 270, color=POS, sw=1.2, dash="3,3"))
    f.append(text(460, 265, "Пропуск", size=9.5, bold=True, color=POS))
    f.append(text(500, 280, "3. legacy_note відкидається (немає у читача)", size=9.5, color=POS))

    f.append(arrow(570, 270, 705, 270, color=FIELD, sw=1.5))
    f.append(text(500, 298, "4. currency підставляється як \"USD\" (дефолт)", size=9.5, color=FIELD))

    # user_id
    f.append(arrow(295, 330, 705, 330, color=FIELD, sw=1.5))
    f.append(text(500, 322, "5. Точний збіг: читається без змін", size=9.5, bold=True, color=FIELD))

    render(out("avro-reader-writer-resolution.svg"), W, H, *f,
           title="Механіка резолюції схем Avro")


if __name__ == "__main__":
    fig_poison_pill_vs_registry()
    fig_wire_format_framing()
    fig_schema_registry_flow()
    fig_compatibility_matrix()
    fig_avro_reader_writer_resolution()
    print("Done generating figures for schema-registry.")
