# ⚙️ Практикум: інспекція /proc, розрахунок метрик та виявлення видалених файлів

Цей практикум демонструє розробку системної утиліти низькорівневого аналізу процесів та відкритої дискової пам'яті. Програма сканує віртуальну файлову систему `/proc`, коректно розбирає поля станів та процесорних тактів у `/proc/[pid]/stat`, інспектує каталог дескрипторів `/proc/[pid]/fd/` за допомогою системного виклику `readlink()` і виявляє відкриті файли, видалені з файлової системи (мітка `(deleted)`), які продовжують блокувати дисковий простір.

---

## 1. Внутрішній механізм VFS та алгоритм роботи інспектора

Системні інструменти на зразок `ps`, `top` та `lsof` не використовують привілейованих магічних викликів: вони працюють як регулярні користувацькі програми, що обходять ієрархію віртуальних каталогів `/proc`.

### Як ядро генерує символічні посилання у /proc/[pid]/fd/

Каталог `/proc/[pid]/fd/` не існує на фізичному диску — це динамічний вузол псевдофайлової системи `procfs`. Коли користувацький процес або утиліта викликає `readdir()` на цьому каталозі, ядро звертається до структури процесу `task_struct`, переходить за покажчиком `files` до таблиці дескрипторів `files_struct` та ітерує відкриті файлові об'єкти `struct file*`.

Кожен числовий запис у каталозі (наприклад, `/proc/4821/fd/3`) є спеціальним символічним посиланням. Коли програма виконує системний виклик `readlink()` на такому дескрипторі, обробник ядра `proc_fd_link()` викликає функцію `d_path()`. Ця функція відновлює повний шлях до файлу, піднімаючись угору деревом елементів каталогу `struct dentry` до кореня точки монтування.

Якщо файл було видалено з файлової системи через виклик `unlink()` або `rm`, але процес утримує дескриптор відкритим, прапорець `d_unhashed(dentry)` стає істинним, а лічильник жорстких посилань іноди `inode->i_nlink` падає до нуля. У цьому разі функція ядра `d_path()` автоматично дописує суфікс `" (deleted)"` у кінець поверненого рядка.

### Чотири етапи алгоритму інспектора

1. **Ітерація простору процесів:** Утиліта відкриває каталог `/proc` системним викликом `opendir()` та ітерує його записи через `readdir()`. Записи, назви яких складаються виключно з десяткових цифр, відповідають активним процесам `PID`. Усі інші службові вузли (`sys/`, `net/`, `fs/`, `bus/`) пропускаються.
2. **Розбір стану та пам'яті (`/proc/[pid]/stat`):** Для кожного знайденого PID зчитується файл `stat`. Алгоритм знаходить крайні круглі дужки для надійного виділення імені команди `comm`, після чого витягує символьний стан задачі (`state`: R, S, D, Z, T), ідентифікатор батьківського процесу (`ppid`), лічильники тактів `utime`/`stime`, розмір віртуальної пам'яті `vsize` та резидентний розмір `rss`.
3. **Сканування дескрипторів (`/proc/[pid]/fd/`):** Програма відкриває каталог дескрипторів конкретного процесу. Виклик `readlink()` повертає цільовий шлях файлу. Якщо рядок містить мітку `(deleted)`, утиліта фіксує потенційний витік дискових блоків.
4. **Оцінка розміру утримуваного файлу:** Для кожного знайденого видаленого файлу виконується системний виклик `stat()` або `fstat()` на шляху `/proc/[pid]/fd/<FD>`. Оскільки VFS резолвить цей шлях безпосередньо до структури `struct inode` в оперативній пам'яті ядра, `stat()` повертає реальний розмір файлу в байтах (`st_size`) та кількість фактично зайнятих 512-байтних блоків диска (`st_blocks`), навіть якщо файлу більше немає в жодному каталозі.

---

## 2. Реалізація інспектора (C та C++)

