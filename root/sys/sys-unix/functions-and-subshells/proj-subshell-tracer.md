# ⚙️ Практикум: інспекція підоболонок та емуляція динамічної видимості у C та C++

У командних оболонках Unix різниця між викликом функції та створенням підоболонки є фундаментальною межею між обчисленнями в межах одного адресного простору та системним клонуванням процесу через механізм ядра `fork()`.

Цей практикум розбирає три ключові інженерні задачі та супроводжує їх повними прикладами на мовах C та ідіоматичному C++:
1. **Низькорівнева емуляція підоболонок**: демонстрація семантики Copy-on-Write (COW) для віртуальної пам'яті та спільного використання позицій відкритих файлових дескрипторів між батьківським процесом і subshell.
2. **Побудова рушія динамічної області видимості (Dynamic Scope)**: реалізація стека викликів функцій та ланцюгового пошуку змінних, ідентичного до поведінки `local` у GNU Bash.
3. **Бенчмаркінг системних накладних витрат**: точний вимір різниці між переходами всередині процесу та створенням структур ядра через `fork()` з аналізом сторінкових збоїв (Page Faults) та перемикань контексту.

---

## 1. Анатомія ізоляції пам'яті та спільних дескрипторів

Коли інтерпретатор створює явну підоболонку `( var=42; echo test )` або конвеєр `cmd1 | cmd2`, ядро операційної системи дублює структури процесу. Змінні користувача ізолюються, але відкриті файлові описи (Open File Descriptions) у ядрі залишаються спільними.

### Фізика Copy-on-Write та VFS

Під час виконання системного виклику `fork()` ядро Linux не копіює всю фізичну пам'ять процесу. Замість цього воно дублює таблицю сторінок пам'яті (Page Tables) і позначає всі сторінки як доступні лише для читання (`read-only`). Щойно дочірній процес (підоболонка) намагається записати нове значення у змінну, процесор генерує апаратне переривання Page Fault (код помилки доступу до сторінки). Ядро перехоплює це переривання, виділяє нову фізичну сторінку оперативної пам'яті, копіює туди 4 кілобайти даних, оновлює запис у таблиці сторінок дочірнього процесу і дозволяє запис.

З файловими дескрипторами ситуація принципово інша: таблиця файлових дескрипторів процесу копіюється, але кожен дескриптор продовжує посилатися на той самий об'єкт `struct file` у таблиці відкритих файлів ядра (VFS Open File Description Table). Через це системне зміщення у файлі (`f_pos`) є спільним: будь-який запис або зчитування дочірнім процесом автоматично зсуває покажчик для батьківського процесу.

У багатопотокових додатках виклик `fork()` для створення підоболонки несе додаткову загрозу: дублюється лише той потік, що викликав `fork()`. Якщо інший потік у цей момент утримував м'ютекс розподільника пам'яті (наприклад, `malloc`), у дочірньому процесі цей м'ютекс назавжди залишиться заблокованим, спричиняючи взаємне блокування (deadlock). Саме тому сучасні оболонки на зразок Bash є однопотоковими процесами, що використовують системний цикл обробки подій замість потоків `pthread`.

Нижче наведено повноцінну програму, яка наочно демонструє ці фізичні ефекти:

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <string.h>

// Симуляція стану командної оболонки
typedef struct {
    int execution_counter;
    char current_working_dir[256];
} ShellContext;

