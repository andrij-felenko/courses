# ⚙️ Проект: Реалізація асинхронного рушія протитиску на основі кредитів та водяних знаків

У цьому проекті реалізовано повнофункціональний неблокуючий контролер потоку з кредитним вікном, механізмом водяних знаків (High/Low Watermark) та інтеграцією із подієвим циклом сокета для запобігання переповненню пам'яті в розподілених сервісах.

Коли вхідний мережевий потік перевищує швидкість обробки бізнес-логіки, наївний сервер накопичує повідомлення в пам'яті до аварійного завершення (`OOM`). Нижче наведено ядро зворотного зв'язку, яке при досягненні порогу High Watermark вимикає вичитування з мережевого сокета (змушуючи ядро активувати TCP ZeroWindow), а при падінні черги нижче Low Watermark — автоматично надсилає споживачеві нові кредити та відновлює прийом.

## Архітектура та принципи синхронізації

Контролер поєднує два скоординованих контури керування:
1. **Дискретний кредитний баланс (Credit Budget):** видача дозволів `request(n)` на відправку фіксованої кількості повідомлень, що обмежує максимальну кількість пакетів «у польоті» (in-flight);
2. **Водяні знаки черги (Queue Watermarks):** відстеження рівня заповнення локального кільцевого буфера з гістерезисом `HWM = 80%` та `LWM = 30%`.

### Синхронізаційні інваріанти:
* **Мережевий потік (Ingress / Event Loop):** ніколи не блокується на тривалий час. Якщо буфер досягає `High Watermark`, потік виконує легку операцію вимкнення інтересу `EPOLLIN` у системному мультиплексорі `epoll` та повертає керування;
* **Робочий потік (Worker / Business Logic):** вибирає завдання з буфера. Коли черга падає до `Low Watermark`, воркер ініціює відновлення реєстрації `EPOLLIN` та надсилає клієнту протокольний кадр поповнення кредитів (`WINDOW_UPDATE` / `REQUEST_N`);
* **Пам'ять:** фіксована місткість `BUFFER_CAPACITY` виділяється один раз під час ініціалізації, унеможливлюючи динамічну алокацію в гарячому тракті обробки.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <pthread.h>
#include <unistd.h>

#define BUFFER_CAPACITY 100
#define HIGH_WATERMARK  80
#define LOW_WATERMARK   30

typedef struct {
    int id;
    int payload_size;
} message_t;

typedef struct {
    message_t ring_buffer[BUFFER_CAPACITY];
    size_t head;
    size_t tail;
    size_t count;

    int32_t active_credits;
    bool is_socket_paused;

    pthread_mutex_t lock;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
} flow_controller_t;

void flow_controller_init(flow_controller_t *fc) {
    fc->head = 0;
    fc->tail = 0;
    fc->count = 0;
    fc->active_credits = 0;
    fc->is_socket_paused = false;

    pthread_mutex_init(&fc->lock, NULL);
    pthread_cond_init(&fc->not_empty, NULL);
    pthread_cond_init(&fc->not_full, NULL);
}

void flow_controller_destroy(flow_controller_t *fc) {
    pthread_mutex_destroy(&fc->lock);
    pthread_cond_destroy(&fc->not_empty);
    pthread_cond_destroy(&fc->not_full);
}

// Емуляція системного виклику керування сокетом (epoll_ctl EPOLLIN)
static void update_socket_epoll_state(bool enable_read) {
    if (enable_read) {
        printf("[SOCKET] Відновлено читання: EPOLL_CTL_MOD (EPOLLIN увімкнено) -> TCP Window > 0\n");
    } else {
        printf("[SOCKET] Пауза читання: EPOLL_CTL_MOD (EPOLLIN вимкнено) -> TCP ZeroWindow\n");
    }
}

// Додавання повідомлення, що надійшло з мережі
bool flow_controller_push_ingress(flow_controller_t *fc, message_t msg) {
    pthread_mutex_lock(&fc->lock);

    if (fc->count >= BUFFER_CAPACITY) {
        // Буфер переповнено через ігнорування протоколу відправником
        pthread_mutex_unlock(&fc->lock);
        return false;
    }

    fc->ring_buffer[fc->tail] = msg;
    fc->tail = (fc->tail + 1) % BUFFER_CAPACITY;
    fc->count++;

    if (fc->active_credits > 0) {
        fc->active_credits--;
    }

    // Перевірка досягнення High Watermark
    if (fc->count >= HIGH_WATERMARK && !fc->is_socket_paused) {
        fc->is_socket_paused = true;
        update_socket_epoll_state(false);
    }

    pthread_cond_signal(&fc->not_empty);
    pthread_mutex_unlock(&fc->lock);
    return true;
}

