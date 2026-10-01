#include <stdio.h>
#include <unistd.h>
#include "sir_adc.h"

/* Симуляція низькорівневого зчитування коду АЦП вимірювального стенду */
static uint16_t read_hardware_adc_channel(uint8_t step) {
    /* Симуляція зниження опору ізоляції під впливом вологості та залишків флюсу */
    if (step < 5) {
        return 5;    /* Дуже низька напруга = дуже високий опір (>1000 МОм) */
    } else if (step < 10) {
        return 120;  /* Помірне зниження опору (~150 МОм) */
    } else {
        return 1200; /* Сильний струм витоку = критичне падіння SIR (<10 МОм) */
    }
}

int main(void) {
    SirAdcChannel_t sir_channel;
    
    printf("=== Стенд тестування залишків флюсу FVS-7 (SIR Test Rig) ===\n");
    printf("Ініціалізація високоомного АЦП та параметрів випробування...\n\n");

    sir_adc_init(&sir_channel);

    /* Головний вимірювальний цикл стенду */
    for (uint8_t step = 0; step < 15; step++) {
        uint16_t raw_code = read_hardware_adc_channel(step);
        sir_adc_update_sample(&sir_channel, raw_code);

        printf("[Крок %02d] Код АЦП: %4u | Напруга: %.3f В | Витік: %.2f мкА | Опір SIR: %.1f МОм | Стан: ",
               step + 1, raw_code, sir_channel.measured_voltage,
               sir_channel.leakage_current_ua, sir_channel.sir_resistance_mohm);

        switch (sir_channel.status) {
            case SIR_STATUS_OK:
                printf("НОРМА (Чиста поверхня)\n");
                break;
            case SIR_STATUS_WARNING:
                printf("УВАГА (Допустимий залишок FVS-7)\n");
                break;
            case SIR_STATUS_CRITICAL_LEAKAGE:
                printf("ТРИВОГА! Струм витоку перевищено (Потрібно відмивання)\n");
                break;
            default:
                printf("ПОМИЛКА ОБЛАДНАННЯ\n");
                break;
        }

        if (sir_channel.alarm_active) {
            printf("  --> [СИГНАЛІЗАЦІЯ] Спрацював релейний вихід захисту стенду!\n");
        }

        usleep(100000); /* 100 мс між вимірюваннями */
    }

    printf("\nВипробування завершено успішно.\n");
    return 0;
}
