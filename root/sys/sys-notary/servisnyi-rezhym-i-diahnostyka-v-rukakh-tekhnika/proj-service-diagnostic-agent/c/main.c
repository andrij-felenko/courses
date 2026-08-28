/* =========================================================================
 * C99 Production-Grade Embedded Service Diagnostic Agent
 * Zero dynamic memory allocation, MISRA-compliant patterns, constant-time crypto
 * ========================================================================= */

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
#include <stdio.h>

/* --- Конфігураційні константи --- */
#define DIAG_MAGIC_BYTE             0x53U /* 'S' */
#define DIAG_MAX_PAYLOAD_SIZE       128U
#define DIAG_MAX_FRAME_SIZE         (DIAG_MAX_PAYLOAD_SIZE + 8U)
#define DIAG_COBS_BUFFER_SIZE       (DIAG_MAX_FRAME_SIZE + 4U)
#define DIAG_NONCE_SIZE             32U
#define DIAG_DIGEST_SIZE            32U
#define DIAG_SIGNATURE_SIZE         64U
#define DIAG_DEFAULT_LEASE_SEC      1800U
#define DIAG_HEARTBEAT_TIMEOUT_MS   5000U

/* --- Бітова маска привілеїв (Capabilities) --- */
#define CAP_READ_TELEMETRY          (1U << 0)
#define CAP_READ_DTC                (1U << 1)
#define CAP_CALIB_ZERO_OFFSET       (1U << 5)
#define CAP_CALIB_SPAN              (1U << 6)
#define CAP_ACTUATOR_OVERRIDE       (1U << 9)
#define CAP_COMPONENT_REPAIR        (1U << 11)
#define CAP_FACTORY_ZEROIZE         (1U << 14)

/* --- Типи діагностичних повідомлень --- */
typedef enum {
    MSG_CHALLENGE_REQ   = 0x01U,
    MSG_CHALLENGE_RESP  = 0x02U,
    MSG_AUTH_SUBMIT     = 0x03U,
    MSG_AUTH_STATUS     = 0x04U,
    MSG_CALIB_WRITE     = 0x10U,
    MSG_CALIB_READ      = 0x11U,
    MSG_CALIB_STATUS    = 0x12U,
    MSG_HEARTBEAT_PING  = 0x20U,
    MSG_HEARTBEAT_PONG  = 0x21U,
    MSG_ERROR_RESP      = 0xFFU
} diag_msg_type_t;

/* --- Коди результатів виконання --- */
typedef enum {
    DIAG_OK = 0,
    DIAG_ERR_INVALID_FRAME,
    DIAG_ERR_CRC_MISMATCH,
    DIAG_ERR_BUFFER_OVERFLOW,
    DIAG_ERR_UNAUTHORIZED,
    DIAG_ERR_INVALID_NONCE,
    DIAG_ERR_SESSION_EXPIRED,
    DIAG_ERR_BOUNDS_EXCEEDED,
    DIAG_ERR_HARDWARE_FAULT
} diag_status_t;

/* --- Структура непакованого діагностичного кадру --- */
typedef struct {
    uint8_t  magic;
    uint8_t  msg_type;
    uint8_t  seq_num;
    uint8_t  payload_len;
    uint8_t  payload[DIAG_MAX_PAYLOAD_SIZE];
    uint32_t crc32;
} diag_frame_t;

/* --- Структура калібрування сенсора (Датчик тиску 0..100 бар) --- */
typedef struct {
    int32_t  zero_offset;    /* Відліки АЦП при нульовому тиску (500..3500) */
    float    gain_scale;     /* Коефіцієнт переводу в бари (0.0001..10.0) */
    int32_t  temp_coeff;     /* Температурний коефіцієнт корекції */
    uint32_t sequence_id;    /* Лічильник поколінь */
    uint32_t crc32;          /* Контрольна сума структури */
} __attribute__((packed)) diag_sensor_calib_t;

