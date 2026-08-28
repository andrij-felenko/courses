#include <iostream>
#include <string>
#include <string_view>
#include <filesystem>
#include <fstream>
#include <system_error>
#include <expected>
#include <cstdlib>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <pwd.h>

namespace fs = std::filesystem;

class AppConfigManager {
public:
    static std::expected<fs::path, std::error_code> getConfigDir(std::string_view appName) {
        if (appName.empty()) {
            return std::unexpected(std::make_error_code(std::errc::invalid_argument));
        }

        const char *xdgConfig = std::getenv("XDG_CONFIG_HOME");
        if (xdgConfig && xdgConfig[0] == '/') {
            return fs::path(xdgConfig) / appName;
        }

        const char *home = std::getenv("HOME");
        if (!home || home[0] == '\0') {
            struct passwd *pw = getpwuid(getuid());
            if (!pw || !pw->pw_dir) {
                return std::unexpected(std::make_error_code(std::errc::no_such_file_or_directory));
            }
            home = pw->pw_dir;
        }

        return fs::path(home) / ".config" / appName;
    }

    static std::expected<void, std::error_code> saveAtomic(const fs::path &filePath, std::string_view content) {
        fs::path parentDir = filePath.parent_path();
        if (parentDir.empty()) parentDir = ".";

        std::error_code ec;
        fs::create_directories(parentDir, ec);
        if (ec) return std::unexpected(ec);

        std::string tempPattern = (parentDir / "cfg.XXXXXX").string();
        int fd = mkstemp(tempPattern.data());
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        fs::path tempPath(tempPattern);
        fchmod(fd, 0600);

        const char *ptr = content.data();
        size_t left = content.size();
        while (left > 0) {
            ssize_t res = ::write(fd, ptr, left);
            if (res < 0) {
                if (errno == EINTR) continue;
                close(fd);
                unlink(tempPath.c_str());
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }
            ptr += res;
            left -= (size_t)res;
        }

        if (fsync(fd) != 0) {
            close(fd);
            unlink(tempPath.c_str());
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        close(fd);

        if (rename(tempPath.c_str(), filePath.c_str()) != 0) {
            unlink(tempPath.c_str());
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        int dirFd = open(parentDir.c_str(), O_RDONLY | O_DIRECTORY);
        if (dirFd >= 0) {
            fsync(dirFd);
            close(dirFd);
        }

        return {};
    }
};
