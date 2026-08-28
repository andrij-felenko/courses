/* cjc_thermocouple_k.h / .c */
#include <stdbool.h>
#include <math.h>

typedef struct {
    float temperature_c;
    bool is_valid;
} cjc_result_t;

/* Пряме перетворення NIST ITS-90: T (°C) -> E (мВ) для опорного спаю */
float nist_type_k_temp_to_mv(float temp_c) {
    if (temp_c < 0.0f) {
        /* Піддіапазон -200 °C ... 0 °C */
        const float c[] = {
            0.0f, 3.945013e-2f, 2.362237e-5f, -3.285891e-7f,
            -4.990483e-9f, -6.750906e-11f, -5.741032e-13f, -3.108894e-15f,
            -1.045161e-17f, -1.988927e-20f
        };
        float mv = c[9];
        for (int i = 8; i >= 0; --i) {
            mv = mv * temp_c + c[i];
        }
        return mv;
    } else {
        /* Піддіапазон 0 °C ... 1372 °C */
        const float c[] = {
            -1.7600413686e-2f, 3.8921204975e-2f, 1.8558770032e-5f,
            -9.9457592874e-8f, 3.1840945719e-10f, -5.6072844889e-13f,
            5.6075059059e-16f, -3.2020720003e-19f, 9.7151147152e-23f,
            -1.2104721275e-26f
        };
        float mv = c[9];
        for (int i = 8; i >= 0; --i) {
            mv = mv * temp_c + c[i];
        }
        /* Експоненційна корекція сплаву нікелю */
        const float a0 = 0.1185976f;
        const float a1 = -1.183432e-4f;
        const float a2 = 126.9686f;
        float diff = temp_c - a2;
        mv += a0 * expf(a1 * diff * diff);
        return mv;
    }
}

/* Зворотне перетворення NIST ITS-90: E_total (мВ) -> T_hot (°C) */
float nist_type_k_mv_to_temp(float mv) {
    if (mv < 0.0f) {
        /* Діапазон -200 °C ... 0 °C (-5.891 мВ ... 0 мВ) */
        const float d[] = {
            0.0f, 2.5173462e1f, -1.1662878f, -1.0833638f,
            -8.9773540e-1f, -3.7342377e-1f, -8.6632643e-2f, -1.0450598e-2f,
            -5.1920577e-4f
        };
        float t = d[8];
        for (int i = 7; i >= 0; --i) {
            t = t * mv + d[i];
        }
        return t;
    } else if (mv <= 20.644f) {
        /* Діапазон 0 °C ... 500 °C (0 мВ ... 20.644 мВ) */
        const float d[] = {
            0.0f, 2.508355e1f, 7.860106e-2f, -2.503131e-1f,
            8.315270e-2f, -1.228034e-2f, 9.804036e-4f, -4.413030e-5f,
            1.057734e-6f, -1.052755e-8f
        };
        float t = d[9];
        for (int i = 8; i >= 0; --i) {
            t = t * mv + d[i];
        }
        return t;
    } else {
        /* Діапазон 500 °C ... 1372 °C (20.644 мВ ... 54.886 мВ) */
        const float d[] = {
            -1.318058e2f, 4.830222e1f, -1.646031f, 5.464731e-2f,
            -9.650715e-4f, 8.802193e-6f, -3.110810e-8f
        };
        float t = d[6];
        for (int i = 5; i >= 0; --i) {
            t = t * mv + d[i];
        }
        return t;
    }
}

/* Повний конвеєр цифрової компенсації холодного спаю */
cjc_result_t thermocouple_k_calculate(float v_meas_mv, float t_cjc_c) {
    cjc_result_t res = {0.0f, false};

    /* Перевірка допустимого діапазону температури плати (-40...+125 °C) */
    if (t_cjc_c < -40.0f || t_cjc_c > 125.0f) {
        return res;
    }

    /* Крок 1 і 2: Розрахунок ЕРС опорного спаю за ITS-90 */
    float v_cjc_mv = nist_type_k_temp_to_mv(t_cjc_c);

    /* Крок 3: Складання потенціалів */
    float v_total_mv = v_meas_mv + v_cjc_mv;

    /* Перевірка виходу за межі шкали типу K (-5.891 мВ ... 54.886 мВ) */
    if (v_total_mv < -5.891f || v_total_mv > 54.886f) {
        return res;
    }

    /* Крок 4: Зворотне перетворення сумарної ЕРС у T_hot */
    res.temperature_c = nist_type_k_mv_to_temp(v_total_mv);
    res.is_valid = true;
    return res;
}
