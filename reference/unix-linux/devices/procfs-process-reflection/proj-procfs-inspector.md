# ⚙️ Практичний інспектор процесів через procfs: безпечний розбір та отримання метрик

Розробка надійних інструментів моніторингу, діагностики та інтроспекції процесів у Linux вимагає коректної взаємодії з псевдофайловою системою `/proc`. Незважаючи на уявну простоту текстового файлового інтерфейсу, пряме зчитування даних із `/proc/[pid]/` приховує низку інженерних пасток, здатних призвести до збоїв парсингу, утекликів файлових дескрипторів або помилкової інтерпретації параметрів системи.

Ця вставка розкриває підводні камені практичної взаємодії з `/proc/[pid]/`, аналізує стан перегонів (race conditions) при зчитуванні метрик і надає повний, безпечний код інспектора процесів мовами C та C++.

## 1. Інженерні підводні камені розбору /proc/[pid]/

При створенні продакшн-парсерів `/proc` розробники зіштовхуються з трьома основними проблемами: обробкою нестандартних імен процесів, обробкою бінарних нуль-байтів та асинхронним зникненням процесів.

### Проблема 1: Обробка складних імен у /proc/[pid]/stat
Найбільш підступною помилкою є розбір файлу `/proc/[pid]/stat`. Друге поле цього файлу (`comm`) містить назву бінарного файлу процесу, обмежену круглими дужками. Згідно зі специфікацією ядра Linux, процес може змінити власну назву викликом `prctl(PR_SET_NAME)` або завантажити бінарник, шлях чи ім'я якого містить пробіли та дужки — наприклад, `(sd-pam)` або навіть `(app (worker thread) v2)`.

