#include <seccomp.h>
#include <unistd.h>
#include <stdlib.h>

int apply_strict_sandbox(void) {
    /* 1. Ініціалізація контексту: дія за замовчуванням — знищення процесу (KILL) */
    scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_KILL);
    if (!ctx) return -1;

    /* 2. Явний білий список дозволених операцій */
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(read), 0) < 0) goto err;
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 0) < 0) goto err;
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit_group), 0) < 0) goto err;
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(futex), 0) < 0) goto err;

    /* 3. Завантаження фільтра в ядро */
    if (seccomp_load(ctx) < 0) goto err;

    seccomp_release(ctx);
    return 0;

err:
    seccomp_release(ctx);
    return -1;
}
