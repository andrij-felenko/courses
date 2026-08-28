#include <contracts>
#include <cstdio>
#include <array>

// Структура для статичного збереження телеметрії збою без використання купи
struct CrashReport {
    const char* file{nullptr};
    std::uint32_t line{0};
    const char* function{nullptr};
    const char* comment{nullptr};
    const char* predicate{nullptr};
    const char* kind{nullptr};
};

inline std::array<CrashReport, 16> g_crash_log{};
inline std::size_t g_crash_count{0};

void handle_contract_violation(const std::contracts::contract_violation& v) noexcept {
    static thread_local bool in_violation_handler = false;
    if (in_violation_handler) {
        // Захист від нескінченної рекурсії у разі повторного збою
        return;
    }
    in_violation_handler = true;

    const char* kind_str = "ASSERTION";
    if (v.kind() == std::contracts::contract_kind::pre) {
        kind_str = "PRECONDITION";
    } else if (v.kind() == std::contracts::contract_kind::post) {
        kind_str = "POSTCONDITION";
    }

    if (g_crash_count < g_crash_log.size()) {
        g_crash_log[g_crash_count++] = CrashReport{
            .file = v.file_name(),
            .line = static_cast<std::uint32_t>(v.line_number()),
            .function = v.function_name(),
            .comment = v.comment(),
            .predicate = v.predicate(),
            .kind = kind_str
        };
    }

    std::fprintf(stderr,
        "==========================================================\n"
        "[SAFETY AUDIT] ПОРУШЕННЯ КОНТРАКТУ В СИСТЕМІ РЕАЛЬНОГО ЧАСУ\n"
        "  Категорія:  %s\n"
        "  Файл:       %s:%u\n"
        "  Функція:    %s\n"
        "  Мітка:      %s\n"
        "  Предикат:   %s\n"
        "==========================================================\n",
        kind_str,
        v.file_name(),
        static_cast<unsigned int>(v.line_number()),
        v.function_name(),
        v.comment()[0] != '\0' ? v.comment() : "<без мітки>",
        v.predicate()
    );

    in_violation_handler = false;
}
