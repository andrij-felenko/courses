# Практичний проєкт: Побудова мережевого демона з комплексною ізоляцією Landlock ABI v4/v5

У цьому практичному проєкті розглядається повноцінна реалізація мережевого сервісу на мовах C та C++, який застосовує безпривілейовану сандбокс-ізоляцію за допомогою Landlock ABI v4 та ABI v5. Демон демонструє адаптивну перевірку версій ядра, конфігурування дозволів для файлової системи VFS, обмеження викликів `bind()` та `connect()` для TCP-сокетів, а також блокування пристроїв `ioctl()`.

## 1. Архітектура та етапи побудови пісочниці

Створення безпривілейованої пісочниці у коді сервісу розбивається на п'ять послідовних кроків:

1. **Запит версії ABI ядра**: Програма викликає `landlock_create_ruleset(NULL, 0, LANDLOCK_CREATE_RULESET_VERSION)` для визначення максимально підтримуваної версії Landlock у запущеній системі.
2. **Формування атрибутів правил (`landlock_ruleset_attr`)**: Залежно від виявленої версії ABI програма додає відповідні бітові маски. Якщо `abi >= 4`, вмикаються прапорці `LANDLOCK_ACCESS_NET_BIND_TCP` та `LANDLOCK_ACCESS_NET_CONNECT_TCP`. Якщо `abi >= 5`, додається `LANDLOCK_ACCESS_FS_IOCTL_DEV`.
3. **Наповнення правилами дозволу (`landlock_add_rule`)**:
   - **VFS-домен**: Додається правило `LANDLOCK_RULE_PATH_BENEATH`, яке дозволяє лише читання каталогів та файлів усередині зазначеної теки (наприклад, `/var/www` або `/tmp`).
   - **Мережевий домен**: Додається правило `LANDLOCK_RULE_NET_PORT` для прапорця `LANDLOCK_ACCESS_NET_BIND_TCP` з дозволеним портом `8080`.
   - **Правило вихідних з'єднань**: Для прапорця `LANDLOCK_ACCESS_NET_CONNECT_TCP` жодних дозволяючих правил не додається. Оскільки прапорець задекларовано в `handled_access_net`, відсутність правил автоматично означає повну заборону всіх вихідних TCP-з'єднань (`connect`).
   - **Пристрої IOCTL**: Оскільки у ABI v5 прапорець `LANDLOCK_ACCESS_FS_IOCTL_DEV` контролює доступ до символьних та блочних пристроїв, відсутність правила дозволу блокує всі нестандартні `ioctl()`, залишаючи лише мінімальний безпечний білий список ядра (`FIOCLEX`, `TCGETS` тощо).
4. **Установлення прапорця `PR_SET_NO_NEW_PRIVS`**: Викликається `prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)`. Це є обов'язковою умовою ядра Linux для безпривілейованих процесів, що гарантує унеможливлення підвищення привілеїв через `setuid`-бінарники під час `execve()`.
5. **Застосування пісочниці (`landlock_restrict_self`)**: Викликом `landlock_restrict_self(ruleset_fd, 0)` набір правил активується для поточного процесу та всіх його майбутніх дочірніх потоків. Файловий дескриптор `ruleset_fd` закривається.

## 2. Поділ на фази виконання та безпековий контур

Шаблон побудови сервісу спирається на чітке розділення життєвого циклу програми на дві фази:

### Фаза 1: Ініціалізація та відкриття системних ресурсів
Під час старту програма від імені користувача виконує всі підготовчі дії, які вимагають підвищених прав або широкого доступу до VFS:
- Зчитування глобальних конфігураційних файлів із `/etc/my_daemon/config.json`.
- Відкриття журнальних файлів аудиту чи підключення до системних сокетів.
- Завантаження ключів шифрування та TLS-сертифікатів у пам'ять процесу.

### Фаза 2: Самоізоляція та обробка недовіреного трафіку
Після завершення ініціалізації сервіс конструює набір правил Landlock, додає до нього мінімально необхідні права (наприклад, доступ лише до каталогу з корисними даними та один слухаючий TCP-порт 8080) і викликає `landlock_restrict_self()`.

Після цього моменту програма переходить у режим зчитування недовірених даних із мережі. Будь-яка вразливість у парсері протоколу чи декодері даних не дозволить зловмиснику зчитати SSH-ключі користувача з `~/.ssh/` чи підключитися до стороннього сервера в мережі, оскільки ці дії блокуються ядром Linux на рівні LSM-хуків.

## 3. Інтеграція з systemd та зовнішніми системними середовищами

