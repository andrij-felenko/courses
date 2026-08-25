# ⚙️ Двигунець сканування ієрархій та об'єднання drop-in конфігурацій

<preknowlist>
- [Файлова система FHS](root:sys-unix/fhs-layout) — призначення каталогів `/etc`, `/run`, `/usr/lib` та правила пріоритетів.
- [Псевдо-ФС: procfs, sysfs, tmpfs, devtmpfs](root:sys-unix/pseudo-filesystems) — псевдопристрій `/dev/null` та його ідентифікатори rdev.
</preknowlist>

Реалізація модульної конфігурації у системних демонах простору користувача Linux (таких як `systemd`, `udevd`, `systemd-sysctl`, `systemd-tmpfiles`) вимагає детермінованого алгоритму обходу файлової системи. Цей алгоритм має строго забезпечувати чотири фундаментальні інваріанти:

1. **Ієрархічний пріоритет каталогів**:
   Конфігураційні правила з каталогу локального адміністратора `/etc/` мають безумовну перевагу над динамічними рантайм-налаштуваннями у `/run/`, а ті, у свою чергу, перекривають фабричні налаштування постачальника дистрибутива у `/usr/lib/`.
2. **Затінення за базовим іменем (Basename Shadowing)**:
   Якщо файл із назвою `50-network.conf` знайдено у каталозі з вищим пріоритетом (наприклад, `/etc/sysctl.d/`), будь-які однойменні файли у каталогах із нижчим пріоритетом (`/run/sysctl.d/` або `/usr/lib/sysctl.d/`) мають бути повністю відкинуті з плану обробки без аналізу їхнього вмісту.
3. **Детекція маскування (Masking Detection)**:
   Якщо файл конфігурації є символьним посиланням, яке вказує на псевдопристрій `/dev/null`, або безпосередньо є символьним спеціальним файлом пристрою з мажорним та мінорним номерами `(1, 3)`, такий запис позначається як маскований (англ. *masked*). Парсер зобов'язаний вилучити його з фінального списку виконання, запобігаючи завантаженню як цього файлу, так і будь-яких однойменних дефолтів постачальника.
4. **Лексикографічне сортування (ASCII Sorting)**:
   Усі відібрані валідні файли, що пережили фазу фільтрації затінень та маскувань, сортуються у порядку зростання числових байтових значень символів їхніх базових імен. Це гарантує, що файл `10-base.conf` передається парсеру раніше за `50-vendor.conf`, а той — раніше за `99-override.conf`.

Нижче наведено повну програмну реалізацію такого сканера мовами C та C++ з детальним аналізом системних викликів та обробки крайових випадків.

---

## 1. Архітектура та програмна реалізація сканера

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/sysmacros.h>
#include <unistd.h>
#include <stdbool.h>

#define MAX_ENTRIES 256
#define MAX_PATH_LEN 1024

/* Рівні пріоритету джерел конфігурації */
typedef enum {
    SOURCE_VENDOR,  /* /usr/lib (Найнижчий пріоритет) */
    SOURCE_RUNTIME, /* /run     (Середній пріоритет) */
    SOURCE_ADMIN    /* /etc     (Найвищий пріоритет) */
} config_tier_t;

/* Запис метаданих знайденого конфігураційного файлу */
typedef struct {
    char filename[256];          /* Базове ім'я файлу (наприклад, 50-net.conf) */
    char full_path[MAX_PATH_LEN];/* Повний абсолютний шлях на диску */
    config_tier_t tier;          /* Джерело походження */
    bool is_masked;              /* Ознака маскування через /dev/null */
} config_file_entry_t;

/* Реєстр зібраних файлів */
typedef struct {
    config_file_entry_t entries[MAX_ENTRIES];
    size_t count;
} config_registry_t;

/*
 * Перевірка маскування:
 * 1. lstat() визначає, чи є файл символьним посиланням.
 * 2. readlink() перевіряє ціль посилання на рівність "/dev/null".
 * 3. stat() перевіряє, чи не є ціль безпосередньо символьним пристроєм (1, 3).
 */
