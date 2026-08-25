# ⚙️ Моніторинг активності swiotlb та діагностика переповнення пулу

Практичний інструментарій діагностики підсистеми swiotlb дозволяє системним інженерам та розробникам драйверів виявляти приховані вузькі місця у швидкодії введення-виведення, відстежувати випадки вичерпання пулу підмінних буферів та аналізувати частоту копіювання даних у режимі реального часу. У цьому проекті розглядається побудова утиліти моніторингу метрик debugfs, створення фонового демона спостереження за сплесками навантаження, аналіз подій трасування ядра, вимірювання затримок копіювання та методи усунення переповнення пулу у виробничому середовищі.

## Завдання: контроль стану пулу підмінних буферів

Коли система працює з периферійними пристроями, що мають обмежену адресну маску (наприклад, 32-бітні PCI-контролери на 64-бітній платформі), або функціонує в режимі захищеної віртуальної машини (AMD SEV / Intel TDX), активність підсистеми swiotlb безпосередньо визначає пропускну здатність дискової та мережевої підсистем. Якщо інтенсивність операцій введення-виведення перевищує місткість пулу (типово 64 МіБ за замовчуванням), ядро не може виділити нові слоти, і виклики відображення повертають помилку `DMA_MAPPING_ERROR`.

У виробничому середовищі це призводить до таких критичних симптомів:

- Масове скидання вхідних та вихідних мережевих пакетів із фіксацією помилок `swiotlb buffer is full` у кільцевому журналі ядра `dmesg`.
- Збільшення затримок запитів (latency spikes) у дисковому вводі-виводі через блокування черг блокових пристроїв.
- Тимчасове зависання або аварійний скид стану апаратних контролерів, які не отримують дескрипторів передачі.
- Падіння пропускної здатності високошвидкісних інтерфейсів (10G/25G VirtIO) у хмарних конфіденційних середовищах.

Для запобігання збоям системний адміністратор та інженер експлуатації повинні вміти регулярно опитувати лічильники утилізації пулу, фіксувати зростання лічильника переповнень `io_tlb_overflow` та виявляти пристрої, які генерують надмірну кількість операцій копіювання `memcpy`.

## Інструмент 1: Зчитування миттєвих метрик пулу

Ядро Linux експортує актуальні лічильники стану пулу через псевдофайлову систему debugfs за шляхом `/sys/kernel/debug/swiotlb/`. Програма моніторингу відкриває відповідні вузли, зчитує показники, обчислює відсоток поточного та пікового навантаження, і в разі наближення до критичного порогу (наприклад, понад 80% зайнятих слотів) сигналізує про необхідність збільшення параметра завантаження ядра `swiotlb=N`.

Нижче наведено реалізацію консольної утиліти `swiotlb_stat` двома мовами — C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>

#define SWIOTLB_BASE "/sys/kernel/debug/swiotlb"
#define BUF_SIZE 64

static int read_debugfs_ulong(const char *node, unsigned long *val) {
    char path[256];
    char buf[BUF_SIZE];
    snprintf(path, sizeof(path), "%s/%s", SWIOTLB_BASE, node);

    int fd = open(path, O_RDONLY);
    if (fd < 0)
        return -errno;

    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);

    if (n <= 0)
        return -EIO;

    buf[n] = '\0';
    char *endptr;
    *val = strtoul(buf, &endptr, 10);
    return 0;
}

