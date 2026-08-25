# ⚙️ Практикум: Інспектування стека, оточення й спадковості процесів

Цей практикум присвячено практичній розробці аналітичної утиліти системного рівня на мовах C та C++, яка в реальному часі досліджує початковий макет стека процесу, розбирає структуру масивів `argv`, `environ` та `auxv`, досліджує механіку успадкування файлових дескрипторів із прапорцем `O_CLOEXEC`, а також розраховує та перевіряє межі системного ліміту `ARG_MAX`.

## 1. Постановка практичної задачі

При розробці високонавантажених серверів, системних демонів, сервісів оркестрації або систем ізоляції контейнерів (наприклад, Docker чи systemd) системний програміст постійно стикається з питанням точного контролю стану, який передається дитячим процесам. Недбала робота з середовищем або файловими дескрипторами призводить до двох основних класів системних дефектів:

1. **Витік файлових дескрипторів (File Descriptor Leakage)**: Якщо батьківський процес відкриває сокет бази даних, сокет сервера або файл із паролями й не встановлює прапорець `O_CLOEXEC`, будь-який сторонній процес, запущений через `execve()`, отримує прямий доступ до цього дескриптора. Це створює діру в безпеці та заважає закриттю ресурсів.
2. **Перевищення меж ARG_MAX**: При генерації командних рядків із тисячами параметрів процес може раптово впасти з помилкою `E2BIG`. Для запобігання цьому сервіс повинен динамічно розраховувати доступний ліміт пам'яті під аргументи.

Наша мета — створити комплексний інструмент інспектування, який виконує чотири задачі:
- Повноцінний дамп початкових параметрів стека (`argc`, `argv`, `environ`).
- Читання системного допоміжного вектора `auxv` через `getauxval()`.
- Експериментальна перевірка закриття дескрипторів при виклику `execve()` для звичайного дескриптора та дескриптора з `O_CLOEXEC`.
- Динамічний розрахунок межі `ARG_MAX` за допомогою виклику `sysconf(_SC_ARG_MAX)`.

### 1.1. Атомарність O_CLOEXEC у багатопотокових програмах

У ранніх стандартах POSIX прапорець закриття при виконанні встановлювався у два окремих кроки:

:::tabs
```c
/* Низькобезпечне встановлення FD_CLOEXEC у два кроки C */
#include <fcntl.h>

int fd = open("/etc/shadow", O_RDONLY);
/* Потенційна діра в безпеці! Стан гонки між open та fcntl */
int flags = fcntl(fd, F_GETFD);
fcntl(fd, F_SETFD, flags | FD_CLOEXEC);
```
```cpp
// Низькобезпечне встановлення FD_CLOEXEC у C++
#include <fcntl.h>

int fd = ::open("/etc/shadow", O_RDONLY);
int flags = ::fcntl(fd, F_GETFD);
::fcntl(fd, F_SETFD, flags | FD_CLOEXEC);
```
:::

Якщо інший потік виконання виконував системний виклик `fork()` + `execve()` саме у проміжку між викликами `open()` та `fcntl()`, дитячий процес встигав успадкувати відкритий дескриптор без встановленого прапорця `FD_CLOEXEC`.

Для усунення цієї вразливості в ядро Linux було додано атомарний прапорець створення `O_CLOEXEC`. Під час виклику `open(path, O_RDONLY | O_CLOEXEC)` ядро встановлює прапорець у таблиці дескрипторів безпосередньо у мить створення файлового об'єкта, унеможливлюючи будь-який витік ресурсів.

### 1.2. Виконання у контейнерах та системних демонах (systemd)

Сучасні рантайми контейнерів (runc, containerd) та менеджери системних сервісів (systemd) активно використовують передачу файлових дескрипторів через `execve()`. Наприклад, механізм активації сокетів у systemd (Socket Activation) створює мережевий сокет у системному процесі, призначає йому дескриптор номер 3 (`SD_LISTEN_FDS_START`) та свідомо **не** встановлює прапорець `O_CLOEXEC`. Після виклику `execve()` дитячий сервіс відразу має готовий відкритий мережевий сокет без виконання викликів `bind()` та `listen()`.

Навпаки, всі внутрішні файлові дескриптори рантайму контейнера (покажчики на cgroups, namespaces, epoll-петлі) позначаються прапорцем `O_CLOEXEC`, щоб контейнеризований процес користувача не міг отримати доступ до управляючих структур хост-системи.

---

## 2. Повна реалізація інспектора на мовах C та C++

Наведені нижче приклади містять повні джерела утиліти інспектування. Кожну вкладку можна скомпілювати як самостійний виконуваний файл.

