# -*- coding: utf-8 -*-
"""Фігури до теми «Оркестрація проти хореографії: хто веде багатокроковий процес»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # збій / небезпека / компенсація
COOL = "#eaf0fd"   # оркестратор / координатор
GOOD = "#e8f6ee"   # успіх / прямий крок
ACCENT = "#fbf4db" # брокер / проміжний стан / шина подій


# ── 1. Порівняння архітектурних топологій: Оркестрація проти Хореографії ──
def fig_orchestration_vs_choreography_flow():
    W, H = 1200, 680
    f = []

    # Фонова панель ліворуч: Оркестрація
    f.append(rect(30, 40, 550, 600, fill="#fcfdfe", stroke=MUTED, sw=1.5, rx=8))
    f.append(rect(30, 40, 550, 44, fill=COOL, stroke=MUTED, sw=1.5, rx=8))
    f.append(text(305, 68, "Оркестрація: Централізований потік керування", size=14.5, color=INK, bold=True))

    # Центральний оркестратор
    f.append(fitbox(205, 115, 200, 70, "Оркестратор процесу\n(Workflow Engine / Saga)", size=13, bold=True, fill=COOL, stroke=NEG, sw=2.0))

    # Воркери / Сервіси ліворуч
    f.append(fitbox(55, 270, 145, 60, "Складський сервіс\n(Inventory)", size=12, bold=True, fill=FILL, stroke=LINE, sw=1.5))
    f.append(fitbox(235, 270, 140, 60, "Платіжний шлюз\n(Payments)", size=12, bold=True, fill=FILL, stroke=LINE, sw=1.5))
    f.append(fitbox(410, 270, 145, 60, "Служба доставки\n(Logistics)", size=12, bold=True, fill=FILL, stroke=LINE, sw=1.5))

    # Двосторонні стрілки команд та відповідей
    # До складу
    f.append(arrow(220, 185, 115, 270, color=NEG, sw=1.8))
    f.append(arrow(140, 270, 245, 185, color=MUTED, sw=1.4))
    f.append(text(130, 210, "1. Команда", size=11, color=NEG, bold=True, anchor="end"))
    f.append(text(215, 245, "Відповідь", size=10.5, color=MUTED, anchor="start"))

    # До платежів
    f.append(arrow(295, 185, 295, 270, color=NEG, sw=1.8))
    f.append(arrow(315, 270, 315, 185, color=MUTED, sw=1.4))
    f.append(text(285, 230, "2. Команда", size=11, color=NEG, bold=True, anchor="end"))
    f.append(text(325, 230, "Відповідь", size=10.5, color=MUTED, anchor="start"))

    # До доставки
    f.append(arrow(370, 185, 470, 270, color=NEG, sw=1.8))
    f.append(arrow(495, 270, 395, 185, color=MUTED, sw=1.4))
    f.append(text(480, 210, "3. Команда", size=11, color=NEG, bold=True, anchor="start"))
    f.append(text(395, 245, "Відповідь", size=10.5, color=MUTED, anchor="end"))

    # Пояснювальний блок властивостей оркестрації
    f.append(fitbox(50, 370, 510, 245,
                    "Ключові властивості оркестрації:\n"
                    "• Координатор явно знає повний граф та стан процесу\n"
                    "• Команди надсилаються адресно конкретним виконавцям\n"
                    "• Централізований журнал виконання (Audit Trail)\n"
                    "• Відмовостійкість: перезапуск та відкат координує рушій\n"
                    "• Сервіси не знають про існування один одного",
                    size=12, bold=False, fill=GOOD, stroke=FIELD, sw=1.5))

    # Фонова панель праворуч: Хореографія
    f.append(rect(620, 40, 550, 600, fill="#fcfdfe", stroke=MUTED, sw=1.5, rx=8))
    f.append(rect(620, 40, 550, 44, fill=ACCENT, stroke=MUTED, sw=1.5, rx=8))
    f.append(text(895, 68, "Хореографія: Децентралізований реактивний ланцюг", size=14.5, color=INK, bold=True))

    # Брокер подій посередині
    f.append(fitbox(645, 220, 500, 60, "Шина доменних подій (Event Bus / Kafka Topics)", size=13.5, bold=True, fill=ACCENT, stroke=INK, sw=2.0))

    # Автономні сервіси праворуч
    f.append(fitbox(645, 115, 140, 60, "Замовлення\n(Orders)", size=12, bold=True, fill=FILL, stroke=LINE, sw=1.5))
    f.append(fitbox(825, 115, 140, 60, "Склад\n(Inventory)", size=12, bold=True, fill=FILL, stroke=LINE, sw=1.5))
    f.append(fitbox(1005, 115, 140, 60, "Оплата\n(Payments)", size=12, bold=True, fill=FILL, stroke=LINE, sw=1.5))

    # Стрілки публікації та підписки
    # Замовлення публікує OrderCreated
    f.append(arrow(690, 175, 690, 220, color=FIELD, sw=1.8))
    f.append(text(640, 198, "OrderCreated", size=10.5, color=FIELD, bold=True, anchor="start"))

    # Склад споживає OrderCreated, публікує StockReserved
    f.append(arrow(850, 220, 850, 175, color=MUTED, sw=1.4))
    f.append(arrow(900, 175, 900, 220, color=FIELD, sw=1.8))
    f.append(text(910, 198, "StockReserved", size=10.5, color=FIELD, bold=True, anchor="start"))

    # Оплата споживає StockReserved, публікує PaymentCaptured
    f.append(arrow(1050, 220, 1050, 175, color=MUTED, sw=1.4))
    f.append(arrow(1090, 175, 1090, 220, color=FIELD, sw=1.8))

    # Сервіс доставки внизу
    f.append(fitbox(825, 315, 140, 55, "Доставка\n(Logistics)", size=12, bold=True, fill=FILL, stroke=LINE, sw=1.5))
    f.append(arrow(895, 280, 895, 315, color=MUTED, sw=1.4))
    f.append(text(1095, 255, "PaymentCaptured", size=10.5, color=FIELD, bold=True, anchor="end"))

    # Пояснювальний блок властивостей хореографії
    f.append(fitbox(640, 395, 510, 220,
                    "Ключові властивості хореографії:\n"
                    "• Немає єдиного центру керування чи точки відмови\n"
                    "• Сервіси публікують факти (події) про зміни стану\n"
                    "• Повна часова автономія та слабке зв'язування\n"
                    "• Загальний бізнес-процес розмазаний між кодом обробників\n"
                    "• Відкат вимагає узгодженого ланцюга компенсаційних подій",
                    size=12, bold=False, fill=GOOD, stroke=FIELD, sw=1.5))

    render(os.path.join(OUT, 'orchestration-vs-choreography-flow.svg'), W, H, *f)


# ── 2. Проблема відкату в хореографії: Каскад компенсацій та стани перегонів ──
def fig_choreography_compensation_chaos():
    W, H = 1200, 680
    f = []

    # Заголовок зверху
    f.append(fitbox(50, 30, 1100, 45, "Каскадний колапс компенсацій у реактивній хореографії", size=15, bold=True, fill=WARM, stroke=POS, sw=2.0))

    # Прямий хід подій (Зелена гілка зліва направо)
    f.append(rect(50, 100, 1100, 140, fill="#f9fdfa", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(150, 125, "ПРЯМИЙ ХІД (Успішні кроки 1 і 2)", size=13, color=FIELD, bold=True))

    f.append(fitbox(80, 145, 200, 70, "1. Склад (Inventory)\nЗарезервовано товар", size=12, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))
    f.append(arrow(280, 180, 430, 180, color=FIELD, sw=2.0))
    f.append(text(355, 170, "StockReserved", size=11, color=FIELD, bold=True))

    f.append(fitbox(430, 145, 200, 70, "2. Оплата (Payments)\nСписано 45 000 грн", size=12, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))
    f.append(arrow(630, 180, 780, 180, color=FIELD, sw=2.0))
    f.append(text(705, 170, "PaymentCaptured", size=11, color=FIELD, bold=True))

    # Точка аварії: Доставка
    f.append(fitbox(780, 145, 230, 70, "3. Доставка (Logistics)\nАВАРІЯ: Немає вільних кур'єрів", size=12, bold=True, fill=WARM, stroke=POS, sw=2.0))

    # Зворотний компенсаційний потік (Червона гілка справа наліво)
    f.append(rect(50, 270, 1100, 180, fill="#fef8f8", stroke=POS, sw=1.5, rx=6))
    f.append(text(210, 295, "ЗВОРОТНИЙ ХІД (Розмазані компенсаційні події)", size=13, color=POS, bold=True))

    # Подія збою
    f.append(arrow(895, 215, 895, 330, color=POS, sw=2.0))
    f.append(text(905, 280, "DeliveryFailedEvent", size=11, color=POS, bold=True, anchor="start"))

    # Обробка повернення оплати
    f.append(fitbox(740, 330, 220, 70, "Платіжний сервіс\nСлухає: DeliveryFailed\nВиконує: Refund 45 000 грн", size=11.5, bold=True, fill=WARM, stroke=POS, sw=1.5))

    # Публікація PaymentRefunded
    f.append(arrow(740, 365, 580, 365, color=POS, sw=2.0))
    f.append(text(660, 350, "PaymentRefunded", size=11, color=POS, bold=True))

    # Обробка розблокування складу
    f.append(fitbox(360, 330, 220, 70, "Складський сервіс\nСлухає: PaymentRefunded\nВиконує: ReleaseStock", size=11.5, bold=True, fill=WARM, stroke=POS, sw=1.5))

    # Публікація StockReleased
    f.append(arrow(360, 365, 220, 365, color=POS, sw=2.0))
    f.append(text(290, 350, "StockReleased", size=11, color=POS, bold=True))

    # Фінал: Скасування замовлення
    f.append(fitbox(80, 330, 140, 70, "Сервіс замовлень\nСтатус: CANCELLED", size=11.5, bold=True, fill=FILL, stroke=LINE, sw=1.5))

    # Пастки та дефекти хореографії внизу
    f.append(fitbox(50, 480, 340, 160,
                    "1. Стан перегонів компенсації:\n"
                    "Якщо DeliveryFailed надійде до\n"
                    "завершення PaymentCaptured, платіж\n"
                    "не знайде що повертати, а потім\n"
                    "спише гроші назавжди (фантомне списання)",
                    size=11.5, bold=False, fill=WARM, stroke=POS, sw=1.5))

    f.append(fitbox(430, 480, 340, 160,
                    "2. Непомітне зависання (Silent Stall):\n"
                    "Якщо платіжний сервіс впаде і не\n"
                    "опублікує PaymentRefunded, склад ніколи\n"
                    "не дізнається про потребу розблокувати\n"
                    "товар. Немає таймера-супервізора.",
                    size=11.5, bold=False, fill=WARM, stroke=POS, sw=1.5))

    f.append(fitbox(810, 480, 340, 160,
                    "3. Комбінаторний вибух топіків:\n"
                    "Кожен сервіс має знати всі варіанти\n"
                    "подій збою від усіх наступних сервісів.\n"
                    "Зв'язність за схемами подій зростає\n"
                    "квадратично: N сервісів → N*(N-1) зв'язків.",
                    size=11.5, bold=False, fill=WARM, stroke=POS, sw=1.5))

    render(os.path.join(OUT, 'choreography-compensation-chaos.svg'), W, H, *f)


# ── 3. Автомат станів оркестратора та LIFO стек компенсацій ──
def fig_orchestrator_state_machine_rollback():
    W, H = 1200, 680
    f = []

    # Ліва половина: Хронологія виконання кроків та стека
    f.append(rect(40, 30, 620, 620, fill="#fcfdfe", stroke=MUTED, sw=1.5, rx=8))
    f.append(rect(40, 30, 620, 44, fill=COOL, stroke=MUTED, sw=1.5, rx=8))
    f.append(text(350, 58, "Оркестратор: Керування прямим ходом та стеком LIFO", size=14, color=INK, bold=True))

    # Крок 1: Успіх
    f.append(fitbox(60, 100, 260, 60, "Крок 1: ReserveInventory\nСтатус: ВИКОНАНО", size=12, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))
    f.append(arrow(320, 130, 420, 130, color=FIELD, sw=2.0))
    f.append(fitbox(420, 100, 220, 60, "Push у стек компенсацій:\n[ReleaseInventory]", size=11.5, bold=True, fill=COOL, stroke=NEG, sw=1.5))

    # Крок 2: Успіх
    f.append(fitbox(60, 190, 260, 60, "Крок 2: ChargePayment\nСтатус: ВИКОНАНО", size=12, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))
    f.append(arrow(320, 220, 420, 220, color=FIELD, sw=2.0))
    f.append(fitbox(420, 190, 220, 60, "Push у стек компенсацій:\n[RefundPayment]", size=11.5, bold=True, fill=COOL, stroke=NEG, sw=1.5))

    # Крок 3: Збій
    f.append(fitbox(60, 280, 260, 60, "Крок 3: BookDelivery\nСтатус: ВІДМОВА (503)", size=12, bold=True, fill=WARM, stroke=POS, sw=2.0))
    f.append(arrow(190, 340, 190, 390, color=POS, sw=2.5))
    f.append(text(205, 370, "Тригер відкату саги", size=11.5, color=POS, bold=True, anchor="start"))

    # Розмотування стека компенсацій (LIFO Rollback)
    f.append(rect(60, 390, 580, 240, fill="#fef8f8", stroke=POS, sw=1.8, rx=6))
    f.append(text(350, 415, "ДЕТЕРМІНОВАНИЙ ВІДКАТ (LIFO Unwinding)", size=13, color=POS, bold=True))

    # Відкат 1: Pop RefundPayment
    f.append(fitbox(80, 435, 250, 65, "1. Pop [RefundPayment]\nВиклик PaymentGateway.Refund", size=11.5, bold=True, fill=WARM, stroke=POS, sw=1.5))
    f.append(arrow(330, 467, 400, 467, color=FIELD, sw=1.8))
    f.append(fitbox(400, 435, 220, 65, "Гроші повернено клієнту\n(Гарантований повтор при збої)", size=11, bold=False, fill=GOOD, stroke=FIELD, sw=1.5))

    # Відкат 2: Pop ReleaseInventory
    f.append(fitbox(80, 525, 250, 65, "2. Pop [ReleaseInventory]\nВиклик Warehouse.Release", size=11.5, bold=True, fill=WARM, stroke=POS, sw=1.5))
    f.append(arrow(330, 557, 400, 557, color=FIELD, sw=1.8))
    f.append(fitbox(400, 525, 220, 65, "Товар повернено на баланс\nКінцевий статус: FAILED", size=11, bold=False, fill=GOOD, stroke=FIELD, sw=1.5))

    # Права половина: Структура стану оркестратора
    f.append(rect(700, 30, 460, 620, fill="#fcfdfe", stroke=MUTED, sw=1.5, rx=8))
    f.append(rect(700, 30, 460, 44, fill=GOOD, stroke=MUTED, sw=1.5, rx=8))
    f.append(text(930, 58, "Незмінний журнал історії (Event Log)", size=14, color=INK, bold=True))

    # Список подій в журналі
    history_events = (
        "1. SagaStarted { order_id: \"ORD-981\" }\n"
        "2. StepScheduled { name: \"ReserveInventory\" }\n"
        "3. StepCompleted { result: \"RESERVED_OK\" }\n"
        "4. CompensationRegistered { action: \"Release\" }\n"
        "5. StepScheduled { name: \"ChargePayment\" }\n"
        "6. StepCompleted { result: \"PAYMENT_OK\" }\n"
        "7. CompensationRegistered { action: \"Refund\" }\n"
        "8. StepScheduled { name: \"BookDelivery\" }\n"
        "9. StepFailed { error: \"NO_COURIERS_503\" }\n"
        "10. RollbackStarted { stack_depth: 2 }\n"
        "11. CompensationExecuted { action: \"Refund\" }\n"
        "12. CompensationExecuted { action: \"Release\" }\n"
        "13. SagaTerminated { status: \"ROLLED_BACK\" }"
    )
    f.append(fitbox(720, 95, 420, 350, history_events, size=11.5, bold=False, fill=FILL, stroke=LINE, sw=1.5))

    # Блок гарантій довговічного оркестратора
    f.append(fitbox(720, 465, 420, 165,
                    "Гарантії Orchestrator Engine:\n"
                    "• Точний стан збережено на кожному кроці\n"
                    "• При падінні вузла: відновлення журналу й\n"
                    "  продовження відкату рівно з точки аварії\n"
                    "• Неможливість втрати компенсації\n"
                    "• Вбудовані політики повторів з джитером",
                    size=12, bold=False, fill=COOL, stroke=NEG, sw=1.5))

    render(os.path.join(OUT, 'orchestrator-state-machine-rollback.svg'), W, H, *f)


# ── 4. Гібридна координація: Макро-хореографія та Мікро-оркестрація ──
def fig_hybrid_coordination_topology():
    W, H = 1200, 680
    f = []

    # Заголовок
    f.append(fitbox(50, 20, 1100, 45, "Гібридна топологія: Макро-хореографія між доменами та Мікро-оркестрація всередині", size=15, bold=True, fill=COOL, stroke=NEG, sw=2.0))

    # Спільна шина подій зверху
    f.append(rect(50, 85, 1100, 60, fill=ACCENT, stroke=INK, sw=2.0, rx=6))
    f.append(text(600, 120, "Глобальна шина макро-подій (Enterprise Kafka / Domain Event Bus)", size=14, color=INK, bold=True))

    # Домен 1: Замовлення (Orders Bounded Context)
    f.append(rect(50, 180, 340, 460, fill="#fcfdfe", stroke=MUTED, sw=1.5, rx=8))
    f.append(rect(50, 180, 340, 40, fill=COOL, stroke=MUTED, sw=1.5, rx=8))
    f.append(text(220, 205, "Домен замовлень (Orders)", size=13.5, color=INK, bold=True))

    # Оркестратор замовлень
    f.append(fitbox(70, 245, 300, 70, "Локальний оркестратор\nOrder Fulfillment Saga", size=12.5, bold=True, fill=COOL, stroke=NEG, sw=1.8))
    # Стрілка зверху з шини до оркестратора: зсунута вліво до x=80
    f.append(arrow(80, 145, 80, 245, color=FIELD, sw=2.0))
    f.append(text(85, 165, "OrderSubmitted", size=10.5, color=FIELD, bold=True, anchor="start"))

    f.append(fitbox(70, 340, 300, 120,
                    "Внутрішні сервіси:\n"
                    "• Перевірка лімітів клієнта\n"
                    "• Резерв промокодів\n"
                    "• Формування чека",
                    size=12, bold=False, fill=FILL, stroke=LINE, sw=1.5))

    f.append(arrow(220, 460, 220, 500, color=FIELD, sw=2.0))
    f.append(fitbox(70, 500, 300, 95, "Публікація в шину:\nOrderReadyForBilling\n(Асинхронний факт)", size=12, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))
    # Стрілка назад у шину: по правому краю x=360
    f.append(arrow(360, 500, 360, 145, color=FIELD, sw=1.8))

    # Домен 2: Білінг та платежі (Payments Bounded Context)
    f.append(rect(430, 180, 340, 460, fill="#fcfdfe", stroke=MUTED, sw=1.5, rx=8))
    f.append(rect(430, 180, 340, 40, fill=COOL, stroke=MUTED, sw=1.5, rx=8))
    f.append(text(600, 205, "Домен платежів (Billing)", size=13.5, color=INK, bold=True))

    # Оркестратор білінгу
    f.append(fitbox(450, 245, 300, 70, "Локальний оркестратор\nPayment Processing Workflow", size=12.5, bold=True, fill=COOL, stroke=NEG, sw=1.8))
    # Стрілка зверху з шини: по лівому краю x=460
    f.append(arrow(460, 145, 460, 245, color=FIELD, sw=2.0))
    f.append(text(465, 165, "OrderReadyForBilling", size=10.5, color=FIELD, bold=True, anchor="start"))

    f.append(fitbox(450, 340, 300, 120,
                    "Внутрішні кроки:\n"
                    "• Антифрод скоринг (3D Secure)\n"
                    "• Списання з банківського шлюзу\n"
                    "• Нарахування кешбеку",
                    size=12, bold=False, fill=FILL, stroke=LINE, sw=1.5))

    f.append(arrow(600, 460, 600, 500, color=FIELD, sw=2.0))
    f.append(fitbox(450, 500, 300, 95, "Публікація в шину:\nPaymentSettled\n(Асинхронний факт)", size=12, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))
    # Стрілка назад у шину: по правому краю x=740
    f.append(arrow(740, 500, 740, 145, color=FIELD, sw=1.8))

    # Домен 3: Логістика (Logistics Bounded Context)
    f.append(rect(810, 180, 340, 460, fill="#fcfdfe", stroke=MUTED, sw=1.5, rx=8))
    f.append(rect(810, 180, 340, 40, fill=COOL, stroke=MUTED, sw=1.5, rx=8))
    f.append(text(980, 205, "Домен логістики (Fulfillment)", size=13.5, color=INK, bold=True))

    # Оркестратор логістики
    f.append(fitbox(830, 245, 300, 70, "Локальний оркестратор\nDispatch & Route Planner", size=12.5, bold=True, fill=COOL, stroke=NEG, sw=1.8))
    # Стрілка зверху з шини: по лівому краю x=840
    f.append(arrow(840, 145, 840, 245, color=FIELD, sw=2.0))
    f.append(text(845, 165, "PaymentSettled", size=10.5, color=FIELD, bold=True, anchor="start"))

    f.append(fitbox(830, 340, 300, 120,
                    "Внутрішні кроки:\n"
                    "• Пакування на складі\n"
                    "• Призначення водія\n"
                    "• Генерація TTH накладної",
                    size=12, bold=False, fill=FILL, stroke=LINE, sw=1.5))

    f.append(arrow(980, 460, 980, 500, color=FIELD, sw=2.0))
    f.append(fitbox(830, 500, 300, 95, "Публікація в шину:\nParcelDispatched\n(Асинхронний факт)", size=12, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))
    # Стрілка назад у шину: по правому краю x=1120
    f.append(arrow(1120, 500, 1120, 145, color=FIELD, sw=1.8))

    render(os.path.join(OUT, 'hybrid-coordination-topology.svg'), W, H, *f)


if __name__ == '__main__':
    fig_orchestration_vs_choreography_flow()
    fig_choreography_compensation_chaos()
    fig_orchestrator_state_machine_rollback()
    fig_hybrid_coordination_topology()
    print("Всі фігури згенеровано успішно.")
