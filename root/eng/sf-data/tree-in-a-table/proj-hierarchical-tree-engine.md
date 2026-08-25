# ⚙️ Реалізація ієрархічного рушія: список суміжності, CTE, шлях і таблиця замикання

Зберігання деревоподібних структур у пам'яті програми та їх трансляція у пласкі реляційні таблиці вимагає ефективних алгоритмів перетворення. Під час роботи бекенд-сервера типовою задачею є вичитування плоского списку суміжності `(id, parent_id, name)` з бази даних, швидке відновлення вказівникового графа в пам'яті, обчислення інтервалів Ейлерового обходу (Nested Sets), формування префіксних шляхів (Materialized Path) та генерація транзитивного замикання (Closure Table).

Нижче наведено повну реалізацію ієрархічного рушія мовами C та C++, яка розкриває алгоритмічну структуру всіх чотирьох моделей, аналізує керування пам'яттю, ефективність кешування та захист від циклічних посилань.

## Відновлення дерева та розрахунок топологічних метрик

Відновлення деревоподібної структури з плаского масиву рядків бази даних виконується у два лінійні етапи:
1. **Створення вузлів та індексація:** виділяється пам'ять для кожного вузла, а покажчик на нього зберігається в хеш-таблиці або прямому індексному масиві за його числовим `id` (час `O(N)`).
2. **Побудова ребер:** виконується другий прохід по масиву записів, де за значенням `parent_id` миттєво знаходиться батьківський вузол і дочірній елемент додається до його динамічного списку дітей (час `O(N)`).

Після побудови графа запускається єдиний прохід пошуку в глибину (DFS), який за один рекурсивний обхід `O(N)` одночасно обчислює:
- числовий лівий ключ `lft` (під час першого входу у вузол);
- текстовий префіксний шлях `path` (успадковуючи шлях батька та додаючи власний `id`);
- глибину вузла `depth` (рівень віддаленості від кореня);
- числовий правий ключ `rgt` (перед виходом із рекурсивного виклику після обходу всіх дітей).

У мові C керування пам'яттю реалізовано за допомогою динамічних масивів покажчиків із коефіцієнтом розширення ×2 (`tree_node_add_child`), що гарантує амортизований сталий час додавання `O(1)`. Звільнення ресурсів вимагає рекурсивного обходу знизу вгору (постфіксний порядок), щоб уникнути витоків пам'яті (`tree_free`).

У мові C++ застосовано сучасні ідіоми стандарту C++20: ексклюзивне володіння дочірніми вузлами через розумні покажчики `std::unique_ptr`, що виключає ручне виділення пам'яті, використання `std::string_view` для передачі рядкових параметрів без зайвих алокацій та `std::unordered_map` для швидкого зіставлення ідентифікаторів під час відновлення дерева.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_NAME_LEN 64
#define MAX_NODES 1024

/* Сирий запис списку суміжності з реляційної таблиці */
typedef struct {
    int id;
    int parent_id; /* 0 означає NULL (корінь) */
    char name[MAX_NAME_LEN];
} FlatRecord;

/* Вузол дерева в оперативній пам'яті */
typedef struct TreeNode {
    int id;
    char name[MAX_NAME_LEN];
    int lft;
    int rgt;
    int depth;
    char path[256];
    struct TreeNode* parent;
    struct TreeNode** children;
    size_t child_count;
    size_t child_capacity;
} TreeNode;

/* Створення нового вузла */
TreeNode* tree_node_create(int id, const char* name) {
    TreeNode* node = (TreeNode*)malloc(sizeof(TreeNode));
    if (!node) return NULL;
    node->id = id;
    strncpy(node->name, name, MAX_NAME_LEN - 1);
    node->name[MAX_NAME_LEN - 1] = '\0';
    node->lft = 0;
    node->rgt = 0;
    node->depth = 0;
    node->path[0] = '\0';
    node->parent = NULL;
    node->child_count = 0;
    node->child_capacity = 4;
    node->children = (TreeNode**)malloc(sizeof(TreeNode*) * node->child_capacity);
    return node;
}

