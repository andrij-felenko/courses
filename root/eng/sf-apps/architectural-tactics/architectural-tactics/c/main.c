// Пробуємо виклик до 3 разів, із паузою між спробами.
// Тактика купує ДОСТУПНІСТЬ (миттєвий збій не доходить до користувача),
// але платить ЗАТРИМКОЮ і навантаженням на сусіда.
int call_with_retry(request_t *req, response_t *out) {
    const int max_tries = 3;
    int backoff_ms = 50;

    for (int attempt = 1; attempt <= max_tries; attempt++) {
        int rc = do_call(req, out);          // один реальний виклик
        if (rc == OK)
            return OK;                        // влучили — виходимо одразу
        if (rc != ERR_TIMEOUT && rc != ERR_BUSY)
            return rc;                        // «жорстка» помилка — повтор не поможе

        sleep_ms(backoff_ms);                 // пауза перед наступною спробою
        backoff_ms *= 2;                      // 50 → 100 → 200: не добиваємо сусіда
    }
    return ERR_UNAVAILABLE;                    // усі спроби вичерпано
}
