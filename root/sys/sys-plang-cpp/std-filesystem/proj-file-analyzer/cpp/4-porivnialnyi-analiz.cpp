// Modern C++: Клін-код із RAII та ітераторами
#include <filesystem>
#include <iostream>

namespace fs = std::filesystem;

void scan_cpp_dir(const fs::path& dir_path) {
    std::error_code ec;
    auto options = fs::directory_options::skip_permission_denied;

    for (const auto& entry : fs::recursive_directory_iterator(dir_path, options, ec)) {
        if (entry.is_regular_file(ec)) {
            std::cout << "File: " << entry.path() << ", Size: " << entry.file_size(ec) << "\n";
        }
    }
    // Автоматичне звільнення системних ресурсів через деструктор ітератора
}
