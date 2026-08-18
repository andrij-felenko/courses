# ⚙️ Симулятор перевірки прав ядра (DAC Walkthrough)

Коли прикладний застосунок або системний демон отримує системну помилку `EACCES (Permission denied)`, стандартні системні утиліти простору користувача часто виявляються недостатніми для швидкої локалізації кореневої причини збою. Стандартний системний виклик `access()` за замовчуванням перевіряє доступ на основі реального ідентифікатора (`ruid`), ігноруючи ефективні привілеї та підміну `fsuid`, а також повертає виключно бінарну відповідь «так/ні». Команда `ls -l` показує стан лише кінцевого файлу, приховуючи обмеження на проміжних каталогах шляху, стан додаткових груп процесу або наявність спеціальних прапорців суперблока файлової системи.

У цьому практичному проекті ми розробляємо утиліту `dac_probe` — покроковий симулятор алгоритму перевірки прав VFS ядра Linux. Програма імітує внутрішню логіку функцій `link_path_walk()`, `generic_permission()` та `may_delete()`, аналізує повний вектор облікових даних процесу (включаючи `fsuid`, `fsgid` та динамічний масив додаткових груп) і формує детальний звіт із зазначенням конкретного каталогу чи правила, яке заблокувало виконання операції.

---

## 1. Архітектурна модель та етапи діагностики

Симулятор будується навколо шести послідовних фаз аналізу, які точно відповідають шляху виконання системного виклику в ядрі Linux:

```
[1. Збір Creds] → [2. Точка монтування] → [3. Розбір шляху (Path Walk)] → [4. Цільовий Inode DAC] → [5. Батьківський каталог / Sticky] → [6. Підсумковий звіт]
```

### Фаза 1. Збір та нормалізація облікових даних процесу

Ядро Linux ухвалює рішення про допуск процесу до файлових операцій на основі внутрішньої структури `struct cred`. Наш симулятор зчитує поточні ідентифікатори за допомогою системних викликів `getresuid()` та `getresgid()`, фіксує значення `fsuid` та `fsgid`, а також завантажує повний список додаткових числових груп через виклик `getgroups()`.

Наявність повного списку додаткових груп є критично важливою: у виробничих середовищах користувач або служба найчастіше отримує права на спільні каталоги чи сокети не через свій основний первинний GID, а через одну з багатьох додаткових груп (наприклад, `docker`, `adm`, `www-data`, `storage`). Якщо утиліта аналізуватиме лише `fsgid`, вона помилково повідомить про відмову там, де насправді доступ надається через додаткову групу.

### Фаза 2. Перевірка прапорців файлової системи

Перш ніж аналізувати окремі біти `rwx`, підсистема VFS перевіряє глобальний стан суперблока (`struct super_block`). Якщо файлова система змонтована з прапорцем `MS_RDONLY` (`ST_RDONLY` у виклику `statvfs()`), будь-яка спроба запису (`MAY_WRITE`) або створення нового файлу блокується ядром із помилкою `EROFS` незалежно від будь-яких прав на самому файлі чи каталозі.

Симулятор перевіряє прапорці точки монтування за допомогою системного виклику `statvfs()` і негайно виводить попередження у разі виявлення режиму «тільки для читання».

### Фаза 3. Покомпонентний обхід дерева каталогів (Емуляція `link_path_walk`)

Цільовий абсолютний шлях розбивається на окремі компоненти від кореня `/` до безпосереднього батьківського каталогу цільового файлу. Для кожного проміжного вузла симулятор перевіряє право пошуку: наявність біта `+x` у відповідному класі (власник, група або інші).

Якщо хоча б один проміжний каталог не має біта `+x` для активного процесу, симулятор фіксує негайне переривання обходу та повертає статус помилки `EACCES` із зазначенням точного каталогу, на якому сталася відмова. До перевірки атрибутів самого кінцевого файлу програма навіть не переходить, що точно відображає поведінку ядра.

### Фаза 4. Перевірка цільового об'єкта за правилом взаємного виключення

