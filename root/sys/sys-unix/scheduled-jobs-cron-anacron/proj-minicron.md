# ⚙️ Реалізація власного планувальника: синхронізація хвилини, бітові маски та керування процесами

Розуміння внутрішньої будови демона `cron` найкраще досягається через побудову його спрощеного, але повністю функціонального аналога. Будь-який планувальник завдань на базі Unix повинен розв'язувати чотири головні інженерні проблеми:
1. **Точна синхронізація часу:** засинання рівно до нульової секунди наступної астрономічної хвилини без накопичення фазового зсуву.
2. **Швидке зіставлення умов розкладу:** перевірка збігу поточного часу із синтаксичними виразами через бітові маски.
3. **Реалізація специфікації POSIX щодо днів:** коректна диз'юнкція (логічне `АБО`) між днем місяця та днем тижня, коли обидва поля явно обмежені.
4. **Безпечне керування процесами:** запуск завдань у дочірніх процесах через [fork](root:sys-unix/fork-semantics) та [exec](root:sys-unix/exec-semantics), ізоляція дескрипторів та своєчасний збір кодів повернення через [waitpid](root:sys-unix/exit-wait-zombies) у неблокуючому обробнику сигналу `SIGCHLD`.

Нижче наведено робочу реалізацію планувальника `minicron`, що демонструє всі ці механізми на мовах C та C++.

:::tabs
@tab C
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <errno.h>

#define MAX_JOBS 32
#define MAX_CMD_LEN 256

/* Бітова маска для кожного поля розкладу.
 * 64 біти вистачає для покриття діапазону хвилин (0..59) та решти полів. */
typedef struct {
    unsigned long long minute_mask;   /* 0-59 */
    unsigned int hour_mask;           /* 0-23 */
    unsigned int dom_mask;            /* 1-31 (біти 1..31) */
    unsigned int month_mask;          /* 1-12 (біти 1..12) */
    unsigned int dow_mask;            /* 0-7 (0 і 7 - неділя) */
    int dom_is_wildcard;              /* чи було поле дня місяця задано як '*' */
    int dow_is_wildcard;              /* чи було поле дня тижня задано як '*' */
    char command[MAX_CMD_LEN];
} cron_job_t;

static cron_job_t g_jobs[MAX_JOBS];
static size_t g_num_jobs = 0;

/* Обробник сигналу SIGCHLD для асинхронного очищення зомбі-процесів */
static void sigchld_handler(int sig) {
    (void)sig;
    int saved_errno = errno;
    while (waitpid(-1, NULL, WNOHANG) > 0) {
        /* Очищаємо всіх нащадків, що завершили роботу */
    }
    errno = saved_errno;
}

