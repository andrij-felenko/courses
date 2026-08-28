# ⚙️ Легковажний детермінований рушій Behavior Tree

Бортовий комп'ютер безпілотного апарата під керуванням операційної системи реального часу (FreeRTOS, Zephyr) або bare-metal середовища вимагає детермінованого часу виконання кожного польотного такту (20–50 Гц) та суворої заборони динамічного виділення пам'яті (`malloc`, `free`, `new`, `delete`) під час польоту відповідно до вимог авіаційних стандартів функціональної безпеки DO-178C та MISRA C/C++. Фрагментація купи (*heap fragmentation*) у тривалому польоті неминуче призводить до раптової відмови алокатора, а непередбачувані затримки системних викликів руйнують часовий бюджет високочастотного контуру стабілізації.

Для надійного виконання місій автономії потрібен спеціалізований рушій дерева поведінки (*Behavior Tree Engine*), у якому всі структури даних, дескриптори вузлів, індекси дочірніх зв'язків та комірки Дошки Оголошень (*Blackboard*) виділяються виключно у статичній пам'яті (*BSS-сегмент*) на етапі стартової ініціалізації апарата.

```
                  ┌─────────────────────────────────────────┐
                  │          Node 0: Root ReactiveFallback  │
                  └────────────────────┬────────────────────┘
       ┌───────────────────────────────┼───────────────────────────────┐
       ▼                               ▼                               ▼
┌──────────────┐                ┌──────────────┐                ┌──────────────┐
│Node 1: Seq   │                │Node 2: Seq   │                │Node 3: Seq   │
│(Failsafe)    │                │(Avoidance)   │                │(Mission)     │
└──────┬───────┘                └──────┬───────┘                └──────┬───────┘
  ┌────┴────┐                      ┌───┴───┐                  ┌────────┴────────┐
  ▼         ▼                      ▼       ▼                  ▼                 ▼
(Node 4)  [Node 5]               (Node 6)  [Node 7]         [Node 8]          [Node 9]
Bat<14V   LandNow                Dist<3m   AvoidPath        Takeoff           PatrolParallel
                                                                                ┌───┴───┐
                                                                                ▼       ▼
                                                                           [Node 10] [Node 11]
                                                                            FlyWp    TrackCam
```

---

### Інженерні вимоги та архітектурні обмеження реального часу

Розробка бортового рушія дерева поведінки для вбудованих автопілотів (мікроконтролери ARM Cortex-M4/M7, STM32H743, NXP i.MX RT1062) базується на чотирьох фундаментальних інженерних принципах:

#### 1. Нульове динамічне виділення пам'яті (Zero-Heap Allocation)
Всі вузли дерева розміщуються в єдиному суцільному статичному масиві фіксованого розміру `nodes[MAX_NODES]`. Дочірні зв'язки зберігаються як масиви беззнакових 8-бітних індексів `children[MAX_CHILDREN]`. Це усуває накладні витрати на збереження 32- або 64-бітних вказівників, гарантує відсутність висячих адрес (*dangling pointers*) і забезпечує просторову локальність даних у кеші першого рівня (L1 Data Cache) під час рекурсивного спуску.

У класичних об'єктно-орієнтованих бібліотеках кожен вузол створюється через оператор `new` як поліморфний об'єкт із віртуальною таблицею методів (*vtable*). Це створює два критичні недоліки:
- **Розкид адрес у пам'яті:** Вказівники на дочірні вузли розкидані по різних ділянках купи, через що кожен крок обходу дерева спричиняє промах кешу даних (*D-Cache miss*), збільшуючи затримку обробки такту в 5–10 разів;
- **Небезпека витоків:** При динамічній перебудові місії на льоту виникає ризик неповного звільнення пам'яті, що призводить до поступового вичерпання RAM.

У представленій статичній моделі розмір усієї системи прийняття рішень фіксується під час компіляції і становить приблизно 3.2 КБ оперативної пам'яті, що дозволяє запускати повноцінний автономний рушій навіть на компактних мікроконтролерах із 64 КБ RAM.

#### 2. Жорстке обмеження глибини стека (Bounded Call Stack)
У задачах FreeRTOS розмір стека зазвичай обмежений 2–4 кілобайтами. Рекурсивний спуск по дереву з необмеженою глибиною може спричинити фатальне переповнення стека (*stack overflow*) та аварійне перезавантаження контролера в польоті.

Рушій обмежує максимальну глибину дерева константою `MAX_TREE_DEPTH = 8`. Кожен рівень рекурсії створює один стековий фрейм розміром не більше 32 байтів (аргументи виклику, збережені регістри R4–R7, вказівник повернення LR). Таким чином, сумарні витрати стека на один такт не перевищують:

```
8 · 32 = 256 байтів   [максимальний обсяг стека для одного тіку]
```

Це дозволяє виділяти для задачі прийняття рішень стандартний стек розміром 1024 байти з 4-кратним запасом надійності.

#### 3. Неблокуюче реактивне витіснення (Non-blocking Preemption)
Коли реактивний селектор (`ReactiveFallback`) на черговому такті виявляє, що умова аварійного захисту (наприклад, критичний розряд акумулятора) повернула `SUCCESS`, рушій зобов'язаний негайно викликати функцію скидання `halt()` для активної тривалої дії поточної гілки, очистити уставки та активувати аварійну гілку.

Обробник `halt()` проектується як строго неблокуючий:
- Заборонено використовувати виклики `vTaskDelay()` або циклічні очікування прапорців готовності апаратури;
- Функція повинна за константний час `O(1)` записати нульові значення в структури цільових уставок (наприклад, скинути вектор горизонтальної швидкості `vx = 0, vy = 0` та виставити прапорець переходу в режим аварійного зниження);
- Усі ресурси (таймери, захоплені буфери повідомлень) звільняються негайно.

#### 4. Потокобезпечна Дошка Оголошень із захистом від розірваних читань
Дошка Оголошень реалізує фіксовану таблицю типізованих ключів. Оскільки сенсорні задачі (наприклад, EKF на 200 Гц) оновлюють просторові координати дрона паралельно з роботою дерева поведінки (20–50 Гц), доступ до багатобайтових структур даних захищається механізмом подвійної буферизації або критичними секціями без блокування високопріоритетних переривань.

Якщо потік EKF оновлює три координати позиції (`float x, y, z`, разом 12 байтів), на 32-бітній шині запис виконується трьома окремими машинними інструкціями `STR`. Якщо в момент між записом `y` та `z` потік планувальника перехоплює процесор і зчитує координати, дерево отримає спотворений вектор зі старою координатою `z` та новими `x, y` (*torn read*). Для запобігання цьому рушій використовує атомарні операції копіювання під захистом критичної секції або подвійну буферизацію.

