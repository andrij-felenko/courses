struct nvmf_disc_rsp_page_entry {
    uint8_t  trtype;             /* Тип транспорту: 1 = RDMA, 3 = TCP, 4 = FC */
    uint8_t  adrfam;             /* Родина адрес: 1 = IPv4, 2 = IPv6, 3 = IB, 4 = FC */
    uint8_t  subtype;            /* Тип підсистеми: 1 = Discovery, 2 = NVM Subsystem */
    uint8_t  treq;               /* Запити транспорту: Secure channel support */
    uint16_t portid;             /* Номер порту таргета */
    uint16_t cntlid;             /* Ідентифікатор контролера */
    uint16_t asqsz;              /* Максимальний розмір адміністративної черги SQ */
    uint8_t  resv10[22];
    char     trsvcid[32];        /* Рядок сервісного порту, наприклад "4420" */
    uint8_t  resv64[192];
    char     subnqn[256];        /* NQN підсистеми зберігання */
    char     traddr[256];        /* Мережева адреса (наприклад "192.168.1.100") */
    char     tsas[256];          /* Transport Specific Address Subsystem */
};
