# ⚙️ Програмне читання та модифікація SecurityFS TOMOYO

При розробці системних утилит адміністрування, оркестраторів контейнерів та моніторів безпеки виникає потреба програмно зчитувати стан політики TOMOYO Linux, аналізувати лічильники використання пам'яті ядра та динамічно додавати нові правила до SecurityFS без використання сторонніх утилит на кшталт `tomoyo-tools`. Цей приклад розкриває практичну взаємодію з віртуальними файлами у каталозі `/sys/kernel/security/tomoyo/` мовами системного програмування C та C++.

---

## 1. Архітектурне завдання та системний контекст

У багатьох виробничих середовищах стандартні утиліти `tomoyo-tools` можуть бути відсутні (наприклад, у мінімалістичних контейнерних дистрибутивах Alpine Linux, ущільнених прошивках вбудованих систем або при розробці власного агента моніторингу). У таких випадках додаток повинен самостійно виконувати низькорівневий I/O-обмін із віртуальною файловою системою SecurityFS.

Файлова система SecurityFS монтується за шляхом `/sys/kernel/security` за допомогою виклику `mount -t securityfs none /sys/kernel/security`. Для підсистеми TOMOYO Linux виділяється підкаталог `/sys/kernel/security/tomoyo/`, у якому розміщуються спеціальні віртуальні файли. Зчитування та запис у ці файли не виконують дій над блоковими пристроями, а викликають внутрішні функції обробки LSM у ядрі.

Для досягнення цієї мети утиліта повинна вирішувати такі практичні завдання:

1. **Діагностика наявності LSM-підсистеми:** Перевірити, чи змонтовано віртуальну файлову систему SecurityFS за шляхом `/sys/kernel/security` і чи активовано в ядрі модуль TOMOYO Linux (наявність каталогу `/sys/kernel/security/tomoyo/`).
2. **Зчитування системної статистики:** Прочитати псевдофайл `stat`, витягти поточну інформацію про кількість зареєстрованих доменів у дереві, обсяг використаної пам'яті під правила та лічильники блокувань.
3. **Атомарний запис нових правил:** Сформувати правильно відформатований рядок із назвою домену та правилом доступу, після чого записати його у файл `domain_policy`.
4. **Обробка виняткових ситуацій та прав доступу:** Коректно обробити помилку `EPERM`, яка виникає у разі, якщо домен поточного процесу не внесено до списку дозволених менеджерів у файлі `manager.conf`.

---

## 2. Реалізація мовами C та C++

Нижче наведено дві повноцінні реалізації утиліти моніторингу та управління політиками TOMOYO. Перший варіант написано класичною мовою C із використанням низькорівневих системних викликів POSIX (`open`, `read`, `write`, `close`), а другий — ідіоматичною мовою C++20 із застосуванням концепції RAII, файлових потоків STL, обробки помилок через `std::expected` та безапеляційної пам'ятної безпеки.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/stat.h>

#define TOMOYO_STAT_PATH "/sys/kernel/security/tomoyo/stat"
#define TOMOYO_DOMAIN_PATH "/sys/kernel/security/tomoyo/domain_policy"
#define BUFFER_SIZE 4096

/* Зчитування та виведення вмісту файлу статистики SecurityFS */
static int read_tomoyo_stat(void) {
    int fd = open(TOMOYO_STAT_PATH, O_RDONLY);
    if (fd < 0) {
        if (errno == ENOENT) {
            fprintf(stderr, "Помилка: TOMOYO LSM не активовано або SecurityFS не змонтовано.\n");
        } else {
            fprintf(stderr, "Помилка відкриття %s: %s\n", TOMOYO_STAT_PATH, strerror(errno));
        }
        return -1;
    }

    char buffer[BUFFER_SIZE];
    ssize_t bytes_read;

    printf("=== Статистика ядра TOMOYO Linux (%s) ===\n", TOMOYO_STAT_PATH);
    while ((bytes_read = read(fd, buffer, sizeof(buffer) - 1)) > 0) {
        buffer[bytes_read] = '\0';
        fputs(buffer, stdout);
    }

    if (bytes_read < 0) {
        fprintf(stderr, "Помилка зчитування даних: %s\n", strerror(errno));
        close(fd);
        return -1;
    }

    close(fd);
    return 0;
}

