struct hwtstamp_config hw_cfg;
memset(&hw_cfg, 0, sizeof(hw_cfg));

// Увімкнути генерацію апаратних міток для всіх вихідних кадрів (TX)
hw_cfg.tx_type = HWTSTAMP_TX_ON;

// Налаштувати апаратний фільтр прийому (RX) на перехоплення PTPv2 Event пакетів
hw_cfg.rx_filter = HWTSTAMP_FILTER_PTP_V2_EVENT;

struct ifreq ifr;
memset(&ifr, 0, sizeof(ifr));
strncpy(ifr.ifr_name, "eth0", sizeof(ifr.ifr_name) - 1);
ifr.ifr_data = (char *)&hw_cfg;

if (ioctl(sock_fd, SIOCSHWTSTAMP, &ifr) < 0) {
    perror("ioctl SIOCSHWTSTAMP failed");
}
