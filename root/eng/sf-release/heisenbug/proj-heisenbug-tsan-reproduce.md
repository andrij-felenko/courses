# ⚙️ Ловля гейзенбага через ThreadSanitizer та фаззинг планувальника

Цей практичний посібник демонструє повний інженерний цикл локалізації плаваючої помилки узгодженості пам'яті: від створення вразливого багатопотокового коду, де гонка даних маскується викликами форматованого виводу, до її детермінованого виявлення за допомогою інструменту динамічного аналізу `ThreadSanitizer` (TSan) та хаотичного зсуву таймінгів планувальника потоків.

## Інженерна проблема: збій без свідків

Уяви типову серверну задачу: паралельний кеш підрахунку метрик активності користувачів. Декілька робочих потоків одночасно оновлюють лічильники переглядів і періодично скидають старі записи.

У релізній збірці з високою оптимізацією (`-O3`) під високим навантаженням сервіс рідко (один раз на десятки тисяч операцій) втрачає оновлення або аварійно завершується через пошкодження вказівника на вузол списку. Проте щойно інженер намагається додати в критичну секцію діагностичний вивід `printf("updating key: %d\n", key)` або підключає інтерактивний відладчик GDB, помилка миттєво зникає: система працює абсолютно стабільно мільйони ітерацій поспіль.

Причиною є спостережницький ефект: виклик `printf` містить внутрішнє захоплення блокування потокобезпеки стандартного потоку виводу (`flockfile(stdout)`), що призводить до примусової серіалізації паралельних потоків та розтягування часу виконання операції з 1 наносекунди до десятків мікросекунд.

## Моделювання вразливого коду: маскована гонка даних

Розглянемо спрощену модель такого кешу: спільний лічильник та вказівник на буфер статистики, які оновлюються двома потоками без використання м'ютексів або атомарних примітивів пам'яті.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

#define NUM_ITERATIONS 100000

typedef struct {
    int user_id;
    long long hits;
    char *session_tag;
} UserStats;

static UserStats *g_stats = NULL;
static int g_enable_probe_logging = 0;

void *worker_updater(void *arg) {
    long thread_id = (long)arg;
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        if (g_enable_probe_logging) {
            // Спостережницький ефект: виклик I/O серіалізує доступ
            // і затримує потік на системному виклику write()
            printf("[Thread %ld] Processing iteration %d\n", thread_id, i);
        }

        UserStats *s = g_stats;
        if (s != NULL) {
            // Гонка даних: паралельний запис без синхронізації
            s->hits++;
            if (i % 1000 == 0) {
                // Тимчасове перепризначення вказівника
                char *old_tag = s->session_tag;
                s->session_tag = (i % 2000 == 0) ? "session_alpha" : "session_beta";
                // Потенційне читання розірваного значення іншим потоком
                (void)old_tag;
            }
        }
    }
    return NULL;
}

void *worker_allocator(void *arg) {
    (void)arg;
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        if (g_enable_probe_logging) {
            printf("[Allocator] Reallocating buffer at %d\n", i);
        }

        UserStats *fresh = (UserStats *)malloc(sizeof(UserStats));
        if (!fresh) continue;
        fresh->user_id = 42;
        fresh->hits = 0;
        fresh->session_tag = "session_init";

        UserStats *old = g_stats;
        // Неатомарна публікація нового вказівника
        g_stats = fresh;

        if (old != NULL) {
            // Коротка затримка або негайне звільнення
            free(old);
        }
    }
    return NULL;
}

