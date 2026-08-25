# ⚙️ Реалізація рушія типізованих буферизованих каналів

Будь-який механізм каналів у високорівневих мовах програмування (Go, Rust, Kotlin) спирається на низькорівневу координацію пам'яті операційної системи. Щоб зрозуміти, як саме абстракція CSP позбавляє прикладний код гонок даних, необхідно розглянути її внутрішню механіку: як системний м'ютекс, змінні стану (condition variables) та кільцевий буфер утворюють потокобезпечний транспорт із підтримкою блокувального очікування, неблокувального опитування та коректного широкомовного закриття.

### Архітектура дескриптора каналу

Канал повинен гарантувати дотримання таких інженерних інваріантів:
1. **Кільцевий буфер фіксованого розміру:** Зберігає елементи за принципом FIFO без додаткових динамічних алокацій пам'яті під час передачі повідомлень. Використання неперервного масиву гарантує високу локальність даних у кеші процесора L1/L2.
2. **Змінні стану для очікування:**
   - `not_full`: Сигналізує відправникам, коли в буфері звільняється хоча б одна комірка або коли канал переходить у закритий стан.
   - `not_empty`: Сигналізує отримувачам, коли в буфер надходить новий елемент або коли канал закривається.
3. **Статуси операцій:** Чітке розмежування успішної передачі, блокування, порожнього стану при неблокувальному виклику та читання із закритого каналу.

### Повна реалізація мовами C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <pthread.h>
#include <errno.h>

typedef enum {
    CHAN_OK = 0,
    CHAN_CLOSED = -1,
    CHAN_WOULDBLOCK = -2,
    CHAN_ERR = -3
} chan_status_t;

typedef struct {
    void **buffer;
    size_t capacity;
    size_t size;
    size_t head;
    size_t tail;
    bool closed;
    pthread_mutex_t lock;
    pthread_cond_t not_full;
    pthread_cond_t not_empty;
} chan_t;

chan_t *chan_create(size_t capacity) {
    if (capacity == 0) {
        capacity = 1; // Уніфіковане представлення для буферизованої черги
    }
    chan_t *ch = (chan_t *)malloc(sizeof(chan_t));
    if (!ch) return NULL;

    ch->buffer = (void **)malloc(sizeof(void *) * capacity);
    if (!ch->buffer) {
        free(ch);
        return NULL;
    }

    ch->capacity = capacity;
    ch->size = 0;
    ch->head = 0;
    ch->tail = 0;
    ch->closed = false;

    pthread_mutex_init(&ch->lock, NULL);
    pthread_cond_init(&ch->not_full, NULL);
    pthread_cond_init(&ch->not_empty, NULL);

    return ch;
}

chan_status_t chan_send(chan_t *ch, void *data) {
    pthread_mutex_lock(&ch->lock);

    while (ch->size == ch->capacity && !ch->closed) {
        pthread_cond_wait(&ch->not_full, &ch->lock);
    }

    if (ch->closed) {
        pthread_mutex_unlock(&ch->lock);
        return CHAN_CLOSED;
    }

    ch->buffer[ch->tail] = data;
    ch->tail = (ch->tail + 1) % ch->capacity;
    ch->size++;

    pthread_cond_signal(&ch->not_empty);
    pthread_mutex_unlock(&ch->lock);
    return CHAN_OK;
}

chan_status_t chan_recv(chan_t *ch, void **out_data) {
    pthread_mutex_lock(&ch->lock);

    while (ch->size == 0 && !ch->closed) {
        pthread_cond_wait(&ch->not_empty, &ch->lock);
    }

    if (ch->size == 0 && ch->closed) {
        pthread_mutex_unlock(&ch->lock);
        *out_data = NULL;
        return CHAN_CLOSED;
    }

    *out_data = ch->buffer[ch->head];
    ch->head = (ch->head + 1) % ch->capacity;
    ch->size--;

    pthread_cond_signal(&ch->not_full);
    pthread_mutex_unlock(&ch->lock);
    return CHAN_OK;
}

chan_status_t chan_try_send(chan_t *ch, void *data) {
    pthread_mutex_lock(&ch->lock);

    if (ch->closed) {
        pthread_mutex_unlock(&ch->lock);
        return CHAN_CLOSED;
    }

    if (ch->size == ch->capacity) {
        pthread_mutex_unlock(&ch->lock);
        return CHAN_WOULDBLOCK;
    }

    ch->buffer[ch->tail] = data;
    ch->tail = (ch->tail + 1) % ch->capacity;
    ch->size++;

    pthread_cond_signal(&ch->not_empty);
    pthread_mutex_unlock(&ch->lock);
    return CHAN_OK;
}

