/* Детермінована генерація криптографічного токена на базі соленого хешу */
static void generate_deterministic_token(const char* input, const char* salt, char* out_hex, size_t out_len) {
    if (out_len < 17) {
        if (out_len > 0) out_hex[0] = '\0';
        return;
    }
    uint64_t hash = 0xcbf29ce484222325ULL;
    const uint64_t prime = 0x100000001b3ULL;

    /* Хешування локальної солі юрисдикції */
    for (const char* p = salt; *p != '\0'; p++) {
        hash ^= (uint64_t)(unsigned char)(*p);
        hash *= prime;
    }
    /* Хешування вхідного рядка PII */
    for (const char* p = input; *p != '\0'; p++) {
        hash ^= (uint64_t)(unsigned char)(*p);
        hash *= prime;
    }

    snprintf(out_hex, out_len, "tok_%016llx", (unsigned long long)hash);
}
