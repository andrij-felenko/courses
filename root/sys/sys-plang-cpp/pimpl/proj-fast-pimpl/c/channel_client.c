/* ==================== C: channel_client.c ==================== */
#include "channel.h"
#include <stdio.h>
#include <string.h>

void run_client(void) {
    /* Створення об'єкта на стеку без жодного виклику malloc! */
    SecureChannel chan;
    
    if (secure_channel_init(&chan, "192.168.1.100", 4433) == 0) {
        const char msg[] = "PING_PAYLOAD";
        secure_channel_send(&chan, msg, strlen(msg));
        secure_channel_destroy(&chan);
    }
}
