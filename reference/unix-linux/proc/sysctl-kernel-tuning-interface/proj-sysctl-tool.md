# ⚙️ Практика: розробка утиліти керування параметрами /proc/sys на C та C++

Утиліта `sysctl(8)` у операційній системі Linux є зручною обгорткою у просторі користувача (*userspace wrapper*) над віртуальною файловою системою `/proc/sys`. Її головне завдання полягає у трансляції зрозумілих людині імен параметрів із крапковою нотацією (наприклад, `net.ipv4.ip_forward`) у відповідні шляхи у віртуальному файловому дереві (`/proc/sys/net/ipv4/ip_forward`), а також у зчитуванні та записі текстових значень з обробкою системних помилок доступу VFS та прав доступу.

У цьому практичному проєкті ми розробимо власну легку утиліту `mini_sysctl`, яка реалізує ключові функції системної утиліти `sysctl(8)` та підтримує три режими роботи:

1. **Режим читання конкретного параметра:** Програма приймає ім'я параметра у крапковій нотації, відкриває відповідний віртуальний файл, зчитує поточне значення та виводить його у стандартний потік виводу у форматі `ключ = значення`.
2. **Режим запису нового значення:** Програма приймає ключ і нове значення, відкриває файл для запису, передає текстовий рядок ядру та обробляє можливі помилки доступу, прав або некоректних діапазонів.
3. **Безаварійна трансляція шляхів:** Програма виконує перетворення крапкової нотації у шлях VFS, контролює довжину шляху у межах системної константи `PATH_MAX` та коректно розпізнає помилки відсутності параметрів у ядрі.

Для демонстрації відмінностей системного програмування рішення реалізовано двома мовами — C та C++.

## Архітектурний задум та перетворення шляхів у VFS

Віртуальна файлова система `/proc/sys` відображає ієрархію каталогів ядра у вигляді звичайного файлового дерева. Правила перетворення крапкової назви параметра у шлях файлу VFS є суворими й однозначними:

- Кожен символ крапки `.` у назві параметра замінюється на символ роздільника каталогів `/`.
- До отриманого відносного шляху додається обов'язковий системний префікс `/proc/sys/`.

Наведемо приклади трансляції найпоширеніших параметрів:

- `kernel.hostname` -> `/proc/sys/kernel/hostname`
- `net.core.somaxconn` -> `/proc/sys/net/core/somaxconn`
- `vm.swappiness` -> `/proc/sys/vm/swappiness`
- `fs.protected_symlinks` -> `/proc/sys/fs/protected_symlinks`

Коли програма намагається відкрити файл у `/proc/sys`, ядро перевіряє існування параметра у внутрішніх таблицях `ctl_table`. Якщо вказаний параметр відсутній у підсистемі ядра, системний виклик `open()` повертає помилку `ENOENT` (Файл або каталог не існує). Якщо процес не має привілеїв `CAP_SYS_ADMIN` чи `CAP_NET_ADMIN`, запис у файл завершується з помилкою `EACCES` (Відмовлено в доступі) або `EPERM` (Операція не дозволена). Якщо файл є read-only (має права доступу `0444`), спроба відкрити його з прапорцем `O_WRONLY` повертає помилку `EACCES` або `EROFS`.

## Детальний розбір алгоритму обробки

Процес обробки параметра утилітою проходить наступні чіткі етапи:

1. **Аналіз аргументів командного рядка:** Програма аналізує кількість аргументів у масиві `argv`. Якщо передано один аргумент — це режим читання. Якщо передано два аргументи — перший вважається ключем, а другий — новим значенням для запису.
2. **Валідація та трансформування шляху:** Переданий рядок перевіряється на відсутність недопустимих символів. Усі крапки замінюються на сліші. Довжина підсумкового рядка перевіряється на відповідність системному ліміту `PATH_MAX` (4096 байтів). Якщо шлях перевищує ліміт, програма негайно зупиняється з кодом помилки `ENAMETOOLONG`.
3. **Виконання системних викликів VFS:**
   - Для режиму читання викликається `open(path, O_RDONLY)`, після чого дані читаються через `read(fd, buffer, count)` і файл закривається викликом `close(fd)`.
   - Для режиму запису викликається `open(path, O_WRONLY)`, новий рядок записується через `write(fd, value, count)` і файл закривається викликом `close(fd)`.
