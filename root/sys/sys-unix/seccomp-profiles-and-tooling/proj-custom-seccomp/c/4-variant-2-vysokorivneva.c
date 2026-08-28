#include <stdio.h>
#include <stdlib.h>
#include <seccomp.h>
#include <unistd.h>

int apply_libseccomp_sandbox(void) {
    // 1. Ініціалізація: дія за замовчуванням — KILL_PROCESS.
    // SCMP_ACT_KILL — синонім SCMP_ACT_KILL_THREAD і вбив би лише потік, а §1 вимагає всього процесу
    scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_KILL_PROCESS);
    if (ctx == NULL) {
        fprintf(stderr, "seccomp_init failed\n");
        return -1;
    }

    int ret = -1;

    // 2. Додаємо виклики у білий список
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(read), 0) < 0) goto out;
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 0) < 0) goto out;
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(brk), 0) < 0) goto out;
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(mmap), 0) < 0) goto out;
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit_group), 0) < 0) goto out;
    if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit), 0) < 0) goto out;

    // 3. Завантаження фільтра в ядро
    if (seccomp_load(ctx) < 0) {
        fprintf(stderr, "seccomp_load failed\n");
        goto out;
    }

    ret = 0;

out:
    // Контекст вивільняється завжди
    seccomp_release(ctx);
    return ret;
}

int main(void) {
    if (apply_libseccomp_sandbox() < 0) {
        return 1;
    }
    printf("libseccomp увімкнено успішно!\n");
    return 0;
}
