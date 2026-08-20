# ⚙️ Дослідження швидкодії SMT та керування прив'язкою ниток

Апаратна багатонитковість створює ілюзію наявності додаткових обчислювальних ядер, проте спільне використання ресурсів фізичного кристала здатне як відчутно прискорити паралельну програму, так і спричинити помітне падіння загальної продуктивності. Коли дві нитки одночасно претендують на одні й ті самі виконавчі порти, цілочислові суматори чи лінії кешу першого рівня, апаратний планувальник ядра змушений чергувати видачу мікрооперацій. Щоб оптимізувати обчислювальні конвеєри, розробник повинен вміти визначати апаратну топологію системи, виявляти споріднені логічні процесори (англ. *sibling hyperthreads*) та явно керувати масками прив'язки ниток (англ. *CPU affinity*).

### Пастки нумерації логічних процесорів у Linux

Поширена помилка розробників — припущення, що логічні процесори одного фізичного ядра завжди мають сусідні індекси (наприклад, `CPU 0` та `CPU 1`). Насправді схема призначення ідентифікаторів у ядрі Linux залежить від таблиць ACPI MADT (англ. *Multiple APIC Description Table*) материнської плати та порядку ініціалізації:

- **Послідовна схема (Intel Core настільних ПК):** парні та непарні індекси або сусідні числа (наприклад, `CPU 0` та `CPU 1` ділять Core 0).
- **Блокова схема (багатосокетні сервери AMD EPYC та Intel Xeon):** перша половина індексів відповідає першим ниткам усіх фізичних ядер (`CPU 0..31`), а друга половина — їхнім SMT-двійникам (`CPU 32..63`). У такій системі спорідненою парою для `CPU 0` є `CPU 32`, а не `CPU 1`.

Спроба «вгадати» номер SMT-двійника математичним додаванням призводить до фатальних помилок планування: програма замість розподілу по окремих фізичних ядрах може випадково помістити всі потоки на одне ядро або зачепити повільний канал [NUMA](book:programming/numa). Єдиним надійним способом є читання системного файлу `thread_siblings_list` у `/sys`.

### Анатомія експерименту

Нижче наведено практичний інструмент, який визначає пари SMT-процесорів через системну файлову систему Linux `/sys` і досліджує поведінку конвеєра в кількох контрольованих сценаріях:

1. **Цілочислове навантаження на спільних АЛП (конкуренція за обчислювальні порти):** обидві нитки безперервно виконують щільні ланцюжки арифметичних операцій. Оскільки кількість цілочислових блоків у ядрі фіксована, фізичний конвеєр стає вузьким місцем.
2. **Змішане навантаження (синергія та взаємне доповнення ресурсів):** перша нитка навантажує АЛП, а друга нитка виконує стрибкоподібне сканування великого масиву в пам'яті (16 МБ, що суттєво перевищує об'єм L2-кешу). Поки друга нитка перебуває у стані очікування даних з оперативної пам'яті, перша нитка захоплює всі вільні слоти станцій резервування та порти ядра.
3. **Порівняння з ізольованими фізичними ядрами:** ті самі тести запускаються на двох процесорах, що належать різним фізичним ядрам, що слугує еталоном для оцінки накладних витрат SMT.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <pthread.h>
#include <sched.h>
#include <time.h>
#include <unistd.h>

#define ITERATIONS 500000000ULL
#define ARRAY_SIZE (16 * 1024 * 1024) /* 16 МБ, суттєво більше за L2 кеш */

typedef struct {
    int cpu_id;
    int mode; /* 0 = обчислення (ALU), 1 = пам'ять (Load/Store) */
    uint64_t result;
    uint32_t *shared_array;
} thread_arg_t;

/* Отримання монотонного часу високої точності в мікросекундах */
static uint64_t get_time_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000ULL + (uint64_t)ts.tv_nsec / 1000ULL;
}

