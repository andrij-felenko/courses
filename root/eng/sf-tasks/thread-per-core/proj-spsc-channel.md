# ⚙️ Неблокувальний між'ядерний канал SPSC на кільцевому буфері

В архітектурі Thread-per-core та Shared-Nothing ядра процесора не мають права безпосередньо читати чи змінювати пам'ять чужих шардіів. Уся між'ядерна взаємодія здійснюється через надсилання асинхронних повідомлень. Головним будівельним блоком цієї комунікації є неблокувальний кільцевий буфер типу **SPSC** (*Single-Producer Single-Consumer* — один виробник, один споживач).

### Інженерні вимоги до між'ядерного SPSC буфера

Для забезпечення максимальної продуктивності та надійності алгоритм черги повинен задовольняти шість суворих критеріїв:

1. **Повна відсутність м'ютексів та спін-замків:** Буфер не повинен містити блокувальних системних викликів або циклів очікування у ядрі. Якщо вхідна черга заповнена, функція відправки повертає помилку, дозволяючи потоку перемикнутися на виконання інших задач.
2. **Усунення хибного розділення (False Sharing):** Змінні `head` (індекс читання) та `tail` (індекс запису) повинні бути рознесені в різні 64-байтні кеш-лінії за допомогою специфікатора `alignas(64)`. Якщо цього не зробити, запис виробника у `tail` постійно скидатиме L1-кеш споживача, який читає `head`.
3. **Легковажні атомарні бар'єри (Acquire-Release):** Виробник публікує дані з семантикою `memory_order_release`, а споживач вичитує індекси з `memory_order_acquire`. Це гарантує коректне упорядкування доступу до пам'яті на процесорах зі слабкою моделлю пам'яті (ARM, POWER) без важких інструкцій `mfence` на x86.
4. **Підтримка пакетованих операцій (Batching):** Можливість надсилати та приймати групи повідомлень за одну атомарну операцію для амортизації витрат на синхронізацію кешів.
5. **Локальне кешування зустрічних індексів:** Збереження змінних `cached_head` у виробника та `cached_tail` у споживача зменшує кількість звернень до атомарних змінних на 95–99%.
6. **Степінь двійки для розміру буфера:** Використання місткості `2^k` дозволяє замінити повільну апаратну операцію ділення за модулем швидким побітовим логічним «І».

Коли виробник і споживач працюють на різних фізичних ядрах багатопроцесорної системи, правильне взаємне розташування структур даних у пам'яті має вирішальне значення. Будь-який спільний доступ до однієї кеш-лінії призводить до передачі прав власності на лінію через міжпроцесорну шину, знижуючи швидкість передачі даних.

### Повна реалізація SPSC кільцевого буфера та прив'язки до ядер

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <pthread.h>
#include <sched.h>
#include <string.h>

#define CACHELINE_SIZE 64
#define RING_CAPACITY 1024  /* Має бути степенем двійки */
#define RING_MASK (RING_CAPACITY - 1)

/* Структура повідомлення між ядрами */
typedef struct {
    uint32_t sender_core;
    uint32_t message_id;
    uint64_t payload;
} cross_core_msg_t;

/* Вирівняний SPSC кільцевий буфер */
typedef struct {
    /* Зона споживача: модифікується лише споживачем */
    alignas(CACHELINE_SIZE) _Atomic size_t head;
    alignas(CACHELINE_SIZE) size_t cached_tail; /* Локальний кеш хвоста для споживача */

    /* Зона виробника: модифікується лише виробником */
    alignas(CACHELINE_SIZE) _Atomic size_t tail;
    alignas(CACHELINE_SIZE) size_t cached_head; /* Локальний кеш голови для виробника */

    /* Буфер даних */
    alignas(CACHELINE_SIZE) cross_core_msg_t buffer[RING_CAPACITY];
} spsc_ring_t;

/* Ініціалізація кільцевого буфера */
void spsc_init(spsc_ring_t *ring) {
    atomic_init(&ring->head, 0);
    atomic_init(&ring->tail, 0);
    ring->cached_head = 0;
    ring->cached_tail = 0;
}

