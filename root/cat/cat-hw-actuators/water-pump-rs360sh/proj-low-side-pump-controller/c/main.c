#include <stdio.h>
#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#endif
#include "water_pump.h"

/* Симуляція системного таймера, що збільшується в мілісекундах */
static uint32_t sys_time_ms = 0;

uint32_t GetSystemTimeMs(void) {
    return sys_time_ms;
}

/* Симуляція апаратного встановлення ШІМ (0-100%) */
void HardwareSetPWM(uint8_t duty_cycle) {
    printf("[АПАРАТУРА] ШІМ встановлено: %d%%\n", duty_cycle);
}

/* Допоміжна функція паузи */
void SleepMs(uint32_t ms) {
#ifdef _WIN32
    Sleep(ms);
#else
    usleep(ms * 1000);
#endif
}

int main(void) {
    WaterPump_t my_pump;
    WaterPumpConfig_t pump_config = {
        .soft_start_duration_ms = 1000, /* 1 секунда на розгін */
        .max_run_time_ms = 5000,        /* Максимум 5 секунд безперервної роботи */
        .target_duty_cycle = 80         /* 80% потужності як робочий режим */
    };
    
    /* Ініціалізація драйвера */
    WaterPump_Init(&my_pump, &pump_config, HardwareSetPWM, GetSystemTimeMs);
    
    printf("--- Запуск помпи (Soft-Start) ---\n");
    WaterPump_Start(&my_pump);
    
    /* Головний цикл симуляції */
    for (int i = 0; i < 60; i++) {
        WaterPump_Update(&my_pump);
        
        SleepMs(100);
        sys_time_ms += 100;
        
        /* Вивід стану кожні півсекунди для наочності */
        if (sys_time_ms % 500 == 0) {
            if (my_pump.state == PUMP_STATE_IDLE) {
                printf("Час: %u мс. Стан: Зупинено (Спрацював захист?)\n", sys_time_ms);
                break;
            } else if (my_pump.state == PUMP_STATE_STARTING) {
                printf("Час: %u мс. Стан: Розгін (ШІМ = %d%%)\n", sys_time_ms, my_pump.current_duty);
            } else {
                printf("Час: %u мс. Стан: Робота (ШІМ = %d%%)\n", sys_time_ms, my_pump.current_duty);
            }
        }
    }
    
    return 0;
}
