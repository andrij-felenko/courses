# ⚙️ Буферний автомат та обробка часткового читання й запису в неблокуючих сокетах

Головна практична складність переходу від синхронного блокуючого вводу-виводу до неблокуючого полягає в тому, що протокол TCP є **неперервним неструктурованим байтовим потоком** (*byte stream*), який не має вбудованого поняття «пакета» чи «межі повідомлення» на рівні застосунку.

У традиційному блокуючому коді програміст може викликати допоміжну функцію на кшталт `read_exact(fd, buf, 1024)`, яка засинає в ядрі доти, доки всі 1024 байти не надійдуть у сокет. Потік просто спить, а після пробудження отримує гарантовано повний масив.

У неблокуючому коді така спроба негайно руйнує роботу програми:
1. Системний виклик `read()` повертає рівно стільки байтів, скільки наразі лежить у приймальному буфері ядра (`sk_receive_queue`). Це може бути 17 байтів, 340 байтів або помилка `EAGAIN`, якщо буфер порожній. Одне логічне повідомлення застосунку може надходити фрагментами по кілька байтів через непередбачувані проміжки часу, або навпаки — один виклик `read()` може повернути фрагменти одразу трьох різних повідомлень, склеєних докупи.
2. Системний виклик `write()` при спробі відправити повідомлення розміром 64 КБ скопіює в ядро лише стільки, скільки наразі вільно у передавальному буфері сокета (`sk_write_queue`, наприклад, 4096 байтів), і негайно поверне число `4096`. Якщо решту 60 КБ не зберегти в пам'яті простору користувача й не спробувати надіслати пізніше, хвіст повідомлення буде безповоротно втрачено.

Цей проект реалізує надійний буферний менеджер на базі **скінченного автомата розбору** (*Finite State Machine*, FSM) для фреймінгу повідомлень із фіксованим 4-байтовим заголовком довжини (*Length-Prefixed Framing*).

---

### Архітектура фреймінгу та стани автомата

Щоб надійно передавати структуровані повідомлення через неблокуючий TCP-потік, протокол прикладного рівня розбивається на кадри. Найпростішим та найефективнішим форматом є префікс довжини: кожне повідомлення починається з 4-байтового цілого числа в мережевому порядку байтів (*Big-Endian*), яке вказує точний розмір тіла повідомлення в байтах, після чого слідують самі корисні дані (*payload*).

Кожне неблокуюче з'єднання володіє двома незалежними буферними структурами:
- **Вхідний буфер прийому (`rx_buf`)**: динамічний масив пам'яті, який накопичує сирі байти з мережі.
- **Вихідний буфер передачі (`tx_buf`)**: черга байтів, готових до відправлення, які не вдалося записати в сокет за один системний виклик через тимчасове переповнення передавального буфера ядра.
- **Зміщення розбору (`offset`)**: позиція курсора у вхідному буфері, яка фіксує, скільки байтів уже успішно розпізнано й передано в бізнес-логіку.

Автомат розбору перебуває в одному з трьох базових станів:
1. `STATE_READ_HEADER`: очікування накопичення щонайменше 4 байтів для зчитування довжини наступного повідомлення.
2. `STATE_READ_PAYLOAD`: накопичення байтів корисного навантаження до досягнення заздалегідь відомого розміру `expected_payload_len`.
3. `STATE_FRAME_READY`: повідомлення повністю зібрано в пам'яті, після чого викликається користувацький обробник, а автомат переходить до очікування наступного заголовка.

```
       [Виклик read() на неблокуючому сокеті]
                         │
                         ▼
        ┌──────────────────────────────────┐
        │  Чи накопичено 4 байти довжини?  │
        └─────────────────┬────────────────┘
                  Ні      │          Так
        ┌─────────────────┘          └─────────────────┐
        ▼                                              ▼
 ┌───────────────┐                             ┌───────────────┐
 │ Очікування    │                             │ Розмір N відомий
 │ нових байтів  │                             │ Чи зібрано    │
 │ (стан HEADER) │                             │ N байтів тіла?│
 └───────────────┘                             └───┬───────┬───┘
                                           Ні     │       │ Так
                                  ┌───────────────┘       └───────────────┐
                                  ▼                                       ▼
                           ┌───────────────┐                      ┌───────────────┐
                           │ Очікування    │                      │ Пакет готовий │
                           │ тіла пакета   │                      │ Перехід до    │
                           │ (PAYLOAD)     │                      │ обробки бізнесу
                           └───────────────┘                      └───────────────┘
```

