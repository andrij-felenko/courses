#include <cstdint>
#include <string_view>
#include <array>
#include <algorithm>
#include <bit>

struct ParamSetMsg {
    float raw_value{0.0f};
    uint8_t target_system{1};
    uint8_t target_component{1};
    std::array<char, 16> id{};
    uint8_t type{0};

    static ParamSetMsg make_float(uint8_t sys, uint8_t comp,
                                  std::string_view name, float val) noexcept {
        ParamSetMsg msg;
        msg.target_system = sys;
        msg.target_component = comp;
        msg.type = 9; /* MAV_PARAM_TYPE_REAL32 */
        msg.raw_value = val;
        msg.id.fill('\0');
        std::copy_n(name.data(), std::min(name.size(), msg.id.size()), msg.id.data());
        return msg;
    }

    static ParamSetMsg make_uint32(uint8_t sys, uint8_t comp,
                                   std::string_view name, uint32_t val) noexcept {
        ParamSetMsg msg;
        msg.target_system = sys;
        msg.target_component = comp;
        msg.type = 5; /* MAV_PARAM_TYPE_UINT32 */
        msg.raw_value = std::bit_cast<float>(val);
        msg.id.fill('\0');
        std::copy_n(name.data(), std::min(name.size(), msg.id.size()), msg.id.data());
        return msg;
    }
};
