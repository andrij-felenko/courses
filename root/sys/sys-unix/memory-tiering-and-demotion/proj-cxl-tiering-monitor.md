# ⚙️ Моніторинг і трасування дворівневої міграції сторінок

Цей практичний проект демонструє створення повноцінної системної утиліти для діагностики, моніторингу та аналізу продуктивності дворівневої пам'яті (Memory Tiering) у режимі реального часу. Інструмент автоматично досліджує топологію наявних ярусів пам'яті через віртуальну файлову систему `sysfs`, періодично опитує низькорівневі лічильники ядра у `/proc/vmstat` та розраховує динамічні швидкості асинхронного витіснення (Demotion) і підвищення (Promotion) сторінок у мегабайтах за секунду.

## Архітектура монітора та джерела даних

Утиліта вирішує дві ключові діагностичні задачі:
1. **Топологічне сканування ярусів:** під час запуску програма обходить каталог `/sys/devices/system/node/memory_tiers/`, виявляє всі зареєстровані яруси продуктивності (`memory_tier0`, `memory_tier1` тощо) та закріплені за ними діапазони NUMA-вузлів. Це дає змогу миттєво визначити, які саме вузли виконують роль швидкої локальної DRAM сокетів, а які є повільними розширювачами CXL.mem або енергонезалежною пам'яттю PMEM.
2. **Диференційний розрахунок метрик міграції:** у фоновому циклі з фіксованим інтервалом опитування (наприклад, 1 секунда) програма фіксує значення кумулятивних лічильників сторінок ядра (`pgdemote_kswapd`, `pgdemote_direct`, `pgpromote_success`, `numa_hint_faults`). Швидкість переміщення даних розраховується як різниця між двома послідовними зрізами, помножена на розмір системної сторінки (4096 байтів).

```
  /sys/devices/system/node/memory_tiers/ ──► [ Сканування топології ярусів ]
                                                            │
  /proc/vmstat (pgdemote_*, pgpromote_*) ──► [ Диференційний розрахунок MB/s ]
                                                            │
                                             [ Консольний дашборд оператора ]
```

## Порівняння підходів: /proc/vmstat проти eBPF та точок трасування

Під час побудови систем спостережливості (Observability) за ярусами пам'яті інженери обирають між двома рівнями деталізації:

* **Періодичний опрос /proc/vmstat (підхід цієї утиліти):** надзвичайно легкий метод, який споживає менше 0.01% процесорного часу. Він ідеально підходить для постійного фонового моніторингу у виробничому середовищі (Production Metrics), побудови графіків у Prometheus/Grafana та раннього виявлення перевантаження шин.
* **Трасування через tracepoints / eBPF (`mm_migrate_pages`, `mm_numa_migrate_ratelimit`):** детальний метод, що фіксує кожну окрему подію міграції, затримки копіювання конкретних фоліо та ідентифікатори процесів (PID). Він незамінний під час локалізації вузьких місць у конкретних додатках, але створює помітний накладний оверхед при швидкостях міграції понад 100 000 сторінок на секунду.

## Реалізація інструменту

Нижче наведено повноцінну реалізацію консольного монітора двома мовами програмування — системною мовою C та ідіоматичною мовою C++ з використанням об'єктно-орієнтованої декомпозиції, RAII-обгорток над файловими потоками та стандартної бібліотеки `<chrono>`.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dirent.h>
#include <time.h>
#include <stdbool.h>

#define SYSFS_TIERS "/sys/devices/system/node/memory_tiers"
#define VMSTAT_PATH "/proc/vmstat"
#define PAGE_SIZE_KB 4

typedef struct {
    unsigned long pgdemote_kswapd;
    unsigned long pgdemote_direct;
    unsigned long pgpromote_success;
    unsigned long pgpromote_candidate;
    unsigned long numa_hint_faults;
} vmstat_tier_metrics_t;

