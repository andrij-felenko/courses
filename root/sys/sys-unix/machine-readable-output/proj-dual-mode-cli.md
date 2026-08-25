# ⚙️ Реалізація дуального CLI-інструмента з підтримкою TTY, JSON та TSV

Утиліти системного адміністрування та моніторингу в операційних системах Unix та Linux повинні однаково ефективно функціонувати у двох принципово різних середовищах: в інтерактивному сеансі під прямим керуванням оператора та у складі автоматизованих конвеєрів (`pipelines`), де потік виводу споживається іншими системними програмами (`jq`, `awk`, `xargs`, `systemd`) або передається мережевим демонам збору метрик.

У цьому практичному проєкті розглядається повноцінна інженерна реалізація системної утиліти `sysproc-stat`, яка зчитує показники споживання оперативної пам'яті процесами та реалізує повноцінну дуальну модель інтерфейсу CLI.

---

## 1. Архітектурні вимоги та виклики проєктування

Створення стабільного консольного інструмента вимагає розв'язання чотирьох фундаментальних інженерних задач:

1. **Динамічна адаптація форматування під середовище**:
   - Якщо стандартний потік виводу `STDOUT` підключений до термінала (`isatty(STDOUT_FILENO) == 1`), утиліта формує візуально привабливу таблицю з шапкою стовпців, фіксованими відступами, ANSI-кольорами статусів та людиночитними скороченнями пам'яті (KiB, MiB, GiB).
   - Якщо `STDOUT` перенаправлено у канал (`pipe`) або файл, утиліта автоматично перемикається у плоский машинний формат TSV (значення через табуляцію) без заголовків та без керуючих байтів кольору, які могли б спотворити дані для парсерів.

2. **Підтримка структурованого та потокового машинних форматів**:
   - Прапорець `--json` генерує валідний документ JSON із точними цілими числами в байтах (`uint64_t`) та часовою міткою епохи Unix.
   - Прапорець `--raw` або `--tsv` генерує плоскі таблиці для обробки за допомогою `cut` та `awk`.
   - Прапорець `-z` (`--null`) перемикає розділювач записів на нульовий байт (`\0`), що забезпечує абсолютну стійкість при передачі утиліті `xargs -0`.

3. **Коректне керування буферизацією введення-виведення**:
   - Для інтерактивного термінала libc за замовчуванням вмикає рядкову буферизацію (`_IOLBF`), скидаючи буфер після кожного `\n`.
   - Для конвеєрів та файлів утиліта налаштовує повну блокову буферизацію (`_IOFBF`) розміром 8192 байти за допомогою `setvbuf()`, що знижує кількість системних викликів `write()` та підвищує пропускну здатність утиліти під високим навантаженням.

4. **Обробка розриву конвеєра (`SIGPIPE`)**:
   - При виклику виду `sysproc-stat | head -n 1` процес `head` зчитує один рядок і негайно закриває свій кінець каналу. Наступний виклик `write()` у закритий дескриптор генерує сигнал `SIGPIPE`. За замовчуванням ядро Linux завершує процес із кодом `141` (`128 + 13`), що є коректною поведінкою, проте утиліта повинна уникати аварійного скидання помилок у `STDERR`.

```
                      ┌────────────────────────────────┐
                      │    sysproc-stat CLI Engine     │
                      └───────────────┬────────────────┘
                                      │
              ┌───────────────────────┴───────────────────────┐
              ▼                                               ▼
   [isatty(STDOUT_FILENO) == 1]                    [isatty(STDOUT_FILENO) == 0]
      або явний прапорець                             або прапорці --json / --raw
              │                                               │
              ▼                                               ▼
   ┌───────────────────────┐                       ┌───────────────────────┐
   │      Human Mode       │                       │     Machine Mode      │
   ├───────────────────────┤                       ├───────────────────────┤
   │ • ANSI Escape кольори │                       │ • Строгий JSON / TSV  │
   │ • Суфікси MiB / GiB   │                       │ • Точні байти (int64) │
   │ • Шапка стовпців      │                       │ • Без кольорів        │
   │ • Рядкова буферизація │                       │ • Блокова буферизація │
   └───────────────────────┘                       └───────────────────────┘
```