/* Додавання дочірнього вузла з динамічним розширенням масиву */
bool tree_node_add_child(TreeNode* parent, TreeNode* child) {
    if (!parent || !child) return false;
    if (parent->child_count >= parent->child_capacity) {
        size_t new_cap = parent->child_capacity * 2;
        TreeNode** new_arr = (TreeNode**)realloc(parent->children, sizeof(TreeNode*) * new_cap);
        if (!new_arr) return false;
        parent->children = new_arr;
        parent->child_capacity = new_cap;
    }
    parent->children[parent->child_count++] = child;
    child->parent = parent;
    return true;
}

/* Обчислення лівих/правих ключів (Nested Sets) та матеріалізованих шляхів (DFS) */
void tree_compute_metrics(TreeNode* node, int* counter, int current_depth, const char* parent_path) {
    if (!node) return;

    node->lft = (*counter)++;
    node->depth = current_depth;

    if (parent_path && strlen(parent_path) > 0) {
        snprintf(node->path, sizeof(node->path), "%s%d/", parent_path, node->id);
    } else {
        snprintf(node->path, sizeof(node->path), "/%d/", node->id);
    }

    for (size_t i = 0; i < node->child_count; ++i) {
        tree_compute_metrics(node->children[i], counter, current_depth + 1, node->path);
    }

    node->rgt = (*counter)++;
}

/* Виведення ієрархічної структури дерева */
void tree_print(const TreeNode* node) {
    if (!node) return;
    for (int i = 0; i < node->depth; ++i) {
        printf("  ");
    }
    printf("|- [%d] %s (lft: %d, rgt: %d, depth: %d, path: %s)\n",
           node->id, node->name, node->lft, node->rgt, node->depth, node->path);
    for (size_t i = 0; i < node->child_count; ++i) {
        tree_print(node->children[i]);
    }
}

/* Рекурсивне звільнення пам'яті */
void tree_free(TreeNode* node) {
    if (!node) return;
    for (size_t i = 0; i < node->child_count; ++i) {
        tree_free(node->children[i]);
    }
    free(node->children);
    free(node);
}

