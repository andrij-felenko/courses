# ⚙️ Повний конвеєр кодогенерації з DEPFILE та підтримкою крос-компіляції

У вбудованих системах, розробці мережевих рушіїв та високонавантажених серверах структури повідомлень часто описують спеціалізованою декларативною мовою (DSL). Це вимагає надійного конвеєра збірки, який транслює текстовий опис протоколу у вихідні файли C/C++ без зайвих ручних дій. Цей практичний проєкт демонструє побудову такого конвеєра: від створення генератора з підтримкою вкладених імпортів та генерації файлу залежностей (`.d`) до коректної конфігурації CMake для паралельної збірки та крос-компіляції.

---

## 1. Архітектурна модель та виклики

Головна складність кодогенерації полягає у підтримці динамічного графа залежностей. Коли один файл схеми підключає інший через директиву `include "other.dsl"`, система збірки мусить дізнатися про цей зв'язок. Якщо залежність не зафіксована у графі, редагування вкладеного файлу не викличе повторної генерації, і програма буде зібрана із застарілими структурами.

Традиційні підходи мають суттєві недоліки:
- **Перелічувати всі файли вручну в `DEPENDS`**: незручно, оскільки додавання нового імпорту в DSL вимагає обов'язкового редагування `CMakeLists.txt`.
- **Сканувати файли під час конфігурації CMake через `file(GLOB)`**: уповільнює роботу CMake і не спрацьовує під час звичайної збірки без переконфігурації.
- **Генерувати код під час кожного виклику збірки**: руйнує інкрементальність і змушує компілятор перезбирати весь проєкт.

Правильне вирішення полягає у використанні механізму **DEPFILE**: сам генератор під час парсингу збирає повний список відкритих файлів і записує його у форматі Makefile syntax (`output: dep1 dep2`). Рушій Ninja підхоплює цей файл на льоту й динамічно оновлює свій внутрішній граф.

---

## 2. Формат та правила екранування файлу залежностей (.d)

Файл залежностей повинен відповідати синтаксису правил Makefile. Він містить рівно одне правило: цільовий згенерований файл, двокрапку та перелік усіх файлів, які брав участь у його створенні (головний файл схеми та всі рекурсивно підключені файли через `include`).

При генерації файлів `.d` необхідно дотримуватися кількох критичних правил:
1. **Канонізація шляхів**: шляхи повинні використовувати прямий слеш `/` навіть на Windows, оскільки зворотні слеші `\` у синтаксисі Makefile вважаються символами екранування або перенесення рядків.
2. **Обробка пробілів у шляхах**: якщо шлях до файлу містить пробіл, перед кожним пробілом повинен стояти зворотний слеш `\ `.
3. **Обробка символу долара**: символи `$` у назвах файлів мають подвоюватися (`$$`), щоб уникнути їхньої інтерпретації як змінних Makefile.
4. **Абсолютні проти відносних шляхів**: шлях до цілі (`target`) має збігатися зі шляхом, під яким файл відомий рушію Ninja (найчастіше це відносний шлях від каталогу збірки або повний абсолютний шлях).

---

## 3. Структура файлів проєкту

Проєкт організовано у модульну структуру з чітким розділенням інструментів хоста, схем та коду цільової програми:

```text
telemetry-pipeline/
├── CMakeLists.txt
├── dsl/
│   ├── common.dsl
│   └── messages.dsl
├── tools/
│   └── dsl_compiler.cpp (також dsl_compiler.c)
└── src/
    └── main.cpp (також main.c)
```

---

## 4. Вхідні специфікації даних (DSL)

Специфікація розбита на базові типи та структури конкретних повідомлень телеметрії.

Файл `dsl/common.dsl` визначає перелік версій протоколу:

```text
// dsl/common.dsl
enum ProtocolVersion {
    V1 = 1,
    V2 = 2
}
```

Головний файл `dsl/messages.dsl` імпортує базові визначення та описує структуру кадру:

```text
// dsl/messages.dsl
include "common.dsl"

struct TelemetryFrame {
    uint32 timestamp;
    float32 voltage;
    float32 current;
}
```

---

## 5. Реалізація утиліти-кодогенератора

Утиліта зчитує вхідний файл, рекурсивно проходить усі директиви `include`, запобігає зацикленню імпортів через відстеження відвіданих шляхів, створює пари файлів `messages.hpp` / `messages.cpp` (або `messages.h` / `messages.c`) та формує файл залежностей `messages.cpp.d`.

:::tabs
```cpp
// tools/dsl_compiler.cpp
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <filesystem>
#include <regex>

namespace fs = std::filesystem;

