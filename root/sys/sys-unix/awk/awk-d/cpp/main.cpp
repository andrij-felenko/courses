#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <iomanip>

// Підрахунок суми другого стовпця мовою C++
int main(int argc, char **argv) {
    std::ifstream file;
    std::istream &in = (argc > 1) ? (file.open(argv[1]), file) : std::cin;
    if (!in) {
        std::cerr << "Не вдалося відкрити вхідний потік\n";
        return 1;
    }

    std::string line;
    double total = 0.0;

    while (std::getline(in, line)) {
        std::istringstream iss(line);
        std::string col1;
        double col2;
        if (iss >> col1 >> col2) {
            total += col2;
        }
    }

    std::cout << "Total: " << std::fixed << std::setprecision(2) << total << "\n";
    return 0;
}
