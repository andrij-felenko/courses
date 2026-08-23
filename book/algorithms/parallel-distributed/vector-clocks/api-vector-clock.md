# 📋 Інтерфейс та структура даних бібліотеки векторного годинника

Цей документ визначає повний відкритий програмний контракт (API), специфікацію двійкової серіалізації, керування пам'яттю, гарантії потокобезпечності та інваріанти поведінки бібліотеки векторних годинників і версійних векторів для високонавантажених розподілених систем.

Бібліотека спроектована для роботи в двох основних режимах:
1. **Статичний режим (Static Array Mode):** фіксована кількість вузлів `N ≤ MAX_NODES`, нульові динамічні виділення пам'яті (zero-allocation), розміщення на стеку або в попередньо виділених пулах пам'яті. Оптимізовано для критичних до затримок мережевих рушіїв.
2. **Динамічний режим (Dynamic Sparse Mode):** відкритий набір ідентифікаторів вузлів `NodeID`, представлений динамічним розрідженим масивом або хеш-таблицею. Оптимізовано для хмарних сервісів із динамічним масштабуванням, де вузли реєструються та виводяться з експлуатації під час роботи.

### Типи даних та сигнатури функцій

#### 1. Перелік результатів порівняння (VectorComparison)

Результат порівняння двох векторів повертається як строго типізоване значення переліку:

| Значення | C / C++ Константа | Опис математичної семантики | Подальша дія розподіленої системи |
| :--- | :--- | :--- | :--- |
| `0` | `VC_CMP_EQUAL` / `VectorComparison::Equal` | Вектори збігаються за всіма координатами (`v1 == v2`). Події описують один і той самий стан. | Повторна доставка або дублікат; операція ігнорується без змін стану. |
| `1` | `VC_CMP_ANCESTOR` / `VectorComparison::Ancestor` | Вектор `v1` є прямим або транзитивним предком `v2` (`v1 < v2`). | Вектор `v1` застарів; стан `v2` містить свіжіші дані та повністю замінює `v1`. |
| `2` | `VC_CMP_DESCENDANT` / `VectorComparison::Descendant` | Вектор `v1` є прямим нащадком `v2` (`v1 > v2`). | Стан `v1` є новішим за `v2`; стан `v2` відкидається як застарілий. |
| `3` | `VC_CMP_CONCURRENT` / `VectorComparison::Concurrent` | Жоден із векторів не домінує (`v1 ∥ v2`). Виявлено паралельний конфлікт записів. | Запуск механізму розв'язання конфлікту: генерація братів (siblings) або злиття CRDT. |

#### 2. Базові структури та коди статусів

:::tabs
```c
typedef uint64_t vc_counter_t;
typedef uint32_t vc_node_id_t;

/* Окремий запис версійного вектора для конкретного актора */
typedef struct {
    vc_node_id_t node_id;
    vc_counter_t counter;
    uint64_t physical_wall_time_ms; /* UTC мітка в мілісекундах для евристичного прибирання сміття */
} vc_entry_t;

/* Динамічний векторний годинник із підтримкою динамічного росту */
typedef struct {
    vc_entry_t *entries;
    size_t count;
    size_t capacity;
    bool is_sorted; /* оптимізаційний прапорець для бінарного пошуку O(log N) */
} vc_dynamic_clock_t;

/* Коди помилок бібліотеки */
typedef enum {
    VC_OK = 0,
    VC_ERR_NULL_PTR = -1,
    VC_ERR_OUT_OF_MEMORY = -2,
    VC_ERR_BUFFER_TOO_SMALL = -3,
    VC_ERR_CORRUPTED_DATA = -4,
    VC_ERR_NODE_NOT_FOUND = -5,
    VC_ERR_CAPACITY_EXCEEDED = -6,
    VC_ERR_COUNTER_OVERFLOW = -7
} vc_status_t;
```
```cpp
#include <cstdint>
#include <cstddef>

using NodeId = uint32_t;
using Counter = uint64_t;

// Окремий запис версійного вектора для конкретного актора
struct Entry {
    NodeId node_id{0};
    Counter counter{0};
    uint64_t physical_wall_time_ms{0}; // UTC мітка в мілісекундах
};

// Коди помилок та статусів бібліотеки
enum class Status : int32_t {
    Ok = 0,
    NullPtr = -1,
    OutOfMemory = -2,
    BufferTooSmall = -3,
    CorruptedData = -4,
    NodeNotFound = -5,
    CapacityExceeded = -6,
    CounterOverflow = -7
};
```
:::

