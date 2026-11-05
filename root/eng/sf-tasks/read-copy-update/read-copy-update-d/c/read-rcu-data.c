#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdatomic.h>
#include <unistd.h>

// Вузол структури даних для RCU-управління
typedef struct {
    int id;
    int payload;
} RcuNode;

// Глобальний атомарний вказівник на актуальні дані
_Atomic(RcuNode *) global_node = NULL;

// Проста імітація RCU-критичної секції читача
void read_rcu_data(int reader_id) {
    // Вхід у секцію читача: розіменування атомарного вказівника без блокувань
    RcuNode *node = atomic_load_explicit(&global_node, memory_order_consume);
    if (node) {
        // Утримуємо посилання під час обробки
        printf("[Читач %d] Зчитано ID: %d, значення: %d\n", reader_id, node->id, node->payload);
    }
    // Вихід із критичної секції (у реальному ядрі — rcu_read_unlock())
}

// Імітація періоду відстрочки (очікування проходження quiescent state усіма ядрами)
void simulate_synchronize_rcu(void) {
    // Письменник блокується, гарантуючи, що всі активні читачі завершать виконання
    usleep(10000); // 10 мс очікування спокійного стану
}

// Функція оновлення з використанням періоду відстрочки
void update_rcu_data(int new_id, int new_payload) {
    RcuNode *old_node = atomic_load_explicit(&global_node, memory_order_relaxed);

    // 1. Створення нової версії в ізольованій пам'яті
    RcuNode *new_node = (RcuNode *)malloc(sizeof(RcuNode));
    new_node->id = new_id;
    new_node->payload = new_payload;

    // 2. Атомарна підміна вказівника (публікація)
    atomic_store_explicit(&global_node, new_node, memory_order_release);

    // 3. Очікування завершення періоду відстрочки (Grace Period)
    simulate_synchronize_rcu();

    // 4. Безпечна утилізація старого вузла після підтвердження quiescent state
    if (old_node) {
        free(old_node);
    }
}
