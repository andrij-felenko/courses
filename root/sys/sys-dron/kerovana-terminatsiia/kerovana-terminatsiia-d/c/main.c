#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define FTS_MAGIC_HEADER        0x5AA5F751U
#define FTS_ARM_WINDOW_MS       2500U
#define FTS_MIN_ARM_TIME_MS     100U

typedef enum {
    FTS_STATE_SAFE = 0,
    FTS_STATE_ARMED,
    FTS_STATE_TRIGGERED,
    FTS_STATE_LATCHED_KILL
} fts_state_t;

typedef enum {
    FTS_CMD_NONE = 0x00,
    FTS_CMD_ARM  = 0xA5,
    FTS_CMD_KILL = 0x5A,
    FTS_CMD_PING = 0x55
} fts_cmd_type_t;

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint32_t seq_num;
    uint32_t timestamp_ms;
    uint8_t  command;
    uint8_t  reserved[3];
    uint32_t auth_token;
    uint32_t crc32;
} fts_packet_t;

typedef struct {
    fts_state_t state;
    uint32_t    last_seq;
    uint32_t    arm_timestamp_ms;
    uint32_t    auth_secret_key;
    bool        hardware_motor_kill_active;
    bool        squib_fired;
} fts_controller_t;

/* Простий CRC32 (IEEE 802.3) */
static uint32_t calculate_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(int32_t)(crc & 1U)));
        }
    }
    return ~crc;
}

/* Обчислення автентифікаційного токена */
static uint32_t compute_auth_token(const fts_packet_t *pkt, uint32_t key) {
    uint32_t hash = key ^ pkt->magic ^ pkt->seq_num ^ pkt->timestamp_ms ^ (uint32_t)pkt->command;
    hash = ((hash << 13) | (hash >> 19)) * 0x5BD1E995U;
    return hash ^ (hash >> 15);
}

void fts_init(fts_controller_t *fts, uint32_t secret_key) {
    memset(fts, 0, sizeof(fts_controller_t));
    fts->state = FTS_STATE_SAFE;
    fts->auth_secret_key = secret_key;
    fts->hardware_motor_kill_active = false;
    fts->squib_fired = false;
}

/* Апаратні дії термінації */
static void hw_execute_motor_kill(void) {
    /* Апаратне замикання ліній DShot на GND та відсікання живлення ESC */
}

static void hw_fire_pyro_squib(void) {
    /* Двоконтурна подача струму на запалювач парашута */
}

bool fts_process_packet(fts_controller_t *fts, const uint8_t *buffer, size_t len, uint32_t current_time_ms) {
    if (len < sizeof(fts_packet_t)) {
        return false;
    }

    const fts_packet_t *pkt = (const fts_packet_t *)buffer;

    /* 1. Перевірка магічного заголовка */
    if (pkt->magic != FTS_MAGIC_HEADER) {
        return false;
    }

    /* 2. Перевірка контрольної суми CRC32 */
    uint32_t calc_crc = calculate_crc32(buffer, sizeof(fts_packet_t) - sizeof(uint32_t));
    if (calc_crc != pkt->crc32) {
        return false;
    }

    /* 3. Захист від повтору: номер пакета мусить строго зростати */
    if (pkt->seq_num <= fts->last_seq) {
        return false;
    }

    /* 4. Перевірка криптографічного токена */
    if (compute_auth_token(pkt, fts->auth_secret_key) != pkt->auth_token) {
        return false;
    }

    fts->last_seq = pkt->seq_num;

    /* 5. Автомат станів безпеки */
    switch (fts->state) {
        case FTS_STATE_SAFE:
            if (pkt->command == FTS_CMD_ARM) {
                fts->state = FTS_STATE_ARMED;
                fts->arm_timestamp_ms = current_time_ms;
            }
            break;

        case FTS_STATE_ARMED:
            if (pkt->command == FTS_CMD_KILL) {
                uint32_t delta = current_time_ms - fts->arm_timestamp_ms;
                if (delta >= FTS_MIN_ARM_TIME_MS && delta <= FTS_ARM_WINDOW_MS) {
                    fts->state = FTS_STATE_TRIGGERED;
                    hw_execute_motor_kill();
                    fts->hardware_motor_kill_active = true;
                    hw_fire_pyro_squib();
                    fts->squib_fired = true;
                    fts->state = FTS_STATE_LATCHED_KILL;
                } else {
                    /* Вихід за межі часового вікна — скидання в SAFE */
                    fts->state = FTS_STATE_SAFE;
                }
            } else if (pkt->command == FTS_CMD_ARM) {
                /* Оновлення таймера взведення */
                fts->arm_timestamp_ms = current_time_ms;
            }
            break;

        case FTS_STATE_TRIGGERED:
        case FTS_STATE_LATCHED_KILL:
            /* Після активації система заблокована до повного знеструмлення */
            hw_execute_motor_kill();
            break;
    }

    return true;
}

void fts_update_periodic(fts_controller_t *fts, uint32_t current_time_ms) {
    if (fts->state == FTS_STATE_ARMED) {
        if (current_time_ms - fts->arm_timestamp_ms > FTS_ARM_WINDOW_MS) {
            fts->state = FTS_STATE_SAFE;
        }
    }
}
