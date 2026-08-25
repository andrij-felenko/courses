# 📋 Інтерфейс та серіалізація логічного годинника Лампорта

Цей документ містить специфікацію програмного інтерфейсу (API) логічного годинника Лампорта для високопродуктивних багатопотокових сервісів, вимоги до атомарних операцій і бар'єрів пам'яті на сучасних багатоядерних процесорах (x86-64 та ARM64), бінарні та текстові протоколи серіалізації для мережевих викликів (gRPC, HTTP/REST), шаблони реалізації мережевих перехоплювачів (interceptors), а також аналіз крайових випадків (переповнення, збереження стану при перезапуску, фальшиве розділення кеш-ліній).

## 1. Архітектурне призначення та семантика викликів

Логічний годинник є ключовим примітивом координації у розподілених сховищах, брокерах повідомлень та акторних моделях обчислень. Його завдання — присвоювати кожній локальній та мережевій дії монотонно зростаючу мітку часу, яка зберігає відношення причинності (happened-before).

У багатопотоковому середовищі вузла декілька робочих потоків одночасно генерують запити або обробляють вхідні мережеві пакети. Тому програмна реалізація годинника повинна забезпечувати:
1. **Потокобезпечність без блокувань** (англ. *lock-free / wait-free concurrency*): операції взяття мітки не повинні захоплювати м'ютекси операційної системи, що призвело б до деградації пропускної здатності на мільйонах операцій за секунду.
2. **Коректні бар'єри пам'яті** (англ. *memory ordering semantics*): запис локальних даних перед відправленням повідомлення повинен бути гарантовано зафіксований у пам'яті до того, як інший потік або вузол прочитає оновлений лічильник годинника.
3. **Захист від помилкового розділення кешу** (англ. *false sharing*): структура годинника повинна бути вирівняна за межею кеш-лінії процесора (типово 64 байти), щоб уникнути паразитної інвалідації кешу сусідніх ядер CPU.

:::tabs
```c
#ifndef LAMPORT_CLOCK_H
#define LAMPORT_CLOCK_H

#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Вирівнювання за розміром типової кеш-лінії L1/L2 (64 байти) для запобігання false sharing */
#define LAMPORT_CACHE_LINE_SIZE 64

/**
 * @brief Незмінний кортеж мітки часу Лампорта (значення лічильника + унікальний ID вузла).
 */
typedef struct {
    uint32_t node_id;
    uint64_t counter;
} lamport_timestamp_t;

/**
 * @brief Структура стану логічного годинника вузла.
 */
typedef struct {
    alignas(LAMPORT_CACHE_LINE_SIZE) _Atomic uint64_t counter;
    uint32_t node_id;
} lamport_clock_t;

/**
 * @brief Ініціалізує логічний годинник для конкретного вузла.
 * @param clock Вказівник на виділену пам'ять годинника.
 * @param node_id Унікальний числовий ідентифікатор вузла в кластері.
 * @param initial_counter Початкове значення лічильника (типово 0 або збережене значення після перезапуску).
 */
void lamport_clock_init(lamport_clock_t* clock, uint32_t node_id, uint64_t initial_counter);

/**
 * @brief Фіксує локальну подію: атомарно збільшує лічильник на 1 і повертає нову мітку.
 * @param clock Вказівник на годинник.
 * @return lamport_timestamp_t Присвоєна події мітка часу.
 */
lamport_timestamp_t lamport_clock_tick(lamport_clock_t* clock);

/**
 * @brief Формує мітку часу перед відправленням повідомлення в мережу.
 * @param clock Вказівник на годинник.
 * @return lamport_timestamp_t Мітка для розміщення в заголовку повідомлення.
 */
lamport_timestamp_t lamport_clock_send_event(lamport_clock_t* clock);

/**
 * @brief Оновлює стан годинника при отриманні вхідного мережевого повідомлення.
 *        Виконує lock-free цикл CAS (Compare-And-Swap): counter = max(current, incoming) + 1.
 * @param clock Вказівник на годинник.
 * @param incoming_counter Значення лічильника із заголовка отриманого повідомлення.
 * @return lamport_timestamp_t Мітка, присвоєна події отримання повідомлення.
 */
lamport_timestamp_t lamport_clock_recv_event(lamport_clock_t* clock, uint64_t incoming_counter);

/**
 * @brief Читає поточне значення годинника без його інкременту.
 * @param clock Вказівник на годинник.
 * @return uint64_t Поточний стан лічильника.
 */
uint64_t lamport_clock_read(const lamport_clock_t* clock);

/**
 * @brief Порівнює дві мітки у тотальному порядку за кортежем (counter, node_id).
 * @param a Перша мітка.
 * @param b Друга мітка.
 * @return int -1 якщо a < b; 0 якщо a == b; +1 якщо a > b.
 */
int lamport_timestamp_compare(lamport_timestamp_t a, lamport_timestamp_t b);

#ifdef __cplusplus
}
#endif

#endif /* LAMPORT_CLOCK_H */
```
```cpp
#pragma once

#include <cstdint>
#include <atomic>
#include <compare>
#include <new>
#include <string>
#include <string_view>
#include <expected>
#include <format>

namespace distributed {

#ifdef __cpp_lib_hardware_interference_size
using std::hardware_destructive_interference_size;
#else
constexpr size_t hardware_destructive_interference_size = 64;
#endif

/**
 * @brief Незмінний кортеж мітки часу Лампорта з підтримкою тристороннього порівняння C++20.
 */
struct LamportTimestamp {
    uint32_t node_id{0};
    uint64_t counter{0};

    [[nodiscard]] constexpr auto operator<=>(const LamportTimestamp& other) const noexcept {
        if (auto cmp = counter <=> other.counter; cmp != 0) return cmp;
        return node_id <=> other.node_id;
    }

    [[nodiscard]] constexpr bool operator==(const LamportTimestamp& other) const noexcept = default;

    [[nodiscard]] std::string to_header_string() const {
        return std::format("{}:{}", counter, node_id);
    }
};

/**
 * @brief Потокобезпечний логічний годинник Лампорта на базі атомарних операцій.
 */
class alignas(hardware_destructive_interference_size) LamportClock {
public:
    explicit LamportClock(uint32_t node_id, uint64_t initial_counter = 0) noexcept
        : node_id_(node_id), counter_(initial_counter) {}

    LamportClock(const LamportClock&) = delete;
    LamportClock& operator=(const LamportClock&) = delete;
    LamportClock(LamportClock&&) = delete;
    LamportClock& operator=(LamportClock&&) = delete;

    /**
     * @brief Фіксує локальну подію: виконує fetch_add(1) з семантикою acquire-release.
     */
    [[nodiscard]] LamportTimestamp tick() noexcept {
        const uint64_t next = counter_.fetch_add(1, std::memory_order_acq_rel) + 1;
        return LamportTimestamp{.node_id = node_id_, .counter = next};
    }

    /**
     * @brief Формує мітку для відправлення повідомлення.
     */
    [[nodiscard]] LamportTimestamp send_event() noexcept {
        return tick();
    }

    /**
     * @brief Оновлює лічильник за правилом max(current, incoming) + 1 через CAS-цикл.
     */
    [[nodiscard]] LamportTimestamp recv_event(uint64_t incoming_counter) noexcept {
        uint64_t current = counter_.load(std::memory_order_relaxed);
        uint64_t next = 0;
        do {
            next = (current > incoming_counter ? current : incoming_counter) + 1;
        } while (!counter_.compare_exchange_weak(
            current, next, std::memory_order_acq_rel, std::memory_order_relaxed));

        return LamportTimestamp{.node_id = node_id_, .counter = next};
    }

    [[nodiscard]] uint32_t node_id() const noexcept { return node_id_; }

    [[nodiscard]] uint64_t read_current() const noexcept {
        return counter_.load(std::memory_order_acquire);
    }

private:
    const uint32_t node_id_;
    std::atomic<uint64_t> counter_;
};

} // namespace distributed
```
:::