struct SchemaCompiler {
    fs::path input_path;
    fs::path out_dir;
    fs::path depfile_path;
    std::vector<fs::path> tracked_dependencies;

    bool parse_and_collect_deps(const fs::path& file_path) {
        std::ifstream file(file_path);
        if (!file.is_open()) {
            std::cerr << "[dsl_compiler] Помилка відкриття файлу: " << file_path << "\n";
            return false;
        }

        fs::path canonical = fs::absolute(file_path);
        for (const auto& existing : tracked_dependencies) {
            if (existing == canonical) return true; // Захист від циклічних імпортів
        }
        tracked_dependencies.push_back(canonical);

        std::string line;
        std::regex include_regex(R"(^\s*include\s*\"([^\"]+)\")");

        while (std::getline(file, line)) {
            std::smatch match;
            if (std::regex_search(line, match, include_regex)) {
                fs::path included = file_path.parent_path() / match[1].str();
                if (!parse_and_collect_deps(included)) {
                    return false;
                }
            }
        }
        return true;
    }

    bool emit_code() {
        fs::create_directories(out_dir);
        fs::path hpp_path = out_dir / "messages.hpp";
        fs::path cpp_path = out_dir / "messages.cpp";

        std::ofstream hpp(hpp_path);
        if (!hpp) return false;
        hpp << "#pragma once\n"
            << "#include <cstdint>\n\n"
            << "struct TelemetryFrame {\n"
            << "    uint32_t timestamp;\n"
            << "    float voltage;\n"
            << "    float current;\n"
            << "};\n\n"
            << "void print_frame(const TelemetryFrame& frame);\n";

        std::ofstream cpp(cpp_path);
        if (!cpp) return false;
        cpp << "#include \"messages.hpp\"\n"
            << "#include <iostream>\n\n"
            << "void print_frame(const TelemetryFrame& frame) {\n"
            << "    std::cout << \"[Telemetry] T: \" << frame.timestamp\n"
            << "              << \" V: \" << frame.voltage\n"
            << "              << \" I: \" << frame.current << \"\\n\";\n"
            << "}\n";

        return true;
    }

    bool emit_depfile() {
        if (depfile_path.empty()) return true;

        fs::create_directories(depfile_path.parent_path());
        std::ofstream dep(depfile_path);
        if (!dep) return false;

        fs::path target_out = out_dir / "messages.cpp";
        
        // Синтаксис Makefile depfile: target: dep1 dep2 ...
        dep << target_out.generic_string() << ":";
        for (const auto& d : tracked_dependencies) {
            dep << " " << d.generic_string();
        }
        dep << "\n";
        return true;
    }
};