4. **Форматування та аналіз системних помилок:** Отримані текстові дані очищаються від символів переносу рядка `\n`. У разі виникнення помилок причина розбирається через `errno` у C або повертається як значення `std::expected` у C++, а розгорнуте пояснення йде у потік `stderr`.

## Реалізація утиліти на C та C++

Нижче наведено повні робочі реалізації консольної програми `mini_sysctl`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <limits.h>

#define SYSCTL_PREFIX "/proc/sys/"
#define BUFFER_SIZE 4096

/* Перетворення крапкової назви net.ipv4.ip_forward у шлях /proc/sys/net/ipv4/ip_forward */
static int key_to_path(const char *key, char *path_out, size_t max_len)
{
    size_t prefix_len = strlen(SYSCTL_PREFIX);
    size_t key_len = strlen(key);

    if (prefix_len + key_len >= max_len) {
        errno = ENAMETOOLONG;
        return -1;
    }

    strcpy(path_out, SYSCTL_PREFIX);
    for (size_t i = 0; i < key_len; i++) {
        path_out[prefix_len + i] = (key[i] == '.') ? '/' : key[i];
    }
    path_out[prefix_len + key_len] = '\0';
    return 0;
}

/* Зчитування значення параметра sysctl */
static int read_sysctl(const char *key)
{
    char path[PATH_MAX];
    char buffer[BUFFER_SIZE];

    if (key_to_path(key, path, sizeof(path)) < 0) {
        fprintf(stderr, "Помилка: занадто довгий ключ '%s'\n", key);
        return 1;
    }

    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        if (errno == ENOENT) {
            fprintf(stderr, "Помилка: параметр '%s' не існує у /proc/sys\n", key);
        } else if (errno == EACCES) {
            fprintf(stderr, "Помилка: немає прав для читання %s\n", path);
        } else {
            fprintf(stderr, "Помилка відкриття %s: %s\n", path, strerror(errno));
        }
        return 1;
    }

    ssize_t bytes_read = read(fd, buffer, sizeof(buffer) - 1);
    close(fd);

    if (bytes_read < 0) {
        fprintf(stderr, "Помилка читання %s: %s\n", path, strerror(errno));
        return 1;
    }

    buffer[bytes_read] = '\0';
    /* Видаляємо кінцевий символ нового рядка, якщо він є */
    if (bytes_read > 0 && buffer[bytes_read - 1] == '\n') {
        buffer[bytes_read - 1] = '\0';
    }

    printf("%s = %s\n", key, buffer);
    return 0;
}

/* Запис нового значення у параметр sysctl */
static int write_sysctl(const char *key, const char *value)
{
    char path[PATH_MAX];

    if (key_to_path(key, path, sizeof(path)) < 0) {
        fprintf(stderr, "Помилка: занадто довгий ключ '%s'\n", key);
        return 1;
    }

    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        if (errno == EACCES || errno == EPERM) {
            fprintf(stderr, "Помилка доступу до %s: потрібні привілеї root (CAP_SYS_ADMIN або CAP_NET_ADMIN)\n", path);
        } else if (errno == ENOENT) {
            fprintf(stderr, "Помилка: параметр '%s' не існує у /proc/sys\n", key);
        } else if (errno == EROFS) {
            fprintf(stderr, "Помилка: параметр %s доступний лише для читання\n", path);
        } else {
            fprintf(stderr, "Помилка відкриття %s для запису: %s\n", path, strerror(errno));
        }
        return 1;
    }

    size_t val_len = strlen(value);
    ssize_t bytes_written = write(fd, value, val_len);
    close(fd);

    if (bytes_written < 0) {
        if (errno == EINVAL) {
            fprintf(stderr, "Помилка запису у %s: недопустиме значення '%s' (out of range або невірний тип)\n", path, value);
        } else {
            fprintf(stderr, "Помилка запису у %s: %s\n", path, strerror(errno));
        }
        return 1;
    }

    printf("%s = %s\n", key, value);
    return 0;
}

