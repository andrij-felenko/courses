# ⚙️ Реалізація трасувальника та перехоплювача системних викликів

Цей практичний проект присвячений розробці двох повнофункціональних системних утиліт моніторингу та перехоплення системних викликів у ядрі Linux. Перша утиліта реалізує інструмент налагодження на основі системного виклику `ptrace()`, здатний перехоплювати сигнали зупинки `sys_enter` та `sys_exit`, зчитувати значення фізичних регістрів процесора та витягувати аргументи викликів. Друга утиліта будується на сучасній асинхронній архітектурі `seccomp user notification` (`SECCOMP_RET_USER_NOTIF`), створюючи супервізор пісочниці, який перехоплює системний виклик створення каталогу (`mkdirat`), аналізує запит у просторі користувача та емулює його виконання без залучення ядерної файлової системи VFS.

Обидва приклади спроєктовано у двох вимірах: на мові C (стандарт POSIX C11 для демонстрації низькорівневої системної взаємодії з ABI ядра) та на мові C++ (стандарт C++20 із застосуванням концепцій RAII для автоматичного управління ресурсами, розумними обгортками для файлових дескрипторів та обробкою помилок через винятки `std::system_error`).

---

## Частина 1: Трасувальник системних викликів на базі ptrace

### Архітектурний аналіз та послідовність дій трасувальника

Робота трасувальника системних викликів спирається на чітку послідовність міжпроцесної взаємодії (IPC) між двома процесами — батьківським процесом-трасувальником (Tracer) та дочірнім трасованим процесом (Tracee). Під час виконання системного виклику ядро Linux здійснює послідовну зміну контекстів виконання:

1. **Створення процесу та оголошення трасування**: Батьківський процес викликає `fork()`. Дочірній процес у гілці `child` виконує системний виклик `ptrace(PTRACE_TRACEME, 0, NULL, NULL)`. Цей виклик ставить прапорець у структурі `task_struct` ядра, що повідомляє про дозвіл на перехоплення сигналів батьківським процесом.
2. **Синхронізація старту та заміна образу**: Негайно після `PTRACE_TRACEME` дочірній процес надсилає собі сигнал `raise(SIGSTOP)` і занурюється у сон. Це необхідно для того, щоб виконати зупинку **до** заміни образу процесу викликом `execvp()`. Завдяки цьому батько дістає змогу налаштувати опції трасування до того, як нова програма почне виконувати свій код.
3. **Налаштування опцій трасування**: Батьківський процес чекає на зупинку дочки через `waitpid(child_pid, &status, 0)`. Отримавши підтвердження, батько виконує `ptrace(PTRACE_SETOPTIONS, child_pid, 0, PTRACE_O_TRACESYSGOOD | PTRACE_O_EXITKILL)`. Прапорець `PTRACE_O_TRACESYSGOOD` налаштовує ядро встановлювати 7-й біт у статусі сигналу зупинки (`SIGTRAP | 0x80`), що дозволяє трасувальнику однозначно відрізнити зупинку на системному виклику від звичайних сигналів процесу. Прапорець `PTRACE_O_EXITKILL` гарантує, що при загибелі трасувальника дочірній процес буде примусово завершено ядром.
4. **Головний цикл відстеження входів та виходів**: Батьківський процес викликає `ptrace(PTRACE_SYSCALL, child_pid, 0, 0)` і заблоковується у `waitpid()`. Ядро відновлює виконання дочірнього процесу. Коли дочірній процес виконує інструкцію `syscall` (точка `sys_enter`), ядро зупиняє його і передає сигнал батькові. Батько через `ptrace(PTRACE_GETREGS, ...)` зчитує регістри (`orig_rax` — номер виклику, `rdi`, `rsi`, `rdx` — аргументи). Батько викликає `PTRACE_SYSCALL` вдруге, ядро виконує виклик, і на точці `sys_exit` ядро знову зупиняє процес, дозволяючи зчитати код повернення з регістру `rax`.

