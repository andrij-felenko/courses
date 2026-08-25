# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── Фігура 1: Периметр токенізації та межа PCI-DSS ───────────────────────────
def fig_tokenization_flow():
    W, H = 880, 520
    frags = []
    frags.append(text(W / 2, 30, "Периметр токенізації: чому бекенд не бачить сирих номерів карток", size=16, bold=True))
    frags.append(text(W / 2, 52, "сирі реквізити (PAN, CVV) ізольовані у захищеному iframe провайдера (SAQ A)",
                      size=12, color=MUTED, italic=True))

    # Зона клієнта (Браузер)
    frags.append(rect(30, 75, 250, 420, fill=BG, stroke=NEG, sw=1.8))
    frags.append(text(155, 100, "Клієнт (Браузер / Мобільний)", size=13, bold=True, color=NEG))
    frags.append(fitbox(45, 120, 220, 55, "Форма чекауту\n(Хост-сторінка магазину)", size=11, fill=FILL, stroke=MUTED))
    frags.append(fitbox(45, 195, 220, 85, "Hosted Fields (iframe PSP)\nВведення номера картки (PAN)\nі коду безпеки (CVV)", size=11, fill="#fdecea", stroke=POS, sw=1.6, bold=True, color=POS))
    frags.append(fitbox(45, 305, 220, 60, "Отримання токена\npm_1N4x9k... (без PAN)", size=11, fill="#eafaf1", stroke=FIELD, sw=1.4))
    frags.append(fitbox(45, 385, 220, 90, "Передача токена на бекенд\nразом із номером замовлення\n(POST /api/checkout)", size=11, fill=FILL, stroke=MUTED))

    # Зона Провайдера (PSP / Stripe / Adyen) — PCI Scope Level 1
    frags.append(rect(315, 75, 250, 420, fill="#fbfcfd", stroke=FIELD, sw=1.8))
    frags.append(text(440, 100, "Платіжний провайдер (PSP)", size=13, bold=True, color=FIELD))
    frags.append(fitbox(330, 120, 220, 45, "Сховище карток (PCI Vault)\nШифрування HSM / L1", size=11, fill="#eafaf1", stroke=FIELD))
    frags.append(fitbox(330, 205, 220, 65, "Генерація токена методу\nPAN → pm_1N4x9k...\n(Одноразовий / прив'язаний)", size=11, fill="#eafaf1", stroke=FIELD))
    frags.append(fitbox(330, 310, 220, 75, "Авторизація / Списання\nЗапит до МПС (Visa/Mastercard)\nта банку-емітента", size=11, fill="#eafaf1", stroke=FIELD))
    frags.append(fitbox(330, 410, 220, 65, "Формування результату\nі відправка вебхука\n(payment_intent.succeeded)", size=11, fill="#eafaf1", stroke=FIELD))

    # Зона Сервера торговця (Merchant Backend) — PCI Scope SAQ A
    frags.append(rect(600, 75, 250, 420, fill=BG, stroke=INK, sw=1.8))
    frags.append(text(725, 100, "Бекенд магазину", size=13, bold=True, color=INK))
    frags.append(fitbox(615, 120, 220, 60, "Межа безпеки:\nЖодних PAN / CVV у базі,\nпам'яті чи логах!", size=11, fill="#eafaf1", stroke=FIELD, bold=True, color=FIELD))
    frags.append(fitbox(615, 205, 220, 75, "Створення PaymentIntent\n(Сума, валюта, Idempotency-Key)\nPOST /v1/payment_intents", size=11, fill=FILL, stroke=INK))
    frags.append(fitbox(615, 305, 220, 80, "Підтвердження списання\nчерез API з секретним ключем\n(Secret Key sk_live_...)", size=11, fill=FILL, stroke=INK))
    frags.append(fitbox(615, 410, 220, 65, "Фіксація результату\nта виконання замовлення\nу внутрішній БД", size=11, fill=FILL, stroke=INK))

    # Стрілки взаємодії
    frags.append(arrow(265, 237, 330, 237, color=POS, sw=1.8))
    frags.append(arrow(330, 335, 265, 335, color=FIELD, sw=1.8))
    frags.append(arrow(265, 430, 615, 430, color=NEG, sw=1.8))
    frags.append(arrow(615, 242, 550, 242, color=INK, sw=1.8))
    frags.append(arrow(615, 345, 550, 345, color=INK, sw=1.8))

    render(os.path.join(IMG, "tokenization-flow.svg"), W, H, *frags)


