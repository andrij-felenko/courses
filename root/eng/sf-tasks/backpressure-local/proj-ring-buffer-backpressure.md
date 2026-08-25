# ⚙️ Кільцевий буфер із гістерезисом та блокуючим протитиском

Коли два системні потоки взаємодіють через спільну чергу, наївна реалізація на базі динамічного списку призводить або до неконтрольованого зростання пам'яті (OOM), або до постійного виділення та звільнення пам'яті на купі (`malloc`/`free`), що фрагментує адресний простір і руйнує локальність кешу процесора. Промисловим стандартом організації локального протитиску є **кільцевий буфер фіксованого розміру** (*bounded ring buffer*) із підтримкою гістерезисних водяних знаків (High / Low Watermark).

### Архітектура та інваріанти структури

Буфер базується на статичному масиві ємністю `Capacity`, яка дорівнює степеню двійки (`Capacity = 2ᵏ`). Це дозволяє замінити повільну операцію взяття залишку від ділення (`index % Capacity`) на швидку побітову маску (`index & (Capacity - 1)`).

Для синхронізації та протитиску використовуються такі інваріанти:
1. **Лічильники позицій:**
   - `head` — монотонно зростаючий індекс, звідки споживач вилучає наступний елемент.
   - `tail` — монотонно зростаючий індекс, куди виробник записує новий елемент.
   - Поточна кількість елементів у черзі: `occupancy = tail - head`.
2. **Гістерезисні пороги:**
   - `HWM (High Watermark)` — верхня межа (наприклад, 80% від `Capacity`). При `occupancy >= HWM` виробник переводиться в режим очікування або отримує сигнал відмови.
   - `LWM (Low Watermark)` — нижня межа (наприклад, 30% від `Capacity`). Поки черга не опуститься до `occupancy <= LWM`, сигнал пробудження виробнику не надсилається.
3. **Умовні змінні (Condition Variables):**
   - `not_empty` — сигналізує споживачеві, що в буфері з'явилися доступні дані (`occupancy > 0`).
   - `can_produce` — сигналізує виробникові, що буфер спорожнів нижче позначки `LWM` і можна відновити запис.
   - `is_paused` — булевий прапорець, що фіксує активний стан блокування виробника для уникнення надлишкових системних викликів `signal()`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <pthread.h>
#include <errno.h>

typedef enum {
    DROP_NONE = 0,    /* Блокуючий протитиск (чекати LWM) */
    DROP_NEWEST = 1,  /* Відхилити вхідний елемент */
    DROP_OLDEST = 2   /* Перетерти найстаріший елемент (Head drop) */
} drop_policy_t;

typedef struct {
    int64_t *data;
    size_t capacity;
    size_t mask;
    size_t head;
    size_t tail;
    size_t hwm;
    size_t lwm;
    bool is_paused;
    bool is_closed;

    pthread_mutex_t lock;
    pthread_cond_t not_empty;
    pthread_cond_t can_produce;
} ring_buffer_t;

/* Ініціалізація кільцевого буфера */
int ring_buffer_init(ring_buffer_t *rb, size_t capacity, size_t hwm, size_t lwm) {
    if ((capacity & (capacity - 1)) != 0 || capacity == 0) {
        return -EINVAL; /* Ємність мусить бути степенем двійки */
    }
    if (hwm > capacity || lwm >= hwm) {
        return -EINVAL; /* Некоректні водяні знаки */
    }

    rb->data = (int64_t *)malloc(capacity * sizeof(int64_t));
    if (!rb->data) return -ENOMEM;

    rb->capacity = capacity;
    rb->mask = capacity - 1;
    rb->head = 0;
    rb->tail = 0;
    rb->hwm = hwm;
    rb->lwm = lwm;
    rb->is_paused = false;
    rb->is_closed = false;

    pthread_mutex_init(&rb->lock, NULL);
    pthread_cond_init(&rb->not_empty, NULL);
    pthread_cond_init(&rb->can_produce, NULL);

    return 0;
}

