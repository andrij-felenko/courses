#include <span>
#include <string_view>
#include <optional>

namespace ribbon {

class Filter;

class StringFilterBuilder {
public:
    static std::optional<Filter> Build(std::span<const std::string_view> keys,
                                       const Options& options = {});
};

} // namespace ribbon
