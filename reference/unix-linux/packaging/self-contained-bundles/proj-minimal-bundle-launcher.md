# ⚙️ Мінімальний лаунчер змонтованого пакунка мовами C та C++

Ця вставка демонструє повну низкорівневу реалізацію системного лаунчера самодостатнього пакунка, який створює новий простір імен монтажу (Mount Namespace), переводить точки монтажу в приватний режим, змонтовує каталог пакунка у ізольовану точку файлової системи, підготовлює змінні середовища оточення та передає керування цільовому бінарному файлу за допомогою системного виклику `execve`.

## Принцип роботи системного лаунчера

Для створення автономного ізольованого середовища запуску без використання важких зовнішніх демонів, лаунчер послідовно виконує шість базових системних кроків на рівні ядра Linux:

1. **Ізоляція простору імен монтажу (`unshare`):** Виклик `unshare(CLONE_NEWNS)` створює приватну копію таблиці монтажу файлової системи для поточного процесу та всіх його подальших нащадків. Будь-які маніпуляції з мотуванням чи демонтуванням не впливають на файлову систему основного хоста.
2. **Перетворення поширення точок монтажу (`mount propagation`):** За замовчуванням у багатьох дистрибутивах Linux точки монтажу успадковують прапор `MS_SHARED`. Лаунчер рекурсивно переводить корінь системи у режим `MS_PRIVATE` за допомогою системного виклику `mount(NULL, "/", NULL, MS_PRIVATE | MS_REC, NULL)`. Це унеможливлює витік нових точок монтажу у глобальний простір хост-системи.
3. **Підготовка точки призначення (`mkdir`):** Створюється тимчасова або постійна тека в системній файловій системі (наприклад, `/tmp/bundle_target`), яка слугуватиме коренем змонтованого пакунка.
4. **Монтування джерела (`bind mount`):** За допомогою прапорів `MS_BIND | MS_REC` лаунчер зв'язує каталог із розпакованим вмістом пакунка (або змонтованим образом SquashFS) із точкою призначення.
5. **Модифікація змінних середовища оточення (`environment setup`):** Лаунчер оновлює системні змінні `LD_LIBRARY_PATH` (додаючи шлях до внутрішніх `.so` бібліотек пакунка з найвищим пріоритетом) та `PATH` (для виконання внутрішніх утиліт).
6. **Заміщення образу процесу (`execve`):** Лаунчер викликає `execv()` для запуску цільового бінарника. Ядро повністю замінює код, стек та дані поточного процесу новим бінарним файлом, зберігаючи при цьому початковий ідентифікатор процесу (PID).

## Режими поширення монтажу (Mount Propagation)

Під час роботи з просторами імен монтажу критично важливо розуміти типи поширення точок монтажу між батьківським та дитячим namespace:

* **MS_SHARED:** Нові точки монтажу у батьківському просторі автоматично з'являються у дитячому, і навпаки. За замовчуванням у systemd корінь `/` є MS_SHARED.
* **MS_PRIVATE:** Повна ізоляція. Жодна точка монтажу не проникає назовні або всередину простору імен.
* **MS_SLAVE:** Одностороннє поширення. Нові точки з хоста проникають у пісочницю, але точки з пісочниці не витікають на хост.

Для лаунчерів пакунків режим `MS_PRIVATE` є обов'язковим стандартом безпеки.

## Порівняння системних викликів розпакування та монтування

Під час запуску бандла перед лаунчером стоїть вибір між двома підходами: розпакуванням вмісту у тимчасовий каталог чи віртуальним монтуванням образу:

| Метод | Переваги | Недоліки |
| :--- | :--- | :--- |
| **Розпакування на диск** | Не вимагає FUSE чи привілеїв `mount`. | Високе навантаження на диск (I/O overhead), повільний перший запуск, вимагає вільного місця у `/tmp`. |
| **FUSE / bind-mount** | Запуск за частки секунди, дані зчитуються з образу по мірі потреби (on-demand page read). | Вимагає модуля ядра FUSE або підтримки `unshare(CLONE_NEWNS)`. |

## Детальний розбір механіки заміщення процесів через execve

Системний виклик `execve()` є ключовим фінальним етапом роботи будь-кого лаунчера пакунків. Коли лаунчер підготував простір імен монтажу, змонтував SquashFS або виконав bind-mount каталогу пакунка та налаштував змінні середовища `LD_LIBRARY_PATH` та `PATH`, він передає керування цільовому бінарнику.

