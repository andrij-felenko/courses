/* Кільце з двох дескрипторів — основа ping-pong потоку */
static dma_desc_t descs[2];
static uint8_t buf_a[BUF_SIZE] __attribute__((aligned(32)));
static uint8_t buf_b[BUF_SIZE] __attribute__((aligned(32)));

void dma_ring_init(void) {
    descs[0].owner  = 1;          /* віддаємо буфер DMA */
    descs[0].eof    = 1;          /* переривання після цього буфера */
    descs[0].length = 0;          /* приймання заповнить саме */
    descs[0].size   = BUF_SIZE;
    descs[0].buf    = buf_a;
    descs[0].next   = &descs[1];  /* → другий вузол */

    descs[1].owner  = 1;
    descs[1].eof    = 1;
    descs[1].length = 0;
    descs[1].size   = BUF_SIZE;
    descs[1].buf    = buf_b;
    descs[1].next   = &descs[0];  /* → назад у перший: кільце замкнулось */
}
