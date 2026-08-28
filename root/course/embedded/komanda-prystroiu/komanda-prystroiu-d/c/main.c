#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CMD_MAGIC             0x434D4431  /* ASCII "CMD1" */
#define IDEMPOTENCY_RING_SIZE 16
#define MAX_PAYLOAD_SIZE      32

/* Типи команд пристрою */
typedef enum {
    CMD_TYPE_NOOP            = 0x00,
    CMD_TYPE_SET_RELAY       = 0x01,  /* Параметр: 1 = ON, 0 = OFF */
    CMD_TYPE_MOVE_STEPPER    = 0x02,  /* Параметр: кроки (int32) */
    CMD_TYPE_CALIBRATE       = 0x03   /* Тривала операція */
} cmd_type_t;

/* Стани команди в життєвому циклі */
typedef enum {
    CMD_STATE_FREE           = 0x00,
    CMD_STATE_ACCEPTED       = 0x01,
    CMD_STATE_EXECUTING      = 0x02,
    CMD_STATE_SUCCEEDED      = 0x03,
    CMD_STATE_FAILED         = 0x04,
    CMD_STATE_EXPIRED        = 0x05
} cmd_state_t;

/* Коди помилок та результатів */
typedef enum {
    CMD_ERR_OK               = 0,
    CMD_ERR_INVALID_MAGIC    = -1,
    CMD_ERR_CRC_MISMATCH     = -2,
    CMD_ERR_EXPIRED          = -3,
    CMD_ERR_BUSY             = -4,
    CMD_ERR_HARDWARE_FAULT   = -5
} cmd_err_t;

/* Структура бінарного пакету команди (мережевий формат) */
typedef struct __attribute__((packed)) {
    uint32_t magic;           /* 0x434D4431 */
    uint64_t token;           /* Токен ідемпотентності */
    uint16_t cmd_type;        /* cmd_type_t */
    uint32_t ttl_ms;          /* Допустимий час життя у мілісекундах */
    uint16_t payload_len;     /* Довжина корисних даних */
    uint8_t  payload[MAX_PAYLOAD_SIZE];
    uint32_t crc32;           /* Контрольна сума всього пакету без поля crc32 */
} cmd_packet_t;

/* Запис у кільцевому буфері ідемпотентності */
typedef struct {
    uint64_t    token;
    cmd_type_t  type;
    cmd_state_t state;
    int32_t     result_code;
    uint32_t    rx_time_ms;
    uint32_t    ttl_ms;
} idempotency_slot_t;

/* Контекст диспетчера команд */
typedef struct {
    idempotency_slot_t ring[IDEMPOTENCY_RING_SIZE];
    uint8_t            ring_head;
    /* Асинхронне поточне завдання */
    uint64_t           active_token;
    uint32_t           exec_start_ms;
    uint32_t           exec_timeout_ms;
} cmd_dispatcher_t;

/* Простий генератор CRC32 для валідації пакетів */
static uint32_t calculate_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320 & (-(int32_t)(crc & 1)));
        }
    }
    return ~crc;
}

/* Ініціалізація диспетчера */
void cmd_dispatcher_init(cmd_dispatcher_t *disp) {
    memset(disp, 0, sizeof(cmd_dispatcher_t));
}

/* Пошук токена в кільцевому буфері */
static idempotency_slot_t* find_slot(cmd_dispatcher_t *disp, uint64_t token) {
    for (uint8_t i = 0; i < IDEMPOTENCY_RING_SIZE; ++i) {
        if (disp->ring[i].state != CMD_STATE_FREE && disp->ring[i].token == token) {
            return &disp->ring[i];
        }
    }
    return NULL;
}

/* Виділення нового слота в кільцевому буфері */
static idempotency_slot_t* allocate_slot(cmd_dispatcher_t *disp, uint64_t token,
                                         cmd_type_t type, uint32_t now_ms, uint32_t ttl_ms) {
    idempotency_slot_t *slot = &disp->ring[disp->ring_head];
    disp->ring_head = (disp->ring_head + 1) % IDEMPOTENCY_RING_SIZE;

    slot->token       = token;
    slot->type        = type;
    slot->state       = CMD_STATE_ACCEPTED;
    slot->result_code = CMD_ERR_OK;
    slot->rx_time_ms  = now_ms;
    slot->ttl_ms      = ttl_ms;
    return slot;
}

/* Імітація апаратних дій виконавчого заліза */
static cmd_err_t execute_hardware_action(cmd_type_t type, const uint8_t *payload, uint16_t len) {
    switch (type) {
        case CMD_TYPE_SET_RELAY:
            if (len < 1) return CMD_ERR_HARDWARE_FAULT;
            /* Фізичний запис у регістр GPIO: наприклад, gpio_set_level(RELAY_PIN, payload[0]); */
            return CMD_ERR_OK;
        case CMD_TYPE_MOVE_STEPPER:
            /* Старт апаратного таймера кроків */
            return CMD_ERR_OK;
        case CMD_TYPE_CALIBRATE:
            /* Запуск асинхронного калібрування АЦП */
            return CMD_ERR_OK;
        default:
            return CMD_ERR_OK;
    }
}