### Аналіз крайових випадків у ptrace

Під час розробки виробничих трасувальників слід враховувати кілька важливих крайових випадків:
- **Багатониткові застосунки**: Якщо трасований процес створює нові нитки виконання через `clone()`, трасувальник мусить встановити опцію `PTRACE_O_TRACECLONE`. При створенні нової нитки ядро зупиняє її та відправляє сповіщення `PTRACE_EVENT_CLONE`. Трасувальник повинен зберігати PID усіх активних ниток у динамічній таблиці й обробляти події від кожної з них окремо.
- **Обробка сигналів переривання (`EINTR`)**: Під час очікування у системному виклику `waitpid()` трасувальник може бути перерваний зовнішнім сигналом. У цьому випадку `waitpid()` повертає `-1` із `errno == EINTR`. Трасувальник повинен обробляти цю ситуацію в циклі та продовжувати очікування.
- **Аварійне завершення цільового процесу**: Якщо цільовий процес генерує помилку доступу до пам'яті (Memory Access Violation, `SIGSEGV`) або ділення на нуль (`SIGFPE`), статус `waitpid()` повертає `WIFSIGNALED(status) == true`. Трасувальник повинен коректно звільнити всі виділені ресурси й завершити роботу.

### Вихідний код ptrace-трасувальника (C та C++)

