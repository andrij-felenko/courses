int main(int argc, char **argv) {
    const char *path = getenv("KVLOG_FILE") ? getenv("KVLOG_FILE") : "store.log";
    int durable = (getenv("KVLOG_NOSYNC") == NULL);
    KV kv;

    if (argc < 2) {
        fprintf(stderr, "використання: kvlog put КЛЮЧ ЗНАЧЕННЯ | del КЛЮЧ"
                        " | get КЛЮЧ | list | fill N\n");
        return 2;
    }
    if (kv_open(&kv, path, durable) < 0) { perror("kv_open"); return 1; }

    int rc = 0;
    if (!strcmp(argv[1], "put") && argc == 4) {
        if (kv_put(&kv, OP_PUT, (uint8_t *)argv[2], (uint32_t)strlen(argv[2]),
                   (uint8_t *)argv[3], (uint32_t)strlen(argv[3])) < 0) { perror("put"); rc = 1; }
    } else if (!strcmp(argv[1], "del") && argc == 3) {
        if (kv_put(&kv, OP_DEL, (uint8_t *)argv[2], (uint32_t)strlen(argv[2]),
                   (uint8_t *)"", 0) < 0) { perror("del"); rc = 1; }
    } else if (!strcmp(argv[1], "get") && argc == 3) {
        Entry *e = find(&kv, (uint8_t *)argv[2], (uint32_t)strlen(argv[2]));
        if (e) printf("%.*s\n", (int)e->vlen, (char *)e->val);
        else   printf("(немає)\n");
    } else if (!strcmp(argv[1], "list")) {
        printf("записів: %zu, журнал: %lld Б, наступний номер: %llu\n",
               kv.n, (long long)kv.end, (unsigned long long)kv.next_seq);
    } else if (!strcmp(argv[1], "fill") && argc == 3) {
        long n = atol(argv[2]);
        char k[32], v[64];
        for (long i = 1; i <= n; i++) {
            snprintf(k, sizeof k, "key%06ld", i);
            snprintf(v, sizeof v, "значення №%ld", i);
            if (kv_put(&kv, OP_PUT, (uint8_t *)k, (uint32_t)strlen(k),
                       (uint8_t *)v, (uint32_t)strlen(v)) < 0) { perror("put"); rc = 1; break; }
            printf("%ld\n", i);
            fflush(stdout);      /* без цього «підтверджено» помре разом із процесом */
        }
    } else {
        fprintf(stderr, "невідома команда\n");
        rc = 2;
    }

    kv_close(&kv);
    return rc;
}
