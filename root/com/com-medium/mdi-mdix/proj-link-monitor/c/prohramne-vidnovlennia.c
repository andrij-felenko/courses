/* Приклад програмного перезапуску автопогодження на C */
static int restart_autoneg(int fd, const char* ifname) {
    struct ethtool_cmd ecmd;
    memset(&ecmd, 0, sizeof(ecmd));
    ecmd.cmd = ETHTOOL_GSET;

    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);
    ifr.ifr_data = (char*)&ecmd;

    if (ioctl(fd, SIOCETHTOOL, &ifr) < 0) {
        return -1;
    }

    ecmd.cmd = ETHTOOL_SSET;
    ecmd.autoneg = AUTONEG_ENABLE;

    if (ioctl(fd, SIOCETHTOOL, &ifr) < 0) {
        return -1;
    }

    return 0;
}
