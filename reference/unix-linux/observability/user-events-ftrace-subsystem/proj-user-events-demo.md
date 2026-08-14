# ⚙️ Практикум: створення та відправка користувацьких подій у ftrace мовами C та C++

Цей практикум є покроковим розбором створення виробничого інструментарію спостережуваності на базі підсистеми User Events ядра Linux. У матеріалі наведено повністю робочі, високопродуктивні приклади програм мовами C та C++, детально проаналізовано алгоритм налаштування зв'язку з ядром, механіку безвикликової перевірки стану через спільну пам'ять (`mmap`), технологію пакування бінарного payload із статичними та динамічними полями, а також надано покрокові інструкції з тестування, фільтрації та перехоплення згенерованих подій за допомогою утиліт `ftrace` та `bpftrace`.

## 1. Архітектурне завдання та розробка специфікації

Перед написанням коду визначимо прикладу задачу. Увага приділяється створенню сервісу моніторингу HTTP-запитів вебсервера.
Необхідно зареєструвати в ядрі Linux користувацьку подію з назвою `app_http_request`.

Згідно з вимогами до телеметрії, подія повинна містити три ключових параметри:
1. `status_code` (`u32`) — числовий код HTTP-відповіді (наприклад, 200 OK, 404 Not Found або 500 Internal Server Error);
2. `latency_ns` (`u64`) — повна тривалість обробки запиту сервером у наносекундах;
3. `url` (`__data_loc char[]`) — динамічний рядок змінної довжини, що містить URI запитаного ресурсу.

### Схема роботи програми

Програма повинна виконувати наступний алгоритм:
1. Відкрити керівний файл `/sys/kernel/tracing/user_events_data`.
2. Зареєструвати специфікацію події через керівний виклик `ioctl(DIAG_IOCSREG)`.
3. Отримати від ядра вихідні значення `status_index` та `write_index`.
4. Виконати відображення сторінки статусу ядра в пам'ять процесу через системний виклик `mmap()`.
5. У гарячому циклі обробки регулярно перевіряти байт статусу `status_page[status_index]`.
6. Якщо байт дорівнює `0` (трасування вимкнено), програма робить пропуск без виконання системних викликів.
7. Якщо байт ненульовий (трасування увімкнено), програма формує вектор `iovec` та викликає `writev()`.
8. Під час отримання сигналів завершення (SIGINT/SIGTERM) програма повинна коректно скасувати відображення пам'яті (`munmap`) та закрити файловий дескриптор.

## 2. Реалізація мовами C та C++

Нижче наведено дві повноцінні реалізації завдання.
У версії на C++ застосовано концепцію RAII (Resource Acquisition Is Initialization): створення та закриття системних ресурсів повністю автоматизовано у конструкторі та деструкторі класу `UserEventsHandle`. Замість використання сирих вказівників на char застосовано безпечний та високошвидкісний `std::string_view`, а для збірки вектора використано `std::array<::iovec, 3>`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/uio.h>
#include <stdint.h>
#include <signal.h>
#include <errno.h>

#ifndef DIAG_IOCSREG
#define DIAG_IOC_MAGIC 0x82
#define DIAG_IOCSREG _IOWR(DIAG_IOC_MAGIC, 0, struct user_reg)
#endif

struct user_reg {
    uint32_t size;
    uint8_t  enable_bit;
    uint8_t  enable_size;
    uint16_t flags;
    uint64_t name_args;
    uint32_t status_index;
    uint32_t write_index;
};

#define USER_EVENT_LOC(offset, len) (((uint32_t)(len) << 16) | ((uint32_t)(offset) & 0xFFFF))

static volatile int keep_running = 1;

static void handle_sigint(int sig) {
    (void)sig;
    keep_running = 0;
}

