# ⚙️ Практичний інспектор процесів через procfs

При розробці системних утиліт моніторингу, діагностики або менеджерів процесів виникає потреба програмно зчитувати стан процесів без залучення важких сторонніх бібліотек. Псевдофайлова система `procfs` надає прямий інтерфейс до внутрішніх метаданих ядра через звичайні виклики файлового вводу-виводу. Зчитування псевдофайлів у каталозі `/proc/[pid]` дозволяє отримати повний зліпок виконання процесу: його ідентифікатори, аргументи запуску, споживання віртуальної та фізичної пам'яті, а також посилання на відкриті ресурси.

Нижче наведено практичний приклад побудови легкого інспектора процесів. Інспектор виконує послідовний розбір псевдофайлів `/proc/[pid]/status`, `/proc/[pid]/cmdline` та символічного посилання `/proc/[pid]/exe`. Реалізація показує як базові системні виклики POSIX у мові C, так і ідіоматичний підхід у сучасній мові C++ із використанням безпечних абстракцій роботи з файловою системою та строкових типів.

## Архітектура інспектора процесів

Перед початком кодування розберемо загальну послідовність дій системної утиліти:

1. **Перевірка існування процесу**: Спроба доступу до каталогу `/proc/[pid]`. Якщо виклик повертає помилку `ENOENT`, процес не існує або вже завершив виконання у ядрі.
2. **Зчитування магічного посилання `/proc/[pid]/exe`**: Отримання абсолютного шляху виконуваного файлу на диску за допомогою виклику `readlink()` або `std::filesystem::read_symlink()`.
3. **Розбір метаданих `/proc/[pid]/status`**: Витяг рядків `Name:`, `State:`, `VmRSS:` для оцінки типу програми, її поточного стану та споживання фізичної оперативної пам'яті.
4. **Сканування файлових дескрипторів у `/proc/[pid]/fd/`**: Ітерація по записах каталогу дескрипторів для підрахунку кількості відкритих сокетів та файлів.

## Реалізація інспектора процесів мовами C та C++

Утиліта приймає ідентифікатор процесу PID як аргумент командного рядка, перевіряє існування відповідного каталогу у `/proc`, розкодовує магічне посилання на виконуваний файл та витягує метрики оперативної пам'яті.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <dirent.h>
#include <errno.h>

#define BUF_SIZE 4096

typedef struct {
    int pid;
    char comm[256];
    char state[64];
    long vm_rss_kb;
    char exe_path[1024];
    int open_fds_count;
} proc_info_t;

int inspect_process(int pid, proc_info_t *info) {
    if (!info || pid <= 0) return -1;
    memset(info, 0, sizeof(proc_info_t));
    info->pid = pid;

    // 1. Отримання шляху до виконуваного файлу через magic symlink /proc/[pid]/exe
    char path_buf[256];
    snprintf(path_buf, sizeof(path_buf), "/proc/%d/exe", pid);
    ssize_t len = readlink(path_buf, info->exe_path, sizeof(info->exe_path) - 1);
    if (len != -1) {
        info->exe_path[len] = '\0';
    } else {
        strncpy(info->exe_path, "<недоступно або недостатньо прав>", sizeof(info->exe_path) - 1);
    }

    // 2. Читання та парсинг /proc/[pid]/status
    snprintf(path_buf, sizeof(path_buf), "/proc/%d/status", pid);
    int fd = open(path_buf, O_RDONLY);
    if (fd < 0) {
        return -1; // Процес не існує або немає прав доступу
    }

    char buffer[BUF_SIZE];
    ssize_t bytes_read = read(fd, buffer, sizeof(buffer) - 1);
    close(fd);

    if (bytes_read <= 0) return -1;
    buffer[bytes_read] = '\0';

    // Розбір рядків Name, State, VmRSS
    char *line = strtok(buffer, "\n");
    while (line != NULL) {
        if (strncmp(line, "Name:", 5) == 0) {
            sscanf(line + 5, "%255s", info->comm);
        } else if (strncmp(line, "State:", 6) == 0) {
            strncpy(info->state, line + 6, sizeof(info->state) - 1);
        } else if (strncmp(line, "VmRSS:", 6) == 0) {
            sscanf(line + 6, "%ld", &info->vm_rss_kb);
        }
        line = strtok(NULL, "\n");
    }

    // 3. Підрахунок відкритих файлових дескрипторів у /proc/[pid]/fd
    snprintf(path_buf, sizeof(path_buf), "/proc/%d/fd", pid);
    DIR *dir = opendir(path_buf);
    if (dir) {
        struct dirent *entry;
        while ((entry = readdir(dir)) != NULL) {
            if (entry->d_name[0] != '.') {
                info->open_fds_count++;
            }
        }
        closedir(dir);
    } else {
        info->open_fds_count = -1; // Відсутні права на перегляд fd
    }

    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <PID>\n", argv[0]);
        return EXIT_FAILURE;
    }

    int pid = atoi(argv[1]);
    proc_info_t info;

    if (inspect_process(pid, &info) != 0) {
        fprintf(stderr, "Не вдалося зчитати дані для PID %d: %s\n", pid, strerror(errno));
        return EXIT_FAILURE;
    }

    printf("=== Інспекція процесу PID %d ===\n", info.pid);
    printf("Назва:       %s\n", info.comm);
    printf("Стан:        %s\n", info.state);
    printf("Шлях бінарн: %s\n", info.exe_path);
    printf("Пам'ять RSS: %ld КБ\n", info.vm_rss_kb);
    if (info.open_fds_count >= 0) {
        printf("Дескриптори: %d відкритих fd\n", info.open_fds_count);
    } else {
        printf("Дескриптори: <немає доступу до /proc/%d/fd>\n", info.pid);
    }

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <filesystem>
#include <optional>
#include <system_error>

