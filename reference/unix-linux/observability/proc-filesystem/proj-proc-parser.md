# ⚙️ Парсер procfs у користувацькому просторі

Створення надійного користувацького парсера віртуальної файлової системи `procfs` мовами C та C++ вимагає точного розбору її текстових форматів, таких як файли спостережуваності `/proc/[pid]/stat` та `/proc/[pid]/maps`. Побудова такого інструментарію охоплює безпечну роботу з буферами пам'яті, обробку складних крайових випадків (зокрема пробілів та дужок у назвах процесів), переведення сирих числових лічильників ядра у фізичні одиниці вимірювання та інспектування системних викликів за допомогою трасувальника `strace`.

---

## 1. Аналіз підводних каменів при парсингу `/proc/[pid]/stat`

Більшість системних утиліт та бібліотек моніторингу стикаються з критичною помилкою при спробі розбору файла `/proc/[pid]/stat` за допомогою стандартних функцій форматованого зчитування на кшталт `fscanf(fp, "%d %s %c ...")` чи `std::stringstream`.

Справа у тому, що поле №2 `comm` містить ім'я виконуваного файлу процесу, яке ядро Linux огортає в круглі дужки. Згідно зі специфікацією POSIX та реалізацією виклику `prctl(PR_SET_NAME)`, процес має право встановити собі будь-яку назву довжиною до 16 символів. Ця назва може містити довільні символи ASCII, у тому числі пробіли, табуляції та закриваючі круглі дужки `)`:

```text
12345 (sd-pam) S 1 12345 12345 0 -1 4194304 120 0 0 0 15 5 0 0 20 0 1 0 123456 41943040 1000 ...
12346 (my_app ) test) S 1 12346 12346 0 -1 4194304 ...
```

Якщо викликати звичайний `sscanf()` із форматичним рядком `%s` для поля `comm`, пробіл всередині `(my_app ) test)` призведе до того, що парсер сприйме першу частину `(my_app` як назву процесу, другу частину `)` як стан процесу `state`, а наступні числові токени зсунуться на кілька позицій ліворуч. В результаті програма зчитає сміттєві значення для CPU-часу `utime`/`stime`, віртуальної пам'яті `vsize` та сторінок `rss`, або завершиться з помилкою парсингу.

### Алгоритм безпечного розбору рядка

Щоб гарантувати абсолютну стійкість до будь-яких назв процесів, використовують двопрохідний алгоритм на основі пошуку меж:

1. **Зчитування повного рядка**: Файл `/proc/[pid]/stat` зчитується повністю за один системний виклик `read()` або `fgets()` у локальний буфер достатнього розміру (щонайменше 1024-2048 байт).
2. **Пошук першої дужки**: За допомогою функції `strchr()` (або `std::string::find`) знаходиться перша відкриваюча дужка `(`, яка відсікає ідентифікатор `PID` ліворуч від неї.
3. **Пошук найостаннішої дужки**: За допомогою функції `strrchr()` (або `std::string::rfind`) знаходиться **найкрайніша права** закриваюча дужка `)` у рядку. Усі дужки всередині назви вважаються частиною поля `comm`.
4. **Витягнення поля comm**: Текст між знайденими позиціями `(` та `)` копіюється в окремий буфер і термінується нулем.
5. **Розбір залишку рядка**: Вказувач зсувається за останню дужку `)`, звідки функцією `sscanf()` зчитуються решта 50 числових полів.

---

## 2. Конвертація одиниць вимірювання ядра

Числові дані у `/proc/[pid]/stat` наводяться у внутрішніх одиницях ядра, які необхідно перевести у звичні для людини секунди та байти:

1. **Конвертація CPU-часу у секунди**:
   Поля `utime` та `stime` вимірюються у тиках системного годинника (`clock ticks`). Для переведення їх у секунди необхідно дізнатися кількість тиків на секунду за допомогою системного виклику `sysconf(_SC_CLK_TCK)` (зазвичай це значення дорівнює 100 у Linux):
   ```
   user_seconds = utime / sysconf(_SC_CLK_TCK)
   ```
