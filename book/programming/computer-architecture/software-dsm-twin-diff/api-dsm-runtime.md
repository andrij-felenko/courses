# 📋 Програмний інтерфейс середовища виконання Twin-and-Diff DSM

Середовище розподіленої спільної пам'яті на базі протоколу Twin-and-Diff надає прикладним програмам двійковий інтерфейс (ABI) та бібліотеку функцій простору користувача. Цей контракт визначає життєвий цикл розподілених областей пам'яті, функції синхронізації епох (замки та бар'єри), структуру бінарних пакетів відмінностей та механізми безпечної обробки системних сторінкових виключень.

## Базові типи даних та структури дескрипторів

Усі структури даних вирівняні за межами слів для усунення накладних витрат маршалінгу при міжвузловій передачі. Контракт визначає три основні стани сторінки, структуру дескриптора модифікованого чанка та формат мережного кадру різниці.

Усі числові поля багатобайтових заголовків передаються у стандартному мережному порядку байтів (Big-Endian). Перед відправкою середовище виконує конвертацію через `htons()` та `htonl()`, а при отриманні — через `ntohs()` та `ntohl()`, що гарантує коректну роботу в гетерогенних кластерах із різною архітектурою процесорів.

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define DSM_PAGE_SIZE       4096
#define DSM_MAX_NODES       64
#define DSM_MAX_CHUNKS      128

typedef enum {
    DSM_SUCCESS             =  0,
    DSM_ERR_INVALID_PARAM   = -1,
    DSM_ERR_NO_MEMORY       = -2,
    DSM_ERR_MPROTECT_FAILED = -3,
    DSM_ERR_SIGNAL_FAILED   = -4,
    DSM_ERR_OUT_OF_BOUNDS   = -5,
    DSM_ERR_BUFFER_OVERFLOW = -6
} dsm_status_t;

typedef enum {
    DSM_PAGE_INVALID = 0,   /* PROT_NONE: байти відсутні або застарілі */
    DSM_PAGE_READ_ONLY,     /* PROT_READ: чистий стан, читання без збоїв */
    DSM_PAGE_DIRTY_TWINNED  /* PROT_READ|WRITE: активний двійник, дозволено запис */
} dsm_page_state_t;

/* Заголовок неперервного сегмента відмінностей всередині 4 КБ сторінки */
typedef struct __attribute__((packed)) {
    uint16_t offset;        /* Зсув від початку сторінки (0 .. 4095) */
    uint16_t length;        /* Довжина модифікованого діапазону в байтах (1 .. 4096) */
} dsm_diff_header_t;

/* Структура бінарного пакета різниці сторінки */
typedef struct {
    uint32_t page_id;       /* Глобальний логічний індекс сторінки */
    uint32_t epoch_id;      /* Індекс часового інтервалу / епохи вузла-автора */
    uint16_t chunk_count;   /* Кількість окремих змінених діапазонів */
    uint16_t data_bytes;    /* Сумарний розмір корисних байтів даних */
    uint8_t  payload[DSM_PAGE_SIZE]; /* Буфер заголовків dsm_diff_header_t та сирих даних */
} dsm_diff_packet_t;

/* Конфігурація ініціалізації середовища DSM */
typedef struct {
    size_t   shared_heap_size;   /* Загальний розмір спільного адресного простору в байтах */
    uint32_t node_id;            /* Унікальний ідентифікатор локального вузла (0 .. DSM_MAX_NODES-1) */
    uint32_t total_nodes;        /* Загальна кількість вузлів у кластері */
    bool     enable_simd_diff;   /* Прапорець активації AVX2/AVX-512 прискорення */
} dsm_config_t;
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <vector>
#include <system_error>

constexpr size_t DsmPageSize = 4096;
constexpr size_t DsmMaxNodes = 64;
constexpr size_t DsmMaxChunks = 128;

enum class DsmErrorCode : int {
    Success = 0,
    InvalidParam = -1,
    NoMemory = -2,
    MprotectFailed = -3,
    SignalFailed = -4,
    OutOfBounds = -5,
    BufferOverflow = -6
};

enum class PageAccessState : uint8_t {
    Invalid = 0,
    ReadOnly = 1,
    DirtyTwinned = 2
};

struct alignas(uint16_t) DiffChunkHeader {
    uint16_t offset{0};
    uint16_t length{0};
};

struct DiffPacket {
    uint32_t pageId{0};
    uint32_t epochId{0};
    uint16_t chunkCount{0};
    std::vector<std::byte> payload;
};

struct DsmEngineConfig {
    size_t sharedHeapSize{1024 * 1024 * 64};
    uint32_t nodeId{0};
    uint32_t totalNodes{1};
    bool enableSimdAcceleration{true};
};
```
:::

## Організація адресного простору та вирівнювання

Спільна пам'ять DSM вимагає ідентичного відображення віртуальних адрес на всіх серверах кластера. Це забезпечує прозору передачу складних динамічних структур даних (зв'язних списків, бінарних дерев, графів), де 64-бітні вказівники зберігають коректність без додаткової трансляції на приймаючій стороні.

Під час виклику `dsm_init()` бібліотека резервує фіксований діапазон віртуальних адрес за допомогою системного виклику:
```
mmap(DSM_BASE_ADDRESS, config->shared_heap_size, PROT_NONE, MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1, 0)
```
Якщо зазначений фіксований діапазон уже зайнятий іншими бібліотеками процесу, функція ініціалізації повертає код помилки `DSM_ERR_NO_MEMORY`. Для гарантії сумісності адреса `DSM_BASE_ADDRESS` обирається у верхній половині користувацького адресного простору x86-64 (наприклад, `0x600000000000`), подалі від сегментів стека та динамічної купи процесу.

## Керування життєвим циклом середовища

Ініціалізація та демонтаж середовища відповідають за безпечну інтеграцію з ядром операційної системи, реєстрацію розширених обробників сигналів та формування пулів двійників.

:::tabs
```c
/* Ініціалізація середовища DSM, пулу двійників та обробника SIGSEGV */
dsm_status_t dsm_init(const dsm_config_t *config);

/* Виділення спільного діапазону пам'яті */
void* dsm_alloc_shared(size_t size_bytes);

/* Звільнення виділеної спільної пам'яті */
void dsm_free_shared(void *ptr);

/* Демонтаж середовища DSM та відновлення системних обробників сигналів */
void dsm_destroy(void);
```
```cpp
class IDsmRuntime {
public:
    virtual ~IDsmRuntime() = default;
    virtual std::expected<void, DsmErrorCode> initialize(const DsmEngineConfig& config) noexcept = 0;
    virtual std::expected<std::span<std::byte>, DsmErrorCode> allocateShared(size_t sizeBytes) noexcept = 0;
    virtual void freeShared(std::span<std::byte> region) noexcept = 0;
    virtual void shutdown() noexcept = 0;
};
```
:::

Детальний опис поведінки функцій життєвого циклу:

- **`dsm_init`**: Приймає конфігураційну структуру, виділяє спільний анонімний діапазон віртуальних адрес через `mmap()`, резервує масив двійників і встановлює обробник сигналу `SIGSEGV` через `sigaction()` із прапорцями `SA_SIGINFO | SA_NODEFER`. Повертає `DSM_SUCCESS` або код помилки. Повторний виклик без попереднього `dsm_destroy()` повертає `DSM_ERR_INVALID_PARAM`.
- **`dsm_alloc_shared`**: Виділяє діапазон пам'яті всередині керованого простору DSM. Розмір автоматично вирівнюється вгору до кратності `DSM_PAGE_SIZE` (4096 байтів). Усі сторінки отримують початковий захист `PROT_READ` (`DSM_PAGE_READ_ONLY`). При нестачі віртуального простору повертає `NULL`.
- **`dsm_free_shared`**: Повертає сторінки до внутрішнього пулу вільних адрес. Якщо сторінка перебувала в стані `DSM_PAGE_DIRTY_TWINNED`, її двійник негайно очищається.
- **`dsm_destroy`**: Скасовує реєстрацію обробника `SIGSEGV`, повертає системні обробники за замовчуванням, викликає `munmap()` для всіх виділених сторінок та пулів двійників.

## Протокол синхронізації та межі епох

Синхронізація у моделі узгодженості за звільненням (Release Consistency) реалізується через розподілені замки та глобальні бар'єри.

:::tabs
```c
/* Захоплення розподіленого замка: переводить змінені попередником сторінки в DSM_PAGE_INVALID */
dsm_status_t dsm_lock_acquire(uint32_t lock_id);

/* Відпускання замка: генерує Diff для всіх брудних сторінок, скидає права до PROT_READ */
dsm_status_t dsm_lock_release(uint32_t lock_id);

/* Глобальний бар'єр: взаємний обмін diff-пакетами та фіксація узгодженого стану */
dsm_status_t dsm_barrier(uint32_t barrier_id);
```
```cpp
class IDsmSynchronization {
public:
    virtual ~IDsmSynchronization() = default;
    virtual std::expected<void, DsmErrorCode> acquireLock(uint32_t lockId) noexcept = 0;
    virtual std::expected<void, DsmErrorCode> releaseLock(uint32_t lockId) noexcept = 0;
    virtual std::expected<void, DsmErrorCode> enterBarrier(uint32_t barrierId) noexcept = 0;
};
```
:::

Семантика та інваріанти операцій синхронізації:

- **Семантика `dsm_lock_acquire`**: Вузол блокується до отримання володіння замком `lock_id`. Разом із передачею прав на замок від попереднього власника отримується оновлений векторний годинник (Vector Clock). Усі сторінки, які були модифіковані в інтервалах, відомих замку, але ще не накладених на локальному вузлі, маркуються як `DSM_PAGE_INVALID` через системний виклик `mprotect(addr, PAGE_SIZE, PROT_NONE)`.
- **Семантика `dsm_lock_release`**: Вузол завершує епоху запису. Середовище сканує внутрішній список брудних сторінок, викликає `dsm_calc_diff` для кожної сторінки у стані `DSM_PAGE_DIRTY_TWINNED`, додає сформовані різниці до локального журналу епохи та відновлює стан `PROT_READ`. Права на замок разом із новим значенням векторного годинника передаються наступному вузлу.
- **Семантика `dsm_barrier`**: Зупиняє виконання всіх вузлів кластера. Кожен вузол генерує Diff для своїх локальних модифікацій та розсилає їх іншим учасникам бар'єра. Після отримання всіх пакетів кожен вузол послідовно застосовує зміни до своїх базових сторінок через `dsm_apply_diff`, скидає стан усіх спільних сторінок до `PROT_READ` і синхронно продовжує виконання.

## Операції низького рівня: генерація та накладання різниць

Низькорівневий інтерфейс дозволяє прямо взаємодіяти з рушієм обчислення відмінностей та маніпулювати двійниками сторінок безпосередньо.

:::tabs
```c
/* Обчислення різниці між сторінкою та двійником з формуванням бінарного пакета */
size_t dsm_calc_diff(const uint8_t *page_addr, const uint8_t *twin_addr, dsm_diff_packet_t *packet_out);

/* Накладання бінарного пакета різниці на локальну сторінку */
dsm_status_t dsm_apply_diff(uint8_t *target_page, const dsm_diff_packet_t *packet_in);

/* Консолідація сторінки: злиття накопиченого ланцюжка різниць у новий еталон */
dsm_status_t dsm_consolidate_page(uint32_t page_id);
```
```cpp
class IDsmDiffEngine {
public:
    virtual ~IDsmDiffEngine() = default;
    virtual size_t computeDiff(std::span<const std::byte, DsmPageSize> page,
                               std::span<const std::byte, DsmPageSize> twin,
                               DiffPacket& packetOut) noexcept = 0;
    virtual std::expected<void, DsmErrorCode> applyDiff(std::span<std::byte, DsmPageSize> targetPage,
                                                        const DiffPacket& packetIn) noexcept = 0;
    virtual std::expected<void, DsmErrorCode> consolidatePage(uint32_t pageId) noexcept = 0;
};
```
:::

Вимоги та інваріанти низькорівневих операцій:

- **Інваріант вирівнювання**: Вказівники `page_addr` та `twin_addr`, що передаються у `dsm_calc_diff`, зобов'язані бути вирівняні за межею 4096 байтів (`addr % DSM_PAGE_SIZE == 0`). Невирівняні вказівники призводять до повернення коду `DSM_ERR_INVALID_PARAM`.
- **Комутативність неперетинних дельт**: Якщо два пакети $D_1$ та $D_2$ містять зміни в неперетинних діапазонах байтів тієї самої сторінки, результат їх послідовного накладання є детермінованим та ідентичним незалежно від черговості виклику `dsm_apply_diff`.
- **Консолідація сторінки (`dsm_consolidate_page`)**: Застосовує всі накопичені за кілька епох пакети різниць безпосередньо до базового фрейму пам'яті, очищає чергу збережених Diff і створює новий монолітний еталон сторінки для оптимізації наступних мережних запитів.

## Безпека сигналів та багатониткові інваріанти

Обробка сигналів операційної системи накладає жорсткі обмеження на використання стандартних бібліотечних функцій (Async-Signal-Safe Invariants). Оскільки сигнал `SIGSEGV` може бути доставлений у будь-який момент виконання інструкцій потоку, всередині функції обробника діють такі правила:

1. **Заборона функцій динамічної пам'яті**: Виклики `malloc()`, `calloc()`, `free()` або `realloc()` суворо заборонені. Усі буфери двійників беруться виключно з попередньо виділеного пулу масиву `twin_pool`.
2. **Заборона функцій стандартного виводу**: Виклики `printf()`, `fprintf()` або `syslog()` заборонені, оскільки вони використовують внутрішні м'ютекси структур `FILE*`. Для діагностичного виводу повідомлень про фатальні збої використовується виключно системний виклик `write(STDERR_FILENO, ...)` ядра ОС.
3. **Прапорець `SA_NODEFER`**: Реєстрація сигналу виконується з прапорцем `SA_NODEFER`, що дозволяє рекурсивний вхід в обробник, якщо під час копіювання даних або обробки стану станеться вкладений збій на іншій сторінці пам'яті.

## Повний приклад використання інтерфейсу в додатку

Нижче наведено фрагмент коду паралельної обробки даних, де два незалежні вузли паралельно модифікують суміжні змінні всередині однієї сторінки, використовуючи наданий інтерфейс.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>

void execute_distributed_worker(uint32_t my_node_id) {
    dsm_config_t config = {
        .shared_heap_size = 1024 * 1024 * 16, /* 16 МБ */
        .node_id = my_node_id,
        .total_nodes = 2,
        .enable_simd_diff = true
    };

    if (dsm_init(&config) != DSM_SUCCESS) {
        fprintf(stderr, "Помилка ініціалізації середовища DSM\n");
        return;
    }

    /* Виділяємо спільний масив на 8192 байти (2 сторінки) */
    uint64_t *shared_data = (uint64_t*)dsm_alloc_shared(8192);
    if (!shared_data) {
        dsm_destroy();
        return;
    }

    /* Стартовий бар'єр синхронізації */
    dsm_barrier(0);

    /* Вузол 0 модифікує перше 64-бітне слово, Вузол 1 — десяте */
    if (my_node_id == 0) {
        dsm_lock_acquire(100);
        shared_data[0] = 0xDEADBEEFCAFEBABE;
        dsm_lock_release(100);
    } else if (my_node_id == 1) {
        dsm_lock_acquire(200);
        shared_data[10] = 0x0123456789ABCDEF;
        dsm_lock_release(200);
    }

    /* Фінальний бар'єр для злиття відмінностей */
    dsm_barrier(1);

    /* Обидва вузли гарантовано бачать коректні зміни сусіда */
    dsm_free_shared(shared_data);
    dsm_destroy();
}
```
```cpp
#include <iostream>
#include <cstdint>
#include <span>

void executeDistributedWorkerCpp(uint32_t myNodeId) {
    DsmEngineConfig config{
        .sharedHeapSize = 1024 * 1024 * 16,
        .nodeId = myNodeId,
        .totalNodes = 2,
        .enableSimdAcceleration = true
    };

    // Приклад виклику C++ обгортки середовища
    if (dsm_init(reinterpret_cast<const dsm_config_t*>(&config)) != DSM_SUCCESS) {
        std::cerr << "Не вдалося ініціалізувати середовище DSM\n";
        return;
    }

    auto* memoryBlock = static_cast<uint64_t*>(dsm_alloc_shared(8192));
    if (memoryBlock == nullptr) {
        dsm_destroy();
        return;
    }

    std::span<uint64_t> sharedArray{memoryBlock, 8192 / sizeof(uint64_t)};

    dsm_barrier(0);

    if (myNodeId == 0) {
        dsm_lock_acquire(100);
        sharedArray[0] = 0xDEADBEEFCAFEBABEULL;
        dsm_lock_release(100);
    } else if (myNodeId == 1) {
        dsm_lock_acquire(200);
        sharedArray[10] = 0x0123456789ABCDEFULL;
        dsm_lock_release(200);
    }

    dsm_barrier(1);

    dsm_free_shared(memoryBlock);
    dsm_destroy();
}
```
:::
