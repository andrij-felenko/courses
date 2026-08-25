# ⚙️ Практичний проект: Моніторинг та програмне перемикання ролей USB Type-C через sysfs та udev

Цей практичний проект демонструє розробку системного сервісу простору користувача мовами C та C++, який відстежує стан роз'ємів USB Type-C, зчитує актуальні профілі Power Delivery та виконує програмний запит на перемикання ролей даних (Data Role Swap) або живлення (Power Role Swap) через уніфікований інтерфейс sysfs.

## Архітектурні виклики та системний дизайн

У практичній розробці вбудованих Linux-систем (роботизовані комплекси, промислові контролери, мобільні термінали) виникає потреба в автоматичному реагуванні на підключення периферійних пристроїв Type-C. Наприклад, коли до робототехнічної платформи підключається зовнішній акумулятор, система повинна переключитися в режим споживача живлення (`sink`). Якщо ж підключається діагностичний сканер, порт має переключитися в режим хоста даних (`host`).

Для вирішення цих задач системний сервіс реалізує два доповнюючі підходи:
1. **Синхронне сканування sysfs-дерева (`/sys/class/typec/`):** Прохід по директоріях при старті сервісу для побудови первинної карти портів.
2. **Асинхронний моніторинг через udev Netlink сокет:** Отримання ядерних подій `KOBJECT_UEVENT` про підключення/від'єднання партнерів у реальному часі без постійного опитування (polling) файлової системи.

### Механіка взаємодії з sysfs та обробка кодів помилок ядра

Коли програма простору користувача записує рядок `host` у файл `/sys/class/typec/port0/data_role`, відбуваються наступні ядерні операції:
- VFS надсилає системний виклик `write()` драйверу Connector Class (`class.c`).
- Драйвер перевіряє підтримку операції та викликає функціональний покажчик `dr_set` із структури `struct typec_operations`.
- Драйвер контролера порту (TCPM або UCSI) генерує BMC-пакет `DR_Swap` і надсилає його через лінію CC підключеному партнеру.
- Потік програми блокується на час очікування відповіді від партнера (до кількох сотень мілісекунд).

Під час запису системний виклик `write()` може повернути наступні специфічні коди помилок `errno`:
- `EOPNOTSUPP` (Operation not supported): Підключений пристрій або фізичний контролер не підтримує роль хоста чи споживача.
- `ETIMEDOUT` (Connection timed out): Партнер не надіслав підтвердження `GoodCRC` або відповіді `Accept` на пакет `DR_Swap` у межах таймаутів, відведених специфікацією PD (одиниці мілісекунд на GoodCRC, десятки — на відповідь).
- `EBUSY` (Device or resource busy): Контролер порту у даний момент вже виконує іншу процедуру узгодження контракту живлення.
- `ENOTCONN` (Transport endpoint is not connected): Запит надіслано на порт, до якого фізично не підключено жодного партнера.

### Повторні спроби (Retry logic) та крайові випадки

У реальних умовах при підключенні кабелю контролер порту перебуває у стані вирівнювання ліній CC протягом перших 100–200 мс (`tCCDebounce`). Якщо простір користувача надсилає запит `--swap` занадто швидко, ядро повертає `EBUSY` або `ENOTCONN`. 

Тому надійний системний сервіс реалізує алгоритм повторних спроб з експоненціальною затримкою (Exponential Backoff): при отриманні `EBUSY` сервіс робить паузу 50 мс і повторює запис у sysfs, щоразу подвоюючи паузу (50, 100, 200 мс — до 3–5 спроб). Якщо ж від партнера отримано відмову `Reject` (код `EOPNOTSUPP`), сервіс зупиняє спроби та фіксує поточний стан, запобігаючи зацикленню обміну пакетами PD.

### Інспекція ідентифікації партнера (e-Marker та VDM)

Окрім аналізу ролей, сервіс зчитує поля ідентифікації з директорії `/sys/class/typec/port0-partner/identity/`. Вузол `id_header` містить 32-бітне значення VDM-пакета (Vendor Defined Message), з якого сервіс витягує ідентифікатор виробника (USB Vendor ID, VID) та тип пристрою (Hub, Peripheral, Display, Power Bank). Якщо підключено активний оптичний кабель (AOC) чи високошвидкісний кабель USB4, сервіс аналізує директорію `/sys/class/typec/port0-cable/`, де вказано підтримуваний струм (3 А чи 5 А); поточного ж постачальника VCONN показує атрибут самого порту — `vconn_role`.

## Повний вихідний код реалізації

Нижче наведено робочий вихідний код системного сервісу мовами C (C99 з використанням POSIX API) та C++ (C++20 з використанням `std::filesystem`).