Окрім внутрішньої самоізоляції у коді C/C++, у сучасних виробничих інфраструктурах Linux сервіси запускаються під управлінням системного менеджера `systemd`. Останні версії systemd підтримують директиви `Sandboxing` та `Landlock`, які можуть накладати первинний базлайн безпеки ще до виконання `execve()` бінарника програми.

Використання Landlock безпосередньо у коді програми (прикладний рівень) доповнює конфігурацію юніта systemd:
- `systemd` закриває глобальні системні каталоги (`ProtectSystem=strict`, `ProtectHome=read-only`).
- Прикладна програма через Landlock ABI v4/v5 ізолює конкретні динамичні ресурси (динамічні порти `bind`, вихідні `connect` та `ioctl` на відкритих псевдопристроях).

Це гарантує двошаровий захист: навіть якщо системний адміністратор помилково спростить конфігурацію `systemd.service`, програма все одно замкне себе у пісочниці під час запуску.

## 4. Аналіз крайових випадків та відловлювання помилок

Під час практичної експлуатації пісочниці важливо обробляти наступні ситуації:
- **Застаріле ядро Linux (без Landlock)**: Якщо `landlock_create_ruleset()` повертає помилку `-ENOSYS` або `-EOPNOTSUPP` (на ядрах < 5.13), програма повинна або вивести попередження і продовжити роботу у режимі без пісочниці, або завершити роботу з помилкою відповідно до вимог безпеки продукту.
- **Спроба `bind()` на неописаний порт**: Після застосування пісочниці спроба виконати `bind()` на порт `9090` переривається ядром і повертає помилку `-EACCES` (Permission Denied).
- **Спроба вихідного `connect()`**: Спроба підключитися до будь-якої віддаленої IP-адреси повертає помилку `-EACCES`, що перешкоджає підняттю reverse shell.
- **Спроба `ioctl()` на TTY або пристрої**: Спроба виконати `ioctl(fd, TIOCSTI, ...)` на файлі пристрою повертає помилку `-EACCES`, зупиняючи ін'єкцію команд у термінал.

## 5. Двомовна реалізація пісочниці (C та C++)

Нижче наведено повноцінні вихідні файли мовами C та C++. Реалізація на C++ використовує ідіоматичний підхід RAII для керування файловими дескрипторами (`ScopedFd`), обробку помилок через винятки та класи `std::system_error`.

:::tabs
@tab C
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/ioctl.h>
#include <linux/landlock.h>

#ifndef LANDLOCK_ACCESS_NET_BIND_TCP
#define LANDLOCK_ACCESS_NET_BIND_TCP (1ULL << 0)
#define LANDLOCK_ACCESS_NET_CONNECT_TCP (1ULL << 1)
#endif

#ifndef LANDLOCK_ACCESS_FS_IOCTL_DEV
#define LANDLOCK_ACCESS_FS_IOCTL_DEV (1ULL << 15)
#endif

#ifndef LANDLOCK_RULE_NET_PORT
#define LANDLOCK_RULE_NET_PORT 2
struct landlock_net_port_attr {
    __u64 allowed_access;
    __u64 port;
};
#endif

static inline int sys_landlock_create_ruleset(const struct landlock_ruleset_attr *attr, size_t size, __u32 flags) {
    return syscall(__NR_landlock_create_ruleset, attr, size, flags);
}

static inline int sys_landlock_add_rule(int ruleset_fd, enum landlock_rule_type rule_type, const void *rule_attr, __u32 flags) {
    return syscall(__NR_landlock_add_rule, ruleset_fd, rule_type, rule_attr, flags);
}

static inline int sys_landlock_restrict_self(int ruleset_fd, __u32 flags) {
    return syscall(__NR_landlock_restrict_self, ruleset_fd, flags);
}

