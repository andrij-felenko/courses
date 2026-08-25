# ⚙️ Практична реалізація HAMT мовами C та C++

У цій вставці наведено практичні реалізації геш-дерева з бітовими мапами (HAMT) двома мовами програмування: процедурною мовою C та об'єктно-орієнтованою/функційною мовою C++20. Обидва приклади демонструють повний цикл роботи структури: побітову декомпозицію 32-бітного гешу, індексацію через інструкцію `popcount`, створення динамічних компактних масивів вказівників, вирішення колізій префіксів та персистентне оновлення шляхом копіювання шляху (Path Copying).

---

## 1. Архітектурні засади та інженерні рішення

При проектуванні HAMT необхідно вирішити три основні інженерні задачі:

1. **Представлення вузлів у пам'яті:** Вузол може бути або *листовим* (зберігає ключ, геш та значення), або *внутрішнім* (зберігає бітову мапу та масив вказівників на дітей). У мові C це реалізується через теговане об'єднання (`enum NodeType` + `union`), а в мові C++ — через безпечні алгебраїчні типи або `std::optional` зі смарт-вказівниками.
2. **Динамічне змінювання розміру масиву дітей:** На відміну від звичайних дерев із фіксованою кількістю вказівників, масив `children` внутрішнього вузла HAMT має розмір `m = popcount(bitmap)`. При додаванні нової дитини створюється новий масив розміром `m + 1`, у який копіюються наявні вказівники із зсувом комірки для нового елемента.
3. **Забезпечення персистентності (Path Copying):** Щоб оновлення дерева не руйнувало попередні версії, операція вставки `insert` повертає корінь нового дерева, залишаючи початкове дерево недоторканим. Усі вузли, які не зазнали змін, перевикористовуються між версіями через покажчики (Structural Sharing).

---

## 2. Реалізація мовами C та C++

Нижче наведено паралельні реалізації HAMT. Перемикач вгорі дозволяє порівняти низькорівневе управління пам'яттю в C із сучасною RAII-автоматизацією в C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

// Алфавіт розгалуження B = 32 (5 бітів на рівень)
#define BITS_PER_LEVEL 5
#define BRANCH_FACTOR 32
#define BITMAP_MASK 0x1F

typedef enum {
    NODE_LEAF,
    NODE_BITMAP
} NodeType;

typedef struct Node Node;

typedef struct {
    char* key;
    uint32_t hash;
    int value;
} KeyValue;

typedef struct {
    uint32_t bitmap;
    Node** children;
} BitmapNode;

struct Node {
    NodeType type;
    union {
        KeyValue leaf;
        BitmapNode internal;
    } data;
};

// Некриптографічна геш-функція FNV-1a (32 біти)
uint32_t fnv1a_hash(const char* key) {
    uint32_t hash = 2166136261U;
    while (*key) {
        hash ^= (uint8_t)(*key++);
        hash *= 16777619U;
    }
    return hash;
}

// Підрахунок одиничних бітів через убудовану інструкцію CPU
static inline int popcount32(uint32_t val) {
#if defined(__GNUC__) || defined(__clang__)
    return __builtin_popcount(val);
#else
    val = val - ((val >> 1) & 0x55555555);
    val = (val & 0x33333333) + ((val >> 2) & 0x33333333);
    return (((val + (val >> 4)) & 0x0F0F0F0F) * 0x01010101) >> 24;
#endif
}

Node* create_leaf(const char* key, uint32_t hash, int value) {
    Node* node = (Node*)malloc(sizeof(Node));
    if (!node) return NULL;
    node->type = NODE_LEAF;
    node->data.leaf.key = strdup(key);
    node->data.leaf.hash = hash;
    node->data.leaf.value = value;
    return node;
}

Node* create_bitmap_node(uint32_t bitmap, Node** children, int count) {
    Node* node = (Node*)malloc(sizeof(Node));
    if (!node) return NULL;
    node->type = NODE_BITMAP;
    node->data.internal.bitmap = bitmap;
    node->data.internal.children = (Node**)malloc(sizeof(Node*) * count);
    if (count > 0 && children) {
        memcpy(node->data.internal.children, children, sizeof(Node*) * count);
    }
    return node;
}

