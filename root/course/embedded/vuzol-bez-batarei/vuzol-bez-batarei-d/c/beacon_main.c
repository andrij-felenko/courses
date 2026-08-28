/* beacon_main.c — Прошивка безбатарейного термомаяка на C */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Регістри апаратного трансивера та периферії (абстракція низького рівня) */
#define RADIO_BASE_ADDR        0x40001000UL
#define RADIO_CRCCNF           (*(volatile uint32_t *)(RADIO_BASE_ADDR + 0x534))
#define RADIO_PACKETPTR        (*(volatile uint32_t *)(RADIO_BASE_ADDR + 0x504))
#define RADIO_FREQUENCY        (*(volatile uint32_t *)(RADIO_BASE_ADDR + 0x508))
#define RADIO_TXPOWER          (*(volatile uint32_t *)(RADIO_BASE_ADDR + 0x50C))
#define RADIO_MODE             (*(volatile uint32_t *)(RADIO_BASE_ADDR + 0x510))
#define RADIO_TASKS_TXEN       (*(volatile uint32_t *)(RADIO_BASE_ADDR + 0x000))
#define RADIO_TASKS_START      (*(volatile uint32_t *)(RADIO_BASE_ADDR + 0x008))
#define RADIO_EVENTS_READY     (*(volatile uint32_t *)(RADIO_BASE_ADDR + 0x100))
#define RADIO_EVENTS_END       (*(volatile uint32_t *)(RADIO_BASE_ADDR + 0x10C))
#define RADIO_TASKS_DISABLE    (*(volatile uint32_t *)(RADIO_BASE_ADDR + 0x010))

/* Адреса захищеної енергонезалежної пам'яті FRAM */
#define FRAM_STORAGE_ADDR      0x20003F00UL

#pragma pack(push, 1)
/* Структура збереження стану між імпульсами Run-to-Die */
typedef struct {
    uint32_t boot_magic;      /* Сигнатура ініціалізації: 0x55AA55AA */
    uint32_t sequence_id;     /* Монотонний лічильник передач */
    int16_t  last_temp_c_x10; /* Останній виміряний показник (0.1 °C) */
    uint16_t last_vcap_mv;    /* Напруга накопичувача на момент передачі (мВ) */
    uint16_t crc16;           /* Контрольна сума структури CCITT-16 */
} fram_state_t;

/* Структура стандартного нез'єднуваного кадру BLE Advertising (ADV_NONCONN_IND) */
typedef struct {
    uint8_t  header;          /* Тип PDU: 0x02 = ADV_NONCONN_IND, TxAdd = 1 (Random) */
    uint8_t  length;          /* Довжина корисного навантаження (Payload Length) */
    uint8_t  adv_addr[6];     /* Статична випадкова MAC-адреса передавача */
    
    /* AD Structure 1: Flags */
    uint8_t  ad1_len;         /* 0x02 */
    uint8_t  ad1_type;        /* 0x01 = Flags */
    uint8_t  ad1_flags;       /* 0x06 = LE General Discoverable | BR/EDR Not Supported */

    /* AD Structure 2: Manufacturer Specific Data */
    uint8_t  ad2_len;         /* 13 байтів */
    uint8_t  ad2_type;        /* 0xFF = Manufacturer Data */
    uint16_t company_id;      /* 0xFFFF = Тестовий ідентифікатор виробника */
    uint32_t sequence_num;    /* Монотонний лічильник з FRAM */
    int16_t  temperature_x10; /* Температура: +23.5 °C -> 235 */
    uint16_t voltage_mv;      /* Напруга шини: 3150 мВ */
    uint8_t  energy_source;   /* 0x01 = Сонячний збирач довкілля */
} ble_adv_packet_t;
#pragma pack(pop)