static bool is_path_masked(const char *path) {
    struct stat st;
    if (lstat(path, &st) != 0) {
        return false;
    }

    if (S_ISLNK(st.st_mode)) {
        char target[MAX_PATH_LEN];
        ssize_t len = readlink(path, target, sizeof(target) - 1);
        if (len != -1) {
            target[len] = '\0';
            if (strcmp(target, "/dev/null") == 0 || strcmp(target, "dev/null") == 0) {
                return true;
            }
        }
    }

    if (stat(path, &st) == 0) {
        if (S_ISCHR(st.st_mode) && major(st.st_rdev) == 1 && minor(st.st_rdev) == 3) {
            return true;
        }
    }

    return false;
}

/* Перевірка валідності розширення файлу (.conf) */
static bool has_conf_extension(const char *name) {
    const char *ext = strrchr(name, '.');
    return (ext != NULL && strcmp(ext, ".conf") == 0);
}

/* Компаратор qsort для впорядкування за ASCII-кодами базового імені */
static int compare_entries(const void *a, const void *b) {
    const config_file_entry_t *entry_a = (const config_file_entry_t *)a;
    const config_file_entry_t *entry_b = (const config_file_entry_t *)b;
    return strcmp(entry_a->filename, entry_b->filename);
}

/* Сканування конкретного каталогу ієрархії */
static void scan_directory(const char *dir_path, config_tier_t tier, config_registry_t *reg) {
    DIR *dir = opendir(dir_path);
    if (!dir) {
        return; /* Каталог може бути відсутнім (наприклад, у чистій системі) */
    }

    struct dirent *de;
    while ((de = readdir(dir)) != NULL) {
        /* Ігноруємо поточний каталог '.', батьківський '..' та приховані файли */
        if (de->d_name[0] == '.') {
            continue;
        }

        /* Перевіряємо суворе розширення .conf */
        if (!has_conf_extension(de->d_name)) {
            continue;
        }

        /*
         * Перевірка затінення (Shadowing):
         * Оскільки ми скануємо від вищого пріоритету до нижчого (/etc -> /run -> /usr),
         * якщо базове ім'я вже є в реєстрі, поточний файл відкидається.
         */
        bool already_seen = false;
        for (size_t i = 0; i < reg->count; ++i) {
            if (strcmp(reg->entries[i].filename, de->d_name) == 0) {
                already_seen = true;
                break;
            }
        }

        if (already_seen) {
            continue;
        }

        if (reg->count >= MAX_ENTRIES) {
            fprintf(stderr, "Помилка: перевищено ліміт записів реєстру\\n");
            break;
        }

        config_file_entry_t *entry = &reg->entries[reg->count++];
        snprintf(entry->filename, sizeof(entry->filename), "%s", de->d_name);
        snprintf(entry->full_path, sizeof(entry->full_path), "%s/%s", dir_path, de->d_name);
        entry->tier = tier;
        entry->is_masked = is_path_masked(entry->full_path);
    }

    closedir(dir);
}

