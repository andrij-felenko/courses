#include <dronecan_msgs.h>   // згенеровані з DSDL структури

void publish_node_status(uint32_t uptime_s, uint8_t healthy) {
    struct uavcan_protocol_NodeStatus st = {0};
    st.uptime_sec = uptime_s;
    st.health = healthy ? UAVCAN_PROTOCOL_NODESTATUS_HEALTH_OK
                        : UAVCAN_PROTOCOL_NODESTATUS_HEALTH_ERROR;
    st.mode   = UAVCAN_PROTOCOL_NODESTATUS_MODE_OPERATIONAL;

    uint8_t buf[UAVCAN_PROTOCOL_NODESTATUS_MAX_SIZE];
    uint32_t len = uavcan_protocol_NodeStatus_encode(&st, buf);  // 7 байт
    canard_broadcast(UAVCAN_PROTOCOL_NODESTATUS_SIGNATURE,       // підпис типу
                     UAVCAN_PROTOCOL_NODESTATUS_ID,              // тип 341
                     &transfer_id, priority, buf, len);          // transfer_id росте сам
}
