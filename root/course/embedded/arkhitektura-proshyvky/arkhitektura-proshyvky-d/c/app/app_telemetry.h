/* app/app_telemetry.h — накопичення вимірів у запис телеметрії.
 * Вікно закривається за часом, а не за кількістю зразків: пропущений через
 * аварію шини вимір не має зсувати розклад передавання. */
#ifndef APP_TELEMETRY_H
#define APP_TELEMETRY_H

#include "include/telemetry_record.h"

#include <stdbool.h>

typedef struct {
    uint32_t window_ms;
    uint32_t window_start_ms;
    uint32_t sample_count;
    uint32_t fault_count;

    float temp_sum_c;
    float temp_min_c;
    float temp_max_c;
    float humidity_sum_rh;
    float pressure_sum_hpa;
    float vibration_sq_sum;  /* сума квадратів для середньоквадратичного */
    float vibration_peak_g;
} app_telemetry_t;

void app_telemetry_init(app_telemetry_t *t, uint32_t window_ms, uint32_t now_ms);

void app_telemetry_add_sample(app_telemetry_t *t, uint32_t now_ms,
                              float temp_c, float humidity_rh,
                              float pressure_hpa, float vibration_g);

/* Невдале опитування давача теж потрапляє в запис: інакше телеметрія
 * виглядатиме бездоганною саме тоді, коли пристрій наполовину сліпий. */
void app_telemetry_add_fault(app_telemetry_t *t);

bool app_telemetry_window_elapsed(const app_telemetry_t *t, uint32_t now_ms);

/* Складає запис і починає нове вікно. false — за вікно не було жодного
 * успішного виміру, тож усереднювати нема чого. */
bool app_telemetry_close_window(app_telemetry_t *t, uint32_t now_ms,
                                telemetry_record_t *out_record);

#endif /* APP_TELEMETRY_H */
