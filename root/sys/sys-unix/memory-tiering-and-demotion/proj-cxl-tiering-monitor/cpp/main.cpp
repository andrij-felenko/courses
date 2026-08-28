#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <unordered_map>
#include <chrono>
#include <thread>
#include <iomanip>
#include <filesystem>

namespace fs = std::filesystem;

struct TierMetrics {
    uint64_t pgdemote_kswapd = 0;
    uint64_t pgdemote_direct = 0;
    uint64_t pgpromote_success = 0;
    uint64_t pgpromote_candidate = 0;
    uint64_t numa_hint_faults = 0;
};

class TieringMonitor {
public:
    static void discover_tiers() {
        const fs::path tiers_path = "/sys/devices/system/node/memory_tiers";
        if (!fs::exists(tiers_path)) {
            std::cout << "[WARN] Каталог memory_tiers не знайдено: " << tiers_path << "\n";
            std::cout << "[INFO] Можливо, CXL-пристрої відсутні або ядро не зібрано з CONFIG_TIERED_MEMORY.\n\n";
            return;
        }

        std::cout << "=== Виявлені яруси пам'яті (Memory Tiers) ===\n";
        for (const auto& entry : fs::directory_iterator(tiers_path)) {
            if (entry.is_directory() && entry.path().filename().string().rfind("memory_tier", 0) == 0) {
                fs::path nodelist_file = entry.path() / "nodelist";
                std::string nodes = "unknown";
                if (std::ifstream in(nodelist_file); in.is_open()) {
                    std::getline(in, nodes);
                }
                std::cout << "  • " << std::left << std::setw(14) << entry.path().filename().string()
                          << " -> NUMA-вузли: [" << nodes << "]\n";
            }
        }
        std::cout << "\n";
    }

    static TierMetrics read_vmstat() {
        TierMetrics metrics;
        std::ifstream file("/proc/vmstat");
        if (!file.is_open()) return metrics;

        std::string key;
        uint64_t value = 0;
        while (file >> key >> value) {
            if (key == "pgdemote_kswapd") metrics.pgdemote_kswapd = value;
            else if (key == "pgdemote_direct") metrics.pgdemote_direct = value;
            else if (key == "pgpromote_success") metrics.pgpromote_success = value;
            else if (key == "pgpromote_candidate") metrics.pgpromote_candidate = value;
            else if (key == "numa_hint_faults") metrics.numa_hint_faults = value;
        }
        return metrics;
    }

    static void run(std::chrono::seconds interval) {
        discover_tiers();

        TierMetrics prev = read_vmstat();

        std::cout << std::left << std::setw(10) << "Час" << " | "
                  << std::setw(16) << "Demote kswapd" << " | "
                  << std::setw(16) << "Demote Direct" << " | "
                  << std::setw(16) << "Promote Success" << " | "
                  << std::setw(14) << "NUMA Hints" << "\n";
        std::cout << std::string(83, '-') << "\n";

        while (true) {
            std::this_thread::sleep_for(interval);
            TierMetrics curr = read_vmstat();

            auto now = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());
            auto local_tm = *std::localtime(&now);

            constexpr double page_kb = 4.0;
            double factor = page_kb / (1024.0 * interval.count());

            double demote_kswapd_mb = static_cast<double>(curr.pgdemote_kswapd - prev.pgdemote_kswapd) * factor;
            double demote_direct_mb = static_cast<double>(curr.pgdemote_direct - prev.pgdemote_direct) * factor;
            double promote_mb = static_cast<double>(curr.pgpromote_success - prev.pgpromote_success) * factor;
            uint64_t hints_rate = (curr.numa_hint_faults - prev.numa_hint_faults) / interval.count();

            std::cout << std::put_time(&local_tm, "%H:%M:%S") << "   | "
                      << std::right << std::setw(10) << std::fixed << std::setprecision(2) << demote_kswapd_mb << " MB/s | "
                      << std::right << std::setw(10) << std::fixed << std::setprecision(2) << demote_direct_mb << " MB/s | "
                      << std::right << std::setw(10) << std::fixed << std::setprecision(2) << promote_mb << " MB/s | "
                      << std::right << std::setw(10) << hints_rate << " f/s\n";

            prev = curr;
        }
    }
};

int main(int argc, char* argv[]) {
    int interval_sec = (argc > 1) ? std::max(1, std::atoi(argv[1])) : 1;
    TieringMonitor::run(std::chrono::seconds(interval_sec));
    return 0;
}
