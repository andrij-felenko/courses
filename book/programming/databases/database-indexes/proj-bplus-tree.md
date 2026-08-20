# ⚙️ Реалізація B+дерева: вузли, розщеплення сторінок та діапазонний пошук

B+дерево є фундаментом індексів у реляційних та документоорієнтованих СУБД завдяки детермінованому логарифмічному часу пошуку, стійкості до фрагментації та можливості ефективного послідовного сканування діапазонів значень. На відміну від двійкових дерев, де кожен вузол зберігає один елемент і два покажчики, B+дерево оптимізоване під блокове читання: кожен вузол є сторінкою фіксованого розміру, що вміщує десятки або сотні ключів.

Нижче наведено робочу реалізацію B+дерева, яка моделює механізми дискових сторінок у пам'яті: структуру вузлів-маршрутизаторів, структуру листів із корисним навантаженням, алгоритм точкового пошуку за ключем, розщеплення переповнених вузлів та діапазонне сканування через листовий ланцюг.

## 1. Архітектурні інваріанти структури B+дерева

Структура B+дерева спирається на суворе розділення обов'язків між вузлами двох типів:
1. **Внутрішні вузли (Internal / Router Nodes):** не зберігають реальних даних кортежів або ідентифікаторів рядків (TID). Вони слугують виключно навігаційними дороговказами. Якщо внутрішній вузол містить `k` впорядкованих ключів-розділювачів `[K_0, K_1, ..., K_(k-1)]`, він обов'язково містить `k + 1` покажчик на дочірні вузли `[C_0, C_1, ..., C_k]`. Для будь-якого піддерева `C_i` виконується інваріант: усі ключі в `C_i` більші або рівні за `K_(i-1)` (для `i > 0`) та строго менші за `K_i` (для `i < k`).
2. **Листові вузли (Leaf Nodes):** зберігають пари `(ключ, ідентифікатор кортежу TID)` або самі рядки таблиці (у випадку кластеризованого індексу). Усі листові вузли розміщуються на однаковій глибині від кореня, що гарантує ідеальну збалансованість дерева. Листи зв'язані горизонтальними покажчиками `next` (та опціонально `prev`) у лінійний одно- чи двозв'язний список.

Параметр `ORDER` (порядок дерева) задає максимальну кількість нащадків для внутрішнього вузла. Вузол вважається переповненим, коли кількість збережених ключів досягає `ORDER`.

## 2. Механізм пошуку та розщеплення сторінок

### Пошук від кореня до листа (Tree Descent)
Пошук починається з кореневого вузла. На кожному внутрішньому рівні виконується пошук першого ключа `K_i`, для якого шуканий ключ `key < K_i`. Знайдений індекс визначає покажчик `C_i`, за яким алгоритм спускається на наступний рівень. Процес повторюється, доки не буде досягнуто листового вузла. Усередині знайденого листа виконується пошук точного збігу. Якщо ключ присутній, повертається асоційований `TID`; якщо ні — запис у таблиці відсутній.

### Розщеплення переповненого листа (Leaf Split)
Коли новий ключ вставляється в листовий вузол, де вже немає вільного місця (`num_keys == ORDER`), вузол розщеплюється:
1. Тимчасовий буфер вміщує всі наявні ключі плюс новий елемент у відсортованому порядку.
2. Створюється новий листовий вузол.
3. Перші `⌊(ORDER + 1) / 2⌋` елементів залишаються в лівому вузлі, а решта переноситься в новий правий вузол.
4. Новий лист вбудовується в горизонтальний ланцюг: `new_leaf->next = leaf->next; leaf->next = new_leaf;`.
5. Найменший ключ правого листа (перший елемент нового вузла) копіюється у батьківський вузол як новий розділювач.

### Розщеплення внутрішнього вузла (Internal Node Split)
Якщо батьківський вузол також заповнений, розщеплення поширюється вгору рекурсивно:
1. Ключі та дочірні покажчики копіюються в тимчасовий буфер.
2. Центральний (медіанний) ключ `K_median` вилучається з дочірніх вузлів і проштовхується вгору до батьківського рівня.
3. Лівий вузол отримує ключі лівіше медіани, правий — ключі правіше медіани. Покажчики на нащадків перерозподіляються між лівим і правим вузлами, а їхні покажчики `parent` оновлюються.
4. Якщо переповнюється корінь, створюється новий кореневий вузол з одним розділювальним ключем і двома нащадками. Це єдиний сценарій, за якого висота B+дерева збільшується на одиницю.

