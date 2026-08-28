// depassivation_driver.c — Драйвер депасивації та контролю батареї (C99)
#include <stdint.h>
#include <stdbool.h>

#define DEPASS_RESISTOR_MOHM    100000UL  // Баластний резистор 100 Ом (100000 мОм)
#define DEPASS_PULSE_MS         50U       // Тривалість імпульсу депасивації (мс)
#define DEPASS_MAX_ATTEMPTS     10U       // Максимальна кількість спроб розминки
#define BATTERY_SAFE_MV         3000U     // Безпечний поріг для старту радіо (3.0 В)
#define BATTERY_CRITICAL_MV     2400U     // Критичний поріг просідання під тестом (2.4 В)

typedef enum {
    BATTERY_STATUS_READY = 0,
    BATTERY_STATUS_DEPASSIVATED,
    BATTERY_STATUS_LOW_BATTERY,
    BATTERY_STATUS_FAULT
} battery_status_t;

typedef struct {
    uint32_t (*read_voltage_mv)(void);
    void (*set_load_switch)(bool enable);
    void (*delay_ms)(uint32_t ms);
} battery_hal_t;

typedef struct {
    uint32_t v_ocv_mv;
    uint32_t v_load_mv;
    uint32_t r_int_mohm;
    uint8_t depass_cycles_done;
    battery_status_t status;
} battery_diag_t;

battery_status_t battery_prepare_for_tx(const battery_hal_t *hal, battery_diag_t *diag) {
    if (!hal || !hal->read_voltage_mv || !hal->set_load_switch || !hal->delay_ms || !diag) {
        return BATTERY_STATUS_FAULT;
    }

    diag->depass_cycles_done = 0;
    
    // 1. Вимірювання напруги холостого ходу (Open Circuit Voltage)
    hal->set_load_switch(false);
    hal->delay_ms(5);
    diag->v_ocv_mv = hal->read_voltage_mv();

    if (diag->v_ocv_mv < BATTERY_SAFE_MV) {
        diag->status = BATTERY_STATUS_LOW_BATTERY;
        return BATTERY_STATUS_LOW_BATTERY;
    }

    // 2. Тестовий імпульс навантаження та адаптивна депасивація
    for (uint8_t attempt = 0; attempt < DEPASS_MAX_ATTEMPTS; ++attempt) {
        hal->set_load_switch(true);
        hal->delay_ms(15); // Час на встановлення перехідного процесу
        diag->v_load_mv = hal->read_voltage_mv();
        
        // Якщо напруга під баластом вище безпечного порогу — депасивація завершена
        if (diag->v_load_mv >= BATTERY_SAFE_MV) {
            hal->set_load_switch(false);
            
            // Розрахунок R_int: R_int = (V_ocv - V_load) / (V_load / R_load)
            uint32_t delta_v = diag->v_ocv_mv - diag->v_load_mv;
            diag->r_int_mohm = (uint32_t)(((uint64_t)delta_v * DEPASS_RESISTOR_MOHM) / diag->v_load_mv);
            
            diag->status = (attempt == 0) ? BATTERY_STATUS_READY : BATTERY_STATUS_DEPASSIVATED;
            return diag->status;
        }

        // Продовжуємо імпульс депасивації під струмом
        hal->delay_ms(DEPASS_PULSE_MS);
        hal->set_load_switch(false);
        diag->depass_cycles_done++;
        
        // Пауза між імпульсами для дифузійного релаксування електроліту
        hal->delay_ms(25);
    }

    // Якщо після максимальної кількості спроб напруга не піднялась
    diag->status = (diag->v_load_mv < BATTERY_CRITICAL_MV) ? BATTERY_STATUS_LOW_BATTERY : BATTERY_STATUS_FAULT;
    return diag->status;
}
