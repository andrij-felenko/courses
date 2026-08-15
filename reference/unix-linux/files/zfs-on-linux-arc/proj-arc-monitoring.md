# ⚙️ Моніторинг та аналіз ефективності ARC кешу мовами C та C++

Підсистема ZFS on Linux відмовляється від використання стандартного сторінкового кешу Linux (Page Cache), тому традиційні утиліти моніторингу системної статистики, такі як `free`, `vmstat` або `top`, не показують реального використання пам'яті під кешування файлових даних. Оскільки кеш ARC живе всередині ядра через шар абстракції SPL (Solaris Porting Layer) і розподіляє пам'ять за допомогою спеціалізованих слаб-алокаторів `spl_kmem_cache`, вся телеметрія експортується безпосередньо через псевдофайл `/proc/spl/kstat/zfs/arcstats`.

Цей практичний проект демонструє створення високоефективного аналізатора статистики ARC кешу. Програма відкриває псевдофайл `/proc/spl/kstat/zfs/arcstats`, зчитує ключові метрики продуктивності, обчислює загальний відсоток влучань (Hit Ratio), розбиття між MRU (Recency) та MFU (Frequency), використання пам'яті під метадані та генерує підсумковий діагностичний звіт для системних адміністраторів.

## 1. Математична модель аналізу телеметрії

Для отримання коректних аналітичних даних утиліта повинна розпарсити текстовий формат `kstat`. Файл містить заголовні рядки, після яких розміщено пари «ключ-значення». 

Програма обчислює три основні групи показників:

1. **Загальний Hit Ratio (у відсотках)** — характеризує підсумкову ефективність кешування для всіх операцій читання:
```
hit_ratio = (hits * 100.0) / (hits + misses)      [відсоток влучань ARC]
```

2. **Частка MRU та MFU серед усіх влучань** — показує баланс між нещодавно запитаними та часто запитуваними блоками:
```
mru_percent = (mru_hits * 100.0) / hits            [частка недавніх звернень]
mfu_percent = (mfu_hits * 100.0) / hits            [частка частоти]
```

3. **Використання оперативної пам'яті в мегабайтах (МБ)** — перераховує байтові лічильники ядра у зрозумілі одиниці:
```
size_mb = size / (1024.0 * 1024.0)                [поточний розмір ARC]
target_mb = c / (1024.0 * 1024.0)                 [цільовий розмір c]
meta_mb = arc_meta_used / (1024.0 * 1024.0)       [використано під метадані]
```

## 2. Реалізація діагностичного інструменту

Приклад реалізації наводиться у двох вкладках: низькорівнева реалізація на мові C зі стандартними файловими потоками `FILE*` та ідіоматична версія на C++ із застосуванням RAII, контейнерів STL, сильних типів та обробки винятків.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define ARCSTATS_PATH "/proc/spl/kstat/zfs/arcstats"
#define BUFFER_SIZE 256

typedef struct {
    unsigned long long hits;
    unsigned long long misses;
    unsigned long long mru_hits;
    unsigned long long mfu_hits;
    unsigned long long size;
    unsigned long long c;
    unsigned long long p;
    unsigned long long arc_meta_used;
} arc_stats_t;

int read_arcstats(arc_stats_t *stats) {
    FILE *fp = fopen(ARCSTATS_PATH, "r");
    if (!fp) {
        perror("Не вдалося відкрити " ARCSTATS_PATH);
        return -1;
    }

    char line[BUFFER_SIZE];
    char key[64];
    unsigned long long value;
    int type;

    memset(stats, 0, sizeof(arc_stats_t));

    while (fgets(line, sizeof(line), fp)) {
        if (sscanf(line, "%63s %d %llu", key, &type, &value) == 3) {
            if (strcmp(key, "hits") == 0) stats->hits = value;
            else if (strcmp(key, "misses") == 0) stats->misses = value;
            else if (strcmp(key, "mru_hits") == 0) stats->mru_hits = value;
            else if (strcmp(key, "mfu_hits") == 0) stats->mfu_hits = value;
            else if (strcmp(key, "size") == 0) stats->size = value;
            else if (strcmp(key, "c") == 0) stats->c = value;
            else if (strcmp(key, "p") == 0) stats->p = value;
            else if (strcmp(key, "arc_meta_used") == 0) stats->arc_meta_used = value;
        }
    }

    fclose(fp);
    return 0;
}

