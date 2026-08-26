# ⚙️ Практикум: утиліта інспекції робочої множини процесу

Оцінка реальної робочої множини працюючого процесу в просторі користувача вимагає інструментів, які дозволяють зафіксувати, які саме віртуальні сторінки перебувають у фізичній пам'яті (RAM) та до яких із них центральний процесор реально звертався протягом заданого часового вікна `Δ`.

У просторі користувача безпосередній доступ до апаратних регістрів MMU заблоковано з міркувань безпеки та ізоляції пам'яті процесів. Проте ядро Linux надає три взаємодоповнюючі інтерфейси віртуальної файлової системи `procfs` та системних викликів, за допомогою яких можна побудувати повноцінний інструментарій вимірювання робочої множини процесу за моделлю Деннінга:

1. **`/proc/[pid]/clear_refs` та `/proc/[pid]/smaps_rollup`:** Найшвидший спосіб вимірювання робочої множини на рівні всього процесу. Запис значення `1` у файл `clear_refs` змушує ядро обійти всі таблиці сторінок процесу та скинути апаратний біт звернення (`Accessed` у x86-64 PTE або `AF` в ARM64). Коли процес продовжує виконання протягом інтервалу спостереження `Δ`, апаратний блок MMU встановлює біт звернення лише на тих сторінках, до яких процесор виконує інструкції читання чи запису. Подальше зчитування зведеного файлу `smaps_rollup` повертає поле `Referenced`, яке містить точний обсяг пам'яті (у кілобайтах), що використовувався у цьому вікні.
2. **Системний виклик `mincore()`:** Дозволяє швидко отримати бінарний вектор резидентності для довільного діапазону віртуальних адрес. Він перевіряє, чи завантажені сторінки у фізичні кадри RAM, без виконання операцій доступу до самих даних (що запобігає виникненню небажаних сторінкових збоїв під час діагностики).
3. **Файл `/proc/[pid]/pagemap`:** Надає найглибший рівень деталізації. Це 64-бітний двійковий дескриптор на кожну віртуальну сторінку, який розкриває номер фізичного кадру (PFN), біт присутності сторінки в пам'яті (`Page Present`) та біт вивантаження у простір підкачки (`Page Swapped`).

Нижче наведено практичну реалізацію цих методів з детальним аналізом механізмів їхньої роботи.

## Вимірювання активної робочої множини через clear_refs

Програма фіксує ідентифікатор цільового процесу (PID), скидає біти звернення через `clear_refs`, очікує вказане вікно спостереження `Δ` (у секундах) і зчитує підсумок зі `smaps_rollup`.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>

/*
 * Зчитує поле Referenced (у кілобайтах) із файлу /proc/[pid]/smaps_rollup.
 * Повертає 0 у разі успіху, -1 у разі помилки.
 */
static int read_referenced_kb(pid_t pid, unsigned long *referenced_kb, unsigned long *rss_kb) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/smaps_rollup", pid);

    FILE *f = fopen(path, "r");
    if (!f) {
        return -1;
    }

    char line[256];
    *referenced_kb = 0;
    *rss_kb = 0;
    int found = 0;

    while (fgets(line, sizeof(line), f)) {
        if (sscanf(line, "Rss: %lu kB", rss_kb) == 1) {
            found |= 1;
        } else if (sscanf(line, "Referenced: %lu kB", referenced_kb) == 1) {
            found |= 2;
        }
        if (found == 3) {
            break;
        }
    }

    fclose(f);
    return (found & 2) ? 0 : -1;
}

/*
 * Скидає біти звернення PTE через /proc/[pid]/clear_refs.
 */
