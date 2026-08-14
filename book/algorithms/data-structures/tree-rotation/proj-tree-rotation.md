# ⚙️ Реалізація повертань дерев у C та C++

Поворот двійкового дерева — це строго локальна операція над вказівниками, що виконується за сталий час `O(1)`. Проте на практиці саме ця операція стає джерелом найнебезпечніших системних помилок: витоків пам'яті, розриву батьківських зв'язків, пошкодження інваріантів дерева та нескінченних циклів при обході. У цьому розділі ми детально розберемо створення коректних, захищених реалізацій поодиноких і подвійних повертань мовами C та C++, розглянемо їхню інтеграцію у збалансоване AVL-дерево та проаналізуємо роботу з пам'яттю на рівні компілятора.

## 1. Модель вузла з батьківськими вказівниками та метаданими

Для виконання повертань та підтримки збалансованості вузол дерева повинен зберігати не лише ключ і вказівники на дітей (`left`, `right`), а й вказівник на батьківський вузол (`parent`) та обчислювальні метадані (висоту `height` або розмір піддерева `size`).

Розглянемо оголошення структури вузла та допоміжних функцій оновлення метаданих у C та C++.

Вузол дерева у пам'яті представляє собою суцільний блок байтів. У мові C для 64-бітної архітектури структура містить ключ `key` (4 байти), висоту `height` (4 байти) та три вказівники `left`, `right`, `parent` по 8 байтів кожен. Разом структура займає 32 байти пам'яті, що ідеально лягає у половину стандартної 64-байтної кеш-лінії процесора.

У мові C++ ми застосовуємо шаблони `template <typename T>`, що дозволяє створювати двійкові дерева для довільних типів даних. Для обробки нульових вказівників написані безпечні функції-хелпери `get_height()` та `get_balance_factor()`, які запобігають розіменуванню `nullptr`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <assert.h>

/**
 * @brief Структура вузла двійкового дерева з батьківським вказівником.
 */
typedef struct Node {
    int key;
    int height;
    struct Node *left;
    struct Node *right;
    struct Node *parent;
} Node;

/* Створення нового вузла в динамічній пам'яті */
Node* create_node(int key) {
    Node* node = (Node*)malloc(sizeof(Node));
    if (!node) {
        perror("Не вдалося виділити пам'ять під Node");
        return NULL;
    }
    node->key = key;
    node->height = 1;
    node->left = NULL;
    node->right = NULL;
    node->parent = NULL;
    return node;
}

/* Безпечне зчитування висоти вузла (обробляє NULL) */
int get_height(const Node* node) {
    return node ? node->height : 0;
}

/* Обчислення фактора балансу: height(right) - height(left) */
int get_balance_factor(const Node* node) {
    return node ? get_height(node->right) - get_height(node->left) : 0;
}

/* Оновлення висоти вузла на основі актуальних висот дітей */
void update_height(Node* node) {
    if (node) {
        int lh = get_height(node->left);
        int rh = get_height(node->right);
        node->height = (lh > rh ? lh : rh) + 1;
    }
}
```
```cpp
#include <iostream>
#include <memory>
#include <algorithm>
#include <cassert>

template <typename T>
struct Node {
    T key;
    int height{1};
    Node* left{nullptr};
    Node* right{nullptr};
    Node* parent{nullptr};

    explicit Node(T val) : key(std::move(val)) {}
};

template <typename T>
int get_height(const Node<T>* node) noexcept {
    return node ? node->height : 0;
}

template <typename T>
int get_balance_factor(const Node<T>* node) noexcept {
    return node ? get_height(node->right) - get_height(node->left) : 0;
}

