#include "platform.h"
#include "cmd_proto.h"

#include <stdio.h>
#include <string.h>

static uint32_t g_uptime_ms = 0;
static uint8_t  g_nvm[PLAT_NVM_SIZE];   /* «FRAM»: не чіпається скиданням живлення */

uint32_t plat_now_ms(void) {
    return g_uptime_ms;
}

void plat_advance_ms(uint32_t dt_ms) {
    g_uptime_ms += dt_ms;
}

void plat_nvm_read(uint8_t *dst) {
    memcpy(dst, g_nvm, PLAT_NVM_SIZE);
}

void plat_nvm_write(const uint8_t *src) {
    memcpy(g_nvm, src, PLAT_NVM_SIZE);
}

void plat_uplink_send(const uint8_t *frame, size_t len) {
    ack_t a;
    if (!wire_parse_ack(frame, len, &a)) {
        printf("      <-- [битий кадр квитанції, %u байт]\n", (unsigned)len);
        return;
    }
    printf("      <-- ACK ф%u  %-9s  token=0x%08lX  %s  detail=%ld  (%u B, t=%u мс)\n",
           (unsigned)a.phase,
           cmd_state_name(a.state),
           (unsigned long)(a.token & 0xFFFFFFFFu),
           cmd_err_name(a.result),
           (long)a.detail,
           (unsigned)len,
           (unsigned)g_uptime_ms);
}

void plat_power_cycle(void) {
    printf("\n  ~~~ ЗНИКЛО ЖИВЛЕННЯ: SRAM очищено, монотонний час скинуто, FRAM цілий ~~~\n");
    g_uptime_ms = 0;
}

void plat_banner(const char *text) {
    printf("\n=== %s ===\n", text);
}
