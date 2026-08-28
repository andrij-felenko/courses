#include <string>
#include <string_view>

class UserProfile {
    std::string nickname_;
    std::string email_;
public:
    UserProfile(std::string nick, std::string mail)
        : nickname_(std::move(nick)), email_(std::move(mail)) {}

    // Повертає посилання, що прив'язане до часу життя об'єкта UserProfile
    const std::string& get_nickname() const [[clang::lifetimebound]] {
        return nickname_;
    }

    // Повертає view, прив'язаний до часу життя *this
    std::string_view get_email_view() const [[clang::lifetimebound]] {
        return email_;
    }
};