template <typename T>
void update_height(Node<T>* node) noexcept {
    if (node) {
        node->height = std::max(get_height(node->left), get_height(node->right)) + 1;
    }
}
```
:::

## 2. Повнофункціональна реалізація поодиноких повертань

При виконанні правого повороту `rotate_right(x)` навколо вузла `x`:
1. Лівий син `y = x->left` піднімається на місце `x`.
2. Правий син `y` (піддерево `B`) переходить у ліве піддерево `x`.
3. Вузол `x` опускається і стає правим сином `y`.
4. Батьківський зв'язок `x->parent` передається вузлу `y`.

Процедура повороту вимагає покрокової модифікації 6 вказівників. Розглянемо детальний порядок операцій:

- **Перепідключення піддерева B:** Операція `x->left = B` передає піддерево `B` від вузла `y` до `x`. Якщо піддерево `B` існує (`B != NULL`), його зворотний вказівник мусить бути оновлений: `B->parent = x`. Якщо пропустити цю перевірку, система спробує звернутися за адресою `NULL->parent`, що викликає аварійну зупинку процесу.
- **Зв'язування з батьком P:** Вузол `y` займає позицію `x` у вищому дереві. Якщо `x` був коренем всього дерева (`x->parent == NULL`), то новий корінь записаний у глобальний вказівник `*root = y`. Якщо ж `x` мав батька `P`, ми перевіряємо, якою саме дитиною був `x` (`x == P->left`), і оновлюємо відповідне поле `P->left = y` або `P->right = y`.
- **Порядок оновлення висот:** Висоти обчислюються строго знизу вгору. Вузол `x` тепер став дитиною `y`, тому спочатку викликається `update_height(x)`, а лише потім `update_height(y)`. Порушення цього порядку призведе до обчислення некоректних висот на вищих рівнях рекурсії.

:::tabs
```c
/* Правий поворот навколо вузла x */
Node* rotate_right(Node* x, Node** root) {
    assert(x != NULL && "Вузол x не може бути NULL");
    assert(x->left != NULL && "Правий поворот вимагає наявності лівого сина");

    Node* y = x->left;
    Node* B = y->right;

    /* Крок 1: Перепідключення правого піддерева B до x */
    x->left = B;
    if (B != NULL) {
        B->parent = x;
    }

    /* Крок 2: Зв'язування y з батьком вузла x (P) */
    y->parent = x->parent;
    if (x->parent == NULL) {
        if (root != NULL) {
            *root = y; /* y стає новим коренем усього дерева */
        }
    } else if (x == x->parent->left) {
        x->parent->left = y;
    } else {
        x->parent->right = y;
    }

    /* Крок 3: Переміщення x у правого сина y */
    y->right = x;
    x->parent = y;

    /* Крок 4: Оновлення метрик (строго знизу вгору: спочатку x, потім y) */
    update_height(x);
    update_height(y);

    return y; /* Повертаємо новий корінь піддерева */
}

/* Лівий поворот навколо вузла x */
Node* rotate_left(Node* x, Node** root) {
    assert(x != NULL && "Вузол x не може бути NULL");
    assert(x->right != NULL && "Лівий поворот вимагає наявності правого сина");

    Node* y = x->right;
    Node* B = y->left;

    /* Крок 1: Перепідключення лівого піддерева B до x */
    x->right = B;
    if (B != NULL) {
        B->parent = x;
    }

    /* Крок 2: Зв'язування y з батьком вузла x (P) */
    y->parent = x->parent;
    if (x->parent == NULL) {
        if (root != NULL) {
            *root = y; /* y стає новим коренем усього дерева */
        }
    } else if (x == x->parent->left) {
        x->parent->left = y;
    } else {
        x->parent->right = y;
    }

    /* Крок 3: Переміщення x у лівого сина y */
    y->left = x;
    x->parent = y;

    /* Крок 4: Оновлення метрик (строго знизу вгору: спочатку x, потім y) */
    update_height(x);
    update_height(y);

    return y;
}
```
```cpp
template <typename T>
Node<T>* rotate_right(Node<T>* x, Node<T>*& root) noexcept {
    assert(x != nullptr && "Вузол x не може бути nullptr");
    assert(x->left != nullptr && "Правий поворот вимагає наявності лівого сина");

    Node<T>* y = x->left;
    Node<T>* B = y->right;

    // Крок 1: Перепідключення піддерева B
    x->left = B;
    if (B != nullptr) {
        B->parent = x;
    }

    // Крок 2: Оновлення батьківського зв'язку для y
    y->parent = x->parent;
    if (x->parent == nullptr) {
        root = y;
    } else if (x == x->parent->left) {
        x->parent->left = y;
    } else {
        x->parent->right = y;
    }

    // Крок 3: x стає правим сином y
    y->right = x;
    x->parent = y;

    // Крок 4: Оновлення висот знизу вгору
    update_height(x);
    update_height(y);

    return y;
}

