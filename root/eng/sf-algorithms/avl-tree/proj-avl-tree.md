# ⚙️ Повна реалізація AVL-дерева мовами C та C++

У цій практичній вставці наведено повний, готовий до компіляції код реалізації AVL-дерева мовами C та C++. Обидва варіанти містять базові операції: обчислення висоти, визначення фактора балансу, малі (поодинокі) та великі (подвійні) обертання, рекурсивну вставку, видалення з каскадним балансуванням та звільнення пам'яті.

## 1. Пояснення структури та механіки мовою C

Реалізація мовою C спирається на явне керування покажчиками та динамічне виділення пам'яті через `malloc` і `free`.

Кожен вузол містить ключ, висоту піддерева та два покажчики на дітей. Висота порожнього піддерева (`NULL`) вважається рівною 0, що дозволяє безпечно обчислювати висоти та фактори балансу за допомогою статичних інлайнових функцій `get_height()` та `get_balance()`.

### Порядок оновлення висот під час обертань

Під час виконання правого або лівого обертання змінюються зв'язки лише між двома вузлами — колишнім коренем та його сином, який піднімається нагору. Критично важливо дотримуватися суворого порядку оновлення висот: **спочатку оновлюється висота вузла, який опустився вниз (колишній корінь), і лише після цього — висота нового кореня**. Порушення цього порядку призведе до збереження застарілих значень висоти та хибного обчислення фактора балансу під час подальшого підйому стеком.

### Рекурсивне видалення та симетричний наступник

Видалення вузла з двома дітьми реалізовано через пошук найменшого елемента у правому піддереві (симетричного наступника). Значення наступника скопіюється у поточний вузол, після чого здійснюється рекурсивне видалення самого наступника із правого піддерева. Оскільки наступник гарантовано має не більше одного сина (правого), його видалення зводиться до базового випадку.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

// Вузол AVL-дерева
typedef struct Node {
    int key;
    int height;
    struct Node *left;
    struct Node *right;
} Node;

// Допоміжні функції для роботи з висотою
static inline int get_height(const Node *node) {
    return node ? node->height : 0;
}

static inline int max(int a, int b) {
    return (a > b) ? a : b;
}

static inline void update_height(Node *node) {
    if (node) {
        node->height = 1 + max(get_height(node->left), get_height(node->right));
    }
}

// Фактор балансу: h(R) - h(L)
static inline int get_balance(const Node *node) {
    return node ? get_height(node->right) - get_height(node->left) : 0;
}

// Створення нового вузла
Node* create_node(int key) {
    Node *node = (Node*)malloc(sizeof(Node));
    if (!node) return NULL;
    node->key = key;
    node->height = 1;
    node->left = NULL;
    node->right = NULL;
    return node;
}

// Праве обертання навколо вузла y (LL-перекіс)
//       y                x
//      / \              / \
//     x   T3   ==>     T1  y
//    / \                  / \
//   T1  T2               T2  T3
Node* rotate_right(Node *y) {
    Node *x = y->left;
    Node *T2 = x->right;

    x->right = y;
    y->left = T2;

    update_height(y);
    update_height(x);

    return x; // Новий корінь піддерева
}

// Ліве обертання навколо вузла x (RR-перекіс)
//     x                  y
//    / \                / \
//   T1  y     ==>      x   T3
//      / \            / \
//     T2  T3         T1  T2
Node* rotate_left(Node *x) {
    Node *y = x->right;
    Node *T2 = y->left;

    y->left = x;
    x->right = T2;

    update_height(x);
    update_height(y);

    return y; // Новий корінь піддерева
}

// Відновлення балансу вузла
Node* rebalance(Node *node) {
    if (!node) return NULL;

    update_height(node);
    int balance = get_balance(node);

    // Лівий перекіс (BF <= -2)
    if (balance < -1) {
        // Якщо в лівого сина правий перекіс — виконуємо LR (попереднє ліве обертання сина)
        if (get_balance(node->left) > 0) {
            node->left = rotate_left(node->left);
        }
        return rotate_right(node);
    }

    // Правий перекіс (BF >= 2)
    if (balance > 1) {
        // Якщо в правого сина лівий перекіс — виконуємо RL (попереднє праве обертання сина)
        if (get_balance(node->right) < 0) {
            node->right = rotate_right(node->right);
        }
        return rotate_left(node);
    }

    return node; // Збалансовано
}

