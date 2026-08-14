# ⚙️ Моніторинг термальних зон та керування тротлінгом через sysfs й Netlink

У цій практичній вставці розглядається створення повноцінної консольної утиліти простору користувача для асинхронного моніторингу подій перегріву ядра Linux. Програма поєднує два класичні механізми взаємодії з ядром: текстовий інтерфейс віртуальної файлової системи sysfs та бінарний подійний протокол Generic Netlink.

## Архітектурний задум та системні виклики

При проектуванні системних демонів моніторингу температури (наприклад, для серверних стійок, високопродуктивних кластерів або вбудованих Linux-пристроїв) використання суто текстового опитування файлів у `/sys/class/thermal/` створює відчутні накладні витрати. Кожне зчитування файлу `temp` вимагає системного виклику `open()`, виконання операції `read()`, перетворення текстового рядка на число в ядрі та закриття файлового дескриптора `close()`. За наявності десятків термальних зон таке опитування кілька разів на секунду призводить до непотрібного навантаження на процесор та викликає додаткове споживання енергії.

Для оптимізації цього процесу сучасна архітектура системних демонів розгортається у дві фази:

1. **Фаза початкової інспекції (sysfs):** Під час старту програма одноразово сканує директорію `/sys/class/thermal/`, зчитує типи термальних зон (`type`), номінальні температури (`temp`), активні регулятори (`policy`) та наявні пристрої охолодження (`cooling_device*`). Це дозволяє сформувати внутрішнє дерево об'єктів у пам'яті програми.
2. **Фаза асинхронного спостереження (Generic Netlink):** Після ініціалізації програма відкриває спеціалізований сокет `AF_NETLINK` з протоколом `NETLINK_GENERIC`, підписується на мультикаст-групу подій ядра `"event"` та переходить у режим очікування подій через виклик `recv()` або подійний цикл `epoll()`. Коли температура кристаллу перетинає порогові точки спрацьовування (`trip points`), ядро самостійно надсилає асинхронний бінарний кадр Netlink.

---

## Деталізація протоколу Netlink та розбір бінарних структур

Сокетний протокол Netlink працює як асоційована двостороння шина між простором ядра та простором користувача. Повідомлення Generic Netlink складаються з кількох вкладених рівнів заголовків з обов'язковим вирівнюванням по 4-байтовій межі:

- **`struct nlmsghdr` (Netlink Header):** Базовий заголовок мережевого кадру Netlink. Містить загальну довжину кадру `nlmsg_len`, тип повідомлення `nlmsg_type` (наприклад, ідентифікатор сімейства `THERMAL_GENL_FAMILY_NAME`), прапори `nlmsg_flags` та порядковий номер пакета `nlmsg_seq`.
- **`struct genlmsghdr` (Generic Netlink Header):** Заголовок підсистеми Generic Netlink. Містить числову команду події `cmd` (наприклад, `THERMAL_GENL_EVENT_TZ_TRIP_UP` або `THERMAL_GENL_EVENT_CPU_CAPABILITY_CHANGE`) та версію протоколу.
- **Послідовність атрибутів `struct nlattr` (TLV):** За заголовком генерується список вкладених атрибутів типу Type-Length-Value. Кожен атрибут містить тип `nla_type` та довжину `nla_len`. Корисне навантаження включає унікальний ідентифікатор зони (`THERMAL_GENL_ATTR_TZ_ID`), виміряну температуру (`THERMAL_GENL_ATTR_TZ_TEMP` у m°C) та індекс точок спрацьовування.

### Буферизація та обробка сплесків подій

При створенні виклик `socket(AF_NETLINK, SOCK_RAW, NETLINK_GENERIC)` створює сокетний буфер прийому. Під час масованого теплового тротлінгу багатьох ядер процесора ядро може генерувати сплески подій. Якщо простір користувача не встигає зчитувати дані з сокета, ядро повертає помилку `ENOBUFS` (No buffer space available). Для запобігання втраті повідомлень у промислових демонах застосовують збільшення сокетного буфера за допомогою виклику `setsockopt(fd, SOL_SOCKET, SO_RCVBUF, &buf_size, sizeof(buf_size))`.

---

## Простеження через ftrace та tracepoints ядра

Окрім прямої обробки подій через Netlink, розробники драйверів та системні інженери можуть простежувати внутрішню динаміку термального фреймворку через вбудовані точки трасування ядра (tracepoints).

