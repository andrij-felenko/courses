# 📋 Інтерфейс та контракт асинхронного dataflow-рушія

Ця специфікація описує архітектурний контракт, структури даних, правила володіння пам'яттю та програмний інтерфейс (API) системного рушія динамічного потоку даних (`df_engine`). Інтерфейс спроектований для побудови високонавантажених асинхронних обчислювальних конвеєрів, розподілу динамічних графів задач та низькорівневого керування пам'яттю за моделлю Explicit Token Store (ETS) і нестрогих I-структур.

Архітектура рушія базується на повній відсутності глобальних блокувань на гарячому шляху передачі повідомлень. Усі структури даних вирівняні за межами 64-байтних кеш-ліній для запобігання апаратному ефекту хибного спільного використання (*false sharing*).

## 1. Базові типи та модель токенів

Токен є атомарним неподільним квантом даних, що циркулює крізь обчислювальне кільце рушія. У системі визначено строгий поділ обов'язків між адресацією інструкції, контекстом виконання та корисним навантаженням.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

typedef uint32_t df_frame_id_t;  /* Унікальний числовий дескриптор кадру активації ETS */
typedef uint16_t df_node_id_t;   /* Індекс інструкції всередині статичного графа */
typedef uint8_t  df_port_t;      /* Номер цільового вхідного порту: 0 (лівий), 1 (правий) */

typedef struct {
    df_frame_id_t frame_id;      /* Базовий контекст кадру активації */
    df_node_id_t  node_id;       /* Адреса цільового оператора в Node Store */
    df_port_t     port;          /* Вхідний порт операнда */
    uint8_t       flags;         /* Прапорці керування (EOF, Ack, Trap) */
    uint64_t      value;         /* 64-бітне значення операнда (IEEE 754 або ціле) */
} df_token_t;
```
```cpp
#include <cstdint>
#include <concepts>
#include <span>
#include <optional>

namespace dataflow {

using FrameId = uint32_t;
using NodeId  = uint16_t;
using Port    = uint8_t;

enum class TokenFlags : uint8_t {
    None         = 0x00,
    EndOfStream  = 0x01,
    Acknowledge  = 0x02,
    ExceptionTrap= 0x04
};

struct Token {
    FrameId    frame_id{0};
    NodeId     node_id{0};
    Port       port{0};
    TokenFlags flags{TokenFlags::None};
    uint64_t   value{0};

    [[nodiscard]] constexpr bool is_ack() const noexcept {
        return (static_cast<uint8_t>(flags) & static_cast<uint8_t>(TokenFlags::Acknowledge)) != 0;
    }
};

} // namespace dataflow
```
:::

### Пояснення полів токена:
* `frame_id` (`FrameId`): вказує на конкретний виділений кадр активації в пам'яті ETS. Забезпечує строгу ізоляцію паралельних ітерацій циклів та рекурсивних гілок одного й того самого графа.
* `node_id` (`NodeId`): індекс вузла в статичній таблиці операторів `Node Store`.
* `port` (`Port`): селектор операнда для бінарних інструкцій. `Port 0` представляє перший вхід (наприклад, зменшуване), `Port 1` — другий вхід (від'ємник). Для унарних інструкцій поле ігнорується або дорівнює `0`.
* `flags` (`TokenFlags`): бітова маска службових сигналів для контролю конвеєра та передачі апаратних винятків.
* `value`: 64-бітний скалярний регістр даних або покажчик на вирівняний блок пам'яті.

## 2. Коди операцій та дескриптори вузлів графа

Кожен вузол графа описує один чистий функціональний оператор та перелік орієнтованих дуг, якими результат передається вузлам-наступникам.

:::tabs
```c
typedef enum {
    DF_OP_NOP      = 0x00,  /* Пересилка операнда без змін */
    DF_OP_ADD      = 0x01,  /* Додавання: result = in0 + in1 */
    DF_OP_SUB      = 0x02,  /* Віднімання: result = in0 - in1 */
    DF_OP_MUL      = 0x03,  /* Множення: result = in0 * in1 */
    DF_OP_DIV      = 0x04,  /* Ділення: result = in0 / in1 */
    DF_OP_BRANCH   = 0x05,  /* Умовне розгалуження за предикатом */
    DF_OP_MERGE    = 0x06,  /* Детерміноване злиття потоків */
    DF_OP_I_READ   = 0x07,  /* Нестроге читання з I-структури */
    DF_OP_I_WRITE  = 0x08,  /* Одноразовий запис у I-структуру */
    DF_OP_CALL     = 0x09,  /* Виділення кадру та виклик підграфа */
    DF_OP_RET      = 0x0A   /* Повернення результату у батьківський контекст */
} df_opcode_t;

