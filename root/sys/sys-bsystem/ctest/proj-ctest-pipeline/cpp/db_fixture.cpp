// tests/integration/db_fixture.cpp
#include <iostream>
#include <fstream>
#include <string_view>
#include <filesystem>

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: db_fixture_runner --setup|--cleanup <db_path>\n";
        return 1;
    }

    std::string_view mode = argv[1];
    std::filesystem::path db_path = argv[2];

    if (mode == "--setup") {
        std::cout << "[FIXTURE] Ініціалізація тестового сховища: " << db_path << "\n";
        std::ofstream db_file(db_path, std::ios::trunc);
        if (!db_file) {
            std::cerr << "[FIXTURE ERROR] Не вдалося створити файл БД!\n";
            return 2;
        }
        db_file << "SCHEMA_VERSION=1\n";
        return 0; // Успішна підготовка
    }

    if (mode == "--cleanup") {
        std::cout << "[FIXTURE] Видалення тимчасового сховища: " << db_path << "\n";
        std::error_code ec;
        std::filesystem::remove(db_path, ec);
        return 0; // Очищення завершено
    }

    std::cerr << "[FIXTURE ERROR] Невідомий режим: " << mode << "\n";
    return 3;
}