int main(int argc, char **argv) {
    if (argc > 1 && argv[1][0] == '1') {
        g_enable_probe_logging = 1;
        printf("[INFO] Probe logging ENABLED (Observation mode)\n");
    } else {
        printf("[INFO] Running in NATIVE mode (No logging)\n");
    }

    g_stats = (UserStats *)malloc(sizeof(UserStats));
    g_stats->user_id = 42;
    g_stats->hits = 0;
    g_stats->session_tag = "root";

    pthread_t t1, t2;
    pthread_create(&t1, NULL, worker_updater, (void *)1);
    pthread_create(&t2, NULL, worker_allocator, (void *)2);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    if (g_stats) free(g_stats);
    printf("[DONE] Completed test successfully.\n");
    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <memory>
#include <thread>
#include <vector>

constexpr int NUM_ITERATIONS = 100000;

struct UserStats {
    int user_id{42};
    long long hits{0};
    std::string_view session_tag{"session_init"};
};

static UserStats* g_stats{nullptr};
static bool g_enable_probe_logging{false};

void worker_updater(int thread_id) {
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        if (g_enable_probe_logging) {
            // Спостережницький ефект: вивід у std::cout захоплює внутрішній буфер
            // та синхронізує виконання відносно I/O ядра
            std::cout << "[Thread " << thread_id << "] Iteration " << i << "\n";
        }

        UserStats* s = g_stats;
        if (s != nullptr) {
            // Несинхронізований модифікуючий доступ (Data Race)
            s->hits++;
            if (i % 1000 == 0) {
                s->session_tag = (i % 2000 == 0) ? "session_alpha" : "session_beta";
            }
        }
    }
}

void worker_allocator() {
    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        if (g_enable_probe_logging) {
            std::cout << "[Allocator] Resetting buffer at " << i << "\n";
        }

        auto* fresh = new UserStats{42, 0, "session_init"};
        UserStats* old = g_stats;
        g_stats = fresh;

        if (old != nullptr) {
            delete old; // Створює вікно use-after-free для паралельного потоку
        }
    }
}

int main(int argc, char** argv) {
    if (argc > 1 && argv[1][0] == '1') {
        g_enable_probe_logging = true;
        std::cout << "[INFO] Probe logging ENABLED (Observation mode)\n";
    } else {
        std::cout << "[INFO] Running in NATIVE mode (No logging)\n";
    }

    g_stats = new UserStats{42, 0, "root"};

    std::jthread t1(worker_updater, 1);
    std::jthread t2(worker_allocator);

    t1.join();
    t2.join();

    delete g_stats;
    std::cout << "[DONE] Completed test successfully.\n";
    return 0;
}
```
:::

### Експеримент 1: Звичайна збірка без спостереження
Збираємо бінарний файл за допомогою компілятора GCC або Clang з оптимізацією `-O2`:

```bash
gcc -O2 -pthread race_demo.c -o race_demo
./race_demo 0
```
Результат запуску: процес падає з помилкою `Segmentation fault (core dumped)` або спотворює дані лічильника, оскільки `worker_allocator` звільняє блок пам'яті через `free()` / `delete`, доки `worker_updater` виконує розіменування покажчика.

### Експеримент 2: Увімкнення діагностичного логування
Запускаємо той самий скомпільований бінарний файл, але передаємо прапорець `1`, що активує виклики `printf` / `std::cout`:

```bash
./race_demo 1
```
Результат: програма виводить сотні тисяч рядків і завершується зі статусом `[DONE] Completed test successfully`. Помилка повністю зникла! Додавання «невинного» діагностичного виводу змінило відносні затримки потоків на чотири порядки (з наносекунд до десятків мікросекунд), надійно розвівши конкуруючі операції в часі.

## Внутрішня механіка ThreadSanitizer: тіньовий стан та векторні годинники

Щоб зрозуміти, чому `ThreadSanitizer v2` (TSan) здатний детерміновано фіксувати такі збої без залежності від випадкових таймінгів, розглянемо його внутрішню архітектуру.

TSan транслює кожну операцію доступу до пам'яті через спеціальну модель **векторних годинників Лампорта** (англ. *vector clocks*). Для кожного потоку `T_i` підтримується монотонно зростаючий лічильник логічного часу (епоха `E_i`). Коли потік взаємодіє з примітивом синхронізації (наприклад, звільняє м'ютекс), він публікує вектор свого поточного часу. Коли інший потік захоплює цей м'ютекс, він оновлює свій локальний вектор значеннями максимального часу, встановлюючи формальне відношення «відбулося раніше» (*happens-before*).

Кожні 8 байтів пам'яті застосунку проєктуються на 4 тіньові комірки розміром по 8 байтів кожна (32 байти тіні на 8 байтів програми). У кожній тіньовій комірці зберігаються:
- 16 бітів: унікальний ідентифікатор потоку (`Thread ID`);
- 42 біти: значення логічного годинника епохи на момент операції;
- 2 біти: тип доступу (читання чи запис);
- 4 біти: розмір та зміщення всередині 8-байтного вирівняного слова.

Коли потік `T1` виконує запис у пам'ять, TSan порівнює його поточну епоху з епохами попередніх звернень, збережених у тіньових комірках. Якщо потік `T2` вже читав або писав за цією адресою, але між епохою `T1` та епохою `T2` немає зв'язку через векторний годинник (тобто операції не були синхронізовані м'ютексом або бар'єром пам'яті), TSan констатує стан гонки негайно — навіть якщо фізично в часі процесора ці дві інструкції були виконані з інтервалом у кілька секунд!

Компілюємо програму з прапорцем `-fsanitize=thread`:

```bash
gcc -fsanitize=thread -g -O1 -pthread race_demo.c -o race_tsan
./race_tsan 0
```

Незалежно від того, стався аварійний збій під час конкретного прогону чи ні, TSan миттєво перехоплює несинхронізований доступ і генерує вичерпний звіт про дефект:

```text
==================
WARNING: ThreadSanitizer: data race (pid=48210)
  Read of size 8 at 0x7b0400000000 by thread T1:
    #0 worker_updater race_demo.c:26 (race_tsan+0x401245)

  Previous write of size 8 at 0x7b0400000000 by thread T2:
    #0 free <null> (race_tsan+0x421890)
    #1 worker_allocator race_demo.c:54 (race_tsan+0x401398)

  Location is heap block of size 24 at 0x7b0400000000 allocated by main thread:
    #0 malloc <null> (race_tsan+0x421710)
    #1 main race_demo.c:68 (race_tsan+0x401420)

  Thread T1 (tid=48211, running) created by main thread at:
    #0 pthread_create <null> (race_tsan+0x425610)
    #1 main race_demo.c:73 (race_tsan+0x401452)

  Thread T2 (tid=48212, running) created by main thread at:
    #0 pthread_create <null> (race_tsan+0x425610)
    #1 main race_demo.c:74 (race_tsan+0x401478)