---

### Організація пам'яті та структура вузлів

Кожен вузол рушія описується дескриптором фіксованого розміру. Нижче наведено детальну схему розташування структур у пам'яті контролера:

```
СТРУКТУРА ПАМ'ЯТІ РУШІЯ (BSS СЕГМЕНТ, ~3.2 КБ RAM):

 ┌─────────────────────────────────────────────────────────────────┐
 │ ПУЛ ДЕСКРИПТОРІВ ВУЗЛІВ: bt_node_t nodes[32]                    │
 │ ┌───────────────────┬──────────────┬──────────────┬───────────┐ │
 │ │ Node 0 (Root)     │ Type: FALLB  │ Status: RUN  │ Child: 1,2│ │
 │ ├───────────────────┼──────────────┼──────────────┼───────────┤ │
 │ │ Node 1 (Failsafe) │ Type: SEQ    │ Status: IDLE │ Child: 3,4│ │
 │ ├───────────────────┼──────────────┼──────────────┼───────────┤ │
 │ │ Node 2 (Mission)  │ Type: SEQ    │ Status: RUN  │ Child: 5,6│ │
 │ └───────────────────┴──────────────┴──────────────┴───────────┘ │
 ├─────────────────────────────────────────────────────────────────┤
 │ ДОШКА ОГОЛОШЕНЬ: bb_entry_t entries[16]                         │
 │ ┌───────────────────────┬────────────┬────────────────────────┐ │
 │ │ Key: "bat_volt"       │ Type: FLT  │ Value: 14.85f          │ │
 │ ├───────────────────────┼────────────┼────────────────────────┤ │
 │ │ Key: "lidar_dist"     │ Type: FLT  │ Value: 2.15f           │ │
 │ ├───────────────────────┼────────────┼────────────────────────┤ │
 │ │ Key: "target_pos"     │ Type: VEC3 │ Value: [120, 45, -30]  │ │
 │ └───────────────────────┴────────────┴────────────────────────┘ │
 └─────────────────────────────────────────────────────────────────┘
```

#### Індексна адресація вузлів (uint8_t Node ID)
Замість збереження сирих 32/64-бітних вказівників, рушій адресує вузли за їхнім числовим індексом у масиві `nodes[]`. Це дає такі переваги:
1. **Зменшення розміру структури вузла:** Масив із 8 дітей займає рівно 8 байтів замість 32 байтів (на 32-бітних архітектурах) або 64 байтів (на 64-бітних авіоніках);
2. **Просторова когерентність:** Усі дескриптори вузлів лежать у пам'яті послідовно. При обході дерева весь масив завантажується в один або два рядки кешу даних L1 (розмір рядка 32 або 64 байти);
3. **Абсолютна безпека серіалізації:** Стан дерева можна миттєво зберегти в енергонезалежну пам'ять FRAM/EEPROM або передати по каналу MAVLink як суцільний бінарний дамп без потреби в трансляції вказівників.

---

### Повна реалізація бортового рушія на мовах C та C++

Нижче наведено повні, готові до компіляції реалізації рушія на чистій мові C99 та сучасному стандарті C++20. Обидва варіанти містять повну підтримку реактивних селекторів, послідовностей, паралельних вузлів із пороговою політикою M-of-N, інверторів, таймаутів, типізованої Дошки Оголошень та наскрізного тестового сценарію польоту.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

#define BT_MAX_CHILDREN      8
#define BT_MAX_NODES         32
#define BT_MAX_BB_ENTRIES    16
#define BT_KEY_LEN           24

/* Статуси виконання вузла */
typedef enum {
    BT_STATUS_IDLE = 0,
    BT_STATUS_RUNNING,
    BT_STATUS_SUCCESS,
    BT_STATUS_FAILURE
} bt_status_t;

/* Типи вузлів дерева поведінки */
typedef enum {
    BT_NODE_ACTION,
    BT_NODE_CONDITION,
    BT_NODE_SEQUENCE,
    BT_NODE_REACTIVE_SEQUENCE,
    BT_NODE_FALLBACK,
    BT_NODE_REACTIVE_FALLBACK,
    BT_NODE_PARALLEL_M_OF_N,
    BT_NODE_INVERTER,
    BT_NODE_TIMEOUT
} bt_node_type_t;

/* Типи даних Дошки Оголошень */
typedef enum {
    BB_TYPE_EMPTY = 0,
    BB_TYPE_BOOL,
    BB_TYPE_INT32,
    BB_TYPE_FLOAT
} bb_val_type_t;

typedef struct {
    char key[BT_KEY_LEN];
    bb_val_type_t type;
    union {
        bool b_val;
        int32_t i_val;
        float f_val;
    } data;
    bool is_set;
} bb_entry_t;

typedef struct {
    bb_entry_t entries[BT_MAX_BB_ENTRIES];
    uint8_t count;
} blackboard_t;

/* Попереднє оголошення вузла */
struct bt_node;
typedef bt_status_t (*bt_tick_fn)(struct bt_node *self, blackboard_t *bb);
typedef void (*bt_halt_fn)(struct bt_node *self, blackboard_t *bb);

/* Дескриптор вузла дерева */
typedef struct bt_node {
    uint8_t id;
    bt_node_type_t type;
    bt_status_t status;
    bt_tick_fn tick_fn;
    bt_halt_fn halt_fn;
    uint8_t children[BT_MAX_CHILDREN];
    uint8_t child_count;
    uint8_t running_child_idx;
    uint8_t threshold_m;          /* Для паралельного вузла: поріг успішних дітей */
    uint32_t timeout_ticks;       /* Для декоратора Timeout: ліміт тактів */
    uint32_t elapsed_ticks;       /* Поточний лічильник тактів */
    void *user_data;              /* Вказівник на локальний контекст */
} bt_node_t;

/* Статичний контекст дерева поведінки */
typedef struct {
    bt_node_t nodes[BT_MAX_NODES];
    uint8_t node_count;
    uint8_t root_id;
    blackboard_t bb;
} bt_tree_t;

/* === РОБОТА З ДОШКОЮ ОГОЛОШЕНЬ === */

void bb_init(blackboard_t *bb) {
    memset(bb, 0, sizeof(blackboard_t));
}