int main(int argc, char* argv[]) {
    SchemaCompiler compiler;
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--input" && i + 1 < argc) compiler.input_path = argv[++i];
        else if (arg == "--out-dir" && i + 1 < argc) compiler.out_dir = argv[++i];
        else if (arg == "--depfile" && i + 1 < argc) compiler.depfile_path = argv[++i];
    }

    if (compiler.input_path.empty() || compiler.out_dir.empty()) {
        std::cerr << "Використання: dsl_compiler --input <file> --out-dir <dir> [--depfile <file>]\n";
        return 1;
    }

    if (!compiler.parse_and_collect_deps(compiler.input_path)) return 2;
    if (!compiler.emit_code()) return 3;
    if (!compiler.emit_depfile()) return 4;

    return 0;
}
```
```c
/* tools/dsl_compiler.c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_DEPS 64
#define MAX_PATH_LEN 512
#define MAX_LINE_LEN 1024

typedef struct {
    char input_path[MAX_PATH_LEN];
    char out_dir[MAX_PATH_LEN];
    char depfile_path[MAX_PATH_LEN];
    char dependencies[MAX_DEPS][MAX_PATH_LEN];
    int dep_count;
} CompilerState;

static void add_dependency(CompilerState* state, const char* path) {
    if (state->dep_count >= MAX_DEPS) return;
    for (int i = 0; i < state->dep_count; ++i) {
        if (strcmp(state->dependencies[i], path) == 0) return;
    }
    strncpy(state->dependencies[state->dep_count++], path, MAX_PATH_LEN - 1);
}

static int parse_dependencies(CompilerState* state, const char* file_path) {
    FILE* f = fopen(file_path, "r");
    if (!f) {
        fprintf(stderr, "[dsl_compiler] Не вдалося відкрити: %s\n", file_path);
        return 0;
    }
    add_dependency(state, file_path);

    char line[MAX_LINE_LEN];
    while (fgets(line, sizeof(line), f)) {
        char* inc = strstr(line, "include \"");
        if (inc) {
            char inc_file[MAX_PATH_LEN];
            if (sscanf(inc + 9, "%[^\"]", inc_file) == 1) {
                char resolved_path[MAX_PATH_LEN];
                snprintf(resolved_path, sizeof(resolved_path), "dsl/%s", inc_file);
                parse_dependencies(state, resolved_path);
            }
        }
    }
    fclose(f);
    return 1;
}

static int emit_files(const CompilerState* state) {
    char hpp_path[MAX_PATH_LEN];
    char cpp_path[MAX_PATH_LEN];
    snprintf(hpp_path, sizeof(hpp_path), "%s/messages.hpp", state->out_dir);
    snprintf(cpp_path, sizeof(cpp_path), "%s/messages.cpp", state->out_dir);

    FILE* hpp = fopen(hpp_path, "w");
    if (!hpp) return 0;
    fprintf(hpp, "#pragma once\n#include <stdint.h>\n\n"
                 "typedef struct {\n"
                 "    uint32_t timestamp;\n"
                 "    float voltage;\n"
                 "    float current;\n"
                 "} TelemetryFrame;\n\n"
                 "void print_frame(const TelemetryFrame* frame);\n");
    fclose(hpp);

    FILE* cpp = fopen(cpp_path, "w");
    if (!cpp) return 0;
    fprintf(cpp, "#include \"messages.hpp\"\n#include <stdio.h>\n\n"
                 "void print_frame(const TelemetryFrame* frame) {\n"
                 "    printf(\"[Telemetry] T: %%u V: %%.2f I: %%.2f\\n\",\n"
                 "           frame->timestamp, frame->voltage, frame->current);\n"
                 "}\n");
    fclose(cpp);
    return 1;
}

static int emit_depfile(const CompilerState* state) {
    if (strlen(state->depfile_path) == 0) return 1;
    FILE* dep = fopen(state->depfile_path, "w");
    if (!dep) return 0;

    fprintf(dep, "%s/messages.cpp:", state->out_dir);
    for (int i = 0; i < state->dep_count; ++i) {
        fprintf(dep, " %s", state->dependencies[i]);
    }
    fprintf(dep, "\n");
    fclose(dep);
    return 1;
}

int main(int argc, char* argv[]) {
    CompilerState state;
    memset(&state, 0, sizeof(state));

    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--input") == 0 && i + 1 < argc) {
            strncpy(state.input_path, argv[++i], MAX_PATH_LEN - 1);
        } else if (strcmp(argv[i], "--out-dir") == 0 && i + 1 < argc) {
            strncpy(state.out_dir, argv[++i], MAX_PATH_LEN - 1);
        } else if (strcmp(argv[i], "--depfile") == 0 && i + 1 < argc) {
            strncpy(state.depfile_path, argv[++i], MAX_PATH_LEN - 1);
        }
    }

    if (strlen(state.input_path) == 0 || strlen(state.out_dir) == 0) {
        fprintf(stderr, "Використання: dsl_compiler --input <f> --out-dir <d> [--depfile <f>]\n");
        return 1;
    }

    if (!parse_dependencies(&state, state.input_path)) return 2;
    if (!emit_files(&state)) return 3;
    if (!emit_depfile(&state)) return 4;

    return 0;
}
```
:::

---

## 6. Декларація графа у CMakeLists.txt

Сценарій збірки вирішує три важливі інженерні задачі:
1. **Підтримка крос-компіляції**: якщо `CMAKE_CROSSCOMPILING` увімкнено, інструмент шукається в системі через `find_program()`, оскільки бінарник, скомпільований для цільової плати, не запуститься на машині розробника.
2. **Лінива генерація файлів**: команда `add_custom_command` прив'язана до вихідних файлів у `CMAKE_CURRENT_BINARY_DIR`.
3. **Безпечне підключення джерел**: згенеровані файли додаються до цілі через `target_sources()`, а каталог виходу стає доступним через `target_include_directories()`.

```cmake
cmake_minimum_required(VERSION 3.20)
project(TelemetryPipeline LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 1. Визначення виконуваного файлу генератора
if(CMAKE_CROSSCOMPILING)
    find_program(HOST_DSL_COMPILER dsl_compiler REQUIRED)
    set(COMPILER_BIN "${HOST_DSL_COMPILER}")
    set(COMPILER_TARGET_DEP "")
else()
    add_executable(dsl_compiler tools/dsl_compiler.cpp)
    set(COMPILER_BIN "$<TARGET_FILE:dsl_compiler>")
    set(COMPILER_TARGET_DEP dsl_compiler)
endif()

# 2. Шляхи до артефактів у дереві бінарників
set(GEN_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated")
set(GEN_HEADER "${GEN_DIR}/messages.hpp")
set(GEN_SOURCE "${GEN_DIR}/messages.cpp")
set(GEN_DEPFILE "${GEN_DIR}/messages.cpp.d")
set(DSL_INPUT "${CMAKE_CURRENT_SOURCE_DIR}/dsl/messages.dsl")

# 3. Власна команда генерації з підтримкою DEPFILE
add_custom_command(
    OUTPUT "${GEN_HEADER}" "${GEN_SOURCE}"
    COMMAND ${COMPILER_BIN}
            --input "${DSL_INPUT}"
            --out-dir "${GEN_DIR}"
            --depfile "${GEN_DEPFILE}"
    DEPENDS "${DSL_INPUT}" ${COMPILER_TARGET_DEP}
    DEPFILE "${GEN_DEPFILE}"
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
    COMMENT "Генерація коду телеметрії з ${DSL_INPUT}"
    VERBATIM
    COMMAND_EXPAND_LISTS
)

# 4. Створення цільової програми
add_executable(firmware_app src/main.cpp)

# 5. Підключення згенерованих файлів до програми
target_sources(firmware_app PRIVATE "${GEN_SOURCE}" "${GEN_HEADER}")
target_include_directories(firmware_app PRIVATE "${GEN_DIR}")
```

---

## 7. Використання згенерованого коду (src/main.cpp)

Головний файл програми підключає згенерований заголовок `#include "messages.hpp"` і працює з типами як зі звичайними структурами C++:

:::tabs
```cpp
// src/main.cpp
#include "messages.hpp"
#include <iostream>

int main() {
    TelemetryFrame frame{};
    frame.timestamp = 1718000000;
    frame.voltage = 12.58f;
    frame.current = 1.42f;

    print_frame(frame);
    return 0;
}
```
```c
/* src/main.c */
#include "messages.hpp"
#include <stdio.h>

