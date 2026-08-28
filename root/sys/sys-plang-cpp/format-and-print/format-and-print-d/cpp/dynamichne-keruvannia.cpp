#include <format>
#include <string>

std::string format_table_row(std::string_view label, double val, int width, int prec) {
    // Вкладені дужки {} означають, що ширина та точність беруться з наступних аргументів
    return std::format("{:<{}} : {:>{}.{}f}", label, width, val, width, prec);
}

// Виклик format_table_row("CPU", 45.6789, 12, 2)
// Поверне рядок: "CPU          :        45.68"
