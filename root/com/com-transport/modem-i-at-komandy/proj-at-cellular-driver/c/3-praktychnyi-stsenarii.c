static void on_network_registration(const char *urc_line, void *user_ctx) {
    int n = 0, stat = 0;
    if (sscanf(urc_line, "+CEREG: %d,%d", &n, &stat) >= 1) {
        if (stat == 1 || stat == 5) {
            printf("[EVENT] Реєстрацію в LTE підтверджено (stat=%d)\n", stat);
        } else {
            printf("[EVENT] Пошук мережі або відмова (stat=%d)\n", stat);
        }
    }
}

static void on_socket_recv(const char *urc_line, void *user_ctx) {
    int sock = 0, len = 0;
    if (sscanf(urc_line, "+QIURC: \"recv\",%d,%d", &sock, &len) == 2) {
        printf("[EVENT] У сокет %d надійшло %d байт даних від сервера\n", sock, len);
    }
}

void modem_bringup_example(at_driver_t *drv) {
    char response[128];
    
    /* 1. Реєстрація обробників спонтанних подій URC */
    at_register_urc(drv, "+CEREG:", on_network_registration, NULL);
    at_register_urc(drv, "+QIURC: \"recv\"", on_socket_recv, NULL);
    
    /* 2. Синхронізація з модемом */
    if (at_send_command_sync(drv, "ATE0", response, sizeof(response), 1000) != AT_RESP_OK) {
        printf("[ERROR] Немає зв'язку з модемом на UART!\n");
        return;
    }
    
    /* 3. Увімкнення розширених помилок */
    at_send_command_sync(drv, "AT+CMEE=2", response, sizeof(response), 1000);
    
    /* 4. Запит якості сигналу */
    if (at_send_command_sync(drv, "AT+CSQ", response, sizeof(response), 1000) == AT_RESP_OK) {
        printf("[MODEM] Якість сигналу: %s\n", response);
    }
}
