# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_retry_storm_cascade():
    """Порівняння наївного негайного повтору (шторм) та експоненційного відступу з джитером."""
    W, H = 960, 480
    frags = []
    frags.append(text(W / 2, 28, "Порівняння реакцій системи: наївний повторний шторм проти розсіювання з джитером",
                      size=15, bold=True))

    # ── Ліва колонка: Наївний повтор (шторм)
    frags.append(rect(30, 55, 435, 400, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    frags.append(text(247, 85, "Наївний негайний повтор (Retry Storm)", size=14, bold=True, color=POS))
    frags.append(text(247, 105, "Повтор одразу після збою множить навантаження", size=11, color=MUTED))

    # Схема клієнтів і сервера
    frags.append(rect(50, 130, 150, 110, fill=BG, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(125, 155, "1000 клієнтів", size=12, bold=True))
    frags.append(text(125, 175, "Тайм-аут запиту", size=10, color=POS))
    frags.append(text(125, 195, "Негайний retry: ×3", size=10, bold=True, color=POS))
    frags.append(text(125, 215, "0 мс паузи", size=10, color=MUTED))

    frags.append(rect(295, 130, 150, 110, fill=BG, stroke=POS, sw=1.5, rx=6))
    frags.append(text(370, 155, "Сервер у кризі", size=12, bold=True, color=POS))
    frags.append(text(370, 175, "CPU / пул БД 100%", size=10, color=POS))
    frags.append(text(370, 195, "Черга accept переповнена", size=10, color=MUTED))
    frags.append(text(370, 215, "RST / 503 / 504", size=10, color=POS))

    # Стрілки шторму
    frags.append(arrow(200, 160, 295, 160, color=POS, sw=2.5))
    frags.append(arrow(200, 185, 295, 185, color=POS, sw=2.5))
    frags.append(arrow(200, 210, 295, 210, color=POS, sw=2.5))
    frags.append(text(247, 148, "3000 req/s", size=10, bold=True, color=POS))

    # Наслідок ліворуч
    left_note = textbox(247, 340, "Каскадний колапс:\n"
                                  "1. Сервер не встигає обробити первинні запити.\n"
                                  "2. Хвиля повторів добиває залишки пам'яті та черг.\n"
                                  "3. Балансувальник маркує вузол як мертвий.\n"
                                  "4. Трафік падає на сусідні вузли, знищуючи весь кластер.",
                        size=11, min_w=395, pad=12, fill="#ffebee", stroke=POS, color=INK)
    frags.append(left_note[0])

    # ── Права колонка: Експоненційний відступ з джитером
    frags.append(rect(495, 55, 435, 400, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(712, 85, "Експоненційний відступ із Jitter", size=14, bold=True, color=FIELD))
    frags.append(text(712, 105, "Збільшення пауз і рандомізація розсіюють удар", size=11, color=MUTED))

    # Схема праворуч
    frags.append(rect(515, 130, 150, 110, fill=BG, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(590, 155, "1000 клієнтів", size=12, bold=True))
    frags.append(text(590, 175, "Тайм-аут запиту", size=10, color=MUTED))
    frags.append(text(590, 195, "Backoff: 2ⁱ · base", size=10, bold=True, color=FIELD))
    frags.append(text(590, 215, "Full Jitter: [0, t]", size=10, color=FIELD))

    frags.append(rect(760, 130, 150, 110, fill=BG, stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(835, 155, "Сервер відновлюється", size=12, bold=True, color=FIELD))
    frags.append(text(835, 175, "Обробка черги", size=10, color=FIELD))
    frags.append(text(835, 195, "Звільнення воркерів", size=10, color=MUTED))
    frags.append(text(835, 215, "200 OK на повторах", size=10, color=FIELD))

    # Стрілки розсіяного трафіку
    frags.append(arrow(665, 160, 760, 160, color=FIELD, sw=1.5))
    frags.append(arrow(665, 185, 760, 185, color=FIELD, sw=1.2))
    frags.append(arrow(665, 210, 760, 210, color=FIELD, sw=1.0))
    frags.append(text(712, 148, "Розмитий потік", size=10, bold=True, color=FIELD))

    # Наслідок праворуч
    right_note = textbox(712, 340, "Стабілізація системи:\n"
                                   "1. Кожен клієнт відступає з експоненційним зростанням.\n"
                                   "2. Випадкове тремтіння (Jitter) ліквідує синхронні піки.\n"
                                   "3. Сервер встигає звільнити сокети та завершити транзакції.\n"
                                   "4. Повторні спроби успішно проходять без перевантаження.",
                         size=11, min_w=395, pad=12, fill="#e8f5e9", stroke=FIELD, color=INK)
    frags.append(right_note[0])

    render(os.path.join(IMG, "retry-storm-cascade.svg"), W, H, *frags)


def fig_jitter_algorithms_comparison():
    """Порівняння розподілів затримки між спробами: Pure, Full, Equal, Decorrelated Jitter."""
    W, H = 960, 480
    frags = []
    frags.append(text(W / 2, 28, "Алгоритми випадкового тремтіння: розподіл затримок для спроб i = 1, 2, 3",
                      size=15, bold=True))

    # 4 блоки для алгоритмів
    algos = [
        ("1. Pure Exponential (без Jitter)",
         "t = min(max_backoff, base · 2ⁱ)",
         "Фіксований детермінований час",
         "Синхронізація: клієнти б'ють одночасно точними хвилями",
         POS,
         [("i=1", 100, 100, "100 мс"), ("i=2", 200, 200, "200 мс"), ("i=3", 400, 400, "400 мс")]),

        ("2. Full Jitter (Повний джитер)",
         "t = Uniform(0, min(max_backoff, base · 2ⁱ))",
         "Рівномірно від 0 до верхньої межі",
         "Максимальне розсіювання: найменше пікове навантаження на сервер",
         FIELD,
         [("i=1", 0, 100, "0..100 мс"), ("i=2", 0, 200, "0..200 мс"), ("i=3", 0, 400, "0..400 мс")]),

        ("3. Equal Jitter (Рівний джитер)",
         "t = half + Uniform(0, half), де half = min/2",
         "Гарантована основа + випадкова добавка",
         "Уникає нульових затримок, зберігаючи помірне розсіювання",
         NEG,
         [("i=1", 50, 100, "50..100 мс"), ("i=2", 100, 200, "100..200 мс"), ("i=3", 200, 400, "200..400 мс")]),

        ("4. Decorrelated Jitter (Декорельований)",
         "t = min(max_backoff, Uniform(base, prev · 3))",
         "Випадкове блукання від попередньої паузи",
         "Повна незалежність від номерів спроб і відсутність кластеризації",
         "#8e44ad",
         [("i=1", 100, 300, "100..300 мс"), ("i=2", 100, 600, "100..600 мс"), ("i=3", 100, 1200, "100..1200 мс")]),
    ]

    y_start = 55
    card_h = 95
    card_gap = 10

    for idx, (title, formula, desc, pros, color, intervals) in enumerate(algos):
        cy = y_start + idx * (card_h + card_gap)
        # Фон картки
        frags.append(rect(30, cy, 900, card_h, fill=BG, stroke=color, sw=1.2, rx=6))

        # Назва та формула
        frags.append(text(45, cy + 22, title, size=13, bold=True, color=color, anchor="start"))
        frags.append(text(310, cy + 22, formula, size=11, bold=True, color=INK, anchor="start"))

        # Опис і властивість
        frags.append(text(45, cy + 44, desc, size=11, color=MUTED, anchor="start"))
        frags.append(text(45, cy + 64, "• " + pros, size=10, bold=True, color=INK, anchor="start"))

        # Візуалізація смуг затримок праворуч (x: 540 до 890)
        base_x = 600
        scale = 0.22  # масштаб ms -> px

        frags.append(text(base_x - 10, cy + 22, "Діапазони затримок:", size=10, color=MUTED, anchor="end"))
        frags.append(line(base_x, cy + 15, base_x + 280, cy + 15, color="#e5e7eb", sw=1))

        # Малюємо 3 інтервали (i=1, 2, 3)
        row_y = cy + 32
        for att_name, start_ms, end_ms, lbl in intervals:
            x1 = base_x + start_ms * scale
            x2 = base_x + end_ms * scale
            w_bar = max(x2 - x1, 4)

            # смужка інтервалу
            if start_ms == end_ms:
                # точкова мітка
                frags.append(circle(x1, row_y, 4, fill=color, stroke=LINE, sw=1))
            else:
                frags.append(rect(x1, row_y - 4, w_bar, 8, fill=color, stroke="none", rx=3))

            frags.append(text(x2 + 8, row_y + 3, f"{att_name}: {lbl}", size=9, color=INK, anchor="start"))
            row_y += 18

    render(os.path.join(IMG, "jitter-algorithms-comparison.svg"), W, H, *frags)


def fig_idempotency_key_flow():
    """Життєвий цикл запиту з заголовком Idempotency-Key та дедуплікацією на сервері."""
    W, H = 960, 500
    frags = []
    frags.append(text(W / 2, 28, "Життєвий цикл ідемпотентного повтору: захист від подвійної обробки транзакцій",
                      size=15, bold=True))

    # Стовпчики: Клієнт (ліворуч), Шлюз/API (центр), База даних/Сховище ключів (праворуч)
    frags.append(rect(40, 55, 230, 420, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(155, 80, "Клієнт (HTTP Client)", size=13, bold=True))
    frags.append(text(155, 98, "Генерує UUID і робить retry", size=10, color=MUTED))

    frags.append(rect(365, 55, 230, 420, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(480, 80, "Серверний обробник (API)", size=13, bold=True))
    frags.append(text(480, 98, "Перевірка ключа й атомарна дія", size=10, color=MUTED))

    frags.append(rect(690, 55, 230, 420, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(805, 80, "Сховище ключів (Redis / DB)", size=13, bold=True))
    frags.append(text(805, 98, "Таблиця idempotency_keys", size=10, color=MUTED))

    # Лінії життя (пунктир)
    frags.append(line(155, 115, 155, 455, color="#d1d5db", sw=1, dash="4,4"))
    frags.append(line(480, 115, 480, 455, color="#d1d5db", sw=1, dash="4,4"))
    frags.append(line(805, 115, 805, 455, color="#d1d5db", sw=1, dash="4,4"))

    # Фаза 1: Перший запит
    frags.append(arrow(155, 140, 480, 140, color=INK, sw=1.8))
    frags.append(text(317, 132, "1. POST /payments [Key: 7b9e-4c21]", size=10, bold=True))

    frags.append(arrow(480, 160, 805, 160, color=INK, sw=1.5))
    frags.append(text(642, 152, "2. SET key status=PROCESSING NX", size=10, color=INK))

    frags.append(arrow(805, 185, 480, 185, color=FIELD, sw=1.5))
    frags.append(text(642, 178, "3. OK (ключ новий, захоплено)", size=10, color=FIELD))

    # Фаза 2: Виконання та обрив мережі
    frags.append(rect(400, 205, 160, 40, fill="#e8f5e9", stroke=FIELD, sw=1, rx=4))
    frags.append(text(480, 222, "Виконання оплати в БД", size=10, bold=True, color=FIELD))
    frags.append(text(480, 237, "Запис 200 OK у кеш ключів", size=9, color=MUTED))

    frags.append(arrow(480, 260, 805, 260, color=FIELD, sw=1.5))
    frags.append(text(642, 252, "4. UPDATE status=COMPLETED, body=...", size=9, color=FIELD))

    # Обрив відповіді
    frags.append(line(480, 285, 260, 285, color=POS, sw=2, dash="4,3"))
    frags.append(text(280, 277, "✕ Мережевий обрив (TCP RST / Drop)", size=10, bold=True, color=POS))

    # Фаза 3: Повторний запит з тим самим ключем
    frags.append(arrow(155, 330, 480, 330, color=NEG, sw=2))
    frags.append(text(317, 322, "5. RETRY: POST /payments [Key: 7b9e-4c21]", size=10, bold=True, color=NEG))

    frags.append(arrow(480, 355, 805, 355, color=NEG, sw=1.5))
    frags.append(text(642, 347, "6. GET key", size=10, color=NEG))

    frags.append(arrow(805, 385, 480, 385, color=FIELD, sw=1.8))
    frags.append(text(642, 377, "7. status=COMPLETED + збережене тіло", size=10, bold=True, color=FIELD))

    frags.append(arrow(480, 420, 155, 420, color=FIELD, sw=2))
    frags.append(text(317, 412, "8. 200 OK (повернено оригінал без списання)", size=10, bold=True, color=FIELD))

    # Підсумок у рамці
    note = textbox(480, 470, "Результат: оплату проведено рівно 1 раз; клієнт отримав успішну відповідь на повторі.",
                   size=11, min_w=870, pad=6, fill="#f9fafb", stroke="#9ca3af", bold=True, color=INK)
    frags.append(note[0])

    render(os.path.join(IMG, "idempotency-key-flow.svg"), W, H, *frags)


def fig_retry_budget_circuit():
    """Клієнтські механізми самозахисту: Бюджет повторів (Token Bucket) та Запобіжник (Circuit Breaker)."""
    W, H = 960, 460
    frags = []
    frags.append(text(W / 2, 28, "Клієнтський самозахист: Бюджет повторів (Retry Budget) та Запобіжник (Circuit Breaker)",
                      size=15, bold=True))

    # Лівий блок: Retry Budget
    frags.append(rect(30, 55, 435, 380, fill=BG, stroke=NEG, sw=1.5, rx=8))
    frags.append(text(247, 85, "Бюджет повторів (Retry Budget)", size=14, bold=True, color=NEG))
    frags.append(text(247, 105, "Обмеження частки повторів у загальному трафіку", size=11, color=MUTED))

    # Схема токен-бакета
    frags.append(rect(50, 130, 395, 140, fill="#f0f4ff", stroke=NEG, sw=1.2, rx=6))
    frags.append(text(247, 150, "Кошик токенів повторів (Token Bucket)", size=12, bold=True, color=NEG))
    frags.append(text(247, 175, "• Успішний запит (2xx) → додає +0.2 токена в пул", size=11, color=INK))
    frags.append(text(247, 195, "• Повторна спроба (Retry) → списує 1.0 токен з пулу", size=11, color=INK))
    frags.append(text(247, 215, "• Пул порожній → повтор блокується, віддається помилка", size=11, bold=True, color=POS))
    frags.append(text(247, 245, "Гарантія: частка повторів ніколи не перевищить 20% трафіку", size=10, bold=True, color=FIELD))

    rb_note = textbox(247, 345, "Захищає бекенд від самознищення клієнтами:\n"
                                "Якщо збої масові, клієнти не генерують шквал retry,\n"
                                "а швидко відсікають надлишок, даючи серверу відновитися.",
                      size=11, min_w=395, pad=10, fill=FILL, stroke="#d1d5db", color=INK)
    frags.append(rb_note[0])

    # Правий блок: Circuit Breaker
    frags.append(rect(495, 55, 435, 380, fill=BG, stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(712, 85, "Запобіжник (Circuit Breaker)", size=14, bold=True, color=FIELD))
    frags.append(text(712, 105, "Автоматичне відсікання безнадійних мережевих викликів", size=11, color=MUTED))

    # Три стани
    # 1. Closed
    frags.append(rect(515, 130, 115, 75, fill="#e8f5e9", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(572, 155, "CLOSED", size=12, bold=True, color=FIELD))
    frags.append(text(572, 175, "Нормальний", size=10, color=INK))
    frags.append(text(572, 190, "обмін запитами", size=9, color=MUTED))

    # 2. Open
    frags.append(rect(800, 130, 115, 75, fill="#ffebee", stroke=POS, sw=1.5, rx=6))
    frags.append(text(857, 155, "OPEN", size=12, bold=True, color=POS))
    frags.append(text(857, 175, "Розрив кола", size=10, bold=True, color=POS))
    frags.append(text(857, 190, "Швидкий fail-fast", size=9, color=MUTED))

    # 3. Half-Open
    frags.append(rect(655, 235, 120, 70, fill="#fff8e1", stroke="#f39c12", sw=1.5, rx=6))
    frags.append(text(715, 258, "HALF-OPEN", size=11, bold=True, color="#d35400"))
    frags.append(text(715, 275, "Пробний запит", size=10, color=INK))
    frags.append(text(715, 290, "Перевірка зв'язку", size=9, color=MUTED))

    # Переходи між станами
    frags.append(arrow(630, 155, 800, 155, color=POS, sw=1.8))
    frags.append(text(715, 145, ">50% помилок", size=10, bold=True, color=POS))

    frags.append(arrow(857, 205, 775, 255, color="#f39c12", sw=1.5))
    frags.append(text(840, 240, "Тайм-аут остигання", size=9, color="#d35400"))

    frags.append(arrow(655, 270, 572, 205, color=FIELD, sw=1.5))
    frags.append(text(595, 250, "Успіх", size=10, bold=True, color=FIELD))

    cb_note = textbox(712, 365, "Fail-Fast поведінка:\n"
                                "У стані OPEN запити не йдуть у мережу взагалі,\n"
                                "захищаючи клієнтські потоки від зависання на тайм-аутах.",
                      size=11, min_w=395, pad=10, fill=FILL, stroke="#d1d5db", color=INK)
    frags.append(cb_note[0])

    render(os.path.join(IMG, "retry-budget-circuit.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_retry_storm_cascade()
    fig_jitter_algorithms_comparison()
    fig_idempotency_key_flow()
    fig_retry_budget_circuit()
    print("Всі 4 фігури згенеровано успішно.")
