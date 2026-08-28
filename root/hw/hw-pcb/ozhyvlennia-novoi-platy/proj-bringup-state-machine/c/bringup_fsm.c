/* ============================================================================
 * Bringup Diagnostic State Machine (C99 Production Implementation)
 * File: bringup_fsm.c
 * ============================================================================ */

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
#include <stdio.h>

#define ADC_SAMPLE_COUNT        1024
#define SWD_ACK_OK              0x01
#define SWD_ACK_WAIT            0x02
#define SWD_ACK_FAULT           0x04

#define TARGET_VDD_NOMINAL_MV   3300
#define TARGET_VDD_MIN_MV       3150
#define TARGET_VDD_MAX_MV       3450
#define MAX_RIPPLE_PP_MV        35
#define MIN_SLEW_RATE_MV_PER_US 50
#define MAX_SLEW_RATE_MV_PER_US 5000

#define DP_REG_IDCODE           0x00
#define DP_REG_CTRL_STAT        0x04
#define DP_REG_SELECT           0x08
#define DP_REG_RDBUFF           0x0C

typedef enum {
    BRINGUP_STATE_IDLE = 0,
    BRINGUP_STATE_POWER_RAIL_CHECK,
    BRINGUP_STATE_NRST_VERIFY,
    BRINGUP_STATE_CLOCK_MEASURE,
    BRINGUP_STATE_SWD_DISCOVERY,
    BRINGUP_STATE_RECOVERY_TRIAGE,
    BRINGUP_STATE_REPORT_TELEMETRY,
    BRINGUP_STATE_COMPLETE_SUCCESS,
    BRINGUP_STATE_COMPLETE_FAIL
} bringup_state_t;

typedef enum {
    BRINGUP_ERR_NONE = 0,
    BRINGUP_ERR_POWER_VOLTAGE_OUT_OF_SPEC,
    BRINGUP_ERR_POWER_NON_MONOTONIC,
    BRINGUP_ERR_POWER_RIPPLE_EXCESSIVE,
    BRINGUP_ERR_NRST_STUCK_LOW,
    BRINGUP_ERR_NRST_TIMEOUT,
    BRINGUP_ERR_CLOCK_ABSENT,
    BRINGUP_ERR_CLOCK_PPM_EXCESSIVE,
    BRINGUP_ERR_SWD_NO_RESPONSE,
    BRINGUP_ERR_SWD_PARITY_MISMATCH,
    BRINGUP_ERR_SWD_INVALID_IDCODE,
    BRINGUP_ERR_CORE_HALT_FAILED
} bringup_error_t;

typedef struct {
    uint32_t vdd_mean_mv;
    uint32_t vdd_ripple_pp_mv;
    uint32_t vdd_slew_rate_mv_per_us;
    bool     vdd_is_monotonic;
    uint32_t nrst_release_delay_us;
    uint32_t nrst_steady_state_mv;
    uint32_t clock_freq_hz;
    int32_t  clock_ppm_error;
    uint32_t swd_dpidr;
    uint8_t  swd_ack_status;
    bool     is_recovered;
    bringup_error_t last_error;
} bringup_telemetry_t;

typedef struct {
    void     (*power_enable)(bool enable);
    void     (*start_adc_sampling)(uint16_t *buf, size_t count);
    bool     (*is_adc_sampling_complete)(void);
    uint32_t (*get_nrst_mv)(void);
    void     (*drive_nrst)(bool assert_low);
    void     (*drive_boot0)(bool high);
    uint32_t (*measure_hse_freq_hz)(uint32_t gate_time_ms);
    void     (*swd_set_clk)(bool level);
    void     (*swd_set_dio)(bool level);
    bool     (*swd_get_dio)(void);
    void     (*swd_set_dio_dir_out)(bool is_output);
    void     (*delay_us)(uint32_t us);
    uint32_t (*get_system_time_ms)(void);
} bringup_hal_ops_t;

typedef struct {
    bringup_state_t     state;
    bringup_telemetry_t telemetry;
    const bringup_hal_ops_t *hal;
    uint16_t            adc_raw_buffer[ADC_SAMPLE_COUNT];
    uint32_t            state_entry_time_ms;
    uint8_t             retry_counter;
} bringup_fsm_t;

