#include <cstdint>
#include <span>
#include <array>

/* C++ обгортка над повідомленням PARAM_REQUEST_LIST з ідіоматичним інтерфейсом */
struct ParamRequestList {
    uint8_t target_system{1};
    uint8_t target_component{1};

    [[nodiscard]] size_t encode(uint8_t sys_id, uint8_t comp_id,
                                std::span<uint8_t> output_buffer) const {
        mavlink_message_t msg;
        mavlink_param_request_list_t payload{
            .target_system = target_system,
            .target_component = target_component
        };
        mavlink_msg_param_request_list_encode(sys_id, comp_id, &msg, &payload);
        uint16_t len = mavlink_msg_to_send_buffer(output_buffer.data(), &msg);
        return static_cast<size_t>(len);
    }
};