#### 3. Таблиця функцій основного інтерфейсу

| Сигнатура функції | Призначення та параметри | Передумови (Preconditions) | Післяумови (Postconditions) | Часова складність |
| :--- | :--- | :--- | :--- | :--- |
| `vc_status_t vc_init(vc_dynamic_clock_t *vc, size_t initial_cap)` | Ініціалізує векторний годинник із виділенням початкової місткості `initial_cap`. | `vc != NULL` | `vc->entries != NULL`, `vc->count == 0`, `vc->capacity == initial_cap` | `O(1)` |
| `void vc_free(vc_dynamic_clock_t *vc)` | Звільняє виділену динамічну пам'ять масиву записів та обнуляє поля. | `vc != NULL` | `vc->entries == NULL`, `vc->count == 0`, `vc->capacity == 0` | `O(1)` |
| `vc_status_t vc_tick(vc_dynamic_clock_t *vc, vc_node_id_t node_id)` | Збільшує лічильник вузла `node_id` на одиницю. Якщо вузол відсутній, додає новий запис. | `vc != NULL` | `counter[node_id] == old_counter + 1`. Масив залишається валідним. | `O(N)` у несортованому, `O(log N)` у сортованому |
| `vc_status_t vc_set(vc_dynamic_clock_t *vc, vc_node_id_t node_id, vc_counter_t val)` | Встановлює точне значення лічильника для вузла `node_id`. | `vc != NULL`, `val >= current_val` | `counter[node_id] == val` | `O(N)` |
| `vc_counter_t vc_get(const vc_dynamic_clock_t *vc, vc_node_id_t node_id)` | Повертає значення лічильника для вузла `node_id`. Якщо вузла немає у векторі, повертає `0`. | `vc != NULL` | Стан `vc` не змінюється. | `O(log N)` або `O(1)` |
| `vc_status_t vc_merge(vc_dynamic_clock_t *dest, const vc_dynamic_clock_t *src)` | Обчислює точну верхню межу (Join, `max` для кожного `node_id`). Результат зберігається в `dest`. | `dest != NULL`, `src != NULL` | `∀ k: dest'[k] == max(dest[k], src[k])` | `O(N + M)` для сортованих векторів |
| `VectorComparison vc_compare(const vc_dynamic_clock_t *v1, const vc_dynamic_clock_t *v2)` | Порівнює два вектори за аксіомами часткового порядку. | `v1 != NULL`, `v2 != NULL` | Повертає один із чотирьох статусів `VectorComparison`. | `O(N + M)` |
| `bool vc_dominates(const vc_dynamic_clock_t *v1, const vc_dynamic_clock_t *v2)` | Перевіряє, чи покриває вектор `v1` усю причинну історію вектора `v2` (`v1 ≥ v2`). | `v1 != NULL`, `v2 != NULL` | Повертає `true`, якщо `∀ k: v1[k] >= v2[k]`. | `O(N + M)` |
| `vc_status_t vc_prune(vc_dynamic_clock_t *vc, size_t max_entries)` | Зменшує розмір вектора до `max_entries`, видаляючи найстаріші вузли за часовою міткою. | `vc != NULL`, `max_entries > 0` | `vc->count <= max_entries`. Видалені елементи вважаються нульовими. | `O(N log N)` |
| `vc_status_t vc_clone(vc_dynamic_clock_t *dest, const vc_dynamic_clock_t *src)` | Створює глибоку копію вектора `src` у новому об'єкті `dest`. | `dest != NULL`, `src != NULL` | `dest` є незалежною точною копією `src`. | `O(N)` |

### Формат двійкової серіалізації через мережу

Для мінімізації накладних витрат мережевого трафіку бібліотека підтримує компактний упакований бінарний формат із кодуванням змінної довжини (LEB128 / Varint).

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Magic (0x5643)| Format Version| Flags (0x00)  | Entry Count   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                 Varint: Node_ID #1 (1..5 байтів)             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                 Varint: Counter #1 (1..10 байтів)            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                 ... наступні пари (Node_ID, Counter) ...      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

#### Специфікація полів двійкового пакета