namespace fs = std::filesystem;

struct ProcessInfo {
    int pid;
    std::string name;
    std::string state;
    long vm_rss_kb{0};
    std::string exe_path;
    int open_fds_count{0};
};

class ProcInspector {
public:
    static std::optional<ProcessInfo> inspect(int pid) {
        if (pid <= 0) return std::nullopt;

        ProcessInfo info;
        info.pid = pid;

        const fs::path proc_dir = fs::path("/proc") / std::to_string(pid);
        if (!fs::exists(proc_dir)) {
            return std::nullopt;
        }

        // 1. Отримання символічного посилання exe за допомогою std::filesystem
        std::error_code ec;
        auto exe_target = fs::read_symlink(proc_dir / "exe", ec);
        if (!ec) {
            info.exe_path = exe_target.string();
        } else {
            info.exe_path = "<недоступно або недостатньо прав>";
        }

        // 2. Зчитування метаданих status за допомогою RAII потоків
        std::ifstream status_file(proc_dir / "status");
        if (!status_file.is_open()) {
            return std::nullopt;
        }

        std::string line;
        while (std::getline(status_file, line)) {
            std::string_view sv(line);
            if (sv.starts_with("Name:")) {
                auto val = sv.substr(5);
                size_t first = val.find_first_not_of(" \t");
                if (first != std::string_view::npos) {
                    info.name = std::string(val.substr(first));
                }
            } else if (sv.starts_with("State:")) {
                auto val = sv.substr(6);
                size_t first = val.find_first_not_of(" \t");
                if (first != std::string_view::npos) {
                    info.state = std::string(val.substr(first));
                }
            } else if (sv.starts_with("VmRSS:")) {
                auto val = sv.substr(6);
                size_t first = val.find_first_not_of(" \t");
                if (first != std::string_view::npos) {
                    info.vm_rss_kb = std::stol(std::string(val.substr(first)));
                }
            }
        }

        // 3. Підрахунок відкритих файлових дескрипторів за допомогою directory_iterator
        const fs::path fd_dir = proc_dir / "fd";
        ec.clear();
        if (fs::exists(fd_dir, ec)) {
            for (const auto& entry : fs::directory_iterator(fd_dir, ec)) {
                if (!ec) {
                    info.open_fds_count++;
                }
            }
        } else {
            info.open_fds_count = -1; // Немає прав на каталог fd
        }

        return info;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <PID>\n";
        return 1;
    }

    int pid = std::stoi(argv[1]);
    auto info_opt = ProcInspector::inspect(pid);

    if (!info_opt) {
        std::cerr << "Помилка: Не вдалося прочитати /proc/" << pid << "\n";
        return 1;
    }

