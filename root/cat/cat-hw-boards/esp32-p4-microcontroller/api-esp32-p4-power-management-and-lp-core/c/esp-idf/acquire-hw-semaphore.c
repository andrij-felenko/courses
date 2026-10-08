#include <stdint.h>
#include <stdbool.h>
#include "esp_attr.h"
#include "hal/hp_sys_clkrst_ll.h"

// Структура спільної пам'яті у пам'яті LP SRAM, доступна обидвом доменам
typedef struct {
    uint32_t sample_counter;
    int16_t  last_temperature_x10;
    uint16_t alarm_threshold_x10;
    uint32_t flags;
} lp_shared_data_t;

// Розміщення структури у спеціальній секції спільної пам'яті LP SRAM
RTC_DATA_ATTR static lp_shared_data_t g_lp_shared_buf;

#define LP_HW_SEMAPHORE_ID 0

// Атомарна спроба захоплення апаратного семафора
static bool acquire_hw_semaphore(uint32_t sem_id)
{
    // Апаратне читання регістру семафора повертає true при успішному захопленні
    return hp_sys_clkrst_ll_hw_semaphore_acquire(sem_id);
}

// Звільнення апаратного семафора
static void release_hw_semaphore(uint32_t sem_id)
{
    hp_sys_clkrst_ll_hw_semaphore_release(sem_id);
}

// Захищений запис даних у спільний буфер пам'яті LP SRAM
void safe_update_sensor_data(int16_t temp_val)
{
    // Очікування звільнення апаратного семафора (spinlock)
    while (!acquire_hw_semaphore(LP_HW_SEMAPHORE_ID)) {
        // У реальних застосуваннях можлива пауза або NOP-інструкція
    }

    // Критична секція: виключний доступ до спільної пам'яті
    g_lp_shared_buf.last_temperature_x10 = temp_val;
    g_lp_shared_buf.sample_counter++;

    // Звільнення апаратного семафора для іншого домену
    release_hw_semaphore(LP_HW_SEMAPHORE_ID);
}
