#include <iostream>
#include <string>
#include <string_view>
#include <sstream>
#include <optional>
#include <format>
#include <memory>
#include <algorithm>
#include <cctype>
#include <cstdint>
#include <cstdio>
#include <stdexcept>

struct DmCacheStats {
    uint64_t read_hits{0};
    uint64_t read_misses{0};
    uint64_t write_hits{0};
    uint64_t write_misses{0};
    uint64_t demotions{0};
    uint64_t promotions{0};
    uint64_t dirty_blocks{0};
    uint64_t used_cache_blocks{0};
    uint64_t total_cache_blocks{0};

    [[nodiscard]] double hit_ratio() const noexcept {
        const uint64_t total_ops = read_hits + read_misses + write_hits + write_misses;
        if (total_ops == 0) return 0.0;
        return (static_cast<double>(read_hits + write_hits) / static_cast<double>(total_ops)) * 100.0;
    }

    [[nodiscard]] double cache_usage_pct() const noexcept {
        if (total_cache_blocks == 0) return 0.0;
        return (static_cast<double>(used_cache_blocks) / static_cast<double>(total_cache_blocks)) * 100.0;
    }
};

class DmStatusMonitor {
public:
    static std::optional<DmCacheStats> fetch_cache_stats(std::string_view dm_name) {
        if (!name_is_safe(dm_name)) {
            std::cerr << "Недопустиме ім'я пристрою: " << dm_name << '\n';
            return std::nullopt;
        }

        const std::string cmd = std::format("dmsetup status {}", dm_name);
        const std::unique_ptr<std::FILE, decltype(&pclose)> pipe(popen(cmd.c_str(), "r"), &pclose);
        if (!pipe) {
            std::cerr << "Не вдалося запустити dmsetup для " << dm_name << '\n';
            return std::nullopt;
        }

        std::string line;
        char chunk[256];
        while (std::fgets(chunk, sizeof(chunk), pipe.get()) != nullptr) {
            line += chunk;
            if (line.back() == '\n') break;
        }
        if (line.empty()) {
            return std::nullopt;
        }

        return parse_status_line(line);
    }

private:
    static bool name_is_safe(std::string_view name) {
        return !name.empty() && std::all_of(name.begin(), name.end(), [](unsigned char c) {
            return std::isalnum(c) || c == '-' || c == '_' || c == '.';
        });
    }

    static std::optional<DmCacheStats> parse_status_line(const std::string& line) {
        std::istringstream iss(line);
        int64_t start{0}, length{0};
        std::string target_type;

        if (!(iss >> start >> length >> target_type) || target_type != "cache") {
            return std::nullopt;
        }

        uint32_t meta_bs{0}, chunk_sz{0};
        std::string meta_usage, cache_usage;

        DmCacheStats stats;
        if (!(iss >> meta_bs >> meta_usage >> chunk_sz >> cache_usage
                  >> stats.read_hits >> stats.read_misses
                  >> stats.write_hits >> stats.write_misses
                  >> stats.demotions >> stats.promotions >> stats.dirty_blocks)) {
            return std::nullopt;
        }

        const auto slash_pos = cache_usage.find('/');
        if (slash_pos == std::string::npos) {
            return std::nullopt;
        }
        try {
            stats.used_cache_blocks = std::stoull(cache_usage.substr(0, slash_pos));
            stats.total_cache_blocks = std::stoull(cache_usage.substr(slash_pos + 1));
        } catch (const std::exception&) {
            return std::nullopt;
        }

        return stats;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <dm-пристрій> (наприклад, my_cached_dev)\n";
        return EXIT_FAILURE;
    }

    const std::string_view dm_device = argv[1];
    const auto stats = DmStatusMonitor::fetch_cache_stats(dm_device);

    if (!stats) {
        std::cerr << "Помилка розбору телеметрії dm-cache для " << dm_device << '\n';
        return EXIT_FAILURE;
    }

    std::cout << std::format("=== Телеметрія dm-cache для {} ===\n", dm_device)
              << std::format("Кешовано блоків:   {} / {} ({:.2f}%)\n",
                             stats->used_cache_blocks, stats->total_cache_blocks, stats->cache_usage_pct())
              << std::format("Влучання (Hits):   Читання: {}, Запис: {}\n", stats->read_hits, stats->write_hits)
              << std::format("Промахи (Misses):  Читання: {}, Запис: {}\n", stats->read_misses, stats->write_misses)
              << std::format("Коефіцієнт Hit Ratio: {:.2f}%\n", stats->hit_ratio())
              << std::format("Брудні блоки:      {}\n", stats->dirty_blocks)
              << std::format("Міграція даних:    Promotions: {}, Demotions: {}\n", stats->promotions, stats->demotions);

    if (stats->hit_ratio() < 50.0 && (stats->read_hits + stats->read_misses) > 10000) {
        std::cout << "УВАГА: Низький Hit Ratio! Розмір кешу може бути замалим для робочого набору.\n";
    }

    return EXIT_SUCCESS;
}
