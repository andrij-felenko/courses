# ⚙️ Моніторинг стану та кеш-статистики Device Mapper через C та C++

Цей практичний проєкт присвячено розробці автономної низькорівневої утиліти моніторингу продуктивності блокових пристроїв `dm-cache` та `dm-writecache`. Системні адміністратори та інженери зберігання даних часто стикаються з потребою контролювати коефіцієнт влучання (hit ratio), обсяг брудних блоків та заповненість метаданих у режимі реального часу, щоб завчасно реагувати на деградацію продуктивності SSD або загрозу буксування (thrashing) кешу.

У рамках цього проєкту розглянуто архітектуру збору телеметрії зі статусного інтерфейсу Device Mapper, алгоритми розрахунку ключових індикаторів (KPI), а також реалізовано дві повноцінні утиліти мовами C та C++, кожна з яких є ідіоматичною для своєї екосистеми.

---

## 1. Архітектура збору метрик і джерело телеметрії

Стан мапованого пристрою Device Mapper ядро віддає не через sysfs, а через ioctl `DM_TABLE_STATUS` на керувальному вузлі `/dev/mapper/control`: у `/sys/block/<dm-device>/dm/` лежать лише `name`, `uuid` та `suspended`, статусу там немає. У відповідь на ioctl драйвер таргету (`dm-cache` або `dm-writecache`) формує однорядковий текстовий зріз поточних лічильників.

До цього рядка ведуть два шляхи: лінкуватися з `libdevmapper` і викликати ioctl самотужки або запустити `dmsetup status <пристрій>` і розібрати його вивід. Нижче обрано другий — він не тягне зовнішньої залежності й дає той самий рядок. Обидва потребують прав `root`: ioctl на `/dev/mapper/control` вимагає `CAP_SYS_ADMIN`.

### 1.1 Структура рядка стану `dm-cache`

Для таргету `dm-cache` рядок статусу має такий формат:

```
0 209715200 cache 8 1024/32768 512 176000/204800 452100 12400 189000 3200 4500 12800 1024 ...
```

Для аналізу продуктивності найбільший інтерес становлять наступні поля:
- Поля 8 та 9 (`read_hits` та `read_misses`): Лічильники операцій читання.
- Поля 10 та 11 (`write_hits` та `write_misses`): Лічильники операцій запису.
- Поля 12 та 13 (`demotions` та `promotions`): Динаміка міграції блоків між SSD та HDD.
- Поле 14 (`dirty_blocks`): Кількість брудних чанків у кеші, що очікують на flush.

### 1.2 Математичні формули метрик продуктивності

Для оцінки ефективності кешу утиліта розраховує два основні коефіцієнти:

1. **Коефіцієнт влучання (Hit Ratio):**
   ```
   Hit Ratio = (read_hits + write_hits) / (read_hits + read_misses + write_hits + write_misses) · 100%
   ```
   Значення `Hit Ratio > 80%` вважається відмінним показником. Якщо значення опускається нижче 50% при значному обсязі В/В, це вказує на те, що розмір кешу є замалим для активного робочого набору (working set) додатка, і система витрачає більше ресурсів на міграцію блоків, ніж отримує виграшу від SSD.

2. **Заповненість кешу (Cache Usage Percentage):**
   ```
   Usage Pct = (used_cache_blocks / total_cache_blocks) · 100%
   ```
   При наближенні заповненості до 100% політика `smq` починає витісняти найменш запитувані блоки (demotions) на HDD, щоб звільнити місце для нових гарячих чанків.

---

## 2. Крайові випадки та обробка помилок

При розробці системних утиліт моніторингу важливо передбачити наступні критичні ситуації:

1. **Еволюція формату рядка статусу між версіями ядра:** Хвіст рядка `dm-cache` залежить від версії ядра й обраної політики: до 4.2 типовою була `mq` з власним набором аргументів, потім `smq` без жодного, а поля `rw|ro` та `needs_check` дописали ще пізніше. Парсер повинен перевіряти кількість успішно прочитаних полів (значення, повернене `sscanf`) і не робити припущень про хвіст рядка.
2. **Права доступу та відсутність пристрою:** Статус доступний лише з правами `root`, а сам пристрій може зникнути просто між двома опитуваннями — наприклад, поки LVM виконує `lvconvert --splitcache`. Утиліта повинна коректно повертати помилку з чітким описом, а не завершуватися з помилкою сегментації (segmentation fault).
3. **Обнулення лічильників при перезавантаженні або зміні таблиці:** Лічильники `read_hits` та `write_misses` — 64-бітні величини, що лише зростають. При заміні таблиці `dmsetup reload` лічильники скидаються в 0, що повинно враховуватися в зовнішніх системах типу Prometheus при розрахунку похідних величин (`rate()`).

