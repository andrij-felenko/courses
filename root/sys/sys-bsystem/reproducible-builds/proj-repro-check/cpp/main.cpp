// main.cpp
#include "calc.hpp"
#include <iostream>
#include <iomanip>

int main() {
    calc::print_build_banner();
    constexpr std::string_view msg = "Reproducible Builds Test";
    const int res = calc::calculate_checksum(msg);
    std::cout << "Checksum result: 0x"
              << std::hex << std::uppercase << std::setfill('0') << std::setw(8)
              << res << "\n";
    return 0;
}