## 3. Робоча реалізація мовами C та C++

У реалізації мовою C структури використовують низькорівневе об'єднання `union` для економії пам'яті між внутрішніми та листовими вузлами. У реалізації мовою C++ використано сучасні безпечні ідіоми: шаблони за типом ключа й значення, автоматичне керування ресурсами через `std::unique_ptr`, алгоритми `std::lower_bound` і `std::upper_bound` та контейнер `std::optional` для повернення результату.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

#define BPLUS_ORDER 4

/* Ідентифікатор кортежу в купі (Tuple ID) */
typedef struct {
    uint32_t page_id;
    uint16_t offset;
} tuple_id_t;

/* Структура вузла B+дерева */
typedef struct bplus_node {
    bool is_leaf;
    int num_keys;
    int64_t keys[BPLUS_ORDER];
    union {
        struct bplus_node* children[BPLUS_ORDER + 1];
        tuple_id_t tids[BPLUS_ORDER];
    };
    struct bplus_node* next; /* Тільки для листів */
    struct bplus_node* parent;
} bplus_node_t;

typedef struct {
    bplus_node_t* root;
} bplus_tree_t;

/* Створення нового вузла */
static bplus_node_t* node_create(bool is_leaf) {
    bplus_node_t* node = (bplus_node_t*)calloc(1, sizeof(bplus_node_t));
    if (!node) return NULL;
    node->is_leaf = is_leaf;
    node->num_keys = 0;
    node->next = NULL;
    node->parent = NULL;
    return node;
}

/* Пошук листового вузла, що містить ключ */
static bplus_node_t* find_leaf(bplus_node_t* root, int64_t key) {
    if (!root) return NULL;
    bplus_node_t* curr = root;
    while (!curr->is_leaf) {
        int i = 0;
        while (i < curr->num_keys && key >= curr->keys[i]) {
            i++;
        }
        curr = curr->children[i];
    }
    return curr;
}

/* Точковий пошук за ключем */
bool bplus_find(bplus_tree_t* tree, int64_t key, tuple_id_t* out_tid) {
    if (!tree || !tree->root) return false;
    bplus_node_t* leaf = find_leaf(tree->root, key);
    for (int i = 0; i < leaf->num_keys; i++) {
        if (leaf->keys[i] == key) {
            if (out_tid) *out_tid = leaf->tids[i];
            return true;
        }
    }
    return false;
}

/* Діапазонне сканування: проходження через ланцюг next */
int bplus_range_scan(bplus_tree_t* tree, int64_t min_key, int64_t max_key,
                     tuple_id_t* results, int max_results) {
    if (!tree || !tree->root) return 0;
    bplus_node_t* leaf = find_leaf(tree->root, min_key);
    int count = 0;

    while (leaf && count < max_results) {
        for (int i = 0; i < leaf->num_keys; i++) {
            if (leaf->keys[i] >= min_key && leaf->keys[i] <= max_key) {
                results[count++] = leaf->tids[i];
                if (count >= max_results) break;
            } else if (leaf->keys[i] > max_key) {
                return count;
            }
        }
        leaf = leaf->next;
    }
    return count;
}

/* Допоміжні функції вставки та розщеплення */
static void insert_into_parent(bplus_tree_t* tree, bplus_node_t* left, int64_t key, bplus_node_t* right);

static void split_leaf(bplus_tree_t* tree, bplus_node_t* leaf, int64_t key, tuple_id_t tid) {
    bplus_node_t* new_leaf = node_create(true);
    int64_t temp_keys[BPLUS_ORDER + 1];
    tuple_id_t temp_tids[BPLUS_ORDER + 1];

    int i = 0, j = 0;
    while (i < leaf->num_keys && leaf->keys[i] < key) {
        temp_keys[j] = leaf->keys[i];
        temp_tids[j] = leaf->tids[i];
        i++; j++;
    }
    temp_keys[j] = key;
    temp_tids[j] = tid;
    j++;
    while (i < leaf->num_keys) {
        temp_keys[j] = leaf->keys[i];
        temp_tids[j] = leaf->tids[i];
        i++; j++;
    }

    int split_idx = (BPLUS_ORDER + 1) / 2;
    leaf->num_keys = split_idx;
    for (i = 0; i < split_idx; i++) {
        leaf->keys[i] = temp_keys[i];
        leaf->tids[i] = temp_tids[i];
    }

    new_leaf->num_keys = (BPLUS_ORDER + 1) - split_idx;
    for (i = 0; i < new_leaf->num_keys; i++) {
        new_leaf->keys[i] = temp_keys[split_idx + i];
        new_leaf->tids[i] = temp_tids[split_idx + i];
    }

    new_leaf->next = leaf->next;
    leaf->next = new_leaf;
    new_leaf->parent = leaf->parent;

    insert_into_parent(tree, leaf, new_leaf->keys[0], new_leaf);
}

