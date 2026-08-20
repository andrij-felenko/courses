# ⚙️ Інкрементний рушій матеріалізованих представлень на C та C++

Інкрементне оновлення представлень (Incremental View Maintenance, IVM) у реляційних рушіях баз даних базується на перехопленні операцій модифікації базових таблиць (`INSERT`, `UPDATE`, `DELETE`) та застосуванні диференційних змін безпосередньо до збереженого матеріалізованого стану.

Нижче реалізовано високопродуктивний багатопотоковий рушій інкрементного представлення в оперативній пам'яті. Рушій відстежує стан двох базових таблиць — `orders` (замовлення) та `order_items` (позиції товарів) — і неперервно підтримує агреговане матеріалізоване представлення загальних продажів за категоріями товарів для оплачених замовлень:

```sql
SELECT i.category_id,
       SUM(i.quantity * i.price) AS total_revenue,
       COUNT(*)                  AS item_count
FROM orders o
JOIN order_items i ON o.order_id = i.order_id
WHERE o.is_paid = true
GROUP BY i.category_id;
```

---

### Архітектура пам'яті, індексація та конвеєр обробки дельт

Рушій реалізує такі фундаментальні структури даних та алгоритмічні кроки:

#### 1. Структури зберігання та індекси з'єднання
* **Сховище первинних сутностей**: таблиці `orders` та `order_items` зберігаються у геш-таблицях для прямого доступу за первинними ключами `order_id` та `item_id`.
* **Вторинний індекс зовнішнього ключа**: для запобігання повному скануванню позицій товарів під час зміни статусу замовлення рушій підтримує вторинний індекс `order_to_items_idx` (мультикарту). Цей індекс зіставляє кожен `order_id` з множиною відповідних `item_id`, забезпечуючи складність диференційного з'єднання `O(k)`, де `k` — середня кількість товарів у замовленні (зазвичай `k ∈ [1, 10]`), замість `O(N)`.

#### 2. Життєвий цикл транзакційної дельти
* **Зміна предиката в замовленні**: коли поле `is_paid` перемикається з `false` на `true`, генерується дельта зі знаком `+1`. Рушій вибирає всі позиції замовлення за індексом і додає їхні вартості до відповідних категорій матеріалізованого представлення. Якщо замовлення повертається або скасовується (`true` → `false`), генерується дельта `-1`.
* **Модифікація позицій товарів**: під час додавання чи видалення позиції товару рушій перевіряє стан оплати замовлення в `orders`. Якщо замовлення оплачене, дельта негайно поширюється на матеріалізований агрегат.
* **Кратність та очищення нульових груп**: поле `item_count` виконує роль лічильника кратності. Якщо в результаті видалень `item_count` досягає нуля, категорія повністю видаляється з геш-таблиці представлення, щоб не засмічувати пам'ять порожніми записами з нульовим балансом.

---

### Вихідний код реалізації

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <unordered_map>
#include <string>
#include <mutex>
#include <shared_mutex>
#include <optional>
#include <cstdint>

// Базові структури реляційних кортежів
struct Order {
    uint64_t order_id;
    uint64_t customer_id;
    bool is_paid;
};

struct OrderItem {
    uint64_t item_id;
    uint64_t order_id;
    uint32_t category_id;
    uint32_t quantity;
    double price;
};

// Збережений агрегований стан матеріалізованого рядка
struct MaterializedCategoryStats {
    uint32_t category_id;
    double total_revenue = 0.0;
    int64_t item_count = 0; // Лічильник кратності для коректного DELETE
};

class IncrementalViewEngine {
private:
    // Базові сховища даних з індексами
    std::unordered_map<uint64_t, Order> orders_;
    std::unordered_map<uint64_t, OrderItem> items_;
    std::unordered_multimap<uint64_t, uint64_t> order_to_items_idx_; // order_id -> item_id

    // Матеріалізований стан (групування за category_id)
    std::unordered_map<uint32_t, MaterializedCategoryStats> mat_view_;

    mutable std::shared_mutex rw_lock_;

