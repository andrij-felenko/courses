# ⚙️ Практична ізоляція ядра та вимірювання джитера: C та C++

Створення додатків із гарантованою субмікросекундною передбачуваністю вимагає ретельної підготовки середовища виконання у користувацькому просторі (userspace). Навіть якщо ядро Linux зібрано з опцією `CONFIG_NO_HZ_FULL` і завантажено з `nohz_full=`, звичайний процес користувача продовжує зазнавати витіснення планувальником CFS, сторінкових помилок (Page Faults) та затримок виділення пам'яті, якщо потік не виконає специфічний протокол ініціалізації.

Ця вставка містить повністю працездатний виробничий шаблон програми для низькозатримкових обчислень мовами C та C++. Програма виконує чотири критичні етапи ініціалізації перед входом у гарячий обчислювальний цикл:

1. **Прив'язка потоку до ізольованого ядра (`pthread_setaffinity_np`):** Примусове закріплення потоку за виділеним CPU запобігає його міграції планувальником на інші ядра, що усуває скидання L1/L2 кешів та перезавантаження TLB.
2. **Встановлення режиму реального часу `SCHED_FIFO`:** Надання потоку найвищого статичного пріоритету реального часу (пріоритет 99) виключає можливість його витіснення звичайними процесами системи (`SCHED_OTHER`).
3. **Блокування пам'яті у фізичному DRAM (`mlockall`):** Фіксація всієї поточної та майбутньої віртуальної пам'яті у фізичній оперативній пам'яті унеможливлює вивантаження сторінок у swap та виникнення сторінкових помилок під час виконання.
4. **Попереднє прогрівання пам'яті (Memory Pre-warming):** Явне звернення до всіх виділених буферів (`memset`) змушує ядро виконати реальну алокацію фізичних сторінок та оновити таблиці сторінок (Page Tables) до входу в критичний цикл.

Після завершення ініціалізації програма занурюється у гарячий цикл без системних викликів, обчислюючи максимальне тремтіння затримок (OS jitter) у наносекундах за допомогою vDSO-викликів `clock_gettime(CLOCK_MONOTONIC_RAW)`.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>
#include <pthread.h>
#include <sched.h>
#include <sys/mman.h>
#include <time.h>
#include <errno.h>

#define TARGET_CPU 1
#define ITERATIONS 10000000
#define JITTER_THRESHOLD_NS 1000

static inline uint64_t get_time_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC_RAW, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

int setup_thread_isolation(int cpu_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);

    pthread_t thread = pthread_self();
    if (pthread_setaffinity_np(thread, sizeof(cpu_set_t), &cpuset) != 0) {
        perror("pthread_setaffinity_np failed");
        return -1;
    }

    struct sched_param param;
    param.sched_priority = 99; // Найвищий пріоритет SCHED_FIFO
    if (pthread_setschedparam(thread, SCHED_FIFO, &param) != 0) {
        perror("pthread_setschedparam failed (потрібні права root)");
        return -1;
    }

    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        perror("mlockall failed");
        return -1;
    }

    return 0;
}

int main(void) {
    printf("Ініціалізація ізоляції для CPU %d...\n", TARGET_CPU);
    if (setup_thread_isolation(TARGET_CPU) != 0) {
        fprintf(stderr, "Помилка налаштування ізоляції\n");
        return EXIT_FAILURE;
    }

    // Попереднє прогрівання пам'яті (запобігання page faults)
    volatile uint8_t dummy_buffer[1024 * 1024];
    memset((void*)dummy_buffer, 0, sizeof(dummy_buffer));

    printf("Запуск гарячого циклу вимірювання затримок...\n");

    uint64_t max_jitter_ns = 0;
    uint64_t prev_time = get_time_ns();

    for (uint64_t i = 0; i < ITERATIONS; ++i) {
        uint64_t current_time = get_time_ns();
        uint64_t delta = current_time - prev_time;
        prev_time = current_time;

        // Порожня ітерація коштує десятки наносекунд, тож усе, що довше
        // за поріг, — це втручання ззовні циклу, а сама дельта і є його ціна.
        if (i > 0 && delta > JITTER_THRESHOLD_NS) {
            if (delta > max_jitter_ns) {
                max_jitter_ns = delta;
            }
        }
    }

    printf("Вимірювання завершено.\n");
    printf("Максимальний OS jitter: %" PRIu64 " наносекунд\n", max_jitter_ns);

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <vector>
#include <chrono>
#include <stdexcept>
#include <system_error>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <cerrno>
#include <pthread.h>
#include <sched.h>
#include <sys/mman.h>

class ThreadIsolator {
public:
    static void isolate_current_thread(int cpu_id) {
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(cpu_id, &cpuset);

        if (int err = pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset); err != 0) {
            throw std::system_error(err, std::generic_category(), "pthread_setaffinity_np failed");
        }

        sched_param param{.sched_priority = 99};
        if (int err = pthread_setschedparam(pthread_self(), SCHED_FIFO, &param); err != 0) {
            throw std::system_error(err, std::generic_category(), "pthread_setschedparam failed (потрібні права root)");
        }

        if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
            throw std::system_error(errno, std::generic_category(), "mlockall failed");
        }
    }
};

