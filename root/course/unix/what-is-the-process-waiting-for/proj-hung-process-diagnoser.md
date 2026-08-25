# ⚙️ Практикум: утиліта неінвазивної діагностики завислих процесів

Підключення важких налагоджувачів на кшталт GDB або запуск утиліти `strace` на високонавантажених виробничих серверах нерідко призводить до неприпустимих наслідків: механізм `ptrace` надсилає сигнали зупинки `SIGSTOP`, заморожує обробку запитів і може спровокувати аварійне вимикання контейнера оркестратором за тайм-аутом (*liveness probe failure*). 

У цьому практикумі реалізовано автономну, легковагу утиліту `prochook`, яка проводить глибокий неінвазивний аналіз завислого процесу та всіх його потоків виключно через інтерфейси псевдофайлової системи `/proc`. Утиліта не змінює стан цільового процесу, не надсилає сигналів і не використовує механізм `ptrace`, але надає вичерпну картину стану кожного потоку, системного виклику очікування, блокуючого файлового дескриптора та ядерного бектрейсу.

## 1. Архітектура та послідовність збору діагностики

Утиліта виконує діагностичний зріз у п'ять послідовних кроків, повністю уникаючи модифікації адресного простору досліджуваного процесу:

1. **Сканування групи потоків (TGID).** Відкривається каталог `/proc/[pid]/task/`, звідки зчитуються ідентифікатори всіх активних підпотоків (`TID`). На відміну від застарілих інтерфейсів ядра, де кожен потік міг розглядатися як окремий процес, каталог `task/` містить точний перелік усіх ниток виконання, що ділять спільний дескриптор пам'яті `mm_struct` та таблицю відкритих файлів `files_struct`.
2. **Аналіз станів та лічильників перемикань.** З файлу `/proc/[pid]/task/[tid]/status` вилучаються прапорець стану (`State`), ім'я потоку (`Name`) та лічильники добровільних і примусових перемикань контексту (`voluntary_ctxt_switches` / `nonvoluntary_ctxt_switches`). Якщо лічильник добровільних перемикань не змінюється між ітераціями, це прямо вказує на зависання всередині системного виклику.
3. **Отримання точки очікування ядра.** Зчитується вміст `/proc/[pid]/task/[tid]/wchan` для швидкої оцінки причини сну (`futex_wait_queue_me`, `sk_wait_data`, `io_schedule`). Функція ядра `get_wchan()` розмотує стек до межі виклику планувальника, що дає змогу миттєво локалізувати підсистему блокування без читання повного бектрейсу.
4. **Декодування активного системного виклику.** Парситься псевдофайл `/proc/[pid]/task/[tid]/syscall`. Якщо номер системного виклику відповідає операціям вводу-виводу (`read`, `write`, `recvfrom`), утиліта автоматично знаходить цільовий дескриптор у `/proc/[pid]/fd/[fd]` і визначає тип ресурсу через системний виклик `readlink()`. Якщо це мережевий сокет, утиліта виводить його inode, що дозволяє миттєво зіставити сокет із віддаленою IP-адресою та портом.
5. **Розгортання ядерного стека.** Якщо процес має права `CAP_SYS_PTRACE` або запущений під обліковим записом `root`, зчитується `/proc/[pid]/task/[tid]/stack` для реконструкції повного ланцюжка викликів функцій ядра.

## 2. Реалізація діагностичної утиліти

Нижче наведено робочий код утиліти двома мовами: на чистому POSIX C з ручною роботою з дескрипторами та ідіоматичному сучасному C++20 із застосуванням бібліотеки `std::filesystem`, типізованих структур та механізму RAII.

:::tabs
@tab C
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

// Трансляція найпоширеніших системних викликів x86_64
static const char* decode_syscall_x86_64(long nr) {
    switch (nr) {
        case 0:   return "read";
        case 1:   return "write";
        case 7:   return "poll";
        case 23:  return "select";
        case 35:  return "nanosleep";
        case 42:  return "connect";
        case 43:  return "accept";
        case 45:  return "recvfrom";
        case 74:  return "fsync";
        case 202: return "futex";
        case 232: return "epoll_wait";
        case 288: return "accept4";
        case -1:  return "RUNNING_IN_USERSPACE";
        default:  return "other_syscall";
    }
}

