#include <string_view>
#include <optional>

class ReentrantLogTokenizer {
public:
    explicit ReentrantLogTokenizer(std::string_view line) noexcept 
        : remaining_(line) {}

    std::optional<std::string_view> next_token(char delimiter) noexcept {
        if (remaining_.empty()) {
            return std::nullopt;
        }

        auto pos = remaining_.find(delimiter);
        if (pos != std::string_view::npos) {
            auto token = remaining_.substr(0, pos);
            remaining_.remove_prefix(pos + 1);
            return token;
        }

        auto token = remaining_;
        remaining_ = {};
        return token;
    }

    [[nodiscard]] bool has_more() const noexcept {
        return !remaining_.empty();
    }

private:
    std::string_view remaining_{};
};
