# ⚙️ Практичний профілювальник енергії: вимірювання джоулів на ділянці коду

Для оптимізації високопродуктивних обчислень та зниження енергетичного сліду серверних застосунків недостатньо вимірювати лише час виконання алгоритму в мілісекундах. Два алгоритми з однаковою швидкістю виконання можуть кардинально відрізнятися за енерговитратами: векторні інструкції AVX-512 нагрівають кристал значно сильніше, ніж скалярні операції, а інтенсивні промахи повз кеш-пам'ять спалюють додаткові джоулі на шині оперативної пам'яті. Цей практичний проєкт демонструє створення системного профілювальника енергії для Linux, який дозволяє вимірювати енергетичні витрати довільного блоку коду з точністю до мікроджоулів через підсистему `powercap` та MSR-інтерфейс.

### Архітектура та принципи побудови системного лічильника

Традиційні підходи до бенчмаркінгу фокусуються виключно на часових мітках за допомогою інструкції `RDTSC` або системного годинника. Проте для отримання достовірного енергетичного профілю програма повинна синхронно реєструвати три взаємопов'язані фізичні величини:
1. **Витрачений фізичний час (`Δt`)**: монотонний інтервал часу, виміряний із наносекундною роздільною здатністю без ризику стрибків системного годинника через синхронізацію NTP.
2. **Абсолютна витрачена енергія (`ΔE`)**: кількість джоулів, накопичених окремими апаратними доменами процесора (весь сокет PKG, обчислювальні ядра PP0 та підсистема оперативної пам'яті DRAM).
3. **Середня розрахункова потужність (`P = ΔE / Δt`)**: електрична потужність у ватах, що показує інтенсивність нагрівання кристала під час виконання коду.

Для мінімізації накладних витрат (*overhead*) профілювальник відкриває дескриптори файлів сенсорів `/sys/class/powercap/intel-rapl/` один раз під час ініціалізації й тримає їх відкритими. Читання показників здійснюється через системний виклик `pread()` з нульовим файловим зсувом (*offset = 0*). Це дозволяє уникнути важких операцій повторного відкриття файлів, пошуку по дереву `dentry` у пам'яті ядра та виділення структур `inode`, скорочуючи тривалість одного виміру до 2–4 мікросекунд.

### Реалізація мовами C та C++

Нижче наведено дві повноцінні версії профілювальника: процедурну бібліотеку мовою C з дескрипторами та об'єктно-орієнтовану реалізацію мовою C++ з використанням патерну RAII (*Resource Acquisition Is Initialization*) та сучасного стандарту C++20.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>
#include <errno.h>

#define RAPL_PKG_PATH "/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj"
#define RAPL_CORE_PATH "/sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:0/energy_uj"
#define RAPL_DRAM_PATH "/sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:2/energy_uj"

typedef struct {
    int fd_pkg;
    int fd_core;
    int fd_dram;
    uint64_t start_energy_pkg;
    uint64_t start_energy_core;
    uint64_t start_energy_dram;
    struct timespec start_time;
} rapl_meter_t;

typedef struct {
    double duration_sec;
    double energy_pkg_joules;
    double energy_core_joules;
    double energy_dram_joules;
    double power_pkg_watts;
    double power_core_watts;
    double power_dram_watts;
} rapl_result_t;

static int open_sensor(const char *path) {
    int fd = open(path, O_RDONLY);
    if (fd < 0 && errno == EACCES) {
        fprintf(stderr, "Помилка доступу до %s: потрібні права root (sudo) через захист PLATYPUS.\n", path);
    }
    return fd;
}

static uint64_t read_energy_uj(int fd) {
    if (fd < 0) return 0;
    char buf[32];
    ssize_t bytes = pread(fd, buf, sizeof(buf) - 1, 0);
    if (bytes <= 0) return 0;
    buf[bytes] = '\0';
    return (uint64_t)strtoull(buf, NULL, 10);
}

bool rapl_meter_init(rapl_meter_t *meter) {
    memset(meter, 0, sizeof(*meter));
    meter->fd_pkg = open_sensor(RAPL_PKG_PATH);
    if (meter->fd_pkg < 0) {
        return false;
    }
    meter->fd_core = open_sensor(RAPL_CORE_PATH);
    meter->fd_dram = open_sensor(RAPL_DRAM_PATH);
    return true;
}

void rapl_meter_start(rapl_meter_t *meter) {
    meter->start_energy_pkg = read_energy_uj(meter->fd_pkg);
    meter->start_energy_core = read_energy_uj(meter->fd_core);
    meter->start_energy_dram = read_energy_uj(meter->fd_dram);
    clock_gettime(CLOCK_MONOTONIC, &meter->start_time);
}

void rapl_meter_stop(const rapl_meter_t *meter, rapl_result_t *res) {
    struct timespec end_time;
    clock_gettime(CLOCK_MONOTONIC, &end_time);

    uint64_t end_pkg = read_energy_uj(meter->fd_pkg);
    uint64_t end_core = read_energy_uj(meter->fd_core);
    uint64_t end_dram = read_energy_uj(meter->fd_dram);

    double sec = (double)(end_time.tv_sec - meter->start_time.tv_sec) +
                 (double)(end_time.tv_nsec - meter->start_time.tv_nsec) / 1e9;
    res->duration_sec = sec;

    // Обробка приросту з захистом від переповнення (sysfs віддає 64-бітне нормалізоване значення)
    uint64_t d_pkg = (end_pkg >= meter->start_energy_pkg) ? 
                     (end_pkg - meter->start_energy_pkg) : 0;
    uint64_t d_core = (end_core >= meter->start_energy_core) ? 
                      (end_core - meter->start_energy_core) : 0;
    uint64_t d_dram = (end_dram >= meter->start_energy_dram) ? 
                      (end_dram - meter->start_energy_dram) : 0;

    res->energy_pkg_joules = (double)d_pkg / 1e6;
    res->energy_core_joules = (double)d_core / 1e6;
    res->energy_dram_joules = (double)d_dram / 1e6;

    res->power_pkg_watts = (sec > 0.0) ? (res->energy_pkg_joules / sec) : 0.0;
    res->power_core_watts = (sec > 0.0) ? (res->energy_core_joules / sec) : 0.0;
    res->power_dram_watts = (sec > 0.0) ? (res->energy_dram_joules / sec) : 0.0;
}

void rapl_meter_close(rapl_meter_t *meter) {
    if (meter->fd_pkg >= 0) close(meter->fd_pkg);
    if (meter->fd_core >= 0) close(meter->fd_core);
    if (meter->fd_dram >= 0) close(meter->fd_dram);
}

// Тестове обчислювальне навантаження (множення масиву чисел з плаваючою комою)
static void compute_heavy_workload(size_t n) {
    volatile double acc = 1.0;
    for (size_t i = 1; i <= n; ++i) {
        acc = acc * 1.0000001 + (double)(i & 0xFF) * 0.00001;
    }
}

int main(void) {
    rapl_meter_t meter;
    if (!rapl_meter_init(&meter)) {
        fprintf(stderr, "Не вдалося ініціалізувати сенсори RAPL.\n");
        return 1;
    }

    printf("Вимірювання енергоспоживання обчислювального блоку...\n");
    rapl_meter_start(&meter);

    compute_heavy_workload(150000000);

    rapl_result_t res;
    rapl_meter_stop(&meter, &res);
    rapl_meter_close(&meter);

    printf("=== Результати вимірювання (C API) ===\n");
    printf("Час виконання:      %.4f с\n", res.duration_sec);
    printf("Енергія Package:    %.4f Дж  (Потужність: %.2f Вт)\n", res.energy_pkg_joules, res.power_pkg_watts);
    printf("Енергія Cores:      %.4f Дж  (Потужність: %.2f Вт)\n", res.energy_core_joules, res.power_core_watts);
    if (res.energy_dram_joules > 0.0) {
        printf("Енергія DRAM:       %.4f Дж  (Потужність: %.2f Вт)\n", res.energy_dram_joules, res.power_dram_watts);
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <chrono>
#include <expected>
#include <system_error>
#include <format>
#include <fcntl.h>
#include <unistd.h>

class UniqueFd {
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_{fd} {}
    ~UniqueFd() noexcept { if (fd_ >= 0) ::close(fd_); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_{other.fd_} { other.fd_ = -1; }
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

private:
    int fd_{-1};
};

struct EnergySample {
    double duration_seconds{0.0};
    double package_joules{0.0};
    double core_joules{0.0};
    double dram_joules{0.0};

    [[nodiscard]] double package_power_watts() const noexcept {
        return (duration_seconds > 0.0) ? (package_joules / duration_seconds) : 0.0;
    }
    [[nodiscard]] double core_power_watts() const noexcept {
        return (duration_seconds > 0.0) ? (core_joules / duration_seconds) : 0.0;
    }
    [[nodiscard]] double dram_power_watts() const noexcept {
        return (duration_seconds > 0.0) ? (dram_joules / duration_seconds) : 0.0;
    }
};

class ScopedEnergyProfiler {
public:
    static std::expected<ScopedEnergyProfiler, std::error_code> create() {
        ScopedEnergyProfiler profiler;
        profiler.fd_pkg_ = open_sensor("/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj");
        if (!profiler.fd_pkg_.valid()) {
            return std::unexpected(std::make_error_code(std::errc::permission_denied));
        }
        profiler.fd_core_ = open_sensor("/sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:0/energy_uj");
        profiler.fd_dram_ = open_sensor("/sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:2/energy_uj");

        profiler.start_pkg_uj_ = profiler.read_energy(profiler.fd_pkg_);
        profiler.start_core_uj_ = profiler.read_energy(profiler.fd_core_);
        profiler.start_dram_uj_ = profiler.read_energy(profiler.fd_dram_);
        profiler.start_time_ = std::chrono::steady_clock::now();

        return profiler;
    }

    [[nodiscard]] EnergySample finish() const {
        const auto end_time = std::chrono::steady_clock::now();
        const std::chrono::duration<double> diff = end_time - start_time_;

        const uint64_t end_pkg = read_energy(fd_pkg_);
        const uint64_t end_core = read_energy(fd_core_);
        const uint64_t end_dram = read_energy(fd_dram_);

        const uint64_t d_pkg = (end_pkg >= start_pkg_uj_) ? (end_pkg - start_pkg_uj_) : 0;
        const uint64_t d_core = (end_core >= start_core_uj_) ? (end_core - start_core_uj_) : 0;
        const uint64_t d_dram = (end_dram >= start_dram_uj_) ? (end_dram - start_dram_uj_) : 0;

        return EnergySample{
            .duration_seconds = diff.count(),
            .package_joules = static_cast<double>(d_pkg) / 1e6,
            .core_joules = static_cast<double>(d_core) / 1e6,
            .dram_joules = static_cast<double>(d_dram) / 1e6
        };
    }

private:
    ScopedEnergyProfiler() = default;

    static UniqueFd open_sensor(std::string_view path) {
        int fd = ::open(path.data(), O_RDONLY);
        return UniqueFd(fd);
    }

    static uint64_t read_energy(const UniqueFd& fd) {
        if (!fd.valid()) return 0;
        char buf[32];
        ssize_t bytes = ::pread(fd.get(), buf, sizeof(buf) - 1, 0);
        if (bytes <= 0) return 0;
        buf[bytes] = '\0';
        return std::stoull(buf);
    }

    UniqueFd fd_pkg_;
    UniqueFd fd_core_;
    UniqueFd fd_dram_;
    uint64_t start_pkg_uj_{0};
    uint64_t start_core_uj_{0};
    uint64_t start_dram_uj_{0};
    std::chrono::steady_clock::time_point start_time_;
};

void run_vector_computation(std::vector<double>& data) {
    for (size_t iter = 0; iter < 100; ++iter) {
        for (double& val : data) {
            val = (val * 1.00001) + 0.5;
        }
    }
}

int main() {
    auto profiler_exp = ScopedEnergyProfiler::create();
    if (!profiler_exp.has_value()) {
        std::cerr << "Помилка ініціалізації RAPL: переконайтеся у наявності прав root.\n";
        return 1;
    }

    std::vector<double> benchmark_data(20'000'000, 1.25);
    std::cout << "Запуск обчислень для профілювання енергії (C++20)...\n";

    const auto& profiler = profiler_exp.value();
    run_vector_computation(benchmark_data);
    const auto result = profiler.finish();

    std::cout << "\n=== Енергетичний звіт (C++ RAII Profiler) ===\n";
    std::cout << std::format("Час виконання:      {:.4f} с\n", result.duration_seconds);
    std::cout << std::format("Енергія Package:    {:.4f} Дж  (Потужність: {:.2f} Вт)\n", 
                             result.package_joules, result.package_power_watts());
    std::cout << std::format("Енергія Cores:      {:.4f} Дж  (Потужність: {:.2f} Вт)\n", 
                             result.core_joules, result.core_power_watts());
    if (result.dram_joules > 0.0) {
        std::cout << std::format("Енергія DRAM:       {:.4f} Дж  (Потужність: {:.2f} Вт)\n", 
                                 result.dram_joules, result.dram_power_watts());
    }

    return 0;
}
```
:::

### Методологія проведення вимірювань та налаштування оточення

Щоб результати вимірювання енергії були стабільними та відтворюваними між різними запусками, системне середовище Linux вимагає попередньої конфігурації.

#### 1. Стабілізація тактової частоти процесора (DVFS)

За замовчуванням планувальник Linux використовує енергозберігаючий регулятор частоти `powersave` або `schedutil`. Коли тестовий алгоритм починає роботу, процесор перебуває на мінімальній частоті (наприклад, 800 МГц або 1.2 ГГц). Лише через 10–30 мілісекунд підсистема `intel_pstate` фіксує 100% завантаження ядра та підвищує частоту до максимального Turbo Boost. 

Ця перехідна фаза спотворює вимірювання, оскільки перші мілісекунди код виконується з низькою енергоефективністю. Перед запуском профілювальника слід примусово перевести всі ядра у фіксований високопродуктивний режим:

```
sudo cpupower frequency-set -g performance
```

Ця команда змушує драйвер P-станів зафіксувати максимальну гарантовану частоту без динамічного скидання в стани простою під час пауз між ітераціями.

#### 2. Апаратна ізоляція ядер та прив'язка потоків (CPU Pinning)

Лічильники домену `PKG` фіксують сумарну енергію всіх логічних ядер сокета. Якщо під час профілювання на сусідньому ядрі операційна система почне індексацію файлів, виділення пам'яті або обробку мережевих пакетів, їхнє енергоспоживання додасться до результату вашого бенчмарку.

Для ізоляції тестового процесу використовують утиліту `taskset` або механізм `cgroups`:

```
sudo taskset -c 2 ./energy_profiler
```

Ця команда жорстко прив'язує виконання алгоритму до фізичного ядра номер 2, виключаючи міграцію потоку між різними ядрами та кешами L2/L3.

#### 3. Налаштування прав доступу без повного sudo

Через обмеження безпеки PLATYPUS файли `energy_uj` за замовчуванням доступні лише користувачу `root`. Щоб дозволити запуск профілювальника звичайним інженерам без надання повних привілеїв суперкористувача, рекомендується створити окрему системну групу `energy` та прописати правило для демона `udev`:

```
# Створення правила udev у файлі /etc/udev/rules.d/99-powercap.rules:
SUBSYSTEM=="powercap", ACTION=="add", RUN+="/bin/chmod -R g+r /sys/class/powercap/intel-rapl/"
```

Після перезавантаження правил `udevadm control --reload-rules && udevadm trigger` члени групи `energy` отримують право безпечного читання лічильників енергії у просторі користувача.

### Аналіз енергетичної ефективності алгоритмів

На основі зібраних метрик можна розрахувати фундаментальні показники енергетичної якості програмного забезпечення:
- **Енергетична вартість операції (Joules per Operation / JPO)**: показує, скільки наноджоулів витрачає процесор на обробку одного елемента даних або одного запиту до бази даних:
  ```
  JPO = ΔE_Joules / Кількість_Операцій
  ```
- **Обчислювальна енергоефективність (MFLOPS / Watt або GFLOPS / Watt)**: ключова метрика для суперкомп'ютерів (список Green500). Вона визначає кількість мільйонів операцій із плаваючою комою, виконаних на один спожитий ват електричної потужності:
  ```
  Ефективність = (Всього_FLOPS / 10⁶) / ΔE_Joules
  ```

Оптимізація алгоритмів під мінімізацію споживання Джоулів часто дає інші архітектурні висновки, ніж чиста оптимізація за часом. Наприклад, агресивна векторизація AVX-512 скорочує час виконання на 30%, але може підвищити споживану потужність на 70%, що робить загальну витрату енергії вищою, ніж при використанні енергоефективніших інструкцій AVX2 на помірних тактових частотах.

#### 4. Багатопотокове масштабування та паралелізм (OpenMP)

При переході від однопотокового виконання до паралельних обчислень за допомогою бібліотеки OpenMP або потоків `std::jthread` енергетична поведінка системи зазнає істотних змін:
- **Закон спадної віддачі енергоефективності**: подвоєння кількості активних ядер (наприклад, з 4 до 8) скорочує час виконання задачі майже вдвічі, проте сумарна енергія сокета PKG не зменшується пропорційно. Додаткові ядра вимагають вищої напруги на загальній шині живлення, а конкуренція за спільний кеш L3 (LLC) та канали пам'яті викликає енергетичні простої конвеєрів (*stall cycles*).
- **Насичення пропускної здатності пам'яті (Memory Wall)**: якщо алгоритм обмежений швидкістю шини оперативної пам'яті (memory-bound, наприклад, сканування гігабайтних масивів чи пошук у графах), подальше додавання потоків не прискорює розрахунок, але призводить до різкого зростання споживання домену DRAM та шини Uncore.
- **Оптимальна робоча точка (Energy-Delay Product / EDP)**: для пошуку балансу між швидкістю та витратами використовують метрику `EDP = ΔE · Δt`. Мінімальне значення цього добутку вказує на оптимальну кількість потоків і P-стан, за яких обчислювальна задача завершується максимально швидко без марнотратного перегріву сокета.
