# ⚙️ Виявлення розривного читання у багатопотоковому середовищі

Коли спільна 64-розрядна змінна змінюється одним потоком і читається іншим без синхронізації або з порушенням природного вирівнювання в пам'яті, багатоядерна система розбиває передачу на окремі шинні транзакції. Читач замість цілісного значення отримує гібрид старого й нового станів — розривне читання (*torn read*).

## Постановка інженерної задачі

Потрібно створити стрес-тест, який на практиці провокує, фіксує та кількісно вимірює частоту розривного читання 64-розрядного числа між паралельними потоками на процесорі, а потім демонструє усунення дефекту за допомогою коректного вирівнювання та атомарних операцій.

Для надійної фіксації розриву використовується метод контрастних бітових масок. Письменник у циклі записує лише два спеціально підібрані взаємодоповнювальні 64-розрядні патерни:

```
Патерн A: 0x00000000_00000000ULL  (усі 64 біти скинуті в 0)
Патерн B: 0xFFFFFFFF_FFFFFFFFULL  (усі 64 біти встановлені в 1)
```

Якщо операція зчитування є неподільною (одинично атомарною), читач за будь-яких умов зобов'язаний побачити або `0x0000000000000000`, або `0xFFFFFFFFFFFFFFFF`. Будь-яке проміжне значення (наприклад, `0x00000000FFFFFFFF` або `0xFFFFFFFF00000000`) є беззаперечним доказом розривного читання: читач захопив молодшу половину одного запису та старшу половину іншого.

## Фізичні фактори виникнення розривів

Частота виявлення розривних станів залежить від чотирьох ключових апаратних чинників:

1. **Розташування відносно ліній кешу L1:** Якщо 64-розрядне число розташоване всередині однієї 64-байтової кеш-лінії, на сучасних 64-розрядних процесорах x86-64 та ARM64 доступ виконується однією мікрооперацією. Щоб гарантовано спровокувати розрив на 64-розрядній системі, цільову змінну штучно зміщують на 61 байт від початку вирівняного блоку пам'яті. Тоді перші 3 байти числа потрапляють у кінець Кеш-лінії N, а решта 5 байтів — на початок Кеш-лінії N+1.
2. **Прив'язка потоків до процесорних ядер (CPU Affinity):** Якщо потік-письменник і потік-читач виконуються на двох логічних потоках одного фізичного ядра (технології SMT або Hyper-Threading), вони спільно використовують спільний кеш даних L1D. Це збільшує ймовірність розриву в десятки разів, оскільки зміна стану кеш-лінії стає видимою миттєво без очікування міжядерних шинних повідомлень Invalidate. Якщо ж потоки рознесені на різні фізичні сокети NUMA, затримка міжядерної когерентності розширює часове вікно розриву між мікроопераціями.
3. **Асинхронний буфер запису (Store Buffer):** Перед тим як потрапити до кешу L1, дані потрапляють у буфер збереження ядра CPU. При невирівняному записі дві частини 64-бітного слова скидаються з буфера збереження у кеш окремими тактами, що створює фізичне вікно вразливості для паралельних читачів.
4. **Рівень оптимізації компілятора:** При компіляції з прапорцем `-O2` або `-O3` компілятор може зберегти читання в регістрі або розгорнути цикли, що змінює частоту фізичних звернень до кешу пам'яті.

## Реалізація стрес-тесту

Програма запускає потік-письменник на одному виділеному ядрі CPU та групу потоків-читачів на сусідніх ядрах. Утиліта збирає агреговану статистику пошкоджених звернень за фіксовану кількість ітерацій.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>
#include <inttypes.h>

#define ITERATIONS 100000000ULL

// Спеціально невирівняний буфер: зміщення 61 байт гарантує,
// що 8-байтне число перетинає межу 64-байтової кеш-лінії L1
typedef struct {
    char padding[61];
    uint64_t value;
} __attribute__((packed)) unaligned_payload_t;

