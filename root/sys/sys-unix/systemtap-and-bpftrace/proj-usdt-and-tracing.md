# ⚙️ Практичне трасування C/C++ застосунків з USDT та автоматизованим збором метрик

Цей проєкт демонструє практичне створення високоефективного сервісу обробки завдань мовами C та C++ з вбудованими статичними точками інструментації користувацького рівня (USDT) та їх подальше трасування у реальному часі за допомогою інструментів `bpftrace` та `SystemTap`.

## Контекст завдання та принцип роботи USDT

Під час розробки високоінтерактивних сервісів (наприклад, веб-серверів, СУБД або брокерів повідомлень) виникає потреба вимірювати затримки обробки окремих запитів без збільшення накладних витрат у звичайному режимі роботи. Механізм USDT (User-Level Statically Defined Tracing) дозволяє розмістити у коді програми статичні маркери. Коли трасування вимкнене, ці маркери виконуються як трибайтові інструкції `nop3` (`0x90 0x90 0x90`) або п'ятибайтові `nop5`, не викликаючи контекстних перемикань. Коли ж системний адміністратор або SRE-інженер запускає скрипт `bpftrace` чи `SystemTap`, ядро Linux динамічно підміняє інструкцію `nop` на виклик переривання `int 3` або BPF trampoline hook, активуючи збір статистики.

### Анатомія препроцесингу макросів USDT та ELF-секція `.note.stapsdt`

Під час компіляції макроси `STAP_PROBE2(provider, name, arg1, arg2)` із заголовочного файла `<sys/sdt.h>` транслюються у вбудовану асемблерну вставку `__asm__ __volatile__`. Ця вставка виконує дві дії:
1. Вставляє у поточну точку виконання секції `.text` інструкцію `nop`.
2. Додає метадані про маркер у незавантажувану ELF-секцію `.note.stapsdt` за допомогою директив препроцесора `.pushsection .note.stapsdt` та `.popsection`.

Запис у секції `.note.stapsdt` містить:
- Ім'я провайдера (Provider Name) та ім'я проби (Probe Name).
- Віртуальну адресу (Location Address) інструкції `nop` у пам'яті.
- Базову адресу (Base Address) для оновлення системних релокацій при викликах у спільних бібліотеках (`.so`).
- Адресу семафора (Semaphore Address), якщо використано захисний семафор.
- Рядок аргументів (Argument String): текстове форматування розташування кожного аргумента у регістрах процесора чи на стеку (наприклад, `-4@%edi -4@%esi` означає, що перший аргумент є 4-байтовим цілим числом у регістрі `EDI`, а другий — у `ESI`).

## Реалізація обробника завдань з USDT-маркерами

Нижче наведено робочий приклад сервісу обробки завдань у пулі потоків. Програма підключає заголовочний файл `<sys/sdt.h>` (що надається пакунком `systemtap-sdt-devel`) і оголошує пробайдер `workpool` із двома маркерами:
- `task_start`: фіксує початок обробки завдання з аргументами `task_id` та `worker_id`.
- `task_finish`: фіксує завершення обробки з аргументами `task_id`, `worker_id` та статусним кодом помилки `status`.

:::tabs
```c
/* main.c — Реалізація мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <sys/sdt.h>

void process_task(int task_id, int worker_id) {
    /* Маркер початку завдання: передаємо task_id та worker_id */
    STAP_PROBE2(workpool, task_start, task_id, worker_id);

    /* Імітація роботи з випадковою затримкою від 10 до 100 мікросекунд */
    struct timespec ts;
    ts.tv_sec = 0;
    ts.tv_nsec = (10 + rand() % 90) * 1000;
    nanosleep(&ts, NULL);

    int status = (rand() % 100 == 0) ? -1 : 0; /* 1% помилок */

    /* Маркер завершення завдання: передаємо task_id, worker_id та status */
    STAP_PROBE3(workpool, task_finish, task_id, worker_id, status);
}

int main(void) {
    srand((unsigned int)time(NULL));
    printf("Сервіс обробки завдань запущену [PID: %d]. Натисніть Ctrl+C для зупинки...\n", getpid());

    int task_counter = 0;
    while (1) {
        int worker_id = rand() % 4;
        process_task(++task_counter, worker_id);
        usleep(5000); /* Пауза 5 мс між завданнями */
    }

    return 0;
}
```
```cpp
// main.cpp — Ідіоматична реалізація мовою C++
#include <iostream>
#include <random>
#include <thread>
#include <chrono>
#include <memory>
#include <string_view>
#include <sys/sdt.h>

class TaskWorker {
public:
    explicit TaskWorker(int worker_id) : worker_id_(worker_id) {}

    void execute_task(int task_id) {
        // RAII-обгортка для автоматичного виклику USDT-маркерів початку та виходу
        struct ScopedTaskProbe {
            int task_id;
            int worker_id;
            int status{0};

            ScopedTaskProbe(int t_id, int w_id) : task_id(t_id), worker_id(w_id) {
                STAP_PROBE2(workpool, task_start, task_id, worker_id);
            }

            ~ScopedTaskProbe() {
                STAP_PROBE3(workpool, task_finish, task_id, worker_id, status);
            }
        } probe{task_id, worker_id_};

        // Імітація обробки завдання з використанням C++11 random та chrono
        static thread_local std::mt19937 gen{std::random_device{}()};
        std::uniform_int_distribution<int> dist_us(10, 100);
        std::uniform_int_distribution<int> dist_err(1, 100);

        std::this_thread::sleep_for(std::chrono::microseconds(dist_us(gen)));

        if (dist_err(gen) == 1) {
            probe.status = -1; // 1% статус помилки
        }
    }

private:
    int worker_id_;
};

int main() {
    std::cout << "C++ TaskWorker Engine запущену [PID: " << getpid() << "]\n";

    auto worker = std::make_unique<TaskWorker>(1);
    int task_counter = 0;

    while (true) {
        worker->execute_task(++task_counter);
        std::this_thread::sleep_for(std::chrono::milliseconds(5));
    }

    return 0;
}
```
:::

