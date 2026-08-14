# ⚙️ Реалізація двійкового дерева та алгоритми його обходу

Ця вставка містить вичерпний практичний опис побудови, обходу та маніпулювання двійковими деревами мовами C та C++. У ній розглядаються як класичні рекурсивні підходи, так і професійні ітеративні алгоритми без рекурсії, розбирається механіка роботи з динамічною пам'яттю, аналізується проблема кеш-локальності та розкриваються підводні камені реального системного програмування.

Подання двійкового дерева в пам'яті вимагає виділення автономних вузлів у купі. Кожен вузол містить корисний вміст (значення) та дві адреси на піддерева. Проте правильна організація життєвого циклу таких об'єктів кардинально різниться залежно від використовуваної мови.

---

## 1. Структура вузла та керування життєвим циклом пам'яті

У мові C виділення пам'яті здійснюється вручную через виклик `malloc()`. Оскільки середовище виконання C не має системного збирача сміття чи автоматичних деструкторів, розробник зобов'язаний самостійно контролювати звільнення кожного виділеного блоку. Звільнення дерева вимагає використання **зворотного обходу (Post-order)**: спочатку рекурсивно вивільняються ліве та праве піддерева, і лише після цього робиться `free()` самого батьківського вузла. Спроба звільнити батьківський вузол першим перетворює посилання на його дітей на «висячі вказівники» (англ. *dangling pointers*), що призводить до втрати контролю над пам'яттю піддерев і спричиняє незворотні витоки пам'яті (англ. *memory leaks*).

У сучасній мові C++ (починаючи з версії C++11) ручне управління за допомогою `new` і `delete` вважається антипаттерном. Натомість використовується концепція RAII (*Resource Acquisition Is Initialization*) та розумні вказівники `std::unique_ptr`. Монопольне володіння `std::unique_ptr` гарантує, що коли батьківський вузол виходить із області видимості або знищується, його деструктор автоматично викликає деструктори для лівого та правого синів. Це повністю виключає витоки пам'яті на рівні мови без накладних витрат на лічильники посилань.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

// Вузол двійкового дерева мовою C
typedef struct Node {
    int data;
    struct Node* left;
    struct Node* right;
} Node;

// Створення нового вузла в динамічній пам'яті (купа)
Node* create_node(int value) {
    Node* node = (Node*)malloc(sizeof(Node));
    if (!node) {
        perror("Помилка виділення пам'яті для вузла");
        exit(EXIT_FAILURE);
    }
    node->data = value;
    node->left = NULL;
    node->right = NULL;
    return node;
}

// Звільнення всієї пам'яті дерева (зворотний обхід / Post-order)
void destroy_tree(Node* root) {
    if (root == NULL) return;
    destroy_tree(root->left);
    destroy_tree(root->right);
    free(root);
}
```
```cpp
#include <iostream>
#include <memory>
#include <vector>
#include <queue>
#include <stack>
#include <algorithm>
#include <string>
#include <unordered_map>

// Вузол двійкового дерева мовою C++ з використанням розумних вказівників (RAII)
struct TreeNode {
    int data;
    std::unique_ptr<TreeNode> left;
    std::unique_ptr<TreeNode> right;

    explicit TreeNode(int val) 
        : data(val), left(nullptr), right(nullptr) {}

    // Фабричний метод для зручного створення вузлів
    static std::unique_ptr<TreeNode> make(int val) {
        return std::make_unique<TreeNode>(val);
    }
};

// В C++ пам'ять автоматично звільняється деструктором std::unique_ptr,
// додаткова функція destroy_tree не потрібна!
```
:::

---

## 2. Метрики дерева: Кількість вузлів та обчислення висоти

Обчислення фундаментальних характеристик дерева — його розміру (кількості вузлів) та висоти — демонструє рекурсивну природу двійкових структур даних.

Кількість вузлів у будь-якому піддереві дорівнює одиниці (сам корінь) плюс сума кількості вузлів у його лівому та правому піддеревах. Базовим випадком рекурсії є порожнє дерево, яке містить 0 вузлів.

Висота дерева обчислюється як максимальне значення між висотою лівого та правого піддерев плюс 1. За загальноприйнятою домовленістю, висота порожнього дерева дорівнює `-1`, а дерево, що складається з одного кореневого вузла, має висоту `0`. Обчислення висоти вимагає повного обходу всіх гілок і має часову складність `O(n)`.

:::tabs
```c
// Обчислення кількості вузлів
int count_nodes(const Node* root) {
    if (root == NULL) return 0;
    return 1 + count_nodes(root->left) + count_nodes(root->right);
}

// Обчислення висоти дерева (порожнє дерево = -1, корінь = 0)
int tree_height(const Node* root) {
    if (root == NULL) return -1;
    int left_h = tree_height(root->left);
    int right_h = tree_height(root->right);
    return 1 + (left_h > right_h ? left_h : right_h);
}
```
```cpp
// Обчислення кількості вузлів
int count_nodes(const TreeNode* root) {
    if (!root) return 0;
    return 1 + count_nodes(root->left.get()) + count_nodes(root->right.get());
}

