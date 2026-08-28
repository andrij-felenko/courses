#include <utility>
#include <string>

struct UserSession {
    std::string token;

    template <typename Self>
    auto&& get_token(this Self&& self) noexcept {
        // Замість складного ланцюжка static_cast копіює const/rvalue кваліфікатори Self на поле token:
        return std::forward_like<Self>(self.token);
    }
};