chan_status_t chan_try_recv(chan_t *ch, void **out_data) {
    pthread_mutex_lock(&ch->lock);

    if (ch->size == 0) {
        bool is_closed = ch->closed;
        pthread_mutex_unlock(&ch->lock);
        *out_data = NULL;
        return is_closed ? CHAN_CLOSED : CHAN_WOULDBLOCK;
    }

    *out_data = ch->buffer[ch->head];
    ch->head = (ch->head + 1) % ch->capacity;
    ch->size--;

    pthread_cond_signal(&ch->not_full);
    pthread_mutex_unlock(&ch->lock);
    return CHAN_OK;
}

void chan_close(chan_t *ch) {
    pthread_mutex_lock(&ch->lock);
    if (!ch->closed) {
        ch->closed = true;
        pthread_cond_broadcast(&ch->not_full);
        pthread_cond_broadcast(&ch->not_empty);
    }
    pthread_mutex_unlock(&ch->lock);
}

void chan_destroy(chan_t *ch) {
    if (!ch) return;
    pthread_mutex_destroy(&ch->lock);
    pthread_cond_destroy(&ch->not_full);
    pthread_cond_destroy(&ch->not_empty);
    free(ch->buffer);
    free(ch);
}
```
```cpp
#include <iostream>
#include <vector>
#include <optional>
#include <mutex>
#include <condition_variable>
#include <utility>

enum class ChannelStatus {
    Success,
    Closed,
    WouldBlock
};

template <typename T>
class Channel {
public:
    explicit Channel(std::size_t capacity = 1)
        : m_capacity(std::max<std::size_t>(1, capacity)),
          m_buffer(m_capacity),
          m_head(0),
          m_tail(0),
          m_size(0),
          m_closed(false) {}

    ~Channel() {
        close();
    }

    Channel(const Channel&) = delete;
    Channel& operator=(const Channel&) = delete;
    Channel(Channel&&) = delete;
    Channel& operator=(Channel&&) = delete;

    ChannelStatus send(T value) {
        std::unique_lock<std::mutex> lock(m_mutex);
        m_not_full.wait(lock, [this]() {
            return m_size < m_capacity || m_closed;
        });

        if (m_closed) {
            return ChannelStatus::Closed;
        }

        m_buffer[m_tail] = std::move(value);
        m_tail = (m_tail + 1) % m_capacity;
        ++m_size;

        m_not_empty.notify_one();
        return ChannelStatus::Success;
    }

    std::optional<T> recv() {
        std::unique_lock<std::mutex> lock(m_mutex);
        m_not_empty.wait(lock, [this]() {
            return m_size > 0 || m_closed;
        });

        if (m_size == 0 && m_closed) {
            return std::nullopt;
        }

        T item = std::move(m_buffer[m_head]);
        m_head = (m_head + 1) % m_capacity;
        --m_size;

        m_not_full.notify_one();
        return item;
    }

    ChannelStatus try_send(T value) {
        std::unique_lock<std::mutex> lock(m_mutex);
        if (m_closed) {
            return ChannelStatus::Closed;
        }
        if (m_size == m_capacity) {
            return ChannelStatus::WouldBlock;
        }

        m_buffer[m_tail] = std::move(value);
        m_tail = (m_tail + 1) % m_capacity;
        ++m_size;

        m_not_empty.notify_one();
        return ChannelStatus::Success;
    }

    std::pair<ChannelStatus, std::optional<T>> try_recv() {
        std::unique_lock<std::mutex> lock(m_mutex);
        if (m_size == 0) {
            if (m_closed) {
                return {ChannelStatus::Closed, std::nullopt};
            }
            return {ChannelStatus::WouldBlock, std::nullopt};
        }

        T item = std::move(m_buffer[m_head]);
        m_head = (m_head + 1) % m_capacity;
        --m_size;

        m_not_full.notify_one();
        return {ChannelStatus::Success, std::move(item)};
    }

    void close() noexcept {
        {
            std::lock_guard<std::mutex> lock(m_mutex);
            if (m_closed) {
                return;
            }
            m_closed = true;
        }
        m_not_full.notify_all();
        m_not_empty.notify_all();
    }

