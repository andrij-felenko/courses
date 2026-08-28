#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define UBX_SYNC1 0xB5
#define UBX_SYNC2 0x62
#define UBX_CLASS_NAV 0x01
#define UBX_ID_NAV_PVT 0x07
#define UBX_NAV_PVT_PAYLOAD_LEN 92

typedef enum {
    UBX_STATE_SYNC1 = 0,
    UBX_STATE_SYNC2,
    UBX_STATE_CLASS,
    UBX_STATE_ID,
    UBX_STATE_LEN1,
    UBX_STATE_LEN2,
    UBX_STATE_PAYLOAD,
    UBX_STATE_CK_A,
    UBX_STATE_CK_B
} ubx_parser_state_t;

typedef enum {
    GNSS_QUALITY_REJECTED = 0,
    GNSS_QUALITY_POOR,
    GNSS_QUALITY_ACCEPTABLE,
    GNSS_QUALITY_EXCELLENT
} gnss_quality_level_t;

#pragma pack(push, 1)
typedef struct {
    uint32_t iTOW;          // Час тижня GPS (мс)
    uint16_t year;          // Рік (UTC)
    uint8_t  month;         // Місяць (1..12)
    uint8_t  day;           // День (1..31)
    uint8_t  hour;          // Година (0..23)
    uint8_t  min;           // Хвилина (0..59)
    uint8_t  sec;           // Секунда (0..60)
    uint8_t  valid;         // Прапорці валідності часу
    uint32_t tAcc;          // Точність часу (нс)
    int32_t  nano;          // Дріб секунди (нс)
    uint8_t  fixType;       // Тип фіксу: 0=NoFix, 2=2D, 3=3D, 4=DGPS, 5=TimeOnly
    uint8_t  flags;         // Прапорці фіксу (gnssFixOK, diffSoln, carrSoln)
    uint8_t  flags2;        // Додаткові прапорці
    uint8_t  numSV;         // Кількість супутників, використаних у розв'язку
    int32_t  lon;           // Довгота (1e-7 град)
    int32_t  lat;           // Широта (1e-7 град)
    int32_t  height;        // Висота над еліпсоїдом WGS84 (мм)
    int32_t  hMSL;          // Висота над середнім рівнем моря MSL (мм)
    uint32_t hAcc;          // Оцінка горизонтальної точності (мм)
    uint32_t vAcc;          // Оцінка вертикальної точності (мм)
    int32_t  velN;          // Швидкість на Північ (мм/с)
    int32_t  velE;          // Швидкість на Схід (мм/с)
    int32_t  velD;          // Швидкість Вниз (мм/с)
    int32_t  gSpeed;        // Горизонтальна швидкість (мм/с)
    int32_t  headMot;       // Курс руху (1e-5 град)
    uint32_t sAcc;          // Точність швидкості (мм/с)
    uint32_t headAcc;       // Точність курсу (1e-5 град)
    uint16_t pDOP;          // Просторовій DOP (масштаб 0.01)
    uint16_t flags3;        // Прапорці валідності розв'язку
    uint8_t  reserved1[4];
    int32_t  headVeh;       // Курс корпусу (для 2-антенних систем)
    int16_t  magDec;        // Магнітне схилення
    uint16_t magAcc;        // Точність магнітного схилення
} ubx_nav_pvt_payload_t;
#pragma pack(pop)

typedef struct {
    ubx_parser_state_t state;
    uint8_t msg_class;
    uint8_t msg_id;
    uint16_t payload_len;
    uint16_t payload_idx;
    uint8_t ck_a;
    uint8_t ck_b;
    uint8_t calc_ck_a;
    uint8_t calc_ck_b;
    uint8_t payload_buf[UBX_NAV_PVT_PAYLOAD_LEN];
} ubx_parser_ctx_t;

typedef struct {
    gnss_quality_level_t quality;
    bool is_valid_3d_fix;
    bool is_rtk_fixed;
    float pdop;
    float h_acc_meters;
    float v_acc_meters;
    uint8_t satellites_used;
    bool arming_allowed;
} gnss_eval_report_t;

void ubx_parser_init(ubx_parser_ctx_t *ctx) {
    memset(ctx, 0, sizeof(ubx_parser_ctx_t));
    ctx->state = UBX_STATE_SYNC1;
}

static void ubx_update_checksum(ubx_parser_ctx_t *ctx, uint8_t byte) {
    ctx->calc_ck_a += byte;
    ctx->calc_ck_b += ctx->calc_ck_a;
}

