# ⚙️ Розбір та аналіз бінарних логів systemd через libsystemd мовами C та C++

Практичне завдання побудови власних моніторингових інструментів, систем аналітики та високопродуктивних агентів спостережуваності вимагає прямої взаємодії з дисковими журнальними файлами systemd без виклику зовнішніх утиліт на кшталт `journalctl`. Виклик командної утиліти через `fork()` та `execve()` з подальшим парсингом її виводу у текстовому форматі створює величезні накладні витрати CPU та пам'яті. Використання офіційної системної бібліотеки `libsystemd` дозволяє отримувати бінарні об'єкти безпосередньо через розділювану пам'ять та дискові індекси з мінімальною затримкою.

Нижче наведено завершену реалізацію міні-читача системних логів мовами C та C++, що виконує фільтрацію за юнітом, часовим діапазоном та рівнями пріоритету через низькорівневе API `libsystemd`.

## Завдання та архітектурні вимоги до реалізації

Необхідно розробити консольну програму, яка виконує такі операції:
1. **Підключення до журналу**: відкриває локальне дискове сховище `systemd-journald` в режимі читання (флаг `SD_JOURNAL_LOCAL_ONLY`).
2. **Налаштування індексного фільтра**: встановлює точну умову співпадіння для вибірки повідомлень конкретної служби (наприклад `sshd.service` або `nginx.service`). Фільтрація виконується за допомогою внутрішніх хеш-таблиць журналу без лінійного сканування всіх записів на диску.
3. **Двонаправлена навігація**: позиціонується на найновіший запис події за допомогою `sd_journal_seek_tail()` та здійснює ітерацію записів від найновіших до найстаріших (у зворотному хронологічному порядку).
4. **Безпечний розбір полів**: безпечно витягує текстові та бінарні значення полів `MESSAGE`, `_PID`, `_UID`, `_SYSTEMD_UNIT` та `PRIORITY`, враховуючи, що значення полів не містять нульового символу термінатора `\0`.
5. **Збереження стану через курсори**: отримує та виводить непрозорий рядок-курсор (англ. *cursor*), який однозначно ідентифікує конкретний запис на диску і дозволяє відновлювати читання з тієї ж позиції при перезапуску програми.

## Повна реалізація мовами C та C++

