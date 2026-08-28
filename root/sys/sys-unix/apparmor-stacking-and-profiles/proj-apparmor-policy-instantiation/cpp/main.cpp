// cpp
#include <iostream>
#include <cstdio>
#include <cstring>
#include <cerrno>
#include <cstdlib>
#include <memory>
#include <string>
#include <string_view>
#include <vector>
#include <format>
#include <filesystem>
#include <expected>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <sys/apparmor.h>

namespace fs = std::filesystem;

class AppArmorPolicyEngine {
public:
    static std::expected<void, std::string> load_instantiated_profile(
        std::string_view profile_name, 
        const fs::path& sandbox_path
    ) {
        std::string profile_content = std::format(
            "profile {} flags=(attach_disconnected) {{\n"
            "  file,\n"
            "  deny /etc/shadow rw,\n"
            "  {} r,\n"
            "  {}/** rw,\n"
            "}}\n",
            profile_name, sandbox_path.string(), sandbox_path.string()
        );

        // Ядро приймає в .load лише скомпільований образ політики,
        // тож текст віддаємо apparmor_parser: він компілює й завантажує його сам.
        std::unique_ptr<std::FILE, decltype(&::pclose)> parser(
            ::popen("apparmor_parser --quiet --replace", "w"), &::pclose);
        if (!parser) {
            return std::unexpected(std::format("Cannot start apparmor_parser: {}", ::strerror(errno)));
        }

        if (std::fwrite(profile_content.data(), 1, profile_content.size(), parser.get())
                != profile_content.size()) {
            return std::unexpected("Incomplete profile text written into apparmor_parser");
        }

        const int status = ::pclose(parser.release());
        if (status != 0) {
            return std::unexpected(std::format("apparmor_parser exited with status {}", status));
        }

        return {};
    }

    static std::expected<void, std::string> schedule_stacked_transition(
        std::string_view base_profile, 
        std::string_view target_profile
    ) {
        std::string stack_spec = std::format("{}//&{}", base_profile, target_profile);
        if (::aa_change_onexec(stack_spec.c_str()) < 0) {
            return std::unexpected(std::format("aa_change_onexec failed for '{}': {}", stack_spec, ::strerror(errno)));
        }
        return {};
    }
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << std::format("Usage: {} <profile_name> <sandbox_dir>\n", argv[0]);
        return EXIT_FAILURE;
    }

    std::string profile_name = argv[1];
    fs::path sandbox_dir = argv[2];

    std::cout << std::format("[C++ Engine] Instantiating policy '{}' for path '{}'...\n", profile_name, sandbox_dir.string());

    auto load_res = AppArmorPolicyEngine::load_instantiated_profile(profile_name, sandbox_dir);
    if (!load_res) {
        std::cerr << std::format("[C++ Engine] Error: {}\n", load_res.error());
        return EXIT_FAILURE;
    }

    auto stack_res = AppArmorPolicyEngine::schedule_stacked_transition("docker-default", profile_name);
    if (!stack_res) {
        std::cerr << std::format("[C++ Engine] Error: {}\n", stack_res.error());
        return EXIT_FAILURE;
    }

    std::cout << "[C++ Engine] Transition scheduled successfully. Executing worker binary...\n";

    std::vector<const char*> exec_args = { "/bin/bash", "-c", "echo 'Worker process running under stacked AppArmor profile'; id", nullptr };
    ::execvp(exec_args[0], const_cast<char* const*>(exec_args.data()));

    std::perror("[C++ Engine] execvp failed");
    return EXIT_FAILURE;
}