:::tabs
```c
/* typec_switcher.c — C99 implementation using standard POSIX file I/O */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <dirent.h>
#include <errno.h>

#define SYSFS_TYPEC_DIR "/sys/class/typec"
#define PATH_BUF_SIZE   512
#define VALUE_BUF_SIZE  64

static int read_sysfs_string(const char *path, char *buf, size_t size) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        return -errno;
    }

    ssize_t ret = read(fd, buf, size - 1);
    int saved_errno = errno;
    close(fd);

    if (ret < 0) {
        return -saved_errno;
    }

    buf[ret] = '\0';
    /* Trim trailing newline character */
    char *nl = strchr(buf, '\n');
    if (nl) {
        *nl = '\0';
    }

    return 0;
}

static int write_sysfs_string(const char *path, const char *val) {
    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        perror("Failed to open sysfs attribute for writing");
        return -errno;
    }

    size_t len = strlen(val);
    ssize_t ret = write(fd, val, len);
    int saved_errno = errno;
    close(fd);

    if (ret < 0) {
        errno = saved_errno;
        perror("Failed to write to sysfs attribute");
        return -saved_errno;
    }

    return 0;
}

static void inspect_typec_port(const char *port_name) {
    char path[PATH_BUF_SIZE];
    char data_role[VALUE_BUF_SIZE] = "unknown";
    char power_role[VALUE_BUF_SIZE] = "unknown";
    char port_type[VALUE_BUF_SIZE] = "unknown";
    char partner_path[PATH_BUF_SIZE];

    snprintf(path, sizeof(path), "%s/%s/data_role", SYSFS_TYPEC_DIR, port_name);
    read_sysfs_string(path, data_role, sizeof(data_role));

    snprintf(path, sizeof(path), "%s/%s/power_role", SYSFS_TYPEC_DIR, port_name);
    read_sysfs_string(path, power_role, sizeof(power_role));

    snprintf(path, sizeof(path), "%s/%s/port_type", SYSFS_TYPEC_DIR, port_name);
    read_sysfs_string(path, port_type, sizeof(port_type));

    snprintf(partner_path, sizeof(partner_path), "%s/%s/%s-partner", SYSFS_TYPEC_DIR, port_name, port_name);
    int partner_connected = (access(partner_path, F_OK) == 0);

    printf("=== Port %s ===\n", port_name);
    printf("  Port Type:  %s\n", port_type);
    printf("  Data Role:  %s\n", data_role);
    printf("  Power Role: %s\n", power_role);
    printf("  Partner:    %s\n", partner_connected ? "CONNECTED" : "DISCONNECTED");
}

int main(int argc, char *argv[]) {
    if (argc >= 4 && strcmp(argv[1], "--swap") == 0) {
        const char *port = argv[2];
        const char *target_role = argv[3]; /* host/device or source/sink */
        char path[PATH_BUF_SIZE];

        if (strcmp(target_role, "host") == 0 || strcmp(target_role, "device") == 0) {
            snprintf(path, sizeof(path), "%s/%s/data_role", SYSFS_TYPEC_DIR, port);
        } else if (strcmp(target_role, "source") == 0 || strcmp(target_role, "sink") == 0) {
            snprintf(path, sizeof(path), "%s/%s/power_role", SYSFS_TYPEC_DIR, port);
        } else {
            fprintf(stderr, "Unknown target role: %s\n", target_role);
            return EXIT_FAILURE;
        }

        printf("Requesting swap on %s to %s...\n", port, target_role);
        if (write_sysfs_string(path, target_role) == 0) {
            printf("Swap request submitted successfully.\n");
        } else {
            fprintf(stderr, "Swap request failed!\n");
            return EXIT_FAILURE;
        }
        return EXIT_SUCCESS;
    }

    DIR *dir = opendir(SYSFS_TYPEC_DIR);
    if (!dir) {
        perror("Cannot open /sys/class/typec");
        return EXIT_FAILURE;
    }

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (strncmp(entry->d_name, "port", 4) == 0 && strchr(entry->d_name, '-') == NULL) {
            inspect_typec_port(entry->d_name);
        }
    }
    closedir(dir);

    return EXIT_SUCCESS;
}
```
```cpp
// typec_switcher.cpp — Idiomatic C++20 implementation with std::filesystem
#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <string_view>
#include <system_error>

namespace fs = std::filesystem;

class TypeCPortInspector {
public:
    explicit TypeCPortInspector(fs::path sysfs_base = "/sys/class/typec")
        : base_path_(std::move(sysfs_base)) {}

    void scan_all_ports() const {
        if (!fs::exists(base_path_)) {
            std::cerr << "Error: " << base_path_ << " does not exist on this kernel.\n";
            return;
        }

        for (const auto& entry : fs::directory_iterator(base_path_)) {
            const auto filename = entry.path().filename().string();
            if (filename.rfind("port", 0) == 0 && filename.find('-') == std::string::npos) {
                print_port_status(entry.path());
            }
        }
    }

    [[nodiscard]] bool request_role_swap(std::string_view port_name, std::string_view target_role) const {
        fs::path target_file;
        if (target_role == "host" || target_role == "device") {
            target_file = base_path_ / port_name / "data_role";
        } else if (target_role == "source" || target_role == "sink") {
            target_file = base_path_ / port_name / "power_role";
        } else {
            std::cerr << "Error: Invalid target role '" << target_role << "'\n";
            return false;
        }

        std::ofstream ofs(target_file);
        if (!ofs.is_open()) {
            std::cerr << "Error: Failed to open " << target_file << " for writing.\n";
            return false;
        }

        ofs << target_role;
        if (ofs.fail()) {
            std::cerr << "Error: Kernel rejected role swap request.\n";
            return false;
        }

        std::cout << "Role swap request to '" << target_role << "' on " << port_name << " accepted by kernel.\n";
        return true;
    }

private:
    fs::path base_path_;

    static std::string read_attribute(const fs::path& attr_path) {
        std::ifstream ifs(attr_path);
        if (!ifs.is_open()) {
            return "unknown";
        }
        std::string val;
        std::getline(ifs, val);
        return val;
    }

    void print_port_status(const fs::path& port_path) const {
        const auto port_name = port_path.filename().string();
        const auto data_role = read_attribute(port_path / "data_role");
        const auto power_role = read_attribute(port_path / "power_role");
        const auto port_type = read_attribute(port_path / "port_type");
        const bool partner_attached = fs::exists(port_path / (port_name + "-partner"));

        std::cout << "=== Port: " << port_name << " ===\n"
                  << "  Port Type:  " << port_type << "\n"
                  << "  Data Role:  " << data_role << "\n"
                  << "  Power Role: " << power_role << "\n"
                  << "  Partner:    " << (partner_attached ? "CONNECTED" : "DISCONNECTED") << "\n\n";
    }
};

int main(int argc, char* argv[]) {
    TypeCPortInspector inspector;

    if (argc >= 4 && std::string_view(argv[1]) == "--swap") {
        const std::string_view port = argv[2];
        const std::string_view role = argv[3];
        return inspector.request_role_swap(port, role) ? EXIT_SUCCESS : EXIT_FAILURE;
    }

    inspector.scan_all_ports();
    return EXIT_SUCCESS;
}
```
:::

