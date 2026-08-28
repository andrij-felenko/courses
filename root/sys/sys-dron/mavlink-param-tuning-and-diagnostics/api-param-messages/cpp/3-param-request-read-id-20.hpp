#include <cstdint>
#include <string_view>
#include <array>
#include <algorithm>

struct ParamRequestRead {
    int16_t index{-1};
    uint8_t target_system{1};
    uint8_t target_component{1};
    std::array<char, 16> id{};

    static ParamRequestRead by_index(uint8_t sys, uint8_t comp, int16_t idx) noexcept {
        ParamRequestRead req;
        req.target_system = sys;
        req.target_component = comp;
        req.index = idx;
        req.id.fill('\0');
        return req;
    }

    static ParamRequestRead by_name(uint8_t sys, uint8_t comp, std::string_view name) noexcept {
        ParamRequestRead req;
        req.target_system = sys;
        req.target_component = comp;
        req.index = -1;
        req.id.fill('\0');
        size_t to_copy = std::min(name.size(), req.id.size());
        std::copy_n(name.data(), to_copy, req.id.data());
        return req;
    }
};
