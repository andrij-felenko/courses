# ⚙️ Практична реалізація паралельного обробника файлових дерев мовами C та C++

Робота з великими масивами файлів на системному рівні вимагає поєднання неблокуючого обходу каталогів через системні виклики VFS, безпечного формування пакетів аргументів з NUL-розділювачами та оркестрації пулу паралельних дочірніх процесів за допомогою `fork()` і `waitpid()`.

Нижче наведено практичну реалізацію утиліти пакетної паралельної обробки, яка виконує роль власного комбінованого генератора `find | xargs -0 -P`.

---

## Архітектура системного генератора та диспетчера пакетів

Традиційні конвеєри в оболонці організовують обробку файлів через два окремі процеси, з'єднані анонімним каналом: генератор (`find`) читає структуру каталогів і записує байти в канал, а виконавець (`xargs`) читає байти з каналу, накопичує аргументи та породжує дочірні процеси. Хоча такий підхід є гнучким, він створює накладні витрати на міжпроцесну комунікацію, дублювання буферизації пам'яті та передачу даних через кільцевий буфер ядра розміром 64 KB.

Програмна реалізація єдиного диспетчера безпосередньо мовами системного програмування об'єднує генерацію списку файлів та диспетчеризацію завдань у межах єдиного адресного простору. Диспетчер самостійно керує життєвим циклом пулу воркерів, контролює ліміт одночасно виконуваних процесів та мінімізує кількість системних викликів.

---

## Постановка інженерної задачі

Необхідно обійти довільно глибоке дерево каталогів, відібрати всі звичайні файли з розширенням `.log`, згрупувати їх у пакети фіксованого розміру (наприклад, по 64 файли на один запуск) та передати їх паралельним процесам-воркерам (наприклад, утиліті стиснення `gzip`), обмежуючи максимальну кількість одночасних процесів фіксованим числом ядер процесора.

Критичні вимоги до реалізації:
1. **Стійкість до спеціальних символів:** коректна обробка імен файлів із пробілами, лапками та символами нового рядка завдяки прямому передаванню масивів покажчиків без проміжного текстового розбору.
2. **Контроль пам'яті:** споживання пам'яті процесу має залежати лише від глибини дерева каталогів O(depth), а не від загальної кількості знайдених файлів у файловій системі.
3. **Запобігання процесам-зомбі:** регулярне збирання статусів завершення всіх дочірніх процесів через неблокуючий системний виклик `waitpid()` з прапорцем `WNOHANG`.
4. **Контроль переповнення лімітів ядра:** сумарний розмір сформованого масиву `argv[]` не повинен перевищувати системний ліміт `ARG_MAX`.

---

## Реалізація системного диспетчера

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <errno.h>

#define BATCH_CAPACITY 64
#define MAX_PARALLEL_WORKERS 4

typedef struct {
    char *items[BATCH_CAPACITY + 2];
    int count;
} BatchBuffer;

static void init_batch(BatchBuffer *b, const char *command) {
    b->items[0] = strdup(command);
    b->count = 1;
}

static void free_batch_payload(BatchBuffer *b) {
    for (int i = 1; i < b->count; ++i) {
        free(b->items[i]);
    }
    b->count = 1;
}

static void drain_workers(int *active_workers, int block_for_slot) {
    while (*active_workers > 0) {
        int status = 0;
        int flags = block_for_slot ? 0 : WNOHANG;
        pid_t pid = waitpid(-1, &status, flags);
        if (pid > 0) {
            (*active_workers)--;
            if (block_for_slot) break;
        } else {
            break;
        }
    }
}

static void dispatch_batch(BatchBuffer *b, int *active_workers) {
    if (b->count <= 1) return;

    b->items[b->count] = NULL;

    while (*active_workers >= MAX_PARALLEL_WORKERS) {
        drain_workers(active_workers, 1);
    }

    pid_t pid = fork();
    if (pid == 0) {
        /* Дочірній процес: заміна образу процесу на цільову команду */
        execvp(b->items[0], b->items);
        _exit(127);
    } else if (pid > 0) {
        (*active_workers)++;
        free_batch_payload(b);
    } else {
        perror("fork");
    }
}