/* --- Прототипи допоміжних функцій SWD --- */
static void swd_clock_pulse(const bringup_hal_ops_t *hal);
static void swd_line_reset(const bringup_hal_ops_t *hal);
static void swd_send_switch_sequence(const bringup_hal_ops_t *hal);
static bool swd_read_dp(const bringup_hal_ops_t *hal, uint8_t addr_reg, uint32_t *out_val, uint8_t *out_ack);
static bool swd_write_dp(const bringup_hal_ops_t *hal, uint8_t addr_reg, uint32_t val);
static uint8_t calc_parity32(uint32_t val);

void bringup_fsm_init(bringup_fsm_t *fsm, const bringup_hal_ops_t *hal) {
    memset(fsm, 0, sizeof(bringup_fsm_t));
    fsm->state = BRINGUP_STATE_IDLE;
    fsm->hal = hal;
}

void bringup_fsm_start(bringup_fsm_t *fsm) {
    fsm->state = BRINGUP_STATE_POWER_RAIL_CHECK;
    fsm->state_entry_time_ms = fsm->hal->get_system_time_ms();
    fsm->retry_counter = 0;
    fsm->hal->power_enable(true);
    fsm->hal->start_adc_sampling(fsm->adc_raw_buffer, ADC_SAMPLE_COUNT);
}

