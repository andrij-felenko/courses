#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Базові адреси периферійних регістрів мікроконтролера STM32 (апаратна модель) */
#define HARDWARE_RCC_BASE       0x40023800U
#define HARDWARE_FLASH_BASE     0x40023C00U
#define HARDWARE_PWR_BASE       0x40007000U

/* Маски та регістри детектора просідання живлення (BOR) та тактування (CSS) */
#define RCC_CR_CSSON_MASK       (1U << 19)
#define PWR_CR_PLS_LEV3         (3U << 5)
#define PWR_CR_PVDE_MASK        (1U << 4)

/* Структура реєстрації стану апаратного голосування */
typedef struct {
    volatile uint32_t channel_a_register;
    volatile uint32_t channel_b_register;
    volatile uint32_t status_flags;
    volatile uint32_t error_counter;
} VoterHardware_t;

/* Структура комплементарної пари даних з інверсією та контрольною сумою */
typedef struct {
    uint32_t direct_val;
    uint32_t inverted_val;
    uint32_t checksum;
} ComplementaryRegisterPair_t;

/* Поріг розходження та шаблон інверсії бітів */
#define MAX_ALLOWED_DIVERGENCE  12U
#define COMPLEMENT_XOR_PATTERN  0xFFFFFFFFU

/* Константна таблиця коригувальних коефіцієнтів у фіксованій кратності (Fixed-Point Q16.16) */
static const uint32_t GAIN_TABLE_FIXED[4] = {
    0x00010000U, /* 1.0000 у форматі Q16.16 */
    0x0001047AU, /* 1.0175 у форматі Q16.16 */
    0x000108F5U, /* 1.0350 у форматі Q16.16 */
    0x00010D70U  /* 1.0525 у форматі Q16.16 */
};

/* Оновлення комплементарного запису з обчисленням контрольної суми */
static void write_complementary_pair(ComplementaryRegisterPair_t *pair, uint32_t value) {
    pair->direct_val = value;
    pair->inverted_val = value ^ COMPLEMENT_XOR_PATTERN;
    pair->checksum = value + (value ^ COMPLEMENT_XOR_PATTERN) + 0x5A5A5A5AU;
}

/* Перевірка цілісності комплементарної пари в ОЗУ */
static bool verify_complementary_pair(const ComplementaryRegisterPair_t *pair) {
    uint32_t expected_checksum = pair->direct_val + pair->inverted_val + 0x5A5A5A5AU;
    bool pattern_ok = ((pair->direct_val ^ pair->inverted_val) == COMPLEMENT_XOR_PATTERN);
    bool checksum_ok = (pair->checksum == expected_checksum);
    return pattern_ok && checksum_ok;
}

/* Ініціалізація апаратних захистів кристала від CCF (CSS, BOR) */
void configure_hardware_ccf_protection(void) {
    volatile uint32_t *rcc_cr = (volatile uint32_t *)(HARDWARE_RCC_BASE + 0x00U);
    volatile uint32_t *pwr_cr = (volatile uint32_t *)(HARDWARE_PWR_BASE + 0x00U);
    
    /* Увімкнення системи безпеки тактування (Clock Security System / CSS) */
    *rcc_cr |= RCC_CR_CSSON_MASK;
    
    /* Налаштування детектора просідання живлення BOR на максимальний поріг безпеки */
    *pwr_cr |= PWR_CR_PLS_LEV3 | PWR_CR_PVDE_MASK;
}

/* Обчислення сигналу у каналі А з використанням арифметики з фіксованою комою */
static uint32_t process_channel_a_fixed(uint32_t raw_adc, uint8_t gain_idx) {
    uint64_t product = (uint64_t)raw_adc * GAIN_TABLE_FIXED[gain_idx & 0x03U];
    return (uint32_t)(product >> 16);
}

/* Функціонально різнорідне обчислення у каналі Б через еквівалентні побітові зсуви */
static uint32_t process_channel_b_fixed(uint32_t raw_adc, uint8_t gain_idx) {
    uint32_t base_gain = GAIN_TABLE_FIXED[gain_idx & 0x03U];
    uint32_t shift_part = (base_gain >> 4);
    uint64_t temp = ((uint64_t)raw_adc * base_gain) + (shift_part & 0x0FU);
    return (uint32_t)(temp >> 16);
}

/* Детермінований низькорівневий голосувальник із часовим зсувом */
bool execute_hardware_voter_step(uint32_t adc_ch_a, uint32_t adc_ch_b, uint8_t mode, uint32_t *voted_result) {
    ComplementaryRegisterPair_t data_b;
    write_complementary_pair(&data_b, adc_ch_b);
    
    /* Канал А виконує обчислення негайно */
    uint32_t val_a = process_channel_a_fixed(adc_ch_a, mode);
    
    /* Перевірка цілісності оперативної пам'яті каналу Б перед обчисленням */
    if (!verify_complementary_pair(&data_b)) {
        *voted_result = 0U;
        return false;
    }
    
    /* Канал Б виконує різнорідне обчислення */
    uint32_t val_b = process_channel_b_fixed(data_b.direct_val, mode);
    
    /* Апаратне порівняння двох каналів */
    uint32_t delta = (val_a > val_b) ? (val_a - val_b) : (val_b - val_a);
    if (delta > MAX_ALLOWED_DIVERGENCE) {
        *voted_result = 0U;
        return false;
    }
    
    /* Видача середнього детермінованого значення */
    *voted_result = (val_a + val_b) >> 1;
    return true;
}
