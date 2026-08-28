#pragma once

#include <string>
#include <string_view>
#include <cstdint>
#include "hyperion/export.hpp"

namespace hyperion {

class HYPERION_API Engine {
public:
    explicit Engine(std::string name);
    
    [[nodiscard]] std::string_view name() const noexcept;
    [[nodiscard]] uint32_t compute_hash(std::string_view payload) const noexcept;

private:
    std::string name_;
};

} // namespace hyperion
