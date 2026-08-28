#include <stdint.h>
#include <stdbool.h>

#define PMU_BASE_ADDR        0x4000E000U
#define REG_PWR_REQ(domain)  (*(volatile uint32_t*)(PMU_BASE_ADDR + 0x10U + ((domain) * 8U)))
#define REG_PWR_STAT(domain) (*(volatile uint32_t*)(PMU_BASE_ADDR + 0x14U + ((domain) * 8U)))

#define PWR_STATUS_ACK_MASK  (1U << 0)
#define PWR_STATUS_BUSY_MASK (1U << 1)
#define PWR_TIMEOUT_CYCLES   100000U

typedef enum {
    PWR_DOMAIN_GPU  = 0,
    PWR_DOMAIN_NPU  = 1,
    PWR_DOMAIN_DSP  = 2,
    PWR_DOMAIN_MAX  = 3
} power_domain_id_t;

typedef enum {
    PWR_ERR_OK      =  0,
    PWR_ERR_TIMEOUT = -1,
    PWR_ERR_INVALID = -2
} power_status_t;

/**
 * Переведення домену живлення у вказаний стан (увімкнено / вимкнено)
 * із контролем апаратного квитування та захистом від зависання.
 */
power_status_t power_domain_set_state(power_domain_id_t domain, bool enable) {
    if (domain >= PWR_DOMAIN_MAX) {
        return PWR_ERR_INVALID;
    }

    // Запис цільового запиту в апаратний регістр PMU
    REG_PWR_REQ(domain) = enable ? 1U : 0U;

    // Очікування квитування від апаратного автомата FSM
    uint32_t timeout = PWR_TIMEOUT_CYCLES;
    while (timeout > 0) {
        uint32_t status = REG_PWR_STAT(domain);
        if ((status & PWR_STATUS_ACK_MASK) != 0U && (status & PWR_STATUS_BUSY_MASK) == 0U) {
            return PWR_ERR_OK;
        }
        timeout--;
    }

    return PWR_ERR_TIMEOUT;
}