Під час виклику `execve()` ядро Linux здійснює такі дії:
* **Збереження PID та таблиці процесів:** Новий бінарний файл успадковує Process ID (PID) лаунчера, його батьківський процес (PPID), а також відкриті файлові дескриптори, якщо для них не було встановлено прапор `FD_CLOEXEC`.
* **Очищення пам'яті:** Стек, купа (heap), сегменти даних (BSS) та адресний простір лаунчера скидаються. Ядро відображає у пам'ять нові ELF-сегменти цільової програми та динамічного завантажувача.
* **Передача змінних середовища:** Масив `envp`, сформований лаунчером, передається цільовій програмі, забезпечуючи її роботу у підготовленому контексті бібліотек.

Ця механіка пояснює, чому у системному моніторі (`ps aux` або `top`) після запуску AppImage чи Flatpak відображається безпосередньо ім'я цільової програми (наприклад, `gimp` чи `firefox`), а не ім'я проміжного лаунчера.

## Непривілейовані простори імен (User Namespaces)

Якщо лаунчер запускається звичайним користувачем без прав root, виклик `unshare(CLONE_NEWNS)` може повернути помилку `EPERM`. Для обходу цього обмеження сучасні лаунчери (на кшталт `bubblewrap`) комбінують `CLONE_NEWNS` із простором імен користувачів `CLONE_NEWUSER`, передаючи системному виклику комбінацію прапорів `CLONE_NEWNS | CLONE_NEWUSER`.

Після цього лаунчер мапує поточного користувача хоста на UID 0 (root) усередині нового простору імен, що надає процесу право виконувати `mount(MS_BIND)` без системних привілеїв `CAP_SYS_ADMIN` на хості.

## Реалізація лаунчера мовами C та C++

Нижче наведено робочий приклад реалізації лаунчера. Приклад мовою C показує пряму роботу з POSIX системними викликами ядра Linux та ручну обробку коду помилок. Приклад мовою C++20 демонструє ідіоматичний підхід: використання концепції RAII для автоматичного гарантованого прибирання точок монтажу при виході з зони видимості, безпечну обробку помилок через `std::expected`, роботу зі шляхами через `std::filesystem` та відсутність ручного виділення пам'яті.