    // Внутрішній метод диференційного оновлення стану матеріалізованого в'ю
    void apply_delta(uint32_t category_id, double delta_revenue, int64_t delta_count) {
        auto it = mat_view_.find(category_id);
        if (it == mat_view_.end()) {
            if (delta_count > 0) {
                mat_view_[category_id] = {category_id, delta_revenue, delta_count};
            }
            return;
        }

        it->second.total_revenue += delta_revenue;
        it->second.item_count += delta_count;

        // Якщо всі входження категорії видалені — прибираємо рядок зі стану
        if (it->second.item_count <= 0) {
            mat_view_.erase(it);
        }
    }

public:
    // Вставка або оновлення замовлення
    void upsert_order(const Order& new_order) {
        std::unique_lock lock(rw_lock_);
        
        bool old_paid = false;
        bool had_old = false;

        auto it = orders_.find(new_order.order_id);
        if (it != orders_.end()) {
            had_old = true;
            old_paid = it->second.is_paid;
            it->second = new_order;
        } else {
            orders_[new_order.order_id] = new_order;
        }

        // Якщо статус оплати не змінився, диференційне з'єднання не змінює MV
        if (had_old && old_paid == new_order.is_paid) {
            return;
        }

        // Зміна предиката: замовлення оплатили (+1) або скасували оплату (-1)
        int64_t sign = (new_order.is_paid ? 1 : 0) - (old_paid ? 1 : 0);
        if (sign == 0) return;

        // Поширюємо дельту на всі прив'язані позиції товарів
        auto [range_begin, range_end] = order_to_items_idx_.equal_range(new_order.order_id);
        for (auto item_it = range_begin; item_it != range_end; ++item_it) {
            const auto& item = items_[item_it->second];
            double rev = item.quantity * item.price * sign;
            apply_delta(item.category_id, rev, sign);
        }
    }

    // Додавання позиції товару до замовлення
    void insert_order_item(const OrderItem& item) {
        std::unique_lock lock(rw_lock_);

        items_[item.item_id] = item;
        order_to_items_idx_.emplace(item.order_id, item.item_id);

        // Перевіряємо, чи оплачене відповідне замовлення
        auto order_it = orders_.find(item.order_id);
        if (order_it != orders_.end() && order_it->second.is_paid) {
            double rev = item.quantity * item.price;
            apply_delta(item.category_id, rev, 1);
        }
    }

    // Видалення позиції товару
    void delete_order_item(uint64_t item_id) {
        std::unique_lock lock(rw_lock_);

        auto it = items_.find(item_id);
        if (it == items_.end()) return;

        const OrderItem item = it->second;
        items_.erase(it);

        // Видалення з індексу
        auto [begin, end] = order_to_items_idx_.equal_range(item.order_id);
        for (auto cur = begin; cur != end; ++cur) {
            if (cur->second == item_id) {
                order_to_items_idx_.erase(cur);
                break;
            }
        }

        auto order_it = orders_.find(item.order_id);
        if (order_it != orders_.end() && order_it->second.is_paid) {
            double rev = -(item.quantity * item.price);
            apply_delta(item.category_id, rev, -1);
        }
    }

    // Миттєве читання матеріалізованого агрегату за O(1)
    std::optional<MaterializedCategoryStats> get_category_stats(uint32_t category_id) const {
        std::shared_lock lock(rw_lock_);
        auto it = mat_view_.find(category_id);
        if (it != mat_view_.end()) {
            return it->second;
        }
        return std::nullopt;
    }
};

