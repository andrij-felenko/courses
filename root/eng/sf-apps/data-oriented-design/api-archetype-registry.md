# 📋 Інтерфейс та структура чанкового реєстру архетипів (Archetype Chunk Storage)

Чанковий реєстр архетипів (англ. *Archetype Chunk Storage*) є промисловим стандартом організації пам'яті в сучасних високонавантажених рушіях Data-Oriented Design (зокрема Unity DOTS, Unreal Engine Mass Entity, Flecs).

На відміну від підходу Sparse Set, де кожен тип компонента зберігається в окремому глобальному масиві, архітектура архетипів групує сутності з **ідентичним набором компонентів** у фіксовані монолітні блоки пам'яті — чанки (англ. *chunks* розміром 16 або 64 КБ). Усередині кожного чанка дані розкладаються за принципом Structure of Arrays (SoA).

Нижче наведено повну специфікацію внутрішньої розкладки пам'яті, дескрипторів типів, механіки розрахунку місткості, графа переходів та функціонального контракту інтерфейсу реєстру архетипів.

---

### Специфікація розкладки пам'яті чанка

Кожен чанк виділяється з пам'яті з обов'язковим апаратним вирівнюванням по межі 64 байтів (розмір лінії кешу L1). Розмір чанка `CHUNK_SIZE` обирається кратним розміру сторінки операційної системи (типово 16 384 байти або 65 536 байтів).

#### 1. Розрахунок місткості чанка (Chunk Capacity)
Оскільки кожен архетип містить унікальний набір компонентів із різними сумарними розмірами, місткість чанка `Capacity` обчислюється динамічно під час створення архетипу за формулою:

```
AvailableBytes = CHUNK_SIZE - sizeof(ChunkHeader)
RowSize        = sizeof(Entity) + ∑ sizeof(Component[i])
Capacity       = floor(AvailableBytes / RowSize)
```

Для запобігання перетину меж кеш-ліній адреса початку кожного стовпця даних усередині чанка вирівнюється за найбільшим вирівнюванням відповідного типу (типово 8, 16 або 32 байти для векторних інструкцій SIMD).

#### 2. Структурна таблиця розкладки пам'яті чанка

| Зсув (байти) | Поле | Тип | Призначення |
| :--- | :--- | :--- | :--- |
| `0x00 .. 0x07` | `archetype` | `Archetype*` | Покажчик на батьківський дескриптор архетипу |
| `0x08 .. 0x0B` | `count` | `uint32_t` | Поточна кількість активних сутностей у чанку |
| `0x0C .. 0x0F` | `capacity` | `uint32_t` | Гранична місткість сутностей для даної комбінації компонентів |
| `0x10 .. 0x17` | `next_chunk` | `Chunk*` | Покажчик на наступний чанк у двозв'язному списку архетипу |
| `0x18 .. 0x1F` | `prev_chunk` | `Chunk*` | Покажчик на попередній чанк у списку |
| `0x20 .. 0x3F` | `reserved` | `uint8_t[32]` | Вирівнювання заголовка до межі 64 байтів (`CACHE_LINE_SIZE`) |
| `0x40 .. Offset[0]` | `Entities` | `Entity[Capacity]` | Лінійний масив числових ідентифікаторів сутностей |
| `Offset[0] .. Offset[1]` | `Comp[0]` | `uint8_t[Size_0 · Capacity]` | Неперервний стовпчик першого типу компонента |
| `Offset[k] .. End` | `Comp[k]` | `uint8_t[Size_k · Capacity]` | Неперервний стовпчик `k`-го типу компонента |

---

### Типи даних та сигнатури інтерфейсу

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define CHUNK_SIZE 16384
#define MAX_COMPONENTS_PER_ARCHETYPE 32

typedef uint32_t EntityID;

/* Структура ідентифікатора сутності з поколінням для усунення проблеми ABA */
typedef struct {
    uint32_t id;
    uint32_t generation;
} Entity;

typedef uint32_t ComponentTypeID;

/* Опис метаданих типу компонента */
typedef struct {
    ComponentTypeID id;
    uint32_t        size;
    uint32_t        alignment;
} ComponentInfo;

/* Заголовок чанка */
typedef struct Chunk {
    struct Archetype* archetype;
    uint32_t          count;
    uint32_t          capacity;
    struct Chunk*     next;
    struct Chunk*     prev;
    uint8_t           padding[32];
} Chunk;

/* Дескриптор унікальної комбінації компонентів */
typedef struct Archetype {
    uint32_t      component_count;
    ComponentInfo components[MAX_COMPONENTS_PER_ARCHETYPE];
    uint32_t      component_offsets[MAX_COMPONENTS_PER_ARCHETYPE];
    uint32_t      chunk_capacity;
    
    Chunk*        first_chunk;
    Chunk*        last_chunk;
    uint32_t      total_entities;
} Archetype;

