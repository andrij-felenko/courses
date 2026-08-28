#include <rte_ethdev.h>

// 1. Активація апаратного таймстемпінгу на порту:
rte_eth_timesync_enable(port_id);

// 2. Зчитування апаратної мітки вхідного пакета:
struct timespec rx_ts;
rte_eth_timesync_read_rx_timestamp(port_id, &rx_ts, pkt_flags);

// 3. Зчитування мітки передавача після відправки:
struct timespec tx_ts;
rte_eth_timesync_read_tx_timestamp(port_id, &tx_ts);

// 4. Пряме підстроювання апаратного годинника карти:
rte_eth_timesync_adjust_time(port_id, delta_nanoseconds);