// Зчитування однорядкового псевдофайлу
static void read_proc_line(const char* path, char* buf, size_t max_len) {
    buf[0] = '\0';
    int fd = open(path, O_RDONLY);
    if (fd < 0) return;
    ssize_t n = read(fd, buf, max_len - 1);
    if (n > 0) {
        buf[n] = '\0';
        char* nl = strchr(buf, '\n');
        if (nl) *nl = '\0';
    }
    close(fd);
}

// Інспекція цільового дескриптора через readlink
static void inspect_fd(pid_t pid, long fd_num, char* out_target, size_t out_len) {
    char path[128];
    snprintf(path, sizeof(path), "/proc/%d/fd/%ld", pid, fd_num);
    ssize_t len = readlink(path, out_target, out_len - 1);
    if (len > 0) {
        out_target[len] = '\0';
    } else {
        snprintf(out_target, out_len, "unknown/closed (errno: %d)", errno);
    }
}

// Діагностика окремого потоку
static void inspect_thread(pid_t tgid, pid_t tid) {
    char path[256];
    char wchan[64] = "unknown";
    char syscall_raw[256] = "";
    char status_line[256];
    char thread_name[64] = "unknown";
    char state_char = '?';
    long vol_switches = -1, nonvol_switches = -1;

    // Читання /proc/[tgid]/task/[tid]/status
    snprintf(path, sizeof(path), "/proc/%d/task/%d/status", tgid, tid);
    FILE* sf = fopen(path, "r");
    if (sf) {
        while (fgets(status_line, sizeof(status_line), sf)) {
            if (strncmp(status_line, "Name:", 5) == 0) {
                sscanf(status_line + 5, "%63s", thread_name);
            } else if (strncmp(status_line, "State:", 6) == 0) {
                sscanf(status_line + 6, " %c", &state_char);
            } else if (strncmp(status_line, "voluntary_ctxt_switches:", 24) == 0) {
                sscanf(status_line + 24, "%ld", &vol_switches);
            } else if (strncmp(status_line, "nonvoluntary_ctxt_switches:", 27) == 0) {
                sscanf(status_line + 27, "%ld", &nonvol_switches);
            }
        }
        fclose(sf);
    }

    // Читання /proc/[tgid]/task/[tid]/wchan
    snprintf(path, sizeof(path), "/proc/%d/task/%d/wchan", tgid, tid);
    read_proc_line(path, wchan, sizeof(wchan));

    // Читання /proc/[tgid]/task/[tid]/syscall
    snprintf(path, sizeof(path), "/proc/%d/task/%d/syscall", tgid, tid);
    read_proc_line(path, syscall_raw, sizeof(syscall_raw));

    long syscall_nr = -1;
    unsigned long arg0 = 0, arg1 = 0, arg2 = 0;
    if (strlen(syscall_raw) > 0 && syscall_raw[0] != 'r') {
        sscanf(syscall_raw, "%ld 0x%lx 0x%lx 0x%lx", &syscall_nr, &arg0, &arg1, &arg2);
    }

    printf("  [+] Потік TID: %d (%s) | Стан: %c\n", tid, thread_name, state_char);
    printf("      Перемикання контексту: добровільні=%ld, примусові=%ld\n", vol_switches, nonvol_switches);
    printf("      Символ wchan: %s\n", wchan);
    printf("      Системний виклик: #%ld (%s)\n", syscall_nr, decode_syscall_x86_64(syscall_nr));

    // Якщо це блокуючий ввід-вивід на файловому дескрипторі
    if (syscall_nr == 0 || syscall_nr == 1 || syscall_nr == 45 || syscall_nr == 232) {
        char fd_target[256];
        inspect_fd(tgid, (long)arg0, fd_target, sizeof(fd_target));
        printf("      -> Блокування на FD %lu: %s\n", arg0, fd_target);
    } else if (syscall_nr == 202) {
        printf("      -> Блокування FUTEX на адресі пам'яті: 0x%lx (опція op=0x%lx, val=%lu)\n", arg0, arg1, arg2);
    }

    // Читання ядерного стека /proc/[tgid]/task/[tid]/stack
    snprintf(path, sizeof(path), "/proc/%d/task/%d/stack", tgid, tid);
    FILE* stf = fopen(path, "r");
    if (stf) {
        printf("      Ядерний стек (Kernel Call Stack):\n");
        char stack_line[256];
        int frame_idx = 0;
        while (fgets(stack_line, sizeof(stack_line), stf)) {
            char* nl = strchr(stack_line, '\n');
            if (nl) *nl = '\0';
            printf("        #%d %s\n", frame_idx++, stack_line);
        }
        fclose(stf);
    }
    printf("\n");
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <PID>\n", argv[0]);
        return 1;
    }

    pid_t pid = (pid_t)atoi(argv[1]);
    char task_dir_path[128];
    snprintf(task_dir_path, sizeof(task_dir_path), "/proc/%d/task", pid);

    DIR* dir = opendir(task_dir_path);
    if (!dir) {
        perror("Не вдалося відкрити /proc/[pid]/task");
        return 1;
    }

    printf("=== Діагностичний зріз процесу PID: %d ===\n\n", pid);

    struct dirent* entry;
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_name[0] == '.') continue;
        pid_t tid = (pid_t)atoi(entry->d_name);
        if (tid > 0) {
            inspect_thread(pid, tid);
        }
    }

    closedir(dir);
    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <filesystem>
