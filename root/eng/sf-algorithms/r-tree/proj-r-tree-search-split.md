# ⚙️ Реалізація R-дерева: квадратичне розщеплення, віконний пошук та k-NN

Ця практична розробка містить вичерпний розбір архітектури та повну реалізацію двовимірного R-дерева мовами C та C++. Розглянутий рушій підтримує динамічну вставку геометричних прямокутників із класичним квадратичним розщепленням вузлів Гутмана (Quadratic Split), віконний пошук перетинів (Range Query) та евристичний пошук `k` найближчих сусідів (k-NN) на основі черги з пріоритетом.

## Архітектурний дизайн та організація пам'яті

Просторові структури даних висувають специфічні вимоги до організації пам'яті. На відміну від бінарних дерев пошуку, де кожен вузол має лише два дочірні покажчики, вузол R-дерева проєктується як компактний контейнер, оптимізований під розмір кеш-лінії процесора або сторінки дискового накопичувача.

Для навчальної та практичної реалізації обрано параметри `M = 4` (максимальна місткість вузла) та `m = 2` (мінімальна допустима наповненість, що складає рівно половину від `M`). Будь-який вузол системи знаходиться в одному з двох станів:
1. **Листковий вузол (`is_leaf = true`):** зберігає масив записів `(Box2D, object_id)`. Поле `Box2D` описує точні просторові межі об'єкта, а `object_id` є числовим дескриптором сутності в зовнішньому сховищі або таблиці реляційної бази даних.
2. **Внутрішній вузол (`is_leaf = false`):** зберігає масив записів `(Box2D, child_pointer)`. Тут `Box2D` є мінімальною обмежувальною рамкою (MBR), яка повністю охоплює всі дочірні прямокутники піддерева `child_pointer`.

### Поетапний аналіз механізмів обробки

Внутрішня логіка індексу розбивається на чотири взаємопов'язані алгоритмічні кроки:

#### 1. Спуск та вибір піддерева (ChooseLeaf)
Під час додавання нового прямокутника алгоритм рекурсивно спускається від кореня до найбільш підходящого листка. На кожному внутрішньому ярусі функція аналізує всі дочірні прямокутники й обчислює функцію приросту площі `ΔArea = Area(Base ⊕ New) - Area(Base)`. Об'єкт спрямовується у вузол, що вимагає найменшого розширення свого MBR. Якщо кілька вузлів дають однаковий приріст `ΔArea`, вибирається вузол із меншою початковою площею, що перешкоджає розростанню вже роздутих обмежувальних рамок.

#### 2. Квадратичне розщеплення (Quadratic Split)
Якщо після вставки кількість елементів у вузлі досягає `M + 1`, активується процедура розщеплення на два вузли:
- **Фаза PickSeeds:** перебираються всі `(M + 1) · M / 2` пар елементів. Обчислюється «мертва площа» об'єднаного прямокутника, яка не зайнята самими прямокутниками: `DeadArea(A, B) = Area(A ⊕ B) - Area(A) - Area(B)`. Пара з максимальною мертвою площею розноситься по двох різних вузлах, стаючи їхніми початковими зародками.
- **Фаза PickNext:** для кожного з решти елементів обчислюються прирости площ `d_1` та `d_2` відносно обох сформованих груп. Алгоритм знаходить елемент із максимальною різницею переваги `|d_1 - d_2|` і додає його до групи з меншим `ΔArea`.
- **Контроль дефіциту заповнення:** якщо залишок нерозподілених елементів разом із поточним розміром групи дорівнює мінімуму `m`, усі елементи, що лишилися, негайно скидаються в цю групу без подальших розрахунків. Це гарантує виконання інваріанта мінімальної наповненості.

#### 3. Віконний пошук (Range Query)
Алгоритм обходить дерево в глибину, перевіряючи перетин `box_intersects(node.box, query)`. Якщо перетину немає, рекурсія миттєво повертається назад, відсікаючи все піддерево. Лише при досягненні листка ідентифікатори об'єктів записуються у вектор результатів або передаються в користувацьку функцію зворотного виклику.

