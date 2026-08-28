#include <iostream>
#include <string>
#include <string_view>
#include <format>
#include <cstdint>

namespace mixed_fleet::cache {

class VersionedCacheKeyBuilder {
public:
    explicit VersionedCacheKeyBuilder(uint32_t schema_major) noexcept
        : schema_major_(schema_major) {}

    [[nodiscard]] std::string makeKey(std::string_view entity_type, uint64_t entity_id) const {
        return std::format("cache:v{}:{}:{}", schema_major_, entity_type, entity_id);
    }

    [[nodiscard]] uint32_t getSchemaMajor() const noexcept {
        return schema_major_;
    }

private:
    uint32_t schema_major_{1};
};

} // namespace mixed_fleet::cache