// Обчислення висоти дерева (порожнє дерево = -1, корінь = 0)
int tree_height(const TreeNode* root) {
    if (!root) return -1;
    return 1 + std::max(tree_height(root->left.get()), 
                        tree_height(root->right.get()));
}
```
:::

---

## 3. Рекурсивні обходи вглиб (Pre-order, In-order, Post-order)

Рекурсивний обхід дерева спирається на системний стек викликів (англ. *call stack*). При кожному вході в піддерево середовище виконання автоматично зберігає локальні змінні та адресу повернення у фреймі стека.

Існує три класичні порядки обходу вглиб:
1. **Прямий обхід (Pre-order):** Спочатку обробляється сам корінь, потім ліве піддерево, потім праве піддерево. Цей порядок використовується для створення точної копії дерева або серіалізації його структури.
2. **Серединний обхід (In-order):** Спочатку відвідується ліве піддерево, потім корінь, потім праве піддерево. У двійкових деревах пошуку (BST) цей обхід гарантує відвідування вузлів строго у відсортованому порядку за зростанням ключів.
3. **Зворотний обхід (Post-order):** Спочатку відвідуються обидва піддерева, і лише в кінці — сам корінь. Цей порядок є єдиним безпечним способом рекурсивного видалення вузлів або обчислення агрегованих значень (наприклад, розміру файлів у підкаталогах).

:::tabs
```c
// Прямий обхід (Pre-order): Корінь -> Ліве -> Праве
void print_preorder(const Node* root) {
    if (root == NULL) return;
    printf("%d ", root->data);
    print_preorder(root->left);
    print_preorder(root->right);
}

// Серединний обхід (In-order): Ліве -> Корінь -> Праве
void print_inorder(const Node* root) {
    if (root == NULL) return;
    print_inorder(root->left);
    printf("%d ", root->data);
    print_inorder(root->right);
}

// Зворотний обхід (Post-order): Ліве -> Праве -> Корінь
void print_postorder(const Node* root) {
    if (root == NULL) return;
    print_postorder(root->left);
    print_postorder(root->right);
    printf("%d ", root->data);
}
```
```cpp
// Збирання елементів серединного обходу (In-order) у вектор
void collect_inorder(const TreeNode* root, std::vector<int>& result) {
    if (!root) return;
    collect_inorder(root->left.get(), result);
    result.push_back(root->data);
    collect_inorder(root->right.get(), result);
}

// Збирання елементів прямого обходу (Pre-order) у вектор
void collect_preorder(const TreeNode* root, std::vector<int>& result) {
    if (!root) return;
    result.push_back(root->data);
    collect_preorder(root->left.get(), result);
    collect_preorder(root->right.get(), result);
}
```
:::

---

## 4. Ітеративний обхід без рекурсії: Безпечний обхід глибоких дерев

Хоча рекурсивні функції виглядають лаконічно, вони містять приховану загрозу: якщо дерево є виродженим (наприклад, являє собою ланцюг із 100 000 вузлів), глибина рекурсії досягає 100 000 вкладених викликів. Системний стек потоку, розмір якого за замовчуванням обмежений (зазвичай 1–8 МБ), вичерпується, і програма аварійно завершується через **Stack Overflow**.

Щоб усунути залежність від системного стека, у відповідальному системному програмуванні використовують **ітеративні алгоритми**. Вони переносять облік відвіданих вузлів із системного стека у власний стек, виділений у купі (Heap RAM), де обсяг доступної пам'яті вимірюється гігабайтами.

Нижче наведено ітеративні реалізації серединного (In-order) та порівневого (Level-order) обходів.

:::tabs
```c
// Ітеративний серединний обхід (In-order) на власному стеку C
void inorder_iterative(Node* root) {
    Node* stack[1000];
    int top = -1;
    Node* current = root;

    while (current != NULL || top >= 0) {
        // Спускаємось до найлівішого вузла, зберігаючи предків у стеку
        while (current != NULL) {
            stack[++top] = current;
            current = current->left;
        }

        // Дістаємо вузол зі стека та обробляємо його
        current = stack[top--];
        printf("%d ", current->data);

        // Переходимо до правого піддерева
        current = current->right;
    }
}
```
```cpp
// Ітеративний серединний обхід у C++ із використанням std::stack
std::vector<int> inorder_iterative(const TreeNode* root) {
    std::vector<int> result;
    std::stack<const TreeNode*> st;
    const TreeNode* current = root;

    while (current != nullptr || !st.empty()) {
        while (current != nullptr) {
            st.push(current);
            current = current->left.get();
        }

        current = st.top();
        st.pop();
        result.push_back(current->data);

        current = current->right.get();
    }
    return result;
}
```
:::

---

## 5. Порівневий обхід (Level-order / BFS) через чергу

Порівневий обхід (англ. *breadth-first search*, BFS) відвідує вузли горизонтальними шарами: спочатку корінь (рівень 0), потім всі вузли рівня 1 зліва направо, потім рівень 2 і так далі.

Для реалізації порівневого обходу використовується структурована **черга (FIFO — First In, First Out)**. Алгоритм виймає з голови черги поточний вузол, обробляє його значення та додає його наявних дітей (спочатку лівого, потім правого) у хвіст черги. Просторова складність такого обходу визначається максимальною шириною дерева, яка у випадку ідеального дерева досягає `O(n / 2) = O(n)` вузлів на найнижчому рівні.

:::tabs
```c
// Черга для вузлів C-версії (спрощена реалізація на масиві)
#define MAX_QUEUE 1000

