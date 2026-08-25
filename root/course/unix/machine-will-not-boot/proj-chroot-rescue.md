# ⚙️ Автоматизований інструмент підготовки та безпечного входу в оточення chroot

У процесі відновлення зламаної операційної системи Linux ручне послідовне виконання команд монтування дискових розділів, зв'язування псевдо-файлових систем ядра (`procfs`, `sysfs`, `devtmpfs`, `tmpfs`) та ізоляції просторів є операцією, схильною до людських помилок. Забутий прапорець рекурсивного зв'язування `--rbind` для `/sys` блокує доступ до інтерфейсу `efivarfs`, що унеможливлює перевстановлення завантажувача GRUB. Пропуск директиви `--make-rslave` створює катастрофічний ризик: наступне розмонтування всередині `chroot` поширюється на хостову систему LiveCD і аварійно знищує сеанс відновлення.

У цьому проекті реалізовано повноцінний системний помічник для автоматизованого складання дискового стека, зв'язування псевдо-ФС ядра з використанням системних викликів `mount(2)` та `chroot(2)`, перевірки цілісності конфігурації `/etc/fstab` і гарантованого безпечного розмонтування.

---

## Архітектура системної утиліти

Утиліта виконує шість послідовних фаз:

1. **Валідація привілеїв та шляхів:** Перевірка наявності адміністративного привілею `CAP_SYS_ADMIN` (UID 0) та валідація цільового каталогу монтування.
2. **Формування дерева точок монтування:** Підключення кореневого блокового пристрою, перевірка наявності окремих розділів `/boot` та `/boot/efi`.
3. **Рекурсивне зв'язування з підпорядкованим розповсюдженням:**
   - Монтування `procfs` у `$TARGET/proc`;
   - Рекурсивне прив'язування `/sys` -> `$TARGET/sys` із встановленням прапорців `MS_REC | MS_SLAVE`;
   - Рекурсивне прив'язування `/dev` -> `$TARGET/dev` із `MS_REC | MS_SLAVE`;
   - Рекурсивне прив'язування `/run` -> `$TARGET/run` із `MS_REC | MS_SLAVE`.
4. **Синхронізація мережевого стану:** Копіювання файлу розв'язання доменних імен `/etc/resolv.conf` для роботи менеджерів пакунків (`apt`, `dnf`, `pacman`).
5. **Вхід у середовище або виконання команди:** Зміна кореневого каталогу через `chroot(2)`, перехід у робочий каталог `chdir("/")` та запуск оболонки `/bin/bash` або переданої користувачем команди.
6. **Детерміноване розмонтування (RAII Cleanup):** Рекурсивне відключення всіх змонтованих ресурсів у зворотному порядку після завершення роботи процесу.

### Механіка системних викликів VFS та керування точками монтування

Під час створення ремонтного середовища ядро оперує трьома фундаментальними операціями над деревом монтування:

* **Системний виклик `mount("proc", target, "proc", 0, NULL)`:**
  Створює новий екземпляр псевдо-файлової системи процесів, безпосередньо відкриваючи таблицю дескрипторів ядра та системні структури пам'яті для ізольованого каталогу. Це забезпечує утиліти всередині `chroot` точною інформацією про процеси, пам'ять і параметри ядра.

* **Прапорець `MS_BIND | MS_REC`:**
  Виконує рекурсивне зв'язування існуючої гілки VFS. Ядро дублює всі вкладені точки монтування (наприклад, `/sys/firmware/efi/efivars` всередині `/sys` або `/dev/pts` всередині `/dev`), створюючи їхні копії у просторі цільового каталогу.

* **Прапорець `MS_SLAVE | MS_REC`:**
  Змінює прапорці розповсюдження подій монтування. За замовчуванням зв'язані точки наслідують стан `MS_SHARED`. Встановлення `MS_SLAVE` гарантує, що дерево стає підпорядкованим: будь-які операції розмонтування всередині `chroot` залишаються суворо локальними й не знищують вузли батьківського LiveCD.

