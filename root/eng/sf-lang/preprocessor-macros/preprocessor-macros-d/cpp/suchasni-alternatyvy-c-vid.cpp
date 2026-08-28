#include <iostream>
#include <string_view>
#include <source_location>

// У C++20 функція фіксує місце виклику за замовчуванням через std::source_location
void log_event(std::string_view msg,
               const std::source_location location = std::source_location::current()) {
    std::cout << "[" << location.file_name() << ":"
              << location.line() << " in "
              << location.function_name() << "()] "
              << msg << "\n";
}

int main() {
    log_event("Ініціалізація підсистеми C++20 без жодного макросу");
    return 0;
}
