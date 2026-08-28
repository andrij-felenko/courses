struct fib_result {
    __be32          prefix;       /* Префікс адреси */
    unsigned char   prefixlen;    /* Довжина маски префіксу */
    unsigned char   nh_sel;       /* Обраний індекс next-hop у масиві ECMP */
    unsigned char   type;         /* Тип маршруту (RTN_UNICAST тощо) */
    unsigned char   scope;        /* Область видимості */
    u32             tclassid;     /* Клас трафіку для QOS */
    struct fib_info *fi;          /* Знайдена структура fib_info */
    struct fib_table *table;      /* Знайдена таблиця маршрутизації */
};