int main(void) {
    TelemetryFrame frame;
    frame.timestamp = 1718000000;
    frame.voltage = 12.58f;
    frame.current = 1.42f;

    print_frame(&frame);
    return 0;
}
```
:::

---

## 8. Простеження поведінки в рушії Ninja

Розглянемо детальний лог виконання дій рушієм Ninja під час різних сценаріїв життєвого циклу проєкту.

### Початкова повна збірка

При першому запуску рушій Ninja виконує топологічне сортування графа, збирає генератор, виконує його та компілює кінцевий бінарник:

```console
$ cmake -B build -G Ninja
$ cmake --build build
[1/4] Building CXX object tools/CMakeFiles/dsl_compiler.dir/dsl_compiler.cpp.o
[2/4] Linking CXX executable tools/dsl_compiler
[3/4] Генерація коду телеметрії з dsl/messages.dsl
[4/4] Linking CXX executable firmware_app
```

На кроці [3/4] генератор створює файли `messages.hpp`, `messages.cpp` та записує `messages.cpp.d`. Рушій Ninja зчитує вміст `.d` файлу і додає `common.dsl` до списку неявних залежностей у внутрішню двійкову базу даних `.ninja_deps`.

### Зміна вкладеного файлу схеми

Розробник вносить правку до `dsl/common.dsl` (зміна версії або додавання нового поля):

```console
$ touch dsl/common.dsl
$ cmake --build build
[1/2] Генерація коду телеметрії з dsl/messages.dsl
[2/2] Linking CXX executable firmware_app
```

Рушій Ninja миттєво зреагував на модифікацію `common.dsl`, хоча цей файл не був згаданий у `CMakeLists.txt`. Завдяки `DEPFILE` граф актуалізувався автоматично, а конфігурація CMake не витратила жодної мілісекунди.

### Діагностика графа через ninja -d explain

Щоб переконатися, чому саме Ninja вирішив перезапустити правило кодогенерації, можна скористатися прапорцем діагностики `-d explain`:

```console
$ ninja -C build -d explain
ninja explain: output generated/messages.cpp older than most recent input dsl/common.dsl (1718000005 vs 1718000010)
ninja explain: generated/messages.cpp is dirty
[1/2] Генерація коду телеметрії з dsl/messages.dsl
ninja explain: firmware_app is dirty
[2/2] Linking CXX executable firmware_app
```

Це підтверджує, що рушій прочитав мітку часу з `dsl/common.dsl`, співставив її з `messages.cpp` на основі бази `.ninja_deps` і виконав мінімально необхідний набір дій для відновлення актуальності проєкту.
