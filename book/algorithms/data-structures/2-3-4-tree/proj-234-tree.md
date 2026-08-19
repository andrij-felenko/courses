# ⚙️ Реалізація 2-3-4 дерева на C та C++

2-3-4 дерево реалізує структуру самоврівноваженого багатошляхового пошуку за допомогою вузлів змінного логічного розміру. Головною алгоритмічною перевагою цієї структури є однопрохідна вставка зверху вниз (Top-Down Insertion): розщеплення переповнених 4-вузлів виконується безпосередньо під час спуску від кореня до листка. Це повністю усуває необхідність збереження стека батьківських вузлів або використання зворотних вказівників.

Нижче наведено повну архітектурну концепцію, детальний розбір кожної функції та робочу програмну реалізацію 2-3-4 дерева двома мовами: чистою мовою C з ручним керуванням пам'яттю та ідіоматичною мовою C++ з використанням шаблонів, семантики переміщення RAII та розумних вказівників `std::unique_ptr`.

---

## Архітектура та організація пам'яті вузла

При проектуванні вузла 2-3-4 дерева в оперативній пам'яті виникає вибір між двома підходами до розміщення даних:
1. **Динамічний вузол:** виділення масивів ключів та вказівників точного розміру під час кожної зміни ємності (1, 2 або 3 елементи). Такий підхід мінімізує обсяг пам'яті, але створює неприйнятний оверхед через часті виклики системного алокатора пам'яті (`malloc`/`free`) та фрагментацію купи.
2. **Фіксований вузол:** виділення фіксованого буфера максимальної ємності (на 3 ключі та 4 вказівники) безпосередньо в тілі структури вузла. Зміна типу вузла (2-вузол ↔ 3-вузол ↔ 4-вузол) здійснюється простою зміною числового лічильника `num_keys` без жодних повторних алокацій пам'яті.

У високоефективних системах обирають саме фіксовану модель, оскільки вона забезпечує безперервне розташування ключів у кеш-лінії процесора та нульову затримку при локальних трансформаціях.

Структура вузла містить три ключові компоненти:
- `num_keys`: цілочисельний лічильник кількості дійсних ключів, що зараз зберігаються у вузлі (`1`, `2` або `3`).
- `keys[3]`: неперервний статичний масив ключів, які завжди підтримуються у строго відсортованому порядку (`keys[0] < keys[1] < keys[2]`).
- `children[4]`: масив вказівників на дочірні вузли. Якщо вузол є внутрішнім, кількість активних вказівників дорівнює `num_keys + 1`. Якщо вузол є листком, усі елементи масиву `children` містять значення `NULL` (або `nullptr` у C++).

---

## Детальний розбір алгоритмів

### 1. Перевірка листового вузла (`is_leaf`)

Вузол є листком тоді й лише тоді, коли його перший дочірній вказівник `children[0]` є порожнім. Оскільки 2-3-4 дерево володіє абсолютно однаковою глибиною всіх листків, ситуація, за якої частина вказівників існує, а частина є порожніми, неможлива. Достатньо однієї перевірки `children[0] == NULL`.

### 2. Превентивне розщеплення дочірнього вузла (`split_child`)

Функція `split_child(parent, child_idx)` є фундаментальним будівельним блоком балансування. Вона приймає батьківський вузол `parent` та індекс `child_idx` його дитини, яка гарантовано є 4-вузлом (`num_keys == 3`).

Операція виконує такі послідовні дії:
1. Створюється новий вузол `right_sibling` (майбутній правий брат).
2. Із переповненого вузла `child` (що містить ключі `[K0, K1, K2]`):
   - Ключ `K0` залишається у вузлі `child`, а його лічильник встановлюється у `num_keys = 1` (він стає 2-вузлом).
   - Ключ `K2` записується у `right_sibling->keys[0]`, а його лічильник встановлюється у `num_keys = 1` (він стає другим 2-вузлом).
   - Ключ `K1` (медіана) готується до переміщення у батьківський вузол `parent`.
3. Якщо `child` не був листком, його чотири дочірні піддерева перерозподіляються:
   - Вказівники `children[0]` та `children[1]` залишаються у вузлі `child`.
   - Вказівники `children[2]` та `children[3]` переміщуються у `right_sibling->children[0]` та `right_sibling->children[1]`.
   - Старі комірки `child->children[2]` і `child->children[3]` занулюються.
4. У батьківському вузлі `parent` звільняється місце під новий ключ та новий вказівник:
   - Усі дочірні вказівники від індексу `parent->num_keys` вниз до `child_idx + 1` зсуваються вправо на одну позицію.
   - На звільнене місце `parent->children[child_idx + 1]` записується вказівник на `right_sibling`.
   - Усі ключі батька від індексу `parent->num_keys - 1` вниз до `child_idx` зсуваються вправо на одну позицію.
   - На звільнене місце `parent->keys[child_idx]` записується медіанний ключ `K1`.
   - Лічильник батька збільшується: `parent->num_keys++`.