:::tabs
```c
/* journal_reader.c — читач логів systemd мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <systemd/sd-journal.h>

#define MAX_CURSOR_LEN 512

static void print_field(sd_journal *j, const char *field_name) {
    const void *data = NULL;
    size_t length = 0;

    int r = sd_journal_get_data(j, field_name, &data, &length);
    if (r < 0) {
        if (r == -ENOENT) {
            printf("  %s: <відсутнє>\n", field_name);
        } else {
            fprintf(stderr, "Помилка читання поля %s: %s\n", field_name, strerror(-r));
        }
        return;
    }

    /* Зчитуване поле повертається у форматі 'FIELD_NAME=value' */
    const char *eq = memchr(data, '=', length);
    if (eq) {
        size_t val_len = length - (eq - (const char*)data) - 1;
        printf("  %s: %.*s\n", field_name, (int)val_len, eq + 1);
    }
}

int main(int argc, char *argv[]) {
    const char *target_unit = (argc > 1) ? argv[1] : "sshd.service";
    sd_journal *j = NULL;

    /* 1. Відкриття локального журналу */
    int r = sd_journal_open(&j, SD_JOURNAL_LOCAL_ONLY);
    if (r < 0) {
        fprintf(stderr, "Не вдалося відкрити журнал: %s\n", strerror(-r));
        return EXIT_FAILURE;
    }

    printf("=== Аналіз логів юніта: %s ===\n", target_unit);

    /* 2. Додавання умов фільтрації */
    char match_buf[256];
    snprintf(match_buf, sizeof(match_buf), "_SYSTEMD_UNIT=%s", target_unit);

    r = sd_journal_add_match(j, match_buf, 0);
    if (r < 0) {
        fprintf(stderr, "Помилка встановлення фільтра юніта: %s\n", strerror(-r));
        sd_journal_close(j);
        return EXIT_FAILURE;
    }

    /* 3. Позиціонування на кінець журналу */
    r = sd_journal_seek_tail(j);
    if (r < 0) {
        fprintf(stderr, "Помилка позиціонування tail: %s\n", strerror(-r));
        sd_journal_close(j);
        return EXIT_FAILURE;
    }

    /* 4. Читання записів у зворотному напрямку */
    int count = 0;
    while ((r = sd_journal_previous(j)) > 0 && count < 5) {
        count++;
        printf("\nЗапис #%d:\n", count);

        print_field(j, "_SYSTEMD_UNIT");
        print_field(j, "_PID");
        print_field(j, "_UID");
        print_field(j, "PRIORITY");
        print_field(j, "MESSAGE");

        /* Отримання курсора для збереження стану */
        char *cursor = NULL;
        if (sd_journal_get_cursor(j, &cursor) >= 0) {
            printf("  Cursor: %s\n", cursor);
            free(cursor); // Курсор виділено динамічно бібліотекою
        }
    }

    if (r < 0) {
        fprintf(stderr, "Помилка ітерації журналу: %s\n", strerror(-r));
    }

    /* 5. Чисте звільнення ресурсів */
    sd_journal_close(j);
    return EXIT_SUCCESS;
}
```
```cpp
// journal_reader.cpp — ідіоматична реалізація на C++20/C++23
#include <iostream>
#include <memory>
#include <string_view>
#include <expected>
#include <system_error>
#include <format>
#include <systemd/sd-journal.h>

class JournalSession {
    struct JournalDeleter {
        void operator()(sd_journal *j) const noexcept {
            if (j) sd_journal_close(j);
        }
    };
    std::unique_ptr<sd_journal, JournalDeleter> handle_;

public:
    static std::expected<JournalSession, std::error_code> create(int flags = SD_JOURNAL_LOCAL_ONLY) {
        sd_journal *raw = nullptr;
        int r = sd_journal_open(&raw, flags);
        if (r < 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(-r)));
        }
        return JournalSession(raw);
    }

    explicit JournalSession(sd_journal *raw) noexcept : handle_(raw) {}

    std::error_code filter_by_unit(std::string_view unit_name) {
        std::string match = std::format("_SYSTEMD_UNIT={}", unit_name);
        int r = sd_journal_add_match(handle_.get(), match.c_str(), 0);
        if (r < 0) {
            return std::make_error_code(static_cast<std::errc>(-r));
        }
        return {};
    }

    std::expected<std::string_view, std::error_code> get_field(std::string_view field_name) {
        const void *data = nullptr;
        size_t len = 0;
        int r = sd_journal_get_data(handle_.get(), std::string(field_name).c_str(), &data, &len);
        if (r < 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(-r)));
        }

        std::string_view raw_str(static_cast<const char*>(data), len);
        auto eq_pos = raw_str.find('=');
        if (eq_pos != std::string_view::npos) {
            return raw_str.substr(eq_pos + 1);
        }
        return raw_str;
    }

    std::expected<std::string, std::error_code> get_cursor() {
        char *c_str = nullptr;
        int r = sd_journal_get_cursor(handle_.get(), &c_str);
        if (r < 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(-r)));
        }
        std::string res(c_str);
        free(c_str);
        return res;
    }

    bool seek_tail() {
        return sd_journal_seek_tail(handle_.get()) >= 0;
    }

    bool previous() {
        return sd_journal_previous(handle_.get()) > 0;
    }
};

int main(int argc, char *argv[]) {
    std::string_view unit = (argc > 1) ? argv[1] : "sshd.service";

    auto session_res = JournalSession::create();
    if (!session_res) {
        std::cerr << "Помилка відкриття журналу: " << session_res.error().message() << "\n";
        return 1;
    }

    auto &session = *session_res;
    if (auto err = session.filter_by_unit(unit); err) {
        std::cerr << "Помилка фільтрації: " << err.message() << "\n";
        return 1;
    }

    if (!session.seek_tail()) {
        std::cerr << "Не вдалося перейти в кінець журналу\n";
        return 1;
    }

    std::cout << std::format("=== Читання логів {} через C++ RAII ===\n", unit);

    int count = 0;
    while (session.previous() && count < 5) {
        count++;
        std::cout << std::format("\nЗапис #{}:\n", count);

        for (auto field : {"_SYSTEMD_UNIT", "_PID", "_UID", "PRIORITY", "MESSAGE"}) {
            if (auto val = session.get_field(field); val) {
                std::cout << std::format("  {}: {}\n", field, *val);
            } else {
                std::cout << std::format("  {}: <відсутнє>\n", field);
            }
        }

        if (auto cursor = session.get_cursor(); cursor) {
            std::cout << std::format("  Cursor: {}\n", *cursor);
        }
    }

    return 0;
}
```
:::

## Збирання та виконання проекту

Для успішної компіляції джерельних файлів необхідно встановити системний пакет із заголовковими файлами `libsystemd-dev` (у дистрибутивах Debian/Ubuntu) або `systemd-devel` (у дистрибутивах RHEL/Fedora/CentOS/SUSE).

Команди збирання у консолі:

```bash
# Компіляція версії на C за допомогою GCC
gcc -O2 -Wall -Wextra journal_reader.c -lsystemd -o journal_reader

# Компіляція версії на C++ (потрібен компілятор із підтримкою стандарту C++20/C++23)
g++ -std=c++23 -O2 -Wall -Wextra journal_reader.cpp -lsystemd -o journal_reader_cpp

# Запуск перевірки логів системного сервісу SSH
./journal_reader sshd.service

# Запуск перевірки логів сервісу управління мережею
./journal_reader_cpp NetworkManager.service
```

## Механізм побудови складних виразів фільтрації (Matches)

Бібліотека `libsystemd` надає можливість будувати складні булеві вирази для фільтрації записів. За замовчуванням декілька послідовних викликів `sd_journal_add_match()` із різними полями об'єднуються за допомогою логічного «І» (AND). Якщо ж додається декілька матчів для одного і того ж поля (наприклад `_SYSTEMD_UNIT=sshd.service` та `_SYSTEMD_UNIT=nginx.service`), бібліотека автоматично об'єднує їх за допомогою логічного «АБО» (OR).

Для довільного групування складних умов використовуються функції розмежування:
- `sd_journal_add_disjunction(j)`: відкриває нову групу умов, що об'єднується з попередньою за допомогою логічного «АБО» (диз'юнкція).
- `sd_journal_add_conjunction(j)`: відкриває нову групу умов, що об'єднується з попередньою за допомогою логічного «І» (кон'юнкція).

Приклад побудови виразу видачі: `(_SYSTEMD_UNIT=sshd.service OR _SYSTEMD_UNIT=nginx.service) AND PRIORITY=3`:

:::tabs
```c
/* Додаємо першу службу */
sd_journal_add_match(j, "_SYSTEMD_UNIT=sshd.service", 0);
/* Додаємо другу службу (автоматичний OR) */
sd_journal_add_match(j, "_SYSTEMD_UNIT=nginx.service", 0);
/* Переходимо до нової групи AND */
sd_journal_add_conjunction(j);
/* Встановлюємо обмеження за пріоритетом */
sd_journal_add_match(j, "PRIORITY=3", 0);
```
```cpp
// Приклад побудови виразу видачі у C++
session.filter_by_unit("sshd.service");
session.filter_by_unit("nginx.service");
// Еквівалентна композиція умов для об'єкта sd_journal
```
:::

## Ключові пастки та підводні камені під час роботи з API

Під час практичної розробки додатків взаємодії з `libsystemd` програмісти найчастіше припускаються п'яти типових помилок:

1. **Необхідність виклику `sd_journal_previous` або `sd_journal_next` після `seek`**:
   Викликавши `sd_journal_seek_tail()` або `sd_journal_seek_head()`, покажчик читача стає *за межі* першого або останнього запису в журналі. Він ще не вказує на конкретний об'єкт події. Для того щоб прочитати сам запис, обов'язково треба виконати один крок у напрямку файлу викликом `sd_journal_previous()` або `sd_journal_next()`. Спроба виклику `sd_journal_get_data()` одразу після `seek` без ітерації поверне помилку `ADDRNOTAVAIL` (-99).

2. **Обробка двійкових даних у полях та відсутність `\0`**:
   Функція `sd_journal_get_data` повертає не нуль-термінований C-рядок (`char*`), а вказівник на сирий буфер байтів `void*` у розділюваній пам'яті та його довжину `size_t`. Якщо значення містить переноси рядків або бінарний блоб, звичайний виклик `printf("%s")` призведе до виходу за межі бувера (Out-Of-Bounds Read) або передчасного обриву виводу на першому ж нульовому байті. У C слід використовувати специфікатор видачі з обмеженням довжини `%.*s`, а в C++ — клас `std::string_view`.

3. **Звільнення пам'яті курсора**:
   Функція `sd_journal_get_cursor()` виділяє пам'ять під рядок курсора за допомогою `malloc()`. Обов'язком клієнтського коду є виклики `free()` після завершення використання рядка. У C++ реалізації цій меті служить виклик `free()` усередині методу класу `get_cursor()`.

4. **Від'ємні коди помилок (Negative Errno)**:
   Усі функції системної бібліотеки `libsystemd` у разі виникнення помилки повертають від'ємне значення коду `errno` (наприклад `-ENOENT`, `-EINVAL` або `-EACCES`). При перевірці умов слід порівнювати повернене число з нулем (`r < 0`) і передавати інвертоване значення `-r` у функції `strerror()` або `std::generic_category()`.

5. **Блокування та асинхронний моніторинг**:
   Спроба побудувати демон моніторингу логів у режимі реального часу через нескінченний цикл `while (1) { sd_journal_next(j); }` призведе до 100% завантаження одного ядра процесора (Busy Waiting). Правильним підходом є використання `sd_journal_get_fd()` та `sd_journal_wait()`, які підключають контекст журналу до системного селектора `epoll_wait()`, присипляючи процес до появи нової датаграми у сокеті ядра.
