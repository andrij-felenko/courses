# ⚙️ Інспекція та підняття рівня Lockdown з простору користувача

Програми простору користувача взаємодіють із підсистемою Kernel Lockdown Mode через віртуальну файлову систему `securityfs`, яка зазвичай монтується системними завантажувачами або сервісом `systemd` за шляхом `/sys/kernel/security`. Файл `/sys/kernel/security/lockdown` слугує єдиним уніфікованим інтерфейсом для інспекції поточного стану захисту ядра та монотонного підвищення його рівня під час виконання операційної системи.

## 1. Архітектура системного інтерфейсу sysfs та правила парсингу

Файл `/sys/kernel/security/lockdown` надає спеціальний текстовий інтерфейс. При виконанні системного виклику `read()` ядро повертає один текстовий рядок, у якому перераховані всі доступні рівні захисту, розділені пробілами, а поточний активний режим узято у квадратні дужки:

```text
none [integrity] confidentiality
```

Залежно від конфігурації ядра та стану системного захисту вміст файлу може набувати трьох варіантів:
* `[none] integrity confidentiality` — підсистему Lockdown активовано, але блокування операцій наразі вимкнено (режим None).
* `none [integrity] confidentiality` — активовано режим захисту цілісності ядра (Integrity).
* `none integrity [confidentiality]` — активовано найсуворіший режим захисту конфіденційності (Confidentiality).

Якщо файл `/sys/kernel/security/lockdown` відсутній або спроба його відкриття повертає помилку `ENOENT`, це свідчить про те, що ядро було скомпільоване без підтримки модуля LSM Lockdown (`CONFIG_SECURITY_LOCKDOWN_LSM=n`), або віртуальну файлову систему `securityfs` не було змонтовано у системі, або виконання відбувається всередині ізольованого контейнера з обмеженим доступом до `/sys`.

## 2. Модель доступу, правила підвищення рівня та обробка помилок

Під час запису текстового рядка у файл `/sys/kernel/security/lockdown` ядро керується принципом монотонного підвищення привілеїв (Monotonic Escalation):
1. Запис рядка `integrity` дозволений лише якщо поточним активним режимом є `none`.
2. Запис рядка `confidentiality` дозволений якщо поточним активним режимом є `none` або `integrity`.
3. Запис будь-якого іншого рядка, спроба пониження рівня (наприклад, запис `none` у режим `integrity`), відхиляється ядром із поверненням помилки **`-EPERM` (Operation not permitted)** для пониження та **`-EINVAL` (Invalid argument)** для нерозпізнаного рядка. Звичайного користувача до запису взагалі не допускає VFS: файл належить `root` із правами `0600`, тож `open()` на запис повертає `-EACCES` ще до будь-якої перевірки самого модуля.

Для забезпечення надійної взаємодії з цим інтерфейсом розробники системного програмного забезпечення повинні дотримуватися правил обробки помилок POSIX та правильно інтерпретувати коди `errno`.

## 3. Детальний розбір реалізації мовою C

С-версія утиліти побудована на системних викликах POSIX (`open`, `read`, `write`, `close`). Основні етапи роботи коду:
* **Зчитання файлу:** Використовується системний виклик `open()` у режимі `O_RDONLY`. Буфер гарантовано завершується нульовим байтом `\0` для запобігання виходу за межі пам'яті при пошуку підрядка.
* **Парсинг квадратних дужок:** Функції `strchr()` знаходять позиції символів `[` та `]`. Довжина назви режиму вираховується як різниця вказівників і копіюється у безпечний локальний буфер.
* **Запис режиму:** Спроба підвищення рівня здійснюється викликом `write()`. У разі виникнення помилки код перевіряє значення `errno`: `EPERM` сигналізує про заборону пониження рівня ядром, а `EINVAL` — про передачу непідтримуваного рядка.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>

#define LOCKDOWN_PATH "/sys/kernel/security/lockdown"
#define BUF_SIZE 256

/* Зчитування поточного статусу sysfs у текстовий буфер */
static int read_lockdown_status(char *buffer, size_t size) {
    int fd = open(LOCKDOWN_PATH, O_RDONLY);
    if (fd < 0) {
        int err = errno;
        if (err == ENOENT) {
            fprintf(stderr, "Помилка: Файл %s відсутній. Lockdown LSM не підтримується ядром.\n",
                    LOCKDOWN_PATH);
        } else if (err == EACCES) {
            fprintf(stderr, "Помилка: Недостатньо прав для читання %s.\n", LOCKDOWN_PATH);
        } else {
            fprintf(stderr, "Помилка відкриття %s: %s\n", LOCKDOWN_PATH, strerror(err));
        }
        return -1;
    }

    ssize_t bytes_read = read(fd, buffer, size - 1);
    close(fd);

    if (bytes_read <= 0) {
        fprintf(stderr, "Помилка: Не вдалося зчитати дані з %s\n", LOCKDOWN_PATH);
        return -1;
    }

    buffer[bytes_read] = '\0';
    /* Видалення символу нового рядка наприкінці */
    char *newline = strchr(buffer, '\n');
    if (newline) {
        *newline = '\0';
    }
    return 0;
}

