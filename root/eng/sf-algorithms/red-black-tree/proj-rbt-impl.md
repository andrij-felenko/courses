# ⚙️ Реалізація червоно-чорного дерева на C та C++

У цьому розділі наведено повну, працездатну та ідіоматичну реалізацію структури червоно-чорного дерева мовами системного програмування C та C++. Реалізація охоплює структури даних для вузлів та дерева, ініціалізацію, допоміжні операції локальних поворотів, основний алгоритм вставки нових елементів та відновлення інваріантів (балансування).

## 1. Архітектура та використання фіктивного sentinel-вузла

При реалізації збалансованого дерева ключовим архітектурним рішенням є використання фіктивного sentinel-вузла `nil`. У звичайному бінарному дереві пошуку листки представлені порожніми вказівниками `NULL`. Проте під час балансування червоно-чорного дерева алгоритм постійно звертається до дочірніх вузлів, батька, дідуся та дядька. Якщо використовувати `NULL`, код переповнюється нескінченними перевірками вигляду `if (node != NULL && node->parent != NULL)`.

Sentinel-вузол `nil` усуває цю проблему. Це єдиний статично виділений чорний вузол, на який посилаються всі листки дерева, а також батьківський вказівник кореневого вузла. Оскільки `nil` є чорним вузлом із колірним атрибутом `BLACK`, перевірки інваріантів (наприклад, оцінка кольору дядька чи дітей) виконуються уніфіковано без жодного ризику розіменування нульового вказівника (Null Pointer Dereference).

## 2. Покроковий розбір допоміжних поворотів

Локальні повороти змінюють геометричні зв'язки між вузлами без порушення впорядкованості бінарного дерева пошуку:

### 2.1. Лівий поворот (`left_rotate`)
- **Алгоритм:** Нехай `x` — вузол, навколо якого виконується поворот, а `y` — його права дитина.
- Праве піддерево `x` заміщується на ліве піддерево `y` (`x->right = y->left`).
- Якщо ліве піддерево `y` не дорівнює `nil`, його батьківський вказівник переспрямовується на `x`.
- Батьком `y` стає колишній батько `x`.
- Якщо `x` був коренем дерева, то новим коренем стає `y`. Якщо `x` був лівою дитиною свого батька, то `y` стає лівою дитиною; інакше `y` стає правою дитиною.
- Вузол `x` стає лівою дитиною `y`, а батьком `x` стає `y`.

### 2.2. Правий поворот (`right_rotate`)
- **Алгоритм:** Дзеркальна операція до Лівого повороту. Ліва дитина `x` вузла `y` займає позицію `y`, а її праве піддерево передається у ліве піддерево `y`.

## 3. Логіка процедури відновлення інваріантів

Під час вставки нового елемента він завжди отримує червоний колір. Це гарантує збереження інваріанту чорної висоти (інваріант 5), проте може порушити червоний інваріант (інваріант 4), якщо батько вставленої вершини також є червоним.

Процедура `insert_fixup` у циклі перевіряє колір батьківського вузла. Доки батько залишається червоним, здійснюється аналіз кольору дядька:
1. **Якщо дядько червоний (Case 1):** виконується перефарбування батька та дядька у чорний колір, а дідусь фарбується у червоний. Конфлікт піднімається на два рівні вгору, і цикл продовжується.
2. **Якщо дядько чорний, а новий вузол утворює зиґзаґ (Case 2):** виконується попередній поворот навколо батька, що випрямляє гілку та зводить конфігурацію до третього випадку.
3. **Якщо дядько чорний, а новий вузол стоїть на одній лінії (Case 3):** виконується підсумковий поворот навколо дідуся та перефарбування батька у чорний, а дідуся у червоний колір. Це повністю ліквідує червоний конфлікт і зупиняє цикл.

Після завершення циклу корінь дерева примусово фарбується у чорний колір для дотримання інваріанту кореня (інваріант 2).

## 4. Логіка вилучення та коригування подвійної чорноти (`delete_fixup`)