// Пошук значення у HAMT за час O(log32 N)
bool hamt_lookup(const Node* root, const char* key, int* out_value) {
    if (!root) return false;
    uint32_t hash = fnv1a_hash(key);
    const Node* curr = root;
    uint32_t shift = 0;

    while (curr) {
        if (curr->type == NODE_LEAF) {
            if (curr->data.leaf.hash == hash && strcmp(curr->data.leaf.key, key) == 0) {
                *out_value = curr->data.leaf.value;
                return true;
            }
            return false;
        }

        uint32_t chunk = (hash >> shift) & BITMAP_MASK;
        uint32_t bit_pos = 1U << chunk;
        uint32_t bitmap = curr->data.internal.bitmap;

        if ((bitmap & bit_pos) == 0) {
            return false;
        }

        int idx = popcount32(bitmap & (bit_pos - 1));
        curr = curr->data.internal.children[idx];
        shift += BITS_PER_LEVEL;
    }
    return false;
}

// Персистентна вставка (Path Copying): повертає новий корінь, не змінюючи старий
Node* hamt_insert_internal(const Node* node, const char* key, uint32_t hash, int value, uint32_t shift) {
    if (!node) {
        return create_leaf(key, hash, value);
    }

    if (node->type == NODE_LEAF) {
        if (node->data.leaf.hash == hash && strcmp(node->data.leaf.key, key) == 0) {
            return create_leaf(key, hash, value);
        }

        uint32_t existing_chunk = (node->data.leaf.hash >> shift) & BITMAP_MASK;
        uint32_t new_chunk = (hash >> shift) & BITMAP_MASK;

        if (existing_chunk == new_chunk) {
            Node* sub_node = hamt_insert_internal(node, key, hash, value, shift + BITS_PER_LEVEL);
            uint32_t bitmap = 1U << existing_chunk;
            Node* children[1] = { sub_node };
            return create_bitmap_node(bitmap, children, 1);
        } else {
            Node* new_leaf = create_leaf(key, hash, value);
            uint32_t bitmap = (1U << existing_chunk) | (1U << new_chunk);
            Node* children[2];

            Node* copied_leaf = create_leaf(node->data.leaf.key, node->data.leaf.hash, node->data.leaf.value);
            if (existing_chunk < new_chunk) {
                children[0] = copied_leaf;
                children[1] = new_leaf;
            } else {
                children[0] = new_leaf;
                children[1] = copied_leaf;
            }
            return create_bitmap_node(bitmap, children, 2);
        }
    }

    uint32_t chunk = (hash >> shift) & BITMAP_MASK;
    uint32_t bit_pos = 1U << chunk;
    uint32_t bitmap = node->data.internal.bitmap;
    int count = popcount32(bitmap);

    if ((bitmap & bit_pos) != 0) {
        int idx = popcount32(bitmap & (bit_pos - 1));
        Node* updated_child = hamt_insert_internal(node->data.internal.children[idx], key, hash, value, shift + BITS_PER_LEVEL);

        Node** new_children = (Node**)malloc(sizeof(Node*) * count);
        for (int i = 0; i < count; i++) {
            new_children[i] = (i == idx) ? updated_child : node->data.internal.children[i];
        }
        return create_bitmap_node(bitmap, new_children, count);
    } else {
        Node* new_leaf = create_leaf(key, hash, value);
        uint32_t new_bitmap = bitmap | bit_pos;
        int idx = popcount32(bitmap & (bit_pos - 1));

        Node** new_children = (Node**)malloc(sizeof(Node*) * (count + 1));
        for (int i = 0; i < idx; i++) {
            new_children[i] = node->data.internal.children[i];
        }
        new_children[idx] = new_leaf;
        for (int i = idx; i < count; i++) {
            new_children[i + 1] = node->data.internal.children[i];
        }
        return create_bitmap_node(new_bitmap, new_children, count + 1);
    }
}

