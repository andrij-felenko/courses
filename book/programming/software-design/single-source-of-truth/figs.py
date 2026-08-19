# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# -- Фігура 1: розходження двох незалежних джерел (дрейф стану) ---------------
def fig_divergence_drift():
    W, H = 960, 520
    f = []

    f.append(text(480, 36, 'Два незалежні місця запису неминуче розходяться в часі',
                  size=16, color=INK, bold=True))

    # Ліва колонка — клієнтський кеш / локальна модель
    b, bw, bh = textbox(240, 110, ['Клієнтський стан (UI)', 'баланс: 1 200 ₴', 'знижка: 10%'],
                        size=14, pad=14, fill='#fdecea', stroke=POS, sw=2.0, min_w=240)
    f.append(b)

    # Права колонка — серверна база даних
    b, bw, bh = textbox(720, 110, ['Серверна база даних', 'баланс: 1 000 ₴', 'знижка: 5% (акція скінчилась)'],
                        size=14, pad=14, fill='#eef2ff', stroke=NEG, sw=2.0, min_w=280)
    f.append(b)

    # Подія посередині
    f.append(line(240, 160, 240, 240, color=POS, sw=1.8, dash='4,4'))
    f.append(line(720, 160, 720, 240, color=NEG, sw=1.8, dash='4,4'))

    b, bw, bh = textbox(480, 240, ['Паралельні зміни без узгодження',
                                   '1. Клієнт застосовує кешовану знижку',
                                   '2. Сервер списує комісію за обслуговування'],
                        size=13, pad=12, fill='#fbfbfd', stroke=MUTED, sw=1.4, min_w=340)
    f.append(b)

    f.append(arrow(480, 290, 240, 350, color=POS, sw=1.8))
    f.append(arrow(480, 290, 720, 350, color=NEG, sw=1.8))

    # Стан після події — розкол правди
    b, bw, bh = textbox(240, 410, ['Локальний розрахунок', 'до сплати: 1 080 ₴', '«Успішно оформлено»'],
                        size=14, pad=14, fill='#fdecea', stroke=POS, sw=2.2, min_w=240)
    f.append(b)

    b, bw, bh = textbox(720, 410, ['Серверна транзакція', 'до сплати: 1 150 ₴', '«Помилка суми / відхилено»'],
                        size=14, pad=14, fill='#eef2ff', stroke=NEG, sw=2.2, min_w=280)
    f.append(b)

    # Підсумок розколу
    f.append(line(240, 475, 720, 475, color=POS, sw=2.0, dash='6,4'))
    f.append(text(480, 500, 'Конфлікт: обидві сторони вважають себе правими, єдиного арбітра немає',
                  size=14, color=POS, bold=True))

    render(os.path.join(IMG, 'divergence-drift.svg'), W, H, *f)