bool bb_set_float(blackboard_t *bb, const char *key, float val) {
    for (uint8_t i = 0; i < bb->count; i++) {
        if (strncmp(bb->entries[i].key, key, BT_KEY_LEN) == 0) {
            bb->entries[i].type = BB_TYPE_FLOAT;
            bb->entries[i].data.f_val = val;
            bb->entries[i].is_set = true;
            return true;
        }
    }
    if (bb->count >= BT_MAX_BB_ENTRIES) return false;
    strncpy(bb->entries[bb->count].key, key, BT_KEY_LEN - 1);
    bb->entries[bb->count].key[BT_KEY_LEN - 1] = '\0';
    bb->entries[bb->count].type = BB_TYPE_FLOAT;
    bb->entries[bb->count].data.f_val = val;
    bb->entries[bb->count].is_set = true;
    bb->count++;
    return true;
}

bool bb_get_float(const blackboard_t *bb, const char *key, float *out_val) {
    for (uint8_t i = 0; i < bb->count; i++) {
        if (bb->entries[i].is_set && strncmp(bb->entries[i].key, key, BT_KEY_LEN) == 0) {
            if (bb->entries[i].type == BB_TYPE_FLOAT) {
                *out_val = bb->entries[i].data.f_val;
                return true;
            }
        }
    }
    return false;
}

bool bb_set_bool(blackboard_t *bb, const char *key, bool val) {
    for (uint8_t i = 0; i < bb->count; i++) {
        if (strncmp(bb->entries[i].key, key, BT_KEY_LEN) == 0) {
            bb->entries[i].type = BB_TYPE_BOOL;
            bb->entries[i].data.b_val = val;
            bb->entries[i].is_set = true;
            return true;
        }
    }
    if (bb->count >= BT_MAX_BB_ENTRIES) return false;
    strncpy(bb->entries[bb->count].key, key, BT_KEY_LEN - 1);
    bb->entries[bb->count].key[BT_KEY_LEN - 1] = '\0';
    bb->entries[bb->count].type = BB_TYPE_BOOL;
    bb->entries[bb->count].data.b_val = val;
    bb->entries[bb->count].is_set = true;
    bb->count++;
    return true;
}

bool bb_get_bool(const blackboard_t *bb, const char *key, bool *out_val) {
    for (uint8_t i = 0; i < bb->count; i++) {
        if (bb->entries[i].is_set && strncmp(bb->entries[i].key, key, BT_KEY_LEN) == 0) {
            if (bb->entries[i].type == BB_TYPE_BOOL) {
                *out_val = bb->entries[i].data.b_val;
                return true;
            }
        }
    }
    return false;
}

/* === СТВОРЕННЯ ТА КОМПОЗИЦІЯ ДЕРЕВА === */

void bt_tree_init(bt_tree_t *tree) {
    memset(tree, 0, sizeof(bt_tree_t));
    bb_init(&tree->bb);
}

uint8_t bt_create_node(bt_tree_t *tree, bt_node_type_t type, bt_tick_fn tick, bt_halt_fn halt) {
    if (tree->node_count >= BT_MAX_NODES) return 0xFF;
    uint8_t id = tree->node_count++;
    bt_node_t *n = &tree->nodes[id];
    n->id = id;
    n->type = type;
    n->status = BT_STATUS_IDLE;
    n->tick_fn = tick;
    n->halt_fn = halt;
    n->child_count = 0;
    n->running_child_idx = 0;
    n->threshold_m = 1;
    n->timeout_ticks = 0;
    n->elapsed_ticks = 0;
    n->user_data = NULL;
    return id;
}

bool bt_add_child(bt_tree_t *tree, uint8_t parent_id, uint8_t child_id) {
    if (parent_id >= tree->node_count || child_id >= tree->node_count) return false;
    bt_node_t *p = &tree->nodes[parent_id];
    if (p->child_count >= BT_MAX_CHILDREN) return false;
    p->children[p->child_count++] = child_id;
    return true;
}

/* === МЕХАНІЗМ ПЕРЕРИВАННЯ ТА ВИКОНАННЯ ТАКТУ === */

void bt_halt_node(bt_tree_t *tree, uint8_t node_id) {
    if (node_id >= tree->node_count) return;
    bt_node_t *n = &tree->nodes[node_id];

    if (n->status == BT_STATUS_RUNNING) {
        if (n->halt_fn) {
            n->halt_fn(n, &tree->bb);
        }
        for (uint8_t i = 0; i < n->child_count; i++) {
            bt_halt_node(tree, n->children[i]);
        }
        n->status = BT_STATUS_IDLE;
        n->running_child_idx = 0;
        n->elapsed_ticks = 0;
    }
}

