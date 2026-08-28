#include <format>
#include <string_view>

enum class UserRole { Admin, Moderator, User, Guest };

// Перетворення enum у string_view
constexpr std::string_view to_string(UserRole role) noexcept {
    switch (role) {
        case UserRole::Admin:     return "Admin";
        case UserRole::Moderator: return "Moderator";
        case UserRole::User:      return "User";
        case UserRole::Guest:     return "Guest";
    }
    return "Unknown";
}

// Успадкування форматування від std::formatter<std::string_view>
template <>
struct std::formatter<UserRole> : std::formatter<std::string_view> {
    template <typename FormatContext>
    auto format(UserRole role, FormatContext& ctx) const {
        // Передаємо заформатований string_view у базовий клас
        return std::formatter<std::string_view>::format(to_string(role), ctx);
    }
};