static void discover_memory_tiers(void) {
    DIR *dir = opendir(SYSFS_TIERS);
    if (!dir) {
        printf("[WARN] Memory tiers sysfs directory not found: %s\n", SYSFS_TIERS);
        printf("[INFO] System may lack CXL/PMEM hardware or CONFIG_TIERED_MEMORY.\n\n");
        return;
    }

    printf("=== Виявлені яруси пам'яті (Memory Tiers) ===\n");
    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (strncmp(entry->d_name, "memory_tier", 11) == 0) {
            char nodes_path[512];
            snprintf(nodes_path, sizeof(nodes_path), "%s/%s/nodelist", SYSFS_TIERS, entry->d_name);
            FILE *f = fopen(nodes_path, "r");
            char nodelist[128] = "unknown";
            if (f) {
                if (fgets(nodelist, sizeof(nodelist), f)) {
                    nodelist[strcspn(nodelist, "\r\n")] = 0;
                }
                fclose(f);
            }
            printf("  • %-14s -> NUMA-вузли: [%s]\n", entry->d_name, nodelist);
        }
    }
    closedir(dir);
    printf("\n");
}

static bool read_vmstat_metrics(vmstat_tier_metrics_t *out) {
    FILE *f = fopen(VMSTAT_PATH, "r");
    if (!f) return false;

    memset(out, 0, sizeof(*out));
    char line[256];
    while (fgets(line, sizeof(line), f)) {
        char key[64];
        unsigned long val;
        if (sscanf(line, "%63s %lu", key, &val) == 2) {
            if (strcmp(key, "pgdemote_kswapd") == 0) out->pgdemote_kswapd = val;
            else if (strcmp(key, "pgdemote_direct") == 0) out->pgdemote_direct = val;
            else if (strcmp(key, "pgpromote_success") == 0) out->pgpromote_success = val;
            else if (strcmp(key, "pgpromote_candidate") == 0) out->pgpromote_candidate = val;
            else if (strcmp(key, "numa_hint_faults") == 0) out->numa_hint_faults = val;
        }
    }
    fclose(f);
    return true;
}