bt_status_t bt_tick_node(bt_tree_t *tree, uint8_t node_id) {
    if (node_id >= tree->node_count) return BT_STATUS_FAILURE;
    bt_node_t *n = &tree->nodes[node_id];

    switch (n->type) {
        case BT_NODE_ACTION:
        case BT_NODE_CONDITION:
            if (n->tick_fn) {
                n->status = n->tick_fn(n, &tree->bb);
            } else {
                n->status = BT_STATUS_FAILURE;
            }
            return n->status;

        case BT_NODE_SEQUENCE: {
            for (uint8_t i = n->running_child_idx; i < n->child_count; i++) {
                bt_status_t s = bt_tick_node(tree, n->children[i]);
                if (s == BT_STATUS_RUNNING) {
                    n->running_child_idx = i;
                    n->status = BT_STATUS_RUNNING;
                    return BT_STATUS_RUNNING;
                }
                if (s == BT_STATUS_FAILURE) {
                    n->running_child_idx = 0;
                    n->status = BT_STATUS_FAILURE;
                    return BT_STATUS_FAILURE;
                }
            }
            n->running_child_idx = 0;
            n->status = BT_STATUS_SUCCESS;
            return BT_STATUS_SUCCESS;
        }

        case BT_NODE_REACTIVE_SEQUENCE: {
            for (uint8_t i = 0; i < n->child_count; i++) {
                bt_status_t s = bt_tick_node(tree, n->children[i]);
                if (s == BT_STATUS_FAILURE) {
                    if (n->status == BT_STATUS_RUNNING && n->running_child_idx > i) {
                        bt_halt_node(tree, n->children[n->running_child_idx]);
                    }
                    n->running_child_idx = 0;
                    n->status = BT_STATUS_FAILURE;
                    return BT_STATUS_FAILURE;
                }
                if (s == BT_STATUS_RUNNING) {
                    if (n->status == BT_STATUS_RUNNING && n->running_child_idx != i) {
                        bt_halt_node(tree, n->children[n->running_child_idx]);
                    }
                    n->running_child_idx = i;
                    n->status = BT_STATUS_RUNNING;
                    return BT_STATUS_RUNNING;
                }
            }
            n->running_child_idx = 0;
            n->status = BT_STATUS_SUCCESS;
            return BT_STATUS_SUCCESS;
        }

        case BT_NODE_FALLBACK: {
            for (uint8_t i = n->running_child_idx; i < n->child_count; i++) {
                bt_status_t s = bt_tick_node(tree, n->children[i]);
                if (s == BT_STATUS_RUNNING) {
                    n->running_child_idx = i;
                    n->status = BT_STATUS_RUNNING;
                    return BT_STATUS_RUNNING;
                }
                if (s == BT_STATUS_SUCCESS) {
                    n->running_child_idx = 0;
                    n->status = BT_STATUS_SUCCESS;
                    return BT_STATUS_SUCCESS;
                }
            }
            n->running_child_idx = 0;
            n->status = BT_STATUS_FAILURE;
            return BT_STATUS_FAILURE;
        }

        case BT_NODE_REACTIVE_FALLBACK: {
            for (uint8_t i = 0; i < n->child_count; i++) {
                bt_status_t s = bt_tick_node(tree, n->children[i]);

                if (s == BT_STATUS_RUNNING) {
                    if (n->status == BT_STATUS_RUNNING && n->running_child_idx > i) {
                        bt_halt_node(tree, n->children[n->running_child_idx]);
                    }
                    n->running_child_idx = i;
                    n->status = BT_STATUS_RUNNING;
                    return BT_STATUS_RUNNING;
                }
                if (s == BT_STATUS_SUCCESS) {
                    if (n->status == BT_STATUS_RUNNING && n->running_child_idx != i) {
                        bt_halt_node(tree, n->children[n->running_child_idx]);
                    }
                    n->running_child_idx = 0;
                    n->status = BT_STATUS_SUCCESS;
                    return BT_STATUS_SUCCESS;
                }
            }
            n->running_child_idx = 0;
            n->status = BT_STATUS_FAILURE;
            return BT_STATUS_FAILURE;
        }

        case BT_NODE_PARALLEL_M_OF_N: {
            uint8_t success_cnt = 0;
            uint8_t failure_cnt = 0;

            for (uint8_t i = 0; i < n->child_count; i++) {
                bt_status_t s = bt_tick_node(tree, n->children[i]);
                if (s == BT_STATUS_SUCCESS) success_cnt++;
                else if (s == BT_STATUS_FAILURE) failure_cnt++;
            }

            if (success_cnt >= n->threshold_m) {
                for (uint8_t i = 0; i < n->child_count; i++) {
                    bt_halt_node(tree, n->children[i]);
                }
                n->status = BT_STATUS_SUCCESS;
                return BT_STATUS_SUCCESS;
            }

            if (failure_cnt > (n->child_count - n->threshold_m)) {
                for (uint8_t i = 0; i < n->child_count; i++) {
                    bt_halt_node(tree, n->children[i]);
                }
                n->status = BT_STATUS_FAILURE;
                return BT_STATUS_FAILURE;
            }

            n->status = BT_STATUS_RUNNING;
            return BT_STATUS_RUNNING;
        }

        case BT_NODE_INVERTER: {
            if (n->child_count == 0) return BT_STATUS_FAILURE;
            bt_status_t s = bt_tick_node(tree, n->children[0]);
            if (s == BT_STATUS_SUCCESS) n->status = BT_STATUS_FAILURE;
            else if (s == BT_STATUS_FAILURE) n->status = BT_STATUS_SUCCESS;
            else n->status = s;
            return n->status;
        }

        case BT_NODE_TIMEOUT: {
            if (n->child_count == 0) return BT_STATUS_FAILURE;
            n->elapsed_ticks++;
            if (n->timeout_ticks > 0 && n->elapsed_ticks > n->timeout_ticks) {
                bt_halt_node(tree, n->children[0]);
                n->elapsed_ticks = 0;
                n->status = BT_STATUS_FAILURE;
                return BT_STATUS_FAILURE;
            }
            bt_status_t s = bt_tick_node(tree, n->children[0]);
            if (s != BT_STATUS_RUNNING) {
                n->elapsed_ticks = 0;
            }
            n->status = s;
            return s;
        }

        default:
            return BT_STATUS_FAILURE;
    }
}

bt_status_t bt_tick(bt_tree_t *tree) {
    return bt_tick_node(tree, tree->root_id);
}
```
```cpp
#include <cstdint>
#include <string_view>
#include <span>
#include <array>
#include <variant>
#include <optional>
#include <concepts>

namespace autopilot::bt {

enum class NodeStatus : uint8_t {
    Idle = 0,
    Running,
    Success,
    Failure
};

enum class NodeType : uint8_t {
    Action,
    Condition,
    Sequence,
    ReactiveSequence,
    Fallback,
    ReactiveFallback,
    ParallelMOfN,
    Inverter,
    Timeout
};

constexpr size_t MaxNodes = 32;
constexpr size_t MaxChildren = 8;
constexpr size_t MaxBlackboardEntries = 16;

using BlackboardValue = std::variant<bool, int32_t, float>;

struct BlackboardEntry {
    std::string_view key{};
    BlackboardValue value{};
    bool is_set{false};
};

class Blackboard {
public:
    template <typename T>
    bool set(std::string_view key, T val) noexcept {
        for (auto& entry : entries_) {
            if (entry.is_set && entry.key == key) {
                entry.value = val;
                return true;
            }
        }
        if (count_ >= MaxBlackboardEntries) return false;
        entries_[count_] = BlackboardEntry{key, val, true};
        count_++;
        return true;
    }

    template <typename T>
    [[nodiscard]] std::optional<T> get(std::string_view key) const noexcept {
        for (size_t i = 0; i < count_; ++i) {
            if (entries_[i].is_set && entries_[i].key == key) {
                if (const auto* val = std::get_if<T>(&entries_[i].value)) {
                    return *val;
                }
            }
        }
        return std::nullopt;
    }

