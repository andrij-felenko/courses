#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <functional>
#include <span>
#include <string_view>

namespace embedded::mqtt {

struct TopicToken {
    std::string_view value;
};

struct Message {
    std::string_view            topic;
    std::span<const uint8_t>    payload;
    std::span<const TopicToken> tokens;
};

using Handler = void (*)(const Message& msg, void* user_ctx);

struct Route {
    std::string_view pattern;
    Handler          handler{nullptr};
    void*            user_ctx{nullptr};
};

template <size_t MaxRoutes = 16, size_t MaxTokens = 8>
class TopicRouter {
public:
    constexpr TopicRouter() = default;

    bool add_route(std::string_view pattern, Handler handler, void* user_ctx = nullptr) noexcept {
        if (route_count_ >= MaxRoutes || handler == nullptr) {
            return false;
        }
        routes_[route_count_++] = Route{pattern, handler, user_ctx};
        return true;
    }

    bool dispatch(std::string_view topic, std::span<const uint8_t> payload) const noexcept {
        std::array<TopicToken, MaxTokens> tokens{};
        size_t token_count = 0;

        for (size_t i = 0; i < route_count_; ++i) {
            if (matches(routes_[i].pattern, topic, tokens, token_count)) {
                const Message msg{
                    .topic = topic,
                    .payload = payload,
                    .tokens = std::span<const TopicToken>(tokens.data(), token_count)
                };
                routes_[i].handler(msg, routes_[i].user_ctx);
                return true;
            }
        }
        return false;
    }

    static bool matches(std::string_view pattern, std::string_view topic,
                        std::span<TopicToken> tokens, size_t& token_count) noexcept {
        token_count = 0;
        size_t p_pos = 0;
        size_t t_pos = 0;

        while (p_pos < pattern.size() && t_pos < topic.size()) {
            if (pattern[p_pos] == '#') {
                if (p_pos + 1 != pattern.size()) {
                    return false; // '#' мусить стояти останнім символом
                }
                if (token_count < tokens.size()) {
                    tokens[token_count++] = TopicToken{topic.substr(t_pos)};
                }
                return true;
            }

            const auto p_next = pattern.find('/', p_pos);
            const auto t_next = topic.find('/', t_pos);

            const auto p_seg = pattern.substr(p_pos, p_next == std::string_view::npos ? std::string_view::npos : p_next - p_pos);
            const auto t_seg = topic.substr(t_pos, t_next == std::string_view::npos ? std::string_view::npos : t_next - t_pos);

            if (p_seg == "+") {
                if (token_count < tokens.size()) {
                    tokens[token_count++] = TopicToken{t_seg};
                }
            } else if (p_seg != t_seg) {
                return false;
            }

            p_pos = (p_next == std::string_view::npos) ? pattern.size() : p_next + 1;
            t_pos = (t_next == std::string_view::npos) ? topic.size() : t_next + 1;
        }

        if (p_pos < pattern.size() && pattern.substr(p_pos) == "#") {
            return true;
        }

        return p_pos == pattern.size() && t_pos == topic.size();
    }

private:
    std::array<Route, MaxRoutes> routes_{};
    size_t                       route_count_{0};
};

} // namespace embedded::mqtt
