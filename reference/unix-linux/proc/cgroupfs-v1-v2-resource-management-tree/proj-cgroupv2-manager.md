# ⚙️ Практичне керування cgroup v2 з простору користувача

Цей проєкт демонструє програмну взаємодію з cgroup v2 з простору користувача: створення вузла, активацію контролерів, встановлення лімітів пам'яті та CPU, прив'язку процесів і обробку подій завершення.

## Принцип взаємодії з VFS-інтерфейсом cgroup v2

Керування ресурсами cgroup v2 реалізовано через стандартні файлові операції у файловій системі `kernfs`, змонтованій у `/sys/fs/cgroup`. Для програмного створення та налаштування групи обчислювальних задач програма у просторі користувача виконує п'ять послідовних кроків:

1. **Делегування контролерів через `cgroup.subtree_control`**: Батьківська cgroup надає дозвіл дочірнім вузлам оперувати конкретними підсистемами ресурсів (наприклад, `+cpu +memory +io`).
2. **Ініціалізація каталогу системним викликом `mkdir()`**: Створення нового каталогу у файловому дереві `/sys/fs/cgroup/` ініціалізує новий об'єкт `struct cgroup` у пам'яті ядра та генерує стандартний набір файлів керування.
3. **Конфігурація обмежень (`memory.max`, `cpu.max`)**: Запис текстових параметрів у відповідні псевдофайли встановлює абсолютні межі або ваги використання ресурсів.
4. **Прив'язка процесу у `cgroup.procs`**: Атомарне переміщення процесу та всіх його потоків виконання у створений вузол cgroup v2 шляхом запису ідентифікатора PID.
5. **Асинхронне відстеження подій у `cgroup.events`**: Очікування сповіщень `POLLPRI` через системні виклики `poll()` або `epoll()`.

## Реалізація менеджера cgroup v2 мовами C та C++

Нижче наведено робочі приклади програмного керування cgroup v2. C-реалізація демонструє низькорівневу роботу з файловими дескрипторами та перевірку кодів системних помилок POSIX. C++-реалізація показує ідіоматичний підхід: керування ресурсами через RAII, типізовані шляхи `std::filesystem::path` та обробку виняткових ситуацій.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <poll.h>
#include <errno.h>

/* Запис текстового значення у псевдофайл cgroupfs */
static int write_control_file(const char *path, const char *value) {
    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        return -1;
    }
    ssize_t len = (ssize_t)strlen(value);
    ssize_t written = write(fd, value, (size_t)len);
    close(fd);
    return (written == len) ? 0 : -1;
}

