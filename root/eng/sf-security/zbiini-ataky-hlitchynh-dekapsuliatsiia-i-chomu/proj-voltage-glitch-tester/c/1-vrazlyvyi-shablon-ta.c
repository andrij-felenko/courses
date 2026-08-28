/* Вразлива реалізація: вразлива до пропуску однієї інструкції BEQ */
bool verify_firmware_signature(const uint8_t *image, size_t len) {
    if (crypto_rsa_verify(image, len) == true) {
        return true;
    }
    return false;
}

void bootloader_main(void) {
    if (verify_firmware_signature(FW_ADDR, FW_SIZE)) {
        boot_kernel(); /* Зловмисник подає глітч і запускає шкідливий образ */
    } else {
        lockup_device();
    }
}