#### 4. Пошук k найближчих сусідів (k-NN)
Пошук найближчих реалізовано за схемою «best-first» із чергою пріоритетів (min-heap). У чергу поміщаються вузли та об'єкти з їхньою відстанню `MINDIST` до точки запиту. Оскільки черга завжди виштовхує елемент із найменшою можливою відстанню, перший витягнутий об'єкт-листок гарантовано є глобально найближчим сусідом, адже жодне нерозгорнуте піддерево не може мати точок ближче за його значення `MINDIST`.

## Аналіз обчислювальної складності та ефективності кешу

Розподіл обчислювальних витрат за операціями:
- **Пошук вікна (Range Query):** у середньому `O(log_M N + K)`, де `K` — кількість знайдених геометричних об'єктів. У найгіршому випадку, коли MBR сильно перекриваються або площа запиту покриває всю карту, алгоритм переглядає всі `N` елементів за час `O(N)`.
- **Вставка нового елемента (Insert):** спуск від кореня до листка вимагає `O(log_M N)` кроків. Якщо на листковому або проміжному рівні відбувається розщеплення, алгоритм `Quadratic Split` виконує `O(M^2)` операцій над масивом записів вузла. Оскільки висота дерева обмежена `h = ⌈log_M N⌉`, максимальний час повної вставки з каскадними розщепленнями до кореня становить `O(M^2 · log_M N)`.
- **Пошук k-NN:** завдяки впорядкуванню за метрикою `MINDIST` у двійковій купі, обхід відвідує мінімальну кількість гілок. Часова складність складає `O(k · log_M N)` за умови гарної просторової кластеризації.

Розмір вузла `M` безпосередньо впливає на кеш-локальність. У пам'яті сучасних процесорів лінійне сканування масиву з `4–16` записів `Box2D` відбувається практично без промахів кешу першого рівня L1 завдяки апаратній передпідкачці (Hardware Prefetching). У промислових СУБД (PostgreSQL / SQLite) розмір `M` підбирається так, щоб вузол повністю займав одну сторінку дискового блоку (зазвичай від 32 до 128 записів на вузол).

## Крайові випадки та тонкощі реалізації

Під час практичного використання R-дерев необхідно враховувати низку критичних ситуацій:
1. **Вироджені прямокутники з нульовою площею:** точки або строго горизонтальні й вертикальні відрізки мають нульову площу (`Area = 0`). Формули розширення площі та об'єднання повинні коректно працювати з нестрогими нерівностями (`<=` та `>=`), щоб уникнути ділення на нуль або неправильного визначення перетинів.
2. **Точкові збіги та однакові координати:** якщо кілька об'єктів мають повністю ідентичні координати MBR, `DeadArea` між ними дорівнює нулю. Алгоритм `PickSeeds` повинен коректно обробляти випадки, коли всі елементи мають нульовий розрив, обираючи довільну валідну пару без зависання циклу.
3. **Каскадне розщеплення до кореня:** якщо розщеплення листка спричиняє переповнення його батьківського вузла, поділ каскадно піднімається вгору. Якщо переповнюється корінь, створюється новий кореневий вузол із двома нащадками, і висота дерева збільшується на 1.

## Відмінності реалізацій мовами C та C++

- **У версії C:** керування пам'яттю здійснюється вручну через покажчики та структуру `union` у записі `RTreeEntry`. Для обходу результатів застосовується класичний патерн із передачею покажчика на функцію та контексту користувача `void* ctx`.
- **У версії C++:** застосовано сучасні ідіоми RAII та семантику переміщення (Move Semantics). Дерево володіє пам'яттю через `std::unique_ptr<RTreeNode>`, що повністю унеможливлює витоки пам'яті при винятках. Вузол зберігає динамічний вектор записів `std::vector<RTreeEntry>`, опційні поля змодельовано через `std::optional<long long>`, а черга k-NN реалізована через `std::priority_queue`.

## Вихідний код реалізації

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <float.h>
#include <math.h>

#define RTREE_MAX_ENTRIES 4
#define RTREE_MIN_ENTRIES 2

