#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Константи специфікації BLE Core 5.4 */
#define BLE_CRC24_POLY        0x00065Bu
#define BLE_CRC24_INIT        0x555555u
#define BLE_T_IFS_US          150u
#define BLE_MAX_PAYLOAD_LEN   251u

/* Стани кінцевого автомата Link Layer */
typedef enum {
    LL_STATE_STANDBY = 0,
    LL_STATE_ADVERTISING,
    LL_STATE_SCANNING,
    LL_STATE_INITIATING,
    LL_STATE_CONNECTION_MASTER,
    LL_STATE_CONNECTION_SLAVE
} ll_state_t;

/* Структура пакету каналу даних Data Channel PDU */
typedef struct {
    uint8_t llid : 2;
    uint8_t nesn : 1;
    uint8_t sn   : 1;
    uint8_t md   : 1;
    uint8_t rfu  : 3;
    uint8_t length;
    uint8_t payload[BLE_MAX_PAYLOAD_LEN];
    uint32_t crc;
} ll_data_pdu_t;

/* Стан вузла зв'язку */
typedef struct {
    ll_state_t state;
    uint8_t transmit_sn;     /* Останній надісланий Sequence Number */
    uint8_t next_expected_sn;/* Очікуваний наступний Sequence Number */
    uint16_t sca_ppm;        /* Точність кварцу сну в ppm */
    uint32_t conn_interval_us;
    uint16_t slave_latency;
    uint32_t supervision_timeout_ms;
} ll_node_t;

/* Обчислення контрольної суми CRC-24 по бітах (LFSR) */
static uint32_t ble_crc24_calc(const uint8_t *data, size_len_t len, uint32_t crc_init) {
    uint32_t state = crc_init & 0x00FFFFFFu;
    for (size_t i = 0; i < len; ++i) {
        uint8_t byte = data[i];
        for (int bit = 0; bit < 8; ++bit) {
            uint8_t data_bit = (byte >> bit) & 1u;
            uint8_t state_bit23 = (state >> 23) & 1u;
            state = ((state << 1) & 0x00FFFFFFu);
            if (data_bit ^ state_bit23) {
                state ^= BLE_CRC24_POLY;
            }
        }
    }
    return state & 0x00FFFFFFu;
}

/* Розрахунок розширення вікна прийому через дрейф кварцу (Window Widening) */
static uint32_t calc_window_widening_us(uint16_t master_sca_ppm, uint16_t slave_sca_ppm, uint32_t sleep_time_us) {
    uint64_t total_drift_ppm = (uint64_t)master_sca_ppm + (uint64_t)slave_sca_ppm;
    /* window_widening = (master_drift + slave_drift) * sleep_time + 16 мкс (jitter) */
    uint32_t drift_us = (uint32_t)((total_drift_ppm * sleep_time_us) / 1000000ULL);
    return drift_us + 16u;
}

/* Формування кадру для передачі */
static void ll_build_pdu(ll_node_t *node, ll_data_pdu_t *pdu, const uint8_t *payload, uint8_t len, bool more_data) {
    pdu->llid = 0x02; /* 10b: Start of L2CAP message */
    pdu->sn = node->transmit_sn;
    pdu->nesn = node->next_expected_sn;
    pdu->md = more_data ? 1 : 0;
    pdu->rfu = 0;
    pdu->length = len;
    memcpy(pdu->payload, payload, len);

    /* Серіалізація заголовка та розрахунок CRC */
    uint8_t raw[BLE_MAX_PAYLOAD_LEN + 2];
    raw[0] = (uint8_t)(pdu->llid | (pdu->nesn << 2) | (pdu->sn << 3) | (pdu->md << 4));
    raw[1] = pdu->length;
    memcpy(&raw[2], pdu->payload, len);

    pdu->crc = ble_crc24_calc(raw, (size_t)(len + 2), BLE_CRC24_INIT);
}

/* Обробка отриманого кадру на приймачі */
static bool ll_receive_pdu(ll_node_t *receiver, const ll_data_pdu_t *pdu, bool simulate_crc_error) {
    uint8_t raw[BLE_MAX_PAYLOAD_LEN + 2];
    raw[0] = (uint8_t)(pdu->llid | (pdu->nesn << 2) | (pdu->sn << 3) | (pdu->md << 4));
    raw[1] = pdu->length;
    memcpy(&raw[2], pdu->payload, pdu->length);

    uint32_t expected_crc = ble_crc24_calc(raw, (size_t)(pdu->length + 2), BLE_CRC24_INIT);
    if (simulate_crc_error || pdu->crc != expected_crc) {
        printf("  [Rx] Помилка CRC! Пакет відкинуто. Очікуваний NESN лишається %u\n", receiver->next_expected_sn);
        return false;
    }

    /* Якщо SN збігається з очікуваним — це новий пакет */
    if (pdu->sn == receiver->next_expected_sn) {
        printf("  [Rx] Прийнято НОВИЙ пакет [SN=%u, NESN=%u, len=%u]: \"%.*s\"\n",
               pdu->sn, pdu->nesn, pdu->length, pdu->length, pdu->payload);
        /* Змінюємо NESN для підтвердження успішного прийому */
        receiver->next_expected_sn = (uint8_t)(1u - receiver->next_expected_sn);
    } else {
        printf("  [Rx] Прийнято ДУБЛІКАТ [SN=%u]. Повторно підтверджуємо поточний стан.\n", pdu->sn);
    }

    /* Перевіряємо підтвердження наших переданих даних (ACK від сусіда) */
    if (pdu->nesn != receiver->transmit_sn) {
        receiver->transmit_sn = (uint8_t)(1u - receiver->transmit_sn);
    }
    return true;
}

