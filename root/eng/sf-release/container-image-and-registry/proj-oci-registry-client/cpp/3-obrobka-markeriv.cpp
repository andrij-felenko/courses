#include <iostream>
#include <string_view>
#include <filesystem>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <sys/xattr.h>
#include <cerrno>
#include <cstring>

namespace fs = std::filesystem;

class OciWhiteoutProcessor {
public:
    static bool process_tar_entry(const fs::path& parent_dir, std::string_view entry_name) {
        if (entry_name == ".wh..wh..opq") {
            // Маркер повної непрозорості каталогу
            int ret = ::setxattr(parent_dir.c_str(), "trusted.overlay.opaque", "y", 1, 0);
            if (ret != 0) {
                ::setxattr(parent_dir.c_str(), "user.overlay.opaque", "y", 1, 0);
            }
            return true;
        }

        if (entry_name.starts_with(".wh.")) {
            // Маркер видалення окремого файлу з нижчого шару
            std::string_view target_name = entry_name.substr(4);
            fs::path target_path = parent_dir / target_name;

            dev_t dev = makedev(0, 0);
            if (::mknod(target_path.c_str(), S_IFCHR | 0600, dev) != 0) {
                std::cerr << "[WARN] Помилка створення whiteout вузла mknod: " 
                          << target_path << " (" << std::strerror(errno) << ")\n";
                return false;
            }
            return true;
        }

        return false; // Звичайний файл
    }
};
