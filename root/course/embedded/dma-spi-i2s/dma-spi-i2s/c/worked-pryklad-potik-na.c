#include "driver/spi_master.h"

static spi_device_handle_t dev;
static uint16_t *fb[2];          /* два DMA-придатні буфери */

/* поставити блок у чергу — виклик не блокує, DMA жене сам */
static void send_chunk(uint16_t *buf, int pixels) {
    static spi_transaction_t t;
    t = (spi_transaction_t){ .length = pixels * 16, .tx_buffer = buf };
    spi_device_queue_trans(dev, &t, portMAX_DELAY);
}

/* дочекатися, поки попередній блок долетів */
static void wait_chunk(void) {
    spi_transaction_t *res;
    spi_device_get_trans_result(dev, &res, portMAX_DELAY);
}

void flush_frame(void (*render)(uint16_t *buf, int y)) {
    int cur = 0;
    render(fb[cur], 0);                  /* перший буфер — поки DMA стоїть */
    for (int y = 0; y < 240; y += 16) {
        send_chunk(fb[cur], 240 * 16);   /* DMA жене fb[cur] у шину */
        int next = cur ^ 1;
        if (y + 16 < 240)
            render(fb[next], y + 16);     /* ядро малює fb[next] паралельно */
        wait_chunk();                     /* цей блок долетів — буфер вільний */
        cur = next;
    }
}