int main(void) {
    ll_node_t master = {
        .state = LL_STATE_CONNECTION_MASTER,
        .transmit_sn = 0,
        .next_expected_sn = 0,
        .sca_ppm = 50,
        .conn_interval_us = 20000, /* 20.0 мс */
        .slave_latency = 4,
        .supervision_timeout_ms = 2000
    };

    ll_node_t slave = {
        .state = LL_STATE_CONNECTION_SLAVE,
        .transmit_sn = 0,
        .next_expected_sn = 0,
        .sca_ppm = 250,
        .conn_interval_us = 20000,
        .slave_latency = 4,
        .supervision_timeout_ms = 2000
    };

    printf("=== СИМУЛЯТОР BLE LINK LAYER (ARQ & TIMINGS) ===\n\n");

    /* 1. Розрахунок дрейфу вікна */
    uint32_t sleep_time_us = master.conn_interval_us * (master.slave_latency + 1);
    uint32_t widening_us = calc_window_widening_us(master.sca_ppm, slave.sca_ppm, sleep_time_us);
    printf("[1] Розрахунок вікна розширення (Window Widening):\n");
    printf("    connInterval = %u мкс, Slave Latency = %u\n", master.conn_interval_us, master.slave_latency);
    printf("    Час сну Slave = %u мкс\n", sleep_time_us);
    printf("    Спільний дрейф = %u ppm -> Розширення вікна прийому = %u мкс\n\n",
           master.sca_ppm + slave.sca_ppm, widening_us);

    /* 2. Передача пакету 1 (Успішно) */
    printf("[2] Подія 1: Master передає пакет 1 -> Slave:\n");
    ll_data_pdu_t pdu1;
    const char *msg1 = "Hello BLE";
    ll_build_pdu(&master, &pdu1, (const uint8_t *)msg1, (uint8_t)strlen(msg1), false);
    printf("  [Tx Master] Пакет відправлено: SN=%u, NESN=%u, CRC=0x%06X\n", pdu1.sn, pdu1.nesn, pdu1.crc);
    ll_receive_pdu(&slave, &pdu1, false);

    /* Відповідь Slave (ACK) */
    ll_data_pdu_t ack1;
    ll_build_pdu(&slave, &ack1, NULL, 0, false);
    printf("  [Tx Slave]  Відповідь ACK:     SN=%u, NESN=%u, CRC=0x%06X\n", ack1.sn, ack1.nesn, ack1.crc);
    ll_receive_pdu(&master, &ack1, false);
    printf("\n");

    /* 3. Передача пакету 2 (Зіпсовано завадою) */
    printf("[3] Подія 2: Master передає пакет 2 (симуляція завади в ефірі):\n");
    ll_data_pdu_t pdu2;
    const char *msg2 = "Data block 2";
    ll_build_pdu(&master, &pdu2, (const uint8_t *)msg2, (uint8_t)strlen(msg2), false);
    printf("  [Tx Master] Пакет відправлено: SN=%u, NESN=%u, CRC=0x%06X\n", pdu2.sn, pdu2.nesn, pdu2.crc);
    ll_receive_pdu(&slave, &pdu2, true); /* Симуляція пошкодження CRC */

    /* Slave надсилає старий NESN (NACK) */
    ll_data_pdu_t nack;
    ll_build_pdu(&slave, &nack, NULL, 0, false);
    printf("  [Tx Slave]  Відповідь NACK:    SN=%u, NESN=%u (NESN не перемкнуто)\n", nack.sn, nack.nesn);
    ll_receive_pdu(&master, &nack, false);
    printf("\n");

    /* 4. Повторна передача пакету 2 (Retransmit) */
    printf("[4] Подія 3: Master фіксує незмінний NESN та повторює пакет 2:\n");
    ll_build_pdu(&master, &pdu2, (const uint8_t *)msg2, (uint8_t)strlen(msg2), false);
    printf("  [Tx Master] Retransmit:        SN=%u, NESN=%u, CRC=0x%06X\n", pdu2.sn, pdu2.nesn, pdu2.crc);
    ll_receive_pdu(&slave, &pdu2, false);

    /* Slave підтверджує успіх */
    ll_build_pdu(&slave, &ack1, NULL, 0, false);
    printf("  [Tx Slave]  Відповідь ACK:     SN=%u, NESN=%u\n", ack1.sn, ack1.nesn);
    ll_receive_pdu(&master, &ack1, false);

    return 0;
}