#define DF_MAX_ARCS 4

typedef struct {
    df_node_id_t dest_node;
    df_port_t    dest_port;
} df_arc_t;

typedef struct {
    df_opcode_t opcode;
    uint8_t     is_binary;     /* 1 = бінарна (потребує ETS), 0 = унарна */
    uint8_t     slot_offset;   /* Зміщення слота в кадрі активації FP + offset */
    uint8_t     arc_count;     /* Кількість вихідних з'єднань (0..DF_MAX_ARCS) */
    df_arc_t    arcs[DF_MAX_ARCS];
} df_node_desc_t;
```
```cpp
#include <vector>

namespace dataflow {

enum class Opcode : uint8_t {
    Nop,
    Add,
    Sub,
    Mul,
    Div,
    Branch,
    Merge,
    IRead,
    IWrite,
    Call,
    Return
};

struct Arc {
    NodeId dest_node{0};
    Port   dest_port{0};
};

struct NodeDesc {
    Opcode           opcode{Opcode::Nop};
    bool             is_binary{false};
    uint8_t          slot_offset{0};
    std::vector<Arc> successors;
};

} // namespace dataflow
```
:::

## 3. Статуси та коди завершення функцій

Усі функції API повертають детермінований числовий статус виконання або типізований результат `std::expected` у C++23.

| Код помилки C | Значення | Опис причини |
| :--- | :--- | :--- |
| `DF_OK` | `0` | Операцію успішно виконано без затримок |
| `DF_ERR_INVALID_ARG` | `-1` | Передано некоректний покажчик, від'ємний розмір або неіснуючий дескриптор |
| `DF_ERR_QUEUE_FULL` | `-2` | Кільцевий буфер черги токенів заповнений (необхідний зворотний тиск / backpressure) |
| `DF_ERR_FRAME_EXHAUSTED` | `-3` | Пул вільних кадрів активації ETS вичерпано (потрібне розширення або дроп ітерацій) |
| `DF_ERR_I_STRUCT_DUPLICATE`| `-4` | Спроба повторного запису в комірку I-структури зі станом `PRESENT` |
| `DF_ERR_NODE_OUT_OF_BOUNDS`| `-5` | Індекс вузла `node_id` виходить за межі скомпільованого графа |
| `DF_ERR_NO_MEMORY` | `-6` | Системний розподілювач пам'яті ОС повернув помилку нестачі RAM |

## 4. Керування життєвим циклом рушія

Функції ініціалізації виділяють ресурси пулу потоків, створюють внутрішні кільцеві черги FIFO та налаштовують структури пам'яті ETS.

:::tabs
```c
typedef struct {
    uint32_t worker_threads;       /* Кількість потоків-обчислювачів (0 = автовизначення) */
    size_t   token_queue_capacity; /* Розмір буфера черги токенів (степінь 2) */
    uint32_t max_frames;           /* Розмір пулу кадрів активації */
    uint32_t slots_per_frame;      /* Кількість операндних слотів у кожному кадрі */
} df_engine_cfg_t;

typedef struct df_engine df_engine_t;

df_status_t df_engine_init(
    df_engine_t**          out_engine,
    const df_engine_cfg_t* cfg
);

df_status_t df_engine_shutdown(df_engine_t* engine);
```
```cpp
#include <memory>
#include <expected>

namespace dataflow {

struct EngineConfig {
    uint32_t worker_threads{0};
    size_t   token_queue_capacity{4096};
    uint32_t max_frames{256};
    uint32_t slots_per_frame{16};
};

enum class Status : int32_t {
    Ok                 = 0,
    InvalidArg         = -1,
    QueueFull          = -2,
    FrameExhausted     = -3,
    IStructDuplicate   = -4,
    NodeOutOfBounds    = -5,
    NoMemory           = -6
};

class Engine {
public:
    static std::expected<std::unique_ptr<Engine>, Status> create(const EngineConfig& cfg);
    virtual ~Engine() = default;

