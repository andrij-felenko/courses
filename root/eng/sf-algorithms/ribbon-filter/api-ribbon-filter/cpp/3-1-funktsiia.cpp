#include <span>
#include <cstdint>
#include <optional>
#include <memory>

namespace ribbon {

class Filter;

class Builder {
public:
    static std::optional<Filter> Build(std::span<const std::uint64_t> keys,
                                       const Options& options = {});
};

} // namespace ribbon
