#include <contracts>
#include <cstdio>

void handle_contract_violation(const std::contracts::contract_violation& v) noexcept {
    const char* kind_name = "невідомий";
    switch (v.kind()) {
        case std::contracts::contract_kind::pre:    kind_name = "ПРЕУМОВА"; break;
        case std::contracts::contract_kind::post:   kind_name = "ПОСТУМОВА"; break;
        case std::contracts::contract_kind::assert: kind_name = "ТВЕРДЖЕННЯ"; break;
    }

    std::fprintf(stderr,
        "[АВАРІЯ КОНТРАКТУ]\n"
        "  Файл:      %s (рядок %u)\n"
        "  Функція:   %s\n"
        "  Категорія: %s\n"
        "  Мітка:     %s\n"
        "  Предикат:  %s\n",
        v.file_name(),
        static_cast<unsigned int>(v.line_number()),
        v.function_name(),
        kind_name,
        v.comment()[0] != '\0' ? v.comment() : "<немає>",
        v.predicate()
    );
}
