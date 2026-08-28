#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <optional>
#include <sstream>
#include <filesystem>
#include <unistd.h>

struct ProcessStat {
    int pid{0};
    std::string comm;
    char state{'?'};
    int ppid{0};
    unsigned long utime{0};
    unsigned long stime{0};
    double utimeSec{0.0};
    double stimeSec{0.0};
    unsigned long vsize{0};
    long rssPages{0};
    unsigned long long rssBytes{0};
};

class ProcStatParser {
public:
    static std::optional<ProcessStat> parseFile(const std::filesystem::path& statPath) {
        std::ifstream file(statPath);
        if (!file.is_open()) {
            return std::nullopt;
        }

        std::string line;
        if (!std::getline(file, line)) {
            return std::nullopt;
        }

        const auto openParen = line.find('(');
        const auto closeParen = line.rfind(')');

        if (openParen == std::string::npos || closeParen == std::string::npos || closeParen <= openParen) {
            return std::nullopt;
        }

        ProcessStat result;
        
        try {
            result.pid = std::stoi(line.substr(0, openParen));
        } catch (const std::exception&) {
            return std::nullopt;
        }

        result.comm = line.substr(openParen + 1, closeParen - openParen - 1);

        std::string_view rest(line.data() + closeParen + 1, line.size() - closeParen - 1);
        std::istringstream iss{std::string(rest)};

        // Пропускаємо 7 неуживаних полів ядра
        unsigned long minflt, cminflt, majflt, cmajflt;
        int pgrp, session, tty_nr, tpgid;
        unsigned int flags;

        if (!(iss >> result.state >> result.ppid >> pgrp >> session >> tty_nr >> tpgid 
                  >> flags >> minflt >> cminflt >> majflt >> cmajflt 
                  >> result.utime >> result.stime)) {
            return std::nullopt;
        }

        long cutime, cstime, priority, nice, num_threads, itrealvalue;
        unsigned long long starttime;

        if (!(iss >> cutime >> cstime >> priority >> nice >> num_threads >> itrealvalue 
                  >> starttime >> result.vsize >> result.rssPages)) {
            return std::nullopt;
        }

        long clockTicks = sysconf(_SC_CLK_TCK);
        if (clockTicks <= 0) clockTicks = 100;

        long pageSize = sysconf(_SC_PAGESIZE);
        if (pageSize <= 0) pageSize = 4096;

        result.utimeSec = static_cast<double>(result.utime) / clockTicks;
        result.stimeSec = static_cast<double>(result.stime) / clockTicks;
        result.rssBytes = static_cast<unsigned long long>(result.rssPages) * pageSize;

        return result;
    }
};

int main() {
    const auto statOpt = ProcStatParser::parseFile("/proc/self/stat");
    if (!statOpt) {
        std::cerr << "Не вдалося розпарсити /proc/self/stat\n";
        return 1;
    }

    const auto& st = *statOpt;
    std::cout << "--- Результат розбору /proc/self/stat (C++) ---\n"
              << "PID:               " << st.pid << "\n"
              << "Comm:              " << st.comm << "\n"
              << "State:             " << st.state << "\n"
              << "PPID:              " << st.ppid << "\n"
              << "User Time:         " << st.utimeSec << " sec (" << st.utime << " ticks)\n"
              << "System Time:       " << st.stimeSec << " sec (" << st.stime << " ticks)\n"
              << "Virtual Memory:    " << (static_cast<double>(st.vsize) / (1024 * 1024)) << " MB\n"
              << "RSS Memory:        " << (static_cast<double>(st.rssBytes) / (1024 * 1024)) << " MB\n";

    return 0;
}