void print_level_order(Node* root) {
    if (root == NULL) return;

    Node* queue[MAX_QUEUE];
    int head = 0, tail = 0;

    queue[tail++] = root;

    while (head < tail) {
        Node* current = queue[head++];
        printf("%d ", current->data);

        if (current->left != NULL) {
            queue[tail++] = current->left;
        }
        if (current->right != NULL) {
            queue[tail++] = current->right;
        }
    }
}
```
```cpp
// Порівневий обхід у C++ з поверненням вектора рівнів
std::vector<std::vector<int>> level_order(const TreeNode* root) {
    std::vector<std::vector<int>> result;
    if (!root) return result;

    std::queue<const TreeNode*> q;
    q.push(root);

    while (!q.empty()) {
        size_t level_size = q.size();
        std::vector<int> current_level;
        current_level.reserve(level_size);

        for (size_t i = 0; i < level_size; ++i) {
            const TreeNode* node = q.front();
            q.pop();
            current_level.push_back(node->data);

            if (node->left)  q.push(node->left.get());
            if (node->right) q.push(node->right.get());
        }
        result.push_back(std::move(current_level));
    }
    return result;
}
```
:::

---

## 6. Алгоритм Морріса: Обхід без додаткової пам'яті O(1)

Найбільш вишуканим алгоритмом обходу є **обхід Морріса (Morris Traversal)**, розроблений Джозефом Моррісом у 1979 році. Всі попередні алгоритми обходу вглиб або вшир вимагають додаткової пам'яті `O(h)` або `O(n)` під стек чи чергу. Обхід Морріса досягає часової складності `O(n)` при абсолютно сталій просторовій складності **`O(1)` додаткової пам'яті**.

Ідея алгоритму Морріса полягає в тимчасовій модифікації структури дерева — так званому **прошиванні (Threading)**. Порожні праві вказівники листків у лівому піддереві тимчасово направляються на поточного предка (створюється місток для повернення догори). Коли обхід лівого піддерева завершується, алгоритм піднімається за цим тимчасовим вказівником, відновлює початкову структуру дерева (занулює тимчасове посилання) і переходить у праве піддерево.

:::tabs
```c
// Обхід Морріса (Morris In-order Traversal) мовою C: O(n) час, O(1) пам'ять
void morris_inorder(Node* root) {
    Node* current = root;

    while (current != NULL) {
        if (current->left == NULL) {
            // Якщо немає лівого піддерева — обробляємо вузол і йдемо праворуч
            printf("%d ", current->data);
            current = current->right;
        } else {
            // Знаходимо попередника в серединному обході (найправіший вузол лівого піддерева)
            Node* predecessor = current->left;
            while (predecessor->right != NULL && predecessor->right != current) {
                predecessor = predecessor->right;
            }

            if (predecessor->right == NULL) {
                // Створюємо тимчасове посилання (місток) на поточний вузол
                predecessor->right = current;
                current = current->left;
            } else {
                // Місток уже існує — відновлюємо дерево та обробляємо вузол
                predecessor->right = NULL;
                printf("%d ", current->data);
                current = current->right;
            }
        }
    }
}
```
```cpp
// Обхід Морріса (Morris In-order Traversal) мовою C++
std::vector<int> morris_inorder(TreeNode* root) {
    std::vector<int> result;
    TreeNode* current = root;

    while (current != nullptr) {
        if (!current->left) {
            result.push_back(current->data);
            current = current->right.get();
        } else {
            // Знаходимо попередника
            TreeNode* predecessor = current->left.get();
            while (predecessor->right && predecessor->right.get() != current) {
                predecessor = predecessor->right.get();
            }

            if (!predecessor->right) {
                // Створюємо тимчасовий місток
                predecessor->right.reset(current);
                current = current->left.get();
            } else {
                // Знімаємо місток
                predecessor->right.release();
                result.push_back(current->data);
                current = current->right.get();
            }
        }
    }
    return result;
}
```
:::

---

## 7. Прошиті двійкові дерева (Threaded Binary Trees)

У системному програмуванні для середовищ із високими вимогами до реального часу (Real-Time Systems) використовують перманентно **прошиті двійкові дерева**.

У стандартному двійковому дереві з `n` вузлами ровно `n + 1` вказівників мають значення `NULL`. Прошивання замінює ці даремно витрачені `NULL`-посилання на корисні вказівники:
- Порожній `left` вказівник розвертається на попередника вузла при серединному обході.
- Порожній `right` вказівник розвертається на наступника вузла при серединному обході.

Щоб відрізнити справжній вказівник на дитину від прошитого вказівника на родича, в структуру вузла додають два бітові прапорці: `left_is_thread` та `right_is_thread`.

:::tabs
```c
// Прошитий вузол двійкового дерева мовою C
typedef struct ThreadedNode {
    int data;
    struct ThreadedNode* left;
    struct ThreadedNode* right;
    bool left_is_thread;   // true, якщо left вказує на попередника
    bool right_is_thread;  // true, якщо right вказує на наступника
} ThreadedNode;