#include <system_error>
#include <unistd.h>

namespace fs = std::filesystem;

struct SyscallInfo {
    long nr{-1};
    unsigned long arg0{0};
    unsigned long arg1{0};
    unsigned long arg2{0};
    std::string name{"RUNNING_IN_USERSPACE"};
};

struct ThreadDiagnostic {
    pid_t tid{0};
    std::string name{"unknown"};
    char state{'?'};
    long vol_switches{-1};
    long nonvol_switches{-1};
    std::string wchan{"unknown"};
    SyscallInfo syscall;
    std::optional<std::string> fd_target;
    std::vector<std::string> kernel_stack;
};

// Декодування номерів системних викликів x86_64
std::string decode_syscall_name(long nr) {
    switch (nr) {
        case 0:   return "read";
        case 1:   return "write";
        case 7:   return "poll";
        case 23:  return "select";
        case 35:  return "nanosleep";
        case 42:  return "connect";
        case 43:  return "accept";
        case 45:  return "recvfrom";
        case 74:  return "fsync";
        case 202: return "futex";
        case 232: return "epoll_wait";
        case 288: return "accept4";
        case -1:  return "RUNNING_IN_USERSPACE";
        default:  return "other_syscall";
    }
}

// Зчитування першого рядка файлу
std::string read_single_line(const fs::path& p) {
    std::ifstream is(p);
    std::string line;
    if (std::getline(is, line)) {
        return line;
    }
    return "";
}

// Інспекція цільового файлового дескриптора
std::string resolve_fd_target(pid_t pid, unsigned long fd_num) {
    fs::path fd_path = fs::path("/proc") / std::to_string(pid) / "fd" / std::to_string(fd_num);
    std::error_code ec;
    fs::path target = fs::read_symlink(fd_path, ec);
    if (!ec) {
        return target.string();
    }
    return "unknown/closed (" + ec.message() + ")";
}