Node* hamt_insert(const Node* root, const char* key, int value) {
    uint32_t hash = fnv1a_hash(key);
    return hamt_insert_internal(root, key, hash, value, 0);
}

void hamt_free(Node* node) {
    if (!node) return;
    if (node->type == NODE_LEAF) {
        free(node->data.leaf.key);
    } else if (node->type == NODE_BITMAP) {
        int count = popcount32(node->data.internal.bitmap);
        for (int i = 0; i < count; i++) {
            hamt_free(node->data.internal.children[i]);
        }
        free(node->data.internal.children);
    }
    free(node);
}

int main(void) {
    Node* v1 = NULL;
    v1 = hamt_insert(v1, "alpha", 100);
    v1 = hamt_insert(v1, "beta", 200);

    Node* v2 = hamt_insert(v1, "alpha", 999);

    int val = 0;
    if (hamt_lookup(v1, "alpha", &val)) {
        printf("V1 ['alpha'] = %d (очікується 100)\n", val);
    }
    if (hamt_lookup(v2, "alpha", &val)) {
        printf("V2 ['alpha'] = %d (очікується 999)\n", val);
    }

    hamt_free(v1);
    hamt_free(v2);
    return 0;
}
```
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <vector>
#include <optional>
#include <cstdint>
#include <bit>

// Незмінне персистентне HAMT-дерево мовою C++20
class PersistentHAMT {
public:
    using Key = std::string;
    using Value = int;

private:
    static constexpr std::uint32_t BITS_PER_LEVEL = 5;
    static constexpr std::uint32_t BITMAP_MASK = 0x1F;

    static std::uint32_t fnv1a_hash(std::string_view key) noexcept {
        std::uint32_t hash = 2166136261U;
        for (char ch : key) {
            hash ^= static_cast<std::uint8_t>(ch);
            hash *= 16777619U;
        }
        return hash;
    }

    struct Node;
    using NodePtr = std::shared_ptr<const Node>;

    struct LeafData {
        Key key;
        std::uint32_t hash;
        Value value;
    };

    struct BitmapData {
        std::uint32_t bitmap{0};
        std::vector<NodePtr> children;
    };

    struct Node {
        enum class Type { Leaf, Bitmap } type;
        std::optional<LeafData> leaf;
        std::optional<BitmapData> bitmap_node;

        static NodePtr make_leaf(Key key, std::uint32_t hash, Value val) {
            auto n = std::make_shared<Node>();
            n->type = Type::Leaf;
            n->leaf = LeafData{std::move(key), hash, val};
            return n;
        }

        static NodePtr make_bitmap(std::uint32_t bmp, std::vector<NodePtr> children) {
            auto n = std::make_shared<Node>();
            n->type = Type::Bitmap;
            n->bitmap_node = BitmapData{bmp, std::move(children)};
            return n;
        }
    };

    NodePtr root_;

    static NodePtr insert_rec(const NodePtr& node, const Key& key, std::uint32_t hash, Value val, std::uint32_t shift) {
        if (!node) {
            return Node::make_leaf(key, hash, val);
        }

        if (node->type == Node::Type::Leaf) {
            const auto& leaf = *node->leaf;
            if (leaf.hash == hash && leaf.key == key) {
                return Node::make_leaf(key, hash, val);
            }

            std::uint32_t existing_chunk = (leaf.hash >> shift) & BITMAP_MASK;
            std::uint32_t new_chunk = (hash >> shift) & BITMAP_MASK;

            if (existing_chunk == new_chunk) {
                auto sub_node = insert_rec(node, key, hash, val, shift + BITS_PER_LEVEL);
                return Node::make_bitmap(1U << existing_chunk, {sub_node});
            } else {
                auto new_leaf = Node::make_leaf(key, hash, val);
                auto existing_leaf = Node::make_leaf(leaf.key, leaf.hash, leaf.value);
                std::uint32_t bmp = (1U << existing_chunk) | (1U << new_chunk);

                if (existing_chunk < new_chunk) {
                    return Node::make_bitmap(bmp, {existing_leaf, new_leaf});
                } else {
                    return Node::make_bitmap(bmp, {new_leaf, existing_leaf});
                }
            }
        }

        const auto& bnode = *node->bitmap_node;
        std::uint32_t chunk = (hash >> shift) & BITMAP_MASK;
        std::uint32_t bit_pos = 1U << chunk;
        std::uint32_t bmp = bnode.bitmap;

        if ((bmp & bit_pos) != 0) {
            std::size_t idx = std::popcount(bmp & (bit_pos - 1));
            auto updated_child = insert_rec(bnode.children[idx], key, hash, val, shift + BITS_PER_LEVEL);

            std::vector<NodePtr> new_children = bnode.children;
            new_children[idx] = updated_child;
            return Node::make_bitmap(bmp, std::move(new_children));
        } else {
            auto new_leaf = Node::make_leaf(key, hash, val);
            std::uint32_t new_bmp = bmp | bit_pos;
            std::size_t idx = std::popcount(bmp & (bit_pos - 1));

            std::vector<NodePtr> new_children = bnode.children;
            new_children.insert(new_children.begin() + idx, new_leaf);
            return Node::make_bitmap(new_bmp, std::move(new_children));
        }
    }

    explicit PersistentHAMT(NodePtr root) : root_(std::move(root)) {}

public:
    PersistentHAMT() = default;

    [[nodiscard]] PersistentHAMT insert(const Key& key, Value val) const {
        std::uint32_t hash = fnv1a_hash(key);
        return PersistentHAMT(insert_rec(root_, key, hash, val, 0));
    }

    [[nodiscard]] std::optional<Value> lookup(std::string_view key) const {
        if (!root_) return std::nullopt;
        std::uint32_t hash = fnv1a_hash(key);
        NodePtr curr = root_;
        std::uint32_t shift = 0;

        while (curr) {
            if (curr->type == Node::Type::Leaf) {
                const auto& leaf = *curr->leaf;
                if (leaf.hash == hash && leaf.key == key) {
                    return leaf.value;
                }
                return std::nullopt;
            }

            const auto& bnode = *curr->bitmap_node;
            std::uint32_t chunk = (hash >> shift) & BITMAP_MASK;
            std::uint32_t bit_pos = 1U << chunk;

            if ((bnode.bitmap & bit_pos) == 0) {
                return std::nullopt;
            }

            std::size_t idx = std::popcount(bnode.bitmap & (bit_pos - 1));
            curr = bnode.children[idx];
            shift += BITS_PER_LEVEL;
        }
        return std::nullopt;
    }
};

int main() {
    PersistentHAMT v1;
    v1 = v1.insert("alpha", 100);
    v1 = v1.insert("beta", 200);

    PersistentHAMT v2 = v1.insert("alpha", 999);

    if (auto val = v1.lookup("alpha")) {
        std::cout << "V1 ['alpha'] = " << *val << " (очікується 100)\n";
    }
    if (auto val = v2.lookup("alpha")) {
        std::cout << "V2 ['alpha'] = " << *val << " (очікується 999)\n";
    }
    return 0;
}
```
:::

