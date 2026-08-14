# ⚙️ Практична реалізація міні-трасувальника системних викликів

У цій практичній вставці ми побудуємо та детально розберемо сирцевий код навчального трасувальника системних викликів (робочого нативного аналога системної утиліти `strace`). Написана програма демонструє повний життєвий цикл керування цільовим процесом у Linux: створення дочірнього процесу за допомогою `fork()` та `execvp()`, перехоплення моментів входу й виходу з системних викликів через виклик `PTRACE_SYSCALL`, витягування регістрів процесора x86_64, розкодування їхніх параметрів, читання зашифрованих рядків з пам'яті трасованого процесу та форматований вивід системних подій у консоль.

---

## 1. Архітектурний задум та кроки алгоритму

Створення надійного трасувальника вимагає чіткого розділення обов'язків між двома основними процесами — контролером (tracer) та контрольованою ціллю (tracee).

### Послідовність дій та етапи виконання:

1. **Створення дочірнього процесу:** Головна програма викликає системний виклик `fork()`, розділяючи виконання на батьківський та дочірній процеси.
2. **Налаштування дочірнього процесу (Tracee):**
   - Дочірній процес інформує ядро операційної системи про дозвіл на трасування за допомогою виклику `ptrace(PTRACE_TRACEME, 0, NULL, NULL)`.
   - Дочірній процес негайно викликає `raise(SIGSTOP)`, зупиняючи власне виконання. Це дає батьківському процесу можливість перехопити контроль, зачекати зупинки та налаштувати розширені опції трасування до того, як буде виконано заміну образу коду.
   - Після відновлення виконання дочірній процес викликає `execvp()`, замінюючи свій простір пам'яті кодом цільової програми.
3. **Налаштування трасувальника (Tracer):**
   - Батьківський процес чекає першої зупинки дочірнього процесу за допомогою виклику `waitpid(child_pid, &status, 0)`.
   - Трасувальник встановлює опції `PTRACE_O_TRACESYSGOOD` та `PTRACE_O_TRACEEXEC` через системний виклик `PTRACE_SETOPTIONS`. Налаштування `PTRACE_O_TRACESYSGOOD` є критично важливим: воно змушує ядро маркувати зупинки на системних викликах сигналом `SIGTRAP | 0x80` (`0x85`), що знімає неоднозначність між входом у системний виклик та виконанні звичайного точки зупину (`int 3`).
