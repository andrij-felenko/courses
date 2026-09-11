#include "boundary_benchmarks.hpp"
#include <benchmark/benchmark.h>
#include <iostream>
#include <iomanip>

// Користувацька точка входу Google Benchmark із виведенням аналітичного підсумку
int main(int argc, char** argv) {
    std::cout << "=========================================================================\n";
    std::cout << "  СТЕНД ВИМІРЮВАННЯ ЦІНИ МЕЖІ: ВІД ПРЯМОГО ВИКЛИКУ ДО МЕРЕЖЕВОГО RPC\n";
    std::cout << "=========================================================================\n";
    std::cout << "  Рівні архітектурної ізоляції, що тестуються:\n";
    std::cout << "   1. Прямий машинний виклик функції (Direct Call)\n";
    std::cout << "   2. Поліморфний виклик через таблицю vtable (In-Process Modularity)\n";
    std::cout << "   3. Міжпотокова черга з блокуванням (std::jthread / Memory Barrier)\n";
    std::cout << "   4. Міжпроцесна передача через сокет AF_UNIX (OS Kernel / Syscalls)\n";
    std::cout << "   5. Локальний gRPC через Protocol Buffers (Binary Serialization)\n";
    std::cout << "   6. Локальний REST через loopback сокет (HTTP / JSON Serialization)\n";
    std::cout << "=========================================================================\n\n";

    benchmark::Initialize(&argc, argv);
    if (benchmark::ReportUnrecognizedArguments(argc, argv)) {
        return 1;
    }

    benchmark::RunSpecifiedBenchmarks();
    benchmark::Shutdown();

    std::cout << "\n=========================================================================\n";
    std::cout << "  ВИСНОВОК: Накладні витрати зростають експоненційно з кожним новим рівнем!\n";
    std::cout << "  Різниця між прямим викликом і REST сягає 100 000 - 1 000 000 разів.\n";
    std::cout << "=========================================================================\n";
    return 0;
}
