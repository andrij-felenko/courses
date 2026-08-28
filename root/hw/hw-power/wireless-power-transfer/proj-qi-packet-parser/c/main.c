#include <stdint.h>
#include <stdbool.h>

#define QI_BIT_HALF_MIN_US    180
#define QI_BIT_HALF_MAX_US    320
#define QI_BIT_FULL_MIN_US    420
#define QI_BIT_FULL_MAX_US    580

#define QI_MAX_PAYLOAD_LEN    32
#define QI_PREAMBLE_MIN_BITS  11

/* Заголовки стандартних пакетів WPC Qi */
#define QI_HDR_SIGNAL_STRENGTH  0x01
#define QI_HDR_END_TRANSFER     0x02
#define QI_HDR_CONTROL_ERROR    0x03
#define QI_HDR_RECEIVED_POWER   0x04
#define QI_HDR_CONFIG           0x51
#define QI_HDR_IDENTIFICATION   0x71

typedef enum {
    BMC_WAIT_SYNC,
    BMC_FIRST_HALF,
    BMC_FULL_CELL
} BmcState;

typedef enum {
    QI_STATE_PREAMBLE,
    QI_STATE_HEADER,
    QI_STATE_PAYLOAD,
    QI_STATE_CHECKSUM
} QiParserState;

typedef struct {
    uint8_t header;
    uint8_t payload[QI_MAX_PAYLOAD_LEN];
    uint8_t payload_len;
    uint8_t checksum;
    bool valid;
} QiPacket;

typedef struct {
    /* Стан BMC */
    BmcState bmc_state;
    uint32_t last_edge_time_us;
    uint8_t preamble_count;

    /* Побайтовий бітовий буфер */
    uint8_t rx_byte;
    uint8_t bit_index;

    /* Стан парсера пакетів */
    QiParserState parser_state;
    QiPacket current_packet;
    uint8_t payload_idx;
    uint8_t calc_checksum;

    /* Колбек успішного прийому */
    void (*on_packet_received)(const QiPacket *pkt);
} QiReceiver;

/* Ініціалізація структури приймача */
void qi_receiver_init(QiReceiver *rx, void (*callback)(const QiPacket *pkt)) {
    rx->bmc_state = BMC_WAIT_SYNC;
    rx->last_edge_time_us = 0;
    rx->preamble_count = 0;
    rx->rx_byte = 0;
    rx->bit_index = 0;
    rx->parser_state = QI_STATE_PREAMBLE;
    rx->payload_idx = 0;
    rx->calc_checksum = 0;
    rx->on_packet_received = callback;
    rx->current_packet.valid = false;
}

/* Отримання довжини корисного навантаження за кодом заголовка */
static uint8_t qi_get_payload_length(uint8_t header) {
    switch (header) {
        case QI_HDR_SIGNAL_STRENGTH: return 1;
        case QI_HDR_END_TRANSFER:    return 1;
        case QI_HDR_CONTROL_ERROR:   return 1;
        case QI_HDR_RECEIVED_POWER:  return 1;
        case QI_HDR_CONFIG:          return 5;
        case QI_HDR_IDENTIFICATION:  return 7;
        default:
            /* Для нестандартних/пропрієтарних пакетів Qi: біти 5..7 задають довжину */
            return (header >> 5) + 1;
    }
}

/* Обробка одного завершеного прийнятого байта */
static void qi_parser_push_byte(QiReceiver *rx, uint8_t byte) {
    switch (rx->parser_state) {
        case QI_STATE_PREAMBLE:
            /* Перший не-0xFF байт після преамбули є заголовком */
            rx->current_packet.header = byte;
            rx->current_packet.payload_len = qi_get_payload_length(byte);
            rx->calc_checksum = byte;
            rx->payload_idx = 0;
            rx->parser_state = (rx->current_packet.payload_len > 0) ? QI_STATE_PAYLOAD : QI_STATE_CHECKSUM;
            break;

        case QI_STATE_PAYLOAD:
            rx->current_packet.payload[rx->payload_idx++] = byte;
            rx->calc_checksum ^= byte;
            if (rx->payload_idx >= rx->current_packet.payload_len) {
                rx->parser_state = QI_STATE_CHECKSUM;
            }
            break;

        case QI_STATE_CHECKSUM:
            rx->current_packet.checksum = byte;
            rx->current_packet.valid = (rx->calc_checksum == byte);
            if (rx->current_packet.valid && rx->on_packet_received) {
                rx->on_packet_received(&rx->current_packet);
            }
            /* Повертаємося до пошуку наступної преамбули */
            rx->parser_state = QI_STATE_PREAMBLE;
            rx->preamble_count = 0;
            break;
    }
}

