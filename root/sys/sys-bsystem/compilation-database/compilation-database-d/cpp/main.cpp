// Ідіоматична робота з базою компіляції через офіційний C++ API Clang LibTooling
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <vector>

#include <clang/Tooling/CompilationDatabase.h>
#include <clang/Tooling/Tooling.h>
#include <llvm/Support/raw_ostream.h>

void inspect_compilation_database(std::string_view build_directory) {
    std::string error_message;
    
    // Завантаження бази компіляції з каталогу збірки (RAII та безпечне керування пам'яттю)
    std::unique_ptr<clang::tooling::CompilationDatabase> compdb =
        clang::tooling::CompilationDatabase::loadFromDirectory(
            std::string(build_directory), error_message);

    if (!compdb) {
        llvm::errs() << "Помилка завантаження бази даних: " << error_message << "\n";
        return;
    }

    // Отримання списку всіх файлів, зареєстрованих у базі
    std::vector<std::string> all_files = compdb->getAllFiles();
    std::cout << "Знайдено одиниць трансляції в базі: " << all_files.size() << "\n\n";

    for (const auto& file_path : all_files) {
        std::cout << "Файл: " << file_path << "\n";

        // Отримання точних команд компіляції для конкретного файлу
        std::vector<clang::tooling::CompileCommand> commands =
            compdb->getCompileCommands(file_path);

        for (const auto& cmd : commands) {
            std::cout << "  Робочий каталог: " << cmd.Directory << "\n";
            std::cout << "  Вихідний артефакт: " << cmd.Output << "\n";
            std::cout << "  Аргументи виклику (" << cmd.CommandLine.size() << " токенів):\n";
            
            for (const auto& arg : cmd.CommandLine) {
                std::cout << "    " << arg << "\n";
            }
        }
        std::cout << "----------------------------------------\n";
    }
}

int main(int argc, char** argv) {
    std::string build_dir = (argc > 1) ? argv[1] : "build";
    inspect_compilation_database(build_dir);
    return 0;
}
