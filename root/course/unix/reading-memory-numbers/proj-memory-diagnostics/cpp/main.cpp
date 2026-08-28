#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <sstream>
#include <vector>
#include <iomanip>
#include <filesystem>
#include <system_error>

namespace fs = std::filesystem;

struct SysMemInfo {
    unsigned long mem_total_kb = 0;
    unsigned long mem_free_kb = 0;
    unsigned long mem_avail_kb = 0;
    unsigned long dirty_kb = 0;
    unsigned long sreclaim_kb = 0;
    double psi_some_avg10 = 0.0;
    double psi_full_avg10 = 0.0;
};

struct ProcMemInfo {
    pid_t pid = 0;
    unsigned long vsz_kb = 0;
    unsigned long rss_kb = 0;
    unsigned long pss_kb = 0;
    unsigned long priv_clean_kb = 0;
    unsigned long priv_dirty_kb = 0;
    unsigned long shared_clean_kb = 0;
    unsigned long shared_dirty_kb = 0;
    unsigned long swap_kb = 0;
    unsigned long swap_pss_kb = 0;
    int oom_score = 0;
    int oom_score_adj = 0;
};

class MemoryInspector {
public:
    static bool inspect(pid_t pid, SysMemInfo& sys, ProcMemInfo& proc) {
        if (!read_sys_mem(sys)) return false;
        if (!read_proc_mem(pid, proc)) return false;
        return true;
    }

    static void print_report(const SysMemInfo& sys, const ProcMemInfo& proc) {
        const unsigned long uss_kb = proc.priv_clean_kb + proc.priv_dirty_kb;
        const unsigned long shared_total_kb = proc.shared_clean_kb + proc.shared_dirty_kb;

        std::cout << "===================================================================\n";
        std::cout << "  ЗВЕДЕНИЙ ЗВІТ СПОЖИВАННЯ ПАМ'ЯТІ ДЛЯ PID " << proc.pid << "\n";
        std::cout << "===================================================================\n\n";

        std::cout << "--- [1] СИСТЕМНИЙ КОНТЕКСТ (/proc/meminfo, PSI) ---\n";
        std::cout << "  RAM Загалом:     " << std::setw(8) << (sys.mem_total_kb / 1024)
                  << " МіБ | Вільна (Free):   " << std::setw(8) << (sys.mem_free_kb / 1024) << " МіБ\n";
        std::cout << "  Доступна (Avail):" << std::setw(8) << (sys.mem_avail_kb / 1024)
                  << " МіБ | Брудна (Dirty):  " << std::setw(8) << (sys.dirty_kb / 1024) << " МіБ\n";
        std::cout << "  Slab (Reclaim):  " << std::setw(8) << (sys.sreclaim_kb / 1024)
                  << " МіБ | Тиск PSI (10с):  some=" << std::fixed << std::setprecision(2)
                  << sys.psi_some_avg10 << "% full=" << sys.psi_full_avg10 << "%\n\n";

        std::cout << "--- [2] СТАН АДРЕСНОГО ПРОСТОРУ ПРОЦЕСУ ---\n";
        std::cout << "  VSZ (Віртуальний): " << std::setw(8) << (proc.vsz_kb / 1024) << " МіБ  (довжина карти адрес VMA)\n";
        std::cout << "  RSS (Резидентний): " << std::setw(8) << (proc.rss_kb / 1024) << " МіБ  (заселені сторінки в PTE)\n";
        std::cout << "  PSS (Пропорційний):" << std::setw(8) << (proc.pss_kb / 1024) << " МіБ  (чесна частка: USS + Shared/N)\n";
        std::cout << "  USS (Винятковий):  " << std::setw(8) << (uss_kb / 1024) << " МіБ  (належить виключно процесу)\n\n";

        std::cout << "--- [3] РОЗКЛАДКА СТОРІНОК ЗА СТАТУСОМ ЗВІЛЬНЕННЯ ---\n";
        std::cout << "  Приватні брудні (Private_Dirty): " << std::setw(8) << (proc.priv_dirty_kb / 1024)
                  << " МіБ  [КУПА/СТЕК: вивільнення в RAM негайне]\n";
        std::cout << "  Приватні чисті  (Private_Clean): " << std::setw(8) << (proc.priv_clean_kb / 1024)
                  << " МіБ  [КОД/ФАЙЛИ: скидаються без запису]\n";
        std::cout << "  Спільні сторінки (Shared Total): " << std::setw(8) << (shared_total_kb / 1024)
                  << " МіБ  [LIBC/SHMEM: спільні з іншими]\n";
        std::cout << "  Витіснено в своп (Swap / SwapPSS):" << std::setw(7) << (proc.swap_kb / 1024)
                  << " / " << (proc.swap_pss_kb / 1024) << " МіБ\n\n";

        std::cout << "--- [4] ОЦІНКА РИЗИКУ ТА ПОВЕДІНКИ OOM-KILLER ---\n";
        std::cout << "  Поточний OOM Score:     " << std::setw(5) << proc.oom_score << " (бали ймовірності: 0..1000)\n";
        std::cout << "  Поправка OOM Score Adj: " << std::setw(5) << proc.oom_score_adj << " (пріоритет: -1000..+1000)\n";
        std::cout << "  Реальний виграш від ліквідації: " << (proc.priv_dirty_kb / 1024) << " МіБ фізичної RAM\n";
        std::cout << "===================================================================\n";
    }

private:
    static bool read_sys_mem(SysMemInfo& sys) {
        std::ifstream meminfo("/proc/meminfo");
        if (!meminfo.is_open()) return false;

        std::string line;
        while (std::getline(meminfo, line)) {
            parse_kb(line, "MemTotal:", sys.mem_total_kb);
            parse_kb(line, "MemFree:", sys.mem_free_kb);
            parse_kb(line, "MemAvailable:", sys.mem_avail_kb);
            parse_kb(line, "Dirty:", sys.dirty_kb);
            parse_kb(line, "SReclaimable:", sys.sreclaim_kb);
        }

        std::ifstream psi("/proc/pressure/memory");
        if (psi.is_open()) {
            std::string p_line;
            while (std::getline(psi, p_line)) {
                if (p_line.rfind("some", 0) == 0) {
                    parse_psi(p_line, sys.psi_some_avg10);
                } else if (p_line.rfind("full", 0) == 0) {
                    parse_psi(p_line, sys.psi_full_avg10);
                }
            }
        }
        return true;
    }