Оскільки батько перед викликом цієї процедури гарантовано містив не більше ніж 2 ключі, зсув масивів та додавання одного елемента ніколи не виходять за межі виділеної пам'яті.

### 3. Низхідна вставка у непереповнений вузол (`insert_non_full`)

Функція `insert_non_full(node, key)` реалізує рекурсивний або ітеративний спуск по дереву за умови, що поточний вузол `node` гарантовано не є 4-вузлом:

1. **Якщо `node` є листком:**
   - Алгоритм знаходить правильну позицію для нового ключа, переглядаючи масив `keys` справа наліво.
   - Усі ключі, більші за `key`, зсуваються на одну позицію вправо.
   - Новий ключ записується у звільнену комірку, а лічильник `num_keys` інкрементується. Вставка завершена.
2. **Якщо `node` є внутрішнім вузлом:**
   - Алгоритм визначає індекс піддерева `i`, в яке необхідно перейти для продовження пошуку (знаходить перше `i`, де `key < keys[i]`, або обирає останній вказівник, якщо ключ більший за всі наявні).
   - **Критичний крок превентивності:** перевіряється дочірній вузол `node->children[i]`. Якщо він є 4-вузлом (`num_keys == 3`), алгоритм негайно викликає `split_child(node, i)`.
   - Після розщеплення медіанний ключ піднявся у поточний вузол `node`, розділивши стару дитину на дві нові. Алгоритм порівнює `key` зі щойно доданим розділовим ключем `node->keys[i]`, щоб уточнити, в якого з двох нових 2-вузлів (лівого `i` чи правого `i + 1`) необхідно спускатися.
   - Виконується рекурсивний перехід у обране дочірнє піддерево: `insert_non_full(node->children[i], key)`.

### 4. Головна точка входу вставки (`tree_insert`)

Функція `tree_insert` обробляє граничні випадки дерева загалом:
1. Якщо дерево порожнє (`root == NULL`), створюється кореневий 2-вузол із доданим ключем.
2. Якщо корінь уже існує і є 4-вузлом (`root->num_keys == 3`), дерево має зрости у висоту:
   - Створюється новий порожній вузол `new_root`.
   - Старий корінь стає першою дитиною: `new_root->children[0] = root`.
   - Викликається `split_child(new_root, 0)`, внаслідок чого старий корінь ділиться на два 2-вузли, а його медіана стає єдиним ключем нового кореня.
   - Глобальний вказівник оновлюється: `root = new_root`.
3. Викликається `insert_non_full(root, key)`.

---

## Програмний код мовами C та C++

Нижче наведено закінчену реалізацію, готову до компіляції та використання у реальних проектах.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MAX_KEYS 3
#define MAX_CHILDREN 4

typedef struct Node234 {
    int num_keys;
    int keys[MAX_KEYS];
    struct Node234* children[MAX_CHILDREN];
} Node234;

typedef struct {
    Node234* root;
} Tree234;

/* Створення нового вузла з нульовими вказівниками */
static Node234* node_create(void) {
    Node234* node = (Node234*)malloc(sizeof(Node234));
    if (!node) return NULL;
    node->num_keys = 0;
    for (int i = 0; i < MAX_CHILDREN; i++) {
        node->children[i] = NULL;
    }
    return node;
}

/* Перевірка, чи є вузол листком */
static bool node_is_leaf(const Node234* node) {
    return node->children[0] == NULL;
}

/* Превентивне розщеплення дочірнього 4-вузла */
static void node_split_child(Node234* parent, int child_idx) {
    Node234* child = parent->children[child_idx];
    Node234* right_sibling = node_create();
    if (!right_sibling) return;

    /* child: [keys[0], keys[1], keys[2]]
       keys[1] піднімається в parent.
       child стає 2-вузлом з keys[0].
       right_sibling стає 2-вузлом з keys[2]. */
    right_sibling->num_keys = 1;
    right_sibling->keys[0] = child->keys[2];

    if (!node_is_leaf(child)) {
        right_sibling->children[0] = child->children[2];
        right_sibling->children[1] = child->children[3];
        child->children[2] = NULL;
        child->children[3] = NULL;
    }

    child->num_keys = 1;

    /* Зсув дочірніх вказівників у батькові вправо */
    for (int i = parent->num_keys; i > child_idx; i--) {
        parent->children[i + 1] = parent->children[i];
    }
    parent->children[child_idx + 1] = right_sibling;

    /* Зсув ключів у батькові вправо */
    for (int i = parent->num_keys - 1; i >= child_idx; i--) {
        parent->keys[i + 1] = parent->keys[i];
    }
    parent->keys[child_idx] = child->keys[1];
    parent->num_keys++;
}