/* Робоче навантаження для тестування мікроархітектури */
static void *worker_function(void *arg) {
    thread_arg_t *tdata = (thread_arg_t *)arg;

    /* Прив'язка поточної нитки до вказаного логічного процесора */
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(tdata->cpu_id, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    if (tdata->mode == 0) {
        /* ALU-bound: інтенсивне навантаження на обчислювальні порти */
        uint64_t acc = 0x12345678ULL;
        for (uint64_t i = 0; i < ITERATIONS; ++i) {
            acc = (acc ^ (i * 0x5DEECE66DULL + 0xBULL)) + (acc >> 3);
        }
        tdata->result = acc;
    } else {
        /* Memory-bound: випадковий доступ, очікування ліній пам'яті */
        uint32_t *arr = tdata->shared_array;
        uint32_t idx = 0;
        uint64_t sum = 0;
        for (uint64_t i = 0; i < (ITERATIONS / 10); ++i) {
            idx = arr[idx & (ARRAY_SIZE - 1)];
            sum += idx;
        }
        tdata->result = sum;
    }
    return NULL;
}

/* Читання спорідненого SMT-процесора для вказаного CPU */
static int get_sibling_cpu(int cpu_id) {
    char path[128];
    snprintf(path, sizeof(path), "/sys/devices/system/cpu/cpu%d/topology/thread_siblings_list", cpu_id);
    FILE *f = fopen(path, "r");
    if (!f) return -1;

    char buf[64];
    if (!fgets(buf, sizeof(buf), f)) {
        fclose(f);
        return -1;
    }
    fclose(f);

    int sibling = -1;
    char *token = strtok(buf, ",-\n");
    while (token) {
        int val = atoi(token);
        if (val != cpu_id) {
            sibling = val;
            break;
        }
        token = strtok(NULL, ",-\n");
    }
    return sibling;
}

int main(void) {
    int cpu0 = 0;
    int cpu0_sibling = get_sibling_cpu(cpu0);

    if (cpu0_sibling < 0 || cpu0_sibling == cpu0) {
        fprintf(stderr, "Помилка: SMT вимкнено або не знайдено спорідненого процесора для CPU %d\n", cpu0);
        return 1;
    }

    /* Знаходимо інший фізичний процесор, який не ділить ядро з CPU 0 */
    int cpu_isolated = -1;
    long num_cpus = sysconf(_SC_NPROCESSORS_ONLN);
    for (int i = 1; i < num_cpus; ++i) {
        if (i != cpu0_sibling) {
            cpu_isolated = i;
            break;
        }
    }

    if (cpu_isolated < 0) {
        fprintf(stderr, "Потрібно щонайменше два фізичні ядра для тестування\n");
        return 1;
    }

    printf("Конфігурація тесту:\n");
    printf("  Фізичне ядро 0 (SMT-пара): CPU %d та CPU %d\n", cpu0, cpu0_sibling);
    printf("  Окреме фізичне ядро:      CPU %d\n\n", cpu_isolated);

    /* Підготовка масиву для тестування пам'яті */
    uint32_t *mem_arr = (uint32_t *)malloc(ARRAY_SIZE * sizeof(uint32_t));
    if (!mem_arr) return 1;
    for (size_t i = 0; i < ARRAY_SIZE; ++i) {
        mem_arr[i] = (uint32_t)((i * 1664525U + 1013904223U) % ARRAY_SIZE);
    }

    pthread_t th0, th1;
    thread_arg_t args[2];

    /* ── Тест 1: Два ALU-потоки на одному SMT-ядрі (конкуренція) ── */
    args[0].cpu_id = cpu0; args[0].mode = 0; args[0].shared_array = mem_arr;
    args[1].cpu_id = cpu0_sibling; args[1].mode = 0; args[1].shared_array = mem_arr;

    uint64_t t_start = get_time_us();
    pthread_create(&th0, NULL, worker_function, &args[0]);
    pthread_create(&th1, NULL, worker_function, &args[1]);
    pthread_join(th0, NULL);
    pthread_join(th1, NULL);
    uint64_t t_smt_alu = get_time_us() - t_start;

    /* ── Тест 2: Два ALU-потоки на окремих фізичних ядрах (ізоляція) ── */
    args[0].cpu_id = cpu0; args[0].mode = 0;
    args[1].cpu_id = cpu_isolated; args[1].mode = 0;

    t_start = get_time_us();
    pthread_create(&th0, NULL, worker_function, &args[0]);
    pthread_create(&th1, NULL, worker_function, &args[1]);
    pthread_join(th0, NULL);
    pthread_join(th1, NULL);
    uint64_t t_iso_alu = get_time_us() - t_start;

    /* ── Тест 3: Змішане навантаження (ALU + Memory) на SMT ── */
    args[0].cpu_id = cpu0; args[0].mode = 0;
    args[1].cpu_id = cpu0_sibling; args[1].mode = 1;

    t_start = get_time_us();
    pthread_create(&th0, NULL, worker_function, &args[0]);
    pthread_create(&th1, NULL, worker_function, &args[1]);
    pthread_join(th0, NULL);
    pthread_join(th1, NULL);
    uint64_t t_smt_mixed = get_time_us() - t_start;

    /* ── Тест 4: Змішане навантаження на окремих ядрах ── */
    args[0].cpu_id = cpu0; args[0].mode = 0;
    args[1].cpu_id = cpu_isolated; args[1].mode = 1;

    t_start = get_time_us();
    pthread_create(&th0, NULL, worker_function, &args[0]);
    pthread_create(&th1, NULL, worker_function, &args[1]);
    pthread_join(th0, NULL);
    pthread_join(th1, NULL);
    uint64_t t_iso_mixed = get_time_us() - t_start;

    printf("Результати вимірювань (час у мс):\n");
    printf("  1. Два ALU-потоки на одному SMT-ядрі:   %7.2f мс\n", t_smt_alu / 1000.0);
    printf("  2. Два ALU-потоки на окремих ядрах:     %7.2f мс (швидше на %.1f%%)\n",
           t_iso_alu / 1000.0, ((double)t_smt_alu / t_iso_alu - 1.0) * 100.0);
    printf("  3. Змішані (ALU + Mem) на SMT-ядрі:     %7.2f мс\n", t_smt_mixed / 1000.0);
    printf("  4. Змішані на окремих ядрах:            %7.2f мс (різниця лише %.1f%%)\n",
           t_iso_mixed / 1000.0, ((double)t_smt_mixed / t_iso_mixed - 1.0) * 100.0);

    free(mem_arr);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <thread>
#include <chrono>
#include <numeric>
#include <format>
#include <span>
#include <pthread.h>
#include <unistd.h>

namespace smt_bench {

constexpr uint64_t ITERATIONS = 500'000'000ULL;
constexpr size_t ARRAY_SIZE = 16 * 1024 * 1024; // 16 МБ

enum class WorkMode {
    ComputeAlu,
    MemoryAccess
};

struct ThreadTask {
    int cpu_id{0};
    WorkMode mode{WorkMode::ComputeAlu};
    uint64_t result{0};
    std::span<const uint32_t> memory_view{};
};

// Прив'язка поточної нитки до вказаного логічного процесора
void pin_current_thread_to_cpu(int cpu_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
}

void execute_task(ThreadTask& task) {
    pin_current_thread_to_cpu(task.cpu_id);

    if (task.mode == WorkMode::ComputeAlu) {
        uint64_t acc = 0x12345678ULL;
        for (uint64_t i = 0; i < ITERATIONS; ++i) {
            acc = (acc ^ (i * 0x5DEECE66DULL + 0xBULL)) + (acc >> 3);
        }
        task.result = acc;
    } else {
        const auto& arr = task.memory_view;
        uint32_t idx = 0;
        uint64_t sum = 0;
        for (uint64_t i = 0; i < (ITERATIONS / 10); ++i) {
            idx = arr[idx & (ARRAY_SIZE - 1)];
            sum += idx;
        }
        task.result = sum;
    }
}

int find_sibling_cpu(int cpu_id) {
    const std::string path = "/sys/devices/system/cpu/cpu" + std::to_string(cpu_id) + "/topology/thread_siblings_list";
    std::ifstream file(path);
    if (!file.is_open()) {
        return -1;
    }

    std::string line;
    if (!std::getline(file, line)) {
        return -1;
    }

    std::stringstream ss(line);
    std::string token;
    while (std::getline(ss, token, ',')) {
        try {
            int val = std::stoi(token);
            if (val != cpu_id) {
                return val;
            }
        } catch (...) {
            continue;
        }
    }
    return -1;
}

double measure_execution_ms(ThreadTask& t1, ThreadTask& t2) {
    auto start = std::chrono::steady_clock::now();

    std::jthread th1([&t1]() { execute_task(t1); });
    std::jthread th2([&t2]() { execute_task(t2); });

    th1.join();
    th2.join();

    auto end = std::chrono::steady_clock::now();
    return std::chrono::duration<double, std::milli>(end - start).count();
}

} // namespace smt_bench

int main() {
    using namespace smt_bench;

    const int cpu0 = 0;
    const int cpu0_sibling = find_sibling_cpu(cpu0);

    if (cpu0_sibling < 0 || cpu0_sibling == cpu0) {
        std::cerr << "Помилка: SMT вимкнено або не знайдено sibling для CPU " << cpu0 << '\n';
        return 1;
    }

    int cpu_isolated = -1;
    const long num_cpus = sysconf(_SC_NPROCESSORS_ONLN);
    for (int i = 1; i < num_cpus; ++i) {
        if (i != cpu0_sibling) {
            cpu_isolated = i;
            break;
        }
    }

    if (cpu_isolated < 0) {
        std::cerr << "Потрібно щонайменше два окремі фізичні ядра для тесту\n";
        return 1;
    }

    std::cout << "Конфігурація тесту:\n"
              << "  Фізичне ядро 0 (SMT-пара): CPU " << cpu0 << " та CPU " << cpu0_sibling << '\n'
              << "  Окреме фізичне ядро:      CPU " << cpu_isolated << "\n\n";

    std::vector<uint32_t> mem_buffer(ARRAY_SIZE);
    for (size_t i = 0; i < ARRAY_SIZE; ++i) {
        mem_buffer[i] = static_cast<uint32_t>((i * 1664525U + 1013904223U) % ARRAY_SIZE);
    }
    std::span<const uint32_t> mem_span{mem_buffer};

    // Тест 1: Конкуренція двох ALU на одному ядрі SMT
    ThreadTask task1_alu{cpu0, WorkMode::ComputeAlu, 0, mem_span};
    ThreadTask task2_alu_smt{cpu0_sibling, WorkMode::ComputeAlu, 0, mem_span};
    double t_smt_alu = measure_execution_ms(task1_alu, task2_alu_smt);

    // Тест 2: Два ALU на двох фізично окремих ядрах
    ThreadTask task2_alu_iso{cpu_isolated, WorkMode::ComputeAlu, 0, mem_span};
    double t_iso_alu = measure_execution_ms(task1_alu, task2_alu_iso);

    // Тест 3: Змішане навантаження на SMT
    ThreadTask task2_mem_smt{cpu0_sibling, WorkMode::MemoryAccess, 0, mem_span};
    double t_smt_mixed = measure_execution_ms(task1_alu, task2_mem_smt);

    // Тест 4: Змішане навантаження на ізольованих ядрах
    ThreadTask task2_mem_iso{cpu_isolated, WorkMode::MemoryAccess, 0, mem_span};
    double t_iso_mixed = measure_execution_ms(task1_alu, task2_mem_iso);

    std::cout << "Результати вимірювань (час у мс):\n"
              << "  1. Два ALU-потоки на одному SMT-ядрі:   " << t_smt_alu << " мс\n"
              << "  2. Два ALU-потоки на окремих ядрах:     " << t_iso_alu << " мс (швидше на "
              << ((t_smt_alu / t_iso_alu) - 1.0) * 100.0 << "%)\n"
              << "  3. Змішані (ALU + Mem) на SMT-ядрі:     " << t_smt_mixed << " мс\n"
              << "  4. Змішані на окремих ядрах:            " << t_iso_mixed << " мс (різниця лише "
              << ((t_smt_mixed / t_iso_mixed) - 1.0) * 100.0 << "%)\n";

    return 0;
}
```
:::

### Детальний аналіз мікроархітектурних метрик

Отримані під час тестування часові показники чітко розкривають внутрішню динаміку конвеєра:

1. **Конфлікт однакових виконавчих портів (Тести 1 і 2):**
   Коли дві нитки одночасно навантажують цілочислові АЛП, вони конкурують за обмежену кількість фізичних портів ядра (наприклад, Порти 0, 1, 5 і 6 в мікроархітектурі Intel Golden Cove). Оскільки кількість суматорів не подвоюється при увімкненні SMT, апаратний планувальник вимушений ділити слоти видачі навпіл. Час виконання обох ниток на SMT-парі зростає майже на 85–95% у порівнянні з виконанням на повністю незалежних фізичних ядрах.

2. **Взаємне заповнення бульбашок конвеєра (Тести 3 і 4):**
   У змішаному сценарії Нитка 1 завантажує АЛП, тоді як Нитка 2 більшу частину часу очікує підтягування ліній пам'яті з LLC та DRAM через блоки генерації адрес (AGU). Коли Нитка 2 зупиняється на тривалому промаху кешу (вертикальний простій), її мікрооперації перестають претендувати на обчислювальні порти. Планувальник ядра негайно заповнює вільні слоти командами Нитки 1. У результаті загальний час виконання змішаної пари на одному SMT-ядрі лише на 5–12% поступається двом окремим фізичним ядрам.

### Профілювання апаратними лічильниками продуктивності

Для детального вивчення поведінки SMT на рівні процесора доцільно скористатися підсистемою `perf` у Linux. Запуск програми з вимірюванням специфічних апаратних подій дозволяє підтвердити гіпотези:

```bash
perf stat -e \
  cycles,instructions,\
  uops_issued.any,\
  uops_retired.retire_slots,\
  resource_stalls.any,\
  l1d_pend_miss.pending \
  ./smt_bench
```

Під час аналізу звертають увагу на три ключові показники:
- `uops_issued.any` проти `cycles`: показує реальний середній темп видачі мікрооперацій (IPC ядра). При змішаному навантаженні на SMT цей показник наближається до 3.0–3.5, тоді як для однієї нитки він рідко перевищує 1.5.
- `resource_stalls.any`: демонструє кількість тактів, коли конвеєр зупинявся через переповнення станцій резервування (RS) або буфера перевпорядкування (ROB). У Тесті 1 цей лічильник різко зростає через блокування портів однакових типів.
- `l1d_pend_miss.pending`: фіксує сумарний час очікування пам'яті. Якщо дві нитки активно працюють з даними й перевищують ємність L1D кешу (зазвичай 32–48 КБ), цей лічильник виявляє взаємне витіснення кеш-ліній (англ. *cache thrashing*).

### Практичні висновки для розробника

На основі отриманих результатів формулюються ключові правила оптимізації багатопотокового програмного забезпечення:

- **Обчислювально щільні задачі (HPC, рендеринг, шифрування):** кількість робочих ниток пулу слід обмежувати кількістю **фізичних ядер**, прив'язуючи кожну нитку до окремого сокета/ядра. Запуск додаткових ниток на SMT-двійниках збільшує накладні витрати синхронізації та конкуренції за L1D/L2 кеш без суттєвого зростання швидкості.
- **Ввід-вивід та реактивні сервіси (вебсервери, проксі, бази даних):** кількість ниток варто збільшувати до кількості **всіх логічних процесорів** (фізичні ядра × 2). Оскільки більшість ниток регулярно блокуються на очікуванні сокетів або дисків, SMT дозволяє іншим готовим ниткам утилізувати процесорні такти без затримок.
