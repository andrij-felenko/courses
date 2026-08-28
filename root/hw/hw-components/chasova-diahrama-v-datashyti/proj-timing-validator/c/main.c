#include <stdio.h>
#include <stdbool.h>
#include <math.h>

/* Паспортні часові параметри вихідного каскаду передавача (нс) */
typedef struct {
    double t_co_min_ns;  /* Найшвидший відгук (Fast corner / Low Temp) */
    double t_co_max_ns;  /* Найповільніший відгук (Slow corner / High Temp) */
} TransmitterTiming;

/* Паспортні вимоги вхідного тригера приймача (нс) */
typedef struct {
    double t_setup_ns;   /* Мінімально необхідний час встановлення */
    double t_hold_ns;    /* Мінімально необхідний час утримання */
} ReceiverTiming;

/* Фізичні параметри друкованої плати та джерела тактування */
typedef struct {
    double trace_length_mm;  /* Довжина провідника на платі (мм) */
    double ps_per_mm;        /* Питома затримка (FR-4 microstrip: ~6.5 пс/мм) */
    double clock_freq_mhz;   /* Робоча тактова частота (МГц) */
    double clock_skew_ns;    /* Перекіс тактових ліній між чіпами */
    double clock_jitter_ns;  /* Фазове тремтіння тактового сигналу */
} InterconnectParams;

/* Результати розрахунку часового бюджету */
typedef struct {
    double t_flight_ns;       /* Час поширення хвилі по трасі PCB */
    double setup_slack_ns;    /* Запас за часом встановлення */
    double hold_slack_ns;     /* Запас за часом утримання */
    double max_safe_freq_mhz; /* Максимальна розрахункова частота */
    bool setup_passed;        /* Чи виконується вимога встановлення */
    bool hold_passed;         /* Чи виконується вимога утримання */
} TimingResult;

/* Функція обчислення часового бюджету синхронної шини */
TimingResult validate_bus_timing(
    const TransmitterTiming *tx,
    const ReceiverTiming *rx,
    const InterconnectParams *bus
) {
    TimingResult res;
    double t_period_ns = 1000.0 / bus->clock_freq_mhz;
    
    /* 1. Розрахунок часу польоту сигналу: t_flight = length · delay_per_mm */
    res.t_flight_ns = (bus->trace_length_mm * bus->ps_per_mm) / 1000.0;
    
    /* 2. Запас за встановленням:
       Slack = T_clk - (t_co_max + t_flight + t_setup + t_skew + t_jitter) */
    double total_setup_path = tx->t_co_max_ns + res.t_flight_ns + rx->t_setup_ns 
                            + bus->clock_skew_ns + bus->clock_jitter_ns;
    res.setup_slack_ns = t_period_ns - total_setup_path;
    res.setup_passed = (res.setup_slack_ns >= 0.0);
    
    /* 3. Запас за утриманням:
       Slack = (t_co_min + t_flight) - (t_hold + t_skew) */
    double min_data_arrival = tx->t_co_min_ns + res.t_flight_ns;
    double hold_required = rx->t_hold_ns + bus->clock_skew_ns;
    res.hold_slack_ns = min_data_arrival - hold_required;
    res.hold_passed = (res.hold_slack_ns >= 0.0);
    
    /* 4. Теоретична максимальна частота, обмежена встановленням */
    if (total_setup_path > 0.0) {
        res.max_safe_freq_mhz = 1000.0 / total_setup_path;
    } else {
        res.max_safe_freq_mhz = 0.0;
    }
    
    return res;
}

int main(void) {
    /* Тестовий випадок: SPI NOR Flash W25Q128JV та мікроконтролер STM32H7 */
    TransmitterTiming flash_tx = {
        .t_co_min_ns = 1.5,
        .t_co_max_ns = 7.0
    };
    
    ReceiverTiming mcu_rx = {
        .t_setup_ns = 3.5,
        .t_hold_ns = 1.0
    };
    
    InterconnectParams pcb = {
        .trace_length_mm = 80.0,
        .ps_per_mm = 6.5,
        .clock_freq_mhz = 60.0,
        .clock_skew_ns = 0.4,
        .clock_jitter_ns = 0.3
    };
    
    TimingResult r = validate_bus_timing(&flash_tx, &mcu_rx, &pcb);
    
    printf("=== ВАЛІДАЦІЯ ЧАСОВОГО БЮДЖЕТУ ШИНИ (C) ===\n");
    printf("Затримка траси плати:       %.3f нс\n", r.t_flight_ns);
    printf("Запас Setup (встановлення): %.3f нс [%s]\n", 
           r.setup_slack_ns, r.setup_passed ? "PASS" : "FAIL");
    printf("Запас Hold (утримання):     %.3f нс [%s]\n", 
           r.hold_slack_ns, r.hold_passed ? "PASS" : "FAIL");
    printf("Максимальна частота шини:   %.2f МГц\n", r.max_safe_freq_mhz);
    
    return 0;
}