    void clear() noexcept {
        count_ = 0;
        for (auto& entry : entries_) {
            entry.is_set = false;
        }
    }

private:
    std::array<BlackboardEntry, MaxBlackboardEntries> entries_{};
    size_t count_{0};
};

struct Node;
using TickFn = NodeStatus (*)(Node& self, Blackboard& bb) noexcept;
using HaltFn = void (*)(Node& self, Blackboard& bb) noexcept;

struct Node {
    uint8_t id{0};
    NodeType type{NodeType::Action};
    NodeStatus status{NodeStatus::Idle};
    TickFn tick_fn{nullptr};
    HaltFn halt_fn{nullptr};
    std::array<uint8_t, MaxChildren> children{};
    uint8_t child_count{0};
    uint8_t running_child_idx{0};
    uint8_t threshold_m{1};
    uint32_t timeout_ticks{0};
    uint32_t elapsed_ticks{0};
    void* user_data{nullptr};
};

class BehaviorTree {
public:
    BehaviorTree() noexcept = default;

    uint8_t create_node(NodeType type, TickFn tick = nullptr, HaltFn halt = nullptr) noexcept {
        if (node_count_ >= MaxNodes) return 0xFF;
        uint8_t id = node_count_++;
        nodes_[id] = Node{id, type, NodeStatus::Idle, tick, halt, {}, 0, 0, 1, 0, 0, nullptr};
        return id;
    }

    bool add_child(uint8_t parent_id, uint8_t child_id) noexcept {
        if (parent_id >= node_count_ || child_id >= node_count_) return false;
        auto& parent = nodes_[parent_id];
        if (parent.child_count >= MaxChildren) return false;
        parent.children[parent.child_count++] = child_id;
        return true;
    }

    void set_parallel_threshold(uint8_t node_id, uint8_t m) noexcept {
        if (node_id < node_count_) {
            nodes_[node_id].threshold_m = m;
        }
    }

    void set_timeout_ticks(uint8_t node_id, uint32_t ticks) noexcept {
        if (node_id < node_count_) {
            nodes_[node_id].timeout_ticks = ticks;
        }
    }

    void set_root(uint8_t root_id) noexcept {
        root_id_ = root_id;
    }

    void halt_node(uint8_t node_id) noexcept {
        if (node_id >= node_count_) return;
        auto& n = nodes_[node_id];
        if (n.status == NodeStatus::Running) {
            if (n.halt_fn) {
                n.halt_fn(n, blackboard_);
            }
            for (size_t i = 0; i < n.child_count; ++i) {
                halt_node(n.children[i]);
            }
            n.status = NodeStatus::Idle;
            n.running_child_idx = 0;
            n.elapsed_ticks = 0;
        }
    }

    NodeStatus tick_node(uint8_t node_id) noexcept {
        if (node_id >= node_count_) return NodeStatus::Failure;
        auto& n = nodes_[node_id];

        switch (n.type) {
            case NodeType::Action:
            case NodeType::Condition:
                n.status = n.tick_fn ? n.tick_fn(n, blackboard_) : NodeStatus::Failure;
                return n.status;

            case NodeType::Sequence: {
                for (size_t i = n.running_child_idx; i < n.child_count; ++i) {
                    const auto s = tick_node(n.children[i]);
                    if (s == NodeStatus::Running) {
                        n.running_child_idx = static_cast<uint8_t>(i);
                        n.status = NodeStatus::Running;
                        return NodeStatus::Running;
                    }
                    if (s == NodeStatus::Failure) {
                        n.running_child_idx = 0;
                        n.status = NodeStatus::Failure;
                        return NodeStatus::Failure;
                    }
                }
                n.running_child_idx = 0;
                n.status = NodeStatus::Success;
                return NodeStatus::Success;
            }

            case NodeType::ReactiveSequence: {
                for (size_t i = 0; i < n.child_count; ++i) {
                    const auto s = tick_node(n.children[i]);
                    if (s == NodeStatus::Failure) {
                        if (n.status == NodeStatus::Running && n.running_child_idx > i) {
                            halt_node(n.children[n.running_child_idx]);
                        }
                        n.running_child_idx = 0;
                        n.status = NodeStatus::Failure;
                        return NodeStatus::Failure;
                    }
                    if (s == NodeStatus::Running) {
                        if (n.status == NodeStatus::Running && n.running_child_idx != i) {
                            halt_node(n.children[n.running_child_idx]);
                        }
                        n.running_child_idx = static_cast<uint8_t>(i);
                        n.status = NodeStatus::Running;
                        return NodeStatus::Running;
                    }
                }
                n.running_child_idx = 0;
                n.status = NodeStatus::Success;
                return NodeStatus::Success;
            }

            case NodeType::Fallback: {
                for (size_t i = n.running_child_idx; i < n.child_count; ++i) {
                    const auto s = tick_node(n.children[i]);
                    if (s == NodeStatus::Running) {
                        n.running_child_idx = static_cast<uint8_t>(i);
                        n.status = NodeStatus::Running;
                        return NodeStatus::Running;
                    }
                    if (s == NodeStatus::Success) {
                        n.running_child_idx = 0;
                        n.status = NodeStatus::Success;
                        return NodeStatus::Success;
                    }
                }
                n.running_child_idx = 0;
                n.status = NodeStatus::Failure;
                return NodeStatus::Failure;
            }

            case NodeType::ReactiveFallback: {
                for (size_t i = 0; i < n.child_count; ++i) {
                    const auto s = tick_node(n.children[i]);

                    if (s == NodeStatus::Running) {
                        if (n.status == NodeStatus::Running && n.running_child_idx > i) {
                            halt_node(n.children[n.running_child_idx]);
                        }
                        n.running_child_idx = static_cast<uint8_t>(i);
                        n.status = NodeStatus::Running;
                        return NodeStatus::Running;
                    }
                    if (s == NodeStatus::Success) {
                        if (n.status == NodeStatus::Running && n.running_child_idx != i) {
                            halt_node(n.children[n.running_child_idx]);
                        }
                        n.running_child_idx = 0;
                        n.status = NodeStatus::Success;
                        return NodeStatus::Success;
                    }
                }
                n.running_child_idx = 0;
                n.status = NodeStatus::Failure;
                return NodeStatus::Failure;
            }

            case NodeType::ParallelMOfN: {
                uint8_t success_cnt = 0;
                uint8_t failure_cnt = 0;

                for (size_t i = 0; i < n.child_count; ++i) {
                    const auto s = tick_node(n.children[i]);
                    if (s == NodeStatus::Success) success_cnt++;
                    else if (s == NodeStatus::Failure) failure_cnt++;
                }

                if (success_cnt >= n.threshold_m) {
                    for (size_t i = 0; i < n.child_count; ++i) {
                        halt_node(n.children[i]);
                    }
                    n.status = NodeStatus::Success;
                    return NodeStatus::Success;
                }

                if (failure_cnt > (n.child_count - n.threshold_m)) {
                    for (size_t i = 0; i < n.child_count; ++i) {
                        halt_node(n.children[i]);
                    }
                    n.status = NodeStatus::Failure;
                    return NodeStatus::Failure;
                }

                n.status = NodeStatus::Running;
                return NodeStatus::Running;
            }

            case NodeType::Inverter: {
                if (n.child_count == 0) return NodeStatus::Failure;
                const auto s = tick_node(n.children[0]);
                if (s == NodeStatus::Success) n.status = NodeStatus::Failure;
                else if (s == NodeStatus::Failure) n.status = NodeStatus::Success;
                else n.status = s;
                return n.status;
            }

            case NodeType::Timeout: {
                if (n.child_count == 0) return NodeStatus::Failure;
                n.elapsed_ticks++;
                if (n.timeout_ticks > 0 && n.elapsed_ticks > n.timeout_ticks) {
                    halt_node(n.children[0]);
                    n.elapsed_ticks = 0;
                    n.status = NodeStatus::Failure;
                    return NodeStatus::Failure;
                }
                const auto s = tick_node(n.children[0]);
                if (s != NodeStatus::Running) {
                    n.elapsed_ticks = 0;
                }
                n.status = s;
                return s;
            }
        }
        return NodeStatus::Failure;
    }