    [[nodiscard]] bool is_closed() const noexcept {
        std::lock_guard<std::mutex> lock(m_mutex);
        return m_closed;
    }

private:
    const std::size_t m_capacity;
    std::vector<T> m_buffer;
    std::size_t m_head;
    std::size_t m_tail;
    std::size_t m_size;
    bool m_closed;
    mutable std::mutex m_mutex;
    std::condition_variable m_not_full;
    std::condition_variable m_not_empty;
};
```
:::

### Детальний інженерний розбір роботи коду

Розглянемо покроково, як взаємодіють структури даних та системні виклики під час передачі повідомлення у багатопотоковому середовищі:

#### 1. Механізм блокування та запобігання втраченим сигналам (Lost Wakeups)
У функції `send` потік спочатку захоплює м'ютекс `m_mutex`. Захоплення м'ютексу гарантує ексклюзивний доступ до лічильника `m_size` та індексів буфера. 

Якщо буфер заповнений (`m_size == m_capacity`), потік викликає метод очікування на змінній стану `m_not_full.wait(lock, predicate)`. 

Цей системний виклик атомарно виконує дві взаємопов'язані дії:
1. Звільняє м'ютекс `m_mutex`, дозволяючи споживачам отримати доступ до дескриптора каналу і вилучити черговий елемент.
2. Присипляє поточний потік у черзі очікування планувальника ядра операційної системи (використовуючи механізм `futex` у Linux).

Коли потік пробуджується споживачем, він повторно захоплює `m_mutex` перед тим, як перевірити стан предикату. Завдяки використанню циклу перевірки стану (у С++ це автоматично виконує лямбда-предикат у методі `wait`) система повністю захищена від **хибних пробуджень** (*spurious wakeups*), коли ядро операційної системи пробуджує потік без фактичного виклику `notify` з боку іншого потоку.

#### 2. Диференціація `notify_one` та `notify_all`
Під час звичайної передачі одного повідомлення пробуджується рівно один реципієнт за допомогою `notify_one` (`pthread_cond_signal`). Це оптимізує навантаження на систему, оскільки пробудження всіх заблокованих потоків одночасно спричинило б явище «громового стада» (*thundering herd*), коли десятки ядер процесора одночасно намагаються захопити один і той самий м'ютекс, створюючи колапс кеш-ліній та пікове споживання CPU.

Проте під час виклику операції `close()` обов'язково викликати `notify_all()` (`pthread_cond_broadcast`). Це пов'язано з тим, що закриття каналу є широкомовною системною подією: абсолютно всі заблоковані читачі та відправники повинні дізнатися про завершення життєвого циклу каналу і коректно завершити очікування.

#### 3. Семантика повного вичерпання буфера (Draining Semantics)
Закриття каналу не призводить до раптової втрати даних. Якщо відправники встигли записати кілька елементів до моменту виклику `close()`, споживач під час наступних викликів `recv()` успішно отримає всі збережені значення. 

Лише коли лічильник `m_size` досягає нуля при встановленому прапорці `m_closed == true`, функція `recv()` повертає `std::nullopt` (у версії для C — статус `CHAN_CLOSED`), що слугує штатним сигналом завершення циклу обробки для потоків-споживачів.

#### 4. Семантика переміщення (Move Semantics) у C++
У реалізації на C++ значення передаються за допомогою `std::move`. Це дозволяє передавати через канал «важкі» об'єкти (наприклад, `std::vector`, великі рядки або `std::unique_ptr`) без жодного глибокого копіювання динамічної пам'яті: переміщуються лише покажчики та розміри дескрипторів, що зводить накладні витрати передачі до кількох машинних інструкцій.

#### 5. Безпека життєвого циклу при руйнуванні (Destruction Safety)
Деструктор класу `Channel` у C++ гарантовано викликає метод `close()`. Це запобігає зависанню сторонніх потоків, якщо власник каналу вийшов з області видимості. Всі потоки, заблоковані на читанні або записі, миттєво отримують сигнал пробудження і повертають статус завершення, що виключає витоки ресурсів у багатопотокових додатках.

#### 6. Апаратна оптимізація кеш-ліній та усунення хибного розділення (False Sharing)
У високопродуктивних системах критично важливо, щоб м'ютекс `m_mutex` та змінні стану не знаходилися на одній кеш-лінії процесора (64 байти) з даними буфера або лічильниками інших ядер. Якщо кілька потоків одночасно мутують змінні в межах однієї 64-байтової кеш-лінії, протокол когерентності MESI змушує ядра скидати стан лінії у `Invalid`, викликаючи багаторазове сповільнення доступу до пам'яті. У промислових реалізаціях структури дескрипторів вирівнюються директивою `alignas(64)` для ізоляції гарячих змінних.

#### 7. Поведінка в топологіях багато-до-багатьох (MPMC Scaling)
Наведена реалізація підтримує довільну кількість паралельних виробників та споживачів (Multi-Producer Multi-Consumer). Завдяки взаємному виключенню через єдиний м'ютекс усі переходи станів черги є строго лінеаризовними. Проте при зростанні кількості потоків понад кількість фізичних ядер процесора конкуренція за м'ютекс призводить до збільшення накладних витрат на системні виклики `futex`, що є сигналом для переходу до шардування каналів або конвеєрної декомпозиції задач.