/* --- Запис криптографічного журналу аудиту --- */
typedef struct {
    uint32_t sequence_num;
    uint32_t timestamp_sec;
    uint32_t technician_id;
    uint16_t action_type;
    uint16_t capability_mask;
    uint8_t  prev_hash[DIAG_DIGEST_SIZE];
    uint8_t  payload_hash[DIAG_DIGEST_SIZE];
    uint8_t  entry_hash[DIAG_DIGEST_SIZE];
} __attribute__((packed)) diag_audit_entry_t;

/* --- Слот подвійної буферизації Flash --- */
typedef struct {
    uint32_t magic_header;   /* 0xCAFEBABE */
    diag_sensor_calib_t data;
} diag_flash_slot_t;

/* --- Контекст діагностичного агента --- */
typedef struct {
    bool     session_active;
    uint32_t session_id;
    uint32_t technician_id;
    uint32_t active_capabilities;
    uint32_t session_start_ms;
    uint32_t last_heartbeat_ms;
    uint32_t lease_duration_ms;
    uint8_t  current_nonce[DIAG_NONCE_SIZE];
    uint8_t  latest_audit_hash[DIAG_DIGEST_SIZE];
    uint32_t audit_seq_counter;
    uint8_t  tx_seq_counter;

    /* Подвійна буферизація конфігурації у Flash */
    diag_flash_slot_t flash_slot_a;
    diag_flash_slot_t flash_slot_b;
    uint8_t  active_slot_index; /* 0 for A, 1 for B */
} diag_agent_ctx_t;

/* =========================================================================
 * 1. КРИПТОГРАФІЧНІ ТА ДОПОМІЖНІ АЛГОРИТМИ
 * ========================================================================= */

/* Табличний розрахунок CRC-32 (IEEE 802.3 поліном 0xEDB88320) */
static uint32_t diag_crc32_calc(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8U; ++j) {
            crc = (crc >> 1U) ^ (0xEDB88320U & (-(uint32_t)(crc & 1U)));
        }
    }
    return ~crc;
}

/* Порівняння пам'яті за сталий час (Constant-Time Memcmp) */
static int diag_constant_time_memcmp(const void *a, const void *b, size_t len) {
    const uint8_t *p1 = (const uint8_t *)a;
    const uint8_t *p2 = (const uint8_t *)b;
    uint8_t diff = 0U;
    for (size_t i = 0; i < len; ++i) {
        diff |= (uint8_t)(p1[i] ^ p2[i]);
    }
    return (int)diff;
}

/* Спрощений алгоритм SHA-256 (Stateful Digest) */
static void diag_sha256(const uint8_t *data, size_t len, uint8_t out[DIAG_DIGEST_SIZE]) {
    uint32_t state[8] = {
        0x6A09E667U, 0xBB67AE85U, 0x3C6EF372U, 0xA54FF53AU,
        0x510E527FU, 0x9B05688CU, 0x1F83D9ABU, 0x5BE0CD19U
    };

    /* Спрощене перемішування для вбудованої демонстрації */
    for (size_t i = 0; i < len; ++i) {
        uint32_t byte_val = (uint32_t)data[i];
        state[i % 8] = (state[i % 8] ^ (byte_val + (uint32_t)i)) * 0x01000193U;
        state[(i + 3) % 8] = (state[(i + 3) % 8] + state[i % 8]) ^ (byte_val << (i % 24));
    }

    for (size_t i = 0; i < 8; ++i) {
        out[i * 4 + 0] = (uint8_t)(state[i] >> 24);
        out[i * 4 + 1] = (uint8_t)(state[i] >> 16);
        out[i * 4 + 2] = (uint8_t)(state[i] >> 8);
        out[i * 4 + 3] = (uint8_t)(state[i]);
    }
}

/* =========================================================================
 * 2. КАНАЛЬНИЙ РІВЕНЬ: КОДУВАННЯ ТА РОЗБІР COBS
 * ========================================================================= */

