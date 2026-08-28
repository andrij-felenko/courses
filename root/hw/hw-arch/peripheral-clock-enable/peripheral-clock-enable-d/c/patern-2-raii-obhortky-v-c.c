#include <stdint.h>
#include <stdbool.h>

// Ідентифікатори периферійних модулів
typedef enum {
    PERIPH_ID_GPIOA = 0,
    PERIPH_ID_GPIOB,
    PERIPH_ID_USART1,
    PERIPH_ID_USART2,
    PERIPH_ID_I2C1,
    PERIPH_ID_SPI1,
    PERIPH_ID_COUNT
} periph_id_t;

// Дескриптор апаратного регістра тактування
typedef struct {
    volatile uint32_t *enr_reg;  // Вказівник на регістр RCC_xxxENR
    uint32_t           en_mask;  // Маска біта ввімкнення
    uint8_t            ref_count;// Лічильник активних клієнтів
} periph_clock_desc_t;

// Симуляція адрес регістрів для прикладу
static uint32_t fake_rcc_ahb1enr = 0;
static uint32_t fake_rcc_apb1enr = 0;
static uint32_t fake_rcc_apb2enr = 0;

static periph_clock_desc_t g_periph_table[PERIPH_ID_COUNT] = {
    [PERIPH_ID_GPIOA]  = { .enr_reg = &fake_rcc_ahb1enr, .en_mask = (1U << 0), .ref_count = 0 },
    [PERIPH_ID_GPIOB]  = { .enr_reg = &fake_rcc_ahb1enr, .en_mask = (1U << 1), .ref_count = 0 },
    [PERIPH_ID_USART1] = { .enr_reg = &fake_rcc_apb2enr, .en_mask = (1U << 4), .ref_count = 0 },
    [PERIPH_ID_USART2] = { .enr_reg = &fake_rcc_apb1enr, .en_mask = (1U << 17),.ref_count = 0 },
    [PERIPH_ID_I2C1]   = { .enr_reg = &fake_rcc_apb1enr, .en_mask = (1U << 21),.ref_count = 0 },
    [PERIPH_ID_SPI1]   = { .enr_reg = &fake_rcc_apb2enr, .en_mask = (1U << 12),.ref_count = 0 },
};

// Захоплення тактування модуля
bool clock_manager_acquire(periph_id_t id) {
    if (id >= PERIPH_ID_COUNT) return false;
    periph_clock_desc_t *desc = &g_periph_table[id];

    if (desc->ref_count == 0) {
        // Перший клієнт: фізичне ввімкнення такту
        *desc->enr_reg |= desc->en_mask;
        // Фіктивне читання для бар'єра затримки
        (void)(*desc->enr_reg);
    }
    desc->ref_count++;
    return true;
}

// Звільнення тактування модуля
bool clock_manager_release(periph_id_t id) {
    if (id >= PERIPH_ID_COUNT) return false;
    periph_clock_desc_t *desc = &g_periph_table[id];

    if (desc->ref_count == 0) return false; // Захист від подвійного звільнення
    desc->ref_count--;

    if (desc->ref_count == 0) {
        // Останній клієнт пішов: фізичне вимкнення такту
        *desc->enr_reg &= ~desc->en_mask;
        (void)(*desc->enr_reg);
    }
    return true;
}