---

## 3. Особливості реалізації мовою C

Реалізація мовою C орієнтована на мінімальні накладні витрати пам'яті та максимальну сумісність із POSIX-системами. Вона запускає `dmsetup status` через `popen()`, читає відповідь у фіксований стековий буфер і розбирає рядок за допомогою `sscanf()`.

Основні інженерні рішення в C-версії:
- **Перевірка помилок на кожному кроці:** Програма коректно обробляє відсутність пристрою в `/sys/block/`, помилки доступу (наприклад, якщо утиліта запущена без належних прав) та невідповідність формату статусу.
- **Відсутність динамічного виділення пам'яті у власному коді:** Утиліта не викликає `malloc()` чи `free()` — усі буфери стекові. Плата за простоту — `popen()`, який породжує оболонку, тож ім'я пристрою перед підстановкою перевіряється на дозволені символи, а в оточенні має бути наявний `dmsetup`.
- **Обробка ділення на нуль:** Якщо пристрій тільки-но створено і сумарна кількість операцій дорівнює 0, утиліта повертає `Hit Ratio = 0.0%` замість генерації винятку `SIGFPE`.

---

## 4. Особливості реалізації мовою C++

Реалізація мовою C++20 базується на сучасних ідіомах безпеки та виразності. Вона бере той самий рядок від `dmsetup`, тримає канал у `std::unique_ptr` з власним видалювачем, розбирає рядок через `std::istringstream`, повертає результат у `std::optional` і форматує вивід через `std::format`.

Основні переваги C++ реалізації:
- **Концепція RAII (Resource Acquisition Is Initialization):** Канал закривається автоматично при виході з області видимості — `pclose` викликає видалювач `unique_ptr`, тож дескриптор не тече навіть на шляху з помилкою.
- **Використання `std::string_view`:** Дозволяє передавати назви пристроїв без зайвого копіювання рядків.
- **Інкапсуляція логики в класі `DmStatusMonitor`:** Модульна структура дозволяє легко інтегрувати цей код як плагін до більших систем моніторингу (наприклад, Prometheus C++ client або утиліта діагностики накопичувачів).

---

## 5. Джерельний код реалізацій

Нижче наведено паралельні реалізації утиліти моніторингу мовами C та C++.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <errno.h>

#define CMD_MAX 256
#define BUFFER_SIZE 2048

typedef struct {
    unsigned long long read_hits;
    unsigned long long read_misses;
    unsigned long long write_hits;
    unsigned long long write_misses;
    unsigned long long demotions;
    unsigned long long promotions;
    unsigned long long dirty_blocks;
    unsigned long long used_cache_blocks;
    unsigned long long total_cache_blocks;
    double hit_ratio;
} dm_cache_stats_t;

static int name_is_safe(const char *s) {
    if (*s == '\0') return 0;
    for (; *s; ++s) {
        if (!isalnum((unsigned char)*s) && *s != '-' && *s != '_' && *s != '.')
            return 0;
    }
    return 1;
}

static int read_dm_status(const char *dm_name, char *buffer, size_t buf_size) {
    char cmd[CMD_MAX];

    if (!name_is_safe(dm_name)) {
        fprintf(stderr, "Недопустиме ім'я пристрою: %s\n", dm_name);
        return -1;
    }
    snprintf(cmd, sizeof(cmd), "dmsetup status %s", dm_name);

    FILE *pipe = popen(cmd, "r");
    if (!pipe) {
        fprintf(stderr, "Не вдалося запустити dmsetup: %s\n", strerror(errno));
        return -1;
    }

    size_t bytes = fread(buffer, 1, buf_size - 1, pipe);
    int rc = pclose(pipe);

    if (bytes == 0 || rc != 0) {
        fprintf(stderr, "dmsetup status не повернув даних для %s\n", dm_name);
        return -1;
    }

    buffer[bytes] = '\0';
    return 0;
}