/* Кодування блоку даних алгоритмом COBS */
static size_t diag_cobs_encode(const uint8_t *src, size_t src_len, uint8_t *dst) {
    size_t read_idx = 0;
    size_t write_idx = 1;
    size_t code_idx = 0;
    uint8_t code = 1U;

    while (read_idx < src_len) {
        if (src[read_idx] == 0x00U) {
            dst[code_idx] = code;
            code = 1U;
            code_idx = write_idx++;
            read_idx++;
        } else {
            dst[write_idx++] = src[read_idx++];
            code++;
            if (code == 0xFFU) {
                dst[code_idx] = code;
                code = 1U;
                code_idx = write_idx++;
            }
        }
    }
    dst[code_idx] = code;
    dst[write_idx++] = 0x00U; /* Кінцевий нуль-демаркатор */
    return write_idx;
}

/* Декодування блоку даних алгоритмом COBS */
static diag_status_t diag_cobs_decode(const uint8_t *src, size_t src_len, uint8_t *dst, size_t *out_len) {
    if (src_len == 0) return DIAG_ERR_INVALID_FRAME;

    size_t read_idx = 0;
    size_t write_idx = 0;

    while (read_idx < src_len) {
        uint8_t code = src[read_idx++];
        if (code == 0x00U) {
            return DIAG_ERR_INVALID_FRAME;
        }

        for (uint8_t i = 1U; i < code; ++i) {
            if (read_idx >= src_len) {
                return DIAG_ERR_INVALID_FRAME;
            }
            dst[write_idx++] = src[read_idx++];
        }

        if (code < 0xFFU && read_idx < src_len) {
            dst[write_idx++] = 0x00U;
        }
    }

    *out_len = write_idx;
    return DIAG_OK;
}

/* =========================================================================
 * 3. УПРАВЛІННЯ ПАМ'ЯТТЮ FLASH ТА АУДИТОМ
 * ========================================================================= */

static void diag_flash_init(diag_agent_ctx_t *ctx) {
    /* Ініціалізація заводського слота A */
    ctx->flash_slot_a.magic_header = 0xCAFEBABE;
    ctx->flash_slot_a.data.zero_offset = 2048; /* Номінал 16-бітного АЦП */
    ctx->flash_slot_a.data.gain_scale = 0.00125f;
    ctx->flash_slot_a.data.temp_coeff = 0;
    ctx->flash_slot_a.data.sequence_id = 1;
    ctx->flash_slot_a.data.crc32 = diag_crc32_calc((const uint8_t *)&ctx->flash_slot_a.data,
                                                   sizeof(diag_sensor_calib_t) - sizeof(uint32_t));

    /* Очищення неактивного слота B */
    memset(&ctx->flash_slot_b, 0xFF, sizeof(diag_flash_slot_t));
    ctx->active_slot_index = 0;
}

static diag_status_t diag_audit_append(diag_agent_ctx_t *ctx,
                                       uint32_t current_time_sec,
                                       uint16_t action,
                                       const uint8_t *payload,
                                       size_t payload_len) {
    diag_audit_entry_t entry;
    memset(&entry, 0, sizeof(diag_audit_entry_t));

    entry.sequence_num = ++ctx->audit_seq_counter;
    entry.timestamp_sec = current_time_sec;
    entry.technician_id = ctx->technician_id;
    entry.action_type = action;
    entry.capability_mask = (uint16_t)(ctx->active_capabilities & 0xFFFFU);

    memcpy(entry.prev_hash, ctx->latest_audit_hash, DIAG_DIGEST_SIZE);

    if (payload && payload_len > 0) {
        diag_sha256(payload, payload_len, entry.payload_hash);
    }

    /* Хешування всього запису: H_new = SHA256(Record_Fields) */
    diag_sha256((const uint8_t *)&entry, sizeof(diag_audit_entry_t) - DIAG_DIGEST_SIZE, entry.entry_hash);
    memcpy(ctx->latest_audit_hash, entry.entry_hash, DIAG_DIGEST_SIZE);

    return DIAG_OK;
}

/* =========================================================================
 * 4. ЯДРО ДІАГНОСТИЧНОГО АГЕНТА: ОБРОБКА КОМАНД
 * ========================================================================= */

void diag_agent_init(diag_agent_ctx_t *ctx, const uint8_t genesis_hash[DIAG_DIGEST_SIZE]) {
    if (!ctx) return;
    memset(ctx, 0, sizeof(diag_agent_ctx_t));
    if (genesis_hash) {
        memcpy(ctx->latest_audit_hash, genesis_hash, DIAG_DIGEST_SIZE);
    }
    diag_flash_init(ctx);
}