int main(int argc, char *argv[])
{
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <ключ> [значення]\n", argv[0]);
        fprintf(stderr, "Приклад читання: %s net.ipv4.ip_forward\n", argv[0]);
        fprintf(stderr, "Приклад запису:   %s net.ipv4.ip_forward 1\n", argv[0]);
        return 1;
    }

    if (argc == 2) {
        return read_sysctl(argv[1]);
    } else {
        return write_sysctl(argv[1], argv[2]);
    }
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
#include <algorithm>

namespace fs = std::filesystem;

class SysctlManager {
private:
    static constexpr std::string_view sysctl_prefix = "/proc/sys/";

public:
    // Трансляція ключа "net.ipv4.ip_forward" у fs::path "/proc/sys/net/ipv4/ip_forward"
    static std::expected<fs::path, std::string> key_to_path(std::string_view key) {
        std::string rel_path(key);
        std::replace(rel_path.begin(), rel_path.end(), '.', '/');

        fs::path full_path = fs::path(sysctl_prefix) / rel_path;
        return full_path;
    }

    // Зчитування значення параметра
    static std::expected<std::string, std::string> read_value(std::string_view key) {
        auto path_res = key_to_path(key);
        if (!path_res) {
            return std::unexpected(path_res.error());
        }

        const fs::path& path = *path_res;
        if (!fs::exists(path)) {
            return std::unexpected("Параметр не існує у /proc/sys: " + path.string());
        }

        std::ifstream file(path);
        if (!file.is_open()) {
            return std::unexpected("Не вдалося відкрити файл для читання: " + path.string() +
                                   " (перевірте права доступу)");
        }

        std::string value;
        if (std::getline(file, value)) {
            return value;
        }

        return std::unexpected("Не вдалося прочитати дані з файлу: " + path.string());
    }

    // Запис нового значення у параметр з автоматичним закриттям дескриптора (RAII)
    static std::expected<void, std::string> write_value(std::string_view key, std::string_view value) {
        auto path_res = key_to_path(key);
        if (!path_res) {
            return std::unexpected(path_res.error());
        }

        const fs::path& path = *path_res;
        if (!fs::exists(path)) {
            return std::unexpected("Параметр не існує у /proc/sys: " + path.string());
        }

        std::ofstream file(path);
        if (!file.is_open()) {
            return std::unexpected("Помилка доступу до " + path.string() +
                                   ": потрібні привілеї root (CAP_SYS_ADMIN або CAP_NET_ADMIN)");
        }

        file << value;
        if (!file.good()) {
            return std::unexpected("Помилка запису даних у " + path.string() +
                                   " (можливо, значення поза допустимим діапазоном)");
        }

        return {};
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <ключ> [значення]\n";
        std::cerr << "Приклад читання: " << argv[0] << " vm.swappiness\n";
        std::cerr << "Приклад запису:   " << argv[0] << " vm.swappiness 10\n";
        return 1;
    }

    std::string_view key = argv[1];

