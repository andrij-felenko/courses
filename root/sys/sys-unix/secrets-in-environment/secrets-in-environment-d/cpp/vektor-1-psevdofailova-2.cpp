// Ідіоматичне читання середовища процесу через std::filesystem та std::string мовою C++
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <filesystem>
#include <system_error>

void dump_process_environ(int target_pid) {
    const std::filesystem::path proc_path = "/proc/" + std::to_string(target_pid) + "/environ";
    
    std::ifstream file(proc_path, std::ios::binary);
    if (!file.is_open()) {
        std::cerr << "Не вдалося відкрити " << proc_path << '\n';
        return;
    }

    std::string entry;
    while (std::getline(file, entry, '\0')) {
        if (!entry.empty()) {
            std::cout << "[ENV] " << entry << '\n';
        }
    }
}
