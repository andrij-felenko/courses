# Зовнішнє сортування злиттям: робоча реалізація

Повна інженерна реалізація алгоритму зовнішнього сортування злиттям (External Merge Sort) для файлів довільного розміру, обсяг яких перевищує доступну оперативну пам'ять процесу.

## 1. Архітектурний дизайн та фази виконання

Коли розмір текстового файлу перевищує фізичний обсяг оперативної пам'яті сервера, пряме застосування алгоритмів швидкого сортування `qsort()` або `std::sort()` стає неможливим, оскільки вони вимагають одночасного завантаження всіх елементів у пам'ять. Спроба виділити пам'ять під гігабайтний масив рядків призводить до інтенсивного свопінгу сторінок (page thrashing), різкого падіння пропускної здатності дискової підсистеми або аварійного завершення процесу через Out-Of-Memory killer.

Алгоритм External Merge Sort розв'язує цю задачу шляхом розділення процесу впорядкування на дві послідовні системні фази з суворим контролем використання пам'яті.

### Фаза 1: Генерація серій (Run Generation)

1. Процес виділяє фіксований буфер пам'яті розміром `MEM_LIMIT_BYTES` (наприклад, 4 МБ або 2 ГБ залежно від конфігурації).
2. Вхідний потік зчитується послідовно рядок за рядком, накопичуючись у динамічному масиві покажчиків або векторних структурах до досягнення ліміту пам'яті.
3. Як тільки буфер заповнюється, завантажений блок сортується в пам'яті за допомогою швидкого внутрішнього алгоритму сортування.
4. Відсортована серія записується на диск у тимчасовий файл з унікальним іменем (наприклад, у каталозі `/tmp`).
5. Пам'ять звільняється, і процес повертається до зчитування наступної порції вхідного потоку.
6. Фаза повторюється до повного вичерпання вхідного файлу, створюючи на диску множину з `K` локально відсортованих тимчасових файлів (серій).

### Фаза 2: K-входове злиття (K-Way Merge)

1. Процес відкриває всі `K` тимчасових файлів для одночасного паралельного зчитування.
2. Для ефективного пошуку поточного глобального мінімуму ініціалізується структура даних **мін-купа (min-heap)** або пріоритетна черга місткістю `K` елементів.
3. З кожного відкритого тимчасового файлу зчитується рівно один початковий рядок (який є найменшим елементом цього конкретного файлу) і поміщається в купу разом із покажчиком на відповідний файловий дескриптор.
4. На кожному кроці основного циклу:
   - Корінь купи, що містить поточний найменший рядок серед усіх активних файлів, вилучається за час `O(log K)`.
   - Вилучений рядок негайно записується у вихідний потік або файл призначення.
   - З того файлового потоку, звідки надійшов вилучений рядок, зчитується наступний рядок.
   - Новий рядок вставляється в купу, зберігаючи її інваріант. Якщо у файлі більше немає рядків, потік закривається, а розмір купи зменшується.
5. Після повного вичерпання всіх серій тимчасові файли на диску закриваються та негайно видаляються з файлової системи за допомогою системного виклику `unlink()` або функцій `std::filesystem::remove()`.

## 2. Повна реалізація мовами C та C++

Нижче наведено закінчену робочу реалізацію утиліти зовнішнього сортування з підтримкою налаштування розміру буфера пам'яті, автоматичним керуванням тимчасовими файлами та блоковим введенням-виведенням.

:::tabs

@tab C (POSIX / C11)
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>

#define MAX_LINE_LEN 4096
#define DEFAULT_MEM_LIMIT (4 * 1024 * 1024) // 4 MB буфер RAM

typedef struct {
    FILE *file;
    char path[256];
    char current_line[MAX_LINE_LEN];
    int is_active;
} RunStream;

typedef struct {
    RunStream **streams;
    size_t size;
    size_t capacity;
} MinHeap;

