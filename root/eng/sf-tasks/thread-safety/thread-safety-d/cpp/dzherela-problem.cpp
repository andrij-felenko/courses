#include <string_view>
#include <iostream>

void parse_tokens_reentrant(std::string_view input) {
    size_t start = 0;
    while (start < input.size()) {
        auto end = input.find(' ', start);
        if (end == std::string_view::npos) {
            end = input.size();
        }
        std::string_view token = input.substr(start, end - start);
        if (!token.empty()) {
            std::cout << "Лексема: " << token << '\n';
        }
        start = end + 1;
    }
}