/* Вставка у піддерево за умови, що поточний вузол не є 4-вузлом */
static void node_insert_non_full(Node234* node, int key) {
    int i = node->num_keys - 1;

    if (node_is_leaf(node)) {
        /* Зсув ключів для вставки нового значення у відсортованому порядку */
        while (i >= 0 && key < node->keys[i]) {
            node->keys[i + 1] = node->keys[i];
            i--;
        }
        node->keys[i + 1] = key;
        node->num_keys++;
    } else {
        /* Пошук піддерева для спуску */
        while (i >= 0 && key < node->keys[i]) {
            i--;
        }
        i++;

        /* Якщо дитина на шляху є 4-вузлом — превентивно розщеплюємо її */
        if (node->children[i]->num_keys == MAX_KEYS) {
            node_split_child(node, i);
            if (key > node->keys[i]) {
                i++;
            }
        }
        node_insert_non_full(node->children[i], key);
    }
}

/* Ініціалізація порожнього дерева */
void tree_init(Tree234* tree) {
    tree->root = NULL;
}

/* Вставка ключа у 2-3-4 дерево */
void tree_insert(Tree234* tree, int key) {
    if (tree->root == NULL) {
        tree->root = node_create();
        if (!tree->root) return;
        tree->root->keys[0] = key;
        tree->root->num_keys = 1;
        return;
    }

    /* Якщо корінь заповнений — розщеплюємо його і збільшуємо висоту */
    if (tree->root->num_keys == MAX_KEYS) {
        Node234* new_root = node_create();
        if (!new_root) return;
        new_root->children[0] = tree->root;
        node_split_child(new_root, 0);
        tree->root = new_root;
    }

    node_insert_non_full(tree->root, key);
}

/* Пошук ключа у 2-3-4 дереві */
bool tree_search(const Tree234* tree, int key) {
    Node234* curr = tree->root;
    while (curr != NULL) {
        int i = 0;
        while (i < curr->num_keys && key > curr->keys[i]) {
            i++;
        }
        if (i < curr->num_keys && key == curr->keys[i]) {
            return true;
        }
        if (node_is_leaf(curr)) {
            break;
        }
        curr = curr->children[i];
    }
    return false;
}

/* Рекурсивне звільнення пам'яті вузлів */
static void node_destroy(Node234* node) {
    if (!node) return;
    for (int i = 0; i <= node->num_keys; i++) {
        node_destroy(node->children[i]);
    }
    free(node);
}

/* Знищення дерева */
void tree_destroy(Tree234* tree) {
    node_destroy(tree->root);
    tree->root = NULL;
}

/* Симетричний обхід для друку ключів у зростаючому порядку */
static void node_print_inorder(const Node234* node) {
    if (!node) return;
    for (int i = 0; i < node->num_keys; i++) {
        node_print_inorder(node->children[i]);
        printf("%d ", node->keys[i]);
    }
    node_print_inorder(node->children[node->num_keys]);
}

void tree_print(const Tree234* tree) {
    node_print_inorder(tree->root);
    printf("\n");
}
```
```cpp
#include <iostream>
#include <memory>
#include <array>
#include <optional>
#include <algorithm>
#include <utility>

template <typename KeyType>
class Tree234 {
private:
    static constexpr size_t MAX_KEYS = 3;
    static constexpr size_t MAX_CHILDREN = 4;

    struct Node {
        size_t num_keys = 0;
        std::array<KeyType, MAX_KEYS> keys{};
        std::array<std::unique_ptr<Node>, MAX_CHILDREN> children{};

        [[nodiscard]] bool is_leaf() const noexcept {
            return children[0] == nullptr;
        }
    };

    std::unique_ptr<Node> root_;

    /* Превентивне розщеплення дитини parent->children[child_idx] */
    void split_child(Node* parent, size_t child_idx) {
        auto child = parent->children[child_idx].get();
        auto right_sibling = std::make_unique<Node>();

        right_sibling->num_keys = 1;
        right_sibling->keys[0] = std::move(child->keys[2]);

        if (!child->is_leaf()) {
            right_sibling->children[0] = std::move(child->children[2]);
            right_sibling->children[1] = std::move(child->children[3]);
        }

        child->num_keys = 1;

        /* Зсув вказівників у батьківському вузлі */
        for (size_t i = parent->num_keys; i > child_idx; --i) {
            parent->children[i + 1] = std::move(parent->children[i]);
        }
        parent->children[child_idx + 1] = std::move(right_sibling);

        /* Зсув ключів у батьківському вузлі */
        for (size_t i = parent->num_keys; i > child_idx; --i) {
            parent->keys[i] = std::move(parent->keys[i - 1]);
        }
        parent->keys[child_idx] = std::move(child->keys[1]);
        parent->num_keys++;
    }