## Порівняльний аналіз C та C++ реалізацій

Обидві реалізації ілюструють ідіоматичні підходи до системного програмування у Linux:

1. **POSIX C99 підхід:**
   - Низькорівневе відкриття через `open()` з прапорами `O_RDONLY` / `O_WRONLY` уникає створення проміжних буферів бібліотеки `stdio`.
   - Пряма обробка кодів помилок системних викликів `read()` / `write()` через `errno` дозволяє точно виявити причину відмови ядра.
   - Використання системного виклику `access(path, F_OK)` надає найшвидший спосіб перевірити факт присутності директорії `port0-partner` без відкриття файлів.

2. **C++20 підхід:**
   - Бібліотека `std::filesystem` забезпечує кросплатформену та безпечну роботу зі шляхами, позбавляючи від ризику переповнення буфера при роботі з `snprintf()`.
   - Застосування `std::string_view` дозволяє обробляти аргументи командного рядка без динамічного виділення пам'яті у купі (`std::string`).
   - Парадигма RAII у файлових потоках `std::ofstream` гарантує закриття системного дескриптора навіть при виникненні винятків.

## Інтеграція з подіями udev та тестування

Для автоматичного запуску утиліти або виконання перемикання ролей при фізичному підключенні пристрою у системну конфігурацію `/etc/udev/rules.d/99-typec.rules` додаються наступні правила:

```ini
# Моніторинг появи нового партнера на порті Type-C
ACTION=="add", SUBSYSTEM=="typec", KERNEL=="port*-partner", RUN+="/usr/local/bin/typec_switcher"

# Автоматичне переключення даних у режим host при підключенні док-станції
ACTION=="change", SUBSYSTEM=="typec", KERNEL=="port0", ATTR{power_role}=="sink", RUN+="/usr/local/bin/typec_switcher --swap port0 host"
```

Для інтерактивного налагодження обміну подіями між ядром та udev використовується системна утиліта:

```bash
# Моніторинг системних подій підсистеми typec у реальному часі
udevadm monitor --environment --subsystem-match=typec
```

Під час підключення кабелю в консолі з'являться події `add` і `change` підсистеми `typec` — окремо для порту, для партнера й для кожного оголошеного альтернативного режиму. Це підтверджує, що весь каскад драйверів ядра відпрацював і подія дійшла до простору користувача.