static void traverse_tree(const char *dir_path, BatchBuffer *b, int *active_workers) {
    DIR *dir = opendir(dir_path);
    if (!dir) return;

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }

        char full_path[4096];
        int len = snprintf(full_path, sizeof(full_path), "%s/%s", dir_path, entry->d_name);
        if (len >= (int)sizeof(full_path)) continue;

        struct stat st;
        if (lstat(full_path, &st) == -1) continue;

        if (S_ISDIR(st.st_mode)) {
            traverse_tree(full_path, b, active_workers);
        } else if (S_ISREG(st.st_mode)) {
            /* Фільтр: файли з розширенням .log */
            const char *dot = strrchr(entry->d_name, '.');
            if (dot && strcmp(dot, ".log") == 0) {
                b->items[b->count++] = strdup(full_path);
                if (b->count > BATCH_CAPACITY) {
                    dispatch_batch(b, active_workers);
                }
            }
        }
    }
    closedir(dir);
}

int main(int argc, char *argv[]) {
    const char *start_dir = (argc > 1) ? argv[1] : ".";
    BatchBuffer batch;
    init_batch(&batch, "gzip");

    int active_workers = 0;
    traverse_tree(start_dir, &batch, &active_workers);

    /* Відправлення фінального залишку накопичених аргументів */
    dispatch_batch(&batch, &active_workers);

    /* Очікування завершення всіх активних воркерів */
    while (active_workers > 0) {
        drain_workers(&active_workers, 1);
    }

    free(batch.items[0]);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <filesystem>
#include <memory>
#include <span>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

namespace fs = std::filesystem;

class WorkerPool {
public:
    explicit WorkerPool(std::size_t max_workers) : max_workers_(max_workers) {}

    ~WorkerPool() {
        wait_all();
    }

    void spawn(const std::string& command, const std::vector<std::string>& batch) {
        if (batch.empty()) return;

        while (active_workers_ >= max_workers_) {
            reap_one(true);
        }

        std::vector<char*> raw_args;
        raw_args.reserve(batch.size() + 2);
        raw_args.push_back(const_cast<char*>(command.c_str()));
        for (const auto& arg : batch) {
            raw_args.push_back(const_cast<char*>(arg.c_str()));
        }
        raw_args.push_back(nullptr);

        pid_t pid = fork();
        if (pid == 0) {
            ::execvp(raw_args[0], raw_args.data());
            ::_exit(127);
        } else if (pid > 0) {
            ++active_workers_;
            reap_nonblocking();
        } else {
            throw std::system_error(errno, std::generic_category(), "fork failed");
        }
    }

    void wait_all() {
        while (active_workers_ > 0) {
            reap_one(true);
        }
    }

private:
    std::size_t max_workers_;
    std::size_t active_workers_{0};

    void reap_nonblocking() {
        while (active_workers_ > 0) {
            int status = 0;
            pid_t pid = ::waitpid(-1, &status, WNOHANG);
            if (pid > 0) {
                --active_workers_;
            } else {
                break;
            }
        }
    }

    void reap_one(bool blocking) {
        int status = 0;
        int flags = blocking ? 0 : WNOHANG;
        pid_t pid = ::waitpid(-1, &status, flags);
        if (pid > 0) {
            --active_workers_;
        }
    }
};

void process_tree(const fs::path& root, const std::string& command, std::size_t batch_size) {
    WorkerPool pool(4);
    std::vector<std::string> current_batch;
    current_batch.reserve(batch_size);

    std::error_code ec;
    auto iter = fs::recursive_directory_iterator(root, fs::directory_options::skip_permission_denied, ec);
    auto end_iter = fs::recursive_directory_iterator();

    for (; iter != end_iter && !ec; iter.increment(ec)) {
        if (ec) {
            ec.clear();
            continue;
        }

        const auto& entry = *iter;
        if (entry.is_regular_file(ec) && entry.path().extension() == ".log") {
            current_batch.push_back(entry.path().string());
            if (current_batch.size() >= batch_size) {
                pool.spawn(command, current_batch);
                current_batch.clear();
            }
        }
    }

    if (!current_batch.empty()) {
        pool.spawn(command, current_batch);
    }
}

int main(int argc, char* argv[]) {
    try {
        fs::path target_dir = (argc > 1) ? argv[1] : ".";
        process_tree(target_dir, "gzip", 64);
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

---

## Покроковий розбір механізму пулу процесів

Алгоритм керування пулом дочірніх процесів базується на двох фазах взаємодії з планувальником ядра:

1. **Неблокуюче опитування (`reap_nonblocking`):** Після кожного успішного запуску нового процесу диспетчер виконує цикл викликів `waitpid(-1, &status, WNOHANG)`. Спеціальний прапорець `WNOHANG` наказує ядру негайно повернути керування з нульовим значенням, якщо жоден із запущених процесів ще не змінив свій стан. Якщо процес уже завершився, ядро повертає його PID, вивільняє запис у таблиці процесів ОС та зменшує внутрішній лічильник активних воркерів `active_workers_`.

2. **Блокуюче очікування вільного слота (`reap_one(true)`):** Якщо кількість запущених воркерів досягає максимального ліміту (наприклад, 4 паралельні процеси на 4-ядерній системі), диспетчер не може викликати наступний `fork()`. Він переходить у блокуючий виклик `waitpid()` без прапорця `WNOHANG`. Потік диспетчера призупиняється ядром і переходить у стан сну `TASK_INTERRUPTIBLE`. Щойно один із воркерів завершує обробку свого пакету файлів, ядро надсилає сигнал `SIGCHLD`, будить процес диспетчера, фіксує звільнення слота та дозволяє запустити наступну пачку файлів.

---

## Аналіз системних пасток та крайових випадків

### 1. Переповнення буфера конвеєра при великій кількості виводу
Якщо дочірні процеси записують великі обсяги діагностичної інформації у стандартні потоки `stdout` або `stderr`, неперенаправлені дескриптори заповнять 64-кілобайтний кільцевий буфер ядра (`pipe_buffer`), спричинивши блокування воркера на системному виклику `write()`. Оскільки батьківський процес не зчитує ці дані, виникає стан мертвого блокування (deadlock): воркер чекає звільнення буфера, а батько чекає завершення воркера. Для високонавантажених завдань кожен воркер повинен перенаправляти свій вивід в окремий файл на диску або у псевдопристрій `/dev/null`.

### 2. Стан гонитви при модифікації файлової системи під час обходу
Якщо інший фоновий процес встигає видалити або перейменувати файл після того, як `readdir()` повернув його запис у списку каталогу, подальший виклик `lstat()` або `open()` поверне помилку `ENOENT`. Програма обходу обов'язково повинна перевіряти статус помилки `errno` та ігнорувати відсутність файлу, не перериваючи загальний цикл сканування всього дерева.

### 3. Перевищення ліміту відкритих дескрипторів файлів
Рекурсивний обхід каталогів через класичний виклик `opendir()` утримує відкритим дескриптор для кожного рівня вкладеності дерева. На глибоких ієрархіях каталогів (понад 1024 рівні) процес може вичерпати системний ліміт `RLIMIT_NOFILE`. Використання лінійного стеку шляхів або сучасних ітераторів на базі системного виклику `openat()` дозволяє утримувати відкритим дескриптор лише для поточного активного каталогу.

### 4. Коректне поширення сигналів завершення
У разі отримання сигналів аварійної зупинки `SIGINT` (Ctrl+C) або `SIGTERM` батьківський процес диспетчера повинен надіслати відповідний сигнал усій групі процесів за допомогою системного виклику `kill(-pgid, SIGTERM)`. Без цього переривання роботи диспетчера залишить десятки фонових процесів-воркерів працювати безконтрольно, нераціонально споживаючи ресурси процесора та дискової підсистеми.