int main(void) {
    signal(SIGINT, handle_sigint);
    signal(SIGTERM, handle_sigint);

    const char *device_path = "/sys/kernel/tracing/user_events_data";
    int fd = open(device_path, O_RDWR);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", device_path, strerror(errno));
        fprintf(stderr, "Перевірте, чи завантажено модуль та чи є права root/CAP_PERFMON.\n");
        return EXIT_FAILURE;
    }

    /* 1. Реєстрація події з динамічним рядком */
    const char *event_spec = "app_http_request u32 status_code; u64 latency_ns; __data_loc char[] url";
    struct user_reg reg;
    memset(&reg, 0, sizeof(reg));
    reg.size = sizeof(reg);
    reg.name_args = (uint64_t)(uintptr_t)event_spec;

    if (ioctl(fd, DIAG_IOCSREG, &reg) < 0) {
        fprintf(stderr, "Помилка ioctl(DIAG_IOCSREG): %s\n", strerror(errno));
        close(fd);
        return EXIT_FAILURE;
    }

    printf("[C] Подію зареєстровано успішно!\n");
    printf("    write_index  = %u\n", reg.write_index);
    printf("    status_index = %u\n", reg.status_index);

    /* 2. Відображення сторінки статусу в пам'ять (mmap) */
    long page_size = sysconf(_SC_PAGESIZE);
    char *status_page = (char *)mmap(NULL, (size_t)page_size, PROT_READ, MAP_SHARED, fd, 0);
    if (status_page == MAP_FAILED) {
        fprintf(stderr, "Помилка mmap: %s\n", strerror(errno));
        close(fd);
        return EXIT_FAILURE;
    }

    uint32_t counter = 0;
    while (keep_running) {
        /* Zero-Overhead перевірка у користувацькому просторі */
        if (status_page[reg.status_index] != 0) {
            const char *url_str = "/api/v1/user/checkout";
            uint16_t url_len = (uint16_t)strlen(url_str) + 1; /* Включаючи нуль-термінатор */

            /* Фіксована частина payload */
            struct {
                uint32_t status_code;
                uint32_t padding; /* Вирівнювання u64 */
                uint64_t latency_ns;
                uint32_t url_loc;
            } __attribute__((packed)) fixed_header;

            fixed_header.status_code = (counter % 5 == 0) ? 500 : 200;
            fixed_header.padding = 0;
            fixed_header.latency_ns = 1500000ULL + (counter * 10000ULL);
            
            /* Зсув від початку fixed_header (16 байтів) */
            uint16_t offset = (uint16_t)sizeof(fixed_header);
            fixed_header.url_loc = USER_EVENT_LOC(offset, url_len);

            /* Збірка iovec: 
             * iov[0] - 4 байти write_index
             * iov[1] - fixed_header
             * iov[2] - динамічні дані рядка url
             */
            struct iovec iov[3];
            iov[0].iov_base = &reg.write_index;
            iov[0].iov_len = sizeof(reg.write_index);

            iov[1].iov_base = &fixed_header;
            iov[1].iov_len = sizeof(fixed_header);

            iov[2].iov_base = (void *)url_str;
            iov[2].iov_len = url_len;

            ssize_t ret = writev(fd, iov, 3);
            if (ret < 0) {
                fprintf(stderr, "Помилка writev: %s\n", strerror(errno));
            } else {
                printf("[C] [ПОДІЯ НАДІСЛАНА] #%u status=%u latency=%lu ns url=%s (bytes=%zd)\n",
                       counter, fixed_header.status_code, fixed_header.latency_ns, url_str, ret);
            }
        } else {
            printf("[C] [ПРОПУСК] Подію вимкнено у ftrace (status_index byte is 0)\n");
        }

        counter++;
        sleep(1);
    }

    printf("\nЗавершення роботи. Звільнення ресурсів...\n");
    munmap(status_page, (size_t)page_size);
    close(fd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <vector>
#include <array>
#include <cstdint>
#include <cstring>
#include <csignal>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/uio.h>
#include <system_error>

#ifndef DIAG_IOCSREG
#define DIAG_IOC_MAGIC 0x82
#define DIAG_IOCSREG _IOWR(DIAG_IOC_MAGIC, 0, struct user_reg)
#endif

struct user_reg {
    std::uint32_t size;
    std::uint8_t  enable_bit;
    std::uint8_t  enable_size;
    std::uint16_t flags;
    std::uint64_t name_args;
    std::uint32_t status_index;
    std::uint32_t write_index;
};

constexpr std::uint32_t make_user_event_loc(std::uint16_t offset, std::uint16_t len) noexcept {
    return (static_cast<std::uint32_t>(len) << 16) | (static_cast<std::uint32_t>(offset) & 0xFFFF);
}

namespace {
    volatile std::sig_atomic_t g_stop_requested = 0;
}

class UserEventsHandle {
    int fd_{-1};
    char* status_map_{static_cast<char*>(MAP_FAILED)};
    std::size_t map_size_{0};
    user_reg reg_{};

public:
    explicit UserEventsHandle(std::string_view event_spec) {
        const char* dev_path = "/sys/kernel/tracing/user_events_data";
        fd_ = ::open(dev_path, O_RDWR);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити user_events_data");
        }

        reg_.size = sizeof(reg_);
        reg_.name_args = reinterpret_cast<std::uint64_t>(event_spec.data());

        if (::ioctl(fd_, DIAG_IOCSREG, &reg_) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "ioctl(DIAG_IOCSREG) failed");
        }

        map_size_ = static_cast<std::size_t>(::sysconf(_SC_PAGESIZE));
        void* ptr = ::mmap(nullptr, map_size_, PROT_READ, MAP_SHARED, fd_, 0);
        if (ptr == MAP_FAILED) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "mmap status page failed");
        }
        status_map_ = static_cast<char*>(ptr);
    }

    ~UserEventsHandle() noexcept {
        if (status_map_ != MAP_FAILED) {
            ::munmap(status_map_, map_size_);
        }
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    UserEventsHandle(const UserEventsHandle&) = delete;
    UserEventsHandle& operator=(const UserEventsHandle&) = delete;

    [[nodiscard]] bool is_enabled() const noexcept {
        return status_map_[reg_.status_index] != 0;
    }

    [[nodiscard]] std::uint32_t write_index() const noexcept {
        return reg_.write_index;
    }

    [[nodiscard]] std::uint32_t status_index() const noexcept {
        return reg_.status_index;
    }

    bool trace_http_request(std::uint32_t status_code, std::uint64_t latency_ns, std::string_view url) {
        if (!is_enabled()) {
            return false;
        }

        struct alignas(4) FixedPayload {
            std::uint32_t status_code;
            std::uint32_t padding;
            std::uint64_t latency_ns;
            std::uint32_t url_loc;
        } header{};

        std::uint16_t url_len = static_cast<std::uint16_t>(url.size()) + 1;
        header.status_code = status_code;
        header.padding = 0;
        header.latency_ns = latency_ns;
        header.url_loc = make_user_event_loc(sizeof(FixedPayload), url_len);

        std::uint32_t w_idx = reg_.write_index;

        std::array<::iovec, 3> iov{};
        iov[0].iov_base = &w_idx;
        iov[0].iov_len = sizeof(w_idx);

        iov[1].iov_base = &header;
        iov[1].iov_len = sizeof(header);

        iov[2].iov_base = const_cast<char*>(url.data());
        iov[2].iov_len = url_len;

        ssize_t written = ::writev(fd_, iov.data(), iov.size());
        return written > 0;
    }
};