// Знаходження найлівішого вузла в піддереві
ThreadedNode* left_most(ThreadedNode* node) {
    if (node == NULL) return NULL;
    while (!node->left_is_thread && node->left != NULL) {
        node = node->left;
    }
    return node;
}

// Серединний обхід прошитого дерева без стека і без рекурсії за O(n) час та O(1) пам'ять
void threaded_inorder(ThreadedNode* root) {
    ThreadedNode* current = left_most(root);

    while (current != NULL) {
        printf("%d ", current->data);

        if (current->right_is_thread) {
            // Перехід за прошитим нитковим посиланням до наступника
            current = current->right;
        } else {
            // Перехід до найлівішого вузла в правому піддереві
            current = left_most(current->right);
        }
    }
}
```
```cpp
// Прошитий вузол двійкового дерева мовою C++
struct ThreadedTreeNode {
    int data;
    ThreadedTreeNode* left = nullptr;
    ThreadedTreeNode* right = nullptr;
    bool left_is_thread = false;
    bool right_is_thread = false;

    explicit ThreadedTreeNode(int val) : data(val) {}
};

ThreadedTreeNode* left_most(ThreadedTreeNode* node) {
    if (!node) return nullptr;
    while (!node->left_is_thread && node->left) {
        node = node->left;
    }
    return node;
}

std::vector<int> threaded_inorder(ThreadedTreeNode* root) {
    std::vector<int> result;
    ThreadedTreeNode* current = left_most(root);

    while (current) {
        result.push_back(current->data);

        if (current->right_is_thread) {
            current = current->right;
        } else {
            current = left_most(current->right);
        }
    }
    return result;
}
```
:::

---

## 8. Персистентне двійкове дерево на C++ (Path Copying)

Для функціонального програмування та систем із підтримкою знімків стану (Snapshots) використовують персистентні двійкові дерева. Замість видалення або перезапису вузлів при додаванні елемента створюються лише нові вузли вздовж шляху від кореня до точки вставки, а всі незмінені піддерева розшарюються через розумні вказівники спільне володіння `std::shared_ptr`.

При вставці нового ключа в персистентне двійкове дерево створюється точна копія лише тих вузлів, які лежать на шляху спуску від кореня. Оскільки висота збалансованого дерева становить `O(log n)`, при вставці виділяється лише `O(log n)` нових вузлів, а решта `n - log n` вузлів старого дерева залишаються недоторканими й спільно використовуються обома версіями дерева.

:::tabs
```c
// Вузол персистентного дерева на C з лічильником посилань
typedef struct PersistentNode {
    int data;
    struct PersistentNode* left;
    struct PersistentNode* right;
    int ref_count;
} PersistentNode;

PersistentNode* create_persistent_node(int val, PersistentNode* l, PersistentNode* r) {
    PersistentNode* node = (PersistentNode*)malloc(sizeof(PersistentNode));
    node->data = val;
    node->left = l;
    node->right = r;
    node->ref_count = 1;
    if (l) l->ref_count++;
    if (r) r->ref_count++;
    return node;
}
```
```cpp
// Персистентний вузол у C++ із використанням std::shared_ptr
struct PersistentTreeNode {
    int data;
    std::shared_ptr<const PersistentTreeNode> left;
    std::shared_ptr<const PersistentTreeNode> right;

    PersistentTreeNode(int val, 
                       std::shared_ptr<const PersistentTreeNode> l = nullptr, 
                       std::shared_ptr<const PersistentTreeNode> r = nullptr)
        : data(val), left(std::move(l)), right(std::move(r)) {}
};

// Вставка у персистентне двійкове дерево пошуку за копіюванням шляху (Path Copying)
std::shared_ptr<const PersistentTreeNode> persistent_insert(
    const std::shared_ptr<const PersistentTreeNode>& root, int val) 
{
    if (!root) {
        return std::make_shared<const PersistentTreeNode>(val);
    }
    if (val < root->data) {
        // Копіюємо поточний вузол, оновлюючи лише ліве піддерево
        return std::make_shared<const PersistentTreeNode>(
            root->data, 
            persistent_insert(root->left, val), 
            root->right
        );
    } else {
        // Копіюємо поточний вузол, оновлюючи лише праве піддерево
        return std::make_shared<const PersistentTreeNode>(
            root->data, 
            root->left, 
            persistent_insert(root->right, val)
        );
    }
}
```
:::

---

## 9. Арена-виділювач пам'яті (Arena Allocator) для високопродуктивних дерев

Для усунення фрагментації пам'яті та прискорення створення вузлів у високонавантажених системах застосовують спеціалізовані **арена-виділювачі**. Замість того, щоб звертатися до системного виділювача пам'яті `malloc` або `new` для кожного з мільйонів вузлів, арена виділяє суцільний великий блок пам'яті (наприклад, 8 МБ) і нарізає з нього вузли за одну інкрементну операцію вказівника.

Це забезпечує дві критичні переваги:
- Час створення вузла зменшується до абсолютно сталого `O(1)` без системних викликів.
- Вузли розміщуються у неперервних блоках фізичної пам'яті, що відновлює ефективність L1/L2 кешу процесора при послідовному обході.

:::tabs
```c
// Простий арена-виділювач пам'яті для вузлів двійкового дерева на C
typedef struct TreeArena {
    Node* memory_block;
    size_t capacity;
    size_t offset;
} TreeArena;