---

### Механіка компактифікації та розширення буферів

При неперервному отриманні даних вхідний буфер поступово заповнюється, а зміщення `offset` просувається вперед. Якщо просто нарощувати масив, пам'ять неконтрольовано витікатиме. Для оптимізації застосовують процедуру **компактифікації** (*compaction*):

- Коли всі накопичені байти повністю оброблені (`offset >= size`), розмір і зміщення просто скидаються в нуль без переміщення пам'яті.
- Якщо в буфері залишився незавершений хвіст наступного повідомлення, функція `memmove()` зсуває залишок байтів на початок виділеного блоку пам'яті, звільняючи місце в кінці масиву для нових системних викликів `read()`.

Якщо ж розмір вхідного повідомлення перевищує поточну місткість буфера, місткість подвоюється через `realloc()` (або `std::vector::resize()` у C++), аж до досягнення максимально допустимої межі безпеки (`MAX_PAYLOAD_SIZE = 1 МБ`), що захищає сервер від атак переповнення пам'яті (*Denial of Service*).

---

### Повна реалізація буферного менеджера

Нижче наведено робочу реалізацію буферного автомата для неблокуючого з'єднання мовами C та C++. Реалізація коректно обробляє часткове читання, частковий запис, переривання сигналами `EINTR` та сигналізацію вичерпання буферів `EAGAIN` / `EWOULDBLOCK`.

:::tabs
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <arpa/inet.h>
#include <sys/socket.h>

#define MAX_PAYLOAD_SIZE (1024 * 1024) /* 1 МБ максимальний розмір пакета */
#define INITIAL_BUF_CAP  4096

typedef enum {
    IO_OK = 0,
    IO_WANT_READ,
    IO_WANT_WRITE,
    IO_PEER_CLOSED,
    IO_ERROR
} io_status_t;

typedef enum {
    STATE_READ_HEADER = 0,
    STATE_READ_PAYLOAD,
    STATE_FRAME_READY
} parser_state_t;

typedef struct {
    uint8_t *data;
    size_t capacity;
    size_t size;
    size_t offset;
} dynamic_buffer_t;

typedef struct {
    int fd;
    parser_state_t rx_state;
    uint32_t expected_payload_len;
    dynamic_buffer_t rx_buf;
    dynamic_buffer_t tx_buf;
} nonblocking_conn_t;

static bool buf_init(dynamic_buffer_t *b, size_t cap) {
    b->data = (uint8_t *)malloc(cap);
    if (!b->data) return false;
    b->capacity = cap;
    b->size = 0;
    b->offset = 0;
    return true;
}

static void buf_free(dynamic_buffer_t *b) {
    if (b->data) {
        free(b->data);
        b->data = NULL;
    }
    b->capacity = b->size = b->offset = 0;
}

static bool buf_ensure_capacity(dynamic_buffer_t *b, size_t needed) {
    if (b->capacity >= needed) return true;
    size_t new_cap = b->capacity * 2;
    if (new_cap < needed) new_cap = needed;
    uint8_t *tmp = (uint8_t *)realloc(b->data, new_cap);
    if (!tmp) return false;
    b->data = tmp;
    b->capacity = new_cap;
    return true;
}

/* Компактифікація буфера: перенесення необробленого залишку на початок */
static void buf_compact(dynamic_buffer_t *b) {
    if (b->offset == 0) return;
    if (b->offset >= b->size) {
        b->size = 0;
        b->offset = 0;
    } else {
        size_t remaining = b->size - b->offset;
        memmove(b->data, b->data + b->offset, remaining);
        b->size = remaining;
        b->offset = 0;
    }
}