bool ubx_parser_feed_byte(ubx_parser_ctx_t *ctx, uint8_t byte, ubx_nav_pvt_payload_t *out_pvt) {
    switch (ctx->state) {
    case UBX_STATE_SYNC1:
        if (byte == UBX_SYNC1) {
            ctx->state = UBX_STATE_SYNC2;
        }
        break;
    case UBX_STATE_SYNC2:
        if (byte == UBX_SYNC2) {
            ctx->state = UBX_STATE_CLASS;
            ctx->calc_ck_a = 0;
            ctx->calc_ck_b = 0;
        } else {
            ctx->state = (byte == UBX_SYNC1) ? UBX_STATE_SYNC2 : UBX_STATE_SYNC1;
        }
        break;
    case UBX_STATE_CLASS:
        ctx->msg_class = byte;
        ubx_update_checksum(ctx, byte);
        ctx->state = UBX_STATE_ID;
        break;
    case UBX_STATE_ID:
        ctx->msg_id = byte;
        ubx_update_checksum(ctx, byte);
        ctx->state = UBX_STATE_LEN1;
        break;
    case UBX_STATE_LEN1:
        ctx->payload_len = byte;
        ubx_update_checksum(ctx, byte);
        ctx->state = UBX_STATE_LEN2;
        break;
    case UBX_STATE_LEN2:
        ctx->payload_len |= ((uint16_t)byte << 8);
        ubx_update_checksum(ctx, byte);
        ctx->payload_idx = 0;
        if (ctx->payload_len == UBX_NAV_PVT_PAYLOAD_LEN &&
            ctx->msg_class == UBX_CLASS_NAV &&
            ctx->msg_id == UBX_ID_NAV_PVT) {
            ctx->state = UBX_STATE_PAYLOAD;
        } else {
            ctx->state = UBX_STATE_SYNC1;
        }
        break;
    case UBX_STATE_PAYLOAD:
        ctx->payload_buf[ctx->payload_idx++] = byte;
        ubx_update_checksum(ctx, byte);
        if (ctx->payload_idx >= ctx->payload_len) {
            ctx->state = UBX_STATE_CK_A;
        }
        break;
    case UBX_STATE_CK_A:
        ctx->ck_a = byte;
        ctx->state = UBX_STATE_CK_B;
        break;
    case UBX_STATE_CK_B:
        ctx->ck_b = byte;
        ctx->state = UBX_STATE_SYNC1;
        if (ctx->ck_a == ctx->calc_ck_a && ctx->ck_b == ctx->calc_ck_b) {
            memcpy(out_pvt, ctx->payload_buf, sizeof(ubx_nav_pvt_payload_t));
            return true;
        }
        break;
    }
    return false;
}

gnss_eval_report_t gnss_evaluate_pvt_quality(const ubx_nav_pvt_payload_t *pvt) {
    gnss_eval_report_t rep;
    memset(&rep, 0, sizeof(rep));

    rep.satellites_used = pvt->numSV;
    rep.pdop = (float)pvt->pDOP * 0.01f;
    rep.h_acc_meters = (float)pvt->hAcc * 0.001f;
    rep.v_acc_meters = (float)pvt->vAcc * 0.001f;

    bool gnss_fix_ok = (pvt->flags & 0x01) != 0;
    uint8_t carr_soln = (pvt->flags >> 6) & 0x03; // 0=None, 1=Float, 2=Fixed

    rep.is_valid_3d_fix = gnss_fix_ok && (pvt->fixType >= 3);
    rep.is_rtk_fixed = (carr_soln == 2);

    if (!rep.is_valid_3d_fix || rep.satellites_used < 6 || rep.pdop > 5.0f || rep.h_acc_meters > 5.0f) {
        rep.quality = GNSS_QUALITY_REJECTED;
        rep.arming_allowed = false;
    } else if (rep.pdop > 2.5f || rep.h_acc_meters > 2.5f || rep.satellites_used < 8) {
        rep.quality = GNSS_QUALITY_POOR;
        rep.arming_allowed = false;
    } else if (rep.pdop > 1.8f || rep.h_acc_meters > 1.2f) {
        rep.quality = GNSS_QUALITY_ACCEPTABLE;
        rep.arming_allowed = true;
    } else {
        rep.quality = GNSS_QUALITY_EXCELLENT;
        rep.arming_allowed = true;
    }

    return rep;
}
