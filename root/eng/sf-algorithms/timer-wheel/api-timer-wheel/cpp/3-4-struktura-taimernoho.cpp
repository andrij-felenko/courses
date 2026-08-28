struct timer_wheel_s {
    timer_tick_t     current_tick; /* Поточний системний час у тіках */
    uint32_t         timer_count;  /* Активна кількість таймерів у системі */
    
    /* Слоти ієрархічних коліс */
    timer_node_t    *tv1[256];     /* Колесо 1: 256 слотів (8 бітів) */
    timer_node_t    *tv2[64];      /* Колесо 2: 64 слоти (6 бітів) */
    timer_node_t    *tv3[64];      /* Колесо 3: 64 слоти (6 бітів) */
    timer_node_t    *tv4[64];      /* Колесо 4: 64 слоти (6 бітів) */
    
    void            *lock_mutex;   /* Вказівник на м'ютекс або спінлок */
};
typedef struct timer_wheel_s timer_wheel_t;
