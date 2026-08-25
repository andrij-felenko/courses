# ⚙️ Інспекція ієрархії FHS та аналіз точок монтування

Практичний інструмент розробника та системного адміністратора для програмної інспекції файлової системи Linux. Програма аналізує ключові каталоги специфікації FHS 3.0 (`/usr`, `/var`, `/tmp`, `/etc`), перевіряє статус впровадження `usrmerge` (наявність та коректність символічних посилань для `/bin`, `/sbin`, `/lib`), визначає межі окремих файлових систем за допомогою `st_dev` та перевіряє прапори монтування (наприклад, наявність прапорця `read-only` для `/usr`).

## 1. Концепція та системні виклики

Для аналізу ієрархії файлової системи у середовищі Linux використовується сукупність системних викликів POSIX та специфічних інтерфейсів ядра:
1. `lstat()` або `std::filesystem::symlink_status()` — дозволяє відрізнити звичайний каталог від символічного посилання `usrmerge` (наприклад, `/bin -> usr/bin`). Використання звичайного `stat()` автоматично переходить за посиланням, що приховало б факт існування симлінка.
2. `statvfs()` — повертає прапори файлової системи (`ST_RDONLY`, `ST_NOSUID`, `ST_NODEV`), геометрію блоків та кількість вільних інодів.
3. `stat()` — повертає ідентифікатор пристрою `st_dev`, що дозволяє визначити, чи знаходиться каталог на окремому змонтованому накопичувачі відносно кореневого каталогу `/`.
4. `/proc/mounts` — містить таблицю активних точок монтування ядра Linux, що дозволяє отримати назву файлової системи (ext4, btrfs, tmpfs) та опції монтування.

Нижче наведено дві повноцінні ідіоматичні реалізації інспектора FHS — мовами **C** та **C++**.

## 2. Системний інспектор FHS

:::tabs
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <errno.h>

typedef struct {
    const char *path;
    const char *expected_type;
    int is_symlink;
    char target_path[256];
    dev_t dev_id;
    int is_readonly;
} fhs_entry_info_t;

static int inspect_fhs_path(const char *path, fhs_entry_info_t *info) {
    struct stat st;
    struct statvfs stfs;
    ssize_t len;

    memset(info, 0, sizeof(*info));
    info->path = path;

    if (lstat(path, &st) != 0) {
        return -1;
    }

    info->dev_id = st.st_dev;

    if (S_ISLNK(st.st_mode)) {
        info->is_symlink = 1;
        len = readlink(path, info->target_path, sizeof(info->target_path) - 1);
        if (len != -1) {
            info->target_path[len] = '\0';
        } else {
            snprintf(info->target_path, sizeof(info->target_path), "<error>");
        }
    }

    if (statvfs(path, &stfs) == 0) {
        if (stfs.f_flag & ST_RDONLY) {
            info->is_readonly = 1;
        }
    }

    return 0;
}

static void print_fhs_report(const fhs_entry_info_t *info) {
    printf("Каталог: %-12s | ", info->path);
    if (info->is_symlink) {
        printf("Тип: SYMLINK -> %-12s | ", info->target_path);
    } else {
        printf("Тип: DIRECTORY           | ");
    }
    printf("DevID: 0x%-6lx | ", (unsigned long)info->dev_id);
    printf("Mode: %s\n", info->is_readonly ? "READ-ONLY" : "READ-WRITE");
}