template <typename T>
Node<T>* rotate_left(Node<T>* x, Node<T>*& root) noexcept {
    assert(x != nullptr && "Вузол x не може бути nullptr");
    assert(x->right != nullptr && "Лівий поворот вимагає наявності правого сина");

    Node<T>* y = x->right;
    Node<T>* B = y->left;

    // Крок 1: Перепідключення піддерева B
    x->right = B;
    if (B != nullptr) {
        B->parent = x;
    }

    // Крок 2: Оновлення батьківського зв'язку для y
    y->parent = x->parent;
    if (x->parent == nullptr) {
        root = y;
    } else if (x == x->parent->left) {
        x->parent->left = y;
    } else {
        x->parent->right = y;
    }

    // Крок 3: x стає лівим сином y
    y->left = x;
    x->parent = y;

    // Крок 4: Оновлення висот знизу вгору
    update_height(x);
    update_height(y);

    return y;
}
```
:::

## 3. Реалізація подвійних повертань (LR та RL)

Якщо в піддереві виник внутрішній зигзагоподібний дисбаланс (Left-Right або Right-Left), поодинокий поворот лише віддзеркалює зигзаг. Подвійний поворот виконує комбінацію з двох повертань.

Процедура Left-Right повороту `rotate_left_right(z)` складається з двох кроків:
1. Спочатку виконується лівий поворот для лівого сина `rotate_left(z->left)`. Це піднімає внутрішній вузол нагору й випрямляє зигзагоподібне піддерево у строго лівоважку форму (LL).
2. Потім виконується правий поворот для самого кореня `rotate_right(z)`. Це зменшує висоту всього фрагмента на 1 і відновлює баланс.

:::tabs
```c
/* Подвійний Left-Right поворот (зигзаг) навколо z */
Node* rotate_left_right(Node* z, Node** root) {
    if (!z || !z->left) return z;
    /* Крок 1: Лівий поворот для лівого сина, щоб випрямити зигзаг у LL */
    z->left = rotate_left(z->left, root);
    /* Крок 2: Правий поворот для кореня z */
    return rotate_right(z, root);
}

/* Подвійний Right-Left поворот (заг-зиг) навколо z */
Node* rotate_right_left(Node* z, Node** root) {
    if (!z || !z->right) return z;
    /* Крок 1: Правий поворот для правого сина, щоб випрямити заг-зиг у RR */
    z->right = rotate_right(z->right, root);
    /* Крок 2: Лівий поворот для кореня z */
    return rotate_left(z, root);
}
```
```cpp
template <typename T>
Node<T>* rotate_left_right(Node<T>* z, Node<T>*& root) noexcept {
    if (!z || !z->left) return z;
    // Крок 1: Лівий поворот для лівого сина
    z->left = rotate_left(z->left, root);
    // Крок 2: Правий поворот для кореня z
    return rotate_right(z, root);
}

