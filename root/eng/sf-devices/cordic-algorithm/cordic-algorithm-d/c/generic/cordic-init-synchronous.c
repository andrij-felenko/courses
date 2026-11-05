#include <stdint.h>
#include <stdbool.h>

/* Структура периферійних регістрів апаратного блоку CORDIC */
typedef struct {
    volatile uint32_t CSR;   /* Регістр керування та стану */
    volatile uint32_t WDATA; /* Регістр запису аргументів */
    volatile uint32_t RDATA; /* Регістр зчитування результатів */
} cordic_hardware_t;

/* Базовий адрес периферійного модуля в адресному просторі мікроконтролера */
#define CORDIC_PERIPH_BASE  (0x40020C00UL)
#define CORDIC_HW           ((cordic_hardware_t*)CORDIC_PERIPH_BASE)

/* Бітові маски налаштування регістра CSR */
#define CORDIC_FUNC_COS_SIN       (0x00000000UL) /* Режим обертання: обчислення cos та sin */
#define CORDIC_FUNC_MOD_PHASE     (0x00000002UL) /* Векторний режим: модуль та кут (atan2) */
#define CORDIC_PRECISION_24CYCLES (0x00000050UL) /* 24 ітерації для 24-бітної точності */
#define CORDIC_SCALE_FACTOR_0     (0x00000000UL) /* Масштаб 1:1 */
#define CORDIC_DMA_READ_ENABLE    (0x00000004UL) /* Дозвіл запитів DMA на читання результату */
#define CORDIC_DMA_WRITE_ENABLE   (0x00000008UL) /* Дозвіл запитів DMA на запис аргументу */
#define CORDIC_FLAG_RRDY          (0x80000000UL) /* Прапорець готовності вихідних даних */

/* Ініціалізація співпроцесора для синхронної роботи з ядром */
void cordic_init_synchronous(void) {
    /* Конфігурація: обчислення cos/sin, максимальна точність 24 цикли */
    CORDIC_HW->CSR = CORDIC_FUNC_COS_SIN | CORDIC_PRECISION_24CYCLES | CORDIC_SCALE_FACTOR_0;
}

/* Синхронний розрахунок синуса й косинуса у форматі Q1.31 */
void cordic_calc_sin_cos_q31(int32_t angle_bam, int32_t* out_cos, int32_t* out_sin) {
    /* Запис вхідного кута BAM ініціює апаратні ітерації */
    CORDIC_HW->WDATA = (uint32_t)angle_bam;

    /* Контролер шини призупиняє ядро за допомогою wait states до готовності даних */
    *out_cos = (int32_t)CORDIC_HW->RDATA;
    *out_sin = (int32_t)CORDIC_HW->RDATA;
}

/* Упакований розрахунок у форматі Q1.15 з мінімальними транзакціями шини */
void cordic_calc_sin_cos_packed_q15(int16_t angle_bam_q15, int16_t* out_cos, int16_t* out_sin) {
    /* Запис 16-бітного аргументу в молодші розряди порту WDATA */
    CORDIC_HW->WDATA = (uint32_t)(uint16_t)angle_bam_q15;

    /* Зчитування єдиного 32-бітного слова: cos у молодших 16 бітах, sin у старших */
    uint32_t packed_result = CORDIC_HW->RDATA;
    *out_cos = (int16_t)(packed_result & 0xFFFFU);
    *out_sin = (int16_t)((packed_result >> 16) & 0xFFFFU);
}

/* Конфігурація апаратного блоку для потокової роботи з контролером DMA */
void cordic_configure_dma_stream(void) {
    /* Активація ліній генерації запитів DMA на передачу вхідних та вихідних слів */
    CORDIC_HW->CSR = CORDIC_FUNC_COS_SIN | 
                     CORDIC_PRECISION_24CYCLES | 
                     CORDIC_DMA_READ_ENABLE | 
                     CORDIC_DMA_WRITE_ENABLE;
}
