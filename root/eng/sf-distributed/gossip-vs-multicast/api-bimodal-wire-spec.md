# 📋 Специфікація мережевого протоколу Bimodal Wire Protocol

Ця специфікація описує бінарний протокол рівня передавання даних **Bimodal Wire Protocol (BWP)**, який поєднує високошвидкісну ненадійну групову розсилку через IP Multicast та епідемічне довиправлення втрачених пакетів через Gossip. Протокол призначений для кластерних систем із високою інтенсивністю повідомлень (ринкові котирування, телеметрія, реплікація логів), де класичний TCP або NAK-орієнтований Multicast викликають перевантаження мережі.

---

## 1. Загальна модель кадрів і типи повідомлень

Усі пакети BWP передаються у форматі Big-Endian (Network Byte Order) у корисній дейтаграмі UDP. Максимальний розмір кадру обмежений величиною MTU локальної мережі (стандартно 1472 байти для IPv4 Ethernet без фрагментації: 1500 байтів MTU мінус 20 байтів IP-заголовка та 8 байтів UDP-заголовка). Фрагментація IP-пакетів категорично заборонена (`DF=1`, Don't Fragment), оскільки втрата одного фрагмента призводить до відкидання всієї дейтаграми, посилюючи навантаження на підсистему відновлення.

Протокол визначає три типи повідомлень:

```
+---------------+-------+--------------------+----------------------------------------+
| Тип (Type)    | Код   | Транспортний канал | Призначення                            |
+---------------+-------+--------------------+----------------------------------------+
| BWP_DATA      | 0x01  | IP Multicast (UDP) | Основний потік прикладних даних        |
| BWP_DIGEST    | 0x02  | Unicast (UDP)      | Періодичний дайджест отриманих номерів |
| BWP_REPAIR    | 0x03  | Unicast (UDP)      | Точковий запит / доставка втрати       |
+---------------+-------+--------------------+----------------------------------------+
```

Розподіл транспортних каналів базується на асиметрії завдань: первинні дані транслюються без затримок усім учасникам одночасно через апаратний Multicast, тоді як обмін дайджестами та запити на ретрансляцію відбуваються точково (Unicast) між випадковими вузлами оверлею, не створюючи широкомовного шуму для решти кластера.--------+-------+-------------------------------------------------------------+
| Тип (Type)    | Код   | Транспортний канал | Призначення                            |
+---------------+-------+--------------------+----------------------------------------+
| BWP_DATA      | 0x01  | IP Multicast (UDP) | Основний потік прикладних даних        |
| BWP_DIGEST    | 0x02  | Unicast (UDP)      | Періодичний дайджест отриманих номерів |
| BWP_REPAIR    | 0x03  | Unicast (UDP)      | Точковий запит / доставка втрати       |
+---------------+-------+--------------------+----------------------------------------+
```

---

## 2. Бінарний формат заголовка та корисного навантаження

Кожен пакет починається з фіксованого 16-байтового заголовка `bwp_header_t`.

### Структура базового заголовка BWP

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Magic (0x4257)       |  Version (1)  |  Type (0x01)  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           Source ID                           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Sequence Number                         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Payload Length        |            Reserved           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

**Опис полів заголовка:**
- `Magic` (16 бітів): Фіксований маркер протоколу `0x4257` (ASCII-символи `'B'`, `'W'`). Пакети з іншим магічним числом негайно відкидаються.
- `Version` (8 бітів): Номер версії протоколу. Поточна версія — `1`.
- `Type` (8 бітів): Тип пакета (`0x01` — DATA, `0x02` — DIGEST, `0x03` — REPAIR).
- `Source ID` (32 біти): Унікальний числовий ідентифікатор вузла-відправника або генератора потоку (вузол, що формує послідовність).
- `Sequence Number` (32 біти): Монотонно зростаючий порядковий номер повідомлення для даного `Source ID`. Починається з `1`.
- `Payload Length` (16 бітів): Розмір прикладного тіла даних у байтах (без урахування 16 байтів заголовка).
- `Reserved` (16 бітів): Зарезервовано для прапорців майбутніх розширень (вирівнювання до 32-бітної межі, має містити `0x0000`).

---

## 3. Формат дайджесту пліток (BWP_DIGEST)

Пакет `BWP_DIGEST` передається одноадресно (Unicast) під час кожного раунду анти-ентропії між випадково обраними парами вузлів. Він інформує сусіда про діапазон послідовностей, якими володіє відправник.

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       bwp_header_t                            |
|               (Type = 0x02, Source ID = Sender)               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Target Source ID                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                      Low Sequence Number                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                      High Sequence Number                     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                      Loss Bitmask (32 bits)                   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

**Семантика полів дайджесту:**
- `Target Source ID` (32 біти): Ідентифікатор джерела даних, стан якого описується цим дайджестом.
- `Low Sequence Number` (32 біти): Найменший номер у локальному кільцевому буфері відправника дайджесту (нижня межа вікна зберігання).
- `High Sequence Number` (32 біти): Найбільший отриманий номер для даного `Target Source ID`.
- `Loss Bitmask` (32 біти): Бітова маска наявності останніх 32 пакетів, що передують `High Sequence Number`. Біт зі значенням `1` означає успішне отримання, біт `0` — пропущений (втрачений) пакет, який потребує ремонту.

---

## 4. Формат запиту та відповіді на відновлення (BWP_REPAIR)

Пакет `BWP_REPAIR` використовується як для запиту відсутнього пакета (Request), так і для передавання відновлених даних (Response).

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       bwp_header_t                            |
|             (Type = 0x03, Payload Length = N)                 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Opcode (1B)  |   Flags (1B)  |            Reserved           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Target Source ID                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Requested Sequence Number                  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                  Data Payload (лише у відповіді)              |
|                               ...                             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

**Опис полів ремонту:**
- `Opcode` (8 бітів):
  - `0x01` (`BWP_OP_REQUEST`): Вузол просить сусіда надіслати вказаний `Sequence Number`. Поле даних порожнє (`Payload Length = 12`).
  - `0x02` (`BWP_OP_RESPONSE`): Відповідь із відновленим тілом повідомлення. Поле даних містить оригінальний payload.
  - `0x03` (`BWP_OP_NOT_FOUND`): Повідомлення про те, що запитаний номер уже витіснено з кільцевого буфера сусіда (Retention Exceeded).
- `Flags` (8 бітів): Керуючі прапорці. Біт 0 (`0x01`) встановлюється, якщо це терміновий запит після кількох пропущених раундів.

---

## 5. Опції сокетів POSIX та мережева конфігурація

Для коректної роботи BWP операційна система вимагає налаштування спеціальних опцій на сокетах Multicast та Unicast:

```
+---------------------+-------------------+----------------------------------------------------+
| Опція сокета        | Рівень            | Інженерне призначення                              |
+---------------------+-------------------+----------------------------------------------------+
| SO_REUSEADDR        | SOL_SOCKET        | Дозволяє кільком процесам слухати спільний порт    |
| IP_ADD_MEMBERSHIP   | IPPROTO_IP        | Приєднання до групи розсилки IGMP на інтерфейсі    |
| IP_MULTICAST_TTL    | IPPROTO_IP        | Обмеження радіуса розсилки (1 = LAN, >1 = роутери) |
| IP_MULTICAST_LOOP   | IPPROTO_IP        | Вимикання лупбеку копій на власний сокет (0 = OFF) |
| IP_MULTICAST_IF     | IPPROTO_IP        | Вибір фізичного мережевого інтерфейсу для виходу   |
| SO_RCVBUF           | SOL_SOCKET        | Розширення системного буфера прийому до 8–16 МБ    |
+---------------------+-------------------+----------------------------------------------------+
```

### Коректне встановлення опцій сокета мовами C та C++

:::tabs
```c
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>

int setup_bwp_multicast_socket(const char *mcast_ip, const char *local_ip, uint16_t port) {
    int fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) return -1;

    int reuse = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));

    /* Розширення буфера прийому до 8 МБ для захисту від сплесків */
    int rcvbuf = 8 * 1024 * 1024;
    setsockopt(fd, SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf));

    struct sockaddr_in bind_addr;
    memset(&bind_addr, 0, sizeof(bind_addr));
    bind_addr.sin_family = AF_INET;
    bind_addr.sin_port = htons(port);
    bind_addr.sin_addr.s_addr = htonl(INADDR_ANY);

    if (bind(fd, (struct sockaddr *)&bind_addr, sizeof(bind_addr)) < 0) {
        close(fd);
        return -2;
    }

    /* Приєднання до групи IGMP через вказаний локальний інтерфейс */
    struct ip_mreq mreq;
    memset(&mreq, 0, sizeof(mreq));
    inet_pton(AF_INET, mcast_ip, &mreq.imr_multiaddr);
    inet_pton(AF_INET, local_ip, &mreq.imr_interface);

    if (setsockopt(fd, IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof(mreq)) < 0) {
        close(fd);
        return -3;
    }

    /* Вимкнення отримання власних пакетів на хості */
    unsigned char loop = 0;
    setsockopt(fd, IPPROTO_IP, IP_MULTICAST_LOOP, &loop, sizeof(loop));

    return fd;
}
```
```cpp
#include <string_view>
#include <system_error>
#include <expected>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>