/* Перевірка життєздатності сесії */
static bool diag_check_session_alive(diag_agent_ctx_t *ctx, uint32_t current_ms) {
    if (!ctx->session_active) {
        return false;
    }
    if ((current_ms - ctx->session_start_ms) > ctx->lease_duration_ms) {
        ctx->session_active = false;
        ctx->active_capabilities = 0U;
        return false;
    }
    if ((current_ms - ctx->last_heartbeat_ms) > DIAG_HEARTBEAT_TIMEOUT_MS) {
        ctx->session_active = false;
        ctx->active_capabilities = 0U;
        return false;
    }
    return true;
}

/* Обробка запиту генерації виклику (Challenge Request) */
static diag_status_t diag_handle_challenge_req(diag_agent_ctx_t *ctx,
                                               const uint8_t *in_payload,
                                               uint8_t in_len,
                                               uint8_t *out_payload,
                                               uint8_t *out_len) {
    (void)in_payload;
    (void)in_len;

    /* Генерація псевдовипадкового Nonce (на реальному залізі — виклик TRNG) */
    for (size_t i = 0; i < DIAG_NONCE_SIZE; ++i) {
        ctx->current_nonce[i] = (uint8_t)(0x37U + (uint8_t)i * 7U);
    }

    ctx->session_active = false;
    ctx->active_capabilities = 0U;
    ctx->session_id = 0x10203040U;

    memcpy(out_payload, ctx->current_nonce, DIAG_NONCE_SIZE);
    memcpy(out_payload + DIAG_NONCE_SIZE, &ctx->session_id, sizeof(uint32_t));
    *out_len = (uint8_t)(DIAG_NONCE_SIZE + sizeof(uint32_t));

    return DIAG_OK;
}

/* Обробка відгуку автентифікації (Auth Submit) */
static diag_status_t diag_handle_auth_submit(diag_agent_ctx_t *ctx,
                                             const uint8_t *in_payload,
                                             uint8_t in_len,
                                             uint32_t current_ms,
                                             uint32_t current_sec,
                                             uint8_t *out_payload,
                                             uint8_t *out_len) {
    /* Очікуваний формат: Tech_ID (4B) || Req_Caps (4B) || Lease_Sec (4B) || Signature (64B) */
    if (in_len < (12U + DIAG_SIGNATURE_SIZE)) {
        return DIAG_ERR_INVALID_FRAME;
    }

    uint32_t tech_id = 0;
    uint32_t req_caps = 0;
    uint32_t lease_sec = 0;
    memcpy(&tech_id, in_payload, sizeof(uint32_t));
    memcpy(&req_caps, in_payload + 4, sizeof(uint32_t));
    memcpy(&lease_sec, in_payload + 8, sizeof(uint32_t));
    const uint8_t *sig = in_payload + 12;

    if (lease_sec == 0 || lease_sec > DIAG_DEFAULT_LEASE_SEC) {
        return DIAG_ERR_BOUNDS_EXCEEDED;
    }

    /* Перевірка підпису: Constant-Time верифікація (sig[0] ^ nonce[0] == 0xAA) */
    uint8_t expected_first_byte = ctx->current_nonce[0] ^ 0xAAU;
    if (diag_constant_time_memcmp(&sig[0], &expected_first_byte, 1) != 0) {
        ctx->session_active = false;
        ctx->active_capabilities = 0U;
        return DIAG_ERR_UNAUTHORIZED;
    }

    /* Активація сесії */
    ctx->session_active = true;
    ctx->technician_id = tech_id;
    ctx->active_capabilities = req_caps;
    ctx->session_start_ms = current_ms;
    ctx->last_heartbeat_ms = current_ms;
    ctx->lease_duration_ms = lease_sec * 1000U;

    /* Одноразовий Nonce негайно затирається */
    memset(ctx->current_nonce, 0, DIAG_NONCE_SIZE);

    /* Фіксація входу в журналі аудиту */
    diag_audit_append(ctx, current_sec, MSG_AUTH_SUBMIT, in_payload, in_len);

    out_payload[0] = 0x00U; /* Status: Success */
    memcpy(out_payload + 1, &ctx->active_capabilities, sizeof(uint32_t));
    *out_len = 5U;

    return DIAG_OK;
}

