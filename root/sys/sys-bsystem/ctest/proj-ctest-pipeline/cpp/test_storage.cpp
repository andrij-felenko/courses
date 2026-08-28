// tests/integration/test_storage.cpp
#include <iostream>
#include <fstream>
#include <string>
#include "calculator.hpp"

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Помилка: відсутній шлях до тестової БД\n";
        return 1;
    }

    std::string db_file = argv[1];
    std::cout << "[INTEGRATION] Запуск перевірки запису в " << db_file << "\n";

    engine::Calculator calc;
    bool ok = calc.write_record(db_file, 42, 3.14159);
    if (!ok) {
        std::cerr << "[FAIL] Не вдалося додати запис у сховище\n";
        return 2;
    }

    std::ifstream in(db_file);
    std::string line;
    bool found = false;
    while (std::getline(in, line)) {
        if (line.find("42:3.14159") != std::string::npos) {
            found = true;
            break;
        }
    }

    if (!found) {
        std::cerr << "[FAIL] Запис не знайдено в базі даних\n";
        return 3;
    }

    std::cout << "[PASS] Інтеграційний тест пройдено успішно.\n";
    return 0;
}
