uint32_t size = 0;
long ret = syscall(__NR_lsm_get_self_attr, LSM_ATTR_CURRENT, NULL, &size, 0);
if (ret < 0 && errno == E2BIG) {
    /* Ядро поклало в size потрібну кількість байт: виділяємо й повторюємо */
    struct lsm_ctx *ctx = malloc(size);
    if (ctx) {
        ret = syscall(__NR_lsm_get_self_attr, LSM_ATTR_CURRENT, ctx, &size, 0);
        free(ctx);
    }
}
