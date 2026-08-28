#include <format>
#include <iostream>

void dynamic_format_demo(const std::string& user_fmt_str) {
    try {
        // Динамічний розбір у runtime через vformat
        std::string res = std::vformat(user_fmt_str, std::make_format_args(42));
        std::cout << "Result: " << res << "\n";
    } catch (const std::format_error& e) {
        std::cerr << "Format error caught: " << e.what() << "\n";
    }
}
