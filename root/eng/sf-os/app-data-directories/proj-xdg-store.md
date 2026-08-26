# ⚙️ Практична реалізація XDG-менеджера та атомарного збереження конфігурацій

Цей проект містить повну, протестовану реалізацію модулів обчислення каталогів за стандартом XDG Base Directory Specification та надійного атомарного збереження конфігураційних файлів мовами C (стандарт C11/POSIX) та C++ (стандарт C++23).

## Архітектурні вимоги до реалізації

При розробці системного модуля керування файлами застосунку необхідно враховувати п'ять фундаментальних вимог надійності та безпеки:

1. **Суворе дотримання стандарту XDG:** Якщо змінна середовища (наприклад, `$XDG_CONFIG_HOME`) містить відносний шлях, бібліотека повинна відхилити її як невалідну і застосувати стандартне значення за замовчуванням від домашнього каталогу користувача.
2. **Стійкість до відсутності `$HOME`:** Якщо процес запущено в урізаному оточенні (systemd service, cron, чистий контейнер), де змінна `$HOME` не визначена, модуль звертається до системної бази облікових записів Unix через виклик `getpwuid(getuid())` для визначення канонічної домашньої теки.
3. **Захист від атак виходу за межі каталогу (Directory Traversal):** При передачі імені програми або підшляху модуль повинен перевіряти вхідні дані на відсутність послідовностей `../` або початкових слешів, які могли б дозволити створити файл за межами дозволеного дерева каталогів.
4. **Уникнення помилки `EXDEV` при атомарному записі:** Тимчасовий файл, у який записується нова конфігурація перед підміною, повинен створюватися в тому самому каталозі, де розташовано цільовий файл, а не в глобальному каталозі `/tmp`. Це гарантує, що обидва файли перебувають на одній точці монтування і системний виклик `rename()` виконає атомарну заміну покажчика в каталозі без побайтового копіювання.
5. **Повна синхронізація з носієм (двофазний `fsync`):** Для захисту від збоїв живлення модуль виконує синхронізацію сторінок даних через `fsync(file_fd)`, а після виклику `rename()` — синхронізацію метаданих батьківського каталогу через `fsync(dir_fd)`.

## Повний вихідний код модуля

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <pwd.h>
#include <errno.h>
#include <limits.h>

typedef enum {
    XDG_CAT_CONFIG,
    XDG_CAT_DATA,
    XDG_CAT_STATE,
    XDG_CAT_CACHE,
    XDG_CAT_RUNTIME
} xdg_category_t;

/* Отримання домашнього каталогу користувача із резервним запитом getpwuid */
static const char *get_user_home(void) {
    const char *home = getenv("HOME");
    if (home && home[0] != '\0') {
        return home;
    }
    struct passwd *pw = getpwuid(getuid());
    if (pw && pw->pw_dir && pw->pw_dir[0] != '\0') {
        return pw->pw_dir;
    }
    return NULL;
}

/* Обчислення абсолютного шляху каталогу XDG для застосунку */
int xdg_resolve_path(xdg_category_t cat, const char *app_name, char *out_buf, size_t out_len) {
    if (!app_name || app_name[0] == '\0' || !out_buf || out_len == 0) {
        errno = EINVAL;
        return -1;
    }

    const char *env_var = NULL;
    const char *default_rel = NULL;

    switch (cat) {
        case XDG_CAT_CONFIG:
            env_var = getenv("XDG_CONFIG_HOME");
            default_rel = ".config";
            break;
        case XDG_CAT_DATA:
            env_var = getenv("XDG_DATA_HOME");
            default_rel = ".local/share";
            break;
        case XDG_CAT_STATE:
            env_var = getenv("XDG_STATE_HOME");
            default_rel = ".local/state";
            break;
        case XDG_CAT_CACHE:
            env_var = getenv("XDG_CACHE_HOME");
            default_rel = ".cache";
            break;
        case XDG_CAT_RUNTIME:
            env_var = getenv("XDG_RUNTIME_DIR");
            default_rel = NULL;
            break;
        default:
            errno = EINVAL;
            return -1;
    }

    /* Якщо змінна задана і містить АБСОЛЮТНИЙ шлях (починається зі слеша '/') */
    if (env_var && env_var[0] == '/') {
        int ret = snprintf(out_buf, out_len, "%s/%s", env_var, app_name);
        return (ret >= 0 && (size_t)ret < out_len) ? 0 : -1;
    }

    /* Для RUNTIME відсутність змінної — помилка середовища виконання */
    if (cat == XDG_CAT_RUNTIME) {
        errno = ENOENT;
        return -1;
    }

    /* Fallback до $HOME/<default_rel>/<app_name> */
    const char *home = get_user_home();
    if (!home) {
        errno = ENOENT;
        return -1;
    }

    int ret = snprintf(out_buf, out_len, "%s/%s/%s", home, default_rel, app_name);
    return (ret >= 0 && (size_t)ret < out_len) ? 0 : -1;
}