int main() {
    constexpr int target_cpu = 1;
    constexpr uint64_t iterations = 10000000;
    constexpr int64_t jitter_threshold_ns = 1000;

    try {
        std::cout << "Ініціалізація ізоляції для CPU " << target_cpu << "...\n";
        ThreadIsolator::isolate_current_thread(target_cpu);

        // RAII-буфер з попередньою ініціалізацією (запобігає page faults)
        std::vector<uint8_t> warm_buffer(1024 * 1024, 0);
        volatile uint8_t sink = warm_buffer[0];
        (void)sink;

        std::cout << "Запуск гарячого циклу вимірювання затримок...\n";

        uint64_t max_jitter_ns = 0;
        auto prev_time = std::chrono::steady_clock::now();

        for (uint64_t i = 0; i < iterations; ++i) {
            auto current_time = std::chrono::steady_clock::now();
            auto delta_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(current_time - prev_time).count();
            prev_time = current_time;

            if (i > 0 && delta_ns > jitter_threshold_ns) {
                const auto jitter = static_cast<uint64_t>(delta_ns);
                if (jitter > max_jitter_ns) {
                    max_jitter_ns = jitter;
                }
            }
        }

        std::cout << "Вимірювання завершено.\n";
        std::cout << "Максимальний OS jitter: " << max_jitter_ns << " наносекунд\n";

    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

### Поглиблений аналіз елементів реалізації

#### 1. Механіка прив'язки потоку (`pthread_setaffinity_np`)
Функція `pthread_setaffinity_np` є обгорткою над системним викликом `sched_setaffinity`. Вона встановлює бітову маску спорідненості потоку з логічними ядрами CPU. Передача маски з одного біта `CPU_SET(cpu_id, &cpuset)` гарантує, що планувальник ядра Linux CFS ніколи не мігруватиме цей потік на інші ядра.

Міграція потоку між ядрами є однією з найдорожчих операцій у системі. Сучасні x86/ARM процесори володіють багаторівневою ієрархією кеш-пам'яті: первинний кеш даних L1d (32-64 КБ) та кеш інструкцій L1i (32 КБ) є індивідуальними для кожного ядра, кеш другого рівня L2 (512 КБ - 1 МБ) є також локальним для ядра. 

Коли потік мігрує на інше ядро, всі його гарячі дані залишаються в кеші попереднього ядра. Нове ядро зазнає суцільних промахів кешу (*cache misses*), що викликає вимушені звернення до повільнішої загальної кеш-пам'яті L3 або до фізичної оперативної пам'яті DRAM. Крім того, міграція вимагає надсилання міжпроцесорних переривань IPI (*Inter-Processor Interrupts*) та перезавантаження буферів асоціативної трансляції адреси TLB (*Translation Lookaside Buffer*).

#### 2. Пріоритет реального часу (`SCHED_FIFO`)
За замовчуванням усі процеси в Linux запускаються під управлінням планувальника `SCHED_OTHER` (CFS), де квант часу розраховується динамічно на основі значення `nice`. Встановлення політики `SCHED_FIFO` із пріоритетом `99` (максимум, який повертає `sched_get_priority_max(SCHED_FIFO)` у Linux; POSIX вимагає лише 32 рівні, тож число залежить від системи) переводить потік у клас реального часу (*real-time scheduling class*). 

На відміну від `SCHED_RR` (Round-Robin), де потоки однакового пріоритету витісняють один одного після закінчення кванта часу, потік `SCHED_FIFO` володіє абсолютним пріоритетом над будь-яким звичайним процесом. Він виконуватиметься нескінченно доти, доки сам не заблокується на I/O або не віддасть управління викликом `sched_yield()`. 

Для успішного виконання `pthread_setschedparam` процес мусить володіти привілегією `CAP_SYS_NICE` або запускатися від імені суперкористувача `root`. Обмеження `RLIMIT_MEMLOCK` та `RLIMIT_RTPRIO` у `/etc/security/limits.conf` також мають бути відкориговані.

#### 3. Фіксація віртуальної пам'яті (`mlockall`)
Виклик `mlockall(MCL_CURRENT | MCL_FUTURE)` повідомляє підсистему управління пам'яттю ядра (Virtual Memory Manager, VMM) про необхідність заблокувати всі сторінки віртуального адресного простору процесу у фізичній оперативній пам'яті (DRAM).
- `MCL_CURRENT`: Фіксує всі сторінки, відображені в адресний простір на даний момент (код, стек, купа).
- `MCL_FUTURE`: Автоматично фіксує будь-які майбутні сторінки, які будуть виділені через `brk`, `sbrk` або `mmap`.

Це гарантує, що підсистема свопінгу ядра не зможе вивантажити сторінки процесу на диск чи в zRAM, усуваючи затримки Major Page Faults (які можуть досягати десятків мілісекунд при виклику дискового I/O).

#### 4. Прогрівання пам'яті (Memory Pre-warming)
У Linux виділення пам'яті через `malloc()` або `std::vector` є лінивим (*lazy allocation*): ядро лише виділяє діапазон віртуальних адрес, але не виділяє реальних фізичних кадрів DRAM до першого запису. Перше звернення до кожної 4-кілобайтної сторінки викликає Minor Page Fault — процесор генерує переривання, перемикається в ядро, алокує фізичну сторінку та оновлює таблиці сторінок Page Table.

Заповнення буфера через `memset` (або `std::vector` з дефолтним значенням) перед входом у критичний цикл змушує ядро обробити всі Minor Page Faults заздалегідь. У результаті під час виконання гарячого циклу кожна сторінка пам'яті вже відображена на фізичний DRAM-кадр, і звернення до пам'яті виконуються з апаратною швидкістю шини пам'яті.

#### 5. Вимірювання часу через vDSO
Функція `clock_gettime(CLOCK_MONOTONIC_RAW)` у сучасних системах Linux реалізована через механізм vDSO (virtual dynamically linked shared object). Ядро мапить сторінку з поточним часом безпосередньо в адресний простір користувацького процесу. 

Використання годинника `CLOCK_MONOTONIC_RAW` є критичним для систем низької затримки, оскільки він надає абсолютний монотонний час апаратного таймера без корекцій з боку демонів NTP (`ntpd`, `chronyd`) та викликів `adjtimex`. Виклик `clock_gettime` зчитує лічильник `RDTSC` процесора без виконання системного виклику (`syscall`) та без перемикання контексту в режим ядра Ring 0 — а отже, не додає до гарячого циклу ані вартості переходу через Context Tracking, ані шансу нажити залежність, яка поверне тик.

Три застереження до цього твердження, кожне з яких перевіряється на місці:
- **vDSO працює не з усяким джерелом часу.** Швидкий шлях існує, поки системне джерело — `tsc`; при `hpet` чи `acpi_pm` vDSO мовчки падає у справжній системний виклик. Перевірка: `cat /sys/devices/system/clocksource/clocksource0/current_clocksource`.
- **Не всі годинники завжди були у vDSO.** `CLOCK_MONOTONIC_RAW` дістав реалізацію в vDSO пізніше за `CLOCK_MONOTONIC`; на старих ядрах той самий код тихо йшов через `syscall`. Остаточну відповідь дає `strace` на вашій машині: на справжньому vDSO-шляху жодного `clock_gettime` у виводі не буде.
- **Вкладка C++ вище міряє іншим годинником.** `std::chrono::steady_clock` у glibc відображається на `CLOCK_MONOTONIC`, а не на `_RAW`, тобто його хід підправляє NTP. Для вимірювань тривалістю в секунди різниця мізерна, але якщо потрібен саме нескоригований апаратний час — і в C++ викликають `clock_gettime(CLOCK_MONOTONIC_RAW, …)` напряму.