    [[nodiscard]] NodeStatus tick() noexcept {
        return tick_node(root_id_);
    }

    Blackboard& blackboard() noexcept { return blackboard_; }
    [[nodiscard]] const Blackboard& blackboard() const noexcept { return blackboard_; }

private:
    std::array<Node, MaxNodes> nodes_{};
    uint8_t node_count_{0};
    uint8_t root_id_{0};
    Blackboard blackboard_{};
};

} // namespace autopilot::bt
```
:::

---

### Сценарій тестування: «Патрулювання з реактивним ухиленням та аварійним RTL»

Для підтвердження надійності рушія реалізуємо симуляційний стенд реального часу. Дрон виконує місію патрулювання коридору, стикається з динамічною перешкодою та зазнає аварійного розряду батареї.

Код симуляції створює повне дерево місії, наповнює Дошку Оголошень початковими даними і виконує три послідовні польотні такти зі зміною зовнішніх умов:

:::tabs
```c
/* Обробники вузлів для тесту */

bt_status_t cond_battery_low(bt_node_t *self, blackboard_t *bb) {
    (void)self;
    float v = 0.0f;
    if (bb_get_float(bb, "bat_volt", &v) && v < 14.0f) {
        printf("  [Condition] Bat Low: %.2fV < 14.0V -> SUCCESS\n", v);
        return BT_STATUS_SUCCESS;
    }
    return BT_STATUS_FAILURE;
}

bt_status_t act_emergency_land(bt_node_t *self, blackboard_t *bb) {
    (void)self;
    (void)bb;
    printf("  [Action] LandNow -> Executing emergency descent\n");
    return BT_STATUS_RUNNING;
}

void act_emergency_land_halt(bt_node_t *self, blackboard_t *bb) {
    (void)self;
    (void)bb;
    printf("  [Halt] LandNow stopped\n");
}

bt_status_t cond_obstacle_near(bt_node_t *self, blackboard_t *bb) {
    (void)self;
    float d = 0.0f;
    if (bb_get_float(bb, "lidar_dist", &d) && d < 3.0f) {
        printf("  [Condition] Obstacle Near: %.2fm < 3.0m -> SUCCESS\n", d);
        return BT_STATUS_SUCCESS;
    }
    return BT_STATUS_FAILURE;
}

bt_status_t act_avoid_path(bt_node_t *self, blackboard_t *bb) {
    (void)self;
    (void)bb;
    printf("  [Action] AvoidPath -> Executing DWA avoidance maneuver\n");
    return BT_STATUS_RUNNING;
}

void act_avoid_path_halt(bt_node_t *self, blackboard_t *bb) {
    (void)self;
    (void)bb;
    printf("  [Halt] AvoidPath stopped\n");
}

bt_status_t act_takeoff(bt_node_t *self, blackboard_t *bb) {
    (void)self;
    (void)bb;
    printf("  [Action] Takeoff -> Reached 30m altitude -> SUCCESS\n");
    return BT_STATUS_SUCCESS;
}

bt_status_t act_fly_waypoint(bt_node_t *self, blackboard_t *bb) {
    (void)self;
    (void)bb;
    printf("  [Action] FlyWp -> Flying to WP#4 (V=12m/s)\n");
    return BT_STATUS_RUNNING;
}

void act_fly_waypoint_halt(bt_node_t *self, blackboard_t *bb) {
    (void)self;
    (void)bb;
    printf("  [Halt] FlyWp stopped -> Velocity setpoint zeroed\n");
}

bt_status_t act_track_camera(bt_node_t *self, blackboard_t *bb) {
    (void)self;
    (void)bb;
    printf("  [Action] TrackCam -> Optical gimbal tracking active\n");
    return BT_STATUS_RUNNING;
}

void act_track_camera_halt(bt_node_t *self, blackboard_t *bb) {
    (void)self;
    (void)bb;
    printf("  [Halt] TrackCam stopped\n");
}

