# 📋 Інтерфейс та методи операторного класу GiST

Узагальнене пошукове дерево GiST (Generalized Search Tree) — це розширюваний шаблон індексного дерева, який абстрагує фізичне керування дисковими сторінками, буферним пулом, журналами випереджального запису (WAL), блокуваннями конкурентного доступу та алгоритмами відновлення від конкретної предметної області даних.

Традиційне B-дерево жорстко прив'язане до лінійного порядку «менше / більше» (`<`, `>`), тому воно принципово не здатне індексувати двовимірні фігури, географічні полігони, тривимірні об'єкти, діапазони дат або текстові множини. GiST замінює скалярні ключі довільними предикатами ієрархії. Щоб реалізувати новий спеціалізований метод доступу (наприклад, R-дерево для геоданих PostGIS або індекс перетинів часових інтервалів), розробник не створює нову дискову структуру з нуля, а визначає функції зворотного виклику (callbacks) користувацького операторного класу (Operator Class).

Нижче наведено технічний довідник функцій, структур даних, контрактних інваріантів та протоколу взаємодії інтерфейсу GiST (на прикладі PostgreSQL Storage Engine API).

## 1. Базові структури даних GiST

Кожен елемент дерева всередині дискової сторінки представлений структурою `GISTENTRY`. Вона об'єднує ключ предикату, покажчик на реляцію, адресу сторінки та службові прапорці стану.

:::tabs
```c
#include "postgres.h"
#include "access/gist.h"
#include "access/itup.h"

/* Запис елемента індексу GiST у C API */
typedef struct GISTENTRY {
    Datum       key;        /* Значення ключа або обмежувальний предикат (наприклад, BOX) */
    Relation    rel;        /* Дескриптор індексованої таблиці каталогу */
    Page        page;       /* Вказівник на дискову сторінку в буферному пулі */
    OffsetNumber offset;    /* Порядковий номер кортежу на сторінці (Line Pointer) */
    bool        leafkey;    /* true, якщо запис розміщений у листовому вузлі */
    bool        is_null;    /* true, якщо значення індексованого стовпця є NULL */
} GISTENTRY;

/* Вектор елементів сторінки для операцій Union та PickSplit */
typedef struct GistEntryVector {
    int32       n;          /* Кількість елементів у масиві */
    GISTENTRY   vector[FLEXIBLE_ARRAY_MEMBER];
} GistEntryVector;

/* Результат розщеплення сторінки: розподіл записів між двома сторінками */
typedef struct GIST_SPLITVEC {
    OffsetNumber *spl_left;       /* Масив зсувів кортежів для лівої нової сторінки */
    int           spl_nleft;      /* Кількість елементів ліворуч */
    Datum         spl_ldatum;     /* Об'єднаний узагальнювальний ключ (Union) лівої сторінки */

    OffsetNumber *spl_right;      /* Масив зсувів кортежів для правої нової сторінки */
    int           spl_nright;     /* Кількість елементів праворуч */
    Datum         spl_rdatum;     /* Об'єднаний узагальнювальний ключ (Union) правої сторінки */
} GIST_SPLITVEC;
```
```cpp
#include <cstdint>
#include <span>
#include <vector>
#include <memory>
#include <optional>

/* Ідіоматична C++ обгортка над внутрішніми структурами GiST */
struct GistEntryView {
    uintptr_t raw_key{0};
    uint32_t page_id{0};
    uint16_t offset{0};
    bool is_leaf{false};
    bool is_null{false};
};

struct GistSplitResult {
    std::vector<uint16_t> left_offsets;
    uintptr_t left_union_key{0};

    std::vector<uint16_t> right_offsets;
    uintptr_t right_union_key{0};
};

class IGistOperatorClass {
public:
    virtual ~IGistOperatorClass() = default;

    [[nodiscard]] virtual bool consistent(const GistEntryView& entry,
                                          uintptr_t query,
                                          uint16_t strategy,
                                          bool& out_recheck) const = 0;

    [[nodiscard]] virtual uintptr_t compute_union(std::span<const GistEntryView> entries) const = 0;

    [[nodiscard]] virtual float penalty(const GistEntryView& orig_entry,
                                        const GistEntryView& new_entry) const = 0;

    [[nodiscard]] virtual GistSplitResult pick_split(std::span<const GistEntryView> entries) const = 0;

    [[nodiscard]] virtual bool equal(uintptr_t key_a, uintptr_t key_b) const = 0;
};
```
:::