## 2. Семантика впорядкування пам'яті (Memory Ordering)

При реалізації багатопотокових розподілених систем використання коректних бар'єрів пам'яті є критично важливим для усунення перевпорядкування інструкцій компілятором і процесором:

1. **Операція `tick()` / `send_event()`**: використовує атомарний виклик `fetch_add(1, std::memory_order_acq_rel)`.
   - Бар'єр `release` гарантує: усі зміни даних у пам'яті (наприклад, підготовка тіла повідомлення, модифікація локальної структури), виконані потоком *до* взяття мітки часу, будуть повністю зафіксовані в когерентному стані кешів CPU до того, як мітка вирушить у мережу.
   - Бар'єр `acquire` гарантує: потік бачить усі попередні зміни лічильника, здійснені іншими потоками процесу.

2. **Операція `recv_event(incoming_counter)`**: використовує цикл неблокуючого оновлення `compare_exchange_weak` (CAS).
   - Успішна модифікація виконується з бар'єром `memory_order_acq_rel`, що гарантує причинну публікацію отриманого стану.
   - Невдала спроба CAS у разі конфлікту паралельних потоків використовує `memory_order_relaxed`, уникаючи надлишкових накладних витрат на синхронізацію шини пам'яті перед повторною ітерацією циклу.

На архітектурах x86-64 зі строгою моделлю пам'яті (TSO — Total Store Order) інструкція `LOCK XADD` апаратно реалізує повний бар'єр. Проте на архітектурах зі слабкою моделлю пам'яті (ARM64, RISC-V) відсутність явного `acq_rel` призведе до того, що процесор переставить читання корисного навантаження пакета раніше за оновлення годинника, спричинивши гонку даних.

## 3. Формати серіалізації та мережевий протокол (Wire Protocol)

Для передачі міток часу між вузлами через транспортні протоколи TCP, UDP або gRPC використовується два типи представлення: двійковий та текстовий.

### Бінарний формат (для бінарних протоколів та gRPC Metadata)

Двійковий заголовок передається у прямому порядку байтів мережі (Big-Endian / Network Byte Order):