// Вибірка повідомлення робочим потоком бізнес-логіки
message_t flow_controller_pop_worker(flow_controller_t *fc) {
    pthread_mutex_lock(&fc->lock);

    while (fc->count == 0) {
        pthread_cond_wait(&fc->not_empty, &fc->lock);
    }

    message_t msg = fc->ring_buffer[fc->head];
    fc->head = (fc->head + 1) % BUFFER_CAPACITY;
    fc->count--;

    // Перевірка падіння черги нижче Low Watermark
    if (fc->count <= LOW_WATERMARK && fc->is_socket_paused) {
        fc->is_socket_paused = false;
        update_socket_epoll_state(true);

        // Поповнення кредитів відправника
        int32_t grant = (int32_t)(BUFFER_CAPACITY - fc->count);
        fc->active_credits += grant;
        printf("[CREDIT] Надіслано кадр REQUEST_N: +%d кредитів (доступно: %d)\n",
               grant, fc->active_credits);
    }

    pthread_cond_signal(&fc->not_full);
    pthread_mutex_unlock(&fc->lock);
    return msg;
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <mutex>
#include <condition_variable>
#include <optional>
#include <span>
#include <cstdint>

struct Message {
    uint32_t id{0};
    uint32_t payload_size{0};
};

class FlowController {
public:
    static constexpr size_t kCapacity = 100;
    static constexpr size_t kHighWatermark = 80;
    static constexpr size_t kLowWatermark = 30;

    explicit FlowController() = default;
    ~FlowController() = default;

    FlowController(const FlowController&) = delete;
    FlowController& operator=(const FlowController&) = delete;

    // Вхідний мережевий виклик від event-loop сокета
    [[nodiscard]] bool push_ingress(Message msg) {
        std::unique_lock<std::mutex> lock(mutex_);

        if (count_ >= kCapacity) {
            return false; // Захист від збійного клієнта
        }

        ring_buffer_[tail_] = msg;
        tail_ = (tail_ + 1) % kCapacity;
        ++count_;

        if (active_credits_ > 0) {
            --active_credits_;
        }

        if (count_ >= kHighWatermark && !socket_paused_) {
            socket_paused_ = true;
            update_epoll_registration(false);
        }

        cv_not_empty_.notify_one();
        return true;
    }

    // Вибірка повідомлення воркером бізнес-обробки
    [[nodiscard]] Message pop_worker() {
        std::unique_lock<std::mutex> lock(mutex_);

        cv_not_empty_.wait(lock, [this] { return count_ > 0; });

        Message msg = ring_buffer_[head_];
        head_ = (head_ + 1) % kCapacity;
        --count_;

        if (count_ <= kLowWatermark && socket_paused_) {
            socket_paused_ = false;
            update_epoll_registration(true);

            auto grant = static_cast<int32_t>(kCapacity - count_);
            active_credits_ += grant;
            std::cout << "[CREDIT] Видано новий кредит: +" << grant 
                      << " (активний ліміт: " << active_credits_ << ")\n";
        }

        cv_not_full_.notify_one();
        return msg;
    }

    [[nodiscard]] size_t current_depth() const noexcept {
        std::lock_guard<std::mutex> lock(mutex_);
        return count_;
    }

private:
    void update_epoll_registration(bool enable_read) const noexcept {
        if (enable_read) {
            std::cout << "[EPOLL] Увімкнено EPOLLIN (відновлення TCP Window)\n";
        } else {
            std::cout << "[EPOLL] Вимкнено EPOLLIN (активація TCP ZeroWindow)\n";
        }
    }

    mutable std::mutex mutex_;
    std::condition_variable cv_not_empty_;
    std::condition_variable cv_not_full_;

    std::vector<Message> ring_buffer_{std::vector<Message>(kCapacity)};
    size_t head_{0};
    size_t tail_{0};
    size_t count_{0};

    int32_t active_credits_{0};
    bool socket_paused_{false};
};
```
:::

## Покрокова динаміка обробки сплеску навантаження

1. **Нормальний стан (`count < 80`):** Мережевий потік вичитує сокет і додає повідомлення в буфер за `O(1)`. Воркер вичитує елементи і виконує обчислення. Сокет зареєстрований з `EPOLLIN`.
2. **Перетин High Watermark (`count == 80`):**
   * Мережевий потік бачить перетин порогу і викликає `update_epoll_registration(false)`.
   * Подієвий цикл вимикає `EPOLLIN`. Ядро Linux припиняє сповіщати процес про нові байти.
   * Пакети накопичуються в буфері сокета ядра `SO_RCVBUF`. Коли він заповнюється, ядро надсилає `TCP ZeroWindow`.
   * Відправник блокується на виклику `send()`.
3. **Робота воркерів під час паузи (`80 -> 30`):**
   * Поки сокет спить, воркери вичерпують накопичені 50 повідомлень із кільцевого буфера.
   * Пам'ять процесу стабілізована і не росте.
4. **Перетин Low Watermark (`count == 30`):**
   * Воркер фіксує досягнення `LWM` і викликає `update_epoll_registration(true)`.
   * Подієвий цикл знову слухає `EPOLLIN`. Ядро вичитує сокет і відкриває TCP-вікно.
   * Контролер надсилає відправнику кредитний кадр на `+70` повідомлень. Потік відновлюється.

## Оптимізація пам'яті: запобігання хибному розділенню кеш-ліній (False Sharing)

У багатопотокових системах з інтенсивним обміном повідомленнями покажчики голови (`head_`), хвоста (`tail_`) та лічильник активних кредитів (`active_credits_`) постійно модифікуються різними ядрами процесора (мережевим потоком та воркером).

Якщо ці змінні опиняються в межах одного 64-байтного кеш-рядка процесора (англ. *cache line*), ядра починають постійно інвалідувати кеш L1/L2 один одного за протоколом MESI/MOESI. Це явище, відоме як хибне розділення кешу (англ. *false sharing*), здатне сповільнити роботу кільцевого буфера в 10–50 разів.

### Правило вирівнювання кеш-ліній (C++20):

```cpp
// Розділення гарячих змінних на окремі кеш-лінії
struct alignas(64) IngressState {
    size_t tail{0};
    int32_t active_credits{0};
    bool socket_paused{false};
};

struct alignas(64) WorkerState {
    size_t head{0};
};
```

Використання атрибута `alignas(64)` або `alignas(std::hardware_destructive_interference_size)` гарантує, що модифікація покажчика хвоста мережевим потоком не блокує зчитування покажчика голови робочим потоком.

## Інструкція зі збірки та тестування

Для перевірки коректності роботи протитиску та відсутності гонок станів компіляцію слід виконувати з увімкненим санітайзером потоків (ThreadSanitizer):

:::tabs
```bash
# Збірка C-версії з ThreadSanitizer та оптимізацією
gcc -O2 -g -fsanitize=thread -pthread flow_controller.c -o flow_controller_c

# Запуск тесту під навантаженням
./flow_controller_c
```
```bash
# Збірка C++20 версії з максимальним рівнем попереджень
g++ -std=c++20 -O3 -Wall -Wextra -Wpedantic -pthread flow_controller.cpp -o flow_controller_cpp

# Запуск стрес-тесту
./flow_controller_cpp
```
:::

## Особливості інтеграції з ядром Linux: Edge-Triggered проти Level-Triggered

Під час підключення контролера потоку до реального подієвого циклу ядра Linux (`epoll`) критично важливо правильно обрати режим спрацьовування дескриптора сокета:

### 1. Рівневий режим (Level-Triggered, за замовчуванням):
* Поки сокет має байти в буфері ядра `SO_RCVBUF`, виклик `epoll_wait()` постійно повертає подію готовності до читання.
* Щоб зупинити виклики обробника, достатньо виконати `epoll_ctl(EPOLL_CTL_MOD)` з видаленням прапорця `EPOLLIN`.
* Після відновлення `EPOLLIN` ядро негайно знову згенерує подію, якщо в черзі сокета залишилися незчитані байти.

### 2. Граничний режим (Edge-Triggered, прапорець `EPOLLET`):
* Подія генерується ядром лише один раз у момент переходу відсутності даних до їх появи.
* Застосунок зобов'язаний вичитувати сокет у циклі `while (true)` до отримання помилки `EAGAIN` / `EWOULDBLOCK`.
* Якщо застосунок перериває читання на порозі `High Watermark` у режимі `EPOLLET`, ядро не згенерує нову подію автоматично після увімкнення `EPOLLIN`, якщо нові пакети не надійдуть з мережі. Тому в режимі `EPOLLET` відновлення читання вимагає обов'язкового примусового виклику `drain_socket_buffer()`.

---

## Пастки реалізації та крайові випадки

1. **Гонка станів між подієвим циклом та чергою:** Системний виклик відновлення читання сокета повинен виконуватися лише після того, як вивільнення слота буфера зафіксовано в пам'яті під блокуванням. Інакше мережевий потік може зчитати нові байти до того, як лічильник `count_` зменшиться.
2. **Втрата сигналу пробудження (Lost Wakeup):** Використання предикату `[this] { return count_ > 0; }` у `condition_variable::wait` захищає від фальшивих пробуджень (англ. *spurious wakeups*) ядра операційної системи.
3. **Захист від недобросовісного джерела:** Якщо клієнт ігнорує вичерпання кредитів і продовжує заливати сокет, метод `push_ingress()` повертає `false`, що є тригером для негайного розриву з'єднання (`RST` / `TCP close`).
4. **Уникнення інверсії пріоритетів:** М'ютекс утримується лише на час зміни індексів та перевірки порогів (кілька наносекунд). Будь-які важкі операції I/O або мережеві виклики виносяться за межі критичної секції.
5. **Атомарність поповнення кредитів:** У високонавантажених конвеєрах видача кредитів агрегується пачками (наприклад, по 16 або 32 дозволи), щоб уникнути надмірної кількості дрібних керуючих пакетів у мережі.