// Рекурсивна вставка ключа
Node* insert(Node *node, int key) {
    if (!node) return create_node(key);

    if (key < node->key) {
        node->left = insert(node->left, key);
    } else if (key > node->key) {
        node->right = insert(node->right, key);
    } else {
        return node; // Дублікати не додаються
    }

    return rebalance(node);
}

// Пошук мінімального вузла в піддереві
Node* min_value_node(Node *node) {
    Node *current = node;
    while (current && current->left != NULL) {
        current = current->left;
    }
    return current;
}

// Рекурсивне видалення ключа
Node* delete_node(Node *root, int key) {
    if (!root) return NULL;

    if (key < root->key) {
        root->left = delete_node(root->left, key);
    } else if (key > root->key) {
        root->right = delete_node(root->right, key);
    } else {
        // Вузол знайдено
        if (!root->left || !root->right) {
            Node *temp = root->left ? root->left : root->right;
            if (!temp) { // Немає дітей (листок)
                temp = root;
                root = NULL;
            } else { // Один син
                *root = *temp; // Копіюємо вміст
            }
            free(temp);
        } else {
            // Два сини: шукаємо найменший ключ у правому піддереві (наступник)
            Node *temp = min_value_node(root->right);
            root->key = temp->key;
            root->right = delete_node(root->right, temp->key);
        }
    }

    if (!root) return NULL;
    return rebalance(root);
}

// Пошук ключа
bool search(const Node *root, int key) {
    if (!root) return false;
    if (key == root->key) return true;
    if (key < root->key) return search(root->left, key);
    return search(root->right, key);
}

// Симетричний обхід (In-order traversal)
void print_in_order(const Node *root) {
    if (root) {
        print_in_order(root->left);
        printf("%d (h=%d, bf=%d) ", root->key, root->height, get_balance(root));
        print_in_order(root->right);
    }
}

// Звільнення пам'яті
void free_tree(Node *root) {
    if (root) {
        free_tree(root->left);
        free_tree(root->right);
        free(root);
    }
}

int main(void) {
    Node *root = NULL;

    int keys[] = {10, 20, 30, 40, 50, 25};
    size_t n = sizeof(keys) / sizeof(keys[0]);

    printf("Вставка елементів: ");
    for (size_t i = 0; i < n; ++i) {
        printf("%d ", keys[i]);
        root = insert(root, keys[i]);
    }
    printf("\nIn-order обхід після вставки:\n");
    print_in_order(root);
    printf("\n");

    printf("\nВидалення 30:\n");
    root = delete_node(root, 30);
    print_in_order(root);
    printf("\n");

    free_tree(root);
    return 0;
}
```
```cpp
#include <iostream>
#include <algorithm>
#include <memory>
#include <optional>
#include <initializer_list>

template <typename T>
class AVLTree {
private:
    struct Node {
        T key;
        int height{1};
        std::unique_ptr<Node> left;
        std::unique_ptr<Node> right;

        explicit Node(T val) : key(std::move(val)) {}
    };

    std::unique_ptr<Node> root_;

    static int getHeight(const std::unique_ptr<Node>& node) noexcept {
        return node ? node->height : 0;
    }

    static int getBalance(const std::unique_ptr<Node>& node) noexcept {
        return node ? getHeight(node->right) - getHeight(node->left) : 0;
    }

    static void updateHeight(Node* node) noexcept {
        if (node) {
            node->height = 1 + std::max(getHeight(node->left), getHeight(node->right));
        }
    }

    // Праве обертання (LL-перекіс)
    static std::unique_ptr<Node> rotateRight(std::unique_ptr<Node> y) {
        auto x = std::move(y->left);
        y->left = std::move(x->right);
        updateHeight(y.get());

        x->right = std::move(y);
        updateHeight(x.get());
        return x;
    }

