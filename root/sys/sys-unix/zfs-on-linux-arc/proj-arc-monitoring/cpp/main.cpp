#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <iomanip>
#include <system_error>
#include <cstdint>

namespace zfs {

struct ArcMetrics {
    std::uint64_t hits{0};
    std::uint64_t misses{0};
    std::uint64_t mru_hits{0};
    std::uint64_t mfu_hits{0};
    std::uint64_t size{0};
    std::uint64_t c{0};
    std::uint64_t p{0};
    std::uint64_t arc_meta_used{0};
};

class ArcMonitor {
private:
    static constexpr std::string_view kArcstatsPath = "/proc/spl/kstat/zfs/arcstats";

public:
    [[nodiscard]] ArcMetrics fetchMetrics() const {
        std::ifstream file{std::string(kArcstatsPath)};
        if (!file.is_open()) {
            throw std::system_error(
                errno, 
                std::generic_category(), 
                "Не вдалося відкрити " + std::string(kArcstatsPath)
            );
        }

        ArcMetrics metrics;
        std::string line;

        // Перші рядки kstat службові (шапка й рядок «name type data»), тож
        // розбираємо порядково й мовчки пропускаємо все, що не лягає у трійку.
        while (std::getline(file, line)) {
            std::istringstream ls{line};
            std::string key;
            int type{0};
            std::uint64_t value{0};
            if (!(ls >> key >> type >> value)) continue;

            if (key == "hits") metrics.hits = value;
            else if (key == "misses") metrics.misses = value;
            else if (key == "mru_hits") metrics.mru_hits = value;
            else if (key == "mfu_hits") metrics.mfu_hits = value;
            else if (key == "size") metrics.size = value;
            else if (key == "c") metrics.c = value;
            else if (key == "p") metrics.p = value;
            else if (key == "arc_meta_used") metrics.arc_meta_used = value;
        }

        return metrics;
    }

    void displayReport(const ArcMetrics& m) const {
        const std::uint64_t total_accesses = m.hits + m.misses;
        const double hit_ratio = total_accesses > 0 ? (static_cast<double>(m.hits) * 100.0) / total_accesses : 0.0;
        const double mru_pct = m.hits > 0 ? (static_cast<double>(m.mru_hits) * 100.0) / m.hits : 0.0;
        const double mfu_pct = m.hits > 0 ? (static_cast<double>(m.mfu_hits) * 100.0) / m.hits : 0.0;

        const double size_mb = static_cast<double>(m.size) / (1024.0 * 1024.0);
        const double c_mb = static_cast<double>(m.c) / (1024.0 * 1024.0);
        const double p_mb = static_cast<double>(m.p) / (1024.0 * 1024.0);
        const double meta_mb = static_cast<double>(m.arc_meta_used) / (1024.0 * 1024.0);

        std::cout << std::fixed << std::setprecision(2);
        std::cout << "================ ZFS ARC Diagnostics (C++) ================\n";
        std::cout << "Поточний розмір ARC (size) : " << std::setw(8) << size_mb << " МБ\n";
        std::cout << "Цільовий розмір кешу (c)   : " << std::setw(8) << c_mb << " МБ\n";
        std::cout << "Вага Recency MRU (p)       : " << std::setw(8) << p_mb << " МБ\n";
        std::cout << "Пам'ять під метадані       : " << std::setw(8) << meta_mb << " МБ\n";
        std::cout << "---------------------------------------------------------\n";
        std::cout << "Загальний Hit Ratio        : " << std::setw(8) << hit_ratio << " %\n";
        std::cout << "Частка MRU Hits            : " << std::setw(8) << mru_pct << " %\n";
        std::cout << "Частка MFU Hits            : " << std::setw(8) << mfu_pct << " %\n";
        std::cout << "=========================================================\n";
    }
};

} // namespace zfs

int main() {
    try {
        zfs::ArcMonitor monitor;
        const auto metrics = monitor.fetchMetrics();
        monitor.displayReport(metrics);
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
