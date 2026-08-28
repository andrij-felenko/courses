#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <regex>
#include <charconv>

namespace {

// Очищення пробілів через створення підрядка без копіювання пам'яті
std::string_view trim(std::string_view sv) {
    const auto start = sv.find_first_not_of(" \t\r\n");
    if (start == std::string_view::npos) return {};
    const auto end = sv.find_last_not_of(" \t\r\n");
    return sv.substr(start, end - start + 1);
}

// Розбиття рядка за роздільником без алокації динамічної пам'яті під токени
std::vector<std::string_view> split(std::string_view sv, char delim) {
    std::vector<std::string_view> tokens;
    size_t pos = 0;
    while (pos < sv.size()) {
        const auto next = sv.find(delim, pos);
        if (next == std::string_view::npos) {
            tokens.push_back(sv.substr(pos));
            break;
        }
        tokens.push_back(sv.substr(pos, next - pos));
        pos = next + 1;
    }
    return tokens;
}

// Швидка валідація IPv4 через std::from_chars без виклику regex
bool validate_ipv4(std::string_view ip) {
    const auto octets = split(ip, '.');
    if (octets.size() != 4) return false;

    for (const auto& octet_sv : octets) {
        if (octet_sv.empty() || octet_sv.size() > 3) return false;
        int val = 0;
        const auto [ptr, ec] = std::from_chars(octet_sv.data(), octet_sv.data() + octet_sv.size(), val);
        if (ec != std::errc{} || ptr != octet_sv.data() + octet_sv.size() || val < 0 || val > 255) {
            return false;
        }
    }
    return true;
}

} // namespace

int main(int argc, char* argv[]) {
    const std::string filename = (argc > 1) ? argv[1] : "";
    std::ifstream file_stream;
    std::istream* input = &std::cin;

    // Автоматичне керування життєвим циклом файлового потоку (RAII)
    if (!filename.empty() && filename != "-") {
        file_stream.open(filename);
        if (!file_stream) {
            std::cerr << "Помилка відкриття файлу: " << filename << '\n';
            return 1;
        }
        input = &file_stream;
    }

    const std::regex name_regex("^[a-zA-Z0-9_-]+$");
    int total = 0, valid = 0, invalid = 0;
    std::string line;

    // std::getline безпечно зчитує потік рядок за рядком до символу \n або EOF
    while (std::getline(*input, line)) {
        std::string_view sv = trim(line);
        if (sv.empty() || sv.front() == '#') {
            continue;
        }

        total++;
        const auto parts = split(sv, ':');
        if (parts.size() != 4) {
            invalid++;
            std::cerr << "[ПОМИЛКА] Некоректна кількість полів: '" << line << "'\n";
            continue;
        }

        const auto name   = trim(parts[0]);
        const auto ip     = trim(parts[1]);
        const auto port_s = trim(parts[2]);
        const auto status = trim(parts[3]);

        bool is_valid = true;

        // Перевірка імені регулярним виразом
        if (!std::regex_match(name.begin(), name.end(), name_regex)) {
            is_valid = false;
        }

        // Перевірка октетів IP-адреси
        if (!validate_ipv4(ip)) {
            is_valid = false;
        }

        // Перевірка числового значення порту через std::from_chars
        int port = 0;
        const auto [ptr, ec] = std::from_chars(port_s.data(), port_s.data() + port_s.size(), port);
        if (ec != std::errc{} || ptr != port_s.data() + port_s.size() || port < 1 || port > 65535) {
            is_valid = false;
        }

        // Перевірка дозволених статусів
        if (status != "ENABLED" && status != "DISABLED" && status != "MAINTENANCE") {
            is_valid = false;
        }

        if (is_valid) {
            valid++;
            std::cout << "[OK] Сервіс: " << name
                      << " | Адреса: " << ip << ':' << port
                      << " | Стан: " << status << '\n';
        } else {
            invalid++;
            std::cerr << "[ПОМИЛКА] Невалідні дані запису: '" << line << "'\n";
        }
    }

    std::cout << "\n=== Підсумок обробки ===\n";
    std::cout << "Усього: " << total << ", Валідних: " << valid << ", Невалідних: " << invalid << '\n';
    return 0;
}
