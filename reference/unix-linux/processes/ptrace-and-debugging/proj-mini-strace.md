# ⚙️ Практична реалізація трасувальника системних викликів

У цій проектній вставці подано повну робочу реалізацію двох версій мініатюрного трасувальника системних викликів (спрощеного аналога інструменту `strace`), побудованого на базі системного виклику `ptrace(2)`. Перша версія реалізована ідіоматичною мовою C, а друга — сучасним стандартом C++20 з використанням типу `std::expected` та концепції RAII.

## Архітектура та принцип роботи

Трасування системних викликів вимагає чіткої синхронізації між двома процесами: трасувальником (батьківським процесом) та трасованим об'єктом (дочірнім процесом).

Основні етапи виконання трасувальника:

1. **Створення процесу:** Головний процес викликає `fork()`. 
2. **Налаштування дочірнього процесу:** У дочірньому процесі перед завантаженням нового бінарного файлу виконується системний виклик `ptrace(PTRACE_TRACEME, 0, NULL, NULL)`. Після цього викликається `execvp()` для завантаження цільової програми.
3. **Первинна зупинка:** Ядро автоматично зупиняє дочірній процес сигналом `SIGTRAP` перед виконанням найпершої інструкції у точці входу.
4. **Конфігурація опцій:** Батьківський процес чекає на зупинку через `waitpid()`, після чого встановлює розширений прапорець `PTRACE_O_TRACESYSGOOD` за допомогою запиту `PTRACE_SETOPTIONS`.
5. **Цикл трасування:** Батьківський процес відновлює виконання дочірнього через `ptrace(PTRACE_SYSCALL, pid, NULL, NULL)`. Ядро перехоплює дві точки у кожному системному виклику:
   - **Syscall Entry (Вхід):** Зупинка перед виконанням. Трасувальник зчитує номер виклику з регістра `orig_rax` (на x86_64) та перші три аргументи з регістрів `rdi`, `rsi`, `rdx`.
   - **Syscall Exit (Вихід):** Зупинка після виконання. Трасувальник зчитує код повернення з регістра `rax`.

:::tabs
=== C
```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/user.h>

static void run_target(char *const argv[]) {
    if (ptrace(PTRACE_TRACEME, 0, NULL, NULL) < 0) {
        perror("ptrace TRACEME failed");
        exit(EXIT_FAILURE);
    }
    execvp(argv[0], argv);
    perror("execvp failed");
    exit(EXIT_FAILURE);
}

static void run_tracer(pid_t child_pid) {
    int status;
    int is_syscall_entry = 1;

    waitpid(child_pid, &status, 0);

    /* Встановлюємо прапорець PTRACE_O_TRACESYSGOOD */
    if (ptrace(PTRACE_SETOPTIONS, child_pid, 0, PTRACE_O_TRACESYSGOOD) < 0) {
        perror("ptrace SETOPTIONS failed");
        exit(EXIT_FAILURE);
    }

    while (1) {
        if (ptrace(PTRACE_SYSCALL, child_pid, 0, 0) < 0) {
            perror("ptrace SYSCALL failed");
            break;
        }

        waitpid(child_pid, &status, 0);

        if (WIFEXITED(status) || WIFSIGNALED(status)) {
            printf("[Процес %d завершився]\n", child_pid);
            break;
        }

        if (WIFSTOPPED(status) && WSTOPSIG(status) == (SIGTRAP | 0x80)) {
            struct user_regs_struct regs;
            if (ptrace(PTRACE_GETREGS, child_pid, 0, &regs) < 0) {
                perror("ptrace GETREGS failed");
                break;
            }

            if (is_syscall_entry) {
                printf("[SYSCALL Entry] № %llu (arg1: 0x%llx, arg2: 0x%llx, arg3: 0x%llx)\n",
                       regs.orig_rax, regs.rdi, regs.rsi, regs.rdx);
                is_syscall_entry = 0;
            } else {
                printf("[SYSCALL Exit ] № %llu -> Result: %lld\n",
                       regs.orig_rax, (long long)regs.rax);
                is_syscall_entry = 1;
            }
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <програма_для_запуску> [аргументи...]\n", argv[0]);
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
=== C++
```cpp
#include <iostream>
#include <vector>
#include <string_view>
#include <system_error>
#include <expected>
#include <unistd.h>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/user.h>

class TraceeProcess {
    pid_t pid_{-1};

public:
    explicit TraceeProcess(pid_t pid) : pid_(pid) {}
    
