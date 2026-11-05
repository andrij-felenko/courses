#include <stdio.h>
#include "gpio_benchmark.h"

int main(void) {
    gpio_bench_init();

    printf("ESP-IDF High-Speed vs Flexible Routing Benchmark\n");

    // Case 1: 80 MHz on IO_MUX Native Pins
    gpio_bench_result_t r1 = gpio_bench_run_spi_test(ROUTING_MODE_IOMUX_NATIVE, 80000000, false);
    gpio_bench_print_report(&r1);

    // Case 2: 40 MHz on GPIO Matrix Pins
    gpio_bench_result_t r2 = gpio_bench_run_spi_test(ROUTING_MODE_GPIO_MATRIX, 40000000, false);
    gpio_bench_print_report(&r2);

    // Case 3: 80 MHz on GPIO Matrix Pins (Exceeding matrix limit)
    gpio_bench_result_t r3 = gpio_bench_run_spi_test(ROUTING_MODE_GPIO_MATRIX, 80000000, false);
    gpio_bench_print_report(&r3);

    return 0;
}