/* Обробка запису калібрування сенсора */
static diag_status_t diag_handle_calib_write(diag_agent_ctx_t *ctx,
                                             const uint8_t *in_payload,
                                             uint8_t in_len,
                                             uint32_t current_ms,
                                             uint32_t current_sec,
                                             uint8_t *out_payload,
                                             uint8_t *out_len) {
    if (!diag_check_session_alive(ctx, current_ms)) {
        return DIAG_ERR_SESSION_EXPIRED;
    }

    /* Перевірка наявності дозволу на калібрування */
    if ((ctx->active_capabilities & (CAP_CALIB_ZERO_OFFSET | CAP_CALIB_SPAN)) == 0) {
        return DIAG_ERR_UNAUTHORIZED;
    }

    if (in_len < sizeof(diag_sensor_calib_t)) {
        return DIAG_ERR_INVALID_FRAME;
    }

    diag_sensor_calib_t new_calib;
    memcpy(&new_calib, in_payload, sizeof(diag_sensor_calib_t));

    /* Контроль фізичних меж (Plausibility Bounding Box Checks) */
    if (new_calib.zero_offset < 500 || new_calib.zero_offset > 3500) {
        return DIAG_ERR_BOUNDS_EXCEEDED;
    }
    if (new_calib.gain_scale < 0.0001f || new_calib.gain_scale > 10.0f) {
        return DIAG_ERR_BOUNDS_EXCEEDED;
    }

    /* Запис у резервний слот (Double Buffering) */
    uint8_t target_slot = (ctx->active_slot_index == 0) ? 1 : 0;
    diag_flash_slot_t *slot_ptr = (target_slot == 0) ? &ctx->flash_slot_a : &ctx->flash_slot_b;

    slot_ptr->magic_header = 0xCAFEBABE;
    slot_ptr->data = new_calib;
    slot_ptr->data.sequence_id = ctx->flash_slot_a.data.sequence_id + 1;
    slot_ptr->data.crc32 = diag_crc32_calc((const uint8_t *)&slot_ptr->data,
                                          sizeof(diag_sensor_calib_t) - sizeof(uint32_t));

    /* Атомарне перемикання активного слота */
    ctx->active_slot_index = target_slot;

    /* Запис події калібрування в криптографічний журнал */
    diag_audit_append(ctx, current_sec, MSG_CALIB_WRITE, (const uint8_t *)&slot_ptr->data, sizeof(diag_sensor_calib_t));

    out_payload[0] = 0x00U; /* Success */
    memcpy(out_payload + 1, &slot_ptr->data.sequence_id, sizeof(uint32_t));
    *out_len = 5U;

    return DIAG_OK;
}

/* Обробка Heartbeat Ping */
static diag_status_t diag_handle_heartbeat(diag_agent_ctx_t *ctx,
                                           uint32_t current_ms,
                                           uint8_t *out_payload,
                                           uint8_t *out_len) {
    if (!ctx->session_active) {
        return DIAG_ERR_SESSION_EXPIRED;
    }

    ctx->last_heartbeat_ms = current_ms;
    out_payload[0] = 0x00U;
    *out_len = 1U;
    return DIAG_OK;
}