/* Швидкий табличний розрахунок контрольної суми CRC-16-CCITT */
static uint16_t compute_crc16(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

/* Зчитування та валідація стану з FRAM */
static void load_or_init_fram_state(fram_state_t *state) {
    volatile fram_state_t *fram_ptr = (volatile fram_state_t *)FRAM_STORAGE_ADDR;
    
    /* Пряме копіювання з шини FRAM без очікування */
    memcpy(state, (const void *)fram_ptr, sizeof(fram_state_t));

    uint16_t expected_crc = compute_crc16((const uint8_t *)state, 
                                          sizeof(fram_state_t) - sizeof(uint16_t));

    if (state->boot_magic != 0x55AA55AA || state->crc16 != expected_crc) {
        /* Холодний пуск після повної втрати заряду або перший запуск */
        state->boot_magic = 0x55AA55AA;
        state->sequence_id = 0;
        state->last_temp_c_x10 = 0;
        state->last_vcap_mv = 0;
        state->crc16 = compute_crc16((const uint8_t *)state, 
                                     sizeof(fram_state_t) - sizeof(uint16_t));
    }
}

/* Атомарний запис оновленого стану у FRAM */
static void commit_fram_state(fram_state_t *state) {
    volatile fram_state_t *fram_ptr = (volatile fram_state_t *)FRAM_STORAGE_ADDR;
    state->sequence_id++;
    state->crc16 = compute_crc16((const uint8_t *)state, 
                                 sizeof(fram_state_t) - sizeof(uint16_t));
    
    /* Запис у FRAM виконується за один такт шини без потреби помпи чи прапорців зайнятості */
    memcpy((void *)fram_ptr, state, sizeof(fram_state_t));
}

/* Швидке вимірювання вбудованим АЦП */
static void sample_sensors(int16_t *out_temp_x10, uint16_t *out_vcap_mv) {
    /* Емуляція швидкого опитування АЦП за 250 мкс */
    *out_temp_x10 = 245;   /* +24.5 °C */
    *out_vcap_mv = 3180;   /* 3.18 В на ємності */
}

/* Випромінювання пакета на заданому каналі BLE (37, 38 або 39) */
static void transmit_ble_channel(uint8_t channel_idx, const ble_adv_packet_t *pkt) {
    /* Частоти BLE: канал 37 (2402 МГц), 38 (2426 МГц), 39 (2480 МГц) */
    static const uint8_t freq_map[3] = { 2, 26, 80 };
    
    RADIO_FREQUENCY = freq_map[channel_idx];
    RADIO_PACKETPTR = (uint32_t)pkt;
    RADIO_EVENTS_READY = 0;
    RADIO_EVENTS_END = 0;

    /* Увімкнення підсилювача потужності передавача */
    RADIO_TASKS_TXEN = 1;
    while (!RADIO_EVENTS_READY);

    /* Старт передачі кадру */
    RADIO_TASKS_START = 1;
    while (!RADIO_EVENTS_END);

    /* Негайне вимкнення радіоканалу для збереження заряду */
    RADIO_TASKS_DISABLE = 1;
}

int main(void) {
    fram_state_t state;
    ble_adv_packet_t packet;

    /* 1. Відновлення прогресу з енергонезалежної FRAM */
    load_or_init_fram_state(&state);

    /* 2. Швидкий замір фізичних величин */
    sample_sensors(&state.last_temp_c_x10, &state.last_vcap_mv);

    /* 3. Формування рекламного кадру */
    packet.header = 0x42; /* ADV_NONCONN_IND | Random Address */
    packet.length = sizeof(ble_adv_packet_t) - 2;
    
    /* Статична MAC-адреса пристрою (Static Random Address) */
    packet.adv_addr[0] = 0xAA;
    packet.adv_addr[1] = 0xBB;
    packet.adv_addr[2] = 0xCC;
    packet.adv_addr[3] = 0xDD;
    packet.adv_addr[4] = 0xEE;
    packet.adv_addr[5] = 0xC0; /* Біти 11 у старшому байті позначають Random Static */

    packet.ad1_len = 0x02;
    packet.ad1_type = 0x01;
    packet.ad1_flags = 0x06;

    packet.ad2_len = 12;
    packet.ad2_type = 0xFF;
    packet.company_id = 0xFFFF;
    packet.sequence_num = state.sequence_id;
    packet.temperature_x10 = state.last_temp_c_x10;
    packet.voltage_mv = state.last_vcap_mv;
    packet.energy_source = 0x01;

    /* 4. Налаштування апаратного радіомодуля */
    RADIO_MODE = 0x03;     /* BLE 1Mbps */
    RADIO_TXPOWER = 0x00;  /* 0 dBm (струм близько 7.5 мА) */
    RADIO_CRCCNF = 0x103;  /* 3-байтний апаратний CRC для BLE */

    /* 5. Випромінювання на трьох каналах */
    transmit_ble_channel(0, &packet); /* Канал 37 */
    transmit_ble_channel(1, &packet); /* Канал 38 */
    transmit_ble_channel(2, &packet); /* Канал 39 */

    /* 6. Збереження оновленого стану у FRAM перед знеструмленням */
    commit_fram_state(&state);

    /* 7. Засинання в очікуванні відсікання живлення супервізором */
    while (1) {
        __asm volatile("wfi");
    }

    return 0;
}