    // Ліве обертання (RR-перекіс)
    static std::unique_ptr<Node> rotateLeft(std::unique_ptr<Node> x) {
        auto y = std::move(x->right);
        x->right = std::move(y->left);
        updateHeight(x.get());

        y->left = std::move(x);
        updateHeight(y.get());
        return y;
    }

    // Відновлення балансу
    static std::unique_ptr<Node> rebalance(std::unique_ptr<Node> node) {
        if (!node) return nullptr;

        updateHeight(node.get());
        int balance = getBalance(node);

        if (balance < -1) {
            if (getBalance(node->left) > 0) {
                node->left = rotateLeft(std::move(node->left));
            }
            return rotateRight(std::move(node));
        }

        if (balance > 1) {
            if (getBalance(node->right) < 0) {
                node->right = rotateRight(std::move(node->right));
            }
            return rotateLeft(std::move(node));
        }

        return node;
    }

    static std::unique_ptr<Node> insertImpl(std::unique_ptr<Node> node, T key) {
        if (!node) {
            return std::make_unique<Node>(std::move(key));
        }

        if (key < node->key) {
            node->left = insertImpl(std::move(node->left), std::move(key));
        } else if (key > node->key) {
            node->right = insertImpl(std::move(node->right), std::move(key));
        } else {
            return node; // Ігноруємо дублікати
        }

        return rebalance(std::move(node));
    }

    static const Node* minNode(const Node* node) noexcept {
        const Node* curr = node;
        while (curr && curr->left) {
            curr = curr->left.get();
        }
        return curr;
    }

    static std::unique_ptr<Node> removeImpl(std::unique_ptr<Node> node, const T& key) {
        if (!node) return nullptr;

        if (key < node->key) {
            node->left = removeImpl(std::move(node->left), key);
        } else if (key > node->key) {
            node->right = removeImpl(std::move(node->right), key);
        } else {
            if (!node->left) return std::move(node->right);
            if (!node->right) return std::move(node->left);

            const Node* successor = minNode(node->right.get());
            node->key = successor->key;
            node->right = removeImpl(std::move(node->right), successor->key);
        }

        return rebalance(std::move(node));
    }

    template <typename Func>
    static void inOrderImpl(const Node* node, Func&& func) {
        if (node) {
            inOrderImpl(node->left.get(), func);
            func(node->key, node->height, getBalance(node));
            inOrderImpl(node->right.get(), func);
        }
    }

public:
    AVLTree() = default;

    AVLTree(std::initializer_list<T> list) {
        for (const auto& item : list) {
            insert(item);
        }
    }

    void insert(T key) {
        root_ = insertImpl(std::move(root_), std::move(key));
    }

    void remove(const T& key) {
        root_ = removeImpl(std::move(root_), key);
    }

    [[nodiscard]] bool contains(const T& key) const noexcept {
        const Node* curr = root_.get();
        while (curr) {
            if (key == curr->key) return true;
            curr = (key < curr->key) ? curr->left.get() : curr->right.get();
        }
        return false;
    }

    template <typename Func>
    void inOrder(Func&& func) const {
        inOrderImpl(root_.get(), std::forward<Func>(func));
    }

    [[nodiscard]] int height() const noexcept {
        return getHeight(root_);
    }
};

