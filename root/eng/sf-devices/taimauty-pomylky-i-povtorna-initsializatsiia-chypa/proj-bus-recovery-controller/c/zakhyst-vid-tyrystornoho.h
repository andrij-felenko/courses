#ifndef RESET_ESCALATION_CONTROLLER_H
#define RESET_ESCALATION_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>
#include "stm32f4xx.h"
#include "dwt_timeout.h"
#include "i2c_bus_recovery.h"

typedef enum {
    ESCALATION_TIER_0_NONE = 0,
    ESCALATION_TIER_1_SOFT_RESET = 1,
    ESCALATION_TIER_2_PIN_RESET = 2,
    ESCALATION_TIER_3_POWER_CYCLE = 3,
    ESCALATION_TIER_FATAL = 4
} escalation_tier_t;

typedef struct {
    // Керування комутатором живлення
    GPIO_TypeDef *pwr_switch_port;
    uint8_t pwr_switch_pin;
    bool pwr_switch_active_high; // true = 1 ON, false = 0 ON (для P-MOSFET)

    // Керування виводом апаратного скидання
    GPIO_TypeDef *nrst_port;
    uint8_t nrst_pin;

    // Сигнальні лінії для переведення в Hi-Z
    GPIO_TypeDef *scl_port;
    uint8_t scl_pin;
    uint8_t scl_af;
    GPIO_TypeDef *sda_port;
    uint8_t sda_pin;
    uint8_t sda_af;

    // Часові параметри
    uint32_t reset_pulse_ms;
    uint32_t reset_settle_ms;
    uint32_t power_off_duration_ms;
    uint32_t power_on_settle_ms;
} peripheral_power_control_t;

typedef struct {
    peripheral_power_control_t power_cfg;
    i2c_bus_hardware_t i2c_hw;
    escalation_tier_t current_tier;
    uint8_t consecutive_failures;
    uint32_t total_tier1_count;
    uint32_t total_tier2_count;
    uint32_t total_tier3_count;
} reset_escalation_manager_t;

static inline void pin_set_analog_hiz(GPIO_TypeDef *port, uint8_t pin) {
    // Mode = Analog (11)
    port->MODER |= (3U << (pin * 2));
    // PUPDR = No pull (00)
    port->PUPDR &= ~(3U << (pin * 2));
}

void escalation_manager_init(reset_escalation_manager_t *mgr, const peripheral_power_control_t *pwr_cfg, const i2c_bus_hardware_t *i2c_hw) {
    mgr->power_cfg = *pwr_cfg;
    mgr->i2c_hw = *i2c_hw;
    mgr->current_tier = ESCALATION_TIER_0_NONE;
    mgr->consecutive_failures = 0;
    mgr->total_tier1_count = 0;
    mgr->total_tier2_count = 0;
    mgr->total_tier3_count = 0;

    // Початкова конфігурація силового виводу
    if (mgr->power_cfg.pwr_switch_port) {
        GPIO_TypeDef *p = mgr->power_cfg.pwr_switch_port;
        uint8_t pin = mgr->power_cfg.pwr_switch_pin;
        p->MODER &= ~(3U << (pin * 2));
        p->MODER |= (1U << (pin * 2)); // Output Push-Pull
        p->OTYPER &= ~(1U << pin);
        // Вмикаємо живлення
        if (mgr->power_cfg.pwr_switch_active_high) {
            p->BSRR = (1U << pin);
        } else {
            p->BSRR = (1U << (pin + 16)); // Low для P-MOSFET
        }
    }

    // Початкова конфігурація виводу nRESET у високий стан
    if (mgr->power_cfg.nrst_port) {
        GPIO_TypeDef *p = mgr->power_cfg.nrst_port;
        uint8_t pin = mgr->power_cfg.nrst_pin;
        p->MODER &= ~(3U << (pin * 2));
        p->MODER |= (1U << (pin * 2)); // Output
        p->BSRR = (1U << pin);         // High (неактивний)
    }
}

