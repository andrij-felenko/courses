# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: Конфлікт нерозділених повноважень кількох станцій ───────────────
def fig_operator_roles_conflict():
    W, H = 840, 440
    frags = []
    frags.append(text(W / 2, 25, "Конфлікт нерозділених повноважень: прямий доступ без арбітражу",
                      size=15, bold=True))

    # Ліва колонка: Три незалежні станції у польовій мережі
    frags.append(rect(20, 50, 240, 370, fill="#f9fafb", stroke=MUTED, sw=1.5))
    frags.append(text(140, 75, "Польова мережа (Broadcast UDP)", size=12, bold=True, color=INK))

    # Пульт 1: Пілот
    frags.append(rect(35, 95, 210, 85, fill="#ffffff", stroke=POS, sw=1.5))
    frags.append(text(140, 115, "Пульт #1: Пілот (GCS ID: 255)", size=11, bold=True, color=POS))
    frags.append(text(140, 135, "Шле: MANUAL_CONTROL (50 Гц)", size=10, color=INK))
    frags.append(text(140, 155, "Тангаж: -15° (пікірування)", size=10, color=MUTED))
    frags.append(text(140, 170, "Газ: 80% (набір швидкості)", size=10, color=MUTED))

    # Пульт 2: Оператор корисного навантаження
    frags.append(rect(35, 195, 210, 85, fill="#ffffff", stroke=NEG, sw=1.5))
    frags.append(text(140, 215, "Пульт #2: Оператор камери (ID: 254)", size=11, bold=True, color=NEG))
    frags.append(text(140, 235, "Шле: SET_POSITION_TARGET (10 Гц)", size=10, color=INK))
    frags.append(text(140, 255, "Захоплення цілі: доворот направо", size=10, color=MUTED))
    frags.append(text(140, 270, "Тангаж: +5° (компенсація кута)", size=10, color=MUTED))

    # Пульт 3: Командир місії
    frags.append(rect(35, 295, 210, 110, fill="#ffffff", stroke="#d98324", sw=1.5))
    frags.append(text(140, 315, "Пульт #3: Командир (ID: 253)", size=11, bold=True, color="#d98324"))
    frags.append(text(140, 335, "Шле: COMMAND_LONG (RTL)", size=10, color=INK))
    frags.append(text(140, 355, "Аварійний сигнал: повернення", size=10, color=MUTED))
    frags.append(text(140, 375, "Режим: автопілот AUTO/RTL", size=10, color=MUTED))
    frags.append(text(140, 395, "Зміна висоти: +50 м", size=10, color=MUTED))

    # Стрілки передачі в ефір
    frags.append(arrow(245, 137, 330, 210, color=POS, sw=2.0))
    frags.append(arrow(245, 237, 330, 225, color=NEG, sw=2.0))
    frags.append(arrow(245, 350, 330, 240, color="#d98324", sw=2.0))

    # Центр: Спільний радіоканал без арбітражу
    frags.append(rect(335, 185, 140, 80, fill="#fdf3f2", stroke=POS, sw=1.8))
    frags.append(text(405, 215, "Колізія команд", size=12, bold=True, color=POS))
    frags.append(text(405, 235, "Мішанина пакетів", size=10, color=INK))
    frags.append(text(405, 252, "в одному радіомодемі", size=10, color=MUTED))

    frags.append(arrow(475, 225, 535, 225, color=POS, sw=2.0))

    # Права колонка: Автопілот і наслідки
    frags.append(rect(540, 50, 280, 370, fill="#fffaf9", stroke=POS, sw=1.8))
    frags.append(text(680, 75, "Бортовий контролер (FCU)", size=13, bold=True, color=POS))

    frags.append(fitbox(555, 95, 250, 85,
                        "Хаос керування:\nАвтопілот перемикається між ручним\nрежимом (Пілот) та автоматичним (Командир)\nдесятки разів на секунду!",
                        size=11, fill="#ffffff", stroke=POS, sw=1.2))

    frags.append(fitbox(555, 190, 250, 105,
                        "Фізичні наслідки:\n• Шалене тремтіння сервоприводів (50 Гц)\n• Стрибки струму двигунів до 120 А\n• Зрив повітряного потоку на елеронах\n• Втрата підйомної сили та зрив у штопор",
                        size=10, fill="#feebe8", stroke=POS, sw=1.4))

    frags.append(fitbox(555, 305, 250, 100,
                        "Висновок:\nОдин фізичний борт не може одночасно\nпідкорятися трьом незалежним пультам.\nПотрібен жорсткий бортовий арбітраж!",
                        size=10, fill="#ffffff", stroke=INK, sw=1.0))

    render(os.path.join(OUT, 'operator-roles-conflict.svg'), W, H, *frags)


