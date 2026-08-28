#include <linux/landlock.h>
#include <sys/syscall.h>

int landlock_create_ruleset(
    const struct landlock_ruleset_attr *attr,
    size_t size,
    __u32 flags
);

int landlock_add_rule(
    int ruleset_fd,
    enum landlock_rule_type rule_type,
    const void *rule_attr,
    __u32 flags
);

int landlock_restrict_self(
    int ruleset_fd,
    __u32 flags
);