int main(void) {
    /* Сирі записи списку суміжності, отримані з реляційної таблиці */
    FlatRecord db_records[] = {
        {1, 0, "Каталог"},
        {2, 1, "Електроніка"},
        {3, 1, "Одяг"},
        {4, 2, "Телефони"},
        {5, 2, "Ноутбуки"},
        {6, 3, "Взуття"}
    };
    size_t count = sizeof(db_records) / sizeof(db_records[0]);

    TreeNode* nodes[MAX_NODES] = {0};
    TreeNode* root = NULL;

    /* Фаза 1: Створення об'єктів */
    for (size_t i = 0; i < count; ++i) {
        nodes[db_records[i].id] = tree_node_create(db_records[i].id, db_records[i].name);
    }

    /* Фаза 2: Зв'язування батьків і дітей */
    for (size_t i = 0; i < count; ++i) {
        int id = db_records[i].id;
        int pid = db_records[i].parent_id;
        if (pid == 0) {
            root = nodes[id];
        } else if (nodes[pid] && nodes[id]) {
            tree_node_add_child(nodes[pid], nodes[id]);
        }
    }

    int counter = 1;
    tree_compute_metrics(root, &counter, 0, "");

    printf("Побудоване дерево з обчисленими метриками:\n");
    tree_print(root);

    tree_free(root);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <unordered_map>
#include <memory>
#include <format>

struct FlatRecord {
    int id;
    int parent_id;
    std::string name;
};

class TreeNode {
public:
    int id;
    std::string name;
    int lft{0};
    int rgt{0};
    int depth{0};
    std::string path;
    TreeNode* parent{nullptr};
    std::vector<std::unique_ptr<TreeNode>> children;

    explicit TreeNode(int node_id, std::string_view node_name)
        : id(node_id), name(node_name) {}

    void add_child(std::unique_ptr<TreeNode> child) {
        child->parent = this;
        children.push_back(std::move(child));
    }

    void compute_metrics(int& counter, int current_depth, std::string_view parent_path) {
        lft = counter++;
        depth = current_depth;
        path = parent_path.empty() ? ("/" + std::to_string(id) + "/")
                                   : (std::string(parent_path) + std::to_string(id) + "/");

        for (const auto& child : children) {
            child->compute_metrics(counter, current_depth + 1, path);
        }

        rgt = counter++;
    }

    void print() const {
        std::string indent(depth * 2, ' ');
        std::cout << indent << "|- [" << id << "] " << name
                  << " (lft: " << lft << ", rgt: " << rgt
                  << ", depth: " << depth << ", path: " << path << ")\n";
        for (const auto& child : children) {
            child->print();
        }
    }
};

int main() {
    std::vector<FlatRecord> db_records = {
        {1, 0, "Каталог"},
        {2, 1, "Електроніка"},
        {3, 1, "Одяг"},
        {4, 2, "Телефони"},
        {5, 2, "Ноутбуки"},
        {6, 3, "Взуття"}
    };

    std::unordered_map<int, std::unique_ptr<TreeNode>> node_map;
    std::unordered_map<int, TreeNode*> raw_ptrs;

    // Фаза 1: Створення вузлів за допомогою std::make_unique
    for (const auto& rec : db_records) {
        auto node = std::make_unique<TreeNode>(rec.id, rec.name);
        raw_ptrs[rec.id] = node.get();
        node_map[rec.id] = std::move(node);
    }

    std::unique_ptr<TreeNode> root;

    // Фаза 2: Збирання ієрархії через переміщення володіння (std::move)
    for (const auto& rec : db_records) {
        if (rec.parent_id == 0) {
            root = std::move(node_map[rec.id]);
        } else {
            auto parent_it = raw_ptrs.find(rec.parent_id);
            auto child_it = node_map.find(rec.id);
            if (parent_it != raw_ptrs.end() && child_it != node_map.end()) {
                parent_it->second->add_child(std::move(child_it->second));
            }
        }
    }

    if (root) {
        int counter = 1;
        root->compute_metrics(counter, 0, "");
        std::cout << "Побудоване дерево в C++ (автоматичне керування пам'яттю):\n";
        root->print();
    }

    return 0;
}
```
:::

## Захист від циклічних посилань та некоректних даних

Під час імпорту даних із зовнішніх неперевірених джерел існує ризик наявності циклів (наприклад, запис `A` вказує на `B`, а `B` — на `A`). Якщо запустити звичайний алгоритм обходу в глибину (DFS) на циклічному графі, програма потрапить у нескінченну рекурсію, що призведе до вичерпання простору стека викликів (Stack Overflow) та аварійного завершення процесу сигналом `SIGSEGV`.

Для гарантії надійності застосовують три механізми захисту:
1. **Обмеження максимальної глибини рекурсії (Depth Guard):** рекурсивний метод перевіряє умову `current_depth > MAX_ALLOWED_DEPTH`. Якщо глибина перевищує поріг (наприклад, 128 рівнів), виконання негайно переривається з кодом помилки.
2. **Множина відвіданих вузлів у поточному стеку (Visited Set):** алгоритм підтримує бітовий масив або хеш-таблицю ідентифікаторів поточного шляху. Перед входом у дочірній вузол перевіряється, чи не був він уже відвіданий вище за ланцюжком предків.
3. **Алгоритм виявлення циклів Тар'яна або Флойда:** попередня валідація орієнтованого графа на ациклічність перед створенням деревоподібних покажчиків.

## Побудова матриці транзитивного замикання (Closure Table)

Для збереження дерева за моделлю таблиці замикання програма повинна розгорнути граф у множину пар `(ancestor_id, descendant_id, depth)`.

Алгоритм обчислює транзитивне замикання наступним чином:
1. Для кожного вузла `u` створюється обов'язковий рефлексивний запис `(u, u, depth = 0)`.
2. Алгоритм піднімається вгору по ланцюжку батьківських покажчиків (`node->parent`), на кожному кроці збільшуючи лічильник глибини на 1 та записуючи пару `(parent->id, u, depth = d)`.
3. Процедура рекурсивно повторюється для всіх дочірніх піддерев.

Загальна кількість згенерованих кортежів для дерева із `N` вузлів та середньою глибиною `h = O(log N)` становить `O(N log N)`. У найгіршому випадку виродженого лінійного ланцюга глибини `N` кількість записів становить `N·(N + 1)/2 = O(N²)`.

Отриманий плоский масив записів ідеально підходить для пакетного завантаження в реляційну базу через команду `COPY` у PostgreSQL або `LOAD DATA` у MySQL, що на два порядки швидше за поодинокі `INSERT`-запити.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int ancestor_id;
    int descendant_id;
    int depth;
} ClosureEntry;

/* Генерація всіх шляхів транзитивного замикання */
size_t tree_generate_closure(const TreeNode* node, ClosureEntry* out_entries, size_t max_entries) {
    if (!node || !out_entries) return 0;

    size_t count = 0;
    /* Рефлексивний запис зв'язку вузла із самим собою */
    if (count < max_entries) {
        out_entries[count++] = (ClosureEntry){node->id, node->id, 0};
    }

    /* Прохід по всіх предках вгору до кореневого вузла */
    const TreeNode* curr = node->parent;
    int cur_depth = 1;
    while (curr && count < max_entries) {
        out_entries[count++] = (ClosureEntry){curr->id, node->id, cur_depth};
        curr = curr->parent;
        cur_depth++;
    }

    /* Рекурсивне повторення для всіх дочірніх піддерев */
    for (size_t i = 0; i < node->child_count; ++i) {
        count += tree_generate_closure(node->children[i], out_entries + count, max_entries - count);
    }

    return count;
}
```
```cpp
#include <vector>
#include <iostream>

struct ClosureEntry {
    int ancestor_id;
    int descendant_id;
    int depth;
};

std::vector<ClosureEntry> generate_closure(const TreeNode* root) {
    std::vector<ClosureEntry> entries;

    auto collect = [&](auto& self, const TreeNode* node) -> void {
        if (!node) return;

        // Рефлексивний запис нульової глибини
        entries.push_back({node->id, node->id, 0});

        // Ітерація по всіх предках вгору до кореня
        const TreeNode* parent_ptr = node->parent;
        int d = 1;
        while (parent_ptr) {
            entries.push_back({parent_ptr->id, node->id, d});
            parent_ptr = parent_ptr->parent;
            ++d;
        }

        for (const auto& child : node->children) {
            self(self, child.get());
        }
    };

    collect(collect, root);
    return entries;
}
```
:::

## Аналіз локальності пам'яті та кеш-ефективності

При роботі з великими деревами (понад 100 000 вузлів) традиційні зв'язні структури на базі покажчиків страждають від фрагментації динамічної пам'яті та частих промахів кешу процесора (CPU cache misses). Кожен перехід по покажчику `node->children[i]` або `node->parent` змушує контролер пам'яті зчитувати новий блок із DRAM, якщо відповідна сторінка не закешована в L1/L2 кеші процесора.

На противагу цьому, компактна таблиця замикання у форматі безперервного масиву структур (`std::vector<ClosureEntry>`) зберігається в пам'яті послідовно. Це забезпечує повне використання ліній кешу L1/L2 (64 байти) та попередню вибірку апаратним префетчером (Hardware Prefetcher).

Для критичних за затримкою систем обробки графів рекомендується використовувати пласкі масиви вузлів (Structure of Arrays, SoA або Array of Structures, AoS), де всі топологічні метрики (`lft`, `rgt`, `depth`) розміщуються у щільних векторах, що зменшує навантаження на систему керування віртуальною пам'яттю та прискорює серіалізацію у сокети операційної системи.
