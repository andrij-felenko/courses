# ⚙️ Монітор асинхронного та прямого витіснення сторінок

Ця вставка містить практичну програму моніторингу затримок та ефективності витіснення сторінок у ядрі Linux. Програма зчитує системні лічильники з псевдо-файлової системи `/proc/vmstat`, обчислює дельти за фіксований часовий інтервал і виявляє ситуації, коли операційна система виходить з безпечного асинхронного режиму `kswapd` і провалюється в синхронні затримки Direct Reclaim (`allocstall`). Її варто відкрити для діагностики раптових спалахів затримок (latency spikes) на продакшн-серверах та під час проведення бенчмарків.

## Архітектура та мета моніторингу

Головним завданням асинхронного витіснення сторінок є абсолютне приховування затримок дискового вводу-виводу та впорядкування пам'яті від процесів користувача. Коли демон `kswapd` працює ефективно й завчасно реагує на падіння вільної пам'яті нижче порогу `WMARK_LOW`, зростають лише лічильники `pgscan_kswapd` та `pgsteal_kswapd`, а лічильник затримок процесів `allocstall` не приростає жодного разу.

Однак при недостатньому значенні `vm.min_free_kbytes` або занадто стрімкому сплеску аллокацій резервний зазор виснажується. Процеси користувача пробивають поріг `WMARK_MIN` і потрапляють у режим Direct Reclaim. У цей момент потік користувача зупиняє своє виконання і змушений самостійно сканувати списки LRU та чекати скидання брудних сторінок на диск.

Для точної фіксації цих деструктивних явищ утиліта моніторингу зчитує `/proc/vmstat` та розраховує наступні ключові показники:

1. **Інтенсивність сканування kswapd (`pgscan_kswapd/s`):** Кількість сторінок на секунду, які фоновий демон просканував у списках LRU.
2. **Інтенсивність прямого сканування (`pgscan_direct/s`):** Кількість сторінок на секунду, просканованих безпосередньо процесами користувача під час перебування в затримках.
3. **Ефективність асинхронного витіснення (kswapd Efficiency Ratio):** Відсоток успішно вивільнених сторінок від відсканованих:
   `Efficiency = (Δpgsteal_kswapd / Δpgscan_kswapd) · 100%`
4. **Частота затримок аллокацій (Stalls per second):** Кількість викликів Direct Reclaim за секунду (`Δallocstall`). Будь-яке значення, більше за нуль, свідчить про виникнення затримок додатків.

## Внутрішній механізм лічильників ядра (/proc/vmstat)

Усі лічильники витіснення в ядрі Linux оновлюються на кожному процесорному ядрі локально у масивах `struct vm_event_state`. При зчитуванні псевдо-файла `/proc/vmstat` підсистема віртуальної пам'яті сумує показники з усіх CPU (через функцію `all_vm_events()`), надаючи глобальну картину без значних блокувань.

Зчитування файлу `/proc/vmstat` є вкрай дешевою операцією, оскільки дані формуються повністю в оперативній пам'яті ядра без звернення до блокових пристроїв. Це дозволяє утиліті моніторингу опитувати файл з високою частотою (наприклад, щосекунди) практично з нульовим overhead для системних ресурсів.

## Реалізація монітора

Нижче наведено робочий код монітора двома мовами: у вигляді низькорівневої C-програми, яка не створює динамічних аллокацій пам'яті в гарячому циклі, та ідіоматичної об'єктно-орієнтованої реалізації на C++20 з використанням RAII, `std::chrono` та обробки потоків.

