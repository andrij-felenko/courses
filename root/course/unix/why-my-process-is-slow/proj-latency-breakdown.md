# ⚙️ Профілювальник бюджету часу задачі на основі procfs

Коли служба чи окремий процес починає відповідати із затримкою, стандартні системні монітори на кшталт `top` або `htop` показують лише миттєвий або усереднений відсоток завантаження процесора. Якщо цей відсоток низький, розробник часто робить поспішний і хибний висновок, що процес «нічого не робить і просто чекає на клієнтів». Насправді ж процес може перебувати у стані жорсткої конкуренції за процесорні ядра в черзі планувальника, щомиті витіснятися іншими задачами, страждати від прихованого тротлінгу в cgroups або безперервно блокуватися на м'ютексах і дискових сторінкових збоях.

Цей практичний проект демонструє побудову повноцінного, неінвазивного інструменту системної діагностики. Утиліта підключається до будь-якого запущеного процесу за його числовим ідентифікатором (`PID`) і розкладає кожну секунду реального астрономічного часу (`Wall-Clock Time`) на чотири фундаментальні складові: виконання прикладного коду у просторі користувача, виконання системних викликів у просторі ядра, затримку в черзі планувальника та час блокування поза процесором.

## Постановка задачі та модель вимірювань

Традиційні підходи до вимірювання затримок зазвичай поділяються на дві крайності. Перша — використання важких профілювальників із семплюванням стека (`perf record`), які створюють помітні накладні витрати на копіювання стеків викликів і генерують гігабайти трасувальних даних. Друга — періодичний перегляд утиліти `top`, яка агрегує лише час перебування на процесорі і повністю ігнорує фази очікування.

Мета цього проекту — створити легку утиліту нульового впливу (zero-overhead profiler), яка працює виключно через інтерфейси ядра `/proc/[pid]/stat`, `/proc/[pid]/schedstat` та `/proc/[pid]/status`. Завдяки цьому інструмент не зупиняє цільовий процес, не використовує системний виклик `ptrace`, не змінює поведінку планувальника і може безпечно застосовуватися на високонавантажених серверах у промисловому середовищі.

Для заданого процесу із заданим періодом спостереження `Δt` (наприклад, одна секунда) утиліта збирає та обчислює такі метрики:

1. **Астрономічний час інтервалу (`Δwall`)** — реальний час, що минув між двома послідовними замірами, виміряний за допомогою монотонного системного годинника `CLOCK_MONOTONIC`. Монотонний таймер гарантує захист від стрибків часу, викликаних синхронізацією через NTP або ручним переведенням годинника.
2. **Час у просторі користувача (`Δutime`)** — час виконання прикладного коду процесу, бібліотек та алгоритмічних обчислень, зчитаний із поля 14 файлу `/proc/[pid]/stat`.
3. **Час у просторі ядра (`Δstime`)** — час обслуговування системних викликів, обробки сторінкових збоїв та мережевих пакетів від імені даного процесу, зчитаний із поля 15 файлу `/proc/[pid]/stat`.
4. **Час очікування в черзі планувальника (`Δsched_wait`)** — затримка між моментом, коли задача була пробуджена або стала готовою до виконання, і моментом фактичного надання їй процесорного ядра, зчитана з другого поля файлу `/proc/[pid]/schedstat`.
5. **Час блокування поза процесором (`Δoff_cpu_wait`)** — час, протягом якого задача добровільно поступилася процесором через очікування вводу-виводу, сокетів, таймерів або блокувань м'ютексів.
6. **Частоту перемикань контексту** — кількість добровільних (`voluntary`) та примусових (`nonvoluntary`) передач процесора за секунду, зчитана з файлу `/proc/[pid]/status`.
7. **Сторінкові збої пам'яті** — приріст незначних (`minflt`) та значних (`majflt`) збоїв сторінок віртуальної пам'яті.

Зв'язок між виміряними величинами описується балансовим рівнянням розподілу бюджету часу процесу:

```
Δwall = Δutime + Δstime + Δsched_wait + Δoff_cpu_wait
```

Аналіз пропорцій у цьому рівнянні дозволяє однозначно класифікувати природу затримок:

* Якщо переважає сума `(Δutime + Δstime)` і вона наближається до `Δwall`, процес повністю завантажує виділене ядро (CPU-bound). Вузьке місце знаходиться в алгоритмах коду або накладних витратах системних викликів.
* Якщо переважає величина `Δsched_wait`, процес страждає від нестачі обчислювальної потужності системи (Scheduler Starvation). Задача повністю готова виконувати інструкції, але планувальник змушений тримати її в черзі через зайнятість усіх ядер іншими задачами або занижений пріоритет `nice`.
* Якщо переважає величина `Δoff_cpu_wait`, процес обмежений зовнішніми блокуваннями (Off-CPU-bound). Якщо при цьому спостерігається велика кількість `majflt`, процес блокується на читанні сторінок із диска. Якщо зростає частота добровільних перемикань, процес блокується на очікуванні м'ютексів чи мережевих відповідей.

## Реалізація утиліти діагностики

Нижче наведено повні та готові до компіляції реалізації утиліти мовами C та C++. Обидві програми виконують періодичне зчитування лічильників ядра, обчислюють дельти показників та виводять структурований звіт із автоматичною діагностикою вузького місця.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <errno.h>

typedef struct {
    unsigned long long utime_ticks;
    unsigned long long stime_ticks;
    unsigned long long minflt;
    unsigned long long majflt;
    unsigned long long sched_cpu_ns;
    unsigned long long sched_wait_ns;
    unsigned long long sched_switches;
    unsigned long long vol_ctxt;
    unsigned long long nonvol_ctxt;
    struct timespec timestamp;
} ProcessMetrics;

static double timespec_diff_sec(const struct timespec *start, const struct timespec *end) {
    return (double)(end->tv_sec - start->tv_sec) +
           (double)(end->tv_nsec - start->tv_nsec) / 1e9;
}

static int read_proc_stat(pid_t pid, ProcessMetrics *m) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/stat", pid);
    FILE *f = fopen(path, "r");
    if (!f) return -1;

    char buffer[2048];
    if (!fgets(buffer, sizeof(buffer), f)) {
        fclose(f);
        return -1;
    }
    fclose(f);

    /* Знаходимо останню закриваючу дужку для безпечного парсингу після назви процесу */
    char *paren = strrchr(buffer, ')');
    if (!paren) return -1;

    char state;
    int ppid, pgrp, session, tty_nr, tpgid;
    unsigned int flags;

    int matched = sscanf(paren + 2,
        "%c %d %d %d %d %d %u %llu %*u %llu %*u %llu %llu",
        &state, &ppid, &pgrp, &session, &tty_nr, &tpgid,
        &flags, &m->minflt, &m->majflt, &m->utime_ticks, &m->stime_ticks);

    return (matched >= 11) ? 0 : -1;
}

static int read_proc_schedstat(pid_t pid, ProcessMetrics *m) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/schedstat", pid);
    FILE *f = fopen(path, "r");
    if (!f) return -1;

    int matched = fscanf(f, "%llu %llu %llu",
                         &m->sched_cpu_ns, &m->sched_wait_ns, &m->sched_switches);
    fclose(f);
    return (matched == 3) ? 0 : -1;
}

static int read_proc_status(pid_t pid, ProcessMetrics *m) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/status", pid);
    FILE *f = fopen(path, "r");
    if (!f) return -1;

    char line[256];
    m->vol_ctxt = 0;
    m->nonvol_ctxt = 0;

    while (fgets(line, sizeof(line), f)) {
        if (strncmp(line, "voluntary_ctxt_switches:", 24) == 0) {
            sscanf(line + 24, "%llu", &m->vol_ctxt);
        } else if (strncmp(line, "nonvoluntary_ctxt_switches:", 27) == 0) {
            sscanf(line + 27, "%llu", &m->nonvol_ctxt);
        }
    }
    fclose(f);
    return 0;
}

