/* Формування GS2-заголовка та початкового виклику SCRAM */
sasl_result_t scram_client_first(const char *username, const char *client_nonce,
                                bool channel_binding, sasl_buffer_t *out) {
    if (!username || !client_nonce || !out) return SASL_ERR_SYNTAX;

    const char *gs2_hdr = channel_binding ? "p=tls-server-end-point,," : "n,,";
    size_t needed = strlen(gs2_hdr) + strlen("n=") + strlen(username) +
                    strlen(",r=") + strlen(client_nonce) + 1;

    out->data = (uint8_t *)malloc(needed);
    if (!out->data) return SASL_ERR_NOMEM;

    int written = snprintf((char *)out->data, needed, "%sn=%s,r=%s",
                           gs2_hdr, username, client_nonce);
    if (written < 0 || (size_t)written >= needed) {
        free(out->data);
        out->data = NULL;
        return SASL_ERR_SYNTAX;
    }
    out->len = (size_t)written;
    return SASL_CONTINUE;
}