    virtual Status shutdown() noexcept = 0;
};

} // namespace dataflow
```
:::

### Контракт життєвого циклу:
1. **Ініціалізація**: функція `df_engine_init` створює робочі потоки у стані готовності. Пам'ять кадрів активації виділяється єдиним суцільним блоком для мінімізації промахів TLB.
2. **Зупинка**: функція `df_engine_shutdown` виставляє атомарний прапорець зупинки, пробуджує всі заблоковані потоки عبر умовні змінні та дочікується коректного завершення виконання (`pthread_join` / `thread::join`). Усі незавершені кадри маркуються як недійсні.

## 5. Створення та конфігурація графів

Граф є незмінною (*immutable*) структурою після завершення стадії конфігурації. Будь-яка модифікація вузлів під час виконання є помилкою і призводить до невизначеної поведінки.

:::tabs
```c
typedef struct df_graph df_graph_t;

df_status_t df_graph_create(
    df_graph_t** out_graph,
    uint32_t     max_nodes
);

df_status_t df_graph_set_node(
    df_graph_t*           graph,
    df_node_id_t          node_id,
    const df_node_desc_t* desc
);

df_status_t df_graph_destroy(df_graph_t* graph);
```
```cpp
namespace dataflow {

class Graph {
public:
    static std::expected<std::unique_ptr<Graph>, Status> create(uint32_t max_nodes);
    virtual ~Graph() = default;

    virtual Status set_node(NodeId node_id, NodeDesc desc) noexcept = 0;
    [[nodiscard]] virtual const NodeDesc* get_node(NodeId node_id) const noexcept = 0;
    [[nodiscard]] virtual size_t node_count() const noexcept = 0;
};

} // namespace dataflow
```
:::

## 6. Керування кадрами активації (ETS Allocator)

Кадр активації створюється на початку кожного циклу чи виклику функції. Він містить масив слотів операндів, захищених атомарними бітами присутності.

:::tabs
```c
df_status_t df_frame_alloc(
    df_engine_t*   engine,
    df_frame_id_t* out_frame_id
);

df_status_t df_frame_free(
    df_engine_t*  engine,
    df_frame_id_t frame_id
);
```
```cpp
namespace dataflow {

class FrameHandle {
public:
    FrameHandle() noexcept = default;
    FrameHandle(Engine* engine, FrameId id) noexcept : engine_(engine), id_(id) {}
    ~FrameHandle() {
        if (engine_ && id_ != 0) {
            release();
        }
    }

    FrameHandle(const FrameHandle&) = delete;
    FrameHandle& operator=(const FrameHandle&) = delete;
    FrameHandle(FrameHandle&& other) noexcept : engine_(other.engine_), id_(other.id_) {
        other.engine_ = nullptr;
        other.id_ = 0;
    }

    [[nodiscard]] FrameId id() const noexcept { return id_; }

private:
    void release() noexcept;
    Engine* engine_{nullptr};
    FrameId id_{0};
};

} // namespace dataflow
```
:::

### Інваріанти кадрів ETS:
* **Атомарність виділення**: виділення кадру з пулу виконується за `O(1)` за допомогою атомарного бітового сканування вільних індексів (*lock-free bitset*).
* **Скидання слотів**: перед поверненням дескриптора всі біти присутності слотів гарантовано скидаються в `0` (`EMPTY`), а значення обнуляються.
* **Переповнення**: якщо всі кадри зайняті, функція негайно повертає статус `DF_ERR_FRAME_EXHAUSTED`. Викликаючий код зобов'язаний обмежити розгортання графа за допомогою механізму `k`-обмеження.

## 7. Емісія токенів та асинхронне виконання

Функція емісії токена вставляє квант даних у кільцеву чергу рушія.

:::tabs
```c
df_status_t df_token_emit(
    df_engine_t*      engine,
    const df_token_t* token
);
```
```cpp
namespace dataflow {

class EngineInterface {
public:
    virtual ~EngineInterface() = default;
    virtual Status emit(const Token& token) noexcept = 0;
};

} // namespace dataflow
```
:::

* **Потокобезпечність**: функція повністю потокобезпечна і може викликатися паралельно з довільної кількості продюсерів.
* **Неблокуюча поведінка**: якщо черга заповнена, функція повертає `DF_ERR_QUEUE_FULL` без блокування викликаючого потоку, що дозволяє реалізувати гнучкі політики відкату (*exponential backoff*).

## 8. Підсистема нестрогої пам'яті (I-Structures API)

I-структури надають апаратну абстракцію масивів з одноразовим записом та автоматичною чергою очікування для передчасних читачів.

:::tabs
```c
typedef struct df_istructure df_istructure_t;

