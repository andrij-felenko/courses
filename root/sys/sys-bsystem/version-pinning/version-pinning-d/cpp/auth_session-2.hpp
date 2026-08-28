// Версія v1.0.1 (PATCH!): auth_session.hpp
#include <cstdint>
#include <array>

struct UserSession {
    uint32_t user_id;
    std::array<char, 32> token;
    bool is_admin; /* Додано нове поле для багфіксу */
};

void init_session(UserSession* s);
[[nodiscard]] bool validate_session(const UserSession* s);
