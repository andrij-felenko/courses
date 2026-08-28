/* Файл: analytics/report_builder.cpp */
#include <string_view>

// Розробник скопіював значення вручну три місяці тому
std::string_view status_to_str(int st) {
    switch (st) {
        case 1: return "AUTH";
        case 2: return "CAPTURED";
        case 3: return "REFUNDED";
        default: return "UNKNOWN"; // Новий статус 4 потрапить сюди і зламає звіт
    }
}