static int compare_strings(const void *a, const void *b) {
    const char *sa = *(const char **)a;
    const char *sb = *(const char **)b;
    return strcmp(sa, sb);
}

static void heap_swap(MinHeap *heap, size_t i, size_t j) {
    RunStream *tmp = heap->streams[i];
    heap->streams[i] = heap->streams[j];
    heap->streams[j] = tmp;
}

static void heapify_down(MinHeap *heap, size_t idx) {
    size_t smallest = idx;
    size_t left = 2 * idx + 1;
    size_t right = 2 * idx + 2;

    if (left < heap->size &&
        strcmp(heap->streams[left]->current_line,
               heap->streams[smallest]->current_line) < 0) {
        smallest = left;
    }

    if (right < heap->size &&
        strcmp(heap->streams[right]->current_line,
               heap->streams[smallest]->current_line) < 0) {
        smallest = right;
    }

    if (smallest != idx) {
        heap_swap(heap, idx, smallest);
        heapify_down(heap, smallest);
    }
}

static void heapify_up(MinHeap *heap, size_t idx) {
    while (idx > 0) {
        size_t parent = (idx - 1) / 2;
        if (strcmp(heap->streams[idx]->current_line,
                   heap->streams[parent]->current_line) < 0) {
            heap_swap(heap, idx, parent);
            idx = parent;
        } else {
            break;
        }
    }
}

static void heap_push(MinHeap *heap, RunStream *stream) {
    heap->streams[heap->size] = stream;
    heapify_up(heap, heap->size);
    heap->size++;
}

static RunStream *heap_pop(MinHeap *heap) {
    if (heap->size == 0) return NULL;
    RunStream *root = heap->streams[0];
    heap->streams[0] = heap->streams[heap->size - 1];
    heap->size--;
    if (heap->size > 0) {
        heapify_down(heap, 0);
    }
    return root;
}

static char *write_temp_run(char **lines, size_t count, size_t run_idx) {
    qsort(lines, count, sizeof(char *), compare_strings);

    char *path = malloc(256);
    snprintf(path, 256, "/tmp/extsort_run_%d_%zu.tmp", getpid(), run_idx);

    FILE *out = fopen(path, "w");
    if (!out) {
        perror("Помилка створення тимчасового файлу");
        free(path);
        return NULL;
    }

    for (size_t i = 0; i < count; ++i) {
        fputs(lines[i], out);
        free(lines[i]);
    }
    fclose(out);
    return path;
}

static size_t generate_runs(FILE *in, size_t mem_limit, char ***out_run_paths) {
    size_t run_count = 0;
    size_t run_cap = 16;
    char **run_paths = malloc(run_cap * sizeof(char *));

    size_t lines_cap = 1024;
    char **lines = malloc(lines_cap * sizeof(char *));
    size_t lines_count = 0;
    size_t current_mem = 0;

    char buffer[MAX_LINE_LEN];
    while (fgets(buffer, sizeof(buffer), in)) {
        size_t len = strlen(buffer);
        char *line = strdup(buffer);

        if (lines_count >= lines_cap) {
            lines_cap *= 2;
            lines = realloc(lines, lines_cap * sizeof(char *));
        }
        lines[lines_count++] = line;
        current_mem += len + sizeof(char *);

        if (current_mem >= mem_limit) {
            char *p = write_temp_run(lines, lines_count, run_count);
            if (run_count >= run_cap) {
                run_cap *= 2;
                run_paths = realloc(run_paths, run_cap * sizeof(char *));
            }
            run_paths[run_count++] = p;
            lines_count = 0;
            current_mem = 0;
        }
    }

    if (lines_count > 0) {
        char *p = write_temp_run(lines, lines_count, run_count);
        if (run_count >= run_cap) {
            run_cap *= 2;
            run_paths = realloc(run_paths, run_cap * sizeof(char *));
        }
        run_paths[run_count++] = p;
    }

    free(lines);
    *out_run_paths = run_paths;
    return run_count;
}