/* Парсинг одного поля crontab у бітову маску (підтримка '*', чисел, діапазонів 'a-b' та кроків */
static int parse_field(const char *str, int min_val, int max_val,
                       unsigned long long *mask_out, int *is_wildcard) {
    *mask_out = 0;
    *is_wildcard = 0;

    if (strcmp(str, "*") == 0) {
        *is_wildcard = 1;
        for (int i = min_val; i <= max_val; ++i) {
            *mask_out |= (1ULL << i);
        }
        return 0;
    }

    if (strncmp(str, "*/", 2) == 0) {
        int step = atoi(str + 2);
        if (step <= 0) return -1;
        for (int i = min_val; i <= max_val; i += step) {
            *mask_out |= (1ULL << i);
        }
        return 0;
    }

    char *dash = strchr(str, '-');
    if (dash) {
        int start = atoi(str);
        int end = atoi(dash + 1);
        if (start < min_val || end > max_val || start > end) return -1;
        for (int i = start; i <= end; ++i) {
            *mask_out |= (1ULL << i);
        }
        return 0;
    }

    /* Простий список через кому або одне число */
    char buf[64];
    strncpy(buf, str, sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = '\0';
    char *token = strtok(buf, ",");
    while (token) {
        int val = atoi(token);
        if (val < min_val || val > max_val) return -1;
        *mask_out |= (1ULL << val);
        token = strtok(NULL, ",");
    }
    return 0;
}

/* Додавання завдання до таблиці */
static int add_job(const char *min_s, const char *hour_s, const char *dom_s,
                   const char *mon_s, const char *dow_s, const char *cmd) {
    if (g_num_jobs >= MAX_JOBS) return -1;
    cron_job_t *j = &g_jobs[g_num_jobs];

    unsigned long long m_mask, h_mask, dom_m, mon_m, dow_m;
    int dom_w, dow_w, dummy;

    if (parse_field(min_s, 0, 59, &m_mask, &dummy) != 0) return -1;
    if (parse_field(hour_s, 0, 23, &h_mask, &dummy) != 0) return -1;
    if (parse_field(dom_s, 1, 31, &dom_m, &dom_w) != 0) return -1;
    if (parse_field(mon_s, 1, 12, &mon_m, &dummy) != 0) return -1;
    if (parse_field(dow_s, 0, 7, &dow_m, &dow_w) != 0) return -1;

    /* Уніфікація неділі: 0 і 7 відповідають неділі */
    if (dow_m & (1ULL << 7)) {
        dow_m |= (1ULL << 0);
    }
    if (dow_m & (1ULL << 0)) {
        dow_m |= (1ULL << 7);
    }

    j->minute_mask = m_mask;
    j->hour_mask = (unsigned int)h_mask;
    j->dom_mask = (unsigned int)dom_m;
    j->month_mask = (unsigned int)mon_m;
    j->dow_mask = (unsigned int)dow_m;
    j->dom_is_wildcard = dom_w;
    j->dow_is_wildcard = dow_w;
    strncpy(j->command, cmd, sizeof(j->command) - 1);
    j->command[sizeof(j->command) - 1] = '\0';

    g_num_jobs++;
    return 0;
}

/* Перевірка збігу завдання з поточним астрономічним часом */
static int job_matches(const cron_job_t *j, const struct tm *t) {
    /* 1. Хвилини, години, місяці перевіряються через кон'юнкцію */
    if (!(j->minute_mask & (1ULL << t->tm_min))) return 0;
    if (!(j->hour_mask & (1ULL << t->tm_hour))) return 0;
    if (!(j->month_mask & (1ULL << (t->tm_mon + 1)))) return 0;

    int dom_match = (j->dom_mask & (1ULL << t->tm_mday)) ? 1 : 0;
    int dow_match = (j->dow_mask & (1ULL << t->tm_wday)) ? 1 : 0;

    /* 2. Особливе правило POSIX: якщо обидва поля обмежені, використовується OR */
    if (!j->dom_is_wildcard && !j->dow_is_wildcard) {
        return dom_match || dow_match;
    }
    /* Якщо хоча б одне поле є '*', використовується звичайна кон'юнкція */
    return dom_match && dow_match;
}

/* Запуск завдання у дочірньому процесі */
static void spawn_job(const char *cmd) {
    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return;
    }
    if (pid == 0) {
        /* Дочірній процес: ізоляція стандартних дескрипторів */
        int devnull = open("/dev/null", O_RDWR);
        if (devnull >= 0) {
            dup2(devnull, STDIN_FILENO);
            close(devnull);
        }
        /* Виконання команди через стандартний командний інтерпретатор */
        execl("/bin/sh", "sh", "-c", cmd, (char *)NULL);
        _exit(127);
    }
}