int main() {
    IncrementalViewEngine engine;

    // Створюємо неоплачене замовлення #1
    engine.upsert_order({1, 1001, false});

    // Додаємо дві позиції товарів у категорію #42
    engine.insert_order_item({101, 1, 42, 2, 50.0});  // 100.0 грн
    engine.insert_order_item({102, 1, 42, 1, 150.0}); // 150.0 грн

    // Оскільки замовлення не оплачене, матеріалізоване в'ю порожнє
    auto stats = engine.get_category_stats(42);
    std::cout << "До оплати: категорія 42 існує? " << (stats.has_value() ? "Так" : "Ні") << "\n";

    // Оплачуємо замовлення #1 — спрацьовує диференційне оновлення IVM
    engine.upsert_order({1, 1001, true});

    stats = engine.get_category_stats(42);
    if (stats) {
        std::cout << "Після оплати:\n";
        std::cout << "  - Дохід (Revenue): " << stats->total_revenue << " грн\n";
        std::cout << "  - Кількість товарів (Count): " << stats->item_count << "\n";
    }

    // Видаляємо одну позицію
    engine.delete_order_item(101);

    stats = engine.get_category_stats(42);
    if (stats) {
        std::cout << "Після видалення позиції 101:\n";
        std::cout << "  - Новий дохід: " << stats->total_revenue << " грн\n";
        std::cout << "  - Нова кількість: " << stats->item_count << "\n";
    }

    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

// Базові реляційні кортежі
typedef struct {
    uint64_t order_id;
    uint64_t customer_id;
    bool is_paid;
} Order;

typedef struct {
    uint64_t item_id;
    uint64_t order_id;
    uint32_t category_id;
    uint32_t quantity;
    double price;
} OrderItem;

// Запис матеріалізованого представлення
typedef struct {
    uint32_t category_id;
    double total_revenue;
    int64_t item_count;
    bool is_active;
} MatViewEntry;

#define MAX_ORDERS 1024
#define MAX_ITEMS 4096
#define MAX_CATEGORIES 256

typedef struct {
    Order orders[MAX_ORDERS];
    bool order_present[MAX_ORDERS];

    OrderItem items[MAX_ITEMS];
    bool item_present[MAX_ITEMS];

    MatViewEntry view_table[MAX_CATEGORIES];
} IncrementalViewEngineC;

void engine_init(IncrementalViewEngineC *eng) {
    for (int i = 0; i < MAX_ORDERS; i++) eng->order_present[i] = false;
    for (int i = 0; i < MAX_ITEMS; i++) eng->item_present[i] = false;
    for (int i = 0; i < MAX_CATEGORIES; i++) eng->view_table[i].is_active = false;
}

// Застосування дельти до матеріалізованого масиву
static void apply_delta_c(IncrementalViewEngineC *eng, uint32_t cat_id, double delta_rev, int64_t delta_cnt) {
    if (cat_id >= MAX_CATEGORIES) return;

    MatViewEntry *entry = &eng->view_table[cat_id];
    if (!entry->is_active) {
        if (delta_cnt > 0) {
            entry->category_id = cat_id;
            entry->total_revenue = delta_rev;
            entry->item_count = delta_cnt;
            entry->is_active = true;
        }
        return;
    }

    entry->total_revenue += delta_rev;
    entry->item_count += delta_cnt;

    if (entry->item_count <= 0) {
        entry->is_active = false;
        entry->total_revenue = 0.0;
        entry->item_count = 0;
    }
}

// Вставка або зміна замовлення
void engine_upsert_order(IncrementalViewEngineC *eng, Order ord) {
    if (ord.order_id >= MAX_ORDERS) return;

    bool had_old = eng->order_present[ord.order_id];
    bool old_paid = had_old ? eng->orders[ord.order_id].is_paid : false;

    eng->orders[ord.order_id] = ord;
    eng->order_present[ord.order_id] = true;

    if (had_old && old_paid == ord.is_paid) return;

    int64_t sign = (ord.is_paid ? 1 : 0) - (old_paid ? 1 : 0);
    if (sign == 0) return;

    // Диференційне сканування прив'язаних позицій
    for (int i = 0; i < MAX_ITEMS; i++) {
        if (eng->item_present[i] && eng->items[i].order_id == ord.order_id) {
            OrderItem *it = &eng->items[i];
            double rev = it->quantity * it->price * (double)sign;
            apply_delta_c(eng, it->category_id, rev, sign);
        }
    }
}

// Вставка позиції товару
void engine_insert_item(IncrementalViewEngineC *eng, OrderItem item) {
    if (item.item_id >= MAX_ITEMS) return;

    eng->items[item.item_id] = item;
    eng->item_present[item.item_id] = true;

    if (item.order_id < MAX_ORDERS && eng->order_present[item.order_id]) {
        if (eng->orders[item.order_id].is_paid) {
            double rev = item.quantity * item.price;
            apply_delta_c(eng, item.category_id, rev, 1);
        }
    }
}

// Видалення позиції товару
void engine_delete_item(IncrementalViewEngineC *eng, uint64_t item_id) {
    if (item_id >= MAX_ITEMS || !eng->item_present[item_id]) return;

    OrderItem it = eng->items[item_id];
    eng->item_present[item_id] = false;

    if (it.order_id < MAX_ORDERS && eng->order_present[it.order_id]) {
        if (eng->orders[it.order_id].is_paid) {
            double rev = -(it.quantity * it.price);
            apply_delta_c(eng, it.category_id, rev, -1);
        }
    }
}

int main(void) {
    IncrementalViewEngineC eng;
    engine_init(&eng);

    // Створюємо замовлення #1 (неоплачене)
    Order o1 = {1, 1001, false};
    engine_upsert_order(&eng, o1);

    // Додаємо позиції товару в категорію 42
    OrderItem it1 = {101, 1, 42, 2, 50.0};  // 100.0 грн
    OrderItem it2 = {102, 1, 42, 1, 150.0}; // 150.0 грн
    engine_insert_item(&eng, it1);
    engine_insert_item(&eng, it2);

    printf("До оплати: категорія 42 активна? %s\n", eng.view_table[42].is_active ? "Так" : "Ні");

    // Оплачуємо замовлення #1
    o1.is_paid = true;
    engine_upsert_order(&eng, o1);

    if (eng.view_table[42].is_active) {
        printf("Після оплати:\n");
        printf("  - Дохід: %.2f грн\n", eng.view_table[42].total_revenue);
        printf("  - Кількість: %lld\n", (long long)eng.view_table[42].item_count);
    }

    // Видаляємо позицію 101
    engine_delete_item(&eng, 101);

    if (eng.view_table[42].is_active) {
        printf("Після видалення позиції 101:\n");
        printf("  - Новий дохід: %.2f грн\n", eng.view_table[42].total_revenue);
        printf("  - Нова кількість: %lld\n", (long long)eng.view_table[42].item_count);
    }

    return 0;
}
```
:::

---

### Покроковий аналіз виконання програми та трасування пам'яті

Розглянемо послідовність дій під час виконання демонстраційного сценарію:
1. **Ініціалізація та вставка неоплаченого замовлення**: виклик `upsert_order({1, 1001, false})` створює запис у таблиці `orders_`. Оскільки предикат `is_paid == false`, диференційне з'єднання не генерує жодних дельт для представлення.
2. **Вставка позицій товарів**: оператори `insert_order_item` для позицій `101` та `102` записують кортежі в таблицю `items_` та реєструють зв'язки в мультиіндексі `order_to_items_idx_`. Оскільки батьківське замовлення ще не оплачене, матеріалізоване представлення лишається порожнім. Виклик `get_category_stats(42)` повертає `std::nullopt`.
3. **Оплата замовлення та диференційний перерахунок**: виклик `upsert_order({1, 1001, true})` виявляє зміну стану предиката `false → true` (`sign = +1`). Рушій зчитує з індексу дві позиції категорії 42 на суми 100.0 грн та 150.0 грн і застосовує дельту `(+250.0, +2)`. Представлення створює новий рядок зі станом `total_revenue = 250.0, item_count = 2`.
4. **Видалення позиції товару**: видалення позиції 101 генерує від'ємну дельту `(-100.0, -1)`. Рушій віднімає 100.0 грн та зменшує лічильник до 1. Стан представлення оновлюється до `150.0 грн, count = 1`.

---

### Оптимізація паралельного доступу та шардування замків

У високонавантажених серверах баз даних використання одного глобального м'ютекса читачів-письменників (`std::shared_mutex rw_lock_`) для всього матеріалізованого стану створює вузьке місце при паралельних мутаціях різних категорій.

Для масштабування на десятках процесорних ядер застосовують такі архітектурні тактики:
* **Шардовані смуги замків (Striped Locks)**: простір ключів групування ділиться на `N` незалежних смуг (наприклад, `N = 64`). Кожна категорія захищається окремим замком за формулою `bucket = hash(category_id) % N`. Це дозволяє паралельним потокам одночасно модифікувати статистику різних категорій без взаємного блокування.
* **Атомарні числові акумулятори**: для простих дистрибутивних сум окремі поля агрегатів реалізують через неблокувальні атомарні типи `std::atomic<int64_t>`, що усуває потребу в ексклюзивних замках для операцій додавання та віднімання.

---

### Детальний аналіз інженерних пасток та граничних випадків

1. **Накопичення похибки заокруглення дійсних чисел (Floating-point Drift)**: Постійне додавання та віднімання сум цін через тип `double` неминуче накопичує похибку стандарту IEEE 754. Після мільйона операцій вставки та видалення баланс категорії може становити `0.0000000000042` замість чистого нуля, через що умова видалення рядка не спрацює. У промислових базах даних (PostgreSQL, Oracle) грошові підсумки завжди розраховуються в цілочисельних типах фіксованої коми (типи `numeric`, `decimal` або `int64_t` у мінімальних неподільних одиницях валюти — копійках/центах).
2. **Конкурентні взаємні блокування (Deadlocks)**: Якщо одна транзакція оновлює базову таблицю `orders`, а інша паралельна транзакція вставляє нові рядки в `order_items`, обидва потоки намагатимуться одночасно захопити ексклюзивні замки на один і той самий рядок категорії в матеріалізованому представленні. Для усунення дедлоків у ядрі рушія застосовують детерміноване сортування ключів оновлення перед захопленням замків або використання неблокувальних черг дельт.
3. **Обробка каскадних видалень (Foreign Key Cascade)**: Коли замовлення видаляється з бази повністю, пов'язані позиції видаляються каскадно. Рушій IVM зобов'язаний гарантувати, що дельти видалення `order_items` будуть враховані до того, як видалиться запис із таблиці `orders`, інакше перевірка `is_paid` поверне хибний результат або спричинить розсинхронізацію агрегатного стану.
4. **Ізоляція відкотів транзакцій (Transaction Rollback)**: Якщо транзакція вставки в `orders` зазнає аварійного відкату (`ABORT / ROLLBACK`), усі згенеровані нею дельти в матеріалізованому представленні мають бути атомарно компенсовані. У реляційних рушіях це забезпечується записом дельт представлення в загальний журнал WAL разом із базовими мутаціями.