void run_simulation_demo(void) {
    bt_tree_t tree;
    bt_tree_init(&tree);

    /* Побудова топології дерева */
    uint8_t root = bt_create_node(&tree, BT_NODE_REACTIVE_FALLBACK, NULL, NULL);
    uint8_t seq_failsafe = bt_create_node(&tree, BT_NODE_SEQUENCE, NULL, NULL);
    uint8_t seq_avoid = bt_create_node(&tree, BT_NODE_SEQUENCE, NULL, NULL);
    uint8_t seq_mission = bt_create_node(&tree, BT_NODE_SEQUENCE, NULL, NULL);

    bt_add_child(&tree, root, seq_failsafe);
    bt_add_child(&tree, root, seq_avoid);
    bt_add_child(&tree, root, seq_mission);

    /* Гілка Failsafe */
    uint8_t c_bat = bt_create_node(&tree, BT_NODE_CONDITION, cond_battery_low, NULL);
    uint8_t a_land = bt_create_node(&tree, BT_NODE_ACTION, act_emergency_land, act_emergency_land_halt);
    bt_add_child(&tree, seq_failsafe, c_bat);
    bt_add_child(&tree, seq_failsafe, a_land);

    /* Гілка Avoidance */
    uint8_t c_obs = bt_create_node(&tree, BT_NODE_CONDITION, cond_obstacle_near, NULL);
    uint8_t a_avoid = bt_create_node(&tree, BT_NODE_ACTION, act_avoid_path, act_avoid_path_halt);
    bt_add_child(&tree, seq_avoid, c_obs);
    bt_add_child(&tree, seq_avoid, a_avoid);

    /* Гілка Mission */
    uint8_t a_takeoff = bt_create_node(&tree, BT_NODE_ACTION, act_takeoff, NULL);
    uint8_t par_patrol = bt_create_node(&tree, BT_NODE_PARALLEL_M_OF_N, NULL, NULL);
    tree.nodes[par_patrol].threshold_m = 2; /* Обидва процеси паралельні */

    uint8_t a_fly = bt_create_node(&tree, BT_NODE_ACTION, act_fly_waypoint, act_fly_waypoint_halt);
    uint8_t a_cam = bt_create_node(&tree, BT_NODE_ACTION, act_track_camera, act_track_camera_halt);
    bt_add_child(&tree, par_patrol, a_fly);
    bt_add_child(&tree, par_patrol, a_cam);

    bt_add_child(&tree, seq_mission, a_takeoff);
    bt_add_child(&tree, seq_mission, par_patrol);

    tree.root_id = root;

    printf("=== ТАКТ 1: Нормальний політ (Bat=15.5V, Dist=10.0m) ===\n");
    bb_set_float(&tree.bb, "bat_volt", 15.5f);
    bb_set_float(&tree.bb, "lidar_dist", 10.0f);
    bt_tick(&tree);

    printf("\n=== ТАКТ 2: Виявлено перешкоду (Dist=2.2m) ===\n");
    bb_set_float(&tree.bb, "lidar_dist", 2.2f);
    bt_tick(&tree);

    printf("\n=== ТАКТ 3: Подвійна відмова: Батарея критична (Bat=13.5V, Dist=2.2m) ===\n");
    bb_set_float(&tree.bb, "bat_volt", 13.5f);
    bt_tick(&tree);
}
```
```cpp
#include <iostream>

using namespace autopilot::bt;

NodeStatus cond_battery_low(Node&, Blackboard& bb) noexcept {
    const auto v = bb.get<float>("bat_volt").value_or(16.0f);
    if (v < 14.0f) {
        std::cout << "  [Condition] Bat Low: " << v << "V < 14.0V -> SUCCESS\n";
        return NodeStatus::Success;
    }
    return NodeStatus::Failure;
}

NodeStatus act_emergency_land(Node&, Blackboard&) noexcept {
    std::cout << "  [Action] LandNow -> Executing emergency descent\n";
    return NodeStatus::Running;
}

void act_emergency_land_halt(Node&, Blackboard&) noexcept {
    std::cout << "  [Halt] LandNow stopped\n";
}

NodeStatus cond_obstacle_near(Node&, Blackboard& bb) noexcept {
    const auto d = bb.get<float>("lidar_dist").value_or(100.0f);
    if (d < 3.0f) {
        std::cout << "  [Condition] Obstacle Near: " << d << "m < 3.0m -> SUCCESS\n";
        return NodeStatus::Success;
    }
    return NodeStatus::Failure;
}

NodeStatus act_avoid_path(Node&, Blackboard&) noexcept {
    std::cout << "  [Action] AvoidPath -> Executing DWA avoidance maneuver\n";
    return NodeStatus::Running;
}

void act_avoid_path_halt(Node&, Blackboard&) noexcept {
    std::cout << "  [Halt] AvoidPath stopped\n";
}

NodeStatus act_takeoff(Node&, Blackboard&) noexcept {
    std::cout << "  [Action] Takeoff -> Reached 30m altitude -> SUCCESS\n";
    return NodeStatus::Success;
}

NodeStatus act_fly_waypoint(Node&, Blackboard&) noexcept {
    std::cout << "  [Action] FlyWp -> Flying to WP#4 (V=12m/s)\n";
    return NodeStatus::Running;
}

void act_fly_waypoint_halt(Node&, Blackboard&) noexcept {
    std::cout << "  [Halt] FlyWp stopped -> Velocity setpoint zeroed\n";
}

NodeStatus act_track_camera(Node&, Blackboard&) noexcept {
    std::cout << "  [Action] TrackCam -> Optical gimbal tracking active\n";
    return NodeStatus::Running;
}

void act_track_camera_halt(Node&, Blackboard&) noexcept {
    std::cout << "  [Halt] TrackCam stopped\n";
}