---

## 2. Реалізація утиліти мовами C та C++

Нижче наведено повний робочий код утиліти двома мовами з однаковим рівнем функціональності та дотриманням відповідних ідіом.

:::tabs
```c
/* sysproc_stat.c — Реалізація дуального CLI мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <inttypes.h>
#include <unistd.h>
#include <signal.h>
#include <time.h>
#include <sys/ioctl.h>

#define ANSI_RESET   "\033[0m"
#define ANSI_BOLD    "\033[1m"
#define ANSI_GREEN   "\033[32m"
#define ANSI_YELLOW  "\033[33m"
#define ANSI_CYAN    "\033[36m"
#define ANSI_RED     "\033[31m"

typedef enum {
    OUT_AUTO,
    OUT_HUMAN,
    OUT_JSON,
    OUT_TSV
} OutputMode;

typedef struct {
    pid_t pid;
    char name[64];
    char state;
    uint64_t rss_bytes;
    uint64_t vsz_bytes;
} ProcessMetric;

typedef struct {
    OutputMode mode;
    bool enable_color;
    bool null_delimited;
    bool no_heading;
} Config;

/* Перевірка стандартів NO_COLOR, CLICOLOR та стану TTY */
static bool detect_color_support(int fd) {
    const char *no_color = getenv("NO_COLOR");
    if (no_color && no_color[0] != '\0') {
        return false;
    }
    const char *clicolor_force = getenv("CLICOLOR_FORCE");
    if (clicolor_force && strcmp(clicolor_force, "0") != 0) {
        return true;
    }
    const char *term = getenv("TERM");
    if (term && strcmp(term, "dumb") == 0) {
        return false;
    }
    const char *clicolor = getenv("CLICOLOR");
    if (clicolor && strcmp(clicolor, "0") == 0) {
        return false;
    }
    return isatty(fd) == 1;
}

/* Форматування байтів у двійкові одиниці IEC (KiB, MiB, GiB) */
static void format_human_bytes(uint64_t bytes, char *buf, size_t buflen) {
    const char *units[] = {"B", "KiB", "MiB", "GiB", "TiB"};
    double size = (double)bytes;
    int unit_idx = 0;
    while (size >= 1024.0 && unit_idx < 4) {
        size /= 1024.0;
        unit_idx++;
    }
    if (unit_idx == 0) {
        snprintf(buf, buflen, "%" PRIu64 " B", bytes);
    } else {
        snprintf(buf, buflen, "%.1f %s", size, units[unit_idx]);
    }
}

/* Вивід у людському форматі */
static void print_human(const ProcessMetric *procs, size_t count, bool color, bool no_heading) {
    if (!no_heading) {
        if (color) {
            printf("%s%-8s %-20s %-8s %-12s %-12s%s\n",
                   ANSI_BOLD, "PID", "NAME", "STATE", "RSS", "VSZ", ANSI_RESET);
        } else {
            printf("%-8s %-20s %-8s %-12s %-12s\n",
                   "PID", "NAME", "STATE", "RSS", "VSZ");
        }
    }

    char rss_str[32], vsz_str[32];
    for (size_t i = 0; i < count; i++) {
        format_human_bytes(procs[i].rss_bytes, rss_str, sizeof(rss_str));
        format_human_bytes(procs[i].vsz_bytes, vsz_str, sizeof(vsz_str));

        if (color) {
            const char *state_col = (procs[i].state == 'R') ? ANSI_GREEN : ANSI_CYAN;
            printf("%-8d %-20s %s%-8c%s %-12s %-12s\n",
                   procs[i].pid, procs[i].name,
                   state_col, procs[i].state, ANSI_RESET,
                   rss_str, vsz_str);
        } else {
            printf("%-8d %-20s %-8c %-12s %-12s\n",
                   procs[i].pid, procs[i].name, procs[i].state, rss_str, vsz_str);
        }
    }
}

/* Вивід у машинному форматі TSV */
static void print_tsv(const ProcessMetric *procs, size_t count, bool no_heading, bool null_delim) {
    char term = null_delim ? '\0' : '\n';
    if (!no_heading && !null_delim) {
        printf("pid\tname\tstate\trss_bytes\tvsz_bytes\n");
    }
    for (size_t i = 0; i < count; i++) {
        printf("%d\t%s\t%c\t%" PRIu64 "\t%" PRIu64 "%c",
               procs[i].pid, procs[i].name, procs[i].state,
               procs[i].rss_bytes, procs[i].vsz_bytes, term);
    }
}

/* Вивід у машинному форматі JSON */
static void print_json(const ProcessMetric *procs, size_t count) {
    printf("{\n  \"timestamp\": %ld,\n  \"processes\": [\n", (long)time(NULL));
    for (size_t i = 0; i < count; i++) {
        printf("    {\n"
               "      \"pid\": %d,\n"
               "      \"name\": \"%s\",\n"
               "      \"state\": \"%c\",\n"
               "      \"rss_bytes\": %" PRIu64 ",\n"
               "      \"vsz_bytes\": %" PRIu64 "\n"
               "    }%s\n",
               procs[i].pid, procs[i].name, procs[i].state,
               procs[i].rss_bytes, procs[i].vsz_bytes,
               (i + 1 < count) ? "," : "");
    }
    printf("  ]\n}\n");
}

int main(int argc, char **argv) {
    /* Безпечна обробка розриву конвеєра */
    signal(SIGPIPE, SIG_DFL);

    Config cfg = {
        .mode = OUT_AUTO,
        .enable_color = false,
        .null_delimited = false,
        .no_heading = false
    };

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--json") == 0 || strcmp(argv[i], "-j") == 0) {
            cfg.mode = OUT_JSON;
        } else if (strcmp(argv[i], "--raw") == 0 || strcmp(argv[i], "--tsv") == 0) {
            cfg.mode = OUT_TSV;
        } else if (strcmp(argv[i], "--human") == 0 || strcmp(argv[i], "-H") == 0) {
            cfg.mode = OUT_HUMAN;
        } else if (strcmp(argv[i], "-z") == 0 || strcmp(argv[i], "--null") == 0) {
            cfg.null_delimited = true;
            cfg.mode = OUT_TSV;
        } else if (strcmp(argv[i], "--no-heading") == 0 || strcmp(argv[i], "-n") == 0) {
            cfg.no_heading = true;
        }
    }

    bool is_terminal = isatty(STDOUT_FILENO) == 1;

    /* Автоматичний вибір режиму виводу на основі типу дескриптора */
    if (cfg.mode == OUT_AUTO) {
        cfg.mode = is_terminal ? OUT_HUMAN : OUT_TSV;
    }

    cfg.enable_color = (cfg.mode == OUT_HUMAN) && detect_color_support(STDOUT_FILENO);

    /* Налаштування оптимальної буферизації потоку */
    if (cfg.mode == OUT_HUMAN && is_terminal) {
        setvbuf(stdout, NULL, _IOLBF, 0);
    } else {
        setvbuf(stdout, NULL, _IOFBF, 8192);
    }

    /* Симуляція зібраних метрик процесів */
    ProcessMetric sample_procs[] = {
        {1, "systemd", 'S', 12451840, 168427520},
        {412, "dbus-daemon", 'S', 4890624, 25165824},
        {1024, "nginx", 'S', 34078720, 142606336},
        {2048, "rust-worker", 'R', 268435456, 1073741824}
    };
    size_t count = sizeof(sample_procs) / sizeof(sample_procs[0]);

    switch (cfg.mode) {
        case OUT_JSON:
            print_json(sample_procs, count);
            break;
        case OUT_TSV:
            print_tsv(sample_procs, count, cfg.no_heading, cfg.null_delimited);
            break;
        case OUT_HUMAN:
        case OUT_AUTO:
            print_human(sample_procs, count, cfg.enable_color, cfg.no_heading);
            break;
    }

    return 0;
}
```
```cpp
// sysproc_stat.cpp — Ідіоматична реалізація дуального CLI мовою C++20
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <optional>
#include <format>
#include <chrono>
#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <csignal>

namespace {

constexpr std::string_view ANSI_RESET  = "\033[0m";
constexpr std::string_view ANSI_BOLD   = "\033[1m";
constexpr std::string_view ANSI_GREEN  = "\033[32m";
constexpr std::string_view ANSI_CYAN   = "\033[36m";

enum class OutputMode {
    Auto,
    Human,
    Json,
    Tsv
};

struct ProcessMetric {
    pid_t pid;
    std::string name;
    char state;
    uint64_t rss_bytes;
    uint64_t vsz_bytes;
};

struct Config {
    OutputMode mode = OutputMode::Auto;
    bool enable_color = false;
    bool null_delimited = false;
    bool no_heading = false;
};

[[nodiscard]] bool detect_color_support(int fd) noexcept {
    if (const char *no_color = std::getenv("NO_COLOR"); no_color && no_color[0] != '\0') {
        return false;
    }
    if (const char *force = std::getenv("CLICOLOR_FORCE"); force && std::string_view(force) != "0") {
        return true;
    }
    if (const char *term = std::getenv("TERM"); term && std::string_view(term) == "dumb") {
        return false;
    }
    if (const char *clicolor = std::getenv("CLICOLOR"); clicolor && std::string_view(clicolor) == "0") {
        return false;
    }
    return isatty(fd) == 1;
}

[[nodiscard]] std::string format_human_bytes(uint64_t bytes) {
    constexpr std::string_view units[] = {"B", "KiB", "MiB", "GiB", "TiB"};
    auto size = static_cast<double>(bytes);
    size_t unit_idx = 0;
    while (size >= 1024.0 && unit_idx < 4) {
        size /= 1024.0;
        unit_idx++;
    }
    if (unit_idx == 0) {
        return std::format("{} B", bytes);
    }
    return std::format("{:.1f} {}", size, units[unit_idx]);
}

void print_human(const std::vector<ProcessMetric> &procs, bool color, bool no_heading) {
    if (!no_heading) {
        if (color) {
            std::cout << std::format("{}{:<8} {:<20} {:<8} {:<12} {:<12}{}\n",
                                     ANSI_BOLD, "PID", "NAME", "STATE", "RSS", "VSZ", ANSI_RESET);
        } else {
            std::cout << std::format("{:<8} {:<20} {:<8} {:<12} {:<12}\n",
                                     "PID", "NAME", "STATE", "RSS", "VSZ");
        }
    }

    for (const auto &p : procs) {
        const auto rss_str = format_human_bytes(p.rss_bytes);
        const auto vsz_str = format_human_bytes(p.vsz_bytes);

        if (color) {
            const auto state_col = (p.state == 'R') ? ANSI_GREEN : ANSI_CYAN;
            std::cout << std::format("{:<8} {:<20} {}{:<8}{} {:<12} {:<12}\n",
                                     p.pid, p.name, state_col, p.state, ANSI_RESET, rss_str, vsz_str);
        } else {
            std::cout << std::format("{:<8} {:<20} {:<8} {:<12} {:<12}\n",
                                     p.pid, p.name, p.state, rss_str, vsz_str);
        }
    }
}

void print_tsv(const std::vector<ProcessMetric> &procs, bool no_heading, bool null_delim) {
    const char term = null_delim ? '\0' : '\n';
    if (!no_heading && !null_delim) {
        std::cout << "pid\tname\tstate\trss_bytes\tvsz_bytes\n";
    }
    for (const auto &p : procs) {
        std::cout << std::format("{}\t{}\t{}\t{}\t{}{}",
                                 p.pid, p.name, p.state, p.rss_bytes, p.vsz_bytes, term);
    }
}

void print_json(const std::vector<ProcessMetric> &procs) {
    const auto now = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());
    std::cout << std::format("{{\n  \"timestamp\": {},\n  \"processes\": [\n", now);
    for (size_t i = 0; i < procs.size(); ++i) {
        const auto &p = procs[i];
        std::cout << std::format("    {{\n"
                                 "      \"pid\": {},\n"
                                 "      \"name\": \"{}\",\n"
                                 "      \"state\": \"{}\",\n"
                                 "      \"rss_bytes\": {},\n"
                                 "      \"vsz_bytes\": {}\n"
                                 "    }}{}\n",
                                 p.pid, p.name, p.state, p.rss_bytes, p.vsz_bytes,
                                 (i + 1 < procs.size()) ? "," : "");
    }
    std::cout << "  ]\n}\n";
}

} // namespace

int main(int argc, char **argv) {
    std::signal(SIGPIPE, SIG_DFL);
    std::ios_base::sync_with_stdio(false);

    Config cfg;
    for (int i = 1; i < argc; ++i) {
        const std::string_view arg(argv[i]);
        if (arg == "--json" || arg == "-j") {
            cfg.mode = OutputMode::Json;
        } else if (arg == "--raw" || arg == "--tsv") {
            cfg.mode = OutputMode::Tsv;
        } else if (arg == "--human" || arg == "-H") {
            cfg.mode = OutputMode::Human;
        } else if (arg == "-z" || arg == "--null") {
            cfg.null_delimited = true;
            cfg.mode = OutputMode::Tsv;
        } else if (arg == "--no-heading" || arg == "-n") {
            cfg.no_heading = true;
        }
    }

    const bool is_terminal = isatty(STDOUT_FILENO) == 1;
    if (cfg.mode == OutputMode::Auto) {
        cfg.mode = is_terminal ? OutputMode::Human : OutputMode::Tsv;
    }

    cfg.enable_color = (cfg.mode == OutputMode::Human) && detect_color_support(STDOUT_FILENO);

    const std::vector<ProcessMetric> sample_procs = {
        {1, "systemd", 'S', 12451840, 168427520},
        {412, "dbus-daemon", 'S', 4890624, 25165824},
        {1024, "nginx", 'S', 34078720, 142606336},
        {2048, "rust-worker", 'R', 268435456, 1073741824}
    };

    switch (cfg.mode) {
        case OutputMode::Json:
            print_json(sample_procs);
            break;
        case OutputMode::Tsv:
            print_tsv(sample_procs, cfg.no_heading, cfg.null_delimited);
            break;
        case OutputMode::Human:
        case OutputMode::Auto:
            print_human(sample_procs, cfg.enable_color, cfg.no_heading);
            break;
    }

    return 0;
}
```
:::