int main(int argc, char **argv) {
    const char *subsystem = (argc > 1) ? argv[1] : "sysctl";
    char etc_dir[MAX_PATH_LEN], run_dir[MAX_PATH_LEN], usr_dir[MAX_PATH_LEN];

    snprintf(etc_dir, sizeof(etc_dir), "/etc/%s.d", subsystem);
    snprintf(run_dir, sizeof(run_dir), "/run/%s.d", subsystem);
    snprintf(usr_dir, sizeof(usr_dir), "/usr/lib/%s.d", subsystem);

    config_registry_t registry = { .count = 0 };

    /* 1. Послідовне сканування за спаданням пріоритету для вирішення затінень */
    scan_directory(etc_dir, SOURCE_ADMIN, &registry);
    scan_directory(run_dir, SOURCE_RUNTIME, &registry);
    scan_directory(usr_dir, SOURCE_VENDOR, &registry);

    /* 2. Лексикографічне сортування результуючого набору за ASCII */
    qsort(registry.entries, registry.count, sizeof(config_file_entry_t), compare_entries);

    /* 3. Генерація підсумкового плану виконання */
    printf("=== ПЛАН ЗАВАНТАЖЕННЯ КОНФІГУРАЦІЇ ДЛЯ [%s.d] ===\\n", subsystem);
    for (size_t i = 0; i < registry.count; ++i) {
        config_file_entry_t *e = &registry.entries[i];
        const char *tier_str = (e->tier == SOURCE_ADMIN) ? "[ADMIN /etc]" :
                               (e->tier == SOURCE_RUNTIME) ? "[RUN /run]" : "[VENDOR /usr]";

        if (e->is_masked) {
            printf("  [-] %-22s -> %-40s %s (ЗАМАСКОВАНО /dev/null)\\n",
                   e->filename, e->full_path, tier_str);
        } else {
            printf("  [+] %-22s -> %-40s %s\\n",
                   e->filename, e->full_path, tier_str);
        }
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <filesystem>
#include <vector>
#include <string>
#include <string_view>
#include <map>
#include <algorithm>
#include <system_error>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <unistd.h>

namespace fs = std::filesystem;

enum class ConfigTier {
    Admin,    // /etc     (Найвищий пріоритет)
    Runtime,  // /run     (Середній пріоритет)
    Vendor    // /usr/lib (Найнижчий пріоритет)
};

struct ConfigEntry {
    std::string filename;
    fs::path full_path;
    ConfigTier tier;
    bool is_masked{false};
};

class DropinHierarchyScanner {
public:
    explicit DropinHierarchyScanner(std::string subsystem_name)
        : subsystem_(std::move(subsystem_name)) {}

    [[nodiscard]] std::vector<ConfigEntry> collect_effective_configs() {
        std::map<std::string, ConfigEntry> registry;

        // Послідовне сканування у порядку спадання пріоритету (/etc -> /run -> /usr/lib)
        scan_tier_directory("/etc/" + subsystem_ + ".d", ConfigTier::Admin, registry);
        scan_tier_directory("/run/" + subsystem_ + ".d", ConfigTier::Runtime, registry);
        scan_tier_directory("/usr/lib/" + subsystem_ + ".d", ConfigTier::Vendor, registry);

        // Перетворюємо асоціативний масив у відсортований вектор
        std::vector<ConfigEntry> result;
        result.reserve(registry.size());
        for (auto& [name, entry] : registry) {
            result.push_back(entry);
        }

        // Лексикографічне сортування за базовим іменем файлу згідно з ASCII
        std::sort(result.begin(), result.end(), [](const auto& a, const auto& b) {
            return a.filename < b.filename;
        });

        return result;
    }

private:
    std::string subsystem_;

    static bool is_masked(const fs::path& path) {
        std::error_code ec;
        if (fs::is_symlink(path, ec)) {
            auto target = fs::read_symlink(path, ec);
            if (!ec && (target == "/dev/null" || target == "dev/null")) {
                return true;
            }
        }

        struct stat st{};
        if (stat(path.c_str(), &st) == 0) {
            if (S_ISCHR(st.st_mode) && major(st.st_rdev) == 1 && minor(st.st_rdev) == 3) {
                return true;
            }
        }

        return false;
    }

    void scan_tier_directory(const fs::path& dir_path, ConfigTier tier,
                             std::map<std::string, ConfigEntry>& registry) {
        std::error_code ec;
        if (!fs::exists(dir_path, ec) || !fs::is_directory(dir_path, ec)) {
            return;
        }

        for (const auto& dir_entry : fs::directory_iterator(dir_path, ec)) {
            if (ec) break;

            const auto& path = dir_entry.path();
            if (path.filename().string().starts_with('.')) {
                continue; // Пропуск прихованих файлів і службових записів
            }

            if (path.extension() != ".conf") {
                continue; // Фільтрація файлів без суфікса .conf
            }

            std::string filename = path.filename().string();

            // Затінення: якщо запис із цим іменем уже зареєстровано з вищого рівня, пропускаємо
            if (registry.find(filename) == registry.end()) {
                registry.emplace(filename, ConfigEntry{
                    .filename = filename,
                    .full_path = path,
                    .tier = tier,
                    .is_masked = is_masked(path)
                });
            }
        }
    }
};

int main(int argc, char* argv[]) {
    std::string subsystem = (argc > 1) ? argv[1] : "sysctl";
    DropinHierarchyScanner scanner(subsystem);

    auto entries = scanner.collect_effective_configs();

    std::cout << "=== ПЛАН ЗАВАНТАЖЕННЯ КОНФІГУРАЦІЇ ДЛЯ [" << subsystem << ".d] ===\n";
    for (const auto& e : entries) {
        std::string_view tier_name = (e.tier == ConfigTier::Admin) ? "[ADMIN /etc]" :
                                     (e.tier == ConfigTier::Runtime) ? "[RUN /run]" : "[VENDOR /usr]";

        if (e.is_masked) {
            std::cout << "  [-] " << e.filename << " -> " << e.full_path
                      << " " << tier_name << " (ЗАМАСКОВАНО /dev/null)\n";
        } else {
            std::cout << "  [+] " << e.filename << " -> " << e.full_path
                      << " " << tier_name << "\n";
        }
    }

    return 0;
}
```
:::

---

## 2. Інженерний аналіз системних викликів та граничних станів

Під час практичної розробки системного сканера drop-in конфігурацій виникає низка критичних граничних умов файлової системи, які вимагають специфічної послідовності системних викликів:

### 1. Розрізнення `lstat()` та `stat()` для детекції маскування
Класичною помилкою є використання системного виклику `stat()` замість `lstat()`. Системний виклик `stat()` автоматично слідує за всіма символьними посиланнями. Якщо у каталозі `/etc/systemd/system/app.service` створено символьне посилання на `/dev/null`, виклик `stat()` поверне інформацію про цільовий файл пристрою (`st_rdev` для `/dev/null`), але не покаже, що сам запис у каталозі є посиланням.

Якщо ж символьне посилання є пошкодженим (вказує на неіснуючий файл), `stat()` завершиться аварійною помилкою `ENOENT` (англ. *No such file or directory*). На противагу цьому, `lstat()` повертає інформацію про саме символьне посилання, дозволяючи викликати `readlink()` для точної перевірки рядка цілі. Сканер спершу перевіряє тип через `lstat()`, зчитує ціль через `readlink()`, і лише за потреби валідації цілі звертається до `stat()`.

### 2. Ідентифікація псевдопристрою `/dev/null` за номерами `rdev`
У середовищі Linux кожен символьний та блоковий пристрій ідентифікується парою чисел у полі `st_rdev`:
- **Major number (мажорний номер)**: визначає тип драйвера пристрою в ядрі. Для пристроїв пам'яті (`mem`, `null`, `zero`, `random`) мажорний номер дорівнює `1`.
- **Minor number (мінорний номер)**: визначає конкретний вузол. Для `/dev/null` мінорний номер дорівнює `3`, для `/dev/zero` — `5`.

Макроси `major(st.st_rdev)` та `minor(st.st_rdev)` із системного заголовка `<sys/sysmacros.h>` дозволяють однозначно ідентифікувати маскування навіть у випадках, коли файл є жорстким посиланням або створений за допомогою системного виклику `mknod()`.

### 3. Фільтрація артефактів редакторів та систем контролю версій
У процесі ручного редагування текстові редактори (`vim`, `emacs`, `nano`) та пакетні менеджери часто створюють тимчасові файли у конфігураційних каталогах: `50-net.conf~`, `50-net.conf.swp`, `50-net.conf.dpkg-dist`, `50-net.conf.rpmnew`. Якщо сканер завантажить ці файли, це спричинить повторне або конфліктне застосування параметрів. Сканер зобов'язаний вимагати точного збігу розширення `.conf` наприкінці рядка та ігнорувати всі приховані файли, ім'я яких починається з крапки.

### 4. Захист від гонитви за станом (TOCTOU) через відносні дескриптори
У високопродуктивних багатопотокових сервісах прямий виклик `stat(path)` створює вразливість до атак типу «час перевірки проти часу використання» (англ. *Time-of-Check to Time-of-Use, TOCTOU*). Якщо зловмисник підмінить каталог між моментом виклику `opendir()` та `open()`, демон може прочитати чужий файл. 

Виробничі реалізації `systemd` використовують системні виклики сімейства `*at`:
- Відкриття каталогу з прапорцями `O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW`.
- Зчитування метаданих за допомогою `fstatat(dirfd, filename, &st, AT_SYMLINK_NOFOLLOW)`.
- Безпечне відкриття файлу через `openat(dirfd, filename, O_RDONLY | O_CLOEXEC | O_NOFOLLOW)`.

Це гарантує, що операція виконується строго в межах перевіреного файлового дескриптора каталогу без ризику виходу за межі ізольованого дерева монтувань.

---

## 3. Збірка, виконання та демонстраційний вивід

Для компіляції програми використовуйте стандартні інструменти збірки GCC або Clang з підтримкою стандартів C11 та C++20:

```bash
# Збірка реалізації мовою C
gcc -std=c11 -Wall -Wextra -O2 proj-dropin-scanner.c -o dropin_scanner_c

# Збірка реалізації мовою C++
g++ -std=c++20 -Wall -Wextra -O2 proj-dropin-scanner.cpp -o dropin_scanner_cpp
```

### Приклад виконання в реальній системі

Уявімо наступний стан файлової системи для підсистеми `sysctl.d`:
- `/usr/lib/sysctl.d/10-default.conf` (фабричні дефолти ядра)
- `/usr/lib/sysctl.d/50-net.conf` (пакетні мережеві налаштування)
- `/usr/lib/sysctl.d/80-disable-ipv6.conf` (дистрибутивне правило вимкнення IPv6)
- `/run/sysctl.d/20-cloud-init.conf` (динамічно згенеровані параметри хмарного образу)
- `/etc/sysctl.d/50-net.conf` (локальні правки адміністратора сервера)
- `/etc/sysctl.d/80-disable-ipv6.conf -> /dev/null` (символьне посилання на `/dev/null`)

Запуск скомпільованого бінарника `./dropin_scanner_cpp sysctl` формує чіткий план обробки:

```text
=== ПЛАН ЗАВАНТАЖЕННЯ КОНФІГУРАЦІЇ ДЛЯ [sysctl.d] ===
  [+] 10-default.conf        -> /usr/lib/sysctl.d/10-default.conf        [VENDOR /usr]
  [+] 20-cloud-init.conf     -> /run/sysctl.d/20-cloud-init.conf         [RUN /run]
  [+] 50-net.conf            -> /etc/sysctl.d/50-net.conf                [ADMIN /etc]
  [-] 80-disable-ipv6.conf   -> /etc/sysctl.d/80-disable-ipv6.conf       [ADMIN /etc] (ЗАМАСКОВАНО /dev/null)
```

З виводу чітко видно:
1. `10-default.conf` зчитано з `/usr/lib`, оскільки його ніхто не перевизначав.
2. `20-cloud-init.conf` підтягнуто з рантайм-пам'яті `/run`.
3. `50-net.conf` з `/usr/lib` було автоматично відкинуто, а натомість взято файл із вищого пріоритету `/etc`.
4. `80-disable-ipv6.conf` зафіксовано як замаскований: правило не буде передано ядру Linux.
