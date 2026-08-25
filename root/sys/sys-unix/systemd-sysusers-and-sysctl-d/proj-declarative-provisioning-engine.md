# ⚙️ Реалізація рушія декларативного налаштування користувачів та параметрів ядра

Створення спрощеної C/C++ бібліотеки для декларативного аналізу конфігураційних каталогів `.d`, створення системних користувачів через безпечне блокування `/etc/passwd` та застосування sysctl-параметрів у віртуальній файлової системі `/proc/sys`.

## Завдання та архітектура рушія

Розроблюваний рушій демонструє внутрішню логіку роботи `systemd-sysusers` та `systemd-sysctl`, відтворюючи ключові етапи роботи системних служб раннього завантаження. Метою цієї реалізації є простеження всього шляху обробки конфігураційного текстового файлу — від сканування дискових каталогів до виклику низькорівневих системних функцій ядра Linux.

Основні задачі, які вирішує розроблюваний конфігураційний рушій:

1. **Сканування ієрархії каталогів**: Утиліта послідовно обходить каталоги `/etc`, `/run` та `/usr/lib` у порядку пріоритету, виконує дедуплікацію конфігураційних файлів за їхнім базовим ім'ям та обробляє символічні посилання на `/dev/null` для підтримки затінення (shadowing) і маскування задекларованих правил.
2. **Атомарне оновлення бази користувачів**: Парсер `sysusers.d` обробляє конфігураційний рядок форми `u name UID "comment" home shell`. Для запобігання гонкам станів (race conditions) при одночасному модифікуванні бази даних системних користувачів декількома паралельними процесами, утиліта викликає системну функцію `lckpwdf()` для встановлення ексклюзивного блокування над файлом `/etc/.pwd.lock`, перевіряє відсутність дублікатів через `getpwnam()` і додає новий рядок у `/etc/passwd`.
3. **Трансляція ключів sysctl у VFS**: Записи у файлах `sysctl.d` перетворюються з крапкової нотації (наприклад, `net.ipv4.ip_forward`) на відповідні шляхи у віртуальній файловій системі `/proc/sys/net/ipv4/ip_forward`. Утиліта підтримує префікс `-` для м'якого ігнорування помилок відсутності вузла при відсутності необхідних модулів ядра.

## Проектування парсера та структур даних

Для зберігання інформації про виявлені конфігураційні файли використовується структура `ConfigFile` у версії на C та `ConfigEntry` у реалізації на C++. Структура фіксує базове ім'я файлу (для виявлення затінення), абсолютний шлях до файлу в системі, рівень пріоритету джерела (`/etc` = 3, `/run` = 2, `/usr/lib` = 1) та прапор маскування `is_masked`.

Процес сканування виконує наступні кроки:
- Використовується системна функція `opendir()` та `readdir()` (в C) або `std::filesystem::directory_iterator` (в C++) для обходу кожного з трьох каталогів.
- Для кожного виявленого файла з розширенням `.conf` перевіряється, чи присутній файл з таким ім'ям у хеш-таблиці або списку вже оброблених елементів з вищим пріоритетом. Якщо файл вже знайдено, поточний елемент пропускається (shadowing).
- За допомогою `lstat()` або `fs::is_symlink()` аналізується, чи є файл символічним посиланням. Якщо посилання вказує на `/dev/null`, об'єкт позначається як замаскований (`is_masked = 1`).
- Отриманий масив файлів сортується у лексикографічному порядку за допомогою `qsort()` в C або `std::sort()` в C++.

