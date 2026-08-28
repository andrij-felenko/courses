#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <bitset>
#include <chrono>
#include <thread>
#include <sstream>
#include <stdexcept>
#include <csignal>
#include <ctime>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <fcntl.h>

namespace minicron {

struct CronJob {
    std::bitset<60> minute_mask;   // 0..59
    std::bitset<24> hour_mask;     // 0..23
    std::bitset<32> dom_mask;      // 1..31
    std::bitset<13> month_mask;    // 1..12
    std::bitset<8>  dow_mask;      // 0..7 (0 і 7 - неділя)
    bool dom_is_wildcard{false};
    bool dow_is_wildcard{false};
    std::string command;
};

class Scheduler {
public:
    Scheduler() {
        setup_signal_handler();
    }

    void add_job(std::string_view min_s, std::string_view hour_s,
                 std::string_view dom_s, std::string_view mon_s,
                 std::string_view dow_s, std::string_view cmd) {
        CronJob job;
        bool dummy = false;

        job.minute_mask = parse_field<60>(min_s, 0, 59, dummy);
        job.hour_mask   = parse_field<24>(hour_s, 0, 23, dummy);
        job.dom_mask    = parse_field<32>(dom_s, 1, 31, job.dom_is_wildcard);
        job.month_mask  = parse_field<13>(mon_s, 1, 12, dummy);
        job.dow_mask    = parse_field<8>(dow_s, 0, 7, job.dow_is_wildcard);

        // Уніфікація неділі: 0 і 7 є еквівалентними
        if (job.dow_mask.test(7)) job.dow_mask.set(0);
        if (job.dow_mask.test(0)) job.dow_mask.set(7);

        job.command = cmd;
        jobs_.push_back(std::move(job));
    }

    void run() {
        std::cout << "minicron (C++) запущено. Завдань: " << jobs_.size() << "\n";

        while (true) {
            auto now = std::chrono::system_clock::now();
            std::time_t time_now = std::chrono::system_clock::to_time_t(now);
            std::tm tm_now{};
            localtime_r(&time_now, &tm_now);

            // Синхронізація з наступною астрономічною хвилиною
            int sleep_sec = 60 - tm_now.tm_sec;
            if (sleep_sec > 0) {
                std::this_thread::sleep_for(std::chrono::seconds(sleep_sec));
            }

            // Перечитуємо поточний час після пробудження
            now = std::chrono::system_clock::now();
            time_now = std::chrono::system_clock::to_time_t(now);
            localtime_r(&time_now, &tm_now);

            for (const auto& job : jobs_) {
                if (matches(job, tm_now)) {
                    spawn_process(job.command);
                }
            }
        }
    }

private:
    std::vector<CronJob> jobs_;

    static void setup_signal_handler() {
        struct sigaction sa{};
        sa.sa_handler = [](int) {
            while (waitpid(-1, nullptr, WNOHANG) > 0) {
                // Збір зомбі-процесів
            }
        };
        sigemptyset(&sa.sa_mask);
        sa.sa_flags = SA_RESTART | SA_NOCLDSTOP;
        sigaction(SIGCHLD, &sa, nullptr);
    }

    template <size_t N>
    static std::bitset<N> parse_field(std::string_view str, int min_val, int max_val, bool& is_wildcard) {
        std::bitset<N> mask;
        is_wildcard = false;

        if (str == "*") {
            is_wildcard = true;
            for (int i = min_val; i <= max_val; ++i) mask.set(i);
            return mask;
        }

        if (str.starts_with("*/")) {
            int step = std::stoi(std::string(str.substr(2)));
            if (step <= 0) throw std::invalid_argument("Некоректний крок розкладу");
            for (int i = min_val; i <= max_val; i += step) mask.set(i);
            return mask;
        }

        auto dash_pos = str.find('-');
        if (dash_pos != std::string_view::npos) {
            int start = std::stoi(std::string(str.substr(0, dash_pos)));
            int end = std::stoi(std::string(str.substr(dash_pos + 1)));
            if (start < min_val || end > max_val || start > end) {
                throw std::out_of_range("Діапазон розкладу поза межами");
            }
            for (int i = start; i <= end; ++i) mask.set(i);
            return mask;
        }

        // Розбір списку значень через кому
        std::stringstream ss{std::string(str)};
        std::string token;
        while (std::getline(ss, token, ',')) {
            int val = std::stoi(token);
            if (val < min_val || val > max_val) {
                throw std::out_of_range("Значення поля виходить за межі");
            }
            mask.set(val);
        }
        return mask;
    }

    static bool matches(const CronJob& job, const std::tm& t) {
        if (!job.minute_mask.test(t.tm_min)) return false;
        if (!job.hour_mask.test(t.tm_hour)) return false;
        if (!job.month_mask.test(t.tm_mon + 1)) return false;

        bool dom_match = job.dom_mask.test(t.tm_mday);
        bool dow_match = job.dow_mask.test(t.tm_wday);

        // Диз'юнкція POSIX: якщо обидва поля явно задані — спрацьовує будь-яке
        if (!job.dom_is_wildcard && !job.dow_is_wildcard) {
            return dom_match || dow_match;
        }
        return dom_match && dow_match;
    }

    static void spawn_process(const std::string& cmd) {
        pid_t pid = fork();
        if (pid < 0) {
            std::cerr << "Помилка fork()\n";
            return;
        }
        if (pid == 0) {
            int devnull = open("/dev/null", O_RDWR);
            if (devnull >= 0) {
                dup2(devnull, STDIN_FILENO);
                close(devnull);
            }
            execl("/bin/sh", "sh", "-c", cmd.c_str(), nullptr);
            _exit(127);
        }
    }
};

} // namespace minicron

int main() {
    try {
        minicron::Scheduler scheduler;
        scheduler.add_job("*", "*", "*", "*", "*", "echo tick $(date) >> /tmp/minicron_cpp.log");
        scheduler.add_job("*/10", "*", "*", "*", "*", "df -h >> /tmp/minicron_df.log");
        scheduler.run();
    } catch (const std::exception& e) {
        std::cerr << "Критична помилка: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
