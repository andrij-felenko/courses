# ⚙️ Надійний розбір аргументів командного рядка: від C до ідіоматичного C++

Коли програма приймає параметри командного рядка, спроба розібрати масив рядків `argv` вручну за допомогою саморобних циклів `for` та викликів `strcmp` швидко перетворюється на джерело критичних дефектів безпеки та нестабільної поведінки. Ручний розбір майже завжди втрачає підтримку групування коротких прапорців (як-от `-xvf`), плутає передачу параметрів через знак рівності `--file=name` із передачею через пробіл `--file name`, некоректно обробляє захисний маркер завершення опцій `--` і видає незрозумілі повідомлення про помилки. У цьому практичному проекті розглядається побудова повнофункціонального, безпечного та стандартизованого парсера параметрів командного рядка на мовах C та C++20.

## Архітектурні вимоги до інтерфейсу утиліти

Сучасна утиліта командного рядка повинна суворо відповідати домовленостям POSIX та розширенням GNU. Наша програма для потокової обробки файлів реалізує такий набір вимог:

1. **Короткі прапорці без аргументів:**
   - Прапорець `-v` активує режим розширеного журналювання (*verbose mode*).
   - Прапорець `-q` вмикає тихий режим (*quiet mode*), пригнічуючи будь-які попередження.
   - Обидва прапорці є взаємовиключними: одночасне вказання `-v -q` повинно викликати помилку валідації.
2. **Короткі опції з аргументами:**
   - Опція `-o <file>` задає шлях до цільового файлу виводу. Парсер повинен підтримувати як роздільний запис `-o output.bin`, так і злитий `-ooutput.bin`.
   - Опція `-b <bytes>` задає розмір внутрішнього буфера обробки в байтах. Парсер повинен виконувати сувору числову валідацію рядка.
3. **Групування коротких прапорців:**
   - Користувач може вводити прапорці разом: виклик `-vq` еквівалентний `-v -q`, а комбінація `-vo out.txt` еквівалентна послідовності `-v -o out.txt`.
4. **Довгі описові опції GNU:**
   - Підтримка парних довгих опцій: `--verbose`, `--quiet`, `--output=<file>`, `--buffer=<bytes>`, `--help`, `--version`.
5. **Опції з опціональним значенням:**
   - Опція `--color[=WHEN]` дозволяє вмикати підсвічування консольного виводу. За замовчуванням діє режим `auto`, користувач може явно передати `always` або `never`.
6. **Маркер захисту від ін'єкцій `--`:**
   - Будь-які аргументи, що слідують після окремого токена `--`, розглядаються суто як імена файлів, навіть якщо вони починаються з символу дефіса (наприклад, `-- -file.txt`).
7. **Стандартизовані коди завершення процесу:**
   - Повернення `0` при успішній обробці або запиті довідки (`--help` / `--version`).
   - Повернення `2` при будь-якій помилці синтаксису параметрів або неправильному типі аргументів.

## Реалізація на мовах C та C++

У мові C стандартом де-факто для системних утиліт Linux є бібліотечна функція `getopt_long()` із заголовка `<getopt.h>`. У C++20 ми відмовляємося від глобальних мутабельних вказівників на користь типобезпечної інкапсуляції зі структурами даних `std::string_view`, `std::span`, `std::optional` та безалокаційного розбору чисел через `std::from_chars`.

