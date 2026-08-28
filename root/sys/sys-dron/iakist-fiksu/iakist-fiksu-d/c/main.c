#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint8_t  fixType;       // 0=NoFix, 2=2D, 3=3D, 4=DGPS
    uint8_t  flags;         // gnssFixOK (bit 0), diffSoln (bit 1), carrSoln (bits 6..7)
    uint8_t  numSV;         // Кількість супутників у розв'язку
    int32_t  lon;           // 1e-7 deg
    int32_t  lat;           // 1e-7 deg
    int32_t  hMSL;          // Висота над рівнем моря (мм)
    uint32_t hAcc;          // Оцінка горизонтальної точності (мм)
    uint32_t vAcc;          // Оцінка вертикальної точності (мм)
    uint16_t pDOP;          // Просторовій DOP (масштаб 0.01)
} ubx_pvt_short_t;

typedef struct {
    bool  is_healthy;
    bool  is_armable;
    float hdop_est;
    float h_acc_m;
} gnss_health_t;

gnss_health_t evaluate_gnss_health(const ubx_pvt_short_t *pvt) {
    gnss_health_t out = { false, false, 99.9f, 999.0f };

    bool fix_ok = (pvt->flags & 0x01) != 0;
    out.h_acc_m = (float)pvt->hAcc * 0.001f;
    float pdop = (float)pvt->pDOP * 0.01f;
    out.hdop_est = pdop * 0.65f; // Наближена оцінка HDOP з PDOP

    // Базові критерії валідності розв'язку
    if (fix_ok && pvt->fixType >= 3 && pvt->numSV >= 6) {
        out.is_healthy = true;
    }

    // Суворі критерії безпеки для дозволу зльоту (Arming Checks)
    if (out.is_healthy && pvt->numSV >= 8 && pdop <= 2.5f && out.h_acc_m <= 2.0f) {
        out.is_armable = true;
    }

    return out;
}
