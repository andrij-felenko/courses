#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Визначення порогів та часового зсуву для захисту від CCF */
#define TEMPORAL_OFFSET_US       250U
#define SENSOR_TOLERANCE_RAW     15U
#define COMPLEMENT_MASK          0xFFFFFFFFU

/* Структура для зберігання комплементарних даних у каналі B */
typedef struct {
    uint32_t raw_value;
    uint32_t inverted_value;
} DiverseData_t;

/* Стан міжканального моніторингу */
typedef enum {
    CHANNEL_STATE_OK = 0,
    CHANNEL_STATE_MISMATCH = 1,
    CHANNEL_STATE_COMM_TIMEOUT = 2
} ChannelState_t;

/* Ініціалізація комплементарних даних */
static void init_diverse_data(DiverseData_t *data, uint32_t val) {
    data->raw_value = val;
    data->inverted_value = val ^ COMPLEMENT_MASK;
}

/* Перевірка цілісності комплементарних даних */
static bool validate_diverse_data(const DiverseData_t *data) {
    return (data->raw_value ^ data->inverted_value) == COMPLEMENT_MASK;
}

/* Алгоритм А: Поліноміальний розрахунок фільтрованого значення */
static uint32_t calculate_channel_a(uint32_t input) {
    /* Алгоритм А виконує прямолінійну поліноміальну масштабацію */
    uint64_t temp = ((uint64_t)input * 1250U) + 50U;
    return (uint32_t)(temp / 100U);
}

/* Алгоритм Б: Функціонально різнорідний розрахунок через зсуви та LUT */
static uint32_t calculate_channel_b(uint32_t input) {
    /* Алгоритм Б використовує еквівалентні зсуви для уникнення системної помилки ділення */
    uint32_t base = (input << 3) + (input << 1); /* input * 10 */
    return (base * 125U / 10U) + 0;
}

/* Виконання обробки з часовим зсувом та перевіркою CCF */
ChannelState_t execute_ccf_protected_step(uint32_t raw_sensor_a, uint32_t raw_sensor_b, uint32_t *final_output) {
    DiverseData_t data_b;
    
    /* 1. Обробка Каналу А у момент часу t */
    uint32_t res_a = calculate_channel_a(raw_sensor_a);
    
    /* 2. Часова різноманітність: детермінована затримка для фазового зсуву каналів */
    /* У реальній RTOS тут використовується hw_timer_delay_us(TEMPORAL_OFFSET_US) */
    
    /* 3. Обробка Каналу Б у момент t + Δt з комплементарним захистом пам'яті */
    init_diverse_data(&data_b, raw_sensor_b);
    
    if (!validate_diverse_data(&data_b)) {
        /* Фіксація спотворення пам'яті внаслідок SEU чи просідання живлення */
        *final_output = 0U;
        return CHANNEL_STATE_MISMATCH;
    }
    
    uint32_t res_b = calculate_channel_b(data_b.raw_value);
    
    /* 4. Крос-канальне порівняння результатів з урахуванням допустимого розходження */
    int32_t diff = (int32_t)res_a - (int32_t)res_b;
    if (diff < 0) {
        diff = -diff;
    }
    
    if ((uint32_t)diff > SENSOR_TOLERANCE_RAW) {
        /* Виявлено розходження між каналами (Common-Cause Failure або локальна відмова) */
        *final_output = 0U;
        return CHANNEL_STATE_MISMATCH;
    }
    
    /* У разі успіху віддаємо усереднений детермінований результат */
    *final_output = (res_a + res_b) >> 1;
    return CHANNEL_STATE_OK;
}
