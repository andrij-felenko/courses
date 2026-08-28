#include <string_view>

class IfRangeValidator {
public:
    [[nodiscard]] static bool isSatisfied(
        std::string_view ifRangeHeader,
        std::string_view currentStrongEtag,
        std::string_view lastModifiedDate) noexcept
    {
        if (ifRangeHeader.empty()) {
            return true; // Безумовний запит
        }

        // Жорстка заборона слабких валідаторів за стандартом RFC 9110
        if (ifRangeHeader.starts_with("W/")) {
            return false;
        }

        // Порівняння сильного ETag
        if (ifRangeHeader.starts_with('"')) {
            return ifRangeHeader == currentStrongEtag;
        }

        // Порівняння HTTP-дати модифікації
        return (!lastModifiedDate.empty() && ifRangeHeader == lastModifiedDate);
    }
};