## Збирання та перевірка ELF-секції `.note.stapsdt`

Для збирання програми з підтримкою USDT у системі має бути встановлений пакунок `systemtap-sdt-devel` (або `systemtap-sdt-dev` у Debian/Ubuntu).

Компіляція програми:

:::tabs
```bash
# Компіляція C-версії
gcc -O2 -g main.c -o usdt_app_c
```
```bash
# Компіляція C++17 версії
g++ -O2 -g -std=c++17 main.cpp -o usdt_app_cpp
```
:::

Після компіляції перевіримо наявність USDT-структур у заголовочних секціях ELF-файлу за допомогою утиліти `readelf`:

```bash
readelf -n ./usdt_app_c
```

У виводі утиліти з'явиться секція `NT_STAPSDT` (`.note.stapsdt`), яка містить описи маркерів:

```text
Displaying notes found in: .note.stapsdt
  Owner                Data size        Description
  stapsdt              0x00000038       NT_STAPSDT (SystemTap probe descriptor)
    Provider: workpool
    Name: task_start
    Location: 0x00000000004011e4, Base: 0x0000000000402004, Semaphore: 0x0000000000000000
    Arguments: -4@%edi -4@%esi
  stapsdt              0x0000003c       NT_STAPSDT (SystemTap probe descriptor)
    Provider: workpool
    Name: task_finish
    Location: 0x0000000000401228, Base: 0x0000000000402004, Semaphore: 0x0000000000000000
    Arguments: -4@%edi -4@%esi -4@%edx
```

Також перевірити працездатність проби можна безпосередньо утилітою `bpftrace`:

```bash
bpftrace -l 'usdt:./usdt_app_c:*'
```

Вивід підтверджує наявність двох точок інструментації:
```text
usdt:./usdt_app_c:workpool:task_start
usdt:./usdt_app_c:workpool:task_finish
```

## Скрипт трасування на bpftrace

Напишемо скрипт `trace_workpool.bt`, який розраховує тривалість виконання кожного завдання у мікросекундах (як різницю часу між `task_start` та `task_finish` для одного й того ж `task_id`), будує логарифмічну гістограму затримок та підраховує кількість помилок:

```awk
/* trace_workpool.bt — Скрипт аналізу затримок USDT */

usdt:./usdt_app_c:workpool:task_start {
    $task_id = arg0;
    @start_time[$task_id] = nsecs;
}

usdt:./usdt_app_c:workpool:task_finish {
    $task_id = arg0;
    $worker_id = arg1;
    $status = arg2;

    if (@start_time[$task_id]) {
        $duration_us = (nsecs - @start_time[$task_id]) / 1000;
        delete(@start_time[$task_id]);

        /* Будуємо гістограму затримок у мікросекундах */
        @latency_us = hist($duration_us);

        /* Агрегуємо лічильники за робітниками */
        @requests_per_worker[$worker_id] = count();

        if ($status != 0) {
            @errors_count = count();
        }
    }
}

END {
    printf("\n=== Результати аналізу роботи WorkPool ===\n");
    print(@latency_us);
    print(@requests_per_worker);
    print(@errors_count);
}
```

Запуск трасувальника:

```bash
sudo bpftrace trace_workpool.bt
```

Приклад виводу гістограми затримок після 10 секунд виконання:

```text
@latency_us: 
[8, 16)                0 |                                                    |
[16, 32)              42 |@@@@@@                                              |
[32, 64)             128 |@@@@@@@@@@@@@@@@@@@                                 |
[64, 128)            340 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|

@requests_per_worker:
[0]: 130
[1]: 125
[2]: 128
[3]: 127

@errors_count: 5
```