int set_socket_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

nonblocking_conn_t* conn_create(int fd) {
    if (set_socket_nonblocking(fd) < 0) return NULL;
    nonblocking_conn_t *c = (nonblocking_conn_t *)calloc(1, sizeof(nonblocking_conn_t));
    if (!c) return NULL;
    c->fd = fd;
    c->rx_state = STATE_READ_HEADER;
    if (!buf_init(&c->rx_buf, INITIAL_BUF_CAP) || !buf_init(&c->tx_buf, INITIAL_BUF_CAP)) {
        buf_free(&c->rx_buf);
        buf_free(&c->tx_buf);
        free(c);
        return NULL;
    }
    return c;
}

void conn_destroy(nonblocking_conn_t *c) {
    if (!c) return;
    if (c->fd >= 0) close(c->fd);
    buf_free(&c->rx_buf);
    buf_free(&c->tx_buf);
    free(c);
}

/* Неблокуюче читання до вичерпання буфера ядра (до отримання EAGAIN) */
io_status_t conn_read_nonblocking(nonblocking_conn_t *c) {
    while (true) {
        buf_compact(&c->rx_buf);
        if (!buf_ensure_capacity(&c->rx_buf, c->rx_buf.size + 4096)) {
            return IO_ERROR;
        }

        ssize_t n = read(c->fd, c->rx_buf.data + c->rx_buf.size, 4096);
        if (n > 0) {
            c->rx_buf.size += (size_t)n;
            continue; /* Вичитуємо всі доступні байти в буфері */
        }
        if (n == 0) {
            return IO_PEER_CLOSED; /* Віддалена сторона надіслала TCP FIN */
        }
        if (errno == EINTR) {
            continue; /* Системний сигнал — повторюємо виклик */
        }
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            return IO_WANT_READ; /* Буфер порожній — повертаємося до мультиплексора */
        }
        return IO_ERROR;
    }
}

/* Розбір накопичених кадрів автоматом */
bool conn_parse_frames(nonblocking_conn_t *c, void (*on_frame)(const uint8_t *payload, size_t len)) {
    while (true) {
        size_t available = c->rx_buf.size - c->rx_buf.offset;

        if (c->rx_state == STATE_READ_HEADER) {
            if (available < sizeof(uint32_t)) {
                return true; /* Недостатньо байтів для читання довжини */
            }
            uint32_t net_len = 0;
            memcpy(&net_len, c->rx_buf.data + c->rx_buf.offset, sizeof(uint32_t));
            c->expected_payload_len = ntohl(net_len);
            c->rx_buf.offset += sizeof(uint32_t);

            if (c->expected_payload_len > MAX_PAYLOAD_SIZE) {
                return false; /* Захист від некоректного розміру кадру */
            }
            c->rx_state = STATE_READ_PAYLOAD;
            available = c->rx_buf.size - c->rx_buf.offset;
        }

        if (c->rx_state == STATE_READ_PAYLOAD) {
            if (available < c->expected_payload_len) {
                return true; /* Тіло кадру надійшло не повністю */
            }
            const uint8_t *payload_ptr = c->rx_buf.data + c->rx_buf.offset;
            on_frame(payload_ptr, c->expected_payload_len);
            c->rx_buf.offset += c->expected_payload_len;

            /* Повертаємося до пошуку наступного кадру */
            c->rx_state = STATE_READ_HEADER;
            c->expected_payload_len = 0;
        }
    }
}

/* Додавання повідомлення у вихідну чергу */
bool conn_enqueue_message(nonblocking_conn_t *c, const uint8_t *payload, size_t len) {
    if (len > MAX_PAYLOAD_SIZE) return false;
    buf_compact(&c->tx_buf);

    size_t total_frame_len = sizeof(uint32_t) + len;
    if (!buf_ensure_capacity(&c->tx_buf, c->tx_buf.size + total_frame_len)) {
        return false;
    }

    uint32_t net_len = htonl((uint32_t)len);
    memcpy(c->tx_buf.data + c->tx_buf.size, &net_len, sizeof(uint32_t));
    c->tx_buf.size += sizeof(uint32_t);

    memcpy(c->tx_buf.data + c->tx_buf.size, payload, len);
    c->tx_buf.size += len;
    return true;
}

