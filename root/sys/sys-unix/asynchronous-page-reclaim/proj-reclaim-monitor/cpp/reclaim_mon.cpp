// reclaim_mon.cpp — C++20 об'єктно-орієнтований монітор витіснення сторінок
#include <iostream>
#include <fstream>
#include <string>
#include <chrono>
#include <thread>
#include <format>
#include <stdexcept>
#include <algorithm>
#include <cstdint>
#include <cstdlib>

struct VmstatMetrics {
    std::uint64_t pgscan_kswapd{0};
    std::uint64_t pgscan_direct{0};
    std::uint64_t pgsteal_kswapd{0};
    std::uint64_t pgsteal_direct{0};
    std::uint64_t allocstall{0};
    std::uint64_t pageoutrun{0};
};

class ReclaimCollector {
public:
    static VmstatMetrics fetch() {
        std::ifstream file("/proc/vmstat");
        if (!file.is_open()) {
            throw std::runtime_error("Cannot open /proc/vmstat");
        }

        VmstatMetrics m{};
        std::string key;
        std::uint64_t value;

        while (file >> key >> value) {
            if (key == "pgscan_kswapd")      m.pgscan_kswapd = value;
            else if (key == "pgscan_direct")  m.pgscan_direct = value;
            else if (key == "pgsteal_kswapd") m.pgsteal_kswapd = value;
            else if (key == "pgsteal_direct") m.pgsteal_direct = value;
            // від ядра 4.9 ключ розбито по зонах: allocstall_dma, allocstall_normal, …
            else if (key.starts_with("allocstall")) m.allocstall += value;
            else if (key == "pageoutrun")     m.pageoutrun = value;
        }
        return m;
    }
};

int main(int argc, char* argv[]) {
    using namespace std::chrono_literals;
    auto interval = 1s;

    if (argc > 1) {
        interval = std::chrono::seconds(std::max(1, std::atoi(argv[1])));
    }

    std::cout << std::format("C++20 Reclaim Monitor active (interval: {}s)\n", interval.count());
    std::cout << std::format("{:<10} | {:<14} | {:<14} | {:<10} | {:<10}\n",
                             "Time", "kswapd scan/s", "Direct scan/s", "Stalls/s", "kswapd Eff");
    std::cout << std::string(67, '-') << '\n';

    try {
        auto prev = ReclaimCollector::fetch();

        while (true) {
            std::this_thread::sleep_for(interval);
            auto curr = ReclaimCollector::fetch();

            auto dk_scan  = curr.pgscan_kswapd - prev.pgscan_kswapd;
            auto dd_scan  = curr.pgscan_direct - prev.pgscan_direct;
            auto dk_steal = curr.pgsteal_kswapd - prev.pgsteal_kswapd;
            auto dstalls  = curr.allocstall - prev.allocstall;

            double k_eff = (dk_scan > 0) 
                ? (static_cast<double>(dk_steal) / dk_scan * 100.0) 
                : 100.0;

            auto now = std::chrono::system_clock::now();
            auto time_t_now = std::chrono::system_clock::to_time_t(now);
            auto tm_now = *std::localtime(&time_t_now);

            std::string alert = (dstalls > 0) ? " [STALL DETECTED!]" : "";

            std::cout << std::format("{:02d}:{:02d}:{:02d}   | {:<14} | {:<14} | {:<10} | {:5.1f}%{}\n",
                                     tm_now.tm_hour, tm_now.tm_min, tm_now.tm_sec,
                                     dk_scan / interval.count(),
                                     dd_scan / interval.count(),
                                     dstalls / interval.count(),
                                     k_eff, alert);

            prev = curr;
        }
    } catch (const std::exception& e) {
        std::cerr << "Error in monitor loop: " << e.what() << '\n';
        return 1;
    }

    return 0;
}