// Збір інформації про окремий потік
ThreadDiagnostic collect_thread(pid_t tgid, pid_t tid) {
    ThreadDiagnostic diag;
    diag.tid = tid;

    const fs::path base = fs::path("/proc") / std::to_string(tgid) / "task" / std::to_string(tid);

    // 1. Статус потоку
    std::ifstream sf(base / "status");
    if (sf.is_open()) {
        std::string line;
        while (std::getline(sf, line)) {
            if (line.starts_with("Name:")) {
                diag.name = line.substr(line.find_first_not_of(" \t", 5));
            } else if (line.starts_with("State:")) {
                size_t pos = line.find_first_not_of(" \t", 6);
                if (pos != std::string::npos) diag.state = line[pos];
            } else if (line.starts_with("voluntary_ctxt_switches:")) {
                diag.vol_switches = std::stol(line.substr(24));
            } else if (line.starts_with("nonvoluntary_ctxt_switches:")) {
                diag.nonvol_switches = std::stol(line.substr(27));
            }
        }
    }

    // 2. wchan
    diag.wchan = read_single_line(base / "wchan");
    if (diag.wchan.empty()) diag.wchan = "0 (running/hidden)";

    // 3. syscall
    std::string sys_raw = read_single_line(base / "syscall");
    if (!sys_raw.empty() && sys_raw[0] != 'r') {
        std::istringstream iss(sys_raw);
        iss >> diag.syscall.nr;
        std::string a0, a1, a2;
        iss >> a0 >> a1 >> a2;
        try {
            if (!a0.empty()) diag.syscall.arg0 = std::stoul(a0, nullptr, 16);
            if (!a1.empty()) diag.syscall.arg1 = std::stoul(a1, nullptr, 16);
            if (!a2.empty()) diag.syscall.arg2 = std::stoul(a2, nullptr, 16);
        } catch (...) {}
        diag.syscall.name = decode_syscall_name(diag.syscall.nr);

        // Якщо це ввід-вивід з дескриптором
        if (diag.syscall.nr == 0 || diag.syscall.nr == 1 || diag.syscall.nr == 45 || diag.syscall.nr == 232) {
            diag.fd_target = resolve_fd_target(tgid, diag.syscall.arg0);
        }
    }

    // 4. Kernel Call Stack
    std::ifstream stf(base / "stack");
    if (stf.is_open()) {
        std::string stack_line;
        while (std::getline(stf, stack_line)) {
            if (!stack_line.empty()) {
                diag.kernel_stack.push_back(stack_line);
            }
        }
    }

    return diag;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <PID>\n";
        return 1;
    }

    pid_t pid = static_cast<pid_t>(std::stoi(argv[1]));
    const fs::path task_dir = fs::path("/proc") / std::to_string(pid) / "task";

    std::error_code ec;
    if (!fs::exists(task_dir, ec) || !fs::is_directory(task_dir, ec)) {
        std::cerr << "Помилка: процес із PID " << pid << " не знайдено в /proc.\n";
        return 1;
    }

    std::cout << "=== Діагностичний зріз процесу PID: " << pid << " ===\n\n";

    for (const auto& entry : fs::directory_iterator(task_dir, ec)) {
        if (!entry.is_directory()) continue;
        std::string filename = entry.path().filename().string();
        try {
            pid_t tid = static_cast<pid_t>(std::stoi(filename));
            ThreadDiagnostic diag = collect_thread(pid, tid);

            std::cout << "  [+] Потік TID: " << diag.tid << " (" << diag.name << ") | Стан: " << diag.state << "\n";
            std::cout << "      Перемикання контексту: добровільні=" << diag.vol_switches 
                      << ", примусові=" << diag.nonvol_switches << "\n";
            std::cout << "      Символ wchan: " << diag.wchan << "\n";
            std::cout << "      Системний виклик: #" << diag.syscall.nr << " (" << diag.syscall.name << ")\n";

            if (diag.fd_target) {
                std::cout << "      -> Блокування на FD " << diag.syscall.arg0 << ": " << *diag.fd_target << "\n";
            } else if (diag.syscall.nr == 202) {
                std::cout << "      -> Блокування FUTEX на адресі: 0x" << std::hex << diag.syscall.arg0 
                          << " (op=0x" << diag.syscall.arg1 << ", val=" << std::dec << diag.syscall.arg2 << ")\n";
            }

            if (!diag.kernel_stack.empty()) {
                std::cout << "      Ядерний стек (Kernel Call Stack):\n";
                for (size_t i = 0; i < diag.kernel_stack.size(); ++i) {
                    std::cout << "        #" << i << " " << diag.kernel_stack[i] << "\n";
                }
            }
            std::cout << "\n";
        } catch (...) {
            continue;
        }
    }

    return 0;
}
```
:::

## 3. Практичний запуск та інтерпретація результатів

Зкомпілюємо утиліту та запустимо її проти завислого сервісу:

```bash
# Збірка версії на C++20:
g++ -std=c++20 -O2 -Wall -Wextra prochook.cpp -o prochook

# Запуск від імені адміністратора для повного доступу до стеків ядра:
sudo ./prochook 18492
```

Приклад виводу для багатопотокового процесу з взаємним блокуванням м'ютексів та завислим мережевим сокетом:

```text
=== Діагностичний зріз процесу PID: 18492 ===

  [+] Потік TID: 18492 (main_event_loop) | Стан: S
      Перемикання контексту: добровільні=41920, примусові=12
      Символ wchan: epoll_wait
      Системний виклик: #232 (epoll_wait)
      -> Блокування на FD 4: anon_inode:[eventpoll]

  [+] Потік TID: 18493 (worker_thread_1) | Стан: S
      Перемикання контексту: добровільні=810, примусові=4
      Символ wchan: futex_wait_queue_me
      Системний виклик: #202 (futex)
      -> Блокування FUTEX на адресі: 0x7fff8040 (op=0x80, val=2)
      Ядерний стек (Kernel Call Stack):
        #0 [<0>] futex_wait_queue_me+0xc2/0x120
        #1 [<0>] futex_wait+0x139/0x240
        #2 [<0>] do_futex+0x12c/0x190
        #3 [<0>] __x64_sys_futex+0x125/0x180
        #4 [<0>] do_syscall_64+0x5c/0x90
        #5 [<0>] entry_SYSCALL_64_after_hwframe+0x6e/0xd8

  [+] Потік TID: 18494 (worker_thread_2) | Стан: S
      Перемикання контексту: добровільні=794, примусові=3
      Символ wchan: futex_wait_queue_me
      Системний виклик: #202 (futex)
      -> Блокування FUTEX на адресі: 0x7fff8020 (op=0x80, val=2)

  [+] Потік TID: 18495 (network_client) | Стан: S
      Перемикання контексту: добровільні=120, примусові=1
      Символ wchan: sk_wait_data
      Системний виклик: #0 (read)
      -> Блокування на FD 9: socket:[5192014]