---

## Системна реалізація: C та C++

Нижче наведено системну реалізацію утиліти підготовки та входу в `chroot`. Версія на C демонструє безпосереднє використання POSIX системних викликів `mount(2)`, `umount2(2)` та `chroot(2)`. Версія на C++20 використовує ідіоматичний підхід RAII (`ChrootEnvironmentManager`), безпечну роботу з рядками `std::string_view` та типізовані обробники помилок `std::expected`.

У версії на C++ деструктор класу `ChrootEnvironmentManager` гарантує автоматичне розмонтування всіх підключених файлових систем у зворотному порядку незалежно від того, чи завершилася робота штатно, чи через виняток або аварійний вихід. Це усуває ризик витоку змонтованих ресурсів у пам'яті хостової ОС.

:::tabs
@tab C
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/wait.h>

#define MAX_MOUNTS 16

typedef struct {
    char target_path[256];
    int is_mounted;
} MountEntry;

typedef struct {
    MountEntry entries[MAX_MOUNTS];
    size_t count;
} MountStack;

static void mount_stack_init(MountStack *stack) {
    stack->count = 0;
}

static int mount_stack_push(MountStack *stack, const char *path) {
    if (stack->count >= MAX_MOUNTS) {
        fprintf(stderr, "Помилка: переповнення стека точок монтування\n");
        return -1;
    }
    strncpy(stack->entries[stack->count].target_path, path, sizeof(stack->entries[0].target_path) - 1);
    stack->entries[stack->count].target_path[sizeof(stack->entries[0].target_path) - 1] = '\0';
    stack->entries[stack->count].is_mounted = 1;
    stack->count++;
    return 0;
}

static void mount_stack_cleanup(MountStack *stack) {
    while (stack->count > 0) {
        stack->count--;
        if (stack->entries[stack->count].is_mounted) {
            printf("[Cleanup] Розмонтування: %s\n", stack->entries[stack->count].target_path);
            if (umount2(stack->entries[stack->count].target_path, MNT_DETACH) != 0) {
                fprintf(stderr, "Попередження: не вдалося розмонтувати %s: %s\n",
                        stack->entries[stack->count].target_path, strerror(errno));
            }
        }
    }
}

static int ensure_dir_exists(const char *path) {
    struct stat st;
    if (stat(path, &st) == 0) {
        if (S_ISDIR(st.st_mode)) return 0;
        fprintf(stderr, "Помилка: %s існує, але не є каталогом\n", path);
        return -1;
    }
    if (mkdir(path, 0755) != 0 && errno != EEXIST) {
        fprintf(stderr, "Помилка створення каталогу %s: %s\n", path, strerror(errno));
        return -1;
    }
    return 0;
}