int main(void) {
    unsigned long nslabs = 0;
    unsigned long used = 0;
    unsigned long highwater = 0;
    unsigned long overflow = 0;

    if (read_debugfs_ulong("io_tlb_nslabs", &nslabs) < 0) {
        fprintf(stderr, "Помилка доступу до debugfs. Перевірте: mount -t debugfs none /sys/kernel/debug\n");
        return EXIT_FAILURE;
    }

    read_debugfs_ulong("io_tlb_used", &used);
    read_debugfs_ulong("io_tlb_used_highwater", &highwater);
    read_debugfs_ulong("io_tlb_overflow", &overflow);

    double total_mb = (double)(nslabs * 2048) / (1024.0 * 1024.0);
    double used_mb = (double)(used * 2048) / (1024.0 * 1024.0);
    double high_mb = (double)(highwater * 2048) / (1024.0 * 1024.0);
    double used_pct = nslabs ? ((double)used / (double)nslabs) * 100.0 : 0.0;
    double high_pct = nslabs ? ((double)highwater / (double)nslabs) * 100.0 : 0.0;

    printf("=== Стан підсистеми SWIOTLB ===\n");
    printf("Загальний пул:      %8lu слотів (%6.2f МіБ)\n", nslabs, total_mb);
    printf("Поточне утримання:  %8lu слотів (%6.2f МіБ) [%5.1f%%]\n", used, used_mb, used_pct);
    printf("Пікове утримання:   %8lu слотів (%6.2f МіБ) [%5.1f%%]\n", highwater, high_mb, high_pct);
    printf("Лічильник відмов:   %8lu переповнень\n", overflow);

    if (overflow > 0) {
        printf("\n[УВАГА] Зафіксовано переповнення пулу! Збільште параметр ядра swiotlb=N\n");
    } else if (high_pct > 80.0) {
        printf("\n[ПОПЕРЕДЖЕННЯ] Пікове навантаження перевищує 80%% ємності пулу.\n");
    } else {
        printf("\n[OK] Пул працює в штатному режимі із запасом пам'яті.\n");
    }

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <expected>
#include <format>

namespace fs = std::filesystem;

struct SwiotlbMetrics {
    unsigned long nslabs{0};
    unsigned long used{0};
    unsigned long highwater{0};
    unsigned long overflow{0};

    [[nodiscard]] double total_mb() const noexcept {
        return static_cast<double>(nslabs * 2048) / (1024.0 * 1024.0);
    }
    [[nodiscard]] double used_mb() const noexcept {
        return static_cast<double>(used * 2048) / (1024.0 * 1024.0);
    }
    [[nodiscard]] double highwater_mb() const noexcept {
        return static_cast<double>(highwater * 2048) / (1024.0 * 1024.0);
    }
    [[nodiscard]] double used_percent() const noexcept {
        return nslabs ? (static_cast<double>(used) / static_cast<double>(nslabs)) * 100.0 : 0.0;
    }
    [[nodiscard]] double highwater_percent() const noexcept {
        return nslabs ? (static_cast<double>(highwater) / static_cast<double>(nslabs)) * 100.0 : 0.0;
    }
};

class SwiotlbMonitor {
    static constexpr std::string_view base_path = "/sys/kernel/debug/swiotlb";

    static std::expected<unsigned long, std::string> read_node(const std::string& name) {
        const fs::path p = fs::path(base_path) / name;
        std::ifstream file(p);
        if (!file.is_open()) {
            return std::unexpected(std::format("Не вдалося відкрити {}", p.string()));
        }
        unsigned long val = 0;
        if (!(file >> val)) {
            return std::unexpected(std::format("Помилка зчитування значення з {}", p.string()));
        }
        return val;
    }

public:
    static std::expected<SwiotlbMetrics, std::string> collect() {
        SwiotlbMetrics m{};
        auto nslabs = read_node("io_tlb_nslabs");
        if (!nslabs) return std::unexpected(nslabs.error());
        m.nslabs = *nslabs;

        m.used = read_node("io_tlb_used").value_or(0);
        m.highwater = read_node("io_tlb_used_highwater").value_or(0);
        m.overflow = read_node("io_tlb_overflow").value_or(0);
        return m;
    }
};

int main() {
    auto res = SwiotlbMonitor::collect();
    if (!res) {
        std::cerr << "Помилка: " << res.error() << "\n"
                  << "Переконайтеся, що debugfs змонтовано: mount -t debugfs none /sys/kernel/debug\n";
        return 1;
    }

    const auto& m = *res;
    std::cout << "=== Стан підсистеми SWIOTLB ===\n";
    std::cout << std::format("Загальний пул:      {:8d} слотів ({:6.2f} МіБ)\n", m.nslabs, m.total_mb());
    std::cout << std::format("Поточне утримання:  {:8d} слотів ({:6.2f} МіБ) [{:5.1f}%]\n", m.used, m.used_mb(), m.used_percent());
    std::cout << std::format("Пікове утримання:   {:8d} слотів ({:6.2f} МіБ) [{:5.1f}%]\n", m.highwater, m.highwater_mb(), m.highwater_percent());
    std::cout << std::format("Лічильник відмов:   {:8d} переповнень\n", m.overflow);

    if (m.overflow > 0) {
        std::cout << "\n[УВАГА] Зафіксовано переповнення пулу! Збільште параметр ядра swiotlb=N\n";
    } else if (m.highwater_percent() > 80.0) {
        std::cout << "\n[ПОПЕРЕДЖЕННЯ] Пікове навантаження перевищує 80% ємності пулу.\n";
    } else {
        std::cout << "\n[OK] Пул працює в штатному режимі із запасом пам'яті.\n";
    }

    return 0;
}
```
:::

## Інструмент 2: Фоновий демон відстеження сплесків навантаження

Для безперервного моніторингу у виробничому середовищі корисний автономний фоновий процес, який з певною періодичністю перевіряє рівень зайнятості пулу та повідомляє системного демона журналювання `syslog` або `systemd-journald` про стрибки пікових значень.

Нижче наведено приклад реалізації циклічного демона спостереження.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <syslog.h>
#include <fcntl.h>
#include <string.h>

#define SWIOTLB_HIGHWATER "/sys/kernel/debug/swiotlb/io_tlb_used_highwater"
#define SWIOTLB_NSLABS    "/sys/kernel/debug/swiotlb/io_tlb_nslabs"
#define SWIOTLB_OVERFLOW  "/sys/kernel/debug/swiotlb/io_tlb_overflow"

static unsigned long read_val(const char *path) {
    char buf[64];
    int fd = open(path, O_RDONLY);
    if (fd < 0) return 0;
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);
    if (n <= 0) return 0;
    buf[n] = '\0';
    return strtoul(buf, NULL, 10);
}

int main(void) {
    openlog("swiotlb-watcher", LOG_PID | LOG_CONS, LOG_DAEMON);
    syslog(LOG_INFO, "Запуск демона спостереження за пулом SWIOTLB");

    unsigned long nslabs = read_val(SWIOTLB_NSLABS);
    if (nslabs == 0) {
        syslog(LOG_ERR, "Не вдалося отримати розмір пулу SWIOTLB. Завершення роботи.");
        closelog();
        return EXIT_FAILURE;
    }

    unsigned long last_highwater = 0;
    unsigned long last_overflow = 0;

    while (1) {
        unsigned long cur_highwater = read_val(SWIOTLB_HIGHWATER);
        unsigned long cur_overflow = read_val(SWIOTLB_OVERFLOW);

        if (cur_overflow > last_overflow) {
            syslog(LOG_CRIT, "КРИТИЧНО: Зафіксовано нові переповнення пулу SWIOTLB (+%lu)! Загалом: %lu",
                   cur_overflow - last_overflow, cur_overflow);
            last_overflow = cur_overflow;
        }

        if (cur_highwater > last_highwater) {
            double pct = ((double)cur_highwater / (double)nslabs) * 100.0;
            if (pct > 75.0) {
                syslog(LOG_WARNING, "Попередження: Новий пік утилізації SWIOTLB: %lu слотів (%.1f%% від %lu)",
                       cur_highwater, pct, nslabs);
            }
            last_highwater = cur_highwater;
        }

        sleep(5);
    }

    closelog();
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <filesystem>
#include <chrono>
#include <thread>
#include <syslog.h>
#include <format>

namespace fs = std::filesystem;

class SwiotlbWatcher {
    fs::path base_{"/sys/kernel/debug/swiotlb"};
    unsigned long nslabs_{0};
    unsigned long last_highwater_{0};
    unsigned long last_overflow_{0};

    [[nodiscard]] unsigned long read_ulong(std::string_view name) const {
        std::ifstream f(base_ / name);
        unsigned long v = 0;
        if (f >> v) return v;
        return 0;
    }

public:
    bool init() {
        openlog("swiotlb-watcher-cpp", LOG_PID | LOG_CONS, LOG_DAEMON);
        nslabs_ = read_ulong("io_tlb_nslabs");
        if (nslabs_ == 0) {
            syslog(LOG_ERR, "Помилка: не вдалося зчитати io_tlb_nslabs з debugfs");
            return false;
        }
        syslog(LOG_INFO, "Демон моніторингу запущено. Розмір пулу: %lu слотів", nslabs_);
        return true;
    }

    ~SwiotlbWatcher() {
        closelog();
    }

    void run(std::chrono::seconds interval) {
        while (true) {
            const auto cur_highwater = read_ulong("io_tlb_used_highwater");
            const auto cur_overflow = read_ulong("io_tlb_overflow");

            if (cur_overflow > last_overflow_) {
                const auto diff = cur_overflow - last_overflow_;
                const auto msg = std::format("КРИТИЧНО: Нові переповнення пулу (+{})! Загалом: {}", diff, cur_overflow);
                syslog(LOG_CRIT, "%s", msg.c_str());
                last_overflow_ = cur_overflow;
            }

            if (cur_highwater > last_highwater_) {
                const double pct = (static_cast<double>(cur_highwater) / static_cast<double>(nslabs_)) * 100.0;
                if (pct > 75.0) {
                    const auto msg = std::format("Попередження: Новий пік утилізації: {} слотів ({:.1f}%)", cur_highwater, pct);
                    syslog(LOG_WARNING, "%s", msg.c_str());
                }
                last_highwater_ = cur_highwater;
            }

            std::this_thread::sleep_for(interval);
        }
    }
};

int main() {
    SwiotlbWatcher watcher;
    if (!watcher.init()) {
        std::cerr << "Не вдалося ініціалізувати SwiotlbWatcher. Перевірте debugfs.\n";
        return 1;
    }

    watcher.run(std::chrono::seconds(5));
    return 0;
}
```
:::

## Аналіз подій трасування за допомогою trace-cmd та ftrace

Зчитування лічильників показує інтегральний стан, але не дає інформації про те, який саме пристрій створює навантаження на підсистему підміни. Для детального профілювання використовується точка трасування `swiotlb_bounced`.

Підсистема ftrace записує кожне виділення слота у кільцевий буфер трасування ядра. Завдяки цьому можна дізнатися точну часову мітку, назву пристрою на шині PCI, обсяг запитаної передачі та виділений розмір пам'яті.

### Увімкнення та збір подій через ftrace

```bash
# 1. Скидання попередніх налаштувань трасувальника
echo 0 > /sys/kernel/tracing/tracing_on
echo > /sys/kernel/tracing/trace

# 2. Активація події swiotlb_bounced
echo 1 > /sys/kernel/tracing/events/swiotlb/swiotlb_bounced/enable

# 3. Запуск трасування на 5 секунд під час навантаження
echo 1 > /sys/kernel/tracing/tracing_on
sleep 5
echo 0 > /sys/kernel/tracing/tracing_on

# 4. Перегляд зібраних подій
head -n 20 /sys/kernel/tracing/trace
```

Приклад виводу системного трасування:

```text
# tracer: nop
#
# entries-in-buffer: 4120, entries-read: 4120
#                            _-----=> irqs-off
#                           / _----=> need-resched
#                          | / _---=> hardirq/softirq
#                          || / _--=> preempt-depth
#                          ||| /     delay
#           TASK-PID CPU#  ||||   TIMESTAMP  FUNCTION
#              | |    |    ||||      |         |
      kworker/u16:1-142 [002] d.s. 124.582910: swiotlb_bounced: dev_name: 0000:00:03.0 dma_addr: 0x0000000038102000 size: 1514 alloc_size: 2048
      kworker/u16:1-142 [002] d.s. 124.582925: swiotlb_bounced: dev_name: 0000:00:03.0 dma_addr: 0x0000000038103000 size: 1514 alloc_size: 2048
      ksoftirqd/3-31   [003] ..s. 124.583102: swiotlb_bounced: dev_name: 0000:00:03.0 dma_addr: 0x0000000038104000 size: 1514 alloc_size: 2048
```

У наведеному журналі чітко видно:

- Пристрій `0000:00:03.0` (мережевий адаптер) щоразу вимагає виділення слота `alloc_size: 2048` для передачі стандартного Ethernet-кадру корисним розміром `size: 1514` байтів.
- Внутрішня фрагментація становить `2048 - 1514 = 534` байти на кожен пакет, що є неминучою платою за квантування слотів по 2 КіБ.

### Швидкий підрахунок частоти підмін за допомогою bpftrace

Якщо на сервері встановлено інструментарій eBPF, можна в реальному часі побудувати гістограму розмірів підмінних буферів за одну команду без збереження гігабайтних текстових журналів:

```bash
bpftrace -e 'tracepoint:swiotlb:swiotlb_bounced { @size_bytes[args->dev_name] = hist(args->size); @total_bounces[args->dev_name] = count(); }'
```

Цей скрипт агрегує розподіл обсягів передачі безпосередньо в просторі ядра, показуючи, які адаптери навантажують підсистему дрібними мережевими кадрами, а які — великими блоковими масивами.

## Практичні кроки усунення переповнення у продакшені

Коли системний моніторинг фіксує переповнення пулу (`io_tlb_overflow > 0`), слід виконати послідовність дій для відновлення стабільності:

1. **Тимчасове збільшення розміру пулу через GRUB.** Відкрийте файл конфігурації `/etc/default/grub` і додайте параметр `swiotlb=262144` (що виділяє 512 МіБ) до змінної `GRUB_CMDLINE_LINUX_DEFAULT`. Після цього оновіть завантажувач командою `update-grub` або `grub2-mkconfig -o /boot/grub2/grub.cfg` і перезавантажте вузол.
2. **Перевірка апаратного IOMMU.** Переконайтеся, що на хості не було випадково вимкнено апаратну віртуалізацію введення-виведення в BIOS/UEFI (Intel VT-d або AMD IOMMU). Якщо апаратний IOMMU увімкнено, більшість сучасних драйверів перестає потребувати swiotlb взагалі.
3. **Активація динамічного swiotlb.** На ядрах версії 6.6 і вище перевірте наявність опції `CONFIG_SWIOTLB_DYNAMIC=y`. Це дозволяє ядру автоматично розширювати пул новими сторінками пам'яті під час пікових навантажень без ручного тюнінгу параметрів завантаження.

## Підводні камені та типові помилки конфігурації

1. **Ігнорування точки монтування debugfs.** За замовчуванням у багатьох захищених дистрибутивах Linux (RHEL, Ubuntu Server) файлова система debugfs не монтується автоматично або доступна виключно суперкористувачу root. Спроба відкрити файл без відповідних прав повертає помилку `EACCES`.
2. **Неврахування сплесків трафіку.** Якщо `io_tlb_used` у спокійному стані показує лише 5–10% утилізації, це не гарантує захисту від збоїв під час пікового навантаження. Завжди слід орієнтуватися на показник `io_tlb_used_highwater`.
3. **Хибне скидання пікового значення.** Запис `echo 0 > /sys/kernel/debug/swiotlb/io_tlb_used_highwater` дозволяє почати новий період спостереження (наприклад, перед запуском навантажувального тесту продуктивності), але безповоротно стирає історичні дані про попередні екстремуми.
4. **Виділення надмірного пулу.** Встановлення `swiotlb=524288` (1 ГБ) у рядку завантаження гарантує відсутність переповнень, але назавжди відчужує 1 ГБ низької пам'яті в інших підсистем ядра, навіть якщо пристрої більшу частину часу простоюють. Розмір слід калібрувати за піковими показниками `io_tlb_used_highwater` із коефіцієнтом запасу 1.5–2.0.
