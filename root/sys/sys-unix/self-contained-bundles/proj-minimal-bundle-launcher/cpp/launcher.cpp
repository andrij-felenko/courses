// launcher.cpp — Ідіоматичний лаунчер пакунка мовою C++20
#include <iostream>
#include <string>
#include <vector>
#include <filesystem>
#include <expected>
#include <system_error>
#include <cstdlib>
#include <cerrno>
#include <unistd.h>
#include <sched.h>
#include <sys/mount.h>
#include <sys/stat.h>

namespace fs = std::filesystem;

// RAII-обгортка для гарантованого прибирання точок монтажу та тимчасових тек
class ScopedMountGuard {
public:
    explicit ScopedMountGuard(fs::path mount_point)
        : mount_point_(std::move(mount_point)), is_mounted_(false) {}

    ~ScopedMountGuard() {
        if (is_mounted_) {
            // Демонтування у режимі MNT_DETACH (lazy unmount)
            umount2(mount_point_.c_str(), MNT_DETACH);
        }
        std::error_code ec;
        fs::remove(mount_point_, ec);
    }

    void mark_mounted() noexcept { is_mounted_ = true; }

    // Заборона копіювання
    ScopedMountGuard(const ScopedMountGuard&) = delete;
    ScopedMountGuard& operator=(const ScopedMountGuard&) = delete;

private:
    fs::path mount_point_;
    bool is_mounted_;
};

enum class LauncherError {
    InsufficientArguments,
    NamespaceCreationFailed,
    MountPropagationFailed,
    DirectoryCreationFailed,
    BindMountFailed,
    EnvironmentSetupFailed,
    ExecutionFailed
};

std::string error_to_string(LauncherError err) {
    switch (err) {
        case LauncherError::InsufficientArguments: return "Недостатньо аргументів командного рядка.";
        case LauncherError::NamespaceCreationFailed: return "Помилка створення Mount Namespace (потрібні привілеї або unprivileged user namespace).";
        case LauncherError::MountPropagationFailed: return "Не вдалося перевести точки монтажу в MS_PRIVATE.";
        case LauncherError::DirectoryCreationFailed: return "Не вдалося створити каталог для точки монтажу.";
        case LauncherError::BindMountFailed: return "Не вдалося виконати bind-mount джерела пакунка.";
        case LauncherError::EnvironmentSetupFailed: return "Не вдалося оновити змінні середовища.";
        case LauncherError::ExecutionFailed: return "Системний виклик execv завершився з помилкою.";
    }
    return "Невідома помилка.";
}

class BundleLauncher {
public:
    static std::expected<void, LauncherError> run(const fs::path& bundle_source, const std::vector<std::string>& user_args) {
        // Крок 1: Ізоляція простору імен монтажу
        if (unshare(CLONE_NEWNS) != 0) {
            return std::unexpected(LauncherError::NamespaceCreationFailed);
        }

        // Крок 2: Режим MS_PRIVATE для унеможливлення витоків у хост-систему
        if (mount(nullptr, "/", nullptr, MS_PRIVATE | MS_REC, nullptr) != 0) {
            return std::unexpected(LauncherError::MountPropagationFailed);
        }

        const fs::path target_mount = "/tmp/cpp_bundle_target";
        ScopedMountGuard guard(target_mount);

        std::error_code ec;
        fs::create_directories(target_mount, ec);
        if (ec) {
            return std::unexpected(LauncherError::DirectoryCreationFailed);
        }

        // Крок 3: Виконання bind-mount
        if (mount(bundle_source.c_str(), target_mount.c_str(), nullptr, MS_BIND | MS_REC, nullptr) != 0) {
            return std::unexpected(LauncherError::BindMountFailed);
        }
        guard.mark_mounted();

        // Крок 4: Налаштування змінних оточення
        if (!setup_env(target_mount)) {
            return std::unexpected(LauncherError::EnvironmentSetupFailed);
        }

        // Крок 5: Підготовка масиву аргументів
        const fs::path binary_path = target_mount / "usr" / "bin" / "app_main";
        std::vector<char*> raw_args;
        raw_args.reserve(user_args.size() + 2);

        // Буфери для змагання з розпадом покажчиків C-style рядків
        std::string bin_str = binary_path.string();
        raw_args.push_back(bin_str.data());

        std::vector<std::string> arg_buffers = user_args;
        for (auto& arg : arg_buffers) {
            raw_args.push_back(arg.data());
        }
        raw_args.push_back(nullptr);

        std::cout << "[CPP-LAUNCHER] Запуск бінарника " << binary_path << " у пісочниці..." << std::endl;

        execv(binary_path.c_str(), raw_args.data());

        // Якщо execv повернув керування — це помилка
        return std::unexpected(LauncherError::ExecutionFailed);
    }

private:
    static bool setup_env(const fs::path& mount_root) {
        const fs::path lib_dir = mount_root / "usr" / "lib";
        const fs::path bin_dir = mount_root / "usr" / "bin";

        const char* current_ld = std::getenv("LD_LIBRARY_PATH");
        std::string new_ld = lib_dir.string() + (current_ld ? ":" + std::string(current_ld) : "");
        if (setenv("LD_LIBRARY_PATH", new_ld.c_str(), 1) != 0) return false;

        const char* current_path = std::getenv("PATH");
        std::string new_path = bin_dir.string() + (current_path ? ":" + std::string(current_path) : "");
        if (setenv("PATH", new_path.c_str(), 1) != 0) return false;

        return true;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <шлях_до_каталогу_бандла> [аргументи...]" << std::endl;
        return EXIT_FAILURE;
    }

    fs::path bundle_path = argv[1];
    std::vector<std::string> user_args;
    for (int i = 2; i < argc; ++i) {
        user_args.emplace_back(argv[i]);
    }

    auto result = BundleLauncher::run(bundle_path, user_args);
    if (!result) {
        std::cerr << "[ERROR] Помилка запуску: " << error_to_string(result.error())
                  << " (errno: " << strerror(errno) << ")" << std::endl;
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