void print_report(const arc_stats_t *stats) {
    unsigned long long total_accesses = stats->hits + stats->misses;
    double hit_ratio = total_accesses > 0 ? ((double)stats->hits * 100.0) / total_accesses : 0.0;
    double mru_pct = stats->hits > 0 ? ((double)stats->mru_hits * 100.0) / stats->hits : 0.0;
    double mfu_pct = stats->hits > 0 ? ((double)stats->mfu_hits * 100.0) / stats->hits : 0.0;

    double size_mb = (double)stats->size / (1024.0 * 1024.0);
    double c_mb = (double)stats->c / (1024.0 * 1024.0);
    double p_mb = (double)stats->p / (1024.0 * 1024.0);
    double meta_mb = (double)stats->arc_meta_used / (1024.0 * 1024.0);

    printf("================ ZFS ARC Diagnostics (C) ================\n");
    printf("Поточний розмір ARC (size) : %8.2f МБ\n", size_mb);
    printf("Цільовий розмір кешу (c)   : %8.2f МБ\n", c_mb);
    printf("Вага Recency MRU (p)       : %8.2f МБ\n", p_mb);
    printf("Пам'ять під метадані       : %8.2f МБ\n", meta_mb);
    printf("---------------------------------------------------------\n");
    printf("Загальний Hit Ratio        : %8.2f %%\n", hit_ratio);
    printf("Частка MRU Hits            : %8.2f %%\n", mru_pct);
    printf("Частка MFU Hits            : %8.2f %%\n", mfu_pct);
    printf("=========================================================\n");
}

