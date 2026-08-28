#include <iostream>
#include <string>
#include <optional>
#include <system_error>
#include <cerrno>
#include <pwd.h>

// Ідіоматична C++ обгортка над системним викликом POSIX getpwnam
class UserDatabaseReader {
public:
    struct UserInfo {
        std::string name;
        uid_t uid;
        gid_t gid;
        std::string home;
        std::string shell;
    };

    static std::optional<UserInfo> find_user(const std::string& username) {
        errno = 0;
        struct passwd* pw = ::getpwnam(username.c_str());
        if (pw == nullptr) {
            if (errno != 0) {
                throw std::system_error(errno, std::generic_category(), "Помилка getpwnam для " + username);
            }
            return std::nullopt;
        }

        return UserInfo{
            .name = pw->pw_name,
            .uid = pw->pw_uid,
            .gid = pw->pw_gid,
            .home = pw->pw_dir,
            .shell = pw->pw_shell
        };
    }
};