int apply_sandbox(uint16_t allowed_port, const char *allowed_dir) {
    int abi = sys_landlock_create_ruleset(NULL, 0, LANDLOCK_CREATE_RULESET_VERSION);
    if (abi < 1) {
        fprintf(stderr, "Landlock не підтримується ядром (abi=%d)\n", abi);
        return -1;
    }
    printf("Landlock ABI версія: %d\n", abi);

    struct landlock_ruleset_attr attr;
    memset(&attr, 0, sizeof(attr));

    attr.handled_access_fs = LANDLOCK_ACCESS_FS_READ_FILE | LANDLOCK_ACCESS_FS_READ_DIR;
    if (abi >= 5) {
        attr.handled_access_fs |= LANDLOCK_ACCESS_FS_IOCTL_DEV;
    }

    if (abi >= 4) {
        attr.handled_access_net = LANDLOCK_ACCESS_NET_BIND_TCP | LANDLOCK_ACCESS_NET_CONNECT_TCP;
    }

    int ruleset_fd = sys_landlock_create_ruleset(&attr, sizeof(attr), 0);
    if (ruleset_fd < 0) {
        perror("landlock_create_ruleset");
        return -1;
    }

    /* Додавання правила VFS */
    int dir_fd = open(allowed_dir, O_PATH | O_CLOEXEC);
    if (dir_fd >= 0) {
        struct landlock_path_beneath_attr path_attr = {
            .allowed_access = LANDLOCK_ACCESS_FS_READ_FILE | LANDLOCK_ACCESS_FS_READ_DIR,
            .parent_fd = dir_fd,
        };
        if (sys_landlock_add_rule(ruleset_fd, LANDLOCK_RULE_PATH_BENEATH, &path_attr, 0) < 0) {
            perror("landlock_add_rule path");
            close(dir_fd);
            close(ruleset_fd);
            return -1;
        }
        close(dir_fd);
    }

    /* Додавання правила Мережі (ABI v4+) */
    if (abi >= 4) {
        struct landlock_net_port_attr net_attr = {
            .allowed_access = LANDLOCK_ACCESS_NET_BIND_TCP,
            .port = allowed_port,
        };
        if (sys_landlock_add_rule(ruleset_fd, LANDLOCK_RULE_NET_PORT, &net_attr, 0) < 0) {
            perror("landlock_add_rule net");
            close(ruleset_fd);
            return -1;
        }
    }

    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) < 0) {
        perror("prctl NO_NEW_PRIVS");
        close(ruleset_fd);
        return -1;
    }

    if (sys_landlock_restrict_self(ruleset_fd, 0) < 0) {
        perror("landlock_restrict_self");
        close(ruleset_fd);
        return -1;
    }

    close(ruleset_fd);
    printf("Пісочницю успішно застосовано!\n");
    return 0;
}

int main(void) {
    if (apply_sandbox(8080, "/tmp") < 0) {
        return EXIT_FAILURE;
    }

    /* Перевірка 1: bind на дозволений порт 8080 */
    int s1 = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in addr1 = { .sin_family = AF_INET, .sin_port = htons(8080) };
    if (bind(s1, (struct sockaddr *)&addr1, sizeof(addr1)) == 0) {
        printf("УСПІХ: bind(8080) дозволено\n");
    } else {
        printf("ПОМИЛКА: bind(8080) відхилено: %s\n", strerror(errno));
    }
    close(s1);

    /* Перевірка 2: bind на заблокований порт 9090 */
    int s2 = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in addr2 = { .sin_family = AF_INET, .sin_port = htons(9090) };
    if (bind(s2, (struct sockaddr *)&addr2, sizeof(addr2)) < 0 && errno == EACCES) {
        printf("УСПІХ: bind(9090) заблоковано ядром (EACCES)\n");
    }
    close(s2);

    return EXIT_SUCCESS;
}
```
@tab C++
```cpp
#include <iostream>
#include <string_view>
#include <system_error>
#include <utility>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <linux/landlock.h>

#ifndef LANDLOCK_ACCESS_NET_BIND_TCP
#define LANDLOCK_ACCESS_NET_BIND_TCP (1ULL << 0)
#define LANDLOCK_ACCESS_NET_CONNECT_TCP (1ULL << 1)
#endif

#ifndef LANDLOCK_ACCESS_FS_IOCTL_DEV
#define LANDLOCK_ACCESS_FS_IOCTL_DEV (1ULL << 15)
#endif

#ifndef LANDLOCK_RULE_NET_PORT
#define LANDLOCK_RULE_NET_PORT 2
struct landlock_net_port_attr {
    __u64 allowed_access;
    __u64 port;
};
#endif

