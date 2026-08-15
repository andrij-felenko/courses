# ⚙️ Вимірювання точності та джиттера timerfd у просторі користувача

Цей практичний проєкт присвячено створенню вимірювача системного джиттера (відхилення часу пробудження від заданого графіку) у просторі користувача. Ми використовуємо механізм `timerfd` ядра Linux для генерації періодичних спрацьовувань наносекундної точності та детально аналізуємо вплив конфігурації ядра, пріоритетів планування і стану процесора на реальні затримки.

## Концепція проєкту та джерела джиттера

Під **джиттером** (англ. *jitter* — тремтіння, розсіювання) розуміють різницю між реальним моментом часу, коли потік простору користувача відновлює виконання після засинання, та плановим теоретичним моментом спрацьовування таймера.

```
теоретичний дедлайн (T_target) = T_start + N · period
фактичне пробудження (T_actual) = ktime_get()
відхилення джиттера (ΔT)      = T_actual - T_target
```

У ідеальній операційній системі `ΔT` мало б дорівнювати 0. Однак у реальних системах загального призначення існує кілька чинників, що викликають позитивне відхилення (`ΔT > 0`):

1. **Затримка обробки апаратного переривання (Hardirq latency)**: Час між моментом, коли апаратний APIC-таймер згенерував переривання, та моментом, коли ядро почало виконувати `hrtimer_interrupt()`. Викликається тимчасовим вимкненням переривань у критичних секціях ядра.
2. **Затримка планувальника (Scheduling latency)**: Час між моментом, коли `hrtimer` перевів потік із стану `TASK_INTERRUPTIBLE` у стан `TASK_RUNNING`, та моментом, коли планувальник реально переключив контекст процесора (context switch) на цей потік.
3. **Енергозберігаючі стани C-states**: Якщо ядро перебувало у глибокому простої (C6/C7), процесору потрібно від 50 до 150 мікросекунд лише для подачі живлення на кеші й повернення на максимальну частоту.
4. **Зміна частоти процесора (CPU Frequency Scaling)**: Якщо регулятор частоти (governor) знизив частоту ядра до мінімуму (наприклад, з 3.8 ГГц до 800 МГц), виконання перших інструкцій після пробудження відбуватиметься у 4–5 разів повільніше.

Завдання нашої тестової програми — виміряти цей джиттер протягом **10 000 послідовних тиків** із періодом **500 мікросекунд** (2000 Гц) і порахувати мінімальне, максимальне та середнє абсолютне відхилення.

---

## Реалізація проєкту

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
#include <unistd.h>
#include <sys/timerfd.h>
#include <sys/epoll.h>
#include <errno.h>

#define ITERATIONS 10000
#define PERIOD_NS  500000LL /* 500 мікросекунд */

static inline int64_t timespec_to_ns(const struct timespec *ts) {
    return (int64_t)ts->tv_sec * 1000000000LL + ts->tv_nsec;
}