/* Реєстр сутностей та граф архетипів */
typedef struct ArchetypeRegistry ArchetypeRegistry;

/* Створення та знищення реєстру */
ArchetypeRegistry* arch_registry_create(void);
void               arch_registry_destroy(ArchetypeRegistry* reg);

/* Реєстрація компонентів */
ComponentTypeID    arch_register_component(ArchetypeRegistry* reg, uint32_t size, uint32_t align);

/* Створення та видалення сутності */
Entity             arch_entity_create(ArchetypeRegistry* reg, const ComponentTypeID* types, uint32_t type_count);
bool               arch_entity_destroy(ArchetypeRegistry* reg, Entity e);

/* Динамічна мутація складу компонентів (перехід між архетипами) */
bool               arch_entity_add_component(ArchetypeRegistry* reg, Entity e, ComponentTypeID comp_id, const void* initial_data);
bool               arch_entity_remove_component(ArchetypeRegistry* reg, Entity e, ComponentTypeID comp_id);

/* Отримання прямого доступу до стовпця даних усередині чанка */
void*              arch_chunk_get_column(Chunk* chunk, uint32_t component_index);
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <vector>
#include <memory>
#include <typeindex>

struct Entity {
    std::uint32_t id{0};
    std::uint32_t generation{0};

    [[nodiscard]] bool operator==(const Entity& other) const noexcept = default;
};

using ComponentTypeID = std::uint32_t;

inline constexpr std::size_t kChunkSize = 16384;
inline constexpr std::size_t kMaxComponentsPerArchetype = 32;

struct ComponentInfo {
    ComponentTypeID id{0};
    std::uint32_t   size{0};
    std::uint32_t   alignment{0};
};

struct alignas(64) ChunkHeader {
    struct Archetype* archetype{nullptr};
    std::uint32_t     count{0};
    std::uint32_t     capacity{0};
    ChunkHeader*      next{nullptr};
    ChunkHeader*      prev{nullptr};
    std::uint8_t      reserved[32]{};
};

class ArchetypeRegistry {
public:
    ArchetypeRegistry() = default;
    ~ArchetypeRegistry() = default;

    ArchetypeRegistry(const ArchetypeRegistry&) = delete;
    ArchetypeRegistry& operator=(const ArchetypeRegistry&) = delete;

    template <typename T>
    ComponentTypeID register_component() {
        return register_component_raw(sizeof(T), alignof(T));
    }

    Entity create_entity(std::span<const ComponentTypeID> types);
    bool   destroy_entity(Entity e);

    template <typename T>
    bool add_component(Entity e, const T& data) {
        return add_component_raw(e, get_type_id<T>(), &data);
    }

    template <typename T>
    bool remove_component(Entity e) {
        return remove_component_raw(e, get_type_id<T>());
    }

    // Отримання неперервного стовпця для пакетної векторизованої ітерації
    template <typename T>
    std::span<T> get_chunk_column(ChunkHeader* chunk, std::uint32_t component_idx) noexcept {
        auto* ptr = static_cast<std::uint8_t*>(static_cast<void*>(chunk));
        std::size_t offset = get_component_offset(chunk, component_idx);
        return { reinterpret_cast<T*>(ptr + offset), chunk->count };
    }

private:
    ComponentTypeID register_component_raw(std::uint32_t size, std::uint32_t align);
    bool add_component_raw(Entity e, ComponentTypeID id, const void* data);
    bool remove_component_raw(Entity e, ComponentTypeID id);
    std::size_t get_component_offset(ChunkHeader* chunk, std::uint32_t component_idx) const noexcept;
    
    template <typename T>
    static ComponentTypeID get_type_id() noexcept;
};
```
:::

---

### Граф переходів між архетипами (Archetype Graph Transitions)

Коли сутність динамічно додає або видаляє компонент під час гри або симуляції, вона не модифікує наявний чанк за місцем, оскільки це порушило б монолітну структуру SoA. Замість цього реєстр виконує перехід за графом архетипів:

```
[Archetype A: Position, Velocity]
          │
          │  + AddComponent(MeshRenderer)
          ▼