/* Звільнення ресурсів */
void ring_buffer_destroy(ring_buffer_t *rb) {
    pthread_mutex_lock(&rb->lock);
    rb->is_closed = true;
    pthread_cond_broadcast(&rb->not_empty);
    pthread_cond_broadcast(&rb->can_produce);
    pthread_mutex_unlock(&rb->lock);

    pthread_mutex_destroy(&rb->lock);
    pthread_cond_destroy(&rb->not_empty);
    pthread_cond_destroy(&rb->can_produce);
    free(rb->data);
}

/* Блокуючий запис із контролем HWM/LWM протитиску */
int ring_buffer_push_blocking(ring_buffer_t *rb, int64_t item) {
    pthread_mutex_lock(&rb->lock);

    while (!rb->is_closed) {
        size_t count = rb->tail - rb->head;

        /* Якщо буфер досяг HWM, активуємо паузу */
        if (count >= rb->hwm) {
            rb->is_paused = true;
        }

        /* Якщо пауза активна, виробник спить до опускання нижче LWM */
        if (rb->is_paused) {
            pthread_cond_wait(&rb->can_produce, &rb->lock);
            continue;
        }

        /* Запис елемента */
        rb->data[rb->tail & rb->mask] = item;
        rb->tail++;

        /* Сповіщення споживача */
        pthread_cond_signal(&rb->not_empty);
        pthread_mutex_unlock(&rb->lock);
        return 0;
    }

    pthread_mutex_unlock(&rb->lock);
    return -EPIPE; /* Чергу закрито */
}

/* Неблокуючий запис із політикою скидання */
int ring_buffer_try_push(ring_buffer_t *rb, int64_t item, drop_policy_t policy) {
    pthread_mutex_lock(&rb->lock);

    if (rb->is_closed) {
        pthread_mutex_unlock(&rb->lock);
        return -EPIPE;
    }

    size_t count = rb->tail - rb->head;

    if (count >= rb->capacity) {
        if (policy == DROP_NEWEST) {
            pthread_mutex_unlock(&rb->lock);
            return -EAGAIN; /* Відкинути новий пакет */
        } else if (policy == DROP_OLDEST) {
            /* Витіснити найстаріший елемент */
            rb->head++;
        } else {
            pthread_mutex_unlock(&rb->lock);
            return -EBUSY;
        }
    }

    rb->data[rb->tail & rb->mask] = item;
    rb->tail++;

    pthread_cond_signal(&rb->not_empty);
    pthread_mutex_unlock(&rb->lock);
    return 0;
}

/* Блокуюче читання споживача з перевіркою LWM для пробудження */
int ring_buffer_pop_blocking(ring_buffer_t *rb, int64_t *out_item) {
    pthread_mutex_lock(&rb->lock);

    while (rb->tail == rb->head && !rb->is_closed) {
        pthread_cond_wait(&rb->not_empty, &rb->lock);
    }

    if (rb->tail == rb->head && rb->is_closed) {
        pthread_mutex_unlock(&rb->lock);
        return -EPIPE;
    }

    *out_item = rb->data[rb->head & rb->mask];
    rb->head++;

    size_t count = rb->tail - rb->head;

    /* Якщо виробник спав і черга опустилася до LWM — будимо виробника */
    if (rb->is_paused && count <= rb->lwm) {
        rb->is_paused = false;
        pthread_cond_broadcast(&rb->can_produce);
    }

    pthread_mutex_unlock(&rb->lock);
    return 0;
}
```
```cpp
#include <vector>
#include <mutex>
#include <condition_variable>
#include <optional>
#include <expected>
#include <cstdint>
#include <concepts>
#include <system_error>

enum class DropPolicy {
    None,       // Блокуючий протитиск
    DropNewest, // Відхилення нових даних
    DropOldest  // Витіснення найстаріших даних (Head Drop)
};

enum class BufferError {
    Closed,
    BufferFull,
    InvalidWatermark
};