TreeArena* create_arena(size_t capacity) {
    TreeArena* arena = (TreeArena*)malloc(sizeof(TreeArena));
    arena->memory_block = (Node*)malloc(capacity * sizeof(Node));
    arena->capacity = capacity;
    arena->offset = 0;
    return arena;
}

Node* arena_alloc_node(TreeArena* arena, int val) {
    if (arena->offset >= arena->capacity) {
        fprintf(stderr, "Арена вичерпана!\n");
        return NULL;
    }
    Node* node = &arena->memory_block[arena->offset++];
    node->data = val;
    node->left = NULL;
    node->right = NULL;
    return node;
}

void free_arena(TreeArena* arena) {
    free(arena->memory_block);
    free(arena);
}
```
```cpp
// Арена-виділювач пам'яті у C++ з використанням std::vector як хранилища
class TreeArenaCPP {
private:
    struct RawNode {
        int data;
        RawNode* left = nullptr;
        RawNode* right = nullptr;
    };
    std::vector<std::vector<RawNode>> chunks;
    size_t chunk_size;
    size_t current_chunk_idx = 0;
    size_t current_node_idx = 0;

public:
    explicit TreeArenaCPP(size_t chunkSize = 4096) : chunk_size(chunkSize) {
        chunks.emplace_back(chunk_size);
    }

    RawNode* alloc(int val) {
        if (current_node_idx >= chunk_size) {
            chunks.emplace_back(chunk_size);
            current_chunk_idx++;
            current_node_idx = 0;
        }
        RawNode* node = &chunks[current_chunk_idx][current_node_idx++];
        node->data = val;
        node->left = nullptr;
        node->right = nullptr;
        return node;
    }
    // Вся пам'ять усіх блоків звільняється автоматично в деструкторі std::vector
};
```
:::

---

## 10. Побудова дерева виразів за постфіксним записом

У компіляторах побудова двійкового дерева синтаксичного виразу є ключовим етапом синтаксичного аналізу. При отриманні виразу в постфіксній нотації (зворотний польський запис), алгоритм будує двійкове дерево за один прохід за допомогою стека вузлів:
1. Якщо зустрічається операнд (число або змінна), створюється листок і кладеться в стек.
2. Якщо зустрічається бінарний оператор, зі стека дістаються два вузли: перший дістається як правий син, другий — як лівий син. Створюється новий внутрішній вузол-оператор з цими двома дітьми і кладеться назад у стек.

:::tabs
```c
// Перевірка, чи є символ оператором
bool is_operator(char c) {
    return c == '+' || c == '-' || c == '*' || c == '/';
}

// Побудова дерева виразів з постфіксного рядка на C
Node* build_expression_tree(const char* postfix) {
    Node* stack[100];
    int top = -1;

    for (int i = 0; postfix[i] != '\0'; ++i) {
        char symbol = postfix[i];
        if (symbol == ' ') continue;

        Node* node = create_node(symbol);

        if (is_operator(symbol)) {
            // Дістаємо правий і лівий операнди
            node->right = stack[top--];
            node->left = stack[top--];
        }
        stack[++top] = node;
    }
    return stack[top];
}
```
```cpp
// Побудова дерева виразів у C++
std::unique_ptr<TreeNode> build_expression_tree(const std::string& postfix) {
    std::stack<std::unique_ptr<TreeNode>> st;

    for (char c : postfix) {
        if (c == ' ') continue;

        auto node = std::make_unique<TreeNode>(c);
        if (c == '+' || c == '-' || c == '*' || c == '/') {
            auto right = std::move(st.top()); st.pop();
            auto left = std::move(st.top()); st.pop();
            node->right = std::move(right);
            node->left = std::move(left);
        }
        st.push(std::move(node));
    }
    return std::move(st.top());
}
```
:::

---

## 11. Відновлення двійкового дерева з двох обходів (Pre-order + In-order)

Для відновлення структури збереженого дерева без використання спеціальних маркерів порожніх посилань (Null-markers) використовують комбінацію **Pre-order** та **In-order** обходів.

- Перший елемент у Pre-order завжди є коренем даного піддерева.
- Знайшовши цей корінь у масиві In-order, ми ділимо In-order на дві частини: всі елементи ліворуч утворюють ліве піддерево, а елементи праворуч — праве піддерево.
- Алгоритм рекурсивно будує ліве та праве піддерева за обчисленими діапазонами індексів.

:::tabs
```c
// Пошук індексу елемента в масиві In-order
int find_index(const int* arr, int start, int end, int val) {
    for (int i = start; i <= end; ++i) {
        if (arr[i] == val) return i;
    }
    return -1;
}

