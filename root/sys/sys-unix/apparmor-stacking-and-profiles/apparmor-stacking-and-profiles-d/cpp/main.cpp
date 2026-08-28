// cpp
#include <iostream>
#include <string_view>
#include <vector>
#include <format>
#include <expected>
#include <cstring>
#include <cerrno>
#include <cstdlib>
#include <unistd.h>
#include <sys/apparmor.h>

class AppArmorStackManager {
public:
    static std::expected<void, std::string> schedule_stack(
        std::string_view base_profile, 
        std::string_view stacked_profile
    ) {
        std::string full_spec = std::format("{}//&{}", base_profile, stacked_profile);
        if (::aa_change_onexec(full_spec.c_str()) < 0) {
            return std::unexpected(std::format("Failed aa_change_onexec for target '{}': {}", full_spec, ::strerror(errno)));
        }
        return {};
    }
};

int main() {
    std::cout << std::format("[Process {}] Setting up AppArmor stacked transition...\n", ::getpid());

    auto result = AppArmorStackManager::schedule_stack("docker-default", "restricted_sandbox");
    if (!result) {
        std::cerr << std::format("Error: {}\n", result.error());
        return EXIT_FAILURE;
    }

    std::cout << "Transition scheduled. Invoking execvp...\n";
    std::vector<const char*> args = { "/usr/bin/worker_bin", nullptr };
    ::execvp(args[0], const_cast<char* const*>(args.data()));

    std::perror("execvp failed");
    return EXIT_FAILURE;
}
