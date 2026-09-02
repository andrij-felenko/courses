/* Стендовий розбір блокувань армінгу: збірка маски з входів,
 * читання її з кадру MSP_STATUS і з рядка CLI, звіт ArduPilot. */

#include "ap_checks.h"
#include "bf_flags.h"
#include "msp.h"
#include "prearm.h"

#include <stdio.h>
#include <string.h>

static void rule(const char *title)
{
    printf("\n=== %s ===\n", title);
}

static void print_hex(const uint8_t *data, size_t len)
{
    for (size_t i = 0; i < len; ++i) {
        printf("%02X ", data[i]);
    }
    printf("\n");
}

/* Справний стенд: живлення від силового модуля, пульт увімкнено,
 * гвинти зняті, конфігуратор закритий. */
static bf_inputs_t healthy_bench(void)
{
    bf_inputs_t in;
    memset(&in, 0, sizeof(in));
    in.gyro_present = true;
    in.acc_calibrated = true;
    in.rx_frame_valid = true;
    in.throttle_us = 1000;
    in.roll_us = 1500;
    in.pitch_us = 1500;
    in.motor_protocol_ok = true;
    in.esc_telemetry_ok = true;
    in.cpu_load_pct = 30;
    return in;
}

static void scenario_bench(void)
{
    rule("Маска на щойно ввімкненому стенді");

    bf_inputs_t in = healthy_bench();
    in.arm_switch_high = true;     /* тумблер Arm забули опустити після польоту */
    in.acc_calibrated = false;
    in.gyro_calibrating = true;
    in.throttle_us = 1180;
    in.cli_open = true;
    in.cpu_load_pct = 88;

    bf_state_t st;
    bf_state_init(&st, &in, 0);

    printf("Одразу після подачі живлення (t=0):\n");
    bf_print_mask(bf_update(&st, &in, 0), stdout);

    /* Оператор дав платі відстоятися, закрив CLI, опустив газ
     * і знизив частоту PID-циклу. Тумблер поки що піднятий. */
    in.gyro_calibrating = false;
    in.acc_calibrated = true;
    in.cli_open = false;
    in.throttle_us = 1000;
    in.cpu_load_pct = 62;
    printf("\nПричини усунено, але тумблер Arm усе ще піднятий (t=3000):\n");
    bf_print_mask(bf_update(&st, &in, 3000), stdout);

    in.arm_switch_high = false;
    printf("\nТумблер Arm опущено (t=3100):\n");
    bf_print_mask(bf_update(&st, &in, 3100), stdout);
}

/* Пульт лежить упритул до приймача: до 500 мс лінка немає взагалі,
 * далі кадр губиться рівно раз на 200 мс, а з 2000 мс пульт віднесли
 * на два метри й потік став чистим. */
static bool link_valid_at(uint32_t t_ms)
{
    if (t_ms < 500) {
        return false;
    }
    if (t_ms < 2000) {
        return (t_ms % 200) != 0;
    }
    return true;
}

static const char *describe_rx(uint32_t rx_bits)
{
    if (rx_bits == 0) {
        return "радіоблокувань немає — армінг дозволено";
    }
    if ((rx_bits & BF_BIT(BF_BAD_RX_RECOVERY)) != 0) {
        return "FAILSAFE + BAD_RX_RECOVERY: лінк є, захисна секунда триває";
    }
    return "FAILSAFE: валідних кадрів немає";
}

static void scenario_link(void)
{
    rule("Захисна секунда після відновлення лінка");

    bf_inputs_t in = healthy_bench();
    in.rx_frame_valid = false;

    bf_state_t st;
    bf_state_init(&st, &in, 0);

    uint32_t prev = 0xFFFFFFFFu;
    for (uint32_t t = 0; t <= 4000; t += 10) {
        in.rx_frame_valid = link_valid_at(t);
        const uint32_t mask = bf_update(&st, &in, t);
        const uint32_t rx_bits = mask & (BF_BIT(BF_FAILSAFE) | BF_BIT(BF_BAD_RX_RECOVERY));
        if (rx_bits != prev) {
            printf("  t=%4u мс  %s\n", t, describe_rx(rx_bits));
            prev = rx_bits;
        }
    }
    printf("  Доки кадр губиться кожні 200 мс, відлік захисної секунди\n"
           "  перезапускається і блокування не знімається взагалі.\n");
}

