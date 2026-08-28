#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define FTS_MAGIC               0x5AA5F751U
#define FTS_ARM_TIMEOUT_MS      2500U
#define FTS_MIN_ARM_TIME_MS     80U
#define FTS_SQUIB_PULSE_MS      60U
#define FTS_MOTOR_SPINDOWN_MS   70U

/* Пороги автономного детектора штопору */
#define FTS_SPIN_RATE_THRESH    7.85f   /* 450 град/с в рад/с */
#define FTS_FREEFALL_G_THRESH   0.25f   /* 0.25 g */
#define FTS_DWELL_TIME_MS       350U    /* Час утримання аномалії */

typedef enum {
    FTS_STATE_SAFE = 0,
    FTS_STATE_ARMED,
    FTS_STATE_TRIGGERED,
    FTS_STATE_LATCHED_KILL
} fts_fsm_state_t;

typedef enum {
    CMD_NONE      = 0x00,
    CMD_ARM       = 0xA5,
    CMD_TERMINATE = 0x5A,
    CMD_HEARTBEAT = 0x55,
    CMD_DISARM    = 0x33
} fts_cmd_t;

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint32_t seq_num;
    uint32_t timestamp_ms;
    uint8_t  command;
    uint8_t  reserved[3];
    uint64_t auth_token;
    uint32_t crc32;
} fts_packet_raw_t;

typedef struct {
    float gx, gy, gz;  /* Рад/с */
    float ax, ay, az;  /* В одиницях g (1g = 9.81 м/с²) */
} fts_imu_sample_t;

typedef struct {
    fts_fsm_state_t state;
    uint32_t        last_valid_seq;
    uint32_t        arm_start_timestamp_ms;
    uint32_t        trigger_timestamp_ms;
    uint32_t        spin_start_timestamp_ms;
    bool            in_spin_anomaly;
    uint64_t        secret_key_low;
    uint64_t        secret_key_high;
    
    /* Стан виходів */
    bool            motor_kill_active;
    bool            squib_gate_arm_active;
    bool            squib_gate_fire_active;
} fts_watchdog_core_t;

/* Обчислення контрольної суми CRC32 IEEE 802.3 */
static uint32_t fts_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; ++bit) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(int32_t)(crc & 1U)));
        }
    }
    return ~crc;
}

/* Спрощений криптографічний хеш-імітовставка (HMAC) */
static uint64_t fts_compute_hmac(const fts_packet_raw_t *pkt, uint64_t k1, uint64_t k2) {
    uint64_t h = k1 ^ ((uint64_t)pkt->magic << 32) ^ pkt->seq_num;
    h = (h ^ ((uint64_t)pkt->timestamp_ms << 16) ^ pkt->command) * 0x517CC1B727220A95ULL;
    h ^= k2;
    h = (h ^ (h >> 32)) * 0x9E3779B97F4A7C15ULL;
    return h ^ (h >> 28);
}

/* Ініціалізація ядра */
void fts_core_init(fts_watchdog_core_t *core, uint64_t k1, uint64_t k2) {
    memset(core, 0, sizeof(fts_watchdog_core_t));
    core->state = FTS_STATE_SAFE;
    core->secret_key_low = k1;
    core->secret_key_high = k2;
}

/* Апаратні функції керування ключами */
static void hw_set_motor_kill(bool active) {
    /* Активує реле знеструмлення ESC та відкриває транзистори заземлення DShot */
}

static void hw_set_squib_arm_gate(bool active) {
    /* Верхнє плече живлення піропатрона */
}

static void hw_set_squib_fire_gate(bool active) {
    /* Нижнє плече (імпульсний ключ підриву) */
}

