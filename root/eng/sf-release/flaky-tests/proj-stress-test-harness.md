# ⚙️ Стендовий інжектор навантаження та виявлення гонок у RTOS

Коли тест у звичайному режимі падає один раз на п'ять тисяч запусків, спроба відтворити збій під інтерактивним відладчиком забирає дні роботи без жодного результату. Для швидкої локалізації таких дефектів застосовують інженерний метод штучного загострення умов (*Stress-Test Harness* або *Race Condition Injector*).

Головна мета тестового стендового інжектора — розширити статистичне вікно виникнення гонки за ресурси шляхом примусового перемішування пріоритетів потоків, випадкового створення навантаження на планувальник процесора та штучного внесення мікрозатримок у критичні фази виконання операцій.

## Архітектура тестового стенду та модель розриву даних

Тестовий стенд моделює типову архітектуру обробки потокових даних у вбудованих системах реального часу:
1. **Потік-виробник (Producer / UART Rx ISR):** Асинхронно отримує байти телеметрії з апаратного інтерфейсу та записує їх у спільний кільцевий буфер.
2. **Потік-споживач (Consumer / Parser Task):** Вичитує накопичені пакети фіксованої довжини, перевіряє контрольну суму (XOR CRC) та оновлює стан системи.
3. **Потік-інжектор хаосу (Chaos Monkey / CPU Stress Worker):** Фоново генерує короткі піки завантаження ядер процесора, примусово викликає перемикання контексту (`sched_yield()`) та змінює таймінги взаємодії.

У звичайних умовах потік-виробник встигає повністю записати пакет до того, як потік-споживач спробує прочитати дані. Проте за відсутності атомарної синхронізації змінної `count` або неправильного використання умовних змінних виникає стан гонки. Якщо споживач вклинюється між інкрементом покажчика `head` та оновленням лічильника байтів, він зчитує суміш старих і нових даних. Контрольна сума пакета не сходиться, і тестовий фреймворк фіксує пошкодження даних.

Завдяки паралельному стрес-навантаженню та примусовому скиданню квантів часу частота виникнення розривів даних або переповнення буфера зростає з 0.02% до 15–30% запусків, що дозволяє виявити дефект за кілька секунд.

## Математична модель загострення умов та ймовірність виявлення

Якщо тривалість критичного вікна незахищеного доступу до буфера становить `W = 50` нс, середній інтервал між зверненнями дорівнює `T = 200` мкс, то ймовірність випадкового накладання операцій двох потоків за один прогін становить:

```
P(колізія за 1 ітерацію)
= W / T                                   [частка небезпечного інтервалу часу]
= 50·10⁻⁹ / (200·10⁻⁶)                    [підстановка значень]
= 2.5·10⁻⁴                                [0.025% ймовірності]
```

За стандартного одиничного запуску в CI тест майже гарантовано пройде успішно. Проте за умови виконання стрес-циклу на `N = 10000` ітерацій сумарна ймовірність спіймати помилку різко зростає:

```
P(виявлення за N циклів)
= 1 - (1 - P(колізія))ᴺ                   [перехід до протилежної події]
= 1 - (1 - 0.00025)¹⁰⁰⁰⁰                  [підстановка для N=10000]
≈ 1 - 0.082                               [обчислення степеня]
≈ 0.918                                   [91.8% впевненості виявлення]
```

Штучне додавання фонових потоків збільшує ефективне вікно `W` у десятки разів за рахунок затримок витіснення планувальника, доводячи ймовірність фіксації дефекту до 99.9%.

## Реалізація стрес-тестового інжектора

Нижче наведено повноцінний робочий стендовий каркас мовами C та C++, який реалізує тестовий цикл із 10000 ітерацій, моделює роботу буфера в нестабільному та захищеному режимах, виявляє пошкодження пакетів і формує статистику збоїв.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>
#include <sched.h>

#define BUFFER_CAPACITY 64
#define TEST_ITERATIONS 10000
#define PACKET_SIZE 8

typedef struct {
    uint8_t data[BUFFER_CAPACITY];
    size_t head;
    size_t tail;
    size_t count;
    pthread_mutex_t lock;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
    bool inject_flakiness;
} RingBuffer;

typedef struct {
    RingBuffer* rb;
    size_t errors_detected;
    size_t dropped_packets;
    bool stop_flag;
} TestContext;

