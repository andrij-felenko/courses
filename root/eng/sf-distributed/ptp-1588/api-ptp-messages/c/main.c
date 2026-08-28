#include <stdint.h>

#pragma pack(push, 1)

typedef struct {
    uint8_t  id[8];
} ptp_clock_identity_t;

typedef struct {
    ptp_clock_identity_t clock_id;
    uint16_t             port_number;
} ptp_port_identity_t;

typedef struct {
    uint16_t seconds_high;
    uint32_t seconds_low;
    uint32_t nanoseconds;
} ptp_timestamp_t;

typedef struct {
    uint8_t  transport_specific_and_msg_type; // [7..4] transport, [3..0] type
    uint8_t  version_ptp;                     // [3..0] version (2)
    uint16_t message_length;
    uint8_t  domain_number;
    uint8_t  minor_version_ptp;
    uint8_t  flag_field[2];
    int64_t  correction_field;                // Scaled nanoseconds (ns << 16)
    uint32_t reserved;
    ptp_port_identity_t source_port_id;
    uint16_t sequence_id;
    uint8_t  control_field;
    int8_t   log_message_interval;
} ptp_header_t;

typedef struct {
    ptp_header_t    header;
    ptp_timestamp_t precise_origin_timestamp;
} ptp_follow_up_msg_t;

typedef struct {
    ptp_header_t        header;
    ptp_timestamp_t     receive_timestamp;
    ptp_port_identity_t requesting_port_id;
} ptp_delay_resp_msg_t;

#pragma pack(pop)
