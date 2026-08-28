// Ціле без провідних нулів ("0" — можна, "01" — ні); заразом ловить переповнення.
static semver_err parse_u(const char *p, char **end, unsigned long *out) {
    if (!isdigit((unsigned char)*p))                 return SEMVER_EINVAL;
    if (p[0] == '0' && isdigit((unsigned char)p[1])) return SEMVER_EINVAL;  // провідний нуль
    errno = 0;
    *out = strtoul(p, end, 10);
    return errno == ERANGE ? SEMVER_EINVAL : SEMVER_OK;
}

semver_err semver_parse(const char *s, semver_t *v) {
    char buf[256];
    if (!s || strlen(s) >= sizeof buf) return SEMVER_EINVAL;
    strcpy(buf, s);                     // працюємо з КОПІЄЮ: розбір псує рядок роздільниками
    memset(v, 0, sizeof *v);

    // 1. Відрізати метадані збірки за першим '+' — у старшинстві їх немає.
    char *plus = strchr(buf, '+');
    if (plus) *plus = '\0';

    // 2. Відділити передвипуск за першим '-'. Ядро — самі цифри й крапки,
    //    тож найперший '-' у рядку — це саме межа ядра й передвипуску.
    char *pre  = NULL;
    char *dash = strchr(buf, '-');
    if (dash) { *dash = '\0'; pre = dash + 1; }

    // 3. Ядро: рівно три числа через крапку, і нічого зайвого після латки.
    char *p = buf, *end;
    if (parse_u(p, &end, &v->major) || *end != '.') return SEMVER_EINVAL;
    p = end + 1;
    if (parse_u(p, &end, &v->minor) || *end != '.') return SEMVER_EINVAL;
    p = end + 1;
    if (parse_u(p, &end, &v->patch) || *end != '\0') return SEMVER_EINVAL;

    // 4. Передвипуск: ідентифікатори через '.'.
    while (pre) {
        char *dot = strchr(pre, '.');
        if (dot) *dot = '\0';
        size_t len = strlen(pre);
        if (len == 0 || len >= sizeof v->pre[0]) return SEMVER_EINVAL;  // порожній чи задовгий
        if (v->pre_count == SEMVER_MAX_IDS)       return SEMVER_EINVAL;

        // числовий ідентифікатор не сміє мати провідний нуль — інакше
        // порівняння за довжиною (нижче) брехало б: "007" виглядало б більшим за "7".
        bool digits = true;
        for (const char *c = pre; *c; ++c)
            if (!isdigit((unsigned char)*c)) { digits = false; break; }
        if (digits && pre[0] == '0' && len > 1) return SEMVER_EINVAL;

        strcpy(v->pre[v->pre_count++], pre);
        if (!dot) break;
        pre = dot + 1;
    }
    return SEMVER_OK;
}
