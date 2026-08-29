/* main.c — стенд секвенсера: ганяємо автомат по сценаріях і дивимось
 * на переходи станів так, як дивилися б логічним аналізатором на EN/PGOOD. */
#include <stddef.h>
#include <stdio.h>

#include "board_sim.h"
#include "power_sequencer.h"

#define TICK_MS       1u
#define RUN_LIMIT_MS  120u

static const pwr_config_t CONFIG = {
    .core_pg_timeout_ms = 20u,
    .io_pg_timeout_ms = 20u,
    .reset_release_ms = 5u,
    .periph_ramp_ms = 8u,   /* t_r ключа 1…5 мс плюс запас */
    .vin_min_mv = 9000u     /* нижня межа робочого діапазону 9…28 В */
};

static void run_scenario(const sim_scenario_t *sc)
{
    power_sequencer_t seq;
    pwr_state_t prev;
    uint32_t t;

    sim_load(sc);
    pwr_seq_init(&seq, &CONFIG);
    pwr_seq_start(&seq);
    prev = seq.state;

    printf("\n=== %s ===\n", sc->name);
    printf("  %4u мс  старт -> %s\n", (unsigned)sim_now_ms(),
           pwr_state_name(seq.state));

    for (t = 0u; t < RUN_LIMIT_MS; t += TICK_MS) {
        sim_advance(TICK_MS);
        pwr_seq_tick(&seq, TICK_MS);

        if (seq.state != prev) {
            printf("  %4u мс  %s -> %s\n", (unsigned)sim_now_ms(),
                   pwr_state_name(prev), pwr_state_name(seq.state));
            prev = seq.state;
        }
        /* READY тримаємо ще трохи: аварії ловляться саме в роботі. */
        if (seq.state == PWR_STATE_FAULT) {
            break;
        }
    }

    if (pwr_seq_is_ready(&seq)) {
        printf("  підсумок: живлення підняте, аварій %u\n",
               (unsigned)seq.fault_count);
    } else {
        printf("  підсумок: %s (%s), падінь %u\n",
               pwr_state_name(seq.state), pwr_error_name(seq.last_error),
               (unsigned)seq.fault_count);
    }
    printf("  витік через піни при знеструмленій периферії: %u мс\n",
           (unsigned)sim_leak_ms());

    pwr_seq_shutdown(&seq);
}

int main(void)
{
    static const sim_scenario_t scenarios[] = {
        { "штатне підняття",              false, false,    0u,  0u,  0u },
        { "не піднявся перший ступінь",   true,  false,    0u,  0u,  0u },
        { "не піднявся LDO шини DVDD",    false, true,     0u,  0u,  0u },
        { "кидок струму C_load 1000 мкФ", false, false, 3500u,  0u,  0u },
        { "перевантаження ключа в роботі",false, false,  800u, 40u,  0u },
        { "просів вхід 12 В у роботі",    false, false,  800u,  0u, 60u }
    };
    size_t i;

    for (i = 0u; i < sizeof(scenarios) / sizeof(scenarios[0]); ++i) {
        run_scenario(&scenarios[i]);
    }
    return 0;
}