:::tabs
```c
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/user.h>
#include <syscall.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

/* Виконання цільової програми у дочірньому процесі */
static void run_target_program(char **argv) {
    /* Дозволяємо батьківському процесу трасувати поточний процес */
    if (ptrace(PTRACE_TRACEME, 0, NULL, NULL) < 0) {
        perror("ptrace PTRACE_TRACEME");
        exit(EXIT_FAILURE);
    }
    
    /* Зупиняємо процес перед заміною образу */
    raise(SIGSTOP);
    
    /* Замінюємо образ процесу на обрану програму */
    execvp(argv[0], argv);
    perror("execvp");
    exit(EXIT_FAILURE);
}

/* Цикл обробки подій трасування у батьківському процесі */
static void run_tracer_loop(pid_t child_pid) {
    int status = 0;
    int is_sys_enter = 1;

    /* Чекаємо початкової зупинки дочірнього процесу після SIGSTOP */
    if (waitpid(child_pid, &status, 0) < 0) {
        perror("waitpid initial");
        return;
    }

    /* Встановлюємо прапорці ptrace */
    if (ptrace(PTRACE_SETOPTIONS, child_pid, 0, PTRACE_O_TRACESYSGOOD | PTRACE_O_EXITKILL) < 0) {
        perror("ptrace PTRACE_SETOPTIONS");
        return;
    }

    printf("[Tracer C] Трасування розпочато для PID: %d\n", child_pid);

    while (1) {
        /* Запускаємо процес до наступної точки системного виклику */
        if (ptrace(PTRACE_SYSCALL, child_pid, 0, 0) < 0) {
            perror("ptrace PTRACE_SYSCALL");
            break;
        }

        /* Чекаємо на зміну стану цільового процесу */
        if (waitpid(child_pid, &status, 0) < 0) {
            perror("waitpid loop");
            break;
        }

        /* Перевірка на нормальне або аварійне завершення */
        if (WIFEXITED(status)) {
            printf("[Tracer C] Процес нормалізовано завершився з кодом: %d\n", WEXITSTATUS(status));
            break;
        }
        if (WIFSIGNALED(status)) {
            printf("[Tracer C] Процес вбито сигналом: %d\n", WTERMSIG(status));
            break;
        }

        /* Ідентифікація точки системного виклику через TRACESYSGOOD (SIGTRAP | 0x80) */
        if (WIFSTOPPED(status) && WSTOPSIG(status) == (SIGTRAP | 0x80)) {
            struct user_regs_struct regs;
            if (ptrace(PTRACE_GETREGS, child_pid, 0, &regs) < 0) {
                perror("ptrace PTRACE_GETREGS");
                break;
            }

            if (is_sys_enter) {
                /* sys_enter: orig_rax = номер виклику, rdi, rsi, rdx = аргументи 1..3 */
                printf("[sys_enter] Syscall NR: %llu (Arg1: 0x%llx, Arg2: 0x%llx, Arg3: 0x%llx)\n",
                       (unsigned long long)regs.orig_rax,
                       (unsigned long long)regs.rdi,
                       (unsigned long long)regs.rsi,
                       (unsigned long long)regs.rdx);
                is_sys_enter = 0;
            } else {
                /* sys_exit: rax = код повернення ядра */
                printf("[sys_exit ] Syscall NR: %llu -> Return Code: %lld\n",
                       (unsigned long long)regs.orig_rax,
                       (long long)regs.rax);
                is_sys_enter = 1;
            }
        }
    }
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <програма> [аргументи...]\n", argv[0]);
        return EXIT_FAILURE;
    }

    pid_t child = fork();
    if (child < 0) {
        perror("fork");
        return EXIT_FAILURE;
    }

    if (child == 0) {
        run_target_program(&argv[1]);
    } else {
        run_tracer_loop(child);
    }

    return EXIT_SUCCESS;
}
```
```cpp
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/user.h>
#include <syscall.h>
#include <unistd.h>
#include <iostream>
#include <vector>
#include <string>
#include <system_error>
#include <cerrno>

/* Об'єктно-орієнтована реалізація C++ трасувальника */
class PtraceTracer {
public:
    explicit PtraceTracer(pid_t childPid) : pid_(childPid) {}

    void run() {
        int status = 0;
        if (waitpid(pid_, &status, 0) < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося виконати початковий waitpid");
        }

        // Налаштовуємо розширені опції трасування ptrace
        if (ptrace(PTRACE_SETOPTIONS, pid_, 0, PTRACE_O_TRACESYSGOOD | PTRACE_O_EXITKILL) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка встановлення PTRACE_SETOPTIONS");
        }

        std::cout << "[C++ Tracer] Моніторинг активовано для PID: " << pid_ << "\n";

        bool isEnter = true;
        while (true) {
            if (ptrace(PTRACE_SYSCALL, pid_, 0, 0) < 0) {
                if (errno == ESRCH) break; // Процес завершився
                throw std::system_error(errno, std::generic_category(), "PTRACE_SYSCALL failed");
            }

            if (waitpid(pid_, &status, 0) < 0) {
                break;
            }

            if (WIFEXITED(status)) {
                std::cout << "[C++ Tracer] Процес нормалізовано завершився з кодом: "
                          << WEXITSTATUS(status) << "\n";
                break;
            }
            if (WIFSIGNALED(status)) {
                std::cout << "[C++ Tracer] Процес вбито сигналом: "
                          << WTERMSIG(status) << "\n";
                break;
            }

            if (WIFSTOPPED(status) && WSTOPSIG(status) == (SIGTRAP | 0x80)) {
                user_regs_struct regs{};
                if (ptrace(PTRACE_GETREGS, pid_, 0, &regs) < 0) {
                    break;
                }

                if (isEnter) {
                    std::cout << "[sys_enter] Виклик #" << regs.orig_rax
                              << " (rdi: 0x" << std::hex << regs.rdi
                              << ", rsi: 0x" << regs.rsi << std::dec << ")\n";
                    isEnter = false;
                } else {
                    std::cout << "[sys_exit ] Виклик #" << regs.orig_rax
                              << " -> Результат: " << static_cast<long long>(regs.rax) << "\n";
                    isEnter = true;
                }
            }
        }
    }

private:
    pid_t pid_;
};

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <програма> [аргументи...]\n";
        return 1;
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return 1;
    }

    if (pid == 0) {
        if (ptrace(PTRACE_TRACEME, 0, nullptr, nullptr) < 0) {
            perror("PTRACE_TRACEME");
            _exit(1);
        }
        raise(SIGSTOP);
        execvp(argv[1], &argv[1]);
        perror("execvp");
        _exit(1);
    }

    try {
        PtraceTracer tracer(pid);
        tracer.run();
    } catch (const std::exception& e) {
        std::cerr << "Критична помилка трасувальника: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
```
:::