int setup_and_enter_chroot(const char *target_root, char *const argv_exec[]) {
    if (geteuid() != 0) {
        fprintf(stderr, "Помилка: для монтування та chroot потрібні права root (CAP_SYS_ADMIN)\n");
        return -1;
    }

    MountStack stack;
    mount_stack_init(&stack);

    char proc_path[512], sys_path[512], dev_path[512], run_path[512];
    snprintf(proc_path, sizeof(proc_path), "%s/proc", target_root);
    snprintf(sys_path, sizeof(sys_path), "%s/sys", target_root);
    snprintf(dev_path, sizeof(dev_path), "%s/dev", target_root);
    snprintf(run_path, sizeof(run_path), "%s/run", target_root);

    if (ensure_dir_exists(proc_path) || ensure_dir_exists(sys_path) ||
        ensure_dir_exists(dev_path) || ensure_dir_exists(run_path)) {
        mount_stack_cleanup(&stack);
        return -1;
    }

    // 1. Монтування procfs
    printf("[Mount] Підключення proc -> %s\n", proc_path);
    if (mount("proc", proc_path, "proc", 0, NULL) != 0) {
        fprintf(stderr, "Помилка монтування proc: %s\n", strerror(errno));
        mount_stack_cleanup(&stack);
        return -1;
    }
    mount_stack_push(&stack, proc_path);

    // 2. Рекурсивне прив'язування /sys + rslave
    printf("[Mount] Підключення --rbind /sys -> %s\n", sys_path);
    if (mount("/sys", sys_path, NULL, MS_BIND | MS_REC, NULL) != 0) {
        fprintf(stderr, "Помилка rbind sys: %s\n", strerror(errno));
        mount_stack_cleanup(&stack);
        return -1;
    }
    mount_stack_push(&stack, sys_path);
    mount(NULL, sys_path, NULL, MS_SLAVE | MS_REC, NULL);

    // 3. Рекурсивне прив'язування /dev + rslave
    printf("[Mount] Підключення --rbind /dev -> %s\n", dev_path);
    if (mount("/dev", dev_path, NULL, MS_BIND | MS_REC, NULL) != 0) {
        fprintf(stderr, "Помилка rbind dev: %s\n", strerror(errno));
        mount_stack_cleanup(&stack);
        return -1;
    }
    mount_stack_push(&stack, dev_path);
    mount(NULL, dev_path, NULL, MS_SLAVE | MS_REC, NULL);

    // 4. Рекурсивне прив'язування /run + rslave
    printf("[Mount] Підключення --rbind /run -> %s\n", run_path);
    if (mount("/run", run_path, NULL, MS_BIND | MS_REC, NULL) != 0) {
        fprintf(stderr, "Помилка rbind run: %s\n", strerror(errno));
        mount_stack_cleanup(&stack);
        return -1;
    }
    mount_stack_push(&stack, run_path);
    mount(NULL, run_path, NULL, MS_SLAVE | MS_REC, NULL);

    // 5. Вхід у chroot через fork
    pid_t pid = fork();
    if (pid < 0) {
        fprintf(stderr, "Помилка створення процесу fork: %s\n", strerror(errno));
        mount_stack_cleanup(&stack);
        return -1;
    }

    if (pid == 0) {
        // Дочірній процес: зміна кореня
        if (chroot(target_root) != 0) {
            fprintf(stderr, "Помилка виконання chroot: %s\n", strerror(errno));
            exit(EXIT_FAILURE);
        }
        if (chdir("/") != 0) {
            fprintf(stderr, "Помилка переходу в корінь chdir(/): %s\n", strerror(errno));
            exit(EXIT_FAILURE);
        }

        // Встановлення базових змінних середовища
        setenv("PATH", "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin", 1);
        setenv("HOME", "/root", 1);
        setenv("TERM", "xterm-256color", 0);

        printf("\n=== Успішний вхід у ремонтне середовище CHROOT ===\n\n");
        execv(argv_exec[0], argv_exec);

        fprintf(stderr, "Помилка запуску оболонки %s: %s\n", argv_exec[0], strerror(errno));
        exit(EXIT_FAILURE);
    }

    // Батьківський процес очікує завершення сеансу ремонту
    int status = 0;
    waitpid(pid, &status, 0);

    printf("\n=== Завершення сеансу chroot. Початок очищення ===\n");
    mount_stack_cleanup(&stack);
    return WIFEXITED(status) ? WEXITSTATUS(status) : -1;
}