void bringup_fsm_process(bringup_fsm_t *fsm) {
    uint32_t now_ms = fsm->hal->get_system_time_ms();

    switch (fsm->state) {
    case BRINGUP_STATE_IDLE:
        break;

    case BRINGUP_STATE_POWER_RAIL_CHECK: {
        if (!fsm->hal->is_adc_sampling_complete()) {
            if (now_ms - fsm->state_entry_time_ms > 100) {
                fsm->telemetry.last_error = BRINGUP_ERR_POWER_VOLTAGE_OUT_OF_SPEC;
                fsm->state = BRINGUP_STATE_RECOVERY_TRIAGE;
            }
            return;
        }

        /* 1. Обробка вибірки АЦП: розрахунок Slew Rate та монотонності */
        uint32_t v_10_idx = 0, v_90_idx = 0;
        uint32_t sum = 0, min_val = 0xFFFF, max_val = 0;
        bool monotonic = true;
        uint16_t v_10_thresh = (TARGET_VDD_NOMINAL_MV * 10) / 100;
        uint16_t v_90_thresh = (TARGET_VDD_NOMINAL_MV * 90) / 100;

        for (size_t i = 0; i < ADC_SAMPLE_COUNT; ++i) {
            uint16_t v = fsm->adc_raw_buffer[i];
            if (v_10_idx == 0 && v >= v_10_thresh) v_10_idx = (uint32_t)i;
            if (v_90_idx == 0 && v >= v_90_thresh) v_90_idx = (uint32_t)i;

            if (i > 0 && v_10_idx > 0 && v_90_idx == 0) {
                if ((int32_t)v - (int32_t)fsm->adc_raw_buffer[i - 1] < -30) {
                    monotonic = false;
                }
            }

            /* Статистика на стаціонарній ділянці (останні 256 відліків) */
            if (i >= ADC_SAMPLE_COUNT - 256) {
                sum += v;
                if (v < min_val) min_val = v;
                if (v > max_val) max_val = v;
            }
        }

        fsm->telemetry.vdd_is_monotonic = monotonic;
        fsm->telemetry.vdd_mean_mv = sum / 256;
        fsm->telemetry.vdd_ripple_pp_mv = max_val - min_val;

        if (v_90_idx > v_10_idx) {
            uint32_t dt_us = v_90_idx - v_10_idx;
            fsm->telemetry.vdd_slew_rate_mv_per_us = (v_90_thresh - v_10_thresh) / dt_us;
        }

        /* 2. Валідація критеріїв придатності шини живлення */
        if (fsm->telemetry.vdd_mean_mv < TARGET_VDD_MIN_MV ||
            fsm->telemetry.vdd_mean_mv > TARGET_VDD_MAX_MV) {
            fsm->telemetry.last_error = BRINGUP_ERR_POWER_VOLTAGE_OUT_OF_SPEC;
            fsm->state = BRINGUP_STATE_RECOVERY_TRIAGE;
            return;
        }

        if (!monotonic) {
            fsm->telemetry.last_error = BRINGUP_ERR_POWER_NON_MONOTONIC;
            fsm->state = BRINGUP_STATE_RECOVERY_TRIAGE;
            return;
        }

        if (fsm->telemetry.vdd_ripple_pp_mv > MAX_RIPPLE_PP_MV) {
            fsm->telemetry.last_error = BRINGUP_ERR_POWER_RIPPLE_EXCESSIVE;
            fsm->state = BRINGUP_STATE_RECOVERY_TRIAGE;
            return;
        }

        /* Перехід до верифікації лінії NRST */
        fsm->state = BRINGUP_STATE_NRST_VERIFY;
        fsm->state_entry_time_ms = now_ms;
        break;
    }

    case BRINGUP_STATE_NRST_VERIFY: {
        uint32_t nrst_mv = fsm->hal->get_nrst_mv();
        fsm->telemetry.nrst_steady_state_mv = nrst_mv;

        if (nrst_mv > (TARGET_VDD_NOMINAL_MV * 80) / 100) {
            fsm->telemetry.nrst_release_delay_us = (now_ms - fsm->state_entry_time_ms) * 1000;
            fsm->state = BRINGUP_STATE_CLOCK_MEASURE;
            fsm->state_entry_time_ms = now_ms;
            return;
        }

        if (now_ms - fsm->state_entry_time_ms > 150) {
            fsm->telemetry.last_error = (nrst_mv < 500) ? BRINGUP_ERR_NRST_STUCK_LOW : BRINGUP_ERR_NRST_TIMEOUT;
            fsm->state = BRINGUP_STATE_RECOVERY_TRIAGE;
        }
        break;
    }

    case BRINGUP_STATE_CLOCK_MEASURE: {
        uint32_t freq = fsm->hal->measure_hse_freq_hz(100);
        fsm->telemetry.clock_freq_hz = freq;

        if (freq == 0) {
            fsm->telemetry.last_error = BRINGUP_ERR_CLOCK_ABSENT;
            fsm->state = BRINGUP_STATE_RECOVERY_TRIAGE;
            return;
        }

        constexpr uint32_t target_freq = 25000000;
        int64_t diff = (int64_t)freq - (int64_t)target_freq;
        int32_t ppm = (int32_t)((diff * 1000000) / target_freq);
        fsm->telemetry.clock_ppm_error = ppm;

        if (ppm > 200 || ppm < -200) {
            fsm->telemetry.last_error = BRINGUP_ERR_CLOCK_PPM_EXCESSIVE;
            fsm->state = BRINGUP_STATE_RECOVERY_TRIAGE;
            return;
        }

        fsm->state = BRINGUP_STATE_SWD_DISCOVERY;
        fsm->state_entry_time_ms = now_ms;
        break;
    }

    case BRINGUP_STATE_SWD_DISCOVERY: {
        swd_line_reset(fsm->hal);
        swd_send_switch_sequence(fsm->hal);
        swd_line_reset(fsm->hal);

        uint32_t dpidr = 0;
        uint8_t ack = 0;
        bool ok = swd_read_dp(fsm->hal, DP_REG_IDCODE, &dpidr, &ack);
        fsm->telemetry.swd_ack_status = ack;
        fsm->telemetry.swd_dpidr = dpidr;

        if (!ok || ack != SWD_ACK_OK) {
            fsm->telemetry.last_error = (ack == 0) ? BRINGUP_ERR_SWD_NO_RESPONSE : BRINGUP_ERR_SWD_PARITY_MISMATCH;
            fsm->state = BRINGUP_STATE_RECOVERY_TRIAGE;
            return;
        }

        if ((dpidr & 0x00000FFE) != 0x00000476 && (dpidr & 0x00000FFE) != 0x00000020) {
            fsm->telemetry.last_error = BRINGUP_ERR_SWD_INVALID_IDCODE;
            fsm->state = BRINGUP_STATE_RECOVERY_TRIAGE;
            return;
        }

        /* Активація доменів живлення налагодження */
        swd_write_dp(fsm->hal, DP_REG_CTRL_STAT, 0x50000000); /* CSYSPWRUPREQ | CDBGPWRUPREQ */

        fsm->state = BRINGUP_STATE_REPORT_TELEMETRY;
        break;
    }

    case BRINGUP_STATE_RECOVERY_TRIAGE: {
        fsm->telemetry.is_recovered = true;
        if (fsm->retry_counter >= 3) {
            fsm->state = BRINGUP_STATE_REPORT_TELEMETRY;
            return;
        }
        fsm->retry_counter++;

        /* 1. Апаратне скидання Connect-Under-Reset */
        fsm->hal->drive_nrst(true);
        fsm->hal->delay_us(5000);

        swd_line_reset(fsm->hal);
        swd_send_switch_sequence(fsm->hal);
        swd_line_reset(fsm->hal);

        uint32_t dpidr = 0;
        uint8_t ack = 0;
        if (swd_read_dp(fsm->hal, DP_REG_IDCODE, &dpidr, &ack) && ack == SWD_ACK_OK) {
            fsm->telemetry.swd_dpidr = dpidr;
            swd_write_dp(fsm->hal, DP_REG_CTRL_STAT, 0x50000000);
            fsm->hal->drive_nrst(false);
            fsm->state = BRINGUP_STATE_REPORT_TELEMETRY;
            return;
        }

        /* 2. Спроба переведення BOOT0 в High (System Memory Bootloader) */
        fsm->hal->drive_boot0(true);
        fsm->hal->drive_nrst(true);
        fsm->hal->delay_us(10000);
        fsm->hal->drive_nrst(false);
        fsm->hal->delay_us(20000);

        fsm->state = BRINGUP_STATE_SWD_DISCOVERY;
        break;
    }

    case BRINGUP_STATE_REPORT_TELEMETRY:
        fsm->state = (fsm->telemetry.last_error == BRINGUP_ERR_NONE || fsm->telemetry.is_recovered)
                     ? BRINGUP_STATE_COMPLETE_SUCCESS
                     : BRINGUP_STATE_COMPLETE_FAIL;
        break;

    case BRINGUP_STATE_COMPLETE_SUCCESS:
    case BRINGUP_STATE_COMPLETE_FAIL:
        break;
    }
}