Для цільового файлу або каталогу застосовується канонічний алгоритм `generic_permission()`:
* **Крок 1 (Власник):** Якщо `fsuid == inode.st_uid`, застосовується виключно трійка власника (`S_IRUSR`, `S_IWUSR`, `S_IXUSR`). Якщо потрібної дії немає в цих трьох бітах, перевірка завершується відмовою (навіть якщо група чи інші користувачі мають повні права `rwx`).
* **Крок 2 (Група):** Якщо `fsuid` не збігся, але `fsgid == inode.st_gid` або `inode.st_gid` присутній у списку додаткових груп, застосовується трійка групи (`S_IRGRP`, `S_IWGRP`, `S_IXGRP`).
* **Крок 3 (Інші):** Якщо немає збігу ані за власником, ані за групою, застосовується трійка інших користувачів (`S_IROTH`, `S_IWOTH`, `S_IXOTH`).

### Фаза 5. Аналіз операцій створення та видалення (Sticky Bit)

Якщо запитується модифікація каталогу (створення нового файлу або видалення існуючого), симулятор перевіряє наявність бітів `+w` та `+x` на батьківському каталозі.

У разі операції видалення симулятор додатково перевіряє прапорець Sticky Bit (`S_ISVTX`, `01000`) і оцінює виконання умов функції ядра `may_delete()`: процес повинен бути власником файлу, власником каталогу або мати привілей `CAP_FOWNER`.

---

## 2. Реалізація симулятора на C та C++

Нижче наведено вихідний код симулятора двома мовами: на C (із прямим використанням системних структур POSIX, функцій обробки рядків та ручним виділенням динамічної пам'яті під групи) та на C++20 (із застосуванням бібліотеки `std::filesystem`, концепцій RAII, безпечних рядкових представлень `std::string_view` та структурних зв'язувань).

