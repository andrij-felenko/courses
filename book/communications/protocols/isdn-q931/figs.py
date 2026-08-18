# -*- coding: utf-8 -*-
"""Фігури до теми «ISDN і сигналізація Q.931»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SOFT = "#eef3fb"
WARM = "#fdf3e6"
COOL = "#eefaf1"
ACCENT = "#8e44ad"


# ─────────────────────────────────────────────────────────────────────────────
# 1. Еталонна модель ISDN (функціональні блоки й точки прив'язки) та структури BRI/PRI
# ─────────────────────────────────────────────────────────────────────────────
def fig_reference_model():
    W, H = 1040, 680
    f = []

    # Тло блоку моделі пристроїв
    f.append(rect(20, 20, 1000, 310, fill="#ffffff", stroke="#c8d6ea", sw=1.4, rx=10))
    f.append(text(40, 48, "Еталонна архітектура абонентського доступу ISDN (ITU-T I.411)",
                  size=14, color=INK, anchor="start", bold=True))

    # Пристрої верхнього ряду (через TA)
    f.append(fitbox(40, 75, 120, 60, "TE2\nАналоговий тел. / RS-232", size=11, fill=WARM, bold=True))
    f.append(fitbox(210, 75, 110, 60, "TA\nТермінальний адаптер", size=11, fill=SOFT, bold=True))
    f.append(arrow(160, 105, 210, 105, color=LINE, sw=1.5))
    f.append(text(185, 96, "R", size=13, color=POS, bold=True))

    # Пристрої другого ряду (нативний TE1)
    f.append(fitbox(40, 160, 120, 60, "TE1\nISDN-термінал\n(цифровий апарат)", size=11, fill=COOL, bold=True))

    # З'єднання до NT2 (PBX)
    f.append(fitbox(380, 115, 120, 80, "NT2\nОфісна АТС (PBX)\n/ Мультиплексор", size=11, fill=SOFT, bold=True))
    f.append(arrow(320, 105, 380, 135, color=LINE, sw=1.5))
    f.append(arrow(160, 190, 380, 165, color=LINE, sw=1.5))
    f.append(text(348, 112, "S", size=13, color=POS, bold=True))
    f.append(text(270, 198, "S (пасивна шина)", size=12, color=POS, bold=True))

    # З'єднання до NT1
    f.append(fitbox(560, 115, 120, 80, "NT1\nМережеве закінчення\n(L1 перетворювач)", size=11, fill=WARM, bold=True))
    f.append(arrow(500, 155, 560, 155, color=LINE, sw=1.5))
    f.append(text(530, 145, "T", size=13, color=POS, bold=True))

    # Лінія до станції (U-інтерфейс)
    f.append(fitbox(820, 115, 180, 80, "LE / ET\nМісцева станція\n(комутатор оператора)", size=11, fill=COOL, bold=True))
    f.append(arrow(680, 155, 820, 155, color=NEG, sw=2.2))
    f.append(text(750, 142, "U (2-провідна абонентська пара)", size=12, color=NEG, bold=True))
    f.append(text(750, 172, "2B1Q або 4B3T · до 5.5 км", size=11, color=MUTED))

    # Пояснення прямого підключення без NT2
    f.append(rect(40, 245, 960, 65, fill=FILL, stroke="#d0d7de", sw=1.0, rx=6))
    f.append(text(520, 270, "Пряме абонентське підключення (без офісної АТС): точки S і T зливаються в єдиний 4-провідний інтерфейс S/T",
                  size=12, color=INK, bold=True))
    f.append(text(520, 292, "NT1 живить пасивну шину (S-bus) та узгоджує 4 проводи всередині будівлі з 2-провідною парою оператора (U)",
                  size=11, color=MUTED))

    # ── Нижня частина: порівняння BRI та PRI ───────────────────────────────
    f.append(rect(20, 350, 1000, 310, fill="#ffffff", stroke="#c8d6ea", sw=1.4, rx=10))
    f.append(text(40, 378, "Структури каналів доступу ISDN: BRI проти PRI (E1 / T1)",
                  size=14, color=INK, anchor="start", bold=True))

    # BRI блок
    f.append(rect(40, 400, 460, 240, fill=SOFT, stroke="#c8d6ea", sw=1.2, rx=8))
    f.append(text(270, 426, "Базовий доступ BRI (2B + D)", size=13, color=INK, bold=True))
    f.append(text(270, 448, "Корисна швидкість: 144 кбіт/с · Лінійна на S/T: 192 кбіт/с", size=11, color=MUTED))

    f.append(fitbox(60, 470, 190, 50, "B1-канал: 64 кбіт/с\nГолос G.711 / Чисті дані", size=11, fill="#ffffff", bold=True))
    f.append(fitbox(270, 470, 190, 50, "B2-канал: 64 кбіт/с\nГолос G.711 / Чисті дані", size=11, fill="#ffffff", bold=True))
    f.append(fitbox(160, 535, 220, 45, "D-канал: 16 кбіт/с\nСигналізація Q.931 / LAPD", size=11, fill=WARM, bold=True))
    f.append(rect(60, 595, 420, 30, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=4))
    f.append(text(270, 615, "Службові біти кадру L1 (синхронізація, ехо D-каналу): 48 кбіт/с", size=10.5, color=MUTED))

    # PRI блок
    f.append(rect(520, 400, 480, 240, fill=COOL, stroke="#c8e6c9", sw=1.2, rx=8))
    f.append(text(760, 426, "Первинний доступ PRI (Магістральний потік)", size=13, color=INK, bold=True))
    f.append(text(760, 448, "Європа / ITU: E1 (2.048 Мбіт/с) · Північна Америка: T1 (1.544 Мбіт/с)", size=11, color=MUTED))

    f.append(fitbox(540, 470, 440, 52, "E1 PRI: 30B + D + Framing (32 таймслоти × 64 кбіт/с)\nТаймслот 0 = Синхронізація/FAS, Таймслот 16 = D-канал 64 кбіт/с", size=10.5, fill="#ffffff", bold=True))
    f.append(fitbox(540, 535, 440, 45, "T1 PRI: 23B + D (24 таймслоти × 64 кбіт/с + 8 кбіт/с кадрування)\nТаймслот 24 = D-канал 64 кбіт/с сигналізації Q.931", size=10.5, fill="#ffffff", bold=True))
    f.append(rect(540, 595, 440, 30, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=4))
    f.append(text(760, 615, "NFAS: 1 D-канал може керувати до 20 транками T1/E1 (до 479 B-каналів)", size=10.5, color=MUTED))

    render(os.path.join(OUT, 'isdn-reference-model.svg'), W, H, *f,
           title="Еталонна архітектура ISDN та структури інтерфейсів BRI і PRI")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Стек протоколів D-каналу та бінарне інкапсулювання LAPD / Q.931
# ─────────────────────────────────────────────────────────────────────────────
def fig_stack_framing():
    W, H = 1040, 720
    f = []

    f.append(rect(20, 20, 1000, 680, fill="#ffffff", stroke="#c8d6ea", sw=1.4, rx=10))
    f.append(text(40, 48, "Стек сигналізації D-каналу та анатомія кадру LAPD (Q.921) + Q.931",
                  size=14, color=INK, anchor="start", bold=True))

    # Стек рівнів (зліва)
    f.append(rect(40, 75, 230, 200, fill=FILL, stroke="#c8d6ea", sw=1.2, rx=8))
    f.append(text(155, 98, "Стек рівнів D-каналу", size=12, color=INK, bold=True))

    f.append(fitbox(55, 115, 200, 42, "Рівень 3: ITU-T Q.931\nКерування викликами (Call Control)", size=10, fill=WARM, bold=True))
    f.append(fitbox(55, 165, 200, 42, "Рівень 2: LAPD (Q.921)\nНадійний канал кадрів (HDLC)", size=10, fill=SOFT, bold=True))
    f.append(fitbox(55, 215, 200, 42, "Рівень 1: I.430 (BRI) / I.431 (PRI)\nФізичний рівень, TDM, біти E", size=10, fill=COOL, bold=True))

    # Загальна структура кадру LAPD (справа вгорі)
    f.append(rect(300, 75, 700, 200, fill=SOFT, stroke="#c8d6ea", sw=1.2, rx=8))
    f.append(text(320, 98, "Кадр LAPD канального рівня L2 (передається біт-орієнтовано з прапорцями 0x7E)",
                  size=12, color=INK, anchor="start", bold=True))

    # Блоки кадру LAPD
    blocks_l2 = [
        (320, 60, "Прапорець\n0x7E", WARM),
        (385, 120, "Адреса (2 байти)\nSAPI, C/R, TEI", COOL),
        (510, 110, "Керування (1-2 Б)\nI / S / U-кадр", COOL),
        (625, 230, "Інформаційне поле (Інфо)\nКорисне навантаження L3 (Пакет Q.931)", WARM),
        (860, 75, "FCS (CRC-16)\n2 байти", COOL),
        (940, 50, "0x7E", WARM),
    ]
    for bx, bw, blabel, bfill in blocks_l2:
        f.append(fitbox(bx, 115, bw, 48, blabel, size=10, fill=bfill, bold=True))

    # Розшифровка адресної частини LAPD
    f.append(rect(320, 175, 660, 85, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=6))
    f.append(text(335, 195, "Адресне поле LAPD:", size=11, color=INK, anchor="start", bold=True))
    f.append(text(335, 216, "• SAPI (6 бітів): 0 = Сигналізація виклику Q.931; 16 = Пакети X.25; 63 = Керування TEI", size=10.5, color=MUTED, anchor="start"))
    f.append(text(335, 234, "• C/R (1 біт): Команда / Відповідь · EA0/EA1: Біти розширення адреси (0 у 1-му байті, 1 у 2-му)", size=10.5, color=MUTED, anchor="start"))
    f.append(text(335, 252, "• TEI (7 бітів): 0 = Точка-точка (PRI/PBX); 64–126 = Динамічні адреси терміналів BRI; 127 = Broadcast", size=10.5, color=MUTED, anchor="start"))

    # ── Нижня частина: анатомія повідомлення Q.931 ─────────────────────────
    f.append(rect(40, 295, 960, 390, fill=WARM, stroke="#f5c6cb", sw=1.2, rx=8))
    f.append(text(60, 322, "Анатомія повідомлення Q.931 (L3 PDU)", size=13, color=INK, anchor="start", bold=True))

    # Складові заголовка Q.931
    f.append(fitbox(60, 340, 180, 55, "Дискримінатор протоколу\n1 байт: 0x08 = Q.931\n(0x03 = X.25, 0x40 = Q.932)", size=10, fill="#ffffff", bold=True))
    f.append(fitbox(250, 340, 230, 55, "Call Reference (Посилання виклику)\n1 байт довжини + 1-2 байти значення\nСтарший біт: 0=Originator, 1=Destination", size=10, fill="#ffffff", bold=True))
    f.append(fitbox(490, 340, 180, 55, "Тип повідомлення\n1 байт: SETUP (0x05),\nCONNECT (0x07), DISC...", size=10, fill="#ffffff", bold=True))
    f.append(fitbox(680, 340, 300, 55, "Змінні інформаційні елементи (IE)\nНабір параметрів змінної довжини (TLV):\nНомери, Кодеки, Канал, Причина", size=10, fill="#ffffff", bold=True))

    # Структура інформаційних елементів (IE)
    f.append(rect(60, 410, 920, 260, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=6))
    f.append(text(80, 432, "Ключові інформаційні елементи (Information Elements, IE) у повідомленнях Q.931:",
                  size=11.5, color=INK, anchor="start", bold=True))

    ies = [
        ("0x04 · Bearer Capability", "Тип послуги: Мова G.711 (A/μ-law), 3.1 кГц аудіо (модем/факс), Unrestricted Digital 64k (дані без обробки).", 455),
        ("0x18 · Channel Identification", "Вибір B-каналу: B1 або B2 для BRI, номер таймслота 1–31 для PRI. Прапорець: Preferred (бажаний) чи Exclusive (виключний).", 495),
        ("0x6C · Calling Party Number", "Номер абонента, що кличе (E.164), тип номера (міжнародний/національний), ознака заборони показу номера (CLIR).", 535),
        ("0x70 · Called Party Number", "Номер абонента, якого кличуть (E.164 цифри призначення: план нумерації, код міста, номер лінії).", 575),
        ("0x08 · Cause (Причина)", "Діагностичний код завершення/відмови: 16 = Normal clearing, 17 = User busy, 1 = Unallocated number, 34 = No circuit.", 615),
        ("0x28 · Display / 0x1E · Progress", "Текстовий напис для екрана телефону або індикатор внутрішньосмугового сигналу (In-band information available).", 655),
    ]
    for code_name, desc, y_pos in ies:
        f.append(text(80, y_pos, code_name, size=11, color=POS, anchor="start", bold=True))
        f.append(text(310, y_pos, desc, size=10.5, color=INK, anchor="start"))

    render(os.path.join(OUT, 'q931-stack-framing.svg'), W, H, *f,
           title="Стек протоколів D-каналу та бінарне кодування кадрів LAPD і Q.931")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Діаграма обміну повідомленнями встановлення та розриву виклику Q.931
# ─────────────────────────────────────────────────────────────────────────────
def fig_call_flow():
    W, H = 1040, 840
    f = []

    f.append(rect(20, 20, 1000, 800, fill="#ffffff", stroke="#c8d6ea", sw=1.4, rx=10))
    f.append(text(40, 48, "Повний цикл виклику Q.931: встановлення, розмова по B-каналу та розрив",
                  size=14, color=INK, anchor="start", bold=True))

    # Вертикальні лінії сутностей
    # TE-A (140), LE-A (370), LE-B (670), TE-B (900)
    entities = [
        (140, "Абонент А (TE1-A)\nТермінал, що дзвонить", WARM),
        (370, "Станція А (LE-A)\nМісцевий комутатор", SOFT),
        (670, "Станція Б (LE-B)\nКінцевий комутатор", SOFT),
        (900, "Абонент Б (TE1-B)\nТермінал, що приймає", COOL),
    ]

    for cx, label, fill_col in entities:
        f.append(fitbox(cx - 90, 65, 180, 45, label, size=10.5, fill=fill_col, bold=True))
        f.append(line(cx, 115, cx, 790, color="#b0bec5", sw=1.5, dash="4,4"))

    # Фаза 1: Встановлення виклику
    f.append(rect(40, 120, 960, 24, fill="#f0f4f8", stroke="none"))
    f.append(text(520, 136, "ФАЗА 1: ІНІЦІАЦІЯ ТА МАРШРУТИЗАЦІЯ ВИКЛИКУ (SETUP)", size=11, color=INK, bold=True))

    # SETUP від A до LE-A
    f.append(arrow(140, 160, 370, 160, color=POS, sw=2.0))
    f.append(text(255, 150, "SETUP (CRV=1, Bearer=Voice, B1)", size=10.5, color=POS, bold=True))
    f.append(text(80, 162, "Старт T303", size=9.5, color=MUTED))

    # CALL PROCEEDING від LE-A до A
    f.append(arrow(370, 190, 140, 190, color=LINE, sw=1.5))
    f.append(text(255, 182, "CALL PROCEEDING (B1 виділено)", size=10.5, color=LINE))
    f.append(text(80, 192, "Стоп T303, старт T310", size=9.5, color=MUTED))

    # Магістральна сигналізація між станціями (SS7 ISUP IAM)
    f.append(arrow(370, 220, 670, 220, color=NEG, sw=2.0))
    f.append(text(520, 210, "Магістраль SS7 ISUP: IAM (Initial Address Message)", size=10.5, color=NEG, bold=True))

    # SETUP від LE-B до B
    f.append(arrow(670, 250, 900, 250, color=POS, sw=2.0))
    f.append(text(785, 242, "SETUP (CRV=85, Bearer, B-ch)", size=10.5, color=POS, bold=True))

    # Фаза 2: Дзвінок і відповідь
    f.append(rect(40, 275, 960, 24, fill="#f0f4f8", stroke="none"))
    f.append(text(520, 291, "ФАЗА 2: ОПОВІЩЕННЯ (ALERTING) ТА ВІДПОВІДЬ (CONNECT)", size=11, color=INK, bold=True))

    # ALERTING від B до LE-B
    f.append(arrow(900, 315, 670, 315, color=FIELD, sw=1.8))
    f.append(text(785, 307, "ALERTING (термінал дзвонить)", size=10.5, color=FIELD, bold=True))

    # ISUP ACM
    f.append(arrow(670, 345, 370, 345, color=NEG, sw=2.0))
    f.append(text(520, 337, "SS7 ISUP: ACM (Address Complete Message)", size=10.5, color=NEG))

    # ALERTING до A
    f.append(arrow(370, 375, 140, 375, color=FIELD, sw=1.8))
    f.append(text(255, 367, "ALERTING (гудки контролю посилки виклику)", size=10.5, color=FIELD))
    f.append(text(80, 377, "Стоп T310, старт T301", size=9.5, color=MUTED))

    # Абонент Б бере слухавку: CONNECT
    f.append(arrow(900, 410, 670, 410, color=POS, sw=2.2))
    f.append(text(785, 402, "CONNECT (знято слухавку)", size=10.5, color=POS, bold=True))

    f.append(arrow(670, 435, 900, 435, color=LINE, sw=1.5))
    f.append(text(785, 427, "CONNECT ACKNOWLEDGE", size=10, color=LINE))

    # ISUP ANM
    f.append(arrow(670, 465, 370, 465, color=NEG, sw=2.0))
    f.append(text(520, 457, "SS7 ISUP: ANM (Answer Message)", size=10.5, color=NEG, bold=True))

    # CONNECT до A
    f.append(arrow(370, 495, 140, 495, color=POS, sw=2.2))
    f.append(text(255, 487, "CONNECT", size=10.5, color=POS, bold=True))
    f.append(text(80, 497, "Стоп T301", size=9.5, color=MUTED))

    f.append(arrow(140, 520, 370, 520, color=LINE, sw=1.5))
    f.append(text(255, 512, "CONNECT ACKNOWLEDGE", size=10, color=LINE))

    # Фаза 3: Активна розмова
    f.append(rect(40, 545, 960, 50, fill=COOL, stroke="#81c784", sw=1.5, rx=6))
    f.append(text(520, 567, "АКТИВНА РОЗМОВА: B-КАНАЛ (64 кбіт/с, PCM G.711 прозорий потік в обидва боки)", size=12, color=FIELD, bold=True))
    f.append(text(520, 585, "Стан Q.931: U10 (Active / Active) · D-канал вільний для інших викликів або сигналів", size=11, color=MUTED))

    # Фаза 4: Розрив з'єднання (Teardown)
    f.append(rect(40, 608, 960, 24, fill="#f0f4f8", stroke="none"))
    f.append(text(520, 624, "ФАЗА 4: РОЗРИВ З'ЄДНАННЯ (DISCONNECT / RELEASE / RELEASE COMPLETE)", size=11, color=INK, bold=True))

    # Абонент А кладе слухавку: DISCONNECT
    f.append(arrow(140, 648, 370, 648, color=POS, sw=2.0))
    f.append(text(255, 640, "DISCONNECT (Cause #16 Normal Clearing)", size=10.5, color=POS, bold=True))
    f.append(text(80, 650, "Старт T305", size=9.5, color=MUTED))

    # ISUP REL
    f.append(arrow(370, 675, 670, 675, color=NEG, sw=2.0))
    f.append(text(520, 667, "SS7 ISUP: REL (Release)", size=10.5, color=NEG))

    # LE-A шле RELEASE до А
    f.append(arrow(370, 700, 140, 700, color=LINE, sw=1.8))
    f.append(text(255, 692, "RELEASE (B-канал звільнено)", size=10.5, color=LINE))
    f.append(text(80, 702, "Стоп T305, старт T308", size=9.5, color=MUTED))

    # A шле RELEASE COMPLETE до LE-A
    f.append(arrow(140, 725, 370, 725, color=LINE, sw=1.8))
    f.append(text(255, 717, "RELEASE COMPLETE (CRV закрито)", size=10.5, color=LINE))
    f.append(text(80, 727, "Стоп T308 -> Стан U0 (Null)", size=9.5, color=MUTED))

    # До абонента Б
    f.append(arrow(670, 750, 900, 750, color=POS, sw=2.0))
    f.append(text(785, 742, "DISCONNECT (Cause #16)", size=10.5, color=POS))

    f.append(arrow(900, 775, 670, 775, color=LINE, sw=1.8))
    f.append(text(785, 767, "RELEASE / RELEASE COMPLETE", size=10, color=LINE))

    render(os.path.join(OUT, 'q931-call-flow.svg'), W, H, *f,
           title="Послідовність сигнальних повідомлень Q.931 під час встановлення та завершення виклику")


if __name__ == '__main__':
    fig_reference_model()
    fig_stack_framing()
    fig_call_flow()
    print("Всі фігури згенеровано успішно.")
