#include <gsl/gsl>
#include <cstdio>
#include <vector>

// Сучасний C++ Scope Guard на базі gsl::finally
int process_file_cpp(gsl::czstring filename) {
    FILE* f = std::fopen(filename, "rb");
    if (!f) return -1;

    // Гарантоване закриття дескриптора при будь-якому виході з функції
    auto file_guard = gsl::finally([f] {
        std::fclose(f);
    });

    std::vector<gsl::byte> buffer(1024);
    if (std::fread(buffer.data(), 1, buffer.size(), f) != buffer.size()) {
        return -3; // file_guard автоматично викличе fclose(f)
    }

    return 0; // file_guard автоматично викличе fclose(f)
}
