#ifndef ETHERNETIF_H
#define ETHERNETIF_H

#include "lwip/err.h"
#include "lwip/netif.h"

/* Прив'язка драйвера до lwIP: подається в netif_add як ostatній аргумент init. */
err_t ethernetif_init(struct netif *netif);

/* Сигнал «прийшов кадр» із обробника ETH_IRQHandler. Усередині — рівно
   один семафор і жодної роботи з пам'яттю. */
void ethernetif_notify_from_isr(void);

#endif /* ETHERNETIF_H */
