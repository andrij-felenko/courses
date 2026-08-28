// bsp_interface.hpp — Апаратний контракт плати (C++)
#pragma once
#include <cstdint>

namespace bsp {

struct IBoardSupport {
    virtual void init() noexcept = 0;
    virtual void toggle_heartbeat() noexcept = 0;
    virtual void log_char(char ch) noexcept = 0;
    [[nodiscard]] virtual bool is_power_good() noexcept = 0;
    virtual ~IBoardSupport() = default;
};

} // namespace bsp
