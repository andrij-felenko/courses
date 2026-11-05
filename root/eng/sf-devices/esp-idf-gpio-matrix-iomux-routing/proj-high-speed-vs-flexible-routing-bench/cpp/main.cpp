#include <iostream>
#include <iomanip>
#include "gpio_benchmark.hpp"

int main() {
    using namespace esp_bench;

    std::cout << "ESP32 IO_MUX vs GPIO Matrix C++ Benchmark Runner\n";

    auto print_res = [](const BenchmarkResult& r) {
        std::cout << "Mode: " << (r.mode == RoutingMode::IoMuxNative ? "IO_MUX Native" : "GPIO Matrix")
                  << " | Freq: " << (r.frequency_hz / 1000000) << " MHz"
                  << " | Delay: " << std::fixed << std::setprecision(2) << (r.propagation_delay_ps / 1000.0) << " ns"
                  << " | Status: " << (r.is_successful() ? "PASS" : "FAIL") << "\n";
    };

    print_res(RoutingBenchmark::run(RoutingMode::IoMuxNative, 80000000));
    print_res(RoutingBenchmark::run(RoutingMode::GpioMatrix, 40000000));
    print_res(RoutingBenchmark::run(RoutingMode::GpioMatrix, 80000000));

    return 0;
}