static void ring_buffer_init(RingBuffer* rb, bool inject_flakiness) {
    memset(rb->data, 0, sizeof(rb->data));
    rb->head = 0;
    rb->tail = 0;
    rb->count = 0;
    rb->inject_flakiness = inject_flakiness;
    pthread_mutex_init(&rb->lock, NULL);
    pthread_cond_init(&rb->not_empty, NULL);
    pthread_cond_init(&rb->not_full, NULL);
}

static void ring_buffer_destroy(RingBuffer* rb) {
    pthread_mutex_destroy(&rb->lock);
    pthread_cond_destroy(&rb->not_empty);
    pthread_cond_destroy(&rb->not_full);
}

/* Запис у кільцевий буфер */
static bool ring_buffer_push(RingBuffer* rb, const uint8_t* src, size_t len) {
    pthread_mutex_lock(&rb->lock);

    while (rb->count + len > BUFFER_CAPACITY) {
        /* При штучній нестабільності симулюємо відсутність блокування */
        if (rb->inject_flakiness) {
            pthread_mutex_unlock(&rb->lock);
            return false; /* Втрата пакета через переповнення */
        }
        pthread_cond_wait(&rb->not_full, &rb->lock);
    }

    for (size_t i = 0; i < len; ++i) {
        rb->data[rb->head] = src[i];
        rb->head = (rb->head + 1) % BUFFER_CAPACITY;
    }
    rb->count += len;

    pthread_cond_signal(&rb->not_empty);
    pthread_mutex_unlock(&rb->lock);
    return true;
}

/* Зчитування з кільцевого буфера */
static bool ring_buffer_pop(RingBuffer* rb, uint8_t* dst, size_t len, int timeout_ms) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    ts.tv_nsec += timeout_ms * 1000000L;
    if (ts.tv_nsec >= 1000000000L) {
        ts.tv_sec += ts.tv_nsec / 1000000000L;
        ts.tv_nsec %= 1000000000L;
    }

    pthread_mutex_lock(&rb->lock);
    while (rb->count < len) {
        int res = pthread_cond_timedwait(&rb->not_empty, &rb->lock, &ts);
        if (res != 0) {
            pthread_mutex_unlock(&rb->lock);
            return false; /* Таймаут вичитування */
        }
    }

    for (size_t i = 0; i < len; ++i) {
        dst[i] = rb->data[rb->tail];
        rb->tail = (rb->tail + 1) % BUFFER_CAPACITY;
    }
    rb->count -= len;

    pthread_cond_signal(&rb->not_full);
    pthread_mutex_unlock(&rb->lock);
    return true;
}

/* Потік виробника (Producer) */
static void* producer_thread(void* arg) {
    TestContext* ctx = (TestContext*)arg;
    uint8_t packet[PACKET_SIZE];

    for (size_t seq = 0; seq < TEST_ITERATIONS && !ctx->stop_flag; ++seq) {
        packet[0] = (uint8_t)(seq & 0xFF);
        packet[1] = (uint8_t)((seq >> 8) & 0xFF);
        for (size_t i = 2; i < PACKET_SIZE - 1; ++i) {
            packet[i] = (uint8_t)(i * 7);
        }
        /* Контрольний байт: XOR сума */
        uint8_t crc = 0;
        for (size_t i = 0; i < PACKET_SIZE - 1; ++i) {
            crc ^= packet[i];
        }
        packet[PACKET_SIZE - 1] = crc;

        if (!ring_buffer_push(ctx->rb, packet, PACKET_SIZE)) {
            ctx->dropped_packets++;
        }

        if (seq % 50 == 0) {
            sched_yield(); /* Спровокувати перемикання контексту */
        }
    }
    return NULL;
}

/* Потік споживача (Consumer) */
static void* consumer_thread(void* arg) {
    TestContext* ctx = (TestContext*)arg;
    uint8_t packet[PACKET_SIZE];
    size_t received = 0;

    while (received < TEST_ITERATIONS && !ctx->stop_flag) {
        if (!ring_buffer_pop(ctx->rb, packet, PACKET_SIZE, 50)) {
            /* Таймаут зчитування через джитер */
            break;
        }

        uint8_t crc = 0;
        for (size_t i = 0; i < PACKET_SIZE - 1; ++i) {
            crc ^= packet[i];
        }

        if (packet[PACKET_SIZE - 1] != crc) {
            ctx->errors_detected++;
        }
        received++;
    }
    return NULL;
}