/* Відправка одного повідомлення (Producer Core) */
bool spsc_push(spsc_ring_t *ring, const cross_core_msg_t *msg) {
    size_t current_tail = atomic_load_explicit(&ring->tail, memory_order_relaxed);
    
    /* Перевірка вільного місця з використанням кешованої голови */
    if (current_tail - ring->cached_head >= RING_CAPACITY) {
        ring->cached_head = atomic_load_explicit(&ring->head, memory_order_acquire);
        if (current_tail - ring->cached_head >= RING_CAPACITY) {
            return false; /* Буфер переповнений */
        }
    }

    /* Запис даних у кільцевий слот */
    ring->buffer[current_tail & RING_MASK] = *msg;
    
    /* Публікація оновленого хвоста з бар'єром release */
    atomic_store_explicit(&ring->tail, current_tail + 1, memory_order_release);
    return true;
}

/* Пакетоване вилучення повідомлень (Consumer Core) */
size_t spsc_pop_batch(spsc_ring_t *ring, cross_core_msg_t *out_msgs, size_t max_count) {
    size_t current_head = atomic_load_explicit(&ring->head, memory_order_relaxed);

    /* Перевірка наявності даних з використанням кешованого хвоста */
    if (current_head == ring->cached_tail) {
        ring->cached_tail = atomic_load_explicit(&ring->tail, memory_order_acquire);
        if (current_head == ring->cached_tail) {
            return 0; /* Буфер порожній */
        }
    }

    size_t available = ring->cached_tail - current_head;
    size_t to_read = (available < max_count) ? available : max_count;

    for (size_t i = 0; i < to_read; ++i) {
        out_msgs[i] = ring->buffer[(current_head + i) & RING_MASK];
    }

    /* Оновлення голови з бар'єром release для сповіщення виробника */
    atomic_store_explicit(&ring->head, current_head + to_read, memory_order_release);
    return to_read;
}

