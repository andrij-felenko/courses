#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define UBX_SYNC1 0xB5
#define UBX_SYNC2 0x62

#define UBX_CLASS_NAV 0x01
#define UBX_ID_NAV_PVT 0x07

#define UBX_CLASS_CFG 0x06
#define UBX_ID_CFG_VALSET 0x8A

#define UBX_LAYER_RAM   0x01
#define UBX_LAYER_BBR   0x02
#define UBX_LAYER_FLASH 0x04

/* Ключі конфігурації u-blox Generation 9 (Configuration Key IDs) */
#define CFG_SIGNAL_GPS_ENA      0x1031001F  /* L1C/A */
#define CFG_SIGNAL_GPS_L5_ENA   0x10310022  /* L5 */
#define CFG_SIGNAL_GAL_ENA      0x10310021  /* E1 */
#define CFG_SIGNAL_GAL_E5A_ENA  0x10310027  /* E5a */
#define CFG_SIGNAL_BDS_ENA      0x10310024  /* B1I / B1C */
#define CFG_SIGNAL_BDS_B2A_ENA  0x10310029  /* B2a */
#define CFG_SIGNAL_GLO_ENA      0x10310023  /* G1 */
#define CFG_NAVSPG_DYNMODEL     0x20110021  /* Динамічна модель польоту */
#define CFG_RATE_MEAS           0x30210001  /* Період вимірювань у мс (100 мс = 10 Гц) */
#define CFG_RATE_NAV            0x30210002  /* Навігаційний дільник */

/* Динамічні моделі польотного контролера */
typedef enum {
    DYNMODEL_PORTABLE   = 0,
    DYNMODEL_STATIONARY = 2,
    DYNMODEL_PEDESTRIAN = 3,
    DYNMODEL_AUTOMOTIVE = 4,
    DYNMODEL_AIRBORNE_1G = 6,
    DYNMODEL_AIRBORNE_2G = 7,
    DYNMODEL_AIRBORNE_4G = 8
} ubx_dynmodel_t;

/* Структура навігаційного повідомлення UBX-NAV-PVT (92 байти) */
#pragma pack(push, 1)
typedef struct {
    uint32_t iTOW;          /* Час навігаційного тижня GPS (мс) */
    uint16_t year;          /* Рік (UTC) */
    uint8_t  month;         /* Місяць 1..12 */
    uint8_t  day;           /* День 1..31 */
    uint8_t  hour;          /* Година 0..23 */
    uint8_t  min;           /* Хвилина 0..59 */
    uint8_t  sec;           /* Секунда 0..60 */
    uint8_t  valid;         /* Прапорці валідності часу */
    uint32_t tAcc;          /* Точність часу (нс) */
    int32_t  nano;          /* Дробова частина секунди (нс) */
    uint8_t  fixType;       /* 0=NoFix, 2=2D, 3=3D, 4=GNSS+DR, 5=TimeOnly */
    uint8_t  flags;         /* Прапорці навігаційного фіксу */
    uint8_t  flags2;        /* Додаткові прапорці інформації */
    uint8_t  numSV;         /* Кількість супутників у розв'язку */
    int32_t  lon;           /* Довгота (1e-7 градуса) */
    int32_t  lat;           /* Широта (1e-7 градуса) */
    int32_t  height;        /* Висота над еліпсоїдом WGS-84 (мм) */
    int32_t  hMSL;          /* Висота над середнім рівнем моря (мм) */
    uint32_t hAcc;          /* Горизонтальна точність (мм) */
    uint32_t vAcc;          /* Вертикальна точність (мм) */
    int32_t  velN;          /* Північна швидкість NED (мм/с) */
    int32_t  velE;          /* Східна швидкість NED (мм/с) */
    int32_t  velD;          /* Вертикальна швидкість NED (мм/с) */
    int32_t  gSpeed;        /* Горизонтальна шляхова швидкість (мм/с) */
    int32_t  headMot;       /* Курс руху (1e-5 градуса) */
    uint32_t sAcc;          /* Точність оцінки швидкості (мм/с) */
    uint32_t headAcc;       /* Точність оцінки курсу (1e-5 градуса) */
    uint16_t pDOP;          /* Geometric DOP (масштаб 0.01) */
    uint8_t  flags3;        /* Прапорці RTK та додаткові дані */
    uint8_t  reserved1[5];
    int32_t  headVeh;       /* Курс корпусу апарата */
    int16_t  magDec;        /* Магнітне схилення */
    uint16_t magAcc;        /* Точність магнітного схилення */
} ubx_nav_pvt_t;
#pragma pack(pop)

