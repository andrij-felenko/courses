#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>

#define FLIT_PAYLOAD_SIZE 64
#define FLIT_HEADER_SIZE  2
#define FLIT_CRC_SIZE     2
#define FLIT_TOTAL_SIZE   68

#define TOTAL_DATA_LANES  64
#define SPARE_LANES       4

/* Структура 68-байтового фліта UCIe Standard */
typedef struct {
    uint8_t  seq_id;
    uint8_t  proto_id;
    uint8_t  payload[FLIT_PAYLOAD_SIZE];
    uint16_t crc16;
} ucie_flit_t;

/* Фізичні параметри каналу D2D */
typedef struct {
    double   lane_capacitance_pf; /* Паразитна ємність лінії (пФ) */
    double   supply_voltage_v;    /* Напруга живлення Vdd (В) */
    uint64_t bad_lanes_mask;      /* Маска фізично несправних ліній */
    int8_t   remap_table[TOTAL_DATA_LANES]; /* Таблиця ремонту ліній */
    uint64_t total_transitions;   /* Лічильник перемикань для розрахунку енергії */
    uint64_t total_bits_sent;     /* Загальна кількість переданих бітів */
    uint64_t retry_count;         /* Кількість повторних передач */
} d2d_channel_t;

/* Обчислення CRC-16 CCITT (поліном 0x1021) */
static uint16_t compute_crc16(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (int b = 0; b < 8; ++b) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

/* Ініціалізація каналу зв'язку */
void d2d_channel_init(d2d_channel_t *ch, double cap_pf, double vdd) {
    ch->lane_capacitance_pf = cap_pf;
    ch->supply_voltage_v = vdd;
    ch->bad_lanes_mask = 0;
    ch->total_transitions = 0;
    ch->total_bits_sent = 0;
    ch->retry_count = 0;
    for (int i = 0; i < TOTAL_DATA_LANES; ++i) {
        ch->remap_table[i] = (int8_t)i; /* Пряме відображення 1:1 */
    }
}

/* Ремонт лінії: перепризначення дефектного контакту на резервний */
bool d2d_repair_lane(d2d_channel_t *ch, uint8_t bad_lane, uint8_t spare_idx) {
    if (bad_lane >= TOTAL_DATA_LANES || spare_idx >= SPARE_LANES) return false;
    ch->bad_lanes_mask |= (1ULL << bad_lane);
    ch->remap_table[bad_lane] = (int8_t)(TOTAL_DATA_LANES + spare_idx);
    printf("[PHY Repair] Лінію #%d перепризначено на резервну SPARE #%d\n", bad_lane, spare_idx);
    return true;
}

/* Пакування даних у фліт та розрахунок CRC */
void ucie_pack_flit(ucie_flit_t *flit, uint8_t seq, uint8_t proto, const uint8_t *data) {
    flit->seq_id = seq;
    flit->proto_id = proto;
    memcpy(flit->payload, data, FLIT_PAYLOAD_SIZE);

    uint8_t buffer[FLIT_HEADER_SIZE + FLIT_PAYLOAD_SIZE];
    buffer[0] = flit->seq_id;
    buffer[1] = flit->proto_id;
    memcpy(buffer + 2, flit->payload, FLIT_PAYLOAD_SIZE);

    flit->crc16 = compute_crc16(buffer, sizeof(buffer));
}

/* Симуляція передавання фліта через 64-бітну паралельну шину */
bool d2d_transmit_flit(d2d_channel_t *ch, const ucie_flit_t *tx_flit, ucie_flit_t *rx_flit, double error_prob) {
    uint8_t raw_tx[FLIT_TOTAL_SIZE];
    uint8_t raw_rx[FLIT_TOTAL_SIZE];

    /* Серіалізація структури у байтовий масив */
    raw_tx[0] = tx_flit->seq_id;
    raw_tx[1] = tx_flit->proto_id;
    memcpy(raw_tx + 2, tx_flit->payload, FLIT_PAYLOAD_SIZE);
    raw_tx[66] = (uint8_t)(tx_flit->crc16 >> 8);
    raw_tx[67] = (uint8_t)(tx_flit->crc16 & 0xFF);

    static uint64_t prev_bus_state = 0;

    /* Передавання 68 байтів за 9 тактів по 64-бітній шині (8 байтів за такт) */
    for (size_offset_t offset = 0; offset < FLIT_TOTAL_SIZE; offset += 8) {
        uint64_t current_word = 0;
        size_t chunk_len = (FLIT_TOTAL_SIZE - offset >= 8) ? 8 : (FLIT_TOTAL_SIZE - offset);
        memcpy(&current_word, raw_tx + offset, chunk_len);

        /* Розрахунок кількості перемикань бітів на лініях для енергії */
        uint64_t toggles = current_word ^ prev_bus_state;
        ch->total_transitions += __builtin_popcountll(toggles);
        prev_bus_state = current_word;
        ch->total_bits_sent += (chunk_len * 8);

        /* Емуляція проходження через фізичні лінії */
        uint64_t rx_word = current_word;
        for (int lane = 0; lane < 64; ++lane) {
            /* Якщо лінія несправна і не відремонтована — залипання в 0 */
            if ((ch->bad_lanes_mask & (1ULL << lane)) && (ch->remap_table[lane] == lane)) {
                rx_word &= ~(1ULL << lane);
            }
            /* Випадковий бітовий збій (інжекція шуму) */
            if (((double)rand() / RAND_MAX) < error_prob) {
                rx_word ^= (1ULL << lane);
            }
        }
        memcpy(raw_rx + offset, &rx_word, chunk_len);
    }

    /* Розпакування на стороні приймача */
    rx_flit->seq_id = raw_rx[0];
    rx_flit->proto_id = raw_rx[1];
    memcpy(rx_flit->payload, raw_rx + 2, FLIT_PAYLOAD_SIZE);
    rx_flit->crc16 = ((uint16_t)raw_rx[66] << 8) | raw_rx[67];

    /* Перевірка контрольної суми CRC-16 */
    uint8_t check_buf[FLIT_HEADER_SIZE + FLIT_PAYLOAD_SIZE];
    check_buf[0] = rx_flit->seq_id;
    check_buf[1] = rx_flit->proto_id;
    memcpy(check_buf + 2, rx_flit->payload, FLIT_PAYLOAD_SIZE);

    uint16_t calculated_crc = compute_crc16(check_buf, sizeof(check_buf));
    return (calculated_crc == rx_flit->crc16);
}

/* Протокол передачі з автоповтором ARQ */
bool d2d_send_with_arq(d2d_channel_t *ch, const ucie_flit_t *tx_flit, ucie_flit_t *rx_flit, int max_retries) {
    for (int attempt = 0; attempt <= max_retries; ++attempt) {
        if (attempt > 0) {
            ch->retry_count++;
            printf("  [ARQ Retry] Помилка CRC! Повторна передача фліта SeqID=%d (спроба %d)\n",
                   tx_flit->seq_id, attempt);
        }
        /* Імовірність випадкового шуму 0.001 (1 збій на 1000 бітів) */
        if (d2d_transmit_flit(ch, tx_flit, rx_flit, 0.001)) {
            return true; /* Успішне підтвердження ACK */
        }
    }
    return false; /* Збій зв'язку: NAK таймаут */
}

int main(void) {
    d2d_channel_t channel;
    /* C_load = 0.08 пФ (80 фФ для мікростовпчика CoWoS), Vdd = 0.75 В */
    d2d_channel_init(&channel, 0.08, 0.75);

    printf("=== Симуляція каналу зв'язку UCIe Die-to-Die ===\n\n");

    /* Тест 1: Передавання пакетів за нормальних умов */
    uint8_t test_data[FLIT_PAYLOAD_SIZE];
    for (int i = 0; i < FLIT_PAYLOAD_SIZE; ++i) test_data[i] = (uint8_t)(0xAA ^ i);

    ucie_flit_t tx_flit, rx_flit;
    for (uint8_t seq = 0; seq < 5; ++seq) {
        ucie_pack_flit(&tx_flit, seq, 0x01 /* PCIe */, test_data);
        if (d2d_send_with_arq(&channel, &tx_flit, &rx_flit, 3)) {
            printf("[ACK] Фліт SeqID=%d успішно прийнято. CRC=0x%04X\n", rx_flit.seq_id, rx_flit.crc16);
        }
    }

    /* Тест 2: Пошкодження лінії та автоматичний ремонт */
    printf("\n[Аварія] Фізичне пошкодження мікростовпчика на лінії #12!\n");
    channel.bad_lanes_mask |= (1ULL << 12);

    ucie_pack_flit(&tx_flit, 5, 0x02 /* CXL.mem */, test_data);
    if (!d2d_send_with_arq(&channel, &tx_flit, &rx_flit, 2)) {
        printf("[Link Error] Канал заблоковано через постійну помилку на лінії #12!\n");
    }

    /* Застосування ремонту ліній (Lane Repair) */
    d2d_repair_lane(&channel, 12, 0);

    if (d2d_send_with_arq(&channel, &tx_flit, &rx_flit, 3)) {
        printf("[ACK] Після ремонту фліт SeqID=%d успішно прийнято!\n", rx_flit.seq_id);
    }

    /* Підсумковий розрахунок енергоефективності */
    double cap_f = channel.lane_capacitance_pf * 1e-12;
    double vdd = channel.supply_voltage_v;
    double total_energy_joules = 0.5 * cap_f * vdd * vdd * (double)channel.total_transitions;
    double energy_pj_per_bit = (total_energy_joules / (double)channel.total_bits_sent) * 1e12;

    printf("\n=== Результати аналізу енергоспоживання ===\n");
    printf("Всього бітів передано: %llu\n", (unsigned long long)channel.total_bits_sent);
    printf("Кількість перемикань ліній: %llu\n", (unsigned long long)channel.total_transitions);
    printf("Повторних передач (Retries): %llu\n", (unsigned long long)channel.retry_count);
    printf("Питома енергія передавання: %.3f пДж / біт\n", energy_pj_per_bit);

    return 0;
}
