#include <iostream>
#include <cstdlib>
#include <string_view>
#include <filesystem>

void audit_environment() {
    const char* path_raw = std::getenv("PATH");
    const char* home_raw = std::getenv("HOME");
    const char* user_raw = std::getenv("USER");

    std::string_view path = path_raw ? path_raw : "(NOT SET - CRITICAL)";
    std::string_view home = home_raw ? home_raw : "(NOT SET - FALLBACK TO /)";
    std::string_view user = user_raw ? user_raw : "(NOT SET)";

    std::cout << "[ENV AUDIT]\n"
              << "  PATH: " << path << "\n"
              << "  HOME: " << home << "\n"
              << "  USER: " << user << "\n";

    if (!home_raw) {
        setenv("HOME", "/tmp", 1);
    }
}
