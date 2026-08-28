// --- test_harness.c: збирає вихід у буфер замість заліза ---
static uint8_t  cap_buf[512];
static size_t   cap_len;

void hw_tx(const uint8_t *bytes, size_t n) {   // підміна на час тесту
    for (size_t i = 0; i < n && cap_len < sizeof cap_buf; i++)
        cap_buf[cap_len++] = bytes[i];
}

static void snapshot(const char *label,
                     const uint8_t *payload, size_t len,
                     bool crc, bool comp, bool be) {
    cap_len = 0;                                // чистимо буфер
    send_frame(payload, len, crc, comp, be);    // ← поточна реалізація
    // друкуємо label + hex(cap_buf[0..cap_len]) — це і є "золотий" відбиток
    print_hex(label, cap_buf, cap_len);
}

int main(void) {
    uint8_t msg[] = { 0x10, 0x20, 0x30 };
    snapshot("raw",  msg, sizeof msg, false, false, false);
    snapshot("crc",  msg, sizeof msg, true,  false, false);
    snapshot("comp", msg, sizeof msg, false, true,  false);
    snapshot("be",   msg, sizeof msg, true,  false, true);
    return 0;
}