/* Парсинг рядка та виділення режиму у квадратних дужках [mode] */
static void print_parsed_mode(const char *raw_status) {
    const char *start = strchr(raw_status, '[');
    const char *end = strchr(raw_status, ']');

    if (start && end && end > start) {
        char current_mode[32];
        size_t len = (size_t)(end - start - 1);
        if (len < sizeof(current_mode)) {
            memcpy(current_mode, start + 1, len);
            current_mode[len] = '\0';
            printf("Поточний активний режим Lockdown: %s\n", current_mode);
        } else {
            fprintf(stderr, "Помилка: Назва режиму перевищує розмір буфера\n");
        }
    } else {
        printf("Не вдалося розпізнати дужки у статусі: %s\n", raw_status);
    }
}

/* Запис нового значення у sysfs для підвищення рівня */
static int set_lockdown_mode(const char *mode) {
    int fd = open(LOCKDOWN_PATH, O_WRONLY);
    if (fd < 0) {
        int err = errno;
        fprintf(stderr, "Не вдалося відкрити sysfs для запису: %s\n", strerror(err));
        return -1;
    }

    size_t len = strlen(mode);
    ssize_t written = write(fd, mode, len);
    int saved_errno = errno;
    close(fd);

    if (written != (ssize_t)len) {
        if (saved_errno == EPERM) {
            fprintf(stderr, "Помилка відмови (-EPERM): Пониження рівня блокування заборонено ядром!\n");
        } else if (saved_errno == EINVAL) {
            fprintf(stderr, "Помилка аргументу (-EINVAL): Передано невідомий режим '%s'.\n", mode);
        } else {
            fprintf(stderr, "Помилка запису режиму '%s': %s\n", mode, strerror(saved_errno));
        }
        return -1;
    }

    printf("Успішно підвищено режим Lockdown до: %s\n", mode);
    return 0;
}