## 2. Специфікація методів операторного класу GiST

Для реєстрації повнофункціонального операторного класу GiST необхідно реалізувати 7 обов'язкових функцій та опціональний метод для сортування за відстанню:

### 1. `consistent` — Перевірка узгодженості предикату запиту
Функція викликається планувальником та виконавцем запитів під час обходу дерева для кожного елемента вузла. Вона визначає, чи може даний запис (або піддерево, яке він покриває) задовольнити умову вибірки `WHERE column OPERATOR query`.

Якщо піддерево задовольняє умову, пошук продовжується вниз за цим покажчиком. Якщо повертається `false`, уся гілка піддерева відсікається, що усуває необхідність завантаження сотень дочірніх сторінок з диска.

Якщо тип індексу використовує наближене стиснення (наприклад, замінює складний полігон із тисячею вершин на його прямокутний габарит MBR), метод встановлює вихідний прапорець `*recheck = true`. У цьому випадку СУБД після вилучення рядка з купи автоматично виконає точну геометричну перевірку по оригінальних даних таблиці.

### 2. `union` — Об'єднання множини ключів сторінки
Функція обчислює мінімальний узагальнений предикат (Super-predicate), що повністю охоплює всі записи, розміщені на дисковій сторінці. Для геопросторових індексів це мінімальний обмежувальний прямокутник, який містить усі об'єкти сторінки. Отриманий узагальнений ключ зберігається у батьківському вузлі як дороговказ до цієї сторінки.

### 3. `compress` / `decompress` — Трансформація та стиснення даних
Метод `compress` перетворює тип колонки таблиці (наприклад, складну фігуру `POLYGON` або довільний геометричний контур) у компактний внутрішній формат індексу (`BOX` з 4 чисел із рухомою комою). Метод `decompress` виконує зворотну операцію, якщо для перевірки предиката потрібне відновлення повної структури.