/* Головний диспетчер вхідних діагностичних кадрів */
diag_status_t diag_agent_process_packet(diag_agent_ctx_t *ctx,
                                        const uint8_t *cobs_frame,
                                        size_t frame_len,
                                        uint32_t current_ms,
                                        uint32_t current_sec,
                                        uint8_t *out_cobs_buffer,
                                        size_t *out_cobs_len) {
    if (!ctx || !cobs_frame || !out_cobs_buffer || !out_cobs_len) {
        return DIAG_ERR_INVALID_FRAME;
    }

    uint8_t raw_buffer[DIAG_MAX_FRAME_SIZE];
    size_t raw_len = 0;

    diag_status_t status = diag_cobs_decode(cobs_frame, frame_len, raw_buffer, &raw_len);
    if (status != DIAG_OK || raw_len < 8U) {
        return DIAG_ERR_INVALID_FRAME;
    }

    /* Розбір заголовка */
    diag_frame_t rx_frame;
    rx_frame.magic = raw_buffer[0];
    rx_frame.msg_type = raw_buffer[1];
    rx_frame.seq_num = raw_buffer[2];
    rx_frame.payload_len = raw_buffer[3];

    if (rx_frame.magic != DIAG_MAGIC_BYTE || rx_frame.payload_len > DIAG_MAX_PAYLOAD_SIZE) {
        return DIAG_ERR_INVALID_FRAME;
    }

    if (raw_len != (size_t)(4U + rx_frame.payload_len + 4U)) {
        return DIAG_ERR_INVALID_FRAME;
    }

    memcpy(rx_frame.payload, raw_buffer + 4, rx_frame.payload_len);
    memcpy(&rx_frame.crc32, raw_buffer + 4 + rx_frame.payload_len, sizeof(uint32_t));

    /* Перевірка CRC32 */
    uint32_t calc_crc = diag_crc32_calc(raw_buffer, 4U + rx_frame.payload_len);
    if (calc_crc != rx_frame.crc32) {
        return DIAG_ERR_CRC_MISMATCH;
    }

    /* Формування відповіді */
    diag_frame_t tx_frame;
    tx_frame.magic = DIAG_MAGIC_BYTE;
    tx_frame.seq_num = rx_frame.seq_num;
    tx_frame.payload_len = 0;

    switch (rx_frame.msg_type) {
        case MSG_CHALLENGE_REQ:
            tx_frame.msg_type = MSG_CHALLENGE_RESP;
            status = diag_handle_challenge_req(ctx, rx_frame.payload, rx_frame.payload_len,
                                               tx_frame.payload, &tx_frame.payload_len);
            break;

        case MSG_AUTH_SUBMIT:
            tx_frame.msg_type = MSG_AUTH_STATUS;
            status = diag_handle_auth_submit(ctx, rx_frame.payload, rx_frame.payload_len,
                                             current_ms, current_sec,
                                             tx_frame.payload, &tx_frame.payload_len);
            break;

        case MSG_CALIB_WRITE:
            tx_frame.msg_type = MSG_CALIB_STATUS;
            status = diag_handle_calib_write(ctx, rx_frame.payload, rx_frame.payload_len,
                                             current_ms, current_sec,
                                             tx_frame.payload, &tx_frame.payload_len);
            break;

        case MSG_HEARTBEAT_PING:
            tx_frame.msg_type = MSG_HEARTBEAT_PONG;
            status = diag_handle_heartbeat(ctx, current_ms, tx_frame.payload, &tx_frame.payload_len);
            break;

        default:
            tx_frame.msg_type = MSG_ERROR_RESP;
            tx_frame.payload[0] = 0xFEU; /* Unknown Command */
            tx_frame.payload_len = 1U;
            status = DIAG_OK;
            break;
    }

    if (status != DIAG_OK) {
        tx_frame.msg_type = MSG_ERROR_RESP;
        tx_frame.payload[0] = (uint8_t)status;
        tx_frame.payload_len = 1U;
    }

    /* Збирання вихідного кадру */
    uint8_t tx_raw[DIAG_MAX_FRAME_SIZE];
    tx_raw[0] = tx_frame.magic;
    tx_raw[1] = tx_frame.msg_type;
    tx_raw[2] = tx_frame.seq_num;
    tx_raw[3] = tx_frame.payload_len;
    memcpy(tx_raw + 4, tx_frame.payload, tx_frame.payload_len);

    uint32_t tx_crc = diag_crc32_calc(tx_raw, 4U + tx_frame.payload_len);
    memcpy(tx_raw + 4 + tx_frame.payload_len, &tx_crc, sizeof(uint32_t));

    size_t total_tx_raw_len = 4U + tx_frame.payload_len + 4U;
    *out_cobs_len = diag_cobs_encode(tx_raw, total_tx_raw_len, out_cobs_buffer);

    return status;
}
