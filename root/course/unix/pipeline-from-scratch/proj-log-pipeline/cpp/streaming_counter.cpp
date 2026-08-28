// streaming_counter.cpp — ідіоматичний агрегатор логів на C++20
#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <vector>
#include <algorithm>
#include <csignal>

// Прозорий компаратор для пошуку в unordered_map за string_view без алокації std::string
struct StringHash {
    using is_transparent = void;
    [[nodiscard]] std::size_t operator()(std::string_view sv) const noexcept {
        return std::hash<std::string_view>{}(sv);
    }
};

int main() {
    // Вимикаємо синхронізацію зі стандартними потоками C для максимальної швидкодії I/O
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(nullptr);
    std::signal(SIGPIPE, SIG_IGN);

    std::unordered_map<std::string, std::uint64_t, StringHash, std::equal_to<>> counts;
    std::string line;
    line.reserve(1024);

    while (std::getline(std::cin, line)) {
        if (line.size() < 10) continue;

        std::string_view view{line};
        
        // Виділяємо IP-адресу без виділення динамічної пам'яті через string_view
        const auto ip_end = view.find(' ');
        if (ip_end == std::string_view::npos) continue;
        std::string_view ip = view.substr(0, ip_end);

        // Знаходимо закінчення HTTP-запиту в лапках
        const auto first_quote = view.find('"', ip_end + 1);
        if (first_quote == std::string_view::npos) continue;
        const auto second_quote = view.find('"', first_quote + 1);
        if (second_quote == std::string_view::npos) continue;

        // Позиція коду статусу
        auto status_pos = second_quote + 1;
        while (status_pos < view.size() && view[status_pos] == ' ') {
            ++status_pos;
        }

        if (status_pos + 3 <= view.size()) {
            std::string_view code = view.substr(status_pos, 3);
            if (code.starts_with('5') && std::isdigit(code[1]) && std::isdigit(code[2])) {
                counts[std::string(ip)]++;
            }
        }
    }

    // Згортання та вивід результатів у потік
    for (const auto& [ip, count] : counts) {
        std::cout << count << ' ' << ip << '\n';
    }

    return 0;
}