class ScopedFd {
    int fd_{-1};
public:
    explicit ScopedFd(int fd = -1) : fd_(fd) {}
    ~ScopedFd() { if (fd_ >= 0) ::close(fd_); }
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ScopedFd(ScopedFd&& o) noexcept : fd_(std::exchange(o.fd_, -1)) {}
    ScopedFd& operator=(ScopedFd&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = std::exchange(o.fd_, -1);
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    explicit operator bool() const noexcept { return fd_ >= 0; }
};

class LandlockSandbox {
    static int sys_landlock_create_ruleset(const struct landlock_ruleset_attr *attr, size_t size, __u32 flags) {
        return static_cast<int>(::syscall(__NR_landlock_create_ruleset, attr, size, flags));
    }
    static int sys_landlock_add_rule(int ruleset_fd, enum landlock_rule_type rule_type, const void *rule_attr, __u32 flags) {
        return static_cast<int>(::syscall(__NR_landlock_add_rule, ruleset_fd, rule_type, rule_attr, flags));
    }
    static int sys_landlock_restrict_self(int ruleset_fd, __u32 flags) {
        return static_cast<int>(::syscall(__NR_landlock_restrict_self, ruleset_fd, flags));
    }

public:
    static void apply(std::uint16_t allowed_port, std::string_view allowed_path) {
        int abi = sys_landlock_create_ruleset(nullptr, 0, LANDLOCK_CREATE_RULESET_VERSION);
        if (abi < 1) {
            throw std::system_error(ENOSYS, std::generic_category(), "Landlock unsupported");
        }

        landlock_ruleset_attr attr{};
        attr.handled_access_fs = LANDLOCK_ACCESS_FS_READ_FILE | LANDLOCK_ACCESS_FS_READ_DIR;
        if (abi >= 5) {
            attr.handled_access_fs |= LANDLOCK_ACCESS_FS_IOCTL_DEV;
        }
        if (abi >= 4) {
            attr.handled_access_net = LANDLOCK_ACCESS_NET_BIND_TCP | LANDLOCK_ACCESS_NET_CONNECT_TCP;
        }

        ScopedFd ruleset{sys_landlock_create_ruleset(&attr, sizeof(attr), 0)};
        if (!ruleset) {
            throw std::system_error(errno, std::generic_category(), "landlock_create_ruleset failed");
        }

        ScopedFd dir{::open(allowed_path.data(), O_PATH | O_CLOEXEC)};
        if (dir) {
            landlock_path_beneath_attr path_attr{
                .allowed_access = LANDLOCK_ACCESS_FS_READ_FILE | LANDLOCK_ACCESS_FS_READ_DIR,
                .parent_fd = dir.get()
            };
            if (sys_landlock_add_rule(ruleset.get(), LANDLOCK_RULE_PATH_BENEATH, &path_attr, 0) < 0) {
                throw std::system_error(errno, std::generic_category(), "add VFS rule failed");
            }
        }

        if (abi >= 4) {
            landlock_net_port_attr net_attr{
                .allowed_access = LANDLOCK_ACCESS_NET_BIND_TCP,
                .port = allowed_port
            };
            if (sys_landlock_add_rule(ruleset.get(), LANDLOCK_RULE_NET_PORT, &net_attr, 0) < 0) {
                throw std::system_error(errno, std::generic_category(), "add Net rule failed");
            }
        }

        if (::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) < 0) {
            throw std::system_error(errno, std::generic_category(), "prctl NO_NEW_PRIVS failed");
        }

        if (sys_landlock_restrict_self(ruleset.get(), 0) < 0) {
            throw std::system_error(errno, std::generic_category(), "restrict_self failed");
        }

        std::cout << "[Landlock C++] Sandboxing active (ABI v" << abi << ")\n";
    }
};

int main() {
    try {
        LandlockSandbox::apply(8080, "/tmp");

        ScopedFd s1{::socket(AF_INET, SOCK_STREAM, 0)};
        sockaddr_in addr1{.sin_family = AF_INET, .sin_port = htons(8080)};
        if (::bind(s1.get(), reinterpret_cast<sockaddr*>(&addr1), sizeof(addr1)) == 0) {
            std::cout << "SUCCESS: bind(8080) permitted\n";
        }

        ScopedFd s2{::socket(AF_INET, SOCK_STREAM, 0)};
        sockaddr_in addr2{.sin_family = AF_INET, .sin_port = htons(9090)};
        if (::bind(s2.get(), reinterpret_cast<sockaddr*>(&addr2), sizeof(addr2)) < 0 && errno == EACCES) {
            std::cout << "SUCCESS: bind(9090) blocked with EACCES\n";
        }
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
:::

## 6. Компіляція та верифікація виконання

### Компіляція проєктів
Для збірки вихідних файлів використовується компілятор GCC або Clang з підтримкою C11 та C++20:

```bash
# Збірка C-версії
gcc -std=c11 -O2 -Wall -Wextra sandbox_daemon.c -o sandbox_daemon_c

# Збірка C++ версії
g++ -std=c++20 -O2 -Wall -Wextra sandbox_daemon.cpp -o sandbox_daemon_cpp
```

### Запуск та аналіз результатів
Запуск згенерованого бінарного файла у середовищі ядра Linux 6.7+ демонструє наступний вивід:

```text
Landlock ABI версія: 4
Пісочницю успішно застосовано!
УСПІХ: bind(8080) дозволено
УСПІХ: bind(9090) заблоковано ядром (EACCES)
```

Результати тестування підтверджують, що ядро Linux успішно перехоплює системний виклик `bind()` для неописаного порту `9090` і відхиляє його з кодом помилки `EACCES`, тоді як порт `8080` успішно проходить перевірку у таблиці правил активного Landlock domain.