2. **Конвертація пам'яті RSS у байти**:
   Поле `rss` містить кількість фізичних сторінок пам'яті. Для переведення у байти або мегабайти це значення множиться на розмір сторінки пам'яті, зчитаний через `sysconf(_SC_PAGESIZE)` або `getpagesize()` (зазвичай 4096 байт):
   ```
   rss_bytes = rss · sysconf(_SC_PAGESIZE)
   ```

---

## 3. Паралельні реалізації мовами C та C++

У наведених нижче прикладах показано повну реалізацію парсера. Вкладка C використовує низькорівневі маніпуляції з вказівниками та буферами пам'яті, а вкладка C++ застосовує концепцію RAII (`std::ifstream`), безпечні строкові обгортки (`std::string_view`), типи обробки помилок (`std::optional`) та сучасні стандарти безпеки.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <unistd.h>
#include <errno.h>

typedef struct {
    int pid;
    char comm[256];
    char state;
    int ppid;
    unsigned long utime;
    unsigned long stime;
    double utime_sec;
    double stime_sec;
    unsigned long vsize;
    long rss_pages;
    unsigned long long rss_bytes;
} proc_stat_t;

bool parse_proc_stat(const char *filepath, proc_stat_t *out_stat) {
    if (!filepath || !out_stat) return false;

    FILE *fp = fopen(filepath, "r");
    if (!fp) {
        perror("Помилка відкриття файлу proc stat");
        return false;
    }

    char buffer[2048];
    if (!fgets(buffer, sizeof(buffer), fp)) {
        fclose(fp);
        return false;
    }
    fclose(fp);

    // 1. Знаходимо першу відкриваючу дужку '(' та останню закриваючу ')'
    char *open_paren = strchr(buffer, '(');
    char *close_paren = strrchr(buffer, ')');

    if (!open_paren || !close_paren || close_paren <= open_paren) {
        return false;
    }

    // 2. Зчитуємо PID до першої дужки
    out_stat->pid = atoi(buffer);

    // 3. Зчитуємо comm між '(' та ')'
    size_t comm_len = close_paren - (open_paren + 1);
    if (comm_len >= sizeof(out_stat->comm)) {
        comm_len = sizeof(out_stat->comm) - 1;
    }
    strncpy(out_stat->comm, open_paren + 1, comm_len);
    out_stat->comm[comm_len] = '\0';

    // 4. Зчитуємо решту полів після останньої дужки ')'
    char *after_comm = close_paren + 1;

    int parsed = sscanf(after_comm,
                        " %c %d %*d %*d %*d %*d %*u %*u %*u %*u %*u %lu %lu %*d %*d %*d %*d %*d %*d %*llu %lu %ld",
                        &out_stat->state,
                        &out_stat->ppid,
                        &out_stat->utime,
                        &out_stat->stime,
                        &out_stat->vsize,
                        &out_stat->rss_pages);

    if (parsed != 6) {
        return false;
    }

    // 5. Конвертуємо тики годинника у секунди та сторінки у байти
    long clock_ticks = sysconf(_SC_CLK_TCK);
    if (clock_ticks <= 0) clock_ticks = 100;

    long page_size = sysconf(_SC_PAGESIZE);
    if (page_size <= 0) page_size = 4096;

    out_stat->utime_sec = (double)out_stat->utime / clock_ticks;
    out_stat->stime_sec = (double)out_stat->stime / clock_ticks;
    out_stat->rss_bytes = (unsigned long long)out_stat->rss_pages * page_size;

    return true;
}