:::tabs
```c
/* sysconfig_engine.c — C99 / POSIX реалізація рушія конфігурації */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <shadow.h>
#include <pwd.h>
#include <errno.h>

#define MAX_ENTRIES 256
#define MAX_PATH 512

typedef struct {
    char name[64];
    char full_path[MAX_PATH];
    int priority; /* 3: /etc, 2: /run, 1: /usr/lib */
    int is_masked;
} ConfigFile;

static int compare_files(const void *a, const void *b) {
    const ConfigFile *fa = (const ConfigFile *)a;
    const ConfigFile *fb = (const ConfigFile *)b;
    return strcmp(fa->name, fb->name);
}

/* Сканування ієрархії каталогів з дедуплікацією та затіненням */
int sc_scan_dir(const char *subdirs, ConfigFile *out_files, int *count) {
    const char *dirs[] = {"/etc", "/run", "/usr/lib"};
    int p_levels[] = {3, 2, 1};
    int total = 0;

    for (int i = 0; i < 3; i++) {
        char dir_path[MAX_PATH];
        snprintf(dir_path, sizeof(dir_path), "%s/%s", dirs[i], subdirs);

        DIR *d = opendir(dir_path);
        if (!d) continue;

        struct dirent *entry;
        while ((entry = readdir(d)) != NULL) {
            if (entry->d_type != DT_REG && entry->d_type != DT_LNK) continue;
            if (!strstr(entry->d_name, ".conf")) continue;

            /* Перевірка чи файл уже був доданий з вищим пріоритетом */
            int exists = 0;
            for (int j = 0; j < total; j++) {
                if (strcmp(out_files[j].name, entry->d_name) == 0) {
                    exists = 1;
                    break;
                }
            }
            if (exists) continue;

            ConfigFile *cf = &out_files[total];
            strncpy(cf->name, entry->d_name, sizeof(cf->name) - 1);
            snprintf(cf->full_path, sizeof(cf->full_path), "%s/%s", dir_path, entry->d_name);
            cf->priority = p_levels[i];

            /* Перевірка на маскування (/dev/null) */
            struct stat st;
            if (lstat(cf->full_path, &st) == 0 && S_ISLNK(st.st_mode)) {
                char target[MAX_PATH];
                ssize_t len = readlink(cf->full_path, target, sizeof(target) - 1);
                if (len > 0) {
                    target[len] = '\0';
                    if (strstr(target, "/dev/null")) cf->is_masked = 1;
                }
            }
            total++;
        }
        closedir(d);
    }

    qsort(out_files, total, sizeof(ConfigFile), compare_files);
    *count = total;
    return 0;
}

/* Застосування ключа sysctl у /proc/sys */
int sc_apply_sysctl_line(const char *key, const char *value) {
    char proc_path[MAX_PATH] = "/proc/sys/";
    int path_idx = strlen(proc_path);
    int ignore_error = 0;

    const char *k_ptr = key;
    if (k_ptr[0] == '-') {
        ignore_error = 1;
        k_ptr++;
    }

    for (int i = 0; k_ptr[i] != '\0'; i++) {
        if (k_ptr[i] == '.') {
            proc_path[path_idx++] = '/';
        } else {
            proc_path[path_idx++] = k_ptr[i];
        }
    }
    proc_path[path_idx] = '\0';

    int fd = open(proc_path, O_WRONLY);
    if (fd < 0) {
        if (ignore_error) return 0;
        fprintf(stderr, "Помилка відкриття sysctl %s: %s\n", proc_path, strerror(errno));
        return -1;
    }

    ssize_t w = write(fd, value, strlen(value));
    close(fd);
    return (w > 0) ? 0 : -1;
}

/* Додавання системного користувача з блокуванням lckpwdf */
int sc_apply_sysuser(const char *username, uid_t uid, const char *comment, const char *home, const char *shell) {
    if (lckpwdf() != 0) {
        fprintf(stderr, "Не вдалося заблокувати базу даних користувачів: %s\n", strerror(errno));
        return -1;
    }

    /* Перевірка чи існує користувач */
    if (getpwnam(username) != NULL) {
        ulckpwdf();
        return 0; /* Вже існує, ідемпотентний вихід */
    }

    FILE *f = fopen("/etc/passwd", "a");
    if (!f) {
        ulckpwdf();
        return -1;
    }

    fprintf(f, "%s:x:%u:%u:%s:%s:%s\n", username, (unsigned)uid, (unsigned)uid, comment, home, shell);
    fclose(f);

    ulckpwdf();
    return 0;
}
```
```cpp
// sysconfig_engine.cpp — Ідіоматична C++20 реалізація
#include <iostream>
#include <fstream>
#include <filesystem>
#include <vector>
#include <string>
#include <string_view>
#include <algorithm>
#include <expected>
#include <shadow.h>
#include <pwd.h>

namespace fs = std::filesystem;

// RAII-обгортка для безпечного блокування бази даних користувачів
class UserDbLock {
public:
    UserDbLock() {
        locked_ = (lckpwdf() == 0);
    }
    ~UserDbLock() {
        if (locked_) ulckpwdf();
    }
    UserDbLock(const UserDbLock&) = delete;
    UserDbLock& operator=(const UserDbLock&) = delete;

    [[nodiscard]] bool is_locked() const noexcept { return locked_; }
private:
    bool locked_{false};
};

struct ConfigEntry {
    std::string name;
    fs::path full_path;
    int priority{0};
    bool is_masked{false};
};

class SysConfigEngine {
public:
    // Сканування каталогів .d з використанням std::filesystem
    static std::vector<ConfigEntry> scan_dot_d(std::string_view subdir) {
        std::vector<ConfigEntry> entries;
        const std::pair<fs::path, int> search_dirs[] = {
            {"/etc", 3}, {"/run", 2}, {"/usr/lib", 1}
        };

        for (const auto& [base, prio] : search_dirs) {
            fs::path p = base / subdir;
            if (!fs::exists(p) || !fs::is_directory(p)) continue;

            for (const auto& dir_entry : fs::directory_iterator(p)) {
                if (dir_entry.path().extension() != ".conf") continue;
                
                std::string fname = dir_entry.path().filename().string();
                auto it = std::find_if(entries.begin(), entries.end(),
                    [&fname](const ConfigEntry& e) { return e.name == fname; });
                
                if (it != entries.end()) continue; // Файл затінено вищим пріоритетом

                bool masked = dir_entry.is_symlink() && 
                              fs::read_symlink(dir_entry.path()).string().find("/dev/null") != std::string::npos;

                entries.push_back({fname, dir_entry.path(), prio, masked});
            }
        }

        std::sort(entries.begin(), entries.end(),
            [](const ConfigEntry& a, const ConfigEntry& b) { return a.name < b.name; });

        return entries;
    }

    // Застосування параметра sysctl через запис у std::ofstream
    static std::expected<void, std::string> apply_sysctl(std::string_view key, std::string_view value) {
        bool ignore_error = false;
        if (key.starts_with('-')) {
            ignore_error = true;
            key.remove_prefix(1);
        }

        std::string rel_path;
        rel_path.reserve(key.size());
        for (char ch : key) {
            rel_path.push_back(ch == '.' ? '/' : ch);
        }

        fs::path target = fs::path("/proc/sys") / rel_path;
        std::ofstream sysctl_file(target);
        if (!sysctl_file.is_open()) {
            if (ignore_error) return {};
            return std::unexpected("Помилка відкриття вузла sysctl: " + target.string());
        }

        sysctl_file << value << "\n";
        return {};
    }

    // Створення системного користувача з безпечним блокуванням бази даних
    static std::expected<void, std::string> apply_sysuser(std::string_view username, uid_t uid,
                                                         std::string_view comment,
                                                         std::string_view home,
                                                         std::string_view shell) {
        UserDbLock lock;
        if (!lock.is_locked()) {
            return std::unexpected("Не вдалося отримати lckpwdf() замок бази даних");
        }

        if (getpwnam(username.data()) != nullptr) {
            return {}; // Обліковий запис вже існує, ідемпотентний успіх
        }

        std::ofstream passwd_file("/etc/passwd", std::ios::app);
        if (!passwd_file.is_open()) {
            return std::unexpected("Не вдалося відкрити /etc/passwd для запису");
        }

        passwd_file << username << ":x:" << uid << ":" << uid << ":"
                    << comment << ":" << home << ":" << shell << "\n";

        return {};
    }
};
```
:::