:::tabs
```c
/* launcher.c — Мінімальний лаунчер пакунка мовою C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sched.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <errno.h>

#define TARGET_MOUNT_POINT "/tmp/mini_bundle_target"

static int setup_environment(const char *bundle_dir) {
    char new_ld_path[4096];
    char new_bin_path[4096];
    const char *old_ld = getenv("LD_LIBRARY_PATH");
    const char *old_path = getenv("PATH");

    /* Формуємо новий LD_LIBRARY_PATH із пріоритетом усередині пакунка */
    if (old_ld && strlen(old_ld) > 0) {
        snprintf(new_ld_path, sizeof(new_ld_path), "%s/usr/lib:%s", bundle_dir, old_ld);
    } else {
        snprintf(new_ld_path, sizeof(new_ld_path), "%s/usr/lib", bundle_dir);
    }

    if (setenv("LD_LIBRARY_PATH", new_ld_path, 1) != 0) {
        perror("[ERROR] Не вдалося встановити LD_LIBRARY_PATH");
        return -1;
    }

    /* Формуємо новий PATH */
    if (old_path && strlen(old_path) > 0) {
        snprintf(new_bin_path, sizeof(new_bin_path), "%s/usr/bin:%s", bundle_dir, old_path);
    } else {
        snprintf(new_bin_path, sizeof(new_bin_path), "%s/usr/bin", bundle_dir);
    }

    if (setenv("PATH", new_bin_path, 1) != 0) {
        perror("[ERROR] Не вдалося встановити PATH");
        return -1;
    }

    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_каталогу_бандла> [аргументи...]\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *bundle_source = argv[1];

    /* Крок 1: Створення приватної копиї простору імен монтажу */
    if (unshare(CLONE_NEWNS) != 0) {
        perror("[ERROR] unshare(CLONE_NEWNS) не вдався (потрібні привілеї CAP_SYS_ADMIN)");
        return EXIT_FAILURE;
    }

    /* Крок 2: Переведення дерева монтажу в режим MS_PRIVATE */
    if (mount(NULL, "/", NULL, MS_PRIVATE | MS_REC, NULL) != 0) {
        perror("[ERROR] Не вдалося змінити режим поширення монтажу на MS_PRIVATE");
        return EXIT_FAILURE;
    }

    /* Крок 3: Створення точки призначення */
    if (mkdir(TARGET_MOUNT_POINT, 0755) != 0 && errno != EEXIST) {
        perror("[ERROR] Не вдалося створити точку монтажу");
        return EXIT_FAILURE;
    }

    /* Крок 4: Виконання bind-mount джерела пакунка в точку призначення */
    if (mount(bundle_source, TARGET_MOUNT_POINT, NULL, MS_BIND | MS_REC, NULL) != 0) {
        perror("[ERROR] bind-mount не вдався");
        return EXIT_FAILURE;
    }

    /* Крок 5: Налаштування змінних середовища */
    if (setup_environment(TARGET_MOUNT_POINT) != 0) {
        return EXIT_FAILURE;
    }

    /* Крок 6: Підготовка аргументів для виконання цільової програми */
    char target_binary[4096];
    snprintf(target_binary, sizeof(target_binary), "%s/usr/bin/app_main", TARGET_MOUNT_POINT);

    char **exec_args = calloc(argc, sizeof(char *));
    if (!exec_args) {
        perror("[ERROR] Помилка виділення пам'яті");
        return EXIT_FAILURE;
    }

    exec_args[0] = target_binary;
    for (int i = 2; i < argc; ++i) {
        exec_args[i - 1] = argv[i];
    }
    exec_args[argc - 1] = NULL;

    printf("[LAUNCHER] Запуск %s всередині ізольованого Mount Namespace...\n", target_binary);

    /* Заміщення образу процесу */
    execv(target_binary, exec_args);

    /* Якщо execv повернув керування — сталася помилка */
    perror("[ERROR] execv не вдався");
    free(exec_args);
    return EXIT_FAILURE;
}
```
```cpp
// launcher.cpp — Ідіоматичний лаунчер пакунка мовою C++20
#include <iostream>
#include <string>
#include <vector>
#include <filesystem>
#include <expected>
#include <system_error>
#include <cstdlib>
#include <cerrno>
#include <unistd.h>
#include <sched.h>
#include <sys/mount.h>
#include <sys/stat.h>

namespace fs = std::filesystem;

// RAII-обгортка для гарантованого прибирання точок монтажу та тимчасових тек
class ScopedMountGuard {
public:
    explicit ScopedMountGuard(fs::path mount_point)
        : mount_point_(std::move(mount_point)), is_mounted_(false) {}

    ~ScopedMountGuard() {
        if (is_mounted_) {
            // Демонтування у режимі MNT_DETACH (lazy unmount)
            umount2(mount_point_.c_str(), MNT_DETACH);
        }
        std::error_code ec;
        fs::remove(mount_point_, ec);
    }

    void mark_mounted() noexcept { is_mounted_ = true; }

    // Заборона копіювання
    ScopedMountGuard(const ScopedMountGuard&) = delete;
    ScopedMountGuard& operator=(const ScopedMountGuard&) = delete;

private:
    fs::path mount_point_;
    bool is_mounted_;
};

enum class LauncherError {
    InsufficientArguments,
    NamespaceCreationFailed,
    MountPropagationFailed,
    DirectoryCreationFailed,
    BindMountFailed,
    EnvironmentSetupFailed,
    ExecutionFailed
};

std::string error_to_string(LauncherError err) {
    switch (err) {
        case LauncherError::InsufficientArguments: return "Недостатньо аргументів командного рядка.";
        case LauncherError::NamespaceCreationFailed: return "Помилка створення Mount Namespace (потрібні привілеї або unprivileged user namespace).";
        case LauncherError::MountPropagationFailed: return "Не вдалося перевести точки монтажу в MS_PRIVATE.";
        case LauncherError::DirectoryCreationFailed: return "Не вдалося створити каталог для точки монтажу.";
        case LauncherError::BindMountFailed: return "Не вдалося виконати bind-mount джерела пакунка.";
        case LauncherError::EnvironmentSetupFailed: return "Не вдалося оновити змінні середовища.";
        case LauncherError::ExecutionFailed: return "Системний виклик execv завершився з помилкою.";
    }
    return "Невідома помилка.";
}

class BundleLauncher {
public:
    static std::expected<void, LauncherError> run(const fs::path& bundle_source, const std::vector<std::string>& user_args) {
        // Крок 1: Ізоляція простору імен монтажу
        if (unshare(CLONE_NEWNS) != 0) {
            return std::unexpected(LauncherError::NamespaceCreationFailed);
        }

        // Крок 2: Режим MS_PRIVATE для унеможливлення витоків у хост-систему
        if (mount(nullptr, "/", nullptr, MS_PRIVATE | MS_REC, nullptr) != 0) {
            return std::unexpected(LauncherError::MountPropagationFailed);
        }

        const fs::path target_mount = "/tmp/cpp_bundle_target";
        ScopedMountGuard guard(target_mount);

        std::error_code ec;
        fs::create_directories(target_mount, ec);
        if (ec) {
            return std::unexpected(LauncherError::DirectoryCreationFailed);
        }

        // Крок 3: Виконання bind-mount
        if (mount(bundle_source.c_str(), target_mount.c_str(), nullptr, MS_BIND | MS_REC, nullptr) != 0) {
            return std::unexpected(LauncherError::BindMountFailed);
        }
        guard.mark_mounted();

        // Крок 4: Налаштування змінних оточення
        if (!setup_env(target_mount)) {
            return std::unexpected(LauncherError::EnvironmentSetupFailed);
        }

        // Крок 5: Підготовка масиву аргументів
        const fs::path binary_path = target_mount / "usr" / "bin" / "app_main";
        std::vector<char*> raw_args;
        raw_args.reserve(user_args.size() + 2);

        // Буфери для змагання з розпадом покажчиків C-style рядків
        std::string bin_str = binary_path.string();
        raw_args.push_back(bin_str.data());

        std::vector<std::string> arg_buffers = user_args;
        for (auto& arg : arg_buffers) {
            raw_args.push_back(arg.data());
        }
        raw_args.push_back(nullptr);

        std::cout << "[CPP-LAUNCHER] Запуск бінарника " << binary_path << " у пісочниці..." << std::endl;

        execv(binary_path.c_str(), raw_args.data());

        // Якщо execv повернув керування — це помилка
        return std::unexpected(LauncherError::ExecutionFailed);
    }

private:
    static bool setup_env(const fs::path& mount_root) {
        const fs::path lib_dir = mount_root / "usr" / "lib";
        const fs::path bin_dir = mount_root / "usr" / "bin";

        const char* current_ld = std::getenv("LD_LIBRARY_PATH");
        std::string new_ld = lib_dir.string() + (current_ld ? ":" + std::string(current_ld) : "");
        if (setenv("LD_LIBRARY_PATH", new_ld.c_str(), 1) != 0) return false;

        const char* current_path = std::getenv("PATH");
        std::string new_path = bin_dir.string() + (current_path ? ":" + std::string(current_path) : "");
        if (setenv("PATH", new_path.c_str(), 1) != 0) return false;

        return true;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <шлях_до_каталогу_бандла> [аргументи...]" << std::endl;
        return EXIT_FAILURE;
    }

    fs::path bundle_path = argv[1];
    std::vector<std::string> user_args;
    for (int i = 2; i < argc; ++i) {
        user_args.emplace_back(argv[i]);
    }

    auto result = BundleLauncher::run(bundle_path, user_args);
    if (!result) {
        std::cerr << "[ERROR] Помилка запуску: " << error_to_string(result.error())
                  << " (errno: " << strerror(errno) << ")" << std::endl;
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

## Ключові відмінності C та C++ реалізацій

1. **Управління ресурсами та RAII:** У версії C++ клас `ScopedMountGuard` гарантує очищення тимчасової точки монтажу при виході з зони видимості (наприклад, якщо один із проміжних кроків завершився з помилкою до виклику `execv`). У версії C розробник змушений вручну викликати очищення у кожній гілці помилок.
2. **Безпека обробки помилок:** Замість повернення від'ємних кодування чисел та обробки глобального `errno`, C++ версія повертає об'єкт `std::expected<void, LauncherError>`, що робить недотримання перевірки результату помилкою компіляції під час збірки.
3. **Робота зі шляхами:** Модуль `std::filesystem` у C++20 ізолює платформозалежну конкатенацію шляхів та перевірку існування файлів, захищаючи від переповнення буфера, властивого `snprintf()` у C.
