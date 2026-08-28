typedef struct {
    char sig[4];                  /* Сигнатура протоколу: "RCmb" (Redis Cluster message bus) */
    uint32_t totlen;              /* Загальна довжина пакета в байтах */
    uint16_t ver;                 /* Версія протоколу кластера (1) */
    uint16_t port;                /* Базовий TCP-порт клієнтських підключень */
    uint16_t type;                /* Тип повідомлення: PING, PONG, MEET, FAIL, PUBLISH */
    uint16_t count;               /* Кількість вкладених блоків Gossip-секції */
    uint64_t currentEpoch;        /* Поточна глобальна епоха конфігурації */
    uint64_t configEpoch;         /* Епоха конфігурації цього конкретного вузла */
    uint64_t offset;              /* Зсув реплікації (Replication Offset) */
    char sender[40];              /* 160-бітний Node ID відправника */
    unsigned char myslots[2048];  /* Бітова маска з 16384 бітів: слоти, закріплені за вузлом */
    char slaveof[40];             /* Node ID майстра (якщо відправник є реплікою) */
    uint16_t my_ip[16];           /* IP-адреса відправника */
    uint16_t pport;               /* Порт TLS (якщо активовано) */
    uint16_t cport;               /* Порт кластерної шини (16379) */
    uint16_t flags;               /* Прапорці вузла: CLUSTER_NODE_MASTER, etc. */
    unsigned char state;          /* Стан кластера: CLUSTER_OK / CLUSTER_FAIL */
    unsigned char mflags[3];      /* Додаткові прапорці повідомлення */
} clusterMsg;
