#include "link_budget.hpp"
#include <iostream>
#include <string>

int main(int argc, char* argv[]) {
    try {
        rf::LinkParameters params;

        for (int i = 1; i < argc; ++i) {
            std::string arg = argv[i];
            if (arg == "-f" && i + 1 < argc) {
                params.freq_mhz = std::stod(argv[++i]);
            } else if (arg == "-d" && i + 1 < argc) {
                params.distance_km = std::stod(argv[++i]);
            } else if (arg == "-p" && i + 1 < argc) {
                params.tx_power_dbm = std::stod(argv[++i]);
            } else if (arg == "-s" && i + 1 < argc) {
                params.rx_sensitivity_dbm = std::stod(argv[++i]);
            } else if (arg == "-h" || arg == "--help") {
                std::cout << "Використання: " << argv[0] << " [-f МГц] [-d км] [-p дБм] [-s дБм]\n";
                return 0;
            }
        }

        rf::LinkBudget budget(params);
        rf::LinkReport report = budget.evaluate();
        std::cout << report.format();

    } catch (const std::exception& e) {
        std::cerr << "Помилка розрахунку: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
