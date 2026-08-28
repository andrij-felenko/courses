/**
 * @file event_filter.hpp
 * @brief C++20 обгортка та типи для сумісності з C API
 */

#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>

extern "C" {
#include "event_filter.h"
}

namespace embedded::c_api {

// C++ обгортка над структурами C для ідіоматичного RAII використання
class FastFilterAdapter final {
public:
    explicit FastFilterAdapter(uint8_t m, uint8_t non, uint8_t noff, bool initial = false) noexcept {
        event_filter_config_t cfg{
            .m_window = m,
            .n_on = non,
            .n_off = noff,
            .max_dwell_samples = 0
        };
        event_filter_fast32_init(&filter_, &cfg, initial);
    }

    bool Update(bool raw_sample) noexcept {
        return event_filter_fast32_update(&filter_, raw_sample);
    }

    [[nodiscard]] bool GetState() const noexcept {
        return event_filter_fast32_get_state(&filter_);
    }

    [[nodiscard]] uint8_t GetCount() const noexcept {
        return event_filter_fast32_get_count(&filter_);
    }

private:
    event_filter_fast32_t filter_{};
};

} // namespace embedded::c_api
