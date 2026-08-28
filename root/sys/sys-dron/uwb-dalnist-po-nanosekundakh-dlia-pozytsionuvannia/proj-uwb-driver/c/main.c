#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define UWB_SPEED_OF_LIGHT_M_S     299792458.0
#define UWB_TIME_RES_PICODECIMAL   15.65104167e-12
#define UWB_TIMESTAMP_MASK         0xFFFFFFFFFFULL
#define UWB_NLOS_THRESHOLD_DB      6.0

/* Опис кадрів протоколу TWR */
#define UWB_FRAME_POLL             0x01
#define UWB_FRAME_RESPONSE         0x02
#define UWB_FRAME_FINAL            0x03

typedef struct __attribute__((packed)) {
    uint8_t  frame_ctrl[2];
    uint8_t  seq_num;
    uint16_t pan_id;
    uint16_t dest_address;
    uint16_t src_address;
    uint8_t  message_type;
} uwb_header_t;

typedef struct __attribute__((packed)) {
    uwb_header_t header;
    uint64_t poll_tx_ts;     /* t1 (40 біт) */
    uint64_t resp_rx_ts;     /* t4 (40 біт) */
    uint64_t final_tx_ts;    /* t5 (40 біт) */
} uwb_final_msg_t;

typedef struct {
    float distance_meters;
    float first_path_power_dbm;
    float total_power_dbm;
    bool  is_nlos;
    bool  is_valid;
} uwb_range_result_t;

/* Віднімання 40-бітних часових міток з урахуванням переповнення 17.2 секунди */
static inline uint64_t uwb_ts_diff(uint64_t end_ts, uint64_t start_ts) {
    return (end_ts - start_ts) & UWB_TIMESTAMP_MASK;
}

/* Розрахунок діагностичних показників потужності за даними CIR */
void uwb_calculate_signal_quality(uint16_t fp_ampl1, uint16_t fp_ampl2, uint16_t fp_ampl3,
                                  uint16_t cir_pwr, uint16_t rxpacc,
                                  float *fpp_dbm, float *rxp_dbm, bool *is_nlos) {
    if (rxpacc == 0) {
        *fpp_dbm = -120.0f;
        *rxp_dbm = -120.0f;
        *is_nlos = true;
        return;
    }

    const float A = 121.74f; /* Константа для PRF 64 МГц у DW1000 */
    const float N = (float)rxpacc;

    /* First Path Power: FPP = 10 * log10((F1^2 + F2^2 + F3^2) / N^2) - A */
    float f1 = (float)fp_ampl1;
    float f2 = (float)fp_ampl2;
    float f3 = (float)fp_ampl3;
    float fp_sum_sq = (f1 * f1) + (f2 * f2) + (f3 * f3);
    *fpp_dbm = 10.0f * log10f(fp_sum_sq / (N * N)) - A;

    /* Receive Signal Power: RXP = 10 * log10((C * 2^17) / N^2) - A */
    float c_pwr = (float)cir_pwr;
    *rxp_dbm = 10.0f * log10f((c_pwr * 131072.0f) / (N * N)) - A;

    /* Якщо сумарна потужність перевищує перший промінь більше ніж на поріг -> NLOS */
    *is_nlos = (*rxp_dbm - *fpp_dbm) > UWB_NLOS_THRESHOLD_DB;
}

/* Обчислення дистанції за симетричною формулою DS-TWR */
uwb_range_result_t uwb_compute_ds_twr(uint64_t t1, uint64_t t2, uint64_t t3,
                                      uint64_t t4, uint64_t t5, uint64_t t6,
                                      uint16_t fp_ampl1, uint16_t fp_ampl2, uint16_t fp_ampl3,
                                      uint16_t cir_pwr, uint16_t rxpacc,
                                      int32_t ant_delay_ticks) {
    uwb_range_result_t result = {0};

    /* Інтервали тега та анкера */
    uint64_t t_round1 = uwb_ts_diff(t4, t1);
    uint64_t t_reply1 = uwb_ts_diff(t3, t2);
    uint64_t t_round2 = uwb_ts_diff(t6, t3);
    uint64_t t_reply2 = uwb_ts_diff(t5, t4);

    /* Формула симетричного DS-TWR: ToF = (T_r1 * T_r2 - T_p1 * T_p2) / (T_r1 + T_r2 + T_p1 + T_p2) */
    double r1 = (double)t_round1;
    double p1 = (double)t_reply1;
    double r2 = (double)t_round2;
    double p2 = (double)t_reply2;

    double numerator   = (r1 * r2) - (p1 * p2);
    double denominator = r1 + r2 + p1 + p2;

    if (denominator <= 0.0 || numerator <= 0.0) {
        result.is_valid = false;
        return result;
    }

    double tof_ticks = numerator / denominator;

    /* Віднімання калібрувальної затримки антени */
    tof_ticks -= (double)ant_delay_ticks;
    if (tof_ticks < 0.0) {
        tof_ticks = 0.0;
    }

    double tof_seconds = tof_ticks * UWB_TIME_RES_PICODECIMAL;
    result.distance_meters = (float)(tof_seconds * UWB_SPEED_OF_LIGHT_M_S);

    /* Діагностика якості каналу */
    uwb_calculate_signal_quality(fp_ampl1, fp_ampl2, fp_ampl3, cir_pwr, rxpacc,
                                 &result.first_path_power_dbm,
                                 &result.total_power_dbm,
                                 &result.is_nlos);

    result.is_valid = (result.distance_meters >= 0.0f && result.distance_meters <= 200.0f);
    return result;
}