/* Зовнішні колбеки відправки квитанцій у радіоканал */
extern void send_phase1_ack(uint64_t token, cmd_state_t state);
extern void send_phase2_ack(uint64_t token, cmd_state_t state, int32_t result_code);
extern uint32_t get_system_uptime_ms(void);

/* Головна точка входу: обробка вхідного мережевого пакету */
cmd_err_t cmd_dispatcher_process_packet(cmd_dispatcher_t *disp, const uint8_t *raw_buf, size_t raw_len) {
    if (raw_len < sizeof(cmd_packet_t)) {
        return CMD_ERR_INVALID_MAGIC;
    }

    const cmd_packet_t *pkt = (const cmd_packet_t *)raw_buf;

    /* 1. Перевірка магічного числа та цілісності CRC32 */
    if (pkt->magic != CMD_MAGIC) {
        return CMD_ERR_INVALID_MAGIC;
    }

    uint32_t calculated_crc = calculate_crc32(raw_buf, sizeof(cmd_packet_t) - sizeof(uint32_t));
    if (calculated_crc != pkt->crc32) {
        return CMD_ERR_CRC_MISMATCH;
    }

    uint32_t now = get_system_uptime_ms();

    /* 2. Перевірка на ідемпотентність (наявність токена в пам'яті) */
    idempotency_slot_t *existing = find_slot(disp, pkt->token);
    if (existing != NULL) {
        /* ДУБЛІКАТ! Залізо не чіпаємо, віддаємо збережений результат */
        if (existing->state == CMD_STATE_SUCCEEDED || existing->state == CMD_STATE_FAILED) {
            send_phase2_ack(existing->token, existing->state, existing->result_code);
            return CMD_ERR_OK;
        } else if (existing->state == CMD_STATE_EXECUTING) {
            send_phase1_ack(existing->token, CMD_STATE_EXECUTING);
            return CMD_ERR_OK;
        }
    }

    /* 3. Перевірка терміну придатності (TTL) */
    if (pkt->ttl_ms > 0 && pkt->ttl_ms < 50) {
        /* Залишок TTL менший за технологічний мінімум обробки */
        send_phase2_ack(pkt->token, CMD_STATE_EXPIRED, CMD_ERR_EXPIRED);
        return CMD_ERR_EXPIRED;
    }

    /* 4. Фіксація токена та Фаза 1 квитування (ACK_ACCEPTED) */
    idempotency_slot_t *slot = allocate_slot(disp, pkt->token, (cmd_type_t)pkt->cmd_type, now, pkt->ttl_ms);
    send_phase1_ack(pkt->token, CMD_STATE_ACCEPTED);

    /* 5. Запуск виконання дії на залізі */
    slot->state = CMD_STATE_EXECUTING;
    disp->active_token    = pkt->token;
    disp->exec_start_ms   = now;
    disp->exec_timeout_ms = (pkt->ttl_ms > 0) ? pkt->ttl_ms : 5000;

    cmd_err_t err = execute_hardware_action(slot->type, pkt->payload, pkt->payload_len);
    if (err != CMD_ERR_OK) {
        slot->state = CMD_STATE_FAILED;
        slot->result_code = err;
        send_phase2_ack(slot->token, CMD_STATE_FAILED, err);
        return err;
    }

    /* Для миттєвих операцій (наприклад, перемикання реле) відразу закриваємо Фазу 2 */
    if (slot->type == CMD_TYPE_SET_RELAY || slot->type == CMD_TYPE_NOOP) {
        slot->state = CMD_STATE_SUCCEEDED;
        slot->result_code = CMD_ERR_OK;
        send_phase2_ack(slot->token, CMD_STATE_SUCCEEDED, CMD_ERR_OK);
    }

    return CMD_ERR_OK;
}

/* Періодичний тік диспетчера (виклик із головного циклу або таймера) */
void cmd_dispatcher_tick(cmd_dispatcher_t *disp) {
    if (disp->active_token == 0) return;

    idempotency_slot_t *slot = find_slot(disp, disp->active_token);
    if (!slot || slot->state != CMD_STATE_EXECUTING) {
        disp->active_token = 0;
        return;
    }

    uint32_t now = get_system_uptime_ms();
    uint32_t elapsed = now - disp->exec_start_ms;

    /* Перевірка таймауту / TTL виконання */
    if (elapsed > disp->exec_timeout_ms) {
        slot->state = CMD_STATE_EXPIRED;
        slot->result_code = CMD_ERR_EXPIRED;
        send_phase2_ack(slot->token, CMD_STATE_EXPIRED, CMD_ERR_EXPIRED);
        disp->active_token = 0;
        /* Аварійне відключення драйверів: наприклад, stepper_stop(); */
    }
}