# -- Фігура 2: архітектура авторитетного стану та похідних проєкцій -----------
def fig_ssot_architecture():
    W, H = 1000, 540
    f = []

    f.append(text(500, 34, 'Авторитетне першоджерело керує мутаціями; решта систем — похідні проєкції',
                  size=16, color=INK, bold=True))

    # Єдине джерело правди у центрі зверху
    b, bw, bh = textbox(500, 115, ['Єдине джерело правди (SSOT)',
                                  'Авторитетний первинний стан',
                                  'Єдине місце запису та валідації інваріантів'],
                        size=15, pad=16, fill='#eafaf0', stroke=FIELD, sw=2.6, min_w=400)
    f.append(b)

    # Шина синхронізації / потік подій
    f.append(arrow(500, 175, 500, 245, color=FIELD, sw=2.4))
    f.append(text(515, 215, 'однонапрямлений потік змін (події / WAL / реплікація)',
                  size=13, color=MUTED, anchor='start'))

    b, bw, bh = textbox(500, 275, ['Шина синхронізації даних', 'CDC / Журнал змін / Подієвий брокер'],
                        size=14, pad=12, fill='#fbfbfd', stroke=MUTED, sw=1.6, min_w=380)
    f.append(b)

    # Стрілки вниз до проєкцій
    f.append(arrow(360, 315, 180, 390, color=MUTED, sw=1.8))
    f.append(arrow(450, 315, 390, 390, color=MUTED, sw=1.8))
    f.append(arrow(550, 315, 610, 390, color=MUTED, sw=1.8))
    f.append(arrow(640, 315, 820, 390, color=MUTED, sw=1.8))

    # 4 типи похідних проєкцій
    b1, _, _ = textbox(180, 440, ['Кеш читання (Redis)', 'Швидкий доступ', 'Скидається по TTL/CDC'],
                       size=13, pad=12, fill='#f4f6f8', stroke=LINE, sw=1.4, min_w=200)
    f.append(b1)

    b2, _, _ = textbox(390, 440, ['Пошуковий індекс', '(Elasticsearch)', 'Повнотекстовий пошук'],
                       size=13, pad=12, fill='#f4f6f8', stroke=LINE, sw=1.4, min_w=200)
    f.append(b2)

    b3, _, _ = textbox(610, 440, ['Аналітична БД (OLAP)', 'Звіти та агрегати', 'Денормалізована вітрина'],
                       size=13, pad=12, fill='#f4f6f8', stroke=LINE, sw=1.4, min_w=200)
    f.append(b3)

    b4, _, _ = textbox(820, 440, ['Клієнтський UI (State)', 'Локальне відображення', 'Тільки читання / Дії'],
                       size=13, pad=12, fill='#f4f6f8', stroke=LINE, sw=1.4, min_w=200)
    f.append(b4)

    f.append(text(500, 515, 'Похідні копії оптимізовані для читання, але ніколи не володіють первинним станом',
                  size=14, color=FIELD, bold=True))

    render(os.path.join(IMG, 'ssot-architecture.svg'), W, H, *f)


# -- Фігура 3: Schema-First конвеєр ------------------------------------------
def fig_schema_first_pipeline():
    W, H = 1000, 500
    f = []

    f.append(text(500, 34, 'Schema-First: єдиний контракт компілюється в код для всіх платформ',
                  size=16, color=INK, bold=True))

    # Схема у вихідній позиції
    b, bw, bh = textbox(180, 240, ['Єдина схема контракту',
                                  'schema.proto / openapi.yaml',
                                  '• Типи полів та нумерація',
                                  '• Обов\'язковість і діапазони',
                                  '• Формати повідомлень'],
                        size=14, pad=16, fill='#eafaf0', stroke=FIELD, sw=2.4, min_w=260)
    f.append(b)

    # Компілятор посередині
    f.append(arrow(320, 240, 440, 240, color=FIELD, sw=2.4))
    f.append(text(380, 218, 'генерація', size=13, color=FIELD, bold=True))

    b, bw, bh = textbox(500, 240, ['Генератор коду', 'protoc / openapi-gen', 'Трансляція типів та валідацій'],
                        size=13, pad=12, fill='#fbfbfd', stroke=MUTED, sw=1.6, min_w=180)
    f.append(b)

    # Стрілки праворуч до цільових артефактів
    f.append(arrow(600, 210, 710, 120, color=NEG, sw=1.8))
    f.append(arrow(600, 240, 710, 240, color=FIELD, sw=1.8))
    f.append(arrow(600, 270, 710, 360, color=POS, sw=1.8))

    # 3 виходи
    b1, _, _ = textbox(840, 120, ['Серверний бекенд', 'C++ / Go / Rust', 'Строгі DTO + gRPC stubs'],
                       size=13, pad=12, fill='#eef2ff', stroke=NEG, sw=1.6, min_w=240)
    f.append(b1)

    b2, _, _ = textbox(840, 240, ['Клієнтський веб/мобільний', 'TypeScript / Swift / Kotlin', 'Типізовані SDK та валідатори'],
                       size=13, pad=12, fill='#eafaf0', stroke=FIELD, sw=1.6, min_w=240)
    f.append(b2)

    b3, _, _ = textbox(840, 360, ['Документація та моки', 'Swagger UI / Mock-сервер', 'Автоматична верифікація'],
                       size=13, pad=12, fill='#fdecea', stroke=POS, sw=1.6, min_w=240)
    f.append(b3)

    f.append(text(500, 465, 'Зміна схеми оновлює всі модулі одночасно — ручний дрейф моделей неможливий',
                  size=14, color=INK, bold=True))

    render(os.path.join(IMG, 'schema-first-pipeline.svg'), W, H, *f)


