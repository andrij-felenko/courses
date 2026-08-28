// Версія v1.0.0: auth_session.hpp
#include <cstdint>
#include <string_view>
#include <array>

struct UserSession {
    uint32_t user_id;
    std::array<char, 32> token;
};

void init_session(UserSession* s);
[[nodiscard]] bool validate_session(const UserSession* s);
