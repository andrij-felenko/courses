#include <stdint.h>
#include <stdbool.h>

// Перелік системних статусно-діагностичних кодів IronOS
typedef enum {
    DIAG_STATUS_OK = 0,
    DIAG_STATUS_LOW_VOLTAGE,
    DIAG_STATUS_PD_NEGOTIATION_FAIL,
    DIAG_STATUS_TIP_DISCONNECTED,
    DIAG_STATUS_THERMAL_RUNAWAY
} diag_status_t;

typedef struct {
    uint16_t vin_mv;          // Поточна вхідна напруга в мілівольтах
    uint16_t v_cutoff_mv;     // Поріг відсічки живлення в мілівольтах
    int16_t tip_temp_c;       // Зчитана температура жала в °C
    bool pd_negotiated;       // Прапор успішного узгодження USB-PD
    bool sensor_valid;        // Прапор справності термопари
} system_metrics_t;

// Функція діагностичної оцінки стану смарт-паяльника
diag_status_t evaluate_system_diagnostics(const system_metrics_t* metrics) {
    if (!metrics->sensor_valid || metrics->tip_temp_c < -20 || metrics->tip_temp_c > 500) {
        return DIAG_STATUS_TIP_DISCONNECTED;
    }
    
    if (metrics->vin_mv < metrics->v_cutoff_mv) {
        return DIAG_STATUS_LOW_VOLTAGE;
    }
    
    if (!metrics->pd_negotiated && metrics->vin_mv < 9000) {
        return DIAG_STATUS_PD_NEGOTIATION_FAIL;
    }
    
    return DIAG_STATUS_OK;
}