template <typename T>
Node<T>* rotate_right_left(Node<T>* z, Node<T>*& root) noexcept {
    if (!z || !z->right) return z;
    // Крок 1: Правий поворот для правого сина
    z->right = rotate_right(z->right, root);
    // Крок 2: Лівий поворот для кореня z
    return rotate_left(z, root);
}
```
:::

## 4. Практичне застосування: Вставка в AVL-дерево з балансуванням

Проілюструємо, як повороти автоматично відновлюють баланс при рекурсивній вставці елементів у класичному AVL-дереві. Після додавання нового вузла у ліве або праве піддерево рекурсивний спуск повертається назад до кореня. На кожному рівні повернення викликається функція `rebalance()`.

Функція обчислює новий фактор балансу `BF = height(right) - height(left)`:
- Якщо `BF <= -2` і `BF(left) <= 0`: дерево є лівоважким (конфігурація LL). Дисбаланс усувається за один поодинокий правий поворот `rotate_right()`.
- Якщо `BF <= -2` і `BF(left) > 0`: дерево містить внутрішній зигзаг (конфігурація LR). Дисбаланс усувається за подвійний поворот `rotate_left_right()`.
- Якщо `BF >= +2` і `BF(right) >= 0`: дерево є правоважким (конфігурація RR). Дисбаланс усувається за один поодинокий лівий поворот `rotate_left()`.
- Якщо `BF >= +2` і `BF(right) < 0`: дерево містить внутрішній заг-зиг (конфігурація RL). Дисбаланс усувається за подвійний поворот `rotate_right_left()`.

:::tabs
```c
/* Автоматична підтримка балансу AVL-вузла повертаннями */
Node* rebalance(Node* node, Node** root) {
    if (!node) return NULL;

    update_height(node);
    int bf = get_balance_factor(node);

    /* Лівоважка конфігурація (BF <= -2) */
    if (bf <= -2) {
        if (get_balance_factor(node->left) <= 0) {
            /* Поодинокий правий поворот (LL) */
            return rotate_right(node, root);
        } else {
            /* Подвійний Left-Right поворот (LR) */
            return rotate_left_right(node, root);
        }
    }

    /* Правоважка конфігурація (BF >= +2) */
    if (bf >= 2) {
        if (get_balance_factor(node->right) >= 0) {
            /* Поодинокий лівий поворот (RR) */
            return rotate_left(node, root);
        } else {
            /* Подвійний Right-Left поворот (RL) */
            return rotate_right_left(node, root);
        }
    }

    return node; /* Дерево збалансоване */
}

/* Рекурсивна вставка вузла в AVL-дерево */
Node* insert_avl(Node* node, int key, Node* parent, Node** root) {
    if (node == NULL) {
        Node* new_node = create_node(key);
        if (new_node) new_node->parent = parent;
        return new_node;
    }

    if (key < node->key) {
        node->left = insert_avl(node->left, key, node, root);
    } else if (key > node->key) {
        node->right = insert_avl(node->right, key, node, root);
    } else {
        return node; /* Дублікати не вставляються */
    }

    return rebalance(node, root);
}
```
```cpp
template <typename T>
Node<T>* rebalance(Node<T>* node, Node<T>*& root) noexcept {
    if (!node) return nullptr;

    update_height(node);
    int bf = get_balance_factor(node);

    // Лівоважка конфігурація
    if (bf <= -2) {
        if (get_balance_factor(node->left) <= 0) {
            return rotate_right(node, root); // LL
        } else {
            return rotate_left_right(node, root); // LR
        }
    }

    // Правоважка конфігурація
    if (bf >= 2) {
        if (get_balance_factor(node->right) >= 0) {
            return rotate_left(node, root); // RR
        } else {
            return rotate_right_left(node, root); // RL
        }
    }

    return node;
}

template <typename T>
Node<T>* insert_avl(Node<T>* node, T key, Node<T>* parent, Node<T>*& root) {
    if (!node) {
        auto* new_node = new Node<T>(std::move(key));
        new_node->parent = parent;
        return new_node;
    }

    if (key < node->key) {
        node->left = insert_avl(node->left, key, node, root);
    } else if (key > node->key) {
        node->right = insert_avl(node->right, key, node, root);
    } else {
        return node;
    }

    return rebalance(node, root);
}
```
:::

## 5. Повний тестовий демонстраційний прогін

Протестуємо вставку послідовності `10, 20, 30, 40, 50, 25` у порожнє дерево. Звичайне BST без повертань виродилося б у лінійний список висотою `h = 6`. AVL-дерево завдяки повертанням перетворює його на ідеально збалансовану структуру висотою `h = 3`.

Кожен крок вставки демонструє роботу конкретного повороту:
- При вставці `30` виникає RR-дисбаланс у вузла `10`, що виправляється поодиноким лівим поворотом `rotate_left(10)`. Новим коренем стає `20`.
- При вставці `50` виникає RR-дисбаланс у вузла `30`, що усувається лівим поворотом `rotate_left(30)`.
- При вставці `25` виникає RL-дисбаланс у кореня `20`, що усувається подвійним поворотом `rotate_right_left(20)`. Новим коренем всього дерева стає `30`.

:::tabs
```c
void print_inorder_tree(const Node* node) {
    if (!node) return;
    print_inorder_tree(node->left);
    printf("Ключ: %2d | Висота: %d | BF: %2d\n", 
           node->key, node->height, get_balance_factor(node));
    print_inorder_tree(node->right);
}

