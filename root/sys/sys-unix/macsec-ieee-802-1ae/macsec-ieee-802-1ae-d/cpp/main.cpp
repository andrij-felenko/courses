// C++-інтерфейс обгортки драйвера апаратного розвантаження (Offload Interface)
struct IMacsecOffloadOps {
    virtual ~IMacsecOffloadOps() = default;
    virtual int dev_open(void* ctx) = 0;
    virtual int dev_stop(void* ctx) = 0;
    virtual int add_rx_sc(void* ctx) = 0;
    virtual int add_rx_sa(void* ctx) = 0;
    virtual int add_tx_sa(void* ctx) = 0;
    virtual int del_tx_sa(void* ctx) = 0;
};
