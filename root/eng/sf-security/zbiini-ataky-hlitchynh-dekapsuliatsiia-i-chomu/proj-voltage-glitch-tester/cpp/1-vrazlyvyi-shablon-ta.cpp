/* Вразлива реалізація на C++ */
#include <cstdint>
#include <span>

bool verify_firmware_signature(std::span<const uint8_t> image) {
    return crypto_rsa_verify(image.data(), image.size());
}

void bootloader_main() {
    if (verify_firmware_signature({FW_ADDR, FW_SIZE})) {
        boot_kernel(); /* Одиничний збій у ALU оминає умову */
    } else {
        lockup_device();
    }
}
