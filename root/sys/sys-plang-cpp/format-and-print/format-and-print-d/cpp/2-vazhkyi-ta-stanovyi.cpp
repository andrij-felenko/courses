// Сучасний ідіоматичний C++20 підхід: std::format та std::format_to
#include <format>
#include <string>
#include <string_view>
#include <span>

std::string format_address_cpp(std::string_view host, int port) {
    // Повна типобезпека: рядок формату перевіряється під час компіляції через consteval
    return std::format("Server {} listening on port {}", host, port);
}

void format_address_cpp_no_alloc(std::span<char> buf, std::string_view host, int port) {
    // Безалокаційний запис у наявний масив пам'яті із суворим контролем межі
    std::format_to_n(buf.data(), buf.size() - 1, "Server {} listening on port {}", host, port);
}
