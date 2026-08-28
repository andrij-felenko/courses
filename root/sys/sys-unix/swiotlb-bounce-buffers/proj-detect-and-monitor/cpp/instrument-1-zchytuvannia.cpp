#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <expected>
#include <format>

namespace fs = std::filesystem;

struct SwiotlbMetrics {
    unsigned long nslabs{0};
    unsigned long used{0};
    unsigned long highwater{0};
    unsigned long overflow{0};

    [[nodiscard]] double total_mb() const noexcept {
        return static_cast<double>(nslabs * 2048) / (1024.0 * 1024.0);
    }
    [[nodiscard]] double used_mb() const noexcept {
        return static_cast<double>(used * 2048) / (1024.0 * 1024.0);
    }
    [[nodiscard]] double highwater_mb() const noexcept {
        return static_cast<double>(highwater * 2048) / (1024.0 * 1024.0);
    }
    [[nodiscard]] double used_percent() const noexcept {
        return nslabs ? (static_cast<double>(used) / static_cast<double>(nslabs)) * 100.0 : 0.0;
    }
    [[nodiscard]] double highwater_percent() const noexcept {
        return nslabs ? (static_cast<double>(highwater) / static_cast<double>(nslabs)) * 100.0 : 0.0;
    }
};

class SwiotlbMonitor {
    static constexpr std::string_view base_path = "/sys/kernel/debug/swiotlb";

    static std::expected<unsigned long, std::string> read_node(const std::string& name) {
        const fs::path p = fs::path(base_path) / name;
        std::ifstream file(p);
        if (!file.is_open()) {
            return std::unexpected(std::format("Не вдалося відкрити {}", p.string()));
        }
        unsigned long val = 0;
        if (!(file >> val)) {
            return std::unexpected(std::format("Помилка зчитування значення з {}", p.string()));
        }
        return val;
    }

public:
    static std::expected<SwiotlbMetrics, std::string> collect() {
        SwiotlbMetrics m{};
        auto nslabs = read_node("io_tlb_nslabs");
        if (!nslabs) return std::unexpected(nslabs.error());
        m.nslabs = *nslabs;

        m.used = read_node("io_tlb_used").value_or(0);
        m.highwater = read_node("io_tlb_used_highwater").value_or(0);
        m.overflow = read_node("io_tlb_overflow").value_or(0);
        return m;
    }
};

int main() {
    auto res = SwiotlbMonitor::collect();
    if (!res) {
        std::cerr << "Помилка: " << res.error() << "\n"
                  << "Переконайтеся, що debugfs змонтовано: mount -t debugfs none /sys/kernel/debug\n";
        return 1;
    }

    const auto& m = *res;
    std::cout << "=== Стан підсистеми SWIOTLB ===\n";
    std::cout << std::format("Загальний пул:      {:8d} слотів ({:6.2f} МіБ)\n", m.nslabs, m.total_mb());
    std::cout << std::format("Поточне утримання:  {:8d} слотів ({:6.2f} МіБ) [{:5.1f}%]\n", m.used, m.used_mb(), m.used_percent());
    std::cout << std::format("Пікове утримання:   {:8d} слотів ({:6.2f} МіБ) [{:5.1f}%]\n", m.highwater, m.highwater_mb(), m.highwater_percent());
    std::cout << std::format("Лічильник відмов:   {:8d} переповнень\n", m.overflow);

    if (m.overflow > 0) {
        std::cout << "\n[УВАГА] Зафіксовано переповнення пулу! Збільште параметр ядра swiotlb=N\n";
    } else if (m.highwater_percent() > 80.0) {
        std::cout << "\n[ПОПЕРЕДЖЕННЯ] Пікове навантаження перевищує 80% ємності пулу.\n";
    } else {
        std::cout << "\n[OK] Пул працює в штатному режимі із запасом пам'яті.\n";
    }

    return 0;
}
