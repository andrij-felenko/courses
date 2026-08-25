# 📋 Інтерфейс системного журналу: сокети, двійковий протокол та C/C++ API

Специфікація програмного контракту підсистеми `systemd-journald` охоплює точки входу в системні сокети, низькорівневу розкладку вхідних датаграм native-протоколу, номенклатуру системних і користувацьких полів, а також повне C/C++ API бібліотеки `libsystemd`.

## Точки входу та сокети системного менеджера

Підсистема journald приймає повідомлення через п'ять основних системних сокетів, які створюються та контролюються безпосередньо PID 1 systemd за допомогою юнітів типу `.socket` (соціальна техніка сокет-активації):

| Шлях до сокета | Тип та протокол | Призначення та формат | Права та параметри ядра |
| :--- | :--- | :--- | :--- |
| `/run/systemd/journal/socket` | `AF_UNIX` / `SOCK_DGRAM` | Рідний (native) протокол journald. Приймає структуровані датаграми ключ-значення. | `0666`, `SO_PASSCRED`, `SO_PASSSEC`, `SO_RCVBUF=8M` |
| `/run/systemd/journal/dev-log` | `AF_UNIX` / `SOCK_DGRAM` | Сумісність із застарілим `syslog()` API (символьне посилання `/dev/log`). | `0666`, `SO_PASSCRED`, `SO_PASSSEC` |
| `/run/systemd/journal/stdout` | `AF_UNIX` / `SOCK_STREAM` | Потоковий сокет для перехоплення `stdout` та `stderr` служб systemd. | `0666`, `PassFD=yes` |
| `/dev/kmsg` | Спеціальний файл | Буфер повідомлень ядра Linux (`printk`). Зчитується демоном безпосередньо. | `0644` (чорнова вибірка ядра) |
| Netlink Audit Socket | `AF_NETLINK` / `NETLINK_AUDIT` | Отримання подій безпеки та системного аудиту від ядра Linux. | Привілеї `CAP_AUDIT_READ` |

Для забезпечення автентичності відправника на сокетах `/run/systemd/journal/socket` та `/run/systemd/journal/dev-log` увімкнено прапорці ядра `SO_PASSCRED` та `SO_PASSSEC`. Це зобов'язує ядро Linux приєднувати до кожної переданої датаграми структуру службових повідомлень `struct cmsghdr` з типом `SCM_CREDENTIALS`, що містить унікальні метадані `struct ucred` (`pid`, `uid`, `gid`), а також текстовий безпековий контекст SELinux чи AppArmor.

## Бланк рідного протоколу (Native Wire Protocol)

Кожна датаграма, що відправляється у сокет `/run/systemd/journal/socket`, є послідовністю полів. Поле може передаватися в одній із двох форм:

1. **Текстова форма** (використовується, якщо значення не містить символів переходу рядка `\n` або нульових байтів `\0`):
   `ІМ'Я_ПОЛЯ=значення\n`
