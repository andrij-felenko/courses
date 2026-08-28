# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

BROWN = "#b07a35"
BROWN_FILL = "#fff8e6"


# ── Фігура 1: Анатомія «третьої зміни» ──────────────────────────────────────────
def fig_third_shift_anatomy():
    W, H = 840, 420
    frags = []
    frags.append(text(W / 2, 28, "Анатомія «третьої зміни»: як виникає неврахований клон",
                      size=15, bold=True))

    # Ліва колонка: Замовник (OEM)
    ox, oy, ow, oh = 30, 60, 190, 330
    frags.append(rect(ox, oy, ow, oh, fill="#f8fafc", stroke=INK, sw=1.6))
    frags.append(text(ox + ow / 2, oy + 26, "ЗАМОВНИК (OEM)", size=13, bold=True))
    frags.append(text(ox + ow / 2, oy + 46, "Власник розробки", size=10, color=MUTED))

    frags.append(rect(ox + 12, oy + 70, ow - 24, 76, fill="#ffffff", stroke=NEG, sw=1.3))
    frags.append(text(ox + ow / 2, oy + 92, "Пакет виробництва:", size=11, bold=True, color=NEG))
    frags.append(text(ox + ow / 2, oy + 112, "Gerber + BOM + прес-форми", size=10, color=INK))
    frags.append(text(ox + ow / 2, oy + 130, "Бінарник прошивки (.bin)", size=10, color=INK))

    frags.append(rect(ox + 12, oy + 160, ow - 24, 54, fill="#ffffff", stroke=FIELD, sw=1.3))
    frags.append(text(ox + ow / 2, oy + 182, "Замовлення партії:", size=11, bold=True, color=FIELD))
    frags.append(text(ox + ow / 2, oy + 200, "10 000 шт. (оплачено)", size=10, color=INK))

    frags.append(arrow(ox + ow, oy + 108, ox + ow + 38, oy + 108, color=INK, sw=1.8))
    frags.append(arrow(ox + ow, oy + 187, ox + ow + 38, oy + 187, color=INK, sw=1.8))

    # Центральна колонка: Завод контрактного виробництва (EMS)
    fx, fy, fw, fh = 260, 60, 310, 330
    frags.append(rect(fx, fy, fw, fh, fill="#f4f6f8", stroke=INK, sw=1.8))
    frags.append(text(fx + fw / 2, fy + 26, "КОНТРАКТНИЙ ЗАВОД (EMS)", size=13, bold=True))
    frags.append(text(fx + fw / 2, fy + 46, "Лінії SMT, монтаж, тест-джиг", size=10, color=MUTED))

    # Зміна 1 і 2 (Легальні)
    frags.append(rect(fx + 12, fy + 64, fw - 24, 106, fill="#eaf4ec", stroke=FIELD, sw=1.4))
    frags.append(text(fx + 24, fy + 86, "Зміни 1 і 2 (08:00 – 24:00)", size=12, bold=True, color=FIELD, anchor="start"))
    frags.append(text(fx + 24, fy + 106, "• Офіційне складання за контрактом", size=10, color=INK, anchor="start"))
    frags.append(text(fx + 24, fy + 124, "• Оригінальний BOM, штатний ВТК", size=10, color=INK, anchor="start"))
    frags.append(text(fx + 24, fy + 142, "• Випуск: 10 000 авторизованих плат", size=10, bold=True, color=FIELD, anchor="start"))

    # Зміна 3 (Нічна «третя зміна»)
    frags.append(rect(fx + 12, fy + 184, fw - 24, 126, fill="#fdecea", stroke=POS, sw=1.6))
    frags.append(text(fx + 24, fy + 206, "«Третя зміна» (00:00 – 08:00)", size=12, bold=True, color=POS, anchor="start"))
    frags.append(text(fx + 24, fy + 226, "• Ті самі лінії SMT і прес-форми корпусу", size=10, color=INK, anchor="start"))
    frags.append(text(fx + 24, fy + 244, "• Той самий бінарник прошивки (.bin)", size=10, color=INK, anchor="start"))
    frags.append(text(fx + 24, fy + 262, "• Зайві компоненти або дешеві аналоги", size=10, color=INK, anchor="start"))
    frags.append(text(fx + 24, fy + 282, "• Випуск: +5 000 неврахованих копій", size=10, bold=True, color=POS, anchor="start"))

    frags.append(arrow(fx + fw, fy + 117, fx + fw + 38, fy + 117, color=FIELD, sw=1.8))
    frags.append(arrow(fx + fw, fy + 247, fx + fw + 38, fy + 247, color=POS, sw=1.8))

    # Права колонка: Наслідки на ринку
    rx, ry, rw, rh = 610, 60, 200, 330
    frags.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke=INK, sw=1.6))
    frags.append(text(rx + rw / 2, ry + 26, "РИНОК ТА СЕРВІС", size=13, bold=True))

    frags.append(rect(rx + 10, ry + 64, rw - 20, 106, fill="#f0faf2", stroke=FIELD, sw=1.3))
    frags.append(text(rx + rw / 2, ry + 88, "Офіційний склад:", size=11, bold=True, color=FIELD))
    frags.append(text(rx + rw / 2, ry + 108, "10 000 виробів", size=10, color=INK))
    frags.append(text(rx + rw / 2, ry + 126, "Повна ціна з R&D", size=10, color=INK))
    frags.append(text(rx + rw / 2, ry + 144, "Офіційна гарантія", size=10, color=FIELD))

    frags.append(rect(rx + 10, ry + 184, rw - 20, 126, fill="#fff2f2", stroke=POS, sw=1.4))
    frags.append(text(rx + rw / 2, ry + 208, "Сірий ринок / Клони:", size=11, bold=True, color=POS))
    frags.append(text(rx + rw / 2, ry + 228, "5 000 примарних копій", size=10, bold=True, color=POS))
    frags.append(text(rx + rw / 2, ry + 248, "Демпінг ціни на 40–50%", size=10, color=INK))
    frags.append(text(rx + rw / 2, ry + 266, "Збитки, фейковий сервіс", size=10, color=POS))
    frags.append(text(rx + rw / 2, ry + 284, "і навантаження на хмару", size=10, color=POS))

    render(os.path.join(OUT, 'third-shift-anatomy.svg'), W, H, *frags)