---

## 3. Глибокий аналіз реалізації та крайові випадки

### 1. Механізм захисту від розриву каналу та SIGPIPE
У конвеєрах Unix програми часто з'єднуються з утилітами обмеження виводу, наприклад `head -n 2`. Коли `head` зчитує необхідну кількість рядків, вона завершує роботу та закриває дескриптор читання анонімного каналу. Наступна спроба нашої утиліти виконати системний виклик `write()` у дескриптор без читача генерує сигнал `SIGPIPE`.

За замовчуванням ядро Linux надсилає процесу сигнал `SIG_DFL`, який аварійно припиняє виконання програми зі статусом `141` (`128 + 13`). Якщо програма перехоплює сигнал `SIGPIPE` або ігнорує його (`signal(SIGPIPE, SIG_IGN)`), системний виклик `write()` завершується з помилкою `EPIPE` ("Broken pipe"). Наша реалізація явно встановлює `signal(SIGPIPE, SIG_DFL)` та уникає спаму повідомленнями про помилки у `STDERR`, забезпечуючи стандартний життєвий цикл процесів у конвеєрі Unix.

### 2. Оптимізація буферизації потоків введення-виведення
Стандартна бібліотека C автоматично призначає тип буферизації на основі результату `isatty()` під час ініціалізації середовища виконання:
- Для терміналів активується рядкова буферизація (`_IOLBF`), де кожен символ переносу рядка `\n` призводить до негайного виклику `write()`. Це забезпечує плавний інтерактивний вивід без затримок для очей оператора.
- Для файлів та каналів активується повна блокова буферизація (`_IOFBF`). Утиліта явно конфігурує буфер розміром 8192 байти за допомогою `setvbuf()`. Завдяки цьому при виводі тисяч рядків метрик процесів кількість системних викликів `write()` скорочується в десятки разів, а перемикання контексту ядра не стає вузьким місцем продуктивності.

