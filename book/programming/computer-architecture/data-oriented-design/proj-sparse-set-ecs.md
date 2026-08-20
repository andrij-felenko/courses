# ⚙️ Реалізація пулу сутностей та компонентів на основі Sparse Set

У Data-Oriented Design ключовою вимогою до структури зберігання компонентів є розв'язання фундаментальної інженерної суперечності між довільним доступом та швидкістю ітерації. 

З одного боку, ігрова логіка, реакція на події, взаємодія з мережею та скрипти вимагають миттєвої перевірки наявності та читання компонента за числовим ідентифікатором сутності (`Entity ID`) за час `O(1)`. З іншого боку, обчислювальні цикли фізики, симуляції частинок, анімації та рендерингу вимагають суцільної, неперервної пам'яті без дірок і пропусків, щоб апаратний префетчер процесора та векторні інструкції SIMD (AVX2/NEON) працювали на піковій швидкості.

Структура розрідженої множини (англ. *Sparse Set*) бездоганно розв'язує цю задачу: вона поєднує пряму адресацію за ідентифікатором сутності з лінійним щільним розміщенням даних, гарантуючи додавання, видалення та перевірку за `O(1)`, а ітерацію — з максимальною просторовою локальністю та нульовим простоєм кешу.

---

### Архітектура структури та розподіл пам'яті

Структура складається з трьох ключових масивів:
1. **`sparse` (розріджений масив):** індексується безпосередньо числовим значенням `Entity ID`. Кожен елемент масиву зберігає індекс відповідного запису в щільному масиві або спеціальний маркер `INVALID_INDEX` (`UINT32_MAX`). Цей масив забезпечує пряму адресацію за час `O(1)`.
2. **`dense_entities` (щільний масив ідентифікаторів):** неперервно зберігає `Entity ID` тих сутностей, які реально володіють цим компонентом на даний момент.
3. **`dense_data` (щільний масив компонентів):** неперервно зберігає самі структури даних компонентів (наприклад, координати або швидкості), розташовані паралельно до `dense_entities`.

```
Entity ID: 5 ──> sparse[5] = 1 ──> dense_entities[1] = 5
                                 dense_pos[1]      = { x: 10.0, y: 20.0, z: 0.0 }
                                 dense_vel[1]      = { vx: 1.0, vy: 0.0, vz: 0.0 }
```

#### Покроковий аналіз операції видалення Swap-and-Pop
Головною перевагою Sparse Set перед звичайними масивами є вилучення компонентів за час `O(1)` без виникнення порожнин (фрагментації) у щільному масиві:

1. **Пошук за індексом:** Знаходимо індекс `removed_idx = sparse[entity]` видаленого компонента в щільному масиві.
2. **Перевірка позиції:** Якщо `removed_idx` уже є останнім елементом масиву (`last_idx = count - 1`), ми просто зменшуємо лічильник `count` на 1 і встановлюємо `sparse[entity] = INVALID_INDEX`.
3. **Перенесення останнього елемента:** Якщо елемент знаходиться всередині масиву, ми копіюємо дані останнього активного елемента (`last_idx`) у чарунку `removed_idx`.
4. **Синхронізація розрідженого індексу:** Для перенесеної сутності `last_entity = dense_entities[last_idx]` оновлюємо запис у розрідженому масиві: `sparse[last_entity] = removed_idx`.
5. **Очищення та зменшення розміру:** Встановлюємо `sparse[entity] = INVALID_INDEX` і декрементуємо `count`.

Завдяки цьому щільний масив завжди лишається компактним монолітним блоком пам'яті від індексу `0` до `count - 1`, не вимагаючи жодних операцій зсуву або перерозподілу пам'яті.

---

### Робоча реалізація на C та C++

Нижче наведено повну робочу реалізацію сховища позицій і швидкостей на базі Sparse Set.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define INVALID_INDEX UINT32_MAX

typedef uint32_t Entity;

