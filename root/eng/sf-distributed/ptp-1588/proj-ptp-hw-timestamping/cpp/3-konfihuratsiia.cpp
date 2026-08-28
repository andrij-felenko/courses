hwtstamp_config hw_cfg{};
hw_cfg.tx_type = HWTSTAMP_TX_ON;
hw_cfg.rx_filter = HWTSTAMP_FILTER_PTP_V2_EVENT;

ifreq ifr{};
std::strncpy(ifr.ifr_name, "eth0", sizeof(ifr.ifr_name) - 1);
ifr.ifr_data = reinterpret_cast<char*>(&hw_cfg);

if (::ioctl(sock_fd, SIOCSHWTSTAMP, &ifr) < 0) {
    std::perror("ioctl SIOCSHWTSTAMP failed");
}