/* Обробка вхідного радіопакета */
bool fts_core_process_packet(fts_watchdog_core_t *core, const uint8_t *raw_buf, size_t len, uint32_t now_ms) {
    if (len < sizeof(fts_packet_raw_t)) {
        return false;
    }

    const fts_packet_raw_t *pkt = (const fts_packet_raw_t *)raw_buf;

    if (pkt->magic != FTS_MAGIC) {
        return false;
    }

    uint32_t computed_crc = fts_crc32(raw_buf, sizeof(fts_packet_raw_t) - sizeof(uint32_t));
    if (computed_crc != pkt->crc32) {
        return false;
    }

    if (pkt->seq_num <= core->last_valid_seq) {
        return false;
    }

    uint64_t expected_token = fts_compute_hmac(pkt, core->secret_key_low, core->secret_key_high);
    if (pkt->auth_token != expected_token) {
        return false;
    }

    core->last_valid_seq = pkt->seq_num;

    switch (core->state) {
        case FTS_STATE_SAFE:
            if (pkt->command == CMD_ARM) {
                core->state = FTS_STATE_ARMED;
                core->arm_start_timestamp_ms = now_ms;
            }
            break;

        case FTS_STATE_ARMED:
            if (pkt->command == CMD_TERMINATE) {
                uint32_t arm_duration = now_ms - core->arm_start_timestamp_ms;
                if (arm_duration >= FTS_MIN_ARM_TIME_MS && arm_duration <= FTS_ARM_TIMEOUT_MS) {
                    core->state = FTS_STATE_TRIGGERED;
                    core->trigger_timestamp_ms = now_ms;
                    core->motor_kill_active = true;
                    hw_set_motor_kill(true);
                } else {
                    core->state = FTS_STATE_SAFE;
                }
            } else if (pkt->command == CMD_DISARM) {
                core->state = FTS_STATE_SAFE;
            }
            break;

        case FTS_STATE_TRIGGERED:
        case FTS_STATE_LATCHED_KILL:
            /* Постійний Motor Kill */
            hw_set_motor_kill(true);
            break;
    }

    return true;
}

/* Періодичний цикл моніторингу IMU та апаратних таймерів (100–500 Гц) */
void fts_core_update(fts_watchdog_core_t *core, const fts_imu_sample_t *imu, uint32_t now_ms) {
    /* 1. Обробка таймауту режиму ARMED */
    if (core->state == FTS_STATE_ARMED) {
        if (now_ms - core->arm_start_timestamp_ms > FTS_ARM_TIMEOUT_MS) {
            core->state = FTS_STATE_SAFE;
        }
    }

    /* 2. Автономний детектор некерованого штопору */
    if (imu != NULL && (core->state == FTS_STATE_SAFE || core->state == FTS_STATE_ARMED)) {
        float spin_mag = sqrtf(imu->gx * imu->gx + imu->gy * imu->gy + imu->gz * imu->gz);
        float accel_mag = sqrtf(imu->ax * imu->ax + imu->ay * imu->ay + imu->az * imu->az);

        if (spin_mag > FTS_SPIN_RATE_THRESH && accel_mag < FTS_FREEFALL_G_THRESH) {
            if (!core->in_spin_anomaly) {
                core->in_spin_anomaly = true;
                core->spin_start_timestamp_ms = now_ms;
            } else if (now_ms - core->spin_start_timestamp_ms >= FTS_DWELL_TIME_MS) {
                /* Катастрофічний зрив: авто-термінація */
                core->state = FTS_STATE_TRIGGERED;
                core->trigger_timestamp_ms = now_ms;
                core->motor_kill_active = true;
                hw_set_motor_kill(true);
            }
        } else {
            core->in_spin_anomaly = false;
        }
    }

    /* 3. Керування послідовністю термінації (Motor Kill -> Squib Fire) */
    if (core->state == FTS_STATE_TRIGGERED) {
        uint32_t elapsed = now_ms - core->trigger_timestamp_ms;

        /* Крок 1: витримуємо зупинку гвинтів */
        if (elapsed >= FTS_MOTOR_SPINDOWN_MS && elapsed < (FTS_MOTOR_SPINDOWN_MS + FTS_SQUIB_PULSE_MS)) {
            core->squib_gate_arm_active = true;
            core->squib_gate_fire_active = true;
            hw_set_squib_arm_gate(true);
            hw_set_squib_fire_gate(true);
        } 
        /* Крок 2: завершення імпульсу підриву */
        else if (elapsed >= (FTS_MOTOR_SPINDOWN_MS + FTS_SQUIB_PULSE_MS)) {
            core->squib_gate_arm_active = false;
            core->squib_gate_fire_active = false;
            hw_set_squib_arm_gate(false);
            hw_set_squib_fire_gate(false);
            
            /* Незворотна фіксація */
            core->state = FTS_STATE_LATCHED_KILL;
        }
    }

    if (core->state == FTS_STATE_LATCHED_KILL) {
        hw_set_motor_kill(true);
    }
}