typedef struct {
    float x;
    float y;
    float z;
} Position;

typedef struct {
    float vx;
    float vy;
    float vz;
} Velocity;

/* Сховище компонентів Position та Velocity на базі Sparse Set */
typedef struct {
    uint32_t* sparse;
    uint32_t  sparse_capacity;
    
    Entity*   dense_entities;
    Position* dense_pos;
    Velocity* dense_vel;
    uint32_t  count;
    uint32_t  dense_capacity;
} PositionPool;

bool pool_init(PositionPool* pool, uint32_t max_entities, uint32_t initial_capacity) {
    pool->sparse = (uint32_t*)malloc(sizeof(uint32_t) * max_entities);
    if (!pool->sparse) return false;
    
    for (uint32_t i = 0; i < max_entities; ++i) {
        pool->sparse[i] = INVALID_INDEX;
    }
    pool->sparse_capacity = max_entities;

    pool->dense_entities = (Entity*)malloc(sizeof(Entity) * initial_capacity);
    pool->dense_pos      = (Position*)malloc(sizeof(Position) * initial_capacity);
    pool->dense_vel      = (Velocity*)malloc(sizeof(Velocity) * initial_capacity);
    
    if (!pool->dense_entities || !pool->dense_pos || !pool->dense_vel) {
        free(pool->sparse);
        free(pool->dense_entities);
        free(pool->dense_pos);
        free(pool->dense_vel);
        return false;
    }

    pool->count = 0;
    pool->dense_capacity = initial_capacity;
    return true;
}

void pool_free(PositionPool* pool) {
    free(pool->sparse);
    free(pool->dense_entities);
    free(pool->dense_pos);
    free(pool->dense_vel);
    memset(pool, 0, sizeof(PositionPool));
}

bool pool_has(const PositionPool* pool, Entity e) {
    if (e >= pool->sparse_capacity) return false;
    return pool->sparse[e] != INVALID_INDEX;
}

bool pool_add(PositionPool* pool, Entity e, Position pos, Velocity vel) {
    if (e >= pool->sparse_capacity) return false;
    if (pool_has(pool, e)) return false;

    if (pool->count >= pool->dense_capacity) {
        uint32_t new_cap = pool->dense_capacity * 2;
        Entity* new_ent   = (Entity*)realloc(pool->dense_entities, sizeof(Entity) * new_cap);
        Position* new_pos = (Position*)realloc(pool->dense_pos, sizeof(Position) * new_cap);
        Velocity* new_vel = (Velocity*)realloc(pool->dense_vel, sizeof(Velocity) * new_cap);
        if (!new_ent || !new_pos || !new_vel) return false;
        
        pool->dense_entities = new_ent;
        pool->dense_pos      = new_pos;
        pool->dense_vel      = new_vel;
        pool->dense_capacity = new_cap;
    }

    uint32_t idx = pool->count;
    pool->dense_entities[idx] = e;
    pool->dense_pos[idx]      = pos;
    pool->dense_vel[idx]      = vel;
    pool->sparse[e]           = idx;
    pool->count++;
    return true;
}

bool pool_remove(PositionPool* pool, Entity e) {
    if (!pool_has(pool, e)) return false;

    uint32_t removed_idx = pool->sparse[e];
    uint32_t last_idx    = pool->count - 1;

    if (removed_idx != last_idx) {
        Entity last_entity = pool->dense_entities[last_idx];
        
        /* Копіюємо останній елемент на місце видаленого */
        pool->dense_entities[removed_idx] = last_entity;
        pool->dense_pos[removed_idx]      = pool->dense_pos[last_idx];
        pool->dense_vel[removed_idx]      = pool->dense_vel[last_idx];

        /* Оновлюємо розріджений індекс перенесеної сутності */
        pool->sparse[last_entity] = removed_idx;
    }

    pool->sparse[e] = INVALID_INDEX;
    pool->count--;
    return true;
}

