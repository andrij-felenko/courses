struct sk_buff {
    /* ... метадані ... */
    struct net_device *dev; // Пристрій, до якого належить пакет
    
    /* Вказівники на буфер даних */
    unsigned char *head;  // Початок виділеної пам'яті
    unsigned char *data;  // Початок поточних корисних даних (напр. TCP-заголовок)
    unsigned char *tail;  // Кінець поточних корисних даних
    unsigned char *end;   // Кінець виділеної пам'яті
};

// При відправленні: додаємо заголовок (зсуваємо data назад)
skb_push(skb, sizeof(struct iphdr)); 

// При отриманні: знімаємо заголовок (зсуваємо data вперед)
skb_pull(skb, sizeof(struct ethhdr));