---

## Частина 2: Супервізор на Seccomp User Notification

### Принцип роботи та деталізація асинхронного супервізора

У другій частині проєкту розробляється асинхронний супервізор. Основна перевага Seccomp User Notification порівняно з `ptrace` полягає у селективності: ядро самостійно обробляє 99% безпечних системних викликів із нульовими накладними витратами, і лише обрані виклики (наприклад, створення файлів або мережеві запити) перехоплюються та передаються супервізору.

Послідовність реалізації супервізора:

1. **Компіляція cBPF інструкцій**: Цільовий процес конструює масив інструкцій `struct sock_filter`. Перша інструкція завантажує номер виклику `seccomp_data.nr` у базований акумулятор. Друга інструкція порівнює значення з константою `__NR_mkdirat`. При збігу повертається статус `SECCOMP_RET_USER_NOTIF`, інакше — `SECCOMP_RET_ALLOW`.
2. **Встановлення NO_NEW_PRIVS**: Перед завантаженням Seccomp-фільтра процес обов'язково викликає `prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)`. Це гарантує, що дочірні процеси не зможуть обійти Seccomp-ізоляцію за допомогою запуску бінарних файлів із прапорцем `setuid` (наприклад, `sudo`).
3. **Реєстрація слухача**: Процес викликає `seccomp(SECCOMP_SET_MODE_FILTER, SECCOMP_FILTER_FLAG_NEW_LISTENER, &prog)`. Ядро повертає файловий дескриптор `listener_fd`.
4. **Обробка запитів супервізором**: Супервізор викликає `ioctl(listener_fd, SECCOMP_IOCTL_NOTIF_RECV, &req)`. Отримавши структуру `req`, супервізор перевіряє її дійсність через `SECCOMP_IOCTL_NOTIF_ID_VALID`. Якщо ідентифікатор чинний, супервізор заповнює структуру `resp` (вказує `val = 0` та `error = 0`) і відправляє її назад через `SECCOMP_IOCTL_NOTIF_SEND`.

### Інспектування пам'яті цільового процесу без TOCTOU

Коли супервізор отримує сповіщення про виклик `mkdirat`, аргумент `args[1]` містить вказівник на рядок шляху у пам'яті цільового процесу. Щоб прочитати цей рядок без виникнення гонитви ниток (TOCTOU):
- Супервізор відкриває дескриптор `/proc/$PID/mem` за допомогою `open()`, або виконує виклик `process_vm_readv()`.
- Оскільки цільова нитка повністю зупинена ядром у стані очікування відповіді Seccomp, її віртуальний адресний простір залишається незмінним, що гарантує 100% безпеку перевірки шляху.

### Вихідний код Seccomp-супервізора (C та C++)

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <sys/prctl.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
#include <sys/wait.h>
#include <linux/seccomp.h>
#include <linux/filter.h>

/* Створення та завантаження Seccomp BPF фільтра */
static int install_seccomp_filter(void) {
    struct sock_filter filter[] = {
        /* 1. Завантажуємо номер системного виклику в акумулятор BPF */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, nr)),
        
        /* 2. Перевіряємо чи дорівнює номер виклику __NR_mkdirat */
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_mkdirat, 0, 1),
        
        /* 3. Повертаємо USER_NOTIF для перехоплення супервізором */
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_USER_NOTIF),
        
        /* 4. Дозволяємо всі інші системні виклики */
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    };
    
    struct sock_fprog prog = {
        .len = (unsigned short)(sizeof(filter) / sizeof(filter[0])),
        .filter = filter,
    };

    /* Забороняємо отримання нових привілеїв */
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) < 0) {
        perror("prctl(PR_SET_NO_NEW_PRIVS)");
        return -1;
    }

    /* Реєструємо фільтр та отримуємо listener_fd */
    return syscall(__NR_seccomp, SECCOMP_SET_MODE_FILTER, SECCOMP_FILTER_FLAG_NEW_LISTENER, &prog);
}

