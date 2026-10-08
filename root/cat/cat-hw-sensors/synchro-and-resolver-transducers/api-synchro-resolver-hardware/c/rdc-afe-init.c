#include <stdint.h>
#include <stdbool.h>

/* Структура конфігурації аналогового фронтенду RDC */
typedef struct {
    uint32_t carrier_freq_hz;  /* Частота збудження: 10000 Гц */
    uint16_t input_gain_db;     /* Підсилення вхідного AFE: 0 dB, 6 dB */
    int16_t  phase_adj_deg;    /* Фазова компенсація в градусах */
    bool     auto_gain_en;     /* Автоматичне регулювання підсилення */
} rdc_afe_config_t;

/* Ініціалізація реєстрів AFE перетворювача RDC */
int32_t rdc_afe_init(const rdc_afe_config_t *config) {
    if (config == NULL || config->carrier_freq_hz < 4000 || config->carrier_freq_hz > 20000) {
        return -1; /* Помилка недопустимих параметрів */
    }

    uint16_t ctrl_reg = 0;
    if (config->carrier_freq_hz == 10000) {
        ctrl_reg |= (1 << 4); /* Установка дільника частоти 10 кГц */
    }
    
    if (config->auto_gain_en) {
        ctrl_reg |= (1 << 2); /* Увімкнення AGC */
    }

    /* Запис конфігураційного слова в АПІ мікросхеми RDC */
    /* rdc_write_register(RDC_REG_AFE_CTRL, ctrl_reg); */

    return 0; /* Успішна ініціалізація */
}