| Зсув (байти) | Розмір (байти) | Тип даних | Назва поля | Опис |
| :--- | :--- | :--- | :--- | :--- |
| `0x00` | 8 | `uint64_t` (Big-Endian) | `LogicalCounter` | Значення лічильника Лампорта |
| `0x08` | 4 | `uint32_t` (Big-Endian) | `NodeIdentifier` | Унікальний числовий ID вузла відправника |
| `0x0C` | 4 | `uint32_t` | `Reserved/Flags` | Прапорці розширення (для гібридних годинників HLC) |

Загальний розмір бінарного заголовка становить рівно 16 байтів, що ідеально вирівнюється за 128-бітними регістрами SIMD.

### Текстовий формат (для HTTP / REST API Headers)

Для міжсервісної взаємодії через HTTP використовується стандартизований заголовок `X-Lamport-Clock`:

```http
X-Lamport-Clock: 1844674407370955161:42
```

Правила синтаксичного аналізу:
- Значення складається з двох десяткових чисел, розділених символом двокрапки `:`.
- Перше число — беззнакове 64-бітне ціле число (значення лічильника `counter`).
- Друге число — унікальний числовий або шістнадцятковий ідентифікатор вузла `node_id`.
- У разі відсутності заголовка або синтаксичної помилки (від'ємне число, некоректні символи) запит обробляється як локальна подія з присвоєнням нового локального лічильника `tick()`.

## 4. Патерн інтеграції через проміжне ПЗ (gRPC Interceptors)

У сучасних мікросервісних архітектурах ручне оновлення годинника в кожному обробнику призводить до дублювання коду та помилок людського фактора. Стандартним інженерним підходом є автоматична ін'єкція міток через мережеві перехоплювачі (middleware / interceptors):

1. **Клієнтський перехоплювач (Client Interceptor)**:
   - Перехоплює вихідний RPC-виклик до серіалізації корисного навантаження.
   - Викликає `clock.send_event()`.
   - Записує згенеровану мітку в бінарні метадані gRPC або HTTP-заголовок `X-Lamport-Clock`.

2. **Серверний перехоплювач (Server Interceptor)**:
   - Отримує запит до передачі у бізнес-логіку обробника.
   - Вилучає мітку `incoming_counter` із метаданих.
   - Викликає `clock.recv_event(incoming_counter)`.
   - Прив'язує отриману мітку до контексту поточного запиту (Thread-Local Context), роблячи її доступною для журналу аудиту та розподіленого трасування.

## 5. Аналіз складності та крайових випадків

| Операція | Часова складність | Використання пам'яті | Механізм синхронізації |
| :--- | :--- | :--- | :--- |
| `tick()` | `O(1)` | `0 B` | `fetch_add` (`acq_rel`) |
| `send_event()` | `O(1)` | `0 B` | `fetch_add` (`acq_rel`) |
| `recv_event(ts)` | `O(1)` амортизовано | `0 B` | Lock-free CAS loop (`compare_exchange_weak`) |
| `compare(a, b)` | `O(1)` | `0 B` | Лексикографічне порівняння кортежу `(counter, node_id)` |

### Крайові випадки інженерної експлуатації

1. **Захист від переповнення лічильника**:
   Використання 64-бітного беззнакового цілого числа (`uint64_t`) повністю знімає проблему переповнення:
   - Максимальне значення: `2^64 - 1 ≈ 1.844 · 10^19` тиків.
   - За екстремального навантаження 10 мільйонів операцій на секунду (10^7 op/s) лічильник працюватиме безперервно понад **58 000 років** до першого переповнення.
   - На противагу цьому, використання застарілих 32-бітних чисел (`uint32_t`) є неприпустимим, оскільки вони переповнюються всього за 7 хвилин за навантаження 10M op/s.

2. **Збереження стану при перезапуску вузла (Crash-Recovery)**:
   Якщо вузол аварійно перезавантажується, його лічильник у пам'яті скидається до нуля. Якщо вузол почне відлічувати мітки з нуля, він повторно згенерує вже використані в минулому мітки, що зруйнує тотальний порядок транзакцій. Для вирішення цієї проблеми застосовують два підходи:
   - **Періодичні чекпоїнти на диск**: кожні `K` тиків вузол записує на диск значення `counter + K` у журнал WAL (Write-Ahead Log) через `fsync`. Після перезапуску годинник ініціалізується останнім зафіксованим значенням з диска.
   - **Гібридні годинники (HLC)**: прив'язка до фізичного часу, де значення старшої частини лічильника завжди ініціалізується поточним системним часом `epoch_ms`, що гарантує зростання міток після будь-якого перезавантаження.

3. **Динамічне призначення ідентифікаторів вузлів (Node ID)**:
   У динамічних хмарних кластерах (Kubernetes, сервіси з автоскейлінгом) вузли постійно створюються та знищуються. Щоб уникнути колізій `node_id`, застосовують два механізми:
   - Призначення 32-бітного унікального ID через централізований координатор (etcd, Consul або Raft).
   - Генерація 128-бітного хешу UUID вузла, де лексикографічне порівняння здійснюється за повним бінарним масивом ідентифікатора.
