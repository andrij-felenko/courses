#include <stdio.h>
#include <stdbool.h>
#include <math.h>

/* Фізичні характеристики середовища передачі */
typedef enum {
    PCB_FR4_MICROSTRIP, /* Зовнішні шари друкованої плати: ~5.96 нс/м */
    PCB_FR4_STRIPLINE,   /* Внутрішні шари друкованої плати: ~6.91 нс/м */
    RIBBON_CABLE_PVC,   /* Плаский стрічковий кабель: ~5.48 нс/м */
    TWISTED_PAIR_PE     /* Вита пара з поліетиленом: ~5.00 нс/м */
} DielectricType;

/* Параметри ведучого контролера (Master) */
typedef struct {
    double t_su_ns;     /* Необхідний час встановлення MISO (Setup Time) */
    double t_h_ns;      /* Необхідний час утримання MISO (Hold Time) */
    double t_co_ns;     /* Вихідна затримка формування MOSI (Clock-to-Out) */
    double t_skew_ns;   /* Внутрішній перекіс фази такту / джиттер */
    bool has_sample_shift; /* Чи підтримує контролер зсув вибірки на повний такт */
} SpiMasterParams;

/* Параметри веденого пристрою (Slave) */
typedef struct {
    double t_su_ns;     /* Необхідний час встановлення MOSI (Setup Time) */
    double t_h_ns;      /* Необхідний час утримання MOSI (Hold Time) */
    double t_v_max_ns;  /* Максимальна затримка виходу MISO (Data Valid) */
    double t_v_min_ns;  /* Мінімальна затримка виходу MISO */
} SpiSlaveParams;

/* Параметри фізичної лінії зв'язку */
typedef struct {
    double length_meters;       /* Довжина лінії в метрах */
    DielectricType dielectric;  /* Тип діелектрика */
    double isolator_prop_delay; /* Затримка одного каналу ізолятора / буфера (нс) */
    double rise_time_ns;        /* Час наростання фронтів (10%-90%) */
} SpiChannelParams;

/* Результати аналізу часових запасів */
typedef struct {
    double target_freq_mhz;
    double period_ns;
    double t_prop_single_ns;
    double total_active_delay_ns;
    double round_trip_delay_ns;
    
    double margin_su_write_ns;
    double margin_su_read_ns;
    double margin_h_read_ns;
    
    double max_freq_write_mhz;
    double max_freq_read_cpha0_mhz;
    double max_freq_read_shifted_mhz;
    
    bool write_ok;
    bool read_ok;
    bool hold_ok;
} SpiTimingResult;

/* Обчислення питомої затримки поширення на метр */
static double get_dielectric_propagation_ns_per_m(DielectricType d) {
    switch (d) {
        case PCB_FR4_MICROSTRIP: return 5.96;
        case PCB_FR4_STRIPLINE:   return 6.91;
        case RIBBON_CABLE_PVC:   return 5.48;
        case TWISTED_PAIR_PE:     return 5.00;
        default:                  return 6.00;
    }
}

/* Основна функція розрахунку часового бюджету */
bool spi_calculate_timing(
    const SpiMasterParams* master,
    const SpiSlaveParams* slave,
    const SpiChannelParams* channel,
    double target_freq_mhz,
    SpiTimingResult* result
) {
    if (!master || !slave || !channel || !result || target_freq_mhz <= 0.0) {
        return false;
    }

    result->target_freq_mhz = target_freq_mhz;
    result->period_ns = 1000.0 / target_freq_mhz;
    double half_period_ns = result->period_ns / 2.0;

    /* 1. Затримка в лінії передачі */
    double tau = get_dielectric_propagation_ns_per_m(channel->dielectric);
    result->t_prop_single_ns = channel->length_meters * tau;
    result->total_active_delay_ns = channel->isolator_prop_delay * 2.0; /* SCLK + MISO */

    /* 2. Повна затримка кругового циклу читання */
    result->round_trip_delay_ns = (2.0 * result->t_prop_single_ns) + 
                                  result->total_active_delay_ns + 
                                  slave->t_v_max_ns;

    /* 3. Часовий запас запису (Master -> Slave) */
    double t_write_arrival = master->t_co_ns + result->t_prop_single_ns + 
                             channel->isolator_prop_delay + master->t_skew_ns;
    result->margin_su_write_ns = half_period_ns - t_write_arrival - slave->t_su_ns;
    result->write_ok = (result->margin_su_write_ns >= 0.0);

    /* 4. Часовий запас читання (Slave -> Master) */
    if (master->has_sample_shift) {
        result->margin_su_read_ns = result->period_ns - result->round_trip_delay_ns - master->t_su_ns;
    } else {
        result->margin_su_read_ns = half_period_ns - result->round_trip_delay_ns - master->t_su_ns;
    }
    result->read_ok = (result->margin_su_read_ns >= 0.0);

    /* 5. Часовий запас утримання під час читання */
    double t_hold_arrival = (2.0 * result->t_prop_single_ns) + 
                            result->total_active_delay_ns + 
                            slave->t_v_min_ns;
    result->margin_h_read_ns = t_hold_arrival - master->t_h_ns;
    result->hold_ok = (result->margin_h_read_ns >= 0.0);

    /* 6. Граничні частоти за різними критеріями */
    double t_min_write_period = 2.0 * (t_write_arrival + slave->t_su_ns);
    result->max_freq_write_mhz = 1000.0 / t_min_write_period;

    double t_min_read_cpha0 = 2.0 * (result->round_trip_delay_ns + master->t_su_ns);
    result->max_freq_read_cpha0_mhz = 1000.0 / t_min_read_cpha0;

    double t_min_read_shifted = result->round_trip_delay_ns + master->t_su_ns;
    result->max_freq_read_shifted_mhz = 1000.0 / t_min_read_shifted;

    return true;
}