/* Робочий цикл супервізора Seccomp */
static void run_supervisor(int notify_fd) {
    struct seccomp_notif req = {0};
    struct seccomp_notif_resp resp = {0};

    printf("[Supervisor C] Слухач активовано на notify_fd=%d. Чекаємо подій...\n", notify_fd);

    while (1) {
        memset(&req, 0, sizeof(req));
        
        /* Читаємо сповіщення з черги ядра */
        if (ioctl(notify_fd, SECCOMP_IOCTL_NOTIF_RECV, &req) < 0) {
            if (errno == EINTR) continue;
            if (errno == ENOENT) break; // Усі трасовані процеси завершилися
            perror("ioctl(SECCOMP_IOCTL_NOTIF_RECV)");
            break;
        }

        printf("[Supervisor C] УСПІШНО ПЕРЕХОПЛЕНО mkdirat() від PID=%d (Syscall NR=%d)\n",
               req.pid, req.data.nr);

        /* Перевірка дійсності ID для захисту від TOCTOU */
        __u64 check_id = req.id;
        if (ioctl(notify_fd, SECCOMP_IOCTL_NOTIF_ID_VALID, &check_id) < 0) {
            printf("[Supervisor C] Запит id=%llu скасовано (процес перервано)\n",
                   (unsigned long long)req.id);
            continue;
        }

        /* Формуємо відповідь про симульований успіх */
        memset(&resp, 0, sizeof(resp));
        resp.id = req.id;
        resp.val = 0;      /* Симулюємо успішне виконання (повертаємо 0) */
        resp.error = 0;    /* Код помилки відсутній */
        resp.flags = 0;

        /* Надсилаємо відповідь ядру */
        if (ioctl(notify_fd, SECCOMP_IOCTL_NOTIF_SEND, &resp) < 0) {
            perror("ioctl(SECCOMP_IOCTL_NOTIF_SEND)");
            break;
        }
        
        printf("[Supervisor C] Надіслано симульований результат для req.id=%llu\n",
               (unsigned long long)req.id);
        break; // Завершуємо роботу після першого перехопленого виклику
    }
}

int main(void) {
    int notify_fd = install_seccomp_filter();
    if (notify_fd < 0) {
        fprintf(stderr, "Не вдалося встановити Seccomp-фільтр\n");
        return EXIT_FAILURE;
    }

    pid_t child = fork();
    if (child < 0) {
        perror("fork");
        close(notify_fd);
        return EXIT_FAILURE;
    }

    if (child == 0) {
        /* Дочірній процес викликає mkdir(), який перехоплюється супервізором */
        printf("[Target C] Спроба виконати mkdir('/tmp/virtual_c_dir', 0755)...\n");
        int res = mkdir("/tmp/virtual_c_dir", 0755);
        printf("[Target C] Результат mkdir: %d (errno: %d, status: %s)\n",
               res, errno, strerror(errno));
        close(notify_fd);
        return EXIT_SUCCESS;
    } else {
        run_supervisor(notify_fd);
        close(notify_fd);
        waitpid(child, NULL, 0);
    }

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <memory>
#include <vector>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/prctl.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
#include <sys/wait.h>
#include <linux/seccomp.h>
#include <linux/filter.h>

/* RAII обгортка для файлового дескриптора */
class UniqueFd {
public:
    explicit UniqueFd(int fd = -1) : fd_(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    UniqueFd& operator=(UniqueFd&& o) noexcept {
        if (this != &o) {
            reset();
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }

    void reset(int newFd = -1) {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = newFd;
    }

    [[nodiscard]] int get() const { return fd_; }
    [[nodiscard]] bool valid() const { return fd_ >= 0; }

private:
    int fd_;
};

/* Налаштування Seccomp фільтра у C++ style */
static UniqueFd setupSeccompFilter() {
    struct sock_filter filter[] = {
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, nr)),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_mkdirat, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_USER_NOTIF),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    };
    
    struct sock_fprog prog = {
        static_cast<unsigned short>(sizeof(filter) / sizeof(filter[0])),
        filter
    };

    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) < 0) {
        throw std::system_error(errno, std::generic_category(), "prctl PR_SET_NO_NEW_PRIVS failed");
    }

    int rawFd = static_cast<int>(syscall(__NR_seccomp, SECCOMP_SET_MODE_FILTER, SECCOMP_FILTER_FLAG_NEW_LISTENER, &prog));
    if (rawFd < 0) {
        throw std::system_error(errno, std::generic_category(), "seccomp syscall failed");
    }
    return UniqueFd(rawFd);
}

