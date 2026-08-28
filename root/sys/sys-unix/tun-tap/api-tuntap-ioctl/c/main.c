struct ifreq {
    char ifr_name[IFNAMSIZ]; /* Ім'я інтерфейсу (наприклад, "tun0", "tap1") */
    union {
        short ifru_flags;    /* Прапорці режиму TUN/TAP */
        int   ifru_ivalue;   /* Цілочисельне значення параметрів */
        /* ... інші поля union ... */
    } ifr_ifru;
};

#define ifr_flags ifr_ifru.ifru_flags