# ── Фігура 2: Криптографічний контроль квот ──────────────────────────────────
def fig_key_quota_architecture():
    W, H = 840, 390
    frags = []
    frags.append(text(W / 2, 26, "Криптографічний контроль випуску: від квоти замовника до активації",
                      size=15, bold=True))

    # 1. Сервер OEM (Центр сертифікації)
    b1_x, b1_y, b1_w, b1_h = 24, 60, 230, 280
    frags.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#eef2f7", stroke=INK, sw=1.6))
    frags.append(text(b1_x + b1_w / 2, b1_y + 24, "СЕРВЕР OEM (ROOT CA)", size=12, bold=True))
    frags.append(text(b1_x + b1_w / 2, b1_y + 42, "Власник кореневого ключа", size=10, color=MUTED))

    frags.append(rect(b1_x + 10, b1_y + 60, b1_w - 20, 110, fill="#ffffff", stroke=NEG, sw=1.3))
    frags.append(text(b1_x + b1_w / 2, b1_y + 80, "Виробничий квиток (Ticket):", size=10, bold=True, color=NEG))
    frags.append(text(b1_x + 18, b1_y + 100, "• Batch ID: #B-2026-08", size=10, color=INK, anchor="start"))
    frags.append(text(b1_x + 18, b1_y + 118, "• Ліміт квоти: N = 10 200", size=10, bold=True, color=FIELD, anchor="start"))
    frags.append(text(b1_x + 18, b1_y + 136, "• Термін: 2026-09-01", size=10, color=INK, anchor="start"))
    frags.append(text(b1_x + 18, b1_y + 154, "• Підпис: Sign_OEM(Data)", size=10, color=POS, anchor="start"))

    frags.append(rect(b1_x + 10, b1_y + 184, b1_w - 20, 72, fill="#ffffff", stroke=FIELD, sw=1.3))
    frags.append(text(b1_x + b1_w / 2, b1_y + 204, "Реєстр активацій (Ledger):", size=10, bold=True, color=FIELD))
    frags.append(text(b1_x + b1_w / 2, b1_y + 224, "База дозволених серійників", size=10, color=INK))
    frags.append(text(b1_x + b1_w / 2, b1_y + 242, "та відбитків сертифікатів", size=10, color=MUTED))

    # Стрілка 1 -> 2: Передача квитка
    frags.append(arrow(b1_x + b1_w, b1_y + 115, b1_x + b1_w + 38, b1_y + 115, color=NEG, sw=1.8))
    frags.append(text(b1_x + b1_w + 19, b1_y + 104, "Квиток", size=10, color=NEG, bold=True))

    # 2. Захищений модуль на заводі (HSM / Secure Fixture)
    b2_x, b2_y, b2_w, b2_h = 294, 60, 252, 280
    frags.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#fff9eb", stroke=BROWN, sw=1.8))
    frags.append(text(b2_x + b2_w / 2, b2_y + 24, "ЗАВОДСЬКИЙ HSM / ДЖИГ", size=12, bold=True, color=BROWN))
    frags.append(text(b2_x + b2_w / 2, b2_y + 42, "Апаратний контроль квоти", size=10, color=MUTED))

    frags.append(rect(b2_x + 10, b2_y + 60, b2_w - 20, 84, fill="#ffffff", stroke=POS, sw=1.4))
    frags.append(text(b2_x + b2_w / 2, b2_y + 80, "Монотонний лічильник:", size=11, bold=True, color=POS))
    frags.append(text(b2_x + b2_w / 2, b2_y + 102, "Залишок = Counter − 1", size=11, bold=True, color=INK))
    frags.append(text(b2_x + b2_w / 2, b2_y + 124, "При Counter = 0 → БЛОКУВАННЯ", size=10, bold=True, color=POS))

    frags.append(rect(b2_x + 10, b2_y + 156, b2_w - 20, 100, fill="#ffffff", stroke=INK, sw=1.3))
    frags.append(text(b2_x + b2_w / 2, b2_y + 176, "Операція на один виріб:", size=10, bold=True))
    frags.append(text(b2_x + 16, b2_y + 196, "1. Зчитати UID чипа й PubKey", size=10, color=INK, anchor="start"))
    frags.append(text(b2_x + 16, b2_y + 214, "2. Списати 1 одиницю квоти", size=10, color=POS, anchor="start"))
    frags.append(text(b2_x + 16, b2_y + 232, "3. Підписати сертифікат пристрою", size=10, color=FIELD, anchor="start"))

    # Стрілка 2 -> 3: Прошивання плати
    frags.append(arrow(b2_x + b2_w, b2_y + 115, b2_x + b2_w + 38, b2_y + 115, color=FIELD, sw=1.8))
    frags.append(text(b2_x + b2_w + 19, b2_y + 104, "Cert + Key", size=10, color=FIELD, bold=True))

    # Стрілка 2 -> 1: Звіт аудиту (внизу)
    frags.append(arrow(b2_x, b1_y + 220, b1_x + b1_w + 6, b1_y + 220, color=MUTED, sw=1.5))
    frags.append(text((b1_x + b1_w + b2_x) / 2, b1_y + 210, "Звіт аудиту (Log)", size=9, color=MUTED))

    # 3. Виріб на конвеєрі (DUT)
    b3_x, b3_y, b3_w, b3_h = 586, 60, 230, 280
    frags.append(rect(b3_x, b3_y, b3_w, b3_h, fill="#f0faf2", stroke=FIELD, sw=1.6))
    frags.append(text(b3_x + b3_w / 2, b3_y + 24, "ГОТОВИЙ ПРИСТРІЙ (DUT)", size=12, bold=True, color=FIELD))
    frags.append(text(b3_x + b3_w / 2, b3_y + 42, "Авторизований екземпляр", size=10, color=MUTED))

    frags.append(rect(b3_x + 10, b3_y + 60, b3_w - 20, 84, fill="#ffffff", stroke=FIELD, sw=1.3))
    frags.append(text(b3_x + b3_w / 2, b3_y + 80, "Апаратний сейф чипа:", size=10, bold=True, color=FIELD))
    frags.append(text(b3_x + 18, b3_y + 100, "• Приватний ключ (eFuse / SE)", size=10, color=INK, anchor="start"))
    frags.append(text(b3_x + 18, b3_y + 118, "• Підписаний сертифікат", size=10, color=INK, anchor="start"))
    frags.append(text(b3_x + 18, b3_y + 136, "• Пропалені eFuse захисту", size=10, color=POS, anchor="start"))

    frags.append(rect(b3_x + 10, b3_y + 156, b3_w - 20, 100, fill="#ffffff", stroke=NEG, sw=1.3))
    frags.append(text(b3_x + b3_w / 2, b3_y + 176, "Перший вихід у хмару (mTLS):", size=10, bold=True, color=NEG))
    frags.append(text(b3_x + b3_w / 2, b3_y + 198, "Доказ володіння ключем", size=10, color=INK))
    frags.append(text(b3_x + b3_w / 2, b3_y + 216, "Звірка з реєстром Ledger", size=10, color=INK))
    frags.append(text(b3_x + b3_w / 2, b3_y + 236, "Клон без квитка = ВІДХИЛЕНО", size=10, bold=True, color=POS))

    # Нижня підсумкова плашка
    frags.append(fitbox(24, H - 36, W - 48, 26,
                        "Без підписаного квитка HSM не видасть сертифікат; без сертифіката пристрій не пустять у хмару.",
                        size=11, fill="#f4f6f8", stroke=INK, sw=1.2))

    render(os.path.join(OUT, 'key-quota-architecture.svg'), W, H, *frags)


