/* power_sequencer.h - C99 embedded HAL implementation */
#ifndef POWER_SEQUENCER_H
#define POWER_SEQUENCER_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    PWR_STATE_OFF = 0,
    PWR_STATE_WAIT_CORE_PG,
    PWR_STATE_ENABLE_IO,
    PWR_STATE_WAIT_IO_PG,
    PWR_STATE_ENABLE_PERIPH,
    PWR_STATE_READY,
    PWR_STATE_FAULT
} pwr_state_t;

typedef enum {
    PWR_ERR_NONE = 0,
    PWR_ERR_CORE_TIMEOUT,
    PWR_ERR_IO_TIMEOUT,
    PWR_ERR_BROWNOUT,
    PWR_ERR_OVERCURRENT
} pwr_error_t;

typedef struct {
    uint32_t core_pg_timeout_ms;
    uint32_t io_pg_timeout_ms;
    uint32_t periph_stabilize_ms;
} pwr_config_t;

typedef struct {
    pwr_state_t state;
    pwr_error_t last_error;
    uint32_t state_timer_ms;
    pwr_config_t config;
    bool core_pg_pin_state;
    bool io_pg_pin_state;
    bool fault_pin_state;
} power_sequencer_t;

void pwr_seq_init(power_sequencer_t *seq, const pwr_config_t *cfg);
void pwr_seq_start_powerup(power_sequencer_t *seq);
void pwr_seq_start_shutdown(power_sequencer_t *seq);
void pwr_seq_process_tick(power_sequencer_t *seq, uint32_t elapsed_ms);

/* Низькорівневі апаратні виклики керування ключами */
void hw_set_core_regulator_en(bool enable);
void hw_set_io_regulator_en(bool enable);
void hw_set_periph_load_switch_en(bool enable);
bool hw_read_core_pgood(void);
bool hw_read_io_pgood(void);
bool hw_read_fault_irq(void);

#endif /* POWER_SEQUENCER_H */