[Archetype B: Position, Velocity, MeshRenderer]
```

Послідовність виконання операції переходу:
1. **Пошук цільового архетипу в графі переходів:** Реєстр перевіряє наявність ребра `+MeshRenderer` у дескрипторі вихідного архетипу. Якщо архетип `B` ще не створено, реєстр генерує новий архетип, обчислює зміщення стовпців і додає ребро переходу в граф.
2. **Резервування місця в цільовому чанку:** Реєстр знаходить останній чанк архетипу `B` із вільним місцем (`count < capacity`) або виділяє новий чанк із вирівняного пулу пам'яті.
3. **Копіювання спільних компонентів:** Байти спільних компонентів (`Position`, `Velocity`) копіюються з вихідного чанка архетипу `A` у відповідні стовпчики чанка архетипу `B`.
4. **Ініціалізація нового компонента:** Новий стовпчик заповнюється переданими даними `MeshRenderer`.
5. **Ущільнення вихідного чанка (Swap-and-Pop):** Щоб не залишити порожнечі у вихідному чанку архетипу `A`, остання активна сутність чанка копіюється на місце переміщеної, а її запис у глобальній таблиці розміщення сутностей оновлюється.

---

### Ітерація за запитами (Query Matching & Iteration)

Головною перевагою архітектури архетипів є швидкість виконання запитів (англ. *queries*). Системи декларують фільтри сутностей за допомогою бітових масок:
- **`All` (обов'язкові компоненти):** архетип мусить містити всі перелічені типи;
- **`Any` (хоча б один із компонентів):** архетип мусить містити принаймні один тип;
- **`None` (заборонені компоненти):** архетипи з цими типами відфільтровуються.

Під час виконання ігрового кадру системі не потрібно перевіряти кожну сутність окремо. Реєстр одноразово зіставляє бітову маску запиту з архетипами, після чого система ітерується безпосередньо за списком відповідних чанків:

```
Для кожного Archetype, що відповідає Query:
    Для кожного Chunk у Archetype:
        float* pos = GetColumn<Position>(Chunk);
        float* vel = GetColumn<Velocity>(Chunk);
        uint32_t count = Chunk->count;
        
        // Векторизований цикл над неперервною пам'яттю
        SIMD_Update(pos, vel, count);
```

Оскільки всі дані всередині чанка лежать поспіль без пропусків, процесор виконує ітерацію з граничною швидкістю пропускної здатності кешу L1, не виконуючи жодного умовного переходу чи розіменування покажчиків у внутрішньому циклі.

---

### Управління пам'яттю та вторинне використання чанків

Постійне виділення та звільнення пам'яті розміром 16 або 64 КБ через загальносистемні виклики операційної системи (такі як `mmap` у POSIX або `VirtualAlloc` у Windows) створює надмірні затримки перемикання контексту ядра та фрагментацію віртуального адресного простору.

Щоб мінімізувати накладні витрати пам'яті, чанковий реєстр використовує дворівневу схему алокації:

1. **Глобальний пул чанків (Chunk Memory Pool):** Реєстр резервує великий неперервний блок пам'яті (наприклад, 256 МБ) і розбиває його на фіксовані блоки по 16 КБ. Звільнені чанки не повертаються операційній системі, а додаються у зв'язний список вільних блоків (англ. *Free List*). Виділення нового чанка для будь-якого архетипу зводиться до вилучення голови списку за `O(1)`.
2. **Антифрагментація через злиття чанків:** Якщо внаслідок масового знищення сутностей два сусідні чанки одного архетипу виявляються заповненими менш ніж на 50%, фоновий процес реєстру переносить сутності з другого чанка в перший за допомогою операцій прямого копіювання пам'яті (`memcpy`), після чого порожній чанк негайно повертається в глобальний вільний пул.

---

### Буферизація команд (Command Buffers)

Пряма мутація архетипів під час ітерації за чанками категорично заборонена, оскільки операція Swap-and-Pop порушує послідовність обходу та призводить до стану гонитви (race condition).

Для відкладеної модифікації стану застосовують буфери команд сутностей (англ. *Entity Command Buffer / ECB*):
1. Під час роботи паралельних систем усі запити на створення сутностей, видалення або додавання компонентів записуються в локальний потоковий буфер команд;
2. Наприкінці кадру, під час фазового бар'єра синхронізації, головний потік послідовно застосовує накопичені команди до реєстру архетипів, мінімізуючи витрати на блокування пам'яті.

---

### Коди помилок та інваріанти контракту

| Код помилки | Умова виникнення | Дія реєстру |
| :--- | :--- | :--- |
| `ERR_INVALID_ENTITY` | `Entity ID` не існує в таблиці пошуку або generation застарів | Повертає `false` або `nullptr`, стан не змінюється |
| `ERR_DUPLICATE_COMPONENT` | Спроба додати компонент, який уже присутній в архетипі сутності | Операція скасовується, перехід не виконується |
| `ERR_COMPONENT_NOT_FOUND` | Спроба видалити компонент, якого сутність не має | Операція повертає `false` |
| `ERR_CHUNK_ALLOC_FAILED` | Вичерпано системну пам'ять або перевищено ліміт вирівняного пулу | Аварійне завершення виділення чанка |

#### Інваріанти структури:
1. **Інваріант щільності:** Усі сутності всередині будь-якого чанка займають індекси від `0` до `count - 1` без жодних порожнин.
2. **Інваріант вирівнювання:** Адреса початку кожного стовпця даних усередині чанка вирівняна за правилом `Offset[i] % Alignment[i] == 0`.
3. **Інваріант паралелізму:** Системи, які читають неперетинні набори компонентів різних архетипів, мають гарантію повної відсутності конфліктів пам'яті (відсутність блокувань та помилкового розділення кеш-ліній).