static int clear_referenced_bits(pid_t pid) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/clear_refs", pid);

    FILE *f = fopen(path, "w");
    if (!f) {
        return -1;
    }

    if (fputs("1\n", f) == EOF) {
        fclose(f);
        return -1;
    }

    fclose(f);
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <pid> <вікно_сек>\n", argv[0]);
        return EXIT_FAILURE;
    }

    pid_t pid = (pid_t)atoi(argv[1]);
    int delta_sec = atoi(argv[2]);

    if (pid <= 0 || delta_sec <= 0) {
        fprintf(stderr, "Помилка: PID та інтервал мають бути додатними числами.\n");
        return EXIT_FAILURE;
    }

    printf("=== Інспекція робочої множини процесу PID=%d (вікно Δ=%d с) ===\n", pid, delta_sec);

    if (clear_referenced_bits(pid) != 0) {
        fprintf(stderr, "Помилка запису в /proc/%d/clear_refs: %s (потрібні права root або власника)\n",
                pid, strerror(errno));
        return EXIT_FAILURE;
    }

    printf("Біти звернення MMU скинуто. Збір статистики звернень протягом %d с...\n", delta_sec);
    sleep(delta_sec);

    unsigned long referenced_kb = 0;
    unsigned long rss_kb = 0;

    if (read_referenced_kb(pid, &referenced_kb, &rss_kb) != 0) {
        fprintf(stderr, "Помилка зчитування /proc/%d/smaps_rollup: %s\n", pid, strerror(errno));
        return EXIT_FAILURE;
    }

    double ws_ratio = (rss_kb > 0) ? ((double)referenced_kb / (double)rss_kb) * 100.0 : 0.0;

    printf("Загальний обсяг резидентної пам'яті (RSS): %lu kB\n", rss_kb);
    printf("Активна робоча множина W(t, Δ):           %lu kB\n", referenced_kb);
    printf("Частка активно використовуваної пам'яті:   %.2f%%\n", ws_ratio);

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <chrono>
#include <thread>
#include <filesystem>
#include <system_error>

namespace fs = std::filesystem;

struct ProcessMemoryStats {
    unsigned long rss_kb{0};
    unsigned long referenced_kb{0};
};

class WorkingSetInspector {
public:
    explicit WorkingSetInspector(pid_t pid) : pid_(pid) {
        proc_dir_ = "/proc/" + std::to_string(pid_);
        if (!fs::exists(proc_dir_)) {
            throw std::runtime_error("Процес із PID " + std::to_string(pid_) + " не існує.");
        }
    }

    void reset_accessed_bits() const {
        const std::string clear_refs_path = proc_dir_ + "/clear_refs";
        std::ofstream file(clear_refs_path);
        if (!file.is_open()) {
            throw std::system_error(errno, std::generic_category(),
                                   "Не вдалося відкрити " + clear_refs_path + " для запису");
        }
        file << "1\n";
        if (!file.good()) {
            throw std::runtime_error("Помилка під час скидання бітів у " + clear_refs_path);
        }
    }

    [[nodiscard]] ProcessMemoryStats sample_stats() const {
        const std::string smaps_path = proc_dir_ + "/smaps_rollup";
        std::ifstream file(smaps_path);
        if (!file.is_open()) {
            throw std::system_error(errno, std::generic_category(),
                                   "Не вдалося відкрити " + smaps_path);
        }

        ProcessMemoryStats stats{};
        std::string line;
        while (std::getline(file, line)) {
            if (line.starts_with("Rss:")) {
                std::istringstream iss(line.substr(4));
                iss >> stats.rss_kb;
            } else if (line.starts_with("Referenced:")) {
                std::istringstream iss(line.substr(11));
                iss >> stats.referenced_kb;
            }
        }
        return stats;
    }

