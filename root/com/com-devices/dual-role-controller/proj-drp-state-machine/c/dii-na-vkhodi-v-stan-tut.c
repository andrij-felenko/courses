typedef enum { DIR_OFF, DIR_SOURCE, DIR_SINK } vbus_dir_t;

static void vbus_apply(vbus_dir_t dir) {
    // 1) БЕЗУМОВНО зняти обидва силові ключі
    tcpc_src_switch(false);
    tcpc_snk_switch(false);
    // 2) мертвий час: дочекатись реального закриття каналів
    delay_us(DEADTIME_US);      // > часу вимикання ключа
    // 3) рівно один бік (розряд — геть, він несумісний із подачею)
    switch (dir) {
        case DIR_SOURCE:
            tcpc_discharge(false);
            tcpc_src_switch(true);   // м'який пуск — усередині драйвера ключа
            break;
        case DIR_SINK:
            tcpc_discharge(false);
            tcpc_snk_switch(true);
            break;
        case DIR_OFF:
            break;                    // лишаємось знеструмленими
    }
}