    if (argc == 2) {
        auto result = SysctlManager::read_value(key);
        if (result) {
            std::cout << key << " = " << *result << "\n";
            return 0;
        } else {
            std::cerr << "Помилка: " << result.error() << "\n";
            return 1;
        }
    } else {
        std::string_view value = argv[2];
        auto result = SysctlManager::write_value(key, value);
        if (result) {
            std::cout << key << " = " << value << "\n";
            return 0;
        } else {
            std::cerr << "Помилка: " << result.error() << "\n";
            return 1;
        }
    }
}
```
:::

## Глибокий аналіз системних відмінностей реалізацій

Порівняння реалізацій на C та C++ демонструє еволюцію системного програмування в інфраструктурі Linux:

1. **Управління ресурсами пам'яті та RAII:**
   У C-версії розробник зобов'язаний вручну стежити за відкритими системними ресурсами. Кожен виклик `open()` вимагає відповідного `close(fd)` у кожній гілці виходу з функції (зокрема при обробці помилок `read` або `write`). Забутий `close()` в одній із гілок помилки призводить до витоку файлових дескрипторів (*file descriptor leak*), що під навантаженням швидко вичерпує ліміт `RLIMIT_NOFILE`. У C++ реалізації об'єкти `std::ifstream` та `std::ofstream` автоматично гарантують закриття системного файлового дескриптора у своєму деструкторі за принципом RAII (*Resource Acquisition Is Initialization*), навіть якщо виконання функції переривається помилкою.

2. **Обробка помилок та семантика типів:**
   У C-реалізації інформація про системну помилку повертається через від'ємне число `-1` і глобальну змінну `errno`, яка зберігає стан останнього системного виклику для даного потоку. Для отримання текстового опису використовується функція `strerror(errno)`. У C++23 реалізації застосовано безпечний тип `std::expected<T, E>`. Він явно повідомляє про результат у сигнатурі функції без використання винятків (*exceptions*), що зберігає високу продуктивність і робить контроль виконання прозорим для компілятора.

3. **Безпечність роботи з файловими шляхами:**
   У версії C трансляція ключа у шлях VFS виконується вручну посимвольним копіюванням у статичний масив `char path[PATH_MAX]`. Для запобігання переповненню буфера (*buffer overflow*) у коді стоїть явна перевірка довжини. У C++ клас `std::filesystem::path` виконує оператор конкатенації `/` безпечно, автоматично розбираючи роздільники шляхів з урахуванням специфіки ОС.

## Тестування утиліти та трасування системних викликів

Збірка обох реалізацій виконується стандартним комплектом компіляторів GCC у середовищі Linux:

```bash
# Збірка C-версії (стандарт C11)
gcc -std=c11 -O2 -Wall proj_sysctl.c -o mini_sysctl_c

# Збірка C++-версії (вимагає стандарту C++23)
g++ -std=c++23 -O2 -Wall proj_sysctl.cpp -o mini_sysctl_cpp
```

### Перевірка читання та запису у працюючій системі

```bash
# 1. Читання поточного стану forwarding IPv4
./mini_sysctl_c net.ipv4.ip_forward
# Вивід: net.ipv4.ip_forward = 0

# 2. Спроба запису нового значення без привілеїв root
./mini_sysctl_c net.ipv4.ip_forward 1
# Вивід: Помилка доступу до /proc/sys/net/ipv4/ip_forward: потрібні привілеї root (CAP_SYS_ADMIN або CAP_NET_ADMIN)

# 3. Запис із привілеями суперкористувача root
sudo ./mini_sysctl_cpp net.ipv4.ip_forward 1
# Вивід: net.ipv4.ip_forward = 1

# 4. Перевірка результату запису
./mini_sysctl_c net.ipv4.ip_forward
# Вивід: net.ipv4.ip_forward = 1

# 5. Спроба запису неприпустимого значення (перевірка minmax у ядрі)
sudo ./mini_sysctl_c vm.swappiness 300
# Вивід: Помилка запису у /proc/sys/vm/swappiness: недопустиме значення '300' (out of range або невірний тип)
```

### Простеження системних викликів через strace

Трасування виконання викликів утиліти через інструмент `strace ./mini_sysctl_c net.ipv4.ip_forward` показує точну послідовність низькорівневих дій у ядрі Linux:

```text
execve("./mini_sysctl_c", ["./mini_sysctl_c", "net.ipv4.ip_forward"], ...) = 0
openat(AT_FDCWD, "/proc/sys/net/ipv4/ip_forward", O_RDONLY) = 3
read(3, "0\n", 4095)                    = 2
close(3)                                = 0
fstat(1, {st_mode=S_IFCHR|0620, ...})   = 0
write(1, "net.ipv4.ip_forward = 0\n", 24) = 24
exit_group(0)                           = 0
```

Цей журнал системних викликів прямо підтверджує головну архітектурну ідею: системна утиліта `sysctl` не використовує жодних магічних привілейованих викликів, а працює як звичайний клієнт віртуальної файлової системи `procfs`, перетворюючи крапкові імена у звичайні виклики VFS `openat`, `read` та `write`.