void spi_print_report(const SpiTimingResult* r) {
    printf("=================================================================\n");
    printf("           ЗВІТ ЧАСОВОГО БАЛАНСУ ШИНИ SPI (%.2f МГц)\n", r->target_freq_mhz);
    printf("=================================================================\n");
    printf("Період такту T_CLK          : %.2f нс (Напівперіод: %.2f нс)\n", r->period_ns, r->period_ns / 2.0);
    printf("Затримка провідника (t_prop): %.2f нс (в один бік)\n", r->t_prop_single_ns);
    printf("Затримка ізоляторів (сума)  : %.2f нс (прямий + зворотний)\n", r->total_active_delay_ns);
    printf("Кругова затримка читання    : %.2f нс (2*t_prop + t_iso + t_V)\n", r->round_trip_delay_ns);
    printf("-----------------------------------------------------------------\n");
    printf("ТРАКТ ЗАПИСУ (MOSI):\n");
    printf("  Запас встановлення (Setup Margin) : %+6.2f нс -> [%s]\n", 
           r->margin_su_write_ns, r->write_ok ? "ДОПУСТИМО" : "ПОМИЛКА (METASTABLE)");
    printf("  Максимальна частота запису        :  %.2f МГц\n", r->max_freq_write_mhz);
    printf("-----------------------------------------------------------------\n");
    printf("ТРАКТ ЧИТАННЯ (MISO):\n");
    printf("  Запас встановлення (Setup Margin) : %+6.2f нс -> [%s]\n", 
           r->margin_su_read_ns, r->read_ok ? "ДОПУСТИМО" : "ПОМИЛКА (TIMING VIOLATION)");
    printf("  Запас утримання (Hold Margin)     : %+6.2f нс -> [%s]\n", 
           r->margin_h_read_ns, r->hold_ok ? "ДОПУСТИМО" : "ПОМИЛКА (HOLD VIOLATION)");
    printf("  Гранична частота (CPHA=0 стандарт):  %.2f МГц\n", r->max_freq_read_cpha0_mhz);
    printf("  Гранична частота (Sample Shifted) :  %.2f МГц\n", r->max_freq_read_shifted_mhz);
    printf("=================================================================\n");
}

int main(void) {
    SpiMasterParams stm32 = {
        .t_su_ns = 4.5,
        .t_h_ns = 2.0,
        .t_co_ns = 6.0,
        .t_skew_ns = 1.0,
        .has_sample_shift = false
    };

    SpiSlaveParams flash_w25q = {
        .t_su_ns = 3.0,
        .t_h_ns = 2.0,
        .t_v_max_ns = 8.0,
        .t_v_min_ns = 1.5
    };

    SpiChannelParams cable = {
        .length_meters = 0.25,
        .dielectric = RIBBON_CABLE_PVC,
        .isolator_prop_delay = 10.7,
        .rise_time_ns = 3.0
    };

    SpiTimingResult result;
    if (spi_calculate_timing(&stm32, &flash_w25q, &cable, 20.0, &result)) {
        spi_print_report(&result);
    }

    return 0;
}