:::tabs
```c
/* reclaim_mon.c — C99/C11 монітор системного витіснення сторінок */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>

typedef struct {
    unsigned long long pgscan_kswapd;
    unsigned long long pgscan_direct;
    unsigned long long pgsteal_kswapd;
    unsigned long long pgsteal_direct;
    unsigned long long allocstall;
    unsigned long long pageoutrun;
} vmstat_metrics_t;

static int read_vmstat(vmstat_metrics_t *m) {
    FILE *fp = fopen("/proc/vmstat", "r");
    if (!fp) {
        perror("Не вдалося відкрити /proc/vmstat");
        return -1;
    }

    memset(m, 0, sizeof(*m));
    char line[256];
    
    while (fgets(line, sizeof(line), fp)) {
        char key[64];
        unsigned long long val;
        if (sscanf(line, "%63s %llu", key, &val) == 2) {
            if (strcmp(key, "pgscan_kswapd") == 0)      m->pgscan_kswapd = val;
            else if (strcmp(key, "pgscan_direct") == 0)  m->pgscan_direct = val;
            else if (strcmp(key, "pgsteal_kswapd") == 0) m->pgsteal_kswapd = val;
            else if (strcmp(key, "pgsteal_direct") == 0) m->pgsteal_direct = val;
            /* від ядра 4.9 лічильник розбито по зонах: allocstall_dma, allocstall_normal, … */
            else if (strncmp(key, "allocstall", 10) == 0) m->allocstall += val;
            else if (strcmp(key, "pageoutrun") == 0)     m->pageoutrun = val;
        }
    }

    fclose(fp);
    return 0;
}

int main(int argc, char *argv[]) {
    int interval_sec = 1;
    if (argc > 1) {
        interval_sec = atoi(argv[1]);
        if (interval_sec <= 0) interval_sec = 1;
    }

    printf("Starting Reclaim Monitor (interval: %d s)...\n", interval_sec);
    printf("%-10s | %-14s | %-14s | %-10s | %-10s\n", 
           "Time", "kswapd scan/s", "Direct scan/s", "Stalls/s", "kswapd Eff");
    printf("-------------------------------------------------------------------\n");

    vmstat_metrics_t prev, curr;
    if (read_vmstat(&prev) < 0) return 1;

    while (1) {
        sleep(interval_sec);
        if (read_vmstat(&curr) < 0) break;

        unsigned long long dk_scan  = curr.pgscan_kswapd - prev.pgscan_kswapd;
        unsigned long long dd_scan  = curr.pgscan_direct - prev.pgscan_direct;
        unsigned long long dk_steal = curr.pgsteal_kswapd - prev.pgsteal_kswapd;
        unsigned long long dstalls  = curr.allocstall - prev.allocstall;

        double k_eff = (dk_scan > 0) ? ((double)dk_steal / dk_scan * 100.0) : 100.0;
        
        time_t now = time(NULL);
        struct tm *t = localtime(&now);
        char time_str[16];
        strftime(time_str, sizeof(time_str), "%H:%M:%S", t);

        const char *alert = (dstalls > 0) ? " [STALL DETECTED!]" : "";

        printf("%-10s | %-14llu | %-14llu | %-10llu | %6.1f%%%s\n",
               time_str, dk_scan / interval_sec, dd_scan / interval_sec,
               dstalls / interval_sec, k_eff, alert);

        prev = curr;
    }

    return 0;
}
```
```cpp
// reclaim_mon.cpp — C++20 об'єктно-орієнтований монітор витіснення сторінок
#include <iostream>
#include <fstream>
#include <string>
#include <chrono>
#include <thread>
#include <format>
#include <stdexcept>
#include <algorithm>
#include <cstdint>
#include <cstdlib>

struct VmstatMetrics {
    std::uint64_t pgscan_kswapd{0};
    std::uint64_t pgscan_direct{0};
    std::uint64_t pgsteal_kswapd{0};
    std::uint64_t pgsteal_direct{0};
    std::uint64_t allocstall{0};
    std::uint64_t pageoutrun{0};
};

class ReclaimCollector {
public:
    static VmstatMetrics fetch() {
        std::ifstream file("/proc/vmstat");
        if (!file.is_open()) {
            throw std::runtime_error("Cannot open /proc/vmstat");
        }

        VmstatMetrics m{};
        std::string key;
        std::uint64_t value;

        while (file >> key >> value) {
            if (key == "pgscan_kswapd")      m.pgscan_kswapd = value;
            else if (key == "pgscan_direct")  m.pgscan_direct = value;
            else if (key == "pgsteal_kswapd") m.pgsteal_kswapd = value;
            else if (key == "pgsteal_direct") m.pgsteal_direct = value;
            // від ядра 4.9 ключ розбито по зонах: allocstall_dma, allocstall_normal, …
            else if (key.starts_with("allocstall")) m.allocstall += value;
            else if (key == "pageoutrun")     m.pageoutrun = value;
        }
        return m;
    }
};

int main(int argc, char* argv[]) {
    using namespace std::chrono_literals;
    auto interval = 1s;

    if (argc > 1) {
        interval = std::chrono::seconds(std::max(1, std::atoi(argv[1])));
    }

    std::cout << std::format("C++20 Reclaim Monitor active (interval: {}s)\n", interval.count());
    std::cout << std::format("{:<10} | {:<14} | {:<14} | {:<10} | {:<10}\n",
                             "Time", "kswapd scan/s", "Direct scan/s", "Stalls/s", "kswapd Eff");
    std::cout << std::string(67, '-') << '\n';

    try {
        auto prev = ReclaimCollector::fetch();

        while (true) {
            std::this_thread::sleep_for(interval);
            auto curr = ReclaimCollector::fetch();

            auto dk_scan  = curr.pgscan_kswapd - prev.pgscan_kswapd;
            auto dd_scan  = curr.pgscan_direct - prev.pgscan_direct;
            auto dk_steal = curr.pgsteal_kswapd - prev.pgsteal_kswapd;
            auto dstalls  = curr.allocstall - prev.allocstall;

            double k_eff = (dk_scan > 0) 
                ? (static_cast<double>(dk_steal) / dk_scan * 100.0) 
                : 100.0;

            auto now = std::chrono::system_clock::now();
            auto time_t_now = std::chrono::system_clock::to_time_t(now);
            auto tm_now = *std::localtime(&time_t_now);

            std::string alert = (dstalls > 0) ? " [STALL DETECTED!]" : "";

            std::cout << std::format("{:02d}:{:02d}:{:02d}   | {:<14} | {:<14} | {:<10} | {:5.1f}%{}\n",
                                     tm_now.tm_hour, tm_now.tm_min, tm_now.tm_sec,
                                     dk_scan / interval.count(),
                                     dd_scan / interval.count(),
                                     dstalls / interval.count(),
                                     k_eff, alert);

            prev = curr;
        }
    } catch (const std::exception& e) {
        std::cerr << "Error in monitor loop: " << e.what() << '\n';
        return 1;
    }

    return 0;
}
```
:::

