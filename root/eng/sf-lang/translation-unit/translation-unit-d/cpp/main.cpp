// main.cpp
#include <iostream>
#include <span>
#include <vector>
#include <cstdint>

extern int g_operation_count;
extern int calculate_checksum(std::span<const uint8_t> data) noexcept;

int main() {
    std::vector<uint8_t> buffer = {1, 2, 3, 4};
    int cs = calculate_checksum(buffer);
    std::cout << "Checksum: " << cs << ", Ops: " << g_operation_count << "\n";
    return 0;
}