/* 8-бітний алгоритм контрольної суми Флетчера (UBX Checksum) */
void ubx_checksum(const uint8_t *data, uint16_t len, uint8_t *ck_a, uint8_t *ck_b) {
    uint8_t a = 0;
    uint8_t b = 0;
    for (uint16_t i = 0; i < len; ++i) {
        a = (uint8_t)(a + data[i]);
        b = (uint8_t)(b + a);
    }
    *ck_a = a;
    *ck_b = b;
}

/* Формування пакету UBX-CFG-VALSET для багатосистемної конфігурації */
uint16_t ubx_build_multiband_cfg(uint8_t *out_buf, uint16_t max_len) {
    uint8_t payload[128];
    uint16_t p_idx = 0;

    payload[p_idx++] = 0x00; /* Version */
    payload[p_idx++] = UBX_LAYER_RAM | UBX_LAYER_BBR; /* Збереження в RAM + BBR */
    payload[p_idx++] = 0x00; /* Reserved */
    payload[p_idx++] = 0x00; /* Reserved */

    /* Додавання пар Key-Value (1 байт = U1 / L) */
    #define ADD_CFG_U8(key, val) do { \
        uint32_t k = (key); \
        memcpy(&payload[p_idx], &k, 4); p_idx += 4; \
        payload[p_idx++] = (uint8_t)(val); \
    } while(0)

    #define ADD_CFG_U16(key, val) do { \
        uint32_t k = (key); uint16_t v = (val); \
        memcpy(&payload[p_idx], &k, 4); p_idx += 4; \
        memcpy(&payload[p_idx], &v, 2); p_idx += 2; \
    } while(0)

    /* Активація сузір'їв та частотних діапазонів L1 + L5 */
    ADD_CFG_U8(CFG_SIGNAL_GPS_ENA, 1);
    ADD_CFG_U8(CFG_SIGNAL_GPS_L5_ENA, 1);
    ADD_CFG_U8(CFG_SIGNAL_GAL_ENA, 1);
    ADD_CFG_U8(CFG_SIGNAL_GAL_E5A_ENA, 1);
    ADD_CFG_U8(CFG_SIGNAL_BDS_ENA, 1);
    ADD_CFG_U8(CFG_SIGNAL_BDS_B2A_ENA, 1);
    ADD_CFG_U8(CFG_SIGNAL_GLO_ENA, 1);

    /* Авіаційна динаміка (Airborne < 4g) та навігаційний темп 10 Гц (100 мс) */
    ADD_CFG_U8(CFG_NAVSPG_DYNMODEL, DYNMODEL_AIRBORNE_4G);
    ADD_CFG_U16(CFG_RATE_MEAS, 100);
    ADD_CFG_U16(CFG_RATE_NAV, 1);

    #undef ADD_CFG_U8
    #undef ADD_CFG_U16

    /* Формування повного UBX фрейму */
    uint16_t total_len = 6 + p_idx + 2;
    if (total_len > max_len) return 0;

    out_buf[0] = UBX_SYNC1;
    out_buf[1] = UBX_SYNC2;
    out_buf[2] = UBX_CLASS_CFG;
    out_buf[3] = UBX_ID_CFG_VALSET;
    out_buf[4] = (uint8_t)(p_idx & 0xFF);
    out_buf[5] = (uint8_t)((p_idx >> 8) & 0xFF);

    memcpy(&out_buf[6], payload, p_idx);

    uint8_t ck_a, ck_b;
    ubx_checksum(&out_buf[2], (uint16_t)(4 + p_idx), &ck_a, &ck_b);
    out_buf[6 + p_idx] = ck_a;
    out_buf[7 + p_idx] = ck_b;

    return total_len;
}