    [[nodiscard]] pid_t pid() const noexcept { return pid_; }

private:
    pid_t pid_;
    std::string proc_dir_;
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <pid> <вікно_сек>\n";
        return 1;
    }

    try {
        const pid_t pid = std::stoi(argv[1]);
        const int delta_sec = std::stoi(argv[2]);

        if (pid <= 0 || delta_sec <= 0) {
            std::cerr << "Помилка: PID та вікно мають бути додатними значеннями.\n";
            return 1;
        }

        WorkingSetInspector inspector(pid);
        std::cout << "=== Інспекція робочої множини PID=" << pid
                  << " (вікно Δ=" << delta_sec << " с) ===\n";

        inspector.reset_accessed_bits();
        std::cout << "Біти звернення скинуто. Очікування спостереження...\n";

        std::this_thread::sleep_for(std::chrono::seconds(delta_sec));

        const auto stats = inspector.sample_stats();
        const double ws_ratio = (stats.rss_kb > 0)
            ? (static_cast<double>(stats.referenced_kb) / static_cast<double>(stats.rss_kb)) * 100.0
            : 0.0;

        std::cout << "Загальний обсяг резидентної пам'яті (RSS): " << stats.rss_kb << " kB\n";
        std::cout << "Активна робоча множина W(t, Δ):           " << stats.referenced_kb << " kB\n";
        std::cout << "Частка активної пам'яті:                   " << ws_ratio << " %\n";

    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
```
:::

## Інспекція резидентності сторінок діапазону через mincore()

Системний виклик `mincore()` приймає початкову адресу буфера, довжину в байтах та масив байтів результату `vec`. Для кожної сторінки розміром 4096 байт ядро встановлює наймолодший біт (`vec[i] & 1`), якщо відповідний кадр наразі знаходиться у фізичній оперативній пам'яті.

Цей виклик є незамінним для інспекції файлових відображень (`mmap`). Наприклад, коли база даних відкриває великий файл таблиці обсягом 100 ГБ, `mincore()` дозволяє дізнатися, яка саме частина цього файлу наразі закешована в оперативній пам'яті без зчитування вмісту.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/mman.h>
#include <string.h>
#include <errno.h>

#define PAGE_SIZE 4096

/*
 * Демонстрація аналізу резидентності виділеного діапазону віртуальної пам'яті.
 */
int main(void) {
    const size_t num_pages = 16;
    const size_t alloc_size = num_pages * PAGE_SIZE;

    /* Виділяємо анонімну пам'ять (ліниве виділення, сторінки ще не існують у RAM) */
    char *buffer = (char *)mmap(NULL, alloc_size, PROT_READ | PROT_WRITE,
                                MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (buffer == MAP_FAILED) {
        perror("mmap failed");
        return EXIT_FAILURE;
    }

    unsigned char vec[num_pages];
    memset(vec, 0, sizeof(vec));

    printf("=== Перевірка резидентності сторінок через mincore() ===\n");

    /* 1. Стан одразу після mmap */
    if (mincore(buffer, alloc_size, vec) != 0) {
        perror("mincore failed");
        munmap(buffer, alloc_size);
        return EXIT_FAILURE;
    }

    size_t resident_initial = 0;
    for (size_t i = 0; i < num_pages; ++i) {
        if (vec[i] & 1) resident_initial++;
    }
    printf("1. Одразу після mmap(): у RAM перебуває %zu з %zu сторінок\n",
           resident_initial, num_pages);

    /* 2. Торкаємося лише парних сторінок (формуємо штучну робочу множину) */
    for (size_t i = 0; i < num_pages; i += 2) {
        buffer[i * PAGE_SIZE] = (char)(i + 1); /* Сторінковий збій ініціалізує кадр */
    }

    memset(vec, 0, sizeof(vec));
    if (mincore(buffer, alloc_size, vec) != 0) {
        perror("mincore failed");
        munmap(buffer, alloc_size);
        return EXIT_FAILURE;
    }

    printf("2. Після звернення до парних сторінок:\n   ");
    size_t resident_active = 0;
    for (size_t i = 0; i < num_pages; ++i) {
        int in_ram = vec[i] & 1;
        if (in_ram) resident_active++;
        printf("P%zu:%s ", i, in_ram ? "[RAM]" : "[---]");
    }
    printf("\n   Всього в активній робочій множині RAM: %zu сторінок (%zu kB)\n",
           resident_active, (resident_active * PAGE_SIZE) / 1024);

    munmap(buffer, alloc_size);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <string>
#include <span>
#include <sys/mman.h>
#include <unistd.h>
#include <system_error>

class MmapRegion {
public:
    explicit MmapRegion(size_t size) : size_(size) {
        void* ptr = ::mmap(nullptr, size_, PROT_READ | PROT_WRITE,
                           MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (ptr == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "mmap failed");
        }
        addr_ = static_cast<std::byte*>(ptr);
    }

    ~MmapRegion() noexcept {
        if (addr_ != nullptr) {
            ::munmap(addr_, size_);
        }
    }

    MmapRegion(const MmapRegion&) = delete;
    MmapRegion& operator=(const MmapRegion&) = delete;
    MmapRegion(MmapRegion&& other) noexcept : addr_(other.addr_), size_(other.size_) {
        other.addr_ = nullptr;
        other.size_ = 0;
    }
    MmapRegion& operator=(MmapRegion&& other) noexcept {
        if (this != &other) {
            if (addr_ != nullptr) ::munmap(addr_, size_);
            addr_ = other.addr_;
            size_ = other.size_;
            other.addr_ = nullptr;
            other.size_ = 0;
        }
        return *this;
    }

    [[nodiscard]] std::byte* data() noexcept { return addr_; }
    [[nodiscard]] size_t size() const noexcept { return size_; }

    [[nodiscard]] std::vector<unsigned char> query_residency(size_t page_size = 4096) const {
        const size_t num_pages = (size_ + page_size - 1) / page_size;
        std::vector<unsigned char> vec(num_pages, 0);
        if (::mincore(addr_, size_, vec.data()) != 0) {
            throw std::system_error(errno, std::generic_category(), "mincore failed");
        }
        return vec;
    }

private:
    std::byte* addr_{nullptr};
    size_t size_{0};
};

int main() {
    constexpr size_t page_size = 4096;
    constexpr size_t num_pages = 16;
    constexpr size_t alloc_size = num_pages * page_size;

    try {
        MmapRegion region(alloc_size);
        std::cout << "=== Перевірка резидентності сторінок через C++ RAII та mincore() ===\n";

        auto vec_initial = region.query_residency(page_size);
        size_t initial_count = 0;
        for (auto b : vec_initial) {
            if (b & 1) ++initial_count;
        }
        std::cout << "1. Після алокації: " << initial_count << " з " << num_pages << " сторінок у RAM\n";

        /* Звертаємося до парних сторінок */
        std::byte* raw = region.data();
        for (size_t i = 0; i < num_pages; i += 2) {
            raw[i * page_size] = static_cast<std::byte>(i + 1);
        }

        auto vec_active = region.query_residency(page_size);
        size_t active_count = 0;
        std::cout << "2. Карта сторінок після часткового доступу:\n   ";
        for (size_t i = 0; i < vec_active.size(); ++i) {
            bool in_ram = (vec_active[i] & 1) != 0;
            if (in_ram) ++active_count;
            std::cout << "P" << i << ":" << (in_ram ? "[RAM]" : "[---]") << " ";
        }
        std::cout << "\n   Активна робоча множина: " << active_count << " сторінок ("
                  << (active_count * page_size) / 1024 << " kB)\n";

    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
```
:::

## Детальний аналіз сторінок через /proc/[pid]/pagemap

Файл `/proc/[pid]/pagemap` містить 64-бітне значення для кожної віртуальної сторінки процесу. Зсув у файлі обчислюється як:

```
offset = (virtual_address / PAGE_SIZE) * sizeof(uint64_t)
```

Структура 64-бітного запису:
- **Біт 63 (`Page Present`):** Сторінка відображена у фізичний кадр оперативної пам'яті (RAM).
- **Біт 62 (`Page Swapped`):** Сторінка витіснена у простір підкачки (swap).
- **Біт 55 (`Soft-dirty`):** Сторінка була модифікована після останнього скидання трекера.
- **Біти 0–54 (`Page Frame Number`):** Фізичний номер сторінки в оперативній пам'яті (доступний для читання процесам із привілеєм `CAP_SYS_ADMIN`).

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

#define PAGE_SIZE 4096

/*
 * Зчитує статус віртуальної сторінки з /proc/[pid]/pagemap.
 */
int inspect_pagemap_entry(pid_t pid, uintptr_t vaddr, uint64_t *entry) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/pagemap", pid);

    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        return -1;
    }

    off_t offset = (off_t)((vaddr / PAGE_SIZE) * sizeof(uint64_t));
    if (lseek(fd, offset, SEEK_SET) == (off_t)-1) {
        close(fd);
        return -1;
    }

    ssize_t bytes_read = read(fd, entry, sizeof(uint64_t));
    close(fd);

    return (bytes_read == sizeof(uint64_t)) ? 0 : -1;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <pid> <hex_vaddr>\n", argv[0]);
        return EXIT_FAILURE;
    }

    pid_t pid = (pid_t)atoi(argv[1]);
    uintptr_t vaddr = (uintptr_t)strtoull(argv[2], NULL, 16);

    uint64_t entry = 0;
    if (inspect_pagemap_entry(pid, vaddr, &entry) != 0) {
        perror("inspect_pagemap_entry failed");
        return EXIT_FAILURE;
    }

    int present = (entry >> 63) & 1;
    int swapped = (entry >> 62) & 1;
    uint64_t pfn = entry & ((1ULL << 55) - 1);

    printf("=== Інспекція pagemap для PID=%d адреса=0x%lx ===\n", pid, vaddr);
    printf("Присутня у RAM (Present): %s\n", present ? "ТАК" : "НІ");
    printf("У свопі (Swapped):        %s\n", swapped ? "ТАК" : "НІ");
    if (present) {
        printf("Фізичний номер кадру PFN: 0x%lx (Фізична адреса: 0x%lx)\n", pfn, pfn * PAGE_SIZE);
    }

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <cstdint>
#include <string>
#include <iomanip>
#include <system_error>