void free_tree_nodes(Node* node) {
    if (!node) return;
    free_tree_nodes(node->left);
    free_tree_nodes(node->right);
    free(node);
}

int main(void) {
    Node* root = NULL;
    int keys[] = {10, 20, 30, 40, 50, 25};
    size_t num_keys = sizeof(keys) / sizeof(keys[0]);

    printf("--- Послідовна вставка елементів 10, 20, 30, 40, 50, 25 ---\n");
    for (size_t i = 0; i < num_keys; ++i) {
        root = insert_avl(root, keys[i], NULL, &root);
    }

    printf("\nПідсумковий центровий обхід дерева:\n");
    print_inorder_tree(root);

    printf("\nКорінь дерева: %d (висота %d)\n", root->key, root->height);
    assert(root->key == 30 && "Корінь мусить бути 30 після балансування");
    assert(root->height == 3 && "Висота збалансованого дерева повинна дорівнювати 3");

    printf("\nТест пройдено успішно: баланс відновлено повертаннями!\n");
    free_tree_nodes(root);
    return 0;
}
```
```cpp
template <typename T>
void print_inorder_tree(const Node<T>* node) {
    if (!node) return;
    print_inorder_tree(node->left);
    std::cout << "Ключ: " << node->key << " | Висота: " << node->height 
              << " | BF: " << get_balance_factor(node) << "\n";
    print_inorder_tree(node->right);
}

template <typename T>
void free_tree_nodes(Node<T>* node) {
    if (!node) return;
    free_tree_nodes(node->left);
    free_tree_nodes(node->right);
    delete node;
}

int main() {
    Node<int>* root = nullptr;
    int keys[] = {10, 20, 30, 40, 50, 25};

    std::cout << "--- Послідовна вставка елементів 10, 20, 30, 40, 50, 25 ---\n";
    for (int k : keys) {
        root = insert_avl(root, k, nullptr, root);
    }

    std::cout << "\nПідсумковий центровий обхід дерева:\n";
    print_inorder_tree(root);

    std::cout << "\nКорінь дерева: " << root->key << " (висота " << root->height << ")\n";
    assert(root->key == 30 && "Корінь мусить бути 30 після балансування");
    assert(root->height == 3 && "Висота збалансованого дерева повинна дорівнювати 3");

    std::cout << "\nТест пройдено успішно: баланс відновлено повертаннями!\n";
    free_tree_nodes(root);
    return 0;
}
```
:::

## 6. Продуктивність та оптимізація кеш-ліній

На сучасних процесорах з багаторівневим кешем (L1/L2/L3) основною вартістю повертання дерева є не самі інструкції процесора, а промахи кешу (cache misses) при розіменуванні вказівників.

Оптимізації повороту у системних реалізаціях:
1. **Упаковка метаданих:** Замість збереження цілого `int height` (4 байти) у червоно-чорних деревах колір зберігається в 1 біті, який упаковується в молодший неіснуючий біт батьківського вказівника `parent` (завдяки вирівнюванню адрес на 8 байтів останні 3 біти вказівника завжди нульові). Наприклад, така оптимізація у `struct rb_node` ядра Linux зменшує розмір вузла з 32 до 24 байтів.
2. **Уникнення батьківських вказівників (Pointer-free parent stack):** При ітеративному спуску шлях від кореня до вузла можна зберігати у локальному масиві-стеку на процесорному стеку. Це звільняє 8 байтів у самому вузлі й зменшує кількість записів у пам'ять під час повороту.