static void insert_into_parent(bplus_tree_t* tree, bplus_node_t* left, int64_t key, bplus_node_t* right) {
    bplus_node_t* parent = left->parent;
    if (!parent) {
        /* Створення нового кореня */
        bplus_node_t* new_root = node_create(false);
        new_root->keys[0] = key;
        new_root->children[0] = left;
        new_root->children[1] = right;
        new_root->num_keys = 1;
        left->parent = new_root;
        right->parent = new_root;
        tree->root = new_root;
        return;
    }

    if (parent->num_keys < BPLUS_ORDER) {
        int i = parent->num_keys - 1;
        while (i >= 0 && parent->keys[i] > key) {
            parent->keys[i + 1] = parent->keys[i];
            parent->children[i + 2] = parent->children[i + 1];
            i--;
        }
        parent->keys[i + 1] = key;
        parent->children[i + 2] = right;
        parent->num_keys++;
        right->parent = parent;
    } else {
        /* Розщеплення внутрішнього вузла */
        bplus_node_t* new_parent = node_create(false);
        int64_t temp_keys[BPLUS_ORDER + 1];
        bplus_node_t* temp_children[BPLUS_ORDER + 2];

        int i = 0, j = 0;
        while (i < parent->num_keys && parent->keys[i] < key) {
            temp_keys[j] = parent->keys[i];
            temp_children[j] = parent->children[i];
            i++; j++;
        }
        temp_keys[j] = key;
        temp_children[j] = parent->children[i];
        temp_children[j + 1] = right;
        j++;
        while (i < parent->num_keys) {
            temp_keys[j] = parent->keys[i];
            temp_children[j + 1] = parent->children[i + 1];
            i++; j++;
        }

        int split_idx = (BPLUS_ORDER + 1) / 2;
        int64_t promote_key = temp_keys[split_idx];

        parent->num_keys = split_idx;
        for (i = 0; i < split_idx; i++) {
            parent->keys[i] = temp_keys[i];
            parent->children[i] = temp_children[i];
        }
        parent->children[split_idx] = temp_children[split_idx];

        new_parent->num_keys = BPLUS_ORDER - split_idx;
        for (i = 0; i < new_parent->num_keys; i++) {
            new_parent->keys[i] = temp_keys[split_idx + 1 + i];
            new_parent->children[i] = temp_children[split_idx + 1 + i];
            new_parent->children[i]->parent = new_parent;
        }
        new_parent->children[new_parent->num_keys] = temp_children[BPLUS_ORDER + 1];
        new_parent->children[new_parent->num_keys]->parent = new_parent;

        new_parent->parent = parent->parent;
        insert_into_parent(tree, parent, promote_key, new_parent);
    }
}

/* Вставка запису */
bool bplus_insert(bplus_tree_t* tree, int64_t key, tuple_id_t tid) {
    if (!tree) return false;
    if (!tree->root) {
        tree->root = node_create(true);
        tree->root->keys[0] = key;
        tree->root->tids[0] = tid;
        tree->root->num_keys = 1;
        return true;
    }

    bplus_node_t* leaf = find_leaf(tree->root, key);
    if (leaf->num_keys < BPLUS_ORDER) {
        int i = leaf->num_keys - 1;
        while (i >= 0 && leaf->keys[i] > key) {
            leaf->keys[i + 1] = leaf->keys[i];
            leaf->tids[i + 1] = leaf->tids[i];
            i--;
        }
        leaf->keys[i + 1] = key;
        leaf->tids[i + 1] = tid;
        leaf->num_keys++;
        return true;
    }

    split_leaf(tree, leaf, key, tid);
    return true;
}

