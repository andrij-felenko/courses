/* Формування двійкового блоку прив'язки до каналу */
int scram_build_channel_binding_field(const uint8_t *cert_der, size_t cert_der_len,
                                      char *out_c_base64, size_t max_out_len) {
    uint8_t cert_hash[SCRAM_SHA256_HASH_SIZE];
    if (scram_hash_sha256(cert_der, cert_der_len, cert_hash) != 0) {
        return -1;
    }

    /* Формування бінарного GS2-заголовка з даними прив'язки */
    const char *prefix = "p=tls-server-end-point,,";
    size_t prefix_len = strlen(prefix);

    uint8_t raw_binding[256];
    memcpy(raw_binding, prefix, prefix_len);
    memcpy(raw_binding + prefix_len, cert_hash, SCRAM_SHA256_HASH_SIZE);

    /* Кодування в Base64 для поля c= */
    return base64_encode(raw_binding, prefix_len + SCRAM_SHA256_HASH_SIZE,
                         out_c_base64, max_out_len);
}