:::tabs
```c
/* cli_parser.c — реалізація на C з використанням POSIX/GNU getopt_long */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>
#include <stdbool.h>

#define PROGRAM_NAME "fileproc"
#define PROGRAM_VERSION "1.4.0"

typedef struct {
    bool verbose;
    bool quiet;
    const char *output_file;
    size_t buffer_size;
    const char *color_mode;
    char **input_files;
    int input_file_count;
} Config;

static void print_version(FILE *out) {
    fprintf(out, "%s version %s\n", PROGRAM_NAME, PROGRAM_VERSION);
    fprintf(out, "Copyright (C) 2026 Open Systems Foundation.\n");
    fprintf(out, "License: MIT (free and open source software).\n");
}

static void print_help(FILE *out) {
    fprintf(out, "Usage: %s [OPTION]... [FILE]...\n", PROGRAM_NAME);
    fprintf(out, "Process input files with customizable buffering and formatting.\n\n");

    fprintf(out, "Main operation mode:\n");
    fprintf(out, "  -o, --output=FILE       write processed data to FILE [default: stdout]\n");
    fprintf(out, "  -b, --buffer=BYTES      set processing buffer size in bytes [default: 4096]\n");
    fprintf(out, "      --color[=WHEN]      colorize console output; WHEN can be 'always',\n");
    fprintf(out, "                            'never', or 'auto' [default: auto]\n\n");

    fprintf(out, "Diagnostic and verbosity options:\n");
    fprintf(out, "  -v, --verbose           print detailed processing diagnostics\n");
    fprintf(out, "  -q, --quiet             suppress all warning and diagnostic messages\n\n");

    fprintf(out, "Informational options:\n");
    fprintf(out, "  -h, --help              display this help and exit\n");
    fprintf(out, "  -V, --version           output version information and exit\n\n");

    fprintf(out, "With no FILE, or when FILE is -, read standard input.\n");
    fprintf(out, "Exit status: 0 if OK, 1 if minor problems, 2 if serious trouble / invalid syntax.\n");
}

static bool parse_cli_options(int argc, char *argv[], Config *cfg) {
    /* Очищення структури за замовчуванням */
    cfg->verbose = false;
    cfg->quiet = false;
    cfg->output_file = NULL;
    cfg->buffer_size = 4096;
    cfg->color_mode = "auto";
    cfg->input_files = NULL;
    cfg->input_file_count = 0;

    static const char *short_opts = "o:b:vqhV";
    static const struct option long_opts[] = {
        {"output",   required_argument, NULL, 'o'},
        {"buffer",   required_argument, NULL, 'b'},
        {"color",    optional_argument, NULL, 'c'},
        {"verbose",  no_argument,       NULL, 'v'},
        {"quiet",    no_argument,       NULL, 'q'},
        {"help",     no_argument,       NULL, 'h'},
        {"version",  no_argument,       NULL, 'V'},
        {NULL, 0, NULL, 0}
    };

    int opt;
    while ((opt = getopt_long(argc, argv, short_opts, long_opts, NULL)) != -1) {
        switch (opt) {
            case 'o':
                cfg->output_file = optarg;
                break;
            case 'b': {
                char *endptr = NULL;
                long val = strtol(optarg, &endptr, 10);
                if (*endptr != '\0' || val <= 0) {
                    fprintf(stderr, "%s: invalid buffer size '%s'\n", PROGRAM_NAME, optarg);
                    fprintf(stderr, "Try '%s --help' for more information.\n", PROGRAM_NAME);
                    exit(2);
                }
                cfg->buffer_size = (size_t)val;
                break;
            }
            case 'c':
                if (optarg) {
                    if (strcmp(optarg, "always") != 0 &&
                        strcmp(optarg, "never") != 0 &&
                        strcmp(optarg, "auto") != 0) {
                        fprintf(stderr, "%s: unrecognized color mode '%s'\n", PROGRAM_NAME, optarg);
                        fprintf(stderr, "Try '%s --help' for more information.\n", PROGRAM_NAME);
                        exit(2);
                    }
                    cfg->color_mode = optarg;
                } else {
                    cfg->color_mode = "always";
                }
                break;
            case 'v':
                cfg->verbose = true;
                break;
            case 'q':
                cfg->quiet = true;
                break;
            case 'h':
                print_help(stdout);
                exit(0);
            case 'V':
                print_version(stdout);
                exit(0);
            case '?':
            default:
                /* getopt_long сам друкує опис невідомої опції у stderr */
                fprintf(stderr, "Try '%s --help' for more information.\n", PROGRAM_NAME);
                exit(2);
        }
    }

    if (cfg->verbose && cfg->quiet) {
        fprintf(stderr, "%s: options --verbose and --quiet are mutually exclusive\n", PROGRAM_NAME);
        exit(2);
    }

    /* Усі елементи argv після optind — позиційні операнди (імена файлів) */
    cfg->input_file_count = argc - optind;
    if (cfg->input_file_count > 0) {
        cfg->input_files = &argv[optind];
    }

    return true;
}

int main(int argc, char *argv[]) {
    Config cfg;
    parse_cli_options(argc, argv, &cfg);

    if (cfg.verbose) {
        printf("[DEBUG] Буфер: %zu байт, Колір: %s, Вивід: %s\n",
               cfg.buffer_size, cfg.color_mode,
               cfg.output_file ? cfg.output_file : "<stdout>");
        printf("[DEBUG] Вхідних файлів для обробки: %d\n", cfg.input_file_count);
    }

    /* Якщо файлів не передано, обробляємо стандартний ввід */
    if (cfg.input_file_count == 0) {
        if (!cfg.quiet) printf("Читання даних зі стандартного вводу (stdin)...\n");
    } else {
        for (int i = 0; i < cfg.input_file_count; ++i) {
            if (!cfg.quiet) printf("Обробка файлу: %s\n", cfg.input_files[i]);
        }
    }

    return 0;
}
```
```cpp
// cli_parser.cpp — ідіоматична реалізація на C++20
#include <iostream>
#include <string_view>
#include <vector>
#include <optional>
#include <span>
#include <charconv>
#include <cstdlib>
#include <getopt.h>

namespace cli {

struct Config {
    bool verbose{false};
    bool quiet{false};
    std::optional<std::string_view> output_file{};
    std::size_t buffer_size{4096};
    std::string_view color_mode{"auto"};
    std::vector<std::string_view> input_files{};
};

class ProgramInfo {
public:
    static constexpr std::string_view Name{"fileproc"};
    static constexpr std::string_view Version{"1.4.0"};

    static void print_version(std::ostream &os = std::cout) noexcept {
        os << Name << " version " << Version << "\n"
           << "Copyright (C) 2026 Open Systems Foundation.\n"
           << "License: MIT (free and open source software).\n";
    }

    static void print_help(std::ostream &os = std::cout) noexcept {
        os << "Usage: " << Name << " [OPTION]... [FILE]...\n"
           << "Process input files with customizable buffering and formatting.\n\n"
           << "Main operation mode:\n"
           << "  -o, --output=FILE       write processed data to FILE [default: stdout]\n"
           << "  -b, --buffer=BYTES      set processing buffer size in bytes [default: 4096]\n"
           << "      --color[=WHEN]      colorize console output; WHEN can be 'always',\n"
           << "                            'never', or 'auto' [default: auto]\n\n"
           << "Diagnostic and verbosity options:\n"
           << "  -v, --verbose           print detailed processing diagnostics\n"
           << "  -q, --quiet             suppress all warning and diagnostic messages\n\n"
           << "Informational options:\n"
           << "  -h, --help              display this help and exit\n"
           << "  -V, --version           output version information and exit\n\n"
           << "With no FILE, or when FILE is -, read standard input.\n"
           << "Exit status: 0 if OK, 1 if minor problems, 2 if serious trouble / invalid syntax.\n";
    }
};

class CommandLineParser {
public:
    static Config parse(std::span<char *> args) {
        Config cfg;
        const int argc = static_cast<int>(args.size());
        char **argv = args.data();

        // Скидаємо глобальний індекс для повторних запусків
        optind = 1;

        static constexpr const char *short_opts = "o:b:vqhV";
        static constexpr option long_opts[] = {
            {"output",   required_argument, nullptr, 'o'},
            {"buffer",   required_argument, nullptr, 'b'},
            {"color",    optional_argument, nullptr, 'c'},
            {"verbose",  no_argument,       nullptr, 'v'},
            {"quiet",    no_argument,       nullptr, 'q'},
            {"help",     no_argument,       nullptr, 'h'},
            {"version",  no_argument,       nullptr, 'V'},
            {nullptr, 0, nullptr, 0}
        };

        int opt;
        while ((opt = getopt_long(argc, argv, short_opts, long_opts, nullptr)) != -1) {
            switch (opt) {
                case 'o':
                    cfg.output_file = std::string_view{optarg};
                    break;
                case 'b': {
                    std::string_view sv{optarg};
                    std::size_t val = 0;
                    auto [ptr, ec] = std::from_chars(sv.data(), sv.data() + sv.size(), val);
                    if (ec != std::errc{} || ptr != sv.data() + sv.size() || val == 0) {
                        std::cerr << ProgramInfo::Name << ": invalid buffer size '" << sv << "'\n"
                                  << "Try '" << ProgramInfo::Name << " --help' for more information.\n";
                        std::exit(2);
                    }
                    cfg.buffer_size = val;
                    break;
                }
                case 'c':
                    if (optarg) {
                        std::string_view mode{optarg};
                        if (mode != "always" && mode != "never" && mode != "auto") {
                            std::cerr << ProgramInfo::Name << ": unrecognized color mode '" << mode << "'\n"
                                      << "Try '" << ProgramInfo::Name << " --help' for more information.\n";
                            std::exit(2);
                        }
                        cfg.color_mode = mode;
                    } else {
                        cfg.color_mode = "always";
                    }
                    break;
                case 'v':
                    cfg.verbose = true;
                    break;
                case 'q':
                    cfg.quiet = true;
                    break;
                case 'h':
                    ProgramInfo::print_help(std::cout);
                    std::exit(0);
                case 'V':
                    ProgramInfo::print_version(std::cout);
                    std::exit(0);
                case '?':
                default:
                    std::cerr << "Try '" << ProgramInfo::Name << " --help' for more information.\n";
                    std::exit(2);
            }
        }

        if (cfg.verbose && cfg.quiet) {
            std::cerr << ProgramInfo::Name << ": options --verbose and --quiet are mutually exclusive\n";
            std::exit(2);
        }

        for (int i = optind; i < argc; ++i) {
            cfg.input_files.emplace_back(argv[i]);
        }

        return cfg;
    }
};

} // namespace cli

int main(int argc, char *argv[]) {
    const auto cfg = cli::CommandLineParser::parse(std::span(argv, argc));

    if (cfg.verbose) {
        std::cout << "[DEBUG] Буфер: " << cfg.buffer_size
                  << " байт, Колір: " << cfg.color_mode
                  << ", Вивід: " << cfg.output_file.value_or("<stdout>") << "\n"
                  << "[DEBUG] Вхідних файлів для обробки: " << cfg.input_files.size() << "\n";
    }

    if (cfg.input_files.empty()) {
        if (!cfg.quiet) std::cout << "Читання даних зі стандартного вводу (stdin)...\n";
    } else {
        for (const auto &file : cfg.input_files) {
            if (!cfg.quiet) std::cout << "Обробка файлу: " << file << "\n";
        }
    }

    return 0;
}
```
:::

