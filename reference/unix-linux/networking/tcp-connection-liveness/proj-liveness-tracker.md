# ⚙️ Реалізація прикладного трекера життєздатності з'єднання (Ping-Pong Heartbeat)

У цьому проекті демонструється розробка асинхронного прикладного трекера життєздатності TCP-з'єднання на основі протоколу Ping-Pong (Heartbeat). Прикладний Heartbeat є єдиним способом гарантувати, що не лише мережевий стек ядра Linux, але й подійний цикл (event loop) та прикладна логіка на віддаленій стороні перебувають у працездатному та задієному стані.

Розроблений модуль призначений для інтеграції у високопродуктивні неблокуючі сервери та клієнти, побудовані на основі системного виклику `epoll` або сучасних подійних бібліотек (таких як libuv, Asio чи io_uring).

---

## 1. Архітектурний задум і подвійний таймер

Трекер життєздатності будується навколо концепції подвійного таймера простою, який відстежує час останньої мережевої активності на файловому дескрипторі:

1. **Таймер відправки Ping (`ping_interval`)**: Якщо протягом заданого часу (наприклад, 5 секунд) від peer-а не надійшло жодного корисного повідомлення або відповіді, трекер генерує та надсилає спеціальний службовий кадр `PING`.
2. **Таймер очікування Pong (`pong_timeout`)**: Після відправки `PING` запускається локальний таймаут очікування (наприклад, 3 секунди). Якщо протягом цього вікна від віддаленого вузла не надходить зворотний кадр `PONG`, трекер фіксує збій прикладної сесії і примусово ініціює закриття сокета.
3. **Оновлення таймерів при будь-якій активності**: Будь-який вхідний пакет від peer-а (як прикладна корисне навантаження, так і відповідь `PONG`) вважається доказом життєздатності каналу та автоматично скидає таймер очікування.

Такий підхід запобігає надсиланню непотрібних зондів у періоди, коли між хостами передається активний потік прикладних даних, що суттєво економить пропускну здатність мережевого каналу.

```text
       Прийомо-передача прикладних даних
                     │
                     ▼
       ┌───────────────────────────┐
       │ Скидання last_rx_time     │
       └─────────────┬─────────────┘
                     │
                     ▼
       [Простой > ping_interval?] ─── НІ ───> Чекаємо далі
                     │
                    ТАК
                     │
                     ▼
       ┌───────────────────────────┐
       │ Надсилання кадру PING     │
       │ Старт pong_timer          │
       └─────────────┬─────────────┘
                     │
                     ▼
       [Отримано PONG у межах       ─── ТАК ──> Звичайний режим
        pong_timeout?]                          (скидання таймера)
                     │
                    НІ
                     │
                     ▼
       ┌───────────────────────────┐
       │ Аварійне закриття сокета  │
       │ (Прикладний розрив сесії) │
       └───────────────────────────┘
```

---

## 2. Структури даних для масштабування: Hashed Timing Wheel

У висококонкурентних серверах, які обслуговують 100,000 паралельних TCP-з'єднань, сканування масиву всіх сокетів кожної секунди для перевірки таймерів у циклі `for (int i = 0; i < N; ++i)` вимагає `O(N)` операцій і створює неприпустиме навантаження на процесор.

Для ефективного відстеження таймаутів застосовується структура даних **Hashed Timing Wheel (Хешоване колесо часу)**, запропонована Джорджем Варгезе та Тоні Лауком.

### Принцип роботи Hashed Timing Wheel

1. **Слоти й круговий буфер:** Колесо часу є круговим масивом із `M` слотів (наприклад, 60 слотів для відстеження хвилинного вікна). Кожен слот відповідає конкретній секунді часу.
2. **Вказівник поточного часу:** Подібний до секундної стрілки годинника. Щосекунди вказівник зсувається на один слот уперед: `current_slot = (current_slot + 1) % M`.
3. **Двобічно зв'язані списки сокетів:** Кожен слот містить список сокетів, таймаут яких повинен спрацювати на цій секунді.
4. **Операції добавлення та вилучення (`O(1)`):**
   - **Додавання сокета:** Коли сокет активується, його приєднують до слота `(current_slot + delay_sec) % M`. Операція займає `O(1)`.
   - **Оновлення при activity:** При отриманні даних сокет вилучається зі свого старого слота і переноситься в новий за `O(1)`.
   - **Перевірка таймаутів:** При переході стрілки на новий слот ядро обробляє лише сокети у цьому конкретному слоті (`O(1)` в середньому).

```text
              [Slot 59]   [Slot 0]   [Slot 1]
                 ┌───────────┬───────────┐
                 │ Socket 42 │ Socket 12 │ ───> Socket 88
                 └───────────┴───────────┘
                       ▲
                       │  Стрілка годинника (Tick щосекунди)
```

### Алгоритмічна складність та вибір таймерів

Порівняємо три підходи до обробки таймерів простою у висококонкурентному сервері:

- **Лінійне сканування масиву:** Складність вставки `O(1)`, оновлення `O(1)`, перевірки `O(N)`. При 100,000 сокетів процес завантажує 100% CPU на кожному тіку.
- **Min-Heap (Пріоритетна черга):** Складність вставки `O(log N)`, оновлення `O(log N)`, перевірки найгострішого таймауту `O(1)`. Підходить для невеликої кількості сокетів (до 10,000), але створює накладні витрати на балансування дерева.
- **Hashed Timing Wheel:** Складність вставки `O(1)`, оновлення `O(1)`, перевірки `O(1)`. Забезпечує найвищу швидкість і мінімальну локальність даних для пам'яті.

---

## 3. Протокольний кадр Heartbeat

Для мінімізації накладних витрат та забезпечення простого парсингу у байт-орієнтованому потоці TCP, службові кадри розпізнаються за першим байтом заголовка (Type Byte):

- `0x01` — `DATA` (прикладні дані користувача)
- `0x02` — `PING` (запит перевірки життєздатності)
- `0x03` — `PONG` (відповідь на запит перевірки)

При використанні бінарних кадрових бітових протоколів (таких як WebSockets або gRPC) кадри Ping та Pong містять у заголовку прапорець Control Frame та опціональний ідентифікатор транзакції (Payload Identifier), який перевіряється на збіг при отриманні Pong.

---

## 4. Повна реалізація трекера на C та C++

Нижче наведено повністю працездатну реалізацію модуля перевірки liveness для неблокуючих сокетів із використанням `:::tabs`. Приклад мовою C++ використовує типи `std::chrono::steady_clock` для уникнення проблем зі стрибками системного часу NTP та гарантує монотонність вимірювання інтервалів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <errno.h>
#include <sys/socket.h>

#define MSG_TYPE_DATA 0x01
#define MSG_TYPE_PING 0x02
#define MSG_TYPE_PONG 0x03

typedef struct {
    int fd;
    time_t last_rx_time;
    time_t ping_sent_time;
    int ping_pending;
    int ping_interval_sec;
    int pong_timeout_sec;
} heartbeat_tracker_t;

void heartbeat_init(heartbeat_tracker_t *hb, int fd, int interval_sec, int timeout_sec) {
    hb->fd = fd;
    hb->last_rx_time = time(NULL);
    hb->ping_sent_time = 0;
    hb->ping_pending = 0;
    hb->ping_interval_sec = interval_sec;
    hb->pong_timeout_sec = timeout_sec;
}

void heartbeat_on_rx(heartbeat_tracker_t *hb, unsigned char msg_type) {
    hb->last_rx_time = time(NULL);
    if (msg_type == MSG_TYPE_PONG) {
        hb->ping_pending = 0;
    } else if (msg_type == MSG_TYPE_PING) {
        // Негайно відповідаємо PONG у відповідь на PING
        unsigned char pong = MSG_TYPE_PONG;
        send(hb->fd, &pong, 1, MSG_NOSIGNAL);
    }
}