Нижче наведено порівняльні реалізації утиліти мовами C та C++ у вкладках `:::tabs`. Реалізація C демонструє пряму роботу з POSIX-інтерфейсами каталогів, буферів та парсингу рядків, а реалізація C++ використовує сучасний стандарт C++20 з бібліотеками `std::filesystem`, `std::string_view`, `std::vector` та безпечними механізмами RAII.

:::tabs
```c
/* C Implementation: /proc Inspector and Deleted File Detector */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <ctype.h>
#include <errno.h>

#define PROC_PATH_MAX 512
#define BUFFER_SIZE 4096

typedef struct {
    pid_t pid;
    pid_t ppid;
    char comm[256];
    char state;
    unsigned long utime;
    unsigned long stime;
    unsigned long vsize;
    long rss;
} ProcessStat;

int is_numeric_dir(const char *name) {
    while (*name) {
        if (!isdigit((unsigned char)*name)) return 0;
        name++;
    }
    return 1;
}

int parse_proc_stat(pid_t pid, ProcessStat *pstat) {
    char stat_path[PROC_PATH_MAX];
    snprintf(stat_path, sizeof(stat_path), "/proc/%d/stat", pid);

    FILE *f = fopen(stat_path, "r");
    if (!f) return -1;

    char buffer[BUFFER_SIZE];
    if (!fgets(buffer, sizeof(buffer), f)) {
        fclose(f);
        return -1;
    }
    fclose(f);

    /* Пошук меж імені comm: перша '(' та остання ')' */
    char *open_paren = strchr(buffer, '(');
    char *close_paren = strrchr(buffer, ')');
    if (!open_paren || !close_paren || close_paren < open_paren) {
        return -1;
    }

    pstat->pid = pid;
    size_t comm_len = (size_t)(close_paren - open_paren - 1);
    if (comm_len >= sizeof(pstat->comm)) comm_len = sizeof(pstat->comm) - 1;
    strncpy(pstat->comm, open_paren + 1, comm_len);
    pstat->comm[comm_len] = '\0';

    /* Зчитування полів після останньої дужки */
    char *rest = close_paren + 2;
    int items = sscanf(rest,
        "%c %d %*d %*d %*d %*d %*u %*u %*u %*u %*u %lu %lu %*d %*d %*d %*d %*d %*d %*u %lu %ld",
        &pstat->state,
        &pstat->ppid,
        &pstat->utime,
        &pstat->stime,
        &pstat->vsize,
        &pstat->rss);

    return (items == 6) ? 0 : -1;
}

void check_deleted_fds(pid_t pid, const char *comm) {
    char fd_dir_path[PROC_PATH_MAX];
    snprintf(fd_dir_path, sizeof(fd_dir_path), "/proc/%d/fd", pid);

    DIR *dir = opendir(fd_dir_path);
    if (!dir) return; /* Можлива відмова у правах доступу для чужих процесів */

    struct dirent *entry;
    char link_target[PROC_PATH_MAX];
    char symlink_path[PROC_PATH_MAX];

    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_name[0] == '.') continue;

        snprintf(symlink_path, sizeof(symlink_path), "/proc/%d/fd/%s", pid, entry->d_name);
        ssize_t len = readlink(symlink_path, link_target, sizeof(link_target) - 1);
        if (len <= 0) continue;
        link_target[len] = '\0';

        /* Перевірка чи містить посилання мітку '(deleted)' */
        if (strstr(link_target, "(deleted)") != NULL) {
            struct stat st;
            off_t file_size = 0;
            if (stat(symlink_path, &st) == 0) {
                file_size = st.st_size;
            }

            printf("[DELETED FILE LEAK] PID: %-6d | Comm: %-15s | FD: %-3s | Size: %10ld bytes | File: %s\n",
                   pid, comm, entry->d_name, (long)file_size, link_target);
        }
    }
    closedir(dir);
}

int main(void) {
    DIR *proc_dir = opendir("/proc");
    if (!proc_dir) {
        perror("Failed to open /proc");
        return 1;
    }

    printf("=== SCANNING SYSTEM PROCESSES & UNLINKED OPEN FILES ===\n");
    struct dirent *entry;
    while ((entry = readdir(proc_dir)) != NULL) {
        if (!is_numeric_dir(entry->d_name)) continue;

        pid_t pid = (pid_t)atoi(entry->d_name);
        ProcessStat pstat;
        if (parse_proc_stat(pid, &pstat) == 0) {
            /* Якщо процес у стані D (дисковий сон), виводимо окреме попередження */
            if (pstat.state == 'D') {
                printf("[UNINTERRUPTIBLE D-STATE] PID: %-6d | Comm: %-15s | PPID: %-6d\n",
                       pstat.pid, pstat.comm, pstat.ppid);
            }

            /* Перевіряємо відкриті файлові дескриптори на витоки */
            check_deleted_fds(pid, pstat.comm);
        }
    }

    closedir(proc_dir);
    return 0;
}
```
```cpp
// C++ Implementation: RAII /proc Inspector and Deleted File Detector using C++20
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <filesystem>
#include <optional>
#include <cctype>
#include <algorithm>
#include <unistd.h>
#include <sys/stat.h>

namespace fs = std::filesystem;

struct ProcessStat {
    pid_t pid{0};
    pid_t ppid{0};
    std::string comm;
    char state{'?'};
    unsigned long utime{0};
    unsigned long stime{0};
    unsigned long vsize{0};
    long rss{0};
};

class ProcInspector {
public:
    static std::optional<ProcessStat> parseStat(pid_t pid) {
        const std::string path = "/proc/" + std::to_string(pid) + "/stat";
        std::ifstream file(path);
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

        ProcessStat stat;
        stat.pid = pid;
        stat.comm = line.substr(openParen + 1, closeParen - openParen - 1);

        const std::string rest = line.substr(closeParen + 2);
        char state = '?';
        pid_t ppid = 0;
        unsigned long utime = 0, stime = 0, vsize = 0;
        long rss = 0;

        const int items = std::sscanf(rest.c_str(),
            "%c %d %*d %*d %*d %*d %*u %*u %*u %*u %*u %lu %lu %*d %*d %*d %*d %*d %*d %*u %lu %ld",
            &state, &ppid, &utime, &stime, &vsize, &rss);

        if (items != 6) {
            return std::nullopt;
        }

        stat.state = state;
        stat.ppid = ppid;
        stat.utime = utime;
        stat.stime = stime;
        stat.vsize = vsize;
        stat.rss = rss;

        return stat;
    }

    static void scanDeletedDescriptors(pid_t pid, std::string_view comm) {
        const std::string fdDirPath = "/proc/" + std::to_string(pid) + "/fd";
        std::error_code ec;
        
        if (!fs::exists(fdDirPath, ec) || ec) {
            return;
        }

        for (const auto& entry : fs::directory_iterator(fdDirPath, fs::directory_options::skip_permission_denied, ec)) {
            if (ec) break;

            std::error_code readlinkEc;
            const auto target = fs::read_symlink(entry.path(), readlinkEc);
            if (readlinkEc) continue;

            const std::string targetStr = target.string();
            if (targetStr.find("(deleted)") != std::string::npos) {
                struct stat st{};
                off_t fileSize = 0;
                if (::stat(entry.path().c_str(), &st) == 0) {
                    fileSize = st.st_size;
                }

                std::cout << "[DELETED FILE LEAK] PID: " << pid
                          << " | Comm: " << comm
                          << " | FD: " << entry.path().filename().string()
                          << " | Size: " << fileSize << " bytes"
                          << " | File: " << targetStr << '\n';
            }
        }
    }

    static void runScan() {
        std::cout << "=== SCANNING SYSTEM PROCESSES & UNLINKED OPEN FILES (C++) ===\n";
        std::error_code ec;

        for (const auto& entry : fs::directory_iterator("/proc", fs::directory_options::skip_permission_denied, ec)) {
            if (ec) break;

            const std::string filename = entry.path().filename().string();
            if (!filename.empty() && std::all_of(filename.begin(), filename.end(), ::isdigit)) {
                const pid_t pid = std::stoi(filename);
                const auto statOpt = parseStat(pid);
                if (statOpt) {
                    if (statOpt->state == 'D') {
                        std::cout << "[UNINTERRUPTIBLE D-STATE] PID: " << statOpt->pid
                                  << " | Comm: " << statOpt->comm
                                  << " | PPID: " << statOpt->ppid << '\n';
                    }
                    scanDeletedDescriptors(pid, statOpt->comm);
                }
            }
        }
    }
};

int main() {
    ProcInspector::runScan();
    return 0;
}
```
:::