// Рекурсивна відбудова дерева на C
Node* build_tree_helper(const int* preorder, const int* inorder, 
                        int in_start, int in_end, int* pre_idx) 
{
    if (in_start > in_end) return NULL;

    int root_val = preorder[(*pre_idx)++];
    Node* root = create_node(root_val);

    if (in_start == in_end) return root;

    int in_idx = find_index(inorder, in_start, in_end, root_val);

    root->left = build_tree_helper(preorder, inorder, in_start, in_idx - 1, pre_idx);
    root->right = build_tree_helper(preorder, inorder, in_idx + 1, in_end, pre_idx);

    return root;
}

Node* build_tree_from_traversals(const int* preorder, const int* inorder, int size) {
    int pre_idx = 0;
    return build_tree_helper(preorder, inorder, 0, size - 1, &pre_idx);
}
```
```cpp
// Відбудова дерева у C++ із хеш-таблицею для O(1) пошуку індексів In-order
class TreeBuilder {
private:
    std::unordered_map<int, int> in_map;
    int pre_idx = 0;

    std::unique_ptr<TreeNode> helper(const std::vector<int>& preorder, 
                                     int in_start, int in_end) 
    {
        if (in_start > in_end) return nullptr;

        int root_val = preorder[pre_idx++];
        auto root = std::make_unique<TreeNode>(root_val);

        int in_idx = in_map[root_val];

        root->left = helper(preorder, in_start, in_idx - 1);
        root->right = helper(preorder, in_idx + 1, in_end);

        return root;
    }

public:
    std::unique_ptr<TreeNode> build(const std::vector<int>& preorder, 
                                    const std::vector<int>& inorder) 
    {
        pre_idx = 0;
        in_map.clear();
        for (int i = 0; i < (int)inorder.size(); ++i) {
            in_map[inorder[i]] = i;
        }
        return helper(preorder, 0, (int)inorder.size() - 1);
    }
};
```
:::

---

## 12. Послідовне представлення дерева у розкладі Ейтцингера (Eytzinger Layout)

Для прискорення пошуку у відсортованих даних на сучасних процесорах з багатьма рівнями кеш-пам'яті замість звичайного двійкового пошуку у відсортованому масиві використовують **розклад Ейтцингера (Eytzinger Layout)**.

Елементи відсортованого масиву розміщуються в масиві за індексами майже повного двійкового дерева:
- Корінь лежить за індексом `1` (1-based indexing).
- Лівий син вузла `k` лежить за індексом `2k`.
- Правий син вузла `k` лежить за індексом `2k + 1`.

Перевага розкладу Ейтцингера полягає у можливості ефективного використання інструкції префетчингу процесора `__builtin_prefetch` для наступного можливого вузла спуску. Це підвищує швидкість двійкового пошуку в 2–3 рази для великих масивів, що не вміщаються в L1/L2 кеш.

:::tabs
```c
// Перетворення відсортованого масиву у розклад Ейтцингера на C
void eytzinger_helper(const int* sorted, int* eytzinger, int n, int k, int* idx) {
    if (k > n) return;
    eytzinger_helper(sorted, eytzinger, n, 2 * k, idx);
    eytzinger[k] = sorted[(*idx)++];
    eytzinger_helper(sorted, eytzinger, n, 2 * k + 1, idx);
}