:::tabs
```c
/* Приклад на мові C: Аналіз стека, перевірка O_CLOEXEC та розрахунок ARG_MAX */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/auxv.h>
#include <sys/wait.h>

extern char **environ;

void dump_stack_and_environment(int argc, char *argv[]) {
    printf("=== Process Context Dump (PID: %d) ===\n", getpid());
    printf("Number of arguments (argc): %d\n", argc);

    for (int i = 0; i < argc; ++i) {
        printf("  argv[%d] at address %p -> %s\n", i, (void*)argv[i], argv[i]);
    }

    printf("\n--- Environment Variables (first 5 entries) ---\n");
    for (int i = 0; environ[i] != NULL && i < 5; ++i) {
        printf("  env[%d] at address %p -> %s\n", i, (void*)environ[i], environ[i]);
    }

    printf("\n--- Auxiliary Vector Kernel Metadata ---\n");
    printf("  Page Size (AT_PAGESZ) : %lu bytes\n", getauxval(AT_PAGESZ));
    printf("  Entry Point (AT_ENTRY): 0x%lx\n", getauxval(AT_ENTRY));
    printf("  ELF Base (AT_BASE)    : 0x%lx\n", getauxval(AT_BASE));
    printf("  Secure Mode (AT_SECURE): %lu\n", getauxval(AT_SECURE));

    long arg_max = sysconf(_SC_ARG_MAX);
    printf("  System ARG_MAX Limit  : %ld bytes\n\n", arg_max);
}

void verify_descriptor_inheritance(void) {
    printf("=== Testing Descriptor Inheritance & O_CLOEXEC ===\n");

    /* Створення звичайного дескриптора */
    int fd_leaked = open("/dev/null", O_RDONLY);
    /* Створення дескриптора із захистом від витоку */
    int fd_protected = open("/dev/null", O_RDONLY | O_CLOEXEC);

    if (fd_leaked < 0 || fd_protected < 0) {
        perror("Failed to open /dev/null");
        return;
    }

    printf("Created fd_leaked = %d (normal), fd_protected = %d (O_CLOEXEC)\n",
           fd_leaked, fd_protected);

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork failed");
        return;
    }

    if (pid == 0) {
        /* Дитячий процес заступає виконувати /bin/true */
        char *child_argv[] = { "true", NULL };
        printf("[Child PID %d] Executing execve(/bin/true)...\n", getpid());
        fflush(stdout);

        execve("/bin/true", child_argv, environ);

        perror("execve failed");
        _exit(EXIT_FAILURE);
    } else {
        int status = 0;
        waitpid(pid, &status, 0);
        printf("[Parent] Child finished with exit code %d\n", WEXITSTATUS(status));

        close(fd_leaked);
        close(fd_protected);
    }
}

int main(int argc, char *argv[]) {
    dump_stack_and_environment(argc, argv);
    
    /* Якщо програма викликана без додаткових прапорців, запускаємо тест */
    if (argc == 1) {
        verify_descriptor_inheritance();
    }

    return EXIT_SUCCESS;
}
```
```cpp
// Приклад на C++20: Системний інспектор контексту з використанням RAII
#include <iostream>
#include <vector>
#include <string_view>
#include <span >
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <sys/auxv.h>
#include <sys/wait.h>

extern char **environ;

class SystemContextInspector {
public:
    static void inspect_stack(int argc, char *argv[]) {
        std::cout << "=== C++ System Context Inspector (PID: " << ::getpid() << ") ===\n";
        std::cout << "argc: " << argc << "\n";

        std::span<char*> arg_span(argv, static_cast<size_t>(argc));
        for (size_t i = 0; i < arg_span.size(); ++i) {
            std::cout << "  argv[" << i << "] (" << static_cast<void*>(arg_span[i]) 
                      << ") -> " << arg_span[i] << "\n";
        }

        std::cout << "\n--- Environment Snapshot (First 5) ---\n";
        size_t count = 0;
        for (char **env = environ; *env != nullptr && count < 5; ++env, ++count) {
            std::cout << "  env[" << count << "] (" << static_cast<void*>(*env) 
                      << ") -> " << *env << "\n";
        }

        std::cout << "\n--- Auxiliary Vector (Kernel Metadata) ---\n";
        std::cout << "  AT_PAGESZ : " << ::getauxval(AT_PAGESZ) << " bytes\n";
        std::cout << "  AT_ENTRY  : 0x" << std::hex << ::getauxval(AT_ENTRY) << std::dec << "\n";
        std::cout << "  AT_SECURE : " << ::getauxval(AT_SECURE) << "\n";

        long arg_max = ::sysconf(_SC_ARG_MAX);
        std::cout << "  ARG_MAX   : " << arg_max << " bytes\n\n";
    }

    static void run_cloexec_experiment() {
        std::cout << "=== Running C++ Descriptor Leakage Experiment ===\n";

        // RAII обгортка для файлового дескриптора
        struct ScopedDescriptor {
            int fd = -1;
            ~ScopedDescriptor() {
                if (fd >= 0) ::close(fd);
            }
        };

        ScopedDescriptor normal_fd{ ::open("/dev/null", O_RDONLY) };
        ScopedDescriptor cloexec_fd{ ::open("/dev/null", O_RDONLY | O_CLOEXEC) };

        if (normal_fd.fd < 0 || cloexec_fd.fd < 0) {
            throw std::system_error(errno, std::generic_category(), "open failed");
        }

        std::cout << "Normal FD  : " << normal_fd.fd << " (will survive execve)\n";
        std::cout << "CLOEXEC FD : " << cloexec_fd.fd << " (will close on execve)\n";

        pid_t pid = ::fork();
        if (pid < 0) {
            throw std::system_error(errno, std::generic_category(), "fork failed");
        }

        if (pid == 0) {
            char *child_args[] = { const_cast<char*>("true"), nullptr };
            ::execve("/bin/true", child_args, environ);
            ::_exit(127);
        }

        int status = 0;
        ::waitpid(pid, &status, 0);
        std::cout << "Child completed with exit code: " << WEXITSTATUS(status) << "\n";
    }
};

int main(int argc, char *argv[]) {
    try {
        SystemContextInspector::inspect_stack(argc, argv);
        if (argc == 1) {
            SystemContextInspector::run_cloexec_experiment();
        }
    } catch (const std::exception& ex) {
        std::cerr << "Fatal Error: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
:::

---

## 3. Детальний покроковий розбір результатів та трасування

Під час запуску розробленої утиліти системний програміст повинен проаналізувати кілька важливих аспектів поведінки ядра Linux:

### 3.1. Перевірка адресації початкового стека

Зверніть увагу на адреси пам'яті, які виводить утиліта для `argv[i]` та `environ[i]`. На 64-бітних архітектурах x86_64 всі ці адреси розташовані в районі `0x7fff...`. Це найвища область віртуального адресного простору користувача. Рядки в Інформаційному блоці йдуть один за одним із кроком, що дорівнює довжині рядка плюс 1 байт для нульового символу `\0`.

### 3.2. Читання auxv безпосередньо з /proc/self/auxv

Окрім бібліотечної функції `getauxval()`, програма може зчитати бінарний вміст віртуального файлу `/proc/self/auxv`. Цей файл представляє собою сирий масив структур `Elf64_auxv_t`, записаний ядром прямо зі стека процесу. Зчитування `/proc/self/auxv` дозволяє дампанути абсолютно всі пари `AT_*`, не знаючи їхніх номерів заздалегідь.

### 3.3. Аналіз трасування через strace

Щоб побачити, як ядро обробляє дескриптори під час системного виклику `execve()`, відтранслюйте програму й запустіть її під трасувальником системних викликів `strace`:

```bash
strace -f -e trace=openat,close,execve ./proc_inspector
```

У логу трасування ви побачите таку послідовність дій:
1. Батьківський процес виконує `openat(AT_FDCWD, "/dev/null", O_RDONLY)` і отримує, наприклад, дескриптор `3`.
2. Батьківський процес виконує `openat(AT_FDCWD, "/dev/null", O_RDONLY|O_CLOEXEC)` і отримує дескриптор `4`.
3. Після виклику `fork()` дитячий процес викликає `execve("/bin/true", ["true"], ...)`.
4. У мить виконання `execve` ядро Linux сканує внутрішню таблицю дескрипторів процесу. Бачачи прапорець `O_CLOEXEC` на дескрипторі `4`, ядро автоматично викликає внутрішню функцію закриття файлу. Дескриптор `3` залишається відкритим і переходить новій програмі.

### 3.4. Практична перевірка лімітів ARG_MAX

Для того, щоб перевірити дію ліміту `ARG_MAX` в умовах реальної оболонки Bash, спробуйте виконати тестовий запуск із передачею великого масиву аргументів через утиліту `seq`:

```bash
./proc_inspector $(seq 1 300000)
```

При виконанні цієї команди оболонка сформує масив аргументів вагою понад 2 МБ. Ядро Linux перерве системний виклик `execve()` і поверне помилку `E2BIG`, після чого оболонка виведе повідомлення `Argument list too long`. Це підтверджує, що теоретичні обмеження `sysconf(_SC_ARG_MAX)` є строго діючими правилами ядра Linux.