size_t bringup_generate_json_report(const bringup_fsm_t *fsm, char *out_buf, size_t max_len) {
    const char *verdict_str = "FAIL_HARDWARE";
    if (fsm->telemetry.last_error == BRINGUP_ERR_NONE) {
        verdict_str = "PASS";
    } else if (fsm->telemetry.is_recovered) {
        verdict_str = "WARN_RECOVERED";
    }

    return (size_t)snprintf(out_buf, max_len,
        "{
"
        "  "bringup_report": {
"
        "    "verdict": "%s",
"
        "    "error_code": %u,
"
        "    "power_rail": {
"
        "      "nominal_mv": %u,
"
        "      "measured_mean_mv": %lu,
"
        "      "ripple_pp_mv": %lu,
"
        "      "slew_rate_mv_per_us": %lu,
"
        "      "is_monotonic": %s
"
        "    },
"
        "    "reset_circuit": {
"
        "      "nrst_steady_mv": %lu,
"
        "      "release_delay_us": %lu
"
        "    },
"
        "    "clock_system": {
"
        "      "measured_freq_hz": %lu,
"
        "      "ppm_error": %ld
"
        "    },
"
        "    "swd_interface": {
"
        "      "dpidr_hex": "0x%08lX",
"
        "      "ack_status": %u,
"
        "      "recovery_invoked": %s
"
        "    }
"
        "  }
"
        "}",
        verdict_str,
        (unsigned)fsm->telemetry.last_error,
        TARGET_VDD_NOMINAL_MV,
        (unsigned long)fsm->telemetry.vdd_mean_mv,
        (unsigned long)fsm->telemetry.vdd_ripple_pp_mv,
        (unsigned long)fsm->telemetry.vdd_slew_rate_mv_per_us,
        fsm->telemetry.vdd_is_monotonic ? "true" : "false",
        (unsigned long)fsm->telemetry.nrst_steady_state_mv,
        (unsigned long)fsm->telemetry.nrst_release_delay_us,
        (unsigned long)fsm->telemetry.clock_freq_hz,
        (long)fsm->telemetry.clock_ppm_error,
        (unsigned long)fsm->telemetry.swd_dpidr,
        fsm->telemetry.swd_ack_status,
        fsm->telemetry.is_recovered ? "true" : "false"
    );
}

/* --- Допоміжні функції низькорівневого бітбенг-майстра SWD --- */

static void swd_clock_pulse(const bringup_hal_ops_t *hal) {
    hal->swd_set_clk(false);
    hal->delay_us(1);
    hal->swd_set_clk(true);
    hal->delay_us(1);
}

