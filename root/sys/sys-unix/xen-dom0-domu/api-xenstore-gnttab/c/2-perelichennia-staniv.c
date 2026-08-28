enum xenbus_state {
    XenbusStateUnknown      = 0,  /* Невідомий стан або пристрій відсутній */
    XenbusStateInitialising = 1,  /* Драйвер виявлено, ініціалізація локальних ресурсів */
    XenbusStateInitWait     = 2,  /* Ресурси виділено, очікування відповіді від протилежної сторони */
    XenbusStateInitialised  = 3,  /* Налаштування завершено, готовність до підключення */
    XenbusStateConnected    = 4,  /* Кільце I/O та Event Channel активні, йде обмін даними */
    XenbusStateClosing      = 5,  /* Запит на відключення пристрою (підготовка до видалення) */
    XenbusStateClosed       = 6,  /* Пристрій повністю відключено та розмаплено */
    XenbusStateReconfiguring= 7,  /* Зміна конфігурації пристрою на льоту (наприклад, зміна розміру) */
    XenbusStateReconfigured = 8   /* Завершення підтвердження зміни конфігурації */
};