df_status_t df_istructure_create(
    df_istructure_t** out_istruct,
    size_t            element_count
);

df_status_t df_istructure_read_async(
    df_istructure_t* istruct,
    size_t           index,
    df_token_t       consumer_token
);

df_status_t df_istructure_write(
    df_engine_t*     engine,
    df_istructure_t* istruct,
    size_t           index,
    uint64_t         value
);

df_status_t df_istructure_destroy(df_istructure_t* istruct);
```
```cpp
namespace dataflow {

class IStructure {
public:
    static std::expected<std::unique_ptr<IStructure>, Status> create(size_t element_count);
    virtual ~IStructure() = default;

    virtual Status read_async(size_t index, Token consumer_token) noexcept = 0;
    virtual Status write(Engine* engine, size_t index, uint64_t value) noexcept = 0;
    [[nodiscard]] virtual size_t size() const noexcept = 0;
};

} // namespace dataflow
```
:::

### Семантичні правила I-структур:
1. **Читання (`read_async`)**:
   * Якщо комірка `index` має стан `PRESENT`: значення миттєво підставляється в `consumer_token.value`, і токен відправляється у чергу рушія.
   * Якщо комірка має стан `EMPTY` або `DEFERRED`: дескриптор `consumer_token` додається до списку відкладених продовжень комірки. Викликаючий потік не блокується і продовжує виконання наступних задач.
2. **Запис (`write`)**:
   * Якщо комірка має стан `EMPTY`: значення записується, а стан змінюється на `PRESENT`.
   * Якщо стан був `DEFERRED`: значення записується, стан стає `PRESENT`, а всім підписаним читачам із черги відкладених запитів генеруються токени-відповіді з новим значенням та надсилаються у чергу рушія.
   * Якщо стан уже був `PRESENT`: операція зазнає краху, генерує виняток і повертає `DF_ERR_I_STRUCT_DUPLICATE`.

## 9. Модель узгодженості пам'яті та порядок синхронізації

У потоковому рушії виконання спирається на строгу послідовність публікації даних без явних глобальних бар'єрів пам'яті:

1. **Семантика Acquire-Release для токенів**: запис значення операнда у кадр активації ETS виконується з семантикою `std::memory_order_release`. Коли парний потік зчитує операнд після успішного скидання біта присутності через `std::memory_order_acquire`, апаратура гарантує видимість усіх попередніх модифікацій пам'яті продюсера.
2. **Неможливість часткового читання (Torn Reads)**: розмір токена вирівняно за 64-бітним словом, що гарантує атомарність читання та запису на сучасних 64-бітних мікропроцесорних архітектурах x86-64 та ARM64.
3. **Ізоляція кадрів активації**: різні кадри активації `frame_id` є повністю ортогональними. Звернення до слотів різних кадрів ніколи не потребують міжпотокової синхронізації або блокувань, забезпечуючи лінійне масштабування пропускної здатності конвеєра при збільшенні кількості ядер.

## 10. Обробка крайових випадків та відмова під навантаженням

1. **Переповнення кільцевої черги (Queue Overflow)**: при сплесках паралелізму функція `df_token_emit` повертає статус `DF_ERR_QUEUE_FULL`. Клієнтський код повинен застосовувати стратегію експоненційного очікування (*exponential backoff*) з короткою паузою процесора `_mm_pause()` / `yield()`, або зменшувати параметр `k` у графах циклів.
2. **Вичерпання пулу кадрів активації**: якщо рекурсивний алгоритм генерує більше активних гілок, ніж фізично вміщує пул `max_frames`, виклик `df_frame_alloc` завершується з помилкою `DF_ERR_FRAME_EXHAUSTED`. Рушій не допускає дедлоку, передаючи керування планувальнику для тимчасової серіалізації виконання гілок.
3. **Захист від повторного запису (Double-Write Trap)**: спроба вдруге записати дані в ту саму комірку I-структури свідчить про недетермінований конфлікт у графі програми. Рушій негайно перехоплює цю операцію, фіксує діагностичний слід помилки із зазначенням ідентифікатора інструкції-порушника та повертає код `DF_ERR_I_STRUCT_DUPLICATE`.