/* Скидання вихідного буфера в сокет */
io_status_t conn_flush_write(nonblocking_conn_t *c) {
    while (c->tx_buf.offset < c->tx_buf.size) {
        size_t to_write = c->tx_buf.size - c->tx_buf.offset;
        ssize_t n = write(c->fd, c->tx_buf.data + c->tx_buf.offset, to_write);

        if (n > 0) {
            c->tx_buf.offset += (size_t)n;
            continue;
        }
        if (errno == EINTR) {
            continue;
        }
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            return IO_WANT_WRITE; /* Буфер ядра заповнений — чекаємо готовності на запис */
        }
        return IO_ERROR;
    }

    buf_compact(&c->tx_buf);
    return IO_OK;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <expected>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <arpa/inet.h>
#include <sys/socket.h>

enum class IoStatus {
    Ok,
    WantRead,
    WantWrite,
    PeerClosed,
    Error
};

enum class ParserState {
    ReadHeader,
    ReadPayload
};

class NonblockingConnection {
public:
    static constexpr size_t MaxPayloadSize = 1024 * 1024; // 1 МБ

    explicit NonblockingConnection(int fd) : fd_(fd) {
        int flags = fcntl(fd_, F_GETFL, 0);
        fcntl(fd_, F_SETFL, flags | O_NONBLOCK);
        rx_buf_.reserve(4096);
        tx_buf_.reserve(4096);
    }

    ~NonblockingConnection() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    NonblockingConnection(const NonblockingConnection&) = delete;
    NonblockingConnection& operator=(const NonblockingConnection&) = delete;
    NonblockingConnection(NonblockingConnection&& other) noexcept 
        : fd_(other.fd_), rx_buf_(std::move(other.rx_buf_)), tx_buf_(std::move(other.tx_buf_)),
          rx_offset_(other.rx_offset_), tx_offset_(other.tx_offset_),
          rx_state_(other.rx_state_), expected_payload_len_(other.expected_payload_len_) {
        other.fd_ = -1;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }

    IoStatus read_nonblocking() {
        while (true) {
            compact_rx();
            size_t old_size = rx_buf_.size();
            rx_buf_.resize(old_size + 4096);

            ssize_t n = ::read(fd_, rx_buf_.data() + old_size, 4096);
            if (n > 0) {
                rx_buf_.resize(old_size + static_cast<size_t>(n));
                continue;
            }
            rx_buf_.resize(old_size);

            if (n == 0) return IoStatus::PeerClosed;
            if (errno == EINTR) continue;
            if (errno == EAGAIN || errno == EWOULDBLOCK) return IoStatus::WantRead;
            return IoStatus::Error;
        }
    }

    template <typename Callback>
    bool parse_frames(Callback&& on_frame) {
        while (true) {
            size_t available = rx_buf_.size() - rx_offset_;

            if (rx_state_ == ParserState::ReadHeader) {
                if (available < sizeof(uint32_t)) return true;
                uint32_t net_len = 0;
                std::memcpy(&net_len, rx_buf_.data() + rx_offset_, sizeof(uint32_t));
                expected_payload_len_ = ntohl(net_len);
                rx_offset_ += sizeof(uint32_t);

                if (expected_payload_len_ > MaxPayloadSize) return false;
                rx_state_ = ParserState::ReadPayload;
                available = rx_buf_.size() - rx_offset_;
            }

            if (rx_state_ == ParserState::ReadPayload) {
                if (available < expected_payload_len_) return true;
                std::span<const std::byte> payload(
                    reinterpret_cast<const std::byte*>(rx_buf_.data() + rx_offset_),
                    expected_payload_len_
                );
                on_frame(payload);
                rx_offset_ += expected_payload_len_;

                rx_state_ = ParserState::ReadHeader;
                expected_payload_len_ = 0;
            }
        }
    }

