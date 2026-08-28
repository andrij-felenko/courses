#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define COLOR_SENSOR_I2C_ADDR   0x29

/* Карта регістрів типового RGBC сенсора (TCS34725 / сумісні) */
#define REG_ENABLE              0x00
#define REG_ATIME               0x01
#define REG_CONTROL             0x0F
#define REG_CDATAL              0x14
#define REG_RDATAL              0x16
#define REG_GDATAL              0x18
#define REG_BDATAL              0x1A

#define ENABLE_PON              0x01  /* Вмикання внутрішнього генератора */
#define ENABLE_AEN              0x02  /* Запуск циклічного вимірювання RGBC */

/* Таблиця підсилення */
typedef enum {
    GAIN_1X  = 0x00,
    GAIN_4X  = 0x01,
    GAIN_16X = 0x02,
    GAIN_60X = 0x03
} color_gain_t;

/* Сирі відліки з АЦП */
typedef struct {
    uint16_t r;
    uint16_t g;
    uint16_t b;
    uint16_t c;
} rgbc_raw_t;

/* Фінальний колориметричний результат */
typedef struct {
    float x;             /* Координата колірності CIE 1931 x */
    float y;             /* Координата колірності CIE 1931 y */
    float lux;           /* Фотометрична освітленість у Люксах */
    float cct_kelvin;    /* Корельована колірна температура CCT (K) */
    uint8_t srgb_r;      /* 8-бітний колір sRGB [0..255] */
    uint8_t srgb_g;
    uint8_t srgb_b;
    bool is_saturated;   /* Прапорець переповнення каналу */
} color_measurement_t;

/* Розрахунок CCT за МакКамі */
static float calculate_cct_mccamy(float x, float y) {
    float denom = 0.1858f - y;
    if (fabsf(denom) < 1e-5f) return 0.0f;
    float n = (x - 0.3320f) / denom;
    float n2 = n * n;
    float n3 = n2 * n;
    return 449.0f * n3 + 3525.0f * n2 + 6823.3f * n + 5520.33f;
}

/* Гамма-корекція для колірного простору sRGB */
static uint8_t linear_to_srgb_8bit(float linear_val) {
    if (linear_val <= 0.0f) return 0;
    if (linear_val >= 1.0f) return 255;
    float srgb = (linear_val <= 0.0031308f) 
               ? (12.92f * linear_val) 
               : (1.055f * powf(linear_val, 1.0f / 2.4f) - 0.055f);
    int32_t val_int = (int32_t)(srgb * 255.0f + 0.5f);
    if (val_int > 255) return 255;
    if (val_int < 0) return 0;
    return (uint8_t)val_int;
}

/* Головна функція колориметричного перетворення */
void color_sensor_process(const rgbc_raw_t *raw, 
                          float atime_ms, 
                          float gain_val, 
                          color_measurement_t *out) 
{
    /* Перевірка насичення АЦП (16-біт макс) */
    out->is_saturated = (raw->c >= 65530 || raw->r >= 65530 || 
                         raw->g >= 65530 || raw->b >= 65530);

    /* 1. Нормування сирих відліків на час інтеграції та підсилення */
    float norm_factor = (atime_ms * gain_val > 0.0f) ? (1.0f / (atime_ms * gain_val)) : 1.0f;
    float rn = (float)raw->r * norm_factor;
    float gn = (float)raw->g * norm_factor;
    float bn = (float)raw->b * norm_factor;

    /* 2. Матриця колірної корекції (CCM 3x3: RGBC -> CIE 1931 XYZ) */
    const float ccm[3][3] = {
        {  0.0829f,  0.1983f, -0.0381f },
        {  0.0321f,  0.2452f, -0.0210f },
        { -0.0512f, -0.0821f,  0.3891f }
    };

    float X = ccm[0][0] * rn + ccm[0][1] * gn + ccm[0][2] * bn;
    float Y = ccm[1][0] * rn + ccm[1][1] * gn + ccm[1][2] * bn;
    float Z = ccm[2][0] * rn + ccm[2][1] * gn + ccm[2][2] * bn;

    if (X < 0.0f) X = 0.0f;
    if (Y < 0.0f) Y = 0.0f;
    if (Z < 0.0f) Z = 0.0f;

    /* 3. Координати колірності x, y */
    float sum_xyz = X + Y + Z;
    if (sum_xyz > 1e-4f) {
        out->x = X / sum_xyz;
        out->y = Y / sum_xyz;
    } else {
        out->x = 0.3127f; /* Точка білого D65 за замовчуванням */
        out->y = 0.3290f;
    }

    /* 4. Освітленість у Люксах та CCT */
    out->lux = 683.0f * Y;
    out->cct_kelvin = calculate_cct_mccamy(out->x, out->y);

    /* 5. Перетворення у простір sRGB (D65) */
    float r_lin =  3.2404542f * X - 1.5371385f * Y - 0.4985314f * Z;
    float g_lin = -0.9692660f * X + 1.8760108f * Y + 0.0415560f * Z;
    float b_lin =  0.0556434f * X - 0.2040259f * Y + 1.0572252f * Z;

    /* Масштабування відносно максимального каналу для збереження хроматичності */
    float max_ch = fmaxf(r_lin, fmaxf(g_lin, b_lin));
    if (max_ch > 1e-4f) {
        r_lin /= max_ch;
        g_lin /= max_ch;
        b_lin /= max_ch;
    }

    out->srgb_r = linear_to_srgb_8bit(r_lin);
    out->srgb_g = linear_to_srgb_8bit(g_lin);
    out->srgb_b = linear_to_srgb_8bit(b_lin);
}
