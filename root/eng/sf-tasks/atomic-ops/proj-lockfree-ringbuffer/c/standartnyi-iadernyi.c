#include <linux/kfifo.h>

// Оголошення kfifo на 64 елементи; сама структура ще не готова до вжитку —
// перед першим kfifo_put() її треба один раз ініціалізувати INIT_KFIFO(my_fifo)
DECLARE_KFIFO(my_fifo, struct my_packet, 64);

void producer_work(struct my_packet *pkt)
{
    // Атомарно пушить елемент у kfifo без блокувань (SPSC)
    kfifo_put(&my_fifo, *pkt);
}

bool consumer_work(struct my_packet *out_pkt)
{
    // Атомарно витягує елемент з kfifo
    return kfifo_get(&my_fifo, out_pkt);
}