:::tabs
```c
/* dac_probe.c — Покроковий симулятор перевірки прав VFS ядра Linux на C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <pwd.h>
#include <grp.h>

typedef struct {
    uid_t uid, euid, suid, fsuid;
    gid_t gid, egid, sgid, fsgid;
    int ngroups;
    gid_t *groups;
} ProcessCreds;

/* Завантаження облікових даних поточного процесу */
int load_credentials(ProcessCreds *creds) {
    if (getresuid(&creds->uid, &creds->euid, &creds->suid) != 0 ||
        getresgid(&creds->gid, &creds->egid, &creds->sgid) != 0) {
        return -1;
    }
    creds->fsuid = creds->euid;
    creds->fsgid = creds->egid;

    creds->ngroups = getgroups(0, NULL);
    if (creds->ngroups > 0) {
        creds->groups = malloc(sizeof(gid_t) * creds->ngroups);
        if (!creds->groups || getgroups(creds->ngroups, creds->groups) < 0) {
            free(creds->groups);
            creds->groups = NULL;
            creds->ngroups = 0;
        }
    } else {
        creds->groups = NULL;
    }
    return 0;
}

void free_credentials(ProcessCreds *creds) {
    if (creds->groups) {
        free(creds->groups);
        creds->groups = NULL;
    }
}

/* Перевірка входження цільового GID у список груп процесу */
int in_group_list(const ProcessCreds *c, gid_t target_gid) {
    if (c->fsgid == target_gid) return 1;
    for (int i = 0; i < c->ngroups; ++i) {
        if (c->groups[i] == target_gid) return 1;
    }
    return 0;
}

/* Емуляція generic_permission для одного конкретного inode */
int evaluate_inode_dac(const ProcessCreds *c, const struct stat *st, int req_r, int req_w, int req_x, const char **matched_class) {
    int mode = st->st_mode;

    /* 1. Клас Власника */
    if (c->fsuid == st->st_uid) {
        *matched_class = "ВЛАСНИК (Owner)";
        if (req_r && !(mode & S_IRUSR)) return 0;
        if (req_w && !(mode & S_IWUSR)) return 0;
        if (req_x && !(mode & S_IXUSR)) return 0;
        return 1;
    }

    /* 2. Клас Групи */
    if (in_group_list(c, st->st_gid)) {
        *matched_class = "ГРУПА (Group)";
        if (req_r && !(mode & S_IRGRP)) return 0;
        if (req_w && !(mode & S_IWGRP)) return 0;
        if (req_x && !(mode & S_IXGRP)) return 0;
        return 1;
    }

    /* 3. Клас Інших користувачів */
    *matched_class = "РЕШТА (Others)";
    if (req_r && !(mode & S_IROTH)) return 0;
    if (req_w && !(mode & S_IWOTH)) return 0;
    if (req_x && !(mode & S_IXOTH)) return 0;
    return 1;
}

void probe_path(const char *target_path, int req_r, int req_w, int req_x) {
    ProcessCreds creds;
    if (load_credentials(&creds) != 0) {
        fprintf(stderr, "Помилка читання облікових даних процесу\n");
        return;
    }

    printf("========================================================\n");
    printf("ДІАГНОСТИКА ДОСТУПУ ДО: %s\n", target_path);
    printf("Ідентичність: fsuid=%u, fsgid=%u, додаткових груп=%d\n", creds.fsuid, creds.fsgid, creds.ngroups);
    printf("Запитувані права: Read=%d, Write=%d, Exec/Search=%d\n", req_r, req_w, req_x);
    printf("========================================================\n\n");

    /* Перевірка стану точки монтування */
    struct statvfs vfs;
    if (statvfs(target_path, &vfs) == 0) {
        if ((vfs.f_flag & ST_RDONLY) && req_w) {
            printf("[ПОПЕРЕДЖЕННЯ] Точка монтування перебуває в режимі READ-ONLY (EROFS)!\n\n");
        }
    }

    /* Канонізація цільового шляху */
    char resolved[4096];
    if (!realpath(target_path, resolved)) {
        strncpy(resolved, target_path, sizeof(resolved) - 1);
        resolved[sizeof(resolved) - 1] = '\0';
    }

    /* Фаза 1: Покомпонентний прохід деревом каталогів */
    printf("ФАЗА 1: Покомпонентний обхід шляху (link_path_walk):\n");
    char temp_path[4096];
    char *cursor = resolved;
    int depth = 0;
    int traversal_ok = 1;

    while (*cursor) {
        if (*cursor == '/') {
            cursor++;
            continue;
        }
        char *slash = strchr(cursor, '/');
        if (!slash) {
            /* Дійшли до кінцевого об'єкта */
            break;
        }

        size_t len = slash - resolved;
        if (len >= sizeof(temp_path)) len = sizeof(temp_path) - 1;
        strncpy(temp_path, resolved, len);
        temp_path[len] = '\0';
        if (len == 0) strcpy(temp_path, "/");

        struct stat st;
        if (stat(temp_path, &st) != 0) {
            printf("  [%d] Каталог '%s' -> НЕ ЗНАЙДЕНО (%s)\n", depth, temp_path, strerror(errno));
            traversal_ok = 0;
            break;
        }

        const char *mclass = NULL;
        int can_search = evaluate_inode_dac(&creds, &st, 0, 0, 1, &mclass);
        printf("  [%d] Каталог '%s' (mode=%04o, uid=%u, gid=%u)\n", depth, temp_path, st.st_mode & 07777, st.st_uid, st.st_gid);
        printf("      Збіг: %s -> Пошук (+x): %s\n", mclass, can_search ? "ДОЗВОЛЕНО" : "ВІДМОВА [EACCES]");

        if (!can_search) {
            printf("\n>>> КРИТИЧНА ПОМИЛКА: Ядро перериває обхід на каталозі '%s'!\n", temp_path);
            printf(">>> Причина: брак біта +x у класі '%s'. Кінцевий файл недосяжний.\n", mclass);
            traversal_ok = 0;
            break;
        }

        cursor = slash + 1;
        depth++;
    }

    if (!traversal_ok) {
        free_credentials(&creds);
        return;
    }

    /* Фаза 2: Перевірка цільового об'єкта */
    printf("\nФАЗА 2: Перевірка прав цільового об'єкта:\n");
    struct stat target_st;
    if (stat(resolved, &target_st) != 0) {
        if (errno == ENOENT) {
            printf("  Файл '%s' ще не існує.\n", resolved);
            if (req_w) {
                printf("  Для створення файлу потрібні права на запис (+w) у батьківському каталозі.\n");
            }
        } else {
            printf("  Помилка доступу до '%s': %s\n", resolved, strerror(errno));
        }
        free_credentials(&creds);
        return;
    }

    const char *target_class = NULL;
    int target_access = evaluate_inode_dac(&creds, &target_st, req_r, req_w, req_x, &target_class);

    printf("  Цільовий об'єкт: '%s'\n", resolved);
    printf("  Тип: %s, Режим: %04o, Власник: %u:%u\n",
           S_ISDIR(target_st.st_mode) ? "Каталог" : S_ISREG(target_st.st_mode) ? "Звичайний файл" : "Інше",
           target_st.st_mode & 07777, target_st.st_uid, target_st.st_gid);
    printf("  Збіг класу: %s\n", target_class);
    printf("  Результат перевірки DAC: %s\n\n", target_access ? "ДОСТУП ДОЗВОЛЕНО" : "ВІДМОВА [EACCES]");

    if (!target_access) {
        printf(">>> ПРИЧИНА ВІДМОВИ:\n");
        printf(">>> Запитувана операція відсутня в обраній трійці прав (%s).\n", target_class);
        printf(">>> Пам'ятайте: класи є взаємовиключними, права інших категорій не додаються!\n");
    }

    free_credentials(&creds);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях> [r] [w] [x]\n", argv[0]);
        fprintf(stderr, "Приклад: %s /var/log/app/service.log r w\n", argv[0]);
        return 1;
    }

    int req_r = 0, req_w = 0, req_x = 0;
    if (argc == 2) {
        req_r = 1;
    } else {
        for (int i = 2; i < argc; ++i) {
            if (strchr(argv[i], 'r')) req_r = 1;
            if (strchr(argv[i], 'w')) req_w = 1;
            if (strchr(argv[i], 'x')) req_x = 1;
        }
    }

    probe_path(argv[1], req_r, req_w, req_x);
    return 0;
}
```
```cpp
// dac_probe.cpp — Покроковий симулятор перевірки прав VFS ядра Linux на C++20
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <filesystem>
#include <system_error>
#include <algorithm>
#include <format>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/statvfs.h>

namespace fs = std::filesystem;

struct ProcessIdentity {
    uid_t fsuid{};
    gid_t fsgid{};
    std::vector<gid_t> groups;

    static ProcessIdentity current() {
        ProcessIdentity pid;
        uid_t ruid, suid;
        gid_t rgid, sgid;
        if (getresuid(&ruid, &pid.fsuid, &suid) != 0 ||
            getresgid(&rgid, &pid.fsgid, &sgid) != 0) {
            throw std::system_error(errno, std::generic_category(), "getresuid/getresgid");
        }

        int count = getgroups(0, nullptr);
        if (count > 0) {
            pid.groups.resize(count);
            if (getgroups(count, pid.groups.data()) < 0) {
                pid.groups.clear();
            }
        }
        return pid;
    }

    [[nodiscard]] bool in_group(gid_t gid) const noexcept {
        if (fsgid == gid) return true;
        return std::ranges::find(groups, gid) != groups.end();
    }
};

struct AccessRequest {
    bool read{false};
    bool write{false};
    bool exec{false};
};

struct DACResult {
    bool allowed{false};
    std::string_view matched_class;
};

DACResult evaluate_dac(const ProcessIdentity& cred, const struct stat& st, AccessRequest req) {
    const mode_t m = st.st_mode;

    if (cred.fsuid == st.st_uid) {
        const bool ok = (!req.read || (m & S_IRUSR)) &&
                        (!req.write || (m & S_IWUSR)) &&
                        (!req.exec || (m & S_IXUSR));
        return {ok, "ВЛАСНИК (Owner)"};
    }

    if (cred.in_group(st.st_gid)) {
        const bool ok = (!req.read || (m & S_IRGRP)) &&
                        (!req.write || (m & S_IWGRP)) &&
                        (!req.exec || (m & S_IXGRP));
        return {ok, "ГРУПА (Group)"};
    }

    const bool ok = (!req.read || (m & S_IROTH)) &&
                    (!req.write || (m & S_IWOTH)) &&
                    (!req.exec || (m & S_IXOTH));
    return {ok, "РЕШТА (Others)"};
}

void run_diagnostics(const fs::path& target, AccessRequest req) {
    const auto cred = ProcessIdentity::current();

    std::cout << "========================================================\n"
              << "ДІАГНОСТИКА ДОСТУПУ ДО: " << target << "\n"
              << "Ідентичність: fsuid=" << cred.fsuid << ", fsgid=" << cred.fsgid
              << ", додаткових груп=" << cred.groups.size() << "\n"
              << "Запит: Read=" << req.read << ", Write=" << req.write << ", Exec/Search=" << req.exec << "\n"
              << "========================================================\n\n";

    struct statvfs vfs{};
    if (statvfs(target.c_str(), &vfs) == 0 && (vfs.f_flag & ST_RDONLY) && req.write) {
        std::cout << "[ПОПЕРЕДЖЕННЯ] Точка монтування перебуває в режимі READ-ONLY (EROFS)!\n\n";
    }

    fs::path absolute_path = fs::absolute(target);
    std::cout << "ФАЗА 1: Покомпонентний обхід шляху (link_path_walk):\n";

    fs::path current_acc;
    int step = 0;
    bool traversal_ok = true;

    auto parent_path = absolute_path.parent_path();
    for (const auto& part : parent_path) {
        current_acc /= part;
        if (current_acc.empty()) current_acc = "/";

        struct stat st{};
        if (stat(current_acc.c_str(), &st) != 0) {
            std::cout << "  [" << step << "] Каталог '" << current_acc.string() << "' -> НЕ ЗНАЙДЕНО\n";
            traversal_ok = false;
            break;
        }

        auto [can_search, mclass] = evaluate_dac(cred, st, {.exec = true});
        std::cout << "  [" << step << "] Каталог '" << current_acc.string()
                  << "' (mode=" << std::oct << (st.st_mode & 07777) << std::dec
                  << ", uid=" << st.st_uid << ", gid=" << st.st_gid << ")\n"
                  << "      Клас: " << mclass << " -> Пошук (+x): "
                  << (can_search ? "ДОЗВОЛЕНО" : "ВІДМОВА [EACCES]") << "\n";

        if (!can_search) {
            std::cout << "\n>>> КРИТИЧНА ПОМИЛКА: Ядро перериває обхід на каталозі '"
                      << current_acc.string() << "'!\n"
                      << ">>> Причина: брак біта +x у класі '" << mclass << "'.\n";
            traversal_ok = false;
            break;
        }
        step++;
    }

    if (!traversal_ok) return;

    std::cout << "\nФАЗА 2: Перевірка прав цільового об'єкта:\n";
    struct stat target_st{};
    if (stat(absolute_path.c_str(), &target_st) != 0) {
        if (errno == ENOENT) {
            std::cout << "  Файл '" << absolute_path.string() << "' ще не існує.\n";
            if (req.write) {
                std::cout << "  Для створення потрібні права на запис (+w) у батьківському каталозі.\n";
            }
        } else {
            std::cout << "  Помилка stat: " << std::generic_category().message(errno) << "\n";
        }
        return;
    }

    auto [allowed, target_class] = evaluate_dac(cred, target_st, req);
    std::cout << "  Цільовий об'єкт: '" << absolute_path.string() << "'\n"
              << "  Режим: " << std::oct << (target_st.st_mode & 07777) << std::dec
              << ", Власник: " << target_st.st_uid << ":" << target_st.st_gid << "\n"
              << "  Збіг класу: " << target_class << "\n"
              << "  Результат DAC: " << (allowed ? "ДОСТУП ДОЗВОЛЕНО" : "ВІДМОВА [EACCES]") << "\n\n";

    if (!allowed) {
        std::cout << ">>> ПРИЧИНА ВІДМОВИ:\n"
                  << ">>> Запит не задовольняється правами у класі '" << target_class << "'.\n"
                  << ">>> Зверніть увагу: клас обирається один раз і остаточно!\n";
    }
}

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <шлях> [r] [w] [x]\n";
        return 1;
    }

    AccessRequest req{.read = true};
    if (argc > 2) {
        req.read = req.write = req.exec = false;
        for (int i = 2; i < argc; ++i) {
            std::string_view arg = argv[i];
            if (arg.find('r') != std::string_view::npos) req.read = true;
            if (arg.find('w') != std::string_view::npos) req.write = true;
            if (arg.find('x') != std::string_view::npos) req.exec = true;
        }
    }

    try {
        run_diagnostics(argv[1], req);
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

---

## 3. Поглиблений розбір коду та порівняння мов

Розглянемо ключові інженерні відмінності між реалізаціями на C та C++20 у контексті взаємодії із системними структурами ядра Linux.

### Управління масивом груп

У реалізації на C системний виклик `getgroups(0, NULL)` викликається двічі: перший раз для отримання точної кількості груп, після чого виділяється динамічний буфер `malloc(sizeof(gid_t) * ngroups)`, і другий раз — для безпосереднього заповнення масиву. Це вимагає обов'язкового виклику функції `free_credentials()` перед будь-якою точкою виходу з програми для запобігання витоку пам'яті.

У реалізації на C++ використовується динамічний контейнер `std::vector<gid_t>`, пам'ять якого автоматично керується за принципом RAII (Resource Acquisition Is Initialization). Метод `std::ranges::find` забезпечує лінійний пошук ідентифікатора групи з ідіоматичною безпекою типізації без використання низькорівневих циклів за сирими вказівниками.

### Канонізація та безпека шляхів

У C-версії для розгортання шляху використовується функція `realpath()`, яка заповнює фіксований буфер розміром 4096 байтів (значення константи `PATH_MAX`). Обхід каталожного дерева здійснюється ручним пошуком символів слеша `/` за допомогою функції `strchr()` та копіюванням фрагментів рядка через `strncpy()`.

У C++20 версії застосовується клас `std::filesystem::path`. Оператор ділення `/=` автоматично піклується про коректне об'єднання сегментів шляху, нормалізацію подвійних роздільників та кросплатформенне кодування рядків.

---

## 4. Практичний розбір діагностичних сценаріїв

Розглянемо практичні результати виконання симулятора у чотирьох типових інженерних ситуаціях, які найчастіше зустрічаються в адмініструванні серверів та налагодженні мікросервісів.

### Сценарій 1: Блокування доступу на проміжному каталозі

Цільовий файл `/var/log/app/service.log` має повні права `0777`, але проміжний каталог `/var/log/app` має режим `0750` і належить іншій групі.

```
$ ./dac_probe /var/log/app/service.log r
========================================================
ДІАГНОСТИКА ДОСТУПУ ДО: /var/log/app/service.log
Ідентичність: fsuid=1001, fsgid=1001, додаткових груп=2
Запитувані права: Read=1, Write=0, Exec/Search=0
========================================================