---

## 3. Крайові випадки, пастки та безпечне усунення витоків

Під час практичної експлуатації та написання системних парсерів `/proc` необхідно враховувати специфічні особливості роботи ядра:

### Зникнення процесу під час ітерації (Race Conditions)

Між моментом, коли функція `readdir()` виявила каталог `/proc/14820`, та моментом відкриття файлу `fopen("/proc/14820/stat")`, процес може завершити виконання та викликати `exit_group()`. У цьому разі системний виклик `open()` поверне помилку `ENOENT` (No such file or directory).

Надійний системний парсер зобов'язаний розглядати помилку `ENOENT` як нормальну штатну ситуацію та продовжувати обхід без виведення панічних повідомлень або аварійної зупинки.

### Обмеження прав доступу (EACCES) та Capabilities

Каталог `/proc/[pid]/fd/` має права доступу `0700` і належить власнику процесу (UID/GID). Якщо діагностична утиліта запущена від імені звичайного непривілейованого користувача, спроба прочитати дескриптори процесів інших користувачів або системних демонів (наприклад, `root` чи `postgres`) завершиться помилкою `EACCES` (Permission denied).

Для повної системної діагностики програма потребує запуску від імені суперкористувача `root` або встановлення спеціалізованих Linux Capabilities без надання повного доступу `root`:

```bash
# Надання утиліті прав читання чужих дескрипторів та структури процесів
$ sudo setcap cap_sys_ptrace,cap_dac_read_search+ep ./proc_inspector
```

Прапорець `CAP_DAC_READ_SEARCH` дозволяє обходити обмеження прав доступу на каталоги дескрипторів, а `CAP_SYS_PTRACE` дозволяє читати символічні посилання та змінні оточення процесів інших користувачів.

### Розрахунок реального споживання пам'яті (RSS проти PSS)

Поле `rss` у файлі `/proc/[pid]/stat` показує загальну кількість фізичних сторінок, відображених у процес. Проте якщо кілька процесів використовують спільні бібліотеки (`libc.so`) або спільні сегменти пам'яті через `fork()`, показник RSS враховує ці сторінки для кожного процесу окремо, що призводить до багаторазового завищення сумарного обсягу пам'яті.

Для точного обліку використовується файл `/proc/[pid]/smaps_rollup`, звідки зчитується показник **PSS (Proportional Set Size)**. Показник PSS ділить розмір кожної спільної сторінки на кількість процесів, які її використовують, надаючи математично коректне значення споживаної фізичної RAM.

### Безпечне вивільнення дискового простору без перезапуску сервісу

Коли утиліта знаходить процес, що утримує багатогігабайтний видалений файл логів (наприклад, `/var/log/app.log (deleted)` під дескриптором `fd=3` у процесі `PID 4821`), адміністратор часто не має можливості перезапустити критичний сервіс бази даних або веб-сервера.

У цьому разі застосовується техніка прямого усікання іноди через дескрипторний інтерфейс `/proc`:

```bash
# Пряме усікання утримуваного файлу до 0 байтів через VFS
$ truncate -s 0 /proc/4821/fd/3
```

Ця команда виконує системний виклик `truncate()` безпосередньо на символічному посиланні дескриптора. Ядро знаходить відповідну структуру `struct inode` і викликає операцію драйвера файлової системи (`ext4_truncate` або `xfs_setattr_size`) для негайного звільнення виділених блоків екстентів на диску, скидаючи розмір `i_size` до 0.

У результаті дисковий простір утиліти `df` негайно повертається в пул вільної пам'яті, а сервіс продовжує записувати нові логи у той самий відкритий дескриптор без збоїв, зависань та втрати з'єднань клієнтів.
