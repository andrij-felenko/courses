# ⚙️ Практична реалізація SocketCAN парсера та фільтра в C і C++

Побудова програмного забезпечення для роботи з мережею CAN у системі Linux за допомогою системного API SocketCAN охоплює створення сирого сокета `SOCK_RAW`, прив'язку до мережевого інтерфейсу, розрахунок та встановлення апаратних фільтрів маскування ідентифікаторів, а також читання, парсинг і декодування вхідних кадрів у мовах C та C++.

---

## 1. Архітектура SocketCAN у системі Linux

На відміну від класичних послідовних портів UART (де програма відкриває файловий пристрій `/dev/ttyUSB0` та самостійно парсить байтовий потік без допомоги ОС), ядро Linux реалізує шину CAN як повноцінний мережевий стековий інтерфейс (Network Protocol Family `PF_CAN` / `AF_CAN`).

```
+-------------------------------------------------------+
|  Прикладний процес (User Space: C / C++)             |
+-------------------------------------------------------+
|  Системні виклики POSIX: socket(), bind(), read()     |
+-------------------------------------------------------+
|  Мережевий сокет ядра Linux: af_can.c, raw.c          |
+-------------------------------------------------------+
|  Апаратний контролер (STM32 bxCAN, mcp251x)           |
+-------------------------------------------------------+
```

Переваги підходу SocketCAN для розробника:
- **Багатозадачний доступ:** Кілька незалежних процесів операційної системи можуть одночасно відкривати сокети й читати або надсилати кадри CAN через один фізичний інтерфейс. Ядро самостійно маршрутизує кадри між буферами процесів.
- **Стандартне POSIX API:** Робота з CAN здійснюється через звичні системні виклики `socket()`, `bind()`, `read()`, `write()`, `select()`, `poll()` та `epoll()`.
- **Ядерна фільтрація:** Фільтрація непотрібних ідентифікаторів виконується безпосередньо в середовищі ядра (або передається апаратному acceptance-фільтру контролера), виключаючи зайві контекстні перемикання між ядром та користувацьким простором.

---

## 2. Кроки реалізації: від сокета до декодування

Для створення парсера необхідно виконати п'ять послідовних кроків розробки:

1. **Створення сокета:** Викликається функція `socket(PF_CAN, SOCK_RAW, CAN_RAW)`, де параметр `CAN_RAW` забезпечує прямий доступ до сирих кадрів даних без додаткових вищих протокольних обгорток.
2. **Прив'язка до мережевого інтерфейсу:** За допомогою системного виклику `ioctl(s, SIOCGIFINDEX, &ifr)` ім'я пристрою (наприклад, `"vcan0"`) перетворюється на числовий індекс `ifr_ifindex`, після чого сокет прив'язується через системний виклик `bind()`.
3. **Налаштування масок фільтрації:** За замовчуванням сокет приймає всі кадри. Через `setsockopt(s, SOL_CAN_RAW, CAN_RAW_FILTER, ...)` задається масив `struct can_filter`. Умова проходження кадру описується формулою `(received_can_id & filter.can_mask) == (filter.can_id & filter.can_mask)`. Через `CAN_RAW_ERR_FILTER` вмикають прийом кадрів помилок.
4. **Зчитування структури кадру:** Системний виклик `read(s, &frame, sizeof(struct can_frame))` повертає бінарну структуру `struct can_frame`. Перевірка повернутого обсягу байтів гарантує цілісність отриманого кадру. Для вимірювання затримок доставки застосовують `recvmsg()` з аналізом часових міток.
5. **Розпакування прапорців та ідентифікатора:** Поле `can_id` об'єднує числовий ID та прапорці стану. Побітові операції `&` з масками `CAN_EFF_FLAG` (29-біт ID), `CAN_RTR_FLAG` (запит даних) та `CAN_SFF_MASK` / `CAN_EFF_MASK` виділяють очищене значення ідентифікатора та його тип.

---

## 3. Сирцевий код: реалізація C та C++

У наведених нижче вкладках представлено два варіанти реалізації: класичний C-код із використанням системних POSIX-викликів та ідіоматичний C++20 код із застосуванням концепції RAII, винятків, мовних типів `std::span` та `std::optional`.

