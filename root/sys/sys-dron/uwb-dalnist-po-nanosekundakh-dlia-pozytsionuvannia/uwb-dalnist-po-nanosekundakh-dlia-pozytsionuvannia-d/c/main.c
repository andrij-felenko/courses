#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    uint16_t anchor_id;
    float    distance_m;
    float    variance_m2;
    bool     valid;
} uwb_range_measurement_t;

/* Обробка сирого вимірювання та динамічне масштабування коваріації шуму */
uwb_range_measurement_t process_uwb_range(uint16_t anchor_id, float raw_dist_m,
                                          float fpp_dbm, float rxp_dbm) {
    uwb_range_measurement_t meas = {
        .anchor_id = anchor_id,
        .distance_m = raw_dist_m,
        .variance_m2 = 0.0025f, /* Базова дисперсія LOS: (5 см)^2 */
        .valid = false
    };

    /* Базова перевірка фізичних меж приміщення */
    if (raw_dist_m < 0.1f || raw_dist_m > 80.0f) {
        return meas;
    }

    float nlos_diff = rxp_dbm - fpp_dbm;

    if (nlos_diff > 10.0f) {
        /* Hard NLOS: сигнал заблоковано, відкидаємо замір */
        meas.valid = false;
        return meas;
    } else if (nlos_diff > 6.0f) {
        /* Soft NLOS: сигнал ослаблено, збільшуємо дисперсію для EKF у 16 разів */
        meas.variance_m2 = 0.0400f; /* (20 см)^2 */
        meas.valid = true;
    } else {
        /* Чистий LOS */
        meas.variance_m2 = 0.0025f;
        meas.valid = true;
    }

    return meas;
}