class UniqueSocket {
    int fd_{-1};
public:
    explicit UniqueSocket(int fd) noexcept : fd_(fd) {}
    ~UniqueSocket() noexcept {
        if (fd_ >= 0) ::close(fd_);
    }
    UniqueSocket(const UniqueSocket&) = delete;
    UniqueSocket& operator=(const UniqueSocket&) = delete;
    UniqueSocket(UniqueSocket&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    UniqueSocket& operator=(UniqueSocket&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] int release() noexcept {
        int temp = fd_;
        fd_ = -1;
        return temp;
    }
};

std::expected<UniqueSocket, std::error_code> make_bwp_multicast_socket(
    std::string_view mcast_ip,
    std::string_view local_ip,
    uint16_t port
) noexcept {
    int fd = ::socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    UniqueSocket sock(fd);

    int reuse = 1;
    ::setsockopt(sock.get(), SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));

    int rcvbuf = 8 * 1024 * 1024;
    ::setsockopt(sock.get(), SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf));

    sockaddr_in bind_addr{};
    bind_addr.sin_family = AF_INET;
    bind_addr.sin_port = htons(port);
    bind_addr.sin_addr.s_addr = htonl(INADDR_ANY);

    if (::bind(sock.get(), reinterpret_cast<sockaddr*>(&bind_addr), sizeof(bind_addr)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    ip_mreq mreq{};
    if (::inet_pton(AF_INET, mcast_ip.data(), &mreq.imr_multiaddr) <= 0 ||
        ::inet_pton(AF_INET, local_ip.data(), &mreq.imr_interface) <= 0) {
        return std::unexpected(std::make_error_code(std::errc::invalid_argument));
    }

    if (::setsockopt(sock.get(), IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof(mreq)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    unsigned char loop = 0;
    ::setsockopt(sock.get(), IPPROTO_IP, IP_MULTICAST_LOOP, &loop, sizeof(loop));

    return sock;
}
```
:::

---

## 6. Скінченний автомат стану вузла (Node State Machine)

Кожен вузол кластера, що приймає або генерує BWP-трафік, функціонує відповідно до детермінованого скінченного автомата з шістьма станами:

```
        ┌────────────────┐
        │  1. BWP_INIT   │
        └───────┬────────┘
                │  Створення сокетів та виклик IP_ADD_MEMBERSHIP
                ▼
        ┌────────────────┐
        │ 2. BWP_JOINING │◄──────────────────────────┐
        └───────┬────────┘                           │
                │  Отримано перший BWP_DATA          │ Невідновна
                ▼                                    │ прогалина
        ┌────────────────┐                           │ (Unrecoverable)
        │ 3. BWP_STREAM  │                           │
        └───────┬────────┘                           │
                │  Виявлено прогалину (Seq N+2 > N)  │
                ▼                                    │
        ┌────────────────┐                           │
        │ 4. BWP_GAP_REQ │                           │
        └───────┬────────┘                           │
                │  Надіслано BWP_OP_REQUEST          │
                ▼                                    │
        ┌────────────────┐      BWP_OP_NOT_FOUND     │
        │ 5. BWP_REPAIR  ├───────────────────────────┘
        └───────┬────────┘
                │  Отримано BWP_OP_RESPONSE з даними
                ▼
        ┌────────────────┐
        │ 6. BWP_COMMITTED
        └───────┬────────┘
                │  Передача у прикладний рівень і повернення до BWP_STREAM
                └────────────────────────► [ Стан BWP_STREAM ]
```

### Таблиця переходів та умови спрацьовування

```
+----------------+--------------------------+-------------------+---------------------------------------------------+
| Початковий стан| Вхідна подія             | Наступний стан    | Виконувана дія                                    |
+----------------+--------------------------+-------------------+---------------------------------------------------+
| BWP_INIT       | socket() + bind() OK     | BWP_JOINING       | Реєстрація в групі IGMP через IP_ADD_MEMBERSHIP   |
| BWP_JOINING    | Перший пакет BWP_DATA    | BWP_STREAM        | Ініціалізація Seq_last = pkt.seq, фіксація даних  |
| BWP_STREAM     | pkt.seq == Seq_last + 1  | BWP_STREAM        | Seq_last++, передача даних у чергу обробки        |
| BWP_STREAM     | pkt.seq > Seq_last + 1   | BWP_GAP_REQ       | Буферизація pkt у черзі, формування запиту ремонту|
| BWP_GAP_REQ    | Таймер раунду пліток     | BWP_REPAIR        | Надсилання BWP_OP_REQUEST на k випадкових вузлів  |
| BWP_REPAIR     | BWP_OP_RESPONSE отримано | BWP_STREAM        | Заповнення прогалини, впорядкований дренаж черги  |
| BWP_REPAIR     | BWP_OP_NOT_FOUND (ліміт) | BWP_STREAM (DROP) | Фіксація GAP_ERROR, Seq_last = pkt.seq, скид черги|
+----------------+--------------------------+-------------------+---------------------------------------------------+
```

---

## 7. Серіалізація та валідація кадру (Wire Codecs)

Функції кодування та декодування виконують обов'язкову перевірку розміру буфера, магічного числа та перетворення порядку байтів між вузлом та мережею.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <arpa/inet.h>

#define BWP_MAGIC 0x4257
#define BWP_TYPE_DATA   0x01
#define BWP_TYPE_DIGEST 0x02
#define BWP_TYPE_REPAIR 0x03

typedef struct __attribute__((packed)) {
    uint16_t magic;
    uint8_t  version;
    uint8_t  type;
    uint32_t source_id;
    uint32_t seq_num;
    uint16_t payload_len;
    uint16_t reserved;
} bwp_header_t;

bool bwp_encode_header(uint8_t type, uint32_t src_id, uint32_t seq,
                       uint16_t payload_len, uint8_t *out_buf, size_t buf_size) {
    if (!out_buf || buf_size < sizeof(bwp_header_t)) return false;

    bwp_header_t *hdr = (bwp_header_t *)out_buf;
    hdr->magic       = htons(BWP_MAGIC);
    hdr->version     = 1;
    hdr->type        = type;
    hdr->source_id   = htonl(src_id);
    hdr->seq_num     = htonl(seq);
    hdr->payload_len = htons(payload_len);
    hdr->reserved    = 0;
    return true;
}

bool bwp_decode_header(const uint8_t *in_buf, size_t in_len,
                       bwp_header_t *out_hdr) {
    if (!in_buf || !out_hdr || in_len < sizeof(bwp_header_t)) return false;

    const bwp_header_t *raw = (const bwp_header_t *)in_buf;
    if (ntohs(raw->magic) != BWP_MAGIC || raw->version != 1) {
        return false;
    }

    out_hdr->magic       = ntohs(raw->magic);
    out_hdr->version     = raw->version;
    out_hdr->type        = raw->type;
    out_hdr->source_id   = ntohl(raw->source_id);
    out_hdr->seq_num     = ntohl(raw->seq_num);
    out_hdr->payload_len = ntohs(raw->payload_len);
    out_hdr->reserved    = ntohs(raw->reserved);

    /* Перевірка цілісності: сумарний розмір не повинен перевищувати дейтаграму */
    if (sizeof(bwp_header_t) + out_hdr->payload_len > in_len) {
        return false;
    }
    return true;
}
```
```cpp
#include <cstdint>
#include <span>
#include <expected>
#include <system_error>
#include <bit>
#include <cstring>
#include <arpa/inet.h>

inline constexpr uint16_t BwpMagic = 0x4257;

enum class BwpType : uint8_t {
    Data   = 0x01,
    Digest = 0x02,
    Repair = 0x03
};

struct BwpHeader {
    uint16_t magic{BwpMagic};
    uint8_t  version{1};
    BwpType  type{BwpType::Data};
    uint32_t source_id{0};
    uint32_t seq_num{0};
    uint16_t payload_len{0};
    uint16_t reserved{0};
};

enum class BwpWireError {
    BufferTooSmall = 1,
    InvalidMagic,
    UnsupportedVersion,
    CorruptedLength
};

struct BwpWireErrorCategory : std::error_category {
    [[nodiscard]] const char* name() const noexcept override { return "bwp_wire"; }
    [[nodiscard]] std::string message(int c) const override {
        switch (static_cast<BwpWireError>(c)) {
            case BwpWireError::BufferTooSmall: return "Buffer too small for BWP header";
            case BwpWireError::InvalidMagic: return "Invalid BWP magic signature";
            case BwpWireError::UnsupportedVersion: return "Unsupported BWP protocol version";
            case BwpWireError::CorruptedLength: return "Payload length exceeds received buffer";
            default: return "Unknown BWP wire error";
        }
    }
};

inline const BwpWireErrorCategory& bwp_category() noexcept {
    static BwpWireErrorCategory category;
    return category;
}

inline std::error_code make_error_code(BwpWireError e) noexcept {
    return {static_cast<int>(e), bwp_category()};
}

std::expected<size_t, std::error_code> encode_bwp_header(
    const BwpHeader& hdr,
    std::span<uint8_t> dst
) noexcept {
    if (dst.size() < 16) {
        return std::unexpected(make_error_code(BwpWireError::BufferTooSmall));
    }

    uint16_t magic_be   = htons(hdr.magic);
    uint8_t  ver        = hdr.version;
    uint8_t  type_raw   = static_cast<uint8_t>(hdr.type);
    uint32_t src_be     = htonl(hdr.source_id);
    uint32_t seq_be     = htonl(hdr.seq_num);
    uint16_t len_be     = htons(hdr.payload_len);
    uint16_t res_be     = htons(hdr.reserved);

    std::memcpy(dst.data() + 0, &magic_be, 2);
    dst[2] = ver;
    dst[3] = type_raw;
    std::memcpy(dst.data() + 4, &src_be, 4);
    std::memcpy(dst.data() + 8, &seq_be, 4);
    std::memcpy(dst.data() + 12, &len_be, 2);
    std::memcpy(dst.data() + 14, &res_be, 2);

    return 16;
}

std::expected<BwpHeader, std::error_code> decode_bwp_header(
    std::span<const uint8_t> src
) noexcept {
    if (src.size() < 16) {
        return std::unexpected(make_error_code(BwpWireError::BufferTooSmall));
    }

    uint16_t magic_be;
    std::memcpy(&magic_be, src.data() + 0, 2);
    if (ntohs(magic_be) != BwpMagic) {
        return std::unexpected(make_error_code(BwpWireError::InvalidMagic));
    }

    if (src[2] != 1) {
        return std::unexpected(make_error_code(BwpWireError::UnsupportedVersion));
    }

    BwpHeader hdr;
    hdr.magic   = ntohs(magic_be);
    hdr.version = src[2];
    hdr.type    = static_cast<BwpType>(src[3]);

    uint32_t src_be, seq_be;
    uint16_t len_be, res_be;
    std::memcpy(&src_be, src.data() + 4, 4);
    std::memcpy(&seq_be, src.data() + 8, 4);
    std::memcpy(&len_be, src.data() + 12, 2);
    std::memcpy(&res_be, src.data() + 14, 2);

    hdr.source_id   = ntohl(src_be);
    hdr.seq_num     = ntohl(seq_be);
    hdr.payload_len = ntohs(len_be);
    hdr.reserved    = ntohs(res_be);

    if (16 + static_cast<size_t>(hdr.payload_len) > src.size()) {
        return std::unexpected(make_error_code(BwpWireError::CorruptedLength));
    }

    return hdr;
}
```
:::

---

## 8. Коди помилок та обробка виняткових ситуацій

```
+---------------------+-------+-----------------------------------------------------------------+
| Код помилки (Enum)  | Знач. | Причина та рекомендована реакція системи                        |
+---------------------+-------+-----------------------------------------------------------------+
| BWP_ERR_MEMBERSHIP  | -101  | Не вдалося приєднатися до IGMP групи (перевірити маршрут/шлюз)  |
| BWP_ERR_BUF_OVERRUN | -102  | Переповнення системного буфера SO_RCVBUF (збільшити розмір ОС)  |
| BWP_ERR_SEQ_WRAPPED | -103  | Переповнення 32-бітного лічильника (перезапуск сесії потоку)    |
| BWP_ERR_UNRECOVER   | -104  | Прогалина перевищує вікно зберігання сусіда (скид до поточного) |
| BWP_ERR_BAD_MAGIC   | -105  | Сторонній або пошкоджений UDP пакет (скидання без обробки)      |
+---------------------+-------+-----------------------------------------------------------------+
```

### Інваріанти надійності

1. **Монотонність доставки:** Прикладний рівень отримує повідомлення строго за зростанням `Sequence Number`. Якщо виявлено прогалину (`Sequence N + 2` прийшов раніше `N + 1`), пакет `N + 2` буферизується в черзі очікування (Staging Buffer), а фоновий потік надсилає `BWP_OP_REQUEST` для отримання `N + 1`.
2. **Захист від дублікатів:** Пакет, чий `Sequence Number` менший або дорівнює останньому зафіксованому (Committed) номеру, негайно відкидається без генерації помилок.
3. **Обмеження ретрансляцій:** Вузол надсилає не більше одного повторного запиту на один і той самий `Sequence Number` за один раунд пліток, щоб запобігти каскадним штормам під час високої затримки.
4. **Вичерпання вікна утримання:** Якщо сусід відповідає кодом `BWP_OP_NOT_FOUND`, вузол фіксує невідновну втрату (Unrecoverable Gap), сповіщає прикладний рівень подією `GAP_ERROR` і скидає стан до поточного максимального номера (Fast-Forward).