## Еквівалентний скрипт на SystemTap

Для порівняння створимо еквівалентний скрипт `trace_workpool.stp` мовою SystemTap:

```awk
/* trace_workpool.stp — SystemTap USDT трасування */

global start_time;
global latency_stats;

probe process("./usdt_app_c").mark("task_start") {
    task_id = $arg1;
    start_time[task_id] = gettimeofday_us();
}

probe process("./usdt_app_c").mark("task_finish") {
    task_id = $arg1;
    worker_id = $arg2;
    status = $arg3;

    if (task_id in start_time) {
        duration = gettimeofday_us() - start_time[task_id];
        delete start_time[task_id];

        latency_stats <<< duration;
    }
}

probe end {
    printf("\n=== SystemTap Статистика Затримок (мкс) ===\n");
    printf("Всього оброблено: %d\n", @count(latency_stats));
    printf("Мін / Сер / Макс: %d / %d / %d мкс\n",
           @min(latency_stats), @avg(latency_stats), @max(latency_stats));
    print(@hist_log(latency_stats));
}
```

Запуск SystemTap модуля:

```bash
sudo stap trace_workpool.stp
```

## Крайові випадки та пастки при використанні USDT

Під час експлуатації USDT-проб у складних виробничих системах розробники стикаються з трьома основними пастками:

### 1. Оптимізації компілятора та втрата frame-pointer
При компіляції з високим рівнем оптимізації (`-O2` або `-O3`) компілятор може прибрати вказівник кадру кадру (`-fomit-frame-pointer`) та перерозподілити локальні змінні по регістрах. Макрос USDT записує розташування аргументів у тому вигляді, в якому вони знаходяться у даний момент execution pipeline. 

Якщо аргумент було згорнуто компілятором у вираз типу `-8(%rsp)`, а трасувальник виконує зчитування після того, як стек було зміщено іншою викликовою інструкцією, значення `arg0` може виявитися сміттям. Для уникнення цього рекомендовано збирати інструментовані модулі з прапорцем `-fno-omit-frame-pointer` або використовувати збереження аргументів у явні локальні змінні перед викликом `STAP_PROBE`.

### 2. Вбудовування функцій (Inlining)
Якщо функція, що містить `STAP_PROBE`, вбудовується (inlined) компілятором у декількох місцях виклику, препроцесор згенерує декілька описів у секції `.note.stapsdt` з однаковими іменами провайдера та проби, але з різними віртуальними адресами інструкцій `nop`. 

Утиліти `bpftrace` та `SystemTap` автоматично розпізнають це і ставлять динамічні проби на всі знайдені адреси. Проте це може призвести до подвійного підрахунку подій, якщо одна й та сама проба виконується у декількох гілках розгалуженого коду.

### 3. Оптимізація обчислення аргументів за допомогою Семафорів (USDT Semaphores)
Якщо обчислення аргументів для USDT-проби вимагає значних ресурсів ЦПУ (наприклад, форматування JSON-рядка або прохід по зв'язаному списку), виконувати ці дії при вимкненому трасувальніку недопустимо, оскільки це порушує принцип Zero Overhead.

Для вирішення цієї проблеми USDT підтримує **семафори**. У коді оголошується спеціальний лічильник:

:::tabs
```c
/* Оптимізована підготовка аргументів мовою C */
#include <sys/sdt.h>
#include <stdlib.h>

unsigned short workpool_task_start_semaphore __attribute__ ((unused)) = 0;

void process_complex_task(int task_id) {
    if (STAP_PROBE_INPUT_ENABLED(workpool, task_start)) {
        /* Обчислюємо дорогі аргументи лише якщо проба активована */
        char *payload = generate_expensive_diagnostics();
        STAP_PROBE1(workpool, task_start, payload);
        free(payload);
    }
}
```
```cpp
// Ідіоматична реалізація мовою C++ з RAII та std::string
#include <sys/sdt.h>
#include <string>
#include <memory>

unsigned short workpool_task_start_semaphore __attribute__ ((unused)) = 0;

void process_complex_task(int task_id) {
    if (STAP_PROBE_INPUT_ENABLED(workpool, task_start)) {
        // Замість ручного malloc/free використовуємо std::string та RAII
        std::string payload = generate_expensive_diagnostics_cpp();
        STAP_PROBE1(workpool, task_start, payload.c_str());
    }
}
```
:::

У неактивному стані `workpool_task_start_semaphore` дорівнює `0`, і блок `if` пропускається за один такт. Коли `bpftrace` або `SystemTap` приєднується до проби, ядро автоматично інкрементує значення семафора у пам'яті процесу на `1`, що активує виконання блоку підготовки аргументів. При від'єднанні трасувальника ядро зменшує семафор до `0`.