typedef struct {
    double min_x, min_y;
    double max_x, max_y;
} Box2D;

typedef struct {
    double x, y;
} Point2D;

typedef struct RTreeNode RTreeNode;

typedef struct {
    Box2D box;
    union {
        RTreeNode* child;
        long long id;
    } target;
} RTreeEntry;

struct RTreeNode {
    bool is_leaf;
    int count;
    RTreeEntry entries[RTREE_MAX_ENTRIES + 1];
};

typedef struct {
    RTreeNode* root;
} RTree;

/* Геометричні примітиви */

static inline Box2D box_create(double x1, double y1, double x2, double y2) {
    Box2D b = { x1 < x2 ? x1 : x2, y1 < y2 ? y1 : y2,
                x1 > x2 ? x1 : x2, y1 > y2 ? y1 : y2 };
    return b;
}

static inline double box_area(const Box2D* b) {
    return (b->max_x - b->min_x) * (b->max_y - b->min_y);
}

static inline Box2D box_combine(const Box2D* a, const Box2D* b) {
    Box2D res;
    res.min_x = a->min_x < b->min_x ? a->min_x : b->min_x;
    res.min_y = a->min_y < b->min_y ? a->min_y : b->min_y;
    res.max_x = a->max_x > b->max_x ? a->max_x : b->max_x;
    res.max_y = a->max_y > b->max_y ? a->max_y : b->max_y;
    return res;
}

static inline double box_enlargement(const Box2D* base, const Box2D* add) {
    Box2D combined = box_combine(base, add);
    return box_area(&combined) - box_area(base);
}

static inline bool box_intersects(const Box2D* a, const Box2D* b) {
    return (a->min_x <= b->max_x && a->max_x >= b->min_x &&
            a->min_y <= b->max_y && a->max_y >= b->min_y);
}

static inline double point_mindist_sq(const Point2D* p, const Box2D* b) {
    double dx = 0.0, dy = 0.0;
    if (p->x < b->min_x) dx = b->min_x - p->x;
    else if (p->x > b->max_x) dx = p->x - b->max_x;
    if (p->y < b->min_y) dy = b->min_y - p->y;
    else if (p->y > b->max_y) dy = p->y - b->max_y;
    return dx * dx + dy * dy;
}

/* Створення та очищення вузлів */

static RTreeNode* node_create(bool is_leaf) {
    RTreeNode* n = (RTreeNode*)malloc(sizeof(RTreeNode));
    if (!n) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }
    n->is_leaf = is_leaf;
    n->count = 0;
    return n;
}

static void node_free(RTreeNode* node) {
    if (!node) return;
    if (!node->is_leaf) {
        for (int i = 0; i < node->count; ++i) {
            node_free(node->entries[i].target.child);
        }
    }
    free(node);
}

static Box2D node_cover(const RTreeNode* node) {
    if (node->count == 0) return box_create(0, 0, 0, 0);
    Box2D res = node->entries[0].box;
    for (int i = 1; i < node->count; ++i) {
        res = box_combine(&res, &node->entries[i].box);
    }
    return res;
}

/* Алгоритм квадратичного розщеплення Гутмана */