/* Прив'язка поточного потоку до фізичного ядра CPU */
bool pin_thread_to_core(int core_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    pthread_t current_thread = pthread_self();
    return pthread_setaffinity_np(current_thread, sizeof(cpu_set_t), &cpuset) == 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <atomic>
#include <span>
#include <memory>
#include <thread>
#include <cstdint>
#include <stdexcept>
#include <pthread.h>
#include <sched.h>

namespace tpc {

constexpr size_t CACHELINE_SIZE = 64;

struct CrossCoreMessage {
    uint32_t sender_core{0};
    uint32_t message_id{0};
    uint64_t payload{0};
};

template <typename T, size_t Capacity>
requires ((Capacity & (Capacity - 1)) == 0) // Ємність має бути степенем двійки
class alignas(CACHELINE_SIZE) SpscRingBuffer {
public:
    SpscRingBuffer() noexcept 
        : head_{0}, cached_tail_{0}, tail_{0}, cached_head_{0} {}

    // Заборона копіювання та переміщення для захисту прив'язки пам'яті
    SpscRingBuffer(const SpscRingBuffer&) = delete;
    SpscRingBuffer& operator=(const SpscRingBuffer&) = delete;

    [[nodiscard]] bool push(const T& item) noexcept {
        const size_t current_tail = tail_.load(std::memory_order_relaxed);

        if (current_tail - cached_head_ >= Capacity) {
            cached_head_ = head_.load(std::memory_order_acquire);
            if (current_tail - cached_head_ >= Capacity) {
                return false; // Буфер переповнений
            }
        }

        buffer_[current_tail & Mask] = item;
        tail_.store(current_tail + 1, std::memory_order_release);
        return true;
    }

    [[nodiscard]] size_t pop_batch(std::span<T> out_items) noexcept {
        const size_t current_head = head_.load(std::memory_order_relaxed);

        if (current_head == cached_tail_) {
            cached_tail_ = tail_.load(std::memory_order_acquire);
            if (current_head == cached_tail_) {
                return 0; // Немає доступних елементів
            }
        }

        const size_t available = cached_tail_ - current_head;
        const size_t to_read = std::min(available, out_items.size());

        for (size_t i = 0; i < to_read; ++i) {
            out_items[i] = buffer_[(current_head + i) & Mask];
        }

        head_.store(current_head + to_read, std::memory_order_release);
        return to_read;
    }

private:
    static constexpr size_t Mask = Capacity - 1;

    // Зона споживача (окрема кеш-лінія)
    alignas(CACHELINE_SIZE) std::atomic<size_t> head_;
    alignas(CACHELINE_SIZE) size_t cached_tail_;

    // Зона виробника (окрема кеш-лінія)
    alignas(CACHELINE_SIZE) std::atomic<size_t> tail_;
    alignas(CACHELINE_SIZE) size_t cached_head_;

    // Буфер елементів
    alignas(CACHELINE_SIZE) std::array<T, Capacity> buffer_{};
};

// RAII обгортка фіксації потоку на фізичному ядрі
class ScopedCorePinning {
public:
    explicit ScopedCorePinning(int core_id) {
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(core_id, &cpuset);
        const int rc = pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
        if (rc != 0) {
            throw std::runtime_error("Не вдалося зафіксувати потік на ядрі");
        }
    }
};

} // namespace tpc
```
:::

### Покроковий розбір алгоритму та мікроархітектурних пасток

1. **Кешування індексів (`cached_head` та `cached_tail`):** Якщо виробник перед кожним записом вичитуватиме атомарний `head_` споживача, лінія кешу споживача постійно інвалідуватиметься. Збереження локальної змінної `cached_head_` дозволяє виробнику виконувати сотні операцій запису без звернення до пам'яті споживача, доки різниця `current_tail - cached_head_` не перевищить місткість буфера. Лише тоді виробник виконує один атомарний виклик `head_.load(memory_order_acquire)`.
2. **Розділення пам'яті за кеш-лініями (`alignas(64)`):** Без специфікатора вирівнювання змінні `head_` та `tail_` опиняються в одній 64-байтній кеш-лінії. Щоразу, коли виробник змінює `tail_`, протокол MESI переводить цю лінію в кеші споживача у стан Invalid. Коли споживач оновлює `head_`, він у свою чергу інвалідує кеш виробника. Програма перетворюється на нескінченний ping-pong кеш-ліній, знижуючи швидкість у 20–50 разів.
3. **Семантика пам'яті (Memory Ordering):** Виробник записує корисні дані у слот масиву перед оновленням покажчика `tail_`. Використання `std::memory_order_release` для запису `tail_` та `std::memory_order_acquire` для читання `tail_` створює відношення синхронізації (*synchronizes-with*). Це гарантує, що споживач побачить повністю записані дані повідомлення, коли прочитає оновлений індекс `tail_`.
4. **Бітове маскування замість оператора `%`:** Завдяки вимозі степеня двійки для місткості `Capacity`, обчислення індексу в кільці виконується швидкою бітовою операцією `index & (Capacity - 1)`, яка займає 1 такт CPU проти 15–40 тактів для апаратної інструкції ділення `div`.
5. **Захист від переповнення індексів `size_t`:** Індекси `head_` та `tail_` не обмежуються діапазоном `0..Capacity-1`, а монотонно зростають від нуля до `2^64 - 1`. Математична коректність різниці `current_tail - cached_head_` зберігається навіть при переході через максимальне значення `size_t` завдяки стандартизованій арифметиці модульного переповнення беззнакових цілих типів у мовах C та C++.
6. **Апаратне попереднє завантаження (Hardware Prefetching):** Оскільки елементи вичитуються з кільцевого буфера послідовно через індекси `(current_head + i) & Mask`, апаратний префетчер процесора (L1 Stream Prefetcher) автоматично підтягує наступні кеш-лінії буфера в кеш до моменту фактичного звернення інструкцій процесора. Це забезпечує практично 100% потраплянь у кеш під час пакетованої обробки.
7. **Відмінність від багатопотокових MPMC-черг:** Багатопотокові черги з кількома виробниками та споживачами (MPMC) змушені використовувати атомарні цикли оновлення CAS (`compare_exchange`), які при високій конкуренції зазнають постійних колізій та перезапусків. У структурі SPSC кожен індекс змінюється лише одним унікальним ядром, що робить операції оновлення безумовними та повністю детермінованими.
8. **Робота буферів відкладеного запису процесора:** На архітектурах x86-64 операції запису спочатку потрапляють у внутрішній буфер запису процесора (*store buffer*). Використання бар'єра `release` забезпечує, що всі попередні записи в масив повідомлень будуть скинуті в L1D-кеш ядра до того, як оновлене значення покажчика `tail` стане доступним іншим процесорним ядрам через механізм когерентності шини. На процесорах ARMv8 компілятор транслює виклик у спеціальну апаратну інструкцію `stlr` (*Store-Release Register*), яка виключає потребу в дорогих глобальних бар'єрах пам'яті.

На практиці такий буфер забезпечує пропускну здатність понад 50 мільйонів повідомлень на секунду між двома сусідніми ядрами процесора із середньою затримкою передачі менше 20 наносекунд. Це дозволяє організувати ефективний обмін повідомленнями без деградації системи на багатоядерних серверах.