int main() {
    std::signal(SIGINT, [](int) { g_stop_requested = 1; });
    std::signal(SIGTERM, [](int) { g_stop_requested = 1; });

    try {
        constexpr std::string_view spec = "app_http_request u32 status_code; u64 latency_ns; __data_loc char[] url";
        UserEventsHandle tracer(spec);

        std::cout << "[C++] Подію успішно зареєстровано!\n"
                  << "      write_index  = " << tracer.write_index() << "\n"
                  << "      status_index = " << tracer.status_index() << std::endl;

        std::uint32_t counter = 0;
        while (!g_stop_requested) {
            if (tracer.is_enabled()) {
                bool ok = tracer.trace_http_request(200, 1200000 + counter * 5000, "/api/v2/orders");
                if (ok) {
                    std::cout << "[C++] [ПОДІЯ НАДІСЛАНА] #" << counter << std::endl;
                }
            } else {
                std::cout << "[C++] [ПРОПУСК] Подію вимкнено (Zero-Overhead check)" << std::endl;
            }

            counter++;
            ::sleep(1);
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << std::endl;
        return EXIT_FAILURE;
    }

    std::cout << "Завершення роботи C++ програми." << std::endl;
    return EXIT_SUCCESS;
}
```
:::

## 3. Детальний аналіз реалізації та пасток коду

Під час розробки коду взаємодії з підсистемою User Events необхідно звернути увагу на декілька критичних моментів реалізації:

### Пастка 1: Вирівнювання 64-бітних цілих чисел (Memory Alignment)
У структурі `fixed_header` поле `latency_ns` має тип `uint64_t`. На 64-бітних архітектурах x86_64 компилятор C/C++ автоматично вирівнює 64-бітні поля по 8-байтній межі адреси. Оскільки перше поле `status_code` має тип `u32` (4 байти), компилятор вставляє 4 байти невидимого падінгу (`padding`) між `status_code` та `latency_ns`. Якщо не врахувати цей `padding` у структурі C або не вказати його явне заповнення, опис полів у файлі `format` ftrace розійдеться з реальним розташуванням байтів, і ядро виведе спотворені дані.

### Пастка 2: Нуль-термінатор у динамічних рядках `__data_loc`
Під час передачі динамічного рядка параметр `url_len` у локаторі `USER_EVENT_LOC` повинен враховувати кінцевий байт `\0`. Якщо передати `strlen(str)` замість `strlen(str) + 1`, ftrace прочитає рядок без завершального символу, що призведе до злиття сусідніх полів у логах.

### Пастка 3: Збереження вказівника string_view у C++
У версії на C++ параметр `url` у системному виклику `writev()` посилається на пам'ять `url.data()`. Необхідно гарантувати, що об'єкт `std::string_view` або `std::string` залишається валідним і не звільняється у пам'яті до завершення системного виклику `writev()`.

## 4. Покроковий практикум із запуску та верифікації

### Крок 1. Компіляція бінарних файлів

Скомпілюйте вихідні файли за допомогою компіляторів `gcc` та `g++`:

```bash
# Компіляція прикладу мовою C
gcc -O2 -Wall user_event_demo.c -o user_event_c

# Компіляція прикладу мовою C++ (потрібен стандарт C++20)
g++ -O2 -std=c++20 -Wall user_event_demo.cpp -o user_event_cpp
```

### Крок 2. Запуск демонстраційного процесу

Оскільки відкриття `/sys/kernel/tracing/user_events_data` вимагає привілеїв, запустіть згенерований бінарний файл за допомогою `sudo`:

```bash
sudo ./user_event_c
```

*Приклад термінального виводу:*
```text
[C] Подію зареєстровано успішно!
    write_index  = 1
    status_index = 0
[C] [ПРОПУСК] Подію вимкнено у ftrace (status_index byte is 0)
[C] [ПРОПУСК] Подію вимкнено у ftrace (status_index byte is 0)
```

Як видно з виводу, програма працює у фоновому циклі, але оскільки трасування вимкнено у ядрі, вона лише перевіряє байт статусу і виводить текстові сповіщення про пропуск, не виконуючи викликів `writev()`.

### Крок 3. Перевірка створення об'єктів у tracefs

Відкрийте друге вікно термінала і перевірте появу нової події у системі трасування ядра Linux:

```bash
ls -l /sys/kernel/tracing/events/user_events/app_http_request
```

У терміналі відобразяться автозгенеровані управляючі файли:
```text
-rw-r--r-- 1 root root 0 Aug 14 12:00 enable
-rw-r--r-- 1 root root 0 Aug 14 12:00 filter
-r--r--r-- 1 root root 0 Aug 14 12:00 format
-r--r--r-- 1 root root 0 Aug 14 12:00 id
```

Перевірте автоматично згенеровану ядром схему полів у файлі `format`:
```bash
cat /sys/kernel/tracing/events/user_events/app_http_request/format
```

### Крок 4. Активація трасування у ядрі

Увімкніть трасування нашої користувацької події, записавши значення `1` у управляючий файл `enable`:

```bash
echo 1 | sudo tee /sys/kernel/tracing/events/user_events/app_http_request/enable
```

Одразу після виконання цієї команди у першому вікні термінала програма помітить зміну байта у `status_page` і почне генерувати та надсилати пакети подій:

```text
[C] [ПОДІЯ НАДІСЛАНА] #5 status=500 latency=1550000 ns url=/api/v1/user/checkout (bytes=40)
[C] [ПОДІЯ НАДІСЛАНА] #6 status=200 latency=1560000 ns url=/api/v1/user/checkout (bytes=40)
```

### Крок 5. Перегляд траси у буфері ftrace

Зчитайте вміст кільцевого буфера ftrace:

```bash
sudo cat /sys/kernel/tracing/trace
```

*Результат у кільцевому буфері:*
```text
# TASK-PID    CPU#  TIMESTAMP  FUNCTION
# |     |      |      |           |
user_event_c-4012 [002] 12450.812301: app_http_request: status_code=200 latency_ns=1560000 url=/api/v1/user/checkout
user_event_c-4012 [002] 12451.812405: app_http_request: status_code=500 latency_ns=1570000 url=/api/v1/user/checkout
```

### Крок 6. Трасування та аналітика через bpftrace

Ви можете прив'язати eBPF-програму до зареєстрованої події у реальному часі:

```bash
sudo bpftrace -e '
tracepoint:user_events:app_http_request {
    printf("[%s] PID %d | Status: %d | Latency: %d ms | URL: %s\n",
           probe, pid, args->status_code, args->latency_ns / 1000000, str(args->url));
}'
```

Після виконання цієї команди `bpftrace` компілює BPF-байткод, завантажує його у ядро і прив'язує до нашої користувацької події. Ви побачите форматований вивід кожної події безперепосередньо в моменти виконання викликів `writev()`.