## Аналіз життєвого циклу пам'яті та керування станом

У системному програмуванні на C вказівник `optarg` посилається безпосередньо на відрізок пам'яті всередині масиву `argv`. Оскільки рядки `argv` завантажуються ядром операційної системи в стек процесу під час виконання системного виклику `execve()`, вони залишаються дійсними протягом усього часу життя програми. Тому збереження вказівника `const char *output_file = optarg` не вимагає динамічного виділення пам'яті через `malloc()`, але вимагає дисципліни: ці рядки не можна модифікувати або звільняти через `free()`.

У версії на C++20 замість копіювання в об'єкти `std::string` використовується `std::string_view`. Це забезпечує нульові накладні витрати на динамічну алокацію пам'яті (*zero-copy parsing*), гарантуючи при цьому сучасний безпечний інтерфейс роботи з рядками. Використання функції `std::from_chars` для числової конвертації гарантує повну незалежність від поточних регіональних налаштувань (*locale-independent parsing*) та захищає процес від виходу за межі пам'яті чи неозначеної поведінки при переповненні цілих чисел.

## Проблема реентерабельності та потокобезпечності

Класичний C API `getopt_long()` спирається на глобальний стан бібліотеки `glibc` (змінні `optind`, `optarg`, `opterr`, `optopt`). Через це функція **не є потокобезпечною** (*non-reentrant* / *not thread-safe*). Якщо два фонових потоки спробують одночасно парсити різні масиви аргументів, стан парсера буде миттєво зруйновано.