/* Динамічне додавання правила до domain_policy */
static int append_domain_rule(const char *domain, const char *rule) {
    int fd = open(TOMOYO_DOMAIN_PATH, O_WRONLY | O_APPEND);
    if (fd < 0) {
        fprintf(stderr, "Помилка запису в %s: %s (перевірте manager.conf та root-права)\n",
                TOMOYO_DOMAIN_PATH, strerror(errno));
        return -1;
    }

    char payload[BUFFER_SIZE];
    int len = snprintf(payload, sizeof(payload), "%s\n%s\n", domain, rule);
    if (len < 0 || (size_t)len >= sizeof(payload)) {
        fprintf(stderr, "Помилка: занадто довгий рядок правила.\n");
        close(fd);
        return -1;
    }

    ssize_t written = write(fd, payload, len);
    if (written != len) {
        fprintf(stderr, "Помилка запису правила у SecurityFS: %s\n", strerror(errno));
        close(fd);
        return -1;
    }

    printf("Успішно додано правило [%s] для домену [%s]\n", rule, domain);
    close(fd);
    return 0;
}

int main(int argc, char *argv[]) {
    if (read_tomoyo_stat() != 0) {
        return EXIT_FAILURE;
    }

    if (argc == 3) {
        const char *target_domain = argv[1];
        const char *target_rule = argv[2];
        if (append_domain_rule(target_domain, target_rule) != 0) {
            return EXIT_FAILURE;
        }
    } else {
        printf("\nВикористання для додавання правила:\n");
        printf("  %s \"<kernel> /usr/sbin/nginx\" \"file read /etc/nginx/nginx.conf\"\n", argv[0]);
    }

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <filesystem>
#include <system_error>
#include <expected>

namespace fs = std::filesystem;

class TomoyoSecurityFS {
public:
    static constexpr std::string_view SecurityFSRoot = "/sys/kernel/security/tomoyo";

    TomoyoSecurityFS() {
        if (!fs::exists(SecurityFSRoot)) {
            throw std::runtime_error("TOMOYO SecurityFS не знайдено за шляхом: " + 
                                     std::string(SecurityFSRoot));
        }
    }

    // Зчитування статистики ядра у формі рядка
    [[nodiscard]] std::expected<std::string, std::string> readStatistics() const {
        const fs::path statPath = fs::path(SecurityFSRoot) / "stat";
        std::ifstream statFile(statPath);

        if (!statFile.is_open()) {
            return std::unexpected("Не вдалося відкрити файл статистики: " + statPath.string());
        }

        std::string content((std::istreambuf_iterator<char>(statFile)),
                             std::istreambuf_iterator<char>());
        return content;
    }

    // Динамічний запис правила доменів через RAII файловий потік
    [[nodiscard]] std::expected<void, std::string> appendRule(std::string_view domain, 
                                                             std::string_view rule) const {
        const fs::path policyPath = fs::path(SecurityFSRoot) / "domain_policy";
        std::ofstream policyFile(policyPath, std::ios::app);

        if (!policyFile.is_open()) {
            return std::unexpected("Не вдалося відкрити domain_policy для запису. "
                                   "Перевірте привілеї та вміст manager.conf.");
        }

        policyFile << domain << "\n" << rule << "\n";
        if (!policyFile.good()) {
            return std::unexpected("Помилка запису в domain_policy.");
        }

        return {};
    }
};

int main(int argc, char* argv[]) {
    try {
        TomoyoSecurityFS tomoyo;

        std::cout << "=== Системний монітор TOMOYO Linux (C++20) ===\n";
        auto statResult = tomoyo.readStatistics();
        if (statResult) {
            std::cout << *statResult << '\n';
        } else {
            std::cerr << "Помилка: " << statResult.error() << '\n';
            return EXIT_FAILURE;
        }

        if (argc == 3) {
            const std::string_view domain = argv[1];
            const std::string_view rule = argv[2];

            auto writeResult = tomoyo.appendRule(domain, rule);
            if (writeResult) {
                std::cout << "Успішно додано правило:\n  Домен: " << domain 
                          << "\n  Правило: " << rule << '\n';
            } else {
                std::cerr << "Помилка запису: " << writeResult.error() << '\n';
                return EXIT_FAILURE;
            }
        }

    } catch (const std::exception& ex) {
        std::cerr << "Критичний збій: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

---

## 3. Детальний аналіз реалізації та системні пастки

### Зчитування статистики з `/sys/kernel/security/tomoyo/stat`

Файл `stat` повертає багаторадкові текстові дані про внутрішній стан LSM-модуля. Причиною використання циклу `read()` у C-версії є те, що віртуальні файли у `/sys` зазвичай звітують про розмір 0 байтів при виклику `stat()`, оскільки вміст генерується "на льоту" функціями ядра при зверненні. Тому заздалегідь виділити буфер точного розміру за допомогою `lseek()` або `fstat()` неможливо.

У C++-версії ця особливість елегантно вирішується шляхом створення ітераторів входження потоку `std::istreambuf_iterator<char>`, які автоматично динамічно розширюють вектор або рядок `std::string` по мірі отримання нових даних від ядерного обробника.

### Обробка атомарних записів у SecurityFS

Особливістю віртуального файлу `/sys/kernel/security/tomoyo/domain_policy` є те, що ядро очікує чіткої послідовності рядків. Запис назви домену (наприклад, `<kernel> /usr/sbin/nginx`) переводить внутрішній парсер ядра у контекст обробки даного домену. Наступні рядки, передані у межах того самого системного виклику `write()` або файлової сесії, сприймаються ядром як правила доступу для цього домену.

У C-реалізації для забезпечення атомарності формується єдиний буфер за допомогою `snprintf`:
```text
int len = snprintf(payload, sizeof(payload), "%s\n%s\n", domain, rule);
write(fd, payload, len);
```
Це гарантує, що ядро отримає ім'я домену та сам рядок правила у межах одного системного виклику `write()`, запобігаючи стану гонки (`race condition`), якщо інші процеси паралельно здійснюють запис у `domain_policy`.

У C++-реалізації використовується файловий потік `std::ofstream` у режимі `std::ios::app`. Потік автоматом закриває дескриптор при виході з області видимості об'єкта завдяки деструктору RAII, усуваючи ризик витоку ресурсів дескрипторів файлів при виникненні винятків.

### Безпека та обмеження `manager.conf`

Якщо скомпілювати цей код і запустити його під обліковим записом `root` (UID 0), системний виклик `open()` для файлу `domain_policy` у режимі запису поверне помилку `-EPERM` (`Operation not permitted`), якщо домен вашої консольної оболонки (наприклад, `<kernel> /sbin/init /usr/sbin/sshd /bin/bash`) не вказано у файлі `/etc/tomoyo/manager.conf`.

Це важливий захисний механізм TOMOYO: суперкористувач `root` у режимі `Enforcing` не має автоматичного права змінювати політики безпеки, якщо його поточний домен не визначено як офіційний менеджер SecurityFS.

### Паралельний доступ та багатопотоковість

Коли декілька додатків або багатопотоковий демон моніторингу одночасно записують у `domain_policy`, ядро Linux захищає свої внутрішні структури даних за допомогою внутрішнього взаємного блокування списків `mutex_lock(&tomoyo_policy_lock)`. Якщо один процес виконує запис правила, інші виклики `write()` тимчасово блокуються у ядрі до завершення парсингу поточного рядка. Для системного програміста це означає, що операції запису правил є безпечними у багатопотоковому середовищі, але вимагають ретельного форматування кожного блоку даних.