int main(void) {
    /* Встановлюємо обробник SIGCHLD */
    struct sigaction sa;
    sa.sa_handler = sigchld_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART | SA_NOCLDSTOP;
    sigaction(SIGCHLD, &sa, NULL);

    /* Додаємо тестові розклади:
     * 1. Кожну хвилину: друк поточної мітки часу
     * 2. Кожні 5 хвилин: системний звіт
     * 3. Щоп'ятниці та 13-го числа: перевірка правила DOM || DOW */
    add_job("*", "*", "*", "*", "*", "echo minicron tick $(date) >> /tmp/minicron.log");
    add_job("*/5", "*", "*", "*", "*", "uptime >> /tmp/minicron-uptime.log");
    add_job("0", "12", "13", "*", "5", "echo Friday the 13th alert >> /tmp/minicron.log");

    printf("minicron запущено. Зареєстровано завдань: %zu\n", g_num_jobs);

    while (1) {
        time_t now = time(NULL);
        struct tm tm_now;
        localtime_r(&now, &tm_now);

        /* Засинаємо до початку наступної хвилини */
        int seconds_to_next_minute = 60 - tm_now.tm_sec;
        if (seconds_to_next_minute > 0) {
            sleep((unsigned int)seconds_to_next_minute);
        }

        /* Оновлюємо час після пробудження */
        now = time(NULL);
        localtime_r(&now, &tm_now);

        /* Перевіряємо всі зареєстровані завдання */
        for (size_t i = 0; i < g_num_jobs; ++i) {
            if (job_matches(&g_jobs[i], &tm_now)) {
                spawn_job(g_jobs[i].command);
            }
        }
    }

    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <bitset>
#include <chrono>
#include <thread>
#include <sstream>
#include <stdexcept>
#include <csignal>
#include <ctime>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <fcntl.h>

namespace minicron {

struct CronJob {
    std::bitset<60> minute_mask;   // 0..59
    std::bitset<24> hour_mask;     // 0..23
    std::bitset<32> dom_mask;      // 1..31
    std::bitset<13> month_mask;    // 1..12
    std::bitset<8>  dow_mask;      // 0..7 (0 і 7 - неділя)
    bool dom_is_wildcard{false};
    bool dow_is_wildcard{false};
    std::string command;
};

class Scheduler {
public:
    Scheduler() {
        setup_signal_handler();
    }

    void add_job(std::string_view min_s, std::string_view hour_s,
                 std::string_view dom_s, std::string_view mon_s,
                 std::string_view dow_s, std::string_view cmd) {
        CronJob job;
        bool dummy = false;

        job.minute_mask = parse_field<60>(min_s, 0, 59, dummy);
        job.hour_mask   = parse_field<24>(hour_s, 0, 23, dummy);
        job.dom_mask    = parse_field<32>(dom_s, 1, 31, job.dom_is_wildcard);
        job.month_mask  = parse_field<13>(mon_s, 1, 12, dummy);
        job.dow_mask    = parse_field<8>(dow_s, 0, 7, job.dow_is_wildcard);

        // Уніфікація неділі: 0 і 7 є еквівалентними
        if (job.dow_mask.test(7)) job.dow_mask.set(0);
        if (job.dow_mask.test(0)) job.dow_mask.set(7);

        job.command = cmd;
        jobs_.push_back(std::move(job));
    }

    void run() {
        std::cout << "minicron (C++) запущено. Завдань: " << jobs_.size() << "\n";

        while (true) {
            auto now = std::chrono::system_clock::now();
            std::time_t time_now = std::chrono::system_clock::to_time_t(now);
            std::tm tm_now{};
            localtime_r(&time_now, &tm_now);

            // Синхронізація з наступною астрономічною хвилиною
            int sleep_sec = 60 - tm_now.tm_sec;
            if (sleep_sec > 0) {
                std::this_thread::sleep_for(std::chrono::seconds(sleep_sec));
            }

            // Перечитуємо поточний час після пробудження
            now = std::chrono::system_clock::now();
            time_now = std::chrono::system_clock::to_time_t(now);
            localtime_r(&time_now, &tm_now);

            for (const auto& job : jobs_) {
                if (matches(job, tm_now)) {
                    spawn_process(job.command);
                }
            }
        }
    }

private:
    std::vector<CronJob> jobs_;

    static void setup_signal_handler() {
        struct sigaction sa{};
        sa.sa_handler = [](int) {
            while (waitpid(-1, nullptr, WNOHANG) > 0) {
                // Збір зомбі-процесів
            }
        };
        sigemptyset(&sa.sa_mask);
        sa.sa_flags = SA_RESTART | SA_NOCLDSTOP;
        sigaction(SIGCHLD, &sa, nullptr);
    }

    template <size_t N>
    static std::bitset<N> parse_field(std::string_view str, int min_val, int max_val, bool& is_wildcard) {
        std::bitset<N> mask;
        is_wildcard = false;

        if (str == "*") {
            is_wildcard = true;
            for (int i = min_val; i <= max_val; ++i) mask.set(i);
            return mask;
        }

        if (str.starts_with("*/")) {
            int step = std::stoi(std::string(str.substr(2)));
            if (step <= 0) throw std::invalid_argument("Некоректний крок розкладу");
            for (int i = min_val; i <= max_val; i += step) mask.set(i);
            return mask;
        }

        auto dash_pos = str.find('-');
        if (dash_pos != std::string_view::npos) {
            int start = std::stoi(std::string(str.substr(0, dash_pos)));
            int end = std::stoi(std::string(str.substr(dash_pos + 1)));
            if (start < min_val || end > max_val || start > end) {
                throw std::out_of_range("Діапазон розкладу поза межами");
            }
            for (int i = start; i <= end; ++i) mask.set(i);
            return mask;
        }

        // Розбір списку значень через кому
        std::stringstream ss{std::string(str)};
        std::string token;
        while (std::getline(ss, token, ',')) {
            int val = std::stoi(token);
            if (val < min_val || val > max_val) {
                throw std::out_of_range("Значення поля виходить за межі");
            }
            mask.set(val);
        }
        return mask;
    }

    static bool matches(const CronJob& job, const std::tm& t) {
        if (!job.minute_mask.test(t.tm_min)) return false;
        if (!job.hour_mask.test(t.tm_hour)) return false;
        if (!job.month_mask.test(t.tm_mon + 1)) return false;

        bool dom_match = job.dom_mask.test(t.tm_mday);
        bool dow_match = job.dow_mask.test(t.tm_wday);

        // Диз'юнкція POSIX: якщо обидва поля явно задані — спрацьовує будь-яке
        if (!job.dom_is_wildcard && !job.dow_is_wildcard) {
            return dom_match || dow_match;
        }
        return dom_match && dow_match;
    }

    static void spawn_process(const std::string& cmd) {
        pid_t pid = fork();
        if (pid < 0) {
            std::cerr << "Помилка fork()\n";
            return;
        }
        if (pid == 0) {
            int devnull = open("/dev/null", O_RDWR);
            if (devnull >= 0) {
                dup2(devnull, STDIN_FILENO);
                close(devnull);
            }
            execl("/bin/sh", "sh", "-c", cmd.c_str(), nullptr);
            _exit(127);
        }
    }
};

} // namespace minicron

int main() {
    try {
        minicron::Scheduler scheduler;
        scheduler.add_job("*", "*", "*", "*", "*", "echo tick $(date) >> /tmp/minicron_cpp.log");
        scheduler.add_job("*/10", "*", "*", "*", "*", "df -h >> /tmp/minicron_df.log");
        scheduler.run();
    } catch (const std::exception& e) {
        std::cerr << "Критична помилка: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

## Інженерний розбір критичних механізмів планувальника

Розробка надійного фонового демона вимагає уваги до деталей, які часто опускають у простих консольних утилітах. Розглянемо ключові інженерні рішення, реалізовані у проекті `minicron`:

### 1. Синхронізація часу та захист від дрейфу фази
Наївна реалізація планувальника використовує простий фіксований сон `sleep(60)` після виконання чергової ітерації. Такий підхід є фатально хибним у виробничих системах. Виклики `fork()`, підготовка дескрипторів та ітерація по списку завдань забирають кілька мілісекунд процесорного часу.

Якщо демон спить рівно 60 секунд після кожного кола, час початку наступної ітерації поступово зсувається: `00.000` → `00.005` → `00.012` → ... Через кілька годин момент пробудження перетинає межу хвилини, і демон повністю пропускає одну астрономічну хвилину.

Щоб усунути цей ефект, `minicron` перед кожним засинанням зчитує системний календарний час `tm_sec` і засинає рівно на `60 - tm_sec` секунд. Навіть якщо обробка завдань тривала 4 секунди, планувальник засне на 56 секунд і прокинеться точно на початку наступної хвилини (секунда 00).

### 2. Оптимізація перевірки розкладу через бітові маски
Текстовий розбір рядків на кшталт `*/5` або `1,15,30` під час кожного хвилинного пробудження створював би надмірне навантаження на процесор і породжував алокації пам'яті. У `minicron` синтаксичний аналіз виконується лише один раз під час реєстрації завдання.

Оскільки всі часові поля є дискретними та обмеженими (хвилини: 0..59, години: 0..23, дні: 1..31, місяці: 1..12, дні тижня: 0..7), кожне поле транслюється у 64-бітне беззнакове ціле число або `std::bitset`.
- Встановлений біт `k` означає, що значення `k` дозволене розкладом.
- Перевірка, чи поточна хвилина підходить для запуску:
:::tabs
@tab C
```c
(minute_mask & (1ULL << current_minute)) != 0
```
@tab C++
```cpp
minute_mask.test(current_minute)
```
:::
Така перевірка займає 1 такт процесора, що дозволяє миттєво оцінювати тисячі завдань.

### 3. Логіка диз'юнкції для Day of Month та Day of Week
Стандарт POSIX вимагає спеціальної обробки полів дня місяця та дня тижня. Якщо користувач задає розклад `0 12 13 * 5`, інтуїтивне очікування новачка — запуск «лише у п'ятницю 13-го». Проте класичний алгоритм Unix працює інакше:
- Якщо обидва поля обмежені (жодне з них не є символом `*`), вони об'єднуються логічним оператором `АБО`.
- Завдання виконається як щоп'ятниці (незалежно від числа місяця), так і 13-го числа (незалежно від дня тижня).
- Якщо хоча б одне з полів містить `*`, діє стандартна кон'юнкція (`І`).

У коді `minicron` зберігаються прапорці `dom_is_wildcard` та `dow_is_wildcard`, які безпосередньо керують логікою у функції `matches()`.

### 4. Асинхронний збір процесів-нащадків та безпека сигналів
Під час запуску кожного завдання функція `fork()` створює новий процес. Якщо батьківський процес не очікує завершення нащадків через `wait()`, після завершення їхньої роботи дескриптори процесів залишаються в таблиці ядра як зомбі (`<defunct>`). При інтенсивному розкладі це швидко вичерпує ліміт PID операційної системи.

Виклик блокуючого `wait()` у головному циклі неприпустимий, оскільки довге завдання заблокує секундний таймер. Тому збір реалізовано через асинхронний обробник сигналу `SIGCHLD`:
- Обробник виконує неблокуючий виклик `waitpid(-1, NULL, WNOHANG)` у циклі `while`.
- Використання циклу є критичним: кілька сигналів `SIGCHLD` можуть злитися в один, якщо кілька завдань завершилися одночасно. Цикл гарантує вичистку всіх готових процесів за один виклик обробника.
- Збереження та відновлення змінної `errno` захищає основний потік програми від випадкового перезапису коду системної помилки під час переривання сигналом.

### 5. Ізоляція стандартного вводу
У дочірньому процесі перед викликом `execl()` файловий дескриптор `STDIN_FILENO` (0) перенаправляється на `/dev/null`. Це унеможливлює зависання фонового завдання, якщо запущений скрипт випадково спробує зчитати дані з термінала або запросити інтерактивне підтвердження в користувача.

### 6. Порівняння підходів C та C++
Реалізації на C та C++ демонструють дві різні системні парадигми:
- **Підхід C:** спирається на фіксовані статичні буфери (`char buf[64]`), глобальний масив завдань, побітові операції над цілими типами `unsigned long long` та виклики бібліотечних функцій `strtok`. Такий код не здійснює динамічного виділення пам'яті на купі (`heap`), має передбачуваний розмір бінарного файлу та ідеально підходить для мікроконтролерів і систем із суворими обмеженнями оперативної пам'яті.
- **Підхід C++:** використовує сучасні безпечні абстракції нульової вартості (`zero-cost abstractions`). Замість ручного копіювання рядків застосовується `std::string_view`, що усуває зайві алокації під час синтаксичного аналізу. Шаблонний клас `std::bitset<N>` надає строго типізований інтерфейс перевірки бітів без ризику переповнення цілого числа, а стандартні винятки `std::invalid_argument` та `std::out_of_range` забезпечують надійну валідацію користувацького вводу на стадії ініціалізації планувальника.

### 7. Системні крайові випадки у промислових планувальниках
У реальних дистрибутивах демони рівня `cronie` або `Vixie cron` враховують додаткові системні сценарії:
- **Переведення годинників (DST):** навесні під час зсуву часу на 1 годину вперед планувальник повинен виявити пропущений інтервал і запустити завдання, які потрапили у випалу годину. Восени під час переведення назад завдання не повинні виконуватися двічі.
- **Зміна системного часу:** якщо адміністратор або демон [NTP](root:sys-unix/wall-clock-and-timezones) змінює час стрибком через `settimeofday()`, сучасні демони отримують сповіщення через механізм таймерних дескрипторів ядра (`timerfd_create` з прапорцем `TFD_TIMER_CANCEL_ON_SET`), миттєво перебудовуючи чергу розкладів.