При вилученні чорного вузла гілка втрачає одиницю чорної висоти. Для компенсації на дочірню вершину `x` покладається концепція «подвійної чорноти». Коригування `delete_fixup` переміщує подвійну чорноту вгору за деревом за допомогою 4 конфігураційних випадків кольору брата `S`:
- **Випадок 1 (Брат S червоний):** Батько фарбується в червоний колір, брат в чорний, виконується поворот. Це зводить ситуацію до чорного брата.
- **Випадок 2 (Брат S чорний, обидва сини S чорні):** Подвійна чорнота знімається з `x`, брат фарбується в червоний колір, а додаткова чорнота передається батькові.
- **Випадок 3 (Брат S чорний, ближній син S червоний):** Брат фарбується у червоний колір, його син у чорний, виконується поворот для перетворення на Випадок 4.
- **Випадок 4 (Брат S чорний, далекий син S червоний):** Брат копіює колір батька, батько та син фарбуються в чорний, виконується поворот навколо батька. Подвійна чорнота зникає.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>

// Кольори вузлів червоно-чорного дерева
typedef enum { RED, BLACK } NodeColor;

// Структура вузла
typedef struct RBNode {
    int key;
    NodeColor color;
    struct RBNode *left;
    struct RBNode *right;
    struct RBNode *parent;
} RBNode;

// Структура дерева із фіктивним листком nil
typedef struct {
    RBNode *root;
    RBNode *nil;
} RBTree;

// Створення нового червоного вузла
RBNode* create_node(RBTree *tree, int key) {
    RBNode *node = (RBNode*)malloc(sizeof(RBNode));
    if (!node) return NULL;
    node->key = key;
    node->color = RED;
    node->left = tree->nil;
    node->right = tree->nil;
    node->parent = tree->nil;
    return node;
}

// Ініціалізація порожнього дерева
RBTree* rbtree_create(void) {
    RBTree *tree = (RBTree*)malloc(sizeof(RBTree));
    if (!tree) return NULL;
    tree->nil = (RBNode*)malloc(sizeof(RBNode));
    if (!tree->nil) {
        free(tree);
        return NULL;
    }
    tree->nil->color = BLACK;
    tree->nil->left = NULL;
    tree->nil->right = NULL;
    tree->nil->parent = NULL;
    tree->root = tree->nil;
    return tree;
}

// Лівий поворот навколо вузла x
void left_rotate(RBTree *tree, RBNode *x) {
    RBNode *y = x->right;
    x->right = y->left;
    
    if (y->left != tree->nil) {
        y->left->parent = x;
    }
    
    y->parent = x->parent;
    
    if (x->parent == tree->nil) {
        tree->root = y;
    } else if (x == x->parent->left) {
        x->parent->left = y;
    } else {
        x->parent->right = y;
    }
    
    y->left = x;
    x->parent = y;
}

// Правий поворот навколо вузла y
void right_rotate(RBTree *tree, RBNode *y) {
    RBNode *x = y->left;
    y->left = x->right;
    
    if (x->right != tree->nil) {
        x->right->parent = y;
    }
    
    x->parent = y->parent;
    
    if (y->parent == tree->nil) {
        tree->root = x;
    } else if (y == y->parent->right) {
        y->parent->right = x;
    } else {
        y->parent->left = x;
    }
    
    x->right = y;
    y->parent = x;
}

// Відновлення інваріантів після вставки червоного вузла z
void rbtree_insert_fixup(RBTree *tree, RBNode *z) {
    while (z->parent->color == RED) {
        if (z->parent == z->parent->parent->left) {
            RBNode *y = z->parent->parent->right; // Дядько
            if (y->color == RED) { // Випадок 1: Дядько червоний (перефарбування)
                z->parent->color = BLACK;
                y->color = BLACK;
                z->parent->parent->color = RED;
                z = z->parent->parent;
            } else {
                if (z == z->parent->right) { // Випадок 2: Zig-Zag (внутрішній)
                    z = z->parent;
                    left_rotate(tree, z);
                }
                // Випадок 3: Line (зовнішній)
                z->parent->color = BLACK;
                z->parent->parent->color = RED;
                right_rotate(tree, z->parent->parent);
            }
        } else { // Симетрична гілка (батько є правою дитиною)
            RBNode *y = z->parent->parent->left;
            if (y->color == RED) {
                z->parent->color = BLACK;
                y->color = BLACK;
                z->parent->parent->color = RED;
                z = z->parent->parent;
            } else {
                if (z == z->parent->left) {
                    z = z->parent;
                    right_rotate(tree, z);
                }
                z->parent->color = BLACK;
                z->parent->parent->color = RED;
                left_rotate(tree, z->parent->parent);
            }
        }
    }
    tree->root->color = BLACK;
}