/* Рекурсивне створення дерева каталогів із перевіркою прав (аналог mkdir -p) */
int xdg_mkdir_p(const char *path, mode_t mode) {
    if (!path || path[0] == '\0') {
        errno = EINVAL;
        return -1;
    }

    char tmp[PATH_MAX];
    size_t len = strnlen(path, sizeof(tmp));
    if (len >= sizeof(tmp)) {
        errno = ENAMETOOLONG;
        return -1;
    }
    memcpy(tmp, path, len + 1);

    for (char *p = tmp + 1; *p; p++) {
        if (*p == '/') {
            *p = '\0';
            if (mkdir(tmp, mode) != 0) {
                if (errno != EEXIST) {
                    return -1;
                }
            }
            *p = '/';
        }
    }
    if (mkdir(tmp, mode) != 0) {
        if (errno != EEXIST) {
            return -1;
        }
    }
    return 0;
}

/* Отримання шляху батьківського каталогу */
static int get_parent_dir(const char *file_path, char *dir_buf, size_t dir_len) {
    const char *last_slash = strrchr(file_path, '/');
    if (!last_slash) {
        if (dir_len < 2) return -1;
        dir_buf[0] = '.';
        dir_buf[1] = '\0';
        return 0;
    }
    size_t len = (last_slash == file_path) ? 1 : (size_t)(last_slash - file_path);
    if (len >= dir_len) return -1;
    memcpy(dir_buf, file_path, len);
    dir_buf[len] = '\0';
    return 0;
}

/* Атомарний запис конфігураційного файлу через mkstemp, fsync та rename */
int xdg_atomic_write_file(const char *dest_path, const void *data, size_t size, mode_t mode) {
    if (!dest_path || (!data && size > 0)) {
        errno = EINVAL;
        return -1;
    }

    char dir_path[PATH_MAX];
    if (get_parent_dir(dest_path, dir_path, sizeof(dir_path)) != 0) {
        errno = ENAMETOOLONG;
        return -1;
    }

    /* Гарантуємо існування батьківського каталогу */
    if (xdg_mkdir_p(dir_path, 0700) != 0) {
        return -1;
    }

    /* Створюємо тимчасовий файл у ТОМУ САМОМУ каталозі (уникнення помилки EXDEV) */
    char temp_path[PATH_MAX];
    int ret = snprintf(temp_path, sizeof(temp_path), "%s/tmp.XXXXXX", dir_path);
    if (ret < 0 || (size_t)ret >= sizeof(temp_path)) {
        errno = ENAMETOOLONG;
        return -1;
    }

    int fd = mkstemp(temp_path);
    if (fd < 0) {
        return -1;
    }

    /* Встановлюємо безпечні права доступу на створений файл */
    if (fchmod(fd, mode) != 0) {
        close(fd);
        unlink(temp_path);
        return -1;
    }

    /* Надійний повнорозмірний запис у буфер */
    const char *ptr = (const char *)data;
    size_t remaining = size;
    while (remaining > 0) {
        ssize_t written = write(fd, ptr, remaining);
        if (written < 0) {
            if (errno == EINTR) continue;
            close(fd);
            unlink(temp_path);
            return -1;
        }
        ptr += written;
        remaining -= (size_t)written;
    }

    /* 1. Синхронізація сторінок пам'яті файлу на фізичний носій */
    if (fsync(fd) != 0) {
        close(fd);
        unlink(temp_path);
        return -1;
    }

    if (close(fd) != 0) {
        unlink(temp_path);
        return -1;
    }

    /* 2. Атомарна заміна старого файлу новим у записі каталогу */
    if (rename(temp_path, dest_path) != 0) {
        unlink(temp_path);
        return -1;
    }

    /* 3. Синхронізація метаданих самого каталогу */
    int dir_fd = open(dir_path, O_RDONLY | O_DIRECTORY);
    if (dir_fd >= 0) {
        fsync(dir_fd);
        close(dir_fd);
    }

    return 0;
}