Для забезпечення надійності в багатопотокових сервісах діють такі правила:
1. Розбір параметрів командного рядка завжди виконується **виключно в головному потоці** процесу під час ініціалізації функції `main()`, до створення будь-яких додаткових потоків `pthread_create()` чи `std::jthread`.
2. Результат розбору записується в незмінну конфігураційну структуру (як наш об'єкт `Config`), доступ до якої з робочих потоків відбувається суворо за константними посиланнями у режимі лише для читання.
3. Для повторного виклику парсера (наприклад, у тестах або вбудованих оболонках) змінну `optind` необхідно примусово скидати в значення `1` перед кожним новим циклом сканування масиву `argv`.

## Валідація крайових випадків та стрес-тестування

Розроблений парсер перевіряється на типових крайових сценаріях вводу в системному терміналі:

### 1. Групування коротких опцій та склеювання параметрів
Користувач може записати команду трьома різними способами:
```bash
./fileproc -v -o out.bin file1.txt
./fileproc -vo out.bin file1.txt
./fileproc -voout.bin file1.txt
```
Усі три варіанти сприймаються парсером абсолютно однаково: вмикається діагностика `verbose = true`, ім'я вихідного файлу встановлюється в `out.bin`, а файл `file1.txt` потрапляє до списку позиційних операндів.

### 2. Захист від ін'єкцій через імена файлів із дефісом
Коли у файловій системі створено файл із назвою `-strange-name.txt`, виклик без розділювача призведе до спроби розпізнати `-s` як прапорець:
```bash
./fileproc -v -- -strange-name.txt -another.txt
```
Завдяки наявності маркера `--` парсер негайно перериває обробку прапорців. Обидва рядки потрапляють до масиву вхідних файлів без виникнення помилок розбору.

### 3. Обробка опціональних параметрів
```bash
./fileproc --color           # вмикає режим 'always'
./fileproc --color=never     # вмикає режим 'never'
```
Якщо викликати `./fileproc --color never`, слово `never` буде трактовано парсером як ім'я першого позиційного файлу для обробки, а кольори залишаться увімкненими в режимі `always`. Ця поведінка повністю відповідає специфікації GNU Long Options.