    /* Вставка у піддерево неповного вузла */
    void insert_non_full(Node* node, KeyType key) {
        int i = static_cast<int>(node->num_keys) - 1;

        if (node->is_leaf()) {
            while (i >= 0 && key < node->keys[i]) {
                node->keys[i + 1] = std::move(node->keys[i]);
                --i;
            }
            node->keys[i + 1] = std::move(key);
            node->num_keys++;
        } else {
            while (i >= 0 && key < node->keys[i]) {
                --i;
            }
            size_t next_idx = static_cast<size_t>(i + 1);

            if (node->children[next_idx]->num_keys == MAX_KEYS) {
                split_child(node, next_idx);
                if (key > node->keys[next_idx]) {
                    next_idx++;
                }
            }
            insert_non_full(node->children[next_idx].get(), std::move(key));
        }
    }

    void print_inorder(const Node* node) const {
        if (!node) return;
        for (size_t i = 0; i < node->num_keys; ++i) {
            print_inorder(node->children[i].get());
            std::cout << node->keys[i] << " ";
        }
        print_inorder(node->children[node->num_keys].get());
    }

public:
    Tree234() = default;
    ~Tree234() = default;

    /* Заборона копіювання, дозвіл переміщення */
    Tree234(Tree234&&) noexcept = default;
    Tree234& operator=(Tree234&&) noexcept = default;
    Tree234(const Tree234&) = delete;
    Tree234& operator=(const Tree234&) = delete;

    /* Вставка нового ключа */
    void insert(KeyType key) {
        if (!root_) {
            root_ = std::make_unique<Node>();
            root_->keys[0] = std::move(key);
            root_->num_keys = 1;
            return;
        }

        if (root_->num_keys == MAX_KEYS) {
            auto new_root = std::make_unique<Node>();
            new_root->children[0] = std::move(root_);
            split_child(new_root.get(), 0);
            root_ = std::move(new_root);
        }

        insert_non_full(root_.get(), std::move(key));
    }

    /* Пошук ключа за константний час на рівень */
    [[nodiscard]] bool contains(const KeyType& key) const noexcept {
        const Node* curr = root_.get();
        while (curr != nullptr) {
            size_t i = 0;
            while (i < curr->num_keys && key > curr->keys[i]) {
                ++i;
            }
            if (i < curr->num_keys && key == curr->keys[i]) {
                return true;
            }
            if (curr->is_leaf()) {
                break;
            }
            curr = curr->children[i].get();
        }
        return false;
    }

    /* Вивід відсортованого вмісту */
    void print() const {
        print_inorder(root_.get());
        std::cout << "\n";
    }
};
```
:::

---

## Типові підводні камені та крайові випадки

1. **Неправильний порядок зсуву елементів масиву:** При вставці ключа в середину вузла елементи масивів `keys` та `children` необхідно зсувати строго **справа наліво** (від кінця масиву до індексу вставки). Якщо виконувати зсув зліва направо, комірка `keys[i+1]` буде перезаписана значенням `keys[i]`, після чого наступний крок зсуне вже скопійоване значення, що призведе до повного спотворення вмісту вузла.
2. **Втрата вказівників на внутрішні піддерева при розщепленні:** При розщепленні 4-вузла, який є внутрішньою вершиною (не листком), необхідно обов'язково перенести вказівники `children[2]` і `children[3]` у новий вузол `right_sibling` як його `children[0]` і `children[1]`. Якщо забути виконати цю умову або застосувати логіку листового вузла, два з чотирьох піддерев безповоротно втратяться, що створить витік пам'яті та зламає цілісність індексу.
3. **Оновлення вказівника на корінь при його розщепленні:** Коли розщеплюється кореневий вузол, старий корінь стає першою дитиною нового кореня, після чого викликається `split_child`. Якщо алгоритм не перепризначить головний вказівник `tree->root = new_root`, дерево продовжить посилатися на стару, наполовину спустошену вершину, втративши другу половину ключів та новий корінь.
4. **Вибір правильного напрямку спуску після спліту:** Після того як функція `split_child` розділила дочірній вузол `children[i]` і підняла новий ключ у позицію `keys[i]` поточного вузла, алгоритм повинен повторно порівняти ключ вставки `key` із цим новим `keys[i]`. Якщо `key > keys[i]`, спуск необхідно продовжувати не у `children[i]`, а у новоствореного правого брата `children[i + 1]`. Пропуск цього порівняння призведе до вставки ключа у хибне піддерево з порушенням симетричного порядку.