Якщо код розбирає рядок наївно через `sscanf(buf, "%d %s %c ...")` або за допомогою `strtok(buf, " ")`, він розіб'є ім'я `(app (worker thread) v2)` на кілька окремих слів. У результаті пробіл усередині імені змістить номери всіх наступних 50 полів:
- Замість однобуквеного стану `state` (#3) код прочитає слово `(worker`;
- Замість `ppid` (#4) код прочитає слово `thread)`;
- Процесорний час `utime` та розмір пам'яті `vsize` отримають повністю сміттєві значення.

**Інженерне рішення:** Надійний алгоритм розбору вимагає двопрохідного пошуку межі `comm`:
1. Знайти першу відкриваючу дужку `(` від початку рядка за допомогою `strchr()` (в C) або `find('(')` (в C++) — це початок поля `comm`.
2. Знайти **останню** закриваючу дужку `)` від кінця рядка за допомогою `strrchr()` (в C) або `rfind(')')` (в C++) — це кінець поля `comm`.
3. Усе, що лежить між першою `(` та останньою `)` — це ім'я `comm`. Усі наступні поля (починаючи з #3 `state`) розбираються з залишкового рядка після останньої закриваючої дужки `)`.

### Проблема 2: Обробка бінарних нуль-байтів у /proc/[pid]/cmdline
Файл `cmdline` містить масив аргументів командного рядка `argv`. На відміну від звичайних текстових файлів, аргументи у `cmdline` розділені нуль-байтами (`\0`), а не пробілами чи символами нового рядка.

Якщо програма спробує прочитати `cmdline` через стандартний виклик `fgets()` або `printf("%s")`, мова C зупинить обробку рядка на першому ж нуль-байті, показавши лише назву бінарника `argv[0]` і втративши всі наступні аргументи `argv[1] ... argv[n]`.

**Інженерне рішення:** Файл слід зчитувати у сирий байтовий буфер викликами `fread()` або `read()`, орієнтуючись на повернутий розмір у байтах, після чого замінювати всі внутрішні символи `\0` на пробіли, зберігаючи лише останній завершальний нуль-байт. Особливим крайовим випадком є ядерні потоки (kernel threads, такі як `[kthreadd]` чи `[kworker/0:1]`): для них файл `cmdline` має розмір 0 байтів.

### Проблема 3: Стан перегонів та асинхронне зникнення процесу
У багатозадачній системі процес може завершити виконання у будь-який момент між викликами `readdir()` для директорії `/proc` та спробою відкрити файл `/proc/[pid]/status`.

Якщо процес помер у цей проміжок часу, системні виклики `open()` повернуть помилку `ENOENT` (No such file or directory). Високонадійний парсер зобов'язаний обробляти `ENOENT` як штатну ситуацію (завершення життя процесу), а не як критичний збій системи.

---

## 2. Практична реалізація інспектора процесів

Нижче наведено робочі реалізації консольного інспектора процесів мовами C та C++. Інспектор виконує наступні завдання:
- Зчитує та безпечно розбирає `stat` з урахуванням складних імен у дужках;
- Прочитує повний командний рядок з `cmdline` із заміною нуль-байтів;
- Сканує магічні символьні посилання у `/proc/[pid]/fd/` за допомогою `readlink()`, виявляючи відкриті файли, сокети та видалені ресурси.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dirent.h>
#include <sys/types.h>
#include <limits.h>

// Структура для збереження метрик процесу
typedef struct {
    pid_t pid;
    char comm[256];
    char state;
    pid_t ppid;
    unsigned long utime;
    unsigned long stime;
    long num_threads;
    unsigned long vsize;
    long rss_pages;
} process_stat_t;

// Безпечний розбір /proc/[pid]/stat
int read_process_stat(pid_t pid, process_stat_t *info) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/stat", pid);

    FILE *f = fopen(path, "r");
    if (!f) return -1; // Процес міг завершитися (ENOENT)

    char buf[2048];
    if (!fgets(buf, sizeof(buf), f)) {
        fclose(f);
        return -1;
    }
    fclose(f);

    // Двопрохідний пошук: перша '(' та остання ')'
    char *first_paren = strchr(buf, '(');
    char *last_paren = strrchr(buf, ')');

    if (!first_paren || !last_paren || first_paren >= last_paren) {
        return -1; // Пошкоджений рядок stat
    }

    // Зчитуємо PID до першої дужки
    info->pid = (pid_t)atoi(buf);

    // Безпечно копіюємо comm всередині дужок
    size_t comm_len = last_paren - (first_paren + 1);
    if (comm_len >= sizeof(info->comm)) comm_len = sizeof(info->comm) - 1;
    strncpy(info->comm, first_paren + 1, comm_len);
    info->comm[comm_len] = '\0';

    // Розбираємо поля після останньої закриваючої дужки
    // Поле після ')' — це state (#3), далі ppid (#4) тощо.
    char *rest = last_paren + 2; // Пропускаємо ") "
    int assigned = sscanf(rest,
        "%c %d %*d %*d %*d %*d %*u %*u %*u %*u %*u %lu %lu %*d %*d %*d %*d %ld %*d %*u %*lu %lu %ld",
        &info->state,
        &info->ppid,
        &info->utime,
        &info->stime,
        &info->num_threads,
        &info->vsize,
        &info->rss_pages);

    return (assigned == 7) ? 0 : -1;
}

// Читання командного рядка з нуль-байтами
void print_process_cmdline(pid_t pid) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/cmdline", pid);

    FILE *f = fopen(path, "rb");
    if (!f) return;

    char buf[1024];
    size_t n = fread(buf, 1, sizeof(buf) - 1, f);
    fclose(f);

    if (n == 0) {
        printf("Cmdline: [ядерний потік або порожньо]\n");
        return;
    }

    // Замінюємо внутрішні нуль-байти на пробіли для виводу
    for (size_t i = 0; i < n - 1; i++) {
        if (buf[i] == '\0') buf[i] = ' ';
    }
    buf[n] = '\0';
    printf("Cmdline: %s\n", buf);
}