int main() {
    try {
        UniqueFd notifyFd = setupSeccompFilter();

        pid_t pid = fork();
        if (pid < 0) {
            perror("fork");
            return 1;
        }

        if (pid == 0) {
            std::cout << "[C++ Target] Викликаємо mkdir('/tmp/cpp_virtual_dir')...\n";
            int res = ::mkdir("/tmp/cpp_virtual_dir", 0755);
            std::cout << "[C++ Target] Результат виклику mkdir: " << res
                      << " (errno: " << errno << ")\n";
            return 0;
        }

        struct seccomp_notif req{};
        struct seccomp_notif_resp resp{};

        std::cout << "[C++ Supervisor] Очікування сповіщення від цільового процесу...\n";

        if (ioctl(notifyFd.get(), SECCOMP_IOCTL_NOTIF_RECV, &req) >= 0) {
            std::cout << "[C++ Supervisor] Перехоплено системний виклик #"
                      << req.data.nr << " від PID " << req.pid << "\n";

            resp.id = req.id;
            resp.val = 0;    // Успішне симульоване повернення
            resp.error = 0;
            resp.flags = 0;

            if (ioctl(notifyFd.get(), SECCOMP_IOCTL_NOTIF_SEND, &resp) < 0) {
                perror("ioctl SECCOMP_IOCTL_NOTIF_SEND");
            } else {
                std::cout << "[C++ Supervisor] Відповідь успішно надіслано в ядро.\n";
            }
        }

        waitpid(pid, nullptr, 0);

    } catch (const std::exception& e) {
        std::cerr << "Критична помилка супервізора: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
```
:::

---

## Інструкції зі збірки, запуску та верифікації

Для перевірки роботи створених програм необхідно виконати компіляцію в середовищі Linux з ядром версії 5.0 або вище.

```bash
# 1. Компіляція ptrace трасувальника
gcc -std=c11 -O2 -Wall proj_ptrace.c -o ptrace_tracer_c
g++ -std=c++20 -O2 -Wall proj_ptrace.cpp -o ptrace_tracer_cpp

# 2. Компіляція Seccomp супервізора
gcc -std=c11 -O2 -Wall proj_seccomp.c -o seccomp_supervisor_c
g++ -std=c++20 -O2 -Wall proj_seccomp.cpp -o seccomp_supervisor_cpp

# 3. Тестування ptrace на системній утиліті ls
./ptrace_tracer_c /bin/ls /tmp

# 4. Тестування Seccomp супервізора
./seccomp_supervisor_c
ls -ld /tmp/virtual_c_dir
```

Під час запуску `seccomp_supervisor_c` у консолі з'явиться вивід, що виклик `mkdir()` повернув код `0` (успіх). Однак наступна перевірка командою `ls -ld /tmp/virtual_c_dir` покаже, що каталог на диску **не існує**. Це наочно доводить, що системний виклик був повністю перехоплений у просторі користувача і емульований супервізором без звернення до файлової системи ядра.
