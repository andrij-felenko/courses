#include <errno.h>
#include <seccomp.h>
#include <stddef.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>

static int lock_down(void)
{
    /* дія за замовчуванням — те, що дістанеться всьому недозволеному */
    scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_ERRNO(ENOSYS));
    if (ctx == NULL)
        return -1;

    /* 2 — збирати дерево, а не ланцюг порівнянь */
    seccomp_attr_set(ctx, SCMP_FLTATR_CTL_OPTIMIZE, 2);

    static const int plain[] = {
        SCMP_SYS(read),  SCMP_SYS(close),  SCMP_SYS(lseek), SCMP_SYS(fstat),
        SCMP_SYS(munmap), SCMP_SYS(brk),
        SCMP_SYS(rt_sigreturn), SCMP_SYS(exit_group),
    };
    for (size_t i = 0; i < sizeof plain / sizeof plain[0]; i++)
        seccomp_rule_add(ctx, SCMP_ACT_ALLOW, plain[i], 0);

    /* писати — лише у два вже відкриті дескриптори */
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 1,
                     SCMP_A0(SCMP_CMP_EQ, 1));
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 1,
                     SCMP_A0(SCMP_CMP_EQ, 2));

    /* анонімна пам'ять — так; відображення файлу в пам'ять — ні */
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(mmap), 1,
                     SCMP_A3(SCMP_CMP_MASKED_EQ, MAP_ANONYMOUS, MAP_ANONYMOUS));

    /* з усього мультиплексора ioctl — один-єдиний запит */
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(ioctl), 1,
                     SCMP_A1(SCMP_CMP_EQ, TIOCGWINSZ));

    seccomp_export_pfc(ctx, STDOUT_FILENO);   /* подивитися, що вийшло */

    int rc = seccomp_load(ctx);   /* сама виставить no_new_privs */
    seccomp_release(ctx);
    return rc;
}