static int collect_metrics(pid_t pid, ProcessMetrics *m) {
    if (read_proc_stat(pid, m) != 0) return -1;
    if (read_proc_schedstat(pid, m) != 0) {
        m->sched_cpu_ns = 0;
        m->sched_wait_ns = 0;
        m->sched_switches = 0;
    }
    if (read_proc_status(pid, m) != 0) return -1;
    clock_gettime(CLOCK_MONOTONIC, &m->timestamp);
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <PID> [інтервал_секунд]\n", argv[0]);
        return 1;
    }

    pid_t pid = (pid_t)atoi(argv[1]);
    int interval_sec = (argc >= 3) ? atoi(argv[2]) : 1;
    if (interval_sec < 1) interval_sec = 1;

    long clk_tck = sysconf(_SC_CLK_TCK);
    if (clk_tck <= 0) clk_tck = 100;

    ProcessMetrics prev, curr;
    if (collect_metrics(pid, &prev) != 0) {
        fprintf(stderr, "Помилка доступу до процесу з PID %d: %s\n", pid, strerror(errno));
        return 1;
    }

    printf("Моніторинг бюджету часу для PID %d (CLK_TCK=%ld, інтервал=%d с)...\n",
           pid, clk_tck, interval_sec);
    printf("--------------------------------------------------------------------------------\n");

    while (1) {
        sleep((unsigned int)interval_sec);
        if (collect_metrics(pid, &curr) != 0) {
            printf("Процес %d завершився або став недоступним.\n", pid);
            break;
        }

        double dt = timespec_diff_sec(&prev.timestamp, &curr.timestamp);
        if (dt <= 0.0) dt = 0.001;

        double utime_sec = (double)(curr.utime_ticks - prev.utime_ticks) / (double)clk_tck;
        double stime_sec = (double)(curr.stime_ticks - prev.stime_ticks) / (double)clk_tck;
        double sched_wait_sec = (double)(curr.sched_wait_ns - prev.sched_wait_ns) / 1e9;
        
        double cpu_total_sec = utime_sec + stime_sec;
        double off_cpu_sec = dt - cpu_total_sec - sched_wait_sec;
        if (off_cpu_sec < 0.0) off_cpu_sec = 0.0;

        double user_pct = (utime_sec / dt) * 100.0;
        double sys_pct  = (stime_sec / dt) * 100.0;
        double wait_pct = (sched_wait_sec / dt) * 100.0;
        double off_pct  = (off_cpu_sec / dt) * 100.0;

        unsigned long long vol_diff = curr.vol_ctxt - prev.vol_ctxt;
        unsigned long long nonvol_diff = curr.nonvol_ctxt - prev.nonvol_ctxt;
        unsigned long long minflt_diff = curr.minflt - prev.minflt;
        unsigned long long majflt_diff = curr.majflt - prev.majflt;

        printf("[Δt=%.2fs] CPU: usr=%.1f%% sys=%.1f%% | SchedWait=%.1f%% | OffCPU=%.1f%% | Ctxt: vol=%llu/s nonvol=%llu/s | Flt: min=%llu maj=%llu\n",
               dt, user_pct, sys_pct, wait_pct, off_pct,
               (unsigned long long)(vol_diff / dt),
               (unsigned long long)(nonvol_diff / dt),
               minflt_diff, majflt_diff);

        /* Автоматична діагностика вузького місця */
        if (user_pct > 60.0) {
            printf("  ↳ ДІАГНОЗ: CPU-Bound (User). Гарячі цикли або обчислення в коді програми.\n");
        } else if (sys_pct > 40.0) {
            printf("  ↳ ДІАГНОЗ: System-Bound. Надмірна кількість системних викликів або сторінкових збоїв.\n");
        } else if (wait_pct > 20.0) {
            printf("  ↳ ДІАГНОЗ: Scheduler Starvation. Процес чекає черги до процесора через нестачу ядер.\n");
        } else if (majflt_diff > 10) {
            printf("  ↳ ДІАГНОЗ: Paging / Swap Bottleneck. Часті значні сторінкові збої з диска.\n");
        } else if (off_pct > 70.0 && vol_diff > 1000) {
            printf("  ↳ ДІАГНОЗ: High Concurrency / I/O Blocking. Часті добровільні блокування на сокетах або м'ютексах.\n");
        } else if (off_pct > 70.0) {
            printf("  ↳ ДІАГНОЗ: Idle / Sleep. Процес здебільшого спить або чекає зовнішніх подій.\n");
        }

        prev = curr;
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <chrono>
#include <thread>
#include <vector>
#include <optional>
#include <iomanip>
#include <unistd.h>

struct ProcessMetrics {
    unsigned long long utime_ticks{0};
    unsigned long long stime_ticks{0};
    unsigned long long minflt{0};
    unsigned long long majflt{0};
    unsigned long long sched_cpu_ns{0};
    unsigned long long sched_wait_ns{0};
    unsigned long long sched_switches{0};
    unsigned long long vol_ctxt{0};
    unsigned long long nonvol_ctxt{0};
    std::chrono::steady_clock::time_point timestamp{};
};

class ProcessProfiler {
public:
    explicit ProcessProfiler(pid_t pid, long clk_tck = 100)
        : pid_{pid}, clk_tck_{clk_tck > 0 ? clk_tck : 100} {}

    [[nodiscard]] std::optional<ProcessMetrics> sample() const {
        ProcessMetrics m;
        m.timestamp = std::chrono::steady_clock::now();

        if (!readStat(m) || !readStatus(m)) {
            return std::nullopt;
        }
        readSchedstat(m); // Може бути відсутній без CONFIG_SCHEDSTATS
        return m;
    }

    void printReport(const ProcessMetrics& prev, const ProcessMetrics& curr) const {
        const auto duration_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(
            curr.timestamp - prev.timestamp).count();
        const double dt = static_cast<double>(duration_ns) / 1e9;
        if (dt <= 0.0) return;

        const double utime_sec = static_cast<double>(curr.utime_ticks - prev.utime_ticks) / static_cast<double>(clk_tck_);
        const double stime_sec = static_cast<double>(curr.stime_ticks - prev.stime_ticks) / static_cast<double>(clk_tck_);
        const double sched_wait_sec = static_cast<double>(curr.sched_wait_ns - prev.sched_wait_ns) / 1e9;

        const double cpu_total = utime_sec + stime_sec;
        double off_cpu_sec = dt - cpu_total - sched_wait_sec;
        if (off_cpu_sec < 0.0) off_cpu_sec = 0.0;

        const double user_pct = (utime_sec / dt) * 100.0;
        const double sys_pct  = (stime_sec / dt) * 100.0;
        const double wait_pct = (sched_wait_sec / dt) * 100.0;
        const double off_pct  = (off_cpu_sec / dt) * 100.0;

        const auto vol_diff = curr.vol_ctxt - prev.vol_ctxt;
        const auto nonvol_diff = curr.nonvol_ctxt - prev.nonvol_ctxt;
        const auto minflt_diff = curr.minflt - prev.minflt;
        const auto majflt_diff = curr.majflt - prev.majflt;

        std::cout << std::fixed << std::setprecision(1)
                  << "[Δt=" << dt << "s] CPU: usr=" << user_pct << "% sys=" << sys_pct
                  << "% | SchedWait=" << wait_pct << "% | OffCPU=" << off_pct
                  << "% | Ctxt: vol=" << static_cast<unsigned long long>(vol_diff / dt)
                  << "/s nonvol=" << static_cast<unsigned long long>(nonvol_diff / dt)
                  << "/s | Flt: min=" << minflt_diff << " maj=" << majflt_diff << "\n";

        diagnose(user_pct, sys_pct, wait_pct, off_pct, vol_diff, majflt_diff);
    }

private:
    pid_t pid_;
    long clk_tck_;

    bool readStat(ProcessMetrics& m) const {
        std::ifstream file("/proc/" + std::to_string(pid_) + "/stat");
        if (!file.is_open()) return false;

        std::string content;
        std::getline(file, content);

        const auto close_paren = content.rfind(')');
        if (close_paren == std::string::npos || close_paren + 2 >= content.size()) {
            return false;
        }

        std::istringstream stream(content.substr(close_paren + 2));
        char state;
        int ppid, pgrp, session, tty_nr, tpgid;
        unsigned int flags;
        unsigned long long cminflt, cmajflt;

        if (stream >> state >> ppid >> pgrp >> session >> tty_nr >> tpgid
                   >> flags >> m.minflt >> cminflt >> m.majflt >> cmajflt
                   >> m.utime_ticks >> m.stime_ticks) {
            return true;
        }
        return false;
    }

    void readSchedstat(ProcessMetrics& m) const {
        std::ifstream file("/proc/" + std::to_string(pid_) + "/schedstat");
        if (file.is_open()) {
            file >> m.sched_cpu_ns >> m.sched_wait_ns >> m.sched_switches;
        }
    }

    bool readStatus(ProcessMetrics& m) const {
        std::ifstream file("/proc/" + std::to_string(pid_) + "/status");
        if (!file.is_open()) return false;

        std::string line;
        while (std::getline(file, line)) {
            if (line.rfind("voluntary_ctxt_switches:", 0) == 0) {
                m.vol_ctxt = std::stoull(line.substr(24));
            } else if (line.rfind("nonvoluntary_ctxt_switches:", 0) == 0) {
                m.nonvol_ctxt = std::stoull(line.substr(27));
            }
        }
        return true;
    }

    static void diagnose(double user_pct, double sys_pct, double wait_pct, double off_pct,
                         unsigned long long vol_diff, unsigned long long majflt_diff) {
        if (user_pct > 60.0) {
            std::cout << "  ↳ ДІАГНОЗ: CPU-Bound (User). Гарячі цикли або обчислення в коді програми.\n";
        } else if (sys_pct > 40.0) {
            std::cout << "  ↳ ДІАГНОЗ: System-Bound. Надмірна кількість системних викликів або сторінкових збоїв.\n";
        } else if (wait_pct > 20.0) {
            std::cout << "  ↳ ДІАГНОЗ: Scheduler Starvation. Процес чекає черги до процесора через нестачу ядер.\n";
        } else if (majflt_diff > 10) {
            std::cout << "  ↳ ДІАГНОЗ: Paging / Swap Bottleneck. Часті значні сторінкові збої з диска.\n";
        } else if (off_pct > 70.0 && vol_diff > 1000) {
            std::cout << "  ↳ ДІАГНОЗ: High Concurrency / I/O Blocking. Часті добровільні блокування на сокетах або м'ютексах.\n";
        } else if (off_pct > 70.0) {
            std::cout << "  ↳ ДІАГНОЗ: Idle / Sleep. Процес здебільшого спить або чекає зовнішніх подій.\n";
        }
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <PID> [інтервал_секунд]\n";
        return 1;
    }

    const pid_t pid = static_cast<pid_t>(std::stoi(argv[1]));
    const int interval_sec = (argc >= 3) ? std::max(1, std::stoi(argv[2])) : 1;
    const long clk_tck = sysconf(_SC_CLK_TCK);

    ProcessProfiler profiler(pid, clk_tck);
    auto prev = profiler.sample();
    if (!prev) {
        std::cerr << "Помилка доступу до процесу з PID " << pid << "\n";
        return 1;
    }

    std::cout << "Моніторинг бюджету часу для PID " << pid
              << " (CLK_TCK=" << clk_tck << ", інтервал=" << interval_sec << " с)...\n";
    std::cout << "--------------------------------------------------------------------------------\n";

    while (true) {
        std::this_thread::sleep_for(std::chrono::seconds(interval_sec));
        auto curr = profiler.sample();
        if (!curr) {
            std::cout << "Процес " << pid << " завершився або став недоступним.\n";
            break;
        }

        profiler.printReport(*prev, *curr);
        prev = curr;
    }

    return 0;
}
```
:::

## Збирання та компіляція

Для компіляції розробленого коду у середовищі Linux використовують стандартні компілятори GCC або Clang. Оскільки програма взаємодіє виключно зі стандартними інтерфейсами POSIX та бібліотекою libc, жодних зовнішніх залежностей чи додаткових бібліотек не потрібно.

```sh
# Компіляція C версії
gcc -O2 -Wall -Wextra -D_GNU_SOURCE profiler.c -o proc_profiler

# Компіляція C++ версії (вимагає C++20 або новішого)
g++ -O2 -Wall -Wextra -std=c++20 profiler.cpp -o proc_profiler_cpp
```

Запуск програми здійснюється передачею PID цільового процесу першим аргументом. Необов'язковий другий аргумент задає інтервал оновлення в секундах:

```sh
./proc_profiler $(pgrep -f my_service) 1
```

## Аналіз поведінки на практичних сценаріях навантаження

Щоб верифікувати правильність розкладання бюджету часу, розглянемо вивід розробленої утиліти під чотирма типовими моделями синтетичного навантаження, які часто зустрічаються у практичній експлуатації систем.

### Сценарій 1: Обчислювальний процес (CPU-Bound)

Запустимо тестову програму, що виконує інтенсивні математичні обчислення (наприклад, перемноження великих матриць, факторіали або хешування SHA-256) у нескінченному циклі без системних викликів.

```
[Δt=1.00s] CPU: usr=98.5% sys=0.5% | SchedWait=0.8% | OffCPU=0.2% | Ctxt: vol=2/s nonvol=120/s | Flt: min=0 maj=0
  ↳ ДІАГНОЗ: CPU-Bound (User). Гарячі цикли або обчислення в коді програми.
```

**Аналіз механізму:** Користувацький час займає 98.5% бюджету. Кількість примусових перемикань (`nonvol=120/s`) показує, що процес регулярно вичерпує свій виділений квант часу і витісняється планувальником EEVDF/CFS для надання процесора іншим задачам. Затримка черги є мінімальною (`0.8%`), що свідчить про достатню кількість процесорних ядер у системі.

У цьому випадку пошук причини затримки має здійснюватися виключно всередині коду користувача: необхідно запустити профілювальник стека `perf top` або зняти флеймграф за допомогою `perf record -F 99 -g -p <PID>`, щоб знайти конкретні функції, гарячі цикли або структури даних із неефективним доступом до кеш-пам'яті.

### Сценарій 2: Шторм системних викликів (System-Bound)

Запустимо програму, яка виконує мільйони дрібних операцій читання файлу по одному байту через системний виклик `read(fd, &byte, 1)` або безперервно запитує системний час чи ідентифікатор процесу `getpid()`.

```
[Δt=1.00s] CPU: usr=14.2% sys=84.1% | SchedWait=1.1% | OffCPU=0.6% | Ctxt: vol=4/s nonvol=98/s | Flt: min=0 maj=0
  ↳ ДІАГНОЗ: System-Bound. Надмірна кількість системних викликів або сторінкових збоїв.
```

**Аналіз механізму:** Час у режимі ядра займає 84.1% бюджету. Процесор витрачає майже всю свою потужність не на корисну логіку застосунку, а на збереження регістрів, перемикання кілець захисту процесора (Ring 3 -> Ring 0), валідацію вхідних аргументів у таблиці системних викликів та повернення назад у простір користувача.

Для виправлення такого вузького місця системний аналітик повинен запустити `strace -c -p <PID>` або `perf trace -p <PID>`, щоб виявити найбільш частотні системні виклики. Рішення полягає у переході на буферизований ввід-вивід (наприклад, використання `fread` замість небуферизованого `read`), агрегації викликів через векторні інтерфейси `readv`/`writev` або переході на сучасний асинхронний інтерфейс `io_uring`.

### Сценарій 3: Конкуренція за процесор (Scheduler Starvation)

Запустимо обчислювальний процес із низьким пріоритетом (`nice +19`) на системі, де всі інші фізичні ядра на 100% завантажені іншими задачами з вищим або нормальним пріоритетом (`nice 0`).

```
[Δt=1.00s] CPU: usr=18.4% sys=0.2% | SchedWait=79.1% | OffCPU=2.3% | Ctxt: vol=1/s nonvol=34/s | Flt: min=0 maj=0
  ↳ ДІАГНОЗ: Scheduler Starvation. Процес чекає черги до процесора через нестачу ядер.
```

**Аналіз механізму:** Якщо подивитися на такий процес через звичайний монітор `top`, він покаже лише 18% використання CPU. Недосвідчений інженер вирішить, що процес виконує мало роботи або навантаження зменшилося. Проте профілювальник показує, що параметр `SchedWait` сягає 79.1%.

Це означає, що понад три чверті реального астрономічного часу процес провів у стані повної готовності `TASK_RUNNING`, очікуючи у черзі виконання `runqueue`, поки планувальник виділить йому процесорне ядро. Оскільки вага задачі з `nice +19` значно менша за вагу нормальних задач, планувальник надає їй процесор лише на короткі проміжки часу. Шляхи вирішення: підвищення пріоритету через `renice -n -5 -p <PID>`, ізоляція процесу на виділені ядра через `taskset -c 0,1` або збільшення лімітів CPU у конфігурації контейнера.

### Сценарій 4: Конфлікт блокувань або очікування сокета (Off-CPU Blocked)

Запустимо багатопотоковий мережевий сервер, у якому 32 паралельні нитки постійно борються за один спільний глобальний м'ютекс `pthread_mutex_t` під час обробки кожного запиту.

```
[Δt=1.00s] CPU: usr=4.1% sys=3.8% | SchedWait=2.0% | OffCPU=90.1% | Ctxt: vol=34200/s nonvol=12/s | Flt: min=0 maj=0
  ↳ ДІАГНОЗ: High Concurrency / I/O Blocking. Часті добровільні блокування на сокетах або м'ютексах.
```

**Аналіз механізму:** Процес споживає сумарно лише 8% потужності процесора, але користувачі скаржаться на колосальні затримки відповідей. Частка `OffCPU` перевищує 90%, а лічильник добровільних перемикань контексту генерує понад 34 000 подій на секунду.

Нитки постійно намагаються захопити зайнятий м'ютекс, переходять у ядро через системний виклик `futex(FUTEX_WAIT)` і добровільно засинають, звільняючи процесор. Звичайні профілювальники CPU тут цілком сліпі, оскільки під час очікування м'ютекса інструкції процесора взагалі не виконуються. Для локалізації конкретного рядка коду, де виникає затор, необхідно застосовувати інструменти Off-CPU аналізу: трасування затримок сну через `offcputime-bpfcc` або аналіз стеків викликів сплячих ниток через `pstack <PID>`.

## Практичні тонкощі та розширення інструменту

Під час побудови виробничих систем моніторингу затримок на основі ядра Linux слід враховувати кілька важливих архітектурних нюансів:

### 1. Агрегація багатопотокових процесів (PID проти TID)

У ядрі Linux кожен потік виконання є окремою задачею `task_struct` із власним унікальним числовим ідентифікатором нитки (`TID`). Файл `/proc/[pid]/stat` для головного процесу відображає агреговані або індивідуальні лічильники головного потоку.

Якщо в застосунку одна робоча нитка завантажена на 100%, а решта 15 ниток пулу сплять у черзі очікування завдань, опитування лише головного `PID` дасть розмиту середню картину. Для повної діагностики багатопотокового процесу утиліта повинна відкривати каталог `/proc/[pid]/task/`, ітерувати всі підкаталоги `[tid]` і підсумовувати лічильники окремо для кожної активної нитки. При цьому слід коректно обробляти стан гонитви (race condition): якщо короткоживуча нитка завершується під час читання її файлу, спроба відкрити `stat` поверне помилку `ENOENT`, яку програма повинна безпечно проігнорувати.

### 2. Дискретність обліку системних тактів (`USER_HZ`)

Показники `utime` та `stime` у файлі `/proc/[pid]/stat` квантуються з точністю до системного таймера (як правило, 100 Гц = 10 мс на такт). Якщо проводити вимірювання на надкоротких інтервалах (наприклад, кожні 50 мс), похибка дискретизації може досягати 20–40%.

На відміну від `stat`, файл `/proc/[pid]/schedstat` містить безпосередні наносекундні лічильники планувальника, які оновлюються апаратними регістрами `TSC` (Time Stamp Counter) при кожній зміні задачі на ядрі. Тому для високочастотного моніторингу метрика `schedstat` є значно точнішою. У ядрах із підтримкою безтикового режиму (`CONFIG_NO_HZ_FULL=y`) ядро зупиняє періодичні переривання таймера на ізольованих ядрах, коли там виконується єдина задача, тому лічильники тактів оновлюються лише під час системних викликів або перемикань.

### 3. Робота в контейнеризованих середовищах

Усередині контейнерів Docker або Kubernetes простір імен `/proc` монтується із хостової операційної системи. Якщо для контейнера встановлено ліміт `resources.limits.cpu`, планувальник cgroups v2 застосовує механізм тротлінгу через контролер `cpu.max`.

У такому разі час штучної затримки процесу фіксується не у файлі `schedstat`, а у файлі `/sys/fs/cgroup/cpu.stat` у вигляді показників `nr_throttled` та `throttled_usec`. Повноцінний профілювальник контейнера повинен поєднувати зчитування `schedstat` для виявлення черг із перевіркою `cpu.stat` для виявлення квотних обмежень.

### 4. Вплив динамічної частоти процесора (CPU Frequency Scaling)

Сучасні процесори динамічно змінюють робочу тактову частоту залежно від навантаження та теплового пакета. Якщо під час моніторингу ядро процесора працювало на енергозберігаючій частоті 800 МГц замість максимальної турбо-частоти 4.5 ГГц, один і той самий обсяг коду виконуватиметься у 5 разів довше в наносекундах. Для виключення впливу регуляторів енергозбереження під час вимірювань перевіряють файл `/sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq`.

### 5. Топологія NUMA та міграція між вузлами

На багатопроцесорних серверах із неоднорідним доступом до пам'яті (NUMA) процес, що мігрує між різними сокетами процесора, стикається з раптовим зростанням затримок читання RAM. Коли ядро планувальника переносить задачу на ядро віддаленого NUMA-вузла, кожне звернення до пам'яті вимагає проходження міжпроцесорної шини (UPI або Infinity Fabric), що збільшує затримку доступу в 2.5–3 рази.

Поле 39 файлу `/proc/[pid]/stat` повертає номер поточного процесора `processor`. Відстежуючи зміни цього номера у часі та зіставляючи його з картою NUMA-вузлів у `/sys/devices/system/node/node*/cpulist`, діагностичний інструмент може виявляти часті міжвузлові міграції (cross-node bounce) і рекомендувати жорстку прив'язку процесу через утиліту `numactl --cpunodebind=... --membind=...`.

### 6. Інтеграція у виробничий моніторинг

Розглянутий підхід до декомпозиції часу легко інтегрується у системи неперервної телеметрії. Замість виводу в консоль структура даних `ProcessMetrics` може експортуватися у форматі Prometheus-метрик або відправлятися у брокери повідомлень:

* `process_cpu_seconds_total{mode="user"}` — сумарний час коду застосунку;
* `process_cpu_seconds_total{mode="system"}` — сумарний час системних викликів та ядра;
* `process_sched_wait_seconds_total` — сумарний час очікування в черзі планувальника;
* `process_context_switches_total{type="voluntary"}` — кількість добровільних блокувань;
* `process_context_switches_total{type="nonvoluntary"}` — кількість примусових витіснень.

### 7. Порівняння підходів: procfs проти eBPF

Опитування псевдофайлової системи `/proc` є найпростішим і найбільш переносним способом моніторингу. Воно працює на будь-якому дистрибутиві Linux без потреби у налагоджувальних символах, завантаженні модулів чи компіляції байт-коду. Головне обмеження підходу полягає в тому, що він дає агреговані цифри за секунду, але не показує конкретні стеки викликів.

Сучасні системи спостереження часто комбінують ці рівні: легкий фоновий демон на основі `/proc` веде постійний підрахунок бюджету часу із мінімальними накладними витратами (менше 0.01% CPU), а в разі фіксації аномалії (наприклад, різкого стрибка `OffCPU` або `SchedWait`) автоматично підключає зонди eBPF (`offcputime`, `runqlat`) на 10–15 секунд для точкового збору стеків викликів і встановлення винуватця затримки.

### 8. Синтетичне тестування та калібрування з stress-ng

Для перевірки правильності класифікації утиліти в тестових лабораторних умовах рекомендується використовувати генератор системного навантаження `stress-ng`. Він дозволяє ізольовано створювати будь-який із чотирьох станів:

* Тестування `CPU-Bound`: `stress-ng --cpu 1 --cpu-method matrixprod --timeout 30s` генерує чисте користувацьке навантаження (%usr > 95%).
* Тестування `System-Bound`: `stress-ng --getpid 1 --timeout 30s` навантажує таблицю системних викликів ядра (%sys > 80%).
* Тестування `Scheduler Starvation`: `stress-ng --cpu $(nproc) --nice 19 --timeout 30s` паралельно з іншим пріоритетним процесом провокує зростання затримки черги (%SchedWait > 60%).
* Тестування `I/O Blocking`: `stress-ng --sync-file 1 --timeout 30s` переводить нитки в стан блокування на диску (OffCPU > 85%, majflt зростає).


### 9. Вплив одночасної багатопотоковості (SMT / Hyper-Threading)

На процесорах із підтримкою SMT (Hyper-Threading) кожне фізичне ядро представлене двома логічними процесорами, які спільно використовують конвеєр інструкцій, кеш L1/L2 та виконавчі блоки ALU/FPU. Якщо на сусідньому логічному потоці того самого ядра виконується важкий векторний код AVX-512, цільовий процес формально отримує 100% часу на своєму логічному ядрі, проте його реальний темп виконання сповільнюється через апаратну конкуренцію за виконавчі порти. Для діагностики таких аномалій перевіряють топологію у файлі `/sys/devices/system/cpu/cpu*/topology/thread_siblings_list`.