static void merge_runs(char **run_paths, size_t run_count, FILE *out) {
    if (run_count == 0) return;

    RunStream *streams = calloc(run_count, sizeof(RunStream));
    MinHeap heap = {
        .streams = malloc(run_count * sizeof(RunStream *)),
        .size = 0,
        .capacity = run_count
    };

    for (size_t i = 0; i < run_count; ++i) {
        strncpy(streams[i].path, run_paths[i], sizeof(streams[i].path) - 1);
        streams[i].file = fopen(streams[i].path, "r");
        if (streams[i].file && fgets(streams[i].current_line, MAX_LINE_LEN, streams[i].file)) {
            streams[i].is_active = 1;
            heap_push(&heap, &streams[i]);
        } else {
            streams[i].is_active = 0;
            if (streams[i].file) fclose(streams[i].file);
        }
    }

    while (heap.size > 0) {
        RunStream *min_stream = heap_pop(&heap);
        fputs(min_stream->current_line, out);

        if (fgets(min_stream->current_line, MAX_LINE_LEN, min_stream->file)) {
            heap_push(&heap, min_stream);
        } else {
            fclose(min_stream->file);
            min_stream->is_active = 0;
        }
    }

    for (size_t i = 0; i < run_count; ++i) {
        unlink(run_paths[i]);
        free(run_paths[i]);
    }

    free(streams);
    free(heap.streams);
    free(run_paths);
}

int main(int argc, char *argv[]) {
    FILE *in = (argc > 1) ? fopen(argv[1], "r") : stdin;
    if (!in) {
        perror("Помилка відкриття вхідного файлу");
        return 1;
    }

    char **run_paths = NULL;
    size_t run_count = generate_runs(in, DEFAULT_MEM_LIMIT, &run_paths);
    if (in != stdin) fclose(in);

    merge_runs(run_paths, run_count, stdout);
    return 0;
}
```

@tab C++ (C++20)
```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <queue>
#include <memory>
#include <algorithm>
#include <filesystem>
#include <unistd.h>

namespace fs = std::filesystem;

class ExternalMergeSort {
public:
    explicit ExternalMergeSort(size_t mem_limit_bytes = 4 * 1024 * 1024)
        : mem_limit_(mem_limit_bytes) {}

    void sort(std::istream& in, std::ostream& out) {
        auto run_files = generate_runs(in);
        merge_runs(run_files, out);
    }

private:
    struct RunStream {
        std::ifstream file;
        fs::path path;
        std::string current_line;

        explicit RunStream(fs::path p) : path(std::move(p)), file(path) {
            advance();
        }

        [[nodiscard]] bool is_valid() const noexcept {
            return !current_line.empty() || file.good();
        }

        bool advance() {
            if (std::getline(file, current_line)) {
                current_line.push_back('\n');
                return true;
            }
            current_line.clear();
            return false;
        }
    };

    struct StreamComparator {
        bool operator()(const std::unique_ptr<RunStream>& a,
                        const std::unique_ptr<RunStream>& b) const {
            return a->current_line > b->current_line; // Мін-купа для вибору найменшого рядка
        }
    };

    std::vector<fs::path> generate_runs(std::istream& in) {
        std::vector<fs::path> run_files;
        std::vector<std::string> buffer;
        size_t current_bytes = 0;
        std::string line;
        size_t run_index = 0;

        auto flush_buffer = [&]() {
            if (buffer.empty()) return;
            std::sort(buffer.begin(), buffer.end());

            fs::path temp_path = fs::temp_directory_path() /
                ("extsort_cpp_" + std::to_string(getpid()) + "_" + std::to_string(run_index++) + ".tmp");

            std::ofstream out(temp_path, std::ios::binary);
            for (const auto& item : buffer) {
                out << item << '\n';
            }

            run_files.push_back(temp_path);
            buffer.clear();
            current_bytes = 0;
        };

        while (std::getline(in, line)) {
            current_bytes += line.size() + sizeof(std::string);
            buffer.push_back(std::move(line));

            if (current_bytes >= mem_limit_) {
                flush_buffer();
            }
        }

        flush_buffer();
        return run_files;
    }

