/* Рушій набору: таблиця дескрипторів, бюджет часу на кожен тест і
 * зупинка набору після провалу блокувального тесту. */

#include "fct.h"
#include "hal.h"
#include "report.h"

static const fct_case_t k_suite[] = {
    {"POWER_RAILS",  test_power_rails,  50000u,  true},
    {"CLOCK_PLL",    test_clock_pll,    20000u,  true},
    {"RAM_MARCH_C",  test_ram_march,    60000u,  false},
    {"I2C_DEVICES",  test_i2c_devices,  40000u,  false},
    {"SPI_FLASH_ID", test_spi_flash,    20000u,  false},
    {"RF_CW",        test_rf_cw,        4000000u, false},
    {"OTP_TRIM",     test_otp_trim,     100000u, false}
};

static void run_suite(void)
{
    const size_t count = sizeof(k_suite) / sizeof(k_suite[0]);
    bool overall_pass = true;
    bool halted = false;
    fct_deadline_t total = fct_deadline_start(0);

    report_begin();

    for (size_t i = 0; i < count; i++) {
        fct_verdict_t verdict = {FCT_SKIPPED, "Набір зупинено попереднім провалом",
                                 0, NULL};
        uint32_t spent = 0;

        if (!halted) {
            hal_watchdog_kick();
            fct_deadline_t d = fct_deadline_start(k_suite[i].budget_us);
            k_suite[i].run(&verdict);
            spent = fct_elapsed_us(&d);

            /* Тест не переривають ззовні — його бюджет сторожать дедлайни
             * усередині. Перевищення означає, що якийсь із них прогавили. */
            if (verdict.code == FCT_PASS && spent > k_suite[i].budget_us) {
                fct_fail_at(&verdict, FCT_TIMEOUT, "Перевищено бюджет часу",
                            (int32_t)spent, "us");
            }
        }

        if (verdict.code != FCT_PASS) {
            overall_pass = false;
            if (k_suite[i].blocking) {
                /* Живлення чи тактування не в нормі — далі не йдемо:
                 * радіо й пропалювання OTP на битій платі лише шкодять. */
                halted = true;
            }
        }

        report_add(k_suite[i].name, &verdict, spent);
    }

    report_finish(overall_pass, fct_elapsed_us(&total));
    hal_result_indicate(overall_pass);
}

int main(void)
{
    hal_board_init();
    run_suite();

    /* Стенд сам зніме живлення після зчитування звіту; до того моменту
     * лише годуємо сторожовий таймер. */
    for (;;) {
        hal_watchdog_kick();
    }
}