- **Magic Number (16 біт):** `0x5643` (символи ASCII `'V'`, `'C'`) — захист від парсингу некоректного потоку даних.
- **Format Version (8 біт):** `0x01` — версія бінарного протоколу.
- **Flags (8 біт):** бітова маска опцій (біт 0: сортований порядок вузлів; біт 1: наявність міток фізичного часу).
- **Entry Count (Varint / 1..4 байти):** кількість непорожніх записів у векторі.
- **Масив пар `(Node_ID, Counter)`:** кожен ідентифікатор та значення лічильника упаковуються через алгоритм беззнакового LEB128 (Unsigned LEB128). Значення `< 128` займають рівно 1 байт.

### Формат JSON для REST API та налагодження

Для діагностики, журналювання та зовнішніх веб-інтерфейсів використовується канонічний JSON-об'єкт, де ключами є рядкові ідентифікатори вузлів, а значеннями — цілі числа:

```json
{
  "version_vector": {
    "node_eu_central_1": 14205,
    "node_us_east_2": 8912,
    "node_ap_southeast_1": 412
  },
  "metadata": {
    "generated_at_unix_ms": 1771598400000,
    "dominant_actor": "node_eu_central_1"
  }
}
```

### Модель потокобезпечності та конкурентного доступу

У багатопотокових мережевих рушіях структури векторних годинників використовуються у двох сценаріях доступу:

1. **Модель єдиного власника (Single-Threaded Worker / Actor Model):** кожен актор або потік обробки з'єднань володіє власним екземпляром `VectorClock`. Модифікації (`vc_tick`, `vc_merge`) виконуються без м'ютексів та атомарних бар'єрів пам'яті, забезпечуючи максимальну швидкість виконання (`< 10` наносекунд на операцію).
2. **Модель спільного стану (Shared Concurrent Access):** якщо векторний годинник розділяється між пулом робочих потоків, обгортка бібліотеки забезпечує потокобезпечність через блокування з подвійним рівнем доступу:
   - **Операції читання (`vc_compare`, `vc_dominates`, серіалізація):** захоплюють розділене блокування на читання (Shared Read Lock / `std::shared_mutex`).
   - **Операції запису (`vc_tick`, `vc_merge`, `vc_prune`):** захоплюють ексклюзивне блокування на запис (Exclusive Write Lock).
   - **Атомарний локальний тік (Atomic Fast-Path):** якщо потрібно збільшити лише власний лічильник вузла без зміни розмірності вектора, використовується атомарна інструкція `fetch_add` з семантикою `std::memory_order_acq_rel` без захоплення важких м'ютексів операційної системи.

### Оцінка просторової складності та локальності кешу

Для мінімізації промахів кешу процесора (CPU Cache Misses) структура `vc_dynamic_clock_t` спроектована як неперервний масив структур (Array of Structures, AoS), вирівняний по межі 64 байтів:

```
Розмір елемента vc_entry_t:
sizeof(node_id) + sizeof(counter) + sizeof(timestamp) = 4 + 8 + 8 = 20 байтів
З вирівнюванням компілятора (Padding): 24 байти

Місткість однієї лінії кешу L1 (64 байти):
Вміщує 2 повні записи vc_entry_t без виходу за межі кеш-лінії.
```

Для статичного режиму `VectorClock` з фіксованим масивом `uint64_t ticks[16]` розмір структури становить рівно `128` байтів, що ідеально лягає у 2 лінії кешу L1 процесора та повністю виключає звернення до повільної оперативної пам'яті DRAM.

### Високорівнева C++ обгортка (VectorClockHandle)

Для безпечної інтеграції в сучасні C++ кодові бази бібліотека надає RAII-обгортку з семантикою переміщення та підтримкою стандартних алгоритмів:

```cpp
namespace vclock {

class VectorClockHandle {
public:
    explicit VectorClockHandle(size_t initial_capacity = 8);
    VectorClockHandle(std::initializer_list<std::pair<vc_node_id_t, vc_counter_t>> init);

    // RAII та заборона неявного копіювання важких ресурсів
    ~VectorClockHandle();
    VectorClockHandle(const VectorClockHandle& other);
    VectorClockHandle& operator=(const VectorClockHandle& other);
    VectorClockHandle(VectorClockHandle&& other) noexcept;
    VectorClockHandle& operator=(VectorClockHandle&& other) noexcept;

    // Основні операції
    void tick(vc_node_id_t node_id);
    void set(vc_node_id_t node_id, vc_counter_t counter);
    [[nodiscard]] vc_counter_t get(vc_node_id_t node_id) const noexcept;
    void merge(const VectorClockHandle& other);
    void prune(size_t max_entries);

    // Порівняння та перевірка причинності
    [[nodiscard]] VectorComparison compare(const VectorClockHandle& other) const noexcept;
    [[nodiscard]] bool dominates(const VectorClockHandle& other) const noexcept;
    [[nodiscard]] bool is_concurrent_with(const VectorClockHandle& other) const noexcept;

    // Серіалізація
    [[nodiscard]] std::vector<uint8_t> to_binary() const;
    static std::expected<VectorClockHandle, vc_status_t> from_binary(std::span<const uint8_t> data);
    [[nodiscard]] std::string to_json() const;

private:
    vc_dynamic_clock_t raw_;
};

} // namespace vclock
```

