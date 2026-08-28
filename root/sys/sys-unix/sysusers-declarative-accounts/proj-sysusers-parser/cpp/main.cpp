#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <optional>
#include <memory>
#include <stdexcept>
#include <system_error>
#include <cerrno>
#include <cstring>
#include <unistd.h>
#include <shadow.h>
#include <pwd.h>
#include <fcntl.h>
#include <sys/stat.h>

constexpr uid_t SYS_UID_MIN = 100;
constexpr uid_t SYS_UID_MAX = 999;

// RAII обгортка для глобального блокування lckpwdf
class PasswdLock {
public:
    PasswdLock() {
        if (lckpwdf() != 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося отримати блокування lckpwdf");
        }
    }
    ~PasswdLock() {
        ulckpwdf();
    }
    PasswdLock(const PasswdLock&) = delete;
    PasswdLock& operator=(const PasswdLock&) = delete;
};

// RAII обгортка для контролю файлових дескрипторів та видалення тимчасового файлу при помилках
class ScopeFileCleanup {
    std::string filepath_;
    bool success_{false};
public:
    explicit ScopeFileCleanup(std::string path) : filepath_(std::move(path)) {}
    ~ScopeFileCleanup() {
        if (!success_) {
            ::unlink(filepath_.c_str());
        }
    }
    void mark_success() { success_ = true; }
};

struct SysUserRule {
    char type{'u'};
    std::string name;
    uid_t requested_uid{0};
    std::string comment;
    std::string home{"/"};
    std::string shell{"/usr/sbin/nologin"};
};

class SysUsersEngine {
public:
    static bool user_exists(const std::string& name, uid_t uid) {
        ::setpwent();
        struct passwd* pw = nullptr;
        while ((pw = ::getpwent()) != nullptr) {
            if ((!name.empty() && name == pw->pw_name) || (uid != 0 && pw->pw_uid == uid)) {
                ::endpwent();
                return true;
            }
        }
        ::endpwent();
        return false;
    }

    static std::optional<uid_t> find_free_uid() {
        for (uid_t candidate = SYS_UID_MIN; candidate <= SYS_UID_MAX; ++candidate) {
            if (!user_exists("", candidate)) {
                return candidate;
            }
        }
        return std::nullopt;
    }

    static void apply_rule(const SysUserRule& rule) {
        PasswdLock lock; // Блокування знімається автоматично при виході з області видимості

        if (user_exists(rule.name, rule.requested_uid)) {
            std::cout << "Користувач " << rule.name << " вже існує у системі. Пропускаємо.\n";
            return;
        }

        uid_t final_uid = rule.requested_uid;
        if (final_uid == 0) {
            auto free_uid = find_free_uid();
            if (!free_uid) {
                throw std::runtime_error("Вичерпано вільні UID у системному діапазоні");
            }
            final_uid = *free_uid;
        }

        const std::string target_path = "/etc/passwd";
        const std::string tmp_path = "/etc/passwd.tmp";

        ScopeFileCleanup cleanup(tmp_path);

        std::ifstream input(target_path);
        if (!input.is_open()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити " + target_path);
        }

        int tmp_fd = ::open(tmp_path.c_str(), O_WRONLY | O_CREAT | O_EXCL, 0644);
        if (tmp_fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося створити " + tmp_path);
        }

        // Записуємо через файловий потік
        {
            std::ofstream output("/proc/self/fd/" + std::to_string(tmp_fd));
            std::string line;
            while (std::getline(input, line)) {
                output << line << "\n";
            }

            output << rule.name << ":x:" << final_uid << ":" << final_uid << ":"
                   << (rule.comment.empty() ? rule.name : rule.comment) << ":"
                   << rule.home << ":" << rule.shell << "\n";
            
            output.flush();
        }

        if (::fsync(tmp_fd) != 0) {
            ::close(tmp_fd);
            throw std::system_error(errno, std::generic_category(), "Помилка скидання даних на диск fsync()");
        }
        ::close(tmp_fd);

        if (::rename(tmp_path.c_str(), target_path.c_str()) != 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка атомарної заміни rename()");
        }

        cleanup.mark_success();
        std::cout << "Успішно створено системного користувача: " << rule.name << " (UID: " << final_uid << ")\n";
    }
};