---

## 3. Детальний аналіз реалізації та покроковий розбір алгоритму

Розглянемо ключові фрагменти реалізації та інженерні рішення, застосовані в коді.

### Покрокове розщеплення листів (Leaf Splitting)

Найскладнішим моментом при вставці в HAMT є випадок, коли алгоритм доходить до наявного листового вузла `NODE_LEAF`, але новий ключ має інше значення.

У функції `hamt_insert_internal` це обробляється наступним чином:
1. Порівнюється 5-бітний фрагмент існуючого листа `existing_chunk` із фрагментом нового ключа `new_chunk` на поточному рівні `shift`.
2. Якщо фрагменти **різні** (`existing_chunk != new_chunk`), створюється новий внутрішній вузол `NODE_BITMAP`. Його маска обчислюється як побітове «АБО»: `bitmap = (1U << existing_chunk) | (1U << new_chunk)`. Масив `children` ініціалізується двома елементами, впорядкованими за зростанням індексів бітів.
3. Якщо фрагменти **однакові** (`existing_chunk == new_chunk`), це означає колізію префіксів на даному рівні. Алгоритм рекурсивно створює новий внутрішній вузол із маскою `1U << existing_chunk` і викликає `hamt_insert_internal` для наступного рівня `shift + 5`. Рекурсія продовжується доти, доки фрагменти не розійдуться (або до досягнення повного гешу).

