#include <linux/landlock.h>
#include <sys/syscall.h>
#include <unistd.h>

/* обгорток у glibc немає — лише через syscall(2) */
int syscall(SYS_landlock_create_ruleset,          /* 444 */
            const struct landlock_ruleset_attr *attr, size_t size, __u32 flags);
int syscall(SYS_landlock_add_rule,                /* 445 */
            int ruleset_fd, enum landlock_rule_type rule_type,
            const void *rule_attr, __u32 flags);
int syscall(SYS_landlock_restrict_self,           /* 446 */
            int ruleset_fd, __u32 flags);