### 4. `penalty` — Обчислення штрафу за розширення області
Визначає додаткову вартість (приріст площі чи об'єму) у разі вставки нового елемента в конкретне піддерево під час спуску від кореня. Алгоритм вставки обчислює значення penalty для кожного дочірнього вузла й обирає піддерево з найменшим штрафом, мінімізуючи розростання обмежувальних рамок.

### 5. `picksplit` — Алгоритм розщеплення переповненої сторінки
Коли на дисковій сторінці закінчується вільне місце під час вставки нового елемента, GiST викликає `picksplit`, щоб розділити записи між двома новими сторінками. Якісний алгоритм розщеплення (наприклад, квадратичний або лінійний алгоритм Гуттмана) мінімізує перекриття та сумарну площу двох утворених обмежувальних областей, запобігаючи деградації пошуку.

### 6. `equal` — Перевірка еквівалентності ключів
Порівнює два значення узагальнених ключів індексу на повну ідентичність для усунення дублікатів та оптимізації оновлень.

### 7. `distance` (Опціонально) — Розрахунок відстані для kNN-пошуку
Обчислює мінімальну відстань від запитуваної точки до обмежувальної області внутрішнього вузла або до конкретної геометрії в листовому вузлі. Це дозволяє організувати чергу з пріоритетом для миттєвого пошуку найближчих географічних об'єктів (`ORDER BY location <-> point(...) LIMIT k`) без перебору всієї таблиці.

:::tabs
```c
#include "postgres.h"
#include "fmgr.h"
#include "access/gist.h"

/* Сигнатури експортованих C-функцій операторного класу GiST */

Datum my_gist_consistent(PG_FUNCTION_ARGS) {
    GISTENTRY *entry = (GISTENTRY *) PG_GETARG_POINTER(0);
    Datum query = PG_GETARG_DATUM(1);
    StrategyNumber strategy = (StrategyNumber) PG_GETARG_UINT16(2);
    bool *recheck = (bool *) PG_GETARG_POINTER(4);

    *recheck = false; /* Встановити true, якщо стиснення втратне */
    /* Обчислення перетину або вміщення предикату */
    PG_RETURN_BOOL(true);
}

Datum my_gist_union(PG_FUNCTION_ARGS) {
    GistEntryVector *entryvec = (GistEntryVector *) PG_GETARG_POINTER(0);
    int *sizep = (int *) PG_GETARG_POINTER(1);
    /* Обчислення спільного обмежувального прямокутника для всіх entryvec->vector */
    PG_RETURN_DATUM((Datum) 0);
}

Datum my_gist_penalty(PG_FUNCTION_ARGS) {
    GISTENTRY *origentry = (GISTENTRY *) PG_GETARG_POINTER(0);
    GISTENTRY *newentry = (GISTENTRY *) PG_GETARG_POINTER(1);
    float *penalty = (float *) PG_GETARG_POINTER(2);
    /* Penalty = Area(Union(orig, new)) - Area(orig) */
    *penalty = 0.0f;
    PG_RETURN_POINTER(penalty);
}

Datum my_gist_picksplit(PG_FUNCTION_ARGS) {
    GistEntryVector *entryvec = (GistEntryVector *) PG_GETARG_POINTER(0);
    GIST_SPLITVEC *v = (GIST_SPLITVEC *) PG_GETARG_POINTER(1);
    /* Квадратичний або лінійний поділ Гуттмана */
    PG_RETURN_POINTER(v);
}
```
```cpp
#include <iostream>
#include <span>
#include <vector>
#include <algorithm>
#include <cmath>

/* Двовимірний обмежувальний прямокутник (Bounding Box) */
struct BoundingBox {
    double xmin{0.0}, ymin{0.0}, xmax{0.0}, ymax{0.0};

    [[nodiscard]] double area() const noexcept {
        return std::max(0.0, xmax - xmin) * std::max(0.0, ymax - ymin);
    }

    [[nodiscard]] bool intersects(const BoundingBox& other) const noexcept {
        return !(xmin > other.xmax || xmax < other.xmin ||
                 ymin > other.ymax || ymax < other.ymin);
    }

    [[nodiscard]] BoundingBox enclose(const BoundingBox& other) const noexcept {
        return {
            std::min(xmin, other.xmin),
            std::min(ymin, other.ymin),
            std::max(xmax, other.xmax),
            std::max(ymax, other.ymax)
        };
    }
};

/* C++ реалізація логіки обчислення штрафу та перевірки предикатів */
class BoxGistOperator final {
public:
    [[nodiscard]] static bool consistent(const BoundingBox& entry_box,
                                         const BoundingBox& query_box,
                                         uint16_t strategy,
                                         bool& out_recheck) noexcept {
        out_recheck = false;
        switch (strategy) {
            case 1: /* Перетин (Overlaps: &&) */
                return entry_box.intersects(query_box);
            case 2: /* Вміщення (Contains: @>) */
                return entry_box.xmin <= query_box.xmin && entry_box.xmax >= query_box.xmax &&
                       entry_box.ymin <= query_box.ymin && entry_box.ymax >= query_box.ymax;
            default:
                return false;
        }
    }

    [[nodiscard]] static BoundingBox compute_union(std::span<const BoundingBox> boxes) noexcept {
        if (boxes.empty()) return {};
        BoundingBox acc = boxes.front();
        for (size_t i = 1; i < boxes.size(); ++i) {
            acc = acc.enclose(boxes[i]);
        }
        return acc;
    }

    [[nodiscard]] static float penalty(const BoundingBox& orig_box,
                                       const BoundingBox& new_box) noexcept {
        const double current_area = orig_box.area();
        const double union_area = orig_box.enclose(new_box).area();
        return static_cast<float>(union_area - current_area);
    }
};
```
:::

## 3. Реєстрація операторного класу мовою SQL

Після збирання модуля у динамічну бібліотеку `.so` операторний клас пов'язується з типом даних і реєструється в системному каталозі:

```sql
CREATE OPERATOR CLASS box_gist_ops
    DEFAULT FOR TYPE box USING gist AS
    OPERATOR 1  && (box, box),      -- Перетин фігур
    OPERATOR 2  @> (box, box),      -- Повне вміщення
    OPERATOR 3  <@ (box, box),      -- Вміщено у фігуру
    OPERATOR 4  ~= (box, box),      -- Геометрична рівність
    FUNCTION 1  my_gist_consistent(internal, box, smallint, oid, internal),
    FUNCTION 2  my_gist_union(internal, internal),
    FUNCTION 3  my_gist_compress(internal),
    FUNCTION 4  my_gist_decompress(internal),
    FUNCTION 5  my_gist_penalty(internal, internal, internal),
    FUNCTION 6  my_gist_picksplit(internal, internal),
    FUNCTION 7  my_gist_equal(box, box, internal);
```

## 4. Контрактні інваріанти та протокол взаємодії з рушієм

Під час розробки операторного класу необхідно неухильно дотримуватися трьох математичних правил:

1. **Інваріант монотонності об'єднання (Union Monotonicity):** Для будь-якої сторінки з набором записів `E_1, E_2, ..., E_k`, узагальнений ключ `U = Union(E_1, ..., E_k)` зобов'язаний покривати кожен окремий елемент: `Contains(U, E_i) == true` для всіх `i`. Якщо хоча б один елемент виходить за межі узагальненого ключа, він стане невидимим для пошукових запитів.
2. **Інваріант коректності відсікання:** Якщо `Consistent(U, Query) == false`, то жоден кортеж усередині цієї гілки піддерева не може дати `true` для `Query`. Помилка у реалізації `consistent` призводить до повернення неповної вибірки даних (false negatives).
3. **Керування пам'яттю у контексті виклику:** Усі обчислення у функціях `union`, `compress` та `picksplit` виконуються у швидкоплинних контекстах пам'яті (`CurrentMemoryContext`). Створювані об'єкти `Datum` повинні виділятися за допомогою `palloc`, що гарантує їхнє автоматичне очищення після завершення транзакції або операції з буфером сторінки.

## 5. Протокол виконання запиту пошуку найближчих сусідів (kNN Search)

Під час виконання просторового запиту з сортуванням за відстанню `ORDER BY location <-> point(...) LIMIT k` рушій GiST не виконує повний обхід дерева. Він використовує алгоритм пошуку за першим найкращим збігом (Best-First Search) на базі черги з пріоритетом (Priority Queue):

1. У чергу з пріоритетом поміщається кореневий вузол із відстанню `0.0`.
2. На кожній ітерації алгоритм вилучає з черги елемент із мінімальною поточною відстанню:
   - Якщо це **внутрішній вузол**, для кожного його дочірнього прямокутника викликається метод `Distance()`, і всі дочірні вузли додаються в чергу з розрахованими відстанями.
   - Якщо це **листовий вузол**, викликається метод `Distance()` для точного об'єкта. Оскільки черга гарантує мінімальність відстані, вилучений листовий об'єкт гарантовано є найближчим серед усіх ще не перевірених піддерев.
3. Щойно алгоритм вилучає з черги `k` листових записів, виконання запиту негайно зупиняється. Решта дерева навіть не зчитується з диска.
