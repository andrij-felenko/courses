// extension.cpp — точка входу модуля fast_tools у C++-варіанті: глобальний
// стан API, таблиця функцій і рукостискання dl_load().
//
// Збірка:
//   g++ -fPIC -shared -O3 -Wall -Wextra -std=c++17 -I/usr/include/gawk \
//       -o fast_tools.so extension.cpp builtins.cpp
#include <gawkapi.h>

#include <cstdio>
#include <string_view>

#include "api.hpp"
#include "builtins.hpp"

// Єдине визначення на всю бібліотеку — решта файлів бачить їх через extern
// в api.hpp. Ініціалізація нулями важлива: якщо якийсь конструктор глобального
// об'єкта смикне API до dl_load(), падіння буде на нульовому вказівнику,
// а не на випадковому сміттєвому.
const gawk_api_t *api = nullptr;
awk_ext_id_t ext_id{};

// Символ мусить мати C-компонування Й БУТИ ВИЗНАЧЕНИМ. У C++ рядок
// `extern "C" int x;` — лише оголошення, тому потрібен ініціалізатор.
extern "C" {
int plugin_is_GPL_compatible = 0;
}

namespace {

constexpr std::string_view kExtVersion = "fast_tools (C++): 1.0.0";

// Порядок полів: ім'я в AWK, реалізація, максимум аргументів, мінімум,
// придушення lint, контекстні дані модуля.
awk_ext_func_t func_table[] = {
    { "monotonic_time_ns", fast_tools::monotonic_time_ns,  0, 0, awk_false, nullptr },
    { "fnv1a_64",          fast_tools::fnv1a_64_of_string, 1, 1, awk_false, nullptr },
};

} // namespace

extern "C" int dl_load(const gawk_api_t *const api_p, awk_ext_id_t id)
{
    api = api_p;
    ext_id = id;

    // Старша версія мусить збігатися точно — від неї залежить розкладка
    // структур; молодша в інтерпретатора має бути не меншою за ту, під яку
    // зібрано модуль, інакше потрібних точок входу в таблиці просто немає.
    if (api->major_version != GAWK_API_MAJOR_VERSION
        || api->minor_version < GAWK_API_MINOR_VERSION) {
        // fatal() і warning() тут ще не можна: вони теж ходять через api,
        // а домовитися про його розкладку ми щойно не змогли.
        std::fprintf(stderr,
                     "fast_tools: gawk дає API %d.%d, а модуль зібрано під %d.%d\n",
                     api->major_version, api->minor_version,
                     GAWK_API_MAJOR_VERSION, GAWK_API_MINOR_VERSION);
        return 0;
    }

    int errors = 0;
    for (auto &func : func_table) {
        if (!fast_tools::glue::descriptor_is_sane(func)) {
            warning(ext_id, "fast_tools: зіпсований дескриптор функції %s",
                    func.name != nullptr ? func.name : "(без імені)");
            ++errors;
            continue;
        }
        // Порожній простір імен означає глобальний: функція з'явиться в AWK
        // під своїм іменем без префікса.
        if (!add_ext_func("", &func)) {
            warning(ext_id, "fast_tools: не зареєстрована функція %s", func.name);
            ++errors;
        }
    }

    register_ext_version(kExtVersion.data());   // рядок мусить пережити виклик
    return errors == 0 ? 1 : 0;
}