static void scenario_msp(void)
{
    rule("Читання маски з відповіді MSP_STATUS");

    uint8_t req[8];
    const size_t req_len = msp_build_request(MSP_STATUS, req, sizeof(req));
    printf("  запит до плати: ");
    print_hex(req, req_len);

    msp_status_t tx;
    memset(&tx, 0, sizeof(tx));
    tx.cycle_time_us = 125;
    tx.sensors = 0x0007;
    tx.cpu_load_pct = 88;
    tx.gyro_cycle_time_us = 125;
    tx.extra_len = 2;
    tx.arming_flag_count = BF_FLAG_COUNT;
    tx.arming_disable_flags = BF_BIT(BF_THROTTLE) | BF_BIT(BF_MSP) |
                              BF_BIT(BF_LOAD) | BF_BIT(BF_ACC_CAL);

    uint8_t frame[MSP_MAX_FRAME];
    const size_t len = msp_encode_status(&tx, frame, sizeof(frame));
    if (len == 0) {
        printf("  кадр не вліз у буфер\n");
        return;
    }
    printf("  відповідь плати (%zu байтів): ", len);
    print_hex(frame, len);

    msp_status_t rx;
    msp_err_t err = msp_parse_status(frame, len, &rx);
    if (err != MSP_OK) {
        printf("  розбір не вдався: %s\n", msp_strerror(err));
        return;
    }
    printf("  такт PID %u мкс, завантаження %u%%, прапорців у прошивці %u\n",
           rx.cycle_time_us, rx.cpu_load_pct, rx.arming_flag_count);
    if (rx.arming_flag_count > BF_FLAG_COUNT) {
        printf("  ! прошивка знає %u прапорців, довідник — %u\n",
               rx.arming_flag_count, BF_FLAG_COUNT);
    }
    bf_print_mask(rx.arming_disable_flags, stdout);

    /* Три способи зіпсувати кадр — три різні відмови розбору. */
    frame[7] ^= 0x20;
    printf("  побитий байт payload: %s\n", msp_strerror(msp_parse_status(frame, len, &rx)));
    frame[7] ^= 0x20;
    printf("  обрізаний буфер:      %s\n", msp_strerror(msp_parse_status(frame, len - 3, &rx)));

    /* Стара прошивка віддає коротший payload: сума збігається,
     * але до armingDisableFlags полів не вистачає. */
    uint8_t old[MSP_MAX_FRAME];
    const uint8_t old_size = 8;
    memcpy(old, frame, 5u + old_size);
    old[3] = old_size;
    uint8_t crc = (uint8_t)(old_size ^ (uint8_t)MSP_STATUS);
    for (uint8_t i = 0; i < old_size; ++i) {
        crc ^= old[5 + i];
    }
    old[5 + old_size] = crc;
    printf("  короткий payload:     %s\n",
           msp_strerror(msp_parse_status(old, 5u + old_size + 1u, &rx)));
}

static void scenario_cli(void)
{
    rule("Розбір рядка CLI-команди status");

    const char *line = "Arming disable flags: THROTTLE CLI MSP RPMFILTER SUPERGLUE";
    unsigned unknown = 0;
    const uint32_t mask = bf_parse_cli_status(line, &unknown);
    printf("  вхід: %s\n", line);
    printf("  маска 0x%08X, нерозпізнаних назв: %u\n", mask, unknown);
    bf_print_mask(mask, stdout);

    printf("\n  вхід: Arming disable flags: None\n");
    bf_print_mask(bf_parse_cli_status("Arming disable flags: None", &unknown), stdout);
}

static void scenario_ardupilot(void)
{
    rule("ArduPilot: ARMING_CHECK і повідомлення STATUSTEXT");

    const uint32_t failing = AP_BIT(AP_CHK_GPS) | AP_BIT(AP_CHK_COMPASS) |
                             AP_BIT(AP_CHK_BOARD_VOLTAGE) | AP_BIT(AP_CHK_HARDWARE_SWITCH);
    mav_statustext_t msgs[AP_CHK_COUNT];

    printf("  ARMING_CHECK = 1 (усі перевірки):\n");
    size_t n = ap_prearm_report(1, failing, msgs, AP_CHK_COUNT);
    for (size_t i = 0; i < n; ++i) {
        mav_statustext_print(&msgs[i], stdout);
    }

    /* Для столу знімають GPS: біт All гасять, решту бітів ставлять руками. */
    const int32_t stand = (int32_t)(0x7FFE & ~AP_BIT(AP_CHK_GPS) & ~AP_BIT(AP_CHK_GPS_CONFIG));
    printf("\n  ARMING_CHECK = %d (усе, крім GPS):\n", stand);
    n = ap_prearm_report(stand, failing, msgs, AP_CHK_COUNT);
    for (size_t i = 0; i < n; ++i) {
        mav_statustext_print(&msgs[i], stdout);
    }

    printf("\n  вимкнені параметром перевірки:");
    for (unsigned i = 1; i < AP_CHK_COUNT; ++i) {
        if (!ap_check_enabled(stand, (ap_check_t)i)) {
            printf(" %s;", ap_check_name((ap_check_t)i));
        }
    }
    printf("\n  Порожній звіт означає дозвіл на армінг.\n");
}

int main(void)
{
    scenario_bench();
    scenario_link();
    scenario_msp();
    scenario_cli();
    scenario_ardupilot();
    return 0;
}
