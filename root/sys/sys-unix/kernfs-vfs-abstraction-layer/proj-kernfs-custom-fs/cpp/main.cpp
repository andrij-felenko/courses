#include <iostream>
#include <fstream>
#include <string>
#include <filesystem>
#include <system_error>

namespace fs = std::filesystem;

static void read_file(const fs::path& filepath) {
    std::ifstream file(filepath);
    if (!file.is_open()) {
        std::cerr << "Помилка відкриття файлу: " << filepath << '\n';
        return;
    }

    std::cout << "--- Вміст " << filepath << " ---\n";
    std::string line;
    while (std::getline(file, line)) {
        std::cout << line << '\n';
    }
}

static void write_status(const fs::path& filepath, int new_val) {
    std::ofstream file(filepath);
    if (!file.is_open()) {
        std::cerr << "Помилка відкриття для запису: " << filepath << '\n';
        return;
    }

    file << new_val << '\n';
    if (file.good()) {
        std::cout << "Успішно оновлено значення у " << filepath << " на " << new_val << '\n';
    } else {
        std::cerr << "Помилка запису у файл " << filepath << '\n';
    }
}

int main() {
    const fs::path info_path{"/mnt/demo_fs/info"};
    const fs::path status_path{"/mnt/demo_fs/control/status"};

    std::cout << "1. Читання інформаційного вузла:\n";
    read_file(info_path);

    std::cout << "\n2. Поточне значення лічильника:\n";
    read_file(status_path);

    std::cout << "\n3. Оновлення значення лічильника на 750:\n";
    write_status(status_path, 750);

    std::cout << "\n4. Перевірка оновленого значення:\n";
    read_file(status_path);

    return 0;
}
