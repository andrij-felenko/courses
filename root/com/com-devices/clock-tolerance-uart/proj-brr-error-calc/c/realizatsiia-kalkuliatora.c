#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Тип джерела тактування вузла */
typedef enum {
    CLK_SOURCE_CRYSTAL_XTAL,  /* Кварцовий резонатор (±30 ppm) */
    CLK_SOURCE_CERAMIC_RES,   /* Керамічний резонатор (±0.5%) */
    CLK_SOURCE_INTERNAL_RC    /* Внутрішній RC-генератор (±2.5%) */
} clock_source_t;

/* Формат кадру UART */
typedef enum {
    UART_FRAME_8N1,           /* 10 бітів: Start, 8 Data, Stop */
    UART_FRAME_8E1_8O1_8N2,   /* 11 бітів: Start, 8 Data, Parity, Stop */
    UART_FRAME_9E1            /* 12 бітів: Start, 9 Data, Parity, Stop */
} uart_frame_format_t;

/* Результат розрахунку регістра BRR */
typedef struct {
    uint32_t mantissa;
    uint32_t fraction;
    uint32_t brr_reg_value;
    double actual_baud;
    double brr_error_percent;
    double total_system_error;
    double max_allowable_error;
    bool is_communication_reliable;
} uart_brr_calc_result_t;

/* Повертає типову нестабільність генератора у відсотках */
static double get_clock_drift_percent(clock_source_t source) {
    switch (source) {
        case CLK_SOURCE_CRYSTAL_XTAL: return 0.005; /* ±50 ppm */
        case CLK_SOURCE_CERAMIC_RES:  return 0.500; /* ±0.5% */
        case CLK_SOURCE_INTERNAL_RC:  return 2.500; /* ±2.5% */
        default:                      return 1.000;
    }
}

/* Повертає максимальну допустиму сумарну похибку для заданого формату кадру */
static double get_max_allowable_error(uart_frame_format_t format, uint32_t oversampling) {
    double n_bits;
    switch (format) {
        case UART_FRAME_8N1:         n_bits = 10.0; break;
        case UART_FRAME_8E1_8O1_8N2: n_bits = 11.0; break;
        case UART_FRAME_9E1:         n_bits = 12.0; break;
        default:                     n_bits = 10.0; break;
    }

    /* Ефективне напіввікно з урахуванням квантування старт-біта та апертури фільтра */
    double w_eff = (oversampling == 16) ? 0.40625 : 0.31250;
    return (w_eff / (n_bits - 0.5)) * 100.0;
}

/* Розрахунок параметрів регістра BRR та верифікація сумарної похибки */
bool calculate_uart_brr(uint32_t pclk_hz,
                        uint32_t target_baud,
                        uint32_t oversampling,
                        uint32_t fract_bits,
                        clock_source_t tx_clk,
                        clock_source_t rx_clk,
                        uart_frame_format_t frame_format,
                        uart_brr_calc_result_t *out_result) {
    if (out_result == NULL || pclk_hz == 0 || target_baud == 0) {
        return false;
    }
    if (oversampling != 8 && oversampling != 16) {
        return false;
    }

    /* 1. Ідеальний коефіцієнт ділення */
    double div_exact = (double)pclk_hz / ((double)oversampling * (double)target_baud);
    if (div_exact < 1.0) {
        /* Частота PCLK занизька для цієї швидкості */
        return false;
    }

    /* 2. Квантування у форматі з фіксованою комою */
    uint32_t fract_scale = 1u << fract_bits;
    uint32_t div_scaled = (uint32_t)round(div_exact * (double)fract_scale);

    out_result->mantissa = div_scaled >> fract_bits;
    out_result->fraction = div_scaled & (fract_scale - 1u);

    if (out_result->mantissa == 0) {
        return false;
    }

    /* Формування значення апаратного регістра (наприклад, USART_BRR для STM32) */
    out_result->brr_reg_value = (out_result->mantissa << fract_bits) | out_result->fraction;

    /* 3. Фактично згенерована швидкість та похибка квантування */
    double div_actual = (double)out_result->mantissa + ((double)out_result->fraction / (double)fract_scale);
    out_result->actual_baud = (double)pclk_hz / ((double)oversampling * div_actual);
    out_result->brr_error_percent = ((out_result->actual_baud - (double)target_baud) / (double)target_baud) * 100.0;

    /* 4. Сумарний розрахунок бюджету похибки */
    double tx_drift = get_clock_drift_percent(tx_clk);
    double rx_drift = get_clock_drift_percent(rx_clk);

    /* Сума похибок: дільник + генератор TX + генератор RX */
    out_result->total_system_error = fabs(out_result->brr_error_percent) + tx_drift + rx_drift;
    out_result->max_allowable_error = get_max_allowable_error(frame_format, oversampling);

    /* Запас надійності: система стабільна, якщо сумарна похибка нижча за критичну межу */
    out_result->is_communication_reliable = (out_result->total_system_error <= out_result->max_allowable_error);

    return true;
}

/* Друк розгорнутого звіту розрахунку */
void print_uart_report(const uart_brr_calc_result_t *res, uint32_t pclk, uint32_t target_baud) {
    printf("============================================================\n");
    printf(" ЗВІТ РОЗРАХУНКУ ТАКТУВАННЯ ТА БЮДЖЕТУ ПОХИБКИ UART\n");
    printf("============================================================\n");
    printf(" Тактова частота PCLK     : %u Гц (%.3f МГц)\n", pclk, pclk / 1e6);
    printf(" Цільова швидкість (Baud) : %u бод\n", target_baud);
    printf(" Мантиса дільника         : %u\n", res->mantissa);
    printf(" Дробова частина          : %u / 16 (0x%X)\n", res->fraction, res->fraction);
    printf(" Регістр USART_BRR        : 0x%04X\n", res->brr_reg_value);
    printf(" Фактична швидкість       : %.2f бод\n", res->actual_baud);
    printf(" Похибка дільника BRR     : %+.3f %%\n", res->brr_error_percent);
    printf(" Сумарна похибка системи  : %.3f %%\n", res->total_system_error);
    printf(" Гранично допустима межа  : %.3f %%\n", res->max_allowable_error);
    printf("------------------------------------------------------------\n");
    if (res->is_communication_reliable) {
        printf(" ВЕРДИКТ: [ НАДІЙНО ] Зв'язок гарантовано стабільний.\n");
    } else {
        printf(" ВЕРДИКТ: [ НЕБЕЗПЕКА ] Ризик Framing Error! Перевищено допуск.\n");
    }
    printf("============================================================\n\n");
}