// Вставка ключа у дерево
void rbtree_insert(RBTree *tree, int key) {
    RBNode *z = create_node(tree, key);
    if (!z) return;
    RBNode *y = tree->nil;
    RBNode *x = tree->root;
    
    while (x != tree->nil) {
        y = x;
        if (z->key < x->key) {
            x = x->left;
        } else {
            x = x->right;
        }
    }
    
    z->parent = y;
    if (y == tree->nil) {
        tree->root = z;
    } else if (z->key < y->key) {
        y->left = z;
    } else {
        y->right = z;
    }
    
    rbtree_insert_fixup(tree, z);
}

// Рекурсивне вивільнення пам'яті
void free_tree_nodes(RBTree *tree, RBNode *node) {
    if (node != tree->nil) {
        free_tree_nodes(tree, node->left);
        free_tree_nodes(tree, node->right);
        free(node);
    }
}

void rbtree_destroy(RBTree *tree) {
    if (!tree) return;
    free_tree_nodes(tree, tree->root);
    free(tree->nil);
    free(tree);
}

int main(void) {
    RBTree *tree = rbtree_create();
    int keys[] = {10, 20, 30, 15, 25, 5};
    for (int i = 0; i < 6; i++) {
        rbtree_insert(tree, keys[i]);
    }
    printf("Червоно-чорне дерево побудовано. Корінь: %d\n", tree->root->key);
    rbtree_destroy(tree);
    return 0;
}
```
```cpp
#include <iostream>
#include <memory>
#include <utility>
#include <vector>

enum class Color { Red, Black };

template <typename T>
class RedBlackTree {
private:
    struct Node {
        T key;
        Color color;
        Node* left{nullptr};
        Node* right{nullptr};
        Node* parent{nullptr};

        explicit Node(T val, Color c = Color::Red) 
            : key(std::move(val)), color(c) {}
    };

    Node* root_{nullptr};
    Node* nil_{nullptr};

    void left_rotate(Node* x) {
        Node* y = x->right;
        x->right = y->left;

        if (y->left != nil_) {
            y->left->parent = x;
        }

        y->parent = x->parent;

        if (x->parent == nil_) {
            root_ = y;
        } else if (x == x->parent->left) {
            x->parent->left = y;
        } else {
            x->parent->right = y;
        }

        y->left = x;
        x->parent = y;
    }

    void right_rotate(Node* y) {
        Node* x = y->left;
        y->left = x->right;

        if (x->right != nil_) {
            x->right->parent = y;
        }

        x->parent = y->parent;

        if (y->parent == nil_) {
            root_ = x;
        } else if (y == y->parent->right) {
            y->parent->right = x;
        } else {
            y->parent->left = x;
        }

        x->right = y;
        y->parent = x;
    }

    void insert_fixup(Node* z) {
        while (z->parent->color == Color::Red) {
            if (z->parent == z->parent->parent->left) {
                Node* y = z->parent->parent->right; // Дядько
                if (y->color == Color::Red) {
                    z->parent->color = Color::Black;
                    y->color = Color::Black;
                    z->parent->parent->color = Color::Red;
                    z = z->parent->parent;
                } else {
                    if (z == z->parent->right) {
                        z = z->parent;
                        left_rotate(z);
                    }
                    z->parent->color = Color::Black;
                    z->parent->parent->color = Color::Red;
                    right_rotate(z->parent->parent);
                }
            } else {
                Node* y = z->parent->parent->left;
                if (y->color == Color::Red) {
                    z->parent->color = Color::Black;
                    y->color = Color::Black;
                    z->parent->parent->color = Color::Red;
                    z = z->parent->parent;
                } else {
                    if (z == z->parent->left) {
                        z = z->parent;
                        right_rotate(z);
                    }
                    z->parent->color = Color::Black;
                    z->parent->parent->color = Color::Red;
                    left_rotate(z->parent->parent);
                }
            }
        }
        root_->color = Color::Black;
    }