/* Обробка одного прийнятого біта */
static void qi_push_bit(QiReceiver *rx, uint8_t bit) {
    if (rx->parser_state == QI_STATE_PREAMBLE) {
        if (bit == 1) {
            rx->preamble_count++;
        } else {
            /* Якщо накопичили достатньо одиниць преамбули, перший 0 позначає Start Bit */
            if (rx->preamble_count >= QI_PREAMBLE_MIN_BITS) {
                rx->bit_index = 0;
                rx->rx_byte = 0;
                rx->parser_state = QI_STATE_HEADER;
            }
            rx->preamble_count = 0;
        }
        return;
    }

    /* Збір байта: у стандарті Qi біти передаються MSB-first у межах байта */
    rx->rx_byte = (rx->rx_byte << 1) | (bit & 0x01);
    rx->bit_index++;

    if (rx->bit_index >= 8) {
        qi_parser_push_byte(rx, rx->rx_byte);
        rx->bit_index = 0;
        rx->rx_byte = 0;
    }
}

/* Переривання захоплення фронтів таймера (Edge Capture ISR) */
void qi_receiver_on_edge(QiReceiver *rx, uint32_t current_time_us) {
    if (rx->last_edge_time_us == 0) {
        rx->last_edge_time_us = current_time_us;
        return;
    }

    uint32_t dt = current_time_us - rx->last_edge_time_us;
    rx->last_edge_time_us = current_time_us;

    /* Фільтрація брязкоту та викидів */
    if (dt < QI_BIT_HALF_MIN_US) {
        return;
    }

    switch (rx->bmc_state) {
        case BMC_WAIT_SYNC:
            if (dt >= QI_BIT_HALF_MIN_US && dt <= QI_BIT_HALF_MAX_US) {
                rx->bmc_state = BMC_FIRST_HALF;
            } else if (dt >= QI_BIT_FULL_MIN_US && dt <= QI_BIT_FULL_MAX_US) {
                qi_push_bit(rx, 0);
            }
            break;

        case BMC_FIRST_HALF:
            /* Очікуємо другу половину біта для логічної «1» */
            if (dt >= QI_BIT_HALF_MIN_US && dt <= QI_BIT_HALF_MAX_US) {
                qi_push_bit(rx, 1);
                rx->bmc_state = BMC_WAIT_SYNC;
            } else {
                /* Помилка синхронізації — скидання стану */
                rx->bmc_state = BMC_WAIT_SYNC;
                rx->preamble_count = 0;
            }
            break;

        default:
            rx->bmc_state = BMC_WAIT_SYNC;
            break;
    }
}

/* ========================================================================= */
/* Замкнений ПІД-регулятор потужності інвертора за пакетами CEP               */
/* ========================================================================= */

#define FREQ_MIN_KHZ  110.0f
#define FREQ_MAX_KHZ  205.0f
#define KP_GAIN       0.25f
#define KI_GAIN       0.05f

typedef struct {
    float current_freq_khz;
    float integral_err;
} QiPowerController;

void qi_controller_init(QiPowerController *ctrl) {
    ctrl->current_freq_khz = 145.0f; /* Стартова безпечна частота вище резонансу */
    ctrl->integral_err = 0.0f;
}

/* Обробка пакета Control Error Packet (CEP) */
void qi_controller_process_cep(QiPowerController *ctrl, int8_t cep_value) {
    /* cep_value > 0: приймачу бракує напруги -> ЗНИЖУЄМО частоту (ближче до резонансу)
       cep_value < 0: напруга завищена -> ПІДВИЩУЄМО частоту (далі від резонансу) */
    float error = (float)cep_value;
    ctrl->integral_err += error;

    /* Анти-вінд-ап захист інтегратора */
    if (ctrl->integral_err > 50.0f)  ctrl->integral_err = 50.0f;
    if (ctrl->integral_err < -50.0f) ctrl->integral_err = -50.0f;

    float delta_f = -(KP_GAIN * error + KI_GAIN * ctrl->integral_err);
    ctrl->current_freq_khz += delta_f;

    /* Захисне насичення робочого діапазону частот */
    if (ctrl->current_freq_khz < FREQ_MIN_KHZ) ctrl->current_freq_khz = FREQ_MIN_KHZ;
    if (ctrl->current_freq_khz > FREQ_MAX_KHZ) ctrl->current_freq_khz = FREQ_MAX_KHZ;
}
