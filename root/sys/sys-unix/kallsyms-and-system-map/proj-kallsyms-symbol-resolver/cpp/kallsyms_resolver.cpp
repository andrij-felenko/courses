// kallsyms_resolver.cpp — Ідіоматична реалізація мовою C++20 (RAII, STL, std::ranges)
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#include <algorithm>
#include <optional>
#include <cstdint>
#include <iomanip>
#include <stdexcept>

struct SymbolEntry {
    std::uint64_t address{0};
    char type{'?'};
    std::string name;
    std::string module;
};

class KernelSymbolResolver {
public:
    explicit KernelSymbolResolver(const std::string& kallsyms_path = "/proc/kallsyms") {
        load_from_file(kallsyms_path);
    }

    [[nodiscard]] std::size_t size() const noexcept {
        return symbols_.size();
    }

    struct LookupResult {
        const SymbolEntry& symbol;
        std::uint64_t offset;
    };

    [[nodiscard]] std::optional<LookupResult> lookup(std::uint64_t address) const {
        if (symbols_.empty()) return std::nullopt;

        auto it = std::upper_bound(
            symbols_.begin(), symbols_.end(), address,
            [](std::uint64_t val, const SymbolEntry& entry) {
                return val < entry.address;
            }
        );

        if (it != symbols_.begin()) {
            --it;
            std::uint64_t offset = address - it->address;
            return LookupResult{*it, offset};
        }
        return std::nullopt;
    }

private:
    std::vector<SymbolEntry> symbols_;

    void load_from_file(const std::string& path) {
        std::ifstream file(path);
        if (!file.is_open()) {
            throw std::runtime_error("Не вдалося відкрити файл: " + path);
        }

        std::string line;
        symbols_.reserve(65536);

        while (std::getline(file, line)) {
            if (line.empty()) continue;

            std::istringstream iss(line);
            std::string addr_str;
            char type;
            std::string name;

            if (!(iss >> addr_str >> type >> name)) continue;

            std::uint64_t addr = std::stoull(addr_str, nullptr, 16);
            if (addr == 0) continue; // Фільтрація маскування kptr_restrict

            std::string module;
            std::string extra;
            if (iss >> extra && extra.front() == '[') {
                module = extra.substr(1, extra.find(']') - 1);
            }

            symbols_.push_back(SymbolEntry{addr, type, std::move(name), std::move(module)});
        }

        std::ranges::sort(symbols_, [](const SymbolEntry& a, const SymbolEntry& b) {
            return a.address < b.address;
        });
    }
};

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <hex_address>\n";
        return 1;
    }

    std::uint64_t target_addr = std::stoull(argv[1], nullptr, 16);

    try {
        KernelSymbolResolver resolver("/proc/kallsyms");
        std::cout << "Успішно завантажено " << resolver.size() << " дійсних символів.\n";

        if (auto result = resolver.lookup(target_addr)) {
            const auto& [sym, offset] = *result;
            std::cout << "Адреса 0x" << std::hex << target_addr
                      << " -> " << sym.name << "+0x" << offset;
            if (!sym.module.empty()) {
                std::cout << " [" << sym.module << "]";
            }
            std::cout << " (Тип: " << sym.type << ")\n";
        } else {
            std::cout << "Символ для адреси не знайдено.\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