### Покрокове трасування вставки трьох елементів

Простежимо стан дерева на конкретному прикладі виконання функції `main()`:

1. **Вставка `"alpha"` (значення 100):**
   - Обчислюється геш `hash("alpha") = 2166136261 ^ ...`
   - Оскільки корінь був `NULL`, створюється єдиний листовий вузол `Leaf("alpha", 100)`.

2. **Вставка `"beta"` (значення 200) у версію v1:**
   - Початковий корінь був листом `"alpha"`.
   - Обчислюються фрагменти на рівні 0 (`shift = 0`): `chunk("alpha") = 13`, `chunk("beta") = 5`.
   - Фрагменти різняться (`13 != 5`). Створюється новий внутрішній вузол `Root_v1` із маскою `bitmap = (1U << 13) | (1U << 5) = 0x2020`.
   - Оскільки `5 < 13`, масив `children` має розмір 2: `children[0] = Leaf("beta", 200)`, `children[1] = Leaf("alpha", 100)`.

3. **Оновлення `"alpha"` на значення 999 у версію v2:**
   - Алгоритм обходить `Root_v1`. Фрагмент `"alpha"` дорівнює `13`.
   - Перевіряється біт `(0x2020 & (1U << 13)) != 0`. Біт присутній.
   - Обчислюється індекс: `popcount(0x2020 & ((1U << 13) - 1)) = popcount(0x0020) = 1`.
   - Алгоритм спускається в `children[1]`, де знаходиться лист `"alpha"`.
   - Створюється новий лист `Leaf("alpha", 999)`.
   - Створюється новий корінь `Root_v2` із тією ж маскою `0x2020`. Масив `children` для `v2` містить `children[0] = Root_v1.children[0]` (перевикористаний лист `"beta"`) та `children[1] = new Leaf("alpha", 999)`.
   - У результаті версія `v1` зберігає старий лист із значенням 100, а `v2` має новий лист із значенням 999, перевикористовуючи лист `"beta"`.

---

## 4. Граничні випадки та оптимізації для продакшну

При перенесенні цього коду в реальні промислові системи слід ураховувати наступні крайові випадки:

1. **Повна колізія геш-кодів (`h(K₁) == h(K₂)`):**
   Якщо два різні ключі мають абсолютно однакові геш-коди, рекурсивне розщеплення досягне глибини `shift = 30` (для 32-бітного гешу). На наступному рівні `shift = 35` подальше виділення 5-бітних фрагментів стане неможливим. Для обробки цього випадку в реальних реалізаціях створюється третій тип вузла — `CollisionNode`, який зберігає масив або зв'язаний список усіх колізійних пар ключ-значення з однаковим гешем.

2. **Оптимізація видалення (Deletion and Compaction):**
   При видаленні ключа з HAMT виконується зворотна операція: біт у `bitmap` скидається в 0, а компактний масив `children` зменшується на 1 елемент. Якщо після видалення внутрішній вузол залишається лише з одним дочірнім листом, цей внутрішній вузол стискається (Compaction) назад у поодинокий листовий вузол, усуваючи зайві рівні дерева.

3. **Локальність пам'яті та Custom Allocator:**
   Утилізація дрібних вузлів через стандартні системні функції `malloc` / `free` створює накладні витрати на заголовки блоків пам'яті (16 байтів на блок) та викликає фрагментацію. У високопродуктивних системах використовують **Arena Allocator** (виділення пам'яті великими блоками) або **Slab Allocator** для вузлів фіксованого розміру, що підвищує локальність кешу L1/L2 і прискорює створення версій у 3–5 разів.
