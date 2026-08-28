#include <optional>

template <typename T>
class CheckedField {
public:
    CheckedField(bool valid, T value) : valid_(valid), value_(value) {}

    [[nodiscard]] bool is_valid() const noexcept { return valid_; }
    [[nodiscard]] T value_or(T fallback) const noexcept {
        return valid_ ? value_ : fallback;
    }
    [[nodiscard]] std::optional<T> to_optional() const noexcept {
        if (valid_) return value_;
        return std::nullopt;
    }

private:
    bool valid_;
    T value_;
};