# -- Фігура 4: SSOT проти SPOF -----------------------------------------------
def fig_ssot_vs_spof():
    W, H = 1000, 520
    f = []

    f.append(text(500, 34, 'Логічне єдине джерело (SSOT) не є фізичною єдиною точкою відмови (SPOF)',
                  size=16, color=INK, bold=True))

    # Ліва панель: помилкове ототожнення (SPOF)
    lx, ly, lw, lh = 50, 70, 420, 390
    f.append(rect(lx, ly, lw, lh, fill='#fdecea', stroke=POS, sw=1.8))
    f.append(text(lx + lw/2, ly + 32, 'Фізичний SPOF (небезпечна наївність)', size=15, color=POS, bold=True))

    b, _, _ = textbox(lx + lw/2, ly + 120, ['Один фізичний сервер', 'або єдиний диск БД'],
                      size=13, pad=10, fill='#ffffff', stroke=POS, sw=1.6, min_w=240)
    f.append(b)

    f.append(arrow(lx + lw/2, ly + 165, lx + lw/2, ly + 215, color=POS, sw=2.0))
    f.append(text(lx + lw/2 + 10, ly + 190, 'аварія / збій живлення', size=12, color=POS, anchor='start'))

    b, _, _ = textbox(lx + lw/2, ly + 270, ['Повна зупинка всієї системи',
                                            '• Немає куди писати',
                                            '• Немає звідки читати',
                                            '• Ризик втрати даних'],
                      size=13, pad=12, fill='#ffffff', stroke=POS, sw=1.6, min_w=300)
    f.append(b)
    f.append(text(lx + lw/2, ly + 360, 'SSOT сплутано з відсутністю резервування', size=13, color=POS, bold=True))

    # Права панель: правильна реалізація SSOT через консенсус і реплікацію
    rx, ry, rw, rh = 530, 70, 420, 390
    f.append(rect(rx, ry, rw, rh, fill='#eafaf0', stroke=FIELD, sw=1.8))
    f.append(text(rx + rw/2, ry + 32, 'Логічний SSOT + Фізична відмовостійкість', size=15, color=FIELD, bold=True))

    b, _, _ = textbox(rx + rw/2, ry + 120, ['Кластер консенсусу (Raft / Paxos)', 'Лідер приймає авторитетний запис'],
                      size=13, pad=10, fill='#ffffff', stroke=FIELD, sw=1.6, min_w=320)
    f.append(b)

    f.append(arrow(rx + rw/2, ry + 165, rx + rw/2, ry + 215, color=FIELD, sw=2.0))
    f.append(text(rx + rw/2 + 10, ry + 190, 'синхронна/кворумна реплікація', size=12, color=FIELD, anchor='start'))

    b, _, _ = textbox(rx + rw/2, ry + 270, ['Високодоступний логічний SSOT',
                                            '• Кворум із 3–5 вузлів',
                                            '• Автоматичні перевибори лідера',
                                            '• Кеші та репліки для читання'],
                      size=13, pad=12, fill='#ffffff', stroke=FIELD, sw=1.6, min_w=320)
    f.append(b)
    f.append(text(rx + rw/2, ry + 360, 'Одне авторитетне правило, багато надійних копій', size=13, color=FIELD, bold=True))

    f.append(text(500, 495, 'SSOT визначає авторитетність рішення, а не кількість фізичних машин',
                  size=14, color=INK, bold=True))

    render(os.path.join(IMG, 'ssot-vs-spof.svg'), W, H, *f)