4. **Головний цикл трасування (PTRACE_SYSCALL Loop):**
   - Tracer відновлює виконання дочірнього процесу до наступної межі системного виклику за допомогою `ptrace(PTRACE_SYSCALL, child_pid, 0, 0)` і блокується у `waitpid()`.
   - При отриманні сповіщення про зупинку трасувальник перевіряє стан процесу за допомогою макросів `WIFEXITED`, `WIFSIGNALED` та `WIFSTOPPED`.
   - Якщо зупинку викликано сигналом `SIGTRAP | 0x80`, tracer зчитує поточний стан регістрів процесора за допомогою `PTRACE_GETREGS`.
   - Трасувальник підтримує внутрішній прапорець `in_syscall`, який перемикається між зупинкою на вході (`Syscall Enter Stop`) та зупинкою на виході (`Syscall Exit Stop`).
   - На вході розкодовується номер системного виклику з псевдорегістра `orig_rax`, а також перші три аргументи з регістрів `rdi`, `rsi`, `rdx`.
   - На виході розкодовується повернуте значення з регістра `rax` (у разі помилки це від'ємне значення `-ERRNO`) і сформований рядок виводиться у консоль.

---

## 2. Повна реалізація мовами C та ідіоматичною C++20

Нижче наведено два паралельні варіанти реалізації. Версія мовою C++20 кодує трасований процес за допомогою RAII-обгортки `TracedProcess`, яка гарантує безпечне примусове припинення або від'єднання дочірнього процесу при виникненні винятків, а також використовує суворі типи з чітким розміром (`std::int64_t`) та безпечні формати виводу `std::cout`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/ptrace.h>
#include <sys/wait.h>
#include <sys/user.h>
#include <sys/types.h>
#include <errno.h>

/* Таблиця імен системних викликів x86_64 для форматованого виводу */
static const char *get_syscall_name(long syscall_nr) {
    switch (syscall_nr) {
        case 0:   return "read";
        case 1:   return "write";
        case 2:   return "open";
        case 3:   return "close";
        case 9:   return "mmap";
        case 10:  return "mprotect";
        case 11:  return "munmap";
        case 12:  return "brk";
        case 59:  return "execve";
        case 231: return "exit_group";
        default:  return "unknown_syscall";
    }
}

/* Функція для безпечного читання рядка з пам'яті tracee по 8 байт (слово) */
static void read_remote_string(pid_t child, unsigned long addr, char *buffer, size_t max_len) {
    size_t bytes_read = 0;
    while (bytes_read < max_len - 1) {
        errno = 0;
        long val = ptrace(PTRACE_PEEKDATA, child, (void*)(addr + bytes_read), NULL);
        if (val == -1 && errno != 0) {
            break;
        }
        char *p = (char *)&val;
        for (int i = 0; i < sizeof(long); ++i) {
            if (p[i] == '\0' || bytes_read >= max_len - 1) {
                buffer[bytes_read] = '\0';
                return;
            }
            buffer[bytes_read++] = p[i];
        }
    }
    buffer[bytes_read] = '\0';
}

static void run_target(char **argv) {
    /* Дозволяємо батьківському процесу трасувати поточний процес */
    if (ptrace(PTRACE_TRACEME, 0, NULL, NULL) < 0) {
        perror("ptrace(TRACEME) failed");
        exit(EXIT_FAILURE);
    }
    
    /* Призупиняємо виконання для налаштування опцій трасувальником */
    raise(SIGSTOP);
    
    /* Замінюємо простір пам'яті кодом цільової програми */
    execvp(argv[0], argv);
    perror("execvp failed");
    exit(EXIT_FAILURE);
}

static void run_tracer(pid_t child_pid) {
    int status;

    /* Чекаємо першої зупинки SIGSTOP від дочірнього процесу */
    if (waitpid(child_pid, &status, 0) < 0) {
        perror("waitpid initial failed");
        return;
    }

    if (!WIFSTOPPED(status)) {
        fprintf(stderr, "Tracee didn't stop properly\n");
        return;
    }

    /* Встановлюємо прапор PTRACE_O_TRACESYSGOOD для маркування syscalls */
    if (ptrace(PTRACE_SETOPTIONS, child_pid, 0, (void*)PTRACE_O_TRACESYSGOOD) < 0) {
        perror("ptrace(PTRACE_SETOPTIONS) failed");
        return;
    }

    int in_syscall = 0;
    long syscall_nr = -1;

    while (1) {
        /* Відновлюємо виконання до наступного системного виклику */
        if (ptrace(PTRACE_SYSCALL, child_pid, 0, 0) < 0) {
            perror("ptrace(SYSCALL) failed");
            break;
        }

        if (waitpid(child_pid, &status, 0) < 0) {
            perror("waitpid loop failed");
            break;
        }

        /* Перевіряємо, чи цільовий процес завершився нормально */
        if (WIFEXITED(status)) {
            printf("\n[Tracer] Tracee exited with code %d\n", WEXITSTATUS(status));
            break;
        }

        /* Перевіряємо, чи цільовий процес було вбито сигналом */
        if (WIFSIGNALED(status)) {
            printf("\n[Tracer] Tracee killed by signal %d\n", WTERMSIG(status));
            break;
        }

        /* Обробка стану ptrace-stop */
        if (WIFSTOPPED(status)) {
            int sig = WSTOPSIG(status);

            /* Перевіряємо, чи це зупинка на системному виклику (SIGTRAP | 0x80 = 0x85) */
            if (sig == (SIGTRAP | 0x80)) {
                struct user_regs_struct regs;
                if (ptrace(PTRACE_GETREGS, child_pid, 0, &regs) < 0) {
                    perror("ptrace(GETREGS) failed");
                    break;
                }

                if (!in_syscall) {
                    /* Точка входу в системний виклик (Syscall Enter Stop) */
                    in_syscall = 1;
                    syscall_nr = (long)regs.orig_rax;
                    
                    printf("[SYS_ENTER] %-12s (arg1=0x%-8llx, arg2=0x%-8llx, arg3=0x%-8llx)",
                           get_syscall_name(syscall_nr),
                           regs.rdi, regs.rsi, regs.rdx);

                    /* Якщо це системний виклик write(), читаємо переданий рядок */
                    if (syscall_nr == 1 && regs.rsi != 0) {
                        char str_buf[64];
                        read_remote_string(child_pid, regs.rsi, str_buf, sizeof(str_buf));
                        printf(" [buf=\"%s\"]", str_buf);
                    }
                    fflush(stdout);
                } else {
                    /* Точка виходу з системного виклику (Syscall Exit Stop) */
                    in_syscall = 0;
                    long res = (long)regs.rax;
                    printf(" = %ld\n", res);
                }
            } else {
                /* Якщо процес зупинився через звичайний апаратний сигнал */
                printf("\n[Tracer] Tracee received signal: %d\n", sig);
            }
        }
    }
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <program> [args...]\n", argv[0]);
        return EXIT_FAILURE;
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork failed");
        return EXIT_FAILURE;
    }

    if (pid == 0) {
        run_target(&argv[1]);
    } else {
        run_tracer(pid);
    }

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <system_error>
#include <memory>
#include <cstdint>
#include <iomanip>
#include <unistd.h>
#include <sys/ptrace.h>
#include <sys/wait.h>
#include <sys/user.h>

// Клас RAII для надійного управління життєвим циклом цільового процесу
class TracedProcess {
    pid_t pid_{-1};

public:
    explicit TracedProcess(pid_t pid) noexcept : pid_(pid) {}
    
    ~TracedProcess() {
        if (pid_ > 0) {
            int status = 0;
            if (::waitpid(pid_, &status, WNOHANG) == 0) {
                ::ptrace(PTRACE_KILL, pid_, nullptr, nullptr);
                ::waitpid(pid_, nullptr, 0);
            }
        }
    }

    TracedProcess(const TracedProcess&) = delete;
    TracedProcess& operator=(const TracedProcess&) = delete;
    TracedProcess(TracedProcess&& other) noexcept : pid_(other.pid_) { other.pid_ = -1; }
    TracedProcess& operator=(TracedProcess&& other) noexcept {
        if (this != &other) {
            pid_ = other.pid_;
            other.pid_ = -1;
        }
        return *this;
    }

    [[nodiscard]] pid_t get_pid() const noexcept { return pid_; }
};

class SyscallTracer {
    static constexpr std::string_view get_syscall_name(std::int64_t nr) noexcept {
        switch (nr) {
            case 0:   return "read";
            case 1:   return "write";
            case 2:   return "open";
            case 3:   return "close";
            case 9:   return "mmap";
            case 10:  return "mprotect";
            case 11:  return "munmap";
            case 12:  return "brk";
            case 59:  return "execve";
            case 231: return "exit_group";
            default:  return "unknown_syscall";
        }
    }

    static std::string read_remote_string(pid_t child, std::uint64_t addr, std::size_t max_len = 64) {
        std::string result;
        result.reserve(max_len);
        std::size_t bytes_read = 0;

        while (bytes_read < max_len) {
            errno = 0;
            const long val = ::ptrace(PTRACE_PEEKDATA, child, reinterpret_cast<void*>(addr + bytes_read), nullptr);
            if (val == -1 && errno != 0) {
                break;
            }
            const auto* p = reinterpret_cast<const char*>(&val);
            for (std::size_t i = 0; i < sizeof(long); ++i) {
                if (p[i] == '\0' || bytes_read >= max_len) {
                    return result;
                }
                result.push_back(p[i]);
                bytes_read++;
            }
        }
        return result;
    }

public:
    static void trace(pid_t child_pid) {
        TracedProcess process(child_pid);
        int status = 0;

        if (::waitpid(child_pid, &status, 0) < 0 || !WIFSTOPPED(status)) {
            throw std::system_error(errno, std::generic_category(), "Початкова зупинка tracee не вдалася");
        }

        if (::ptrace(PTRACE_SETOPTIONS, child_pid, nullptr, PTRACE_O_TRACESYSGOOD) < 0) {
            throw std::system_error(errno, std::generic_category(), "PTRACE_SETOPTIONS failed");
        }

        bool in_syscall = false;

        while (true) {
            if (::ptrace(PTRACE_SYSCALL, child_pid, nullptr, nullptr) < 0) {
                std::perror("PTRACE_SYSCALL failed");
                break;
            }

            if (::waitpid(child_pid, &status, 0) < 0) {
                break;
            }

            if (WIFEXITED(status)) {
                std::cout << "\n[Tracer] Процес завершився з кодом: " << WEXITSTATUS(status) << "\n";
                break;
            }

            if (WIFSIGNALED(status)) {
                std::cout << "\n[Tracer] Процес знищено сигналом: " << WTERMSIG(status) << "\n";
                break;
            }

            if (WIFSTOPPED(status)) {
                const int sig = WSTOPSIG(status);

                if (sig == (SIGTRAP | 0x80)) {
                    user_regs_struct regs{};
                    if (::ptrace(PTRACE_GETREGS, child_pid, nullptr, &regs) < 0) {
                        std::perror("PTRACE_GETREGS failed");
                        break;
                    }

                    if (!in_syscall) {
                        in_syscall = true;
                        const auto sys_nr = static_cast<std::int64_t>(regs.orig_rax);
                        std::cout << "[SYS_ENTER] " << std::left << std::setw(12) 
                                  << get_syscall_name(sys_nr)
                                  << " (arg1=0x" << std::hex << regs.rdi
                                  << ", arg2=0x" << regs.rsi
                                  << ", arg3=0x" << regs.rdx << std::dec << ")";

                        if (sys_nr == 1 && regs.rsi != 0) {
                            const auto str = read_remote_string(child_pid, regs.rsi);
                            std::cout << " [buf=\"" << str << "\"]";
                        }
                        std::cout.flush();
                    } else {
                        in_syscall = false;
                        const auto res = static_cast<std::int64_t>(regs.rax);
                        std::cout << " = " << res << "\n";
                    }
                } else {
                    std::cout << "\n[Tracer] Сигнал зупинки: " << sig << "\n";
                }
            }
        }
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <програма> [аргументи...]\n";
        return EXIT_FAILURE;
    }

    const pid_t pid = ::fork();
    if (pid < 0) {
        std::perror("fork failed");
        return EXIT_FAILURE;
    }

    if (pid == 0) {
        if (::ptrace(PTRACE_TRACEME, 0, nullptr, nullptr) < 0) {
            std::perror("PTRACE_TRACEME failed");
            std::_Exit(EXIT_FAILURE);
        }
        ::raise(SIGSTOP);
        ::execvp(argv[1], &argv[1]);
        std::perror("execvp failed");
        std::_Exit(EXIT_FAILURE);
    }

    try {
        SyscallTracer::trace(pid);
    } catch (const std::exception& ex) {
        std::cerr << "Помилка трасування: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

---

## 3. Детальний розбір системних інваріантів та крайових випадків

Під час розробки інструментів спостережуваності та трасування на базі `ptrace` виникає низка системних особливостей та потенційних пасток.

### 3.1. Різниця між регістрами orig_rax та rax

На архітектурі x86_64 під час входу в системний виклик (`Syscall Enter Stop`) регістр `rax` містить номер системного виклику. Проте ядро операційної системи негайно перезаписує `rax` значенням `-ENOSYS` (сигнал про те, що системний виклик ще знаходиться в процесі обробки). Якщо трасувальник спробує зчитати номер системного виклику з `rax` на вході, він завжди отримає число `-38` (`-ENOSYS`).

Оригінальний номер виклику зберігається у псевдорегістрі `orig_rax` структури `user_regs_struct`.

> ⚠️ **Критичний інваріант:** Зчитувати номер системного виклику на вході необхідно СТРОГО з регістра `orig_rax`. Читання з `rax` на вході дасть помилкове значення `-ENOSYS`.

### 3.2. Роль прапора PTRACE_O_TRACESYSGOOD

За замовчуванням будь-яка ptrace-зупинка повертає сигнал `SIGTRAP` (`5`). Оскільки апаратні точки зупину (інструкції `INT 3`) також надсилають `SIGTRAP`, трасувальник без `PTRACE_O_TRACESYSGOOD` не зможе відрізнити вхід у виклик `read()` від виконання breakpoint'а в коді програми.

Опція `PTRACE_O_TRACESYSGOOD` змушує ядро додавати біт `0x80` до сигналу зупинки на системному виклику, роблячи його `SIGTRAP | 0x80` (`0x85`). Перевірка `WSTOPSIG(status) == (SIGTRAP | 0x80)` гарантує, що трасувальник обробляє саме системний виклик.

### 3.3. Обробка багатопоточності (PTRACE_O_TRACECLONE)

Якщо цільова програма використовує декілька потоків виконання (POSIX Threads / `pthread_create`), нові потоки створюються за допомогою системного виклику `clone()` із прапорцями `CLONE_VM` та `CLONE_THREAD`.

За замовчуванням `ptrace` трасує тільки той конкретний потік (LWP), до якого він приєднався. Щоб автоматично підхоплювати нові потоки процесу, трасувальник повинен встановити опцію `PTRACE_O_TRACECLONE`:

:::tabs
```c
ptrace(PTRACE_SETOPTIONS, child_pid, 0, (void*)(PTRACE_O_TRACESYSGOOD | PTRACE_O_TRACECLONE));
```
```cpp
::ptrace(PTRACE_SETOPTIONS, child_pid, nullptr, reinterpret_cast<void*>(PTRACE_O_TRACESYSGOOD | PTRACE_O_TRACECLONE));
```
:::

При створенні нового потоку ядро згенерирує подію `PTRACE_EVENT_CLONE`. Трасувальник повинен викликати `ptrace(PTRACE_GETEVENTMSG, child_pid, NULL, &new_tid)`, щоб отримати PID/TID нового потоку, і включити його у свій цикл обробки `waitpid(-1, &status, 0)`.

### 3.4. Передача та придушення сигналів

Якщо трасований процес під час роботи отримує сигнал від операційної системи (наприклад, користувач натиснув `Ctrl+C` і надіслав `SIGINT`, або програма звернулася за невалідним вказівником і отримала `SIGSEGV`), ядро переходить у стан `Signal-delivery-stop` і сповіщає tracer через `waitpid()`.

Трасувальник отримує номер цього сигналу через `WSTOPSIG(status)`. Далі tracer повинен прийняти рішення:
- **Передати сигнал процесу:** При наступному виклику `ptrace(PTRACE_SYSCALL, pid, 0, (void*)(uintptr_t)sig)` трасувальник передає номер сигналу `sig` останнім параметром. Ядро доставить цей сигнал обробнику tracee.
- **Придушити сигнал:** Якщо tracer передає `0` в останньому параметрі `ptrace()`, ядро повністю придушує сигнал, і цільовий процес про нього ніколи не дізнається.
