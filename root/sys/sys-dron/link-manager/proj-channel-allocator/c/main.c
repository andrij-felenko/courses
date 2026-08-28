typedef struct __mavlink_status {
    uint8_t msg_received;
    uint8_t buffer_overrun;
    uint8_t parse_error;
    mavlink_parse_state_t parse_state;
    uint8_t packet_idx;
    uint8_t current_rx_seq;
    uint8_t current_tx_seq;
    uint16_t packet_rx_success_count;
    uint16_t packet_rx_drop_count;
    uint8_t flags;
    uint8_t signature_wait;
    struct __mavlink_signing *signing;
    struct __mavlink_signing_streams *signing_streams;
} mavlink_status_t;