## Глибоке простеження через eBPF та tracepoints ядра

У випадках, коли зчитування метрик з `/proc/vmstat` підтверджує наявність затримок `allocstall`, системному інженеру необхідно точно встановити, які саме процеси та виклики аллокації стають причиною пробудження Direct Reclaim. Для цього застосовуються трасувальні точки ядра (kernel tracepoints) за допомогою утиліти `bpftrace`:

```bash
# Трасування подій пробудження kswapd та початку Direct Reclaim у реальному часі
sudo bpftrace -e '
tracepoint:vmscan:mm_vmscan_kswapd_wake {
    printf("kswapd woken for node %d, order %d\n", args->nid, args->order);
}
tracepoint:vmscan:mm_vmscan_direct_reclaim_begin {
    printf("Process %s (PID %d) entered Direct Reclaim (order %d)\n", 
           comm, pid, args->order);
}
'
```

Цей BPF-скрипт фіксує точні імена команд (`comm`) та ідентифікатори процесів (`pid`), які змушені виконувати синхронне витіснення сторінок, а також порядок виділення (`order`), для якого не вистачило вільної пам'яті.

## Особливості асиметрії NUMA-вузлів

На багатовузлових системах (Multi-Socket NUMA) глобальний файл `/proc/vmstat` показує сумарне значення. Однак ситуація, коли один NUMA-вузол виснажив свій резерв пам'яті, а на сусідньому вузлі залишаються гігабайти вільної пам'яті, є досить поширеною (NUMA imbalance).

У таких випадках локальні процеси, прив'язані до першого вузла, потраплятимуть у Direct Reclaim, хоча загальносистемний обсяг вільної RAM видаватиметься достатнім. Для діагностики таких асиметрій слід доповнювати моніторинг зчитуванням специфічних лічильників вузлів із файлів `/sys/devices/system/node/node*/vmstat`, звертаючи особливу увагу на лічильники `numa_hit`, `numa_miss` та `numa_foreign`.

## Оцінка результатів та інтеграція в продакшн

Під час проведення бенчмарків або аналізу роботи сервісів у продакшн-середовищі результати монітора дозволяють точно локалізувати проблеми з підсистемою пам'яті.

### Тлумачення відхилень у метриках:

1. **Ефективність `kswapd Eff < 50%`**: Якщо `kswapd` сканує велику кількість сторінок, але вивільняє лише малу частку, це означає, що більшість сторінок у неактивному списку є брудними (dirty) або заблокованими. У цьому випадку необхідно зменшити поріг `vm.dirty_background_ratio`, щоб підсистема writeback раніше скидала сторінки на диск.
2. **Переважання `Direct scan/s` над `kswapd scan/s`**: Якщо число `Direct scan/s` перевищує `kswapd scan/s`, це прямо вказує на те, що зазор `WMARK_LOW` занадто малий для даного типу навантаження. Демон `kswapd` прокидається занадто пізно. Для виправлення ситуації слід підняти `vm.watermark_scale_factor` з 10 до 50 або 100, або збільшити `vm.min_free_kbytes`.
3. **Поява `allocstall > 0`**: Будь-який ненульовий спалах у колонці `Stalls/s` є індикатором прямого падіння продуктивності додатків користувача. У Prometheus-експортерах (наприклад, `node_exporter`) цим лічильникам відповідають метрики виду `node_vmstat_allocstall_normal` — по одній на зону, і підсумовувати їх треба самому. Рекомендується налаштовувати алерт при появі приросту цієї метрики за 5-хвилинний інтервал.
