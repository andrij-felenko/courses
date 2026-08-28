#define CANARY 0xDEADBEEFu

void handle_input(const uint8_t *src, uint32_t len) {
    volatile uint32_t guard = CANARY;   /* вартовий перед буфером на стеку */
    uint8_t buf[64];

    memcpy(buf, src, len);              /* НЕБЕЗПЕЧНО, якщо len > 64 */

    if (guard != CANARY)               /* переповнення затерло вартового? */
        fault_handler();               /* ловимо ТУТ, а не за дві години в полі */
}
