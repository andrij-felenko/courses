struct cipher_testvec {
    const char *key;      /* Байт-масив ключа */
    const char *p;        /* Відкритий текст (Plaintext) */
    const char *c;        /* Очікуваний шифротекст (Ciphertext) */
    const char *iv;       /* Вектор ініціалізації (IV) */
    unsigned char klen;   /* Довжина ключа в байтах */
    unsigned short plen;  /* Довжина відкритого тексту */
    unsigned short clen;  /* Довжина шифротексту */
    bool fail;            /* Ознака негативного тесту (має відхилятися) */
    unsigned char wk;     /* Прапорець слабкого ключа (weak key) */
};

struct hash_testvec {
    const char *key;      /* Ключ для HMAC (NULL для чистого гешу) */
    const char *plaintext;/* Вхідні дані для гешування */
    const char *digest;   /* Очікуваний дайджест */
    unsigned short psize; /* Довжина вхідних даних */
    unsigned char ksize;  /* Довжина ключа HMAC */
};

struct drbg_state {
    spinlock_t lock;
    unsigned char *v;               /* Внутрішній вектор стану DRBG V */
    unsigned char *c;               /* Константа C (для Hash_DRBG) */
    void *priv_data;                /* Дані контексту шифру чи гешу */
    size_t reseed_threshold;        /* Поріг ресідінгу (максимум операцій до оновлення) */
    size_t reseed_ctr;              /* Лічильник згенерованих блоків від останнього ресіду */
    const struct drbg_core *core;   /* Вказівник на специфікацію рушія */
    bool seeded;                    /* Ознака успішної ініціалізації ентропією */
    bool pr;                        /* Прапорець Prediction Resistance */
};
