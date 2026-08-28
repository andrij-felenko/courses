// Крок мережевого автомата. Кличеться щовитка loop(); НІКОЛИ не блокує.
static void net_step(uint32_t now) {
    switch (g_net_state) {

    case NET_OFFLINE:
        // Спокій. Є Wi-Fi — пора пробувати під'єднатися.
        if (wifi_is_connected()) {
            esp_mqtt_client_reconnect(g_client);   // наказ з'єднатися, не блокує
            net_goto(NET_CONNECTING);
        }
        break;

    case NET_CONNECTING:
        // Ждемо CONNACK. Прийде — обробник події сам переведе в ONLINE.
        // Не прийшов за таймаут — визнаємо невдачу й падаємо у відкат.
        if (now - t_state_enter > CONNECT_TIMEOUT_MS) {
            esp_mqtt_client_disconnect(g_client);  // обірвати завислу спробу
            net_goto(NET_BACKOFF);
        }
        break;

    case NET_ONLINE:
        // Тут нічого «крутити» не треба: поки зв'язок є, ми просто в ONLINE,
        // а звіт і команди робить повільна петля, читаючи g_net_up.
        // Вихід звідси — лише подія DISCONNECTED (обробник переведе в BACKOFF).
        break;

    case NET_BACKOFF:
        // Відлічуємо ФІКСОВАНУ паузу g_backoff_wait, кинуту на вході в стан.
        // Сплила — ростимо СТЕЛЮ (на майбутнє) і пробуємо знову.
        if (now - t_state_enter > g_backoff_wait) {
            g_backoff_ceil <<= 1;                   // ×2 стеля на наступний раз
            if (g_backoff_ceil > BACKOFF_MAX_MS)
                g_backoff_ceil = BACKOFF_MAX_MS;    // упираємось у дах
            net_goto(NET_OFFLINE);                  // → спробувати ще раз
        }
        break;
    }
}
