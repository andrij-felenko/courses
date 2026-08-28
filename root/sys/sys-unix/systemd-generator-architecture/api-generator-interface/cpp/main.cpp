// Приклад використання внутрішніх C-функцій systemd generator API у C++
#include <cstdlib>
#include <iostream>

extern "C" {
#include "generator.h"
}

int main(int argc, char *argv[]) {
    const char *normal_dir = nullptr;
    const char *early_dir = nullptr;
    const char *late_dir = nullptr;

    int r = generator_open_output_dirs(argc, argv, &normal_dir, &early_dir, &late_dir);
    if (r < 0) {
        std::cerr << "Не вдалося відкрити каталоги виводу генератора\n";
        return EXIT_FAILURE;
    }

    FILE *f = nullptr;
    r = generator_open_unit_file(normal_dir, nullptr, "my-gen.service", &f);
    if (r < 0 || !f) {
        std::cerr << "Не вдалося створити unit-файл через sd-generator API\n";
        return EXIT_FAILURE;
    }

    std::fprintf(f,
        "[Unit]\n"
        "Description=Generated via sd-generator C++ wrapper\n");
    std::fclose(f);

    r = generator_add_symlink(normal_dir, "multi-user.target", "wants", "my-gen.service");
    if (r < 0) {
        std::cerr << "Не вдалося створити symlink через sd-generator API\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