void demonstrate_subshell_isolation(void) {
    ShellContext ctx;
    ctx.execution_counter = 0;
    strcpy(ctx.current_working_dir, "/var/log");

    // Створюємо спільний тимчасовий файл для перевірки дескрипторів
    int shared_fd = open("/tmp/subshell_test.log", O_CREAT | O_RDWR | O_TRUNC, 0644);
    if (shared_fd == -1) {
        perror("open failed");
        return;
    }

    printf("[Parent Before Fork] Counter: %d, CWD: %s\n", 
           ctx.execution_counter, ctx.current_working_dir);

    pid_t pid = fork();

    if (pid < 0) {
        perror("fork failed");
        close(shared_fd);
        return;
    }

    if (pid == 0) {
        // === Дочірній процес: Підоболонка (Subshell) ===
        printf("  [Subshell PID %d] Modifying context...\n", getpid());
        ctx.execution_counter = 999; // Модифікація скопійованої сторінки пам'яті
        strcpy(ctx.current_working_dir, "/tmp");

        const char *subshell_msg = "Line from subshell\n";
        write(shared_fd, subshell_msg, strlen(subshell_msg));

        printf("  [Subshell PID %d] Counter is now: %d, CWD: %s\n",
               getpid(), ctx.execution_counter, ctx.current_working_dir);

        close(shared_fd);
        exit(0); // Завершення підоболонки, пам'ять знищується ядром
    }

    // === Батьківський процес (Main Shell) ===
    int status;
    waitpid(pid, &status, 0); // Очікуємо завершення підоболонки

    const char *parent_msg = "Line from parent\n";
    // Зверніть увагу: зміщення (offset) зсунуто дочірнім процесом!
    write(shared_fd, parent_msg, strlen(parent_msg));

    printf("[Parent After Wait] Counter: %d (NOT 999!), CWD: %s\n",
           ctx.execution_counter, ctx.current_working_dir);

    // Перевіряємо розмір та вміст файлу
    lseek(shared_fd, 0, SEEK_SET);
    char buffer[256];
    ssize_t bytes_read = read(shared_fd, buffer, sizeof(buffer) - 1);
    if (bytes_read > 0) {
        buffer[bytes_read] = '\0';
        printf("[File Content Analysis]:\n%s", buffer);
    }

    close(shared_fd);
    unlink("/tmp/subshell_test.log");
}