У під системі `thermal` реалізовано наступні основні точки трасування:
- `thermal_zone_trip`: Фіксує оцінку точки спрацьовування та результат порівняння температури.
- `thermal_power_allocator`: Фіксує вихідні значення PID-контролера, розрахований бюджет потужності `P_alloc` та частки `P_granted` для кожного актора.
- `thermal_power_cpu_get_power` / `thermal_power_cpu_limit`: Фіксує запити та обмеження частоти процесорних ядер.

Для активації трасування у реальному часі без написання коду використовується інструмент `trace-cmd`:

```bash
# Активація трасування термальних подій ядра
sudo trace-cmd record -e thermal -e thermal_power_allocator

# Перегляд зібраних подій трасування
sudo trace-cmd report
```

Або через прямо зчитування подій з віртуальної файлової системи `tracefs`:

```bash
echo 1 > /sys/kernel/tracing/events/thermal/enable
cat /sys/kernel/tracing/trace_pipe
```

---

## Архітектура демона користувацького рівня `thermald`

На настільних ПК та ноутбуках архітектури Intel за термальну політику відповідає демон `thermald`. Він взаємодіє з ядром через регулятор `user_space` та розширені драйвери прошивки Intel DPTF (Dynamic Platform and Thermal Framework) та ACPI INT3400.

Демон `thermald` будується за наступною схемою:
1. Зчитує конфігураційний XML-файл `/etc/thermald/thermal-conf.xml`, де визначено специфічні для конкретної моделі ноутбука матриці термочутливості.
2. Переводить термальні зони процесора у регулятор `user_space`.
3. Підписується на Thermal Netlink сокет для миттєвого відстеження перегріву.
4. При отриманні подій перегріву прямим записом в атрибути `cur_state` пристроїв охолодження або через D-Bus виклики повертає систему у безпечний термальний коридор.

---

## Порівняння підходів у C та C++20

Вихідний код представлено у вигляді двох ідіоматичних варіантів реалізації:

- **Реалізація мовою C:** Використовує низькорівневі системні виклики POSIX, ручне керування файловими дескрипторами, розбір бінарних структур `struct nlmsghdr` та `struct genlmsghdr` за допомогою стандартних макросів ядра `NLMSG_OK`, `NLMSG_DATA`, `RTA_OK` та `RTA_NEXT`.
- **Реалізація мовою C++20:** Застосовує паттерн RAII (Resource Acquisition Is Initialization) для гарантованого закриття сокетного дескриптора при виході з області видимості, обгортку над файловими потоками `std::ifstream`, роботу зі шляхами файлової системи `std::filesystem::path`, безпечну обробку помилок через винятки `std::system_error` та типізовані контейнери `std::vector` і `std::optional` без використання сирих покажчиків чи ручного виділення пам'яті.

## Вихідний код програми

