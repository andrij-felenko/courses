# ⚙️ Моніторинг стану та кеш-статистики Device Mapper через C та C++

Цей практичний проєкт присвячено розробці автономної низькорівневої утиліти моніторингу продуктивності блокових пристроїв `dm-cache` та `dm-writecache`. Системні адміністратори та інженери зберігання даних часто стикаються з потребою контролювати коефіцієнт влучання (hit ratio), обсяг брудних блоків та заповненість метаданих у режимі реального часу, щоб завчасно реагувати на деградацію продуктивності SSD або загрозу буксування (thrashing) кешу.

У рамках цього проєкту розглянуто архітектуру збору телеметрії з підсистеми sysfs ядра Linux, алгоритми розрахунку ключових індикаторів (KPI), а також реалізовано дві повноцінні утиліти мовами C та C++, кожна з яких є ідіоматичною для своєї екосистеми.

---

## 1. Архітектура збору метрик та аналіз даних sysfs

Ядро Linux експортує поточний стан будь-якого мапованого пристрою Device Mapper через віртуальну файлову систему sysfs за шляхом `/sys/block/<dm-device>/dm/status`. Коли утиліта відкриває цей файл і виконує системний виклик `read()`, відповідний драйвер таргету (`dm-cache` або `dm-writecache`) формує однорядковий текстовий зріз по поточних лічильниках.

Слід враховувати, що віртуальні файли в sysfs не мають реального розміру (функція `stat()` повертає розмір 0 байтів). Через це спроба прочитати файл за допомогою фунцій, які покладаються на розмір файлу, завершиться невдачею. Зчитування повинно виконуватися фіксованим буфером (наприклад, 2048 байтів) за один системний виклик `read()`.

### 1.1 Структура рядка стану `dm-cache`

Для таргету `dm-cache` рядок статусу має такий формат:

```
0 204800000 cache 2 1024/32768 512 452100/524288 452100 12400 189000 3200 4500 12800 1024 ...
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

1. **Еволіція формату рядка статусу між версіями ядра:** У старих версіях ядер Linux (до 4.2) рядок статусу `dm-cache` містив менше полів, оскільки використовувалася політика `mq` замість `smq`. Парсер повинен перевіряти кількість успішно прочитаних полів (значення, повернене `sscanf`) і не робити припущень про наявність опціональних хвостів рядка.
2. **Права доступу та відсутність пристрою:** Файли у `/sys/block/` доступні для читання всім користувачам, однак сам віртуальний пристрій `dm-X` може бути від'єднаний LVM під час виконання команди `lvconvert`. Утиліта повинна коректно повертати помилку з чітким описом, а не завершуватися з помилкою сегментації (segmentation fault).
3. **Обнулення лічильників при перезавантаженні або зміні таблиці:** Лічильники `read_hits` та `write_misses` є 64-бітними неузгодженими інкрементальними величинами. При заміні таблиці `dmsetup reload` лічильники скидаються в 0, що повинно враховуватися в зовнішніх системах типу Prometheus при розрахунку похідних величин (`rate()`).

---

## 3. Особливості реалізації мовою C

Реалізація мовою C орієнтована на мінімальні накладні витрати пам'яті та максимальну сумісність із POSIX-системами. Вона використовує системні виклики `open()`, `read()`, `close()`, працює з фіксованими стакровими буферами й здійснює безпечний розбір рядків за допомогою `sscanf()`.

Основні інженерні рішення в C-версії:
- **Перевірка помилок на кожному кроці:** Програма коректно обробляє відсутність пристрою в `/sys/block/`, помилки доступу (наприклад, якщо утиліта запущена без належних прав) та невідповідність формату статусу.
- **Відсутність динамічного виділення пам'яті:** Утиліта не використовує `malloc()` чи `free()`, що робить її безпечною для використання в критичних системних демон-процесах або контейнерах із суворими обмеженнями пам'яті.
- **Обробка ділення на нуль:** Якщо пристрій тільки-но створено і сумарна кількість операцій дорівнює 0, утиліта повертає `Hit Ratio = 0.0%` замість генерації винятку `SIGFPE`.

---

## 4. Особливості реалізації мовою C++

Реалізація мовою C++20 базується на сучасних ідіомах безпеки та виразності. Вона використовує модуль `std::filesystem` для роботи з шляхами sysfs, файлові потоки `std::ifstream`, обгортку `std::optional` для безпечної обробки відсутності даних та безпечне форматування рядків `std::format`.

Основні переваги C++ реалізації:
- **Концепція RAII (Resource Acquisition Is Initialization):** Файлові потоки закриваються автоматично при виході з області видимості, що повністю усуває ризик витоку файлових дескрипторів при виникненні помилок.
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
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>

#define SYSFS_PATH_MAX 256
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

static int read_sysfs_status(const char *dm_name, char *buffer, size_t buf_size) {
    char path[SYSFS_PATH_MAX];
    snprintf(path, sizeof(path), "/sys/block/%s/dm/status", dm_name);

    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", path, strerror(errno));
        return -1;
    }

    ssize_t bytes = read(fd, buffer, buf_size - 1);
    close(fd);

    if (bytes <= 0) {
        fprintf(stderr, "Помилка читання зі статусного файлу sysfs\n");
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
        fprintf(stderr, "Використання: %s <dm-пристрій> (наприклад, dm-0)\n", argv[0]);
        return EXIT_FAILURE;
    }

    char buffer[BUFFER_SIZE];
    if (read_sysfs_status(argv[1], buffer, sizeof(buffer)) != 0) {
        return EXIT_FAILURE;
    }

    dm_cache_stats_t stats;
    if (parse_dm_cache_status(buffer, &stats) != 0) {
        return EXIT_FAILURE;
    }

    printf("=== Телеметрія dm-cache для %s ===\n", argv[1]);
    printf("Кешовано блоків:   %llu / %llu (%.2f%%)\n",
           stats.used_cache_blocks, stats.total_cache_blocks,
           (double)stats.used_cache_blocks / (double)stats.total_cache_blocks * 100.0);
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
#include <fstream>
#include <string>
#include <string_view>
#include <sstream>
#include <optional>
#include <format>
#include <filesystem>
#include <stdexcept>

namespace fs = std::filesystem;

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
        const fs::path sysfs_path = fs::path("/sys/block") / dm_name / "dm" / "status";
        std::ifstream file(sysfs_path);
        if (!file.is_open()) {
            std::cerr << "Не вдалося відкрити файл статусу: " << sysfs_path << '\n';
            return std::nullopt;
        }

        std::string line;
        if (!std::getline(file, line)) {
            return std::nullopt;
        }

        return parse_status_line(line);
    }

private:
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
        if (slash_pos != std::string::npos) {
            stats.used_cache_blocks = std::stoull(cache_usage.substr(0, slash_pos));
            stats.total_cache_blocks = std::stoull(cache_usage.substr(slash_pos + 1));
        }

        return stats;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <dm-пристрій> (наприклад, dm-0)\n";
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

Компіляція утиліти вимагає вказання прапорців стандартів C/C++. Прапорець `-std=c11` необхідний для підтримки сучасного стандарту C, а `-std=c++20` зумовлений використанням модулів `std::filesystem` та `std::format` у C++ версії:

```bash
# Компіляція C-версії (стандарт C11)
gcc -std=c11 -O2 -Wall -Wextra proj-dm-cache-status-monitor.c -o dm_status_c

# Компіляція C++-версії (стандарт C++20)
g++ -std=c++20 -O2 -Wall -Wextra proj-dm-cache-status-monitor.cpp -o dm_status_cpp
```

Приклад запуску для віртуального пристрою `dm-0`:

```bash
./dm_status_c dm-0
```

Утиліту можна легко обгорнути в системну службу systemd або інкорпорувати до складу агента моніторингу (наприклад, Telegraf exec plugin), забезпечуючи безперервний збір метрик для системного графічного аналізу в Grafana.