int main(int argc, char *argv[]) {
    char status_buf[BUF_SIZE];

    printf("--- Інспекція Kernel Lockdown Mode (C POSIX API) ---\n");
    if (read_lockdown_status(status_buf, sizeof(status_buf)) != 0) {
        return EXIT_FAILURE;
    }

    printf("Вміст sysfs: %s\n", status_buf);
    print_parsed_mode(status_buf);

    if (argc > 1) {
        const char *new_mode = argv[1];
        printf("\nСпроба зміни режиму на '%s'...\n", new_mode);
        if (set_lockdown_mode(new_mode) != 0) {
            return EXIT_FAILURE;
        }
    }

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <filesystem>
#include <expected>
#include <system_error>

namespace fs = std::filesystem;

class LockdownManager {
public:
    static constexpr std::string_view sysfs_path = "/sys/kernel/security/lockdown";

    enum class Error {
        FileNotFound,
        AccessDenied,
        ReadError,
        WriteDenied,
        InvalidArgument,
        ParseError
    };

    struct Status {
        std::string raw_line;
        std::string active_mode;
    };

    [[nodiscard]] static std::expected<Status, Error> get_status() {
        if (!fs::exists(sysfs_path)) {
            return std::unexpected(Error::FileNotFound);
        }

        std::ifstream file{std::string(sysfs_path)};
        if (!file.is_open()) {
            return std::unexpected(Error::AccessDenied);
        }

        std::string line;
        if (!std::getline(file, line)) {
            return std::unexpected(Error::ReadError);
        }

        auto start = line.find('[');
        auto end = line.find(']');
        if (start == std::string::npos || end == std::string::npos || end <= start) {
            return std::unexpected(Error::ParseError);
        }

        std::string active = line.substr(start + 1, end - start - 1);
        return Status{ .raw_line = std::move(line), .active_mode = std::move(active) };
    }

    [[nodiscard]] static std::expected<void, Error> set_mode(std::string_view mode) {
        std::ofstream file{std::string(sysfs_path)};
        if (!file.is_open()) {
            return std::unexpected(Error::AccessDenied);
        }

        file << mode;
        file.flush();  /* без явного скидання помилка запису спливе аж у деструкторі */
        if (file.fail()) {
            return std::unexpected(Error::WriteDenied);
        }

        return {};
    }

    static std::string_view error_to_string(Error err) noexcept {
        switch (err) {
            case Error::FileNotFound: return "Файл sysfs відсутній (Lockdown LSM вимкнено)";
            case Error::AccessDenied: return "Відмовлено у доступі (потрібні права root)";
            case Error::ReadError: return "Помилка читання з файлу sysfs";
            case Error::WriteDenied: return "Відмовлено у записі (пониження рівня заборонено)";
            case Error::InvalidArgument: return "Невідомий режим блокування";
            case Error::ParseError: return "Не вдалося розпізнати формат статусу sysfs";
        }
        return "Невідома помилка";
    }
};

int main(int argc, char* argv[]) {
    std::cout << "--- Інспекція Kernel Lockdown Mode (C++23 API) ---\n";

    auto status_result = LockdownManager::get_status();
    if (!status_result) {
        std::cerr << "Помилка: " << LockdownManager::error_to_string(status_result.error()) << '\n';
        return 1;
    }

    const auto& status = status_result.value();
    std::cout << "Вміст sysfs: " << status.raw_line << '\n';
    std::cout << "Активний режим: " << status.active_mode << '\n';

    if (argc > 1) {
        std::string_view requested_mode = argv[1];
        std::cout << "\nСпроба зміни режиму на '" << requested_mode << "'...\n";
        
        auto write_result = LockdownManager::set_mode(requested_mode);
        if (!write_result) {
            std::cerr << "Помилка зміни режиму: " 
                      << LockdownManager::error_to_string(write_result.error()) << '\n';
            return 1;
        }
        std::cout << "Успішно змінено режим Lockdown на: " << requested_mode << '\n';
    }

    return 0;
}
```
:::

## 4. Детальний розбір реалізації мовою C++23

Версія C++23 використовує сучасні ідіоми стандарту для створення безпечного та виразного коду:
* **RAII та керування ресурсами:** Класи `std::ifstream` та `std::ofstream` автоматично закривають файлові дескриптори при виході з області видимості (Scope), гарантуючи відсутність витоків ресурсів навіть при виникненні виняткових ситуацій.
* **Строго типізована обробка помилок через `std::expected`:** Замість повернення сирих цілочисельних кодів або викидання винятків використовується шаблон `std::expected<T, Error>`. Це змушує клієнтський код явно обробляти як успішний результат (`Status`), так і можливі помилки (`Error`).
* **Безпечна робота з рядками:** Клас `std::string_view` використовується для передачі параметрів без додаткового виділення пам'яті у купі (Heap Allocation). Методи `find()` та `substr()` забезпечують елегантний парсинг квадратних дужок.

## 5. Практична інспекція та сценарії тестування

Для тестування роботи реалізованої утиліти у системі без увімкненого Secure Boot (де початковим режимом є `none`) виконуються такі кроки:

1. **Інспекція стану від звичайного користувача:**
   ```bash
   $ ./check_lockdown
   --- Інспекція Kernel Lockdown Mode (C POSIX API) ---
   Вміст sysfs: [none] integrity confidentiality
   Поточний активний режим Lockdown: none
   ```

2. **Підвищення рівня до Integrity з правами root:**
   ```bash
   # sudo ./check_lockdown integrity
   --- Інспекція Kernel Lockdown Mode (C POSIX API) ---
   Вміст sysfs: [none] integrity confidentiality
   Поточний активний режим Lockdown: none

   Спроба зміни режиму на 'integrity'...
   Успішно підвищено режим Lockdown до: integrity
   ```

3. **Спроба пониження рівня назад до none:**
   ```bash
   # sudo ./check_lockdown none
   --- Інспекція Kernel Lockdown Mode (C POSIX API) ---
   Вміст sysfs: none [integrity] confidentiality
   Поточний активний режим Lockdown: integrity

   Спроба зміни режиму на 'none'...
   Помилка відмови (-EPERM): Пониження рівня блокування заборонено ядром!
   ```

4. **Перевірка блокування чутливих операцій у dmesg:**
   Після переходу у режим `integrity` будь-яка спроба прямого запису у пристрій пам'яті фіксується ядром:
   ```bash
   # sudo dd if=/dev/zero of=/dev/mem bs=1K count=1
   dd: error writing '/dev/mem': Operation not permitted
   
   # dmesg | tail -n 1
   [ 1420.512091] Lockdown: dd: /dev/mem,kmem,port is restricted; see man kernel_lockdown.7
   ```

## 6. Особливості виконання у контейнерних середовищах

У середовищах Docker, Podman та Kubernetes пристрої `/sys/kernel/security` часто монтуються в режимі "Read-Only" або перекриваються за допомогою масок маппінгу namespaces. Якщо контейнер намагається виконати запис у sysfs Lockdown без наявності привілею `CAP_SYS_ADMIN` у початковому user namespace (User Namespace 0), ядро повертає помилку `-EACCES` чи `-EPERM`.

Крім того, оскільки рівень Lockdown є глобальним параметром ядра (`kernel_locked_down`), його підвищення всередині привілейованого контейнера негайно змінює режим блокування для всієї хост-системи та всіх сусідніх контейнерів. З огляду на це, управління Lockdown рекомендується виконувати виключно на етапі ініціалізації хост-ОС через параметри завантажувача або ранні сервіси systemd.