int main(int argc, char **argv) {
    int interval_sec = 1;
    if (argc > 1) {
        interval_sec = atoi(argv[1]);
        if (interval_sec < 1) interval_sec = 1;
    }

    discover_memory_tiers();

    vmstat_tier_metrics_t prev, curr;
    if (!read_vmstat_metrics(&prev)) {
        perror("Помилка читання /proc/vmstat");
        return 1;
    }

    printf("%-10s | %-16s | %-16s | %-16s | %-14s\n",
           "Час", "Demote kswapd", "Demote Direct", "Promote Success", "NUMA Hints");
    printf("-----------------------------------------------------------------------------------\n");

    while (1) {
        sleep((unsigned int)interval_sec);
        if (!read_vmstat_metrics(&curr)) break;

        time_t rawtime;
        time(&rawtime);
        struct tm *ti = localtime(&rawtime);
        char time_buf[16];
        strftime(time_buf, sizeof(time_buf), "%H:%M:%S", ti);

        double demote_kswapd_mbs = ((double)(curr.pgdemote_kswapd - prev.pgdemote_kswapd) * PAGE_SIZE_KB) / (1024.0 * interval_sec);
        double demote_direct_mbs = ((double)(curr.pgdemote_direct - prev.pgdemote_direct) * PAGE_SIZE_KB) / (1024.0 * interval_sec);
        double promote_mbs = ((double)(curr.pgpromote_success - prev.pgpromote_success) * PAGE_SIZE_KB) / (1024.0 * interval_sec);
        unsigned long hints_rate = (curr.numa_hint_faults - prev.numa_hint_faults) / (unsigned long)interval_sec;

        printf("%-10s | %10.2f MB/s | %10.2f MB/s | %10.2f MB/s | %10lu f/s\n",
               time_buf, demote_kswapd_mbs, demote_direct_mbs, promote_mbs, hints_rate);
        fflush(stdout);

        prev = curr;
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <unordered_map>
#include <chrono>
#include <thread>
#include <iomanip>
#include <filesystem>

namespace fs = std::filesystem;

struct TierMetrics {
    uint64_t pgdemote_kswapd = 0;
    uint64_t pgdemote_direct = 0;
    uint64_t pgpromote_success = 0;
    uint64_t pgpromote_candidate = 0;
    uint64_t numa_hint_faults = 0;
};

class TieringMonitor {
public:
    static void discover_tiers() {
        const fs::path tiers_path = "/sys/devices/system/node/memory_tiers";
        if (!fs::exists(tiers_path)) {
            std::cout << "[WARN] Каталог memory_tiers не знайдено: " << tiers_path << "\n";
            std::cout << "[INFO] Можливо, CXL-пристрої відсутні або ядро не зібрано з CONFIG_TIERED_MEMORY.\n\n";
            return;
        }

        std::cout << "=== Виявлені яруси пам'яті (Memory Tiers) ===\n";
        for (const auto& entry : fs::directory_iterator(tiers_path)) {
            if (entry.is_directory() && entry.path().filename().string().rfind("memory_tier", 0) == 0) {
                fs::path nodelist_file = entry.path() / "nodelist";
                std::string nodes = "unknown";
                if (std::ifstream in(nodelist_file); in.is_open()) {
                    std::getline(in, nodes);
                }
                std::cout << "  • " << std::left << std::setw(14) << entry.path().filename().string()
                          << " -> NUMA-вузли: [" << nodes << "]\n";
            }
        }
        std::cout << "\n";
    }

    static TierMetrics read_vmstat() {
        TierMetrics metrics;
        std::ifstream file("/proc/vmstat");
        if (!file.is_open()) return metrics;

        std::string key;
        uint64_t value = 0;
        while (file >> key >> value) {
            if (key == "pgdemote_kswapd") metrics.pgdemote_kswapd = value;
            else if (key == "pgdemote_direct") metrics.pgdemote_direct = value;
            else if (key == "pgpromote_success") metrics.pgpromote_success = value;
            else if (key == "pgpromote_candidate") metrics.pgpromote_candidate = value;
            else if (key == "numa_hint_faults") metrics.numa_hint_faults = value;
        }
        return metrics;
    }

    static void run(std::chrono::seconds interval) {
        discover_tiers();

        TierMetrics prev = read_vmstat();

        std::cout << std::left << std::setw(10) << "Час" << " | "
                  << std::setw(16) << "Demote kswapd" << " | "
                  << std::setw(16) << "Demote Direct" << " | "
                  << std::setw(16) << "Promote Success" << " | "
                  << std::setw(14) << "NUMA Hints" << "\n";
        std::cout << std::string(83, '-') << "\n";

        while (true) {
            std::this_thread::sleep_for(interval);
            TierMetrics curr = read_vmstat();

            auto now = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());
            auto local_tm = *std::localtime(&now);

            constexpr double page_kb = 4.0;
            double factor = page_kb / (1024.0 * interval.count());

            double demote_kswapd_mb = static_cast<double>(curr.pgdemote_kswapd - prev.pgdemote_kswapd) * factor;
            double demote_direct_mb = static_cast<double>(curr.pgdemote_direct - prev.pgdemote_direct) * factor;
            double promote_mb = static_cast<double>(curr.pgpromote_success - prev.pgpromote_success) * factor;
            uint64_t hints_rate = (curr.numa_hint_faults - prev.numa_hint_faults) / interval.count();

            std::cout << std::put_time(&local_tm, "%H:%M:%S") << "   | "
                      << std::right << std::setw(10) << std::fixed << std::setprecision(2) << demote_kswapd_mb << " MB/s | "
                      << std::right << std::setw(10) << std::fixed << std::setprecision(2) << demote_direct_mb << " MB/s | "
                      << std::right << std::setw(10) << std::fixed << std::setprecision(2) << promote_mb << " MB/s | "
                      << std::right << std::setw(10) << hints_rate << " f/s\n";

            prev = curr;
        }
    }
};

int main(int argc, char* argv[]) {
    int interval_sec = (argc > 1) ? std::max(1, std::atoi(argv[1])) : 1;
    TieringMonitor::run(std::chrono::seconds(interval_sec));
    return 0;
}
```
:::

## Компіляція, вимоги ядра та системна інтеграція

Для збирання та коректного виконання утиліти необхідно забезпечити такі системні передумови:

### 1. Опції конфігурації ядра Linux
Ядро повинно бути зібрано з підтримкою багаторівневої пам'яті та міграції:
* `CONFIG_NUMA=y` — базова підтримка неоднорідної пам'яті.
* `CONFIG_MIGRATION=y` — інфраструктура копіювання сторінок між вузлами.
* `CONFIG_NUMA_BALANCING=y` — підсистема автоматичного балансування та генерації hint faults.
* `CONFIG_TIERED_MEMORY=y` (або `CONFIG_MEMORY_TIERS=y` у новіших версіях) — реєстрація каталогу `/sys/devices/system/node/memory_tiers/`.
* `CONFIG_CXL_MEM=y` — драйвер розширювачів пам'яті Compute Express Link.

### 2. Практичні команди компіляції
```bash
# Компіляція версії C
gcc -O2 -Wall -Wextra -pedantic tiering_monitor.c -o tiering_monitor

# Компіляція версії C++ (потрібен стандарт C++17 для std::filesystem)
g++ -O2 -Wall -Wextra -std=c++17 tiering_monitor.cpp -o tiering_monitor_cpp
```

### 3. Запуск та інтеграція в систему моніторингу
Утиліту можна запускати з інтервалом опитування в 1 секунду без прав суперкористувача (читання `/proc/vmstat` та `sysfs` доступне звичайним процесам):

```bash
./tiering_monitor 1
```

Для створення автоматичних сповіщень (Alerting) рекомендується встановити поріг: якщо `Demote Direct` перевищує 50 МБ/с упродовж більше ніж 10 секунд поспіль, система оркестрації повинна надіслати сповіщення про брак швидкої пам'яті DRAM та ризик деградації p99-затримок додатків.

## Інтерпретація метрик та діагностичні сценарії

Під час аналізу роботи дворівневої системи на реальному навантаженні монітор допомагає швидко розпізнати чотири типові патологічні стани:

### 1. Домінування прямого витіснення (Direct Demotion Dominance)
* *Симптоми:* Показник `Demote Direct` перевищує `Demote kswapd` (наприклад, 450 МБ/с проти 20 МБ/с).
* *Фізична суть:* Потоки користувача виділяють пам'ять швидше, ніж фоновий демон встигає прокинутися й підготувати вільні сторінки в швидкій DRAM. Потоки додатків зупиняються (stall) і самостійно копіюють свої сторінки у CXL.
* *Дія:* Збільшити буфер між водяними знаками `sysctl -w vm.watermark_scale_factor=100`, щоб `kswapd` прокидався заздалегідь.

### 2. Паразитне коливання сторінок (Thrashing)
* *Симптоми:* Високі швидкості `Demote kswapd` та `Promote Success` одночасно (наприклад, обидва по 600–800 МБ/с) при постійній кількості `NUMA Hints` понад 50 000 f/s.
* *Фізична суть:* Робочий набір процесу перевищує розмір Top-tier DRAM, але весь активно використовується. Ядро безперервно виштовхує сторінки в CXL і тут же затягує їх назад, спалюючи пропускну здатність шини PCIe.
* *Дія:* Увімкнути фільтрацію гарячих сторінок `sysctl -w kernel.numa_balancing=7` або зменшити ліміт промоції `sysctl -w kernel.numa_balancing_rate_limit_mbps=512`.

### 3. Блокування промоції через ліміти швидкості (Rate Limit Throttling)
* *Симптоми:* Високий показник `pgpromote_candidate` (багато сторінок хочуть піднятися) при низькому `Promote Success` та зростанні лічильника точок трасування `mm_numa_migrate_ratelimit`.
* *Фізична суть:* Промоція штучно гальмується внутрішнім механізмом захисту шини, сторінки лишаються в повільній CXL-пам'яті, що сповільнює виконання чутливих до затримок запитів.
* *Дія:* Якщо шина PCIe не перевантажена іншими пристроями, збільшити параметр `numa_balancing_rate_limit_mbps` до 2048–4096 МБ/с.

### 4. Нульова активність при дефіциті пам'яті
* *Симптоми:* Показники `Demote` рівні 0, але вільна пам'ять на вузлі 0 падає до критичного рівня, і система починає скидати сторінки у дисковий swap.
* *Фізична суть:* Асинхронний спуск глобально вимкнено або для даного контейнера cgroup встановлено `memory.demote_enabled = 0`.
* *Дія:* Перевірити значення `/sys/kernel/mm/numa/demotion_enabled` та конфігурацію відповідного cgroup.
