#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include "calc/math_ops.h"

#ifndef APP_DATADIR
#define APP_DATADIR "/usr/local/share/calcapp"
#endif

int main(int argc, char* argv[]) {
    namespace fs = std::filesystem;
    const fs::path asset_path = fs::path(APP_DATADIR) / "operations.json";

    std::ifstream file(asset_path);
    if (!file.is_open()) {
        std::cerr << "Помилка: не знайдено файл конфігурації за шляхом: " 
                  << asset_path << '\n';
        return 1;
    }

    std::cout << "Конфігурацію успішно завантажено з: " << asset_path << '\n';
    std::cout << "Розрахунок: 12 + 30 = " << calc_add(12, 30) << '\n';
    return 0;
}
