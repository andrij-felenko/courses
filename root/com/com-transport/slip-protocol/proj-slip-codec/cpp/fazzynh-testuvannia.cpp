#include <cstdint>
#include <cstddef>
#include <span>
#include <array>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    std::array<uint8_t, 1024> buffer;
    
    SlipDecoder decoder(buffer, [](std::span<const uint8_t> frame) {
        volatile uint8_t checksum = 0;
        for (uint8_t b : frame) {
            checksum ^= b;
        }
        (void)checksum;
    });

    decoder.feed(std::span<const uint8_t>(data, size));
    return 0;
}
