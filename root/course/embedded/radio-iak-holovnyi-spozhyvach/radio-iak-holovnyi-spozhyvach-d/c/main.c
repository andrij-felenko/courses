/* ============================================================================
 * Енергоефективний менеджер радіотранзакцій (ANSI C99 / Вбудовані системи)
 * ============================================================================ */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define RF_MAX_RETRIES        3
#define RF_ADR_ACK_LIMIT      64
#define RF_ADR_ACK_DELAY      32

typedef enum {
    RF_STATE_SLEEP = 0,
    RF_STATE_WARMUP_PLL,
    RF_STATE_TRANSMITTING,
    RF_STATE_WAIT_RX1,
    RF_STATE_LISTEN_RX1,
    RF_STATE_WAIT_RX2,
    RF_STATE_LISTEN_RX2
} rf_state_t;

typedef enum {
    LORA_SF7 = 7,
    LORA_SF8 = 8,
    LORA_SF9 = 9,
    LORA_SF10 = 10,
    LORA_SF11 = 11,
    LORA_SF12 = 12
} lora_sf_t;

/* Щільне бінарне представлення корисного навантаження (рівно 5 байтів) */
#pragma pack(push, 1)
typedef struct {
    int16_t  temp_centi_deg;   /* Температура в 0.01 °C (-327.68 .. +327.67) */
    uint8_t  humidity_half_pct;/* Відносна вологість у 0.5% (0 .. 200 = 100%) */
    uint8_t  battery_raw_mv;   /* Напруга: (V - 2000) / 10 мВ (2.00 .. 4.55 В) */
    uint8_t  status_flags;     /* Бітові прапорці: D0=помилка сенсора, D1=ADR_ACK */
} telemetry_payload_t;
#pragma pack(pop)

typedef struct {
    rf_state_t  state;
    lora_sf_t   current_sf;
    int8_t      tx_power_dbm;
    uint32_t    tx_count;
    uint32_t    adr_ack_counter;
    uint32_t    total_coulombs_uc; /* Лічильник витраченого заряду в мікрокулонах */
    uint8_t     retry_count;
} rf_energy_manager_t;

void rf_manager_init(rf_energy_manager_t *mgr) {
    mgr->state = RF_STATE_SLEEP;
    mgr->current_sf = LORA_SF7;       /* Стартуємо з найбільш енергоощадного режиму */
    mgr->tx_power_dbm = 14;           /* Стандартні +14 дБм (25 мВт) */
    mgr->tx_count = 0;
    mgr->adr_ack_counter = 0;
    mgr->total_coulombs_uc = 0;
    mgr->retry_count = 0;
}

/* Пакування телеметрії у фіксовані 5 байтів */
uint8_t rf_manager_pack_telemetry(float temp_c, float hum_pct, float v_batt, 
                                  bool sensor_ok, uint8_t *out_buf, uint8_t max_len) {
    if (max_len < sizeof(telemetry_payload_t)) return 0;

    telemetry_payload_t payload;
    payload.temp_centi_deg = (int16_t)(temp_c * 100.0f);
    
    if (hum_pct < 0.0f) hum_pct = 0.0f;
    if (hum_pct > 100.0f) hum_pct = 100.0f;
    payload.humidity_half_pct = (uint8_t)(hum_pct * 2.0f);

    uint32_t mv = (uint32_t)(v_batt * 1000.0f);
    if (mv < 2000) mv = 2000;
    if (mv > 4550) mv = 4550;
    payload.battery_raw_mv = (uint8_t)((mv - 2000) / 10);

    payload.status_flags = sensor_ok ? 0x00 : 0x01;

    memcpy(out_buf, &payload, sizeof(telemetry_payload_t));
    return (uint8_t)sizeof(telemetry_payload_t);
}

/* Оцінка заряду та перехід до передачі */
void rf_manager_start_tx(rf_energy_manager_t *mgr, uint32_t toa_ms) {
    mgr->state = RF_STATE_TRANSMITTING;
    mgr->tx_count++;
    mgr->adr_ack_counter++;

    /* Оцінка струму Tx залежно від потужності (для чіпа з DC-DC, як SX1262) */
    uint32_t current_ma = 22; /* Базовий струм при +14 дБм */
    if (mgr->tx_power_dbm >= 20) current_ma = 95;
    else if (mgr->tx_power_dbm <= 2) current_ma = 12;

    /* Q = I * t (мікрокулони = мА * мс) */
    mgr->total_coulombs_uc += (current_ma * toa_ms) + (5 * 2); /* + запуск PLL */
}

/* Обробка успішного отримання підтвердження (Downlink ACK) */
void rf_manager_on_ack_received(rf_energy_manager_t *mgr, int8_t gateway_snr) {
    mgr->adr_ack_counter = 0;
    mgr->retry_count = 0;
    mgr->state = RF_STATE_SLEEP;

    /* Локальна оптимізація потужності: якщо сигнал чудовий, зменшуємо потужність */
    if (gateway_snr > 8 && mgr->tx_power_dbm > 2) {
        mgr->tx_power_dbm -= 3; /* Знижуємо на 3 дБ (у 2 рази по випромінюванню) */
    }
}

/* Обробка втрати зв'язку (ADR Fallback) */
void rf_manager_on_tx_timeout(rf_energy_manager_t *mgr) {
    if (mgr->retry_count < RF_MAX_RETRIES) {
        mgr->retry_count++;
        /* Експоненційний відкат або негайний перехід у сон */
        mgr->state = RF_STATE_SLEEP;
        return;
    }

    /* Якщо досягнуто ліміту ADR без відповідей — покроковий fallback */
    if (mgr->adr_ack_counter >= (RF_ADR_ACK_LIMIT + RF_ADR_ACK_DELAY)) {
        if (mgr->tx_power_dbm < 20) {
            mgr->tx_power_dbm = 20; /* Спочатку викручуємо потужність на максимум */
        } else if (mgr->current_sf < LORA_SF12) {
            mgr->current_sf = (lora_sf_t)(mgr->current_sf + 1); /* Збільшуємо SF */
            mgr->adr_ack_counter = RF_ADR_ACK_LIMIT; /* Скидаємо для наступного кроку */
        }
    }
    mgr->retry_count = 0;
    mgr->state = RF_STATE_SLEEP;
}