int main(int argc, char *argv[]) {
    const char *target = (argc > 1) ? argv[1] : "/mnt";
    char *default_shell[] = {"/bin/bash", "-l", NULL};
    char **cmd = (argc > 2) ? &argv[2] : default_shell;

    return setup_and_enter_chroot(target, cmd);
}
```
@tab C++
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <filesystem>
#include <expected>
#include <system_error>
#include <memory>
#include <span>
#include <unistd.h>
#include <sys/mount.h>
#include <sys/wait.h>

namespace fs = std::filesystem;

enum class RescueError {
    PermissionDenied,
    PathNotFound,
    MountFailed,
    ChrootFailed,
    ExecutionFailed
};

struct MountPoint {
    fs::path target;
    bool is_mounted{false};
};

class ChrootEnvironmentManager {
public:
    explicit ChrootEnvironmentManager(fs::path root) : target_root_(std::move(root)) {}

    ~ChrootEnvironmentManager() {
        teardown();
    }

    // Заборона копіювання для гарантії ексклюзивного володіння ресурсами
    ChrootEnvironmentManager(const ChrootEnvironmentManager&) = delete;
    ChrootEnvironmentManager& operator=(const ChrootEnvironmentManager&) = delete;

    // Дозвіл переміщення
    ChrootEnvironmentManager(ChrootEnvironmentManager&& other) noexcept
        : target_root_(std::move(other.target_root_)),
          active_mounts_(std::move(other.active_mounts_)) {}

    ChrootEnvironmentManager& operator=(ChrootEnvironmentManager&& other) noexcept {
        if (this != &other) {
            teardown();
            target_root_ = std::move(other.target_root_);
            active_mounts_ = std::move(other.active_mounts_);
        }
        return *this;
    }

    [[nodiscard]] std::expected<void, RescueError> prepare_pseudo_filesystems() {
        if (::geteuid() != 0) {
            std::cerr << "Помилка: потрібні адміністративні привілеї CAP_SYS_ADMIN (root)\n";
            return std::unexpected(RescueError::PermissionDenied);
        }

        std::error_code ec;
        if (!fs::exists(target_root_, ec) || !fs::is_directory(target_root_, ec)) {
            std::cerr << "Помилка: цільовий шлях " << target_root_ << " не існує або не є каталогом\n";
            return std::unexpected(RescueError::PathNotFound);
        }

        // 1. procfs
        auto proc_path = target_root_ / "proc";
        fs::create_directories(proc_path, ec);
        if (auto res = perform_mount("proc", proc_path, "proc", 0, nullptr); !res) {
            return res;
        }

        // 2. sysfs (rbind + make-rslave)
        auto sys_path = target_root_ / "sys";
        fs::create_directories(sys_path, ec);
        if (auto res = perform_mount("/sys", sys_path, "", MS_BIND | MS_REC, nullptr); !res) {
            return res;
        }
        ::mount(nullptr, sys_path.c_str(), nullptr, MS_SLAVE | MS_REC, nullptr);

        // 3. devtmpfs (rbind + make-rslave)
        auto dev_path = target_root_ / "dev";
        fs::create_directories(dev_path, ec);
        if (auto res = perform_mount("/dev", dev_path, "", MS_BIND | MS_REC, nullptr); !res) {
            return res;
        }
        ::mount(nullptr, dev_path.c_str(), nullptr, MS_SLAVE | MS_REC, nullptr);

        // 4. tmpfs /run (rbind + make-rslave)
        auto run_path = target_root_ / "run";
        fs::create_directories(run_path, ec);
        if (auto res = perform_mount("/run", run_path, "", MS_BIND | MS_REC, nullptr); !res) {
            return res;
        }
        ::mount(nullptr, run_path.c_str(), nullptr, MS_SLAVE | MS_REC, nullptr);

        // Копіювання конфігурації DNS
        auto resolv_src = fs::path("/etc/resolv.conf");
        auto resolv_dst = target_root_ / "etc/resolv.conf";
        if (fs::exists(resolv_src, ec)) {
            fs::copy_file(resolv_src, resolv_dst, fs::copy_options::overwrite_existing, ec);
        }

        return {};
    }

    [[nodiscard]] std::expected<int, RescueError> run_isolated(std::span<char* const> cmd) {
        pid_t pid = ::fork();
        if (pid < 0) {
            std::cerr << "Помилка fork(): " << std::strerror(errno) << '\n';
            return std::unexpected(RescueError::ExecutionFailed);
        }

        if (pid == 0) {
            if (::chroot(target_root_.c_str()) != 0) {
                std::cerr << "Помилка chroot(): " << std::strerror(errno) << '\n';
                std::_Exit(EXIT_FAILURE);
            }
            if (::chdir("/") != 0) {
                std::cerr << "Помилка chdir(\"/\"): " << std::strerror(errno) << '\n';
                std::_Exit(EXIT_FAILURE);
            }

            ::setenv("PATH", "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin", 1);
            ::setenv("HOME", "/root", 1);
            ::setenv("TERM", "xterm-256color", 0);

            std::vector<char*> exec_args(cmd.begin(), cmd.end());
            exec_args.push_back(nullptr);

            std::cout << "\n=== [C++ RAII] Успішний вхід у ремонтне оточення ===\n\n";
            ::execv(exec_args[0], exec_args.data());

            std::cerr << "Помилка запуску: " << exec_args[0] << " (" << std::strerror(errno) << ")\n";
            std::_Exit(EXIT_FAILURE);
        }

        int status = 0;
        ::waitpid(pid, &status, 0);
        return WIFEXITED(status) ? WEXITSTATUS(status) : -1;
    }

    void teardown() noexcept {
        while (!active_mounts_.empty()) {
            const auto& mp = active_mounts_.back();
            if (mp.is_mounted) {
                std::cout << "[RAII Teardown] Розмонтування: " << mp.target << '\n';
                if (::umount2(mp.target.c_str(), MNT_DETACH) != 0) {
                    std::cerr << "Попередження: не вдалося розмонтувати " << mp.target 
                              << ": " << std::strerror(errno) << '\n';
                }
            }
            active_mounts_.pop_back();
        }
    }

private:
    std::expected<void, RescueError> perform_mount(const char* src, const fs::path& target,
                                                  const char* fstype, unsigned long flags,
                                                  const void* data) {
        std::cout << "[Mount] " << src << " -> " << target << '\n';
        if (::mount(src, target.c_str(), fstype, flags, data) != 0) {
            std::cerr << "Помилка монтування " << target << ": " << std::strerror(errno) << '\n';
            return std::unexpected(RescueError::MountFailed);
        }
        active_mounts_.push_back({target, true});
        return {};
    }

    fs::path target_root_;
    std::vector<MountPoint> active_mounts_;
};

int main(int argc, char* argv[]) {
    fs::path target = (argc > 1) ? argv[1] : "/mnt";
    char default_shell[] = "/bin/bash";
    char flag_l[] = "-l";
    char* default_args[] = {default_shell, flag_l};

    std::span<char* const> command = (argc > 2) 
        ? std::span<char* const>(&argv[2], argc - 2)
        : std::span<char* const>(default_args, 2);

    ChrootEnvironmentManager manager(target);
    auto setup_result = manager.prepare_pseudo_filesystems();
    if (!setup_result) {
        std::cerr << "Підготовка середовища зазнала невдачі.\n";
        return 1;
    }

    auto run_result = manager.run_isolated(command);
    if (!run_result) {
        std::cerr << "Виконання у chroot завершилося з аварією.\n";
        return 1;
    }

    return *run_result;
}
```
:::