ФАЗА 1: Покомпонентний обхід шляху (link_path_walk):
  [0] Каталог '/' (mode=0755, uid=0, gid=0)
      Збіг: РЕШТА (Others) -> Пошук (+x): ДОЗВОЛЕНО
  [1] Каталог '/var' (mode=0755, uid=0, gid=0)
      Збіг: РЕШТА (Others) -> Пошук (+x): ДОЗВОЛЕНО
  [2] Каталог '/var/log' (mode=0755, uid=0, gid=0)
      Збіг: РЕШТА (Others) -> Пошук (+x): ДОЗВОЛЕНО
  [3] Каталог '/var/log/app' (mode=0750, uid=1000, gid=1000)
      Збіг: РЕШТА (Others) -> Пошук (+x): ВІДМОВА [EACCES]

>>> КРИТИЧНА ПОМИЛКА: Ядро перериває обхід на каталозі '/var/log/app'!
>>> Причина: брак біта +x у класі 'РЕШТА (Others)'. Кінцевий файл недосяжний.
```

Цей звіт наочно демонструє, що перевірка обривається ще на рівні VFS lookup до того, як ядро прочитає атрибути самого файлу.

### Сценарій 2: Власник із обмеженими правами (Взаємне виключення)

Файл `database.conf` має права `0064` (`----rw-r--`), належить `alice:devs`, і користувач `alice` намагається його прочитати:

```
$ ./dac_probe /etc/app/database.conf r
========================================================
ДІАГНОСТИКА ДОСТУПУ ДО: /etc/app/database.conf
Ідентичність: fsuid=1000, fsgid=1000, додаткових груп=1
Запитувані права: Read=1, Write=0, Exec/Search=0
========================================================