# ── Фігура 2: Двофазний платіж — Авторизація проти Миттєвого списання ──────────
def fig_auth_capture_lifecycle():
    W, H = 880, 480
    frags = []
    frags.append(text(W / 2, 30, "Двофазний платіж: Авторизація (Hold) та Захоплення (Capture)", size=16, bold=True))
    frags.append(text(W / 2, 52, "чому пряме списання шкідливе в інтернет-торгівлі при відмові чи коригуванні замовлення",
                      size=12, color=MUTED, italic=True))

    # Верхня доріжка: Однофазне списання (Immediate Charge)
    frags.append(rect(40, 75, 800, 165, fill=BG, stroke=POS, sw=1.7))
    frags.append(text(170, 100, "Однофазне списання (Immediate Charge)", size=13, bold=True, color=POS))
    frags.append(fitbox(60, 120, 210, 50, "1. Списання $100\n(Гроші знято з балансу)", size=11, fill="#fdecea", stroke=POS))
    frags.append(fitbox(305, 120, 230, 50, "2. Товар закінчився на складі\n(Замовлення неможливо виконати)", size=11, fill=FILL, stroke=MUTED))
    frags.append(fitbox(570, 115, 250, 60, "3. Повне повернення (Refund)\n• Комісія шлюзу втрачена\n• Очікування клієнта 3–5 днів", size=11, fill="#fdecea", stroke=POS, bold=True, color=POS))
    frags.append(arrow(270, 145, 305, 145, color=POS, sw=1.6))
    frags.append(arrow(535, 145, 570, 145, color=POS, sw=1.6))
    frags.append(text(440, 215, "Ризик: фінансові втрати на interchange-комісіях та незадоволений клієнт", size=11, color=POS, italic=True))

    # Нижня доріжка: Двофазне списання (Authorize & Capture)
    frags.append(rect(40, 260, 800, 200, fill=BG, stroke=FIELD, sw=1.8))
    frags.append(text(170, 285, "Двофазне списання (Authorize & Capture)", size=13, bold=True, color=FIELD))
    frags.append(fitbox(60, 310, 210, 60, "1. Авторизація (Hold)\nБлокування ліміту на картці\n(Діє 7 днів, $0 комісій)", size=11, fill="#eafaf1", stroke=FIELD))

    # Розгалуження успіх / скасування
    frags.append(fitbox(310, 300, 240, 60, "2А. Товар відправлено покупцю\nВиклик Capture на $100\n(Остаточний кліринг коштів)", size=11, fill="#eafaf1", stroke=FIELD))
    frags.append(fitbox(585, 300, 235, 60, "Результат: Кошти списано\nТовар доставлено\nКомісія сплачена раз", size=11, fill="#eafaf1", stroke=FIELD, bold=True, color=FIELD))

    frags.append(fitbox(310, 385, 240, 60, "2Б. Відмова / Немає на складі\nВиклик Void (Скасування холду)\n(Миттєве зняття блоку)", size=11, fill="#eaf0fd", stroke=NEG))
    frags.append(fitbox(585, 385, 235, 60, "Результат: $0 комісій\nБаланс доступний миттєво\nНемає процедури Refund", size=11, fill="#eaf0fd", stroke=NEG, bold=True, color=NEG))

    frags.append(arrow(270, 340, 310, 330, color=FIELD, sw=1.6))
    frags.append(arrow(270, 340, 310, 415, color=NEG, sw=1.6))
    frags.append(arrow(550, 330, 585, 330, color=FIELD, sw=1.6))
    frags.append(arrow(550, 415, 585, 415, color=NEG, sw=1.6))

    render(os.path.join(IMG, "auth-capture-lifecycle.svg"), W, H, *frags)


