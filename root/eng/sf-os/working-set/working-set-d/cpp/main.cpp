#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <chrono>
#include <thread>
#include <filesystem>
#include <system_error>

namespace fs = std::filesystem;

struct WorkingSetReport {
    unsigned long rss_kb{0};
    unsigned long referenced_kb{0};
};

class MemoryProfiler {
public:
    explicit MemoryProfiler(pid_t pid) : pid_(pid) {
        proc_root_ = "/proc/" + std::to_string(pid_);
        if (!fs::exists(proc_root_)) {
            throw std::runtime_error("Процес PID=" + std::to_string(pid_) + " не знайдено.");
        }
    }

    void reset_references() const {
        std::ofstream clear_file(proc_root_ + "/clear_refs");
        if (!clear_file.is_open()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити clear_refs");
        }
        clear_file << "1\n";
    }

    [[nodiscard]] WorkingSetReport sample_report() const {
        std::ifstream smaps_file(proc_root_ + "/smaps_rollup");
        if (!smaps_file.is_open()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити smaps_rollup");
        }

        WorkingSetReport report{};
        std::string line;
        while (std::getline(smaps_file, line)) {
            if (line.starts_with("Rss:")) {
                std::istringstream(line.substr(4)) >> report.rss_kb;
            } else if (line.starts_with("Referenced:")) {
                std::istringstream(line.substr(11)) >> report.referenced_kb;
            }
        }
        return report;
    }

private:
    pid_t pid_;
    std::string proc_root_;
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <pid> <вікно_сек>\n";
        return 1;
    }

    try {
        const pid_t pid = std::stoi(argv[1]);
        const int window_sec = std::stoi(argv[2]);

        MemoryProfiler profiler(pid);
        profiler.reset_references();

        std::cout << "Спостереження за PID=" << pid << " протягом " << window_sec << " с...\n";
        std::this_thread::sleep_for(std::chrono::seconds(window_sec));

        const auto report = profiler.sample_report();
        const double active_ratio = (report.rss_kb > 0)
            ? (static_cast<double>(report.referenced_kb) / static_cast<double>(report.rss_kb)) * 100.0
            : 0.0;

        std::cout << "Повна резидентна пам'ять (RSS):       " << report.rss_kb << " kB\n";
        std::cout << "Активна робоча множина W(t, Δ):        " << report.referenced_kb << " kB\n";
        std::cout << "Частка активно задіяної пам'яті:       " << active_ratio << " %\n";

    } catch (const std::exception& ex) {
        std::cerr << "Помилка інспекції: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