    ~TraceeProcess() {
        if (pid_ > 0) {
            int status;
            ptrace(PTRACE_DETACH, pid_, nullptr, nullptr);
            waitpid(pid_, &status, WNOHANG);
        }
    }

    TraceeProcess(const TraceeProcess&) = delete;
    TraceeProcess& operator=(const TraceeProcess&) = delete;

    TraceeProcess(TraceeProcess&& other) noexcept : pid_(other.pid_) {
        other.pid_ = -1;
    }

    TraceeProcess& operator=(TraceeProcess&& other) noexcept {
        if (this != &other) {
            pid_ = other.pid_;
            other.pid_ = -1;
        }
        return *this;
    }

    [[nodiscard]] pid_t pid() const noexcept { return pid_; }
};

class SyscallTracer {
public:
    static std::expected<void, std::string_view> run(char* const argv[]) {
        pid_t pid = fork();
        if (pid < 0) {
            return std::unexpected("Не вдалося виконати fork()");
        }

        if (pid == 0) {
            if (ptrace(PTRACE_TRACEME, 0, nullptr, nullptr) < 0) {
                std::perror("PTRACE_TRACEME failed");
                std::_Exit(EXIT_FAILURE);
            }
            execvp(argv[0], argv);
            std::perror("execvp failed");
            std::_Exit(EXIT_FAILURE);
        }

        TraceeProcess tracee(pid);
        int status = 0;
        waitpid(tracee.pid(), &status, 0);

        if (ptrace(PTRACE_SETOPTIONS, tracee.pid(), 0, PTRACE_O_TRACESYSGOOD) < 0) {
            return std::unexpected("Помилка при встановленні PTRACE_O_TRACESYSGOOD");
        }

        bool is_entry = true;

        while (true) {
            if (ptrace(PTRACE_SYSCALL, tracee.pid(), 0, 0) < 0) {
                break;
            }

            waitpid(tracee.pid(), &status, 0);

            if (WIFEXITED(status) || WIFSIGNALED(status)) {
                std::cout << "[Процес " << tracee.pid() << " завершив роботу]\n";
                break;
            }

            if (WIFSTOPPED(status) && WSTOPSIG(status) == (SIGTRAP | 0x80)) {
                struct user_regs_struct regs{};
                if (ptrace(PTRACE_GETREGS, tracee.pid(), 0, &regs) < 0) {
                    return std::unexpected("Помилка зчитування регістрів через PTRACE_GETREGS");
                }

                if (is_entry) {
                    std::cout << "[SYSCALL Entry] № " << regs.orig_rax 
                              << " (rdi: 0x" << std::hex << regs.rdi 
                              << ", rsi: 0x" << regs.rsi 
                              << ", rdx: 0x" << regs.rdx << std::dec << ")\n";
                    is_entry = false;
                } else {
                    std::cout << "[SYSCALL Exit ] № " << regs.orig_rax 
                              << " -> Код повернення: " << static_cast<long long>(regs.rax) << "\n";
                    is_entry = true;
                }
            }
        }
        return {};
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <програма_для_запуску> [аргументи...]\n";
        return EXIT_FAILURE;
    }