void build_eytzinger(const int* sorted, int* eytzinger, int n) {
    int idx = 0;
    eytzinger_helper(sorted, eytzinger, n, 1, &idx);
}
```
```cpp
// Двійковий пошук за розкладом Ейтцингера у C++ з префетчингом кешу
int eytzinger_search(const std::vector<int>& eytzinger, int target) {
    int k = 1;
    int n = (int)eytzinger.size() - 1;

    while (k <= n) {
        // Завантажуємо потенційні лінії кешу для дітей на крок уперед
        __builtin_prefetch(&eytzinger[2 * k]);
        __builtin_prefetch(&eytzinger[2 * k + 1]);

        if (eytzinger[k] >= target) {
            k = 2 * k;       // Перехід у ліве піддерево
        } else {
            k = 2 * k + 1;   // Перехід у праве піддерево
        }
    }
    return k >> __builtin_ffs(~k);
}
```
:::

---

## 13. Алгоритм пошуку найменшого спільного предка (Lowest Common Ancestor, LCA)

У багатьох практичних задачах (наприклад, аналіз родоводів, побудова мережевих маршрутів або аналіз залежностей у графах викликів) виникає потреба знайти **найменшого спільного предка (LCA)** двох заданих вузлів `p` та `q` у двійковому дереві.

Найменший спільний предок — це найглибший вузол у дереві, який має як вузол `p`, так і вузол `q` серед своїх нащадків (при цьому вузол може бути предком сам собі).

Алгоритм рекурсивного пошуку LCA вглиб працює за один прохід `O(n)`:
- Якщо поточний вузол є порожнім, або дорівнює `p`, або дорівнює `q`, повертається сам поточний вузол.
- Рекурсивно шукаємо LCA у лівому та правому піддеревах.
- Якщо обидва рекурсивні виклики повернули ненульові вказівники, це означає, що `p` та `q` лежать у різних гілках від поточного вузла. Отже, саме поточний вузол є їхнім найменшим спільним предком!
- Якщо ненульовий вказівник повернуло лише одне піддерево, повертається цей результат.

:::tabs
```c
// Пошук найменшого спільного предка (LCA) мовою C
Node* lowest_common_ancestor(Node* root, Node* p, Node* q) {
    if (root == NULL || root == p || root == q) {
        return root;
    }

    Node* left_lca = lowest_common_ancestor(root->left, p, q);
    Node* right_lca = lowest_common_ancestor(root->right, p, q);

    if (left_lca != NULL && right_lca != NULL) {
        return root;  // Обидва вузли знайдені у різних гілках
    }

    return (left_lca != NULL) ? left_lca : right_lca;
}
```
```cpp
// Пошук найменшого спільного предка (LCA) у C++ з сирими вказівниками
const TreeNode* lowest_common_ancestor(const TreeNode* root, 
                                      const TreeNode* p, 
                                      const TreeNode* q) 
{
    if (!root || root == p || root == q) {
        return root;
    }

    const TreeNode* left_lca = lowest_common_ancestor(root->left.get(), p, q);
    const TreeNode* right_lca = lowest_common_ancestor(root->right.get(), p, q);

    if (left_lca && right_lca) {
        return root;
    }

    return left_lca ? left_lca : right_lca;
}
```
:::

---

## 14. Дзеркальне відображення двійкового дерева (Invert / Mirror Binary Tree)

Класична операція дзеркального відображення перевертає дерево навпаки, міняючи місцями лівого та правого синів для кожного вузла.

Ця операція є прикладом постфіксного чи префіксного трансформаційного обходу:
- Спочатку взаємно міняються місцями вказівники `left` та `right` поточного вузла.
- Потім рекурсивно дзеркально відображаються ліве та праве піддерева.

:::tabs
```c
// Інвертування двійкового дерева на C
Node* invert_tree(Node* root) {
    if (root == NULL) return NULL;

    Node* temp = root->left;
    root->left = invert_tree(root->right);
    root->right = invert_tree(temp);

    return root;
}
```
```cpp
// Інвертування двійкового дерева у C++
std::unique_ptr<TreeNode> invert_tree(std::unique_ptr<TreeNode> root) {
    if (!root) return nullptr;

    auto temp = std::move(root->left);
    root->left = invert_tree(std::move(root->right));
    root->right = invert_tree(std::move(temp));

    return root;
}
```
:::

---

## 15. Безпечне відсікання та видалення піддерева (Subtree Deletion)

При роботі з динамічними двійковими деревами виникає задача видалення цілого піддерева, корінь якого задано вказівником.

Для запобігання появі висячих вказівників (англ. *dangling pointers*) у батьківському вузлі перед викликом деструкції обов'язково обнуляють посилання на це піддерево (`left = NULL` або `right = NULL`).

:::tabs
```c
// Видалення лівого піддерева на C
void detach_and_destroy_left(Node* parent) {
    if (parent == NULL || parent->left == NULL) return;
    destroy_tree(parent->left);
    parent->left = NULL;
}
```
```cpp
// Видалення лівого піддерева у C++ (RAII обнулення)
void detach_and_destroy_left(TreeNode* parent) {
    if (!parent) return;
    parent->left.reset(); // Деструктор std::unique_ptr видалить піддерево автоматично
}
```
:::

---

## 16. Перевірка симетрії та еквівалентності двох дерев

Для перевірки симетричності двійкового дерева відносно свого кореня порівнюють ліве піддерево з дзеркально перевернутим правим піддеревом.

Перевірка симетрії є основою для виявлення фрактальних та дзеркальних структур у синтаксичних графах. Дві гілки вважаються дзеркально симетричними, якщо вони одночасно порожні, або їхні кореневі значення збігаються, а ліве піддерево першої гілки є дзеркальним відображенням правого піддерева другої гілки, і навпаки.

:::tabs
```c
// Перевірка, чи є два піддерева дзеркально симетричними на C
bool is_mirror(const Node* t1, const Node* t2) {
    if (t1 == NULL && t2 == NULL) return true;
    if (t1 == NULL || t2 == NULL) return false;
    return (t1->data == t2->data) &&
           is_mirror(t1->left, t2->right) &&
           is_mirror(t1->right, t2->left);
}

