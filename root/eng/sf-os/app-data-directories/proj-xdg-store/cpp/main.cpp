#include <iostream>
#include <string>
#include <string_view>
#include <filesystem>
#include <fstream>
#include <system_error>
#include <expected>
#include <cstdlib>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <pwd.h>

namespace fs = std::filesystem;

enum class XdgCategory {
    Config,
    Data,
    State,
    Cache,
    Runtime
};

class XdgDirectoryResolver {
public:
    static std::expected<fs::path, std::error_code> get_user_home() {
        const char *home_env = std::getenv("HOME");
        if (home_env && home_env[0] != '\0') {
            return fs::path(home_env);
        }
        struct passwd *pw = getpwuid(getuid());
        if (pw && pw->pw_dir && pw->pw_dir[0] != '\0') {
            return fs::path(pw->pw_dir);
        }
        return std::unexpected(std::make_error_code(std::errc::no_such_file_or_directory));
    }

    static std::expected<fs::path, std::error_code> resolve(XdgCategory cat, std::string_view app_name) {
        if (app_name.empty()) {
            return std::unexpected(std::make_error_code(std::errc::invalid_argument));
        }

        const char *env_var = nullptr;
        std::string_view default_rel;

        switch (cat) {
            case XdgCategory::Config:
                env_var = std::getenv("XDG_CONFIG_HOME");
                default_rel = ".config";
                break;
            case XdgCategory::Data:
                env_var = std::getenv("XDG_DATA_HOME");
                default_rel = ".local/share";
                break;
            case XdgCategory::State:
                env_var = std::getenv("XDG_STATE_HOME");
                default_rel = ".local/state";
                break;
            case XdgCategory::Cache:
                env_var = std::getenv("XDG_CACHE_HOME");
                default_rel = ".cache";
                break;
            case XdgCategory::Runtime:
                env_var = std::getenv("XDG_RUNTIME_DIR");
                break;
        }

        /* Якщо змінна оточення задана і містить абсолютний шлях */
        if (env_var && env_var[0] == '/') {
            return fs::path(env_var) / app_name;
        }

        if (cat == XdgCategory::Runtime) {
            return std::unexpected(std::make_error_code(std::errc::no_such_file_or_directory));
        }

        auto home_res = get_user_home();
        if (!home_res) {
            return std::unexpected(home_res.error());
        }

        return *home_res / default_rel / app_name;
    }
};

class AtomicFileWriter {
public:
    static std::expected<void, std::error_code> write(const fs::path &dest_path, 
                                                     std::string_view payload, 
                                                     mode_t mode = 0600) {
        fs::path parent_dir = dest_path.parent_path();
        if (parent_dir.empty()) {
            parent_dir = ".";
        }

        std::error_code ec;
        fs::create_directories(parent_dir, ec);
        if (ec) {
            return std::unexpected(ec);
        }

        /* Надійні права доступу на каталог */
        fs::permissions(parent_dir, fs::perms::owner_all, fs::perm_options::replace, ec);

        fs::path temp_template = parent_dir / "tmp.XXXXXX";
        std::string temp_str = temp_template.string();

        int fd = mkstemp(temp_str.data());
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        fs::path temp_path(temp_str);

        if (fchmod(fd, mode) != 0) {
            close(fd);
            unlink(temp_path.c_str());
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        const char *data_ptr = payload.data();
        size_t bytes_left = payload.size();

        while (bytes_left > 0) {
            ssize_t written = ::write(fd, data_ptr, bytes_left);
            if (written < 0) {
                if (errno == EINTR) continue;
                close(fd);
                unlink(temp_path.c_str());
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }
            data_ptr += written;
            bytes_left -= (size_t)written;
        }

        /* 1. Синхронізація файлу на фізичний накопичувач */
        if (fsync(fd) != 0) {
            close(fd);
            unlink(temp_path.c_str());
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (close(fd) != 0) {
            unlink(temp_path.c_str());
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        /* 2. Атомарна заміна файлу в каталозі */
        if (rename(temp_path.c_str(), dest_path.c_str()) != 0) {
            unlink(temp_path.c_str());
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        /* 3. Синхронізація запису батьківського каталогу */
        int dir_fd = open(parent_dir.c_str(), O_RDONLY | O_DIRECTORY);
        if (dir_fd >= 0) {
            fsync(dir_fd);
            close(dir_fd);
        }

        return {};
    }
};

int main() {
    constexpr std::string_view app = "demo_service";

    auto conf_path = XdgDirectoryResolver::resolve(XdgCategory::Config, app);
    auto cache_path = XdgDirectoryResolver::resolve(XdgCategory::Cache, app);

    if (conf_path) {
        std::cout << "Конфігураційний каталог: " << *conf_path << '\n';
    }
    if (cache_path) {
        std::cout << "Каталог кешу:             " << *cache_path << '\n';
    }

    if (conf_path) {
        fs::path settings_file = *conf_path / "settings.json";
        std::string payload = "{\n  \"version\": 1,\n  \"theme\": \"dark\"\n}\n";

        auto write_res = AtomicFileWriter::write(settings_file, payload, 0600);
        if (write_res) {
            std::cout << "Успішно збережено конфігурацію в " << settings_file << '\n';
        } else {
            std::cerr << "Помилка збереження: " << write_res.error().message() << '\n';
            return 1;
        }
    }

    return 0;
}