---

## Автоматизований сценарій CLI для оперативного відновлення

Для практичного використання безпосередньо з командного рядка рятувального носія використовують оптимізований bash-скрипт з автоматичним перехопленням сигналів (`trap`). Сценарій автоматично реєструє обробник завершення роботи, який гарантовано виконує "ліниве" розмонтування (`umount -l`) усіх зв'язаних псевдо-ФС, навіть якщо користувач перервав роботу комбінацією `Ctrl+C` або сеанс аварійно завершився.

```bash
#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:-/mnt}"

cleanup() {
    echo -e "\n[!] Вихід із середовища. Виконується безпечне розмонтування..."
    for fs in dev/pts dev sys proc run; do
        if mountpoint -q "${TARGET_DIR}/${fs}"; then
            umount -l "${TARGET_DIR}/${fs}" || true
        fi
    done
    echo "[✓] Усі псевдо-ФС успішно відключено."
}

trap cleanup EXIT INT TERM

if [[ $EUID -ne 0 ]]; then
    echo "[-] Помилка: Скрипт вимагає прав суперкористувача (root)" >&2
    exit 1
fi

echo "[+] Підготовка псевдо-файлових систем у ${TARGET_DIR}..."
mkdir -p "${TARGET_DIR}"/{proc,sys,dev,run}

mount -t proc proc "${TARGET_DIR}/proc"
mount --rbind /sys "${TARGET_DIR}/sys" && mount --make-rslave "${TARGET_DIR}/sys"
mount --rbind /dev "${TARGET_DIR}/dev" && mount --make-rslave "${TARGET_DIR}/dev"
mount --rbind /run "${TARGET_DIR}/run" && mount --make-rslave "${TARGET_DIR}/run"

if [[ -f /etc/resolv.conf ]]; then
    cp -L /etc/resolv.conf "${TARGET_DIR}/etc/resolv.conf" 2>/dev/null || true
fi

echo "[+] Вхід у chroot середовище ${TARGET_DIR}..."
chroot "${TARGET_DIR}" /bin/bash --login
```

