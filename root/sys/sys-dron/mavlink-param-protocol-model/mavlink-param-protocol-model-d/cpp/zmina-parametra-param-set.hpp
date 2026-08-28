#include <cstdint>
#include <cstring>
#include <string_view>
#include <array>
#include <bit>

struct ParamSetMessage {
    float    param_value{0.0f};
    uint8_t  target_system{1};
    uint8_t  target_component{1};
    std::array<char, 16> param_id{};
    uint8_t  param_type{9}; // MAV_PARAM_TYPE_REAL32
};

// Складання типізованого повідомлення PARAM_SET
ParamSetMessage create_param_set_float(uint8_t sys_id,
                                       uint8_t comp_id,
                                       std::string_view name,
                                       float val) noexcept {
    ParamSetMessage msg{};
    msg.target_system = sys_id;
    msg.target_component = comp_id;
    msg.param_type = 9;
    msg.param_value = val;

    const size_t copy_len = std::min(name.size(), msg.param_id.size());
    std::memcpy(msg.param_id.data(), name.data(), copy_len);

    return msg;
}
