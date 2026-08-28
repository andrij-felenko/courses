#include <stdint.h>
#include <stdbool.h>

// Запис стану одного вхідного потоку сесії
typedef struct __mavlink_signing_stream_t {
    uint8_t  link_id;        // Ідентифікатор фізичного каналу зв'язку
    uint8_t  sysid;          // Системний номер відправника (System ID)
    uint8_t  compid;         // Номер компонента відправника (Component ID)
    uint8_t  flags;          // Резервні прапорці стану потоку
    uint64_t last_timestamp; // Останній успішно валідований час (в одиницях по 10 мкс)
} mavlink_signing_stream_t;

// Таблиця потоків сесій для відстеження Replay-атак
typedef struct __mavlink_signing_streams_t {
    uint16_t num_signing_streams;
    mavlink_signing_stream_t stream[MAVLINK_MAX_SIGNING_STREAMS];
} mavlink_signing_streams_t;

struct __mavlink_status;

// Загальний контекст підпису для інтерфейсу MAVLink
typedef struct __mavlink_signing_t {
    uint8_t  flags;                             // MAVLINK_SIGNING_FLAG_SIGN_OUTGOING
    uint8_t  link_id;                           // Локальний ідентифікатор каналу
    uint64_t timestamp;                         // Поточний монотонний час передавача
    uint8_t  secret_key[32];                    // 256-бітний спільний секретний ключ
    mavlink_signing_streams_t *streams;         // Вказівник на таблицю вхідних потоків
    bool (*accept_unsigned_callback)(const struct __mavlink_status *status, uint32_t msgid);
} mavlink_signing_t;