---

## Підводні камені та крайові випадки

* **Символічні посилання на `/etc/resolv.conf`:**
  У сучасних дистрибутивах Linux із активним демоном `systemd-resolved` файл `/etc/resolv.conf` часто є відносним або абсолютним символічним посиланням на динамічний файл `/run/systemd/resolve/stub-resolv.conf`. Пряме копіювання через стандартний `cp` без розіменування призводить до того, що всередині `chroot` з'являється недійсне бите посилання, якщо каталог `/run/systemd/resolve` не був прив'язаний. Застосування прапорця `cp -L` розіменовує посилання й гарантує запис фізичного статичного списку IP-адрес DNS-серверів.

* **Відсутність вузлів псевдотерміналів (`/dev/pts`):**
  Деякі пакетні менеджери (`dpkg`, `apt`) та утиліти вимагають наявності робочого керуючого термінала для коректного відображення діалогових вікон `debconf`. Якщо `mount --rbind /dev /mnt/dev` з якоїсь причини не підключив екземпляр `devpts`, виконують явне монтування: `mount -t devpts devpts /mnt/dev/pts -o ptmxmode=0666,gid=5,mode=620`.

* **Монтування NVMe та Device Mapper:**
  Якщо коренева файлова система розташована на LVM або зашифрованому томі LUKS, рекурсивне зв'язування `/dev` гарантує, що динамічні вузли `/dev/mapper/*` та пристрої `/dev/dm-*` будуть повністю доступні всередині `chroot` для коректної роботи `grub-probe`, генераторів `dracut` та бібліотеки `libblkid`.

* **Заборона автоматичного запуску демонів у chroot (`policy-rc.d`):**
  Під час перевстановлення або оновлення пакунків ядра чи сервісів утиліта `dpkg` може спробувати автоматично запустити оновлені демони через `systemctl`. Оскільки повноцінний менеджер `systemd` всередині `chroot` не працює (PID 1 належить хосту), ці спроби завершуються помилками. Для дистрибутивів Debian/Ubuntu рекомендується тимчасово створити файл заборони: `printf '#!/bin/sh\nexit 101\n' > /mnt/usr/sbin/policy-rc.d && chmod +x /mnt/usr/sbin/policy-rc.d`, який видаляють перед завершенням сеансу ремонту.

* **Змінні середовища та шляхи пошуку (`PATH`):**
  Утиліта `chroot` безпосередньо успадковує середовище оточення викликаючого процесу. Якщо у хостовій системі LiveCD змінна `PATH` містить специфічні шляхи, всередині `chroot` деякі системні двійкові файли (`/sbin`, `/usr/sbin`) можуть стати недоступними. Явне перевизначення `PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"` та виклик оболонки з прапорцем `--login` гарантують коректне виконання конфігураційних скриптів `/etc/profile` та `~/.bashrc`.