typedef struct {
    unaligned_payload_t shared_data;
    volatile bool is_active;
    uint64_t total_torn_events;
} benchmark_env_t;

static benchmark_env_t g_env;

void *writer_thread(void *arg) {
    (void)arg;
    const uint64_t val_a = 0x0000000000000000ULL;
    const uint64_t val_b = 0xFFFFFFFFFFFFFFFFULL;

    for (uint64_t i = 0; i < ITERATIONS && g_env.is_active; ++i) {
        // Чергування запису двох патернів без атоміків над невирівняною пам'яттю
        g_env.shared_data.value = (i & 1) ? val_a : val_b;
    }
    g_env.is_active = false;
    return NULL;
}

void *reader_thread(void *arg) {
    (void)arg;
    const uint64_t val_a = 0x0000000000000000ULL;
    const uint64_t val_b = 0xFFFFFFFFFFFFFFFFULL;
    uint64_t local_torn = 0;

    while (g_env.is_active) {
        uint64_t sample = g_env.shared_data.value;
        // Якщо прочитано не 0 і не повну маску — це розривне читання!
        if (sample != val_a && sample != val_b) {
            local_torn++;
        }
    }

    __sync_fetch_and_add(&g_env.total_torn_events, local_torn);
    return NULL;
}

int main(void) {
    pthread_t writer;
    pthread_t readers[4];

    g_env.is_active = true;
    g_env.total_torn_events = 0;

    printf("Запуск стрес-тесту неатомарного доступу...\n");

    pthread_create(&writer, NULL, writer_thread, NULL);
    for (int i = 0; i < 4; ++i) {
        pthread_create(&readers[i], NULL, reader_thread, NULL);
    }

    pthread_join(writer, NULL);
    for (int i = 0; i < 4; ++i) {
        pthread_join(readers[i], NULL);
    }

    printf("Тест завершено. Виявлено розривних читань: %" PRIu64 "\n", g_env.total_torn_events);
    return 0;
}
```
```cpp
#include <iostream>
#include <thread>
#include <vector>
#include <atomic>
#include <cstdint>
#include <chrono>

struct alignas(64) StressHarness {
    // Навмисне невирівняне поле для провокації розриву кеш-лінії
    struct alignas(1) UnalignedSlot {
        char pad[61];
        uint64_t raw_value;
    } unaligned;

    // Альтернативне коректне атомарне поле для порівняння
    std::atomic<uint64_t> safe_value{0};
    std::atomic<bool> running{true};
    std::atomic<uint64_t> torn_reads_detected{0};
};

void run_writer(StressHarness& harness, uint64_t iterations) {
    constexpr uint64_t val_a = 0x0000000000000000ULL;
    constexpr uint64_t val_b = 0xFFFFFFFFFFFFFFFFULL;

    for (uint64_t i = 0; i < iterations && harness.running.load(std::memory_order_relaxed); ++i) {
        harness.unaligned.raw_value = (i & 1) ? val_a : val_b;
    }
    harness.running.store(false, std::memory_order_relaxed);
}

void run_reader(StressHarness& harness) {
    constexpr uint64_t val_a = 0x0000000000000000ULL;
    constexpr uint64_t val_b = 0xFFFFFFFFFFFFFFFFULL;
    uint64_t local_anomalies = 0;

    while (harness.running.load(std::memory_order_relaxed)) {
        uint64_t observed = harness.unaligned.raw_value;
        if (observed != val_a && observed != val_b) {
            local_anomalies++;
        }
    }

    harness.torn_reads_detected.fetch_add(local_anomalies, std::memory_order_relaxed);
}