static int parse_dm_cache_status(const char *status_str, dm_cache_stats_t *stats) {
    long long start, length;
    char target_type[32];
    unsigned int meta_block_size;
    unsigned long long meta_used, meta_total;
    unsigned int chunk_size;

    int parsed = sscanf(status_str, "%lld %lld %31s %u %llu/%llu %u %llu/%llu %llu %llu %llu %llu %llu %llu %llu",
                       &start, &length, target_type,
                       &meta_block_size, &meta_used, &meta_total,
                       &chunk_size, &stats->used_cache_blocks, &stats->total_cache_blocks,
                       &stats->read_hits, &stats->read_misses,
                       &stats->write_hits, &stats->write_misses,
                       &stats->demotions, &stats->promotions, &stats->dirty_blocks);

    if (parsed < 16 || strcmp(target_type, "cache") != 0) {
        fprintf(stderr, "Рядок статусу не відповідає формату dm-cache або це інший target\n");
        return -1;
    }

    unsigned long long total_ops = stats->read_hits + stats->read_misses + stats->write_hits + stats->write_misses;
    if (total_ops > 0) {
        stats->hit_ratio = ((double)(stats->read_hits + stats->write_hits) / (double)total_ops) * 100.0;
    } else {
        stats->hit_ratio = 0.0;
    }

    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <dm-пристрій> (наприклад, my_cached_dev)\n", argv[0]);
        return EXIT_FAILURE;
    }

    char buffer[BUFFER_SIZE];
    if (read_dm_status(argv[1], buffer, sizeof(buffer)) != 0) {
        return EXIT_FAILURE;
    }

    dm_cache_stats_t stats = {0};
    if (parse_dm_cache_status(buffer, &stats) != 0) {
        return EXIT_FAILURE;
    }

    printf("=== Телеметрія dm-cache для %s ===\n", argv[1]);
    double usage_pct = stats.total_cache_blocks
                     ? (double)stats.used_cache_blocks / (double)stats.total_cache_blocks * 100.0
                     : 0.0;
    printf("Кешовано блоків:   %llu / %llu (%.2f%%)\n",
           stats.used_cache_blocks, stats.total_cache_blocks, usage_pct);
    printf("Влучання (Hits):   Читання: %llu, Запис: %llu\n", stats.read_hits, stats.write_hits);
    printf("Промахи (Misses):  Читання: %llu, Запис: %llu\n", stats.read_misses, stats.write_misses);
    printf("Коефіцієнт Hit Ratio: %.2f%%\n", stats.hit_ratio);
    printf("Брудні блоки:      %llu\n", stats.dirty_blocks);
    printf("Міграція даних:    Promotions: %llu, Demotions: %llu\n", stats.promotions, stats.demotions);

    if (stats.hit_ratio < 50.0 && (stats.read_hits + stats.read_misses) > 10000) {
        printf("УВАГА: Низький Hit Ratio! Розмір кешу може бути замалим для робочого набору.\n");
    }

    return EXIT_SUCCESS;
}
```

```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <sstream>
#include <optional>
#include <format>
#include <memory>
#include <algorithm>
#include <cctype>
#include <cstdint>
#include <cstdio>
#include <stdexcept>

struct DmCacheStats {
    uint64_t read_hits{0};
    uint64_t read_misses{0};
    uint64_t write_hits{0};
    uint64_t write_misses{0};
    uint64_t demotions{0};
    uint64_t promotions{0};
    uint64_t dirty_blocks{0};
    uint64_t used_cache_blocks{0};
    uint64_t total_cache_blocks{0};

    [[nodiscard]] double hit_ratio() const noexcept {
        const uint64_t total_ops = read_hits + read_misses + write_hits + write_misses;
        if (total_ops == 0) return 0.0;
        return (static_cast<double>(read_hits + write_hits) / static_cast<double>(total_ops)) * 100.0;
    }

    [[nodiscard]] double cache_usage_pct() const noexcept {
        if (total_cache_blocks == 0) return 0.0;
        return (static_cast<double>(used_cache_blocks) / static_cast<double>(total_cache_blocks)) * 100.0;
    }
};