class PagemapReader {
public:
    explicit PagemapReader(pid_t pid) {
        path_ = "/proc/" + std::to_string(pid) + "/pagemap";
    }

    [[nodiscard]] uint64_t read_entry(uintptr_t virtual_address, size_t page_size = 4096) const {
        std::ifstream file(path_, std::ios::binary);
        if (!file.is_open()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити " + path_);
        }

        const auto offset = static_cast<std::streamoff>((virtual_address / page_size) * sizeof(uint64_t));
        file.seekg(offset);
        if (!file.good()) {
            throw std::runtime_error("Помилка позиціонування lseek у pagemap");
        }

        uint64_t entry{0};
        file.read(reinterpret_cast<char*>(&entry), sizeof(entry));
        if (file.gcount() != sizeof(entry)) {
            throw std::runtime_error("Не вдалося зчитати повний 64-бітний запис pagemap");
        }
        return entry;
    }

private:
    std::string path_;
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <pid> <hex_vaddr>\n";
        return 1;
    }

    try {
        const pid_t pid = std::stoi(argv[1]);
        const uintptr_t vaddr = std::stoull(argv[2], nullptr, 16);

        PagemapReader reader(pid);
        const uint64_t entry = reader.read_entry(vaddr);

        const bool present = ((entry >> 63) & 1) != 0;
        const bool swapped = ((entry >> 62) & 1) != 0;
        const uint64_t pfn = entry & ((1ULL << 55) - 1);

        std::cout << "=== Pagemap інспекція PID=" << pid << " Адреса=0x"
                  << std::hex << vaddr << std::dec << " ===\n";
        std::cout << "Присутня у RAM: " << (present ? "ТАК" : "НІ") << "\n";
        std::cout << "У свопі:        " << (swapped ? "ТАК" : "НІ") << "\n";
        if (present) {
            std::cout << "Фізичний PFN:   0x" << std::hex << pfn
                      << " (Фізична адреса: 0x" << (pfn * 4096) << ")" << std::dec << "\n";
        }

    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
```
:::

## Інваріанти та крайові випадки інспекції

1. **Багатопотоковість та атомарність:** Скидання бітів `clear_refs` впливає на всі потоки процесу одночасно, оскільки вони поділяють спільну структуру `mm_struct` та таблиці сторінок. Отримане значення `Referenced` показує об'єднання робочих множин усіх активних ниток виконання.
2. **Накладні витрати інспекції:** Запис у `clear_refs` вимагає проходу ядра по всіх записах VMA та блокування блокувань таблиць сторінок (`page_table_lock`), а також ініціює міжпроцесорні переривання (IPI) для скидання локальних кешів TLB на всіх ядрах процесора. Тому скидання `clear_refs` не слід виконувати з надто високою частотою (наприклад, сотні разів на секунду), щоб не створювати штучного сповільнення процесу.
3. **Спільні сторінки та пам'ять тільки для читання:** Якщо кілька процесів одночасно використовують спільну бібліотеку, звернення до її коду будь-яким процесом призведе до встановлення біта `Accessed` у спільній сторінці. Для ізоляції власної робочої множини конкретного процесу слід аналізувати метрику `Pss` (Proportional Set Size) або зосереджуватися на приватних анонімних регіонах пам'яті.

## Практичне застосування результатів у профілюванні систем

Вимірювання робочої множини через наведені інструменти вирішує кілька ключових завдань оптимізації сучасних серверних середовищ:

- **Калібрування лімітів пам'яті контейнерів (Memory cgroups):** Часто розробники встановлюють ліміт `memory.max` контейнера на рівні пікового споживання віртуального простору (VSS) або повного резидентного набору (RSS). Проте, якщо сервіс тримає в пам'яті 8 ГБ даних, а його активна робоча множина за 10-секундне вікно становить лише 1.2 ГБ, виділення контейнеру 2 ГБ RAM із увімкненим свопом дозволить безпечно розмістити у 4 рази більше мікросервісів на тому самому фізичному сервері без жодної втрати затримок (latency SLO).
- **Діагностика прихованого трішингу:** Якщо метрики показують, що `RSS` процесу залишається сталим, але час відповіді системи зростає на порядки, замір `Referenced` зіставити з лічильниками сторінкових збоїв `majflt` у `/proc/[pid]/stat`. Якщо значення `Referenced` близьке до `RSS`, але `majflt` стрімко наростає, це пряма ознака того, що робоча множина виходить за межі виділених процесу фізичних кадрів і ядро безперервно витісняє та підкачує активні дані.
- **Оцінка ефективності структур даних:** Порівняння розміру робочої множини для геш-таблиці та B-дерева на однакових обсягах даних наочно демонструє перевагу просторової локальності. B-дерево групує ключі у неперервні сторінки, утримуючи малий розмір `W(t, Δ)`, тоді як випадковий доступ геш-таблиці примушує ядро тримати в RAM практично весь обсяг алокації, спричиняючи деградацію продуктивності на великих масштабах.