    static bool read_proc_mem(pid_t pid, ProcMemInfo& proc) {
        proc.pid = pid;
        const std::string proc_dir = "/proc/" + std::to_string(pid);

        std::ifstream smaps(proc_dir + "/smaps_rollup");
        if (!smaps.is_open()) return false;

        std::string line;
        while (std::getline(smaps, line)) {
            parse_kb(line, "Rss:", proc.rss_kb);
            parse_kb(line, "Pss:", proc.pss_kb);
            parse_kb(line, "Private_Clean:", proc.priv_clean_kb);
            parse_kb(line, "Private_Dirty:", proc.priv_dirty_kb);
            parse_kb(line, "Shared_Clean:", proc.shared_clean_kb);
            parse_kb(line, "Shared_Dirty:", proc.shared_dirty_kb);
            parse_kb(line, "Swap:", proc.swap_kb);
            parse_kb(line, "SwapPss:", proc.swap_pss_kb);
        }

        std::ifstream status(proc_dir + "/status");
        if (status.is_open()) {
            while (std::getline(status, line)) {
                parse_kb(line, "VmSize:", proc.vsz_kb);
            }
        }

        std::ifstream oom_score_file(proc_dir + "/oom_score");
        if (oom_score_file.is_open()) oom_score_file >> proc.oom_score;

        std::ifstream oom_adj_file(proc_dir + "/oom_score_adj");
        if (oom_adj_file.is_open()) oom_adj_file >> proc.oom_score_adj;

        return true;
    }

    static void parse_kb(const std::string& line, std::string_view key, unsigned long& value) {
        if (line.rfind(key, 0) == 0) {
            std::istringstream iss(line.substr(key.length()));
            iss >> value;
        }
    }

    static void parse_psi(const std::string& line, double& avg10) {
        auto pos = line.find("avg10=");
        if (pos != std::string::npos) {
            std::istringstream iss(line.substr(pos + 6));
            iss >> avg10;
        }
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <PID>\n";
        return 1;
    }

    const pid_t pid = std::stoi(argv[1]);
    if (pid <= 0) {
        std::cerr << "Помилка: некоректний PID\n";
        return 1;
    }

    SysMemInfo sys;
    ProcMemInfo proc;
    if (!MemoryInspector::inspect(pid, sys, proc)) {
        std::cerr << "Помилка читання метрик для PID " << pid << "\n";
        return 1;
    }

    MemoryInspector::print_report(sys, proc);
    return 0;
}