static void split_node(RTreeNode* old_node, RTreeNode* new_node) {
    int total = old_node->count;
    RTreeEntry all[RTREE_MAX_ENTRIES + 1];
    for (int i = 0; i < total; ++i) all[i] = old_node->entries[i];

    /* 1. PickSeeds: знаходження пари з максимальною мертвою площею */
    int seed1 = 0, seed2 = 1;
    double max_d = -1.0;
    for (int i = 0; i < total; ++i) {
        for (int j = i + 1; j < total; ++j) {
            Box2D u = box_combine(&all[i].box, &all[j].box);
            double d = box_area(&u) - box_area(&all[i].box) - box_area(&all[j].box);
            if (d > max_d) {
                max_d = d;
                seed1 = i;
                seed2 = j;
            }
        }
    }

    bool taken[RTREE_MAX_ENTRIES + 1] = { false };
    taken[seed1] = true;
    taken[seed2] = true;

    old_node->count = 0;
    new_node->count = 0;
    new_node->is_leaf = old_node->is_leaf;

    old_node->entries[old_node->count++] = all[seed1];
    new_node->entries[new_node->count++] = all[seed2];

    Box2D box1 = all[seed1].box;
    Box2D box2 = all[seed2].box;
    int assigned = 2;

    /* 2. Розподіл решти елементів */
    while (assigned < total) {
        /* Перевірка умови мінімальної наповненості m */
        if (old_node->count + (total - assigned) == RTREE_MIN_ENTRIES) {
            for (int i = 0; i < total; ++i) {
                if (!taken[i]) {
                    old_node->entries[old_node->count++] = all[i];
                    taken[i] = true;
                    assigned++;
                }
            }
            break;
        }
        if (new_node->count + (total - assigned) == RTREE_MIN_ENTRIES) {
            for (int i = 0; i < total; ++i) {
                if (!taken[i]) {
                    new_node->entries[new_node->count++] = all[i];
                    taken[i] = true;
                    assigned++;
                }
            }
            break;
        }

        /* PickNext: вибір елемента з найбільшим контрастом розширення */
        int best_idx = -1;
        double max_diff = -1.0;
        for (int i = 0; i < total; ++i) {
            if (taken[i]) continue;
            double d1 = box_enlargement(&box1, &all[i].box);
            double d2 = box_enlargement(&box2, &all[i].box);
            double diff = fabs(d1 - d2);
            if (diff > max_diff) {
                max_diff = diff;
                best_idx = i;
            }
        }

        double d1 = box_enlargement(&box1, &all[best_idx].box);
        double d2 = box_enlargement(&box2, &all[best_idx].box);

        if (d1 < d2 || (d1 == d2 && box_area(&box1) < box_area(&box2)) ||
           (d1 == d2 && box_area(&box1) == box_area(&box2) && old_node->count <= new_node->count)) {
            old_node->entries[old_node->count++] = all[best_idx];
            box1 = box_combine(&box1, &all[best_idx].box);
        } else {
            new_node->entries[new_node->count++] = all[best_idx];
            box2 = box_combine(&box2, &all[best_idx].box);
        }
        taken[best_idx] = true;
        assigned++;
    }
}

/* Рекурсивна вставка */

static RTreeNode* insert_recursive(RTreeNode* node, const RTreeEntry* entry) {
    if (node->is_leaf) {
        node->entries[node->count++] = *entry;
    } else {
        /* ChooseLeaf евристика: обираємо дочірній вузол із найменшим розширенням */
        int best_idx = 0;
        double min_enl = box_enlargement(&node->entries[0].box, &entry->box);
        double min_area = box_area(&node->entries[0].box);

        for (int i = 1; i < node->count; ++i) {
            double enl = box_enlargement(&node->entries[i].box, &entry->box);
            double a = box_area(&node->entries[i].box);
            if (enl < min_enl || (enl == min_enl && a < min_area)) {
                min_enl = enl;
                min_area = a;
                best_idx = i;
            }
        }

        RTreeNode* split_child = insert_recursive(node->entries[best_idx].target.child, entry);
        node->entries[best_idx].box = node_cover(node->entries[best_idx].target.child);

        if (split_child) {
            RTreeEntry new_entry;
            new_entry.box = node_cover(split_child);
            new_entry.target.child = split_child;
            node->entries[node->count++] = new_entry;
        }
    }

    if (node->count > RTREE_MAX_ENTRIES) {
        RTreeNode* new_sibling = node_create(node->is_leaf);
        split_node(node, new_sibling);
        return new_sibling;
    }
    return NULL;
}

void rtree_insert(RTree* tree, Box2D box, long long id) {
    RTreeEntry entry;
    entry.box = box;
    entry.target.id = id;

    if (!tree->root) {
        tree->root = node_create(true);
        tree->root->entries[tree->root->count++] = entry;
        return;
    }

    RTreeNode* split_root = insert_recursive(tree->root, &entry);
    if (split_root) {
        RTreeNode* new_root = node_create(false);
        new_root->entries[0].box = node_cover(tree->root);
        new_root->entries[0].target.child = tree->root;
        new_root->entries[1].box = node_cover(split_root);
        new_root->entries[1].target.child = split_root;
        new_root->count = 2;
        tree->root = new_root;
    }
}