    const auto& info = *info_opt;
    std::cout << "=== Інспекція процесу PID " << info.pid << " ===\n"
              << "Назва:       " << info.name << "\n"
              << "Стан:        " << info.state << "\n"
              << "Шлях бінарн: " << info.exe_path << "\n"
              << "Пам'ять RSS: " << info.vm_rss_kb << " КБ\n";
    if (info.open_fds_count >= 0) {
        std::cout << "Дескриптори: " << info.open_fds_count << " відкритих fd\n";
    } else {
        std::cout << "Дескриптори: <немає доступу до /proc/" << info.pid << "/fd>\n";
    }

    return 0;
}
```
:::

## Покроковий алгоритмічний аналіз реалізації

Розберемо ключові інженерні деталі наведеного коду:

### 1. Робота з магічними посиланнями readlink та std::filesystem

Системний виклик POSIX `readlink()` є низькорівневим інструментом. Під час його використання необхідно враховувати два критичних правила:
* `readlink()` **не ставить** завершального нульового байта `\0` в кінець масиву `buffer`. Якщо розробник використає буфер без попереднього обнулення або без установки `info->exe_path[len] = '\0'`, передача цього масиву у `printf("%s")` призведе до зчитування сміття з пам'яті або до виходу за межі буфера.
* Розмір буфера має бути достатнім для розкодування найдовших системних шляхів. Рекомендовано виділяти буфер розміром `PATH_MAX` (4096 байтів).

У C++ версії використання стандарту C++17 та `std::filesystem::read_symlink()` повністю ховає низькорівневі виклики VFS. Функція автоматично виділяє пам'ять під об'єкт `std::filesystem::path` та повертає безпечний рядок. Передача об'єкта `std::error_code` запобігає викиданню системних винятків (`std::filesystem::filesystem_error`) у разі відсутності прав доступу або раптового завершення процесу.

### 2. Парсинг псевдофайла status та використання string_view

Під час аналізу псевдофайлів `procfs` використання `std::string_view` у C++ дозволяє повністю уникнути зайвих динамічних виділень пам'яті на купі (`heap allocations`). Метод `std::getline()` зчитує рядок у буфер, після чого `std::string_view` дає зріз цього рядка для швидкої перевірки префікса `starts_with("Name:")` (сам метод — із C++20) та видалення початкових пробілів без копіювання байтів.

У C-версії застосовується функція `strtok()`, яка модифікує вхідний буфер, замінюючи символи `\n` на нульові байти. Це вимагає, щоб вхідний буфер виділявся у стек-пам'яті або купі з можливістю запису.

### 3. Обхід файлових дескрипторів та закриття системних ресурсів

Для підрахунку відкритих дескрипторів у каталозі `/proc/[pid]/fd/` у мові C застосовуються виклики `opendir()` та `readdir()`. Обов'язковою умовою є ігнорування записів із крапками (`.` та `..`), оскільки вони є системними покажчиками каталогу.

У мові C++ метод `std::filesystem::directory_iterator` автоматично ігнорує записи `.` та `..`, полегшуючи обхід каталогу. При цьому в обох мовах необхідно обробляти помилку доступу: якщо користувач намагається проінспектувати чужий процес без прав `root`, відкриття каталогу `/proc/[pid]/fd` поверне помилку `EACCES` (Permission denied). Код повинен коректно повертати прапор відсутності доступу, а не завершувати виконання програми.

## Крайові випадки та безпека системного вводу-виводу

При масштабуванні інспектора процесів для роботи у виробничих середовищах слід враховувати наступні крайові умови:

1. **Гонка станів процесів (Race Condition)**: Процес може померти між викликом `fs::exists("/proc/1234")` та зчитуванням `/proc/1234/status`. Системна утиліта не повинна покладатися на попередню перевірку існування каталогу; основними критеріями успіху є результати відкриття файлів `open()` або `ifstream::open()`.
2. **Переповнення пам'яті під час читання cmdline**: На відміну від `status`, псевдофайл `cmdline` може мати великий розмір (до 2 МБ у сучасних ядрах Linux). Зчитування `cmdline` вимагає циклічного виклику `read()` із динамічним розширенням буфера.
3. **Прапори hidepid та ізоляція у контейнерах**: Якщо система змонтована з опцією `hidepid=2`, спроба інспектування процесу іншого користувача поверне `ENOENT`. Інспектор повинен розрізняти ситуації "процес не існує у системі" та "процес приховано політикою безпеки hidepid".