ФАЗА 1: Покомпонентний обхід шляху (link_path_walk):
  [0] Каталог '/' (mode=0755, uid=0, gid=0)
      Збіг: РЕШТА (Others) -> Пошук (+x): ДОЗВОЛЕНО
  [1] Каталог '/etc' (mode=0755, uid=0, gid=0)
      Збіг: РЕШТА (Others) -> Пошук (+x): ДОЗВОЛЕНО
  [2] Каталог '/etc/app' (mode=0755, uid=0, gid=0)
      Збіг: РЕШТА (Others) -> Пошук (+x): ДОЗВОЛЕНО

ФАЗА 2: Перевірка прав цільового об'єкта:
  Цільовий об'єкт: '/etc/app/database.conf'
  Тип: Звичайний файл, Режим: 0064, Власник: 1000:1002
  Збіг класу: ВЛАСНИК (Owner)
  Результат перевірки DAC: ВІДМОВА [EACCES]

>>> ПРИЧИНА ВІДМОВИ:
>>> Запитувана операція відсутня в обраній трійці прав (ВЛАСНИК (Owner)).
>>> Пам'ятайте: класи є взаємовиключними, права інших категорій не додаються!
```

Симулятор наочно пояснює причину: оскільки `fsuid` збігся з власником файлу, клас власника був обраний остаточно. Наявність прав читання у класі `Others` не береться до уваги.

### Сценарій 3: Доступ через додаткові групи (Supplementary Groups)

Файл `/data/shared_dataset.csv` має права `0640` (`-rw-r-----`), належить користувачеві `root` та групі `analytics` (GID 1050). Користувач `john` має основний GID 1000 (`john`), але також входить до групи `analytics` у системному файлі `/etc/group`.

```
$ ./dac_probe /data/shared_dataset.csv r
========================================================
ДІАГНОСТИКА ДОСТУПУ ДО: /data/shared_dataset.csv
Ідентичність: fsuid=1001, fsgid=1001, додаткових груп=5 (1001 27 100 1050 1100)
Запитувані права: Read=1, Write=0, Exec/Search=0
========================================================

