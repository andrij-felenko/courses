#include <iostream>
#include <optional>
#include <string_view>

std::optional<uint32_t> lookup_id(std::string_view key) {
    if (key.empty()) {
        return std::nullopt; // Явна відсутність
    }
    return 1001; // Неявна ініціалізація валідним значенням
}

int main() {
    auto id = lookup_id("admin");
    if (id.has_value()) {
        std::cout << "Отримано ID: " << id.value() << "\n";
    }
    return 0;
}
