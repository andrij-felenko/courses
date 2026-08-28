/* Тип функції зворотного виклику при виявленні злиття кластерів */
typedef void (*hk_cluster_event_cb)(
    int event_type,        /* 1 - створення нового кластера, 2 - злиття кластерів */
    int primary_root,
    int merged_root,
    int new_total_size,
    void* user_data
);

/* Реєстрація функції зворотного виклику в контексті */
hk_error_t hk_set_cluster_event_callback(
    hk_context_t* ctx,
    hk_cluster_event_cb callback,
    void* user_data
);
