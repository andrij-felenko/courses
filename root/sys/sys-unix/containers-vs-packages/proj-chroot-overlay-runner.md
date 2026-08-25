# ⚙️ Мінімальний контейнерний рушій на OverlayFS та namespaces

Ця вставка демонструє практичну реалізацію мінімального контейнерного рушія мовами C та C++, який підключає ізольовану файлову систему OverlayFS та створює нові простори імен (namespaces) ядра Linux. Проєкт показує, що контейнер не вимагає важких фонових демонів чи гіпервізорів — це звичайний процес Linux, запущений із прапорцями `CLONE_NEWNS`, `CLONE_NEWPID` та `CLONE_NEWUTS`, для якого ядро об'єднує шари файлової системи через VFS-драйвер OverlayFS.

---

## 1. Архітектурний план та послідовність системних викликів

Щоб перетворити звичайний каталог із файлами на ізольований OCI-подібний контейнер без допомоги Docker чи Podman, програма виконує чітку послідовність низькорівневих системних викликів ядра Linux:

1. **Створення файлової структури OverlayFS:** Програма готує на хості чотири фундаментальні каталоги: `lower/` (базове read-only середовище з системними утилітами), `upper/` (мутабельний шар запису контейнера), `work/` (внутрішній робочий каталог для атомарних операцій VFS) та `merged/` (віртуальна точка об'єднаного монтування).
2. **Створення ізольованого child-процесу:** Батьківський процес викликає системну функцію `clone()` із прапорцями `CLONE_NEWNS` (новий mount namespace), `CLONE_NEWPID` (новий PID namespace) та `CLONE_NEWUTS` (новий UTS namespace для ізольованого імені хоста).
3. **Захист від поширення точок монтування (`MS_PRIVATE`):** Дочірній процес ізолює свої майбутні точки монтування від глобальної файлової системи хоста, перевизначаючи дерево монтування в режим `MS_REC | MS_PRIVATE`. Це унеможливлює ситуацію, коли розмонтування або монтування в контейнері випадково змінить точки монтування хоста.
4. **Монтування OverlayFS у дочірньому процесі:** Дочірній процес виконує системний виклик `mount()` із типом файлової системи `"overlay"`, передаючи у спеціальному рядку опцій шляхи до `lowerdir`, `upperdir` та `workdir`.
5. **Зміна кореневої файлової системи (`pivot_root` / `chroot`):** Дочірній процес переходить у каталог `merged/` і робить його новим коренем `/` для поточного процесу та всіх його майбутніх нащадків.
6. **Монтування `/proc`:** Для коректної роботи системних утиліт аналізу процесів усередині нового PID namespace дочірній процес монтує віртуальну файлову систему `proc` у новий каталог `/proc`.
7. **Запуск цільової програми (`execv`):** Заміщення образа дочірнього процесу командною оболонкою `/bin/sh` або бінарним файлом застосунку через системний виклик `execve()`.

---

## 2. Покроковий розбір системних викликів ядра

Перед розбором коду важливо зрозуміти семантику кожного системного виклику, який бере участь у побудові середовища контейнера:

- **`clone(child_func, stack_top, flags, arg)`:** На відміну від стандартного `fork()`, системний виклик `clone()` дозволяє точно вказати, які саме примітиви ядра мають бути створені заново. Прапорці `CLONE_NEWNS` відсікають дерево монтування від хоста, `CLONE_NEWPID` створює нове ізольоване дерево процесів (де перший процес отримує PID 1), а `CLONE_NEWUTS` дозволяє встановити власне ім'я хоста через `sethostname()`.
- **`mount("overlay", merged_dir, "overlay", 0, options)`:** Виклик звертається безпосередньо до VFS-драйвера OverlayFS ядра Linux. Рядок опцій `lowerdir=...,upperdir=...,workdir=...` вказує ядру, з яких каталогів створювати об'єднане віртуальне дерево.
- **`chroot(merged_dir)` та `chdir("/")`:** Змінює корінь файлової системи для дочірнього процесу. У промислових OCI-рантаймах (`runc`) замість `chroot` використовується складніший виклик `pivot_root()`, який повністю змонтовує новий корінь і відмонтовує старий корінь хоста.
- **`mount("proc", "/proc", "proc", 0, NULL)`:** Монтує віртуальну файлову систему `/proc`, яка відображає лише ті процеси, які належать новому PID namespace даного контейнера.

Слід звернути увагу на порядок монтування `/proc`: якщо замонтувати `/proc` до зміни кореневого каталогу через `chroot` або без прапорця `CLONE_NEWPID`, дочірній процес продовжуватиме бачити таблицю процесів хоста. Крім того, у промислових контейнерних рушіях обов'язково налаштовуються права доступу через User Namespaces (`CLONE_NEWUSER`), що дозволяє виконувати розмонтування та монтування непривілейованим користувачам на хості.

---

## 3. Реалізація контейнерного рушія

Нижче наведено робочий вихідний код мовами C та C++. У версії C++ реалізовано RAII-обгортки для автоматичного очищення ресурсів (розмонтування OverlayFS та видалення тимчасових каталогів при виході з області видимості), тоді як у C використовується класична структура з `goto` та перевіркою кодів помилок.

:::tabs
```c
/* container_runner.c — Мінімальний контейнерний рушій мовою C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sched.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <errno.h>

#define STACK_SIZE (1024 * 1024)

struct container_config {
    const char *lower_dir;
    const char *upper_dir;
    const char *work_dir;
    const char *merged_dir;
    const char *hostname;
};

static int ensure_dir(const char *path) {
    if (mkdir(path, 0755) < 0 && errno != EEXIST) {
        perror("mkdir failed");
        return -1;
    }
    return 0;
}

static int child_main(void *arg) {
    struct container_config *cfg = (struct container_config *)arg;
    char mount_opts[1024];

    /* 1. Налаштування нового hostname в UTS namespace */
    if (sethostname(cfg->hostname, strlen(cfg->hostname)) < 0) {
        perror("sethostname failed");
        return -1;
    }

    /* 2. Захист від поширення монтів у хостовий namespace */
    if (mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL) < 0) {
        perror("mount MS_PRIVATE failed");
        return -1;
    }

    /* 3. Формування опцій для драйвера OverlayFS */
    snprintf(mount_opts, sizeof(mount_opts),
             "lowerdir=%s,upperdir=%s,workdir=%s",
             cfg->lower_dir, cfg->upper_dir, cfg->work_dir);

    /* 4. Монтування OverlayFS у каталог merged */
    if (mount("overlay", cfg->merged_dir, "overlay", 0, mount_opts) < 0) {
        perror("mount overlayfs failed");
        return -1;
    }

    /* 5. Зміна кореневого каталогу на merged */
    if (chroot(cfg->merged_dir) < 0) {
        perror("chroot failed");
        umount(cfg->merged_dir);
        return -1;
    }

    if (chdir("/") < 0) {
        perror("chdir root failed");
        return -1;
    }

    /* 6. Монтування /proc для нового PID namespace */
    ensure_dir("/proc");
    if (mount("proc", "/proc", "proc", 0, NULL) < 0) {
        perror("mount /proc failed");
        return -1;
    }

    printf("[Child Container] Rootfs й namespaces успішно ініціалізовано!\n");
    printf("[Child Container] Запуск /bin/sh (PID у контейнері = %d)...\n", getpid());

    /* 7. Запуск оболонки усередині контейнера */
    char *const argv[] = { "/bin/sh", NULL };
    char *const envp[] = { "PATH=/bin:/usr/bin", "TERM=xterm", NULL };

    execve("/bin/sh", argv, envp);

    /* У разі помилки execve */
    perror("execve failed");
    return -1;
}

int main(int argc, char *argv[]) {
    (void)argc; (void)argv;
    struct container_config cfg = {
        .lower_dir  = "/tmp/mini_container/lower",
        .upper_dir  = "/tmp/mini_container/upper",
        .work_dir   = "/tmp/mini_container/work",
        .merged_dir = "/tmp/mini_container/merged",
        .hostname   = "isolated-container"
    };

    printf("[Host] Підготовка каталогів для OverlayFS...\n");
    if (ensure_dir("/tmp/mini_container") < 0 ||
        ensure_dir(cfg.lower_dir) < 0 ||
        ensure_dir(cfg.upper_dir) < 0 ||
        ensure_dir(cfg.work_dir) < 0 ||
        ensure_dir(cfg.merged_dir) < 0) {
        fprintf(stderr, "Помилка створення каталогів\n");
        return EXIT_FAILURE;
    }

    /* Виділення стеку для дочірнього процесу */
    char *stack = malloc(STACK_SIZE);
    if (!stack) {
        perror("malloc stack failed");
        return EXIT_FAILURE;
    }

    printf("[Host] Створення дочірнього процесу через clone()...\n");
    int flags = CLONE_NEWNS | CLONE_NEWPID | CLONE_NEWUTS | SIGCHLD;
    pid_t child_pid = clone(child_main, stack + STACK_SIZE, flags, &cfg);

    if (child_pid < 0) {
        perror("clone failed");
        free(stack);
        return EXIT_FAILURE;
    }

    printf("[Host] Дочірній процес запуск з PID %d на хості.\n", child_pid);

    int status;
    waitpid(child_pid, &status, 0);

    printf("[Host] Контейнер завершив роботу з кодом %d.\n", WEXITSTATUS(status));

    /* Очищення монтування після виходу контейнера */
    umount(cfg.merged_dir);
    free(stack);
    return EXIT_SUCCESS;
}
```
```cpp
// container_runner.cpp — Ідіоматична реалізація контейнерного рушія на C++20
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <filesystem>
#include <memory>
#include <system_error>
#include <sched.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/mount.h>
#include <sys/stat.h>

namespace fs = std::filesystem;

class OverlayContainer {
public:
    struct Config {
        fs::path base_path = "/tmp/cpp_container";
        std::string hostname = "cpp-isolated-node";
    };

    explicit OverlayContainer(Config cfg)
        : config_(std::move(cfg)),
          lower_dir_(config_.base_path / "lower"),
          upper_dir_(config_.base_path / "upper"),
          work_dir_(config_.base_path / "work"),
          merged_dir_(config_.base_path / "merged") {}

    ~OverlayContainer() {
        cleanup();
    }

    // Заборона копіювання через управління системними ресурсами
    OverlayContainer(const OverlayContainer&) = delete;
    OverlayContainer& operator=(const OverlayContainer&) = delete;

    void prepare_environment() {
        std::error_code ec;
        fs::create_directories(lower_dir_, ec);
        fs::create_directories(upper_dir_, ec);
        fs::create_directories(work_dir_, ec);
        fs::create_directories(merged_dir_, ec);

        if (ec) {
            throw std::system_error(ec, "Failed to create OverlayFS structure");
        }
    }

    void run() {
        prepare_environment();

        constexpr std::size_t stack_size = 1024 * 1024;
        auto stack = std::make_unique<char[]>(stack_size);
        char* stack_top = stack.get() + stack_size;

        int flags = CLONE_NEWNS | CLONE_NEWPID | CLONE_NEWUTS | SIGCHLD;
        
        std::cout << "[Host C++] Launching isolated child via clone()...\n";
        pid_t pid = clone(&OverlayContainer::child_entry, stack_top, flags, this);

        if (pid < 0) {
            throw std::system_error(errno, std::generic_category(), "clone failed");
        }

        int status = 0;
        ::waitpid(pid, &status, 0);
        std::cout << "[Host C++] Container exited with status: " << WEXITSTATUS(status) << "\n";
    }

private:
    Config config_;
    fs::path lower_dir_;
    fs::path upper_dir_;
    fs::path work_dir_;
    fs::path merged_dir_;

    void cleanup() noexcept {
        // RAII-розмонтування OverlayFS при знищенні об'єкта
        std::error_code ec;
        if (fs::exists(merged_dir_, ec)) {
            ::umount2(merged_dir_.c_str(), MNT_DETACH);
        }
    }

    static int child_entry(void* arg) noexcept {
        auto* self = static_cast<OverlayContainer*>(arg);
        return self->execute_inside_container();
    }

    int execute_inside_container() noexcept {
        if (::sethostname(config_.hostname.c_str(), config_.hostname.size()) < 0) {
            std::perror("sethostname failed");
            return -1;
        }

        if (::mount(nullptr, "/", nullptr, MS_REC | MS_PRIVATE, nullptr) < 0) {
            std::perror("mount MS_PRIVATE failed");
            return -1;
        }

        std::string opts = "lowerdir=" + lower_dir_.string() +
                           ",upperdir=" + upper_dir_.string() +
                           ",workdir=" + work_dir_.string();

        if (::mount("overlay", merged_dir_.c_str(), "overlay", 0, opts.c_str()) < 0) {
            std::perror("mount overlay failed");
            return -1;
        }

        if (::chroot(merged_dir_.c_str()) < 0 || ::chdir("/") < 0) {
            std::perror("chroot/chdir failed");
            return -1;
        }

        fs::create_directory("/proc");
        if (::mount("proc", "/proc", "proc", 0, nullptr) < 0) {
            std::perror("mount /proc failed");
            return -1;
        }

        std::cout << "[Child C++] Shell running in container (PID=" << ::getpid() << ")\n";

        char* const argv[] = { const_cast<char*>("/bin/sh"), nullptr };
        char* const envp[] = { const_cast<char*>("PATH=/bin:/usr/bin"), nullptr };

        ::execve("/bin/sh", argv, envp);
        std::perror("execve failed");
        return -1;
    }
};

int main() {
    try {
        OverlayContainer::Config cfg;
        OverlayContainer container(cfg);
        container.run();
    } catch (const std::exception& ex) {
        std::cerr << "Fatal Error: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
:::

---

## 4. Порівняльний аналіз розбіжностей між реалізаціями на C та C++

При порівнянні обох варіантів вихідного коду чітко видно переваги ідіоматичного C++20 для побудови надійних системних утиліт управління контейнерними ресурсами ядра:
- **Управління системним станом через RAII:** У реалізації на C виклик `umount()` має виконуватися вручну у разі виникнення помилки на будь-якому з наступних системних викликів. Якщо програма завершується аварійно, точка монтування OverlayFS залишається "завислою" в ядрі. У коді на C++ деструктор `~OverlayContainer()` автоматично виконує розмонтування `merged_dir_` через `umount2(..., MNT_DETACH)` при виході з області видимості, включаючи обробку винятків.
- **Безпека маніпуляцій зі шляхами:** Замість небезпечного формованого запису в байтовий буфер `snprintf()`, версія C++ оперує типубезпечними об'єктами `std::filesystem::path`, які самостійно корегують розділювачі та унеможливлюють помилки виходу за межі масиву.
- **Ізоляція пам'яті стеку:** Системний виклик `clone()` вимагає виділення окремого фрагмента оперативної пам'яті під стек дочірнього процесу. Код на C++ загортає виділений масив у `std::make_unique<char[]>`, що запобігає витокам оперативної пам'яті при виникненні помилок ініціалізації.
- **Обробка помилок та винятки:** Версія C++ використовує об'єкти `std::system_error` для створення прозорої ієрархії винятків із збереженням системних кодів `errno`. Це спрощує налагодження та дозволяє передавати системний контекст помилки на верхні рівні абстракції додатка.