int main() {
    AVLTree<int> tree{10, 20, 30, 40, 50, 25};

    std::cout << "In-order обхід (значення, висота, BF):\n";
    tree.inOrder([](int key, int h, int bf) {
        std::cout << key << " (h=" << h << ", bf=" << bf << ") ";
    });
    std::cout << "\n\nВисота дерева: " << tree.height() << "\n";

    std::cout << "Видаляємо 30...\n";
    tree.remove(30);

    std::cout << "Обхід після видалення:\n";
    tree.inOrder([](int key, int h, int bf) {
        std::cout << key << " (h=" << h << ", bf=" << bf << ") ";
    });
    std::cout << "\n";

    return 0;
}
```
:::

## 2. Особливості реалізації мовою C++ (RAII та семантика переміщення)

Варіант реалізації мовою C++20 у другій вкладці показує ідіоматичний підхід до написання контейнерів із використання концепції RAII (англ. *Resource Acquisition Is Initialization*).

### Автоматичне керування пам'яттю через `std::unique_ptr`

Замість сирих покажчиків та ручного виклику `free()` у C++ реалізації використовується розумний покажчик `std::unique_ptr<Node>`. Це дає такі переваги:

1. **Гарантія відсутності витоків пам'яті (Memory Leaks):** При знищенні об'єкта `AVLTree` або окремого піддерева деструктор `std::unique_ptr` автоматично та рекурсивно звільняє всі виділені вузли.
2. **Передача володіння через `std::move`:** Обертання піддерев передають володіння вузлами через семантику переміщення, що повністю виключає копіювання об'єктів та залишає покажчики у коректному стані.
3. **Універсальний шаблонний клас:** Клас `AVLTree<T>` є шаблоном, який може працювати з будь-якими типами даних `T`, що підтримують операції порівняння `<` та `>`.

### Безпека щодо винятків (Exception Safety)

Оскільки вставка виконується через `std::make_unique`, у разі виникнення винятку під час виділення пам'яті або копіювання ключа `T` стек викликів акуратно згортається, а вже створені вузли автоматично знищуються без порушення інваріанта структури даних.

## 3. Детальний простеження стеку під час вставки

Простежимо виконання вставки елементів `10, 20, 30` у порожнє AVL-дерево для демонстрації механіки балансування:

1. **Вставка 10:** Створюється корінь з `key=10, height=1`. Дерево збалансоване.
2. **Вставка 20:** Ключ 20 більший за 10, додається як правий син. Висота 10 стає 2, `BF(10) = +1`. Баланс збережено.
3. **Вставка 30:** Ключ 30 додається праворуч від 20. Стек викликів повертається до вузла 20: `height(20) = 2, BF(20) = +1`. Стек повертається до 10: `height(10) = 3`, але `BF(10) = +2` (виявлено перекіс RR!).
4. **Викликається `rebalance(10)`:** Оскільки `BF(10) = +2` та `BF(20) = +1`, виконується мале ліве обертання `rotate_left(10)`. Вузол 20 стає новим коренем, 10 — його лівим сином, 30 — правим сином. Висота нового кореня 20 стає рівною 2, а `BF(20) = 0`. Дерево знову повністю збалансоване.

## 4. Пастки реалізації та поширені дефекти

Під час програмування AVL-дерева найчастіше припускаються таких трьох помилок:

1. **Забуте оновлення висот:** Якщо у функції обертання оновити лише корінь і не оновити вузол, що опустився нижче, фактор балансу батьківських вузлів обчислиться хибно.
2. **Нехтування перевіркою `NULL`:** Спроба зчитати `node->height` без перевірки покажчика на `NULL` призводить до фатальної помилки сегментації (англ. *segmentation fault*). Допоміжна функція `get_height(const Node*)` захищає від цього.
3. **Витік пам'яті при видаленні вузла з двома дітьми:** Під час копіювання значення наступника не можна забувати рекурсивно видалити оригінальний вузол наступника зі збереженням процедури балансування.

## 5. Порівняння C та C++20 підходів до реалізації

Розглянуті два варіанти реалізації демонструють еволюцію підходів до розробки системного коду:

- **Підхід у C:** Максимальна прозорість адресної арифметики та повний контроль за розміщенням полів у пам'яті. Кожен крок перебудови покажчиків виконується явно, що корисно для розуміння низькорівневої механіки або розробки в межах системних модулів ядра.
- **Підхід у C++20:** Високий рівень абстракції без втрати продуктивності (zero-cost abstractions). Шаблонні параметри дозволяють використовувати дерево для будь-яких типів даних, а власницькі розумні покажчики `std::unique_ptr` повністю усувають ризик витоків пам'яті.

Обидві реалізації забезпечують строгу логарифмічну складність `O(log n)` для всіх основних операцій і повністю відповідають вимогам до високоефективних впорядкованих контейнерів.
