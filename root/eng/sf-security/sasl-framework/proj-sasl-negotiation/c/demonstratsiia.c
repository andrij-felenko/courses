int main(void) {
    printf("=== Демонстрація роботи каркаса SASL (C) ===\n");

    /* 1. Ініціалізація облікових даних */
    sasl_credentials_t alice_cred = {
        .authzid = NULL,
        .authcid = "alice",
        .password = "SecretPass_42!"
    };

    /* 2. Створення клієнтської сесії з механізмом PLAIN */
    sasl_client_session_t client_sess;
    sasl_client_init(&client_sess, &sasl_mech_plain, &alice_cred);

    sasl_buffer_t initial_response = {NULL, 0};
    sasl_result_t c_res = sasl_client_evaluate(&client_sess, NULL, &initial_response);

    if (c_res == SASL_OK) {
        printf("[Клієнт] Згенеровано початковий кадр PLAIN, розмір: %zu байтів\n", initial_response.len);
    }

    /* 3. Серверна обробка вхідного кадру */
    char authenticated_user[128] = {0};
    sasl_buffer_t server_out = {NULL, 0};
    sasl_result_t s_res = sasl_mech_plain.server_step(NULL, &initial_response, &server_out,
                                                     authenticated_user, sizeof(authenticated_user));

    if (s_res == SASL_OK) {
        printf("[Сервер] Автентифікацію успішно пройдено! Суб'єкт: %s\n", authenticated_user);
    } else {
        printf("[Сервер] Помилка автентифікації: код %d\n", s_res);
    }

    /* 4. Безпечне очищення виділених буферів */
    sasl_buffer_free(&initial_response);
    sasl_buffer_free(&server_out);

    return 0;
}