### 3. Точність представлення даних та уникнення накопичення похибок
При форматуванні людиночитних значень пам'яті (`format_human_bytes`) операція ділення на `1024.0` призводить до округлення дробової частини. Наприклад, значення `12 451 840` байтів перетворюється на рядок `"11.9 MiB"`. Зворотне перетворення цього рядка парсером скрипту дасть `11.9 * 1024 * 1024 = 12 478 054.4` байти, що спотворює початкові дані на 26 кілобайтів.

У машинних режимах JSON та TSV утиліта принципово відмовляється від будь-яких округлень і передає сире 64-бітне ціле число `uint64_t`. Це гарантує нульову похибку при зборі метрик системними базами даних (Prometheus, InfluxDB).

---

## 4. Практичне тестування та інтеграція в системні сценарії

### Сценарій 1: Інтерактивний виклик оператором у терміналі
При прямому запуску у вікні термінала функція `isatty(STDOUT_FILENO)` повертає значення `1`. Утиліта автоматично вмикає ANSI-кольори та форматує байти пам'яті у зрозумілі величини `MiB` та `GiB`:

```bash
$ ./sysproc-stat
PID      NAME                 STATE    RSS          VSZ         
1        systemd              S        11.9 MiB     160.6 MiB   
412      dbus-daemon          S        4.7 MiB      24.0 MiB    
1024     nginx                S        32.5 MiB     136.0 MiB   
2048     rust-worker          R        256.0 MiB    1.0 GiB     
```

