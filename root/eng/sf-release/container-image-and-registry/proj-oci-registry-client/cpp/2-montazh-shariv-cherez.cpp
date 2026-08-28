#include <iostream>
#include <string>
#include <vector>
#include <string_view>
#include <numeric>
#include <sys/mount.h>
#include <cerrno>
#include <cstring>
#include <stdexcept>
#include <filesystem>

namespace fs = std::filesystem;

class OverlayRootfsMount {
public:
    static void mount_layers(const std::vector<fs::path>& lower_dirs,
                             const fs::path& upper_dir,
                             const fs::path& work_dir,
                             const fs::path& merged_target) {
        if (lower_dirs.empty()) {
            throw std::invalid_argument("Масив lower_dirs не може бути порожнім");
        }

        // Формування рядка опцій lowerdir=dir1:dir2:dir3
        std::string lower_opt = "lowerdir=";
        for (size_t i = 0; i < lower_dirs.size(); ++i) {
            lower_opt += lower_dirs[i].string();
            if (i + 1 < lower_dirs.size()) {
                lower_opt += ":";
            }
        }

        std::string options = lower_opt + 
                              ",upperdir=" + upper_dir.string() + 
                              ",workdir=" + work_dir.string();

        // Створення цільової точки монтування
        fs::create_directories(merged_target);

        int res = ::mount("overlay", merged_target.c_str(), "overlay", 0, options.c_str());
        if (res != 0) {
            throw std::runtime_error("Системна помилка mount OverlayFS: " + 
                                     std::string(std::strerror(errno)));
        }

        std::cout << "[OK] OverlayFS змонтовано: " << merged_target 
                  << " (lowerdir count: " << lower_dirs.size() << ")\n";
    }

    static void unmount_rootfs(const fs::path& merged_target) {
        if (::umount2(merged_target.c_str(), MNT_DETACH) != 0) {
            throw std::runtime_error("Помилка розмонтування umount2: " + 
                                     std::string(std::strerror(errno)));
        }
        std::cout << "[OK] Розмонтовано rootfs: " << merged_target << "\n";
    }
};
