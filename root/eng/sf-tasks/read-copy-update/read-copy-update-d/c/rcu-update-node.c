#include <stdatomic.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int id;
    char name[64];
} Node;

typedef struct {
    _Atomic(Node *) global_node;
} RcuContainer;

// Функція оновлення за патерном Read-Copy-Update
void rcu_update_node(RcuContainer *container, int new_id, const char *new_name) {
    // 1. Read: отримуємо поточний вказівник
    Node *old_node = atomic_load_explicit(&container->global_node, memory_order_relaxed);
    
    // 2. Copy: виділяємо нову пам'ять та копіюємо вміст
    Node *new_node = (Node *)malloc(sizeof(Node));
    if (!new_node) return;
    if (old_node) {
        memcpy(new_node, old_node, sizeof(Node));
    }
    
    // 3. Update: модифікуємо копію в ізоляції (без замків)
    new_node->id = new_id;
    strncpy(new_node->name, new_name, sizeof(new_node->name) - 1);
    new_node->name[sizeof(new_node->name) - 1] = '\0';
    
    // 4. Publish (Atomic Swap): оновлюємо вказівник із семантикою release
    atomic_store_explicit(&container->global_node, new_node, memory_order_release);
    
    // УВАГА: Ми НЕ МОЖЕМО викликати free(old_node) прямо зараз!
    // Старі читачі все ще можуть розіменовувати old_node.
    // Тут потрібне очікування періоду відстрочки (grace period).
}