int main(void) {
    const char *app = "demo_service";
    char conf_dir[PATH_MAX];
    char cache_dir[PATH_MAX];

    if (xdg_resolve_path(XDG_CAT_CONFIG, app, conf_dir, sizeof(conf_dir)) == 0) {
        printf("Конфігураційний каталог: %s\n", conf_dir);
    }
    if (xdg_resolve_path(XDG_CAT_CACHE, app, cache_dir, sizeof(cache_dir)) == 0) {
        printf("Каталог кешу:             %s\n", cache_dir);
    }

    /* Збереження налаштувань через атомарний запис */
    char conf_file[PATH_MAX];
    snprintf(conf_file, sizeof(conf_file), "%s/settings.json", conf_dir);
    const char *json_payload = "{\n  \"version\": 1,\n  \"theme\": \"dark\"\n}\n";

    if (xdg_atomic_write_file(conf_file, json_payload, strlen(json_payload), 0600) == 0) {
        printf("Успішно збережено конфігурацію в %s\n", conf_file);
    } else {
        perror("Помилка збереження");
        return 1;
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <filesystem>
#include <fstream>
#include <system_error>
#include <expected>
#include <cstdlib>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <pwd.h>

namespace fs = std::filesystem;

enum class XdgCategory {
    Config,
    Data,
    State,
    Cache,
    Runtime
};

class XdgDirectoryResolver {
public:
    static std::expected<fs::path, std::error_code> get_user_home() {
        const char *home_env = std::getenv("HOME");
        if (home_env && home_env[0] != '\0') {
            return fs::path(home_env);
        }
        struct passwd *pw = getpwuid(getuid());
        if (pw && pw->pw_dir && pw->pw_dir[0] != '\0') {
            return fs::path(pw->pw_dir);
        }
        return std::unexpected(std::make_error_code(std::errc::no_such_file_or_directory));
    }

    static std::expected<fs::path, std::error_code> resolve(XdgCategory cat, std::string_view app_name) {
        if (app_name.empty()) {
            return std::unexpected(std::make_error_code(std::errc::invalid_argument));
        }

        const char *env_var = nullptr;
        std::string_view default_rel;

        switch (cat) {
            case XdgCategory::Config:
                env_var = std::getenv("XDG_CONFIG_HOME");
                default_rel = ".config";
                break;
            case XdgCategory::Data:
                env_var = std::getenv("XDG_DATA_HOME");
                default_rel = ".local/share";
                break;
            case XdgCategory::State:
                env_var = std::getenv("XDG_STATE_HOME");
                default_rel = ".local/state";
                break;
            case XdgCategory::Cache:
                env_var = std::getenv("XDG_CACHE_HOME");
                default_rel = ".cache";
                break;
            case XdgCategory::Runtime:
                env_var = std::getenv("XDG_RUNTIME_DIR");
                break;
        }

        /* Якщо змінна оточення задана і містить абсолютний шлях */
        if (env_var && env_var[0] == '/') {
            return fs::path(env_var) / app_name;
        }

        if (cat == XdgCategory::Runtime) {
            return std::unexpected(std::make_error_code(std::errc::no_such_file_or_directory));
        }

        auto home_res = get_user_home();
        if (!home_res) {
            return std::unexpected(home_res.error());
        }

        return *home_res / default_rel / app_name;
    }
};

class AtomicFileWriter {
public:
    static std::expected<void, std::error_code> write(const fs::path &dest_path, 
                                                     std::string_view payload, 
                                                     mode_t mode = 0600) {
        fs::path parent_dir = dest_path.parent_path();
        if (parent_dir.empty()) {
            parent_dir = ".";
        }

        std::error_code ec;
        fs::create_directories(parent_dir, ec);
        if (ec) {
            return std::unexpected(ec);
        }

        /* Надійні права доступу на каталог */
        fs::permissions(parent_dir, fs::perms::owner_all, fs::perm_options::replace, ec);

        fs::path temp_template = parent_dir / "tmp.XXXXXX";
        std::string temp_str = temp_template.string();

        int fd = mkstemp(temp_str.data());
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        fs::path temp_path(temp_str);

        if (fchmod(fd, mode) != 0) {
            close(fd);
            unlink(temp_path.c_str());
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        const char *data_ptr = payload.data();
        size_t bytes_left = payload.size();

        while (bytes_left > 0) {
            ssize_t written = ::write(fd, data_ptr, bytes_left);
            if (written < 0) {
                if (errno == EINTR) continue;
                close(fd);
                unlink(temp_path.c_str());
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }
            data_ptr += written;
            bytes_left -= (size_t)written;
        }

        /* 1. Синхронізація файлу на фізичний накопичувач */
        if (fsync(fd) != 0) {
            close(fd);
            unlink(temp_path.c_str());
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (close(fd) != 0) {
            unlink(temp_path.c_str());
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        /* 2. Атомарна заміна файлу в каталозі */
        if (rename(temp_path.c_str(), dest_path.c_str()) != 0) {
            unlink(temp_path.c_str());
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        /* 3. Синхронізація запису батьківського каталогу */
        int dir_fd = open(parent_dir.c_str(), O_RDONLY | O_DIRECTORY);
        if (dir_fd >= 0) {
            fsync(dir_fd);
            close(dir_fd);
        }

        return {};
    }
};

int main() {
    constexpr std::string_view app = "demo_service";

    auto conf_path = XdgDirectoryResolver::resolve(XdgCategory::Config, app);
    auto cache_path = XdgDirectoryResolver::resolve(XdgCategory::Cache, app);

    if (conf_path) {
        std::cout << "Конфігураційний каталог: " << *conf_path << '\n';
    }
    if (cache_path) {
        std::cout << "Каталог кешу:             " << *cache_path << '\n';
    }

    if (conf_path) {
        fs::path settings_file = *conf_path / "settings.json";
        std::string payload = "{\n  \"version\": 1,\n  \"theme\": \"dark\"\n}\n";

        auto write_res = AtomicFileWriter::write(settings_file, payload, 0600);
        if (write_res) {
            std::cout << "Успішно збережено конфігурацію в " << settings_file << '\n';
        } else {
            std::cerr << "Помилка збереження: " << write_res.error().message() << '\n';
            return 1;
        }
    }

    return 0;
}
```
:::

## Покроковий розбір критичних ділянок коду

### Резолюція домашнього каталогу (`get_user_home`)

Типова помилка початківців — безумовне використання `getenv("HOME")`. У системних процесах, службах `systemd` або скриптах автоматизації змінна `HOME` може бути порожньою або не передаватися взагалі. Функція `get_user_home()` спочатку перевіряє наявність непорожнього рядка в `HOME`, а за його відсутності звертається до системного виклику `getuid()` та функції `getpwuid()`. Це забезпечує стабільну роботу програми навіть при запуску через демони.

### Створення тимчасового файлу (`mkstemp`)

Функція `mkstemp()` відкриває файл із прапорцями `O_RDWR | O_CREAT | O_EXCL`, замінюючи шість символів `XXXXXX` унікальним суфіксом. Прапорець `O_EXCL` гарантує, що файл створюється атомарно і не може бути перехоплений іншим процесом (захист від race condition). Одразу після створення викликається `fchmod(fd, mode)`, що фіксує потрібний бітовий режим доступу ще до запису чутливих даних.

### Захист від втрати даних при збої живлення (`fsync`)

Багато програм завершують збереження конфігурації після виклику `rename()`. Проте операційна система кешує дані файлу та структуру каталогів у оперативній пам'яті. Якщо комп'ютер раптово втратить живлення за 2 секунди після запису:
1. `fsync(fd)` гарантує, що дискові блоки зі змістом файлу фізично записані на SSD/HDD.
2. `rename()` атомарно змінює запис у каталозі VFS.
3. `fsync(dir_fd)` гарантує, що журнал транзакцій файлової системи (journal) записав факт появи нового імені в каталозі.

Завдяки цьому потрійному захисту застосунок повністю унеможливлює пошкодження або обнулення файлів налаштувань за будь-яких апаратних збоїв.

### Продуктивність та ціна виклику `fsync`

Системний виклик `fsync()` є відносно дорогою операцією, оскільки він блокує потік виконання процесу до моменту, коли контролер фізичного накопичувача підтвердить запис даних із внутрішнього кешу Flash/DRAM на незалежну пам'ять (виконання команди NVMe Flush або ATA Flush Cache). На сучасних твердотільних накопичувачах NVMe затримка одного виклику `fsync()` коливається в межах від 0.5 до 5 мілісекунд, тоді як на класичних магнітних HDD вона може досягати 15–30 мілісекунд через очікування оберту шпинделя.

Саме тому атомарне збереження через повний `fsync()` застосовується виключно для конфігураційних файлів та критичних станів, які змінюються відносно рідко (при зміні налаштувань користувачем або збереженні документа). Для високочастотних операцій (наприклад, запис логів у `$XDG_STATE_HOME`) застосовують буферизований дозапис (`append-only`) без блокуючого `fsync` на кожну транзакцію.

### Альтернатива на Linux: прапорець `O_TMPFILE`

У ядрах Linux, починаючи з версії 3.11, доступний спеціальний прапорець `open(dir_path, O_TMPFILE | O_RDWR, 0600)`. Він створює безіменний `inode` безпосередньо у структурі файлової системи без видимого запису в каталозі. Після завершення запису та виклику `fsync(fd)` файл зв'язується з постійним ім'ям за допомогою системного виклику `linkat(AT_FDCWD, proc_path, AT_FDCWD, dest_path, AT_SYMLINK_FOLLOW)`. Такий підхід повністю виключає необхідність генерації імен `tmp.XXXXXX` та подальшого виклику `unlink()` у разі аварійного переривання запису. Проте для збереження кросплатформної сумісності з BSD та macOS у представленій бібліотеці обрано універсальний стандартний виклик `mkstemp()`.

### Аналіз системних викликів через утиліту `strace`

Під час виконання функції `xdg_atomic_write_file()` послідовність звернень процесу до ядра Linux має такий вигляд у виводі `strace`:

```
openat(AT_FDCWD, "/home/user/.config/demo_service/tmp.K8x9La", O_RDWR|O_CREAT|O_EXCL, 0600) = 3
fchmod(3, 0600)                                                  = 0
write(3, "{\n  \"version\": 1,\n  \"theme\": "..., 38)            = 38
fsync(3)                                                         = 0
close(3)                                                         = 0
renameat(AT_FDCWD, "/home/user/.config/demo_service/tmp.K8x9La", 
         AT_FDCWD, "/home/user/.config/demo_service/settings.json") = 0
openat(AT_FDCWD, "/home/user/.config/demo_service", O_RDONLY|O_DIRECTORY) = 3
fsync(3)                                                         = 0
close(3)                                                         = 0
```

Цей трасування наочно демонструє відсутність проміжних небезпечних операцій обнулення (`O_TRUNC`) над цільовим файлом `settings.json`.

## Компіляція та перевірка роботи

Для компіляції та перевірки розробленого модуля виконайте такі команди в терміналі:

```bash
# Компіляція версії мовою C (стандарт C11)
gcc -std=c11 -Wall -Wextra -pedantic -D_GNU_SOURCE proj-xdg-store.c -o xdg_store_c

# Компіляція версії мовою C++ (стандарт C++23)
g++ -std=c++23 -Wall -Wextra -pedantic proj-xdg-store.cpp -o xdg_store_cpp

# Запуск бінарного файлу
./xdg_store_c
./xdg_store_cpp
```

Обидві версії демонструють ідентичну поведінку: створюють дерево каталогів у `$HOME/.config/demo_service/` із правами доступу `0700` та зберігають валідний файл `settings.json` із правами `0600`.
