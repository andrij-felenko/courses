// power_glitch_monitor.c — Апаратний монітор коротких провалів живлення (C99/C11)
#include <stdint.h>
#include <stdbool.h>

// Симуляція регістрів STM32 PWR / EXTI / Backup SRAM
#define PWR_CR_PLS_2V9      (0x07 << 5)  // Поріг PVD = 2.9 В
#define PWR_CR_PVDE         (1 << 4)     // Увімкнення PVD
#define PWR_CSR_PVDO        (1 << 2)     // Прапорець: 1 = напруга нижче порогу

typedef struct {
    uint32_t glitch_count;       // Загальна кількість зафіксованих провалів
    uint32_t brownout_resets;    // Скидання по BOD
    uint32_t last_glitch_stamp;  // Системний час останнього глітчу (мс)
    uint32_t min_voltage_code;   // Код найнижчого зафіксованого порогу
    uint32_t magic_signature;    // Сигнатура валідності структури
} __attribute__((packed)) power_fault_log_t;

// Вказівник на незалежну Backup SRAM (зберігає дані при reset)
#define BACKUP_SRAM_BASE 0x40024000
#define FAULT_LOG ((volatile power_fault_log_t *)BACKUP_SRAM_BASE)
#define LOG_MAGIC 0xA55A1234

static volatile uint32_t g_system_tick_ms = 0;

void power_glitch_monitor_init(void) {
    // 1. Ініціалізація структури діагностики, якщо пам'ять скинута
    if (FAULT_LOG->magic_signature != LOG_MAGIC) {
        FAULT_LOG->glitch_count = 0;
        FAULT_LOG->brownout_resets = 0;
        FAULT_LOG->last_glitch_stamp = 0;
        FAULT_LOG->magic_signature = LOG_MAGIC;
    }

    // 2. Налаштування порогу PVD на 2.9 В та активація детектора
    // PWR->CR = (PWR->CR & ~(0x7 << 5)) | PWR_CR_PLS_2V9 | PWR_CR_PVDE;

    // 3. Конфігурація EXTI Line 16 (PVD Output) на спадний та наростаючий фронти
    // EXTI->IMR  |= (1 << 16);  // Дозволити переривання
    // EXTI->FTSR |= (1 << 16);  // Тригер при падінні нижче 2.9 В
    // EXTI->RTSR |= (1 << 16);  // Тригер при поверненні вище 2.9 В

    // 4. Встановлення найвищого пріоритету переривання PVD у контролері NVIC
    // NVIC_SetPriority(PVD_IRQn, 0);
    // NVIC_EnableIRQ(PVD_IRQn);
}

// Високопріоритетний обробник переривання PVD
void PVD_IRQHandler(void) {
    // 1. Екстрена зупинка потужних споживачів струму (зниження навантаження)
    // TIM1->BDTR &= ~TIM_BDTR_MOE; // Аварійне відключення ШІМ-виходів драйвера мотора
    // RF_TRANSCEIVER_CE_LOW();     // Примусовий перехід радіо у Standby

    // 2. Фіксація факту провалу напруги
    FAULT_LOG->glitch_count++;
    FAULT_LOG->last_glitch_stamp = g_system_tick_ms;

    // 3. Очікування виходу з просадки або фатального скидання BOD
    // Якщо напруга відновлюється за 200 мкс — ядро не скидається і продовжує роботу
    
    // Очищення прапорця EXTI
    // EXTI->PR = (1 << 16);
    
    __asm volatile("dsb 0xF" ::: "memory"); // Бар'єр пам'яті для гарантованого запису
}
