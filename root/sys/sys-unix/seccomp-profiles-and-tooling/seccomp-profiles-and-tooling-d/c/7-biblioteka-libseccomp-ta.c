#include <stdio.h>
#include <stdlib.h>
#include <seccomp.h>
#include <unistd.h>

int apply_libseccomp_policy(void) {
    // 1. Створюємо контекст з дією за замовчуванням KILL_PROCESS.
    // Увага: SCMP_ACT_KILL у libseccomp — синонім SCMP_ACT_KILL_THREAD, він убив би лише потік
    scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_KILL_PROCESS);
    if (!ctx) return -1;

    // 2. Додаємо виклики у білий список
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(read), 0) < 0) goto err;
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 0) < 0) goto err;
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit_group), 0) < 0) goto err;

    // 3. Завантажуємо фільтр у ядро
    if (seccomp_load(ctx) < 0) goto err;

    seccomp_release(ctx);
    return 0;

err:
    seccomp_release(ctx);
    return -1;
}