void escalation_execute_tier2_pin_reset(reset_escalation_manager_t *mgr) {
    if (!mgr->power_cfg.nrst_port) return;

    GPIO_TypeDef *p = mgr->power_cfg.nrst_port;
    uint8_t pin = mgr->power_cfg.nrst_pin;

    // 1. Опускаємо nRESET у 0
    p->BSRR = (1U << (pin + 16));
    dwt_delay_ms(mgr->power_cfg.reset_pulse_ms ? mgr->power_cfg.reset_pulse_ms : 5);

    // 2. Піднімаємо nRESET у 1
    p->BSRR = (1U << pin);
    dwt_delay_ms(mgr->power_cfg.reset_settle_ms ? mgr->power_cfg.reset_settle_ms : 20);

    mgr->total_tier2_count++;
}

void escalation_execute_tier3_power_cycle(reset_escalation_manager_t *mgr) {
    if (!mgr->power_cfg.pwr_switch_port) return;

    // 1. Ізоляція всіх ліній: переведення SCL, SDA, nRESET в Analog Hi-Z
    pin_set_analog_hiz(mgr->power_cfg.scl_port, mgr->power_cfg.scl_pin);
    pin_set_analog_hiz(mgr->power_cfg.sda_port, mgr->power_cfg.sda_pin);
    if (mgr->power_cfg.nrst_port) {
        pin_set_analog_hiz(mgr->power_cfg.nrst_port, mgr->power_cfg.nrst_pin);
    }

    // 2. Знеструмлення: закриваємо MOSFET
    GPIO_TypeDef *pwr = mgr->power_cfg.pwr_switch_port;
    uint8_t pwr_pin = mgr->power_cfg.pwr_switch_pin;
    if (mgr->power_cfg.pwr_switch_active_high) {
        pwr->BSRR = (1U << (pwr_pin + 16)); // Low = OFF
    } else {
        pwr->BSRR = (1U << pwr_pin);        // High = OFF (P-MOSFET)
    }

    // 3. Пауза для повного розряду ємностей шини (50 мс)
    dwt_delay_ms(mgr->power_cfg.power_off_duration_ms ? mgr->power_cfg.power_off_duration_ms : 50);

    // 4. Подача живлення: відкриваємо MOSFET
    if (mgr->power_cfg.pwr_switch_active_high) {
        pwr->BSRR = (1U << pwr_pin);        // High = ON
    } else {
        pwr->BSRR = (1U << (pwr_pin + 16)); // Low = ON (P-MOSFET)
    }

    // 5. Очікування стабілізації живлення та POR
    dwt_delay_ms(mgr->power_cfg.power_on_settle_ms ? mgr->power_cfg.power_on_settle_ms : 20);

    // 6. Відновлення режиму виводу nRESET
    if (mgr->power_cfg.nrst_port) {
        GPIO_TypeDef *nrst = mgr->power_cfg.nrst_port;
        uint8_t nrst_pin = mgr->power_cfg.nrst_pin;
        nrst->MODER &= ~(3U << (nrst_pin * 2));
        nrst->MODER |= (1U << (nrst_pin * 2)); // Output
        nrst->BSRR = (1U << nrst_pin);         // High
    }

    // 7. Відновлення режимів альтернативної функції для SCL та SDA
    i2c_pin_set_af_od(mgr->power_cfg.scl_port, mgr->power_cfg.scl_pin, mgr->power_cfg.scl_af);
    i2c_pin_set_af_od(mgr->power_cfg.sda_port, mgr->power_cfg.sda_pin, mgr->power_cfg.sda_af);

    mgr->total_tier3_count++;
}

escalation_tier_t escalation_step(reset_escalation_manager_t *mgr) {
    mgr->consecutive_failures++;

    if (mgr->consecutive_failures == 1) {
        mgr->current_tier = ESCALATION_TIER_1_SOFT_RESET;
        i2c_bus_unlock_9_pulses(&mgr->i2c_hw, NULL);
        mgr->total_tier1_count++;
    } else if (mgr->consecutive_failures == 2) {
        mgr->current_tier = ESCALATION_TIER_2_PIN_RESET;
        escalation_execute_tier2_pin_reset(mgr);
    } else if (mgr->consecutive_failures == 3) {
        mgr->current_tier = ESCALATION_TIER_3_POWER_CYCLE;
        escalation_execute_tier3_power_cycle(mgr);
    } else {
        mgr->current_tier = ESCALATION_TIER_FATAL;
    }

    return mgr->current_tier;
}

void escalation_mark_success(reset_escalation_manager_t *mgr) {
    mgr->consecutive_failures = 0;
    mgr->current_tier = ESCALATION_TIER_0_NONE;
}

#endif // RESET_ESCALATION_CONTROLLER_H