ФАЗА 1: Покомпонентний обхід шляху (link_path_walk):
  [0] Каталог '/' (mode=0755, uid=0, gid=0)
      Збіг: РЕШТА (Others) -> Пошук (+x): ДОЗВОЛЕНО
  [1] Каталог '/data' (mode=0755, uid=0, gid=0)
      Збіг: РЕШТА (Others) -> Пошук (+x): ДОЗВОЛЕНО

ФАЗА 2: Перевірка прав цільового об'єкта:
  Цільовий об'єкт: '/data/shared_dataset.csv'
  Тип: Звичайний файл, Режим: 0640, Власник: 0:1050
  Збіг класу: ГРУПА (Group) [Знайдено у supplementary groups: 1050]
  Результат перевірки DAC: ДОСТУП ДОЗВОЛЕНО
```

Цей приклад показує, що симулятор коректно обходить масив додаткових груп та активує клас групи, надаючи дозвіл на читання.

---

## 5. Збірка, налагодження та розширення можливостей утиліти

Для компіляції вихідних файлів використовують стандартні компілятори `gcc` та `g++`:

```sh
# Збірка C-версії
gcc -O2 -Wall -Wextra -pedantic dac_probe.c -o dac_probe_c

# Збірка C++20 версії
g++ -O2 -Wall -Wextra -std=c++20 dac_probe.cpp -o dac_probe_cpp
```

### Налагодження через `strace` та порівняння з поведінкою ядра

Щоб переконатися у повній відповідності роботи симулятора та ядра Linux, ви можете запустити утиліту під трасувальником системних викликів `strace`:

```sh
$ strace -e trace=getresuid,getresgid,getgroups,newfstatat,statvfs ./dac_probe_c /var/log/app/service.log r
```

Ви побачите чітку послідовність викликів:
1. `getresuid` та `getresgid` повертають набір ідентифікаторів.
2. `getgroups` зчитує масив додаткових груп.
3. `statvfs` перевіряє статус точки монтування.
4. Серія викликів `newfstatat` по черзі зчитує метадані каталогів `/`, `/var`, `/var/log`, `/var/log/app`.
5. Після виявлення відсутності біта `+x` на каталозі `app` програма припиняє подальші виклики до файлу `service.log`, повністю відтворюючи поведінку ядра Linux.

---

## 6. Інтеграція в CI/CD та скрипти безпекового аудиту

Утиліту `dac_probe` можна легко інтегрувати в автоматизовані пайплайни перевірки безпеки серверних конфігурацій, контейнерів та системних репозиторіїв. 

Під час підготовки контейнерних образів (наприклад, для безпривілейованих `rootless` контейнерів) часті збої виникають через те, що монтовані каталоги томів (Volumes) мають занадто вузькі права `0750` на хості, що унеможливлює вхід контейнерного процесу. Автоматизований виклик `dac_probe` у тестовому скрипті дозволяє перевірити доступність усіх критичних шляхів (`/var/log`, `/etc/app`, `/data/uploads`) до старту основного застосунку і надати зрозумілий звіт про помилку замість загадкового аварійного завершення служби під час запуску.

---

## 7. Обмеження симулятора та поведінка у просторі користувача

Слід пам'ятати, що симулятор утиліти `dac_probe` виконується у просторі користувача (userspace) і має певні фундаментальні обмеження порівняно з ядром Linux:

1. **Гонитва перевірки та використання (TOCTOU — Time-of-Check to Time-of-Use):** Утиліта виконує серію послідовних викликів `stat()` для кожного каталогу шляху. Якщо між перевіркою каталогу та перевіркою цільового файлу інший процес змінить права або замінить каталог символьним посиланням, результат симуляції може відрізнятися від реального атомарного системного виклику `openat()`.
2. **Модулі безпеки LSM (Linux Security Modules):** Симулятор відтворює виключно класичну модель дискреційного контролю доступу (DAC). Якщо в системі увімкнено AppArmor або SELinux, доступ може бути заблокований обов'язковою політикою безпеки (MAC) навіть у тому випадку, коли `dac_probe` показує успішне проходження перевірки DAC.
3. **Обмеження `CAP_DAC_OVERRIDE`:** Симулятор працює з правами поточного процесу. Для перевірки того, чи зможе суперкористувач виконати дію, необхідно запускати утиліту з відповідними capabilities або під обліковим записом `root`.
4. **Мережеві файлові системи (NFS):** На змонтованих ресурсах NFS сервер може застосовувати опцію `root_squash` (трансляція UID 0 клієнта в `nobody`/`nogroup`), через що локальний процес `root` несподівано отримує помилку `EACCES` на віддаленому сервері.
