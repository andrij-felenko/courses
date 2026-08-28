#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <chrono>
#include <thread>
#include <vector>
#include <optional>
#include <iomanip>
#include <unistd.h>

struct ProcessMetrics {
    unsigned long long utime_ticks{0};
    unsigned long long stime_ticks{0};
    unsigned long long minflt{0};
    unsigned long long majflt{0};
    unsigned long long sched_cpu_ns{0};
    unsigned long long sched_wait_ns{0};
    unsigned long long sched_switches{0};
    unsigned long long vol_ctxt{0};
    unsigned long long nonvol_ctxt{0};
    std::chrono::steady_clock::time_point timestamp{};
};

class ProcessProfiler {
public:
    explicit ProcessProfiler(pid_t pid, long clk_tck = 100)
        : pid_{pid}, clk_tck_{clk_tck > 0 ? clk_tck : 100} {}

    [[nodiscard]] std::optional<ProcessMetrics> sample() const {
        ProcessMetrics m;
        m.timestamp = std::chrono::steady_clock::now();

        if (!readStat(m) || !readStatus(m)) {
            return std::nullopt;
        }
        readSchedstat(m); // Може бути відсутній без CONFIG_SCHEDSTATS
        return m;
    }

    void printReport(const ProcessMetrics& prev, const ProcessMetrics& curr) const {
        const auto duration_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(
            curr.timestamp - prev.timestamp).count();
        const double dt = static_cast<double>(duration_ns) / 1e9;
        if (dt <= 0.0) return;

        const double utime_sec = static_cast<double>(curr.utime_ticks - prev.utime_ticks) / static_cast<double>(clk_tck_);
        const double stime_sec = static_cast<double>(curr.stime_ticks - prev.stime_ticks) / static_cast<double>(clk_tck_);
        const double sched_wait_sec = static_cast<double>(curr.sched_wait_ns - prev.sched_wait_ns) / 1e9;

        const double cpu_total = utime_sec + stime_sec;
        double off_cpu_sec = dt - cpu_total - sched_wait_sec;
        if (off_cpu_sec < 0.0) off_cpu_sec = 0.0;

        const double user_pct = (utime_sec / dt) * 100.0;
        const double sys_pct  = (stime_sec / dt) * 100.0;
        const double wait_pct = (sched_wait_sec / dt) * 100.0;
        const double off_pct  = (off_cpu_sec / dt) * 100.0;

        const auto vol_diff = curr.vol_ctxt - prev.vol_ctxt;
        const auto nonvol_diff = curr.nonvol_ctxt - prev.nonvol_ctxt;
        const auto minflt_diff = curr.minflt - prev.minflt;
        const auto majflt_diff = curr.majflt - prev.majflt;

        std::cout << std::fixed << std::setprecision(1)
                  << "[Δt=" << dt << "s] CPU: usr=" << user_pct << "% sys=" << sys_pct
                  << "% | SchedWait=" << wait_pct << "% | OffCPU=" << off_pct
                  << "% | Ctxt: vol=" << static_cast<unsigned long long>(vol_diff / dt)
                  << "/s nonvol=" << static_cast<unsigned long long>(nonvol_diff / dt)
                  << "/s | Flt: min=" << minflt_diff << " maj=" << majflt_diff << "\n";

        diagnose(user_pct, sys_pct, wait_pct, off_pct, vol_diff, majflt_diff);
    }

private:
    pid_t pid_;
    long clk_tck_;

    bool readStat(ProcessMetrics& m) const {
        std::ifstream file("/proc/" + std::to_string(pid_) + "/stat");
        if (!file.is_open()) return false;

        std::string content;
        std::getline(file, content);

        const auto close_paren = content.rfind(')');
        if (close_paren == std::string::npos || close_paren + 2 >= content.size()) {
            return false;
        }

        std::istringstream stream(content.substr(close_paren + 2));
        char state;
        int ppid, pgrp, session, tty_nr, tpgid;
        unsigned int flags;
        unsigned long long cminflt, cmajflt;

        if (stream >> state >> ppid >> pgrp >> session >> tty_nr >> tpgid
                   >> flags >> m.minflt >> cminflt >> m.majflt >> cmajflt
                   >> m.utime_ticks >> m.stime_ticks) {
            return true;
        }
        return false;
    }

    void readSchedstat(ProcessMetrics& m) const {
        std::ifstream file("/proc/" + std::to_string(pid_) + "/schedstat");
        if (file.is_open()) {
            file >> m.sched_cpu_ns >> m.sched_wait_ns >> m.sched_switches;
        }
    }

    bool readStatus(ProcessMetrics& m) const {
        std::ifstream file("/proc/" + std::to_string(pid_) + "/status");
        if (!file.is_open()) return false;

        std::string line;
        while (std::getline(file, line)) {
            if (line.rfind("voluntary_ctxt_switches:", 0) == 0) {
                m.vol_ctxt = std::stoull(line.substr(24));
            } else if (line.rfind("nonvoluntary_ctxt_switches:", 0) == 0) {
                m.nonvol_ctxt = std::stoull(line.substr(27));
            }
        }
        return true;
    }

    static void diagnose(double user_pct, double sys_pct, double wait_pct, double off_pct,
                         unsigned long long vol_diff, unsigned long long majflt_diff) {
        if (user_pct > 60.0) {
            std::cout << "  ↳ ДІАГНОЗ: CPU-Bound (User). Гарячі цикли або обчислення в коді програми.\n";
        } else if (sys_pct > 40.0) {
            std::cout << "  ↳ ДІАГНОЗ: System-Bound. Надмірна кількість системних викликів або сторінкових збоїв.\n";
        } else if (wait_pct > 20.0) {
            std::cout << "  ↳ ДІАГНОЗ: Scheduler Starvation. Процес чекає черги до процесора через нестачу ядер.\n";
        } else if (majflt_diff > 10) {
            std::cout << "  ↳ ДІАГНОЗ: Paging / Swap Bottleneck. Часті значні сторінкові збої з диска.\n";
        } else if (off_pct > 70.0 && vol_diff > 1000) {
            std::cout << "  ↳ ДІАГНОЗ: High Concurrency / I/O Blocking. Часті добровільні блокування на сокетах або м'ютексах.\n";
        } else if (off_pct > 70.0) {
            std::cout << "  ↳ ДІАГНОЗ: Idle / Sleep. Процес здебільшого спить або чекає зовнішніх подій.\n";
        }
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <PID> [інтервал_секунд]\n";
        return 1;
    }

    const pid_t pid = static_cast<pid_t>(std::stoi(argv[1]));
    const int interval_sec = (argc >= 3) ? std::max(1, std::stoi(argv[2])) : 1;
    const long clk_tck = sysconf(_SC_CLK_TCK);

    ProcessProfiler profiler(pid, clk_tck);
    auto prev = profiler.sample();
    if (!prev) {
        std::cerr << "Помилка доступу до процесу з PID " << pid << "\n";
        return 1;
    }

    std::cout << "Моніторинг бюджету часу для PID " << pid
              << " (CLK_TCK=" << clk_tck << ", інтервал=" << interval_sec << " с)...\n";
    std::cout << "--------------------------------------------------------------------------------\n";

    while (true) {
        std::this_thread::sleep_for(std::chrono::seconds(interval_sec));
        auto curr = profiler.sample();
        if (!curr) {
            std::cout << "Процес " << pid << " завершився або став недоступним.\n";
            break;
        }

        profiler.printReport(*prev, *curr);
        prev = curr;
    }

    return 0;
}