# ── Фігура 3: Скінченний автомат станів платіжного наміру ─────────────────────
def fig_payment_state_machine():
    W, H = 880, 500
    frags = []
    frags.append(text(W / 2, 30, "Граф станів платіжного наміру (PaymentIntent Lifecycle)", size=16, bold=True))
    frags.append(text(W / 2, 52, "асинхронні переходи між токенізацією, 3D Secure 2 та клірингом",
                      size=12, color=MUTED, italic=True))

    # Стан 1: requires_payment_method
    frags.append(fitbox(30, 110, 200, 60, "requires_payment_method\nОчікування введення\nреквізитів покупцем", size=11, fill=FILL, stroke=INK))

    # Стан 2: requires_confirmation
    frags.append(fitbox(270, 110, 180, 60, "requires_confirmation\nМетод прив'язано,\nготовий до списання", size=11, fill=FILL, stroke=INK))

    # Стан 3: requires_action (3DS Challenge)
    frags.append(fitbox(490, 110, 170, 60, "requires_action\nВиклик 3D Secure 2\n(SCA / SMS-код / Банк)", size=11, fill="#eaf0fd", stroke=NEG, bold=True, color=NEG))

    # Стан 4: processing
    frags.append(fitbox(690, 110, 160, 60, "processing\nАсинхронна обробка\n(SEPA / ACH / Кліринг)", size=11, fill=FILL, stroke=INK))

    # Стан 5: requires_capture
    frags.append(fitbox(270, 260, 200, 60, "requires_capture\nУспішна авторизація\n(Холд коштів)", size=11, fill="#eafaf1", stroke=FIELD, bold=True, color=FIELD))

    # Фінальний стан успіху: succeeded
    frags.append(fitbox(570, 250, 250, 80, "succeeded\n✓ ПЛАТІЖ ЗАВЕРШЕНО\nКошти гарантовано зараховано\n(Товар відвантажується)", size=12, fill="#eafaf1", stroke=FIELD, sw=2.2, bold=True, color=FIELD))

    # Термінальні стани помилки / скасування
    frags.append(fitbox(150, 390, 240, 70, "canceled\n✗ Скасовано торговцем\n(Виклик Void або таймаут intent)", size=11, fill="#fdecea", stroke=POS, sw=1.6, bold=True, color=POS))
    frags.append(fitbox(500, 390, 250, 70, "failed (відмова)\n✗ Картку відхилено банком\n(Недостатньо коштів / Шахрайство)", size=11, fill="#fdecea", stroke=POS, sw=1.6, bold=True, color=POS))

    # Переходи (стрілки)
    frags.append(arrow(230, 140, 270, 140, color=INK, sw=1.6))
    frags.append(arrow(450, 140, 490, 140, color=NEG, sw=1.6))
    frags.append(arrow(660, 140, 690, 140, color=INK, sw=1.6))

    frags.append(arrow(360, 170, 360, 260, color=FIELD, sw=1.6))
    frags.append(arrow(575, 170, 380, 260, color=FIELD, sw=1.6))
    frags.append(arrow(770, 170, 720, 250, color=FIELD, sw=1.6))

    frags.append(arrow(470, 290, 570, 290, color=FIELD, sw=2.0))

    # До скасування / помилок
    frags.append(arrow(330, 320, 290, 390, color=POS, sw=1.6))
    frags.append(arrow(540, 170, 580, 390, color=POS, sw=1.6))
    frags.append(arrow(130, 170, 210, 390, color=POS, sw=1.6))

    render(os.path.join(IMG, "payment-state-machine.svg"), W, H, *frags)