```

Отриманий зріз дає змогу негайно зробити кілька важливих технічних висновків:
* Потік `18492` є головним диспетчером подій (`main_event_loop`), що очікує нових клієнтів через системний виклик `epoll_wait` на дескрипторі epoll-інстансу `anon_inode:[eventpoll]`.
* Потоки `18493` та `18494` заблоковані на взаємному очікуванні користувацьких м'ютексів на адресах `0x7fff8040` та `0x7fff8020`. Обидва сплять усередині функції ядра `futex_wait_queue_me`.
* Потік `18495` заблокований на синхронному читанні із сокета з дескриптором `9` та inode `5192014`.

## 4. Підводні камені, паралелізм та крайові випадки

Під час експлуатації утиліти в реальних середовищах слід враховувати важливі особливості роботи віртуальної файлової системи Linux:

### Стан гонитви під час ітерації потоків (Concurrent Thread Teardown)

У багатопотокових програмах короткоживучі потоки можуть створюватися та знищуватися сотні разів на секунду. Якщо потік завершує роботу під час того, як утиліта зчитує каталог `/proc/[pid]/task/`, системний виклик `readdir()` встигне повернути числовий ідентифікатор `TID`, але наступна спроба відкрити псевдофайли `status`, `wchan` або `stack` завершиться помилкою `ENOENT` (файл або каталог не існує).

Утиліта спроєктована з урахуванням цього сценарію: помилка відкриття окремого псевдофайлу не призводить до переривання всієї програми, а обробляється як штатна подія динамічної зміни структури завдань.

### Безпека читання псевдофайлу syscall

Псевдофайл `/proc/[pid]/syscall` є атомарним зрізом регістрового стану завдання. Якщо потік перебуває в режимі виконання коду користувача (`TASK_RUNNING`), перший символ у файлі може бути `r` (рядок `running`) або `-1`. Спроба безпосереднього розбору шістнадцяткових чисел у такому стані спричинить помилку формату. Утиліта перевіряє перший символ рядка і коректно ідентифікує стан `RUNNING_IN_USERSPACE`.

### Робота з символічними посиланнями дескрипторів

Символічні посилання в каталозі `/proc/[pid]/fd/` не є звичайними файловими посиланнями на диску. Вони існують виключно у віртуальній пам'яті ядра і генеруються підсистемою VFS на основі внутрішніх структур `struct file`. Системний виклик `readlink()` для сокетів та каналів повертає спеціальні системні рядки виду `socket:[inode]` або `pipe:[inode]`. Для анонімних дескрипторів підсистем ядра виводяться назви на кшталт `anon_inode:[eventpoll]`, `anon_inode:[signalfd]` або `anon_inode:[eventfd]`.

### Порівняння продуктивності: prochook проти ptrace

Традиційне трасування через `strace -p` або підключення `gdb -p` виконує системний виклик `ptrace(PTRACE_ATTACH)`. Це призводить до надсилання цільовому процесу сигналу `SIGSTOP`, примусової зупинки всіх робочих ниток, перемикання контексту ядра та сповіщення трейсера через `waitpid()`. На високонавантажених сервісах із тисячами активних з'єднань така затримка тривалістю навіть у 50–100 мілісекунд призводить до переповнення черги `ListenBacklog`, скидання TCP-сесій клієнтами та помилок моніторингу.

Утиліта `prochook` виконує виключно операції пасивного читання пам'яті структур ядра через VFS. Цільовий процес не отримує сигналів, не зупиняється на жодну мікросекунду і продовжує обслуговувати трафік із нульовим оверхедом продуктивності.