static void swd_line_reset(const bringup_hal_ops_t *hal) {
    hal->swd_set_dio_out(true);
    hal->swd_set_dio(true);
    for (int i = 0; i < 56; ++i) {
        swd_clock_pulse(hal);
    }
}

static void swd_send_switch_sequence(const bringup_hal_ops_t *hal) {
    uint16_t seq = 0xE79E; /* LSB-first для 0x79E7 */
    hal->swd_set_dio_out(true);
    for (int i = 0; i < 16; ++i) {
        hal->swd_set_dio((seq >> i) & 1);
        swd_clock_pulse(hal);
    }
}

static uint8_t calc_parity32(uint32_t val) {
    val ^= val >> 16;
    val ^= val >> 8;
    val ^= val >> 4;
    val ^= val >> 2;
    val ^= val >> 1;
    return (uint8_t)(val & 1);
}

static bool swd_read_dp(const bringup_hal_ops_t *hal, uint8_t addr_reg, uint32_t *out_val, uint8_t *out_ack) {
    uint8_t req = 0x81 | ((addr_reg & 0x0C) << 1); /* Start=1, APnDP=0, RnW=1, Stop=0, Park=1 */
    uint8_t parity = ((req >> 1) ^ (req >> 2) ^ (req >> 3) ^ (req >> 4)) & 1;
    req |= (parity << 5);

    hal->swd_set_dio_out(true);
    for (int i = 0; i < 8; ++i) {
        hal->swd_set_dio((req >> i) & 1);
        swd_clock_pulse(hal);
    }

    hal->swd_set_dio_out(false);
    swd_clock_pulse(hal);

    uint8_t ack = 0;
    for (int i = 0; i < 3; ++i) {
        hal->swd_set_clk(false);
        hal->delay_us(1);
        if (hal->swd_get_dio()) ack |= (1 << i);
        hal->swd_set_clk(true);
        hal->delay_us(1);
    }
    *out_ack = ack;

    if (ack != SWD_ACK_OK) return false;

    uint32_t data = 0;
    for (int i = 0; i < 32; ++i) {
        hal->swd_set_clk(false);
        hal->delay_us(1);
        if (hal->swd_get_dio()) data |= (1UL << i);
        hal->swd_set_clk(true);
        hal->delay_us(1);
    }

    hal->swd_set_clk(false);
    hal->delay_us(1);
    bool rcv_par = hal->swd_get_dio();
    hal->swd_set_clk(true);
    hal->delay_us(1);

    hal->swd_set_dio_out(true);
    hal->swd_set_dio(false);
    for (int i = 0; i < 4; ++i) swd_clock_pulse(hal);

    if (rcv_par != calc_parity32(data)) return false;

    *out_val = data;
    return true;
}

static bool swd_write_dp(const bringup_hal_ops_t *hal, uint8_t addr_reg, uint32_t val) {
    uint8_t req = 0x81 | ((addr_reg & 0x0C) << 1); /* Start=1, APnDP=0, RnW=0, Stop=0, Park=1 */
    uint8_t parity = ((req >> 1) ^ (req >> 2) ^ (req >> 3) ^ (req >> 4)) & 1;
    req |= (parity << 5);

    hal->swd_set_dio_out(true);
    for (int i = 0; i < 8; ++i) {
        hal->swd_set_dio((req >> i) & 1);
        swd_clock_pulse(hal);
    }

    hal->swd_set_dio_out(false);
    swd_clock_pulse(hal);

    uint8_t ack = 0;
    for (int i = 0; i < 3; ++i) {
        hal->swd_set_clk(false);
        hal->delay_us(1);
        if (hal->swd_get_dio()) ack |= (1 << i);
        hal->swd_set_clk(true);
        hal->delay_us(1);
    }

    if (ack != SWD_ACK_OK) return false;

    swd_clock_pulse(hal);
    hal->swd_set_dio_out(true);

    for (int i = 0; i < 32; ++i) {
        hal->swd_set_dio(((val >> i) & 1) != 0);
        swd_clock_pulse(hal);
    }

    hal->swd_set_dio(calc_parity32(val));
    swd_clock_pulse(hal);

    hal->swd_set_dio(false);
    for (int i = 0; i < 4; ++i) swd_clock_pulse(hal);

    return true;
}