int main(void) {
    const char *fhs_paths[] = {
        "/",
        "/bin",
        "/sbin",
        "/lib",
        "/usr",
        "/usr/bin",
        "/var",
        "/var/log",
        "/etc",
        "/tmp",
        "/run"
    };
    size_t path_count = sizeof(fhs_paths) / sizeof(fhs_paths[0]);
    fhs_entry_info_t info;

    printf("=== ЗВІТ ІНСПЕКЦІЇ ІЄРАРХІЇ FHS 3.0 (C Impl) ===\n\n");

    int usrmerge_active = 1;

    for (size_t i = 0; i < path_count; ++i) {
        if (inspect_fhs_path(fhs_paths[i], &info) == 0) {
            print_fhs_report(&info);
            if ((strcmp(fhs_paths[i], "/bin") == 0 || strcmp(fhs_paths[i], "/lib") == 0) && !info.is_symlink) {
                usrmerge_active = 0;
            }
        } else {
            printf("Каталог: %-12s | Стан: ВІДСУТНІЙ (%s)\n", fhs_paths[i], strerror(errno));
        }
    }

    printf("\nСтатус usrmerge: %s\n", usrmerge_active ? "АКТИВНО (успішно об'єднано)" : "ТРАДИЦІЙНИЙ (окремі каталоги)");

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <filesystem>
#include <vector>
#include <string>
#include <string_view>
#include <iomanip>
#include <sys/statvfs.h>
#include <sys/stat.h>

namespace fs = std::filesystem;

struct FhsNodeInfo {
    std::string path;
    bool is_symlink{false};
    std::string symlink_target{};
    dev_t device_id{0};
    bool is_readonly{false};
    bool exists{false};
};

class FhsInspector {
public:
    static FhsNodeInfo inspect(std::string_view path_str) {
        FhsNodeInfo node;
        node.path = path_str;
        fs::path p(path_str);

        std::error_code ec;
        fs::file_status status = fs::symlink_status(p, ec);

        if (ec || status.type() == fs::file_type::not_found) {
            node.exists = false;
            return node;
        }

        node.exists = true;
        if (fs::is_symlink(status)) {
            node.is_symlink = true;
            fs::path target = fs::read_symlink(p, ec);
            node.symlink_target = ec ? "<invalid_link>" : target.string();
        }

        struct stat st{};
        if (::stat(node.path.c_str(), &st) == 0) {
            node.device_id = st.st_dev;
        }

        struct statvfs stfs{};
        if (::statvfs(node.path.c_str(), &stfs) == 0) {
            node.is_readonly = (stfs.f_flag & ST_RDONLY) != 0;
        }

        return node;
    }

    static void print_report(const std::vector<FhsNodeInfo>& nodes) {
        std::cout << "=== ЗВІТ ІНСПЕКЦІЇ ІЄРАРХІЇ FHS 3.0 (C++20 Impl) ===\n\n";

        bool usrmerge_detected = true;

        for (const auto& node : nodes) {
            if (!node.exists) {
                std::cout << "Каталог: " << std::left << std::setw(12) << node.path
                          << " | Стан: ВІДСУТНІЙ\n";
                continue;
            }

            std::cout << "Каталог: " << std::left << std::setw(12) << node.path << " | ";
            if (node.is_symlink) {
                std::cout << "Тип: SYMLINK -> " << std::left << std::setw(12) << node.symlink_target << " | ";
            } else {
                std::cout << "Тип: DIRECTORY           | ";
            }

            std::cout << "DevID: 0x" << std::hex << node.device_id << std::dec << " | "
                      << "Mode: " << (node.is_readonly ? "READ-ONLY" : "READ-WRITE") << "\n";

            if ((node.path == "/bin" || node.path == "/lib") && !node.is_symlink) {
                usrmerge_detected = false;
            }
        }

        std::cout << "\nСтатус usrmerge: " 
                  << (usrmerge_detected ? "АКТИВНО (успішно об'єднано)" : "ТРАДИЦІЙНИЙ (окремі каталоги)")
                  << "\n";
    }
};

int main() {
    const std::vector<std::string_view> target_paths = {
        "/", "/bin", "/sbin", "/lib", "/usr", "/usr/bin",
        "/var", "/var/log", "/etc", "/tmp", "/run"
    };

    std::vector<FhsNodeInfo> results;
    results.reserve(target_paths.size());

    for (auto path : target_paths) {
        results.push_back(FhsInspector::inspect(path));
    }

    FhsInspector::print_report(results);

    return 0;
}
```
:::

## 3. Детальний аналіз алгоритму та системних викликів

Програма виконує покроковий аналіз заданого списку ш шляхів у системі:

1. **Аналіз статусів та розрізнення символічних посилань**:
   При використанні виклику `lstat()` ядро перевіряє атрибути самого запису у каталозі, а не файла, на який воно вказує. Це ключовий момент: якщо замість `lstat()` викликати стандартну функцію `stat()`, ядро пройде за символічним посиланням `/bin -> usr/bin` і поверне атрибути цільового каталогу `/usr/bin`. В результаті програма помилково вирішить, що `/bin` є звичайним каталогом.

2. **Опитування цільового шляху через `readlink`**:
   Якщо прапорець `S_ISLNK` у масці `st_mode` встановлено в одиницю, програма викликає системну функцію `readlink()`. Ця функція копіює вміст символічного посилання у наданий буфер. Якщо результат містить `usr/bin` або `usr/lib`, це підтверджує успішну консолідацію бінарників згідно з концепцією `usrmerge`.

3. **Аналіз точок монтування за допомогою `st_dev`**:
   Поле `st_dev` у структурі `struct stat` містить старший та молодший майорні/мінорні номери пристрою файлової системи (макроси `major()` та `minor()`). Зіставивши значення `st_dev` каталогу `/usr` та кореневого каталогу `/`, програма точно визначає, чи рознесені ці каталоги по різних фізичних розділах накопичувача чи монтуються з єдиного дискового тома.

4. **Опитування прапорців монтування через `statvfs`**:
   Системна функція `statvfs()` зчитує сукупну статистику файлової системи. Поле `f_flag` містить бітові маски стану точки монтування. Перевірка прапорця `ST_RDONLY` опитує, чи знаходиться представлена ділянка файлового дерева в режимі захисту від запису (`read-only`).

## 4. Глибока інспекція структури `struct statvfs`

Для розробників системного рівня важливим є аналіз усіх полів структури `struct statvfs`:
- `f_bsize` — розмір блоку файлової системи (наприклад, 4096 байтів);
- `f_frsize` — фундаментальний розмір фрагмента;
- `f_blocks` — загальна кількість блоків у файловій системі;
- `f_bfree` — кількість вільних блоків для непривілейованих процесів;
- `f_files` — загальна кількість інодів (індексних вузлів);
- `f_ffree` — кількість вільних інодів;
- `f_namemax` — максимальна довжина імені файла (зазвичай 255 символів для ext4/btrfs).

## 5. Програмний парсинг /proc/mounts через setmntent

Для детальної перевірки параметрів точок монтування POSIX надає спеціалізовані функції для роботи з файлом `/proc/mounts` або `/etc/mtab`:
- `setmntent("/proc/mounts", "r")` — відкриває файл таблиці монтування та повертає покажчик `FILE*`;
- `getmntent(fp)` — послідовно читає записи та повертає покажчик на структуру `struct mntent` (поля `mnt_fsname`, `mnt_dir`, `mnt_type`, `mnt_opts`);
- `endmntent(fp)` — закриває потік таблиці монтування.

Використання `getmntent()` дозволяє інспектору отримати точний тип файлової системи (ext4, btrfs, zfs, overlay, tmpfs, proc, sysfs) та перевірити текстовий рядок параметрів монтування (наприклад, наявність `noexec` або `nosuid` у `/var/tmp`).

## 6. Інструкція з збірки та інтеграції в CI/CD

### Збірка програми
Для збірки версії на мові C скористайтеся GCC або Clang:
```bash
gcc -std=c11 -Wall -Wextra -O2 proj-fhs-traverser.c -o fhs_inspector_c
```

Для збірки версії на C++20 з використанням бібліотеки `<filesystem>`:
```bash
g++ -std=c++20 -Wall -Wextra -O2 proj-fhs-traverser.cpp -o fhs_inspector_cpp
```

### Використання у автоматичних тестах дистрибутива
Код інспектора може бути інтегрований у тестовий фреймворк збірки Linux-дистрибутива (наприклад, у формі тесту `pytest` або `bash` обгортки) для перевірки дотримання вимог FHS 3.0 та перевірки некоректного розміщення бінарних файлів у `/etc` або збоїв під час міграції `usrmerge`.

## 7. Робота з просторами імен точок монтування (Mount Namespaces)

При роботі у середовищі контейнеризації (Docker, Podman, systemd-nspawn) інспектор може аналізувати точки монтування ізольованого контейнера через `/proc/<PID>/mountinfo`. 

Файл `mountinfo` надає детальнішу інформацію ніж `/proc/mounts`:
- Поле `mount ID` та `parent ID` — утворюють ієрархічне дерево точок монтування;
- Поле `major:minor` — точні ідентифікатори пристрою;
- Поле `root` — корінь файлової системи всередині точки монтування;
- Поле `optional fields` — прапори поширення точок монтування (`shared`, `master`, `propagate_from`, `unbindable`).

## 8. Пастки та крайові випадки при інспекції

1. **Circular Symlinks при `usrmerge`**: При відносних символічних посиланнях (наприклад, `/bin -> usr/bin`), виконання `stat()` слідує за посиланням до `/usr/bin`, а `lstat()` опитує безпосередньо вузол посилання `/bin`. Використовуйте `lstat()` для перевірки статусу `usrmerge`.
2. **Помилки прав доступу (`EACCES`)**: При відсутності прав на виконання (`+x`) для проміжних каталогів виклики `stat()` повертають помилку `EACCES`. Програма має обробляти це коректно, не перериваючи аналіз інших шляхів.
3. **Обхід мережевих точок монтування**: При скануванні каталогів `/mnt` чи `/net` виклики `statvfs()` можуть блокувати потік виконання у разі таймауту мережевої ФС (NFS). Рекомендовано застосовувати асинхронні перевірки або таймаути.