// Інспекція відкритих файлових дескрипторів
void inspect_process_fds(pid_t pid) {
    char dirpath[64];
    snprintf(dirpath, sizeof(dirpath), "/proc/%d/fd", pid);

    DIR *d = opendir(dirpath);
    if (!d) return;

    printf("Відкриті дескриптори /proc/%d/fd:\n", pid);
    struct dirent *dir;
    int count = 0;
    while ((dir = readdir(d)) != NULL) {
        if (dir->d_name[0] == '.') continue;

        char linkpath[PATH_MAX];
        char targetpath[PATH_MAX];
        snprintf(linkpath, sizeof(linkpath), "%s/%s", dirpath, dir->d_name);

        // readlink() повертає ціль магічного посилання без нуль-байта в кінці
        ssize_t len = readlink(linkpath, targetpath, sizeof(targetpath) - 1);
        if (len != -1) {
            targetpath[len] = '\0';
            printf("  fd %s -> %s\n", dir->d_name, targetpath);
            count++;
        }
        if (count >= 5) { // Обмежуємо вивід першими 5 для лаконічності
            printf("  ... (показано перші 5)\n");
            break;
        }
    }
    closedir(d);
}

int main() {
    pid_t my_pid = getpid();
    process_stat_t stat_info;

    printf("=== Інспекція поточного процесу (PID: %d) ===\n", my_pid);

    if (read_process_stat(my_pid, &stat_info) == 0) {
        printf("Comm:    %s\n", stat_info.comm);
        printf("State:   %c\n", stat_info.state);
        printf("PPID:    %d\n", stat_info.ppid);
        printf("Threads: %ld\n", stat_info.num_threads);
        printf("VSize:   %lu KB\n", stat_info.vsize / 1024);
        printf("RSS:     %ld сторінок\n", stat_info.rss_pages);
    } else {
        fprintf(stderr, "Помилка зчитування stat\n");
    }

    print_process_cmdline(my_pid);
    inspect_process_fds(my_pid);

    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <filesystem>
#include <system_error>
#include <cstdio>
#include <unistd.h>

namespace fs = std::filesystem;

struct ProcessMetrics {
    pid_t pid{0};
    std::string comm;
    char state{'?'};
    pid_t ppid{0};
    unsigned long utime{0};
    unsigned long stime{0};
    long num_threads{0};
    unsigned long vsize{0};
    long rss_pages{0};
};

class ProcfsInspector {
public:
    // Безпечний розбір /proc/[pid]/stat через string_view та rfind
    static std::optional<ProcessMetrics> readStat(pid_t pid) {
        const std::string path = "/proc/" + std::to_string(pid) + "/stat";
        std::ifstream file(path);
        if (!file.is_open()) return std::nullopt;

        std::string content;
        std::getline(file, content);
        if (content.empty()) return std::nullopt;

        const size_t first_paren = content.find('(');
        const size_t last_paren = content.rfind(')');

        if (first_paren == std::string::npos || last_paren == std::string::npos || first_paren >= last_paren) {
            return std::nullopt;
        }

        ProcessMetrics metrics;
        metrics.pid = std::stoi(content.substr(0, first_paren));
        metrics.comm = content.substr(first_paren + 1, last_paren - first_paren - 1);

        // Парсимо залишок рядка після останньої закриваючої дужки
        std::string_view rest(content.data() + last_paren + 2, content.size() - last_paren - 2);
        
        // Розбираємо параметри після ')'
        int assigned = ::sscanf(rest.data(),
            "%c %d %*d %*d %*d %*d %*u %*u %*u %*u %*u %lu %lu %*d %*d %*d %*d %ld %*d %*u %*lu %lu %ld",
            &metrics.state,
            &metrics.ppid,
            &metrics.utime,
            &metrics.stime,
            &metrics.num_threads,
            &metrics.vsize,
            &metrics.rss_pages);

        if (assigned != 7) return std::nullopt;
        return metrics;
    }

    // Читання командного рядка із заміною нуль-байтів
    static std::string readCmdline(pid_t pid) {
        const std::string path = "/proc/" + std::to_string(pid) + "/cmdline";
        std::ifstream file(path, std::ios::binary);
        if (!file.is_open()) return "";

        std::string cmdline((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
        if (cmdline.empty()) return "[ядерний потік або порожньо]";

        for (size_t i = 0; i < cmdline.size() - 1; ++i) {
            if (cmdline[i] == '\0') cmdline[i] = ' ';
        }
        return cmdline;
    }

    // Перегляд відкритих файлових дескрипторів через std::filesystem
    static std::vector<std::pair<std::string, std::string>> inspectFds(pid_t pid, size_t limit = 5) {
        std::vector<std::pair<std::string, std::string>> result;
        const std::string fd_dir = "/proc/" + std::to_string(pid) + "/fd";

        std::error_code ec;
        if (!fs::exists(fd_dir, ec)) return result;

        size_t count = 0;
        for (const auto& entry : fs::directory_iterator(fd_dir, ec)) {
            if (ec) break;
            
            std::error_code read_ec;
            auto target = fs::read_symlink(entry.path(), read_ec);
            if (!read_ec) {
                result.emplace_back(entry.path().filename().string(), target.string());
                if (++count >= limit) break;
            }
        }
        return result;
    }
};

int main() {
    pid_t pid = ::getpid();
    std::cout << "=== C++ Інспектор процесу (PID: " << pid << ") ===\n";

    if (auto metrics = ProcfsInspector::readStat(pid)) {
        std::cout << "Comm:    " << metrics->comm << "\n";
        std::cout << "State:   " << metrics->state << "\n";
        std::cout << "PPID:    " << metrics->ppid << "\n";
        std::cout << "Threads: " << metrics->num_threads << "\n";
        std::cout << "VSize:   " << (metrics->vsize / 1024) << " KB\n";
        std::cout << "RSS:     " << metrics->rss_pages << " сторінок\n";
    } else {
        std::cerr << "Помилка розбору /proc/PID/stat\n";
    }

    std::cout << "Cmdline: " << ProcfsInspector::readCmdline(pid) << "\n";

    std::cout << "Відкриті дескриптори:\n";
    for (const auto& [fd, target] : ProcfsInspector::inspectFds(pid)) {
        std::cout << "  fd " << fd << " -> " << target << "\n";
    }

    return 0;
}
```
:::

---

## 3. Оптимізація продуктивності та високонавантажені монітори

При створенні високонавантажених серверних моніторів (наприклад, утиліт масового збору метрик для тисяч контейнерів) сканування всієї `/proc` кожні кілька секунд може створювати відчутні накладні витрати на системні виклики та процесорний час.

Для оптимізації парсингу застосовуються наступні системні прийоми:
1. **Перевикористання файлових дескрипторів:** Замість постійного відкриття та закриття файлів викликами `open()`/`close()`, демон може відкрити дескриптори на довгоживучі файли `/proc/[pid]/stat` та виконувати `lseek(fd, 0, SEEK_SET)` перед кожним новим повторним читанням викликом `read()`. Це економить виклики пошуку dentry в VFS.
2. **Використання openat() для захисту від перегонів:** При скануванні директорій `/proc/[pid]/fd/` спочатку відкривається дескриптор директорії `dirfd = open("/proc/[pid]/fd", O_RDONLY | O_DIRECTORY)`, після чого читання символьних посилань виконується через `readlinkat(dirfd, filename, ...)` замість конкатенації текстових шляхів.
3. **Обмеження зчитування `smaps`:** Читання файлу `/proc/[pid]/smaps` вимагає від ядра обходу всього дерева VMA та таблиць сторінок процесу під затиснутим `mm->mmap_lock`. Масове зчитування `smaps` для великих процесів (наприклад бази даних із сотнями гігабайтів RAM) може спричинити затримки виконання самого процесу (mmap_lock contention). Для регулярного моніторингу рекомендується використовувати поверхневі файли `statm` або `status`.