int main(void) {
    const char *cgroup_root = "/sys/fs/cgroup";
    const char *child_dir = "/sys/fs/cgroup/demo_workload";
    char path_buf[512];

    /* 1. Активація контролерів для дочірніх cgroups */
    snprintf(path_buf, sizeof(path_buf), "%s/cgroup.subtree_control", cgroup_root);
    if (write_control_file(path_buf, "+cpu +memory\n") < 0) {
        perror("Не вдалося увімкнути subtree_control (потрібні права root)");
        return EXIT_FAILURE;
    }

    /* 2. Створення нової cgroup через mkdir */
    if (mkdir(child_dir, 0755) < 0 && errno != EEXIST) {
        perror("Помилка створення каталогу cgroup");
        return EXIT_FAILURE;
    }

    /* 3. Встановлення ліміту пам'яті (512 МіБ = 536870912 байтів) */
    snprintf(path_buf, sizeof(path_buf), "%s/memory.max", child_dir);
    if (write_control_file(path_buf, "536870912\n") < 0) {
        perror("Не вдалося встановити memory.max");
        return EXIT_FAILURE;
    }

    /* 4. Встановлення ліміту CPU (квота 50 мс на період 100 мс = 0.5 ядра CPU) */
    snprintf(path_buf, sizeof(path_buf), "%s/cpu.max", child_dir);
    if (write_control_file(path_buf, "50000 100000\n") < 0) {
        perror("Не вдалося встановити cpu.max");
        return EXIT_FAILURE;
    }

    /* 5. Додавання поточного процесу у cgroup.procs */
    snprintf(path_buf, sizeof(path_buf), "%s/cgroup.procs", child_dir);
    char pid_str[32];
    snprintf(pid_str, sizeof(pid_str), "%d\n", getpid());
    if (write_control_file(path_buf, pid_str) < 0) {
        perror("Не вдалося додати PID у cgroup.procs");
        return EXIT_FAILURE;
    }

    printf("Процес C [PID %d] успішно додано до %s\n", getpid(), child_dir);

    /* 6. Очікування подій зміни стану cgroup через poll() */
    snprintf(path_buf, sizeof(path_buf), "%s/cgroup.events", child_dir);
    int ev_fd = open(path_buf, O_RDONLY);
    if (ev_fd >= 0) {
        struct pollfd pfd = { .fd = ev_fd, .events = POLLPRI | POLLERR, .revents = 0 };
        printf("Моніторинг cgroup.events (таймаут 1000 мс)...\n");
        poll(&pfd, 1, 1000);
        close(ev_fd);
    }

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <string_view>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <poll.h>

namespace fs = std::filesystem;

/* RAII-обгортка для безпечного управління файловими дескрипторами у C++ */
class ScopedFd {
public:
    explicit ScopedFd(int fd = -1) noexcept : fd_(fd) {}
    ~ScopedFd() { reset(); }

    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;

    ScopedFd(ScopedFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_;
};

class CgroupV2Manager {
public:
    explicit CgroupV2Manager(fs::path root_path = "/sys/fs/cgroup")
        : root_(std::move(root_path)) {}

    void enable_controllers(std::string_view controllers) const {
        write_control_file(root_ / "cgroup.subtree_control", controllers);
    }

    void create_cgroup(const fs::path& rel_path) const {
        fs::create_directories(root_ / rel_path);
    }

    void set_memory_max(const fs::path& rel_path, uint64_t bytes) const {
        write_control_file(root_ / rel_path / "memory.max", std::to_string(bytes));
    }

    void set_cpu_max(const fs::path& rel_path, uint64_t quota_us, uint64_t period_us) const {
        std::string val = std::to_string(quota_us) + " " + std::to_string(period_us);
        write_control_file(root_ / rel_path / "cpu.max", val);
    }

    void attach_process(const fs::path& rel_path, pid_t pid) const {
        write_control_file(root_ / rel_path / "cgroup.procs", std::to_string(pid));
    }

    void monitor_events(const fs::path& rel_path, int timeout_ms) const {
        fs::path events_path = root_ / rel_path / "cgroup.events";
        ScopedFd fd(::open(events_path.c_str(), O_RDONLY));
        if (!fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Помилка відкриття cgroup.events");
        }

        pollfd pfd{.fd = fd.get(), .events = POLLPRI | POLLERR, .revents = 0};
        int ret = ::poll(&pfd, 1, timeout_ms);
        if (ret < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка виконання poll()");
        }
    }

private:
    static void write_control_file(const fs::path& file_path, std::string_view value) {
        std::ofstream ofs(file_path);
        if (!ofs.is_open()) {
            throw std::runtime_error("Не вдалося відкрити файл керування: " + file_path.string());
        }
        ofs << value << "\n";
        if (!ofs.good()) {
            throw std::runtime_error("Помилка запису даних у файл: " + file_path.string());
        }
    }

    fs::path root_;
};

int main() {
    try {
        CgroupV2Manager mgr;
        const fs::path workload_dir = "cpp_workload";

        mgr.enable_controllers("+cpu +memory");
        mgr.create_cgroup(workload_dir);
        mgr.set_memory_max(workload_dir, 536870912); // 512 MiB
        mgr.set_cpu_max(workload_dir, 50000, 100000); // 50 ms на 100 ms = 0.5 ядра
        mgr.attach_process(workload_dir, ::getpid());

        std::cout << "Процес C++ [PID " << ::getpid() << "] успішно додано до cgroup v2\n";
        mgr.monitor_events(workload_dir, 1000);
    } catch (const std::exception& ex) {
        std::cerr << "Помилка керування cgroup v2: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
:::

## Крок за кроком: Аналіз виконання системних викликів

При запуску скомпільованого бінарного файлу менеджера cgroup v2 під інструментом трасування системних викликів `strace` можна спостерігати точну послідовність викликів ядра:

```
openat(AT_FDCWD, "/sys/fs/cgroup/cgroup.subtree_control", O_WRONLY) = 3
write(3, "+cpu +memory\n", 13)         = 13
close(3)                                = 0
mkdir("/sys/fs/cgroup/demo_workload", 0755) = 0
openat(AT_FDCWD, "/sys/fs/cgroup/demo_workload/memory.max", O_WRONLY) = 3
write(3, "536870912\n", 10)             = 10
close(3)                                = 0
openat(AT_FDCWD, "/sys/fs/cgroup/demo_workload/cpu.max", O_WRONLY) = 3
write(3, "50000 100000\n", 13)          = 13
close(3)                                = 0
openat(AT_FDCWD, "/sys/fs/cgroup/demo_workload/cgroup.procs", O_WRONLY) = 3
write(3, "4012\n", 5)                   = 5
close(3)                                = 0
openat(AT_FDCWD, "/sys/fs/cgroup/demo_workload/cgroup.events", O_RDONLY) = 3
poll([{fd=3, events=POLLPRI|POLLERR}], 1, 1000) = 0 (Timeout)
close(3)                                = 0
```

Як видно з трасування, взаємодія з cgroup v2 повністю зводиться до базових викликів `openat()`, `write()`, `close()` та `mkdir()`. Це підтверджує, що для управління ресурсами у Linux не використовуються спеціалізовані бінарні `ioctl()` розширення — увесь контроль спирається на прозорий текстовий інтерфейс VFS.

## Детальний парсинг подій та асинхронна обробка

Файл `cgroup.events` надає текстовий формат ключ-значення, де кожен рядок описує поточний стан прапорця. Для прочитання подій програма зчитує вміст файлу у буфер:

```
populated 1
frozen 0
```

Коли оновлюється поле `populated` (наприклад, останній процес у cgroup завершив виконання чи був перенесений в інший вузол), значення змінюється з `1` на `0`, і функція `kernfs_notify()` надсилає сповіщення `POLLPRI` усім процесам, які слухають цей дескриптор.

У багатопотокових демонах керування контейнерами (наприклад, у службі моніторингу процесів) для паралельного відстеження сотень cgroups доцільно використовувати системний виклик `epoll()` з прапорцем `EPOLLPRI` замість лінійного `poll()`. Це дозволяє обслуговувати тисячі віртуальних контейнерів з мінімальними накладними витратами процесорного часу.

## Перевірка готовності системи та резервні стратегії

Перед виконанням операцій створення cgroup v2 у продакшн-додатках рекомендується виконати перевірку точки монтування файлової системи за допомогою системного виклику `statfs()`:

1. Перевірка типу файлової системи через `statfs.f_type` (для cgroup v2 константа `CGROUP2_SUPER_MAGIC` дорівнює `0x63677270`).
2. Читання файлу `/proc/filesystems` для підтвердження підтримки ядра.
3. Якщо cgroup v2 не змонтовано у `/sys/fs/cgroup`, програма може повернутися до спрощених обмежень POSIX `setrlimit()` або занотувати попередження у системний журнал.

## Аналіз крайніх випадків та архітектурних нюансів

При практичній реалізації керування cgroup v2 у прикладних сервісах, фонових демонах та сучасних системах контейнеризації слід враховувати важливі особливості поведінки ядра Linux та правильну послідовність файлових операцій:

- **Привілеї доступу (CAP_SYS_ADMIN)**: Активація контролерів у `cgroup.subtree_control` та переміщення довільних PID вимагає прав суперкористувача або делегованих прав доступу через системний менеджер systemd (`systemd --user`). При відсутності необхідних привілеїв ядро повертає системну помилку `EPERM` або `EACCES`.
- **Безпривілейовані контейнери (Rootless Containers)**: Для роботи у безпривілейованому середовищі контейнерний рушій спирається на делегування піддерева cgroup v2 користувачеві від systemd під час ініціалізації сесії. Вузол у `/sys/fs/cgroup/user.slice/user-1000.slice/` отримує власника `UID 1000`, що дозволяє створювати дочірні cgroups без прав root.
- **Спроба порушення правила відсутності внутрішніх процесів**: Якщо спробувати записати `+cpu` у `cgroup.subtree_control` вузла, який вже містить процеси у своєму `cgroup.procs`, системний виклик `write()` поверне помилку `EBUSY`. Для уникнення цієї помилки перед активацією дочірніх контролерів необхідно перенести всі наявні процеси у відповідний листковий вузол.
- **Безпека видалення вузлів**: Видалення cgroup за допомогою системного виклику `rmdir()` можливе лише тоді, коли у вузлі не залишилося жодного активного процесу (метрика `populated` у `cgroup.events` дорівнює `0`). Якщо в cgroup є хоча б один PID, `rmdir()` поверне помилку `EBUSY`.
- **Атомарне знищення задач**: Для аварійного очищення cgroup замість послідовного надсилання сигналів `SIGKILL` по списку PIDs рекомендується записати `1` у файл `cgroup.kill`, що гарантує атомарне завершення усіх процесів без створення залишкових умов гонки (race conditions).
- **Обробка виняткових ситуацій у C++**: Реалізація `CgroupV2Manager` використовує клас `ScopedFd` для забезпечення гарантії закриття файлового дескриптора навіть при виникненні винятків `std::system_error` під час системного виклику `poll()`. Це гарантує відсутність витоків файлових дескрипторів у довготривалих системних сервісах.
- **Особливості роботи з файловими потоками**: Значення у псевдофайл cgroupfs слід записувати одним викликом `write()` — ядро розбирає кожен запис як цілісну команду, а не накопичує буфер між викликами. Саме тому `std::ofstream` тут вимагає обережності: потік вільний розрізати дані на кілька системних викликів, і помилку запису видно лише після `flush()`/закриття, а не одразу після `operator<<`. Завершальний `\n` ядро приймає й ігнорує (обов'язковим він не є), але робить запис однозначним і збігається з тим, що потім читається з файла.
