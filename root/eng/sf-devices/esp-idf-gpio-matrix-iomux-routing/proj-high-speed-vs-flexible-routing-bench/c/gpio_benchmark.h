#ifndef GPIO_BENCHMARK_H
#define GPIO_BENCHMARK_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    ROUTING_MODE_IOMUX_NATIVE = 0,
    ROUTING_MODE_GPIO_MATRIX
} routing_mode_t;

typedef struct {
    routing_mode_t mode;
    uint32_t frequency_hz;
    uint32_t measured_propagation_delay_ps;
    uint32_t round_trip_error_count;
    bool invert_signal;
} gpio_bench_result_t;

void gpio_bench_init(void);
gpio_bench_result_t gpio_bench_run_spi_test(routing_mode_t mode, uint32_t target_freq_hz, bool invert);
void gpio_bench_print_report(const gpio_bench_result_t *res);

#ifdef __cplusplus
}
#endif

#endif // GPIO_BENCHMARK_H