# ── Фігура 3: Взаємодія всередині захищеного тест-джига ─────────────────────────
def fig_hsm_fixture_workflow():
    W, H = 820, 400
    frags = []
    frags.append(text(W / 2, 26, "Взаємодія всередині захищеного тест-джига: протокол провізіонування",
                      size=15, bold=True))

    # Ліва вісь: Стенд/HSM, Права вісь: Мікроконтролер (DUT)
    hsm_x = 180
    dut_x = 640
    y_top = 65
    y_bot = 350

    frags.append(rect(hsm_x - 90, y_top - 18, 180, 32, fill="#fff9eb", stroke=BROWN, sw=1.6))
    frags.append(text(hsm_x, y_top + 3, "ЗАВОДСЬКИЙ HSM / СТАНЦІЯ", size=11, bold=True, color=BROWN))

    frags.append(rect(dut_x - 90, y_top - 18, 180, 32, fill="#eaf4ec", stroke=FIELD, sw=1.6))
    frags.append(text(dut_x, y_top + 3, "ПЛАТА НА ГОЛКАХ (DUT)", size=11, bold=True, color=FIELD))

    frags.append(line(hsm_x, y_top + 14, hsm_x, y_bot, color=MUTED, sw=1.4, dash="4,4"))
    frags.append(line(dut_x, y_top + 14, dut_x, y_bot, color=MUTED, sw=1.4, dash="4,4"))

    # Крок 1: Опускання голок і старт
    y1 = 110
    frags.append(arrow(hsm_x, y1, dut_x, y1, color=INK, sw=1.5))
    frags.append(text((hsm_x + dut_x) / 2, y1 - 8, "1. Подача живлення, скидання та старт завантажувача", size=10, color=INK))

    # Крок 2: Генерація ключів на чипі
    y2 = 150
    frags.append(rect(dut_x + 10, y2 - 14, 155, 30, fill="#ffffff", stroke=FIELD, sw=1.2))
    frags.append(text(dut_x + 87, y2 + 5, "DUT TRNG: пара (Priv, Pub)", size=9, bold=True, color=FIELD))
    frags.append(arrow(dut_x, y2 + 10, hsm_x, y2 + 10, color=NEG, sw=1.5))
    frags.append(text((hsm_x + dut_x) / 2, y2 + 2, "2. Відповідь: Silicon_UID + Device_PubKey", size=10, color=NEG))

    # Крок 3: Перевірка лічильника й списання квоти в HSM
    y3 = 205
    frags.append(rect(hsm_x - 165, y3 - 16, 155, 36, fill="#ffffff", stroke=POS, sw=1.4))
    frags.append(text(hsm_x - 87, y3 - 2, "HSM: Counter > 0 ?", size=10, bold=True, color=POS))
    frags.append(text(hsm_x - 87, y3 + 12, "Counter = Counter − 1", size=9, color=INK))

    frags.append(arrow(hsm_x, y3 + 10, dut_x, y3 + 10, color=FIELD, sw=1.5))
    frags.append(text((hsm_x + dut_x) / 2, y3 + 2, "3. Запис підписаного сертифіката (Cert) у Flash/NVS", size=10, color=FIELD))

    # Крок 4: Фіксація та пропалювання eFuse
    y4 = 265
    frags.append(rect(dut_x + 10, y4 - 16, 155, 36, fill="#ffffff", stroke=POS, sw=1.4))
    frags.append(text(dut_x + 87, y4 - 2, "Пропалювання eFuse:", size=10, bold=True, color=POS))
    frags.append(text(dut_x + 87, y4 + 12, "Lock JTAG, Secure Boot = ON", size=9, color=INK))

    frags.append(arrow(dut_x, y4 + 10, hsm_x, y4 + 10, color=INK, sw=1.5))
    frags.append(text((hsm_x + dut_x) / 2, y4 + 2, "4. Статус: eFuse спалено, захист замкнено", size=10, color=INK))

    # Крок 5: Запис аудиту
    y5 = 320
    frags.append(rect(hsm_x - 165, y5 - 14, 155, 30, fill="#ffffff", stroke=INK, sw=1.2))
    frags.append(text(hsm_x - 87, y5 + 5, "HSM: Log(UID, Cert, TS)", size=9, bold=True, color=INK))
    frags.append(arrow(hsm_x, y5 + 5, (hsm_x + dut_x) / 2, y5 + 5, color=MUTED, sw=1.4))
    frags.append(text((hsm_x + dut_x) / 2 + 10, y5 + 10, "5. Джиг розмикає голки; плата готова", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'hsm-fixture-workflow.svg'), W, H, *frags)


if __name__ == "__main__":
    fig_third_shift_anatomy()
    fig_key_quota_architecture()
    fig_hsm_fixture_workflow()
    print("Figures generated successfully.")