    void destroy_recursive(Node* node) {
        if (node != nil_) {
            destroy_recursive(node->left);
            destroy_recursive(node->right);
            delete node;
        }
    }

public:
    RedBlackTree() {
        nil_ = new Node(T{}, Color::Black);
        root_ = nil_;
    }

    ~RedBlackTree() {
        destroy_recursive(root_);
        delete nil_;
    }

    RedBlackTree(const RedBlackTree&) = delete;
    RedBlackTree& operator=(const RedBlackTree&) = delete;
    RedBlackTree(RedBlackTree&& o) noexcept 
        : root_(std::exchange(o.root_, nullptr)), nil_(std::exchange(o.nil_, nullptr)) {}

    RedBlackTree& operator=(RedBlackTree&& o) noexcept {
        if (this != &o) {
            if (root_) destroy_recursive(root_);
            delete nil_;
            root_ = std::exchange(o.root_, nullptr);
            nil_ = std::exchange(o.nil_, nullptr);
        }
        return *this;
    }

    void insert(T key) {
        Node* z = new Node(std::move(key), Color::Red);
        z->left = nil_;
        z->right = nil_;

        Node* y = nil_;
        Node* x = root_;

        while (x != nil_) {
            y = x;
            if (z->key < x->key) {
                x = x->left;
            } else {
                x = x->right;
            }
        }

        z->parent = y;
        if (y == nil_) {
            root_ = z;
        } else if (z->key < y->key) {
            y->left = z;
        } else {
            y->right = z;
        }

        insert_fixup(z);
    }

    [[nodiscard]] bool contains(const T& key) const {
        Node* curr = root_;
        while (curr != nil_) {
            if (key == curr->key) return true;
            if (key < curr->key) curr = curr->left;
            else curr = curr->right;
        }
        return false;
    }

    [[nodiscard]] const T& root_key() const {
        return root_->key;
    }
};

int main() {
    RedBlackTree<int> tree;
    for (int k : {10, 20, 30, 15, 25, 5}) {
        tree.insert(k);
    }
    std::cout << "Root key: " << tree.root_key() << "\n";
    std::cout << "Contains 15: " << std::boolalpha << tree.contains(15) << "\n";
    return 0;
}
```
:::

## 5. Порівняння підходів у мовах C та C++

1. **Керування пам'яттю:** У мові C пам'ять для кожного вузла виділяється вручну через `malloc` та звільняється у `rbtree_destroy`. У мові C++ виділення та звільнення інкапсульовано за принципом RAII.
2. **Типізація:** C-реалізація оперує фіксованим типом `int` (або `void*` для універсальних структур з функціями порівняння), тоді як C++ реалізація використовує шаблони `template <typename T>`, що дозволяє працювати з довільними типами ключів без втрати продуктивності й без приведення типів.
3. **Безпека винятків та семантика переміщення:** C++ реалізація містить підтримку move-семантики (`RedBlackTree(RedBlackTree&&)`), що забезпечує ефективне передавання ownership об'єкта без копіювання його ресурсів.

## 6. Практичне тестування та гарантії продуктивності

Під час тестування наведеного коду на послідовно зростаючих масивах елементів (наприклад від 1 до 1 000 000) звичайне бінарне дерево шукало б кожен елемент за глибиною близько `1 000 000` кроків. Червоно-чорне дерево завдяки процедурі `insert_fixup` переструктуровує гілки таким чином, що максимальна глибина дерева не перевищує 39 рівнів. Усі операції вставки та пошуку виконуються за стабільний логарифмічний час `O(log n)`.
