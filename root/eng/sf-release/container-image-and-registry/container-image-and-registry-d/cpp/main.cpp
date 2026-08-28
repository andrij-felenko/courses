#include <iostream>
#include <string>
#include <string_view>
#include <sys/mount.h>
#include <cerrno>
#include <cstring>
#include <stdexcept>
#include <filesystem>

namespace fs = std::filesystem;

class ContainerRootfsManager {
public:
    static void mount_rootfs(std::string_view lower_layers,
                             const fs::path& upper_dir,
                             const fs::path& work_dir,
                             const fs::path& target_merged) {
        std::string options = "lowerdir=" + std::string(lower_layers) +
                              ",upperdir=" + upper_dir.string() +
                              ",workdir=" + work_dir.string();

        fs::create_directories(target_merged);

        if (::mount("overlay", target_merged.c_str(), "overlay", 0, options.c_str()) != 0) {
            throw std::runtime_error("Системна помилка mount OverlayFS: " + 
                                     std::string(std::strerror(errno)));
        }

        std::cout << "[OK] OverlayFS rootfs змонтовано у " << target_merged << "\n";
    }
};
