// Перевірити XOR-суму рядка виду "$...*XX". true — сума збіглася.
bool report_checksum_ok(const char *line) {
    const char *star = strrchr(line, '*');
    if (!star || line[0] != '$') return false;

    // очікувана сума — два шістнадцяткові символи після '*'
    if (strlen(star) < 3) return false;
    uint8_t want = (uint8_t)strtol(star + 1, NULL, 16);

    uint8_t got = 0;
    for (const char *p = line + 1; p < star; p++) got ^= (uint8_t)*p;

    return got == want;
}

// Дістати рядкове значення поля "NAME=..." у out. true — поле знайдено.
bool field_str(const char *line, const char *name, char *out, size_t outlen) {
    char key[24];
    snprintf(key, sizeof(key), ";%s=", name);   // шукаємо ";NAME="
    const char *p = strstr(line, key);
    if (!p) return false;
    p += strlen(key);
    size_t i = 0;
    while (*p && *p != ';' && *p != '*' && i < outlen - 1) out[i++] = *p++;
    out[i] = '\0';
    return true;
}

// Числове поле. true — знайдено й розібрано в *val.
bool field_int(const char *line, const char *name, long *val) {
    char tmp[24];
    if (!field_str(line, name, tmp, sizeof(tmp))) return false;
    char *end;
    long v = strtol(tmp, &end, 0);   // база 0 → зрозуміє і 0x71, і 274
    if (end == tmp) return false;    // там було не число
    *val = v;
    return true;
}