template <typename T>
class BoundedRingBuffer {
public:
    BoundedRingBuffer(size_t capacity, size_t hwm, size_t lwm)
        : capacity_(capacity),
          mask_(capacity - 1),
          hwm_(hwm),
          lwm_(lwm),
          buffer_(capacity) {
        if ((capacity & (capacity - 1)) != 0 || capacity == 0 || hwm > capacity || lwm >= hwm) {
            throw std::invalid_argument("Capacity must be power of 2 and 0 < LWM < HWM <= Capacity");
        }
    }

    ~BoundedRingBuffer() {
        close();
    }

    // Заборона копіювання
    BoundedRingBuffer(const BoundedRingBuffer&) = delete;
    BoundedRingBuffer& operator=(const BoundedRingBuffer&) = delete;

    void close() noexcept {
        std::unique_lock<std::mutex> lock(mutex_);
        is_closed_ = true;
        not_empty_cv_.notify_all();
        can_produce_cv_.notify_all();
    }

    // Блокуючий запис із гістерезисом
    std::expected<void, BufferError> push_blocking(T item) {
        std::unique_lock<std::mutex> lock(mutex_);

        while (!is_closed_) {
            const size_t count = tail_ - head_;

            if (count >= hwm_) {
                is_paused_ = true;
            }

            if (is_paused_) {
                can_produce_cv_.wait(lock, [this]() {
                    return is_closed_ || !is_paused_;
                });
                continue;
            }

            buffer_[tail_ & mask_] = std::move(item);
            ++tail_;

            not_empty_cv_.notify_one();
            return {};
        }

        return std::unexpected(BufferError::Closed);
    }

    // Неблокуючий запис із вибором політики скидання
    std::expected<void, BufferError> try_push(T item, DropPolicy policy = DropPolicy::DropNewest) {
        std::unique_lock<std::mutex> lock(mutex_);

        if (is_closed_) {
            return std::unexpected(BufferError::Closed);
        }

        const size_t count = tail_ - head_;

        if (count >= capacity_) {
            if (policy == DropPolicy::DropNewest) {
                return std::unexpected(BufferError::BufferFull);
            } else if (policy == DropPolicy::DropOldest) {
                ++head_; // Витісняємо найстаріший елемент
            }
        }

        buffer_[tail_ & mask_] = std::move(item);
        ++tail_;

        not_empty_cv_.notify_one();
        return {};
    }

    // Блокуюче читання споживача
    std::expected<T, BufferError> pop_blocking() {
        std::unique_lock<std::mutex> lock(mutex_);

        not_empty_cv_.wait(lock, [this]() {
            return is_closed_ || (tail_ > head_);
        });

        if (head_ == tail_ && is_closed_) {
            return std::unexpected(BufferError::Closed);
        }

        T item = std::move(buffer_[head_ & mask_]);
        ++head_;

        const size_t count = tail_ - head_;

        // Гістерезисне пробудження виробника при досягненні LWM
        if (is_paused_ && count <= lwm_) {
            is_paused_ = false;
            can_produce_cv_.notify_all();
        }

        return item;
    }

    [[nodiscard]] size_t size() const noexcept {
        std::unique_lock<std::mutex> lock(mutex_);
        return tail_ - head_;
    }

private:
    const size_t capacity_;
    const size_t mask_;
    const size_t hwm_;
    const size_t lwm_;

    std::vector<T> buffer_;
    size_t head_{0};
    size_t tail_{0};

    bool is_paused_{false};
    bool is_closed_{false};