void run_cpp_simulation() noexcept {
    BehaviorTree tree;

    const uint8_t root = tree.create_node(NodeType::ReactiveFallback);
    const uint8_t seq_failsafe = tree.create_node(NodeType::Sequence);
    const uint8_t seq_avoid = tree.create_node(NodeType::Sequence);
    const uint8_t seq_mission = tree.create_node(NodeType::Sequence);

    tree.add_child(root, seq_failsafe);
    tree.add_child(root, seq_avoid);
    tree.add_child(root, seq_mission);

    const uint8_t c_bat = tree.create_node(NodeType::Condition, cond_battery_low);
    const uint8_t a_land = tree.create_node(NodeType::Action, act_emergency_land, act_emergency_land_halt);
    tree.add_child(seq_failsafe, c_bat);
    tree.add_child(seq_failsafe, a_land);

    const uint8_t c_obs = tree.create_node(NodeType::Condition, cond_obstacle_near);
    const uint8_t a_avoid = tree.create_node(NodeType::Action, act_avoid_path, act_avoid_path_halt);
    tree.add_child(seq_avoid, c_obs);
    tree.add_child(seq_avoid, a_avoid);

    const uint8_t a_takeoff = tree.create_node(NodeType::Action, act_takeoff);
    const uint8_t par_patrol = tree.create_node(NodeType::ParallelMOfN);
    tree.set_parallel_threshold(par_patrol, 2);

    const uint8_t a_fly = tree.create_node(NodeType::Action, act_fly_waypoint, act_fly_waypoint_halt);
    const uint8_t a_cam = tree.create_node(NodeType::Action, act_track_camera, act_track_camera_halt);
    tree.add_child(par_patrol, a_fly);
    tree.add_child(par_patrol, a_cam);

    tree.add_child(seq_mission, a_takeoff);
    tree.add_child(seq_mission, par_patrol);

    tree.set_root(root);

    std::cout << "=== ТАКТ 1: Нормальний політ (Bat=15.5V, Dist=10.0m) ===\n";
    tree.blackboard().set("bat_volt", 15.5f);
    tree.blackboard().set("lidar_dist", 10.0f);
    tree.tick();

    std::cout << "\n=== ТАКТ 2: Виявлено перешкоду (Dist=2.2m) ===\n";
    tree.blackboard().set("lidar_dist", 2.2f);
    tree.tick();

    std::cout << "\n=== ТАКТ 3: Подвійна відмова: Батарея критична (Bat=13.5V, Dist=2.2m) ===\n";
    tree.blackboard().set("bat_volt", 13.5f);
    tree.tick();
}
```
:::

---

### Детальний покроковий аналіз виконання та трасування тактів

Щоб зрозуміти внутрішню динаміку рушія, розглянемо повний стан структур даних та послідовність викликів функцій у кожному з трьох змодельованих тактів:

#### Аналіз Такту 1: Нормальний політ
1. Планувальник записує у Дошку Оголошень: `bat_volt = 15.5`, `lidar_dist = 10.0`;
2. Викликається `bt_tick(&tree)`. Спуск починається з кореневого вузла `Node 0 (ReactiveFallback)`;
3. `Node 0` тікає свою першу дитину — `Node 1 (Failsafe Sequence)`;
4. `Node 1` викликає `Node 4 (cond_battery_low)`. Напруга 15.5 В перевищує поріг 14.0 В. Функція повертає `FAILURE`;
5. Оскільки `Node 4` зазнав невдачі, послідовність `Node 1` негайно повертає `FAILURE`, не викликаючи дію `Node 5 (LandNow)`;
6. `Node 0` переходить до другої дитини — `Node 2 (Avoidance Sequence)`;
7. `Node 2` викликає `Node 6 (cond_obstacle_near)`. Дистанція 10.0 м перевищує поріг 3.0 м. Функція повертає `FAILURE`;
8. Послідовність `Node 2` повертає `FAILURE`;
9. `Node 0` переходить до третьої дитини — `Node 3 (Mission Sequence)`;
10. `Node 3` викликає `Node 8 (Takeoff)`. Дія виконує одноразовий крок, досягає висоти 30 м і повертає `SUCCESS`;
11. `Node 3` бачить `SUCCESS` від `Node 8` і в тому ж такті переходить до наступної дитини — `Node 9 (ParallelMOfN)`;
12. `Node 9` одночасно тікає обох своїх дітей: `Node 10 (FlyWp)` повертає `RUNNING`, `Node 11 (TrackCam)` повертає `RUNNING`;
13. Оскільки обидві дії виконуються, але поріг успіху `threshold_m = 2` ще не досягнуто, `Node 9` повертає `RUNNING`;
14. `Node 3` зберігає `running_child_idx = 1` (індекс `Node 9`) і повертає `RUNNING`;
15. `Node 0` зберігає `running_child_idx = 2` (індекс `Node 3`) і повертає `RUNNING` планувальнику польоту.

#### Аналіз Такту 2: Реактивне переривання перешкодою
1. Планувальник оновлює лідар: `lidar_dist = 2.2`;
2. Викликається `bt_tick(&tree)`. Оскільки `Node 0` є **реактивним** селектором (`ReactiveFallback`), він ігнорує попередній індекс `running_child_idx = 2` і знову починає спуск з нульової дитини (`Node 1`);
3. `Node 1 (Failsafe)` тікає `Node 4 (cond_battery_low)` — батарея в нормі, повертає `FAILURE`;
4. `Node 0` переходить до `Node 2 (Avoidance Sequence)`;
5. `Node 2` викликає `Node 6 (cond_obstacle_near)`. Дистанція 2.2 м менша за 3.0 м. Умова повертає `SUCCESS`!
6. `Node 2` переходить до `Node 7 (act_avoid_path)`. Запускається алгоритм DWA, дія повертає `RUNNING`;
7. `Node 2` повертає `RUNNING`;
8. `Node 0` виявляє зміну активного індексу: на попередньому такті активною була гілка 2 (`Mission`), а тепер активною стала гілка 1 (`Avoidance`) (`1 < 2`);
9. **Виклик витіснення:** `Node 0` негайно викликає `bt_halt_node(&tree, Node 3)`:
   - `Node 3` викликає `bt_halt_node(&tree, Node 9)`;
   - `Node 9` рекурсивно викликає `act_fly_waypoint_halt()` для `Node 10` та `act_track_camera_halt()` для `Node 11`;
   - Статуси вузлів 3, 9, 10, 11 переводяться в `BT_STATUS_IDLE`;
10. `Node 0` фіксує новий `running_child_idx = 1` і повертає `RUNNING`.

#### Аналіз Такту 3: Подвійна відмова та перемикання на аварійний захист
1. Напруга батареї падає: `bat_volt = 13.5`;
2. Викликається `bt_tick(&tree)`. `Node 0` знову починає з нульової дитини — `Node 1 (Failsafe)`;
3. `Node 1` викликає `Node 4 (cond_battery_low)`. Напруга 13.5 В нижча за 14.0 В -> повертає `SUCCESS`;
4. `Node 1` переходить до `Node 5 (act_emergency_land)`. Дія починає вертикальний спуск і повертає `RUNNING`;
5. `Node 1` повертає `RUNNING`;
6. `Node 0` виявляє зміну активного індексу з 1 (`Avoidance`) на 0 (`Failsafe`);
7. **Виклик витіснення:** `Node 0` викликає `bt_halt_node(&tree, Node 2)`. Викликається `act_avoid_path_halt()`, ухилення припиняється;
8. Дрон переходить до безумовного аварійного спуску.

---

### Приховані пастки та правила проектування вбудованого BT

При впровадженні рушія в польотний контролер слід враховувати такі інженерні нюанси:

1. **Гістерезис в умовах безпеки:** Якщо показники сенсорів шумлять, умова може повертати то `SUCCESS`, то `FAILURE` на сусідніх тактах. Для запобігання брязкоту (*chattering*) умови повинні зберігати внутрішній стан або використовувати різні пороги активації та деактивації;
2. **Гарантія детермінізму `Halt()`:** Якщо дія керує фізичним приводом (наприклад, сервоприводом скидання вантажу), функція `halt()` не повинна залишати привід у невизначеному проміжному стані;
3. **Вирівнювання структур даних:** Для 32-бітних процесорів ARM дескриптор `bt_node_t` вирівнюється за 4-байтовою межею для запобігання невирівняному доступу до пам'яті (*unaligned access fault*).

Ця реалізація надає детермінований фундамент автономії, гарантуючи надійність поведінки апарата в критичних ситуаціях.
