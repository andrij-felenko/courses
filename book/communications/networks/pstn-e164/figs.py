# -*- coding: utf-8 -*-
"""Фігури до теми «Телефонна мережа й нумерація E.164».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b9770e"     # транзитні вузли / бази даних SCP
PURPLE = "#7c3aed"    # сигнальна площина SS7
CYAN = "#0891b2"      # цифрові потоки TDM / E1
GREEN = "#27ae60"     # голосовий тракт / успішний стан

# ── 1. Архітектура PSTN: площина комутації каналів і площина сигналізації SS7 ─
def fig_pstn_hierarchy_ss7():
    W, H = 880, 520
    p = [text(W / 2, 24, "Дворівнева архітектура PSTN: голосовий тракт TDM та сигнальна мережа SS7", size=15, bold=True)]

    # Фонова зона для площини сигналізації SS7
    p.append(rect(15, 45, W - 30, 195, fill="#faf5ff", stroke=PURPLE, sw=1.2, rx=8))
    p.append(text(30, 70, "Площина сигналізації (Out-of-Band SS7 / CCS7 Network): комутація пакетів", size=11.5, color=PURPLE, bold=True, anchor="start"))

    # Фонова зона для площини передачі голосу TDM
    p.append(rect(15, 255, W - 30, 235, fill="#f0fdf4", stroke=GREEN, sw=1.2, rx=8))
    p.append(text(30, 280, "Площина голосових каналів (Bearer TDM Network): комутація каналів 64 кбіт/с DS0", size=11.5, color=GREEN, bold=True, anchor="start"))

    # Вузли SS7 площини
    # STP-A (Signal Transfer Point)
    p.append(rect(240, 95, 170, 85, fill="#ffffff", stroke=PURPLE, sw=1.8, rx=6))
    p.append(text(325, 122, "STP (Вузол A)", size=13, color=PURPLE, bold=True))
    p.append(text(325, 144, "Маршрутизатор SS7", size=10.5, color=MUTED))
    p.append(text(325, 163, "Пакетна комутація MTP3", size=10, color=INK))

    # STP-B
    p.append(rect(470, 95, 170, 85, fill="#ffffff", stroke=PURPLE, sw=1.8, rx=6))
    p.append(text(555, 122, "STP (Вузол B)", size=13, color=PURPLE, bold=True))
    p.append(text(555, 144, "Транзит сигналізації", size=10.5, color=MUTED))
    p.append(text(555, 163, "SCCP / Global Title", size=10, color=INK))

    # SCP (Service Control Point)
    p.append(rect(690, 95, 165, 85, fill="#fffbeb", stroke=AMBER, sw=1.8, rx=6))
    p.append(text(772, 122, "SCP (База даних)", size=13, color=AMBER, bold=True))
    p.append(text(772, 144, "Інтелектуальна мережа", size=10.5, color=MUTED))
    p.append(text(772, 163, "800-номери / MNP / TCAP", size=10, color=INK))

    # Лінії сигналізації між STP та SCP
    p.append(line(410, 137, 470, 137, color=PURPLE, sw=2.0, dash="4,3"))
    p.append(line(640, 137, 690, 137, color=AMBER, sw=2.0, dash="4,3"))
    p.append(text(440, 125, "MTP3", size=10.5, color=PURPLE, bold=True))
    p.append(text(665, 125, "TCAP", size=10.5, color=AMBER, bold=True))

    # Вузли голосової площини
    # Абонент А
    p.append(rect(30, 310, 110, 130, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(85, 338, "Абонент A", size=12, bold=True))
    p.append(text(85, 362, "Телефон / PBX", size=10.5, color=MUTED))
    p.append(text(85, 386, "Аналог 2-пров.", size=10, color=INK))
    p.append(text(85, 410, "-48 В / DTMF", size=10, color=POS))

    # Local Exchange A (Class 5 / SSP A)
    p.append(rect(180, 300, 170, 150, fill="#ffffff", stroke=GREEN, sw=2.0, rx=6))
    p.append(text(265, 328, "Class 5 (LE / SSP A)", size=12, color=GREEN, bold=True))
    p.append(text(265, 350, "Місцева станція", size=11, color=INK))
    p.append(text(265, 374, "АЦП G.711 / PCM", size=10, color=MUTED))
    p.append(text(265, 398, "Формування ISUP IAM", size=10, color=PURPLE))
    p.append(text(265, 422, "Комутаційне поле TDM", size=10, color=GREEN))

    # Transit / Tandem Switch (Class 4 / SSP Transit)
    p.append(rect(400, 310, 170, 130, fill="#ffffff", stroke=CYAN, sw=1.8, rx=6))
    p.append(text(485, 338, "Class 4 (Tandem)", size=12, color=CYAN, bold=True))
    p.append(text(485, 360, "Транзитна станція", size=11, color=INK))
    p.append(text(485, 386, "Магістральний транзит", size=10, color=MUTED))
    p.append(text(485, 410, "Комутація E1/T1", size=10, color=CYAN))

    # Local Exchange B (Class 5 / SSP B)
    p.append(rect(620, 300, 170, 150, fill="#ffffff", stroke=GREEN, sw=2.0, rx=6))
    p.append(text(705, 328, "Class 5 (LE / SSP B)", size=12, color=GREEN, bold=True))
    p.append(text(705, 350, "Місцева станція", size=11, color=INK))
    p.append(text(705, 374, "Генерація виклику (90V)", size=10, color=POS))
    p.append(text(705, 398, "Відповідь ISUP ACM/ANM", size=10, color=PURPLE))
    p.append(text(705, 422, "ЦАП G.711 / PCM", size=10, color=GREEN))

    # Абонент Б
    p.append(rect(825, 310, 40, 130, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(845, 350, "Абон.", size=10.5, bold=True))
    p.append(text(845, 375, "B", size=13, bold=True, color=POS))
    p.append(text(845, 405, "Дзвін.", size=10, color=MUTED))

    # З'єднання голосової площини
    # Абонент А -> SSP A
    p.append(line(140, 375, 180, 375, color=LINE, sw=2.0))
    p.append(text(160, 365, "Loop", size=9.5, color=MUTED))

    # SSP A -> Tandem
    p.append(line(350, 375, 400, 375, color=GREEN, sw=3.0))
    p.append(text(375, 362, "E1 Trunk", size=10, color=GREEN, bold=True))

    # Tandem -> SSP B
    p.append(line(570, 375, 620, 375, color=GREEN, sw=3.0))
    p.append(text(595, 362, "E1 Trunk", size=10, color=GREEN, bold=True))

    # SSP B -> Абонент Б
    p.append(line(790, 375, 825, 375, color=LINE, sw=2.0))
    p.append(text(807, 365, "Ring", size=9.5, color=POS))

    # Вертикальні сигнальні лінки (A-links від SSP до STP)
    p.append(line(265, 300, 305, 180, color=PURPLE, sw=2.0, dash="5,3"))
    p.append(text(250, 235, "ISUP / MTP2", size=10, color=PURPLE, bold=True))

    p.append(line(450, 310, 365, 180, color=PURPLE, sw=1.5, dash="4,3"))
    p.append(line(520, 310, 525, 180, color=PURPLE, sw=1.5, dash="4,3"))

    p.append(line(705, 300, 595, 180, color=PURPLE, sw=2.0, dash="5,3"))
    p.append(text(685, 235, "ISUP / MTP2", size=10, color=PURPLE, bold=True))

    p.append(text(W / 2, H - 12, "Сигналізація SS7 передається виділеною мережею передачі даних окремо від голосового каналу DS0 64 кбіт/с.",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "pstn-hierarchy-ss7.svg"), W, H, *p)


# ── 2. Структура телефонного номера E.164 ──────────────────────────────────────
def fig_e164_structure():
    W, H = 860, 420
    p = [text(W / 2, 26, "Глобальний план нумерації електрозв'язку ITU-T E.164", size=15, bold=True)]

    # Головний блок: Максимум 15 десяткових цифр
    y0 = 60
    p.append(rect(40, y0, 780, 50, fill="#f8fafc", stroke=LINE, sw=1.8, rx=6))
    p.append(text(430, y0 + 30, "Міжнародний публічний номер електрозв'язку E.164 (максимум 15 цифр)", size=13, bold=True))

    # Рівень 1: Префікс + CC + NSN
    y1 = 135
    # Префікс виходу (не входить у 15 цифр)
    p.append(rect(40, y1, 150, 95, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(115, y1 + 25, "Префікс виходу", size=11.5, color=POS, bold=True))
    p.append(text(115, y1 + 45, "Міжнародний: «+»", size=10.5, color=INK))
    p.append(text(115, y1 + 65, "«00» (ЄС) / «011» (NANP)", size=9.5, color=MUTED))
    p.append(text(115, y1 + 82, "Національний: «0» / «1»", size=9.5, color=MUTED))

    # CC (Country Code)
    p.append(rect(205, y1, 190, 95, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(300, y1 + 25, "Код країни (CC)", size=12, color=NEG, bold=True))
    p.append(text(300, y1 + 45, "Country Code: 1–3 цифри", size=10.5, color=INK))
    p.append(text(300, y1 + 65, "«380» (Україна), «1» (США)", size=9.5, color=MUTED))
    p.append(text(300, y1 + 82, "«44» (Британія), «49» (ФРН)", size=9.5, color=MUTED))

    # NSN (National Significant Number)
    p.append(rect(410, y1, 410, 95, fill="#f0fdf4", stroke=GREEN, sw=1.8, rx=6))
    p.append(text(615, y1 + 25, "Національний значущий номер (NSN)", size=12, color=GREEN, bold=True))
    p.append(text(615, y1 + 45, "National Significant Number (до 14 цифр)", size=10.5, color=INK))
    p.append(text(615, y1 + 65, "Маршрутизується національним оператором зв'язку", size=9.5, color=MUTED))
    p.append(text(615, y1 + 82, "Географічні зони, мобільні мережі, спецслужби", size=9.5, color=MUTED))

    # Рівень 2: Розбивка NSN на NDC та SN
    y2 = 255
    # NDC
    p.append(rect(410, y2, 200, 95, fill="#f5f3ff", stroke=PURPLE, sw=1.5, rx=6))
    p.append(text(510, y2 + 25, "Код призначення (NDC)", size=11.5, color=PURPLE, bold=True))
    p.append(text(510, y2 + 45, "National Destination Code", size=10, color=INK))
    p.append(text(510, y2 + 65, "Зональний код: «44» (Київ)", size=9.5, color=MUTED))
    p.append(text(510, y2 + 82, "Код мережі: «67», «50» (моб.)", size=9.5, color=MUTED))

    # SN
    p.append(rect(620, y2, 200, 95, fill="#fffbeb", stroke=AMBER, sw=1.5, rx=6))
    p.append(text(720, y2 + 25, "Номер абонента (SN)", size=11.5, color=AMBER, bold=True))
    p.append(text(720, y2 + 45, "Subscriber Number", size=10, color=INK))
    p.append(text(720, y2 + 65, "Ідентифікатор лінії на станції", size=9.5, color=MUTED))
    p.append(text(720, y2 + 82, "Приклад: «123 45 67» (7 цифр)", size=9.5, color=MUTED))

    # З'єднувальні лінії
    p.append(arrow(300, 110, 300, y1, color=NEG, sw=1.5))
    p.append(arrow(615, 110, 615, y1, color=GREEN, sw=1.5))
    p.append(arrow(510, y1 + 95, 510, y2, color=PURPLE, sw=1.5))
    p.append(arrow(720, y1 + 95, 720, y2, color=AMBER, sw=1.5))

    # Приклад внизу
    p.append(rect(40, 365, 780, 35, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(430, 387, "Приклад: +380 (CC) 44 (NDC) 1234567 (SN) → Загальна довжина 12 цифр (<= 15 цифр E.164)",
                  size=11, color=INK, bold=True))

    render(os.path.join(IMG, "e164-structure.svg"), W, H, *p)


# ── 3. Трансляція виклику: SS7 ISUP <-> SIP VoIP через шлюз MGC/MG ─────────────
def fig_isup_sip_call_flow():
    W, H = 880, 520
    p = [text(W / 2, 26, "Взаємодія протоколів сигналізації: трансляція SS7 ISUP у SIP через шлюз VoIP", size=15, bold=True)]

    # Колонки сутностей
    cols = [
        (90, "Абонент PSTN", "Аналоговий телефон", LINE),
        (260, "Class 5 (SSP)", "Місцева станція PSTN", PURPLE),
        (460, "MGC / Softswitch", "Контролер шлюзу VoIP", CYAN),
        (640, "Media Gateway (MG)", "Перетворювач TDM/RTP", GREEN),
        (800, "SIP Клієнт", "IP-телефон / IMS", POS),
    ]

    for cx, title, sub, col in cols:
        p.append(rect(cx - 65, 50, 130, 48, fill="#ffffff", stroke=col, sw=1.8, rx=6))
        p.append(text(cx, 70, title, size=11.5, color=col, bold=True))
        p.append(text(cx, 88, sub, size=9.5, color=MUTED))
        p.append(line(cx, 98, cx, 475, color="#d1d5db", sw=1.2, dash="4,4"))

    # Покроковий потік сигналізації
    steps = [
        (120, 90, 260, "Зняття слухавки + DTMF", LINE, "right"),
        (160, 260, 460, "ISUP IAM (Initial Address Msg, CIC=12)", PURPLE, "right"),
        (195, 460, 800, "SIP INVITE (SDP: PCMA/8000)", CYAN, "right"),
        (230, 460, 640, "Megaco/H.248: Reserve TDM/RTP context", CYAN, "right"),
        (265, 800, 460, "SIP 180 Ringing", POS, "left"),
        (300, 460, 260, "ISUP ACM (Address Complete Msg)", PURPLE, "left"),
        (330, 260, 90, "КПВ (Сигнал контролю виклику)", LINE, "left"),
        (365, 800, 460, "SIP 200 OK (SDP Answer)", POS, "left"),
        (395, 460, 800, "SIP ACK", CYAN, "right"),
        (425, 460, 260, "ISUP ANM (Answer Msg / Старт тарифікації)", PURPLE, "left"),
    ]

    for y, x1, x2, label, col, direction in steps:
        if direction == "right":
            p.append(arrow(x1, y, x2, y, color=col, sw=1.6))
            p.append(text((x1 + x2) / 2, y - 6, label, size=9.5, color=col, bold=True))
        else:
            p.append(arrow(x1, y, x2, y, color=col, sw=1.6))
            p.append(text((x1 + x2) / 2, y - 6, label, size=9.5, color=col, bold=True))

    # Голосовий потік (Медіасесія RTP та TDM)
    p.append(rect(80, 445, 730, 32, fill="#ecfdf5", stroke=GREEN, sw=1.5, rx=4))
    p.append(text(445, 465, "Голосовий тракт: PSTN (64 кбіт/с DS0 G.711) <──TDM──> Media Gateway <──RTP/UDP──> SIP Телефон",
                  size=10.5, color=GREEN, bold=True))

    p.append(text(W / 2, H - 15, "Шлюз транслює стани ISUP у SIP: IAM -> INVITE, 180 Ringing -> ACM, 200 OK -> ANM.",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "isup-sip-call-flow.svg"), W, H, *p)


# ── 4. Трансляція номера E.164 в URI через ENUM (RFC 6116) ───────────────────
def fig_enum_dns_resolution():
    W, H = 860, 470
    p = [text(W / 2, 26, "Алгоритм трансляції телефонного номера E.164 в SIP URI через DNS ENUM", size=15, bold=True)]

    boxes = [
        ("Крок 1. Вхідний номер E.164",
         ["+380 44 123 4567", "(Номер у міжнародному форматі)"],
         POS, "#fef2f2", 50),
        ("Крок 2. Нормалізація та реверс цифр",
         ["1. Видалення символів крім цифр: 380441234567",
          "2. Реверс послідовності: 765432144083",
          "3. Розділення крапками та суфікс: 7.6.5.4.3.2.1.4.4.0.8.3.e164.arpa"],
         PURPLE, "#f5f3ff", 135),
        ("Крок 3. Запит до системи доменних імен (DNS NAPTR)",
         ["DNS Query: Type NAPTR для домену «7.6.5.4.3.2.1.4.4.0.8.3.e164.arpa»",
          "Відповідь DNS: Запис Naming Authority Pointer (RFC 3403 / RFC 6116):",
          "IN NAPTR 100 10 \"u\" \"E2U+sip\" \"!^.*$!sip:user@operator.ua!\" ."],
         CYAN, "#ecfeff", 235),
        ("Крок 4. Обчислення регулярного виразу та результат",
         ["Підстановка регулярного виразу до вхідного номера:",
          "Цільовий URI адресації VoIP: sip:user@operator.ua",
          "Маршрутизація SIP INVITE безпосередньо через IP-мережу"],
         GREEN, "#f0fdf4", 355),
    ]

    for title, lines, col, fill, y in boxes:
        h = 24 + len(lines) * 18 + 10
        p.append(rect(40, y, 780, h, fill=fill, stroke=col, sw=1.5, rx=6))
        p.append(text(60, y + 20, title, size=11.5, color=col, bold=True, anchor="start"))
        for j, ln in enumerate(lines):
            p.append(text(60, y + 40 + j * 18, ln, size=10, color=INK, anchor="start"))

    # Стрілки між кроками
    p.append(arrow(430, 118, 430, 133, color=LINE, sw=1.5))
    p.append(arrow(430, 218, 430, 233, color=LINE, sw=1.5))
    p.append(arrow(430, 338, 430, 353, color=LINE, sw=1.5))

    p.append(text(W / 2, H - 15, "ENUM перетворює телефонний номер на глобальне доменне ім'я для прямого з'єднання IP-до-IP.",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "enum-dns-resolution.svg"), W, H, *p)


if __name__ == "__main__":
    fig_pstn_hierarchy_ss7()
    fig_e164_structure()
    fig_isup_sip_call_flow()
    fig_enum_dns_resolution()
    print("Всі фігури згенеровано успішно.")