# ── Фігура 2: Архітектура токена авторитету та розділення каналів ─────────────
def fig_authority_token_architecture():
    W, H = 840, 430
    frags = []
    frags.append(text(W / 2, 25, "Архітектура токена авторитету: розділення каналів керування",
                      size=15, bold=True))

    # 3 площини керування (Control Planes)
    y0 = 60
    # Площина 1: Пілотування (Flight Control Plane)
    frags.append(rect(20, y0, 250, 110, fill="#edf7ee", stroke=FIELD, sw=1.8))
    frags.append(text(145, y0 + 22, "1. Канал пілотування (Flight Plane)", size=11, bold=True, color=FIELD))
    frags.append(text(145, y0 + 42, "Ексклюзивний токен: AUTH_PILOT", size=10, bold=True, color=INK))
    frags.append(text(145, y0 + 62, "Штанга стіків, ручне кермо, тангаж/крен", size=9, color=MUTED))
    frags.append(text(145, y0 + 80, "Володар: Пульт #1 (Пілот, ID: 255)", size=10, bold=True, color=FIELD))
    frags.append(text(145, y0 + 98, "Частота: 50 Гц (жорсткий реалтайм)", size=9, color=MUTED))

    # Площина 2: Корисне навантаження (Payload Control Plane)
    frags.append(rect(20, y0 + 120, 250, 110, fill="#e8f0fe", stroke=NEG, sw=1.8))
    frags.append(text(145, y0 + 142, "2. Канал навантаження (Payload Plane)", size=11, bold=True, color=NEG))
    frags.append(text(145, y0 + 162, "Ексклюзивний токен: AUTH_PAYLOAD", size=10, bold=True, color=INK))
    frags.append(text(145, y0 + 182, "Керування камерою, лазером, скиданням", size=9, color=MUTED))
    frags.append(text(145, y0 + 200, "Володар: Пульт #2 (Оператор, ID: 254)", size=10, bold=True, color=NEG))
    frags.append(text(145, y0 + 218, "Не впливає на траєкторію польоту!", size=9, color=FIELD))

    # Площина 3: Спостереження та нагляд (Monitor Plane)
    frags.append(rect(20, y0 + 240, 250, 115, fill="#f4f6f8", stroke=MUTED, sw=1.5))
    frags.append(text(145, y0 + 262, "3. Канал нагляду (Monitor Plane)", size=11, bold=True, color=INK))
    frags.append(text(145, y0 + 282, "Режим: Тільки читання (Read-Only)", size=10, bold=True, color=MUTED))
    frags.append(text(145, y0 + 302, "Телеметрія, мапа, статус місії", size=9, color=MUTED))
    frags.append(text(145, y0 + 320, "Пульт #3 (Командир) + інші GCS", size=10, color=INK))
    frags.append(text(145, y0 + 338, "Право: Аварійне перехоплення (Override)", size=9, bold=True, color=POS))

    # Стрілки до бортового диспетчера
    frags.append(arrow(270, y0 + 55, 340, 180, color=FIELD, sw=2.0))
    frags.append(arrow(270, y0 + 175, 340, 210, color=NEG, sw=2.0))
    frags.append(arrow(270, y0 + 295, 340, 240, color=POS, sw=1.8))

    # Бортовий арбітр (Authority Arbiter)
    frags.append(rect(345, 55, 230, 360, fill="#ffffff", stroke=INK, sw=2.0))
    frags.append(text(460, 80, "Бортовий арбітр токенів", size=13, bold=True, color=INK))
    frags.append(text(460, 98, "(Onboard Authority Arbiter)", size=10, color=MUTED))

    frags.append(fitbox(360, 115, 200, 75,
                        "Таблиця активних токенів:\n• Pilot Token: GCS #255 (OK)\n• Payload Token: GCS #254 (OK)\n• Commander Lock: Неактивний",
                        size=10, fill="#fdf7e7", stroke="#d98324", sw=1.2))

    frags.append(fitbox(360, 200, 200, 95,
                        "Фільтр вхідних пакетів:\n1. Перевірка Source ID\n2. Звірка з правами токена\n3. Перевірка тахометра пінгу\n4. Відхилення несанкціонованих\nкоманд (DROP & NACK)",
                        size=9, fill="#f9fafb", stroke=MUTED, sw=1.0))

    frags.append(fitbox(360, 305, 200, 95,
                        "Таймери втрати зв'язку:\n• T_heartbeat(Pilot) = 1000 мс\n• Якщо прострочено → Failsafe\n• Можливість перехоплення\nіншою станцією",
                        size=9, fill="#edf7ee", stroke=FIELD, sw=1.2))

    # Стрілки до виконавчих підсистем
    frags.append(arrow(575, 140, 635, 120, color=FIELD, sw=2.0))
    frags.append(arrow(575, 220, 635, 220, color=NEG, sw=2.0))
    frags.append(arrow(575, 320, 635, 320, color=MUTED, sw=1.5))

    # Підсистеми апарата
    frags.append(rect(640, 65, 180, 95, fill="#edf7ee", stroke=FIELD, sw=1.5))
    frags.append(text(730, 90, "Польотний контролер", size=11, bold=True, color=FIELD))
    frags.append(text(730, 110, "Мікшер моторів, рулі", size=10, color=INK))
    frags.append(text(730, 130, "Приймає ЛИШЕ від Пульта #1", size=9, bold=True, color=FIELD))
    frags.append(text(730, 147, "Навігаційні вектори", size=9, color=MUTED))

    frags.append(rect(640, 175, 180, 95, fill="#e8f0fe", stroke=NEG, sw=1.5))
    frags.append(text(730, 200, "Підвіс і камера", size=11, bold=True, color=NEG))
    frags.append(text(730, 220, "Сервоприводи стабілізатора", size=10, color=INK))
    frags.append(text(730, 240, "Приймає ЛИШЕ від Пульта #2", size=9, bold=True, color=NEG))
    frags.append(text(730, 257, "Оптичний зум, сенсори", size=9, color=MUTED))

    frags.append(rect(640, 285, 180, 95, fill="#f4f6f8", stroke=MUTED, sw=1.5))
    frags.append(text(730, 310, "Транслятор телеметрії", size=11, bold=True, color=INK))
    frags.append(text(730, 330, "Шле стан усім станціям", size=10, color=MUTED))
    frags.append(text(730, 350, "Broadcast для моніторингу", size=9, color=MUTED))
    frags.append(text(730, 367, "1–10 Гц телеметрія", size=9, color=MUTED))

    render(os.path.join(OUT, 'authority-token-architecture.svg'), W, H, *frags)


