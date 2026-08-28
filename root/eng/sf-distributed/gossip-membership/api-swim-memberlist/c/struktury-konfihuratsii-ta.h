typedef enum {
    SWIM_NODE_ALIVE   = 0,
    SWIM_NODE_SUSPECT = 1,
    SWIM_NODE_DEAD    = 2,
    SWIM_NODE_LEFT    = 3
} swim_node_status_t;

typedef struct {
    uint32_t ip;                    /* Мережева IPv4-адреса у форматі Network Byte Order */
    uint16_t port;                  /* UDP-порт для обміну дейтаграмами */
    uint64_t incarnation;           /* Поточний номер інкарнації вузла */
    swim_node_status_t status;      /* Поточний статус членства */
    uint64_t state_change_time_ms;  /* Монотонна часова мітка останньої зміни стану */
    uint8_t  suspect_confirmations; /* Кількість незалежних підтверджень підозри */
} swim_member_t;

typedef struct {
    uint32_t bind_ip;               /* Локальна адреса для прив'язки сокета */
    uint16_t bind_port;             /* Локальний порт */
    uint32_t probe_interval_ms;     /* Інтервал між раундами зондування (T_probe) */
    uint32_t probe_timeout_ms;      /* Таймаут прямої відповіді (T_ack) */
    uint32_t indirect_checks_k;     /* Кількість посередників для непрямих перевірок */
    uint32_t suspicion_multiplier;  /* Множник розрахунку максимального часу підозри */
    uint32_t retransmit_multiplier; /* Множник кількості повторних передач плітки */
    
    /* Колбеки сповіщення прикладного коду про зміну топології */
    void (*on_node_join)(const swim_member_t *member, void *userdata);
    void (*on_node_leave)(const swim_member_t *member, void *userdata);
    void (*on_node_failed)(const swim_member_t *member, void *userdata);
    void (*on_user_message)(const uint8_t *data, size_t len, void *userdata);
    void *userdata;                 /* Користувацький контекст для передачі в колбеки */
} swim_config_t;