/* Звільнення пам'яті */
static void free_node(bplus_node_t* node) {
    if (!node) return;
    if (!node->is_leaf) {
        for (int i = 0; i <= node->num_keys; i++) {
            free_node(node->children[i]);
        }
    }
    free(node);
}

void bplus_destroy(bplus_tree_t* tree) {
    if (tree) {
        free_node(tree->root);
        tree->root = NULL;
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <optional>
#include <algorithm>
#include <span>
#include <cstdint>

struct TupleId {
    uint32_t page_id{0};
    uint16_t offset{0};

    auto operator<=>(const TupleId&) const = default;
};

template <typename Key = int64_t, typename Value = TupleId, size_t Order = 4>
class BPlusTree {
    static_assert(Order >= 3, "Порядок B+дерева повинен бути щонайменше 3");

    struct Node {
        bool is_leaf{true};
        std::vector<Key> keys;
        Node* parent{nullptr};

        explicit Node(bool leaf) : is_leaf(leaf) {
            keys.reserve(Order + 1);
        }
        virtual ~Node() = default;
    };

    struct LeafNode : public Node {
        std::vector<Value> values;
        LeafNode* next{nullptr};

        LeafNode() : Node(true) {
            values.reserve(Order + 1);
        }
    };

    struct InternalNode : public Node {
        std::vector<std::unique_ptr<Node>> children;

        InternalNode() : Node(false) {
            children.reserve(Order + 2);
        }
    };

    std::unique_ptr<Node> root_;

    LeafNode* find_leaf(Node* current, const Key& key) const {
        if (!current) return nullptr;
        if (current->is_leaf) {
            return static_cast<LeafNode*>(current);
        }
        auto* internal = static_cast<InternalNode*>(current);
        auto it = std::upper_bound(internal->keys.begin(), internal->keys.end(), key);
        size_t idx = std::distance(internal->keys.begin(), it);
        return find_leaf(internal->children[idx].get(), key);
    }

    void insert_into_parent(Node* left, Key key, std::unique_ptr<Node> right) {
        Node* parent_ptr = left->parent;
        if (!parent_ptr) {
            auto new_root = std::make_unique<InternalNode>();
            new_root->keys.push_back(key);
            left->parent = new_root.get();
            right->parent = new_root.get();

            new_root->children.push_back(std::move(root_));
            new_root->children.push_back(std::move(right));
            root_ = std::move(new_root);
            return;
        }

        auto* parent = static_cast<InternalNode*>(parent_ptr);
        auto it_key = std::upper_bound(parent->keys.begin(), parent->keys.end(), key);
        size_t idx = std::distance(parent->keys.begin(), it_key);

        parent->keys.insert(it_key, key);
        right->parent = parent;
        parent->children.insert(parent->children.begin() + idx + 1, std::move(right));

        if (parent->keys.size() >= Order) {
            split_internal(parent);
        }
    }

    void split_internal(InternalNode* node) {
        auto new_node = std::make_unique<InternalNode>();
        size_t split_idx = node->keys.size() / 2;
        Key promote_key = node->keys[split_idx];

        new_node->keys.assign(node->keys.begin() + split_idx + 1, node->keys.end());
        node->keys.erase(node->keys.begin() + split_idx, node->keys.end());

        for (size_t i = split_idx + 1; i < node->children.size(); ++i) {
            node->children[i]->parent = new_node.get();
            new_node->children.push_back(std::move(node->children[i]));
        }
        node->children.erase(node->children.begin() + split_idx + 1, node->children.end());

        insert_into_parent(node, promote_key, std::move(new_node));
    }

    void split_leaf(LeafNode* leaf, Key key, Value val) {
        auto it = std::lower_bound(leaf->keys.begin(), leaf->keys.end(), key);
        size_t idx = std::distance(leaf->keys.begin(), it);
        leaf->keys.insert(it, key);
        leaf->values.insert(leaf->values.begin() + idx, val);

        auto new_leaf = std::make_unique<LeafNode>();
        size_t split_idx = leaf->keys.size() / 2;

        new_leaf->keys.assign(leaf->keys.begin() + split_idx, leaf->keys.end());
        new_leaf->values.assign(leaf->values.begin() + split_idx, leaf->values.end());

        leaf->keys.erase(leaf->keys.begin() + split_idx, leaf->keys.end());
        leaf->values.erase(leaf->values.begin() + split_idx, leaf->values.end());

        new_leaf->next = leaf->next;
        leaf->next = new_leaf.get();

        Key promote_key = new_leaf->keys.front();
        insert_into_parent(leaf, promote_key, std::move(new_leaf));
    }

public:
    BPlusTree() = default;

    [[nodiscard]] std::optional<Value> find(const Key& key) const {
        LeafNode* leaf = find_leaf(root_.get(), key);
        if (!leaf) return std::nullopt;

        auto it = std::lower_bound(leaf->keys.begin(), leaf->keys.end(), key);
        if (it != leaf->keys.end() && *it == key) {
            size_t idx = std::distance(leaf->keys.begin(), it);
            return leaf->values[idx];
        }
        return std::nullopt;
    }

    [[nodiscard]] std::vector<Value> range_scan(const Key& min_key, const Key& max_key) const {
        std::vector<Value> result;
        LeafNode* leaf = find_leaf(root_.get(), min_key);

        while (leaf) {
            for (size_t i = 0; i < leaf->keys.size(); ++i) {
                if (leaf->keys[i] >= min_key && leaf->keys[i] <= max_key) {
                    result.push_back(leaf->values[i]);
                } else if (leaf->keys[i] > max_key) {
                    return result;
                }
            }
            leaf = leaf->next;
        }
        return result;
    }

    void insert(Key key, Value val) {
        if (!root_) {
            auto leaf = std::make_unique<LeafNode>();
            leaf->keys.push_back(key);
            leaf->values.push_back(val);
            root_ = std::move(leaf);
            return;
        }

        LeafNode* leaf = find_leaf(root_.get(), key);
        if (leaf->keys.size() < Order - 1) {
            auto it = std::lower_bound(leaf->keys.begin(), leaf->keys.end(), key);
            size_t idx = std::distance(leaf->keys.begin(), it);
            leaf->keys.insert(it, key);
            leaf->values.insert(leaf->values.begin() + idx, val);
            return;
        }

        split_leaf(leaf, key, val);
    }
};
```
:::

## 4. Інженерні пастки та крайові випадки

### Монотонно зростаючі ключі та асиметричне розщеплення
У разі використання числових первинних ключів з автоматичним приростом (`AUTO_INCREMENT`, `SERIAL`, послідовності `UUIDv7`) кожен новий ключ гарантовано перевищує всі наявні значення. Якщо застосовувати класичне симетричне розщеплення навпіл (50/50 split), щойно заповнена сторінка ділиться на дві напівпорожні частини. Усі наступні вставки потраплятимуть виключно в праву половину, яка знову переповниться, а ліва сторінка назавжди залишиться заповненою лише наполовину. У результаті індекс займає вдвічі більше дискового простору, ніж необхідно.

*Як це розв'язують:* Промислові СУБД (PostgreSQL `nbtree`, InnoDB) аналізують точку вставки. Якщо новий ключ вставляється в крайню праву позицію максимальної сторінки, рушій виконує асиметричне розщеплення (90/10 або Right-Leaning Split): створюється нова порожня сторінка, куди переноситься лише один новий ключ, а попередня сторінка залишається заповненою на 100%.

### Відмінність розділювачів у внутрішніх вузлах і листах
Найпоширеніша алгоритмічна помилка полягає в однаковому поводженні з ключем розділення під час розщеплення листів та внутрішніх вузлів.
- У листовому вузлі ключ розділення **мусить залишатися** в правому листі, оскільки листи містять повний набір даних таблиці.
- У внутрішньому вузлі ключ розділення **вилучається** з обох дочірніх сторінок і переноситься суто на вищий рівень. Якщо скопіювати ключ у правий внутрішній вузол, у дереві виникнуть дублікати маршрутизації, що порушить бінарний пошук `std::upper_bound`.

### Оновлення покажчиків на батьків при переміщенні піддерев
Під час розщеплення внутрішнього вузла половина покажчиків на нащадків `children` передається новому вузлу `new_parent`. Якщо забути оновити поле `parent` у всіх переданих дочірніх вузлах (`child->parent = new_parent`), наступні операції вставки чи каскадного розщеплення на нижчих рівнях звертатимуться до застарілого батька, що призведе до розриву зв'язків у дереві та витоків пам'яті.
