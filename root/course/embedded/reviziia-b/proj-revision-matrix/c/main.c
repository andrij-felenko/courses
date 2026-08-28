#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Перелік підтримуваних апаратних ревізій плати.
 */
typedef enum {
    BOARD_REV_UNKNOWN = 0,
    BOARD_REV_A       = 1,
    BOARD_REV_B       = 2,
    BOARD_REV_C       = 3,
    BOARD_REV_D       = 4,
    BOARD_REV_E       = 5
} board_revision_t;

/**
 * @brief Структура допускового вікна відліків АЦП для ідентифікації ревізії.
 */
typedef struct {
    board_revision_t revision;
    uint16_t adc_min;
    uint16_t adc_max;
} rev_threshold_t;

static const rev_threshold_t REV_THRESHOLDS[] = {
    { BOARD_REV_A,    0,  300 },   /* 0.00 В: R1 DNP, R2 10k */
    { BOARD_REV_B,  850, 1200 },   /* 0.825 В (номінал 1024)  */
    { BOARD_REV_C, 1850, 2250 },   /* 1.650 В (номінал 2048)  */
    { BOARD_REV_D, 2900, 3300 },   /* 2.475 В (номінал 3072)  */
    { BOARD_REV_E, 3850, 4095 }    /* 3.300 В: R1 10k, R2 DNP */
};

#define REV_THRESHOLDS_COUNT (sizeof(REV_THRESHOLDS) / sizeof(REV_THRESHOLDS[0]))

/**
 * @brief Визначення ревізії плати за усередненим вибірковим значенням АЦП.
 * 
 * @param adc_raw_value Значення АЦП (12 біт: 0..4095).
 * @return board_revision_t Розпізнана ревізія або BOARD_REV_UNKNOWN при збої.
 */
board_revision_t board_identify_revision(uint16_t adc_raw_value) {
    for (size_t i = 0; i < REV_THRESHOLDS_COUNT; ++i) {
        if (adc_raw_value >= REV_THRESHOLDS[i].adc_min &&
            adc_raw_value <= REV_THRESHOLDS[i].adc_max) {
            return REV_THRESHOLDS[i].revision;
        }
    }
    return BOARD_REV_UNKNOWN;
}