int heartbeat_tick(heartbeat_tracker_t *hb) {
    time_t now = time(NULL);

    if (hb->ping_pending) {
        if (now - hb->ping_sent_time >= hb->pong_timeout_sec) {
            // Таймаут очікування PONG перевищено — з'єднання мертве
            return -1;
        }
    } else {
        if (now - hb->last_rx_time >= hb->ping_interval_sec) {
            // Прийшов час надіслати PING
            unsigned char ping = MSG_TYPE_PING;
            if (send(hb->fd, &ping, 1, MSG_NOSIGNAL) == 1) {
                hb->ping_pending = 1;
                hb->ping_sent_time = now;
            } else {
                return -1;
            }
        }
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <chrono>
#include <optional>
#include <cstdint>
#include <unistd.h>
#include <sys/socket.h>

enum class FrameType : uint8_t {
    Data = 0x01,
    Ping = 0x02,
    Pong = 0x03
};

class HeartbeatTracker {
public:
    using Clock = std::chrono::steady_clock;
    using TimePoint = Clock::time_point;

    HeartbeatTracker(int socket_fd, std::chrono::seconds interval, std::chrono::seconds timeout)
        : fd_(socket_fd), ping_interval_(interval), pong_timeout_(timeout), last_rx_time_(Clock::now()) {}

    void on_frame_received(FrameType type) {
        last_rx_time_ = Clock::now();
        if (type == FrameType::Pong) {
            ping_pending_ = false;
        } else if (type == FrameType::Ping) {
            send_frame(FrameType::Pong);
        }
    }

    [[nodiscard]] bool tick() {
        const auto now = Clock::now();

        if (ping_pending_) {
            if (now - ping_sent_time_ >= pong_timeout_) {
                // Сервер не відповів на PONG у межах дозволеного вікна
                return false;
            }
        } else {
            if (now - last_rx_time_ >= ping_interval_) {
                if (send_frame(FrameType::Ping)) {
                    ping_pending_ = true;
                    ping_sent_time_ = now;
                } else {
                    return false;
                }
            }
        }
        return true;
    }

private:
    bool send_frame(FrameType type) {
        const auto byte = static_cast<uint8_t>(type);
        const ::ssize_t ret = ::send(fd_, &byte, sizeof(byte), MSG_NOSIGNAL);
        return ret == sizeof(byte);
    }

    int fd_;
    std::chrono::seconds ping_interval_;
    std::chrono::seconds pong_timeout_;
    TimePoint last_rx_time_;
    TimePoint ping_sent_time_{};
    bool ping_pending_{false};
};
```
:::

---

## 5. Інтеграція у подійний цикл `epoll`

У реальних високонавантажених серверах модуль `HeartbeatTracker` викликається при спрацюванні таймера в подійному циклі (наприклад, кожні 1000 мілісекунд через `timerfd` або регулярну перевірку списку активних з'єднань).

1. При спрацюванні системного таймера `epoll_wait` викликається метод `tick()` для всіх відкритих сесій.
2. Якщо `tick()` повертає `false` (або `-1`), це свідчить про те, що віддалений процес завис або зв'язок втрачено.
3. Сокет негайно вилучається з контексту епол `epoll_ctl(epfd, EPOLL_CTL_DEL, fd, NULL)`, викликається `close(fd)`, а застосунок переходить до процедури повторного підключення.

---

## 6. Практичні пастки та способи їх уникнення

### 1. Шторм повторних підключень (Thundering Herd / Reconnection Storm)

Якщо 10,000 клієнтів одночасно втрачають зв'язок із сервером через короткочасний мережевий збій, їхні таймери `Heartbeat` спрацюють одночасно. Щоб сервер не впав від пікового навантаження при одночасному перепідключенні, додають **експоненційну затримку з випадковим тремтінням (Full Jitter)**:

:::tabs
```c
/* Вирахування затримки з випадковим відхиленням (jitter) у C */
int calculate_backoff_c(int attempt, int base_sec, int max_sec) {
    int backoff = base_sec * (1 << attempt);
    if (backoff > max_sec) backoff = max_sec;
    int half = backoff / 2;
    return half + (rand() % (half + 1));
}
```
```cpp
/* Вирахування затримки з випадковим відхиленням (jitter) у C++ */
#include <chrono>
#include <random>
#include <algorithm>

std::chrono::seconds calculate_backoff_cpp(int attempt, std::chrono::seconds base, std::chrono::seconds max_val) {
    auto backoff_count = base.count() * (1LL << attempt);
    auto capped_count = std::min<long long>(backoff_count, max_val.count());
    auto half = capped_count / 2;
    
    thread_local std::mt19937 rng{std::random_device{}()};
    std::uniform_int_distribution<long long> dist(0, half);
    
    return std::chrono::seconds(half + dist(rng));
}
```
:::

### 2. Застрягання у буферах відправки (TCP Send Queue Head-of-Line Blocking)

Якщо мережевий канал розірвано, виклик `send()` для `PING`-кадру може заблокуватися (для блокуючих сокетів) або наповнити буфер відправки (для неблокуючих сокетів). Для запобігання цьому обов'язково використовується комбінація прикладного Heartbeat із сумісним системним таймаутом `TCP_USER_TIMEOUT` на рівні ядра Linux.

### 3. Перехоплення сигналу SIGPIPE

Під час відправки кадру `PING` у сокет, віддалена сторона якого вже закрила з'єднання та надіслала RST, за замовчуванням ядро Linux генерує для процесу сигнал `SIGPIPE`. Якщо процес не встановив обробник цього сигналу, системна поведінка за замовчуванням — негайно завершити процес (Crash).

Щоб уникнути цього, при кожному системному виклику `send()` обов'язково передається прапорець `MSG_NOSIGNAL` (у Linux) або встановлюється опція сокета `SO_NOSIGPIPE` (у системі macOS/BSD):

:::tabs
```c
/* Блокування сигналу SIGPIPE у виклику send() у C */
#include <sys/socket.h>
#include <errno.h>

ssize_t send_safe_c(int fd, const void *buf, size_t len) {
    ssize_t res = send(fd, buf, len, MSG_NOSIGNAL);
    if (res < 0 && errno == EPIPE) {
        /* Обробка закриття сокета без аварійного виходу з програми */
    }
    return res;
}
```
```cpp
/* Безпечна відправка кадру без SIGPIPE у C++ */
#include <sys/socket.h>
#include <cerrno>
#include <span>
#include <system_error>

std::size_t send_safe_cpp(int fd, std::span<const std::byte> buffer) {
    const ::ssize_t res = ::send(fd, buffer.data(), buffer.size(), MSG_NOSIGNAL);
    if (res < 0) {
        if (errno == EPIPE || errno == ECONNRESET) {
            return 0; // З'єднання закрите
        }
        throw std::system_error(errno, std::generic_category(), "send failed");
    }
    return static_cast<std::size_t>(res);
}
```
:::

### 4. Напіввідкриті з'єднання та обробка часткового запису

У байт-орієнтованому потоці TCP виклик `send()` не гарантує відправку всього кадру за один раз (особливо при використанні неблокуючих сокетів `O_NONBLOCK`). Якщо `send()` відправив лише 0 байтів з поверненням `EAGAIN`, необхідно зберегти `PING` кадр у прикладному буфері запису та зареєструвати прапорець `EPOLLOUT` у подійному циклі `epoll`, перш ніж запускати таймаут очікування `PONG`.