    mutable std::mutex mutex_;
    std::condition_variable not_empty_cv_;
    std::condition_variable can_produce_cv_;
};
```
:::

### Покроковий розбір сценаріїв виконання

#### Сценарій A: Швидкий виробник і повільний споживач
1. Виробник на високій швидкості заповнює буфер від індексу `0` до `HWM` (наприклад, 800 елементів із 1000).
2. На 801-му елементі умова `count >= hwm_` стає істинною: встановлюється `is_paused = true`.
3. Виробник входить у виклик `can_produce_cv_.wait(lock)`. М'ютекс звільняється, а потік виробника переводиться ядром у стан блокування.
4. Споживач прокидається по черзі на кожне вилучення, обробляє елементи `0, 1, 2, ...` і зменшує різницю `tail - head`.
5. Поки `count > LWM` (наприклад, від 800 до 301 елемента), споживач не здійснює жодних сповіщень.
6. Коли споживач вилучає 300-й елемент (`count == 300 <= LWM`), умова гістерезису спрацьовує: прапорець `is_paused` скидається в `false`, і надсилається `can_produce_cv_.notify_all()`.
7. Виробник прокидається і безперешкодно записує наступні 500 елементів пакетною серією.

#### Сценарій B: Повільний виробник і швидкий споживач
1. Споживач вичитує всі доступні елементи, після чого `head == tail`.
2. Споживач блокується на умовній змінній `not_empty_cv_`.
3. Виробник генерує черговий елемент, записує його в масив і викликає `not_empty_cv_.notify_one()`.
4. Споживач прокидається, забирає дані й знову переходить у режим очікування без активізації механізму протитиску HWM.

---

### Детальний розбір оптимізацій та підводні камені

#### 1. Захист від хибних пробуджень (Spurious Wakeups)
У багатозадачних операційних системах системні виклики очікування на умовних змінних (`pthread_cond_wait` у POSIX або `std::condition_variable::wait` у C++) можуть повертати керування до того, як інший потік надіслав явний сигнал `signal()` чи `notify_one()`. Це стається через обробку апаратних та програмних переривань ядра Linux.

Якщо потік після повернення з виклику очікування не перевірить інваріант повторно, він спробує виконати запис у повністю заповнений масив, що зруйнує дані. Використання циклу `while (!condition)` або лямбда-предиката в C++ гарантує, що потік продовжить роботу виключно за умови реального виконання інваріанта стану.

#### 2. Атомарність зміни прапорця стану паузи
Прапорець `is_paused` є ключовим для усунення стану гонки (race condition). Якщо перевіряти лише рівень `count <= LWM` без додаткового стану, споживач був би змушений викликати `pthread_cond_broadcast()` на кожне вилучення елемента з черги, що призвело б до масового шторму сповіщень (*notification storm*) і марних спроб захоплення м'ютекса.

Завдяки прапорцю `is_paused`:
- Системний сигнал пробудження надсилається **рівно один раз** — у той момент, коли потік споживача перетинає поріг `LWM` зверху вниз.
- Усі наступні операції читання до порогу `0` виконуються споживачем без будь-яких сповіщень виробника.

#### 3. Вирівнювання пам'яті та усунення хибного розділення (False Sharing)
У високопродуктивних lock-free варіантах кільцевих буферів покажчики `head` та `tail` мутуються різними ядрами процесора: ядро виробника постійно змінює `tail`, а ядро споживача — `head`.

Якщо змінні `head` і `tail` розташовані в пам'яті поруч, вони потрапляють в одну 64-байтну лінію кешу процесора (L1 cache line). Кожна мутація `tail` призводить до апаратної інвалідації лінії кешу за протоколом MESI/MOESI на ядрі споживача, що знижує пропускну здатність шини пам'яті до 5–10 разів. Для запобігання цьому у промислових реалізаціях покажчики розносять на окремі лінії кешу за допомогою директиви вирівнювання `alignas(64)`:

```cpp
struct alignas(64) ProducerState {
    size_t tail{0};
    bool is_paused{false};
};

struct alignas(64) ConsumerState {
    size_t head{0};
};
```

#### 4. Порівняльний аналіз стратегій скидання: `DropNewest` проти `DropOldest`
- **Стратегія `DropNewest` (Tail Drop):** Найпростіша в реалізації, оскільки не вимагає модифікації позиції читання `head`. Застосовується в транзакційних сервісах, де важлива послідовна хронологія перших отриманих команд, а надлишок відхиляється з кодом помилки `EAGAIN` чи HTTP 429 (Too Many Requests).
- **Стратегія `DropOldest` (Head Drop):** Зсуває покажчик `head++`, викидаючи найдавніший пакет без його читання споживачем. Це незамінно для обробки аудіо, відео, потоків відстеження координат дронів та сенсорів реального часу, де затримка є критичнішою за повноту історії.
