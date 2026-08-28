/* Формування корисного навантаження клієнта PLAIN */
static sasl_result_t plain_client_start(void **ctx, const sasl_credentials_t *cred, sasl_buffer_t *out) {
    if (!cred || !cred->authcid || !cred->password) {
        return SASL_ERR_SYNTAX;
    }

    size_t authzid_len = cred->authzid ? strlen(cred->authzid) : 0;
    size_t authcid_len = strlen(cred->authcid);
    size_t pass_len = strlen(cred->password);

    /* Загальний розмір: len(authzid) + 1 + len(authcid) + 1 + len(passwd) */
    size_t total_len = authzid_len + 1 + authcid_len + 1 + pass_len;
    out->data = (uint8_t *)malloc(total_len);
    if (!out->data) return SASL_ERR_NOMEM;
    out->len = total_len;

    uint8_t *p = out->data;
    if (authzid_len > 0) {
        memcpy(p, cred->authzid, authzid_len);
        p += authzid_len;
    }
    *p++ = '\0';

    memcpy(p, cred->authcid, authcid_len);
    p += authcid_len;
    *p++ = '\0';

    memcpy(p, cred->password, pass_len);
    *ctx = NULL;

    return SASL_OK; /* Механізм PLAIN завершується за 1 крок клієнта */
}

/* Безпечний серверний розбір повідомлення PLAIN */
static sasl_result_t plain_server_step(void *ctx, const sasl_buffer_t *in, sasl_buffer_t *out,
                                      char *auth_user, size_t user_max) {
    (void)ctx;
    (void)out;
    if (!in || in->len == 0 || !in->data) return SASL_ERR_SYNTAX;

    const char *payload = (const char *)in->data;
    size_t len = in->len;

    /* Пошук першого розділювача NUL */
    const char *first_nul = (const char *)memchr(payload, '\0', len);
    if (!first_nul) return SASL_ERR_SYNTAX;

    size_t authzid_len = first_nul - payload;
    const char *authcid = first_nul + 1;
    size_t rem = len - (authzid_len + 1);

    /* Пошук другого розділювача NUL */
    const char *second_nul = (const char *)memchr(authcid, '\0', rem);
    if (!second_nul) return SASL_ERR_SYNTAX;

    size_t authcid_len = second_nul - authcid;
    const char *password = second_nul + 1;
    size_t pass_len = rem - (authcid_len + 1);

    if (authcid_len == 0) return SASL_ERR_SYNTAX;

    /* Демонстраційна перевірка (у промисловій системі: виклик PAM / запит до БД) */
    bool valid = false;
    if (authcid_len == 5 && memcmp(authcid, "alice", 5) == 0 &&
        pass_len == 14 && memcmp(password, "SecretPass_42!", 14) == 0) {
        valid = true;
    }

    if (!valid) return SASL_ERR_AUTH;

    /* Визначаємо підсумкового суб'єкта авторизації */
    if (authzid_len > 0) {
        if (authzid_len >= user_max) return SASL_ERR_NOMEM;
        memcpy(auth_user, payload, authzid_len);
        auth_user[authzid_len] = '\0';
    } else {
        if (authcid_len >= user_max) return SASL_ERR_NOMEM;
        memcpy(auth_user, authcid, authcid_len);
        auth_user[authcid_len] = '\0';
    }

    return SASL_OK;
}

const sasl_mech_t sasl_mech_plain = {
    .name = "PLAIN",
    .client_start = plain_client_start,
    .client_step = NULL,
    .client_destroy = NULL,
    .server_start = NULL,
    .server_step = plain_server_step,
    .server_destroy = NULL
};