### Сценарій 2: Автоматичний перехід у TSV при переході в пайп
Коли вивід команди спрямовується на вхід іншої програми (`awk`, `cut`, `grep`), дескриптор `STDOUT` стає каналом зв'язку. Програма скидає всі оформлювальні елементи, що дозволяє виконувати прямі арифметичні розрахунки над числовими значеннями:

```bash
$ ./sysproc-stat | awk '$4 > 20000000 {print $2, $4}'
name rss_bytes
nginx 34078720
rust-worker 268435456
```

### Сценарій 3: Структурований розбір через jq
При використанні прапорця `--json` вивід утиліти стає суворо типізованим потоком JSON. Це дозволяє здійснювати складні запити та трансформації даних за допомогою фільтрів:

```bash
$ ./sysproc-stat --json | jq '.processes[] | select(.rss_bytes > 50000000) | {pid: .pid, process_name: .name}'
{
  "pid": 2048,
  "process_name": "rust-worker"
}
```

### Сценарій 4: Безпечна пакетна обробка з нульовим розділювачем
Використання прапорця `-z` у комбінації з `--no-heading` дозволяє передавати ідентифікатори процесів або їхні назви утиліті `xargs -0` без ризику спотворення даних спецсимволами:

```bash
$ ./sysproc-stat -z --no-heading | cut -z -f 1 | xargs -0 -I {} echo "Аналіз процесу PID: {}"
Аналіз процесу PID: 1
Аналіз процесу PID: 412
Аналіз процесу PID: 1024
Аналіз процесу PID: 2048
```