# ── Фігура 4: Обробка вебхуків та фінансова звірка (Reconciliation) ───────────
def fig_webhook_reconciliation():
    W, H = 880, 500
    frags = []
    frags.append(text(W / 2, 30, "Обробка вебхуків та щоденна звірка (Reconciliation)", size=16, bold=True))
    frags.append(text(W / 2, 52, "гарантія узгодженості стану між платіжним шлюзом та внутрішньою головною книгою",
                      size=12, color=MUTED, italic=True))

    # Ліва колонка: Вхідний вебхук (Потокова обробка)
    frags.append(rect(40, 75, 380, 400, fill=BG, stroke=NEG, sw=1.8))
    frags.append(text(230, 100, "Потоковий обробник вебхуків", size=13, bold=True, color=NEG))
    frags.append(fitbox(55, 120, 350, 55, "1. Перевірка HMAC-SHA256 підпису\nStripe-Signature (timestamp + v1)\nЗахист від спуфінгу та replay", size=11, fill="#eaf0fd", stroke=NEG))
    frags.append(fitbox(55, 190, 350, 55, "2. Дедуплікація подій (Таблиця processed_events)\nПеревірка UNIQUE(event_id)\nІдемпотентний захист від повторів", size=11, fill=FILL, stroke=INK))
    frags.append(fitbox(55, 260, 350, 65, "3. Монотонний захист станів (State Guard)\nВідхилення застарілих подій,\nякщо локальний стан уже 'succeeded'", size=11, fill=FILL, stroke=INK))
    frags.append(fitbox(55, 340, 350, 65, "4. Подвійний бухгалтерський запис (Ledger)\nДебет: Розрахунковий рахунок шлюзу\nКредит: Дохід від реалізації замовлення", size=11, fill="#eafaf1", stroke=FIELD, bold=True, color=FIELD))
    frags.append(fitbox(55, 420, 350, 40, "5. Відповідь 200 OK провайдеру", size=11, fill=FILL, stroke=MUTED))

    # Права колонка: Фонова звірка (Batch Reconciliation)
    frags.append(rect(460, 75, 380, 400, fill=BG, stroke=FIELD, sw=1.8))
    frags.append(text(650, 100, "Фонова щоденна звірка (Reconciliation)", size=13, bold=True, color=FIELD))
    frags.append(fitbox(475, 120, 350, 60, "1. Завантаження балансового звіту PSP\n(Settlement Report / Payout API / CSV)\nУсі списання, повернення та комісії за добу", size=11, fill=FILL, stroke=INK))
    frags.append(fitbox(475, 195, 350, 65, "2. Посторінкове порівняння (Diff Engine)\nПорівняння PSP Charge ID з записами\nвнутрішньої бази транзакцій магазину", size=11, fill=FILL, stroke=INK))
    frags.append(fitbox(475, 275, 350, 75, "3. Виявлення розбіжностей (Discrepancies):\n• Втрачені вебхуки (charge є у PSP, нема в БД)\n• Несподівані чарджбеки (Disputes)\n• Відхилення валютної конвертації (FX slippage)", size=11, fill="#fdecea", stroke=POS, bold=True, color=POS))
    frags.append(fitbox(475, 365, 350, 95, "4. Автоматичне виправлення та алерт:\n• Допроведення відсутніх проводок у Ledger\n• Сповіщення фінансового відділу при суттєвих відхиленнях суми", size=11, fill="#eafaf1", stroke=FIELD, bold=True, color=FIELD))

    render(os.path.join(IMG, "webhook-reconciliation.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_tokenization_flow()
    fig_auth_capture_lifecycle()
    fig_payment_state_machine()
    fig_webhook_reconciliation()
    print("All figures generated successfully.")