### Філософія обробки помилок та діагностика

Бібліотека не генерує неперехоплюваних винятків C++ у ядрі C-функцій, дотримуючись суворої дисципліни кодів повернення:
- **Нульові вказівники (`VC_ERR_NULL_PTR`):** функції негайно повертають помилку, якщо будь-який обов'язковий аргумент є `NULL`.
- **Вичерпання пам'яті (`VC_ERR_OUT_OF_MEMORY`):** якщо системний алокатор `malloc` / `realloc` повертає нуль під час динамічного розширення вектора, попередній стан структури залишається неушкодженим і валідним (Strong Exception Safety Guarantee).
- **Переповнення буфера (`VC_ERR_BUFFER_TOO_SMALL`):** якщо цільовий масив байтів для серіалізації менший за розмір закодованого пакета, запис не починається, а функція повертає необхідний розмір буфера.
- **Пошкодження даних (`VC_ERR_CORRUPTED_DATA`):** невідповідність контрольної суми, магічного числа або наявність некоректно закодованого Varint-байта призводить до відхилення всього пакета без витоку пам'яті.

### Інтеграція в рушій сховища ключ-значення (Storage Engine Integration)

Типовий життєвий цикл використання версійного вектора при записі та читанні в реплікованому сховищі:

1. **Фаза читання (Read Path):**
   Клієнт виконує `GET(key)` на координаторний вузол. Координатор надсилає паралельні запити на `R` реплік. Отримавши `R` відповідей, координатор попарно порівнює їхні вектори функцією `vc_compare`. Якщо одна відповідь домінує над усіма іншими (`VC_CMP_DESCENDANT`), клієнту повертається єдине значення. Якщо виявлено `VC_CMP_CONCURRENT`, координатор повертає клієнту масив усіх братів-двійників разом із масивом їхніх векторів.
2. **Фаза запису (Write Path):**
   Клієнт формує нове значення `PUT(key, value, context_vector)`. Контекстний вектор — це результат об'єднання (`vc_merge`) векторів усіх прочитаних раніше братів. Координатор додає локальний тік `vc_tick(context_vector, coordinator_node_id)` і розсилає запис на `W` реплік. Оскільки новий вектор строго більший за всіх попередників, репліки безконфліктно замінюють старі версії новим значенням.

### Інваріанти бібліотеки та гарантії цілісності

1. **Монотонність локальних оновлень:** для будь-якого вузла `k` після виклику `vc_tick(vc, k)` значення `counter[k]` суворо збільшується на одиницю.
2. **Ідемпотентність та комутативність злиття:** для будь-яких векторів `A` та `B`:
   `vc_merge(A, B) == vc_merge(B, A)` та `vc_merge(A, A) == A`.
3. **Транзитивність відношень:** якщо `vc_compare(A, B) == VC_CMP_ANCESTOR` та `vc_compare(B, C) == VC_CMP_ANCESTOR`, то гарантується `vc_compare(A, C) == VC_CMP_ANCESTOR`.
4. **Коректність присікання (Pruning Invariant):** видалення старих записів функцією `vc_prune` може перетворити відношення `VC_CMP_ANCESTOR` на `VC_CMP_CONCURRENT`, але **ніколи** не може перетворити `VC_CMP_CONCURRENT` на `VC_CMP_ANCESTOR` (система може створити хибний конфлікт, але гарантовано не допустить тихої втрати даних відкиданням конкурентного запису).
5. **Стійкість до пошкодження двійкових пакетів:** десеріалізатор перевіряє магічне число `0x5643`, довжину буфера перед кожним читанням Varint та відхиляє пакети з немонотонними чи пошкодженими значеннями, повертаючи код `VC_ERR_CORRUPTED_DATA` без аварійного завершення процесу.
