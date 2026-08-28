int main(void) {
    IdemEngine *engine = idem_create();
    const char *key = "req-uuid-9948-2831";
    const char *order_json = "{\"order_id\": 101, \"amount\": 500}";
    const char *tampered_json = "{\"order_id\": 101, \"amount\": 9999}";

    int code = 0;
    char body_buf[256];

    /* Сценарій 1: Первинний запит */
    IdemAction a1 = idem_acquire(engine, key, order_json, strlen(order_json), &code, body_buf, sizeof(body_buf));
    if (a1 == IDEM_ACTION_EXECUTE) {
        printf("[Спроба 1] EXECUTE -> виконуємо списання коштів у БД\n");
        /* Фіксуємо результат */
        idem_commit(engine, key, 200, "{\"status\": \"PAID\", \"tx_id\": 98871}");
    }

    /* Сценарій 2: Мережевий retry з тим самим ключем і тілом */
    IdemAction a2 = idem_acquire(engine, key, order_json, strlen(order_json), &code, body_buf, sizeof(body_buf));
    if (a2 == IDEM_ACTION_RETURN_CACHED) {
        printf("[Спроба 2] RETURN_CACHED -> код %d, відповідь: %s\n", code, body_buf);
    }

    /* Сценарій 3: Спроба використати той самий ключ для іншого платежу */
    IdemAction a3 = idem_acquire(engine, key, tampered_json, strlen(tampered_json), &code, body_buf, sizeof(body_buf));
    if (a3 == IDEM_ACTION_PAYLOAD_MISMATCH) {
        printf("[Спроба 3] PAYLOAD_MISMATCH -> відхилено, захист від підміни спрацював!\n");
    }

    /* Очищення ресурсів */
    idem_destroy(engine);
    return 0;
}