class DmStatusMonitor {
public:
    static std::optional<DmCacheStats> fetch_cache_stats(std::string_view dm_name) {
        if (!name_is_safe(dm_name)) {
            std::cerr << "Недопустиме ім'я пристрою: " << dm_name << '\n';
            return std::nullopt;
        }

        const std::string cmd = std::format("dmsetup status {}", dm_name);
        const std::unique_ptr<std::FILE, decltype(&pclose)> pipe(popen(cmd.c_str(), "r"), &pclose);
        if (!pipe) {
            std::cerr << "Не вдалося запустити dmsetup для " << dm_name << '\n';
            return std::nullopt;
        }

        std::string line;
        char chunk[256];
        while (std::fgets(chunk, sizeof(chunk), pipe.get()) != nullptr) {
            line += chunk;
            if (line.back() == '\n') break;
        }
        if (line.empty()) {
            return std::nullopt;
        }

        return parse_status_line(line);
    }

private:
    static bool name_is_safe(std::string_view name) {
        return !name.empty() && std::all_of(name.begin(), name.end(), [](unsigned char c) {
            return std::isalnum(c) || c == '-' || c == '_' || c == '.';
        });
    }

    static std::optional<DmCacheStats> parse_status_line(const std::string& line) {
        std::istringstream iss(line);
        int64_t start{0}, length{0};
        std::string target_type;

        if (!(iss >> start >> length >> target_type) || target_type != "cache") {
            return std::nullopt;
        }

        uint32_t meta_bs{0}, chunk_sz{0};
        std::string meta_usage, cache_usage;

        DmCacheStats stats;
        if (!(iss >> meta_bs >> meta_usage >> chunk_sz >> cache_usage
                  >> stats.read_hits >> stats.read_misses
                  >> stats.write_hits >> stats.write_misses
                  >> stats.demotions >> stats.promotions >> stats.dirty_blocks)) {
            return std::nullopt;
        }

        const auto slash_pos = cache_usage.find('/');
        if (slash_pos == std::string::npos) {
            return std::nullopt;
        }
        try {
            stats.used_cache_blocks = std::stoull(cache_usage.substr(0, slash_pos));
            stats.total_cache_blocks = std::stoull(cache_usage.substr(slash_pos + 1));
        } catch (const std::exception&) {
            return std::nullopt;
        }

        return stats;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <dm-пристрій> (наприклад, my_cached_dev)\n";
        return EXIT_FAILURE;
    }

    const std::string_view dm_device = argv[1];
    const auto stats = DmStatusMonitor::fetch_cache_stats(dm_device);

    if (!stats) {
        std::cerr << "Помилка розбору телеметрії dm-cache для " << dm_device << '\n';
        return EXIT_FAILURE;
    }

    std::cout << std::format("=== Телеметрія dm-cache для {} ===\n", dm_device)
              << std::format("Кешовано блоків:   {} / {} ({:.2f}%)\n",
                             stats->used_cache_blocks, stats->total_cache_blocks, stats->cache_usage_pct())
              << std::format("Влучання (Hits):   Читання: {}, Запис: {}\n", stats->read_hits, stats->write_hits)
              << std::format("Промахи (Misses):  Читання: {}, Запис: {}\n", stats->read_misses, stats->write_misses)
              << std::format("Коефіцієнт Hit Ratio: {:.2f}%\n", stats->hit_ratio())
              << std::format("Брудні блоки:      {}\n", stats->dirty_blocks)
              << std::format("Міграція даних:    Promotions: {}, Demotions: {}\n", stats->promotions, stats->demotions);

    if (stats->hit_ratio() < 50.0 && (stats->read_hits + stats->read_misses) > 10000) {
        std::cout << "УВАГА: Низький Hit Ratio! Розмір кешу може бути замалим для робочого набору.\n";
    }

    return EXIT_SUCCESS;
}
```
:::

---

## 6. Інтеграція та компіляція

Компіляція утиліти вимагає вказання прапорців стандартів C/C++. Прапорець `-std=c11` необхідний для підтримки сучасного стандарту C, а `-std=gnu++20` — використанням `std::format` разом із POSIX-функцією `popen()`, якої строгий `-std=c++20` не оголошує:

```bash
# Компіляція C-версії (стандарт C11)
gcc -std=c11 -O2 -Wall -Wextra proj-dm-cache-status-monitor.c -o dm_status_c

# Компіляція C++-версії (C++20 з POSIX-розширеннями)
g++ -std=gnu++20 -O2 -Wall -Wextra proj-dm-cache-status-monitor.cpp -o dm_status_cpp
```

Приклад запуску для кешованого пристрою `my_cached_dev` (потрібні права `root`):

```bash
sudo ./dm_status_c my_cached_dev
```

Утиліту можна легко обгорнути в системну службу systemd або інкорпорувати до складу агента моніторингу (наприклад, Telegraf exec plugin), забезпечуючи безперервний збір метрик для системного графічного аналізу в Grafana.