## Аналіз крайових випадків та реалізаційних пасток

Під час створення низькорівневих системних інструментів конфігурації необхідно враховувати специфіку поведінки ядра Linux, механізми обробки файлових затискачів та особливості файлової системи:

- **Гонка станів при оновленні /etc/passwd**: Пряме відкриття та запис у `/etc/passwd` без використання системного виклику `lckpwdf()` призводить до пошкодження системної бази даних користувачів, якщо декілька інсталяційних скриптів або системних служб виконуються паралельно під час розгортання пакетів. Системний виклик `lckpwdf()` створює ексклюзивний замок над файлом `/etc/.pwd.lock` з таймаутом, гарантуючи послідовний та атомарний доступ.
- **Відсутність модулів ядра у sysctl**: Якщо параметр мережі (наприклад, IPv6 або мережеві мости) реалізовано у вигляді окремого модуля ядра Linux, який ще не завантажено на момент виклику, спроба відкрити `/proc/sys/net/ipv6/...` поверне системну помилку `ENOENT`. Використання префікса `-` у синтаксисі `sysctl.d` повідомляє парсеру про необхідність перехоплення цієї помилки без зупинки процесу завантаження всієї системи.
- **Символічні посилання та маскування**: При реалізації обходу каталогів `.d` обов'язково використовувати системний виклик `lstat()` замість `stat()`, оскільки `stat()` автоматично слідує за символічними посиланнями і не дозволить виявити посилання на `/dev/null`, які слугують прапорцями маскування небажаних конфігурацій.
- **Буферизація виводу при роботі з VFS**: При записі значений у віртуальні файли `/proc/sys/` необхідно відключати буферизацію стандартної бібліотеки C (за допомогою `fflush()`) або одразу закривати дескриптор файлу, оскільки віртуальна файлова система ядра не підтримує позиціонування каретки через `lseek()` і вимагає запису повного рядка за один виклик `write()`.
- **Безпека файлових прав**: Файли `/etc/passwd` та `/etc/group` повинні створюватися з суворими масками прав доступу `0644`, тоді як файли модових паролів `/etc/shadow` та `/etc/gshadow` вимагають маски `0600` або `0640` під управлінням групи `shadow`.
- **Сигнали та переривання**: При роботі з блокуванням `lckpwdf()` необхідно обробляти перехоплення системних сигналів (`SIGINT`, `SIGTERM`), щоб у разі передчасного завершення процесу примусово викликати `ulckpwdf()`, уникаючи залишення мертвих файл-замків у файловій системі.
- **Діапазони ідентифікаторів NIS/LDAP**: При автоматичному виділенні системного UID необхідно перевіряти не лише файл `/etc/passwd`, але й виконувати запити через NSS (Name Service Switch) `getpwnam()`, щоб уникнути колізій із користувачами, визначеними у зовнішніх каталогах Active Directory чи LDAP.
