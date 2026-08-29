#include "dev_driver.h"
#include "sim_device.h"

#include <stdio.h>

/* Прогін одного сценарію: автомат крокує щомілісекунди, як у справжньому
   while(1) поруч з іншими диспетчерами задач. */
static dev_fsm_state_t run_scenario(const char *title,
                                    const sim_faults_t *faults,
                                    const reg_config_entry_t *config,
                                    uint8_t config_count,
                                    uint32_t budget_ms)
{
    dev_driver_t drv;
    dev_fsm_state_t prev;
    uint32_t t;

    printf("\n=== %s ===\n", title);
    sim_device_reset(faults);
    dev_driver_init(&drv, config, config_count);
    prev = drv.state;
    printf("%6u мс  %s\n", sim_now(), dev_driver_state_name(drv.state));

    for (t = 0U; t < budget_ms; ++t) {
        dev_driver_step(&drv);          /* тут же крокували б інші драйвери */

        if (drv.state != prev) {
            printf("%6u мс  %s\n", sim_now(), dev_driver_state_name(drv.state));
            prev = drv.state;
        }
        if (dev_driver_is_ready(&drv) || dev_driver_is_fault(&drv)) {
            break;
        }
        sim_tick();
    }

    printf("       спроб: %u, відновлень шини: %u, SDA затиснута: %s\n",
           drv.retry_count, sim_recoveries(), sim_sda_stuck() ? "так" : "ні");
    if (drv.fault_reason != NULL) {
        printf("       причина відмови: %s\n", drv.fault_reason);
    }
    return drv.state;
}

static int expect(dev_fsm_state_t got, dev_fsm_state_t want)
{
    if (got == want) {
        printf("       ОК: очікували %s\n", dev_driver_state_name(want));
        return 0;
    }
    printf("       ЗБІЙ: очікували %s, дістали %s\n",
           dev_driver_state_name(want), dev_driver_state_name(got));
    return 1;
}

int main(void)
{
    int failures = 0;
    sim_faults_t f;

    /* Штучна розбіжність Read-Back: у таблиці підмінено байт ODR на
       заборонену комбінацію, яку кремній не приймає. */
    static const reg_config_entry_t FORBIDDEN_CONFIG[2] = {
        { REG_RANGE_CTRL, 0x02U, 0x0FU },
        { REG_ODR_FILTER, 0x7FU, 0x7FU },
    };

    f = sim_faults_default();
    failures += expect(run_scenario("Нормальний старт", &f,
                                    DEV_DEFAULT_CONFIG, DEV_DEFAULT_CONFIG_SIZE, 2000U),
                       FSM_STATE_READY);

    /* Штучний NACK: живлення давача зникає під час SW_RESET і повертається
       через 150 мс. Перевіряємо вхід у RETRY_BACKOFF і звільнення шини. */
    f = sim_faults_default();
    f.power_off_at_ms = 20U;
    f.power_on_at_ms = 150U;
    failures += expect(run_scenario("Провал живлення під час SW_RESET", &f,
                                    DEV_DEFAULT_CONFIG, DEV_DEFAULT_CONFIG_SIZE, 2000U),
                       FSM_STATE_READY);

    /* Той самий обрив, але живлення не повертається: ліміт спроб вичерпано. */
    f = sim_faults_default();
    f.power_off_at_ms = 20U;
    failures += expect(run_scenario("Давач не повернувся після обриву", &f,
                                    DEV_DEFAULT_CONFIG, DEV_DEFAULT_CONFIG_SIZE, 2000U),
                       FSM_STATE_FAULT_SAFE);

    f = sim_faults_default();
    failures += expect(run_scenario("Заборонена конфігурація (Read-Back Mismatch)", &f,
                                    FORBIDDEN_CONFIG, 2U, 2000U),
                       FSM_STATE_FAULT_SAFE);

    /* Імітація повільного POR: лабораторний блок наростає 50 мс. */
    f = sim_faults_default();
    f.por_ramp_ms = 50U;
    failures += expect(run_scenario("Повільне наростання V_DD (50 мс)", &f,
                                    DEV_DEFAULT_CONFIG, DEV_DEFAULT_CONFIG_SIZE, 2000U),
                       FSM_STATE_READY);

    printf("\nПідсумок: %s\n", failures == 0 ? "усі сценарії пройдено" : "є розбіжності");
    return failures == 0 ? 0 : 1;
}