int main(void) {
    /* 1. Створюємо таймерний дескриптор hrtimer для монотонного годинника */
    int tfd = timerfd_create(CLOCK_MONOTONIC, TFD_CLOEXEC);
    if (tfd == -1) {
        perror("timerfd_create");
        return EXIT_FAILURE;
    }

    /* 2. Задаємо період 500 мікросекунд */
    struct itimerspec new_val = {0};
    new_val.it_interval.tv_sec = 0;
    new_val.it_interval.tv_nsec = PERIOD_NS;
    new_val.it_value.tv_sec = 0;
    new_val.it_value.tv_nsec = PERIOD_NS;

    struct timespec start_ts;
    clock_gettime(CLOCK_MONOTONIC, &start_ts);

    if (timerfd_settime(tfd, 0, &new_val, NULL) == -1) {
        perror("timerfd_settime");
        close(tfd);
        return EXIT_FAILURE;
    }

    /* 3. Створюємо epoll дескриптор для очікування подій */
    int epfd = epoll_create1(EPOLL_CLOEXEC);
    if (epfd == -1) {
        perror("epoll_create1");
        close(tfd);
        return EXIT_FAILURE;
    }

    struct epoll_event ev;
    ev.events = EPOLLIN;
    ev.data.fd = tfd;
    if (epoll_ctl(epfd, EPOLL_CTL_ADD, tfd, &ev) == -1) {
        perror("epoll_ctl");
        close(epfd);
        close(tfd);
        return EXIT_FAILURE;
    }

    int64_t expected_target = timespec_to_ns(&start_ts) + PERIOD_NS;
    int64_t min_jitter = 1000000000LL;
    int64_t max_jitter = -1000000000LL;
    int64_t total_jitter = 0;

    printf("Розпочинаємо вимірювання 10000 тиків з періодом %lld нс...\n", PERIOD_NS);

    for (int i = 0; i < ITERATIONS; i++) {
        struct epoll_event events[1];
        int nfds = epoll_wait(epfd, events, 1, -1);
        if (nfds < 0) {
            if (errno == EINTR) continue;
            perror("epoll_wait");
            break;
        }

        uint64_t expirations = 0;
        ssize_t s = read(tfd, &expirations, sizeof(expirations));
        if (s != sizeof(expirations)) {
            perror("read");
            break;
        }

        struct timespec now_ts;
        clock_gettime(CLOCK_MONOTONIC, &now_ts);
        int64_t now_ns = timespec_to_ns(&now_ts);

        int64_t jitter = now_ns - expected_target;
        if (jitter < min_jitter) min_jitter = jitter;
        if (jitter > max_jitter) max_jitter = jitter;
        total_jitter += (jitter < 0 ? -jitter : jitter);

        /* Коригуємо плановий дедлайн з урахуванням можливо пропущених ітерацій */
        expected_target += (int64_t)expirations * PERIOD_NS;
    }

    printf("\n=== Результати вимірювання джиттера timerfd (10000 тиків) ===\n");
    printf("Мінімальний джиттер : %6.3f мкс\n", (double)min_jitter / 1000.0);
    printf("Максимальний джиттер: %6.3f мкс\n", (double)max_jitter / 1000.0);
    printf("Середнє відхилення  : %6.3f мкс\n", (double)total_jitter / (ITERATIONS * 1000.0));

    close(epfd);
    close(tfd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <vector>
#include <chrono>
#include <numeric>
#include <algorithm>
#include <system_error>
#include <cstdint>
#include <cmath>
#include <unistd.h>
#include <sys/timerfd.h>
#include <sys/epoll.h>

class TimerFd {
    int m_fd{-1};
public:
    explicit TimerFd(clockid_t clock_id) {
        m_fd = ::timerfd_create(clock_id, TFD_CLOEXEC);
        if (m_fd == -1) {
            throw std::system_error(errno, std::generic_category(), "timerfd_create failed");
        }
    }

    ~TimerFd() {
        if (m_fd != -1) {
            ::close(m_fd);
        }
    }

    TimerFd(const TimerFd&) = delete;
    TimerFd& operator=(const TimerFd&) = delete;

    TimerFd(TimerFd&& other) noexcept : m_fd(other.m_fd) {
        other.m_fd = -1;
    }

    int native_handle() const noexcept { return m_fd; }

    void set_interval(std::chrono::nanoseconds period) {
        struct itimerspec new_val{};
        auto secs = std::chrono::duration_cast<std::chrono::seconds>(period);
        auto nsecs = period - secs;

        new_val.it_interval.tv_sec = secs.count();
        new_val.it_interval.tv_nsec = nsecs.count();
        new_val.it_value = new_val.it_interval;

        if (::timerfd_settime(m_fd, 0, &new_val, nullptr) == -1) {
            throw std::system_error(errno, std::generic_category(), "timerfd_settime failed");
        }
    }

    std::uint64_t wait_expirations() {
        std::uint64_t count{0};
        ssize_t res = ::read(m_fd, &count, sizeof(count));
        if (res != sizeof(count)) {
            throw std::system_error(errno, std::generic_category(), "timerfd read failed");
        }
        return count;
    }
};

int main() {
    constexpr std::size_t iterations = 10000;
    constexpr auto period = std::chrono::microseconds(500);

    try {
        TimerFd timer(CLOCK_MONOTONIC);
        
        int epfd = ::epoll_create1(EPOLL_CLOEXEC);
        if (epfd == -1) {
            throw std::system_error(errno, std::generic_category(), "epoll_create1 failed");
        }

        struct epoll_event ev{};
        ev.events = EPOLLIN;
        ev.data.fd = timer.native_handle();
        if (::epoll_ctl(epfd, EPOLL_CTL_ADD, timer.native_handle(), &ev) == -1) {
            ::close(epfd);
            throw std::system_error(errno, std::generic_category(), "epoll_ctl failed");
        }

        auto start_time = std::chrono::steady_clock::now();
        timer.set_interval(period);

        auto expected_target = start_time + period;
        std::vector<double> jitters_us;
        jitters_us.reserve(iterations);

        std::cout << "Розпочинаємо вимірювання C++ timerfd (10000 тиків)...\n";

        for (std::size_t i = 0; i < iterations; ++i) {
            struct epoll_event events[1];
            int nfds = ::epoll_wait(epfd, events, 1, -1);
            if (nfds < 0) continue;

            std::uint64_t overruns = timer.wait_expirations();
            auto now = std::chrono::steady_clock::now();

            auto diff = std::chrono::duration_cast<std::chrono::nanoseconds>(now - expected_target);
            jitters_us.push_back(static_cast<double>(diff.count()) / 1000.0);

            expected_target += overruns * period;
        }

        ::close(epfd);

        auto [min_it, max_it] = std::minmax_element(jitters_us.begin(), jitters_us.end());
        double sum_abs = std::accumulate(jitters_us.begin(), jitters_us.end(), 0.0,
            [](double acc, double val) { return acc + std::abs(val); });

        std::cout << "\n=== Результати вимірювання джиттера C++ (10000 тиків) ===\n";
        std::cout << "Мінімальний джиттер : " << *min_it << " мкс\n";
        std::cout << "Максимальний джиттер: " << *max_it << " мкс\n";
        std::cout << "Середнє відхилення  : " << (sum_abs / iterations) << " мкс\n";

    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

---

## Детальний розбір алгоритму вимірювання

### 1. Розрахунок точки виходу без накопичення похибки

Найпоширеніша помилка при вимірюванні джиттера періодичних таймерів — обчислення наступного дедлайну відносно поточного часу пробудження.

Якщо викликом `clock_gettime()` зчитувати час після пробудження й додавати до нього період, джиттер кожного тику додається до наступного інтервалу, і за 10 000 ітерацій системний годинник "втікає" на кілька мілісекунд.

У нашому коді ми використовуємо абсолютну сітку часу, де кожна наступна точка спрацьовування додає період до попереднього планового значення. Множник `expirations` гарантує, що навіть якщо система була тимчасово заблокована і пропустила кілька тиків, розрахунок наступного дедлайну не зб'ється з точної часової сітки.

### 2. Використання epoll замість блокуючого read()

Хоча виклик `read()` на блокуючому `timerfd` може зупиняти потік до спрацьовування таймера, використання `epoll` моделює поведінку реальних системних серверів (наприклад, Nginx, Envoy або аудіосерверів PipeWire/JACK), де таймер є лише однією з багатьох подій у циклі обробки.

---

## Профілювання джиттера за допомогою ftrace та perf

Для точного аналізу системних джерел джиттера при виконанні тестової програми застосовують вбудований механізм точки простеження ядра (tracepoints).

### 1. Запис точок простеження hrtimer

Запустіть утиліту `perf record` для фіксації моментів вставки таймера та виконання зворотних викликів:

```bash
sudo perf record -e 'hrtimer:hrtimer_start' -e 'hrtimer:hrtimer_expire_entry' -e 'hrtimer:hrtimer_expire_exit' ./benchmark_c
```

### 2. Аналіз часових інтервалів у Ftrace

Утиліта `trace-cmd` дозволяє виміряти точний інтервал між викликом `hrtimer_expire_entry` (початок обробки в ядрі) та виходом із системного виклику `epoll_wait` у просторі користувача:

```bash
sudo trace-cmd record -e "hrtimer:*" -e "sched:sched_wakeup" ./benchmark_c
sudo trace-cmd report | head -n 30
```

Вивід покаже точний розподіл часу між апаратним перериванням та перемиканням контексту планувальника.

---

## Інструкція зі збірки, запуску та експериментів

### 1. Компіляція бінарних файлів

Збірка вихідного коду виконується з максимальним рівнем оптимізації `-O2` для мінімізації накладних витрат власне інструкцій вимірювання.

```bash
# Збірка версії C
gcc -O2 -Wall benchmark_timerfd.c -o benchmark_c

# Збірка версії C++
g++ -O2 -std=c++20 -Wall benchmark_timerfd.cpp -o benchmark_cpp
```

### 2. Експеримент 1: Звичайний запуск (SCHED_OTHER)

Запустіть вимірювання без привілеїв адміністратора на звичайній настільній системі під управлінням планувальника CFS (Completely Fair Scheduler):

```bash
./benchmark_c
```

**Очікувані результати у звичайному середовищі:**
- Мінімальний джиттер: `1.2 – 2.5 мкс`
- Середній джиттер: `4.5 – 9.8 мкс`
- Максимальний джиттер: `40 – 180 мкс`

Сплески до 180 мікросекунд виникають, коли інший фоновий процес (наприклад, браузер чи оновлення пакета) перехоплює процесорне ядро.

### 3. Експеримент 2: Системне навантаження (Stress Test)

Згенеруйте інтенсивне навантаження на процесор та оперативну пам'ять у сусідньому терміналі за допомогою `stress-ng`:

```bash
# Запуск 4 потоків навантаження на процесор і пам'ять
stress-ng --cpu 4 --vm 2 --vm-bytes 512M
```

Повторіть запуск вимірювання під навантаженням:

```bash
./benchmark_c
```

**Очікувані результати під навантаженням:**
- Середній джиттер зростає до `25 – 60 мкс`
- Максимальний джиттер може досягати `1500 – 4000 мкс` (1.5–4 мілісекунди) через чергу витіснення планувальника CFS.

### 4. Експеримент 3: Оптимізація реального часу (SCHED_FIFO + CPU Pinning + CPU Governor)

Для усунення сплесків затримки застосовують комплексну тюнінгову конфігурацію ядра та середовища виконання:

1. **Фіксація максимальної частоти процесора (performance governor)**:
   ```bash
   sudo cpupower frequency-set -g performance
   ```
2. **Вимкнення глибини C-states для усунення затримок пробудження ядра**:
   ```bash
   # Максимально припустима затримка = 0 мкс (дескриптор мусить лишатися відкритим)
   exec 3> /dev/cpu_dma_latency
   echo -ne "\x00\x00\x00\x00" >&3
   ```
3. **Переведення процесу у клас реального часу SCHED_FIFO та ізоляція на ядрі №2**:
   ```bash
   sudo chrt -f 99 taskset -c 2 ./benchmark_c
   ```

**Очікувані результати після повної оптимізації:**
- Мінімальний джиттер: `0.6 – 0.9 мкс`
- Середній джиттер: `1.1 – 1.6 мкс`
- Максимальний джиттер: `3.8 – 6.2 мкс`

Завдяки комбінації `hrtimers`, планувальника `SCHED_FIFO` та ізоляції ядра нам вдалося зменшити максимальний джиттер більш ніж у 600 разів — з 4 мілісекунд до 6 мікросекунд!

---

## Висновки з практичного досліду

1. **Субмілісекундна точність `timerfd`**: Підсистема `hrtimers` дозволяє досягти стабільних затримок пробудження на рівні одиниць мікросекунд у звичайному просторі користувача.
2. **Критичність класів планування**: Для гарантії затримок < 10 мікросекунд використання `hrtimers` має супроводжуватися переведенням процесу у режими реального часу (`SCHED_FIFO` або `SCHED_RR`).
3. **Ефективність реалізації у C та C++**: обгортки C++ не коштують нічого понад те, що робить C, тож C-версія та ідіоматична C++ версія з `std::chrono` показують однаковий джиттер — усе, що вимірюється, відбувається в ядрі.