:::tabs
```c
/* thermal_monitor.c — Системний монітор термальних подій мовою C (POSIX & Netlink API) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/genetlink.h>
#include <linux/thermal.h>

#define BUFFER_SIZE 8192

/* Зчитування текстового атрибута з sysfs */
static int read_sysfs_string(const char *path, char *buf, size_t size) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) return -1;

    ssize_t bytes = read(fd, buf, size - 1);
    close(fd);
    if (bytes <= 0) return -1;

    buf[bytes] = '\0';
    char *newline = strchr(buf, '\n');
    if (newline) *newline = '\0';
    return 0;
}

/* Зчитування температури зони у градусах Цельсія */
static double read_zone_temperature(int zone_id) {
    char path[256];
    char buf[32];
    snprintf(path, sizeof(path), "/sys/class/thermal/thermal_zone%d/temp", zone_id);
    
    if (read_sysfs_string(path, buf, sizeof(buf)) == 0) {
        long temp_mC = atol(buf);
        return temp_mC / 1000.0;
    }
    return -1.0;
}

/* Створення та прив'язка Netlink-сокета */
static int create_thermal_netlink_socket(void) {
    int fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_GENERIC);
    if (fd < 0) {
        perror("Помилка створення AF_NETLINK сокета");
        return -1;
    }

    /* Збільшення сокетного буфера прийому для запобігання ENOBUFS */
    int rcvbuf = 256 * 1024;
    setsockopt(fd, SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf));

    struct sockaddr_nl local;
    memset(&local, 0, sizeof(local));
    local.nl_family = AF_NETLINK;
    local.nl_groups = 1; /* Підписка на мультикаст події */

    if (bind(fd, (struct sockaddr *)&local, sizeof(local)) < 0) {
        perror("Помилка прив'язки bind() сокета Netlink");
        close(fd);
        return -1;
    }

    return fd;
}

/* Розбір бінарного термального повідомлення Netlink */
static void parse_thermal_nl_message(const char *buf, ssize_t len) {
    struct nlmsghdr *nlh = (struct nlmsghdr *)buf;

    while (NLMSG_OK(nlh, len)) {
        if (nlh->nlmsg_type == NLMSG_ERROR) {
            fprintf(stderr, "Отримано повідомлення про помилку Netlink\n");
            break;
        }

        struct genlmsghdr *gnlh = (struct genlmsghdr *)NLMSG_DATA(nlh);
        printf("[Netlink Event] Команда події: 0x%X (Версія %d)\n",
               gnlh->cmd, gnlh->version);

        /* Інспекція додаткових атрибутів події */
        struct nlattr *attr = (struct nlattr *)((char *)gnlh + GENL_HDRLEN);
        int attr_len = nlh->nlmsg_len - NLMSG_HDRLEN - GENL_HDRLEN;

        while (RTA_OK(attr, attr_len)) {
            if (attr->nla_type == THERMAL_GENL_ATTR_TZ_TEMP) {
                int temp_mC = *(int *)RTA_DATA(attr);
                printf("  -> Подія температури зони: %.2f °C\n", temp_mC / 1000.0);
            }
            attr = RTA_NEXT(attr, attr_len);
        }

        nlh = NLMSG_NEXT(nlh, len);
    }
}

int main(void) {
    printf("=== Термальний монітор ядра Linux (C POSIX / Netlink) ===\n\n");

    /* 1. Сканування перших двох термальних зон у sysfs */
    for (int zone = 0; zone < 2; zone++) {
        char type_path[256], type_buf[64];
        snprintf(type_path, sizeof(type_path), "/sys/class/thermal/thermal_zone%d/type", zone);

        if (read_sysfs_string(type_path, type_buf, sizeof(type_buf)) == 0) {
            double temp_C = read_zone_temperature(zone);
            printf("Зона %d [%s]: поточна температура = %.2f °C\n", zone, type_buf, temp_C);
        }
    }

    /* 2. Ініціалізація Netlink-сокета для асинхронного відстеження */
    int nl_fd = create_thermal_netlink_socket();
    if (nl_fd < 0) {
        fprintf(stderr, "Продовження роботи у режимі лише sysfs...\n");
        return EXIT_FAILURE;
    }

    printf("\nОчікування асинхронних подій перегріву ядра (Ctrl+C для виходу)...\n");
    char buffer[BUFFER_SIZE];

    while (1) {
        ssize_t bytes_received = recv(nl_fd, buffer, sizeof(buffer), 0);
        if (bytes_received < 0) {
            if (errno == EINTR) continue;
            perror("Помилка читання recv() з Netlink-сокета");
            break;
        }

        parse_thermal_nl_message(buffer, bytes_received);
    }

    close(nl_fd);
    return EXIT_SUCCESS;
}
```
```cpp
// thermal_monitor.cpp — Ідіоматичний системний термальний монітор мовою C++20 (RAII, Expected/Exceptions, StringView)
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <optional>
#include <filesystem>
#include <system_error>
#include <array>
#include <cstdint>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/genetlink.h>
#include <linux/thermal.h>

namespace fs = std::filesystem;

// RAII-обгортка для управління ресурсом мережевого сокета Netlink
class ThermalNetlinkSocket {
public:
    explicit ThermalNetlinkSocket(uint32_t multicast_groups = 1) {
        m_fd = ::socket(AF_NETLINK, SOCK_RAW, NETLINK_GENERIC);
        if (m_fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to create AF_NETLINK socket");
        }

        // Збільшення розміру буфера прийому для запобігання втраті подій
        int rcvbuf = 256 * 1024;
        ::setsockopt(m_fd, SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf));

        struct sockaddr_nl local{};
        local.nl_family = AF_NETLINK;
        local.nl_groups = multicast_groups;

        if (::bind(m_fd, reinterpret_cast<struct sockaddr*>(&local), sizeof(local)) < 0) {
            ::close(m_fd);
            throw std::system_error(errno, std::generic_category(), "Failed to bind Netlink socket");
        }
    }

    ~ThermalNetlinkSocket() noexcept {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
    }

    // Заборона копіювання для збереження суворої власності RAII
    ThermalNetlinkSocket(const ThermalNetlinkSocket&) = delete;
    ThermalNetlinkSocket& operator=(const ThermalNetlinkSocket&) = delete;

    // Дозвіл переміщення
    ThermalNetlinkSocket(ThermalNetlinkSocket&& other) noexcept : m_fd(other.m_fd) {
        other.m_fd = -1;
    }

    [[nodiscard]] int get_fd() const noexcept { return m_fd; }

    [[nodiscard]] std::vector<std::uint8_t> receive_event(std::size_t buffer_size = 8192) const {
        std::vector<std::uint8_t> buffer(buffer_size);
        ssize_t bytes = ::recv(m_fd, buffer.data(), buffer.size(), 0);
        
        if (bytes < 0) {
            throw std::system_error(errno, std::generic_category(), "recv() failed");
        }
        
        buffer.resize(static_cast<std::size_t>(bytes));
        return buffer;
    }

private:
    int m_fd{-1};
};

// Клас інспекції атрибутів термальних зон у sysfs
class SysfsThermalInspector {
public:
    static std::optional<double> read_temperature(unsigned int zone_id) {
        const auto path = fs::path("/sys/class/thermal") / ("thermal_zone" + std::to_string(zone_id)) / "temp";
        std::ifstream file(path);
        if (!file.is_open()) return std::nullopt;

        long temp_mC = 0;
        if (file >> temp_mC) {
            return static_cast<double>(temp_mC) / 1000.0;
        }
        return std::nullopt;
    }

    static std::optional<std::string> read_zone_type(unsigned int zone_id) {
        const auto path = fs::path("/sys/class/thermal") / ("thermal_zone" + std::to_string(zone_id)) / "type";
        std::ifstream file(path);
        if (!file.is_open()) return std::nullopt;

        std::string type;
        std::getline(file, type);
        return type;
    }
};

// Головний клас керування моніторингом
class ThermalMonitorApp {
public:
    void run_sysfs_scan() const {
        std::cout << "=== Сканування термальних зон у sysfs ===\n";
        for (unsigned int zone = 0; zone < 4; ++zone) {
            const auto type = SysfsThermalInspector::read_zone_type(zone);
            const auto temp = SysfsThermalInspector::read_temperature(zone);

            if (type && temp) {
                std::cout << "Зона " << zone << " [" << *type << "]: "
                          << *temp << " °C\n";
            }
        }
    }

    void start_event_loop() const {
        try {
            ThermalNetlinkSocket nl_socket(1);
            std::cout << "\n[Netlink] Асинхронний монітор запущеній. Очікування подій ядра...\n";

            while (true) {
                const auto raw_data = nl_socket.receive_event();
                process_netlink_payload(raw_data);
            }
        } catch (const std::exception& ex) {
            std::cerr << "[Помилка моніторингу]: " << ex.what() << '\n';
        }
    }

private:
    void process_netlink_payload(const std::vector<std::uint8_t>& payload) const {
        if (payload.size() < sizeof(struct nlmsghdr)) return;

        const auto* nlh = reinterpret_cast<const struct nlmsghdr*>(payload.data());
        if (nlh->nlmsg_type == NLMSG_ERROR) return;

        const auto* gnlh = reinterpret_cast<const struct genlmsghdr*>(NLMSG_DATA(nlh));
        std::cout << "[C++ Event] Команда події ядра: 0x" << std::hex 
                  << static_cast<int>(gnlh->cmd) << std::dec << '\n';
    }
};

int main() {
    std::cout << "=== Термальний монітор ядра Linux (C++20 RAII & Netlink) ===\n\n";

    ThermalMonitorApp app;
    app.run_sysfs_scan();
    app.start_event_loop();

    return 0;
}
```
:::

## Інструкція зі збірки та запуску

Для компіляції обох прикладів у системі мають бути встановлені стандартний інструментарій компіляції (`gcc`, `g++`) та заголовні файли ядра Linux (`linux-headers`).

```bash
# Компіляція прикладу мовою C
gcc -O2 -Wall thermal_monitor.c -o thermal_monitor_c

# Компіляція прикладу мовою C++20
g++ -O2 -Wall -std=c++20 thermal_monitor.cpp -o thermal_monitor_cpp

# Запуск з правами суперкористувача (необхідно для приєднання до сокета Netlink)
sudo ./thermal_monitor_c
```