    bool enqueue_message(std::span<const std::byte> payload) {
        if (payload.size() > MaxPayloadSize) return false;
        compact_tx();

        uint32_t net_len = htonl(static_cast<uint32_t>(payload.size()));
        const auto* len_bytes = reinterpret_cast<const uint8_t*>(&net_len);
        tx_buf_.insert(tx_buf_.end(), len_bytes, len_bytes + sizeof(uint32_t));

        const auto* payload_bytes = reinterpret_cast<const uint8_t*>(payload.data());
        tx_buf_.insert(tx_buf_.end(), payload_bytes, payload_bytes + payload.size());
        return true;
    }

    IoStatus flush_write() {
        while (tx_offset_ < tx_buf_.size()) {
            size_t to_write = tx_buf_.size() - tx_offset_;
            ssize_t n = ::write(fd_, tx_buf_.data() + tx_offset_, to_write);

            if (n > 0) {
                tx_offset_ += static_cast<size_t>(n);
                continue;
            }
            if (errno == EINTR) continue;
            if (errno == EAGAIN || errno == EWOULDBLOCK) return IoStatus::WantWrite;
            return IoStatus::Error;
        }
        compact_tx();
        return IoStatus::Ok;
    }

private:
    void compact_rx() {
        if (rx_offset_ == 0) return;
        if (rx_offset_ >= rx_buf_.size()) {
            rx_buf_.clear();
        } else {
            rx_buf_.erase(rx_buf_.begin(), rx_buf_.begin() + static_cast<std::ptrdiff_t>(rx_offset_));
        }
        rx_offset_ = 0;
    }

    void compact_tx() {
        if (tx_offset_ == 0) return;
        if (tx_offset_ >= tx_buf_.size()) {
            tx_buf_.clear();
        } else {
            tx_buf_.erase(tx_buf_.begin(), tx_buf_.begin() + static_cast<std::ptrdiff_t>(tx_offset_));
        }
        tx_offset_ = 0;
    }

    int fd_{-1};
    std::vector<uint8_t> rx_buf_;
    std::vector<uint8_t> tx_buf_;
    size_t rx_offset_{0};
    size_t tx_offset_{0};
    ParserState rx_state_{ParserState::ReadHeader};
    uint32_t expected_payload_len_{0};
};
```
:::

---

### Підводні камені та практичні правила

1. **Захист від монополізації потоку (*Fair Scheduling & Starvation*)**: якщо клієнт передає гігабайти даних на повній швидкості інтерфейсу, вичитування сокета у неперервному циклі `while(true)` може заблокувати робочий потік на сотні мілісекунд, не даючи процесору обробляти інші клієнтські дескриптори. У промислових подієвих циклах встановлюють квоту (наприклад, не більше 64 КБ або 16 системних викликів `read()` за одну подію), після чого сокет повертають у кінець черги мультиплексора.
2. **Контроль зворотного тиску (*Backpressure*)**: якщо віддалений споживач повільно читає дані з мережі, вихідний буфер `tx_buf` на стороні сервера може неконтрольовано розростатися при кожному виклику `enqueue_message()`. Сервер зобов'язаний встановлювати поріг високої позначки (*High Watermark*, наприклад, 256 КБ): при його перевищенні сервер тимчасово знімає сокет із реєстрації на читання (`EPOLLIN`), примушуючи віддаленого клієнта зменшити темп передачі.
3. **Очищення дескриптора при закритті**: якщо виклик `conn_read_nonblocking()` повертає `IO_PEER_CLOSED`, це свідчить про отримання TCP-пакета `FIN`. Спроба подальшого читання завжди повертатиме `0`, тому сокет необхідно негайно видалити з контексту мультиплексора (`epoll_ctl(..., EPOLL_CTL_DEL)`) та закрити дескриптор.