bool is_symmetric(const Node* root) {
    if (root == NULL) return true;
    return is_mirror(root->left, root->right);
}
```
```cpp
// Перевірка симетрії двійкового дерева у C++
bool is_mirror(const TreeNode* t1, const TreeNode* t2) {
    if (!t1 && !t2) return true;
    if (!t1 || !t2) return false;
    return (t1->data == t2->data) &&
           is_mirror(t1->left.get(), t2->right.get()) &&
           is_mirror(t1->right.get(), t2->left.get());
}

bool is_symmetric(const TreeNode* root) {
    if (!root) return true;
    return is_mirror(root->left.get(), root->right.get());
}
```
:::

---

## 17. Демонстраційна програма (main)

:::tabs
```c
int main(void) {
    // Побудова тестового дерева:
    //         1
    //       /   \
    //      2     3
    //     / \
    //    4   5
    Node* root = create_node(1);
    root->left = create_node(2);
    root->right = create_node(3);
    root->left->left = create_node(4);
    root->left->right = create_node(5);

    printf("Кількість вузлів: %d\n", count_nodes(root));
    printf("Висота дерева: %d\n", tree_height(root));

    printf("Pre-order: ");
    print_preorder(root);
    printf("\n");

    printf("In-order (рекурсія):  ");
    print_inorder(root);
    printf("\n");

    printf("In-order (ітеративно): ");
    inorder_iterative(root);
    printf("\n");

    printf("In-order (Морріс):    ");
    morris_inorder(root);
    printf("\n");

    printf("Level-order: ");
    print_level_order(root);
    printf("\n");

    Node* lca = lowest_common_ancestor(root, root->left->left, root->left->right);
    printf("LCA вузлів 4 та 5: %d\n", lca ? lca->data : -1);

    // Обов'язкове звільнення пам'яті!
    destroy_tree(root);
    return 0;
}
```
```cpp
int main() {
    // Побудова того самого дерева в C++ з авто-управлінням пам'яттю
    auto root = TreeNode::make(1);
    root->left = TreeNode::make(2);
    root->right = TreeNode::make(3);
    root->left->left = TreeNode::make(4);
    root->left->right = TreeNode::make(5);

    std::cout << "Кількість вузлів: " << count_nodes(root.get()) << "\n";
    std::cout << "Висота дерева: " << tree_height(root.get()) << "\n";

    std::vector<int> inorder_vals;
    collect_inorder(root.get(), inorder_vals);
    
    std::cout << "In-order (рекурсія): ";
    for (int val : inorder_vals) {
        std::cout << val << " ";
    }
    std::cout << "\n";

    auto iter_vals = inorder_iterative(root.get());
    std::cout << "In-order (ітеративно): ";
    for (int val : iter_vals) {
        std::cout << val << " ";
    }
    std::cout << "\n";

    auto levels = level_order(root.get());
    std::cout << "Рівні дерева (BFS):\n";
    for (size_t i = 0; i < levels.size(); ++i) {
        std::cout << "  Рівень " << i << ": ";
        for (int v : levels[i]) std::cout << v << " ";
        std::cout << "\n";
    }

    const TreeNode* lca = lowest_common_ancestor(root.get(), 
                                                root->left->left.get(), 
                                                root->left->right.get());
    std::cout << "LCA вузлів 4 та 5: " << (lca ? lca->data : -1) << "\n";

    // Пам'ять звільниться сама при виході з функції завдяки std::unique_ptr
    return 0;
}
```
:::

---

## 🔧 Аналіз системних пасток та інженерні рішення

1. **Захист від переповнення стеку:**
   Рекурсивні обходи є прийнятними лише для підтверджено збалансованих дерев (AVL, Red-Black), де висота строго обмежена `O(log n)`. У високодеталізованих системах зберігання даних або при роботі з недоввіреними зовнішніми даними слід завжди віддавати перевагу ітеративним обходам із власним стеком у купі (Heap RAM) або алгоритму Морріса.

2. **Оптимізація виділення пам'яті (Arena Allocators):**
   Часті виклики `malloc` або `new` для кожного з мільйонів вузлів створюють фрагментацію пам'яті та призводять до значних накладних витрат метаданих аллокатора. Для продуктивних систем (компілятори, бази даних) вузли дерева виділяють аренами — великими суцільними блоками (наприклад, по 4 МБ), що прискорює створення вузлів у 10–20 разів і відновлює кеш-локальність.

3. **Багатопотокова синхронізація:**
   Двійкові дерева за своєю природою не є побічно безпечними для паралельного запису (англ. *thread-safe*). Якщо один потік модифікує вказівник `left` під час обходу іншим потоком, виникає стан гонки (англ. *data race*). Для безпечної паралельної роботи застосовують каскадні блокування (англ. *fine-grained lock coupling*), читацько-письменницькі блокування (`std::shared_mutex`) або персистентні двійкові дерева з копіюванням при записі (Copy-on-Write).

4. **Підсумок інженерної практики:**
   Двійкове дерево є універсальною системною структурою. Вибір між вказівниковим та масивним поданням залежить від того, чи потребує алгоритм динамічного перебудування гілок, чи вимагає максимальної кеш-локальності та лінійної швидкості обчислень.
