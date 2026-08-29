/* power_sequencer.h — кінцевий автомат покрокового вмикання рейок.
 *
 * Порядок жорсткий: ядро -> DVDD -> зняття NRST -> периферія через ключ.
 * Крок далі робиться лише за фактом PGOOD попереднього, а не «через затримку
 * на око»: інакше периферія дістає живлення раніше за ядро й тягне струм
 * крізь ESD-діоди непіднятого мікроконтролера. */
#ifndef POWER_SEQUENCER_H
#define POWER_SEQUENCER_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    PWR_STATE_OFF = 0,        /* усе знято, шина ізольована */
    PWR_STATE_WAIT_CORE_PG,   /* подали EN на I ступінь, чекаємо PGOOD */
    PWR_STATE_WAIT_IO_PG,     /* подали DVDD, чекаємо PGOOD */
    PWR_STATE_RELEASE_RESET,  /* витримка на перехідні процеси, тоді NRST геть */
    PWR_STATE_PERIPH_RAMP,    /* ключ відкритий, напруга наростає (dV/dt) */
    PWR_STATE_READY,          /* робочий стан, триває моніторинг */
    PWR_STATE_FAULT           /* аварія зафіксована, живлення знято */
} pwr_state_t;

typedef enum {
    PWR_ERR_NONE = 0,
    PWR_ERR_VIN_LOW,        /* вхід нижчий за 9 В ще до старту */
    PWR_ERR_CORE_TIMEOUT,   /* PGOOD ядра не з'явився */
    PWR_ERR_IO_TIMEOUT,     /* PGOOD DVDD не з'явився */
    PWR_ERR_BROWNOUT,       /* просідання входу або втрата PGOOD у роботі */
    PWR_ERR_OVERCURRENT     /* лінія аварії силового ключа */
} pwr_error_t;

typedef struct {
    uint32_t core_pg_timeout_ms;  /* скільки чекати PGOOD I ступеня */
    uint32_t io_pg_timeout_ms;    /* скільки чекати PGOOD DVDD */
    uint32_t reset_release_ms;    /* витримка перед зняттям NRST */
    uint32_t periph_ramp_ms;      /* t_r ключа плюс запас */
    uint16_t vin_min_mv;          /* нижня межа робочого діапазону входу */
} pwr_config_t;

typedef struct {
    pwr_config_t cfg;
    pwr_state_t state;
    pwr_error_t last_error;
    uint32_t state_timer_ms;  /* час у поточному стані */
    uint32_t fault_count;     /* скільки разів падали від старту прошивки */
} power_sequencer_t;

/* Приводить структуру й плату у відомий знеструмлений стан. */
void pwr_seq_init(power_sequencer_t *seq, const pwr_config_t *cfg);

/* Запускає підняття. Дозволено лише з OFF або FAULT (аварія засувна). */
void pwr_seq_start(power_sequencer_t *seq);

/* Знімає живлення у зворотному порядку. Викликати можна з будь-якого стану. */
void pwr_seq_shutdown(power_sequencer_t *seq);

/* Один крок автомата; elapsed_ms — час від попереднього виклику. */
void pwr_seq_tick(power_sequencer_t *seq, uint32_t elapsed_ms);

bool pwr_seq_is_ready(const power_sequencer_t *seq);

const char *pwr_state_name(pwr_state_t state);
const char *pwr_error_name(pwr_error_t err);

#endif /* POWER_SEQUENCER_H */