# ── Фігура 3: Безпечна 4-фазна передача зміни (Shift Handover) ────────────────
def fig_shift_handover_sequence():
    W, H = 840, 450
    frags = []
    frags.append(text(W / 2, 25, "Безпечна 4-фазна процедура передачі зміни (Safe Shift Handover)",
                      size=15, bold=True))

    # Стовпчики 3 учасників
    x_gcs1 = 120
    x_fcu  = 420
    x_gcs2 = 720

    # Заголовки
    frags.append(rect(x_gcs1 - 90, 50, 180, 45, fill="#edf7ee", stroke=FIELD, sw=1.8))
    frags.append(text(x_gcs1, 68, "Пульт #1: Здавач", size=11, bold=True, color=FIELD))
    frags.append(text(x_gcs1, 84, "Поточний Master (ID: 255)", size=10, color=MUTED))

    frags.append(rect(x_fcu - 90, 50, 180, 45, fill="#fdf7e7", stroke="#d98324", sw=1.8))
    frags.append(text(x_fcu, 68, "Бортовий арбітр", size=11, bold=True, color="#d98324"))
    frags.append(text(x_fcu, 84, "Автопілот апарата", size=10, color=MUTED))

    frags.append(rect(x_gcs2 - 90, 50, 180, 45, fill="#e8f0fe", stroke=NEG, sw=1.8))
    frags.append(text(x_gcs2, 68, "Пульт #2: Приймач", size=11, bold=True, color=NEG))
    frags.append(text(x_gcs2, 84, "Змінний пілот (ID: 254)", size=10, color=MUTED))

    # Вертикальні лінії життя з розривами під плашки подій
    # GCS1 lifeline
    frags.append(line(x_gcs1, 95, x_gcs1, 430, color=MUTED, sw=1.5, dash="4,4"))

    # FCU lifeline з розривом під плашку атомарного світча (y: 305..355)
    frags.append(line(x_fcu,  95, x_fcu,  305, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(line(x_fcu, 355, x_fcu,  430, color=MUTED, sw=1.5, dash="4,4"))

    # GCS2 lifeline з розривом під плашку підгонки стіків (y: 210..275)
    frags.append(line(x_gcs2, 95, x_gcs2, 210, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(line(x_gcs2, 275, x_gcs2, 430, color=MUTED, sw=1.5, dash="4,4"))

    # Фаза 1: Ініціація передачі
    y = 120
    frags.append(rect(30, y - 12, 180, 24, fill="#edf7ee", stroke=FIELD, sw=1.0, rx=4))
    frags.append(text(120, y + 4, "1. Клік «Передати зміну»", size=10, bold=True, color=FIELD))

    frags.append(arrow(x_gcs1, y + 15, x_fcu, y + 15, color=FIELD, sw=1.8))
    frags.append(text(270, y + 8, "HANDOVER_REQUEST(Target: GCS #254)", size=10, bold=True, color=INK))

    frags.append(arrow(x_fcu, y + 35, x_gcs2, y + 35, color="#d98324", sw=1.8))
    frags.append(text(570, y + 28, "HANDOVER_OFFER(From: GCS #255)", size=10, bold=True, color=INK))

    # Фаза 2: Підтвердження готовності та перевірка стіків
    y = 195
    frags.append(rect(630, y - 12, 180, 24, fill="#e8f0fe", stroke=NEG, sw=1.0, rx=4))
    frags.append(text(720, y + 4, "2. Звірка стіків у нейтраль", size=10, bold=True, color=NEG))

    frags.append(fitbox(x_gcs2 - 100, y + 20, 200, 50,
                        "Інтерфейс показує цільові стіки:\n• Газ: вирівняти на 52%\n• Крен/Тангаж: у мертву зону (±3%)",
                        size=9, fill="#f4f6f8", stroke=NEG, sw=1.2))

    y = 285
    frags.append(arrow(x_gcs2, y, x_fcu, y, color=NEG, sw=1.8))
    frags.append(text(570, y - 8, "HANDOVER_ACCEPT(Sticks: Neutral/Matched)", size=10, bold=True, color=INK))

    # Фаза 3: Атомарне перемикання на борту
    y = 325
    frags.append(rect(x_fcu - 110, y - 18, 220, 45, fill="#fdf3f2", stroke=POS, sw=1.5))
    frags.append(text(x_fcu, y - 2, "3. АТОМАРНИЙ СВІТЧ ТОКЕНА", size=10, bold=True, color=POS))
    frags.append(text(x_fcu, y + 14, "Active Pilot = GCS #254 (0 мс стрибок)", size=9, color=INK))

    # Фаза 4: Сповіщення та фіксація статусу
    y = 390
    frags.append(arrow(x_fcu, y, x_gcs1, y, color=FIELD, sw=1.8))
    frags.append(text(270, y - 8, "HANDOVER_COMPLETED (Role: Read-Only)", size=10, bold=True, color=MUTED))

    frags.append(arrow(x_fcu, y + 20, x_gcs2, y + 20, color=NEG, sw=1.8))
    frags.append(text(570, y + 12, "HANDOVER_COMPLETED (Role: Active Master)", size=10, bold=True, color=FIELD))

    render(os.path.join(OUT, 'shift-handover-sequence.svg'), W, H, *frags)


# ── Фігура 4: Ієрархія пріоритетів та перехоплення командиром ──────────────────
def fig_commander_override_arbitration():
    W, H = 840, 420
    frags = []
    frags.append(text(W / 2, 25, "Ієрархія авторитету та аварійне перехоплення (Commander Override)",
                      size=15, bold=True))

    # Лівий блок: Драбина пріоритетів
    frags.append(rect(20, 50, 260, 350, fill="#f9fafb", stroke=MUTED, sw=1.5))
    frags.append(text(150, 75, "Ієрархія рівнів доступу", size=13, bold=True, color=INK))

    # Рівень 3: Командир (Суперкористувач)
    frags.append(rect(35, 95, 230, 75, fill="#fdf3f2", stroke=POS, sw=2.0))
    frags.append(text(150, 115, "Рівень 3: Командир місії", size=11, bold=True, color=POS))
    frags.append(text(150, 135, "Пріоритет: MAXIMUM (255)", size=10, bold=True, color=INK))
    frags.append(text(150, 153, "Право: Безумовне перехоплення", size=9, color=MUTED))

    # Рівень 2: Пілот (Оператор польоту)
    frags.append(rect(35, 180, 230, 75, fill="#edf7ee", stroke=FIELD, sw=1.8))
    frags.append(text(150, 200, "Рівень 2: Пілот апарата", size=11, bold=True, color=FIELD))
    frags.append(text(150, 220, "Пріоритет: HIGH (128)", size=10, bold=True, color=INK))
    frags.append(text(150, 238, "Право: Навігація, ручні стіки", size=9, color=MUTED))

    # Рівень 1: Оператор корисного навантаження / Спостерігач
    frags.append(rect(35, 265, 230, 75, fill="#e8f0fe", stroke=NEG, sw=1.8))
    frags.append(text(150, 285, "Рівень 1: Оператор / Сенсори", size=11, bold=True, color=NEG))
    frags.append(text(150, 305, "Пріоритет: NORMAL (64)", size=10, bold=True, color=INK))
    frags.append(text(150, 323, "Право: Камера, підвіс, телеметрія", size=9, color=MUTED))

    frags.append(text(150, 375, "Нижчий рівень НЕ може перебити вищий", size=9, bold=True, color=POS))

    # Стрілки арбітражу
    frags.append(arrow(280, 132, 340, 170, color=POS, sw=2.2))
    frags.append(arrow(280, 217, 340, 210, color=FIELD, sw=1.8))
    frags.append(arrow(280, 302, 340, 250, color=NEG, sw=1.8))

    # Правий блок: Логіка перехоплення та захисту
    frags.append(rect(345, 50, 475, 350, fill="#ffffff", stroke=INK, sw=2.0))
    frags.append(text(582, 75, "Бортовий автомат арбітражу перехоплення", size=13, bold=True, color=INK))

    frags.append(fitbox(360, 95, 445, 80,
                        "Сценарій 1: Штатна робота (Пілот керує)\n• Пілот (ID: 255) тримає токен польоту\n• Пульт шле Heartbeat кожні 200 мс\n• Командир і Сенсор працюють у своїх дозволених межах",
                        size=10, fill="#edf7ee", stroke=FIELD, sw=1.2))

    frags.append(fitbox(360, 185, 445, 95,
                        "Сценарій 2: Аварійне перехоплення (Commander Override)\n• Командир бачить перешкоду / неадекватні дії пілота\n• Тисне [ ПЕРЕХОПИТИ КЕРУВАННЯ ] з підписом MAVLink v2\n• Борт миттєво анулює токен Пілота (REVOKE) та скидає автопілот у LOITER/BRAKE\n• Токен польоту передається Командиру без очікування згоди Пілота!",
                        size=9.5, fill="#fdf3f2", stroke=POS, sw=1.5))

    frags.append(fitbox(360, 290, 445, 95,
                        "Сценарій 3: Втрата зв'язку з пілотом (Pilot Link Loss)\n• Якщо T_heartbeat(Pilot) > 1500 мс:\n  1. Борт блокує виконання старих стіків (Stale Control Lock)\n  2. Активується таймер аварійного очікування (3.0 с)\n  3. Якщо з'являється резервний пульт → дозволено швидке захоплення токена",
                        size=9.5, fill="#fdf7e7", stroke="#d98324", sw=1.2))

    render(os.path.join(OUT, 'commander-override-arbitration.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_operator_roles_conflict()
    fig_authority_token_architecture()
    fig_shift_handover_sequence()
    fig_commander_override_arbitration()
    print("Всі фігури згенеровано успішно.")