int main(void) {
    arc_stats_t stats;
    if (read_arcstats(&stats) != 0) {
        return EXIT_FAILURE;
    }
    print_report(&stats);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <iomanip>
#include <system_error>
#include <cstdint>

namespace zfs {

struct ArcMetrics {
    std::uint64_t hits{0};
    std::uint64_t misses{0};
    std::uint64_t mru_hits{0};
    std::uint64_t mfu_hits{0};
    std::uint64_t size{0};
    std::uint64_t c{0};
    std::uint64_t p{0};
    std::uint64_t arc_meta_used{0};
};

class ArcMonitor {
private:
    static constexpr std::string_view kArcstatsPath = "/proc/spl/kstat/zfs/arcstats";

public:
    [[nodiscard]] ArcMetrics fetchMetrics() const {
        std::ifstream file{std::string(kArcstatsPath)};
        if (!file.is_open()) {
            throw std::system_error(
                errno, 
                std::generic_category(), 
                "Не вдалося відкрити " + std::string(kArcstatsPath)
            );
        }

        ArcMetrics metrics;
        std::string line;

        // Перші рядки kstat службові (шапка й рядок «name type data»), тож
        // розбираємо порядково й мовчки пропускаємо все, що не лягає у трійку.
        while (std::getline(file, line)) {
            std::istringstream ls{line};
            std::string key;
            int type{0};
            std::uint64_t value{0};
            if (!(ls >> key >> type >> value)) continue;

            if (key == "hits") metrics.hits = value;
            else if (key == "misses") metrics.misses = value;
            else if (key == "mru_hits") metrics.mru_hits = value;
            else if (key == "mfu_hits") metrics.mfu_hits = value;
            else if (key == "size") metrics.size = value;
            else if (key == "c") metrics.c = value;
            else if (key == "p") metrics.p = value;
            else if (key == "arc_meta_used") metrics.arc_meta_used = value;
        }

        return metrics;
    }

    void displayReport(const ArcMetrics& m) const {
        const std::uint64_t total_accesses = m.hits + m.misses;
        const double hit_ratio = total_accesses > 0 ? (static_cast<double>(m.hits) * 100.0) / total_accesses : 0.0;
        const double mru_pct = m.hits > 0 ? (static_cast<double>(m.mru_hits) * 100.0) / m.hits : 0.0;
        const double mfu_pct = m.hits > 0 ? (static_cast<double>(m.mfu_hits) * 100.0) / m.hits : 0.0;

        const double size_mb = static_cast<double>(m.size) / (1024.0 * 1024.0);
        const double c_mb = static_cast<double>(m.c) / (1024.0 * 1024.0);
        const double p_mb = static_cast<double>(m.p) / (1024.0 * 1024.0);
        const double meta_mb = static_cast<double>(m.arc_meta_used) / (1024.0 * 1024.0);

        std::cout << std::fixed << std::setprecision(2);
        std::cout << "================ ZFS ARC Diagnostics (C++) ================\n";
        std::cout << "Поточний розмір ARC (size) : " << std::setw(8) << size_mb << " МБ\n";
        std::cout << "Цільовий розмір кешу (c)   : " << std::setw(8) << c_mb << " МБ\n";
        std::cout << "Вага Recency MRU (p)       : " << std::setw(8) << p_mb << " МБ\n";
        std::cout << "Пам'ять під метадані       : " << std::setw(8) << meta_mb << " МБ\n";
        std::cout << "---------------------------------------------------------\n";
        std::cout << "Загальний Hit Ratio        : " << std::setw(8) << hit_ratio << " %\n";
        std::cout << "Частка MRU Hits            : " << std::setw(8) << mru_pct << " %\n";
        std::cout << "Частка MFU Hits            : " << std::setw(8) << mfu_pct << " %\n";
        std::cout << "=========================================================\n";
    }
};

} // namespace zfs

int main() {
    try {
        zfs::ArcMonitor monitor;
        const auto metrics = monitor.fetchMetrics();
        monitor.displayReport(metrics);
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
:::

## 3. Детальний аналіз механізмів обробки та розширена інтерпретація метрик

Під час аналізу роботи представлених утиліт та їх інтеграції в комерційні системи моніторингу (такі як Prometheus exporters, Zabbix або Datadog agents) слід звернути увагу на архітектурні деталі взаємодії з файловою системою `/proc`.

### Особливості зчитування псевдофайлу `/proc/spl/kstat/zfs/arcstats`
Файл `/proc/spl/kstat/zfs/arcstats` є віртуальним вікном інтерфейсу kstat ядра. При кожному читанні модуль ZFS генерує послідовність рядків із внутрішніх лічильників структури `arc_stats_t`, які оновлюються атомарно. 

Розбір рядків через `sscanf` у версії на C іде в фіксований буфер на 256 байтів, а ключ читається з обмеженням `%63s` — тож ані задовгий рядок, ані задовга назва лічильника не вилізуть за межі масивів. Застосування `strcmp` для ключових слів дозволяє мапувати рядкові назви параметрів на статичні поля структури `arc_stats_t`. При цьому версія на C++ пропонує більш високий рівень безпеки типів: використання `std::ifstream` спільно з оператором вилучення з потоку `>>` автоматично обробляє пробіли та форматування без ризику виходу за межі пам'яті.

### Інтерпретація динаміки зміщення параметра `p`
Значення параметра `p` у виводі діагностики показує, в який бік зміщено адаптивний баланс кешу. Один застережний рядок: в OpenZFS від 2.2 лічильника `p` в `arcstats` уже немає — ARC переписано, — тож на свіжій системі утиліта покаже тут нуль, і це не помилка розбору. Якщо параметр `p` становить понад 70% від цільового значення `c`, це сигналізує про те, що система обробляє потік нових, раніше не кешованих даних. Такий стан притаманний серверам резервного копіювання або потокового відео.

Якщо ж значення `p` наближається до нуля, ARC майже повністю віддав пам'ять під список MFU (Frequency). Це означає, що система утримує гарячі індекси СУБД та часті таблиці, а повторні запити обробляються з оперативної пам'яті без залучення I/O дисків.

### Взаємодія з Linux Kernel Shrinker та тиск метаданих
Коли система працює під високим тиском оперативної пам'яті, ядро Linux активує `shrinker`. У цей момент лічильник `c` (цільовий розмір ARC) починає динамічно зменшуватися. Якщо значення `size` значно перевищує `c`, підсистема ARC Eviction витісняє блоки зі списків MRU та MFU, доки `size` не досягне нової цілі `c`.

Якщо в аналізованому виводі показник `arc_meta_used` становить понад 70% від загального розміру `size`, системному інженеру слід перевірити параметр `zfs_arc_meta_limit_percent`. Занадто високе значення цього параметра загрожує витісненням даних користувача в умовах активного обходу каталогу (команди `find`, `du`, `rsync`).

### Порівняльний аналіз підходів реалізації на C та C++
Версія утиліти на мові C розроблена для застосування у системних сервісах мінімального розміру (наприклад, у вбудованих прошивках на базі Alpine Linux або BusyBox), де важливі мінімальний розмір виконуваного бінарного файлу та відсутність залежностей від стандартної бібліотеки C++. Вона використовує виключно стандартні POSIX-функції `fopen`, `fgets`, `sscanf` та `fclose`. Обробка помилок виконується через аналіз коду повернення та перевірку `NULL` файлового вказівника.

Версія на C++, навпаки, застосовує сучасні парадигми проєктування:
1. **Інкапсуляція у класі `ArcMonitor`**: Всі операції відкриття, розбору та форматування згруповано всередині єдиного класу, що виключає забруднення глобального простору імен.
2. **Гарантія вивільнення ресурсів (RAII)**: Об'єкт `std::ifstream` автоматично закриває файловий дескриптор при виході з області видимості методів, навіть якщо під час зчитування виникнув виняток.
3. **Строга типізація та безпека**: Поля структури `ArcMetrics` ініціалізуються значеннями за замовчуванням при конструюванні. Тип `std::uint64_t` фіксує ширину лічильника в 64 біти на будь-якій платформі — рівно стільки, скільки віддає ядро, тож значення не зрізається.

### Рекомендації з автоматизації моніторингу
Для створення безперервного моніторингу у виробничому середовищі розроблену утиліту можна доповнити циклом із затримкою `sleep()` або інтегрувати її у демона системи збору метрик. При цьому рекомендується обчислювати дельту метрик `hits` та `misses` за певний інтервал часу (наприклад, 1 секунду) для отримання миттєвого Hit Ratio замість накопичувального показника з моменту завантаження системи.
