#include <stdint.h>
#include <stdbool.h>
#include "chopper.h"

// Заглушки апаратних регістрів (спрощено)
#define REG_ADC_RESULT  (*(volatile uint32_t*)0x40012440)
#define REG_TIMER_STAT  (*(volatile uint32_t*)0x40000000)
#define REG_SENSOR_CTRL (*(volatile uint32_t*)0x40020000)

static MovingAverage hall_ma;
static FirFilter hall_fir;

static void Hardware_Init(void) {
    // Налаштування АЦП та таймерів
}

static void SetSensorPhase(uint8_t phase) {
    REG_SENSOR_CTRL = (phase == 0) ? 0x01 : 0x02;
}

static void DelayUs(void) {
    for (volatile int i = 0; i < 150; i++) {} // Час на перехідні процеси
}

int main(void) {
    Hardware_Init();
    Chopper_Init(&hall_ma, &hall_fir);
    
    while (1) {
        if (REG_TIMER_STAT & 0x01) {
            REG_TIMER_STAT &= ~0x01;
            
            // Вимірювання Фази 0
            SetSensorPhase(0);
            DelayUs();
            int32_t phase0_data = REG_ADC_RESULT;
            
            // Вимірювання Фази 1
            SetSensorPhase(1);
            DelayUs();
            int32_t phase1_data = REG_ADC_RESULT;
            
            // Цифрова обробка та стабілізація
            int32_t hall_field = Chopper_Process(phase0_data, phase1_data, &hall_ma, &hall_fir);
            
            // Виявлення близькості магніту за порогом
            bool is_magnet_near = (hall_field > 1000) || (hall_field < -1000);
            if (is_magnet_near) {
                // Дії при спрацьовуванні
            }
        }
    }
    return 0;
}