    auto result = SyscallTracer::run(&argv[1]);
    if (!result) {
        std::cerr << "Помилка: " << result.error() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

## Ключові особливості реалізації та підводні камені

Під час побудови власного інструменту трасування на базі `ptrace` необхідно враховувати кілька важливих системних нюансів:

1. **Необхідність прапорця `PTRACE_O_TRACESYSGOOD`:** Без активації цієї опції ядро надсилає стандартний сигнал `SIGTRAP` при кожній зупинці системного виклику. Якщо цільова програма сама використовує точки зупину або інструкцію `int 3`, трасувальник не зможе відрізнити справжній системний виклик від апаратного переривання коду. Прапорець `PTRACE_O_TRACESYSGOOD` примушує ядро встановлювати 7-й біт сигналу (`SIGTRAP | 0x80`), роблячи код сигналу рівним `0x85`.

2. **Зберігання початкового номера виклику:** В архітектурі x86_64 під час входу в системний виклик ядро зберігає початковий номер виклику в регістрі `orig_rax`. Під час виконання виклику регістр `rax` перезаписується кодом повернення. Якщо ви прочитаєте `rax` на етапі входу, ви отримаєте номер виклику, але на етапі виходу `rax` буде містити статус (наприклад, кількість прочитаних байтів). Тому для ідентифікації системного виклику завжди використовується регістр `orig_rax`.

3. **Роз синхронізація входу й виходу при сигналах:** Якщо цільовий процес отримує асинхронний сигнал (наприклад, `SIGALRM` або `SIGINT`) у той самий момент, коли він намагається зробити системний виклик, ядро може спочатку призупинити процес для обробки сигналу. У результаті прапорець `is_syscall_entry` у спрощеному циклі може збитися. Професійні інструменти (на кшталт `strace`) відстежують стан кожного системного виклику за допомогою таблиці станів кожної нитки й перевірки значення `orig_rax`.

4. **Очищення ресурсів при завершенні (RAII):** У версії на C++ клас `TraceeProcess` реалізує концепцію RAII. Якщо процес-трасувальник завершується достроково або викидає виняток, деструктор `TraceeProcess` автоматично надсилає `PTRACE_DETACH`, щоб цільовий процес не залишився назавжди в заблокованому стані `TASK_TRACED`.

5. **Відображення текстових рядків та шляхів файлів:** При перехопленні системного виклику `openat` або `execve` регістр `rdi` або `rsi` містить не самий рядок, а віртуальну адресу вказівника на рядок у пам'яті цільового процесу. Щоб вивести шлях до файла у консоль, трасувальник мусить додатково зчитати байти з цієї адреси за допомогою `PTRACE_PEEKDATA` або `process_vm_readv` до першого нульового термінатора `\0`.

6. **Опрацювання багатонитковості (`CLONE_THREAD`):** Якщо цільова програма створює нові нитки за допомогою `pthread_create()`, трасувальник мусить увімкнути опцію `PTRACE_O_TRACECLONE` і викликати `waitpid(-1, &status, __WALL)` у циклі для перехоплення системних викликів усіх активних ниток процесу.

7. **Портативність між архітектурами:** Структура регістрів `user_regs_struct` відрізняється залежно від апаратної платформи. На x86_64 номер виклику передається в `orig_rax`, а аргументи — в `rdi`, `rsi`, `rdx`, `r10`, `r8`, `r9`. На архітектурі ARM64 номер виклику передається в регістрі `x8`, а аргументи — у регістрах від `x0` до `x5`. Інструменти трасування вимагають умовної компіляції під кожну цільову архітектуру.

8. **Розкодування аргументів системних викликів:** У повноцінних інструментах (таких як `strace`) трасувальник не просто друкує шістнадцяткові значення регістрів, а зіставляє номер системного виклику з таблицею системних викликів ядра (`sys_call_table`). Наприклад, для виклику `sys_read(fd, buf, count)` трасувальник інтерпретує перші три регістри як файловий дескриптор, вказівник буфера та розмір читання відповідно, декодуючи прапорці пристроїв та системні символи.

9. **Обробка аварійних сигналів цільового процесу:** Якщо трасований процес спричиняє помилку сегментації пам'яті (`SIGSEGV`) або ділення на нуль (`SIGFPE`), ядро зупиняє процес і надсилає сповіщення трасувальнику. Трасувальник перевіряє `WIFSTOPPED(status)` і може прочитати інформацію про причину аварії через виклик `ptrace(PTRACE_GETSIGINFO, pid, 0, &siginfo)`.

10. **Продуктивність та оптимізації:** Оскільки трасування через `PTRACE_SYSCALL` призводить до двох зупинок і двох перемикань контексту на кожен системний виклик, використання трасувальника уповільнює виконання програм з інтенсивним I/O у 10–50 разів. Для зменшення накладних витрат у високопродуктивних системах моніторингу замість `ptrace` використовують eBPF-зонди або `perf_event_open`.

11. **Тестування на реальних бінарних файлах:** Під час тестування міні-трасувальника рекомендується запускати прості системні утиліти, такі як `ls`, `whoami` або `cat`. Трасувальник перехопить перші виклики завантаження сокетів та динамічного зв'язування бібліотек (`execve`, `brk`, `mmap`, `access`, `openat`), наочно демонструючи кожен крок ініціалізації середовища виконання у просторі користувача.

12. **Практична цінність реалізації:** Написання власного міні-трасувальника дозволяє глибше зрозуміти низькорівневу взаємодію між ядром Linux, таблицями сторінок та процесором. Розуміння механізмів `PTRACE_SYSCALL` і `PTRACE_GETREGS` показує, як влаштовані професійні налагоджувачі та чому системний виклик `ptrace` лишається надійним фундаментом інструментів системного аналізу.