int main(void) {
    demonstrate_subshell_isolation();
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <array>
#include <system_error>
#include <unistd.h>
#include <sys/wait.h>
#include <fcntl.h>

struct ShellContext {
    int execution_counter = 0;
    std::string current_working_dir = "/var/log";
};

class FileDescriptor {
    int fd_ = -1;
public:
    explicit FileDescriptor(int fd) : fd_(fd) {}
    ~FileDescriptor() { if (fd_ >= 0) ::close(fd_); }
    int get() const noexcept { return fd_; }
    
    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;
    FileDescriptor(FileDescriptor&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    FileDescriptor& operator=(FileDescriptor&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }
};

void demonstrate_cpp_subshell_isolation() {
    ShellContext ctx;
    
    int raw_fd = ::open("/tmp/subshell_test_cpp.log", O_CREAT | O_RDWR | O_TRUNC, 0644);
    if (raw_fd == -1) {
        throw std::system_error(errno, std::generic_category(), "open failed");
    }
    FileDescriptor shared_fd(raw_fd);

    std::cout << "[Parent Before Fork] Counter: " << ctx.execution_counter 
              << ", CWD: " << ctx.current_working_dir << "\n";

    pid_t pid = ::fork();
    if (pid < 0) {
        throw std::system_error(errno, std::generic_category(), "fork failed");
    }

    if (pid == 0) {
        // Дочірній процес (Subshell)
        std::cout << "  [Subshell PID " << ::getpid() << "] Modifying context...\n";
        ctx.execution_counter = 999;
        ctx.current_working_dir = "/tmp";

        std::string subshell_msg = "Line from modern C++ subshell\n";
        ::write(shared_fd.get(), subshell_msg.data(), subshell_msg.size());

        std::cout << "  [Subshell PID " << ::getpid() << "] Counter: " 
                  << ctx.execution_counter << ", CWD: " << ctx.current_working_dir << "\n";
        std::exit(0);
    }

    int status = 0;
    ::waitpid(pid, &status, 0);

    std::string parent_msg = "Line from modern C++ parent\n";
    ::write(shared_fd.get(), parent_msg.data(), parent_msg.size());

    std::cout << "[Parent After Wait] Counter: " << ctx.execution_counter 
              << " (Unchanged), CWD: " << ctx.current_working_dir << "\n";

    ::lseek(shared_fd.get(), 0, SEEK_SET);
    std::array<char, 256> buf{};
    ssize_t n = ::read(shared_fd.get(), buf.data(), buf.size() - 1);
    if (n > 0) {
        buf[n] = '\0';
        std::cout << "[File Content Analysis]:\n" << buf.data();
    }

    ::unlink("/tmp/subshell_test_cpp.log");
}

int main() {
    try {
        demonstrate_cpp_subshell_isolation();
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

---

## 2. Реалізація динамічної видимості змінних (Dynamic Scope Evaluator)

У статичних мовах програмування (C, C++, Rust) змінна шукається у лексичному блоці вихідного коду під час компіляції. У Bash пошук змінної відбувається **динамічно вгору по стеку активних фреймів викликів у рантаймі**.

Коли виконується інструкція `local var=value`, інтерпретатор створює новий запис у таблиці символів поточного фрейму виклику. Будь-яка вкладена функція, яка читає `$var`, шукає цю змінну лінійно: спочатку у своєму власному фреймі, потім у фреймі функції, яка її викликала, і так далі до глобального рівня.

Цей механізм дозволяє реалізовувати неявну передачу контексту крізь шари абстракцій без явної передачі параметрів у кожен виклик. Проте динамічна видимість створює загрозу колізій імен: якщо викликана допоміжна функція змінює змінну, яка випадково збігається за іменем з локальною змінною викликача, відбувається неявна зміна стану фрейму вищого рівня.

Наступна програма реалізує інтерпретатор таблиці символів зі стеком викликів, емулюючи точну роботу динамічної видимості у Bash:

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_VARS 32
#define MAX_FRAMES 16

typedef struct {
    char name[32];
    char value[64];
} Variable;

typedef struct {
    char function_name[32];
    Variable locals[MAX_VARS];
    int local_count;
} CallFrame;

typedef struct {
    CallFrame frames[MAX_FRAMES];
    int frame_top; // 0 - глобальний рівень
} ScopeStack;

void init_scope(ScopeStack *stack) {
    stack->frame_top = 0;
    strcpy(stack->frames[0].function_name, "global");
    stack->frames[0].local_count = 0;
}

void push_frame(ScopeStack *stack, const char *func_name) {
    if (stack->frame_top >= MAX_FRAMES - 1) {
        fprintf(stderr, "Stack overflow!\n");
        return;
    }
    stack->frame_top++;
    strcpy(stack->frames[stack->frame_top].function_name, func_name);
    stack->frames[stack->frame_top].local_count = 0;
    printf("──► Entering function: %s (Depth: %d)\n", func_name, stack->frame_top);
}

void pop_frame(ScopeStack *stack) {
    if (stack->frame_top <= 0) return;
    printf("◄── Exiting function: %s\n", stack->frames[stack->frame_top].function_name);
    stack->frame_top--;
}

void set_local(ScopeStack *stack, const char *name, const char *val) {
    CallFrame *current = &stack->frames[stack->frame_top];
    for (int i = 0; i < current->local_count; i++) {
        if (strcmp(current->locals[i].name, name) == 0) {
            strncpy(current->locals[i].value, val, 63);
            return;
        }
    }
    if (current->local_count < MAX_VARS) {
        strncpy(current->locals[current->local_count].name, name, 31);
        strncpy(current->locals[current->local_count].value, val, 63);
        current->local_count++;
    }
}

// Динамічний пошук: йдемо від вершини стека до глобального фрейму 0
const char* resolve_variable(const ScopeStack *stack, const char *name) {
    for (int f = stack->frame_top; f >= 0; f--) {
        const CallFrame *frame = &stack->frames[f];
        for (int i = 0; i < frame->local_count; i++) {
            if (strcmp(frame->locals[i].name, name) == 0) {
                return frame->locals[i].value;
            }
        }
    }
    return NULL; // Змінна не знайдена
}

void inner_function(ScopeStack *stack) {
    push_frame(stack, "inner_function");
    // inner_function не оголошує 'auth_token', але читає його з контексту виклику!
    const char *token = resolve_variable(stack, "auth_token");
    printf("  [inner_function] Resolved 'auth_token': %s\n", token ? token : "<undefined>");
    pop_frame(stack);
}

void outer_function(ScopeStack *stack) {
    push_frame(stack, "outer_function");
    set_local(stack, "auth_token", "SECRET_KEY_12345");
    inner_function(stack);
    pop_frame(stack);
}

int main(void) {
    ScopeStack stack;
    init_scope(&stack);

    set_local(&stack, "auth_token", "GLOBAL_DEFAULT");
    printf("[Main] Initial auth_token: %s\n", resolve_variable(&stack, "auth_token"));

    outer_function(&stack);

    printf("[Main] auth_token after calls: %s\n", resolve_variable(&stack, "auth_token"));
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <optional>
#include <memory>

class DynamicScopeStack {
    struct CallFrame {
        std::string function_name;
        std::unordered_map<std::string, std::string> locals;
    };
    std::vector<CallFrame> frames_;

public:
    DynamicScopeStack() {
        frames_.push_back(CallFrame{"global", {}});
    }

    void push_frame(const std::string& func_name) {
        frames_.push_back(CallFrame{func_name, {}});
        std::cout << "──► Entering function: " << func_name 
                  << " (Depth: " << frames_.size() - 1 << ")\n";
    }

    void pop_frame() {
        if (frames_.size() > 1) {
            std::cout << "◄── Exiting function: " << frames_.back().function_name << "\n";
            frames_.pop_back();
        }
    }

    void set_local(const std::string& name, const std::string& value) {
        frames_.back().locals[name] = value;
    }

    // Динамічний пошук змінної від вершини стека вниз
    std::optional<std::string> resolve(const std::string& name) const {
        for (auto it = frames_.rbegin(); it != frames_.rend(); ++it) {
            auto found = it->locals.find(name);
            if (found != it->locals.end()) {
                return found->second;
            }
        }
        return std::nullopt;
    }
};

void run_inner(DynamicScopeStack& scope) {
    scope.push_frame("run_inner");
    auto token = scope.resolve("auth_token");
    std::cout << "  [run_inner] Resolved 'auth_token': " 
              << token.value_or("<undefined>") << "\n";
    scope.pop_frame();
}

void run_outer(DynamicScopeStack& scope) {
    scope.push_frame("run_outer");
    scope.set_local("auth_token", "MODERN_CPP_SECRET_999");
    run_inner(scope);
    scope.pop_frame();
}

int main() {
    DynamicScopeStack scope;
    scope.set_local("auth_token", "GLOBAL_CPP_DEFAULT");

    std::cout << "[Main] Initial token: " << scope.resolve("auth_token").value() << "\n";
    run_outer(scope);
    std::cout << "[Main] Final token: " << scope.resolve("auth_token").value() << "\n";

    return 0;
}
```
:::

---

## 3. Бенчмаркінг: вартість виклику функції проти створення Subshell

Чому заміна круглих дужок `( cmd )` на фігурні дужки `{ cmd; }` критична для продуктивності системних утиліт?

Для відповіді на це запитання розглянемо операційні витрати ядра операційної системи. Виклик функції всередині процесу — це лише збереження регістрів на апаратному стеку та передача керування за новою адресою пам'яті (інструкція `call` процесора). 

Натомість системний виклик `fork()` вимагає:
1. Переходу в простір ядра через апаратне переривання або інструкцію `syscall`.
2. Виділення та ініціалізації нової структури `task_struct` та структур `mm_struct` у ядрі.
3. Копіювання записів таблиць сторінок пам'яті (`pgd`, `p4d`, `pud`, `pmd`, `pte`) процесу.
4. Оновлення лічильників посилань на файлові дескриптори, файлові системи та простори імен (namespaces).
5. Реєстрації нового процесу у планувальнику завдань CFS (Completely Fair Scheduler).
6. Синхронізації та очікування батьківським процесом через системний виклик `waitpid()`.

Наведений нижче бенчмарк на мовах C та C++ вимірює точну різницю часу між цими двома операціями та аналізує телеметрію ядра:

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/resource.h>
#include <time.h>

#define ITERATIONS 5000

static inline void in_process_function(volatile int *val) {
    *val += 1;
}

double measure_function_calls(void) {
    volatile int counter = 0;
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    for (int i = 0; i < ITERATIONS; i++) {
        in_process_function(&counter);
    }

    clock_gettime(CLOCK_MONOTONIC, &end);
    return (end.tv_sec - start.tv_sec) * 1e6 + (end.tv_nsec - start.tv_nsec) / 1e3;
}

double measure_subshell_forks(void) {
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    for (int i = 0; i < ITERATIONS; i++) {
        pid_t pid = fork();
        if (pid == 0) {
            _exit(0); // Імітуємо швидке завершення підоболонки
        }
        waitpid(pid, NULL, 0);
    }

    clock_gettime(CLOCK_MONOTONIC, &end);
    return (end.tv_sec - start.tv_sec) * 1e6 + (end.tv_nsec - start.tv_nsec) / 1e3;
}

int main(void) {
    printf("Benchmarking %d operations on current CPU...\n", ITERATIONS);
    double fn_time_us = measure_function_calls();
    double fork_time_us = measure_subshell_forks();

    printf("In-process Function Calls: %.2f us total (%.4f us per call)\n",
           fn_time_us, fn_time_us / ITERATIONS);
    printf("Subshell fork() Creation:  %.2f us total (%.2f us per fork)\n",
           fork_time_us, fork_time_us / ITERATIONS);
    printf("Cost Ratio: fork() is ~%.1f times slower than in-process function!\n",
           fork_time_us / fn_time_us);

    // Інспекція ресурсів ядра через getrusage
    struct rusage usage;
    if (getrusage(RUSAGE_CHILDREN, &usage) == 0) {
        printf("Kernel Telemetry for %d child subshells:\n", ITERATIONS);
        printf("  Minor Page Faults (COW events): %ld\n", usage.ru_minflt);
        printf("  Voluntary Context Switches:     %ld\n", usage.ru_nvcsw);
        printf("  Involuntary Context Switches:   %ld\n", usage.ru_nivcsw);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <chrono>
#include <vector>
#include <system_error>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/resource.h>

constexpr int ITERATIONS = 5000;

void benchmark_in_process() {
    volatile int counter = 0;
    auto start = std::chrono::high_resolution_clock::now();

    for (int i = 0; i < ITERATIONS; ++i) {
        counter += 1;
    }

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::micro> elapsed = end - start;
    std::cout << "In-process Calls: " << elapsed.count() << " us (" 
              << elapsed.count() / ITERATIONS << " us/call)\n";
}

void benchmark_subshells() {
    auto start = std::chrono::high_resolution_clock::now();

    for (int i = 0; i < ITERATIONS; ++i) {
        pid_t pid = ::fork();
        if (pid < 0) {
            throw std::system_error(errno, std::generic_category(), "fork failed");
        }
        if (pid == 0) {
            ::_exit(0);
        }
        ::waitpid(pid, nullptr, 0);
    }

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::micro> elapsed = end - start;
    std::cout << "Subshell Forks:   " << elapsed.count() << " us (" 
              << elapsed.count() / ITERATIONS << " us/fork)\n";
}

int main() {
    try {
        std::cout << "Running benchmark for " << ITERATIONS << " iterations...\n";
        benchmark_in_process();
        benchmark_subshells();

        rusage usage{};
        if (::getrusage(RUSAGE_CHILDREN, &usage) == 0) {
            std::cout << "Kernel Telemetry for " << ITERATIONS << " child subshells:\n";
            std::cout << "  Minor Page Faults (COW events): " << usage.ru_minflt << "\n";
            std::cout << "  Voluntary Context Switches:     " << usage.ru_nvcsw << "\n";
            std::cout << "  Involuntary Context Switches:   " << usage.ru_nivcsw << "\n";
        }
    } catch (const std::exception& e) {
        std::cerr << "Benchmark Error: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

Практичні вимірювання підтверджують незмінну закономірність операційної системи: виклик функції виконується процесором за кілька наносекунд без перемикання контексту ядра. Натомість створення підоболонки через `fork()` займає від 300 до 800 мікросекунд, що у сотні разів повільніше. Інспекція лічильника `ru_minflt` показує тисячі мінорних збоїв сторінок пам'яті (Minor Page Faults), які генеруються ядром для копіювання COW-сторінок під час кожного створення підоболонки.
