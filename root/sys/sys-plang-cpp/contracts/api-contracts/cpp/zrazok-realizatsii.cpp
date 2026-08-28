#include <contracts>
#include <cstdio>
#include <cstdlib>

void handle_contract_violation(const std::contracts::contract_violation& v) noexcept {
    static thread_local bool in_violation_handler = false;
    if (in_violation_handler) {
        // Запобігання повторному входу у разі рекурсивного збою
        return;
    }
    in_violation_handler = true;

    const char* kind_str = "невідомий";
    switch (v.kind()) {
        case std::contracts::contract_kind::pre:    kind_str = "преумова (pre)"; break;
        case std::contracts::contract_kind::post:   kind_str = "постумова (post)"; break;
        case std::contracts::contract_kind::assert: kind_str = "твердження (assert)"; break;
    }

    const char* mode_str = (v.detection_mode() == std::contracts::detection_mode::predicate_false)
        ? "предикат хибний"
        : "виник виняток під час оцінки";

    std::fprintf(stderr,
        "[CRITICAL CONTRACT VIOLATION]\n"
        "  Файл:        %s:%u\n"
        "  Функція:     %s\n"
        "  Тип:         %s\n"
        "  Мітка:       %s\n"
        "  Предикат:    %s\n"
        "  Причина:     %s\n",
        v.file_name(),
        static_cast<unsigned int>(v.line_number()),
        v.function_name(),
        kind_str,
        v.comment()[0] != '\0' ? v.comment() : "<немає>",
        v.predicate(),
        mode_str
    );

    in_violation_handler = false;
}