2. **Двійкова binary-safe форма** (якщо значення містить переноси рядків, бінарні байти або нульові символи):
   `ІМ'Я_ПОЛЯ\n` (ім'я поля та символ `\n`) + 64-бітне ціле число в форматі Little-Endian (довжина значення в байтах) + самі байти значення + підсумковий символ `\n`.

Схема двійкової розкладки датаграми у пам'яті:

```text
+-----------------------------------------------------------------------+
| MESSAGE=Database service started\n                                    |  <- Текстове поле
+-----------------------------------------------------------------------+
| PRIORITY=6\n                                                          |  <- Текстове поле
+-----------------------------------------------------------------------+
| PAYLOAD\n                                                             |  <- Поле двійкового блоба
| 0x08 0x00 0x00 0x00 0x00 0x00 0x00 0x00 (64-бітне число довжини = 8)  |
| 0x89 0x50 0x4E 0x47 0x0D 0x0A 0x1A 0x0A (8 байтів бінарних даних)       |
| \n                                                                    |
+-----------------------------------------------------------------------+
| \n                                                                    |  <- Порожній рядок (кінець запису)
+-----------------------------------------------------------------------+
```

Завершується датаграма порожнім рядком `\n` або досягненням кінця датаграми Unix-сокета. Якщо розмір запису перевищує максимальний допустимий розмір датаграми сокета (типово 8 МБ), відправник створює анонімний файл у пам'яті за допомогою системного виклику `memfd_create()`, записує туди датаграму, запечатує файл від змін викликом `fcntl(fd, F_ADD_SEALS, F_SEAL_SEAL)` і передає сам файловий дескриптор через виклик `sendmsg()` із допоміжним типом `SCM_RIGHTS`.

## Повний каталог полів запису

Поля в записі системного журналу розділяються на три основні категорії:

### 1. Поля відправника (Клієнтські поля)
Формуються самою програмою-клієнтом. Не мають префікса підкреслення:
- `MESSAGE`: текстове повідомлення події для людини.
- `PRIORITY`: числовий рівень пріоритету syslog (0 — `emerg`, 1 — `alert`, 2 — `crit`, 3 — `err`, 4 — `warning`, 5 — `notice`, 6 — `info`, 7 — `debug`).
- `SYSLOG_IDENTIFIER`: ім'я програми або тег (наприклад `sshd` або `my-app`).
- `SYSLOG_FACILITY`: числовий код категорії syslog (0 — `kernel`, 1 — `user`, 3 — `daemon`, 4 — `auth`, 9 — `cron`, 10 — `authpriv`).
- `SYSLOG_PID`: процес-ідентифікатор, задекларований клієнтом (неперевірений).
- `ERRNO`: числовий код системної помилки `errno` (наприклад `11` для `EAGAIN` або `2` для `ENOENT`).
- `CODE_FILE`, `CODE_LINE`, `CODE_FUNC`: джерельний файл, рядок і назва функції в коді програми, де виник лог.
- `MESSAGE_ID`: 128-бітний унікальний UUID у 16-тковому форматі (наприклад `8daee1d3b9a04f8e9b2c1d0a77e51234`) для каталогізації типових подій.

### 2. Довірені метаполя демона та ядра (Trusted Metadata Fields)
Автоматично додаються journald на основі даних від ядра та аналізу `/proc/<PID>/`. Будь-яка спроба клієнта передати власне поле з префіксом `_` відкидається демоном:
- `_PID`: ідентифікатор процесу-відправника (перевірено ядром через `SO_PASSCRED`).
- `_UID`, `_GID`: реальні ідентифікатори користувача та групи процесу.
- `_COMM`: коротке ім'я виконуваного файлу процесу (з `/proc/<PID>/comm`).
- `_EXE`: канонічний абсолютний шлях до виконуваного файлу (з `/proc/<PID>/exe`).
- `_CMDLINE`: повний рядок аргументів запуску процесу через пробіли чи нульові байти.
- `_SYSTEMD_UNIT`: назва юніта systemd (визначається з `/proc/<PID>/cgroup`).
- `_SYSTEMD_SLICE`: назва зрізу cgroups (наприклад `system.slice` або `user.slice`).
- `_SYSTEMD_USER_UNIT`: назва юніта у сесії користувача.
- `_BOOT_ID`: 128-бітний UUID поточного сеансу завантаження системи.
- `_MACHINE_ID`: унікальний ідентифікатор хоста з `/etc/machine-id`.
- `_HOSTNAME`: мережеве ім'я хоста, зчитане демоном.
- `_TRANSPORT`: спосіб потрапляння запису в демон (`journal`, `syslog`, `stdout`, `kernel`, `audit`, `driver`).

### 3. Метаполя ядра Linux (Kernel Metadata Fields)
- `_KERNEL_DEVICE`: текстовий ідентифікатор пристрою ядра (наприклад `+pci:0000:00:1f.2`).
- `_KERNEL_SUBSYSTEM`: назва підсистеми ядра (наприклад `net`, `input`, `acpi`).
- `_UDEV_SYSNAME`: назва пристрою у файловій системі sysfs (наприклад `sda1` або `eth0`).
- `_UDEV_DEVNODE`: шлях до файлу пристрою у `/dev/` (наприклад `/dev/sda1`).

## Повний опис C та C++ API (libsystemd)

Для роботи із системним журналом програми на C та C++ використовують заголовковий файл `<systemd/sd-journal.h>` та лінкують бібліотеку `-lsystemd`.

### Функції запису логів

Бібліотека надає як прості виклики форматування, так і структуровані варіанти:

```c
/* Простий вивід у стилі printf */
int sd_journal_print(int priority, const char *format, ...);
int sd_journal_printv(int priority, const char *format, va_list ap);

/* Структурований вивід ключ-значення */
int sd_journal_send(const char *format, ...);
int sd_journal_sendv(const struct iovec *iov, int n);

/* Запис із явним вказуванням location у коді */
int sd_journal_send_with_location(const char *file, const char *line, const char *func, const char *format, ...);
```

### Функції читання, навігації та фільтрації

Двонаправлена навігація та встановлення фільтрів виконуються через структуру `sd_journal*`:

```c
/* Відкриття та закриття сесії журналу */
int sd_journal_open(sd_journal **ret, int flags);
void sd_journal_close(sd_journal *j);

/* Прапорці відкриття (flags): */
/* SD_JOURNAL_LOCAL_ONLY    - лише локальні логи поточного хоста */
/* SD_JOURNAL_RUNTIME_ONLY  - лише тимчасові логи з /run (tmpfs) */
/* SD_JOURNAL_SYSTEM        - лише системні логи (без логів користувачів) */
/* SD_JOURNAL_CURRENT_USER   - лише логи поточного користувача */

/* Додавання та скидання фільтрів (matches) */
int sd_journal_add_match(sd_journal *j, const void *data, size_t size);
int sd_journal_add_disjunction(sd_journal *j); // Логічне АБО (OR)
int sd_journal_add_conjunction(sd_journal *j); // Логічне І (AND)
void sd_journal_flush_matches(sd_journal *j);  // Очищення всіх фільтрів

/* Навігація покажчиком читання */
int sd_journal_next(sd_journal *j);
int sd_journal_previous(sd_journal *j);
int sd_journal_seek_head(sd_journal *j);
int sd_journal_seek_tail(sd_journal *j);
int sd_journal_seek_monotonic_usec(sd_journal *j, sd_id128_t boot_id, uint64_t usec);
int sd_journal_seek_realtime_usec(sd_journal *j, uint64_t usec);
int sd_journal_seek_cursor(sd_journal *j, const char *cursor);

/* Отримання даних та стан курсора */
int sd_journal_get_data(sd_journal *j, const char *field, const void **data, size_t *l);
int sd_journal_get_cursor(sd_journal *j, char **cursor);
int sd_journal_test_cursor(sd_journal *j, const char *cursor);

/* Асинхронне відстеження нових подій через epoll/poll */
int sd_journal_get_fd(sd_journal *j);
int sd_journal_get_events(sd_journal *j);
int sd_journal_get_timeout(sd_journal *j, uint64_t *timeout_usec);
int sd_journal_process(sd_journal *j);
int sd_journal_wait(sd_journal *j, uint64_t timeout_usec);
```

### Комплексні приклади відправки та читання

:::tabs
```c
/* example_api.c — повний приклад відправки та фільтрації C API */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <systemd/sd-journal.h>

void send_structured_log_c(void) {
    int res = sd_journal_send(
        "MESSAGE=Старт обробки транзакції клієнта",
        "PRIORITY=%d", LOG_NOTICE,
        "TRANSACTION_ID=TX-9948201",
        "AMOUNT_CENT=150000",
        "CURRENCY=UAH",
        "CODE_FILE=%s", __FILE__,
        "CODE_LINE=%d", __LINE__,
        NULL
    );

    if (res < 0) {
        fprintf(stderr, "Не вдалося відправити лог у journald: %s\n", strerror(-res));
    }
}

void poll_journal_events_c(void) {
    sd_journal *j = NULL;
    if (sd_journal_open(&j, SD_JOURNAL_LOCAL_ONLY) < 0) return;

    /* Фільтруємо логи системного сервісу sshd */
    sd_journal_add_match(j, "_SYSTEMD_UNIT=sshd.service", 0);
    sd_journal_seek_tail(j);

    printf("Очікування нових подій від sshd.service...\n");
    for (int i = 0; i < 3; ++i) {
        /* Чекаємо нових даних на сокеті (таймаут 5 секунд) */
        int r = sd_journal_wait(j, 5000000);
        if (r == SD_JOURNAL_NOP) {
            printf("Таймаут очікування подій...\n");
            continue;
        }

        while (sd_journal_next(j) > 0) {
            const void *msg = NULL;
            size_t len = 0;
            if (sd_journal_get_data(j, "MESSAGE", &msg, &len) >= 0) {
                printf("Нова подія: %.*s\n", (int)len, (const char*)msg);
            }
        }
    }

    sd_journal_close(j);
}
```
```cpp
// example_api.cpp — ідіоматичний C++20 варіант
#include <iostream>
#include <memory>
#include <string_view>
#include <format>
#include <array>
#include <systemd/sd-journal.h>

class JournalAPIWrapper {
    struct JournalCloser {
        void operator()(sd_journal *j) const noexcept {
            if (j) sd_journal_close(j);
        }
    };
    std::unique_ptr<sd_journal, JournalCloser> handle_;

public:
    JournalAPIWrapper() {
        sd_journal *raw = nullptr;
        if (sd_journal_open(&raw, SD_JOURNAL_LOCAL_ONLY) < 0) {
            throw std::runtime_error("Не вдалося відкрити журнал systemd");
        }
        handle_.reset(raw);
    }

    static void send_transaction_log(std::string_view tx_id, uint64_t amount_cent) {
        std::string msg = std::format("MESSAGE=Старт обробки транзакції {}", tx_id);
        std::string prio = std::format("PRIORITY={}", LOG_NOTICE);
        std::string tx = std::format("TRANSACTION_ID={}", tx_id);
        std::string amt = std::format("AMOUNT_CENT={}", amount_cent);

        int r = sd_journal_send(
            msg.c_str(),
            prio.c_str(),
            tx.c_str(),
            amt.c_str(),
            "CURRENCY=UAH",
            nullptr
        );
        if (r < 0) {
            std::cerr << "Помилка відправки логу: " << strerror(-r) << "\n";
        }
    }

    void watch_unit_events(std::string_view unit_name) {
        std::string match = std::format("_SYSTEMD_UNIT={}", unit_name);
        sd_journal_add_match(handle_.get(), match.c_str(), 0);
        sd_journal_seek_tail(handle_.get());

        std::cout << std::format("Моніторинг подій {} через C++ epoll...\n", unit_name);
        for (int i = 0; i < 3; ++i) {
            int r = sd_journal_wait(handle_.get(), 5000000); // 5 sec timeout
            if (r == SD_JOURNAL_NOP) {
                std::cout << "Очікування нових записів...\n";
                continue;
            }

            while (sd_journal_next(handle_.get()) > 0) {
                const void *data = nullptr;
                size_t len = 0;
                if (sd_journal_get_data(handle_.get(), "MESSAGE", &data, &len) >= 0) {
                    std::string_view msg_sv(static_cast<const char*>(data), len);
                    std::cout << std::format("Отримано: {}\n", msg_sv);
                }
            }
        }
    }
};
```
:::