    void merge_runs(const std::vector<fs::path>& run_files, std::ostream& out) {
        if (run_files.empty()) return;

        std::priority_queue<
            std::unique_ptr<RunStream>,
            std::vector<std::unique_ptr<RunStream>>,
            StreamComparator
        > min_heap;

        for (const auto& path : run_files) {
            auto stream = std::make_unique<RunStream>(path);
            if (!stream->current_line.empty()) {
                min_heap.push(std::move(stream));
            }
        }

        while (!min_heap.empty()) {
            auto min_stream = std::move(const_cast<std::unique_ptr<RunStream>&>(min_heap.top()));
            min_heap.pop();

            out << min_stream->current_line;

            if (min_stream->advance()) {
                min_heap.push(std::move(min_stream));
            }
        }

        for (const auto& path : run_files) {
            std::error_code ec;
            fs::remove(path, ec);
        }
    }

    size_t mem_limit_;
};

int main(int argc, char* argv[]) {
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(nullptr);

    ExternalMergeSort sorter(8 * 1024 * 1024); // 8 MB RAM буфер

    if (argc > 1) {
        std::ifstream in(argv[1], std::ios::binary);
        if (!in) {
            std::cerr << "Помилка відкриття файлу: " << argv[1] << '\n';
            return 1;
        }
        sorter.sort(in, std::cout);
    } else {
        sorter.sort(std::cin, std::cout);
    }

    return 0;
}
```

:::

## 3. Критичні деталі системної реалізації

Під час практичного використання та оптимізації зовнішнього сортування необхідно враховувати системні обмеження ядра Linux та апаратні властивості підсистеми введення-виведення:

### 1. Ліміт відкритих дескрипторів файлів (RLIMIT_NOFILE)

Якщо розмір вхідного файлу становить 1 ТБ, а буфер пам'яті обмежено 100 МБ, кількість сформованих серій сягає `K = 10 000`. У стандартній конфігурації Linux ліміт на кількість одночасно відкритих файлових дескрипторів процесу (`ulimit -n`) зазвичай становить 1024.

Спроба відкрити всі `10 000` тимчасових файлів одночасно на початку фази злиття завершиться помилкою `EMFILE (Too many open files)`.

Виробничі реалізації утиліти (зокрема GNU `sort`) розв'язують цю проблему за допомогою **багаторівневого ієрархічного злиття (multi-pass merge)**, керованого параметром `--batch-size`. Замість прямого злиття всіх `K` файлів одночасно утиліта зливає їх групами по 16–32 файли у нові проміжні тимчасові серії вищого рівня, зменшуючи кількість відкритих дескрипторів до безпечного значення.

### 2. Буферизація введення-виведення та системні виклики

Читання та запис по одному рядку або по одному байту створюють колосальне навантаження перемиканням контексту між простором користувача та простором ядра під час системних викликів `read()` та `write()`.

Для досягнення високої пропускної здатності необхідно використовувати буферизацію розміром від 64 КБ до 1 МБ на кожен відкритий дескриптор. У мові C це досягається функцією `setvbuf()`, а в C++ — налаштуванням розміру буферів `std::filebuf`. Такий підхід узгоджується з розміром сторінок дискового кешу ядра Linux (VFS Page Cache) та максимізує послідовну швидкість читання накопичувача.

### 3. Очищення тимчасових файлів при аварійному перериванні

Оскільки під час роботи можуть створюватися десятки гігабайтів тимчасових даних, аварійне переривання процесу (наприклад, натискання комбінації `Ctrl+C` у терміналі або сигнал `SIGTERM` від системи моніторингу) може призвести до засмічення каталогу `/tmp`. Промисловий код обов'язково реєструє обробники сигналів через `sigaction()`, які гарантовано викликають `unlink()` для всіх зареєстрованих тимчасових файлів перед завершенням процесу.
