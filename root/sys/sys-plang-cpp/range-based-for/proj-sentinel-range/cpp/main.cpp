#include <cstddef>
#include <string_view>

class split_by {
public:
    constexpr split_by(std::string_view text, char sep) noexcept
        : text_(text), sep_(sep) {}

    struct end_marker {};                      // вартовий: жодного поля

    class cursor {
    public:
        constexpr cursor(std::string_view text, char sep) noexcept
            : rest_(text), sep_(sep) { step(); }

        constexpr std::string_view operator*() const noexcept { return piece_; }

        constexpr cursor& operator++() noexcept { step(); return *this; }

        constexpr bool operator==(end_marker) const noexcept { return finished_; }

    private:
        constexpr void step() noexcept {
            if (!more_) { finished_ = true; return; }
            const std::size_t at = rest_.find(sep_);
            if (at == std::string_view::npos) {
                piece_ = rest_;
                more_  = false;                // цей шматок останній
            } else {
                piece_ = rest_.substr(0, at);
                rest_.remove_prefix(at + 1);
            }
        }

        std::string_view rest_;
        std::string_view piece_;
        char sep_;
        bool more_     = true;
        bool finished_ = false;
    };

    constexpr cursor     begin() const noexcept { return cursor{text_, sep_}; }
    constexpr end_marker end()   const noexcept { return {}; }

private:
    std::string_view text_;
    char sep_;
};
