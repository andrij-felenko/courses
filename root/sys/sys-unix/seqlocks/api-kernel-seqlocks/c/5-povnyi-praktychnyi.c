#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/seqlock.h>
#include <linux/netdevice.h>

struct net_device_stats_cpu {
    seqlock_t lock;
    u64 rx_packets;
    u64 rx_bytes;
    u64 tx_packets;
    u64 tx_bytes;
};

static struct net_device_stats_cpu my_stats;

/* Ініціалізація при завантаженні модуля */
static int __init my_module_init(void)
{
    seqlock_init(&my_stats.lock);
    my_stats.rx_packets = 0;
    my_stats.rx_bytes = 0;
    return 0;
}

/* Оновлення статистики. Викликається з обробника переривання мережевої карти,
   а той самий лічильник скидають з контексту процесу (ethtool). */
void my_net_rx_handler(u32 pkt_len)
{
    unsigned long flags;

    /* irqsave потрібен заради виклику з контексту процесу: інакше переривання
       вклинилося б у вже початий запис і навічно застрягло на spin_lock того
       самого замка. У самому обробнику вони й так вимкнені — там irqsave
       лише збереже та відновить прапорці. */
    write_seqlock_irqsave(&my_stats.lock, flags);
    my_stats.rx_packets++;
    my_stats.rx_bytes += pkt_len;
    write_sequnlock_irqrestore(&my_stats.lock, flags);
}

/* Читання статистики у контексті системного виклику (User Context / sysfs) */
void my_get_stats(u64 *packets, u64 *bytes)
{
    unsigned seq;

    /* Оптимістичний цикл читання — не вимикає переривань і не блокує NAPI */
    do {
        seq = read_seqbegin(&my_stats.lock);
        *packets = my_stats.rx_packets;
        *bytes = my_stats.rx_bytes;
    } while (read_seqretry(&my_stats.lock, seq));
}
