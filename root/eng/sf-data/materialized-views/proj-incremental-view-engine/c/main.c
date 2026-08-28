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
