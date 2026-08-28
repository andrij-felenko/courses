typedef enum {
    DRIVER_OK = 0,
    DRIVER_ERR_PARAM,          /* Некоректний аргумент (NULL, вихід за межі діапазону) */
    DRIVER_ERR_NACK_ADDR,      /* Чип не відповів на власну адресу на шині */
    DRIVER_ERR_NACK_DATA,      /* Чип відхилив байт даних/регістра */
    DRIVER_ERR_CRC_MISMATCH,   /* Помилка контрольної суми пакета */
    DRIVER_ERR_BUS_TIMEOUT,    /* Апаратний таймаут очікування лінії/прапорця */
    DRIVER_ERR_BUS_STUCK,      /* Лінія SDA або SCL апаратно затиснута в нуль */
    DRIVER_ERR_WRONG_DEVICE_ID /* Зчитано невірний ID чипа (WHO_AM_I) */
} driver_status_t;

typedef enum {
    ACTION_NONE = 0,
    ACTION_RETRY_IMMEDIATE,    /* Повторити негайно (при поодинокому CRC) */
    ACTION_RETRY_WITH_BACKOFF, /* Повторити після часової паузи */
    ACTION_BUS_RECOVER,        /* Необхідна процедура очищення шини 9 імпульсами SCL */
    ACTION_CIRCUIT_BREAKER_HIT /* Зафіксувати фатальну відмову, заблокувати запити */
} error_action_t;

error_action_t classify_driver_error(driver_status_t status) {
    switch (status) {
        case DRIVER_OK:
            return ACTION_NONE;

        case DRIVER_ERR_CRC_MISMATCH:
        case DRIVER_ERR_NACK_DATA:
            /* Транзиєнтний збій: повторюємо через Backoff */
            return ACTION_RETRY_WITH_BACKOFF;

        case DRIVER_ERR_NACK_ADDR:
        case DRIVER_ERR_BUS_TIMEOUT:
            /* Можливе зависання шини або транзиєнтний скид живлення */
            return ACTION_RETRY_WITH_BACKOFF;

        case DRIVER_ERR_BUS_STUCK:
            /* Апаратне залипання лінії: потрібен спец-протокол відновлення */
            return ACTION_BUS_RECOVER;

        case DRIVER_ERR_PARAM:
        case DRIVER_ERR_WRONG_DEVICE_ID:
        default:
            /* Фатальні помилки: ретраї не допоможуть, фіксуємо відмову */
            return ACTION_CIRCUIT_BREAKER_HIT;
    }
}