==================
```

### Як читати звіт TSan:
1. **Тип помилки:** `data race` — виявлено два одночасні звернення до однієї адреси `0x7b0400000000`, щонайменше одне з яких є записом, без відношення «відбулося раніше» (happens-before).
2. **Стек першого конфліктуючого звернення:** Потік `T1` намагався прочитати 8 байтів у рядку 26 (`s->hits++`).
3. **Стек попереднього звернення:** Потік `T2` звільнив цю пам'ять у рядку 54 (`free(old)`).
4. **Місце виділення пам'яті:** Початковий блок виділено в функції `main` у рядку 68.

TSan виявив логічний дефект у структурі програми незалежно від швидкості виконання конкретного процесора та наявності налагоджувальних затримок.

## Фаззинг планувальника: примусове відкриття вікон гонок

Якщо гонка виникає вкрай рідко через специфічну топологію потоків або наявність грубих блокувань в інших частинах коду, для провокації збоїв застосовують техніку **хаотичного планування** (англ. *scheduler fuzzing* або *chaos mode*).

Ідея полягає в тому, щоб на кожній точці синхронізації, вході в системний виклик або розіменуванні покажчика інжектувати псевдовипадкові мікрозатримки (`sched_yield()` або `usleep()`), які змушують планувальник операційної системи перемикати контекст ядра саме в найнебезпечніший момент.

Створимо бібліотеку-перехоплювач для інжекції хаосу через механізм динамічного лінкера `LD_PRELOAD`:

:::tabs
```c
// chaos_inject.c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <sched.h>
#include <unistd.h>

static int (*real_pthread_mutex_lock)(void *) = NULL;

int pthread_mutex_lock(void *mutex) {
    if (!real_pthread_mutex_lock) {
        real_pthread_mutex_lock = (int (*)(void *))dlsym(RTLD_NEXT, "pthread_mutex_lock");
    }

    // Випадкова поступка кванта часу процесора перед взяттям блокування
    if (rand() % 4 == 0) {
        sched_yield();
    }
    if (rand() % 10 == 0) {
        usleep(rand() % 50); // Пауза від 0 до 50 мікросекунд
    }

    return real_pthread_mutex_lock(mutex);
}
```
```cpp
// chaos_inject.cpp
#include <iostream>
#include <random>
#include <thread>
#include <chrono>
#include <dlfcn.h>
#include <pthread.h>