int main(void) {
    proc_stat_t st;
    if (parse_proc_stat("/proc/self/stat", &st)) {
        printf("--- Результат розбору /proc/self/stat (C) ---\n");
        printf("PID:               %d\n", st.pid);
        printf("Comm:              %s\n", st.comm);
        printf("State:             %c\n", st.state);
        printf("PPID:              %d\n", st.ppid);
        printf("User Time:         %.2f sec (%lu ticks)\n", st.utime_sec, st.utime);
        printf("System Time:       %.2f sec (%lu ticks)\n", st.stime_sec, st.stime);
        printf("Virtual Memory:    %.2f MB (%lu bytes)\n", (double)st.vsize / (1024 * 1024), st.vsize);
        printf("RSS Memory:        %.2f MB (%llu bytes)\n", (double)st.rss_bytes / (1024 * 1024), st.rss_bytes);
    } else {
        fprintf(stderr, "Помилка парсингу /proc/self/stat\n");
        return 1;
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <optional>
#include <sstream>
#include <filesystem>
#include <unistd.h>

struct ProcessStat {
    int pid{0};
    std::string comm;
    char state{'?'};
    int ppid{0};
    unsigned long utime{0};
    unsigned long stime{0};
    double utimeSec{0.0};
    double stimeSec{0.0};
    unsigned long vsize{0};
    long rssPages{0};
    unsigned long long rssBytes{0};
};

class ProcStatParser {
public:
    static std::optional<ProcessStat> parseFile(const std::filesystem::path& statPath) {
        std::ifstream file(statPath);
        if (!file.is_open()) {
            return std::nullopt;
        }

        std::string line;
        if (!std::getline(file, line)) {
            return std::nullopt;
        }

        const auto openParen = line.find('(');
        const auto closeParen = line.rfind(')');

        if (openParen == std::string::npos || closeParen == std::string::npos || closeParen <= openParen) {
            return std::nullopt;
        }

        ProcessStat result;
        
        try {
            result.pid = std::stoi(line.substr(0, openParen));
        } catch (const std::exception&) {
            return std::nullopt;
        }

        result.comm = line.substr(openParen + 1, closeParen - openParen - 1);

        std::string_view rest(line.data() + closeParen + 1, line.size() - closeParen - 1);
        std::istringstream iss{std::string(rest)};

        // Пропускаємо 7 неуживаних полів ядра
        unsigned long minflt, cminflt, majflt, cmajflt;
        int pgrp, session, tty_nr, tpgid;
        unsigned int flags;

        if (!(iss >> result.state >> result.ppid >> pgrp >> session >> tty_nr >> tpgid 
                  >> flags >> minflt >> cminflt >> majflt >> cmajflt 
                  >> result.utime >> result.stime)) {
            return std::nullopt;
        }

        long cutime, cstime, priority, nice, num_threads, itrealvalue;
        unsigned long long starttime;

        if (!(iss >> cutime >> cstime >> priority >> nice >> num_threads >> itrealvalue 
                  >> starttime >> result.vsize >> result.rssPages)) {
            return std::nullopt;
        }

        long clockTicks = sysconf(_SC_CLK_TCK);
        if (clockTicks <= 0) clockTicks = 100;

        long pageSize = sysconf(_SC_PAGESIZE);
        if (pageSize <= 0) pageSize = 4096;

        result.utimeSec = static_cast<double>(result.utime) / clockTicks;
        result.stimeSec = static_cast<double>(result.stime) / clockTicks;
        result.rssBytes = static_cast<unsigned long long>(result.rssPages) * pageSize;

        return result;
    }
};

int main() {
    const auto statOpt = ProcStatParser::parseFile("/proc/self/stat");
    if (!statOpt) {
        std::cerr << "Не вдалося розпарсити /proc/self/stat\n";
        return 1;
    }

    const auto& st = *statOpt;
    std::cout << "--- Результат розбору /proc/self/stat (C++) ---\n"
              << "PID:               " << st.pid << "\n"
              << "Comm:              " << st.comm << "\n"
              << "State:             " << st.state << "\n"
              << "PPID:              " << st.ppid << "\n"
              << "User Time:         " << st.utimeSec << " sec (" << st.utime << " ticks)\n"
              << "System Time:       " << st.stimeSec << " sec (" << st.stime << " ticks)\n"
              << "Virtual Memory:    " << (static_cast<double>(st.vsize) / (1024 * 1024)) << " MB\n"
              << "RSS Memory:        " << (static_cast<double>(st.rssBytes) / (1024 * 1024)) << " MB\n";

    return 0;
}
```
:::

---

## 4. Простеження викликів через strace та вимірювання швидкодії

При запуску скомпільованого парсера у середовищі Linux можна виконати простеження його системних викликів за допомогою трасувальника `strace`:

```bash
$ strace -e trace=openat,read,close ./proc_parser
openat(AT_FDCWD, "/proc/self/stat", O_RDONLY) = 3
read(3, "12345 (proc_parser) R 1234 123"..., 2048) = 320
close(3)                                = 0
```

Як видно з трасування, ядро обробляє зчитування `/proc/self/stat` у три послідовні кроки:
1. `openat()` відкриває віртуальний файл і отримує дескриптор `fd=3`.
2. `read()` звертається до підсистеми VFS, яка викликає внутрішній обробник `proc_tgid_stat()` у ядрі. Ядро форматує рядок статистик і копіює 320 байт у буфер користувацького простору через `copy_to_user()`.
3. `close()` звільняє дескриптор та вивільняє асоційовані об'єкти пам'яті VFS.

### Оптимізація у високонавантажених циклах моніторингу

Якщо демон моніторингу (наприклад Prometheus node_exporter чи Zabbix agent) зчитує метрики сотень процесів раз на секунду, постійне відкриття та закриття файлів `/proc/[pid]/stat` створює накладні витрати на створення інодів.

Для оптимізації продуктивності рекомендується використовувати такі прийоми:
- **Повторне використання файлових дескрипторів**: Відкрити дескриптор файлу `/proc/[pid]/stat` один раз при старті демона, а у циклі вимірювання виконувати системні виклики `lseek(fd, 0, SEEK_SET)` та `read(fd, buf, size)`. Це усуває накладні витрати на виклики `openat()` та `close()`.
- **Буферизація у пам'яті**: Читати файли `procfs` зчитуванням великих блоків пам'яті за один виклик `read()`, оминаючи попотокове зчитування байт за байтом.

---

## 5. Обробка помилок доступу та обходові стратегії

При розробці продуктового коду обходу `/proc` слід враховувати такі крайові умови:

1. **Процес завершився під час читання (`ENOENT`)**:
   Оскільки запущені процеси в системі постійно створюються та завершуються, виклик `open("/proc/PID/stat")` може повернути помилку `ENOENT` (No such file or directory). Отримання цієї помилки є нормальним штатною поведінкою і свідчить про те, що процес завершив своє виконання між викликом `readdir("/proc")` та спробою його відкриття.
2. **Недостатньо привілеїв під прапорцем `hidepid` (`EACCES`)**:
   Якщо файлову систему `/proc` змонтовано з прапорцем `hidepid=1` або `hidepid=2`, спроба зчитати `/proc/[pid]/cmdline` або `/proc/[pid]/environ` для процесів інших користувачів поверне помилку `EACCES` (Permission denied). Програма повинна коректно обробляти відсутність доступу без аварійного завершення.
3. **Обмеження розміру буфера для `cmdline` та `environ`**:
   Аргументи командного рядка у `/proc/[pid]/cmdline` можуть досягати розміру кількох мегабайт (ліміт `MAX_ARG_STRLEN`). Фіксований буфер розміром 1-2 КБ обріже аргументи. Для надійного зчитання `cmdline` слід виконувати зчитування у циклі до досягнення кінця файлу `EOF`.
