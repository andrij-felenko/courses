#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <expected>
#include <system_error>
#include <filesystem>

namespace fs = std::filesystem;

enum class AppArmorMode {
    Unconfined,
    Enforce,
    Complain
};

struct ProfileInfo {
    std::string profile_name;
    AppArmorMode mode;
};

std::expected<ProfileInfo, std::error_code> get_current_apparmor_profile() {
    const fs::path primary_path{"/proc/self/attr/apparmor/current"};
    const fs::path fallback_path{"/proc/self/attr/current"};

    fs::path target_path = fs::exists(primary_path) ? primary_path : fallback_path;

    std::ifstream attr_file(target_path);
    if (!attr_file.is_open()) {
        return std::unexpected(std::make_error_code(std::errc::no_such_file_or_directory));
    }

    std::string raw_content;
    std::getline(attr_file, raw_content);

    if (raw_content.empty() || raw_content == "unconfined") {
        return ProfileInfo{.profile_name = "unconfined", .mode = AppArmorMode::Unconfined};
    }

    constexpr std::string_view complain_suffix = " (complain)";
    constexpr std::string_view enforce_suffix = " (enforce)";

    if (auto pos = raw_content.find(complain_suffix); pos != std::string::npos) {
        return ProfileInfo{
            .profile_name = raw_content.substr(0, pos),
            .mode = AppArmorMode::Complain
        };
    }

    if (auto pos = raw_content.find(enforce_suffix); pos != std::string::npos) {
        return ProfileInfo{
            .profile_name = raw_content.substr(0, pos),
            .mode = AppArmorMode::Enforce
        };
    }

    return ProfileInfo{.profile_name = raw_content, .mode = AppArmorMode::Enforce};
}

int main() {
    auto result = get_current_apparmor_profile();
    if (!result) {
        std::cerr << "Не вдалося зчитати профіль AppArmor: " 
                  << result.error().message() << '\n';
        return 1;
    }

    const auto& [name, mode] = *result;
    switch (mode) {
        case AppArmorMode::Unconfined:
            std::cout << "Процес працює поза контролем AppArmor (unconfined).\n";
            break;
        case AppArmorMode::Complain:
            std::cout << "Активний профіль: '" << name << "' [COMPLAIN]\n";
            break;
        case AppArmorMode::Enforce:
            std::cout << "Активний профіль: '" << name << "' [ENFORCE]\n";
            break;
    }

    return 0;
}