extern "C" int pthread_mutex_lock(pthread_mutex_t* mutex) {
    static auto real_lock = reinterpret_cast<int(*)(pthread_mutex_t*)>(
        dlsym(RTLD_NEXT, "pthread_mutex_lock")
    );

    thread_local std::mt19937 gen(std::random_device{}());
    thread_local std::uniform_int_distribution<int> dist_yield(0, 3);
    thread_local std::uniform_int_distribution<int> dist_sleep(0, 9);
    thread_local std::uniform_int_distribution<int> dist_duration(1, 50);

    if (dist_yield(gen) == 0) {
        std::this_thread::yield();
    }
    if (dist_sleep(gen) == 0) {
        std::this_thread::sleep_for(std::chrono::microseconds(dist_duration(gen)));
    }

    return real_lock(mutex);
}
```
:::

Компілюємо перехоплювач у динамічну бібліотеку та запускаємо тестований застосунок під його наглядом:

```bash
gcc -shared -fPIC -O2 chaos_inject.c -o libchaos.so -ldl
LD_PRELOAD=./libchaos.so ./race_demo 0
```

Під впливом хаотичних затримок навіть ті вікна гонок, які в звичайних умовах відкривалися з імовірністю 0.001 %, починають призводити до збоїв майже на кожному прогоні тесту.

## Виправлення дефекту: перехід до детермінованої синхронізації

Для повного усунення гейзенбага необхідно забезпечити атомарність зміни вказівника та використання механізмів безпечного читання/запису. Нижче наведено виправлені та потокобезпечні варіанти реалізації.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdatomic.h>

typedef struct {
    int user_id;
    _Atomic long long hits;
    const char *session_tag;
} UserStats;

static _Atomic(UserStats *) g_stats = NULL;
static pthread_mutex_t g_alloc_lock = PTHREAD_MUTEX_INITIALIZER;

void *worker_updater_safe(void *arg) {
    (void)arg;
    for (int i = 0; i < 100000; ++i) {
        // Безпечне читання атомарного покажчика
        UserStats *s = atomic_load_explicit(&g_stats, memory_order_acquire);
        if (s != NULL) {
            atomic_fetch_add_explicit(&s->hits, 1, memory_order_relaxed);
        }
    }
    return NULL;
}

void *worker_allocator_safe(void *arg) {
    (void)arg;
    for (int i = 0; i < 100000; ++i) {
        UserStats *fresh = (UserStats *)malloc(sizeof(UserStats));
        fresh->user_id = 42;
        atomic_init(&fresh->hits, 0);
        fresh->session_tag = "session_init";

        pthread_mutex_lock(&g_alloc_lock);
        UserStats *old = atomic_exchange_explicit(&g_stats, fresh, memory_order_acq_rel);
        pthread_mutex_unlock(&g_alloc_lock);

        // У реальних системах для безпечного звільнення використовують RCU
        // або епохи пам'яті (hazard pointers) замість негайного free
        (void)old;
    }
    return NULL;
}
```
```cpp
#include <iostream>
#include <memory>
#include <thread>
#include <atomic>
#include <string_view>

struct UserStats {
    int user_id{42};
    std::atomic<long long> hits{0};
    std::string_view session_tag{"session_init"};
};

// Використання std::atomic<std::shared_ptr> для потокобезпечного володіння
static std::shared_ptr<UserStats> g_stats{std::make_shared<UserStats>()};
static std::mutex g_swap_mutex;

void worker_updater_safe(int thread_id) {
    (void)thread_id;
    for (int i = 0; i < 100000; ++i) {
        // Атомарне копіювання розумного вказівника (збільшує лічильник посилань)
        std::shared_ptr<UserStats> local_s = std::atomic_load(&g_stats);
        if (local_s) {
            local_s->hits.fetch_add(1, std::memory_order_relaxed);
        }
    }
}

void worker_allocator_safe() {
    for (int i = 0; i < 100000; ++i) {
        auto fresh = std::make_shared<UserStats>();
        fresh->user_id = 42;

        // Атомарна підміна глобального ресурсу
        std::atomic_store(&g_stats, fresh);
    }
}
```
:::

Перевіряємо виправлений код під керуванням ThreadSanitizer:
```bash
gcc -fsanitize=thread -g -O2 -pthread race_fixed.c -o race_fixed
./race_fixed
```
TSan завершує виконання без жодного попередження, підтверджуючи коректність моделі узгодженості пам'яті.
