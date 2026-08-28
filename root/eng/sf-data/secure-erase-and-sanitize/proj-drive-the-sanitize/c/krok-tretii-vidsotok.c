struct sanitize_log {            /* сторінка журналу 81h, рівно 512 байтів */
    uint16_t sprog;              /* чисельник дробу зі знаменником 65536 */
    uint16_t sstat;              /* 2:0 — стан, 7:3 — зроблені проходи, 8 — GDE */
    uint32_t scdw10;             /* CDW10 команди, що почала операцію */
    uint32_t etfo, etfbe, etfce; /* оцінки часу, секунди */
    uint32_t etfownd, etfbewnd, etfcewnd;
    uint8_t  rsvd[480];
};

static int read_sanitize_log(int fd, struct sanitize_log *out)
{
    uint32_t numd = sizeof *out / 4 - 1;    /* 127, а не 128 */
    struct nvme_passthru_cmd c = {
        .opcode     = NVME_ADMIN_GET_LOG,
        .nsid       = 0xffffffff,
        .addr       = (uint64_t)(uintptr_t)out,
        .data_len   = sizeof *out,
        .cdw10      = 0x81 | (numd << 16),  /* LID | NUMDL */
        .timeout_ms = 15000,
    };
    return admin(fd, &c);
}

static const char *state_name(unsigned s)
{
    switch (s) {
    case 0: return "ніколи не санітизували";
    case 1: return "завершено успішно";
    case 2: return "триває";
    case 3: return "завершено з помилкою";
    case 4: return "успішно, блоки не звільнено";
    default: return "невідомий стан";
    }
}

static int watch(int fd)
{
    for (;;) {
        struct sanitize_log lg;
        int rc = read_sanitize_log(fd, &lg);
        if (rc) return rc;

        unsigned sstat = le16toh(lg.sstat);
        unsigned state = sstat & 0x7;

        if (state != 2) {
            printf("\n%s · проходів %u · уся медіа стерта: %s\n",
                   state_name(state), (sstat >> 3) & 0x1f,
                   (sstat & 0x100) ? "так" : "ні");
            return (state == 1 || state == 4) ? 0 : -1;
        }
        /* +32768 — округлення до найближчого, а не вниз */
        printf("\rтриває: %3u %%",
               (le16toh(lg.sprog) * 100u + 32768u) / 65536u);
        fflush(stdout);
        sleep(1);
    }
}
