#include <iostream>
#include <fstream>
#include <string>
#include <filesystem>
#include <iomanip>

namespace fs = std::filesystem;

int main(int argc, char* argv[]) {
    std::string dev_name = (argc > 1) ? argv[1] : "10040000.bus-controller";
    fs::path base_path = fs::path("/sys/class/devfreq") / dev_name;

    fs::path cur_freq_file = base_path / "cur_freq";
    std::ifstream cur_file(cur_freq_file);
    if (!cur_file.is_open()) {
        std::cerr << "Помилка відкриття " << cur_freq_file << std::endl;
        return 1;
    }

    unsigned long long freq = 0;
    if (cur_file >> freq) {
        std::cout << "Пристрій: " << dev_name << "\n"
                  << "Поточна частота: " << std::fixed << std::setprecision(2)
                  << (static_cast<double>(freq) / 1e6) << " МГц\n";
    }

    fs::path trans_stat_file = base_path / "trans_stat";
    std::ifstream trans_file(trans_stat_file);
    if (trans_file.is_open()) {
        std::cout << "\n--- Статистика переходів частот ---\n";
        std::string line;
        while (std::getline(trans_file, line)) {
            std::cout << line << "\n";
        }
    }

    return 0;
}
