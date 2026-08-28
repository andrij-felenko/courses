typedef union {
    volatile uint32_t word;          // погляд 1: ціле слово (завжди чесне)
    struct {
        volatile uint32_t rxfifo_cnt : 8;   // погляд 2: поля
        volatile uint32_t st_urx_out : 4;   // (порядок — на цьому компіляторі)
        volatile uint32_t _rsvd0     : 1;
        volatile uint32_t dsrn       : 1;
        volatile uint32_t ctsn       : 1;
        volatile uint32_t rxd        : 1;
        volatile uint32_t txfifo_cnt : 8;
        volatile uint32_t st_utx_out : 4;
        volatile uint32_t _rsvd1     : 1;
        volatile uint32_t dtrn       : 1;
        volatile uint32_t rtsn       : 1;
        volatile uint32_t txd        : 1;
    };                               // анонімна — поля вливаються в union
} UartStatus;                        // sizeof == 4: слово й біти на одній пам'яті
