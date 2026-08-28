#define MAVLINK_MAX_SIGNING_STREAMS 16

typedef struct __mavlink_signing_stream {
    uint8_t  link_id;       // Ідентифікатор лінку відправника (0..255)
    uint8_t  sysid;         // Системний ID апарата відправника (1..255)
    uint8_t  compid;        // ID компонента відправника (1..255)
    uint64_t timestamp;     // Останній прийнятий валідний таймстемп (48 біт)
} mavlink_signing_stream_t;

typedef struct __mavlink_signing_streams {
    uint16_t num_signing_streams; // Поточна кількість зайнятих слотів
    mavlink_signing_stream_t stream[MAVLINK_MAX_SIGNING_STREAMS]; // Масив активних слотів
} mavlink_signing_streams_t;
