// hermetic_sandbox.cpp - герметичний раннер дій компіляції на C++20
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <expected>
#include <fstream>
#include <filesystem>
#include <system_error>

#include <unistd.h>
#include <sched.h>
#include <sys/mount.h>
#include <sys/stat.h>

namespace fs = std::filesystem;

namespace sandbox {

class HermeticEnvironment {
public:
    explicit HermeticEnvironment(fs::path root_directory)
        : root_path_(std::move(root_directory)) {}

    ~HermeticEnvironment() = default;

    [[nodiscard]] std::expected<void, std::string> setup_namespaces_and_mounts() {
        const uid_t host_uid = getuid();
        const gid_t host_gid = getgid();

        constexpr int clone_flags = CLONE_NEWUSER | CLONE_NEWNS | CLONE_NEWNET | CLONE_NEWIPC | CLONE_NEWUTS;
        if (unshare(clone_flags) != 0) {
            return std::unexpected("unshare() failed: " + std::string(strerror(errno)));
        }

        if (auto res = initialize_user_mapping(host_uid, host_gid); !res) {
            return res;
        }

        // Забезпечуємо приватність усіх точок монтування
        if (mount(nullptr, "/", nullptr, MS_REC | MS_PRIVATE, nullptr) != 0) {
            return std::unexpected("mount(MS_PRIVATE) failed: " + std::string(strerror(errno)));
        }

        std::error_code ec;
        fs::create_directories(root_path_, ec);
        if (ec) {
            return std::unexpected("create_directories failed: " + ec.message());
        }

        if (mount("tmpfs", root_path_.c_str(), "tmpfs", 0, "size=128M,mode=0755") != 0) {
            return std::unexpected("mount tmpfs failed: " + std::string(strerror(errno)));
        }

        fs::create_directories(root_path_ / "src", ec);
        fs::create_directories(root_path_ / "out", ec);
        fs::create_directories(root_path_ / "tmp", ec);

        return {};
    }

    [[nodiscard]] std::expected<void, std::string> bind_inputs_readonly(const fs::path& host_inputs) {
        const auto target = root_path_ / "src";
        if (mount(host_inputs.c_str(), target.c_str(), nullptr, MS_BIND | MS_REC, nullptr) != 0) {
            return std::unexpected("bind mount inputs failed: " + std::string(strerror(errno)));
        }
        if (mount(nullptr, target.c_str(), nullptr, MS_BIND | MS_REMOUNT | MS_RDONLY | MS_REC, nullptr) != 0) {
            return std::unexpected("remount inputs read-only failed: " + std::string(strerror(errno)));
        }
        return {};
    }

    [[nodiscard]] std::expected<void, std::string> bind_outputs_readwrite(const fs::path& host_outputs) {
        const auto target = root_path_ / "out";
        if (mount(host_outputs.c_str(), target.c_str(), nullptr, MS_BIND | MS_REC, nullptr) != 0) {
            return std::unexpected("bind mount outputs failed: " + std::string(strerror(errno)));
        }
        return {};
    }

    [[nodiscard]] std::expected<void, std::string> execute(std::span<char*> arguments) {
        if (chroot(root_path_.c_str()) != 0) {
            return std::unexpected("chroot failed: " + std::string(strerror(errno)));
        }
        if (chdir("/src") != 0) {
            return std::unexpected("chdir(/src) failed: " + std::string(strerror(errno)));
        }

        char* const sanitized_env[] = {
            const_cast<char*>("PATH=/bin:/usr/bin"),
            const_cast<char*>("LANG=C.UTF-8"),
            const_cast<char*>("LC_ALL=C.UTF-8"),
            const_cast<char*>("TMPDIR=/tmp"),
            nullptr
        };

        execvpe(arguments.front(), arguments.data(), sanitized_env);
        return std::unexpected("execvpe failed: " + std::string(strerror(errno)));
    }

private:
    fs::path root_path_;

    static std::expected<void, std::string> write_file(const fs::path& file_path, std::string_view payload) {
        std::ofstream stream(file_path);
        if (!stream.is_open()) {
            return std::unexpected("Не вдалося відкрити " + file_path.string());
        }
        stream << payload;
        if (!stream.good()) {
            return std::unexpected("Не вдалося записати " + file_path.string());
        }
        return {};
    }

    static std::expected<void, std::string> initialize_user_mapping(uid_t uid, gid_t gid) {
        if (auto res = write_file("/proc/self/setgroups", "deny"); !res) {
            return res;
        }
        if (auto res = write_file("/proc/self/uid_map", "0 " + std::to_string(uid) + " 1\n"); !res) {
            return res;
        }
        if (auto res = write_file("/proc/self/gid_map", "0 " + std::to_string(gid) + " 1\n"); !res) {
            return res;
        }
        return {};
    }
};

} // namespace sandbox

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Використання: " << argv[0] << " <каталог_входів> <каталог_виходів> <команда> [аргументи...]\n";
        return 1;
    }

    const fs::path inputs_path = argv[1];
    const fs::path outputs_path = argv[2];
    std::vector<char*> arguments(&argv[3], &argv[argc]);
    arguments.push_back(nullptr);

    sandbox::HermeticEnvironment env("/tmp/hermetic_sandbox_root");

    if (auto res = env.setup_namespaces_and_mounts(); !res) {
        std::cerr << "Помилка конфігурації: " << res.error() << "\n";
        return 1;
    }

    if (auto res = env.bind_inputs_readonly(inputs_path); !res) {
        std::cerr << "Помилка підключення входів: " << res.error() << "\n";
        return 1;
    }

    if (auto res = env.bind_outputs_readwrite(outputs_path); !res) {
        std::cerr << "Помилка підключення виходів: " << res.error() << "\n";
        return 1;
    }

    if (auto res = env.execute(std::span<char*>(arguments.data(), arguments.size() - 1)); !res) {
        std::cerr << "Помилка запуску команди: " << res.error() << "\n";
        return 1;
    }

    return 0;
}
