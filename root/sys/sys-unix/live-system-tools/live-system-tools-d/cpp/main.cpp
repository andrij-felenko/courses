// C++ Implementation: RAII /proc/stat CPU Utilization Calculator using C++20
#include <iostream>
#include <fstream>
#include <string>
#include <chrono>
#include <thread>
#include <optional>
#include <format>

struct CpuSnapshot {
    std::uint64_t user{0};
    std::uint64_t nice{0};
    std::uint64_t system{0};
    std::uint64_t idle{0};
    std::uint64_t iowait{0};
    std::uint64_t irq{0};
    std::uint64_t softirq{0};
    std::uint64_t steal{0};

    [[nodiscard]] std::uint64_t total() const noexcept {
        return user + nice + system + idle + iowait + irq + softirq + steal;
    }
};

class CpuMonitor {
public:
    static std::optional<CpuSnapshot> capture() {
        std::ifstream statFile("/proc/stat");
        if (!statFile.is_open()) {
            return std::nullopt;
        }

        std::string cpuLabel;
        CpuSnapshot s{};
        if (!(statFile >> cpuLabel >> s.user >> s.nice >> s.system >> s.idle
                        >> s.iowait >> s.irq >> s.softirq >> s.steal)) {
            return std::nullopt;
        }

        return (cpuLabel == "cpu") ? std::optional{s} : std::nullopt;
    }
};

int main() {
    const auto snap1 = CpuMonitor::capture();
    if (!snap1) {
        std::cerr << "Failed to capture initial CPU snapshot from /proc/stat\n";
        return 1;
    }

    std::this_thread::sleep_for(std::chrono::seconds(1));

    const auto snap2 = CpuMonitor::capture();
    if (!snap2) {
        std::cerr << "Failed to capture second CPU snapshot from /proc/stat\n";
        return 1;
    }

    const auto dUser = (snap2->user + snap2->nice) - (snap1->user + snap1->nice);
    const auto dSystem = snap2->system - snap1->system;
    const auto dIdle = snap2->idle - snap1->idle;
    const auto dIowait = snap2->iowait - snap1->iowait;
    const auto dTotal = std::max<std::uint64_t>(1, snap2->total() - snap1->total());

    const double pctUser = static_cast<double>(dUser) * 100.0 / dTotal;
    const double pctSystem = static_cast<double>(dSystem) * 100.0 / dTotal;
    const double pctIowait = static_cast<double>(dIowait) * 100.0 / dTotal;
    const double pctIdle = static_cast<double>(dIdle) * 100.0 / dTotal;

    std::cout << "=== CPU UTILIZATION REPORT (C++) ===\n";
    std::cout << "User Space:   " << pctUser << "%\n";
    std::cout << "Kernel Space: " << pctSystem << "%\n";
    std::cout << "IO Wait:      " << pctIowait << "%\n";
    std::cout << "Idle:         " << pctIdle << "%\n";

    return 0;
}