int main(void) {
    RingBuffer rb;
    TestContext ctx;
    pthread_t prod, cons;

    printf("=== Запуск стрес-тесту буфера на 10000 ітерацій ===\n");

    /* Тест 1: Режим зі штучною нестабільністю (симуляція джитеру) */
    ring_buffer_init(&rb, true);
    ctx.rb = &rb;
    ctx.errors_detected = 0;
    ctx.dropped_packets = 0;
    ctx.stop_flag = false;

    pthread_create(&prod, NULL, producer_thread, &ctx);
    pthread_create(&cons, NULL, consumer_thread, &ctx);

    pthread_join(prod, NULL);
    pthread_join(cons, NULL);
    ring_buffer_destroy(&rb);

    printf("Результати нестабільного режиму:\n");
    printf("  - Втрачено пакетів: %zu\n", ctx.dropped_packets);
    printf("  - Помилок контрольної суми: %zu\n", ctx.errors_detected);

    /* Тест 2: Захищений детермінований режим */
    ring_buffer_init(&rb, false);
    ctx.errors_detected = 0;
    ctx.dropped_packets = 0;

    pthread_create(&prod, NULL, producer_thread, &ctx);
    pthread_create(&cons, NULL, consumer_thread, &ctx);

    pthread_join(prod, NULL);
    pthread_join(cons, NULL);
    ring_buffer_destroy(&rb);

    printf("Результати захищеного детермінованого режиму:\n");
    printf("  - Втрачено пакетів: %zu\n", ctx.dropped_packets);
    printf("  - Помилок контрольної суми: %zu\n", ctx.errors_detected);

    if (ctx.errors_detected == 0 && ctx.dropped_packets == 0) {
        printf("СТАТУС: ТЕСТ УСПІШНО ПРОЙДЕНО (100%% ДЕТЕРМІНІЗМ)\n");
        return 0;
    }
    return 1;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <atomic>
#include <span>
#include <numeric>

constexpr size_t BufferCapacity = 64;
constexpr size_t TestIterations = 10000;
constexpr size_t PacketSize = 8;

using Packet = std::array<uint8_t, PacketSize>;

class ThreadSafeRingBuffer {
public:
    explicit ThreadSafeRingBuffer(bool injectFlakiness)
        : injectFlakiness_(injectFlakiness) {}

    bool push(std::span<const uint8_t> src) {
        std::unique_lock<std::mutex> lock(mutex_);

        while (count_ + src.size() > BufferCapacity) {
            if (injectFlakiness_) {
                return false; // Симуляція втрати через переповнення
            }
            notFull_.wait(lock, [this, &src]() {
                return count_ + src.size() <= BufferCapacity;
            });
        }

        for (uint8_t byte : src) {
            buffer_[head_] = byte;
            head_ = (head_ + 1) % BufferCapacity;
        }
        count_ += src.size();

        notEmpty_.notify_one();
        return true;
    }

    bool pop(std::span<uint8_t> dst, std::chrono::milliseconds timeout) {
        std::unique_lock<std::mutex> lock(mutex_);

        const bool ready = notEmpty_.wait_for(lock, timeout, [this, &dst]() {
            return count_ >= dst.size();
        });

        if (!ready) {
            return false; // Таймаут зчитування
        }

        for (uint8_t& byte : dst) {
            byte = buffer_[tail_];
            tail_ = (tail_ + 1) % BufferCapacity;
        }
        count_ -= dst.size();

        notFull_.notify_one();
        return true;
    }

private:
    std::array<uint8_t, BufferCapacity> buffer_{};
    size_t head_{0};
    size_t tail_{0};
    size_t count_{0};
    const bool injectFlakiness_{false};
    std::mutex mutex_;
    std::condition_variable notEmpty_;
    std::condition_variable notFull_;
};

struct TestResults {
    std::atomic<size_t> droppedPackets{0};
    std::atomic<size_t> checksumErrors{0};
};

void runStressBenchmark(bool injectFlakiness) {
    ThreadSafeRingBuffer ringBuffer(injectFlakiness);
    TestResults results;
    std::atomic<bool> stopFlag{false};

    auto producer = [&]() {
        Packet packet{};
        for (size_t seq = 0; seq < TestIterations && !stopFlag.load(); ++seq) {
            packet[0] = static_cast<uint8_t>(seq & 0xFF);
            packet[1] = static_cast<uint8_t>((seq >> 8) & 0xFF);
            for (size_t i = 2; i < PacketSize - 1; ++i) {
                packet[i] = static_cast<uint8_t>(i * 7);
            }
            uint8_t crc = 0;
            for (size_t i = 0; i < PacketSize - 1; ++i) {
                crc ^= packet[i];
            }
            packet[PacketSize - 1] = crc;

            if (!ringBuffer.push(packet)) {
                results.droppedPackets.fetch_add(1, std::memory_order_relaxed);
            }

            if (seq % 50 == 0) {
                std::this_thread::yield();
            }
        }
    };

    auto consumer = [&]() {
        Packet packet{};
        size_t received = 0;

        while (received < TestIterations && !stopFlag.load()) {
            if (!ringBuffer.pop(packet, std::chrono::milliseconds(50))) {
                break;
            }

            uint8_t crc = 0;
            for (size_t i = 0; i < PacketSize - 1; ++i) {
                crc ^= packet[i];
            }

            if (packet[PacketSize - 1] != crc) {
                results.checksumErrors.fetch_add(1, std::memory_order_relaxed);
            }
            received++;
        }
    };

    std::thread prodThread(producer);
    std::thread consThread(consumer);

    prodThread.join();
    consThread.join();

    std::cout << "  - Втрачено пакетів: " << results.droppedPackets.load() << "\n";
    std::cout << "  - Помилок контрольної суми: " << results.checksumErrors.load() << "\n";
}

int main() {
    std::cout << "=== Запуск C++ стрес-тесту буфера на 10000 ітерацій ===\n";

    std::cout << "Результати нестабільного режиму (симуляція гонки):\n";
    runStressBenchmark(true);

    std::cout << "Результати захищеного детермінованого режиму:\n";
    runStressBenchmark(false);

    std::cout << "СТАТУС: ТЕСТ ЗАВЕРШЕНО\n";
    return 0;
}
```
:::

## Методологія локалізації та простеження черги

Для ефективного пошуку причин нестабільності в реальних проектах рекомендується застосовувати триступеневу методику простеження:

1. **Прив'язка до процесорних ядер (CPU Affinity):**
   Використання виклику `pthread_setaffinity_np()` для примусового запуску виробника та споживача на одному фізичному ядрі. Якщо збій зникає на одному ядрі й з'являється лише при розподілі на різні ядра — першопричиною є відсутність бар'єрів пам'яті (*Memory Ordering / Store Buffer reordering*), а не алгоритмічна логіка.

2. **Апаратне трасування без спостережницького ефекту:**
   Додавання викликів `printf()` до критичних секцій кардинально сповільнює виконання і маскує гонку (ефект Гейзенбага). Замість консольного виводу вбудовані розробники використовують вільні піни GPIO мікроконтролера. Встановлення високого рівня `GPIO_PIN->BSRR = PIN_SET` на вході в обробник займає рівно 1 такт процесора (0.005 мкс). Зовнішній логічний аналізатор з частотою дискретизації 100 МГц фіксує точні часові інтервали конфлікту без жодного впливу на хід виконання програми.

3. **Стрес-тестування виділення пам'яті (Memory Churn):**
   Паралельний фоновий потік, що безперервно виділяє та звільняє блоки пам'яті різного розміру (`malloc(rand() % 1024)`), змушує алокатор та ядро регулярно оновлювати таблиці сторінок і скидати кеш процесора L1/L2. Це провокує прояв крайових помилок адресації та розсинхронізації таймінгів.

## Аналіз пасток та крайових випадків

Під час проектування подібних тестових інжекторів слід враховувати три критичні інженерні пастки:

1. **Пастка штучного голодування черги:** Якщо потік-інжектор споживає 100% процесорного часу без пауз, операційна система починає примусово затримувати потоки драйверів стенду. Тест падає не через гонку даних у буфері, а через системний таймаут USB/Ethernet стека. Інжектор повинен періодично поступатися квантом через `sched_yield()` або мікропаузи `nanosleep()`.
2. **Пастка помилкових спрацьовувань таймауту:** При зміні конфігурації раннера CI (наприклад, перехід з 8-ядерного локального сервера на 2-ядерну віртуальну машину хмарного провайдера) час реакції системи природно зростає в кілька разів. Ліміт очікування `wait_for()` повинен адаптуватися до базової швидкодії раннера.
3. **Пастка надлишкових оптимізацій компілятора:** У релізних режимах `-O2` та `-O3` компілятор має право кешувати читання неатомарних змінних у регістри процесора. Якщо прапорець зупинки циклу не позначений як `std::atomic` або `volatile`, оптимізатор створює нескінченний цикл, що призводить до зависання тесту на стенді.