/* Віконний пошук */

static void search_recursive(const RTreeNode* node, const Box2D* query, void (*callback)(long long id, void* ctx), void* ctx) {
    for (int i = 0; i < node->count; ++i) {
        if (box_intersects(&node->entries[i].box, query)) {
            if (node->is_leaf) {
                callback(node->entries[i].target.id, ctx);
            } else {
                search_recursive(node->entries[i].target.child, query, callback, ctx);
            }
        }
    }
}

void rtree_search(const RTree* tree, Box2D query, void (*callback)(long long id, void* ctx), void* ctx) {
    if (tree->root) {
        search_recursive(tree->root, &query, callback, ctx);
    }
}

static void collect_results(long long id, void* ctx) {
    int* count = (int*)ctx;
    (*count)++;
    printf("Знайдено об'єкт id: %lld\n", id);
}

int main(void) {
    RTree tree = { NULL };

    /* Вставка 6 тестових геометричних об'єктів */
    rtree_insert(&tree, box_create(10, 10, 20, 20), 101);
    rtree_insert(&tree, box_create(15, 12, 25, 22), 102);
    rtree_insert(&tree, box_create(50, 60, 70, 80), 103);
    rtree_insert(&tree, box_create(55, 62, 75, 85), 104);
    rtree_insert(&tree, box_create(12, 14, 22, 24), 105);
    rtree_insert(&tree, box_create(80, 80, 90, 90), 106);

    printf("=== Віконний пошук у зоні [5, 5]x[30, 30] ===\n");
    int found = 0;
    rtree_search(&tree, box_create(5, 5, 30, 30), collect_results, &found);
    printf("Всього знайдено: %d об'єктів\n", found);

    node_free(tree.root);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <queue>
#include <cmath>
#include <algorithm>
#include <optional>

constexpr size_t RTREE_MAX_ENTRIES = 4;
constexpr size_t RTREE_MIN_ENTRIES = 2;

struct Point2D {
    double x{0.0};
    double y{0.0};
};

struct Box2D {
    double min_x{0.0};
    double min_y{0.0};
    double max_x{0.0};
    double max_y{0.0};

    [[nodiscard]] double area() const noexcept {
        return (max_x - min_x) * (max_y - min_y);
    }

    [[nodiscard]] static Box2D combine(const Box2D& a, const Box2D& b) noexcept {
        return {
            std::min(a.min_x, b.min_x),
            std::min(a.min_y, b.min_y),
            std::max(a.max_x, b.max_x),
            std::max(a.max_y, b.max_y)
        };
    }

    [[nodiscard]] double enlargement(const Box2D& add) const noexcept {
        return combine(*this, add).area() - area();
    }

    [[nodiscard]] bool intersects(const Box2D& other) const noexcept {
        return (min_x <= other.max_x && max_x >= other.min_x &&
                min_y <= other.max_y && max_y >= other.min_y);
    }

    [[nodiscard]] double mindist_sq(const Point2D& p) const noexcept {
        double dx = 0.0, dy = 0.0;
        if (p.x < min_x) dx = min_x - p.x;
        else if (p.x > max_x) dx = p.x - max_x;
        if (p.y < min_y) dy = min_y - p.y;
        else if (p.y > max_y) dy = p.y - max_y;
        return dx * dx + dy * dy;
    }
};

struct RTreeNode;

struct RTreeEntry {
    Box2D box;
    std::unique_ptr<RTreeNode> child{nullptr};
    std::optional<long long> id{std::nullopt};
};

struct RTreeNode {
    bool is_leaf{true};
    std::vector<RTreeEntry> entries;

    [[nodiscard]] Box2D cover() const noexcept {
        if (entries.empty()) return {};
        Box2D res = entries.front().box;
        for (size_t i = 1; i < entries.size(); ++i) {
            res = Box2D::combine(res, entries[i].box);
        }
        return res;
    }
};

class RTree {
private:
    std::unique_ptr<RTreeNode> root_{nullptr};

    static std::unique_ptr<RTreeNode> split_node(RTreeNode& old_node) {
        std::vector<RTreeEntry> all = std::move(old_node.entries);
        const size_t total = all.size();

        /* 1. PickSeeds */
        size_t seed1 = 0, seed2 = 1;
        double max_dead_area = -1.0;

        for (size_t i = 0; i < total; ++i) {
            for (size_t j = i + 1; j < total; ++j) {
                Box2D combined = Box2D::combine(all[i].box, all[j].box);
                double dead = combined.area() - all[i].box.area() - all[j].box.area();
                if (dead > max_dead_area) {
                    max_dead_area = dead;
                    seed1 = i;
                    seed2 = j;
                }
            }
        }

        auto new_node = std::make_unique<RTreeNode>();
        new_node->is_leaf = old_node.is_leaf;

        std::vector<bool> taken(total, false);
        taken[seed1] = true;
        taken[seed2] = true;

        old_node.entries.push_back(std::move(all[seed1]));
        new_node->entries.push_back(std::move(all[seed2]));

        Box2D box1 = old_node.entries.front().box;
        Box2D box2 = new_node->entries.front().box;
        size_t assigned = 2;

        /* 2. Розподіл решти елементів */
        while (assigned < total) {
            if (old_node.entries.size() + (total - assigned) == RTREE_MIN_ENTRIES) {
                for (size_t i = 0; i < total; ++i) {
                    if (!taken[i]) {
                        old_node.entries.push_back(std::move(all[i]));
                        taken[i] = true;
                        ++assigned;
                    }
                }
                break;
            }
            if (new_node->entries.size() + (total - assigned) == RTREE_MIN_ENTRIES) {
                for (size_t i = 0; i < total; ++i) {
                    if (!taken[i]) {
                        new_node->entries.push_back(std::move(all[i]));
                        taken[i] = true;
                        ++assigned;
                    }
                }
                break;
            }

            /* PickNext */
            size_t best_idx = 0;
            double max_diff = -1.0;
            for (size_t i = 0; i < total; ++i) {
                if (taken[i]) continue;
                double d1 = box1.enlargement(all[i].box);
                double d2 = box2.enlargement(all[i].box);
                double diff = std::abs(d1 - d2);
                if (diff > max_diff) {
                    max_diff = diff;
                    best_idx = i;
                }
            }

            double d1 = box1.enlargement(all[best_idx].box);
            double d2 = box2.enlargement(all[best_idx].box);

            if (d1 < d2 || (d1 == d2 && box1.area() < box2.area()) ||
               (d1 == d2 && box1.area() == box2.area() && old_node.entries.size() <= new_node->entries.size())) {
                box1 = Box2D::combine(box1, all[best_idx].box);
                old_node.entries.push_back(std::move(all[best_idx]));
            } else {
                box2 = Box2D::combine(box2, all[best_idx].box);
                new_node->entries.push_back(std::move(all[best_idx]));
            }
            taken[best_idx] = true;
            ++assigned;
        }

        return new_node;
    }

    static std::unique_ptr<RTreeNode> insert_recursive(RTreeNode& node, RTreeEntry entry) {
        if (node.is_leaf) {
            node.entries.push_back(std::move(entry));
        } else {
            /* ChooseLeaf евристика */
            size_t best_idx = 0;
            double min_enl = node.entries[0].box.enlargement(entry.box);
            double min_area = node.entries[0].box.area();

            for (size_t i = 1; i < node.entries.size(); ++i) {
                double enl = node.entries[i].box.enlargement(entry.box);
                double a = node.entries[i].box.area();
                if (enl < min_enl || (enl == min_enl && a < min_area)) {
                    min_enl = enl;
                    min_area = a;
                    best_idx = i;
                }
            }

            auto split_child = insert_recursive(*node.entries[best_idx].child, std::move(entry));
            node.entries[best_idx].box = node.entries[best_idx].child->cover();

            if (split_child) {
                RTreeEntry new_entry;
                new_entry.box = split_child->cover();
                new_entry.child = std::move(split_child);
                node.entries.push_back(std::move(new_entry));
            }
        }

        if (node.entries.size() > RTREE_MAX_ENTRIES) {
            return split_node(node);
        }
        return nullptr;
    }

    static void search_recursive(const RTreeNode& node, const Box2D& query, std::vector<long long>& results) {
        for (const auto& entry : node.entries) {
            if (entry.box.intersects(query)) {
                if (node.is_leaf) {
                    if (entry.id.has_value()) {
                        results.push_back(*entry.id);
                    }
                } else if (entry.child) {
                    search_recursive(*entry.child, query, results);
                }
            }
        }
    }

public:
    RTree() = default;

    void insert(Box2D box, long long id) {
        RTreeEntry entry{box, nullptr, id};

        if (!root_) {
            root_ = std::make_unique<RTreeNode>();
            root_->is_leaf = true;
            root_->entries.push_back(std::move(entry));
            return;
        }

        auto split_root = insert_recursive(*root_, std::move(entry));
        if (split_root) {
            auto new_root = std::make_unique<RTreeNode>();
            new_root->is_leaf = false;

            RTreeEntry e1{root_->cover(), std::move(root_), std::nullopt};
            RTreeEntry e2{split_root->cover(), std::move(split_root), std::nullopt};

            new_root->entries.push_back(std::move(e1));
            new_root->entries.push_back(std::move(e2));
            root_ = std::move(new_root);
        }
    }

    [[nodiscard]] std::vector<long long> search_range(const Box2D& query) const {
        std::vector<long long> results;
        if (root_) {
            search_recursive(*root_, query, results);
        }
        return results;
    }

    struct QueueItem {
        double dist_sq{0.0};
        const RTreeNode* node{nullptr};
        std::optional<long long> id{std::nullopt};

        bool operator>(const QueueItem& other) const noexcept {
            return dist_sq > other.dist_sq;
        }
    };

    [[nodiscard]] std::vector<long long> search_knn(const Point2D& query_point, size_t k) const {
        std::vector<long long> neighbors;
        if (!root_ || k == 0) return neighbors;

        std::priority_queue<QueueItem, std::vector<QueueItem>, std::greater<QueueItem>> pq;
        pq.push({root_->cover().mindist_sq(query_point), root_.get(), std::nullopt});

        while (!pq.empty() && neighbors.size() < k) {
            auto current = pq.top();
            pq.pop();

            if (current.id.has_value()) {
                neighbors.push_back(*current.id);
            } else if (current.node) {
                for (const auto& entry : current.node->entries) {
                    double d_sq = entry.box.mindist_sq(query_point);
                    if (current.node->is_leaf) {
                        pq.push({d_sq, nullptr, entry.id});
                    } else if (entry.child) {
                        pq.push({d_sq, entry.child.get(), std::nullopt});
                    }
                }
            }
        }
        return neighbors;
    }
};

int main() {
    RTree tree;

    /* Вставка тестових об'єктів */
    tree.insert({10, 10, 20, 20}, 101);
    tree.insert({15, 12, 25, 22}, 102);
    tree.insert({50, 60, 70, 80}, 103);
    tree.insert({55, 62, 75, 85}, 104);
    tree.insert({12, 14, 22, 24}, 105);
    tree.insert({80, 80, 90, 90}, 106);

    std::cout << "=== Віконний пошук у зоні [5, 5]x[30, 30] ===\n";
    auto in_range = tree.search_range({5, 5, 30, 30});
    for (auto id : in_range) {
        std::cout << "Знайдено об'єкт id: " << id << "\n";
    }

    std::cout << "\n=== Пошук 3 найближчих сусідів до точки (14, 14) ===\n";
    auto nearest = tree.search_knn({14.0, 14.0}, 3);
    for (size_t i = 0; i < nearest.size(); ++i) {
        std::cout << (i + 1) << "-й найближчий id: " << nearest[i] << "\n";
    }

    return 0;
}
```
:::