/* Система фізики: суто лінійна обробка суміжних буферів */
void movement_system(PositionPool* pool, float dt) {
    Position* restrict pos = pool->dense_pos;
    const Velocity* restrict vel = pool->dense_vel;
    const uint32_t count = pool->count;

    #pragma omp simd
    for (uint32_t i = 0; i < count; ++i) {
        pos[i].x += vel[i].vx * dt;
        pos[i].y += vel[i].vy * dt;
        pos[i].z += vel[i].vz * dt;
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <cstdint>
#include <limits>
#include <span>
#include <optional>
#include <algorithm>

using Entity = std::uint32_t;
inline constexpr Entity kInvalidEntity = std::numeric_limits<Entity>::max();
inline constexpr std::uint32_t kInvalidIndex = std::numeric_limits<std::uint32_t>::max();

struct Position {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

struct Velocity {
    float vx{0.0f};
    float vy{0.0f};
    float vz{0.0f};
};

template <typename TComponent>
class ComponentPool {
public:
    explicit ComponentPool(std::size_t max_entities = 100'000)
        : sparse_(max_entities, kInvalidIndex) {}

    [[nodiscard]] bool has(Entity e) const noexcept {
        return e < sparse_.size() && sparse_[e] != kInvalidIndex;
    }

    void add(Entity e, TComponent comp) {
        if (e >= sparse_.size()) {
            sparse_.resize(std::max(sparse_.size() * 2, static_cast<std::size_t>(e + 1)), kInvalidIndex);
        }
        if (has(e)) {
            data_[sparse_[e]] = comp;
            return;
        }

        const auto idx = static_cast<std::uint32_t>(dense_entities_.size());
        dense_entities_.push_back(e);
        data_.push_back(comp);
        sparse_[e] = idx;
    }

    bool remove(Entity e) noexcept {
        if (!has(e)) {
            return false;
        }

        const std::uint32_t removed_idx = sparse_[e];
        const std::uint32_t last_idx = static_cast<std::uint32_t>(dense_entities_.size() - 1);

        if (removed_idx != last_idx) {
            const Entity last_entity = dense_entities_[last_idx];
            dense_entities_[removed_idx] = last_entity;
            data_[removed_idx] = std::move(data_[last_idx]);
            sparse_[last_entity] = removed_idx;
        }

        sparse_[e] = kInvalidIndex;
        dense_entities_.pop_back();
        data_.pop_back();
        return true;
    }

    [[nodiscard]] TComponent* get(Entity e) noexcept {
        if (!has(e)) return nullptr;
        return &data_[sparse_[e]];
    }

    [[nodiscard]] std::span<TComponent> data() noexcept {
        return data_;
    }

    [[nodiscard]] std::span<const TComponent> data() const noexcept {
        return data_;
    }

    [[nodiscard]] std::size_t size() const noexcept {
        return data_.size();
    }

private:
    std::vector<std::uint32_t> sparse_;
    std::vector<Entity>        dense_entities_;
    std::vector<TComponent>    data_;
};

// Система руху, що оперує безпосередньо неперервними зрізами пам'яті
void update_movement(std::span<Position> positions, std::span<const Velocity> velocities, float dt) noexcept {
    const std::size_t n = std::min(positions.size(), velocities.size());
    for (std::size_t i = 0; i < n; ++i) {
        positions[i].x += velocities[i].vx * dt;
        positions[i].y += velocities[i].vy * dt;
        positions[i].z += velocities[i].vz * dt;
    }
}
```
:::

---

### Апаратний аналіз та векторизація SIMD

Коли компілятор (GCC або Clang із прапорцем `-O3 -march=native`) обробляє функцію `movement_system`, наявність ключового слова `restrict` (або `__restrict`) усуває припущення про можливе накладання пам'яті (англ. *pointer aliasing*).

Оскільки масиви `dense_pos` та `dense_vel` лежать неперервно, компілятор розгортає цикл у векторні інструкції AVX2:

```assembly
.LBB0_4:
    vmovups (%rsi,%rax), %ymm0         ; Завантаження 8 чисел float швидкості
    vmovups 32(%rsi,%rax), %ymm1       ; Завантаження наступних 8 чисел float швидкості
    vmulps  %ymm2, %ymm0, %ymm0        ; Множення vel * dt (8 елементів за 1 такт)
    vmulps  %ymm2, %ymm1, %ymm1
    vaddps  (%rdi,%rax), %ymm0, %ymm0  ; Додавання pos + (vel * dt)
    vaddps  32(%rdi,%rax), %ymm1, %ymm1
    vmovups %ymm0, (%rdi,%rax)         ; Запис оновлених 8 координат у пам'ять
    vmovups %ymm1, 32(%rdi,%rax)
    addq    $64, %rax                  ; Зсув на 64 байти (1 кеш-лінія)
    cmpq    %rcx, %rax
    jb      .LBB0_4
```

Кожна ітерація розгорнутого векторного циклу обробляє **16 координат за кілька тактів процесора**, досягаючи теоретичної межі пропускної здатності локального кешу L1D.

---

### Ітерація за перетином кількох компонентів (Multi-Component Queries)

Коли система вимагає одночасної присутності двох або більше компонентів (наприклад, сутність мусить мати і `Position`, і `Velocity`, і `Health`), Sparse Set використовує стратегію обходу за **найменшим пулом**:

1. Система порівнює розміри (`count`) пулів усіх запитуваних компонентів;
2. Обхід виконується за щільним масивом того пулу, який містить найменшу кількість елементів (англ. *smallest pool iteration*);
3. Для кожного елемента найменшого пулу система перевіряє наявність інших компонентів за час `O(1)` шляхом прямого звернення до їхніх розріджених масивів `sparse`.

Такий алгоритм гарантує, що кількість перевірок ніколи не перевищує розмір найменшого набору даних, повністю уникаючи повного декартового сканування або побудови важких геш-таблиць.

---

### Сортування та просторове групування щільного масиву

Оскільки порядок сутностей у щільному масиві `dense_entities` та `dense_data` не впливає на коректність ідентифікації через `sparse`, дані можна періодично сортувати за просторовими критеріями:

1. **Сортування за Z-кривою (Morton Order) або просторовою сіткою:** Сутності, що знаходяться поруч у тривимірному віртуальному світі, переставляються так, щоб вони лежали в сусідніх комірках щільного масиву;
2. **Перевага для систем колізій та рендерингу:** Коли алгоритм перевірки зіткнень опрацьовує фізичні тіла в одній просторовій чарунці, всі необхідні координати сусідніх об'єктів уже завантажені в кеш L1 під час обробки попереднього елемента. При перестановці оновлюються лише значення індексів у масиві `sparse`.

---

### Пастки та оптимізації для великих просторів ID

1. **Сторінкова організація (Paged Sparse Set):**
   Якщо максимальний `Entity ID` досягає мільйонів (наприклад, у відкритих світах із динамічною генерацією об'єктів), виділення суцільного плоского масиву `sparse` на гігабайти пам'яті є неприйнятним. У такому разі `sparse` перетворюють на дворівневий масив сторінок фіксованого розміру (типово по 4096 записів). Сторінка виділяється в динамічній пам'яті лише тоді, коли з'являється перша сутність із відповідного діапазону індексів, що знижує витрати пам'яті до фактично зайнятих кластерів.

2. **Інвалідація збережених покажчиків:**
   Оскільки алгоритм Swap-and-Pop постійно змінює фізичний порядок елементів усередині `dense_data`, збереження довгоживучих прямих покажчиків на компоненти (`Position* p = pool_get(e)`) між кадрами або фазами мутації призводить до звернення до чужих даних (Use-After-Move/Dangling Pointer). Усі міжсистемні зв'язки та посилання мають зберігатися виключно у вигляді числових `Entity ID`.
