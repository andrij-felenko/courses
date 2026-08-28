struct timer_node {
    timer_id_t       id;          /* Унікальний ідентифікатор таймера */
    timer_tick_t     expires;     /* Абсолютний час спрацьовування у тіках */
    timer_tick_t     interval;    /* Інтервал повтору для періодичних таймерів */
    uint32_t         flags;       /* Бітові прапорці конфігурації TW_FLAG_* */
    timer_callback_t callback;    /* Вказівник на функцію зворотного виклику */
    void            *user_data;   /* Контекстний вказівник даних користувача */
    struct timer_node *prev;      /* Вказівник на попередній вузол списку слота */
    struct timer_node *next;      /* Вказівник на наступний вузол списку слота */
};
typedef struct timer_node timer_node_t;