# -- Фігура 5 (вставка hist): часова шкала еволюції єдиного джерела -----------
def fig_hist_lineage():
    W, H = 1050, 460
    f = []
    axis_y = 230

    items = [
        ('1970', 'Едгар Кодд (IBM)', 'Реляційна нормалізація\nусунення аномалій запису'),
        ('1999', 'Хант і Томас', 'Принцип DRY у книзі\nThe Pragmatic Programmer'),
        ('2005', 'Грег Янг', 'Event Sourcing: події\nяк абсолютна правда'),
        ('2014', 'Confluent', 'Schema Registry для\nKafka та протоколів'),
        ('2015', 'Абрамов, Кларк', 'Redux: єдине сховище\n(Single Store) для UI'),
    ]

    f.append(text(525, 40, 'Еволюція ідеї єдиного джерела: від таблиць баз даних до розподілених систем',
                  size=16, color=INK, bold=True))
    f.append(line(60, axis_y, W - 60, axis_y, color=MUTED, sw=2.0))

    xs = [110 + i * 205 for i in range(len(items))]
    for i, (year, author, desc) in enumerate(items):
        x = xs[i]
        above = (i % 2 == 0)
        cy = 130 if above else 330
        col = FIELD if i >= 3 else NEG
        b, bw, bh = textbox(x, cy, [year, author, desc], size=12, pad=10,
                            fill='#fbfbfd', stroke=col, sw=1.8, min_w=175)
        f.append(b)
        y_edge = cy + bh / 2 if above else cy - bh / 2
        f.append(line(x, y_edge, x, axis_y, color=MUTED, sw=1.4, dash='4,4'))
        f.append(circle(x, axis_y, 6, fill=col, stroke=col, sw=1.0))

    render(os.path.join(IMG, 'hist-lineage.svg'), W, H, *f)


# -- Фігура 6 (вставка proj): пайплайн валідації та запобігання дрейфу --------
def fig_proj_pipeline():
    W, H = 960, 440
    f = []

    f.append(text(480, 34, 'Пайплайн неперервної інтеграції: блокування збірки при розходженні контракту',
                  size=15, color=INK, bold=True))

    b1, _, _ = textbox(150, 160, ['Схема контракту', 'user_profile.proto'],
                       size=13, pad=12, fill='#eafaf0', stroke=FIELD, sw=2.0, min_w=180)
    f.append(b1)

    f.append(arrow(240, 160, 350, 160, color=FIELD, sw=2.0))
    f.append(text(295, 140, 'protoc', size=13, color=FIELD, bold=True))

    b2, _, _ = textbox(460, 160, ['Згенерований код', '• C++ server headers', '• TypeScript client DTOs'],
                       size=13, pad=12, fill='#fbfbfd', stroke=MUTED, sw=1.6, min_w=200)
    f.append(b2)

    f.append(arrow(560, 160, 670, 160, color=MUTED, sw=2.0))
    f.append(text(615, 140, 'CI Test', size=13, color=MUTED, bold=True))

    b3, _, _ = textbox(790, 160, ['Детектор дрейфу', 'Contract Drift Check', 'Порівняння бінарних хешів'],
                       size=13, pad=12, fill='#eef2ff', stroke=NEG, sw=2.0, min_w=200)
    f.append(b3)

    # Дві гілки перевірки
    f.append(arrow(790, 220, 600, 330, color=FIELD, sw=2.0))
    b_ok, _, _ = textbox(520, 350, ['✓ Хеші збігаються', 'Збірка успішна, деплой дозволено'],
                         size=13, pad=10, fill='#eafaf0', stroke=FIELD, sw=1.8, min_w=240)
    f.append(b_ok)

    f.append(arrow(790, 220, 850, 330, color=POS, sw=2.0))
    b_err, _, _ = textbox(850, 350, ['✖ Виявлено дрейф', 'Ручна зміна клієнта без схеми', 'Збірку заблоковано'],
                          size=13, pad=10, fill='#fdecea', stroke=POS, sw=1.8, min_w=200)
    f.append(b_err)

    render(os.path.join(IMG, 'proj-pipeline.svg'), W, H, *f)


fig_divergence_drift()
fig_ssot_architecture()
fig_schema_first_pipeline()
fig_ssot_vs_spof()
fig_hist_lineage()
fig_proj_pipeline()
print('All figures generated successfully.')