int main() {
    StressHarness harness{};
    constexpr uint64_t test_iterations = 100'000'000ULL;
    constexpr size_t num_readers = 4;

    std::cout << "Запуск багатопотокового аналізу розривних звернень..." << std::endl;

    std::vector<std::jthread> reader_pool;
    reader_pool.reserve(num_readers);
    for (size_t i = 0; i < num_readers; ++i) {
        reader_pool.emplace_back(run_reader, std::ref(harness));
    }

    std::jthread writer(run_writer, std::ref(harness), test_iterations);
    writer.join();

    for (auto& reader : reader_pool) {
        reader.join();
    }

    std::cout << "Аналіз завершено. Кількість розривних станів: "
              << harness.torn_reads_detected.load() << std::endl;

    return 0;
}
```
:::

## Аналіз результатів та поведінки мікроархітектури

Під час виконання на процесорі Intel Core i7 або AMD Ryzen програма демонструє від кількох сотень до сотень тисяч випадків розривного читання.

Типовий аналіз захоплених аномальних значень у регістрах читача показує характерні бітові маски:

* `0x00000000FFFFFFFF` — читач захопив молодші 32 біти від запису `0xFFFFFFFFFFFFFFFF`, а старші 32 біти — від попереднього `0x0000000000000000`.
* `0xFFFFFFFF00000000` — читач захопив молодші 32 біти від запису `0x0000000000000000`, а старші — від `0xFFFFFFFFFFFFFFFF`.
* `0x000000FFFFFFFFFF` або `0xFFFFFF0000000000` — асиметричні розриви, зумовлені зсувом на 3 байти на межі 64-байтової кеш-лінії.

### Дизасемблерний аналіз та апаратні лічильники

Якщо переглянути машинний код неатомарного читання, компілятор генерує інструкцію `mov rax, [rdi+61]`. На апаратному рівні процесор розщеплює це звернення на дві окремі операції зчитування з кешу L1.

Під час профілювання утилітою `perf stat -e split_lock,cache-misses,L1-dcache-load-misses ./detector` на рівні ядра операційної системи фіксується сплеск апаратних лічильників продуктивності (*Performance Monitoring Unit*, PMU). Кожне розщеплене звернення призводить до простою конвеєра та додаткового навантаження на кільцеву шину когерентності.

Якщо скомпілювати цей самий тест із санітайзером потоків Clang/GCC (*ThreadSanitizer*, `-fsanitize=thread`), компілятор негайно перехопить несинхронізований паралельний доступ і видасть звіт про стан гонки даних (*data race on non-atomic memory*), зупинивши виконання ще до появи першого пошкодженого значення.

### Розриви у взаємодії з апаратним DMA

Аналогічний клас дефектів розривного читання виникає у вбудованих системах (*embedded*) під час взаємодії процесора з контролерами прямого доступу до пам'яті (*DMA*). Якщо периферійний модуль оновлює кільцевий буфер пакетами по 1 або 2 байти через шину AHB/APB, а ядро процесора зчитує 32-розрядне слово лічильника розміру буфера без попереднього скидання кешу або без використання прапорця завершення передачі (*Transfer Complete Interrupt*), процесор отримує розривне значення розміру буфера. Це призводить до обробки сміттєвих пакетів або падіння парсера протоколу.

### Усунення вади за допомогою атоміків

Якщо ми перемикаємося на використання коректно вирівняного атомарного поля:

```cpp
harness.safe_value.store(val, std::memory_order_relaxed);
uint64_t safe_sample = harness.safe_value.load(std::memory_order_relaxed);
```

Компілятор гарантує розміщення поля за адресою, кратною 8 байтам (`alignas(8)` або `alignas(64)` для повного запобігання помилковому розділенню кеш-ліній — *False Sharing*). Машинний код залишається тією самою одиночною інструкцією `mov`, але завдяки вирівнюванню вся операція виконується строго в межах однієї кеш-лінії L1. Протокол когерентності MESI гарантує, що жодне інше ядро не може спостерігати проміжний стан.

Кількість розривних станів при атомарному підході становить рівно **0**, а загальний час виконання циклу скорочується у 3–5 разів через ліквідацію апаратних затримок розщеплення кешу та шинних конфліктів.