:::tabs
```c
/* Файл: socketcan_demo.c
   Компіляція: gcc -Wall -Wextra socketcan_demo.c -o socketcan_demo */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <linux/can.h>
#include <linux/can/raw.h>
#include <linux/can/error.h>

int main(void) {
    int s;
    struct sockaddr_can addr;
    struct ifreq ifr;
    struct can_frame frame;

    /* 1. Створення сирого сокета CAN */
    if ((s = socket(PF_CAN, SOCK_RAW, CAN_RAW)) < 0) {
        perror("Помилка відкриття сокета CAN");
        return EXIT_FAILURE;
    }

    /* 2. Пошук індексу мережевого інтерфейсу за іменем "vcan0" або "can0" */
    const char *ifname = "vcan0";
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);
    ifr.ifr_name[IFNAMSIZ - 1] = '\0';

    if (ioctl(s, SIOCGIFINDEX, &ifr) < 0) {
        perror("Помилка ioctl (SIOCGIFINDEX)");
        close(s);
        return EXIT_FAILURE;
    }

    /* 3. Прив'язка сокета до інтерфейсу */
    memset(&addr, 0, sizeof(addr));
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;

    if (bind(s, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("Помилка bind сокета");
        close(s);
        return EXIT_FAILURE;
    }

    /* 4. Налаштування апаратного фільтра кадрових ID.
       Приймаємо лише ID = 0x123 та маскуємо ID 0x200..0x20F */
    struct can_filter rfilter[2];
    rfilter[0].can_id   = 0x123;
    rfilter[0].can_mask = CAN_SFF_MASK; /* Точний збіг 11 бітів */

    rfilter[1].can_id   = 0x200;
    rfilter[1].can_mask = 0x7F0;        /* Перевіряти біти 0x7F0 (від 0x200 до 0x20F) */

    if (setsockopt(s, SOL_CAN_RAW, CAN_RAW_FILTER, &rfilter, sizeof(rfilter)) < 0) {
        perror("Помилка встановлення фільтра setsockopt");
        close(s);
        return EXIT_FAILURE;
    }

    /* Налаштування маски кадрів помилок шини */
    can_err_mask_t err_mask = (CAN_ERR_CRIT | CAN_ERR_BUSOFF);
    setsockopt(s, SOL_CAN_RAW, CAN_RAW_ERR_FILTER, &err_mask, sizeof(err_mask));

    printf("SocketCAN успішно ініціалізовано на %s. Очікування кадрів...\n", ifname);

    /* 5. Цикл прийому та декодування кадрів */
    for (int i = 0; i < 5; ++i) {
        ssize_t nbytes = read(s, &frame, sizeof(struct can_frame));
        if (nbytes < 0) {
            perror("Помилка читання кадру з сокета");
            break;
        }

        if (nbytes < (ssize_t)sizeof(struct can_frame)) {
            fprintf(stderr, "Помилка: отримано неповний кадр CAN (%zd байтів)\n", nbytes);
            continue;
        }

        /* Парсинг ідентифікатора та прапорців */
        can_id_t raw_id = frame.can_id;
        int is_extended = (raw_id & CAN_EFF_FLAG) != 0;
        int is_rtr      = (raw_id & CAN_RTR_FLAG) != 0;
        int is_error    = (raw_id & CAN_ERR_FLAG) != 0;

        uint32_t clean_id = is_extended ? (raw_id & CAN_EFF_MASK) : (raw_id & CAN_SFF_MASK);

        printf("[%s] ID: 0x%08X | DLC: %d | Тип: %s%s\n  Дані: ",
               ifname, clean_id, frame.can_dlc,
               is_extended ? "EFF (29-bit)" : "SFF (11-bit)",
               is_rtr ? " [RTR]" : (is_error ? " [ERR]" : ""));

        if (!is_rtr) {
            for (int j = 0; j < frame.can_dlc; ++j) {
                printf("%02X ", frame.data[j]);
            }
        }
        printf("\n");
    }

    close(s);
    return EXIT_SUCCESS;
}
```
```cpp
// Файл: socketcan_demo.cpp
// Компіляція: g++ -std=c++20 -Wall -Wextra socketcan_demo.cpp -o socketcan_demo

#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <optional>
#include <system_error>
#include <cstring>
#include <cstdint>
#include <unistd.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <linux/can.h>
#include <linux/can/raw.h>
#include <linux/can/error.h>

namespace can {

enum class FrameType {
    Standard11Bit,
    Extended29Bit,
    RemoteRequest,
    ErrorFrame
};

struct Message {
    uint32_t id{0};
    FrameType type{FrameType::Standard11Bit};
    std::vector<uint8_t> data;
};

// RAII обгортка для управління файловим дескриптором сокета CAN
class Socket {
public:
    explicit Socket(std::string_view interface_name) {
        fd_ = ::socket(PF_CAN, SOCK_RAW, CAN_RAW);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити сокет CAN");
        }

        struct ifreq ifr{};
        std::strncpy(ifr.ifr_name, interface_name.data(), IFNAMSIZ - 1);
        if (::ioctl(fd_, SIOCGIFINDEX, &ifr) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "Не вдалося отримати індекс інтерфейсу");
        }

        struct sockaddr_can addr{};
        addr.can_family = AF_CAN;
        addr.can_ifindex = ifr.ifr_ifindex;

        if (::bind(fd_, reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "Не вдалося прив'язати сокет");
        }
    }

    ~Socket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    // Заборона копіювання (RAII ресурс)
    Socket(const Socket&) = delete;
    Socket& operator=(const Socket&) = delete;

    // Дозвіл переміщення
    Socket(Socket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    Socket& operator=(Socket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    void set_filters(std::span<const struct can_filter> filters) {
        if (::setsockopt(fd_, SOL_CAN_RAW, CAN_RAW_FILTER, filters.data(), filters.size_bytes()) < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося встановити маску фільтрації");
        }
    }

    void set_error_filter(can_err_mask_t err_mask) {
        if (::setsockopt(fd_, SOL_CAN_RAW, CAN_RAW_ERR_FILTER, &err_mask, sizeof(err_mask)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося встановити маску кадрів помилок");
        }
    }

    std::optional<Message> receive() {
        struct can_frame frame{};
        ssize_t nbytes = ::read(fd_, &frame, sizeof(struct can_frame));

        if (nbytes < static_cast<ssize_t>(sizeof(struct can_frame))) {
            return std::nullopt;
        }

        Message msg;
        const can_id_t raw_id = frame.can_id;

        if (raw_id & CAN_ERR_FLAG) {
            msg.type = FrameType::ErrorFrame;
            msg.id = raw_id & CAN_ERR_MASK;
        } else if (raw_id & CAN_RTR_FLAG) {
            msg.type = FrameType::RemoteRequest;
            msg.id = (raw_id & CAN_EFF_FLAG) ? (raw_id & CAN_EFF_MASK) : (raw_id & CAN_SFF_MASK);
        } else if (raw_id & CAN_EFF_FLAG) {
            msg.type = FrameType::Extended29Bit;
            msg.id = raw_id & CAN_EFF_MASK;
        } else {
            msg.type = FrameType::Standard11Bit;
            msg.id = raw_id & CAN_SFF_MASK;
        }

        if (msg.type != FrameType::RemoteRequest) {
            const uint8_t dlc = std::min<uint8_t>(frame.can_dlc, 8);
            msg.data.assign(frame.data, frame.data + dlc);
        }

        return msg;
    }

private:
    int fd_{-1};
};

} // namespace can

int main() {
    try {
        can::Socket can_sock("vcan0");

        // Налаштування фільтрів
        std::vector<struct can_filter> filters(2);
        filters[0] = {.can_id = 0x123, .can_mask = CAN_SFF_MASK};
        filters[1] = {.can_id = 0x200, .can_mask = 0x7F0};
        can_sock.set_filters(filters);
        can_sock.set_error_filter(CAN_ERR_CRIT | CAN_ERR_BUSOFF);

        std::cout << "C++ SocketCAN слухач активовано. Очікування повідомлень...\n";

        for (int i = 0; i < 5; ++i) {
            auto msg_opt = can_sock.receive();
            if (!msg_opt) continue;

            const auto& msg = *msg_opt;
            std::cout << "Отримано ID: 0x" << std::hex << msg.id << std::dec;

            switch (msg.type) {
                case can::FrameType::Standard11Bit: std::cout << " [11-bit Std]"; break;
                case can::FrameType::Extended29Bit: std::cout << " [29-bit Ext]"; break;
                case can::FrameType::RemoteRequest: std::cout << " [RTR Request]"; break;
                case can::FrameType::ErrorFrame:    std::cout << " [Error Frame]"; break;
            }

            std::cout << " | Байт: " << msg.data.size() << " | Дані: ";
            for (uint8_t b : msg.data) {
                std::cout << std::hex << (int)b << " ";
            }
            std::cout << std::dec << "\n";
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

---

## 4. Інженерні пастки реалізації та аналіз крайових випадків

Під час розробки високозавантажених промислових та автомобільних систем на базі SocketCAN розробники стикаються з шістьма категоріями крайових випадків:

### Порядок байтів у корисній підкладці (Endianness)

Системне поле `can_id` у SocketCAN передається в хостовому порядку байтів (Host Byte Order). Проте самі бати корисної підкладки в масиві `data[]` у більшості автомобільних протоколів (CANopen, SAE J1939) упаковуються за специфікаціями Little-Endian (Intel) або Big-Endian (Motorola). Необхідно виконувати побайтові зсуви та маскування для виділення 16-бітних та 32-бітних значень.

### Переповнення приймального буфера ядра (Socket Buffer Overflow)

При високій швидкості шини (500 кбіт/с або 1 Мбіт/с) та щільності трафіку буфер сокета в ядрі Linux може переповнюватися, спричиняючи втрату кадрів. Для запобігання втратам збільшують буфер викликом `setsockopt(s, SOL_SOCKET, SO_RCVBUF, &rcvbuf_size, sizeof(rcvbuf_size))` та переводять сокет у неблокуючий режим із подієвим мультиплексуванням `epoll`.

### Обробка помилок передачі та переповнення апаратного TX-буфера

У неблокуючому режимі (`O_NONBLOCK`) виклик `write()` при переповненні апаратного буфера повертає `-1` із кодом `errno == ENOBUFS` або `EAGAIN`. Програма повинна реалізувати буферну чергу відправки в оперативній пам'яті та чекати готовності сокета на запис.

### Глибокий розбір обробки кадрів помилок CAN (Error Frames)

Ядро Linux за замовчуванням приглушує апаратні помилки. Для їх отримання налаштовують маску `setsockopt(s, SOL_CAN_RAW, CAN_RAW_ERR_FILTER, &err_mask, sizeof(err_mask))`. Отриманий кадр має прапорець `CAN_ERR_FLAG` у полі `can_id`.

Критичні стани апаратного контролера розшифровуються прапорцями:
- **`CAN_ERR_CRIT`:** Фіксує критичні проблеми контролера або трансивера (стан Error Passive при лічильниках помилок понад 127). Деталі описуються в байті `frame.data[1]` (`CAN_ERR_CRIT_TX_PASSIVE`, `CAN_ERR_CRIT_RX_PASSIVE`).
- **`CAN_ERR_BUSOFF`:** Фіксує перехід контролера в стан Bus-Off (коли лічильник помилок передачі TEC > 255). Вузлу повністю забороняється передача. Програма зафіксовує аварію і після усунення фізичного замикання виконує відновлення (автоматичний перезапуск ядра або команда `ip link set can0 type can restart`).

Байт `frame.data[2]` розкриває тип протокольної помилки (Bit, Form, Stuff або CRC error), а байти `frame.data[6]` та `frame.data[7]` містять значення лічильників помилок TEC та REC.

### Вимірювання затримок доставки через SO_TIMESTAMP та SO_TIMESTAMPING

Для детермінованих систем важлива часова прив'язка кадрів. Виклик `read()` не фіксує момент надходження кадру в мережевий стек.

Для вимірювання затримок сокет налаштовується прапорцем:
`int enable = 1; setsockopt(s, SOL_SOCKET, SO_TIMESTAMP, &enable, sizeof(enable));`

Замість `read()` застосовують `recvmsg()` із передачею структури `struct msghdr` та буфера `struct cmsghdr`. Ітерація за допомогою макросів `CMSG_FIRSTHDR` та `CMSG_NXTHDR` виділяє елемент із рівня `SOL_SOCKET` та типу `SCM_TIMESTAMP` (або `SO_TIMESTAMPING` для апаратних міток). Повернута структура `struct timeval` фіксує момент надходження кадру перериванням NIC, що дозволяє обчислити затримку доставки `Δt = t_sys - t_frame`.

### Тестування та робочий процес із candump і can-utils у Linux

Для налагодження без фізичного заліза створюють віртуальну шину `vcan0` (`sudo modprobe vcan; sudo ip link add dev vcan0 type vcan; sudo ip link set vcan0 up`).

Для діагностики та тестування мереж CAN у Linux використовують інструменти `can-utils`:
- **`candump`:** Перегляд і фільтрація трафіку в реальному часі. Прапорець `-t a` виводить абсолютний час, `-t z` — відносний інтервал, `-l` записує лог у файл. Приклади фільтрації: `candump vcan0,0x123:0x7FF` (лише ID 0x123) або `candump any,0:0#R` (перехоплення виключно кадрів помилок).
- **`cansend`:** Генерація поодиноких кадрів (наприклад, `cansend vcan0 123#11223344` або `cansend vcan0 1F345678#8877665544332211` для 29-бітного ID).
- **`canplayer`:** Відтворення збережених дампів (`canplayer -I candump-2026-08-13.log vcan0=can0`), що забезпечує Hardware-in-the-Loop (HIL) тестування.
- **`cangen`:** Навантажувальне тестування шини згенерованим трафіком (`cangen vcan0 -g 10 -I 0x123`).
